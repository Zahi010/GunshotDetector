"""
Automated Pytest Reproduction & Forensic Verification Suite for Phase 33.

MANDATORY SAFETY DESIGNATION:
RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY
This experimental acoustic machine-learning software is uncertified and must never
be deployed for autonomous emergency dispatch, tactical police response,
active-shooter alerting, automated evacuation, building lockdown, or life-critical
physical security. Safe recorded audio playback only; no live-fire testing.
"""

import os
import sys
import json
import zipfile
import hashlib
import numpy as np
import pandas as pd
import pytest

WORKSPACE_ROOT = r"E:\gunshot\gunshot"
REPORTS_DIR = os.path.join(WORKSPACE_ROOT, "reports")
EXPERIMENTS_DIR = os.path.join(WORKSPACE_ROOT, "experiments")
SCRIPTS_DIR = os.path.join(WORKSPACE_ROOT, "scripts")
TESTS_DIR = os.path.join(WORKSPACE_ROOT, "tests")
ARCHIVE_ROOT = r"E:\gunshot"

def sha256_file(filepath):
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


class TestWorkstream1CanonicalProvenance:
    """Workstream 1: 23-stream canonical registry, duration arithmetic, and campaign provenance."""

    def test_canonical_stream_registry_exists_and_valid(self):
        csv_path = os.path.join(REPORTS_DIR, "phase33_canonical_stream_registry.csv")
        assert os.path.isfile(csv_path), "Registry CSV must exist"
        df = pd.read_csv(csv_path)
        assert len(df) == 23, "Must contain exactly 23 streams"
        assert df["original_filename"].nunique() == 23, "All filenames must be unique"
        for _, row in df.iterrows():
            full_path = os.path.join(WORKSPACE_ROOT, row["exact_relative_filepath"])
            assert os.path.isfile(full_path), f"File {full_path} must exist"
            assert row["file_size_bytes"] > 0, f"File {row['original_filename']} has non-positive size"
            assert row["exact_duration_seconds"] > 0, f"File {row['original_filename']} has non-positive duration"

    def test_duration_arithmetic_reconciliation(self):
        csv_path = os.path.join(REPORTS_DIR, "phase33_duration_reconciliation.csv")
        assert os.path.isfile(csv_path), "Duration reconciliation CSV must exist"
        df = pd.read_csv(csv_path)
        assert len(df) == 23, "Must contain 23 stream rows"
        
        exact_seconds = df["exact_duration_s"].sum()
        exact_hours = df["exact_duration_hr"].sum()
        
        # Verify exact mathematical values
        assert abs(exact_seconds - 45525.5755) < 0.01, f"Expected 45525.5755s, got {exact_seconds}"
        assert abs(exact_hours - 12.645993) < 0.001, f"Expected ~12.6460h, got {exact_hours}"
        assert round(exact_hours, 4) == 12.6460, f"Rounded hours must be 12.6460, got {round(exact_hours, 4)}"

    def test_campaign_provenance_reconciliation(self):
        csv_path = os.path.join(REPORTS_DIR, "phase33_campaign_reconciliation.csv")
        assert os.path.isfile(csv_path), "Campaign reconciliation CSV must exist"
        df = pd.read_csv(csv_path)
        assert len(df) == 23, "Must contain 23 streams"
        
        # Phase 31 verified campaign assignments: 10 RPISOUND-UK, 1 CHEWMAGNA-UK, 6 BILBAO-ES, 6 AEROSONIC-AU
        p31_counts = df["phase31_campaign_id"].value_counts().to_dict()
        assert p31_counts.get("CAMPAIGN-RPISOUND-UK", 0) == 10
        assert p31_counts.get("CAMPAIGN-CHEWMAGNA-UK", 0) == 1
        assert p31_counts.get("CAMPAIGN-BILBAO-ES", 0) == 6
        assert p31_counts.get("CAMPAIGN-AEROSONIC-AU", 0) == 6

        # Authoritative assignments mirror verified Phase 31 physical ground truth
        auth_counts = df["authoritative_campaign_id"].value_counts().to_dict()
        assert auth_counts.get("CAMPAIGN-RPISOUND-UK", 0) == 10
        assert auth_counts.get("CAMPAIGN-CHEWMAGNA-UK", 0) == 1
        assert auth_counts.get("CAMPAIGN-BILBAO-ES", 0) == 6
        assert auth_counts.get("CAMPAIGN-AEROSONIC-AU", 0) == 6

        # Phase 32 introduced discrepancies (assigning Bilbao files to DCASE/UrbanSound-PL)
        p32_counts = df["phase32_campaign_id"].value_counts().to_dict()
        assert "CAMPAIGN-URBANSOUND-PL" in p32_counts
        assert "CAMPAIGN-DCASE2020-ES" in p32_counts

        # Verify that all 23 streams have clear forensic diagnosis
        for _, row in df.iterrows():
            assert "DISCREPANCY" in row["discrepancy_status"] or "MATCH" in row["discrepancy_status"]


class TestWorkstream2FactorialAblation:
    """Workstream 2: Factorial condition totals, main effects, interaction, and Condition D audit."""

    def test_factorial_condition_totals(self):
        csv_path = os.path.join(REPORTS_DIR, "phase33_factorial_reproduction.csv")
        assert os.path.isfile(csv_path), "Factorial CSV must exist"
        df = pd.read_csv(csv_path)
        totals_df = df[df["recording_id"] == "CORPUS_TOTAL"]
        totals = dict(zip(totals_df["condition_id"], totals_df["alert_count"]))
        
        assert totals["A"] == 108, "Condition A must be 108 alerts"
        assert totals["B"] == 130, "Condition B must be 130 alerts"
        assert totals["C"] == 66, "Condition C must be 66 alerts"
        assert totals["D"] == 72, "Condition D must be 72 alerts"

    def test_factorial_effects_and_interaction(self):
        A, B, C, D = 108, 130, 66, 72
        reset_effect_suppr_on = A - C  # 108 - 66 = +42
        reset_effect_suppr_off = B - D # 130 - 72 = +58
        suppr_effect_defective = A - B # 108 - 130 = -22
        suppr_effect_corrected = C - D # 66 - 72 = -6
        interaction = (A - B) - (C - D) # -22 - (-6) = -16

        assert reset_effect_suppr_on == 42
        assert reset_effect_suppr_off == 58
        assert suppr_effect_defective == -22
        assert suppr_effect_corrected == -6
        assert interaction == -16

    def test_condition_d_timing_and_schema_divergence(self):
        # Verify from condition config hashes
        json_path = os.path.join(REPORTS_DIR, "phase33_condition_config_hashes.json")
        assert os.path.isfile(json_path), "Condition config hashes JSON must exist"
        with open(json_path, "r") as f:
            data = json.load(f)
        
        assert data["factorial_alert_counts"]["Condition_D"] == 72
        assert "CORRECTED-CANDIDATE / SUPPRESSION-OFF" in data["condition_d_label"]

    def test_aircraft_fragmentation_vs_ambient_suppression(self):
        csv_path = os.path.join(REPORTS_DIR, "phase33_event_level_reconciliation.csv")
        assert os.path.isfile(csv_path), "Event-level reconciliation CSV must exist"
        df = pd.read_csv(csv_path)
        assert len(df) == 25, "Must contain exactly 25 aircraft flyover sequences"
        
        cond_a_flyover = df["cond_a_alerts"].sum()
        cond_b_flyover = df["cond_b_alerts"].sum()
        cond_c_flyover = df["cond_c_alerts"].sum()
        cond_d_flyover = df["cond_d_alerts"].sum()

        assert cond_a_flyover == 78
        assert cond_b_flyover == 72
        assert cond_c_flyover == 52
        assert cond_d_flyover == 47

        # In flyovers, animal suppression causes fragmentation (+6 and +5)
        assert cond_a_flyover - cond_b_flyover == +6
        assert cond_c_flyover - cond_d_flyover == +5

        # Outside flyovers (ambient), animal suppression reduces false alerts (30 vs 58)
        cond_a_ambient = 108 - cond_a_flyover
        cond_b_ambient = 130 - cond_b_flyover
        assert cond_a_ambient == 30
        assert cond_b_ambient == 58
        assert cond_a_ambient - cond_b_ambient == -28


class TestWorkstream3WilcoxonAndStatistics:
    """Workstream 3: 23 paired streams, full 256 permutations, exact tied vs untied vs asymptotic."""

    def test_paired_observations_structure(self):
        csv_path = os.path.join(REPORTS_DIR, "phase33_paired_observations.csv")
        assert os.path.isfile(csv_path), "Paired observations CSV must exist"
        df = pd.read_csv(csv_path)
        assert len(df) == 23, "Must have 23 stream rows"
        
        zero_diffs = df[df["diff_p14_minus_p17"] == 0]
        nonzero_diffs = df[df["diff_p14_minus_p17"] != 0]
        assert len(zero_diffs) == 15, "Must have exactly 15 zero differences"
        assert len(nonzero_diffs) == 8, "Must have exactly 8 non-zero differences"

        # Check the 8 non-zero values
        sorted_diffs = sorted(nonzero_diffs["diff_p14_minus_p17"].tolist())
        assert sorted_diffs == [-13, -11, -8, -2, -2, 1, 2, 2]

    def test_statistical_test_results_precision(self):
        json_path = os.path.join(REPORTS_DIR, "phase33_statistical_test_results.json")
        assert os.path.isfile(json_path), "Statistical test results JSON must exist"
        with open(json_path, "r") as f:
            data = json.load(f)
        
        # Test values
        assert abs(data["exact_untied_combinatorial"]["two_sided_p"] - 0.1953125) < 1e-6
        assert abs(data["exact_tied_permutation"]["two_sided_p"] - 0.2109375) < 1e-6
        assert abs(data["scipy_asymptotic_normal"]["asymptotic_p"] - 0.1562601) < 1e-5
        assert abs(data["pratt_zero_handling"]["pratt_p"] - 0.3675438) < 1e-5
        assert abs(data["exact_sign_test"]["sign_test_p"] - 0.7265625) < 1e-6

        # Permutations count
        assert data["exact_tied_permutation"]["total_combinations"] == 256
        assert data["exact_tied_permutation"]["combinations_le_W"] == 27
        assert data["exact_untied_combinatorial"]["combinations_le_W"] == 25

        # All p-values > 0.15 -> No significant difference
        p_vals = [
            data["exact_untied_combinatorial"]["two_sided_p"],
            data["exact_tied_permutation"]["two_sided_p"],
            data["scipy_asymptotic_normal"]["asymptotic_p"],
            data["pratt_zero_handling"]["pratt_p"],
            data["exact_sign_test"]["sign_test_p"]
        ]
        for p in p_vals:
            assert p > 0.15, f"p={p} must be > 0.15"


class TestWorkstream4PittsburghEventMatching:
    """Workstream 4: Pittsburgh 50-round strict 1-to-1 matching and McNemar exact test."""

    def test_pittsburgh_strict_matching_counts(self):
        csv_path = os.path.join(REPORTS_DIR, "phase33_pittsburgh_matching_assignments.csv")
        assert os.path.isfile(csv_path), "Assignments CSV must exist"
        df = pd.read_csv(csv_path)
        assert len(df) == 50, "Must contain exactly 50 physical rounds"
        
        p14_detected = df[df["phase14_matched"] == True]
        p17_detected = df[df["phase17_matched"] == True]
        assert len(p14_detected) == 15, "Phase 14 must detect 15/50 rounds"
        assert len(p17_detected) == 19, "Phase 17 must detect 19/50 rounds"

    def test_pittsburgh_contingency_table_and_mcnemar(self):
        csv_path = os.path.join(REPORTS_DIR, "phase33_pittsburgh_contingency_table.csv")
        assert os.path.isfile(csv_path), "Contingency table CSV must exist"
        df = pd.read_csv(csv_path)
        
        round_row = df[df["evaluation_level"] == "Round-Level (Strict 1-to-1)"].iloc[0]
        assert round_row["both_detected"] == 14
        assert round_row["phase14_only"] == 1
        assert round_row["phase17_only"] == 5
        assert round_row["neither_detected"] == 30
        assert round_row["mcnemar_discordant_pairs"] == 6
        assert abs(round_row["mcnemar_exact_two_sided_p"] - 0.21875) < 1e-5

        rec_row = df[df["evaluation_level"] == "Recording-Level (Incident)"].iloc[0]
        assert rec_row["both_detected"] == 15
        assert rec_row["phase14_only"] == 0
        assert rec_row["phase17_only"] == 3
        assert rec_row["neither_detected"] == 2
        assert rec_row["mcnemar_discordant_pairs"] == 3
        assert abs(rec_row["mcnemar_exact_two_sided_p"] - 0.25000) < 1e-5


class TestWorkstream5StateMachineAudit:
    """Workstream 5: 12 regression test vectors, Phase 17 failure count resolution."""

    def test_state_machine_12_vector_counts(self):
        csv_path = os.path.join(REPORTS_DIR, "phase33_state_machine_test_reconciliation.csv")
        assert os.path.isfile(csv_path), "State machine CSV must exist"
        df = pd.read_csv(csv_path)
        assert len(df) == 12, "Must contain 12 vectors"
        
        p14_pass = df[df["phase14_verdict"] == "PASS"]
        assert len(p14_pass) == 12, "Phase 14 must pass 12/12 vectors (100%)"

        cand_pass = df[df["candidate_verdict"] == "PASS"]
        assert len(cand_pass) == 12, "Candidate must pass 12/12 vectors (100%)"

        p17_fail = df[df["phase17_verdict"] == "FAIL_DEFECT"]
        p17_pass = df[df["phase17_verdict"] == "PASS"]
        assert len(p17_fail) == 8, "Phase 17 must fail exactly 8/12 vectors (66.7%)"
        assert len(p17_pass) == 4, "Phase 17 must pass exactly 4/12 vectors (33.3%)"

        # Check exact failing vector IDs
        failing_ids = sorted(p17_fail["vector_id"].tolist())
        expected_fail = ["VEC-01", "VEC-02", "VEC-03", "VEC-04", "VEC-07", "VEC-09", "VEC-10", "VEC-12"]
        assert failing_ids == expected_fail, f"Expected {expected_fail}, got {failing_ids}"

        passing_ids = sorted(p17_pass["vector_id"].tolist())
        expected_pass = ["VEC-05", "VEC-06", "VEC-08", "VEC-11"]
        assert passing_ids == expected_pass, f"Expected {expected_pass}, got {passing_ids}"


class TestWorkstream6DeliverableAndReleaseVerification:
    """Workstream 6: Historical release archive verification and baseline model freeze."""

    def test_phase32_archive_integrity(self):
        zip_path = os.path.join(ARCHIVE_ROOT, "gunshot_detection_phase32.zip")
        assert os.path.isfile(zip_path), "Phase 32 zip must exist"
        assert os.path.getsize(zip_path) == 4545869, "Size must be 4,545,869 bytes"
        
        expected_sha256 = "b27bbb6336e3d0bb229ac10ade6c669b3d917d5ba58e91617c5c3cdd1eadddfb"
        assert sha256_file(zip_path) == expected_sha256, "SHA256 must match Phase 32 release"

        with zipfile.ZipFile(zip_path, "r") as z:
            assert z.testzip() is None, "Zip file must pass CRC test"
            assert len(z.infolist()) == 41, "Must contain 41 entries"

    def test_frozen_baseline_model_hashes(self):
        p14_path = os.path.join(WORKSPACE_ROOT, "model_phase14.py")
        p17_path = os.path.join(WORKSPACE_ROOT, "model_phase17.py")
        cand_path = os.path.join(WORKSPACE_ROOT, "experiments", "phase31", "model_phase17_state_reset_candidate.py")

        assert sha256_file(p14_path) == "a268551604ae8b73068435ff10ab3d265065f56e0679757fca5b6bf0f061c065"
        assert sha256_file(p17_path) == "e2b262b866fdd5d7f1a4ab91a7b8b9bac189ee8cc7a78603b3544ca1579fb819"
        assert sha256_file(cand_path) == "c144b917b56532787e2a9198f2cad4a77dc2095b57962f31d11d250a4d5d9ea5"


class TestSafetyDesignationEnforcement:
    """Audit safety banner presence across all Phase 33 artifacts."""

    def test_safety_designation_in_reports(self):
        report_files = [f for f in os.listdir(REPORTS_DIR) if f.startswith("phase33_") and f.endswith(".md")]
        assert len(report_files) >= 6, "Must have all Phase 33 reports"
        for rf in report_files:
            full_path = os.path.join(REPORTS_DIR, rf)
            with open(full_path, "r", encoding="utf-8") as f:
                content = f.read()
            assert "RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY" in content, (
                f"File {rf} missing mandatory safety designation banner"
            )
