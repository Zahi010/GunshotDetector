import sys, os, pathlib
sys.path.insert(0, os.path.abspath("."))
sys.path.insert(0, os.path.abspath("src"))

import soundfile as sf
import numpy as np
import pandas as pd
from experiments.detector_improvement_v7.model_detector_improvement_v7 import (
    DetectorImprovementV7,
    FIREWORKS_CLASSES,
    PURE_GUN_CLASSES,
    BALLISTIC_CLASSES
)

v7 = DetectorImprovementV7()
p15_manifest = pd.read_csv("reports/phase15_dataset_manifest.csv")

for rid in ["p15_neg_051", "p15_neg_054", "p15_neg_059", "p12_neg_075"]:
    row = p15_manifest[p15_manifest["recording_id"].str.startswith(rid)]
    if len(row) == 0:
        p12_rca = pd.read_csv("experiments/detector_improvement_v4/recording_condition_analysis.csv")
        r12 = p12_rca[p12_rca["recording_id"].str.startswith(rid)]
        fpath = r12.iloc[0]["relative_path"]
    else:
        fpath = row.iloc[0]["filepath"]
        
    y, sr = sf.read(fpath)
    print(f"\n=== Inspecting {rid} ({fpath}) ===")
    v7.reset()
    win_size = 15360
    hop_size = 7680
    n_wins = 1 + int((len(y) - win_size) // hop_size) if len(y) >= win_size else 1
    for w in range(n_wins):
        win = y[w*hop_size : w*hop_size + win_size] if len(y) >= win_size else np.pad(y, (0, win_size - len(y)))
        feat, ys, acoustics = v7.extract_features(win)
        crest, flat, hi, mid, lo, m2l, rolloff, cent, rms, peak = acoustics
        raw_s = float(v7.fusion_model.predict_proba(feat.reshape(1, -1))[:, 1][0])
        fw_s = max(ys.get(c, 0.0) for c in FIREWORKS_CLASSES)
        pure_s = max(ys.get(c, 0.0) for c in PURE_GUN_CLASSES)
        bal_s = max(ys.get(c, 0.0) for c in BALLISTIC_CLASSES)
        supp = v7.suppression.apply_suppression(raw_s, ys, acoustics)
        adj_s = supp["adjusted_score"]
        if adj_s >= 0.70 or raw_s >= 0.70:
            print(f"  w={w}: raw={raw_s:.4f}, adj={adj_s:.4f}, supp={supp['category']}, fw={fw_s:.3f}, pure={pure_s:.3f}, bal={bal_s:.3f}, crest={crest:.2f}dB")
            top_y = sorted([(k, v) for k, v in ys.items() if v > 0.08], key=lambda x: x[1], reverse=True)[:3]
            print(f"    top YAMNet: {top_y}")
