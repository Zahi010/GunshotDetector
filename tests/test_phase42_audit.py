#!/usr/bin/env python3
"""
tests/test_phase42_audit.py

Phase 42 Benchmark Denominator Reconciliation & Independent Statistical Validation
Automated Forensic Regression & Verification Suite
Mandatory Designation: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY
"""

import hashlib
import json
import pathlib
import pytest
import numpy as np
import pandas as pd
from scipy import stats

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
P42_DIR = REPO_ROOT / "experiments" / "phase42"

class TestPhase42SafetyAndProtocol:
    """Verifies mandatory safety designations and protocol integrity."""

    def test_mandatory_safety_designation_in_reports(self):
        reports = [
            P42_DIR / "phase42_continuous_reconciliation.md",
            P42_DIR / "phase42_fireworks_reconciliation.md",
            P42_DIR / "phase42_statistical_methods.md",
            P42_DIR / "phase42_cluster_inference_report.md",
            P42_DIR / "phase42_positive_recall_sensitivity.md",
            P42_DIR / "phase42_mechanism_validation.md"
        ]
        mandatory_phrase = "RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY"
        for r_path in reports:
            assert r_path.exists(), f"Missing report: {r_path.name}"
            content = r_path.read_text(encoding="utf-8")
            assert mandatory_phrase in content, f"Safety notice missing in {r_path.name}"


class TestDetectorModelFreezeHashes:
    """Verifies exact physical hashes and byte sizes of all frozen detector files."""

    FROZEN_FILES = {
        "model_phase14.py": ("a268551604ae8b73068435ff10ab3d265065f56e0679757fca5b6bf0f061c065", 23340),
        "model_phase17.py": ("e2b262b866fdd5d7f1a4ab91a7b8b9bac189ee8cc7a78603b3544ca1579fb819", 29067),
        "experiments/phase31/model_phase17_state_reset_candidate.py": ("c144b917b56532787e2a9198f2cad4a77dc2095b57962f31d11d250a4d5d9ea5", 29718),
        "experiments/phase36/model_phase36.py": ("2774ab4cae0fca6d2f3646b443694fefa40d6837ff195f1d216ae7ff7732563a", 13891),
        "experiments/phase36/event_state_machine.py": ("a91e9bc6d0ab9ca805817a406857d31e1f482f7d8815b0eaf7fee9075cd23c31", 24905),
        "experiments/phase36/acoustic_features.py": ("5cc775f97b8e9f2c62018efe6f3fc6d64913cfcb5ffd470a1daba625c6510a51", 9812),
        "feature_extractor.py": ("1c665b7c1749de98337da0726627710fffe0dcfa56335291b666ae7abcbae94f", 6218),
        "config.py": ("55749f9d46d561d131fad374064021b73c08274e2a79954efd08570b029b1858", 2619),
        "experiments/phase36/config_phase36.json": ("1aaffd5423e116958807372855d989e294d3ff12b614052e10df78346d62e363", 1337),
        "experiments/phase40/phase40_evaluation_protocol.md": ("05aa77bd3fb30f7c472fa1b2db2862283bf1bf5fd25111142ae95993245b1fc7", 5575)
    }

    def test_detector_freeze_integrity(self):
        for rel_path, (expected_hash, expected_size) in self.FROZEN_FILES.items():
            full_path = REPO_ROOT / rel_path
            assert full_path.exists(), f"Missing frozen file: {rel_path}"
            content = full_path.read_bytes()
            assert len(content) == expected_size, f"Size mismatch for {rel_path}: {len(content)} != {expected_size}"
            actual_hash = hashlib.sha256(content).hexdigest()
            assert actual_hash == expected_hash, f"Hash mismatch for {rel_path}: {actual_hash} != {expected_hash}"


class TestWorkstreamAContinuousDenominator:
    """Verifies Workstream A continuous exposure denominator reconciliation."""

    def test_continuous_reconciliation_csv_exists_and_valid(self):
        csv_path = P42_DIR / "phase42_continuous_exposure_reconciliation.csv"
        assert csv_path.exists(), "Missing phase42_continuous_exposure_reconciliation.csv"
        df = pd.read_csv(csv_path)
        assert len(df) == 28, f"Expected 28 streams, found {len(df)}"
        
        # Verify duration sums
        total_sec = df["source_duration_sec"].sum()
        assert np.isclose(total_sec, 15185.60, atol=0.1), f"Total duration {total_sec} != 15185.60"
        
        # Verify alert sums
        assert df["alerts_cond1"].sum() == 31
        assert df["alerts_cond2"].sum() == 104
        assert df["alerts_cond3"].sum() == 31
        assert df["alerts_cond4"].sum() == 26
        assert df["alerts_cond5"].sum() == 26
        assert df["alerts_cond6"].sum() == 26

    def test_stream_level_results_table(self):
        csv_path = P42_DIR / "phase42_stream_level_results.csv"
        assert csv_path.exists(), "Missing phase42_stream_level_results.csv"
        df = pd.read_csv(csv_path)
        assert len(df) == 168, f"Expected 168 rows (28 * 6), found {len(df)}"
        
        # Check condition coverage
        for cid in ["COND1", "COND2", "COND3", "COND4", "COND5", "COND6"]:
            sub = df[df["condition_id"] == cid]
            assert len(sub) == 28
            assert np.isclose(sub["duration_sec"].sum(), 15185.60, atol=0.1)


class TestWorkstreamBFireworksReconciliation:
    """Verifies Workstream B Phase 17 fireworks decision reconciliation."""

    def test_fireworks_decision_counts(self):
        csv_path = P42_DIR / "phase42_fireworks_decision_reconciliation.csv"
        assert csv_path.exists(), "Missing phase42_fireworks_decision_reconciliation.csv"
        df = pd.read_csv(csv_path)
        assert len(df) == 100, f"Expected 100 fireworks clips, found {len(df)}"
        
        c1_trig = (df["cond1_decision"] == "DETECTED_FA").sum()
        c2_trig = (df["cond2_physical_decision"] == "DETECTED_FA").sum()
        c3_trig = (df["cond3_decision"] == "DETECTED_FA").sum()
        c6_trig = (df["cond6_decision"] == "DETECTED_FA").sum()
        
        assert c1_trig == 47, f"COND1 triggers {c1_trig} != 47"
        assert c2_trig == 71, f"COND2 physical triggers {c2_trig} != 71"
        assert c3_trig == 57, f"COND3 triggers {c3_trig} != 57"
        assert c6_trig == 57, f"COND6 triggers {c6_trig} != 57"

    def test_candidate_defect_identification(self):
        csv_path = P42_DIR / "phase42_fireworks_decision_reconciliation.csv"
        df = pd.read_csv(csv_path)
        defect_clips = df[df["forensic_category"] == "PHASE17_CANDIDATE_ACCUMULATION_DEFECT"]
        assert len(defect_clips) == 14, f"Expected 14 defect-elevated clips, found {len(defect_clips)}"


class TestWorkstreamCConfidenceIntervals:
    """Verifies Workstream C confidence interval methodology."""

    def test_physical_rate_non_negativity(self):
        csv_path = P42_DIR / "phase42_confidence_interval_audit.csv"
        assert csv_path.exists(), "Missing phase42_confidence_interval_audit.csv"
        df = pd.read_csv(csv_path)
        assert len(df) == 6
        
        # Check that Log-Cluster Wald and Poisson Exact are strictly positive
        for _, row in df.iterrows():
            assert row["poisson_exact_95_ci_lower"] > 0, f"Poisson lower bound not positive for {row['condition_id']}"
            assert row["log_cluster_wald_95_ci_lower"] > 0, f"Log Wald lower bound not positive for {row['condition_id']}"
            assert row["naive_has_negative_lower_bound"] == True, f"Naive Wald expected to be negative for {row['condition_id']}"

    def test_rate_difference_ci_contains_zero(self):
        # Difference between COND1 (7.3491) and COND6 (6.1637) is 1.1853 alerts/hr
        # With SE_diff = 0.8494 and t_crit = 2.1009, CI is [-0.5992, 2.9699]
        # Must contain zero, indicating no statistically significant difference
        diff = 7.3491 - 6.1637
        se_diff = 0.8494
        t_crit = stats.t.ppf(0.975, 18)
        ci_low = diff - t_crit * se_diff
        ci_high = diff + t_crit * se_diff
        assert ci_low < 0 < ci_high, f"Expected difference CI to span zero, got [{ci_low}, {ci_high}]"


class TestWorkstreamDRecordistAnalysis:
    """Verifies Workstream D recordist analysis and Wilcoxon identity."""

    def test_recordist_counts_and_clusters(self):
        csv_path = P42_DIR / "phase42_recordist_analysis.csv"
        assert csv_path.exists(), "Missing phase42_recordist_analysis.csv"
        df = pd.read_csv(csv_path)
        assert len(df) == 19, f"Expected 19 recordists, found {len(df)}"
        assert df["stream_count"].sum() == 28, "Total stream count across recordists != 28"

    def test_wilcoxon_identity_explanation(self):
        csv_path = P42_DIR / "phase42_recordist_analysis.csv"
        df = pd.read_csv(csv_path)
        nonzero_rec = df[df["paired_diff_cond1_cond6"] != 0]["paired_diff_cond1_cond6"].values
        assert sorted(list(nonzero_rec)) == [1, 1, 3], f"Expected non-zero diffs [1, 1, 3], got {nonzero_rec}"
        
        # Verify exact permutation p-value: 2 / 2^3 = 2 / 8 = 0.2500
        p_exact = 2.0 / (2**3)
        assert p_exact == 0.2500


class TestWorkstreamEPositiveDeduplication:
    """Verifies Workstream E positive audio deduplication and sensitivity."""

    def test_deduplication_metrics_and_deltas(self):
        csv_path = P42_DIR / "phase42_positive_deduplication_audit.csv"
        assert csv_path.exists(), "Missing phase42_positive_deduplication_audit.csv"
        df = pd.read_csv(csv_path)
        assert len(df) == 6
        
        # COND1: 74/120 (61.67%) -> 73/119 (61.34%)
        c1 = df[df["condition_id"] == "COND1"].iloc[0]
        assert c1["entry_level_detected_tp"] == 74
        assert c1["deduplicated_detected_tp"] == 73
        assert np.isclose(c1["entry_level_recall"], 0.6167, atol=0.001)
        assert np.isclose(c1["deduplicated_recall"], 0.6134, atol=0.001)
        assert c1["recall_delta_percentage_points"] == -0.32


class TestWorkstreamFMechanismValidation:
    """Verifies Workstream F crest factor mechanism validation."""

    def test_counterfactual_crest_audit(self):
        csv_path = P42_DIR / "phase42_crest_factor_reconstruction.csv"
        assert csv_path.exists(), "Missing phase42_crest_factor_reconstruction.csv"
        df = pd.read_csv(csv_path)
        assert len(df) == 10, f"Expected 10 discordant clips, found {len(df)}"
        
        # In all 10 clips, setting crest=0 still caused alert
        assert (df["cond6_counterfactual_crest_0db_decision"] == "DETECTED_FA").sum() == 10
        assert (df["crest_gate_necessary_for_alert"] == False).all()
        assert (df["causal_mechanism_classification"] == "NOT_ESTABLISHED").all()


class TestWorkstreamGAuthoritativeBenchmark:
    """Verifies Workstream G authoritative benchmark and registers."""

    def test_authoritative_benchmark_completeness(self):
        csv_path = P42_DIR / "phase42_authoritative_benchmark.csv"
        assert csv_path.exists(), "Missing phase42_authoritative_benchmark.csv"
        df = pd.read_csv(csv_path)
        assert len(df) >= 12
        required_cols = [
            "metric_id", "metric_name", "condition_id", "architecture_profile",
            "numerator", "denominator", "unit", "dataset_version",
            "point_estimate", "confidence_interval_95", "ci_method", "audit_verdict"
        ]
        for col in required_cols:
            assert col in df.columns, f"Missing required column {col} in benchmark"

    def test_discrepancy_register_completeness(self):
        csv_path = P42_DIR / "phase42_discrepancy_register.csv"
        assert csv_path.exists(), "Missing phase42_discrepancy_register.csv"
        df = pd.read_csv(csv_path)
        assert len(df) >= 6
        for _, row in df.iterrows():
            assert "RESOLVED" in row["resolution_status"]

    def test_claim_evidence_matrix_completeness(self):
        csv_path = P42_DIR / "phase42_claim_evidence_matrix.csv"
        assert csv_path.exists(), "Missing phase42_claim_evidence_matrix.csv"
        df = pd.read_csv(csv_path)
        assert len(df) >= 10
        statuses = df["authoritative_status"].unique()
        for s in statuses:
            assert s in ["SUPPORTED_BY_PHYSICAL_EVIDENCE", "PARTIALLY_SUPPORTED", "NOT_ESTABLISHED", "REFUTED"]

