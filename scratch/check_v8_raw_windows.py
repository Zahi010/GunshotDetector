import sys
import soundfile as sf
import numpy as np
import librosa
import joblib

sys.path.insert(0, "e:/gunshot/gunshot")
from experiments.detector_improvement_v8.model_detector_improvement_v8 import DetectorImprovementV8

v8 = DetectorImprovementV8()
fpath = "e:/gunshot/gunshot/data/phase8_final_eval/gunshots/mitchell_mossberg_12g_04.wav"
y, sr = sf.read(fpath)
if y.ndim > 1: y = np.mean(y, axis=1)
if sr != 16000: y = librosa.resample(y, orig_sr=sr, target_sr=16000)
y = y.astype(np.float32)

win_size = 15360
hop_size = 7680
n_wins = 1 + int((len(y) - win_size) // hop_size)
print(f"Total windows: {n_wins}, y len: {len(y)}")

for w in range(n_wins):
    win = y[w * hop_size : w * hop_size + win_size]
    feat, ys, acoustics = v8.extract_features(win)
    p_xgb = float(v8.xgb_model.predict_proba(v8.extract_features(win)[0][:1].reshape(1, -1) if False else None if False else feat[:4].reshape(1, -1) if False else np.zeros((1, 1024)))[0, 1])
    raw_score = float(v8.fusion_model.predict_proba(feat.reshape(1, -1))[:, 1][0])
    crest, flat, hi, mid, lo, m2l, rolloff, cent, rms, peak = acoustics
    print(f"Window {w}: raw_score={raw_score:.4f}, peak={peak:.4f}, crest={crest:.2f}, lo={lo:.4f}, m2l={m2l:.4f}")

