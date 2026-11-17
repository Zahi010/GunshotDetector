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
p12_all = p12_rca[p12_rca["dataset_source"] == "phase12_independent"]

pos_p12 = p12_all[p12_all["ground_truth_gunshot"] == 1]
neg_p12 = p12_all[p12_all["ground_truth_gunshot"] == 0]

print(f"Phase 12 Discrete: {len(pos_p12)} Positives, {len(neg_p12)} Negatives")

v6_pos_hits, v7_pos_hits, v8_pos_hits = 0, 0, 0
for _, r in pos_p12.iterrows():
    fpath = r["filepath"]
    y, sr = sf.read(fpath)
    if y.ndim > 1: y = np.mean(y, axis=1)
    v6.reset(); res6 = v6.evaluate_waveform(y, sr)
    v7.reset(); res7 = v7.evaluate_waveform(y, sr)
    v8.reset(); res8 = v8.evaluate_waveform(y, sr)
    if res6["detected"]: v6_pos_hits += 1
    if res7["detected"]: v7_pos_hits += 1
    if res8["detected"]: v8_pos_hits += 1

print(f"Phase 12 Positive Recall:")
print(f"  V6: {v6_pos_hits}/{len(pos_p12)} ({v6_pos_hits/len(pos_p12)*100:.2f}%)")
print(f"  V7: {v7_pos_hits}/{len(pos_p12)} ({v7_pos_hits/len(pos_p12)*100:.2f}%)")
print(f"  V8: {v8_pos_hits}/{len(pos_p12)} ({v8_pos_hits/len(pos_p12)*100:.2f}%)")

v6_neg_fps, v7_neg_fps, v8_neg_fps = 0, 0, 0
for _, r in neg_p12.iterrows():
    fpath = r["filepath"]
    y, sr = sf.read(fpath)
    if y.ndim > 1: y = np.mean(y, axis=1)
    v6.reset(); res6 = v6.evaluate_waveform(y, sr)
    v7.reset(); res7 = v7.evaluate_waveform(y, sr)
    v8.reset(); res8 = v8.evaluate_waveform(y, sr)
    if res6["detected"]: v6_neg_fps += 1
    if res7["detected"]: v7_neg_fps += 1
    if res8["detected"]: v8_neg_fps += 1

print(f"\nPhase 12 Negative False Positives:")
print(f"  V6: {v6_neg_fps}/{len(neg_p12)} ({v6_neg_fps/len(neg_p12)*100:.2f}%)")
print(f"  V7: {v7_neg_fps}/{len(neg_p12)} ({v7_neg_fps/len(neg_p12)*100:.2f}%)")
print(f"  V8: {v8_neg_fps}/{len(neg_p12)} ({v8_neg_fps/len(neg_p12)*100:.2f}%)")

