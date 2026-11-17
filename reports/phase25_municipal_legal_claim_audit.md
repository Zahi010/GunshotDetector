# PHASE 25 FORENSIC AUDIT OF MUNICIPAL OPEN DATA PORTAL POLICIES & LEGAL CLAIMS

> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.**  
> *This experimental acoustic machine-learning software is uncertified and must never be deployed for autonomous emergency dispatch, tactical police response, active-shooter alerting, automated lockdown or evacuation, or life-critical physical security. Use legally obtained recordings and safe audio playback only. Live-fire testing and hazardous acoustic experiments are strictly prohibited.*

---

## 1. Executive Summary & Audit Mandate

In Phase 24, investigations into public municipal data portals (**City of Louisville Open Data** and **City of Chicago Data Portal**) concluded that while tabular GIS/CAD metadata records are publicly accessible, raw continuous acoustic audio feeds are not downloadable.

However, Phase 24 asserted that audio feeds were withheld *"under Federal Wiretap Act (18 U.S.C. § 2510) compliance and commercial proprietary vendor contracts."*

Phase 25 Workstream A mandates a forensic audit of this claim, strictly disaggregating observed empirical evidence from legal interpretation, eliminating unsupported assertions regarding universal statutory requirements, and qualifying statements in accordance with established evidentiary standards.

---

## 2. Five-Tier Evidentiary Categorization

To maintain strict scientific and legal objectivity, all evidence regarding municipal acoustic audio availability is classified into five formal evidentiary tiers:

```
+---------------------------------------------------------------------------------------------------+
| FIVE-TIER EVIDENTIARY AUDIT TAXONOMY                                                              |
+===================================================================================================+
| TIER 1: DIRECTLY OBSERVED PORTAL BEHAVIOR                                                         |
| Facts directly verified by inspecting the live web portals:                                       |
| - Louisville Metro Open Data (data.louisvilleky.gov) provides downloadable CSV and GeoJSON        |
|   tables containing incident identifiers, timestamps, block-level coordinates, and round counts.  |
| - Chicago Data Portal (data.cityofchicago.org) provides tabular CSV records under the title       |
|   "Violence Reduction - ShotSpotter Alerts" with district, beat, and timestamp fields.            |
| - Neither portal displays a link, API endpoint, or bucket to download raw acoustic WAV/FLAC files.|
+---------------------------------------------------------------------------------------------------+
| TIER 2: EXPLICIT STATEMENTS FROM MUNICIPAL AGENCIES                                               |
| Public notices and metadata documentation published by the municipalities:                        |
| - Portal metadata notes specify that datasets represent dispatch and CAD log summaries.           |
| - Municipalities do not publish statements on their portals explaining why acoustic waveforms are |
|   not included in open data catalogs.                                                             |
+---------------------------------------------------------------------------------------------------+
| TIER 3: PUBLISHED VENDOR CONTRACT PROVISIONS                                                      |
| Publicly accessible municipal procurement agreements with acoustic detection vendors:             |
| - Master service agreements between municipalities and commercial acoustic detection vendors      |
|   (e.g., ShotSpotter / SoundThinking) designate sensor hardware, raw acoustic telemetry, and     |
|   acoustic classification algorithms as proprietary vendor trade secrets.                         |
| - Contracts typically grant municipalities a license to incident notifications and CAD metadata,   |
|   while audio snippets are restricted to forensic court testimony or active criminal investigation.|
+---------------------------------------------------------------------------------------------------+
| TIER 4: OFFICIALLY DOCUMENTED LEGAL RESTRICTIONS                                                  |
| Statutory frameworks and judicial rulings:                                                        |
| - Title III of the Omnibus Crime Control and Safe Streets Act of 1968 (Federal Wiretap Act,        |
|   18 U.S.C. § 2510 et seq.) regulates interception of oral communications where there is a       |
|   reasonable expectation of privacy.                                                              |
| - Various state electronic surveillance statutes impose two-party consent requirements.           |
| - However, no public court ruling or official statutory text universally mandates that all       |
|   outdoor ambient street sound recordings must be withheld from research datasets.                |
+---------------------------------------------------------------------------------------------------+
| TIER 5: MODEL OR RESEARCHER INTERPRETATION                                                        |
| Inferences previously drawn by project researchers:                                               |
| - Inferring that the Federal Wiretap Act is the direct, proximate legal cause for why Louisville  |
|   or Chicago does not host downloadable continuous audio is a researcher hypothesis, not a        |
|   directly observed fact.                                                                         |
+---------------------------------------------------------------------------------------------------+
```

---

## 3. Discrepancy Reconciliation & Accurate Qualification

### 3.1 The Flaw in Naive Legal Attribution
A lack of downloadable audio on an open data portal does not, by itself, establish the underlying legal or administrative rationale. Municipal open data catalogs omit thousands of raw operational data streams (e.g., raw CCTV video feeds, police radio raw baseband, raw traffic radar Doppler returns) due to:
1. Massive storage and egress bandwidth costs.
2. Proprietary vendor software architecture.
3. Lack of public interest in terabytes of continuous ambient noise.
4. Privacy and policy considerations.

Attributing the absence of raw audio exclusively to the Federal Wiretap Act was an **over-extension of researcher interpretation** that conflated plausible legal risk factors with verified municipal policy decisions.

### 3.2 Canonical Qualified Statement
For all future technical reports, publications, and release manifests, the project adopts the following standardized, legally precise qualification:

> *"The inspected municipal open data portals (City of Louisville and City of Chicago) publish tabular incident logs and geospatial coordinates, but do not provide downloadable raw acoustic waveforms. The specific administrative, legal, or commercial reasons for non-publication were not definitively established by the available portal evidence."*

---

## 4. Legal Disclaimer

Nothing in this document, the project codebase, or associated reports constitutes legal advice. The discussion of electronic surveillance statutes represents an audit of research hypotheses regarding data availability and does not express an authoritative legal conclusion.

---

## 5. Mandatory Safety Reiteration

This audit confirms that municipal open data portals cannot serve as an open source for continuous audio benchmarks. The software prototype remains strictly non-operational and must never be deployed for life-safety or tactical emergency response.

