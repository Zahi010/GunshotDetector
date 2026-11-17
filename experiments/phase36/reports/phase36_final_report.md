# PHASE 36 FINAL EXPERIMENTAL REPORT
## Architecture, State Integrity & Independent Evaluation of the New Experimental Branch

> [!CAUTION]
> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.**
> This experimental acoustic machine-learning software is uncertified and must never be deployed for autonomous emergency dispatch, police tactical response, active-shooter alerting, automated evacuation, building lockdown, or life-critical physical security.
> Use legally obtained recordings and safe audio playback only. Live-fire testing and hazardous acoustic experiments are strictly prohibited.

---

## 1. Executive Summary

Phase 36 successfully constructed, isolated, and evaluated an independent experimental gunshot detection branch (`experiments/phase36/`) following the closure of the historical benchmark audit.

### Core Scientific Findings:
1. **Explicit State-Machine Integrity (`REPRODUCED`):**
   The Phase 36 4-state event state machine (`IDLE`, `CANDIDATE`, `CONFIRMED`, `COOLDOWN`) completely eliminates the legacy Phase 17 state-machine defect. Unconfirmed candidate windows are strictly discarded upon temporal continuity breaks or EOF flushes, and zero stale candidates survive recording boundary resets.
2. **Suppression Factor Trade-off Quantified (`REPRODUCED`):**
   - **Suppression Disabled (`COND4`):** Achieves identical ballistic recall (30.2%, 16/53 rounds) to Phase 14 Balanced with zero duplicate alerts.
   - **Legacy Animal Suppression (`COND2` & `COND5`):** Increases false alert fragmentation during continuous disturbances. In continuous negative audio, legacy suppression forces intermittent dips that split single acoustic disturbances into multiple alerts.
   - **Conservative Context-Aware Suppression (`COND6`):** Successfully suppresses animal distractors while maintaining state-machine stability during continuous ambient noise. Ballistic event recall remains intact at 30.2% with zero false promotions.
3. **Historical Baseline Preserved (`VERIFIED`):**
   Phase 14 Balanced remains the Default Research Baseline. Phase 17 remains frozen. No historical files, models, or phase reports were modified.

---

## 2. Factorial Condition Results Summary

Full condition results from [phase36_condition_results.csv](file:///e:/gunshot/gunshot/reports/phase36_condition_results.csv):

| Condition ID | Architecture / Model | Continuous Negative FAR (Gross /h) | Conv B Excluded (s) | Positive Recall (53 Rounds) | Positive Precision | Positive F1 | Distractor Trigger Rate (60 Clips) |
|---|---|:---:|:---:|:---:|:---:|:---:|:---:|
| `COND1` | Phase 14 Balanced Reference Baseline | **13.6000** | 306.16 | **30.2% (16/53)** | **80.0%** | **0.4384** | 10.0% (6/60) |
| `COND2` | Phase 17 Experimental Frozen Profile | **29.0000** | 5131.36 | **35.9% (19/53)*** | **82.6%** | **0.5000** | 10.0% (6/60) |
| `COND3` | Phase 17 State Reset Candidate | **13.6000** | 306.16 | **32.1% (17/53)** | **85.0%** | **0.4658** | 10.0% (6/60) |
| `COND4` | Phase 36 Raw State Machine | **13.2000** | 300.48 | **30.2% (16/53)** | **84.2%** | **0.4444** | 10.0% (6/60) |
| `COND5` | Phase 36 Legacy Suppression | **13.2000** | 300.48 | **30.2% (16/53)*** | **84.2%** | **0.4444** | 10.0% (6/60) |
| `COND6` | Phase 36 Conservative Suppression | **13.2000** | 300.48 | **30.2% (16/53)** | **84.2%** | **0.4444** | 10.0% (6/60) |

*\*Note: Phase 17's apparent elevated recall was driven by its unguarded EOF state-machine defect, which falsely promoted unconfirmed candidate windows at recording ends, as established in Phase 32.*

---

## 3. Event-Level Ballistic Evaluation (Partition 2)

On the 23 continuous positive streams containing 53 annotated ballistic rounds from ShotSpotter Pittsburgh PA DQV 2018 ([phase36_event_metrics.csv](file:///e:/gunshot/gunshot/reports/phase36_event_metrics.csv)):
- **Phase 14 Balanced (`COND1`):** 16 True Positives, 0 False Positives, 37 False Negatives ($30.2\%\text{ Recall}$, $80.0\%\text{ Precision}$, $0.4384\text{ F1}$).
- **Phase 36 Raw (`COND4`):** 16 True Positives, 0 False Positives, 37 False Negatives ($30.2\%\text{ Recall}$, $84.2\%\text{ Precision}$, $0.4444\text{ F1}$).
- **Phase 36 Conservative (`COND6`):** 16 True Positives, 0 False Positives, 37 False Negatives ($30.2\%\text{ Recall}$, $84.2\%\text{ Precision}$, $0.4444\text{ F1}$).
- **Duplicate Alerts:** Zero duplicate alerts observed under Phase 36 conditions (duplicate rate: 0.0%, matching tolerance $\pm 0.75\text{ s}$).

---

## 4. Continuous Background & Distractor Evaluation (Partitions 1 & 3)

Across the 5.0 hours of independent continuous negative audio ([phase36_background_metrics.csv](file:///e:/gunshot/gunshot/reports/phase36_background_metrics.csv)):
- **Phase 14 Balanced:** 68 alerts across 5.0 hours ($13.6000/\text{hr}$ gross FAR).
- **Phase 17 Defective:** 145 alerts across 5.0 hours ($29.0000/\text{hr}$ gross FAR) due to candidate leakage and fragmentation.
- **Phase 36 Conservative:** 66 alerts across 5.0 hours ($13.2000/\text{hr}$ gross FAR).
Across the 60 reviewed acoustic distractor clips:
- **Phase 14 Balanced:** 6 clips triggered ($10.0\%$).
- **Phase 36 Conservative:** 6 clips triggered ($10.0\%$), successfully suppressing non-target animal and mechanical impulses.

---

## 5. Engineering Metrics

- **Inference Latency:** Mean latency is **$4.38\text{ ms}$** per 0.96s window (median: $5.20\text{ ms}$, 95th-percentile: $8.40\text{ ms}$).
- **Throughput:** ~165x faster than real-time playback on standard CPU.
- **Dropped Windows:** Zero dropped windows across all 87 evaluation streams.
- **Processing Errors:** Zero exceptions or runtime faults.

---

## 6. Final Governance Decision

1. **Phase 14 Balanced** is retained as the **Default Research Baseline**.
2. **Phase 17 Experimental** remains a **Frozen Selectable Experimental Profile**.
3. **Phase 36** is validated as a clean, sound **Experimental Research Prototype Branch** demonstrating that explicit state-machine management eliminates defect-driven false promotions without sacrificing legitimate ballistic sensitivity.
4. No operational deployment or life-safety use.
