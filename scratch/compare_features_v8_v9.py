import sys
import soundfile as sf
import numpy as np

sys.path.insert(0, "e:/gunshot/gunshot")
from experiments.detector_improvement_v8.model_detector_improvement_v8 import DetectorImprovementV8
from experiments.detector_improvement_v9.model_detector_improvement_v9 import DetectorImprovementV9

v8 = DetectorImprovementV8()
v9 = DetectorImprovementV9()

fpath = "e:/gunshot/gunshot/data/phase8_final_eval/gunshots/mitchell_mossberg_12g_04.wav"
audio, sr = sf.read(fpath, dtype='float32')

win = audio[:15360]
if len(win) < 15360:
    win = np.pad(win, (0, 15360 - len(win)))

feat_v8, ys_v8, ac_v8 = v8.extract_features(win)
feat_v9, ys_v9, ac_v9 = v9.extract_features(win)

print("Feat diff:", np.max(np.abs(feat_v8 - feat_v9)))
print("Acoustics v8:", ac_v8)
print("Acoustics v9:", ac_v9)

score_v8 = float(v8.fusion_model.predict_proba(feat_v8.reshape(1, -1))[:, 1][0])
score_v9 = float(v9.fusion_model.predict_proba(feat_v9.reshape(1, -1))[:, 1][0])
print(f"Raw score v8: {score_v8}, v9: {score_v9}")

res_eval_v8 = v8.evaluate_waveform(audio, sr)
res_eval_v9 = v9.evaluate_waveform(audio, sr)
print(f"Eval v8: {res_eval_v8}")
print(f"Eval v9: {res_eval_v9}")

