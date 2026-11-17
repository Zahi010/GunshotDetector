# Phase 31: Experimental Patch Review Report
## Minimal State-Machine Reset Candidate Inspection & Source Diff Analysis

**Document ID:** `REPORT-PHASE31-PATCH-001`  
**Phase:** 31 (State-Machine Defect Verification & Patch Review)  
**Date:** November 2026  
**Status:** EXPERIMENTAL CANDIDATE AUDITED — DO NOT DEPLOY TO PRODUCTION  

---

### MANDATORY SAFETY DESIGNATION
> [!CAUTION]
> **RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.**  
> This experimental acoustic machine-learning software is uncertified and must never be deployed for autonomous emergency dispatch, tactical police response, active-shooter alerting, automated evacuation, building lockdown, or life-critical physical security. Use legally obtained recordings and safe audio playback only. Live-fire testing and hazardous acoustic experiments are strictly prohibited.

---

## 1. Executive Summary & Governance Directive

Following empirical confirmation of the state-machine defect in `model_phase17.py`, Phase 31 authored an isolated experimental implementation:
- **File Location:** `experiments/phase31/model_phase17_state_reset_candidate.py`
- **File Size:** 29,718 bytes
- **SHA-256 Digest:** `c144b917b56532787e2a9198f2cad4a77dc2095b57962f31d11d250a4d5d9ea5`

### Strict Governance Constraints (Section 4 & Section 8)
1. **No Changes to Frozen Models:**  
   `model_phase14.py` and `model_phase17.py` remain frozen and unmodified. Their canonical hashes are verified and preserved.
2. **Experimental Designation Only:**  
   `model_phase17_state_reset_candidate.py` is an experimental research candidate created solely for regression verification. It is NOT promoted to baseline, default, or production status.
3. **No Retrospective Benchmark cherry-picking:**  
   This candidate must not be evaluated on the existing continuous benchmark to cherry-pick favorable metrics. Synthetic regression tests establish the state-machine properties; new, independently collected field data would be mandatory for any future performance claims.

---

## 2. Artifact Comparison & Cryptographic Provenance

| Property | Frozen Historical Model (`model_phase17.py`) | Experimental Candidate (`model_phase17_state_reset_candidate.py`) |
| :--- | :--- | :--- |
| **Role** | Selectable Experimental Profile | Isolated Experimental Patch Candidate |
| **Path** | `E:/gunshot/gunshot/model_phase17.py` | `E:/gunshot/gunshot/experiments/phase31/model_phase17_state_reset_candidate.py` |
| **Size (Bytes)** | 29,067 bytes | 29,718 bytes |
| **SHA-256** | `e2b262b866fdd5d7f1a4ab91a7b8b9bac189ee8cc7a78603b3544ca1579fb819` | `c144b917b56532787e2a9198f2cad4a77dc2095b57962f31d11d250a4d5d9ea5` |
| **State-Machine Reset**| Omitted (`active_cluster` retained across gaps) | Restored (`else: active_cluster = []`) |
| **EOF Flush Guard** | Unguarded (`if active_cluster:`) | Guarded (`if in_event and active_cluster:`) |
| **Streaming Reset** | Omitted | Restored (`else: self.active_cluster = []`) |
| **Synthetic Test Score**| 2/5 PASS (40%) | 5/5 PASS (100%) |

---

## 3. Exact Unified Diff

```diff
--- model_phase17.py
+++ model_phase17_state_reset_candidate.py
@@ -1,3 +1,9 @@
+# =============================================================================
+# PHASE 31 EXPERIMENTAL CANDIDATE: STATE-MACHINE RESET PATCH
+# MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY
+# EXPERIMENTAL ARTIFACT ONLY — DO NOT OVERWRITE FROZEN model_phase17.py OR model_phase14.py
+# Restores the missing 'else: active_cluster = []' reset branch and guards EOF flushing.
+# =============================================================================
 """
 Phase 17 Experimental Adaptive Gunshot Detector.
 
@@ -152,6 +158,8 @@
                     if len(active_cluster) >= confirm_windows:
                         in_event = True
                         had_decayed = False
+                else:
+                    active_cluster = []
         else:
             if score >= threshold_off:
                 active_cluster.append(win)
@@ -177,7 +185,7 @@
                 in_event = False
                 had_decayed = True
 
-    if active_cluster:
+    if in_event and active_cluster:
         ev_start = min(w["start_time"] for w in active_cluster)
         ev_end = max(w["end_time"] for w in active_cluster)
         max_sc = max(w["score"] for w in active_cluster)
@@ -647,6 +655,8 @@
                                 new_alerts.append(alert)
                                 self.detected_alerts.append(alert)
                                 self.cooldown_until = win_et + self.detector.cooldown_secs
+                        else:
+                            self.active_cluster = []
                 else:
                     if calibrated_s >= self.detector.threshold_off:
                         self.active_cluster.append(win_record)
```

---

## 4. Technical Explanation of Applied Modifications

1. **Safety Banner & Candidate Notice (Lines 1–9):**  
   Explicitly declares the experimental nature of the file and warns future operators never to overwrite the frozen baseline or experimental models.
2. **Offline Event Merger Reset Branch (Lines 158–160):**  
   In `merge_phase17_events`, when $st \ge cooldown\_until$ and a window fails to qualify ($score < threshold\_base$), the `else: active_cluster = []` clause immediately resets the unconfirmed cluster. This prevents transient noise spikes from leaking across subsequent silence or merging with distant subsequent disturbances.
3. **Guarded End-of-Sequence Flush (Line 188):**  
   Changes `if active_cluster:` to `if in_event and active_cluster:`. If a recording terminates with a single sub-threshold window ($len = 1, in\_event = False$), it is properly dropped rather than emitted as a false alarm.
4. **Streaming Ring-Buffer Reset Branch (Lines 658–660):**  
   In `RealTimeStreamDetectorPhase17.process_chunk`, when incoming audio chunks do not qualify, `self.active_cluster = []` ensures that memory across streaming buffers does not persist unconfirmed candidates.

---

## 5. Architectural Review & Governance Decision

- **Verification:** All 5 synthetic regression tests pass with zero regressions.
- **Decision:** The patch proves the technical root cause of the Phase 17 state-machine defect. However, because Phase 17 remains an experimental profile that demonstrated increased false alert susceptibility in real-world continuous audio (+31 false alarms), **Phase 17 is officially rejected for baseline promotion**. Phase 14 Balanced remains the Default Research Baseline.

