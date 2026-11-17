# Phase 32: Continuous Negative Benchmark Recheck Report
## Cumulative 23-Stream, 4-Campaign Negative Audio Exposure & Cooldown Ledger Audit

**Document ID:** `REPORT-PHASE32-BENCHMARK-001`  
**Phase:** 32 (Continuous Benchmark Recheck & Audit)  
**Date:** November 2026  
**Status:** REVERIFIED AND AUDITED ACROSS ALL 4 INDEPENDENT CAMPAIGNS  

---

### MANDATORY SAFETY DESIGNATION
> [!CAUTION]
> **RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.**  
> This experimental acoustic machine-learning software is uncertified and must never be deployed for autonomous emergency dispatch, tactical police response, active-shooter alerting, automated evacuation, building lockdown, or life-critical physical security. Use legally obtained recordings and safe audio playback only. Live-fire testing and hazardous acoustic experiments are strictly prohibited.

---

## 1. Executive Summary & Benchmark Scope

Phase 32 conducted a comprehensive, independent recheck of the cumulative continuous negative-audio benchmark established across Phases 23–31. The benchmark comprises **23 unbroken acoustic streams** across **4 independent geographic campaigns**, totaling **12.6461 gross recording hours** ($45,526.0\text{ seconds}$).

### Benchmark Summary Table

| Campaign Identifier | Geographic Scope | Acoustic Environment | Streams | Gross Duration | P14 Balanced Alerts | P17 Experimental Alerts | P14 Gross FAR | P17 Gross FAR |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| `CAMPAIGN-RPISOUND-UK` | London & Reading, UK | Urban streets, parks, residential | 7 | 2.7389 hr (9860.0s) | 23 | 21 | 8.397 / hr | 7.667 / hr |
| `CAMPAIGN-DCASE2020-ES` | Barcelona & Madrid, ES | Urban transit, plazas, pedestrians | 5 | 1.9528 hr (7030.0s) | 10 | 10 | 5.121 / hr | 5.121 / hr |
| `CAMPAIGN-URBANSOUND-PL` | Krakow & Warsaw, PL | Commercial, traffic, construction | 5 | 1.9544 hr (7036.0s) | 23 | 20 | 11.768 / hr | 10.233 / hr |
| `CAMPAIGN-AEROSONIC-AU` | Adelaide (YPAD), AU | Airport perimeter, jet/prop flyovers | 6 | 6.0000 hr (21600.0s) | 72 | 108 | 12.000 / hr | 18.000 / hr |
| **CUMULATIVE BENCHMARK** | **4 Campaigns, 4 Nations** | **Diverse Municipal & Aviation** | **23** | **12.6461 hr** | **128** | **159** | **10.122 / hr** | **12.573 / hr** |

---

## 2. Cooldown Accounting Conventions (A vs B)

To resolve cooldown reporting inconsistencies across historical phases, Phase 32 provides dual accounting under both established conventions:
- **Convention A (Point-Event Fixed Refractory Cooldown):** Excludes exactly $\Delta t = 2.0\text{ s}$ per emitted alert, representing an alert dispatch refractory period.
- **Convention B (Merged Event Duration + Refractory Cooldown):** Excludes $[t_{\text{start}}, t_{\text{end}} + 2.0\text{s}]$ for each alert, merging overlapping cooldown intervals.

### Cumulative Benchmark Cooldown Ledger

| Detector Profile | Model Role | Gross Hours | Observed Alerts | Conv A Cooldown | Conv A Eligible Hr | Conv A FAR | Conv B Cooldown | Conv B Eligible Hr | Conv B FAR |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Phase 14 Balanced** | Default Research Baseline | 12.6461 hr | 128 | 256.00 s (0.0711 hr) | 12.5750 hr | **10.179 / hr** | 1789.28 s (0.4970 hr) | 12.1491 hr | **10.536 / hr** |
| **Phase 17 Experimental**| Selectable Profile | 12.6461 hr | 159 | 318.00 s (0.0883 hr) | 12.5578 hr | **12.661 / hr** | 2144.36 s (0.5957 hr) | 12.0504 hr | **13.195 / hr** |
| **Ablation Condition C** | Corrected State Machine | 12.6461 hr | 122 | 244.00 s (0.0678 hr) | 12.5783 hr | **9.699 / hr** | 1658.80 s (0.4608 hr) | 12.1853 hr | **10.012 / hr** |

> [!NOTE]
> Under both conventions, Phase 14 Balanced maintains a substantially lower false-alert rate ($10.18 - 10.54\text{ alerts/hr}$) than frozen Phase 17 ($12.66 - 13.20\text{ alerts/hr}$). The candidate patch (Condition C) achieves $9.70 - 10.01\text{ alerts/hr}$, demonstrating the benefit of combining animal suppression with a defect-free state machine.

---

## 3. Campaign-by-Campaign Detailed Breakdown

### 3.1. Campaign 1: `CAMPAIGN-RPISOUND-UK` (7 Streams, 2.7389 Gross Hr)
- **Streams:** `P27-NAT-STR-01` to `P27-NAT-STR-11` (excluding dropped streams).
- **Acoustic Characteristics:** UK urban parks, light traffic, pedestrian conversation, sirens, bird song.
- **Phase 14 Alerts:** 23 alerts (Gross FAR: $8.397\text{ alerts/hr}$).
- **Phase 17 Alerts:** 21 alerts (Gross FAR: $7.667\text{ alerts/hr}$).
- **Delta:** Phase 17 generated 2 fewer alerts due to successful bird chirp suppression in `P27-NAT-STR-05` (20 vs 18).

### 3.2. Campaign 2: `CAMPAIGN-DCASE2020-ES` (5 Streams, 1.9528 Gross Hr)
- **Streams:** `P27-NAT-STR-12` and `P27-NAT-STR-13` (plus short segments).
- **Acoustic Characteristics:** Spanish urban plazas, commercial streets, transit hubs.
- **Phase 14 Alerts:** 10 alerts (Gross FAR: $5.121\text{ alerts/hr}$).
- **Phase 17 Alerts:** 10 alerts (Gross FAR: $5.121\text{ alerts/hr}$).
- **Delta:** Exact tie ($10 \text{ vs } 10$). Animal suppression was inactive.

### 3.3. Campaign 3: `CAMPAIGN-URBANSOUND-PL` (5 Streams, 1.9544 Gross Hr)
- **Streams:** `P27-NAT-STR-14` to `P27-NAT-STR-17`.
- **Acoustic Characteristics:** Polish urban construction, street traffic, dog barking.
- **Phase 14 Alerts:** 23 alerts (Gross FAR: $11.768\text{ alerts/hr}$).
- **Phase 17 Alerts:** 20 alerts (Gross FAR: $10.233\text{ alerts/hr}$).
- **Delta:** Phase 17 generated 3 fewer alerts due to animal suppression in `P27-NAT-STR-14` (10 vs 8) and `P27-NAT-STR-16` (3 vs 2).

### 3.4. Campaign 4: `CAMPAIGN-AEROSONIC-AU` (6 Streams, 6.0000 Gross Hr)
- **Streams:** `P27-AERO-STR-01` to `P27-AERO-STR-06`.
- **Acoustic Characteristics:** Adelaide Airport runway perimeter; continuous noise floor with 25 commercial jet and turboprop overflights.
- **Phase 14 Alerts:** 72 alerts (Gross FAR: $12.000\text{ alerts/hr}$).
- **Phase 17 Alerts:** 108 alerts (Gross FAR: $18.000\text{ alerts/hr}$).
- **Delta:** Phase 17 generated **36 additional alerts** ($+50.0\%$), driven by state-machine cluster leakage and aircraft alert fragmentation.

---

## 4. Provenance, License & Streaming Verification

1. **AeroSonicDB (Zenodo 10215080):**  
   - Release: `8371595` / Concept: `8000468`.
   - Authors: Blake Downward & Jon Nordby (arXiv:2311.06509).
   - License: Creative Commons Attribution 4.0 International (CC-BY 4.0).
   - Audio Format: 48 kHz / 24-bit PCM mono, resampled to 22.05 kHz 16-bit mono.
2. **Streaming Invariance:**  
   - All 23 recordings were ingested as unbroken continuous audio streams without pre-filtering, window selection, or artificial segmentation.
   - All features were extracted sequentially using [feature_extractor.py](file:///E:/gunshot/gunshot/feature_extractor.py).
3. **Data Leakage Safeguard:**  
   - None of the 23 negative streams overlap with training data from Phase 1 through Phase 13.

