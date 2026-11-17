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
neg_df = df[df["ground_truth_label"] == 0]

print(f"Total negatives to evaluate: {len(neg_df)}")

results = []
for idx, row in neg_df.iterrows():
    p = pathlib.Path("e:/gunshot/gunshot") / row["filepath"]
    if not p.exists(): p = pathlib.Path(row["filepath"])
    audio, sr = sf.read(str(p), dtype="float32")
    res = det10.evaluate_waveform(audio, sr)
    results.append({
        "filename": row["filename"],
        "sub_category": row.get("sub_category", ""),
        "detected": res["detected"],
        "peak_score": res["peak_score"]
    })

res_df = pd.DataFrame(results)
print(f"Total false alerts on negatives: {res_df['detected'].sum()} / {len(neg_df)} ({res_df['detected'].mean()*100:.2f}%)")

for subcat, g in res_df.groupby("sub_category"):
    fa = g["detected"].sum()
    max_score = g["peak_score"].max()
    print(f"  {subcat:35s} (N={len(g):2d}): {fa} false alerts ({fa/len(g)*100:5.1f}%), max_peak={max_score:.4f}")

