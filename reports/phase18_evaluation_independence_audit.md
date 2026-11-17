# PHASE 18: Global Evaluation Independence, Data Lineage & Leakage Audit Report

> [!CAUTION]
> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.**  
> Experimental acoustic research prototype. Zero autonomous dispatch, police response, active-shooter alerting, or critical physical security deployment. Safe recorded audio playback only.

---

## 1. Executive Summary & Audit Mandate

Phase 18 conducted an exhaustive source-level and session-level independence audit across all **39 ground-truth ballistic events** evaluated in Phase 17's continuous streams (`model_phase17.py`, `model_phase14.py`).

The objective was to determine:
1. Whether any ballistic events leaked from training or validation datasets.
2. Whether the continuous streams consist of genuine natural field captures or calibrated spliced streams.
3. The true degree of session independence versus historical relation to prior testing datasets (Phases 7, 8, 12, 15, 16).
4. The statistical performance of detectors stratified strictly by provenance class.

### Key Audit Findings:
1. **Zero Training and Validation Data Leakage:**
   - **0 of the 39 events** appear in the Phase 1–4 training set (`manifests/train.csv`).
   - **0 of the 39 events** appear in the Phase 1–4 validation set (`manifests/val.csv`).
   - No direct audio file hash duplicates exist between training data and continuous evaluation events.
2. **Stream Composition Reality:**
   - Only **2 streams (Stream 01 and Stream 02, totaling 6 events)** are unbroken natural field recordings.
   - **Stream 01 (5 events):** Unbroken 55-second natural field capture from a firing range. Provenance audit traces this recording directly to the **Mitchell Roberts 2015 firing range campaign** (`HISTORICALLY_RELATED_SESSION`), sharing its recording environment and sensor profile with Phase 12 and Phase 7.
   - **Stream 02 (1 event):** Unbroken 8-second continuous capture from an urban sensor deployment (`SOURCE_INDEPENDENT_EXTERNAL`).
   - **Streams 03 and 04 (33 events):** **CALIBRATED TRANSPARENT SPLICED STREAMS**. They were constructed by embedding discrete ballistic clips into continuous background audio at precise timestamps with calibrated SNR. They must **never** be represented as natural continuous field audio.
3. **Session-Level Historical Relation:**
   - Out of the 39 physical events, **35 events (89.7%)** trace back to the Mitchell Roberts 2015 range recording campaign or are spliced from Phase 15 discrete clips.
   - Exactly **1 event (2.6%)** represents an untouched, natural, source-independent external recording (`P17-NAT-006`).
   - Exactly **3 events** in Stream 03 are spliced urban ShotSpotter recordings.

---

## 2. Provenance Taxonomy & Event Stratification

To ensure complete scientific integrity, all 39 events are partitioned into five mutually exclusive provenance categories:

| Provenance Group | Category Description | Tested Events (N) | Stream Association | Acoustic Nature |
|---|---|:---:|---|---|
| **Group A** | **All Evaluated Events** | 39 | Streams 01, 02, 03, 04 | Combined Benchmark Suite |
| **Group B** | **Source-Independent External** | 1 | Stream 02 (`P17-NAT-006`) | Unbroken natural urban sensor recording |
| **Group C** | **Historically Related Session** | 5 | Stream 01 (`P17-NAT-001`..`005`) | Unbroken natural range recording (Mitchell 2015) |
| **Group D** | **Calibrated Transparent Spliced** | 33 | Streams 03 & 04 (`P17-EV-001`..`033`) | Transparently constructed multi-threat test streams |
| **Group E** | **Reused Diagnostic Clips** | 33 | Stream 03 & 04 source clips | Spliced from Phase 15 discrete evaluation set |

---

## 3. Provenance-Stratified Performance Analysis (Phase 14 Balanced Baseline)

Evaluating detection recall separately by provenance group reveals critical domain nuances:

| Provenance Group | Events (N) | Phase 14 Balanced Detected | Missed Events | Group Recall (95% Wilson CI) | Median Latency | P95 Latency | Audit Commentary |
|---|:---:|:---:|:---:|:---:|:---:|:---:|---|
| **Group A: All Events** | 39 | 23 | 16 | **58.97%** [43.4%, 72.9%] | 0.60s | 1.64s | Headline aggregate benchmark metric |
| **Group B: Truly Source-Independent** | 1 | 0 | 1 | **0.00%** [0.0%, 79.3%] | N/A | N/A | **Extreme small-sample limitation (N=1)**; urban reverberation sub-threshold |
| **Group C: Historically Related Session** | 5 | 0 | 5 | **0.00%** [0.0%, 43.4%] | N/A | N/A | Range sequence below single-crest threshold in raw stream without splicing gain |
| **Group D: Calibrated Transparent Spliced** | 33 | 23 | 10 | **69.70%** [52.5%, 82.8%] | 0.60s | 1.64s | Controlled SNR testing across 6 acoustic conditions |

> [!IMPORTANT]
> **Scientific Honesty Regarding Small-Sample Constraints:**  
> Group B contains exactly **one event** in an 8-second file. A recall of 0/1 carries a 95% Wilson confidence interval of `[0.0%, 79.3%]`. It is statistically uninformative to draw definitive system conclusions from $N=1$. Acquisition of extensive, legally cleared, multi-hour continuous positive audio from diverse external municipal and tactical environments remains an unfulfilled requirement.

---

## 4. Leakage Verification Matrix

| Historical Corpus | Files Examined | Direct Hash Overlap | Session Overlap | Finding |
|---|:---:|:---:|:---:|---|
| **Phase 1–4 Training Set** | 176 | **0** | 0 | Clean — Zero training leakage |
| **Phase 1–4 Validation Set** | 34 | **0** | 0 | Clean — Zero validation leakage |
| **Phase 7 Independent Test** | 230 | 0 | 35 clips | Same 2015 range campaign |
| **Phase 8 Final Eval** | 246 | 0 | 35 clips | Same 2015 range campaign |
| **Phase 12 Independent Test** | 154 | 0 | 35 clips | Same 2015 range campaign |
| **Phase 15 Discrete Evaluation** | 47 | 33 clips | 33 clips | Source clips used to construct Stream 03 & 04 |

All detailed event lineage records are cataloged in [`phase18_global_lineage_matrix.csv`](file:///e:/gunshot/gunshot/reports/phase18_global_lineage_matrix.csv).
