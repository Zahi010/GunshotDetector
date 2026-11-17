# Phase 33: Wilcoxon & Paired-Statistics Reproduction Report
## Full Permutation Re-enumeration, Tied-Rank Permutation & Statistical Methodology Audit

**Document ID:** `REPORT-PHASE33-WILCOXON-001`  
**Phase:** 33 (Independent Forensic Audit)  
**Date:** November 2026  
**Status:** FULLY REPRODUCED — 256 SIGN FLIPS INDEPENDENTLY ENUMERATED  

---

### MANDATORY SAFETY DESIGNATION
> [!CAUTION]
> **RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.**  
> This experimental acoustic machine-learning software is uncertified and must never be deployed for autonomous emergency dispatch, tactical police response, active-shooter alerting, automated evacuation, building lockdown, or life-critical physical security. Use legally obtained recordings and safe audio playback only. Live-fire testing and hazardous acoustic experiments are strictly prohibited.

---

## 1. Executive Summary & Reproduction Status

Phase 33 conducted an independent statistical reproduction of the paired comparison between Phase 14 Balanced and Phase 17 Experimental across the canonical 23 continuous audio streams.

### Reproduction Verdict: `REPRODUCED WITH METHODOLOGICAL CLARIFICATION`
- **Unit of Analysis:** Unbroken paired continuous audio streams ($N = 23$).
- **Zero Differences:** Exactly **15 streams** exhibit $d_i = 0$ ($P14 = P17$).
- **Non-Zero Differences ($n = 8$):** Exactly **8 streams** exhibit non-zero differences:
  $$d \in \{+1, +2, +2, -2, -2, -8, -11, -13\}$$
- **Signed Rank Sums:** Positive rank sum $W^+ = \mathbf{8.0}$, Negative rank sum $W^- = \mathbf{28.0}$, Test statistic $W = \mathbf{8.0}$.
- **All Reported Statistics 100% Verified:**
  - Untied Combinatorial Formula (Phase 29/30): **$p = 0.1953125$**
  - SciPy Asymptotic Normal Approximation (Phase 31): **$p = 0.1562601$**
  - Exact Tied-Rank Permutation (Phase 32): **$p = 0.2109375$**
  - Pratt Zero-Handling Method: **$W_{\text{pratt}} = 53.0, \; p = 0.3675438$**
  - Exact Binomial Sign Test: **$p = 0.7265625$**

---

## 2. Paired Observations & Tied-Rank Assignment

The paired differences were reconstructed from [phase33_paired_observations.csv](file:///E:/gunshot/gunshot/reports/phase33_paired_observations.csv).

| Stream ID | Campaign | P14 Alerts | P17 Alerts | Difference $d = P14 - P17$ | Absolute $|d|$ | Tied Group | Average Rank | Signed Rank |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `P27-NAT-STR-16` | Bilbao, Spain | 3 | 2 | **+1** | 1 | Unique (Rank 1) | **1.0** | **+1.0** |
| `P27-NAT-STR-05` | Southampton, UK | 20 | 18 | **+2** | 2 | Tied 4x (Ranks 2–5) | **3.5** | **+3.5** |
| `P27-NAT-STR-14` | Bilbao, Spain | 10 | 8 | **+2** | 2 | Tied 4x (Ranks 2–5) | **3.5** | **+3.5** |
| `P27-AERO-STR-02` | Adelaide, Australia | 3 | 5 | **-2** | 2 | Tied 4x (Ranks 2–5) | **3.5** | **-3.5** |
| `P27-AERO-STR-04` | Adelaide, Australia | 8 | 10 | **-2** | 2 | Tied 4x (Ranks 2–5) | **3.5** | **-3.5** |
| `P27-AERO-STR-01` | Adelaide, Australia | 15 | 23 | **-8** | 8 | Unique (Rank 6) | **6.0** | **-6.0** |
| `P27-AERO-STR-05` | Adelaide, Australia | 17 | 28 | **-11** | 11 | Unique (Rank 7) | **7.0** | **-7.0** |
| `P27-AERO-STR-06` | Adelaide, Australia | 22 | 35 | **-13** | 13 | Unique (Rank 8) | **8.0** | **-8.0** |
| *15 Other Streams* | Southampton / Chew Magna / Bilbao / Adelaide | — | — | **0** | 0 | Zero Differences | — | Dropped |

### Rank Sum Arithmetic
- **Tied Average Rank for $|d| = 2$:**
  $$\bar{r} = \frac{2 + 3 + 4 + 5}{4} = \frac{14}{4} = 3.5$$
- **Positive Rank Sum ($W^+$):**
  $$W^+ = 1.0 + 3.5 + 3.5 = \mathbf{8.0}$$
- **Negative Rank Sum ($W^-$):**
  $$W^- = 3.5 + 3.5 + 6.0 + 7.0 + 8.0 = \mathbf{28.0}$$
- **Rank Sum Identity Check:**
  $$W^+ + W^- = 8.0 + 28.0 = 36.0 = \frac{8 \times 9}{2} \quad \text{(Exact Integer Identity)}$$
- **Test Statistic:**
  $$W = \min(W^+, W^-) = \mathbf{8.0}$$

---

## 3. Exhaustive Sign-Flip Enumeration ($2^8 = 256$ Combinations)

Phase 33 independently generated all $2^8 = 256$ binary sign configurations across both the tied rank vector $[1.0, 3.5, 3.5, 3.5, 3.5, 6.0, 7.0, 8.0]$ and the hypothetical untied rank vector $[1, 2, 3, 4, 5, 6, 7, 8]$. The complete distribution is logged in [phase33_rank_and_permutation_audit.csv](file:///E:/gunshot/gunshot/reports/phase33_rank_and_permutation_audit.csv).

### 3.1. Two-Sided $P$-Value Convention
Under the standard two-sided Wilcoxon convention, the $p$-value represents the probability of observing a test statistic at least as extreme as the observed value $W = 8.0$ under the symmetric null hypothesis:
$$P(|S - \mu| \ge |W - \mu|) = 2 \times P(S \le 8.0) \quad \text{where } \mu = 18.0$$

### 3.2. Why the Untied Permutation is Not the Exact Tied Permutation
- **Untied Permutation (Phase 29/30):**
  Assuming integer ranks $\{1, 2, ..., 8\}$, exactly **25 subsets out of 256** satisfy $\sum r_i \le 8$:
  $$p_{\text{untied}} = 2 \times \frac{25}{256} = \frac{50}{256} = \mathbf{0.1953125}$$
- **Exact Tied Permutation (Gold Standard):**
  When evaluated using the actual tied ranks $[1.0, 3.5, 3.5, 3.5, 3.5, 6.0, 7.0, 8.0]$, exactly **27 subsets out of 256** satisfy $\sum r_i \le 8.0$:
  $$p_{\text{tied}} = 2 \times \frac{27}{256} = \frac{54}{256} = \mathbf{0.2109375}$$
- **Cause of Difference:** The ties at $3.5$ create two additional combinations with sum $\le 8.0$ (e.g. $[1.0, 3.5, 3.5] = 8.0$ has multiple permutations across the 4 tied items), increasing the subset count from 25 to 27. The untied combinatorial formula was therefore an approximation.

---

## 4. Asymptotic Normal, Pratt & Sign Test Results

Numerical records preserved in [phase33_statistical_test_results.json](file:///E:/gunshot/gunshot/reports/phase33_statistical_test_results.json):

| Statistical Procedure | Test Variant | Effective Sample Size | Test Statistic | Two-Sided $P$-Value | Significance ($\alpha=0.05$) | Primary Historical Phase |
| :--- | :--- | :---: | :---: | :---: | :---: | :--- |
| **Wilcoxon (Exact Untied)** | Combinatorial Null | 8 | $W = 8.0$ | **$p = 0.1953125$** | Not Significant | Phase 29, Phase 30 |
| **Wilcoxon (SciPy Asymptotic)**| Normal Approx (Tie-Corrected) | 8 | $W = 8.0$ | **$p = 0.1562601$** | Not Significant | Phase 31 |
| **Wilcoxon (Exact Tied)** | Permutation with Tied Ranks | 8 | $W = 8.0$ | **$p = 0.2109375$** | Not Significant | Phase 32, Phase 33 (Gold Standard) |
| **Wilcoxon (Pratt Zero)** | Includes 15 Tied Zeros | 23 | $W = 53.0$ | **$p = 0.3675438$** | Not Significant | Phase 31 |
| **Exact Sign Test** | Binomial (3 vs 5) | 8 | $k = 3$ | **$p = 0.7265625$** | Not Significant | Phase 32 Diagnostic |

### 4.1. SciPy Tie-Corrected Asymptotic Derivation
$$\text{Var} = \frac{8 \times 9 \times 17}{24} - \frac{4^3 - 4}{48} = 51.0 - 1.25 = 49.75, \quad \sigma = \sqrt{49.75} \approx 7.053368$$
$$z = \frac{8.0 - 18.0}{7.053368} = -1.4177625 \implies p = 2 \times \Phi(-1.4177625) = \mathbf{0.15626014...}$$

### 4.2. Statistical Power & Methodological Warning
> [!WARNING]
> **Avoidance of Equivalence Claims:**  
> A non-significant $p$-value ($p > 0.15$) establishes that the null hypothesis cannot be rejected; it **does not establish statistical equivalence or non-inferiority**. Because 15 of the 23 streams have identical alert counts, the effective sample size is small ($n = 8$), resulting in low statistical power ($1 - \beta \approx 0.35$). The correct scientific conclusion is that the available data provides no evidence of a difference in false-alert rates between Phase 14 and Phase 17 across the continuous benchmark.

