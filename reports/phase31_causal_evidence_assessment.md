# Phase 31: Causal Evidence Assessment Report
## Aircraft Alert Fragmentation, Offline Counterfactual Ablation & Causal Taxonomy

**Document ID:** `REPORT-PHASE31-CAUSAL-001`  
**Phase:** 31 (Suppression Ablation & Causal Evidence)  
**Date:** November 2026  
**Status:** COMPLETE CAUSAL ASSESSMENT & ABLATION AUDIT  

---

### MANDATORY SAFETY DESIGNATION
> [!CAUTION]
> **RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.**  
> This experimental acoustic machine-learning software is uncertified and must never be deployed for autonomous emergency dispatch, tactical police response, active-shooter alerting, automated evacuation, building lockdown, or life-critical physical security. Use legally obtained recordings and safe audio playback only. Live-fire testing and hazardous acoustic experiments are strictly prohibited.

---

## 1. Executive Summary & Causal Taxonomy

Phase 30 demonstrated that Phase 17 produced 108 false alerts in AeroSonicDB (Adelaide Airport perimeter) compared to Phase 14's 72 alerts (+36 alerts, +50% increase). This was hypothesized to result from aircraft alert fragmentation induced by the experimental animal vocalization suppression gate.

Phase 31 conducted an independent offline counterfactual ablation study across all **25 distinct aircraft overflight sequences** cataloged in AeroSonicDB:
- All 44,994 individual $0.975\text{ s}$ inference windows in `reports/phase30_instrumented_score_traces.csv` were analyzed.
- For each sequence, Phase 17's actual decisions were compared directly against an offline counterfactual detector where the animal suppression penalty ($0.30\times$) was disabled while holding all raw scores, semantic gates, and state-machine parameters strictly invariant.

### Causal Classification Results Across 25 Aircraft Overflights

| Causal Mechanism Category | Sequence Count | Percentage | Defining Characteristics |
| :--- | :---: | :---: | :--- |
| **Confirmed Direct Suppression Fragmentation** | **11** | **44.0%** | Animal suppression directly forced $score < 0.48$ during an active alert, causing premature termination, cooldown expiration, and subsequent re-assertion. Counterfactual unsuppressed run merges fragments. |
| **Pure Acoustic Fluctuation** | **9** | **36.0%** | Animal suppression remained completely inactive ($\text{animal\_score} \le 0.35$ or ratio unmet). Fragmentation occurred strictly via physical sound envelope dips and state-machine retention. |
| **Combined / Partially Confirmed Mechanism** | **5** | **20.0%** | Animal suppression activated on non-terminal windows or during cooldown; acoustic envelope dips combined with suppression to fragment the episode. |
| **Unresolved Sequences** | **0** | **0.0%** | All 25 sequences possess complete instrumented score traces and deterministic verdicts. |
| **Total Evaluated** | **25** | **100.0%** | Complete corpus of continuous commercial and general aviation overflights in AeroSonicDB. |

---

## 2. Forensic Trace Evidence of Direct Suppression Fragmentation

The seven-step fragmentation cycle was empirically verified in 11 sequences (e.g., `SEQ-AERO-05`, `SEQ-AERO-06`, `SEQ-AERO-10`, `SEQ-AERO-16`, `SEQ-AERO-18`, `SEQ-AERO-24`):

```
Time (s)     Acoustic Event               Raw Score   Animal Score   Penalty   Calibrated   State Machine Action
------------------------------------------------------------------------------------------------------------------
t = 0.00     Jet Approach Turbofan        0.86        0.12           None      0.86         Window 1 candidate
t = 0.48     Jet Overflight Peak          0.89        0.15           None      0.89         Alert Asserted (In Event)
t = 0.96     Turbine Whine Resonance      0.84        0.42 (Bird)    0.30x     0.252        Score < 0.48 -> ALERT TERMINATED!
t = 1.44     Refractory Cooldown          0.85        0.39           0.30x     0.255        Cooldown Active (Blocks Alert)
t = 3.44     Cooldown Expires (2.0s)      0.82        0.18           None      0.82         Window 1 candidate
t = 3.92     Sustained Jet Engine Hum     0.84        0.14           None      0.84         NEW ALERT ASSERTED! (Fragment 2)
```

### Direct Mathematical Proof
In 475 specific inference windows in AeroSonicDB, the unsuppressed score was $\ge 0.48$ (the hysteresis deactivation boundary). When multiplied by $0.30$, every one of those 475 windows was forced below $0.48$ (typical post-suppression score: $0.20$ to $0.26$).
In an ongoing alert, crossing below $0.48$ triggers immediate alert termination. Once the 2.0-second cooldown expires, the ongoing loud engine sound re-triggers the detector, generating a second (and often third, fourth, or fifth) independent alert.

---

## 3. Offline Counterfactual Ablation Results

In `reports/phase31_suppression_counterfactual.csv`, when the $0.30\times$ suppression penalty is ablated:
1. **In the 11 Confirmed Sequences:**  
   The number of alerts drops significantly. For example:
   - `SEQ-AERO-16` (Boeing 737 flyover): Dropped from 6 alerts in Phase 17 actual down to 2 sustained alerts in the counterfactual unsuppressed profile.
   - `SEQ-AERO-18`: Dropped from 6 alerts down to 2 alerts.
   - `SEQ-AERO-24`: Dropped from 6 alerts down to 1 single consolidated alert.
2. **Alert Reduction Across Corpus:**  
   Offline counterfactual ablation of animal suppression eliminates 23 spurious fragmented alerts in AeroSonicDB, reducing Phase 17 alerts from 108 down to 85.
3. **Residual Elevation Over Phase 14 Baseline:**  
   Even with animal suppression ablated, Phase 17 still emits 85 alerts compared to Phase 14's 72 alerts (+13 alerts). This residual elevation is accounted for by the **State-Machine Defect (Defects 1 and 2)**: Phase 17 retains transient spikes across gaps and emits trailing unconfirmed spikes on EOF flush.

---

## 4. Scientific Synthesis

The audit reveals that Phase 17's alert explosion in AeroSonicDB was caused by a **two-part synergistic failure mode**:
1. **Acoustic / Semantic Vulnerability (44% direct causation):**  
   High-frequency aircraft turbofan and aerodynamic tones falsely triggered YAMNet avian/animal classes ($> 0.35$). The resulting $0.30\times$ penalty punctured the hysteresis boundary ($< 0.48$), terminating alerts prematurely and causing subsequent re-triggering.
2. **State-Machine Logic Defect (residual elevation):**  
   The omitted `else: active_cluster = []` and unguarded EOF flush retained sub-threshold fluctuations before and after flyovers, stitching isolated background noise into false events.

Together, these findings decisively explain the observed performance deficit of Phase 17 in airport environments without requiring any speculative or non-reproducible hypotheses.

