# PHASE 41 CONTINUOUS BACKGROUND STATISTICAL ROBUSTNESS REPORT
## Six-Condition Benchmark Reproduction, Clustered Sandwich Variance & Significance Audit

> [!CAUTION]
> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.**
> This software is uncertified research code. It must never be deployed for autonomous emergency dispatch, police tactical response, active-shooter alerting, automated evacuation, building lockdown, or life-critical physical security.
> Use lawfully obtained recordings and safe audio playback only. Live-fire testing and hazardous acoustic experiments are strictly prohibited.

---

## 1. Executive Summary & Audit Objectives

This audit independently reproduced and evaluated the performance of all six detector configurations across the complete prospective continuous ambient dataset (**28 streams, 4.2182 hours**).

Earlier phases reported that the Phase 36 experimental detector achieved a "16.1% reduction in continuous gross false alerts" relative to the Phase 14 baseline (26 vs. 31 alerts). Workstream E conducted a rigorous cluster-robust statistical investigation to determine whether this observed difference represents a statistically significant improvement or is attributable to random sampling noise and clustered recordist variance.

### Authoritative Statistical Conclusions:
1. **The 16.1% Continuous FAR Reduction Is NOT Statistically Significant ($p > 0.05$):**
   - **Stream-Level Wilcoxon Signed-Rank Test:** $W = 0.0$, $p = 0.1025$ (two-sided).
   - **Recordist-Level Clustered Wilcoxon Test:** $W = 0.0$, $p = 0.1025$ (two-sided).
   - **Cluster-Robust Paired Difference Test ($t$-test on sandwich estimator):**
     $$\hat{\Delta} = 1.1853 \text{ alerts/hr}, \quad \text{SE}_{\text{cluster}} = 0.8494 \text{ alerts/hr}, \quad t = 1.3955, \quad p = 0.1799$$
     $$95\% \text{ Clustered CI: } [-0.5992, +2.9699] \text{ alerts/hr}$$
   - **Conclusion:** Across 28 continuous streams, 25 streams showed zero difference between Phase 14 and Phase 36. Only 3 streams showed differences (+1, +3, +1 alert reductions under Phase 36). Because $n = 3$ discordant streams is statistically underpowered, this difference does not meet the standard scientific threshold of $\alpha = 0.05$. Claims of superior background quietness for Phase 36 are unestablished.
2. **Phase 17 Candidate Accumulation Defect Confirmed (`VERIFIED_FROM_PHYSICAL_FILE`):**
   - Under Phase 17 (`COND2`), unconfirmed candidate leakage generates **104 false alerts** ($24.6549$ alerts/hr) and forces the system into **3,440.00 seconds** (57.33 minutes) of Convention B cooldown exclusion (22.7% of monitoring time lost).
   - In contrast, Phase 14 (`COND1`) and Phase 36 (`COND6`) incurred only 120.64 s and 107.20 s of cooldown exclusion, respectively.
   - The Phase 17 defect is statistically confirmed at $p = 0.000634$ (Wilcoxon signed-rank test).
3. **Clustered Variance Impact:**
   - Naïve Poisson standard error estimates underestimate true sampling uncertainty by a factor of $\sim 3.4\times$ to $3.7\times$ (e.g. Phase 14 naïve SE = 1.32 /hr vs. clustered SE = 4.93 /hr).
   - Recordist clustering (where recordist `duseigne` contributed 8 streams, 1.2583 hours) and geographic soundscape heterogeneity (industrial vs. rural) dominate background false alert variance.

---

## 2. Six-Condition Continuous Benchmark Reproduction Table

| Condition ID | Architecture / Model Profile | False Alerts | Gross Exposure | Gross FAR (/hr) | Naïve Poisson SE | Clustered SE | Conv B Excluded (s) | Conv B Eligible FAR (/hr) | Audit Status |
|---|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---|
| **COND1** | Phase 14 Balanced Baseline | 31 | 4.2182 hr | **7.3491** | 1.3199 | 4.9274 | 120.64 s | 7.4079 | `REPRODUCED` |
| **COND2** | Phase 17 Defective Experimental | 104 | 4.2182 hr | **24.6549** | 2.4176 | 12.0357 | 3,440.00 s | 31.8758 | `REPRODUCED` |
| **COND3** | Phase 17 State Reset Candidate | 31 | 4.2182 hr | **7.3491** | 1.3199 | 4.9274 | 120.64 s | 7.4079 | `REPRODUCED` |
| **COND4** | Phase 36 Raw State Machine | 26 | 4.2182 hr | **6.1637** | 1.2088 | 4.1231 | 107.20 s | 6.2076 | `REPRODUCED` |
| **COND5** | Phase 36 Legacy Suppression | 26 | 4.2182 hr | **6.1637** | 1.2088 | 4.1231 | 107.20 s | 6.2076 | `REPRODUCED` |
| **COND6** | Phase 36 Conservative Suppression | 26 | 4.2182 hr | **6.1637** | 1.2088 | 4.1231 | 107.20 s | 6.2076 | `REPRODUCED` |

---

## 3. Mathematical Formulation of Cluster-Robust Variance

### 3.1 Sandwich Estimator for Event Rates
Let $i \in \{1, \dots, N\}$ index the $N = 28$ continuous streams, partitioned into $K = 19$ recordist clusters $k \in \{1, \dots, K\}$.
Let $Y_{k} = \sum_{i \in \text{cluster } k} Y_i$ denote total false alerts in cluster $k$, and $T_k = \sum_{i \in \text{cluster } k} T_i$ denote total duration in cluster $k$.
The overall rate is:
$$\hat{R} = \frac{\sum_{k=1}^K Y_k}{\sum_{k=1}^K T_k} = \frac{Y}{T}$$

Under cluster correlation across streams recorded by the same recordist or equipment rig, the cluster-robust sandwich variance estimator is:
$$\widehat{\text{Var}}_{\text{cluster}}(\hat{R}) = \frac{K}{K - 1} \frac{1}{T^2} \sum_{k=1}^K \left( Y_k - \hat{R} T_k \right)^2$$
$$\text{SE}_{\text{cluster}}(\hat{R}) = \sqrt{\widehat{\text{Var}}_{\text{cluster}}(\hat{R})}$$

### 3.2 Paired Difference Variance
For the paired difference $\hat{\Delta} = \hat{R}_{14} - \hat{R}_{36}$, let $D_k = Y_{14, k} - Y_{36, k}$ denote the cluster-level difference in alerts. The clustered variance is:
$$\widehat{\text{Var}}_{\text{cluster}}(\hat{\Delta}) = \frac{K}{K - 1} \frac{1}{T^2} \sum_{k=1}^K \left( D_k - \hat{\Delta} T_k \right)^2$$
For Phase 14 vs. Phase 36:
- $\hat{\Delta} = \frac{31 - 26}{4.2182} = 1.1853 \text{ alerts/hr}$
- $\text{SE}_{\text{cluster}}(\hat{\Delta}) = 0.8494 \text{ alerts/hr}$
- Degrees of freedom $\nu = K - 1 = 18$
- $t = \frac{1.1853}{0.8494} = 1.3955, \quad p = 0.1799$
- $95\% \text{ Clustered Confidence Interval: } [-0.5992, +2.9699] \text{ alerts/hr}$

---

## 4. Itemized Discordant Stream Analysis (Phase 14 vs. Phase 36)

Across the 28 evaluated streams, exactly 3 streams exhibited alert count discrepancies:

| Stream ID | Recordist / Uploader | Soundscape Description | Duration (s) | Phase 14 Alerts | Phase 36 Alerts | Difference | Acoustic Cause |
|---|---|---|:---:|:---:|:---:|:---:|---|
| `p38_cont_01_goussainville` | `duseigne` | Dense urban / church bells / traffic | 823.10 | 11 | 10 | +1 | Short acoustic clang suppressed by Phase 36 minimum persistence |
| `p39_cont_05_montataire` | `marc_namblard` | Industrial railway / metal scraping | 851.30 | 12 | 9 | +3 | Low-frequency rumble state machine re-triggering avoided in Phase 36 |
| `p40_cont_01_porec` | `udo_noll` | Harbor boat rigging / slap transients | 684.20 | 2 | 1 | +1 | Marginal transient below single-window crest gate |

The remaining 25 streams had identical alert counts between Phase 14 and Phase 36 (including 14 streams with 0 alerts under both detectors).

Full machine-readable outputs:
- Per-stream reconstruction: [phase41_continuous_reconstruction.csv](file:///E:/gunshot/gunshot/experiments/phase41/phase41_continuous_reconstruction.csv)
- Statistical test parameters: [phase41_statistical_reproduction.json](file:///E:/gunshot/gunshot/experiments/phase41/phase41_statistical_reproduction.json)
