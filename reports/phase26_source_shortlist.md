# PHASE 26 SOURCE SHORTLIST & ACQUISITION GATE AUDIT

> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.**  
> *This experimental acoustic machine-learning software is uncertified and must never be deployed for autonomous emergency dispatch, tactical police response, active-shooter alerting, automated lockdown or evacuation, or life-critical physical security. Use legally obtained recordings and safe audio playback only. Live-fire testing and hazardous acoustic experiments are strictly prohibited.*

---

## 1. Executive Summary & Acquisition Mandate

Phase 26 investigated candidate external acoustic soundscape repositories to acquire up to 20 additional hours of eligible, continuous urban negative-background audio.

In strict adherence to the project's scientific integrity principles:
1. **Target, Not a Quota:** The 20-hour acquisition target is an aspirational research milestone. Eligibility standards (unbroken continuous field recording, verified negative status, authentic urban clutter) are never relaxed to force exposure totals.
2. **Prohibition of Synthetic Manipulation:** Artificially concatenating discrete clips, looping audio, or fabricating synthetic soundscapes is strictly forbidden.
3. **Transparent Reporting:** If candidate sources are gated by access controls or disqualify on continuity grounds, the limitation is documented honestly with zero exposure inflation.

---

## 2. Comprehensive Candidate Evaluation Matrix

| Source ID | Repository Name | Primary Platform | Geographic Origin | Format & Audio Duration | Continuity Status | Negative Evidence | License | Disposition Status |
|---|---|---|---|---|---|---|---|---|
| **`SRC-ZENODO-7493820`** | RPISOUND Continuous Logger | Zenodo | Bristol & Somerset, UK | WAV, 30–60 min streams | Unbroken continuous | Verified environmental non-ballistic | CC BY 4.0 | **ACQUIRED_AND_ELIGIBLE** (Audited) |
| **`SRC-ZENODO-3938837`** | Chew Magna Ambient Survey | Zenodo | Somerset, UK | WAV, 35 min continuous | Unbroken continuous | Verified rural aquatic non-ballistic | CC BY 4.0 | **ACQUIRED_AND_ELIGIBLE** (Audited) |
| **`SRC-ZENODO-18561165`**| Bilbao Old Town Field Survey | Zenodo | Bilbao, Spain | WAV, 5–6 min continuous | Unbroken continuous | Verified municipal non-ballistic | CC BY-NC 4.0| **ACQUIRED_AND_ELIGIBLE** (Audited) |
| **`SRC-AEROSONIC-DB`** | AeroSonicDB (YPAD-0523) | Zenodo (10215080) | Adelaide, Australia | WAV, 6 x 1.0 h streams | Unbroken continuous | Verified civilian urban non-ballistic | CC BY 4.0 | **`CONDITIONAL_ACCESS_PENDING`** |
| **`SRC-ISD-URBAN`** | International Soundscape DB | Zenodo (4459422) | Multi-city (Global) | WAV, 30-second clips | Segmented survey clips | Ambient public spaces | CC BY 4.0 | **`REJECTED`** (Discrete 30s clips) |
| **`SRC-IHTAPARK`** | IHTApark Virtual Acoustics | Zenodo | Aachen, Germany | WAV, 10–20 min | Short survey sessions | Calibrated park background | CC BY 4.0 | **`CONDITIONAL_ACCESS_PENDING`** |
| **`SRC-UNIV-COLLAB`** | Academic Research Testbeds | Bilateral Request | University Sensor Beds | Continuous WAV | Subject to Agreement | Institutional verification | Data Use Agreement| **`CONDITIONAL_ACCESS_PENDING`** |
| **`SRC-LOUISVILLE-OPEN`**| Louisville Metro Open Data | Portal | Louisville, KY, USA | Tabular CSV / GIS | Tabular metadata only | N/A (Zero audio published) | Public Domain | **`REJECTED`** (Tabular only) |
| **`SRC-CHICAGO-OPEN`** | Chicago Data Portal | Portal | Chicago, IL, USA | Tabular CSV / GIS | Tabular metadata only | N/A (Zero audio published) | Public Domain | **`REJECTED`** (Tabular only) |
| **`SRC-SONYC-UST-V1`** | SONYC Urban Sound Tagging | Zenodo / NYU | New York City, USA | WAV, 10-second clips | Segmented snippets | Acoustic scene labels | CC BY 4.0 | **`REJECTED`** (Segmented clips) |
| **`SRC-TAU-DCASE-2020`**| TAU Urban Acoustic Scenes | Zenodo / TAU | 10 European Cities | WAV, 10-second clips | Segmented snippets | Acoustic scene labels | Custom Research| **`REJECTED`** (Segmented clips) |
| **`SRC-HISTORICAL-SYNTH`**| Phase 7/8 Synthetic Overlays | Internal | Simulated Lab | WAV, 6 x 1.0 h streams | Synthetic overlay | Unverified negative status | Internal | **`REJECTED`** (Synthetic overlay) |

---

## 3. Detailed Audit Outcomes for Priority Candidates

### 3.1 Candidate A: AeroSonicDB (YPAD-0523)
- **Investigation Outcome:** The dataset possesses legitimate unbroken 1-hour urban environmental recordings ($6.0\text{ gross hours}$) and a permissive CC BY 4.0 license.
- **Acquisition Gate Blocker:** Programmatic download attempts via Zenodo file endpoints returned **HTTP 403 Forbidden** due to automated Cloudflare anti-bot edge protection. Under behavioral guidelines, automated agents must not attempt to evade or bypass anti-bot challenges.
- **Classification:** **`CONDITIONAL_ACCESS_PENDING`**. The files cannot be acquired through unattended scripts; manual browser download by human operators or registered token access is required.

### 3.2 Candidate B: International Soundscape Database (ISD)
- **Investigation Outcome:** Direct inspection of the primary repository (Mitchell et al., Zenodo 4459422 / 5578703) revealed that ISD consists of **30-second discrete binaural audio recordings** tied to pedestrian survey questionnaires.
- **Continuity Disqualification:** Splicing or concatenating discrete short clips is strictly prohibited by project continuity rules.
- **Classification:** **`REJECTED`** for the primary continuous negative-exposure benchmark.

---

## 4. Exposure Accounting & Honest Reporting

Because Candidate A is gated by remote host anti-bot access controls and Candidate B is disqualified on continuity grounds, **zero new eligible continuous hours were ingested during Phase 26**.

In accordance with Phase 26 directives:
- Previously audited Phase 23–25 exposure: **6.6460 gross hours** (6.6149 eligible hours for Phase 14).
- New Phase 26 gross exposure: **0.0000 hours** (0.00 s).
- Cumulative gross exposure: **6.6460 hours**.
- Shortfall against 20-hour expansion target: **20.0000 hours**.
- Cumulative shortfall against 50-hour aspirational milestone: **43.3540 hours**.

Audio was not fabricated, looped, or synthetically padded.

