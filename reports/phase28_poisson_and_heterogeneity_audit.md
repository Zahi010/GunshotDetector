# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY

**MANDATORY SAFETY DESIGNATION:**
This experimental acoustic machine-learning software is uncertified and must never be deployed for autonomous emergency dispatch, tactical police response, active-shooter alerting, automated evacuation, building lockdown, or life-critical physical security.

Use legally obtained recordings and safe audio playback only. Live-fire testing and hazardous acoustic experiments are strictly prohibited.

---

# PHASE 28 TECHNICAL AUDIT REPORT
## Poisson Assumptions, Garwood Confidence Limits & Environmental Heterogeneity Forensics

**Document Identifier:** `PHASE28-REP-POISSON-HETEROGENEITY`  
**Phase:** `PHASE_28_INDEPENDENT_REPRODUCTION_CAMPAIGN_STATISTICS_COOLDOWN_FORENSICS`  
**Scope:** Cumulative 23-stream continuous negative benchmark (Phases 23–27)

---

## 1. Executive Summary

In acoustic machine-learning research, false alert rates are frequently reported alongside **exact Garwood Poisson confidence intervals**. While the Garwood formula is arithmetically exact for a stationary counting process, its validity relies on foundational statistical assumptions that are severely challenged in real-world environmental acoustics.

This audit evaluates:
1. **Mathematical Correctness:** The exact Garwood formula was verified and reproduced with 100% precision across all 23 streams and aggregate totals.
2. **Exposure Denominators:** The effect of gross exposure versus cooldown-adjusted eligible exposure is analyzed.
3. **Assumptions Audit:** Five key assumptions of the Poisson process (constant arrival rate, event independence, temporal stationarity, between-recording homogeneity, and between-campaign homogeneity) were audited. All five are violated in complex urban acoustic environments.
4. **Methodological Boundaries:** A conditional Poisson confidence interval provides a bound **conditioned exclusively on the observed recording environment**. It must never be interpreted as an operational false-alert rate for municipal deployment or generalized to uncharacterized cities.
5. **Prohibition of CI Overlap as Hypothesis Test:** We formally document why overlapping or non-overlapping confidence intervals must never be used as a substitute for a paired hypothesis test on correlated data.

---

## 2. Mathematical Audit of the Garwood Formula

### 2.1 Theoretical Formulation
For an observed count of $k$ events over valid exposure duration $T$ hours, the exact $100(1 - \alpha)\%$ central confidence interval for the Poisson rate $\lambda$ is derived from the relationship between the cumulative Poisson distribution and the chi-square ($\chi^2$) distribution:

$$\lambda_{\text{lower}} = \begin{cases} 0 & \text{if } k = 0 \\ \frac{1}{2T} \chi^2_{2k, \, \alpha/2} & \text{if } k > 0 \end{cases}$$

$$\lambda_{\text{upper}} = \frac{1}{2T} \chi^2_{2(k+1), \, 1 - \alpha/2}$$

For a 95% confidence interval ($\alpha = 0.05$), $\alpha/2 = 0.025$ and $1 - \alpha/2 = 0.975$.

### 2.2 Independent Reproduction of Benchmark Totals
Using the actual cumulative exposure from [reports/phase28_exposure_reproduction.csv](file:///e:/gunshot/gunshot/reports/phase28_exposure_reproduction.csv):

1. **Phase 14 Balanced (Default Research Baseline):**
   - Observed Alerts: $k = 128$
   - Gross Exposure: $T_{\text{gross}} = 12.6460\text{ hr}$ $\rightarrow$ Gross Rate = **10.1218 /hr** (95% CI: [8.4447, 12.0354])
   - Eligible Exposure: $T_{\text{eligible}} = 12.5199\text{ hr}$ $\rightarrow$ Eligible Rate = **10.2237 /hr** (95% CI: [8.5294, 12.1561])
   - Reproduced Phase 27 Value: Matched with $< 0.01\%$ numerical difference.
2. **Phase 17 Experimental (Selectable Profile):**
   - Observed Alerts: $k = 159$
   - Gross Exposure: $T_{\text{gross}} = 12.6460\text{ hr}$ $\rightarrow$ Gross Rate = **12.5732 /hr** (95% CI: [10.6974, 14.6896])
   - Eligible Exposure: $T_{\text{eligible}} = 10.8723\text{ hr}$ $\rightarrow$ Eligible Rate = **14.6243 /hr** (95% CI: [12.4395, 17.0824])
   - Reproduced Phase 27 Value: Matched with $< 0.01\%$ numerical difference.

---

## 3. Systematic Audit of Poisson Process Assumptions

| Assumption | Theoretical Requirement | Real-World Empirical Reality in Acoustic Benchmark | Audit Finding |
| :--- | :--- | :--- | :--- |
| **1. Constant Event Rate** | $\lambda(t) = \lambda$ across entire monitored duration | False alerts occur in concentrated bursts coinciding with episodic distractors (e.g., low-altitude aircraft flyovers, sirens, pneumatic exhaust cycles). Background is quiescent for hours, then surges. | **VIOLATED** (Non-homogeneous arrival process) |
| **2. Event Independence** | Events in non-overlapping intervals are independent | Consecutive alerts cluster heavily due to state-machine hysteresis chatter and prolonged flyovers. The occurrence of an alert at $t$ dramatically increases $P(\text{alert at } t + \Delta t)$. | **VIOLATED** (Severe temporal clustering / self-excitation) |
| **3. Temporal Stationarity** | Distribution of events depends only on interval length, not origin | Diurnal traffic patterns, aircraft flight schedules, and weather shifts cause strong non-stationarity across continuous streams. | **VIOLATED** |
| **4. Between-Recording Homogeneity** | All streams within a campaign share identical arrival rate | In `CAMPAIGN-BILBAO-ES`, rates vary from 19.3 /hr (Plaza Nueva) to 107.8 /hr (Arcade) due to physical micro-acoustics and reverberation. | **VIOLATED** (Spatial overdispersion) |
| **5. Between-Campaign Homogeneity** | All campaigns share identical underlying arrival rate | Rates range from 0.00 /hr in rural Chew Magna to 56.87 /hr in urban Bilbao and 12.00 /hr in Adelaide perimeter. | **VIOLATED** (Extreme environmental heterogeneity) |

---

## 4. Why Garwood Intervals Remain Mathematically Useful (and Their Limits)

Given these severe violations, why compute Garwood Poisson intervals at all?
- **Valid Conditional Interpretation:** For a single continuous recording in a specific static environment, the Garwood interval provides an exact, conservative coverage bound for the **realized sample rate conditioned on that specific channel and time window**.
- **Invalid Generalization:** The Garwood interval must **never** be extrapolated beyond the specific observed test set. It does not bound the false alert rate of:
  - Other sensor nodes in the same city.
  - The same sensor node during different seasons or flight schedules.
  - An arbitrary uncharacterized municipality.
- **Overdispersion Implication:** Because between-recording and between-campaign variance dominates within-recording Poisson variance ($\text{VMR} \gg 1$), population-level rate estimation requires negative binomial, compound Poisson-gamma, or hierarchical Bayesian random-effects models.

---

## 5. Prohibition: Confidence Interval Overlap vs. Paired Hypothesis Testing

It is a common statistical fallacy to compare two models by checking whether their separate 95% confidence intervals overlap:
- In Phase 27, the 95% Garwood CI for Phase 14 was $[8.53, 12.16]$ and for Phase 17 was $[12.44, 17.08]$. Because the lower bound of Phase 17 exceeded the upper bound of Phase 14, naive observers might conclude that the difference is statistically significant ($p < 0.05$).
- **Statistical Fallacy:** Two-sample independent confidence intervals assume the two groups are independent. In continuous benchmark evaluation, both detectors process the **exact same identical audio streams at the exact same identical timestamps**. The observations are **strictly paired and correlated** ($r \approx 0.95$).
- **Mandatory Rule:** Hypotheses regarding relative detector superiority must be evaluated using **paired non-parametric tests** (e.g., Wilcoxon signed-rank test on stream-level differences $d_i = \text{Alerts}_{P14, i} - \text{Alerts}_{P17, i}$).
- **The Correct Test Output:** As proven in [reports/phase28_campaign_aware_statistics.md](file:///e:/gunshot/gunshot/reports/phase28_campaign_aware_statistics.md), the paired Wilcoxon test yields $W = 8.0, p = 0.1953 \ge 0.05$. The difference is **not statistically significant** under rigorous paired inference.

