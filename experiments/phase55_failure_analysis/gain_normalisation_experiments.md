# Phase 55 — Diagnostic Gain Normalization Experimental Report

**MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.**

*This uncertified research prototype must never be deployed for autonomous emergency dispatch, tactical police response, active-shooter alerting, automated evacuation, building lockdown, or life-critical physical security.*

---

## 1. Executive Summary

In Phase 54 independent testing, 39 out of 134 positive gunshots were missed (70.90% recall). Forensic analysis revealed that **38.5% (15/39) of missed gunshots suffered from low recording gain** (peak amplitude $< 0.15$ or RMS $< -28\text{ dBFS}$), which dampened crest factor and prevented single-impulse ballistic confirmation in V10's finite state machine.

To determine whether pre-inference gain normalization or dynamic range expansion could safely recover these missed gunshots without modifying V10, a controlled diagnostic experiment was conducted across:
1. **The 39 False Negatives:** Tested to measure positive gunshot recovery.
2. **The 169 True Negatives:** Tested to measure false-alarm inflation on challenge negatives that V10 previously rejected.

---

## 2. Experimental Methodology & Evaluated Normalization Strategies

Four gain adjustment strategies were tested against the unnormalized baseline:

1. **Baseline (Unnormalized):** Original 16 kHz mono waveform as ingested during Phase 54.
2. **Peak Normalization (0.95):** Waveform scaled to peak amplitude of $0.95$ ($-0.45\text{ dBFS}$).
3. **Peak Normalization (0.70):** Waveform scaled to peak amplitude of $0.707$ ($-3.0\text{ dBFS}$).
4. **RMS Target Normalization (-20 dBFS):** Target RMS energy normalized to $-20\text{ dBFS}$ with a peak-limiting ceiling at $0.95$ to prevent digital clipping.
5. **Fixed Dynamic Boost (+6 dB):** Uniform $+6.0\text{ dB}$ linear gain boost with peak ceiling at $0.95$.

All audio processing was performed strictly in-memory without altering source files, using the frozen `DetectorImprovementV10` evaluation pipeline.

---

## 3. Empirical Results

### Summary Comparison Table

| Normalization Method | FNs Recovered ($N=39$) | FN Recovery (%) | Post-Gain Total Recall (%) | TN False Alarms Inflated ($N=169$) | TN Inflation Rate (%) | Post-Gain Total FPs ($N=217$) | Post-Gain Challenge FPR (%) | Net Gain Benefit ($\Delta TP - \Delta FP$) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Baseline (Original)** | **0** | **0.00%** | **70.90%** | **0** | **0.00%** | **48** | **22.12%** | **0** |
| **Peak Norm (0.95)** | 3 | 7.69% | 73.13% | 6 | 3.55% | 54 | 24.88% | **-3** |
| **Peak Norm (0.70)** | 3 | 7.69% | 73.13% | 9 | 5.33% | 57 | 26.27% | **-6** |
| **RMS Norm (-20 dBFS)** | 5 | 12.82% | 74.63% | 6 | 3.55% | 54 | 24.88% | **-1** |
| **Fixed Boost (+6 dB)** | 3 | 7.69% | 73.13% | 2 | 1.18% | 50 | 23.04% | **+1** |

---

## 4. Analysis of False Positive Inflation by Sub-Category

Evaluating the 169 True Negatives revealed that scaling up quiet audio signals amplifies subtle background transients and low-level room impacts, converting previously benign non-gunshot recordings into false alarms:

| Normalization Method | Inflated False Alarms ($N$) | Affected Sub-Categories and File Breakdown |
| :--- | :---: | :--- |
| **Peak Norm (0.95)** | 6 | `glass_breakage` (3), `heavy_door_slams` (1), `metal_hammer_impacts` (1), `bioacoustic_human_vocalizations` (1) |
| **Peak Norm (0.70)** | 9 | `glass_breakage` (4), `fireworks_pyrotechnics` (1), `heavy_door_slams` (1), `metal_hammer_impacts` (1), `thunder_rumbles` (1), `bioacoustic_human_vocalizations` (1) |
| **RMS Norm (-20 dBFS)** | 6 | `glass_breakage` (3), `heavy_door_slams` (1), `metal_hammer_impacts` (1), `bioacoustic_human_vocalizations` (1) |
| **Fixed Boost (+6 dB)** | 2 | `glass_breakage` (2) |

### Key Observations:
1. **Glass Shatter Fragility:** Quiet glassware clinks, bottle handling, and dropped utensils possess high spectral centroids ($> 3000\text{ Hz}$). When normalized, their elevated crest factor triggers single-impulse detection, inflating glass breakage false alarms by up to 4 files.
2. **Pyrotechnics and Mechanical Impacts:** Distant fireworks and slamming doors that had low baseline amplitude were boosted into the FSM's trigger zone, further degrading V10's already elevated challenge FPR.
3. **Negative Net Benefit:** In three out of four normalization schemes, the number of newly created false alarms exceeded the number of recovered gunshots (e.g., Peak Norm 0.95 recovered 3 gunshots but produced 6 new false alarms, yielding a net penalty of $-3$).

---

## 5. Technical Conclusion & Recommendation

1. **Reject Global Gain Normalization:** Global peak normalization or aggressive RMS leveling cannot be safely applied as a pre-processing step in the acoustic detection pipeline. It degrades overall system precision.
2. **Local Adaptive AGC with Transient Masking:** Rather than blind global gain scaling, future architectures should employ:
   - Dynamic noise floor tracking with high-pass rumble rejection ($< 40\text{ Hz}$).
   - Transient-preserving soft compression that limits crest factor amplification on high-frequency noise bursts.
   - Learned post-classifier rejection that inspects multi-dimensional features regardless of absolute signal level.

