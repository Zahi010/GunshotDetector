import os
import sys
sys.path.insert(0, os.path.abspath("."))
sys.path.insert(0, os.path.abspath("src"))

import soundfile as sf
import numpy as np
import json
from experiments.detector_improvement_v6.model_detector_improvement_v6 import (
    DetectorImprovementV6,
    compute_physical_acoustic_features_v6
)

detector = DetectorImprovementV6()
suppressor = detector.suppression

test_files = [
    "data/phase19_independent_positive/normalized_16k/P19-CAT-A-FP1-test_004.wav",
    "data/phase19_independent_positive/normalized_16k/P19-CAT-A-FP1-test_007.wav",
    "data/phase19_independent_positive/normalized_16k/P19-CAT-A-FP4-test_058.wav",
    "data/phase12_independent_test/positives/phase12_gunshot_urban_shotspotter_d7_03.wav",
    "data/phase15_historical_holdout/positives/phase15_gunshot_urban_shotspotter_d5_01.wav"
]

for fpath in test_files:
    y, sr = sf.read(fpath)
    res = detector.evaluate_waveform(y, sr)
    print(f"\nFile: {fpath}")
    print(f"  Detected: {res['detected']}, Events: {res['events']}, Peak: {res['peak_score']:.4f}")
    
    # Analyze window by window
    win_size = 15360
    hop_size = 7680
    n_wins = 1 + int((len(y) - win_size) // hop_size)
    for w in range(n_wins):
        win = y[w*hop_size : w*hop_size + win_size]
        feat, ys, acoustics = detector.extract_features(win)
        raw_s = float(detector.fusion_model.predict_proba(feat.reshape(1, -1))[:, 1][0])
        supp_res = suppressor.apply_suppression(raw_s, ys, acoustics)
        crest, flat, hi, mid, lo, m2l, rolloff, cent, rms, peak = acoustics
        if raw_s > 0.50 or supp_res['adjusted_score'] > 0.20:
            pure_gun = max(ys.get(c, 0.0) for c in [421, 422, 425])
            cap_gun = ys.get(424, 0.0)
            bal_s = max(ys.get(c, 0.0) for c in [420, 421, 422, 424, 425, 428, 434, 460])
            thun_s = max(ys.get(c, 0.0) for c in [280, 281])
            print(f"  Win {w:02d} | raw: {raw_s:.4f} -> adj: {supp_res['adjusted_score']:.4f} | supp: {supp_res['suppressed']} ({supp_res['category']}) | pure_gun: {pure_gun:.3f}, cap: {cap_gun:.3f}, bal: {bal_s:.3f}, thun: {thun_s:.3f} | lo: {lo:.3f}, hi: {hi:.3f}, cent: {cent:.1f} Hz, crest: {crest:.1f} dB")
