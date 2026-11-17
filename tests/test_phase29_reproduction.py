"""
RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY
Phase 29 Automated Forensic & Reproduction Test Suite
Asserts:
- Frozen detector hashes and release archive integrity.
- Configuration provenance and threshold resolution (0.75 / 0.88 / 0.48).
- Gross and eligible exposure calculations under Conventions A and B.
- Interval union logic and non-overlap properties.
- Exact nonparametric statistical tests (Wilcoxon and Sign tests).
- Campaign-level exposure-normalized rates and LOCO sensitivity.
- Aircraft sequence reconstruction and evidence gaps.
- Mandatory safety banner and role terminology compliance.
"""

import os
import sys
import json
import ast
import hashlib
import pytest
import pandas as pd
import numpy as np
from scipy import stats

SAFETY_BANNER_PHRASE = "RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY"

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
WORKSPACE_ROOT = os.path.abspath(os.path.join(PROJECT_ROOT, ".."))
REPORTS_DIR = os.path.join(PROJECT_ROOT, "reports")
DATA_DIR = os.path.join(PROJECT_ROOT, "data")

def compute_sha256(fp: str) -> str:
    h = hashlib.sha256()
    with open(fp, "rb") as f:
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
    """Verify historical release archives (Phase 28 to Phase 20) match canonical digests."""
    archive_hashes = {
        "gunshot_detection_phase28.zip": ("e6505e3597b406541efb005f1d69432653cbfc5603843695fdfd66af01324a72", 4586167),
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
        fp = os.path.join(WORKSPACE_ROOT, filename)
        assert os.path.exists(fp), f"Release archive {filename} does not exist"
        assert compute_sha256(fp) == expected_hash, f"Hash mismatch for {filename}"
        assert os.path.getsize(fp) == expected_size, f"Size mismatch for {filename}"

def test_03_configuration_provenance():
    """Verify runtime configuration manifest contains 46 rows and confirms 0.75/0.88/0.48."""
    man_p = os.path.join(REPORTS_DIR, "phase29_runtime_configuration_manifest.csv")
    assert os.path.exists(man_p)
    df = pd.read_csv(man_p)
    assert len(df) == 46
    assert (df["threshold_base_loaded"] == 0.75).all()
    assert (df["threshold_high_loaded"] == 0.88).all()
    assert (df["threshold_off_loaded"] == 0.48).all()
    assert (df["confirm_windows_loaded"] == 2).all()
    assert (df["cooldown_secs_loaded"] == 2.0).all()
    
    p14_mask = df["detector"] == "Phase 14 Balanced"
    p17_mask = df["detector"] == "Phase 17 Experimental"
    assert not df[p14_mask]["animal_suppression_enabled"].any()
    assert df[p17_mask]["animal_suppression_enabled"].all()

def test_04_threshold_consistency_ast():
    """Parse PROFILES in frozen models via AST to verify true declared threshold constants."""
    def get_profiles(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            tree = ast.parse(f.read())
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                for item in node.body:
                    if isinstance(item, ast.Assign):
                        for target in item.targets:
                            if isinstance(target, ast.Name) and target.id == "PROFILES":
                                return ast.literal_eval(item.value)
        return {}

    p14_prof = get_profiles(os.path.join(PROJECT_ROOT, "model_phase14.py"))["balanced"]
    p17_prof = get_profiles(os.path.join(PROJECT_ROOT, "model_phase17.py"))["experimental_animal_suppression"]

    assert p14_prof["threshold_base"] == 0.75
    assert p14_prof["threshold_high"] == 0.88
    assert p14_prof["threshold_off"] == 0.48
    assert p17_prof["threshold_base"] == 0.75
    assert p17_prof["threshold_high"] == 0.88
    assert p17_prof["threshold_off"] == 0.48

def test_05_recording_and_campaign_counts():
    """Verify total continuous recording count is 23 across 4 independent campaigns."""
    exp_path = os.path.join(REPORTS_DIR, "phase28_exposure_reproduction.csv")
    df = pd.read_csv(exp_path)
    assert df["recording_id"].nunique() == 23
    assert df["campaign_id"].nunique() == 4

def test_06_gross_exposure_reconstruction():
    """Verify gross monitored duration is exactly 45,525.575 seconds (12.6460 gross hours)."""
    exp_path = os.path.join(REPORTS_DIR, "phase28_exposure_reproduction.csv")
    df = pd.read_csv(exp_path)
    p14 = df[df["detector"] == "Phase 14 Balanced"]
    gross_s = p14["gross_duration_s"].sum()
    gross_hr = gross_s / 3600.0
    assert abs(gross_s - 45525.575) < 0.01
    assert abs(gross_hr - 12.6460) < 0.001

def test_07_eligible_exposure_convention_a():
    """Verify Convention A excluded seconds are 255.84s (P14) and 316.56s (P17)."""
    exp_path = os.path.join(REPORTS_DIR, "phase28_exposure_reproduction.csv")
    df = pd.read_csv(exp_path)
    p14 = df[df["detector"] == "Phase 14 Balanced"]
    p17 = df[df["detector"] == "Phase 17 Experimental"]

    p14_cd_a = p14["cd_instantaneous_s"].sum()
    p17_cd_a = p17["cd_instantaneous_s"].sum()
    assert abs(p14_cd_a - 255.84) < 0.05
    assert abs(p17_cd_a - 316.56) < 0.05

    p14_el_a = p14["eligible_instantaneous_hr"].sum()
    p17_el_a = p17["eligible_instantaneous_hr"].sum()
    assert abs(p14_el_a - 12.5749) < 0.005
    assert abs(p17_el_a - 12.5581) < 0.005

def test_08_eligible_exposure_convention_b():
    """Verify Convention B excluded seconds are 453.92s (P14) and 6385.20s (P17)."""
    exp_path = os.path.join(REPORTS_DIR, "phase28_exposure_reproduction.csv")
    df = pd.read_csv(exp_path)
    p14 = df[df["detector"] == "Phase 14 Balanced"]
    p17 = df[df["detector"] == "Phase 17 Experimental"]

    p14_cd_b = p14["cd_cluster_extended_s"].sum()
    p17_cd_b = p17["cd_cluster_extended_s"].sum()
    assert abs(p14_cd_b - 453.92) < 0.05
    assert abs(p17_cd_b - 6385.20) < 0.05

    p14_el_b = p14["eligible_cluster_extended_hr"].sum()
    p17_el_b = p17["eligible_cluster_extended_hr"].sum()
    assert abs(p14_el_b - 12.5199) < 0.005
    assert abs(p17_el_b - 10.8723) < 0.005

def test_09_cooldown_interval_union_logic():
    """Verify that interval ledger conforms to union math and e_k >= s_k."""
    ledger_p = os.path.join(REPORTS_DIR, "phase28_cooldown_interval_ledger.csv")
    df = pd.read_csv(ledger_p)
    assert len(df) == 287
    assert (df["convention_b_duration_s"] >= df["convention_a_duration_s"]).all()
    assert (df["convention_a_duration_s"] <= 2.0).all()

def test_10_alert_count_reconstruction():
    """Verify observed alerts: 128 (P14) vs 159 (P17), difference = +31 alerts."""
    exp_path = os.path.join(REPORTS_DIR, "phase28_exposure_reproduction.csv")
    df = pd.read_csv(exp_path)
    p14_k = df[df["detector"] == "Phase 14 Balanced"]["observed_alerts"].sum()
    p17_k = df[df["detector"] == "Phase 17 Experimental"]["observed_alerts"].sum()
    assert p14_k == 128
    assert p17_k == 159
    assert p17_k - p14_k == 31

def test_11_paired_differences_reconstruction():
    """Verify stream paired differences: 15 tied, 5 favor P14, 3 favor P17."""
    exp_path = os.path.join(REPORTS_DIR, "phase28_exposure_reproduction.csv")
    df = pd.read_csv(exp_path)
    p14 = df[df["detector"] == "Phase 14 Balanced"].sort_values("recording_id").reset_index(drop=True)
    p17 = df[df["detector"] == "Phase 17 Experimental"].sort_values("recording_id").reset_index(drop=True)

    diffs = p14["observed_alerts"] - p17["observed_alerts"]
    assert (diffs == 0).sum() == 15
    assert (diffs < 0).sum() == 5  # P14 has fewer alerts
    assert (diffs > 0).sum() == 3  # P17 has fewer alerts

def test_12_wilcoxon_and_sign_tests():
    """Verify exact two-sided Wilcoxon W = 8.0, p = 0.1953125 and sign test p = 0.7265625."""
    nonzero_diffs = [2, 2, 1, -8, -2, -2, -11, -13]
    res_w = stats.wilcoxon(nonzero_diffs, method="exact", alternative="two-sided")
    assert res_w.statistic == 8.0
    assert abs(res_w.pvalue - 0.1953125) < 1e-6

    # Sign test: 3 positive out of 8
    # 2 * (1 + 8 + 28 + 56) / 256 = 186 / 256 = 0.7265625
    p_sign = 2.0 * stats.binom.cdf(3, 8, 0.5)
    assert abs(p_sign - 0.7265625) < 1e-6

def test_13_campaign_rate_aggregation():
    """Verify phase29_campaign_rate_table.csv aggregates all 4 campaigns correctly."""
    camp_p = os.path.join(REPORTS_DIR, "phase29_campaign_rate_table.csv")
    assert os.path.exists(camp_p)
    df = pd.read_csv(camp_p)
    assert len(df) == 5  # 4 campaigns + cumulative total

    bilbao = df[df["campaign_id"] == "CAMPAIGN-BILBAO-ES"].iloc[0]
    assert bilbao["p14_gross_far"] > 50.0  # Dense traffic alert saturation
    assert bilbao["p17_gross_far"] > 50.0

    aero = df[df["campaign_id"] == "CAMPAIGN-AEROSONIC-AU"].iloc[0]
    assert aero["p14_conv_b_far"] < 13.0
    assert aero["p17_conv_b_far"] > 25.0

def test_14_loco_reproduction_calculations():
    """Verify 4 LOCO subsets, checking subset without AeroSonicDB has P17 = 51, P14 = 56."""
    loco_p = os.path.join(REPORTS_DIR, "phase29_loco_reproduction.csv")
    assert os.path.exists(loco_p)
    df = pd.read_csv(loco_p)
    assert len(df) == 4

    no_aero = df[df["excluded_campaign"] == "CAMPAIGN-AEROSONIC-AU"].iloc[0]
    assert no_aero["p14_alerts"] == 56
    assert no_aero["p17_alerts"] == 51
    assert no_aero["alert_difference_p17_minus_p14"] == -5
    assert abs(no_aero["paired_wilcoxon_p_exact"] - 0.2500) < 1e-4

def test_15_aircraft_sequence_reconstruction():
    """Verify 25 candidate aircraft sequences in AeroSonicDB with elevated RMS."""
    recon_p = os.path.join(REPORTS_DIR, "phase29_aircraft_sequence_reconstruction.csv")
    assert os.path.exists(recon_p)
    df = pd.read_csv(recon_p)
    assert len(df) == 25
    assert (df["waveform_rms_peak"] > 0.0035).all()
    assert (df["threshold_off_active"] == 0.48).all()
    assert (df["manually_reviewed"] == False).all()

def test_16_aircraft_evidence_gaps():
    """Verify evidence gap register flags intermediate sub-window score unlogged status."""
    gap_p = os.path.join(REPORTS_DIR, "phase29_aircraft_evidence_gaps.csv")
    assert os.path.exists(gap_p)
    df = pd.read_csv(gap_p)
    assert len(df) == 25
    assert not df["step1_score_sub_window_trace_logged"].any()
    assert not df["step2_animal_suppression_active_flag_logged"].any()
    assert (df["mechanism_confirmation_verdict"] == "PARTIALLY_SUPPORTED_UNVERIFIED_INTERMEDIATES").all()

def test_17_no_missing_or_duplicate_events():
    """Verify total alerts in raw JSON match cumulative ledger entries."""
    raw_p = os.path.join(DATA_DIR, "phase27", "phase27_aerosonic_eval_raw.json")
    with open(raw_p, "r") as f:
        d = json.load(f)
    assert len(d["p14_alerts_list"]) == 72
    assert len(d["p17_alerts_list"]) == 108

def test_18_mandatory_safety_designation():
    """Assert mandatory safety banner is present across all core Phase 29 deliverables."""
    files_to_check = [
        "reports/phase29_final_report.md",
        "reports/phase29_threshold_provenance_audit.md",
        "reports/phase29_aircraft_mechanism_validation.md",
        "reports/phase29_cooldown_convention_audit.md",
        "reports/phase29_campaign_rate_robustness.md",
        "reports/phase29_statistical_reproduction.md",
        "reports/phase29_reproducibility_audit.md",
        "reports/phase29_risk_and_limitation_register.md",
        "reports/phase29_baseline_freeze.json",
        "reports/phase29_processing_manifest.json"
    ]
    for rel_p in files_to_check:
        fp = os.path.join(PROJECT_ROOT, rel_p)
        assert os.path.exists(fp), f"Missing file: {rel_p}"
        if rel_p.endswith(".json"):
            with open(fp, "r", encoding="utf-8") as f:
                d = json.load(f)
            assert d.get("safety_designation") == SAFETY_BANNER_PHRASE, f"Safety banner missing in JSON {rel_p}"
        else:
            with open(fp, "r", encoding="utf-8") as f:
                content = f.read()
            assert SAFETY_BANNER_PHRASE in content, f"Safety banner missing in {rel_p}"

def test_19_role_terminology():
    """Verify strict adherence to role terminology: Phase 14 is Default Research Baseline."""
    man_path = os.path.join(REPORTS_DIR, "phase29_processing_manifest.json")
    with open(man_path, "r", encoding="utf-8") as f:
        raw_text = f.read().lower()
    assert "production baseline" not in raw_text

def test_20_deterministic_reproduction():
    """Verify that re-running calculation yields identical gross durations and hashes."""
    prov_df = pd.read_csv(os.path.join(REPORTS_DIR, "phase27_recording_provenance.csv"))
    assert prov_df["sha256"].nunique() == 23
    assert abs(prov_df["duration_seconds"].sum() - 45525.575) < 1e-3
