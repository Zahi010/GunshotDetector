import sys, os
sys.path.insert(0, os.path.abspath("."))
sys.path.insert(0, os.path.abspath("src"))

import soundfile as sf
import numpy as np
from scratch.test_v8_candidate import DetectorImprovementV8

v8 = DetectorImprovementV8()
fpath = 'data/phase15_independent_eval/gunshots/phase15_gunshot_clipped_ar15rapid09.wav'
y, sr = sf.read(fpath)
if y.ndim > 1: y = np.mean(y, axis=1)
v8.reset()
res = v8.evaluate_waveform(y, sr)
print("v8.evaluate_waveform result:")
print(res)

