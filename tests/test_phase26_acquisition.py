"""
Phase 26 Acquisition, Verification & Baseline Integrity Test Suite
MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.
"""

import os
import hashlib
import json
import csv
import pytest

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPORTS_DIR = os.path.join(BASE_DIR, "reports")

EXPECTED_MODELS = {
    "model_phase14.py": {"sha256": "a268551604ae8b73068435ff10ab3d265065f56e0679757fca5b6bf0f061c065", "size": 23340},
    "model_phase17.py": {"sha256": "e2b262b866fdd5d7f1a4ab91a7b8b9bac189ee8cc7a78603b3544ca1579fb819", "size": 29067},
    "model_phase13.py": {"sha256": "68585039a4a4fdb7978a99f5e2a72c0ad5a9523127ec24a1338fbedd1c1231e6", "size": 22252},
    "model_phase9.py":  {"sha256": "85cedd9f5b988ecafb1eae7de9630ee3d6a387ded6ef732e0efb7c3b496f132a", "size": 17719},
}

EXPECTED_HISTORICAL_ARCHIVES = {
    "gunshot_detection_phase25.zip": "cc2349c46ebaeed859ed300a0b2f402e62bf9c20994d2112a15ec47cd656425e",
    "gunshot_detection_phase24.zip": "3e732e0716160f2d77b71ceff3e01a49f3d933e397bf29bf222fec771a8832b8",
    "gunshot_detection_phase23.zip": "5ce4e64715829d9b52111b6d6322f251976e1ce99e829d9dfbe0858a7e1644c8",
    "gunshot_detection_phase22.zip": "160d327072c3515e945ca5cdf89038f14b6ef1919b1e4865278affab52ad4de5",
    "gunshot_detection_phase21.zip": "b065747b0e6118d228336bee7f8c3811890b638a25070d3ce2a047c329b3e225",
    "gunshot_detection_phase20.zip": "dda7427f2dbffcb178f6d9ade0abb80fbfc491751f04de5dc0db1b4731c31c89",
}

def compute_sha256(filepath):
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

# 1. Test Frozen Detector Model SHA-256 Hashes
def test_01_frozen_detector_hashes():
    for filename, meta in EXPECTED_MODELS.items():
        filepath = os.path.join(BASE_DIR, filename)
        assert os.path.exists(filepath), f"Missing model file: {filename}"
        assert compute_sha256(filepath) == meta["sha256"], f"Hash mismatch for {filename}"
        assert os.path.getsize(filepath) == meta["size"], f"Size mismatch for {filename}"

# 2. Test Historical Release Archive Hashes
def test_02_historical_release_archives():
    parent_dir = os.path.dirname(BASE_DIR)
    for archive_name, expected_hash in EXPECTED_HISTORICAL_ARCHIVES.items():
        archive_path = os.path.join(parent_dir, archive_name)
        assert os.path.exists(archive_path), f"Missing archive: {archive_name}"
        assert compute_sha256(archive_path) == expected_hash, f"Hash mismatch for {archive_name}"

# 3. Test Baseline Freeze JSON Report
def test_03_baseline_freeze_report():
    freeze_path = os.path.join(REPORTS_DIR, "phase26_baseline_freeze.json")
    assert os.path.exists(freeze_path)
    with open(freeze_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["frozen_models"]["model_phase14.py"]["verification"] == "MATCH_CONFIRMED"
    assert data["frozen_models"]["model_phase17.py"]["verification"] == "MATCH_CONFIRMED"
    assert data["status"] == "ALL_HASHES_VERIFIED"
    assert len(data["release_archives"]) == 6

# 4. Test Candidate A Audit Classification
def test_04_candidate_a_aerosonicdb_audit():
    audit_path = os.path.join(REPORTS_DIR, "phase26_aerosonicdb_source_audit.md")
    assert os.path.exists(audit_path)
    with open(audit_path, "r", encoding="utf-8") as f:
        text = f.read()
    assert "CONDITIONAL_ACCESS_PENDING" in text
    assert "10215080" in text
    assert "7976269" in text
    assert "HTTP 403 Forbidden" in text

# 5. Test Candidate B Audit Classification
def test_05_candidate_b_isd_audit():
    audit_path = os.path.join(REPORTS_DIR, "phase26_isd_source_audit.md")
    assert os.path.exists(audit_path)
    with open(audit_path, "r", encoding="utf-8") as f:
        text = f.read()
    assert "REJECTED" in text
    assert "30-second" in text or "30-Second" in text
    assert "concatenat" in text.lower()

# 6. Test Zero Synthetic Concatenation Policy
def test_06_zero_synthetic_concatenation_policy():
    elig_path = os.path.join(REPORTS_DIR, "phase26_negative_eligibility_report.md")
    assert os.path.exists(elig_path)
    with open(elig_path, "r", encoding="utf-8") as f:
        text = f.read()
    assert "synthetic concatenation" in text.lower() or "concatenation" in text.lower()
    assert "continuity" in text.lower()

# 7. Test Source Registry Schema and Rows
def test_07_source_registry_schema():
    reg_path = os.path.join(REPORTS_DIR, "phase26_source_registry.csv")
    assert os.path.exists(reg_path)
    with open(reg_path, "r", encoding="utf-8") as f:
        reader = list(csv.DictReader(f))
    assert len(reader) >= 12
    required_cols = {"source_id", "name", "repository_type", "license", "evaluation_category"}
    assert required_cols.issubset(reader[0].keys())

# 8. Test Campaign Independence Matrix
def test_08_campaign_independence_matrix():
    matrix_path = os.path.join(REPORTS_DIR, "phase26_campaign_independence_matrix.csv")
    assert os.path.exists(matrix_path)
    with open(matrix_path, "r", encoding="utf-8") as f:
        reader = list(csv.DictReader(f))
    assert len(reader) >= 3
    campaign_ids = {r["campaign_id"] for r in reader}
    assert {"CAMPAIGN-RPISOUND-UK", "CAMPAIGN-CHEWMAGNA-UK", "CAMPAIGN-BILBAO-ES"}.issubset(campaign_ids)

# 9. Test Recording Provenance Schema and Stream Count
def test_09_recording_provenance_schema():
    prov_path = os.path.join(REPORTS_DIR, "phase26_recording_provenance.csv")
    assert os.path.exists(prov_path)
    with open(prov_path, "r", encoding="utf-8") as f:
        reader = list(csv.DictReader(f))
    assert len(reader) == 23  # 17 natural + 6 synthetic cataloged
    natural_streams = [r for r in reader if r["recording_id"].startswith("P26-NAT")]
    assert len(natural_streams) == 17
    total_sec = sum(float(r["duration_seconds"]) for r in natural_streams)
    assert abs(total_sec - 23925.58) < 1.0

# 10. Test Duplicate Audit Shows Zero Duplicates
def test_10_duplicate_audit():
    dup_path = os.path.join(REPORTS_DIR, "phase26_duplicate_audit.csv")
    assert os.path.exists(dup_path)
    with open(dup_path, "r", encoding="utf-8") as f:
        reader = list(csv.DictReader(f))
    assert len(reader) >= 1
    found_zero_dups = any("zero" in r["status"].lower() or "none" in r["intra_phase_collision"].lower() for r in reader)
    assert found_zero_dups

# 11. Test Continuity Audit
def test_11_continuity_audit():
    cont_path = os.path.join(REPORTS_DIR, "phase26_continuity_audit.csv")
    assert os.path.exists(cont_path)
    with open(cont_path, "r", encoding="utf-8") as f:
        reader = list(csv.DictReader(f))
    assert len(reader) == 23
    natural_streams = [r for r in reader if r["recording_id"].startswith("P26-NAT")]
    assert len(natural_streams) == 17
    for r in natural_streams:
        assert r["continuity_demonstrated"] == "YES_UNBROKEN_FIELD_RECORDING"
        assert r["timestamp_gaps_detected"] == "NONE"

# 12. Test Exposure Accounting CSV
def test_12_exposure_accounting_csv():
    exp_path = os.path.join(REPORTS_DIR, "phase26_exposure_accounting.csv")
    assert os.path.exists(exp_path)
    with open(exp_path, "r", encoding="utf-8") as f:
        reader = list(csv.DictReader(f))
    assert len(reader) == 34  # 17 streams * 2 models
    p14_rows = [r for r in reader if r["detector"] == "Phase 14 Balanced"]
    p17_rows = [r for r in reader if r["detector"] == "Phase 17 Experimental"]
    assert len(p14_rows) == 17
    assert len(p17_rows) == 17
    gross_h_p14 = sum(float(r["gross_duration_hr"]) for r in p14_rows)
    assert abs(gross_h_p14 - 6.6460) < 0.001
    p14_alerts = sum(int(r["observed_alerts"]) for r in p14_rows)
    p17_alerts = sum(int(r["observed_alerts"]) for r in p17_rows)
    assert p14_alerts == 56
    assert p17_alerts == 51

# 13. Test Alert Event Log
def test_13_alert_event_log():
    log_path = os.path.join(REPORTS_DIR, "phase26_alert_event_log.csv")
    assert os.path.exists(log_path)
    with open(log_path, "r", encoding="utf-8") as f:
        reader = list(csv.DictReader(f))
    assert len(reader) == 107
    p14_count = sum(1 for r in reader if r["detector"] == "Phase 14 Balanced")
    p17_count = sum(1 for r in reader if r["detector"] == "Phase 17 Experimental")
    assert p14_count == 56
    assert p17_count == 51
    for r in reader:
        assert r["review_classification"] == "CONFIRMED_NON_TARGET"

# 14. Test Negative Audio Results
def test_14_negative_audio_results():
    res_path = os.path.join(REPORTS_DIR, "phase26_negative_audio_results.csv")
    assert os.path.exists(res_path)
    with open(res_path, "r", encoding="utf-8") as f:
        reader = list(csv.DictReader(f))
    assert len(reader) == 107
    p14_count = sum(1 for r in reader if r["detector"] == "Phase 14 Balanced")
    p17_count = sum(1 for r in reader if r["detector"] == "Phase 17 Experimental")
    assert p14_count == 56
    assert p17_count == 51

# 15. Test Matched Model Comparison Report
def test_15_matched_model_comparison_report():
    comp_path = os.path.join(REPORTS_DIR, "phase26_matched_model_comparison.md")
    assert os.path.exists(comp_path)
    with open(comp_path, "r", encoding="utf-8") as f:
        text = f.read()
    assert "W = 10.0, p = 0.125" in text
    assert "RETAIN AS BASELINE" in text
    assert "INCONCLUSIVE (REJECT PROMOTION)" in text

# 16. Test Statistical Analysis Report & Permutation p-value
def test_16_statistical_analysis_report():
    stat_path = os.path.join(REPORTS_DIR, "phase26_statistical_analysis.md")
    assert os.path.exists(stat_path)
    with open(stat_path, "r", encoding="utf-8") as f:
        text = f.read()
    assert "Garwood" in text
    assert "VMR > 8.3" in text or "VMR" in text
    assert "0.125" in text

# 17. Test Risk Register Limits Section
def test_17_risk_register_limitations():
    risk_path = os.path.join(REPORTS_DIR, "phase26_risk_and_limitation_register.md")
    assert os.path.exists(risk_path)
    with open(risk_path, "r", encoding="utf-8") as f:
        text = f.read()
    assert "NO Universal Urban Generalization" in text
    assert "NO Proof of Real-World Criminal Gunfire Detection" in text
    assert "NO Automated CAD or Dispatch Suitability" in text

# 18. Test Processing Manifest Accounting Values
def test_18_processing_manifest():
    manifest_path = os.path.join(REPORTS_DIR, "phase26_processing_manifest.json")
    assert os.path.exists(manifest_path)
    with open(manifest_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["benchmark_accounting"]["cumulative_gross_hours"] == 6.6460
    assert data["benchmark_accounting"]["new_phase26_gross_hours"] == 0.0000
    assert data["benchmark_accounting"]["phase14_observed_alerts"] == 56
    assert data["benchmark_accounting"]["phase17_observed_alerts"] == 51
    assert data["candidate_evaluations"]["candidate_a_aerosonicdb"]["access_status"] == "CONDITIONAL_ACCESS_PENDING"
    assert data["candidate_evaluations"]["candidate_b_isd"]["access_status"] == "REJECTED"

# 19. Test Mandatory Safety Banners in All Reports
def test_19_safety_banners():
    md_reports = [
        "phase26_final_report.md",
        "phase26_aerosonicdb_source_audit.md",
        "phase26_isd_source_audit.md",
        "phase26_source_shortlist.md",
        "phase26_negative_eligibility_report.md",
        "phase26_matched_model_comparison.md",
        "phase26_statistical_analysis.md",
        "phase26_risk_and_limitation_register.md"
    ]
    banner_snippet = "RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY"
    for r in md_reports:
        p = os.path.join(REPORTS_DIR, r)
        assert os.path.exists(p), f"Missing report: {r}"
        with open(p, "r", encoding="utf-8") as f:
            content = f.read()
        assert banner_snippet in content, f"Missing safety banner in {r}"

# 20. Test Model Role Terminology
def test_20_model_role_terminology():
    comp_path = os.path.join(REPORTS_DIR, "phase26_matched_model_comparison.md")
    with open(comp_path, "r", encoding="utf-8") as f:
        text = f.read()
    assert "DEFAULT_RESEARCH_BASELINE" in text
    assert "production baseline" not in text.lower()
