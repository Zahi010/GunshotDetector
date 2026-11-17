# PHASE 39 POSITIVE ANNOTATION METHODOLOGY AUDIT REPORT
## Forensic Audit of Ground-Truth Granularity, Timestamp Lineage & Evaluation Validity

> [!CAUTION]
> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.**
> This software is uncertified research code. It must never be deployed for autonomous emergency dispatch, police tactical response, active-shooter alerting, automated evacuation, building lockdown, or life-critical physical security.
> Use lawfully obtained recordings and safe audio playback only. Live-fire testing and hazardous acoustic experiments are strictly prohibited.

---

## 1. Executive Summary

This audit rigorously inspects the ground truth and annotation methodology used for the 120 positive gunshot recordings in Phase 38.

### Key Audit Findings:
1. **Ground Truth is Strictly Clip-Level Multi-Label:**
   All 120 positive recordings originate from the Freesound Dataset 50K (FSD50K Dev Set, Fonseca et al., IEEE/ACM TASLP 2021). The underlying ground-truth annotation provided by FSD50K is a **clip-level class label** (`Gunshot_and_gunfire`), verified through Freesound collaborative tagging and AudioSet ontology mapping.
2. **Zero Temporal Event Onset or Offset Annotations:**
   **0 out of 120 clips (0.0%)** have human-annotated event onset timestamps, offset timestamps, or round-by-round time-series annotations. FSD50K provides weak labels for whole audio clips (ranging from 0.34 s to 10.0 s duration), not time-stamped acoustic boundaries.
3. **No Exact Matching Window Was Applied:**
   Phase 38 documented an evaluation tolerance of [-0.50 s, +1.00 s] relative to event onset. However, forensic inspection of `scripts/run_phase38_prospective_evaluation.py` reveals that because no onset timestamps existed, the evaluation code evaluated `if len(events) > 0: tp_events += 1`. Any alert emitted anywhere within the clip counted as a True Positive.
4. **Heuristic Round Inferences:**
   In Phase 38, burst-fire vs single-round status was heuristically estimated based on uploader tags and titles (assigning a nominal count of 3 rounds for burst fire), with a nominal peak time placed at the mathematical midpoint (`duration / 2.0`). This midpoint was never verified against acoustic pressure logs.
5. **Mandatory Reclassification:**
   In accordance with research integrity standards, the Phase 38 results (74/120 for Phase 14; 77/120 for Phase 36) must be classified as **CLIP-LEVEL DETECTION ACCURACY / RECALL**, and **NOT** strict event-level or round-level ballistic recall.

---

## 2. Granularity Hierarchy: Classification vs Event Detection vs Round Detection

To establish methodological clarity for future phases, acoustic gunshot detection evaluation must be partitioned into three distinct operational tiers:

| Evaluation Tier | Ground-Truth Requirement | Matching Criteria | Meaning of Metric | Phase 38 Applicability |
|---|---|---|---|:---:|
| **Tier 1: Clip-Level Classification** | Weak clip-level label (e.g. FSD50K `Gunshot_and_gunfire`) | Any confirmed alert emitted within clip duration ([0, T]) | Proportion of gunshot-containing clips triggering at least 1 alert | **APPLICABLE (True Status of Phase 38)** |
| **Tier 2: Event-Level Detection** | Human-annotated acoustic event onset ($t_0$) and offset ($t_1$) | Alert onset falls within [$t_0 - 0.50\text{ s}$, $t_0 + 1.00\text{ s}$] | Proportion of discrete acoustic gunfire incidents detected | **NOT APPLICABLE (No timestamps in FSD50K)** |
| **Tier 3: Round-Level Ballistic Verification** | High-speed ballistic ground-truth with physical round timestamps | Individual muzzle blast or shockwave peak matching within millisecond tolerance | Proportion of physical ballistic discharges detected | **NOT APPLICABLE (Only available in controlled live-fire tests like Pittsburgh DQV)** |

---

## 3. Clip-by-Clip Audit Summary (N = 120 Positive Clips)

- **Total Clips Audited:** 120
- **Source Dataset:** FSD50K Dev Set (`E:/FSD50K.dev_audio/`)
- **Total Unique Uploaders:** 120 distinct uploaders (zero session correlation)
- **Clips with Clip-Level Class Label:** 120 / 120 (100.0%)
- **Clips with Human-Annotated Onset:** 0 / 120 (0.0%)
- **Clips with Human-Annotated Offset:** 0 / 120 (0.0%)
- **Clips with Round-Level Ballistic Logs:** 0 / 120 (0.0%)
- **Clips with Independently Verified Timestamps:** 0 / 120 (0.0%)
- **Evaluation Status:** Verified as **CLIP-LEVEL DETECTION**.

The full clip-by-clip registry is recorded in [phase39_positive_annotation_audit.csv](file:///E:/gunshot/gunshot/experiments/phase39/phase39_positive_annotation_audit.csv).

---

## 4. Governance Implications

1. **Honest Reporting:** The Phase 38 positive sensitivity numbers (Phase 14: 61.7%; Phase 36: 64.2%) accurately measure clip-level detection rate on unseen, diverse gunshot recordings. They should be described strictly as clip-level detection rate.
2. **No Ground-Truth Manufacturing:** No synthetic timestamps have been manufactured or retroactively fitted to detector alert times. FSD50K clips remain categorized by their authentic weak labels.
