import sys, os
sys.path.insert(0, os.path.abspath("."))
sys.path.insert(0, os.path.abspath("src"))

import soundfile as sf
import numpy as np
import librosa
from experiments.detector_improvement_v7.model_detector_improvement_v7 import DetectorImprovementV7

v7 = DetectorImprovementV7()
fpath = "data/phase12_independent_test/negatives/phase12_negative_esc50_glass_breaking_3-216284-A-39.wav"
y, sr = sf.read(fpath)
if y.ndim > 1: y = np.mean(y, axis=1)
if sr != 16000: y = librosa.resample(y, orig_sr=sr, target_sr=16000)

win = y[:15360]
feat, ys, acoustics = v7.extract_features(win)
raw_s = float(v7.fusion_model.predict_proba(feat.reshape(1, -1))[:, 1][0])
supp7 = v7.suppression.apply_suppression(raw_s, ys, acoustics)
print(f"w=0: raw={raw_s:.4f}, v7_adj={supp7['adjusted_score']:.4f}, cat={supp7['category']}")

