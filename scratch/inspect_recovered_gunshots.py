import sys, os, pathlib
sys.path.insert(0, os.path.abspath("."))
sys.path.insert(0, os.path.abspath("src"))

import soundfile as sf
import numpy as np
from experiments.detector_improvement_v6.model_detector_improvement_v6 import (
    DetectorImprovementV6,
    FIREWORKS_CLASSES,
    PURE_GUN_CLASSES,
    BALLISTIC_CLASSES
)

v6 = DetectorImprovementV6()

files = [
    "data/phase15_independent_eval/gunshots/phase15_gunshot_clipped_ar15rapid09.wav",
    "data/phase15_independent_eval/gunshots/phase15_gunshot_clipped_ar15rapid10.wav",
    "data/phase15_independent_eval/gunshots/phase15_gunshot_urban_shotspotter_d5_01.wav"
]

for fpath in files:
    y, sr = sf.read(fpath)
    if y.ndim > 1: y = np.mean(y, axis=1)
    win_size = 15360
    hop_size = 7680
    n_wins = 1 + int((len(y) - win_size) // hop_size) if len(y) >= win_size else 1
    print(f"\n=== Inspecting {pathlib.Path(fpath).name} ===")
    v6.reset()
    for w in range(n_wins):
        win = y[w*hop_size : w*hop_size + win_size] if len(y) >= win_size else np.pad(y, (0, win_size - len(y)))
        feat, ys, acoustics = v6.extract_features(win)
        crest, flat, hi, mid, lo, m2l, rolloff, cent, rms, peak = acoustics
        raw_s = float(v6.fusion_model.predict_proba(feat.reshape(1, -1))[:, 1][0])
        fw_s = max(ys.get(c, 0.0) for c in FIREWORKS_CLASSES)
        pure_s = max(ys.get(c, 0.0) for c in PURE_GUN_CLASSES)
        bal_s = max(ys.get(c, 0.0) for c in BALLISTIC_CLASSES)
        supp6 = v6.suppression.apply_suppression(raw_s, ys, acoustics)
        print(f"  w={w}: raw={raw_s:.4f}, v6_adj={supp6['adjusted_score']:.4f}, cat={supp6['category']}, crest={crest:.2f}dB, peak={peak:.3f}, fw={fw_s:.3f}, pure={pure_s:.3f}, bal={bal_s:.3f}")
        top_y = sorted([(k, v) for k, v in ys.items() if v > 0.08], key=lambda x: x[1], reverse=True)[:3]
        print(f"    top YAMNet: {top_y}")

