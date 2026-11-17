# PHASE 40 STATISTICAL ANALYSIS & INFERENCE REPORT
## Continuous Ambient Rates, Paired Significance & Clustered Variance

> [!CAUTION]
> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.**
> This software is uncertified research code. It must never be deployed for autonomous emergency dispatch, police tactical response, active-shooter alerting, automated evacuation, building lockdown, or life-critical physical security.
> Use lawfully obtained recordings and safe audio playback only. Live-fire testing and hazardous acoustic experiments are strictly prohibited.

---

## 1. Executive Summary

This study conducted rigorous statistical inference across the prospective continuous exposure (28 streams, 4.2182 hours) and paired challenge partitions.

### Key Inferential Results:
1. **Continuous Exposure FAR Comparison:**
   - **Phase 14 Balanced Baseline (COND1):** 31 false alerts -> **7.3491 alerts/hr** (Exact Poisson 95% CI: $[4.9933, 10.4314]$ /hr).
   - **Phase 17 Defective Profile (COND2):** 104 false alerts -> **24.6549 alerts/hr** (Exact Poisson 95% CI: $[20.1449, 29.8736]$ /hr). Statistically significant FAR inflation ($p = 6.337626e-04$ Wilcoxon signed-rank test).
   - **Phase 36 Conservative (COND6):** 26 false alerts -> **6.1637 alerts/hr** (Exact Poisson 95% CI: $[4.0264, 9.0313]$ /hr). 16.1% reduction in continuous gross false alerts relative to Phase 14 ($W = 0.0$, $p = 0.1025$).
2. **Convention B Excluded Cooldown Inflation:**
   - In Phase 17, the unconfirmed candidate leakage locks the detector into **3,440.00 seconds** (57.33 minutes) of cooldown time, invalidating 22.7% of total field monitoring time.
   - In Phase 36, Convention B excluded time was only **107.20 seconds** (1.79 minutes, 0.71% of exposure), demonstrating clean event boundary termination.
3. **Fireworks Sensitivity Divergence:**
   - Paired McNemar $\chi^2 = 8.1000, p = 0.0044$ ($+10.0\%$ absolute trigger elevation on pyrotechnics for Phase 36, 95% CI: $[+4.12\%, +15.88\%]$). Exact paired binomial test $p = 0.00195$.

---

## 2. Six-Condition Continuous Benchmark Summary

| Condition ID | Architecture / Model | Total False Alerts | Gross Exposure (hr) | Gross FAR (/hr) | Exact Poisson 95% CI | Conv B Excluded (s) | Conv B Eligible FAR (/hr) |
|---|---|:---:|:---:|:---:|:---:|:---:|:---:|
| **COND1** | Phase 14 Balanced Baseline | 31 | 4.2182 | **7.3491** | [4.9933, 10.4314] | 120.64 s | 7.4079 |
| **COND2** | Phase 17 Experimental Profile | 104 | 4.2182 | **24.6549** | [20.1449, 29.8736] | 3,440.00 s | 31.8758 |
| **COND3** | Phase 17 State Reset Candidate | 31 | 4.2182 | **7.3491** | [4.9933, 10.4314] | 120.64 s | 7.4079 |
| **COND4** | Phase 36 Raw State Machine | 26 | 4.2182 | **6.1637** | [4.0264, 9.0313] | 107.20 s | 6.2076 |
| **COND5** | Phase 36 Legacy Suppression | 26 | 4.2182 | **6.1637** | [4.0264, 9.0313] | 107.20 s | 6.2076 |
| **COND6** | Phase 36 Conservative | 26 | 4.2182 | **6.1637** | [4.0264, 9.0313] | 107.20 s | 6.2076 |

---

## 3. Campaign-Level Cluster Breakdown

Aggregate performance across 28 independent recording campaigns:
- **Zero-Alert Streams:** Phase 36 remained completely silent on 14 out of 28 streams (50.0% clean streams).
- **Urban Concentration:** The highest alert cluster occurred in dense urban/industrial soundscapes with repetitive mechanical banging (e.g. `p38_cont_01_goussainville` and `p39_cont_05_montataire`).
- **Forest & Rural Streams:** Produced near-zero false alarms under Phase 36 (e.g. Sivry-Rance woods, Tromsdalen forest, Curonian spit: 0 alerts).

Full campaign dataset: [phase40_campaign_level_results.csv](file:///E:/gunshot/gunshot/experiments/phase40/phase40_campaign_level_results.csv).
