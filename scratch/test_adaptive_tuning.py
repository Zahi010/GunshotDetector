"""
Test Condition Estimator and Policy Tuning
"""
import sys, os
sys.path.insert(0, "E:/gunshot/gunshot")
os.chdir("E:/gunshot/gunshot")

import soundfile as sf
import numpy as np
import pandas as pd
import pathlib

from experiments.detector_improvement_v5.model_detector_improvement_v5 import (
    DetectorImprovementV5,
    OperatingMode
)

v5 = DetectorImprovementV5(profile="condition_adaptive")

# Test 1: Phase 15 Pocket recordings (18 recordings)
p15_manifest = pd.read_csv("reports/phase15_dataset_manifest.csv")
pocket_recs = p15_manifest[p15_manifest["recording_id"].str.contains("pocket") & (p15_manifest["ground_truth_label"] == 1)]
print(f"Testing {len(pocket_recs)} Phase 15 Pocket recordings...")

pkt_detected = 0
for idx, r in pocket_recs.iterrows():
    fpath = pathlib.Path(r["filepath"])
    y, sr = sf.read(str(fpath))
    res = v5.evaluate_waveform(y, sr)
    if res["detected"]:
        pkt_detected += 1
print(f"Pocket Recall: {pkt_detected} / {len(pocket_recs)} ({pkt_detected / len(pocket_recs) * 100:.1f}%)")

# Test 2: Phase 12 Continuous Stream (first 10 sampled 30s blocks)
p12_cont_path = pathlib.Path("data/phase12_independent_test/continuous_ambient/phase12_continuous_stream_01_urban_and_environmental_2hr.wav")
cont_alerts = 0
if p12_cont_path.exists():
    info = sf.info(str(p12_cont_path))
    sr = info.samplerate
    tot_samples = info.frames
    block_len = 16000 * 30
    tested_blocks = 0
    sample_stride = 10
    with sf.SoundFile(str(p12_cont_path)) as f:
        while f.tell() < tot_samples:
            block = f.read(block_len, dtype='float32')
            if len(block) == 0: break
            if tested_blocks % sample_stride == 0:
                res = v5.evaluate_waveform(block, sr)
                cont_alerts += len(res.get("events", []))
            tested_blocks += 1

print(f"Phase 12 Continuous 2hr stream alerts: {cont_alerts}")

