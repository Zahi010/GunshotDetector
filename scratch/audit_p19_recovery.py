import sys, os, pathlib
sys.path.insert(0, os.path.abspath("."))
sys.path.insert(0, os.path.abspath("src"))

import soundfile as sf
import numpy as np
from experiments.detector_improvement_v6.model_detector_improvement_v6 import DetectorImprovementV6
from experiments.detector_improvement_v7.model_detector_improvement_v7 import DetectorImprovementV7

v6 = DetectorImprovementV6()
v7 = DetectorImprovementV7()

p19_dir = pathlib.Path("data/phase19_independent_positive/normalized_16k")
p19_files = sorted(list(p19_dir.glob("*.wav")))

print(f"Auditing all {len(p19_files)} Phase 19 recordings...")
for fpath in p19_files:
    y, sr = sf.read(fpath)
    v6.reset()
    res_v6 = v6.evaluate_waveform(y, sr)
    v7.reset()
    res_v7 = v7.evaluate_waveform(y, sr)
    
    n_v6 = len(res_v6["events"])
    n_v7 = len(res_v7["events"])
    
    if n_v7 > 0 and n_v6 == 0:
        ev7 = res_v7["events"][0]
        print(f"Recovered {fpath.stem}: score={ev7['peak_score']:.4f}, crest={ev7['peak_crest_db']:.2f}dB, mode={ev7['operating_mode']}, type={ev7['trigger_type']}")

