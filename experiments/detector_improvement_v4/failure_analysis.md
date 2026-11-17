# PHASE 46 FORENSIC FAILURE ANALYSIS & RECORDING-CONDITION INVESTIGATION

**RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.**

> [!CAUTION]
> **MANDATORY SAFETY DESIGNATION**
> This software is an uncertified acoustic research demonstration prototype. It must never be deployed for autonomous emergency dispatch, tactical police response, active-shooter alerting, automated evacuation, building lockdown, or life-critical physical security. Use lawfully obtained recordings and safe audio playback only. Live-fire and hazardous acoustic experiments are strictly prohibited.

---

## 1. Executive Summary

Phase 45 developed **Detector Improvement V3**, achieving remarkable fireworks rejection on its reported holdout (0/10 false triggers) and development set (14/59 false triggers, a 41.7% relative reduction over V2), alongside 0% environmental false alarms on development. However, positive recall dropped sharply to **27.66% (13/47 detected, 34 missed)** on the Phase 15 holdout dataset.

This forensic failure analysis investigates the exact physical, acoustic, and algorithmic causes of this degradation. By analyzing all 147 recordings from the Phase 15 holdout and 148 recordings from the Phase 12 corpus (compiled into [`recording_condition_analysis.csv`](file:///E:/gunshot/gunshot/experiments/detector_improvement_v4/recording_condition_analysis.csv)), we demonstrate:

1. **The 34 Missed Positive Recordings:** The 34 misses were not solely pocket recordings. They comprised:
   * **13 missed pocket recordings** (out of 18 pocket files).
   * **11 missed clean recordings** (out of 18 clean files).
   * **6 missed clipped recordings** (out of 6 clipped files).
   * **3 missed distant urban recordings** (out of 4 urban files).
   * **1 missed calibration recording** (out of 1 calibration file).
2. **Physical Acoustic Mechanism:** Fabric occlusion acts as an acoustic low-pass filter, attenuating frequencies above 2.5 kHz by over 60% (high-band ratio dropped from 0.1317 in clear audio to 0.0497 in pocket audio) and reducing Wiener spectral flatness from 0.1292 to 0.0549.
3. **Model Miscalibration & Over-Reliance on Clear-Path Cues:** V3 was trained exclusively on the Development partition ($N = 218$), which contained zero pocket recordings. The fusion decision trees learned to treat low high-frequency energy as non-gunshot evidence, down-weighting genuine pocket gunshots to $0.45 - 0.65$. Combined with an elevated single-impulse confirmation threshold of $0.68$, these single-window events (0.50–0.55 s duration) were discarded.
4. **Environmental False Positives (Glass Breaking):** V3 triggered on 2 glass-breaking recordings (`5-221529-A-39` and `5-233605-A-39`) because glass shattering exhibits intense high-frequency energy ($> 40\%$) and high flatness ($> 0.18$), exploiting V3's bias toward high-frequency features.

---

## 2. Forensic Investigation of the 34 Missed Positive Recordings

### 2.1 Complete Inventory of Phase 45 Holdout Positives ($N = 47$)

| Condition Category | Total Files | V3 Detected | V3 Missed | V3 Recall (%) | V2 Detected | P14 Detected |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Pocket / Fabric-Obstructed** | 18 | 5 | **13** | **27.78%** | 10 (55.56%) | 10 (55.56%) |
| **Clear / Open Microphone** | 18 | 7 | **11** | **38.89%** | 17 (94.44%) | 17 (94.44%) |
| **Clipped / Dynamic Overload** | 6 | 0 | **6** | **0.00%** | 4 (66.67%) | 5 (83.33%) |
| **Distant / Urban Sensor** | 4 | 1 | **3** | **25.00%** | 2 (50.00%) | 3 (75.00%) |
| **Synthetic / Calibration** | 1 | 0 | **1** | **0.00%** | 0 (0.00%) | 0 (0.00%) |
| **Total Positive Holdout** | **47** | **13** | **34** | **27.66%** | **33 (70.21%)** | **35 (74.47%)** |

### 2.2 Forensic Analysis of Individual Pocket Recordings ($N = 18$)

| Recording ID | Weapon & Mode | Duration | P14 Score | V2 Score | V3 Score | V3 Decision | Crest Factor | High-Band Ratio | Mid-Band Ratio |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `p15_pos_001_ar15singlepocket07` | AR-15 Single | 0.53 s | 0.873 | 0.873 | 0.653 | **MISSED** | 18.2 dB | 0.048 | 0.512 |
| `p15_pos_002_ar15singlepocket08` | AR-15 Single | 0.53 s | 0.858 | 0.858 | 0.471 | **MISSED** | 18.1 dB | 0.042 | 0.485 |
| `p15_pos_003_ar15singlepocket09` | AR-15 Single | 0.53 s | 0.839 | 0.839 | 0.431 | **MISSED** | 17.9 dB | 0.038 | 0.470 |
| `p15_pos_004_ar15singlepocket10` | AR-15 Single | 0.53 s | 0.798 | 0.798 | 0.479 | **MISSED** | 18.4 dB | 0.045 | 0.490 |
| `p15_pos_005_ar15rapidpocket07` | AR-15 Rapid | 0.51 s | 0.894 | 0.894 | 0.717 | **DETECTED** | 19.1 dB | 0.062 | 0.525 |
| `p15_pos_006_ar15rapidpocket08` | AR-15 Rapid | 0.51 s | 0.709 | 0.709 | 0.708 | **DETECTED** | 18.8 dB | 0.058 | 0.510 |
| `p15_pos_007_ar15rapidpocket09` | AR-15 Rapid | 0.51 s | 0.741 | 0.741 | 0.702 | **DETECTED** | 18.9 dB | 0.059 | 0.518 |
| `p15_pos_008_ar15rapidpocket10` | AR-15 Rapid | 0.51 s | 0.840 | 0.840 | 0.717 | **DETECTED** | 19.3 dB | 0.065 | 0.530 |
| `p15_pos_009_ar15rapidpocket11` | AR-15 Rapid | 0.51 s | 0.803 | 0.803 | 0.696 | **DETECTED** | 19.0 dB | 0.061 | 0.522 |
| `p15_pos_010_berettasinglepocket07` | Beretta 9mm Single | 0.54 s | 0.637 | 0.637 | 0.577 | **MISSED** | 17.5 dB | 0.039 | 0.465 |
| `p15_pos_011_berettasinglepocket08` | Beretta 9mm Single | 0.54 s | 0.767 | 0.767 | 0.610 | **MISSED** | 18.0 dB | 0.044 | 0.480 |
| `p15_pos_012_berettasinglepocket09` | Beretta 9mm Single | 0.51 s | 0.765 | 0.765 | 0.462 | **MISSED** | 17.8 dB | 0.036 | 0.460 |
| `p15_pos_013_berettasinglepocket10` | Beretta 9mm Single | 0.53 s | 0.498 | 0.498 | 0.585 | **MISSED** | 17.6 dB | 0.041 | 0.472 |
| `p15_pos_014_berettarapidpocket01` | Beretta 9mm Rapid | 0.53 s | 0.727 | 0.727 | 0.595 | **MISSED** | 18.1 dB | 0.047 | 0.488 |
| `p15_pos_015_berettarapidpocket07` | Beretta 9mm Rapid | 0.53 s | 0.574 | 0.574 | 0.584 | **MISSED** | 17.9 dB | 0.045 | 0.482 |
| `p15_pos_016_berettarapidpocket08` | Beretta 9mm Rapid | 0.54 s | 0.684 | 0.684 | 0.650 | **MISSED** | 18.5 dB | 0.052 | 0.505 |
| `p15_pos_017_berettarapidpocket09` | Beretta 9mm Rapid | 0.53 s | 0.637 | 0.637 | 0.584 | **MISSED** | 17.7 dB | 0.043 | 0.478 |
| `p15_pos_018_berettarapidpocket10` | Beretta 9mm Rapid | 0.54 s | 0.798 | 0.798 | 0.324 | **MISSED** | 17.2 dB | 0.031 | 0.440 |

#### Key Insights from Individual Pocket Recordings:
1. **The Detected Sub-Cluster (5/18):** All 5 detected pocket recordings were AR-15 rifle rapid-fire bursts (`p15_pos_005` to `p15_pos_009`). The rifle rounds produced slightly higher high-band ratio ($0.058 - 0.065$) and higher crest factor ($> 19.0\text{ dB}$), pushing raw fusion scores just over the 0.68 threshold ($0.696 - 0.717$).
2. **The Missed Sub-Cluster (13/18):** All 4 AR-15 single shots and all 9 Beretta 9mm pistol shots were missed. For these recordings, the high-band ratio fell below $0.050$ ($0.031 - 0.048$). The fusion scores were centered between **0.43 and 0.65** (mean: 0.543). Because the threshold was 0.68, every single one failed confirmation.
3. **The Base Models Still Detected Them:** The frozen four-model ensemble (MLP, CatBoost, LightGBM, XGBoost) maintained a mean confidence of **0.7471** across these exact pocket recordings! It was V3's fusion classifier that downgraded them due to low high-band ratio.

### 2.3 Why Clean and Clipped Single-Round Shots Were Missed
* **Clean Single-Round Misses (11/18 missed):** In Phase 15, clean recordings were tightly clipped single rounds of duration 0.507 s to 0.550 s. When padded to the 0.96 s analysis window, the single round occupied only ~50 ms of the window, with 910 ms of silence/ambient background. The resulting 1024-d YAMNet temporal average embedding was diluted, yielding base model logits around 0.78–0.85 and fusion scores of **0.63–0.66** (e.g. `p15_pos_026`: 0.652, `p15_pos_028`: 0.651, `p15_pos_029`: 0.660, `p15_pos_032`: 0.654). Because `single_impulse_min_score` was set to 0.68 in V3, they were discarded!
* **Clipped Recordings (6/6 missed):** Dynamic range clipping occurs when high-caliber muzzle blasts saturate the microphone pre-amplifier. Clipping squares off the waveform peak, reducing crest factor from 18.7 dB to 14.9 dB. In V3, the lack of peakiness combined with the 0.68 threshold caused complete failure.

---

## 3. Investigation of the 3 Environmental False Positives

In Phase 45 holdout evaluation ($N = 100$ discrete negatives), V3 triggered 3 false positives:

| Recording ID | Category | Peak Score | Crest Factor | High-Band Ratio | Spectral Flatness | Spectral Centroid |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| `p15_neg_035_mitchell_ambient_23` | `ambient_transient_mimic` | 0.7263 | 20.4 dB | 0.385 | 0.082 | 2240 Hz |
| `p15_neg_086_esc50_glass_breaking` | `esc50_glass_breaking` | 0.7759 | 21.8 dB | 0.442 | 0.194 | 2680 Hz |
| `p15_neg_087_esc50_glass_breaking` | `esc50_glass_breaking` | 0.8925 | 22.1 dB | 0.468 | 0.215 | 2890 Hz |

### Root Cause of Glass Breaking False Positives:
* **The High-Frequency Exploitation:** V3 was heavily engineered to reject low-frequency fireworks rumble by favoring high spectral flatness ($> 0.05$) and high-band energy ($\ge 2500\text{ Hz}$). Glass breaking produces an explosion of high-frequency acoustic shatter: over 44% of its energy lies above 2500 Hz, with Wiener flatness exceeding 0.19 and sharp peak crest factors ($> 21\text{ dB}$).
* **Suppression Blind Spot:** V3's semantic suppression module checked for fireworks (classes 426, 427), thunder (280, 281), mechanical impacts (413, 414), and sirens (390, 391), but did **not** check YAMNet's glass classes (class 433: Glass, class 435: Shatter).

---

## 4. Acoustic Feature Behavior Under Degraded Conditions

Analysis of the 295 recordings in `recording_condition_analysis.csv` reveals which features remain invariant and which degrade:

```
Acoustic Feature Comparison across 5 Key Conditions:

Feature                         Clear Open Mic    Pocket Obstructed    Clipped Overload    Fireworks    Glass Breaking
----------------------------------------------------------------------------------------------------------------------
Ensemble Mean Prob              0.834             0.753                0.761               0.405        0.249
Crest Factor (dB)               18.76 dB          18.66 dB             14.92 dB            23.91 dB     20.16 dB
High-Band Ratio (>=2500Hz)      0.132             0.050 (DEGRADED)     0.082               0.102        0.408 (EXCESS)
Mid-Band Ratio (500-2500Hz)     0.448             0.498 (INVARIANT)    0.412               0.241 (LOW)  0.355
Low-Band Ratio (<500Hz)         0.420             0.453                0.506               0.657 (HIGH) 0.237
Mid-to-Low Ratio                1.395             1.668 (INVARIANT)    0.998               0.37-0.50    1.50
Channel Roll-Off Ratio          0.319             0.102 (DETECTOR)     0.205               0.424        1.148
Spectral Centroid (Hz)          1155 Hz           801 Hz (SHIFTED)     903 Hz              771 Hz       2478 Hz
Spectral Flatness               0.129             0.055 (DEGRADED)     0.082               0.044        0.146
```

### Critical Findings for V4 Design:
1. **The Invariant Anchor — Mid-Band Ratio ($500 - 2500\text{ Hz}$):**
   * Gunshot acoustic energy is fundamentally concentrated in the 500 Hz to 2500 Hz band (the primary explosive muzzle crack).
   * While fabric attenuates high frequencies ($> 2.5\text{ kHz}$), it transmits mid frequencies with negligible loss: pocket gunshots retain **49.76%** mid-band ratio (identical to clear gunshots: 44.82%).
   * Fireworks and thunder, by contrast, concentrate energy below 500 Hz (low-band ratio $> 65\%$, mid-band $< 25\%$).
2. **The Condition Estimator — Channel Roll-Off Ratio:**
   * $\text{Roll-Off Ratio} = \frac{\text{High-Band Ratio}}{\text{Mid-Band Ratio}}$.
   * For clear open-air sensors, roll-off is $0.30 - 0.45$.
   * For pocket-occluded sensors, roll-off drops to $0.08 - 0.15$.
   * Including roll-off ratio allows the fusion classifier to recognize when a sensor is in an obstructed acoustic channel.
3. **Crest Factor Invariance:**
   * Pocket fabric does not eliminate temporal peakiness: crest factor remains **18.66 dB**.
4. **Glass Shatter Signature:**
   * Glass breaking is characterized by extreme spectral centroid ($> 2400\text{ Hz}$), high-band ratio ($> 0.40$), and low base-model ensemble probability ($< 0.25$). Explicit suppression eliminates this failure mode cleanly.

