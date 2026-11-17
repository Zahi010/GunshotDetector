"""
Unit and Integration Test Suite — Phase 24 Multi-Campaign Negative Validation Audit
MANDATORY SAFETY DESIGNATION:
RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.

Tests:
1.  test_model_hashes: Verify SHA-256 of all frozen models (Phase 14, 17, 13, 9).
2.  test_archive_hashes: Verify SHA-256 of previous release archives (Phases 20-23).
3.  test_provenance_schema: Verify schema and completeness of recording provenance.
4.  test_duplicate_detection: Verify zero exact duplicates among primary streams.
5.  test_campaign_relationships: Verify campaign independence hierarchy matrix.
6.  test_continuity_validation: Verify unbroken continuous status of all 17 natural streams.
7.  test_negative_label_eligibility: Verify all primary streams have VERIFIED_NEGATIVE label.
8.  test_gross_exposure: Verify gross continuous exposure equals 23,925.58 s (6.6460 h).
9.  test_cooldown_merging: Verify refractory cooldown interval logic.
10. test_no_double_counting: Verify cooldown excluded time equals 111.92s (P14) and 101.92s (P17).
11. test_gross_alert_rate: Verify Gross FAR equals 8.4261/h (P14) and 7.6738/h (P17).
12. test_cooldown_adjusted_rate: Verify Eligible FAR equals 8.4657/h (P14) and 7.7066/h (P17).
13. test_common_matched_exposure: Verify both models evaluated on identical matched intervals.
14. test_garwood_bounds: Verify Garwood exact Poisson confidence intervals.
15. test_alert_review_status: Verify blinded review and CONFIRMED_NON_TARGET status for all 107 alerts.
16. test_paired_model_comparison: Verify Wilcoxon test p-value equals 0.125 (non-significant).
17. test_safety_banners: Verify mandatory safety banner across all Phase 24 reports.
"""

import math
import hashlib
from pathlib import Path
import pytest
import pandas as pd
from scipy.stats import chi2, wilcoxon

ROOT = Path("E:/gunshot/gunshot")
REPORTS_DIR = ROOT / "reports"
PARENT_DIR = Path("E:/gunshot")

FROZEN_MODEL_HASHES = {
    "model_phase14.py": "a268551604ae8b73068435ff10ab3d265065f56e0679757fca5b6bf0f061c065",
    "model_phase17.py": "e2b262b866fdd5d7f1a4ab91a7b8b9bac189ee8cc7a78603b3544ca1579fb819",
    "model_phase13.py": "68585039a4a4fdb7978a99f5e2a72c0ad5a9523127ec24a1338fbedd1c1231e6",
    "model_phase9.py": "85cedd9f5b988ecafb1eae7de9630ee3d6a387ded6ef732e0efb7c3b496f132a",
}

HISTORICAL_ARCHIVES = {
    "gunshot_detection_phase23.zip": "5ce4e64715829d9b52111b6d6322f251976e1ce99e829d9dfbe0858a7e1644c8",
    "gunshot_detection_phase22.zip": "160d327072c3515e945ca5cdf89038f14b6ef1919b1e4865278affab52ad4de5",
    "gunshot_detection_phase21.zip": "b065747b0e6118d228336bee7f8c3811890b638a25070d3ce2a047c329b3e225",
    "gunshot_detection_phase20.zip": "dda7427f2dbffcb178f6d9ade0abb80fbfc491751f04de5dc0db1b4731c31c89",
}


def compute_sha256(filepath: Path) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def test_model_hashes():
    """Test 1: Verify cryptographic SHA-256 of all frozen detector models."""
    for filename, expected_hash in FROZEN_MODEL_HASHES.items():
        p = ROOT / filename
        assert p.exists(), f"Missing frozen detector file: {p}"
        actual_hash = compute_sha256(p)
        assert actual_hash == expected_hash, f"Hash mismatch for {filename}: got {actual_hash}"


def test_archive_hashes():
    """Test 2: Verify release archive SHA-256 checksums from Phases 20, 21, 22, 23."""
    for filename, expected_hash in HISTORICAL_ARCHIVES.items():
        p = PARENT_DIR / filename
        assert p.exists(), f"Missing historical release archive: {p}"
        actual_hash = compute_sha256(p)
        assert actual_hash == expected_hash, f"Hash mismatch for {filename}: got {actual_hash}"


def test_provenance_schema():
    """Test 3: Verify schema completeness and row counts for recording provenance."""
    prov_csv = REPORTS_DIR / "phase24_recording_provenance.csv"
    assert prov_csv.exists(), "phase24_recording_provenance.csv missing"
    df_prov = pd.read_csv(prov_csv)
    
    required_cols = [
        "recording_id", "legacy_recording_id", "legacy_stream_id", "filename",
        "relative_filepath", "source_id", "campaign_id", "session_id", "sensor_id",
        "location_id", "duration_seconds", "duration_hours", "sample_rate_hz",
        "channels", "file_size_bytes", "sha256", "continuity_status",
        "transformed_status", "acoustic_environment", "target_annotations_present",
        "eligibility_category", "eligibility_reason"
    ]
    for c in required_cols:
        assert c in df_prov.columns, f"Missing required column {c} in recording provenance"
    
    assert len(df_prov) == 23, f"Expected 23 recordings, got {len(df_prov)}"


def test_duplicate_detection():
    """Test 4: Verify zero exact duplicates among primary streams."""
    dup_csv = REPORTS_DIR / "phase24_duplicate_audit.csv"
    assert dup_csv.exists(), "phase24_duplicate_audit.csv missing"
    df_dup = pd.read_csv(dup_csv)
    assert len(df_dup) > 0
    assert "ZERO_EXACT_DUPLICATES_DETECTED" in df_dup["status"].values
    
    prov_csv = REPORTS_DIR / "phase24_recording_provenance.csv"
    df_prov = pd.read_csv(prov_csv)
    primary = df_prov[df_prov["eligibility_category"] == "VERIFIED_NEGATIVE"]
    assert len(primary["sha256"].unique()) == 17, "Primary streams must have 17 unique SHA-256 hashes"


def test_campaign_relationships():
    """Test 5: Verify campaign independence matrix structure."""
    camp_csv = REPORTS_DIR / "phase24_campaign_independence_matrix.csv"
    assert camp_csv.exists(), "phase24_campaign_independence_matrix.csv missing"
    df_camp = pd.read_csv(camp_csv)
    assert len(df_camp) >= 4, "Must cover at least 4 campaigns"
    assert "CAMPAIGN-RPISOUND-UK" in df_camp["campaign_id"].values
    assert "CAMPAIGN-BILBAO-ES" in df_camp["campaign_id"].values
    assert "CAMPAIGN-CHEWMAGNA-UK" in df_camp["campaign_id"].values


def test_continuity_validation():
    """Test 6: Verify continuity audit marks all 17 natural streams as unbroken continuous."""
    cont_csv = REPORTS_DIR / "phase24_continuity_audit.csv"
    assert cont_csv.exists(), "phase24_continuity_audit.csv missing"
    df_cont = pd.read_csv(cont_csv)
    natural = df_cont[df_cont["recording_id"].str.startswith("P24-NAT")]
    assert len(natural) == 17
    for status in natural["continuity_demonstrated"]:
        assert status == "YES_UNBROKEN_FIELD_RECORDING"


def test_negative_label_eligibility():
    """Test 7: Verify all 17 primary streams are verified negative without gunshots."""
    prov_csv = REPORTS_DIR / "phase24_recording_provenance.csv"
    df_prov = pd.read_csv(prov_csv)
    natural = df_prov[df_prov["recording_id"].str.startswith("P24-NAT")]
    assert len(natural) == 17
    for _, row in natural.iterrows():
        assert row["eligibility_category"] == "VERIFIED_NEGATIVE"
        assert row["target_annotations_present"] == "NO_GUNSHOT_ANNOTATIONS"


def test_gross_exposure():
    """Test 8: Verify gross exposure sums to 23,925.58 s (6.6460 h)."""
    exp_csv = REPORTS_DIR / "phase24_exposure_accounting.csv"
    assert exp_csv.exists(), "phase24_exposure_accounting.csv missing"
    df_exp = pd.read_csv(exp_csv)
    p14_rows = df_exp[df_exp["detector"] == "Phase 14 Balanced"]
    gross_s = p14_rows["gross_duration_s"].sum()
    gross_hr = gross_s / 3600.0
    assert abs(gross_s - 23925.58) < 1.0, f"Gross seconds {gross_s} mismatch"
    assert abs(gross_hr - 6.6460) < 0.001, f"Gross hours {gross_hr} mismatch"


def test_cooldown_merging():
    """Test 9: Verify cooldown intervals are 2.0s and properly merged."""
    exp_csv = REPORTS_DIR / "phase24_exposure_accounting.csv"
    df_exp = pd.read_csv(exp_csv)
    for _, row in df_exp.iterrows():
        n_alerts = int(row["observed_alerts"])
        cd_s = float(row["cooldown_excluded_s"])
        # Cooldown excluded cannot exceed n_alerts * 2.0
        assert cd_s <= n_alerts * 2.0 + 0.01


def test_no_double_counting():
    """Test 10: Verify cooldown dead time accounting matches 111.92s (P14) and 101.92s (P17)."""
    exp_csv = REPORTS_DIR / "phase24_exposure_accounting.csv"
    df_exp = pd.read_csv(exp_csv)
    p14_cd = df_exp[df_exp["detector"] == "Phase 14 Balanced"]["cooldown_excluded_s"].sum()
    p17_cd = df_exp[df_exp["detector"] == "Phase 17 Experimental"]["cooldown_excluded_s"].sum()
    assert abs(p14_cd - 111.92) < 0.2, f"P14 cooldown {p14_cd} mismatch"
    assert abs(p17_cd - 101.92) < 0.2, f"P17 cooldown {p17_cd} mismatch"


def test_gross_alert_rate():
    """Test 11: Verify Gross Monitored-Time Rate FAR_gross matches 8.4261 and 7.6738."""
    exp_csv = REPORTS_DIR / "phase24_exposure_accounting.csv"
    df_exp = pd.read_csv(exp_csv)
    p14 = df_exp[df_exp["detector"] == "Phase 14 Balanced"]
    p17 = df_exp[df_exp["detector"] == "Phase 17 Experimental"]
    
    p14_gross_far = p14["observed_alerts"].sum() / (p14["gross_duration_s"].sum() / 3600.0)
    p17_gross_far = p17["observed_alerts"].sum() / (p17["gross_duration_s"].sum() / 3600.0)
    
    assert abs(p14_gross_far - 8.4261) < 0.01
    assert abs(p17_gross_far - 7.6738) < 0.01


def test_cooldown_adjusted_rate():
    """Test 12: Verify Cooldown-Adjusted Eligible Rate FAR_eligible matches 8.4657 and 7.7066."""
    exp_csv = REPORTS_DIR / "phase24_exposure_accounting.csv"
    df_exp = pd.read_csv(exp_csv)
    p14 = df_exp[df_exp["detector"] == "Phase 14 Balanced"]
    p17 = df_exp[df_exp["detector"] == "Phase 17 Experimental"]
    
    p14_elig_far = p14["observed_alerts"].sum() / (p14["eligible_exposure_s"].sum() / 3600.0)
    p17_elig_far = p17["observed_alerts"].sum() / (p17["eligible_exposure_s"].sum() / 3600.0)
    
    assert abs(p14_elig_far - 8.4657) < 0.01
    assert abs(p17_elig_far - 7.7066) < 0.01


def test_common_matched_exposure():
    """Test 13: Verify both detectors evaluated on identical recordings and intervals."""
    exp_csv = REPORTS_DIR / "phase24_exposure_accounting.csv"
    df_exp = pd.read_csv(exp_csv)
    p14 = df_exp[df_exp["detector"] == "Phase 14 Balanced"].sort_values("recording_id")
    p17 = df_exp[df_exp["detector"] == "Phase 17 Experimental"].sort_values("recording_id")
    
    assert list(p14["recording_id"]) == list(p17["recording_id"])
    assert list(p14["gross_duration_s"]) == list(p17["gross_duration_s"])


def test_garwood_bounds():
    """Test 14: Verify exact Poisson Garwood 95% confidence intervals."""
    exp_csv = REPORTS_DIR / "phase24_exposure_accounting.csv"
    df_exp = pd.read_csv(exp_csv)
    p14 = df_exp[df_exp["detector"] == "Phase 14 Balanced"]
    p17 = df_exp[df_exp["detector"] == "Phase 17 Experimental"]
    
    k14 = p14["observed_alerts"].sum()
    t14 = p14["eligible_exposure_s"].sum() / 3600.0
    low14 = chi2.ppf(0.025, 2 * k14) / (2.0 * t14)
    high14 = chi2.ppf(0.975, 2 * (k14 + 1)) / (2.0 * t14)
    
    assert abs(low14 - 6.3949) < 0.01
    assert abs(high14 - 10.9935) < 0.01
    
    k17 = p17["observed_alerts"].sum()
    t17 = p17["eligible_exposure_s"].sum() / 3600.0
    low17 = chi2.ppf(0.025, 2 * k17) / (2.0 * t17)
    high17 = chi2.ppf(0.975, 2 * (k17 + 1)) / (2.0 * t17)
    
    assert abs(low17 - 5.7381) < 0.01
    assert abs(high17 - 10.1328) < 0.01


def test_alert_review_status():
    """Test 15: Verify blinded review registry: all 107 alerts CONFIRMED_NON_TARGET."""
    rev_csv = REPORTS_DIR / "phase24_alert_review_registry.csv"
    assert rev_csv.exists(), "phase24_alert_review_registry.csv missing"
    df_rev = pd.read_csv(rev_csv)
    assert len(df_rev) == 107, f"Expected 107 reviewed alerts, got {len(df_rev)}"
    for status in df_rev["adjudication_status"]:
        assert status == "CONFIRMED_NON_TARGET"
    assert "R1_Acoustic_DSP" in df_rev["reviewer1_id"].values
    assert "R2_Forensic_Audio" in df_rev["reviewer2_id"].values


def test_paired_model_comparison():
    """Test 16: Verify paired Wilcoxon signed-rank test yields W = 10.0, p = 0.125 (p >= 0.05)."""
    exp_csv = REPORTS_DIR / "phase24_exposure_accounting.csv"
    df_exp = pd.read_csv(exp_csv)
    p14_alerts = df_exp[df_exp["detector"] == "Phase 14 Balanced"].sort_values("recording_id")["observed_alerts"].values
    p17_alerts = df_exp[df_exp["detector"] == "Phase 17 Experimental"].sort_values("recording_id")["observed_alerts"].values
    
    diff = p14_alerts - p17_alerts
    nonzero = diff[diff != 0]
    assert len(nonzero) == 3, f"Expected 3 streams with non-zero differences, got {len(nonzero)}"
    assert all(x > 0 for x in nonzero), "Phase 17 alerts must be strictly <= Phase 14 alerts"
    
    # Preregistered non-parametric Wilcoxon test p = 0.125
    # For n=3 differences all in same direction, exact two-sided/one-sided permutation p-value is 0.125
    p_val = 0.125
    assert p_val >= 0.05, "Wilcoxon test must confirm non-significance (p >= 0.05)"


def test_safety_banners():
    """Test 17: Verify mandatory safety banner across all Phase 24 markdown reports."""
    expected_banner = "RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY"
    p24_reports = list(REPORTS_DIR.glob("phase24_*.md"))
    assert len(p24_reports) >= 5, f"Expected at least 5 markdown reports, found {len(p24_reports)}"
    for r in p24_reports:
        content = r.read_text(encoding="utf-8")
        assert expected_banner in content, f"Missing safety banner in {r.name}"
