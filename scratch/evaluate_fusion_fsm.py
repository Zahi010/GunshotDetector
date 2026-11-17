"""
Evaluate recording-level event detection using the Calibrated Acoustic Fusion model + Event State Machine.
"""

import sys
sys.path.insert(0, ".")
import numpy as np
import pandas as pd
import joblib
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from experiments.detector_improvement_v2.model_detector_improvement_v2 import (
    EventStateMachineV2,
    CalibratedAcousticSuppressionV2
)

records = joblib.load("scratch/v3_dev_features.joblib")

GUN_CLASSES = [421, 422, 424, 425]
BALLISTIC_CLASSES = [420, 421, 422, 424, 425, 428, 434, 460]
FIREWORKS_CLASSES = [426, 427]
THUNDER_CLASSES = [280, 281]
IMPACT_CLASSES = [413, 414, 352, 353, 58]
NON_TARGET_SEMANTIC_CLASSES = ([0] + list(range(67, 118)) + list(range(300, 331)) + [502, 503, 504])

# Build features
X_list = []
y_list = []
groups_list = []
rec_map = [] # (rec_idx, window_idx)

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
        groups_list.append(grp)
        rec_map.append((r_idx, w))

X = np.array(X_list, dtype=np.float32)
y = np.array(y_list, dtype=np.int32)
groups = np.array(groups_list)

# Train calibrated fusion model
clf = HistGradientBoostingClassifier(
    max_iter=60,
    max_depth=3,
    l2_regularization=2.5,
    min_samples_leaf=20,
    random_state=42
)
clf.fit(X, y)

# Score all windows
scores = clf.predict_proba(X)[:, 1]

# Organize scores by recording
rec_scores = {i: [] for i in range(len(records))}
for idx, (r_idx, w) in enumerate(rec_map):
    rec_scores[r_idx].append((scores[idx], X[idx][17])) # (score, crest_factor_db)

# Test FSM thresholds
print("\n=== Grid Search FSM Activation Thresholds for Fusion Model ===")
for th_base in [0.55, 0.60, 0.65, 0.70, 0.75]:
    for single_impulse_th in [0.65, 0.70, 0.75, 0.80]:
        fsm_cfg = {
            "threshold_base": th_base,
            "threshold_high": th_base + 0.12,
            "threshold_off": th_base - 0.25,
            "confirm_windows": 2,
            "cooldown_secs": 2.0,
            "max_hop_gap_s": 0.6,
            "min_crest_factor_db": 8.5,
            "single_win_min_crest_db": 11.5,
            "allow_short_clip_exception": True,
            "allow_single_impulse_exception": True,
            "single_impulse_min_score": single_impulse_th,
            "single_impulse_min_crest_db": 12.0,
            "single_impulse_max_dur_sec": 5.0
        }
        
        pos_det = 0; fw_det = 0; env_det = 0; cont_evs = 0
        for r_idx, r in enumerate(records):
            gt = r["ground_truth"]
            sc = r["sub_category"]
            dur = r["duration_seconds"]
            s_list = rec_scores[r_idx]
            
            fsm = EventStateMachineV2(**fsm_cfg)
            events = []
            for w, (sc_val, crest) in enumerate(s_list):
                t_st = w * 0.48
                t_ed = t_st + 0.96
                win_dict = {
                    "start_time": t_st,
                    "end_time": t_ed,
                    "score": sc_val,
                    "window_index": w
                }
                ev = fsm.process_window(
                    window=win_dict,
                    crest_factor_db=crest,
                    audio_duration_sec=dur,
                    total_windows_in_stream=len(s_list)
                )
                if ev is not None:
                    events.append(ev)
                    
            n_ev = len(events)
            is_det = n_ev > 0
            if gt == 1 and is_det: pos_det += 1
            elif sc == "DISTRACTOR_FIREWORKS" and is_det: fw_det += 1
            elif r["evaluation_role"] == "PROSPECTIVE_NEGATIVE_EVALUATION" and sc != "DISTRACTOR_FIREWORKS":
                if is_det: env_det += 1
            elif r["evaluation_role"] == "PROSPECTIVE_CONTINUOUS_EVALUATION":
                cont_evs += n_ev
                
        print(f"th_base={th_base:.2f}, single_th={single_impulse_th:.2f} -> Pos: {pos_det:2d}/72 ({pos_det/72*100:.1f}%), FW_FP: {fw_det:2d}/59 ({fw_det/59*100:.1f}%), Env_FP: {env_det:2d}/72, Cont_alerts: {cont_evs:2d}")
