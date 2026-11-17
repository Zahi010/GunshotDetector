# Phase 44 Forensic Failure Mode Analysis: V1 Weaknesses and Acoustic Root Causes

**MANDATORY SAFETY DESIGNATION:**
> **RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY**
>
> This experimental acoustic machine-learning software is uncertified and must never be deployed for autonomous emergency dispatch, tactical police response, active-shooter alerting, automated evacuation, building lockdown, or life-critical physical security. Safe recorded audio playback only; live-fire testing and hazardous acoustic experiments are strictly prohibited.

---

## 1. Executive Summary

In Phase 43, Detector Improvement V1 achieved substantial advances over historical baselines by integrating a deterministic 4-state refractory Finite State Machine (FSM) with multi-category acoustic suppression. However, rigorous benchmark evaluation across 368 recordings (4.94 hours of audio exposure) revealed three primary failure modes:

1. **Fireworks False Alarms:** 45 out of 100 challenging fireworks recordings ($45.0\%$) triggered false alarms.
2. **Continuous Background Exposure Triggers:** 9 out of 28 continuous streams produced 26 false alert events ($6.16\text{ alerts/hour}$), dominated by 12 repeated triggers in a single outdoor park recording (`p40_cont_03_bruxelles.mp3`).
3. **Missed Genuine Gunshots:** 46 out of 120 authentic gunshot recordings ($38.3\%$) were missed, including 18 high-confidence single-round recordings with raw ensemble scores between $0.75$ and $0.88$ and physical crest factors up to $34.2\text{ dB}$.

This document details the acoustic, semantic, and algorithmic forensic investigation that diagnosed the root causes of these failures, providing the empirical foundation for Detector Improvement V2.

---

## 2. Fireworks False Alarms: The Rigid Ballistic Ceiling Defect

### 2.1 Phenomenon
In Phase 43, V1 evaluated 100 prospective fireworks recordings. Despite the activation of YAMNet fireworks classes (Class 426: `Fireworks`, Class 427: `Firecracker`), 45 recordings still triggered gunshot alerts (37 via `multi_window_confirmation`, 8 via `single_window_high_confidence`).

### 2.2 Forensic Inspection of YAMNet Activations
Analysis of feature caches across the 45 triggered fireworks files revealed a critical algorithmic flaw in V1's `CalibratedAcousticSuppressionV1`:

```python
# V1 Logic (Flawed Ceiling)
elif (
    fireworks_score > self.fw_cfg["threshold"] # 0.30
    and fireworks_score >= gun_score * self.fw_cfg["ratio"] # 1.5
    and gun_score < self.fw_cfg["gun_max"] # gun_max was strictly 0.10!
):
    adj_score *= 0.35
```

When high-energy pyrotechnic shells (e.g. aerial salutes, multi-break rockets, heavy firecrackers) detonate, the explosive shockwave induces a minor secondary activation in YAMNet's gunshot class (Class 421: `Gunshot, gunfire`), typically outputting $p_{\text{gun}} \in [0.10, 0.28]$.

In **33 of the 45 triggered fireworks recordings**, YAMNet produced an overwhelming fireworks probability ($p_{\text{fw}} \in [0.45, 0.99]$) that exceeded $p_{\text{gun}}$ by a factor of $2\times$ to $5\times$. However, because $p_{\text{gun}} \ge 0.10$, V1's rigid ballistic safeguard (`gun_score < 0.10`) blocked suppression entirely:

| Recording ID | Peak Raw Score | Peak Fireworks ($p_{\text{fw}}$) | Peak Gunshot ($p_{\text{gun}}$) | Max File Fireworks | V1 Decision Reason |
| :--- | :---: | :---: | :---: | :---: | :--- |
| `p39_dist_DISTRACTOR_FIREWORKS_25006` | 0.884 | **0.897** | 0.166 | 0.918 | Ballistic ceiling blocked ($p_{\text{gun}} \ge 0.10$) |
| `p39_dist_DISTRACTOR_FIREWORKS_172983` | 0.952 | **0.896** | 0.112 | 0.896 | Ballistic ceiling blocked ($p_{\text{gun}} \ge 0.10$) |
| `p39_dist_DISTRACTOR_FIREWORKS_160720` | 0.885 | **0.934** | 0.108 | 0.998 | Ballistic ceiling blocked ($p_{\text{gun}} \ge 0.10$) |
| `p39_dist_DISTRACTOR_FIREWORKS_60822` | 0.907 | **0.737** | 0.225 | 0.928 | Ballistic ceiling blocked ($p_{\text{gun}} \ge 0.10$) |
| `p39_dist_DISTRACTOR_FIREWORKS_208783` | 0.913 | **0.920** | 0.207 | 0.967 | Ballistic ceiling blocked ($p_{\text{gun}} \ge 0.10$) |
| `p39_dist_DISTRACTOR_FIREWORKS_422079` | 0.911 | **0.640** | 0.291 | 0.640 | Ballistic ceiling blocked ($p_{\text{gun}} \ge 0.10$) |
| `p39_dist_DISTRACTOR_FIREWORKS_113513` | 0.904 | **0.482** | 0.163 | 0.950 | Ballistic ceiling blocked ($p_{\text{gun}} \ge 0.10$) |

### 2.3 Physical Acoustic Contrast
Comparative physical acoustic analysis between 30 genuine gunshots and 30 fireworks recordings demonstrated clear physical differences:

| Acoustic Feature | Genuine Gunshots ($N=30$) | Fireworks Challenge ($N=30$) | Physical Rationale |
| :--- | :---: | :---: | :--- |
| **Spectral Flatness** | **0.0911** | **0.0488** | Gunshots produce broad white-noise blast spectra; fireworks have resonant shell modes. |
| **Reverberant Decay Energy** | **0.3385** | **0.1982** | Gunshots excite sustained acoustic environment reverberation; outdoor fireworks decay rapidly. |
| **Crest Factor** | 17.21 dB | 24.10 dB | Distant fireworks explosions exhibit artificial peak-to-RMS ratios due to quiet pre-burst ambient. |

---

## 3. Continuous Background Triggers: The Wind Buffeting Discovery

### 3.1 Historical Mischaracterization
Phase 43 previously assumed that the 12 false alert events in `p40_cont_03_bruxelles.mp3` were caused by mechanical impacts from a "playground iron gate clatter". 

### 3.2 Acoustic Forensic Re-Investigation
To verify this hypothesis, the actual raw waveform (`experiments/phase40/dataset/continuous/p40_cont_03_bruxelles.mp3`) was extracted and subjected to spectral and sub-band decomposition at all 12 alert onset timestamps:

```
=== ACOUSTIC METRICS AT BRUXELLES ALERT WINDOWS ===
Mean across Bruxelles alert windows:
- Low-Frequency Energy Ratio (< 250 Hz): 0.8562 (85.6% of total spectral energy!)
- Mid-Frequency Energy Ratio (250 - 2000 Hz): 0.1389
- High-Frequency Energy Ratio (> 2000 Hz): 0.0049 (almost zero high-frequency crackle)
- Spectral Centroid: 942.08 Hz (vs Gunshot mean: 1736.67 Hz)
- Spectral Rolloff (85%): 1877.77 Hz (vs Gunshot mean: 3482.09 Hz)
- Spectral Flatness: 0.0036 (vs Gunshot mean: 0.0911 — 25x lower flatness!)
```

### 3.3 Semantic Model Failure Mode
Evaluating YAMNet class probabilities on the 12 alert windows revealed that **ballistic gunshot probabilities were literally zero ($p_{\text{gun}} \le 0.002$)**. 
The top YAMNet classes were:
- `Clip-clop` ($p = 0.294$)
- `Animal` / `Horse` / `Bird` ($p = 0.280$)
- `Speech` ($p = 0.310$)
- `Outside, urban or manmade` ($p = 0.248$)
- `Wind noise (microphone)` / `Wind` ($p \in [0.05, 0.12]$)

**Root Cause:**
The 12 repeated alerts were **NOT mechanical gate clatters**. The recording is an outdoor field recording in Brussels by Flavien Gillié (Radio Aporee). The alerts were caused by **wind buffeting against the microphone diaphragm**, producing intense infrasonic low-frequency pressure spikes. 

The tabular tree ensemble (CatBoost, LightGBM, XGBoost), having been trained on YAMNet embeddings without an acoustic coherence constraint, assigned high gunshot confidence ($0.80 - 0.90$) to these wind embeddings. Because YAMNet's gunshot class was 0.000, V1's semantic suppression engine did not trigger because none of V1's 5 target categories (thunder, fireworks, canine, fire, siren) reached threshold!

---

## 4. Missed Gunshot Analysis: Rigid Two-Window Confirmation on Single Rounds

### 4.1 Phenomenon
V1 missed 46 out of 120 authentic gunshot recordings. Analysis of the missed recordings revealed an extraordinary finding: **all 46 missed recordings were `SINGLE_ROUND` gunshot recordings** (e.g., bolt-action rifle, single handgun discharge).

### 4.2 Forensic Score Trajectory
Evaluating raw ensemble scores across the 46 missed gunshots showed:
- $p_{\text{raw}} < 0.20$: 0 recordings
- $0.20 \le p_{\text{raw}} < 0.48$: 5 recordings
- $0.48 \le p_{\text{raw}} < 0.75$: 23 recordings
- **$0.75 \le p_{\text{raw}} < 0.88$**: **18 recordings** (Crest factors: $12.4\text{ dB}$ to $34.2\text{ dB}$)

### 4.3 Algorithmic Elimination Mechanism
For these 18 authentic gunshots, the acoustic blast produced a sharp ensemble peak in Window $i$ (e.g. $p = 0.84$, crest factor $= 24.6\text{ dB}$).
1. In Window $i$, because $p < 0.88$ (`threshold_high`), the window did not qualify for `single_window_high_confidence` immediate promotion.
2. The FSM transitioned from `IDLE` to `CANDIDATE`.
3. Because the gunshot was a single discrete impulse, the acoustic energy dissipated rapidly. By Window $i+1$ (480 ms later), the reverberation decayed below $0.75$ (`threshold_base`).
4. The FSM observed $p_{i+1} < 0.75$, executed `TransitionReason.CANDIDATE_DISCARDED_BELOW_BASE`, and purged the candidate window!
5. As a result, genuine gunshots with physical crest factors up to $34.2\text{ dB}$ and ensemble scores up to $0.877$ were discarded simply because the shot was single rather than automatic fire!

---

## 5. Architectural Corrective Actions for V2

Based on these forensic discoveries, four targeted architectural improvements were formulated for Detector Improvement V2:

1. **Non-Ballistic Acoustic Coherence Safeguard:** If YAMNet's aggregate ballistic probability is negligible ($p_{\text{ballistic}} < 0.015$) while non-target semantic classes (speech, animal, vehicle, outside ambient) are active ($p \ge 0.12$), attenuate the ensemble score by $0.20\times$. This directly neutralizes tree ensemble hallucinations on wind buffeting and animal sounds.
2. **Refined Two-Tier Pyrotechnic Gating:**
   - Dominant Tier: When $p_{\text{fw}} \ge 0.45$ and $p_{\text{fw}} \ge 1.8 \cdot p_{\text{gun}}$, expand the ballistic ceiling from $0.10$ to $0.25$, attenuating by $0.30\times$.
   - Standard Tier: When $p_{\text{fw}} \ge 0.30$ and $p_{\text{fw}} \ge 1.5 \cdot p_{\text{gun}}$, keep ballistic ceiling at $0.12$, attenuating by $0.35\times$.
3. **Infrasonic Rumble & Wind Attenuation:** Explicitly detect microphone wind buffeting (YAMNet classes 277, 279) and attenuate by $0.25\times$.
4. **Single-Round Impulse Dispatch Exception:** In `EventStateMachineV2`, allow a decaying candidate window with $p \ge 0.82$, physical crest factor $\ge 14.0\text{ dB}$, and unsuppressed ballistic confidence to achieve confirmation under `single_round_impulse` without requiring a second sustained window.

