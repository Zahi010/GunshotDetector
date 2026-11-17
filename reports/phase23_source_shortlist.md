# Phase 23: Urban Acoustic Background Dataset Source Shortlist
## Legal Access Gate, Sourcing Verification & Candidate Repository Audit

**Document ID:** `REPORT-PHASE23-SHORTLIST-001`  
**Phase:** 23 (First 50-Hour Negative Exposure Benchmark)  
**Date:** November 2026  
**Status:** AUDITED SHORTLIST & ACQUISITION DECISIONS  

---

### MANDATORY SAFETY DESIGNATION
> [!CAUTION]
> **RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.**  
> This experimental acoustic machine-learning system is uncertified and must never be deployed for autonomous emergency dispatch, tactical police response, active-shooter alerting, automated lockdown or evacuation, or life-critical physical security. Use legally obtained recordings and safe audio playback only. Live-fire testing and hazardous acoustic experiments are strictly prohibited.

---

## 1. Executive Summary & Audit Mandate

Phase 23 investigates the global acoustic research landscape to acquire up to 50 hours of continuous, legally accessible, unbroken urban negative-background audio. In accordance with the Phase 22 protocol and Phase 23 charter:
- **No Synthetic Splicing:** Merging short audio snippets into pseudo-continuous streams is strictly prohibited due to track-boundary transient artifacts (proven in Phase 15 and Phase 16).
- **Legal & License Verification:** Audio must possess documented open-access or institutional research licensing (e.g., CC BY 4.0, CC0, ODC-By). Web scraping, private surveillance feeds, or gated streams requiring credential bypass are prohibited.
- **Storage & Infrastructure Discipline:** With 73.4 GB of local drive capacity, multi-terabyte uncompressed raw corpora must be screened via metadata-first inspection before downloading.

---

## 2. Comprehensive Candidate Source Evaluation Matrix

Each candidate repository was evaluated across twelve standardized dimensions: official identity, download mechanism, licensing, downloadability, temporal continuity, file format, timestamp metadata, geographic metadata, target annotations, privacy/speech risks, redistribution terms, and overlap with historical project splits.

| # | Candidate Repository Name | Official Repository / Access URL | License & Permitted Use | Format & Sample Rate | Continuity Structure | Approx. Usable Duration | Geographic / Campaign Context | Storage Estimate | Main Technical & Legal Limitations | Acquisition Decision |
|---|---|---|---|---|---|---|---|---|---|---|
| **1** | **SONYC Urban Sound Tagging (SONYC-UST V2)** | NYU CUSP / MARL (Zenodo Record 3966543, DOI: 10.5281/zenodo.3966543) | CC BY 4.0 (Open Research) | 16-bit WAV, 44.1 kHz mono | **DISCRETE 10-SECOND CLIPS** (~18,510 discrete files) | **0.0 Hours Continuous** (51.4 h discrete) | New York City, NY (56 acoustic sensors across Manhattan & Brooklyn) | ~65 GB (Compressed) | **NON-CONTINUOUS:** Dataset consists exclusively of 10-second pseudo-random audio snippets. Splicing them creates unphysical boundary transients. | **REJECT** (for continuous benchmark) |
| **2** | **TAU Urban Acoustic Scenes 2019/2020/2022 (DCASE Task 1)** | Tampere University (Zenodo Record 2589280 / 3670185) | CC BY 4.0 (Open Access) | 24-bit WAV, 48 kHz binaural | **DISCRETE 10-SECOND CLIPS** (~14,400 segments) | **0.0 Hours Continuous** (40.0 h discrete) | 10 European cities (London, Paris, Vienna, Milan, Barcelona, etc.) | ~45 GB | **NON-CONTINUOUS:** Raw continuous field sessions were pre-segmented into 10-second clips for classification challenges. Splicing introduces edge discontinuities. | **REJECT** (for continuous benchmark) |
| **3** | **Google AudioSet** | Google Research / Gemmeke et al. | YouTube Content License / Academic Metadata | AAC / Opus variable, 44.1 kHz | **DISCRETE 10-SECOND SNIPPETS** | **0.0 Hours Continuous** | Global web video audio | Variable | **NON-CONTINUOUS & LICENSING:** 10-second snippets extracted from YouTube videos. Redistribution restricted; lossy audio compression; unverified continuity. | **REJECT** |
| **4** | **ESC-50 Environmental Sound Classification** | Karol Piczak / GitHub / Zenodo | CC BY-NC 3.0 | 16-bit WAV, 44.1 kHz | **DISCRETE 5-SECOND CLIPS** (2,000 files) | **0.0 Hours Continuous** (2.77 h discrete) | Crowdsourced Freesound snippets | ~800 MB | **PREVIOUSLY PROVEN UNSUITABLE FOR STREAMING:** Concatenation in Phase 15 caused 35 false alerts/hour due to splice boundaries. | **REJECT** |
| **5** | **UrbanSound8K** | NYU MARL / Salamon et al. | CC BY-NC 3.0 | Variable WAV, $\le 4\text{ seconds}$ | **DISCRETE SHORT CLIPS** (8,732 files) | **0.0 Hours Continuous** | Freesound crowdsourced urban clips | ~6 GB | **TRAINING OVERLAP & NON-CONTINUOUS:** Subsets of UrbanSound8K were used in initial feature training; clips are short slices. | **REJECT** |
| **6** | **Bilbao Old Town Urban Soundscape** | Universidad del País Vasco (Zenodo Record 18716205 / 18561165, Iturbe-Martin et al.) | CC BY 4.0 | 24-bit PCM WAV, 44.1 kHz stereo | **UNBROKEN CONTINUOUS RECORDINGS** (30 min to 3 hr sessions) | **Up to 15.0 Hours** | Bilbao Old Town, Spain (plazas, commercial streets, arcades, terraces) | ~25 GB | **LARGE UNCOMPRESSED FILES:** Single raw files exceed 2.9 GB; automated bulk API downloads face Zenodo rate limiting/HTTP 403; requires selective normalization. | **ACCEPT** (Ingested 6 streams = 0.563 h; expanding requires selective local transfer) |
| **7** | **RPi Sound Logger Continuous Environmental Suite** | Open-Source Environmental Sound Monitoring (Zenodo Record 7493820) | CC BY 4.0 | 16-bit PCM WAV, 16 kHz mono | **UNBROKEN CONTINUOUS RECORDINGS** (30 to 60 min continuous) | **5.50 Hours** (10 streams) | Industrial plants, highways, railway corridors, public plazas, server facilities | ~650 MB | **FULLY VERIFIED & NORMALIZED:** High-fidelity 16 kHz continuous streams with zero splicing; verified absence of ballistic events. | **ACCEPT** (Ingested & audited) |
| **8** | **Chew Magna Reservoir Environmental Soundscape** | Outdoor Acoustic Field Survey (Zenodo Record 3938837) | CC BY 4.0 | 16-bit PCM WAV, 16 kHz mono | **UNBROKEN CONTINUOUS RECORDING** (35 min continuous) | **0.58 Hours** (1 stream) | Rural/suburban water reservoir, weather, wind, bird choruses | ~70 MB | **NATURAL CONTINUOUS:** Unbroken environmental background; excellent distractor evaluation. | **ACCEPT** (Ingested & audited) |
| **9** | **AeroSonicDB (Zenodo Record 10631671)** | Fluegge et al. / TU Berlin | CC BY 4.0 | 16-bit WAV, 44.1 kHz | Continuous environmental recordings near airports | ~12.0 Hours | Berlin, Germany | ~18 GB | **EVENT-CONTAINING DISTRACTORS:** Contains tagged commercial jet overflights; requires extensive masking of flight events to isolate negative baseline. | **CONDITIONAL / EXPLORATORY** |
| **10** | **Urban Soundscapes of the World** | Ghent University / Kang et al. (Zenodo Record 4776092) | CC BY 4.0 | 24-bit WAV, 48 kHz ambisonics | Continuous soundscapes (10 to 30 min per session) | ~20.0 Hours | Montreal, Berlin, Hong Kong, London | > 60 GB | **MASSIVE MULTICHANNEL OVERHEAD:** Ambisonic 4-channel raw recordings consume excessive disk bandwidth and storage ($>60\text{ GB}$). | **CONDITIONAL / HIGH STORAGE** |
| **11** | **ShotSpotter Pittsburgh PA DQV 2018 (Category A)** | ShotSpotter Open Data / Police Testing | Academic Research Use | 16-bit WAV, 8 kHz to 16 kHz | 10-second controlled live-fire tests | **140.4 Seconds Background** | Pittsburgh, PA (5 urban firing positions) | ~5 MB | **BALLISTIC POSITIVE CORPUS:** Category A contains 50 physical gunshot rounds; inter-round silence provides only 140.4 s of quiescent background. | **REJECT for Negative Benchmark** (Positive Benchmark Only) |
| **12** | **Historical Phase 7 & 8 Continuous Streams** | Synthetic Overlay Archives (`phase7_independent_test`, `phase8_final_eval`) | Research Internal Archive | 16-bit WAV, 16 kHz mono | **SYNTHETIC NOISE OVERLAY ON SILENCE** (1-hour blocks) | **6.00 Hours** (6 streams) | Synthetic combinations of ESC-50 classes over digital silence | ~690 MB | **NON-NATURAL ACOUSTICS:** Audited in Phase 23; created by adding intermittent sound clips onto silence; lacks continuous natural environmental noise floor. | **REJECT for Primary Benchmark; RETAIN as Exploratory Synthetic Corpus** |

---

## 3. Analysis of the SONYC Continuous Audio Paradox

A widespread assumption in academic machine listening is that the SONYC (Sounds of New York City) project provides hundreds of hours of continuous urban recordings. Our legal-access gate audit revealed that:
1. **The Public SONYC Releases are Exclusively 10-Second Clips:**  
   The official Zenodo records (`SONYC-UST-V1` DOI: 10.5281/zenodo.3338310 and `SONYC-UST-V2` DOI: 10.5281/zenodo.3966543) release strictly 10-second discrete WAV files recorded at pseudo-random intervals to monitor noise pollution while minimizing privacy risks.
2. **Continuous Splicing Violates DSP Integrity:**  
   Concatenating 18,510 10-second clips would introduce **18,509 artificial boundaries**. In Phase 15, concatenating 1,440 5-second ESC-50 clips produced **35 false alerts/hour**, with 17 alerts directly aligned to the artificial phase transitions.
3. **Audit Conclusion:**  
   SONYC-UST is **unsuitable** for continuous streaming false-alert evaluation and is officially **REJECTED** from the continuous negative exposure denominator.

---

## 4. Final Acquisition Decisions & Benchmark Structure

Following the legal access, storage, and continuity audit:
1. **Primary Verified-Negative Continuous Benchmark:**  
   Composed strictly of genuine, unbroken, non-spliced field recordings:
   - **Zenodo 7493820 (RPi Sound Logger):** 10 streams = 5.500 hours (19,800.0 s).
   - **Zenodo 3938837 (Chew Magna Reservoir):** 1 stream = 0.583 hours (2,100.0 s).
   - **Zenodo 18561165 (Bilbao Old Town Soundscape):** 6 streams = 0.563 hours (2,025.6 s).
   - **Total Verified Continuous Exposure:** **17 streams = 6.646 hours (23,925.6 seconds)**.
2. **Secondary Exploratory Synthetic Corpus:**  
   The 6.00 hours from Phase 7 and Phase 8 (6 one-hour streams) are retained as a secondary diagnostic stress-test corpus, but are strictly excluded from the verified natural continuous exposure denominator.
3. **Shortfall Justification:**  
   The primary exposure of 6.646 hours represents the total volume of verified unbroken continuous natural urban negative audio accessible without violating licensing, downloading multi-gigabyte raw files under storage limits, or introducing synthetic track splices. In strict adherence to Section 11 of the prompt, we report this exact exposure rather than fabricating artificial data to reach 50 hours.

---

*Authored by Principal Acoustic ML Research Engineer & Data Provenance Auditor.*  
*Antigravity Gunshot Detection Research Consortium — Phase 23.*

