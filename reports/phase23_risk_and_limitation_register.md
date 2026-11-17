# Acoustic Gunshot Detection Risk & Limitation Register — Phase 23
## Acquisition Hazards, Non-Continuous Sound Traps, Exposure Shortfall & Life-Safety Disclaimers

**Document ID:** `REPORT-PHASE23-RISK-001`  
**Phase:** 23 (First 50-Hour Negative Exposure Benchmark)  
**Date:** November 2026  
**Status:** ACTIVE RISK REGISTER  

---

### MANDATORY SAFETY DESIGNATION
> [!CAUTION]
> **RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.**  
> This experimental acoustic machine-learning system is uncertified and must never be deployed for autonomous emergency dispatch, tactical police response, active-shooter alerting, automated lockdown or evacuation, or life-critical physical security. Use legally obtained recordings and safe audio playback only. Live-fire testing and hazardous acoustic experiments are strictly prohibited.

---

## 1. Domain-Specific Risk Catalog

| Risk ID | Risk Domain | Hazard Description | Pre-Mitigation Severity | Post-Mitigation Residual Risk | Mitigation Strategy & Phase 23 Status |
|---|---|---|---|---|---|
| **ACQ-01** | Dataset Ingestion | **The SONYC / DCASE Discrete Clip Trap:** Treating collections of 10-second segmented clips as continuous streams. Splicing creates artificial acoustic boundary transients that trigger spurious false alerts. | **CRITICAL** | **CONTROLLED** | Phase 23 formally audited SONYC-UST and DCASE repositories and rejected them from the continuous benchmark. Only genuine unbroken continuous recordings are admitted. |
| **ACQ-02** | Legal & Licensing | **Unlawful Audio Scraping & Access Bypass:** Attempting to bypass web rate limits, CAPTCHAs, or terms of service on proprietary municipal sensor networks or commercial streaming feeds. | **CRITICAL** | **ELIMINATED** | Strict compliance with legal-access gates. Only CC BY 4.0 and documented open academic repositories (Zenodo 7493820, 3938837, 18561165) are utilized. |
| **ACQ-03** | Data Integrity | **Synthetic Padding to Force Exposure Targets:** Looping, duplicating, or concatenating unrelated audio to falsely claim reaching a 50-hour benchmark target. | **HIGH** | **ELIMINATED** | In strict accordance with prompt instructions, Phase 23 reports the exact verified natural exposure achieved (6.646 hours) and transparently documents the 43.354-hour shortfall. |
| **HARD-01** | Storage & System | **Local Disk Exhaustion:** Downloading multi-terabyte raw uncompressed 24-bit/48kHz WAV audio files rapidly consumes remaining local drive space (73.4 GB available). | **HIGH** | **CONTROLLED** | Strict storage discipline: metadata-first inspection before acquisition; raw uncompressed multi-channel ambisonic datasets rejected. |
| **EVAL-01** | Metric Distortion | **Cooldown Dead Time Omission in Exposure Denominator:** Including refractory dead times ($\tau_{\text{cooldown}} = 2.0\text{ s}$) where the detector is blind to new alerts in the exposure denominator, artificially deflating reported false-alarm rates. | **HIGH** | **RESOLVED** | Phase 23 calculates and reports both Gross Duration and Net Eligible Exposure ($T_{\text{eligible}} = T_{\text{gross}} - \sum \tau_{\text{cooldown}}$). |
| **STAT-01** | Statistical Bias | **Single-Environment False-Alert Overdispersion:** False alarms cluster in specific acoustic environments (e.g., arterial roads with truck air brakes or reverberant market halls), violating the homogeneous Poisson arrival assumption. | **HIGH** | **DOCUMENTED** | Report documents per-stream and per-environment alert distributions alongside exact Garwood confidence intervals. |
| **SAFE-01** | Life Safety | **Operational Dispatch Assumption:** Assuming an observed false-alert rate on 6.65 hours of audio is sufficient to deploy an autonomous dispatch system across a 1,000-sensor metropolitan network. | **FATAL** | **GOVERNED** | Mandatory prominent safety banners across all code, reports, and UI. Explicit disclaimers prohibiting CAD or emergency deployment. |

---

## 2. In-Depth Technical Analysis of Core Limitations

### 2.1 The Exposure Shortfall Reality
- **Target:** 50.0 continuous negative exposure hours.
- **Achieved Primary Natural Continuous Exposure:** 6.646 hours (23,925.58 seconds) across 17 unbroken field streams.
- **Root Cause of Shortfall:**
  1. The vast majority of published "urban sound" research datasets (SONYC, UrbanSound8K, DCASE, AudioSet) are composed exclusively of short slices ($1\text{ to }10\text{ seconds}$).
  2. Public repositories containing genuine unbroken multi-hour continuous ambient audio are rare and often require downloading massive uncompressed files (>25 GB) that exceed reasonable bandwidth and disk limits.
  3. Synthetically concatenating or looping clips was conclusively proven in Phase 15/16 to generate dozens of false positives from edge discontinuities, corrupting the scientific validity of the benchmark.
  4. Per Section 11 of the Phase 23 mandate: *"If only 12 eligible hours can be established, report 12 hours. Do not manufacture, concatenate, loop, duplicate, or relabel audio to reach 50 hours... State the exact eligible hours obtained and explain the shortfall."*

### 2.2 Environmental Sensitivity Distribution
The false-alert distribution across the 17 natural streams demonstrates severe environmental non-uniformity:
- **Quiet / Continuous Mechanical Ambience:** Pneumatic compressors, concrete mixers, pumps, washing machines, and rural reservoirs produced **0 false alerts** over ~4.5 hours of exposure.
- **Impulsive / Dynamic Urban Transients:** Arterial road traffic (`P16-STREAM-05`) and reverberant stone-paved pedestrian walkways (`P17-STREAM-14`, `P17-STREAM-12`) produced over 80% of all false alerts.
- **Conclusion:** A simple single-number Poisson arrival rate ($\lambda$) fails to capture the spatial and environmental bimodality of urban false alarms.

---

*Authored by Principal Acoustic ML Research Engineer & Systems Safety Auditor.*  
*Antigravity Gunshot Detection Research Consortium — Phase 23.*

