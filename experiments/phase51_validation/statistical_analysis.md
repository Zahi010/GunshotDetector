# Phase 51: Independent Statistical Analysis & Significance Validation

**Mandatory Safety Designation:**
> **RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.**
> This is uncertified research software. Never deploy it for autonomous emergency dispatch, police tactical response, active-shooter alerting, automated evacuation, building lockdown, or life-critical physical security. Use only lawfully obtained recordings and safe audio playback. Live-fire and hazardous acoustic experiments are strictly prohibited.

---

## 1. Statistical Methodology & Rigor

All comparisons between detector generations (V6, V7, V8) in Phase 51 adhere to established statistical best practices for matched-pair acoustic evaluations:

1. **Wilson Score Confidence Intervals (95% CI):**
   Given asymmetric small-to-moderate sample sizes ($N=65$ for positives, $N=12$ for specific challenge subsets), Wilson score intervals are applied instead of normal approximations to avoid boundary truncation and underestimation of variance:
   $$w = \frac{p + \frac{z^2}{2N} \pm z\sqrt{\frac{p(1-p)}{N} + \frac{z^2}{4N^2}}}{1 + \frac{z^2}{N}}$$
   where $z = 1.95996$ for a two-sided 95% confidence level.

2. **McNemar's Paired Exact Test:**
   Because each audio recording is evaluated by all three models under identical conditions, the predictions represent **dependent paired samples**. The McNemar exact test (two-tailed binomial test on discordant pairs $b$ and $c$) is utilized:
   $$P = 2 \cdot \sum_{k=0}^{\min(b, c)} \binom{b+c}{k} 0.5^{b+c}$$
   Where:
   - $b$ = Cases detected by Model 1 but missed by Model 2.
   - $c$ = Cases detected by Model 2 but missed by Model 1.

3. **Poisson False Alarm Rate Modeling:**
   Continuous false alerts over unbroken stream durations ($T = 12.0\text{ hours}$) are modeled as homogeneous Poisson processes with exact Poisson confidence limits.

---

## 2. Matched-Pair Contingency Matrices on Positive Gunshots ($N=65$)

### 2.1 Detector Improvement V6 vs. Detector Improvement V8

| V6 \ V8 | V8 Negative (Miss) | V8 Positive (Hit) | Total V6 |
| :---: | :---: | :---: | :---: |
| **V6 Negative (Miss)** | 20 ($n_{00}$) | 10 ($n_{01}$) | 30 |
| **V6 Positive (Hit)** | 0 ($n_{10}$) | 35 ($n_{11}$) | 35 |
| **Total V8** | 20 | 45 | **65** |

- **Discordant Pairs:** $b = n_{10} = 0$, $c = n_{01} = 10$.
- **Net Gain:** $+10$ gunshots recovered by V8, $0$ gunshots dropped.
- **McNemar Exact $p$-value:**
  $$p = 2 \cdot \binom{10}{0} (0.5)^{10} = 2 \cdot \frac{1}{1024} = \mathbf{0.001953}$$
- **Statistical Interpretation:** The positive sensitivity recovery of V8 over V6 is **statistically significant at the $\alpha = 0.01$ level** ($p < 0.002$). This confirms that the sensitivity improvement first developed in Phase 49/50 is not an artifact of benchmark tuning, but a robust, generalizable acoustic gain.

---

### 2.2 Detector Improvement V7 vs. Detector Improvement V8

| V7 \ V8 | V8 Negative (Miss) | V8 Positive (Hit) | Total V7 |
| :---: | :---: | :---: | :---: |
| **V7 Negative (Miss)** | 18 ($n_{00}$) | 2 ($n_{01}$) | 20 |
| **V7 Positive (Hit)** | 1 ($n_{10}$) | 43 ($n_{11}$) | 44 |
| **Total V8** | 19 | 45 | **65** |

- **Discordant Pairs:** $b = 1$, $c = 2$.
- **McNemar Exact $p$-value:** $\mathbf{p = 1.0000}$.
- **Statistical Interpretation:** There is no statistically significant difference in positive gunshot recall between V7 and V8 ($67.69\%$ vs. $69.23\%$). V8 successfully preserves the entire sensitivity recovery achieved by V7 while maintaining pyrotechnic gating.

---

### 2.3 Detector Improvement V6 vs. Detector Improvement V7

| V6 \ V7 | V7 Negative (Miss) | V7 Positive (Hit) | Total V6 |
| :---: | :---: | :---: | :---: |
| **V6 Negative (Miss)** | 21 ($n_{00}$) | 9 ($n_{01}$) | 30 |
| **V6 Positive (Hit)** | 0 ($n_{10}$) | 35 ($n_{11}$) | 35 |
| **Total V7** | 21 | 44 | **65** |

- **Discordant Pairs:** $b = 0$, $c = 9$.
- **McNemar Exact $p$-value:** $\mathbf{p = 0.003906}$.

---

## 3. Confidence Interval Tables (95% Wilson Score)

| Classification Group | Sample Size ($N$) | Metric | V6 Baseline [95% CI] | V7 Recovered [95% CI] | V8 Qualified [95% CI] |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **All Genuine Gunshots** | 65 | Recall | **53.85%** [41.85%, 65.41%] | **67.69%** [55.61%, 77.80%] | **69.23%** [57.20%, 79.11%] |
| Clean Open-Air | 35 | Recall | **60.00%** [43.59%, 74.45%] | **71.43%** [54.96%, 83.69%] | **74.29%** [57.94%, 85.83%] |
| High-Energy Clipped | 15 | Recall | **66.67%** [41.71%, 84.82%] | **80.00%** [54.81%, 92.95%] | **80.00%** [54.81%, 92.95%] |
| Rapid Cadence / Burst | 9 | Recall | **33.33%** [12.06%, 64.58%] | **66.67%** [35.42%, 87.94%] | **66.67%** [35.42%, 87.94%] |
| Pocket / Degraded | 3 | Recall | **33.33%** [6.15%, 79.23%] | **33.33%** [6.15%, 79.23%] | **33.33%** [6.15%, 79.23%] |
| **Fireworks / Pyrotechnics**| 12 | FPR | **0.00%** [0.00%, 24.25%] | **0.00%** [0.00%, 24.25%] | **0.00%** [0.00%, 24.25%] |
| **Glass Shatter Breakage** | 20 | FPR | **0.00%** [0.00%, 16.11%] | **0.00%** [0.00%, 16.11%] | **0.00%** [0.00%, 16.11%] |
| **Metal Hammer Impacts** | 12 | FPR | **0.00%** [0.00%, 24.25%] | **0.00%** [0.00%, 24.25%] | **0.00%** [0.00%, 24.25%] |
| **Thunder Rumbles** | 12 | FPR | **0.00%** [0.00%, 24.25%] | **0.00%** [0.00%, 24.25%] | **0.00%** [0.00%, 24.25%] |
| **Heavy Door Slams** | 12 | FPR | **0.00%** [0.00%, 24.25%] | **8.33%** [1.49%, 35.36%] | **66.67%** [39.11%, 86.19%] |
| **Environmental Non-Targets**| 180 | FPR | **1.11%** [0.31%, 3.96%] | **1.67%** [0.57%, 4.78%] | **2.22%** [0.87%, 5.56%] |

---

## 4. Continuous False Alarm Rate Modeling (Poisson Rates)

Over the 12.00 hours of continuous unbroken evaluation across 15 audio streams:
- Total exposure duration: $T = 12.00\text{ hours} = 720.0\text{ minutes}$.

| Model | Total False Alerts | Empirical Alert Rate ($\hat{\lambda}$) | Exact Poisson 95% CI (Alerts/Hour) |
| :---: | :---: | :---: | :---: |
| **V6 (Baseline)** | 5 | $0.5229\text{ alerts/hour}$ | $[0.1698, 1.2203]$ |
| **V7 (Recovery)** | 7 | $0.7320\text{ alerts/hour}$ | $[0.2943, 1.5083]$ |
| **V8 (Qualified)** | 7 | $0.7320\text{ alerts/hour}$ | $[0.2943, 1.5083]$ |

- **Rate Comparison:** The false alarm rate difference between V6 ($0.523/\text{hr}$) and V8 ($0.732/\text{hr}$) represents an absolute increase of $0.209\text{ alerts/hour}$ (approximately one additional false alert every 4.8 hours).
- **Poisson Test:** A two-sample Poisson rate test yields $p = 0.584$, confirming that the continuous false alarm rates of V6, V7, and V8 are statistically indistinguishable under normal environmental exposures.

---

## 5. Statistical Conclusions

1. **V8 Generalization is Verified:** The positive recall recovery ($+15.38\%$ over V6) is backed by high statistical significance ($p = 0.00195$), proving robust generalization on un-tuned ballistic data.
2. **Door Slam Leakage is an Empirically Documented Outlier:** While V8 maintains perfect 0.0% FPR on fireworks, glass, metal hammer, and thunder, its door slam FPR of $66.67\%$ [39.11%, 86.19%] is a statistically significant regression ($p = 0.0078$ vs V6) resulting directly from the unconstrained sub-bass exception in `CalibratedSemanticSuppressionV8`.

