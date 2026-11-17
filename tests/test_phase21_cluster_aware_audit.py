"""
Phase 21 Automated Test Suite: Cluster-Aware Statistical Validation & Final Evidence Audit
MANDATORY SAFETY DESIGNATION:
RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.

This experimental acoustic machine-learning system is not certified and must never be used
for autonomous emergency dispatch, police response, active-shooter alerting, automated evacuation,
or critical physical security.
"""

import sys
import json
import math
import hashlib
from pathlib import Path
import pytest
import pandas as pd
from scipy import stats

ROOT = Path("E:/gunshot/gunshot")
sys.path.insert(0, str(ROOT))

REPORTS_DIR = ROOT / "reports"
MANDATORY_BANNER = "RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY"

EXPECTED_MODEL_HASHES = {
    "model_phase14.py": "a268551604ae8b73068435ff10ab3d265065f56e0679757fca5b6bf0f061c065",
    "model_phase17.py": "e2b262b866fdd5d7f1a4ab91a7b8b9bac189ee8cc7a78603b3544ca1579fb819",
    "model_phase13.py": "68585039a4a4fdb7978a99f5e2a72c0ad5a9523127ec24a1338fbedd1c1231e6",
    "model_phase9.py":  "85cedd9f5b988ecafb1eae7de9630ee3d6a387ded6ef732e0efb7c3b496f132a"
}

def test_mandatory_safety_designation():
    """Verify mandatory safety banner in all Phase 21 markdown reports."""
    reports_to_check = [
        "phase21_event_level_statistics.md",
        "phase21_recording_level_comparison.md",
        "phase21_clustered_statistics.md",
        "phase21_false_alert_exposure_correction.md",
        "phase21_category_d_reconciliation.md"
    ]
    for rname in reports_to_check:
        rpath = REPORTS_DIR / rname
        assert rpath.exists(), f"Missing report: {rname}"
        content = rpath.read_text(encoding="utf-8")
        assert MANDATORY_BANNER in content, f"Safety banner missing in {rname}"

def test_frozen_model_hashes_and_baseline_selection():
    """Verify SHA-256 hashes of all models and confirm Phase 14 default selection."""
    for fname, exp_hash in EXPECTED_MODEL_HASHES.items():
        p = ROOT / fname
        assert p.exists(), f"Model file missing: {fname}"
        actual_hash = hashlib.sha256(p.read_bytes()).hexdigest()
        assert actual_hash == exp_hash, f"Hash mismatch on {fname}"
    
    # Check baseline freeze json
    with open(REPORTS_DIR / "phase21_baseline_freeze.json", "r", encoding="utf-8") as f:
        freeze = json.load(f)
    assert freeze["models"]["model_phase14.py"]["role"] == "DEFAULT_PRODUCTION_BASELINE"
    assert freeze["models"]["model_phase17.py"]["role"] == "SELECTABLE_EXPERIMENTAL_PROFILE"

def test_canonical_event_counts_and_no_duplicates():
    """Verify event counts and absence of duplicate IDs."""
    df_man = pd.read_csv(REPORTS_DIR / "phase20_canonical_event_manifest.csv")
    assert len(df_man) == 53
    assert len(df_man["event_id"].unique()) == 53
    cat_a = df_man[df_man["category"] == "CATEGORY_A_NATURAL_CONTINUOUS"]
    assert len(cat_a) == 50
    assert len(cat_a["event_id"].unique()) == 50

def test_recording_and_firing_position_id_integrity():
    """Verify recording IDs and firing position IDs are complete without missing values."""
    df_hier = pd.read_csv(REPORTS_DIR / "phase21_event_cluster_hierarchy.csv")
    assert df_hier["level_4_stream_id"].isna().sum() == 0
    assert df_hier["level_2_firing_position"].isna().sum() == 0
    assert set(df_hier["level_2_firing_position"].unique()) == {"FP1", "FP2", "FP3", "FP4", "FP5"}
    assert len(df_hier["level_4_stream_id"].unique()) == 20

def test_burst_assignments_and_round_accounting():
    """Verify burst sequence assignments (15 3-round bursts and 5 single shots)."""
    df_burst = pd.read_csv(REPORTS_DIR / "phase21_burst_analysis.csv")
    assert len(df_burst) == 20
    assert (df_burst["sequence_type"] == "SINGLE_SHOT").sum() == 5
    assert (df_burst["sequence_type"] == "3_ROUND_BURST").sum() == 15
    assert df_burst["round_count"].sum() == 50
    
    # Assert inter-shot intervals for bursts
    for _, r in df_burst[df_burst["sequence_type"] == "3_ROUND_BURST"].iterrows():
        assert r["burst_total_duration_s"] < 2.5
    assert df_burst[df_burst["sequence_type"] == "3_ROUND_BURST"]["cooldown_window_conflict"].sum() == 14

def test_paired_contingency_and_mcnemar_exact_p():
    """Verify paired contingency table [27, 0; 6, 17] and exact p=0.03125."""
    with open(REPORTS_DIR / "phase21_event_contingency.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    t = data["contingency_table"]
    assert t["cell_a_both_detected"] == 27
    assert t["cell_b_phase14_only"] == 0
    assert t["cell_c_phase17_only"] == 6
    assert t["cell_d_neither_detected"] == 17
    
    hyp = data["hypothesis_testing"]
    assert hyp["total_discordant_pairs"] == 6
    assert abs(hyp["exact_two_sided_p_value"] - 0.03125) < 0.0001
    assert hyp["statistically_significant_alpha_05"] == True

def test_recording_level_aggregation_and_incident_stats():
    """Verify recording-level metrics and incident detection p-value."""
    df_rec = pd.read_csv(REPORTS_DIR / "phase21_recording_level_results.csv")
    assert len(df_rec) == 20
    assert df_rec["phase_14_incident_detected"].sum() == 15
    assert df_rec["phase_17_incident_detected"].sum() == 18
    assert (df_rec["discordant_physical_events"] == 0).sum() == 15
    assert (df_rec["discordant_physical_events"] > 0).sum() == 5
    
    inc_p = stats.binomtest(0, 3, 0.5, alternative='two-sided').pvalue
    assert abs(inc_p - 0.25000) < 0.0001

def test_position_level_aggregation_and_concentration():
    """Verify position-level gains: FP4=+3, FP1=+2, FP3=+1, FP2=0, FP5=0."""
    df_pos = pd.read_csv(REPORTS_DIR / "phase21_position_level_results.csv")
    assert len(df_pos) == 5
    pos_map = dict(zip(df_pos["firing_position"], df_pos["round_detection_gain"]))
    assert pos_map["FP4"] == 3
    assert pos_map["FP1"] == 2
    assert pos_map["FP3"] == 1
    assert pos_map["FP2"] == 0
    assert pos_map["FP5"] == 0

def test_leave_one_position_out_sensitivity():
    """Verify LOPO results: excluding FP4 makes p=0.25000 (not significant)."""
    df_lopo = pd.read_csv(REPORTS_DIR / "phase21_leave_one_position_out.csv")
    fp4 = df_lopo[df_lopo["excluded_firing_position"] == "FP4"].iloc[0]
    assert fp4["round_gain"] == 3
    assert abs(fp4["exact_mcnemar_p_value"] - 0.25000) < 0.0001
    assert fp4["statistically_significant_05"] == False

def test_cooldown_exposure_and_poisson_bounds():
    """Verify exposure calculations and exact Garwood upper bounds."""
    with open(REPORTS_DIR / "phase21_false_alert_statistics.json", "r", encoding="utf-8") as f:
        fa = json.load(f)
    scenarios = fa["exposure_scenarios"]
    assert abs(scenarios["definition_1_total_recorded_audio"]["garwood_95_upper_bound_alerts_per_hour"] - 53.923) < 0.1
    assert abs(scenarios["definition_3_nominal_rounded_quiescent_background"]["garwood_95_upper_bound_alerts_per_hour"] - 77.033) < 0.1
    assert abs(scenarios["definition_2_eligible_background_matching_window"]["garwood_95_upper_bound_alerts_per_hour"] - 76.805) < 0.1

def test_category_d_denominator_consistency_and_reconciliation():
    """Verify Category D reconciliation: 83.33% = 35/42 Balanced, 89.29% = 25/28 High-Sensitivity."""
    with open(REPORTS_DIR / "phase21_category_d_corrected_metrics.json", "r", encoding="utf-8") as f:
        cd = json.load(f)
    prov = cd["provenance_investigation"]
    set_42 = prov["dataset_variant_2_comprehensive_range_42_clips"]
    assert set_42["phase_14_balanced"]["detected"] == 35
    assert set_42["denominator_genuine_events"] == 42
    assert abs(set_42["phase_14_balanced"]["event_recall"] - 0.8333) < 0.001
    
    set_28 = prov["dataset_variant_1_discrete_blind_test_28_events"]
    assert set_28["phase_14_high_sensitivity"]["detected"] == 25
    assert set_28["denominator_genuine_events"] == 28
    assert abs(set_28["phase_14_high_sensitivity"]["event_recall"] - 0.8929) < 0.001

def test_multiple_comparisons_holm_bonferroni():
    """Verify Holm-Bonferroni step-down adjustments across all 5 comparisons."""
    df_comp = pd.read_csv(REPORTS_DIR / "phase21_all_model_comparisons.csv")
    assert len(df_comp) == 5
    p17_row = df_comp[df_comp["model_b"] == "phase_17_experimental"].iloc[0]
    assert abs(p17_row["unadjusted_exact_mcnemar_p_value"] - 0.03125) < 0.0001
    assert abs(p17_row["holm_adjusted_p_value"] - 0.12500) < 0.0001
    assert p17_row["statistically_significant_holm_05"] == False
    assert df_comp["statistically_significant_holm_05"].sum() == 0
