import sys, os
sys.path.insert(0, os.path.abspath("."))
sys.path.insert(0, os.path.abspath("src"))

import soundfile as sf
import numpy as np
import librosa
from scratch.test_v8_candidate import DetectorImprovementV8

v8 = DetectorImprovementV8()
fpath = "data/phase12_independent_test/negatives/phase12_negative_esc50_glass_breaking_3-216284-A-39.wav"
y, sr = sf.read(fpath)
if y.ndim > 1: y = np.mean(y, axis=1)
if sr != 16000: y = librosa.resample(y, orig_sr=sr, target_sr=16000)

n_wins = 1 + int((len(y) - 15360) // 7680)
v8.reset()
print(f"=== Glass Breaking (n_wins={n_wins}) ===")
for w in range(n_wins):
    win = y[w*7680 : w*7680 + 15360]
    t = w * 0.48
    feat, ys, acoustics = v8.extract_features(win)
    crest, flat, hi, mid, lo, m2l, rolloff, cent, rms, peak = acoustics
    mode, _, _ = v8.estimator.update(rolloff, hi, mid, lo, m2l, t, w)
    raw_s = float(v8.fusion_model.predict_proba(feat.reshape(1, -1))[:, 1][0])
    supp = v8.suppression.apply_suppression(raw_s, ys, acoustics)
    st, ev = v8.fsm.step(supp["adjusted_score"], crest, t, acoustics, mode)
    if supp["adjusted_score"] >= 0.60 or ev is not None:
        print(f"w={w}: raw={raw_s:.4f}, adj={supp['adjusted_score']:.4f}, cat={supp['category']}, crest={crest:.2f}dB, mode={mode.value}, st={st}, ev={ev is not None}")

