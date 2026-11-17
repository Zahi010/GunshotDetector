"""
Full Phase 45 Evaluation Script:
1. Evaluates Phase 14, Phase 36, V1, V2, and V3 on Development Partition (218 recordings).
   Outputs: experiments/detector_improvement_v3/development_results.csv
2. Evaluates Phase 14, Phase 36, V1, V2, and V3 on NEW Independent Holdout (Phase 15, 147 discrete + 2hr continuous).
   Outputs: experiments/detector_improvement_v3/new_holdout_results.csv
3. Generates recording-level predictions for all recordings.
   Outputs: experiments/detector_improvement_v3/recording_level_predictions.csv
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

# Ensure output directory exists
out_dir = pathlib.Path("experiments/detector_improvement_v3")
out_dir.mkdir(parents=True, exist_ok=True)

# Detectors
from model_phase14 import Phase14CandidateGunshotDetector
from experiments.phase36.model_phase36 import Phase36CandidateGunshotDetector
from experiments.detector_improvement_v1.model_detector_improvement_v1 import DetectorImprovementV1
from experiments.detector_improvement_v2.model_detector_improvement_v2 import DetectorImprovementV2
from experiments.detector_improvement_v3.model_detector_improvement_v3 import DetectorImprovementV3

print("Loading detectors...")
p14 = Phase14CandidateGunshotDetector(profile="balanced")
p36 = Phase36CandidateGunshotDetector(config_path="experiments/phase36/config_phase36.json")
v1 = DetectorImprovementV1(profile="balanced")
v2 = DetectorImprovementV2(profile="balanced")
v3 = DetectorImprovementV3(profile="balanced")
detectors = {
    "Phase 14 Baseline": p14,
    "Phase 36 Refractory": p36,
    "Detector Improvement V1": v1,
    "Detector Improvement V2": v2,
    "Detector Improvement V3": v3
}

# ------------------------------------------------------------------------------
# PART 1: EVALUATION ON DEVELOPMENT PARTITION (218 recordings)
# ------------------------------------------------------------------------------
print("\n==================================================================")
print("PART 1: EVALUATING DEVELOPMENT PARTITION (218 recordings)")
print("==================================================================")

parts = pd.read_csv("scratch/v2_partitions.csv")
inv = pd.read_csv("experiments/phase41/phase41_recording_inventory.csv")
merged = pd.merge(inv, parts[["recording_id", "v2_partition"]], on="recording_id")
dev_df = merged[merged["v2_partition"] == "development"].copy()

p38 = pathlib.Path("experiments/phase38/dataset")
p39 = pathlib.Path("experiments/phase39/dataset")
p40 = pathlib.Path("experiments/phase40/dataset")

p38_cache = pathlib.Path("experiments/phase38/feature_cache")
p39_cache = pathlib.Path("experiments/phase39/feature_cache")
p40_cache = pathlib.Path("experiments/phase40/feature_cache")

def get_cache(rid):
    for c in [p40_cache, p39_cache, p38_cache]:
        f = c / f"{rid}.npz"
        if f.exists(): return f
    return None

def find_audio_file(r):
    fn = r["filename"]
    for p in [p38 / "positive" / fn, p38 / "distractors" / fn, p38 / "continuous" / fn,
             p39 / "distractor" / fn, p39 / "continuous" / fn, p40 / "continuous" / fn]:
        if p.exists(): return p
    return None

dev_results_rows = []
dev_rec_predictions = []

for idx, r in dev_df.iterrows():
    rid = r["recording_id"]
    role = r["evaluation_role"]
    cat = r["sub_category"]
    dur = float(r["duration_seconds"])
    gt = 1 if role == "PROSPECTIVE_POSITIVE_EVALUATION" else 0
    
    # Load audio
    af = find_audio_file(r)
    y, sr = sf.read(str(af))
    if y.ndim > 1: y = np.mean(y, axis=1)
    if sr != 16000:
        y = librosa.resample(y, orig_sr=sr, target_sr=16000)
    y = y.astype(np.float32)
    
    # Load cache if available
    cf = get_cache(rid)
    embs = None; ys = None
    if cf is not None:
        npz = np.load(cf)
        embs = npz["embeddings"]
        ys = npz["yamnet_scores"]
        
    row_pred = {
        "recording_id": rid,
        "partition": "development",
        "sub_category": cat,
        "ground_truth": gt,
        "duration_sec": dur
    }
    
    # Evaluate with each detector
    for det_name, det in detectors.items():
        if det_name == "Detector Improvement V3" and embs is not None:
            res = det.evaluate_waveform(y, precomputed_embeddings=embs, precomputed_yamnet_scores=ys)
        else:
            res = det.evaluate_waveform(y)
            
        det_key = det_name.split()[0].lower() + ("3" if "V3" in det_name else ("2" if "V2" in det_name else ("1" if "V1" in det_name else ("36" if "36" in det_name else "14"))))
        events = res.get("events", [])
        ev_count = len(events)
        is_det = 1 if (res.get("detected", False) or ev_count > 0) else 0
        pk_sc = float(res.get("peak_score", res.get("overall_score", 0.0)))
        if pk_sc == 0.0 and ev_count > 0:
            pk_sc = float(max((e.get("peak_score", 0.0) for e in events), default=0.0))
            
        row_pred[f"{det_key}_detected"] = is_det
        row_pred[f"{det_key}_event_count"] = ev_count
        row_pred[f"{det_key}_peak_score"] = round(pk_sc, 4)
        
    dev_rec_predictions.append(row_pred)
    if (idx + 1) % 50 == 0:
        print(f"  Processed {idx + 1} / {len(dev_df)} dev recordings...")

print(f"Completed development partition evaluation ({len(dev_rec_predictions)} recordings).")
df_dev_pred = pd.DataFrame(dev_rec_predictions)

# Compute development partition summary metrics table
for det_name in detectors.keys():
    det_key = det_name.split()[0].lower() + ("3" if "V3" in det_name else ("2" if "V2" in det_name else ("1" if "V1" in det_name else ("36" if "36" in det_name else "14"))))
    
    pos_mask = df_dev_pred["ground_truth"] == 1
    fw_mask = df_dev_pred["sub_category"] == "DISTRACTOR_FIREWORKS"
    env_mask = (df_dev_pred["ground_truth"] == 0) & (~fw_mask) & (df_dev_pred["duration_sec"] < 300)
    cont_mask = df_dev_pred["duration_sec"] >= 300
    
    pos_det = df_dev_pred[pos_mask][f"{det_key}_detected"].sum()
    pos_tot = pos_mask.sum()
    
    fw_det = df_dev_pred[fw_mask][f"{det_key}_detected"].sum()
    fw_tot = fw_mask.sum()
    
    env_det = df_dev_pred[env_mask][f"{det_key}_detected"].sum()
    env_tot = env_mask.sum()
    
    cont_events = df_dev_pred[cont_mask][f"{det_key}_event_count"].sum()
    cont_hours = df_dev_pred[cont_mask]["duration_sec"].sum() / 3600.0
    cont_far = cont_events / cont_hours if cont_hours > 0 else 0.0
    
    dev_results_rows.append({
        "detector": det_name,
        "positive_detected": int(pos_det),
        "positive_total": int(pos_tot),
        "positive_recall_pct": round(pos_det / pos_tot * 100.0, 2),
        "fireworks_false_positives": int(fw_det),
        "fireworks_total": int(fw_tot),
        "fireworks_fpr_pct": round(fw_det / fw_tot * 100.0, 2),
        "env_false_positives": int(env_det),
        "env_total": int(env_tot),
        "env_fpr_pct": round(env_det / env_tot * 100.0, 2),
        "continuous_alerts": int(cont_events),
        "continuous_hours": round(cont_hours, 4),
        "continuous_alert_rate_per_hr": round(cont_far, 4)
    })

df_dev_summary = pd.DataFrame(dev_results_rows)
df_dev_summary.to_csv(out_dir / "development_results.csv", index=False)
print("\n--- DEVELOPMENT RESULTS SUMMARY ---")
print(df_dev_summary.to_string(index=False))

# ------------------------------------------------------------------------------
# PART 2: EVALUATION ON NEW INDEPENDENT EVALUATION SET (PHASE 15)
# ------------------------------------------------------------------------------
print("\n==================================================================")
print("PART 2: EVALUATING NEW INDEPENDENT EVALUATION SET (PHASE 15)")
print("==================================================================")

p15_manifest = pd.read_csv("reports/phase15_dataset_manifest.csv")
# Filter out ambiguous recordings (ground_truth_label == -1)
p15_eval_df = p15_manifest[p15_manifest["ground_truth_label"] != -1].copy()
print(f"Loaded {len(p15_eval_df)} discrete independent evaluation recordings (Pos: {(p15_eval_df['ground_truth_label']==1).sum()}, Neg: {(p15_eval_df['ground_truth_label']==0).sum()}).")

# Continuous 2hr stream
p15_cont_path = pathlib.Path("data/phase15_independent_eval/continuous/phase15_independent_continuous_2hr.wav")
print(f"Continuous stream path exists: {p15_cont_path.exists()} (size {p15_cont_path.stat().st_size / (1024*1024):.1f} MB)")

holdout_rec_predictions = []
for idx, r in p15_eval_df.iterrows():
    rid = r["recording_id"]
    cat = r["event_classification"]
    gt = int(r["ground_truth_label"])
    dur = float(r["duration_seconds"])
    fpath = pathlib.Path(r["filepath"])
    
    y, sr = sf.read(str(fpath))
    if y.ndim > 1: y = np.mean(y, axis=1)
    if sr != 16000:
        y = librosa.resample(y, orig_sr=sr, target_sr=16000)
    y = y.astype(np.float32)
    
    row_pred = {
        "recording_id": rid,
        "partition": "new_independent_holdout",
        "sub_category": cat,
        "ground_truth": gt,
        "duration_sec": dur
    }
    
    for det_name, det in detectors.items():
        res = det.evaluate_waveform(y)
        det_key = det_name.split()[0].lower() + ("3" if "V3" in det_name else ("2" if "V2" in det_name else ("1" if "V1" in det_name else ("36" if "36" in det_name else "14"))))
        events = res.get("events", [])
        ev_count = len(events)
        is_det = 1 if (res.get("detected", False) or ev_count > 0) else 0
        pk_sc = float(res.get("peak_score", res.get("overall_score", 0.0)))
        if pk_sc == 0.0 and ev_count > 0:
            pk_sc = float(max((e.get("peak_score", 0.0) for e in events), default=0.0))
            
        row_pred[f"{det_key}_detected"] = is_det
        row_pred[f"{det_key}_event_count"] = ev_count
        row_pred[f"{det_key}_peak_score"] = round(pk_sc, 4)
        
    holdout_rec_predictions.append(row_pred)
    if (idx + 1) % 30 == 0:
        print(f"  Processed {idx + 1} / {len(p15_eval_df)} independent holdout files...")

print(f"Completed discrete holdout evaluation ({len(holdout_rec_predictions)} recordings).")
df_holdout_pred = pd.DataFrame(holdout_rec_predictions)

# Evaluate continuous 2-hour recording in chunks for each detector
print("\nEvaluating continuous 2-hour recording on each detector...")
cont_results = {}
y_cont, sr_cont = sf.read(str(p15_cont_path))
if y_cont.ndim > 1: y_cont = np.mean(y_cont, axis=1)
if sr_cont != 16000:
    y_cont = librosa.resample(y_cont, orig_sr=sr_cont, target_sr=16000)
y_cont = y_cont.astype(np.float32)
cont_duration_hr = len(y_cont) / 16000.0 / 3600.0

for det_name, det in detectors.items():
    det_key = det_name.split()[0].lower() + ("3" if "V3" in det_name else ("2" if "V2" in det_name else ("1" if "V1" in det_name else ("36" if "36" in det_name else "14"))))
    print(f"  Streaming 2.0hr audio through {det_name}...")
    res = det.evaluate_waveform(y_cont)
    cont_results[det_key] = {
        "event_count": res["event_count"],
        "hours": cont_duration_hr,
        "rate": res["event_count"] / cont_duration_hr
    }
    print(f"    -> Events: {res['event_count']}, Rate: {res['event_count'] / cont_duration_hr:.2f} alerts/hr")

# Summary metrics table for new holdout
holdout_summary_rows = []
for det_name in detectors.keys():
    det_key = det_name.split()[0].lower() + ("3" if "V3" in det_name else ("2" if "V2" in det_name else ("1" if "V1" in det_name else ("36" if "36" in det_name else "14"))))
    
    pos_mask = df_holdout_pred["ground_truth"] == 1
    fw_mask = df_holdout_pred["sub_category"] == "esc50_fireworks"
    env_mask = (df_holdout_pred["ground_truth"] == 0) & (~fw_mask)
    
    pos_det = df_holdout_pred[pos_mask][f"{det_key}_detected"].sum()
    pos_tot = pos_mask.sum()
    
    fw_det = df_holdout_pred[fw_mask][f"{det_key}_detected"].sum()
    fw_tot = fw_mask.sum()
    
    env_det = df_holdout_pred[env_mask][f"{det_key}_detected"].sum()
    env_tot = env_mask.sum()
    
    cont_ev = cont_results[det_key]["event_count"]
    cont_hr = cont_results[det_key]["hours"]
    cont_far = cont_results[det_key]["rate"]
    
    holdout_summary_rows.append({
        "detector": det_name,
        "holdout_positive_detected": int(pos_det),
        "holdout_positive_total": int(pos_tot),
        "holdout_positive_recall_pct": round(pos_det / pos_tot * 100.0, 2),
        "holdout_fireworks_false_positives": int(fw_det),
        "holdout_fireworks_total": int(fw_tot),
        "holdout_fireworks_fpr_pct": round(fw_det / fw_tot * 100.0, 2),
        "holdout_env_false_positives": int(env_det),
        "holdout_env_total": int(env_tot),
        "holdout_env_fpr_pct": round(env_det / env_tot * 100.0, 2),
        "continuous_2hr_alerts": int(cont_ev),
        "continuous_hours": round(cont_hr, 4),
        "continuous_alert_rate_per_hr": round(cont_far, 4)
    })

df_holdout_summary = pd.DataFrame(holdout_summary_rows)
df_holdout_summary.to_csv(out_dir / "new_holdout_results.csv", index=False)
print("\n--- NEW INDEPENDENT HOLDOUT RESULTS SUMMARY ---")
print(df_holdout_summary.to_string(index=False))

# ------------------------------------------------------------------------------
# PART 3: RECORDING-LEVEL PREDICTIONS TABLE
# ------------------------------------------------------------------------------
print("\n==================================================================")
print("PART 3: COMBINED RECORDING-LEVEL PREDICTIONS TABLE")
print("==================================================================")
df_all_pred = pd.concat([df_dev_pred, df_holdout_pred], ignore_index=True)
df_all_pred.to_csv(out_dir / "recording_level_predictions.csv", index=False)
print(f"Saved {len(df_all_pred)} recording-level predictions to {out_dir / 'recording_level_predictions.csv'}!")
print("Full evaluation script finished successfully!")
