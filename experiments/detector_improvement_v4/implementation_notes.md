# PHASE 46 IMPLEMENTATION NOTES: DETECTOR IMPROVEMENT V4

**RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.**

> [!CAUTION]
> **MANDATORY SAFETY DESIGNATION**
> This software is an uncertified acoustic research demonstration prototype. It must never be deployed for autonomous emergency dispatch, tactical police response, active-shooter alerting, automated evacuation, building lockdown, or life-critical physical security. Use lawfully obtained recordings and safe audio playback only. Live-fire and hazardous acoustic experiments are strictly prohibited.

---

## 1. System Overview

Detector Improvement V4 is a condition-robust multi-modal acoustic gunshot detector designed to operate across diverse sensor environments, specifically overcoming high-frequency acoustic attenuation caused by fabric occlusion (pocket-worn sensors), dynamic range pre-amplifier saturation, and single-round window dilution.

The architecture comprises five tightly integrated subsystems:
1. **Low-Latency Sub-Band Acoustic DSP:** Real-time computation of 8 physical time-domain and frequency-domain discriminators in $< 0.28\text{ ms}$.
2. **26-Dimensional Supervised Fusion Classifier:** A calibrated `HistGradientBoostingClassifier` trained with controlled domain adaptation (fabric low-pass simulation and dynamic saturation) under strict GroupKFold cross-validation.
3. **Calibrated Multi-Category Semantic Suppression V4:** Incorporates dedicated glass shatter gating, two-tier pyrotechnic gating, and ballistic shockwave protection.
4. **Deterministic Refractory State Machine (FSM V4):** State-preserving 4-state automaton featuring candidate-bound crest attribution and duration-invariant single-impulse promotion.
5. **Circular-Buffer Real-Time Stream Processor:** Optimized sliding window pipeline operating on 480 ms hops with $< 3.0\%$ CPU utilization.

---

## 2. DSP Feature Formulations & Condition Estimator

For every 0.96-second analysis window (15,360 samples at 16 kHz), the DSP engine extracts 8 physical acoustic metrics:

### 2.1 Time-Domain Crest Factor
$$\text{Crest Factor (dB)} = 20 \log_{10} \left( \frac{\max |x(t)|}{\text{RMS}(x) + \epsilon} \right)$$
Measures instantaneous waveform peakiness. Remains robust under fabric occlusion (18.66 dB mean) but drops under pre-amp clipping (14.92 dB).

### 2.2 Wiener Spectral Flatness
$$\text{Flatness} = \frac{\exp \left( \frac{1}{K} \sum_{k=1}^K \ln S(k) \right)}{\frac{1}{K} \sum_{k=1}^K S(k)}$$
Measures spectral distribution uniformity (broad-band white noise vs. tonal harmonics).

### 2.3 Acoustic Sub-Band Partitioning
The single-sided power spectrum $P(f) = |X(f)|^2$ is segmented into three physically motivated frequency bands:
* **Low-Band ($f < 500\text{ Hz}$):** Captures mechanical rumble, wind buffeting, and fireworks combustion tails.
  $$\text{Low-Band Ratio} = \frac{\sum_{f < 500} P(f)}{\sum P(f) + \epsilon}$$
* **Mid-Band ($500\text{ Hz} \le f < 2500\text{ Hz}$):** Contains the primary explosive shockwave and muzzle gas discharge. This band passes through clothing fabric with minimal attenuation.
  $$\text{Mid-Band Ratio} = \frac{\sum_{500 \le f < 2500} P(f)}{\sum P(f) + \epsilon}$$
* **High-Band ($f \ge 2500\text{ Hz}$):** Contains microsecond supersonic N-wave rise times, but is heavily absorbed by fabrics.
  $$\text{High-Band Ratio} = \frac{\sum_{f \ge 2500} P(f)}{\sum P(f) + \epsilon}$$

### 2.4 Relative Sub-Band Dynamic Invariants
* **Mid-to-Low Energy Ratio:**
  $$\text{Mid-to-Low Ratio} = \frac{\text{Mid-Band Ratio} + 10^{-4}}{\text{Low-Band Ratio} + 10^{-4}}$$
  Gunshots (both clean and pocket-occluded) maintain $\text{Mid-to-Low Ratio} \approx 1.2 - 3.5$. Fireworks and thunder have heavy low-band dominance ($\text{Mid-to-Low Ratio} < 0.6$).
* **Channel Roll-Off Ratio (Condition Estimator):**
  $$\text{Channel Roll-Off Ratio} = \frac{\text{High-Band Ratio} + 10^{-4}}{\text{Mid-Band Ratio} + 10^{-4}}$$
  Acts as an implicit sensor condition indicator:
  * Clear open-air sensors: $\text{Roll-Off} \approx 0.30 - 0.45$.
  * Pocket-occluded sensors: $\text{Roll-Off} \approx 0.08 - 0.15$.
  * Glass breaking / high-frequency shatter: $\text{Roll-Off} > 1.0$.

---

## 3. Domain Adaptation & Supervised Classifier Training

### 3.1 Feature Vector Specification $\mathbf{x} \in \mathbb{R}^{26}$
1. `p_mlp`: Frozen MLP model probability.
2. `p_cb`: Frozen CatBoost model probability.
3. `p_lgb`: Frozen LightGBM model probability.
4. `p_xgb`: Frozen XGBoost model probability.
5. `ensemble_mean`: Arithmetic mean of the 4 base models.
6. `ensemble_max`: Max base model probability.
7. `ensemble_min`: Min base model probability.
8. `ensemble_std`: Standard deviation of base model probabilities.
9. `ensemble_top2`: Mean of the highest 2 base model probabilities.
10. `yamnet_gunshot`: Max of YAMNet classes [421, 422, 424, 425].
11. `yamnet_ballistic`: Max of YAMNet classes [420, 421, 422, 424, 425, 428, 434, 460].
12. `yamnet_fireworks`: Max of YAMNet classes [426, 427].
13. `yamnet_thunder`: Max of YAMNet classes [280, 281].
14. `yamnet_impact`: Max of YAMNet classes [413, 414, 352, 353, 58].
15. `yamnet_glass`: Max of YAMNet classes [433, 435, 436].
16. `yamnet_non_target`: Max of speech, motor vehicle, and natural ambient classes.
17. `bal_to_fw_ratio`: $(\text{ballistic} + 10^{-4}) / (\text{fireworks} + 10^{-4})$.
18. `bal_to_impact_ratio`: $(\text{ballistic} + 10^{-4}) / (\text{impact} + 10^{-4})$.
19. `crest_factor_db`: Physical time-domain peakiness.
20. `spectral_flatness`: Wiener entropy.
21. `high_band_ratio`: Energy $\ge 2500\text{ Hz}$.
22. `mid_band_ratio`: Energy in $[500\text{ Hz}, 2500\text{ Hz}]$.
23. `low_band_ratio`: Energy $< 500\text{ Hz}$.
24. `mid_to_low_ratio`: Sub-band ratio invariant.
25. `channel_rolloff_ratio`: Condition estimator.
26. `spectral_centroid_hz`: Spectral center of mass.

### 3.2 Training Regimen & Cross-Validation
* **Base Training Set:** 218 recordings ($14,663$ windows) from Development partition.
* **Domain Adaptation Pipeline:** All 72 positive development recordings were augmented with:
  * Fabric attenuation: 2nd-order Butterworth low-pass filter at 1800 Hz (light fabric).
  * Heavy fabric attenuation: 2nd-order Butterworth low-pass filter at 1400 Hz (dense fabric).
  * Saturation clipping: Amplitude soft-clipping at 0.65 threshold.
* **Leakage Prevention:** 5-Fold `GroupKFold` grouped strictly by `recording_id`. All 4 variants of a positive recording shared identical group IDs, ensuring no augmented variant ever leaked between train and validation folds.
* **Cross-Validation Metrics:**
  * Mean ROC-AUC: **0.9398 $\pm$ 0.0235**
  * Mean Brier Score: **0.0563 $\pm$ 0.0125**
* **Final Model:** Serialized to [`experiments/detector_improvement_v4/fusion_model.joblib`](file:///E:/gunshot/gunshot/experiments/detector_improvement_v4/fusion_model.joblib).

---

## 4. Calibrated Semantic Suppression V4

```
[ Raw Fusion Score ]
         |
         v
+-------------------------------------------------------------+
| Check 1: Ballistic Coherence Safeguard                       |
| If ballistic < 0.015 and non-target > 0.12: -0.20           |
+-------------------------------------------------------------+
         |
         v
+-------------------------------------------------------------+
| Check 2: Ballistic Shockwave Protection Override            |
| If ballistic >= 0.40 and ballistic >= 0.85 * fireworks:     |
|   -> Bypass all fireworks attenuation rules!                |
+-------------------------------------------------------------+
         |
         v (If not protected)
+-------------------------------------------------------------+
| Check 3: Two-Tier Fireworks Gating                          |
| Dominant: fw > 0.45 and fw > 1.8 * gun -> -0.30             |
| Standard: fw > 0.30 and fw > 1.5 * gun -> -0.35             |
+-------------------------------------------------------------+
         |
         v
+-------------------------------------------------------------+
| Check 4: Glass Shatter Gating (NEW IN V4)                   |
| If glass > 0.30 and high_band > 0.30 and ballistic < 0.20:  |
|   -> Attenuate by 0.35!                                     |
+-------------------------------------------------------------+
         |
         v
+-------------------------------------------------------------+
| Check 5: Mechanical Impact, Thunder, Siren, Canine Gating    |
+-------------------------------------------------------------+
         |
         v
[ Adjusted Score ]
```

---

## 5. Event State Machine (FSM V4) & Profiles

```
State Machine Operating Logic:

      +-------------------------------------------------------------+
      |                                                             |
      v                                                             |
  +-------+         Window Score >= 0.62 and Crest >= 7.5 dB        +-----------+
  | IDLE  | ------------------------------------------------------> | CANDIDATE |
  +-------+                                                         +-----------+
      ^                                                                   |
      |                     Window Score >= 0.80                          |
      |                     or Sustained Windows >= 2                     |
      |                   +-----------------------------------------------+
      |                   v
  +----------+        +-----------+
  | COOLDOWN | <----- | CONFIRMED |
  +----------+        +-----------+
      |                     |
      | (Gap > 0.60s or     | (Gap > 0.60s or
      |  Cooldown elapsed)  |  Score < 0.40)
      +---------------------+
```

### Profile Specifications in `config_improvement_v4.json`

| Parameter | Balanced (Default) | High-Precision | High-Sensitivity |
| :--- | :---: | :---: | :---: |
| `threshold_base` | 0.62 | 0.72 | 0.52 |
| `threshold_high` | 0.80 | 0.88 | 0.70 |
| `threshold_off` | 0.40 | 0.48 | 0.35 |
| `confirm_windows` | 2 | 2 | 1 |
| `cooldown_secs` | 2.0 s | 2.5 s | 1.5 s |
| `min_crest_factor_db` | 7.5 dB | 9.0 dB | 6.5 dB |
| `single_impulse_min_crest_db` | 11.5 dB | 13.5 dB | 10.0 dB |
| `single_impulse_min_score` | 0.62 | 0.72 | 0.52 |
| `allow_single_impulse_exception` | True | True | True |

---

## 6. Execution Latency & Streaming Performance

* **DSP Extraction Latency:** $0.28\text{ ms}$ per 0.96 s window.
* **YAMNet Inference:** $11.50\text{ ms}$.
* **Ensemble Models + HistGradientBoosting:** $1.85\text{ ms}$.
* **FSM Update:** $0.05\text{ ms}$.
* **Total Pipeline Latency:** $\mathbf{\approx 13.68\text{ ms}}$ per 480 ms hop interval ($2.85\%$ CPU budget).
* **Streaming Stability:** Evaluated on the 2.0-hour continuous audio stream (`phase12_continuous_stream_01_urban_and_environmental_2hr.wav`) with 0 buffer overflows and zero memory growth.

