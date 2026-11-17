import sys
import soundfile as sf
import numpy as np

sys.path.insert(0, "e:/gunshot/gunshot")
from experiments.detector_improvement_v8.model_detector_improvement_v8 import DetectorImprovementV8
from experiments.detector_improvement_v9.model_detector_improvement_v9 import DetectorImprovementV9

v8 = DetectorImprovementV8()
v9 = DetectorImprovementV9()

fpath = "e:/gunshot/gunshot/data/phase8_final_eval/gunshots/mitchell_mossberg_12g_01.wav"
audio, sr = sf.read(fpath, dtype='float32')

res_v8 = v8.evaluate_waveform(audio, sr)
res_v9 = v9.evaluate_waveform(audio, sr)

print("V8 result:", res_v8)
print("V9 result:", res_v9)

