# Dataset Acquisition & Research Governance Plan
## Legal Sourcing, Provenance Verification, and Ethical Ingestion Protocol

**Document ID:** `REPORT-PHASE22-DATA-001`  
**Version:** 1.0 (Governance & Acquisition Roadmap)  
**Date:** November 2026  
**Status:** SPECIFICATION & ACQUISITION SHORTLIST  

---

### MANDATORY SAFETY DESIGNATION
> [!CAUTION]
> **RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.**  
> This experimental acoustic machine-learning system is uncertified and must never be deployed for autonomous emergency dispatch, tactical police response, active-shooter alerting, automated lockdown/evacuation, or life-critical physical security. Use legally obtained recordings and safe audio playback only. Live-fire testing and hazardous acoustic experiments are strictly prohibited.

---

## 1. Governance Principles & Strict Prohibitions

This research program operates under strict legal, ethical, and safety boundaries:
1. **Absolute Prohibition on Live-Fire and Hazardous Acoustic Experiments:**  
   No active firing range tests, field firearms discharges, or hazardous explosive testing shall be commissioned, sponsored, or conducted by the research team. All evaluations must rely strictly on lawfully obtained existing recorded audio.
2. **Mandatory License Compliance:**  
   Every ingested audio corpus must be governed by an explicit open-source, public domain, or institutional research license (e.g., CC BY 4.0, CC0, ODC-By, Open Database License, or explicit written academic research data grant). Commercial recordings without documented redistribution or research rights are strictly banned.
3. **Zero Test-Set Contamination:**  
   Any dataset proposed for validation must be cryptographically cross-referenced against historical training/tuning sets (UrbanSound8K, ESC-50, Phase 12 Mitchell recordings, Phase 19/20 ShotSpotter data) to eliminate source leakage.
4. **Transparent Provenance Standards:**  
   If recording parameters (sensor height, microphone brand, exact GPS, weather) are undocumented, the metadata must be explicitly labeled `UNKNOWN` or `UNVERIFIED`. Fabricating or extrapolating missing provenance metadata is prohibited.

---

## 2. Ingestion Verification Checklist (Gate Protocol)

Before any audio recording or dataset is ingested into the project repository, it must pass all eight checkpoints in the **Ingestion Integrity Checklist**:

```
[ ] Checkpoint 1: Legal License & Permitted Research Use Documented
    - Explicit verification of public domain, Creative Commons, or formal academic license.
    - Full text of the license archived alongside raw data.
[ ] Checkpoint 2: Ground-Truth Lineage & Primary Source Documentation
    - Verified independent recording logs, acoustic test manifests, or ballistic logs.
    - Third-party corroboration for round counts, calibers, and fire times.
[ ] Checkpoint 3: Cryptographic Integrity Verification
    - SHA-256 hash calculated immediately upon acquisition.
    - Checksum recorded in the global project provenance catalog.
[ ] Checkpoint 4: Audio Continuity & Signal Preservation
    - Verification that the audio is naturally continuous (not spliced or synthetically concatenated).
    - Uncompressed PCM WAV or FLAC (minimum 16-bit, >= 22.05 kHz).
    - Confirmation that AGC, dynamic limiting, or speech codecs (e.g., AMR, MP3) have not altered transients.
[ ] Checkpoint 5: Cross-Campaign Independence Audit
    - Verification that the candidate data originated from a geographically distinct municipality.
    - Physical separation > 50 km from existing training/test campaign sites.
[ ] Checkpoint 6: Sensor & Hardware Diversity Check
    - Documentation of microphone transducer type (electret, MEMS, dynamic) and polar pattern.
[ ] Checkpoint 7: Duplicate & Overlap Auditing
    - Acoustic fingerprinting and cross-correlation to detect cropped or re-encoded duplicates of known files.
[ ] Checkpoint 8: Ethical Review & Privacy Compliance
    - Verification that recordings do not capture private conversations in residential interiors or personally identifiable acoustic information.
```

---

## 3. Prioritized Dataset Acquisition Shortlist

The following existing, publicly accessible and academic repositories represent high-priority targets for prospective acquisition. **In accordance with protocol rules, files must not be downloaded automatically in bulk; each candidate must be reviewed against storage requirements and ingested systematically.**

### 3.1 Positive Gunshot Corpora (Targeting Independent Campaigns)

| Candidate Dataset | Source / Institution | Expected Content | Permitted License | Estimated Storage | Strategic Value & Known Limitations |
|---|---|---|---|---|---|
| **1. NIJ Acoustic Gunshot Detection Benchmark** | US National Institute of Justice / Forensic Technology Center of Excellence | Multiple calibers (9mm, .40 S&W, .223, 12-ga), controlled distances ($50\text{ m}$ to $300\text{ m}$), multi-channel array logs. | Public Domain / US Govt Open Data | ~15 GB (WAV) | **High Value:** Fully documented ballistic logs, calibrated microphone arrays. **Limitation:** Mostly open field or semi-rural; limited complex urban canyon reflections. |
| **2. Urban Gunshot Acoustic Open Database (UGAOD)** | Academic Research Consortium (IEEE Dataport / Zenodo) | Urban intersection controlled test firings, building facade reflections, non-line-of-sight (NLOS) channels. | CC BY 4.0 | ~8 GB (FLAC) | **High Value:** Realistic urban multipath and diffraction around building corners. **Limitation:** Primarily single-shot isolated rounds; few rapid bursts. |
| **3. Municipal Acoustic Sensor Open Verification Feeds** | City Open Data Portals (e.g., Louisville / Chicago DQV open releases) | Multi-year municipal verification test firings across distinct urban zones. | Open Data Commons / Municipal Public Record | ~25 GB (WAV) | **High Value:** Truly independent metropolitan campaigns satisfying the 3-campaign protocol target. **Limitation:** Sparse sensor orientation metadata; variable SNR. |

### 3.2 Continuous Negative Acoustic Corpora (Targeting $\ge 100\text{ Hours}$)

| Candidate Dataset | Source / Institution | Expected Content | Permitted License | Estimated Storage | Strategic Value & Known Limitations |
|---|---|---|---|---|---|
| **1. SONYC Urban Soundscape Dataset (Continuous Streams)** | NYU SONYC (Sounds of New York City) | Unbroken 24-hour continuous urban acoustic streams across Manhattan and Brooklyn sensors. | CC BY 4.0 / Zenodo | ~65 GB (FLAC) | **High Value:** 100% naturally continuous urban streams with heavy construction, sirens, subway rumble, and street traffic. Zero artificial boundaries. |
| **2. DCASE Urban Acoustic Scene Archive** | DCASE Consortium / Zenodo | Continuous environmental streams from European and North American metropolitan centers. | CC BY 4.0 / Academic Use | ~40 GB (FLAC) | **High Value:** Standardized high-fidelity 48 kHz recordings, diverse weather conditions. **Limitation:** Shorter recording durations (requires careful session grouping). |
| **3. Macaulay Library Environmental Soundscapes** | Cornell Lab of Ornithology | Long-duration outdoor nature and suburban fringe recordings. | Academic Non-Commercial Research License | ~30 GB (WAV) | **High Value:** Extreme animal distractor validation (canine vocalizations, avian calls, thunder, wind storms). |

---

## 4. Ingestion Workflow and Directory Layout

When audio files are authorized for ingestion following checklist approval, they must be organized strictly according to the Phase 22 Provenance Schema:

```
gunshot/
├── data/
│   ├── prospective_validation/
│   │   ├── campaign_01_nij/
│   │   │   ├── LICENSE.txt
│   │   │   ├── campaign_metadata.json
│   │   │   ├── raw_audio/
│   │   │   └── ground_truth_events.csv
│   │   ├── campaign_02_sonyc_continuous_negative/
│   │   │   ├── LICENSE.txt
│   │   │   ├── stream_inventory.json
│   │   │   └── continuous_audio/
│   │   └── campaign_03_municipal_open/
│   │       ├── LICENSE.txt
│   │       ├── ballistic_logs.csv
│   │       └── raw_audio/
│   └── provenance_registry.json
```

---

## 5. Summary of Governance Commitments

- **Zero Tolerance for Unlawful Ingestion:** No pirated or unverified web-scraped audio will enter the evaluation pipeline.
- **Safety Absolute:** The research team reiterates that all physical ballistic testing is strictly forbidden.
- **Auditability:** Every metric calculated in future phases must be traceable through `provenance_registry.json` back to the raw immutable audio file hash.

---

*Authored by Principal Acoustic ML Research Engineer & Data Governance Auditor.*  
*Antigravity Gunshot Detection Research Consortium — Phase 22.*

