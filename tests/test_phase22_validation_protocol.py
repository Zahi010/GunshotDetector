"""
Unit and Integration Test Suite — Phase 22 Validation Protocol & Forensics
MANDATORY SAFETY DESIGNATION:
RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.

Tests:
1. Frozen baseline checksums and integrity.
2. Burst-cooldown forensic classifications across all 50 Category A rounds.
3. Alert timeline intervals, ordering, and cooldown non-negativity.
4. Dataset provenance schema compliance.
5. Poisson exposure and confidence bound calculations.
6. Model promotion decision logic.
7. Mandatory safety designations across all Phase 22 documentation.
"""

import json
import hashlib
import math
import pytest
import pandas as pd
from pathlib import Path
from scipy.stats import chi2

ROOT = Path("E:/gunshot/gunshot")
REPORTS_DIR = ROOT / "reports"

FROZEN_HASHES = {
    "model_phase14.py": "a268551604ae8b73068435ff10ab3d265065f56e0679757fca5b6bf0f061c065",
    "model_phase17.py": "e2b262b866fdd5d7f1a4ab91a7b8b9bac189ee8cc7a78603b3544ca1579fb819",
    "model_phase13.py": "68585039a4a4fdb7978a99f5e2a72c0ad5a9523127ec24a1338fbedd1c1231e6",
    "model_phase9.py": "85cedd9f5b988ecafb1eae7de9630ee3d6a387ded6ef732e0efb7c3b496f132a",
    "reports/phase20_canonical_event_manifest.csv": "6c3e5d5c07cb5102ee7160c0272e90d5c98cdb4659538ee58ad276855d971691",
}

VALID_CATEGORIES = {
    "DETECTED_WITH_INDEPENDENT_ALERT",
    "DETECTED_BUT_MERGED_INTO_EARLIER_ALERT",
    "MISSED_WHILE_IN_REFRACTORY_COOLDOWN",
    "MISSED_WHILE_ELIGIBLE",
    "AMBIGUOUS_DUE_TO_INSUFFICIENT_PRECISION",
}


def compute_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def test_baseline_hashes():
    """Verify that all core detector scripts match immutable cryptographic checksums."""
    for rel_path, expected_hash in FROZEN_HASHES.items():
        file_path = ROOT / rel_path
        assert file_path.exists(), f"Missing required frozen file: {file_path}"
        actual_hash = compute_sha256(file_path)
        assert actual_hash == expected_hash, f"Hash mismatch for {rel_path}: got {actual_hash}, expected {expected_hash}"


def test_historical_archive_hashes():
    """Verify Phase 20 and Phase 21 historical zip archives."""
    p20_zip = Path("E:/gunshot/gunshot_detection_phase20.zip")
    p21_zip = Path("E:/gunshot/gunshot_detection_phase21.zip")
    assert p20_zip.exists(), "Phase 20 archive missing"
    assert p21_zip.exists(), "Phase 21 archive missing"
    assert compute_sha256(p20_zip) == "dda7427f2dbffcb178f6d9ade0abb80fbfc491751f04de5dc0db1b4731c31c89"
    assert compute_sha256(p21_zip) == "b065747b0e6118d228336bee7f8c3811890b638a25070d3ce2a047c329b3e225"


def test_burst_cooldown_forensics_counts():
    """Verify forensic classifications of all 50 physical rounds in Category A."""
    csv_path = REPORTS_DIR / "phase22_burst_cooldown_forensics.csv"
    assert csv_path.exists(), "phase22_burst_cooldown_forensics.csv missing"
    df = pd.read_csv(csv_path)
    assert len(df) == 50, f"Expected 50 physical rounds, got {len(df)}"

    # Check category validity
    for cat in df["phase_14_balanced_forensic_category"]:
        assert cat in VALID_CATEGORIES, f"Invalid p14 category: {cat}"
    for cat in df["phase_17_experimental_forensic_category"]:
        assert cat in VALID_CATEGORIES, f"Invalid p17 category: {cat}"

    # Verify exact forensic counts
    p14_counts = df["phase_14_balanced_forensic_category"].value_counts().to_dict()
    assert p14_counts.get("DETECTED_WITH_INDEPENDENT_ALERT", 0) == 27
    assert p14_counts.get("DETECTED_BUT_MERGED_INTO_EARLIER_ALERT", 0) == 5
    assert p14_counts.get("MISSED_WHILE_IN_REFRACTORY_COOLDOWN", 0) == 2
    assert p14_counts.get("MISSED_WHILE_ELIGIBLE", 0) == 16
    assert p14_counts.get("AMBIGUOUS_DUE_TO_INSUFFICIENT_PRECISION", 0) == 0

    p17_counts = df["phase_17_experimental_forensic_category"].value_counts().to_dict()
    assert p17_counts.get("DETECTED_WITH_INDEPENDENT_ALERT", 0) == 33
    assert p17_counts.get("DETECTED_BUT_MERGED_INTO_EARLIER_ALERT", 0) == 6
    assert p17_counts.get("MISSED_WHILE_IN_REFRACTORY_COOLDOWN", 0) == 3
    assert p17_counts.get("MISSED_WHILE_ELIGIBLE", 0) == 8
    assert p17_counts.get("AMBIGUOUS_DUE_TO_INSUFFICIENT_PRECISION", 0) == 0


def test_alert_event_timeline():
    """Verify timing consistency, cooldown bounds, and non-negativity."""
    timeline_path = REPORTS_DIR / "phase22_alert_event_timeline.csv"
    assert timeline_path.exists(), "phase22_alert_event_timeline.csv missing"
    df = pd.read_csv(timeline_path)
    assert len(df) > 0

    required_cols = [
        "stream_id", "model_name", "alert_index", "alert_start_s", "alert_end_s",
        "alert_duration_s", "peak_time_s", "peak_score", "cooldown_start_s", "cooldown_end_s", "cooldown_duration_s"
    ]
    for col in required_cols:
        assert col in df.columns, f"Missing column {col} in alert timeline"

    for _, row in df.iterrows():
        assert row["alert_start_s"] <= row["alert_end_s"], f"Invalid alert duration: {row}"
        assert row["cooldown_start_s"] <= row["cooldown_end_s"], f"Invalid cooldown bounds: {row}"
        assert abs((row["cooldown_end_s"] - row["cooldown_start_s"]) - 2.0) < 1e-4, f"Cooldown must be 2.0s: {row}"
        assert row["peak_score"] >= 0.0, f"Negative score: {row}"


def test_provenance_schema():
    """Verify dataset provenance schema JSON format and required structure."""
    schema_path = REPORTS_DIR / "phase22_dataset_provenance_schema.json"
    assert schema_path.exists(), "phase22_dataset_provenance_schema.json missing"
    with open(schema_path, "r", encoding="utf-8") as f:
        schema = json.load(f)
    assert schema.get("$schema") == "https://json-schema.org/draft/2020-12/schema"
    assert "campaign_metadata" in schema.get("properties", {})
    assert "source_recording_metadata" in schema.get("properties", {})
    assert "legal_and_compliance" in schema.get("properties", {})


def test_poisson_garwood_formula():
    """Verify that exact Poisson Garwood formula yields ~0.02996 upper bound for 0 alerts in 100 hours."""
    k = 0
    exposure_hr = 100.0
    alpha = 0.05
    # One-sided 95% upper bound for k=0: chi2.ppf(1 - alpha, 2*(k+1)) / (2 * exposure_hr)
    chi2_val = chi2.ppf(1.0 - alpha, 2 * (k + 1))
    lambda_upper = chi2_val / (2.0 * exposure_hr)
    expected_upper = -math.log(0.05) / 100.0  # 2.99573 / 100 = 0.029957
    assert abs(lambda_upper - expected_upper) < 1e-4
    assert abs(lambda_upper - 0.02996) < 1e-4


def test_eligible_exposure_calculation():
    """Verify math for gross vs eligible exposure calculation."""
    gross_seconds = 3600.0  # 1 hour
    cooldowns = [2.0, 2.0, 2.0]  # 3 alerts
    excluded_seconds = 10.0
    eligible_seconds = gross_seconds - sum(cooldowns) - excluded_seconds
    assert eligible_seconds == 3584.0
    assert eligible_seconds < gross_seconds


def test_model_promotion_decision_logic():
    """Verify decision rules for PROMOTE, RETAIN DEFAULT, and INCONCLUSIVE."""
    def evaluate_promotion(campaigns_won, total_campaigns, wilcoxon_p, holm_bonferroni_sig, far_delta):
        if far_delta > 0.50:
            return "RETAIN DEFAULT"
        if campaigns_won >= 2 and total_campaigns >= 3 and wilcoxon_p < 0.05 and holm_bonferroni_sig and far_delta <= 0.20:
            return "PROMOTE"
        return "INCONCLUSIVE"

    # Perfect promotion case
    assert evaluate_promotion(2, 3, 0.01, True, 0.05) == "PROMOTE"
    # Fails campaign count (only 1 won)
    assert evaluate_promotion(1, 3, 0.01, True, 0.05) == "INCONCLUSIVE"
    # Fails Wilcoxon recording-level test
    assert evaluate_promotion(2, 3, 0.08, True, 0.05) == "INCONCLUSIVE"
    # Severe FAR degradation
    assert evaluate_promotion(3, 3, 0.001, True, 0.60) == "RETAIN DEFAULT"


def test_safety_designation_in_reports():
    """Verify that all Phase 22 markdown documents contain the mandatory safety designation."""
    md_files = [
        "phase22_final_report.md",
        "phase22_burst_cooldown_analysis.md",
        "phase22_independent_validation_protocol.md",
        "phase22_preregistered_analysis_plan.md",
        "phase22_negative_audio_protocol.md",
        "phase22_model_promotion_criteria.md",
        "phase22_dataset_acquisition_plan.md",
        "phase22_risk_and_limitation_register.md",
    ]
    mandatory_banner = "RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY."
    for fname in md_files:
        fpath = REPORTS_DIR / fname
        assert fpath.exists(), f"Report file missing: {fname}"
        content = fpath.read_text(encoding="utf-8")
        assert mandatory_banner in content, f"Mandatory safety designation missing in {fname}"


if __name__ == "__main__":
    pytest.main(["-v", __file__])
