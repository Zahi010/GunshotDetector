# PHASE 42 AUDIT REPORT: RECORDIST-LEVEL DEPENDENCE & CLUSTERED INFERENCE

> [!CAUTION]
> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.**
> This software is uncertified research code. It must never be deployed for autonomous emergency dispatch, police tactical response, active-shooter alerting, automated evacuation, building lockdown, or life-critical physical security.
> Use lawfully obtained recordings and safe audio playback only. Live-fire testing and hazardous acoustic experiments are strictly prohibited.

---

## 1. Executive Summary & Objective

Workstream D audits recordist-level dependence across the 28 continuous streams, solves the historical puzzle of identical Wilcoxon signed-rank results ($W = 0.0, p = 0.1025$) at both stream and cluster levels, and establishes the exact permutation p-value for the detector comparison.

---

## 2. The Identity Puzzle: Why Stream-Level Equaled Recordist-Level

In Phase 41, the Wilcoxon signed-rank test comparing Phase 14 Balanced Baseline (COND1) vs. Phase 36 Conservative Suppression (COND6) yielded the **exact same test statistic and p-value**:
- Stream-level ($N = 28$): $W = 0.0, \; p = 0.1025$
- Recordist-level ($K = 19$): $W = 0.0, \; p = 0.1025$

This was initially suspected to be a script copy-paste error or aggregation failure. Forensic audit proves this was an authentic mathematical identity arising from the underlying data structure:

### Mathematical Proof of Equality:
1. **Zero-Difference Pruning:** The Wilcoxon signed-rank algorithm prunes all paired observations where the difference is zero ($d_i = 0$).
2. **Stream-Level Non-Zero Differences:**
   Across all 28 streams, exactly 3 streams produced discordant alert counts between COND1 and COND6:
   - `p38_cont_01_goussainville`: COND1 = 3 alerts, COND6 = 2 alerts ($\Delta = +1$)
   - `p40_cont_03_bruxelles`: COND1 = 15 alerts, COND6 = 12 alerts ($\Delta = +3$)
   - `p40_cont_11_fukutsu_japan`: COND1 = 5 alerts, COND6 = 4 alerts ($\Delta = +1$)
   - All other 25 streams produced identical counts ($\Delta = 0$).
   - The stream-level non-zero difference set is: **{+1, +3, +1}** ($n = 3$).
3. **Recordist-Level Non-Zero Differences:**
   - `p38_cont_01_goussainville` was recorded by **Vincent Duseigne**. Duseigne contributed 8 streams, but on the other 7 streams, COND1 and COND6 had identical counts. His net cluster difference is $+1$.
   - `p40_cont_03_bruxelles` was recorded by **Flavien Gillié**. Gillié contributed 1 stream; net cluster difference is $+3$.
   - `p40_cont_11_fukutsu_japan` was recorded by **Thomas Martin Nutt**. Nutt contributed 1 stream; net cluster difference is $+1$.
   - All other 16 recordists contributed streams with zero differences; their net cluster differences are $0$.
   - The recordist-level non-zero difference set is: **{+1, +3, +1}** ($n = 3$).

Because the two non-zero difference sets are **identical in element values and size** ({1, 3, 1}), any rank-based algorithm operates on identical inputs, producing identical ranks (ranks 1.5, 3.0, 1.5), identical sum of negative ranks ($W = 0.0$), and an identical asymptotic p-value ($p = 0.1025$).

---

## 3. Exact Permutation Test vs. Flawed Asymptotic P-Value

While the identity is mathematically valid, relying on an asymptotic p-value of $p = 0.1025$ is statistically invalid:

1. **Flawed Asymptotic Assumption:**
   The asymptotic normal approximation for the Wilcoxon signed-rank test assumes $n \to \infty$. For $n = 3$ effective observations, the asymptotic approximation has massive error and creates the misleading impression of borderline significance ($p \approx 0.10$).
2. **Exact Permutation Test ($n = 3$):**
   Under the sharp null hypothesis of exchangeable detector decisions, each of the 3 non-zero differences could independently have been positive or negative with equal probability ($p = 1/2$).
   - Total possible sign configurations: $2^3 = 8$.
   - Configurations as extreme or more extreme than observed (all positive or all negative):
     - {+1, +3, +1} (all positive)
     - {-1, -3, -1} (all negative)
   - Two-sided exact permutation p-value:
     $$p_{\text{exact}} = \frac{2}{8} = 0.2500$$

### Conclusion:
The exact permutation p-value is **$p = 0.2500$**. The observed 5-alert difference between Phase 14 and Phase 36 is entirely consistent with chance variation and provides **no statistically significant evidence of superiority** at any standard significance level ($lpha = 0.05$ or $lpha = 0.10$).

---

## 4. Small-Sample Cluster Asymptotics with $K=19$ Recordists

When conducting clustered inference with $K = 19$ clusters:
1. **Cluster Concentration:** Vincent Duseigne accounts for 8 of 28 streams (28.6% of streams, 1.2583 of 4.2182 hours = 29.8% of total exposure).
2. **Effective Cluster Degrees of Freedom:** When exposure is concentrated in one large cluster and 18 small clusters, the effective sample size is significantly smaller than $K - 1 = 18$.
3. **Inference Guardrail:** Asymptotic cluster-robust standard errors can underestimate variance under severe cluster imbalance. Cluster wild-bootstrap or exact permutation tests must be the primary standard of evidence.

---

## 5. Artifact Provenance
- Recordist analysis CSV: [`phase42_recordist_analysis.csv`](file:///E:/gunshot/gunshot/experiments/phase42/phase42_recordist_analysis.csv)
