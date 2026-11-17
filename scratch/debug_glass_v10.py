import sys
import pathlib
import pandas as pd
import soundfile as sf
import numpy as np

sys.path.insert(0, "e:/gunshot/gunshot")
from experiments.detector_improvement_v10.model_detector_improvement_v10 import DetectorImprovementV10

det10 = DetectorImprovementV10()
manifest_path = "e:/gunshot/gunshot/experiments/phase51_validation/phase51_evaluation_manifest.csv"
df = pd.read_csv(manifest_path)
glass_df = df[df["sub_category"] == "esc50_glass_breaking_untouched"]

for idx, row in glass_df.iterrows():
    p = pathlib.Path("e:/gunshot/gunshot") / row["filepath"]
    audio, sr = sf.read(str(p), dtype="float32")
    res = det10.evaluate_waveform(audio, sr)
    if res["detected"]:
        print(f"Triggered: {row['filename']}, peak={res['peak_score']:.4f}, events={res['events']}")

