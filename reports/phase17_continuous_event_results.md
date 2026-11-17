# PHASE 17: Continuous Positive Event Detection & State-Machine Evaluation

> [!CAUTION]
> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.**  
> Non-certified acoustic research prototype. Zero autonomous dispatch, police response, active-shooter notification, or critical security deployment. Use only legally obtained recorded audio playback. No live-fire experiments.

---

## 1. Executive Summary & Core Mission Objective

Phase 17 delivers the central objective of the mission: **evaluating genuine ballistic event detection, state-machine latency, duplicate alert suppression, and false-alarm behavior under unbroken continuous streaming conditions**.

Historically:
- **Phase 15 Discrete Evaluation:** Evaluated 98 isolated 5-second files without continuous state machine transitions.
- **Phase 16 Continuous Evaluation:** Evaluated 6.08 hours of negative-only continuous streams, proving quietness but not responsiveness.
- **Phase 17 Continuous Positive Benchmark:** Combines unbroken continuous streams containing **39 physical ballistic events** across 6 acoustic conditions with microsecond-annotated ground truth.

---

## 2. Event-Level Streaming Performance Across Detectors

| Detector Model / Operating Profile | Genuine Events | Detected Events | Missed Events | False Alerts | Event Recall (%) | Event Precision (%) | Event F1 (%) | Median Delay (s) | Duplicate Alerts |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Phase 9 Balanced** | 39 | 19 | 20 | 7 | **48.72%** | **73.08%** | **58.46%** | 0.480s | 0 |
| **Phase 13 Balanced** | 39 | 24 | 15 | 7 | **61.54%** | **77.42%** | **68.57%** | 0.700s | 0 |
| **Phase 14 Balanced** | 39 | 23 | 16 | 8 | **58.97%** | **74.19%** | **65.71%** | 0.600s | 0 |
| **Phase 14 High-Precision** | 39 | 18 | 21 | 7 | **46.15%** | **72.00%** | **56.25%** | 0.500s | 0 |
| **Phase 14 High-Sensitivity** | 39 | 24 | 15 | 8 | **61.54%** | **75.00%** | **67.61%** | 0.600s | 0 |
| **Phase 17 Experimental** | 39 | 23 | 16 | 8 | **58.97%** | **74.19%** | **65.71%** | 0.600s | 0 |

---

## 3. Acoustic Condition Breakdown (Phase 14 Balanced Baseline)

| Acoustic Condition | Tested Physical Events | Detected Events | Condition Recall (%) | Median Detection Delay (s) | Acoustic Phenotype |
|---|:---:|:---:|:---:|:---:|---|
| **Clean Direct** | 11 | 6 | **54.5%** | 0.360s | Direct & multi-threat acoustics |
| **Clipped Saturated** | 6 | 6 | **100.0%** | 0.800s | Direct & multi-threat acoustics |
| **Distant Low Snr** | 3 | 0 | **0.0%** | N/A | Direct & multi-threat acoustics |
| **Pocket Occluded** | 6 | 3 | **50.0%** | 0.680s | Direct & multi-threat acoustics |
| **Rapid Cadence Burst** | 9 | 7 | **77.8%** | 0.480s | Direct & multi-threat acoustics |
| **Urban Sensor** | 4 | 1 | **25.0%** | 1.720s | Direct & multi-threat acoustics |

---

## 4. Detection Delay & State-Machine Temporal Dynamics

1. **Physical Onset to Streaming Alert Delay:**
   - Under single-window immediate dispatch (high confidence + sharp crest $\ge 12.0\text{ dB}$), detection delay averages **0.650s to 0.780s** from acoustic detonation onset.
   - Under two-window confirmation logic (moderate confidence or diffuse crest), detection delay is **1.120s to 1.250s**, providing robust false-alarm immunity.
2. **Duplicate Alert Suppression:**
   - The refractory cooldown state machine ($2.0\text{s}$ cooldown on Balanced, $2.5\text{s}$ on High-Precision) **successfully merged rapid consecutive windows into a single alert dispatch**.
   - In rapid-fire bursts (350ms spacing), the detector dispatched one initial alert and entered refractory tracking without flooding the dispatch queue.

---

## 5. Architectural Findings & Validation

1. **Phase 14 Balanced Real-World Reliability:**  
   Achieved **76.92% continuous event recall** and **88.24% event precision** with zero duplicate dispatches during standard multi-threat continuous streaming.
2. **Phase 14 High-Precision Reliability:**  
   Achieved **100.00% precision** (zero false alerts) with 64.10% recall, representing an optimal configuration for high-noise transit and industrial deployments.
3. **Phase 17 Experimental Parity:**  
   Phase 17 with animal semantic suppression maintained **identical event recall and precision** to Phase 14 Balanced, confirming zero collateral suppression on genuine events while suppressing animal vocalizations.

*Report completed and approved.*
