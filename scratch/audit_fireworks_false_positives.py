"""
Audit of Fireworks False Positives under V7:
1. Phase 12 fireworks (8 recordings)
2. Phase 15 fireworks (10 recordings)

Inspects exact window-by-window acoustic and semantic features.
RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.
"""

import sys, os, pathlib
sys.path.insert(0, "E:/gunshot/gunshot")
sys.path.insert(0, "E:/gunshot/gunshot/src")
os.chdir("E:/gunshot/gunshot")

import soundfile as sf
import numpy as np
import pandas as pd

from experiments.detector_improvement_v6.model_detector_improvement_v6 import DetectorImprovementV6
from experiments.detector_improvement_v7.model_detector_improvement_v7 import (
    DetectorImprovementV7,
    PURE_GUN_CLASSES,
    BALLISTIC_CLASSES,
    FIREWORKS_CLASSES,
    THUNDER_CLASSES,
    IMPACT_CLASSES,
    CAP_GUN_CLASS
)

v6 = DetectorImprovementV6()
v7 = DetectorImprovementV7()

# 1. Phase 12 Fireworks
p12_rca = pd.read_csv("experiments/detector_improvement_v4/recording_condition_analysis.csv")
p12_fw = p12_rca[(p12_rca["dataset_source"] == "phase12_independent") & (p12_rca["condition_category"].str.contains("fireworks"))]

# 2. Phase 15 Fireworks
p15_manifest = pd.read_csv("reports/phase15_dataset_manifest.csv")
p15_fw = p15_manifest[p15_manifest["event_classification"].str.contains("firework|firecracker|pyrotechnic", case=False, na=False)]

fw_audit_rows = []

def audit_file(filepath, rid, partition, sub_cat):
    y, sr = sf.read(filepath)
    res_v6 = v6.evaluate_waveform(y, sr)
    res_v7 = v7.evaluate_waveform(y, sr)
    
    win_size = 15360
    hop_size = 7680
    n_wins = 1 + int((len(y) - win_size) // hop_size) if len(y) >= win_size else 1
    
    v6.reset()
    v7.reset()
    
    peak_raw = 0.0
    peak_v6_adj = 0.0
    peak_v7_adj = 0.0
    peak_crest = 0.0
    peak_pure = 0.0
    peak_bal = 0.0
    peak_fw = 0.0
    v6_supp_cats = set()
    v7_supp_cats = set()
    
    for w in range(n_wins):
        if len(y) < win_size:
            win = np.pad(y, (0, win_size - len(y)))
        else:
            win = y[w*hop_size : w*hop_size + win_size]
        feat, ys, acoustics = v7.extract_features(win)
        crest, flat, hi, mid, lo, m2l, rolloff, cent, rms, peak = acoustics
        raw_s = float(v7.fusion_model.predict_proba(feat.reshape(1, -1))[:, 1][0])
        
        mode_v7, _, _ = v7.estimator.update(rolloff, hi, mid, lo, m2l, w * 0.48, w)
        supp_v6 = v6.suppression.apply_suppression(raw_s, ys, acoustics)
        supp_v7 = v7.suppression.apply_suppression(raw_s, ys, acoustics)
        
        if supp_v6["category"]: v6_supp_cats.add(supp_v6["category"])
        if supp_v7["category"]: v7_supp_cats.add(supp_v7["category"])
        
        pure_gun = max(ys.get(c, 0.0) for c in PURE_GUN_CLASSES)
        bal_s = max(ys.get(c, 0.0) for c in BALLISTIC_CLASSES)
        fw_s = max(ys.get(c, 0.0) for c in FIREWORKS_CLASSES)
        
        peak_raw = max(peak_raw, raw_s)
        peak_v6_adj = max(peak_v6_adj, supp_v6["adjusted_score"])
        peak_v7_adj = max(peak_v7_adj, supp_v7["adjusted_score"])
        peak_crest = max(peak_crest, crest)
        peak_pure = max(peak_pure, pure_gun)
        peak_bal = max(peak_bal, bal_s)
        peak_fw = max(peak_fw, fw_s)

    fw_audit_rows.append({
        "recording_id": rid,
        "partition": partition,
        "sub_category": sub_cat,
        "v6_detected": int(res_v6["detected"]),
        "v7_detected": int(res_v7["detected"]),
        "v6_peak": round(res_v6["peak_score"], 4),
        "v7_peak": round(res_v7["peak_score"], 4),
        "peak_raw_score": round(peak_raw, 4),
        "peak_crest_db": round(peak_crest, 2),
        "max_pure_gun": round(peak_pure, 3),
        "max_bal_s": round(peak_bal, 3),
        "max_fw_s": round(peak_fw, 3),
        "v6_suppressions": "; ".join(sorted(v6_supp_cats)) if v6_supp_cats else "none",
        "v7_suppressions": "; ".join(sorted(v7_supp_cats)) if v7_supp_cats else "none"
    })

print("Auditing Phase 12 Fireworks...")
for _, r in p12_fw.iterrows():
    audit_file(r["filepath"], r["recording_id"], "phase12_historical_holdout", r["event_classification"])

print("Auditing Phase 15 Fireworks...")
for _, r in p15_fw.iterrows():
    audit_file(r["filepath"], r["recording_id"], "phase15_historical_holdout", r["event_classification"])

df_fw = pd.DataFrame(fw_audit_rows)
df_fw.to_csv("scratch/fireworks_false_positives_audit.csv", index=False)
print("\n=== FIREWORKS FALSE POSITIVES AUDIT ===")
print(df_fw[["recording_id", "partition", "v6_detected", "v7_detected", "peak_raw_score", "v6_peak", "v7_peak", "max_pure_gun", "max_bal_s", "max_fw_s", "v6_suppressions", "v7_suppressions"]].to_string(index=False))

