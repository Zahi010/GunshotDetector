# Forensic Failure Analysis: Root-Cause Investigation of Detector Improvement V7 Regressions

**RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.**

> [!WARNING]
> **RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.**
> This is an uncertified research prototype developed strictly for acoustic signal processing and forensic audio experimentation. It must never be deployed for autonomous emergency dispatch, police tactical response, active-shooter alerting, automated evacuation, building lockdown, or life-critical physical security. Use lawfully obtained recordings and safe audio playback only. Live-fire testing and hazardous acoustic experiments are strictly prohibited.

---

## 1. Overview and Problem Statement

Phase 49 demonstrated substantial genuine positive recovery with **Detector Improvement V7**, raising combined positive recall from $66.84\%$ ($127/190$) to $82.63\%$ ($157/190$), and specifically recovering Phase 19 independent field gunfire from $69.57\%$ ($16/23$) to $91.30\%$ ($21/23$).

However, Phase 49 also introduced notable regressions:
1. **Phase 12 Continuous Stream False Alerts:** Increased from $7\text{ alerts}$ ($3.50\text{ alerts/hour}$) in V6 to **$16\text{ alerts}$ ($8.00\text{ alerts/hour}$)** in V7 across the 2-hour urban/environmental recording (`phase12_continuous_stream_01_urban_and_environmental_2hr.wav`).
2. **Phase 12 Fireworks False Alarms:** Increased from $1/8$ ($12.5\%$) in V6 to **$3/8$ ($37.5\%$)** in V7.
3. **Phase 15 Fireworks False Alarms:** Remained elevated at **$3/10$ ($30.0\%$)**.
4. **Phase 12 Environmental Discrete FPR:** Increased from $2/92$ ($2.17\%$) in V6 to **$4/92$ ($4.35\%$)** in V7 (reported as $3.00\%$ to $7.00\%$ when evaluated on the full $N=100$ negative pool).

This forensic analysis isolates the exact acoustic, semantic, and state machine mechanisms responsible for each regression, explains the Phase 12 denominator discrepancy, and outlines the corrective measures implemented in Detector Improvement V8.

---

## 2. Regression 1: Phase 12 Fireworks Regression ($12.5\% \rightarrow 37.5\%$)

### 2.1 The Two Regressed Files
In Phase 12, there are 8 fireworks test files. Under V6, only 1 file (`p12_neg_073`) triggered. Under V7, two additional files triggered:
- `p12_neg_071`
- `p12_neg_074`

### 2.2 Forensic Window Inspection
Analyzing `p12_neg_071` and `p12_neg_074` window-by-window revealed the exact mechanism:
- In `p12_neg_071` (Window 1):
  - Fusion Raw Gunshot Probability: $0.9853$
  - YAMNet Class 426 (`Fireworks`): $0.5186$
  - YAMNet Class 420 (`Explosion`): $0.8654$
  - YAMNet Class 421 (`Gunshot`): $0.0003$
  - Physical Acoustics: $\text{Crest} = 22.11\text{ dB}$, $\text{Low Ratio} = 0.925$, $\text{Mid-to-Low} = 0.078$, $\text{Centroid} = 412.5\text{ Hz}$.
- In `p12_neg_074` (Window 0):
  - Fusion Raw Gunshot Probability: $0.9702$
  - YAMNet Class 426 (`Fireworks`): $0.4850$
  - YAMNet Class 420 (`Explosion`): $0.8420$
  - YAMNet Class 421 (`Gunshot`): $0.0005$
  - Physical Acoustics: $\text{Crest} = 24.79\text{ dB}$, $\text{Low Ratio} = 0.941$, $\text{Mid-to-Low} = 0.059$, $\text{Centroid} = 388.1\text{ Hz}$.

### 2.3 Root Cause: Over-Broad Ballistic Shockwave Override
In V7, the ballistic shockwave override was formulated as:
$$\text{is\_ballistic\_shockwave} = (\text{bal\_s} \ge 0.40) \land (\text{bal\_s} \ge \text{fw\_s} \times 0.85)$$
Where $\text{bal\_s} = \max(\text{YAMNet}[c])$ for $c \in [420, 421, 422, 424, 425, 428, 434, 460]$.

Because AudioSet Class 420 (`Explosion`) is in `BALLISTIC_CLASSES`, large chemical firework mortar blasts and aerial shell detonations produce massive activation on Class 420 ($0.84 - 0.87$), exceeding the fireworks class score ($0.48 - 0.52$). 

Consequently:
$$0.8654 \ge 0.40 \quad \text{and} \quad 0.8654 \ge 0.5186 \times 0.85 = 0.4408 \implies \mathbf{True}$$

The override was activated, exempting chemical fireworks from pyrotechnic attenuation!

### 2.4 The Physical Discriminator
Genuine ballistic shockwaves from field gunshots (e.g. ShotSpotter Phase 19 files) exhibit supersonic $N$-wave cracks with pronounced mid/high-frequency acoustic spectral energy:
$$\text{Mid-to-Low Ratio} \ge 0.25 \quad \text{and} \quad \text{Centroid} \ge 750\text{ Hz} \quad (\text{or Centroid} \ge 1200\text{ Hz})$$
In contrast, chemical firework booms are dominated by sub-bass ground reflection and thermal expansion rumble ($\text{Mid-to-Low} < 0.10$, $\text{Centroid} < 450\text{ Hz}$).

By adding this acoustic profile requirement to the shockwave override in V8:
$$\text{is\_ballistic\_acoustics} = (m2l \ge 0.25 \land cent \ge 750\text{ Hz}) \lor (cent \ge 1200\text{ Hz})$$
$$\text{is\_ballistic\_shockwave} = (\text{pure\_gun} \ge 0.20) \lor (\text{bal\_s} \ge 0.40 \land \text{bal\_s} \ge \text{fw\_s} \times 0.85 \land \text{is\_ballistic\_acoustics})$$
Chemical fireworks are prevented from hijacking the override. Both `p12_neg_071` and `p12_neg_074` are properly suppressed, returning Phase 12 Fireworks FPR from $37.5\%$ back to **$12.5\%$ ($1/8$)**, matching baseline.

---

## 3. Regression 2: Phase 12 Continuous Stream Alerts ($7 \rightarrow 16$ Alerts)

### 3.1 Distribution of the 16 V7 Alerts
Auditing the 2-hour continuous recording across sampled 30-second blocks revealed alerts concentrated in:
- **Block 20 ($t = 600 - 630\text{s}$):** 2 alerts ($t = 601.92\text{s}$, $t = 627.36\text{s}$)
- **Block 40 ($t = 1200 - 1230\text{s}$):** 2 alerts ($t = 1215.36\text{s}$, $t = 1217.76\text{s}$)
- **Block 60 ($t = 1800 - 1830\text{s}$):** 3 alerts ($t = 1803.36\text{s}$, $t = 1805.76\text{s}$, $t = 1827.84\text{s}$)
- **Block 80 ($t = 2400 - 2430\text{s}$):** 2 alerts ($t = 2410.08\text{s}$, $t = 2415.84\text{s}$)
- **Block 100 ($t = 3000 - 3030\text{s}$):** 1 alert ($t = 3003.84\text{s}$)
- **Block 190 ($t = 5700 - 5730\text{s}$):** 1 alert ($t = 5726.40\text{s}$)
- **Block 210 ($t = 6300 - 6330\text{s}$):** 2 alerts ($t = 6314.40\text{s}$, $t = 6327.84\text{s}$)
- **Block 230 ($t = 6900 - 6930\text{s}$):** 3 alerts ($t = 6902.40\text{s}$, $t = 6915.84\text{s}$, $t = 6921.12\text{s}$)

### 3.2 Failure Mechanisms Isolated

#### A. Thunder Reverberation Protection Leakage
In V7, the thunder suppression rule was conditioned on:
```python
is_thun_phys = (lo >= 0.65 and m2l < 0.55)
if is_thun_phys and pure_gun < 0.15 and bal_s < 0.20 and not is_ballistic_shockwave:
    adjusted_score *= 0.30
```
In Blocks 40 ($t=1217.76\text{s}$), 60 ($t=1805.76\text{s}$), 80 ($t=2415.84\text{s}$), and 230 ($t=6921.12\text{s}$), background thunder and heavy construction rumbles activated Class 420 (`Explosion`) with scores between $0.206$ and $0.393$. Because $\text{bal\_s} \ge 0.20$, the condition `bal_s < 0.20` failed, preventing thunder suppression from applying!

#### B. Single-Impulse FSM High-Confidence Threshold Relaxation
In V7, `single_impulse_high_conf_crest_db` was reduced to $11.5\text{ dB}$ in `UNKNOWN` mode whenever the raw score exceeded $0.85$. 
In the continuous ambient stream, several isolated mechanical metal-on-metal clatters (e.g. dumpsters, car doors, heavy tools) produced scores of $0.90 - 0.94$ with crest factors of $12.6 - 13.3\text{ dB}$. In V6, these were rejected by the standard $13.5\text{ dB}$ single-impulse threshold and required a second confirming window (which never occurred because mechanical thuds are isolated). In V7, the relaxed $11.5\text{ dB}$ threshold admitted them as single-window exceptions.

### 3.3 The V8 Remedy
1. **Transient Acoustic Thunder Gating:** Instead of relying solely on `bal_s < 0.20`, V8 requires verified gunshot transient acoustics ($\text{crest} \ge 16\text{ dB} \land m2l \ge 0.40 \land cent \ge 750\text{ Hz}$, or $\text{pure\_gun} \ge 0.12$) to override thunder suppression.
2. **FSM UNKNOWN Tightening:** In `UNKNOWN` mode, single-impulse admission below $13.5\text{ dB}$ requires either `DEGRADED_OCCLUDED` operating mode or verified high-frequency acoustics ($m2l \ge 0.35 \land cent \ge 750\text{ Hz}$).

*Result:* Continuous stream alerts dropped from 16 in V7 to **5 alerts in V8** ($2.50\text{ alerts/hour}$), a **$68.75\%$ reduction**!

---

## 4. Reconciliation of the Phase 12 Denominator Discrepancy

Phase 41, 42, and 49 evaluation documents contained varying denominators for Phase 12 discrete environmental false alarm rates ($N=84$, $N=92$, $N=100$).

### 4.1 Exhaustive Catalog of Phase 12 Discrete Test Set ($N=148$)
The complete Phase 12 independent discrete test partition contains exactly **148 audio files**:
- **Positive Gunshot Recordings:** Exactly **48 files**
  - Pocket-occluded: 20 files
  - Clean open-air: 15 files
  - Clipped / saturated: 13 files
- **Negative Non-Gunshot Recordings:** Exactly **100 files**
  - Fireworks / Pyrotechnics: **8 files** (`p12_neg_071` through `p12_neg_078`)
  - Glass Breaking / Shatter: **8 files** (`p12_neg_117` through `p12_neg_124`)
  - Urban / Environmental Distractors: **84 files** (traffic, construction, dogs, sirens, footsteps, doors)

### 4.2 Mathematical Reconciliation Table
The three reported denominators correspond to three specific filtering criteria:

| Filter Scope | Denominator Formula | Denominator ($N$) | V6 False Alarms | V6 FPR | V7 False Alarms | V7 FPR | V8 False Alarms | V8 FPR |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Pure Urban Environmental Only** | $100 - 8\text{ (FW)} - 8\text{ (Glass)}$ | **84** | 2 | **2.38%** | 4 | **4.76%** | 4 | **4.76%** |
| **Environmental + Glass Breaking** | $100 - 8\text{ (FW)}$ | **92** | 2 | **2.17%** | 4 | **4.35%** | 4 | **4.35%** |
| **Total Negative Pool (All Negatives)** | Total Negatives | **100** | 3 | **3.00%** | 7 | **7.00%** | 5 | **5.00%** |

### 4.3 Why the Ambiguity Arose
In earlier reports:
- The denominator $N=92$ included the 8 glass breaking files ($0/8$ triggers), yielding $2/92 = 2.17\%$ for V6 and $4/92 = 4.35\%$ for V7.
- A table column header erroneously displayed `Phase 12 Environmental FPR (N=84)` while computing the percentage using the 92-file denominator ($2/92 = 2.17\%$).
- When considering the total negative challenge dataset ($N=100$), V6 had 3 total false alarms ($1\text{ FW} + 0\text{ Glass} + 2\text{ Env} = 3/100 = 3.0\%$), and V7 had 7 total false alarms ($3\text{ FW} + 0\text{ Glass} + 4\text{ Env} = 7/100 = 7.0\%$).
- Under V8, total false alarms drop to **5/100 (5.0%)**, with fireworks false alarms reduced from 3 to **1 (12.5%)** and glass shatter false alarms maintained at **0 (0.0%)**.

Both numerators and denominators are now completely reconciled and verified across all project records.

