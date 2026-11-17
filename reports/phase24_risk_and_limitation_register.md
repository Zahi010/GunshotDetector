# PHASE 24 — RISK AND LIMITATION REGISTER: ACOUSTIC ML RESEARCH PROTOCOL

> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.**  
> *This experimental acoustic machine-learning software is uncertified and must never be deployed for autonomous emergency dispatch, tactical police response, active-shooter alerting, automated lockdown or evacuation, or life-critical physical security. Use legally obtained recordings and safe audio playback only. Live-fire testing and hazardous acoustic experiments are strictly prohibited.*

---

## 1. Risk Register Overview

This register formally itemizes the technical, statistical, operational, and data provenance risks associated with the Phase 24 acoustic gunshot detection research prototype. Each risk is evaluated under likelihood and severity scales and assigned actionable containment protocols.

---

## 2. Risk Matrix

| Risk ID | Risk Domain | Severity | Likelihood | Risk Description | Containment & Mitigation Protocol | Status |
|---|---|---|---|---|---|---|
| **RISK-24-01** | **Life Safety** | **CRITICAL** | Low (Internal) / High (External Misuse) | **Unauthorized Deployment in Life-Safety Applications:** Attempting to use the research prototype for autonomous 911 dispatch, tactical armed response, active shooter alerting, or lockdown automation. | Enforce prominent machine-readable and human-readable safety banners (`RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY`) across all source code, manifests, and technical reports. Refuse all integration with emergency communication infrastructure. | **ACTIVE / PERMANENT** |
| **RISK-24-02** | **Provenance & Compliance** | **CRITICAL** | Medium | **Municipal Portal Data Expectation Mismatch:** Assuming municipal open data portals (e.g. City of Chicago, Louisville Metro) distribute raw acoustic audio streams. In reality, portals publish tabular GIS/CAD metadata only due to wiretap laws and vendor IP restrictions. | Formally audit portals before acquisition; log and document exact data formats; strictly reject wiretap-violating or unverified sources; never scrape or bypass authentication. | **MITIGATED** |
| **RISK-24-03** | **Data Exposure** | **HIGH** | High | **Benchmark Duration Shortfall:** Inability to achieve 50 hours of verified continuous negative audio due to the scarcity of legally accessible, multi-hour unbroken urban field recordings. | Reject synthetic concatenation, looping, or audio duplication. Report achieved exposure (6.6460 hours) honestly and transparently with exact Garwood confidence bounds. | **RESOLVED / REPORTED** |
| **RISK-24-04** | **Acoustic ML** | **HIGH** | High | **Acoustic Distractor Susceptibility:** Extreme false-alert vulnerability to urban non-target transients (truck air brakes, tire slaps, metal chair drags, ceramic dish drops) yielding FARs up to 107 alerts/hour. | Quantify distractor categories via blinded double-reviewer audit; establish exact peak crest factors; reject claims of production readiness. | **DOCUMENTED** |
| **RISK-24-05** | **Statistical Rigor** | **HIGH** | High | **Severe Environmental Overdispersion:** False alerts cluster heavily in specific micro-environments (VMR > 8.0), invalidating homogeneous Poisson assumptions and naive cross-city extrapolation. | Employ exact Garwood confidence intervals; calculate recording-level non-parametric Wilcoxon tests; prohibit claims of universal city-wide performance. | **MITIGATED** |
| **RISK-24-06** | **Model Governance** | **MEDIUM** | Medium | **Premature Baseline Promotion:** Promoting Phase 17 Experimental over Phase 14 Balanced based on an unadjusted 5-alert reduction that fails statistical significance ($p = 0.125$). | Enforce preregistered Model Promotion Criteria; retain Phase 14 Balanced as the default research baseline; classify Phase 17 outcome as `INCONCLUSIVE`. | **ENFORCED** |
| **RISK-24-07** | **Evaluation Metrics** | **MEDIUM** | Low | **Denominator Ambiguity:** Conflating gross calendar duration with refractory cooldown-adjusted exposure, distorting false-alarm rate metrics. | Enforce the Tripartite Denominator Framework; explicitly report both $\text{FAR}_{\text{gross}}$ and $\text{FAR}_{\text{eligible}}$ alongside matched common intervals. | **RECONCILED** |
| **RISK-24-08** | **Hardware / Sensor** | **HIGH** | Medium | **Single-Microphone Spatial Blindness:** Monophonic recordings cannot distinguish between a 110 dB impulse at 50 meters and a 75 dB impulse at 1 meter. | Require multi-channel microphone array architectures and time-difference-of-arrival (TDOA) spatial filtering for future physical sensor design. | **DEFERRED** |

---

## 3. Explicit Limitations of Phase 24

To ensure absolute scientific integrity, the project explicitly registers what Phase 24 **does NOT establish**:
1. **No Universal Urban Generalization:** The 17 continuous streams originate from three European regions (UK Industrial, Chew Magna, Bilbao Old Town). These results cannot predict false-alarm rates in North American cities with different traffic patterns, architectural reverberation, or sirens.
2. **No Real-World Criminal Gunfire Detection Proof:** The negative benchmark contains zero firearms discharges. Performance on real-world criminal gunfire in acoustic clutter remains unverified.
3. **No Commercial or Operational Certification:** The software prototype does not meet UL, CE, NFPA, or NIJ public-safety sensor certification standards.
4. **No Automated CAD or Dispatch Suitability:** Generating 7.7 to 8.5 false alerts per hour would cripple municipal dispatchers and cause severe alert fatigue.

---

## 4. Mandatory Safety Reiteration

This software is strictly an experimental machine-learning research demonstration. Under no circumstances should this software be connected to or relied upon for physical safety, tactical armed deployment, or automated alarm systems.

