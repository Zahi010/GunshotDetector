"""
Generate detailed diagnostic analysis for all V6 missed positive recordings across partitions:
- Development Partition (26 misses)
- Phase 12 Historical Holdout (16 misses)
- Phase 15 Historical Holdout (14 misses)
- Phase 19 Field Recordings (7 misses)

Outputs: experiments/detector_improvement_v7/v6_missed_positive_analysis.csv
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
    NON_TARGET_SEMANTIC_CLASSES,
    compute_physical_acoustic_features_v6
)

out_dir = pathlib.Path("experiments/detector_improvement_v7")
out_dir.mkdir(parents=True, exist_ok=True)

# Load V6 predictions
df_preds = pd.read_csv("experiments/detector_improvement_v6/recording_level_predictions.csv")
v6_misses = df_preds[(df_preds["ground_truth_gunshot"] == 1) & (df_preds["v6_discriminated_detected"] == 0)].copy()

print(f"Total V6 Missed Positives: {len(v6_misses)}")
print(v6_misses["partition"].value_counts())

detector = DetectorImprovementV6()
fusion_model = detector.fusion_model
suppressor = detector.suppression
fsm = detector.fsm
estimator = detector.estimator

# Helper to locate audio file for a given recording_id
manifest_p12 = pd.read_csv("data/phase12_independent_test/manifest.csv") if os.path.exists("data/phase12_independent_test/manifest.csv") else None
manifest_p15 = pd.read_csv("data/phase15_holdout/manifest.csv") if os.path.exists("data/phase15_holdout/manifest.csv") else None
manifest_p19 = pd.read_csv("data/phase19_field_tests/manifest.csv") if os.path.exists("data/phase19_field_tests/manifest.csv") else None

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
    elif partition == "phase19_field_recordings" and manifest_p19 is not None:
        row = manifest_p19[manifest_p19["recording_id"] == rid]
        if not row.empty:
            p = row.iloc[0]["filepath"]
            if os.path.exists(p): return p
    
    # Generic search in data/
    for root, dirs, files in os.walk("data"):
        for f in files:
            if f.startswith(rid) or rid in f:
                return os.path.join(root, f)
    return None

# Load cached dev features
dev_cache = {item["recording_id"]: item for item in joblib.load("scratch/v3_dev_features.joblib")}

analysis_rows = []

for idx, (_, r) in enumerate(v6_misses.iterrows()):
    rid = r["recording_id"]
    partition = r["partition"]
    sub_cat = r["sub_category"]
    
    # We will compute window-by-window details
    peak_raw = 0.0
    peak_adj = 0.0
    supp_reasons = set()
    max_crest = 0.0
    avg_centroid = 0.0
    top_yamnet = []
    n_windows = 0
    fsm_state_reached = "IDLE"
    max_cand_windows = 0
    
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
            if supp["category"]:
                supp_reasons.add(supp["category"])
            
            peak_raw = max(peak_raw, raw_s)
            peak_adj = max(peak_adj, adj_s)
            max_crest = max(max_crest, crest)
            avg_centroid += cent
            
            st, _ = fsm.step(adj_s, crest, w * 0.48, acoustics, mode)
            if st == EventState.CONFIRMED:
                fsm_state_reached = "CONFIRMED"
            elif st == EventState.CANDIDATE and fsm_state_reached != "CONFIRMED":
                fsm_state_reached = "CANDIDATE"
                max_cand_windows = max(max_cand_windows, len(fsm.candidate_scores))
        
        avg_centroid = avg_centroid / max(1, n_windows)
    else:
        apath = find_audio_path(rid, partition)
        if apath and os.path.exists(apath):
            y, sr = sf.read(apath)
            if y.ndim > 1: y = np.mean(y, axis=1)
            if sr != 16000: y = librosa.resample(y, orig_sr=sr, target_sr=16000)
            y = y.astype(np.float32)
            
            win_size = 15360
            hop_size = 7680
            if len(y) < win_size:
                y_proc = np.pad(y, (0, win_size - len(y)))
                n_windows = 1
            else:
                y_proc = y
                n_windows = 1 + int((len(y) - win_size) // hop_size)
            
            detector.reset()
            for w in range(n_windows):
                win = y_proc[w*hop_size : w*hop_size + win_size]
                feat, ys, acoustics = detector.extract_features(win)
                crest, flat, hi, mid, lo, m2l, rolloff, cent, rms, peak = acoustics
                raw_s = float(fusion_model.predict_proba(feat.reshape(1, -1))[:, 1][0])
                mode, _, _ = detector.estimator.update(rolloff, hi, mid, lo, m2l, w * 0.48, w)
                supp = detector.suppression.apply_suppression(raw_s, ys, acoustics, detector.fsm.state == EventState.CONFIRMED)
                adj_s = supp["adjusted_score"]
                if supp["category"]:
                    supp_reasons.add(supp["category"])
                
                peak_raw = max(peak_raw, raw_s)
                peak_adj = max(peak_adj, adj_s)
                max_crest = max(max_crest, crest)
                avg_centroid += cent
                
                st, _ = detector.fsm.step(adj_s, crest, w * 0.48, acoustics, mode)
                if st == EventState.CONFIRMED:
                    fsm_state_reached = "CONFIRMED"
                elif st == EventState.CANDIDATE and fsm_state_reached != "CONFIRMED":
                    fsm_state_reached = "CANDIDATE"
                    max_cand_windows = max(max_cand_windows, len(detector.fsm.candidate_scores))
            avg_centroid = avg_centroid / max(1, n_windows)

    # Classify failure mechanism
    if "fireworks_dominant" in supp_reasons or "pyrotechnic_ratio" in supp_reasons:
        failure_mech = "PYROTECHNIC_OVER_SUPPRESSION"
    elif "thunder_rumble" in supp_reasons:
        failure_mech = "REVERB_THUNDER_OVER_SUPPRESSION"
    elif "ballistic_incoherence" in supp_reasons:
        failure_mech = "BALLISTIC_INCOHERENCE_ATTENUATION"
    elif "mechanical_impact" in supp_reasons:
        failure_mech = "MECHANICAL_IMPACT_SUPPRESSION"
    elif n_windows <= 2 and fsm_state_reached == "CANDIDATE":
        failure_mech = "SHORT_FILE_FSM_WINDOW_CUTOFF"
    elif peak_raw < 0.40:
        failure_mech = "LOW_SNR_OCCLUDED_ATTENUATION"
    elif peak_adj >= 0.70 and fsm_state_reached == "IDLE":
        failure_mech = "CREST_FACTOR_BARRIER_UNMET"
    elif peak_adj < 0.70 and peak_raw >= 0.70:
        failure_mech = "GENERAL_SUPPRESSION_DROP"
    else:
        failure_mech = "CONFIRMATION_BARRIER_UNMET"

    analysis_rows.append({
        "recording_id": rid,
        "partition": partition,
        "sub_category": sub_cat,
        "v6_score": round(r["v6_discriminated_peak_score"], 4),
        "peak_raw_score": round(peak_raw, 4),
        "peak_adj_score": round(peak_adj, 4),
        "max_crest_db": round(max_crest, 2),
        "avg_centroid_hz": round(avg_centroid, 1),
        "n_windows": n_windows,
        "fsm_state_reached": fsm_state_reached,
        "max_candidate_windows": max_cand_windows,
        "active_suppressions": "; ".join(sorted(supp_reasons)) if supp_reasons else "none",
        "failure_mechanism": failure_mech
    })

df_analysis = pd.DataFrame(analysis_rows)
csv_path = out_dir / "v6_missed_positive_analysis.csv"
df_analysis.to_csv(csv_path, index=False)
print(f"\nSaved missed positive analysis to {csv_path}")
print("\nFailure Mechanism Breakdown:")
print(df_analysis["failure_mechanism"].value_counts())

