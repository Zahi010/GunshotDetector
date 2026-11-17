import sys, os
sys.path.insert(0, os.path.abspath("."))
sys.path.insert(0, os.path.abspath("src"))

import soundfile as sf
import numpy as np
from experiments.detector_improvement_v7.model_detector_improvement_v7 import DetectorImprovementV7

v7 = DetectorImprovementV7()
files = [
    ("train_115", "data/phase12_independent_test/negatives/phase12_negative_esc50_train_4-165791-B-45.wav"),
    ("glass_120", "data/phase12_independent_test/negatives/phase12_negative_esc50_glass_breaking_3-216284-A-39.wav")
]

for name, fpath in files:
    y, sr = sf.read(fpath)
    if y.ndim > 1: y = np.mean(y, axis=1)
    win_size = 15360
    hop_size = 7680
    n_wins = 1 + int((len(y) - win_size) // hop_size) if len(y) >= win_size else 1
    v7.reset()
    print(f"\n=== {name} ===")
    for w in range(n_wins):
        win = y[w*hop_size : w*hop_size + win_size] if len(y) >= win_size else np.pad(y, (0, win_size - len(y)))
        feat, ys, acoustics = v7.extract_features(win)
        crest, flat, hi, mid, lo, m2l, rolloff, cent, rms, peak = acoustics
        mode, _, _ = v7.estimator.update(rolloff, hi, mid, lo, m2l, w * 0.48, w)
        raw_s = float(v7.fusion_model.predict_proba(feat.reshape(1, -1))[:, 1][0])
        supp7 = v7.suppression.apply_suppression(raw_s, ys, acoustics)
        print(f"w={w}: raw={raw_s:.4f}, v7_adj={supp7['adjusted_score']:.4f}, cat={supp7['category']}, mode={mode.value}, crest={crest:.2f}dB")

