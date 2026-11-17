# Phase 32: Wilcoxon Statistical Reconciliation Report
## Mathematical Resolution of Asymptotic Approximation vs Exact Permutation Divergence

**Document ID:** `REPORT-PHASE32-WILCOXON-001`  
**Phase:** 32 (Statistical Reconciliation & Event Audit)  
**Date:** November 2026  
**Status:** FULL MATHEMATICAL PROOF — EXACT AND ASYMPTOTIC VALUES RESOLVED  

---

### MANDATORY SAFETY DESIGNATION
> [!CAUTION]
> **RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.**  
> This experimental acoustic machine-learning software is uncertified and must never be deployed for autonomous emergency dispatch, tactical police response, active-shooter alerting, automated evacuation, building lockdown, or life-critical physical security. Use legally obtained recordings and safe audio playback only. Live-fire testing and hazardous acoustic experiments are strictly prohibited.

---

## 1. Executive Summary & Problem Formulation

Across recent evaluation phases, an apparent discrepancy in the paired Wilcoxon signed-rank test comparing Phase 14 Balanced against Phase 17 Experimental was reported:
- **Phase 29 & Phase 30 Reported:** $W = 8.0, \; p = 0.1953125$
- **Phase 31 Reported:** $W = 8.0, \; p = 0.15626$ (and Pratt $W = 53.0, \; p = 0.36754$)

Phase 32 conducted a definitive mathematical and algorithmic audit to reconstruct the complete rank hierarchy, resolve the exact source of divergence, and provide the exact permutation distribution under ties.

### Definitive Conclusion
The underlying test statistic is **$100\%$ IDENTICAL ($W = 8.0$)** in all phases. The numerical divergence in $p$-values arises entirely from the calculation method:
1. **Phase 29/30 evaluated the theoretical combinatorial distribution of $W$ assuming untied ranks:**
   $$\text{Count}(S \le 8) = 25 / 256 \implies p = 2 \times \frac{25}{256} = \frac{50}{256} = \mathbf{0.1953125}$$
2. **Phase 31 used SciPy's default implementation (`scipy.stats.wilcoxon`), which automatically falls back to an asymptotic normal approximation when ties exist:**
   Because $|d| = 2$ occurs 4 times, SciPy computes tie-corrected variance $\text{Var} = 49.75$, yielding $z = -1.41776$ and $p = \mathbf{0.1562601}$.
3. **The exact permutation distribution accounting for the 4 tied ranks yields:**
   $$\text{Count}(S \le 8.0) = 27 / 256 \implies p = 2 \times \frac{27}{256} = \frac{54}{256} = \mathbf{0.2109375}$$

**Crucially, all test specifications without exception yield $p > 0.15$, confirming that there is no statistically significant difference in false-alert rates between Phase 14 and Phase 17 across the 23 continuous benchmark streams.**

---

## 2. Complete Paired Difference & Rank Table (N=23 Streams)

The 23 continuous audio streams comprise 17 European streams and 6 Australian AeroSonicDB streams. The table below lists all 23 streams sorted by absolute alert difference $|d| = |P14 - P17|$.

| Stream Identifier | Campaign | Gross Duration | P14 Alerts | P17 Alerts | Difference $d = P14 - P17$ | Absolute $|d|$ | Tied Group | Wilcoxon Rank | Signed Rank |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `P27-NAT-STR-01` | RPISOUND-UK | 1.00 hr | 0 | 0 | 0 | 0 | Zero (Dropped) | — | — |
| `P27-NAT-STR-02` | RPISOUND-UK | 0.50 hr | 2 | 2 | 0 | 0 | Zero (Dropped) | — | — |
| `P27-NAT-STR-03` | RPISOUND-UK | 0.50 hr | 0 | 0 | 0 | 0 | Zero (Dropped) | — | — |
| `P27-NAT-STR-04` | RPISOUND-UK | 0.50 hr | 0 | 0 | 0 | 0 | Zero (Dropped) | — | — |
| `P27-NAT-STR-06` | RPISOUND-UK | 0.50 hr | 1 | 1 | 0 | 0 | Zero (Dropped) | — | — |
| `P27-NAT-STR-07` | RPISOUND-UK | 0.50 hr | 1 | 1 | 0 | 0 | Zero (Dropped) | — | — |
| `P27-NAT-STR-08` | RPISOUND-UK | 0.50 hr | 0 | 0 | 0 | 0 | Zero (Dropped) | — | — |
| `P27-NAT-STR-09` | RPISOUND-UK | 0.14 hr | 0 | 0 | 0 | 0 | Zero (Dropped) | — | — |
| `P27-NAT-STR-10` | RPISOUND-UK | 0.05 hr | 0 | 0 | 0 | 0 | Zero (Dropped) | — | — |
| `P27-NAT-STR-11` | RPISOUND-UK | 0.05 hr | 0 | 0 | 0 | 0 | Zero (Dropped) | — | — |
| `P27-NAT-STR-12` | DCASE2020-ES | 0.50 hr | 9 | 9 | 0 | 0 | Zero (Dropped) | — | — |
| `P27-NAT-STR-13` | DCASE2020-ES | 0.50 hr | 2 | 2 | 0 | 0 | Zero (Dropped) | — | — |
| `P27-NAT-STR-15` | URBANSOUND-PL| 0.09 hr | 3 | 3 | 0 | 0 | Zero (Dropped) | — | — |
| `P27-NAT-STR-17` | URBANSOUND-PL| 0.09 hr | 5 | 5 | 0 | 0 | Zero (Dropped) | — | — |
| `P27-AERO-STR-03` | AEROSONIC-AU | 1.00 hr | 7 | 7 | 0 | 0 | Zero (Dropped) | — | — |
| `P27-NAT-STR-16` | URBANSOUND-PL| 0.11 hr | 3 | 2 | **+1** | 1 | Unique (Rank 1) | **1.0** | **+1.0** |
| `P27-NAT-STR-05` | RPISOUND-UK | 0.50 hr | 20 | 18 | **+2** | 2 | Tied 4x (Ranks 2–5) | **3.5** | **+3.5** |
| `P27-NAT-STR-14` | URBANSOUND-PL| 0.50 hr | 10 | 8 | **+2** | 2 | Tied 4x (Ranks 2–5) | **3.5** | **+3.5** |
| `P27-AERO-STR-02` | AEROSONIC-AU | 1.00 hr | 3 | 5 | **-2** | 2 | Tied 4x (Ranks 2–5) | **3.5** | **-3.5** |
| `P27-AERO-STR-04` | AEROSONIC-AU | 1.00 hr | 8 | 10 | **-2** | 2 | Tied 4x (Ranks 2–5) | **3.5** | **-3.5** |
| `P27-AERO-STR-01` | AEROSONIC-AU | 1.00 hr | 15 | 23 | **-8** | 8 | Unique (Rank 6) | **6.0** | **-6.0** |
| `P27-AERO-STR-05` | AEROSONIC-AU | 1.00 hr | 17 | 28 | **-11** | 11 | Unique (Rank 7) | **7.0** | **-7.0** |
| `P27-AERO-STR-06` | AEROSONIC-AU | 1.00 hr | 22 | 35 | **-13** | 13 | Unique (Rank 8) | **8.0** | **-8.0** |

---

## 3. Derivation of Rank Sums & Test Statistic

Of the 23 streams:
- Exactly **15 streams** exhibit zero paired differences ($d = 0$). Under the standard Wilcoxon convention (`zero_method='wilcox'`), these zero differences are eliminated from the ranking, leaving an effective sample size of $n = 8$.
- Exactly **8 streams** exhibit non-zero differences:
  - 3 positive differences: $+1, +2, +2$
  - 5 negative differences: $-2, -2, -8, -11, -13$

### 3.1. Tied Rank Assignment ($|d| = 2$)
The absolute differences are: $1, 2, 2, 2, 2, 8, 11, 13$.
- Value $1$ receives rank $1.0$.
- Value $2$ appears 4 times, occupying rank positions $2, 3, 4, 5$.  
  The mid-rank (average rank) assigned to each tied observation is:
  $$\bar{r} = \frac{2 + 3 + 4 + 5}{4} = \frac{14}{4} = 3.5$$
- Value $8$ receives rank $6.0$.
- Value $11$ receives rank $7.0$.
- Value $13$ receives rank $8.0$.

### 3.2. Sum of Signed Ranks
- **Positive Rank Sum ($W^+$):**
  $$W^+ = 1.0 (\text{from } +1) + 3.5 (\text{from } +2) + 3.5 (\text{from } +2) = 1.0 + 7.0 = \mathbf{8.0}$$
- **Negative Rank Sum ($W^-$):**
  $$W^- = 3.5 (\text{from } -2) + 3.5 (\text{from } -2) + 6.0 (\text{from } -8) + 7.0 (\text{from } -11) + 8.0 (\text{from } -13) = 7.0 + 6.0 + 7.0 + 8.0 = \mathbf{28.0}$$
- **Sum Identity Check:**
  $$W^+ + W^- = 8.0 + 28.0 = 36.0 = \frac{8 \times (8 + 1)}{2} \quad \text{(Exact match)}$$
- **Wilcoxon Test Statistic ($W$):**
  $$W = \min(W^+, W^-) = \mathbf{8.0}$$

---

## 4. Mathematical Reconciliation of Reported P-Values

### 4.1. Formula 1: Untied Exact Combinatorial Distribution ($p = 0.1953125$)
If ranks were strictly untied integer values $\{1, 2, 3, 4, 5, 6, 7, 8\}$, the null distribution of $W$ is generated by considering all $2^8 = 256$ equally likely sign assignments.
The number of subsets summing to $\le 8$ is:
- Sum 0: $\emptyset$ (1)
- Sum 1: $\{1\}$ (1)
- Sum 2: $\{2\}$ (1)
- Sum 3: $\{3\}, \{1, 2\}$ (2)
- Sum 4: $\{4\}, \{1, 3\}$ (2)
- Sum 5: $\{5\}, \{1, 4\}, \{2, 3\}$ (3)
- Sum 6: $\{6\}, \{1, 5\}, \{2, 4\}, \{1, 2, 3\}$ (4)
- Sum 7: $\{7\}, \{1, 6\}, \{2, 5\}, \{3, 4\}, \{1, 2, 4\}$ (5)
- Sum 8: $\{8\}, \{1, 7\}, \{2, 6\}, \{3, 5\}, \{1, 2, 5\}, \{1, 3, 4\}$ (6)

$$\text{Total Subsets with Sum} \le 8 = 1 + 1 + 1 + 2 + 2 + 3 + 4 + 5 + 6 = 25$$
$$\text{One-Sided Exact } p = \frac{25}{256} = 0.09765625$$
$$\text{Two-Sided Exact } p = 2 \times \frac{25}{256} = \frac{50}{256} = \mathbf{0.1953125}$$
This is the exact formula evaluated in Phase 29 and Phase 30.

### 4.2. Formula 2: SciPy Asymptotic Normal Approximation ($p = 0.1562601$)
When modern `scipy.stats.wilcoxon` detects tied ranks, it defaults to the asymptotic normal approximation with tie-corrected variance:
- Expected Value:
  $$\mu = \frac{n(n + 1)}{4} = \frac{8 \times 9}{4} = 18.0$$
- Tie-Corrected Variance:
  $$\text{Var} = \frac{n(n + 1)(2n + 1)}{24} - \frac{1}{48}\sum_{i=1}^{k}(t_i^3 - t_i)$$
  Here $n = 8$, untied variance is $\frac{8 \times 9 \times 17}{24} = 51.0$.  
  There is one tied group of size $t_1 = 4$:
  $$t_1^3 - t_1 = 4^3 - 4 = 64 - 4 = 60 \implies \frac{60}{48} = 1.25$$
  $$\text{Var} = 51.0 - 1.25 = 49.75$$
  $$\sigma = \sqrt{49.75} \approx 7.05336799$$
- Standardized $Z$-Score:
  $$Z = \frac{W - \mu}{\sigma} = \frac{8.0 - 18.0}{7.05336799} = \frac{-10.0}{7.05336799} = -1.41776251$$
- Two-Sided Asymptotic Normal $p$-Value:
  $$p = 2 \times \Phi(-1.41776251) = 2 \times 0.07813007 = \mathbf{0.156260142...}$$
This is the exact number reported by SciPy in Phase 31.

### 4.3. Formula 3: Tied Exact Permutation Distribution ($p = 0.2109375$)
When the exact permutation distribution is evaluated using the actual tied ranks $[1.0, 3.5, 3.5, 3.5, 3.5, 6.0, 7.0, 8.0]$, there are **27 subsets out of 256** with sum $\le 8.0$:
$$\text{One-Sided Exact } p = \frac{27}{256} = 0.10546875$$
$$\text{Two-Sided Exact } p = 2 \times \frac{27}{256} = \frac{54}{256} = \mathbf{0.2109375}$$

### 4.4. Formula 4: Pratt Zero-Handling Method ($p = 0.3675438$)
If the 15 tied zero differences are ranked rather than discarded (`zero_method='pratt'`):
$$W_{\text{pratt}} = 53.0, \quad p = \mathbf{0.3675438}$$

### 4.5. Formula 5: Exact Binomial Sign Test ($p = 0.7265625$)
Disregarding magnitudes entirely and testing the direction of differences (3 positive vs 5 negative, $N=8$ non-zeros):
$$p = 2 \times \sum_{k=0}^{3}\binom{8}{k}(0.5)^8 = 2 \times \frac{1 + 8 + 28 + 56}{256} = \frac{186}{256} = \mathbf{0.7265625}$$

---

## 5. Statistical Comparison Matrix & Definitive Finding

| Statistical Procedure | Test Variant | Effective $N$ | Test Statistic | Two-Sided $P$-Value | Significance ($\alpha=0.05$) | Primary Historical Phase |
| :--- | :--- | :---: | :---: | :---: | :---: | :--- |
| **Wilcoxon (Exact Untied)** | Combinatorial Null | 8 | $W = 8.0$ | **$p = 0.19531$** ($50/256$) | Not Significant | Phase 29, Phase 30 |
| **Wilcoxon (SciPy Asymptotic)**| Normal Approx (Tie-Corrected) | 8 | $W = 8.0$ | **$p = 0.15626$** ($z=-1.418$) | Not Significant | Phase 31 |
| **Wilcoxon (Exact Tied)** | Permutation with Tied Ranks | 8 | $W = 8.0$ | **$p = 0.21094$** ($54/256$) | Not Significant | Phase 32 (Gold Standard) |
| **Wilcoxon (Pratt Zero)** | Includes Tied Zeros | 23 | $W = 53.0$ | **$p = 0.36754$** | Not Significant | Phase 31 |
| **Exact Sign Test** | Two-sided Binomial (3 vs 5) | 8 | $k = 3$ | **$p = 0.72656$** ($186/256$) | Not Significant | Phase 32 Diagnostic |

> [!IMPORTANT]
> **Definitive Scientific Resolution:**  
> The divergence between $0.1953125$ and $0.15626$ is entirely resolved. It reflects the difference between the untied exact permutation formula and SciPy's tie-corrected asymptotic normal approximation. Under the exact tied permutation distribution, the true two-sided $p$-value is **$0.2109375$**. All statistical procedures without exception confirm that Phase 17 does not significantly differ from Phase 14 across the continuous audio benchmark ($p > 0.15$).

