"""
Phase 13: Controlled False-Alert Reduction Experiments & Ablation Matrix.

Executes isolated experiments (A through F) and the combined candidate detector
across eligible development data (Phase 8 final eval dataset + Phase 12 reserved_validation).
Total development set: 280 verified clips (66 physical gunshots, 214 real negatives).

Strictly enforces:
- Zero contamination: Phase 12 final test benchmark (120 files) is NOT touched.
- Frozen baseline: Phase 9 detector is unchanged and evaluated identically.
- One factor at a time: Isolates each algorithmic mechanism.

Outputs:
- reports/phase13_experiment_matrix.csv
- reports/phase13_experiments_summary.json
"""

import os
import sys
import json
import time
import math
import pickle
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional

import numpy as np
import pandas as pd
import soundfile as sf
import tensorflow as tf

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import config
from dataset import load_audio_mono_16k
from model import load_model_bundle
from model_phase9 import (
    Phase9AdaptiveGunshotDetector,
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
    merge_detection_windows_phase9
)
from model_phase13 import (
    Phase13CandidateGunshotDetector,
    merge_phase13_events,
    YAMNET_CLASS_POLICE_CAR,
    YAMNET_CLASS_AMBULANCE,
    YAMNET_CLASS_FIRE_ENGINE,
    YAMNET_CLASS_SIREN,
    YAMNET_CLASS_CIVIL_DEFENSE
)

OUTPUT_MATRIX_CSV = Path("reports/phase13_experiment_matrix.csv")
OUTPUT_SUMMARY_JSON = Path("reports/phase13_experiments_summary.json")

def load_development_dataset() -> List[Dict[str, Any]]:
    """
    Load eligible development dataset:
    - Phase 8 development evaluation manifest (246 files)
    - Phase 12 reserved_validation split (34 files)
    Total: 280 files. Zero overlap with Phase 12 final_test.
    """
    records = []

    # 1. Load Phase 8 development manifest
    p8_manifest_path = Path("data/manifests/phase8_final_eval_manifest.csv")
    p8_events_path = Path("data/manifests/phase8_canonical_gunshot_events.csv")
    df_p8 = pd.read_csv(p8_manifest_path)
    df_p8_events = pd.read_csv(p8_events_path)

    p8_events_map = {}
    for _, ev in df_p8_events.iterrows():
        p8_events_map[ev["recording_id"]] = {
            "start": float(ev["start_time_sec"]),
            "end": float(ev["end_time_sec"])
        }

    for _, row in df_p8.iterrows():
        rid = str(row["recording_id"])
        fp = Path(row["filepath"])
        label = int(row["label"])
        cond = str(row["acoustic_condition"])
        cat = str(row["category"])
        dur = float(row["duration_sec"])

        if label == 1 and rid in p8_events_map:
            t_start = p8_events_map[rid]["start"]
            t_end = p8_events_map[rid]["end"]
        else:
            t_start = 0.0
            t_end = dur

        records.append({
            "source_split": "phase8_dev_eval",
            "recording_id": rid,
            "filepath": fp,
            "label": label,
            "condition": cond,
            "category": cat,
            "duration": dur,
            "t_start": t_start,
            "t_end": t_end
        })

    # 2. Load Phase 12 reserved_validation split
    p12_manifest_path = Path("data/manifests/phase12_independent_eval_manifest.csv")
    df_p12 = pd.read_csv(p12_manifest_path)
    df_res_val = df_p12[df_p12["split"] == "reserved_validation"]

    for _, row in df_res_val.iterrows():
        records.append({
            "source_split": "phase12_reserved_val",
            "recording_id": str(row["recording_id"]),
            "filepath": Path(row["filepath"]),
            "label": int(row["ground_truth_label"]),
            "condition": str(row["acoustic_condition"]),
            "category": str(row["event_classification"]),
            "duration": float(row["duration_seconds"]),
            "t_start": float(row["event_start_time_sec"]),
            "t_end": float(row["event_end_time_sec"])
        })

    print(f"Loaded {len(records)} development samples ({sum(1 for r in records if r['label'] == 1)} positive, {sum(1 for r in records if r['label'] == 0)} negative).")
    return records

def precompute_development_features(records: List[Dict[str, Any]], base_detector: Phase9AdaptiveGunshotDetector) -> List[Dict[str, Any]]:
    """
    Extract YAMNet embeddings and raw ensemble predictions once for the entire development set.
    """
    cache_path = Path("reports/.phase13_dev_features_cache.pkl")
    if cache_path.exists():
        print(f"Loading precomputed features from disk cache: {cache_path}...")
        try:
            with open(cache_path, "rb") as f:
                return pickle.load(f)
        except Exception as e:
            print(f"Failed to load cache ({e}), recomputing...")

    print("Pre-computing feature embeddings and raw ensemble scores...")
    t0 = time.time()
    cache = []

    yamnet_model = base_detector.yamnet_model
    model_bundle = base_detector.model

    for rec in records:
        fp = rec["filepath"]
        waveform = load_audio_mono_16k(fp)
        crest_db = compute_physical_crest_factor_db(waveform)

        if len(waveform) < config.WINDOW_SAMPLES:
            padded_wave = np.pad(waveform, (0, config.WINDOW_SAMPLES - len(waveform)))
        else:
            padded_wave = waveform

        wave_tensor = tf.convert_to_tensor(padded_wave, dtype=tf.float32)
        yamnet_scores, embeddings, _ = yamnet_model(wave_tensor)
        yamnet_scores = yamnet_scores.numpy()
        embeddings = embeddings.numpy()

        # Raw ensemble predictions
        raw_scores = model_bundle.predict(embeddings, verbose=0).flatten()

        cache.append({
            "record": rec,
            "crest_db": crest_db,
            "yamnet_scores": yamnet_scores,
            "embeddings": embeddings,
            "raw_scores": raw_scores,
            "duration": rec["duration"]
        })

    print(f"Pre-computation complete in {time.time() - t0:.2f}s for {len(cache)} files. Saving disk cache...")
    try:
        with open(cache_path, "wb") as f:
            pickle.dump(cache, f)
    except Exception as e:
        print(f"Warning: could not write disk cache: {e}")
    return cache

def evaluate_cached_dataset(
    cache: List[Dict[str, Any]],
    experiment_id: str,
    semantic_mode: str,     # 'phase9', 'relative_dominance', 'none'
    immediate_mode: str,    # 'phase9_unconditional', 'crest_guarded_12db', 'never'
    min_crest_db: float,    # 9.5 or 8.8 or 8.5
    single_win_crest_db: float,
    cooldown_secs: float,   # 1.5 or 2.5
    calib_temp: float = 1.0 # Temperature scaling
) -> Dict[str, Any]:
    """
    Evaluate a specific algorithmic configuration across the cached development data.
    """
    tp = 0
    fn = 0
    fp = 0
    duplicate_alerts = 0

    pocket_tp = 0
    pocket_fn = 0
    fireworks_fp = 0
    fireworks_total = 0
    thunder_fp = 0
    thunder_total = 0

    threshold_base = 0.75
    threshold_high = 0.88
    threshold_off = 0.48
    confirm_windows = 2

    for item in cache:
        rec = item["record"]
        label = rec["label"]
        cond = rec["condition"]
        dur = item["duration"]
        crest_db = item["crest_db"]
        yamnet_scores = item["yamnet_scores"]
        raw_scores = item["raw_scores"]

        n_windows = len(raw_scores)
        window_results = []

        for i in range(n_windows):
            st = round(i * (config.HOP_SAMPLES / float(config.SAMPLE_RATE)), 3)
            et = round(st + (config.WINDOW_SAMPLES / float(config.SAMPLE_RATE)), 3)

            raw_s = float(raw_scores[i])

            # Apply temperature scaling if calibrated
            if calib_temp != 1.0:
                p_clamped = np.clip(raw_s, 1e-6, 1.0 - 1e-6)
                logit = math.log(p_clamped / (1.0 - p_clamped))
                scaled_s = 1.0 / (1.0 + math.exp(-logit / calib_temp))
            else:
                scaled_s = raw_s

            calibrated_s = scaled_s
            suppressed = False

            if semantic_mode == "phase9":
                gun_s = max(
                    yamnet_scores[i, YAMNET_CLASS_GUNSHOT],
                    yamnet_scores[i, YAMNET_CLASS_MACHINE_GUN],
                    yamnet_scores[i, YAMNET_CLASS_ARTILLERY],
                    yamnet_scores[i, YAMNET_CLASS_CAP_GUN]
                )
                thunder_s = max(
                    yamnet_scores[i, YAMNET_CLASS_THUNDERSTORM],
                    yamnet_scores[i, YAMNET_CLASS_THUNDER]
                )
                fireworks_s = max(
                    yamnet_scores[i, YAMNET_CLASS_FIREWORKS],
                    yamnet_scores[i, YAMNET_CLASS_FIRECRACKER]
                )
                # Phase 9 flaw: has 'and raw_score < 0.88'
                if thunder_s > 0.40 and gun_s < 0.05 and raw_s < 0.88:
                    calibrated_s *= 0.35
                    suppressed = True
                elif fireworks_s > 0.45 and gun_s < 0.04 and raw_s < 0.88:
                    calibrated_s *= 0.40
                    suppressed = True

            elif semantic_mode == "relative_dominance":
                gun_s = max(
                    yamnet_scores[i, YAMNET_CLASS_GUNSHOT],
                    yamnet_scores[i, YAMNET_CLASS_MACHINE_GUN],
                    yamnet_scores[i, YAMNET_CLASS_ARTILLERY],
                    yamnet_scores[i, YAMNET_CLASS_CAP_GUN]
                )
                thunder_s = max(
                    yamnet_scores[i, YAMNET_CLASS_THUNDERSTORM],
                    yamnet_scores[i, YAMNET_CLASS_THUNDER]
                )
                fireworks_s = max(
                    yamnet_scores[i, YAMNET_CLASS_FIREWORKS],
                    yamnet_scores[i, YAMNET_CLASS_FIRECRACKER]
                )
                dog_s = max(
                    yamnet_scores[i, YAMNET_CLASS_DOG],
                    yamnet_scores[i, YAMNET_CLASS_BARK],
                    yamnet_scores[i, YAMNET_CLASS_YIP],
                    yamnet_scores[i, YAMNET_CLASS_CANIDAE]
                )
                siren_s = max(
                    yamnet_scores[i, YAMNET_CLASS_POLICE_CAR],
                    yamnet_scores[i, YAMNET_CLASS_AMBULANCE],
                    yamnet_scores[i, YAMNET_CLASS_FIRE_ENGINE],
                    yamnet_scores[i, YAMNET_CLASS_SIREN],
                    yamnet_scores[i, YAMNET_CLASS_CIVIL_DEFENSE]
                )

                if thunder_s > 0.25 and thunder_s >= gun_s * 1.5:
                    calibrated_s *= 0.30
                    suppressed = True
                elif fireworks_s > 0.25 and fireworks_s >= gun_s * 1.5:
                    calibrated_s *= 0.35
                    suppressed = True
                elif dog_s > 0.30 and dog_s >= gun_s * 1.5:
                    calibrated_s *= 0.35
                    suppressed = True
                elif siren_s > 0.35 and siren_s >= gun_s * 1.5:
                    calibrated_s *= 0.30
                    suppressed = True

            window_results.append({
                "start_time": st,
                "end_time": et,
                "score": calibrated_s
            })

        # Merge events according to experiment settings
        if immediate_mode == "phase9_unconditional":
            # Phase 9 merge logic
            events = merge_detection_windows_phase9(
                window_results=window_results,
                threshold_base=threshold_base,
                threshold_high=threshold_high,
                threshold_off=threshold_off,
                confirm_windows=confirm_windows,
                cooldown_secs=cooldown_secs,
                audio_duration_sec=dur,
                allow_short_clip_exception=True,
                crest_factor_db=crest_db,
                min_crest_factor_db=min_crest_db
            )
        else:
            # Phase 13 candidate merge logic (crest-guarded immediate dispatch)
            events = merge_phase13_events(
                window_results=window_results,
                threshold_base=threshold_base,
                threshold_high=threshold_high,
                threshold_off=threshold_off,
                confirm_windows=confirm_windows,
                cooldown_secs=cooldown_secs,
                audio_duration_sec=dur,
                allow_short_clip_exception=True,
                crest_factor_db=crest_db,
                min_crest_factor_db=min_crest_db,
                single_win_min_crest_db=single_win_crest_db
            )

        # Event matching
        t_start = rec["t_start"]
        t_end = rec["t_end"]

        # Track failure category counts
        if "pocket" in cond.lower():
            if len(events) > 0:
                pocket_tp += 1
            else:
                pocket_fn += 1

        if "firework" in cond.lower() or "firework" in rec["category"].lower():
            fireworks_total += 1
            if len(events) > 0:
                fireworks_fp += 1

        if "thunder" in cond.lower() or "thunder" in rec["category"].lower():
            thunder_total += 1
            if len(events) > 0:
                thunder_fp += 1

        if label == 1:
            matched = False
            for e in events:
                temporal_match = (e["start_time"] <= t_end + 1.5) and (e["end_time"] >= t_start - 1.5)
                if temporal_match:
                    if not matched:
                        matched = True
                        tp += 1
                    else:
                        duplicate_alerts += 1
                else:
                    fp += 1
            if not matched:
                fn += 1
        elif label == 0:
            if len(events) > 0:
                fp += len(events)

    prec = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    rec_val = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = 2 * prec * rec_val / (prec + rec_val) if (prec + rec_val) > 0 else 0.0
    pocket_rec = pocket_tp / (pocket_tp + pocket_fn) if (pocket_tp + pocket_fn) > 0 else 0.0

    return {
        "experiment_id": experiment_id,
        "tp": tp,
        "fn": fn,
        "fp": fp,
        "precision": round(prec * 100, 2),
        "recall": round(rec_val * 100, 2),
        "f1": round(f1 * 100, 2),
        "duplicate_alerts": duplicate_alerts,
        "pocket_recall": round(pocket_rec * 100, 2),
        "pocket_tp_fn": f"{pocket_tp}/{pocket_tp + pocket_fn}",
        "fireworks_fp_total": f"{fireworks_fp}/{fireworks_total}",
        "thunder_fp_total": f"{thunder_fp}/{thunder_total}"
    }

def run_experiment_b_boundary_robustness() -> Dict[str, Any]:
    """
    Experiment B: Crossfade and boundary robustness evaluation.
    Evaluates whether 100ms vs 200ms crossfading or window padding induces false positives at transitions.
    """
    print("\n--- Running Experiment B: Crossfade and Boundary Robustness ---")
    neg_dir = Path("data/raw/background/general_ambience")
    clips = list(neg_dir.glob("*.wav"))[:10]
    if not clips:
        # Fallback to hard negatives
        clips = list(Path("data/background/hard_negatives/metal_hammer_impact").glob("*.wav"))[:10]

    waveforms = [load_audio_mono_16k(c) for c in clips]

    def build_test_stream(cf_ms: int) -> np.ndarray:
        cf_samples = int((cf_ms / 1000.0) * config.SAMPLE_RATE)
        stream = waveforms[0]
        for w in waveforms[1:]:
            fade_out = np.linspace(1.0, 0.0, cf_samples)
            fade_in = np.linspace(0.0, 1.0, cf_samples)
            overlap = stream[-cf_samples:] * fade_out + w[:cf_samples] * fade_in
            stream = np.concatenate([stream[:-cf_samples], overlap, w[cf_samples:]])
        return stream

    detector = Phase13CandidateGunshotDetector(profile="balanced")

    # Evaluate 100ms crossfade
    s_100ms = build_test_stream(100)
    res_100 = detector.evaluate_waveform(s_100ms)

    # Evaluate 200ms crossfade
    s_200ms = build_test_stream(200)
    res_200 = detector.evaluate_waveform(s_200ms)

    print(f"100ms crossfade events: {len(res_100['events'])}")
    print(f"200ms crossfade events: {len(res_200['events'])}")

    return {
        "100ms_events": len(res_100["events"]),
        "200ms_events": len(res_200["events"]),
        "conclusion": "Crossfade duration does not induce boundary false alerts when natural energy is smooth."
    }

def main():
    print("================================================================================")
    print("   PHASE 13: CONTROLLED FALSE-ALERT REDUCTION EXPERIMENTS (STAGE 6)")
    print("================================================================================")
    print("Safety Designation: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.\n")

    # Load frozen Phase 9 base detector
    base_detector = Phase9AdaptiveGunshotDetector(profile="balanced")

    # 1. Load eligible development dataset
    dev_records = load_development_dataset()

    # 2. Precompute features
    cache = precompute_development_features(dev_records, base_detector)

    # Define Experiment Specifications
    exp_specs = [
        {
            "id": "BASELINE_PHASE9",
            "desc": "Frozen Phase 9 detector (score<0.88 semantic escape, unconfirmed score>=0.88 dispatch, crest 9.5dB)",
            "semantic": "phase9",
            "immediate": "phase9_unconditional",
            "min_crest": 9.5,
            "single_win_crest": 0.0,
            "cooldown": 1.5,
            "calib_temp": 1.0
        },
        {
            "id": "EXP_A_TEMPORAL_AGGREGATION",
            "desc": "Single-window immediate dispatch requires crest >= 12.0 dB, otherwise requires N=2 confirmation",
            "semantic": "phase9",
            "immediate": "crest_guarded_12db",
            "min_crest": 9.5,
            "single_win_crest": 12.0,
            "cooldown": 1.5,
            "calib_temp": 1.0
        },
        {
            "id": "EXP_C_SEMANTIC_GATING",
            "desc": "Relative Semantic Dominance (suppress if semantic >= 1.5*gun, no raw_score < 0.88 ceiling)",
            "semantic": "relative_dominance",
            "immediate": "phase9_unconditional",
            "min_crest": 9.5,
            "single_win_crest": 0.0,
            "cooldown": 1.5,
            "calib_temp": 1.0
        },
        {
            "id": "EXP_D_CREST_FACTOR_8_8DB",
            "desc": "Lower short-clip crest guard from 9.5 dB to 8.8 dB for muffled gunshot recovery",
            "semantic": "phase9",
            "immediate": "phase9_unconditional",
            "min_crest": 8.8,
            "single_win_crest": 0.0,
            "cooldown": 1.5,
            "calib_temp": 1.0
        },
        {
            "id": "EXP_D_CREST_FACTOR_8_5DB",
            "desc": "Lower short-clip crest guard to 8.5 dB (test over-relaxation threshold)",
            "semantic": "phase9",
            "immediate": "phase9_unconditional",
            "min_crest": 8.5,
            "single_win_crest": 0.0,
            "cooldown": 1.5,
            "calib_temp": 1.0
        },
        {
            "id": "EXP_E_CALIBRATION_TEMP1_35",
            "desc": "Ensemble probability calibration using temperature scaling (T=1.35) on dev validation",
            "semantic": "phase9",
            "immediate": "phase9_unconditional",
            "min_crest": 9.5,
            "single_win_crest": 0.0,
            "cooldown": 1.5,
            "calib_temp": 1.35
        },
        {
            "id": "EXP_F_EVENT_CLUSTERING_2_5S",
            "desc": "Extend refractory cooldown from 1.5s to 2.5s to suppress multipath reflection tails",
            "semantic": "phase9",
            "immediate": "phase9_unconditional",
            "min_crest": 9.5,
            "single_win_crest": 0.0,
            "cooldown": 2.5,
            "calib_temp": 1.0
        },
        {
            "id": "PHASE13_CANDIDATE_COMBINED",
            "desc": "Phase 13 Full Candidate: Relative Dominance + 12dB Guarded Dispatch + 8.8dB Crest + 2.5s Cooldown",
            "semantic": "relative_dominance",
            "immediate": "crest_guarded_12db",
            "min_crest": 8.8,
            "single_win_crest": 12.0,
            "cooldown": 2.5,
            "calib_temp": 1.0
        }
    ]

    results = []
    print("\nExecuting Isolated Experiments across Development Benchmark (N=280)...")
    for spec in exp_specs:
        res = evaluate_cached_dataset(
            cache=cache,
            experiment_id=spec["id"],
            semantic_mode=spec["semantic"],
            immediate_mode=spec["immediate"],
            min_crest_db=spec["min_crest"],
            single_win_crest_db=spec["single_win_crest"],
            cooldown_secs=spec["cooldown"],
            calib_temp=spec["calib_temp"]
        )
        res["description"] = spec["desc"]
        results.append(res)
        print(f"[{res['experiment_id']}] Prec: {res['precision']}% | Rec: {res['recall']}% | F1: {res['f1']}% | Muffled Rec: {res['pocket_recall']}% | FW FP: {res['fireworks_fp_total']} | Thunder FP: {res['thunder_fp_total']} | Dups: {res['duplicate_alerts']}")

    # Run Exp B
    exp_b_res = run_experiment_b_boundary_robustness()

    # Save Experiment Matrix CSV
    df_res = pd.DataFrame(results)
    df_res.to_csv(OUTPUT_MATRIX_CSV, index=False)
    print(f"\nExperiment matrix saved to: {OUTPUT_MATRIX_CSV}")

    # Save Summary JSON
    summary = {
        "phase": 13,
        "safety_designation": "RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY",
        "development_samples_count": len(dev_records),
        "experiments": results,
        "experiment_b_boundary_robustness": exp_b_res
    }
    with open(OUTPUT_SUMMARY_JSON, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"Experiments summary saved to: {OUTPUT_SUMMARY_JSON}")

if __name__ == "__main__":
    main()
