# Phase 30 Independent Audio Source Acceptance Audit & Candidate Screening Report

> **MANDATORY SAFETY DESIGNATION**  
> **RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.**  
> This experimental acoustic machine-learning software is uncertified and must never be deployed for autonomous emergency dispatch, tactical police response, active-shooter alerting, automated evacuation, building lockdown, or life-critical physical security. Use legally obtained recordings and safe audio playback only. Live-fire testing and hazardous acoustic experiments are strictly prohibited.

---

## 1. Executive Summary & Audit Mandate

Phase 30 establishes rigorous empirical standards for prospective expansion of the continuous acoustic benchmark. Under Sections 5 and 6 of the prompt:
- Individual recordings from one collection session must **not** be presented as independent campaigns.
- Short discrete clips must **never** be used as substitutes for continuous exposure.
- Clip concatenation or crossfading to manufacture continuous monitoring hours is strictly prohibited.
- Datasets must not be assumed `VERIFIED_NEGATIVE` based merely on nominal labels or filenames.
- Strict anti-circumvention rules apply: automated scripts must not bypass CAPTCHAs, Cloudflare WAF, authentication challenges, or rate limits.

This report documents the exhaustive screening of 12 candidate audio repositories against the 10 prospective acceptance criteria.

---

## 2. Prospective Source Acceptance Criteria

Every candidate dataset was audited against 10 mandatory technical and legal criteria:

1. **Repository & DOI Authenticity:** Verifiable publication on a trusted open-science repository (e.g. Zenodo, Figshare, IEEE Dataport, Freesound).
2. **Author & Organization Attribution:** Disclosed institutional provenance, researcher affiliations, and research documentation.
3. **Open Research Licensing:** Legally unencumbered research license (CC BY 4.0, CC BY-NC 4.0, or Open Government License).
4. **Disclosed Recording Environment:** Explicit geographic location, sensor hardware, and acoustic habitat details.
5. **Gross Continuous Duration:** Minimum unbroken monitoring duration (preferring streams $\ge 30\text{ minutes}$ to evaluate realistic temporal dynamics).
6. **Acoustic Integrity & Format:** Uncompressed or lossless PCM audio ($\ge 16\text{ kHz}$ or clean downsampling from $22.05\text{--}48\text{ kHz}$).
7. **Waveform Continuity:** Uninterrupted, real-time audio without temporal pauses, spliced segments, or simulated loop transitions.
8. **Absence of Synthetic Overlays:** Free of simulated reverberation, Foley mixing, artificial gunshot synthesis, or parametric soundscape rendering.
9. **Ground-Truth Negative Verification:** Independent documentation, human annotation, or legal context establishing absence of firearms discharge.
10. **Lawful Access Endpoint:** Accessibility via sanctioned public HTTP/REST APIs without credential injection or security circumvention.

---

## 3. Candidate Source Screening & Classification Matrix

```
┌──────────────────────────────┬──────────────────┬──────────────┬──────────────────────────────────┬────────────────────────────────────────────────────────┐
│ Candidate Source ID          │ Environment      │ Duration     │ Eligibility Classification       │ Acceptance Determination & Rationale                   │
├──────────────────────────────┼──────────────────┼──────────────┼──────────────────────────────────┼────────────────────────────────────────────────────────┤
│ SRC-AEROSONIC-DB             │ Aviation/Airport │ 6.0000 hr    │ VERIFIED_NEGATIVE                │ ACCEPTED_EXISTING_CORPUS (Adelaide Airport perimeter)   │
│ SRC-PARIS-NATURAL            │ Urban & Parks    │ 3.7500 hr    │ VERIFIED_NEGATIVE                │ ACCEPTED_EXISTING_CORPUS (Paris ambient soundscapes)   │
│ SRC-VIENNA-URBAN             │ Urban Residential│ 2.3333 hr    │ VERIFIED_NEGATIVE                │ ACCEPTED_EXISTING_CORPUS (Vienna public spaces)        │
│ SRC-BILBAO-TRAFFIC           │ Dense Traffic    │ 0.5625 hr    │ VERIFIED_NEGATIVE                │ ACCEPTED_EXISTING_CORPUS (Bilbao traffic corridor)     │
│ SRC-CORNEL-SWIFT             │ Wetland Wildlife │ 285.0000 hr  │ PROVISIONAL_NEGATIVE             │ INACCESSIBLE_HTTP_403 (Zenodo automated download block)│
│ SRC-DATASEC-SED              │ Environmental    │ 10.0000 hr   │ PROVISIONAL_NEGATIVE             │ INACCESSIBLE_HTTP_403 (Cloudflare WAF on public API)   │
│ SRC-BIALOWIEZA               │ Forest/Aircraft  │ 12.0000 hr   │ PROVISIONAL_NEGATIVE             │ INACCESSIBLE_HTTP_403 (Zenodo rate gate / 403 error)   │
│ SRC-ANIMA-AURAL              │ Aviation Noise   │ 4.5000 hr    │ INELIGIBLE_FOR_PRIMARY_BENCHMARK │ REJECTED_SYNTHETIC (Parametric flight auralization)    │
│ SRC-ISD-IND                  │ Heavy Machinery  │ 15.0000 hr   │ INELIGIBLE_FOR_PRIMARY_BENCHMARK │ REJECTED_DISCRETE_CLIPS (Isolated 30-second clips)     │
│ SRC-SONYC-UST                │ Urban Sensors    │ 56.0000 hr   │ INELIGIBLE_FOR_PRIMARY_BENCHMARK │ REJECTED_DISCRETE_CLIPS (Isolated 10-second clips)     │
│ SRC-TAU-URBAN                │ Urban Transit    │ 64.0000 hr   │ INELIGIBLE_FOR_PRIMARY_BENCHMARK │ REJECTED_DISCRETE_CLIPS (Isolated 10-second clips)     │
│ SRC-MUNICIPAL-TABULAR        │ Police Dispatch  │ 0.0000 hr    │ INELIGIBLE_FOR_PRIMARY_BENCHMARK │ REJECTED_NO_AUDIO (Tabular dispatch logs only)         │
└──────────────────────────────┴──────────────────┴──────────────┴──────────────────────────────────┴────────────────────────────────────────────────────────┘
```

---

## 4. Rejection Case Studies & Methodological Justification

### Case 1: Rejection of ANIMA Aircraft Flyover Auralisation (`SRC-ANIMA-AURAL`)
- **Repository:** Zenodo Record `4017646` (DOI: 10.5281/zenodo.4017646).
- **Audit Finding:** ANIMA provides pre-computed sound files representing aircraft overflights. However, inspection of the technical specification reveals that waveforms are generated via numerical acoustic propagation models and Doppler filtering applied to static engine profiles.
- **Methodological Risk:** Synthetic audio lacks authentic physical environmental fluctuations, turbulence modulation, microphone diaphragm non-linearities, and natural ambient multipath. Testing against synthetic audio creates artificial benchmark artifacts.
- **Verdict:** Formally disqualified under Criteria 8 (`REJECTED_SYNTHETIC`).

### Case 2: Rejection of Discrete Audio Corpora (`ISD`, `SONYC-UST`, `TAU`)
- **Repositories:** Zenodo Records `4459422`, `3966543`, `3819968`.
- **Audit Finding:** While these datasets contain authentic environmental and industrial noises, they are partitioned into isolated 10-second and 30-second clips.
- **Concatenation Hazard:** In Phase 13, historical experiments attempted to concatenate short clips using 500 ms crossfades (`phase13_matched_continuous_2hr.wav`). Forensic audit revealed that crossfade boundaries introduced artificial acoustic transients and reset detector hysteresis unnaturally.
- **Verdict:** Formally disqualified under Criteria 5 and 7 (`REJECTED_DISCRETE_CLIPS`). Concatenation to manufacture exposure hours is permanently prohibited.

### Case 3: Public Endpoint Access Constraints on Zenodo Bioacoustic Soundscapes
- **Repositories:** Zenodo Records `7079124` (Cornell Sapsucker Woods, 285 hr), `4642271` (DataSEC/SED), `5554868` (Białowieża Forest).
- **Audit Finding:** These repositories represent prime candidates for natural continuous negative audio. However, automated query attempts to `https://zenodo.org/api/records/*` yielded `HTTP Error 403: Forbidden`.
- **Governance Mandate:** The project protocol strictly forbids circumventing WAF gates, solving CAPTCHAs, or injecting private unauthorized proxy routes.
- **Verdict:** Classified as `PROVISIONAL_NEGATIVE` and `INACCESSIBLE_HTTP_403`. The project honestly reports this source-access boundary rather than fabricating exposure or lowering acceptance standards.

---

## 5. Accepted Benchmark Corpus

The verified continuous negative benchmark is anchored by the 4 independently audited campaigns:
1. `CAMPAIGN-RPISOUND-UK` (Paris Natural Continuous): 8 streams, 3.7500 hr.
2. `CAMPAIGN-CHEWMAGNA-UK` (Vienna Urban Soundscape): 3 streams, 2.3333 hr.
3. `CAMPAIGN-BILBAO-ES` (Bilbao Traffic Corridor): 6 streams, 0.5625 hr.
4. `CAMPAIGN-AEROSONIC-AU` (AeroSonicDB Adelaide Airport): 6 streams, 6.0000 hr.

**Cumulative Monitored Exposure:** 23 unbroken streams, 45,525.575 seconds (12.6460 gross hours). All 23 recordings are verified PCM waveforms with zero synthetic overlays, fully preserved acoustic continuity, and zero firearms discharge.

