# PHASE 40 REPRODUCTION FINDINGS & CROSS-PHASE METRIC AUDIT
## Forensic Reconciliation of Phase 38 vs Phase 39 Detection Metrics

> [!CAUTION]
> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.**
> This software is uncertified research code. It must never be deployed for autonomous emergency dispatch, police tactical response, active-shooter alerting, automated evacuation, building lockdown, or life-critical physical security.
> Use lawfully obtained recordings and safe audio playback only. Live-fire testing and hazardous acoustic experiments are strictly prohibited.

---

## 1. Executive Summary

This audit resolved the reported discrepancy between Phase 38 and Phase 39 positive recall values:
- **Reported in Phase 40 prompt:**
  - Phase 14 (COND1): 74 / 120 (both)
  - Phase 17 (COND2): 81 / 120 (Phase 38) vs 92 / 120 (Phase 39)
  - Phase 31 (COND3): 75 / 120 (Phase 38) vs 77 / 120 (Phase 39)
  - Phase 36 (COND6): 77 / 120 (both)

### Authoritative Forensic Finding:
1. **Physical Artifact Concordance (`REPRODUCED`):**
   Re-execution of the frozen evaluators on the 120 prospective positive clips demonstrates **100.0% clip-level concordance** across all 720 clip-condition evaluations (see [phase40_clip_level_decision_diff.csv](file:///E:/gunshot/gunshot/experiments/phase40/phase40_clip_level_decision_diff.csv)):
   - **Phase 14 Balanced Baseline (COND1):** Exactly **74 / 120 detected** (61.67% recall, 46 FN, 28 duplicate alerts).
   - **Phase 17 Experimental Profile (COND2):** Exactly **92 / 120 detected** (76.67% recall, 28 FN, 26 duplicate alerts).
   - **Phase 17 State Reset Candidate (COND3):** Exactly **77 / 120 detected** (64.17% recall, 43 FN, 22 duplicate alerts).
   - **Phase 36 Raw FSM (COND4):** Exactly **77 / 120 detected** (64.17% recall, 43 FN, 13 duplicate alerts).
   - **Phase 36 Legacy Suppression (COND5):** Exactly **77 / 120 detected** (64.17% recall, 43 FN, 13 duplicate alerts).
   - **Phase 36 Conservative Suppression (COND6):** Exactly **77 / 120 detected** (64.17% recall, 43 FN, 13 duplicate alerts).

2. **Root Cause of the Discrepancy (`MANUAL_TRANSCRIPTION_ERROR`):**
   - In Phase 38, the official CSV artifact [phase38_positive_event_results.csv](file:///E:/gunshot/gunshot/experiments/phase38/phase38_positive_event_results.csv) and final report [phase38_final_evaluation_report.md](file:///E:/gunshot/gunshot/experiments/phase38/phase38_final_evaluation_report.md) recorded **COND2 = 92/120** and **COND3 = 77/120**.
   - In Phase 39, the automated reproduction script [scripts/reproduce_phase38_metrics.py](file:///E:/gunshot/gunshot/scripts/reproduce_phase38_metrics.py) successfully loaded the Phase 38 CSVs and created [phase39_phase38_reproduction.csv](file:///E:/gunshot/gunshot/experiments/phase39/phase39_phase38_reproduction.csv), which correctly contains **COND2 = 92** and **COND3 = 77**.
   - However, when formatting the Markdown report [phase39_metric_reconciliation.md](file:///E:/gunshot/gunshot/experiments/phase39/phase39_metric_reconciliation.md), lines 124–125 contained an unverified manual copy-paste transcription error:
     - COND2 was typed as `81 / 120` (39 FN, 24 duplicates) instead of `92 / 120` (28 FN, 26 duplicates).
     - COND3 was typed as `75 / 120` (45 FN, 22 duplicates) instead of `77 / 120` (43 FN, 22 duplicates).
   - No underlying detector code, feature cache, or CSV artifact ever generated 81 or 75. The true physical evaluation values for COND2 and COND3 on this prospective positive corpus are **92/120** and **77/120**, respectively.

---

## 2. Six-Condition Metric Audit Table

The table below reconciles the reported vs actual physical metrics across phases:

| Condition ID | Architecture Profile | Phase 38 Report Printed TP | Phase 38 CSV Recorded TP | Phase 39 Report Printed TP | Phase 39 CSV Recorded TP | Reproducible Ground Truth TP | Clip Recall (%) | 95% Clopper-Pearson CI | Duplicate Alerts | Audit Classification |
|---|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---|
| **COND1** | Phase 14 Balanced Baseline | 74 | 74 | 74 | 74 | **74 / 120** | 61.67% | [52.35%, 70.39%] | 28 | `CONCORDANT_REPRODUCED` |
| **COND2** | Phase 17 Experimental Profile | 92 | 92 | 81 *(error)* | 92 | **92 / 120** | 76.67% | [68.07%, 83.90%] | 26 | `MANUAL_TRANSCRIPTION_ERROR_IN_P39_REPORT` |
| **COND3** | Phase 17 State Reset Candidate | 77 | 77 | 75 *(error)* | 77 | **77 / 120** | 64.17% | [54.90%, 72.71%] | 22 | `MANUAL_TRANSCRIPTION_ERROR_IN_P39_REPORT` |
| **COND4** | Phase 36 Raw State Machine | 77 | 77 | 77 | 77 | **77 / 120** | 64.17% | [54.90%, 72.71%] | 13 | `CONCORDANT_REPRODUCED` |
| **COND5** | Phase 36 Legacy Suppression | 77 | 77 | 77 | 77 | **77 / 120** | 64.17% | [54.90%, 72.71%] | 13 | `CONCORDANT_REPRODUCED` |
| **COND6** | Phase 36 Conservative | 77 | 77 | 77 | 77 | **77 / 120** | 64.17% | [54.90%, 72.71%] | 13 | `CONCORDANT_REPRODUCED` |

Full difference dataset: [phase40_phase38_phase39_metric_diff.csv](file:///E:/gunshot/gunshot/experiments/phase40/phase40_phase38_phase39_metric_diff.csv).

---

## 3. Clip-Level Decision Consistency

We cross-audited all 120 positive clips evaluated under Phase 38 vs Phase 39 evaluation harnesses:
- **Total Comparisons:** 120 clips × 6 conditions = 720 clip decisions.
- **Decision Divergence Count:** **0 / 720 (0.00%)**.
- **Alert Count Divergence Count:** **0 / 720 (0.00%)**.
- **State Machine Event Boundaries:** Identical start times, end times, and peak scores across every file.

### Architectural Insights on Sensitivity Differences:
1. **COND2 Sensitivity Elevation (+15 TP over COND1, +15 TP over COND3/4/5/6):**
   - Phase 17's state machine defect (`if active_cluster:` without requiring `in_event`) allows single-window candidate accumulations at the end of audio files to convert into full alerts.
   - For 15 short gunfire clips where energy only triggered a single window above 0.75 without meeting confirmation requirements, COND2 emitted an alert.
   - When the state reset candidate was applied (COND3), this defect was eliminated, dropping detections from 92 to 77.
2. **COND1 vs COND4/5/6 (+3 TP for Phase 36 over Phase 14):**
   - Phase 14 detects 74/120 clips; Phase 36 detects 77/120 clips.
   - The 3 clips detected by Phase 36 but missed by Phase 14 had brief impulse transients where Phase 14's rigid multi-class suppression (e.g. fire/crackle or siren overlap) dampened scores below threshold, whereas Phase 36's conservative suppression preserved gunshot signal energy when crest-factor exceeded 12.0 dB.

