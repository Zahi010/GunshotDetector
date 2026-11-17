# PHASE 25 SOURCE SHORTLIST & CANDIDATE REPOSITORY EVALUATION

> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.**  
> *This experimental acoustic machine-learning software is uncertified and must never be deployed for autonomous emergency dispatch, tactical police response, active-shooter alerting, automated lockdown or evacuation, or life-critical physical security. Use legally obtained recordings and safe audio playback only. Live-fire testing and hazardous acoustic experiments are strictly prohibited.*

---

## 1. Executive Summary & Acquisition Strategy

The objective of Phase 25 Workstream B is to identify legally accessible continuous urban background audio recordings from independent campaigns to expand the negative exposure benchmark toward the 20-hour expansion target (cumulative 26.6-hour goal).

In strict adherence to the project's scientific rigor standards:
1. **Target, Not a Quota:** The 20-hour acquisition target is an aspirational research milestone. Eligibility criteria (continuous unbroken recording, verified negative provenance, uncompressed audio) are never weakened.
2. **Prohibition of Synthetic Manipulation:** Artificially concatenating 10-second discrete clips, looping audio, or creating synthetic overlays is strictly prohibited.
3. **Formal Classification:** Candidate sources are evaluated and classified as `ACCEPT`, `CONDITIONAL`, or `REJECT`.

---

## 2. Evaluation of Candidate Audio Repositories

### 2.1 Evaluated Sources Summary Matrix

| Source ID | Repository Name | Primary Platform | Geographic Origin | Format & Duration | Continuity Status | Negative Evidence | License | Disposition |
|---|---|---|---|---|---|---|---|---|
| `SRC-ZENODO-7493820` | RPISOUND Continuous Logger | Zenodo | Bristol & Somerset, UK | WAV, 30–60 min streams | Unbroken continuous | Verified environmental non-ballistic | CC BY 4.0 | **ACCEPT** (Audited) |
| `SRC-ZENODO-3938837` | Chew Magna Ambient Survey | Zenodo | Somerset, UK | WAV, 35 min continuous | Unbroken continuous | Verified rural aquatic non-ballistic | CC BY 4.0 | **ACCEPT** (Audited) |
| `SRC-ZENODO-18561165`| Bilbao Old Town Field Survey | Zenodo | Bilbao, Spain | WAV, 5–6 min continuous | Unbroken continuous | Verified municipal non-ballistic | CC BY-NC 4.0| **ACCEPT** (Audited) |
| `SRC-AEROSONIC-DB` | AeroSonicDB (YPAD-0523) | Zenodo (7976269) | Adelaide, Australia | WAV, 6 x 1.0 h streams | Unbroken continuous | Background urban; contains aircraft events | CC BY 4.0 | **CONDITIONAL** |
| `SRC-ISD-URBAN` | International Soundscape DB | Zenodo | Multi-city (Global) | WAV/FLAC, 5–15 min | Multi-channel sessions | Survey ambient soundscapes | Academic Use | **CONDITIONAL** |
| `SRC-IHTAPARK` | IHTApark Virtual Acoustics | Zenodo | Aachen, Germany | WAV, 10–20 min | Continuous sessions | Calibrated park background | CC BY 4.0 | **CONDITIONAL** |
| `SRC-LOUISVILLE-OPEN`| Louisville Metro Open Data | Portal | Louisville, KY, USA | Tabular CSV / GIS | Tabular metadata only | N/A (Zero audio published) | Public Domain | **REJECT** |
| `SRC-CHICAGO-OPEN` | Chicago Data Portal | Portal | Chicago, IL, USA | Tabular CSV / GIS | Tabular metadata only | N/A (Zero audio published) | Public Domain | **REJECT** |
| `SRC-SONYC-UST-V1` | SONYC Urban Sound Tagging | Zenodo / NYU | New York City, USA | WAV, 10-second clips | Segmented snippets | Acoustic scene labels | CC BY 4.0 | **REJECT** (Segmented) |
| `SRC-TAU-DCASE-2020`| TAU Urban Acoustic Scenes | Zenodo / TAU | 10 European Cities | WAV, 10-second clips | Segmented snippets | Acoustic scene labels | Custom Research| **REJECT** (Segmented) |
| `SRC-UNIV-COLLAB` | Academic Research Collaboration| Bilateral | University Sensor Beds | Continuous WAV | Subject to Agreement | Institutional verification | Data Use Agreement| **CONDITIONAL** |

---

## 3. Deep-Dive Evaluations by Source Category

### 3.1 Accepted Historical Benchmarks (`ACCEPT`)
The three existing European campaigns established in Phases 16, 17, 23, and 24 represent **6.6460 gross hours** across 17 unbroken continuous streams. These streams satisfy all criteria:
- High-resolution uncompressed PCM16 at 16 kHz.
- Documented sensor hardware (Raspberry Pi with MEMS microphones, Zoom H4n Handy Recorder, Sound Devices field recorder).
- Zero firearms discharge annotations and verified civilian recording locations.

### 3.2 Promising Independent Candidates (`CONDITIONAL`)
1. **AeroSonicDB (Zenodo Record 7976269):**
   - **Characteristics:** Six 1-hour continuous audio recordings captured in urban Adelaide, Australia near airport corridors.
   - **Evaluation:** Genuinely continuous and long-duration (6.0 hours). However, the audio contains prominent low-altitude commercial aircraft flyovers annotated with start/end timestamps.
   - **Condition for Ingestion:** To enter the negative gunshot benchmark, aircraft transit intervals must either be evaluated as hard acoustic distractors or precisely excluded via temporal masking to isolate pure urban background. Requires secondary review prior to local ingestion.
2. **International Soundscape Database (ISD / ISO 12913):**
   - **Characteristics:** High-fidelity binaural and ambisonic urban recordings across public plazas, shopping districts, and parks.
   - **Condition for Ingestion:** Recordings are typically 5 to 15 minutes long. Requires channel downmixing to mono and validation that sessions are unbroken.
3. **Academic Collaboration Pathway (`SRC-UNIV-COLLAB`):**
   - **Characteristics:** Bilateral data access requests to university acoustic ecology testbeds (e.g., smart city sensor networks).
   - **Condition for Ingestion:** Execution of institutional Data Use Agreements (DUAs) without collecting private conversations. Formal template drafted in [`reports/phase25_research_data_access_request.md`](file:///e:/gunshot/gunshot/reports/phase25_research_data_access_request.md).

### 3.3 Rejected Portals and Segmented Corpora (`REJECT`)
1. **Municipal Open Data Portals (Louisville, Chicago):**
   - Rejection Reason: Portals publish tabular GIS/CAD dispatch coordinates only. Zero downloadable acoustic audio exists.
2. **SONYC-UST and TAU Urban Acoustic Scenes:**
   - Rejection Reason: These corpora comprise 10-second segmented clips. Stitching or concatenating discrete clips into artificial continuous audio introduces artificial phase discontinuities and spectral onset transients, violating the preregistered continuous validation protocol.

---

## 4. Current Ingestion Status & Scientific Honesty

Because candidate external sources (`AeroSonicDB`, `ISD`) require secondary temporal masking or institutional data use authorization prior to ingestion, **no new continuous audio files were imported into the local active benchmark during Phase 25**.

In accordance with Phase 25 directives:
- Previously audited Phase 23/24 exposure: **6.6460 gross hours** (6.6149 eligible hours for Phase 14).
- New Phase 25 gross exposure: **0.0000 hours** (0.00 s).
- Cumulative gross exposure: **6.6460 hours**.
- Shortfall against 20-hour expansion target: **20.0000 hours**.
- Cumulative shortfall against 50-hour aspirational milestone: **43.3540 hours**.

The limitation is documented transparently without fabricating or looping audio.

