import sys
import soundfile as sf
import numpy as np

sys.path.insert(0, "e:/gunshot/gunshot")
from experiments.detector_improvement_v9.model_detector_improvement_v9 import DetectorImprovementV9

v9 = DetectorImprovementV9()
fpath = "e:/gunshot/gunshot/data/phase8_final_eval/gunshots/mitchell_mossberg_12g_04.wav"
audio, sr = sf.read(fpath, dtype='float32')
res = v9.evaluate_waveform(audio, sr)
print("V9 eval:", res)

