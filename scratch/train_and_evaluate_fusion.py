"""
Train and evaluate Acoustic Fusion Model on the development partition under GroupKFold.
"""

import sys
sys.path.insert(0, ".")
import numpy as np
import pandas as pd
import joblib
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestClassifier
from sklearn.model_selection import GroupKFold
from sklearn.metrics import roc_auc_score, average_precision_score
from experiments.detector_improvement_v2.model_detector_improvement_v2 import (
    CalibratedAcousticSuppressionV2,
    EventStateMachineV2
)

records = joblib.load("scratch/v3_dev_features.joblib")
print(f"Loaded {len(records)} development records.")

GUN_CLASSES = [421, 422, 424, 425]
BALLISTIC_CLASSES = [420, 421, 422, 424, 425, 428, 434, 460]
FIREWORKS_CLASSES = [426, 427]
THUNDER_CLASSES = [280, 281]
IMPACT_CLASSES = [413, 414, 352, 353, 58]
NON_TARGET_SEMANTIC_CLASSES = ([0] + list(range(67, 118)) + list(range(300, 331)) + [502, 503, 504])

# Build window-level dataset
X_list = []
y_list = []
groups_list = []
rec_indices = []

for r_idx, r in enumerate(records):
    gt = r["ground_truth"]
    grp = r["uploader_or_recordist"]
    ys = r["yamnet_scores"]
    p_mlp = r["p_mlp"]
    p_cb = r["p_cb"]
    p_lgb = r["p_lgb"]
    p_xgb = r["p_xgb"]
    acoustics = r["win_acoustics"]
    
    for w in range(r["n_windows"]):
        m = p_mlp[w]
        c = p_cb[w]
        l = p_lgb[w]
        x = p_xgb[w]
        
        # Only consider windows where at least one model or acoustics show activity
        # or sample negative background windows
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
        
        # Label: if ground_truth is 1, label is 1 for windows near peak
        # In FSD50K gunshots, peak windows contain the blast
        # For negatives, all windows are 0
        if gt == 1:
            # Only count as positive window if model or crest shows the event window
            if m_max > 0.35 or crest > 12.0:
                y_label = 1
            else:
                y_label = 0
        else:
            y_label = 0
            
        X_list.append(feats)
        y_list.append(y_label)
        groups_list.append(grp)
        rec_indices.append(r_idx)

X = np.array(X_list, dtype=np.float32)
y = np.array(y_list, dtype=np.int32)
groups = np.array(groups_list)
print(f"Total windows: {len(y)}, Positive windows: {np.sum(y == 1)}, Negative windows: {np.sum(y == 0)}")

# Check feature names
feature_names = [
    "mlp", "cb", "lgb", "xgb",
    "model_mean", "model_max", "model_min", "model_std", "top2_mean",
    "yamnet_gun", "yamnet_ballistic", "yamnet_fireworks", "yamnet_thunder", "yamnet_impact", "yamnet_non_target",
    "bal_to_fw_ratio", "bal_to_imp_ratio",
    "crest_factor_db", "spectral_flatness", "high_freq_ratio", "low_freq_ratio", "spectral_centroid"
]

# Evaluate models with GroupKFold
gkf = GroupKFold(n_splits=5)
print("\n--- Evaluating Classifiers with 5-fold GroupKFold ---")

# 1. Regularized Logistic Regression
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline

pipe_lr = Pipeline([
    ("scaler", StandardScaler()),
    ("clf", LogisticRegression(C=0.5, max_iter=1000, class_weight="balanced"))
])

oof_lr = np.zeros(len(y))
for fold, (trn_idx, val_idx) in enumerate(gkf.split(X, y, groups)):
    pipe_lr.fit(X[trn_idx], y[trn_idx])
    oof_lr[val_idx] = pipe_lr.predict_proba(X[val_idx])[:, 1]

print(f"Logistic Regression OOF ROC-AUC: {roc_auc_score(y, oof_lr):.4f}, PR-AUC: {average_precision_score(y, oof_lr):.4f}")

# 2. HistGradientBoostingClassifier (shallow, regularized)
pipe_gb = Pipeline([
    ("scaler", StandardScaler()),
    ("clf", HistGradientBoostingClassifier(max_iter=50, max_depth=3, l2_regularization=2.0, min_samples_leaf=15, random_state=42))
])

oof_gb = np.zeros(len(y))
for fold, (trn_idx, val_idx) in enumerate(gkf.split(X, y, groups)):
    pipe_gb.fit(X[trn_idx], y[trn_idx])
    oof_gb[val_idx] = pipe_gb.predict_proba(X[val_idx])[:, 1]

print(f"HistGradientBoosting OOF ROC-AUC: {roc_auc_score(y, oof_gb):.4f}, PR-AUC: {average_precision_score(y, oof_gb):.4f}")

# Fit on all development data to inspect coefficients / importances
pipe_lr.fit(X, y)
coefs = pipe_lr.named_steps["clf"].coef_[0]
print("\n--- Logistic Regression Feature Coefficients ---")
for fn, c in sorted(zip(feature_names, coefs), key=lambda x: abs(x[1]), reverse=True):
    print(f"{fn:22s}: {c:+.4f}")

