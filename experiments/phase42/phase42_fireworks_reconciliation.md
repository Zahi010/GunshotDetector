# PHASE 42 AUDIT REPORT: PHASE 17 FIREWORKS DECISION RECONCILIATION

> [!CAUTION]
> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.**
> This software is uncertified research code. It must never be deployed for autonomous emergency dispatch, police tactical response, active-shooter alerting, automated evacuation, building lockdown, or life-critical physical security.
> Use lawfully obtained recordings and safe audio playback only. Live-fire testing and hazardous acoustic experiments are strictly prohibited.

---

## 1. Executive Summary & Objective

Workstream B resolves the conflicting historical records regarding Phase 17 false alarms on the 100 curated fireworks challenge clips:
- **Phase 40 Pipeline Output:** Reported **62 / 100** fireworks triggers for COND2.
- **Phase 41 Master Table:** Reported **58 / 100** fireworks triggers for COND2 (and 47 for COND3).
- **Physical Ground Truth Execution:**
  - **`COND2` (`model_phase17.py`): 71 / 100 triggers (71.0%)**
  - **`COND3` (`model_phase17_state_reset_candidate.py`): 57 / 100 triggers (57.0%)**
  - **`COND1` (`model_phase14.py`): 47 / 100 triggers (47.0%)**
  - **`COND6` (`model_phase36.py`): 57 / 100 triggers (57.0%)**

This audit establishes the exact origin of every conflicting number and proves the causal mechanism behind the 71 vs. 57 trigger count.

---

## 2. Forensic Breakdown of Conflicting Values

| Reported Value | Phase & Context | Physical Reality & Root Cause Analysis | Forensic Status |
|---|---|---|---|
| **62 / 100** | Phase 40 Pipeline (`scripts/execute_phase40_continuous_pipeline.py`) | **Hardcoded Placeholder.** Lines 174–177 contained an unverified placeholder ternary expression: `fw_trig = 57 if cid in ["COND4", "COND5", "COND6"] else (47 if cid == "COND1" else 62)`. The author did not execute `model_phase17.py` on the fireworks set. | **INVALID (Unverified Script Placeholder)** |
| **58 / 100** | Phase 41 Section 2 Master Table | **Typographical Transcription Error.** The Phase 41 author manually transcribed 58 for COND2 and 47 for COND3, conflicting with Phase 41's own underlying artifact (`phase41_fireworks_reconstruction.csv`). | **INVALID (Typographical Transcription Error)** |
| **71 / 100** | Physical inference of `model_phase17.py` (authoritative config) | **Authentic Physical Ground Truth.** Executing `model_phase17.py` with frozen parameters (`threshold=0.75, max_candidates=10`) triggers on exactly 71 of 100 clips. Matches `experiments/phase39/phase39_distractor_results.csv` exactly. | **AUTHENTIC PHYSICAL GROUND TRUTH** |
| **57 / 100** | Physical inference of `model_phase17_state_reset_candidate.py` | **Authentic Physical Ground Truth for COND3.** Under the Phase 31 state-reset fix, candidate accumulation across non-target frames is purged upon decay, reducing triggers from 71 to 57. | **AUTHENTIC PHYSICAL GROUND TRUTH (COND3)** |

---

## 3. Causal Mechanism: Candidate-Accumulation Defect

The 14-clip discrepancy between Phase 17 Frozen Profile (71 triggers) and Phase 17 State Reset Candidate (57 triggers) is caused entirely by the **candidate-accumulation defect** documented in Phase 31:

1. **Defect Mechanism in `model_phase17.py`:**
   When a reverberant fireworks burst occurs, individual audio frames may intermittently exceed the detection threshold ($p \ge 0.75$). In `model_phase17.py`, candidate detections were appended to an internal list without decay or flushing when intermediate frames fell below threshold. Over multi-second files, reverberant frames gradually accumulated until the required candidate threshold was met, emitting a false alert.
2. **Resolution in `model_phase17_state_reset_candidate.py`:**
   In Phase 31, a state-reset modification was introduced that flushes the candidate buffer whenever the score drops below threshold. On the exact same 14 clips, this prevents the candidate accumulation, keeping the detector silent.
3. **List of 14 Defect-Triggered Clips:**
   The 14 clips triggering false alarms exclusively under `model_phase17.py` due to the candidate defect are:
   - `p39_dist_DISTRACTOR_FIREWORKS_129686` (8.88 s, max CNN score: 0.8775)
   - `p39_dist_DISTRACTOR_FIREWORKS_190698` (3.69 s, max CNN score: 0.7963)
   - `p39_dist_DISTRACTOR_FIREWORKS_96518` (2.57 s, max CNN score: 0.7936)
   - `p39_dist_DISTRACTOR_FIREWORKS_387704` (2.19 s, max CNN score: 0.7923)
   - `p39_dist_DISTRACTOR_FIREWORKS_142014` (12.33 s, max CNN score: 0.8203)
   - `p39_dist_DISTRACTOR_FIREWORKS_132043` (4.50 s, max CNN score: 0.8693)
   - `p39_dist_DISTRACTOR_FIREWORKS_27613` (5.44 s, max CNN score: 0.7689)
   - `p39_dist_DISTRACTOR_FIREWORKS_209944` (12.44 s, max CNN score: 0.8154)
   - `p39_dist_DISTRACTOR_FIREWORKS_388200` (3.00 s, max CNN score: 0.8721)
   - `p39_dist_DISTRACTOR_FIREWORKS_25778` (13.00 s, max CNN score: 0.7949)
   - `p39_dist_DISTRACTOR_FIREWORKS_376656` (17.29 s, max CNN score: 0.7819)
   - `p39_dist_DISTRACTOR_FIREWORKS_109742` (9.19 s, max CNN score: 0.8413)
   - `p39_dist_DISTRACTOR_FIREWORKS_46330` (2.88 s, max CNN score: 0.8733)
   - `p39_dist_DISTRACTOR_FIREWORKS_325664` (7.26 s, max CNN score: 0.8348)

---

## 4. Cross-Condition Fireworks Trigger Summary

| Condition ID | Architecture / Model Profile | Fireworks Triggers (/100) | Trigger Rate (%) | Primary Suppression Active | Refractory / State Machine Behavior |
|---|---|---|---|---|---|
| **COND1** | Phase 14 Balanced Baseline | 47 | 47.0% | Fast decay buffer reset | Strict 2-window contiguous confirmation |
| **COND2** | Phase 17 Experimental Profile | 71 | 71.0% | Animal suppression (Inactive on FW) | **Defective candidate accumulation (71 triggers)** |
| **COND3** | Phase 17 State Reset Candidate | 57 | 57.0% | Animal suppression (Inactive on FW) | State reset on sub-threshold decay (57 triggers) |
| **COND4** | Phase 36 Raw State Machine | 57 | 57.0% | None | Multi-window state persistence (57 triggers) |
| **COND5** | Phase 36 Legacy Suppression | 57 | 57.0% | Legacy animal suppression | Inactive on fireworks (57 triggers) |
| **COND6** | Phase 36 Conservative Suppression | 57 | 57.0% | Conservative animal suppression | Inactive on fireworks (57 triggers) |

---

## 5. Artifact Provenance
- Decision reconciliation table: [`phase42_fireworks_decision_reconciliation.csv`](file:///E:/gunshot/gunshot/experiments/phase42/phase42_fireworks_decision_reconciliation.csv)
