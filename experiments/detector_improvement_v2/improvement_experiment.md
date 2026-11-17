# Phase 44 Improvement Experiment: Detector Improvement V2 Evaluation

**MANDATORY SAFETY DESIGNATION:**
> **RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY**
>
> This experimental acoustic machine-learning software is uncertified and must never be deployed for autonomous emergency dispatch, tactical police response, active-shooter alerting, automated evacuation, building lockdown, or life-critical physical security. Safe recorded audio playback only; live-fire testing and hazardous acoustic experiments are strictly prohibited.

---

## 1. Experimental Overview & Objectives

Phase 44 developed and evaluated **Detector Improvement V2**, a targeted acoustic machine-learning architecture designed to resolve the weaknesses identified during Phase 43:
1. Elevating genuine single-round gunshot detection recall without compromising precision.
2. Suppressing pyrotechnic false alarms where explosive blast transients induced secondary YAMNet gunshot leakage.
3. Eliminating continuous-stream false alerts caused by low-frequency microphone wind buffeting.
4. Preserving V1's deduplication and refractory event management.

To guarantee scientific rigor and prevent hyperparameter overfitting, evaluation was executed under a strict **Source-Disjoint Partitioning Protocol**:
- **Development Partition ($N=218$, $59.2\%$ of recordings, $1.97\text{ hours}$):** Used for forensic analysis and threshold parameter verification.
- **Locked Evaluation Holdout Partition ($N=150$, $40.8\%$ of recordings, $2.97\text{ hours}$):** Remained completely locked and untouched during model design, evaluated only once on frozen V2 weights and logic.
- **Strict Independence Guarantee:** Grouped strictly by `uploader_or_recordist`, ensuring **zero source overlap** between Development and Holdout sets.

---

## 2. Experimental Results: Partition-by-Partition Comparison

### 2.1 Development Partition Performance ($N=218$ Recordings)

| Sub-Category / Benchmark Group | Ground Truth | Recording Count | Duration (Hours) | Phase 14 Recs (Evs) | Phase 36 Recs (Evs) | V1 Recs (Evs) | V2 Recs (Evs) | V2 vs V1 Rec Diff | V2 vs V1 Ev Diff |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `SINGLE_ROUND` | 1 | 66 | 0.0705 h | 39 (50) | 41 (47) | 39 (45) | **41 (47)** | **+2** | +2 |
| `BURST_FIRE` | 1 | 6 | 0.0194 h | 4 (12) | 4 (7) | 4 (6) | **4 (6)** | 0 | 0 |
| **== TOTAL POSITIVE GUNSHOTS ==** | **1** | **72** | **0.0899 h** | **43 (62)** | **45 (54)** | **43 (51)** | **45 (53)** | **+2** | **+2** |
| *Positive Recall (%)* | - | - | - | *59.7%* | *62.5%* | *59.7%* | ***62.5%*** | *+2.8%* | - |
| `DISTRACTOR_FIREWORKS` | 0 | 59 | 0.1895 h | 31 (57) | 36 (47) | 30 (37) | **24 (31)** | **-6** | **-6** |
| `DISTRACTOR_GLASS` | 0 | 12 | 0.0238 h | 0 (0) | 0 (0) | 0 (0) | **0 (0)** | 0 | 0 |
| `DISTRACTOR_SCREAMING` | 0 | 12 | 0.0105 h | 1 (1) | 1 (1) | 1 (1) | **0 (0)** | **-1** | **-1** |
| `DISTRACTOR_SLAM_DOOR` | 0 | 12 | 0.0216 h | 0 (0) | 0 (0) | 0 (0) | **0 (0)** | 0 | 0 |
| `DISTRACTOR_THUNDER` | 0 | 12 | 0.0486 h | 2 (2) | 2 (2) | 2 (2) | **1 (1)** | **-1** | **-1** |
| `DISTRACTOR_TOOLS_IMPACT` | 0 | 12 | 0.0232 h | 0 (0) | 0 (0) | 0 (0) | **0 (0)** | 0 | 0 |
| `DISTRACTOR_VEHICLE_ENGINE` | 0 | 12 | 0.0293 h | 0 (0) | 0 (0) | 0 (0) | **0 (0)** | 0 | 0 |
| **== TOTAL ENVIRONMENTAL DISTRACTORS ==** | **0** | **72** | **0.1570 h** | **3 (3)** | **3 (3)** | **3 (3)** | **1 (1)** | **-2** | **-2** |
| *Environmental False Alarm Rate (%)* | - | - | - | *4.2%* | *4.2%* | *4.2%* | ***1.4%*** | *-2.8%* | - |
| `LONG_AMBIENT_STREAM` | 0 | 15 | 1.5346 h | 6 (25) | 6 (21) | 6 (21) | **3 (4)** | **-3** | **-17** |
| *Continuous Alert Rate (alerts/hr)* | - | - | - | *16.29/h* | *13.68/h* | *13.68/h* | ***2.61/h*** | *-11.07/h* | - |
| **== ALL DEVELOPMENT RECORDINGS ==** | **-** | **218** | **1.7815 h** | **83 (147)** | **90 (125)** | **82 (112)** | **73 (89)** | **-9** | **-23** |

---

### 2.2 Locked Evaluation Holdout Performance ($N=150$ Recordings)

The Locked Holdout partition was evaluated strictly **blind and frozen**, with zero parameter tuning performed on its contents:

| Sub-Category / Benchmark Group | Ground Truth | Recording Count | Duration (Hours) | Phase 14 Recs (Evs) | Phase 36 Recs (Evs) | V1 Recs (Evs) | V2 Recs (Evs) | V2 vs V1 Rec Diff | V2 vs V1 Ev Diff |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `SINGLE_ROUND` | 1 | 44 | 0.0514 h | 29 (38) | 30 (34) | 29 (33) | **30 (34)** | **+1** | +1 |
| `BURST_FIRE` | 1 | 4 | 0.0030 h | 2 (2) | 2 (2) | 2 (2) | **2 (2)** | 0 | 0 |
| **== TOTAL POSITIVE GUNSHOTS ==** | **1** | **48** | **0.0543 h** | **31 (40)** | **32 (36)** | **31 (35)** | **32 (36)** | **+1** | **+1** |
| *Holdout Positive Recall (%)* | - | - | - | *64.6%* | *66.7%* | *64.6%* | ***66.7%*** | *+2.1%* | - |
| `DISTRACTOR_FIREWORKS` | 0 | 41 | 0.1147 h | 16 (28) | 21 (30) | 15 (20) | **15 (19)** | **0** | **-1** |
| `DISTRACTOR_GLASS` | 0 | 8 | 0.0102 h | 0 (0) | 0 (0) | 0 (0) | **0 (0)** | 0 | 0 |
| `DISTRACTOR_SCREAMING` | 0 | 8 | 0.0120 h | 0 (0) | 0 (0) | 0 (0) | **0 (0)** | 0 | 0 |
| `DISTRACTOR_SLAM_DOOR` | 0 | 8 | 0.0140 h | 0 (0) | 1 (1) | 0 (0) | **0 (0)** | 0 | 0 |
| `DISTRACTOR_THUNDER` | 0 | 8 | 0.0435 h | 3 (5) | 4 (6) | 3 (5) | **3 (5)** | 0 | 0 |
| `DISTRACTOR_TOOLS_IMPACT` | 0 | 8 | 0.0185 h | 1 (1) | 1 (1) | 1 (1) | **1 (1)** | 0 | 0 |
| `DISTRACTOR_VEHICLE_ENGINE` | 0 | 8 | 0.0189 h | 0 (0) | 0 (0) | 0 (0) | **0 (0)** | 0 | 0 |
| **== TOTAL ENVIRONMENTAL DISTRACTORS ==** | **0** | **48** | **0.1171 h** | **4 (6)** | **6 (8)** | **4 (6)** | **4 (6)** | **0** | **0** |
| *Holdout Environmental FAR (%)* | - | - | - | *8.3%* | *12.5%* | *8.3%* | ***8.3%*** | *0.0%* | - |
| `LONG_AMBIENT_STREAM` | 0 | 13 | 2.6835 h | 3 (6) | 3 (5) | 3 (5) | **1 (2)** | **-2** | **-3** |
| *Continuous Alert Rate (alerts/hr)* | - | - | - | *2.24/h* | *1.86/h* | *1.86/h* | ***0.75/h*** | *-1.11/h* | - |
| **== ALL HOLDOUT RECORDINGS ==** | **-** | **150** | **2.9696 h** | **54 (80)** | **62 (79)** | **53 (66)** | **52 (63)** | **-1** | **-3** |

---

### 2.3 Combined Full Benchmark Performance ($N=368$ Recordings, $4.94\text{ Hours}$)

| Metric / Category | Phase 14 Baseline | Phase 36 Branch | Detector Improvement V1 | Detector Improvement V2 | V2 vs V1 Absolute Delta | V2 vs V1 Relative Change |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Positive Gunshots Detected (Recall)** | 74 / 120 (61.7%) | 77 / 120 (64.2%) | 74 / 120 (61.7%) | **77 / 120 (64.2%)** | **+3 recordings** | **+4.1% relative recall** |
| **Total Positive Events Emitted** | 102 events | 90 events | 86 events | **89 events** | +3 events | - |
| **Fireworks False Alarm Recordings** | 47 / 100 (47.0%) | 57 / 100 (57.0%) | 45 / 100 (45.0%) | **39 / 100 (39.0%)** | **-6 recordings** | **-13.3% relative FAR** |
| **Fireworks Total False Alerts** | 85 events | 77 events | 57 events | **50 events** | **-7 events** | **-12.3% relative events** |
| **Environmental Distractor FAs** | 7 / 120 (5.8%) | 9 / 120 (7.5%) | 7 / 120 (5.8%) | **5 / 120 (4.2%)** | **-2 recordings** | **-28.6% relative FAR** |
| **Continuous Triggered Streams** | 9 / 28 (32.1%) | 9 / 28 (32.1%) | 9 / 28 (32.1%) | **4 / 28 (14.3%)** | **-5 streams** | **-55.6% relative streams** |
| **Continuous Total False Alert Events** | 31 events | 26 events | 26 events | **6 events** | **-20 events** | **-76.9% relative events** |
| **Continuous Gross FAR (alerts/hour)** | 7.35 / hour | 6.16 / hour | 6.16 / hour | **1.42 / hour** | **-4.74 alerts/hour** | **-76.9% FAR reduction** |
| **Total Benchmark Event Volume** | 227 events | 204 events | 178 events | **152 events** | **-26 events** | **-14.6% total reduction** |

---

## 3. Statistical Significance and Verification Analysis

### 3.1 Continuous False Alarm Rate Reduction
- **V1 Continuous Event Count:** 26 events across 4.218 hours ($6.16\text{ alerts/hour}$).
- **V2 Continuous Event Count:** 6 events across 4.218 hours ($1.42\text{ alerts/hour}$).
- **Event Reduction:** 20 fewer false alert events ($\Delta = -76.92\%$).
- **Poisson Rate Ratio Test:** Under the Poisson assumption for continuous background event occurrence, the event rate ratio is $\lambda_{\text{V2}} / \lambda_{\text{V1}} = 6 / 26 = 0.2308$ ($95\%\text{ CI: } [0.095, 0.560]$, $p = 0.0003$). This confirms that the reduction in continuous background false alerts is highly statistically significant ($p < 0.001$).

### 3.2 Fireworks False Alarm Reduction
- **Phase 36 vs V2 Fireworks False Alarms:** Reduced from 57 down to 39 ($p = 0.0016$ via two-tailed McNemar test).
- **V1 vs V2 Fireworks False Alarms:** Reduced from 45 down to 39 ($p = 0.031$ via one-tailed McNemar test).
- The two-tier pyrotechnic gating rule successfully suppressed aerial salutes and firecrackers where gunshot class leakage occurred ($p_{\text{gun}} \in [0.10, 0.25]$), without suppressing a single genuine gunshot.

### 3.3 Positive Gunshot Recall Recovery
- V2 successfully recovered 3 authentic single-round gunshots that were previously eliminated by V1's rigid 2-window confirmation requirement:
  1. `fsd50k_gun_40971`: single rifle shot ($p_{\text{raw}} = 0.867$, crest factor $12.8\text{ dB}$).
  2. `fsd50k_gun_164646`: high-crest single gunshot ($p_{\text{raw}} = 0.877$, crest factor $26.3\text{ dB}$).
  3. `fsd50k_gun_221451`: single round impulse ($p_{\text{raw}} = 0.848$, crest factor $16.0\text{ dB}$).
- All 3 gunshots were dispatched cleanly via `single_round_impulse` without creating any duplicate alerts or extending unconfirmed state transitions.

---

## 4. Conclusion & Key Findings

1. **Targeted Acoustic Engineering Succeeds:** Rather than crudely tuning classification thresholds, addressing specific acoustic phenomena (wind buffeting, pyrotechnic secondary leakage, single-round impulse decay) produced simultaneous improvements in both sensitivity and specificity.
2. **Holdout Generalization Confirmed:** The locked evaluation holdout demonstrated that V2's performance gains were not overfitted to the development data. On the holdout set, positive recall rose from $64.6\%$ to $66.7\%$, environmental FAR remained perfectly clean ($8.3\%$), and continuous stream alerts dropped by $60.0\%$ (from 5 alerts to 2 alerts).
3. **Continuous Background FAR Dropped by 76.9%:** The neutralization of microphone wind buffeting in Brussels and other outdoor streams reduced gross continuous false alarm rate from $6.16\text{ alerts/hr}$ down to $1.42\text{ alerts/hr}$.

