# PHASE 42 RELEASE NOTES
## Benchmark Denominator Reconciliation & Independent Statistical Validation

> [!CAUTION]
> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.**
> This software is uncertified research code. It must never be deployed for autonomous emergency dispatch, police tactical response, active-shooter alerting, automated evacuation, building lockdown, or life-critical physical security.
> Use lawfully obtained recordings and safe audio playback only. Live-fire testing and hazardous acoustic experiments are strictly prohibited.

---

## 1. Overview & Scope

Phase 42 delivers a comprehensive, read-only forensic audit and statistical reconciliation of the prospective gunshot detection benchmarks established in Phases 38–41.
All frozen detector models, feature extraction pipelines, neural network weights, decision thresholds, and historical freeze manifests were preserved without modification.

---

## 2. Key Audit Resolutions

1. **Continuous Exposure Denominator Reconciled (Workstream A):**
   - **Discrepancy:** Prior records cited both 17,786.33 seconds (4.9406 hours) and 15,185.60 seconds (4.2182 hours).
   - **Resolution:** 15,185.60 seconds is the sole authoritative denominator for continuous ambient False Alarm Rate (FAR), spanning 100% of the audio across all 28 continuous streams.
   - **Root Cause:** 17,786.33 seconds represents the entire 368-file evaluation corpus (28 continuous streams + 340 short challenge clips). The exact 2,600.73-second difference accounts for the 120 positive clips (519.29 s), 100 fireworks clips (1,094.87 s), and 120 other distractor clips (986.56 s).
2. **Phase 17 Fireworks Trigger Count Reconciled (Workstream B):**
   - **Discrepancy:** Prior reports cited 62 / 100 (Phase 40 pipeline) and 58 / 100 (Phase 41 table).
   - **Resolution:** Physical ground truth execution under `model_phase17.py` produces **71 / 100 triggers (71.0%)**, whereas the repaired state-reset candidate (`model_phase17_state_reset_candidate.py`) produces **57 / 100 triggers (57.0%)**.
   - **Root Cause:** Phase 40 script used an unverified hardcoded placeholder `62`; Phase 41 summary table had a typographical error `58`. The 14-clip elevation under Phase 17 is caused entirely by the candidate-accumulation defect across multi-burst reverberant intervals.
3. **Bounded Confidence Intervals Standardized (Workstream C):**
   - **Discrepancy:** Phase 41 reported negative lower bounds on physical false alarm rates (e.g. $[-2.31, 17.01]\text{ alerts/hr}$).
   - **Resolution:** All physical alert rates are strictly non-negative ($\lambda \ge 0$). Log-transformed cluster-robust Wald intervals (COND1: $[1.80, 30.06]$, COND6: $[1.51, 25.13]$) and exact Poisson intervals (COND1: $[4.99, 10.43]$, COND6: $[4.03, 9.03]$) are standardized.
   - **Difference Interval:** The 95% confidence interval for the paired rate difference ($\Delta = 1.1853\text{ alerts/hr}$) is $[-0.5992, 2.9699]$, spanning zero and confirming no statistically significant difference between Phase 14 and Phase 36.
4. **Wilcoxon Identity Solved & Exact Permutation Established (Workstream D):**
   - **Discrepancy:** Wilcoxon test yielded identical values at stream level ($N=28$) and recordist level ($K=19$): $W = 0.0, p = 0.1025$.
   - **Resolution:** Proved mathematical identity: only 3 streams had non-zero differences between COND1 and COND6 ($\{+1, +3, +1\}$), and each stream belonged to a distinct recordist. The exact permutation p-value is **$p = 0.2500$**, demonstrating that the observed 5-alert difference is entirely consistent with chance.
5. **Positive Audio Deduplication Sensitivity Verified (Workstream E):**
   - **Discrepancy:** 120 positive catalog entries vs. 119 unique waveforms due to duplicate pair `fsd50k_gun_51749` / `115295`.
   - **Resolution:** Both files triggered True Positives with exactly 1 alert across all models. Deduplication shifts recall by only -0.20% to -0.32% percentage points (COND1: 61.67% $\to$ 61.34%; COND6: 64.17% $\to$ 63.87%). Dual reporting is officially adopted.
6. **Crest-Factor Causal Claim Formally Refuted (Workstream F):**
   - **Discrepancy:** Phase 41 claimed 12.0 dB crest-factor gate caused 10 fireworks triggers in Phase 36 vs Phase 14.
   - **Resolution:** Counterfactual simulation setting `crest = 0 dB` produced identical false alarms in 10 out of 10 clips. Phase 36 triggered due to multi-window CNN persistence ($\ge 2$ windows $\ge 0.75$) and lack of fireworks semantic suppression. Causal status is classified as **`NOT_ESTABLISHED`**.

---

## 3. Governance Classifications

| Architecture Profile | File Path | Phase 42 Role | Promotion Decision |
|---|---|---|---|
| **Phase 14 Balanced Baseline** | `gunshot/model_phase14.py` | `DEFAULT_RESEARCH_BASELINE` | **Retained as Authoritative Baseline** |
| **Phase 17 Experimental Profile** | `gunshot/model_phase17.py` | `SELECTABLE_EXPERIMENTAL_PROFILE` | **Quarantined (Candidate Defect)** |
| **Phase 31 State Reset Candidate** | `experiments/phase31/model_phase17_state_reset_candidate.py` | `QUARANTINED_DIAGNOSTIC_REFERENCE` | **Quarantined Diagnostic Reference** |
| **Phase 36 Experimental Branch** | `experiments/phase36/model_phase36.py` | `EXPERIMENTAL_RESEARCH_BRANCH_V1` | **NOT PROMOTED (Research Only)** |

---

## 4. Key Artifacts Produced
- [phase42_final_audit_report.md](file:///E:/gunshot/gunshot/experiments/phase42/phase42_final_audit_report.md)
- [phase42_authoritative_benchmark.csv](file:///E:/gunshot/gunshot/experiments/phase42/phase42_authoritative_benchmark.csv)
- [phase42_discrepancy_register.csv](file:///E:/gunshot/gunshot/experiments/phase42/phase42_discrepancy_register.csv)
- [phase42_claim_evidence_matrix.csv](file:///E:/gunshot/gunshot/experiments/phase42/phase42_claim_evidence_matrix.csv)
- [phase42_continuous_exposure_reconciliation.csv](file:///E:/gunshot/gunshot/experiments/phase42/phase42_continuous_exposure_reconciliation.csv)
- [phase42_stream_level_results.csv](file:///E:/gunshot/gunshot/experiments/phase42/phase42_stream_level_results.csv)
- [phase42_continuous_reconciliation.md](file:///E:/gunshot/gunshot/experiments/phase42/phase42_continuous_reconciliation.md)
- [phase42_fireworks_decision_reconciliation.csv](file:///E:/gunshot/gunshot/experiments/phase42/phase42_fireworks_decision_reconciliation.csv)
- [phase42_fireworks_reconciliation.md](file:///E:/gunshot/gunshot/experiments/phase42/phase42_fireworks_reconciliation.md)
- [phase42_confidence_interval_audit.csv](file:///E:/gunshot/gunshot/experiments/phase42/phase42_confidence_interval_audit.csv)
- [phase42_statistical_methods.md](file:///E:/gunshot/gunshot/experiments/phase42/phase42_statistical_methods.md)
- [phase42_recordist_analysis.csv](file:///E:/gunshot/gunshot/experiments/phase42/phase42_recordist_analysis.csv)
- [phase42_cluster_inference_report.md](file:///E:/gunshot/gunshot/experiments/phase42/phase42_cluster_inference_report.md)
- [phase42_positive_deduplication_audit.csv](file:///E:/gunshot/gunshot/experiments/phase42/phase42_positive_deduplication_audit.csv)
- [phase42_positive_recall_sensitivity.md](file:///E:/gunshot/gunshot/experiments/phase42/phase42_positive_recall_sensitivity.md)
- [phase42_crest_factor_reconstruction.csv](file:///E:/gunshot/gunshot/experiments/phase42/phase42_crest_factor_reconstruction.csv)
- [phase42_mechanism_validation.md](file:///E:/gunshot/gunshot/experiments/phase42/phase42_mechanism_validation.md)
- [test_phase42_audit.py](file:///E:/gunshot/gunshot/tests/test_phase42_audit.py)
- [phase42_test_execution_log.txt](file:///E:/gunshot/gunshot/experiments/phase42/phase42_test_execution_log.txt)
"""

    output_path = PHASE42_DIR / "phase42_release_notes.md"
    output_path.write_text(md_content, encoding="utf-8")
    print(f"Saved: {output_path}")

if __name__ == "__main__":
    run_benchmark_and_discrepancy()

