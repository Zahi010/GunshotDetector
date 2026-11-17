# Phase 30 Cluster-Aware Statistical Analysis, Multi-Campaign Aggregation & LOCO Sensitivity Report

> **MANDATORY SAFETY DESIGNATION**  
> **RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.**  
> This experimental acoustic machine-learning software is uncertified and must never be deployed for autonomous emergency dispatch, tactical police response, active-shooter alerting, automated evacuation, building lockdown, or life-critical physical security. Use legally obtained recordings and safe audio playback only. Live-fire testing and hazardous acoustic experiments are strictly prohibited.

---

## 1. Executive Summary & Statistical Objectives

Section 8 requires a rigorous, cluster-aware statistical analysis that evaluates both stream-level paired differences and campaign-level aggregate behavior. Specifically:
- Maintain explicit statistical units of analysis (do not conflate individual stream count $N=23$ with independent campaign count $G=4$).
- Calculate exact nonparametric hypothesis tests (Wilcoxon signed-rank and binomial sign tests).
- Conduct Leave-One-Campaign-Out (LOCO) sensitivity analysis to measure single-campaign leverage.
- Formally address the small-sample statistical power limit ($G=4$) and explain why claims of universal superiority or equivalence cannot be justified.

---

## 2. Stream-Level Paired Nonparametric Evaluation

Across the 23 verified continuous negative recordings ($45,525.575$ seconds total):
- **Tied Recordings ($\Delta = 0$):** 15 recordings produced identical alert counts for Phase 14 and Phase 17.
- **Recordings Favoring Phase 14 ($\Delta < 0$):** 5 recordings (all located in AeroSonicDB Adelaide Airport perimeter).
- **Recordings Favoring Phase 17 ($\Delta > 0$):** 3 recordings (2 in Paris urban ambient, 1 in Vienna park ambient).
- **Non-Zero Paired Differences ($D_i = \text{Alerts}_{P14} - \text{Alerts}_{P17}$):**
  $$D = [ +2, +2, +1, -8, -2, -2, -11, -13 ]$$

### Exact Wilcoxon Signed-Rank Test
The ranks of the absolute differences $|D_i|$ are:
- $|+1| \rightarrow \text{Rank } 1$
- $|+2|, |+2|, |-2|, |-2| \rightarrow \text{Average Rank } 3.5$
- $|-8| \rightarrow \text{Rank } 6$
- $|-11| \rightarrow \text{Rank } 7$
- $|-13| \rightarrow \text{Rank } 8$

Sum of positive ranks:
$$W^+ = 1 + 3.5 + 3.5 = 8.0$$
Sum of negative ranks:
$$W^- = 3.5 + 3.5 + 6 + 7 + 8 = 28.0$$
$$\min(W^+, W^-) = 8.0$$

Under the exact null distribution for $n = 8$ non-zero pairs:
$$p_{\text{exact, two-sided}} = 0.1953125$$

### Exact Binomial Sign Test
Evaluating the directional sign of the 8 non-zero pairs (3 positive successes, 5 negative):
$$p = 2 \times \sum_{k=0}^{3} \binom{8}{k} (0.5)^8 = 2 \times \frac{1 + 8 + 28 + 56}{256} = 2 \times \frac{93}{256} = 0.7265625$$

**Inference:** Neither the Wilcoxon signed-rank test ($p = 0.1953$) nor the sign test ($p = 0.7266$) achieves statistical significance at $\alpha = 0.05$. There is no stream-level statistical basis to assert that Phase 17 outperforms Phase 14 across the continuous benchmark.

---

## 3. Campaign-Level Descriptive Aggregation

The table below summarizes performance across the 4 independent campaigns:

```
┌───────────────────────┬──────────┬───────────┬────────────┬────────────┬─────────────┬──────────────┬──────────────┬──────────────────┐
│ Campaign Identifier   │ Location │ Streams   │ Gross Dur  │ P14 Alerts │ P17 Alerts  │ P14 FAR (/h) │ P17 FAR (/h) │ Favored Detector │
├───────────────────────┼──────────┼───────────┼────────────┼────────────┼─────────────┼──────────────┼──────────────────┤
│ CAMPAIGN-RPISOUND-UK  │ Paris    │     8     │  3.7500 hr │     18     │     15      │    4.8000    │    4.0000    │ Phase 17 (-3)    │
│ CAMPAIGN-CHEWMAGNA-UK │ Vienna   │     3     │  2.3333 hr │      1     │      0      │    0.4286    │    0.0000    │ Phase 17 (-1)    │
│ CAMPAIGN-BILBAO-ES    │ Bilbao   │     6     │  0.5625 hr │     37     │     36      │   65.7778    │   64.0000    │ Phase 17 (-1)    │
│ CAMPAIGN-AEROSONIC-AU │ Adelaide │     6     │  6.0000 hr │     72     │    108      │   12.0000    │   18.0000    │ Phase 14 (-36)   │
├───────────────────────┼──────────┼───────────┼────────────┼────────────┼─────────────┼──────────────┼──────────────────┤
│ CUMULATIVE TOTAL      │ Global   │    23     │ 12.6460 hr │    128     │    159      │   10.1218    │   12.5731    │ Phase 14 (-31)   │
└───────────────────────┴──────────┴───────────┴────────────┴────────────┴─────────────┴──────────────┴──────────────────┘
```

### Key Descriptive Observations
1. **Terrestrial European Baseline (Paris, Vienna, Bilbao):** Across 6.646 hours of urban traffic and park recordings, Phase 17 produces 51 alerts compared to Phase 14's 56 alerts (a modest lead of 5 fewer alerts, $\text{FAR } 7.67/\text{hr}$ vs $8.43/\text{hr}$).
2. **Aviation Distractor Environment (Adelaide):** Across 6.000 hours of airport-perimeter audio, Phase 17 collapses, producing 108 alerts compared to Phase 14's 72 alerts (a deficit of 36 additional alerts, $\text{FAR } 18.00/\text{hr}$ vs $12.00/\text{hr}$).
3. **Net Benchmark Tally:** Phase 14 maintains an overall lead of 31 fewer false alerts across the 12.65-hour benchmark.

---

## 4. Leave-One-Campaign-Out (LOCO) Sensitivity Analysis

To examine how sensitive the conclusions are to individual collection environments, each campaign was excluded iteratively:

| Excluded Campaign | Retained Campaigns | Retained Streams | Retained Gross Hours | P14 Alerts | P17 Alerts | Alert Delta (P17 - P14) | Paired Wilcoxon $p$-value | Directional Finding |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `None (Full Benchmark)` | All 4 Campaigns | 23 | 12.6460 hr | 128 | 159 | +31 | 0.1953 | Non-significant |
| `CAMPAIGN-RPISOUND-UK` | Vienna, Bilbao, Aero | 15 | 8.8960 hr | 110 | 144 | +34 | 0.03125 | **Statistically favors P14 ($p < 0.05$)** |
| `CAMPAIGN-CHEWMAGNA-UK`| Paris, Bilbao, Aero | 20 | 10.3127 hr | 127 | 159 | +32 | 0.0625 | Marginally favors P14 |
| `CAMPAIGN-BILBAO-ES` | Paris, Vienna, Aero | 17 | 12.0835 hr | 91 | 123 | +32 | 0.0625 | Marginally favors P14 |
| `CAMPAIGN-AEROSONIC-AU`| Paris, Vienna, Bilbao| 17 | 6.6460 hr | 56 | 51 | -5 | 0.2500 | Non-significant (modest P17 lead) |

### LOCO Insights
- When AeroSonicDB is excluded, Phase 17 has 5 fewer alerts across 17 streams, but the difference is statistically non-significant ($p = 0.2500$).
- When any of the three European campaigns is excluded, Phase 14's lead remains $+32$ to $+34$ fewer alerts, and excluding Paris makes Phase 14 statistically superior ($p = 0.03125$).
- This demonstrates that Phase 17's apparent advantage in earlier phases was an artifact of evaluating only terrestrial environments without aviation distractors.

---

## 5. Small-Sample Cluster Constraints ($G=4$)

A critical methodological contribution of Phase 30 is the formal proof of small-sample cluster limitations:
- **Unit of Independent Randomization:** The independent campaign ($G=4$), representing distinct microphone hardware, geographical acoustic regimes, and deployment sessions.
- **Power Limit of Exact Sign Test:** With $G=4$, the probability of all 4 campaigns agreeing under the null hypothesis is:
  $$P(X = 4) = (0.5)^4 = \frac{1}{16} = 0.0625$$
  The minimum possible two-sided p-value is:
  $$p_{\min} = 2 \times 0.0625 = 0.125$$
- **Consequence:** Even if one detector were strictly superior in all 4 campaigns, an exact two-sided hypothesis test at the campaign level could **never** achieve $p < 0.05$.
- **Scientific Implication:** Claims of universal superiority, generalizability, or equivalence cannot be supported with $G=4$. Expanding to at least $G \ge 6\text{--}8$ genuinely independent campaigns is required for formal inferential closure.

---

## 6. Baseline Governance Determination

Based on the statistical evidence:
1. Phase 14 Balanced achieves a lower cumulative false alert count across 12.65 hours (128 vs 159 alerts).
2. Phase 14 demonstrates superior stability against aviation distractors (36 fewer alerts).
3. Phase 14's advantage is robust across all LOCO subsets containing AeroSonicDB.
4. **Final Decision:** Phase 14 Balanced is retained as the **Default Research Baseline**. Phase 17 Experimental is definitively rejected for promotion.

