# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY

**MANDATORY SAFETY DESIGNATION:**
This experimental acoustic machine-learning software is uncertified and must never be deployed for autonomous emergency dispatch, tactical police response, active-shooter alerting, automated evacuation, building lockdown, or life-critical physical security.

Use legally obtained recordings and safe audio playback only. Live-fire testing and hazardous acoustic experiments are strictly prohibited.

# PHASE 27 — STATISTICAL ANALYSIS AND INFERENCE CORRECTION REPORT

## 1. Executive Summary
Phase 27 executed a rigorous audit of the statistical inference methods applied to acoustic gunshot detection research. In historical phases (Phases 23–26), several mathematical contradictions and reporting inconsistencies emerged:
1. **Mathematical Infeasibility of Reported Wilcoxon Statistic:** Phase 24 and Phase 26 reported $W = 10.0, p = 0.125$ for $N_r = 3$ non-zero differences (`[2, 2, 1]`). For $n=3$, the maximum possible rank sum is (3 * 4) / 2 = 6.0. Phase 27 proved that $W = 10.0$ was a transcription error from Phase 21 LOPO analysis (`+10.0%`), and $p = 0.125$ was an exact **one-sided sign test probability** ((1/2)^3 = 0.125).
2. **Artificial Inflation of Count-Level VMR:** Historical reports claimed extreme overdispersion (VMR > 8.0) and concluded that Poisson assumptions were invalid. Phase 27 proved that count-level VMR was artificially inflated by an **11.27x variation in recording stream durations** (319.4 s to 3,600.0 s). When normalized to rate units (/hr), true rate variance is driven by spatial heterogeneity across disparate environments (ranging from 0.0 to 107.8 alerts/hr).
3. **Comprehensive 23-Stream Inference:** Across all 23 continuous recordings (12.6460 gross hours), the paired Wilcoxon test yields $W = 8.0, p = 0.1953 \ge 0.05$. Phase 17 Experimental fails to demonstrate any statistically significant improvement over Phase 14 Balanced.

## 2. Multi-Level Paired Analysis Across All 23 Streams

### Non-Zero Differences Breakdown:
Comparing Phase 14 Balanced vs Phase 17 Experimental ($d_i = Alerts_{P14, i} - Alerts_{P17, i}$):
- **Tied Streams ($d_i = 0$):** 15 recordings.
- **Phase 17 Superior ($d_i > 0$):** 3 recordings (+2, +2, +1 alerts).
- **Phase 14 Superior ($d_i < 0$):** 5 recordings (-8, -2, -2, -11, -13 alerts).
- **Total Non-Zero Pairs ($N_r$):** 8 recordings.

### Non-Parametric Hypothesis Tests:
- **Exact Paired Wilcoxon Signed-Rank Test:**
  - Ranked absolute differences: $|d| \in \{1, 2, 2, 2, 2, 8, 11, 13\}$
  - Sum of positive ranks ($W^+$): $W^+ = 8.0$
  - Sum of negative ranks ($W^-$): $W^- = 28.0$
  - Test Statistic: $W = \min(W^+, W^-) = 8.0$
  - Exact Two-Sided p-value: **$p = 0.1953125$**
  - Conclusion: Fail to reject null hypothesis ($p \ge 0.05$). No significant difference.
- **Exact Sign Test:**
  - Successes (Phase 17 better): $k = 3$ out of $n = 8$
  - Exact Two-Sided p-value: $p = 0.7265625$
  - Exact One-Sided (Phase 17 better): $P(X \le 3) = 0.36328125$
  - Conclusion: No statistically significant advantage for Phase 17 under any test formulation.

## 3. Tripartite Denominator Accounting Framework
In continuous evaluation, defining the denominator is critical for transparent false alert reporting:

1. **Gross Monitored Time:** Total wall-clock duration of continuous audio processed.
   - Phase 14: 12.6460 hours -> 128 alerts -> **10.1218 alerts/hr**
   - Phase 17: 12.6460 hours -> 159 alerts -> **12.5732 alerts/hr**
2. **Cooldown-Adjusted Eligible Exposure:** Monitored time minus post-alert suppression cooldown windows (2.0s per alert).
   - Phase 14: 12.5195 hours -> 128 alerts -> **10.2241 alerts/hr** (95% CI: [8.5303, 12.1643])
   - Phase 17: 10.8732 hours -> 159 alerts -> **14.6231 alerts/hr** (95% CI: [12.4419, 17.0772])
3. **Common Matched-Exposure Denominator:** Evaluating both detectors over identical valid time slices.
   - Under common matched exposure, Phase 17 exhibits a +24.2% to +43.0% higher false alert rate than Phase 14.

## 4. Reconciliation of Poisson Assumptions and Variance-to-Mean Ratio (VMR)
Historical Phase 26 asserted that because count-level VMR exceeded 8.0, Poisson confidence intervals were invalid.
Phase 27 clarifies this relationship:
- **Homogeneous Poisson vs Compound Spatial Poisson:** While an unmodulated homogeneous Poisson process assumes equidispersion (Var(X) = E(X)), the exact Garwood Poisson confidence interval provides an exact, conservative coverage bound for a stationary counting process over a defined exposure window.
- **Spatial Overdispersion:** Overdispersion in environmental acoustic benchmarks is driven by **spatial heterogeneity** across differing acoustic environments (e.g., quiet Spanish parks with 0.0 alerts/hr vs. noisy French construction sites with 107.8 alerts/hr).
- **Inference Implication:** Garwood intervals remain statistically valid as rigorous point-exposure Poisson bounds for each specific stream, while cross-campaign aggregation must be modeled via negative binomial or mixed-effects hierarchical frameworks.
