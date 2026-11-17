# PHASE 21 MASTER TECHNICAL REPORT: CLUSTER-AWARE STATISTICAL VALIDATION, METRIC RECONCILIATION & FINAL EVIDENCE AUDIT

> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY**  
> *This experimental acoustic machine-learning system is not certified and must never be used for autonomous emergency dispatch, police response, active-shooter alerting, automated evacuation, or critical physical security.*  
> *Use legally obtained recordings and safe playback only. No live-fire testing or hazardous acoustic experiments.*

---

## Executive Summary

Phase 21 concludes the forensic re-evaluation of the acoustic gunshot detection research project by subjecting the Phase 20 Pittsburgh validation findings to rigorous **cluster-aware statistical modeling, metric reconciliation, and exposure re-quantification**.

In Phase 20, the experimental candidate (**Phase 17 Experimental**) detected 6 more physical rounds than the production baseline (**Phase 14 Balanced**) on the 50-round Category A benchmark (ShotSpotter Pittsburgh PA DQV 2018), yielding an unadjusted paired event-level McNemar test of $p = 0.03125$.

This Phase 21 audit proves that the perceived statistical superiority of Phase 17 Experimental is an artifact of treating clustered acoustic events as independent and identically distributed (i.i.d.) observations. When evaluated under cluster-aware hierarchies, incident-level metrics, and multiple-testing corrections, the statistical significance disappears.

### Core Audit Discoveries:
1. **Event-Level Reproduction Verified ($p = 0.03125$):** The paired event contingency table ($a=27, b=0, c=6, d=17$) is 100% mathematically reproduced. Under naive event-level assumptions, the exact two-sided binomial $p$-value is $0.03125$.
2. **Cluster Concentration:** The 6 additional Phase 17 detections are **not distributed across the campaign**:
   - **FP4 alone accounts for 3 of the 6 gained rounds (50.0%)**.
   - **FP1 accounts for 2 gained rounds (33.3%)**.
   - In FP2 and FP5, Phase 17 achieved **exactly zero gain** over Phase 14 Balanced (both models achieved identical recall).
3. **Fragility Under Leave-One-Position-Out (LOPO):** Excluding FP4 causes the round gain to drop from +6 to +3, increasing the McNemar $p$-value from **$0.03125$ to $0.25000$** ($8\times$ higher). Excluding FP1 increases $p$ to **$0.12500$**. The apparent significance is driven by single street-corner clusters.
4. **Incident-Level Equivalence ($p = 0.25000$):** In 15 of 20 recordings (75.0%), both models produced identical round counts. Across the 20 streams, incident recall is $75.0\%$ (15/20) for Phase 14 and $90.0\%$ (18/20) for Phase 17. The paired incident-level exact binomial test yields **$p = 0.25000$ (NOT statistically significant)**.
5. **Multiple-Comparison Adjustments (Holm-Bonferroni):** When controlling family-wise error across all candidate model comparisons, Phase 17's adjusted $p$-value is **$p_{\text{Holm}} = 0.12500$** (NOT significant at $\alpha = 0.05$).
6. **False-Alert Exposure Correction:** Category A contains only **$140.4\text{ seconds}$ (~2.34 minutes) of quiescent background exposure**. The exact 95% Poisson Garwood upper bound on false alarms is **$77.03\text{ alerts/hour}$**—too loose to evaluate false-alarm resistance.
7. **Category D Metric Reconciled:** The discrepancy between $83.33\%$ (Phase 19) and $89.3\%$ (Phase 20) is resolved: $83.33\%$ is Phase 14 Balanced recall on the 42-clip Mitchell set ($35/42$), while $89.29\%$ is Phase 14 High-Sensitivity recall on the 28-event discrete test set ($25/28$).
8. **Final Architectural Decision:** **Phase 14 Balanced remains the DEFAULT PRODUCTION BASELINE.** Phase 17 Experimental remains a selectable experimental profile.

---

## 1. Explicit Answers to the Ten Final Decision-Gate Questions

### Question 1: Does the event-level $p = 0.03125$ reproduce?
**Audited Verdict: YES (Exactly Reproduced).**  
Evaluating the 50 canonical physical gunshot rounds in Category A yields:
- Both detected: **27 rounds** (54.0%)
- Phase 14 only: **0 rounds** (0.0%)
- Phase 17 only: **6 rounds** (12.0%)
- Neither detected: **17 rounds** (34.0%)
- Discordant pairs: $n = 6$
The exact two-sided binomial test calculation:
$$p = 2 \cdot \binom{6}{0} (0.5)^6 = 2 \cdot \frac{1}{64} = 0.03125$$
This confirms the mathematical arithmetic of Phase 20.

### Question 2: Does the result remain persuasive after accounting for recording and burst clustering?
**Audited Verdict: NO.**  
The 50 rounds are physically clustered within 20 recordings and 15 bursts. When evaluated at the recording level:
- In 15 of 20 recordings (75%), both models exhibit identical round detections.
- At the incident level (detecting the shooting stream), Phase 14 detected 15/20 and Phase 17 detected 18/20. The paired exact binomial test yields **$p = 0.25000$**.
- A non-parametric Wilcoxon signed-rank test on recording recall differences yields **$p = 0.06250$** (not significant at $\alpha = 0.05$).
The apparent statistical significance disappears once intra-recording covariance is respected.

### Question 3: Are the six additional detections distributed across multiple firing positions?
**Audited Verdict: NO (Heavily Concentrated in FP4 and FP1).**  
The six gained rounds are distributed as follows:
- **FP4:** **+3 rounds (50.0% of the entire gain)**
- **FP1:** **+2 rounds (33.3% of the entire gain)**
- **FP3:** **+1 round (16.7% of the entire gain)**
- **FP2:** **+0 rounds (0.0% gain — both models detected 6/10)**
- **FP5:** **+0 rounds (0.0% gain — both models detected 7/10)**
FP4 and FP1 account for **83.3% of the gain**. In two of the five positions, Phase 17 offered zero improvement.

### Question 4: Does Phase 17 outperform Phase 14 consistently across the five positions?
**Audited Verdict: NO.**  
Phase 17 outperforms Phase 14 in only 3 positions (FP1, FP3, FP4). In FP2 (open multi-way intersection) and FP5 (broad arterial corridor), Phase 14 and Phase 17 achieved identical recall ($60.0\%$ in FP2, $70.0\%$ in FP5). There is no uniform superiority across urban geometries.

### Question 5: Does the conclusion change when one position is excluded?
**Audited Verdict: YES (Radically).**  
Under Leave-One-Position-Out (LOPO) testing:
- **Excluding FP4:** Round gain drops from +6 to +3. The exact McNemar $p$-value jumps from **$0.03125$ to $0.25000$** ($8\times$ higher), completely destroying statistical significance.
- **Excluding FP1:** Round gain drops to +4. The $p$-value jumps to **$0.12500$** ($4\times$ higher), again losing significance.
- **Excluding FP3:** The $p$-value becomes **$0.06250$**, exceeding the $0.05$ threshold.
In 3 out of 5 position exclusions, statistical significance is lost.

### Question 6: What is the valid negative-background exposure?
**Audited Verdict: 140.4 seconds (~2.34 minutes).**  
The total recording duration of Category A is 200.0 seconds. However:
- Active gunshot pulses and official matching intervals occupy **$59.584\text{ seconds}$**.
- Detector refractory cooldown windows occupy **$63.584\text{ seconds}$**.
An acoustic detector cannot generate a false alarm during a genuine gunshot or during its refractory suppression period. Subtracting event-associated audio leaves only **$140.416\text{ seconds}$ of eligible quiescent background exposure** (nominal rounded baseline: $140.0\text{ seconds}$). Treating 200.0 seconds as negative exposure is a methodological error.

### Question 7: What is the corrected Poisson upper false-alert bound?
**Audited Verdict: 77.03 alerts per hour.**  
Using the nominal 140.0-second quiescent background duration ($0.03889\text{ hours}$), the exact one-sided 95% Garwood Poisson upper confidence bound for zero observed false alerts is:
$$\lambda_{\text{upper}} = \frac{-\ln(0.05)}{140 / 3600} = \frac{2.99573}{0.03889} = \mathbf{77.033\text{ alerts/hour}}$$
(Using the exact matching window of 140.416s yields $76.805\text{ alerts/hour}$). Observing zero false alerts over 140 seconds only bounds the false-alarm rate to **less than 77 alerts per hour** (one false alarm every 47 seconds).

### Question 8: Which Category D recall value is correct?
**Audited Verdict: Both Are Authentic, but Refer to Different Sets and Profiles.**  
- **$83.33\%$ ($35 / 42$)** is the canonical event recall of **Phase 14 Balanced** on the comprehensive 42-clip Mitchell 2015 range set.
- **$89.29\% \approx 89.3\%$ ($25 / 28$)** is the event recall of **Phase 14 High-Sensitivity** on the 28-event blind discrete test set.
Phase 20's cross-category table erroneously cited the High-Sensitivity figure ($89.3\%$) for Phase 14 Balanced. On that same 28-event set, Phase 14 Balanced achieved **$75.00\%$ ($21 / 28$)**. The canonical Category D recall for Phase 14 Balanced is certified as **$83.33\%$ ($35/42$)**.

### Question 9: Does the evidence justify changing the default detector?
**Audited Verdict: NO. Phase 14 Balanced Remains the Default Baseline.**  
Promotion of Phase 17 Experimental is rejected:
1. The event-level $p = 0.03125$ is statistically fragile and fails at the incident level ($p = 0.25$) and under Holm correction ($p_{\text{Holm}} = 0.125$).
2. The gain is localized to FP4 (+3) and FP1 (+2), with zero gain in FP2 and FP5.
3. Phase 17 was designed for rural animal suppression; its false-alarm rejection over hundreds of hours of complex urban non-gunfire noise remains unproven.
4. Phase 14 Balanced has proven stability ($0.99\text{ alerts/hour}$ over $6.08\text{ hours}$ in Phase 16).

### Question 10: What additional independent campaigns would be required for stronger generalization claims?
**Audited Verdict: Multi-City, Multi-Season Field Trials.**  
To establish genuine population-level generalization, future research must evaluate:
- **Multiple Municipal Campaigns:** Testing in at least 3 distinct metropolitan areas with varying topographies (e.g., desert grid cities, high-rise glass canyons, coastal humid climates).
- **Seasonal & Environmental Diversity:** Multi-day recordings covering summer thermal gradients, rain, high wind, and heavy traffic.
- **Diverse Weapon & Standoff Conditions:** Moving drive-by shooters, rifles, concealed weapons, and varying sensor-to-source distances ($50\text{ m}$ to $500\text{ m}$).
- **Continuous Negative Validation:** A minimum of $100\text{ hours}$ of unbroken continuous urban audio to bound false alarm rates to $< 0.03\text{ alerts/hour}$.

---

## 2. Epistemological Classification of Evidence

To prevent overstating experimental findings, all Phase 21 results are formally classified:

```
┌────────────────────────────────────────────────────────────────────────┐
│ LEVEL 1: ESTABLISHED EMPIRICAL OBSERVATIONS                            │
│ - Phase 14 Balanced detected 27 of 50 physical rounds (54.00%).        │
│ - Phase 17 Experimental detected 33 of 50 physical rounds (66.00%).    │
│ - Phase 17 detected 6 additional rounds; Phase 14 detected 0 missed.   │
│ - Category A recordings belong to ONE controlled municipal campaign.   │
│ - In 15 of 20 recordings, both models had identical round detections.  │
│ - FP4 accounts for 3 of the 6 gained rounds; FP2 and FP5 had 0 gain.   │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ LEVEL 2: UNADJUSTED STATISTICAL EVIDENCE                               │
│ - Unadjusted event-level McNemar test: p = 0.03125 (< 0.05).          │
│ - Valid ONLY under the assumption of independent, unclustered trials.  │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ LEVEL 3: CLUSTER-AWARE INFERENTIAL EVIDENCE                            │
│ - Incident-level exact binomial test (N=20): p = 0.25000 (Not Sig).   │
│ - Recording-level Wilcoxon signed-rank test: p = 0.06250 (Not Sig).    │
│ - LOPO excluding FP4 McNemar test: p = 0.25000 (Not Sig).             │
│ - Holm-Bonferroni adjusted McNemar test: p = 0.12500 (Not Sig).        │
│ - Category A Poisson 95% upper bound: 77.03 alerts/hour.               │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ LEVEL 4: UNPROVEN GENERALIZATION CLAIMS (FORBIDDEN IN PRODUCTION)      │
│ - "Phase 17 proves reliable generalization across urban environments." │
│ - "The detector is immune to false alarms in the field (100% prec)."  │
│ - "Phase 17 outperforms Phase 14 across different cities or seasons." │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 3. Comprehensive Model Comparison Matrix

The table below summarizes paired evaluations of all frozen models against **Phase 14 Balanced** across the 50 Category A events, incorporating unadjusted and Holm-Bonferroni adjusted $p$-values:

| Comparison Model | Both Det ($a$) | P14 Only ($b$) | Comp Only ($c$) | Neither ($d$) | Discordant ($b+c$) | Raw McNemar $p$ | Holm-Adjusted $p$ | Significant ($\alpha=0.05$) | Absolute Diff | Newcombe 95% CI | Recording Wilcoxon $p$ | Position Gain Range |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Phase 13 Balanced** | 13 | 14 | 3 | 20 | 17 | **0.01273** | **0.06363** | NO | $-22.00\%$ | $[-36.4\%, -7.6\%]$ | $0.00781$ | $[-5\text{ to }0]$ |
| **Phase 17 Experimental** | 27 | 0 | 6 | 17 | 6 | **0.03125** | **0.12500** | NO | $+12.00\%$ | $[+2.4\%, +21.6\%]$ | $0.06250$ | $[0\text{ to }+3]$ |
| **Phase 14 High-Sensitivity** | 22 | 5 | 0 | 23 | 5 | **0.06250** | **0.18750** | NO | $-10.00\%$ | $[-18.8\%, -1.2\%]$ | $0.06250$ | $[-3\text{ to }0]$ |
| **Phase 14 High-Precision** | 22 | 5 | 2 | 21 | 7 | **0.45312** | **0.90625** | NO | $-6.00\%$ | $[-16.7\%, +4.7\%]$ | $0.37500$ | $[-2\text{ to }+1]$ |
| **Phase 9 Balanced** | 25 | 2 | 3 | 20 | 5 | **1.00000** | **1.00000** | NO | $+2.00\%$ | $[-6.4\%, +10.4\%]$ | $1.00000$ | $[-1\text{ to }+1]$ |

**Statistical Insight:** Under Holm-Bonferroni correction, **no candidate detector shows a statistically significant difference from Phase 14 Balanced at $\alpha = 0.05$**.

---

## 4. Master Deliverables Directory

All Phase 21 artifacts have been generated, cryptographically signed, and archived:

| Artifact Path | Format | Content & Forensic Purpose |
| :--- | :--- | :--- |
| [phase21_baseline_freeze.json](file:///e:/gunshot/gunshot/reports/phase21_baseline_freeze.json) | JSON | Cryptographic verification of models and historical archives. |
| [phase21_event_cluster_hierarchy.csv](file:///e:/gunshot/gunshot/reports/phase21_event_cluster_hierarchy.csv) | CSV | 7-level nesting hierarchy mapping all 50 physical rounds. |
| [phase21_event_level_reproduction.csv](file:///e:/gunshot/gunshot/reports/phase21_event_level_reproduction.csv) | CSV | Canonical 50-round event-level predictions and pairing states. |
| [phase21_event_contingency.json](file:///e:/gunshot/gunshot/reports/phase21_event_contingency.json) | JSON | Exact $2\times 2$ event contingency table and unadjusted McNemar test. |
| [phase21_event_level_statistics.md](file:///e:/gunshot/gunshot/reports/phase21_event_level_statistics.md) | Markdown | Unadjusted event-level statistics and discordant pair audit. |
| [phase21_recording_level_results.csv](file:///e:/gunshot/gunshot/reports/phase21_recording_level_results.csv) | CSV | Stream-by-stream performance, recall differences, and incident status. |
| [phase21_recording_level_comparison.md](file:///e:/gunshot/gunshot/reports/phase21_recording_level_comparison.md) | Markdown | Recording-level paired comparison and incident-level audit ($p=0.25$). |
| [phase21_position_level_results.csv](file:///e:/gunshot/gunshot/reports/phase21_position_level_results.csv) | CSV | Firing position breakdown (FP1–FP5) showing gain concentration. |
| [phase21_burst_analysis.csv](file:///e:/gunshot/gunshot/reports/phase21_burst_analysis.csv) | CSV | Audit of 15 bursts and 5 single shots against refractory cooldown. |
| [phase21_clustered_statistics.md](file:///e:/gunshot/gunshot/reports/phase21_clustered_statistics.md) | Markdown | Clustered inferential audit, LOPO analysis, and bootstrap evaluation. |
| [phase21_cluster_bootstrap_results.json](file:///e:/gunshot/gunshot/reports/phase21_cluster_bootstrap_results.json) | JSON | 10,000-iteration cluster bootstrap results across streams and positions. |
| [phase21_leave_one_position_out.csv](file:///e:/gunshot/gunshot/reports/phase21_leave_one_position_out.csv) | CSV | LOPO sensitivity metrics demonstrating significance collapse. |
| [phase21_negative_exposure_timeline.csv](file:///e:/gunshot/gunshot/reports/phase21_negative_exposure_timeline.csv) | CSV | Second-by-second exposure timeline across all 20 recordings. |
| [phase21_false_alert_statistics.json](file:///e:/gunshot/gunshot/reports/phase21_false_alert_statistics.json) | JSON | Poisson upper bounds across 4 exposure definitions. |
| [phase21_false_alert_exposure_correction.md](file:///e:/gunshot/gunshot/reports/phase21_false_alert_exposure_correction.md) | Markdown | Methodological audit proving Category A cannot assess false alarms. |
| [phase21_category_d_reconciliation.md](file:///e:/gunshot/gunshot/reports/phase21_category_d_reconciliation.md) | Markdown | Resolution of the $83.33\%$ vs. $89.3\%$ Category D discrepancy. |
| [phase21_category_d_corrected_metrics.json](file:///e:/gunshot/gunshot/reports/phase21_category_d_corrected_metrics.json) | JSON | Structured data and audit trail for Category D reconciliation. |
| [phase21_all_model_comparisons.csv](file:///e:/gunshot/gunshot/reports/phase21_all_model_comparisons.csv) | CSV | Model comparisons with Newcombe CIs and Holm adjustments. |
| [phase21_test_results.txt](file:///e:/gunshot/gunshot/reports/phase21_test_results.txt) | Text | Full pytest execution log (12/12 passed). |
| [test_phase21_cluster_aware_audit.py](file:///e:/gunshot/gunshot/tests/test_phase21_cluster_aware_audit.py) | Python | Automated pytest test suite covering all Phase 21 requirements. |
| [reproduce_phase21_cluster_aware_analysis.py](file:///e:/gunshot/gunshot/scripts/reproduce_phase21_cluster_aware_analysis.py) | Python | 12-step end-to-end automated reproduction harness. |

---

## 5. Architectural Baseline Integrity

The release package is sealed:
- **Default Production Baseline:** `Phase 14 Balanced` (`model_phase14.py`)
- **Selectable Experimental Profile:** `Phase 17 Experimental` (`model_phase17.py`)
- **Historical Comparators:** `model_phase13.py`, `model_phase9.py`

---
*Report certified by Principal Acoustic ML Research Engineer, Audio DSP Specialist, Dataset Provenance Auditor and Real-Time Systems Engineer.*

