import sys, os
sys.path.insert(0, os.path.abspath("."))
sys.path.insert(0, os.path.abspath("src"))

import soundfile as sf
import numpy as np
from experiments.detector_improvement_v7.model_detector_improvement_v7 import DetectorImprovementV7

v7 = DetectorImprovementV7()
fpath = "data/phase15_independent_eval/gunshots/phase15_gunshot_urban_shotspotter_d5_01.wav"
y, sr = sf.read(fpath)
if y.ndim > 1: y = np.mean(y, axis=1)

win_size = 15360
hop_size = 7680
n_wins = 1 + int((len(y) - win_size) // hop_size) if len(y) >= win_size else 1
v7.reset()
for w in range(n_wins):
    win = y[w*hop_size : w*hop_size + win_size] if len(y) >= win_size else np.pad(y, (0, win_size - len(y)))
    t = w * 0.48
    feat, ys, acoustics = v7.extract_features(win)
    crest, flat, hi, mid, lo, m2l, rolloff, cent, rms, peak = acoustics
    mode, _, _ = v7.estimator.update(rolloff, hi, mid, lo, m2l, t, w)
    raw_s = float(v7.fusion_model.predict_proba(feat.reshape(1, -1))[:, 1][0])
    supp = v7.suppression.apply_suppression(raw_s, ys, acoustics)
    adj_s = supp["adjusted_score"]
    st, ev = v7.fsm.step(adj_s, crest, t, acoustics, mode)
    print(f"w={w}: raw={raw_s:.4f}, adj={adj_s:.4f}, supp={supp['category']}, crest={crest:.2f}dB, mode={mode.value}, st={st}, ev={ev is not None}")

