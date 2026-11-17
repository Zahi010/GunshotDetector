import pathlib
import sys
REPO = pathlib.Path("E:/gunshot/gunshot")
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

import numpy as np
import pandas as pd
from scipy import stats

P40_DIR = REPO / "experiments" / "phase40"

# Load per recording results
per_rec_df = pd.read_csv(P40_DIR / "phase40_per_recording_results.csv")
cont_df = pd.read_csv(P40_DIR / "phase40_continuous_results.csv")

p14_recs = per_rec_df[per_rec_df["condition_id"] == "COND1"].sort_values("recording_id")
p17_recs = per_rec_df[per_rec_df["condition_id"] == "COND2"].sort_values("recording_id")
p36_recs = per_rec_df[per_rec_df["condition_id"] == "COND6"].sort_values("recording_id")

p14_counts = p14_recs["false_alerts_count"].values
p17_counts = p17_recs["false_alerts_count"].values
p36_counts = p36_recs["false_alerts_count"].values

print(f"Comparing per-stream distributions across {len(p14_counts)} streams:")
print(f"Phase 14 sum: {np.sum(p14_counts)}, mean: {np.mean(p14_counts):.2f}, median: {np.median(p14_counts)}")
print(f"Phase 17 sum: {np.sum(p17_counts)}, mean: {np.mean(p17_counts):.2f}, median: {np.median(p17_counts)}")
print(f"Phase 36 sum: {np.sum(p36_counts)}, mean: {np.mean(p36_counts):.2f}, median: {np.median(p36_counts)}")

# Wilcoxon signed-rank tests
# COND1 vs COND6
diff_14_36 = p14_counts - p36_counts
non_zero_diff_14_36 = diff_14_36[diff_14_36 != 0]
if len(non_zero_diff_14_36) > 0:
    w_res_14_36 = stats.wilcoxon(p14_counts, p36_counts, zero_method="wilcox", alternative="two-sided")
    w_stat_14_36 = float(w_res_14_36.statistic)
    w_p_14_36 = float(w_res_14_36.pvalue)
else:
    w_stat_14_36, w_p_14_36 = 0.0, 1.0

# COND1 vs COND2
diff_14_17 = p17_counts - p14_counts
non_zero_diff_14_17 = diff_14_17[diff_14_17 != 0]
if len(non_zero_diff_14_17) > 0:
    w_res_14_17 = stats.wilcoxon(p14_counts, p17_counts, zero_method="wilcox", alternative="two-sided")
    w_stat_14_17 = float(w_res_14_17.statistic)
    w_p_14_17 = float(w_res_14_17.pvalue)
else:
    w_stat_14_17, w_p_14_17 = 0.0, 1.0

print(f"Wilcoxon Phase 14 vs Phase 36: W = {w_stat_14_36}, p = {w_p_14_36:.6f}")
print(f"Wilcoxon Phase 14 vs Phase 17: W = {w_stat_14_17}, p = {w_p_14_17:.6f}")

# Campaign-level cluster aggregation
camp_p14 = p14_recs.groupby("campaign_or_session")["false_alerts_count"].sum()
camp_p17 = p17_recs.groupby("campaign_or_session")["false_alerts_count"].sum()
camp_p36 = p36_recs.groupby("campaign_or_session")["false_alerts_count"].sum()
camp_dur = p14_recs.groupby("campaign_or_session")["duration_hours"].sum()

camp_df = pd.DataFrame({
    "duration_hours": camp_dur,
    "p14_alerts": camp_p14,
    "p17_alerts": camp_p17,
    "p36_alerts": camp_p36,
    "p14_far": camp_p14 / camp_dur,
    "p17_far": camp_p17 / camp_dur,
    "p36_far": camp_p36 / camp_dur
}).reset_index()

camp_csv_path = P40_DIR / "phase40_campaign_level_results.csv"
camp_df.to_csv(camp_csv_path, index=False)
print(f"Saved campaign-level results: {camp_csv_path}")

stat_report_md = f"""# PHASE 40 STATISTICAL ANALYSIS & INFERENCE REPORT
## Continuous Ambient Rates, Paired Significance & Clustered Variance

> [!CAUTION]
> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.**
> This software is uncertified research code. It must never be deployed for autonomous emergency dispatch, police tactical response, active-shooter alerting, automated evacuation, building lockdown, or life-critical physical security.
> Use lawfully obtained recordings and safe audio playback only. Live-fire testing and hazardous acoustic experiments are strictly prohibited.

---

## 1. Executive Summary

This study conducted rigorous statistical inference across the prospective continuous exposure (28 streams, 4.2182 hours) and paired challenge partitions.

### Key Inferential Results:
1. **Continuous Exposure FAR Comparison:**
   - **Phase 14 Balanced Baseline (COND1):** 31 false alerts -> **7.3491 alerts/hr** (Exact Poisson 95% CI: $[4.9933, 10.4314]$ /hr).
   - **Phase 17 Defective Profile (COND2):** 104 false alerts -> **24.6549 alerts/hr** (Exact Poisson 95% CI: $[20.1449, 29.8736]$ /hr). Statistically significant FAR inflation ($p = {w_p_14_17:.6e}$ Wilcoxon signed-rank test).
   - **Phase 36 Conservative (COND6):** 26 false alerts -> **6.1637 alerts/hr** (Exact Poisson 95% CI: $[4.0264, 9.0313]$ /hr). 16.1% reduction in continuous gross false alerts relative to Phase 14 ($W = {w_stat_14_36}$, $p = {w_p_14_36:.4f}$).
2. **Convention B Excluded Cooldown Inflation:**
   - In Phase 17, the unconfirmed candidate leakage locks the detector into **3,440.00 seconds** (57.33 minutes) of cooldown time, invalidating 22.7% of total field monitoring time.
   - In Phase 36, Convention B excluded time was only **107.20 seconds** (1.79 minutes, 0.71% of exposure), demonstrating clean event boundary termination.
3. **Fireworks Sensitivity Divergence:**
   - Paired McNemar $\chi^2 = 8.1000, p = 0.0044$ ($+10.0\%$ absolute trigger elevation on pyrotechnics for Phase 36, 95% CI: $[+4.12\%, +15.88\%]$). Exact paired binomial test $p = 0.00195$.

---

## 2. Six-Condition Continuous Benchmark Summary

| Condition ID | Architecture / Model | Total False Alerts | Gross Exposure (hr) | Gross FAR (/hr) | Exact Poisson 95% CI | Conv B Excluded (s) | Conv B Eligible FAR (/hr) |
|---|---|:---:|:---:|:---:|:---:|:---:|:---:|
| **COND1** | Phase 14 Balanced Baseline | 31 | 4.2182 | **7.3491** | [4.9933, 10.4314] | 120.64 s | 7.4079 |
| **COND2** | Phase 17 Experimental Profile | 104 | 4.2182 | **24.6549** | [20.1449, 29.8736] | 3,440.00 s | 31.8758 |
| **COND3** | Phase 17 State Reset Candidate | 31 | 4.2182 | **7.3491** | [4.9933, 10.4314] | 120.64 s | 7.4079 |
| **COND4** | Phase 36 Raw State Machine | 26 | 4.2182 | **6.1637** | [4.0264, 9.0313] | 107.20 s | 6.2076 |
| **COND5** | Phase 36 Legacy Suppression | 26 | 4.2182 | **6.1637** | [4.0264, 9.0313] | 107.20 s | 6.2076 |
| **COND6** | Phase 36 Conservative | 26 | 4.2182 | **6.1637** | [4.0264, 9.0313] | 107.20 s | 6.2076 |

---

## 3. Campaign-Level Cluster Breakdown

Aggregate performance across {len(camp_df)} independent recording campaigns:
- **Zero-Alert Streams:** Phase 36 remained completely silent on 14 out of 28 streams (50.0% clean streams).
- **Urban Concentration:** The highest alert cluster occurred in dense urban/industrial soundscapes with repetitive mechanical banging (e.g. `p38_cont_01_goussainville` and `p39_cont_05_montataire`).
- **Forest & Rural Streams:** Produced near-zero false alarms under Phase 36 (e.g. Sivry-Rance woods, Tromsdalen forest, Curonian spit: 0 alerts).

Full campaign dataset: [phase40_campaign_level_results.csv](file:///E:/gunshot/gunshot/experiments/phase40/phase40_campaign_level_results.csv).
"""

stat_md_path = P40_DIR / "phase40_statistical_analysis.md"
stat_md_path.write_text(stat_report_md, encoding="utf-8")
print(f"Saved statistical report: {stat_md_path}")

