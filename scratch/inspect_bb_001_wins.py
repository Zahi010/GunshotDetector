import sys
import soundfile as sf
import numpy as np
import librosa

sys.path.insert(0, "e:/gunshot/gunshot")
from experiments.detector_improvement_v9.model_detector_improvement_v9 import (
    DetectorImprovementV9,
    compute_physical_acoustic_features_v9
)

v9 = DetectorImprovementV9()
fpath = "e:/gunshot/gunshot/data/background/hard_negatives/balloon_burst/hard_neg_balloon_burst_001.wav"
y, sr = sf.read(fpath)
if y.ndim > 1: y = np.mean(y, axis=1)
if sr != 16000: y = librosa.resample(y, orig_sr=sr, target_sr=16000)

win_size = 15360
hop_size = 7680
n_wins = 1 + int((len(y) - win_size) // hop_size)
print(f"Total windows: {n_wins}")

for w in range(n_wins):
    win = y[w * hop_size : w * hop_size + win_size]
    feat, ys, acoustics = v9.extract_features(win)
    crest, flat, hi, mid, lo, m2l, rolloff, cent, rms, peak = acoustics
    raw_score = float(v9.fusion_model.predict_proba(feat.reshape(1, -1))[:, 1][0])
    supp = v9.suppression.apply_suppression(raw_score, ys, acoustics, False)
    print(f"Win {w}: peak={peak:.4f}, crest={crest:.2f}, cent={cent:.1f}, hi={hi:.4f}, lo={lo:.4f}, pure_gun={ys.get(421, 0.0):.4f}")
    print(f"       raw={raw_score:.4f}, adj={supp['adjusted_score']:.4f}, supp={supp['suppressed']} ({supp['category']})")

