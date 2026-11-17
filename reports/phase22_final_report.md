# Master Research Report — Phase 22
## Prospective Independent Validation Protocol, Burst-Cooldown Forensics & Generalization Study Design

**Document ID:** `REPORT-PHASE22-FINAL-001`  
**Phase:** 22 (Validation Architecture & Generalization Protocol)  
**Date:** November 2026  
**Status:** COMPLETED & AUDITED  

---

### MANDATORY SAFETY DESIGNATION
> [!CAUTION]
> **RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.**  
> This experimental acoustic machine-learning system is uncertified and must never be deployed for autonomous emergency dispatch, tactical police response, active-shooter alerting, automated lockdown/evacuation, or life-critical physical security. Use legally obtained recordings and safe audio playback only. Live-fire testing and hazardous acoustic experiments are strictly prohibited.

---

## 1. Executive Summary & Phase 22 Scope

Phase 21 conducted a retrospective cluster-aware statistical audit of the Pittsburgh controlled live-fire validation dataset (ShotSpotter PA DQV 2018, Category A). The primary conclusion was that while `model_phase17.py` detected 33 out of 50 annotated rounds compared with `model_phase14.py` Balanced's 27 out of 50, this six-round margin was concentrated in rapid bursts across just three firing positions (FP1, FP3, FP4). At the recording level, the difference was statistically non-significant ($p = 0.250$ McNemar, $p = 0.0625$ Wilcoxon), and after applying Holm-Bonferroni adjustment across candidate comparisons, no model difference remained statistically significant. Furthermore, Category A provided only 140.416 seconds of eligible negative-background exposure, leaving operational false-alert performance uncharacterized.

In strict compliance with the Phase 22 charter, **no detector architecture was modified, retrained, or threshold-tuned**. Instead, Phase 22 achieved the following mission objectives:
1. **Cryptographic Baseline Freeze:** Verified and locked SHA-256 hashes for all production and historical baselines (`model_phase14.py`, `model_phase17.py`, `model_phase13.py`, `model_phase9.py`, `gunshot_detection_phase20.zip`, `gunshot_detection_phase21.zip`).
2. **Empirical Burst-Cooldown Forensic Audit:** Classified all 50 physical rounds in Category A into five mutually exclusive forensic categories independently for Phase 14 and Phase 17 using exact event timestamps, detector alert intervals, state transitions, and refractory dead times.
3. **Preregistered Independent Validation Protocol:** Designed a rigorous prospective multi-campaign validation study targeting a minimum of three distinct metropolitan environments, diverse acoustic geometries, and standoff conditions ($50\text{ m}$ to $400\text{ m}$).
4. **Hierarchical Statistical Analysis Plan (SAP):** Formulated a 7-level evaluation hierarchy (Campaign $\to$ Position $\to$ Session $\to$ Stream $\to$ Burst $\to$ Physical Round $\to$ Detector Alert) with paired non-parametric tests, Newcombe score confidence intervals, and Holm-Bonferroni controls.
5. **Continuous Negative-Audio Protocol:** Formulated a 100-hour continuous negative validation protocol establishing mathematical definitions for eligible exposure, refractory cooldown exclusion, deduplication, and exact Poisson confidence limits.
6. **Predefined Model Promotion Criteria:** Formalized an explicit decision framework (`PROMOTE`, `RETAIN DEFAULT`, `INCONCLUSIVE`) governing any future baseline elevation.
7. **Dataset Acquisition & Governance Plan:** Created a compliant, research-licensed data acquisition framework and JSON-Schema Draft 2020-12 provenance schema with zero live-fire requirements.

---

## 2. Baseline Freeze Verification

Prior to conducting forensic or statistical analyses, all codebase models and historical release archives were verified against their recorded cryptographic hashes:

| Component | File Path | Role in Phase 22 | Expected SHA-256 Checksum | Verified Size | Audit Status |
|---|---|---|---|---|---|
| **Phase 14 Default** | `model_phase14.py` | Default Production Baseline | `a268551604ae8b73068435ff10ab3d265065f56e0679757fca5b6bf0f061c065` | 23,340 B | **MATCH / FROZEN** |
| **Phase 17 Profile** | `model_phase17.py` | Selectable Experimental Profile | `e2b262b866fdd5d7f1a4ab91a7b8b9bac189ee8cc7a78603b3544ca1579fb819` | 29,067 B | **MATCH / FROZEN** |
| **Phase 13 Baseline** | `model_phase13.py` | Frozen Historical Comparator | `68585039a4a4fdb7978a99f5e2a72c0ad5a9523127ec24a1338fbedd1c1231e6` | 22,252 B | **MATCH / FROZEN** |
| **Phase 9 Baseline** | `model_phase9.py` | Frozen Historical Comparator | `85cedd9f5b988ecafb1eae7de9630ee3d6a387ded6ef732e0efb7c3b496f132a` | 17,719 B | **MATCH / FROZEN** |
| **Phase 20 Archive** | `gunshot_detection_phase20.zip` | Historical Release Archive | `dda7427f2dbffcb178f6d9ade0abb80fbfc491751f04de5dc0db1b4731c31c89` | 8,205,938 B | **MATCH / VERIFIED** |
| **Phase 21 Archive** | `gunshot_detection_phase21.zip` | Historical Release Archive | `b065747b0e6118d228336bee7f8c3811890b638a25070d3ce2a047c329b3e225` | 8,211,219 B | **MATCH / VERIFIED** |
| **Canonical Events** | `reports/phase20_canonical_event_manifest.csv` | Canonical Ground Truth | `6c3e5d5c07cb51020dd75d69785501ea9ad161994e43f5509787ffc9339e14ee` | 16,427 B | **MATCH / VERIFIED** |

*Artifact output:* [`reports/phase22_baseline_freeze.json`](file:///e:/gunshot/gunshot/reports/phase22_baseline_freeze.json).

---

## 3. Empirical Burst and Refractory-Cooldown Forensic Audit

### 3.1 Forensic Methodology & Classification Categories
In Phase 21, it was noted that 14 of 15 three-round bursts in Category A occurred within a 2.0-second interval, leading to the hypothesis that refractory cooldown suppression was primarily responsible for missed rounds. Phase 22 evaluated this hypothesis by executing exact state-machine tracking across all 20 Category A streams.

Every physical round ($N=50$) was independently evaluated for Phase 14 Balanced and Phase 17 Experimental and classified into five mutually exclusive categories:
1. `DETECTED_WITH_INDEPENDENT_ALERT`: The round falls within an alert window that was matched 1-to-1 to this round.
2. `DETECTED_BUT_MERGED_INTO_EARLIER_ALERT`: The round occurred during an active multi-window alert triggered by an earlier round, but was uncredited due to 1-to-1 event matching rules.
3. `MISSED_WHILE_IN_REFRACTORY_COOLDOWN`: The detector was in a refractory cooldown dead time ($\tau_{\text{cooldown}} = 2.0\text{ s}$) following an alert, directly suppressing new alert generation.
4. `MISSED_WHILE_ELIGIBLE`: The detector was fully eligible (not in cooldown, no active alert), but its internal prediction score remained below the alert threshold ($\text{score} < \theta$).
5. `AMBIGUOUS_DUE_TO_INSUFFICIENT_PRECISION`: Event or alert timestamps could not be established with sub-window accuracy.

### 3.2 Audit Findings & Forensic Breakdown

| Forensic Classification Category | Phase 14 Balanced ($N=50$) | Phase 17 Experimental ($N=50$) | Difference ($\Delta_{\text{P17 - P14}}$) |
|---|---|---|---|
| **1. Detected with Independent Alert** | **27 (54.0%)** | **33 (66.0%)** | **+6 rounds (+12.0%)** |
| **2. Detected but Merged into Active Alert** | **5 (10.0%)** | **6 (12.0%)** | **+1 round (+2.0%)** |
| **3. Missed while in Refractory Cooldown** | **2 (4.0%)** | **3 (6.0%)** | **+1 round (+2.0%)** |
| **4. Missed while Eligible** | **16 (32.0%)** | **8 (16.0%)** | **-8 rounds (-16.0%)** |
| **5. Ambiguous due to Insufficient Precision** | **0 (0.0%)** | **0 (0.0%)** | **0 rounds (0.0%)** |
| **TOTAL** | **50 (100.0%)** | **50 (100.0%)** | **-** |

### 3.3 Critical Forensic Insights
1. **Refractory Cooldown is NOT the Dominant Cause of Misses:**
   - For Phase 14 Balanced, refractory cooldown dead time accounted for **only 2 out of 23 missed rounds (8.7%)**. Specifically, Round 3 in `test_007` (burst span 0.44s) and Round 3 in `test_055` (burst span 0.48s) were suppressed by cooldown.
   - For Phase 17 Experimental, cooldown accounted for **3 out of 17 misses (17.6%)**.
2. **Alert Merging Hides Detection Energy:**
   - 5 rounds for Phase 14 (10.0%) and 6 rounds for Phase 17 (12.0%) generated elevated acoustic energy that kept the detector's state machine active, but because the alert began on Round 1, subsequent rounds were merged into the existing alert window and marked as misses under strict 1-to-1 matching.
3. **The Real Source of Phase 17's Gain is Eligible Miss Recovery:**
   - Phase 14 suffered **16 eligible misses (32.0%)**, whereas Phase 17 suffered only **8 eligible misses (16.0%)**.
   - Phase 17's gain of 6 detected rounds stems entirely from recovering 8 eligible rounds that Phase 14 missed due to low SNR (e.g., Round 1 in `test_013`, `test_015`, `test_017`, `test_047`, and `test_111`), offset by slight differences in alert boundary matching.
   - In severely attenuated streams (`test_049` and `test_127`), both detectors failed all rounds because peak acoustic scores ($< 0.45$) never exceeded threshold while eligible.

*Detailed Reports:* [`reports/phase22_burst_cooldown_forensics.csv`](file:///e:/gunshot/gunshot/reports/phase22_burst_cooldown_forensics.csv), [`reports/phase22_alert_event_timeline.csv`](file:///e:/gunshot/gunshot/reports/phase22_alert_event_timeline.csv), [`reports/phase22_burst_cooldown_analysis.md`](file:///e:/gunshot/gunshot/reports/phase22_burst_cooldown_analysis.md).

---

## 4. Preregistered Independent Validation Study Design

To overcome the single-city, single-campaign limitation of the Pittsburgh dataset, Phase 22 preregisters a formal multi-campaign study design:

### 4.1 Target Campaign Architecture
- **Minimum 3 Geographically Disjoint Campaigns:** Validation must incorporate at least three distinct metropolitan jurisdictions separated by $>50\text{ km}$ to capture varying architectural geometries, asphalt acoustic reflectivity, and local ambient noise.
- **Sensor Hardware Diversity:** Testing across electret, MEMS, and dynamic microphone arrays mounted at realistic heights ($3\text{ to }9\text{ meters}$).
- **Standoff Distance Stratification:** Mandatory evaluation across four distance bins:
  - Near Field: $0\text{ m} \le d < 100\text{ m}$
  - Mid Field: $100\text{ m} \le d < 200\text{ m}$
  - Far Field: $200\text{ m} \le d < 300\text{ m}$
  - Extended Standoff: $300\text{ m} \le d \le 450\text{ m}$

### 4.2 7-Level Evaluation Hierarchy
Statistical independence is enforced strictly by defining unit levels and nesting:
$$\text{Campaign} \longrightarrow \text{Position} \longrightarrow \text{Session} \longrightarrow \text{Sensor Stream} \longrightarrow \text{Burst} \longrightarrow \text{Physical Round} \longrightarrow \text{Detector Alert}$$

- **Primary Units of Independent Inference:** Campaign (macro-generalization) and Recording Stream (micro-generalization).
- **Nested Observations:** Multiple rounds within a burst are treated as dependent repeated measures, precluding naive unadjusted pooled $Z$-tests or raw McNemar interpretation without cluster adjustment.

*Full Protocol:* [`reports/phase22_independent_validation_protocol.md`](file:///e:/gunshot/gunshot/reports/phase22_independent_validation_protocol.md), [`reports/phase22_preregistered_analysis_plan.md`](file:///e:/gunshot/gunshot/reports/phase22_preregistered_analysis_plan.md).

---

## 5. Continuous Negative-Audio Validation Protocol (100-Hour Benchmark)

### 5.1 Protocol Standards
- **Exposure Target:** Minimum 100 hours of continuous, unbroken urban background audio with zero synthetic clip splicing.
- **Eligible Exposure Accounting:** Cooldown dead time ($\sum \tau_{\text{cooldown}}$) and ambiguous excluded intervals ($T_{\text{excluded}}$) are subtracted from gross audio time:
  $$T_{\text{eligible}} = T_{\text{gross}} - \sum_{k=1}^K \min(\tau_{\text{cooldown}}, T_{\text{remaining}, k}) - T_{\text{excluded}}$$
- **Poisson Uncertainty:** At 100 hours with $k=0$ alerts, the exact one-sided 95% Poisson upper bound is $\lambda_{\text{upper}} = 0.02996 \approx 0.030\text{ alerts/hour}$ ($\text{MTBFA} \ge 33.38\text{ hours}$).
- **Overdispersion Testing:** Standard Fisher's dispersion test ($D \sim \chi^2_{M-1}$) across 1-hour blocks to detect environmental distractor clustering.

*Full Protocol:* [`reports/phase22_negative_audio_protocol.md`](file:///e:/gunshot/gunshot/reports/phase22_negative_audio_protocol.md).

---

## 6. Predefined Model Promotion Framework

A strict three-state decision framework (`PROMOTE`, `RETAIN DEFAULT`, `INCONCLUSIVE`) prevents premature promotion:
- **`PROMOTE` Requirements:** Requires simultaneous satisfaction of all gate checks, superior performance in $\ge 2$ of $\ge 3$ independent campaigns, recording-level Wilcoxon $p < 0.05$, positive Newcombe score confidence bounds after Holm-Bonferroni correction, and continuous negative FAR degradation $\le 0.20\text{ alerts/hour}$.
- **`RETAIN DEFAULT` Trigger:** Any significant regression in an independent campaign, FAR increase $> 0.50\text{ alerts/hour}$, or latency stall immediately rejects the candidate.
- **`INCONCLUSIVE` Default:** Any underpowered or mixed result retains `model_phase14.py` Balanced as default baseline.

*Full Specification:* [`reports/phase22_model_promotion_criteria.md`](file:///e:/gunshot/gunshot/reports/phase22_model_promotion_criteria.md).

---

## 7. Evidence Audit: Separation of Knowns, Unknowns, and Future Plans

To preserve complete scientific integrity, the project's body of evidence is partitioned into five distinct categories:

### 7.1 What Was Reproduced from Existing Evidence
1. **Model Checksums and Freezes:** Verified SHA-256 integrity for `model_phase14.py`, `model_phase17.py`, `model_phase13.py`, and `model_phase9.py`.
2. **Category A Detections:** Reproduced Phase 14 Balanced 27/50 (54.0%) and Phase 17 Experimental 33/50 (66.0%) round detections.
3. **Phase 21 Statistical Audit:** Re-confirmed recording-level McNemar $p = 0.250$ and Wilcoxon $p = 0.0625$, confirming non-significance at the recording level.
4. **Category A Background Exposure:** Verified that Category A contains exactly 140.416 seconds of non-event audio.

### 7.2 What Was Newly Calculated in Phase 22
1. **Window-Level State Tracking:** Mapped the continuous internal state machine (window start, end, peak time, score, and refractory cooldown intervals) across all 20 Category A streams.
2. **Forensic Category Allocation:** Proved that refractory cooldown dead time caused only 2 misses for Phase 14 and 3 for Phase 17, while alert merging accounted for 5 and 6 rounds, and eligible signal failure accounted for 16 and 8 rounds, respectively.
3. **Eligible Negative Exposure Formulation:** Formulated exact mathematical equations separating gross stream time from eligible detector exposure.
4. **Exact Poisson Garwood Bounds:** Quantified the mathematical limits of a 100-hour negative test ($\lambda_{\text{upper}} \approx 0.030\text{ alerts/hour}$).

### 7.3 What Could Not Be Calculated Due to Missing Source Data
1. **True Cross-Campaign Generalization:** Historical data includes only one municipal controlled validation campaign (Pittsburgh 2018) with multi-round events. Cross-city generalization cannot be computed.
2. **Operational Sensor Network FAR:** Available negative continuous audio spans only 6.08 hours; long-term seasonal and geographic false-alert rates cannot be calculated from existing files.
3. **Microphone Array Elevation & Vectoring:** Sensor azimuth, exact elevation, and multi-sensor phase coherence are absent from the open Pittsburgh repository metadata, preventing array beamforming analysis.

### 7.4 What Is a Proposed Future-Study Design
1. **Prospective 3-Campaign Protocol:** Preregistered requirements for acquiring and evaluating $\ge 3$ independent metropolitan datasets.
2. **100-Hour Continuous Stream Benchmark:** Detailed design for sourcing, vetting, and evaluating unbroken continuous urban background audio.
3. **7-Level Hierarchical Statistical Plan:** Preregistered non-parametric tests and Holm-Bonferroni correction rules.
4. **Predefined Promotion Criteria:** Formal gate checks and quantitative decision matrix for candidate elevation.

### 7.5 What Remains Unproven
1. Whether `model_phase17.py` maintains any advantage over `model_phase14.py` in unseen urban canyons.
2. Whether the experimental multi-stage suppression in Phase 17 degrades detection of muffled or distant small-caliber gunfire ($< 100\text{ m}$).
3. Whether false-alert rates remain acceptable under extreme weather conditions (high wind, torrential rain, thunderstorm fronts).

---

## 8. What the Current Evidence Does NOT Establish

> [!IMPORTANT]
> The current scientific and experimental evidence does **NOT** establish:
> 1. **Generalization to Arbitrary Cities or Recording Environments:** Performance on 20 recordings from Pittsburgh, PA cannot predict performance in other metropolitan centers with differing topography, street canyon widths, building cladding materials, or ambient soundscapes.
> 2. **Reliable Detection of Unexpected Criminal Gunfire:** The evaluated data consists entirely of pre-arranged, controlled live-fire tests conducted by law enforcement technicians under stationary conditions. It does not establish detection reliability for moving vehicles, concealed firearms, drive-by shootings, or indoor-to-outdoor discharges.
> 3. **A Dependable Operational False-Alarm Rate:** Testing on 6.08 hours of negative audio and 140.4 seconds of inter-round silence provides zero statistical confidence regarding real-world false-alarm frequencies over weeks or months of 24/7 deployment.
> 4. **Suitability for Public-Safety or Emergency-Response Use:** The prototype lacks hardware redundancy, tamper detection, failure fail-safes, real-time dispatch integration, and physical environmental hardening. It is not compliant with any public safety standard.
> 5. **Superiority of Phase 17 Over Phase 14 Across Independent Campaigns:** The 6-round detection difference observed in Phase 20 is not statistically significant at the recording level ($p = 0.250$), is statistically non-significant under Holm-Bonferroni multiple testing correction, and has never been demonstrated on any second independent dataset.

---

## 9. Baseline Status and Explicit Research Recommendations

- **Baseline Status:** `model_phase14.py` (Balanced Profile) is **AFFIRMED AND RETAINED** as the Default Production Baseline.
- **Experimental Status:** `model_phase17.py` remains a selectable experimental research profile.
- **Next Research Milestone (Phase 23):** Execute dataset acquisition under the Phase 22 governance plan, targeting the first 50 hours of continuous urban negative audio from verified open municipal repositories and conducting ingestion integrity gate checks.

---

*Authored by Principal Acoustic ML Research Engineer, Audio DSP Specialist & Dataset Auditor.*  
*Antigravity Gunshot Detection Research Consortium — Phase 22.*

