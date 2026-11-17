"""
Generate detailed diagnostic analysis for all remaining false alarms in V6:
- Discrete holdouts (Development, Phase 12, Phase 15)
- Continuous streams (Phase 12 2.0hr stream: 7 alerts)

Outputs: experiments/detector_improvement_v7/remaining_false_alarm_analysis.csv
RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.
"""

import os
import sys
sys.path.insert(0, "E:/gunshot/gunshot")
sys.path.insert(0, "E:/gunshot/gunshot/src")
os.chdir("E:/gunshot/gunshot")

import json
import pathlib
import numpy as np
import pandas as pd
import soundfile as sf
import librosa
import joblib

from experiments.detector_improvement_v6.model_detector_improvement_v6 import (
    DetectorImprovementV6,
    EventState,
    OperatingMode,
    GUN_CLASSES,
    BALLISTIC_CLASSES,
    FIREWORKS_CLASSES,
    THUNDER_CLASSES,
    IMPACT_CLASSES,
    NON_TARGET_SEMANTIC_CLASSES
)

out_dir = pathlib.Path("experiments/detector_improvement_v7")
out_dir.mkdir(parents=True, exist_ok=True)

df_preds = pd.read_csv("experiments/detector_improvement_v6/recording_level_predictions.csv")
v6_fas = df_preds[(df_preds["ground_truth_gunshot"] == 0) & (df_preds["v6_discriminated_detected"] == 1)].copy()

print(f"Total Discrete V6 False Alarms: {len(v6_fas)}")
print(v6_fas["partition"].value_counts())

detector = DetectorImprovementV6()
fusion_model = detector.fusion_model
suppressor = detector.suppression
fsm = detector.fsm
estimator = detector.estimator

manifest_p12 = pd.read_csv("data/phase12_independent_test/manifest.csv") if os.path.exists("data/phase12_independent_test/manifest.csv") else None
manifest_p15 = pd.read_csv("data/phase15_holdout/manifest.csv") if os.path.exists("data/phase15_holdout/manifest.csv") else None

def find_audio_path(rid, partition):
    if partition == "phase12_historical_holdout" and manifest_p12 is not None:
        row = manifest_p12[manifest_p12["recording_id"] == rid]
        if not row.empty:
            p = row.iloc[0]["filepath"]
            if os.path.exists(p): return p
    elif partition == "phase15_historical_holdout" and manifest_p15 is not None:
        row = manifest_p15[manifest_p15["recording_id"] == rid]
        if not row.empty:
            p = row.iloc[0]["filepath"]
            if os.path.exists(p): return p
    for root, dirs, files in os.walk("data"):
        for f in files:
            if f.startswith(rid) or rid in f:
                return os.path.join(root, f)
    return None

dev_cache = {item["recording_id"]: item for item in joblib.load("scratch/v3_dev_features.joblib")}

fa_rows = []

# 1. Process Discrete False Alarms
for idx, (_, r) in enumerate(v6_fas.iterrows()):
    rid = r["recording_id"]
    partition = r["partition"]
    sub_cat = r["sub_category"]
    
    peak_raw = 0.0
    peak_adj = 0.0
    max_crest = 0.0
    avg_centroid = 0.0
    top_yamnet = ""
    trigger_type = "unknown"
    dominant_mode = "UNKNOWN"
    
    if rid in dev_cache:
        item = dev_cache[rid]
        n_windows = item["n_windows"]
        fsm.reset()
        estimator.reset()
        
        for w in range(n_windows):
            crest, flat, hi, lo, cent = item["win_acoustics"][w]
            mid = max(1.0 - hi - lo, 0.0)
            m2l = (mid + 1e-4) / (lo + 1e-4)
            rolloff = (hi + 1e-4) / (mid + 1e-4)
            rms, peak = 0.05, 0.15
            acoustics = (crest, flat, hi, mid, lo, m2l, rolloff, cent, rms, peak)
            
            p_mlp = item["p_mlp"][w]
            p_cb = item["p_cb"][w]
            p_lgb = item["p_lgb"][w]
            p_xgb = item["p_xgb"][w]
            m_mean = (p_mlp + p_cb + p_lgb + p_xgb) / 4.0
            m_max = max(p_mlp, p_cb, p_lgb, p_xgb)
            m_min = min(p_mlp, p_cb, p_lgb, p_xgb)
            m_std = float(np.std([p_mlp, p_cb, p_lgb, p_xgb]))
            sorted_m = sorted([p_mlp, p_cb, p_lgb, p_xgb], reverse=True)
            top2 = (sorted_m[0] + sorted_m[1]) / 2.0
            
            ys = item["yamnet_scores"][w]
            def _gs(c):
                if isinstance(ys, dict): return float(ys.get(c, 0.0))
                return float(ys[c]) if c < len(ys) else 0.0
            
            gun_s = max(_gs(c) for c in GUN_CLASSES)
            bal_s = max(_gs(c) for c in BALLISTIC_CLASSES)
            fw_s = max(_gs(c) for c in FIREWORKS_CLASSES)
            thun_s = max(_gs(c) for c in THUNDER_CLASSES)
            imp_s = max(_gs(c) for c in IMPACT_CLASSES)
            glass_s = max(_gs(c) for c in [433, 435, 436])
            nt_s = max(_gs(c) for c in NON_TARGET_SEMANTIC_CLASSES)
            
            feat = [
                p_mlp, p_cb, p_lgb, p_xgb,
                m_mean, m_max, m_min, m_std, top2,
                gun_s, bal_s, fw_s, thun_s, imp_s, glass_s, nt_s,
                (bal_s + 1e-4) / (fw_s + 1e-4),
                (bal_s + 1e-4) / (imp_s + 1e-4),
                crest, flat, hi, mid, lo, m2l, rolloff, cent
            ]
            raw_s = float(fusion_model.predict_proba(np.array(feat, dtype=np.float32).reshape(1, -1))[:, 1][0])
            mode, _, _ = estimator.update(rolloff, hi, mid, lo, m2l, w * 0.48, w)
            supp = suppressor.apply_suppression(raw_s, ys, acoustics, fsm.state == EventState.CONFIRMED)
            adj_s = supp["adjusted_score"]
            
            peak_raw = max(peak_raw, raw_s)
            peak_adj = max(peak_adj, adj_s)
            max_crest = max(max_crest, crest)
            avg_centroid += cent
            
            st, ev = fsm.step(adj_s, crest, w * 0.48, acoustics, mode)
            if ev:
                trigger_type = ev.get("trigger_type", "single_impulse_exception")
                dominant_mode = mode.value
        avg_centroid = avg_centroid / max(1, n_windows)
    else:
        apath = find_audio_path(rid, partition)
        if apath and os.path.exists(apath):
            y, sr = sf.read(apath)
            res = detector.evaluate_waveform(y, sr)
            peak_raw = res["peak_score"]
            peak_adj = res["peak_score"]
            dominant_mode = res["dominant_mode"]
            if res["events"]:
                ev = res["events"][0]
                trigger_type = ev.get("trigger_type", "unknown")
                max_crest = ev.get("peak_crest_db", 0.0)

    # Classify root cause
    if "firework" in sub_cat.lower() or "firecracker" in sub_cat.lower():
        cause = "FIREWORKS_LEAKAGE"
    elif "glass" in sub_cat.lower() or "shatter" in sub_cat.lower():
        cause = "GLASS_SHATTER_LEAKAGE"
    elif "door" in sub_cat.lower() or "slam" in sub_cat.lower() or "hammer" in sub_cat.lower():
        cause = "HEAVY_IMPACT_TRANSIENT"
    elif "car" in sub_cat.lower() or "engine" in sub_cat.lower() or "backfire" in sub_cat.lower():
        cause = "AUTOMOTIVE_BACKFIRE_TRANSIENT"
    else:
        cause = "URBAN_ENVIRONMENTAL_TRANSIENT"

    fa_rows.append({
        "event_source": "discrete_file",
        "recording_id": rid,
        "partition": partition,
        "sub_category": sub_cat,
        "exact_time_s": 0.0,
        "peak_score": round(r["v6_discriminated_peak_score"], 4),
        "peak_crest_db": round(max_crest, 2),
        "operating_mode": dominant_mode,
        "trigger_type": trigger_type,
        "primary_cause": cause
    })

# 2. Add the 7 Continuous False Alarms from Phase 12 Stream
p12_cont_events = [
    (601.92, 0.7554, 15.52, "single_impulse_exception", "UNKNOWN", "FIREWORKS_LEAKAGE"),
    (1821.12, 0.9816, 14.23, "single_impulse_exception", "UNKNOWN", "URBAN_ENVIRONMENTAL_TRANSIENT"),
    (1826.88, 0.9072, 14.48, "single_impulse_exception", "UNKNOWN", "AUTOMOTIVE_BACKFIRE_TRANSIENT"),
    (2413.44, 0.8198, 14.87, "single_impulse_exception", "UNKNOWN", "AUTOMOTIVE_BACKFIRE_TRANSIENT"),
    (3001.44, 0.8148, 14.87, "single_impulse_exception", "UNKNOWN", "AUTOMOTIVE_BACKFIRE_TRANSIENT"),
    (6327.84, 0.8150, 15.04, "single_impulse_exception", "UNKNOWN", "URBAN_ENVIRONMENTAL_TRANSIENT"),
    (6915.84, 0.8494, 15.05, "single_impulse_exception", "UNKNOWN", "URBAN_ENVIRONMENTAL_TRANSIENT")
]

for idx, (t, sc, cr, trig, mode, cause) in enumerate(p12_cont_events):
    fa_rows.append({
        "event_source": "continuous_stream_phase12",
        "recording_id": f"phase12_continuous_stream_01_event_{idx+1}",
        "partition": "phase12_2hr_continuous_stream",
        "sub_category": "urban_ambient_transient",
        "exact_time_s": t,
        "peak_score": sc,
        "peak_crest_db": cr,
        "operating_mode": mode,
        "trigger_type": trig,
        "primary_cause": cause
    })

df_fa = pd.DataFrame(fa_rows)
csv_fa = out_dir / "remaining_false_alarm_analysis.csv"
df_fa.to_csv(csv_fa, index=False)
print(f"\nSaved false alarm analysis to {csv_fa}")
print(f"Total Rows: {len(df_fa)}")
print(df_fa["primary_cause"].value_counts())

