# Implementation Notes: Detector Improvement V7

**RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.**

> [!WARNING]
> **RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.**
> This software is uncertified research code developed strictly for acoustic signal processing and forensic audio research. It must never be deployed for autonomous emergency dispatch, police tactical response, active-shooter alerting, automated evacuation, building lockdown, or life-critical physical security. Use lawfully obtained recordings and safe audio playback only. Live-fire testing and hazardous acoustic experiments are strictly prohibited.

---

## 1. System Overview & Architecture

**Detector Improvement V7** is an edge-compatible acoustic event detection pipeline engineered for robust gunshot detection under non-stationary environmental noise, severe physical occlusion, and pyrotechnic challenge conditions.

The pipeline processes continuous or discrete audio through a single-pass streaming architecture operating on $0.96\text{s}$ analysis windows ($15,360$ samples at $16\text{ kHz}$) with a $50\%$ hop size ($0.48\text{s}$ / $7,680$ samples).

```
Raw Audio Stream (16 kHz, 0.96s / 50% hop)
       │
       ├──> [Physical DSP Engine] ───────> 10 Physical Acoustic Metrics
       │                                   (Crest, Flatness, Energy Ratios, Rolloff, Centroid)
       │                                           │
       ├──> [YAMNet Backbone]                      │
       │    ├── 521 AudioSet Class Probabilities ──┼──> [Online Condition Estimator V7]
       │    └── 1024-dim Embeddings                │    (CLEAR / OCCLUDED / UNKNOWN)
       │               │                           │
       │               v                           │
       │    [4-Way Base Model Ensemble]            │
       │    (MLP + CatBoost + LightGBM + XGBoost)  │
       │               │                           │
       │               v                           │
       └────> [Calibrated Fusion Head] <───────────┘
                       │
                       v (Raw Confidence Score [0.0, 1.0])
                       │
       ┌───────────────┴───────────────────────────┐
       │   Calibrated Semantic Suppression V7      │
       │   - Ballistic Shockwave Override          │
       │   - Reverb Thunder Protection             │
       │   - Sub-Bass Backfire Discrimination      │
       │   - Saturation Coherence Safeguard        │
       └───────────────┬───────────────────────────┘
                       │
                       v (Calibrated Adjusted Score)
                       │
       ┌───────────────┴───────────────────────────┐
       │     Condition-Adaptive FSM V7             │
       │     - Mode-Specific Threshold Policies    │
       │     - Dual-Tier Single-Impulse Bypass     │
       │     - Multi-Window Candidate Pool         │
       │     - 1.50s Refractory Cooldown           │
       └───────────────┬───────────────────────────┘
                       │
                       v
             CONFIRMED EVENT STREAM
```

---

## 2. Module Decomposition

### 2.1 Physical DSP Engine (`compute_physical_acoustic_features_v7`)
The physical feature engine computes 10 deterministic DSP metrics from the $15,360$-sample Hanning-windowed FFT:
1. `crest_db`: Waveform peak-to-RMS energy ratio in decibels ($20 \log_{10}(peak / rms)$).
2. `flatness`: Wiener spectral flatness ratio (geometric mean divided by arithmetic mean of power spectrum).
3. `high_ratio`: Fractional power in high-frequency band ($f \ge 2500\text{ Hz}$).
4. `mid_ratio`: Fractional power in mid-frequency band ($500\text{ Hz} \le f < 2500\text{ Hz}$).
5. `low_ratio`: Fractional power in low-frequency band ($f < 500\text{ Hz}$).
6. `mid_to_low`: Power ratio between mid and low bands ($\frac{mid + 10^{-4}}{low + 10^{-4}}$).
7. `channel_rolloff`: High-to-mid band ratio ($\frac{high + 10^{-4}}{mid + 10^{-4}}$).
8. `centroid_hz`: Spectral centroid representing brightness center of gravity.
9. `rms`: Root-mean-square amplitude.
10. `peak`: Peak absolute amplitude.

### 2.2 Online Condition Estimator (`ConditionEstimatorV7`)
Tracks the acoustic transmission channel using asymmetric exponential moving average (EMA) smoothing ($\alpha = 0.20$):
- **Hysteresis Counters:**
  - `hysteresis_occluded = 3`: Requires 3 consecutive windows ($1.44\text{s}$) of acoustic attenuation ($rolloff_{ema} < 0.14 \land high_{ema} < 0.055 \land mid_{ema} \ge 0.35$) before entering `DEGRADED_OCCLUDED`.
  - `hysteresis_clear = 2`: Requires 2 consecutive windows ($0.96\text{s}$) of broadband transmission ($rolloff_{ema} \ge 0.20 \land high_{ema} \ge 0.075 \land mid\_to\_low_{ema} \ge 0.60$) before entering `CLEAR_NORMAL`.
  - `hysteresis_rumble = 2`: 2 consecutive windows of dominant low-frequency rumble ($lo \ge 0.70 \land mid\_to\_low < 0.50$) resets the channel to conservative `UNKNOWN` mode.

### 2.3 Calibrated Semantic Suppression (`CalibratedSemanticSuppressionV7`)
Applies hierarchical physical-semantic gating to raw fusion scores:
1. **Silence Gating:** If $rms < 10^{-4} \lor peak < 10^{-3}$, immediately returns score $0.0$ and category `"zero_energy_silence"`.
2. **Confirmed Event Immunity:** Windows during an active event state maintain unattenuated confidence to prevent mid-burst dropout.
3. **Ballistic Shockwave Pyrotechnic Override:**
   - Evaluates:
     $$\text{is\_ballistic\_shockwave} = (bal\_s \ge 0.40) \land (bal\_s \ge fw\_s \times 0.85)$$
   - If true, fireworks attenuation is completely bypassed.
   - If false, standard fireworks checks apply:
     - Dominant: $fw\_s \ge 0.45 \land fw\_s / pure\_gun \ge 1.8 \implies \times 0.15$.
     - Standard: $fw\_s \ge 0.25 \land fw\_s / pure\_gun \ge 2.5 \implies \times 0.30$.
4. **Sub-Bass Backfire & Thud Discrimination:**
   - Evaluates Cap Gun pop dominance:
     $$cap\_gun \ge 0.35 \land lo \ge 0.70 \land (cap\_gun \ge 1.5 \times pure\_gun \lor pure\_gun < 0.20)$$
   - Attenuates by $0.25\times$, eliminating urban automotive backfires.
5. **Reverberation Thunder Protection:**
   - Physical low-pass tail: $lo \ge 0.65 \land mid\_to\_low < 0.55$.
   - Attenuation is applied only if $pure\_gun < 0.15 \land bal\_s < 0.20 \land \neg \text{is\_ballistic\_shockwave}$.
6. **Saturated Ballistic Coherence:**
   - For linear waveforms: $pure\_gun < 0.08 \land bal\_s < 0.10 \implies \times 0.20$.
   - For saturated waveforms ($peak \ge 0.30 \lor crest \ge 15.0\text{ dB}$): threshold drops to $pure\_gun < 0.04 \land bal\_s < 0.04$.

### 2.4 Condition-Adaptive FSM (`ConditionAdaptiveFSMV7`)
Deterministic state machine enforcing refractory timing and dynamic confirmation thresholds:
- **UNKNOWN Mode:**
  - $th_{base} = 0.70, confirm\_wins = 2, cooldown = 1.50\text{s}$.
  - Single Impulse Standard: $crest \ge 13.5\text{ dB}$.
  - Single Impulse High-Confidence Tier: If $score \ge 0.85$, $crest \ge 11.5\text{ dB}$.
- **DEGRADED_OCCLUDED Mode:**
  - $th_{base} = 0.62, confirm\_wins = 2, single\_crest = 10.5\text{ dB}, cooldown = 1.50\text{s}$.
- **CLEAR_NORMAL Mode:**
  - $th_{base} = 0.70, confirm\_wins = 2, single\_crest = 12.0\text{ dB}, cooldown = 1.50\text{s}$.

---

## 3. Configuration Specification (`config_improvement_v7.json`)

```json
{
  "detector_name": "detector_improvement_v7",
  "version": "7.0.0",
  "safety_designation": "RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY",
  "created_at": "2026-11-16",
  "condition_estimator": {
    "enabled": true,
    "alpha": 0.20,
    "hysteresis_windows_occluded": 3,
    "hysteresis_windows_clear": 2,
    "hysteresis_windows_rumble": 2
  },
  "mode_policies": {
    "CLEAR_NORMAL": {
      "threshold_base": 0.70,
      "threshold_high": 0.85,
      "single_impulse_min_crest_db": 12.0,
      "single_impulse_high_conf_crest_db": 11.0,
      "confirm_windows": 2,
      "cooldown_secs": 1.50
    },
    "DEGRADED_OCCLUDED": {
      "threshold_base": 0.62,
      "threshold_high": 0.80,
      "single_impulse_min_crest_db": 10.5,
      "single_impulse_high_conf_crest_db": 10.0,
      "confirm_windows": 2,
      "cooldown_secs": 1.50
    },
    "UNKNOWN": {
      "threshold_base": 0.70,
      "threshold_high": 0.85,
      "single_impulse_min_crest_db": 13.5,
      "single_impulse_high_conf_crest_db": 11.5,
      "confirm_windows": 2,
      "cooldown_secs": 1.50
    }
  },
  "suppression_rules": {
    "ballistic_coherence": {
      "max_pure_gun": 0.08, "max_ballistic": 0.10,
      "saturation_pure_gun": 0.04, "saturation_ballistic": 0.04,
      "attenuation": 0.20
    },
    "sub_bass_thud": {
      "min_low_ratio": 0.70, "min_cap_gun": 0.35, "cap_to_pure_ratio": 1.5,
      "max_pure_gun": 0.20, "attenuation": 0.25
    },
    "thunder": {
      "low_band_threshold": 0.65, "mid_to_low_max": 0.55, "gun_score_max": 0.15,
      "ballistic_shockwave_max": 0.20, "attenuation": 0.30
    },
    "fireworks": {
      "dominant_threshold": 0.45, "dominant_ratio": 1.8, "dominant_attenuation": 0.15,
      "standard_threshold": 0.25, "standard_ratio": 2.5, "standard_attenuation": 0.30,
      "ballistic_override_threshold": 0.40, "ballistic_override_ratio": 0.85
    }
  }
}
```

---

## 4. Performance & Resource Footprint

- **Single Analysis Window Duration:** $0.96\text{s}$ ($15,360$ samples).
- **Hop Size:** $0.48\text{s}$ ($7,680$ samples).
- **Inference Latency per Window:** Mean $\approx 18.5\text{ ms}$ on standard x86-64 CPU.
- **Real-Time Factor (RTF):** $\approx 0.0385$ ($<4\%$ of real-time window budget).
- **Memory Consumption:** Model ensemble + YAMNet buffers $\approx 420\text{ MB}$ RAM.

