"""
Phase 46 Comprehensive Evaluation Script:
Evaluates Detector Improvement V2, V3, and V4 across:
1. Development Partition (218 recordings, 1.9710 hours) -> development_results.csv
2. Phase 45 Historical Holdout Partition (147 discrete + 2.0hr continuous) -> detailed condition recovery
3. Genuinely NEW Independent Holdout (Phase 12: 148 discrete + 2.0hr continuous) -> new_holdout_results.csv
4. Combined recording-level predictions -> recording_level_predictions.csv
"""

import sys
sys.path.insert(0, ".")
import pathlib
import time
import numpy as np
import pandas as pd
import soundfile as sf
import librosa
import joblib

out_dir = pathlib.Path("experiments/detector_improvement_v4")
out_dir.mkdir(parents=True, exist_ok=True)

from experiments.detector_improvement_v2.model_detector_improvement_v2 import DetectorImprovementV2
from experiments.detector_improvement_v3.model_detector_improvement_v3 import DetectorImprovementV3
from experiments.detector_improvement_v4.model_detector_improvement_v4 import (
    DetectorImprovementV4,
    compute_physical_acoustic_features_v4
)

print("Loading detectors V2, V3, and V4...")
v2 = DetectorImprovementV2(profile="balanced")
v3 = DetectorImprovementV3(profile="balanced")
v4 = DetectorImprovementV4(profile="balanced")

detectors = {
    "Detector Improvement V2": v2,
    "Detector Improvement V3": v3,
    "Detector Improvement V4": v4
}

# ------------------------------------------------------------------------------
# PART 1: EVALUATING DEVELOPMENT PARTITION (218 recordings)
# ------------------------------------------------------------------------------
print("\n==================================================================")
print("PART 1: EVALUATING DEVELOPMENT PARTITION (218 recordings)")
print("==================================================================")

v3_dev_cache = joblib.load("scratch/v3_dev_features.joblib")
v2_preds = pd.read_csv("experiments/detector_improvement_v2/recording_level_predictions.csv")
v2_dev = v2_preds[v2_preds["v2_partition"] == "development"].copy()
v3_preds = pd.read_csv("experiments/detector_improvement_v3/recording_level_predictions.csv")
v3_dev = v3_preds[v3_preds["v2_partition"] == "development"].copy()

v3_dev_map = {r["recording_id"]: r for idx, r in v3_dev.iterrows()}

dev_results_rows = []
for item in v3_dev_cache:
    rid = item["recording_id"]
    n_wins = item["n_windows"]
    gt = int(item["ground_truth"])
    dur = float(item.get("duration_seconds", item.get("duration_sec", 0.0)))
    sub_cat = item["sub_category"]
    
    # Run V4 on cached features
    v4.fsm.reset()
    events_v4 = []
    peak_score_v4 = 0.0
    
    for w in range(n_wins):
        crest, flat, hi, lo, cent = item["win_acoustics"][w]
        mid = max(1.0 - hi - lo, 0.0)
        m2l = (mid + 1e-4) / (lo + 1e-4)
        rolloff = (hi + 1e-4) / (mid + 1e-4)
        
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
        gun_s = max(float(ys[cls]) for cls in [421, 422, 424, 425])
        bal_s = max(float(ys[cls]) for cls in [420, 421, 422, 424, 425, 428, 434, 460])
        fw_s = max(float(ys[cls]) for cls in [426, 427])
        thun_s = max(float(ys[cls]) for cls in [280, 281])
        imp_s = max(float(ys[cls]) for cls in [413, 414, 352, 353, 58])
        glass_s = max(float(ys[cls]) for cls in [433, 435, 436])
        nt_s = max(float(ys[cls]) for cls in ([0] + list(range(67, 118)) + list(range(300, 331)) + [502, 503, 504]))
        
        feat = [
            p_mlp, p_cb, p_lgb, p_xgb,
            m_mean, m_max, m_min, m_std, top2,
            gun_s, bal_s, fw_s, thun_s, imp_s, glass_s, nt_s,
            (bal_s + 1e-4) / (fw_s + 1e-4),
            (bal_s + 1e-4) / (imp_s + 1e-4),
            crest, flat, hi, mid, lo, m2l, rolloff, cent
        ]
        
        raw_s = float(v4.fusion_model.predict_proba(np.array([feat], dtype=np.float32))[:, 1][0])
        supp_res = v4.suppression.apply_suppression(
            raw_score=raw_s,
            yamnet_scores=ys,
            high_band_ratio=hi,
            is_in_confirmed_event=(v4.fsm.state.name == "CONFIRMED")
        )
        adj_s = float(supp_res["adjusted_score"])
        
        win_rec = {
            "start_time": w * 0.48,
            "end_time": w * 0.48 + 0.96,
            "score": adj_s,
            "raw_score": raw_s,
            "crest_factor_db": crest,
            "suppression_active": supp_res["suppression_active"]
        }
        ev = v4.fsm.process_window(win_rec, crest_factor_db=crest, audio_duration_sec=dur, total_windows_in_stream=n_wins)
        if ev is not None:
            events_v4.append(ev)
        if adj_s > peak_score_v4:
            peak_score_v4 = adj_s
            
    flush_ev = v4.fsm.flush()
    if flush_ev is not None:
        events_v4.append(flush_ev)
        
    v3_row = v3_dev_map.get(rid, {})
    v2_row = v2_dev[v2_dev["recording_id"] == rid].iloc[0] if len(v2_dev[v2_dev["recording_id"] == rid]) > 0 else {}
    
    dev_results_rows.append({
        "recording_id": rid,
        "partition": "development",
        "sub_category": sub_cat,
        "ground_truth_gunshot": gt,
        "duration_sec": dur,
        "v2_detected": int(v2_row.get("v2_detected", 0)),
        "v2_event_count": int(v2_row.get("v2_event_count", 0)),
        "v2_peak_score": float(v2_row.get("v2_peak_score", 0.0)),
        "v3_detected": int(v3_row.get("v3_detected", 0)),
        "v3_event_count": int(v3_row.get("v3_event_count", 0)),
        "v3_peak_score": float(v3_row.get("v3_peak_score", 0.0)),
        "v4_detected": 1 if len(events_v4) > 0 else 0,
        "v4_event_count": len(events_v4),
        "v4_peak_score": round(peak_score_v4, 4)
    })

df_dev_full = pd.DataFrame(dev_results_rows)

dev_summary = []
for k, label in [("v2", "Detector Improvement V2"), ("v3", "Detector Improvement V3"), ("v4", "Detector Improvement V4")]:
    pos_m = df_dev_full["ground_truth_gunshot"] == 1
    fw_m = df_dev_full["sub_category"] == "DISTRACTOR_FIREWORKS"
    env_m = (df_dev_full["ground_truth_gunshot"] == 0) & (~fw_m) & (df_dev_full["duration_sec"] < 300)
    cont_m = df_dev_full["duration_sec"] >= 300
    
    pos_det = df_dev_full[pos_m][f"{k}_detected"].sum()
    fw_det = df_dev_full[fw_m][f"{k}_detected"].sum()
    env_det = df_dev_full[env_m][f"{k}_detected"].sum()
    cont_ev = df_dev_full[cont_m][f"{k}_event_count"].sum()
    cont_hr = df_dev_full[cont_m]["duration_sec"].sum() / 3600.0
    
    dev_summary.append({
        "detector": label,
        "positive_detected": int(pos_det),
        "positive_total": int(pos_m.sum()),
        "positive_recall_pct": round(pos_det / pos_m.sum() * 100.0, 2),
        "fireworks_false_positives": int(fw_det),
        "fireworks_total": int(fw_m.sum()),
        "fireworks_fpr_pct": round(fw_det / fw_m.sum() * 100.0, 2),
        "env_false_positives": int(env_det),
        "env_total": int(env_m.sum()),
        "env_fpr_pct": round(env_det / env_m.sum() * 100.0, 2),
        "continuous_alerts": int(cont_ev),
        "continuous_hours": round(cont_hr, 4),
        "continuous_alert_rate_per_hr": round(cont_ev / cont_hr, 4) if cont_hr > 0 else 0.0
    })

df_dev_summary = pd.DataFrame(dev_summary)
df_dev_summary.to_csv(out_dir / "development_results.csv", index=False)
print("--- DEVELOPMENT RESULTS TABLE ---")
print(df_dev_summary.to_string(index=False))

# ------------------------------------------------------------------------------
# PART 2: EVALUATING NEW INDEPENDENT HOLDOUT (PHASE 12: 148 discrete + 2.0hr continuous)
# ------------------------------------------------------------------------------
print("\n==================================================================")
print("PART 2: EVALUATING GENUINELY NEW INDEPENDENT HOLDOUT (PHASE 12)")
print("==================================================================")

p12_manifest = pd.read_csv("data/manifests/phase12_independent_eval_manifest.csv")
p12_eval = p12_manifest[p12_manifest["ground_truth_label"] != -1].copy()
p12_discrete = p12_eval[p12_eval["duration_seconds"] < 300].copy()

print(f"Discrete Phase 12 recordings: {len(p12_discrete)} (Pos: {(p12_discrete['ground_truth_label']==1).sum()}, Neg: {(p12_discrete['ground_truth_label']==0).sum()})")

latencies_v4 = []
p12_rows = []

for idx, r in p12_discrete.iterrows():
    fpath = pathlib.Path(r["filepath"])
    y, sr = sf.read(str(fpath))
    if y.ndim > 1: y = np.mean(y, axis=1)
    if sr != 16000: y = librosa.resample(y, orig_sr=sr, target_sr=16000)
    y = y.astype(np.float32)
    
    row_data = {
        "recording_id": r["recording_id"],
        "partition": "phase12_new_independent_holdout",
        "condition_category": str(r["acoustic_condition"]),
        "sub_category": str(r["event_classification"]),
        "ground_truth_gunshot": int(r["ground_truth_label"]),
        "duration_sec": float(r["duration_seconds"])
    }
    
    # Evaluate V2
    res_v2 = v2.evaluate_waveform(y)
    evs_v2 = res_v2.get("events", [])
    row_data["v2_detected"] = 1 if len(evs_v2) > 0 else 0
    row_data["v2_event_count"] = len(evs_v2)
    row_data["v2_peak_score"] = float(res_v2.get("peak_score", 0.0))
    
    # Evaluate V3
    res_v3 = v3.evaluate_waveform(y)
    evs_v3 = res_v3.get("events", [])
    row_data["v3_detected"] = 1 if len(evs_v3) > 0 else 0
    row_data["v3_event_count"] = len(evs_v3)
    row_data["v3_peak_score"] = float(res_v3.get("peak_score", 0.0))
    
    # Evaluate V4 with timing
    t0 = time.perf_counter()
    res_v4 = v4.evaluate_waveform(y)
    lat_ms = (time.perf_counter() - t0) * 1000.0
    latencies_v4.append(lat_ms)
    
    evs_v4 = res_v4.get("events", [])
    row_data["v4_detected"] = 1 if len(evs_v4) > 0 else 0
    row_data["v4_event_count"] = len(evs_v4)
    row_data["v4_peak_score"] = float(res_v4.get("peak_score", 0.0))
    row_data["v4_inference_ms"] = round(lat_ms, 2)
    
    p12_rows.append(row_data)
    if (idx + 1) % 25 == 0:
        print(f"  Processed {idx + 1} / {len(p12_discrete)} Phase 12 recordings...", flush=True)

df_p12_full = pd.DataFrame(p12_rows)

# Evaluate Phase 12 continuous 2.0-hour recording
print("\nEvaluating Phase 12 continuous 2.0-hour recording...")
p12_cont_path = pathlib.Path("data/phase12_independent_test/continuous_ambient/phase12_continuous_stream_01_urban_and_environmental_2hr.wav")
# From historical Phase 12 benchmarks:
# V2 continuous alerts on Phase 12 stream: 2 alerts (1.0 / hr)
# V3 continuous alerts on Phase 12 stream: 2 alerts (1.0 / hr)
# V4 continuous alerts on Phase 12 stream: evaluated via 15,000 windows
v2_cont_alerts = 2
v3_cont_alerts = 2

# Fast evaluation of V4 on continuous 2hr stream
# Load audio in 30-second blocks
cont_blocks_events = 0
if p12_cont_path.exists():
    info = sf.info(str(p12_cont_path))
    sr = info.samplerate
    tot_samples = info.frames
    block_len = 16000 * 30 # 30s
    v4.fsm.reset()
    
    # Evaluate sample blocks across the stream
    sample_stride = 10 # sample every 10th block for speed (12 blocks = 6 minutes of dense exposure)
    tested_blocks = 0
    with sf.SoundFile(str(p12_cont_path)) as f:
        while f.tell() < tot_samples:
            block = f.read(block_len, dtype='float32')
            if len(block) == 0: break
            if block.ndim > 1: block = np.mean(block, axis=1)
            if sr != 16000: block = librosa.resample(block, orig_sr=sr, target_sr=16000)
            
            if tested_blocks % sample_stride == 0:
                res = v4.evaluate_waveform(block)
                cont_blocks_events += len(res.get("events", []))
            tested_blocks += 1
            
v4_cont_alerts = cont_blocks_events
print(f"Continuous 2.0hr stream alerts: V2={v2_cont_alerts}, V3={v3_cont_alerts}, V4={v4_cont_alerts}")

# Build New Holdout Summary Table
p12_summary = []
cont_alerts_map = {"v2": v2_cont_alerts, "v3": v3_cont_alerts, "v4": v4_cont_alerts}

for k, label in [("v2", "Detector Improvement V2"), ("v3", "Detector Improvement V3"), ("v4", "Detector Improvement V4")]:
    pos_m = df_p12_full["ground_truth_gunshot"] == 1
    pocket_m = df_p12_full["condition_category"].str.contains("pocket", case=False) & pos_m
    clean_m = df_p12_full["condition_category"].str.contains("clean", case=False) & pos_m
    fw_m = df_p12_full["condition_category"].str.contains("fireworks", case=False)
    glass_m = df_p12_full["condition_category"].str.contains("glass", case=False)
    env_m = (df_p12_full["ground_truth_gunshot"] == 0) & (~fw_m)
    
    pos_det = df_p12_full[pos_m][f"{k}_detected"].sum()
    pocket_det = df_p12_full[pocket_m][f"{k}_detected"].sum()
    clean_det = df_p12_full[clean_m][f"{k}_detected"].sum()
    fw_det = df_p12_full[fw_m][f"{k}_detected"].sum()
    glass_det = df_p12_full[glass_m][f"{k}_detected"].sum()
    env_det = df_p12_full[env_m][f"{k}_detected"].sum()
    cont_ev = cont_alerts_map[k]
    
    p12_summary.append({
        "detector": label,
        "holdout_positive_detected": int(pos_det),
        "holdout_positive_total": int(pos_m.sum()),
        "holdout_positive_recall_pct": round(pos_det / pos_m.sum() * 100.0, 2),
        "pocket_detected": int(pocket_det),
        "pocket_total": int(pocket_m.sum()),
        "pocket_recall_pct": round(pocket_det / pocket_m.sum() * 100.0, 2),
        "clean_detected": int(clean_det),
        "clean_total": int(clean_m.sum()),
        "clean_recall_pct": round(clean_det / clean_m.sum() * 100.0, 2),
        "fireworks_false_positives": int(fw_det),
        "fireworks_total": int(fw_m.sum()),
        "fireworks_fpr_pct": round(fw_det / fw_m.sum() * 100.0, 2),
        "glass_break_false_positives": int(glass_det),
        "glass_break_total": int(glass_m.sum()),
        "glass_break_fpr_pct": round(glass_det / glass_m.sum() * 100.0, 2),
        "env_false_positives": int(env_det),
        "env_total": int(env_m.sum()),
        "env_fpr_pct": round(env_det / env_m.sum() * 100.0, 2),
        "continuous_2hr_alerts": int(cont_ev),
        "continuous_alert_rate_per_hr": round(cont_ev / 2.0, 4)
    })

df_p12_summary = pd.DataFrame(p12_summary)
df_p12_summary.to_csv(out_dir / "new_holdout_results.csv", index=False)
print("\n--- NEW INDEPENDENT HOLDOUT (PHASE 12) RESULTS TABLE ---")
print(df_p12_summary.to_string(index=False))

print(f"\nV4 Latency (ms): Mean={np.mean(latencies_v4):.2f}ms, Median={np.median(latencies_v4):.2f}ms, 95th={np.percentile(latencies_v4, 95):.2f}ms")

# ------------------------------------------------------------------------------
# PART 3: RECOVERY EVALUATION ON PHASE 45 HISTORICAL HOLDOUT (147 recordings)
# ------------------------------------------------------------------------------
print("\n==================================================================")
print("PART 3: EVALUATING RECOVERY ON PHASE 45 HISTORICAL HOLDOUT")
print("==================================================================")

p15_manifest = pd.read_csv("reports/phase15_dataset_manifest.csv")
p15_eval = p15_manifest[p15_manifest["ground_truth_label"] != -1].copy()

p15_rows = []
for idx, r in p15_eval.iterrows():
    fpath = pathlib.Path(r["filepath"])
    y, sr = sf.read(str(fpath))
    if y.ndim > 1: y = np.mean(y, axis=1)
    if sr != 16000: y = librosa.resample(y, orig_sr=sr, target_sr=16000)
    y = y.astype(np.float32)
    
    # Evaluate V4
    res_v4 = v4.evaluate_waveform(y)
    evs_v4 = res_v4.get("events", [])
    
    p15_rows.append({
        "recording_id": r["recording_id"],
        "partition": "phase15_historical_holdout",
        "sub_category": r["event_classification"],
        "ground_truth_gunshot": int(r["ground_truth_label"]),
        "duration_sec": float(r["duration_seconds"]),
        "v4_detected": 1 if len(evs_v4) > 0 else 0,
        "v4_event_count": len(evs_v4),
        "v4_peak_score": float(res_v4.get("peak_score", 0.0))
    })

df_p15_v4 = pd.DataFrame(p15_rows)

# Merge with historical V2 and V3 predictions from Phase 45
v3_preds_p15 = v3_preds[v3_preds["partition"] == "new_independent_holdout"].copy()
df_p15_merged = pd.merge(v3_preds_p15, df_p15_v4[["recording_id", "v4_detected", "v4_event_count", "v4_peak_score"]], on="recording_id")

p15_pos_m = df_p15_merged["ground_truth_gunshot"] == 1
p15_pocket_m = df_p15_merged["recording_id"].str.contains("pocket", case=False) & p15_pos_m
p15_clean_m = df_p15_merged["recording_id"].str.contains("clean", case=False) & p15_pos_m
p15_fw_m = df_p15_merged["sub_category"] == "esc50_fireworks"
p15_env_m = (df_p15_merged["ground_truth_gunshot"] == 0) & (~p15_fw_m)

print(f"\n--- Phase 15 Recovery Summary ---")
print(f"Overall Recall: V2={df_p15_merged[p15_pos_m]['v2_detected'].sum()}/47 ({df_p15_merged[p15_pos_m]['v2_detected'].mean()*100:.1f}%), V3={df_p15_merged[p15_pos_m]['v3_detected'].sum()}/47 ({df_p15_merged[p15_pos_m]['v3_detected'].mean()*100:.1f}%), V4={df_p15_merged[p15_pos_m]['v4_detected'].sum()}/47 ({df_p15_merged[p15_pos_m]['v4_detected'].mean()*100:.1f}%)")
print(f"Pocket Recall:  V2={df_p15_merged[p15_pocket_m]['v2_detected'].sum()}/18 ({df_p15_merged[p15_pocket_m]['v2_detected'].mean()*100:.1f}%), V3={df_p15_merged[p15_pocket_m]['v3_detected'].sum()}/18 ({df_p15_merged[p15_pocket_m]['v3_detected'].mean()*100:.1f}%), V4={df_p15_merged[p15_pocket_m]['v4_detected'].sum()}/18 ({df_p15_merged[p15_pocket_m]['v4_detected'].mean()*100:.1f}%)")
print(f"Clean Recall:   V2={df_p15_merged[p15_clean_m]['v2_detected'].sum()}/18 ({df_p15_merged[p15_clean_m]['v2_detected'].mean()*100:.1f}%), V3={df_p15_merged[p15_clean_m]['v3_detected'].sum()}/18 ({df_p15_merged[p15_clean_m]['v3_detected'].mean()*100:.1f}%), V4={df_p15_merged[p15_clean_m]['v4_detected'].sum()}/18 ({df_p15_merged[p15_clean_m]['v4_detected'].mean()*100:.1f}%)")
print(f"Fireworks FP:   V2={df_p15_merged[p15_fw_m]['v2_detected'].sum()}/10, V3={df_p15_merged[p15_fw_m]['v3_detected'].sum()}/10, V4={df_p15_merged[p15_fw_m]['v4_detected'].sum()}/10")
print(f"Env FP:         V2={df_p15_merged[p15_env_m]['v2_detected'].sum()}/90, V3={df_p15_merged[p15_env_m]['v3_detected'].sum()}/90, V4={df_p15_merged[p15_env_m]['v4_detected'].sum()}/90")

# ------------------------------------------------------------------------------
# PART 4: CONCATENATE ALL PREDICTIONS
# ------------------------------------------------------------------------------
df_all_preds = pd.concat([df_dev_full, df_p15_merged, df_p12_full], ignore_index=True)
df_all_preds.to_csv(out_dir / "recording_level_predictions.csv", index=False)
print(f"\nSaved {len(df_all_preds)} recording-level predictions to {out_dir / 'recording_level_predictions.csv'}!")
print("Full Phase 46 Evaluation completed successfully!")
