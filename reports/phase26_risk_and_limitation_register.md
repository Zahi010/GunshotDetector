# PHASE 26 RISK AND LIMITATION REGISTER: ACOUSTIC ML RESEARCH PROTOCOL

> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.**  
> *This experimental acoustic machine-learning software is uncertified and must never be deployed for autonomous emergency dispatch, tactical police response, active-shooter alerting, automated lockdown or evacuation, or life-critical physical security. Use legally obtained recordings and safe audio playback only. Live-fire testing and hazardous acoustic experiments are strictly prohibited.*


---

## 1. Risk Register Overview

This register formally identifies, classifies, and tracks operational, technical, legal, and statistical risks associated with the Phase 26 acoustic gunshot detection research prototype (`E:/gunshot`).

---

## 2. Risk Matrix

| Risk ID | Domain | Severity | Likelihood | Risk Description | Containment & Mitigation Protocol | Status |
|---|---|---|---|---|---|---|
| **RISK-26-01** | **Life Safety** | **CRITICAL** | Low (Internal) / High (External Misuse) | **Unauthorized Operational Deployment:** Using the research software for automated 911 dispatch, tactical armed response, active shooter alerting, or lockdown automation. | Enforce mandatory safety designation banners across all source code, manifests, and technical reports. Prohibit integration with emergency dispatch or CAD infrastructure. | **PERMANENT / ACTIVE** |
| **RISK-26-02** | **Provenance & Compliance** | **CRITICAL** | Medium | **Municipal Portal Misconception:** Assuming municipal open data portals host downloadable raw acoustic audio feeds. In reality, portals publish tabular incident logs only. | Formally audit portals before acquisition; qualify legal claims objectively; reject wiretap-violating or unverified sources; never scrape or bypass authentication. | **MITIGATED** |
| **RISK-26-03** | **Anti-Bot / Access Gate** | **HIGH** | High | **Zenodo Edge Cloudflare 403 Blocking:** Programmatic automated download tools receive HTTP 403 Forbidden due to Cloudflare anti-bot bot-management challenges on Zenodo file endpoints. | Strictly adhere to agent guidelines: never attempt to bypass, spoof, or evade anti-bot gates; classify Candidate A as `CONDITIONAL_ACCESS_PENDING` requiring manual browser acquisition or authenticated token. | **ACTIVE / MANAGED** |
| **RISK-26-04** | **Data Integrity** | **CRITICAL** | High | **Synthetic Concatenation / Discontinuity:** Concatenating short 30-second clips (e.g. Candidate B / ISD) to artificially create continuous streams, corrupting temporal arrival dynamics. | Enforce strict continuous-recording eligibility rule (Rule R-CONT-01): reject non-continuous short clips; zero synthetic concatenation permitted. | **MITIGATED / ENFORCED** |
| **RISK-26-05** | **Data Exposure** | **HIGH** | High | **Benchmark Duration Shortfall:** Inability to achieve the 20-hour expansion target due to access gates and scarcity of verified continuous open recordings. | Reject synthetic concatenation, looping, or audio duplication. Report achieved exposure (6.6460 gross hours) honestly and transparently with exact Garwood bounds. | **DOCUMENTED / ACTIVE** |
| **RISK-26-06** | **Acoustic ML** | **HIGH** | High | **Acoustic Distractor Susceptibility:** Extreme false-alert vulnerability to urban non-target transients (truck air brakes, tire slaps, metal chair drags, ceramic dish drops) yielding FARs up to 40.9 alerts/hour. | Quantify distractor categories via blinded double-reviewer audit; establish peak crest factors; reject claims of production readiness. | **DOCUMENTED** |
| **RISK-26-07** | **Statistical Rigor** | **HIGH** | High | **Severe Environmental Overdispersion:** False alerts cluster heavily in specific micro-environments (VMR > 8.0), invalidating homogeneous Poisson assumptions and naive cross-city extrapolation. | Employ exact Garwood confidence intervals; calculate recording-level non-parametric Wilcoxon tests; prohibit claims of universal city-wide performance. | **MITIGATED** |
| **RISK-26-08** | **Model Governance** | **MEDIUM** | Medium | **Premature Baseline Promotion:** Promoting Phase 17 Experimental over Phase 14 Balanced based on an unadjusted 5-alert reduction that fails statistical significance ($p = 0.125$). | Enforce preregistered Model Promotion Criteria; retain Phase 14 Balanced as the default research baseline; classify Phase 17 outcome as `INCONCLUSIVE`. | **ENFORCED** |
| **RISK-26-09** | **Hardware / Sensor** | **HIGH** | Medium | **Single-Microphone Spatial Blindness:** Monophonic recordings cannot distinguish between a 110 dB impulse at 50 meters and a 75 dB impulse at 1 meter. | Require multi-channel microphone array architectures and time-difference-of-arrival (TDOA) spatial filtering for future physical sensor design. | **DEFERRED** |

---

## 3. Explicit Limitations of Phase 26

To ensure scientific integrity, the project explicitly registers what Phase 26 **does NOT establish**:
1. **NO Universal Urban Generalization:** The 17 continuous streams originate from three European regions (UK Industrial, Chew Magna, Bilbao Old Town). These results cannot predict false-alarm rates in North American cities with different traffic patterns, architectural reverberation, or sirens.
2. **NO Proof of Real-World Criminal Gunfire Detection:** The negative benchmark contains zero firearms discharges. Performance on real-world criminal gunfire in acoustic clutter remains unverified.
3. **NO Commercial or Operational Certification:** The software prototype does not meet UL, CE, NFPA, or NIJ public-safety sensor certification standards.
4. **NO Automated CAD or Dispatch Suitability:** Generating 7.7 to 8.5 false alerts per hour would cripple municipal dispatchers and cause severe alert fatigue.
5. **NO Superiority of Phase 17 Over Phase 14 Across Independent Campaigns:** The 5-alert difference fails statistical significance ($p = 0.125$). Phase 17 cannot be claimed to outperform Phase 14 on general environmental negative audio.
6. **NO Ingestion of Candidate A or Candidate B:** Candidate A is awaiting conditional access protocol execution, and Candidate B was rejected due to clip discontinuity.

---

## 4. Mandatory Safety Reiteration

This research software prototype is strictly an experimental acoustic machine-learning system. Under no circumstances should this software be connected to or relied upon for physical safety, tactical armed deployment, or automated alarm systems.
