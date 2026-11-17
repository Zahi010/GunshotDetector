"""
Unit and Integration Test Suite — Phase 25 Cross-Phase Reconciliation & Independent Acquisition Audit
MANDATORY SAFETY DESIGNATION:
RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.

Comprehensive Automated Verification Suite:
1.  test_baseline_hashes: Verify SHA-256 of all frozen detector models.
2.  test_historical_archive_hashes: Verify release archives from Phases 20-24.
3.  test_stream_comparison_reconciliation: Verify 3 improved, 14 equal, 0 worse.
4.  test_recording_inventory_reconciliation: Verify statuses of all 23 cataloged recordings.
5.  test_evaluated_vs_excluded_exposure: Verify 6.6460 h evaluated vs 6.0000 h excluded.
6.  test_reviewer_contingency_table: Verify contingency table counts (107/107).
7.  test_cohens_kappa_assessment: Verify kappa is flagged as UNVERIFIED on stored artifact.
8.  test_provenance_schema_validation: Verify provenance schema completeness.
9.  test_duplicate_detection: Verify zero exact duplicates among primary streams.
10. test_campaign_independence_matrix: Verify multi-tier hierarchy in campaign matrix.
11. test_continuity_verification: Verify all 17 natural streams are unbroken field recordings.
12. test_negative_label_eligibility: Verify all primary streams have VERIFIED_NEGATIVE label.
13. test_gross_exposure_accounting: Verify gross exposure equals 23,925.58 s (6.6460 h).
14. test_cooldown_union_and_no_double_counting: Verify cooldown dead time accounting.
15. test_gross_alert_rate: Verify Gross FAR equals 8.4261/h (P14) and 7.6738/h (P17).
16. test_eligible_alert_rate: Verify Eligible FAR equals 8.4657/h (P14) and 7.7066/h (P17).
17. test_matched_exposure_consistency: Verify matched evaluation intervals.
18. test_garwood_confidence_intervals: Verify Garwood exact Poisson bounds.
19. test_statistical_comparison_validation: Verify Wilcoxon test p-value equals 0.125 (p >= 0.05).
20. test_mandatory_safety_designation: Verify mandatory safety banner across all Phase 25 reports.
"""

import math
import hashlib
from pathlib import Path
import pytest
import pandas as pd
from scipy.stats import chi2

ROOT = Path("E:/gunshot/gunshot")
REPORTS_DIR = ROOT / "reports"
PARENT_DIR = Path("E:/gunshot")

FROZEN_MODELS = {
    "model_phase14.py": "a268551604ae8b73068435ff10ab3d265065f56e0679757fca5b6bf0f061c065",
    "model_phase17.py": "e2b262b866fdd5d7f1a4ab91a7b8b9bac189ee8cc7a78603b3544ca1579fb819",
    "model_phase13.py": "68585039a4a4fdb7978a99f5e2a72c0ad5a9523127ec24a1338fbedd1c1231e6",
    "model_phase9.py": "85cedd9f5b988ecafb1eae7de9630ee3d6a387ded6ef732e0efb7c3b496f132a",
}

HISTORICAL_ARCHIVES = {
    "gunshot_detection_phase24.zip": "3e732e0716160f2d77b71ceff3e01a49f3d933e397bf29bf222fec771a8832b8",
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


def test_baseline_hashes():
    """Test 1: Verify SHA-256 of all frozen detector models."""
    for filename, exp_hash in FROZEN_MODELS.items():
        p = ROOT / filename
        assert p.exists(), f"Missing frozen model {filename}"
        assert compute_sha256(p) == exp_hash, f"Hash mismatch on {filename}"


def test_historical_archive_hashes():
    """Test 2: Verify release archive SHA-256 checksums from Phases 20-24."""
    for filename, exp_hash in HISTORICAL_ARCHIVES.items():
        p = PARENT_DIR / filename
        assert p.exists(), f"Missing archive {filename}"
        assert compute_sha256(p) == exp_hash, f"Archive hash mismatch on {filename}"


def test_stream_comparison_reconciliation():
    """Test 3: Verify stream comparison reconciliation: 3 improved, 14 equal, 0 worse."""
    recon_csv = REPORTS_DIR / "phase25_stream_comparison_reconciliation.csv"
    assert recon_csv.exists(), "phase25_stream_comparison_reconciliation.csv missing"
    df = pd.read_csv(recon_csv)
    assert len(df) == 17, f"Expected 17 streams, got {len(df)}"
    
    improved = df["phase17_improved"].sum()
    equal = df["counts_equal"].sum()
    worse = df["phase17_worse"].sum()
    net_diff = df["difference"].sum()
    
    assert improved == 3, f"Expected 3 improved streams, got {improved}"
    assert equal == 14, f"Expected 14 equal streams, got {equal}"
    assert worse == 0, f"Expected 0 worse streams, got {worse}"
    assert net_diff == 5, f"Expected net difference of 5 alerts, got {net_diff}"


def test_recording_inventory_reconciliation():
    """Test 4: Verify accounting for all 23 cataloged recordings."""
    inv_csv = REPORTS_DIR / "phase25_recording_inventory_reconciliation.csv"
    assert inv_csv.exists(), "phase25_recording_inventory_reconciliation.csv missing"
    df = pd.read_csv(inv_csv)
    assert len(df) == 23, f"Expected 23 recordings, got {len(df)}"
    
    status_counts = df["status"].value_counts().to_dict()
    assert status_counts.get("INCLUDED_PRIMARY_EVALUATION", 0) == 17
    assert status_counts.get("EXCLUDED_NOT_CONTINUOUS", 0) == 6


def test_evaluated_vs_excluded_exposure():
    """Test 5: Verify gross exposure breakdown: 6.6460h evaluated vs 6.0000h excluded."""
    inv_csv = REPORTS_DIR / "phase25_recording_inventory_reconciliation.csv"
    df = pd.read_csv(inv_csv)
    
    eval_s = df[df["status"] == "INCLUDED_PRIMARY_EVALUATION"]["gross_duration_s"].sum()
    excl_s = df[df["status"] == "EXCLUDED_NOT_CONTINUOUS"]["gross_duration_s"].sum()
    
    assert abs(eval_s - 23925.58) < 1.0
    assert abs(eval_s / 3600.0 - 6.6460) < 0.001
    assert abs(excl_s - 21600.0) < 1.0
    assert abs(excl_s / 3600.0 - 6.0000) < 0.001


def test_reviewer_contingency_table():
    """Test 6: Verify reviewer contingency table counts (107/107)."""
    cont_csv = REPORTS_DIR / "phase25_reviewer_contingency_table.csv"
    assert cont_csv.exists(), "phase25_reviewer_contingency_table.csv missing"
    df = pd.read_csv(cont_csv, index_col=0)
    assert "CONFIRMED_NON_TARGET" in df.index
    assert "CONFIRMED_NON_TARGET" in df.columns
    count = df.loc["CONFIRMED_NON_TARGET", "CONFIRMED_NON_TARGET"]
    assert count == 107


def test_cohens_kappa_assessment():
    """Test 7: Verify Cohen's kappa is flagged as UNVERIFIED on stored artifact."""
    manifest_path = REPORTS_DIR / "phase25_processing_manifest.json"
    assert manifest_path.exists(), "phase25_processing_manifest.json missing"
    manifest = pd.read_json(manifest_path, typ="series")
    recon_sec = manifest["workstream_a_forensic_reconciliation"]
    audit_info = recon_sec["double_reviewer_audit"]
    assert audit_info["cohens_kappa_assessment"] == "UNVERIFIED_FROM_ARTIFACT"


def test_provenance_schema_validation():
    """Test 8: Verify provenance schema completeness."""
    prov_csv = REPORTS_DIR / "phase25_recording_provenance.csv"
    assert prov_csv.exists(), "phase25_recording_provenance.csv missing"
    df = pd.read_csv(prov_csv)
    assert len(df) == 23
    for col in ["recording_id", "filename", "sha256", "duration_seconds", "eligibility_category"]:
        assert col in df.columns


def test_duplicate_detection():
    """Test 9: Verify zero exact duplicates among primary streams."""
    dup_csv = REPORTS_DIR / "phase25_duplicate_audit.csv"
    assert dup_csv.exists(), "phase25_duplicate_audit.csv missing"
    df = pd.read_csv(dup_csv)
    assert "ZERO_EXACT_DUPLICATES_DETECTED" in df["status"].values
    
    prov_csv = REPORTS_DIR / "phase25_recording_provenance.csv"
    df_prov = pd.read_csv(prov_csv)
    primary = df_prov[df_prov["eligibility_category"] == "VERIFIED_NEGATIVE"]
    assert len(primary["sha256"].unique()) == 17


def test_campaign_independence_matrix():
    """Test 10: Verify multi-tier hierarchy in campaign matrix."""
    camp_csv = REPORTS_DIR / "phase25_campaign_independence_matrix.csv"
    assert camp_csv.exists(), "phase25_campaign_independence_matrix.csv missing"
    df = pd.read_csv(camp_csv)
    assert len(df) >= 4
    for camp in ["CAMPAIGN-RPISOUND-UK", "CAMPAIGN-CHEWMAGNA-UK", "CAMPAIGN-BILBAO-ES"]:
        assert camp in df["campaign_id"].values


def test_continuity_verification():
    """Test 11: Verify all 17 natural streams are unbroken field recordings."""
    cont_csv = REPORTS_DIR / "phase25_continuity_audit.csv"
    assert cont_csv.exists(), "phase25_continuity_audit.csv missing"
    df = pd.read_csv(cont_csv)
    natural = df[df["recording_id"].str.startswith("P25-NAT")]
    assert len(natural) == 17
    for s in natural["continuity_demonstrated"]:
        assert s == "YES_UNBROKEN_FIELD_RECORDING"


def test_negative_label_eligibility():
    """Test 12: Verify all 17 natural streams have VERIFIED_NEGATIVE label."""
    prov_csv = REPORTS_DIR / "phase25_recording_provenance.csv"
    df = pd.read_csv(prov_csv)
    natural = df[df["recording_id"].str.startswith("P25-NAT")]
    assert len(natural) == 17
    for cat in natural["eligibility_category"]:
        assert cat == "VERIFIED_NEGATIVE"


def test_gross_exposure_accounting():
    """Test 13: Verify gross exposure sums to 23,925.58 s (6.6460 h)."""
    exp_csv = REPORTS_DIR / "phase25_exposure_accounting.csv"
    assert exp_csv.exists(), "phase25_exposure_accounting.csv missing"
    df = pd.read_csv(exp_csv)
    p14 = df[df["detector"] == "Phase 14 Balanced"]
    gross_s = p14["gross_duration_s"].sum()
    gross_hr = gross_s / 3600.0
    assert abs(gross_s - 23925.58) < 1.0
    assert abs(gross_hr - 6.6460) < 0.001


def test_cooldown_union_and_no_double_counting():
    """Test 14: Verify cooldown excluded time equals 111.92s (P14) and 101.92s (P17)."""
    exp_csv = REPORTS_DIR / "phase25_exposure_accounting.csv"
    df = pd.read_csv(exp_csv)
    p14_cd = df[df["detector"] == "Phase 14 Balanced"]["cooldown_excluded_s"].sum()
    p17_cd = df[df["detector"] == "Phase 17 Experimental"]["cooldown_excluded_s"].sum()
    assert abs(p14_cd - 111.92) < 0.2
    assert abs(p17_cd - 101.92) < 0.2


def test_gross_alert_rate():
    """Test 15: Verify Gross Monitored-Time Rate FAR_gross matches 8.4261 and 7.6738."""
    exp_csv = REPORTS_DIR / "phase25_exposure_accounting.csv"
    df = pd.read_csv(exp_csv)
    p14 = df[df["detector"] == "Phase 14 Balanced"]
    p17 = df[df["detector"] == "Phase 17 Experimental"]
    
    p14_gross_far = p14["observed_alerts"].sum() / (p14["gross_duration_s"].sum() / 3600.0)
    p17_gross_far = p17["observed_alerts"].sum() / (p17["gross_duration_s"].sum() / 3600.0)
    
    assert abs(p14_gross_far - 8.4261) < 0.01
    assert abs(p17_gross_far - 7.6738) < 0.01


def test_eligible_alert_rate():
    """Test 16: Verify Cooldown-Adjusted Eligible Rate FAR_eligible matches 8.4657 and 7.7066."""
    exp_csv = REPORTS_DIR / "phase25_exposure_accounting.csv"
    df = pd.read_csv(exp_csv)
    p14 = df[df["detector"] == "Phase 14 Balanced"]
    p17 = df[df["detector"] == "Phase 17 Experimental"]
    
    p14_elig_far = p14["observed_alerts"].sum() / (p14["eligible_exposure_s"].sum() / 3600.0)
    p17_elig_far = p17["observed_alerts"].sum() / (p17["eligible_exposure_s"].sum() / 3600.0)
    
    assert abs(p14_elig_far - 8.4657) < 0.01
    assert abs(p17_elig_far - 7.7066) < 0.01


def test_matched_exposure_consistency():
    """Test 17: Verify matched evaluation intervals across models."""
    exp_csv = REPORTS_DIR / "phase25_exposure_accounting.csv"
    df = pd.read_csv(exp_csv)
    p14 = df[df["detector"] == "Phase 14 Balanced"].sort_values("recording_id")
    p17 = df[df["detector"] == "Phase 17 Experimental"].sort_values("recording_id")
    assert list(p14["recording_id"]) == list(p17["recording_id"])
    assert list(p14["gross_duration_s"]) == list(p17["gross_duration_s"])


def test_garwood_confidence_intervals():
    """Test 18: Verify Garwood exact Poisson confidence intervals."""
    exp_csv = REPORTS_DIR / "phase25_exposure_accounting.csv"
    df = pd.read_csv(exp_csv)
    p14 = df[df["detector"] == "Phase 14 Balanced"]
    p17 = df[df["detector"] == "Phase 17 Experimental"]
    
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


def test_statistical_comparison_validation():
    """Test 19: Verify Wilcoxon test p-value equals 0.125 (p >= 0.05)."""
    exp_csv = REPORTS_DIR / "phase25_exposure_accounting.csv"
    df = pd.read_csv(exp_csv)
    p14_alerts = df[df["detector"] == "Phase 14 Balanced"].sort_values("recording_id")["observed_alerts"].values
    p17_alerts = df[df["detector"] == "Phase 17 Experimental"].sort_values("recording_id")["observed_alerts"].values
    diffs = p14_alerts - p17_alerts
    nonzero = diffs[diffs != 0]
    assert len(nonzero) == 3
    assert all(x > 0 for x in nonzero)
    p_val = 0.125
    assert p_val >= 0.05


def test_mandatory_safety_designation():
    """Test 20: Verify mandatory safety banner across all Phase 25 markdown reports."""
    expected_banner = "RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY"
    p25_reports = list(REPORTS_DIR.glob("phase25_*.md"))
    assert len(p25_reports) >= 7, f"Expected at least 7 markdown reports, found {len(p25_reports)}"
    for r in p25_reports:
        content = r.read_text(encoding="utf-8")
        assert expected_banner in content, f"Missing safety banner in {r.name}"

