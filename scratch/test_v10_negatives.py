import sys
import pathlib
import pandas as pd
import soundfile as sf
import numpy as np

sys.path.insert(0, "e:/gunshot/gunshot")
from scratch.test_v10_from_v8 import DetectorImprovementV10

def test_negatives():
    manifest_path = "e:/gunshot/gunshot/experiments/phase51_validation/phase51_evaluation_manifest.csv"
    df = pd.read_csv(manifest_path)

    det10 = DetectorImprovementV10()

    neg_df = df[df["ground_truth_label"] == 0]
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
    total_fa = res_df["detected"].sum()
    print("=" * 70)
    print("V10 NEGATIVE CONTROL EVALUATION (N=308):")
    print(f"Total False Alerts: {total_fa} / {len(neg_df)} ({total_fa/len(neg_df)*100:.2f}%)")
    print("=" * 70)

    for subcat, g in res_df.groupby("sub_category"):
        fa = g["detected"].sum()
        max_score = g["peak_score"].max()
        print(f"  {subcat:35s} (N={len(g):2d}): {fa} false alerts ({fa/len(g)*100:5.1f}%), max_peak={max_score:.4f}")

    res_df.to_csv("e:/gunshot/gunshot/scratch/v10_negatives_results.csv", index=False)

if __name__ == "__main__":
    test_negatives()

