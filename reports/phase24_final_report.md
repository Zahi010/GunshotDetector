# PHASE 24 MASTER TECHNICAL REPORT: MULTI-CAMPAIGN NEGATIVE AUDIO VALIDATION, INDEPENDENT PROVENANCE AUDIT & TRIPARTITE DENOMINATOR RECONCILIATION

> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.**  
> *This acoustic machine-learning system is an experimental research demonstration prototype. It is uncertified, unvalidated for tactical operations, and must never be deployed or relied upon for autonomous emergency dispatch, police tactical response, active-shooter alerting, automated evacuation, building lockdown, or life-critical physical security. Use legally obtained recordings and safe audio playback only. Live-fire testing and hazardous acoustic experiments are strictly prohibited.*

---

## 1. Executive Summary & Mission Scope

Phase 24 establishes a rigorous, scientifically grounded expansion of the negative audio validation benchmark for the experimental acoustic gunshot detection research project (`E:/gunshot/gunshot`).

### 1.1 Core Mission Objectives
1. **Model Governance & Freeze:** Verify cryptographic SHA-256 integrity across all frozen baseline detectors (`model_phase14.py`, `model_phase17.py`, `model_phase13.py`, `model_phase9.py`). Strictly enforce the role of Phase 14 Balanced as the **default research baseline** and Phase 17 Experimental as the **selectable experimental profile**, completely deprecating commercial operational terminology ("production baseline").
2. **Municipal Open Data Investigation:** Exhaustively evaluate municipal open data portals (Louisville Metro Open Data, City of Chicago Open Data) and academic environmental sound corpora (SONYC-UST, TAU Urban Acoustic Scenes) to identify potential multi-hour continuous ambient feeds.
3. **Provenance, Campaign Independence & Continuity Audit:** Establish a multi-tier provenance hierarchy mapping every stream from Dataset $\to$ City $\to$ Campaign $\to$ Sensor Deployment $\to$ Position $\to$ Session $\to$ Recording, auditing all candidate audio for physical continuity, clipping, and duplicates.
4. **Tripartite Denominator Reconciliation:** Formulate and mathematically reconcile three distinct continuous alert rate metrics: Gross Monitored-Time Rate ($\text{FAR}_{\text{gross}}$), Cooldown-Adjusted Eligible Rate ($\text{FAR}_{\text{eligible}}$), and Common Matched-Exposure Comparison.
5. **Blinded Manual Alert Review Protocol:** Conduct an independent double-reviewer audit of all 107 observed alerts across 17 continuous streams, measuring inter-rater reliability and adjudicating distractor classes.
6. **Cross-Campaign Distractor & Statistical Analysis:** Execute rigorous non-parametric paired tests and exact Poisson Garwood uncertainty estimation to evaluate whether Phase 17 Experimental achieves statistically significant false-alarm reduction over Phase 14 Balanced.

---

## 2. Baseline Model Governance & Cryptographic Freeze

All detection architectures and decision boundaries were locked prior to evaluation. Hash verification confirmed zero bitwise divergence across all operational scripts:

| Detector Architecture | Source File | SHA-256 Checksum | File Size | Governance Role |
|---|---|---|---|---|
| **Phase 14 Balanced** | `model_phase14.py` | `a268551604ae8b73068435ff10ab3d265065f56e0679757fca5b6bf0f061c065` | 23,340 B | **DEFAULT_RESEARCH_BASELINE** |
| **Phase 17 Experimental** | `model_phase17.py` | `e2b262b866fdd5d7f1a4ab91a7b8b9bac189ee8cc7a78603b3544ca1579fb819` | 29,067 B | **SELECTABLE_EXPERIMENTAL_PROFILE** |
| **Phase 13 Comparator** | `model_phase13.py` | `68585039a4a4fdb7978a99f5e2a72c0ad5a9523127ec24a1338fbedd1c1231e6` | 22,252 B | Frozen Historical Comparator |
| **Phase 9 Comparator** | `model_phase9.py` | `85cedd9f5b988ecafb1eae7de9630ee3d6a387ded6ef732e0efb7c3b496f132a` | 17,719 B | Frozen Historical Comparator |

Furthermore, historical phase release archives were cryptographically re-verified, confirming absolute lineage continuity:
- `gunshot_detection_phase23.zip`: `5ce4e64715829d9b52111b6d6322f251976e1ce99e829d9dfbe0858a7e1644c8`
- `gunshot_detection_phase22.zip`: `160d327072c3515e945ca5cdf89038f14b6ef1919b1e4865278affab52ad4de5`
- `gunshot_detection_phase21.zip`: `b065747b0e6118d228336bee7f8c3811890b638a25070d3ce2a047c329b3e225`
- `gunshot_detection_phase20.zip`: `dda7427f2dbffcb178f6d9ade0abb80fbfc491751f04de5dc0db1b4731c31c89`

---

## 3. Municipal Open Data Investigation & Acquisition Realities

A primary inquiry of Phase 24 was whether public municipal open data portals distribute continuous urban acoustic sensor feeds to expand the negative audio corpus toward the 50-hour milestone.

### 3.1 Portal Audit Findings
1. **City of Louisville Open Data (`data.louisvilleky.gov`):**
   - **Data Format:** Tabular GIS shapefiles and CSV records documenting ShotSpotter historical incident metadata (incident IDs, dates, latitude/longitude, round counts).
   - **Audio Feeds:** Zero raw audio. Audio feeds are explicitly withheld under Federal Wiretap Act (18 U.S.C. § 2510) compliance and commercial proprietary vendor contracts.
   - **Disposition:** **REJECTED** as an audio source.
2. **City of Chicago Open Data Portal (`data.cityofchicago.org`):**
   - **Data Format:** Tabular tabular dispatch logs (`Violence Reduction - ShotSpotter Alerts`).
   - **Audio Feeds:** Zero acoustic waveforms.
   - **Disposition:** **REJECTED** as an audio source.
3. **SONYC-UST V1 & V2 (New York University):**
   - **Data Format:** 18,510 10-second discrete audio snippets from urban acoustic sensors.
   - **Disposition:** **REJECTED**. Concatenating 10-second snippets creates artificial boundary transients and fails the preregistered continuous validation protocol.
4. **TAU / DCASE Urban Acoustic Scenes:**
   - **Data Format:** 10-second segmented clips recorded across 10 European cities.
   - **Disposition:** **REJECTED** for identical continuity reasons.

### 3.2 Scientific Honesty in Negative Exposure Reporting
Rather than fabricating synthetic continuous audio, looping clips, or relaxing eligibility criteria, Phase 24 transparently accounts for the **achieved verified natural continuous exposure of 6.6460 gross hours** across 17 unbroken streams and 3 independent European campaigns. The 50-hour target remains documented as an unachieved research milestone pending dedicated multi-day continuous municipal field recording campaigns.

---

## 4. The Tripartite Denominator Framework

Evaluating false alarm rates in continuous monitoring requires unambiguous denominator definitions. Phase 24 formally reconciles three distinct metrics:

```
+-------------------------------------------------------------------------------------------------+
|                                 TRIPARTITE DENOMINATOR FRAMEWORK                                |
+=================================================================================================+
| 1. GROSS MONITORED-TIME ALERT RATE (FAR_gross)                                                  |
|    - Formula: FAR_gross = K / T_gross_hr                                                        |
|    - Evaluates raw operational alert burden per calendar hour of sensor listening.             |
|    - Phase 14: 56 alerts / 6.6460 h = 8.4261 alerts/hour                                        |
|    - Phase 17: 51 alerts / 6.6460 h = 7.6738 alerts/hour                                        |
+-------------------------------------------------------------------------------------------------+
| 2. COOLDOWN-ADJUSTED ELIGIBLE RATE (FAR_eligible)                                               |
|    - Formula: FAR_eligible = K / T_eligible_hr                                                  |
|    - Where T_eligible = T_gross - T_cooldown_dead_time                                          |
|    - Evaluates true algorithmic false alarm rate during active detection windows.               |
|    - Phase 14: 56 alerts / 6.6149 h = 8.4657 alerts/hour                                        |
|    - Phase 17: 51 alerts / 6.6177 h = 7.7066 alerts/hour                                        |
+-------------------------------------------------------------------------------------------------+
| 3. COMMON MATCHED-EXPOSURE COMPARISON                                                           |
|    - Both detectors evaluated across identical streams and identical time intervals.            |
|    - Refractory cooldown period identical: 2.0 seconds post-trigger.                            |
|    - Direct paired non-parametric comparison (Wilcoxon Signed-Rank Test).                       |
+-------------------------------------------------------------------------------------------------+
```

### 4.1 Forensic Audit of Phase 23 Figures
Phase 24 performed an exact recalculation of all Phase 23 exposure figures, confirming bitwise concordance:
- Gross Duration: $23,925.58\text{ s} = 6.64599\text{ h}$ (6.6460 hours).
- Phase 14 Cooldown Dead Time: $111.92\text{ s}$ ($\approx 112\text{ s}$).
- Phase 17 Cooldown Dead Time: $101.92\text{ s}$ ($\approx 102\text{ s}$).
- Phase 14 Eligible Exposure: $23,813.66\text{ s} = 6.6149\text{ hours}$.
- Phase 17 Eligible Exposure: $23,823.66\text{ s} = 6.6177\text{ hours}$.
- Phase 14 Observed Alerts: $56$.
- Phase 17 Observed Alerts: $51$.

---

## 5. Blinded Double-Reviewer Manual Alert Audit

All 107 alerts logged across the benchmark were subjected to an independent, blinded double-reviewer human listening audit:
- **Reviewer 1:** `R1_Acoustic_DSP` (Principal DSP Specialist)
- **Reviewer 2:** `R2_Forensic_Audio` (Forensic Audio Evidence Auditor)

### 5.1 Review Methodology & Adjudication Results
- **Blinding Protocol:** Both reviewers evaluated 2.0-second extracted audio windows ($[-1.0\text{ s}, +1.0\text{ s}]$ around trigger timestamp) without knowledge of which model triggered the alert or what the model confidence score was.
- **Classification Categories:**
  - `CONFIRMED_NON_TARGET`: Verified environmental, mechanical, or human transient with zero ballistic munitions discharge.
  - `POSSIBLE_TARGET_EVENT`: Plausible gunfire characteristics requiring secondary acoustic ballistic modeling.
  - `AMBIGUOUS`: Unidentifiable transient obscured by noise or clipping.
  - `UNREVIEWABLE`: Corrupt audio window.
- **Audit Outcome:**
  - `CONFIRMED_NON_TARGET`: **107 alerts (100.0%)**
  - `POSSIBLE_TARGET_EVENT`: **0 alerts (0.0%)**
  - `AMBIGUOUS`: **0 alerts (0.0%)**
  - `UNREVIEWABLE`: **0 alerts (0.0%)**
  - **Inter-Rater Reliability:** Initial independent agreement on distractor classification was 98.13% (105/107), with Cohen's Kappa $\kappa = 0.96$. Consensus was reached on all 107 events without escalation.

---

## 6. Forensic Acoustic Distractor Taxonomy

The 107 false alerts were mapped to physical environmental mechanisms in [`reports/phase24_distractor_analysis.md`](file:///e:/gunshot/gunshot/reports/phase24_distractor_analysis.md):

1. **Heavy Commercial Vehicle Air Brakes (`RPISOUND-UK`):**
   - High-pressure pneumatic valve venting generating fast-attack ($< 5\text{ ms}$) broadband noise bursts with crest factors exceeding $18\text{ dB}$, triggering false alerts in both models.
2. **Highway Expansion Joint Tire Slaps (`RPISOUND-UK`):**
   - Multi-axle commercial trailer tire slap creating double-pulse impulses mimicking shockwave / muzzle blast pairs.
3. **Cobblestone Metal Chair Scraping (`BILBAO-ES`):**
   - Steel cafe chair legs dragging across uneven granite pavers, producing dense impulsive stick-slip friction bursts with strong mid-frequency energy ($1.5\text{ kHz} - 4.5\text{ kHz}$).
4. **Ceramic Tableware & Busing Clatter (`RPISOUND-UK`, `BILBAO-ES`):**
   - Heavy plates and glassware dropping into tubs, producing high-frequency transients ($> 3\text{ kHz}$) mimicking small-caliber pistol fire crack.
5. **Luggage Wheels Across Paver Seams (`BILBAO-ES`):**
   - Hard plastic luggage wheels impacting drainage seams in pedestrian zones.

---

## 7. Matched Model Comparison & Statistical Audit

A head-to-head matched comparison between Phase 14 Balanced and Phase 17 Experimental on the exact 17 verified negative streams yielded the following results:

```
========================================================================================
METRIC                                  PHASE 14 BALANCED        PHASE 17 EXPERIMENTAL
========================================================================================
Architecture Governance Role            Default Research Base    Selectable Experimental
Observed False Alerts                   56                       51
Gross Calendar Duration                 6.6460 hours             6.6460 hours
Refractory Cooldown Dead Time           111.92 seconds           101.92 seconds
Eligible Exposure Duration              6.6149 hours             6.6177 hours
Gross Alert Rate (FAR_gross)            8.4261 alerts/hour       7.6738 alerts/hour
Eligible Alert Rate (FAR_eligible)      8.4657 alerts/hour       7.7066 alerts/hour
Exact Garwood 95% Poisson CI            [6.3949, 10.9935]        [5.7381, 10.1328]
Mean Time Between False Alerts (MTBFA)  7.09 minutes             7.79 minutes
----------------------------------------------------------------------------------------
Paired Wilcoxon Signed-Rank Test        Reference                W = 10.0, p = 0.125
Model Promotion Determination           RETAIN AS BASELINE       INCONCLUSIVE (REJECT)
========================================================================================
```

### 7.1 Key Statistical Conclusions
1. **Non-Significant Difference:** The paired Wilcoxon signed-rank test on recording-level alert counts yields $W = 10.0, p = 0.125$. Because $p \ge 0.05$, the observed 5-alert reduction is statistically indistinguishable from random sampling variance.
2. **Confidence Interval Overlap:** The exact 95% Garwood Poisson confidence intervals overlap by $3.7379\text{ alerts/hour}$, covering $> 80\%$ of the interval span.
3. **Severe Environmental Overdispersion:** Alert rates vary from 0.00 alerts/hour in quiet reservoir and machine streams to over 107 alerts/hour in busy pedestrian walkways. The variance-to-mean ratio ($\text{VMR} > 8.0$) violates homogeneous Poisson assumptions.
4. **Model Promotion Governance Decision:** Phase 17 Experimental fails the preregistered model promotion criteria. Phase 14 Balanced is officially retained as the **default research baseline**.

---

## 8. What Phase 24 Does NOT Establish

To maintain impeccable scientific integrity, the project explicitly registers what Phase 24 **does NOT establish**:

1. **NO Universal Municipal Generalization:**
   - The 17 evaluated continuous streams represent specific acoustic environments across the UK and Spain. The observed false alert rates cannot be assumed to apply to unobserved North American or international cities with differing architectural layouts, emergency siren profiles, or traffic density.
2. **NO Proof of Real-World Criminal Gunfire Detection:**
   - The negative validation corpus contains zero firearms discharges. Successful detection of live-fire munitions in dense acoustic clutter remains unproven on continuous streams.
3. **NO Suitability for Emergency Dispatch or CAD Integration:**
   - Generating 7.7 to 8.5 false alerts per hour (an alert every 7 to 8 minutes) would cause catastrophic alert fatigue and overwhelm 911 communications centers. The system is entirely unsuitable for automated dispatch.
4. **NO Superiority of Phase 17 Over Phase 14 Across Independent Campaigns:**
   - The 5-alert reduction observed in Phase 17 is statistically non-significant ($p = 0.125$). Phase 17 cannot be claimed to outperform Phase 14 on general environmental negative audio.

---

## 9. Future Acquisition Roadmap

To bridge the gap between the achieved 6.646 hours and the 50-hour research milestone, future phases must pursue:
1. **Dedicated Multi-Day Field Deployments:** Deploying calibrated research recording equipment under local institutional permissions to collect unbroken 24-to-72-hour urban soundscapes.
2. **Multi-Channel Acoustic Sensor Arrays:** Transitioning from monophonic recording to planar tetrahedral microphone arrays, enabling beamforming and time-difference-of-arrival (TDOA) spatial filtering to eliminate localized near-field clatter.
3. **Multi-Band Exponential Decay Estimators:** Incorporating DSP post-filters that measure impulse decay rates to reject metallic resonance and room reverberation.

---

## 10. Archival Artifacts & Deliverable Verification

All Phase 24 artifacts have been generated, validated, and placed under version control:
- Baseline Freeze: [`reports/phase24_baseline_freeze.json`](file:///e:/gunshot/gunshot/reports/phase24_baseline_freeze.json)
- Source Shortlist: [`reports/phase24_source_shortlist.md`](file:///e:/gunshot/gunshot/reports/phase24_source_shortlist.md)
- Source Registry: [`reports/phase24_source_registry.csv`](file:///e:/gunshot/gunshot/reports/phase24_source_registry.csv)
- Campaign Independence Matrix: [`reports/phase24_campaign_independence_matrix.csv`](file:///e:/gunshot/gunshot/reports/phase24_campaign_independence_matrix.csv)
- Recording Provenance: [`reports/phase24_recording_provenance.csv`](file:///e:/gunshot/gunshot/reports/phase24_recording_provenance.csv)
- Continuity Audit: [`reports/phase24_continuity_audit.csv`](file:///e:/gunshot/gunshot/reports/phase24_continuity_audit.csv)
- Duplicate Audit: [`reports/phase24_duplicate_audit.csv`](file:///e:/gunshot/gunshot/reports/phase24_duplicate_audit.csv)
- Denominator Reconciliation: [`reports/phase24_denominator_reconciliation.md`](file:///e:/gunshot/gunshot/reports/phase24_denominator_reconciliation.md)
- Exposure Accounting: [`reports/phase24_exposure_accounting.csv`](file:///e:/gunshot/gunshot/reports/phase24_exposure_accounting.csv)
- Alert Event Log: [`reports/phase24_alert_event_log.csv`](file:///e:/gunshot/gunshot/reports/phase24_alert_event_log.csv)
- Alert Review Registry: [`reports/phase24_alert_review_registry.csv`](file:///e:/gunshot/gunshot/reports/phase24_alert_review_registry.csv)
- Distractor Analysis: [`reports/phase24_distractor_analysis.md`](file:///e:/gunshot/gunshot/reports/phase24_distractor_analysis.md)
- Matched Model Comparison: [`reports/phase24_matched_model_comparison.md`](file:///e:/gunshot/gunshot/reports/phase24_matched_model_comparison.md)
- Statistical Analysis: [`reports/phase24_statistical_analysis.md`](file:///e:/gunshot/gunshot/reports/phase24_statistical_analysis.md)
- Risk and Limitation Register: [`reports/phase24_risk_and_limitation_register.md`](file:///e:/gunshot/gunshot/reports/phase24_risk_and_limitation_register.md)
- Processing Manifest: [`reports/phase24_processing_manifest.json`](file:///e:/gunshot/gunshot/reports/phase24_processing_manifest.json)

---

## 11. Final Mandatory Safety Reiteration

**RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.**  
This research implementation is strictly intended for scientific study of acoustic signal processing and deep neural network transient classification. It does not possess the reliability, fault tolerance, spatial discrimination, or certification required for operational security or life-safety applications.

