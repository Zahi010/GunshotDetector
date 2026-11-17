import sys
import pathlib
import pandas as pd
import soundfile as sf
import numpy as np

sys.path.insert(0, "e:/gunshot/gunshot")
from experiments.detector_improvement_v10.model_detector_improvement_v10 import DetectorImprovementV10

det10 = DetectorImprovementV10()

target = "mitchell_ak47_762_01.wav"
manifest_path = "e:/gunshot/gunshot/experiments/phase51_validation/phase51_evaluation_manifest.csv"
df = pd.read_csv(manifest_path)
row = df[df["filename"] == target].iloc[0]
p = pathlib.Path("e:/gunshot/gunshot") / row["filepath"]
audio, sr = sf.read(str(p), dtype="float32")

dur = float(len(audio)) / 16000.0
print(f"File: {target}, duration={dur:.3f}s, samples={len(audio)}")

# Let's see what evaluate_waveform does
det10.reset()
res = det10.evaluate_waveform(audio, sr)
print("Evaluate waveform result:", res)
print("FSM transitions:", [(t.from_state, t.to_state, t.reason) for t in det10.fsm.history])

