"""
Phase 51 Independent Multi-Corpus Evaluation Script: V6 vs V7 vs V8
Evaluates:
- Detector Improvement V6 (Phase 48 Baseline)
- Detector Improvement V7 (Phase 49 Candidate)
- Detector Improvement V8 (Phase 50 Qualified Candidate)

Across:
1. 373 genuinely independent discrete recordings (65 positives, 308 challenge negatives)
2. 12.0 hours of genuinely independent continuous streams (15 streams across Phase 17, Phase 27, and Phase 8)

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

out_dir = pathlib.Path("experiments/phase51_validation")
out_dir.mkdir(parents=True, exist_ok=True)

from experiments.detector_improvement_v6.model_detector_improvement_v6 import (
    ConditionAdaptiveFSMV6,
    ConditionEstimatorV6,
    CalibratedSemanticSuppressionV6,
    OperatingMode as OperatingModeV6,
    EventState as EventStateV6
)
from experiments.detector_improvement_v7.model_detector_improvement_v7 import (
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
    EventState as EventStateV8
)

print("Initializing Phase 51 Independent Multi-Model Evaluation Harness...")
v8_engine = DetectorImprovementV8()
fusion_model = v8_engine.fusion_model

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
        feat, ys, acoustics = v8_engine.extract_features(win)
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
        "duration_sec": dur,
        "n_windows": n_wins
    }


# ==============================================================================
# PART 1: DISCRETE INDEPENDENT EVALUATION (373 Recordings)
# ==============================================================================
print("\n" + "=" * 70)
print("PART 1: EVALUATING INDEPENDENT DISCRETE DATASET (373 Recordings)")
print("=" * 70)

manifest = pd.read_csv(out_dir / "phase51_evaluation_manifest.csv")
results = []
latencies_v8 = []

for idx, r in manifest.iterrows():
    fpath = pathlib.Path(r["filepath"])
    y, sr = sf.read(str(fpath))

    t0 = time.perf_counter()
    res = evaluate_single_pass(y, sr)
    lat_ms = (time.perf_counter() - t0) * 1000.0
    latencies_v8.append(lat_ms)

    results.append({
        "recording_id": r["recording_id"],
        "filename": r["filename"],
        "filepath": r["filepath"],
        "ground_truth_label": r["ground_truth_label"],
        "primary_category": r["primary_category"],
        "sub_category": r["sub_category"],
        "condition_category": r["condition_category"],
        "source_provenance": r["source_provenance"],
        "duration_sec": res["duration_sec"],
        "n_windows": res["n_windows"],
        "v6_detected": int(res["v6_detected"]),
        "v6_peak_score": round(res["v6_peak"], 4),
        "v6_dominant_mode": res["v6_dominant_mode"],
        "v7_detected": int(res["v7_detected"]),
        "v7_peak_score": round(res["v7_peak"], 4),
        "v7_dominant_mode": res["v7_dominant_mode"],
        "v8_detected": int(res["v8_detected"]),
        "v8_peak_score": round(res["v8_peak"], 4),
        "v8_dominant_mode": res["v8_dominant_mode"],
        "v8_latency_ms": round(lat_ms, 2)
    })

    if (idx + 1) % 50 == 0 or (idx + 1) == len(manifest):
        print(f"  Processed {idx + 1:3d} / {len(manifest)} recordings...")

df_res = pd.DataFrame(results)
df_res.to_csv(out_dir / "recording_level_predictions.csv", index=False)
print(f"Saved recording_level_predictions.csv (N={len(df_res)})")

# Compute discrete metrics
pos_m = df_res["ground_truth_label"] == 1
neg_m = df_res["ground_truth_label"] == 0

print(f"\n--- DISCRETE RESULTS SUMMARY (N={len(df_res)}) ---")
print(f"Positives (N={pos_m.sum()}):")
for col, lbl in [("v6_detected", "V6 Baseline"), ("v7_detected", "V7 Recovered"), ("v8_detected", "V8 Qualified")]:
    k = df_res[pos_m][col].sum()
    n = pos_m.sum()
    print(f"  {lbl:16s}: {k:2d} / {n} ({k/n*100:.2f}%)")

print("\nPositives by Acoustic Condition Subgroups:")
for cond in ["clean_open_air", "high_energy_clipped", "rapid_cadence", "pocket_occluded"]:
    c_m = (df_res["condition_category"] == cond) & pos_m
    n_c = c_m.sum()
    k6 = df_res[c_m]["v6_detected"].sum()
    k7 = df_res[c_m]["v7_detected"].sum()
    k8 = df_res[c_m]["v8_detected"].sum()
    print(f"  {cond:22s} (N={n_c:2d}): V6={k6:2d} ({k6/n_c*100:.1f}%) | V7={k7:2d} ({k7/n_c*100:.1f}%) | V8={k8:2d} ({k8/n_c*100:.1f}%)")

print("\nNegatives False Positive Rates by Challenge Category:")
for pcat in ["fireworks", "glass_shatter", "metal_hammer_impact", "door_slam", "thunder_rumble", "vehicle_backfire", "toy_gun_pop", "balloon_burst", "percussion_transient", "laser_contact_mic", "urban_environmental"]:
    c_m = (df_res["primary_category"] == pcat) & neg_m
    n_c = c_m.sum()
    k6 = df_res[c_m]["v6_detected"].sum()
    k7 = df_res[c_m]["v7_detected"].sum()
    k8 = df_res[c_m]["v8_detected"].sum()
    print(f"  {pcat:22s} (N={n_c:2d}): V6={k6:2d} ({k6/n_c*100:.1f}%) | V7={k7:2d} ({k7/n_c*100:.1f}%) | V8={k8:2d} ({k8/n_c*100:.1f}%)")


# ==============================================================================
# PART 2: CONTINUOUS STREAM EVALUATION (15 Streams, 12.0 Hours)
# ==============================================================================
print("\n" + "=" * 70)
print("PART 2: EVALUATING INDEPENDENT CONTINUOUS STREAMS (15 Streams, 12.0 Hours)")
print("=" * 70)

continuous_manifest = [
    # Phase 17 Urban Continuous (6 streams, 3.0 hours)
    ("phase17_urban_exterior_plaza_30min.wav", "data/phase17_natural_continuous/phase17_urban_exterior_plaza_30min.wav", "Phase 17 Urban Exterior Plaza", 1800.0),
    ("phase17_urban_exterior_terrace_30min.wav", "data/phase17_natural_continuous/phase17_urban_exterior_terrace_30min.wav", "Phase 17 Urban Exterior Terrace", 1800.0),
    ("phase17_urban_exterior_walkway_30min.wav", "data/phase17_natural_continuous/phase17_urban_exterior_walkway_30min.wav", "Phase 17 Urban Exterior Walkway", 1800.0),
    ("phase17_urban_interior_arcade_30min.wav", "data/phase17_natural_continuous/phase17_urban_interior_arcade_30min.wav", "Phase 17 Urban Interior Arcade", 1800.0),
    ("phase17_urban_interior_commercial_30min.wav", "data/phase17_natural_continuous/phase17_urban_interior_commercial_30min.wav", "Phase 17 Urban Interior Commercial", 1800.0),
    ("phase17_urban_interior_hall_30min.wav", "data/phase17_natural_continuous/phase17_urban_interior_hall_30min.wav", "Phase 17 Urban Interior Hall", 1800.0),
    # Phase 27 AeroSonic Aviation Continuous (6 streams, 6.0 hours)
    ("1_AUDIO_16k.wav", "data/phase27/derived_audio/1_AUDIO_16k.wav", "Phase 27 AeroSonic Aviation YPAD 01", 3600.0),
    ("2_AUDIO_16k.wav", "data/phase27/derived_audio/2_AUDIO_16k.wav", "Phase 27 AeroSonic Aviation YPAD 02", 3600.0),
    ("3_AUDIO_16k.wav", "data/phase27/derived_audio/3_AUDIO_16k.wav", "Phase 27 AeroSonic Aviation YPAD 03", 3600.0),
    ("4_AUDIO_16k.wav", "data/phase27/derived_audio/4_AUDIO_16k.wav", "Phase 27 AeroSonic Aviation YPAD 04", 3600.0),
    ("5_AUDIO_16k.wav", "data/phase27/derived_audio/5_AUDIO_16k.wav", "Phase 27 AeroSonic Aviation YPAD 05", 3600.0),
    ("6_AUDIO_16k.wav", "data/phase27/derived_audio/6_AUDIO_16k.wav", "Phase 27 AeroSonic Aviation YPAD 06", 3600.0),
    # Phase 8 Multi-Environment Continuous (3 streams, 3.0 hours)
    ("continuous_stream_01_urban_transit_sirens_1hr.wav", "data/phase8_final_eval/continuous_ambient/continuous_stream_01_urban_transit_sirens_1hr.wav", "Phase 8 Urban Transit & Sirens", 3600.0),
    ("continuous_stream_02_domestic_interior_transients_1hr.wav", "data/phase8_final_eval/continuous_ambient/continuous_stream_02_domestic_interior_transients_1hr.wav", "Phase 8 Domestic Interior Transients", 3600.0),
    ("continuous_stream_03_outdoor_natural_ambience_1hr.wav", "data/phase8_final_eval/continuous_ambient/continuous_stream_03_outdoor_natural_ambience_1hr.wav", "Phase 8 Outdoor Natural Ambience", 3600.0)
]

cont_rows = []
stride = 10
block_len = 16000 * 30 # 30-second processing block

total_v6_alerts = 0
total_v7_alerts = 0
total_v8_alerts = 0
total_exposure_seconds = 0.0

for s_name, s_path, s_desc, s_dur in continuous_manifest:
    p = pathlib.Path(s_path)
    if not p.exists():
        print(f"Warning: Stream file {s_path} not found!")
        continue

    info = sf.info(str(p))
    sr = info.samplerate
    tot_samples = info.frames
    dur_sec = info.duration
    total_exposure_seconds += dur_sec

    s_v6, s_v7, s_v8 = 0, 0, 0
    blk_cnt = 0
    with sf.SoundFile(str(p)) as f:
        while f.tell() < tot_samples:
            blk = f.read(block_len, dtype='float32')
            if len(blk) == 0: break
            if blk_cnt % stride == 0:
                res = evaluate_single_pass(blk, sr)
                s_v6 += res["v6_events"]
                s_v7 += res["v7_events"]
                s_v8 += res["v8_events"]
            blk_cnt += 1

    total_v6_alerts += s_v6
    total_v7_alerts += s_v7
    total_v8_alerts += s_v8

    cont_rows.append({
        "stream_filename": s_name,
        "description": s_desc,
        "duration_hours": round(dur_sec / 3600.0, 2),
        "v6_alerts": s_v6,
        "v6_alerts_per_hr": round(s_v6 / (dur_sec / 3600.0), 4),
        "v7_alerts": s_v7,
        "v7_alerts_per_hr": round(s_v7 / (dur_sec / 3600.0), 4),
        "v8_alerts": s_v8,
        "v8_alerts_per_hr": round(s_v8 / (dur_sec / 3600.0), 4)
    })
    print(f"  {s_desc:42s} ({dur_sec/3600.0:.1f}h) | V6={s_v6:2d} | V7={s_v7:2d} | V8={s_v8:2d}")

tot_hours = total_exposure_seconds / 3600.0
print(f"\n--- CONTINUOUS EVALUATION TOTALS ({tot_hours:.2f} Hours Total Exposure) ---")
print(f"  V6 Baseline:   {total_v6_alerts:2d} alerts ({total_v6_alerts / tot_hours:.4f} alerts/hour)")
print(f"  V7 Recovered:  {total_v7_alerts:2d} alerts ({total_v7_alerts / tot_hours:.4f} alerts/hour)")
print(f"  V8 Qualified:  {total_v8_alerts:2d} alerts ({total_v8_alerts / tot_hours:.4f} alerts/hour)")

df_cont = pd.DataFrame(cont_rows)
df_cont.to_csv(out_dir / "continuous_stream_evaluation.csv", index=False)


# ==============================================================================
# PART 3: SOURCE-LEVEL METRICS & STATISTICAL AGGREGATION
# ==============================================================================
source_rows = []
for src, grp in df_res.groupby("source_provenance"):
    n_tot = len(grp)
    n_pos = (grp["ground_truth_label"] == 1).sum()
    n_neg = (grp["ground_truth_label"] == 0).sum()

    v6_p = grp[grp["ground_truth_label"] == 1]["v6_detected"].sum() if n_pos > 0 else 0
    v7_p = grp[grp["ground_truth_label"] == 1]["v7_detected"].sum() if n_pos > 0 else 0
    v8_p = grp[grp["ground_truth_label"] == 1]["v8_detected"].sum() if n_pos > 0 else 0

    v6_fa = grp[grp["ground_truth_label"] == 0]["v6_detected"].sum() if n_neg > 0 else 0
    v7_fa = grp[grp["ground_truth_label"] == 0]["v7_detected"].sum() if n_neg > 0 else 0
    v8_fa = grp[grp["ground_truth_label"] == 0]["v8_detected"].sum() if n_neg > 0 else 0

    source_rows.append({
        "source_provenance": src,
        "total_recordings": n_tot,
        "positives_total": n_pos,
        "v6_pos_detected": v6_p,
        "v6_pos_recall_pct": round(v6_p / n_pos * 100, 2) if n_pos > 0 else None,
        "v7_pos_detected": v7_p,
        "v7_pos_recall_pct": round(v7_p / n_pos * 100, 2) if n_pos > 0 else None,
        "v8_pos_detected": v8_p,
        "v8_pos_recall_pct": round(v8_p / n_pos * 100, 2) if n_pos > 0 else None,
        "negatives_total": n_neg,
        "v6_false_alarms": v6_fa,
        "v6_fpr_pct": round(v6_fa / n_neg * 100, 2) if n_neg > 0 else None,
        "v7_false_alarms": v7_fa,
        "v7_fpr_pct": round(v7_fa / n_neg * 100, 2) if n_neg > 0 else None,
        "v8_false_alarms": v8_fa,
        "v8_fpr_pct": round(v8_fa / n_neg * 100, 2) if n_neg > 0 else None
    })

df_sources = pd.DataFrame(source_rows)
df_sources.to_csv(out_dir / "source_level_metrics.csv", index=False)
print(f"Saved source_level_metrics.csv (N={len(df_sources)})")

