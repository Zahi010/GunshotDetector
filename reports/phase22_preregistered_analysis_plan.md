# Phase 22: Preregistered Statistical Analysis Plan (SAP)

> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY..**  
> *This experimental acoustic machine-learning system is not certified and must never be used for autonomous emergency dispatch, police response, active-shooter alerting, automated evacuation, or critical physical security.*  
> *Use legally obtained recordings and safe playback only. No live-fire testing or hazardous acoustic experiments.*

---

## 1. Executive Summary

This Statistical Analysis Plan (SAP) preregisters all mathematical, inferential, and sensitivity evaluation methodologies to be executed in prospective validation trials. 

By defining hypothesis tests, confidence intervals, clustering adjustments, and decision criteria **prior to inspecting prospective test data**, this plan eliminates researcher degrees of freedom, p-hacking, and post-hoc rationalization.

---

## 2. Prespecified Statistical Hypotheses

All model comparisons evaluate the prospective experimental candidate ($M_{\text{exp}}$, e.g. Phase 17 Experimental) against the frozen default production baseline ($M_{\text{base}}$, Phase 14 Balanced).

### 2.1 Primary Incident-Level Hypothesis Test
- **Null Hypothesis ($H_{0, \text{inc}}$):** Marginal incident detection probabilities are identical across candidate models:
  $$P(M_{\text{base}} = 1) = P(M_{\text{exp}} = 1)$$
- **Alternative Hypothesis ($H_{1, \text{inc}}$):** Experimental candidate achieves superior incident detection:
  $$P(M_{\text{exp}} = 1) > P(M_{\text{base}} = 1)$$
- **Test Statistic:** Exact two-sided and one-sided Binomial McNemar Test on discordant recording streams ($b_{\text{stream}}, c_{\text{stream}}$).

### 2.2 Primary False-Alert Hypothesis Test
- **Null Hypothesis ($H_{0, \text{FAR}}$):** The experimental candidate's false-alert rate on continuous negative audio does not exceed that of the baseline by more than an equivalence margin $\delta = 0.5\text{ alerts/hour}$:
  $$\lambda_{\text{exp}} - \lambda_{\text{base}} \le \delta$$
- **Alternative Hypothesis ($H_{1, \text{FAR}}$):** The experimental candidate produces an unacceptably elevated false-alert rate:
  $$\lambda_{\text{exp}} - \lambda_{\text{base}} > \delta$$
- **Test Statistic:** Paired Poisson rate difference test / exact Garwood confidence limits.

---

## 3. Statistical Methodology and Estimators

### 3.1 Interval Estimation for Single Proportions
All detection proportions (round recall, incident recall, stream precision) shall be reported with **Exact Wilson Score 95% Confidence Intervals**:
$$CI_{95\%} = \frac{\hat{p} + \frac{z^2}{2n} \pm z \sqrt{\frac{\hat{p}(1-\hat{p})}{n} + \frac{z^2}{4n^2}}}{1 + \frac{z^2}{n}}$$
where $z = 1.95996$. Wald asymptotic intervals ($\hat{p} \pm z\sqrt{\hat{p}(1-\hat{p})/n}$) are strictly forbidden due to severe undercoverage near boundaries ($p \approx 0$ or $p \approx 1$).

### 3.2 Interval Estimation for Paired Differences
Differences in paired proportions between models evaluated on identical audio streams shall be estimated using **Newcombe Paired Score Intervals**:
$$CI_{95\%}(\Delta) = (\hat{p}_1 - \hat{p}_2) \pm z \cdot \text{SE}_{\text{paired}}$$
$$\text{SE}_{\text{paired}} = \frac{1}{n} \sqrt{b + c - \frac{(b - c)^2}{n}}$$
where $b$ and $c$ are the off-diagonal discordant counts in the paired $2 \times 2$ matrix.

### 3.3 Multiple-Testing Family-Wise Error Rate Control
When $M$ model comparisons are conducted simultaneously against the default baseline (e.g., Phase 14 Balanced vs. Phase 17, Phase 13, Phase 9, High-Precision, High-Sensitivity), **Holm-Bonferroni Step-Down Correction** is mandatory:
1. Sort unadjusted $p$-values: $p_{(1)} \le p_{(2)} \le \dots \le p_{(M)}$.
2. Compare each $p_{(i)}$ against adjusted threshold $\alpha / (M - i + 1)$.
3. Adjusted $p$-value:
   $$p_{\text{Holm}, (i)} = \max_{k \le i} \left( \min(1.0, (M - k + 1) \cdot p_{(k)}) \right)$$
4. A comparison is declared statistically significant if and only if $p_{\text{Holm}, (i)} < 0.05$.

---

## 4. Cluster-Aware Sensitivity Protocols

Because prospective field evaluations involve hierarchical nesting (campaigns $\to$ positions $\to$ sessions $\to$ recordings $\to$ bursts $\to$ rounds), unadjusted event-level tests are treated as **exploratory diagnostics only**.

### 4.1 Leave-One-Campaign-Out (LOCO) Sensitivity Analysis
For prospective trials across $K \ge 3$ campaigns:
- Systematically remove campaign $k \in \{1, \dots, K\}$.
- Re-evaluate incident recall, round recall, and McNemar test statistics across remaining $K-1$ campaigns.
- **Decision Rule:** If statistical significance relies entirely on a single campaign (i.e., significance is lost when that campaign is omitted), the model superiority claim is declared **UNSTABLE AND INCONCLUSIVE**.

### 4.2 Cluster Bootstrap Protocol
- Resample at the highest independent experimental unit available (Campaign or Recording Stream).
- Execute $B = 10,000$ iterations with replacement.
- Report the percentile 95% bootstrap confidence interval on recall difference.
- **Small-Sample Constraint:** If the number of clusters is $K < 15$, bootstrap theory suffers from small-sample distortion. In such cases, bootstrap outputs must be explicitly labeled as **descriptive sensitivity checks**, not definitive population-level inference.

---

## 5. Missing, Ambiguous, and Corrupted Data Handling

1. **Uncertain Ballistic Ground Truth:** If an acoustic impulse cannot be verified against physical logs, laser surveys, or multi-channel microsecond logs, it shall be classified as `AMBIGUOUS_GROUND_TRUTH` and excluded from the primary benchmark.
2. **Recording Dropouts & Missing Samples:** Any recording stream suffering buffer overflow, packet loss, or hardware dropouts exceeding $10\text{ ms}$ shall be quarantined.
3. **Duplicate Files:** Files sharing identical SHA-256 hashes or $>90\%$ Chromaprint acoustic similarity with previously analyzed files shall be identified and evaluated once only. Duplicate entries shall not inflate the sample denominator.

---
*Preregistered protocol certified under Phase 22 Forensic Standard.*
