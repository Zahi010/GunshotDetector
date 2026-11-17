import sys, os, pathlib
sys.path.insert(0, os.path.abspath("."))
sys.path.insert(0, os.path.abspath("src"))

import soundfile as sf
import numpy as np
import pandas as pd
from scratch.test_v8_candidate import DetectorImprovementV8
from experiments.detector_improvement_v7.model_detector_improvement_v7 import DetectorImprovementV7

v7 = DetectorImprovementV7()
v8 = DetectorImprovementV8()

# 1. Inspect Phase 19 files where V7 detected but V8 missed
p19_dir = pathlib.Path("data/phase19_independent_positive/normalized_16k")
p19_files = sorted(list(p19_dir.glob("*.wav")))

print("\n=== Phase 19 Differences (V7 True, V8 False) ===")
for fpath in p19_files:
    y, sr = sf.read(fpath)
    v7.reset(); res7 = v7.evaluate_waveform(y, sr)
    v8.reset(); res8 = v8.evaluate_waveform(y, sr)
    if res7["detected"] and not res8["detected"]:
        print(f"\nMissed in V8: {fpath.name}")
        win_size = 15360
        hop_size = 7680
        n_wins = 1 + int((len(y) - win_size) // hop_size) if len(y) >= win_size else 1
        for w in range(n_wins):
            win = y[w*hop_size : w*hop_size + win_size] if len(y) >= win_size else np.pad(y, (0, win_size - len(y)))
            feat, ys, acoustics = v7.extract_features(win)
            crest, flat, hi, mid, lo, m2l, rolloff, cent, rms, peak = acoustics
            raw_s = float(v7.fusion_model.predict_proba(feat.reshape(1, -1))[:, 1][0])
            supp7 = v7.suppression.apply_suppression(raw_s, ys, acoustics)
            supp8 = v8.suppression.apply_suppression(raw_s, ys, acoustics)
            print(f"  w={w}: raw={raw_s:.4f} | V7_adj={supp7['adjusted_score']:.4f} (cat={supp7['category']}) | V8_adj={supp8['adjusted_score']:.4f} (cat={supp8['category']}) | crest={crest:.2f}dB | m2l={m2l:.3f} | cent={cent:.1f}Hz")

