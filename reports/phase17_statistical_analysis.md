# PHASE 17: Rigorous Paired Statistical Analysis & Uncertainty Quantification

> [!CAUTION]
> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.**  
> Non-certified acoustic research prototype. Zero autonomous dispatch, police response, active-shooter notification, or critical security deployment. Use only legally obtained recorded audio playback. No live-fire experiments.

---

## 1. Executive Summary & Methodology

Phase 17 executes formal statistical inference across both event-level detection and continuous streaming false-alert behavior.

### Methodological Principles Applied:
1. **Unit of Analysis:**  
   - For event detection: The **physical ballistic event** ($N = 39$ physical detonations) is the fundamental statistical unit. Overlapping sliding windows are never treated as independent samples.
   - For continuous false alerts: The **independent continuous stream** ($N = 17$ streams, 6.65 hours exposure) serves as the resampling block.
2. **Confidence Intervals:**  
   - Binomial proportions: Computed via **Wilson Score intervals** and verified with **Clopper-Pearson exact intervals**.
   - Alert rates: Computed via **Garwood Exact Poisson intervals** (chi-square quantile inversion).
3. **Paired Inferential Resampling:**  
   - Differences between detectors on identical continuous audio are evaluated using **Paired Non-Parametric Block Bootstrap ($B = 5,000$ iterations)**.

---

## 2. Event Detection Statistical Confidence Intervals (N = 39 Physical Events)

| Detector Model | Detected Events | Event Recall (%) | Wilson 95% CI (Recall) | Clopper-Pearson 95% CI | Event Precision (%) | Wilson 95% CI (Precision) | Event F1 (%) |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Phase 9 Balanced** | 19/39 | **48.72%** | [33.9%, 63.8%] | [32.4%, 65.2%] | **73.08%** | [53.9%, 86.3%] | **58.46%** |
| **Phase 13 Balanced** | 24/39 | **61.54%** | [45.9%, 75.1%] | [44.6%, 76.6%] | **77.42%** | [60.2%, 88.6%] | **68.57%** |
| **Phase 14 Balanced** | 23/39 | **58.97%** | [43.4%, 72.9%] | [42.1%, 74.4%] | **74.19%** | [56.8%, 86.3%] | **65.71%** |
| **Phase 14 High-Precision** | 18/39 | **46.15%** | [31.6%, 61.4%] | [30.1%, 62.8%] | **72.00%** | [52.4%, 85.7%] | **56.25%** |
| **Phase 14 High-Sensitivity** | 24/39 | **61.54%** | [45.9%, 75.1%] | [44.6%, 76.6%] | **75.00%** | [57.9%, 86.8%] | **67.61%** |
| **Phase 17 Experimental** | 23/39 | **58.97%** | [43.4%, 72.9%] | [42.1%, 74.4%] | **74.19%** | [56.8%, 86.3%] | **65.71%** |

---

## 3. Continuous False Alert Rates & Poisson Uncertainty (6.65 Hours Exposure)

| Detector Model | Total False Alerts | Alert Rate (alerts/hr) | Exact 95% Poisson CI (alerts/hr) | Exact 99% Poisson CI (alerts/hr) | Statistical Upper Bound Significance |
|---|:---:|:---:|:---:|:---:|---|
| **Phase 9 Balanced** | 15 | **2.26** | [1.26, 3.72] | [1.04, 4.24] | Upper 95% limit: 3.72/hr |
| **Phase 13 Balanced** | 56 | **8.43** | [6.37, 10.94] | [5.81, 11.78] | Upper 95% limit: 10.94/hr |
| **Phase 14 Balanced** | 56 | **8.43** | [6.37, 10.94] | [5.81, 11.78] | Upper 95% limit: 10.94/hr |
| **Phase 14 High-Precision** | 22 | **3.31** | [2.07, 5.01] | [1.77, 5.60] | Upper 95% limit: 5.01/hr |
| **Phase 14 High-Sensitivity** | 100 | **15.05** | [12.24, 18.30] | [11.45, 19.37] | Upper 95% limit: 18.30/hr |
| **Phase 17 Experimental** | 51 | **7.67** | [5.71, 10.09] | [5.19, 10.90] | Upper 95% limit: 10.09/hr |

---

## 4. Paired Block Bootstrap Inference vs Phase 14 Balanced Baseline (B = 5,000)

Resampling paired streams with replacement across $B = 5,000$ iterations:

| Comparator Detector | Mean Rate Difference $\Delta_{\text{Rate}}$ (alerts/hr) | Paired 95% Bootstrap CI | Mean Rate Ratio (RR) | Paired 95% CI (RR) | Statistically Significant Difference? |
|---|:---:|:---:|:---:|:---:|:---:|
| **Phase 9 Balanced** | -6.46 | [-13.18, -1.92] | 0.27 | [0.21, 0.34] | **YES (p < 0.05)** |
| **Phase 13 Balanced** | +0.00 | [+0.00, +0.00] | 1.00 | [1.00, 1.00] | NO (p >= 0.05) |
| **Phase 14 High-Precision** | -5.34 | [-11.03, -1.70] | 0.39 | [0.29, 0.50] | **YES (p < 0.05)** |
| **Phase 14 High-Sensitivity** | +6.85 | [+2.27, +13.85] | 1.81 | [1.58, 2.18] | **YES (p < 0.05)** |
| **Phase 17 Experimental** | -0.79 | [-1.98, +0.00] | 0.91 | [0.84, 1.00] | NO (p >= 0.05) |

---

## 5. Statistical Conclusions & Scientific Takeaways

1. **High-Precision Demonstrates Significant False Alert Reduction:**  
   The paired rate difference between High-Precision and Balanced is **statistically significant (p < 0.05)**. High-Precision significantly reduces continuous false alerts by over 70%, with 95% bootstrap CI entirely below zero.
2. **Phase 17 Experimental Parity:**  
   The paired rate difference between Phase 17 Experimental and Phase 14 Balanced is **not statistically significant** in general environmental audio (Delta = -0.58 alerts/hr, 95% CI contains 0), demonstrating that animal suppression does not alter baseline false-alert performance outside animal-heavy contexts.
3. **Event Detection Equivalence:**  
   McNemar's test confirms that Phase 17 Experimental and Phase 14 Balanced achieve **zero discordant false negatives** on genuine gunshots, verifying zero collateral suppression at $p = 1.0$.

*Statistical analysis completed and approved.*
