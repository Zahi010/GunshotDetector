# Phase 20: Paired Model Comparison and McNemar Statistical Audit

> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY**  
> *This experimental acoustic machine-learning system is not certified and must never be used for autonomous emergency dispatch, police response, active-shooter alerting, automated evacuation, or critical physical security. Use legally obtained recorded audio and safe playback only. No live-fire testing or hazardous acoustic experiments.*

---

## 1. Executive Summary

When evaluating machine learning detectors on acoustic field data, comparing overall recall percentages without accounting for sample pairing obscures statistical significance. Because all candidate models in Phase 20 were evaluated on the **exact same 50 physical gunshot rounds** across 20 unbroken sensor recordings, paired non-parametric statistical hypothesis testing is required.

This audit reconstructs the exact $2 \times 2$ event-level contingency tables and calculates the exact two-sided binomial McNemar test for:
1. **Phase 14 Balanced (Production Baseline) vs. Phase 17 Experimental (Animal Suppression)**
2. **Phase 14 Balanced vs. Historical Comparators (Phase 9 Balanced, Phase 13 Balanced)**
3. **Phase 14 Balanced vs. Internal Profiles (High-Precision, High-Sensitivity)**

---

## 2. Primary Paired Comparison: Phase 14 Balanced vs. Phase 17 Experimental

### 2.1 Contingency Table ($N = 50$ Ground-Truth Events)

```
                       Phase 17 Experimental
                       Detected     Missed     Total
Phase 14   Detected       27           0         27  (54.0%)
Balanced   Missed          6          17         23  (46.0%)
           Total          33          17         50  (100.0%)
                        (66.0%)     (34.0%)
```

- **Both Detect ($a$):** 27 events (54.0%)
- **Phase 14 Only ($b$):** 0 events (0.0%)
- **Phase 17 Only ($c$):** 6 events (12.0%)
- **Neither Detect ($d$):** 17 events (34.0%)
- **Total Discordant Pairs ($b + c$):** 6 events

### 2.2 Exact Binomial McNemar Test Calculation
Under the null hypothesis $H_0$, both models have equal marginal detection probabilities, meaning discordant events are equally likely to be detected by Phase 14 or Phase 17 ($p = 0.5$).
Because $b = 0$ and $c = 6$, the total number of discordant pairs is $n = 6$.
The exact two-sided binomial $p$-value is:
$$p = 2 \cdot P(X = 0 \mid n=6, p=0.5) = 2 \cdot \binom{6}{0} (0.5)^6 = 2 \cdot \frac{1}{64} = \frac{2}{64} = 0.03125$$

### 2.3 Interpretation and Significance
- **Result:** $p = 0.03125 < 0.05$.
- **Conclusion:** The null hypothesis of marginal homogeneity is **rejected at the $\alpha = 0.05$ significance level**. 
- **Physical Interpretation:** Phase 17 Experimental detected every single event that Phase 14 Balanced detected ($b = 0$), plus 6 additional ballistic events in reverberant urban conditions ($c = 6$). 
- **Production Gate Consideration:** Despite this statistically significant recall advantage (+12.0%), Phase 17 Experimental **must not be promoted to the default production baseline automatically**. Phase 17 incorporates animal suppression adjustments designed for rural wildlife environments; while it exhibits higher sensitivity in Pittsburgh, its false-positive resistance across broader multi-day urban noise remains under evaluation. Phase 14 Balanced remains the verified default baseline.

---

## 3. Paired Comparisons Across All Model Profiles

The table below summarizes paired $2 \times 2$ metrics across all model combinations against Phase 14 Balanced:

| Comparison | Both Detected ($a$) | Phase 14 Only ($b$) | Competitor Only ($c$) | Neither Detected ($d$) | Discordant ($b+c$) | Exact McNemar $p$-value | Significant ($\alpha=0.05$) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Phase 14 Balanced vs Phase 17 Experimental** | 27 | 0 | 6 | 17 | 6 | **0.03125** | **YES** |
| **Phase 14 Balanced vs Phase 9 Balanced** | 25 | 2 | 3 | 20 | 5 | **1.00000** | NO |
| **Phase 14 Balanced vs Phase 13 Balanced** | 13 | 14 | 3 | 20 | 17 | **0.01273** | **YES** |
| **Phase 14 Balanced vs Phase 14 High-Precision** | 22 | 5 | 2 | 21 | 7 | **0.45312** | NO |
| **Phase 14 Balanced vs Phase 14 High-Sensitivity** | 22 | 5 | 0 | 23 | 5 | **0.06250** | NO |

### 3.1 Analysis of Historical Comparators
1. **Phase 14 Balanced vs. Phase 9 Balanced ($p = 1.0000$):**
   - Phase 9 Balanced achieved 28 detections vs. Phase 14's 27 detections (25 shared, 2 Phase 14 only, 3 Phase 9 only).
   - With 5 discordant events, there is **no statistically significant difference** in raw detection recall ($p = 1.0000$).
   - Crucially, Phase 14 achieves zero false alerts and zero duplicate triggers, whereas Phase 9 produced duplicate alerts in multi-round bursts.
2. **Phase 14 Balanced vs. Phase 13 Balanced ($p = 0.01273$):**
   - Phase 14 Balanced significantly outperforms Phase 13 Balanced (+22.0% recall, $p = 0.01273 < 0.05$).
   - Phase 13's aggressive spectral centroid and onset thresholding over-suppressed reverberant urban pulses (14 events detected by Phase 14 were missed by Phase 13).

---

## 4. Audit Sign-Off

- All 50 physical gunshot events in Category A have been independently paired.
- Exact binomial formulation was verified against `scipy.stats.binomtest`.
- Data saved to `reports/phase20_paired_model_comparison.csv`.

---
*Report certified under Phase 20 Forensic Audit protocol.*
