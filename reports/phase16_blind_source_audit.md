# PHASE 16: Discrete Blind-Evaluation Source & Leakage Audit

> [!CAUTION]
> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.**  
> Non-certified acoustic research prototype. Zero autonomous dispatch, police response, active-shooter notification, or critical security deployment.

---

## 1. Audit Mandate & Scope

Phase 16 Section 9 mandates an independent post-evaluation audit of the Phase 15 98-recording discrete blind evaluation set to confirm:
- Ground truth event counts (28 positive gunshot events, 70 confusers/ambiguous).
- Correct event-level matching without duplicate detection inflation.
- Absence of train-to-test leakage.
- Parent-source and recording-session leakage disclosure.
- Category label integrity.
- Formal retirement of the Phase 15 set from future blind status.

---

## 2. Partition Verification

| Sub-Partition | Count | Description | Verified Provenance Status |
|---|:---:|---|---|
| **Definitive Positive Events (`label = 1`)** | **28** | Ballistic recordings from Mitchell `testing/gunshots` (18 pocket, 4 clean, 6 clipped) | `HISTORICALLY_RELATED_SESSION` |
| **Definitive Negative Confusers (`label = 0`)** | **66** | 31 Mitchell training non-gunshot, 9 Mitchell testing non-gunshot, 26 ESC-50 unexamined | `HISTORICALLY_RELATED` (Mitchell) / `SOURCE_INDEPENDENT` (ESC-50) |
| **Ambiguous Edge Cases (`label = -1`)** | **4** | Difficult percussive transients (clapping, slamming, near-threshold transients) | `EVALUATION_EDGE_CASES` |
| **Total Non-Positive Benchmarks** | **70** | 66 definitive clean negatives + 4 ambiguous confusers | Audited |
| **Total Discrete Blind Set** | **98** | Evaluated in Phase 15 | **Permanently Inspected Diagnostic Evidence** |

*(Note: An additional 1 ambiguous item exists in validation, bringing repository ambiguous pool to 5).*

---

## 3. Event Matching & Duplicate Detection Audit

In Phase 15, event evaluation utilized a $\pm 0.75\text{s}$ tolerance window matching continuous alerts to annotated canonical gunshot onsets.
An audit of all 28 positive evaluation tracks verified:
1. **One-to-One Alert Matching:** In all true-positive cases, only **one true-detection credit** was assigned per physical event onset.
2. **Duplicate Suppression:** Second and third window triggers within the same gunshot envelope fell within the 2.0s cooldown window, preventing multi-counting.
3. **Double-Tap Integrity:** For rapid double-taps (e.g. `Ar15Double09`, `Ar15Double10`), each individual ballistic onset was evaluated against separate canonical event timestamps (`EV-P15-xxxx`).
4. **False Detection Isolation:** Confuser tracks were evaluated for spurious alerts over their full 5.0-second durations.

---

## 4. Parent-Source and Session Leakage Findings

### 4.1 Positive Recordings (Gunshots)
- **Train-to-Test Leakage:** Verified **0 SHA-256 collisions** between Phase 1-6 training sets (`train.csv`) and Phase 15 blind positives.
- **Recording-Session Leakage:** **CONFIRMED.** All 28 positive recordings originate from the same 2015 shooting range collection campaign conducted by Mitchell Roberts as Phase 12.
- **Acoustic Generalization Level:** Within-session, cross-condition generalization (clean training models generalizing to pocket-muffled and clipped variants from the same shooting range).

### 4.2 Negative Recordings (Confusers)
- **ESC-50 Negatives (26 clips):** 100% `SOURCE_INDEPENDENT`. Zero overlap with any prior training, validation, or diagnostic benchmark.
- **Mitchell Non-Gunshots (40 clips):**
  - 31 clips from `training/not-gunshot/`
  - 9 clips from `testing/non-gunshots/`
  - While cryptographically distinct from prior test files, these share the same parent repository and environment.

---

## 5. Formal Retirement of the Phase 15 Blind Set

In accordance with strict safety-critical ML evaluation standards:
1. **Inspected Diagnostic Evidence:** The Phase 15 benchmark has been examined, inspected, and diagnostically analyzed.
2. **Permanent Prohibition:** **Never reuse this 98-recording set as an untouched blind test in Phase 16 or any future phase.**
3. **Historical Benchmark Archival:** All 98 tracks remain preserved in `data/phase15_independent_eval/` for regression testing only.

*Audit signed off by Principal Acoustic ML Research Engineer and Dataset Provenance Auditor.*
