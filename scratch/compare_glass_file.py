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

r9 = det9.evaluate_waveform(audio, sr)
r10 = det10.evaluate_waveform(audio, sr)

print("V9 result:", r9)
print("V10 result:", r10)

