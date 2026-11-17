"""
Inspect individual predictions of MLP, CatBoost, LightGBM, XGBoost
on missed gunshots, fireworks, and distractors.
"""

import pathlib
import numpy as np
import pandas as pd
import joblib
import tensorflow as tf

bundle_dir = pathlib.Path("models/gunshot_yamnet_bundle")
mlp = tf.keras.models.load_model(str(bundle_dir / "classifier_head.keras"))
cb = joblib.load(str(bundle_dir / "catboost_model.joblib"))
lgb = joblib.load(str(bundle_dir / "lightgbm_model.joblib"))
xgb = joblib.load(str(bundle_dir / "xgboost_model.joblib"))

p38 = pathlib.Path("experiments/phase38/feature_cache")
p39 = pathlib.Path("experiments/phase39/feature_cache")
p40 = pathlib.Path("experiments/phase40/feature_cache")

def get_cache(rid):
    for c in [p40, p39, p38]:
        f = c / f"{rid}.npz"
        if f.exists():
            return f
    return None

df = pd.read_csv("experiments/detector_improvement_v2/recording_level_predictions.csv")

# 1. Inspect 10 missed gunshots
missed_pos = df[(df['ground_truth_gunshot'] == 1) & (df['v2_detected'] == 0)].head(10)
print("=== INDIVIDUAL MODEL PREDICTIONS ON MISSED GUNSHOTS ===")
for _, r in missed_pos.iterrows():
    f = get_cache(r['recording_id'])
    npz = np.load(f)
    embs = npz['embeddings']
    if len(embs) == 0: continue
    
    mlp_preds = mlp.predict(embs, verbose=0).flatten()
    cb_preds = cb.predict_proba(embs)[:, 1]
    lgb_preds = lgb.predict_proba(embs)[:, 1]
    xgb_preds = xgb.predict_proba(embs)[:, 1]
    
    # Peak window
    pk = np.argmax(npz['raw_scores'])
    print(f"{r['recording_id']:25s} (crest={r['crest_factor_db']:.1f}dB, dur={r['duration_sec']:.2f}s): "
          f"MLP={mlp_preds[pk]:.3f}, CB={cb_preds[pk]:.3f}, LGB={lgb_preds[pk]:.3f}, XGB={xgb_preds[pk]:.3f} -> Raw={npz['raw_scores'][pk]:.3f}")

# 2. Inspect 10 fireworks false alarms
fw_fps = df[(df['sub_category'] == 'DISTRACTOR_FIREWORKS') & (df['v2_detected'] == 1)].head(10)
print("\n=== INDIVIDUAL MODEL PREDICTIONS ON FIREWORKS FALSE ALARMS ===")
for _, r in fw_fps.iterrows():
    f = get_cache(r['recording_id'])
    npz = np.load(f)
    embs = npz['embeddings']
    if len(embs) == 0: continue
    
    mlp_preds = mlp.predict(embs, verbose=0).flatten()
    cb_preds = cb.predict_proba(embs)[:, 1]
    lgb_preds = lgb.predict_proba(embs)[:, 1]
    xgb_preds = xgb.predict_proba(embs)[:, 1]
    
    pk = np.argmax(npz['raw_scores'])
    print(f"{r['recording_id']:35s} (crest={r['crest_factor_db']:.1f}dB): "
          f"MLP={mlp_preds[pk]:.3f}, CB={cb_preds[pk]:.3f}, LGB={lgb_preds[pk]:.3f}, XGB={xgb_preds[pk]:.3f} -> Raw={npz['raw_scores'][pk]:.3f}")

# 3. Inspect continuous false alarms
cont_fps = df[(df['sub_category'] == 'LONG_AMBIENT_STREAM') & (df['v2_detected'] == 1)]
print("\n=== INDIVIDUAL MODEL PREDICTIONS ON CONTINUOUS FALSE ALARMS ===")
for _, r in cont_fps.iterrows():
    f = get_cache(r['recording_id'])
    npz = np.load(f)
    embs = npz['embeddings']
    if len(embs) == 0: continue
    
    mlp_preds = mlp.predict(embs, verbose=0).flatten()
    cb_preds = cb.predict_proba(embs)[:, 1]
    lgb_preds = lgb.predict_proba(embs)[:, 1]
    xgb_preds = xgb.predict_proba(embs)[:, 1]
    
    pk = np.argmax(npz['raw_scores'])
    print(f"{r['recording_id']:30s}: "
          f"MLP={mlp_preds[pk]:.3f}, CB={cb_preds[pk]:.3f}, LGB={lgb_preds[pk]:.3f}, XGB={xgb_preds[pk]:.3f} -> Raw={npz['raw_scores'][pk]:.3f}")

