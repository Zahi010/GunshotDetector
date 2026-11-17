# Phase 33: Factorial Ablation Reproduction Report
## Independent Verification of 4-Condition Ablation, Aircraft Fragmentation & Schema Divergence

**Document ID:** `REPORT-PHASE33-FACTORIAL-001`  
**Phase:** 33 (Independent Forensic Audit)  
**Date:** November 2026  
**Status:** FULLY REPRODUCED — FACTORIAL INTERACTION CONFIRMED — SCHEMA DIVERGENCE CLARIFIED  

---

### MANDATORY SAFETY DESIGNATION
> [!CAUTION]
> **RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.**  
> This experimental acoustic machine-learning software is uncertified and must never be deployed for autonomous emergency dispatch, tactical police response, active-shooter alerting, automated evacuation, building lockdown, or life-critical physical security. Use legally obtained recordings and safe audio playback only. Live-fire testing and hazardous acoustic experiments are strictly prohibited.

---

## 1. Executive Summary & Reproduction Status

Phase 33 conducted an independent reproduction of the Phase 32 $2 \times 2$ factorial diagnostic ablation across the 6.0-hour AeroSonicDB aviation benchmark (6 streams, 21,600 elapsed seconds, 44,796 analysis windows, 25 ground-truth aircraft overflight sequences).

### Reproduction Verdict: `REPRODUCED WITH CLARIFICATION`
- **Condition A (Suppression ON, Defective Reset):** Exactly **108 alerts** ($18.00\text{ alerts/hr}$) — **100% REPRODUCED**.
- **Condition B (Suppression OFF, Defective Reset):** Exactly **130 alerts** ($21.67\text{ alerts/hr}$) — **100% REPRODUCED**.
- **Condition C (Suppression ON, Corrected Reset):** Exactly **66 alerts** ($11.00\text{ alerts/hr}$) — **100% REPRODUCED**.
- **Condition D (Suppression OFF, Corrected Reset):** Exactly **72 alerts** ($12.00\text{ alerts/hr}$) — **100% REPRODUCED**.

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

### Critical Architectural Clarification: Condition D vs Phase 14 Baseline
Phase 32 described Condition D as "equivalent to Phase 14 Baseline." Phase 33 conducted a line-by-line event and schema comparison:
1. **Timing & Event Count Equivalence:** Condition D produces exactly 72 events across all 6 AeroSonicDB streams, with **100% identical event start times ($0.0\text{s}$ delta)** and **100% identical event end times ($0.0\text{s}$ delta)** compared to `model_phase14.py`.
2. **Schema & Record Representation Divergence:**  
   `model_phase14.py` generates event dictionaries using `_create_phase14_event_record` (`duration_seconds`, `peak_score` rounded to 3 decimals, `dispatch_path`, `verdict`). Condition D executes within `model_phase17_state_reset_candidate.py`, returning `_create_phase17_event_record` (`duration`, unrounded float `score`, `raw_ensemble_score`, `crest_factor_db`).
3. **Mandatory Labeling:** Per Phase 33 requirements, Condition D is formally classified as **`CORRECTED-CANDIDATE / SUPPRESSION-OFF`** to reflect that it is an ablated candidate profile, not a literal execution of the frozen Phase 14 baseline codebase.

---

## 2. Configuration & Input Score Trace Provenance

All four conditions evaluated identical raw acoustic windows from [phase30_instrumented_score_traces.csv](file:///E:/gunshot/gunshot/reports/phase30_instrumented_score_traces.csv) ($44,796$ rows, SHA-256: `34b3e6c0d0c3eb1df9f2f8121d5828469ad0593dd1ff5f22f778619bcbb7353f`).

| Factor / Component | Canonical Value / File | SHA-256 / Checksum | Audit Verification |
| :--- | :--- | :--- | :--- |
| **Input Score Traces** | `reports/phase30_instrumented_score_traces.csv` | `34b3e6c0...` | 44,796 windows verified identical across all conditions |
| **Frozen Phase 14 Model** | `model_phase14.py` | `a2685516...` | Unchanged baseline source |
| **Frozen Phase 17 Model** | `model_phase17.py` | `e2b262b8...` | Unchanged experimental source |
| **Candidate Patch Model** | `experiments/phase31/model_phase17_state_reset_candidate.py` | `c144b917...` | Verified state-reset patch |
| **Detection Threshold ($\tau_{\text{base}}$)** | `0.75` | Fixed parameter | Identical across A, B, C, D |
| **Immediate Threshold ($\tau_{\text{immediate}}$)** | `0.88` | Fixed parameter | Identical across A, B, C, D |
| **Decay Threshold ($\tau_{\text{decay}}$)** | `0.48` | Fixed parameter | Identical across A, B, C, D |
| **Confirm Windows ($N_{\text{confirm}}$)** | `2` consecutive windows | Fixed parameter | Identical across A, B, C, D |
| **Cooldown Duration ($\Delta t_{\text{cooldown}}$)**| `2.0` seconds | Fixed parameter | Identical across A, B, C, D |

Complete cryptographic hashes are recorded in [phase33_condition_config_hashes.json](file:///E:/gunshot/gunshot/reports/phase33_condition_config_hashes.json).

---

## 3. Reproduced Main Effects & Interaction Contrasts

Data preserved in [phase33_factorial_reproduction.csv](file:///E:/gunshot/gunshot/reports/phase33_factorial_reproduction.csv):

| Stream ID | Duration | Condition A (Frozen P17) | Condition B (No Suppr, Defective) | Condition C (Suppr ON, Corrected) | Condition D (CORRECTED-CANDIDATE / SUPPRESSION-OFF) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| `P27-AERO-STR-01` | 1.0 hr | 23 | 25 | 14 | 15 |
| `P27-AERO-STR-02` | 1.0 hr | 5 | 6 | 3 | 3 |
| `P27-AERO-STR-03` | 1.0 hr | 7 | 16 | 3 | 7 |
| `P27-AERO-STR-04` | 1.0 hr | 10 | 12 | 7 | 8 |
| `P27-AERO-STR-05` | 1.0 hr | 28 | 34 | 13 | 17 |
| `P27-AERO-STR-06` | 1.0 hr | 35 | 37 | 26 | 22 |
| **CORPUS TOTAL** | **6.0 hr** | **108 alerts (18.00/hr)** | **130 alerts (21.67/hr)** | **66 alerts (11.00/hr)** | **72 alerts (12.00/hr)** |

### Statistical Contrast Decomposition
1. **Suppression Effect (Defective Reset):**
   $$\Delta S_{\text{def}} = A - B = 108 - 130 = \mathbf{-22\text{ alerts}}$$
2. **Suppression Effect (Corrected Reset):**
   $$\Delta S_{\text{cor}} = C - D = 66 - 72 = \mathbf{-6\text{ alerts}}$$
3. **Reset Defect Effect (Suppression ON):**
   $$\Delta R_{\text{suppr\_on}} = A - C = 108 - 66 = \mathbf{+42\text{ alerts}}$$
4. **Reset Defect Effect (Suppression OFF):**
   $$\Delta R_{\text{suppr\_off}} = B - D = 130 - 72 = \mathbf{+58\text{ alerts}}$$
5. **Combined Net Inflation ($A - D$):**
   $$A - D = 108 - 72 = \mathbf{+36\text{ alerts}}$$
6. **Factorial Interaction Contrast:**
   $$\text{Interaction} = (A - B) - (C - D) = (-22) - (-6) = \mathbf{-16\text{ alerts}}$$

---

## 4. Reconstructed Aircraft Overflight Event Analysis

The 25 ground-truth aircraft overflights identified in AeroSonicDB were audited in [phase33_event_level_reconciliation.csv](file:///E:/gunshot/gunshot/reports/phase33_event_level_reconciliation.csv).

| Acoustic Partition | Condition A (Frozen P17) | Condition B (No Suppr, Defective) | Condition C (Candidate) | Condition D (Candidate No Suppr) | Suppression Delta ($A - B$) | Reset Defect Delta ($A - C$) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Inside 25 Flyovers** | **78 alerts** | **72 alerts** | **52 alerts** | **47 alerts** | **$+6$ alerts (Fragmentation)** | **$+26$ alerts** |
| **Outside Flyovers (Ambient)** | **30 alerts** | **58 alerts** | **14 alerts** | **25 alerts** | **$-28$ alerts (Suppression)** | **$+16$ alerts** |
| **Total AeroSonicDB Corpus** | **108 alerts** | **130 alerts** | **66 alerts** | **72 alerts** | **$-22$ alerts (Net)** | **$+42$ alerts** |

### Aircraft Alert Fragmentation Confirmed
Inside aircraft overflight sequences:
- Condition A generates **78 alerts** vs Condition B's **72 alerts** (an increase of $+6$ alerts).
- Condition C generates **52 alerts** vs Condition D's **47 alerts** (an increase of $+5$ alerts).
- During high-amplitude jet engine flyovers, acoustic harmonics periodically cross the animal classifier threshold. This applies a penalty that artificially forces the score below $\tau_{\text{decay}} = 0.48$, terminating the alert prematurely. Upon cooldown expiration, the ongoing engine noise re-triggers a new alert, producing multiple alert fragments per flyover.
- Ambient alerts outside aircraft sequences are reduced by animal suppression (from $58$ to $30$ alerts in defective mode; from $25$ to $14$ alerts in corrected mode). However, they cannot be categorically assumed to be false alarms without independent verification.

