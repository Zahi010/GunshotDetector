# PHASE 10 STAGE 4: DATASET PROVENANCE, PARTITION LEAKAGE & FIELD PROTOCOL AUDIT

> [!CAUTION]
> **SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY**  
> Claims of independent generalization must be supported by physical evidence from distinct geographical environments and hardware setups.

---

## 1. Executive Provenance Finding

An exhaustive audit of all **1,972 audio files on disk** and historical manifest files was conducted:
1. **Zero Data Leakage Between Training and Diagnostic Benchmarks:**  
   Cross-referencing training/validation manifests (`train.csv`, `val.csv`) against the diagnostic evaluation manifests (`phase7_independent_eval_manifest.csv`, `phase8_final_eval_manifest.csv`) confirmed **zero SHA-256 collisions** and **zero base stem overlaps**. The evaluation sets were never included in model training weights.
2. **Generalization Status: UNVERIFIED INDEPENDENT FIELD GENERALIZATION:**  
   All physical gunshot recordings on disk originated from:
   - AudioSet / FreeSound online repositories (used during Phases 1–7).
   - The Mitchell Roberts Open Ballistic Archive (added in Phase 8).  
   Both datasets were extensively examined, characterized, and used to design Phase 8/Phase 9 thresholding rules and the physical crest-factor guard.
   **Crucially, no genuinely unencountered field recordings from novel deployment sites exist on disk.**
3. **Mandatory Audit Compliance:**  
   In strict accordance with Non-Negotiable Rule 3 and Rule 7, **we do not relabel existing diagnostic recordings as independent field data**. Instead, we establish a formal field collection protocol, manifest schema ([`data/manifests/phase10_evaluation_manifest.csv`](file:///e:/gunshot/gunshot/data/manifests/phase10_evaluation_manifest.csv)), and annotation methodology for genuine future field trials.

---

## 2. Partition Cross-Leakage Matrix

Pairwise overlap analysis across all 5 repository manifests:

| Manifest Pair | First Manifest Rows | Second Manifest Rows | SHA-256 Collisions | Stem / Name Collisions | Audit Finding |
|---|---:|---:|---:|---:|---|
| **`train` vs `val`** | 102 | 34 | **0** | **0** | Clean holdout partition |
| **`train` vs `historical_test`** | 102 | 45 | **0** | **0** | Clean holdout partition |
| **`train` vs `phase7_diagnostic`** | 102 | 230 | **0** | **0** | **Zero leakage** |
| **`train` vs `phase8_diagnostic`** | 102 | 246 | **0** | **0** | **Zero leakage** |
| **`val` vs `phase7_diagnostic`** | 34 | 230 | **0** | **0** | **Zero leakage** |
| **`val` vs `phase8_diagnostic`** | 34 | 246 | **0** | **0** | **Zero leakage** |
| **`phase7_diagnostic` vs `phase8_diagnostic`** | 230 | 246 | **0** | **0** | Separate diagnostic suites |

*Detailed JSON Record:* [`reports/phase10_leakage_audit.json`](file:///e:/gunshot/gunshot/reports/phase10_leakage_audit.json).

---

## 3. Physical Audio Disk Inventory

Across the local repository, 1,972 audio files are distributed as follows:
- `data/hard_negatives/approved`: 732 files (mined in Phase 3/4).
- `data/background/hard_negatives/*`: 108 files (impulsive non-gunshot sounds: door slams, balloon bursts, toy gun pops, hammer impacts).
- `data/phase8_final_eval`: 246 files (43 ballistic gunshots, 200 ESC-50 mimics, 3 continuous streams).
- `data/phase7_independent_test`: 230 files (27 gunshot events, 200 mimics, 3 continuous streams).
- `data/processed/train`: 176 files (101 gunshots, 75 backgrounds).
- `data/processed/test`: 47 files (27 gunshots, 20 backgrounds).
- `data/processed/validation`: 34 files (22 gunshots, 12 backgrounds).
- `data/raw/background/*`: 340 files (machinery backfires, thunder, metallic chimes, sharp impacts).

---

## 4. Canonical Field Evaluation Manifest & Annotation Protocol

To prepare for true independent validation on new field recordings, [`data/manifests/phase10_evaluation_manifest.csv`](file:///e:/gunshot/gunshot/data/manifests/phase10_evaluation_manifest.csv) defines a strict 18-column schema:

### Canonical Schema Definition:
1. `field_recording_id`: Globally unique identifier (`P10-FIELD-XXXX`).
2. `primary_filename`: Exact audio filename.
3. `filepath`: Full relative path to lossless WAV (16 kHz, 16-bit mono float).
4. `sha256`: Cryptographic file checksum.
5. `sample_rate`: Native recording sample rate (Hz).
6. `duration_seconds`: Exact audio duration.
7. `ground_truth_label`:
   - `1`: Confirmed physical firearm discharge.
   - `0`: Verified acoustic negative mimic.
   - `-1`: **Uncertain / Ambiguous acoustic transient** (must NOT be forced into positive or negative labels).
8. `event_classification`: Categorical sound type (`confirmed_gunshot`, `verified_mimic`, `continuous_ambient`, `uncertain_transient`).
9. `weapon_type_caliber`: Specific firearm and ammunition (e.g. `9mm_Luger`, `12_gauge_shotgun`, `5.56x45mm_NATO`).
10. `microphone_hardware`: Microphone make, transducer type (MEMS / Electret / Dynamic), and pre-amp gain.
11. `distance_meters`: Physical standoff distance from muzzle to microphone.
12. `acoustic_environment`: Categorical setting (`urban_street_canyon`, `open_rural_field`, `indoor_hall`, `woodland`).
13. `weather_condition`: Atmospheric conditions (`clear`, `rain_light`, `wind_gusts`, `temperature_celsius`).
14. `estimated_snr_db`: Acoustic signal-to-noise ratio in decibels.
15. `physical_crest_factor_db`: Peak-to-RMS ratio.
16. `adjudication_status`: Verification standard (`confirmed_double_blind`, `verified_expert`, `unverified_single`).
17. `source_license`: Ownership and data provenance.
18. `notes`: Technical observations (e.g. digital clipping, microphone wind pop, reverberation time $T_{60}$).

### Strict Event-Matching Protocol:
- **One-to-One Canonical Matching:** A single detection alert cannot claim multiple physical gunshots.
- **Fixed Tolerance:** $\pm 0.50\text{ seconds}$ temporal matching window around ground-truth onset.
- **Duplicate Alerts:** Any secondary detection alert falling on an already-claimed physical gunshot within the refractory cooldown period is recorded as a **duplicate alert**, not a true positive.
- **Unmatched Alerts:** Any detection alert occurring during verified negative or non-event periods is classified as a **false positive**.
