# Phase 31: Campaign and Recording Provenance Reconciliation Report
## Forensic Lineage Audit, 23-Stream Master Registry & Cross-Phase Reconciliation

**Document ID:** `REPORT-PHASE31-PROVENANCE-001`  
**Phase:** 31 (Forensic Verification, Defect Verification & Suppression Ablation)  
**Date:** November 2026  
**Status:** COMPLETE FORENSIC RECONCILIATION  

---

### MANDATORY SAFETY DESIGNATION
> [!CAUTION]
> **RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.**  
> This experimental acoustic machine-learning software is uncertified and must never be deployed for autonomous emergency dispatch, tactical police response, active-shooter alerting, automated evacuation, building lockdown, or life-critical physical security. Use legally obtained recordings and safe audio playback only. Live-fire testing and hazardous acoustic experiments are strictly prohibited. Historical controlled-validation recordings may be analysed only as existing research data; do not conduct new firing experiments.

---

## 1. Executive Summary & Audit Mandate

Phase 30 reported apparent discrepancies in campaign assignments, stream counts, and alert allocations when compared to Phase 29:
- **Phase 29 Reported:**
  - Southampton industrial: 10 streams, 5.5000 hours, P14 = 24 alerts, P17 = 22 alerts.
  - Chew Magna rural: 1 stream, 0.5833 hours, P14 = 0 alerts, P17 = 0 alerts.
  - Bilbao urban traffic: 6 streams, 0.5627 hours, P14 = 32 alerts, P17 = 29 alerts.
  - Adelaide airport periphery: 6 streams, 6.0000 hours, P14 = 72 alerts, P17 = 108 alerts.
  - Total: 23 streams, 12.6460 gross hours, P14 = 128 alerts, P17 = 159 alerts.
- **Phase 30 Prose Table Reported:**
  - Paris: 8 streams, 3.7500 hours, P14 = 18 alerts, P17 = 15 alerts.
  - Vienna: 3 streams, 2.3333 hours, P14 = 1 alert, P17 = 0 alerts.
  - Bilbao: 6 streams, 0.5625 hours, P14 = 37 alerts, P17 = 36 alerts.
  - Adelaide: 6 streams, 6.0000 hours, P14 = 72 alerts, P17 = 108 alerts.
  - Total: 23 streams, 12.6458 gross hours, P14 = 128 alerts, P17 = 159 alerts.

Phase 31 conducted a comprehensive, byte-level forensic audit of all 23 underlying audio files, event logs, and provenance CSV files across all phases (Phase 23 through Phase 30).

### Key Forensic Findings
1. **The Physical Audio Dataset Never Changed:**  
   The underlying 23 continuous audio recordings have identical filenames, SHA-256 digests, sample rates (16 kHz mono PCM), and durations across Phases 27, 28, 29, 30, and 31 ($45,525.575\text{ s} = 12.6460\text{ gross hours}$). No streams were added, deleted, re-sampled, or concatenated.
2. **The Underlying Phase 30 CSV Data Was Always Authentic:**  
   In Phase 30, the actual data files (`reports/phase30_recording_provenance.csv`, `reports/phase30_campaign_comparison.csv`, and `reports/phase30_frozen_detector_results.csv`) retained the authentic assignments:
   - `CAMPAIGN-RPISOUND-UK` (Southampton, UK): 10 streams, 5.5000 hr, P14 = 24, P17 = 22.
   - `CAMPAIGN-CHEWMAGNA-UK` (Chew Magna, UK): 1 stream, 0.5833 hr, P14 = 0, P17 = 0.
   - `CAMPAIGN-BILBAO-ES` (Bilbao, Spain): 6 streams, 0.5627 hr, P14 = 32, P17 = 29.
   - `CAMPAIGN-AEROSONIC-AU` (Adelaide, Australia): 6 streams, 6.0000 hr, P14 = 72, P17 = 108.
3. **Root Cause: Clerical Markdown Narrative Error:**  
   The author of `reports/phase30_statistical_analysis.md` copied text from an unvetted draft candidate shortlist (`reports/phase30_candidate_source_inventory.csv` which listed candidate entries for Paris and Vienna) and manually constructed a markdown narrative table that mislabeled `CAMPAIGN-RPISOUND-UK` as "Paris" (8 streams), `CAMPAIGN-CHEWMAGNA-UK` as "Vienna" (3 streams), and shifted residual alerts into Bilbao (37/36). The underlying CSV data remained intact.
4. **Conclusion:**  
   There are exactly **4 independent environmental audio campaigns** spanning **4 distinct acoustic environments** in **3 countries** (United Kingdom, Spain, Australia).

---

## 2. Reconciled Campaign Comparison Matrix

| Campaign ID | Geographic Location | Acoustic Modality | Streams | Gross Duration (hr) | P14 Alerts | P17 Alerts | Delta (P14 - P17) | Favored Detector |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| `CAMPAIGN-RPISOUND-UK` | Southampton, UK | Industrial & Transit Ambient | 10 | 5.5000 | 24 | 22 | +2 | Phase 17 (+2) |
| `CAMPAIGN-CHEWMAGNA-UK` | Chew Magna, UK | Rural Aquatic Soundscape | 1 | 0.5833 | 0 | 0 | 0 | Tied (0) |
| `CAMPAIGN-BILBAO-ES` | Bilbao Old Town, Spain | Dense Urban Pedestrian & Traffic | 6 | 0.5627 | 32 | 29 | +3 | Phase 17 (+3) |
| `CAMPAIGN-AEROSONIC-AU` | Adelaide, Australia | Aviation Airspace & Perimeter | 6 | 6.0000 | 72 | 108 | -36 | Phase 14 (-36) |
| **Cumulative Total** | **UK, Spain, Australia** | **Diverse Multi-Campaign** | **23** | **12.6460** | **128** | **159** | **-31** | **Phase 14 (-31)** |

---

## 3. Detailed Forensic Accounting of All 23 Audio Streams

Each recording was verified against its physical file on disk, its original Zenodo DOI, and its SHA-256 digest:

### 3.1. Campaign 1: Southampton Urban & Industrial (`CAMPAIGN-RPISOUND-UK`)
- **Repository:** Zenodo `10.5281/zenodo.7493820` (RPi Sound Logger Suite)
- **License:** CC BY 4.0
- **Location:** Southampton Industrial & Urban Corridors, United Kingdom
- **Total Streams:** 10 continuous unbroken streams (5.5000 gross hours)
- **Streams Inventory:**
  1. `P27-NAT-STR-01`: `phase16_industrial_compressor_pneumatic_60min.wav` (3600.0s) | P14: 0 | P17: 0
  2. `P27-NAT-STR-02`: `phase16_industrial_exhaust_ventilation_30min.wav` (1800.0s) | P14: 2 | P17: 2
  3. `P27-NAT-STR-03`: `phase16_industrial_concrete_mixer_30min.wav` (1800.0s) | P14: 0 | P17: 0
  4. `P27-NAT-STR-04`: `phase16_industrial_monoblock_pump_30min.wav` (1800.0s) | P14: 0 | P17: 0
  5. `P27-NAT-STR-05`: `phase16_traffic_road_arterial_30min.wav` (1800.0s) | P14: 20 | P17: 18 (P17 +2)
  6. `P27-NAT-STR-06`: `phase16_traffic_transit_train_30min.wav` (1800.0s) | P14: 1 | P17: 1
  7. `P27-NAT-STR-07`: `phase16_public_space_canteen_plaza_30min.wav` (1800.0s) | P14: 1 | P17: 1
  8. `P27-NAT-STR-08`: `phase16_percussion_acoustic_drums_30min.wav` (1800.0s) | P14: 0 | P17: 0
  9. `P27-NAT-STR-09`: `phase16_indoor_appliance_washing_machine_30min.wav` (1800.0s) | P14: 0 | P17: 0
  10. `P27-NAT-STR-10`: `phase16_indoor_interior_laptop_exhaust_30min.wav` (1800.0s) | P14: 0 | P17: 0

### 3.2. Campaign 2: Chew Magna Rural Soundscape (`CAMPAIGN-CHEWMAGNA-UK`)
- **Repository:** Zenodo `10.5281/zenodo.3938837` (Chew Magna Soundscape Survey)
- **License:** CC BY 4.0
- **Location:** Chew Magna, Somerset, United Kingdom
- **Total Streams:** 1 continuous unbroken stream (0.5833 gross hours)
- **Streams Inventory:**
  11. `P27-NAT-STR-11`: `phase16_natural_weather_aquatic_reservoir_35min.wav` (2100.0s) | P14: 0 | P17: 0

### 3.3. Campaign 3: Bilbao Old Town Urban Soundscape (`CAMPAIGN-BILBAO-ES`)
- **Repository:** Zenodo `10.5281/zenodo.18716205` (Universidad del País Vasco)
- **License:** CC BY 4.0
- **Location:** Casco Viejo (Old Town), Bilbao, Spain
- **Total Streams:** 6 continuous unbroken streams (0.5627 gross hours)
- **Streams Inventory:**
  12. `P27-NAT-STR-12`: `phase17_urban_exterior_plaza_30min.wav` (322.708s) | P14: 9 | P17: 9
  13. `P27-NAT-STR-13`: `phase17_urban_interior_commercial_30min.wav` (327.268s) | P14: 2 | P17: 2
  14. `P27-NAT-STR-14`: `phase17_urban_exterior_walkway_30min.wav` (353.872s) | P14: 10 | P17: 8 (P17 +2)
  15. `P27-NAT-STR-15`: `phase17_urban_exterior_terrace_30min.wav` (322.736s) | P14: 3 | P17: 3
  16. `P27-NAT-STR-16`: `phase17_urban_interior_arcade_30min.wav` (379.550s) | P14: 3 | P17: 2 (P17 +1)
  17. `P27-NAT-STR-17`: `phase17_urban_interior_hall_30min.wav` (319.441s) | P14: 5 | P17: 5

### 3.4. Campaign 4: AeroSonicDB Adelaide Airport Periphery (`CAMPAIGN-AEROSONIC-AU`)
- **Repository:** Zenodo `10.5281/zenodo.10215080` (AeroSonicDB 3K / YPAD-0523)
- **License:** CC BY 4.0
- **Location:** Adelaide Airport Residential Perimeter, South Australia
- **Total Streams:** 6 continuous unbroken streams (6.0000 gross hours)
- **Streams Inventory:**
  18. `P27-AERO-STR-01`: `1_AUDIO_16k.wav` (3600.0s) | P14: 15 | P17: 23 (P14 +8)
  19. `P27-AERO-STR-02`: `2_AUDIO_16k.wav` (3600.0s) | P14: 3 | P17: 5 (P14 +2)
  20. `P27-AERO-STR-03`: `3_AUDIO_16k.wav` (3600.0s) | P14: 7 | P17: 7 (Tied)
  21. `P27-AERO-STR-04`: `4_AUDIO_16k.wav` (3600.0s) | P14: 8 | P17: 10 (P14 +2)
  22. `P27-AERO-STR-05`: `5_AUDIO_16k.wav` (3600.0s) | P14: 17 | P17: 28 (P14 +11)
  23. `P27-AERO-STR-06`: `6_AUDIO_16k.wav` (3600.0s) | P14: 22 | P17: 35 (P14 +13)

---

## 4. Resolution of the Phase 30 Narrative Discrepancy

The investigation conclusively establishes:
1. **No Data Regeneration:** Event logs, detection scores, window features, and alert timelines were never re-computed or altered between Phase 29 and Phase 30.
2. **Identical Cumulative Alert Totals:** Phase 14 generated exactly 128 alerts and Phase 17 generated exactly 159 alerts in all phases.
3. **Reconciliation Table:**
   - In Phase 30 prose, the author reported:
     - "Paris": 8 streams, 3.7500 hr, P14 = 18, P17 = 15
     - "Vienna": 3 streams, 2.3333 hr, P14 = 1, P17 = 0
     - "Bilbao": 6 streams, 0.5625 hr, P14 = 37, P17 = 36
   - Sum of prose European baseline: $8 + 3 + 6 = 17\text{ streams}$, $3.75 + 2.3333 + 0.5625 = 6.6458\text{ hr}$, $\text{P14} = 18 + 1 + 37 = 56$, $\text{P17} = 15 + 0 + 36 = 51$.
   - True European baseline: Southampton (10 streams, 5.5h, 24/22) + Chew Magna (1 stream, 0.5833h, 0/0) + Bilbao (6 streams, 0.5627h, 32/29) = $17\text{ streams}$, $6.6460\text{ hr}$, $\text{P14} = 56$, $\text{P17} = 51$.
   - The European totals were mathematically identical ($56\text{ vs }51$, $17\text{ streams}$, $6.65\text{ hr}$). The discrepancy was solely an arbitrary repartitioning and mislabeling inside the markdown narrative of `phase30_statistical_analysis.md`.
4. **Resolution:**
   The master registry in `reports/phase31_recording_master_registry.csv` and `reports/phase31_campaign_assignment_changes.csv` officially supersedes the erroneous Phase 30 narrative. The true campaign identities are restored and confirmed.

