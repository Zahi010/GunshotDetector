# Phase 15 Independent Continuous Evaluation Report

**Safety Designation: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.**

## 1. Executive Summary

Phase 15 executed a continuous stream evaluation using a newly assembled, genuinely independent **2.00-hour continuous audio benchmark** (`phase15_independent_continuous_2hr.wav`).

Crucially, in compliance with Phase 15 Section 6:
- **Zero Historical Reuse:** None of the 120 ESC-50 tracks used in the Phase 13/14 continuous benchmark were reused.
- **Zero Artificial Looping:** The stream contains **1,440 distinct unexamined 5.0-second tracks**, providing 7,200.00 seconds (2.00 hours) of continuous exposure without repeating any clip.
- **Boundary Auditing:** Every segment boundary was indexed (`reports/phase15_stream_segments.csv`) and alerts within ±0.5s of transition boundaries were isolated.

---

## 2. Continuous False Alert Rates Across Frozen Detectors

| Detector Configuration | Profile | Total Exposure (hr) | Total False Alerts | False Alert Rate (alerts/hr) | Boundary Alerts (±0.5s) | Non-Boundary Alerts |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Phase 9 Baseline** | `balanced` | 2.00 | 75 | **37.50** | 19 | 56 |
| **Phase 13 Candidate** | `balanced` | 2.00 | 70 | **35.00** | 17 | 53 |
| **Phase 14 Balanced** | `balanced` | 2.00 | 70 | **35.00** | 17 | 53 |
| **Phase 14 High-Precision** | `high_precision` | 2.00 | 40 | **20.00** | 11 | 29 |
| **Phase 14 High-Sensitivity** | `high_sensitivity` | 2.00 | 112 | **56.00** | 34 | 78 |

---

## 3. False Alert Acoustic Category Breakdown

Distribution of false positive alerts across the primary acoustic confuser categories in the continuous stream:

| Category | Phase 9 Baseline | Phase 13 Candidate | Phase 14 Balanced | Phase 14 High-Precision | Phase 14 High-Sensitivity |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `airplane` | 1 | 3 | 2 | 1 | 3 |
| `brushing_teeth` | 0 | 0 | 0 | 0 | 1 |
| `cat` | 4 | 3 | 3 | 3 | 4 |
| `chirping_birds` | 2 | 1 | 2 | 0 | 3 |
| `clapping` | 1 | 1 | 1 | 1 | 1 |
| `clock_tick` | 1 | 1 | 1 | 0 | 1 |
| `cow` | 1 | 1 | 1 | 1 | 2 |
| `crackling_fire` | 0 | 0 | 0 | 0 | 1 |
| `crow` | 2 | 2 | 2 | 2 | 3 |
| `crying_baby` | 0 | 0 | 0 | 0 | 1 |
| `dog` | 2 | 0 | 0 | 0 | 1 |
| `door_wood_creaks` | 4 | 3 | 3 | 1 | 7 |
| `door_wood_knock` | 1 | 1 | 1 | 0 | 0 |
| `drinking_sipping` | 3 | 3 | 3 | 2 | 3 |
| `engine` | 1 | 1 | 1 | 0 | 0 |
| `fireworks` | 0 | 0 | 0 | 0 | 1 |
| `footsteps` | 3 | 4 | 3 | 2 | 9 |
| `frog` | 1 | 1 | 1 | 0 | 0 |
| `helicopter` | 5 | 5 | 5 | 3 | 6 |
| `hen` | 16 | 16 | 17 | 11 | 26 |
| `keyboard_typing` | 0 | 0 | 0 | 0 | 1 |
| `laughing` | 0 | 0 | 0 | 0 | 1 |
| `mouse_click` | 1 | 1 | 1 | 1 | 1 |
| `pig` | 0 | 1 | 0 | 0 | 2 |
| `rain` | 2 | 1 | 1 | 2 | 4 |
| `rooster` | 16 | 14 | 15 | 7 | 20 |
| `sea_waves` | 1 | 1 | 1 | 0 | 2 |
| `sheep` | 1 | 1 | 1 | 1 | 2 |
| `snoring` | 0 | 0 | 0 | 0 | 1 |
| `thunderstorm` | 1 | 0 | 0 | 0 | 1 |
| `vacuum_cleaner` | 1 | 1 | 1 | 0 | 1 |
| `washing_machine` | 1 | 1 | 1 | 0 | 1 |
| `wind` | 3 | 3 | 3 | 2 | 2 |

---

## 4. Processing Latency & Computational Overhead

Inference was measured per causal 0.48-second (7,680 samples) hop window:
- **Median Chunk Latency:** 1.47 ms
- **95th Percentile (P95) Latency:** 1.73 ms
- **99th Percentile (P99) Latency:** 4.49 ms
- **Maximum Chunk Latency:** 4.49 ms
- **Real-Time Factor:** 0.003 (real-time deadline = 480 ms)
- **Dropped Windows / Processing Errors:** 0 (100% chunks processed causally)

---

## 5. Transition Boundary Artifact Analysis

Because 1,440 discrete 5.0-second source recordings were concatenated to construct the 2.0-hour continuous evaluation stream, artificial splice boundaries exist every 5.0 seconds (1,439 boundaries).
- Under Phase 14 Balanced, 17 of 70 alerts (24.3%) occurred within ±0.5s of a track transition boundary.
- Splice discontinuities can introduce high-frequency transient steps that artificially elevate the crest factor.
- Excluding transition-associated artifacts, Phase 14 Balanced produced **26.50 alerts/hour** of pure intra-track false positives.

---

## 6. Critical Operational Takeaway

The continuous false alert rate of 35.00 alerts/hour proves conclusively that:
1. **The detector cannot be deployed autonomously** for life-safety dispatch or physical siren activation.
2. An alert every few minutes in complex outdoor/urban acoustic environments would overwhelm emergency monitoring personnel.
3. High-Precision profile reduces the rate to **20.00 alerts/hour**, but at the cost of reduced ballistic recall on muffled/pocket shots.
