import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import soundfile as sf
import numpy as np

from model_phase14 import Phase14CandidateGunshotDetector
from model_phase17 import Phase17ExperimentalGunshotDetector

print("Loading detectors...")
det14_bal = Phase14CandidateGunshotDetector(profile="balanced")
det17_exp = Phase17ExperimentalGunshotDetector(profile="balanced_animal_suppressed")

test_wav = Path("E:/gunshot/gunshot/data/phase19_independent_positive/normalized_16k/P19-CAT-A-FP1-test_001.wav")
data, sr = sf.read(test_wav)
print(f"Read {test_wav.name}: {len(data)} samples, {sr} Hz, {len(data)/sr}s")

res14 = det14_bal.evaluate_waveform(data)
print(f"Phase 14 Balanced on test_001: detected={res14['detected']}, count={res14['events_count']}")
for ev in res14['events']:
    print("  Event:", ev)

res17 = det17_exp.evaluate_waveform(data)
print(f"Phase 17 Exp on test_001: detected={res17['detected']}, count={res17['events_count']}")
for ev in res17['events']:
    print("  Event:", ev)