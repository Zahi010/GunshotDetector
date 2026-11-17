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
pos_df = df[df["ground_truth_label"] == 1]

missed = []
for idx, row in pos_df.iterrows():
    p = pathlib.Path("e:/gunshot/gunshot") / row["filepath"]
    if not p.exists():
        p = pathlib.Path(row["filepath"])
    audio, sr = sf.read(str(p), dtype="float32")
    res = det10.evaluate_waveform(audio, sr)
    if not res["detected"]:
        missed.append({
            "filename": row["filename"],
            "filepath": row["filepath"],
            "sub_category": row.get("sub_category", ""),
            "condition": row.get("condition_category", ""),
            "peak_score": res["peak_score"],
            "dur": res["duration_sec"]
        })

print(f"Total missed by V10: {len(missed)} / {len(pos_df)}")
for m in missed:
    print(f"{m['filename']}: peak={m['peak_score']:.4f}, dur={m['dur']:.2f}s, cond={m['condition']}, sub={m['sub_category']}")

