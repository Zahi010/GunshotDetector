"""
Train the Detector Improvement V3 Acoustic Fusion Classifier on the Development Partition.
"""

import sys
sys.path.insert(0, ".")
import pathlib
import numpy as np
import joblib
from sklearn.ensemble import HistGradientBoostingClassifier

# Ensure output directory exists
out_dir = pathlib.Path("experiments/detector_improvement_v3")
out_dir.mkdir(parents=True, exist_ok=True)

records = joblib.load("scratch/v3_dev_features.joblib")
print(f"Loaded {len(records)} development records.")

GUN_CLASSES = [421, 422, 424, 425]
BALLISTIC_CLASSES = [420, 421, 422, 424, 425, 428, 434, 460]
FIREWORKS_CLASSES = [426, 427]
THUNDER_CLASSES = [280, 281]
IMPACT_CLASSES = [413, 414, 352, 353, 58]
NON_TARGET_SEMANTIC_CLASSES = ([0] + list(range(67, 118)) + list(range(300, 331)) + [502, 503, 504])

X_list = []
y_list = []
for r in records:
    gt = r["ground_truth"]
    ys = r["yamnet_scores"]
    p_mlp = r["p_mlp"]
    p_cb = r["p_cb"]
    p_lgb = r["p_lgb"]
    p_xgb = r["p_xgb"]
    acoustics = r["win_acoustics"]
    
    for w in range(r["n_windows"]):
        m, c, l, x = p_mlp[w], p_cb[w], p_lgb[w], p_xgb[w]
        crest, flat, hi, lo, cent = acoustics[w]
        
        gun_s = max(float(ys[w][cls]) for cls in GUN_CLASSES)
        bal_s = max(float(ys[w][cls]) for cls in BALLISTIC_CLASSES)
        fw_s = max(float(ys[w][cls]) for cls in FIREWORKS_CLASSES)
        thun_s = max(float(ys[w][cls]) for cls in THUNDER_CLASSES)
        imp_s = max(float(ys[w][cls]) for cls in IMPACT_CLASSES)
        nt_s = max(float(ys[w][cls]) for cls in NON_TARGET_SEMANTIC_CLASSES)
        
        m_mean = (m + c + l + x) / 4.0
        m_max = max(m, c, l, x)
        m_min = min(m, c, l, x)
        m_std = float(np.std([m, c, l, x]))
        sorted_m = sorted([m, c, l, x], reverse=True)
        top2 = (sorted_m[0] + sorted_m[1]) / 2.0
        
        feats = [
            m, c, l, x,
            m_mean, m_max, m_min, m_std, top2,
            gun_s, bal_s, fw_s, thun_s, imp_s, nt_s,
            (bal_s + 1e-4) / (fw_s + 1e-4),
            (bal_s + 1e-4) / (imp_s + 1e-4),
            crest, flat, hi, lo, cent
        ]
        
        y_label = 1 if (gt == 1 and (m_max > 0.35 or crest > 12.0)) else 0
        X_list.append(feats)
        y_list.append(y_label)

X = np.array(X_list, dtype=np.float32)
y = np.array(y_list, dtype=np.int32)
print(f"Training fusion model on {len(y)} windows (Pos: {np.sum(y==1)}, Neg: {np.sum(y==0)})...")

model = HistGradientBoostingClassifier(
    max_iter=60,
    max_depth=3,
    l2_regularization=2.5,
    min_samples_leaf=20,
    random_state=42
)
model.fit(X, y)

model_path = out_dir / "fusion_model.joblib"
joblib.dump(model, model_path)
print(f"Saved calibrated fusion model to {model_path}!")

