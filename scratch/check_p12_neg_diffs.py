import sys, os, pathlib
sys.path.insert(0, os.path.abspath("."))
sys.path.insert(0, os.path.abspath("src"))

import soundfile as sf
import numpy as np
import pandas as pd
from scratch.test_v8_candidate import DetectorImprovementV8
from experiments.detector_improvement_v6.model_detector_improvement_v6 import DetectorImprovementV6
from experiments.detector_improvement_v7.model_detector_improvement_v7 import DetectorImprovementV7

v6 = DetectorImprovementV6()
v7 = DetectorImprovementV7()
v8 = DetectorImprovementV8()

p12_rca = pd.read_csv("experiments/detector_improvement_v4/recording_condition_analysis.csv")
neg_p12 = p12_rca[(p12_rca["dataset_source"] == "phase12_independent") & (p12_rca["ground_truth_gunshot"] == 0)]

print("=== Phase 12 Negatives with False Alarms ===")
for _, r in neg_p12.iterrows():
    fpath = r["filepath"]
    y, sr = sf.read(fpath)
    if y.ndim > 1: y = np.mean(y, axis=1)
    v6.reset(); res6 = v6.evaluate_waveform(y, sr)
    v7.reset(); res7 = v7.evaluate_waveform(y, sr)
    v8.reset(); res8 = v8.evaluate_waveform(y, sr)
    if res6["detected"] or res7["detected"] or res8["detected"]:
        print(f"{r['recording_id']}: V6={int(res6['detected'])}, V7={int(res7['detected'])}, V8={int(res8['detected'])} | cond={r['condition_category']}")

