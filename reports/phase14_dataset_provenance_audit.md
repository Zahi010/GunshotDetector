# Phase 14: Dataset Independence & Historical Source-Provenance Audit

**Mandatory Safety Designation:**
RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.
This project is an experimental research prototype and is not certified for life safety, automated 911 dispatch, or critical security monitoring.

---

## 1. Scope & Objective

Section 4 of the Phase 14 directive requires an exhaustive, forensic provenance audit of the 120 source tracks used to construct the Phase 13 continuous benchmark:
`data/phase13_matched_continuous/phase13_matched_continuous_2hr.wav`
(assembled from `data/raw/background/`).

The primary objective is to determine whether these recordings represent **genuinely independent, novel acoustic recordings** or whether they were **historically used** in earlier training, validation, development benchmarking, or hard-negative mining splits.

Every source track must receive an explicit, unambiguous classification from the mandatory set:
- `HISTORICALLY_USED`
- `DEVELOPMENT_ONLY`
- `VALIDATION_ONLY`
- `DIAGNOSTIC_ONLY`
- `SOURCE_INDEPENDENT`
- `UNKNOWN_PROVENANCE`

---

## 2. Methodology & Cryptographic Auditing Protocol

Each of the 120 tracks was audited across five independent dimensions:
1. **Raw File SHA-256 Digest**: Exact binary cryptographic hash of the source `.wav` file on disk.
2. **Canonical Decoded Audio SHA-256 Digest**: 16 kHz mono Float32 audio waveform hash to identify re-encoded, resampled, or converted audio files with identical content.
3. **Manifest Cross-Referencing**: Exact matching against:
   - Phase 1–4 Training Splits: `data/manifests/train.csv`, `val.csv`, `test.csv`
   - Master Source Repository: `data/manifests/negative_audio_sources.csv`
   - Phase 7 Manifest: `data/manifests/phase7_independent_eval_manifest.csv`
   - Phase 8 Manifest: `data/manifests/phase8_final_eval_manifest.csv`
   - Phase 10 Manifest: `data/manifests/phase10_evaluation_manifest.csv`
   - Phase 11 Manifest: `data/manifests/phase11_field_collection_manifest.csv`
   - Phase 12 Manifest: `data/manifests/phase12_independent_eval_manifest.csv`
4. **Directory Structure & Historical Lineage**: Tracing directory parent paths across `data/raw/background/`, `data/background/hard_negatives/`, and `data/hard_negatives/approved/`.
5. **Session and Parent Attribution**: Extraction of original recording IDs, ESC-50 clip stems, Freesound URLs, and licensing metadata.

---

## 3. Provenance Audit Results & Classification Breakdown

### Master Classification Summary
Out of 120 unique source tracks evaluated in the Phase 13 continuous benchmark:

| Provenance Classification | Count | Percentage | Description |
|---|---|---|---|
| **HISTORICALLY_USED** | **120** | **100.0%** | Previously curated, evaluated, or benchmarked in prior phases |
| **SOURCE_INDEPENDENT** | **0** | **0.0%** | Genuinely novel, previously unexamined acoustic recordings |
| **DEVELOPMENT_ONLY** | **0** | **0.0%** | Restricted exclusively to development training/tuning splits |
| **VALIDATION_ONLY** | **0** | **0.0%** | Restricted to reserved validation split |
| **DIAGNOSTIC_ONLY** | **0** | **0.0%** | Restricted to Phase 12 final test benchmark (permanently diagnostic) |
| **UNKNOWN_PROVENANCE** | **0** | **0.0%** | Unidentifiable provenance or missing chain-of-custody |

### Historical Overlap Breakdown by Manifest
Every track was cross-referenced across historical repository manifests:

1. **Phase 1–4 Training Datasets (`train.csv`, `val.csv`, `test.csv`)**:
   - Matches: **0 / 120 (0.0%)**. None of the 120 continuous benchmark tracks were used in model weights training (CatBoost, LightGBM, XGBoost, or Keras MLP).
2. **Phase 7 Independent Evaluation Manifest (`phase7_independent_eval_manifest.csv`)**:
   - Matches: **88 / 120 (73.33%)**.
   - Exactly 88 of the 120 tracks were evaluated as discrete test clips during Phase 7.
3. **Phase 8 Final Evaluation Manifest (`phase8_final_eval_manifest.csv`)**:
   - Matches: **10 / 120 (8.33%)**.
   - 10 tracks (specifically ESC-50 crackling fire clips `1-17150-A-12.wav`, `1-17565-A-12.wav`, etc.) were evaluated in Phase 8 final evaluation under the category `mimic_crackling_fire`.
4. **Curated ESC-50 Negative Pool (`negative_audio_sources.csv`)**:
   - Matches: **120 / 120 (100.0%)**.
   - All 120 tracks originated from the Freesound ESC-50 curation performed during earlier phases. The remaining 22 tracks that were not selected into Phase 7 or 8 discrete evaluation manifests were approved real negatives residing in the repository's background pool.
5. **Phase 12 Independent Evaluation Benchmark (`phase12_independent_eval_manifest.csv`)**:
   - Matches: **0 / 120 (0.0%)**.
   - None of the Phase 13 continuous benchmark files originated from the Phase 12 dataset.

---

## 4. Integrity and Diagnostic Protection of Phase 12

A critical requirement of Phase 14 is verifying that the Phase 12 final test benchmark remains **strictly untouched, uncontaminated, and diagnostic-only**.

### Verification Findings:
- Total Phase 12 Final Test recordings: 120 files (`split == 'final_test'`).
- Total Phase 12 Reserved Validation recordings: 34 files (`split == 'reserved_validation'`).
- Overlap between Phase 12 Final Test and Phase 13 continuous benchmark: **0 files (0.0%)**.
- Overlap between Phase 12 Final Test and Phase 14 development/tuning scripts: **0 files (0.0%)**.
- Status: **PHASE 12 FINAL TEST REMAINS PERMANENTLY DIAGNOSTIC-ONLY AND HAS ZERO CONTAMINATION**.

---

## 5. Critical Disclosure Regarding Phase 13 Continuous Benchmark Independence

> [!CAUTION]
> **DISCLOSURE OF BENCHMARK LINEAGE**:
> The Phase 13 continuous benchmark **CANNOT BE CLAIMED TO BE AN INDEPENDENT NOVEL DATASET**.
> 
> Although the files were assembled into a new continuous streaming format (with 100ms crossfading and 12-cycle repetition), **73.3% of the audio tracks had already been evaluated in Phase 7**, and **8.3% had been evaluated in Phase 8**.
> 
> Therefore, the 33.16% false-alert reduction reported in Phase 13 represents performance on a **familiar, historically curated acoustic pool**, NOT proof of zero-shot generalization to novel outdoor environments.

---

## 6. Audit Artifacts & Audit Logs

- Full overlap matrix (all 120 tracks with SHA-256 and history): [reports/phase14_source_overlap_matrix.csv](file:///e:/gunshot/gunshot/reports/phase14_source_overlap_matrix.csv)
- Duplicate and near-duplicate audit report: [reports/phase14_duplicate_and_near_duplicate_audit.json](file:///e:/gunshot/gunshot/reports/phase14_duplicate_and_near_duplicate_audit.json)
- Provenance verification runner: [scripts/run_phase14_audit.py](file:///e:/gunshot/gunshot/scripts/run_phase14_audit.py)
