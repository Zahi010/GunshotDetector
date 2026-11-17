import sys, os, pathlib
sys.path.insert(0, os.path.abspath("."))
sys.path.insert(0, os.path.abspath("src"))

import soundfile as sf
import numpy as np
import pandas as pd
from experiments.detector_improvement_v6.model_detector_improvement_v6 import DetectorImprovementV6
from experiments.detector_improvement_v7.model_detector_improvement_v7 import DetectorImprovementV7

v6 = DetectorImprovementV6()
v7 = DetectorImprovementV7()

files = [
    "data/phase15_independent_eval/gunshots/phase15_gunshot_clean_berettadouble04.wav",
    "data/phase15_independent_eval/gunshots/phase15_gunshot_clipped_ar15rapid09.wav",
    "data/phase15_independent_eval/gunshots/phase15_gunshot_clipped_ar15rapid10.wav",
    "data/phase15_independent_eval/gunshots/phase15_gunshot_urban_shotspotter_d5_01.wav",
    "data/phase15_independent_eval/gunshots/phase15_gunshot_urban_shotspotter_d5_03.wav"
]

for fpath in files:
    y, sr = sf.read(fpath)
    if y.ndim > 1: y = np.mean(y, axis=1)
    v6.reset()
    res6 = v6.evaluate_waveform(y, sr)
    v7.reset()
    res7 = v7.evaluate_waveform(y, sr)
    print(f"{pathlib.Path(fpath).name}: V6 detected={res6['detected']} (peak={res6['peak_score']:.4f}) | V7 detected={res7['detected']} (peak={res7['peak_score']:.4f})")

