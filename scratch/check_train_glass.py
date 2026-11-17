import sys, os
sys.path.insert(0, os.path.abspath("."))
sys.path.insert(0, os.path.abspath("src"))

import soundfile as sf
import numpy as np
from scratch.test_v8_candidate import DetectorImprovementV8
from experiments.detector_improvement_v7.model_detector_improvement_v7 import DetectorImprovementV7

v7 = DetectorImprovementV7()
v8 = DetectorImprovementV8()

files = [
    ("train_115", "data/phase12_independent_test/negatives/phase12_negative_esc50_train_4-165791-B-45.wav"),
    ("glass_120", "data/phase12_independent_test/negatives/phase12_negative_esc50_glass_breaking_3-216284-A-39.wav")
]

for name, fpath in files:
    y, sr = sf.read(fpath)
    if y.ndim > 1: y = np.mean(y, axis=1)
    v7.reset(); res7 = v7.evaluate_waveform(y, sr)
    v8.reset(); res8 = v8.evaluate_waveform(y, sr)
    print(f"\n=== {name} ===")
    print("V7 detected:", res7["detected"], res7["events"])
    print("V8 detected:", res8["detected"], res8["events"])

