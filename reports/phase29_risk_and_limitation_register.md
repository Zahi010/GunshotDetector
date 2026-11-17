# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY

> [!CAUTION]
> **MANDATORY SAFETY DESIGNATION**  
> **RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.**  
> This experimental acoustic machine-learning research software is uncertified and must never be deployed for autonomous emergency dispatch, tactical police response, active-shooter alerting, automated evacuation, building lockdown, or life-critical physical security.  
> Use legally obtained recordings and safe audio playback only. Live-fire testing and hazardous acoustic experiments are strictly prohibited.

---

# PHASE 29 RISK AND LIMITATION REGISTER
## Formal Operational Risk Catalog, Acoustic Failure Modes & Benchmark Governance Boundaries

**Document Identifier:** `PHASE29-REG-RISK-LIMITATIONS`  
**Phase:** `PHASE_29_CONFIGURATION_VERIFICATION_AIRCRAFT_VALIDATION_ROBUSTNESS_AUDIT`  
**Focus:** Explicit Enumeration of Algorithmic, Statistical, Operational, and Legal Failure Modes

---

## 1. Risk Register Overview

This register formally logs eight critical technical risks and scientific limitations inherent to the acoustic gunshot detection prototype. All users, researchers, and stakeholders must strictly review these constraints before interpreting any benchmark result.

---

## 2. Risk Matrix

| Risk ID | Risk Category | Risk Summary | Severity | Mitigating Constraint / Action |
| :---: | :--- | :--- | :---: | :--- |
| **RSK-01** | **Life Safety** | Autonomous Tactical Police Dispatch or Active Shooter Evacuation | **CRITICAL** | Strict prohibition: Research prototype only; never connect to autonomous dispatch or alarm systems. |
| **RSK-02** | **Statistical** | Small-Sample Cluster Invalidation ($G = 4$ campaigns) | **HIGH** | Explicit prohibition on claiming statistical significance or constructing cluster-robust CIs. |
| **RSK-03** | **Algorithmic** | Phase 17 Aircraft Fragmentation & Exposure Blindness (29.1%) | **HIGH** | Retain Phase 14 Balanced as Default Research Baseline; reject Phase 17 baseline promotion. |
| **RSK-04** | **Environmental**| Dense Urban Traffic Alert Saturation (>50 alerts/hr in Bilbao) | **HIGH** | Disclose that current models fail operational false-alarm standards in dense European city centers. |
| **RSK-05** | **Forensic** | Missing Sub-Window Score Traces in Historical Ingestion | **MEDIUM** | Explicitly classify aircraft fragmentation mechanism as "partially supported" rather than verified fact. |
| **RSK-06** | **Legal** | Commercial Exploitation of CC BY-NC 4.0 Datasets | **HIGH** | Enforce non-commercial research use only; require commercial users to obtain independent licenses. |
| **RSK-07** | **Sampling** | Severe Geographic Exposure Imbalance (90.9% in 2 campaigns) | **MEDIUM** | Mandate exposure-normalized rate reporting alongside raw alert counts. |
| **RSK-08** | **Benchmark** | Decoupled Positive and Negative Continuous Evaluation | **MEDIUM** | Positive live-fire rounds (Pittsburgh) evaluated separately from continuous negative exposure. |

---

## 3. Detailed Risk Characterization

### RSK-01: Prohibition Against Life-Critical Deployment
- **Description:** The system is an experimental machine-learning demonstration prototype trained on public acoustic corpora. It lacks hardware redundancy, environmental enclosure hardening, anti-tamper sensing, sub-millisecond real-time OS scheduling, and certified ballistic detection reliability.
- **Operational Hazard:** Deploying this prototype for active-shooter notification or automated building lockdown could result in catastrophic failure to alert during real gunfire or disruptive false lockdowns caused by vehicle backfires, pneumatic tools, or jet aircraft.

### RSK-02: Small-Sample Cluster Constraints ($G = 4$)
- **Description:** All 23 audio streams originate from only 4 independent data collection campaigns (Southampton, Chew Magna, Bilbao, and Adelaide).
- **Statistical Hazard:** Observations within a campaign share background noise and acoustic propagation characteristics. With only $G=4$ independent clusters, standard errors cannot be estimated robustly, sign tests are mathematically bounded ($p \ge 0.125$), and universal generalization claims cannot be supported.

### RSK-03: Phase 17 Aircraft Distractor Fragmentation
- **Description:** During continuous jet flyovers, Phase 17's animal suppression sub-filter drops acoustic scores into the release band, prematurely terminating active events and immediately re-triggering upon acoustic recovery.
- **Consequence:** In AeroSonicDB, Phase 17 triggered 108 false alerts (+50% increase over Phase 14) and blinded the detector for 29.1% of monitored time (1.75 hours). Phase 17 is unsuitable for environments near civilian or military airports.

### RSK-04: Dense Urban Traffic Alert Saturation
- **Description:** In the Bilbao campaign, both Phase 14 and Phase 17 triggered dozens of false alarms across 33.7 minutes of audio, resulting in false alert rates exceeding **50 alerts per hour**.
- **Operational Reality:** In operational municipal deployments, acceptable false alert rates are typically $< 1\text{ alert per week}$ per square kilometer. Both models are orders of magnitude away from acceptable urban noise rejection.

### RSK-05: Missing Intermediate Sub-Window Score Traces
- **Description:** In Phase 27's execution of `evaluate_phase27_aerosonic.py`, sub-window raw score traces and intermediate boolean suppression flags were not dumped to disk.
- **Forensic Impact:** The step-by-step mechanism of aircraft fragmentation cannot be proven at sub-second resolution. It remains a partially supported hypothesis based on model source code inspection and macro alert timing.

### RSK-06: CC BY-NC 4.0 Non-Commercial Boundaries
- **Description:** AeroSonicDB is licensed under Creative Commons Attribution-NonCommercial 4.0 International.
- **Legal Impact:** Any commercial integration, paid pilot deployment, or proprietary surveillance product using this benchmark without a commercial license from the original authors constitutes copyright infringement.

### RSK-07: Exposure Imbalance Across Benchmark Campaigns
- **Description:** Over 90.9% of monitored time is concentrated in Southampton (5.5 hr) and Adelaide (6.0 hr), while Bilbao (0.56 hr) and Chew Magna (0.58 hr) represent less than 10% combined.
- **Analytical Impact:** Aggregate raw counts are overwhelmingly dominated by Adelaide and Southampton. Raw count comparisons obscure the fact that Phase 17 has a lower rate in Bilbao and Southampton.

### RSK-08: Separation of Positive and Negative Benchmarks
- **Description:** The 23 continuous streams in the negative benchmark contain zero confirmed gunshots. Conversely, the 50 positive gunshot rounds evaluated in Phase 20–22 (Pittsburgh DQV) were collected in a controlled municipal validation campaign.
- **Scientific Impact:** The trade-off between gunshot recall and false-alert rate cannot be evaluated simultaneously on the same natural continuous soundscape.

