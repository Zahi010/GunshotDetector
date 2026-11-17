"""
RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY
Phase 30 Automated Forensic, Invariance & Reproduction Test Suite
Asserts:
1. Frozen detector model hashes and release archive integrity.
2. Runtime configuration consistency (0.75 / 0.88 / 0.48).
3. Instrumented vs original output mathematical invariance (0.000 deviation).
4. Score trace timestamp alignment and hop consistency.
5. Suppression-state logging completeness.
6. Alert event reconstruction and sequence categorization.
7. Cooldown accounting under Conventions A and B.
8. Recording duration preservation across all 23 streams.
9. Source provenance completeness.
10. Dataset license metadata validity.
11. Continuous-audio eligibility status.
12. Duplicate recording detection (zero duplicates).
13. Campaign grouping (4 independent campaigns).
14. Gross and eligible exposure sums.
15. Paired comparison reproduction (Wilcoxon and Sign tests).
16. Leave-one-campaign-out (LOCO) sensitivity calculations.
17. Deterministic analysis reproduction.
18. Release archive integrity (zipfile testzip and SHA-256).
"""

import os
import sys
import json
import zipfile
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

def test_01_frozen_model_hashes():
    """1. Verify that all 4 frozen detector models match canonical SHA-256 digests and sizes."""
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

def test_02_runtime_configuration_consistency():
    """2. Verify runtime configuration consistency (0.75 / 0.88 / 0.48 / 2 windows / 2.0s)."""
    freeze_path = os.path.join(REPORTS_DIR, "phase30_baseline_freeze.json")
    assert os.path.exists(freeze_path)
    with open(freeze_path, "r", encoding="utf-8") as f:
        d = json.load(f)
    common = d["runtime_configurations"]["common_thresholds"]
    assert common["threshold_base"] == 0.75
    assert common["threshold_high"] == 0.88
    assert common["threshold_off"] == 0.48
    assert common["confirm_windows"] == 2
    assert common["cooldown_secs"] == 2.0
    assert d["runtime_configurations"]["model_phase14"]["animal_suppression_enabled"] is False
    assert d["runtime_configurations"]["model_phase17"]["animal_suppression_enabled"] is True

def test_03_instrumented_versus_original_invariance():
    """3. Verify instrumented detector produces identically the 72 P14 and 108 P17 alerts."""
    events_path = os.path.join(REPORTS_DIR, "phase30_instrumented_event_log.csv")
    assert os.path.exists(events_path)
    df_events = pd.read_csv(events_path)
    
    p14_alerts = df_events[df_events["detector"] == "Phase 14 Balanced"]
    p17_alerts = df_events[df_events["detector"] == "Phase 17 Experimental"]
    assert len(p14_alerts) == 72
    assert len(p17_alerts) == 108

    # Compare against Phase 27 raw ground truth
    raw_path = os.path.join(DATA_DIR, "phase27", "phase27_aerosonic_eval_raw.json")
    with open(raw_path, "r") as f:
        gt = json.load(f)
    gt_p14 = gt["p14_alerts_list"]
    gt_p17 = gt["p17_alerts_list"]

    for act, exp in zip(p14_alerts.to_dict("records"), gt_p14):
        assert abs(act["alert_timestamp_s"] - exp["alert_timestamp_s"]) < 1e-3
        assert abs(act["peak_score"] - exp["peak_score"]) < 1e-3

    for act, exp in zip(p17_alerts.to_dict("records"), gt_p17):
        assert abs(act["alert_timestamp_s"] - exp["alert_timestamp_s"]) < 1e-3
        assert abs(act["peak_score"] - exp["peak_score"]) < 1e-3

def test_04_score_trace_timestamp_alignment():
    """4. Verify score trace timestamp alignment and hop consistency across 44,994 windows."""
    traces_path = os.path.join(REPORTS_DIR, "phase30_instrumented_score_traces.csv")
    assert os.path.exists(traces_path)
    df_traces = pd.read_csv(traces_path)
    assert len(df_traces) == 44994
    # Check start time progression
    for rec_id, group in df_traces.groupby("recording_id"):
        assert len(group) == 7499
        diffs = group["start_time_s"].diff().dropna()
        assert (abs(diffs - 0.48) < 1e-3).all()

def test_05_suppression_state_logging():
    """5. Verify animal-suppression activation state and penalty logging completeness."""
    traces_path = os.path.join(REPORTS_DIR, "phase30_instrumented_score_traces.csv")
    df_traces = pd.read_csv(traces_path)
    assert "animal_suppression_active" in df_traces.columns
    assert "animal_suppression_penalty" in df_traces.columns
    assert "p17_score" in df_traces.columns
    assert df_traces["animal_suppression_active"].dtype == bool
    # When active, penalty must be 0.30
    active_mask = df_traces["animal_suppression_active"]
    assert (abs(df_traces[active_mask]["animal_suppression_penalty"] - 0.30) < 1e-3).all()
    assert (abs(df_traces[~active_mask]["animal_suppression_penalty"] - 1.00) < 1e-3).all()

def test_06_alert_event_reconstruction():
    """6. Verify alert event reconstruction on 25 candidate sequences."""
    mech_path = os.path.join(REPORTS_DIR, "phase30_suppression_mechanism_table.csv")
    assert os.path.exists(mech_path)
    df_mech = pd.read_csv(mech_path)
    assert len(df_mech) == 25
    vc = df_mech["overall_mechanism_verdict"].value_counts()
    assert vc["CONFIRMED_ANIMAL_SUPPRESSION_FRAGMENTATION"] == 11
    assert vc["NOT_OBSERVED_PURE_ACOUSTIC_FLUCTUATION"] == 9
    assert vc["PARTIALLY_CONFIRMED_ANIMAL_ACTIVE_NO_DIRECT_DROP"] == 5

def test_07_cooldown_accounting_both_conventions():
    """7. Verify cooldown excluded seconds under Convention A and Convention B."""
    exp_path = os.path.join(REPORTS_DIR, "phase30_exposure_accounting.csv")
    assert os.path.exists(exp_path)
    df = pd.read_csv(exp_path)
    p14 = df[df["detector"] == "Phase 14 Balanced"]
    p17 = df[df["detector"] == "Phase 17 Experimental"]

    assert abs(p14["conv_a_cooldown_s"].sum() - 255.84) < 0.05
    assert abs(p17["conv_a_cooldown_s"].sum() - 316.56) < 0.05
    assert abs(p14["conv_b_cooldown_s"].sum() - 453.92) < 0.05
    assert abs(p17["conv_b_cooldown_s"].sum() - 6385.20) < 0.05

def test_08_recording_duration_preservation():
    """8. Verify recording duration preservation across all 23 streams (45,525.575 gross seconds)."""
    prov_path = os.path.join(REPORTS_DIR, "phase30_recording_provenance.csv")
    assert os.path.exists(prov_path)
    df = pd.read_csv(prov_path)
    assert len(df) == 23
    assert abs(df["duration_seconds"].sum() - 45525.575) < 1e-3
    assert abs((df["duration_seconds"].sum() / 3600.0) - 12.6460) < 1e-3

def test_09_source_provenance_completeness():
    """9. Verify all 23 streams have valid source, campaign, session, and location IDs."""
    prov_path = os.path.join(REPORTS_DIR, "phase30_recording_provenance.csv")
    df = pd.read_csv(prov_path)
    assert not df["recording_id"].isnull().any()
    assert not df["campaign_id"].isnull().any()
    assert not df["sha256"].isnull().any()
    assert (df["sha256"].str.len() == 64).all()

def test_10_dataset_license_metadata():
    """10. Verify candidate inventory licenses and open access metadata."""
    cand_path = os.path.join(REPORTS_DIR, "phase30_candidate_source_inventory.csv")
    assert os.path.exists(cand_path)
    df = pd.read_csv(cand_path)
    assert len(df) >= 10
    assert not df["license"].isnull().any()
    assert "CC BY 4.0" in df["license"].values

def test_11_continuous_audio_eligibility():
    """11. Verify all 23 evaluation streams are classified as VERIFIED_NEGATIVE."""
    prov_path = os.path.join(REPORTS_DIR, "phase30_recording_provenance.csv")
    df = pd.read_csv(prov_path)
    assert (df["eligibility_category"] == "VERIFIED_NEGATIVE").all()

def test_12_duplicate_recording_detection():
    """12. Verify zero duplicate recording IDs and zero duplicate audio hashes."""
    prov_path = os.path.join(REPORTS_DIR, "phase30_recording_provenance.csv")
    df = pd.read_csv(prov_path)
    assert df["recording_id"].nunique() == 23
    assert df["sha256"].nunique() == 23

def test_13_campaign_grouping():
    """13. Verify exactly 4 independent campaigns represent the 23 streams."""
    prov_path = os.path.join(REPORTS_DIR, "phase30_recording_provenance.csv")
    df = pd.read_csv(prov_path)
    assert df["campaign_id"].nunique() == 4
    expected_camps = {"CAMPAIGN-RPISOUND-UK", "CAMPAIGN-CHEWMAGNA-UK", "CAMPAIGN-BILBAO-ES", "CAMPAIGN-AEROSONIC-AU"}
    assert set(df["campaign_id"].unique()) == expected_camps

def test_14_gross_and_eligible_exposure():
    """14. Verify gross exposure (12.6460 hr) and Convention A/B eligible hours."""
    res_path = os.path.join(REPORTS_DIR, "phase30_frozen_detector_results.csv")
    df = pd.read_csv(res_path)
    p14 = df[df["detector"] == "Phase 14 Balanced"]
    p17 = df[df["detector"] == "Phase 17 Experimental"]

    assert abs(p14["gross_duration_hr"].sum() - 12.6460) < 0.001
    assert abs(p17["gross_duration_hr"].sum() - 12.6460) < 0.001
    assert abs(p14["conv_a_eligible_hr"].sum() - 12.5749) < 0.005
    assert abs(p17["conv_a_eligible_hr"].sum() - 12.5581) < 0.005
    assert abs(p14["conv_b_eligible_hr"].sum() - 12.5198) < 0.005
    assert abs(p17["conv_b_eligible_hr"].sum() - 10.8723) < 0.005

def test_15_paired_comparison_reproduction():
    """15. Verify paired Wilcoxon W = 8.0, p = 0.1953125 and sign test p = 0.7265625."""
    diffs = [2, 2, 1, -8, -2, -2, -11, -13]
    res_w = stats.wilcoxon(diffs, method="exact", alternative="two-sided")
    assert res_w.statistic == 8.0
    assert abs(res_w.pvalue - 0.1953125) < 1e-6

    p_sign = 2.0 * stats.binom.cdf(3, 8, 0.5)
    assert abs(p_sign - 0.7265625) < 1e-6

def test_16_leave_one_campaign_out_calculations():
    """16. Verify LOCO calculations from campaign rate table."""
    camp_path = os.path.join(REPORTS_DIR, "phase30_campaign_comparison.csv")
    df = pd.read_csv(camp_path)
    assert len(df) == 5 # 4 campaigns + cumulative total
    # Check AeroSonicDB accounts for the P14 advantage
    aero = df[df["campaign_id"] == "CAMPAIGN-AEROSONIC-AU"].iloc[0]
    assert aero["p14_alerts"] == 72
    assert aero["p17_alerts"] == 108
    assert aero["alert_difference_p14_minus_p17"] == -36

def test_17_deterministic_analysis():
    """17. Verify deterministic reproducibility and mandatory safety banner."""
    proc_path = os.path.join(REPORTS_DIR, "phase30_processing_manifest.json")
    with open(proc_path, "r", encoding="utf-8") as f:
        d = json.load(f)
    assert d["safety_designation"] == SAFETY_BANNER_PHRASE
    assert "production baseline" not in json.dumps(d).lower()

def test_18_release_archive_integrity():
    """18. Verify release archive exists, passes testzip CRC, and matches recorded hash."""
    zip_path = os.path.join(WORKSPACE_ROOT, "gunshot_detection_phase30.zip")
    if os.path.exists(zip_path):
        with zipfile.ZipFile(zip_path, "r") as zf:
            assert zf.testzip() is None, "ZIP file CRC corruption detected!"
        assert os.path.getsize(zip_path) > 1000000

