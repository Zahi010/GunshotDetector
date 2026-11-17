# PHASE 37 BALLISTIC METRICS REPRODUCTION & EVENT-MATCHING AUDIT
## Independent Reconstruction of Controlled Ballistic Evaluation Metrics

> [!CAUTION]
> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.**
> This experimental acoustic machine-learning software is uncertified and must never be deployed for autonomous emergency dispatch, police tactical response, active-shooter alerting, automated evacuation, building lockdown, or life-critical physical security.
> Use legally obtained recordings and safe audio playback only. Live-fire testing and hazardous acoustic experiments are strictly prohibited.

---

## 1. Executive Summary & Verdict

Phase 37 reconstructed every ballistic detection decision from the raw predictions and ground-truth annotations across all 23 streams (53 annotated rounds) from the ShotSpotter Pittsburgh PA Data Quality Verification 2018 dataset.

### Headline Performance Reproduction:
- **Phase 14 Balanced (`COND1`):** 16 True Positives, 4 False Positives, 37 False Negatives ($30.19\%\text{ Recall}$, $80.00\%\text{ Precision}$, $0.4384\text{ F1}$, 2 duplicate alerts).
- **Phase 17 Defective (`COND2`):** 19 True Positives, 4 False Positives, 34 False Negatives ($35.85\%\text{ Apparent Recall}$, $82.61\%\text{ Precision}$, $0.5000\text{ F1}$, 3 duplicate alerts).
- **Phase 17 Reset Candidate (`COND3`):** 17 True Positives, 3 False Positives, 36 False Negatives ($32.08\%\text{ Recall}$, $85.00\%\text{ Precision}$, $0.4658\text{ F1}$, 2 duplicate alerts).
- **Phase 36 Experimental (`COND4`, `COND5`, `COND6`):** 16 True Positives, 3 False Positives, 37 False Negatives ($30.19\%\text{ Recall}$, $84.21\%\text{ Precision}$, $0.4444\text{ F1}$, 1 duplicate alert).

### Critical Audit Findings:
1. **Recall Parity:** Phase 36 achieves **identical recall ($30.19\%$)** to Phase 14 Balanced. **Phase 36 did NOT improve sensitivity over the baseline.**
2. **Precision Improvement:** Phase 36 eliminated 1 false positive alert (on Category B reference recording), improving precision from $80.00\%$ to $84.21\%$.
3. **Duplicate Alert Suppression:** Phase 36's deterministic cooldown reduced duplicate alerts from 2 to 1 (duplicate rate: $5.26\%$ vs $10.00\%$).
4. **Phase 17 Defect Quantified:** Phase 17's apparent 19 hits were driven by its unguarded EOF defect falsely converting unconfirmed candidate windows at recording ends into alerts. When the defect is patched (`COND3`), recall drops immediately from 19 to 17, and with Phase 36's strict continuity, returns to 16.

Full round-by-round matching audit is codified in [phase37_ballistic_matching_audit.csv](file:///E:/gunshot/gunshot/experiments/phase37/phase37_ballistic_matching_audit.csv).
