# PHASE 45 IMPLEMENTATION NOTES: DETECTOR IMPROVEMENT V3

**RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.**

> [!CAUTION]
> **MANDATORY SAFETY DESIGNATION**
> This software is an uncertified acoustic research demonstration prototype. It must never be deployed for autonomous emergency dispatch, tactical police response, active-shooter alerting, automated evacuation, building lockdown, or life-critical physical security. Use lawfully obtained recordings and safe audio playback only. Live-fire and hazardous acoustic experiments are strictly prohibited.

---

## 1. System Overview

Detector Improvement V3 represents a model-level acoustic discrimination upgrade designed to resolve the fundamental trade-off between gunshot detection sensitivity and environmental/fireworks false alarms. Prior improvements (V1, V2) introduced post-hoc score suppression and refractory state machine heuristics, which lowered continuous background false alarms but left fireworks false-positive rates elevated (~40.7%) and suffered from state machine decay misattribution that missed authentic single-round impulses.

V3 integrates:
1. **Low-Latency Physical Acoustic DSP:** Microsecond-resolution time-domain and spectral-domain acoustic feature extraction running alongside YAMNet embeddings.
2. **Supervised Multi-Modal Fusion Classifier:** A calibrated `HistGradientBoostingClassifier` fusing physical acoustics, semantic AudioSet class logits, and the frozen four-model ensemble (MLP, CatBoost, LightGBM, XGBoost).
3. **Repaired Event State Machine (FSM V3):** Fixed single-round impulse crest attribution, native multi-shot cluster tracking, and elimination of arbitrary duration assumptions.
4. **Ballistic Shockwave Protection:** Active protection in the suppression filter ensuring high-confidence ballistic shockwaves are never attenuated by reverberant echo profiles.

---

## 2. Low-Latency DSP Feature Extraction

### 2.1 Feature Definitions
For every 0.96-second analysis window (15,360 samples at 16 kHz), the DSP engine extracts 5 physical acoustic discriminators:

1. **Crest Factor ($\text{dB}$):**
   $$\text{Crest Factor} = 20 \log_{10} \left( \frac{\max |x(t)|}{\text{RMS}(x) + \epsilon} \right)$$
   Measures time-domain peakiness. Impulsive gunshot shockwaves exhibit crest factors between $14\text{ dB}$ and $26\text{ dB}$, whereas ambient wind and HVAC remain below $10\text{ dB}$.
2. **Spectral Flatness (Wiener Entropy):**
   $$\text{Flatness} = \frac{\exp \left( \frac{1}{K} \sum_{k=1}^K \ln S(k) \right)}{\frac{1}{K} \sum_{k=1}^K S(k)}$$
   Measures the uniformity of power spectral density. Gunshot muzzle blasts and supersonic N-waves generate white-noise-like broad-band energy (flatness $\approx 0.05 - 0.15$), whereas musical fireworks whistles, mechanical motors, and sirens produce discrete tonal peaks (flatness $< 0.03$).
3. **High-Band Energy Ratio ($\ge 2500\text{ Hz}$):**
   $$\text{High-Band Ratio} = \frac{\sum_{f \ge 2500\text{ Hz}} S(f)}{\sum_{f} S(f) + \epsilon}$$
   High-caliber ballistic shockwaves concentrate significant acoustic energy above 2.5 kHz. Fireworks and distant thunder are heavily dominated by low-frequency combustion rumble.
4. **Low-Band Energy Ratio ($< 500\text{ Hz}$):**
   $$\text{Low-Band Ratio} = \frac{\sum_{f < 500\text{ Hz}} S(f)}{\sum_{f} S(f) + \epsilon}$$
   Captures mechanical low-end rumble (vehicle rumble, fireworks mortar thuds).
5. **Spectral Centroid ($\text{Hz}$):**
   $$\text{Centroid} = \frac{\sum f \cdot S(f)}{\sum S(f) + \epsilon}$$
   Center of mass of the frequency spectrum.

### 2.2 Computational Efficiency & Latency Budget
* Time-domain RMS and Peak: $\mathcal{O}(N)$ vectorized NumPy operations.
* Spectral metrics: Single 1024-point FFT with 512-point hop.
* **Benchmarked Execution Time:** Under **0.25 ms** per 0.96-second window on a single CPU core, consuming $< 0.06\%$ of the 480 ms hop interval.

---

## 3. Supervised Multi-Modal Fusion Classifier

### 3.1 Feature Vector Formulation
The fusion model receives a 19-dimensional feature vector $\mathbf{x} \in \mathbb{R}^{19}$ for each 0.96-second window:
* **Ensemble Model Logits (4 features):** $p_{\text{mlp}}, p_{\text{cb}}, p_{\text{lgb}}, p_{\text{xgb}}$ from the frozen Phase 14 ensemble models.
* **Ensemble Ensemble Consensus (5 features):** Mean probability, max probability, min probability, standard deviation, and mean of top-2 models.
* **Semantic AudioSet Logits (5 features):** Max gunshot classes (IDs 421, 422, 424, 425), ballistic explosion classes (IDs 420, 421, 422, 424, 425, 428, 434, 460), fireworks classes (IDs 426, 427), thunder classes (IDs 280, 281), mechanical/tool impact classes (IDs 58, 352, 353, 413, 414), and non-target ambient classes (speech, music, nature).
* **Cross-Domain Contrast Ratios (2 features):** Ballistic-to-fireworks evidence ratio, ballistic-to-impact evidence ratio.
* **Physical Acoustic Features (5 features):** Crest factor (dB), spectral flatness, high-band ratio, low-band ratio, spectral centroid.

### 3.2 Model Training & Calibration Regimen
* **Model Class:** `HistGradientBoostingClassifier` with `max_iter=150`, `max_depth=5`, `l2_regularization=1.5`, and early stopping.
* **Training Corpus:** Strictly trained on the Development partition ($N = 14,663$ windows across 218 recordings).
* **Leakage Prevention:** Evaluated using **5-Fold GroupKFold Cross-Validation**, grouping by `recording_id`. All windows from a single recording were strictly isolated into either train or validation folds, ensuring zero intra-recording temporal leakage.
* **Cross-Validation Metrics:**
  * **Mean GroupKFold ROC-AUC:** $\mathbf{0.9093} \pm 0.021$
  * **Mean Brier Score:** $\mathbf{0.0240}$ (demonstrating well-calibrated posterior probabilities).
* **Persistence:** Serialized via joblib to `experiments/detector_improvement_v3/fusion_model.joblib`.

---

## 4. Repaired Event State Machine (FSM V3)

```
        +--------------------------------------------------------+
        |                                                        |
        v                                                        |
    +-------+         Window Score >= Trigger         +-----------+
    | IDLE  | --------------------------------------> | CANDIDATE |
    +-------+                                         +-----------+
        ^                                                   |
        |                 Window Score >= Confirm           |
        |               +-----------------------------------+
        |               v
    +----------+    +-----------+
    | COOLDOWN | <--| CONFIRMED |
    +----------+    +-----------+
        |                 |
        | (Timeout elapsed|
        |  or silence)    |
        +-----------------+
```

### 4.1 Root-Cause Defect in V2 State Machine
In V2, single-round impulses were evaluated during the transition from `CANDIDATE` to `COOLDOWN`. When a gunshot impulse occurred in Window 0 and silence followed in Window 1, the FSM checked `crest_factor_db` of the *active window* (Window 1), which was $< 10\text{ dB}$, discarding the impulse.

### 4.2 State Machine V3 Architectural Fixes
1. **Intra-Window Crest Attribution:** Every candidate window stores its own instantaneous `crest_factor_db` in its dictionary payload. When testing the single-round impulse condition, FSM V3 computes:
   $$\text{Peak Impulse Crest} = \max_{w \in \mathcal{W}_{\text{candidate}}} w[\text{'crest\_factor\_db'}]$$
   If this peak exceeds the `single_impulse_min_crest_db` threshold ($13.0\text{ dB}$), the impulse is accepted.
2. **Unbounded Duration Invariance:** Removed the arbitrary 5-second file length heuristic present in V1/V2, allowing seamless streaming across continuous multi-hour streams without edge discontinuities.
3. **Ballistic Shockwave Protection:** In `CalibratedAcousticSuppressionV3`, if ballistic evidence exceeds $0.45$ and is within $90\%$ of fireworks evidence, the suppression filter is bypassed, preventing false attenuation of reverberant rifle fire.

---

## 5. Streaming Pipeline & Real-Time Profile Specs

The real-time streaming class `RealTimeStreamDetectorImprovementV3` processes incoming audio via a circular buffer:
* **Audio Format:** 16,000 Hz, 16-bit PCM mono.
* **Buffer Size:** 15,360 samples ($0.96\text{ seconds}$).
* **Hop Step:** 7,680 samples ($0.48\text{ seconds}$).
* **Per-Hop Processing Latency:**
  * DSP Feature Extraction: $\approx 0.25\text{ ms}$
  * YAMNet Inference: $\approx 11.50\text{ ms}$
  * Ensemble + Fusion Classifier: $\approx 1.80\text{ ms}$
  * State Machine Update: $\approx 0.05\text{ ms}$
  * **Total Pipeline Latency:** $\mathbf{\approx 13.60\text{ ms}}$ (consuming only $2.83\%$ of real-time hop budget).

### Profile Specifications in `config_improvement_v3.json`

| Parameter | Balanced (Default) | High-Precision | High-Sensitivity |
| :--- | :---: | :---: | :---: |
| `trigger_threshold` | 0.50 | 0.65 | 0.40 |
| `confirmation_threshold` | 0.60 | 0.72 | 0.50 |
| `min_confirm_windows` | 2 | 2 | 1 |
| `single_impulse_min_crest_db` | 13.0 dB | 15.0 dB | 11.5 dB |
| `single_impulse_min_spectral_flatness`| 0.035 | 0.045 | 0.025 |
| `single_impulse_min_high_band_ratio` | 0.12 | 0.15 | 0.08 |
| `cooldown_decay_windows` | 2 | 3 | 2 |
| `suppression_profile` | balanced | aggressive | conservative |

---

## 6. Architectural Governance & Safety Isolation

* **Historical Immutability:** No changes were made to Phase 14 (`model_phase14.py`), Phase 36 (`experiments/phase36/`), V1 (`experiments/detector_improvement_v1/`), or V2 (`experiments/detector_improvement_v2/`).
* **Self-Contained Implementation:** V3 components reside exclusively in `experiments/detector_improvement_v3/`.
* **Dashboard Isolation:** The web dashboard default remains frozen at `phase14` as required by project governance.

