# Phase 30 Non-Invasive Diagnostic Instrumentation Architecture & Design Specification

> **MANDATORY SAFETY DESIGNATION**  
> **RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.**  
> This experimental acoustic machine-learning software is uncertified and must never be deployed for autonomous emergency dispatch, tactical police response, active-shooter alerting, automated evacuation, building lockdown, or life-critical physical security. Use legally obtained recordings and safe audio playback only. Live-fire testing and hazardous acoustic experiments are strictly prohibited.

---

## 1. Executive Summary & Objective

In Phase 29, the forensic audit established that while Phase 17 produced 36 additional false alerts (+50.0%) and 5,931.28 seconds of extra cooldown exclusion in AeroSonicDB, the underlying intermediate states (such as sub-window model scores, animal classifier activations, suppression penalties, and state-machine transitions) were unpersisted in raw event logs. Consequently, the aircraft-fragmentation explanation remained classified as **PARTIALLY_SUPPORTED_UNVERIFIED_INTERMEDIATES**.

Phase 30 resolves this empirical limitation by designing and implementing a **non-invasive, mathematically invariant diagnostic instrumentation architecture** (`gunshot/instrumented_detector.py`). This layer wraps the frozen feature extraction pipeline and ensemble models, intercepting and logging every intermediate variable without modifying detector behavior, parameters, or outputs.

---

## 2. Strict Invariance Design Principles

To ensure that diagnostic instrumentation does not alter detector behavior or invalidate historical comparisons, the instrumentation architecture strictly complies with the following invariants:

1. **Frozen Code Isolation:** The source files `model_phase14.py` and `model_phase17.py` are left strictly read-only and unmodified. All diagnostic logging is encapsulated in an external wrapper class (`InstrumentedDetector` in `instrumented_detector.py`).
2. **Deterministic Feature Invariance:** Audio waveforms are converted to 16 kHz tensors and passed through the exact frozen `YAMNetFeatureExtractor` instance, ensuring that extracted embeddings and semantic logits are identical bit-for-bit to production runs.
3. **Threshold and Parameter Preservation:** All runtime parameters are strictly bound to canonical frozen values:
   $$\text{threshold\_base} = 0.75, \quad \text{threshold\_high} = 0.88, \quad \text{threshold\_off} = 0.48$$
   $$\text{confirm\_windows} = 2, \quad \text{cooldown\_secs} = 2.0\text{ s}, \quad \text{window\_samples} = 15,600, \quad \text{hop\_samples} = 7,680$$
4. **Hysteresis State Synchronization:** State-machine transitions are evaluated using the official frozen merger routines (`merge_phase14_events` and `merge_phase17_events`), while a parallel shadow tracker reconstructs sub-window transition flags (`in_event`, `had_decayed`, `alert_asserted`, `alert_terminated`) to provide cycle-accurate audit trails.

---

## 3. Intercepted Diagnostic State Space

For each 0.975-second window (0.48-second hop), the instrumented detector logs a comprehensive 22-dimensional telemetry vector:

| Variable | Data Type | Units / Range | Engineering Description |
| :--- | :--- | :--- | :--- |
| `recording_id` | String | Categorical | Continuous recording stream identifier (e.g. `P27-AERO-STR-01`) |
| `window_index` | Integer | $[0, 7498]$ | Sequential zero-based sub-window index |
| `start_time_s` | Float | Seconds | Physical start timestamp of the window ($i \times 0.48\text{ s}$) |
| `end_time_s` | Float | Seconds | Physical end timestamp of the window ($\text{start} + 0.975\text{ s}$) |
| `raw_score` | Float | $[0.0, 1.0]$ | Raw unsuppressed gunshot prediction from the ensemble model |
| `gun_semantic_score` | Float | $[0.0, 1.0]$ | $\max(\text{YAMNet logits for gunshot, machine gun, artillery, cap gun})$ |
| `animal_semantic_score` | Float | $[0.0, 1.0]$ | $\max(\text{YAMNet logits across 13 animal vocalization classes})$ |
| `thunder_score` | Float | $[0.0, 1.0]$ | $\max(\text{YAMNet logits for thunderstorm, thunder})$ |
| `fireworks_score` | Float | $[0.0, 1.0]$ | $\max(\text{YAMNet logits for fireworks, firecracker})$ |
| `dog_score` | Float | $[0.0, 1.0]$ | $\max(\text{YAMNet logits for dog, bark, yip, canidae})$ |
| `siren_score` | Float | $[0.0, 1.0]$ | $\max(\text{YAMNet logits for emergency sirens and defense alarms})$ |
| `p14_score` | Float | $[0.0, 1.0]$ | Phase 14 calibrated score after semantic gating |
| `p14_suppression_reason` | String | Categorical | Active Phase 14 suppression category (`None`, `thunder`, `fireworks`, etc.) |
| `animal_suppression_active` | Boolean | True / False | Phase 17 animal condition ($\text{animal\_s} > 0.35 \land \text{animal\_s} \ge 2.0 \times \text{gun\_s}$) |
| `animal_suppression_penalty` | Float | $0.30 \text{ or } 1.00$ | Score attenuation scalar applied by Phase 17 |
| `p17_score` | Float | $[0.0, 1.0]$ | Post-animal-suppression Phase 17 score ($\text{p14\_score} \times \text{penalty}$) |
| `p17_suppression_reason` | String | Categorical | Active Phase 17 suppression category (including `animal_vocalization`) |
| `p14_in_event` | Boolean | True / False | Phase 14 state-machine event active state |
| `p14_cooldown_until_s` | Float | Seconds | Timestamp through which new Phase 14 cluster formation is gated |
| `p17_in_event` | Boolean | True / False | Phase 17 state-machine event active state |
| `p17_cooldown_until_s` | Float | Seconds | Timestamp through which new Phase 17 cluster formation is gated |
| `overall_mechanism_verdict` | String | Categorical | Telemetry diagnostic classification for candidate multi-alert episodes |

---

## 4. Analytical Counterfactual Path

In addition to logging the two production baselines, the instrumentation layer executes an **analytical counterfactual replay**:
- **Definition:** Replaying the identical raw scores and Phase 14 semantic gating scores through Phase 17's state-machine merger, but with animal suppression explicitly forced to `False`.
- **Purpose:** By evaluating whether the 36-alert inflation and 29.1% dead-time expansion disappear when animal suppression is neutralized, the analytical counterfactual isolates whether the fragmentation is caused by the acoustic gating penalty or by structural differences in the merger logic.
- **Analytical Boundary:** This counterfactual replay is strictly an experimental diagnostic probe; it is not a candidate detector, has not been validated for live monitoring, and must never be treated as an operational model profile.

---

## 5. Architectural Diagram

```
                 Continuous Waveform (16 kHz PCM)
                                │
                  YAMNet Feature Extraction
                                │
        ┌───────────────────────┴───────────────────────┐
        ▼                                               ▼
1,024-d Embeddings (N x 1024)             521-Class Semantic Logits
        │                                               │
Ensemble Classifier (CatBoost/LGBM/XGB)       Semantic Class Extraction
        │                                               │
  Raw Score (raw_score)                   [Gunshot, Animal, Thunder, Fireworks, Siren]
        │                                               │
        └───────────────────────┬───────────────────────┘
                                ▼
                   Phase 14 Semantic Gating
                                │
                      p14_score (Logged)
                                │
        ┌───────────────────────┴───────────────────────┐
        │                                               │
[Animal Supp Disabled]                        [Animal Supp Enabled]
        │                                 animal_s > 0.35 & animal_s >= 2.0*gun_s?
        │                                               │
        │                                       ┌───────┴───────┐
        │                                       ▼ YES           ▼ NO
        │                                  score *= 0.30    score *= 1.0
        │                                       └───────┬───────┘
        ▼                                               ▼
Phase 14 State Machine                        Phase 17 State Machine
  (merge_phase14_events)                        (merge_phase17_events)
        │                                               │
   P14 Alerts                                      P17 Alerts
 (Exact 72 Alerts)                              (Exact 108 Alerts)
```

---

## 6. Deliverable Linkages

The instrumentation layer directly drives:
- `reports/phase30_instrumentation_invariance_audit.md` (Verifying 0.000 deviation against ground-truth)
- `reports/phase30_instrumented_event_log.csv` (180 event records across 6 continuous hours)
- `reports/phase30_instrumented_score_traces.csv` (44,994 sub-window telemetry records)
- `reports/phase30_suppression_mechanism_analysis.md` (Forensic evaluation of 25 multi-alert sequences)

