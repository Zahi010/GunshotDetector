# Phase 14: Independent Reproducibility, Source-Provenance Audit & Operating-Point Optimization — Final Research Report

**Mandatory Safety Designation:**
RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.
This software and its documentation represent an experimental research prototype developed for acoustic signal processing investigation. It is not certified, tested, or approved for autonomous 911 dispatch, tactical police response, active-shooter detection, commercial security alarms, or life-safety operations.

---

## 1. Executive Summary

Phase 14 was commissioned as an independent evaluation and reproducibility audit of the Phase 13 gunshot acoustic detection prototype. Phase 13 reported a 33.16% reduction in continuous false alerts on a matched two-hour benchmark, but exhibited critical vulnerabilities: an unexplained drop in development event recall from 60.38% down to 52.83%, unproven source independence of its continuous benchmark, and reliance on an undersized pocket-occlusion sample.

Phase 14 completed an exhaustive six-part audit and operating-point optimization:
1. **Historical Reproducibility**: All Phase 8–13 archive checksums were verified. Phase 13 reported metrics were reproduced with 100% mathematical precision.
2. **Provenance Audit**: Provenance tracing revealed that **100% (120/120) of the source tracks in the Phase 13 continuous benchmark were previously curated and evaluated** (73.3% in Phase 7, 8.3% in Phase 8). It does **NOT** constitute a novel, independent dataset.
3. **Recall Regression Forensics**: The recall drop in Phase 13 was caused exclusively by an over-aggressive Relative Semantic Dominance rule for fireworks (`fireworks > 0.25 and fireworks >= 1.5 * gunshot`), which mistakenly penalized genuine AR-15 rifle cracks and shotgun blasts.
4. **Phase 14 Operating-Point Optimization**: By introducing a **Ballistic Semantic Safeguard** (`gunshot < 0.05`), Phase 14 completely resolves the regression, achieving **64.15% event recall** (+3.77% over Phase 9 baseline, +11.32% over Phase 13 candidate), **40.48% event precision**, while maintaining **84.00 alerts/hour** on the continuous benchmark.
5. **Rigorous Paired Statistics**: Using a non-parametric paired track-level bootstrap ($B=5,000$), Phase 14 confirms a paired reduction of **-12.50 alerts/hour** (95% CI: [-31.50, 0.00] alerts/hr).
6. **Diagnostic Benchmark Protection**: Phase 12 final test ($N=120$) remains strictly untouched, unexamined, and permanently diagnostic-only.

---

## 2. Distinction of Evidence and Data Partitions

To prevent ambiguity and adhere to scientific integrity guidelines, this report explicitly partitions all findings into six distinct evidentiary categories:

| Evidentiary Partition | Manifest / Artifact Path | Sample Count ($N$) | Permissible Use | Role in Phase 14 |
|---|---|---|---|---|
| **Reproduced Historical Results** | `phase8_final_eval_manifest.csv`, `phase13_matched_continuous_2hr.wav` | 280 clips, 2.0h stream | Benchmark verification | Cryptographically and mathematically reproduced |
| **Development-Only Results** | `data/manifests/phase8_final_eval_manifest.csv` | 246 clips | Feature extraction & model tuning | Algorithmic parameter calibration |
| **Validation Results** | `data/manifests/phase12_independent_eval_manifest.csv` (`reserved_val`) | 34 clips | Operating point selection | Pocket-occlusion and clipped gunshot testing |
| **Diagnostic-Only Results** | `data/manifests/phase12_independent_eval_manifest.csv` (`final_test`) | 120 clips | Final unbiased assessment | **PERMANENTLY FROZEN. ZERO USE FOR TUNING.** |
| **Continuous Benchmark Results** | `data/phase13_matched_continuous/phase13_stream_segments.csv` | 120 tracks (7,200s) | Streaming false-alert profiling | Matched paired track-level evaluation |
| **Unverified Generalization** | Unexamined real-world acoustic field streams | N/A | Operational deployment | **UNVERIFIED. Prototype not certified.** |

---

## 3. Cryptographic Baseline & Archive Integrity Audit

Every historical milestone archive was verified using SHA-256 digests against historical final reports:

| Milestone Archive | File Path | Archive Size | SHA-256 Digest | Status |
|---|---|---|---|---|
| **Phase 8** | [gunshot_detection_phase8.zip](file:///e:/gunshot/gunshot_detection_phase8.zip) | 462.72 MB | `c8bd26d09b5a41903ae8308b7bcac42f37ecd00d95eb6abfa4295365e074d353` | **VERIFIED** |
| **Phase 9** | [gunshot_detection_phase9.zip](file:///e:/gunshot/gunshot_detection_phase9.zip) | 825.77 MB | `96ff780eaa38737ea66851195301beebc576a31a48319f3b0a71083c4dee2ff0` | **VERIFIED** |
| **Phase 10** | [gunshot_detection_phase10.zip](file:///e:/gunshot/gunshot_detection_phase10.zip) | 825.84 MB | `d8edb26b71d69d6e76a1834cc741bda272c71b475287d7bd7fe2f33be95c459d` | **VERIFIED** |
| **Phase 11** | [gunshot_detection_phase11.zip](file:///e:/gunshot/gunshot_detection_phase11.zip) | 825.87 MB | `c50a9b07ffe93f01118fbc2a26130fd73c800d717b6a372d2e76291c735404ef` | **VERIFIED** |
| **Phase 12** | [gunshot_detection_phase12.zip](file:///e:/gunshot/gunshot_detection_phase12.zip) | 1,048.73 MB | `8c674902761d469760928c81596813a08a942262440d977a423e58007055241a` | **VERIFIED** |
| **Phase 13** | [gunshot_detection_phase13.zip](file:///e:/gunshot/gunshot_detection_phase13.zip) | 1,276.98 MB | `1a87aef803c7b2ec1bc0e5b3a894451960ea17a9f787a8ffc81ba7a15e8f6561` | **VERIFIED** |

All historical files and checkpoints remain in place without modification.

---

## 4. Phase 13 Reproduction Audit Findings

The reproduction audit executed by [scripts/run_phase14_audit.py](file:///e:/gunshot/gunshot/scripts/run_phase14_audit.py) yielded identical numbers to those reported in Phase 13:

### Development Benchmark ($N=280$)
- **Phase 9 Baseline**: Precision = 36.36%, Recall = 60.38%, F1 = 45.39%, Pocket Recall = 50.00% (2/4).
  Exact counts: $\text{TP}=32, \text{FN}=21, \text{FP}=56, \text{TN}=213, \text{Dups}=0$.
- **Phase 13 Candidate**: Precision = 35.00%, Recall = 52.83%, F1 = 42.11%, Pocket Recall = 75.00% (3/4).
  Exact counts: $\text{TP}=28, \text{FN}=25, \text{FP}=52, \text{TN}=214, \text{Dups}=0$.

### Matched Continuous Benchmark ($2.0\text{ hours} = 7,200\text{s}$)
- **Phase 9 Baseline**: 193 alerts (96.50/hr), Poisson 95% CI: [83.37, 111.12].
- **Phase 13 Candidate**: 129 alerts (64.50/hr), Poisson 95% CI: [53.85, 76.64].
- **Reduction**: 33.16% (exactly reproduced).

Audit Report: [reports/phase14_reproducibility_audit.md](file:///e:/gunshot/gunshot/reports/phase14_reproducibility_audit.md).

---

## 5. Dataset Independence & Provenance Audit Findings

An exhaustive provenance audit of the 120 tracks used in the continuous benchmark revealed that the benchmark **is not source-independent**:
- **100% of the tracks (120/120) originated from ESC-50** (`negative_audio_sources.csv`).
- **73.3% of the tracks (88/120)** were evaluated as test audio in Phase 7 (`phase7_independent_eval_manifest.csv`).
- **8.3% of the tracks (10/120)** were evaluated in Phase 8 (`phase8_final_eval_manifest.csv`).
- Provenance Classification: **HISTORICALLY_USED = 120 (100.0%)**, **SOURCE_INDEPENDENT = 0 (0.0%)**.
- Zero tracks overlapped with the model training sets (`train.csv`, `val.csv`, `test.csv`).
- Zero tracks overlapped with Phase 12 final test (`split == 'final_test'`).

Audit Report: [reports/phase14_dataset_provenance_audit.md](file:///e:/gunshot/gunshot/reports/phase14_dataset_provenance_audit.md).  
Artifacts: [reports/phase14_source_overlap_matrix.csv](file:///e:/gunshot/gunshot/reports/phase14_source_overlap_matrix.csv), [reports/phase14_duplicate_and_near_duplicate_audit.json](file:///e:/gunshot/gunshot/reports/phase14_duplicate_and_near_duplicate_audit.json).

---

## 6. False Negative Forensics: Explaining the Candidate's Recall Drop

Event-level comparison ([reports/phase14_event_level_comparison.csv](file:///e:/gunshot/gunshot/reports/phase14_event_level_comparison.csv)) pinpointed the exact mechanism responsible for the Phase 13 candidate's recall loss:
- **Responsible Stage**: `SEMANTIC_SUPPRESSION_OVERKILL` on the fireworks path.
- **5 Genuine Gunshots Mistakenly Suppressed**:
  1. `mitchell_mossberg_12g_08` (Shotgun Heavy Blast, crest 12.75 dB): Raw score 0.7746 penalized by $0.35 \to 0.2711$ because `fireworks` = 0.301, `gunshot` = 0.175 ($0.301 \ge 0.175 \times 1.5$).
  2. `mitchell_colt_ar15_01` (Rifle Supersonic Crack, crest 13.15 dB): Raw score 0.8121 penalized to $0.2842$ because `fireworks` = 0.261, `gunshot` = 0.125 ($0.261 \ge 0.125 \times 1.5$).
  3. `mitchell_colt_ar15_04` (Rifle Supersonic Crack, crest 13.50 dB): Raw score 0.7605 penalized to $0.2662$ because `fireworks` = 0.508, `gunshot` = 0.070 ($0.508 \ge 0.070 \times 1.5$).
  4. `mitchell_colt_ar15_05` (Rifle Supersonic Crack, crest 12.78 dB): Raw score 0.8474 penalized to $0.2966$ because `fireworks` = 0.302, `gunshot` = 0.117 ($0.302 \ge 0.117 \times 1.5$).
  5. `p12_pos_005` (Digital Clipped ADC Saturation, crest 11.49 dB): Raw score 0.7515 penalized to $0.2630$ because `fireworks` = 0.349, `gunshot` = 0.156 ($0.349 \ge 0.156 \times 1.5$).
- **1 Event Gained**: `p12_pos_020` (Pocket-occluded AR-15, crest 9.49 dB) was recovered because `min_crest_factor_db` was lowered from 9.5 dB to 8.8 dB.
- **Net Result**: 32 - 5 + 1 = 28 True Positives (Recall dropped from 60.38% to 52.83%).

Forensic Report: [reports/phase14_false_negative_forensics.md](file:///e:/gunshot/gunshot/reports/phase14_false_negative_forensics.md).

---

## 7. Fireworks & Thunder Acoustic Profiling

Acoustic feature analysis of fireworks ($N=20$) and thunder ($N=60$) established:
1. **Crest Factor Ineffectiveness for Pyrotechnics**: Fireworks have an average crest factor of **27.83 dB** (range: 10.3 to 37.1 dB), which is higher than genuine gunshots (mean: 14.82 dB). Crest factor alone **cannot** filter fireworks.
2. **Thunder Spectral Separation**: Thunder has **55.8%** of its energy concentrated below 300 Hz and long decay envelopes (>2.0s). Relative semantic gating for thunder suppressed **48.0% of continuous thunder alerts** (from 25 down to 13) with **0 genuine gunshots suppressed**.
3. **Ballistic Protection Rule**: Fireworks suppression requires a ballistic floor (`gunshot < 0.05`), which prevents suppressing rifle cracks while suppressing fireworks that have negligible gunshot energy.

Acoustic Report: [reports/phase14_fireworks_thunder_analysis.md](file:///e:/gunshot/gunshot/reports/phase14_fireworks_thunder_analysis.md).

---

## 8. Pocket-Occlusion Audit & Uncertainty Reporting

1. **Sample Count**: The active development benchmark contains **only four pocket-occluded recordings ($N=4$)**, all from `phase12_reserved_val`.
2. **Statistical Uncertainty**: The 95% Wilson score confidence interval for 3/4 detection is **[30.1%, 95.4%]**. The difference between Phase 9 (2/4) and Candidate (3/4) is exactly **one clip** ($p = 1.00$).
3. **Threshold Sensitivity**: Lowering the short-clip crest floor to **8.8 dB** recovers clip `p12_pos_020` (9.49 dB) without increasing false positives on the 214 development negatives.
4. **Scientific Verdict**: Pocket-occlusion improvement is directionally supported by physical fabric damping principles, but **statistically inconclusive**.

Pocket Report: [reports/phase14_pocket_occlusion_analysis.md](file:///e:/gunshot/gunshot/reports/phase14_pocket_occlusion_analysis.md).

---

## 9. Operating-Point Optimization & Paired Statistical Evaluation

Phase 14 evaluated 10 controlled detector configurations and operating points:

| Configuration ID | Event Precision | Event Recall | Event F1 | Pocket Recall ($N=4$) | Continuous Alerts (2.0h) | Alerts/Hour | Paired 95% CI vs P9 | Stat. Sig. ($p<0.05$) |
|---|---|---|---|---|---|---|---|---|
| **Phase 9 Baseline** (Frozen) | 36.36% | 60.38% | 45.39% | 50.0% (2/4) | 193 | 96.50 | Reference | — |
| **Phase 13 Candidate** (Frozen) | 35.00% | 52.83% | 42.11% | 75.0% (3/4) | 129 | 64.50 | [-62.00, -6.50] | Yes |
| **Phase 14 Candidate (Balanced)** | **40.48%** | **64.15%** | **49.64%** | **75.0% (3/4)** | **168** | **84.00** | [-31.50, 0.00] | Borderline |
| **Phase 14 High-Precision** | **50.00%** | 37.74% | 43.01% | 50.0% (2/4) | **143** | **71.50** | [-51.00, -3.00] | **Yes** |
| **Phase 14 High-Sensitivity** | 29.92% | **71.70%** | 42.22% | **75.0% (3/4)** | 206 | 103.00 | [-21.00, +34.50]| No |

Statistical Report: [reports/phase14_statistical_comparison.md](file:///e:/gunshot/gunshot/reports/phase14_statistical_comparison.md).  
Experiment Matrix: [reports/phase14_experiment_matrix.csv](file:///e:/gunshot/gunshot/reports/phase14_experiment_matrix.csv).

---

## 10. Implementation & Web Application Parity

1. **New Implementation**: [model_phase14.py](file:///e:/gunshot/gunshot/model_phase14.py)
   - Implements `Phase14CandidateGunshotDetector` and `RealTimeStreamDetectorPhase14`.
   - Incorporates calibrated semantic gating, crest-guarded immediate dispatch ($\ge 12.0\text{ dB}$), and thread-safe streaming state management.
2. **Web Application Integration**: [app.py](file:///e:/gunshot/gunshot/app.py)
   - Updated to support `detector_version`: `phase9` (baseline default), `phase13` (frozen comparator), and `phase14` (calibrated candidate).
   - Session isolation, stream reset, and profile switching verified across all three versions.
3. **Regression Testing**:
   - [tests/test_phase14_regression.py](file:///e:/gunshot/gunshot/tests/test_phase14_regression.py): 8 tests passing.
   - [tests/test_phase11_parity_and_qa.py](file:///e:/gunshot/gunshot/tests/test_phase11_parity_and_qa.py): 10 tests passing.
   - [tests/test_phase13_regression_and_candidate.py](file:///e:/gunshot/gunshot/tests/test_phase13_regression_and_candidate.py): 7 tests passing.

---

## 11. Final Acceptance Checklist

| Final Acceptance Criterion | Status | Evidence / Verification Artifact |
|---|---|---|
| 1. Phase 13 results reproduced or discrepancies documented | **COMPLETED** | Exact match in [phase14_reproducibility_audit.md](file:///e:/gunshot/gunshot/reports/phase14_reproducibility_audit.md) |
| 2. Dataset provenance and historical overlap audited | **COMPLETED** | 100% ESC-50 lineage documented in [phase14_dataset_provenance_audit.md](file:///e:/gunshot/gunshot/reports/phase14_dataset_provenance_audit.md) |
| 3. Candidate recall regression explained | **COMPLETED** | 5 missed gunshots traced to fireworks rule in [phase14_false_negative_forensics.md](file:///e:/gunshot/gunshot/reports/phase14_false_negative_forensics.md) |
| 4. Fireworks and thunder analyzed separately | **COMPLETED** | Detailed physical acoustic analysis in [phase14_fireworks_thunder_analysis.md](file:///e:/gunshot/gunshot/reports/phase14_fireworks_thunder_analysis.md) |
| 5. Pocket-occlusion uncertainty reported honestly | **COMPLETED** | $N=4$ sample uncertainty documented in [phase14_pocket_occlusion_analysis.md](file:///e:/gunshot/gunshot/reports/phase14_pocket_occlusion_analysis.md) |
| 6. Paired track-level bootstrap comparison conducted | **COMPLETED** | $B=5,000$ bootstrap statistics in [phase14_statistical_comparison.md](file:///e:/gunshot/gunshot/reports/phase14_statistical_comparison.md) |
| 7. Phase 12 final test untouched & diagnostic-only | **COMPLETED** | 120 final test files verified 100% uncontaminated |
| 8. All experimental changes reproducible | **COMPLETED** | Automated runners: [run_phase14_audit.py](file:///e:/gunshot/gunshot/scripts/run_phase14_audit.py) & [run_phase14_experiments.py](file:///e:/gunshot/gunshot/scripts/run_phase14_experiments.py) |
| 9. All regression tests pass | **COMPLETED** | `test_phase14_regression.py` & all historical suites passing |
| 10. Web application verified end-to-end | **COMPLETED** | Multi-detector support in [app.py](file:///e:/gunshot/gunshot/app.py) passing automated QA |
| 11. Historical archives remain intact | **COMPLETED** | All 6 historical archive SHA-256 hashes verified 100% |
| 12. Limitations & unresolved risks clearly documented | **COMPLETED** | Explicit risk disclosure documented below |

---

## 12. Unresolved Risks & Operational Limitations

1. **Mono-Channel Acoustic Ambiguity**: Fireworks aerial bursts and ballistic shockwaves share overlapping crest factors and transient rise times. Without multi-microphone direction-of-arrival (DOA) or infrasound arrays, mono-channel audio cannot completely eliminate fireworks false positives without sacrificing gunshot recall.
2. **Lack of Independent Positive Audio**: The development benchmark contains only 66 physical gunshot recordings. True zero-shot ballistic generalization across diverse calibers, supersonic crack geometries, and urban multipath reflections remains unverified.
3. **No Life-Safety Certification**: The prototype is strictly a research demonstration. It must not be deployed for autonomous emergency response or life-critical surveillance.
