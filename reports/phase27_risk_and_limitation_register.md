# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY

**MANDATORY SAFETY DESIGNATION:**
This experimental acoustic machine-learning software is uncertified and must never be deployed for autonomous emergency dispatch, tactical police response, active-shooter alerting, automated evacuation, building lockdown, or life-critical physical security.

Use legally obtained recordings and safe audio playback only. Live-fire testing and hazardous acoustic experiments are strictly prohibited.


# PHASE 27 — RISK AND LIMITATION REGISTER

## 1. Safety and Operational Prohibitions
- **RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY:** This software is an experimental machine-learning prototype. It has never received third-party life-safety certification (e.g., UL, NFPA, DoD, NIJ).
- **Prohibited Uses:** Autonomous emergency 911 dispatch, tactical police response, automated building lockdown, fire suppression initiation, active-shooter alerting, or critical physical perimeter defense.
- **Acoustic Testing Safety:** Strictly prohibited from live-fire munitions testing or hazardous acoustic experiments. All research must utilize legally obtained digital recordings.

## 2. Technical Risk Matrix

| Risk ID | Risk Title | Category | Likelihood | Impact | Severity | Mitigation & Audit Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **RSK-27-01** | Life-Safety Misrepresentation | Operational | High | Critical | **CRITICAL** | Prominent safety banners on all artifacts; explicit disclaimers in technical reports. |
| **RSK-27-02** | Anti-Bot Evasion / Sandboxing | Compliance | Medium | High | **HIGH** | Discontinued web scraping; accessed Zenodo via official sanctioned InvenioRDM REST API. |
| **RSK-27-03** | Cluster Fragmentation in P17 | Algorithmic | High | High | **HIGH** | Retained Phase 14 Balanced as default research baseline; rejected Phase 17 promotion. |
| **RSK-27-04** | Cooldown Exposure Blindness | Operational | High | Medium | **MEDIUM** | Monitored tripartite denominators; highlighted Phase 17's excessive 29.1% blindness on AeroSonicDB. |
| **RSK-27-05** | Statistical Transcription Errors | Scientific | Medium | Medium | **MEDIUM** | Audited historical Wilcoxon discrepancies; corrected mathematical derivations and test formulations. |
| **RSK-27-06** | Commercial License Violation | Legal | Medium | High | **HIGH** | Reverified AeroSonicDB true license as CC BY-NC 4.0; documented non-commercial research limitation. |
| **RSK-27-07** | Geographic Generalization Gap | Scientific | High | Medium | **MEDIUM** | Acknowledged dataset covers only 4 urban areas (UK, Spain, France, Australia); cannot generalize globally. |

## 3. Explicit Generalization and Evaluation Limits
### What Phase 27 Does NOT Establish:
1. **Does NOT Establish Reliable Detection of Unexpected Criminal Gunfire:** Evaluation on 23 continuous negative recordings measures false-alarm rejection on ambient background; it does not measure real-world sensitivity against unexpected, concealed, or suppressed criminal gunfire.
2. **Does NOT Establish Generalization to Arbitrary Cities:** Urban acoustic morphology varies widely (canyon geometries, building materials, climate). Results from 4 specific campaigns cannot predict performance in arbitrary global municipalities.
3. **Does NOT Establish Municipal-Scale Operational False-Alert Feasibility:** An eligible false-alert rate of 10.22 alerts/hr translates to ~245 false alarms per 24-hour period per sensor node. In a municipal sensor grid of 100 nodes, this would produce 24,500 false alerts daily, which is completely unviable for dispatch operations.
4. **Does NOT Establish Public-Safety or Emergency-Response Suitability:** The prototype lacks automated health monitoring, sensor tamper detection, encrypted transport, and redundant fail-safes required for emergency response.
5. **Does NOT Establish Superiority of Phase 17 Across Independent Campaigns:** Empirical evaluation conclusively demonstrated that Phase 17 produced +24.2% more false alerts overall and was inferior in 5 out of 6 AeroSonicDB streams.
