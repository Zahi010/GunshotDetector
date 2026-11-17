# Phase 31: State-Machine Forensic Audit Report
## Source Inspection, State Variable Dynamics & Defect Mechanism Verification

**Document ID:** `REPORT-PHASE31-STATEMACHINE-001`  
**Phase:** 31 (Defect Verification & Forensic Regression)  
**Date:** November 2026  
**Status:** DEFECT EMPIRICALLY CONFIRMED IN FROZEN PHASE 17 SOURCE  

---

### MANDATORY SAFETY DESIGNATION
> [!CAUTION]
> **RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.**  
> This experimental acoustic machine-learning software is uncertified and must never be deployed for autonomous emergency dispatch, tactical police response, active-shooter alerting, automated evacuation, building lockdown, or life-critical physical security. Use legally obtained recordings and safe audio playback only. Live-fire testing and hazardous acoustic experiments are strictly prohibited.

---

## 1. Executive Summary & Defect Statement

Phase 30 identified an apparent discrepancy between `model_phase14.py` and `model_phase17.py` regarding the handling of unconfirmed qualifying detection clusters.

Phase 31 conducted a rigorous, line-by-line inspection of the frozen source code of both models:
- **`model_phase14.py`** (SHA-256: `a2685516...`, 23,340 bytes, Frozen Default Research Baseline)
- **`model_phase17.py`** (SHA-256: `e2b262b8...`, 29,067 bytes, Frozen Selectable Experimental Profile)

### Definitive Conclusion
The reported defect in `model_phase17.py` is **100% CONFIRMED**.
The frozen implementation of Phase 17 contains two interrelated state-machine defects that cause severe alert inflation, cluster leakage across arbitrary temporal gaps, and spurious alerts at file boundaries:
1. **Defect 1 (Omission of Cluster Reset on Sub-Threshold Window):**  
   In `merge_phase17_events` (lines 150–155), the state machine fails to clear `active_cluster` when a window has $score < threshold\_base$ while $in\_event$ is `False`.
2. **Defect 2 (Unguarded Trailing Cluster Flush at EOF):**  
   In `merge_phase17_events` (lines 180–199), the trailing flush at file termination evaluates `if active_cluster:` instead of `if in_event and active_cluster:`, asserting an alert even when only a single unconfirmed window exists.
3. **Defect 3 (Streaming Detector State Leakage):**  
   In `RealTimeStreamDetectorPhase17.process_chunk` (lines 640–655), the streaming state machine similarly omits `else: self.active_cluster = []`, leaking unconfirmed candidates across consecutive chunks.

---

## 2. Line-by-Line Code Comparison

### 2.1. Batch / Offline Merger: `merge_phase14_events` vs `merge_phase17_events`

In `model_phase14.py` (lines 121–132):
```python
            else:
                if qualifies_immediate:
                    active_cluster = [win]
                    in_event = True
                    had_decayed = False
                elif score >= threshold_base:
                    active_cluster.append(win)
                    if len(active_cluster) >= confirm_windows:
                        in_event = True
                        had_decayed = False
                else:
                    active_cluster = []  # <--- CRITICAL: Clears unconfirmed candidate!
```

In `model_phase17.py` (lines 145–155):
```python
            else:
                if qualifies_immediate:
                    active_cluster = [win]
                    in_event = True
                    had_decayed = False
                elif score >= threshold_base:
                    active_cluster.append(win)
                    if len(active_cluster) >= confirm_windows:
                        in_event = True
                        had_decayed = False
                # <--- CRITICAL OMISSION: The 'else: active_cluster = []' branch is MISSING!
```

### 2.2. End-of-Sequence Flush Logic

In `model_phase14.py` (lines 143–144):
```python
    if in_event and active_cluster:
        events.append(_create_phase14_event_record(active_cluster))
```

In `model_phase17.py` (lines 180–199):
```python
    if active_cluster:  # <--- CRITICAL BUG: Emits alert even if in_event is False!
        ev_start = min(w["start_time"] for w in active_cluster)
        ev_end = max(w["end_time"] for w in active_cluster)
        ...
        events.append({ ... })
```

---

## 3. State Variable Dynamics & Failure Mode Analysis

The state machine tracks five core variables:
- `active_cluster: List[Dict]`: Accumulator of qualifying window records.
- `in_event: bool`: Whether the detector is currently within an active, confirmed gunfire episode.
- `had_decayed: bool`: Whether the acoustic score decayed below `threshold_off` (0.48) to reset refractory gating.
- `cooldown_until: float`: Refractory timestamp blocking immediate re-triggering.
- `qualifies_immediate: bool`: Whether a single window satisfies `score >= threshold_high` (0.88) with `crest_factor >= 12.0 dB`.

### Failure Scenario 1: Transient Unconfirmed Noise Spike at File Termination
1. A recording contains background noise with an isolated peak at $t = 10.0\text{ s}$ where $score = 0.78$ ($threshold\_base = 0.75$, $threshold\_high = 0.88$).
2. Window 1 is appended to `active_cluster` ($len = 1$). Because $len < 2$, $in\_event$ remains `False`.
3. Subsequent windows return to ambient silence ($score = 0.10$).
4. In Phase 14: On the very next window ($score = 0.10 < 0.75$), the `else:` branch executes: `active_cluster = []`. At EOF, `in_event` is `False`, so no alert is emitted (0 alerts).
5. In Phase 17: Because `else:` is omitted, `active_cluster` retains Window 1 indefinitely. At EOF, line 180 evaluates `if active_cluster:` (which is `True`), and EMITS A SPURIOUS ALERT for an unconfirmed single window!

### Failure Scenario 2: Unrelated Noise Spikes Separated by Minutes or Hours
1. A recording experiences an engine rumble at $t = 10.0\text{ s}$ ($score = 0.78$). Window 1 is stored in `active_cluster`.
2. Silent background audio persists for 100 seconds (or 1 hour).
3. At $t = 110.0\text{ s}$, an industrial crane thud produces an isolated sub-threshold spike ($score = 0.78$).
4. Window 200 is evaluated: $score \ge 0.75$, so it is appended to `active_cluster`.
5. Now $len(active\_cluster) = 2 \ge confirm\_windows$ (2)!
6. $in\_event$ becomes `True`!
7. The state machine synthesizes an alert with:
   - `start_time`: 10.000 s
   - `end_time`: 110.975 s
   - `duration`: 100.975 s
   - `windows_count`: 2
8. Two completely unrelated acoustic disturbances separated by 100 seconds are fused into an erroneous 100-second continuous gunshot detection alert.

---

## 4. Architectural Lineage: Why Was the Reset Branch Omitted?

During Phase 17 development, the author refactored `model_phase14.py` to embed the experimental animal vocalization suppression gate. During the rewrite of `merge_phase17_events`:
- The inline helper `_create_phase14_event_record` was eliminated in favor of an in-place dictionary construction.
- During the restructuring of the `if not in_event:` conditional ladder, the trailing `else: active_cluster = []` clause was accidentally dropped.
- In addition, the author replaced `if in_event and active_cluster:` with `if active_cluster:` at the bottom of the function.

Because historical unit tests in Phase 17 tested synthetic multi-round bursts and short isolated clips (where files were $< 1.05\text{ s}$ and triggered `allow_short_clip_exception`), the defect was not caught during initial development.

---

## 5. Governance Directive

1. **Do Not Overwrite Frozen `model_phase17.py`:**  
   Per Phase 31 Section 8 instructions, the frozen historical file `model_phase17.py` must NEVER be modified or silently replaced. Historical evaluation artifacts must remain exact.
2. **Designate Phase 17 as Defective:**  
   Phase 17 Experimental is officially classified as possessing an unconfirmed cluster retention defect and an unguarded trailing flush defect.
3. **Preserve Phase 14 as Baseline:**  
   Phase 14 Balanced remains the sole and unmodified Default Research Baseline.

