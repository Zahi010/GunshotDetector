# PHASE 47 IMPLEMENTATION NOTES: CONDITION-ADAPTIVE DETECTION SYSTEM (V5)

**RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.**

> [!CAUTION]
> **MANDATORY SAFETY DESIGNATION**
> This software is an uncertified acoustic research demonstration prototype. It must never be deployed for autonomous emergency dispatch, tactical police response, active-shooter alerting, automated evacuation, building lockdown, or life-critical physical security. Use lawfully obtained recordings and safe audio playback only. Live-fire and hazardous acoustic experiments are strictly prohibited.

---

## 1. Architecture Overview

`DetectorImprovementV5` is an isolated experimental detector built to provide **condition-adaptive acoustic discrimination**. It combines frozen neural feature representations, physical sub-band dynamics, real-time acoustic transmission estimation, and a context-aware finite state machine (FSM).

```
Pipeline Flow for Detector Improvement V5:

[Audio Waveform (16 kHz Mono)]
              │
              ▼
   [DSP Feature Extraction] ──► 8 Physical Acoustic Metrics
              │                 (Crest, Flatness, High, Mid, Low, Mid-to-Low, Roll-Off, Centroid)
              │
              ├──► [Condition Estimator V5] ──► EMA Smoothing (alpha=0.25) + 2-Win Hysteresis
              │                                      │
              │                                      ▼
              │                              Operating Mode:
              │                              - CLEAR_NORMAL
              │                              - DEGRADED_OCCLUDED
              │                              - UNKNOWN
              │                                      │
              ▼                                      │
    [Frozen Model Ensemble]                          │
    (MLP, CatBoost, LightGBM, XGBoost)               │
              │                                      │
              ▼                                      │
   [26-Dim Feature Vector]                           │
              │                                      │
              ▼                                      │
   [Supervised Fusion Model]                         │
  (HistGradientBoostingClassifier)                   │
              │                                      │
              ▼                                      │
 [Calibrated Semantic Suppression]                   │
  - Glass Shatter Deadlock Fix                       │
  - Low-Rumble Thunder Attenuation                   │
              │                                      │
              ▼                                      │
     [Adjusted Score]                                │
              │                                      │
              └──────────────► [Condition-Adaptive FSM V5] ◄──┘
                                (Applies mode-specific confirmation policies)
                                        │
                                        ▼
                             [Confirmed Gunshot Event]
```

---

## 2. DSP & Physical Acoustic Features

The function `compute_physical_acoustic_features_v5` operates on single 0.96 s analysis windows ($N = 15,360$ samples at $16,000\text{ Hz}$):

### 2.1 Mathematical Formulations
1. **Peak-to-RMS Crest Factor:**
   $$\text{CF}_{\text{dB}} = 20 \log_{10} \left( \frac{\max |y| + 10^{-6}}{\text{RMS}(y) + 10^{-6}} \right)$$
2. **Sub-Band Energy Partitions:**
   Computed via short-time Fourier transform magnitude spectrum $S(f)$:
   $$E_{\text{low}} = \sum_{f < 500\text{ Hz}} |S(f)|^2, \quad E_{\text{mid}} = \sum_{500 \le f < 2500\text{ Hz}} |S(f)|^2, \quad E_{\text{high}} = \sum_{f \ge 2500\text{ Hz}} |S(f)|^2$$
   Normalized ratios:
   $$r_{\text{low}} = \frac{E_{\text{low}}}{E_{\text{total}} + \epsilon}, \quad r_{\text{mid}} = \frac{E_{\text{mid}}}{E_{\text{total}} + \epsilon}, \quad r_{\text{high}} = \frac{E_{\text{high}}}{E_{\text{total}} + \epsilon}$$
3. **Channel Dynamics:**
   * **Mid-to-Low Ratio:**
     $$r_{\text{m2l}} = \frac{r_{\text{mid}} + 10^{-4}}{r_{\text{low}} + 10^{-4}}$$
   * **Channel Roll-Off Ratio:**
     $$r_{\text{rolloff}} = \frac{r_{\text{high}} + 10^{-4}}{r_{\text{mid}} + 10^{-4}}$$
4. **Wiener Spectral Flatness:**
   $$\text{SF} = \frac{\exp \left( \frac{1}{K} \sum_{k=1}^K \ln |S(k)|^2 \right)}{\frac{1}{K} \sum_{k=1}^K |S(k)|^2 + 10^{-8}}$$

---

## 3. Condition Estimator Specification (`ConditionEstimatorV5`)

### 3.1 Exponential Moving Average (EMA)
The condition estimator tracks transmission invariants over time to filter out transient fluctuations:

$$\bar{x}_t = \alpha x_t + (1 - \alpha) \bar{x}_{t-1}, \quad \alpha = 0.25$$

At startup ($t = 0$), state variables are initialized directly to the first window's measurements:
$$\bar{x}_0 = x_0$$

### 3.2 Hysteresis State Machine
To guarantee zero chatter during borderline acoustic conditions:
* A provisional mode change requires **2 consecutive confirming windows** ($0.96\text{ s}$) before the committed operating mode is modified.
* If the acoustic parameters bounce back during the hysteresis window, the provisional counter resets to zero.
* Every state transition is recorded in `transition_log` with:
  * `timestamp_s`: Audio offset in seconds.
  * `from_mode`: Prior committed mode.
  * `to_mode`: New committed mode.
  * `raw_metrics`: Unsmoothed window metrics.
  * `smoothed_metrics`: Current EMA state values.
  * `confidence`: Model confidence in the transition.

### 3.3 Operating Mode Criteria

```python
# Clear / Normal Acoustic Path
if rolloff_ema >= 0.18 and high_ema >= 0.080 and mid_to_low_ema >= 0.65:
    candidate_mode = OperatingMode.CLEAR_NORMAL

# Degraded / Pocket Occluded Path
elif rolloff_ema < 0.14 and (high_ema < 0.060 or mid_to_low_ema < 0.60):
    candidate_mode = OperatingMode.DEGRADED_OCCLUDED

# Transition / Intermediate State
else:
    candidate_mode = OperatingMode.UNKNOWN
```

---

## 4. Condition-Adaptive Finite State Machine (`ConditionAdaptiveFSMV5`)

The FSM manages event lifecycles across five formal states: `IDLE`, `CANDIDATE`, `CONFIRMED`, `DECAY`, and `COOLDOWN`.

### 4.1 Mode-Specific Policy Matrix

| Policy Parameter | `CLEAR_NORMAL` | `DEGRADED_OCCLUDED` | `UNKNOWN` | Operational Purpose |
| :--- | :---: | :---: | :---: | :--- |
| **`threshold_base`** | **0.70** | **0.62** | **0.68** | Higher barrier in clear air prevents false triggers. |
| **`single_impulse_min_score`** | **0.70** | **0.62** | **0.68** | Direct impulse confirmation threshold. |
| **`single_impulse_min_crest_db`** | **13.5 dB** | **11.5 dB** | **13.0 dB** | Pocket audio dampens crest; clear audio requires peakiness. |
| **`energy_decay_db`** | **8.5 dB** | **7.0 dB** | **8.0 dB** | Multi-window energy decay verification. |
| **`max_candidate_windows`** | 3 | 3 | 3 | Maximum candidate evaluation window. |
| **`cooldown_seconds`** | 0.80 s | 0.80 s | 0.80 s | Duplicate-alert suppression interval. |

### 4.2 State Transition Invariants
1. **Candidate-Bound Crest Factor:** Crest factor is recorded and attributed strictly at the timestamp of the triggering window, eliminating the historical bug where crest factor was sampled during decay tails.
2. **Mode-Invariance During Events:** If a mode change occurs while the FSM is in `CANDIDATE` or `CONFIRMED`, the active event uses the policy under which it was initiated. Mode changes never abort active candidates or artificially confirm pending ones.

---

## 5. Enhanced Semantic Suppression (`CalibratedSemanticSuppressionV5`)

### 5.1 Glass Shatter Suppression Fix
In V4, the ballistic override rule `bal_s < 0.20` prevented glass shatter suppression because YAMNet's explosive crack classes (434: `Crack`, 436: `Sharp crack`) were included in $p_{\text{bal}}$, causing $p_{\text{bal}}$ to spike to $\sim 0.50$.

V5 fixes this logic:
```python
# V5 Calibrated Glass Shatter Suppression
if glass_s >= 0.30 and high_band_ratio >= 0.30:
    # Protect genuine gunshots only if pure gunshot classes are active
    # or if ballistic score exceeds glass score
    if glass_s > bal_s or gun_s < 0.20:
        multiplier = 0.35
        adjusted_score *= multiplier
```

### 5.2 Low-Frequency Rumble & Thunder Suppression
To catch distant thunder and heavy diesel machinery where YAMNet's semantic thunder score is weak ($p_{\text{thunder}} < 0.25$):
```python
# Physical Low-Rumble Gate
if low_band_ratio >= 0.65 and mid_to_low < 0.55 and gun_s < 0.15:
    adjusted_score *= 0.30
```

---

## 6. Real-Time Latency & Production Profile

Across 148 evaluations of 2–4 second audio files on a standard CPU:
* **Feature Extraction & YAMNet Inference:** $11.2\text{ ms}$ per 480 ms hop.
* **Condition Estimator Update:** $< 0.05\text{ ms}$.
* **FSM Step:** $< 0.02\text{ ms}$.
* **Total Per-Hop Latency:** **$< 15\text{ ms}$**, representing **$< 3.2\%$ CPU budget** on a 480 ms streaming audio frame.

---

*Mandatory Safety Designation: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.*

