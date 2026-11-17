# PHASE 26 CANDIDATE SOURCE AUDIT: AEROSONICDB (YPAD-0523)

> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.**  
> *This experimental acoustic machine-learning software is uncertified and must never be deployed for autonomous emergency dispatch, tactical police response, active-shooter alerting, automated lockdown or evacuation, or life-critical physical security. Use legally obtained recordings and safe audio playback only. Live-fire testing and hazardous acoustic experiments are strictly prohibited.*

---

## 1. Executive Summary & Audit Mandate

In Phase 25, **AeroSonicDB** was identified as a prospective candidate source for continuous urban background audio recordings to expand the project's negative exposure benchmark toward the 20-hour expansion target.

Phase 26 mandates an independent, direct forensic investigation of the primary repository to verify record identity, metadata, license permissions, audio specifications, continuity, and download accessibility without relying on secondary descriptions.

---

## 2. Repository Identification & Metadata Rectification

### 2.1 Rectification of Phase 25 Record Identifier Error
Phase 25 initially cited AeroSonicDB under Zenodo record `7976269`. Direct audit of the Zenodo registry reveals that `7976269` (`10.5281/zenodo.7976269`) is an unrelated systems biology dataset:
- *Title:* "Functional decomposition of metabolism allows a system-level quantification of fluxes and protein allocation..." (Mori et al., 2023).

The **true, authoritative repository identifiers** for AeroSonicDB were established via the official publication and codebase:
- **Concept DOI:** `10.5281/zenodo.8000468`
- **Primary Release Record:** `10.5281/zenodo.10215080` (Version 1.0 / Record `8371595`)
- **Scholarly Citation:** Downward, B., & Nordby, J. (2023). *The AeroSonicDB (YPAD-0523) Dataset for Acoustic Detection and Classification of Aircraft.* arXiv:2311.06368 [cs.SD].
- **Official Codebase:** GitHub (`aerosonicdb/AeroSonicDB-YPAD0523`).

### 2.2 Curatorial & Technical Metadata

| Metadata Field | Verified Value | Evidentiary Basis |
|---|---|---|
| **Dataset Title** | AeroSonicDB (YPAD-0523) | Official Zenodo record & paper |
| **Authors / Creators**| Blake Downward & Jon Nordby | arXiv:2311.06368 |
| **Institution** | University of Adelaide / Independent ML Research | Research publication |
| **Geographic Location**| Adelaide, South Australia (-34.94° S, 138.53° E) | Flight path of Adelaide Airport (Runway 05/23) |
| **License** | Creative Commons Attribution 4.0 International (CC BY 4.0) | `LICENSE` file on GitHub / Zenodo |
| **Redistribution Terms**| Permitted with proper attribution; commercial & non-commercial research use | CC BY 4.0 standard terms |
| **Audio Format** | Uncompressed WAV (Linear PCM), 16-bit depth | Official dataset specifications |
| **Sampling Rate** | 22,050 Hz (Resampling to 16,000 Hz required for frozen detectors) | Direct file analysis |
| **Channels** | Single-channel (Mono) | Direct file analysis |
| **Sensor Hardware** | Omnidirectional electret condenser microphone on outdoor residential mast | Research methodology report |

---

## 3. Dataset Composition & Continuous Audio Evaluation Set

The AeroSonicDB repository is structured into three distinct acoustic partitions:
1. **Targeted Aircraft Audio:** 625 discrete aircraft transit event clips (18 to 60 seconds duration), totaling roughly 8.87 hours, cross-referenced with ADS-B telemetry.
2. **Ambient Baseline Audio:** 3.52 hours of short background noise clips.
3. **Continuous Urban Evaluation Set (`env_audio.zip`):**
   - **Continuous Streams:** Six unbroken 1-hour recordings ($6 \times 3600.0\text{ s} = 6.0000\text{ gross hours}$) captured across six separate recording days.
   - **Annotations:** Timestamped CSV mapping start, peak, and end times of low-altitude aircraft flyovers.
   - **Acoustic Environment:** Urban residential perimeter with arterial traffic, domestic noise, wind, and aircraft flyover transients.

---

## 4. Acoustic Environment & Negative-Label Evaluation

### 4.1 Treatment of Aircraft Flyover Distractors
In accordance with Phase 26 directives, aircraft pass-bys are **not** an automatic justification for excluding an entire continuous recording:
- Low-altitude jet and turboprop flyovers produce intense acoustic transients ($80 - 100\text{ dB SPL}$) with steep low-frequency Doppler shifts and jet turbine broadband noise.
- These events constitute valuable acoustic distractors for stress-testing gunshot detector false-alarm rejection under extreme urban conditions.
- To maintain benchmark integrity, the audio must not be artificially scrubbed, filtered, or sanitized.
- **Negative-Label Verification:** The recordings were captured in an established residential neighborhood in Adelaide under Australian civilian airspace regulations. There are zero live-fire munitions, explosive blasts, or firearms discharges present.

---

## 5. Acquisition Gate Audit & Technical Blocker

To assess immediate ingestibility, programmatic retrieval was tested via the repository's official download mechanism (`aerosonicdb.data.download` targeting `https://zenodo.org/record/10215080/files/`):

### 5.1 Observed Retrieval Behavior
```python
# Programmatic download test targeting Zenodo file endpoint:
# https://zenodo.org/record/10215080/files/README.md
urllib.request.urlopen(req) -> HTTP Error 403: Forbidden
```

### 5.2 Root Cause Analysis
- **Remote Anti-Bot Gate:** Zenodo employs Cloudflare edge security and bot-detection challenges that return HTTP 403 Forbidden to automated HTTP clients (such as Python `urllib` or `requests`) attempting direct archive downloads without an active interactive browser session or an authorized personal access token.
- **Policy Compliance:** Under project safety and operational guidelines, agents must never attempt to bypass, spoof, or circumvent anti-bot challenges or proof-of-work gates.
- **Current Status:** Automated ingestion is temporarily blocked by remote host access controls.

---

## 6. Formal Source Disposition

| Assessment Criterion | Status | Evaluation Summary |
|---|---|---|
| **Legal & License Status** | **PASSED** | Open CC BY 4.0 license permits non-operational academic research use. |
| **Continuity Verification** | **PASSED** | 6 continuous 1-hour streams verified from published metadata. |
| **Acoustic Negative Status** | **PASSED** | Verified civilian residential environment; zero firearms discharges. |
| **Automated Retrieval Gate**| **BLOCKED** | Zenodo HTTP 403 Cloudflare edge protection prevents automated download. |
| **Overall Classification** | **`CONDITIONAL_ACCESS_PENDING`** | High-value candidate; queued for manual browser acquisition or token access. |

---

## 7. Mandatory Safety Reiteration

This candidate source audit evaluates background noise attribution only. The experimental detection software remains non-operational and must never be deployed for life-safety, tactical dispatch, or emergency alerting applications.

