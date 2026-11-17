import sys
import pathlib
import pandas as pd
import soundfile as sf
import numpy as np

sys.path.insert(0, "e:/gunshot/gunshot")
from experiments.detector_improvement_v10.model_detector_improvement_v10 import DetectorImprovementV10

det10 = DetectorImprovementV10()
target = "1-88807-A-39.wav"
manifest_path = "e:/gunshot/gunshot/experiments/phase51_validation/phase51_evaluation_manifest.csv"
df = pd.read_csv(manifest_path)
row = df[df["filename"] == target].iloc[0]
p = pathlib.Path("e:/gunshot/gunshot") / row["filepath"]
audio, sr = sf.read(str(p), dtype="float32")

# Let's inspect step by step
det10.reset()
waveform = audio
dur = float(len(waveform)) / 16000.0
win_size = 15360
hop_size = 7680
n_wins = 1 + int((len(waveform) - win_size) // hop_size)

for w in range(n_wins):
    st = w * hop_size
    en = st + win_size
    win = waveform[st:en]

    feat, ys, acoustics, m_mean = det10.extract_features(win)
    crest, flat, hi, mid, lo, m2l, rolloff, cent, rms, peak = acoustics

    mode, conf, _ = det10.estimator.update(rolloff, hi, mid, lo, m2l, w * 0.48, w)

    raw_score = float(det10.fusion_model.predict_proba(feat.reshape(1, -1))[:, 1][0])

    is_confirmed = (det10.fsm.state == det10.fsm.state.CONFIRMED)
    supp = det10.suppression.apply_suppression(raw_score, ys, acoustics, is_confirmed)
    adj_score = supp["adjusted_score"]

    state, ev = det10.fsm.step(adj_score, crest, w * 0.48, acoustics, mode)
    if ev is not None:
        print(f"Triggered at win {w} (time {w*0.48:.2f}s)! ev={ev}, adj_score={adj_score:.4f}, raw={raw_score:.4f}, supp_cat={supp['category']}")
        break

