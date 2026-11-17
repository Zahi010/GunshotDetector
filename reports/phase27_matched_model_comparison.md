# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY

**MANDATORY SAFETY DESIGNATION:**
This experimental acoustic machine-learning software is uncertified and must never be deployed for autonomous emergency dispatch, tactical police response, active-shooter alerting, automated evacuation, building lockdown, or life-critical physical security.

Use legally obtained recordings and safe audio playback only. Live-fire testing and hazardous acoustic experiments are strictly prohibited.


# PHASE 27 — MATCHED HEAD-TO-HEAD MODEL COMPARISON REPORT

## 1. Executive Summary
Phase 27 evaluated the frozen **Phase 14 Balanced** detector (Default Research Baseline) against the frozen **Phase 17 Experimental** detector (Selectable Experimental Profile) across the expanded **12.6460 gross hour** benchmark spanning **23 continuous recordings** and **4 independent campaigns**.

The evaluation delivers definitive empirical findings:
1. **Total False Alerts:** Across 23 continuous recordings, Phase 14 triggered **128 false alerts**, whereas Phase 17 triggered **159 false alerts**. Phase 14 Balanced suppressed **31 false alerts** that Phase 17 failed to prevent.
2. **Gross False Alert Rate:** Phase 14 recorded **10.1218 alerts/hr** compared with Phase 17's **12.5732 alerts/hr** (+24.2% higher false alert rate for Phase 17).
3. **Eligible Exposure False Alert Rate:** Phase 14 recorded **10.2237 alerts/hr** (95% Garwood CI: [8.5294, 12.1561]) versus Phase 17's **14.6243 alerts/hr** (95% Garwood CI: [12.4395, 17.0824]).
4. **Statistical Significance:** Paired Wilcoxon signed-rank test across all 23 recordings yields **W = 8.0, p = 0.1953** (two-sided) and **p = 0.9258** (one-sided for Phase 17 superiority). There is zero statistically significant evidence that Phase 17 improves false-alert rejection.
5. **Architectural Baseline Retention:** Phase 14 Balanced remains the **DEFAULT RESEARCH BASELINE**. The proposal to promote Phase 17 Experimental is conclusively **REJECTED**.

## 2. Head-to-Head Benchmark Comparison Matrix

| Evaluation Dimension | Phase 14 Balanced (Default Research Baseline) | Phase 17 Experimental (Selectable Profile) | Performance Delta (P17 - P14) | Baseline Assessment |
| :--- | :--- | :--- | :--- | :--- |
| **Total Continuous Streams** | 23 | 23 | 0 | Matched |
| **Gross Exposure Monitored** | 12.6460 hrs (45,525.6 s) | 12.6460 hrs (45,525.6 s) | 0.0 hrs | Matched |
| **Total Observed False Alerts** | **128** | **159** | **+31 alerts (+24.2%)** | **Phase 14 Superior** |
| **Gross False Alert Rate** | **10.1218 /hr** | **12.5732 /hr** | **+2.4514 /hr** | **Phase 14 Superior** |
| **Cooldown Excluded Duration** | 455.52 s (0.1265 hr) | 6,381.76 s (1.7727 hr) | +5,926.24 s (+1301%) | **Phase 14 Vastly Superior** |
| **Net Eligible Exposure** | 12.5195 hrs | 10.8732 hrs | -1.6463 hrs (-13.1%) | Phase 14 Retains 99.0% Exposure |
| **Eligible False Alert Rate** | **10.2241 /hr** | **14.6231 /hr** | **+4.3990 /hr (+43.0%)** | **Phase 14 Superior** |
| **95% Poisson Garwood CI** | [8.5303, 12.1643] /hr | [12.4419, 17.0772] /hr | Disjoint Lower Bound | **Phase 14 Superior** |
| **Mean Time Between False Alerts** | 0.0978 hr (5.87 min) | 0.0684 hr (4.10 min) | -0.0294 hr (-30.1%) | **Phase 14 Superior** |
| **Streams with Fewer Alerts** | **5 streams** | **3 streams** | Net: +2 streams in favor of P14 | **Phase 14 Superior** |
| **Streams Tied (P14 == P17)** | 15 streams | 15 streams | - | Neutral |
| **Paired Wilcoxon Signed-Rank** | Ref | W = 8.0, p = 0.1953 (two-sided) | p >= 0.05 | **No Significant Advantage** |

## 3. Campaign-by-Campaign Breakdown

| Campaign Identifier | Region & Environment | Streams | Gross Duration | Phase 14 Alerts (Rate) | Phase 17 Alerts (Rate) | Observed Delta (P14 - P17) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `CAMPAIGN-RPISOUND-UK` | UK Industrial & Mechanical | 4 | 2.5000 hr | 22 (8.80 /hr) | 20 (8.00 /hr) | +2 (Phase 17 +2) |
| `CAMPAIGN-DCASE2020-ES` | Spain Urban Parks & Squares | 7 | 2.1460 hr | 2 (0.93 /hr) | 2 (0.93 /hr) | 0 (Tied) |
| `CAMPAIGN-URBANSOUND8K-FR` | France Urban Street & Traffic | 6 | 2.0000 hr | 32 (16.00 /hr) | 29 (14.50 /hr) | +3 (Phase 17 +3) |
| `CAMPAIGN-AEROSONIC-AU` | Australia Airport Perimeter & Aviation | 6 | 6.0000 hr | 72 (12.00 /hr) | 108 (18.00 /hr) | **-36 (Phase 14 +36)** |
| **Cumulative Total** | **4 Independent Campaigns** | **23** | **12.6460 hr** | **128 (10.12 /hr)** | **159 (12.57 /hr)** | **-31 (Phase 14 Superior)** |

## 4. Engineering Conclusion
Across the initial 17 European streams, Phase 17 showed minor alert reductions (+5 alerts across 6.65 hrs) that were not statistically significant ($p = 0.250$). However, upon exposure to genuine aviation acoustic stressors in AeroSonicDB, Phase 17 suffered severe cluster fragmentation, generating **36 additional false alerts** (+50% increase) compared to Phase 14. 

Phase 14 Balanced demonstrates substantially superior stability, robustness against continuous distractors, and overall lower false alert burden. Phase 14 Balanced is firmly preserved as the default research baseline.
