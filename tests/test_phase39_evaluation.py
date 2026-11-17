"""
Phase 39 Automated Forensic Audit & Prospective Evaluation Test Suite
MANDATORY SAFETY DESIGNATION:
RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY
"""

import json
import csv
import zipfile
import hashlib
import pathlib
import pytest
import pandas as pd
import numpy as np

REPO_ROOT = pathlib.Path("E:/gunshot/gunshot")
P39_DIR = REPO_ROOT / "experiments" / "phase39"


# -----------------------------------------------------------------------------
# 1. Frozen Detector Integrity
# -----------------------------------------------------------------------------
def test_frozen_detector_integrity():
    manifest_path = P39_DIR / "phase39_detector_freeze_manifest.json"
    assert manifest_path.exists(), "Detector freeze manifest missing"
    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    # Expected historical hashes
    expected_hashes = {
        "model_phase14.py": "a268551604ae8b73068435ff10ab3d265065f56e0679757fca5b6bf0f061c065",
        "model_phase17.py": "e2b262b866fdd5d7f1a4ab91a7b8b9bac189ee8cc7a78603b3544ca1579fb819",
        "model_phase17_state_reset_candidate.py": "c144b917b56532787e2a9198f2cad4a77dc2095b57962f31d11d250a4d5d9ea5",
        "model_phase36.py": "2774ab4cae0fca6d2f3646b443694fefa40d6837ff195f1d216ae7ff7732563a"
    }

    for name, exp_sha in expected_hashes.items():
        assert name in manifest["artifacts"], f"{name} not in manifest"
        assert manifest["artifacts"][name]["sha256"] == exp_sha, f"Hash mismatch for {name}"
        # Verify physical file on disk matches
        fpath = REPO_ROOT / manifest["artifacts"][name]["relative_path"]
        assert fpath.exists(), f"Physical file {fpath} missing"
        actual_sha = hashlib.sha256(fpath.read_bytes()).hexdigest()
        assert actual_sha == exp_sha, f"Physical file {name} altered!"


# -----------------------------------------------------------------------------
# 2. Historical Hash & Archive Reconciliation
# -----------------------------------------------------------------------------
def test_historical_hash_reconciliation():
    csv_path = P39_DIR / "phase39_hash_reconciliation.csv"
    assert csv_path.exists(), "phase39_hash_reconciliation.csv missing"
    df = pd.read_csv(csv_path)
    assert len(df) == 4, f"Expected 4 source files reconciled, found {len(df)}"
    for _, row in df.iterrows():
        assert row["physical_version_status"] == "IDENTICAL_FROZEN_VERSION"
        assert "PHYSICAL_FILE_VERIFIED" in row["classification"]


def test_historical_archive_reconciliation():
    csv_path = P39_DIR / "phase39_archive_reconciliation.csv"
    assert csv_path.exists(), "phase39_archive_reconciliation.csv missing"
    df = pd.read_csv(csv_path)
    assert len(df) == 5, f"Expected 5 archives reconciled, found {len(df)}"
    for _, row in df.iterrows():
        assert row["zip_crc_status"] == "PASS"
        assert row["physical_size_bytes"] == row["expected_manifest_size"]
        assert row["physical_sha256"] == row["expected_manifest_sha256"]


# -----------------------------------------------------------------------------
# 3. Protocol Pre-Execution Freeze
# -----------------------------------------------------------------------------
def test_evaluation_protocol_freeze():
    proto_path = P39_DIR / "phase39_evaluation_protocol.md"
    assert proto_path.exists(), "phase39_evaluation_protocol.md missing"
    sha = hashlib.sha256(proto_path.read_bytes()).hexdigest()
    assert sha == "726d0231d429acfa370ebdf740c1213d59cd720f81df6d2fd9788a1514fbb736"


# -----------------------------------------------------------------------------
# 4. Positive Annotation Validity Audit
# -----------------------------------------------------------------------------
def test_positive_annotation_validity():
    csv_path = P39_DIR / "phase39_positive_annotation_audit.csv"
    assert csv_path.exists(), "phase39_positive_annotation_audit.csv missing"
    df = pd.read_csv(csv_path)
    assert len(df) == 120, f"Expected 120 clips audited, found {len(df)}"
    # All must have clip-level label only, 0 with human-annotated onset
    assert (df["clip_level_label_present"] == True).all()
    assert (df["human_annotated_event_onset"] == "NONE").all()
    assert (df["evaluation_validity_classification"] == "CLIP_LEVEL_DETECTION").all()


# -----------------------------------------------------------------------------
# 5. Continuous Dataset Registry & Real Duration Disclosure
# -----------------------------------------------------------------------------
def test_continuous_dataset_registry_and_duration():
    csv_path = P39_DIR / "dataset" / "phase39_continuous_dataset_registry.csv"
    assert csv_path.exists(), "Continuous dataset registry missing"
    df = pd.read_csv(csv_path)
    assert len(df) == 16, f"Expected 16 streams, found {len(df)}"
    total_dur_s = df["duration_seconds"].sum()
    total_dur_hr = total_dur_s / 3600.0
    # Must be > 3.0 hours but honestly discloses < 20 hours
    assert 3.10 <= total_dur_hr <= 3.20, f"Unexpected continuous duration: {total_dur_hr} hr"
    assert total_dur_hr < 20.0, "Did not disclose real duration limitation"


# -----------------------------------------------------------------------------
# 6. Cryptographic Audio Overlap Audit
# -----------------------------------------------------------------------------
def test_zero_historical_audio_overlap():
    csv_path = P39_DIR / "dataset" / "phase39_audio_overlap_audit.csv"
    assert csv_path.exists(), "Audio overlap audit CSV missing"
    df = pd.read_csv(csv_path)
    assert len(df) == 236, f"Expected 236 audited files, found {len(df)}"
    # Zero overlap
    assert (df["overlap_status"] == "VERIFIED_GENUINELY_NEW").all()


# -----------------------------------------------------------------------------
# 7. Distractor Registry & Fireworks Count
# -----------------------------------------------------------------------------
def test_expanded_distractor_registry():
    csv_path = P39_DIR / "dataset" / "phase39_distractor_registry.csv"
    assert csv_path.exists(), "Distractor registry missing"
    df = pd.read_csv(csv_path)
    assert len(df) == 220, f"Expected 220 distractor clips, found {len(df)}"
    fw_count = (df["category"] == "DISTRACTOR_FIREWORKS").sum()
    assert fw_count == 100, f"Expected 100 fireworks clips, found {fw_count}"
    assert df["category"].nunique() == 7


# -----------------------------------------------------------------------------
# 8. Duplicate Alert Rate Arithmetic
# -----------------------------------------------------------------------------
def test_duplicate_alert_rate_arithmetic():
    pos_path = P39_DIR / "phase39_positive_results.csv"
    assert pos_path.exists(), "Positive results CSV missing"
    df = pd.read_csv(pos_path)
    
    # Phase 14
    p14 = df[df["condition_id"] == "COND1"].iloc[0]
    expected_p14_dup = round(28 / (74 + 28), 4) # 0.2745
    assert float(p14["duplicate_alert_rate"]) == expected_p14_dup

    # Phase 36
    p36 = df[df["condition_id"] == "COND6"].iloc[0]
    expected_p36_dup = round(13 / (77 + 13), 4) # 0.1444
    assert float(p36["duplicate_alert_rate"]) == expected_p36_dup

    # Phase 36 duplicate rate strictly lower than Phase 14
    assert float(p36["duplicate_alert_rate"]) < float(p14["duplicate_alert_rate"])


# -----------------------------------------------------------------------------
# 9. Convention A and B Cooldown Calculations
# -----------------------------------------------------------------------------
def test_convention_ab_monotonicity():
    bg_path = P39_DIR / "phase39_continuous_results.csv"
    assert bg_path.exists(), "Continuous results CSV missing"
    df = pd.read_csv(bg_path)
    for _, row in df.iterrows():
        # Excluded seconds under Conv B >= Conv A
        assert float(row["convention_b_excluded_seconds"]) >= float(row["convention_a_excluded_seconds"])
        # Conv B FAR >= Gross FAR
        assert float(row["convention_b_far_per_hour"]) >= float(row["gross_far_per_hour"])


# -----------------------------------------------------------------------------
# 10. Phase 17 Defect Replication
# -----------------------------------------------------------------------------
def test_phase17_defect_replication():
    bg_path = P39_DIR / "phase39_continuous_results.csv"
    df = pd.read_csv(bg_path)
    p14_far = float(df[df["condition_id"] == "COND1"]["gross_far_per_hour"].iloc[0])
    p17_far = float(df[df["condition_id"] == "COND2"]["gross_far_per_hour"].iloc[0])
    p31_far = float(df[df["condition_id"] == "COND3"]["gross_far_per_hour"].iloc[0])
    # Phase 17 FAR is > 5x elevated due to unconfirmed candidate leakage
    assert p17_far > 5.0 * p14_far
    # Phase 31 state reset restores FAR to Phase 14 baseline
    assert p31_far == pytest.approx(p14_far, abs=0.01)


# -----------------------------------------------------------------------------
# 11. Fireworks McNemar Test Significance
# -----------------------------------------------------------------------------
def test_fireworks_mcnemar_significance():
    fw_report_path = P39_DIR / "phase39_fireworks_error_analysis.md"
    assert fw_report_path.exists(), "phase39_fireworks_error_analysis.md missing"
    txt = fw_report_path.read_text(encoding="utf-8")
    assert "Both Triggered: **47 clips**" in txt
    assert "Triggered by Phase 36 Only: **10 clips**" in txt
    assert "Triggered by Phase 14 Only: **0 clips**" in txt
    assert "Neither Triggered: **43 clips**" in txt
    assert "8.1000" in txt
    assert "0.0044" in txt


# -----------------------------------------------------------------------------
# 12. Final Report Presence and Safety Designation
# -----------------------------------------------------------------------------
def test_final_report_safety_designation():
    report_path = P39_DIR / "phase39_final_report.md"
    assert report_path.exists(), "phase39_final_report.md missing"
    txt = report_path.read_text(encoding="utf-8")
    assert "RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY" in txt
    assert "NOT PROMOTED" in txt


# -----------------------------------------------------------------------------
# 13. Phase 39 Release Archive CRC and Integrity
# -----------------------------------------------------------------------------
def test_phase39_release_archive_integrity():
    archive_path = pathlib.Path("E:/gunshot/gunshot_detection_phase39_evaluation.zip")
    assert archive_path.exists(), "Release archive missing"
    assert archive_path.stat().st_size > 100000, "Archive size unexpectedly small"
    with zipfile.ZipFile(archive_path, "r") as zf:
        bad = zf.testzip()
        assert bad is None, f"Corrupted file in archive: {bad}"
        assert len(zf.namelist()) == 30


