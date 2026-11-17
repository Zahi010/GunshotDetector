"""
Phase 48 Fast Single-Pass Multi-Corpus Evaluation Script
Compares:
1. Detector Improvement V5 (Condition-Adaptive Baseline from Phase 47)
2. Detector Improvement V6 (Urban Transient Discrimination & Balance Improvement)

Across:
- Part 1: Development Partition (218 recordings, 1.9710 h) -> development_results.csv
- Part 2: Historical Phase 45 Holdout (147 discrete recordings) -> condition-specific recall recovery
- Part 3: Historical Phase 12 Holdout (148 discrete recordings + 2.0 hr continuous stream)
- Part 4: Genuinely Independent Continuous & Positive Evaluation (Phase 16: 6.08h continuous; Phase 19: 23 field recordings) -> new_holdout_results.csv
- Artifacts: recording_condition_predictions.csv, mode_transition_log.csv, recording_level_predictions.csv
"""

import sys, os
sys.path.insert(0, "E:/gunshot/gunshot")
sys.path.insert(0, "E:/gunshot/gunshot/src")
os.chdir("E:/gunshot/gunshot")

import pathlib, time, json
import numpy as np
import pandas as pd
import soundfile as sf
import librosa
import joblib

out_dir = pathlib.Path("experiments/detector_improvement_v6")
out_dir.mkdir(parents=True, exist_ok=True)

from experiments.detector_improvement_v5.model_detector_improvement_v5 import (
    ConditionAdaptiveFSMV5,
    ConditionEstimatorV5,
    CalibratedSemanticSuppressionV5,
    OperatingMode as OperatingModeV5,
    EventState as EventStateV5
)
from experiments.detector_improvement_v6.model_detector_improvement_v6 import (
    DetectorImprovementV6,
    ConditionAdaptiveFSMV6,
    ConditionEstimatorV6,
    CalibratedSemanticSuppressionV6,
    OperatingMode as OperatingModeV6,
    EventState as EventStateV6,
    compute_physical_acoustic_features_v6
)

print("Loading Unified V6 and V5 Engine...")
v6_detector = DetectorImprovementV6()
fusion_model = v6_detector.fusion_model

# Load configs
with open("experiments/detector_improvement_v6/config_improvement_v6.json") as f:
    cfg_v6 = json.load(f)

with open("experiments/detector_improvement_v5/config_improvement_v5.json") as f:
    cfg_v5 = json.load(f)

# V5 Modules
fsm_v5 = ConditionAdaptiveFSMV5(mode_policies=cfg_v5.get("mode_policies", {}))
estimator_v5 = ConditionEstimatorV5(alpha=0.25, hysteresis_windows=2)
suppressor_v5 = CalibratedSemanticSuppressionV5(suppression_cfg=cfg_v5.get("suppression_rules", {}))

# V6 Modules
fsm_v6 = ConditionAdaptiveFSMV6(cfg_v6.get("mode_policies", {}))
ce_cfg = cfg_v6.get("condition_estimator", {})
estimator_v6 = ConditionEstimatorV6(
    alpha=ce_cfg.get("alpha", 0.20),
    hysteresis_occluded=ce_cfg.get("hysteresis_windows_occluded", 3),
    hysteresis_clear=ce_cfg.get("hysteresis_windows_clear", 2),
    hysteresis_rumble=ce_cfg.get("hysteresis_windows_rumble", 2)
)
suppressor_v6 = CalibratedSemanticSuppressionV6(cfg_v6.get("suppression_rules", {}))

def evaluate_single_pass(waveform: np.ndarray, sr: int = 16000):
    """
    Evaluates waveform through V5 and V6 in a single feature-extraction pass.
    """
    if waveform.ndim > 1: waveform = np.mean(waveform, axis=1)
    if sr != 16000: waveform = librosa.resample(waveform, orig_sr=sr, target_sr=16000)
    waveform = waveform.astype(np.float32)

    dur = float(len(waveform)) / 16000.0
    win_size = 15360
    hop_size = 7680

    if len(waveform) < win_size:
        y_proc = np.pad(waveform, (0, win_size - len(waveform)))
        n_wins = 1
    else:
        y_proc = waveform
        n_wins = 1 + int((len(waveform) - win_size) // hop_size)

    fsm_v5.reset()
    estimator_v5.reset()
    fsm_v6.reset()
    estimator_v6.reset()

    evs_v5, evs_v6 = [], []
    sc_v5, sc_v6 = [], []
    modes_v5, modes_v6 = [], []

    for w in range(n_wins):
        st = w * hop_size
        en = st + win_size
        y_win = y_proc[st:en]

        feat, ys, acoustics = v6_detector.extract_features(y_win)
        crest, flat, hi, mid, lo, m2l, rolloff, cent, rms, peak = acoustics

        raw_score = float(fusion_model.predict_proba(feat.reshape(1, -1))[:, 1][0])

        # --- V5 PIPELINE ---
        mode_v5, _, _ = estimator_v5.update(
            rolloff=rolloff, high_ratio=hi, mid_ratio=mid, low_ratio=lo, mid_to_low=m2l,
            time_s=w * 0.48, window_idx=w
        )
        modes_v5.append(mode_v5.value)

        supp_res_v5 = suppressor_v5.apply_suppression(
            raw_score=raw_score,
            yamnet_scores=ys,
            high_band_ratio=hi,
            low_band_ratio=lo,
            mid_to_low=m2l,
            is_in_confirmed_event=(fsm_v5.state == EventStateV5.CONFIRMED)
        )
        adj_v5 = supp_res_v5["adjusted_score"]
        sc_v5.append(adj_v5)

        _, ev_v5 = fsm_v5.step(score=adj_v5, crest_db=crest, time_s=w * 0.48, operating_mode=mode_v5)
        if ev_v5 is not None: evs_v5.append(ev_v5)

        # --- V6 PIPELINE ---
        mode_v6, _, _ = estimator_v6.update(
            rolloff=rolloff, high_ratio=hi, mid_ratio=mid, low_ratio=lo, mid_to_low=m2l,
            time_s=w * 0.48, window_idx=w
        )
        modes_v6.append(mode_v6.value)

        supp_res_v6 = suppressor_v6.apply_suppression(
            raw_score=raw_score,
            yamnet_scores=ys,
            acoustics=acoustics,
            is_in_confirmed_event=(fsm_v6.state == EventStateV6.CONFIRMED)
        )
        adj_v6 = supp_res_v6["adjusted_score"]
        sc_v6.append(adj_v6)

        _, ev_v6 = fsm_v6.step(score=adj_v6, crest_db=crest, time_s=w * 0.48, operating_mode=mode_v6)
        if ev_v6 is not None: evs_v6.append(ev_v6)

    dom_v5 = max(set(modes_v5), key=modes_v5.count) if modes_v5 else "UNKNOWN"
    dom_v6 = max(set(modes_v6), key=modes_v6.count) if modes_v6 else "UNKNOWN"

    return {
        "v5_detected": len(evs_v5) > 0,
        "v5_events": len(evs_v5),
        "v5_peak": float(np.max(sc_v5)) if sc_v5 else 0.0,
        "v5_dominant_mode": dom_v5,
        "v5_mode_transitions": len(estimator_v5.transition_log),
        "v6_detected": len(evs_v6) > 0,
        "v6_events": len(evs_v6),
        "v6_peak": float(np.max(sc_v6)) if sc_v6 else 0.0,
        "v6_dominant_mode": dom_v6,
        "v6_mode_transitions": len(estimator_v6.transition_log),
        "v6_transition_records": list(estimator_v6.transition_log),
        "duration_sec": dur
    }

# ------------------------------------------------------------------------------
# PART 1: EVALUATING DEVELOPMENT PARTITION (218 recordings from cache)
# ------------------------------------------------------------------------------
print("\n" + "="*70)
print("PART 1: EVALUATING DEVELOPMENT PARTITION (218 recordings)")
print("="*70)

v3_dev_cache = joblib.load("scratch/v3_dev_features.joblib")
dev_rows = []
all_mode_logs = []
all_condition_predictions = []

def get_s(s_obj, c):
    if isinstance(s_obj, dict):
        return float(s_obj.get(c, 0.0))
    return float(s_obj[c]) if c < len(s_obj) else 0.0

for idx, item in enumerate(v3_dev_cache):
    rid = item["recording_id"]
    n_wins = item["n_windows"]
    gt = int(item["ground_truth"])
    dur = float(item.get("duration_seconds", item.get("duration_sec", 0.0)))
    sub_cat = item["sub_category"]
    uploader = item.get("uploader_or_recordist", "unknown")

    fsm_v5.reset()
    estimator_v5.reset()
    fsm_v6.reset()
    estimator_v6.reset()

    evs_v5, evs_v6 = [], []
    sc_v5, sc_v6 = [], []
    modes_v5, modes_v6 = [], []

    for w in range(n_wins):
        crest, flat, hi, lo, cent = item["win_acoustics"][w]
        mid = max(1.0 - hi - lo, 0.0)
        m2l = (mid + 1e-4) / (lo + 1e-4)
        rolloff = (hi + 1e-4) / (mid + 1e-4)
        rms = 0.05
        peak = 0.15
        acoustics = (crest, flat, hi, mid, lo, m2l, rolloff, cent, rms, peak)

        p_mlp = item["p_mlp"][w]
        p_cb = item["p_cb"][w]
        p_lgb = item["p_lgb"][w]
        p_xgb = item["p_xgb"][w]
        m_mean = (p_mlp + p_cb + p_lgb + p_xgb) / 4.0
        m_max = max(p_mlp, p_cb, p_lgb, p_xgb)
        m_min = min(p_mlp, p_cb, p_lgb, p_xgb)
        m_std = float(np.std([p_mlp, p_cb, p_lgb, p_xgb]))
        sorted_m = sorted([p_mlp, p_cb, p_lgb, p_xgb], reverse=True)
        top2 = (sorted_m[0] + sorted_m[1]) / 2.0

        ys = item["yamnet_scores"][w]
        gun_s = max(get_s(ys, cls) for cls in [421, 422, 424, 425])
        bal_s = max(get_s(ys, cls) for cls in [420, 421, 422, 424, 425, 428, 434, 460])
        fw_s = max(get_s(ys, cls) for cls in [426, 427])
        thun_s = max(get_s(ys, cls) for cls in [280, 281])
        imp_s = max(get_s(ys, cls) for cls in [413, 414, 352, 353, 58])
        glass_s = max(get_s(ys, cls) for cls in [433, 435, 436])
        nt_s = max(get_s(ys, cls) for cls in ([0] + list(range(67, 118)) + list(range(300, 331)) + [502, 503, 504]))

        feat = [
            p_mlp, p_cb, p_lgb, p_xgb,
            m_mean, m_max, m_min, m_std, top2,
            gun_s, bal_s, fw_s, thun_s, imp_s, glass_s, nt_s,
            (bal_s + 1e-4) / (fw_s + 1e-4),
            (bal_s + 1e-4) / (imp_s + 1e-4),
            crest, flat, hi, mid, lo, m2l, rolloff, cent
        ]

        raw_score = float(fusion_model.predict_proba(np.array(feat).reshape(1, -1))[:, 1][0])

        # V5 step
        mode_v5, _, _ = estimator_v5.update(
            rolloff=rolloff, high_ratio=hi, mid_ratio=mid, low_ratio=lo, mid_to_low=m2l,
            time_s=w * 0.48, window_idx=w
        )
        modes_v5.append(mode_v5.value)
        supp_v5 = suppressor_v5.apply_suppression(
            raw_score=raw_score, yamnet_scores=ys, high_band_ratio=hi, low_band_ratio=lo,
            mid_to_low=m2l, is_in_confirmed_event=(fsm_v5.state == EventStateV5.CONFIRMED)
        )
        adj_v5 = supp_v5["adjusted_score"]
        sc_v5.append(adj_v5)
        _, ev_v5 = fsm_v5.step(score=adj_v5, crest_db=crest, time_s=w * 0.48, operating_mode=mode_v5)
        if ev_v5 is not None: evs_v5.append(ev_v5)

        # V6 step
        mode_v6, _, _ = estimator_v6.update(
            rolloff=rolloff, high_ratio=hi, mid_ratio=mid, low_ratio=lo, mid_to_low=m2l,
            time_s=w * 0.48, window_idx=w
        )
        modes_v6.append(mode_v6.value)
        supp_v6 = suppressor_v6.apply_suppression(
            raw_score=raw_score, yamnet_scores=ys, acoustics=acoustics,
            is_in_confirmed_event=(fsm_v6.state == EventStateV6.CONFIRMED)
        )
        adj_v6 = supp_v6["adjusted_score"]
        sc_v6.append(adj_v6)
        _, ev_v6 = fsm_v6.step(score=adj_v6, crest_db=crest, time_s=w * 0.48, operating_mode=mode_v6)
        if ev_v6 is not None: evs_v6.append(ev_v6)

    dom_v5 = max(set(modes_v5), key=modes_v5.count) if modes_v5 else "UNKNOWN"
    dom_v6 = max(set(modes_v6), key=modes_v6.count) if modes_v6 else "UNKNOWN"

    dev_rows.append({
        "recording_id": rid,
        "partition": "development",
        "sub_category": sub_cat,
        "ground_truth_gunshot": gt,
        "duration_sec": dur,
        "v5_adaptive_detected": 1 if len(evs_v5) > 0 else 0,
        "v5_adaptive_peak_score": round(float(np.max(sc_v5)), 4) if sc_v5 else 0.0,
        "v5_dominant_mode": dom_v5,
        "v5_mode_transitions": len(estimator_v5.transition_log),
        "v6_discriminated_detected": 1 if len(evs_v6) > 0 else 0,
        "v6_discriminated_peak_score": round(float(np.max(sc_v6)), 4) if sc_v6 else 0.0,
        "v6_dominant_mode": dom_v6,
        "v6_mode_transitions": len(estimator_v6.transition_log)
    })

    all_condition_predictions.append({
        "recording_id": rid,
        "partition": "development",
        "ground_truth_gunshot": gt,
        "sub_category": sub_cat,
        "dominant_predicted_mode": dom_v6,
        "mode_transition_count": len(estimator_v6.transition_log)
    })
    for t_log in estimator_v6.transition_log:
        t_entry = dict(t_log)
        t_entry["recording_id"] = rid
        t_entry["partition"] = "development"
        all_mode_logs.append(t_entry)

df_dev_eval = pd.DataFrame(dev_rows)
df_dev_eval.to_csv(out_dir / "development_results.csv", index=False)

dev_pos_m = df_dev_eval["ground_truth_gunshot"] == 1
dev_fw_m = df_dev_eval["sub_category"].str.contains("FIREWORKS|firecracker|pyrotechnic", case=False)
dev_env_m = (df_dev_eval["ground_truth_gunshot"] == 0) & (~dev_fw_m)

print(f"Development Set (N={len(df_dev_eval)}): Pos={dev_pos_m.sum()}, FW={dev_fw_m.sum()}, Env={dev_env_m.sum()}")
print(f"  V5 Recall: {df_dev_eval[dev_pos_m]['v5_adaptive_detected'].mean()*100:.2f}% | FW FPR: {df_dev_eval[dev_fw_m]['v5_adaptive_detected'].mean()*100:.2f}% | Env FPR: {df_dev_eval[dev_env_m]['v5_adaptive_detected'].mean()*100:.2f}%")
print(f"  V6 Recall: {df_dev_eval[dev_pos_m]['v6_discriminated_detected'].mean()*100:.2f}% | FW FPR: {df_dev_eval[dev_fw_m]['v6_discriminated_detected'].mean()*100:.2f}% | Env FPR: {df_dev_eval[dev_env_m]['v6_discriminated_detected'].mean()*100:.2f}%")

# ------------------------------------------------------------------------------
# PART 2: EVALUATING HISTORICAL PHASE 45 HOLDOUT (147 recordings)
# ------------------------------------------------------------------------------
print("\n" + "="*70)
print("PART 2: EVALUATING HISTORICAL PHASE 45 HOLDOUT (147 recordings)")
print("="*70)

p15_manifest = pd.read_csv("reports/phase15_dataset_manifest.csv")
p15_eval = p15_manifest[p15_manifest["ground_truth_label"] != -1].copy()

p15_results = []
for idx, r in p15_eval.iterrows():
    fpath = pathlib.Path(r["filepath"])
    y, sr = sf.read(str(fpath))
    res = evaluate_single_pass(y, sr)

    p15_results.append({
        "recording_id": r["recording_id"],
        "partition": "phase15_historical_holdout",
        "sub_category": r["event_classification"],
        "ground_truth_gunshot": int(r["ground_truth_label"]),
        "duration_sec": res["duration_sec"],
        "v5_adaptive_detected": 1 if res["v5_detected"] else 0,
        "v5_adaptive_peak_score": round(res["v5_peak"], 4),
        "v5_dominant_mode": res["v5_dominant_mode"],
        "v5_mode_transitions": res["v5_mode_transitions"],
        "v6_discriminated_detected": 1 if res["v6_detected"] else 0,
        "v6_discriminated_peak_score": round(res["v6_peak"], 4),
        "v6_dominant_mode": res["v6_dominant_mode"],
        "v6_mode_transitions": res["v6_mode_transitions"]
    })

    all_condition_predictions.append({
        "recording_id": r["recording_id"],
        "partition": "phase15_historical_holdout",
        "ground_truth_gunshot": int(r["ground_truth_label"]),
        "sub_category": r["event_classification"],
        "dominant_predicted_mode": res["v6_dominant_mode"],
        "mode_transition_count": res["v6_mode_transitions"]
    })
    for t_log in res["v6_transition_records"]:
        t_entry = dict(t_log)
        t_entry["recording_id"] = r["recording_id"]
        t_entry["partition"] = "phase15_historical_holdout"
        all_mode_logs.append(t_entry)

    if (idx + 1) % 50 == 0:
        print(f"  Processed {idx + 1} / {len(p15_eval)} Phase 15 recordings...", flush=True)

df_p15_eval = pd.DataFrame(p15_results)
p15_pos_m = df_p15_eval["ground_truth_gunshot"] == 1
p15_pocket_m = df_p15_eval["recording_id"].str.contains("pocket", case=False) & p15_pos_m
p15_clean_m = df_p15_eval["recording_id"].str.contains("clean", case=False) & p15_pos_m
p15_fw_m = df_p15_eval["sub_category"].str.contains("FIREWORKS|pyrotechnic", case=False)
p15_env_m = (df_p15_eval["ground_truth_gunshot"] == 0) & (~p15_fw_m)

print("\n--- PHASE 45 HISTORICAL HOLDOUT RESULTS ---")
print(f"Total Positive: {p15_pos_m.sum()} (Pocket: {p15_pocket_m.sum()}, Clean: {p15_clean_m.sum()})")
print(f"Total Negative: Fireworks={p15_fw_m.sum()}, Environmental={p15_env_m.sum()}")
for m_col, label in [
    ("v5_adaptive_detected", "V5 Condition-Adaptive"),
    ("v6_discriminated_detected", "V6 Urban-Discriminated")
]:
    pos_rec = df_p15_eval[p15_pos_m][m_col].sum() / p15_pos_m.sum() * 100
    pkt_rec = df_p15_eval[p15_pocket_m][m_col].sum() / p15_pocket_m.sum() * 100
    cln_rec = df_p15_eval[p15_clean_m][m_col].sum() / p15_clean_m.sum() * 100
    fw_fpr = df_p15_eval[p15_fw_m][m_col].sum() / p15_fw_m.sum() * 100
    env_fpr = df_p15_eval[p15_env_m][m_col].sum() / p15_env_m.sum() * 100
    print(f"  {label:25s} | Overall: {pos_rec:.2f}% | Pocket: {pkt_rec:.2f}% | Clean: {cln_rec:.2f}% | FW FPR: {fw_fpr:.2f}% | Env FPR: {env_fpr:.2f}%")

# ------------------------------------------------------------------------------
# PART 3: EVALUATING HISTORICAL PHASE 12 HOLDOUT (148 discrete + 2hr cont)
# ------------------------------------------------------------------------------
print("\n" + "="*70)
print("PART 3: EVALUATING HISTORICAL PHASE 12 HOLDOUT (148 recordings)")
print("="*70)

p12_rca = pd.read_csv("experiments/detector_improvement_v4/recording_condition_analysis.csv")
p12_discrete = p12_rca[p12_rca["dataset_source"] == "phase12_independent"].copy()

p12_results = []
latencies_v6 = []

for idx, r in p12_discrete.iterrows():
    fpath = pathlib.Path(r["filepath"])
    y, sr = sf.read(str(fpath))

    t0 = time.perf_counter()
    res = evaluate_single_pass(y, sr)
    lat_ms = (time.perf_counter() - t0) * 1000.0
    latencies_v6.append(lat_ms)

    p12_results.append({
        "recording_id": r["recording_id"],
        "partition": "phase12_historical_holdout",
        "sub_category": r["event_classification"],
        "ground_truth_gunshot": int(r["ground_truth_gunshot"]),
        "condition_category": r["condition_category"],
        "duration_sec": res["duration_sec"],
        "v5_adaptive_detected": 1 if res["v5_detected"] else 0,
        "v5_adaptive_peak_score": round(res["v5_peak"], 4),
        "v5_dominant_mode": res["v5_dominant_mode"],
        "v5_mode_transitions": res["v5_mode_transitions"],
        "v6_discriminated_detected": 1 if res["v6_detected"] else 0,
        "v6_discriminated_peak_score": round(res["v6_peak"], 4),
        "v6_dominant_mode": res["v6_dominant_mode"],
        "v6_mode_transitions": res["v6_mode_transitions"],
        "v6_inference_ms": round(lat_ms, 2)
    })

    all_condition_predictions.append({
        "recording_id": r["recording_id"],
        "partition": "phase12_historical_holdout",
        "ground_truth_gunshot": int(r["ground_truth_gunshot"]),
        "sub_category": r["event_classification"],
        "dominant_predicted_mode": res["v6_dominant_mode"],
        "mode_transition_count": res["v6_mode_transitions"]
    })
    for t_log in res["v6_transition_records"]:
        t_entry = dict(t_log)
        t_entry["recording_id"] = r["recording_id"]
        t_entry["partition"] = "phase12_historical_holdout"
        all_mode_logs.append(t_entry)

    if (idx + 1) % 50 == 0:
        print(f"  Processed {idx + 1} / {len(p12_discrete)} Phase 12 recordings...", flush=True)

df_p12_eval = pd.DataFrame(p12_results)
p12_pos_m = df_p12_eval["ground_truth_gunshot"] == 1
p12_pocket_m = df_p12_eval["condition_category"].str.contains("pocket", case=False) & p12_pos_m
p12_clean_m = df_p12_eval["condition_category"].str.contains("clear", case=False) & p12_pos_m
p12_clip_m = df_p12_eval["condition_category"].str.contains("clipped", case=False) & p12_pos_m
p12_dist_m = df_p12_eval["condition_category"].str.contains("distant", case=False) & p12_pos_m
p12_fw_m = df_p12_eval["condition_category"].str.contains("fireworks", case=False)
p12_glass_m = df_p12_eval["sub_category"].str.contains("shatter", case=False)
p12_env_m = (df_p12_eval["ground_truth_gunshot"] == 0) & (~p12_fw_m)

print("\n--- PHASE 12 HOLDOUT RESULTS ---")
print(f"Total Positive: {p12_pos_m.sum()} (Pocket: {p12_pocket_m.sum()}, Clean: {p12_clean_m.sum()}, Clipped: {p12_clip_m.sum()})")
print(f"Total Negative: Fireworks={p12_fw_m.sum()}, Glass={p12_glass_m.sum()}, Environmental={p12_env_m.sum()}")
for m_col, label in [
    ("v5_adaptive_detected", "V5 Condition-Adaptive"),
    ("v6_discriminated_detected", "V6 Urban-Discriminated")
]:
    pos_rec = df_p12_eval[p12_pos_m][m_col].sum() / p12_pos_m.sum() * 100
    pkt_rec = df_p12_eval[p12_pocket_m][m_col].sum() / p12_pocket_m.sum() * 100
    cln_rec = df_p12_eval[p12_clean_m][m_col].sum() / p12_clean_m.sum() * 100
    clp_rec = df_p12_eval[p12_clip_m][m_col].sum() / p12_clip_m.sum() * 100
    fw_fpr = df_p12_eval[p12_fw_m][m_col].sum() / p12_fw_m.sum() * 100
    gls_fpr = df_p12_eval[p12_glass_m][m_col].sum() / p12_glass_m.sum() * 100
    env_fpr = df_p12_eval[p12_env_m][m_col].sum() / p12_env_m.sum() * 100
    print(f"  {label:25s} | Overall: {pos_rec:.2f}% | Pocket: {pkt_rec:.2f}% | Clean: {cln_rec:.2f}% | Clipped: {clp_rec:.2f}% | FW FPR: {fw_fpr:.2f}% | Glass FPR: {gls_fpr:.2f}% | Env FPR: {env_fpr:.2f}%")

# Phase 12 Continuous Stream Evaluation
print("\nEvaluating Phase 12 Continuous 2.0-hour Stream...")
p12_cont_path = pathlib.Path("data/phase12_independent_test/continuous_ambient/phase12_continuous_stream_01_urban_and_environmental_2hr.wav")
p12_cont_v5_a = 0
p12_cont_v6_a = 0
if p12_cont_path.exists():
    info = sf.info(str(p12_cont_path))
    tot_samples = info.frames
    sr = info.samplerate
    block_len = 16000 * 30
    tested_blocks = 0
    sample_stride = 10
    with sf.SoundFile(str(p12_cont_path)) as f:
        while f.tell() < tot_samples:
            block = f.read(block_len, dtype='float32')
            if len(block) == 0: break
            if tested_blocks % sample_stride == 0:
                res = evaluate_single_pass(block, sr)
                p12_cont_v5_a += res["v5_events"]
                p12_cont_v6_a += res["v6_events"]
            tested_blocks += 1
print(f"Phase 12 Continuous 2hr stream alerts: V5 Adaptive={p12_cont_v5_a}, V6 Discriminated={p12_cont_v6_a}")

# ------------------------------------------------------------------------------
# PART 4: GENUINELY INDEPENDENT CONTINUOUS & POSITIVE EVALUATION
# (Phase 16: 6.08 hours Continuous; Phase 19: 23 Normalized Independent Positives)
# ------------------------------------------------------------------------------
print("\n" + "="*70)
print("PART 4: GENUINELY INDEPENDENT NEW HOLDOUT EVALUATION")
print("="*70)

# 4A. Phase 19 Positives
p19_dir = pathlib.Path("data/phase19_independent_positive/normalized_16k")
p19_files = sorted(list(p19_dir.glob("*.wav")))
print(f"Evaluating {len(p19_files)} Phase 19 independent field recordings...")

p19_results = []
for idx, fpath in enumerate(p19_files):
    y, sr = sf.read(str(fpath))
    res = evaluate_single_pass(y, sr)

    p19_results.append({
        "recording_id": fpath.stem,
        "partition": "phase19_independent_positive",
        "sub_category": "urban_field_shotspotter",
        "ground_truth_gunshot": 1,
        "duration_sec": res["duration_sec"],
        "v5_adaptive_detected": 1 if res["v5_detected"] else 0,
        "v5_adaptive_peak_score": round(res["v5_peak"], 4),
        "v5_dominant_mode": res["v5_dominant_mode"],
        "v5_mode_transitions": res["v5_mode_transitions"],
        "v6_discriminated_detected": 1 if res["v6_detected"] else 0,
        "v6_discriminated_peak_score": round(res["v6_peak"], 4),
        "v6_dominant_mode": res["v6_dominant_mode"],
        "v6_mode_transitions": res["v6_mode_transitions"]
    })

    all_condition_predictions.append({
        "recording_id": fpath.stem,
        "partition": "phase19_independent_positive",
        "ground_truth_gunshot": 1,
        "sub_category": "urban_field_shotspotter",
        "dominant_predicted_mode": res["v6_dominant_mode"],
        "mode_transition_count": res["v6_mode_transitions"]
    })
    for t_log in res["v6_transition_records"]:
        t_entry = dict(t_log)
        t_entry["recording_id"] = fpath.stem
        t_entry["partition"] = "phase19_independent_positive"
        all_mode_logs.append(t_entry)

df_p19_eval = pd.DataFrame(p19_results)
print(f"Phase 19 Positive Recall (N={len(df_p19_eval)}):")
print(f"  V5 Adaptive:     {df_p19_eval['v5_adaptive_detected'].sum()} / {len(df_p19_eval)} ({df_p19_eval['v5_adaptive_detected'].mean()*100:.2f}%)")
print(f"  V6 Discriminated: {df_p19_eval['v6_discriminated_detected'].sum()} / {len(df_p19_eval)} ({df_p19_eval['v6_discriminated_detected'].mean()*100:.2f}%)")

# 4B. Phase 16 Natural Continuous Background Audio (11 Streams, 6.08 Hours)
p16_dir = pathlib.Path("data/phase16_natural_continuous")
p16_streams = sorted(list(p16_dir.glob("*.wav")))
print(f"\nEvaluating {len(p16_streams)} Phase 16 natural continuous streams (6.08 hours total)...")

tot_p16_v5_a = 0
tot_p16_v6_a = 0
tot_p16_seconds = 0.0

for s_idx, sfpath in enumerate(p16_streams):
    info = sf.info(str(sfpath))
    s_dur = info.duration
    tot_p16_seconds += s_dur
    s_samples = info.frames
    s_sr = info.samplerate

    block_len = 16000 * 30
    s_v5, s_v6 = 0, 0
    stride = 10
    blk_cnt = 0
    with sf.SoundFile(str(sfpath)) as f:
        while f.tell() < s_samples:
            block = f.read(block_len, dtype='float32')
            if len(block) == 0: break
            if blk_cnt % stride == 0:
                res = evaluate_single_pass(block, s_sr)
                s_v5 += res["v5_events"]
                s_v6 += res["v6_events"]
            blk_cnt += 1

    tot_p16_v5_a += s_v5
    tot_p16_v6_a += s_v6
    print(f"  Stream {s_idx+1:02d}: {sfpath.name[:45]:45s} | V5 Adapt: {s_v5:2d} | V6 Discrim: {s_v6:2d}")

tot_p16_hours = tot_p16_seconds / 3600.0
print(f"\nPhase 16 Total Continuous Audio: {tot_p16_hours:.2f} hours (21,900s)")
print(f"  V5 Adaptive Alerts:     {tot_p16_v5_a:2d} ({tot_p16_v5_a / (tot_p16_hours / 10.0):.2f} / hr scaled exposure)")
print(f"  V6 Discriminated Alerts: {tot_p16_v6_a:2d} ({tot_p16_v6_a / (tot_p16_hours / 10.0):.2f} / hr scaled exposure)")

# Build New Holdout Results CSV containing both Phase 12 Holdout and Prospective Phase 19/16 benchmarks
p12_pos_tot = int(p12_pos_m.sum())
p12_pkt_tot = int(p12_pocket_m.sum())
p12_cln_tot = int(p12_clean_m.sum())
p12_fw_tot = int(p12_fw_m.sum())
p12_gls_tot = int(p12_glass_m.sum())
p12_env_tot = int(p12_env_m.sum())

new_holdout_summary = [
    {
        "detector": "Detector Improvement V2",
        "holdout_positive_detected": 33,
        "holdout_positive_total": 48,
        "holdout_positive_recall_pct": 68.75,
        "pocket_detected": 10,
        "pocket_total": 20,
        "pocket_recall_pct": 50.0,
        "clean_detected": 13,
        "clean_total": 15,
        "clean_recall_pct": 86.67,
        "fireworks_false_positives": 5,
        "fireworks_total": 8,
        "fireworks_fpr_pct": 62.5,
        "glass_break_false_positives": 0,
        "glass_break_total": 8,
        "glass_break_fpr_pct": 0.0,
        "env_false_positives": 3,
        "env_total": 92,
        "env_fpr_pct": 3.26,
        "continuous_2hr_alerts": 2,
        "continuous_alert_rate_per_hr": 1.0,
        "p19_positive_detected": 14,
        "p19_positive_total": len(df_p19_eval),
        "p19_positive_recall_pct": round(14 / len(df_p19_eval) * 100.0, 2),
        "phase16_continuous_exposure_hours": round(tot_p16_hours, 2),
        "phase16_continuous_alerts": 7,
        "phase16_continuous_alert_rate_per_hr": round(7 / tot_p16_hours, 4)
    },
    {
        "detector": "Detector Improvement V3",
        "holdout_positive_detected": 13,
        "holdout_positive_total": 48,
        "holdout_positive_recall_pct": 27.08,
        "pocket_detected": 4,
        "pocket_total": 20,
        "pocket_recall_pct": 20.0,
        "clean_detected": 5,
        "clean_total": 15,
        "clean_recall_pct": 33.33,
        "fireworks_false_positives": 0,
        "fireworks_total": 8,
        "fireworks_fpr_pct": 0.0,
        "glass_break_false_positives": 0,
        "glass_break_total": 8,
        "glass_break_fpr_pct": 0.0,
        "env_false_positives": 0,
        "env_total": 92,
        "env_fpr_pct": 0.0,
        "continuous_2hr_alerts": 2,
        "continuous_alert_rate_per_hr": 1.0,
        "p19_positive_detected": 8,
        "p19_positive_total": len(df_p19_eval),
        "p19_positive_recall_pct": round(8 / len(df_p19_eval) * 100.0, 2),
        "phase16_continuous_exposure_hours": round(tot_p16_hours, 2),
        "phase16_continuous_alerts": 2,
        "phase16_continuous_alert_rate_per_hr": round(2 / tot_p16_hours, 4)
    },
    {
        "detector": "Detector Improvement V4",
        "holdout_positive_detected": 38,
        "holdout_positive_total": 48,
        "holdout_positive_recall_pct": 79.17,
        "pocket_detected": 16,
        "pocket_total": 20,
        "pocket_recall_pct": 80.0,
        "clean_detected": 14,
        "clean_total": 15,
        "clean_recall_pct": 93.33,
        "fireworks_false_positives": 0,
        "fireworks_total": 8,
        "fireworks_fpr_pct": 0.0,
        "glass_break_false_positives": 8,
        "glass_break_total": 8,
        "glass_break_fpr_pct": 100.0,
        "env_false_positives": 9,
        "env_total": 92,
        "env_fpr_pct": 9.78,
        "continuous_2hr_alerts": 21,
        "continuous_alert_rate_per_hr": 10.5,
        "p19_positive_detected": 18,
        "p19_positive_total": len(df_p19_eval),
        "p19_positive_recall_pct": round(18 / len(df_p19_eval) * 100.0, 2),
        "phase16_continuous_exposure_hours": round(tot_p16_hours, 2),
        "phase16_continuous_alerts": 8,
        "phase16_continuous_alert_rate_per_hr": round(8 / tot_p16_hours, 4)
    },
    {
        "detector": "Detector Improvement V5",
        "holdout_positive_detected": int(df_p12_eval[p12_pos_m]["v5_adaptive_detected"].sum()),
        "holdout_positive_total": p12_pos_tot,
        "holdout_positive_recall_pct": round(df_p12_eval[p12_pos_m]["v5_adaptive_detected"].sum() / p12_pos_tot * 100.0, 2),
        "pocket_detected": int(df_p12_eval[p12_pocket_m]["v5_adaptive_detected"].sum()),
        "pocket_total": p12_pkt_tot,
        "pocket_recall_pct": round(df_p12_eval[p12_pocket_m]["v5_adaptive_detected"].sum() / p12_pkt_tot * 100.0, 2),
        "clean_detected": int(df_p12_eval[p12_clean_m]["v5_adaptive_detected"].sum()),
        "clean_total": p12_cln_tot,
        "clean_recall_pct": round(df_p12_eval[p12_clean_m]["v5_adaptive_detected"].sum() / p12_cln_tot * 100.0, 2),
        "fireworks_false_positives": int(df_p12_eval[p12_fw_m]["v5_adaptive_detected"].sum()),
        "fireworks_total": p12_fw_tot,
        "fireworks_fpr_pct": round(df_p12_eval[p12_fw_m]["v5_adaptive_detected"].sum() / p12_fw_tot * 100.0, 2),
        "glass_break_false_positives": int(df_p12_eval[p12_glass_m]["v5_adaptive_detected"].sum()),
        "glass_break_total": p12_gls_tot,
        "glass_break_fpr_pct": round(df_p12_eval[p12_glass_m]["v5_adaptive_detected"].sum() / p12_gls_tot * 100.0, 2),
        "env_false_positives": int(df_p12_eval[p12_env_m]["v5_adaptive_detected"].sum()),
        "env_total": p12_env_tot,
        "env_fpr_pct": round(df_p12_eval[p12_env_m]["v5_adaptive_detected"].sum() / p12_env_tot * 100.0, 2),
        "continuous_2hr_alerts": p12_cont_v5_a,
        "continuous_alert_rate_per_hr": round(p12_cont_v5_a / 2.0, 4),
        "p19_positive_detected": int(df_p19_eval['v5_adaptive_detected'].sum()),
        "p19_positive_total": len(df_p19_eval),
        "p19_positive_recall_pct": round(df_p19_eval['v5_adaptive_detected'].sum() / len(df_p19_eval) * 100.0, 2),
        "phase16_continuous_exposure_hours": round(tot_p16_hours, 2),
        "phase16_continuous_alerts": int(tot_p16_v5_a),
        "phase16_continuous_alert_rate_per_hr": round(tot_p16_v5_a / tot_p16_hours, 4)
    },
    {
        "detector": "Detector Improvement V6",
        "holdout_positive_detected": int(df_p12_eval[p12_pos_m]["v6_discriminated_detected"].sum()),
        "holdout_positive_total": p12_pos_tot,
        "holdout_positive_recall_pct": round(df_p12_eval[p12_pos_m]["v6_discriminated_detected"].sum() / p12_pos_tot * 100.0, 2),
        "pocket_detected": int(df_p12_eval[p12_pocket_m]["v6_discriminated_detected"].sum()),
        "pocket_total": p12_pkt_tot,
        "pocket_recall_pct": round(df_p12_eval[p12_pocket_m]["v6_discriminated_detected"].sum() / p12_pkt_tot * 100.0, 2),
        "clean_detected": int(df_p12_eval[p12_clean_m]["v6_discriminated_detected"].sum()),
        "clean_total": p12_cln_tot,
        "clean_recall_pct": round(df_p12_eval[p12_clean_m]["v6_discriminated_detected"].sum() / p12_cln_tot * 100.0, 2),
        "fireworks_false_positives": int(df_p12_eval[p12_fw_m]["v6_discriminated_detected"].sum()),
        "fireworks_total": p12_fw_tot,
        "fireworks_fpr_pct": round(df_p12_eval[p12_fw_m]["v6_discriminated_detected"].sum() / p12_fw_tot * 100.0, 2),
        "glass_break_false_positives": int(df_p12_eval[p12_glass_m]["v6_discriminated_detected"].sum()),
        "glass_break_total": p12_gls_tot,
        "glass_break_fpr_pct": round(df_p12_eval[p12_glass_m]["v6_discriminated_detected"].sum() / p12_gls_tot * 100.0, 2),
        "env_false_positives": int(df_p12_eval[p12_env_m]["v6_discriminated_detected"].sum()),
        "env_total": p12_env_tot,
        "env_fpr_pct": round(df_p12_eval[p12_env_m]["v6_discriminated_detected"].sum() / p12_env_tot * 100.0, 2),
        "continuous_2hr_alerts": p12_cont_v6_a,
        "continuous_alert_rate_per_hr": round(p12_cont_v6_a / 2.0, 4),
        "p19_positive_detected": int(df_p19_eval['v6_discriminated_detected'].sum()),
        "p19_positive_total": len(df_p19_eval),
        "p19_positive_recall_pct": round(df_p19_eval['v6_discriminated_detected'].sum() / len(df_p19_eval) * 100.0, 2),
        "phase16_continuous_exposure_hours": round(tot_p16_hours, 2),
        "phase16_continuous_alerts": int(tot_p16_v6_a),
        "phase16_continuous_alert_rate_per_hr": round(tot_p16_v6_a / tot_p16_hours, 4)
    }
]

df_new_holdout = pd.DataFrame(new_holdout_summary)
df_new_holdout.to_csv(out_dir / "new_holdout_results.csv", index=False)
print("\n--- NEW HOLDOUT RESULTS SUMMARY ---")
print(df_new_holdout.to_string(index=False))

# ------------------------------------------------------------------------------
# SAVE ALL DELIVERABLE CSV ARTIFACTS
# ------------------------------------------------------------------------------
# 1. recording_condition_predictions.csv
df_cond_preds = pd.DataFrame(all_condition_predictions)
df_cond_preds.to_csv(out_dir / "recording_condition_predictions.csv", index=False)

# 2. mode_transition_log.csv
df_mode_log = pd.DataFrame(all_mode_logs)
df_mode_log.to_csv(out_dir / "mode_transition_log.csv", index=False)

# 3. recording_level_predictions.csv
all_rec_preds = pd.concat([df_dev_eval, df_p15_eval, df_p12_eval, df_p19_eval], ignore_index=True)
all_rec_preds.to_csv(out_dir / "recording_level_predictions.csv", index=False)

print("\n" + "="*70)
print(f"Latency V6 across {len(latencies_v6)} evaluations:")
print(f"  Mean: {np.mean(latencies_v6):.2f} ms | Median: {np.median(latencies_v6):.2f} ms | 95th: {np.percentile(latencies_v6, 95):.2f} ms")
print("All evaluation artifacts successfully written to experiments/detector_improvement_v6/")
print("="*70)
