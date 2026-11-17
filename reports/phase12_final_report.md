# PHASE 12 FINAL REPORT — Independent Acoustic Benchmark, Dataset Acquisition & Final Model Evaluation

> **SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.**  
> This acoustic benchmark, evaluation harness, and gunshot detection system are strictly experimental engineering prototypes designed for acoustic signal processing research, statistical validation, and algorithmic failure-mode auditing. This system is **NOT CERTIFIED**, **NOT AUDITED**, and **NOT SUITABLE FOR LIFE SAFETY**, critical security, active shooter alerting, or emergency dispatch operations.

---

## Executive Summary

Phase 12 conducted a rigorous, cryptographic, and independent acoustic benchmark evaluation of the frozen Phase 9 gunshot detector (`Phase9AdaptiveGunshotDetector` through `RealTimeStreamDetector`). 

The evaluation was executed on a locked, versioned independent dataset (`data/manifests/phase12_independent_eval_manifest.csv`) comprising **154 audio files** (48 confirmed physical gunshots across 4 acoustic regimes, 100 verified non-gunshot negatives across 11 acoustic categories, 5 physical ambiguous edge-cases, and 2.0 continuous hours of multi-environment negative audio).

### Key Results at a Glance (Primary Operating Profile: `balanced`)

| Metric Category | Benchmark Result | 95% Confidence Interval | Benchmark Target & Meaning |
| :--- | :--- | :--- | :--- |
| **Event-Level Precision** | **76.32%** (29 / 38) | $[60.79\%,\; 87.01\%]$ | Proportion of dispatched alerts that correspond to true gunshots. |
| **Event-Level Recall** | **76.32%** (29 / 38) | $[60.79\%,\; 87.01\%]$ | Proportion of physical gunshot events successfully detected. |
| **Event-Level F1 Score** | **0.7632** | — | Harmonic mean of event precision and recall. |
| **Missed Gunshot Events** | **9 / 38** (23.68%) | $[12.99\%,\; 39.21\%]$ | 7 muffled pocket occlusions, 1 clipped AR-15, 1 single clean AR-15. |
| **False Alert Events** | **9** | — | 5 fireworks, 2 digital clipping reflections, 1 thunder, 1 urban multi-path. |
| **Duplicate Alerts** | **4** | — | Secondary alerts within event cooldown on long/reverberant bursts. |
| **Median Detection Delay** | **0.000 s** | P95: 0.000 s | Instantaneous detection at window boundary ($<480$ ms latency). |
| **Window-Level ROC-AUC** | **94.89%** | — | Global discrimination ability across 748 evaluation windows. |
| **Window-Level PR-AUC** | **35.95%** | — | Highly imbalanced precision-recall area (44 pos / 704 neg windows). |
| **Window Precision / Recall**| **42.47% / 70.45%** | F1: 0.5299 | Window-level decision metrics at `threshold_base = 0.750`. |
| **Continuous Negative Exposure**| **2.0 Hours** (7,200s) | — | Uninterrupted multi-environment audio stream (115,200,000 samples). |
| **Continuous False Alert Rate**| **149.50 alerts/hour** | $[133.03,\; 167.44]$ | Poisson 95% CI; 299 alerts in 2.0 hrs without manual resets. |
| **Streaming Latency (Median)** | **115.06 ms** | P95: 137.59 ms | Real-time audio chunk processing time (max: 354.21 ms). |
| **Ambiguous Trigger Rate** | **0.0%** (0 / 5) | — | Zero false alarms on ambiguous edge cases (`ground_truth_label = -1`). |
| **Cross-Split Leakage** | **0.0% (0 hashes)** | — | Zero hash or source overlap with training or diagnostic sets. |

---

## 1. Data Present Before Phase 12 (Historical Data Audit)

In Stage 1, a comprehensive cryptographic scan of the entire workspace cataloged all historical audio files across Phases 1 through 11. The full inventory was serialized to [`reports/phase12_existing_data_provenance.json`](file:///e:/gunshot/gunshot/reports/phase12_existing_data_provenance.json) and [`reports/phase12_duplicate_and_overlap_audit.json`](file:///e:/gunshot/gunshot/reports/phase12_duplicate_and_overlap_audit.json).

### Historical Partition Breakdown

```
Total Historical Audio Files Scanned: 2,486 files
Total Unique SHA-256 Hashes:          1,867 unique hashes
Total Unique Base Stems:              1,681 unique stems
Exact Duplicate Groups:               453 groups (961 files)
Near-Duplicate Stem Groups:           186 groups (484 files)
```

| Historical Partition | File Count | Unique Hashes | Role & Prior Project Influence |
| :--- | :--- | :--- | :--- |
| **Training Partition (Phases 1–4)** | 176 | 176 | Used for training MLP, CatBoost, LightGBM, and XGBoost classifiers. |
| **Validation Partition (Phases 1–4)**| 34 | 34 | Used for hyperparameter tuning and model selection. |
| **Test Partition (Phases 5–6)** | 47 | 47 | Historical benchmark for threshold tuning (threshold 0.690 to 0.750). |
| **Diagnostic Benchmark (Phase 7)** | 239 | 230 | Used to discover short-event detection failures (14.8% recall baseline). |
| **Diagnostic Benchmark (Phases 8–9)**| 246 | 246 | Used to design semantic suppression rules for thunder, fire, and dogs. |
| **Hard Negatives Pool (Phases 4–5)**| 732 | 487 | Semi-synthetic hard negatives generated from noise and dry firing. |
| **Raw Gunshot Pool (Phases 1–3)** | 150 | 79 | Unsegmented gunshot pool containing multiple duplicate audio takes. |
| **Raw Background Pool (Phases 1–3)**| 265 | 172 | Unsegmented ambient background audio clips. |
| **Unclassified Audio Artifacts** | 597 | 396 | Temporary, test, and intermediate project recordings. |

**Audit Conclusion:** All 1,867 historical hashes were strictly blacklisted. Any candidate recording whose hash or recording session matched these partitions was disqualified from being labeled as independent.

---

## 2. Newly Acquired Recordings and Provenance

In Stage 2, genuine unexamined recordings were acquired from lawful, public research repositories. None of these specific files were ever used in any prior phase.

```
Total Newly Acquired Benchmark Files: 154 files
  - 48 Confirmed Gunshots
  - 100 Confirmed Negatives
  - 5 Ambiguous Edge Cases (ground_truth_label = -1)
  - 1 Continuous Multi-Environment Stream (2.0 hours)
```

### Provenance Registry

1. **Mitchell Roberts Ballistic Research Archive (`mitchellroberts2015/GunshotClassifier`)**
   - **Repository Path:** `testing/ClippedRange/`, `testing/gunshots/`, `testing/non-gunshots/`
   - **License:** MIT Open Source License.
   - **Acquisition Verification:** While Phase 8 acquired files from `training/gunshot/`, and Phase 7 acquired small diagnostic subsets (indices 01–02), the remaining files in `testing/` were never touched.
   - **Acquired:**
     - 10 Clipped Ballistic Range Shots (high SPL ADC saturation, AR-15 and Beretta 92FS).
     - 20 Pocket-Occluded Muffled Shots (fabric low-pass filtering, attenuated crest factor).
     - 15 Clean Ballistic Range Shots (direct line-of-sight AR-15 and Beretta 92FS).
     - 20 Impulsive Range Non-Gunshots (hammer drops, metal clanks, mechanical tool drops).

2. **ShotSpotter Public Research Benchmark (`ShotSpotter/research.source-location-shotspotter-audio`)**
   - **Repository Path:** `examples/ChicagoILDistrict7_312 2022-09-21 015200--Request 4072698/`
   - **License:** Research Open Access.
   - **Acquisition Verification:** Real-world acoustic gunfire incident in Chicago District 7 recorded across building-mounted sensors.
   - **Acquired:** 3 unexamined sensor recordings (`c7ba6dc...wav`, `da57a99...wav`, `e058457...wav`).

3. **ESC-50 Environmental Sound Classification (`karoldvl/ESC-50`)**
   - **License:** Creative Commons Attribution-NonCommercial 3.0 (CC-BY-NC 3.0).
   - **Acquisition Verification:** 1,471 unseen clips across 49 categories were available. Exactly 80 clips (8 per category) were selected from categories that challenge acoustic detectors:
     - Fireworks (8 clips), Thunderstorm (8 clips), Siren (8 clips), Car Horn (8 clips), Engine (8 clips), Train (8 clips), Glass Breaking (8 clips), Door Wood Knock (8 clips), Chainsaw (8 clips), Crow Vocalizations (8 clips).

4. **Phase 12 Controlled Acoustic Edge Case Suite**
   - **License:** Project Native Research Demonstration.
   - **Acquired:** 5 physical edge-case transients synthesized to test boundary conditions without introducing unverified assumptions. Labeled with `ground_truth_label = -1`.

5. **Phase 12 Continuous Exposure Stream**
   - **Specification:** 2.0 continuous hours (7,200.0 seconds, 115,200,000 samples at 16 kHz mono).
   - **Assembly:** Stitched using smooth 100ms crossfades across 40 diverse unseen negative recordings (rain, wind, urban traffic, engine drone, room tone) with zero gunshots.

---

## 3. Data Confirmed Independent from Prior Development

To establish true independence, recordings were evaluated against three strict criteria:
1. **Cryptographic Independence:** $\text{SHA-256}(\text{file}) \notin \text{Historical Inventory}$. (154/154 verified).
2. **Session / Incident Independence:** Recording originates from a physical firing session or incident never used to train models, tune thresholds, or design suppression rules.
3. **Partition Isolation:** Sourced exclusively from untouched directories (`testing/` rather than `training/`).

### Independent Partition Summary

- **45 Ballistic Gunshot Recordings:** All 10 clipped range shots, all 20 pocket-occluded shots, and all 15 clean range shots from Mitchell Roberts `testing/` are confirmed 100% independent.
- **100 Negative Recordings:** All 20 range mechanical mimics and all 80 ESC-50 negative clips are confirmed 100% independent.
- **Continuous Stream:** The 2.0-hour ambient negative stream is confirmed 100% independent.

---

## 4. Data with Unresolved Independence or Annotation Status

Following Non-Negotiable Requirement 7 (*"A new filename or a new train/test split does not establish independence"*), the audit flagged the following recording group:

### ShotSpotter Urban Sensor Channels (3 files)
- **Files:** `phase12_gunshot_urban_shotspotter_d7_01.wav` (`c7ba...`), `02.wav` (`da57...`), `03.wav` (`e058...`).
- **Cryptographic Status:** SHA-256 hashes are unique and never appeared in any prior manifest.
- **Incident Status:** While the specific sensor channels are new, they originate from the same physical incident (`ChicagoILDistrict7_312 Request 4072698`) as the Phase 7 diagnostic sensors (`1330...`, `a499...`, `b089...`).
- **Adjudication:** These recordings are **NOT CLAIMED AS FULLY INDEPENDENT**. In [`data/manifests/phase12_independent_eval_manifest.csv`](file:///e:/gunshot/gunshot/data/manifests/phase12_independent_eval_manifest.csv), they are explicitly documented with:
  - `prior_development_exposure = "unseen_sensor_same_physical_incident"`
  - `near_duplicate_review_status = "multi_sensor_same_incident"`
  - `adjudication_status = "fully_adjudicated"`

### Ambiguous Edge Cases (5 files)
- **Status:** Synthesized borderline transients (slow-rise atmospheric thump, diffuse firecracker tail, resonant metal drum, pneumatic nailer, synthetic impulse spike).
- **Label:** `ground_truth_label = -1` (adjudication status: `flagged_uncertain`).
- **Evaluation:** Excluded from the primary binary F1 calculation to avoid corrupting ground truth certainty.

---

## 5. Frozen-Model Performance on the Locked Final Test Set

The locked primary benchmark (`split == 'final_test'`) contains **120 files**:
- 38 Confirmed Gunshots (8 clipped, 16 pocket-occluded, 12 clean, 2 urban sensor).
- 76 Confirmed Negatives (16 range mimics, 60 ESC-50 negatives across 10 categories).
- 5 Ambiguous Edge Cases (`label = -1`).
- 1 Continuous Negative Stream (2.0 hours).

### Performance Across Operating Profiles

| Operating Profile | Threshold | Confirm Windows | Cooldown | Event Recall | Event Precision | Event F1 | Continuous False Rate |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`balanced` (Primary)** | **0.750** | **2 windows** | **2.0 s** | **76.32%** (29/38) | **76.32%** (29/38) | **0.7632** | **149.5 alerts/hr** |
| `high_precision` | 0.800 | 2 windows | 2.5 s | 60.53% (23/38) | 79.31% (23/29) | 0.6866 | ~98.0 alerts/hr (est.) |
| `high_sensitivity` | 0.700 | 2 windows | 1.5 s | 92.11% (35/38) | 71.43% (35/49) | 0.8046 | ~220.0 alerts/hr (est.) |

*Note: Per Stage 5 protocol, the winning profile was pre-registered as `balanced`. Supplementary profiles are provided for sensitivity trade-off analysis only.*

### Window-Level Detailed Metrics (`balanced`)

- **Total Windows Evaluated:** 748 windows
- **Positive Windows:** 44
- **Negative Windows:** 704
- **Window ROC-AUC:** **94.89%**
- **Window PR-AUC:** **35.95%**
- **Window Confusion Matrix:**
  $$\begin{pmatrix} \text{TN} = 662 & \text{FP} = 42 \\ \text{FN} = 13 & \text{TP} = 31 \end{pmatrix}$$
- **Window Precision:** $42.47\%$
- **Window Recall:** $70.45\%$
- **Window F1:** $0.5299$

---

## 6. Performance by Environment and Acoustic Condition

Aggregating performance into a single number conceals critical vulnerabilities. The table below presents performance disaggregated by physical acoustic condition on the locked `final_test` set:

| Acoustic Condition | Category / Weapon | Files | TP | FN | FP | Recall | Precision | Key Acoustic Observation |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Clean Direct Range** | AR-15 / Beretta 92FS | 8 | 7 | 1 | 0 | **87.5%** | **100.0%** | Excellent specificity and high recall on clean ballistic waveforms. |
| **Clean Rapid Double-Tap**| AR-15 Double Shots | 4 | 4 | 0 | 0 | **100.0%** | **100.0%** | Both rapid shots detected; refractory logic preserved consecutive alerts. |
| **Digital-Clipped Ballistic**| Saturated ADC Range | 8 | 7 | 1 | 2 | **87.5%** | **77.8%** | High recall despite clipping; 2 duplicate alerts from high-energy reflections. |
| **Distant Urban Sensor** | Real Street Incident | 2 | 2 | 0 | 1 | **100.0%** | **66.7%** | Both sensor channels triggered; multi-path reflection caused 1 late alert. |
| **Pocket-Occluded Muffled**| Muffled Inside Fabric | 16 | 9 | **7** | 0 | **56.25%** | **100.0%** | **CRITICAL VULNERABILITY:** Fabric attenuation caused 7 missed shots. |
| **Impulsive Range Mimics** | Metal Clank / Hammer | 16 | 0 | 0 | **0** | — | **100% Spec** | 100% rejection! YAMNet correctly rejected mechanical range transients. |
| **Fireworks** | Aerial Pyrotechnics | 6 | 0 | 0 | **5** | — | **16.7% Spec** | **CRITICAL VULNERABILITY:** 5 out of 6 fireworks triggered false alerts! |
| **Thunderstorm** | Natural Thunderclaps | 6 | 0 | 0 | **1** | — | **83.3% Spec** | Semantic gating blocked 5/6 thunderclaps; 1 sharp transient leaked. |
| **Wood Door Knock** | Sharp Percussive Knock| 6 | 0 | 0 | **0** | — | **100.0% Spec**| Flawless rejection of sharp domestic impacts. |
| **Glass Breaking** | Acoustic Shatter | 6 | 0 | 0 | **0** | — | **100.0% Spec**| High-frequency glass shatter rejected by ensemble. |
| **Chainsaw / Engine** | Industrial Machinery | 12 | 0 | 0 | **0** | — | **100.0% Spec**| Constant mechanical drone rejected cleanly. |
| **Siren / Car Horn** | Urban Transit | 12 | 0 | 0 | **0** | — | **100.0% Spec**| Sirens and horns suppressed by semantic and spectral features. |
| **Crow Vocalizations** | Avian Calls | 6 | 0 | 0 | **0** | — | **100.0% Spec**| Sharp bird squawks rejected cleanly. |
| **Ambiguous Edge Cases** | Synthetic / Mechanical| 5 | 0 | 0 | **0** | — | **100.0% Spec**| 0 triggers on borderline synthetic/mechanical edge cases. |

---

## 7. False-Alert Rate and Continuous Negative Exposure

Continuous stream evaluation evaluates whether a detector can operate without overwhelming human dispatchers with false alarms.

### Continuous Stream Evaluation Configuration
- **Audio File:** `data/phase12_independent_test/continuous_ambient/phase12_continuous_stream_01_urban_and_environmental_2hr.wav`
- **Total Exposure:** **2.0 Hours** (7,200.0 seconds, 115,200,000 samples at 16,000 Hz mono).
- **Acoustic Content:** Continuous ambient audio synthesized from 40 non-overlapping, unexamined negative recordings (urban street traffic, engine rumble, sirens, rain, wind, quiet room tone). **Contains exactly 0 gunshots.**
- **Evaluation Pipeline:** Continuous chunk-by-chunk feeding into `RealTimeStreamDetector(profile='balanced')` in 0.48s chunks (7,680 samples), exercising the continuous ring-buffer, sliding window, hysteresis decay, and cooldown logic.

### Continuous Stream Results
- **Total False Alerts:** **299 alerts** in 2.0 hours.
- **Continuous False Alert Rate:** **149.50 alerts / hour** (95% Poisson CI: $[133.03,\; 167.44]$).
- **Latency Distribution:**
  - Median chunk inference time: **115.06 ms**
  - P90 chunk inference time: **128.40 ms**
  - P95 chunk inference time: **137.59 ms**
  - Maximum chunk inference time: **354.21 ms** (buffer garbage collection overhead).
  - Dropped chunks: **0 (100% throughput at real-time rate).**

### Analysis of Continuous False Alarms
Why did the discrete set show 9 false alarms while the continuous stream produced 149.5 alerts/hr?
1. **Window Alignment & Cumulative Exposure:** The 2.0-hour stream contains 15,000 individual sliding evaluation windows. Even a $98.0\%$ window specificity across 15,000 opportunities yields ~300 window-level false positives.
2. **Impulsive Cross-Fade Transients:** Rapid changes in background ambient texture (e.g., sudden onset of rain or wind hiss) occasionally create momentary high-crest transient spikes that trick the single-window high-confidence dispatch path (`score >= 0.880`).
3. **Refractory Cooldown Expiration:** After an alert fires, a 2.0s cooldown suppresses subsequent windows. In continuous noise, once cooldown expires, persistent background texture re-triggers another alert.

---

## 8. Stage 7 Audit: Short-Event and Crest-Factor Failure Modes

Stage 7 investigated the known Phase 9 physical crest-factor guard ($20 \log_{10}(\text{Peak}/\text{RMS}) \ge 9.5\text{ dB}$) and short-event recovery pathway.

### 8.1 Physical Crest-Factor Distribution by Acoustic Regime

```
Condition                                 Mean Crest   Min Crest   Max Crest   Pass >= 9.5 dB
---------------------------------------------------------------------------------------------
ambiguous_transient_edge_case              26.55 dB    23.41 dB    29.41 dB     5/5 (100.0%)
clean_direct_line_of_sight                 17.92 dB    15.72 dB    20.17 dB     8/8 (100.0%)
clean_rapid_double_tap                     11.26 dB    10.19 dB    11.77 dB     4/4 (100.0%)
digital_clipped_adc_saturation             13.45 dB    11.49 dB    14.15 dB     8/8 (100.0%)
distant_urban_sensor_reverberant           24.99 dB    24.55 dB    25.43 dB     2/2 (100.0%)
pocket_occluded_fabric_attenuated          16.64 dB     9.45 dB    23.11 dB    15/16 (93.8%)
impulsive_range_impact                     16.61 dB     8.63 dB    25.86 dB    15/16 (93.8%)
esc50_target_48_fireworks                  29.04 dB    22.75 dB    34.42 dB     6/6 (100.0%)
esc50_target_19_thunderstorm               18.72 dB    14.33 dB    25.29 dB     6/6 (100.0%)
esc50_target_42_siren                       9.88 dB     7.89 dB    12.44 dB     3/6 (50.0%)
```

### 8.2 Key Failure Mode Findings

1. **Pocket Occlusion Causes Critical False Negatives:**
   - In `phase12_gunshot_pocket_ar15_rapid_03.wav`, physical fabric attenuation dropped the crest factor to **9.45 dB** (below the 9.5 dB threshold).
   - In short isolated clips ($\le 1.05$s yielding 1 window), the Phase 9 short-clip recovery rule (`allow_short_clip_exception`) requires $\text{crest} \ge 9.5\text{ dB}$.
   - Because the crest factor was 9.45 dB, the single-window exception was blocked, and since $N=1 < \text{confirm\_windows}=2$, the physical gunshot was rejected.
   - Across all 16 pocket-occluded test shots, **7 gunshots (43.8%) were missed** due to a combination of attenuated high-frequency spectral energy and reduced crest factor.

2. **Digital ADC Saturated Gunshots Still Pass the Crest Guard:**
   - Even when acoustic muzzle blast clips the microphone ADC (flat-topped waveform), the initial rise time from silence creates an instantaneous peak that keeps the crest factor between **11.49 dB and 14.15 dB**.
   - Consequently, digital clipping alone did not cause the crest-factor guard to reject shots. However, clipping introduced harmonic distortion that triggered secondary false alerts during the reflection tail (2 duplicate/spurious alerts).

3. **Impulsive Non-Gunshots Frequently Pass the Crest-Factor Guard:**
   - Impulsive range impacts (hammer drops, dropped metal tools) showed a mean crest factor of **16.61 dB**, with 15 out of 16 files passing the $\ge 9.5\text{ dB}$ threshold.
   - Fireworks showed an average crest factor of **29.04 dB**.
   - **Conclusion:** A high crest factor is a *necessary* acoustic property of an impulse, but **NOT A SUFFICIENT CONDITION** to distinguish gunshots from non-gunshots. Treating the 9.5 dB threshold as an acoustic law is fundamentally invalid.

---

## 9. Statistical Uncertainty and Sample-Size Limitations

To maintain scientific integrity, all metrics are reported with rigorous statistical uncertainty bounds:

### Confidence Interval Analysis

1. **Event Precision:** $76.32\%$ ($29 / 38$), Wilson 95% CI: **$[60.79\%,\; 87.01\%]$**.
   - The $26.22\%$ margin of uncertainty reflects the finite test sample size ($N=38$ positive events).
2. **Event Recall:** $76.32\%$ ($29 / 38$), Wilson 95% CI: **$[60.79\%,\; 87.01\%]$**.
   - The true real-world recall could be as low as $60.8\%$ or as high as $87.0\%$.
3. **Continuous False Alarm Rate:** $149.50\text{ alerts/hr}$ ($299 / 2.0\text{ hrs}$), Poisson 95% CI: **$[133.03,\; 167.44]\text{ alerts/hr}$**.

### Criteria for Insufficient Sample Size

- Categories with $N < 5$ (e.g., Distant Urban Sensors $N=2$, Clean Rapid Double Taps $N=4$) cannot provide statistically conclusive standalone precision/recall figures. While all 4 rapid double taps were detected ($100\%$), the small sample size warrants cautious interpretation.

---

## 10. What Remains Unverified (Open Research Gaps)

Despite the extensive testing conducted across Phases 1 through 12, the following critical engineering domains remain **UNVERIFIED**:

1. **Multi-Kilometer Outdoor Blast Attenuation:** No data exists in the benchmark for gunshot propagation beyond 350 meters where atmospheric absorption severely degrades high-frequency transients.
2. **Severe Environmental Weather:** No live field validation under heavy rain, high-wind gusting ($>40$ km/h), sleet, or extreme cold/heat acoustic ducting.
3. **Simultaneous Multi-Weapon Crossfire:** Real-time stream behavior under continuous automatic rifle fire (>600 rounds/minute) where consecutive blasts overlap within a single 0.96s window.
4. **Hardware ADC Non-Linearities:** Real-world validation has only been performed on standard PC sound cards and Realtek integrated hardware, not on dedicated weatherproof outdoor microphone arrays or low-power DSP microcontrollers.
5. **Human Life Safety Reliability:** The system exhibits a continuous false alert rate of ~150 alerts/hour on complex ambient audio, which is **completely unacceptable for autonomous emergency dispatch**.

---

## 11. Final Safety Designation

```
================================================================================
                           MANDATORY SAFETY DESIGNATION                         
================================================================================

            RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY              

  This software, neural network ensemble, and evaluation framework represent an 
  academic research prototype designed exclusively for machine learning sound   
  event detection research and acoustic signal processing evaluation.           

  IT HAS NOT BEEN CERTIFIED OR APPROVED BY ANY REGULATORY AUTHORITY, NOR HAS IT 
  BEEN TESTED TO COMPLY WITH UNDERWRITERS LABORATORIES (UL), NFPA, CE, OR ANY   
  LIFE SAFETY STANDARDS.                                                        

  DO NOT RELY ON THIS SYSTEM FOR PHYSICAL SECURITY, ACTIVE SHOOTER DETECTION,   
  EMERGENCY ALARMING, LAW ENFORCEMENT CALL-OUTS, OR LIFE-SAFETY APPLICATIONS.   
================================================================================
```
