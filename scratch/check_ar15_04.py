import sys
import soundfile as sf
import numpy as np
import librosa

sys.path.insert(0, "e:/gunshot/gunshot")
from experiments.detector_improvement_v8.model_detector_improvement_v8 import DetectorImprovementV8

v8 = DetectorImprovementV8()
fpath = "e:/gunshot/gunshot/data/phase8_final_eval/gunshots/mitchell_colt_ar15_04.wav"
y, sr = sf.read(fpath)
if y.ndim > 1: y = np.mean(y, axis=1)
if sr != 16000: y = librosa.resample(y, orig_sr=sr, target_sr=16000)
win = y[:15360]
if len(win) < 15360: win = np.pad(win, (0, 15360 - len(win)))

feat, ys, acoustics = v8.extract_features(win)
crest, flat, hi, mid, lo, m2l, rolloff, cent, rms, peak = acoustics

print(f"cent: {cent}, crest: {crest}, m2l: {m2l}, lo: {lo}")
print("YAMNet top 10:")
sorted_ys = sorted(ys.items(), key=lambda x: x[1], reverse=True)[:10]
for k, v in sorted_ys:
    print(f"  Class {k}: {v:.4f}")

raw_score = float(v8.fusion_model.predict_proba(feat.reshape(1, -1))[:, 1][0])
print(f"raw_score: {raw_score}")
supp = v8.suppression.apply_suppression(raw_score, ys, acoustics, False)
print(f"suppression: {supp}")

