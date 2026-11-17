# PHASE 26 NEGATIVE-LABEL & CONTINUOUS AUDIO ELIGIBILITY REPORT

> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.**  
> *This experimental acoustic machine-learning software is uncertified and must never be deployed for autonomous emergency dispatch, tactical police response, active-shooter alerting, automated lockdown or evacuation, or life-critical physical security. Use legally obtained recordings and safe audio playback only. Live-fire testing and hazardous acoustic experiments are strictly prohibited.*

---

## 1. Executive Summary & Governance Mandate

The primary objective of continuous negative-audio evaluation is to establish empirical false-alarm rates ($\text{FAR}$) under authentic environmental acoustic exposure.

However, an acoustic machine-learning system can only establish valid negative exposure if two criteria are met simultaneously:
1. **Verifiable Temporal Continuity:** Audio must represent an unbroken continuous physical field recording without synthetic concatenation, loop repetitions, or spliced transitions.
2. **Defensible Negative-Label Evidence:** There must be positive evidence that the recording environment was free from live-fire ballistic discharges. The mere absence of a gunshot annotation in an uncurated database is insufficient to certify an interval as negative.

Phase 26 evaluated candidate repositories against these dual criteria.

---

## 2. Five-Tier Eligibility Classification Framework

All audio streams evaluated or cataloged in Phase 26 are classified under one of five pre-registered eligibility designations:

```
+---------------------------------------------------------------------------------------------------+
| FIVE-TIER ELIGIBILITY TAXONOMY                                                                    |
+===================================================================================================+
| 1. VERIFIED_NEGATIVE (Primary Benchmark Eligible)                                                 |
|    - Unbroken continuous physical field recording.                                                |
|    - Provenance from verified civilian, rural, or industrial environments with zero live-fire     |
|      activities (e.g. university campuses, public plazas, municipal water reservoirs).             |
|    - Independent manual listening audit confirms absence of target gunfire.                      |
|    - Eligible to contribute to Primary Continuous Negative Exposure.                              |
+---------------------------------------------------------------------------------------------------+
| 2. POTENTIALLY_NEGATIVE_UNVERIFIED (Excluded from Primary Benchmark)                              |
|    - Audio lacks target annotations, but geographic or operational provenance cannot rule out    |
|      distant firearms, hunting, or explosive activities.                                          |
|    - Synthetic overlays of environmental sounds onto silence (e.g. Phase 7/8 synthetic streams).   |
|    - Ineligible for primary benchmark; retained for exploratory analysis only.                    |
+---------------------------------------------------------------------------------------------------+
| 3. EVENT_CONTAINING (Target Dataset)                                                              |
|    - Audio known to contain physical gunshot discharges or ballistic shockwaves.                  |
|    - Used for positive recall evaluation (e.g. Phase 20 Pittsburgh live-fire dataset).            |
|    - Excluded entirely from negative exposure calculation.                                        |
+---------------------------------------------------------------------------------------------------+
| 4. AMBIGUOUS (Excluded)                                                                           |
|    - Audio containing unidentifiable high-energy impulsive transients obscured by extreme clipping|
|      or acoustic distortion where gunfire cannot be definitively confirmed or ruled out.         |
|    - Excluded from exposure to prevent false-alarm distortion.                                    |
+---------------------------------------------------------------------------------------------------+
| 5. INVALID (Disqualified)                                                                        |
|    - Discrete short clips (< 10 minutes), artificially concatenated audio, or corrupt files.      |
|    - Disqualified from continuous monitoring benchmarks.                                         |
+---------------------------------------------------------------------------------------------------+
```

---

## 3. Audit of Candidate Sources Against Eligibility Criteria

### 3.1 Candidate A: AeroSonicDB Continuous Urban Set
- **Continuity Assessment:** **ELIGIBLE**. Published metadata documents six 1-hour unbroken continuous recordings ($6.0\text{ gross hours}$) recorded on outdoor residential masts.
- **Negative-Label Evidence:** **ELIGIBLE**. Recorded in an established civilian residential neighborhood of Adelaide, South Australia under Australian civil aviation monitoring. Civilian airspace and residential zoning confirm absence of live-fire munitions.
- **Environmental Clutter:** Audio contains low-altitude jet and turboprop aircraft flyovers. In accordance with Phase 26 rules, aircraft noise is treated as a valid environmental distractor, not a disqualifying defect.
- **Acquisition Status:** Gated by remote host HTTP 403 anti-bot controls (`CONDITIONAL_ACCESS_PENDING`).

### 3.2 Candidate B: International Soundscape Database (ISD)
- **Continuity Assessment:** **INVALID / DISQUALIFIED**. The primary archive comprises 30-second discrete binaural clips tied to individual participant questionnaires.
- **Critical Continuity Violation:** Chaining thirty-second snippets together violates the continuity rule by creating artificial boundary transients.
- **Negative-Label Evidence:** Urban public parks and pedestrian promenades; civilian soundscapes.
- **Eligibility Verdict:** Disqualified from primary continuous exposure due to lack of temporal continuity.

---

## 4. Current Primary Benchmark Composition

The primary `VERIFIED_NEGATIVE` continuous benchmark remains composed of the 17 verified unbroken streams established in Phases 16, 17, 23, and 24:

| Campaign Identifier | Region | Acoustic Environment | Streams | Gross Duration | Eligible Duration (P14) | Eligibility Category |
|---|---|---|---|---|---|---|
| `CAMPAIGN-RPISOUND-UK` | Bristol & Somerset, UK | Industrial machinery, rail, arterial highway, university canteen | 10 streams | 5.0000 h | 4.9866 h | **VERIFIED_NEGATIVE** |
| `CAMPAIGN-CHEWMAGNA-UK`| Chew Magna, Somerset, UK | Reservoir lake, aquatic water movement, wind & rain | 1 stream | 0.5833 h | 0.5833 h | **VERIFIED_NEGATIVE** |
| `CAMPAIGN-BILBAO-ES` | Bilbao Old Town, Spain | Public exterior plazas, commercial arcades, terraces, market hall | 6 streams | 1.0627 h | 1.0449 h | **VERIFIED_NEGATIVE** |
| **Total Benchmark** | **3 European Campaigns** | **Urban, Industrial, Transportation, Rural** | **17 streams** | **6.6460 h** | **6.6149 h** | **VERIFIED_NEGATIVE** |

All 17 streams have been independently verified for:
1. Zero gunshot annotations and zero physical munitions discharge.
2. Unbroken temporal continuity without gaps, clipping, or synthetic splicing.
3. Linear PCM16 format at native 16.0 kHz sampling rate.

---

## 5. Mandatory Safety Reiteration

Negative-label verification ensures sound data provenance, but does not render the experimental detector safe for operational use. The system generates 7.7 to 8.5 false alerts per monitoring hour and is strictly uncertified for life-safety or emergency dispatch applications.

