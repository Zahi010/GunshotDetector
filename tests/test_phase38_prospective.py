"""
Phase 38 Comprehensive Prospective Holdout Evaluation Audit Suite
MANDATORY SAFETY DESIGNATION:
RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY
"""

import hashlib
import json
import pathlib
import zipfile
import pytest
import pandas as pd

REPO_ROOT = pathlib.Path("E:/gunshot/gunshot")
ROOT = pathlib.Path("E:/gunshot")
P38_DIR = REPO_ROOT / "experiments" / "phase38"
P38_DATA_DIR = P38_DIR / "dataset"
P38_PROV_DIR = P38_DIR / "provenance"

EXPECTED_FROZEN_HASHES = {
    "model_phase14.py": "a268551604ae8b73068435ff10ab3d265065f56e0679757fca5b6bf0f061c065",
    "model_phase17.py": "e2b262b866fdd5d7f1a4ab91a7b8b9bac189ee8cc7a78603b3544ca1579fb819",
    "model_phase17_state_reset_candidate.py": "c144b917b56532787e2a9198f2cad4a77dc2095b57962f31d11d250a4d5d9ea5",
    "feature_extractor.py": "1c665b7c1749de98337da0726627710fffe0dcfa56335291b666ae7abcbae94f",
    "config.py": "55749f9d46d561d131fad374064021b73c08274e2a79954efd08570b029b1858",
    "model_phase36.py": "2774ab4cae0fca6d2f3646b443694fefa40d6837ff195f1d216ae7ff7732563a",
    "event_state_machine.py": "a91e9bc6d0ab9ca805817a406857d31e1f482f7d8815b0eaf7fee9075cd23c31",
    "acoustic_features.py": "5cc775f97b8e9f2c62018efe6f3fc6d64913cfcb5ffd470a1daba625c6510a51",
    "config_phase36.json": "1aaffd5423e116958807372855d989e294d3ff12b614052e10df78346d62e363"
}

EXPECTED_PROTOCOL_HASH = "87e5574b52669017804f5cf3128475d0417cf3cbb24e842455794b47db2e81de"


class TestFrozenAssetIntegrityAndReconciliation:
    def test_frozen_detector_hashes(self):
        paths = {
            "model_phase14.py": REPO_ROOT / "model_phase14.py",
            "model_phase17.py": REPO_ROOT / "model_phase17.py",
            "model_phase17_state_reset_candidate.py": REPO_ROOT / "experiments/phase31/model_phase17_state_reset_candidate.py",
            "feature_extractor.py": REPO_ROOT / "feature_extractor.py",
            "config.py": REPO_ROOT / "config.py",
            "model_phase36.py": REPO_ROOT / "experiments/phase36/model_phase36.py",
            "event_state_machine.py": REPO_ROOT / "experiments/phase36/event_state_machine.py",
            "acoustic_features.py": REPO_ROOT / "experiments/phase36/acoustic_features.py",
            "config_phase36.json": REPO_ROOT / "experiments/phase36/config_phase36.json"
        }
        for name, expected_h in EXPECTED_FROZEN_HASHES.items():
            p = paths[name]
            assert p.exists(), f"File {p} does not exist"
            actual_h = hashlib.sha256(p.read_bytes()).hexdigest()
            assert actual_h == expected_h, f"Hash mismatch for {name}: {actual_h} != {expected_h}"

    def test_protocol_freeze_integrity(self):
        proto_file = P38_DIR / "phase38_evaluation_protocol.md"
        assert proto_file.exists()
        h = hashlib.sha256(proto_file.read_bytes()).hexdigest()
        assert h == EXPECTED_PROTOCOL_HASH, f"Protocol hash modified! {h} != {EXPECTED_PROTOCOL_HASH}"

    def test_provenance_reconciliation_csv(self):
        recon_csv = P38_PROV_DIR / "phase38_frozen_asset_hash_reconciliation.csv"
        assert recon_csv.exists()
        df = pd.read_csv(recon_csv)
        assert len(df) == 13
        assert (df["classification"] == "PHYSICAL_HASH_MATCHES_HISTORICAL_RECORD").all()


class TestDatasetLineageAndIndependence:
    def test_dataset_registry_completeness(self):
        reg_csv = P38_DATA_DIR / "phase38_dataset_registry.csv"
        assert reg_csv.exists()
        df = pd.read_csv(reg_csv)
        assert len(df) == 247
        assert "recording_id" in df.columns
        assert "sha256" in df.columns
        assert "partition" in df.columns
        assert df["recording_id"].nunique() == 247

    def test_license_register_completeness(self):
        lic_csv = P38_DATA_DIR / "phase38_dataset_license_register.csv"
        assert lic_csv.exists()
        df = pd.read_csv(lic_csv)
        assert len(df) >= 4
        assert "license_type" in df.columns
        assert "recordings_count" in df.columns

    def test_historical_overlap_zero_leakage(self):
        overlap_csv = P38_DATA_DIR / "phase38_historical_overlap_audit.csv"
        assert overlap_csv.exists()
        df = pd.read_csv(overlap_csv)
        assert len(df) == 247
        assert (df["audit_classification"] == "VERIFIED_GENUINELY_NEW").all()
        assert (df["matched_historical_path"] == "NONE").all()

    def test_partition_isolation_and_no_leakage(self):
        reg_csv = P38_DATA_DIR / "phase38_dataset_registry.csv"
        df = pd.read_csv(reg_csv)
        pos = df[df["partition"] == "PARTITION_PROSPECTIVE_POSITIVE"]
        dist = df[df["partition"] == "PARTITION_PROSPECTIVE_DISTRACTOR"]
        cont = df[df["partition"] == "PARTITION_PROSPECTIVE_CONTINUOUS"]

        assert len(pos) == 120
        assert len(dist) == 120
        assert len(cont) == 7

        # Check disjoint hashes
        pos_hashes = set(pos["sha256"])
        dist_hashes = set(dist["sha256"])
        cont_hashes = set(cont["sha256"])
        assert len(pos_hashes.intersection(dist_hashes)) == 0
        assert len(pos_hashes.intersection(cont_hashes)) == 0
        assert len(dist_hashes.intersection(cont_hashes)) == 0


class TestEvaluationArithmeticAndMetrics:
    def test_positive_event_matching_arithmetic(self):
        pos_csv = P38_DIR / "phase38_positive_event_results.csv"
        assert pos_csv.exists()
        df = pd.read_csv(pos_csv)
        assert len(df) == 6
        for idx, row in df.iterrows():
            tp = row["strict_matched_true_positives"]
            fn = row["false_negatives"]
            total = row["annotated_event_clips"]
            assert tp + fn == total == 120
            rec = row["event_level_recall"]
            assert round(tp / total, 4) == rec
            dups = row["duplicate_alerts_count"]
            dup_rate = row["duplicate_alert_rate"]
            expected_dup_rate = round(dups / (tp + dups), 4) if (tp + dups) > 0 else 0.0
            assert dup_rate == expected_dup_rate

    def test_continuous_background_arithmetic(self):
        bg_csv = P38_DIR / "phase38_background_results.csv"
        assert bg_csv.exists()
        df = pd.read_csv(bg_csv)
        assert len(df) == 6
        for idx, row in df.iterrows():
            dur_hr = row["gross_duration_hours"]
            assert round(dur_hr, 3) == 1.953
            alerts = row["total_false_alerts"]
            gross_far = row["gross_far_per_hour"]
            assert round(alerts / dur_hr, 4) == gross_far
            # Conv B excluded time must be >= Conv A excluded time
            assert row["convention_b_excluded_seconds"] >= row["convention_a_excluded_seconds"]

    def test_convention_ab_phase17_defect(self):
        bg_csv = P38_DIR / "phase38_background_results.csv"
        df = pd.read_csv(bg_csv)
        p14 = df[df["condition_id"] == "COND1"].iloc[0]
        p17_defect = df[df["condition_id"] == "COND2"].iloc[0]
        p36 = df[df["condition_id"] == "COND6"].iloc[0]

        # Phase 17 defective has massive excluded exposure and alert count
        assert p17_defect["total_false_alerts"] > p14["total_false_alerts"]
        assert p17_defect["convention_b_excluded_seconds"] > 500.0
        # Phase 36 has fewer false alerts than Phase 14
        assert p36["total_false_alerts"] <= p14["total_false_alerts"]

    def test_distractor_trigger_rate_consistency(self):
        dist_csv = P38_DIR / "phase38_distractor_results.csv"
        assert dist_csv.exists()
        df = pd.read_csv(dist_csv)
        assert len(df) == 6
        for idx, row in df.iterrows():
            total = row["total_reviewed_clips"]
            assert total == 120
            trig = row["triggered_clips_count"]
            assert round(trig / total, 4) == row["overall_trigger_rate"]

    def test_condition_comparison_table_consistency(self):
        comp_csv = P38_DIR / "phase38_condition_comparison.csv"
        assert comp_csv.exists()
        df = pd.read_csv(comp_csv)
        assert len(df) == 6
        assert "condition_id" in df.columns
        assert "continuous_gross_far" in df.columns
        assert "positive_event_recall" in df.columns
        assert "distractor_trigger_rate" in df.columns


class TestReleaseArchiveIntegrity:
    def test_phase34_and_35_archives_crc(self):
        zip34 = ROOT / "gunshot_detection_phase34.zip"
        zip35 = ROOT / "gunshot_detection_phase35.zip"
        assert zip34.exists()
        assert zip35.exists()
        assert zipfile.ZipFile(zip34).testzip() is None
        assert zipfile.ZipFile(zip35).testzip() is None

    def test_phase38_prospective_archive_crc(self):
        zip38 = ROOT / "gunshot_detection_phase38_prospective_evaluation.zip"
        if zip38.exists():
            with zipfile.ZipFile(zip38, "r") as zf:
                bad = zf.testzip()
                assert bad is None
