import sys, os
sys.path.insert(0, os.path.abspath("."))
sys.path.insert(0, os.path.abspath("src"))

import soundfile as sf
import numpy as np
from experiments.detector_improvement_v7.model_detector_improvement_v7 import DetectorImprovementV7

v7 = DetectorImprovementV7()
fpath = 'data/phase15_independent_eval/gunshots/phase15_gunshot_clipped_ar15rapid09.wav'
y, sr = sf.read(fpath)
if y.ndim > 1: y = np.mean(y, axis=1)
v7.reset()
res = v7.evaluate_waveform(y, sr)
print("v7.evaluate_waveform result:")
print(res)

