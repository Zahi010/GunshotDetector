import os
import sys
import time
import numpy as np

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

import config
from model_phase14 import Phase14CandidateGunshotDetector
from model_phase17 import Phase17ExperimentalGunshotDetector

print("Initializing Phase 14 detector...")
t0 = time.time()
d14 = Phase14CandidateGunshotDetector(profile="balanced")
print(f"d14 initialized in {time.time()-t0:.2f}s")

print("Initializing Phase 17 detector...")
t0 = time.time()
d17 = Phase17ExperimentalGunshotDetector(profile="balanced_animal_suppressed")
print(f"d17 initialized in {time.time()-t0:.2f}s")

dummy_wave = np.random.randn(16000 * 10).astype(np.float32) * 0.05
print("Running 10s benchmark on d14...")
t0 = time.time()
res14 = d14.evaluate_waveform(dummy_wave)
print(f"d14 evaluated 10s in {time.time()-t0:.2f}s, events={len(res14.get('events', []))}")

print("Running 10s benchmark on d17...")
t0 = time.time()
res17 = d17.evaluate_waveform(dummy_wave)
print(f"d17 evaluated 10s in {time.time()-t0:.2f}s, events={len(res17.get('events', []))}")
