# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY

**MANDATORY SAFETY DESIGNATION:**
This experimental acoustic machine-learning software is uncertified and must never be deployed for autonomous emergency dispatch, tactical police response, active-shooter alerting, automated evacuation, building lockdown, or life-critical physical security.

Use legally obtained recordings and safe audio playback only. Live-fire testing and hazardous acoustic experiments are strictly prohibited.

---

# PHASE 28 TECHNICAL AUDIT REPORT
## Cooldown Accounting Forensics, Interval Reconciliation & Exposure Lineage

**Document Identifier:** `PHASE28-REP-COOLDOWN-RECONCILIATION`  
**Phase:** `PHASE_28_INDEPENDENT_REPRODUCTION_CAMPAIGN_STATISTICS_COOLDOWN_FORENSICS`  
**Target Scope:** Cumulative 23-stream continuous negative benchmark (Phases 23–27)

---

## 1. Executive Summary

A critical priority of Phase 28 is the complete forensic audit of post-alert refractory cooldown accounting. In Phase 27, a numerical discrepancy emerged between the underlying exposure accounting ledger and the narrative summary tables:
- **Historical Cooldown Totals (17 Streams):** Phase 14 Balanced = **111.92 seconds**; Phase 17 Experimental = **101.92 seconds**.
- **AeroSonicDB Cooldown Totals (6 Streams):** Phase 14 Balanced = **342.00 seconds**; Phase 17 Experimental = **6,283.28 seconds**.
- **Simple Sums:** Phase 14 Balanced = **453.92 seconds**; Phase 17 Experimental = **6,385.20 seconds**.
- **Reported Phase 27 Narrative Totals:** Phase 14 Balanced = **455.52 seconds** ($\Delta = +1.60\text{ s}$); Phase 17 Experimental = **6,381.76 seconds** ($\Delta = -3.44\text{ s}$).

This forensic investigation traces the exact event-level timestamps, interval topologies, boundary conditions, and state-machine transitions across all 287 alerts and 23 continuous recordings.

### Primary Audit Findings:
1. **Source of the Narrative Discrepancy:** The underlying per-recording accounting CSV (`reports/phase27_exposure_accounting.csv`) and machine-readable lineage (`reports/phase27_processing_manifest.json`) strictly contain the exact sums: **453.92 seconds** for Phase 14 and **6,385.20 seconds** for Phase 17. The figures 455.52 s and 6,381.76 s appeared exclusively in the preliminary Markdown comparison table template and artifact manifest from an unmerged draft iteration ($\Delta_{P14} = +1.60\text{ s}$, $\Delta_{P17} = -3.44\text{ s}$).
2. **Identification of Two Distinct Cooldown Accounting Conventions:**
   - **Convention A (Instantaneous Refractory Window):** Assumes each alert is an instantaneous event at $t_{\text{alert}}$, and excludes $[t_{\text{alert}}, \min(T, t_{\text{alert}} + 2.0)]$. When merged, this yields **255.84 seconds** for Phase 14 and **316.56 seconds** for Phase 17.
   - **Convention B (Cluster-Extended Refractory Interval):** Accounts for multi-window detection clusters spanning non-zero physical durations $[s, e]$, excluding $[s, \min(T, e + 2.0)]$. When merged, this yields **453.92 seconds** for Phase 14 and **6,385.20 seconds** for Phase 17.
3. **No Negative Exposure Distortion:** In all 46 stream evaluations, eligible exposure remains strictly positive ($T_{\text{eligible}} > 0$). While Phase 17 suffered severe cluster fragmentation on continuous aircraft flyovers (excluding 2,574.16 seconds on Stream 3), the calculations strictly followed mathematically sound interval union algebra without double-counting.

---

## 2. Forensic Audit Questions (Items 1–8)

### Item 1: Are cooldown intervals inclusive or exclusive at their boundaries?
Cooldown intervals operate on continuous wall-clock time $t \in [0, T]$. Formally, an exclusion interval is defined as the half-open interval $[s, e)$. In discrete sample indexing at 16,000 Hz, sample indices $n \in [\lfloor s \cdot f_s \rfloor, \lfloor e \cdot f_s \rfloor - 1]$ are flagged as refractory dead-time. The Lebesgue measure of this interval is identically $e - s$, regardless of endpoint inclusion, ensuring zero boundary ambiguity.

### Item 2: Are overlapping cooldown intervals merged before summation?
**Yes.** All implementations in `run_phase23_negative_benchmark.py` and `evaluate_phase27_aerosonic.py` apply an explicit one-dimensional interval union algorithm:
1. Intervals are sorted chronologically by start timestamp: $(s_1, e_1), (s_2, e_2), \dots, (s_m, e_m)$.
2. If $s_{k+1} \le e_k$, the active interval is extended to $\max(e_k, e_{k+1})$.
3. Otherwise, the interval is appended to the merged list and a new interval begins.
4. Total cooldown dead-time is computed strictly as $\sum (e_{\text{merged}} - s_{\text{merged}})$.
Across the historical 17 streams, two alerts in `P27-NAT-STR-14` overlapped by exactly 0.08 seconds (alert timestamps at 322.08s and 324.00s; $322.08 + 2.0 = 324.08 > 324.00$), reducing the exclusion from 20.00s to 19.92s.

### Item 3: Are intervals clipped to recording boundaries?
**Yes.** Every cooldown interval is bounded by the upper temporal limit of the audio file:
$$e_k = \min(T_{\text{gross}}, t_{\text{alert}} + 2.0)$$
In the empirical benchmark, no alerts occurred within the final 2.0 seconds of any stream (the latest alert occurred at 3,550.56s in `P27-AERO-STR-03`, where $T = 3,600.0\text{s}$), so boundary truncation was not triggered in practice.

### Item 4: Is the same interval counted more than once?
**No.** Merging intervals before computing duration mathematically guarantees idempotence:
$$\mu\left(\bigcup_{k=1}^m I_k\right) \le \sum_{k=1}^m \mu(I_k)$$
Double subtraction is strictly prevented.

### Item 5: Do timestamps use consistent units and clock origins?
**Yes.** All timestamps are calibrated in seconds relative to $t = 0.000\text{ s}$ (the first audio sample of each continuous file). Frame windowing is governed by `HOP_SAMPLES = 7680` at 16,000 Hz ($\Delta t = 0.480\text{ s}$) with `WINDOW_SAMPLES = 15360` ($0.960\text{ s}$).

### Item 6: Was historical exposure recalculated using a changed implementation?
**No.** The 17 historical streams were kept strictly frozen. Their cooldown durations (111.92 s for Phase 14, 101.92 s for Phase 17) were imported verbatim from Phase 26 (`reports/phase26_exposure_accounting.csv`) without modification.

### Item 7: Is cooldown duration measured from alert onset, alert termination, or another event?
Here lies the key conceptual divergence:
- **Historical Methodology (Instantaneous):** Measured from **alert onset timestamp** $t_{\text{alert}}$ to $t_{\text{alert}} + 2.0\text{ s}$.
- **Phase 27 AeroSonicDB Methodology (Cluster-Extended):** Measured from **cluster onset** $s_{\text{cluster}}$ to **cluster release** $e_{\text{cluster}} + 2.0\text{ s}$.
Because AeroSonicDB flyovers spanned tens of seconds above the release threshold, cluster durations were substantial (e.g., 3.44s to 2,572.16s).

### Item 8: Do alerts at the end of a recording create cooldown exclusions beyond available duration?
**No.** As verified under Item 3, all intervals are explicitly clipped to $T_{\text{gross}}$. No recording produced negative eligible exposure or duration overshoot.

---

## 3. Complete Interval Accounting Ledger

The complete per-alert ledger is documented in [reports/phase28_cooldown_interval_ledger.csv](file:///e:/gunshot/gunshot/reports/phase28_cooldown_interval_ledger.csv).

### Summary Reconciliation Table

| Benchmark Segment | Stream Count | Phase 14 Alerts | P14 Cooldown (Conv A) | P14 Cooldown (Conv B) | Phase 17 Alerts | P17 Cooldown (Conv A) | P17 Cooldown (Conv B) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Historical 17 Streams** | 17 | 56 | 111.92 s | 111.92 s | 51 | 101.92 s | 101.92 s |
| **AeroSonicDB 6 Streams** | 6 | 72 | 143.92 s | 342.00 s | 108 | 214.64 s | 6,283.28 s |
| **Cumulative Total (23 Streams)** | **23** | **128** | **255.84 s** | **453.92 s** | **159** | **316.56 s** | **6,385.20 s** |
| *Phase 27 Narrative Report Value* | 23 | 128 | - | 455.52 s | 159 | - | 6,381.76 s |
| *Narrative Reporting Discrepancy* | - | 0 | - | **-1.60 s** | 0 | - | **+3.44 s** |

---

## 4. Exposure Reproduction Across Both Conventions

The full per-stream exposure comparison is documented in [reports/phase28_exposure_reproduction.csv](file:///e:/gunshot/gunshot/reports/phase28_exposure_reproduction.csv).

### Head-to-Head Impact on False Alert Rates

1. **Under Convention A (Instantaneous Union):**
   - Gross Monitored Exposure: 12.6460 hours.
   - Phase 14 Cooldown Exclusion: 255.84 s (0.0711 hr) $\rightarrow$ Net Eligible Exposure: **12.5749 hours** (99.4% retained).
   - Phase 14 Eligible Alert Rate: **10.1790 alerts/hour**.
   - Phase 17 Cooldown Exclusion: 316.56 s (0.0879 hr) $\rightarrow$ Net Eligible Exposure: **12.5581 hours** (99.3% retained).
   - Phase 17 Eligible Alert Rate: **12.6611 alerts/hour**.
   - Performance Delta: Phase 14 exhibits a **+24.4% lower false alert rate** than Phase 17.
2. **Under Convention B (Cluster-Extended Union — Primary Ledger):**
   - Gross Monitored Exposure: 12.6460 hours.
   - Phase 14 Cooldown Exclusion: 453.92 s (0.1261 hr) $\rightarrow$ Net Eligible Exposure: **12.5199 hours** (99.0% retained).
   - Phase 14 Eligible Alert Rate: **10.2237 alerts/hour** (95% CI: [8.5294, 12.1561]).
   - Phase 17 Cooldown Exclusion: 6,385.20 s (1.7737 hr) $\rightarrow$ Net Eligible Exposure: **10.8723 hours** (86.0% retained).
   - Phase 17 Eligible Alert Rate: **14.6243 alerts/hour** (95% CI: [12.4395, 17.0824]).
   - Performance Delta: Phase 14 exhibits a **+43.0% lower false alert rate** than Phase 17.

### Definitive Conclusion:
Under **both** accounting conventions, Phase 14 Balanced is unequivocally superior to Phase 17 Experimental. The narrative discrepancy of 1.60s (P14) and 3.44s (P17) in Phase 27 text does not alter any statistical conclusion, model ranking, or baseline determination. Phase 14 Balanced remains the default research baseline.

