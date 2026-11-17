# Phase 24: Municipal & Research Acoustic Source Shortlist
## Legal Access Gate, Sourcing Verification & Municipal Repository Audit

**Document ID:** `REPORT-PHASE24-SHORTLIST-001`  
**Phase:** 24 (Municipal Audio Acquisition & False-Alert Rate Audit)  
**Date:** November 2026  
**Status:** AUDITED SHORTLIST & ACQUISITION DECISIONS  

---

### MANDATORY SAFETY DESIGNATION
> [!CAUTION]
> **RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.**  
> This experimental acoustic machine-learning system is uncertified and must never be deployed for autonomous emergency dispatch, tactical police response, active-shooter alerting, automated lockdown or evacuation, or life-critical physical security. Use legally obtained recordings and safe audio playback only. Live-fire testing and hazardous acoustic experiments are strictly prohibited.

---

## 1. Executive Summary & Audit Mandate

Phase 24 investigates municipal open-data portals and academic acoustic repositories to evaluate candidate sources of continuous urban background audio. In strict compliance with research governance:
- **No Synthetic Splicing:** Splicing short clips into pseudo-continuous streams remains strictly prohibited due to track-boundary transient artifacts (proven in Phase 15 and Phase 16).
- **No Unauthorized Surveillance Scraping:** Municipal portals with open dashboards must not be accessed via unauthorized scraping or credential bypass.
- **Strict Distinction Between Metadata and Raw Audio:** Portals publishing GIS incident coordinates or tabular crime records must not be conflated with raw continuous audio archives.

---

## 2. Municipal Candidate Repository Forensic Audit

### 2.1 Louisville Metro Open Data Portal (`data.louisvilleky.gov`)
- **Official Identity:** Louisville Metro Government Open Data / Louisville Metro Police Department (LMPD) GIS Services.
- **Actual Availability of Audio:** **ZERO RAW AUDIO.** The portal publishes tabular CSV and Esri REST FeatureServices containing incident date/time, block-level address, beat/division, and round counts.
- **Legal & Contractual Barriers:** Raw sensor audio streams recorded by commercial acoustic gunshot detection systems (ShotSpotter / SoundThinking) are contractually proprietary to the vendor and protected under municipal wiretap/surveillance privacy restrictions.
- **Acquisition Decision:** **REJECT** (No raw audio available; tabular metadata only).

### 2.2 City of Chicago Data Portal (`data.cityofchicago.org`)
- **Official Identity:** City of Chicago Open Data / Chicago Police Department (CPD).
- **Actual Availability of Audio:** **ZERO RAW CONTINUOUS AUDIO.** Chicago Open Data hosts the *Gun Violence Dashboard* and *Violence Reduction Dashboard*, which track ShotSpotter incident timestamps and ward-level counts.
- **Prior Dataset Overlap:** A tiny public sample of isolated 4-second incident snippets released via academic discovery (Chicago District 5 & 7, Incident 556267 and Request 4072698) was previously audited in Phase 7 and Phase 20. Neither the city portal nor the open repository distributes continuous multi-hour environmental background streams.
- **Acquisition Decision:** **REJECT** (No raw continuous audio available).

### 2.3 SONYC Urban Sound Tagging (SONYC-UST V1 & V2 - Zenodo 3338310 / 3966543)
- **Official Identity:** NYU Center for Urban Science and Progress (CUSP) & Music and Audio Research Lab (MARL).
- **Actual Availability of Audio:** ~18,510 files downloadable via Zenodo under CC BY 4.0.
- **Continuity Structure:** **STRICTLY DISCRETE 10-SECOND CLIPS.** SONYC sensors recorded isolated 10-second snippets at pseudo-random intervals to monitor noise pollution while avoiding continuous eavesdropping. Splicing these clips together introduces 18,509 artificial boundaries.
- **Acquisition Decision:** **REJECT for Continuous Benchmark** (Pre-segmented discrete snippets).

### 2.4 TAU Urban Acoustic Scenes 2019/2020/2022 (DCASE Task 1 - Zenodo 2589280 / 6582075)
- **Official Identity:** Tampere University Audio Research Group / DCASE Consortium.
- **Continuity Structure:** **STRICTLY DISCRETE 10-SECOND CLIPS.** Raw field sessions were pre-segmented into 10-second segments for challenge classification.
- **Acquisition Decision:** **REJECT for Continuous Benchmark** (Pre-segmented discrete snippets).

---

## 3. Academic & Environmental Continuous Repository Audit

| # | Candidate Repository Name | Official Repository / Access Mechanism | License & Permitted Use | Format & Sample Rate | Continuity Structure | Approx. Usable Duration | Geographic & Campaign Context | Storage Estimate | Main Technical & Legal Limitations | Acquisition Decision |
|---|---|---|---|---|---|---|---|---|---|---|
| **1** | **RPi Sound Logger Environmental Suite** | Zenodo Record 7493820 | CC BY 4.0 | 16-bit PCM WAV, 16 kHz mono | **UNBROKEN NATURAL CONTINUOUS** (30 to 60 min continuous) | **5.500 Hours** (10 streams) | Industrial, transit, and public spaces in the United Kingdom | ~650 MB | Verified continuous baseline; zero gunshot annotations; fully characterized. | **ACCEPT (Primary Benchmark)** |
| **2** | **Chew Magna Reservoir Soundscape** | Zenodo Record 3938837 | CC BY 4.0 | 16-bit PCM WAV, 16 kHz mono | **UNBROKEN NATURAL CONTINUOUS** (35 min continuous) | **0.583 Hours** (1 stream) | Rural aquatic and weather background, Somerset, UK | ~70 MB | Verified continuous ecological background; excellent natural distractor suite. | **ACCEPT (Primary Benchmark)** |
| **3** | **Bilbao Old Town Urban Soundscape** | Zenodo Record 18716205 / 18561165 | CC BY 4.0 | 24-bit PCM WAV, 44.1 kHz stereo | **UNBROKEN NATURAL CONTINUOUS** (30 min to 3 hr sessions) | **0.563 Hours** (6 standardized streams) | Bilbao Old Town, Spain (plazas, walkways, arcades, terraces) | ~330 MB (Standardized) | Multi-point urban field survey; exterior/interior pedestrian soundscapes. | **ACCEPT (Primary Benchmark)** |
| **4** | **Historical Phase 7 & 8 Continuous Streams** | Internal Research Archive (`phase7_independent_test`, `phase8_final_eval`) | Research Internal Archive | 16-bit PCM WAV, 16 kHz mono | **SYNTHETIC NOISE OVERLAY ON SILENCE** (1-hour blocks) | **6.000 Hours** (6 streams) | Synthetic laboratory assembly (ESC-50 distractor classes on silence) | ~690 MB | Lacks natural continuous background noise floor; intermittent zero-amplitude gaps. | **REJECT for Primary Benchmark; RETAIN as Secondary Exploratory Corpus** |
| **5** | **Louisville Metro Open Data Portal** | Louisville Metro GIS Portal (`data.louisvilleky.gov`) | Public Domain (Metadata) | CSV / GeoJSON Tabular | **NO AUDIO AVAILABLE** | **0.000 Hours** | Louisville, KY, USA | 0 MB | Distributes tabular crime/dispatch logs only. No raw sensor audio files. | **REJECT** |
| **6** | **City of Chicago Data Portal** | Chicago Data Portal (`data.cityofchicago.org`) | Public Domain (Metadata) | CSV / Web Dashboard | **NO AUDIO AVAILABLE** | **0.000 Hours** | Chicago, IL, USA | 0 MB | Distributes ShotSpotter incident logs only. No raw continuous audio streams. | **REJECT** |
| **7** | **SONYC Urban Sound Tagging (SONYC-UST V2)** | Zenodo Record 3966543 | CC BY 4.0 | 16-bit WAV, 44.1 kHz mono | **DISCRETE 10-SECOND CLIPS** (18,510 files) | **0.000 Hours Continuous** | Manhattan & Brooklyn, New York City, NY | ~65 GB | Discrete 10s snippets; concatenation creates boundary artifacts. | **REJECT** |
| **8** | **TAU Urban Acoustic Scenes 2022 (DCASE Task 1)** | Zenodo Record 6582075 | CC BY 4.0 | 24-bit WAV, 48 kHz binaural | **DISCRETE 10-SECOND CLIPS** (14,400 files) | **0.000 Hours Continuous** | 10 European cities | ~45 GB | Pre-segmented into 10s segments for classification challenges. | **REJECT** |
| **9** | **AeroSonicDB** | Zenodo Record 10631671 | CC BY 4.0 | 16-bit WAV, 44.1 kHz | Continuous environmental recordings near airports | ~12.0 Hours | Berlin, Germany | ~18 GB | Contains tagged commercial aircraft flyovers; requires flight masking. | **CONDITIONAL** |
| **10** | **Urban Soundscapes of the World** | Zenodo Record 4776092 | CC BY 4.0 | 24-bit WAV, 48 kHz ambisonics | Continuous soundscapes (10 to 30 min per session) | ~20.0 Hours | Montreal, Berlin, Hong Kong, London | > 60 GB | Multichannel ambisonics; excessive disk storage overhead (>60 GB). | **CONDITIONAL** |

---

## 4. Final Acquisition Decisions & Evidence Base Allocation

1. **Primary Verified-Negative Continuous Benchmark:**  
   - 17 unbroken, non-spliced natural continuous streams.
   - 6.646 gross hours (23,925.58 seconds).
   - 3 independent European campaigns (UK Industrial, Chew Magna, and Bilbao Old Town).
   - 100% verified negative with zero firearms discharges.
2. **Secondary Exploratory Continuous Benchmark:**  
   - 6 synthetic overlay streams from Phase 7 and Phase 8 (6.000 hours, 21,600.00 seconds).
   - Retained strictly for secondary diagnostic stress testing; excluded from the primary natural negative exposure denominator.
3. **Target Shortfall Justification:**  
   The primary exposure of 6.646 hours reflects the total verified volume of natural continuous urban audio available without downloading multi-gigabyte files under storage limits or violating DSP continuity standards by concatenating 10-second SONYC clips.

---

*Authored by Principal Acoustic ML Research Engineer & Data Provenance Auditor.*  
*Antigravity Gunshot Detection Research Consortium — Phase 24.*

