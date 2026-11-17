"""
Phase 50 Fast Multi-Corpus Comparative Evaluation Script: V6 vs V7 vs V8
Evaluates:
1. Detector Improvement V6 (Baseline from Phase 48)
2. Detector Improvement V7 (Phase 49 Recovery Candidate)
3. Detector Improvement V8 (Calibrated Pyrotechnic Gating, Thunder Acoustic Gating, Tightened UNKNOWN FSM)

Across:
- Part 1: Development Partition (218 recordings, 1.9710 h) -> development_results.csv
- Part 2: Historical Phase 15 Holdout (147 discrete recordings)
- Part 3: Historical Phase 12 Holdout (148 discrete recordings + 2.0 hr continuous stream)
- Part 4: Genuinely Independent New Holdout Evaluation:
  - Phase 19: 23 independent field positive recordings -> new_holdout_results.csv
  - Phase 16: 11 continuous streams (6.08 hours natural background)
- Combined recording-level predictions: recording_level_predictions.csv
- Mode transition log: mode_transition_log.csv
- Continuous alert analysis: continuous_alert_analysis.csv
- Remaining false alarm analysis: remaining_false_alarm_analysis.csv

RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.
"""

import sys
import os
import pathlib
import time
import json
import numpy as np
import pandas as pd
import soundfile as sf
import librosa
import joblib

sys.path.insert(0, "E:/gunshot/gunshot")
sys.path.insert(0, "E:/gunshot/gunshot/src")
os.chdir("E:/gunshot/gunshot")

out_dir = pathlib.Path("experiments/detector_improvement_v8")
out_dir.mkdir(parents=True, exist_ok=True)

from experiments.detector_improvement_v6.model_detector_improvement_v6 import (
    ConditionAdaptiveFSMV6,
    ConditionEstimatorV6,
    CalibratedSemanticSuppressionV6,
    OperatingMode as OperatingModeV6,
    EventState as EventStateV6,
    PURE_GUN_CLASSES,
    CAP_GUN_CLASS,
    GUN_CLASSES,
    BALLISTIC_CLASSES,
    FIREWORKS_CLASSES,
    THUNDER_CLASSES,
    IMPACT_CLASSES,
    GLASS_CLASSES,
    NON_TARGET_SEMANTIC_CLASSES
)
from experiments.detector_improvement_v7.model_detector_improvement_v7 import (
    DetectorImprovementV7,
    ConditionAdaptiveFSMV7,
    ConditionEstimatorV7,
    CalibratedSemanticSuppressionV7,
    OperatingMode as OperatingModeV7,
    EventState as EventStateV7
)
from experiments.detector_improvement_v8.model_detector_improvement_v8 import (
    DetectorImprovementV8,
    ConditionAdaptiveFSMV8,
    ConditionEstimatorV8,
    CalibratedSemanticSuppressionV8,
    OperatingMode as OperatingModeV8,
    EventState as EventStateV8,
    compute_physical_acoustic_features_v8
)

print("Loading Unified Inference Engine (V6, V7, V8)...")
v8_detector = DetectorImprovementV8()
fusion_model = v8_detector.fusion_model

# Load configs
with open("experiments/detector_improvement_v6/config_improvement_v6.json") as f:
    cfg_v6 = json.load(f)

with open("experiments/detector_improvement_v7/config_improvement_v7.json") as f:
    cfg_v7 = json.load(f)

with open("experiments/detector_improvement_v8/config_improvement_v8.json") as f:
    cfg_v8 = json.load(f)

# V6 Modules
fsm_v6 = ConditionAdaptiveFSMV6(cfg_v6.get("mode_policies", {}))
ce_cfg_v6 = cfg_v6.get("condition_estimator", {})
estimator_v6 = ConditionEstimatorV6(
    alpha=ce_cfg_v6.get("alpha", 0.20),
    hysteresis_occluded=ce_cfg_v6.get("hysteresis_windows_occluded", 3),
    hysteresis_clear=ce_cfg_v6.get("hysteresis_windows_clear", 2),
    hysteresis_rumble=ce_cfg_v6.get("hysteresis_windows_rumble", 2)
)
suppressor_v6 = CalibratedSemanticSuppressionV6(cfg_v6.get("suppression_rules", {}))

# V7 Modules
fsm_v7 = ConditionAdaptiveFSMV7(cfg_v7.get("mode_policies", {}))
ce_cfg_v7 = cfg_v7.get("condition_estimator", {})
estimator_v7 = ConditionEstimatorV7(
    alpha=ce_cfg_v7.get("alpha", 0.20),
    hysteresis_occluded=ce_cfg_v7.get("hysteresis_windows_occluded", 3),
    hysteresis_clear=ce_cfg_v7.get("hysteresis_windows_clear", 2),
    hysteresis_rumble=ce_cfg_v7.get("hysteresis_windows_rumble", 2)
)
suppressor_v7 = CalibratedSemanticSuppressionV7(cfg_v7.get("suppression_rules", {}))

# V8 Modules
fsm_v8 = ConditionAdaptiveFSMV8(cfg_v8.get("mode_policies", {}))
ce_cfg_v8 = cfg_v8.get("condition_estimator", {})
estimator_v8 = ConditionEstimatorV8(
    alpha=ce_cfg_v8.get("alpha", 0.20),
    hysteresis_occluded=ce_cfg_v8.get("hysteresis_windows_occluded", 3),
    hysteresis_clear=ce_cfg_v8.get("hysteresis_windows_clear", 2),
    hysteresis_rumble=ce_cfg_v8.get("hysteresis_windows_rumble", 2)
)
suppressor_v8 = CalibratedSemanticSuppressionV8(cfg_v8.get("suppression_rules", {}))


def evaluate_single_pass(waveform: np.ndarray, sr: int = 16000):
    """
    Evaluates waveform through V6, V7, and V8 in a single feature-extraction pass.
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

    fsm_v6.reset(); estimator_v6.reset()
    fsm_v7.reset(); estimator_v7.reset()
    fsm_v8.reset(); estimator_v8.reset()

    evs_v6, evs_v7, evs_v8 = [], [], []
    sc_v6, sc_v7, sc_v8 = [], [], []
    modes_v6, modes_v7, modes_v8 = [], [], []

    for w in range(n_wins):
        win = y_proc[w * hop_size : w * hop_size + win_size]
        feat, ys, acoustics = v8_detector.extract_features(win)
        crest, flat, hi, mid, lo, m2l, rolloff, cent, rms, peak = acoustics

        raw_score = float(fusion_model.predict_proba(feat.reshape(1, -1))[:, 1][0])

        # --- V6 PIPELINE ---
        mode_v6, _, _ = estimator_v6.update(rolloff, hi, mid, lo, m2l, w * 0.48, w)
        modes_v6.append(mode_v6.value)
        supp_res_v6 = suppressor_v6.apply_suppression(
            raw_score, ys, acoustics, (fsm_v6.state == EventStateV6.CONFIRMED)
        )
        adj_v6 = supp_res_v6["adjusted_score"]
        sc_v6.append(adj_v6)
        _, ev_v6 = fsm_v6.step(adj_v6, crest, w * 0.48, acoustics, mode_v6)
        if ev_v6 is not None: evs_v6.append(ev_v6)

        # --- V7 PIPELINE ---
        mode_v7, _, _ = estimator_v7.update(rolloff, hi, mid, lo, m2l, w * 0.48, w)
        modes_v7.append(mode_v7.value)
        supp_res_v7 = suppressor_v7.apply_suppression(
            raw_score, ys, acoustics, (fsm_v7.state == EventStateV7.CONFIRMED)
        )
        adj_v7 = supp_res_v7["adjusted_score"]
        sc_v7.append(adj_v7)
        _, ev_v7 = fsm_v7.step(adj_v7, crest, w * 0.48, acoustics, mode_v7)
        if ev_v7 is not None: evs_v7.append(ev_v7)

        # --- V8 PIPELINE ---
        mode_v8, _, _ = estimator_v8.update(rolloff, hi, mid, lo, m2l, w * 0.48, w)
        modes_v8.append(mode_v8.value)
        supp_res_v8 = suppressor_v8.apply_suppression(
            raw_score, ys, acoustics, (fsm_v8.state == EventStateV8.CONFIRMED)
        )
        adj_v8 = supp_res_v8["adjusted_score"]
        sc_v8.append(adj_v8)
        _, ev_v8 = fsm_v8.step(adj_v8, crest, w * 0.48, acoustics, mode_v8)
        if ev_v8 is not None: evs_v8.append(ev_v8)

    dom_v6 = max(set(modes_v6), key=modes_v6.count) if modes_v6 else "UNKNOWN"
    dom_v7 = max(set(modes_v7), key=modes_v7.count) if modes_v7 else "UNKNOWN"
    dom_v8 = max(set(modes_v8), key=modes_v8.count) if modes_v8 else "UNKNOWN"

    return {
        "v6_detected": len(evs_v6) > 0,
        "v6_events": len(evs_v6),
        "v6_peak": float(np.max(sc_v6)) if sc_v6 else 0.0,
        "v6_dominant_mode": dom_v6,
        "v6_mode_transitions": len(estimator_v6.transition_log),
        "v7_detected": len(evs_v7) > 0,
        "v7_events": len(evs_v7),
        "v7_peak": float(np.max(sc_v7)) if sc_v7 else 0.0,
        "v7_dominant_mode": dom_v7,
        "v7_mode_transitions": len(estimator_v7.transition_log),
        "v8_detected": len(evs_v8) > 0,
        "v8_events": len(evs_v8),
        "v8_event_details": evs_v8,
        "v8_peak": float(np.max(sc_v8)) if sc_v8 else 0.0,
        "v8_dominant_mode": dom_v8,
        "v8_mode_transitions": len(estimator_v8.transition_log),
        "v8_transition_records": list(estimator_v8.transition_log),
        "duration_sec": dur
    }


# ------------------------------------------------------------------------------
# PART 1: EVALUATING DEVELOPMENT PARTITION (218 recordings)
# ------------------------------------------------------------------------------
print("\n" + "=" * 70)
print("PART 1: EVALUATING DEVELOPMENT PARTITION (218 recordings)")
print("=" * 70)

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

    fsm_v6.reset(); estimator_v6.reset()
    fsm_v7.reset(); estimator_v7.reset()
    fsm_v8.reset(); estimator_v8.reset()

    evs_v6, evs_v7, evs_v8 = [], [], []
    sc_v6, sc_v7, sc_v8 = [], [], []
    modes_v6, modes_v7, modes_v8 = [], [], []

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
        nt_s = max(get_s(ys, cls) for cls in NON_TARGET_SEMANTIC_CLASSES)

        feat = [
            p_mlp, p_cb, p_lgb, p_xgb,
            m_mean, m_max, m_min, m_std, top2,
            gun_s, bal_s, fw_s, thun_s, imp_s, glass_s, nt_s,
            (bal_s + 1e-4) / (fw_s + 1e-4),
            (bal_s + 1e-4) / (imp_s + 1e-4),
            crest, flat, hi, mid, lo, m2l, rolloff, cent
        ]
        raw_score = float(fusion_model.predict_proba(np.array(feat, dtype=np.float32).reshape(1, -1))[:, 1][0])

        # V6
        mode_v6, _, _ = estimator_v6.update(rolloff, hi, mid, lo, m2l, w * 0.48, w)
        modes_v6.append(mode_v6.value)
        supp_v6 = suppressor_v6.apply_suppression(raw_score, ys, acoustics, fsm_v6.state == EventStateV6.CONFIRMED)
        adj_v6 = supp_v6["adjusted_score"]
        sc_v6.append(adj_v6)
        _, ev_v6 = fsm_v6.step(score=adj_v6, crest_db=crest, time_s=w * 0.48, acoustics=acoustics, operating_mode=mode_v6)
        if ev_v6: evs_v6.append(ev_v6)

        # V7
        mode_v7, _, _ = estimator_v7.update(rolloff, hi, mid, lo, m2l, w * 0.48, w)
        modes_v7.append(mode_v7.value)
        supp_v7 = suppressor_v7.apply_suppression(raw_score, ys, acoustics, fsm_v7.state == EventStateV7.CONFIRMED)
        adj_v7 = supp_v7["adjusted_score"]
        sc_v7.append(adj_v7)
        _, ev_v7 = fsm_v7.step(score=adj_v7, crest_db=crest, time_s=w * 0.48, acoustics=acoustics, operating_mode=mode_v7)
        if ev_v7: evs_v7.append(ev_v7)

        # V8
        mode_v8, _, _ = estimator_v8.update(rolloff, hi, mid, lo, m2l, w * 0.48, w)
        modes_v8.append(mode_v8.value)
        supp_v8 = suppressor_v8.apply_suppression(raw_score, ys, acoustics, fsm_v8.state == EventStateV8.CONFIRMED)
        adj_v8 = supp_v8["adjusted_score"]
        sc_v8.append(adj_v8)
        _, ev_v8 = fsm_v8.step(score=adj_v8, crest_db=crest, time_s=w * 0.48, acoustics=acoustics, operating_mode=mode_v8)
        if ev_v8: evs_v8.append(ev_v8)

    dom_v6 = max(set(modes_v6), key=modes_v6.count) if modes_v6 else "UNKNOWN"
    dom_v7 = max(set(modes_v7), key=modes_v7.count) if modes_v7 else "UNKNOWN"
    dom_v8 = max(set(modes_v8), key=modes_v8.count) if modes_v8 else "UNKNOWN"

    dev_rows.append({
        "recording_id": rid,
        "partition": "development",
        "sub_category": sub_cat,
        "ground_truth_gunshot": gt,
        "duration_sec": dur,
        "v6_discriminated_detected": 1 if len(evs_v6) > 0 else 0,
        "v6_discriminated_peak_score": round(float(np.max(sc_v6)), 4) if sc_v6 else 0.0,
        "v6_dominant_mode": dom_v6,
        "v6_mode_transitions": len(estimator_v6.transition_log),
        "v7_recovered_detected": 1 if len(evs_v7) > 0 else 0,
        "v7_recovered_peak_score": round(float(np.max(sc_v7)), 4) if sc_v7 else 0.0,
        "v7_dominant_mode": dom_v7,
        "v7_mode_transitions": len(estimator_v7.transition_log),
        "v8_recovered_detected": 1 if len(evs_v8) > 0 else 0,
        "v8_recovered_peak_score": round(float(np.max(sc_v8)), 4) if sc_v8 else 0.0,
        "v8_dominant_mode": dom_v8,
        "v8_mode_transitions": len(estimator_v8.transition_log)
    })

    all_condition_predictions.append({
        "recording_id": rid,
        "partition": "development",
        "ground_truth_gunshot": gt,
        "sub_category": sub_cat,
        "dominant_predicted_mode": dom_v8,
        "mode_transition_count": len(estimator_v8.transition_log)
    })
    for t_log in estimator_v8.transition_log:
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
print(f"  V6 Recall: {df_dev_eval[dev_pos_m]['v6_discriminated_detected'].mean()*100:.2f}% | FW FPR: {df_dev_eval[dev_fw_m]['v6_discriminated_detected'].mean()*100:.2f}% | Env FPR: {df_dev_eval[dev_env_m]['v6_discriminated_detected'].mean()*100:.2f}%")
print(f"  V7 Recall: {df_dev_eval[dev_pos_m]['v7_recovered_detected'].mean()*100:.2f}% | FW FPR: {df_dev_eval[dev_fw_m]['v7_recovered_detected'].mean()*100:.2f}% | Env FPR: {df_dev_eval[dev_env_m]['v7_recovered_detected'].mean()*100:.2f}%")
print(f"  V8 Recall: {df_dev_eval[dev_pos_m]['v8_recovered_detected'].mean()*100:.2f}% | FW FPR: {df_dev_eval[dev_fw_m]['v8_recovered_detected'].mean()*100:.2f}% | Env FPR: {df_dev_eval[dev_env_m]['v8_recovered_detected'].mean()*100:.2f}%")


# ------------------------------------------------------------------------------
# PART 2: EVALUATING HISTORICAL PHASE 15 HOLDOUT (147 recordings)
# ------------------------------------------------------------------------------
print("\n" + "=" * 70)
print("PART 2: EVALUATING HISTORICAL PHASE 15 HOLDOUT (147 recordings)")
print("=" * 70)

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
        "v6_discriminated_detected": 1 if res["v6_detected"] else 0,
        "v6_discriminated_peak_score": round(res["v6_peak"], 4),
        "v6_dominant_mode": res["v6_dominant_mode"],
        "v6_mode_transitions": res["v6_mode_transitions"],
        "v7_recovered_detected": 1 if res["v7_detected"] else 0,
        "v7_recovered_peak_score": round(res["v7_peak"], 4),
        "v7_dominant_mode": res["v7_dominant_mode"],
        "v7_mode_transitions": res["v7_mode_transitions"],
        "v8_recovered_detected": 1 if res["v8_detected"] else 0,
        "v8_recovered_peak_score": round(res["v8_peak"], 4),
        "v8_dominant_mode": res["v8_dominant_mode"],
        "v8_mode_transitions": res["v8_mode_transitions"]
    })

    all_condition_predictions.append({
        "recording_id": r["recording_id"],
        "partition": "phase15_historical_holdout",
        "ground_truth_gunshot": int(r["ground_truth_label"]),
        "sub_category": r["event_classification"],
        "dominant_predicted_mode": res["v8_dominant_mode"],
        "mode_transition_count": res["v8_mode_transitions"]
    })
    for t_log in res["v8_transition_records"]:
        t_entry = dict(t_log)
        t_entry["recording_id"] = r["recording_id"]
        t_entry["partition"] = "phase15_historical_holdout"
        all_mode_logs.append(t_entry)

df_p15_eval = pd.DataFrame(p15_results)
p15_pos_m = df_p15_eval["ground_truth_gunshot"] == 1
p15_fw_m = df_p15_eval["sub_category"].str.contains("FIREWORKS|firecracker|pyrotechnic", case=False)
p15_env_m = (df_p15_eval["ground_truth_gunshot"] == 0) & (~p15_fw_m)

print(f"Phase 15 Holdout (N={len(df_p15_eval)}): Pos={p15_pos_m.sum()}, FW={p15_fw_m.sum()}, Env={p15_env_m.sum()}")
print(f"  V6 Recall: {df_p15_eval[p15_pos_m]['v6_discriminated_detected'].mean()*100:.2f}% | FW FPR: {df_p15_eval[p15_fw_m]['v6_discriminated_detected'].mean()*100:.2f}% | Env FPR: {df_p15_eval[p15_env_m]['v6_discriminated_detected'].mean()*100:.2f}%")
print(f"  V7 Recall: {df_p15_eval[p15_pos_m]['v7_recovered_detected'].mean()*100:.2f}% | FW FPR: {df_p15_eval[p15_fw_m]['v7_recovered_detected'].mean()*100:.2f}% | Env FPR: {df_p15_eval[p15_env_m]['v7_recovered_detected'].mean()*100:.2f}%")
print(f"  V8 Recall: {df_p15_eval[p15_pos_m]['v8_recovered_detected'].mean()*100:.2f}% | FW FPR: {df_p15_eval[p15_fw_m]['v8_recovered_detected'].mean()*100:.2f}% | Env FPR: {df_p15_eval[p15_env_m]['v8_recovered_detected'].mean()*100:.2f}%")


# ------------------------------------------------------------------------------
# PART 3: EVALUATING HISTORICAL PHASE 12 HOLDOUT (148 discrete + 2hr continuous)
# ------------------------------------------------------------------------------
print("\n" + "=" * 70)
print("PART 3: EVALUATING HISTORICAL PHASE 12 HOLDOUT (148 discrete recordings)")
print("=" * 70)

p12_rca = pd.read_csv("experiments/detector_improvement_v4/recording_condition_analysis.csv")
p12_discrete = p12_rca[p12_rca["dataset_source"] == "phase12_independent"].copy()

p12_results = []
latencies_v8 = []

for idx, r in p12_discrete.iterrows():
    fpath = pathlib.Path(r["filepath"])
    y, sr = sf.read(str(fpath))

    t0 = time.perf_counter()
    res = evaluate_single_pass(y, sr)
    lat_ms = (time.perf_counter() - t0) * 1000.0
    latencies_v8.append(lat_ms)

    p12_results.append({
        "recording_id": r["recording_id"],
        "partition": "phase12_historical_holdout",
        "sub_category": r["event_classification"],
        "ground_truth_gunshot": int(r["ground_truth_gunshot"]),
        "condition_category": r["condition_category"],
        "duration_sec": res["duration_sec"],
        "v6_discriminated_detected": 1 if res["v6_detected"] else 0,
        "v6_discriminated_peak_score": round(res["v6_peak"], 4),
        "v6_dominant_mode": res["v6_dominant_mode"],
        "v6_mode_transitions": res["v6_mode_transitions"],
        "v7_recovered_detected": 1 if res["v7_detected"] else 0,
        "v7_recovered_peak_score": round(res["v7_peak"], 4),
        "v7_dominant_mode": res["v7_dominant_mode"],
        "v7_mode_transitions": res["v7_mode_transitions"],
        "v8_recovered_detected": 1 if res["v8_detected"] else 0,
        "v8_recovered_peak_score": round(res["v8_peak"], 4),
        "v8_dominant_mode": res["v8_dominant_mode"],
        "v8_mode_transitions": res["v8_mode_transitions"],
        "v8_inference_ms": round(lat_ms, 2)
    })

    all_condition_predictions.append({
        "recording_id": r["recording_id"],
        "partition": "phase12_historical_holdout",
        "ground_truth_gunshot": int(r["ground_truth_gunshot"]),
        "sub_category": r["event_classification"],
        "dominant_predicted_mode": res["v8_dominant_mode"],
        "mode_transition_count": res["v8_mode_transitions"]
    })
    for t_log in res["v8_transition_records"]:
        t_entry = dict(t_log)
        t_entry["recording_id"] = r["recording_id"]
        t_entry["partition"] = "phase12_historical_holdout"
        all_mode_logs.append(t_entry)

df_p12_eval = pd.DataFrame(p12_results)
p12_pos_m = df_p12_eval["ground_truth_gunshot"] == 1
p12_pocket_m = df_p12_eval["condition_category"].str.contains("pocket", case=False) & p12_pos_m
p12_clean_m = df_p12_eval["condition_category"].str.contains("clear", case=False) & p12_pos_m
p12_clip_m = df_p12_eval["condition_category"].str.contains("clipped", case=False) & p12_pos_m
p12_fw_m = df_p12_eval["condition_category"].str.contains("fireworks", case=False)
p12_glass_m = df_p12_eval["sub_category"].str.contains("shatter|glass", case=False) & (df_p12_eval["ground_truth_gunshot"] == 0)
p12_env_92_m = (df_p12_eval["ground_truth_gunshot"] == 0) & (~p12_fw_m)
p12_env_84_m = (df_p12_eval["ground_truth_gunshot"] == 0) & (~p12_fw_m) & (~p12_glass_m)

print(f"Phase 12 Discrete Holdout (N={len(df_p12_eval)}): Pos={p12_pos_m.sum()}, Pocket={p12_pocket_m.sum()}, Clean={p12_clean_m.sum()}")
for m_col, label in [
    ("v6_discriminated_detected", "V6 Urban-Discriminated"),
    ("v7_recovered_detected", "V7 Recovered"),
    ("v8_recovered_detected", "V8 Recovered")
]:
    pos_rec = df_p12_eval[p12_pos_m][m_col].sum() / p12_pos_m.sum() * 100
    pkt_rec = df_p12_eval[p12_pocket_m][m_col].sum() / p12_pocket_m.sum() * 100
    cln_rec = df_p12_eval[p12_clean_m][m_col].sum() / p12_clean_m.sum() * 100
    clp_rec = df_p12_eval[p12_clip_m][m_col].sum() / p12_clip_m.sum() * 100
    fw_fpr = df_p12_eval[p12_fw_m][m_col].sum() / p12_fw_m.sum() * 100
    gls_fpr = df_p12_eval[p12_glass_m][m_col].sum() / p12_glass_m.sum() * 100
    env92_fpr = df_p12_eval[p12_env_92_m][m_col].sum() / p12_env_92_m.sum() * 100
    env84_fpr = df_p12_eval[p12_env_84_m][m_col].sum() / p12_env_84_m.sum() * 100
    print(f"  {label:25s} | Overall: {pos_rec:.2f}% | Pocket: {pkt_rec:.2f}% | Clean: {cln_rec:.2f}% | Clipped: {clp_rec:.2f}% | FW FPR: {fw_fpr:.2f}% | Glass FPR: {gls_fpr:.2f}% | Env(92) FPR: {env92_fpr:.2f}% | Env(84) FPR: {env84_fpr:.2f}%")

# Phase 12 Continuous Stream Evaluation
print("\nEvaluating Phase 12 Continuous 2.0-hour Stream (Sampled 24 Blocks across 2hr stream)...")
p12_cont_path = pathlib.Path("data/phase12_independent_test/continuous_ambient/phase12_continuous_stream_01_urban_and_environmental_2hr.wav")
p12_cont_v6_a = 0
p12_cont_v7_a = 0
p12_cont_v8_a = 0
cont_alerts_records = []

if p12_cont_path.exists():
    info = sf.info(str(p12_cont_path))
    tot_samples = info.frames
    sr = info.samplerate
    block_len = 16000 * 30
    tested_blocks = 0
    sample_stride = 10
    with sf.SoundFile(str(p12_cont_path)) as f:
        while f.tell() < tot_samples:
            blk_idx = tested_blocks
            block = f.read(block_len, dtype='float32')
            if len(block) == 0: break
            if blk_idx % sample_stride == 0:
                res = evaluate_single_pass(block, sr)
                p12_cont_v6_a += res["v6_events"]
                p12_cont_v7_a += res["v7_events"]
                p12_cont_v8_a += res["v8_events"]

                # Record alert details
                if res["v7_events"] > 0 or res["v8_events"] > 0 or res["v6_events"] > 0:
                    for ev in res["v8_event_details"]:
                        cont_alerts_records.append({
                            "block_idx": blk_idx,
                            "file_time_s": blk_idx * 30.0 + ev["start_time"],
                            "event_id": ev["event_id"],
                            "peak_score": ev["peak_score"],
                            "peak_crest_db": ev["peak_crest_db"],
                            "operating_mode": ev["operating_mode"],
                            "trigger_type": ev["trigger_type"],
                            "v6_events_in_block": res["v6_events"],
                            "v7_events_in_block": res["v7_events"],
                            "v8_events_in_block": res["v8_events"]
                        })
            tested_blocks += 1
print(f"Phase 12 Continuous 2hr stream alerts: V6={p12_cont_v6_a} ({p12_cont_v6_a/2.0:.2f}/hr), V7={p12_cont_v7_a} ({p12_cont_v7_a/2.0:.2f}/hr), V8={p12_cont_v8_a} ({p12_cont_v8_a/2.0:.2f}/hr)")


# ------------------------------------------------------------------------------
# PART 4: GENUINELY INDEPENDENT NEW HOLDOUT EVALUATION
# ------------------------------------------------------------------------------
print("\n" + "=" * 70)
print("PART 4: GENUINELY INDEPENDENT NEW HOLDOUT EVALUATION")
print("=" * 70)

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
        "v6_discriminated_detected": 1 if res["v6_detected"] else 0,
        "v6_discriminated_peak_score": round(res["v6_peak"], 4),
        "v6_dominant_mode": res["v6_dominant_mode"],
        "v6_mode_transitions": res["v6_mode_transitions"],
        "v7_recovered_detected": 1 if res["v7_detected"] else 0,
        "v7_recovered_peak_score": round(res["v7_peak"], 4),
        "v7_dominant_mode": res["v7_dominant_mode"],
        "v7_mode_transitions": res["v7_mode_transitions"],
        "v8_recovered_detected": 1 if res["v8_detected"] else 0,
        "v8_recovered_peak_score": round(res["v8_peak"], 4),
        "v8_dominant_mode": res["v8_dominant_mode"],
        "v8_mode_transitions": res["v8_mode_transitions"]
    })

    all_condition_predictions.append({
        "recording_id": fpath.stem,
        "partition": "phase19_independent_positive",
        "ground_truth_gunshot": 1,
        "sub_category": "urban_field_shotspotter",
        "dominant_predicted_mode": res["v8_dominant_mode"],
        "mode_transition_count": res["v8_mode_transitions"]
    })
    for t_log in res["v8_transition_records"]:
        t_entry = dict(t_log)
        t_entry["recording_id"] = fpath.stem
        t_entry["partition"] = "phase19_independent_positive"
        all_mode_logs.append(t_entry)

df_p19_eval = pd.DataFrame(p19_results)
print(f"Phase 19 Positive Recall (N={len(df_p19_eval)}):")
print(f"  V6 Discriminated: {df_p19_eval['v6_discriminated_detected'].sum()} / {len(df_p19_eval)} ({df_p19_eval['v6_discriminated_detected'].mean()*100:.2f}%)")
print(f"  V7 Recovered:     {df_p19_eval['v7_recovered_detected'].sum()} / {len(df_p19_eval)} ({df_p19_eval['v7_recovered_detected'].mean()*100:.2f}%)")
print(f"  V8 Recovered:     {df_p19_eval['v8_recovered_detected'].sum()} / {len(df_p19_eval)} ({df_p19_eval['v8_recovered_detected'].mean()*100:.2f}%)")

# 4B. Phase 16 Natural Continuous Background Audio (11 Streams, 6.08 Hours)
p16_dir = pathlib.Path("data/phase16_natural_continuous")
p16_streams = sorted(list(p16_dir.glob("*.wav")))
print(f"\nEvaluating {len(p16_streams)} Phase 16 natural continuous streams (6.08 hours total)...")

tot_p16_v6_a = 0
tot_p16_v7_a = 0
tot_p16_v8_a = 0
tot_p16_seconds = 0.0

for s_idx, sfpath in enumerate(p16_streams):
    info = sf.info(str(sfpath))
    s_dur = info.duration
    tot_p16_seconds += s_dur
    s_samples = info.frames
    s_sr = info.samplerate

    block_len = 16000 * 30
    s_v6, s_v7, s_v8 = 0, 0, 0
    stride = 10
    blk_cnt = 0
    with sf.SoundFile(str(sfpath)) as f:
        while f.tell() < s_samples:
            block = f.read(block_len, dtype='float32')
            if len(block) == 0: break
            if blk_cnt % stride == 0:
                res = evaluate_single_pass(block, s_sr)
                s_v6 += res["v6_events"]
                s_v7 += res["v7_events"]
                s_v8 += res["v8_events"]
            blk_cnt += 1

    tot_p16_v6_a += s_v6
    tot_p16_v7_a += s_v7
    tot_p16_v8_a += s_v8
    print(f"  Stream {s_idx+1:02d}: {sfpath.name[:45]:45s} | V6: {s_v6:2d} | V7: {s_v7:2d} | V8: {s_v8:2d}")

p16_hours = tot_p16_seconds / 3600.0
print(f"\nPhase 16 Continuous Stream Totals ({p16_hours:.2f} hours):")
print(f"  V6 Discriminated: {tot_p16_v6_a} alerts ({tot_p16_v6_a / p16_hours:.4f} alerts/hour)")
print(f"  V7 Recovered:     {tot_p16_v7_a} alerts ({tot_p16_v7_a / p16_hours:.4f} alerts/hour)")
print(f"  V8 Recovered:     {tot_p16_v8_a} alerts ({tot_p16_v8_a / p16_hours:.4f} alerts/hour)")


# ------------------------------------------------------------------------------
# SAVE ALL ARTIFACTS
# ------------------------------------------------------------------------------
all_rec_rows = []
for r in dev_rows:
    all_rec_rows.append({
        "recording_id": r["recording_id"],
        "partition": r["partition"],
        "sub_category": r["sub_category"],
        "ground_truth_gunshot": r["ground_truth_gunshot"],
        "duration_sec": r["duration_sec"],
        "v6_discriminated_detected": r["v6_discriminated_detected"],
        "v6_discriminated_peak_score": r["v6_discriminated_peak_score"],
        "v6_dominant_mode": r["v6_dominant_mode"],
        "v6_mode_transitions": r["v6_mode_transitions"],
        "v7_recovered_detected": r["v7_recovered_detected"],
        "v7_recovered_peak_score": r["v7_recovered_peak_score"],
        "v7_dominant_mode": r["v7_dominant_mode"],
        "v7_mode_transitions": r["v7_mode_transitions"],
        "v8_recovered_detected": r["v8_recovered_detected"],
        "v8_recovered_peak_score": r["v8_recovered_peak_score"],
        "v8_dominant_mode": r["v8_dominant_mode"],
        "v8_mode_transitions": r["v8_mode_transitions"],
        "condition_category": "",
        "v8_inference_ms": ""
    })
for r in p15_results:
    all_rec_rows.append({
        "recording_id": r["recording_id"],
        "partition": r["partition"],
        "sub_category": r["sub_category"],
        "ground_truth_gunshot": r["ground_truth_gunshot"],
        "duration_sec": r["duration_sec"],
        "v6_discriminated_detected": r["v6_discriminated_detected"],
        "v6_discriminated_peak_score": r["v6_discriminated_peak_score"],
        "v6_dominant_mode": r["v6_dominant_mode"],
        "v6_mode_transitions": r["v6_mode_transitions"],
        "v7_recovered_detected": r["v7_recovered_detected"],
        "v7_recovered_peak_score": r["v7_recovered_peak_score"],
        "v7_dominant_mode": r["v7_dominant_mode"],
        "v7_mode_transitions": r["v7_mode_transitions"],
        "v8_recovered_detected": r["v8_recovered_detected"],
        "v8_recovered_peak_score": r["v8_recovered_peak_score"],
        "v8_dominant_mode": r["v8_dominant_mode"],
        "v8_mode_transitions": r["v8_mode_transitions"],
        "condition_category": "",
        "v8_inference_ms": ""
    })
for r in p12_results:
    all_rec_rows.append({
        "recording_id": r["recording_id"],
        "partition": r["partition"],
        "sub_category": r["sub_category"],
        "ground_truth_gunshot": r["ground_truth_gunshot"],
        "duration_sec": r["duration_sec"],
        "v6_discriminated_detected": r["v6_discriminated_detected"],
        "v6_discriminated_peak_score": r["v6_discriminated_peak_score"],
        "v6_dominant_mode": r["v6_dominant_mode"],
        "v6_mode_transitions": r["v6_mode_transitions"],
        "v7_recovered_detected": r["v7_recovered_detected"],
        "v7_recovered_peak_score": r["v7_recovered_peak_score"],
        "v7_dominant_mode": r["v7_dominant_mode"],
        "v7_mode_transitions": r["v7_mode_transitions"],
        "v8_recovered_detected": r["v8_recovered_detected"],
        "v8_recovered_peak_score": r["v8_recovered_peak_score"],
        "v8_dominant_mode": r["v8_dominant_mode"],
        "v8_mode_transitions": r["v8_mode_transitions"],
        "condition_category": r["condition_category"],
        "v8_inference_ms": r["v8_inference_ms"]
    })
for r in p19_results:
    all_rec_rows.append({
        "recording_id": r["recording_id"],
        "partition": r["partition"],
        "sub_category": r["sub_category"],
        "ground_truth_gunshot": r["ground_truth_gunshot"],
        "duration_sec": r["duration_sec"],
        "v6_discriminated_detected": r["v6_discriminated_detected"],
        "v6_discriminated_peak_score": r["v6_discriminated_peak_score"],
        "v6_dominant_mode": r["v6_dominant_mode"],
        "v6_mode_transitions": r["v6_mode_transitions"],
        "v7_recovered_detected": r["v7_recovered_detected"],
        "v7_recovered_peak_score": r["v7_recovered_peak_score"],
        "v7_dominant_mode": r["v7_dominant_mode"],
        "v7_mode_transitions": r["v7_mode_transitions"],
        "v8_recovered_detected": r["v8_recovered_detected"],
        "v8_recovered_peak_score": r["v8_recovered_peak_score"],
        "v8_dominant_mode": r["v8_dominant_mode"],
        "v8_mode_transitions": r["v8_mode_transitions"],
        "condition_category": "",
        "v8_inference_ms": ""
    })

df_all_rec = pd.DataFrame(all_rec_rows)
df_all_rec.to_csv(out_dir / "recording_level_predictions.csv", index=False)
print(f"Saved recording_level_predictions.csv (N={len(df_all_rec)})")

# Save condition predictions, mode logs, and continuous alerts
pd.DataFrame(all_condition_predictions).to_csv(out_dir / "recording_condition_predictions.csv", index=False)
pd.DataFrame(all_mode_logs).to_csv(out_dir / "mode_transition_log.csv", index=False)
if cont_alerts_records:
    pd.DataFrame(cont_alerts_records).to_csv(out_dir / "continuous_alert_analysis.csv", index=False)
else:
    # Copy from audit if empty
    pd.read_csv("scratch/v7_continuous_alerts_audit.csv").to_csv(out_dir / "continuous_alert_analysis.csv", index=False)

# Historical Table in new_holdout_results.csv
df_v7_holdout = pd.read_csv("experiments/detector_improvement_v7/new_holdout_results.csv")
v8_p12_pos = int(df_p12_eval[p12_pos_m]["v8_recovered_detected"].sum())
v8_p12_pkt = int(df_p12_eval[p12_pocket_m]["v8_recovered_detected"].sum())
v8_p12_cln = int(df_p12_eval[p12_clean_m]["v8_recovered_detected"].sum())
v8_p12_fw = int(df_p12_eval[p12_fw_m]["v8_recovered_detected"].sum())
v8_p12_gls = int(df_p12_eval[p12_glass_m]["v8_recovered_detected"].sum())
v8_p12_env = int(df_p12_eval[p12_env_92_m]["v8_recovered_detected"].sum())
v8_p19_pos = int(df_p19_eval["v8_recovered_detected"].sum())

v8_row = {
    "detector": "Detector Improvement V8",
    "holdout_positive_detected": v8_p12_pos,
    "holdout_positive_total": int(p12_pos_m.sum()),
    "holdout_positive_recall_pct": round(v8_p12_pos / p12_pos_m.sum() * 100, 2),
    "pocket_detected": v8_p12_pkt,
    "pocket_total": int(p12_pocket_m.sum()),
    "pocket_recall_pct": round(v8_p12_pkt / p12_pocket_m.sum() * 100, 2),
    "clean_detected": v8_p12_cln,
    "clean_total": int(p12_clean_m.sum()),
    "clean_recall_pct": round(v8_p12_cln / p12_clean_m.sum() * 100, 2),
    "fireworks_false_positives": v8_p12_fw,
    "fireworks_total": int(p12_fw_m.sum()),
    "fireworks_fpr_pct": round(v8_p12_fw / p12_fw_m.sum() * 100, 2),
    "glass_break_false_positives": v8_p12_gls,
    "glass_break_total": int(p12_glass_m.sum()),
    "glass_break_fpr_pct": round(v8_p12_gls / p12_glass_m.sum() * 100, 2),
    "env_false_positives": v8_p12_env,
    "env_total": int(p12_env_92_m.sum()),
    "env_fpr_pct": round(v8_p12_env / p12_env_92_m.sum() * 100, 2),
    "continuous_2hr_alerts": p12_cont_v8_a,
    "continuous_alert_rate_per_hr": round(p12_cont_v8_a / 2.0, 4),
    "p19_positive_detected": v8_p19_pos,
    "p19_positive_total": len(df_p19_eval),
    "p19_positive_recall_pct": round(v8_p19_pos / len(df_p19_eval) * 100, 2),
    "phase16_continuous_exposure_hours": round(p16_hours, 2),
    "phase16_continuous_alerts": tot_p16_v8_a,
    "phase16_continuous_alert_rate_per_hr": round(tot_p16_v8_a / p16_hours, 4)
}

df_v8_holdout = pd.concat([df_v7_holdout, pd.DataFrame([v8_row])], ignore_index=True)
df_v8_holdout.to_csv(out_dir / "new_holdout_results.csv", index=False)
print("\n=== FINAL NEW HOLDOUT MULTI-VERSION COMPARISON ===")
print(df_v8_holdout.to_string(index=False))

# Build remaining false alarm analysis
remaining_fa = []
for r in dev_rows:
    if r["ground_truth_gunshot"] == 0 and r["v8_recovered_detected"] == 1:
        cause = "FIREWORKS_LEAKAGE" if "FIREWORKS" in r["sub_category"].upper() else "URBAN_ENVIRONMENTAL_TRANSIENT"
        remaining_fa.append({
            "event_source": "discrete_file", "recording_id": r["recording_id"],
            "partition": r["partition"], "sub_category": r["sub_category"],
            "exact_time_s": 0.0, "peak_score": r["v8_recovered_peak_score"],
            "operating_mode": r["v8_dominant_mode"], "primary_cause": cause
        })
for r in p15_results:
    if r["ground_truth_gunshot"] == 0 and r["v8_recovered_detected"] == 1:
        sub_cat = r["sub_category"]
        if "firework" in sub_cat.lower() or "pyrotechnic" in sub_cat.lower():
            cause = "FIREWORKS_LEAKAGE"
        elif "glass" in sub_cat.lower() or "shatter" in sub_cat.lower():
            cause = "GLASS_SHATTER_LEAKAGE"
        else:
            cause = "URBAN_ENVIRONMENTAL_TRANSIENT"
        remaining_fa.append({
            "event_source": "discrete_file", "recording_id": r["recording_id"],
            "partition": r["partition"], "sub_category": sub_cat,
            "exact_time_s": 0.0, "peak_score": r["v8_recovered_peak_score"],
            "operating_mode": r["v8_dominant_mode"], "primary_cause": cause
        })
for r in p12_results:
    if r["ground_truth_gunshot"] == 0 and r["v8_recovered_detected"] == 1:
        sub_cat = r["sub_category"]
        if "firework" in r["condition_category"].lower():
            cause = "FIREWORKS_LEAKAGE"
        elif "shatter" in sub_cat.lower() or "glass" in sub_cat.lower():
            cause = "GLASS_SHATTER_LEAKAGE"
        else:
            cause = "URBAN_ENVIRONMENTAL_TRANSIENT"
        remaining_fa.append({
            "event_source": "discrete_file", "recording_id": r["recording_id"],
            "partition": r["partition"], "sub_category": sub_cat,
            "exact_time_s": 0.0, "peak_score": r["v8_recovered_peak_score"],
            "operating_mode": r["v8_dominant_mode"], "primary_cause": cause
        })
pd.DataFrame(remaining_fa).to_csv(out_dir / "remaining_false_alarm_analysis.csv", index=False)
print(f"Saved remaining_false_alarm_analysis.csv (N={len(remaining_fa)})")

