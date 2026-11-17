import sys
import pathlib
import pandas as pd
import soundfile as sf
import numpy as np

sys.path.insert(0, "e:/gunshot/gunshot")
from experiments.detector_improvement_v9.model_detector_improvement_v9 import DetectorImprovementV9
from experiments.detector_improvement_v10.model_detector_improvement_v10 import DetectorImprovementV10

det9 = DetectorImprovementV9()
det10 = DetectorImprovementV10()

target = "1-88807-A-39.wav"
manifest_path = "e:/gunshot/gunshot/experiments/phase51_validation/phase51_evaluation_manifest.csv"
df = pd.read_csv(manifest_path)
row = df[df["filename"] == target].iloc[0]
p = pathlib.Path("e:/gunshot/gunshot") / row["filepath"]
audio, sr = sf.read(str(p), dtype="float32")

dur = float(len(audio)) / 16000.0
win_size = 15360
hop_size = 7680
n_wins = 1 + int((len(audio) - win_size) // hop_size)

print(f"Target: {target}, {n_wins} windows")
for w in range(n_wins):
    win = audio[w*hop_size : w*hop_size + win_size]
    # V9
    f9, ys9, ac9 = det9.extract_features(win)
    raw9 = float(det9.fusion_model.predict_proba(f9.reshape(1, -1))[:, 1][0])
    supp9 = det9.suppression.apply_suppression(raw9, ys9, ac9, False)
    
    # V10
    f10, ys10, ac10, mm10 = det10.extract_features(win)
    raw10 = float(det10.fusion_model.predict_proba(f10.reshape(1, -1))[:, 1][0])
    supp10 = det10.suppression.apply_suppression(raw10, ys10, ac10, False)
    
    print(f"Win {w}: V9 raw={raw9:.3f}, adj={supp9['adjusted_score']:.3f} (cat={supp9['category']}) | V10 raw={raw10:.3f}, adj={supp10['adjusted_score']:.3f} (cat={supp10['category']})")

