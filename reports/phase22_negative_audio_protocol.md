# Continuous Negative-Audio Validation Protocol (100-Hour Benchmark)
## Prospective Evaluation of Operational False-Alarm Rates and Temporal Stability

**Document ID:** `REPORT-PHASE22-NEG-001`  
**Version:** 1.0 (Preregistered Protocol)  
**Date:** November 2026  
**Status:** PROSPECTIVE PROTOCOL SPECIFICATION  

---

### MANDATORY SAFETY DESIGNATION
> [!CAUTION]
> **RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.**  
> This experimental acoustic machine-learning system is uncertified and must never be deployed for autonomous emergency dispatch, tactical police response, active-shooter alerting, automated lockdown/evacuation, or life-critical physical security. Use legally obtained recordings and safe audio playback only. Live-fire testing and hazardous acoustic experiments are strictly prohibited.

---

## 1. Executive Summary & Objective

In Phase 16 and Phase 17, continuous negative audio testing on naturally continuous urban streams (6.08 hours) demonstrated that `model_phase14.py` (Balanced Profile) produced 6 false alerts (~0.99 alerts/hour), while `model_phase14.py` (High-Precision Profile) produced 0 false alerts. In contrast, concatenating synthetic 5-second slices (ESC-50) in Phase 15 yielded an artificial rate of 35 alerts/hour due to boundary discontinuities. In Phase 21, forensic audit revealed that the Pittsburgh Category A live-fire benchmark contains only 140.416 seconds of eligible negative-background exposure—completely insufficient to estimate long-term false-alert rates.

This protocol designs a prospective, long-duration continuous negative-audio validation benchmark targeting a minimum of **100 hours** of unbroken, legally obtained continuous urban acoustic audio. It establishes mathematical definitions for eligible exposure, cooldown exclusions, deduplication rules, Poisson uncertainty quantification, and overdispersion testing.

---

## 2. Ingestion Criteria for Negative Continuous Audio

### 2.1 Acoustic Environment Stratification
The 100-hour corpus must be partitioned across realistic, diverse metropolitan acoustic environments:

| Environment Category | Target Hours | Typical Acoustic Distractors | Target SPL Range ($L_{\text{Aeq}}$) |
|---|---|---|---|
| **Urban Canyon & Downtown** | 30.0 h | Traffic acceleration, sirens, bus air brakes, metal construction clanks, car door slams, echoes | 65–85 dBA |
| **Light Industrial / Rail Corridor** | 20.0 h | Heavy machinery, pneumatic tools, diesel engines, wheel squeal, coupler impacts, train horns | 70–95 dBA |
| **Commercial / Transit Hubs** | 20.0 h | Crowd noise, delivery tailgates, HVAC exhaust fans, reverberant concourses, garbage truck compactors | 60–80 dBA |
| **Residential / Suburban Fringe** | 15.0 h | Distant traffic, dog barks, lawn mowers, leaf blowers, residential fireworks, thunder | 45–65 dBA |
| **High-Wind & Inclement Weather** | 15.0 h | Wind turbulence across microphone grills ($>25\text{ km/h}$), rain impact, distant thunder rumble | 55–80 dBA |
| **TOTAL** | **100.0 h** | Complete urban background distribution | Dynamic |

### 2.2 Continuity and Hardware Integrity
1. **Unbroken Continuous Audio:** Audio must be captured in unbroken segments of duration $T \ge 60\text{ minutes}$ (preferred $4\text{ to }24\text{ hours}$ continuous capture). Synthetic concatenation of short clips is strictly forbidden.
2. **Native Sampling & Format:** Native uncompressed WAV or FLAC (minimum 16-bit, 22.05 kHz or 48 kHz). Upsampling or synthetic bandwidth restoration is prohibited.
3. **Absence of Audio Processing:** No dynamic range compression, automatic gain control (AGC), aggressive noise-gate suppression, or post-production equalization applied prior to model ingestion.

---

## 3. Ground Truth Verification & Positive Event Exclusion

To ensure that the negative audio benchmark contains zero true gunshot events:
1. **Multi-Stage Vetting:**
   - **Stage 1 (Source Verification):** Audio sourced from documented non-conflict urban monitoring streams, wildlife/soundscape archives, or municipal sensor feeds recorded during confirmed quiet periods.
   - **Stage 2 (Automated Energy Filtering):** Automated scanning for high-energy transient spikes ($L_{\text{peak}} - L_{\text{RMS}} > 18\text{ dB}$).
   - **Stage 3 (Human Expert Acoustic Review):** Any segment triggering an alert on *any* candidate detector (`model_phase14.py` or `model_phase17.py`) or flagged by automated energy scanning must be independently reviewed by two audio forensic analysts with spectrogram inspection.
2. **Exclusion of Ambiguous Intervals:**
   - If an impulsive sound cannot be definitively verified as non-gunfire (e.g., distant high-amplitude fireworks, unconfirmed industrial explosions), the segment spanning $[t_{\text{event}} - 5.0\text{ s}, t_{\text{event}} + 5.0\text{ s}]$ must be excised and categorized as `EXCLUDED_AMBIGUOUS`.
   - Excluded segments are subtracted from both total audio duration and eligible exposure.

---

## 4. Mathematical Definition of Eligible Exposure & Cooldown Dynamics

A detector cannot produce an alert while its internal state machine is in refractory cooldown or during model suppression buffers. Therefore, treating raw recording duration as the denominator produces an artificially suppressed false-alarm rate.

### 4.1 Refractory Cooldown Accounting
- Both `model_phase14.py` and `model_phase17.py` enforce a post-alert refractory cooldown:
  $$\tau_{\text{cooldown}} = 2.0\text{ seconds}$$
- When an alert occurs at time $t_{\text{alert}}$, the detector is blinded to new alert generation during $[t_{\text{alert}}, t_{\text{alert}} + \tau_{\text{cooldown}}]$.
- If a burst of false triggers occurs within the cooldown window, only the initial trigger generates an alert; subsequent windows are merged or suppressed.

### 4.2 Eligible Negative Exposure Formulation
Let $T_{\text{gross}}$ be the gross duration of unbroken negative audio in seconds. Let $K$ be the number of observed false alerts generated by the detector, each triggering an empirical refractory dead time $\tau_k$.

The **Eligible Negative Exposure** $T_{\text{eligible}}$ is formally defined as:
$$T_{\text{eligible}} = T_{\text{gross}} - \sum_{k=1}^K \min\left(\tau_{\text{cooldown}},\, T_{\text{remaining}, k}\right) - T_{\text{excluded}}$$

Where:
- $T_{\text{gross}}$: Total continuous runtime (e.g., $360,000\text{ s} = 100.0\text{ h}$).
- $T_{\text{excluded}}$: Total duration of excised ambiguous or clipped intervals.
- $\sum \tau_{\text{cooldown}}$: Total refractory suppression time during which the detector was incapable of issuing a false alert.
- $T_{\text{eligible}}$: Net operational exposure expressed in hours ($T_{\text{eligible\_hr}} = T_{\text{eligible}} / 3600$).

### 4.3 Dual-Metric Reporting Requirement
Every evaluation must report two distinct exposure denominators:
1. **Gross Stream False-Alert Rate ($\text{FAR}_{\text{gross}}$):**
   $$\text{FAR}_{\text{gross}} = \frac{K}{T_{\text{gross\_hr}}} \quad (\text{alerts per calendar stream hour})$$
2. **Eligible Operational False-Alert Rate ($\text{FAR}_{\text{eligible}}$):**
   $$\text{FAR}_{\text{eligible}} = \frac{K}{T_{\text{eligible\_hr}}} \quad (\text{alerts per eligible detector hour})$$

---

## 5. Statistical Estimation & Poisson Uncertainty Quantification

### 5.1 Idealized Poisson Model & Upper Bound Formula
Assuming false alerts follow a homogeneous Poisson point process with arrival rate $\lambda$ (alerts/hour) across eligible exposure $T_{\text{eligible\_hr}}$:
$$P(K = k) = \frac{(\lambda T)^k e^{-\lambda T}}{k!}$$

For an observed count $K = k$, the exact two-sided $(1 - \alpha)$ confidence interval $[\lambda_{\text{lower}}, \lambda_{\text{upper}}]$ is derived from the Chi-Square distribution (Garwood method):
$$\lambda_{\text{lower}} = \frac{\chi^2_{2k, \, \alpha/2}}{2 \, T_{\text{eligible\_hr}}}$$
$$\lambda_{\text{upper}} = \frac{\chi^2_{2(k+1), \, 1 - \alpha/2}}{2 \, T_{\text{eligible\_hr}}}$$

For the critical benchmark case of **zero false alerts** ($k = 0$) across $T = 100\text{ hours}$ at $\alpha = 0.05$ (one-sided 95% upper confidence bound):
$$\chi^2_{2, \, 0.95} = 2 \cdot (-\ln(0.05)) = 2 \cdot 2.99573 = 5.99146$$
$$\lambda_{\text{upper}, 95\%} = \frac{5.99146}{2 \cdot 100.0} = 0.02996 \approx 0.030\text{ alerts/hour}$$
This corresponds to an expected mean time between false alerts (MTBFA) of:
$$\text{MTBFA}_{\text{lower}, 95\%} = \frac{1}{\lambda_{\text{upper}}} \ge 33.38\text{ hours}$$

### 5.2 Test of Poisson Assumptions (Overdispersion & Burstiness)
Urban false alerts frequently cluster around localized disturbance events (e.g., a passing train with squealing flanges or continuous jackhammer operation).
To detect violations of the homogeneous Poisson assumption:
1. **Poisson Dispersion Test:** Partition the 100 hours into $M = 100$ one-hour blocks. Compute sample mean $\bar{x}$ and sample variance $s^2$. Compute Fisher's index of dispersion:
   $$D = \frac{(M - 1) s^2}{\bar{x}} \sim \chi^2_{M-1}$$
   If $p < 0.05$, reject the homogeneous Poisson hypothesis in favor of a negative binomial or zero-inflated cluster model.
2. **Cluster Sensitivity Analysis:** Report both raw alert count $K$ and clustered alert incident count $K_{\text{incident}}$, where alerts occurring within 60 seconds of each other are grouped into a single disturbance incident.

---

## 6. Execution Protocol Across Frozen Detectors

To ensure exact comparability without data leakage or test bias:
1. **Identical Signal Ingestion:** All frozen models evaluate the exact same digital audio streams sequentially or via parallel immutable pipes.
2. **Model Freeze Enforced:**
   - Default Production Baseline: `model_phase14.py` (Balanced Profile, threshold = 0.45, refractory = 2.0s).
   - High-Precision Profile: `model_phase14.py` (High-Precision Profile, threshold = 0.65).
   - High-Sensitivity Profile: `model_phase14.py` (High-Sensitivity Profile, threshold = 0.35).
   - Selectable Experimental Profile: `model_phase17.py` (Experimental Profile, multi-stage spectral suppression).
3. **Log Generation:** Every run outputs timestamped alert records containing:
   - Stream ID and timestamp offset.
   - Raw model score and feature vectors (spectral flux, crest factor, harmonic ratio).
   - Cooldown entry and exit timestamps.

---

## 7. Critical Limitations of 100-Hour Validation

> [!WARNING]
> Achieving zero false alerts across 100 continuous hours **does NOT establish**:
> 1. **Universal Urban Generalization:** A 100-hour sample cannot capture the seasonal acoustic diversity (snow-dampened canyons, heavy summer cicada choruses, torrential downpours) of arbitrary global municipalities.
> 2. **Operational Dispatch Reliability:** In municipal operations covering thousands of square kilometers, a sensor network aggregates thousands of channel-hours daily. An alert rate of 0.03 alerts/channel-hour scales to **30 false dispatches per 1,000 sensor-hours**, which is unacceptably high for autonomous dispatch.
> 3. **Life-Safety Certification:** No statistical validation protocol on pre-recorded audio substitutes for physical environmental stress, acoustic non-linearity, and hardware life-safety engineering.

---

*Authored by Principal Acoustic ML Research Engineer & Audio DSP Specialist.*  
*Antigravity Gunshot Detection Research Consortium — Phase 22.*

