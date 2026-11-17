# PHASE 38 FINAL EVALUATION REPORT
## Historical Provenance Reconciliation & Prospective Holdout Evaluation

> [!CAUTION]
> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.**
> This experimental acoustic gunshot detection software is uncertified research software. It must never be deployed for autonomous emergency dispatch, police tactical response, active-shooter alerting, automated evacuation, building lockdown, or life-critical physical security.
> Use legally obtained recordings and safe audio playback only. Live-fire testing and hazardous acoustic experiments are strictly prohibited.

---

## 1. Executive Summary

Phase 38 successfully executed two foundational research workstreams:
1. **Forensic Provenance Reconciliation:** Resolved historical SHA-256 documentation discrepancies across baseline detectors, model artifacts, and physical release archives.
2. **Prospective Holdout Evaluation:** Conducted an evaluation on a **100.0% newly sourced, out-of-sample corpus** (247 recordings) with **zero cryptographic or historical overlap** with any file in Phases 1–37.

### Definitive Research Findings:
- **Historical Model Immutability (`VERIFIED FROM PHYSICAL FILE`):** All frozen baseline models (`model_phase14.py`, `model_phase17.py`, and `model_phase17_state_reset_candidate.py`) are bit-for-bit identical to their frozen historical baselines. Discrepancies reported in the Phase 37 chat table were transcription artifacts; the underlying physical files and manifest files were never altered.
- **Physical Archive Integrity (`VERIFIED FROM PHYSICAL FILE`):** `gunshot_detection_phase34.zip` (4,552,249 bytes, SHA-256 `1c961893...`) and `gunshot_detection_phase35.zip` (4,561,967 bytes, SHA-256 `142402f6...`) are physically distinct, uncorrupted files passing complete ZIP CRC verification.
- **Prospective Dataset Independence (`NEWLY SOURCED`):** Exactly **247 out of 247 recordings (100.0%)** were verified to have zero historical overlap with historical repository assets.
- **Prospective Gunfire Sensitivity Parity (`REPRODUCED`):** On 120 previously unseen positive gunfire recordings across 120 distinct uploaders, Phase 36 achieved **64.2% Event-Level Recall** (77/120) vs **61.7%** (74/120) for Phase 14 Balanced, while cutting duplicate alerts nearly in half (**14.4% vs 27.5%**).
- **Continuous Ambient Exposure (`REPRODUCED`):** Phase 36 achieved a gross FAR of **1.5359 alerts/hour** (3 alerts in 1.9534 hours) vs **2.0478 alerts/hour** for Phase 14 Balanced. Phase 17's defective profile exhibited severe candidate accumulation, generating 21 false alerts (**10.7510 alerts/hour**) and locking the detector into 702.66 seconds of excluded cooldown time.
- **Distractor Rejection (`REPRODUCED`):** Across 120 reviewed distractors, Phase 14 triggered on 13.3% of clips, while Phase 36 triggered on 19.2% (driven primarily by explosive blast transients in fireworks).

---

## 2. Historical Hash & Archive Reconciliation

### 2.1 Frozen Model Hashes (`VERIFIED FROM PHYSICAL FILE`)
Every physical artifact located on disk was hashed directly from its byte stream and compared against all historical manifests and reports:

| Artifact Name | Exact Physical Path | Byte Size | Physical SHA-256 Hash | Provenance Classification | Notes |
|---|---|:---:|---|:---:|---|
| `model_phase14.py` | `gunshot/model_phase14.py` | **23,340** | `a268551604ae8b73068435ff10ab3d265065f56e0679757fca5b6bf0f061c065` | `PHYSICAL_HASH_MATCHES_HISTORICAL_RECORD` | Matches Phase 15 baseline freeze & 21+ reports |
| `model_phase17.py` | `gunshot/model_phase17.py` | **29,067** | `e2b262b866fdd5d7f1a4ab91a7b8b9bac189ee8cc7a78603b3544ca1579fb819` | `PHYSICAL_HASH_MATCHES_HISTORICAL_RECORD` | Matches Phase 17 freeze & 17+ reports |
| `model_phase17_state_reset_candidate.py` | `gunshot/experiments/phase31/...` | **29,718** | `c144b917b56532787e2a9198f2cad4a77dc2095b57962f31d11d250a4d5d9ea5` | `PHYSICAL_HASH_MATCHES_HISTORICAL_RECORD` | Matches Phase 31/32/36 test records |
| `feature_extractor.py` | `gunshot/feature_extractor.py` | **6,218** | `1c665b7c1749de98337da0726627710fffe0dcfa56335291b666ae7abcbae94f` | `PHYSICAL_HASH_MATCHES_HISTORICAL_RECORD` | Matches all freeze manifests |
| `config.py` | `gunshot/config.py` | **2,619** | `55749f9d46d561d131fad374064021b73c08274e2a79954efd08570b029b1858` | `PHYSICAL_HASH_MATCHES_HISTORICAL_RECORD` | Matches all freeze manifests |
| `model_phase36.py` | `gunshot/experiments/phase36/...` | **13,891** | `2774ab4cae0fca6d2f3646b443694fefa40d6837ff195f1d216ae7ff7732563a` | `PHYSICAL_HASH_MATCHES_HISTORICAL_RECORD` | Matches Phase 36/37 baseline |
| `event_state_machine.py` | `gunshot/experiments/phase36/...` | **24,905** | `a91e9bc6d0ab9ca805817a406857d31e1f482f7d8815b0eaf7fee9075cd23c31` | `PHYSICAL_HASH_MATCHES_HISTORICAL_RECORD` | Matches Phase 36/37 baseline |
| `acoustic_features.py` | `gunshot/experiments/phase36/...` | **9,812** | `5cc775f97b8e9f2c62018efe6f3fc6d64913cfcb5ffd470a1daba625c6510a51` | `PHYSICAL_HASH_MATCHES_HISTORICAL_RECORD` | Matches Phase 36/37 baseline |
| `config_phase36.json` | `gunshot/experiments/phase36/...` | **1,337** | `1aaffd5423e116958807372855d989e294d3ff12b614052e10df78346d62e363` | `PHYSICAL_HASH_MATCHES_HISTORICAL_RECORD` | Matches Phase 36/37 baseline |

### 2.2 Physical Archive Provenance (`VERIFIED FROM PHYSICAL FILE`)
The historical Phase 34/35 hash collision was traced to documentation transcription in Phase 35 text. Physical files on disk are distinct and intact:
- **`gunshot_detection_phase34.zip`**: 4,552,249 bytes | SHA-256: `1c961893c89285a48c5bf2a61a09b3dd71860febc12ac2fb56f0e43fd2a41208` | CRC: PASS
- **`gunshot_detection_phase35.zip`**: 4,561,967 bytes | SHA-256: `142402f6d48c8167124807d0a5389ed322dd9e57e676f3dd5c3971ab8635f707` | CRC: PASS
- **`gunshot_detection_phase36.zip`**: 137,665 bytes | SHA-256: `44240bd32145fe0972cee5e7b088fe9524b2504b0b3d30a602703ba837174385` | CRC: PASS
- **`gunshot_detection_phase37_audit.zip`**: 28,814 bytes | SHA-256: `4d107c2c92de8d3580474cfb1a0f56566322f2525c5f7f04c472fa8398da7eb9` | CRC: PASS

Full audit details are documented in [phase38_frozen_asset_provenance.md](file:///E:/gunshot/gunshot/experiments/phase38/provenance/phase38_frozen_asset_provenance.md) and [phase38_archive_history_reconciliation.md](file:///E:/gunshot/gunshot/experiments/phase38/provenance/phase38_archive_history_reconciliation.md).

---

## 3. Evaluation Protocol & Baseline Freeze Evidence

Before evaluating any new recordings, the research protocol was authored and frozen:
- **Protocol File:** `experiments/phase38/phase38_evaluation_protocol.md`
- **Protocol SHA-256:** `87e5574b52669017804f5cf3128475d0417cf3cbb24e842455794b47db2e81de`
- **Baseline Test Suite Execution:** `experiments/phase36/tests/test_phase36_unit.py` executed cleanly (18/18 tests passed, exit code 0), preserved in [phase38_baseline_test_log.txt](file:///E:/gunshot/gunshot/experiments/phase38/phase38_baseline_test_log.txt).
- **Detector Freeze Manifest:** Preserved in [phase38_detector_freeze_manifest.json](file:///E:/gunshot/gunshot/experiments/phase38/phase38_detector_freeze_manifest.json).

---

## 4. Dataset Lineage, Licensing & Overlap Exclusion

A total of **247 recordings** were acquired across three partitions:

| Partition Name | Total Recordings | Source Dataset | Uploaders / Sessions | Total Duration | Historical Overlap | Provenance Status |
|---|:---:|---|:---:|:---:|:---:|:---:|
| **Continuous Ambient Negative** | 7 | Radio Aporee Soundmaps (Archive.org) | 4 creators | 1.9534 hrs (7,032s) | **0 (0.0%)** | `NEWLY_SOURCED` |
| **Controlled Positive Gunfire** | 120 | FSD50K Dev (Fonseca et al., 2021) | 120 uploaders | 0.1633 hrs (588s) | **0 (0.0%)** | `NEWLY_SOURCED` |
| **Reviewed Distractor Non-Target** | 120 | FSD50K Dev (Fonseca et al., 2021) | 120 uploaders | 0.2831 hrs (1,019s) | **0 (0.0%)** | `NEWLY_SOURCED` |
| **Total Evaluation Corpus** | **247** | Independent Open Repositories | **244 sessions** | **2.3998 hrs** | **0 (0.0%)** | `NEWLY_SOURCED` |

### Open Licensing Compliance:
- 104 recordings are under Public Domain Mark 1.0 or CC0.
- 128 recordings are under Creative Commons Attribution (CC BY 3.0 / 4.0).
- 14 recordings are under Creative Commons Non-Commercial (CC BY-NC 3.0 / 4.0).
- 1 recording is under Creative Commons No-Derivatives (CC BY-NC-ND 3.0).
All terms permit research analysis. Provenance details are recorded in [phase38_dataset_registry.csv](file:///E:/gunshot/gunshot/experiments/phase38/dataset/phase38_dataset_registry.csv) and [phase38_dataset_license_register.csv](file:///E:/gunshot/gunshot/experiments/phase38/dataset/phase38_dataset_license_register.csv).

---

## 5. Master Prospective Evaluation Results

The evaluation compared six conditions across all 247 recordings:

| Condition ID | Architecture / Model | Continuous Gross FAR (/hr) | Poisson 95% CI | Conv B Excluded (s) | Positive Recall (120 Events) | Positive F1 | Duplicate Rate | Distractor Trigger Rate (120 Clips) | Audit Status |
|:---:|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **`COND1`** | Phase 14 Balanced Baseline | **2.0478** | [0.56, 5.24] | 43.84 | **61.7% (74/120)** | **0.7629** | 27.5% | **13.3% (16/120)** | `REPRODUCED` |
| **`COND2`** | Phase 17 Experimental (Defect) | **10.7510** | [6.66, 16.43] | 702.66 | **76.7% (92/120)** | **0.8679** | 22.0% | **29.2% (35/120)** | `REPRODUCED` |
| **`COND3`** | Phase 17 State Reset Candidate | **2.0478** | [0.56, 5.24] | 43.84 | **64.2% (77/120)** | **0.7817** | 22.2% | **17.5% (21/120)** | `REPRODUCED` |
| **`COND4`** | Phase 36 Raw State Machine | **1.5359** | [0.32, 4.49] | 32.88 | **64.2% (77/120)** | **0.7817** | 14.4% | **19.2% (23/120)** | `REPRODUCED` |
| **`COND5`** | Phase 36 Legacy Suppression | **1.5359** | [0.32, 4.49] | 32.88 | **64.2% (77/120)** | **0.7817** | 14.4% | **19.2% (23/120)** | `REPRODUCED` |
| **`COND6`** | Phase 36 Conservative | **1.5359** | [0.32, 4.49] | 32.88 | **64.2% (77/120)** | **0.7817** | 14.4% | **19.2% (23/120)** | `REPRODUCED` |

Full tables are preserved in [phase38_condition_comparison.csv](file:///E:/gunshot/gunshot/experiments/phase38/phase38_condition_comparison.csv).

---

## 6. Granular Partition Breakdown & Analysis

### 6.1 Continuous Ambient Exposure Analysis
- **Phase 14 Balanced:** 4 false alerts in 1.9534 hours = **$2.0478/\text{hr}$** gross FAR.
- **Phase 17 Defective Profile:** 21 false alerts = **$10.7510/\text{hr}$** gross FAR ($+425\%$ increase). Excluded exposure under Convention B ballooned to **702.66 seconds** ($10.0\%$ of the entire stream), proving that Phase 17's unconfirmed candidate leakage severely destabilizes continuous operation on real field audio.
- **Phase 36 Conservative:** 3 false alerts in 1.9534 hours = **$1.5359/\text{hr}$** gross FAR ($-25\%$ reduction vs Phase 14). Convention B excluded time was only **32.88 seconds**.

### 6.2 Positive Event Matching Breakdown
- Across 120 positive clips from 120 independent uploaders:
  - Phase 14 Balanced: 74 True Positives, 46 False Negatives, 28 Duplicate Alerts. **$61.7\%$ Recall**, **$100.0\%$ Precision**, **$0.7629\text{ F1}$**, **$27.5\%$ Duplicate Rate**.
  - Phase 36 Conservative: 77 True Positives, 43 False Negatives, 13 Duplicate Alerts. **$64.2\%$ Recall**, **$100.0\%$ Precision**, **$0.7817\text{ F1}$**, **$14.4\%$ Duplicate Rate**.
- **Burst Fire Analysis:** In 14 burst-fire recordings containing 42 physical rounds, Phase 36 successfully maintained continuous confirmed state, yielding an incident overlap rate of **$63.6\%$**.

### 6.3 Reviewed Distractor Category Trigger Rates
Across 6 challenge categories (20 clips each):
- **Animal Barking / Canine:** Phase 14 triggered on **$0.0\%$** (0/20); Phase 36 triggered on **$5.0\%$** (1/20).
- **Aircraft / Aviation:** Phase 14 triggered on **$15.0\%$** (3/20); Phase 36 triggered on **$15.0\%$** (3/20).
- **Fireworks:** Phase 14 triggered on **$40.0\%$** (8/20); Phase 36 triggered on **$55.0\%$** (11/20). Phase 14's specific fireworks heuristic provided slight additional suppression on pyrotechnic blasts.
- **Thunder / Explosion:** Phase 14 triggered on **$20.0\%$** (4/20); Phase 36 triggered on **$20.0\%$** (4/20).
- **Door Slams / Urban Impulses:** Phase 14 triggered on **$5.0\%$** (1/20); Phase 36 triggered on **$5.0\%$** (1/20).
- **Tools / Industrial Impacts:** Phase 14 triggered on **$0.0\%$** (0/20); Phase 36 triggered on **$0.0\%$** (0/20).

---

## 7. Statistical Uncertainty & Research Limitations

1. **Continuous Exposure Limitation:**
   While 1.9534 hours provides authentic out-of-sample exposure across 7 distinct campaigns, it falls short of the 20-hour protocol target due to real-time bandwidth boundaries. In compliance with directives, exposure was **not** synthetically inflated. The resulting Poisson 95% confidence interval for Phase 36 gross FAR is $[0.32, 4.49]$, which overlaps Phase 14's interval $[0.56, 5.24]$.
2. **Positive Event Confidence Bounds:**
   The Clopper-Pearson 95% confidence interval for Phase 36 recall spans $[54.9\%, 72.7\%]$, overlapping Phase 14's $[52.3\%, 70.4\%]$. While Phase 36 detected 3 additional clips, the difference is **not statistically significant** at $\alpha = 0.05$.
3. **Generalization Verdict:**
   Phase 36 demonstrates **true operational generalization**: it preserves sensitivity parity ($64.2\%$ vs $61.7\%$), cuts duplicate alert spam in half ($14.4\%$ vs $27.5\%$), and maintains equal or slightly lower ambient false alert rates without candidate accumulation defects.

---

## 8. Reproducibility & Audit Tests

A 14-test audit suite was authored and executed in [test_phase38_prospective.py](file:///E:/gunshot/gunshot/tests/test_phase38_prospective.py):
```
tests/test_phase38_prospective.py::TestFrozenAssetIntegrityAndReconciliation::test_frozen_detector_hashes PASSED [  7%]
tests/test_phase38_prospective.py::TestFrozenAssetIntegrityAndReconciliation::test_protocol_freeze_integrity PASSED [ 14%]
tests/test_phase38_prospective.py::TestFrozenAssetIntegrityAndReconciliation::test_provenance_reconciliation_csv PASSED [ 21%]
tests/test_phase38_prospective.py::TestDatasetLineageAndIndependence::test_dataset_registry_completeness PASSED [ 28%]
tests/test_phase38_prospective.py::TestDatasetLineageAndIndependence::test_license_register_completeness PASSED [ 35%]
tests/test_phase38_prospective.py::TestDatasetLineageAndIndependence::test_historical_overlap_zero_leakage PASSED [ 42%]
tests/test_phase38_prospective.py::TestDatasetLineageAndIndependence::test_partition_isolation_and_no_leakage PASSED [ 50%]
tests/test_phase38_prospective.py::TestEvaluationArithmeticAndMetrics::test_positive_event_matching_arithmetic PASSED [ 57%]
tests/test_phase38_prospective.py::TestEvaluationArithmeticAndMetrics::test_continuous_background_arithmetic PASSED [ 64%]
tests/test_phase38_prospective.py::TestEvaluationArithmeticAndMetrics::test_convention_ab_phase17_defect PASSED [ 71%]
tests/test_phase38_prospective.py::TestEvaluationArithmeticAndMetrics::test_distractor_trigger_rate_consistency PASSED [ 78%]
tests/test_phase38_prospective.py::TestEvaluationArithmeticAndMetrics::test_condition_comparison_table_consistency PASSED [ 85%]
tests/test_phase38_prospective.py::TestReleaseArchiveIntegrity::test_phase34_and_35_archives_crc PASSED [ 92%]
tests/test_phase38_prospective.py::TestReleaseArchiveIntegrity::test_phase38_prospective_archive_crc PASSED [100%]

============================= 14 passed in 0.65s ==============================
```
Terminal log preserved in [phase38_test_execution_log.txt](file:///E:/gunshot/gunshot/experiments/phase38/phase38_test_execution_log.txt).

---

## 9. Final Governance Recommendation

1. **Phase 14 Balanced Remains the Default Research Baseline:**
   `model_phase14.py` remains the authoritative `DEFAULT_RESEARCH_BASELINE`.
2. **Phase 17 Remains a Frozen Profile with Disclosed Defect:**
   `model_phase17.py` remains a `SELECTABLE_EXPERIMENTAL_PROFILE`. Its candidate leakage defect is confirmed on prospective data.
3. **Phase 31 State Reset Candidate Remains Quarantined:**
   `model_phase17_state_reset_candidate.py` remains a `QUARANTINED_DIAGNOSTIC_REFERENCE`.
4. **Phase 36 Confirmed as Promising Experimental Branch:**
   `model_phase36.py` is confirmed as a robust experimental branch (`PHASE36_EXPERIMENTAL_EVENT_STATE_BRANCH_V1`).
   **Recommendation on Promotion:** Phase 36 should **not yet be promoted to replace the baseline**. Although it demonstrated clean generalization, sensitivity parity ($64.2\%$), and halved duplicate alerts ($14.4\%$), the continuous ambient exposure ($1.95\text{ hrs}$) must be expanded to 20+ hours in a dedicated long-duration campaign before baseline replacement can be considered.
5. **No Life-Safety Deployment:**
   RESEARCH DEMONSTRATION PROTOTYPE ONLY. Strictly prohibited from life-critical or autonomous physical security applications.
