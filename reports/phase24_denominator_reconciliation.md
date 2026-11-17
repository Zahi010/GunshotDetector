# Phase 24: Denominator Reconciliation & False-Alert Rate Audit
## Methodological Audit of Gross Monitored Time vs. Cooldown-Adjusted Eligible Exposure

**Document ID:** `REPORT-PHASE24-DENOM-001`  
**Phase:** 24 (Municipal Audio Acquisition & False-Alert Rate Audit)  
**Date:** November 2026  
**Status:** AUDITED RECONCILIATION REPORT  

---

### MANDATORY SAFETY DESIGNATION
> [!CAUTION]
> **RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.**  
> This experimental acoustic machine-learning system is uncertified and must never be deployed for autonomous emergency dispatch, tactical police response, active-shooter alerting, automated lockdown or evacuation, or life-critical physical security. Use legally obtained recordings and safe audio playback only. Live-fire testing and hazardous acoustic experiments are strictly prohibited.

---

## 1. Executive Summary & Purpose of Audit

In Phase 23, the evaluation of continuous negative urban audio reported model-specific eligible exposures:
- Phase 14 Balanced: 6.6149 hours (23,813.58 seconds).
- Phase 17 Experimental: 6.6177 hours (23,823.58 seconds).

While mathematically rigorous for modeling independent Poisson opportunities, using model-specific denominators creates subtle operational ambiguities:
1. **The Dispatch Burden Estimand:** In real-world monitoring, an emergency management center or security operator measures false alarms per **wall-clock calendar hour** (Gross Monitored Time). A 2.0-second internal refractory dead time does not shorten the physical passage of time for the operator.
2. **Model Comparison Parity:** If Model A generates 56 alerts (triggering 112s of dead time) and Model B generates 51 alerts (triggering 102s of dead time), dividing Model A's count by a smaller denominator slightly inflates Model A's rate relative to Model B.

Phase 24 establishes a definitive tripartite denominator framework and performs an exact forensic recalculation of the Phase 23 source data.

---

## 2. Tripartite Denominator Framework

Phase 24 formally defines and separates three distinct statistical quantities:

### Denominator A: Gross Monitored-Time Alert Rate ($\text{FAR}_{\text{gross}}$)
$$\text{FAR}_{\text{gross}} = \frac{K}{T_{\text{gross\_hr}}} \quad \left[\frac{\text{Observed False Alerts}}{\text{Gross Calendar Hours of Audio}}\right]$$
- **Operational Estimand:** Measures true operator alert burden per unit of continuous audio stream time.
- **Refractory Rule:** Refractory cooldown dead time remains part of the exposure denominator.
- **Status:** **Primary descriptive operational metric.**

### Denominator B: Cooldown-Adjusted Eligible-Time Rate ($\text{FAR}_{\text{eligible}}$)
$$\text{FAR}_{\text{eligible}} = \frac{K}{T_{\text{eligible\_hr}}} = \frac{K}{(T_{\text{gross}} - \sum \tau_{\text{cooldown}} - T_{\text{excluded}}) / 3600}$$
- **Statistical Estimand:** Measures the rate of alert generation per unit of time during which the detector's state machine was actively capable of issuing a new alert.
- **Refractory Rule:** Subtracts merged non-overlapping refractory intervals.
- **Status:** **Point-process rate parameter for Poisson and hazard models.**

### Denominator C: Common Matched-Exposure Comparison
$$\Delta_{\text{rate, common}} = \frac{K_{\text{candidate}} - K_{\text{baseline}}}{T_{\text{common\_gross\_hr}}}$$
- **Comparative Estimand:** Direct head-to-head comparison where both candidate architectures evaluate the exact same audio intervals over an identical common denominator.
- **Refractory Rule:** Prevents denominator skew from biasing paired model comparisons.
- **Status:** **Preregistered metric for model promotion and hypothesis testing.**

---

## 3. Forensic Recalculation of Phase 23 Benchmark Data

The raw timestamp logs and stream manifests from Phase 23 (`phase23_recording_provenance.csv`, `phase23_exposure_accounting.csv`, and `phase23_negative_audio_results.csv`) were independently parsed and recalculated:

```
[AUDIT VERIFICATION STEPS]
1. Summing duration_seconds across all 17 primary VERIFIED_NEGATIVE streams:
   Gross Duration = 3600.0 (P16-01) + 1800.0 (P16-02) + 1800.0 (P16-03) + 1800.0 (P16-04) + 
                    1800.0 (P16-05) + 1800.0 (P16-06) + 1800.0 (P16-07) + 1800.0 (P16-08) + 
                    1800.0 (P16-09) + 1800.0 (P16-10) + 2100.0 (P16-11) + 322.71 (P17-12) + 
                    327.27 (P17-13) + 353.87 (P17-14) + 322.74 (P17-15) + 379.55 (P17-16) + 
                    319.44 (P17-17)
   = 23,925.580 seconds = 6.645994 hours. (MATCHES EXPECTED: 23,925.58 s).

2. Auditing Phase 14 Balanced Alert Counts and Cooldown:
   Total alerts observed = 56.
   Cooldown interval per alert = 2.0 seconds.
   Overlapping cooldown verification: None of the 56 alerts occurred within 2.0s of each other (the detector's state machine enforces this during inference).
   Total cooldown dead time = 56 * 2.0 = 112.000 seconds. (MATCHES EXPECTED: 112 s).
   Net eligible exposure = 23,925.580 - 112.000 = 23,813.580 seconds = 6.614883 hours. (MATCHES EXPECTED: 23,813.58 s).

3. Auditing Phase 17 Experimental Alert Counts and Cooldown:
   Total alerts observed = 51.
   Cooldown interval per alert = 2.0 seconds.
   Total cooldown dead time = 51 * 2.0 = 102.000 seconds. (MATCHES EXPECTED: 102 s).
   Net eligible exposure = 23,925.580 - 102.000 = 23,823.580 seconds = 6.617661 hours. (MATCHES EXPECTED: 23,823.58 s).
```

### 3.1 Side-by-Side Audit Reconciliation Table

| Metric | Phase 14 Balanced | Phase 17 Experimental | Absolute Difference ($\Delta$) | Audit Reconciliation Status |
|---|---|---|---|---|
| **Gross Stream Duration ($T_{\text{gross}}$)** | 23,925.58 s (6.6460 h) | 23,925.58 s (6.6460 h) | 0.00 s (0.0000 h) | **VERIFIED EXACT MATCH** |
| **Observed Alert Count ($K$)** | 56 alerts | 51 alerts | -5 alerts (-8.9%) | **VERIFIED EXACT MATCH** |
| **Refractory Dead Time ($\sum \tau_{\text{cd}}$)** | 112.00 s (0.0311 h) | 102.00 s (0.0283 h) | -10.00 s | **VERIFIED EXACT MATCH** |
| **Net Eligible Exposure ($T_{\text{eligible}}$)**| 23,813.58 s (6.6149 h) | 23,823.58 s (6.6177 h) | +10.00 s (+0.0028 h) | **VERIFIED EXACT MATCH** |
| **Gross Rate ($\text{FAR}_{\text{gross}}$)** | **8.4261 alerts/hour** | **7.6738 alerts/hour** | **-0.7523 alerts/hour** | **INDEPENDENTLY REPRODUCED** |
| **Eligible Rate ($\text{FAR}_{\text{eligible}}$)**| **8.4658 alerts/hour** | **7.7066 alerts/hour** | **-0.7592 alerts/hour** | **INDEPENDENTLY REPRODUCED** |
| **Garwood 95% CI (Gross)** | [6.3649, 10.9421] / hr | [5.7136, 10.0894] / hr | Substantial overlap | **VERIFIED NON-SIGNIFICANT** |
| **Garwood 95% CI (Eligible)** | [6.3949, 10.9935] / hr | [5.7381, 10.1328] / hr | Substantial overlap | **VERIFIED NON-SIGNIFICANT** |

---

## 4. Methodological Findings & Recommendations

1. **Impact of Cooldown Adjustment on Rates:**  
   Because the 56 alerts in Phase 14 occupied only 112 seconds out of 23,925.58 seconds (0.47% of total stream duration), the numerical difference between the gross rate (8.426 alerts/hr) and the eligible rate (8.466 alerts/hr) is small: **0.040 alerts/hour (0.47%)**.
2. **When Cooldown Adjustment is Essential:**  
   If an uncalibrated detector produced 600 alerts/hour, cooldown dead time would total $600 \times 2.0 = 1,200\text{ seconds}$ (33.3% of the hour). In that regime, failure to adjust for cooldown would severely mask false alarms.
3. **Phase 24 Preregistered Standard:**  
   All Phase 24 deliverables and subsequent research phases must explicitly report **both** Gross Monitored-Time Rate and Cooldown-Adjusted Eligible Rate.

---

*Authored by Principal Acoustic ML Research Engineer & Audio DSP Specialist.*  
*Antigravity Gunshot Detection Research Consortium — Phase 24.*

