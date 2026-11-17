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

# Check Phase 19
p19_dir = pathlib.Path("data/phase19_independent_positive/normalized_16k")
p19_files = sorted(list(p19_dir.glob("*.wav")))
for fpath in p19_files:
    y, sr = sf.read(fpath)
    v7.reset(); res7 = v7.evaluate_waveform(y, sr)
    v8.reset(); res8 = v8.evaluate_waveform(y, sr)
    if res7["detected"] and not res8["detected"]:
        print(f"P19 diff: {fpath.name}")

# Check Phase 15 Positives
p15_manifest = pd.read_csv("reports/phase15_dataset_manifest.csv")
p15_pos = p15_manifest[p15_manifest["ground_truth_label"] == 1]
for _, r in p15_pos.iterrows():
    fpath = r["filepath"]
    y, sr = sf.read(fpath)
    if y.ndim > 1: y = np.mean(y, axis=1)
    v7.reset(); res7 = v7.evaluate_waveform(y, sr)
    v8.reset(); res8 = v8.evaluate_waveform(y, sr)
    if res7["detected"] and not res8["detected"]:
        print(f"P15 diff: {r['recording_id']} ({r['acoustic_condition']})")

