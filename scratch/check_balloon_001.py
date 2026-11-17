import sys
import soundfile as sf
import numpy as np

sys.path.insert(0, "e:/gunshot/gunshot")
from experiments.detector_improvement_v9.model_detector_improvement_v9 import (
    DetectorImprovementV9,
    compute_physical_acoustic_features_v9
)

v9 = DetectorImprovementV9()
fpath = "e:/gunshot/gunshot/data/hard_negatives/hard_neg_balloon_burst_001.wav"
y, sr = sf.read(fpath)
res = v9.evaluate_waveform(y, sr)
print("V9 eval on balloon burst 001:", res)

