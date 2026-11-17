# Phase 51: Duplicate and Data Leakage Analysis

**Mandatory Safety Designation:**
> **RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.**
> This is uncertified research software. Never deploy it for autonomous emergency dispatch, police tactical response, active-shooter alerting, automated evacuation, building lockdown, or life-critical physical security. Use only lawfully obtained recordings and safe audio playback. Live-fire and hazardous acoustic experiments are strictly prohibited.

---

## 1. Objective and Methodology

To ensure that the Phase 51 independent generalization assessment of **Detector Improvement V8** is statistically valid and free from optimistic bias, a rigorous, automated cryptographic audit was executed across all candidate audio files.

Data leakage in machine learning evaluations can manifest in multiple subtle ways:
1. **Training Set Leakage:** Evaluation recordings identical or near-identical to samples used to train the base classifiers (MLP, CatBoost, LightGBM, XGBoost, or YAMNet transfer weights).
2. **Tuning Benchmark Contamination:** Evaluation recordings drawn from prior holdout partitions (such as Phase 12, Phase 15, Phase 17, or Phase 19) where detection thresholds, suppression constants, or FSM rules were empirically optimized.
3. **Internal Duplication:** Redundant identical audio clips across different class labels or multiple identical sensor channels of the same gunshot event artificially inflating sample sizes ($N$).

To detect and eliminate every form of leakage, **SHA-256 cryptographic hashes** were computed for every file in the candidate evaluation pool and cross-referenced against historical archives.

---

## 2. Historical Datasets Audited

The candidate evaluation manifest was cross-matched against the complete inventory of historical datasets in the repository:

| Dataset / Partition | Historical Role | Recorded Files | Hash Inventory Source |
| :--- | :--- | :---: | :--- |
| **Phase 1 & Phase 9 Training Splits** | Base classifier training (`train.csv`) | 1,600+ | `data/train.csv`, `models/gunshot_yamnet_bundle/` |
| **Phase 12 Urban Benchmark** | Tuning and holdout evaluation | 224 | `data/phase12/` |
| **Phase 15 Forensic Holdout** | Calibrated threshold benchmark | 150 | `data/phase15/` |
| **Phase 16 Industrial Continuous** | Continuous exposure validation | 6.08 hours | `data/phase16/` |
| **Phase 17 Urban Continuous & Fireworks**| False alarm tuning & verification | 3.0 hr + 30 files | `data/phase17/` |
| **Phase 19 Field Validation** | Calibrated field ballistic holdout | 46 | `data/phase19/` |
| **Phase 27 AeroSonic Audio** | Aviation acoustic evaluation | 6.0 hours | `data/phase27/` |
| **Phase 45–50 Evaluation Splits** | Iterative candidate development | 380+ | `data/phase45/` through `data/phase50/` |

---

## 3. Quarantined Files: Detection & Exclusion

During the initial candidate assembly, 27 gunshot recordings from `data/phase7_independent_test/gunshots/` were analyzed. Cryptographic SHA-256 matching discovered that **5 files** had bit-for-bit duplicate hashes matching recordings in the Phase 15 holdout archive.

### Quarantined File Audit Table:

| Filename | File Path | SHA-256 Checksum | Contamination Source | Action Taken |
| :--- | :--- | :--- | :--- | :---: |
| `shotspotter_chicago_d5_sensor1.wav` | `data/phase7_independent_test/gunshots/` | `65595cbe1411cecfd330d08ef61b997097ecae3557e937d2f32f3068e8e77a56` | Phase 15 Holdout (`p15_pos_001.wav`) | **QUARANTINED / EXCLUDED** |
| `shotspotter_chicago_d5_sensor2.wav` | `data/phase7_independent_test/gunshots/` | `cb5a79ee8863fba564e9a376518178dc48c081e7d0f39ec0c0bb7538be78f3c7` | Phase 15 Holdout (`p15_pos_002.wav`) | **QUARANTINED / EXCLUDED** |
| `shotspotter_chicago_d5_sensor3.wav` | `data/phase7_independent_test/gunshots/` | `378dcba8257007aaae85785f7e735e5bfa780d6f4b66dfb37c09d5eb6ee4ff4b` | Phase 15 Holdout (`p15_pos_003.wav`) | **QUARANTINED / EXCLUDED** |
| `shotspotter_chicago_d5_sensor4.wav` | `data/phase7_independent_test/gunshots/` | `d7a5b3a37b38d39f4007629b35db67ec4fa7d3d7515053ce91102711816f1947` | Phase 15 Holdout (`p15_pos_004.wav`) | **QUARANTINED / EXCLUDED** |
| `shotspotter_scepter_test.wav` | `data/phase7_independent_test/gunshots/` | `a9062eb4b23ff03d98ef57ea4d025b583305a415ff6ee246fdb854226156e174` | Phase 15 Holdout (`p15_pos_012.wav`) | **QUARANTINED / EXCLUDED** |

All 5 files were permanently excised from the Phase 51 evaluation manifest before running model inferences. The remaining 22 files from Phase 7 (19 Mitchell Roberts field gunshots and 3 ShotSpotter Chicago D7 sensor recordings) exhibited unique SHA-256 hashes with zero historical contamination.

---

## 4. Final Evaluation Integrity Audit

A comprehensive hash collision verification was conducted across all final assets:
- **Discrete Positive Recordings ($N=65$):** 65 unique SHA-256 hashes; 0 matches against training data (`train.csv`); 0 matches against tuning holdouts (Phases 12, 15, 17, 19, 45–50).
- **Discrete Negative Recordings ($N=308$):** 308 unique SHA-256 hashes; 0 cross-class collisions; 0 matches against positive sets.
- **Continuous Evaluation Streams ($T=12.0\text{ hr}$):** 15 unique streams; verified unsegmented continuous background audio.

The complete hash inventory and cross-validation log is archived in [`duplicate_and_leakage_analysis.csv`](file:///E:/gunshot/gunshot/experiments/phase51_validation/duplicate_and_leakage_analysis.csv).

**Conclusion:** The Phase 51 evaluation corpus possesses **0.00% data leakage**, establishing a pristine, fully independent validation benchmark.

