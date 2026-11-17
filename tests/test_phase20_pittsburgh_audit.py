"""
Phase 20 Automated Test Suite: Pittsburgh Forensic Audit, Event-Level Revalidation & Generalization Limits

MANDATORY SAFETY DESIGNATION:
RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.
This experimental acoustic machine-learning system is not certified and must never be used
for autonomous emergency dispatch, police response, active-shooter alerting, automated evacuation,
or critical physical security.
"""

import sys
import json
import hashlib
from pathlib import Path
import pytest
import pandas as pd
from scipy import stats

ROOT = Path("E:/gunshot/gunshot")
sys.path.insert(0, str(ROOT))

REPORTS_DIR = ROOT / "reports"
DATA_DIR = ROOT / "data" / "phase19_independent_positive"

MANDATORY_BANNER = "RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY"

# Expected Frozen SHA-256 Checksums
EXPECTED_MODEL_HASHES = {
    "model_phase14.py": "a268551604ae8b73068435ff10ab3d265065f56e0679757fca5b6bf0f061c065",
    "model_phase17.py": "e2b262b866fdd5d7f1a4ab91a7b8b9bac189ee8cc7a78603b3544ca1579fb819",
    "model_phase13.py": "68585039a4a4fdb7978a99f5e2a72c0ad5a9523127ec24a1338fbedd1c1231e6",
    "model_phase9.py":  "85cedd9f5b988ecafb1eae7de9630ee3d6a387ded6ef732e0efb7c3b496f132a"
}

def test_mandatory_safety_designation():
    """Verify mandatory safety banner in all Phase 20 reports."""
    reports_to_check = [
        "phase20_session_independence_audit.md",
        "phase20_event_accounting_audit.md",
        "phase20_mcnemar_audit.md",
        "phase20_false_alert_exposure_audit.md",
        "phase20_cross_category_interpretation.md",
        "phase20_dataset_source_verification.md",
        "phase20_recording_transformation_lineage.md",
        "phase20_license_attribution.md"
    ]
    for rname in reports_to_check:
        rpath = REPORTS_DIR / rname
        assert rpath.exists(), f"Missing report: {rname}"
        with open(rpath, "r", encoding="utf-8") as f:
            content = f.read()
        assert MANDATORY_BANNER in content, f"Safety designation missing in {rname}"

def test_baseline_model_checksums():
    """Verify SHA-256 digests of all frozen baseline models."""
    for model_name, exp_hash in EXPECTED_MODEL_HASHES.items():
        mpath = ROOT / model_name
        assert mpath.exists(), f"Model file missing: {model_name}"
        with open(mpath, "rb") as f:
            actual_hash = hashlib.sha256(f.read()).hexdigest()
        assert actual_hash == exp_hash, f"Hash mismatch on {model_name}"

def test_canonical_event_and_recording_accounting():
    """Verify exact 53-event and 23-stream accounting reconciliation."""
    manifest_path = REPORTS_DIR / "phase20_canonical_event_manifest.csv"
    accounting_path = REPORTS_DIR / "phase20_event_accounting.json"
    assert manifest_path.exists()
    assert accounting_path.exists()
    
    df = pd.read_csv(manifest_path)
    with open(accounting_path, "r", encoding="utf-8") as f:
        acct = json.load(f)
        
    assert len(df) == 53
    assert len(df["event_id"].unique()) == 53
    assert acct["total_canonical_events"] == 53
    assert acct["total_positive_recordings"] == 23
    assert acct["category_a_events"] == 50
    assert acct["category_b_events"] == 3
    assert acct["category_a_recordings"] == 20
    assert acct["category_b_recordings"] == 3
    assert acct["accounting_reconciliation_verdict"] == "PERFECT_RECONCILIATION_ZERO_DISCREPANCIES"

def test_category_a_continuity_and_provenance():
    """Verify 20-recording unbroken temporal continuity and 1-to-1 resampling."""
    cont_path = REPORTS_DIR / "phase20_continuity_audit.csv"
    assert cont_path.exists()
    df = pd.read_csv(cont_path)
    
    assert len(df) == 20
    for _, r in df.iterrows():
        assert r["duration_difference_seconds"] == 0.0
        assert r["continuity_classification"] == "RESAMPLED_OR_NORMALIZED_COPY"
        assert r["parent_source_classification"] == "ORIGINAL_UNBROKEN_SENSOR_RECORDING"
        assert r["concatenation_detected"] == False
        assert r["looping_detected"] == False
        assert r["crossfade_detected"] == False

def test_firing_position_lineage_and_arbitrary_origins():
    """Verify that all 5 firing positions belong to a single campaign with arbitrary local origins."""
    geo_path = REPORTS_DIR / "phase20_geographic_lineage.csv"
    assert geo_path.exists()
    df = pd.read_csv(geo_path)
    
    assert len(df) == 5
    assert set(df["firing_position_id"].tolist()) == {"FP1", "FP2", "FP3", "FP4", "FP5"}
    for _, r in df.iterrows():
        assert r["campaign_id"] == "PittsburghPA_DQV_2018-12-18"
        assert r["campaign_independence_classification"] == "SINGLE_MUNICIPAL_VALIDATION_CAMPAIGN"
        assert r["inter_position_distance_computable"] == False
        assert r["physical_rounds_selected"] == 10

def test_model_detection_counts_category_a():
    """Verify frozen detector detection counts across the 50 Category A events."""
    manifest_path = REPORTS_DIR / "phase20_canonical_event_manifest.csv"
    df = pd.read_csv(manifest_path)
    cat_a = df[df["category"] == "CATEGORY_A_NATURAL_CONTINUOUS"]
    
    assert int(cat_a["phase_14_balanced_detected"].sum()) == 27
    assert int(cat_a["phase_14_hp_detected"].sum()) == 24
    assert int(cat_a["phase_14_hs_detected"].sum()) == 22
    assert int(cat_a["phase_17_experimental_detected"].sum()) == 33
    assert int(cat_a["phase_9_balanced_detected"].sum()) == 28
    assert int(cat_a["phase_13_balanced_detected"].sum()) == 16

def test_paired_mcnemar_phase14_vs_phase17():
    """Verify paired McNemar 2x2 contingency table and exact p-value."""
    paired_path = REPORTS_DIR / "phase20_paired_model_comparison.csv"
    assert paired_path.exists()
    df = pd.read_csv(paired_path)
    row = df[df["model_b"] == "phase_17_experimental"].iloc[0]
    
    assert row["both_detected"] == 27
    assert row["model_a_only"] == 0
    assert row["model_b_only"] == 6
    assert row["neither_detected"] == 17
    assert row["total_discordant"] == 6
    assert abs(row["exact_mcnemar_p_value"] - 0.03125) < 0.0001
    assert row["statistically_significant_05"] == True

def test_false_alert_exposure_and_poisson_bounds():
    """Verify false-alert exposure duration and Poisson upper confidence bounds."""
    t_total = 200.0
    t_quiescent = 140.0
    garwood_total_rate = (2.99573 / t_total) * 3600.0
    garwood_quiescent_rate = (2.99573 / t_quiescent) * 3600.0
    
    assert abs(garwood_total_rate - 53.92) < 0.1
    assert abs(garwood_quiescent_rate - 77.03) < 0.1

def test_incident_vs_round_recall():
    """Verify incident-level recall vs round-level recall on Category A."""
    # Phase 14 Balanced: 27/50 (54%) rounds, 15/20 (75%) incidents
    # Phase 17 Exp: 33/50 (66%) rounds, 18/20 (90%) incidents
    acct_path = REPORTS_DIR / "phase20_event_accounting.json"
    with open(acct_path, "r", encoding="utf-8") as f:
        acct = json.load(f)
    
    assert acct["category_a_model_detections"]["phase_14_balanced"]["detected"] == 27
    assert acct["category_a_model_detections"]["phase_17_experimental"]["detected"] == 33

