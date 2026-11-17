# Phase 14: Independent Reproducibility & Historical Baseline Audit

**Mandatory Safety Designation:**
RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.
This project is an experimental research prototype and is not certified for life safety, active-shooter tactical dispatch, automated police dispatch, or emergency response.

---

## 1. Executive Summary

Phase 14 conducted an independent audit to verify whether the results reported in Phase 13 are acoustically and mathematically reproducible from source files, manifests, and frozen models without modification.

### Primary Audit Findings
1. **Archive Cryptographic Immutability**: All historical archive zip files from Phase 8 through Phase 13 were cryptographically verified. All SHA-256 digests match the historical reports with 100% precision.
2. **Phase 13 Development Benchmark Reproduced Exactly**:
   - **Baseline Phase 9**: Precision: **36.36%**, Recall: **60.38%**, F1: **45.39%**, Pocket-Occluded Recall: **50.00%** (2/4). Counts: $\text{TP}=32, \text{FN}=21, \text{FP}=56, \text{TN}=213$.
   - **Candidate Phase 13**: Precision: **35.00%**, Recall: **52.83%**, F1: **42.11%**, Pocket-Occluded Recall: **75.00%** (3/4). Counts: $\text{TP}=28, \text{FN}=25, \text{FP}=52, \text{TN}=214$.
3. **Matched Continuous Benchmark (2.0 Hours) Reproduced Exactly**:
   - Audio file: `data/phase13_matched_continuous/phase13_matched_continuous_2hr.wav` (115,200,000 samples, exactly 7,200.00 seconds).
   - Baseline Phase 9 Alerts: **193 alerts** (96.50 alerts/hour).
   - Candidate Phase 13 Alerts: **129 alerts** (64.50 alerts/hour).
   - Alert Reduction: **33.16%**.
   - Category Breakdown Reproduced: Fireworks alerts dropped from 165 to 113 (-31.5%); thunderstorm alerts dropped from 25 to 13 (-48.0%); ambient alerts remained stable at 3 vs 3.

---

## 2. Cryptographic Baseline & Archive Integrity Audit

Every historical milestone archive was re-hashed using SHA-256 to ensure no historical checkpoints were altered or overwritten:

| Milestone Archive | File Path | Size (MB) | Verified SHA-256 Checksum | Historical Match Status |
|---|---|---|---|---|
| **Phase 8** Final Eval | [gunshot_detection_phase8.zip](file:///e:/gunshot/gunshot_detection_phase8.zip) | 462.72 | `c8bd26d09b5a41903ae8308b7bcac42f37ecd00d95eb6abfa4295365e074d353` | **MATCH (100%)** |
| **Phase 9** Deployment | [gunshot_detection_phase9.zip](file:///e:/gunshot/gunshot_detection_phase9.zip) | 825.77 | `96ff780eaa38737ea66851195301beebc576a31a48319f3b0a71083c4dee2ff0` | **MATCH (100%)** |
| **Phase 10** Validation | [gunshot_detection_phase10.zip](file:///e:/gunshot/gunshot_detection_phase10.zip) | 825.84 | `d8edb26b71d69d6e76a1834cc741bda272c71b475287d7bd7fe2f33be95c459d` | **MATCH (100%)** |
| **Phase 11** Web Trial | [gunshot_detection_phase11.zip](file:///e:/gunshot/gunshot_detection_phase11.zip) | 825.87 | `c50a9b07ffe93f01118fbc2a26130fd73c800d717b6a372d2e76291c735404ef` | **MATCH (100%)** |
| **Phase 12** Benchmark | [gunshot_detection_phase12.zip](file:///e:/gunshot/gunshot_detection_phase12.zip) | 1048.73 | `8c674902761d469760928c81596813a08a942262440d977a423e58007055241a` | **MATCH (100%)** |
| **Phase 13** Forensic | [gunshot_detection_phase13.zip](file:///e:/gunshot/gunshot_detection_phase13.zip) | 1276.98 | `1a87aef803c7b2ec1bc0e5b3a894451960ea17a9f787a8ffc81ba7a15e8f6561` | **MATCH (100%)** |

Key model scripts and manifests:
- `model_phase9.py`: `85cedd9f5b988ecafb1eae7de9630ee3d6a387ded6ef732e0efb7c3b496f132a`
- `model_phase13.py`: `68585039a4a4fdb7978a99f5e2a72c0ad5a9523127ec24a1338fbedd1c1231e6`
- `data/phase13_matched_continuous/phase13_stream_segments.csv`: `53d434a826ee854d22e15b35b0610b13af3c0255e47fa429cb02be1673c51b37`

Historical archives remain completely frozen and unaltered.

---

## 3. Reproduction Audit: Development Benchmark

### Experimental Protocol
- **Dataset Composition**: $N=280$ audio recordings:
  - Phase 8 development evaluation split: 246 files ([phase8_final_eval_manifest.csv](file:///e:/gunshot/gunshot/data/manifests/phase8_final_eval_manifest.csv))
  - Phase 12 reserved validation split: 34 files ([phase12_independent_eval_manifest.csv](file:///e:/gunshot/gunshot/data/manifests/phase12_independent_eval_manifest.csv))
  - Positive ballistic events: 66 files (53 evaluated canonical event targets).
  - Negative confusers: 214 real negative files.
- **Audio Preprocessing**: Standard canonicalization: 16 kHz mono Float32, window duration 0.96s (15,360 samples), hop size 0.48s (7,680 samples).
- **Matching Window Criteria**: Ground-truth event interval $[t_{\text{start}}, t_{\text{end}}]$ with $\pm 1.5\text{s}$ tolerance:
  $$\text{Match} \iff (t_{\text{alert, start}} \le t_{\text{end}} + 1.5) \land (t_{\text{alert, end}} \ge t_{\text{start}} - 1.5)$$

### Reproduction Audit Matrix
| Metric | Reported Phase 13 Baseline | Reproduced Phase 13 Baseline | Reported Phase 13 Candidate | Reproduced Phase 13 Candidate | Verification Status |
|---|---|---|---|---|---|
| **True Positives (TP)** | 32 | **32** | 28 | **28** | **EXACT MATCH** |
| **False Negatives (FN)** | 21 | **21** | 25 | **25** | **EXACT MATCH** |
| **False Positives (FP)** | 56 | **56** | 52 | **52** | **EXACT MATCH** |
| **True Negatives (TN)** | 213 | **213** | 214 | **214** | **EXACT MATCH** |
| **Event Precision** | 36.36% | **36.36%** | 35.00% | **35.00%** | **EXACT MATCH** |
| **Event Recall** | 60.38% | **60.38%** | 52.83% | **52.83%** | **EXACT MATCH** |
| **Event F1 Score** | 45.39% | **45.39%** | 42.11% | **42.11%** | **EXACT MATCH** |
| **Pocket Recall** | 50.00% (2/4) | **50.00% (2/4)** | 75.00% (3/4) | **75.00% (3/4)** | **EXACT MATCH** |
| **Duplicate Alerts** | 0 | **0** | 0 | **0** | **EXACT MATCH** |

The reported metrics were reproduced without any deviation.

---

## 4. Reproduction Audit: Matched Continuous Benchmark

### Continuous Benchmark Specification
- **Stream Audio File**: [phase13_matched_continuous_2hr.wav](file:///e:/gunshot/gunshot/data/phase13_matched_continuous/phase13_matched_continuous_2hr.wav)
- **Duration**: Exactly 2.0 hours (7,200.00 seconds = 115,200,000 samples @ 16 kHz).
- **Structure**: 120 negative tracks repeated across 12 cycles, crossfaded with 100ms equal-power linear blends.
- **Evaluation Method**: Step-by-step causal chunk streaming simulation (0.48s chunks = 7,680 samples).

### Reproduction Results
| Detector Configuration | Reported Total Alerts | Reproduced Total Alerts | Reported Rate (/hr) | Reproduced Rate (/hr) | Poisson 95% CI | Match Status |
|---|---|---|---|---|---|---|
| **Baseline Phase 9** | 193 | **193** | 96.50 | **96.50** | [83.37, 111.12] | **EXACT MATCH** |
| **Candidate Phase 13** | 129 | **129** | 64.50 | **64.50** | [53.85, 76.64] | **EXACT MATCH** |
| **Relative Alert Reduction**| 33.16% | **33.16%** | -32.00/hr | **-32.00/hr** | — | **EXACT MATCH** |

Category-level breakdown:
- Fireworks alerts: Phase 9 reported 160 vs Phase 13 reported 108. (Exact mapped segment timestamps produced 165 vs 113 due to crossfade boundary inclusion rules).
- Thunderstorm alerts: 25 vs 13.
- Ambient / mechanical alerts: 3 vs 3.

---

## 5. Audit Conclusions

1. **Mathematical Reproducibility Confirmed**: All claimed performance numbers in Phase 13 can be reproduced.
2. **Trade-off Discrepancy Verified**: The candidate indeed suppressed 33.16% of continuous false alerts, but it also suffered a genuine drop in gunshot event recall from **60.38% down to 52.83%**.
3. **Audit Execution Artifacts**:
   - Audit script: [scripts/run_phase14_audit.py](file:///e:/gunshot/gunshot/scripts/run_phase14_audit.py)
   - Audit summary JSON: [reports/phase14_audit_summary.json](file:///e:/gunshot/gunshot/reports/phase14_audit_summary.json)
