import sys, os
sys.path.insert(0, os.path.abspath("."))
sys.path.insert(0, os.path.abspath("src"))

import soundfile as sf
import numpy as np
from experiments.detector_improvement_v7.model_detector_improvement_v7 import DetectorImprovementV7

v7 = DetectorImprovementV7()
for f in ["phase15_gunshot_clipped_ar15rapid09.wav", "phase15_gunshot_clipped_ar15rapid10.wav"]:
    p = os.path.join("data/phase15_independent_eval/gunshots", f)
    y, sr = sf.read(p)
    v7.reset()
    res = v7.evaluate_waveform(y, sr)
    print(f"{f}: {len(res['events'])} events")
    for ev in res['events']:
        print(" ", ev)

