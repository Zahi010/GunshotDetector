# Phase 35 Technical Report: Ground-Truth Annotation Audit & False Alert Terminology Review

> [!CAUTION]
> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.**
> This experimental acoustic machine-learning software is uncertified and must never be deployed for autonomous emergency dispatch, police tactical response, active-shooter alerting, automated evacuation, building lockdown, or life-critical physical security.
> Use legally obtained recordings and safe audio playback only. Live-fire testing and hazardous acoustic experiments are strictly prohibited.

---

## 1. Executive Summary

Phase 34 described alerts across Southampton, Chew Magna, and Bilbao as "false alerts" and characterized them as "short acoustic transients."
This workstream conducted a forensic audit of all 287 alerts across the 23-stream continuous benchmark to evaluate whether the underlying annotations support this descriptive language.

### Categorization Standards
In accordance with Phase 35 audit instructions, alerts are classified into five strict scientific categories:
1. `CONFIRMED_NON_TARGET`: Accompanied by an explicit, external, microsecond-accurate event-level non-gunshot annotation from the source dataset provider.
2. `REVIEWED_NON_TARGET`: Formally audited via independent acoustic listening review and classified as non-target distractors by human researchers.
3. `UNANNOTATED_BACKGROUND`: Continuous environmental recordings with zero event-level annotations; non-target status is inferred solely from negative macro-context and the absence of gunshot reports.
4. `POSSIBLE_TARGET`: Acoustic events resembling ballistic shockwaves or muzzle blasts that cannot be excluded without further verification.
5. `UNKNOWN`: Insufficient recording or metadata context to determine origin.

---

## 2. Benchmark Audit Findings

| Campaign Cluster | Stream Count | Phase 14 Alerts | Phase 17 Alerts | Total Alerts | Review Status | Primary Ground-Truth Category |
|---|:---:|:---:|:---:|:---:|---|---|
| `CAMPAIGN-SOUTHAMPTON-EXP1` | 10 | 24 | 22 | 46 | Double-blind expert listening review (Phase 24) | `REVIEWED_NON_TARGET` |
| `CAMPAIGN-CHEW-MAGNA` | 1 | 0 | 0 | 0 | Quiescent rural stream (0 alerts) | N/A |
| `CAMPAIGN-BILBAO` | 6 | 32 | 29 | 61 | Double-blind expert listening review (Phase 24) | `REVIEWED_NON_TARGET` |
| `CAMPAIGN-ADELAIDE-AEROSONIC` | 6 | 72 | 108 | 180 | Unreviewed continuous ambient audio (Phase 29) | `UNANNOTATED_BACKGROUND` |
| **CORPUS TOTAL** | **23** | **128** | **159** | **287** | **107 Reviewed / 180 Unreviewed** | **37.3% REVIEWED / 62.7% UNANNOTATED** |

### Key Scientific Distinctions:
1. **Zero Alerts Qualify as `CONFIRMED_NON_TARGET`:**
   None of the source Zenodo repositories (Zenodo 4009292, 3670814, 10215080) contain microsecond-accurate ground-truth event labels for continuous background streams. The files were captured as general environmental soundscapes.
2. **107 Alerts Qualify as `REVIEWED_NON_TARGET`:**
   In Phase 24, all 107 European campaign alerts (46 Southampton, 61 Bilbao) underwent blinded dual-reviewer listening evaluation (`R1_Acoustic_DSP` and `R2_Forensic_Audio`). Reviewers classified specific acoustic distractor morphologies (e.g. pneumatic damper snaps, vehicle air brakes, rooster crows, hen clucks, door slams). These are legitimately classified as `REVIEWED_NON_TARGET`.
3. **180 Alerts Qualify as `UNANNOTATED_BACKGROUND`:**
   The 180 Adelaide Airport alerts (72 Phase 14, 108 Phase 17) occur in continuous unbroken 1-hour files from AeroSonicDB (`env_audio.zip`). As confirmed in Phase 29 Section 2, none of these 25 sequences underwent human listening review. They represent detector activations during continuous acoustic disturbances attributed to suspected aircraft based on catalog metadata.

---

## 3. Recommended Descriptive Phrasing

To prevent overstating benchmark verification rigor, future technical documentation must adhere to the following linguistic rules:
- **Do NOT claim:** *"All 287 alerts are confirmed false alarms."* (Incorrect; 180 alerts lack event annotations or human review).
- **Do NOT claim:** *"Zero false alerts occurred in Adelaide."* (Incorrect; activations occurred during unreviewed ambient recordings).
- **Acceptable scientific terminology:**
  - *"The benchmark observed 107 expert-reviewed non-target alerts in European environmental recordings and 180 detector activations in unreviewed continuous airport ambient streams."*
  - *"Non-target status for Adelaide activations is inferred from macro-context (airport vicinity without reported firearms discharge), but event-level ground truth remains unannotated."*

See [phase35_alert_ground_truth_audit.csv](file:///e:/gunshot/gunshot/reports/phase35_alert_ground_truth_audit.csv) for the full 287-alert ledger.
