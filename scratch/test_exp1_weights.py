"""
Experiment 1: Re-weighting and Calibrating the 4 Ensemble Models
(MLP, CatBoost, LightGBM, XGBoost) on the Development Set.
"""

import sys
sys.path.insert(0, ".")
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

p38_cache = pathlib.Path("experiments/phase38/feature_cache")
p39_cache = pathlib.Path("experiments/phase39/feature_cache")
p40_cache = pathlib.Path("experiments/phase40/feature_cache")

def get_cache(rid):
    for c in [p40_cache, p39_cache, p38_cache]:
        f = c / f"{rid}.npz"
        if f.exists(): return f
    return None

parts = pd.read_csv("scratch/v2_partitions.csv")
inv = pd.read_csv("experiments/phase41/phase41_recording_inventory.csv")
v2_pred = pd.read_csv("experiments/detector_improvement_v2/recording_level_predictions.csv")

merged = pd.merge(inv, parts[['recording_id', 'v2_partition']], on='recording_id')
merged = pd.merge(merged, v2_pred[['recording_id', 'v2_detected', 'v2_event_count', 'v2_peak_score', 'crest_factor_db']], on='recording_id')
dev_df = merged[merged['v2_partition'] == 'development'].copy()

# Precompute model predictions on dev set windows
print(f"Precomputing model predictions for {len(dev_df)} dev recordings...")
dev_cached = []
for _, r in dev_df.iterrows():
    rid = r['recording_id']
    f = get_cache(rid)
    if f is None: continue
    npz = np.load(f)
    embs = npz['embeddings']
    ys = npz['yamnet_scores']
    if len(embs) == 0: continue
    
    mlp_preds = mlp.predict(embs, verbose=0).flatten()
    cb_preds = cb.predict_proba(embs)[:, 1]
    lgb_preds = lgb.predict_proba(embs)[:, 1]
    xgb_preds = xgb.predict_proba(embs)[:, 1]
    
    dev_cached.append({
        "recording_id": rid,
        "sub_category": r['sub_category'],
        "ground_truth": 1 if r['evaluation_role'] == 'PROSPECTIVE_POSITIVE_EVALUATION' else 0,
        "duration_sec": r['duration_seconds'],
        "crest_factor_db": r['crest_factor_db'],
        "n_windows": len(embs),
        "mlp": mlp_preds,
        "cb": cb_preds,
        "lgb": lgb_preds,
        "xgb": xgb_preds,
        "yamnet": ys
    })

print(f"Done precomputing for {len(dev_cached)} recordings.")

from experiments.detector_improvement_v2.model_detector_improvement_v2 import (
    CalibratedAcousticSuppressionV2,
    EventStateMachineV2
)

# Test different weight blends
# Current default in bundle: w = [0.25, 0.35, 0.25, 0.15]
weight_configs = [
    ("V2_baseline_weights", [0.25, 0.35, 0.25, 0.15]),
    ("Equal_weights", [0.25, 0.25, 0.25, 0.25]),
    ("MLP_heavy_35", [0.35, 0.25, 0.25, 0.15]),
    ("MLP_heavy_45", [0.45, 0.25, 0.20, 0.10]),
    ("MLP_heavy_55", [0.55, 0.20, 0.15, 0.10]),
    ("Tree_heavy", [0.15, 0.40, 0.30, 0.15]),
    ("CatBoost_XGB_dominant", [0.20, 0.40, 0.15, 0.25]),
]

def eval_weights(weights):
    w1, w2, w3, w4 = weights
    supp = CalibratedAcousticSuppressionV2({
        "enabled": True,
        "coherence_safeguard": {"enabled": True, "ballistic_max_threshold": 0.015, "non_target_threshold": 0.12, "attenuation": 0.20},
        "fireworks": {"dominant_threshold": 0.45, "dominant_ratio": 1.8, "dominant_gun_max": 0.25, "dominant_attenuation": 0.30, "standard_threshold": 0.30, "standard_ratio": 1.5, "standard_gun_max": 0.12, "standard_attenuation": 0.35},
        "wind_buffeting": {"threshold": 0.25, "ratio": 1.5, "attenuation": 0.25},
        "mechanical_impact": {"threshold": 0.30, "ratio": 1.5, "gun_max": 0.20, "attenuation": 0.35},
        "thunder": {"threshold": 0.25, "ratio": 1.5, "attenuation": 0.30},
        "canine": {"threshold": 0.30, "ratio": 1.5, "attenuation": 0.35},
        "fire_crackle": {"threshold": 0.25, "ratio": 1.5, "attenuation": 0.35},
        "siren": {"threshold": 0.35, "ratio": 1.5, "attenuation": 0.30}
    })
    
    pos_det = 0; pos_tot = 0
    fw_fps = 0; fw_tot = 0
    env_fps = 0; env_tot = 0
    cont_evs = 0; cont_tot = 0
    
    for d in dev_cached:
        gt = d['ground_truth']
        sc = d['sub_category']
        dur = d['duration_sec']
        crest = d['crest_factor_db']
        nw = d['n_windows']
        
        if gt == 1: pos_tot += 1
        elif sc == 'DISTRACTOR_FIREWORKS': fw_tot += 1
        elif sc.startswith('DISTRACTOR_'): env_tot += 1
        elif sc == 'LONG_AMBIENT_STREAM': cont_tot += 1
        
        raw_s = w1 * d['mlp'] + w2 * d['cb'] + w3 * d['lgb'] + w4 * d['xgb']
        
        fsm = EventStateMachineV2(
            threshold_base=0.75,
            threshold_high=0.88,
            threshold_off=0.48,
            confirm_windows=2,
            cooldown_secs=2.0,
            allow_single_impulse_exception=True,
            single_impulse_min_score=0.82,
            single_impulse_min_crest_db=14.0,
            single_impulse_max_dur_sec=5.0
        )
        
        for i in range(nw):
            st = i * 0.48; et = min(dur, st + 0.96)
            r_sc = float(raw_s[i])
            ym = d['yamnet'][i] if i < len(d['yamnet']) else None
            supp_res = supp.apply_suppression(r_sc, ym, is_in_confirmed_event=(fsm.state.value == 'CONFIRMED'))
            
            win_rec = {
                "window_index": i, "start_time": st, "end_time": et,
                "raw_score": r_sc, "score": supp_res["adjusted_score"],
                "crest_factor_db": crest,
                "suppression_active": supp_res["suppression_active"]
            }
            fsm.process_window(win_rec, crest_factor_db=crest, audio_duration_sec=dur, total_windows_in_stream=nw)
        fsm.flush()
        
        det = len(fsm.events_emitted) > 0
        cnt = len(fsm.events_emitted)
        
        if gt == 1 and det: pos_det += 1
        elif sc == 'DISTRACTOR_FIREWORKS' and det: fw_fps += 1
        elif sc.startswith('DISTRACTOR_') and det: env_fps += 1
        elif sc == 'LONG_AMBIENT_STREAM': cont_evs += cnt
        
    return {
        "pos_recall": pos_det / pos_tot,
        "pos_count": pos_det,
        "fw_fps": fw_fps,
        "env_fps": env_fps,
        "cont_evs": cont_evs
    }

print("\n=== EXPERIMENT 1: ENSEMBLE WEIGHTS COMPARISON ON DEV SET ===")
for name, w in weight_configs:
    r = eval_weights(w)
    print(f"{name:25s} {str(w):26s} -> Pos: {r['pos_count']}/72 ({r['pos_recall']*100:.1f}%), FW_FP: {r['fw_fps']}/59, Env_FP: {r['env_fps']}/72, Cont_Evs: {r['cont_evs']}")
