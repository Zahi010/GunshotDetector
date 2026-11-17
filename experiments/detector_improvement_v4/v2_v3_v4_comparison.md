# PHASE 46 COMPARATIVE BENCHMARK: DETECTOR IMPROVEMENT V2 VS. V3 VS. V4

**RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.**

> [!CAUTION]
> **MANDATORY SAFETY DESIGNATION**
> This software is an uncertified acoustic research demonstration prototype. It must never be deployed for autonomous emergency dispatch, tactical police response, active-shooter alerting, automated evacuation, building lockdown, or life-critical physical security. Use lawfully obtained recordings and safe audio playback only. Live-fire and hazardous acoustic experiments are strictly prohibited.

---

## 1. Executive Summary

Phase 46 evaluated **Detector Improvement V4** against prior generations (**Detector Improvement V2** from Phase 44 and **Detector Improvement V3** from Phase 45) across three rigorous empirical datasets:
1. **Development Partition ($N = 218$, $1.9710\text{ hours}$):** Baseline development corpus.
2. **Phase 45 Historical Holdout ($N = 147$ discrete):** Benchmark where V3 suffered acute recall collapse on pocket-worn recordings.
3. **Genuinely NEW Independent Holdout (Phase 12: $N = 148$ discrete + 2.0 hr continuous):** An untouched evaluation corpus featuring 48 positive gunshots (20 pocket-worn, 15 clean, 10 clipped, 3 urban) and 100 negatives.

### Core Empirical Findings:
* **Pocket-Occlusion Recovery:** V4 successfully resolved the pocket-muffled detection failure:
  * On Phase 45 holdout, pocket recall rose from **27.8% (V3)** to **77.8% (V4)** (+9 pocket gunshots recovered, exceeding the 70% aspirational goal!).
  * On Phase 12 new independent holdout, pocket recall tripled from **20.0% (V3)** to **60.0% (V4)**.
* **Overall Positive Detection:**
  * Phase 45 holdout overall recall rose from **27.7% (V3)** to **85.1% (V4)** (+27 gunshots recovered!).
  * Phase 12 holdout overall recall rose from **27.1% (V3)** to **79.2% (V4)**.
  * Development recall reached **97.22% (70/72)**.
* **Fireworks Discrimination:** V4 maintained strong pyrotechnic rejection:
  * Phase 45 holdout: **10.0% FPR (1/10)**.
  * Phase 12 holdout: **12.5% FPR (1/8)** (versus 62.5% for V2).
* **The Operational Trade-Off:** The relaxed confirmation threshold ($0.62$) and enhanced mid-band feature sensitivity allowed impulsive mechanical clatter and range impacts to trigger elevated false alarms in continuous background monitoring (continuous alert rate: **10.5 alerts/hour** on the Phase 12 urban continuous stream).
* **Completion Decision:** In adherence to rigorous scientific integrity, **Choice B** (*“V4 improves some conditions but needs another targeted experiment”*) is formally adopted.

---

## 2. Multi-Corpus Quantitative Comparison Matrix

### 2.1 Development Partition ($N = 218$, $1.9710\text{ hours}$)

| Detector | Gunshot Recall (%) | Gunshots Det / Tot | Fireworks FPR (%) | FW FP / Tot | Env FPR (%) | Env FP / Tot | Continuous Alerts | Continuous FAR |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Detector Improvement V2** | 62.50% | 45 / 72 | 40.68% | 24 / 59 | 2.53% | 2 / 79 | 3 | 2.68 / hr |
| **Detector Improvement V3** | 66.67% | 48 / 72 | 23.73% | 14 / 59 | 0.00% | 0 / 79 | 0 | 0.00 / hr |
| **Detector Improvement V4** | **97.22%** | **70 / 72** | **33.90%** | **20 / 59** | **7.59%** | **6 / 79** | **1** | **0.89 / hr** |

---

### 2.2 Historical Phase 45 Holdout Partition ($N = 147$ discrete)

| Detector | Overall Recall (%) | Pocket Recall (%) | Clean Recall (%) | Fireworks FPR (%) | Env FPR (%) | Net Missed Gunshots |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Detector Improvement V2** | 70.21% (33/47) | 55.56% (10/18) | 94.44% (17/18) | 40.00% (4/10) | 1.11% (1/90) | 14 / 47 missed |
| **Detector Improvement V3** | 27.66% (13/47) | 27.78% (5/18) | 38.89% (7/18) | 0.00% (0/10) | 3.33% (3/90) | **34 / 47 missed** |
| **Detector Improvement V4** | **85.11% (40/47)** | **77.78% (14/18)** | **94.44% (17/18)** | **10.00% (1/10)** | **18.89% (17/90)** | **Only 7 / 47 missed!** |

*Forensic Impact:* V4 recovered **27 of the 34 gunshots** missed by V3, including 9 pocket-occluded recordings and 10 clean single-round recordings, while maintaining 90% pyrotechnic rejection.

---

### 2.3 Genuinely NEW Independent Holdout Partition (Phase 12: $N = 148$ discrete + 2.0 hr continuous)

| Performance Dimension | Detector Improvement V2 | Detector Improvement V3 | Detector Improvement V4 | V4 Delta over V2 | V4 Delta over V3 |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Overall Positive Recall** | 68.75% (33/48) | 27.08% (13/48) | **79.17% (38/48)** | **+10.42% abs** | **+52.09% abs** |
| **Pocket-Occluded Recall** | 50.00% (10/20) | 20.00% (4/20) | **60.00% (12/20)** | **+10.00% abs** | **+40.00% abs** |
| **Clean Single-Round Recall**| 86.67% (13/15) | 33.33% (5/15) | **93.33% (14/15)** | **+6.66% abs** | **+60.00% abs** |
| **Clipped / Overload Recall**| 60.00% (6/10) | 30.00% (3/10) | **90.00% (9/10)** | **+30.00% abs** | **+60.00% abs** |
| **Distant Urban Recall** | 33.33% (1/3) | 33.33% (1/3) | **66.67% (2/3)** | **+33.34% abs** | **+33.34% abs** |
| **Fireworks False Positive Rate** | 62.50% (5/8) | 0.00% (0/8) | **12.50% (1/8)** | **-50.00% abs** | +12.50% abs |
| **Glass Break False Positives**| 0.00% (0/8) | 0.00% (0/8) | **25.00% (2/8)** | +25.00% abs | +25.00% abs |
| **Environmental Distractor FPR** | 3.26% (3/92) | 0.00% (0/92) | **11.96% (11/92)** | +8.70% abs | +11.96% abs |
| **Continuous 2hr Alerts** | 2 alerts (1.00 / hr) | 2 alerts (1.00 / hr) | **21 alerts (10.50 / hr)** | +9.50 / hr | +9.50 / hr |

---

## 3. Comprehensive Architectural Dimension Comparison

| Dimension | Detector Improvement V2 | Detector Improvement V3 | Detector Improvement V4 |
| :--- | :--- | :--- | :--- |
| **Feature Representation** | 1024-d YAMNet embeddings only. | 1024-d YAMNet embeddings + 5 physical DSP metrics (crest, flatness, high-band, low-band, centroid). | 1024-d YAMNet embeddings + 8 sub-band dynamic DSP metrics (crest, flatness, high-band, mid-band, low-band, mid/low ratio, roll-off ratio, centroid). |
| **Domain Adaptation** | None (evaluated only on frozen representations). | None (trained strictly on open-air development audio). | **Physically Plausible Acoustic Adaptation:** 2nd-order Butterworth low-pass filter (1400–1800 Hz) and dynamic range saturation during GroupKFold training. |
| **Classification Layer** | Arithmetic mean of 4 frozen base models (MLP, CatBoost, LightGBM, XGBoost). | Supervised `HistGradientBoostingClassifier` on 19 multi-modal features. | Supervised `HistGradientBoostingClassifier` on 26 multi-modal features with sub-band dynamics. |
| **Suppression Mechanisms** | Heuristic post-hoc score multiplier: `score * (1.0 - 0.45 * fw)`. | Calibrated multi-category suppression with Ballistic Shockwave Protection override. | Calibrated multi-category suppression with Ballistic Shockwave Protection + **Glass Shatter Gating**. |
| **State Machine Calibration**| Threshold: 0.75 / 0.88; Decay window crest attribution bug. | Threshold: 0.68 / 0.83; Candidate-bound crest attribution; Single impulse threshold: 0.68. | Threshold: 0.62 / 0.80; Candidate-bound crest attribution; Single impulse threshold: 0.62; Crest min: 11.5 dB. |
| **Processing Latency** | ~12.2 ms per 480 ms hop. | ~13.6 ms per 480 ms hop. | ~13.7 ms per 480 ms hop (<3.0% CPU utilization). |

---

## 4. Operational Trade-Off Analysis

### 4.1 The Triumph of Domain Adaptation (Pocket & Muffled Detection)
The primary objective of Phase 46 was to recover genuine gunshot detection under degraded and pocket-occluded recording conditions without forfeiting fireworks rejection.
* **The Mechanism:** By incorporating **Mid-Band Ratio ($500 - 2500\text{ Hz}$)** and **Channel Roll-Off Ratio**, and training the model on low-pass filtered audio, V4 learned that muffled gunshots retain intense mid-band energy and high crest factor even when high frequencies are absorbed by fabric.
* **The Proof:** Across both independent holdout corpora, pocket recall increased by **+40.0% to +50.0% absolute**, while clean recall reached **93.3% to 94.4%**. Fireworks false positives remained low (10.0% and 12.5%, compared to 40.0% and 62.5% for V2).

### 4.2 The Regression (Continuous Environmental Background False Alarms)
* When the confirmation threshold was realigned to $0.62$ and mid-band sensitivity was elevated to recover muffled impulses, environmental transients (such as heavy metal clatter on firing ranges, mechanical vehicle backfires, and percussive impacts) that possess moderate mid-band energy crossed the confirmation threshold.
* Consequently, on the Phase 12 urban continuous stream, false alerts rose to **10.5 alerts/hour**.

---

## 5. Formal Completion Decision

In accordance with Phase 46 directives, three completion paths were considered:

* **Choice A (Proceed to Live Dashboard Integration):** *Rejected.* While V4 represents a massive breakthrough in pocket-occluded gunshot recovery, its continuous alert rate on urban background streams (10.5 alerts/hr) exceeds acceptable operational limits for live integration.
* **Choice B (V4 Improves Some Conditions But Needs Another Targeted Experiment):** **FORMALLY ADOPTED.**
  * V4 demonstrated robust, verified improvements on pocket-obstructed and degraded recordings (pocket recall 77.8% on Phase 15, 60.0% on Phase 12; clean recall 94.4% and 93.3%; fireworks FPR suppressed to 10–12.5% vs. 40–62.5% in V2).
  * However, continuous environmental false alarms require another targeted experiment before live promotion.
  * Preserves Phase 14 Baseline as the dashboard default.
  * Preserves V2 and V3 as selectable experimental models in the UI.
  * Preserves V4 in its dedicated research branch [`experiments/detector_improvement_v4/`](file:///E:/gunshot/gunshot/experiments/detector_improvement_v4/).
* **Choice C (Reject V4):** *Rejected.* V4 solved the primary failure of Phase 45 and established the first domain-adapted acoustic feature architecture in the project, providing immense research value.

### Path Forward for Targeted Experiment (Phase 47):
Implement **Condition-Adaptive State Machine Gating**:
* Use the **Channel Roll-Off Ratio** as an active condition selector:
  * When $\text{Roll-Off} < 0.20$ (indicating an obstructed, fabric-muffled sensor): activate the condition-adapted profile (`threshold_base = 0.62`) to ensure full pocket gunshot sensitivity.
  * When $\text{Roll-Off} \ge 0.20$ (indicating an open, unobstructed environment): default to the high-precision profile (`threshold_base = 0.72`) to enforce zero continuous false alarms on background streams.

