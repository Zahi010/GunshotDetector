import sys, os
sys.path.insert(0, os.path.abspath("."))
sys.path.insert(0, os.path.abspath("src"))

import soundfile as sf
import numpy as np
import librosa
from experiments.detector_improvement_v6.model_detector_improvement_v6 import DetectorImprovementV6
from experiments.detector_improvement_v7.model_detector_improvement_v7 import DetectorImprovementV7

v6 = DetectorImprovementV6()
v7 = DetectorImprovementV7()
fpath = "data/phase12_independent_test/negatives/phase12_negative_esc50_glass_breaking_3-216284-A-39.wav"
y, sr = sf.read(fpath)
if y.ndim > 1: y = np.mean(y, axis=1)
if sr != 16000: y = librosa.resample(y, orig_sr=sr, target_sr=16000)

win_size = 15360
hop_size = 7680
n_wins = 1 + int((len(y) - win_size) // hop_size)
v6.reset(); res6 = v6.evaluate_waveform(y, 16000)
v7.reset(); res7 = v7.evaluate_waveform(y, 16000)
print(f"Resampled Glass: V6={res6['detected']}, V7={res7['detected']}")
if res7['detected']: print("V7 events:", res7['events'])
if res6['detected']: print("V6 events:", res6['events'])

