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

files = [
    ("P19-CAT-A-FP1-test_004", "data/phase19_independent_positive/normalized_16k/P19-CAT-A-FP1-test_004.wav"),
    ("p15_pos_009", "data/phase15_independent_eval/gunshots/phase15_gunshot_pocket_ar15rapidpocket11.wav"),
    ("p15_pos_023", "data/phase15_independent_eval/gunshots/phase15_gunshot_clean_ar15double10.wav"),
    ("p15_pos_038", "data/phase15_independent_eval/gunshots/phase15_gunshot_clipped_ar15rapid09.wav"),
    ("p15_pos_039", "data/phase15_independent_eval/gunshots/phase15_gunshot_clipped_ar15rapid10.wav")
]

for name, fpath in files:
    y, sr = sf.read(fpath)
    if y.ndim > 1: y = np.mean(y, axis=1)
    print(f"\n==================== {name} ====================")
    v7.reset(); res7 = v7.evaluate_waveform(y, sr)
    v8.reset(); res8 = v8.evaluate_waveform(y, sr)
    print(f"V7 events={len(res7['events'])}: {res7['events']}")
    print(f"V8 events={len(res8['events'])}: {res8['events']}")
    
    # Trace windows in V8
    win_size = 15360
    hop_size = 7680
    n_wins = 1 + int((len(y) - win_size) // hop_size) if len(y) >= win_size else 1
    v8.reset()
    for w in range(n_wins):
        win = y[w*hop_size : w*hop_size + win_size] if len(y) >= win_size else np.pad(y, (0, win_size - len(y)))
        t = w * 0.48
        feat, ys, acoustics = v8.extract_features(win)
        crest, flat, hi, mid, lo, m2l, rolloff, cent, rms, peak = acoustics
        mode, _, _ = v8.estimator.update(rolloff, hi, mid, lo, m2l, t, w)
        raw_s = float(v8.fusion_model.predict_proba(feat.reshape(1, -1))[:, 1][0])
        supp7 = v7.suppression.apply_suppression(raw_s, ys, acoustics)
        supp8 = v8.suppression.apply_suppression(raw_s, ys, acoustics)
        st, ev = v8.fsm.step(supp8["adjusted_score"], crest, t, acoustics, mode)
        print(f"  w={w}: raw={raw_s:.4f} | v7_adj={supp7['adjusted_score']:.4f} (cat={supp7['category']}) | v8_adj={supp8['adjusted_score']:.4f} (cat={supp8['category']}) | crest={crest:.2f}dB | m2l={m2l:.3f} | cent={cent:.1f}Hz | mode={mode.value} | st={st}")

