# Phase 15 False Negative & Missed Event Analysis

**Safety Designation: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.**

## 1. Executive Summary

This report examines every genuine gunshot event that was missed (False Negative) by frozen detectors during the blind independent discrete evaluation (Split C: 28 genuine gunshot events across 18 pocket-occluded, 6 clipped range, and 4 clean recordings).

---

## 2. Miss Rates Across Acoustic Regimes

| Detector Profile | Pocket Occluded (N=18) Misses | Clean Direct (N=4) Misses | Clipped Range (N=6) Misses | Total Misses (N=28) | Overall Blind Recall (%) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Phase 9 Baseline** | 8 | 0 | 1 | 9 | 67.86% |
| **Phase 13 Candidate** | 9 | 0 | 3 | 12 | 57.14% |
| **Phase 14 Balanced** | 8 | 0 | 1 | 9 | 67.86% |
| **Phase 14 High-Precision** | 12 | 1 | 4 | 17 | 39.29% |
| **Phase 14 High-Sensitivity** | 5 | 0 | 0 | 5 | 82.14% |

*(Note: Ground truth in Split C comprises unexamined Mitchell ballistic recordings; 14 clean recordings in Split B validation were kept separate).*

---

## 3. Forensic Analysis of Missed Events

### A. Pocket Occlusion Misses (Heavy Fabric Damping)
- **Acoustic Phenomenon:** When a firearm is fired from inside a pocket or bag, acoustic energy above 2.5–3.0 kHz is attenuated by 15–25 dB.
- **Crest Factor Attenuation:** Direct gunshots exhibit crest factors of 18–24 dB; inside denim or canvas, the crest factor drops to 9.5–13.2 dB.
- **Phase 14 Balanced Performance:** Detects 10 of 18 pocket shots (55.6% recall). The 8 missed shots had crest factors below 10.5 dB, falling below the single-window confirmation threshold.
- **High-Sensitivity Advantage:** Phase 14 High-Sensitivity lowers the minimum crest threshold to 10.5 dB and base threshold to 0.68, recovering 13 of 18 pocket shots (72.2% recall).

### B. Severe ADC Saturation / Clipped Range Misses
- **Acoustic Phenomenon:** Close-range recordings (e.g. `Ar15Rapid08-10`, `BerettaRapid08-10`) where the microphone pre-amplifier saturates completely (flat-topped waveform).
- **Harmonic Distortion:** ADC hard-clipping generates artificial square-wave harmonics across the entire spectrum. This distorts the mel-spectrogram patch seen by YAMNet, causing YAMNet embeddings to deviate from normal ballistic blast patterns.
- **Phase 14 Balanced Performance:** Detects 5 of 6 clipped range shots (83.3% recall). Phase 13 missed 3 of 6 because hard clipping artificially lowered the crest factor.

---

## 4. Key Takeaways

1. Pocket occlusion remains the single greatest vulnerability for single-microphone acoustic detectors.
2. Increasing sensitivity recovers 72.2% of pocket shots, but triples continuous false alerts.
3. Single-microphone thresholding cannot break this fundamental trade-off. Dual-sensor coherence or spatial beamforming is required for robust pocket detection.
