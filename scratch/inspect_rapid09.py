import sys, os
sys.path.insert(0, os.path.abspath("."))
sys.path.insert(0, os.path.abspath("src"))

import soundfile as sf
import numpy as np
import librosa
from experiments.detector_improvement_v7.model_detector_improvement_v7 import DetectorImprovementV7

v7 = DetectorImprovementV7()
fpath = 'data/phase15_independent_eval/gunshots/phase15_gunshot_clipped_ar15rapid09.wav'
y, sr = sf.read(fpath)
if y.ndim > 1: y = np.mean(y, axis=1)
if sr != 16000: y = librosa.resample(y, orig_sr=sr, target_sr=16000)
y = y.astype(np.float32)

y_proc = np.pad(y, (0, 15360 - len(y)))
feat, ys, acoustics = v7.extract_features(y_proc)
crest, flat, hi, mid, lo, m2l, rolloff, cent, rms, peak = acoustics
raw_s = float(v7.fusion_model.predict_proba(feat.reshape(1, -1))[:, 1][0])
supp7 = v7.suppression.apply_suppression(raw_s, ys, acoustics)

print(f"raw_s: {raw_s:.4f}")
print("acoustics: crest=", crest, "lo=", lo, "m2l=", m2l, "cent=", cent, "peak=", peak)
print("supp7:", supp7)
print("top YAMNet:", sorted([(k, v) for k, v in ys.items() if v > 0.05], key=lambda x: x[1], reverse=True)[:5])
