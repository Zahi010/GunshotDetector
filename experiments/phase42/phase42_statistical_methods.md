# PHASE 42 STATISTICAL AUDIT REPORT: CONFIDENCE INTERVAL METHODOLOGY

> [!CAUTION]
> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.**
> This software is uncertified research code. It must never be deployed for autonomous emergency dispatch, police tactical response, active-shooter alerting, automated evacuation, building lockdown, or life-critical physical security.
> Use lawfully obtained recordings and safe audio playback only. Live-fire testing and hazardous acoustic experiments are strictly prohibited.

---

## 1. Executive Summary & Problem Formulation

In Phase 41, statistical reporting contained a critical methodological defect:
- Naive cluster-robust Wald intervals were applied directly to physical event rates:
  $$\hat{\lambda} \pm z_{0.975} \cdot \text{SE}_{\text{cluster}}$$
- For COND1, with $\hat{\lambda} = 7.3491\text{ alerts/hr}$ and $\text{SE}_{\text{cluster}} = 4.9274$, this produced:
  $$7.3491 - 1.96 \cdot 4.9274 = -2.3085 \implies [-2.3085, \; 17.0067]$$
- **Physical Impossibility:** False alarm rates represent physical counting processes normalized by elapsed time ($k / T \ge 0$). An acoustic detector cannot emit a negative number of false alarms. Reporting a confidence interval spanning $[-2.31, 17.01]$ is a violation of basic physical and statistical constraints.

Phase 42 Workstream C resolves this defect by establishing rigorous, bounded confidence interval formulations and formally distinguishing **single-rate confidence intervals** from **rate-difference confidence intervals**.

---

## 2. Reconciled Interval Formulations for Physical Rates

To guarantee strict physical validity (non-negativity $\lambda \ge 0$) under clustered sampling:

### Method 1: Exact Poisson Confidence Interval (Garwood Formula)
Conditioned on homogeneous Poisson arrivals over exposure $T$:
$$L = \frac{\chi^2(2 k, \, \alpha/2)}{2 T}, \quad U = \frac{\chi^2(2 k + 2, \, 1 - \alpha/2)}{2 T}$$
This interval is strictly non-negative for all $k \ge 0$.

### Method 2: Log-Transformed Cluster-Robust Wald Interval
When accounting for clustered correlation across recordists ($M = 19$), we estimate the variance on the natural logarithmic scale $\theta = \log(\lambda)$. By the Delta Method:
$$\text{Var}(\log \hat{\lambda}) \approx \frac{\text{Var}(\hat{\lambda})}{\hat{\lambda}^2} = \left(\frac{\text{SE}_{\text{cluster}}}{\hat{\lambda}}\right)^2 = \text{CV}^2$$
The $95\%$ confidence interval on $\theta$ with $df = M - 1 = 18$ degrees of freedom is:
$$[\log(\hat{\lambda}) - t_{18, 0.975} \cdot \text{CV}, \; \log(\hat{\lambda}) + t_{18, 0.975} \cdot \text{CV}]$$
Exponentiating back to the rate domain yields:
$$\left[ \hat{\lambda} \cdot \exp(-t_{18, 0.975} \cdot \text{CV}), \; \hat{\lambda} \cdot \exp(+t_{18, 0.975} \cdot \text{CV}) \right]$$
Because $\exp(x) > 0$ for all real $x$, the lower bound is **strictly positive** whenever $\hat{\lambda} > 0$.

---

## 3. Comparison of Interval Methods across Frozen Conditions

| Condition ID | Architecture / Model Profile | Gross FAR (alerts/hr) | Poisson Exact 95% CI | Defective Naive Wald CI (Phase 41) | Correct Log-Cluster Wald 95% CI | Defect Status |
|---|---|---|---|---|---|---|
| **COND1** | Phase 14 Balanced Baseline | 7.3491 | [4.9933, 10.4314] | [-3.0027, 17.7009] (z: [-2.31, 17.01]) | **[1.7968, 30.0589]** | RESOLVED (Non-negative) |
| **COND2** | Phase 17 Experimental Profile | 24.6550 | [20.1449, 29.8736] | [-0.6306, 49.9405] | **[8.8410, 68.7553]** | RESOLVED (Non-negative) |
| **COND3** | Phase 17 State Reset Candidate | 7.3491 | [4.9933, 10.4314] | [-3.0027, 17.7009] | **[1.7968, 30.0589]** | RESOLVED (Non-negative) |
| **COND4** | Phase 36 Raw State Machine | 6.1637 | [4.0264, 9.0313] | [-2.4984, 14.8259] | **[1.5119, 25.1290]** | RESOLVED (Non-negative) |
| **COND5** | Phase 36 Legacy Suppression | 6.1637 | [4.0264, 9.0313] | [-2.4984, 14.8259] | **[1.5119, 25.1290]** | RESOLVED (Non-negative) |
| **COND6** | Phase 36 Conservative Suppression | 6.1637 | [4.0264, 9.0313] | [-2.4984, 14.8259] | **[1.5119, 25.1290]** | RESOLVED (Non-negative) |

---

## 4. Rate Difference Confidence Interval Formulation

A critical distinction must be drawn between estimating a single physical rate $\lambda$ and estimating the **rate difference** $\Delta = \lambda_1 - \lambda_6$:

1. **Physical Rate $\lambda$:** Bounded strictly below by zero ($\lambda \in [0, \infty)$). Negative bounds are physically meaningless.
2. **Rate Difference $\Delta$:** Unbounded difference between two rates ($\Delta \in (-\infty, \infty)$). A negative lower bound on $\Delta$ is **statistically valid and expected** whenever the two detectors perform comparably or when the evidence does not establish superiority.

### Paired Clustered Difference Calculation:
- Point estimate: $\hat{\Delta} = \hat{\lambda}_{\text{COND1}} - \hat{\lambda}_{\text{COND6}} = 7.3491 - 6.1637 = 1.1853\text{ alerts/hr}$
- Cluster-robust standard error of difference: $\text{SE}_{\Delta, \text{cluster}} = 0.8494$
- Degrees of freedom: $df = 18$, $t_{18, 0.975} = 2.1009$
- **95% Confidence Interval for Difference:**
  $$[-0.5992, \; 2.9699]\text{ alerts/hr}$$

### Inference:
Because the $95\%$ confidence interval for $\Delta$ contains zero ($0 \in [-0.5992, 2.9699]$), the data **fail to reject the null hypothesis of equal continuous false alarm rates** between Phase 14 Balanced Baseline and Phase 36 Conservative Suppression at $\alpha = 0.05$.

---

## 5. Artifact Provenance
- Confidence interval audit CSV: [`phase42_confidence_interval_audit.csv`](file:///E:/gunshot/gunshot/experiments/phase42/phase42_confidence_interval_audit.csv)
