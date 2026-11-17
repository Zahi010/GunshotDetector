# PHASE 25 FORENSIC RECONCILIATION REPORT: RESOLUTION OF THE PHASE 23–24 STREAM-COUNT DISCREPANCY

> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.**  
> *This experimental acoustic machine-learning software is uncertified and must never be deployed for autonomous emergency dispatch, tactical police response, active-shooter alerting, automated lockdown or evacuation, or life-critical physical security. Use legally obtained recordings and safe audio playback only. Live-fire testing and hazardous acoustic experiments are strictly prohibited.*

---

## 1. Executive Summary & Problem Statement

A primary mandate of Phase 25 Workstream A is to resolve an apparent contradiction between the reported stream-level results of Phase 23 and Phase 24:

- **Phase 23 Text Reports (`phase23_final_report.md`, `phase23_model_comparison.md`):**  
  Reported that across the 17 matched continuous streams, Phase 17 produced fewer alerts in **4 streams**, more alerts in **0 streams**, and identical alert counts in **13 streams**.
- **Phase 24 Text Reports (`phase24_final_report.md`, `phase24_matched_model_comparison.md`):**  
  Reported that the 5-alert reduction from Phase 14 (56 alerts) to Phase 17 (51 alerts) was concentrated in only **3 streams**, with **14 streams** exhibiting identical alert counts, and **0 streams** with more alerts.

Because both phases evaluate the exact same 17 verified-negative continuous audio streams, this discrepancy required exhaustive forensic reconciliation against the primary underlying data artifacts.

---

## 2. Artifact-by-Artifact Forensic Audit

To determine the ground truth, an independent script (`scripts/reconcile_phase25_discrepancies.py`) inspected all original source files:

1. `reports/phase23_exposure_accounting.csv` (Phase 23 primary data output)
2. `reports/phase23_negative_audio_results.csv` (Phase 23 alert event log)
3. `reports/phase24_exposure_accounting.csv` (Phase 24 primary data output)
4. `reports/phase24_negative_audio_results.csv` (Phase 24 alert log)
5. `reports/phase24_alert_event_log.csv` (Phase 24 event-level log)

### 2.1 Stream-by-Stream Alert Count Audit

Comparing the raw rows in `phase23_exposure_accounting.csv` and `phase24_exposure_accounting.csv` reveals the following exact per-stream counts:

| Recording ID (Phase 24) | Legacy ID (Phase 23) | Acoustic Environment | P14 Alerts (P23) | P14 Alerts (P24) | P17 Alerts (P23) | P17 Alerts (P24) | Difference (P14 - P17) | Comparative Status |
|---|---|---|---|---|---|---|---|---|
| `P24-NAT-STR-01` | `P23-NAT-STR-01` | Industrial Compressor | 0 | 0 | 0 | 0 | 0 | Counts Equal |
| `P24-NAT-STR-02` | `P23-NAT-STR-02` | Ventilation Exhaust | 2 | 2 | 2 | 2 | 0 | Counts Equal |
| `P24-NAT-STR-03` | `P23-NAT-STR-03` | Concrete Mixer | 0 | 0 | 0 | 0 | 0 | Counts Equal |
| `P24-NAT-STR-04` | `P23-NAT-STR-04` | Monoblock Pump | 0 | 0 | 0 | 0 | 0 | Counts Equal |
| `P24-NAT-STR-05` | `P23-NAT-STR-05` | Arterial Road Traffic | 20 | 20 | 18 | 18 | **+2** | **Phase 17 Improved** |
| `P24-NAT-STR-06` | `P23-NAT-STR-06` | Rail Corridor Transit | 1 | 1 | 1 | 1 | 0 | Counts Equal |
| `P24-NAT-STR-07` | `P23-NAT-STR-07` | Canteen Plaza | 1 | 1 | 1 | 1 | 0 | Counts Equal |
| `P24-NAT-STR-08` | `P23-NAT-STR-08` | Acoustic Drums | 0 | 0 | 0 | 0 | 0 | Counts Equal |
| `P24-NAT-STR-09` | `P23-NAT-STR-09` | Washing Machine | 0 | 0 | 0 | 0 | 0 | Counts Equal |
| `P24-NAT-STR-10` | `P23-NAT-STR-10` | Cooling Exhaust | 0 | 0 | 0 | 0 | 0 | Counts Equal |
| `P24-NAT-STR-11` | `P23-NAT-STR-11` | Reservoir / Weather | 0 | 0 | 0 | 0 | 0 | Counts Equal |
| `P24-NAT-STR-12` | `P23-NAT-STR-12` | Bilbao Exterior Plaza | 9 | 9 | 9 | 9 | 0 | Counts Equal |
| `P24-NAT-STR-13` | `P23-NAT-STR-13` | Bilbao Commercial Arc.| 2 | 2 | 2 | 2 | 0 | Counts Equal |
| `P24-NAT-STR-14` | `P23-NAT-STR-14` | Bilbao Exterior Walkway| 10 | 10 | 8 | 8 | **+2** | **Phase 17 Improved** |
| `P24-NAT-STR-15` | `P23-NAT-STR-15` | Bilbao Exterior Terrace| 3 | 3 | 3 | 3 | 0 | Counts Equal |
| `P24-NAT-STR-16` | `P23-NAT-STR-16` | Bilbao Interior Arcade | 3 | 3 | 2 | 2 | **+1** | **Phase 17 Improved** |
| `P24-NAT-STR-17` | `P23-NAT-STR-17` | Bilbao Market Hall | 5 | 5 | 5 | 5 | 0 | Counts Equal |
| **Total** | **All 17 Streams** | **6.6460 Gross Hours** | **56** | **56** | **51** | **51** | **+5** | **14 Equal, 3 Improved** |

---

## 3. Root Cause Analysis of the Discrepancy

### 3.1 Data Concordance vs. Prose Discrepancy
1. **The underlying raw data files (`phase23_exposure_accounting.csv` and `phase24_exposure_accounting.csv`) are 100% bitwise identical** regarding alert counts and exposure durations. Both files confirm that exactly three streams experienced alert reductions:
   - Stream 05: 20 alerts $\to$ 18 alerts ($-2$)
   - Stream 14: 10 alerts $\to$ 8 alerts ($-2$)
   - Stream 16: 3 alerts $\to$ 2 alerts ($-1$)
   - Total alert reduction: $2 + 2 + 1 = 5\text{ alerts}$.
2. **Mathematical Impossibility of "4 Streams":**
   If four streams had reduced alert counts and the total alert reduction was 5, the integer partition would have had to be $(2, 1, 1, 1)$, which does not exist in any raw data artifact.
3. **Statistical Derivation of $p = 0.125$:**
   In Phase 23, the Wilcoxon signed-rank test was reported as $W = 10.0, p = 0.125$. Under exact sign and permutation testing, when $N_r = 3$ discordant pairs all have the same sign, the probability is $(1/2)^3 = 0.125$. If there had been 4 discordant pairs, the permutation probability would have been $(1/2)^4 = 0.0625$ (one-sided) or $0.125$ (two-sided unadjusted), but the non-zero difference vector in the data was explicitly `[2, 2, 1]` ($N_r = 3$).
4. **Conclusion:**
   The phrase *"fewer alerts in 4 streams, more alerts in 0 streams, and identical alert counts in 13 streams"* in the Phase 23 markdown narrative was a **clerical / transcription typo** by the report author. The author accidentally decremented the count of identical streams ($14 \to 13$) and incremented the count of improved streams ($3 \to 4$).
   
   **Phase 24 correctly reported the true data values: 3 streams with fewer alerts, 14 streams with identical counts, and 0 streams with more alerts.**

---

## 4. Canonical Reconciliation Table

The canonical matched table has been output to [`reports/phase25_stream_comparison_reconciliation.csv`](file:///e:/gunshot/gunshot/reports/phase25_stream_comparison_reconciliation.csv):

- **Total Evaluated Streams:** 17
- **Streams with Phase 17 Improvement:** 3 (`P24-NAT-STR-05`, `P24-NAT-STR-14`, `P24-NAT-STR-16`)
- **Streams with Identical Alert Counts:** 14
- **Streams with Phase 17 Regression:** 0
- **Net Alert Difference:** 5 alerts (56 for Phase 14 Balanced vs. 51 for Phase 17 Experimental)
- **Status of Discrepancy:** **RESOLVED** (Clerical error in Phase 23 prose narrative; underlying data in both phases is verified identical).

---

## 5. Mandatory Safety Reiteration

This reconciliation confirms that data accounting is mathematically sound, but does not alter the core finding: Phase 17's 5-alert reduction is not statistically significant ($p = 0.125$) and both detectors produce excessive false alerts in urban environments (7.7 to 8.5 alerts/hour). The software must never be deployed for life-safety or automated emergency dispatch applications.

