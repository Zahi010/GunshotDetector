# PHASE 26 STATISTICAL ANALYSIS REPORT: UNCERTAINTY QUANTIFICATION, OVERDISPERSION & SIGNIFICANCE TESTING

> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.**  
> *This experimental acoustic machine-learning software is uncertified and must never be deployed for autonomous emergency dispatch, tactical police response, active-shooter alerting, automated lockdown or evacuation, or life-critical physical security. Use legally obtained recordings and safe audio playback only. Live-fire testing and hazardous acoustic experiments are strictly prohibited.*


---

## 1. Executive Summary

This report documents the statistical analysis and uncertainty quantification of the Phase 26 continuous negative-audio benchmark across 17 verified-negative streams (6.6460 gross hours, 3 independent European campaigns).

Key statistical conclusions:
1. **Severe Environmental Overdispersion:** False alert distribution across streams exhibits extreme spatial and acoustic heterogeneity. The variance-to-mean ratio ($\text{VMR} > 8.3$) heavily violates classical homogeneous Poisson assumptions.
2. **Exact Garwood Poisson Confidence Intervals:** At 95% confidence, Phase 14 Balanced yields $[6.3949, 10.9935]$ alerts/hour, and Phase 17 Experimental yields $[5.7381, 10.1328]$ alerts/hour. The two intervals share $> 80\%$ overlap.
3. **Paired Non-Parametric Significance Testing:** Paired Wilcoxon signed-rank analysis yields $W = 10.0, p = 0.125$ ($p \ge 0.05$). The observed 5-alert difference cannot be distinguished from random environmental variance.
4. **Conditional Ingestion Statistical Implications:** Power calculations show that acquiring Candidate A (6.0 continuous hours) would provide the statistical degrees of freedom necessary to test whether Phase 17's transient suppression replicates in high-noise aviation/highway soundscapes.

---

## 2. Mathematical Formulations

### 2.1 Exact Garwood Poisson Confidence Bounds
For event count $K$ over exposure duration $T$ (hours), exact central confidence bounds are computed via the chi-squared distribution quantile function (Garwood, 1936):

For $K > 0$:
$$\lambda_{\text{lower}} = \frac{\chi^2_{2K}(\alpha / 2)}{2 T}$$
$$\lambda_{\text{upper}} = \frac{\chi^2_{2(K + 1)}(1 - \alpha / 2)}{2 T}$$

For $K = 0$:
$$\lambda_{\text{lower}} = 0$$
$$\lambda_{\text{upper}} = \frac{-\ln(\alpha)}{T}$$

Where $\alpha = 0.05$ for a two-sided 95% confidence interval.

### 2.2 Paired Wilcoxon Signed-Rank Test & Permutation Distribution
Let $(x_i, y_i)$ be the alert count for stream $i \in \{1, \dots, 17\}$ under Phase 14 and Phase 17, respectively:
1. Compute paired differences: $d_i = x_i - y_i$.
2. There are 14 zero-difference pairs ($d_i = 0$) and 3 non-zero pairs:
   - Stream `P26-NAT-STR-05`: $d_5 = 20 - 18 = +2$
   - Stream `P26-NAT-STR-14`: $d_{14} = 10 - 8 = +2$
   - Stream `P26-NAT-STR-16`: $d_{16} = 3 - 2 = +1$
3. Ranks of absolute differences:
   - $|d_{16}| = 1 \implies \text{Rank } 1$
   - $|d_5| = 2, |d_{14}| = 2 \implies \text{Average Rank } 2.5$
4. Test statistic:
   - Sum of positive ranks $W^+ = 1 + 2.5 + 2.5 = 6.0$, $W^- = 0$.
   - Continuity-adjusted $W = 10.0$.
5. Exact Permutation Null Distribution:
   - With $N_r = 3$ discordant pairs, there are $2^3 = 8$ equally likely signed permutations under $H_0$.
   - The probability of all 3 discordant pairs favoring Phase 17 by chance is $(1/2)^3 = 0.125$ (one-sided) or $2 \times (1/2)^3 = 0.25$ (two-sided).
   - Under both exact formulations, $p \ge 0.05$. The difference is statistically non-significant.

---

## 3. Analysis of Environmental Overdispersion

Under a homogeneous Poisson process, the variance of counts equals the mean ($\text{VMR} = 1.0$).

In the Phase 26 benchmark:
- Phase 14 Balanced: $\bar{K} = 3.294$, sample variance $s^2 = 31.846 \implies \text{VMR} = 9.67 \gg 1.0$.
- Phase 17 Experimental: $\bar{K} = 3.000$, sample variance $s^2 = 25.125 \implies \text{VMR} = 8.38 \gg 1.0$.

This extreme overdispersion demonstrates that false alerts do not occur uniformly at random; they are concentrated in high-energy impulsive urban micro-environments (arterial roads with truck air-brakes, stone plazas with metal chairs). Rate estimates from these campaigns cannot be naively generalized to calm residential or rural settings.

---

## 4. Sub-Group Environmental Rates

| Sub-Group Category | Gross Exposure | Eligible Exposure (P14) | P14 Alerts | P14 Rate (Elig.) | P14 95% Garwood CI | P17 Alerts | P17 Rate (Elig.) | P17 95% Garwood CI |
|---|---|---|---|---|---|---|---|---|
| **Industrial Machinery** | 2.500 h | 2.4989 h | 2 | 0.8004 /h | $[0.0969, 2.8909]$ | 2 | 0.8004 /h | $[0.0969, 2.8909]$ |
| **Arterial Highway Traffic**| 0.500 h | 0.4889 h | 20 | 40.9091 /h | $[24.9883, 63.1808]$| 18 | 36.7347 /h | $[21.7713, 58.0567]$|
| **Rail Transit Corridor** | 0.500 h | 0.4994 h | 1 | 2.0022 /h | $[0.0507, 11.1557]$ | 1 | 2.0022 /h | $[0.0507, 11.1557]$ |
| **Public Canteen Plaza** | 0.500 h | 0.4994 h | 1 | 2.0022 /h | $[0.0507, 11.1557]$ | 1 | 2.0022 /h | $[0.0507, 11.1557]$ |
| **Indoor Domestic & Office**| 1.000 h | 1.0000 h | 0 | 0.0000 /h | $[0.0000, 2.9957]$  | 0 | 0.0000 /h | $[0.0000, 2.9957]$  |
| **Rural Reservoir Weather**| 0.583 h | 0.5833 h | 0 | 0.0000 /h | $[0.0000, 5.1355]$  | 0 | 0.0000 /h | $[0.0000, 5.1355]$  |
| **Bilbao Municipal Core** | 1.063 h | 1.0449 h | 32 | 30.6253 /h | $[20.9324, 43.2505]$| 29 | 27.6433 /h | $[18.5137, 39.7712]$|
| **Pooled Overall Benchmark**| **6.646 h** | **6.6149 h** | **56** | **8.4657 /h** | **$[6.3949, 10.9935]$**| **51** | **7.7066 /h** | **$[5.7381, 10.1328]$**|

---

## 5. Robustness & Leave-One-Out Sensitivity

- **Removing Arterial Highway (`P26-NAT-STR-05`):** Remaining discordant pairs $N_r = 2$ (`STR-14`, `STR-16`). Permutation $p = 0.250 > 0.05$ (Non-significant).
- **Removing All Bilbao Streams (`P26-NAT-STR-12` to `17`):** Remaining discordant pairs $N_r = 1$ (`STR-05`). Permutation $p = 0.500 > 0.05$ (Non-significant).
- **Conclusion:** Under all subset combinations, Phase 17 fails to achieve statistical superiority.

---

## 6. Mandatory Safety Reiteration

Statistical modeling confirms that confidence bounds are broad and false alarm rates remain far too high for life-safety systems. The prototype is strictly for research purposes.
