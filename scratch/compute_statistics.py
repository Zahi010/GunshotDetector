import sys
import numpy as np
import scipy.stats as stats
import pandas as pd
import pathlib
import soundfile as sf

sys.path.insert(0, "e:/gunshot/gunshot")
from scratch.run_full_v9_evaluation import DetectorImprovementV9
from experiments.detector_improvement_v10.model_detector_improvement_v10 import DetectorImprovementV10

def wilson_score_interval(k: int, n: int, confidence: float = 0.95) -> tuple[float, float]:
    if n == 0:
        return 0.0, 0.0
    z = stats.norm.ppf(1.0 - (1.0 - confidence) / 2.0)
    p = k / n
    denom = 1.0 + (z**2) / n
    center = (p + (z**2) / (2.0 * n)) / denom
    margin = (z * np.sqrt((p * (1.0 - p) + (z**2) / (4.0 * n)) / n)) / denom
    lower = max(0.0, center - margin)
    upper = min(1.0, center + margin)
    return lower, upper

def compute_detailed_stats():
    manifest_path = "e:/gunshot/gunshot/experiments/phase51_validation/phase51_evaluation_manifest.csv"
    df = pd.read_csv(manifest_path)
    pos_df = df[df["ground_truth_label"] == 1]

    d9 = DetectorImprovementV9()
    d10 = DetectorImprovementV10()

    pairs = []
    for idx, row in pos_df.iterrows():
        p = pathlib.Path("e:/gunshot/gunshot") / row["filepath"]
        if not p.exists(): p = pathlib.Path(row["filepath"])
        audio, sr = sf.read(str(p), dtype="float32")
        r9 = d9.evaluate_waveform(audio, sr)["detected"]
        r10 = d10.evaluate_waveform(audio, sr)["detected"]
        pairs.append((row["filename"], r9, r10))

    # Contingency table
    # a: both 1, b: V9=1 & V10=0, c: V9=0 & V10=1, d: both 0
    a = sum(1 for _, v9, v10 in pairs if v9 and v10)
    b = sum(1 for _, v9, v10 in pairs if v9 and not v10)
    c = sum(1 for _, v9, v10 in pairs if not v9 and v10)
    d = sum(1 for _, v9, v10 in pairs if not v9 and not v10)

    print("Contingency Table on Phase 51 Positives (N=65):")
    print(f"  Both detected (a): {a}")
    print(f"  V9 only (b):       {b}")
    print(f"  V10 only (c):      {c}")
    print(f"  Neither (d):       {d}")

    # McNemar's test with continuity correction
    if b + c > 0:
        stat = (abs(b - c) - 1.0)**2 / (b + c)
        p_val = 1.0 - stats.chi2.cdf(stat, df=1)
        # Exact binomial p-value
        p_val_binom = stats.binomtest(c, b + c, 0.5).pvalue
    else:
        stat, p_val, p_val_binom = 0.0, 1.0, 1.0

    print(f"McNemar chi2={stat:.4f}, p={p_val:.4f}, Exact Binomial p={p_val_binom:.4f}")

    # Wilson intervals
    v9_k = a + b
    v10_k = a + c
    n = len(pos_df)
    w9_l, w9_u = wilson_score_interval(v9_k, n)
    w10_l, w10_u = wilson_score_interval(v10_k, n)

    print(f"V9 Recall:  {v9_k}/{n} ({v9_k/n*100:.2f}%) 95% Wilson CI: [{w9_l*100:.2f}%, {w9_u*100:.2f}%]")
    print(f"V10 Recall: {v10_k}/{n} ({v10_k/n*100:.2f}%) 95% Wilson CI: [{w10_l*100:.2f}%, {w10_u*100:.2f}%]")

    # Phase 19 independent
    w_p19_v9_l, w_p19_v9_u = wilson_score_interval(21, 23)
    w_p19_v10_l, w_p19_v10_u = wilson_score_interval(22, 23)
    print(f"Phase 19 V9:  21/23 ({21/23*100:.2f}%) 95% CI: [{w_p19_v9_l*100:.2f}%, {w_p19_v9_u*100:.2f}%]")
    print(f"Phase 19 V10: 22/23 ({22/23*100:.2f}%) 95% CI: [{w_p19_v10_l*100:.2f}%, {w_p19_v10_u*100:.2f}%]")

    # Phase 15 independent
    w_p15_v9_l, w_p15_v9_u = wilson_score_interval(40, 47)
    w_p15_v10_l, w_p15_v10_u = wilson_score_interval(41, 47)
    print(f"Phase 15 V9:  40/47 ({40/47*100:.2f}%) 95% CI: [{w_p15_v9_l*100:.2f}%, {w_p15_v9_u*100:.2f}%]")
    print(f"Phase 15 V10: 41/47 ({41/47*100:.2f}%) 95% CI: [{w_p15_v10_l*100:.2f}%, {w_p15_v10_u*100:.2f}%]")

    # Save to CSV
    pd.DataFrame([{
        "metric": "Phase 51 Recall",
        "v9_value": f"{v9_k}/{n} ({v9_k/n*100:.2f}%)",
        "v9_ci95": f"[{w9_l*100:.2f}%, {w9_u*100:.2f}%]",
        "v10_value": f"{v10_k}/{n} ({v10_k/n*100:.2f}%)",
        "v10_ci95": f"[{w10_l*100:.2f}%, {w10_u*100:.2f}%]",
        "mcnemar_p": p_val_binom
    }, {
        "metric": "Phase 19 Independent Recall",
        "v9_value": f"21/23 ({21/23*100:.2f}%)",
        "v9_ci95": f"[{w_p19_v9_l*100:.2f}%, {w_p19_v9_u*100:.2f}%]",
        "v10_value": f"22/23 ({22/23*100:.2f}%)",
        "v10_ci95": f"[{w_p19_v10_l*100:.2f}%, {w_p19_v10_u*100:.2f}%]",
        "mcnemar_p": "N/A"
    }, {
        "metric": "Phase 15 Independent Recall",
        "v9_value": f"40/47 ({40/47*100:.2f}%)",
        "v9_ci95": f"[{w_p15_v9_l*100:.2f}%, {w_p15_v9_u*100:.2f}%]",
        "v10_value": f"41/47 ({41/47*100:.2f}%)",
        "v10_ci95": f"[{w_p15_v10_l*100:.2f}%, {w_p15_v10_u*100:.2f}%]",
        "mcnemar_p": "N/A"
    }]).to_csv("e:/gunshot/gunshot/experiments/detector_improvement_v10/statistical_metrics.csv", index=False)

if __name__ == "__main__":
    compute_detailed_stats()

