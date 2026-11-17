# Phase 21: Clustered Statistics, Bootstrap Sensitivity, and Leave-One-Position-Out Audit

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

| Excluded Firing Position | Remaining Positions | Remaining Rounds | Phase 14 Recall | Phase 17 Recall | Round Gain | McNemar Discordant ($b+c$) | Exact McNemar $p$-value | Significant at $\alpha=0.05$ |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **FP1** | `FP2+FP3+FP4+FP5` | 40 | 62.5% | 72.5% | +4 | 4 | **0.12500** | **NO (Not Sig)** |
| **FP2** | `FP1+FP3+FP4+FP5` | 40 | 52.5% | 67.5% | +6 | 6 | **0.03125** | **YES** |
| **FP3** | `FP1+FP2+FP4+FP5` | 40 | 52.5% | 65.0% | +5 | 5 | **0.06250** | **NO (Not Sig)** |
| **FP4** | `FP1+FP2+FP3+FP5` | 40 | 52.5% | 60.0% | +3 | 3 | **0.25000** | **NO (Not Sig)** |
| **FP5** | `FP1+FP2+FP3+FP4` | 40 | 50.0% | 65.0% | +6 | 6 | **0.03125** | **YES** |

### Key Findings from LOPO:
1. **Extreme Fragility of Significance:**
   - When **FP4 is excluded**, the round gain drops from +6 to +3, and the exact McNemar $p$-value increases from **$0.03125$ to $0.25000$** ($8\times$ higher). Statistical significance completely disappears.
   - When **FP1 is excluded**, the round gain drops from +6 to +4, and the $p$-value increases to **$0.12500$** ($4\times$ higher), again losing significance.
   - When **FP3 is excluded**, the $p$-value increases to **$0.06250$**, exceeding the $\alpha=0.05$ threshold.
2. **Concentration in FP4 and FP1:**
   - Out of the 6 total additional detections achieved by Phase 17, **3 rounds (50.0%) originate from FP4**, and **2 rounds (33.3%) originate from FP1**.
   - Together, FP4 and FP1 account for **5 of the 6 gained rounds (83.3%)**.
   - In FP2 and FP5, Phase 17 achieved **exactly zero gain** over Phase 14 Balanced (both models detected 6/10 in FP2 and 7/10 in FP5).

---

## 3. Cluster Bootstrap Sensitivity Analysis (10,000 Iterations)

### 3.1 Recording-Level Cluster Bootstrap
Resampling the 20 continuous recordings with replacement ($B = 10,000$) preserves the intra-recording acoustic covariance and refractory burst dynamics:
- **Mean Recall Difference:** $+12.16$ percentage points
- **Percentile 95% Confidence Interval:** $[3.70\%, 22.92\%]$
- **Empirical Two-Sided $p$-value:** $0.00580$
- *Interpretation:* The recording-level cluster bootstrap 95% CI is bounded away from zero, but borders on zero at its lower bound (3.70%), reflecting the fact that 75% of recordings exhibit zero difference between models.

### 3.2 Firing-Position Cluster Bootstrap Caveat
Resampling the 5 firing positions ($B = 10,000$) yields:
- **Mean Recall Difference:** $+12.03$ percentage points
- **Percentile 95% Confidence Interval:** $[2.00\%, 22.00\%]$
- *Critical Methodological Limitation:* With only $N=5$ cluster units, asymptotic bootstrap theory fails entirely. There are only $5^5 = 3,125$ possible resample combinations. While the bootstrap CI is mathematically computable, **it cannot manufacture statistical certainty across metropolitan regions**. It describes variability across these five specific Pittsburgh street corners, not generalized urban performance.

---

## 4. Synthesis: How Robust Is the Phase 17 Improvement?

| Analytical Perspective | Evaluated Sample Unit | Observed Metric | Test Statistic & $p$-value | Statistical Significance |
| :--- | :--- | :--- | :--- | :--- |
| **Unadjusted Event-Level** | 50 physical rounds | 54.0% vs. 66.0% (+12.0%) | Exact McNemar $p = 0.03125$ | **YES ($p < 0.05$)** |
| **Incident-Level** | 20 sensor streams | 75.0% vs. 90.0% (+15.0%) | Exact Binomial $p = 0.25000$ | **NO ($p \gg 0.05$)** |
| **Recording Recall (Wilcoxon)** | 20 paired differences | Mean diff +12.0% | Wilcoxon signed-rank $p = 0.06250$ | **NO ($p > 0.05$)** |
| **LOPO Exclude FP4** | 40 rounds (FP1,2,3,5) | 52.5% vs. 60.0% (+7.5%) | Exact McNemar $p = 0.25000$ | **NO ($p \gg 0.05$)** |
| **LOPO Exclude FP1** | 40 rounds (FP2,3,4,5) | 62.5% vs. 72.5% (+10.0%) | Exact McNemar $p = 0.12500$ | **NO ($p > 0.05$)** |

### Definitive Conclusion:
The apparent statistical superiority of Phase 17 Experimental ($p = 0.03125$) is an artifact of treating clustered rounds as independent observations. When evaluated at the incident level ($p = 0.25$), under non-parametric paired testing ($p = 0.0625$), or when excluding FP4 ($p = 0.25$), the statistical significance evaporates. 

Therefore, **Phase 17 must NOT be promoted to default production baseline**. Phase 14 Balanced remains the proven, conservative default.

---
*Report certified under Phase 21 Forensic Audit protocol.*
