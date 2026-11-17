# PHASE 25 MASTER TECHNICAL REPORT: CROSS-PHASE EVIDENCE RECONCILIATION, INDEPENDENT ACQUISITION AUDIT & EXPOSURE BENCHMARK

> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.**  
> *This experimental acoustic machine-learning software is uncertified, unvalidated for tactical operations, and must never be deployed or relied upon for autonomous emergency dispatch, police tactical response, active-shooter alerting, automated evacuation, building lockdown, or life-critical physical security. Use legally obtained recordings and safe audio playback only. Live-fire testing and hazardous acoustic experiments are strictly prohibited.*

---

## 1. Executive Summary & Mission Scope

Phase 25 executed two mandatory workstreams for the acoustic gunshot detection research project (`E:/gunshot`):
1. **Workstream A — Forensic Reconciliation:** Systematically audited and resolved discrepancies between Phases 23 and 24, accounted for the complete 23-recording catalog, re-evaluated the double-reviewer manual audit statistics and Cohen's kappa, and audited municipal legal and open data claims.
2. **Workstream B — Independent Acquisition Audit:** Evaluated open research soundscape archives and municipal data portals, developed a formal research collaboration access pathway, and conducted rigorous exposure accounting separating historical from new exposure.

All detection models remained cryptographically frozen under strict governance:
- **Phase 14 Balanced (`model_phase14.py`):** **DEFAULT_RESEARCH_BASELINE**
- **Phase 17 Experimental (`model_phase17.py`):** **SELECTABLE_EXPERIMENTAL_PROFILE**
- **Phase 13 & Phase 9:** Frozen Historical Comparators
- **Release Archives Verified:** Phases 20, 21, 22, 23, and 24.

---

## 2. Workstream A — Forensic Evidence Reconciliation

### 2.1 Resolution of the Stream-Count Discrepancy
- **The Discrepancy:** Phase 23 narrative text claimed that Phase 17 produced fewer alerts in *4 streams* and identical counts in *13 streams*. Conversely, Phase 24 reported that Phase 17 improved in only *3 streams* and was identical in *14 streams*.
- **Forensic Finding:** Independent inspection of the underlying data files (`phase23_exposure_accounting.csv` and `phase24_exposure_accounting.csv`) confirms that the raw data is **100% bitwise identical**. In both phases, exactly 3 streams showed alert reductions:
  - `STR-05` (Arterial traffic): 20 vs 18 alerts ($-2$)
  - `STR-14` (Pedestrian walkway): 10 vs 8 alerts ($-2$)
  - `STR-16` (Covered arcade): 3 vs 2 alerts ($-1$)
  - Remaining 14 streams: exact equality ($0-0, 2-2, 1-1, 9-9, 2-2, 3-3, 5-5$).
- **Resolution:** The Phase 23 text was a **clerical / transcription typo** in the narrative table. The true empirical ground truth is **3 streams improved, 14 streams equal, and 0 streams worse**, fully corroborating the Wilcoxon permutation derivation with $N_r = 3$ ($p = (1/2)^3 = 0.125$).

### 2.2 Accounting of the Complete 23-Recording Inventory
The 23 cataloged recordings in [`reports/phase25_recording_inventory_reconciliation.csv`](file:///e:/gunshot/gunshot/reports/phase25_recording_inventory_reconciliation.csv) were individually audited:
- **`INCLUDED_PRIMARY_EVALUATION` (17 recordings, 6.6460 gross hours):** Verified natural unbroken field recordings from the UK Industrial, Chew Magna, and Bilbao campaigns.
- **`EXCLUDED_NOT_CONTINUOUS` (6 recordings, 6.0000 gross hours):** The Phase 7/8 synthetic overlay streams (`continuous_stream_01_urban_traffic_and_machinery_1hr.wav`, etc.). These are digital overlays of ESC-50 clips on synthetic silence, not genuine unbroken field audio, and have unverified negative status.
- **Zero Double-Counting:** Excluded recordings do not contribute to primary negative exposure metrics.

### 2.3 Double-Reviewer Manual Audit & Cohen's Kappa Reproducibility
- **The Finding:** In `phase24_alert_review_registry.csv`, both `reviewer1_classification` and `reviewer2_classification` contain identical post-adjudication labels: all 107 alerts are labeled `CONFIRMED_NON_TARGET`.
- **Statistical Evaluation:** When all ratings fall into a single category ($P_o = 1.0, P_e = 1.0$), Cohen's kappa is mathematically indeterminate ($\kappa = 0/0$).
- **Determination:** The previously reported $\kappa = 0.96$ and 105/107 initial agreement is **`UNVERIFIED_FROM_ARTIFACT`** because raw pre-adjudication discordant labels were not separately preserved in the stored file.
- **Mitigation:** Designed and formalized a mandatory dual-column pre-adjudication schema for all future manual reviews.

### 2.4 Audit of Municipal Open Data Legal Claims
- **The Claim:** Prior text asserted that municipal portals in Louisville and Chicago withhold raw acoustic audio under Federal Wiretap Act (18 U.S.C. § 2510) compliance and vendor contracts.
- **Evidentiary Separation:** Portal inspection confirms that Louisville and Chicago open data portals host tabular CSV/GIS dispatch logs and do not provide raw acoustic waveforms. However, portal documentation does not cite the Federal Wiretap Act as the specific administrative reason for non-publication.
- **Correction:** The project adopts the qualified factual statement: *"The inspected municipal portals provide tabular dispatch logs and geospatial coordinates, but do not provide downloadable raw acoustic recordings. The specific administrative, legal, or commercial reasons for non-publication were not definitively established by the available portal evidence."*

---

## 3. Workstream B — Independent Audio Acquisition & Candidate Evaluation

### 3.1 Candidate Repositories Evaluated
1. **`SRC-AEROSONIC-DB` (AeroSonicDB / Zenodo 7976269):** Evaluated as `CONDITIONAL`. Contains 6 one-hour continuous urban audio recordings in Adelaide, Australia. However, audio includes prominent aircraft flyovers requiring temporal masking before benchmark ingestion.
2. **`SRC-ISD-URBAN` (International Soundscape Database / ISO 12913):** Evaluated as `CONDITIONAL`. High-fidelity urban soundscapes across global cities, but recordings are distributed as 5-to-15 minute multichannel ambisonic files requiring downmixing and session continuity audits.
3. **`SRC-LOUISVILLE-OPEN` & `SRC-CHICAGO-OPEN`:** Evaluated as `REJECT`. Portals provide tabular GIS/CAD metadata only; zero raw audio exists.
4. **`SRC-SONYC-UST-V1` & `SRC-TAU-DCASE-2020`:** Evaluated as `REJECT`. Both datasets consist of 10-second segmented clips. Splicing discrete snippets is strictly prohibited by continuous validation protocols.
5. **Research Collaboration Pathway (`REQ-ACOUSTIC-DATA-P25`):** Formal bilateral data access request drafted in [`reports/phase25_research_data_access_request.md`](file:///e:/gunshot/gunshot/reports/phase25_research_data_access_request.md) for future academic sensor testbeds. Stored as draft pending user approval.

### 3.2 Formal Exposure Accounting

In strict compliance with scientific honesty and eligibility standards:

| Exposure Category | Gross Duration (Hours) | Eligible Exposure (Hours, P14) | Eligible Exposure (Hours, P17) | Observed Alerts (P14) | Observed Alerts (P17) |
|---|---:|---:|---:|---:|---:|
| **Previously Audited Phase 23/24 Exposure** | 6.6460 | 6.6149 | 6.6177 | 56 | 51 |
| **New Phase 25 Ingested Exposure** | 0.0000 | 0.0000 | 0.0000 | 0 | 0 |
| **Cumulative Benchmark Exposure** | **6.6460** | **6.6149** | **6.6177** | **56** | **51** |

- **Shortfall Against 20-Hour Expansion Target:** 20.0000 hours.
- **Cumulative Shortfall Against 50-Hour Milestone:** 43.3540 hours.
- The shortfall is transparently reported. Audio was not fabricated or looped.

---

## 4. Workstream C — Frozen-Model Evaluation & Tripartite Denominators

The matched performance across the 17 verified continuous streams under the Tripartite Denominator Framework:

```
==================================================================================================
METRIC                                   PHASE 14 BALANCED            PHASE 17 EXPERIMENTAL
==================================================================================================
Model Role                               DEFAULT_RESEARCH_BASELINE    SELECTABLE_EXPERIMENTAL
Gross Exposure Duration                  6.6460 hours (23,925.58 s)   6.6460 hours (23,925.58 s)
Refractory Cooldown Excluded Duration    111.92 seconds               101.92 seconds
Net Eligible Exposure Duration           6.6149 hours (23,813.66 s)   6.6177 hours (23,823.66 s)
Total Observed False Alerts              56                           51
Gross Alert Rate (FAR_gross)             8.4261 alerts/hour           7.6738 alerts/hour
Eligible Alert Rate (FAR_eligible)       8.4657 alerts/hour           7.7066 alerts/hour
Exact Garwood 95% Poisson CI             [6.3949, 10.9935]            [5.7381, 10.1328]
Empirical MTBFA                          7.09 minutes (0.1181 h)      7.79 minutes (0.1298 h)
--------------------------------------------------------------------------------------------------
Stream Comparison Breakdown              Reference                    3 Improved, 14 Equal, 0 Worse
Paired Wilcoxon Signed-Rank Test         Reference                    W = 10.0, p = 0.125 (p >= 0.05)
Model Promotion Determination            RETAIN AS BASELINE           INCONCLUSIVE (REJECT PROMOTION)
==================================================================================================
```

---

## 5. What Phase 25 Does NOT Establish

To maintain absolute scientific transparency, the project explicitly registers what Phase 25 **does NOT establish**:

1. **NO Reliable Detection of Unexpected Criminal Gunfire:** The continuous negative benchmark contains zero firearms discharges. Performance on unexpected criminal gunfire in complex urban acoustic environments remains unvalidated.
2. **NO Generalization to Arbitrary Cities:** The 17 evaluated continuous streams represent specific acoustic environments in the UK and Spain. The observed false-alert rates cannot be generalized to unobserved cities with differing traffic profiles or emergency sirens.
3. **NO Municipal-Scale Operational False-Alert Feasibility:** Generating 7.7 to 8.5 false alerts per hour (an alert every 7 to 8 minutes) would cause catastrophic alert fatigue and overwhelm 911 dispatch personnel.
4. **NO Public-Safety or Emergency-Response Suitability:** The software prototype lacks certification (UL, CE, NIJ) and must never be deployed for tactical dispatch, active-shooter alerting, or life-safety applications.
5. **NO Superiority of Phase 17 Over Phase 14 Across Independent Campaigns:** The 5-alert reduction observed in Phase 17 fails statistical significance ($p = 0.125$). Phase 17 cannot be claimed to outperform Phase 14 on general environmental negative audio.

---

## 6. Deliverable Inventory & Archival Manifest

All Phase 25 deliverables have been produced, validated, and placed under version control:
- Baseline Freeze: [`reports/phase25_baseline_freeze.json`](file:///e:/gunshot/gunshot/reports/phase25_baseline_freeze.json)
- Reconciliation Report: [`reports/phase25_phase23_phase24_reconciliation.md`](file:///e:/gunshot/gunshot/reports/phase25_phase23_phase24_reconciliation.md)
- Stream Reconciliation CSV: [`reports/phase25_stream_comparison_reconciliation.csv`](file:///e:/gunshot/gunshot/reports/phase25_stream_comparison_reconciliation.csv)
- Inventory Reconciliation CSV: [`reports/phase25_recording_inventory_reconciliation.csv`](file:///e:/gunshot/gunshot/reports/phase25_recording_inventory_reconciliation.csv)
- Reviewer Agreement Audit: [`reports/phase25_reviewer_agreement_audit.md`](file:///e:/gunshot/gunshot/reports/phase25_reviewer_agreement_audit.md)
- Reviewer Contingency Table: [`reports/phase25_reviewer_contingency_table.csv`](file:///e:/gunshot/gunshot/reports/phase25_reviewer_contingency_table.csv)
- Municipal Legal Audit: [`reports/phase25_municipal_legal_claim_audit.md`](file:///e:/gunshot/gunshot/reports/phase25_municipal_legal_claim_audit.md)
- Source Shortlist: [`reports/phase25_source_shortlist.md`](file:///e:/gunshot/gunshot/reports/phase25_source_shortlist.md)
- Source Registry: [`reports/phase25_source_registry.csv`](file:///e:/gunshot/gunshot/reports/phase25_source_registry.csv)
- Campaign Matrix: [`reports/phase25_campaign_independence_matrix.csv`](file:///e:/gunshot/gunshot/reports/phase25_campaign_independence_matrix.csv)
- Recording Provenance: [`reports/phase25_recording_provenance.csv`](file:///e:/gunshot/gunshot/reports/phase25_recording_provenance.csv)
- Duplicate Audit: [`reports/phase25_duplicate_audit.csv`](file:///e:/gunshot/gunshot/reports/phase25_duplicate_audit.csv)
- Continuity Audit: [`reports/phase25_continuity_audit.csv`](file:///e:/gunshot/gunshot/reports/phase25_continuity_audit.csv)
- Exposure Accounting: [`reports/phase25_exposure_accounting.csv`](file:///e:/gunshot/gunshot/reports/phase25_exposure_accounting.csv)
- Alert Event Log: [`reports/phase25_alert_event_log.csv`](file:///e:/gunshot/gunshot/reports/phase25_alert_event_log.csv)
- Negative Results Log: [`reports/phase25_negative_audio_results.csv`](file:///e:/gunshot/gunshot/reports/phase25_negative_audio_results.csv)
- Matched Model Comparison: [`reports/phase25_matched_model_comparison.md`](file:///e:/gunshot/gunshot/reports/phase25_matched_model_comparison.md)
- Statistical Analysis: [`reports/phase25_statistical_analysis.md`](file:///e:/gunshot/gunshot/reports/phase25_statistical_analysis.md)
- Risk & Limitation Register: [`reports/phase25_risk_and_limitation_register.md`](file:///e:/gunshot/gunshot/reports/phase25_risk_and_limitation_register.md)
- Processing Manifest: [`reports/phase25_processing_manifest.json`](file:///e:/gunshot/gunshot/reports/phase25_processing_manifest.json)
- Research Collaboration Request: [`reports/phase25_research_data_access_request.md`](file:///e:/gunshot/gunshot/reports/phase25_research_data_access_request.md)

---

## 7. Mandatory Safety Reiteration

**RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.**  
This research software implementation is strictly intended for scientific investigation of acoustic signal processing and deep neural network transient classification. It does not possess the reliability, fault tolerance, spatial discrimination, or certification required for operational security or life-safety applications.

