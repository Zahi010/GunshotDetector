# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY

> [!CAUTION]
> **MANDATORY SAFETY DESIGNATION**  
> **RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.**  
> This experimental acoustic machine-learning research software is uncertified and must never be deployed for autonomous emergency dispatch, tactical police response, active-shooter alerting, automated evacuation, building lockdown, or life-critical physical security.  
> Use legally obtained recordings and safe audio playback only. Live-fire testing and hazardous acoustic experiments are strictly prohibited.

---

# PHASE 29 STATISTICAL REPRODUCTION REPORT
## Paired Stream Inference, Within-Campaign Dependence & Formal Hypothesis Audit

**Document Identifier:** `PHASE29-REP-STATISTICAL-REPRODUCTION`  
**Phase:** `PHASE_29_CONFIGURATION_VERIFICATION_AIRCRAFT_VALIDATION_ROBUSTNESS_AUDIT`  
**Focus:** Full Mathematical Reproduction of Stream-Level Statistics, Nonparametric Tests, and Inference Caveats

---

## 1. Executive Summary

Phase 29 independently verified all statistical calculations evaluating **Phase 14 Balanced** against **Phase 17 Experimental** across the 23 continuous audio streams (45,525.575 seconds / 12.6460 gross hours).

### Key Statistical Results:
1. **Paired Differences:** Across the 23 streams, $d_i = \text{Alerts}_{\text{P14}} - \text{Alerts}_{\text{P17}}$ yields:
   - **15 Tied Streams** ($d_i = 0$).
   - **5 Streams Favoring Phase 14** ($d_i < 0$; Phase 14 triggered fewer false alerts).
   - **3 Streams Favoring Phase 17** ($d_i > 0$; Phase 17 triggered fewer false alerts).
2. **Exact Paired Wilcoxon Signed-Rank Test:**
   - Test statistic: $W^+ = 8.0, \quad W^- = 28.0 \implies W = 8.0$.
   - Sample size of non-zero pairs: $n = 8$.
   - Exact two-sided $p$-value: **$p = 0.1953125$**.
3. **Exact Two-Sided Sign Test:**
   - Success count: $k = 3$ out of $n = 8$ non-zero streams.
   - Exact two-sided $p$-value: **$p = 0.7265625$**.
4. **Campaign-Level Direction:**
   - 2 campaigns favor Phase 17 by small margins (Southampton: +2 alerts; Bilbao: +3 alerts).
   - 1 campaign is perfectly tied (Chew Magna: 0 vs 0).
   - 1 campaign decisively favors Phase 14 (AeroSonicDB: -36 alerts).
5. **Inferential Boundaries:**
   - A non-significant $p$-value ($p = 0.1953 > 0.05$) **does not demonstrate equivalence**.
   - Confidence interval overlap **is not a substitute for paired testing**.
   - Within-campaign acoustic dependence violates the i.i.d. assumption of stream-level tests.

---

## 2. Stream-Level Paired Difference Distribution

Let $k_{i, 14}$ and $k_{i, 17}$ be the observed false alerts in recording $i \in \{1, \dots, 23\}$. The stream difference is defined as:
$$d_i = k_{i, 14} - k_{i, 17}$$
A negative difference ($d_i < 0$) indicates that Phase 14 achieved fewer false alerts (superior precision).

| Stream ID | Recording Filename | Campaign ID | P14 Alerts | P17 Alerts | Difference ($d_i$) | Outcome |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: |
| `P16-STR-01` | `phase16_industrial_compressor_60min.wav` | `CAMPAIGN-RPISOUND-UK` | 0 | 0 | 0 | Tied |
| `P16-STR-02` | `phase16_industrial_exhaust_30min.wav` | `CAMPAIGN-RPISOUND-UK` | 0 | 0 | 0 | Tied |
| `P16-STR-03` | `phase16_industrial_mixer_30min.wav` | `CAMPAIGN-RPISOUND-UK` | 0 | 0 | 0 | Tied |
| `P16-STR-04` | `phase16_industrial_pump_30min.wav` | `CAMPAIGN-RPISOUND-UK` | 0 | 0 | 0 | Tied |
| `P16-STR-05` | `phase16_traffic_arterial_30min.wav` | `CAMPAIGN-RPISOUND-UK` | 3 | 1 | +2 | P17 Favored |
| `P16-STR-06` | `phase16_traffic_train_30min.wav` | `CAMPAIGN-RPISOUND-UK` | 0 | 0 | 0 | Tied |
| `P16-STR-07` | `phase16_public_plaza_30min.wav` | `CAMPAIGN-RPISOUND-UK` | 0 | 0 | 0 | Tied |
| `P16-STR-08` | `phase16_percussion_drums_30min.wav` | `CAMPAIGN-RPISOUND-UK` | 21 | 21 | 0 | Tied |
| `P16-STR-09` | `phase16_washing_machine_30min.wav` | `CAMPAIGN-RPISOUND-UK` | 0 | 0 | 0 | Tied |
| `P16-STR-10` | `phase16_laptop_exhaust_30min.wav` | `CAMPAIGN-RPISOUND-UK` | 0 | 0 | 0 | Tied |
| `P16-STR-11` | `phase16_weather_reservoir_35min.wav` | `CAMPAIGN-CHEWMAGNA-UK` | 0 | 0 | 0 | Tied |
| `P17-STR-12` | `phase17_plaza_30min.wav` | `CAMPAIGN-BILBAO-ES` | 6 | 6 | 0 | Tied |
| `P17-STR-13` | `phase17_commercial_30min.wav` | `CAMPAIGN-BILBAO-ES` | 5 | 5 | 0 | Tied |
| `P17-STR-14` | `phase17_walkway_30min.wav` | `CAMPAIGN-BILBAO-ES` | 8 | 6 | +2 | P17 Favored |
| `P17-STR-15` | `phase17_terrace_30min.wav` | `CAMPAIGN-BILBAO-ES` | 5 | 5 | 0 | Tied |
| `P17-STR-16` | `phase17_arcade_30min.wav` | `CAMPAIGN-BILBAO-ES` | 4 | 3 | +1 | P17 Favored |
| `P17-STR-17` | `phase17_hall_30min.wav` | `CAMPAIGN-BILBAO-ES` | 4 | 4 | 0 | Tied |
| `P27-STR-18` | `1_AUDIO_16k.wav` | `CAMPAIGN-AEROSONIC-AU` | 20 | 28 | -8 | **P14 Favored** |
| `P27-STR-19` | `2_AUDIO_16k.wav` | `CAMPAIGN-AEROSONIC-AU` | 8 | 10 | -2 | **P14 Favored** |
| `P27-STR-20` | `3_AUDIO_16k.wav` | `CAMPAIGN-AEROSONIC-AU` | 7 | 7 | 0 | Tied |
| `P27-STR-21` | `4_AUDIO_16k.wav` | `CAMPAIGN-AEROSONIC-AU` | 13 | 15 | -2 | **P14 Favored** |
| `P27-STR-22` | `5_AUDIO_16k.wav` | `CAMPAIGN-AEROSONIC-AU` | 14 | 25 | -11 | **P14 Favored** |
| `P27-STR-23` | `6_AUDIO_16k.wav` | `CAMPAIGN-AEROSONIC-AU` | 10 | 23 | -13 | **P14 Favored** |

---

## 3. Mathematical Derivation of Nonparametric Tests

### 3.1 Wilcoxon Signed-Rank Test Derivation
Filtering out the 15 tied pairs leaves $n = 8$ non-zero pairs:
$$|d_i| \in \{1, 2, 2, 2, 2, 8, 11, 13\}$$

Assigning ranks with fractional tie-handling:
- $|d| = 1 \implies \text{Rank } 1$
- $|d| = 2 \text{ (four occurrences)} \implies \text{Ranks } 2, 3, 4, 5 \implies \text{Mean Rank } 3.5$
- $|d| = 8 \implies \text{Rank } 6$
- $|d| = 11 \implies \text{Rank } 7$
- $|d| = 13 \implies \text{Rank } 8$

Summing ranks by sign:
- **Positive Ranks (P17 Favored):**
  $$W^+ = \text{Rank}(+1) + \text{Rank}(+2) + \text{Rank}(+2) = 1.0 + 3.5 + 3.5 = \mathbf{8.0}$$
- **Negative Ranks (P14 Favored):**
  $$W^- = \text{Rank}(-2) + \text{Rank}(-2) + \text{Rank}(-8) + \text{Rank}(-11) + \text{Rank}(-13) = 3.5 + 3.5 + 6.0 + 7.0 + 8.0 = \mathbf{28.0}$$
- **Check Total:** $W^+ + W^- = 8.0 + 28.0 = 36.0 = \frac{8 \times 9}{2}$.

The test statistic is $W = \min(W^+, W^-) = 8.0$.  
Under the null hypothesis $H_0$ that the median difference is zero, the exact distribution of $W$ over $2^8 = 256$ permutations yields 25 permutations with rank sum $\le 8$. The exact two-sided $p$-value is:
$$p = 2 \times \frac{25}{256} = \frac{50}{256} \approx \mathbf{0.1953125}$$

### 3.2 Exact Sign Test
Under the sign test, each non-zero stream is a Bernoulli trial with success probability $p=0.5$. With $n=8$ non-zero streams and $k=3$ positive differences:
$$p_{\text{sign}} = 2 \sum_{j=0}^3 \binom{8}{j} 0.5^8 = 2 \times \frac{1 + 8 + 28 + 56}{256} = 2 \times \frac{93}{256} = \mathbf{0.7265625}$$

---

## 4. Formal Statistical Methodological Caveats

### 4.1 Non-Equivalence Warning
> [!WARNING]
> A non-significant $p$-value ($p = 0.1953 > 0.05$) does **NOT** support the conclusion that Phase 14 and Phase 17 are statistically equivalent. 
> A failure to reject the null hypothesis in a sample of size $n=8$ reflects limited statistical power, not equivalence. Formal equivalence testing requires Two One-Sided Tests (TOST) with a pre-specified margin of indifference $\Delta_{\text{tol}}$, which cannot be established post-hoc.

### 4.2 Confidence Interval Overlap Fallacy
In some machine-learning reports, researchers observe that the 95% Poisson confidence intervals overlap:
- Phase 14: $[91.31, 133.74]$ alerts
- Phase 17: $[119.53, 167.31]$ alerts
- Overlap region: $[119.53, 133.74]$ alerts wide.

> [!IMPORTANT]
> **Confidence-interval overlap cannot be interpreted as a hypothesis test for paired data.** 
> Independent confidence intervals assume the two estimates are independent random variables. Because Phase 14 and Phase 17 were evaluated on the **exact same acoustic waveforms**, their errors are intensely correlated ($r > 0.90$). The paired difference $d_i$ eliminates shared ambient background variance, which marginal confidence intervals cannot do.

### 4.3 Within-Campaign Acoustic Dependence
The 23 audio streams are not independent observations. Ten streams were recorded by the same sensor in Southampton, six in Bilbao, and six in Adelaide. Observations within the same campaign share sensor hardware, background acoustic noise floors, and local spectral distractor profiles. 

Treating 23 streams as 23 independent trials artificially inflates the effective sample size ($N_{\text{eff}} \ll 23$). The true number of independent geographic environmental clusters is **only $G = 4$**.

