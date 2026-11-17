# Phase 32: Risk and Limitation Register
## Technical, Methodological & Life-Safety Risk Register for Acoustic Machine-Learning Research

**Document ID:** `REPORT-PHASE32-RISK-001`  
**Phase:** 32 (Risk & Limitation Audit)  
**Date:** November 2026  
**Status:** ACTIVE RESEARCH RISK REGISTER — HIGH/CRITICAL MITIGATIONS DOCUMENTED  

---

### MANDATORY SAFETY DESIGNATION
> [!CAUTION]
> **RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.**  
> This experimental acoustic machine-learning software is uncertified and must never be deployed for autonomous emergency dispatch, tactical police response, active-shooter alerting, automated evacuation, building lockdown, or life-critical physical security. Use legally obtained recordings and safe audio playback only. Live-fire testing and hazardous acoustic experiments are strictly prohibited.

---

## 1. Risk Matrix & Classification Overview

| Risk ID | Risk Domain | Severity | Likelihood | Pre-Mitigation Risk | Mitigation Strategy | Post-Mitigation Risk |
| :---: | :--- | :---: | :---: | :---: | :--- | :---: |
| **RSK-01** | Life-Safety Operational Misuse | **CRITICAL** | Moderate | **UNACCEPTABLE** | Explicit architectural prohibitions, license restrictions, mandatory safety banners on all interfaces. | **CONTROLLED** |
| **RSK-02** | State-Machine Candidate Premature Promotion | **HIGH** | High | **HIGH** | Baseline freeze policy: candidate patch kept in `experiments/` only; Phase 14 retained as sole default baseline. | **LOW** |
| **RSK-03** | Multi-Credit Evaluation Fallacy | **HIGH** | High | **HIGH** | Mandatory 1-to-1 event matching standard for all burst and continuous audio evaluations. | **LOW** |
| **RSK-04** | Statistical Inconclusiveness (Low Power) | **MEDIUM** | High | **MEDIUM** | Multi-method reporting: exact tied permutation, asymptotic SciPy, Pratt, and Sign test side-by-side. | **LOW** |
| **RSK-05** | Acoustic Generalization Gap (Aviation Dominance) | **HIGH** | High | **HIGH** | Cross-campaign stratification; separating aircraft flyovers from municipal ambient noise. | **MEDIUM** |
| **RSK-06** | Live-Fire Acoustic Hazard & Legal Non-Compliance | **CRITICAL** | Low | **HIGH** | Strict prohibition on live-fire testing; historical controlled recordings audited as read-only research data. | **CONTROLLED** |

---

## 2. Detailed Technical Risk Assessments

### RSK-01: Life-Safety Operational Deployment Hazard
- **Hazard Description:** Deployment of uncertified machine-learning models for automated emergency dispatch, armed tactical response, active shooter alerting, or automated facility lockdowns.
- **Consequences:** False alarms trigger unwarranted armed responses, panic, economic disruption, and civilian danger; false negatives result in unaddressed lethal violence.
- **Root Cause:** Current research models exhibit a false-alert rate of $\approx 10 - 13\text{ alerts per hour}$ on continuous urban/aviation noise floors. In a 24-hour municipal deployment, a single sensor would emit $> 240$ false gunshot dispatches per day!
- **Mandatory Mitigations:**
  1. Prominent safety banners on all software artifacts, source files, and reports.
  2. Software architecture contains no autonomous dispatch APIs or hardware actuator triggers.
  3. Status permanently designated: `RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY`.

### RSK-02: Premature Promotion of Unvalidated Candidate Patches
- **Hazard Description:** Promoting `model_phase17_state_reset_candidate.py` to production baseline without extensive independent prospective validation.
- **Consequences:** The candidate patch fixes synthetic regression vectors and eliminates 42 AeroSonicDB alerts, but has not undergone prospective validation on newly acquired, independent physical recording campaigns.
- **Mitigation:**
  - Strict baseline governance: `model_phase14.py` remains the frozen **Default Research Baseline**.
  - `model_phase17_state_reset_candidate.py` is quarantined under `experiments/phase31/` as a diagnostic reference only.

### RSK-03: Multi-Credit Matching Fallacy in Gunfire Datasets
- **Hazard Description:** Evaluating gunshot detectors against multi-shot burst sequences using loose temporal windows that grant multiple round credits to a single sustained alert.
- **Consequences:** Creates an illusion of statistical significance ($p = 0.03125$ on Pittsburgh DQV 2018), obscuring that the detector cannot resolve individual rounds.
- **Mitigation:**
  - Enforce a strict 1-to-1 event matching protocol where each alert can consume at most one ground-truth round.
  - Require incident-level reporting alongside round-level reporting.

### RSK-04: Statistical Power Limitations from Low Sample Size
- **Hazard Description:** Evaluating paired differences across 23 continuous streams where 15 streams have identical alert counts ($d=0$), leaving an effective sample size of $n=8$.
- **Consequences:** $n=8$ provides limited statistical power to detect small effect sizes ($1 - \beta \approx 0.35$).
- **Mitigation:**
  - Acknowledge statistical inconclusiveness: $p = 0.2109$ indicates lack of evidence of difference, not proof of equivalence.
  - Report exact permutation distributions, asymptotic approximations, Pratt zero-handling, and non-parametric sign tests.

### RSK-05: Acoustic Domain Generalization Gap
- **Hazard Description:** Models tuned or evaluated primarily on urban background recordings exhibit massive performance degradation when exposed to aviation, industrial, or rural soundscapes.
- **Consequences:** High-amplitude low-frequency jet turbine harmonics or animal vocalizations trigger unexpected state-machine leakage and alert fragmentation.
- **Mitigation:**
  - Stratify all benchmarks by acoustic domain (Aviation vs Municipal Urban vs Residential).
  - Explicitly evaluate continuous audio streams across diverse geographic campaigns.

---

## 3. Residual Risk Sign-Off

The research team certifies that all active risks are identified, classified, and bounded by technical safeguards. No operational life-safety claims are made.

