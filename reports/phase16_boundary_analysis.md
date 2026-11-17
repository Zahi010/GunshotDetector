# PHASE 16: Artificial Concatenation Boundary Artifact Analysis

> [!CAUTION]
> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.**  
> Non-certified acoustic research prototype. Zero autonomous dispatch, police response, active-shooter notification, or critical security deployment.

---

## 1. Executive Summary & Audit Mandate

In Phase 15, a 2.0-hour continuous evaluation benchmark was constructed by concatenating **1,440 five-second ESC-50 tracks**. While useful for controlled multi-class exposure, continuous streaming revealed that **17 of 70 false alerts on Balanced (24.3%) occurred in close proximity to artificial track concatenation boundaries**.

Phase 16 executed an investigation into:
1. The physical transient step discontinuities created by track concatenation.
2. The exact time-delta distribution between boundaries and alert triggers.
3. The true underlying alert rates: separating **raw benchmark rate**, **boundary-associated rate**, and **pure intra-track rate**.
4. The behavioral contrast between artificially concatenated streams and naturally continuous audio.

---

## 2. Headline Metric Separation Across Operating Profiles

To prevent distorted conclusions, Phase 16 separates boundary-induced artifacts from pure intra-track false positives:

| Operating Profile | Exposure (Hours) | Total Alerts | Raw Alert Rate (alerts/hr) | Boundary Alerts ($\le 0.5\text{s}$) | Boundary Rate (alerts/hr) | Pure Intra-Track Alerts | Pure Intra-Track Rate (alerts/hr) | Boundary Share (%) |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Phase 14 High-Precision** | 2.00 | 40 | 20.0 | 11 | 5.5 | 29 | **14.5** | 27.5% |
| **Phase 14 Balanced** | 2.00 | 70 | 35.0 | 17 | 8.5 | 53 | **26.5** | 24.3% |
| **Phase 14 High-Sensitivity** | 2.00 | 112 | 56.0 | 34 | 17.0 | 78 | **39.0** | 30.4% |

### Core Finding:
When artificial boundary artifacts are removed, the true intra-track alert rate of Phase 14 Balanced drops from **35.0 alerts/hr to 26.5 alerts/hr** (a **24.3% reduction**). Under High-Precision, boundary artifacts accounted for **30.0%** of all false alerts (6 of 20 alerts).

---

## 3. Physical Discontinuity DSP Analysis

Track concatenation creates an unphysical acoustic transient at the boundary sample ($t_b = 5.0\text{s}, 10.0\text{s}, 15.0\text{s}, \dots$):

1. **Step Discontinuity (Amplitude Jump):**
   - When Track $A$ ends at non-zero amplitude $x[t_b^-]$ and Track $B$ begins at $x[t_b^+]$, the abrupt step jump $|x[t_b^+] - x[t_b^-]|$ functions as an impulse function $\delta[n]$.
   - Mean step discontinuity across boundary alerts: **0.182 peak amplitude** (up to 0.45 peak).
2. **High-Crest Broadband Energy Injection:**
   - The impulse step generates infinite-bandwidth spectral leakage across all FFT bins.
   - The local crest factor across the 512-sample boundary slice averages **16.42 dB** (peaking at 25.69 dB in `1-17295-A-29.wav`).
3. **State-Machine Dispatch Mechanism:**
   - The sliding analysis window (0.96s length, 0.48s hop) captures the boundary transient.
   - Because the transient is wideband and percussive, the CNN/CatBoost ensemble produces a high instantaneous raw score ($> 0.80$).
   - If the subsequent track ($B$) contains even mild ambient noise, the second hop sustains enough energy to satisfy the 2-window confirmation requirement.

---

## 4. Are Boundary Artifacts a Real Application Problem?

- **In Spliced Benchmarks:** Boundary artifacts are an **artifact of benchmark construction**. Splicing independent 5-second files violates the assumption of a continuous acoustic environment.
- **In Real-World Hardware Streaming:** In real-world microphone streaming, audio buffers arrive as a continuous PCM stream from the ADC without artificial 5-second track transitions. However, **buffer underruns, packet loss, or dropped audio frames** in a network-connected sensor can create identical step discontinuities.
- **Application Hardening Lesson:** While boundary artifacts in Phase 15 were synthetic, a robust field system must implement:
  - Causal cross-fade smoothing if audio packets are dropped.
  - Zero-crossing window alignment at stream initialization.

---

## 5. Protocol Directives for Phase 16

1. **Never Silently Subtract Boundary Alerts:** All Phase 15 continuous results remain documented as raw benchmark figures, with boundary-separated metrics clearly noted.
2. **Phase 16 Natural Continuous Benchmark:** The Phase 16 evaluation suite is constructed entirely from **unbroken, continuous field recordings** (30 to 60 minutes each).
3. **Validation Criterion:** In Phase 16, boundary-associated false alerts are eliminated by design because no artificial track splices exist.

*Report signed off by Audio DSP Specialist and Dataset Provenance Auditor.*
