# Forensic Acoustic Failure Analysis: Baseline & Historical Experimental Detectors

> [!WARNING]
> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY**  
> This software is an uncertified acoustic research prototype. Never deploy it for autonomous emergency dispatch, tactical police response, active-shooter alerting, automated evacuation, building lockdown, or life-critical physical security. Use legally obtained recordings and safe audio playback only. Live-fire testing and hazardous acoustic experiments are strictly prohibited.

---

## 1. Executive Summary & Audit Context

Prior to Phase 42, extensive forensic auditing documented persistent performance trade-offs across historical detector implementations:
- **Phase 14 Balanced Baseline** (`model_phase14.py`): Established solid semantic suppression but suffered from **28 duplicate alerts** (27.45% duplicate rate) during true positive gunshot bursts and high continuous background false alarm rates (7.35 alerts/hour).
- **Phase 36 Experimental V1** (`experiments/phase36`): Solved event boundaries with a deterministic 4-state refractory state machine (halving duplicate alerts to 13), but **regressed significantly on fireworks distractors**, surging from 47 false alarms to **57 false alarms** (+21.3% error surge) because pyrotechnic and thunderstorm semantic suppression was removed.

This investigation analyzes the acoustic, temporal, and machine-learning mechanisms responsible for these failure modes across 368 benchmark recordings (120 positive gunshots, 100 fireworks, 120 environmental distractors, and 28 continuous ambient streams totaling 4.22 hours).

---

## 2. Failure Mode 1: Pyrotechnic Acoustic Leakage & Semantic Suppression Regression

### Acoustic Mechanism
Fireworks, firecrackers, and aerial salutes exhibit acoustic properties remarkably similar to gunfire:
- High peak sound pressure levels (>130 dB SPL).
- Instantaneous acoustic rise time ($t_{\text{rise}} < 5\text{ ms}$).
- Elevated physical crest factor ($12.0 - 28.0\text{ dB}$).
- Broad initial spectral excitation across the 500 Hz – 8 kHz band.

Because YAMNet 1024-dimensional bottleneck embeddings capture generic energy envelopes and spectral distributions, gunshot classifier heads (CatBoost, LightGBM, XGBoost, and MLP) frequently assign raw scores $p \ge 0.80$ to commercial firecrackers and aerial shell bursts.

### Comparative Failure Evidence
In Phase 36, pyrotechnic and thunderstorm semantic suppression was stripped down in favor of conservative animal-only gating (`AcousticSuppressionEngine` in `experiments/phase36/acoustic_features.py`). This led directly to severe pyrotechnic leakage:

| Detector Architecture | Fireworks False Triggers ($N=100$) | Fireworks FAR (%) | Other Distractor Triggers ($N=120$) | Total Distractor Triggers ($N=220$) | Total Distractor FAR (%) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Phase 14 Balanced Baseline** | 47 / 100 | 47.00% | 7 / 120 | 54 / 220 | 24.55% |
| **Phase 36 Experimental V1** | 57 / 100 | 57.00% | 9 / 120 | 66 / 220 | 30.00% |
| **Detector Improvement V1** | **45 / 100** | **45.00%** | **7 / 120** | **52 / 220** | **23.64%** |

### Root Cause Analysis
In Phase 36, when fireworks bursts occurred with raw ensemble scores between 0.75 and 0.88, the absence of fireworks class attenuation (`YAMNET_CLASS_FIREWORKS=426`, `YAMNET_CLASS_FIRECRACKER=427`) allowed consecutive 960 ms windows to achieve multi-window confirmation. 

In contrast, **Detector Improvement V1** introduces a calibrated semantic suppression engine with ballistic protection:
$$\text{Suppression Condition: } p_{\text{fw}} > 0.30 \land p_{\text{fw}} \ge 1.5 \cdot p_{\text{gun}} \land p_{\text{gun}} < 0.10$$
When satisfied, the ensemble score is attenuated by $0.35\times$, dropping spurious pyrotechnic scores well below the base threshold of $0.75$. This eliminates 12 false alarms relative to Phase 36 (a **21.21% relative error reduction**).

---

## 3. Failure Mode 2: Multi-Alert Fragmentation & Echo Re-triggering (Duplicate Alerts)

### Acoustic Mechanism
Real-world gunfire generates severe multi-path acoustic reflections:
- Direct line-of-sight muzzle blast impulse ($0 - 50\text{ ms}$).
- Supersonic shockwave / Mach cone (for supersonic rounds).
- Ground, wall, and architectural reverberation decay tails ($200 - 1500\text{ ms}$).
- Multi-round bursts (burst fire or rapid semi-automatic fire within 150–500 ms).

### Failure Analysis in Phase 14
Phase 14 used an implicit state heuristic (`in_event = True`, `cooldown_until = t + 2.0`). When an acoustic burst occurred:
1. Window 1 and Window 2 met confirmation criteria ($p \ge 0.75$), triggering `in_event = True`.
2. As reverberation decayed, intermediate window score dropped momentarily below `threshold_off = 0.48`.
3. Phase 14 emitted an event record, reset `active_cluster = []`, and marked `in_event = False`.
4. However, if a secondary gunshot round or loud flutter echo arrived 600 ms later (prior to `cooldown_until`), the cooldown logic in Phase 14 did not maintain an explicit `COOLDOWN` state machine: in streaming chunk processing and certain batch edge cases, fresh windows restarted candidate accumulation, emitting a second duplicate alert for the same firing incident.

### Comparative Duplicate Alert Performance ($N=120$ Positive Clips)

| Detector Architecture | Positive Detected | Total Events Emitted | TP Duplicate Alerts | Duplicate Alert Rate (%) |
| :--- | :---: | :---: | :---: | :---: |
| **Phase 14 Balanced Baseline** | 74 / 120 | 102 events | 28 duplicate alerts | 27.45% |
| **Phase 36 Experimental V1** | 77 / 120 | 90 events | 13 duplicate alerts | 14.44% |
| **Detector Improvement V1 (Balanced)** | 74 / 120 | 86 events | **12 duplicate alerts** | **13.95%** |
| **Detector Improvement V1 (High Precision)** | 66 / 120 | 76 events | **10 duplicate alerts** | **13.16%** |

Detector Improvement V1 incorporates Phase 36's deterministic 4-state refractory state machine (`IDLE`, `CANDIDATE`, `CONFIRMED`, `COOLDOWN`), locking the detector into a hard 2.0-second refractory state upon event termination. This reduces duplicate alerts from 28 down to 12—a **57.14% reduction in redundant alarms**.

---

## 4. Failure Mode 3: Clustered Ambient False Alarms in Continuous Streams

### Forensic Audio Stream Audit
Across the 28 continuous ambient recordings (4.2182 hours / 15,185.60 seconds), continuous false alarms were highly concentrated in a single urban environment:

| Stream ID | Location / Acoustic Setting | Duration | Phase 14 Alerts | Phase 36 Alerts | V1 Alerts | Dominant Noise Source |
| :--- | :--- | :---: | :---: | :---: | :---: | :--- |
| `p40_cont_03_bruxelles` | Parc Léopold, Brussels, Belgium | 884.2 s | 15 alerts | 12 alerts | 12 alerts | Playground iron gate clatter, metal maintenance carts |
| `p40_cont_11_fukutsu_japan` | Coastal park, Fukutsu, Japan | 868.5 s | 5 alerts | 4 alerts | 4 alerts | Transient mic wind pops, shore mechanical thuds |
| `p38_cont_01_goussainville` | Abandoned village, France | 900.0 s | 3 alerts | 2 alerts | 2 alerts | Loose corrugated metal sheet banging in wind |
| `p40_cont_05_hamburg` | Urban street, Hamburg, Germany | 871.3 s | 2 alerts | 2 alerts | 2 alerts | Heavy truck suspension slam, dumpster impact |
| `p39_cont_09_poznan` | City park, Poznan, Poland | 895.0 s | 2 alerts | 2 alerts | 2 alerts | Skateboard grinding on concrete bench |
| *Other 23 Streams* | Various natural & quiet suburban | ~10,766 s | 4 alerts | 2 alerts | 2 alerts | Isolated mechanical transients |
| **Total Exposure** | **28 Streams (4.22 Hours)** | **15,185.6 s** | **31 alerts (7.35/hr)** | **26 alerts (6.16/hr)** | **26 alerts (6.16/hr)** | **16.19% FAR reduction vs P14** |

### Analysis of `p40_cont_03_bruxelles`
In `p40_cont_03_bruxelles`, a heavy iron gate repeatedly slams shut against an unpadded metal latch. Each slam generates:
- Physical crest factor exceeding 14.5 dB.
- Resonant metallic ringing in the 1–3 kHz region.
- Insufficient spectral disparity for YAMNet to classify as standard transit or canine noise.
Because the clanging occurs in bursts every 10–30 seconds, both Phase 36 and V1 emit alerts when two consecutive windows align with double impacts. However, under `Detector Improvement V1 (High Precision)`, the required threshold rises to 0.80 and minimum crest factor to 9.5 dB, cutting continuous ambient alerts from 26 down to 15 (3.56 alerts/hour, a **51.56% FAR reduction vs Phase 14**).

---

## 5. Failure Mode 4: False Negatives on Transient Single-Round Gunshots

### Acoustic Mechanism
Single-round gunshot recordings (e.g. hunting rifle or bolt-action rifle in open terrain) produce an extremely abrupt impulse ($< 50\text{ ms}$). Because YAMNet computes spectrogram frames over 960 ms windows advanced by 480 ms hops:
- Window 1 captures the blast near its peak, scoring $p \ge 0.82$.
- Window 2 (480 ms later) contains only the dissipated acoustic tail, where the raw ensemble score frequently drops to $0.45 - 0.65$.

### State Machine Behavior
Under rigid multi-window confirmation (`confirm_windows = 2`), Window 1 transitions the FSM from `IDLE` to `CANDIDATE`. When Window 2 scores below `threshold_base = 0.75`, the candidate buffer is not confirmed. At file termination (EOF), if `allow_short_clip_exception` is disabled or requires isolated clips ($\le 1.05\text{ s}$), candidate windows are discarded.

### Empirical Validation
In our grid search across candidate confirmation rules:
- Requiring Window 1 score $p \ge 0.88$ with crest factor $\ge 12.0\text{ dB}$ safely enables immediate single-window promotion without escalating false alarms.
- Setting $p \ge 0.88$ maintains positive recall at 74/120 while holding total distractor false alarms at 52/220.
- Lowering the immediate threshold to $p \ge 0.84$ raised positive recall to 79/120, but increased total distractor false alarms from 52 to 75 (+23 false alarms), representing an unacceptable false positive trade-off for urban monitoring.

---

## 6. Summary Comparison Matrix

| Failure Mode Dimension | Phase 14 Balanced Baseline | Phase 36 Experimental V1 | Detector Improvement V1 (Balanced) |
| :--- | :--- | :--- | :--- |
| **Pyrotechnic Leakage** | 47 / 100 false alarms (47.0%) | 57 / 100 false alarms (57.0%) *(+10 surge)* | **45 / 100 false alarms (45.0%)** *(-12 vs P36)* |
| **Total Challenge Distractors** | 54 / 220 false alarms (24.55%) | 66 / 220 false alarms (30.00%) *(+12 surge)* | **52 / 220 false alarms (23.64%)** *(-14 vs P36)* |
| **Positive Recall ($N=120$)** | 74 / 120 (61.67%) | 77 / 120 (64.17%) | 74 / 120 (61.67%) |
| **Duplicate Alerts on TP** | 28 duplicates (27.45%) | 13 duplicates (14.44%) | **12 duplicates (13.95%)** *(-57.1% vs P14)* |
| **Continuous FAR (4.22 hr)** | 31 alerts (7.35 / hour) | 26 alerts (6.16 / hour) | **26 alerts (6.16 / hour)** *(-16.2% vs P14)* |
| **Continuous FAR (Precision)** | N/A | N/A | **15 alerts (3.56 / hour)** *(-51.6% vs P14)* |

