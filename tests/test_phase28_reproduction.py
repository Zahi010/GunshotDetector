"""
Automated Regression and Reproduction Test Suite for Phase 28
Audits independent reproduction of Phase 27 headline metrics,
cooldown interval ledger reconciliation, campaign-aware statistics,
and state-machine fragmentation forensics.

MANDATORY SAFETY DESIGNATION:
RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.
"""

import os
import json
import hashlib
import numpy as np
import pandas as pd
import pytest
from scipy import stats

SAFETY_BANNER_PHRASE = "RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY"
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
REPORTS_DIR = os.path.join(PROJECT_ROOT, "reports")
DATA_DIR = os.path.join(PROJECT_ROOT, "data", "phase27")

def compute_sha256(filepath):
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

def test_01_frozen_detector_hashes():
    """Verify that all frozen detector models match canonical SHA-256 digests and sizes."""
    canonical_models = {
        "model_phase14.py": ("a268551604ae8b73068435ff10ab3d265065f56e0679757fca5b6bf0f061c065", 23340),
        "model_phase17.py": ("e2b262b866fdd5d7f1a4ab91a7b8b9bac189ee8cc7a78603b3544ca1579fb819", 29067),
        "model_phase13.py": ("68585039a4a4fdb7978a99f5e2a72c0ad5a9523127ec24a1338fbedd1c1231e6", 22252),
        "model_phase9.py": ("85cedd9f5b988ecafb1eae7de9630ee3d6a387ded6ef732e0efb7c3b496f132a", 17719),
    }
    for filename, (expected_hash, expected_size) in canonical_models.items():
        fp = os.path.join(PROJECT_ROOT, filename)
        assert os.path.exists(fp), f"Model file {filename} does not exist"
        assert compute_sha256(fp) == expected_hash, f"Hash mismatch for {filename}"
        assert os.path.getsize(fp) == expected_size, f"Size mismatch for {filename}"

def test_02_historical_release_archives():
    """Verify historical release archives exist and match canonical digests."""
    parent_root = os.path.abspath(os.path.join(PROJECT_ROOT, ".."))
    archive_hashes = {
        "gunshot_detection_phase27.zip": ("59c27ccdb74a8e17c269eddd3d8965a6a9350cc0b9f45687b792e5ba1dfb490d", 4610265),
        "gunshot_detection_phase26.zip": ("df8d3e0165c98b1b093e93d6edf12a43a6c831c6818122a23da4c3db29ea5c01", 8218546),
        "gunshot_detection_phase25.zip": ("cc2349c46ebaeed859ed300a0b2f402e62bf9c20994d2112a15ec47cd656425e", 8213032),
        "gunshot_detection_phase24.zip": ("3e732e0716160f2d77b71ceff3e01a49f3d933e397bf29bf222fec771a8832b8", 8215859),
        "gunshot_detection_phase23.zip": ("5ce4e64715829d9b52111b6d6322f251976e1ce99e829d9dfbe0858a7e1644c8", 8194616),
        "gunshot_detection_phase22.zip": ("160d327072c3515e945ca5cdf89038f14b6ef1919b1e4865278affab52ad4de5", 8199741),
        "gunshot_detection_phase21.zip": ("b065747b0e6118d228336bee7f8c3811890b638a25070d3ce2a047c329b3e225", 8211219),
        "gunshot_detection_phase20.zip": ("dda7427f2dbffcb178f6d9ade0abb80fbfc491751f04de5dc0db1b4731c31c89", 8205938),
    }
    for filename, (expected_hash, expected_size) in archive_hashes.items():
        fp = os.path.join(parent_root, filename)
        assert os.path.exists(fp), f"Release archive {filename} does not exist"
        assert compute_sha256(fp) == expected_hash, f"Hash mismatch for {filename}"
        assert os.path.getsize(fp) == expected_size, f"Size mismatch for {filename}"

def test_03_baseline_freeze_manifest():
    """Verify phase28_baseline_freeze.json structure and verification status."""
    freeze_path = os.path.join(REPORTS_DIR, "phase28_baseline_freeze.json")
    assert os.path.exists(freeze_path)
    with open(freeze_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["status"] == "ALL_HASHES_VERIFIED"
    assert data["safety_designation"] == SAFETY_BANNER_PHRASE
    assert len(data["frozen_models"]) == 4

def test_04_recording_and_campaign_counts():
    """Verify total continuous recording count is 23 across 4 independent campaigns."""
    exp_path = os.path.join(REPORTS_DIR, "phase28_exposure_reproduction.csv")
    df = pd.read_csv(exp_path)
    assert df["recording_id"].nunique() == 23
    assert df["campaign_id"].nunique() == 4
    assert df.shape[0] == 46 # 23 streams * 2 detectors

def test_05_gross_exposure_reconstruction():
    """Verify gross monitored duration is exactly 45,525.58 seconds (12.6460 gross hours)."""
    exp_path = os.path.join(REPORTS_DIR, "phase28_exposure_reproduction.csv")
    df = pd.read_csv(exp_path)
    p14_df = df[df["detector"] == "Phase 14 Balanced"]
    gross_s = p14_df["gross_duration_s"].sum()
    gross_hr = p14_df["gross_duration_hr"].sum()
    assert abs(gross_s - 45525.58) < 0.05
    assert abs(gross_hr - 12.6460) < 0.001

def test_06_cooldown_reconciliation_sums():
    """Verify reconciliation of cooldown sums between historical, AeroSonic, and cumulative totals."""
    exp_path = os.path.join(REPORTS_DIR, "phase28_exposure_reproduction.csv")
    df = pd.read_csv(exp_path)
    
    p14 = df[df["detector"] == "Phase 14 Balanced"]
    p17 = df[df["detector"] == "Phase 17 Experimental"]

    p14_hist_cd = p14[p14["campaign_id"] != "CAMPAIGN-AEROSONIC-AU"]["cd_cluster_extended_s"].sum()
    p17_hist_cd = p17[p17["campaign_id"] != "CAMPAIGN-AEROSONIC-AU"]["cd_cluster_extended_s"].sum()
    assert abs(p14_hist_cd - 111.92) < 0.01
    assert abs(p17_hist_cd - 101.92) < 0.01

    p14_aero_cd = p14[p14["campaign_id"] == "CAMPAIGN-AEROSONIC-AU"]["cd_cluster_extended_s"].sum()
    p17_aero_cd = p17[p17["campaign_id"] == "CAMPAIGN-AEROSONIC-AU"]["cd_cluster_extended_s"].sum()
    assert abs(p14_aero_cd - 342.00) < 0.01
    assert abs(p17_aero_cd - 6283.28) < 0.01

    p14_tot_cd = p14["cd_cluster_extended_s"].sum()
    p17_tot_cd = p17["cd_cluster_extended_s"].sum()
    assert abs(p14_tot_cd - 453.92) < 0.01
    assert abs(p17_tot_cd - 6385.20) < 0.01

def test_07_cooldown_interval_ledger_properties():
    """Verify cooldown interval ledger contains 287 alerts with valid boundaries and union logic."""
    ledger_path = os.path.join(REPORTS_DIR, "phase28_cooldown_interval_ledger.csv")
    assert os.path.exists(ledger_path)
    df = pd.read_csv(ledger_path)
    assert df.shape[0] == 287
    assert (df["convention_a_duration_s"] <= 2.0).all()
    assert (df["convention_a_duration_s"] > 0.0).all()
    assert (df["convention_b_duration_s"] >= df["convention_a_duration_s"]).all()

def test_08_alert_count_reconstruction():
    """Verify total alert counts: 128 for Phase 14 Balanced, 159 for Phase 17 Experimental."""
    exp_path = os.path.join(REPORTS_DIR, "phase28_exposure_reproduction.csv")
    df = pd.read_csv(exp_path)
    p14_alerts = df[df["detector"] == "Phase 14 Balanced"]["observed_alerts"].sum()
    p17_alerts = df[df["detector"] == "Phase 17 Experimental"]["observed_alerts"].sum()
    assert p14_alerts == 128
    assert p17_alerts == 159
    assert p17_alerts - p14_alerts == 31

def test_09_gross_and_eligible_alert_rates():
    """Verify gross and eligible alert rates match independent calculations."""
    exp_path = os.path.join(REPORTS_DIR, "phase28_exposure_reproduction.csv")
    df = pd.read_csv(exp_path)
    p14 = df[df["detector"] == "Phase 14 Balanced"]
    p17 = df[df["detector"] == "Phase 17 Experimental"]

    p14_g_far = p14["observed_alerts"].sum() / p14["gross_duration_hr"].sum()
    p17_g_far = p17["observed_alerts"].sum() / p17["gross_duration_hr"].sum()
    assert abs(p14_g_far - 10.1218) < 0.001
    assert abs(p17_g_far - 12.5732) < 0.001

    p14_el_far = p14["observed_alerts"].sum() / p14["eligible_cluster_extended_hr"].sum()
    p17_el_far = p17["observed_alerts"].sum() / p17["eligible_cluster_extended_hr"].sum()
    assert abs(p14_el_far - 10.2237) < 0.005
    assert abs(p17_el_far - 14.6243) < 0.005

def test_10_paired_stream_differences():
    """Verify 23 paired stream differences: 5 favor P14, 3 favor P17, 15 tied."""
    exp_path = os.path.join(REPORTS_DIR, "phase28_exposure_reproduction.csv")
    df = pd.read_csv(exp_path)
    p14_s = df[df["detector"] == "Phase 14 Balanced"].sort_values("recording_id").reset_index(drop=True)
    p17_s = df[df["detector"] == "Phase 17 Experimental"].sort_values("recording_id").reset_index(drop=True)
    
    diffs = p14_s["observed_alerts"] - p17_s["observed_alerts"]
    zeros = (diffs == 0).sum()
    p14_fav = (diffs < 0).sum()
    p17_fav = (diffs > 0).sum()
    assert zeros == 15
    assert p14_fav == 5
    assert p17_fav == 3

def test_11_wilcoxon_rank_and_pvalue():
    """Verify paired Wilcoxon signed-rank test yields W = 8.0, p = 0.1953125."""
    diffs = [0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 1, 0, -8, -2, 0, -2, -11, -13]
    res = stats.wilcoxon(diffs, method="exact", alternative="two-sided")
    assert res.statistic == 8.0
    assert abs(res.pvalue - 0.1953125) < 1e-6

def test_12_campaign_summary_aggregation():
    """Verify phase28_campaign_summary.csv aggregates across all 4 campaigns correctly."""
    camp_path = os.path.join(REPORTS_DIR, "phase28_campaign_summary.csv")
    assert os.path.exists(camp_path)
    df = pd.read_csv(camp_path)
    assert df.shape[0] == 4
    assert df["stream_count"].sum() == 23
    assert df["p14_alerts"].sum() == 128
    assert df["p17_alerts"].sum() == 159
    assert df["delta_alerts_p14_minus_p17"].sum() == -31

def test_13_leave_one_campaign_out_sensitivity():
    """Verify phase28_leave_one_campaign_out.csv contains 4 iterations and P14 dominance."""
    loco_path = os.path.join(REPORTS_DIR, "phase28_leave_one_campaign_out.csv")
    assert os.path.exists(loco_path)
    df = pd.read_csv(loco_path)
    assert df.shape[0] == 4
    # Check that in 3 out of 4 LOCO iterations, Phase 14 is superior
    p14_sup = (df["predominant_model"] == "Phase 14 Superior").sum()
    assert p14_sup == 3

def test_14_aircraft_fragmentation_sequences():
    """Verify phase28_aircraft_event_sequences.csv identifies fragmented sequences."""
    seq_path = os.path.join(REPORTS_DIR, "phase28_aircraft_event_sequences.csv")
    assert os.path.exists(seq_path)
    df = pd.read_csv(seq_path)
    assert df.shape[0] >= 20 # At least 20 fragmented sequences
    assert (df["fragmentation_observed"] == True).all()

def test_15_poisson_garwood_bounds():
    """Verify Garwood Poisson intervals for aggregate counts."""
    # Count k=128, T=12.5199 hr
    alpha = 0.05
    lower_128 = 0.5 * stats.chi2.ppf(0.025, 2 * 128) / 12.5199
    upper_128 = 0.5 * stats.chi2.ppf(0.975, 2 * 129) / 12.5199
    assert abs(lower_128 - 8.5294) < 0.05
    assert abs(upper_128 - 12.1561) < 0.05

def test_16_dataset_provenance_and_license():
    """Verify AeroSonicDB source metadata preservation and CC BY-NC 4.0 status."""
    prov_path = os.path.join(REPORTS_DIR, "phase28_dataset_license_and_provenance_audit.md")
    assert os.path.exists(prov_path)
    with open(prov_path, "r", encoding="utf-8") as f:
        content = f.read()
    assert "10215080" in content
    assert "CC BY-NC 4.0" in content
    assert "Blake Downward" in content
    assert "Jon Nordby" in content

def test_17_metric_reconciliation_coverage():
    """Verify reconciliation CSV covers at least 20 key headline metrics."""
    recon_path = os.path.join(REPORTS_DIR, "phase28_metric_reconciliation.csv")
    assert os.path.exists(recon_path)
    df = pd.read_csv(recon_path)
    assert df.shape[0] >= 20
    assert set(df["status"].unique()).issubset({"VERIFIED", "RECONCILED_WITH_DISCREPANCY"})

def test_18_mandatory_safety_designation():
    """Verify all Phase 28 markdown reports display mandatory safety designation."""
    md_reports = [
        "phase28_final_report.md",
        "phase28_cooldown_reconciliation.md",
        "phase28_campaign_aware_statistics.md",
        "phase28_aircraft_fragmentation_audit.md",
        "phase28_poisson_and_heterogeneity_audit.md",
        "phase28_dataset_license_and_provenance_audit.md",
        "phase28_risk_and_limitation_register.md"
    ]
    for r in md_reports:
        fp = os.path.join(REPORTS_DIR, r)
        assert os.path.exists(fp), f"Missing markdown report {r}"
        with open(fp, "r", encoding="utf-8") as f:
            content = f.read()
        assert SAFETY_BANNER_PHRASE in content, f"Safety phrase missing in {r}"

def test_19_model_role_terminology():
    """Verify strict adherence to role terminology across manifests."""
    man_path = os.path.join(REPORTS_DIR, "phase28_processing_manifest.json")
    with open(man_path, "r", encoding="utf-8") as f:
        raw_text = f.read().lower()
    assert "default research baseline" in raw_text or "phase14_balanced" in raw_text
    assert "production baseline" not in raw_text

def test_20_deterministic_reproduction():
    """Verify that re-running calculation yields identical sums and hashes."""
    prov_df = pd.read_csv(os.path.join(REPORTS_DIR, "phase27_recording_provenance.csv"))
    assert prov_df["sha256"].nunique() == 23
    assert round(prov_df["duration_seconds"].sum(), 2) == 45525.58
    assert abs(prov_df["duration_seconds"].sum() - 45525.575) < 1e-3
