# PHASE 35 FINAL FORENSIC REPORT
## Cooldown Ledger Reconciliation, Campaign Independence Qualification & Benchmark Closure

> [!CAUTION]
> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.**
> This experimental acoustic machine-learning software is uncertified and must never be deployed for autonomous emergency dispatch, police tactical response, active-shooter alerting, automated evacuation, building lockdown, or life-critical physical security.
> Use legally obtained recordings and safe audio playback only. Live-fire testing and hazardous acoustic experiments are strictly prohibited.

---

## 1. Executive Summary

Phase 35 represents the definitive closure of the historical continuous-audio benchmark audit across the 23-stream negative evaluation corpus ($12.6460\text{ gross hours}$, 287 cumulative alerts).

This phase resolved all outstanding arithmetic, methodological, and terminology questions:
1. **The 10-Second Discrepancy Resolved (`REPRODUCED WITH CORRECTION`):**
   The apparent $10.00\text{-second}$ difference between Phase 34's narrative table ($6,395.20\text{ s}$) and historical records ($6,385.20\text{ s}$) was traced to a cross-detector column transposition in Phase 34's summary text. Phase 14's European campaign cooldowns ($48.00\text{ s}$ and $63.92\text{ s}$) were accidentally read into Phase 17's total instead of Phase 17's true values ($44.00\text{ s}$ and $57.92\text{ s}$). The difference of exactly $(48.00 - 44.00) + (63.92 - 57.92) = \mathbf{+10.00\text{ seconds}}$ accounts for the exact 5 animal-suppressed alerts. The underlying per-recording data has remained completely consistent across all phases at **$6,385.20\text{ seconds}$**.
2. **Unrounded Cooldown-Adjusted Rates Recomputed (`REPRODUCED`):**
   Full unrounded rates were computed across stream, campaign, and corpus levels. Under Convention B, Phase 14 Balanced achieves **$10.2237\text{ alerts/eligible hr}$** ($453.92\text{ s}$ excluded), while Phase 17 Experimental exhibits **$14.6243\text{ alerts/eligible hr}$** ($6,385.20\text{ s}$ excluded).
3. **"False Alert" Descriptive Classification Audited (`REPRODUCED WITH CORRECTION`):**
   Of the 287 alerts, **107 alerts** (all European events) qualify as `REVIEWED_NON_TARGET` based on Phase 24 double-blind expert listening evaluation. The remaining **180 alerts** (all Adelaide Airport events) qualify as `UNANNOTATED_BACKGROUND` because they occur in continuous ambient recordings without event-level ground truth or listening review. Zero alerts qualify as `CONFIRMED_NON_TARGET` from original dataset annotations.
4. **Campaign Independence Qualified (`REPRODUCED WITH CORRECTION`):**
   Full statistical independence could not be established across the four campaign clusters due to severe intra-campaign temporal contiguity (e.g. Southampton session slicing) and shared hardware. The mandatory qualification phrase is formally ratified:
   > *"Four campaign-level clusters were available; full statistical independence could not be established from retained metadata."*
5. **Benchmark Closure Established (`REPRODUCED`):**
   The 23-stream registry, file hashes, WAV durations, alert counts, and campaign allocations are verified and permanently frozen. Phase 35 formally concludes the forensic audit of historical phases.

---

## 2. Safety Designation

> [!CAUTION]
> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.**
> This experimental acoustic machine-learning software is uncertified and must never be deployed for autonomous emergency dispatch, police tactical response, active-shooter alerting, automated evacuation, building lockdown, or life-critical physical security.
> Use legally obtained recordings and safe audio playback only. Live-fire testing and hazardous acoustic experiments are strictly prohibited.

---

## 3. Phase 34 Input Integrity

All primary input artifacts from Phase 34 and historical phases were verified against cryptographic digests:
- [phase34_canonical_23_stream_registry.csv](file:///e:/gunshot/gunshot/reports/phase34_canonical_23_stream_registry.csv) (`ff30bec3785a5d53...`)
- [phase34_stream_level_detector_metrics.csv](file:///e:/gunshot/gunshot/reports/phase34_stream_level_detector_metrics.csv) (`7d6b4c783af40d04...`)
- [phase34_campaign_level_metrics.csv](file:///e:/gunshot/gunshot/reports/phase34_campaign_level_metrics.csv) (`1827801dd592d66e...`)
- [phase28_cooldown_interval_ledger.csv](file:///e:/gunshot/gunshot/reports/phase28_cooldown_interval_ledger.csv) (`bb2c4838cb67c4bd...`)
- [phase24_alert_review_registry.csv](file:///e:/gunshot/gunshot/reports/phase24_alert_review_registry.csv) (`201fcc05122fd02d...`)
- [phase27_aerosonic_eval_raw.json](file:///e:/gunshot/gunshot/data/phase27/phase27_aerosonic_eval_raw.json) (`44ecb7b4125d9e55...`)

All 23 physical audio files exist, match recorded file sizes, and have matching header durations.

---

## 4. Convention A Interval Reproduction

Convention A defines an instantaneous cooldown window of $[t_{\text{alert}}, \min(T_{\text{gross}}, t_{\text{alert}} + 2.0\text{ s})]$.
Across all 287 alerts, interval unions were evaluated with boundary clipping and overlap merging:
- **Phase 14 Balanced:** 128 alerts produce **$255.84\text{ s}$** of excluded exposure ($0.0711\text{ h}$). Eligible exposure is **$12.5749\text{ h}$**, yielding **$10.1790\text{ alerts/eligible hr}$**.
- **Phase 17 Experimental:** 159 alerts produce **$316.56\text{ s}$** of excluded exposure ($0.0879\text{ h}$). Eligible exposure is **$12.5581\text{ h}$**, yielding **$12.6612\text{ alerts/eligible hr}$**.
- **Status:** `REPRODUCED`.

---

## 5. Convention B Interval Reproduction

Convention B extends cooldown to two seconds past the termination of sustained detector clusters $[t_{\text{start}}, \min(T_{\text{gross}}, t_{\text{end}} + 2.0\text{ s})]$:
- In European campaigns (17 streams), all alerts are point transients ($t_{\text{end}} = t_{\text{start}}$), so Convention B equals Convention A.
- In Adelaide Airport (6 streams), sustained acoustic energy from aircraft flyovers interacts with Phase 17's state-machine, expanding exclusions:
  - Phase 14 Adelaide Conv B exclusion: **$342.00\text{ s}$** ($0.0950\text{ h}$).
  - Phase 17 Adelaide Conv B exclusion: **$6,283.28\text{ s}$** ($1.7454\text{ h}$).
- **Corpus Totals:**
  - Phase 14 Balanced: **$453.92\text{ s}$** ($0.1261\text{ h}$).
  - Phase 17 Experimental: **$6,385.20\text{ s}$** ($1.7737\text{ h}$).
- **Status:** `REPRODUCED`.

---

## 6. Ten-Second Discrepancy Resolution

The $10.00\text{-second}$ discrepancy between the prompt summary ($6,395.20\text{ s}$) and historical records ($6,385.20\text{ s}$) is fully resolved:
- **Root Cause:** A column mix-up in narrative reporting where Phase 14's Southampton ($48.00\text{ s}$) and Bilbao ($63.92\text{ s}$) values were summed with Phase 17's Adelaide value ($6,283.28\text{ s}$).
- **True Phase 17 Values:** Southampton = $44.00\text{ s}$, Bilbao = $57.92\text{ s}$, Adelaide = $6,283.28\text{ s}$ (Sum = $6,385.20\text{ s}$).
- **Exact Difference:** $(48.00 - 44.00) + (63.92 - 57.92) = +4.00 + +6.00 = \mathbf{+10.00\text{ seconds}}$.
- **Attribution:** Represents the 5 alerts suppressed by Phase 17's animal-sound filter (2 in Southampton `P27-NAT-STR-05`, 3 in Bilbao `P27-NAT-STR-14` & `STR-16`). Each alert contributed $2.00\text{ s}$ ($5 \times 2.0 = 10.0\text{ s}$).
- **Status:** `REPRODUCED WITH CORRECTION`.

---

## 7. Final Stream-Level Exposure

All 23 streams have verified physical durations, alert counts, and unrounded eligible exposures.
Eligible exposure is strictly positive for every stream under both detector conventions ($T_{\text{elig}} > 0$).
Full stream-level records are published in [phase35_stream_exposure_reconciliation.csv](file:///e:/gunshot/gunshot/reports/phase35_stream_exposure_reconciliation.csv).
- **Status:** `REPRODUCED`.

---

## 8. Final Campaign-Level Exposure

| Campaign Identifier | Streams | Gross Duration (s) | Gross (h) | P14 Alerts | P17 Alerts | P14 Conv B Excl (s) | P17 Conv B Excl (s) | True P17 Conv B (s) | Prompt Transposed (s) | Delta (s) |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| `CAMPAIGN-SOUTHAMPTON-EXP1` | 10 | 19,800.0000 | 5.5000 | 24 | 22 | 48.00 | 44.00 | 44.00 | 48.00 | +4.00 |
| `CAMPAIGN-CHEW-MAGNA` | 1 | 2,100.0000 | 0.5833 | 0 | 0 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| `CAMPAIGN-BILBAO` | 6 | 2,025.5755 | 0.5627 | 32 | 29 | 63.92 | 57.92 | 57.92 | 63.92 | +6.00 |
| `CAMPAIGN-ADELAIDE-AEROSONIC` | 6 | 21,600.0000 | 6.0000 | 72 | 108 | 342.00 | 6,283.28 | 6,283.28 | 6,283.28 | 0.00 |
| **CUMULATIVE BENCHMARK TOTAL** | **23** | **45,525.5755** | **12.6460** | **128** | **159** | **453.92** | **6,385.20** | **6,385.20** | **6,395.20** | **+10.00** |

- **Status:** `REPRODUCED`.

---

## 9. Final Gross and Adjusted Rates

| Metric Scope | Phase 14 Balanced | Phase 17 Experimental | Absolute Difference (P14 - P17) |
|---|:---:|:---:|:---:|
| **Gross Alerts** | 128 | 159 | -31 alerts |
| **Gross Alert Rate** | **10.1218 /h** | **12.5732 /h** | -2.4514 /h |
| **Convention A Excluded Exposure** | 255.8400 s (0.0711 h) | 316.5600 s (0.0879 h) | -60.7200 s (-0.0169 h) |
| **Convention A Eligible Exposure** | 45,269.7355 s (12.5749 h) | 45,209.0155 s (12.5581 h) | +60.7200 s (+0.0169 h) |
| **Convention A Adjusted FAR** | **10.1790 /h** | **12.6612 /h** | -2.4822 /h |
| **Convention B Excluded Exposure** | 453.9200 s (0.1261 h) | 6,385.2000 s (1.7737 h) | -5,931.2800 s (-1.6476 h) |
| **Convention B Eligible Exposure** | 45,071.6555 s (12.5199 h) | 39,140.3755 s (10.8723 h) | +5,931.2800 s (+1.6476 h) |
| **Convention B Adjusted FAR** | **10.2237 /h** | **14.6243 /h** | **-4.4006 /h** |

- **Status:** `REPRODUCED`.

---

## 10. Alert Ground-Truth Classification

All 287 alerts were audited against source annotations and historical review registries:
- **`CONFIRMED_NON_TARGET`:** 0 alerts (0.0%). Original source datasets lack event-level ground truth.
- **`REVIEWED_NON_TARGET`:** 107 alerts (37.3%). Formally reviewed by double-blind acoustic experts in Phase 24.
- **`UNANNOTATED_BACKGROUND`:** 180 alerts (62.7%). Continuous ambient recordings from Adelaide Airport; non-target status inferred from macro-context.
- **`POSSIBLE_TARGET`:** 0 alerts (0.0%).
- **`UNKNOWN`:** 0 alerts (0.0%).
- **Status:** `REPRODUCED WITH CORRECTION`.

---

## 11. Campaign Independence Qualification

Due to physical sensor sharing, identical recording hardware, and temporal session slicing (e.g. Southampton morning slices), the 23 streams cannot be treated as independent experimental units.
The mandatory qualification phrase is formally ratified:
> **"Four campaign-level clusters were available; full statistical independence could not be established from retained metadata."**
- **Status:** `REPRODUCED WITH CORRECTION`.

---

## 12. Historical Corrections

1. **Phase 34 Summary Narrative Discrepancy:** The $6,395.20\text{ s}$ Convention B total is formally corrected to **$6,385.20\text{ seconds}$**.
2. **Phase 33 Narrative Transposition:** The transposed campaign durations in Phase 33 narrative text remain permanently retracted.
3. **Phase 34 False-Alert Descriptive Generalization:** Broad characterization of all alerts as "confirmed false alerts" is corrected to distinguish between reviewed non-target events and unannotated background streams.
- **Status:** `REPRODUCED WITH CORRECTION`.

---

## 13. Test and Archive Verification

- **Automated Test Suite:** [test_phase35_reproduction.py](file:///e:/gunshot/gunshot/tests/test_phase35_reproduction.py) validates all 12 mandatory audit domains.
- **Test Execution Log:** [phase35_test_execution_log.txt](file:///e:/gunshot/gunshot/reports/phase35_test_execution_log.txt) documents 100% test pass rate.
- **Release Archive:** `E:/gunshot/gunshot_detection_phase35.zip` verified with CRC check.
- **Status:** `REPRODUCED`.

---

## 14. Unresolved Limitations

1. **AeroSonicDB Sub-Window Intermediate Traces Discarded:** In Phase 27, raw sub-window model score traces and intermediate boolean flags were evaluated in memory and not persisted. Verification relies on final event records and stream-level metrics.
2. **Cluster Count Constraint:** With only $K=4$ campaign clusters, non-parametric paired tests lack statistical power to achieve $p < 0.05$.
3. **Absence of Ground-Truth Aviation Transponder Sync:** Continuous 1-hour Adelaide streams lack synchronized ADS-B transponder logs.

---

## 15. Final Governance Decision & Benchmark Closure

### Governance Rulings:
1. **Phase 14 Balanced** remains the **Default Research Baseline**.
2. **Phase 17 Experimental** remains a **Frozen Selectable Experimental Profile**.
3. The candidate state-machine reset patch remains **Quarantined Diagnostic Prototype**; no model promotion.
4. No frozen historical artifacts or model weights were modified.
5. Zero production-readiness or life-safety deployment claims.

### Benchmark Closure Assessment:
Phase 35 successfully completes the audit and establishes full internal consistency across all 23 streams, 4 campaigns, 287 alerts, and historical ledgers.
The historical benchmark audit is **FORMALLY CLOSED**.
The evidence base is now sufficiently reconciled and consistent to support a separately scoped experimental research phase, should the project choose to undertake one.
