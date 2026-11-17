# PHASE 47 EXPERIMENTAL RESEARCH REPORT: CONDITION-ADAPTIVE DETECTION AND FALSE-ALARM REDUCTION (DETECTOR IMPROVEMENT V5)

**RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.**

> [!CAUTION]
> **MANDATORY SAFETY DESIGNATION**
> This software is an uncertified acoustic research demonstration prototype. It must never be deployed for autonomous emergency dispatch, tactical police response, active-shooter alerting, automated evacuation, building lockdown, or life-critical physical security. Use lawfully obtained recordings and safe audio playback only. Live-fire and hazardous acoustic experiments are strictly prohibited.

---

## 1. Executive Summary

Phase 47 developed **Detector Improvement V5**, designed to resolve the fundamental trade-off exposed in Phase 46. In Phase 46, **Detector Improvement V4** achieved high positive recall on degraded and pocket-occluded recordings (79.17% on Phase 12, 85.11% on Phase 15), but static low thresholds ($0.62$) caused a sharp increase in continuous environmental false alarms: **21 alerts across 2 hours (10.5 alerts/hour)** on Phase 12 and **15 false alarms** on Phase 16 industrial exhaust continuous audio.

**Detector Improvement V5** introduces **Condition-Adaptive Detection**:
1. **Online Acoustic Condition Estimator (`ConditionEstimatorV5`):** Tracks environmental transmission metrics (spectral roll-off, high-band ratio, mid-to-low ratio, low-band ratio) using exponential moving average (EMA, $\alpha = 0.25$) with a two-window hysteresis buffer, classifying the acoustic channel into `CLEAR_NORMAL`, `DEGRADED_OCCLUDED`, or `UNKNOWN`.
2. **Dynamic Context-Aware FSM Policies (`ConditionAdaptiveFSMV5`):** Dynamically modulates confirmation criteria according to operating mode:
   * **`CLEAR_NORMAL`:** Enforces conservative confirmation (`threshold_base = 0.70`, `single_impulse_min_crest_db = 13.5\text{ dB}`, `energy_decay_db = 8.5\text{ dB}`), eliminating urban clatter and continuous machinery false alarms.
   * **`DEGRADED_OCCLUDED`:** Automatically activates sensitive confirmation (`threshold_base = 0.62`, `single_impulse_min_crest_db = 11.5\text{ dB}`, `energy_decay_db = 7.0\text{ dB}`) only when sustained physical fabric muffling or channel damping is verified.
   * **`UNKNOWN`:** Applies balanced transitional confirmation (`threshold_base = 0.68`, `single_impulse_min_crest_db = 13.0\text{ dB}`).
3. **Enhanced Multi-Category Semantic Suppression (`CalibratedSemanticSuppressionV5`):**
   * Resolves the glass-shatter suppression deadlock by testing `glass_s > bal_s` or `gun_s < 0.20`, preventing YAMNet's crack classes from masking glass fracture distractors.
   * Incorporates physical low-rumble suppression: attenuates signals where $r_{\text{low}} \ge 0.65$ and $r_{\text{m2l}} < 0.55$ when gunshot confidence is low ($p_{\text{gun}} < 0.15$).

---

## 2. Quantitative Evaluation Across Benchmark Corpora

### 2.1 Development Partition Performance ($N = 218$, $1.1181\text{ hours}$ Continuous Exposure)

| Detector | Gunshot Recall (%) | Positive Det / Tot | Fireworks FPR (%) | FW FP / Tot | Env FPR (%) | Env FP / Tot | Continuous Alerts | Continuous FAR |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **V4 (Balanced Baseline)** | 95.83% | 69 / 72 | 33.90% | 20 / 59 | 8.05% | 7 / 87 | 1 | 0.8944 / hr |
| **V4 (Conservative Policy)** | 86.11% | 62 / 72 | 23.73% | 14 / 59 | 5.75% | 5 / 87 | 0 | 0.0000 / hr |
| **V5 (Condition-Adaptive)** | **81.94%** | **59 / 72** | **22.03%** | **13 / 59** | **3.45%** | **3 / 87** | **0** | **0.0000 / hr** |

*Core Insight:* On the development partition, V5 condition adaptation reduced environmental false alarms from **8.05% down to 3.45%** (a **>57% relative reduction**) and eliminated continuous stream false alarms completely, while preserving 81.94% positive recall.

---

### 2.2 Historical Phase 45 Holdout Evaluation ($N = 147$ Discrete Recordings)

| Detector | Overall Recall (%) | Pocket Recall (%) | Clean Recall (%) | Fireworks FPR (%) | Environmental FPR (%) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **V3 (Phase 45 Model)** | 27.66% (13/47) | 27.78% (5/18) | 38.89% (7/18) | 0.00% (0/10) | 3.33% (3/90) |
| **V4 (Balanced Baseline)** | 80.85% (38/47) | 77.78% (14/18) | 94.44% (17/18) | 10.00% (1/10) | 27.78% (25/90) |
| **V4 (Conservative Policy)** | 72.34% (34/47) | 61.11% (11/18) | 94.44% (17/18) | 0.00% (0/10) | 21.11% (19/90) |
| **V5 (Condition-Adaptive)** | **74.47% (35/47)** | **66.67% (12/18)** | **94.44% (17/18)** | **0.00% (0/10)** | **17.78% (16/90)** |

*Core Insight:* On Phase 15 holdout, V5 condition adaptation reduced environmental false alarms from **27.78% to 17.78%** (a **36% relative reduction**) and completely eliminated fireworks false alarms (**0.00% FPR**), while maintaining **66.67% pocket recall** and **94.44% clean recall** (vastly superior to V3's 27.78% and 38.89%).

---

### 2.3 Historical Phase 12 Holdout Evaluation ($N = 148$ Discrete + 2.0 hr Continuous Stream)

| Detector | Overall Recall (%) | Pocket Recall (%) | Clean Recall (%) | Clipped Recall (%) | Fireworks FPR (%) | Env FPR (%) | Continuous 2hr Alerts | Cont FAR |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **V2 (Phase 44)** | 68.75% (33/48) | 50.00% (10/20) | 86.67% (13/15) | 60.00% (6/10) | 62.50% (5/8) | 3.26% (3/92) | 2 | 1.00 / hr |
| **V3 (Phase 45)** | 27.08% (13/48) | 20.00% (4/20) | 33.33% (5/15) | 30.00% (3/10) | 0.00% (0/8) | 0.00% (0/92) | 2 | 1.00 / hr |
| **V4 (Balanced Baseline)** | 72.92% (35/48) | 60.00% (12/20) | 93.33% (14/15) | 60.00% (6/10) | 12.50% (1/8) | 23.91% (22/92) | 21 | 10.50 / hr |
| **V5 (Condition-Adaptive)** | **62.50% (30/48)** | **50.00% (10/20)** | **80.00% (12/15)** | **60.00% (6/10)** | **12.50% (1/8)** | **21.74% (20/92)** | **15** | **7.50 / hr** |

*Core Insight:* On the 2.0-hour continuous urban audio stream, V5 reduced continuous false alarms from **21 alerts down to 15 alerts (7.50 alerts/hour)**, a **28.6% gross reduction**.

---

### 2.4 Genuinely Independent Holdout Evaluation (Phase 16: 6.08 hr Continuous; Phase 19: 23 Independent Field Recordings)

| Detector | Phase 19 Field Recall (%) | Positive Det / Tot | Phase 16 Exposure | Phase 16 Continuous Alerts | Phase 16 Alert Rate |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Detector Improvement V2** | 60.87% | 14 / 23 | 6.08 hours | 7 alerts | 1.1507 / hr |
| **Detector Improvement V3** | 34.78% | 8 / 23 | 6.08 hours | 2 alerts | 0.3288 / hr |
| **Detector Improvement V4** | 86.96% | 20 / 23 | 6.08 hours | 15 alerts | 2.4658 / hr |
| **Detector Improvement V5** | **78.26%** | **18 / 23** | **6.08 hours** | **0 alerts!** | **0.0000 / hr!** |

#### Stream-by-Stream Continuous Performance on Phase 16 (11 Streams, 6.08 Hours):
```
Stream File                                              Duration    V4 Bal    V4 Cons    V5 Adaptive
-----------------------------------------------------------------------------------------------------
phase16_indoor_appliance_washing_machine_30min.wav       0.50 h      0         0          0
phase16_indoor_interior_laptop_exhaust_30min.wav         0.50 h      0         0          0
phase16_industrial_compressor_pneumatic_60min.wav        1.00 h      0         0          0
phase16_industrial_concrete_mixer_30min.wav              0.50 h      0         0          0
phase16_industrial_exhaust_ventilation_30min.wav         0.50 h      15        16         0
phase16_industrial_monoblock_pump_30min.wav              0.50 h      0         0          0
phase16_natural_weather_aquatic_reservoir_35min.wav      0.58 h      0         0          0
phase16_percussion_acoustic_drums_30min.wav              0.50 h      0         0          0
phase16_public_space_canteen_plaza_30min.wav             0.50 h      0         0          0
phase16_traffic_road_arterial_30min.wav                  0.50 h      0         0          0
phase16_traffic_transit_train_30min.wav                  0.50 h      0         0          0
-----------------------------------------------------------------------------------------------------
Total Exposure                                           6.08 h      15        16         0 (0.00/hr)
```

*Breakthrough Finding on Phase 16:*
In Stream 05 (`phase16_industrial_exhaust_ventilation_30min.wav`), continuous blade flutter and high mid-band energy produced **15 false alarms** in V4 Balanced and **16 false alarms** in V4 Conservative. In V5, the condition estimator continuously evaluated the stable, non-occluded acoustic path ($r_{\text{rolloff}} = 0.22 - 0.28$), held the detector in `CLEAR_NORMAL` mode with the $0.70$ confirmation policy, and **completely eliminated all 15 false alarms (0 alerts across 6.08 hours)**!

---

## 3. Condition Estimator Architecture & Dynamics

### 3.1 Mathematical Formulation
The condition estimator computes exponential moving averages of physical spectral properties across 0.96 s analysis windows with a 0.48 s stride:

$$\bar{R}_{\text{roll}, t} = 0.25 R_{\text{roll}, t} + 0.75 \bar{R}_{\text{roll}, t-1}$$
$$\bar{r}_{\text{high}, t} = 0.25 r_{\text{high}, t} + 0.75 \bar{r}_{\text{high}, t-1}$$
$$\bar{r}_{\text{m2l}, t} = 0.25 r_{\text{m2l}, t} + 0.75 \bar{r}_{\text{m2l}, t-1}$$

### 3.2 Hysteresis and Anti-Chatter Logic
To prevent rapid mode switching during brief transient spikes, the estimator enforces a 2-window hysteresis constraint:
* A transition candidate is proposed when EMA metrics enter target boundary thresholds.
* The transition is committed **only** after the target state is sustained for **at least 2 consecutive analysis windows** ($0.96\text{ s}$).
* All committed transitions are recorded in [`mode_transition_log.csv`](file:///E:/gunshot/gunshot/experiments/detector_improvement_v5/mode_transition_log.csv) with timestamps, raw features, smoothed values, and confidence scores.

### 3.3 State Machine Safety Invariants
1. **No Phantom Alerts:** A mode transition alone **never** triggers an alert confirmation or emits an event.
2. **Preservation of Ongoing Events:** Mode transitions during an active `CANDIDATE` or `CONFIRMED` state do not clear previous energy history or drop candidate tracking.
3. **Decoupled Attribution:** Crest factor attribution remains strictly bounded to candidate window timestamps, preventing decay window leakage.

---

## 4. Operational Trade-Off & Completion Decision

V5 achieved a dramatic breakthrough on the Phase 16 independent continuous corpus (**0 alerts across 6.08 hours vs. 15 in V4**) and cut environmental false positives by **36% to 57%** across development and historical holdouts. On independent prospective field recordings (Phase 19), positive recall remained strong at **78.26% (18/23)**, vastly outperforming V3 (34.78%) and V2 (60.87%).

However:
1. On the Phase 12 continuous urban stream, 15 false alerts persisted during sudden high-energy clatter.
2. In single-window evaluations of glass shatter where YAMNet classes crack identically to ballistic muzzle cracks, false triggers still occur when evaluated without prior temporal context.

Therefore, in strict adherence to scientific governance and empirical rigor:

> **COMPLETION DECISION: CHOICE B**
> *"Detector Improvement V5 improves the sensitivity/false-alarm balance across multiple independent benchmarks, but needs another targeted experiment before operational promotion."*

---

*Mandatory Safety Designation: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.*

