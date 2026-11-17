# PHASE 34 — STATISTICAL RECONCILIATION & METHOD REGISTER
## Workstream 5: Authoritative Resolution of Paired Non-Parametric Inference

> **MANDATORY SAFETY DESIGNATION**  
> **RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY**  
> *This experimental acoustic machine-learning software is uncertified and must never be deployed for autonomous emergency dispatch, tactical police response, active-shooter alerting, automated evacuation, building lockdown, or life-critical physical security. Use legally obtained recordings and safe audio playback only. Live-fire testing and hazardous acoustic experiments are strictly prohibited.*

---

## 1. Executive Summary & Purpose

Across Phases 27 through 33, multiple differing $p$-values were reported for the paired comparison between Phase 14 Balanced and Phase 17 Experimental on the continuous benchmark ($p = 0.125 \to 0.156 \to 0.195 \to 0.211$).

Phase 34 establishes the definitive, mathematical resolution of these values. All variations are demonstrated to arise from well-defined methodological choices regarding:
1. Exact permutation vs. asymptotic normal approximation.
2. Treatment of tied ranks (mid-rank variance correction vs. discrete permutation vs. integer null distribution).
3. Treatment of zero-difference observations (Wilcoxon-Pratt exclusion vs. Pratt ranking).

---

## 2. Reconstructed Paired Observations & Rank Assignment

Evaluating Phase 14 Balanced vs. Phase 17 Experimental across all 23 canonical streams produces the paired difference series:
$$D_i = \text{Alerts}_{\text{P14}, i} - \text{Alerts}_{\text{P17}, i}$$

### 2.1 Distribution of Differences
- **Zero Differences ($D_i = 0$):** Exactly **15 streams (65.2%)**.
  - 10 Southampton streams: `P27-NAT-STR-01, 03, 04, 06, 07, 08, 09, 10` (8 zeros), plus `P27-NAT-STR-02` (0 difference: 2 vs 2).
  - 1 Chew Magna stream: `P27-NAT-STR-11` (0 vs 0).
  - 4 Bilbao streams: `P27-NAT-STR-12` (9 vs 9), `13` (2 vs 2), `15` (3 vs 3), `17` (5 vs 5).
  - 1 Adelaide stream: `P27-AERO-STR-03` (7 vs 7).
- **Non-Zero Differences ($D_i \neq 0$):** Exactly **8 streams (34.8%)**.
  - Positive ($P14 > P17$, favors P17):
    - `P27-NAT-STR-05` (Road Traffic): $20 - 18 = \mathbf{+2}$
    - `P27-NAT-STR-14` (Bilbao Walkway): $10 - 8 = \mathbf{+2}$
    - `P27-NAT-STR-16` (Bilbao Arcade): $3 - 2 = \mathbf{+1}$
  - Negative ($P14 < P17$, favors P14):
    - `P27-AERO-STR-01` (AeroSonic 1): $15 - 23 = \mathbf{-8}$
    - `P27-AERO-STR-02` (AeroSonic 2): $3 - 5 = \mathbf{-2}$
    - `P27-AERO-STR-04` (AeroSonic 4): $8 - 10 = \mathbf{-2}$
    - `P27-AERO-STR-05` (AeroSonic 5): $17 - 28 = \mathbf{-11}$
    - `P27-AERO-STR-06` (AeroSonic 6): $22 - 35 = \mathbf{-13}$

### 2.2 Rank Assignment for Non-Zero Pairs ($n = 8$)
Ordered by absolute difference $|D_i|$:
$$|D| = [1, 2, 2, 2, 2, 8, 11, 13]$$

| Index $i$ | Stream ID | $D_i$ | Sign | $|D_i|$ | Assigned Tied Mid-Rank | Untied Integer Rank |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: |
| 1 | `P27-NAT-STR-16` | +1 | $+$ | 1 | **1.0** | 1 |
| 2 | `P27-NAT-STR-05` | +2 | $+$ | 2 | **3.5** | 2 |
| 3 | `P27-NAT-STR-14` | +2 | $+$ | 2 | **3.5** | 3 |
| 4 | `P27-AERO-STR-02` | -2 | $-$ | 2 | **3.5** | 4 |
| 5 | `P27-AERO-STR-04` | -2 | $-$ | 2 | **3.5** | 5 |
| 6 | `P27-AERO-STR-01` | -8 | $-$ | 8 | **6.0** | 6 |
| 7 | `P27-AERO-STR-05` | -11 | $-$ | 11 | **7.0** | 7 |
| 8 | `P27-AERO-STR-06` | -13 | $-$ | 13 | **8.0** | 8 |

- Tie Group: 4 values of $|D| = 2$ occupy rank positions 2, 3, 4, 5:
  $$\text{Mid-Rank} = \frac{2 + 3 + 4 + 5}{4} = \mathbf{3.5}$$
- Rank Sums:
  $$W^+ = 1.0 + 3.5 + 3.5 = \mathbf{8.0}$$
  $$W^- = 3.5 + 3.5 + 6.0 + 7.0 + 8.0 = \mathbf{28.0}$$
  $$\text{Total Rank Sum} = W^+ + W^- = 8.0 + 28.0 = 36.0 = \frac{8 \times 9}{2}$$
  $$\text{Test Statistic } W = \min(W^+, W^-) = \mathbf{8.0}$$

---

## 3. Mathematical Derivations of Historical $p$-Values

### 3.1 Method 1: Exact Tied-Rank Permutation ($p = 0.2109375$)
- **Algorithm:** Enumerate all $2^8 = 256$ binary sign configurations $s \in \{-1, +1\}^8$ applied to the tied ranks $[1.0, 3.5, 3.5, 3.5, 3.5, 6.0, 7.0, 8.0]$.
- **Evaluation:** Sum positive ranks $W(s)$ for each permutation:
  - Permutations with $W(s) \le 8.0$: Exactly **27 permutations**.
  - By symmetry, permutations with $W(s) \ge 28.0$: Exactly **27 permutations**.
  - Total extreme permutations: $27 + 27 = \mathbf{54\text{ permutations}}$.
- **Exact Two-Sided $p$-Value:**
  $$p = \frac{54}{256} = \mathbf{0.2109375}$$

### 3.2 Method 2: Exact Untied Combinatorial Null ($p = 0.1953125$)
- **Algorithm:** Evaluate permutations assuming untied integer ranks $[1, 2, 3, 4, 5, 6, 7, 8]$ (the standard textbook Wilcoxon null distribution).
- **Evaluation:**
  - Permutations with $W(s) \le 8.0$: Exactly **25 permutations**.
  - Permutations with $W(s) \ge 28.0$: Exactly **25 permutations**.
  - Total extreme permutations: $25 + 25 = \mathbf{50\text{ permutations}}$.
- **Exact Two-Sided $p$-Value:**
  $$p = \frac{50}{256} = \mathbf{0.1953125}$$
> [!IMPORTANT]
> The untied combinatorial value ($0.1953125$) must never be cited as the "exact tied-rank" result. Because 4 of the 8 observations tie at $|D| = 2$, the tied-rank permutation ($0.2109375$) is the mathematically rigorous exact permutation test.

### 3.3 Method 3: SciPy Asymptotic Normal Approximation ($p = 0.1562601$)
- **Algorithm:** Standard `scipy.stats.wilcoxon(..., zero_method='wilcox', correction=False)`.
- **Expected Value:**
  $$\mu_W = \frac{n(n+1)}{4} = \frac{8 \times 9}{4} = \mathbf{18.0}$$
- **Variance with Tie Correction:**
  $$\text{Var}_0(W) = \frac{n(n+1)(2n+1)}{24} = \frac{8 \times 9 \times 17}{24} = 51.0$$
  $$\text{Tie Correction} = \frac{t_1^3 - t_1}{48} = \frac{4^3 - 4}{48} = \frac{60}{48} = 1.25$$
  $$\text{Var}(W) = 51.0 - 1.25 = \mathbf{49.75}$$
  $$\sigma_W = \sqrt{49.75} \approx 7.053368$$
- **Standardized $z$-Score:**
  $$z = \frac{W - \mu_W}{\sigma_W} = \frac{8.0 - 18.0}{7.053368} = \mathbf{-1.417762}$$
- **Two-Sided Asymptotic $p$-Value:**
  $$p = 2 \times \Phi(-1.417762) = \mathbf{0.1562601}$$

### 3.4 Method 4: Pratt Zero-Handling Method ($p = 0.3675438$)
- **Algorithm:** Ranks all $N = 23$ pairs including zeros.
  - 15 zero differences occupy rank positions 1 through 15:
    $$\text{Zero Mid-Rank} = \frac{1 + \dots + 15}{15} = 8.0$$
  - Non-zero differences receive ranks 16 through 23.
  - Zero ranks are subsequently dropped from test statistic computation.
- **Result:** $W_{\text{pratt}} = 53.0$, yielding asymptotic two-sided $p = \mathbf{0.3675438}$.
- **Diagnostic:** Pratt's method is overly conservative for high-zero datasets ($65\%$ zeros), severely depressing statistical power.

### 3.5 Method 5: Exact Binomial Sign Test ($p = 0.7265625$)
- **Algorithm:** Evaluates only directional signs ($3\text{ positive signs vs. } 5\text{ negative signs}$, $n = 8$):
  $$p = 2 \times \sum_{k=0}^3 \binom{8}{k} 0.5^8 = 2 \times \frac{1 + 8 + 28 + 56}{256} = 2 \times \frac{93}{256} = \frac{186}{256} = \mathbf{0.7265625}$$

---

## 4. Master Statistical Register Summary

| Method ID | Method Name | Sample Size | Test Statistic | Two-Sided $p$-Value | Status & Implementation Rule |
| :---: | :--- | :---: | :---: | :---: | :--- |
| `STAT-01` | **SciPy Asymptotic Normal** | $n_{\text{eff}} = 8$ | $z = -1.4178$ | **$0.1562601$** | Standard software package default. |
| `STAT-02` | **Exact Tied Permutation** | $n_{\text{eff}} = 8$ | $W = 8.0$ | **$0.2109375$** | **Gold standard exact test for tied ranks.** |
| `STAT-03` | **Exact Untied Combinatorial** | $n_{\text{eff}} = 8$ | $W = 8.0$ | **$0.1953125$** | Classical Wilcoxon table (assumes integer ranks). |
| `STAT-04` | **Pratt Zero-Handling** | $N = 23$ | $W = 53.0$ | **$0.3675438$** | Conservative zero-inclusive ranking. |
| `STAT-05` | **Exact Binomial Sign Test** | $n_{\text{eff}} = 8$ | $k = 3$ | **$0.7265625$** | Sign test discarding magnitude. |

---

## 5. Statistical Power & Equivalence Doctrine

### Critical Rule for Governance and Reporting
Every valid statistical test yields $p > 0.15$. However, this failure to reject the null hypothesis ($H_0$) is primarily caused by **low statistical power**:
- Total sample size is $N = 23$, but 15 pairs exhibit zero difference.
- The effective sample size is only $n_{\text{eff}} = 8$ non-zero pairs.
- With $n = 8$, the minimum attainable two-sided $p$-value for Wilcoxon is $2 / 256 = 0.0078$, and a difference of $+3$ vs $-5$ pairs cannot achieve statistical significance.

> [!CAUTION]
> **ABSENCE OF EVIDENCE IS NOT EVIDENCE OF ABSENCE.**  
> Non-significance ($p > 0.15$) indicates that the current benchmark lacks sufficient sample size to establish a statistically significant difference between Phase 14 and Phase 17. **It does NOT prove statistical equivalence, detector parity, or non-inferiority.**

