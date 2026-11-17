# Phase 33: State-Machine Test Report Integrity Audit
## Forensic Reconciliation of Vector Failure Counts, Batch vs Streaming Paths & Boundary Guarantees

**Document ID:** `REPORT-PHASE33-STATEMACHINE-001`  
**Phase:** 33 (Independent Forensic Audit)  
**Date:** November 2026  
**Status:** RECONCILIATION COMPLETE — TRUE FAILURE COUNT CONFIRMED (8/12 FAILURES)  

---

### MANDATORY SAFETY DESIGNATION
> [!CAUTION]
> **RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.**  
> This experimental acoustic machine-learning software is uncertified and must never be deployed for autonomous emergency dispatch, tactical police response, active-shooter alerting, automated evacuation, building lockdown, or life-critical physical security. Use legally obtained recordings and safe audio playback only. Live-fire testing and hazardous acoustic experiments are strictly prohibited.

---

## 1. Executive Summary & Clerical Reconciliation

Phase 32's executive summary and final report stated:
> *"Phase 17 Frozen: Failed 6 / 12 (50%) (VEC-01, VEC-02, VEC-03, VEC-04, VEC-07, VEC-09, VEC-10, VEC-12) due to cluster leakage across silence gaps and unguarded EOF flushes."*

The text explicitly enumerated **8 distinct vector IDs**, while reporting a count of **6 failures**.

### Definitive Forensic Finding
Phase 33 audited the underlying execution records, test scripts, and output logs:
1. **The True Failure Count for Phase 17 is 8 Out of 12 (66.7% Failure Rate):**  
   All 8 enumerated vectors (`VEC-01`, `VEC-02`, `VEC-03`, `VEC-04`, `VEC-07`, `VEC-09`, `VEC-10`, `VEC-12`) genuinely **failed** on the frozen `model_phase17.py` implementation. Phase 17 passed only 4 vectors (`VEC-05`, `VEC-06`, `VEC-08`, `VEC-11`).
2. **Root Cause of the Discrepancy:**  
   The phrase "Failed 6 / 12 (50%)" was a **clerical markdown prose error**. The author appears to have inadvertently inverted $12 - 6 = 6$ (perhaps confusing the 6 passing vectors of an earlier 8-vector draft with failures) while correctly listing all 8 failed vector IDs from the underlying CSV table.
3. **No Duplicate or Skipped Vectors:**  
   All 12 vectors were executed independently without skipping, duplication, or multi-counting.

---

## 2. 12-Vector Test Results & Implementation Comparison

Reconciled from [phase33_state_machine_test_reconciliation.csv](file:///E:/gunshot/gunshot/reports/phase33_state_machine_test_reconciliation.csv):

| Vector ID | Scenario Name | Expected Alerts | Phase 14 Baseline | Phase 17 Frozen | Candidate Patch | Phase 17 Defect Mechanism |
| :---: | :--- | :---: | :---: | :---: | :---: | :--- |
| **VEC-01** | Isolated Unconfirmed Spike | **0** | 0 (PASS) | **1 (FAIL)** | 0 (PASS) | Unguarded EOF flush asserts 1-window cluster |
| **VEC-02** | Unrelated Spikes (3s Gap) | **0** | 0 (PASS) | **1 (FAIL)** | 0 (PASS) | Omission of reset stitches spikes across 3s gap |
| **VEC-03** | Unrelated Spikes (100s Gap) | **0** | 0 (PASS) | **1 (FAIL)** | 0 (PASS) | Indefinite retention of unconfirmed cluster across 100s gap |
| **VEC-04** | Three Unrelated Spikes Across Gaps | **0** | 0 (PASS) | **2 (FAIL)** | 0 (PASS) | Accumulation of unconfirmed spikes into multiple spurious alerts |
| **VEC-05** | Consecutive Qualifying Windows | **1** | 1 (PASS) | 1 (PASS) | 1 (PASS) | Legitimate 2-window confirmation |
| **VEC-06** | Genuine Immediate Qualification | **1** | 1 (PASS) | 1 (PASS) | 1 (PASS) | Immediate high-confidence qualification ($\ge 0.88$, crest $\ge 12\text{ dB}$) |
| **VEC-07** | Recording-Boundary State Isolation | **0** | 0 (PASS) | **2 (FAIL)** | 0 (PASS) | Unguarded EOF flush emits spurious alert in both files |
| **VEC-08** | Empty Window Sequence | **0** | 0 (PASS) | 0 (PASS) | 0 (PASS) | Graceful handling of zero input windows |
| **VEC-09** | Irregular Timestamp Intervals | **0** | 0 (PASS) | **1 (FAIL)** | 0 (PASS) | Cluster retention across timestamp discontinuity |
| **VEC-10** | End-of-Stream Trailing Flush Guard | **0** | 0 (PASS) | **1 (FAIL)** | 0 (PASS) | Unguarded flush flushes partial cluster at EOF |
| **VEC-11** | Previously Confirmed Active Event | **1** | 1 (PASS) | 1 (PASS) | 1 (PASS) | Valid multi-window gunshot duration |
| **VEC-12** | Confirmed Event Followed by Spike | **1** | 1 (PASS) | **2 (FAIL)** | 1 (PASS) | P17 detects Event 1, but flushes trailing spike as Event 2 |
| **TOTALS** | **12 Standardized Vectors** | — | **12/12 PASS (100%)** | **4/12 PASS (33.3%)** | **12/12 PASS (100%)** | **8 FAILURES IN PHASE 17 CONFIRMED** |

---

## 3. Batch vs Streaming Execution Paths

Phase 33 audited both processing paths independently:

### 3.1. Batch Path (`merge_phase14_events` vs `merge_phase17_events`)
- In `model_phase14.py` (lines 121–133):
  When $score < \tau_{\text{base}}$ and not $in\_event$, `active_cluster` is explicitly reset to `[]`.
- In `model_phase17.py` (lines 145–155):
  The `else: active_cluster = []` branch is omitted, causing `active_cluster` to accumulate across arbitrary time intervals.
- In `model_phase17.py` (line 180):
  The EOF flush evaluates `if active_cluster:` instead of `if in_event and active_cluster:`.

### 3.2. Streaming Path (`RealTimeStreamDetectorPhase17.process_chunk`)
- Evaluated in `test_streaming_chunk_state_leakage`:
  Chunk 1 contains an isolated unconfirmed qualifying spike ($s = 0.78$); Chunk 2 contains another isolated spike after 5 seconds of silence.
- `RealTimeStreamDetectorPhase14`: Purges candidate state upon silence; emits 0 alerts (**PASS**).
- `RealTimeStreamDetectorPhase17`: Leaks candidate state across chunk boundaries; stitches the two chunks into a spurious alert (**FAIL**).
- `CandidateStreamDetector`: Restores clean chunk boundaries; emits 0 alerts (**PASS**).

Execution logs from the automated pytest suite are preserved in [phase33_test_execution_log.txt](file:///E:/gunshot/gunshot/reports/phase33_test_execution_log.txt).

---

## 4. General Reliability Limitation

> [!WARNING]
> **Unit Test Bounds:**  
> Passing 12 / 12 synthetic regression vectors demonstrates that `model_phase14.py` and the candidate patch adhere to intended state-machine transitions on idealized inputs. **It does not establish operational reliability, environmental robustness, or life-safety readiness.** Real-world acoustic soundscapes contain non-stationary reverberations, moving vehicular noise floors, and atmospheric effects that cannot be evaluated with synthetic test vectors.

