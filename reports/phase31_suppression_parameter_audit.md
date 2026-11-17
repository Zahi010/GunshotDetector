# Phase 31: Animal Suppression Parameter Audit Report
## Disambiguation of Thresholds, Multipliers, Semantic Gates & Hysteresis Dynamics

**Document ID:** `REPORT-PHASE31-SUPPRESSION-001`  
**Phase:** 31 (Animal Suppression Parameter & Causal Audit)  
**Date:** November 2026  
**Status:** COMPLETE TECHNICAL AUDIT  

---

### MANDATORY SAFETY DESIGNATION
> [!CAUTION]
> **RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.**  
> This experimental acoustic machine-learning software is uncertified and must never be deployed for autonomous emergency dispatch, tactical police response, active-shooter alerting, automated evacuation, building lockdown, or life-critical physical security. Use legally obtained recordings and safe audio playback only. Live-fire testing and hazardous acoustic experiments are strictly prohibited.

---

## 1. Executive Summary & Parameter Disambiguation

Phase 30 documentation utilized several overlapping numerical descriptors when discussing Phase 17's experimental animal vocalization suppression mechanism:
- "Animal activation threshold: 0.35"
- "Table notation: 0.35 / 2.0x"
- "Applied score multiplier: 0.30x"
- "Shared detector off-threshold: 0.48"

Phase 31 conducted a rigorous audit of `model_phase17.py` to establish the exact definition, mathematical role, and state-machine interactions of each parameter.

### Core Disambiguation Finding
- **`0.35` (`animal_thresh`):** The absolute semantic confidence threshold required for the YAMNet animal classifier to be considered active.
- **`2.0x` (`animal_ratio`):** The relative dominance multiplier. The animal score must be at least twice the gunshot score ($animal\_score \ge 2.0 \times gun\_score$) to prevent suppressing genuine gunfire in the presence of low-level ambient bird noise. **It is NOT an applied penalty.**
- **`0.30x` (`suppression_penalty`):** The actual mathematical multiplier applied to the detection score when suppression triggers ($calibrated\_score \leftarrow calibrated\_score \times 0.30$). It attenuates the score by 70%.
- **`0.48` (`threshold_off`):** The hysteresis cutoff threshold. In an ongoing alert ($in\_event = True$), if the score drops below 0.48, the alert immediately terminates and enters refractory cooldown.

---

## 2. Nine-Point Architectural Specification

### 2.1. Animal Classifier Score Definition
Evaluates 12 specific YAMNet classes corresponding to animal, canine, avian, and livestock vocalizations:
- Class 67: Animal
- Class 68: Domestic animals, pets
- Class 76: Cat
- Class 80: Caterwaul
- Class 81: Livestock, farm animals, working animals
- Class 85: Cattle, bovinae
- Class 93: Fowl
- Class 94: Chicken, rooster
- Class 96: Crowing, cock-a-doodle-doo
- Class 103: Wild animals
- Class 106: Bird
- Class 110: Bird vocalization, bird call, bird song
- Class 111: Chirp, tweet
- Class 114: Crow

The scalar animal score is defined as:
$$\text{animal\_score} = \max_{c \in \text{ANIMAL\_CLASSES}} YAMNet\_Score_i(c) \in [0.0, 1.0]$$

### 2.2. Activation Threshold
The absolute activation condition requires:
$$\text{animal\_score} > 0.35$$
If $\text{animal\_score} \le 0.35$, the gate remains dormant regardless of other scores.

### 2.3. Window Scope & Temporal Memory
The animal suppression check is strictly **instantaneous and per-window** ($0.975\text{ s}$ window length, $0.480\text{ s}$ hop). It has no internal multi-window memory or sliding accumulator. It evaluates each window independently.

### 2.4. Suppression Penalty Multiplier
When activated, the penalty applied is:
$$\text{calibrated\_score} \leftarrow \text{calibrated\_score} \times 0.30$$
This is a fixed 70% attenuation factor hardcoded in `model_phase17.py` line 472.

### 2.5. Score Application Target
The penalty is applied directly to `calibrated_score`, which is initialized as the raw ensemble model prediction `raw_score` ($\in [0.0, 1.0]$). It directly alters the score evaluated by the downstream state machine.

### 2.6. Suppression Persistence and Release Conditions
The gate is stateless across windows. If the next window has $\text{animal\_score} < 0.35$ or $gun\_score \times 2.0 > animal\_score$, suppression is instantly released on that window.

### 2.7. Interaction with Hysteresis (`threshold_off = 0.48`)
This is the primary mechanism of aircraft alert fragmentation.
During a loud aircraft flyover, jet engine harmonics frequently produce false activations in YAMNet animal/bird classes (e.g., turbine whine scoring $0.40$ in Bird Song).
1. An ongoing alert is active ($in\_event = True$) with raw jet noise scoring $0.85$.
2. In window $k$, turbine whine triggers animal suppression:
   $$\text{calibrated\_score} = 0.85 \times 0.30 = 0.255$$
3. Because $0.255 < 0.48$ (`threshold_off`), the state machine considers the acoustic event over!
4. The alert terminates, and refractory cooldown is initiated ($cooldown\_until = et + 2.0\text{ s}$).

### 2.8. Interaction with Confirmation Windows (`confirm_windows = 2`)
If suppression triggers on window 2 of a candidate cluster, $score$ drops from $\sim 0.80$ to $0.24 < 0.75$ (`threshold_base`), preventing 2-window confirmation.

### 2.9. State Reset Between Recordings
Because the animal suppression gate is a memoryless per-window transformation inside the window loop of `evaluate_waveform`, it holds zero state between recordings. State leakage occurs solely inside the downstream clustering state machine (`active_cluster`).

---

## 3. Systematic Summary Table

| Parameter Name | Frozen Code Variable | Value | Purpose / Function |
| :--- | :--- | :---: | :--- |
| **Animal Threshold** | `self.animal_thresh` | `0.35` | Minimum absolute YAMNet animal class probability required to trigger gate |
| **Animal Ratio** | `self.animal_ratio` | `2.0x` | Ballistic safeguard; animal score must be $\ge 2.0 \times$ gunshot score |
| **Suppression Penalty**| Hardcoded scalar | `0.30x` | Multiplicative penalty reducing calibrated score by 70% |
| **Off-Threshold** | `self.threshold_off` | `0.48` | Hysteresis lower bound; dropping below terminates active alerts |
| **Base Threshold** | `self.threshold_base` | `0.75` | Minimum score to start or continue candidate cluster |
| **High Threshold** | `self.threshold_high` | `0.88` | Immediate qualification threshold when crest factor $\ge 12.0\text{ dB}$ |
| **Cooldown Duration**| `self.cooldown_secs` | `2.0 s` | Mandatory refractory window following alert termination |

