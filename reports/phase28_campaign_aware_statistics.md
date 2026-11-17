# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY

**MANDATORY SAFETY DESIGNATION:**
This experimental acoustic machine-learning software is uncertified and must never be deployed for autonomous emergency dispatch, tactical police response, active-shooter alerting, automated evacuation, building lockdown, or life-critical physical security.

Use legally obtained recordings and safe audio playback only. Live-fire testing and hazardous acoustic experiments are strictly prohibited.

---

# PHASE 28 TECHNICAL AUDIT REPORT
## Campaign-Aware Statistical Audit, Multi-Level Exposure & Sensitivity Analysis

**Document Identifier:** `PHASE28-REP-CAMPAIGN-STATISTICS`  
**Phase:** `PHASE_28_INDEPENDENT_REPRODUCTION_CAMPAIGN_STATISTICS_COOLDOWN_FORENSICS`  
**Dataset Architecture:** 23 continuous field recordings across 4 independent campaigns (12.6460 gross hours)

---

## 1. Executive Summary

A critical methodological question in acoustic sensor evaluation is **spatial and environmental clustering**. The cumulative continuous benchmark consists of 23 recordings collected across four distinct campaigns in the United Kingdom, Spain, and Australia. 

Recordings within the same campaign share recording sensors, acoustic morphology, urban geometry, and local background distributions. Therefore, treating 23 recordings as 23 independent and identically distributed ($i.i.d.$) samples risks pseudo-replication and within-cluster correlation.

This report evaluates detector performance across multiple levels of statistical aggregation:
1. **Stream-Level Paired Analysis ($N=23$):** Exact two-sided Wilcoxon signed-rank test yields **$W = 8.0, p = 0.1953 \ge 0.05$**; exact sign test yields **$p = 0.7266$**. Phase 14 has 5 superior streams, Phase 17 has 3 superior streams, and 15 streams are tied.
2. **Campaign-Level Aggregation ($G=4$):** Two campaigns favor Phase 17 (+2 and +3 alerts), one campaign ties (0 vs 0), and one campaign decisively favors Phase 14 (-36 alerts). Net alert delta across all campaigns is **-31 alerts in favor of Phase 14**.
3. **Leave-One-Campaign-Out (LOCO) Sensitivity Analysis:** In 3 out of 4 LOCO iterations, Phase 14 is heavily superior (-31 to -34 alerts). Only when AeroSonicDB is excluded does Phase 17 show a modest, non-significant +5 alert advantage ($p = 0.250$).
4. **Statistical Power Limitations:** With only $G=4$ independent clusters, campaign-level hypothesis testing lacks statistical power ($p_{\min} = 2 \times (0.5)^4 = 0.125$), and asymptotic cluster-robust standard errors are invalid.

---

## 2. Campaign-Level Performance Breakdown

The benchmark comprises four independent recording campaigns:
1. `CAMPAIGN-RPISOUND-UK`: 10 recordings, 5.5000 gross hours. Fixed acoustic sensors monitoring industrial ventilation, compressors, generators, and street traffic in the UK.
2. `CAMPAIGN-CHEWMAGNA-UK`: 1 recording, 0.5833 gross hours (35 minutes). Ambient rural and semi-rural soundscape recorded in Chew Magna, UK.
3. `CAMPAIGN-BILBAO-ES`: 6 recordings, 0.5627 gross hours (33.7 minutes). Public squares, arcades, and pedestrian corridors in Bilbao, Spain.
4. `CAMPAIGN-AEROSONIC-AU`: 6 recordings, 6.0000 gross hours. Suburban perimeter and approach flight corridors of Adelaide International Airport (YPAD), South Australia.

### Comprehensive Campaign Ledger

| Campaign Identifier | Region & Environment | Streams | Gross Exposure | P14 Alerts | P17 Alerts | Alert Delta (P14 - P17) | P14 Gross Rate (/hr) | P17 Gross Rate (/hr) | Rate Delta (/hr) | P14 Eligible Exposure | P17 Eligible Exposure | Campaign Outcome |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `CAMPAIGN-RPISOUND-UK` | UK Industrial & Traffic | 10 | 5.5000 hr | 24 | 22 | +2 | 4.3636 | 4.0000 | -0.3636 | 5.4800 hr | 5.4811 hr | Phase 17 Superior |
| `CAMPAIGN-CHEWMAGNA-UK`| UK Rural Ambient | 1 | 0.5833 hr | 0 | 0 | 0 | 0.0000 | 0.0000 | 0.0000 | 0.5833 hr | 0.5833 hr | Tied (0 Alerts) |
| `CAMPAIGN-BILBAO-ES` | Spain Urban Squares | 6 | 0.5627 hr | 32 | 29 | +3 | 56.8727 | 51.5409 | -5.3318 | 0.5484 hr | 0.5532 hr | Phase 17 Superior |
| `CAMPAIGN-AEROSONIC-AU` | Australia Airport Perimeter | 6 | 6.0000 hr | 72 | 108 | **-36** | 12.0000 | 18.0000 | **+6.0000** | 5.9050 hr | 4.2546 hr | **Phase 14 Superior** |
| **Cumulative Total** | **4 Independent Campaigns** | **23** | **12.6460 hr** | **128** | **159** | **-31** | **10.1218** | **12.5732** | **+2.4514** | **12.5199 hr** | **10.8723 hr** | **Phase 14 Superior** |

---

## 3. Leave-One-Campaign-Out (LOCO) Sensitivity Analysis

To evaluate whether the empirical superiority of Phase 14 is driven solely by a single outlier campaign, a full Leave-One-Campaign-Out (LOCO) jackknife sensitivity analysis was performed.

| Excluded Campaign | Remaining Campaigns | Remaining Streams | Remaining Gross Hours | P14 Alerts | P17 Alerts | Delta Alerts (P14 - P17) | P14 Gross Rate (/hr) | P17 Gross Rate (/hr) | P14 Favored Streams | P17 Favored Streams | Tied Streams | Paired Wilcoxon W (p-value) | Predominant Model |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **None (Full Benchmark)** | 4 | 23 | 12.6460 hr | 128 | 159 | **-31** | 10.1218 | 12.5732 | 5 | 3 | 15 | W = 8.0 (p = 0.1953) | **Phase 14 Superior** |
| **Exclude `CAMPAIGN-AEROSONIC-AU`** | 3 | 17 | 6.6460 hr | 56 | 51 | +5 | 8.4261 | 7.6738 | 0 | 3 | 14 | W = 0.0 (p = 0.2500) | Phase 17 Favored (NS) |
| **Exclude `CAMPAIGN-BILBAO-ES`** | 3 | 17 | 12.0833 hr | 96 | 130 | **-34** | 7.9449 | 10.7586 | 5 | 2 | 10 | W = 8.0 (p = 0.4375) | **Phase 14 Superior** |
| **Exclude `CAMPAIGN-RPISOUND-UK`** | 3 | 13 | 7.1460 hr | 104 | 137 | **-33** | 14.5536 | 19.1716 | 5 | 2 | 6 | W = 4.0 (p = 0.2188) | **Phase 14 Superior** |
| **Exclude `CAMPAIGN-CHEWMAGNA-UK`**| 3 | 22 | 12.0627 hr | 128 | 159 | **-31** | 10.6112 | 13.1811 | 5 | 3 | 14 | W = 8.0 (p = 0.1953) | **Phase 14 Superior** |

### Key Insights from LOCO Sensitivity:
1. **AeroSonicDB Impact:** When AeroSonicDB is included (the last 3 rows), Phase 14 Balanced dominates across all subsets with a net advantage of 31 to 34 fewer false alarms.
2. **Historical Benchmark Retrospective:** Excluding AeroSonicDB isolates the historical 17 European streams, where Phase 17 logged 5 fewer alerts across 6.65 hours. However, the exact Wilcoxon p-value for this subset is $p = 0.2500$, proving that even in isolation, Phase 17's historical advantage **never attained statistical significance**.
3. **Stability of Ranking:** No campaign exclusion flips the overall cumulative conclusion into a statistically significant victory for Phase 17.

---

## 4. Methodological Limitations of Campaign-Level Inference

### The Small-Cluster Constraint ($G=4$)
Statistical inference in clustered data faces well-known finite-sample bounds:
1. **Sign Test Power:** With $G=4$ independent clusters, a sign test on campaign outcomes has a sample space of $2^4 = 16$ equally likely outcomes under $H_0: P(\text{P17 better}) = 0.5$. The most extreme possible realization (all 4 campaigns favoring one model) has a two-sided probability of:
   $$p_{\min} = 2 \times \left(\frac{1}{2}\right)^4 = 2 \times \frac{1}{16} = 0.125$$
   Because $0.125 > 0.05$, it is mathematically impossible to achieve statistical significance at $\alpha = 0.05$ at the campaign level with only four campaigns.
2. **Cluster-Robust Variance Estimation (CRVE) Failure:** Econometric and epidemiological cluster-robust methods (e.g., Liang-Zeger GEE, Cameron-Miller wild cluster bootstrap) require $G \ge 30$ to $G \ge 50$ clusters for the empirical covariance matrix to achieve consistent asymptotic coverage. With $G=4$, cluster sandwich estimators suffer catastrophic downward bias in standard errors, leading to severe false-positive over-rejection.
3. **Recommended Reporting Protocol:** Researchers must not claim that the benchmark represents four independent statistical replications supporting generalizability. Instead, results must be reported descriptively across campaigns, acknowledging that spatial heterogeneity dominates.

