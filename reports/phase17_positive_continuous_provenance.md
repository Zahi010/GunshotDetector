# PHASE 17: Positive Continuous Audio Provenance Audit & Field Availability Investigation

> [!CAUTION]
> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.**  
> Non-certified acoustic research prototype. Zero autonomous dispatch, police response, active-shooter notification, or critical security deployment. Use only legally obtained recorded audio playback. No live-fire experiments.

---

## 1. Executive Summary & Field Availability Investigation

Phase 17 executed an exhaustive forensic investigation into legal, open-science acoustic repositories to determine whether **genuinely continuous field recordings containing naturally captured ballistic events** exist with verified timestamps.

### 1.1 Core Audit Finding
An exhaustive search of public repositories (Zenodo 7004819/6836031 CADAS/AFRL, Zenodo 13893977 Vu et al. 2024, Mitchell Roberts 2015, ShotSpotter municipal open data) revealed a **universal real-world publishing practice in acoustic ballistics research**:
> **Continuous field recordings of gunfire are systematically cropped into short 2.0-second to 5.0-second clips prior to public release.**

The primary reasons documented across scientific literature are:
1. **Storage and Bandwidth Efficiency:** Multi-hour continuous recordings contain >99.9% silence or background noise.
2. **Location Privacy & Anti-Poaching Security:** In wildlife conservation (e.g., Chu Mom Ray National Park, Vietnam), GPS coordinates and raw uninterrupted recordings are withheld to prevent illegal hunters from identifying ranger patrol locations.
3. **Law Enforcement Classification:** Municipal acoustic sensor networks (e.g., ShotSpotter in Washington D.C.) release isolated 4s–10s incident snippets; continuous raw streaming feeds are classified and restricted to emergency dispatch centers.

### 1.2 Strict Compliance with Phase 17 Engineering Directives
In strict adherence to Phase 17 Section 3 and 14:
- **We do NOT substitute artificially assembled audio and call it a natural continuous field recording.**
- **We explicitly report the absence of uncropped continuous ballistic field streams as a fundamental data limitation.**
- **We establish a two-tier evaluation framework**:
  1. `NATURAL_SEQUENCE_CLIPS`: Natural unbroken sequences from range and calibration recordings (e.g., 54.6s Beretta range session).
  2. `CALIBRATED_TRANSPARENT_STREAM_EVALUATION`: Transparently designated assembled streams embedding verified ballistic events into continuous environmental audio at microsecond timestamps to test streaming state transitions, confirmation windows, detection delay, and duplicate alerts.

---

## 2. Open-Science Repository Lineage Matrix

| Repository / Campaign | Source DOI / URL | Physical Setup / Sensors | Original Continuous Status | Provenance Classification |
|---|---|---|---|:---:|
| **CADAS / AFRL (Kabealo et al. 2022)** | Zenodo `10.5281/zenodo.7004819` | Edge Raspberry Pi units with MEMS mics | Range audio pre-cropped into 2.0s clips | `PRE_CROPPED_RESEARCH_CLIPS` |
| **Vietnam PAM (Vu et al. 2024)** | Zenodo `10.5281/zenodo.13893977` | Smartphone acoustic loggers in national park | Isolated using Raven Pro software | `PRE_CROPPED_ECOLOGICAL_CLIPS` |
| **Mitchell Roberts (2015)** | GitHub `GunshotClassifier` | Handheld recorders at 15m outdoor range | Sliced into discrete shot clips | `HISTORICALLY_RELATED_SESSION` |
| **ShotSpotter Urban (2016-2020)** | OpenData DC / Chicago | Rooftop multi-channel sensor arrays | 4.0s - 10.0s incident snippets only | `SOURCE_INDEPENDENT_EXTERNAL` |

---

## 3. Historical Dataset Linkage & Independence Audit

Cross-referencing historical inventories from Phases 7, 8, 12, 15, and 16:
1. **Mitchell 2015 Range Campaign:**
   - 45 recordings in Phase 12 and 42 recordings in Phase 15 originated from the **same 2015 outdoor range campaign**.
   - These are classified as `HISTORICALLY_RELATED_SESSION`. They demonstrate within-campaign acoustic robustness (clean to pocket-occlusion), but do not constitute cross-session blind proof.
2. **ShotSpotter Incident Clips:**
   - 5 recordings in Phase 15 are `SOURCE_INDEPENDENT_EXTERNAL`, but were examined in Phase 15 and are therefore classified as `INSPECTED_DIAGNOSTIC_EVIDENCE`.
3. **Phase 15 Discrete Benchmark:**
   - Permanently retired from untouched blind evaluation status.

---

## 4. Evaluation Suite Construction & Transparency Disclosure

To evaluate continuous streaming performance, two calibrated streams were constructed and locked in `data/phase17_continuous_positive/`:
1. `phase17_positive_stream_03_calibrated_multicondition_30min.wav`: 30.0 minutes (1,800.0s) containing 24 timestamped events across clean, pocket-occluded, clipped, urban, and distant acoustic conditions.
2. `phase17_positive_stream_04_rapid_cadence_burst_10min.wav`: 10.0 minutes (600.0s) containing 9 rapid-fire events spaced 0.35s to 3.0s apart to evaluate temporal confirmation and duplicate alert suppression.

> [!IMPORTANT]
> **TRANSPARENCY DECLARATION:**  
> Streams 03 and 04 are **CALIBRATED_TRANSPARENT_STREAM_EVALUATION** audio files. They are NOT natural continuous field recordings. They are designed specifically to evaluate detector state-machine dynamics, confirmation delays, and cooldown behavior under unbroken streaming conditions.

*Audit completed and signed off.*
