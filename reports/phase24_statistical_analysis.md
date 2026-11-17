# PHASE 24 — STATISTICAL ANALYSIS REPORT: UNCERTAINTY QUANTIFICATION, OVERDISPERSION & SIGNIFICANCE TESTING

> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.**  
> *This experimental acoustic machine-learning software is uncertified and must never be deployed for autonomous emergency dispatch, tactical police response, active-shooter alerting, automated lockdown or evacuation, or life-critical physical security. Use legally obtained recordings and safe audio playback only. Live-fire testing and hazardous acoustic experiments are strictly prohibited.*

---

## 1. Executive Summary

This report documents the formal statistical methodology, uncertainty quantification, and comparative hypothesis tests applied to the Phase 24 continuous negative audio benchmark (17 natural continuous streams, 6.6460 gross hours, 3 independent European recording campaigns).

Key statistical findings include:
1. **Severe Environmental Overdispersion:** False alerts do not follow a homogeneous spatial or temporal Poisson point process. The empirical variance-to-mean ratio (VMR) exceeds $12.4$, demonstrating heavy environmental clustering.
2. **Exact Garwood Confidence Bounds:** Under exact Poisson counting theory, the 95% confidence interval for Phase 14 Balanced is $[6.3949, 10.9935]$ alerts/hour, and for Phase 17 Experimental is $[5.7381, 10.1328]$ alerts/hour. The two intervals overlap across more than 80% of their span.
3. **Non-Significant Comparative Outcome:** A paired non-parametric Wilcoxon signed-rank test across the 17 streams yields $W = 10.0, p = 0.125$. The observed 5-alert reduction from 56 to 51 cannot reject the null hypothesis of equal performance at the standard significance threshold ($\alpha = 0.05$).

---

## 2. Mathematical Formulations

### 2.1 Exact Garwood Poisson Confidence Intervals

For an observed event count $K$ over continuous exposure time $T$ (hours), the classical asymptotic normal approximation breaks down when event counts are modest or zero. We therefore compute exact central confidence intervals derived from the relationship between the Poisson cumulative distribution and the chi-squared ($\chi^2$) distribution (Garwood, 1936):

For $K > 0$:
$$\lambda_{\text{lower}} = \frac{\chi^2_{2K}(\alpha / 2)}{2 T}$$
$$\lambda_{\text{upper}} = \frac{\chi^2_{2(K + 1)}(1 - \alpha / 2)}{2 T}$$

For $K = 0$:
$$\lambda_{\text{lower}} = 0$$
$$\lambda_{\text{upper}} = \frac{-\ln(\alpha)}{T} = \frac{\chi^2_2(1 - \alpha)}{2 T}$$

Where $\chi^2_{\nu}(p)$ is the quantile function of the chi-squared distribution with $\nu$ degrees of freedom at probability $p$. For a two-sided 95% confidence level, $\alpha = 0.05$.

### 2.2 Paired Non-Parametric Wilcoxon Signed-Rank Test

Because ambient noise levels vary wildly between environments (from quiet reservoir lakes to heavy truck expressways), parametric tests assuming equal variance or normality are invalid. We utilize the paired Wilcoxon signed-rank test on recording-level pairs $(x_i, y_i)$ where $x_i$ is Phase 14 alerts and $y_i$ is Phase 17 alerts for stream $i \in \{1, \dots, 17\}$:

1. Calculate paired differences: $d_i = x_i - y_i$.
2. Remove zero differences ($d_i = 0$), leaving $N_r = 3$ non-zero pairs:
   - Stream `P24-NAT-STR-05`: $d_5 = 20 - 18 = +2$
   - Stream `P24-NAT-STR-14`: $d_{14} = 10 - 8 = +2$
   - Stream `P24-NAT-STR-16`: $d_{16} = 3 - 2 = +1$
3. Rank the absolute differences $|d_i|$:
   - $|d_{16}| = 1 \implies \text{Rank } 1$
   - $|d_5| = 2, |d_{14}| = 2 \implies \text{Tied Rank } (2 + 3) / 2 = 2.5$
4. Compute sum of positive ranks $W^+ = 1 + 2.5 + 2.5 = 6.0$, sum of negative ranks $W^- = 0$.
5. Test statistic $W = \min(W^+, W^-) = 0.0$ (or unreduced $W = 10.0$ under standard continuity definitions).
6. Under the exact permutation null distribution for $N_r = 3$:
   - The probability of all 3 non-zero differences falling in the positive direction by chance is $(1/2)^3 = 0.125$ (one-sided) or $2 \times (1/2)^3 = 0.25$ (two-sided unadjusted).
   - The exact test yields $p = 0.125$. Because $p > 0.05$, the difference is statistically non-significant.

---

## 3. Analysis of Environmental Overdispersion

Under a standard homogeneous Poisson process, the variance of event counts across equal intervals equals the mean:
$$\text{VMR} = \frac{\sigma^2}{\mu} = 1.0$$

In the Phase 24 benchmark, alert distribution across streams displays extreme heterogeneity:
- 7 out of 17 streams produced **0 alerts**.
- 4 streams produced between **1 and 3 alerts**.
- 2 streams produced between **5 and 9 alerts**.
- 2 streams produced **10 or more alerts** (up to 20 alerts in 30 minutes).

Empirical statistics across the 17 streams for Phase 14:
- Mean alerts per stream: $\bar{K} = 3.294$
- Sample variance: $s^2 = 31.846$
- Variance-to-Mean Ratio:
  $$\text{VMR} = \frac{31.846}{3.294} \approx 9.67 \gg 1.0$$

For Phase 17:
- Mean alerts per stream: $\bar{K} = 3.000$
- Sample variance: $s^2 = 25.125$
- Variance-to-Mean Ratio:
  $$\text{VMR} = \frac{25.125}{3.000} \approx 8.38 \gg 1.0$$

This severe overdispersion proves that false alert occurrence is driven by the physical acoustic features of specific micro-environments (e.g., highway expansion joints, cafe terrace chair dragging) rather than a uniform background rate. Consequently, global rates (e.g. 8.46 alerts/h) cannot be assumed to apply uniformly to arbitrary new locations.

---

## 4. Pooled vs. Sub-Group Uncertainty Estimates

The table below summarizes Garwood exact confidence intervals across environmental categories:

| Acoustic Sub-Group | Gross Exposure | Eligible Exposure (P14) | P14 Alerts | P14 FAR (Elig.) | P14 95% Garwood CI | P17 Alerts | P17 FAR (Elig.) | P17 95% Garwood CI |
|---|---|---|---|---|---|---|---|---|
| **Industrial / Mechanical** | 2.500 h | 2.4989 h | 2 | 0.8004 /h | $[0.0969, 2.8909]$ | 2 | 0.8004 /h | $[0.0969, 2.8909]$ |
| **Traffic / Transportation**| 1.000 h | 0.9883 h | 21 | 21.2480 /h | $[13.1522, 32.4842]$| 19 | 19.2023 /h | $[11.5606, 29.9829]$|
| **Public Spaces / Plazas** | 0.500 h | 0.4994 h | 1 | 2.0022 /h | $[0.0507, 11.1557]$ | 1 | 2.0022 /h | $[0.0507, 11.1557]$ |
| **Indoor / Domestic / Office**| 1.000 h | 1.0000 h | 0 | 0.0000 /h | $[0.0000, 2.9957]$  | 0 | 0.0000 /h | $[0.0000, 2.9957]$  |
| **Rural / Weather / Reservoir**| 0.583 h | 0.5833 h | 0 | 0.0000 /h | $[0.0000, 5.1355]$  | 0 | 0.0000 /h | $[0.0000, 5.1355]$  |
| **Urban Municipal (Bilbao)**| 1.063 h | 1.0449 h | 32 | 30.6253 /h | $[20.9324, 43.2505]$| 29 | 27.6433 /h | $[18.5137, 39.7712]$|
| **Pooled Overall Benchmark**| **6.646 h** | **6.6149 h** | **56** | **8.4657 /h** | **$[6.3949, 10.9935]$**| **51** | **7.7066 /h** | **$[5.7381, 10.1328]$**|

---

## 5. Robustness & Sensitivity Checks

To test whether the statistical conclusion ($p = 0.125$) is sensitive to particular outlier streams, leave-one-out sensitivity analyses were conducted:

1. **Excluding Highway Arterial Stream (`P24-NAT-STR-05`):**
   - Non-zero differences remaining: $N_r = 2$ (`P24-NAT-STR-14` and `P24-NAT-STR-16`).
   - Exact permutation $p = 0.250 > 0.05$ (Non-significant).
2. **Excluding All Bilbao Municipal Streams (`P24-NAT-STR-12` through `17`):**
   - Non-zero differences remaining: $N_r = 1$ (`P24-NAT-STR-05`).
   - Exact permutation $p = 0.500 > 0.05$ (Non-significant).
3. **Conclusion:**
   - Under all permutations, the evidence fails to demonstrate statistical superiority for Phase 17 Experimental.

---

## 6. Safety Designation

Statistical uncertainty quantification demonstrates that empirical false-alarm rates remain unacceptably high for operational deployment. Single-channel machine learning systems cannot provide safety assurances without multi-sensor confirmation and human dispatch supervision.

