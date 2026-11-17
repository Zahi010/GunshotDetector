# Phase 31: State-Machine Regression Test Results Report
## Multi-Model Verification Across Synthetic Vectors (Tests A through E)

**Document ID:** `REPORT-PHASE31-REGRESSION-001`  
**Phase:** 31 (State-Machine Defect Verification)  
**Date:** November 2026  
**Status:** COMPLETED EMPIRICAL EVALUATION  

---

### MANDATORY SAFETY DESIGNATION
> [!CAUTION]
> **RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.**  
> This experimental acoustic machine-learning software is uncertified and must never be deployed for autonomous emergency dispatch, tactical police response, active-shooter alerting, automated evacuation, building lockdown, or life-critical physical security. Use legally obtained recordings and safe audio playback only. Live-fire testing and hazardous acoustic experiments are strictly prohibited.

---

## 1. Executive Summary & Verification Protocol

Phase 31 designed an isolated, non-hazardous synthetic regression test harness to rigorously test the event-clustering state machines of three implementations:
1. **`model_phase14.py`** — Frozen Default Research Baseline (SHA-256: `a2685516...`)
2. **`model_phase17.py`** — Frozen Selectable Experimental Profile (SHA-256: `e2b262b8...`)
3. **`model_phase17_state_reset_candidate.py`** — Separate Experimental Reset Candidate (SHA-256: `c144b917...`)

All tests were executed programmatically using mathematical synthetic score vectors under standardized detection parameters:
- `threshold_base = 0.75`
- `threshold_high = 0.88`
- `threshold_off = 0.48`
- `confirm_windows = 2`
- `cooldown_secs = 2.0`
- `single_win_min_crest_db = 12.0`

---

## 2. Regression Results Summary Matrix

| Test ID | Test Vector Description | Expected Alerts | Phase 14 Baseline | Phase 17 Frozen | Reset Candidate | State Machine Property Verified |
| :--- | :--- | :---: | :---: | :---: | :---: | :--- |
| **Test A** | Isolated Qualifying Spike ($0.78 \rightarrow 0.10 \rightarrow 0.10$) | **0** | **0 (PASS)** | **1 (FAIL_DEFECT)** | **0 (PASS)** | Single sub-threshold spike must not trigger an alert |
| **Test B** | Unrelated Spikes Across 100s Gap ($0.78 \dots 100\text{s} \dots 0.78$) | **0** | **0 (PASS)** | **1 (FAIL_DEFECT)** | **0 (PASS)** | Unconfirmed spikes must reset across temporal gaps |
| **Test C** | Consecutive 2-Window Confirmation ($0.78 \rightarrow 0.79$) | **1** | **1 (PASS)** | **1 (PASS)** | **1 (PASS)** | Valid multi-window confirmation logic preserved |
| **Test D** | Independent Recording Boundary (Trailing $0.78$, Leading $0.78$) | **0** | **0 (PASS)** | **1 (FAIL_DEFECT)** | **0 (PASS)** | No alert emission or state leakage across boundaries |
| **Test E** | Immediate Qualification ($0.92$ with $15.0\text{ dB}$ crest) | **1** | **1 (PASS)** | **1 (PASS)** | **1 (PASS)** | High-confidence ballistic impulse dispatch preserved |
| **Overall** | **5 Synthetic Test Vectors** | — | **5/5 PASS (100%)** | **2/5 PASS (40%)** | **5/5 PASS (100%)** | **Defect confirmed in P17; resolved in candidate** |

---

## 3. Detailed Per-Test Vector Findings

### 3.1. Test A — Isolated Qualifying Spike
- **Vector Specification:**
  - Window 0: $t \in [0.000, 0.975]\text{ s}$, $score = 0.78$ ($> 0.75\text{ base}, < 0.88\text{ high}$)
  - Window 1: $t \in [0.480, 1.455]\text{ s}$, $score = 0.10$ ($< 0.48\text{ off}$)
  - Window 2: $t \in [0.960, 1.935]\text{ s}$, $score = 0.10$
- **Expected Behavior:** Window 0 is an unconfirmed candidate ($len = 1 < 2$). Window 1 decays below threshold. The state machine must discard Window 0 and emit 0 alerts.
- **Observed Behavior:**
  - `model_phase14.py`: Clears `active_cluster` on Window 1 via `else: active_cluster = []`. Result: **0 alerts (PASS)**.
  - `model_phase17.py`: Fails to clear `active_cluster`. At EOF, evaluates `if active_cluster:` and emits a false alert with $duration = 0.975\text{ s}$, $score = 0.78$. Result: **1 alert (FAIL — Spurious Alert)**.
  - `model_phase17_state_reset_candidate.py`: Clears `active_cluster` on Window 1; EOF flush is guarded by `if in_event and active_cluster:`. Result: **0 alerts (PASS)**.

### 3.2. Test B — Unrelated Qualifying Spikes Across 100s Gap
- **Vector Specification:**
  - Spike 1: Window 0 at $t = 0.000\text{ s}$, $score = 0.78$, followed by silence.
  - Gap: 100 seconds of quiescent background noise ($score = 0.10$).
  - Spike 2: Window 50 at $t = 100.000\text{ s}$, $score = 0.78$, followed by silence.
- **Expected Behavior:** Neither spike achieves local 2-window confirmation. Both must decay independently. Expected: 0 alerts.
- **Observed Behavior:**
  - `model_phase14.py`: Discards Spike 1 at $t=0.48\text{ s}$. Discards Spike 2 at $t=100.48\text{ s}$. Result: **0 alerts (PASS)**.
  - `model_phase17.py`: Retains Spike 1 in memory across the entire 100s gap. When Spike 2 arrives at $t=100.0\text{ s}$, appends it to `active_cluster`. $len = 2 \ge confirm\_windows$, setting $in\_event = True$! Emits a single composite event spanning $0.000\text{ s}$ to $100.975\text{ s}$ ($duration = 100.975\text{ s}$, $windows\_count = 2$). Result: **1 alert (FAIL — Catastrophic Temporal Leakage)**.
  - `model_phase17_state_reset_candidate.py`: Correctly resets state on Window 1 and Window 51. Result: **0 alerts (PASS)**.

### 3.3. Test C — Consecutive Confirmation
- **Vector Specification:**
  - Window 0: $t \in [0.000, 0.975]\text{ s}$, $score = 0.78$
  - Window 1: $t \in [0.480, 1.455]\text{ s}$, $score = 0.79$
  - Window 2: $t \in [0.960, 1.935]\text{ s}$, $score = 0.10$
- **Expected Behavior:** Two consecutive windows exceed $0.75$, confirming a genuine 2-window event.
- **Observed Behavior:**
  - `model_phase14.py`: Emits 1 confirmed event ($start = 0.000\text{ s}, end = 1.455\text{ s}, score = 0.79$). Result: **1 alert (PASS)**.
  - `model_phase17.py`: Emits 1 confirmed event ($start = 0.000\text{ s}, end = 1.455\text{ s}, score = 0.79$). Result: **1 alert (PASS)**.
  - `model_phase17_state_reset_candidate.py`: Emits 1 confirmed event ($start = 0.000\text{ s}, end = 1.455\text{ s}, score = 0.79$). Result: **1 alert (PASS)**.

### 3.4. Test D — Reset After Recording Boundary
- **Vector Specification:**
  - File 1: Ends with an unconfirmed qualifying spike ($score = 0.78$ at $t = 0.48\text{ s}$).
  - File 2: Begins with an unconfirmed qualifying spike ($score = 0.78$ at $t = 0.00\text{ s}$).
- **Expected Behavior:** Each file evaluated independently must emit 0 alerts.
- **Observed Behavior:**
  - `model_phase14.py`: File 1 emits 0 alerts; File 2 emits 0 alerts. Result: **0 alerts total (PASS)**.
  - `model_phase17.py`: File 1 emits 1 alert due to unguarded EOF flush. Result: **1 alert (FAIL — Boundary False Alert)**.
  - `model_phase17_state_reset_candidate.py`: File 1 emits 0 alerts; File 2 emits 0 alerts. Result: **0 alerts total (PASS)**.

### 3.5. Test E — Genuine Immediate Qualification
- **Vector Specification:**
  - Window 0: $score = 0.92 \ge 0.88$, physical crest factor $= 15.0\text{ dB} \ge 12.0\text{ dB}$.
  - Window 1: $score = 0.10$.
- **Expected Behavior:** Emits 1 immediate alert on single high-confidence window.
- **Observed Behavior:**
  - `model_phase14.py`: Emits 1 immediate alert. Result: **1 alert (PASS)**.
  - `model_phase17.py`: Emits 1 immediate alert. Result: **1 alert (PASS)**.
  - `model_phase17_state_reset_candidate.py`: Emits 1 immediate alert. Result: **1 alert (PASS)**.

---

## 4. Empirical Conclusion

1. The state-machine defect in `model_phase17.py` is definitively proven. It fails 3 out of 5 synthetic regression tests (Tests A, B, and D).
2. The candidate patch in `experiments/phase31/model_phase17_state_reset_candidate.py` completely resolves the defect, passing 5 out of 5 tests (100%) while preserving all intended Phase 14 baseline behavior.
3. In accordance with Phase 31 governance rules, this candidate is an experimental prototype only and is NOT promoted to production or baseline status.

