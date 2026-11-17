import sys
import os
import soundfile as sf
import librosa
import numpy as np
import pandas as pd
from pathlib import Path

sys.path.insert(0, "e:/gunshot/gunshot")
from experiments.detector_improvement_v10.model_detector_improvement_v10 import (
    DetectorImprovementV10,
    EventState
)

print("=" * 70, flush=True)
print("PHASE 55: GAIN NORMALIZATION EXPERIMENTAL AUDIT", flush=True)
print("=" * 70, flush=True)

pred_csv = "e:/gunshot/gunshot/experiments/phase54_final_validation/recording_level_predictions.csv"
df = pd.read_csv(pred_csv)

fn_df = df[(df["ground_truth_label"] == 1) & (df["prediction"] == 0)].copy()
tn_df = df[(df["ground_truth_label"] == 0) & (df["prediction"] == 0)].copy()

print(f"Loaded {len(fn_df)} False Negatives (Positives missed in Phase 54)", flush=True)
print(f"Loaded {len(tn_df)} True Negatives (Negatives correctly rejected in Phase 54)", flush=True)

det = DetectorImprovementV10()

def run_detector_on_audio(audio_signal, det_instance):
    det_instance.reset()
    res = det_instance.evaluate_waveform(audio_signal)
    detected = bool(res["detected"])
    max_score = float(res["peak_score"])
    conf_cnt = int(res["event_count"])
    return detected, max_score, 0.0, conf_cnt

def normalize_peak(audio, target_peak=0.95):
    peak = np.max(np.abs(audio))
    if peak < 1e-6:
        return audio.copy()
    gain = target_peak / peak
    return audio * gain

def normalize_rms(audio, target_rms_db=-20.0, max_peak=0.95):
    rms = np.sqrt(np.mean(audio**2) + 1e-12)
    current_rms_db = 20 * np.log10(max(rms, 1e-6))
    gain_db = target_rms_db - current_rms_db
    gain = 10 ** (gain_db / 20)
    norm = audio * gain
    peak = np.max(np.abs(norm))
    if peak > max_peak:
        norm = norm * (max_peak / peak)
    return norm

# Methods to test:
# 1: Baseline (Unnormalized)
# 2: Peak Norm -0.5 dB (target_peak=0.95)
# 3: Peak Norm -3.0 dB (target_peak=0.707)
# 4: RMS Norm -20 dBFS (with peak limit 0.95)
# 5: Moderate AGC / Boost (+6 dB uniform boost with peak clip guard at 0.95)

def boost_6db(audio, max_peak=0.95):
    gain = 10 ** (6.0 / 20.0) # ~2.0x
    boosted = audio * gain
    peak = np.max(np.abs(boosted))
    if peak > max_peak:
        boosted = boosted * (max_peak / peak)
    return boosted

methods = {
    "baseline": lambda x: x,
    "peak_norm_0.95": lambda x: normalize_peak(x, target_peak=0.95),
    "peak_norm_0.70": lambda x: normalize_peak(x, target_peak=0.707),
    "rms_norm_neg20db": lambda x: normalize_rms(x, target_rms_db=-20.0, max_peak=0.95),
    "boost_6db": lambda x: boost_6db(x, max_peak=0.95)
}

print("\n--- STEP 1: EVALUATING RECOVERY ON 39 FALSE NEGATIVES ---", flush=True)
fn_results = {m: {"recovered": 0, "scores": [], "crests": []} for m in methods}
fn_details = []

for idx, row in fn_df.iterrows():
    fpath = row["filepath"]
    audio, sr = sf.read(fpath, dtype="float32")
    if audio.ndim > 1:
        audio = np.mean(audio, axis=1)
    if sr != 16000:
        audio = librosa.resample(audio, orig_sr=sr, target_sr=16000)
    audio = audio.astype(np.float32)
    
    file_record = {"fname": row["fname"], "sub_category": row.get("sub_category", "unknown")}
    
    for m_name, m_func in methods.items():
        proc_audio = m_func(audio)
        trig, score, crest, conf_cnt = run_detector_on_audio(proc_audio, det)
        if trig:
            fn_results[m_name]["recovered"] += 1
        fn_results[m_name]["scores"].append(score)
        fn_results[m_name]["crests"].append(crest)
        file_record[f"{m_name}_trig"] = trig
        file_record[f"{m_name}_score"] = round(score, 4)
        file_record[f"{m_name}_crest"] = round(crest, 2)
        
    fn_details.append(file_record)

print("FN Recovery Results across methods (out of 39):", flush=True)
for m_name in methods:
    rec = fn_results[m_name]["recovered"]
    pct = (rec / len(fn_df)) * 100
    mean_sc = np.mean(fn_results[m_name]["scores"])
    print(f"  {m_name:20s}: Recovered {rec:2d}/39 ({pct:5.2f}%) | Mean Score: {mean_sc:.4f}", flush=True)

print("\n--- STEP 2: EVALUATING FALSE ALARM INFLATION ON 169 TRUE NEGATIVES ---", flush=True)
tn_results = {m: {"inflated_fp": 0, "scores": [], "by_cat": {}} for m in methods}
tn_details = []

for idx, row in tn_df.iterrows():
    fpath = row["filepath"]
    audio, sr = sf.read(fpath, dtype="float32")
    if audio.ndim > 1:
        audio = np.mean(audio, axis=1)
    if sr != 16000:
        audio = librosa.resample(audio, orig_sr=sr, target_sr=16000)
    audio = audio.astype(np.float32)
    
    cat = row.get("sub_category", "unknown")
    file_record = {"fname": row["fname"], "sub_category": cat}
    
    for m_name, m_func in methods.items():
        proc_audio = m_func(audio)
        trig, score, crest, conf_cnt = run_detector_on_audio(proc_audio, det)
        if trig:
            tn_results[m_name]["inflated_fp"] += 1
            tn_results[m_name]["by_cat"][cat] = tn_results[m_name]["by_cat"].get(cat, 0) + 1
        tn_results[m_name]["scores"].append(score)
        file_record[f"{m_name}_trig"] = trig
        file_record[f"{m_name}_score"] = round(score, 4)
        
    tn_details.append(file_record)

print("TN False Alarm Inflation Results across methods (out of 169):", flush=True)
for m_name in methods:
    inf = tn_results[m_name]["inflated_fp"]
    pct = (inf / len(tn_df)) * 100
    mean_sc = np.mean(tn_results[m_name]["scores"])
    by_cat_str = ", ".join([f"{k}: {v}" for k, v in tn_results[m_name]["by_cat"].items()]) or "None"
    print(f"  {m_name:20s}: False Alarms {inf:2d}/169 ({pct:5.2f}%) | Mean Score: {mean_sc:.4f} | Inflated: {by_cat_str}", flush=True)

# Save details for reporting
out_dir = Path("e:/gunshot/gunshot/experiments/phase55_failure_analysis")
pd.DataFrame(fn_details).to_csv(out_dir / "gain_norm_fn_recovery_details.csv", index=False)
pd.DataFrame(tn_details).to_csv(out_dir / "gain_norm_tn_inflation_details.csv", index=False)

# Summary dataframe
summary_rows = []
for m_name in methods:
    rec = fn_results[m_name]["recovered"]
    inf = tn_results[m_name]["inflated_fp"]
    summary_rows.append({
        "method": m_name,
        "fn_recovered": rec,
        "fn_recovery_pct": round((rec / 39) * 100, 2),
        "post_gain_total_recall": round(((95 + rec) / 134) * 100, 2),
        "tn_false_alarms": inf,
        "tn_false_alarm_pct": round((inf / 169) * 100, 2),
        "post_gain_total_fp": 48 + inf,
        "post_gain_total_fpr": round(((48 + inf) / 217) * 100, 2),
        "net_gain_benefit": rec - inf
    })

sum_df = pd.DataFrame(summary_rows)
sum_df.to_csv(out_dir / "gain_normalization_summary.csv", index=False)
print("\nGain Normalization Summary Table:")
print(sum_df.to_string(index=False), flush=True)
print("\nDone!", flush=True)
