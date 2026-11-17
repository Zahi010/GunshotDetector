import sys, os
sys.path.insert(0, os.path.abspath("."))
sys.path.insert(0, os.path.abspath("src"))

import soundfile as sf
import numpy as np
from experiments.detector_improvement_v6.model_detector_improvement_v6 import DetectorImprovementV6

v6 = DetectorImprovementV6()
for name, fpath in [("p12_neg_071", "data/phase12_independent_test/negatives/phase12_negative_esc50_fireworks_3-251617-A-48.wav"),
                    ("p12_neg_074", "data/phase12_independent_test/negatives/phase12_negative_esc50_fireworks_4-119647-C-48.wav")]:
    y, sr = sf.read(fpath)
    n_wins = 1 + int((len(y) - 15360) // 7680)
    print(f"\n=== {name} ===")
    for w in range(n_wins):
        win = y[w*7680 : w*7680 + 15360]
        feat, ys, acoustics = v6.extract_features(win)
        crest, flat, hi, mid, lo, m2l, rolloff, cent, rms, peak = acoustics
        raw_s = float(v6.fusion_model.predict_proba(feat.reshape(1, -1))[:, 1][0])
        supp = v6.suppression.apply_suppression(raw_s, ys, acoustics)
        pure = max(ys.get(c, 0) for c in [421, 422, 423])
        fw = max(ys.get(c, 0) for c in [426, 427])
        bal = max(ys.get(c, 0) for c in [420])
        print(f"w={w}: raw={raw_s:.4f}, adj={supp['adjusted_score']:.4f}, cat={supp['category']}, crest={crest:.2f}dB, m2l={m2l:.3f}, cent={cent:.1f}Hz, pure={pure:.3f}, fw={fw:.3f}, bal={bal:.3f}")

