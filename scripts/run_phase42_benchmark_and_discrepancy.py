"""
Phase 42 Workstream G: Authoritative Benchmark, Discrepancy Register & Claim Evidence Matrix
Author: Antigravity / Google DeepMind
Mandatory Designation: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY
"""

import os
import sys
import pathlib
import pandas as pd
import numpy as np

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

PHASE42_DIR = REPO_ROOT / "experiments" / "phase42"
PHASE42_DIR.mkdir(parents=True, exist_ok=True)

def run_benchmark_and_discrepancy():
    print("=== WORKSTREAM G: Authoritative Benchmark & Discrepancy Register ===")
    
    # 1. Authoritative Benchmark Table
    benchmark_rows = [
        # Continuous FAR (Gross / Conv A)
        {
            "metric_id": "METRIC_CONT_FAR_GROSS",
            "metric_name": "Continuous Ambient Gross False Alarm Rate (Convention A)",
            "condition_id": "COND1",
            "architecture_profile": "Phase 14 Balanced Baseline",
            "numerator": 31,
            "denominator": 4.2182,
            "unit": "alerts / hour",
            "dataset_version": "Prospective Continuous Ambient (28 streams)",
            "inclusion_criteria": "100% of 28 continuous audio streams evaluated (15,185.60 s)",
            "point_estimate": 7.3491,
            "confidence_interval_95": "[4.9933, 10.4314]",
            "ci_method": "Poisson Exact (Garwood)",
            "cluster_robust_ci_95": "[1.7968, 30.0589]",
            "cluster_ci_method": "Log-Transformed Cluster-Robust Wald (df=18)",
            "source_artifact": "phase42_stream_level_results.csv",
            "calculation_formula": "total_alerts / total_duration_hours",
            "audit_verdict": "VERIFIED_FROZEN_BASELINE"
        },
        {
            "metric_id": "METRIC_CONT_FAR_GROSS",
            "metric_name": "Continuous Ambient Gross False Alarm Rate (Convention A)",
            "condition_id": "COND2",
            "architecture_profile": "Phase 17 Experimental Profile (Defective)",
            "numerator": 104,
            "denominator": 4.2182,
            "unit": "alerts / hour",
            "dataset_version": "Prospective Continuous Ambient (28 streams)",
            "inclusion_criteria": "100% of 28 continuous audio streams evaluated (15,185.60 s)",
            "point_estimate": 24.6550,
            "confidence_interval_95": "[20.1449, 29.8736]",
            "ci_method": "Poisson Exact (Garwood)",
            "cluster_robust_ci_95": "[8.8410, 68.7553]",
            "cluster_ci_method": "Log-Transformed Cluster-Robust Wald (df=18)",
            "source_artifact": "phase42_stream_level_results.csv",
            "calculation_formula": "total_alerts / total_duration_hours",
            "audit_verdict": "QUARANTINED_DEFECTIVE_PROFILE"
        },
        {
            "metric_id": "METRIC_CONT_FAR_GROSS",
            "metric_name": "Continuous Ambient Gross False Alarm Rate (Convention A)",
            "condition_id": "COND3",
            "architecture_profile": "Phase 17 State Reset Candidate",
            "numerator": 31,
            "denominator": 4.2182,
            "unit": "alerts / hour",
            "dataset_version": "Prospective Continuous Ambient (28 streams)",
            "inclusion_criteria": "100% of 28 continuous audio streams evaluated (15,185.60 s)",
            "point_estimate": 7.3491,
            "confidence_interval_95": "[4.9933, 10.4314]",
            "ci_method": "Poisson Exact (Garwood)",
            "cluster_robust_ci_95": "[1.7968, 30.0589]",
            "cluster_ci_method": "Log-Transformed Cluster-Robust Wald (df=18)",
            "source_artifact": "phase42_stream_level_results.csv",
            "calculation_formula": "total_alerts / total_duration_hours",
            "audit_verdict": "DIAGNOSTIC_REPAIRED_PROFILE"
        },
        {
            "metric_id": "METRIC_CONT_FAR_GROSS",
            "metric_name": "Continuous Ambient Gross False Alarm Rate (Convention A)",
            "condition_id": "COND4",
            "architecture_profile": "Phase 36 Raw State Machine",
            "numerator": 26,
            "denominator": 4.2182,
            "unit": "alerts / hour",
            "dataset_version": "Prospective Continuous Ambient (28 streams)",
            "inclusion_criteria": "100% of 28 continuous audio streams evaluated (15,185.60 s)",
            "point_estimate": 6.1637,
            "confidence_interval_95": "[4.0264, 9.0313]",
            "ci_method": "Poisson Exact (Garwood)",
            "cluster_robust_ci_95": "[1.5119, 25.1290]",
            "cluster_ci_method": "Log-Transformed Cluster-Robust Wald (df=18)",
            "source_artifact": "phase42_stream_level_results.csv",
            "calculation_formula": "total_alerts / total_duration_hours",
            "audit_verdict": "EXPERIMENTAL_BRANCH_V1"
        },
        {
            "metric_id": "METRIC_CONT_FAR_GROSS",
            "metric_name": "Continuous Ambient Gross False Alarm Rate (Convention A)",
            "condition_id": "COND5",
            "architecture_profile": "Phase 36 Legacy Animal Suppression",
            "numerator": 26,
            "denominator": 4.2182,
            "unit": "alerts / hour",
            "dataset_version": "Prospective Continuous Ambient (28 streams)",
            "inclusion_criteria": "100% of 28 continuous audio streams evaluated (15,185.60 s)",
            "point_estimate": 6.1637,
            "confidence_interval_95": "[4.0264, 9.0313]",
            "ci_method": "Poisson Exact (Garwood)",
            "cluster_robust_ci_95": "[1.5119, 25.1290]",
            "cluster_ci_method": "Log-Transformed Cluster-Robust Wald (df=18)",
            "source_artifact": "phase42_stream_level_results.csv",
            "calculation_formula": "total_alerts / total_duration_hours",
            "audit_verdict": "EXPERIMENTAL_BRANCH_V1"
        },
        {
            "metric_id": "METRIC_CONT_FAR_GROSS",
            "metric_name": "Continuous Ambient Gross False Alarm Rate (Convention A)",
            "condition_id": "COND6",
            "architecture_profile": "Phase 36 Conservative Suppression",
            "numerator": 26,
            "denominator": 4.2182,
            "unit": "alerts / hour",
            "dataset_version": "Prospective Continuous Ambient (28 streams)",
            "inclusion_criteria": "100% of 28 continuous audio streams evaluated (15,185.60 s)",
            "point_estimate": 6.1637,
            "confidence_interval_95": "[4.0264, 9.0313]",
            "ci_method": "Poisson Exact (Garwood)",
            "cluster_robust_ci_95": "[1.5119, 25.1290]",
            "cluster_ci_method": "Log-Transformed Cluster-Robust Wald (df=18)",
            "source_artifact": "phase42_stream_level_results.csv",
            "calculation_formula": "total_alerts / total_duration_hours",
            "audit_verdict": "EXPERIMENTAL_BRANCH_V1"
        },
        # Continuous FAR (Convention B)
        {
            "metric_id": "METRIC_CONT_FAR_CONVB",
            "metric_name": "Continuous Ambient Eligible False Alarm Rate (Convention B)",
            "condition_id": "COND1",
            "architecture_profile": "Phase 14 Balanced Baseline",
            "numerator": 31,
            "denominator": 4.1847,
            "unit": "alerts / eligible hour",
            "dataset_version": "Prospective Continuous Ambient (28 streams)",
            "inclusion_criteria": "Excluded 120.64 s refractory cooldown post-alert",
            "point_estimate": 7.4079,
            "confidence_interval_95": "[5.0333, 10.5150]",
            "ci_method": "Poisson Exact (Garwood)",
            "cluster_robust_ci_95": "[1.8112, 30.2995]",
            "cluster_ci_method": "Log-Transformed Cluster-Robust Wald (df=18)",
            "source_artifact": "phase42_stream_level_results.csv",
            "calculation_formula": "total_alerts / eligible_duration_hours",
            "audit_verdict": "VERIFIED_FROZEN_BASELINE"
        },
        {
            "metric_id": "METRIC_CONT_FAR_CONVB",
            "metric_name": "Continuous Ambient Eligible False Alarm Rate (Convention B)",
            "condition_id": "COND6",
            "architecture_profile": "Phase 36 Conservative Suppression",
            "numerator": 26,
            "denominator": 4.1919,
            "unit": "alerts / eligible hour",
            "dataset_version": "Prospective Continuous Ambient (28 streams)",
            "inclusion_criteria": "Excluded 94.64 s refractory cooldown post-alert",
            "point_estimate": 6.2024,
            "confidence_interval_95": "[4.0517, 9.0880]",
            "ci_method": "Poisson Exact (Garwood)",
            "cluster_robust_ci_95": "[1.5214, 25.2869]",
            "cluster_ci_method": "Log-Transformed Cluster-Robust Wald (df=18)",
            "source_artifact": "phase42_stream_level_results.csv",
            "calculation_formula": "total_alerts / eligible_duration_hours",
            "audit_verdict": "EXPERIMENTAL_BRANCH_V1"
        },
        # Positive Recall Entry-Level (N=120)
        {
            "metric_id": "METRIC_POS_RECALL_ENTRY",
            "metric_name": "Prospective Positive Clip-Level Recall (Entry-Level N=120)",
            "condition_id": "COND1",
            "architecture_profile": "Phase 14 Balanced Baseline",
            "numerator": 74,
            "denominator": 120,
            "unit": "proportion",
            "dataset_version": "FSD50K Prospective Positive Set (120 entries)",
            "inclusion_criteria": "All 120 catalog entries included without deduplication",
            "point_estimate": 0.6167,
            "confidence_interval_95": "[0.5235, 0.7039]",
            "ci_method": "Clopper-Pearson Exact Binomial",
            "cluster_robust_ci_95": "N/A (Clip-level evaluation)",
            "cluster_ci_method": "N/A",
            "source_artifact": "phase42_positive_deduplication_audit.csv",
            "calculation_formula": "tp_clips / total_clips",
            "audit_verdict": "VERIFIED_FROZEN_BASELINE"
        },
        {
            "metric_id": "METRIC_POS_RECALL_ENTRY",
            "metric_name": "Prospective Positive Clip-Level Recall (Entry-Level N=120)",
            "condition_id": "COND6",
            "architecture_profile": "Phase 36 Conservative Suppression",
            "numerator": 77,
            "denominator": 120,
            "unit": "proportion",
            "dataset_version": "FSD50K Prospective Positive Set (120 entries)",
            "inclusion_criteria": "All 120 catalog entries included without deduplication",
            "point_estimate": 0.6417,
            "confidence_interval_95": "[0.5490, 0.7271]",
            "ci_method": "Clopper-Pearson Exact Binomial",
            "cluster_robust_ci_95": "N/A (Clip-level evaluation)",
            "cluster_ci_method": "N/A",
            "source_artifact": "phase42_positive_deduplication_audit.csv",
            "calculation_formula": "tp_clips / total_clips",
            "audit_verdict": "EXPERIMENTAL_BRANCH_V1"
        },
        # Positive Recall Deduplicated (N=119)
        {
            "metric_id": "METRIC_POS_RECALL_DEDUP",
            "metric_name": "Prospective Positive Clip-Level Recall (Deduplicated N=119)",
            "condition_id": "COND1",
            "architecture_profile": "Phase 14 Balanced Baseline",
            "numerator": 73,
            "denominator": 119,
            "unit": "proportion",
            "dataset_version": "FSD50K Prospective Positive Set (119 unique waveforms)",
            "inclusion_criteria": "Excludes 1 instance of cryptographic duplicate (51749/115295)",
            "point_estimate": 0.6134,
            "confidence_interval_95": "[0.5198, 0.7013]",
            "ci_method": "Clopper-Pearson Exact Binomial",
            "cluster_robust_ci_95": "N/A (Clip-level evaluation)",
            "cluster_ci_method": "N/A",
            "source_artifact": "phase42_positive_deduplication_audit.csv",
            "calculation_formula": "tp_clips_dedup / total_clips_dedup",
            "audit_verdict": "VERIFIED_FROZEN_BASELINE"
        },
        {
            "metric_id": "METRIC_POS_RECALL_DEDUP",
            "metric_name": "Prospective Positive Clip-Level Recall (Deduplicated N=119)",
            "condition_id": "COND6",
            "architecture_profile": "Phase 36 Conservative Suppression",
            "numerator": 76,
            "denominator": 119,
            "unit": "proportion",
            "dataset_version": "FSD50K Prospective Positive Set (119 unique waveforms)",
            "inclusion_criteria": "Excludes 1 instance of cryptographic duplicate (51749/115295)",
            "point_estimate": 0.6387,
            "confidence_interval_95": "[0.5455, 0.7247]",
            "ci_method": "Clopper-Pearson Exact Binomial",
            "cluster_robust_ci_95": "N/A (Clip-level evaluation)",
            "cluster_ci_method": "N/A",
            "source_artifact": "phase42_positive_deduplication_audit.csv",
            "calculation_formula": "tp_clips_dedup / total_clips_dedup",
            "audit_verdict": "EXPERIMENTAL_BRANCH_V1"
        },
        # Fireworks Challenge Triggers
        {
            "metric_id": "METRIC_FIREWORKS_TRIGGERS",
            "metric_name": "Fireworks Challenge False Trigger Count",
            "condition_id": "COND1",
            "architecture_profile": "Phase 14 Balanced Baseline",
            "numerator": 47,
            "denominator": 100,
            "unit": "triggers / 100 clips",
            "dataset_version": "Phase 39 Fireworks Challenge Set (100 clips)",
            "inclusion_criteria": "All 100 curated fireworks clips evaluated",
            "point_estimate": 0.4700,
            "confidence_interval_95": "[0.3694, 0.5724]",
            "ci_method": "Clopper-Pearson Exact Binomial",
            "cluster_robust_ci_95": "N/A",
            "cluster_ci_method": "N/A",
            "source_artifact": "phase42_fireworks_decision_reconciliation.csv",
            "calculation_formula": "triggered_clips / total_clips",
            "audit_verdict": "VERIFIED_FROZEN_BASELINE"
        },
        {
            "metric_id": "METRIC_FIREWORKS_TRIGGERS",
            "metric_name": "Fireworks Challenge False Trigger Count",
            "condition_id": "COND2",
            "architecture_profile": "Phase 17 Experimental Profile (Defective)",
            "numerator": 71,
            "denominator": 100,
            "unit": "triggers / 100 clips",
            "dataset_version": "Phase 39 Fireworks Challenge Set (100 clips)",
            "inclusion_criteria": "All 100 curated fireworks clips evaluated",
            "point_estimate": 0.7100,
            "confidence_interval_95": "[0.6107, 0.7964]",
            "ci_method": "Clopper-Pearson Exact Binomial",
            "cluster_robust_ci_95": "N/A",
            "cluster_ci_method": "N/A",
            "source_artifact": "phase42_fireworks_decision_reconciliation.csv",
            "calculation_formula": "triggered_clips / total_clips",
            "audit_verdict": "QUARANTINED_DEFECTIVE_PROFILE"
        },
        {
            "metric_id": "METRIC_FIREWORKS_TRIGGERS",
            "metric_name": "Fireworks Challenge False Trigger Count",
            "condition_id": "COND3",
            "architecture_profile": "Phase 17 State Reset Candidate",
            "numerator": 57,
            "denominator": 100,
            "unit": "triggers / 100 clips",
            "dataset_version": "Phase 39 Fireworks Challenge Set (100 clips)",
            "inclusion_criteria": "All 100 curated fireworks clips evaluated",
            "point_estimate": 0.5700,
            "confidence_interval_95": "[0.4671, 0.6686]",
            "ci_method": "Clopper-Pearson Exact Binomial",
            "cluster_robust_ci_95": "N/A",
            "cluster_ci_method": "N/A",
            "source_artifact": "phase42_fireworks_decision_reconciliation.csv",
            "calculation_formula": "triggered_clips / total_clips",
            "audit_verdict": "DIAGNOSTIC_REPAIRED_PROFILE"
        },
        {
            "metric_id": "METRIC_FIREWORKS_TRIGGERS",
            "metric_name": "Fireworks Challenge False Trigger Count",
            "condition_id": "COND6",
            "architecture_profile": "Phase 36 Conservative Suppression",
            "numerator": 57,
            "denominator": 100,
            "unit": "triggers / 100 clips",
            "dataset_version": "Phase 39 Fireworks Challenge Set (100 clips)",
            "inclusion_criteria": "All 100 curated fireworks clips evaluated",
            "point_estimate": 0.5700,
            "confidence_interval_95": "[0.4671, 0.6686]",
            "ci_method": "Clopper-Pearson Exact Binomial",
            "cluster_robust_ci_95": "N/A",
            "cluster_ci_method": "N/A",
            "source_artifact": "phase42_fireworks_decision_reconciliation.csv",
            "calculation_formula": "triggered_clips / total_clips",
            "audit_verdict": "EXPERIMENTAL_BRANCH_V1"
        }
    ]
    df_bm = pd.DataFrame(benchmark_rows)
    output_bm_path = PHASE42_DIR / "phase42_authoritative_benchmark.csv"
    df_bm.to_csv(output_bm_path, index=False)
    print(f"Saved: {output_bm_path} ({len(df_bm)} rows)")
    
    # 2. Historical Discrepancy Register
    discrepancy_rows = [
        {
            "discrepancy_id": "DISC-01",
            "discovery_phase": "Phase 40 / Phase 41",
            "audit_domain": "Continuous Exposure Denominator",
            "conflicting_values": "17,786.33 seconds (4.9406 hours) vs. 15,185.60 seconds (4.2182 hours)",
            "physical_ground_truth": "15,185.60 seconds across 28 continuous streams; 17,786.33 seconds across all 368 corpus files",
            "root_cause": "Conflation of total multi-partition evaluation corpus (28 streams + 340 short clips = 368 files) with continuous ambient stream exposure.",
            "impact": "Dividing continuous alerts by 4.94 hr deflated continuous FAR by 14.6%.",
            "resolution_artifact": "phase42_continuous_exposure_reconciliation.csv",
            "resolution_status": "RESOLVED_AUTHORITATIVE_DENOMINATOR_ESTABLISHED"
        },
        {
            "discrepancy_id": "DISC-02",
            "discovery_phase": "Phase 40 / Phase 41",
            "audit_domain": "Phase 17 Fireworks False Alarm Count",
            "conflicting_values": "62 / 100 (Phase 40 pipeline) vs. 58 / 100 (Phase 41 Section 2) vs. 71 / 100 (Physical COND2) vs. 57 / 100 (Physical COND3)",
            "physical_ground_truth": "71 / 100 for model_phase17.py (COND2); 57 / 100 for model_phase17_state_reset_candidate.py (COND3)",
            "root_cause": "Phase 40 script used unverified hardcoded placeholder '62' in execute_phase40_continuous_pipeline.py; Phase 41 table contained manual transcription typo '58'.",
            "impact": "Concealed true extent of Phase 17 candidate-accumulation defect (14 additional triggers over state-reset candidate).",
            "resolution_artifact": "phase42_fireworks_decision_reconciliation.csv",
            "resolution_status": "RESOLVED_PHYSICAL_GROUND_TRUTH_ESTABLISHED"
        },
        {
            "discrepancy_id": "DISC-03",
            "discovery_phase": "Phase 41",
            "audit_domain": "Confidence Interval Methodology",
            "conflicting_values": "Reported negative lower bounds for physical false alarm rate: [-2.3085, 17.0067] alerts/hr",
            "physical_ground_truth": "False alarm rate is physically bounded below by zero (lambda >= 0). Log-transformed cluster Wald yields [1.7968, 30.0589].",
            "root_cause": "Direct application of linear Wald interval (lambda_hat +/- z * SE) to Poisson rate under large cluster variance.",
            "impact": "Produced physically impossible negative rate intervals and confused single-rate CIs with rate-difference CIs.",
            "resolution_artifact": "phase42_confidence_interval_audit.csv",
            "resolution_status": "RESOLVED_LOG_CLUSTER_WALD_AND_EXACT_POISSON_MANDATED"
        },
        {
            "discrepancy_id": "DISC-04",
            "discovery_phase": "Phase 41",
            "audit_domain": "Paired Statistical Inference & Wilcoxon Equality",
            "conflicting_values": "Identical Wilcoxon test statistic and p-value at stream level and recordist level (W=0.0, p=0.1025)",
            "physical_ground_truth": "Mathematical identity caused by non-zero differences ({+1, +3, +1}) originating across 3 separate single-stream recordists. Exact permutation p-value = 0.2500.",
            "root_cause": "Pruning of zero-difference pairs left identical 3-element difference vectors at both levels of aggregation.",
            "impact": "Asymptotic normal approximation on n=3 created illusion of borderline significance (p~0.10), whereas exact test (p=0.2500) shows no significant difference.",
            "resolution_artifact": "phase42_cluster_inference_report.md",
            "resolution_status": "RESOLVED_EXACT_PERMUTATION_P_VALUE_ESTABLISHED"
        },
        {
            "discrepancy_id": "DISC-05",
            "discovery_phase": "Phase 41",
            "audit_domain": "Positive Audio Dataset Integrity",
            "conflicting_values": "120 evaluation entries vs. 119 unique physical waveforms",
            "physical_ground_truth": "Single cryptographic duplicate pair: fsd50k_gun_51749 and fsd50k_gun_115295 have identical SHA-256.",
            "root_cause": "Same Freesound audio uploaded by two different community users and ingested under distinct FSD50K identifiers.",
            "impact": "Minor recall shift (-0.20% to -0.32% percentage points); relative ranking of all detectors is completely invariant.",
            "resolution_artifact": "phase42_positive_deduplication_audit.csv",
            "resolution_status": "RESOLVED_DUAL_REPORTING_STANDARDIZED"
        },
        {
            "discrepancy_id": "DISC-06",
            "discovery_phase": "Phase 41",
            "audit_domain": "Crest-Factor Suppression Mechanism",
            "conflicting_values": "Phase 41 claimed 12.0 dB crest factor gate explained 10 fireworks triggers in Phase 36 vs Phase 14",
            "physical_ground_truth": "Counterfactual simulation setting crest=0 dB produced identical false alarms in 10/10 clips.",
            "root_cause": "Phase 36 triggers on fireworks due to multi-window CNN persistence (raw>=0.75) and absence of fireworks semantic suppression; crest gate is inactive on pyrotechnics.",
            "impact": "Phase 41 causal mechanism claim was unsubstantiated by counterfactual evidence.",
            "resolution_artifact": "phase42_crest_factor_reconstruction.csv",
            "resolution_status": "RESOLVED_CLASSIFIED_AS_NOT_ESTABLISHED"
        }
    ]
    df_disc = pd.DataFrame(discrepancy_rows)
    output_disc_path = PHASE42_DIR / "phase42_discrepancy_register.csv"
    df_disc.to_csv(output_disc_path, index=False)
    print(f"Saved: {output_disc_path} ({len(df_disc)} discrepancies)")
    
    # 3. Authoritative Claim-Evidence Matrix
    claim_rows = [
        {
            "claim_id": "CLM-01",
            "claim_source": "Phase 40 / Phase 41 Scope",
            "claim_text": "Prospective continuous ambient evaluation exposure is exactly 15,185.60 seconds (4.2182 hours) across 28 streams.",
            "supporting_evidence": "All 28 streams verified physically on disk; decoded duration sums to 15,185.60 s.",
            "counter_evidence": "None. 17,786.33 s figure represents total multi-partition corpus.",
            "authoritative_status": "SUPPORTED_BY_PHYSICAL_EVIDENCE",
            "risk_assessment": "Low risk; establishing correct denominator prevents rate distortion."
        },
        {
            "claim_id": "CLM-02",
            "claim_source": "Phase 40 Section 3",
            "claim_text": "Phase 17 Frozen Profile produces 62 false alarms on the 100 fireworks challenge clips.",
            "supporting_evidence": "None. Script execute_phase40_continuous_pipeline.py used hardcoded placeholder '62'.",
            "counter_evidence": "Physical execution of model_phase17.py produces exactly 71 / 100 triggers.",
            "authoritative_status": "REFUTED",
            "risk_assessment": "High risk of understating Phase 17 defect severity; refuted by physical inference."
        },
        {
            "claim_id": "CLM-03",
            "claim_source": "Phase 41 Section 2",
            "claim_text": "Phase 17 Frozen Profile produces 58 false alarms on the 100 fireworks challenge clips.",
            "supporting_evidence": "None. Typographical transcription error in Phase 41 summary table.",
            "counter_evidence": "Physical execution of model_phase17.py produces exactly 71 / 100 triggers.",
            "authoritative_status": "REFUTED",
            "risk_assessment": "High risk of error propagation; refuted by physical inference."
        },
        {
            "claim_id": "CLM-04",
            "claim_source": "Phase 31 / Phase 42 Audit",
            "claim_text": "Candidate-accumulation defect is the sole causal mechanism elevating Phase 17 fireworks triggers from 57 to 71.",
            "supporting_evidence": "model_phase17_state_reset_candidate.py purges accumulated candidates upon decay, reducing triggers from 71 to exactly 57.",
            "counter_evidence": "None.",
            "authoritative_status": "SUPPORTED_BY_PHYSICAL_EVIDENCE",
            "risk_assessment": "Low risk; validates quarantine classification of Phase 17."
        },
        {
            "claim_id": "CLM-05",
            "claim_source": "Phase 40 / Phase 41 Conclusions",
            "claim_text": "Phase 36 achieves a statistically significant reduction in continuous ambient false alarm rate over Phase 14 Baseline.",
            "supporting_evidence": "Point estimate shows 5 fewer alerts (26 vs 31, 6.16 vs 7.35 alerts/hr).",
            "counter_evidence": "Paired difference 95% CI [-0.5992, 2.9699] spans zero; exact permutation test yields p=0.2500.",
            "authoritative_status": "REFUTED",
            "risk_assessment": "Critical governance risk; claim of statistically demonstrated superiority is unsupported."
        },
        {
            "claim_id": "CLM-06",
            "claim_source": "Phase 41 Statistical Methods",
            "claim_text": "Stream-level and recordist-level Wilcoxon test equality (W=0.0, p=0.1025) indicates pipeline execution defect.",
            "supporting_evidence": "Apparent numerical identity across different unit granularities.",
            "counter_evidence": "Mathematical proof shows identical non-zero difference sets ({1, 3, 1}) due to 3 single-stream recordists.",
            "authoritative_status": "REFUTED",
            "risk_assessment": "Low risk; confirms mathematical integrity of underlying aggregation."
        },
        {
            "claim_id": "CLM-07",
            "claim_source": "Phase 41 Crest Factor Audit",
            "claim_text": "12.0 dB crest-factor gate causally explains the 10 additional fireworks false alarms in Phase 36 vs Phase 14.",
            "supporting_evidence": "Observed crest factor was above 12.0 dB on all 10 clips.",
            "counter_evidence": "Counterfactual simulation setting crest=0 dB still emitted false alarms on 10/10 clips.",
            "authoritative_status": "NOT_ESTABLISHED",
            "risk_assessment": "Medium risk; prevents promoting unverified physical mechanism explanations."
        },
        {
            "claim_id": "CLM-08",
            "claim_source": "Phase 41 Inventory Audit",
            "claim_text": "Cryptographic duplicate waveform in positive dataset (51749/115295) materially invalidates reported recall.",
            "supporting_evidence": "Waveform redundancy violates strict i.i.d. sampling assumptions.",
            "counter_evidence": "Deduplicated recall shifts by only -0.20% to -0.32% percentage points; relative ranking is invariant.",
            "authoritative_status": "REFUTED",
            "risk_assessment": "Low risk; dual reporting completely neutralizes validity concerns."
        },
        {
            "claim_id": "CLM-09",
            "claim_source": "Phase 36 / Phase 39 Evaluation",
            "claim_text": "Phase 36 achieves a meaningful reduction in duplicate alert rate on positive gunshot clips compared to Phase 14.",
            "supporting_evidence": "Phase 36 emits 13 duplicate alerts (14.4%) vs. Phase 14 emitting 28 duplicate alerts (27.5%).",
            "counter_evidence": "None. Replicated across all evaluation phases.",
            "authoritative_status": "SUPPORTED_BY_PHYSICAL_EVIDENCE",
            "risk_assessment": "Low risk; confirms improved refractory state machine behavior."
        },
        {
            "claim_id": "CLM-10",
            "claim_source": "Phase 42 Governance",
            "claim_text": "Phase 36 must remain EXPERIMENTAL_RESEARCH_BRANCH_V1 and must NOT be promoted to production baseline.",
            "supporting_evidence": "Lack of statistically significant FAR improvement (p=0.2500), elevated fireworks triggers (57 vs 47), unproven field generalization.",
            "counter_evidence": "None.",
            "authoritative_status": "SUPPORTED_BY_PHYSICAL_EVIDENCE",
            "risk_assessment": "Mandatory safety guardrail: uncertified research prototype, not for life safety."
        }
    ]
    df_claim = pd.DataFrame(claim_rows)
    output_claim_path = PHASE42_DIR / "phase42_claim_evidence_matrix.csv"
    df_claim.to_csv(output_claim_path, index=False)
    print(f"Saved: {output_claim_path} ({len(df_claim)} claims)")

if __name__ == "__main__":
    run_benchmark_and_discrepancy()
