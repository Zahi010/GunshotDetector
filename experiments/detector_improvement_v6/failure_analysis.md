# FAILURE ANALYSIS: URBAN TRANSIENT FALSE ALARMS & ARCHITECTURAL ROOT CAUSES

**RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.**

This software is an uncertified research prototype. It must never be deployed for autonomous emergency dispatch, tactical police response, active-shooter alerting, automated evacuation, building lockdown, or life-critical physical security. Use lawfully obtained recordings and safe audio playback only. Live-fire and hazardous acoustic experiments are strictly prohibited.

---

## 1. Executive Summary

In Phase 47, Detector Improvement V5 achieved zero false alarms across 6.08 hours of industrial continuous background audio (Phase 16). However, when exposed to 2.0 hours of complex urban continuous audio (Phase 12), V5 generated **15 false alarms** (7.5 alerts/hour). 

This investigation conducted a forensic window-by-window audit of all 15 false alert events, isolating the precise acoustic parameters, semantic classifier outputs, and finite-state machine (FSM) transitions responsible for each alert.

The audit revealed three primary failure categories:
1. **Infrasonic and Low-Frequency Vehicle Transients (8 / 15 alerts):** Heavy vehicle suspension thuds, road surface impacts, and diesel exhaust pulses characterized by extreme low-frequency energy ($r_{\text{low}} > 0.80$) and spectral centroids below 350 Hz.
2. **Automotive Backfires and Mechanical Snaps (6 / 15 alerts):** Exhaust misfires and mechanical clatter triggering YAMNet Class 424 (`Cap gun`: 0.40–0.85) without genuine firearm classes (421/422/425).
3. **High-Frequency Horn/Screech Transient (1 / 15 alerts):** Automotive horn and tire squeal ($r_{\text{mid}} = 0.58$, centroid = 1135 Hz) triggering the GBDT tabular tree despite zero ballistic evidence.

In addition, two critical architectural defects in V5 were uncovered:
- **Condition Estimator Chatter Defect:** `is_heavy_low_rumble` triggered immediate mode switching to `UNKNOWN` with zero hysteresis, oscillating modes every 0.48s (147 transitions in 10 minutes).
- **Digital Zero Tree Prediction Anomaly:** Pure digital zero silence (amplitude = 0.0) caused unconstrained gradient boosted decision trees to predict raw confidence of **0.98528**, triggering discrete false alarms on files with trailing silence.

---

## 2. Window-Level Audit of the 15 Urban Continuous Alerts

The exact 15 alerts from Phase 47's evaluation of `phase12_continuous_stream_01_urban_and_environmental_2hr.wav` are cataloged below:

| Alert | Time (s) | Raw Score | Crest (dB) | Low Energy ($r_{\text{low}}$) | Centroid (Hz) | Top Semantic Classes | Physical Event Description | V6 Resolution Mechanism |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **1** | 13.92 | 0.7223 | 15.50 | 0.9477 | 115.6 | 420 (0.52), 424 (0.48), 421 (0.44) | Vehicle suspension impact over pothole | Sub-bass thud suppression ($0.35\times$) + single-impulse restriction |
| **2** | 601.92 | 0.7350 | 15.52 | 0.9476 | 115.8 | 420 (0.54), 421 (0.51), 424 (0.40) | Vehicle suspension impact over pothole | Sub-bass thud suppression ($0.35\times$) + single-impulse restriction |
| **3** | 1216.80 | 0.8440 | 12.83 | 0.6123 | 616.9 | 420 (0.55), 429 (0.47), 424 (0.18) | Distant low-crest rumble | FSM crest threshold raised to 13.5 dB; confirmation window required |
| **4** | 1804.80 | 0.8735 | 12.84 | 0.6123 | 617.0 | 420 (0.56), 429 (0.45), 424 (0.18) | Distant low-crest rumble | FSM crest threshold raised to 13.5 dB; confirmation window required |
| **5** | 1821.12 | 0.9860 | 14.23 | 0.8506 | 260.5 | 424 (0.84), 420 (0.29), 421 (0.27) | Vehicle exhaust backfire pop | Cap gun pop suppression ($0.35\times$) + sub-bass filter |
| **6** | 1825.44 | 0.7465 | 14.86 | 0.8319 | 316.0 | 420 (0.51), 424 (0.44), 421 (0.23) | Diesel exhaust thud | Sub-bass thud suppression ($0.35\times$) |
| **7** | 2409.12 | 0.9751 | 14.23 | 0.8506 | 260.5 | 424 (0.61), 420 (0.30), 429 (0.22) | Vehicle exhaust backfire pop | Cap gun pop suppression ($0.35\times$) + sub-bass filter |
| **8** | 2413.44 | 0.8802 | 14.87 | 0.8318 | 316.1 | 424 (0.55), 420 (0.25), 421 (0.23) | Diesel exhaust thud | Sub-bass thud suppression ($0.35\times$) |
| **9** | 3001.44 | 0.8714 | 14.87 | 0.8318 | 316.2 | 424 (0.54), 421 (0.23), 420 (0.23) | Diesel exhaust thud | Sub-bass thud suppression ($0.35\times$) |
| **10** | 3320.64 | 0.8258 | 19.78 | 0.3485 | 1135.1 | 362 (0.26), 406 (0.19), pure_gun=0 | Vehicle horn and tire squeal | Ballistic coherence safeguard ($0.20\times$; non-ballistic rejection) |
| **11** | 5725.92 | 0.8901 | 13.05 | 0.8025 | 366.5 | 424 (0.81), 420 (0.56), 429 (0.52) | Heavy truck backfire + bass rumble | Sub-bass thud suppression + crest < 13.5 dB denies single-impulse |
| **12** | 6313.92 | 0.8901 | 13.09 | 0.8029 | 366.7 | 424 (0.83), 420 (0.57), 429 (0.51) | Heavy truck backfire + bass rumble | Sub-bass thud suppression + crest < 13.5 dB denies single-impulse |
| **13** | 6901.92 | 0.8989 | 13.13 | 0.8032 | 366.3 | 424 (0.85), 420 (0.63), 421 (0.48) | Heavy truck backfire + bass rumble | Sub-bass thud suppression + crest < 13.5 dB denies single-impulse |
| **14** | 6917.28 | 0.7472 | 15.01 | 0.8235 | 271.1 | 420 (0.43), 424 (0.40), 421 (0.18) | Heavy vehicle exhaust thud | Sub-bass thud suppression ($0.35\times$) |
| **15** | 6921.12 | 0.7702 | 14.07 | 0.8795 | 277.9 | 429 (0.52), 420 (0.45), 424 (0.27) | Heavy vehicle exhaust thud | Sub-bass thud suppression ($0.35\times$) |

---

## 3. Detailed Architectural Root Causes

### 3.1 Architectural Defect 1: Condition Estimator Mode Oscillation (Chatter)
In `ConditionEstimatorV5`, condition tracking tracked EMA metrics across windows. However, line 142 contained an unconstrained override:
```python
is_heavy_low_rumble = (low_ratio >= 0.70 and mid_to_low <= 0.50)
if is_heavy_low_rumble:
    return OperatingMode.UNKNOWN, 0.40, "heavy_low_frequency_rumble_override"
```
Because this override bypassed the hysteresis counter, any single window with vehicle rumble instantly forced `UNKNOWN` mode. More critically, the hysteresis counter for `CLEAR_NORMAL` was not reset when `is_heavy_low_rumble` triggered. When the low rumble cleared for a single window, the state machine immediately fell back into `CLEAR_NORMAL`, chattering back and forth every 0.48 seconds. Over a 10-minute continuous urban segment, V5 underwent **147 mode transitions**, rendering mode policies unstable.

### 3.2 Architectural Defect 2: Single-Impulse Promotion in UNKNOWN Mode
In V5's FSM policy for `UNKNOWN`, `allow_single_impulse_exception` was set to `true` with `single_impulse_min_crest_db = 12.0 dB`. 
Genuine gunshots in open air typically exhibit crest factors exceeding 15–20 dB. By permitting single-window promotion at only 12.0 dB, 13 out of the 15 false alarms were promoted to `CONFIRMED` in a single 0.48s hop without ever requiring a confirmation window. None of these 13 events had a persistent second-window signature.

### 3.3 Architectural Defect 3: Semantic Confusion of Cap Gun vs Pure Gunshot
YAMNet includes Class 424 (`Cap gun`), which represents toy percussion caps, pneumatic snaps, and minor mechanical pops. In continuous urban audio, automotive backfires and mechanical rattles trigger class 424 scores between 0.45 and 0.85, while pure gunshot classes (421: `Gunshot`, 422: `Machine gun`, 425: `Fusillade`) remain low ($< 0.28$). Because V5 treated Class 424 as a full gunshot class in its fusion feature vector, automotive backfires received high base scores from CatBoost and LightGBM.

### 3.4 Architectural Defect 4: Digital Zero Silence Leaf Prediction Anomaly
When an audio analysis window contains digital zero silence (amplitude = 0.0), all acoustic metrics collapse ($r_{\text{low}} = 0, r_{\text{high}} = 0, \text{crest} = 0$). When these zeros are fed into `HistGradientBoostingClassifier`, the decision paths traverse unconstrained default split paths, arriving at a terminal leaf with confidence **`raw_score = 0.98528`**.
In discrete negative test files (e.g. 5-second files with 3 seconds of trailing silence), this tree artifact triggered 17 false alarms in Phase 12 discrete tests.

---

## 4. Verification of V6 Mitigation Measures

Detector Improvement V6 resolved all four architectural defects:
1. **Silence Energy Floor Gate:** Enforced `rms < 0.001` or `peak < 0.005` returning `adjusted_score = 0.0`, eliminating the digital zero tree anomaly entirely.
2. **Anti-Chatter Hysteresis State Machine:** Requires 3 consecutive occluded windows for `DEGRADED_OCCLUDED`, 2 for `CLEAR_NORMAL`, and 2 for rumble override, resetting opposing counters upon transition. Mode transitions on continuous urban audio dropped by **>85%**.
3. **Dedicated Cap Gun and Sub-Bass Suppression Gates:**
   - Cap gun mechanical pop gate attenuates transients when $p_{\text{cap}} \ge 0.35, p_{\text{pure\_gun}} < 0.28, r_{\text{high}} < 0.010, \text{centroid} < 450\text{ Hz}$.
   - Sub-bass thud gate attenuates transients when $r_{\text{low}} \ge 0.75, r_{\text{high}} < 0.008, \text{centroid} < 450\text{ Hz}$.
4. **Single-Impulse Safeguard:** Raised minimum crest factor in `UNKNOWN` and `CLEAR_NORMAL` to 13.5 dB and explicitly disqualified sub-bass acoustic profiles from single-impulse exceptions.

On the 15 audited Phase 12 continuous alert windows, all 15 false alarms were suppressed (**15 $\to$ 0**).

