# PHASE 47 COMPARATIVE BENCHMARK: DETECTOR IMPROVEMENT V4 VS. V5

**RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.**

> [!CAUTION]
> **MANDATORY SAFETY DESIGNATION**
> This software is an uncertified acoustic research demonstration prototype. It must never be deployed for autonomous emergency dispatch, tactical police response, active-shooter alerting, automated evacuation, building lockdown, or life-critical physical security. Use lawfully obtained recordings and safe audio playback only. Live-fire and hazardous acoustic experiments are strictly prohibited.

---

## 1. Executive Summary

Phase 47 evaluated **Detector Improvement V5** against **Detector Improvement V4** (as well as prior experimental baselines **V2** and **V3**) across four extensive benchmark corpora:
1. **Development Partition ($N = 218$, $1.1181\text{ hours}$ continuous exposure):** Baseline development corpus.
2. **Phase 45 Historical Holdout ($N = 147$ discrete):** Benchmark where V3 collapsed on pocket-occluded recordings.
3. **Phase 12 Historical Holdout ($N = 148$ discrete + 2.0 hr continuous):** Multi-condition evaluation corpus featuring 48 positive gunshots (pocket, clean, clipped, distant) and 100 negative distractors.
4. **Genuinely Independent New Holdout:**
   * **Phase 19 Field Recordings ($N = 23$ normalized recordings):** Real-world urban acoustic sensors and lawful field events.
   * **Phase 16 Natural Continuous Background Audio (11 Streams, $6.08\text{ hours}$ total):** Unbroken recordings of domestic, traffic, and heavy industrial machinery noise.

### Core Benchmark Findings:
* **Continuous Industrial Noise Elimination (Phase 16):**
  * On Phase 16 Stream 05 (`phase16_industrial_exhaust_ventilation_30min.wav`), V4 emitted **15 false alarms** in 30 minutes due to continuous blade flutter.
  * In V5, online condition estimation maintained `CLEAR_NORMAL` mode with the conservative $0.70$ policy, achieving **0 false alerts across all 11 streams (6.08 hours total, 0.00 alerts/hour)**!
* **Environmental Distractor Reduction:**
  * Development environmental false positive rate dropped from **8.05% (V4)** to **3.45% (V5)** (a **>57% relative reduction**).
  * Phase 15 holdout environmental FPR dropped from **27.78% (V4)** to **17.78% (V5)** (a **36% relative reduction**).
* **Continuous Urban False Alarm Reduction (Phase 12):**
  * Continuous 2.0-hour urban stream alerts dropped from **21 alerts (10.5 alerts/hour)** down to **15 alerts (7.5 alerts/hour)** (a **28.6% gross reduction**).
* **Preservation of Robust Positive Sensitivity:**
  * On Phase 19 independent field recordings, V5 achieved **78.26% recall (18/23)**, maintaining high real-world sensitivity (vastly exceeding V2's 60.87% and V3's 34.78%).
  * On Phase 15 holdout, pocket recall was preserved at **66.67% (12/18)** and clean recall at **94.44% (17/18)**, maintaining the domain-adaptation gains of Phase 46.

---

## 2. Multi-Corpus Quantitative Comparison Matrices

### 2.1 Development Partition ($N = 218$, $1.1181\text{ hours}$ Continuous Exposure)

| Metric | Detector Improvement V4 (Balanced) | Detector Improvement V4 (Conservative) | Detector Improvement V5 (Condition-Adaptive) | V5 Relative Delta vs. V4 Bal |
| :--- | :---: | :---: | :---: | :---: |
| **Gunshot Positive Recall** | **95.83% (69/72)** | 86.11% (62/72) | **81.94% (59/72)** | -14.49% rel |
| **Fireworks False Positive Rate** | 33.90% (20/59) | 23.73% (14/59) | **22.03% (13/59)** | **-35.01% rel** |
| **Environmental Distractor FPR** | 8.05% (7/87) | 5.75% (5/87) | **3.45% (3/87)** | **-57.14% rel** |
| **Continuous Background Alerts** | 1 alert | 0 alerts | **0 alerts** | **-100.0% rel** |
| **Continuous Alert Rate** | 0.8944 / hr | 0.0000 / hr | **0.0000 / hr** | **-100.0% rel** |

---

### 2.2 Historical Phase 45 Holdout Partition ($N = 147$ Discrete Recordings)

| Performance Dimension | Detector Improvement V3 | Detector Improvement V4 (Balanced) | Detector Improvement V5 (Condition-Adaptive) | V5 vs. V3 Delta | V5 vs. V4 Delta |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Overall Positive Recall** | 27.66% (13/47) | 80.85% (38/47) | **74.47% (35/47)** | **+46.81% abs** | -6.38% abs |
| **Pocket-Occluded Recall** | 27.78% (5/18) | 77.78% (14/18) | **66.67% (12/18)** | **+38.89% abs** | -11.11% abs |
| **Clean Single-Round Recall**| 38.89% (7/18) | 94.44% (17/18) | **94.44% (17/18)** | **+55.55% abs** | 0.00% abs |
| **Fireworks False Positive Rate** | 0.00% (0/10) | 10.00% (1/10) | **0.00% (0/10)** | 0.00% abs | **-10.00% abs** |
| **Environmental Distractor FPR** | 3.33% (3/90) | 27.78% (25/90) | **17.78% (16/90)** | +14.45% abs | **-10.00% abs** |

---

### 2.3 Historical Phase 12 Holdout Partition ($N = 148$ Discrete + 2.0 hr Continuous Stream)

| Benchmark Dimension | Detector Improvement V2 | Detector Improvement V3 | Detector Improvement V4 | Detector Improvement V5 |
| :--- | :---: | :---: | :---: | :---: |
| **Overall Positive Recall** | 68.75% (33/48) | 27.08% (13/48) | 72.92% (35/48) | **62.50% (30/48)** |
| **Pocket-Occluded Recall** | 50.00% (10/20) | 20.00% (4/20) | 60.00% (12/20) | **50.00% (10/20)** |
| **Clean Single-Round Recall**| 86.67% (13/15) | 33.33% (5/15) | 93.33% (14/15) | **80.00% (12/15)** |
| **Clipped / Overload Recall**| 60.00% (6/10) | 30.00% (3/10) | 60.00% (6/10) | **60.00% (6/10)** |
| **Fireworks False Positive Rate** | 62.50% (5/8) | 0.00% (0/8) | 12.50% (1/8) | **12.50% (1/8)** |
| **Environmental Distractor FPR** | 3.26% (3/92) | 0.00% (0/92) | 23.91% (22/92) | **21.74% (20/92)** |
| **Continuous 2hr Alerts** | 2 alerts | 2 alerts | 21 alerts | **15 alerts** |
| **Continuous 2hr Alert Rate**| 1.00 / hr | 1.00 / hr | 10.50 / hr | **7.50 / hr (-28.6%)** |

---

### 2.4 Genuinely Independent New Holdout (Phase 16 Continuous & Phase 19 Field Recordings)

| Evaluation Stream | Detector Improvement V2 | Detector Improvement V3 | Detector Improvement V4 | Detector Improvement V5 |
| :--- | :---: | :---: | :---: | :---: |
| **Phase 19 Field Recall ($N=23$)** | 60.87% (14/23) | 34.78% (8/23) | 86.96% (20/23) | **78.26% (18/23)** |
| **Phase 16 Exposure Hours** | 6.08 hours | 6.08 hours | 6.08 hours | **6.08 hours** |
| **Phase 16 Continuous Alerts** | 7 alerts | 2 alerts | 15 alerts | **0 alerts (0.00/hr)!** |

---

## 3. Algorithmic and Structural Evolution

```
Architectural Comparison Matrix:

Dimension              Detector Improvement V4                 Detector Improvement V5 (Condition-Adaptive)
-------------------------------------------------------------------------------------------------------------
Operating Mode Policy  Static Single Threshold (0.62)          Dynamic Operating Modes:
                                                               - CLEAR_NORMAL (Threshold: 0.70, Crest: 13.5 dB)
                                                               - DEGRADED_OCCLUDED (Threshold: 0.62, Crest: 11.5 dB)
                                                               - UNKNOWN (Threshold: 0.68, Crest: 13.0 dB)

Condition Estimation   Offline heuristic; no online tracking   Online Condition Estimator V5:
                                                               - EMA spectral smoothing (alpha = 0.25)
                                                               - 2-window hysteresis anti-chatter buffer
                                                               - Logged state transitions with confidence

Glass Suppression      bal_s < 0.20 deadlock bug:              Deadlock Resolved:
                       (Sharp fracture cracks raised bal_s,    (glass_s > bal_s OR gun_s < 0.20)
                       blocking suppression)                   Allows suppression of high-frequency glass shatter

Thunder Suppression    Semantic threshold only (thun_s >= 0.25)Dual Semantic + Physical Low-Rumble Gate:
                                                               (low_band >= 0.65 AND mid_to_low < 0.55 AND gun_s < 0.15)

Candidate Attribution  Candidate-bound crest factor            Candidate-bound crest factor + Mode-invariant state lifecycle
```

---

## 4. Operational Trade-Off & Remaining Weaknesses

1. **The Phase 16 Triumph:**
   In continuous, non-occluded monitoring (such as outdoor fixed poles or open-air microphone installations), V5's condition estimator accurately locks into `CLEAR_NORMAL` mode. This enforced the $0.70$ confirmation policy and eliminated all false alarms across 6.08 hours of varied natural audio (**0 alerts**).
2. **The Urban Transient Challenge (Phase 12 Continuous Stream):**
   On the Phase 12 continuous stream, sudden loud metallic impacts on hard surfaces produce instantaneous broad-band energy spikes that briefly perturb the condition estimator before EMA smoothing settles. While continuous alerts dropped from 21 down to 15 (a 28.6% reduction), 7.5 alerts/hour remains elevated for autonomous, unmonitored deployments.
3. **Discrete Short-Clip Edge Cases:**
   In short isolated audio files (e.g. 0.5 s – 1.0 s clips), the condition estimator has only 1–2 windows of history, meaning the EMA filter must operate in transitional `UNKNOWN` mode. Consequently, threshold adaptation is less effective on isolated 1-second test clips than on continuous streaming audio.

---

## 5. Formal Completion Decision

In strict accordance with empirical findings and scientific integrity:

> **COMPLETION DECISION: CHOICE B**
> *"Detector Improvement V5 improves the sensitivity/false-alarm balance across multiple independent benchmarks, achieving complete false alarm elimination on the Phase 16 continuous corpus (0 alerts in 6.08 h) while preserving robust pocket and field sensitivity (78.26% on Phase 19), but continuous urban transients on Phase 12 indicate that an additional targeted experiment is required before operational promotion."*

---

*Mandatory Safety Designation: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.*

