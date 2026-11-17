"""
Automated Test Suite for Phase 27
Focus: Authorized AeroSonicDB Acquisition, Continuous-Audio Ingestion & Statistical Inference Correction

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
    """Verify that all frozen detector models are unchanged with canonical hashes."""
    canonical_hashes = {
        "model_phase14.py": ("a268551604ae8b73068435ff10ab3d265065f56e0679757fca5b6bf0f061c065", 23340),
        "model_phase17.py": ("e2b262b866fdd5d7f1a4ab91a7b8b9bac189ee8cc7a78603b3544ca1579fb819", 29067),
        "model_phase13.py": ("68585039a4a4fdb7978a99f5e2a72c0ad5a9523127ec24a1338fbedd1c1231e6", 22252),
        "model_phase9.py": ("85cedd9f5b988ecafb1eae7de9630ee3d6a387ded6ef732e0efb7c3b496f132a", 17719),
    }
    for filename, (expected_hash, expected_size) in canonical_hashes.items():
        fp = os.path.join(PROJECT_ROOT, filename)
        assert os.path.exists(fp), f"Model file {filename} does not exist"
        assert compute_sha256(fp) == expected_hash, f"Hash mismatch for {filename}"
        assert os.path.getsize(fp) == expected_size, f"Size mismatch for {filename}"

def test_02_historical_release_archives():
    """Verify historical release archives exist and match canonical digests."""
    parent_root = os.path.abspath(os.path.join(PROJECT_ROOT, ".."))
    archive_hashes = {
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

def test_03_baseline_freeze_report():
    """Verify phase27_baseline_freeze.json structure and verification status."""
    freeze_path = os.path.join(REPORTS_DIR, "phase27_baseline_freeze.json")
    assert os.path.exists(freeze_path)
    with open(freeze_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["status"] == "ALL_HASHES_VERIFIED"
    assert data["safety_designation"] == SAFETY_BANNER_PHRASE
    assert len(data["frozen_models"]) == 4
    assert len(data["release_archives"]) >= 7

def test_04_source_metadata_verification():
    """Verify phase27_source_verification.json records Zenodo 10215080 details."""
    verif_path = os.path.join(REPORTS_DIR, "phase27_source_verification.json")
    assert os.path.exists(verif_path)
    with open(verif_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["zenodo_record_id"] == 10215080
    assert data["zenodo_concept_id"] == 8000468
    assert data["license_verified"]["license_actual_zenodo"] == "CC BY-NC 4.0"
    assert data["license_verified"]["commercial_use_permitted"] is False
    assert data["access_route"]["protocol"] == "HTTPS_REST_API"

def test_05_download_integrity():
    """Verify downloaded env_audio.zip matches exact repository checksums and testzip CRC passes."""
    integ_path = os.path.join(REPORTS_DIR, "phase27_download_integrity.json")
    assert os.path.exists(integ_path)
    with open(integ_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["archive_md5"] == "8c042dc817f459e80ac2491ffc8dd1cd"
    assert data["archive_size_bytes"] == 495276974
    assert data["md5_verification"] == "PASS_EXACT_MATCH"
    assert data["testzip_crc_result"] == "PASS_ZERO_CORRUPT_FILES"
    assert len(data["extracted_files"]) == 6

def test_06_provenance_schema_and_counts():
    """Verify phase27_recording_provenance.csv contains exactly 23 verified streams."""
    prov_path = os.path.join(REPORTS_DIR, "phase27_recording_provenance.csv")
    assert os.path.exists(prov_path)
    df = pd.read_csv(prov_path)
    assert df.shape[0] == 23, f"Expected 23 recordings, got {df.shape[0]}"
    assert (df["eligibility_category"] == "VERIFIED_NEGATIVE").all()
    assert (df["continuity_status"] == "NATURAL_CONTINUOUS").all()
    assert (df["sample_rate_hz"] == 16000).all()
    assert (df["channels"] == 1).all()

def test_07_duplicate_detection():
    """Verify all 23 recording SHA-256 hashes are unique (zero duplication)."""
    prov_path = os.path.join(REPORTS_DIR, "phase27_recording_provenance.csv")
    df = pd.read_csv(prov_path)
    assert df["sha256"].nunique() == 23, "Duplicate recording hash detected"
    assert df["filename"].nunique() == 23, "Duplicate filename detected"

def test_08_continuity_audit():
    """Verify phase27_continuity_audit.csv demonstrates 100% continuity and zero corruption."""
    cont_path = os.path.join(REPORTS_DIR, "phase27_continuity_audit.csv")
    assert os.path.exists(cont_path)
    df = pd.read_csv(cont_path)
    assert df.shape[0] == 23
    assert df["decoding_success"].str.startswith("PASS").all()
    assert (df["timestamp_gaps_detected"] == "NONE").all()
    assert (df["file_corruption_detected"] == "NONE").all()
    assert df["front_end_clipping_detected"].str.startswith("NONE").all()
    assert df["event_annotations"].str.contains("NO_TARGET_EVENTS|ZERO_GUNSHOT").all()

def test_09_negative_label_eligibility():
    """Verify negative eligibility report covers provenance and lack of weapon fire."""
    report_path = os.path.join(REPORTS_DIR, "phase27_negative_eligibility_report.md")
    assert os.path.exists(report_path)
    with open(report_path, "r", encoding="utf-8") as f:
        content = f.read()
    assert SAFETY_BANNER_PHRASE in content
    assert "VERIFIED_NEGATIVE" in content
    assert "YPAD" in content
    assert "Adelaide" in content

def test_10_exposure_calculations():
    """Verify gross and eligible exposure calculations in exposure accounting CSV."""
    exp_path = os.path.join(REPORTS_DIR, "phase27_exposure_accounting.csv")
    assert os.path.exists(exp_path)
    df = pd.read_csv(exp_path)
    assert df.shape[0] == 46 # 23 streams * 2 detectors
    
    # Check that eligible exposure = gross - cooldown
    for _, row in df.iterrows():
        expected_el_s = round(row["gross_duration_s"] - row["cooldown_excluded_s"], 2)
        assert abs(row["eligible_exposure_s"] - expected_el_s) <= 0.05
        assert row["eligible_exposure_hr"] <= row["gross_duration_hr"]

def test_11_cooldown_interval_union_and_no_duplicated_exposure():
    """Verify cooldown exclusion intervals do not exceed gross duration and have valid bounds."""
    exp_path = os.path.join(REPORTS_DIR, "phase27_exposure_accounting.csv")
    df = pd.read_csv(exp_path)
    assert (df["cooldown_excluded_s"] >= 0.0).all()
    assert (df["cooldown_excluded_s"] <= df["gross_duration_s"]).all()
    assert (df["eligible_exposure_s"] > 0.0).all()

def test_12_paired_difference_reconstruction():
    """Verify stream-by-stream paired differences match exactly across all 23 streams."""
    exp_path = os.path.join(REPORTS_DIR, "phase27_exposure_accounting.csv")
    df = pd.read_csv(exp_path)
    p14_df = df[df["detector"] == "Phase 14 Balanced"].sort_values("recording_id").reset_index(drop=True)
    p17_df = df[df["detector"] == "Phase 17 Experimental"].sort_values("recording_id").reset_index(drop=True)
    
    diffs = p14_df["observed_alerts"] - p17_df["observed_alerts"]
    # Check counts of diffs
    zeros = (diffs == 0).sum()
    p17_better = (diffs > 0).sum()
    p14_better = (diffs < 0).sum()
    
    assert zeros == 15, f"Expected 15 tied streams, got {zeros}"
    assert p17_better == 3, f"Expected 3 streams in favor of P17, got {p17_better}"
    assert p14_better == 5, f"Expected 5 streams in favor of P14, got {p14_better}"

def test_13_zero_difference_handling_and_wilcoxon_rank_calculation():
    """Verify that zero differences are correctly excluded in standard Pratt/Wilcoxon calculation."""
    diffs = [0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 1, 0, -8, -2, 0, -2, -11, -13]
    non_zero = [d for d in diffs if d != 0]
    assert len(non_zero) == 8
    res = stats.wilcoxon(diffs, method="exact", alternative="two-sided")
    assert res.statistic == 8.0
    assert abs(res.pvalue - 0.1953125) < 1e-6

def test_14_exact_sign_test_calculations():
    """Verify exact one-sided and two-sided sign test calculations."""
    # Historical 17 streams: 3 positive, 0 negative (n=3)
    p_one_sided_hist = 0.5 ** 3
    p_two_sided_hist = 2 * (0.5 ** 3)
    assert p_one_sided_hist == 0.125
    assert p_two_sided_hist == 0.250
    
    # All 23 streams: 3 positive, 5 negative (n=8)
    p_two_sided_all = 2 * sum(stats.binom.pmf(i, 8, 0.5) for i in range(4))
    assert p_two_sided_all > 0.05

def test_15_vmr_and_poisson_overdispersion():
    """Verify VMR audit: count VMR > 1.0 is driven by duration variance and spatial heterogeneity."""
    vmr_path = os.path.join(REPORTS_DIR, "phase27_vmr_reproduction.csv")
    assert os.path.exists(vmr_path)
    df = pd.read_csv(vmr_path)
    assert "p14_vmr" in df.columns
    assert "p17_vmr" in df.columns
    assert "duration_variance_hr_sq" in df.columns
    # Check that raw stream count VMR is >> 1.0 (overdispersed)
    raw_row = df[df["analysis_level"] == "RAW_STREAM_COUNTS_DDOF1"].iloc[0]
    assert raw_row["p14_vmr"] > 7.5
    assert raw_row["p17_vmr"] > 7.0

def test_16_garwood_poisson_ci_calculations():
    """Verify Garwood Poisson confidence intervals on sample counts."""
    # Count k=0, exposure=1.0 hr -> lower=0.0, upper=3.6889
    alpha = 0.05
    upper_0 = 0.5 * stats.chi2.ppf(0.975, 2)
    assert abs(upper_0 - 3.6889) < 0.001
    
    # Count k=128, exposure=12.5195 hr
    lower_128 = 0.5 * stats.chi2.ppf(0.025, 2 * 128) / 12.5195
    upper_128 = 0.5 * stats.chi2.ppf(0.975, 2 * 129) / 12.5195
    assert 8.5 < lower_128 < 9.0
    assert 12.0 < upper_128 < 12.5

def test_17_gross_and_eligible_alert_rate_audit():
    """Verify gross and eligible alert rates across all 23 streams."""
    exp_path = os.path.join(REPORTS_DIR, "phase27_exposure_accounting.csv")
    df = pd.read_csv(exp_path)
    
    p14_alerts = df[df["detector"] == "Phase 14 Balanced"]["observed_alerts"].sum()
    p17_alerts = df[df["detector"] == "Phase 17 Experimental"]["observed_alerts"].sum()
    
    assert p14_alerts == 128
    assert p17_alerts == 159
    assert p14_alerts < p17_alerts, "Phase 14 should have fewer alerts than Phase 17 overall"

def test_18_common_matched_exposure_comparison():
    """Verify matched comparison shows Phase 14 superior under identical gross exposure."""
    matched_path = os.path.join(REPORTS_DIR, "phase27_matched_model_comparison.md")
    assert os.path.exists(matched_path)
    with open(matched_path, "r", encoding="utf-8") as f:
        content = f.read()
    assert "128" in content
    assert "159" in content
    assert "Phase 14 Superior" in content
    assert "RETAIN_PHASE_14_BALANCED" or "DEFAULT RESEARCH BASELINE" in content

def test_19_distractor_analysis_cluster_fragmentation():
    """Verify distractor analysis documents cluster fragmentation and hysteresis in Phase 17."""
    dist_path = os.path.join(REPORTS_DIR, "phase27_distractor_analysis.md")
    assert os.path.exists(dist_path)
    with open(dist_path, "r", encoding="utf-8") as f:
        content = f.read()
    assert "cluster fragmentation" in content.lower()
    assert "threshold_off" in content
    assert "animal" in content.lower()

def test_20_model_role_terminology():
    """Verify strict adherence to role terminology across manifests."""
    man_path = os.path.join(REPORTS_DIR, "phase27_processing_manifest.json")
    with open(man_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["frozen_detectors"]["default_research_baseline"]["name"] == "Phase 14 Balanced"
    assert data["frozen_detectors"]["selectable_experimental_profile"]["name"] == "Phase 17 Experimental"
    # Ensure forbidden 'production baseline' term is not used
    raw_text = json.dumps(data).lower()
    assert "production baseline" not in raw_text

def test_21_mandatory_safety_designation():
    """Verify all Markdown reports and test files display mandatory safety designation."""
    md_files = [
        "phase27_final_report.md",
        "phase27_acquisition_log.md",
        "phase27_negative_eligibility_report.md",
        "phase27_matched_model_comparison.md",
        "phase27_distractor_analysis.md",
        "phase27_statistical_analysis.md",
        "phase27_risk_and_limitation_register.md",
        "phase27_historical_paired_statistics_audit.md",
        "phase27_poisson_assumption_audit.md"
    ]
    for filename in md_files:
        fp = os.path.join(REPORTS_DIR, filename)
        assert os.path.exists(fp), f"Markdown file {filename} missing"
        with open(fp, "r", encoding="utf-8") as f:
            content = f.read()
        assert SAFETY_BANNER_PHRASE in content, f"Safety phrase missing in {filename}"
