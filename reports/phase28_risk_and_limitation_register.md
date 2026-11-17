# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY

**MANDATORY SAFETY DESIGNATION:**
This experimental acoustic machine-learning software is uncertified and must never be deployed for autonomous emergency dispatch, tactical police response, active-shooter alerting, automated evacuation, building lockdown, or life-critical physical security.

Use legally obtained recordings and safe audio playback only. Live-fire testing and hazardous acoustic experiments are strictly prohibited.

---

# PHASE 28 TECHNICAL AUDIT REPORT
## Risk Matrix, Limitation Register & Operational Governance

**Document Identifier:** `PHASE28-REP-RISK-REGISTER`  
**Phase:** `PHASE_28_INDEPENDENT_REPRODUCTION_CAMPAIGN_STATISTICS_COOLDOWN_FORENSICS`  
**Governance Scope:** Research software evaluation, model freeze compliance & data integrity

---

## 1. Safety and Operational Governance Policy

### Absolute Operational Prohibitions
The software evaluated herein is an **experimental research prototype** designed solely for offline academic exploration of acoustic feature extraction and machine-learning classification. 
- **NO LIFE-SAFETY APPLICATION:** The system has not been certified under NFPA 72, UL 2017, DoD MIL-STD-810H, or NIJ public-safety standards.
- **NO DISPATCH AUTOMATION:** It must never be connected to or utilized for autonomous emergency 911 dispatch, tactical police routing, active-shooter lockdown, automated fire suppression, or perimeter security defense.
- **NO LIVE-FIRE EXPERIMENTS:** The research protocol strictly prohibits live-fire munitions testing, field explosives, or hazardous acoustic generation. All experiments must utilize legally obtained digital audio recordings.

---

## 2. Technical Risk Matrix

| Risk ID | Risk Title | Category | Likelihood | Impact | Severity | Status & Mitigation Strategy |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **RSK-28-01** | Life-Safety Misrepresentation | Operational | High | Critical | **CRITICAL** | Prominent safety banners on every report, manifest, and test script; explicit disclaimer of life-safety fitness. |
| **RSK-28-02** | Cooldown Ledger Discrepancy | Accounting | Low | Medium | **LOW** | **RECONCILED IN PHASE 28:** Proved that narrative report draft values (455.52s / 6381.76s) differed from underlying accounting CSV (453.92s / 6385.20s) by +1.60s and -3.44s without affecting conclusions. Full per-alert ledger published. |
| **RSK-28-03** | Cluster Fragmentation in P17 | Algorithmic | High | High | **HIGH** | **RESOLVED:** Confirmed Phase 17's elevated off-threshold (`0.48`) and animal suppression heuristics fragment continuous flyovers (+50% alerts). Retained Phase 14 Balanced as default research baseline; rejected Phase 17 promotion. |
| **RSK-28-04** | Within-Campaign Clustering | Statistical | High | Medium | **MEDIUM** | **AUDITED:** Formalized LOCO sensitivity and demonstrated small-cluster constraints ($G=4$); cautioned against treating 23 streams as $i.i.d.$ observations. |
| **RSK-28-05** | Poisson Overdispersion | Inference | High | Medium | **MEDIUM** | **AUDITED:** Demonstrated that Garwood CIs represent conditional within-stream bounds and cannot be extrapolated across heterogeneous environments; prohibited CI overlap as a paired test. |
| **RSK-28-06** | Commercial License Breach | Compliance | Medium | High | **HIGH** | **VERIFIED:** Reconfirmed AeroSonicDB license is CC BY-NC 4.0; research reproduction permitted, commercial usage strictly prohibited. |
| **RSK-28-07** | Geographic Generalization Gap | Scientific | High | Medium | **MEDIUM** | **DOCUMENTED:** Explicitly restricted findings to the 4 observed campaigns; prohibited extrapolating performance to arbitrary unstudied cities. |

---

## 3. Explicit Operational and Generalization Limits

### What Phase 28 Does NOT Establish:
1. **Does NOT Establish Reliable Gunshot Detection Sensitivity:** The benchmark consists exclusively of continuous negative-background ambient audio. It assesses non-target rejection; it does **not** establish probability of detection ($P_d$), missed-detection rate, or round-level localization accuracy for unexpected or suppressed firearm discharges.
2. **Does NOT Establish Municipal Operational Readiness:** An eligible false alert rate of **10.22 alerts/hour** generates approximately **245 false alerts per day per sensor**. In a municipal sensor deployment of 100 outdoor nodes, this translates to over **24,500 false dispatches every 24 hours**. This rate is several orders of magnitude above acceptable dispatch thresholds.
3. **Does NOT Establish Independence Across Campaigns:** The 23 continuous recordings originate from only four distinct campaigns. Performance variance is dominated by site-specific environmental characteristics rather than stationary Gaussian noise.
4. **Does NOT Establish Model Certification:** The software contains no automated sensor fault detection, no hardware watchdog monitoring, no cryptographic transmission security, and no redundant fail-safe mechanisms.

---

## 4. Architectural Baseline Decision Statement

> [!IMPORTANT]
> **DECISION STATEMENT:**  
> **Phase 14 Balanced remains the DEFAULT RESEARCH BASELINE.**  
> **Phase 17 remains an EXPERIMENTAL COMPARISON PROFILE.**  
> Phase 27's reported comparison decisively favors Phase 14 (-31 fewer alerts overall; -36 fewer alerts on AeroSonicDB), but the four-campaign benchmark does not establish universal performance, municipal operational feasibility, or life-safety certification.

