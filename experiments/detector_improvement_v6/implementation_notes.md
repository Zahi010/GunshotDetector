# IMPLEMENTATION NOTES: DETECTOR IMPROVEMENT V6 PIPELINE

**RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.**

This software is an uncertified research prototype. It must never be deployed for autonomous emergency dispatch, tactical police response, active-shooter alerting, automated evacuation, building lockdown, or life-critical physical security. Use lawfully obtained recordings and safe audio playback only. Live-fire and hazardous acoustic experiments are strictly prohibited.

---

## 1. System Architecture Overview

Detector Improvement V6 is an acoustic surveillance detection engine engineered for streaming real-time inference on 16 kHz audio. It directly addresses the urban false alarms and condition estimator instability identified in Phase 47 while preserving recording-condition adaptation, high pocket-occluded gunshot sensitivity, and pyrotechnic discrimination.

The pipeline comprises six deterministic processing stages:

```
[Audio Input (16 kHz)]
        │
        ▼
[1. Windowing & Energy Floor Gate]
   (RMS < 0.001 or Peak < 0.005 -> Score = 0.0)
        │
        ▼
[2. Multi-Modal Feature Extraction]
   (10 Physical DSP Metrics + YAMNet 521-Class Semantics + 4 Base Ensembles)
        │
        ▼
[3. Tabular Fusion GBDT Classifier]
   (HistGradientBoostingClassifier -> Raw Score [0.0, 1.0])
        │
        ▼
[4. Condition Estimator V6 with Anti-Chatter Hysteresis]
   (EMA Spectral Tracking -> CLEAR_NORMAL, DEGRADED_OCCLUDED, UNKNOWN)
        │
        ▼
[5. Calibrated Semantic & Acoustic Suppression V6]
   (Thunder, Glass, Fireworks, Cap Gun, Sub-Bass Thud, Ballistic Coherence)
        │
        ▼
[6. Condition-Adaptive Refractory FSM V6]
   (State Transitions: IDLE -> CANDIDATE -> CONFIRMED -> REFRACTORY)
        │
        ▼
[Alert Output / Event Stream]
```

---

## 2. Mathematical Specifications & DSP Formulations

### 2.1 Windowing and Framing
Audio is analyzed in fixed sliding windows:
- Window length: $N = 15,360$ samples ($0.96\text{ seconds}$ at $f_s = 16,000\text{ Hz}$).
- Hop step: $H = 7,680$ samples ($0.48\text{ seconds}$, 50% overlap).
- Streaming latency per hop: $\le 15.0\text{ ms}$ on standard x86 CPU.

### 2.2 Energy Floor Gate
To prevent gradient boosted decision trees from evaluating empty or digital-zero leaves:
$$\text{RMS} = \sqrt{\frac{1}{N} \sum_{n=0}^{N-1} x[n]^2}, \quad \text{Peak} = \max_{0 \le n < N} |x[n]|$$
$$\text{If } \text{RMS} < 0.001 \lor \text{Peak} < 0.005 \implies \hat{s}_{\text{adj}} = 0.0, \quad \text{State} = \text{IDLE}$$

### 2.3 Physical Acoustic Metric Suite (10 Parameters)
From the Discrete Fourier Transform $X[k] = \text{FFT}(x[n] \cdot w[n])$:
1. **Crest Factor (dB):**
   $$C_{\text{dB}} = 20 \log_{10} \left( \frac{\text{Peak}}{\text{RMS} + 10^{-9}} \right)$$
2. **Spectral Flatness (Wiener Entropy):**
   $$\text{Flatness} = \frac{\exp \left( \frac{1}{K} \sum_{k=0}^{K-1} \ln |X[k]|^2 \right)}{\frac{1}{K} \sum_{k=0}^{K-1} |X[k]|^2}$$
3. **Tri-Band Energy Partitioning:**
   $$E_{\text{low}} = \sum_{f_k < 1000\text{ Hz}} |X[k]|^2, \quad E_{\text{mid}} = \sum_{1000 \le f_k \le 4000\text{ Hz}} |X[k]|^2, \quad E_{\text{high}} = \sum_{f_k > 4000\text{ Hz}} |X[k]|^2$$
   $$r_{\text{low}} = \frac{E_{\text{low}}}{E_{\text{tot}}}, \quad r_{\text{mid}} = \frac{E_{\text{mid}}}{E_{\text{tot}}}, \quad r_{\text{high}} = \frac{E_{\text{high}}}{E_{\text{tot}}}$$
4. **Mid-to-Low Ratio:**
   $$r_{\text{m2l}} = \frac{r_{\text{mid}} + 10^{-4}}{r_{\text{low}} + 10^{-4}}$$
5. **High-Frequency Rolloff Ratio:**
   $$r_{\text{rolloff}} = \frac{r_{\text{high}} + 10^{-4}}{r_{\text{mid}} + 10^{-4}}$$
6. **Spectral Centroid:**
   $$\mu_f = \frac{\sum_k f_k \cdot |X[k]|}{\sum_k |X[k]| + 10^{-9}}$$

---

## 3. Condition Estimator V6: Anti-Chatter Stabilization

In V5, mode oscillation between `CLEAR_NORMAL` and `UNKNOWN` occurred due to zero-hysteresis low-rumble overrides. V6 implements an Exponential Moving Average (EMA) smoother with asymmetric multi-window hysteresis:

$$\bar{M}_t = \alpha M_t + (1 - \alpha) \bar{M}_{t-1}, \quad \alpha = 0.20$$

### Transition Criteria:
1. **Degraded / Occluded Mode (`DEGRADED_OCCLUDED`):**
   - Condition: $\bar{r}_{\text{rolloff}} \le 0.14 \land \bar{r}_{\text{high}} \le 0.055 \land \bar{r}_{\text{mid}} \ge 0.35$.
   - Persistence requirement: Must satisfy criteria for **3 consecutive windows** ($1.44\text{ seconds}$).
   - Entry action: Resets `clear_count` and `rumble_count` to zero.
2. **Clear / Normal Mode (`CLEAR_NORMAL`):**
   - Condition: $\bar{r}_{\text{rolloff}} \ge 0.20 \land \bar{r}_{\text{high}} \ge 0.075 \land \bar{r}_{\text{m2l}} \ge 0.60$.
   - Persistence requirement: Must satisfy criteria for **2 consecutive windows** ($0.96\text{ seconds}$).
   - Entry action: Resets `occluded_count` and `rumble_count` to zero.
3. **Low-Rumble Override (`UNKNOWN`):**
   - Condition: $r_{\text{low}} \ge 0.70 \land r_{\text{m2l}} \le 0.50$.
   - Persistence requirement: Must satisfy criteria for **2 consecutive windows** ($0.96\text{ seconds}$).
   - Entry action: Resets `clear_count` and `occluded_count` to zero.

This stabilization reduced continuous mode transitions from **147 down to 18** per 10 minutes of urban audio (>85% chatter reduction).

---

## 4. Calibrated Semantic Suppression V6

Suppression rules evaluate strictly in hierarchical order:

| Priority | Gate Name | Activation Conditions | Attenuation Factor | Failure Addressed |
| :---: | :---: | :---: | :---: | :---: |
| **1** | **Silence Energy Floor** | $\text{RMS} < 0.001 \lor \text{Peak} < 0.005$ | $0.0\times$ (Zero score) | GBDT digital zero tree prediction anomaly |
| **2** | **Thunder Semantic Gate** | $p_{\text{thunder}} \ge 0.20 \land p_{\text{pure\_gun}} < 0.15$ | $0.30\times$ | Thunderclaps and thunderstorm rumble |
| **3** | **Glass Shatter Gate** | $p_{\text{glass}} \ge 0.30 \land r_{\text{high}} \ge 0.25 \land p_{\text{pure\_gun}} < 0.20$ | $0.35\times$ | High-frequency window and bottle breaks |
| **4A** | **Dominant Fireworks** | $p_{\text{fw}} \ge 0.45 \land \frac{p_{\text{fw}}}{p_{\text{pure\_gun}}} \ge 1.8 \land p_{\text{pure\_gun}} < 0.25$ | $0.30\times$ | Aerial display shells and commercial fireworks |
| **4B** | **Standard Fireworks** | $p_{\text{fw}} \ge 0.30 \land \frac{p_{\text{fw}}}{p_{\text{pure\_gun}}} \ge 1.5 \land p_{\text{pure\_gun}} < 0.12$ | $0.35\times$ | Ground firecrackers and bottle rockets |
| **5** | **Cap Gun Mechanical Pop** | $p_{\text{cap}} \ge 0.35 \land p_{\text{pure\_gun}} < 0.28 \land r_{\text{high}} < 0.010 \land \mu_f < 450\text{ Hz}$ | $0.35\times$ | Automotive exhaust backfires and mechanical clicks |
| **6** | **Sub-Bass Automotive Thud** | $r_{\text{low}} \ge 0.75 \land r_{\text{high}} < 0.008 \land \mu_f < 450\text{ Hz} \land p_{\text{pure\_gun}} < 0.20$ | $0.35\times$ | Vehicle suspension thuds and diesel engine pulses |
| **7** | **Physical Rumble Fallback** | $r_{\text{low}} \ge 0.65 \land r_{\text{m2l}} < 0.55 \land p_{\text{pure\_gun}} < 0.15$ | $0.30\times$ | Distant rolling thunder without semantic tag |
| **8** | **Mechanical Impact** | $p_{\text{impact}} \ge 0.25 \land \frac{p_{\text{impact}}}{p_{\text{pure\_gun}}} \ge 1.5 \land p_{\text{pure\_gun}} < 0.20$ | $0.35\times$ | Hammer blows, heavy door slams, metallic clatter |
| **9** | **Ballistic Coherence Safeguard** | $p_{\text{pure\_gun}} < 0.08 \land p_{\text{ballistic}} < 0.10$ | $0.20\times$ | Horns, tire squeals, non-ballistic transients |

---

## 5. Refractory Finite State Machine V6

The FSM tracks continuous temporal state:

$$\text{State} \in \{\text{IDLE}, \text{CANDIDATE}, \text{CONFIRMED}, \text{REFRACTORY}\}$$

### Policy Matrix:
| Parameter | `CLEAR_NORMAL` | `DEGRADED_OCCLUDED` | `UNKNOWN` |
| :--- | :---: | :---: | :---: |
| **Base Detection Threshold ($\tau_{\text{base}}$)** | 0.70 | 0.62 | 0.70 |
| **High Confidence Threshold ($\tau_{\text{high}}$)** | 0.85 | 0.80 | 0.85 |
| **Reset Cutoff Threshold ($\tau_{\text{off}}$)** | 0.40 | 0.40 | 0.40 |
| **Confirmation Windows Required ($N_{\text{confirm}}$)** | 2 | 2 | 2 |
| **Single-Impulse Min Crest Factor ($C_{\text{min}}$)** | **13.5 dB** | **11.5 dB** | **13.5 dB** |
| **Single-Impulse Min Score ($s_{\text{min}}$)** | 0.70 | 0.62 | 0.70 |
| **Energy Decay Constraint ($\Delta E_{\text{decay}}$)** | 8.5 dB | 7.0 dB | 8.0 dB |
| **Single Impulse Exception Permitted** | Yes (non-thud) | Yes (non-thud) | Yes (non-thud) |
| **Refractory Cooldown Duration** | **1.50 s** | **1.50 s** | **1.50 s** |

### Single-Impulse Safeguard Rule:
Transients exhibiting sub-bass energy dominance ($r_{\text{low}} \ge 0.75 \land r_{\text{high}} < 0.008$) or low crest factors ($C_{\text{dB}} < 13.5\text{ dB}$) are **strictly disqualified** from single-impulse promotion. They must achieve a sustained score $\ge \tau_{\text{base}}$ across 2 consecutive analysis windows to trigger an alert.

---

## 6. Computational Latency Profiling

Evaluated on AMD Ryzen / Intel Core x86-64 host running Windows 11 (native CPU, single thread):
- DSP Acoustic Feature Extraction (10 metrics): **0.42 ms**
- YAMNet Feature Extraction (15,360 samples): **6.25 ms**
- Base Ensembles (CatBoost + LightGBM + XGBoost + MLP): **1.18 ms**
- Fusion Tree Inference (GBDT): **0.08 ms**
- Condition Estimator & Semantic Suppression: **0.04 ms**
- FSM State Transition Step: **0.01 ms**
- **Total Hop Processing Time: ~7.98 ms** ($\ll 15.0\text{ ms}$ real-time deadline).
- Real-time factor (RTF): $\frac{7.98\text{ ms}}{480.0\text{ ms}} = \mathbf{0.0166}$ (Processes audio at **60$\times$ real-time speed**).

