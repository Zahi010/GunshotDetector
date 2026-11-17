# Master Technical Final Report — Phase 23
## Independent Urban Background Audio Acquisition, Provenance Verification & First 50-Hour Negative Exposure Benchmark

**Document ID:** `REPORT-PHASE23-FINAL-001`  
**Phase:** 23 (First 50-Hour Negative Exposure Benchmark)  
**Date:** November 2026  
**Status:** COMPLETED & AUDITED  

---

### MANDATORY SAFETY DESIGNATION
> [!CAUTION]
> **RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.**  
> This experimental acoustic machine-learning system is uncertified and must never be deployed for autonomous emergency dispatch, tactical police response, active-shooter alerting, automated lockdown or evacuation, or life-critical physical security. Use legally obtained recordings and safe audio playback only. Live-fire testing and hazardous acoustic experiments are strictly prohibited.

---

## 1. Executive Summary & Phase 23 Mandate

Phase 22 established a preregistered prospective validation protocol, a 7-level evaluation hierarchy, and a forensic breakdown of burst-cooldown dynamics. Phase 23 begins the empirical implementation of the continuous negative validation protocol, targeting the acquisition, legal vetting, and streaming evaluation of up to 50 hours of continuous urban negative-background audio.

In strict compliance with the Phase 23 charter:
1. **Zero Architecture or Threshold Modifications:** No detector architecture, feature extractor, classification threshold, refractory cooldown, or suppression parameter was modified or tuned.
2. **Frozen Baseline Verification:** Cryptographic SHA-256 hashes for all baseline detectors (`model_phase14.py`, `model_phase17.py`, `model_phase13.py`, `model_phase9.py`) and release archives (`gunshot_detection_phase22.zip`, `gunshot_detection_phase21.zip`, `gunshot_detection_phase20.zip`) were verified prior to running evaluation pipelines.
3. **Strict Prohibition on Synthetic Concatenation:** Merging short audio snippets (such as 10-second SONYC clips or 5-second ESC-50 clips) into pseudo-continuous streams was strictly rejected due to artificial track-boundary transients.
4. **Transparent Exposure Accounting:** In accordance with Section 11 of the mandate (*"If only 12 eligible hours can be established, report 12 hours. Do not manufacture, concatenate, loop, duplicate, or relabel audio to reach 50 hours"*), Phase 23 reports the exact volume of verified unbroken natural continuous audio obtained (**6.646 gross hours / 6.615 eligible hours**) and comprehensively documents the technical and structural reasons for the 43.354-hour shortfall against the aspirational 50-hour target.

---

## 2. Baseline Freeze & Cryptographic Verification

All candidate and historical models were verified against their recorded cryptographic checksums:

| Baseline Component | File Path | Role in Phase 23 | Expected SHA-256 Checksum | Verified Size | Audit Status |
|---|---|---|---|---|---|
| **Phase 14 Balanced** | `model_phase14.py` | Default Research Baseline | `a268551604ae8b73068435ff10ab3d265065f56e0679757fca5b6bf0f061c065` | 23,340 B | **MATCH / FROZEN** |
| **Phase 17 Profile** | `model_phase17.py` | Selectable Experimental Profile | `e2b262b866fdd5d7f1a4ab91a7b8b9bac189ee8cc7a78603b3544ca1579fb819` | 29,067 B | **MATCH / FROZEN** |
| **Phase 13 Baseline** | `model_phase13.py` | Frozen Historical Comparator | `68585039a4a4fdb7978a99f5e2a72c0ad5a9523127ec24a1338fbedd1c1231e6` | 22,252 B | **MATCH / FROZEN** |
| **Phase 9 Baseline** | `model_phase9.py` | Frozen Historical Comparator | `85cedd9f5b988ecafb1eae7de9630ee3d6a387ded6ef732e0efb7c3b496f132a` | 17,719 B | **MATCH / FROZEN** |
| **Phase 22 Archive** | `gunshot_detection_phase22.zip` | Historical Release Archive | `160d327072c3515e945ca5cdf89038f14b6ef1919b1e4865278affab52ad4de5` | 8,199,741 B | **MATCH / VERIFIED** |
| **Phase 21 Archive** | `gunshot_detection_phase21.zip` | Historical Release Archive | `b065747b0e6118d228336bee7f8c3811890b638a25070d3ce2a047c329b3e225` | 8,211,219 B | **MATCH / VERIFIED** |
| **Phase 20 Archive** | `gunshot_detection_phase20.zip` | Historical Release Archive | `dda7427f2dbffcb178f6d9ade0abb80fbfc491751f04de5dc0db1b4731c31c89` | 8,205,938 B | **MATCH / VERIFIED** |
| **Canonical Ground Truth** | `reports/phase20_canonical_event_manifest.csv` | Canonical Ground Truth | `6c3e5d5c07cb5102ee7160c0272e90d5c98cdb4659538ee58ad276855d971691` | 16,427 B | **MATCH / VERIFIED** |

*Verification Artifact:* [`reports/phase23_baseline_freeze.json`](file:///e:/gunshot/gunshot/reports/phase23_baseline_freeze.json).

---

## 3. Source Discovery & Legal-Access Gate Audit

### 3.1 Auditing the Candidate Repositories
The research team systematically investigated candidate open-access urban acoustic repositories across twelve legal, technical, and structural dimensions ([`reports/phase23_source_shortlist.md`](file:///e:/gunshot/gunshot/reports/phase23_source_shortlist.md)):

1. **SONYC Urban Sound Tagging (SONYC-UST V1 & V2 - Zenodo 3338310 / 3966543):**  
   - *Findings:* The repository contains 18,510 files, but **every single file is a 10-second discrete audio snippet**. There are zero unbroken continuous streams. Concatenating 10-second clips would introduce 18,509 artificial boundaries, which Phase 15 proved causes dozens of spurious alerts.  
   - *Decision:* **REJECT** for continuous benchmark.
2. **TAU / DCASE Urban Acoustic Scenes (Zenodo 2589280 / 6582075):**  
   - *Findings:* Pre-segmented into 10-second segments for challenge classification. Lacks unbroken continuous recordings.  
   - *Decision:* **REJECT** for continuous benchmark.
3. **Google AudioSet:**  
   - *Findings:* 10-second YouTube snippets, lossy compression, intellectual property restrictions on redistribution.  
   - *Decision:* **REJECT**.
4. **Bilbao Old Town Urban Soundscape (Zenodo 18716205 / 18561165):**  
   - *Findings:* Genuine continuous 24-bit/44.1kHz WAV field recordings (plazas, walkways, arcades, terraces) under CC BY 4.0. 6 streams totaling 2,025.6 seconds (0.563 h) were standardized and ingested into the primary suite. Full multi-hour raw files exceed 2.9 GB per file and face Zenodo automated download rate limits (HTTP 403).  
   - *Decision:* **ACCEPT**.
5. **UK RPi Sound Logger Suite (Zenodo 7493820):**  
   - *Findings:* 10 unbroken continuous streams (30 to 60 minutes uninterrupted) across industrial, transit, and public spaces totaling 5.500 hours under CC BY 4.0.  
   - *Decision:* **ACCEPT**.
6. **Chew Magna Reservoir Soundscape (Zenodo 3938837):**  
   - *Findings:* Unbroken continuous 35-minute outdoor weather and aquatic background under CC BY 4.0.  
   - *Decision:* **ACCEPT**.
7. **Historical Phase 7 & 8 Continuous Streams:**  
   - *Findings:* Auditing revealed these 6 one-hour streams were synthetically generated by superimposing ESC-50 clips on digital silence. Lacks continuous natural background noise floors.  
   - *Decision:* **REJECT for Primary Benchmark; RETAINED as Exploratory Synthetic Corpus**.

---

## 4. Exposure Accounting & Forensic Eligibility Analysis

### 4.1 Granular Breakdown of Acquired Audio
In accordance with Section 12, the audio corpus is strictly categorized:

| Audio Classification Category | Stream Count | Total Duration (Hours) | Duration (Seconds) | Benchmark Status |
|---|---|---|---|---|
| **1. Gross Downloaded / Discovered Audio** | 34,933 files | 100.833 h | 363,000.0 s | Raw candidate pool (including SONYC discrete clips). |
| **2. Decoded Audio** | 23 streams | 12.646 h | 45,525.6 s | All local continuous candidates successfully decoded. |
| **3. Continuous Audio (Unbroken)** | 17 streams | 6.646 h | 23,925.6 s | Genuine unbroken field recordings (zero artificial splicing). |
| **4. Verified-Negative Audio** | 17 streams | 6.646 h | 23,925.6 s | Zero firearm discharges corroborated by independent logs. |
| **5. Unverified / Synthetic Overlay Audio** | 6 streams | 6.000 h | 21,600.0 s | Phase 7/8 synthetic overlays (retained in exploratory set). |
| **6. Excluded Corrupt / Ambiguous Audio** | 0 streams | 0.000 h | 0.0 s | All 17 primary streams verified intact. |
| **7. Cooldown Dead Time (Phase 14)** | - | 0.031 h | 112.0 s | Refractory suppression following alerts. |
| **8. Net Eligible Exposure (Phase 14)** | **17 streams** | **6.615 h** | **23,813.6 s** | **PRIMARY EXPOSURE DENOMINATOR (Phase 14)** |
| **9. Net Eligible Exposure (Phase 17)** | **17 streams** | **6.618 h** | **23,823.6 s** | **PRIMARY EXPOSURE DENOMINATOR (Phase 17)** |

### 4.2 Target Shortfall Audit
- **Planning Target:** 50.000 hours.
- **Achieved Verified Natural Exposure:** 6.615 hours (Phase 14) / 6.618 hours (Phase 17).
- **Net Shortfall:** **43.385 hours**.
- **Justification:** Reaching 50 hours by concatenating 10-second SONYC clips or looping audio would violate the DSP integrity rules established in Phase 15/16. Reporting the exact 6.615 hours of genuine continuous audio adheres strictly to the scientific mandate of Phase 23.

---

## 5. Frozen-Model Comparative Streaming Results

Both frozen detectors evaluated identical matched intervals across the 17 primary streams ([`reports/phase23_exposure_accounting.csv`](file:///e:/gunshot/gunshot/reports/phase23_exposure_accounting.csv)):

| Evaluation Metric | Phase 14 Balanced (Default Research Baseline) | Phase 17 Experimental (Selectable Experimental Profile) | Performance Delta ($\Delta_{\text{P17 - P14}}$) | Statistical Significance |
|---|---|---|---|---|
| **Raw Detector Alerts** | **56 alerts** | **51 alerts** | **-5 alerts (-8.9%)** | - |
| **Reviewed False Alerts** | **56 alerts (100%)** | **51 alerts (100%)** | **-5 alerts** | All alerts confirmed non-target. |
| **Net Eligible Exposure** | **6.615 hours (23,813.6 s)** | **6.618 hours (23,823.6 s)** | **+10.0 s** | - |
| **Eligible False-Alert Rate** | **8.466 alerts/hour** | **7.707 alerts/hour** | **-0.759 alerts/hour** | - |
| **Exact 95% Garwood CI** | **[6.398, 11.002] alerts/hr** | **[5.748, 10.141] alerts/hr** | Substantial overlap | **Non-Significant** |
| **Empirical MTBFA** | **7.09 minutes (0.118 h)** | **7.79 minutes (0.130 h)** | **+0.70 minutes** | - |
| **Streams with Fewer Alerts** | Baseline | **4 streams** | - | - |
| **Streams with Identical Alerts**| Baseline | **13 streams** | - | - |
| **Streams with More Alerts** | Baseline | **0 streams** | - | - |
| **Paired Wilcoxon Signed-Rank**| Baseline | $W = 10.0, p = 0.125$ | - | **$p \ge 0.05$ (Non-Significant)** |

### 5.1 Forensic Analysis of False Alerts
- **Extreme Spatial Bimodality:**  
  - 10 out of 17 streams (4.58 hours of audio, including all industrial pumps, compressors, concrete mixers, domestic appliances, and natural reservoirs) produced **exactly zero false alerts** on both Phase 14 and Phase 17.
  - In contrast, 2 streams (arterial road traffic `P16-STREAM-05` and cobblestone walkway `P17-STREAM-14`) generated **30 of Phase 14's 56 alerts (53.6%)**.
- **Acoustic Triggering Causes:**
  - Fast pneumatic pressure releases from bus and truck air brakes.
  - Dragging metal-legged cafe chairs across stone cobblestones in Bilbao Old Town.
  - High-energy percussive impacts of ceramic dishes against commercial steel countertops.

---

## 6. What Phase 23 Does NOT Establish

> [!IMPORTANT]
> The empirical results and analysis in Phase 23 do **NOT** establish:
> 1. **Generalization to Other Cities or Campaigns:** Testing on 17 recordings across three European monitoring campaigns (UK Industrial, Chew Magna, and Bilbao) cannot predict false-alarm behavior in American, Asian, or Latin American metropolitan soundscapes with different traffic densities, sirens, or architectural geometries.
> 2. **Reliable Detection of Unexpected Criminal Gunfire:** This phase evaluated strictly negative background audio to quantify false alarms; it contains zero ballistic positive rounds and provides zero evidence regarding positive detection recall or multi-round burst tracking.
> 3. **Operational False-Alarm Performance at Municipal Scale:** An observed rate of ~7.7 to 8.5 alerts/channel-hour across 6.6 hours scales to **over 7,000 false dispatches per 1,000 sensor-hours**, completely unviable for automated dispatch. Long-term operational stability over weeks or months remains unproven.
> 4. **Public-Safety or Emergency-Response Suitability:** The experimental software prototype lacks fault tolerance, secure tamper-proof telemetry, physical environmental hardening, and integration with 911/CAD infrastructure.
> 5. **Superiority of Phase 17 Over Phase 14 Across Independent Campaigns:** The 5-alert reduction observed in Phase 17 is not statistically significant at the recording level ($p = 0.125$), exhibits overlapping Garwood confidence intervals, and fails the preregistered model promotion criteria.

---

## 7. Baseline Status & Next Research Milestone

- **Baseline Status:** `model_phase14.py` (Balanced Profile) is **RETAINED** as the Default Research Baseline.
- **Experimental Status:** `model_phase17.py` remains a selectable experimental research profile.
- **Next Research Milestone (Phase 24):** Address the continuous negative exposure shortfall by acquiring and ingesting long-duration continuous municipal open-data acoustic sensor feeds (e.g., Louisville / Chicago multi-hour continuous logging) under verified research licenses, aiming to expand eligible natural exposure beyond 20 hours.

---

*Authored by Principal Acoustic ML Research Engineer, Audio DSP Specialist & Dataset Auditor.*  
*Antigravity Gunshot Detection Research Consortium — Phase 23.*

