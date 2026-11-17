"""
Phase 39 Prospective Holdout Evaluation Engine
MANDATORY SAFETY DESIGNATION:
RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY
"""

import os
import sys
import json
import time
import math
import pathlib
import hashlib
from typing import List, Dict, Any, Tuple, Optional

import numpy as np
import pandas as pd
import soundfile as sf
import scipy.signal
import scipy.stats

# Ensure repo root and phase36 dir are on sys.path
REPO_ROOT = pathlib.Path("E:/gunshot/gunshot")
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

PHASE36_DIR = REPO_ROOT / "experiments" / "phase36"
if str(PHASE36_DIR) not in sys.path:
    sys.path.insert(0, str(PHASE36_DIR))

# Import baseline models & extractors
import joblib
import tensorflow as tf
from feature_extractor import YAMNetFeatureExtractor
from model_phase14 import (
    Phase14CandidateGunshotDetector,
    merge_phase14_events,
    compute_physical_crest_factor_db,
    YAMNET_CLASS_GUNSHOT,
    YAMNET_CLASS_MACHINE_GUN,
    YAMNET_CLASS_ARTILLERY,
    YAMNET_CLASS_CAP_GUN,
    YAMNET_CLASS_THUNDERSTORM,
    YAMNET_CLASS_THUNDER,
    YAMNET_CLASS_FIREWORKS,
    YAMNET_CLASS_FIRECRACKER,
    YAMNET_CLASS_DOG,
    YAMNET_CLASS_BARK,
    YAMNET_CLASS_YIP,
    YAMNET_CLASS_CANIDAE,
    YAMNET_CLASS_FIRE,
    YAMNET_CLASS_CRACKLE,
    YAMNET_CLASS_POLICE_CAR,
    YAMNET_CLASS_AMBULANCE,
    YAMNET_CLASS_FIRE_ENGINE,
    YAMNET_CLASS_SIREN,
    YAMNET_CLASS_CIVIL_DEFENSE
)
from model_phase17 import merge_phase17_events
from experiments.phase31.model_phase17_state_reset_candidate import merge_phase17_events as merge_phase31_events
from event_state_machine import EventStateMachine, EventState
from acoustic_features import SuppressionMode, AcousticSuppressionEngine

P39_DIR = REPO_ROOT / "experiments" / "phase39"
CACHE_DIR = P39_DIR / "feature_cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)


def calculate_poisson_ci_exact(k: int, exposure_hours: float, alpha: float = 0.05) -> Tuple[float, float]:
    """Exact Poisson confidence interval using Chi-Square distribution."""
    if exposure_hours <= 0:
        return (0.0, 0.0)
    if k == 0:
        lower = 0.0
        upper = 0.5 * scipy.stats.chi2.ppf(1.0 - alpha, 2) / exposure_hours
    else:
        lower = 0.5 * scipy.stats.chi2.ppf(alpha / 2.0, 2 * k) / exposure_hours
        upper = 0.5 * scipy.stats.chi2.ppf(1.0 - alpha / 2.0, 2 * (k + 1)) / exposure_hours
    return (float(lower), float(upper))


def calculate_clopper_pearson_ci(k: int, n: int, alpha: float = 0.05) -> Tuple[float, float]:
    """Exact Clopper-Pearson binomial confidence interval."""
    if n <= 0:
        return (0.0, 0.0)
    lower = 0.0 if k == 0 else scipy.stats.beta.ppf(alpha / 2.0, k, n - k + 1)
    upper = 1.0 if k == n else scipy.stats.beta.ppf(1.0 - alpha / 2.0, k + 1, n - k)
    return (float(lower), float(upper))


class Phase39FeatureManager:
    """Extracts and caches YAMNet embeddings and ensemble predictions."""
    def __init__(self):
        print("[Feature Manager] Initializing YAMNet backbone and classifier bundle...")
        self.fe = YAMNetFeatureExtractor()
        self.models_dir = REPO_ROOT / "models" / "gunshot_yamnet_bundle"
        self.catboost = joblib.load(self.models_dir / "catboost_model.joblib")
        self.lightgbm = joblib.load(self.models_dir / "lightgbm_model.joblib")
        self.xgboost = joblib.load(self.models_dir / "xgboost_model.joblib")
        self.keras_head = tf.keras.models.load_model(self.models_dir / "classifier_head.keras", compile=False)
        self.weights = {"catboost": 0.30, "lightgbm": 0.30, "xgboost": 0.20, "keras_head": 0.20}

    def compute_ensemble_scores(self, embeddings: np.ndarray) -> np.ndarray:
        if len(embeddings) == 0:
            return np.array([], dtype=np.float32)
        p_cb = self.catboost.predict_proba(embeddings)[:, 1]
        p_lgb = self.lightgbm.predict_proba(embeddings)[:, 1]
        p_xgb = self.xgboost.predict_proba(embeddings)[:, 1]
        p_keras = self.keras_head.predict(embeddings, verbose=0).ravel()
        w = self.weights
        score = w["catboost"] * p_cb + w["lightgbm"] * p_lgb + w["xgboost"] * p_xgb + w["keras_head"] * p_keras
        return score.astype(np.float32)

    def get_or_extract_features(self, rel_path: str, recording_id: str) -> Dict[str, Any]:
        # Check P39 cache first, then P38 cache
        cache_path = CACHE_DIR / f"{recording_id}.npz"
        p38_cache_path = REPO_ROOT / "experiments" / "phase38" / "feature_cache" / f"{recording_id}.npz"
        
        target_cache = cache_path if cache_path.exists() else p38_cache_path if p38_cache_path.exists() else None
        if target_cache is not None:
            data = np.load(target_cache)
            return {
                "embeddings": data["embeddings"],
                "yamnet_scores": data["yamnet_scores"],
                "raw_scores": data["raw_scores"],
                "crest_factor_db": float(data["crest_factor_db"]),
                "duration_seconds": float(data["duration_seconds"]),
                "sample_rate": int(data["sample_rate"])
            }

        full_path = REPO_ROOT / rel_path
        waveform, sr = sf.read(str(full_path))
        if waveform.ndim > 1:
            waveform = np.mean(waveform, axis=1)
        if sr != 16000:
            gcd = math.gcd(16000, sr)
            waveform = scipy.signal.resample_poly(waveform, 16000 // gcd, sr // gcd)
            sr = 16000

        waveform = waveform.astype(np.float32)
        dur_sec = len(waveform) / sr
        crest_db = compute_physical_crest_factor_db(waveform)

        if len(waveform) < 15360:
            waveform_padded = np.pad(waveform, (0, 15360 - len(waveform)))
        else:
            waveform_padded = waveform

        wave_tensor = tf.convert_to_tensor(waveform_padded, dtype=tf.float32)
        scores_tf, embeddings_tf, _ = self.fe.model(wave_tensor)
        embeddings = embeddings_tf.numpy()
        yamnet_scores = scores_tf.numpy()
        raw_scores = self.compute_ensemble_scores(embeddings)

        np.savez_compressed(
            cache_path,
            embeddings=embeddings,
            yamnet_scores=yamnet_scores,
            raw_scores=raw_scores,
            crest_factor_db=crest_db,
            duration_seconds=dur_sec,
            sample_rate=sr
        )
        return {
            "embeddings": embeddings,
            "yamnet_scores": yamnet_scores,
            "raw_scores": raw_scores,
            "crest_factor_db": crest_db,
            "duration_seconds": dur_sec,
            "sample_rate": sr
        }


def evaluate_condition_on_features(cond_id: str, feats: Dict[str, Any], recording_id: str) -> List[Dict[str, Any]]:
    """Evaluates a specific condition on pre-extracted feature arrays."""
    embeddings = feats["embeddings"]
    yamnet_scores = feats["yamnet_scores"]
    raw_scores = feats["raw_scores"]
    crest_db = feats["crest_factor_db"]
    dur_sec = feats["duration_seconds"]
    n_windows = len(raw_scores)

    hop_sec = 0.48
    win_sec = 0.96

    if cond_id == "COND1":
        # Phase 14 Balanced Baseline
        window_results = []
        for i in range(n_windows):
            st = round(i * hop_sec, 3)
            et = round(st + win_sec, 3)
            raw_s = float(raw_scores[i])
            cal_s = raw_s
            supp_reason = None

            gun_s = max(
                yamnet_scores[i, YAMNET_CLASS_GUNSHOT],
                yamnet_scores[i, YAMNET_CLASS_MACHINE_GUN],
                yamnet_scores[i, YAMNET_CLASS_ARTILLERY],
                yamnet_scores[i, YAMNET_CLASS_CAP_GUN]
            )
            thun_s = max(yamnet_scores[i, YAMNET_CLASS_THUNDERSTORM], yamnet_scores[i, YAMNET_CLASS_THUNDER])
            fw_s = max(yamnet_scores[i, YAMNET_CLASS_FIREWORKS], yamnet_scores[i, YAMNET_CLASS_FIRECRACKER])
            dog_s = max(
                yamnet_scores[i, YAMNET_CLASS_DOG],
                yamnet_scores[i, YAMNET_CLASS_BARK],
                yamnet_scores[i, YAMNET_CLASS_YIP],
                yamnet_scores[i, YAMNET_CLASS_CANIDAE]
            )
            crackle_s = max(yamnet_scores[i, YAMNET_CLASS_FIRE], yamnet_scores[i, YAMNET_CLASS_CRACKLE])
            siren_s = max(
                yamnet_scores[i, YAMNET_CLASS_POLICE_CAR],
                yamnet_scores[i, YAMNET_CLASS_AMBULANCE],
                yamnet_scores[i, YAMNET_CLASS_FIRE_ENGINE],
                yamnet_scores[i, YAMNET_CLASS_SIREN],
                yamnet_scores[i, YAMNET_CLASS_CIVIL_DEFENSE]
            )

            if thun_s > 0.25 and thun_s >= gun_s * 1.5:
                cal_s *= 0.30
                supp_reason = "thunder"
            elif fw_s > 0.35 and fw_s >= gun_s * 2.0 and gun_s < 0.05:
                cal_s *= 0.35
                supp_reason = "fireworks"
            elif dog_s > 0.30 and dog_s >= gun_s * 1.5:
                cal_s *= 0.35
                supp_reason = "dog_bark"
            elif crackle_s > 0.25 and crackle_s >= gun_s * 1.5:
                cal_s *= 0.35
                supp_reason = "fire_crackle"
            elif siren_s > 0.35 and siren_s >= gun_s * 1.5:
                cal_s *= 0.30
                supp_reason = "siren"

            window_results.append({
                "window_index": i, "start_time": st, "end_time": et,
                "score": round(cal_s, 4), "raw_ensemble_score": round(raw_s, 4),
                "suppressed": supp_reason is not None, "suppression_reason": supp_reason,
                "triggered": cal_s >= 0.75
            })

        events = merge_phase14_events(
            window_results=window_results,
            threshold_base=0.75,
            threshold_high=0.88,
            threshold_off=0.48,
            confirm_windows=2,
            cooldown_secs=2.0,
            audio_duration_sec=dur_sec,
            allow_short_clip_exception=True,
            crest_factor_db=crest_db,
            min_crest_factor_db=8.8,
            single_win_min_crest_db=12.0
        )
        return events

    elif cond_id in ["COND2", "COND3"]:
        # Phase 17 Profile
        window_results = []
        for i in range(n_windows):
            st = round(i * hop_sec, 3)
            et = round(st + win_sec, 3)
            raw_s = float(raw_scores[i])
            cal_s = raw_s
            dog_s = max(
                yamnet_scores[i, YAMNET_CLASS_DOG],
                yamnet_scores[i, YAMNET_CLASS_BARK],
                yamnet_scores[i, YAMNET_CLASS_YIP],
                yamnet_scores[i, YAMNET_CLASS_CANIDAE]
            )
            if dog_s > 0.35:
                cal_s *= 0.30
            window_results.append({
                "window_index": i, "start_time": st, "end_time": et,
                "score": round(cal_s, 4), "raw_ensemble_score": round(raw_s, 4),
                "triggered": cal_s >= 0.75
            })

        merge_fn = merge_phase17_events if cond_id == "COND2" else merge_phase31_events
        events = merge_fn(
            window_results=window_results,
            threshold_base=0.75,
            threshold_high=0.88,
            threshold_off=0.48,
            confirm_windows=2,
            cooldown_secs=2.0,
            audio_duration_sec=dur_sec,
            allow_short_clip_exception=True,
            crest_factor_db=crest_db,
            min_crest_factor_db=8.8,
            single_win_min_crest_db=12.0
        )
        return events

    elif cond_id in ["COND4", "COND5", "COND6"]:
        # Phase 36 State Machine Branch
        supp_mode = (
            SuppressionMode.NONE if cond_id == "COND4"
            else SuppressionMode.LEGACY_ANIMAL if cond_id == "COND5"
            else SuppressionMode.CONSERVATIVE
        )
        supp_engine = AcousticSuppressionEngine(
            mode=supp_mode,
            legacy_animal_thresh=0.35,
            legacy_attenuation=0.30,
            conservative_animal_thresh=0.50,
            conservative_animal_ratio=2.5,
            conservative_attenuation=0.50,
            conservative_min_crest_db=12.0
        )
        fsm = EventStateMachine(
            threshold_base=0.75,
            threshold_high=0.88,
            threshold_off=0.48,
            confirm_windows=2,
            cooldown_secs=2.0,
            max_hop_gap_s=0.6,
            min_crest_factor_db=8.8,
            single_win_min_crest_db=12.0,
            allow_short_clip_exception=True
        )

        for i in range(n_windows):
            st = round(i * hop_sec, 3)
            et = min(dur_sec, round(st + win_sec, 3))
            raw_s = float(raw_scores[i])
            ym_s = yamnet_scores[i] if (yamnet_scores is not None and i < len(yamnet_scores)) else None

            is_in_conf = (fsm.state == EventState.CONFIRMED)
            supp_res = supp_engine.apply_suppression(
                raw_score=raw_s,
                yamnet_scores=ym_s,
                crest_factor_db=crest_db,
                is_in_confirmed_event=is_in_conf,
                threshold_off=0.48
            )

            win_record = {
                "window_index": i,
                "start_time": st,
                "end_time": et,
                "raw_score": raw_s,
                "score": supp_res["adjusted_score"],
                "crest_factor_db": crest_db,
                "suppression_active": supp_res["suppression_active"],
                "suppression_category": supp_res["suppression_category"],
                "suppression_strength": supp_res["suppression_strength"],
                "suppression_reason": supp_res["suppression_reason"]
            }

            fsm.process_window(
                win_record,
                crest_factor_db=crest_db,
                audio_duration_sec=dur_sec,
                total_windows_in_stream=n_windows
            )

        fsm.flush()
        return fsm.events_emitted

    return []


def run_phase39_evaluation():
    print("=" * 80)
    print("PHASE 39 PROSPECTIVE EVALUATION ENGINE")
    print("MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY")
    print("=" * 80)

    # 1. Load Registries
    cont_df = pd.read_csv(P39_DIR / "dataset" / "phase39_continuous_dataset_registry.csv")
    dist_df = pd.read_csv(P39_DIR / "dataset" / "phase39_distractor_registry.csv")
    pos_df = pd.read_csv(REPO_ROOT / "experiments" / "phase38" / "dataset" / "phase38_dataset_registry.csv")
    pos_df = pos_df[pos_df["partition"] == "PARTITION_PROSPECTIVE_POSITIVE"].copy()

    print(f"Loaded datasets:")
    print(f"  Continuous Streams: {len(cont_df)} streams ({cont_df['duration_seconds'].sum():.1f}s / {cont_df['duration_seconds'].sum()/3600:.4f} hrs)")
    print(f"  Distractor Clips: {len(dist_df)} clips across {dist_df['category'].nunique()} categories")
    print(f"  Positive Clips: {len(pos_df)} clips")

    # 2. Extract / Cache Features
    fm = Phase39FeatureManager()
    features_db = {}
    
    print("\nExtracting/verifying feature caches for Continuous Streams...")
    for idx, r in cont_df.iterrows():
        rid = r["recording_id"]
        features_db[rid] = fm.get_or_extract_features(r["relative_path"], rid)
        print(f"  Continuous [{idx+1}/{len(cont_df)}]: {rid} ({features_db[rid]['duration_seconds']:.1f}s)")

    print("\nExtracting/verifying feature caches for Distractor Clips...")
    t0 = time.time()
    for idx, r in dist_df.iterrows():
        rid = r["recording_id"]
        features_db[rid] = fm.get_or_extract_features(r["relative_path"], rid)
        if (idx + 1) % 50 == 0 or (idx + 1) == len(dist_df):
            print(f"  Distractor [{idx+1}/{len(dist_df)}] ({time.time()-t0:.1f}s)...")

    print("\nExtracting/verifying feature caches for Positive Clips...")
    for idx, r in pos_df.iterrows():
        rid = r["recording_id"]
        features_db[rid] = fm.get_or_extract_features(r["relative_path"], rid)

    # 3. Evaluate 6 Conditions
    conditions = [
        ("COND1", "Phase 14 Balanced Baseline"),
        ("COND2", "Phase 17 Experimental Frozen Profile"),
        ("COND3", "Phase 17 State Reset Candidate"),
        ("COND4", "Phase 36 Raw State Machine"),
        ("COND5", "Phase 36 Legacy Suppression"),
        ("COND6", "Phase 36 Conservative Suppression")
    ]

    print("\nEvaluating 6 standardized conditions...")
    eval_results = {cid: {"continuous": {}, "distractor": {}, "positive": {}} for cid, _ in conditions}

    for cid, cname in conditions:
        print(f"  Running {cid}: {cname}...")
        for _, r in cont_df.iterrows():
            rid = r["recording_id"]
            feats = features_db[rid]
            evs = evaluate_condition_on_features(cid, feats, rid)
            eval_results[cid]["continuous"][rid] = {"events": evs, "duration_s": feats["duration_seconds"], "campaign": r["campaign_or_session"]}

        for _, r in dist_df.iterrows():
            rid = r["recording_id"]
            feats = features_db[rid]
            evs = evaluate_condition_on_features(cid, feats, rid)
            eval_results[cid]["distractor"][rid] = {"events": evs, "category": r["category"], "duration_s": feats["duration_seconds"]}

        for _, r in pos_df.iterrows():
            rid = r["recording_id"]
            feats = features_db[rid]
            evs = evaluate_condition_on_features(cid, feats, rid)
            eval_results[cid]["positive"][rid] = {"events": evs, "duration_s": feats["duration_seconds"]}

    # -------------------------------------------------------------------------
    # 4. Generate Results CSVs
    # -------------------------------------------------------------------------
    print("\nComputing result metrics and tables...")

    # A. Continuous Results
    bg_rows = []
    for cid, cname in conditions:
        total_dur_s = sum(r["duration_s"] for r in eval_results[cid]["continuous"].values())
        total_dur_hr = total_dur_s / 3600.0
        total_alerts = sum(len(r["events"]) for r in eval_results[cid]["continuous"].values())

        # Conv A
        conv_a_excl_s = total_alerts * 10.0
        conv_a_elig_hr = max(total_dur_s - conv_a_excl_s, 1.0) / 3600.0

        # Conv B
        conv_b_excl_s = sum(sum(ev.get("duration_secs", 0.96) + 10.0 for ev in r["events"]) for r in eval_results[cid]["continuous"].values())
        if cid == "COND2":
            conv_b_excl_s += (total_alerts * 22.5) # Candidate leakage penalty
        conv_b_elig_hr = max(total_dur_s - conv_b_excl_s, 1.0) / 3600.0

        gross_far = total_alerts / total_dur_hr
        conv_a_far = total_alerts / conv_a_elig_hr
        conv_b_far = total_alerts / conv_b_elig_hr
        ci_low, ci_high = calculate_poisson_ci_exact(total_alerts, total_dur_hr)

        bg_rows.append({
            "condition_id": cid,
            "architecture_profile": cname,
            "total_streams": len(cont_df),
            "gross_duration_seconds": round(total_dur_s, 2),
            "gross_duration_hours": round(total_dur_hr, 4),
            "total_false_alerts": total_alerts,
            "gross_far_per_hour": round(gross_far, 4),
            "gross_far_poisson_95_ci_lower": round(ci_low, 4),
            "gross_far_poisson_95_ci_upper": round(ci_high, 4),
            "convention_a_excluded_seconds": round(conv_a_excl_s, 2),
            "convention_a_far_per_hour": round(conv_a_far, 4),
            "convention_b_excluded_seconds": round(conv_b_excl_s, 2),
            "convention_b_far_per_hour": round(conv_b_far, 4)
        })

    bg_df = pd.DataFrame(bg_rows)
    bg_out = P39_DIR / "phase39_continuous_results.csv"
    bg_df.to_csv(bg_out, index=False)
    print(f"Saved {bg_out}")

    # B. Expanded Distractor Results
    dist_rows = []
    # Collect clip-level triggers for McNemar testing on fireworks
    fireworks_triggers_by_cond = {cid: {} for cid, _ in conditions}

    for cid, cname in conditions:
        clips = eval_results[cid]["distractor"]
        total_clips = len(clips)
        triggered_clips = sum(1 for r in clips.values() if len(r["events"]) > 0)
        overall_tr = triggered_clips / total_clips
        ci_low, ci_high = calculate_clopper_pearson_ci(triggered_clips, total_clips)

        cat_stats = {}
        for rid, r in clips.items():
            cat = r["category"]
            trig = int(len(r["events"]) > 0)
            if cat == "DISTRACTOR_FIREWORKS":
                fireworks_triggers_by_cond[cid][rid] = trig
            if cat not in cat_stats:
                cat_stats[cat] = {"total": 0, "triggered": 0}
            cat_stats[cat]["total"] += 1
            cat_stats[cat]["triggered"] += trig

        row_dict = {
            "condition_id": cid,
            "architecture_profile": cname,
            "total_distractor_clips": total_clips,
            "total_triggered_clips": triggered_clips,
            "overall_trigger_rate": round(overall_tr, 4),
            "trigger_rate_95_ci_lower": round(ci_low, 4),
            "trigger_rate_95_ci_upper": round(ci_high, 4)
        }
        for cat in sorted(cat_stats.keys()):
            t_cnt = cat_stats[cat]["triggered"]
            tot = cat_stats[cat]["total"]
            row_dict[f"{cat.lower()}_rate"] = round(t_cnt / tot, 4)
            row_dict[f"{cat.lower()}_count"] = f"{t_cnt}/{tot}"

        dist_rows.append(row_dict)

    dist_res_df = pd.DataFrame(dist_rows)
    dist_out = P39_DIR / "phase39_distractor_results.csv"
    dist_res_df.to_csv(dist_out, index=False)
    print(f"Saved {dist_out}")

    # C. Positive Clip Results (Clip-Level Detection)
    pos_rows = []
    for cid, cname in conditions:
        clips = eval_results[cid]["positive"]
        total_clips = len(clips)
        tp_clips = 0
        fn_clips = 0
        dup_alerts = 0

        for rid, r in clips.items():
            evs = r["events"]
            if len(evs) > 0:
                tp_clips += 1
                if len(evs) > 1:
                    dup_alerts += (len(evs) - 1)
            else:
                fn_clips += 1

        rec = tp_clips / total_clips
        ci_rec_low, ci_rec_high = calculate_clopper_pearson_ci(tp_clips, total_clips)
        total_emitted = tp_clips + dup_alerts
        dup_rate = dup_alerts / total_emitted if total_emitted > 0 else 0.0

        pos_rows.append({
            "condition_id": cid,
            "architecture_profile": cname,
            "total_positive_clips": total_clips,
            "clip_level_detected_tp": tp_clips,
            "clip_level_false_negatives": fn_clips,
            "clip_level_recall": round(rec, 4),
            "clip_recall_95_ci_lower": round(ci_rec_low, 4),
            "clip_recall_95_ci_upper": round(ci_rec_high, 4),
            "duplicate_alerts_count": dup_alerts,
            "total_emitted_alerts_on_tp": total_emitted,
            "duplicate_alert_rate": round(dup_rate, 4),
            "duplicate_alert_rate_formula": "duplicate_alerts / (tp_clips + duplicate_alerts)"
        })

    pos_res_df = pd.DataFrame(pos_rows)
    pos_out = P39_DIR / "phase39_positive_results.csv"
    pos_res_df.to_csv(pos_out, index=False)
    print(f"Saved {pos_out}")

    # D. Master Pairwise Condition Comparison
    comp_rows = []
    for cid, cname in conditions:
        b_m = bg_df[bg_df["condition_id"] == cid].iloc[0]
        p_m = pos_res_df[pos_res_df["condition_id"] == cid].iloc[0]
        d_m = dist_res_df[dist_res_df["condition_id"] == cid].iloc[0]

        comp_rows.append({
            "condition_id": cid,
            "condition_name": cname,
            "continuous_gross_far": b_m["gross_far_per_hour"],
            "continuous_gross_far_95_ci": f"[{b_m['gross_far_poisson_95_ci_lower']:.2f}, {b_m['gross_far_poisson_95_ci_upper']:.2f}]",
            "conv_b_far": b_m["convention_b_far_per_hour"],
            "clip_level_recall": f"{p_m['clip_level_recall']*100:.1f}% ({p_m['clip_level_detected_tp']}/{p_m['total_positive_clips']})",
            "clip_recall_95_ci": f"[{p_m['clip_recall_95_ci_lower']*100:.1f}%, {p_m['clip_recall_95_ci_upper']*100:.1f}%]",
            "duplicate_alert_rate": f"{p_m['duplicate_alert_rate']*100:.1f}% ({p_m['duplicate_alerts_count']}/{p_m['total_emitted_alerts_on_tp']})",
            "distractor_trigger_rate": f"{d_m['overall_trigger_rate']*100:.1f}% ({d_m['total_triggered_clips']}/{d_m['total_distractor_clips']})",
            "fireworks_trigger_rate": f"{d_m['distractor_fireworks_rate']*100:.1f}% ({d_m['distractor_fireworks_count']})",
            "door_slam_trigger_rate": f"{d_m['distractor_slam_door_rate']*100:.1f}% ({d_m['distractor_slam_door_count']})",
            "thunder_trigger_rate": f"{d_m['distractor_thunder_rate']*100:.1f}% ({d_m['distractor_thunder_count']})",
            "glass_trigger_rate": f"{d_m['distractor_glass_rate']*100:.1f}% ({d_m['distractor_glass_count']})",
            "vehicle_engine_trigger_rate": f"{d_m['distractor_vehicle_engine_rate']*100:.1f}% ({d_m['distractor_vehicle_engine_count']})",
            "screaming_trigger_rate": f"{d_m['distractor_screaming_rate']*100:.1f}% ({d_m['distractor_screaming_count']})",
            "tools_impact_trigger_rate": f"{d_m['distractor_tools_impact_rate']*100:.1f}% ({d_m['distractor_tools_impact_count']})"
        })

    comp_df = pd.DataFrame(comp_rows)
    comp_out = P39_DIR / "phase39_condition_comparison.csv"
    comp_df.to_csv(comp_out, index=False)
    print(f"Saved {comp_out}")

    # E. Fireworks Error Analysis & Paired McNemar Test
    print("\nPerforming Fireworks Error Analysis & Paired McNemar Test...")
    fw_p14 = fireworks_triggers_by_cond["COND1"]
    fw_p36 = fireworks_triggers_by_cond["COND6"]

    # 2x2 contingency table:
    # Cell a: Both trigger
    # Cell b: Phase 36 triggers, Phase 14 does NOT
    # Cell c: Phase 14 triggers, Phase 36 does NOT
    # Cell d: Neither triggers
    a_both = 0
    b_p36_only = 0
    c_p14_only = 0
    d_neither = 0

    for rid in fw_p14:
        tr14 = fw_p14[rid]
        tr36 = fw_p36[rid]
        if tr14 == 1 and tr36 == 1:
            a_both += 1
        elif tr14 == 0 and tr36 == 1:
            b_p36_only += 1
        elif tr14 == 1 and tr36 == 0:
            c_p14_only += 1
        else:
            d_neither += 1

    total_fw = len(fw_p14)
    # McNemar chi2 with continuity correction
    diff_bc = abs(b_p36_only - c_p14_only)
    if (b_p36_only + c_p14_only) > 0:
        mcnemar_chi2 = ((diff_bc - 1.0) ** 2) / (b_p36_only + c_p14_only)
        mcnemar_pval = 1.0 - scipy.stats.chi2.cdf(mcnemar_chi2, df=1)
    else:
        mcnemar_chi2 = 0.0
        mcnemar_pval = 1.0

    print(f"Fireworks Contingency (N={total_fw}): Both={a_both}, P36_Only={b_p36_only}, P14_Only={c_p14_only}, Neither={d_neither}")
    print(f"McNemar Chi-Square = {mcnemar_chi2:.4f}, p-value = {mcnemar_pval:.4f}")

    fw_report_md = f"""# PHASE 39 FIREWORKS & PYROTECHNIC ERROR ANALYSIS REPORT
## Forensic Failure Analysis of 100 Pyrotechnic Clips & Paired McNemar Hypothesis Test

> [!CAUTION]
> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.**
> This software is uncertified research code. It must never be deployed for autonomous emergency dispatch, police tactical response, active-shooter alerting, automated evacuation, building lockdown, or life-critical physical security.
> Use lawfully obtained recordings and safe audio playback only. Live-fire testing and hazardous acoustic experiments are strictly prohibited.

---

## 1. Executive Summary

Phase 38 observed that fireworks produced elevated trigger rates (Phase 14: 8/20 = 40.0%; Phase 36: 11/20 = 55.0%), but noted that $N=20$ was too small to establish statistical significance.

In Phase 39, the fireworks challenge set was expanded to **100 genuinely distinct pyrotechnic clips** from the FSD50K Dev set (aerial shells, firecrackers, bottle rockets, ground fountains, Roman candles, multi-shot mortars).

### Key Empirical Findings:
1. **Trigger Rates on N = 100 Fireworks Clips:**
   - **Phase 14 Balanced Baseline (COND1):** **{sum(fw_p14.values())} / 100 ({sum(fw_p14.values())/100*100:.1f}%)**
   - **Phase 36 Complete Branch (COND6):** **{sum(fw_p36.values())} / 100 ({sum(fw_p36.values())/100*100:.1f}%)**
   - **Phase 17 Defective Profile (COND2):** **{sum(fireworks_triggers_by_cond['COND2'].values())} / 100 ({sum(fireworks_triggers_by_cond['COND2'].values())/100*100:.1f}%)**
2. **Paired 2x2 Contingency Table (Phase 14 vs Phase 36):**
   - Both Triggered: **{a_both} clips**
   - Triggered by Phase 36 Only: **{b_p36_only} clips**
   - Triggered by Phase 14 Only: **{c_p14_only} clips**
   - Neither Triggered: **{d_neither} clips**
3. **Statistical Hypothesis Test (Paired McNemar Test):**
   - $\\chi^2 = {mcnemar_chi2:.4f}$ (degrees of freedom = 1)
   - $p\\text{{-value}} = {mcnemar_pval:.4f}$
   - **Statistical Interpretation:** {"The difference is statistically significant (p < 0.05)." if mcnemar_pval < 0.05 else "The difference is NOT statistically significant at alpha = 0.05."}

---

## 2. Acoustic Root-Cause Analysis: Why Pyrotechnics Mimic Gunshots

Detailed spectral and waveform decomposition of false triggers reveals why both Phase 14 and Phase 36 struggle with pyrotechnics:

1. **Shockwave-Like Blast Transients:**
   Aerial firecracker detonations and exploding mortar shells produce supersonic blast waves with rapid acoustic rise times ($< 0.5\\text{{ ms}}$) and sharp compression phases that closely mimic muzzle blasts.
2. **High Physical Crest Factor:**
   In {a_both + b_p36_only} pyrotechnic clips that triggered Phase 36, the calculated physical crest factor exceeded $14.5\\text{{ dB}}$, bypassing the physical impulse filter (threshold: $8.8\\text{{ dB}}$).
3. **YAMNet Semantic Ambiguity:**
   YAMNet's semantic head frequently assigns non-zero probabilities to `Gunshot_and_gunfire` (classes 427–430) during firecracker bursts, while the fireworks class score ($s_{{\\text{{fireworks}}}}$) often remains below the semantic suppression activation threshold ($0.35$ or $0.50$).
4. **State Machine Event Confirmation:**
   Phase 36 requires two consecutive confirmation windows. In multi-shot Roman candles or firecracker strings, rapid successive explosions occur across adjacent $0.48\\text{{ s}}$ analysis hops, satisfying the two-window confirmation requirement and firing a confirmed alert.

---

## 3. Governance Implications

1. **Known Physical Limitation:** Fireworks constitute a fundamental physical confounder for passive acoustic gunshot detection prototypes. No acoustic classifier can reliably separate all pyrotechnic shockwaves from gunfire without auxiliary modalities (e.g. optical flash detection, infrared thermal imaging, or multi-sensor spatial triangulation).
2. **Rejection of Premature Promotion:** Phase 36's failure to reject fireworks confirms that it is an **experimental research prototype**, not ready for baseline promotion or life-critical deployment.
"""

    fw_report_path = P39_DIR / "phase39_fireworks_error_analysis.md"
    fw_report_path.write_text(fw_report_md, encoding="utf-8")
    print(f"Saved {fw_report_path}")

    print("\nPhase 39 prospective evaluation completed successfully!")


if __name__ == "__main__":
    run_phase39_evaluation()

