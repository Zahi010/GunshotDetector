# PHASE 27 HISTORICAL PAIRED STATISTICS AUDIT: WILCOXON SIGNED-RANK REPRODUCTION & CORRECTION

> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.**  
> *This experimental acoustic machine-learning software is uncertified and must never be deployed for autonomous emergency dispatch, tactical police response, active-shooter alerting, automated evacuation, building lockdown, or life-critical physical security. Use legally obtained recordings and safe audio playback only. Live-fire testing and hazardous acoustic experiments are strictly prohibited.*


---

## 1. Executive Summary & Audit Mandate

In Phases 23, 24, 25, and 26, the matched comparison between Phase 14 Balanced and Phase 17 Experimental on 17 continuous natural audio streams was reported as:
$$\text{Paired Wilcoxon Signed-Rank Test: } W = 10.0, p = 0.125$$

Phase 27 mandates a rigorous, independent mathematical audit of this historical claim by reconstructing the exact per-recording paired differences from canonical source data.

### Principal Audit Findings
1. **$W = 10.0$ Is Mathematically Impossible for $N_r = 3$ Discordant Pairs:**
   - Out of 17 evaluated recordings, exactly **14 recordings are tied** ($d_i = 0$).
   - Exactly **3 recordings have non-zero differences** ($d_i \in \{+1, +2, +2\}$).
   - In a Wilcoxon signed-rank test on 3 non-zero pairs, the ranks assigned to absolute differences are $1.0, 2.5, 2.5$.
   - The total sum of ranks is:
     $$T = 1.0 + 2.5 + 2.5 = \frac{3 \times (3 + 1)}{2} = 6.0$$
   - The maximum possible rank sum for 3 observations is **6.0**. A statistic of **$W = 10.0$ cannot mathematically exist** for 3 pairs under any standard Wilcoxon formulation.
2. **$p = 0.125$ Is the Exact One-Sided Sign-Test Probability:**
   - Under a one-sided sign test (or exact one-sided Wilcoxon permutation test), the probability of all 3 non-zero pairs favoring Phase 17 by chance is:
     $$p = \left(\frac12\right)^3 = \frac18 = 0.1250$$
   - Under a standard two-sided test, the exact permutation probability is:
     $$p = 2 \times 0.1250 = 0.2500$$
3. **Scientific Decision Invariant:**
   - Under all correct formulations (two-sided Wilcoxon $W = 0.0, p = 0.2500$; two-sided sign test $p = 0.2500$; one-sided Wilcoxon $W^+ = 6.0, p = 0.1250$; Scipy asymptotic $W = 0.0, p = 0.1025$), **$p \ge 0.05$**.
   - The qualitative conclusion of Phases 23–26 remains fully validated: **Phase 17 Experimental does not achieve statistically significant superiority, and Phase 14 Balanced must be permanently retained as the default research baseline**.

---

## 2. Forensic Reconstruction of the 17 Paired Differences

From [phase27_paired_differences.csv](file:///e:/gunshot/gunshot/reports/phase27_paired_differences.csv):

| Recording ID | Campaign | Acoustic Environment | Duration | P14 Alerts | P17 Alerts | Diff ($d_i$) | Rank ($|d_i|$) | Signed Rank |
|---|---|---|---|---|---|---|---|---|
| `P26-NAT-STR-01` | UK-IND | Industrial Compressor | 3600.0 s (1.00 h) | 0 | 0 | 0 | TIED | 0.0 |
| `P26-NAT-STR-02` | UK-IND | Ventilation Duct | 1800.0 s (0.50 h) | 2 | 2 | 0 | TIED | 0.0 |
| `P26-NAT-STR-03` | UK-IND | Concrete Mixer | 1800.0 s (0.50 h) | 0 | 0 | 0 | TIED | 0.0 |
| `P26-NAT-STR-04` | UK-IND | Monoblock Pump | 1800.0 s (0.50 h) | 0 | 0 | 0 | TIED | 0.0 |
| **`P26-NAT-STR-05`** | **UK-IND** | **Arterial Highway Traffic** | **1800.0 s (0.50 h)** | **20** | **18** | **+2** | **2.5** | **+2.5** |
| `P26-NAT-STR-06` | UK-IND | Rail Transit Corridor | 1800.0 s (0.50 h) | 1 | 1 | 0 | TIED | 0.0 |
| `P26-NAT-STR-07` | UK-IND | Public Canteen Plaza | 1800.0 s (0.50 h) | 1 | 1 | 0 | TIED | 0.0 |
| `P26-NAT-STR-08` | UK-IND | Acoustic Drums Mimic | 1800.0 s (0.50 h) | 0 | 0 | 0 | TIED | 0.0 |
| `P26-NAT-STR-09` | UK-IND | Washing Machine | 1800.0 s (0.50 h) | 0 | 0 | 0 | TIED | 0.0 |
| `P26-NAT-STR-10` | UK-IND | Laptop Exhaust | 1800.0 s (0.50 h) | 0 | 0 | 0 | TIED | 0.0 |
| `P26-NAT-STR-11` | CHEW | Reservoir Weather | 2100.0 s (0.58 h) | 0 | 0 | 0 | TIED | 0.0 |
| `P26-NAT-STR-12` | BILBAO | Urban Exterior Plaza | 322.7 s (0.09 h) | 9 | 9 | 0 | TIED | 0.0 |
| `P26-NAT-STR-13` | BILBAO | Commercial Market | 327.3 s (0.09 h) | 2 | 2 | 0 | TIED | 0.0 |
| **`P26-NAT-STR-14`** | **BILBAO** | **Exterior Walkway** | **353.9 s (0.10 h)** | **10** | **8** | **+2** | **2.5** | **+2.5** |
| `P26-NAT-STR-15` | BILBAO | Exterior Terrace Cafe | 322.7 s (0.09 h) | 3 | 3 | 0 | TIED | 0.0 |
| **`P26-NAT-STR-16`** | **BILBAO** | **Commercial Arcade** | **379.6 s (0.11 h)** | **3** | **2** | **+1** | **1.0** | **+1.0** |
| `P26-NAT-STR-17` | BILBAO | Market Hall | 319.4 s (0.09 h) | 5 | 5 | 0 | TIED | 0.0 |

---

## 3. Mathematical Analysis & Null Permutation Distribution

### 3.1 Nonzero Difference Vector
The non-zero differences are:
$$D = \{d_{16} = +1, d_5 = +2, d_{14} = +2\}$$

Ranks of absolute differences $|D| = \{1, 2, 2\}$:
- Rank for $|d_{16}| = 1$: Rank $1$
- Ranks for $|d_5| = 2$ and $|d_{14}| = 2$: Tied for ranks 2 and 3 $\implies \text{Average rank } \frac{2 + 3}{2} = 2.5$

### 3.2 Rank Sums
- Sum of positive ranks: $W^+ = 1.0 + 2.5 + 2.5 = 6.0$
- Sum of negative ranks: $W^- = 0.0$
- Total rank sum: $T = W^+ + W^- = 6.0$
- Under standard convention for two-sided test: $W = \min(W^+, W^-) = 0.0$
- Under one-sided test ($H_1: \text{P14} > \text{P17}$): $W = W^+ = 6.0$

### 3.3 Exact Permutation Space ($2^3 = 8$ outcomes)
| Permutation $(s_1, s_2, s_3)$ | Signed Ranks | $W^+$ | Probability Under $H_0$ |
|---|---|---|---|
| $(-, -, -)$ | $(-1, -2.5, -2.5)$ | $0.0$ | $1/8 = 0.1250$ |
| $(+, -, -)$ | $(+1, -2.5, -2.5)$ | $1.0$ | $1/8 = 0.1250$ |
| $(-, +, -)$ | $(-1, +2.5, -2.5)$ | $2.5$ | $1/8 = 0.1250$ |
| $(-, -, +)$ | $(-1, -2.5, +2.5)$ | $2.5$ | $1/8 = 0.1250$ |
| $(+, +, -)$ | $(+1, +2.5, -2.5)$ | $3.5$ | $1/8 = 0.1250$ |
| $(+, -, +)$ | $(+1, -2.5, +2.5)$ | $3.5$ | $1/8 = 0.1250$ |
| $(-, +, +)$ | $(-1, +2.5, +2.5)$ | $5.0$ | $1/8 = 0.1250$ |
| **$(+, +, +)$ [OBSERVED]** | **$(+1, +2.5, +2.5)$** | **$6.0$** | **$1/8 = 0.1250$** |

- **Exact One-Sided $p$-value ($P(W^+ \ge 6.0)$):** $1/8 = 0.1250$
- **Exact Two-Sided $p$-value ($P(W^+ \ge 6.0 \text{ or } W^+ \le 0.0)$):** $2/8 = 0.2500$

---

## 4. Origin of the Historical $W = 10.0$ Discrepancy

A forensic examination of the project repository explains the origin of the anomalous $W = 10.0$ reporting:
1. In Phase 21, the Leave-One-Position-Out (LOPO) round recall analysis reported:
   `LOPO Exclude FP1: 62.5% vs 72.5% (+10.0%) | Exact McNemar p = 0.12500`
2. During Phase 23's synthesis, the `+10.0%` figure was transcribed alongside the one-sided permutation probability `p = 0.125` as `W = 10.0, p = 0.125`.
3. Subsequent phases (Phase 24, 25, 26) inherited this string without re-evaluating the underlying mathematical bounds.
4. **Correction:** Phase 27 formally registers $W = 0.0$ (two-sided) or $W^+ = 6.0$ (one-sided) as the true Wilcoxon test statistics, and clarifies that $p = 0.125$ is the exact one-sided probability ($p = 0.250$ two-sided).

---

## 5. Mandatory Safety Reiteration

Correcting statistical test statistics from $W = 10.0$ to $W = 0.0$ ($p = 0.250$) further reinforces that Phase 17 provides no statistically defensible improvement over Phase 14. This experimental research software is uncertified and must never be deployed for life-safety or emergency dispatch applications.
