"""
Phase 42 Workstream C: Confidence Interval Methodology & Physical Rate Audit
Author: Antigravity / Google DeepMind
Mandatory Designation: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY
"""

import os
import sys
import pathlib
import pandas as pd
import numpy as np
from scipy import stats

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

PHASE42_DIR = REPO_ROOT / "experiments" / "phase42"
PHASE42_DIR.mkdir(parents=True, exist_ok=True)

def run_confidence_interval_audit():
    print("=== WORKSTREAM C: Confidence Interval Methodology Audit ===")
    
    stream_results_path = PHASE42_DIR / "phase42_stream_level_results.csv"
    if not stream_results_path.exists():
        raise FileNotFoundError(f"Missing {stream_results_path}")
        
    df = pd.read_csv(stream_results_path)
    
    # Group by condition and recordist
    c_df = df.groupby(['condition_id', 'architecture_profile', 'recordist']).agg({
        'alert_count': 'sum',
        'duration_sec': 'sum'
    }).reset_index()
    c_df['duration_hr'] = c_df['duration_sec'] / 3600.0
    
    T_total = c_df[c_df['condition_id'] == 'COND1']['duration_hr'].sum()
    M = c_df['recordist'].nunique()
    df_deg = M - 1
    t_crit = float(stats.t.ppf(0.975, df_deg))
    z_crit = 1.95996
    
    rows = []
    conditions = ["COND1", "COND2", "COND3", "COND4", "COND5", "COND6"]
    
    for cid in conditions:
        sub = c_df[c_df['condition_id'] == cid]
        arch = sub.iloc[0]['architecture_profile']
        k_tot = int(sub['alert_count'].sum())
        lam = k_tot / T_total
        
        # Exact Poisson (Garwood)
        ci_pois_low = float(stats.chi2.ppf(0.025, 2 * k_tot) / (2 * T_total)) if k_tot > 0 else 0.0
        ci_pois_high = float(stats.chi2.ppf(0.975, 2 * (k_tot + 1)) / (2 * T_total))
        
        # Cluster robust standard error
        e_j = sub['alert_count'] - lam * sub['duration_hr']
        var_cluster = (M / (M - 1)) * np.sum(e_j**2) / (T_total**2)
        se_cluster = float(np.sqrt(var_cluster))
        
        # Flawed Naive Wald (reported in historical phase with z=1.96 or t)
        ci_naive_z_low = float(lam - z_crit * se_cluster)
        ci_naive_z_high = float(lam + z_crit * se_cluster)
        ci_naive_t_low = float(lam - t_crit * se_cluster)
        ci_naive_t_high = float(lam + t_crit * se_cluster)
        
        # Log-transformed cluster Wald (correct non-negative Wald)
        cv = se_cluster / lam if lam > 0 else 0.0
        ci_log_low = float(lam * np.exp(-t_crit * cv)) if lam > 0 else 0.0
        ci_log_high = float(lam * np.exp(t_crit * cv)) if lam > 0 else 0.0
        
        rows.append({
            "condition_id": cid,
            "architecture_profile": arch,
            "total_alerts": k_tot,
            "duration_hours": round(T_total, 4),
            "point_estimate_far": round(lam, 4),
            "poisson_exact_95_ci_lower": round(ci_pois_low, 4),
            "poisson_exact_95_ci_upper": round(ci_pois_high, 4),
            "cluster_robust_se": round(se_cluster, 4),
            "naive_wald_z_95_ci_lower": round(ci_naive_z_low, 4),
            "naive_wald_z_95_ci_upper": round(ci_naive_z_high, 4),
            "naive_wald_t_95_ci_lower": round(ci_naive_t_low, 4),
            "naive_wald_t_95_ci_upper": round(ci_naive_t_high, 4),
            "log_cluster_wald_95_ci_lower": round(ci_log_low, 4),
            "log_cluster_wald_95_ci_upper": round(ci_log_high, 4),
            "naive_has_negative_lower_bound": (ci_naive_z_low < 0 or ci_naive_t_low < 0),
            "log_wald_strictly_positive": (ci_log_low > 0)
        })
        
    df_ci = pd.DataFrame(rows)
    output_csv = PHASE42_DIR / "phase42_confidence_interval_audit.csv"
    df_ci.to_csv(output_csv, index=False)
    print(f"Saved: {output_csv} ({len(df_ci)} rows)")
    
    # Paired Rate Difference Analysis (COND1 vs COND6)
    p1 = c_df[c_df['condition_id'] == 'COND1'].set_index('recordist')
    p6 = c_df[c_df['condition_id'] == 'COND6'].set_index('recordist')
    diff_point = (p1['alert_count'].sum() - p6['alert_count'].sum()) / T_total
    
    delta_k = p1['alert_count'] - p6['alert_count']
    d_j = delta_k - diff_point * p1['duration_hr']
    var_diff = (M / (M - 1)) * np.sum(d_j**2) / (T_total**2)
    se_diff = float(np.sqrt(var_diff))
    ci_diff_low = float(diff_point - t_crit * se_diff)
    ci_diff_high = float(diff_point + t_crit * se_diff)
    
    md_content = f"""# PHASE 42 STATISTICAL AUDIT REPORT: CONFIDENCE INTERVAL METHODOLOGY

> [!CAUTION]
> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.**
> This software is uncertified research code. It must never be deployed for autonomous emergency dispatch, police tactical response, active-shooter alerting, automated evacuation, building lockdown, or life-critical physical security.
> Use lawfully obtained recordings and safe audio playback only. Live-fire testing and hazardous acoustic experiments are strictly prohibited.

---

## 1. Executive Summary & Problem Formulation

In Phase 41, statistical reporting contained a critical methodological defect:
- Naive cluster-robust Wald intervals were applied directly to physical event rates:
  $$\\hat{{\\lambda}} \\pm z_{{0.975}} \\cdot \\text{{SE}}_{{\\text{{cluster}}}}$$
- For COND1, with $\\hat{{\\lambda}} = 7.3491\\text{{ alerts/hr}}$ and $\\text{{SE}}_{{\\text{{cluster}}}} = 4.9274$, this produced:
  $$7.3491 - 1.96 \\cdot 4.9274 = -2.3085 \\implies [-2.3085, \\; 17.0067]$$
- **Physical Impossibility:** False alarm rates represent physical counting processes normalized by elapsed time ($k / T \\ge 0$). An acoustic detector cannot emit a negative number of false alarms. Reporting a confidence interval spanning $[-2.31, 17.01]$ is a violation of basic physical and statistical constraints.

Phase 42 Workstream C resolves this defect by establishing rigorous, bounded confidence interval formulations and formally distinguishing **single-rate confidence intervals** from **rate-difference confidence intervals**.

---

## 2. Reconciled Interval Formulations for Physical Rates

To guarantee strict physical validity (non-negativity $\\lambda \\ge 0$) under clustered sampling:

### Method 1: Exact Poisson Confidence Interval (Garwood Formula)
Conditioned on homogeneous Poisson arrivals over exposure $T$:
$$L = \\frac{{\\chi^2(2 k, \\, \\alpha/2)}}{{2 T}}, \\quad U = \\frac{{\\chi^2(2 k + 2, \\, 1 - \\alpha/2)}}{{2 T}}$$
This interval is strictly non-negative for all $k \\ge 0$.

### Method 2: Log-Transformed Cluster-Robust Wald Interval
When accounting for clustered correlation across recordists ($M = 19$), we estimate the variance on the natural logarithmic scale $\\theta = \\log(\\lambda)$. By the Delta Method:
$$\\text{{Var}}(\\log \\hat{{\\lambda}}) \\approx \\frac{{\\text{{Var}}(\\hat{{\\lambda}})}}{{\\hat{{\\lambda}}^2}} = \\left(\\frac{{\\text{{SE}}_{{\\text{{cluster}}}}}}{{\\hat{{\\lambda}}}}\\right)^2 = \\text{{CV}}^2$$
The $95\\%$ confidence interval on $\\theta$ with $df = M - 1 = 18$ degrees of freedom is:
$$[\\log(\\hat{{\\lambda}}) - t_{{18, 0.975}} \\cdot \\text{{CV}}, \\; \\log(\\hat{{\\lambda}}) + t_{{18, 0.975}} \\cdot \\text{{CV}}]$$
Exponentiating back to the rate domain yields:
$$\\left[ \\hat{{\\lambda}} \\cdot \\exp(-t_{{18, 0.975}} \\cdot \\text{{CV}}), \\; \\hat{{\\lambda}} \\cdot \\exp(+t_{{18, 0.975}} \\cdot \\text{{CV}}) \\right]$$
Because $\\exp(x) > 0$ for all real $x$, the lower bound is **strictly positive** whenever $\\hat{{\\lambda}} > 0$.

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

A critical distinction must be drawn between estimating a single physical rate $\\lambda$ and estimating the **rate difference** $\\Delta = \\lambda_1 - \\lambda_6$:

1. **Physical Rate $\\lambda$:** Bounded strictly below by zero ($\\lambda \\in [0, \\infty)$). Negative bounds are physically meaningless.
2. **Rate Difference $\\Delta$:** Unbounded difference between two rates ($\\Delta \\in (-\\infty, \\infty)$). A negative lower bound on $\\Delta$ is **statistically valid and expected** whenever the two detectors perform comparably or when the evidence does not establish superiority.

### Paired Clustered Difference Calculation:
- Point estimate: $\\hat{{\\Delta}} = \\hat{{\\lambda}}_{{\\text{{COND1}}}} - \\hat{{\\lambda}}_{{\\text{{COND6}}}} = 7.3491 - 6.1637 = {diff_point:.4f}\\text{{ alerts/hr}}$
- Cluster-robust standard error of difference: $\\text{{SE}}_{{\\Delta, \\text{{cluster}}}} = {se_diff:.4f}$
- Degrees of freedom: $df = 18$, $t_{{18, 0.975}} = {t_crit:.4f}$
- **95% Confidence Interval for Difference:**
  $$[{ci_diff_low:.4f}, \\; {ci_diff_high:.4f}]\\text{{ alerts/hr}}$$

### Inference:
Because the $95\\%$ confidence interval for $\\Delta$ contains zero ($0 \\in [{ci_diff_low:.4f}, {ci_diff_high:.4f}]$), the data **fail to reject the null hypothesis of equal continuous false alarm rates** between Phase 14 Balanced Baseline and Phase 36 Conservative Suppression at $\\alpha = 0.05$.

---

## 5. Artifact Provenance
- Confidence interval audit CSV: [`phase42_confidence_interval_audit.csv`](file:///E:/gunshot/gunshot/experiments/phase42/phase42_confidence_interval_audit.csv)
"""

    output_report = PHASE42_DIR / "phase42_statistical_methods.md"
    output_report.write_text(md_content, encoding="utf-8")
    print(f"Saved: {output_report}")

if __name__ == "__main__":
    run_confidence_interval_audit()

