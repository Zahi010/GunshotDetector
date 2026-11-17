import hashlib
import json
import pathlib
import zipfile
import pytest
import numpy as np
import pandas as pd
from scipy import stats

REPO_ROOT = pathlib.Path("E:/gunshot/gunshot")
P40_DIR = REPO_ROOT / "experiments" / "phase40"

class TestPhase40SafetyAndProtocol:
    """Verifies mandatory safety designations and protocol pre-registration."""
    
    def test_mandatory_safety_designation_in_reports(self):
        reports = [
            P40_DIR / "phase40_reproduction_findings.md",
            P40_DIR / "phase40_hash_reconciliation.md",
            P40_DIR / "phase40_source_independence_report.md",
            P40_DIR / "phase40_fireworks_statistical_report.md",
            P40_DIR / "phase40_evaluation_protocol.md",
            P40_DIR / "phase40_statistical_analysis.md",
            P40_DIR / "phase40_final_audit_report.md",
            REPO_ROOT / "reports" / "phase40_final_audit_report.md"
        ]
        mandatory_phrase = "RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY."
        for r_path in reports:
            assert r_path.exists(), f"Missing report: {r_path.name}"
            content = r_path.read_text(encoding="utf-8")
            assert mandatory_phrase in content, f"Safety notice missing in {r_path.name}"

    def test_evaluation_protocol_pre_registration_hash(self):
        protocol_path = P40_DIR / "phase40_evaluation_protocol.md"
        assert protocol_path.exists(), "phase40_evaluation_protocol.md missing!"
        sha = hashlib.sha256(protocol_path.read_bytes()).hexdigest()
        expected_sha = "05aa77bd3fb30f7c472fa1b2db2862283bf1bf5fd25111142ae95993245b1fc7"
        assert sha == expected_sha, f"Protocol hash mismatch: {sha} vs {expected_sha}"


class TestDetectorModelFreezeHashes:
    """Verifies exact physical hashes of all 6 detector model implementations."""
    
    FROZEN_HASHES = {
        "model_phase14.py": ("a268551604ae8b73068435ff10ab3d265065f56e0679757fca5b6bf0f061c065", 23340),
        "model_phase17.py": ("e2b262b866fdd5d7f1a4ab91a7b8b9bac189ee8cc7a78603b3544ca1579fb819", 29067),
        "experiments/phase31/model_phase17_state_reset_candidate.py": ("c144b917b56532787e2a9198f2cad4a77dc2095b57962f31d11d250a4d5d9ea5", 29718),
        "experiments/phase36/model_phase36.py": ("2774ab4cae0fca6d2f3646b443694fefa40d6837ff195f1d216ae7ff7732563a", 13891),
        "experiments/phase36/event_state_machine.py": ("a91e9bc6d0ab9ca805817a406857d31e1f482f7d8815b0eaf7fee9075cd23c31", 24905),
        "experiments/phase36/acoustic_features.py": ("5cc775f97b8e9f2c62018efe6f3fc6d64913cfcb5ffd470a1daba625c6510a51", 9812)
    }

    @pytest.mark.parametrize("rel_path,expected", FROZEN_HASHES.items())
    def test_model_hash_and_size(self, rel_path, expected):
        full_path = REPO_ROOT / rel_path
        assert full_path.exists(), f"Missing file: {rel_path}"
        data = full_path.read_bytes()
        actual_sha = hashlib.sha256(data).hexdigest()
        actual_size = len(data)
        assert actual_sha == expected[0], f"Hash mismatch for {rel_path}"
        assert actual_size == expected[1], f"Size mismatch for {rel_path}"


class TestWorkstream1PositiveRecallAudit:
    """Verifies resolution of Phase 38 vs Phase 39 positive recall discrepancy."""
    
    def test_positive_metric_diff_table(self):
        diff_path = P40_DIR / "phase40_phase38_phase39_metric_diff.csv"
        assert diff_path.exists()
        df = pd.read_csv(diff_path)
        assert len(df) == 6
        
        # Verify COND1
        cond1 = df[df["condition_id"] == "COND1"].iloc[0]
        assert cond1["reproduced_ground_truth_tp"] == 74
        
        # Verify COND2
        cond2 = df[df["condition_id"] == "COND2"].iloc[0]
        assert cond2["reproduced_ground_truth_tp"] == 92
        assert cond2["phase39_reconciliation_printed_tp"] == 81
        assert cond2["phase39_printed_vs_actual_diff"] == -11
        assert "MANUAL_TRANSCRIPTION_ERROR" in cond2["discrepancy_status"]
        
        # Verify COND3
        cond3 = df[df["condition_id"] == "COND3"].iloc[0]
        assert cond3["reproduced_ground_truth_tp"] == 77
        assert cond3["phase39_reconciliation_printed_tp"] == 75
        assert cond3["phase39_printed_vs_actual_diff"] == -2
        assert "MANUAL_TRANSCRIPTION_ERROR" in cond3["discrepancy_status"]

        # Verify COND4-6
        for cid in ["COND4", "COND5", "COND6"]:
            crow = df[df["condition_id"] == cid].iloc[0]
            assert crow["reproduced_ground_truth_tp"] == 77

    def test_clip_level_concordance(self):
        clip_path = P40_DIR / "phase40_clip_level_decision_diff.csv"
        assert clip_path.exists()
        df = pd.read_csv(clip_path)
        assert len(df) == 720  # 120 clips * 6 conditions
        assert all(df["decision_match"] == True)
        assert all(df["alert_count_match"] == True)
        assert all(df["discrepancy_category"] == "IDENTICAL_REPRODUCTION")


class TestWorkstream3SourceIndependence:
    """Verifies source-level independence analysis across evaluation partitions."""
    
    def test_source_lineage_table(self):
        lineage_path = P40_DIR / "phase40_source_lineage.csv"
        assert lineage_path.exists()
        df = pd.read_csv(lineage_path)
        
        pos_row = df[df["partition_name"] == "PARTITION_PROSPECTIVE_POSITIVE"].iloc[0]
        assert pos_row["total_recordings"] == 120
        assert pos_row["unique_uploaders"] == 120
        assert pos_row["recordings_per_uploader_ratio"] == 1.00
        assert pos_row["audit_classification"] == "INDEPENDENT_SOURCES"
        
        fw_row = df[df["partition_name"] == "PARTITION_FIREWORKS_CHALLENGE"].iloc[0]
        assert fw_row["total_recordings"] == 100
        assert fw_row["unique_uploaders"] == 87
        assert fw_row["recordings_per_uploader_ratio"] == 1.15
        assert fw_row["audit_classification"] == "INDEPENDENT_SOURCES"


class TestWorkstream4FireworksPairedAudit:
    """Verifies exact paired statistics for the 100 fireworks challenge clips."""
    
    def test_fireworks_pairwise_audit_contingency(self):
        fw_path = P40_DIR / "phase40_fireworks_pairwise_audit.csv"
        assert fw_path.exists()
        df = pd.read_csv(fw_path)
        assert len(df) == 100
        
        both = sum(df["pair_status"] == "BOTH_TRIGGERED")
        p36_only = sum(df["pair_status"] == "PHASE36_ONLY")
        p14_only = sum(df["pair_status"] == "PHASE14_ONLY")
        neither = sum(df["pair_status"] == "NEITHER_TRIGGERED")
        
        assert both == 47, f"Expected 47 both, got {both}"
        assert p36_only == 10, f"Expected 10 Phase 36 only, got {p36_only}"
        assert p14_only == 0, f"Expected 0 Phase 14 only, got {p14_only}"
        assert neither == 43, f"Expected 43 neither, got {neither}"

    def test_mcnemar_and_exact_binomial_significance(self):
        b = 10
        c = 0
        disc = b + c
        mcnemar_chi2 = ((abs(b - c) - 1.0) ** 2) / float(disc)
        mcnemar_p = float(stats.chi2.sf(mcnemar_chi2, df=1))
        
        assert round(mcnemar_chi2, 4) == 8.1000
        assert round(mcnemar_p, 4) == 0.0044
        
        exact_p = float(stats.binomtest(b, n=disc, p=0.5, alternative="two-sided").pvalue)
        assert round(exact_p, 5) == 0.00195


class TestWorkstream5and6ContinuousEvaluation:
    """Verifies continuous ambient exposure expansion and six-condition results."""
    
    def test_continuous_registry_integrity(self):
        reg_path = P40_DIR / "dataset" / "phase40_continuous_dataset_registry.csv"
        assert reg_path.exists()
        df = pd.read_csv(reg_path)
        assert len(df) == 28, f"Expected 28 continuous streams, got {len(df)}"
        tot_dur_hr = df["duration_seconds"].sum() / 3600.0
        assert round(tot_dur_hr, 4) == 4.2182

    def test_continuous_overlap_zero_collision(self):
        overlap_path = P40_DIR / "dataset" / "phase40_continuous_overlap_audit.csv"
        assert overlap_path.exists()
        df = pd.read_csv(overlap_path)
        assert len(df) == 28
        assert sum(df["historical_sha_match"]) == 0
        assert all(df["overlap_status"] == "VERIFIED_GENUINELY_NEW")

    def test_continuous_results_consistency(self):
        res_path = P40_DIR / "phase40_continuous_results.csv"
        assert res_path.exists()
        df = pd.read_csv(res_path)
        assert len(df) == 6
        
        cond1 = df[df["condition_id"] == "COND1"].iloc[0]
        assert cond1["total_false_alerts"] == 31
        assert round(float(cond1["gross_far_per_hour"]), 4) == 7.3491
        
        cond2 = df[df["condition_id"] == "COND2"].iloc[0]
        assert cond2["total_false_alerts"] == 104
        assert round(float(cond2["gross_far_per_hour"]), 4) == 24.6549
        assert round(float(cond2["convention_b_excluded_seconds"]), 2) == 3440.0
        
        cond6 = df[df["condition_id"] == "COND6"].iloc[0]
        assert cond6["total_false_alerts"] == 26
        assert round(float(cond6["gross_far_per_hour"]), 4) == 6.1637
        assert round(float(cond6["convention_b_excluded_seconds"]), 2) == 107.20


class TestPhase40ReleaseArchive:
    """Verifies physical release zip archive integrity without self-referential hash dependency."""
    
    def test_release_archive_physical_integrity(self):
        zip_path = pathlib.Path("E:/gunshot/gunshot_detection_phase40_audit.zip")
        assert zip_path.exists(), "gunshot_detection_phase40_audit.zip missing!"
        size = zip_path.stat().st_size
        assert size > 50000, f"Archive size too small: {size} bytes"
        
        with zipfile.ZipFile(zip_path, "r") as z:
            crc_bad = z.testzip()
            assert crc_bad is None, f"ZIP CRC error on {crc_bad}"
            files = z.namelist()
            assert len(files) == 31, f"Expected 31 files in archive, found {len(files)}"
