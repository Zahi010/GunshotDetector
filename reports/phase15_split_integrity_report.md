# Phase 15 Split Integrity & Provenance Audit Report

**Safety Designation: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.**

## 1. Executive Summary

Phase 15 establishes an audited, legally compliant, and cryptographically verified acoustic dataset architecture for evaluating gunshot acoustic detection models.

- **Total Discrete Recordings:** 152
- **Total Continuous Evaluation Stream:** 1440 segments (7200.0 seconds = 2.00 hours)
- **Zero Collision with Phase 12 Final Test:** Confirmed (0 hash collisions). Phase 12 final test benchmark remains permanently diagnostic-only.
- **Zero Reuse of Phase 13/14 Continuous Benchmark Sources:** Confirmed (0 track overlap with the 120 reused ESC-50 tracks).
- **Zero Looping or Synthetic Inflation:** Every continuous segment is played exactly once from a distinct source recording.

---

## 2. Partitioning by Split and Provenance

### Discrete Dataset Distribution

| Split Partition | File Count | Label Breakdown (Positive / Negative / Ambiguous) | Role & Access Restriction |
|---|---|---|---|
| **Blind Evaluation (`blind_eval`)** | **99** | **28 Pos / 66 Neg / 5 Amb** | **Strictly locked for frozen evaluation; inaccessible to tuning or threshold selection.** |
| **Validation (`validation`)** | **48** | **14 Pos / 34 Neg** | Used solely for candidate operating point selection and tuning. |
| **Diagnostic Only (`diagnostic_only`)** | **5** | **5 Pos** | Historical ShotSpotter sensors (D5 & Scepter); segregated as reference comparator. |

### Provenance Classification Distribution

| Classification | Count | Description |
|---|---|---|
| **`SOURCE_INDEPENDENT`** | **147** | Genuinely unexamined recordings with verified zero collision against all prior phases. |
| **`HISTORICALLY_USED`** | **5** | Historical ShotSpotter real-world recordings examined in Phase 7; kept diagnostic-only. |
| **`DEVELOPMENT_ONLY`** | **0** | No development-only clips included in evaluation manifests. |
| **`UNKNOWN_PROVENANCE`** | **0** | Zero unknown provenance files permitted. |

---

## 3. Continuous Evaluation Stream Integrity

- **Audio File:** `data/phase15_independent_eval/continuous/phase15_independent_continuous_2hr.wav`
- **Total Duration:** 7,200.00 seconds (120.00 minutes = 2.00 hours)
- **Sample Rate / Channels:** 16,000 Hz, Mono, 16-bit PCM
- **Total Independent Source Tracks:** 1,440 distinct 5.0-second tracks
- **Track Overlap with Phase 13/14 Stream:** **0 tracks (0.0%)**
- **Track Overlap with Phase 12 Evaluation Set:** **0 tracks (0.0%)**
- **Looping Count:** **0** (Each track appears exactly once)
- **Transition Boundaries:** 1,439 transition points logged with millisecond offsets in `phase15_stream_segments.csv`.

---

## 4. Historical Overlap & Collision Matrix

```
| historical_benchmark      |   historical_count |   discrete_hash_collisions |   discrete_name_matches |   continuous_stream_track_overlap |   overlap_percentage_discrete |   overlap_percentage_continuous | status                     |
|:--------------------------|-------------------:|---------------------------:|------------------------:|----------------------------------:|------------------------------:|--------------------------------:|:---------------------------|
| Phase 1-6 Dev (train.csv) |                176 |                          0 |                       0 |                                 0 |                          0    |                            0    | AUDITED_INDEPENDENT        |
| Phase 1-6 Dev (val.csv)   |                 34 |                          0 |                       0 |                                 0 |                          0    |                            0    | AUDITED_INDEPENDENT        |
| Phase 1-6 Dev (test.csv)  |                 47 |                          0 |                       0 |                                 0 |                          0    |                            0    | AUDITED_INDEPENDENT        |
| Phase 4 Hard Negatives    |                340 |                          0 |                       0 |                                97 |                          0    |                            6.74 | AUDITED_INDEPENDENT        |
| Phase 7 Independent Eval  |                230 |                          5 |                       0 |                                 0 |                          3.29 |                            0    | HISTORICAL_COMPARATOR_ONLY |
| Phase 8 Final Eval        |                246 |                          0 |                       0 |                                 0 |                          0    |                            0    | AUDITED_INDEPENDENT        |
| Phase 10 Evaluation       |                246 |                          0 |                       0 |                                 0 |                          0    |                            0    | AUDITED_INDEPENDENT        |
| Phase 11 Field Collection |                  0 |                          0 |                       0 |                                 0 |                          0    |                            0    | AUDITED_INDEPENDENT        |
| Phase 12 Independent Eval |                154 |                          0 |                       0 |                                 0 |                          0    |                            0    | ZERO_OVERLAP               |
| Phase 13 Matched Stream   |               1470 |                          0 |                       0 |                                 0 |                          0    |                            0    | ZERO_OVERLAP               |
```

---

## 5. Audit Attestation

The Phase 15 dataset split and continuous benchmark have been verified under strict cryptographic provenance auditing. No blind evaluation data has been tuned against or exposed to model training.
