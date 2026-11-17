# Phase 31: Statistical Reassessment Report
## Rebuilt Multi-Campaign Statistical Inference, Non-Parametric Hypothesis Tests & LOCO Sensitivity

**Document ID:** `REPORT-PHASE31-STATISTICS-001`  
**Phase:** 31 (Statistical Reassessment on Reconciled Registry)  
**Date:** November 2026  
**Status:** REBUILT RECONCILED STATISTICAL ANALYSIS  

---

### MANDATORY SAFETY DESIGNATION
> [!CAUTION]
> **RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.**  
> This experimental acoustic machine-learning software is uncertified and must never be deployed for autonomous emergency dispatch, tactical police response, active-shooter alerting, automated evacuation, building lockdown, or life-critical physical security. Use legally obtained recordings and safe audio playback only. Live-fire testing and hazardous acoustic experiments are strictly prohibited.

---

## 1. Executive Summary & Core Reassessment Metrics

Following the complete reconciliation of the master recording registry, all statistical inferences were rebuilt from the ground up using the verified 23-stream dataset.

### Cumulative Benchmark Summary Metrics
- **Total Validated Recordings:** Exactly 23 unbroken continuous audio streams.
- **Independent Audio Campaigns ($G$):** 4 independent campaigns (`CAMPAIGN-RPISOUND-UK`, `CAMPAIGN-CHEWMAGNA-UK`, `CAMPAIGN-BILBAO-ES`, `CAMPAIGN-AEROSONIC-AU`).
- **Geographic Locations:** 4 distinct environments in 3 countries (Southampton, UK; Chew Magna, UK; Bilbao, Spain; Adelaide, Australia).
- **Gross Monitoring Exposure:** $45,525.575\text{ seconds} = 12.6460\text{ gross hours}$.
- **Cumulative Alert Totals:**
  - **Phase 14 Balanced:** 128 alerts ($10.1218\text{ alerts/hour}$)
  - **Phase 17 Experimental:** 159 alerts ($12.5732\text{ alerts/hour}$)
  - **Net Difference ($\text{P14} - \text{P17}$):** $-31\text{ alerts}$ (Phase 17 produced 31 additional false alerts).

---

## 2. Eligible Exposure & False Alert Rates Under Both Cooldown Conventions

To prevent bias arising from post-alert refractory blindness, exposure was calculated under both standardized conventions:

| Benchmark Dimension | Phase 14 Balanced (Baseline) | Phase 17 Experimental | Empirical Difference |
| :--- | :---: | :---: | :---: |
| **Gross Exposure** | 12.6460 hr | 12.6460 hr | 0.0000 hr |
| **Gross Alert Count** | 128 alerts | 159 alerts | $+31$ alerts (+24.2%) |
| **Gross Alert Rate** | 10.1218 alerts/hr | 12.5732 alerts/hr | $+2.4514$ alerts/hr |
| **Convention A Cooldown (Instantaneous)** | 255.84 s (0.0711 hr) | 316.56 s (0.0879 hr) | $+60.72$ s (+23.7%) |
| **Convention A Eligible Exposure** | 12.5750 hr | 12.5579 hr | $-0.0171$ hr |
| **Convention A Eligible FAR** | **10.1789 alerts/hr** | **12.6614 alerts/hr** | $+2.4825$ alerts/hr |
| **Convention B Cooldown (Cluster-Extended)**| 453.92 s (0.1261 hr) | 6,385.20 s (1.7737 hr) | $+5,931.28$ s (+1306.7%) |
| **Convention B Eligible Exposure** | 12.5199 hr | 10.8723 hr | $-1.6476$ hr (-13.1%) |
| **Convention B Eligible FAR** | **10.2237 alerts/hr** | **14.6243 alerts/hr** | $+4.4006$ alerts/hr |
| **Cooldown Inflation Ratio (B vs A)** | $1.77\times$ | $20.17\times$ | $+18.40\times$ |

### Critical Finding on Cooldown Inflation
Under Convention B, Phase 17's defective state machine caused single events to span over $100\text{ seconds}$, inflating cooldown-excluded exposure to 1.77 hours (14.0% monitoring blindness) in AeroSonicDB. When this excluded time is removed, Phase 17's eligible false-alert rate rises to **14.62 alerts/hour**, widening Phase 14's performance lead.

---

## 3. Recording-Level Paired Inferences & Hypothesis Testing

Across the 23 paired continuous recordings:
- **Recordings Favoring Phase 17 ($D_i = \text{Alerts}_{P14} - \text{Alerts}_{P17} > 0$):** Exactly **3 recordings** (1 in Southampton: $+2$; 2 in Bilbao: $+2, +1$).
- **Recordings Favoring Phase 14 ($D_i < 0$):** Exactly **5 recordings** (all 5 in Adelaide: $-8, -2, -2, -11, -13$).
- **Recordings Tied ($D_i = 0$):** Exactly **15 recordings** (8 in Southampton, 1 in Chew Magna, 4 in Bilbao, 2 in Adelaide).
- **Total Non-Zero Pairs ($N_{nz}$):** $3 + 5 = 8\text{ recordings}$.

### Non-Parametric Hypothesis Tests

| Statistical Test | Method / Zero Handling | Test Statistic | Exact $p$-Value | Significance ($\alpha = 0.05$) | Inferential Interpretation |
| :--- | :--- | :---: | :---: | :---: | :--- |
| **Wilcoxon Signed-Rank** | Wilcox (zeros dropped, $N=8$) | $W = 8.0$ | **$p = 0.15626$** | **Not Significant** | Insufficient evidence of difference |
| **Wilcoxon Signed-Rank** | Pratt (zeros ranked, $N=23$) | $W = 53.0$ | **$p = 0.36754$** | **Not Significant** | Insufficient evidence of difference |
| **Exact Sign Test** | Two-sided Binomial ($k=3, n=8$) | $k = 3$ | **$p = 0.72656$** | **Not Significant** | Consistent with random fluctuation |

### Formal Inferential Conclusions
1. **No Statistically Significant Difference:**  
   Neither the Wilcoxon signed-rank test ($p = 0.156$) nor the exact sign test ($p = 0.727$) achieves statistical significance at $\alpha = 0.05$.
2. **Equivalence Cannot Be Inferred:**  
   A non-significant $p$-value fails to reject the null hypothesis; it DOES NOT prove that Phase 14 and Phase 17 are equivalent.
3. **Small-Sample Power Limitations:**  
   With only 8 non-zero pairs across 4 campaigns, statistical power to detect subtle distributional shifts across campaigns is low.
4. **Correction of Phase 30 Narrative:**  
   The claim in Phase 30's narrative that "Phase 14 is statistically superior at $p = 0.03125$ when excluding Paris" is REJECTED. That $p$-value was a clerical copy from the Pittsburgh McNemar test. When Southampton is excluded from the true dataset, Wilcoxon yields $p = 0.1250$ (non-significant).

---

## 4. Leave-One-Campaign-Out (LOCO) Sensitivity Analysis

LOCO analysis evaluates the stability of conclusions when individual campaigns are omitted:

| Excluded Campaign | Retained Campaigns | Streams | Gross Hours | P14 Alerts | P17 Alerts | Delta (P14 - P17) | Wilcoxon $p$ | Exact Sign $p$ | Stability Finding |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **None (Full Benchmark)** | All 4 Campaigns | 23 | 12.6460 | 128 | 159 | -31 | 0.15626 | 0.72656 | Non-significant |
| `CAMPAIGN-AEROSONIC-AU` | Southampton, Chew Magna, Bilbao | 17 | 6.6458 | 56 | 51 | **+5** | 0.10247 | 0.25000 | Modest Phase 17 lead; non-significant |
| `CAMPAIGN-RPISOUND-UK` | Chew Magna, Bilbao, Adelaide | 13 | 7.1458 | 104 | 137 | **-33** | 0.12500 | 0.45312 | Phase 14 leads; non-significant |
| `CAMPAIGN-CHEWMAGNA-UK` | Southampton, Bilbao, Adelaide | 22 | 12.0625 | 128 | 159 | **-31** | 0.15626 | 0.72656 | Invariant (Chew Magna has 0 alerts) |
| `CAMPAIGN-BILBAO-ES` | Southampton, Chew Magna, Adelaide | 17 | 12.0833 | 96 | 130 | **-34** | 0.07155 | 0.21875 | Marginally favors Phase 14 |

### LOCO Insights
1. **Sensitivity to AeroSonicDB:**  
   Phase 17's higher cumulative alert count is heavily driven by AeroSonicDB ($108\text{ vs }72$). When AeroSonicDB is removed, Phase 17 has slightly fewer alerts ($51\text{ vs }56$), but this difference is NOT statistically significant ($p = 0.102$).
2. **Robustness of Non-Significance:**  
   Across all four LOCO iterations, no subset achieves statistical significance ($p > 0.05$ everywhere).
3. **Multi-Campaign Generalization:**  
   With only 4 campaigns, claims of universal domain generalization are scientifically premature. Additional continuous recording campaigns in varied global regions are necessary before architectural changes can be validated.

