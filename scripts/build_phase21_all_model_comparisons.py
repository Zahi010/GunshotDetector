"""
Phase 21 All Model Comparisons with Multiple-Comparison Corrections
MANDATORY SAFETY DESIGNATION:
RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.

Calculates paired contingency tables, exact two-sided McNemar p-values,
Holm-Bonferroni multiple testing adjustments, Newcombe paired score intervals,
and recording-level sensitivity tests across all 5 model comparisons against Phase 14 Balanced.
Outputs reports/phase21_all_model_comparisons.csv.
"""

from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path("E:/gunshot/gunshot")
REPORTS_DIR = ROOT / "reports"

hier_path = REPORTS_DIR / "phase21_event_cluster_hierarchy.csv"
rec_path = REPORTS_DIR / "phase21_recording_level_results.csv"
manifest_path = REPORTS_DIR / "phase20_canonical_event_manifest.csv"

df = pd.read_csv(manifest_path)
cat_a = df[df["category"] == "CATEGORY_A_NATURAL_CONTINUOUS"].copy()
assert len(cat_a) == 50

# Define paired models to compare against Phase 14 Balanced
comparisons = [
    ("Phase 14 Balanced vs Phase 17 Experimental", "phase_14_balanced", "phase_17_experimental"),
    ("Phase 14 Balanced vs Phase 9 Balanced", "phase_14_balanced", "phase_9_balanced"),
    ("Phase 14 Balanced vs Phase 13 Balanced", "phase_14_balanced", "phase_13_balanced"),
    ("Phase 14 Balanced vs Phase 14 High-Precision", "phase_14_balanced", "phase_14_hp"),
    ("Phase 14 Balanced vs Phase 14 High-Sensitivity", "phase_14_balanced", "phase_14_hs")
]

# Function for Newcombe paired score interval for difference of proportions
def paired_diff_ci(a, b, c, d, alpha=0.05):
    n = a + b + c + d
    p1 = (a + b) / n
    p2 = (a + c) / n
    diff = p2 - p1
    z = stats.norm.ppf(1 - alpha / 2)
    # Variance of paired difference: (b + c - (b - c)^2 / n) / n^2
    var_diff = (b + c - ((b - c) ** 2) / n) / (n ** 2)
    se = np.sqrt(max(0.0, var_diff))
    ci_lower = diff - z * se
    ci_upper = diff + z * se
    return round(float(diff * 100.0), 2), round(float(ci_lower * 100.0), 2), round(float(ci_upper * 100.0), 2)

comp_rows = []

for label, col_a, col_b in comparisons:
    s_a = cat_a[f"{col_a}_detected"] == True
    s_b = cat_a[f"{col_b}_detected"] == True
    
    a = int(((s_a == True) & (s_b == True)).sum())
    b = int(((s_a == True) & (s_b == False)).sum())
    c = int(((s_a == False) & (s_b == True)).sum())
    d = int(((s_a == False) & (s_b == False)).sum())
    
    n_disc = b + c
    if n_disc > 0:
        p_val = stats.binomtest(min(b, c), n_disc, 0.5, alternative='two-sided').pvalue
    else:
        p_val = 1.0
        
    diff_pp, ci_low, ci_high = paired_diff_ci(a, b, c, d)
    
    # Recording-level paired test
    rec_a = cat_a.groupby("stream_id")[f"{col_a}_detected"].mean()
    rec_b = cat_a.groupby("stream_id")[f"{col_b}_detected"].mean()
    rec_diff = rec_b - rec_a
    mean_rec_diff_pp = round(float(rec_diff.mean() * 100.0), 2)
    
    non_zero_diff = rec_diff[rec_diff != 0]
    if len(non_zero_diff) > 0:
        try:
            w_pval = stats.wilcoxon(non_zero_diff).pvalue
        except Exception:
            w_pval = 1.0
    else:
        w_pval = 1.0
        
    # Position level gain range
    pos_a = cat_a.groupby("firing_position")[f"{col_a}_detected"].sum()
    pos_b = cat_a.groupby("firing_position")[f"{col_b}_detected"].sum()
    pos_gains = pos_b - pos_a
    min_gain = int(pos_gains.min())
    max_gain = int(pos_gains.max())
    pos_gain_str = f"[{min_gain:+d} to {max_gain:+d}]"
    
    comp_rows.append({
        "comparison": label,
        "model_a": col_a,
        "model_b": col_b,
        "both_detected": a,
        "model_a_only": b,
        "model_b_only": c,
        "neither_detected": d,
        "total_discordant": n_disc,
        "unadjusted_exact_mcnemar_p_value": float(p_val),
        "absolute_recall_difference_pp": diff_pp,
        "paired_diff_95_ci_lower_pp": ci_low,
        "paired_diff_95_ci_upper_pp": ci_high,
        "recording_level_mean_diff_pp": mean_rec_diff_pp,
        "recording_level_wilcoxon_p_value": round(float(w_pval), 5),
        "position_level_gain_range": pos_gain_str
    })

df_all_comp = pd.DataFrame(comp_rows)

# Holm-Bonferroni adjustment across the 5 comparisons
# Sort by unadjusted p-value ascending
df_all_comp = df_all_comp.sort_values("unadjusted_exact_mcnemar_p_value").reset_index(drop=True)
m = len(df_all_comp)

holm_pvals = []
for i, r in df_all_comp.iterrows():
    raw_p = r["unadjusted_exact_mcnemar_p_value"]
    multiplier = m - i
    adj_p = min(1.0, raw_p * multiplier)
    holm_pvals.append(adj_p)

# Enforce monotonicity: p_adj[i] = max(p_adj[i], p_adj[i-1])
for i in range(1, m):
    holm_pvals[i] = max(holm_pvals[i], holm_pvals[i-1])

df_all_comp["holm_adjusted_p_value"] = [round(x, 5) for x in holm_pvals]
df_all_comp["statistically_significant_unadjusted_05"] = df_all_comp["unadjusted_exact_mcnemar_p_value"] < 0.05
df_all_comp["statistically_significant_holm_05"] = df_all_comp["holm_adjusted_p_value"] < 0.05

# Round unadjusted p-value
df_all_comp["unadjusted_exact_mcnemar_p_value"] = df_all_comp["unadjusted_exact_mcnemar_p_value"].apply(lambda x: round(float(x), 5))

out_csv = REPORTS_DIR / "phase21_all_model_comparisons.csv"
df_all_comp.to_csv(out_csv, index=False)
print(f"Saved all model comparisons to: {out_csv}")
print(df_all_comp[["comparison", "total_discordant", "unadjusted_exact_mcnemar_p_value", "holm_adjusted_p_value", "statistically_significant_holm_05"]].to_string())

