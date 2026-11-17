# Technical Implementation Notes: Detector Improvement V8

**RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.**

> [!WARNING]
> **RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.**
> This is an uncertified research prototype developed strictly for acoustic signal processing and forensic audio experimentation. It must never be deployed for autonomous emergency dispatch, police tactical response, active-shooter alerting, automated evacuation, building lockdown, or life-critical physical security. Use lawfully obtained recordings and safe audio playback only. Live-fire testing and hazardous acoustic experiments are strictly prohibited.

---

## 1. Architecture Overview

**Detector Improvement V8** is engineered to resolve the acoustic false-alarm regressions of V7 while preserving its genuine positive gunshot recovery across degraded, occluded, and field environments.

The V8 pipeline operates on streaming audio with a $0.96\text{s}$ analysis window ($15,360\text{ samples}$ at $16\text{ kHz}$) and a $0.48\text{s}$ hop size ($7,680\text{ samples}$).

```
Input Audio Stream (16 kHz, 0.96s / 0.48s hop)
  ├── 1. Physical DSP Metric Extraction (10 features)
  ├── 2. YAMNet Deep Feature Extraction (1024-dim embedding + 521 class scores)
  │     ├── 4-Way Ensemble (MLP, CatBoost, LightGBM, XGBoost)
  │     └── Calibrated Gradient Boosted Fusion Head -> Raw Gunshot Probability
  ├── 3. Stabilized Online Condition Estimator V8 (Anti-Chatter Hysteresis)
  │     └── Operating Mode: [CLEAR_NORMAL | DEGRADED_OCCLUDED | UNKNOWN]
  ├── 4. Calibrated Semantic Suppression V8
  │     ├── Zero-Energy Silence Gate
  │     ├── Calibrated Pyrotechnic Gating (Acoustic Spectral Profile)
  │     ├── Transient Acoustic Thunder & Rumble Gating
  │     ├── Glass Shatter Gating
  │     ├── Sub-Bass Automotive Backfire Discrimination
  │     └── Saturated Ballistic Coherence Safeguard
  └── 5. Condition-Adaptive Finite State Machine V8
        ├── Mode-Dependent Single Impulse Thresholding (13.5 dB in UNKNOWN)
        ├── Multi-Window Confirmation Clustering (gap <= 0.60s)
        └── 1.50s Refractory Cooldown Suppressing Duplicate Alerts
```

---

## 2. DSP Feature Extraction & Physical Metrics

For every $0.96\text{s}$ analysis window $x[n]$, V8 computes 10 physical DSP metrics:

1. **Peak Amplitude:**
   $$\text{Peak} = \max_n |x[n]|$$

2. **Root Mean Square (RMS) Energy:**
   $$\text{RMS} = \sqrt{\frac{1}{N} \sum_{n=0}^{N-1} x[n]^2}$$

3. **Crest Factor ($\text{dB}$):**
   $$\text{Crest}_{\text{dB}} = 20 \log_{10}\left(\frac{\text{Peak} + 10^{-6}}{\text{RMS} + 10^{-6}}\right)$$

4. **Tri-Band Power Spectral Decomposition:**
   Let $X[k]$ be the discrete Fourier transform of $x[n]$ with a Hanning window. Total power $P_{\text{tot}} = \sum_k |X[k]|^2$.
   - **Low Band ($< 500\text{ Hz}$):** $P_{\text{low}} = \sum_{f_k < 500} |X[k]|^2$, $\text{Low Ratio} = P_{\text{low}} / P_{\text{tot}}$
   - **Mid Band ($500 - 2500\text{ Hz}$):** $P_{\text{mid}} = \sum_{500 \le f_k < 2500} |X[k]|^2$, $\text{Mid Ratio} = P_{\text{mid}} / P_{\text{tot}}$
   - **High Band ($\ge 2500\text{ Hz}$):** $P_{\text{high}} = \sum_{f_k \ge 2500} |X[k]|^2$, $\text{High Ratio} = P_{\text{high}} / P_{\text{tot}}$

5. **Mid-to-Low Ratio ($m2l$):**
   $$m2l = \frac{\text{Mid Ratio} + 10^{-4}}{\text{Low Ratio} + 10^{-4}}$$

6. **High-Frequency Channel Rolloff Ratio:**
   $$\text{Rolloff} = \frac{\text{High Ratio} + 10^{-4}}{\text{Mid Ratio} + 10^{-4}}$$

7. **Wiener Spectral Flatness:**
   $$\text{Flatness} = \frac{\exp\left(\frac{1}{K}\sum_{k=0}^{K-1} \ln(|X[k]|^2 + 10^{-12})\right)}{\frac{1}{K}\sum_{k=0}^{K-1} |X[k]|^2 + 10^{-9}}$$

8. **Spectral Centroid ($\text{Hz}$):**
   $$\text{Centroid} = \frac{\sum_k f_k |X[k]|}{\sum_k |X[k]| + 10^{-9}}$$

---

## 3. Calibrated Semantic Suppression V8

### 3.1 Calibrated Pyrotechnic Gating (Shockwave Acoustic Profile)
In V7, AudioSet Class 420 (`Explosion`) was treated unconditionally as a ballistic shockwave, allowing chemical fireworks mortar blasts to bypass suppression.

In V8, pyrotechnic override requires physical proof of high-frequency supersonic shockwave propagation:
$$\text{is\_ballistic\_acoustics} = (m2l \ge 0.25 \land \text{Centroid} \ge 750\text{ Hz}) \lor (\text{Centroid} \ge 1200\text{ Hz})$$
$$\text{is\_ballistic\_shockwave} = (\text{pure\_gun} \ge 0.20) \lor (\text{bal\_s} \ge 0.40 \land \text{bal\_s} \ge \text{fw\_s} \times 0.85 \land \text{is\_ballistic\_acoustics})$$

If $\text{fw\_s} \ge 0.45$ and $\neg \text{is\_ballistic\_shockwave}$ and $\text{fw\_s} / (\text{pure\_gun} + 10^{-4}) \ge 1.8$:
$$S_{\text{adj}} = S_{\text{raw}} \times 0.15 \quad (\text{Dominant Fireworks Suppression})$$

If $\text{fw\_s} \ge 0.25$ and $\neg \text{is\_ballistic\_shockwave}$ and $\text{fw\_s} / (\text{pure\_gun} + 10^{-4}) \ge 2.2$:
$$S_{\text{adj}} = S_{\text{raw}} \times 0.30 \quad (\text{Standard Fireworks Suppression})$$

### 3.2 Transient Acoustic Thunder & Rumble Gating
Low-frequency urban clatter, thunderclaps, and vehicle rumbles frequently activate Class 420 or Class 429 (`Boom`). In V8, thunder suppression applies to all heavy low-frequency acoustic energy unless explicit gunshot transient physical or semantic evidence is present:
$$\text{is\_thun\_semantic} = (\text{thun\_s} \ge 0.20)$$
$$\text{is\_thun\_phys} = (\text{Low Ratio} \ge 0.65 \land m2l < 0.55)$$
$$\text{is\_gunshot\_transient} = (m2l \ge 0.40 \land \text{Centroid} \ge 750\text{ Hz} \land \text{Crest}_{\text{dB}} \ge 16.0) \lor (\text{pure\_gun} \ge 0.12) \lor (\text{Peak} \ge 0.30 \land \text{Crest}_{\text{dB}} \ge 12.0 \land \text{Centroid} \ge 600\text{ Hz})$$

If $(\text{is\_thun\_semantic} \lor \text{is\_thun\_phys}) \land \neg \text{is\_gunshot\_transient}$:
$$S_{\text{adj}} = S_{\text{raw}} \times 0.30 \quad (\text{Thunder Rumble Suppression})$$

### 3.3 Glass Shatter Gating
When sharp high-frequency glass breakage occurs:
$$\text{glass\_s} \ge 0.30 \land \text{High Ratio} \ge 0.25 \land \text{pure\_gun} < 0.20 \implies S_{\text{adj}} = S_{\text{raw}} \times 0.35$$

### 3.4 Saturated Ballistic Coherence Safeguard
For extreme amplitude clipped signals ($\text{Crest}_{\text{dB}} \ge 15.0\text{ dB} \lor \text{Peak} \ge 0.30$), the coherence threshold is relaxed from $0.08 / 0.10$ to $0.04 / 0.04$, protecting saturated muzzle blasts from distortion-induced suppression.

---

## 4. Condition-Adaptive Finite State Machine V8

The FSM tracks states $\mathcal{S} \in \{\text{IDLE}, \text{CANDIDATE}, \text{CONFIRMED}, \text{REFRACTORY}\}$.

### 4.1 Mode Policies Table

| Parameter | CLEAR_NORMAL | DEGRADED_OCCLUDED | UNKNOWN |
| :--- | :---: | :---: | :---: |
| Threshold Base ($T_{\text{base}}$) | $0.70$ | $0.62$ | $0.70$ |
| Threshold High ($T_{\text{high}}$) | $0.85$ | $0.80$ | $0.85$ |
| Threshold Off ($T_{\text{off}}$) | $0.40$ | $0.40$ | $0.40$ |
| Confirm Windows | 2 | 2 | 2 |
| Single Impulse Min Crest ($C_{\text{std}}$) | $12.0\text{ dB}$ | $10.5\text{ dB}$ | **$13.5\text{ dB}$** |
| High-Conf Single Crest ($C_{\text{high}}$) | $11.5\text{ dB}$ | $10.0\text{ dB}$ | **$12.0\text{ dB}$** (conditional) |
| Refractory Cooldown | $1.50\text{ s}$ | $1.50\text{ s}$ | $1.50\text{ s}$ |

### 4.2 Tightened High-Confidence Gating in UNKNOWN Mode
In UNKNOWN mode, a single isolated window can trigger an alert if:
$$\text{Crest}_{\text{dB}} \ge 13.5\text{ dB} \quad \text{OR} \quad (S_{\text{adj}} \ge 0.85 \land \text{Crest}_{\text{dB}} \ge 12.0\text{ dB} \land m2l \ge 0.35 \land \text{Centroid} \ge 750\text{ Hz})$$

Isolated mechanical impacts (crest $12.5 - 13.3\text{ dB}$, centroid $< 550\text{ Hz}$) fail this test and enter `CANDIDATE` state. Because they lack a second confirming window within $0.60\text{s}$, they cleanly decay to `IDLE` without issuing a false alert.

