import sys
import pathlib
import soundfile as sf
import numpy as np

sys.path.insert(0, "e:/gunshot/gunshot")
from experiments.detector_improvement_v8.model_detector_improvement_v8 import compute_physical_acoustic_features_v8

pos_files = list(pathlib.Path("data/phase19_independent_positive/normalized_16k").glob("*.wav"))
violators = []
for p in pos_files:
    a, sr = sf.read(str(p))
    if a.ndim > 1: a = np.mean(a, axis=1)
    for w in range(0, len(a)-15360, 7680):
        c, fl, hi, mi, lo, m2l, ro, cent, rms, peak = compute_physical_acoustic_features_v8(a[w:w+15360], 16000)
        if cent > 3200.0 and hi > 0.60:
            violators.append((p.name, cent, hi, lo))
print("Phase 19 positives matching cent > 3200 and hi > 0.60:", len(violators))
for v in violators:
    print("Violator:", v)
