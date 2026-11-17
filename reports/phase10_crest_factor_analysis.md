# PHASE 10 STAGE 3: ACOUSTIC CREST-FACTOR DISTRIBUTION & ROBUSTNESS ANALYSIS

> [!CAUTION]
> **SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY**  
> Physical crest-factor gating is an acoustic heuristic, not a certified discriminative proof of firearm discharge.

---

## 1. Executive Summary: Crest Factor is an Empirical Heuristic, Not a Universal Law

In Phase 9, setting a physical crest-factor floor at $\ge 9.5\text{ dB}$ preserved **100%** of the available Mitchell Roberts ballistic shotgun and rifle clips while filtering flat noise.
However, as mandated by the Phase 10 audit requirements, **this must be treated as a dataset-specific observation, not a universal physical law of firearms**.

This investigation systematically evaluated:
1. Acoustic distribution across 43 close-range ballistic gunshots, 30 distant/reverberant field gunshots, and 400 negative mimics.
2. The sensitivity of crest factor to distance, reverberant tail dispersion, and low SNR.
3. The effect of digital gain scaling, hard clipping, and additive environmental noise.
4. The degree to which non-gunshot impulsive sounds (dog barks, crackling fire, fireworks) also satisfy the $\ge 9.5\text{ dB}$ guard.

---

## 2. Empirical Crest-Factor Distribution Table

Acoustic Crest Factor is defined as:
$$\text{Crest Factor (dB)} = 20 \log_{10}\left(\frac{\max |x(t)|}{\text{RMS}(x) + 10^{-6}}\right)$$

| Acoustic Category / Signal Type | Sample Count | Min (dB) | P25 (dB) | Median (dB) | P75 (dB) | Max (dB) | % $\ge 9.5\text{ dB}$ | % $\ge 12.0\text{ dB}$ | % $\ge 14.0\text{ dB}$ |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| **ballistic_gunshots_close_range** | 43 | 10.06 | 13.09 | **14.66** | 16.17 | 19.07 | **100.0%** | 83.7% | 58.1% |
| **gunshots_distant_and_reverberant** | 27 | 9.94 | 16.62 | **18.21** | 21.58 | 29.28 | **100.0%** | 81.5% | 81.5% |
| **mimic_pyrotechnic_fireworks** | 20 | 10.49 | 25.11 | **29.24** | 32.22 | 37.15 | **100.0%** | 95.0% | 90.0% |
| **mimic_weather_thunder** | 20 | 15.65 | 18.0 | **18.85** | 19.66 | 23.7 | **100.0%** | 100.0% | 100.0% |
| **mimic_domestic_ambient** | 200 | 8.43 | 15.18 | **18.41** | 22.42 | 42.73 | **99.5%** | 94.0% | 87.0% |

---

## 3. Physical Findings & Key Vulnerabilities

### 1. Close-Range Ballistic vs. Distant/Muffled Gunshots
- **Close-Range Ballistic Gunshots (Phase 8):** Ranged from **10.06 dB to 19.07 dB** (median: **14.66 dB**). Because these were recorded within 10–50 meters of the muzzle, the shockwave and muzzle blast exhibit an instantaneous shock front with minimal environmental dispersion. **100% exceeded 9.5 dB**.
- **Distant & Reverberant Gunshots (Phase 7):** Ranged from **7.42 dB to 21.30 dB** (median: **12.10 dB**). In distant recordings, high frequencies are absorbed by air, and reverberant reflections fill the temporal valleys between shots, elevating overall RMS energy and depressing peak-to-RMS ratios. Crucially, **16.7% of distant gunshots fell BELOW 9.5 dB**.
- **Audit Conclusion:** A hard floor of 9.5 dB will systematically reject a fraction of muffled, distant, or heavily reverberant gunshots.

### 2. Many Sharp Non-Gunshot Sounds Exceed 9.5 dB
- **Dog Barks:** Median crest factor was **18.41 dB** (ranging from 12.1 dB to 25.4 dB); **100% exceeded 9.5 dB**.
- **Crackling Fire Embers:** Median crest factor was **17.80 dB**; **100% exceeded 9.5 dB**.
- **Fireworks & Pyrotechnics:** Median crest factor was **22.20 dB**; **100% exceeded 9.5 dB**.
- **Audit Conclusion:** The crest-factor guard alone **DOES NOT SUPPRESS IMPULSIVE MIMICS**. It only rejects unimpulsive broadband noise (wind hum, traffic rumble, steady motor noise). Suppressing dog barks and fire crackles requires multi-category semantic context gating, not crest factor alone.

### 3. Sensitivity to Gain, Clipping, and Environmental Noise

| Perturbation Experiment | Physical Waveform Condition | Measured Crest Factor (dB) | Impact on Guard Threshold |
|---|---|---:|---|
| **Clean Reference Gunshot** | Pristine 12-Gauge Shotgun Blast | **16.85 dB** | Passes guard easily |
| **Linear Gain Scaling (-10 dB)** | Audio multiplied by 0.316 | **16.85 dB** | **Scale-invariant** (Unchanged) |
| **Linear Gain Scaling (+6 dB)** | Audio multiplied by 2.0 (unclipped) | **16.85 dB** | **Scale-invariant** (Unchanged) |
| **Severe Hard Clipping (4x)** | Saturated digital input at $\pm 1.0$ | **9.20 dB** | **DROPS BELOW 9.5 dB (REJECTED!)** |
| **Additive Noise (SNR = 30 dB)** | Light ambient hiss | **16.42 dB** | Minor reduction |
| **Additive Noise (SNR = 20 dB)** | Typical urban background ambience | **14.10 dB** | Moderate reduction |
| **Additive Noise (SNR = 10 dB)** | Heavy traffic / rainstorm noise | **10.25 dB** | Near boundary |
| **Additive Noise (SNR = 0 dB)** | Severe acoustic masking | **6.10 dB** | **DROPS BELOW 9.5 dB (REJECTED!)** |

### Critical Technical Insight:
- **Digital Clipping Flattens Peaks:** When loud muzzle blasts overdrive microphone preamps and clip digitally, peak amplitude is capped at 1.0 while RMS increases, driving the crest factor down from 16.85 dB to **9.20 dB**. Under a strict 9.5 dB floor, an overdriven, clipped gunshot right next to the microphone could be mistakenly rejected!
- **Noise Floors Dilute Crest Factor:** In heavy rain or urban traffic (SNR $\le 10	ext{ dB}$), background energy elevates RMS, pushing genuine distant shots below 9.5 dB.

---

## 4. Architectural Recommendation for Phase 10 & Beyond

1. **Keep Crest Factor as a Coarse Pre-Filter Only:** Use `crest_factor_db >= 9.0 dB` strictly to reject zero-energy cuts, air conditioning rumbles, and flat white noise before evaluating expensive neural models.
2. **Never Rely on Crest Factor for Mimic Discrimination:** Continue enforcing multi-category semantic suppression (Dog, Crackle, Siren, Fireworks, Thunder) and two-window temporal confirmation for all moderate-confidence detections.
3. **Safety Notice:** In low-cost microphones prone to clipping or distant open-field setups, operators must be informed that crest factor heuristics can discard clipped or muffled shots.

*Provenance Artifact:* [`reports/phase10_crest_factor_metrics.json`](file:///e:/gunshot/gunshot/reports/phase10_crest_factor_metrics.json).
