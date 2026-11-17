import sys
import pathlib
import pandas as pd
import soundfile as sf
import numpy as np

sys.path.insert(0, "e:/gunshot/gunshot")
from experiments.detector_improvement_v9.model_detector_improvement_v9 import DetectorImprovementV9

det_v9 = DetectorImprovementV9()
manifest_path = "e:/gunshot/gunshot/experiments/phase51_validation/phase51_evaluation_manifest.csv"
df = pd.read_csv(manifest_path)
gunshots = df[df["ground_truth_label"] == 1]

print(f"Evaluating all {len(gunshots)} gunshots with DetectorImprovementV9...")

v9_results = []
for idx, row in gunshots.iterrows():
    p = pathlib.Path("e:/gunshot/gunshot") / row["filepath"]
    if not p.exists():
        p = pathlib.Path(row["filepath"])
    audio, sr = sf.read(str(p), dtype='float32')
    res = det_v9.evaluate_waveform(audio, sr)
    v9_results.append({
        "filename": row["filename"],
        "sub_category": row["sub_category"],
        "condition": row["condition_category"],
        "detected": res["detected"],
        "peak_score": round(res["peak_score"], 4),
        "events": res["event_count"]
    })

res_df = pd.DataFrame(v9_results)
detected_count = res_df["detected"].sum()
print(f"V9 Actual Detections: {detected_count} / {len(gunshots)} ({detected_count / len(gunshots) * 100:.2f}%)")
res_df.to_csv("e:/gunshot/gunshot/scratch/v9_actual_gunshot_detections.csv", index=False)

missed = res_df[~res_df["detected"]]
print(f"True missed count: {len(missed)}")
print(missed[["filename", "condition", "peak_score"]].to_string())
missed.to_csv("e:/gunshot/gunshot/scratch/v9_actual_missed.csv", index=False)

