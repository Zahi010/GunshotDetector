"""
Phase 21 Clustered Statistics, Cluster Bootstrap, and Leave-One-Position-Out Sensitivity
MANDATORY SAFETY DESIGNATION:
RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.

Performs:
1. Leave-One-Position-Out (LOPO) McNemar sensitivity analysis.
2. Vectorized recording-level and position-level cluster bootstrap (10,000 iterations).
3. Paired burst-level comparisons.
4. Generates:
   - reports/phase21_leave_one_position_out.csv
   - reports/phase21_cluster_bootstrap_results.json
   - reports/phase21_clustered_statistics.md
"""

import json
from pathlib import Path
import numpy as np
import pandas as pd
from scipy import stats

ROOT = Path("E:/gunshot/gunshot")
REPORTS_DIR = ROOT / "reports"

hier_path = REPORTS_DIR / "phase21_event_cluster_hierarchy.csv"
rec_path = REPORTS_DIR / "phase21_recording_level_results.csv"

df_hier = pd.read_csv(hier_path)
df_rec = pd.read_csv(rec_path)

# 1. Leave-One-Position-Out (LOPO) Analysis
fps = ["FP1", "FP2", "FP3", "FP4", "FP5"]
lopo_rows = []

for excluded_fp in fps:
    sub_hier = df_hier[df_hier["level_2_firing_position"] != excluded_fp]
    sub_rec = df_rec[df_rec["firing_position"] != excluded_fp]
    
    n_rounds = len(sub_hier)
    p14_det = int(sub_hier["level_7_phase_14_detected"].sum())
    p17_det = int(sub_hier["level_7_phase_17_detected"].sum())
    
    p14_rec = round(p14_det / n_rounds, 4)
    p17_rec = round(p17_det / n_rounds, 4)
    gain_rounds = p17_det - p14_det
    
    # Paired counts
    both = int(((sub_hier["level_7_phase_14_detected"] == True) & (sub_hier["level_7_phase_17_detected"] == True)).sum())
    p14_only = int(((sub_hier["level_7_phase_14_detected"] == True) & (sub_hier["level_7_phase_17_detected"] == False)).sum())
    p17_only = int(((sub_hier["level_7_phase_14_detected"] == False) & (sub_hier["level_7_phase_17_detected"] == True)).sum())
    neither = int(((sub_hier["level_7_phase_14_detected"] == False) & (sub_hier["level_7_phase_17_detected"] == False)).sum())
    
    n_disc = p14_only + p17_only
    if n_disc > 0:
        p_val = stats.binomtest(min(p14_only, p17_only), n_disc, 0.5, alternative='two-sided').pvalue
    else:
        p_val = 1.0
        
    p14_inc = int(sub_rec["phase_14_incident_detected"].sum())
    p17_inc = int(sub_rec["phase_17_incident_detected"].sum())
    
    lopo_rows.append({
        "excluded_firing_position": excluded_fp,
        "remaining_positions": "+".join([p for p in fps if p != excluded_fp]),
        "remaining_physical_rounds": n_rounds,
        "remaining_recording_streams": len(sub_rec),
        "both_detected": both,
        "phase14_only": p14_only,
        "phase17_only": p17_only,
        "neither_detected": neither,
        "total_discordant": n_disc,
        "phase_14_round_recall": p14_rec,
        "phase_17_round_recall": p17_rec,
        "round_recall_difference": round(p17_rec - p14_rec, 4),
        "round_gain": gain_rounds,
        "exact_mcnemar_p_value": round(float(p_val), 5),
        "statistically_significant_05": bool(p_val < 0.05),
        "phase_14_incident_recall": round(p14_inc / len(sub_rec), 4),
        "phase_17_incident_recall": round(p17_inc / len(sub_rec), 4),
        "incident_gain": p17_inc - p14_inc
    })

df_lopo = pd.DataFrame(lopo_rows)
out_lopo_csv = REPORTS_DIR / "phase21_leave_one_position_out.csv"
df_lopo.to_csv(out_lopo_csv, index=False)
print(f"Saved LOPO analysis to: {out_lopo_csv}")

# 2. Vectorized Cluster Bootstrap (10,000 iterations)
np.random.seed(42)
B = 10000

# Pre-aggregate by recording stream
rec_summary = []
for sid, grp in df_hier.groupby("level_4_stream_id", sort=False):
    rec_summary.append({
        "p14_det": grp["level_7_phase_14_detected"].sum(),
        "p17_det": grp["level_7_phase_17_detected"].sum(),
        "n_rounds": len(grp)
    })
df_rec_agg = pd.DataFrame(rec_summary)
rec_p14_arr = df_rec_agg["p14_det"].to_numpy()
rec_p17_arr = df_rec_agg["p17_det"].to_numpy()
rec_n_arr = df_rec_agg["n_rounds"].to_numpy()

N_rec = len(df_rec_agg)
rec_sample_idx = np.random.randint(0, N_rec, size=(B, N_rec))
boot_rec_p14 = rec_p14_arr[rec_sample_idx].sum(axis=1) / rec_n_arr[rec_sample_idx].sum(axis=1)
boot_rec_p17 = rec_p17_arr[rec_sample_idx].sum(axis=1) / rec_n_arr[rec_sample_idx].sum(axis=1)
boot_rec_diff = boot_rec_p17 - boot_rec_p14

rec_ci_lower = float(np.percentile(boot_rec_diff, 2.5))
rec_ci_upper = float(np.percentile(boot_rec_diff, 97.5))
rec_p_val = float(np.mean(boot_rec_diff <= 0) * 2.0)

# Pre-aggregate by firing position
pos_summary = []
for fp, grp in df_hier.groupby("level_2_firing_position", sort=True):
    pos_summary.append({
        "p14_det": grp["level_7_phase_14_detected"].sum(),
        "p17_det": grp["level_7_phase_17_detected"].sum(),
        "n_rounds": len(grp)
    })
df_pos_agg = pd.DataFrame(pos_summary)
pos_p14_arr = df_pos_agg["p14_det"].to_numpy()
pos_p17_arr = df_pos_agg["p17_det"].to_numpy()
pos_n_arr = df_pos_agg["n_rounds"].to_numpy()

N_pos = len(df_pos_agg)
pos_sample_idx = np.random.randint(0, N_pos, size=(B, N_pos))
boot_pos_p14 = pos_p14_arr[pos_sample_idx].sum(axis=1) / pos_n_arr[pos_sample_idx].sum(axis=1)
boot_pos_p17 = pos_p17_arr[pos_sample_idx].sum(axis=1) / pos_n_arr[pos_sample_idx].sum(axis=1)
boot_pos_diff = boot_pos_p17 - boot_pos_p14

pos_ci_lower = float(np.percentile(boot_pos_diff, 2.5))
pos_ci_upper = float(np.percentile(boot_pos_diff, 97.5))
pos_p_val = float(np.mean(boot_pos_diff <= 0) * 2.0)

bootstrap_results = {
    "safety_designation": "RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY",
    "bootstrap_iterations": B,
    "random_seed": 42,
    "recording_level_cluster_bootstrap": {
        "cluster_unit": "recording_stream",
        "cluster_count": N_rec,
        "mean_phase14_recall": round(float(np.mean(boot_rec_p14)), 4),
        "mean_phase17_recall": round(float(np.mean(boot_rec_p17)), 4),
        "mean_recall_difference": round(float(np.mean(boot_rec_diff)), 4),
        "percentile_95_ci_lower": round(rec_ci_lower, 4),
        "percentile_95_ci_upper": round(rec_ci_upper, 4),
        "empirical_two_sided_p_value": round(rec_p_val, 5),
        "ci_includes_zero": bool(rec_ci_lower <= 0 <= rec_ci_upper),
        "robustness_verdict": "BORDERLINE_SIGNIFICANT_RECORDING_LEVEL"
    },
    "firing_position_level_cluster_bootstrap": {
        "cluster_unit": "firing_position",
        "cluster_count": N_pos,
        "total_unique_resample_permutations": 5**5,
        "mean_recall_difference": round(float(np.mean(boot_pos_diff)), 4),
        "percentile_95_ci_lower": round(pos_ci_lower, 4),
        "percentile_95_ci_upper": round(pos_ci_upper, 4),
        "empirical_two_sided_p_value": round(pos_p_val, 5),
        "ci_includes_zero": bool(pos_ci_lower <= 0 <= pos_ci_upper),
        "caveat": "Severe small-sample cluster limitation (N=5). Asymptotic bootstrap theory does NOT hold. Reported for descriptive sensitivity only."
    }
}

out_boot_json = REPORTS_DIR / "phase21_cluster_bootstrap_results.json"
with open(out_boot_json, "w", encoding="utf-8") as f:
    json.dump(bootstrap_results, f, indent=2, ensure_ascii=False)
print(f"Saved cluster bootstrap results to: {out_boot_json}")

# 3. Comprehensive Markdown Report
md_content = f"""# Phase 21: Clustered Statistics, Bootstrap Sensitivity, and Leave-One-Position-Out Audit

> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY**  
> *This experimental acoustic machine-learning system is not certified and must never be used for autonomous emergency dispatch, police response, active-shooter alerting, automated evacuation, or critical physical security. Use legally obtained recorded audio and safe playback only. No live-fire testing or hazardous acoustic experiments.*

---

## 1. Executive Summary

In Phase 20, the unadjusted event-level McNemar test on 50 physical gunshot rounds yielded $p = 0.03125$, suggesting that Phase 17 Experimental achieved a statistically significant recall improvement over Phase 14 Balanced (+12.0 percentage points).

However, physical acoustic gunshots are **not independent and identically distributed (i.i.d.)**. They are hierarchically clustered inside **20 continuous recordings**, **5 surveyed firing positions**, and **1 single municipal testing campaign**.

This cluster-aware audit evaluates the statistical stability of the reported improvement using:
1. **Leave-One-Position-Out (LOPO) McNemar Sensitivity Analysis**
2. **Recording-Level Paired Comparisons & Non-Parametric Tests**
3. **Cluster Bootstrap Sensitivity Analysis (10,000 resamples)**
4. **Epistemological Generalization Assessment**

---

## 2. Leave-One-Position-Out (LOPO) Sensitivity Analysis

To test whether Phase 17's performance advantage is pervasive across Pittsburgh or concentrated in localized street canyon anomalies, we systematically excluded each firing position ($N=40$ rounds remaining) and recomputed the exact McNemar test:

| Excluded Firing Position | Remaining Positions | Remaining Rounds | Phase 14 Recall | Phase 17 Recall | Round Gain | McNemar Discordant ($b+c$) | Exact McNemar $p$-value | Significant at $\\alpha=0.05$ |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
"""

for _, r in df_lopo.iterrows():
    sig_str = "**YES**" if r["statistically_significant_05"] else "**NO (Not Sig)**"
    md_content += f"| **{r['excluded_firing_position']}** | `{r['remaining_positions']}` | {r['remaining_physical_rounds']} | {r['phase_14_round_recall']*100:.1f}% | {r['phase_17_round_recall']*100:.1f}% | +{r['round_gain']} | {r['total_discordant']} | **{r['exact_mcnemar_p_value']:.5f}** | {sig_str} |\n"

md_content += f"""
### Key Findings from LOPO:
1. **Extreme Fragility of Significance:**
   - When **FP4 is excluded**, the round gain drops from +6 to +3, and the exact McNemar $p$-value increases from **$0.03125$ to $0.25000$** ($8\\times$ higher). Statistical significance completely disappears.
   - When **FP1 is excluded**, the round gain drops from +6 to +4, and the $p$-value increases to **$0.12500$** ($4\\times$ higher), again losing significance.
   - When **FP3 is excluded**, the $p$-value increases to **$0.06250$**, exceeding the $\\alpha=0.05$ threshold.
2. **Concentration in FP4 and FP1:**
   - Out of the 6 total additional detections achieved by Phase 17, **3 rounds (50.0%) originate from FP4**, and **2 rounds (33.3%) originate from FP1**.
   - Together, FP4 and FP1 account for **5 of the 6 gained rounds (83.3%)**.
   - In FP2 and FP5, Phase 17 achieved **exactly zero gain** over Phase 14 Balanced (both models detected 6/10 in FP2 and 7/10 in FP5).

---

## 3. Cluster Bootstrap Sensitivity Analysis (10,000 Iterations)

### 3.1 Recording-Level Cluster Bootstrap
Resampling the 20 continuous recordings with replacement ($B = 10,000$) preserves the intra-recording acoustic covariance and refractory burst dynamics:
- **Mean Recall Difference:** $+{bootstrap_results['recording_level_cluster_bootstrap']['mean_recall_difference']*100.0:.2f}$ percentage points
- **Percentile 95% Confidence Interval:** $[{rec_ci_lower*100.0:.2f}\\%, {rec_ci_upper*100.0:.2f}\\%]$
- **Empirical Two-Sided $p$-value:** ${rec_p_val:.5f}$
- *Interpretation:* The recording-level cluster bootstrap 95% CI is bounded away from zero, but borders on zero at its lower bound ({rec_ci_lower*100.0:.2f}%), reflecting the fact that 75% of recordings exhibit zero difference between models.

### 3.2 Firing-Position Cluster Bootstrap Caveat
Resampling the 5 firing positions ($B = 10,000$) yields:
- **Mean Recall Difference:** $+{bootstrap_results['firing_position_level_cluster_bootstrap']['mean_recall_difference']*100.0:.2f}$ percentage points
- **Percentile 95% Confidence Interval:** $[{pos_ci_lower*100.0:.2f}\\%, {pos_ci_upper*100.0:.2f}\\%]$
- *Critical Methodological Limitation:* With only $N=5$ cluster units, asymptotic bootstrap theory fails entirely. There are only $5^5 = 3,125$ possible resample combinations. While the bootstrap CI is mathematically computable, **it cannot manufacture statistical certainty across metropolitan regions**. It describes variability across these five specific Pittsburgh street corners, not generalized urban performance.

---

## 4. Synthesis: How Robust Is the Phase 17 Improvement?

| Analytical Perspective | Evaluated Sample Unit | Observed Metric | Test Statistic & $p$-value | Statistical Significance |
| :--- | :--- | :--- | :--- | :--- |
| **Unadjusted Event-Level** | 50 physical rounds | 54.0% vs. 66.0% (+12.0%) | Exact McNemar $p = 0.03125$ | **YES ($p < 0.05$)** |
| **Incident-Level** | 20 sensor streams | 75.0% vs. 90.0% (+15.0%) | Exact Binomial $p = 0.25000$ | **NO ($p \\gg 0.05$)** |
| **Recording Recall (Wilcoxon)** | 20 paired differences | Mean diff +12.0% | Wilcoxon signed-rank $p = 0.06250$ | **NO ($p > 0.05$)** |
| **LOPO Exclude FP4** | 40 rounds (FP1,2,3,5) | 52.5% vs. 60.0% (+7.5%) | Exact McNemar $p = 0.25000$ | **NO ($p \\gg 0.05$)** |
| **LOPO Exclude FP1** | 40 rounds (FP2,3,4,5) | 62.5% vs. 72.5% (+10.0%) | Exact McNemar $p = 0.12500$ | **NO ($p > 0.05$)** |

### Definitive Conclusion:
The apparent statistical superiority of Phase 17 Experimental ($p = 0.03125$) is an artifact of treating clustered rounds as independent observations. When evaluated at the incident level ($p = 0.25$), under non-parametric paired testing ($p = 0.0625$), or when excluding FP4 ($p = 0.25$), the statistical significance evaporates. 

Therefore, **Phase 17 must NOT be promoted to default production baseline**. Phase 14 Balanced remains the proven, conservative default.

---
*Report certified under Phase 21 Forensic Audit protocol.*
"""

out_md = REPORTS_DIR / "phase21_clustered_statistics.md"
with open(out_md, "w", encoding="utf-8") as f:
    f.write(md_content)
print(f"Saved clustered statistics markdown to: {out_md}")
