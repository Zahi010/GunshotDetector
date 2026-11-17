"""
Automated Test Suite for Phase 35 Audit Reproduction
MANDATORY SAFETY DESIGNATION:
RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY
This experimental acoustic machine-learning software is uncertified and must never
be deployed for autonomous emergency dispatch, tactical police response,
active-shooter alerting, automated evacuation, building lockdown, or life-critical
physical security. Safe recorded audio playback only; no live-fire testing.
"""

import os
import json
import hashlib
import pytest
import numpy as np
import pandas as pd
from pathlib import Path

WORKSPACE_ROOT = Path(r"E:\gunshot\gunshot")
REPORTS_DIR = WORKSPACE_ROOT / "reports"
DATA_DIR = WORKSPACE_ROOT / "data"

INDEPENDENCE_PHRASE = (
    "Four campaign-level clusters were available; full statistical independence could not be established from retained metadata."
)

def sha256_file(filepath):
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

# -----------------------------------------------------------------------------
# 1. Interval union arithmetic
# -----------------------------------------------------------------------------
def test_interval_union_arithmetic():
    """Verify interval union calculation, overlap merging, and boundary clipping."""
    import sys
    if str(WORKSPACE_ROOT) not in sys.path:
        sys.path.insert(0, str(WORKSPACE_ROOT))
    from scripts.reproduce_phase35_audit import merge_intervals, total_duration

    # Test 1: Disjoint intervals
    ivs1 = [(10.0, 12.0), (20.0, 22.0)]
    m1 = merge_intervals(ivs1, clip_max=100.0)
    assert m1 == [(10.0, 12.0), (20.0, 22.0)]
    assert total_duration(m1) == 4.0

    # Test 2: Overlapping intervals
    ivs2 = [(10.0, 13.0), (12.0, 15.0)]
    m2 = merge_intervals(ivs2, clip_max=100.0)
    assert m2 == [(10.0, 15.0)]
    assert total_duration(m2) == 5.0

    # Test 3: Contiguous / touching intervals
    ivs3 = [(10.0, 12.0), (12.0, 14.0)]
    m3 = merge_intervals(ivs3, clip_max=100.0)
    assert m3 == [(10.0, 14.0)]
    assert total_duration(m3) == 4.0

    # Test 4: Boundary clipping
    ivs4 = [(95.0, 105.0)]
    m4 = merge_intervals(ivs4, clip_max=100.0)
    assert m4 == [(95.0, 100.0)]
    assert total_duration(m4) == 5.0


# -----------------------------------------------------------------------------
# 2. Convention A and B definitions
# -----------------------------------------------------------------------------
def test_convention_definitions():
    """Verify Convention A and B definitions across the 287 alert rows."""
    df_ledger = pd.read_csv(REPORTS_DIR / "phase35_cooldown_interval_ledger.csv")
    assert len(df_ledger) == 287

    for _, row in df_ledger.iterrows():
        t_s = row["alert_timestamp_s"]
        ca_start = row["convention_a_cd_start_s"]
        ca_end = row["convention_a_cd_end_s"]
        ca_dur = row["convention_a_duration_s"]

        # Convention A start must equal alert timestamp
        assert abs(ca_start - t_s) < 1e-4

        # Convention A duration must be <= 2.0 seconds
        assert ca_dur <= 2.0 + 1e-4
        assert abs(ca_dur - (ca_end - ca_start)) < 1e-4

        # Convention B must be at least as long as Convention A
        cb_dur = row["convention_b_duration_s"]
        assert cb_dur >= ca_dur - 1e-4


# -----------------------------------------------------------------------------
# 3. Per-recording exposure
# -----------------------------------------------------------------------------
def test_per_recording_exposure():
    """Verify each recording has positive duration and valid cooldown bounds."""
    df_stream = pd.read_csv(REPORTS_DIR / "phase35_stream_exposure_reconciliation.csv")
    assert len(df_stream) == 46

    for _, row in df_stream.iterrows():
        dur_s = row["gross_duration_s"]
        ca_cd = row["conv_a_cooldown_s"]
        ca_el = row["conv_a_eligible_s"]
        cb_cd = row["conv_b_cooldown_s"]
        cb_el = row["conv_b_eligible_s"]

        assert dur_s > 0.0
        assert ca_cd >= 0.0
        assert cb_cd >= ca_cd - 1e-4

        # Exposure arithmetic: gross = cooldown + eligible
        assert abs(dur_s - (ca_cd + ca_el)) < 1e-4
        assert abs(dur_s - (cb_cd + cb_el)) < 1e-4

        # Eligible exposure must be strictly positive
        assert ca_el > 0.0
        assert cb_el > 0.0


# -----------------------------------------------------------------------------
# 4. Campaign exposure aggregation
# -----------------------------------------------------------------------------
def test_campaign_exposure_aggregation():
    """Verify that campaign aggregations equal stream sums exactly."""
    df_stream = pd.read_csv(REPORTS_DIR / "phase35_stream_exposure_reconciliation.csv")
    df_camp = pd.read_csv(REPORTS_DIR / "phase35_campaign_exposure_reconciliation.csv")

    for cid in ["CAMPAIGN-SOUTHAMPTON-EXP1", "CAMPAIGN-CHEW-MAGNA", "CAMPAIGN-BILBAO", "CAMPAIGN-ADELAIDE-AEROSONIC"]:
        camp_row = df_camp[df_camp["campaign_id"] == cid].iloc[0]
        sub_p14 = df_stream[(df_stream["campaign_id"] == cid) & (df_stream["detector"] == "Phase 14 Balanced")]
        sub_p17 = df_stream[(df_stream["campaign_id"] == cid) & (df_stream["detector"] == "Phase 17 Experimental")]

        # Stream count
        assert camp_row["stream_count"] == len(sub_p14)

        # Duration sum
        assert abs(camp_row["gross_duration_s"] - sub_p14["gross_duration_s"].sum()) < 1e-4

        # Alert counts
        assert camp_row["phase14_alerts"] == sub_p14["observed_alerts"].sum()
        assert camp_row["phase17_alerts"] == sub_p17["observed_alerts"].sum()

        # Cooldown exclusions
        assert abs(camp_row["phase14_conv_b_cd_s"] - sub_p14["conv_b_cooldown_s"].sum()) < 1e-4
        assert abs(camp_row["phase17_conv_b_cd_s"] - sub_p17["conv_b_cooldown_s"].sum()) < 1e-4


# -----------------------------------------------------------------------------
# 5. Corpus exposure aggregation
# -----------------------------------------------------------------------------
def test_corpus_exposure_aggregation():
    """Verify corpus-level totals match benchmark constants."""
    df_camp = pd.read_csv(REPORTS_DIR / "phase35_campaign_exposure_reconciliation.csv")
    corpus = df_camp[df_camp["campaign_id"] == "CUMULATIVE_BENCHMARK_TOTAL"].iloc[0]

    assert corpus["stream_count"] == 23
    assert abs(corpus["gross_duration_s"] - 45525.5755) < 1e-4
    assert abs(corpus["gross_duration_hr"] - 12.6460) < 1e-3

    assert corpus["phase14_alerts"] == 128
    assert corpus["phase17_alerts"] == 159

    # Convention B exclusions
    assert abs(corpus["phase14_conv_b_cd_s"] - 453.92) < 1e-2
    assert abs(corpus["phase17_conv_b_cd_s"] - 6385.20) < 1e-2


# -----------------------------------------------------------------------------
# 6. Eligible exposure calculations
# -----------------------------------------------------------------------------
def test_eligible_exposure_calculations():
    """Verify eligible exposure is never negative and properly computed."""
    df_rates = pd.read_csv(REPORTS_DIR / "phase35_final_rate_table.csv")

    for _, row in df_rates.iterrows():
        g_s = row["gross_exposure_s"]
        ca_ex = row["conv_a_excluded_s"]
        ca_el = row["conv_a_eligible_s"]
        cb_ex = row["conv_b_excluded_s"]
        cb_el = row["conv_b_eligible_s"]

        assert ca_el > 0.0, f"Non-positive Conv A eligible exposure for {row['identifier']}"
        assert cb_el > 0.0, f"Non-positive Conv B eligible exposure for {row['identifier']}"
        assert abs(g_s - (ca_ex + ca_el)) < 1e-4
        assert abs(g_s - (cb_ex + cb_el)) < 1e-4


# -----------------------------------------------------------------------------
# 7. Rate calculations
# -----------------------------------------------------------------------------
def test_rate_calculations():
    """Verify unrounded rate calculations match (alerts / eligible_hr)."""
    df_rates = pd.read_csv(REPORTS_DIR / "phase35_final_rate_table.csv")

    for _, row in df_rates.iterrows():
        k = row["alert_count"]
        g_hr = row["gross_exposure_hr"]
        ca_hr = row["conv_a_eligible_hr"]
        cb_hr = row["conv_b_eligible_hr"]

        expected_gross = (k / g_hr) if g_hr > 0 else 0.0
        expected_ca = (k / ca_hr) if ca_hr > 0 else 0.0
        expected_cb = (k / cb_hr) if cb_hr > 0 else 0.0

        assert abs(row["gross_alert_rate_per_hr"] - expected_gross) < 1e-4
        assert abs(row["conv_a_rate_per_hr"] - expected_ca) < 1e-4
        assert abs(row["conv_b_rate_per_hr"] - expected_cb) < 1e-4


# -----------------------------------------------------------------------------
# 8. Source-level alert count consistency
# -----------------------------------------------------------------------------
def test_source_level_alert_count_consistency():
    """Verify exact alert counts across ledger and campaign partitions."""
    df_ledger = pd.read_csv(REPORTS_DIR / "phase35_cooldown_interval_ledger.csv")
    df_gt = pd.read_csv(REPORTS_DIR / "phase35_alert_ground_truth_audit.csv")

    assert len(df_ledger) == 287
    assert len(df_gt) == 287

    p14_count = (df_ledger["detector"] == "Phase 14 Balanced").sum()
    p17_count = (df_ledger["detector"] == "Phase 17 Experimental").sum()

    assert p14_count == 128
    assert p17_count == 159

    # Campaign-specific counts
    camp_counts_p14 = df_ledger[df_ledger["detector"] == "Phase 14 Balanced"]["campaign_id"].value_counts().to_dict()
    camp_counts_p17 = df_ledger[df_ledger["detector"] == "Phase 17 Experimental"]["campaign_id"].value_counts().to_dict()

    assert camp_counts_p14["CAMPAIGN-SOUTHAMPTON-EXP1"] == 24
    assert camp_counts_p14["CAMPAIGN-BILBAO"] == 32
    assert camp_counts_p14["CAMPAIGN-ADELAIDE-AEROSONIC"] == 72

    assert camp_counts_p17["CAMPAIGN-SOUTHAMPTON-EXP1"] == 22
    assert camp_counts_p17["CAMPAIGN-BILBAO"] == 29
    assert camp_counts_p17["CAMPAIGN-ADELAIDE-AEROSONIC"] == 108


# -----------------------------------------------------------------------------
# 9. Ground-truth label categories
# -----------------------------------------------------------------------------
def test_ground_truth_label_categories():
    """Verify that alert categories strictly adhere to audit definitions."""
    df_gt = pd.read_csv(REPORTS_DIR / "phase35_alert_ground_truth_audit.csv")

    # Categories must be valid
    allowed_categories = {
        "CONFIRMED_NON_TARGET",
        "REVIEWED_NON_TARGET",
        "UNANNOTATED_BACKGROUND",
        "POSSIBLE_TARGET",
        "UNKNOWN"
    }
    assert set(df_gt["classification_category"].unique()).issubset(allowed_categories)

    # 107 European alerts must be REVIEWED_NON_TARGET
    reviewed = df_gt[df_gt["classification_category"] == "REVIEWED_NON_TARGET"]
    assert len(reviewed) == 107
    assert set(reviewed["campaign_id"].unique()) == {"CAMPAIGN-SOUTHAMPTON-EXP1", "CAMPAIGN-BILBAO"}

    # 180 Adelaide alerts must be UNANNOTATED_BACKGROUND
    unannotated = df_gt[df_gt["classification_category"] == "UNANNOTATED_BACKGROUND"]
    assert len(unannotated) == 180
    assert set(unannotated["campaign_id"].unique()) == {"CAMPAIGN-ADELAIDE-AEROSONIC"}

    # Zero unverified claims of CONFIRMED_NON_TARGET
    assert (df_gt["classification_category"] == "CONFIRMED_NON_TARGET").sum() == 0


# -----------------------------------------------------------------------------
# 10. Campaign independence qualification
# -----------------------------------------------------------------------------
def test_campaign_independence_qualification():
    """Verify that the required formal independence qualification phrase is present."""
    df_indep = pd.read_csv(REPORTS_DIR / "phase35_campaign_independence_evidence.csv")
    assert len(df_indep) == 4

    # Every campaign row must include the mandatory qualification phrase
    for phrase in df_indep["mandatory_independence_qualification"]:
        assert phrase == INDEPENDENCE_PHRASE

    # Verify report files contain the exact phrase
    for report_name in ["phase35_campaign_independence_qualification.md", "phase35_final_report.md"]:
        report_path = REPORTS_DIR / report_name
        assert report_path.exists()
        content = report_path.read_text(encoding="utf-8")
        assert INDEPENDENCE_PHRASE in content


# -----------------------------------------------------------------------------
# 11. Historical value reconciliation
# -----------------------------------------------------------------------------
def test_historical_value_reconciliation():
    """Verify resolution of the 10-second discrepancy between 6395.20s and 6385.20s."""
    df_camp = pd.read_csv(REPORTS_DIR / "phase35_campaign_exposure_reconciliation.csv")
    corpus = df_camp[df_camp["campaign_id"] == "CUMULATIVE_BENCHMARK_TOTAL"].iloc[0]

    true_p17_conv_b = corpus["phase17_conv_b_cd_s"]
    prompt_transposed_p17 = corpus["prompt_transposed_p17_conv_b_s"]
    delta = corpus["transposition_error_delta_s"]

    # True Phase 17 exclusion
    assert abs(true_p17_conv_b - 6385.20) < 1e-2

    # Prompt transposed sum
    assert abs(prompt_transposed_p17 - 6395.20) < 1e-2

    # Delta must be exactly 10.00 seconds
    assert abs(delta - 10.00) < 1e-2

    # Verify that Phase 28 and Phase 31 historical records match 6385.20s
    df_p28 = pd.read_csv(REPORTS_DIR / "phase28_exposure_reproduction.csv")
    df_p31 = pd.read_csv(REPORTS_DIR / "phase31_exposure_reconciliation.csv")

    p28_p17_b = df_p28[df_p28["detector"] == "Phase 17 Experimental"]["cd_cluster_extended_s"].sum()
    p31_p17_b = df_p31[df_p31["detector"] == "Phase 17 Experimental"]["conv_b_cooldown_s"].sum()

    assert abs(p28_p17_b - 6385.20) < 1e-2
    assert abs(p31_p17_b - 6385.20) < 1e-2


# -----------------------------------------------------------------------------
# 12. Archive manifest integrity
# -----------------------------------------------------------------------------
def test_archive_manifest_integrity():
    """Verify that all artifacts listed in phase35_artifact_manifest.json exist and match hashes."""
    manifest_path = REPORTS_DIR / "phase35_artifact_manifest.json"
    assert manifest_path.exists()

    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    assert manifest["safety_designation"] == "RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY"
    assert manifest["benchmark_summary"]["streams"] == 23
    assert manifest["benchmark_summary"]["campaigns"] == 4
    assert manifest["benchmark_summary"]["phase14_alerts"] == 128
    assert manifest["benchmark_summary"]["phase17_alerts"] == 159

    artifacts = manifest["artifacts"]
    assert len(artifacts) >= 12

    for name, info in artifacts.items():
        if name == "phase35_test_execution_log.txt":
            continue
        file_path = WORKSPACE_ROOT / info["relative_path"]
        assert file_path.exists(), f"Artifact file {file_path} does not exist"
        assert file_path.stat().st_size == info["size_bytes"]
        computed_hash = sha256_file(file_path)
        assert computed_hash == info["sha256"], f"Hash mismatch for {name}: {computed_hash} != {info['sha256']}"
