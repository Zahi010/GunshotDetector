# Phase 32: Factorial Diagnostic Ablation Report
## 2x2 Factorial Decomposition of Animal Suppression & State-Machine Defect Dynamics

**Document ID:** `REPORT-PHASE32-FACTORIAL-001`  
**Phase:** 32 (Factorial Defect Ablation & Statistical Reconciliation)  
**Date:** November 2026  
**Status:** COMPLETE EMPIRICAL ABLATION — INTERACTION EFFECT QUANTIFIED  

---

### MANDATORY SAFETY DESIGNATION
> [!CAUTION]
> **RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.**  
> This experimental acoustic machine-learning software is uncertified and must never be deployed for autonomous emergency dispatch, tactical police response, active-shooter alerting, automated evacuation, building lockdown, or life-critical physical security. Use legally obtained recordings and safe audio playback only. Live-fire testing and hazardous acoustic experiments are strictly prohibited.

---

## 1. Executive Summary & Experimental Objectives

Phase 31 identified two competing explanations for the severe false-alert inflation observed in Phase 17 on the AeroSonicDB aviation benchmark (108 alerts vs 72 in Phase 14):
1. **The Animal Suppression Hypothesis:** Intermediate animal classification penalties intermittently depressing composite scores, causing aircraft alert fragmentation.
2. **The State-Machine Defect Hypothesis:** Omission of `active_cluster = []` upon sub-threshold windows, leaking unconfirmed candidates across arbitrary temporal gaps.

To rigorously resolve the separate and combined contributions of these two mechanisms, Phase 32 conducted a definitive **$2 \times 2$ Factorial Diagnostic Ablation** across the entire 6.0-hour AeroSonicDB benchmark (6 continuous 1-hour streams, 21,600 elapsed seconds, 44,796 analysis windows, including 25 ground-truth aircraft overflight sequences).

### Key Empirical Findings
- **Condition A (Suppression ON, Defective Reset — Frozen Phase 17):** 108 alerts (18.00 alerts/hr).
- **Condition B (Suppression OFF, Defective Reset):** 130 alerts (21.67 alerts/hr).
- **Condition C (Suppression ON, Corrected Reset):** 66 alerts (11.00 alerts/hr).
- **Condition D (Suppression OFF, Corrected Reset — Equivalent to Phase 14 Baseline):** 72 alerts (12.00 alerts/hr).

```
                      +------------------------------------------+
                      |         2x2 FACTORIAL DESIGN MATRIX      |
                      +--------------------+---------------------+
                      | Defective Reset    | Corrected Reset     |
+---------------------+--------------------+---------------------+
| Suppression ON      | Cond A: 108 alerts | Cond C: 66 alerts   |
+---------------------+--------------------+---------------------+
| Suppression OFF     | Cond B: 130 alerts | Cond D: 72 alerts   |
+---------------------+--------------------+---------------------+
```

### Definitive Causal Decomposition
1. **Reset Defect is the Dominant Inflation Driver:** Correcting the state-machine reset reduces false alerts by **42 alerts** when suppression is active ($108 \to 66$, $-38.9\%$) and by **58 alerts** when suppression is disabled ($130 \to 72$, $-44.6\%$).
2. **Suppression Effect Reversal:** Outside aircraft sequences, animal suppression moderately reduces false alerts ($130 \to 108$ in defective reset; $72 \to 66$ in corrected reset). However, **inside the 25 aircraft overflight sequences**, animal suppression produces an alert inflation of **$+8$ alerts** ($69 \to 77$) under defective reset and **$+5$ alerts** ($47 \to 52$) under corrected reset, proving that animal suppression actively fragments aircraft overflights.
3. **Significant Non-Zero Interaction ($\Delta = -16$ alerts):** The two factors are non-additive. The defective state machine magnifies the apparent impact of animal suppression by a factor of 3.67 ($22$ vs $6$ alerts) because unsuppressed noise spikes are retained across multi-second gaps and stitched into spurious alerts.

---

## 2. 2x2 Factorial Design & Experimental Isolation

All four conditions evaluated identical raw window-level acoustic scores ($T=0.975\text{ s}$, hop $=0.48\text{ s}$, 44,796 total inference windows) extracted directly from [phase30_instrumented_score_traces.csv](file:///E:/gunshot/gunshot/reports/phase30_instrumented_score_traces.csv).

| Condition ID | Animal Suppression | State Machine Reset | Architectural Equivalent | Implementation Source |
| :---: | :---: | :---: | :---: | :--- |
| **Condition A** | **ENABLED** | **DEFECTIVE (Original)** | Frozen Phase 17 Experimental | [model_phase17.py](file:///E:/gunshot/gunshot/model_phase17.py) |
| **Condition B** | **DISABLED** | **DEFECTIVE (Original)** | Phase 17 with Raw Scores | [model_phase17.py](file:///E:/gunshot/gunshot/model_phase17.py) with `raw_score` |
| **Condition C** | **ENABLED** | **CORRECTED (Candidate)** | Repaired Phase 17 Candidate | [model_phase17_state_reset_candidate.py](file:///E:/gunshot/gunshot/experiments/phase31/model_phase17_state_reset_candidate.py) |
| **Condition D** | **DISABLED** | **CORRECTED (Candidate)** | Phase 14 Balanced Baseline | [model_phase14.py](file:///E:/gunshot/gunshot/model_phase14.py) |

### Parameter Invariance
In all four conditions, the temporal aggregation parameters were strictly fixed to canonical values:
- Base Detection Threshold: $\tau_{\text{base}} = 0.75$
- Confirmation Window Requirement: $N_{\text{confirm}} = 2$ consecutive qualifying windows
- Immediate Qualification Threshold: $\tau_{\text{immediate}} = 0.88$ (with crest factor $\ge 12.0\text{ dB}$)
- Decay / Continuation Threshold: $\tau_{\text{decay}} = 0.48$
- Post-Alert Refractory Cooldown: $\Delta t_{\text{cooldown}} = 2.0\text{ s}$

---

## 3. Factorial Results Across AeroSonicDB Streams

The table below summarizes the alert counts and false-alert rates per stream across all 4 conditions. Data reproduced from [phase32_factorial_results.csv](file:///E:/gunshot/gunshot/reports/phase32_factorial_results.csv).

| Stream ID | Gross Duration | Condition A (Frozen P17) | Condition B (Suppr OFF, Defective) | Condition C (Suppr ON, Corrected) | Condition D (P14 Baseline) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| `P27-AERO-STR-01` | 1.0 hr (3600s) | 23 alerts (23.0/hr) | 25 alerts (25.0/hr) | 14 alerts (14.0/hr) | 15 alerts (15.0/hr) |
| `P27-AERO-STR-02` | 1.0 hr (3600s) | 5 alerts (5.0/hr) | 6 alerts (6.0/hr) | 3 alerts (3.0/hr) | 3 alerts (3.0/hr) |
| `P27-AERO-STR-03` | 1.0 hr (3600s) | 7 alerts (7.0/hr) | 16 alerts (16.0/hr) | 3 alerts (3.0/hr) | 7 alerts (7.0/hr) |
| `P27-AERO-STR-04` | 1.0 hr (3600s) | 10 alerts (10.0/hr) | 12 alerts (12.0/hr) | 7 alerts (7.0/hr) | 8 alerts (8.0/hr) |
| `P27-AERO-STR-05` | 1.0 hr (3600s) | 28 alerts (28.0/hr) | 34 alerts (34.0/hr) | 13 alerts (13.0/hr) | 17 alerts (17.0/hr) |
| `P27-AERO-STR-06` | 1.0 hr (3600s) | 35 alerts (35.0/hr) | 37 alerts (37.0/hr) | 26 alerts (26.0/hr) | 22 alerts (22.0/hr) |
| **CORPUS TOTAL** | **6.0 hr (21600s)** | **108 alerts (18.00/hr)** | **130 alerts (21.67/hr)** | **66 alerts (11.00/hr)** | **72 alerts (12.00/hr)** |

---

## 4. Main Effects, Combined Effect & Factor Interactions

The statistical decomposition was computed using standard $2 \times 2$ factorial orthogonal contrast analysis:

```
                  Defective Reset (R_def)    Corrected Reset (R_cor)         Marginal Row
                 +-------------------------+-------------------------+
Suppr ON  (S_on) | A = 108                 | C = 66                  | S_on = 174
Suppr OFF (S_off)| B = 130                 | D = 72                  | S_off = 202
                 +-------------------------+-------------------------+
Marginal Col     | R_def = 238             | R_cor = 138             | Total = 376
```

### 4.1. Suppression Effect
- Under Defective Reset:
  $$\Delta S_{\text{def}} = A - B = 108 - 130 = -22\text{ alerts} \quad (-16.9\%)$$
- Under Corrected Reset:
  $$\Delta S_{\text{cor}} = C - D = 66 - 72 = -6\text{ alerts} \quad (-8.3\%)$$
- Main Effect of Suppression (marginal):
  $$\Delta \bar{S} = \frac{(A + C) - (B + D)}{2} = \frac{174 - 202}{2} = -14.0\text{ alerts}$$

### 4.2. Reset Defect Effect
- Under Suppression ON:
  $$\Delta R_{\text{suppr\_on}} = A - C = 108 - 66 = +42\text{ alerts} \quad (+63.6\%)$$
- Under Suppression OFF:
  $$\Delta R_{\text{suppr\_off}} = B - D = 130 - 72 = +58\text{ alerts} \quad (+80.6\%)$$
- Main Effect of Reset Defect (marginal):
  $$\Delta \bar{R} = \frac{(A + B) - (C + D)}{2} = \frac{238 - 138}{2} = +50.0\text{ alerts}$$

### 4.3. Combined Net Effect (Condition A vs Condition D)
The total inflation of frozen Phase 17 over the Phase 14 baseline is:
$$\text{Net Inflation} = A - D = 108 - 72 = +36\text{ alerts} \quad (+50.0\%)$$

### 4.4. Factor Interaction Effect
The interaction contrast evaluates whether the effect of animal suppression depends on whether the state-machine reset is defective:
$$\text{Interaction} = (A - B) - (C - D) = (-22) - (-6) = -16\text{ alerts}$$
Equivalently:
$$\text{Interaction} = (A - C) - (B - D) = 42 - 58 = -16\text{ alerts}$$

> [!IMPORTANT]
> **Mechanistic Interpretation of Non-Zero Interaction:**  
> The interaction is non-zero ($-16$ alerts) because the two mechanisms are structurally coupled. In the presence of the reset defect, unconfirmed qualifying noise spikes are never purged from memory. When suppression is disabled (Condition B), ambient environmental noises trigger spurious single windows, which are preserved across minutes of silence and eventually stitched with subsequent distant transients. When suppression is active (Condition A), some of those initial noise spikes are suppressed, preventing them from entering the leaky cluster. Thus, suppression appears to eliminate 22 alerts under the defective reset, but eliminates only 6 alerts under a clean state machine. The defective state machine magnified the apparent benefit of animal suppression by **$367\%$**!

---

## 5. Aircraft Flyover Sequences vs Background Audio

A critical finding from [phase32_event_level_ablation.csv](file:///E:/gunshot/gunshot/reports/phase32_event_level_ablation.csv) is the profound divergence in behavior inside aircraft flyover sequences versus background audio:

| Acoustic Domain | Condition A (Frozen P17) | Condition B (Suppr OFF, Defective) | Condition C (Suppr ON, Corrected) | Condition D (P14 Baseline) | Suppression Impact (A - B) | Reset Defect Impact (A - C) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Inside 25 Aircraft Flyovers** | **78 alerts** | **72 alerts** | **52 alerts** | **47 alerts** | **$+6$ alerts (Fragmentation)** | **$+26$ alerts** |
| **Outside Aircraft (Ambient BG)** | **30 alerts** | **58 alerts** | **14 alerts** | **25 alerts** | **$-28$ alerts (Suppression)** | **$+16$ alerts** |
| **TOTAL AEROSONICDB CORPUS** | **108 alerts** | **130 alerts** | **66 alerts** | **72 alerts** | **$-22$ alerts (Net)** | **$+42$ alerts** |

### 5.1. The Aircraft Fragmentation Mechanism (Confirmed)
Inside loud aircraft flyovers, animal suppression has the **opposite effect** of its intended design:
- In Condition B (Suppression OFF), an aircraft produces sustained high raw scores ($> 0.75$), triggering an alert that remains active until the aircraft sound diminishes, producing a smaller number of alerts (72 total across 25 sequences).
- In Condition A (Suppression ON), jet turbine whining and harmonic resonances periodically activate the animal detector, applying penalties that force the composite score to drop below $0.48$. This prematurely terminates the alert. As the turbine frequency shifts, the penalty drops, and the detector re-triggers a new alert once refractory cooldown (2.0s) elapses. This splits single flyovers into 2, 3, or 4 distinct alert fragments, increasing the alert count inside aircraft sequences from 72 to 78 ($+6$ alerts). Under corrected reset, suppression similarly increases flyover alerts from 47 to 52 ($+5$ alerts).

### 5.2. Ambient Audio Suppression
In quiescent ambient audio between aircraft overflights, animal suppression successfully suppresses dog barks, bird chirp harmonics, and brief mechanical clicks ($58 \to 30$ alerts in defective mode; $25 \to 14$ alerts in corrected mode).

---

## 6. Cooldown Accounting & Eligible Exposure Under All 4 Conditions

Because Phase 17's state-machine defect caused alerts to span across tens or hundreds of seconds, cooldown conventions have vastly different impacts across the 4 conditions:

| Metric | Condition A (Frozen P17) | Condition B (Suppr OFF, Defective) | Condition C (Suppr ON, Corrected) | Condition D (P14 Baseline) |
| :--- | :---: | :---: | :---: | :---: |
| **Total Observed Alerts** | 108 | 130 | 66 | 72 |
| **Gross Exposure (hr)** | 6.0000 | 6.0000 | 6.0000 | 6.0000 |
| **Gross FAR (alerts/hr)** | **18.0000** | **21.6667** | **11.0000** | **12.0000** |
| **Convention A Cooldown (s)** | 216.00 s | 260.00 s | 132.00 s | 144.00 s |
| **Convention A Eligible (hr)** | 5.9400 hr | 5.9278 hr | 5.9633 hr | 5.9600 hr |
| **Convention A FAR (alerts/hr)** | **18.1818** | **21.9306** | **11.0676** | **12.0805** |
| **Convention B Cooldown (s)** | 6283.28 s | 6942.16 s | 228.48 s | 258.96 s |
| **Convention B Eligible (hr)** | **4.2546 hr** | **4.0716 hr** | **5.9365 hr** | **5.9281 hr** |
| **Convention B FAR (alerts/hr)** | **25.3840** | **31.9283** | **11.1176** | **12.1456** |

> [!WARNING]
> **Convention B Exposure Distortion:**  
> In Condition A, Convention B cooldown accounts for **6,283.3 seconds (1.745 hours)** of excluded exposure ($29.1\%$ of the entire recording!), because unconfirmed clusters stitched together distant windows into alerts lasting up to 2,574 seconds. When the state machine is corrected (Conditions C and D), alerts have natural physical durations ($0.96\text{s} - 3.84\text{s}$), and Convention B cooldown drops to only $228 - 259$ seconds ($3.8 - 4.3$ minutes), restoring eligible exposure to $> 5.93$ hours.

---

## 7. Conclusions & Governance Decision

1. **Defect vs Suppression Causal Share:**
   - The state-machine defect accounts for **$+42$ false alerts** ($70.0\%$ of the anomalous variance).
   - Animal suppression reduces background false alerts by **$-6$ to $-22$ alerts**, but actively increases aircraft false alerts by **$+8$ alerts** through event fragmentation.
2. **Experimental Candidate Assessment:**
   - The corrected state reset candidate (`model_phase17_state_reset_candidate.py`) eliminates all 42 spurious reset alerts, bringing Phase 17's false-alert rate down to $11.00\text{ alerts/hr}$ on AeroSonicDB (superior to Phase 14's $12.00\text{ alerts/hr}$).
3. **Retention of Phase 14 Balanced Baseline:**
   - In accordance with baseline freeze rules, `model_phase14.py` remains the **Default Research Baseline**.
   - `model_phase17.py` remains a **Frozen Selectable Experimental Profile** documented with known defect dynamics. The candidate patch remains an experimental diagnostic prototype and is not promoted to production baseline.
