import sys
import soundfile as sf
import numpy as np
import librosa

sys.path.insert(0, "e:/gunshot/gunshot")
from experiments.detector_improvement_v9.model_detector_improvement_v9 import DetectorImprovementV9

v9 = DetectorImprovementV9()
fpath = "e:/gunshot/gunshot/data/phase8_final_eval/gunshots/mitchell_mossberg_12g_04.wav"
audio, sr = sf.read(fpath, dtype='float32')
if audio.ndim > 1: audio = np.mean(audio, axis=1)
if sr != 16000: audio = librosa.resample(audio, orig_sr=sr, target_sr=16000)

win = audio[:15360]
if len(win) < 15360:
    win = np.pad(win, (0, 15360 - len(win)))

feat, ys, acoustics = v9.extract_features(win)
raw_score = float(v9.fusion_model.predict_proba(feat.reshape(1, -1))[:, 1][0])
print(f"Raw score: {raw_score}")

supp = v9.suppression.apply_suppression(raw_score, ys, acoustics, False)
print(f"Suppressed: {supp['suppressed']}, category: {supp['category']}, adj_score: {supp['adjusted_score']}")

for k in [420, 421, 422, 423, 424, 425, 466]:
    print(f"YAMNet class {k}: {ys.get(k, 0.0)}")

