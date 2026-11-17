import sys
import pathlib
import joblib
import numpy as np
import pandas as pd
import tensorflow as tf

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
import config

bundle = config.MODELS_DIR / "gunshot_yamnet_bundle"
cb = joblib.load(bundle / "catboost_model.joblib")
lgb = joblib.load(bundle / "lightgbm_model.joblib")
xgb = joblib.load(bundle / "xgboost_model.joblib")
mlp = tf.keras.models.load_model(bundle / "classifier_head.keras")

p38_cache = REPO_ROOT / "experiments" / "phase38" / "feature_cache"
p39_cache = REPO_ROOT / "experiments" / "phase39" / "feature_cache"
inv = pd.read_csv(REPO_ROOT / "experiments" / "phase41" / "phase41_recording_inventory.csv")

pos_clips = inv[inv["evaluation_partition"] == "POSITIVE_GUNSHOT"]
fw_clips = inv[inv["is_fireworks_eval"] == True]

def evaluate_models_on_set(clips, cache_dir):
    mlp_maxes, cb_maxes, lgb_maxes, xgb_maxes, ens_maxes = [], [], [], [], []
    for _, r in clips.iterrows():
        npz = np.load(cache_dir / f"{r['recording_id']}.npz")
        embs = npz["embeddings"]
        if len(embs) == 0:
            continue
        p_mlp = mlp.predict(embs, verbose=0).flatten()
        p_cb = cb.predict_proba(embs)[:, 1]
        p_lgb = lgb.predict_proba(embs)[:, 1]
        p_xgb = xgb.predict_proba(embs)[:, 1]
        p_ens = 0.25 * p_mlp + 0.35 * p_cb + 0.25 * p_lgb + 0.15 * p_xgb
        
        mlp_maxes.append(np.max(p_mlp))
        cb_maxes.append(np.max(p_cb))
        lgb_maxes.append(np.max(p_lgb))
        xgb_maxes.append(np.max(p_xgb))
        ens_maxes.append(np.max(p_ens))
        
    return {
        "mlp": np.array(mlp_maxes),
        "cb": np.array(cb_maxes),
        "lgb": np.array(lgb_maxes),
        "xgb": np.array(xgb_maxes),
        "ens": np.array(ens_maxes)
    }

print("Evaluating Positive Clips...")
pos_res = evaluate_models_on_set(pos_clips, p38_cache)
print("Evaluating Fireworks Clips...")
fw_res = evaluate_models_on_set(fw_clips, p39_cache)

print("\n=== POSITIVE CLIPS (N=120) ===")
for k in ["mlp", "cb", "lgb", "xgb", "ens"]:
    print(f"  {k.upper()}: Mean={np.mean(pos_res[k]):.3f}, >=0.75: {np.sum(pos_res[k] >= 0.75)}, >=0.50: {np.sum(pos_res[k] >= 0.50)}")

print("\n=== FIREWORKS CLIPS (N=100) ===")
for k in ["mlp", "cb", "lgb", "xgb", "ens"]:
    print(f"  {k.upper()}: Mean={np.mean(fw_res[k]):.3f}, >=0.75: {np.sum(fw_res[k] >= 0.75)}, >=0.50: {np.sum(fw_res[k] >= 0.50)}")

