"""
Extract features for development recordings:
- 4 bundle model probabilities (MLP, CatBoost, LightGBM, XGBoost)
- YAMNet semantic class scores
- Fast physical acoustic metrics (crest factor dB, spectral flatness, high ratio, low ratio, centroid)
Save to scratch/v3_dev_features.joblib
"""

import sys
sys.path.insert(0, ".")
import pathlib
import numpy as np
import pandas as pd
import joblib
import tensorflow as tf
import soundfile as sf

bundle_dir = pathlib.Path("models/gunshot_yamnet_bundle")
mlp = tf.keras.models.load_model(str(bundle_dir / "classifier_head.keras"))
cb = joblib.load(str(bundle_dir / "catboost_model.joblib"))
lgb = joblib.load(str(bundle_dir / "lightgbm_model.joblib"))
xgb = joblib.load(str(bundle_dir / "xgboost_model.joblib"))

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

parts = pd.read_csv("scratch/v2_partitions.csv")
inv = pd.read_csv("experiments/phase41/phase41_recording_inventory.csv")
merged = pd.merge(inv, parts[["recording_id", "v2_partition"]], on="recording_id")
dev_df = merged[merged["v2_partition"] == "development"].copy()
print(f"Total dev recordings to process: {len(dev_df)}")

def extract_fast(y_win, sr=16000):
    if len(y_win) == 0:
        return 0.0, 0.0, 0.0, 0.0, 0.0
    pk = np.max(np.abs(y_win))
    rms = np.sqrt(np.mean(y_win**2) + 1e-12)
    crest_db = 20 * np.log10(max(pk / (rms + 1e-12), 1.0))
    P = np.abs(np.fft.rfft(y_win))**2
    freqs = np.fft.rfftfreq(len(y_win), d=1.0/sr)
    flatness = float(np.exp(np.mean(np.log(P + 1e-12))) / (np.mean(P) + 1e-12))
    tot_e = np.sum(P) + 1e-12
    low_e = np.sum(P[freqs < 500])
    high_e = np.sum(P[freqs >= 2500])
    centroid = float(np.sum(freqs * P) / tot_e)
    return float(crest_db), float(flatness), float(high_e / tot_e), float(low_e / tot_e), float(centroid)

records = []
for idx, r in dev_df.iterrows():
    rid = r["recording_id"]
    cache_f = get_cache(rid)
    if cache_f is None:
        continue
    npz = np.load(cache_f)
    embs = npz["embeddings"]
    ys = npz["yamnet_scores"]
    if len(embs) == 0:
        continue
    
    # Run 4 models
    p_mlp = mlp.predict(embs, verbose=0).flatten()
    p_cb = cb.predict_proba(embs)[:, 1]
    p_lgb = lgb.predict_proba(embs)[:, 1]
    p_xgb = xgb.predict_proba(embs)[:, 1]
    
    audio_f = find_audio_file(r)
    win_acoustics = []
    if audio_f is not None and audio_f.exists():
        # Read audio using soundfile (much faster than librosa)
        y, sr = sf.read(str(audio_f))
        if y.ndim > 1:
            y = np.mean(y, axis=1)
        if sr != 16000:
            import librosa
            y = librosa.resample(y, orig_sr=sr, target_sr=16000)
            sr = 16000
        y = y.astype(np.float32)
        
        for w in range(len(embs)):
            st = w * 7680
            ed = st + 15360
            y_win = y[st:ed] if st < len(y) else np.zeros(15360, dtype=np.float32)
            if len(y_win) < 15360:
                y_win = np.pad(y_win, (0, 15360 - len(y_win)))
            crest, flat, hi, lo, cent = extract_fast(y_win, sr=16000)
            win_acoustics.append((crest, flat, hi, lo, cent))
    else:
        for w in range(len(embs)):
            win_acoustics.append((float(npz.get("crest_factor_db", 10.0)), 0.05, 0.1, 0.5, 1500.0))
            
    records.append({
        "recording_id": rid,
        "uploader_or_recordist": r.get("uploader_or_recordist", "unknown"),
        "sub_category": r["sub_category"],
        "evaluation_role": r["evaluation_role"],
        "ground_truth": 1 if r["evaluation_role"] == "PROSPECTIVE_POSITIVE_EVALUATION" else 0,
        "duration_seconds": r["duration_seconds"],
        "n_windows": len(embs),
        "p_mlp": p_mlp,
        "p_cb": p_cb,
        "p_lgb": p_lgb,
        "p_xgb": p_xgb,
        "yamnet_scores": ys,
        "win_acoustics": win_acoustics
    })

print(f"Extracted features for {len(records)} development recordings. Saving to scratch/v3_dev_features.joblib...")
joblib.dump(records, "scratch/v3_dev_features.joblib")
print("Done!")
