"""
Test calibrated ballistic shockwave override:
bal_s >= 0.50 and bal_s >= fw_s * 1.35 and fw_s < 0.75
On Phase 12 fireworks and Phase 19 field gunshots!
"""

import sys, os, pathlib
sys.path.insert(0, "E:/gunshot/gunshot")
import pandas as pd
import soundfile as sf
import numpy as np

from experiments.detector_improvement_v6.model_detector_improvement_v6 import DetectorImprovementV6

detector = DetectorImprovementV6()

# 1. Test Phase 19 files that needed recovery
p19_files = [
    "data/phase19_independent_positive/normalized_16k/P19-CAT-A-FP1-test_004.wav",
    "data/phase19_independent_positive/normalized_16k/P19-CAT-A-FP1-test_007.wav",
    "data/phase19_independent_positive/normalized_16k/P19-CAT-A-FP3-test_049.wav",
    "data/phase19_independent_positive/normalized_16k/P19-CAT-A-FP4-test_058.wav",
    "data/phase19_independent_positive/normalized_16k/P19-CAT-A-FP4-test_061.wav"
]

print("=== Phase 19 Gunshots ===")
for p in p19_files:
    y, sr = sf.read(p)
    win_size = 15360
    hop_size = 7680
    n_wins = 1 + int((len(y) - win_size) // hop_size)
    for w in range(n_wins):
        win = y[w*hop_size : w*hop_size + win_size]
        feat, ys, acoustics = detector.extract_features(win)
        bal_s = max(ys.get(c, 0.0) for c in [420, 421, 422, 424, 425, 428, 434, 460])
        fw_s = max(ys.get(c, 0.0) for c in [426, 427])
        pure_gun = max(ys.get(c, 0.0) for c in [421, 422, 425])
        is_override = (bal_s >= 0.50 and bal_s >= fw_s * 1.30 and fw_s < 0.70)
        if fw_s >= 0.25:
            print(f"  {pathlib.Path(p).name} w={w}: bal={bal_s:.3f}, fw={fw_s:.3f}, pure={pure_gun:.3f} | override={is_override}")

# 2. Test Phase 12 Fireworks
p12_rca = pd.read_csv("experiments/detector_improvement_v4/recording_condition_analysis.csv")
p12_fw = p12_rca[(p12_rca["dataset_source"] == "phase12_independent") & (p12_rca["condition_category"].str.contains("fireworks"))]

print("\n=== Phase 12 Fireworks ===")
for _, r in p12_fw.iterrows():
    y, sr = sf.read(r["filepath"])
    win_size = 15360
    hop_size = 7680
    n_wins = 1 + int((len(y) - win_size) // hop_size)
    for w in range(n_wins):
        win = y[w*hop_size : w*hop_size + win_size]
        feat, ys, acoustics = detector.extract_features(win)
        bal_s = max(ys.get(c, 0.0) for c in [420, 421, 422, 424, 425, 428, 434, 460])
        fw_s = max(ys.get(c, 0.0) for c in [426, 427])
        pure_gun = max(ys.get(c, 0.0) for c in [421, 422, 425])
        is_override = (bal_s >= 0.50 and bal_s >= fw_s * 1.30 and fw_s < 0.70)
        if fw_s >= 0.25:
            print(f"  {r['recording_id']} w={w}: bal={bal_s:.3f}, fw={fw_s:.3f}, pure={pure_gun:.3f} | override={is_override}")

