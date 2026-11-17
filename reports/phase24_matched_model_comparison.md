# PHASE 24 — MATCHED MODEL COMPARISON: PHASE 14 BALANCED VS. PHASE 17 EXPERIMENTAL

> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.**  
> *This experimental acoustic machine-learning software is uncertified and must never be deployed for autonomous emergency dispatch, tactical police response, active-shooter alerting, automated lockdown or evacuation, or life-critical physical security. Use legally obtained recordings and safe audio playback only. Live-fire testing and hazardous acoustic experiments are strictly prohibited.*

---

## 1. Objective & Scope

This report provides a head-to-head empirical comparison of two frozen acoustic gunshot detectors across the 17 verified-negative continuous audio streams established in the Phase 24 benchmark:
1. **Phase 14 Balanced (`model_phase14.py`):** The frozen **default research baseline** for acoustic event classification.
2. **Phase 17 Experimental (`model_phase17.py`):** The frozen **selectable experimental profile** featuring secondary animal and distractor suppression filters.

Both models were evaluated on the exact same audio files, sample-for-sample, with an identical 2.0-second post-alert refractory cooldown mechanism and identical operational thresholds.

---

## 2. Key Comparative Findings

```
========================================================================================
METRIC                                  PHASE 14 BALANCED        PHASE 17 EXPERIMENTAL
========================================================================================
Architecture / Role                     Default Research Base    Selectable Experimental
Gross Exposure Duration                 6.6460 hours             6.6460 hours
Refractory Cooldown Excluded Time       111.92 seconds           101.92 seconds
Eligible Exposure Duration              6.6149 hours             6.6177 hours
Total Observed False Alerts             56                       51
Gross Alert Rate (FAR_gross)            8.4261 alerts/hour       7.6738 alerts/hour
Eligible Alert Rate (FAR_eligible)      8.4657 alerts/hour       7.7066 alerts/hour
Exact Garwood 95% Poisson CI            [6.3949, 10.9935]        [5.7381, 10.1328]
Mean Time Between False Alerts (MTBFA)  7.09 minutes             7.79 minutes
----------------------------------------------------------------------------------------
Absolute Alert Difference               Reference                -5 alerts (-8.93%)
Paired Wilcoxon Signed-Rank Test        Reference                W = 10.0, p = 0.125
Model Promotion Decision                RETAIN AS BASELINE       INCONCLUSIVE (REJECT)
========================================================================================
```

---

## 3. Stream-by-Stream Matched Comparison

The table below details performance across each of the 17 verified continuous streams:

| Recording ID | Environment | Duration | P14 Alerts | P17 Alerts | Delta (P14 - P17) | P14 FAR (Elig.) | P17 FAR (Elig.) | Stream Outcome |
|---|---|---|---|---|---|---|---|---|
| `P24-NAT-STR-01` | Industrial Compressor | 3600.0 s | 0 | 0 | 0 | 0.00 /h | 0.00 /h | Matched Zero |
| `P24-NAT-STR-02` | Ventilation Exhaust | 1800.0 s | 2 | 2 | 0 | 4.01 /h | 4.01 /h | Identical |
| `P24-NAT-STR-03` | Concrete Mixer | 1800.0 s | 0 | 0 | 0 | 0.00 /h | 0.00 /h | Matched Zero |
| `P24-NAT-STR-04` | Monoblock Pump | 1800.0 s | 0 | 0 | 0 | 0.00 /h | 0.00 /h | Matched Zero |
| `P24-NAT-STR-05` | Arterial Road Traffic | 1800.0 s | 20 | 18 | +2 | 40.91 /h | 36.73 /h | P17 Reduced |
| `P24-NAT-STR-06` | Rail Transit Corridor | 1800.0 s | 1 | 1 | 0 | 2.00 /h | 2.00 /h | Identical |
| `P24-NAT-STR-07` | Canteen Plaza | 1800.0 s | 1 | 1 | 0 | 2.00 /h | 2.00 /h | Identical |
| `P24-NAT-STR-08` | Acoustic Drums | 1800.0 s | 0 | 0 | 0 | 0.00 /h | 0.00 /h | Matched Zero |
| `P24-NAT-STR-09` | Washing Machine | 1800.0 s | 0 | 0 | 0 | 0.00 /h | 0.00 /h | Matched Zero |
| `P24-NAT-STR-10` | Laptop Cooling Exhaust| 1800.0 s | 0 | 0 | 0 | 0.00 /h | 0.00 /h | Matched Zero |
| `P24-NAT-STR-11` | Reservoir / Weather | 2100.0 s | 0 | 0 | 0 | 0.00 /h | 0.00 /h | Matched Zero |
| `P24-NAT-STR-12` | Bilbao Exterior Plaza | 322.7 s | 9 | 9 | 0 | 106.33 /h | 106.33 /h | Identical |
| `P24-NAT-STR-13` | Bilbao Commercial Arc. | 327.3 s | 2 | 2 | 0 | 22.27 /h | 22.27 /h | Identical |
| `P24-NAT-STR-14` | Bilbao Exterior Walkway| 353.9 s | 10 | 8 | +2 | 107.80 /h | 85.22 /h | P17 Reduced |
| `P24-NAT-STR-15` | Bilbao Exterior Terrace| 322.7 s | 3 | 3 | 0 | 34.10 /h | 34.10 /h | Identical |
| `P24-NAT-STR-16` | Bilbao Interior Arcade | 379.6 s | 3 | 2 | +1 | 28.91 /h | 19.17 /h | P17 Reduced |
| `P24-NAT-STR-17` | Bilbao Market Hall | 319.4 s | 5 | 5 | 0 | 58.17 /h | 58.17 /h | Identical |
| **Total** | **All 17 Streams** | **23925.6 s** | **56** | **51** | **+5** | **8.47 /h** | **7.71 /h** | **Non-Significant** |

---

## 4. Evaluation Under the Tripartite Denominator Framework

As formally established in [`reports/phase24_denominator_reconciliation.md`](file:///e:/gunshot/gunshot/reports/phase24_denominator_reconciliation.md), three distinct denominators govern continuous evaluation:

### 4.1 Denominator 1: Gross Monitored-Time Rate ($\text{FAR}_{\text{gross}}$)
- Exposure: Total calendar audio duration $T_{\text{gross}} = 23925.58\text{ s} = 6.6460\text{ hours}$.
- Phase 14: $\text{FAR}_{\text{gross}} = 56 / 6.6460 = 8.4261\text{ alerts/hour}$.
- Phase 17: $\text{FAR}_{\text{gross}} = 51 / 6.6460 = 7.6738\text{ alerts/hour}$.
- Delta: $-0.7523\text{ alerts/hour}$ ($-8.93\%$).

### 4.2 Denominator 2: Cooldown-Adjusted Eligible Rate ($\text{FAR}_{\text{eligible}}$)
- Exposure: Active detector listening time excluding 2.0-second post-alert refractory periods.
  - Phase 14: $T_{\text{eligible}} = 23813.66\text{ s} = 6.6149\text{ hours}$.
  - Phase 17: $T_{\text{eligible}} = 23823.66\text{ s} = 6.6177\text{ hours}$.
- Phase 14: $\text{FAR}_{\text{eligible}} = 56 / 6.6149 = 8.4657\text{ alerts/hour}$.
- Phase 17: $\text{FAR}_{\text{eligible}} = 51 / 6.6177 = 7.7066\text{ alerts/hour}$.
- Delta: $-0.7591\text{ alerts/hour}$ ($-8.97\%$).

### 4.3 Denominator 3: Common Matched-Exposure Comparison
- Evaluating the detectors across the identical 17 stream recordings reveals that:
  - 14 out of 17 streams show **zero difference** in alert counts.
  - The entire observed 5-alert reduction is concentrated in only 3 streams (`P24-NAT-STR-05`, `P24-NAT-STR-14`, and `P24-NAT-STR-16`).
  - No stream showed an alert increase under Phase 17.

---

## 5. Statistical Rigor & Model Promotion Audit

The preregistered Model Promotion Criteria ([`reports/phase22_model_promotion_criteria.md`](file:///e:/gunshot/gunshot/reports/phase22_model_promotion_criteria.md)) mandate that a candidate model must demonstrate statistically significant improvement ($p < 0.05$) without regression on core baselines before replacing the default baseline.

1. **Paired Wilcoxon Signed-Rank Test:**
   - On the recording-level alert pairs across the 17 streams, the Wilcoxon signed-rank test yields $W = 10.0, p = 0.125$.
   - Because $p = 0.125 > 0.05$, the null hypothesis (that differences in alert rates between Phase 14 and Phase 17 are due to random sampling variance) cannot be rejected.
2. **Garwood Poisson Confidence Interval Overlap:**
   - The 95% confidence interval for Phase 14 is $[6.3949, 10.9935]$ alerts/hour.
   - The 95% confidence interval for Phase 17 is $[5.7381, 10.1328]$ alerts/hour.
   - The two intervals overlap substantially (by $3.7379\text{ alerts/hour}$, or over 80% of the span).
3. **Formal Determination:**
   - **`INCONCLUSIVE`**. Phase 17 Experimental fails to demonstrate statistically significant false-alert reduction on multi-campaign continuous audio.
   - **Decision:** Retain Phase 14 Balanced as the **default research baseline**. Phase 17 Experimental remains archived strictly as a selectable experimental profile.

---

## 6. Safety Reiteration

Neither Phase 14 Balanced nor Phase 17 Experimental has achieved false-alarm rates acceptable for municipal life-safety systems. With Mean Time Between False Alerts (MTBFA) under 8 minutes in dense urban traffic and pedestrian environments, these models would overwhelm 911 dispatch and tactical units. They are experimental research artifacts only.

