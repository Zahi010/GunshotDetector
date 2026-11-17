import sys
sys.path.insert(0, ".")
import pathlib
import numpy as np
import pandas as pd
import soundfile as sf
import librosa
import tensorflow as tf

from experiments.detector_improvement_v3.model_detector_improvement_v3 import (
    DetectorImprovementV3,
    extract_fast_acoustics
)

v3 = DetectorImprovementV3(profile="balanced")

def compute_extended_acoustics(y_win: np.ndarray, sr: int = 16000):
    """
    Computes 8 acoustic features:
    1. crest_factor_db
    2. spectral_flatness
    3. high_band_ratio (>= 2500 Hz)
    4. mid_band_ratio (500 Hz - 2500 Hz)
    5. low_band_ratio (< 500 Hz)
    6. mid_to_low_ratio ((mid + 1e-4) / (low + 1e-4))
    7. channel_rolloff_ratio ((high + 1e-4) / (mid + 1e-4))
    8. spectral_centroid_hz
    """
    if len(y_win) == 0:
        return 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0
    pk = float(np.max(np.abs(y_win)))
    rms = float(np.sqrt(np.mean(y_win**2) + 1e-12))
    crest_db = float(20.0 * np.log10(max(pk / (rms + 1e-12), 1.0)))
    
    P = np.abs(np.fft.rfft(y_win))**2
    freqs = np.fft.rfftfreq(len(y_win), d=1.0 / float(sr))
    
    log_p = np.log(P + 1e-12)
    flatness = float(np.exp(np.mean(log_p)) / (np.mean(P) + 1e-12))
    
    tot_e = float(np.sum(P) + 1e-12)
    low_e = float(np.sum(P[freqs < 500.0]))
    mid_e = float(np.sum(P[(freqs >= 500.0) & (freqs < 2500.0)]))
    high_e = float(np.sum(P[freqs >= 2500.0]))
    
    low_ratio = low_e / tot_e
    mid_ratio = mid_e / tot_e
    high_ratio = high_e / tot_e
    
    mid_to_low = (mid_ratio + 1e-4) / (low_ratio + 1e-4)
    rolloff = (high_ratio + 1e-4) / (mid_ratio + 1e-4)
    centroid = float(np.sum(freqs * P) / tot_e)
    
    return crest_db, flatness, high_ratio, mid_ratio, low_ratio, mid_to_low, rolloff, centroid

all_records = []

# 1. Process Phase 15 Holdout
p15_manifest = pd.read_csv("reports/phase15_dataset_manifest.csv")
p15_eval = p15_manifest[p15_manifest["ground_truth_label"] != -1].copy()

for idx, r in p15_eval.iterrows():
    fpath = pathlib.Path(r["filepath"])
    y, sr = sf.read(str(fpath))
    if y.ndim > 1: y = np.mean(y, axis=1)
    if sr != 16000: y = librosa.resample(y, orig_sr=sr, target_sr=16000)
    y = y.astype(np.float32)
    
    y_win = y[:15360] if len(y) >= 15360 else np.pad(y, (0, 15360 - len(y)))
    crest, flat, hi, mid, lo, m2l, rolloff, cent = compute_extended_acoustics(y_win)
    
    # YAMNet & ensemble
    wave_tensor = tf.convert_to_tensor(y_win, dtype=tf.float32)
    yamnet_out = v3.yamnet_model(wave_tensor)
    scores_t, embs_t = yamnet_out[0], yamnet_out[1]
    emb = embs_t.numpy()
    ys = scores_t.numpy()[0]
    
    p_mlp = float(v3.mlp.predict(emb, verbose=0).flatten()[0])
    p_cb = float(v3.cb.predict_proba(emb)[:, 1][0])
    p_lgb = float(v3.lgb.predict_proba(emb)[:, 1][0])
    p_xgb = float(v3.xgb.predict_proba(emb)[:, 1][0])
    ens_mean = (p_mlp + p_cb + p_lgb + p_xgb) / 4.0
    
    gt = int(r["ground_truth_label"])
    fp_str = str(fpath).lower()
    cat = r["event_classification"]
    
    if gt == 1:
        if "pocket" in fp_str: cond = "pocket_or_fabric_obstructed"
        elif "clean" in fp_str: cond = "clear_open_microphone"
        elif "clipped" in fp_str: cond = "clipped_dynamic_overload"
        elif "urban" in fp_str: cond = "distant_or_attenuated"
        else: cond = "unknown_recording_condition"
    else:
        if "fireworks" in cat: cond = "fireworks_pyrotechnic"
        elif "thunder" in cat: cond = "weather_thunder"
        elif "engine" in cat: cond = "noisy_background_vehicle"
        elif "glass" in cat or "clapping" in cat: cond = "indoor_transient"
        else: cond = "outdoor_ambient_mimic"
        
    all_records.append({
        "dataset_source": "phase15_holdout",
        "recording_id": r["recording_id"],
        "filepath": r["filepath"],
        "ground_truth_gunshot": gt,
        "event_classification": cat,
        "condition_category": cond,
        "duration_seconds": round(float(r["duration_seconds"]), 3),
        "ensemble_mean": round(ens_mean, 4),
        "crest_factor_db": round(crest, 2),
        "spectral_flatness": round(flat, 4),
        "high_band_ratio_ge_2500hz": round(hi, 4),
        "mid_band_ratio_500_2500hz": round(mid, 4),
        "low_band_ratio_lt_500hz": round(lo, 4),
        "mid_to_low_energy_ratio": round(m2l, 4),
        "channel_rolloff_ratio": round(rolloff, 4),
        "spectral_centroid_hz": round(cent, 1)
    })

# 2. Process Phase 12 Independent Test
p12_manifest = pd.read_csv("data/manifests/phase12_independent_eval_manifest.csv")
p12_eval = p12_manifest[p12_manifest["ground_truth_label"] != -1].copy()
# Filter to discrete files (skip continuous 2hr in discrete table)
p12_discrete = p12_eval[p12_eval["duration_seconds"] < 300].copy()

for idx, r in p12_discrete.iterrows():
    fpath = pathlib.Path(r["filepath"])
    if not fpath.exists(): continue
    y, sr = sf.read(str(fpath))
    if y.ndim > 1: y = np.mean(y, axis=1)
    if sr != 16000: y = librosa.resample(y, orig_sr=sr, target_sr=16000)
    y = y.astype(np.float32)
    
    y_win = y[:15360] if len(y) >= 15360 else np.pad(y, (0, 15360 - len(y)))
    crest, flat, hi, mid, lo, m2l, rolloff, cent = compute_extended_acoustics(y_win)
    
    wave_tensor = tf.convert_to_tensor(y_win, dtype=tf.float32)
    yamnet_out = v3.yamnet_model(wave_tensor)
    scores_t, embs_t = yamnet_out[0], yamnet_out[1]
    emb = embs_t.numpy()
    ys = scores_t.numpy()[0]
    
    p_mlp = float(v3.mlp.predict(emb, verbose=0).flatten()[0])
    p_cb = float(v3.cb.predict_proba(emb)[:, 1][0])
    p_lgb = float(v3.lgb.predict_proba(emb)[:, 1][0])
    p_xgb = float(v3.xgb.predict_proba(emb)[:, 1][0])
    ens_mean = (p_mlp + p_cb + p_lgb + p_xgb) / 4.0
    
    gt = int(r["ground_truth_label"])
    ac_cond = str(r["acoustic_condition"]).lower()
    cat = r["event_classification"]
    
    if gt == 1:
        if "pocket" in ac_cond: cond = "pocket_or_fabric_obstructed"
        elif "clean" in ac_cond: cond = "clear_open_microphone"
        elif "clipped" in ac_cond: cond = "clipped_dynamic_overload"
        elif "distant" in ac_cond or "urban" in ac_cond: cond = "distant_or_attenuated"
        else: cond = "unknown_recording_condition"
    else:
        if "fireworks" in ac_cond or "pyrotechnic" in cat: cond = "fireworks_pyrotechnic"
        elif "thunder" in ac_cond: cond = "weather_thunder"
        elif "engine" in ac_cond or "train" in ac_cond or "chainsaw" in ac_cond or "car_horn" in ac_cond: cond = "noisy_background_vehicle"
        elif "glass" in ac_cond or "knock" in ac_cond: cond = "indoor_transient"
        else: cond = "outdoor_ambient_mimic"
        
    all_records.append({
        "dataset_source": "phase12_independent",
        "recording_id": r["recording_id"],
        "filepath": r["filepath"],
        "ground_truth_gunshot": gt,
        "event_classification": cat,
        "condition_category": cond,
        "duration_seconds": round(float(r["duration_seconds"]), 3),
        "ensemble_mean": round(ens_mean, 4),
        "crest_factor_db": round(crest, 2),
        "spectral_flatness": round(flat, 4),
        "high_band_ratio_ge_2500hz": round(hi, 4),
        "mid_band_ratio_500_2500hz": round(mid, 4),
        "low_band_ratio_lt_500hz": round(lo, 4),
        "mid_to_low_energy_ratio": round(m2l, 4),
        "channel_rolloff_ratio": round(rolloff, 4),
        "spectral_centroid_hz": round(cent, 1)
    })

df_all = pd.DataFrame(all_records)
out_csv = pathlib.Path("experiments/detector_improvement_v4/recording_condition_analysis.csv")
df_all.to_csv(out_csv, index=False)
print("Saved condition analysis of", len(df_all), "recordings to", out_csv)

print("\n--- Summary Statistics by Condition Category across Datasets ---")
cols = ["ensemble_mean", "crest_factor_db", "spectral_flatness", "high_band_ratio_ge_2500hz", "mid_band_ratio_500_2500hz", "low_band_ratio_lt_500hz", "mid_to_low_energy_ratio", "channel_rolloff_ratio", "spectral_centroid_hz"]
summary_df = df_all.groupby(["condition_category", "ground_truth_gunshot"])[cols].agg(["count", "mean", "std"])
print(df_all.groupby("condition_category")[cols].mean().to_string())

