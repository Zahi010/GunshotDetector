# Phase 15 Independent Statistical Analysis & Generalization Audit

**Safety Designation: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.**

## 1. Unit of Statistical Analysis

In compliance with Phase 15 Section 9:
- **Discrete Event Analysis:** The unit of analysis is the **independent physical audio recording** (or distinct ballistic firing event), NOT extracted sliding sub-windows. Sliding windows from the same recording are acoustically and temporally correlated.
- **Continuous Stream Analysis:** The unit of analysis is the **independent 5.0-second source recording track** ($N = 1,440$ distinct tracks across 2.00 hours).
- Treating repeated sliding windows as independent degrees of freedom produces artificially deflated $p$-values and pseudoreplication.

---

## 2. Event-Level Confidence Intervals (Blind Independent Dataset, Split C)

All confidence intervals are exact 95% Wilson score intervals:

| Detector Profile | Events Evaluated | TP / FP / FN | Event Precision | 95% Wilson CI (Prec) | Event Recall | 95% Wilson CI (Recall) | Event F1 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Phase 9 Baseline** | 28 genuine | 21 / 3 / 7 | **87.50%** | [69.0%, 95.66%] | **75.00%** | [56.64%, 87.32%] | **80.77%** |
| **Phase 13 Candidate** | 28 genuine | 20 / 2 / 8 | **90.91%** | [72.19%, 97.47%] | **71.43%** | [52.94%, 84.75%] | **80.00%** |
| **Phase 14 Balanced** | 28 genuine | 21 / 3 / 7 | **87.50%** | [69.0%, 95.66%] | **75.00%** | [56.64%, 87.32%] | **80.77%** |
| **Phase 14 High-Precision** | 28 genuine | 16 / 1 / 12 | **94.12%** | [73.02%, 98.95%] | **57.14%** | [39.07%, 73.49%] | **71.11%** |
| **Phase 14 High-Sensitivity** | 28 genuine | 25 / 5 / 3 | **83.33%** | [66.44%, 92.66%] | **89.29%** | [72.8%, 96.29%] | **86.21%** |

---

## 3. Acoustic Regime Subgroup Analysis

Confidence intervals across acoustic conditions on independent physical recordings:

| Detector Profile | Pocket Occlusion Recall (N=18) | Pocket 95% Wilson CI | Clean Direct Recall (N=18) | Clean 95% Wilson CI | Clipped Range Recall (N=6) | Clipped 95% Wilson CI |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Phase 9 Baseline** | **55.56%** | [33.72%, 75.44%] | **94.44%** | [74.24%, 99.01%] | **83.33%** | [43.65%, 96.99%] |
| **Phase 13 Candidate** | **50.00%** | [29.03%, 70.97%] | **94.44%** | [74.24%, 99.01%] | **50.00%** | [18.76%, 81.24%] |
| **Phase 14 Balanced** | **55.56%** | [33.72%, 75.44%] | **94.44%** | [74.24%, 99.01%] | **83.33%** | [43.65%, 96.99%] |
| **Phase 14 High-Precision** | **33.33%** | [16.28%, 56.25%] | **83.33%** | [60.78%, 94.16%] | **33.33%** | [9.68%, 70.0%] |
| **Phase 14 High-Sensitivity** | **72.22%** | [49.13%, 87.5%] | **100.00%** | [82.41%, 100.0%] | **100.00%** | [60.97%, 100.0%] |

---

## 4. Continuous False Alert Analysis (N = 1,440 Independent Tracks, 2.00 Hours)

| Detector Configuration | Total Alerts | False Alert Rate (alerts/hr) | Boundary Splice Alerts | Non-Boundary Alerts |
| :--- | :--- | :--- | :--- | :--- |
| **Phase 9 Baseline** | 75 | **37.50** | 19 | 56 |
| **Phase 13 Candidate** | 70 | **35.00** | 17 | 53 |
| **Phase 14 Balanced** | 70 | **35.00** | 17 | 53 |
| **Phase 14 High-Precision** | 40 | **20.00** | 11 | 29 |
| **Phase 14 High-Sensitivity** | 112 | **56.00** | 34 | 78 |

---

## 5. Statistical Hypothesis Testing & Significance Reconciliation

### A. Paired Comparison: Phase 14 Balanced vs Phase 13 Candidate
- **Continuous Stream Alert Reduction:** Phase 14 achieves comparable continuous false alert rates to Phase 13 while recovering ballistic sensitivity that Phase 13 had suppressed.
- **Pocket Sensitivity Recovery:** On 18 independent pocket-occluded recordings, Phase 14 Balanced achieves 55.56% recall vs Phase 13's 50.00% (High-Sensitivity reaches 72.22%).
- **Reconciliation:** The difference in discrete pocket sample recall between Phase 14 Balanced (10/18) and Phase 13 (9/18) is not statistically significant at $\alpha = 0.05$ (McNemar's $p > 0.30$) due to sample size constraints ($N=18$). However, Phase 14 High-Sensitivity (13/18) demonstrates a substantial practical gain in muffled event capture.

### B. Paired Comparison: Phase 14 Balanced vs Phase 9 Baseline
- Phase 9 baseline lacks pyrotechnic and canine semantic suppression, resulting in higher false alerts on fireworks and barking.
- Phase 14 incorporates calibrated semantic gating with ballistic protection, preventing muzzle blast suppression while reducing pyrotechnic confusers.

---

## 6. Safety & Operational Implications

1. **Uncertainty Bounds Confirm Prototype Status:** With 95% confidence intervals for pocket recall spanning [33.7%, 75.4%], there is immense physical uncertainty under varied occlusion conditions.
2. **False Alert Rate Incompatible with Autonomous Response:** Even the High-Precision profile generates false alerts in complex environments, which would trigger unacceptable false dispatch rates in production municipal or school environments.
3. **Mandatory Designation:** These statistical facts establish beyond doubt that this acoustic detection system is a **RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY**.
