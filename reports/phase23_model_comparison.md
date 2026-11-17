# Phase 23: Continuous Negative Audio Model Comparison
## Comparative Evaluation of Frozen Baselines Across 17 Verified-Negative Urban Streams

**Document ID:** `REPORT-PHASE23-COMPARE-001`  
**Phase:** 23 (First 50-Hour Negative Exposure Benchmark)  
**Date:** November 2026  
**Status:** AUDITED COMPARATIVE ANALYSIS  

---

### MANDATORY SAFETY DESIGNATION
> [!CAUTION]
> **RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.**  
> This experimental acoustic machine-learning system is uncertified and must never be deployed for autonomous emergency dispatch, tactical police response, active-shooter alerting, automated lockdown or evacuation, or life-critical physical security. Use legally obtained recordings and safe audio playback only. Live-fire testing and hazardous acoustic experiments are strictly prohibited.

---

## 1. Executive Summary & Evaluation Scope

In accordance with the Phase 23 charter, the frozen detectors were evaluated across **17 verified-negative, unbroken continuous environmental streams** spanning **6.646 hours (23,925.58 seconds)** of exposure:
- **Default Research Baseline:** `model_phase14.py` (Balanced Profile, $\theta = 0.45$, refractory $\tau_{\text{cooldown}} = 2.0\text{ s}$).
- **Selectable Experimental Profile:** `model_phase17.py` (Experimental Profile with Animal Semantic Suppression).

Both models evaluated **100% identical, matched audio intervals** with zero synthetic padding, looping, or concatenation.

### Key Comparative Findings:
1. **Aggregate False Alert Counts:**
   - **Phase 14 Balanced:** 56 total alerts across 6.646 gross hours.
   - **Phase 17 Experimental:** 51 total alerts across 6.646 gross hours ($\Delta = -5\text{ alerts}$, 8.9% reduction).
2. **Eligible Operational False-Alarm Rates:**
   - **Phase 14 Balanced:** Net eligible exposure = **6.615 hours** (after subtracting 112.0s of empirical refractory dead time). Operational Rate: **8.466 alerts/eligible hour** (Exact 95% Garwood CI: $[6.398, 11.002]$ alerts/hour; MTBFA: $0.118\text{ hours} \approx 7.09\text{ minutes}$).
   - **Phase 17 Experimental:** Net eligible exposure = **6.618 hours** (after subtracting 102.0s of empirical refractory dead time). Operational Rate: **7.707 alerts/eligible hour** (Exact 95% Garwood CI: $[5.748, 10.141]$ alerts/hour; MTBFA: $0.130\text{ hours} \approx 7.79\text{ minutes}$).
3. **Paired Recording-Level Equivalence:**
   - Across 17 matched streams, Phase 17 produced fewer alerts in 4 streams, more alerts in 0 streams, and identical alert counts in 13 streams.
   - A paired Wilcoxon signed-rank test on recording-level alert counts yields **$W = 10.0, p = 0.125$ (non-significant)**.
   - Therefore, the 5-alert difference **does not achieve statistical significance** and cannot substantiate a claim of cross-campaign false-alarm superiority.

---

## 2. Comparative Exposure Accounting & Cooldown Dynamics

In compliance with the Phase 22 exposure formulation, refractory dead times ($\tau_{\text{cooldown}} = 2.0\text{ s}$) following each alert are tracked to prevent deflating the operational false-alarm rate:

| Metric Dimension | Phase 14 Balanced | Phase 17 Experimental | Comparative Delta ($\Delta_{\text{P17 - P14}}$) |
|---|---|---|---|
| **Gross Stream Duration** | 23,925.58 s (6.6460 h) | 23,925.58 s (6.6460 h) | Matched (0.00 s) |
| **Documented Excluded Intervals** | 0.00 s (0.0000 h) | 0.00 s (0.0000 h) | 0.00 s (100% verified negative) |
| **Refractory Cooldown Dead Time** | 112.00 s (0.0311 h) | 102.00 s (0.0283 h) | -10.00 s |
| **Net Eligible Negative Exposure** | **23,813.58 s (6.6149 h)** | **23,823.58 s (6.6177 h)** | **+10.00 s (+0.0028 h)** |
| **Total Observed False Alerts** | **56 alerts** | **51 alerts** | **-5 alerts (-8.9%)** |
| **Gross Rate ($\text{FAR}_{\text{gross}}$)** | 8.426 alerts/hour | 7.674 alerts/hour | -0.752 alerts/hour |
| **Eligible Rate ($\text{FAR}_{\text{eligible}}$)** | **8.466 alerts/hour** | **7.707 alerts/hour** | **-0.759 alerts/hour** |
| **Exact 95% Garwood CI** | **[6.398, 11.002] alerts/hr** | **[5.748, 10.141] alerts/hr** | Substantial overlap |
| **Empirical Mean Time Between Alerts** | 7.09 minutes | 7.79 minutes | +0.70 minutes |

---

## 3. Environmental Distribution of False Alerts

False alerts exhibit extreme spatial and acoustic overdispersion across different soundscape environments:

| Acoustic Environment Category | Streams Evaluated | Total Duration | Phase 14 Alerts | Phase 17 Alerts | Dominant Acoustic Distractor Triggering Alerts |
|---|---|---|---|---|---|
| **Industrial & Mechanical** | 4 streams (`P16-01` to `04`) | 2.500 h | 0 alerts | 0 alerts | Continuous pumps and compressors do not trigger alerts ($\text{FAR} = 0.00$). |
| **General Indoor Ambience** | 2 streams (`P16-09`, `10`) | 1.000 h | 0 alerts | 0 alerts | Washing machines and laptop fans do not trigger alerts ($\text{FAR} = 0.00$). |
| **Natural Aquatic & Weather** | 1 stream (`P16-11`) | 0.583 h | 0 alerts | 0 alerts | Reservoir water movement and wind do not trigger alerts ($\text{FAR} = 0.00$). |
| **Percussive Practice** | 1 stream (`P16-08`) | 0.500 h | 0 alerts | 0 alerts | Drumming practice suppressed by spectral flux gating ($\text{FAR} = 0.00$). |
| **Public Spaces & Canteens** | 1 stream (`P16-07`) | 0.500 h | 1 alert | 1 alert | Heavy tray impact against metal counter. |
| **Arterial Traffic & Transit** | 2 streams (`P16-05`, `06`) | 1.000 h | 21 alerts | 19 alerts | Truck pneumatic air brake releases, tire thumps on metal expansion joints. |
| **Urban Exterior & Pedestrian** | 6 streams (`P17-12` to `17`) | 0.563 h | 34 alerts | 31 alerts | Metal cafe chair dragging on stone pavers, ceramic dish clatter, echoes in stone arcades. |
| **TOTAL** | **17 Streams** | **6.646 h** | **56 alerts** | **51 alerts** | Bimodal distribution: 0 alerts in 4.58h; 55+ alerts in 2.06h. |

---

## 4. Forensic Alert Review

Every alert generated by both detectors across the 17 verified-negative streams was subjected to forensic acoustic review:
- **Ground Truth Review Verdict:** 100% of alerts are classified as `CONFIRMED_NON_TARGET_DISTRACTOR`.
- **Zero Gunshot Suspicion:** Independent audio provenance confirms zero firearm discharges during these recording sessions.
- **Triggering Morphologies:**
  1. *Sharp Metal-on-Stone Transients:* Dragging metal furniture across cobblestone pavement in Bilbao Old Town (`P17-STREAM-12`, `P17-STREAM-14`) generates fast-rise-time acoustic spikes with crest factors $> 15\text{ dB}$, triggering false alerts.
  2. *Heavy Vehicle Braking & Road Joints:* Fast pressure release from pneumatic bus air brakes in arterial road monitoring (`P16-STREAM-05`) mimics impulsive blast profiles.

---

## 5. Statistical Interpretation & Promotion Status

In accordance with the preregistered **Model Promotion Criteria** ([`reports/phase22_model_promotion_criteria.md`](file:///e:/gunshot/gunshot/reports/phase22_model_promotion_criteria.md)):
1. **Recording-Level Non-Significance:** The 5-alert reduction from 56 to 51 yields a Wilcoxon signed-rank $p = 0.125$. Because $p \ge 0.05$, the candidate fails Criterion 2.
2. **Confidence Interval Overlap:** The 95% Garwood confidence interval for Phase 17 ($[5.748, 10.141]$) completely overlaps that of Phase 14 ($[6.398, 11.002]$).
3. **Formal Determination:** The comparative outcome is officially designated **`INCONCLUSIVE`**.
4. **Baseline Invariance:** `model_phase14.py` Balanced is **RETAINED** as the Default Research Baseline. Phase 17 Experimental remains a selectable experimental research profile.

---

*Authored by Principal Acoustic ML Research Engineer & Audio DSP Specialist.*  
*Antigravity Gunshot Detection Research Consortium — Phase 23.*

