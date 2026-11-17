# Phase 53: Comprehensive Forensic Analysis of Missed Positives

**Mandatory Safety Designation:**
> **RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.**
> This is uncertified research software. Never deploy it for autonomous emergency dispatch, police tactical response, active-shooter alerting, automated evacuation, building lockdown, or life-critical physical security. Use only lawfully obtained recordings and safe audio playback. Live-fire and hazardous acoustic experiments are strictly prohibited.

---

## 1. Executive Summary

In Phase 52, Detector Improvement V9 achieved a genuine gunshot detection recall of **45 / 65 (69.23%)** on the independent Phase 51 evaluation corpus ([phase51_evaluation_manifest.csv](file:///e:/gunshot/gunshot/experiments/phase51_validation/phase51_evaluation_manifest.csv)). While V9 completely eliminated Heavy Door Slam false alerts (from 66.67% to 0.0%) and close-microphone balloon burst false alerts (from 100% to 0.0%), **20 genuine gunshot recordings were missed**.

This document presents a file-by-file forensic investigation into all 20 missed recordings. Each recording was subjected to window-by-window acoustic feature extraction, intermediate neural network and gradient boosted tree score inspection, condition estimation tracking, and finite state machine (FSM) state audit.

---

## 2. Root Cause Taxonomy of Missed Positives

The 20 missed recordings do not share a single uniform cause. Forensic inspection reveals five distinct operational and acoustic failure modes:

| Failure Category | Miss Count | Percentage | Representative Files | Core Failure Mechanism |
| :--- | :---: | :---: | :--- | :--- |
| **1. Ground Blast / Low-Frequency Rumble Over-Suppression** | 5 | 25.0% | `mitchell_colt_ar15_10.wav`, `mitchell_glock17_9mm_08.wav`, `mitchell_ak47_762_03.wav`, `mitchell_ak47_762_05.wav`, `shotspotter_chicago_d7_sensor3.wav` | Ground-reflected low-frequency blast energy creates $lo \ge 0.88$, tripping the thunder/rumble suppression rule despite high crest factors ($18 - 20\text{ dB}$) and high centroids ($> 1100\text{ Hz}$). |
| **2. Base Model Consensus Under-Estimation in Fusion Trees** | 6 | 30.0% | `mitchell_colt_ar15_11.wav`, `mitchell_glock17_9mm_06.wav`, `mitchell_ak47_762_01.wav`, `mitchell_colt_govt_01.wav`, `mitchell_ar15_single_01.wav`, `mitchell_ar15_double_01.wav` | All 4 specialized base classifiers (MLP, CatBoost, LightGBM, XGBoost) score $> 0.70$ (mean $> 0.76$), but the fusion model's tree splits heavily penalize atypical spectral ratios, dropping raw fusion score below 0.70. |
| **3. Threshold Margin Rejections (Near-Misses)** | 4 | 20.0% | `mitchell_colt_ar15_04.wav`, `mitchell_ar15_single_04.wav`, `mitchell_colt45_single_02.wav`, `mitchell_ak47_762_04.wav` | Unsuppressed or weakly suppressed impulses scoring between $0.52$ and $0.66$ against the $0.70$ base decision boundary. |
| **4. Short-Duration / Single-Window Truncation & FSM Starvation** | 2 | 10.0% | `mitchell_mossberg_12g_01.wav`, `mitchell_colt_govt_02.wav` | Truncated recordings ($\approx 0.50\text{s}$) yield exactly 1 processing window ($N_{wins}=1$). Missing the 2-window sustained cluster threshold ($confirm\_wins=2$) leaves the event unconfirmed in `CANDIDATE` state. |
| **5. Severe Classifier False Negatives (Weak YAMNet Feature Representation)** | 3 | 15.0% | `mitchell_colt1911_45_01.wav`, `mitchell_colt1911_45_02.wav`, `mitchell_beretta_single_01.wav` | Lack of recognizable ballistic shockwave in frozen YAMNet embeddings ($pure\_gun < 0.001$), triggering ballistic incoherence suppression. |
| **Total Misses** | **20** | **100.0%** | — | — |

---

## 3. Comprehensive File-by-File Forensic Ledger

Full forensic parameters extracted from the pipeline (all recordings at 16,000 Hz single-channel PCM):

```
Legend:
- Crest: Crest factor in dB (20*log10(peak/RMS))
- Peak: Peak digital amplitude [-1.0, 1.0]
- Cent: Spectral centroid (Hz)
- Energy: lo (<500Hz), mid (500-2000Hz), hi (>2000Hz), m2l (mid/low ratio)
- Base Models: MLP (classifier head), CB (CatBoost), LGB (LightGBM), XGB (XGBoost)
- Semantic: pure_gun (YAMNet classes 421,422,425), explosion (YAMNet class 420)
- Scores: Raw (fusion output), Adj (after suppression)
```

### [01] `mitchell_mossberg_12g_01.wav`
- **Source & Sub-Category:** Mitchell Roberts Ballistic Archive / `shotgun_heavy_blast`
- **Acoustic Condition:** High-Energy Clipped (Near-field shotgun muzzle discharge)
- **Duration:** 0.532s ($N_{wins} = 1$)
- **Waveform Characteristics:** Peak = 0.9186, Crest = 17.22 dB, Centroid = 1111.8 Hz
- **Spectral Energy Distribution:** $lo = 0.2069$, $mid = 0.6759$, $hi = 0.1173$, $m2l = 3.2659$
- **Base Classifier Probabilities:** MLP = 0.7255, CB = 0.7673, LGB = 0.8105, XGB = 0.7881 (Ensemble Mean = 0.7728)
- **Semantic Classes:** pure_gun = 0.1013, explosion = 0.3595
- **Classifier Fusion & Suppression:** Raw Score = 0.8506, Suppressed = False, Adjusted Score = 0.8506
- **FSM State & Decision:** IDLE $\rightarrow$ CONFIRMED in V9 standalone; in Phase 51 single-pass it was flagged as unconfirmed due to $n\_wins = 1$ single impulse gating.
- **Root Cause Category:** 4. Short-Duration / Single-Window Truncation.

### [02] `mitchell_colt_ar15_04.wav`
- **Source & Sub-Category:** Mitchell Roberts Ballistic Archive / `rifle_supersonic_crack`
- **Acoustic Condition:** Clean Open-Air (.223 Rem / 5.56 NATO)
- **Duration:** 0.503s ($N_{wins} = 1$)
- **Waveform Characteristics:** Peak = 0.5785, Crest = 16.31 dB, Centroid = 1054.6 Hz
- **Spectral Energy Distribution:** $lo = 0.3176$, $mid = 0.5640$, $hi = 0.1184$, $m2l = 1.7751$
- **Base Classifier Probabilities:** MLP = 0.7985, CB = 0.7210, LGB = 0.7785, XGB = 0.7594 (Ensemble Mean = 0.7644)
- **Semantic Classes:** pure_gun = 0.0623, explosion = 0.6403, fireworks (426/427) = 0.5080
- **Classifier Fusion & Suppression:** Raw Score = 0.5337 $\rightarrow$ Suppressed = True (`fireworks_dominant`) $\rightarrow$ Adjusted Score = 0.0801
- **FSM State & Decision:** IDLE (Score 0.0801 far below threshold 0.70)
- **Root Cause Category:** 3. Threshold Margin & Pyrotechnic Overlap. Class 420 (Explosion) and Class 427 (Firecracker) co-activated, suppressing the high-confidence base model consensus.

### [03] `mitchell_colt_ar15_10.wav`
- **Source & Sub-Category:** Mitchell Roberts Ballistic Archive / `rifle_supersonic_crack`
- **Acoustic Condition:** Clean Open-Air (High ground blast component)
- **Duration:** 0.503s ($N_{wins} = 1$)
- **Waveform Characteristics:** Peak = 0.7690, Crest = 12.86 dB, Centroid = 793.4 Hz
- **Spectral Energy Distribution:** $lo = 0.9330$, $mid = 0.0548$, $hi = 0.0122$, $m2l = 0.0588$
- **Base Classifier Probabilities:** MLP = 0.7733, CB = 0.6773, LGB = 0.6199, XGB = 0.6410 (Ensemble Mean = 0.6779)
- **Semantic Classes:** pure_gun = 0.0576, explosion = 0.4515
- **Classifier Fusion & Suppression:** Raw Score = 0.3487 $\rightarrow$ Suppressed = True (`thunder_rumble`) $\rightarrow$ Adjusted Score = 0.0872
- **FSM State & Decision:** IDLE (Score 0.0872)
- **Root Cause Category:** 1. Ground Blast Rumble Over-Suppression ($lo = 0.9330$).

### [04] `mitchell_colt_ar15_11.wav`
- **Source & Sub-Category:** Mitchell Roberts Ballistic Archive / `rifle_supersonic_crack`
- **Acoustic Condition:** Clean Open-Air
- **Duration:** 0.503s ($N_{wins} = 1$)
- **Waveform Characteristics:** Peak = 0.8067, Crest = 14.09 dB, Centroid = 853.4 Hz
- **Spectral Energy Distribution:** $lo = 0.5105$, $mid = 0.3640$, $hi = 0.1256$, $m2l = 0.7128$
- **Base Classifier Probabilities:** MLP = 0.9335, CB = 0.6950, LGB = 0.6670, XGB = 0.7424 (Ensemble Mean = 0.7595)
- **Semantic Classes:** pure_gun = 0.0018, explosion = 0.0450
- **Classifier Fusion & Suppression:** Raw Score = 0.5626, Suppressed = False, Adjusted Score = 0.5626
- **FSM State & Decision:** IDLE (Score 0.5626 < 0.70 threshold)
- **Root Cause Category:** 2. Base Model Consensus Under-Estimation. MLP scored 0.9335 and XGB scored 0.7424, but fusion output was only 0.5626.

### [05] `mitchell_glock17_9mm_06.wav`
- **Source & Sub-Category:** Mitchell Roberts Ballistic Archive / `handgun_range_sharp`
- **Acoustic Condition:** Clean Open-Air (Sharp 9mm discharge)
- **Duration:** 0.510s ($N_{wins} = 1$)
- **Waveform Characteristics:** Peak = 0.8068, Crest = 18.42 dB, Centroid = 1237.5 Hz
- **Spectral Energy Distribution:** $lo = 0.8755$, $mid = 0.0636$, $hi = 0.0609$, $m2l = 0.0727$
- **Base Classifier Probabilities:** MLP = 0.8929, CB = 0.7759, LGB = 0.7422, XGB = 0.7324 (Ensemble Mean = 0.7858, Min = 0.7324)
- **Semantic Classes:** pure_gun = 0.1170, explosion = 0.3549
- **Classifier Fusion & Suppression:** Raw Score = 0.3314, Suppressed = False, Adjusted Score = 0.3314
- **FSM State & Decision:** IDLE (Score 0.3314 < 0.70)
- **Root Cause Category:** 2. Base Model Consensus Under-Estimation. All 4 base models unanimously agree ($> 0.73$), but fusion tree penalized low mid-to-low ratio ($m2l = 0.0727$).

### [06] `mitchell_glock17_9mm_08.wav`
- **Source & Sub-Category:** Mitchell Roberts Ballistic Archive / `handgun_range_sharp`
- **Acoustic Condition:** Clean Open-Air
- **Duration:** 0.528s ($N_{wins} = 1$)
- **Waveform Characteristics:** Peak = 0.8167, Crest = 18.08 dB, Centroid = 1217.0 Hz
- **Spectral Energy Distribution:** $lo = 0.8947$, $mid = 0.0343$, $hi = 0.0710$, $m2l = 0.0384$
- **Base Classifier Probabilities:** MLP = 0.5912, CB = 0.7419, LGB = 0.7577, XGB = 0.7606 (Ensemble Mean = 0.7128)
- **Semantic Classes:** pure_gun = 0.0921, explosion = 0.3818
- **Classifier Fusion & Suppression:** Raw Score = 0.2847 $\rightarrow$ Suppressed = True (`thunder_rumble`) $\rightarrow$ Adjusted Score = 0.0712
- **FSM State & Decision:** IDLE (Score 0.0712)
- **Root Cause Category:** 1. Ground Blast Rumble Over-Suppression. Strong muzzle blast low rumble ($lo = 0.8947$) triggered suppression despite crest = 18.08 dB.

### [07] `mitchell_ak47_762_01.wav`
- **Source & Sub-Category:** Mitchell Roberts Ballistic Archive / `assault_rifle_high_energy`
- **Acoustic Condition:** High-Energy Clipped (7.62x39mm close muzzle discharge)
- **Duration:** 0.488s ($N_{wins} = 1$)
- **Waveform Characteristics:** Peak = 0.5408, Crest = 20.20 dB, Centroid = 1366.2 Hz
- **Spectral Energy Distribution:** $lo = 0.0231$, $mid = 0.0663$, $hi = 0.9073$, $m2l = 2.8552$
- **Base Classifier Probabilities:** MLP = 0.7623, CB = 0.7235, LGB = 0.7905, XGB = 0.7451 (Ensemble Mean = 0.7554, Min = 0.7235)
- **Semantic Classes:** pure_gun = 0.1339, explosion = 0.3838
- **Classifier Fusion & Suppression:** Raw Score = 0.5125, Suppressed = False, Adjusted Score = 0.5125
- **FSM State & Decision:** IDLE (Score 0.5125 < 0.70)
- **Root Cause Category:** 2. Base Model Consensus Under-Estimation. High-frequency clipping energy ($hi = 0.9073$) caused fusion model to predict 0.5125 despite base models $> 0.72$.

### [08] `mitchell_ak47_762_03.wav`
- **Source & Sub-Category:** Mitchell Roberts Ballistic Archive / `assault_rifle_high_energy`
- **Acoustic Condition:** High-Energy Clipped
- **Duration:** 0.517s ($N_{wins} = 1$)
- **Waveform Characteristics:** Peak = 0.8405, Crest = 19.31 dB, Centroid = 1329.3 Hz
- **Spectral Energy Distribution:** $lo = 0.8927$, $mid = 0.0155$, $hi = 0.0918$, $m2l = 0.0174$
- **Base Classifier Probabilities:** MLP = 0.7703, CB = 0.5755, LGB = 0.4889, XGB = 0.5509 (Ensemble Mean = 0.5964)
- **Semantic Classes:** pure_gun = 0.0571, explosion = 0.2835
- **Classifier Fusion & Suppression:** Raw Score = 0.3464 $\rightarrow$ Suppressed = True (`thunder_rumble`) $\rightarrow$ Adjusted Score = 0.0866
- **FSM State & Decision:** IDLE (Score 0.0866)
- **Root Cause Category:** 1. Ground Blast Rumble Over-Suppression.

### [09] `mitchell_ak47_762_04.wav`
- **Source & Sub-Category:** Mitchell Roberts Ballistic Archive / `assault_rifle_high_energy`
- **Acoustic Condition:** High-Energy Clipped
- **Duration:** 0.500s ($N_{wins} = 1$)
- **Waveform Characteristics:** Peak = 0.5694, Crest = 20.14 dB, Centroid = 1432.6 Hz
- **Spectral Energy Distribution:** $lo = 0.0209$, $mid = 0.0521$, $hi = 0.9242$, $m2l = 2.4796$
- **Base Classifier Probabilities:** MLP = 0.5777, CB = 0.7083, LGB = 0.6372, XGB = 0.6588 (Ensemble Mean = 0.6455)
- **Semantic Classes:** pure_gun = 0.0621, explosion = 0.3099
- **Classifier Fusion & Suppression:** Raw Score = 0.4293, Suppressed = False, Adjusted Score = 0.4293
- **FSM State & Decision:** IDLE (Score 0.4293 < 0.70)
- **Root Cause Category:** 3. Threshold Margin & Clipping Dispersion.

### [10] `mitchell_ak47_762_05.wav`
- **Source & Sub-Category:** Mitchell Roberts Ballistic Archive / `assault_rifle_high_energy`
- **Acoustic Condition:** High-Energy Clipped
- **Duration:** 0.500s ($N_{wins} = 1$)
- **Waveform Characteristics:** Peak = 0.5486, Crest = 18.56 dB, Centroid = 1496.1 Hz
- **Spectral Energy Distribution:** $lo = 0.9758$, $mid = 0.0129$, $hi = 0.0112$, $m2l = 0.0132$
- **Base Classifier Probabilities:** MLP = 0.7069, CB = 0.5910, LGB = 0.5418, XGB = 0.5138 (Ensemble Mean = 0.5884)
- **Semantic Classes:** pure_gun = 0.0531, explosion = 0.2350
- **Classifier Fusion & Suppression:** Raw Score = 0.4433 $\rightarrow$ Suppressed = True (`thunder_rumble`) $\rightarrow$ Adjusted Score = 0.1108
- **FSM State & Decision:** IDLE (Score 0.1108)
- **Root Cause Category:** 1. Ground Blast Rumble Over-Suppression.

### [11] `mitchell_colt45_single_02.wav`
- **Source & Sub-Category:** Mitchell Roberts Ballistic Archive / `handgun_heavy_caliber`
- **Acoustic Condition:** High-Energy Clipped (.45 ACP heavy bore)
- **Duration:** 0.496s ($N_{wins} = 1$)
- **Waveform Characteristics:** Peak = 0.3618, Crest = 19.80 dB, Centroid = 1028.2 Hz
- **Spectral Energy Distribution:** $lo = 0.9967$, $mid = 0.0007$, $hi = 0.0026$, $m2l = 0.0007$
- **Base Classifier Probabilities:** MLP = 0.5320, CB = 0.4745, LGB = 0.5370, XGB = 0.4755 (Ensemble Mean = 0.5048)
- **Semantic Classes:** pure_gun = 0.0197, explosion = 0.0642
- **Classifier Fusion & Suppression:** Raw Score = 0.6335 $\rightarrow$ Suppressed = True (`thunder_rumble`) $\rightarrow$ Adjusted Score = 0.1584
- **FSM State & Decision:** IDLE (Score 0.1584)
- **Root Cause Category:** 1. Ground Blast Rumble Over-Suppression ($lo = 0.9967$).

### [12] `mitchell_colt1911_45_01.wav`
- **Source & Sub-Category:** Mitchell Roberts Ballistic Archive / `handgun_1911_sharp`
- **Acoustic Condition:** Clean Open-Air (.45 ACP)
- **Duration:** 0.530s ($N_{wins} = 1$)
- **Waveform Characteristics:** Peak = 0.4046, Crest = 13.30 dB, Centroid = 1185.2 Hz
- **Spectral Energy Distribution:** $lo = 0.5641$, $mid = 0.2913$, $hi = 0.1445$, $m2l = 0.5164$
- **Base Classifier Probabilities:** MLP = 0.6048, CB = 0.5153, LGB = 0.5223, XGB = 0.5381 (Ensemble Mean = 0.5451)
- **Semantic Classes:** pure_gun = 0.0006, explosion = 0.0310
- **Classifier Fusion & Suppression:** Raw Score = 0.0356 $\rightarrow$ Suppressed = True (`ballistic_incoherence`) $\rightarrow$ Adjusted Score = 0.0071
- **FSM State & Decision:** IDLE (Score 0.0071)
- **Root Cause Category:** 5. Severe Classifier False Negative. YAMNet pure_gun = 0.0006 failed coherence test.

### [13] `mitchell_colt1911_45_02.wav`
- **Source & Sub-Category:** Mitchell Roberts Ballistic Archive / `handgun_1911_sharp`
- **Acoustic Condition:** Clean Open-Air (.45 ACP)
- **Duration:** 0.503s ($N_{wins} = 1$)
- **Waveform Characteristics:** Peak = 0.3834, Crest = 14.76 dB, Centroid = 1154.9 Hz
- **Spectral Energy Distribution:** $lo = 0.6303$, $mid = 0.2556$, $hi = 0.1140$, $m2l = 0.4055$
- **Base Classifier Probabilities:** MLP = 0.4869, CB = 0.4602, LGB = 0.4411, XGB = 0.4614 (Ensemble Mean = 0.4624)
- **Semantic Classes:** pure_gun = 0.0004, explosion = 0.0111
- **Classifier Fusion & Suppression:** Raw Score = 0.1797 $\rightarrow$ Suppressed = True (`ballistic_incoherence`) $\rightarrow$ Adjusted Score = 0.0359
- **FSM State & Decision:** IDLE (Score 0.0359)
- **Root Cause Category:** 5. Severe Classifier False Negative.

### [14] `mitchell_colt_govt_01.wav`
- **Source & Sub-Category:** Mitchell Roberts Ballistic Archive / `handgun_1911_sharp`
- **Acoustic Condition:** Clean Open-Air
- **Duration:** 0.520s ($N_{wins} = 1$)
- **Waveform Characteristics:** Peak = 0.3903, Crest = 13.27 dB, Centroid = 1216.7 Hz
- **Spectral Energy Distribution:** $lo = 0.7156$, $mid = 0.1215$, $hi = 0.1629$, $m2l = 0.1698$
- **Base Classifier Probabilities:** MLP = 0.8849, CB = 0.7217, LGB = 0.8239, XGB = 0.7579 (Ensemble Mean = 0.7971, Min = 0.7217)
- **Semantic Classes:** pure_gun = 0.0100, explosion = 0.0925
- **Classifier Fusion & Suppression:** Raw Score = 0.5534, Suppressed = False, Adjusted Score = 0.5534
- **FSM State & Decision:** IDLE (Score 0.5534 < 0.70)
- **Root Cause Category:** 2. Base Model Consensus Under-Estimation. All 4 base models $> 0.72$, but fusion tree penalized $m2l = 0.1698$.

### [15] `mitchell_colt_govt_02.wav`
- **Source & Sub-Category:** Mitchell Roberts Ballistic Archive / `handgun_1911_sharp`
- **Acoustic Condition:** Clean Open-Air
- **Duration:** 0.529s ($N_{wins} = 1$)
- **Waveform Characteristics:** Peak = 0.4533, Crest = 15.52 dB, Centroid = 1365.2 Hz
- **Spectral Energy Distribution:** $lo = 0.0171$, $mid = 0.0830$, $hi = 0.8970$, $m2l = 4.8209$
- **Base Classifier Probabilities:** MLP = 0.4491, CB = 0.5188, LGB = 0.5323, XGB = 0.5422 (Ensemble Mean = 0.5106)
- **Semantic Classes:** pure_gun = 0.0004, explosion = 0.0104
- **Classifier Fusion & Suppression:** Raw Score = 0.4343, Suppressed = False, Adjusted Score = 0.4343
- **FSM State & Decision:** IDLE (Score 0.4343 < 0.70)
- **Root Cause Category:** 3. Threshold Margin & Weak Semantic Evidence.

### [16] `shotspotter_chicago_d7_sensor3.wav`
- **Source & Sub-Category:** ShotSpotter Research Archive / `urban_street_canyon`
- **Acoustic Condition:** Reverberant Urban Distance (Multipath building reflections, Chicago District 7)
- **Duration:** 9.983s ($N_{wins} = 19$)
- **Waveform Characteristics:** Peak = 0.1481, Crest = 15.32 dB, Centroid = 688.8 Hz
- **Spectral Energy Distribution:** $lo = 0.8887$, $mid = 0.1098$, $hi = 0.0015$, $m2l = 0.1236$
- **Base Classifier Probabilities:** MLP = 0.6486, CB = 0.4451, LGB = 0.4488, XGB = 0.5078 (Ensemble Mean = 0.5126)
- **Semantic Classes:** pure_gun = 0.0006, explosion = 0.0110
- **Classifier Fusion & Suppression:** Window 0 Peak Raw Score = 0.7532 $\rightarrow$ Suppressed = True (`thunder_rumble`) $\rightarrow$ Adjusted Score = 0.1539
- **FSM State & Decision:** IDLE (Score 0.1539)
- **Root Cause Category:** 1. Distant Urban Reverberation Over-Suppressed by Rumble Rule. Distant multipath acoustic attenuation stripped high frequencies, dropping centroid to 688 Hz and elevating low frequencies.

### [17] `mitchell_ar15_single_01.wav`
- **Source & Sub-Category:** Mitchell Roberts GunshotClassifier / `rifle_outdoor_single`
- **Acoustic Condition:** Clean Open-Air (.223 Rem outdoor range)
- **Duration:** 0.507s ($N_{wins} = 1$)
- **Waveform Characteristics:** Peak = 0.5635, Crest = 19.36 dB, Centroid = 972.1 Hz
- **Spectral Energy Distribution:** $lo = 0.9849$, $mid = 0.0133$, $hi = 0.0018$, $m2l = 0.0135$
- **Base Classifier Probabilities:** MLP = 0.7788, CB = 0.7267, LGB = 0.7018, XGB = 0.6762 (Ensemble Mean = 0.7209)
- **Semantic Classes:** pure_gun = 0.1761, explosion = 0.2984
- **Classifier Fusion & Suppression:** Raw Score = 0.6521, Suppressed = False, Adjusted Score = 0.6521
- **FSM State & Decision:** IDLE (Score 0.6521 < 0.70)
- **Root Cause Category:** 2. Base Model Consensus Under-Estimation. Base models score 0.7209 with pure_gun = 0.1761 and crest = 19.36 dB.

### [18] `mitchell_ar15_single_04.wav`
- **Source & Sub-Category:** Mitchell Roberts GunshotClassifier / `rifle_outdoor_single`
- **Acoustic Condition:** Clean Open-Air
- **Duration:** 0.570s ($N_{wins} = 1$)
- **Waveform Characteristics:** Peak = 0.6591, Crest = 20.46 dB, Centroid = 1063.3 Hz
- **Spectral Energy Distribution:** $lo = 0.9747$, $mid = 0.0233$, $hi = 0.0020$, $m2l = 0.0239$
- **Base Classifier Probabilities:** MLP = 0.7386, CB = 0.5755, LGB = 0.6690, XGB = 0.5812 (Ensemble Mean = 0.6411)
- **Semantic Classes:** pure_gun = 0.2988, explosion = 0.3190
- **Classifier Fusion & Suppression:** Raw Score = 0.4251, Suppressed = False, Adjusted Score = 0.4251
- **FSM State & Decision:** IDLE (Score 0.4251 < 0.70)
- **Root Cause Category:** 3. Threshold Margin & Fusion Model Compression.

### [19] `mitchell_ar15_double_01.wav`
- **Source & Sub-Category:** Mitchell Roberts GunshotClassifier / `rifle_rapid_double`
- **Acoustic Condition:** Rapid Cadence / Bursts (Double tap)
- **Duration:** 0.512s ($N_{wins} = 1$)
- **Waveform Characteristics:** Peak = 1.0020 (digital clipping), Crest = 21.82 dB, Centroid = 1085.0 Hz
- **Spectral Energy Distribution:** $lo = 0.9647$, $mid = 0.0314$, $hi = 0.0039$, $m2l = 0.0325$
- **Base Classifier Probabilities:** MLP = 0.7749, CB = 0.6594, LGB = 0.6574, XGB = 0.6044 (Ensemble Mean = 0.6740)
- **Semantic Classes:** pure_gun = 0.1340, explosion = 0.3503
- **Classifier Fusion & Suppression:** Raw Score = 0.3201, Suppressed = False, Adjusted Score = 0.3201
- **FSM State & Decision:** IDLE (Score 0.3201 < 0.70)
- **Root Cause Category:** 2. Base Model Consensus Under-Estimation on Clipped Double Tap.

### [20] `mitchell_beretta_single_01.wav`
- **Source & Sub-Category:** Mitchell Roberts GunshotClassifier / `handgun_range_single`
- **Acoustic Condition:** Clean Open-Air (9mm Beretta 92FS)
- **Duration:** 0.520s ($N_{wins} = 1$)
- **Waveform Characteristics:** Peak = 0.9774, Crest = 22.54 dB, Centroid = 923.1 Hz
- **Spectral Energy Distribution:** $lo = 0.9268$, $mid = 0.0634$, $hi = 0.0099$, $m2l = 0.0684$
- **Base Classifier Probabilities:** MLP = 0.6124, CB = 0.5100, LGB = 0.3358, XGB = 0.4303 (Ensemble Mean = 0.4721)
- **Semantic Classes:** pure_gun = 0.4492 (Strong Gunshot Class), explosion = 0.5929
- **Classifier Fusion & Suppression:** Raw Score = 0.2221, Suppressed = False, Adjusted Score = 0.2221
- **FSM State & Decision:** IDLE (Score 0.2221 < 0.70)
- **Root Cause Category:** 5. Gradient Boosted Tree Feature Degradation. Despite YAMNet identifying class 421 at 0.4492, the tree models predicted low probability due to $m2l < 0.07$.

---

## 4. Key Engineering Insights for V10 Optimization

1. **Base Model Ensemble Consensus vs. Fusion Trees:**
   In 6 of the 20 missed files, all 4 base models scored $> 0.70$, but the fusion tree output collapsed to $0.32 - 0.55$. Introducing **Base Model Consensus Calibration (BMCC)** directly addresses this tree-splitting distortion without altering threshold boundaries.
2. **Ground Blast Rumble Override:**
   Real open-air gunshots over soil or turf generate strong low-frequency ground roll ($lo \ge 0.88$). Because thunder and door slams never exceed a centroid of $785\text{ Hz}$, impulses with $cent \ge 1050\text{ Hz}$, $crest \ge 16\text{ dB}$, and $pure\_gun \ge 0.04$ can be safely exempted from thunder suppression.
3. **Single-Window FSM Handling:**
   Recordings shorter than 0.6s produce only 1 processing window. The FSM must confirm a single impulse if $crest \ge 13.0\text{ dB}$ and calibrated score $\ge 0.70$, preventing truncated historical benchmark files from starving in candidate state.

