import sys
sys.path.insert(0, ".")
import pathlib
import numpy as np
import pandas as pd
import soundfile as sf
import librosa
import tensorflow as tf
import joblib

from experiments.detector_improvement_v3.model_detector_improvement_v3 import (
    DetectorImprovementV3,
    extract_fast_acoustics
)

v3 = DetectorImprovementV3(profile="balanced")
p15_manifest = pd.read_csv("reports/phase15_dataset_manifest.csv")
p15_eval = p15_manifest[p15_manifest["ground_truth_label"] != -1].copy()

rows = []
for idx, r in p15_eval.iterrows():
    fpath = pathlib.Path(r["filepath"])
    y, sr = sf.read(str(fpath))
    if y.ndim > 1: y = np.mean(y, axis=1)
    if sr != 16000: y = librosa.resample(y, orig_sr=sr, target_sr=16000)
    y = y.astype(np.float32)
    
    # 0.96s window (15360 samples)
    if len(y) < 15360:
        y_pad = np.pad(y, (0, 15360 - len(y)))
    else:
        y_pad = y[:15360]
        
    crest_db, flatness, high_ratio, low_ratio, centroid = extract_fast_acoustics(y_pad)
    
    wave_tensor = tf.convert_to_tensor(y_pad, dtype=tf.float32)
    yamnet_out = v3.yamnet_model(wave_tensor)
    scores_t, embs_t = yamnet_out[0], yamnet_out[1]
    emb = embs_t.numpy()
    ys = scores_t.numpy()[0]
    
    p_mlp = float(v3.mlp.predict(emb, verbose=0).flatten()[0])
    p_cb = float(v3.cb.predict_proba(emb)[:, 1][0])
    p_lgb = float(v3.lgb.predict_proba(emb)[:, 1][0])
    p_xgb = float(v3.xgb.predict_proba(emb)[:, 1][0])
    
    m_mean = (p_mlp + p_cb + p_lgb + p_xgb) / 4.0
    
    gun_s = max(float(ys[cls]) for cls in [421, 422, 424, 425])
    bal_s = max(float(ys[cls]) for cls in [420, 421, 422, 424, 425, 428, 434, 460])
    fw_s = max(float(ys[cls]) for cls in [426, 427])
    thun_s = max(float(ys[cls]) for cls in [280, 281])
    imp_s = max(float(ys[cls]) for cls in [413, 414, 352, 353, 58])
    nt_s = max(float(ys[cls]) for cls in ([0] + list(range(67, 118)) + list(range(300, 331)) + [502, 503, 504]))
    
    feat = [
        p_mlp, p_cb, p_lgb, p_xgb,
        m_mean, max(p_mlp, p_cb, p_lgb, p_xgb), min(p_mlp, p_cb, p_lgb, p_xgb),
        float(np.std([p_mlp, p_cb, p_lgb, p_xgb])),
        (sorted([p_mlp, p_cb, p_lgb, p_xgb], reverse=True)[0] + sorted([p_mlp, p_cb, p_lgb, p_xgb], reverse=True)[1]) / 2.0,
        gun_s, bal_s, fw_s, thun_s, imp_s, nt_s,
        (bal_s + 1e-4) / (fw_s + 1e-4),
        (bal_s + 1e-4) / (imp_s + 1e-4),
        crest_db, flatness, high_ratio, low_ratio, centroid
    ]
    raw_s = float(v3.fusion_model.predict_proba(np.array([feat], dtype=np.float32))[:, 1][0])
    
    # Recording condition categorization
    fp_str = str(fpath).lower()
    cat = r["event_classification"]
    gt = int(r["ground_truth_label"])
    
    if gt == 1:
        if "pocket" in fp_str:
            cond = "pocket_obstructed"
        elif "clean" in fp_str:
            cond = "clear_open_mic"
        elif "clipped" in fp_str:
            cond = "clipped_dynamic_overload"
        elif "urban" in fp_str or "shotspotter" in fp_str:
            cond = "urban_distant"
        else:
            cond = "unknown_condition"
    else:
        if "fireworks" in cat:
            cond = "fireworks_distractor"
        elif "thunder" in cat:
            cond = "thunder_distractor"
        elif "engine" in cat:
            cond = "engine_distractor"
        elif "clapping" in cat or "glass" in cat:
            cond = "indoor_transient_distractor"
        else:
            cond = "ambient_mimic_distractor"
            
    rows.append({
        "recording_id": r["recording_id"],
        "filepath": r["filepath"],
        "ground_truth_label": gt,
        "event_classification": cat,
        "condition": cond,
        "duration_seconds": float(r["duration_seconds"]),
        "p_mlp": round(p_mlp, 4),
        "p_cb": round(p_cb, 4),
        "p_lgb": round(p_lgb, 4),
        "p_xgb": round(p_xgb, 4),
        "ensemble_mean": round(m_mean, 4),
        "yamnet_gunshot": round(gun_s, 4),
        "yamnet_ballistic": round(bal_s, 4),
        "yamnet_fireworks": round(fw_s, 4),
        "crest_factor_db": round(crest_db, 2),
        "spectral_flatness": round(flatness, 4),
        "high_band_ratio": round(high_ratio, 4),
        "low_band_ratio": round(low_ratio, 4),
        "spectral_centroid_hz": round(centroid, 1),
        "v3_raw_fusion_score": round(raw_s, 4)
    })

df_analysis = pd.DataFrame(rows)
df_analysis.to_csv("scratch/phase45_holdout_condition_analysis.csv", index=False)
print("Saved analysis of", len(df_analysis), "recordings.")
print("\n--- Summary Means by Condition ---")
cols_to_show = ["ensemble_mean", "yamnet_gunshot", "crest_factor_db", "spectral_flatness", "high_band_ratio", "low_band_ratio", "spectral_centroid_hz", "v3_raw_fusion_score"]
print(df_analysis.groupby("condition")[cols_to_show].mean().to_string())

