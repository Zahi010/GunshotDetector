"""
Phase 31 Reproduction and Validation Test Suite
MANDATORY SAFETY DESIGNATION:
RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.

Independent verification of all Phase 31 findings, including:
1. Frozen baseline model checksums and historical archive integrity.
2. Master recording registry reconciliation (23 streams, 4 campaigns, 12.646h).
3. Phase 17 state-machine defect confirmation (Tests A, B, D fail on P17).
4. Phase 14 baseline state-machine correctness (Tests A-E pass on P14).
5. Experimental candidate patch verification (Tests A-E pass on candidate).
6. Animal suppression parameter disambiguation and causal counterfactuals.
7. Rebuilt statistical analysis (Wilcoxon, Sign test, LOCO subsets).
8. Cooldown exposure accounting under both conventions.
"""

import sys
import os
import json
import hashlib
import zipfile
from pathlib import Path
import pytest
import pandas as pd
import numpy as np
from scipy import stats

ROOT = Path("E:/gunshot/gunshot")
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "experiments/phase31"))

from model_phase14 import merge_phase14_events
from model_phase17 import merge_phase17_events
import model_phase17_state_reset_candidate as candidate

REPORTS_DIR = ROOT / "reports"


# =============================================================================
# 1. BASELINE FREEZE & ARCHIVE INTEGRITY TESTS
# =============================================================================
def test_frozen_model_hashes():
    """Verify all frozen detector model checksums match historical baseline."""
    expected = {
        "model_phase14.py": ("a268551604ae8b73068435ff10ab3d265065f56e0679757fca5b6bf0f061c065", 23340),
        "model_phase17.py": ("e2b262b866fdd5d7f1a4ab91a7b8b9bac189ee8cc7a78603b3544ca1579fb819", 29067),
        "model_phase13.py": ("68585039a4a4fdb7978a99f5e2a72c0ad5a9523127ec24a1338fbedd1c1231e6", 22252),
        "model_phase9.py":  ("85cedd9f5b988ecafb1eae7de9630ee3d6a387ded6ef732e0efb7c3b496f132a", 17719)
    }
    for fname, (exp_hash, exp_size) in expected.items():
        fpath = ROOT / fname
        assert fpath.exists(), f"Missing file: {fname}"
        assert fpath.stat().st_size == exp_size, f"Size mismatch on {fname}"
        with open(fpath, "rb") as f:
            h = hashlib.sha256(f.read()).hexdigest()
        assert h == exp_hash, f"Hash mismatch on {fname}"


def test_historical_release_archives():
    """Verify release archives exist, match SHA-256 hashes, and pass testzip()."""
    archives = {
        "gunshot_detection_phase31.zip": ("92a4f4d9882d0d69edf1cacc390244ef480fea09a1bc80351787297c0e361c47", 4564376),
        "gunshot_detection_phase30.zip": ("a50cc30c13f840f1d68cb111b868242562262e979d9b211d902b6573ab14ada4", 5451607),
        "gunshot_detection_phase29.zip": ("23a3f8af3dc74db6bc71b0babbc813bb0e96d1bbd4ca2001cb508b8756081dd5", 4593850),
        "gunshot_detection_phase28.zip": ("e6505e3597b406541efb005f1d69432653cbfc5603843695fdfd66af01324a72", 4586167)
    }
    for fname, (exp_hash, exp_size) in archives.items():
        p = Path("E:/gunshot") / fname
        assert p.exists(), f"Missing archive: {fname}"
        assert p.stat().st_size == exp_size, f"Size mismatch on {fname}"
        with open(p, "rb") as f:
            h = hashlib.sha256(f.read()).hexdigest()
        assert h == exp_hash, f"Hash mismatch on archive {fname}"
        with zipfile.ZipFile(p, "r") as zf:
            bad = zf.testzip()
            assert bad is None, f"Corrupted file in {fname}: {bad}"


def test_experimental_candidate_hash():
    """Verify experimental candidate model exists and has correct hash."""
    cand_path = ROOT / "experiments/phase31/model_phase17_state_reset_candidate.py"
    assert cand_path.exists(), "Candidate patch file does not exist"
    assert cand_path.stat().st_size == 29718
    with open(cand_path, "rb") as f:
        h = hashlib.sha256(f.read()).hexdigest()
    assert h == "c144b917b56532787e2a9198f2cad4a77dc2095b57962f31d11d250a4d5d9ea5"


# =============================================================================
# 2. PROVENANCE RECONCILIATION & MASTER REGISTRY TESTS
# =============================================================================
def test_master_recording_registry():
    """Verify master recording registry has 23 streams and correct properties."""
    df = pd.read_csv(REPORTS_DIR / "phase31_recording_master_registry.csv")
    assert len(df) == 23, f"Expected 23 recordings, got {len(df)}"
    assert len(df["recording_id"].unique()) == 23, "Duplicate recording_id found"
    assert len(df["sha256"].unique()) == 23, "Duplicate audio sha256 found"

    # Campaign counts
    c_counts = df["campaign_id"].value_counts().to_dict()
    assert c_counts["CAMPAIGN-RPISOUND-UK"] == 10
    assert c_counts["CAMPAIGN-CHEWMAGNA-UK"] == 1
    assert c_counts["CAMPAIGN-BILBAO-ES"] == 6
    assert c_counts["CAMPAIGN-AEROSONIC-AU"] == 6

    # Gross duration
    assert abs(df["duration_seconds"].sum() - 45525.575) < 0.001
    assert abs(df["duration_hours"].sum() - 12.646) < 0.002


def test_alert_reconciliation_totals():
    """Verify alert reconciliation totals match exactly across phases."""
    df = pd.read_csv(REPORTS_DIR / "phase31_alert_reconciliation.csv")
    assert len(df) == 23
    assert df["p14_alerts"].sum() == 128
    assert df["p17_alerts"].sum() == 159
    assert (df["p14_alerts"] - df["p17_alerts"]).sum() == -31

    # Campaign splits
    grp = df.groupby("campaign_id")[["p14_alerts", "p17_alerts"]].sum()
    assert grp.loc["CAMPAIGN-RPISOUND-UK", "p14_alerts"] == 24
    assert grp.loc["CAMPAIGN-RPISOUND-UK", "p17_alerts"] == 22
    assert grp.loc["CAMPAIGN-CHEWMAGNA-UK", "p14_alerts"] == 0
    assert grp.loc["CAMPAIGN-CHEWMAGNA-UK", "p17_alerts"] == 0
    assert grp.loc["CAMPAIGN-BILBAO-ES", "p14_alerts"] == 32
    assert grp.loc["CAMPAIGN-BILBAO-ES", "p17_alerts"] == 29
    assert grp.loc["CAMPAIGN-AEROSONIC-AU", "p14_alerts"] == 72
    assert grp.loc["CAMPAIGN-AEROSONIC-AU", "p17_alerts"] == 108


def test_exposure_reconciliation_metrics():
    """Verify exposure calculations under Conventions A and B."""
    df = pd.read_csv(REPORTS_DIR / "phase31_exposure_reconciliation.csv")
    assert len(df) == 46  # 23 recordings x 2 detectors

    p14 = df[df["detector"] == "Phase 14 Balanced"]
    p17 = df[df["detector"] == "Phase 17 Experimental"]

    assert abs(p14["conv_a_cooldown_s"].sum() - 255.84) < 0.01
    assert abs(p17["conv_a_cooldown_s"].sum() - 316.56) < 0.01
    assert abs(p14["conv_b_cooldown_s"].sum() - 453.92) < 0.01
    assert abs(p17["conv_b_cooldown_s"].sum() - 6385.20) < 0.01


# =============================================================================
# 3. STATE-MACHINE REGRESSION TESTS (TESTS A THROUGH E)
# =============================================================================
def test_regression_test_a_isolated_spike():
    """Test A: Isolated qualifying spike must emit 0 alerts."""
    wins = [
        {"start_time": 0.0, "end_time": 0.975, "score": 0.78},
        {"start_time": 0.48, "end_time": 1.455, "score": 0.10},
        {"start_time": 0.96, "end_time": 1.935, "score": 0.10}
    ]
    p14_ev = merge_phase14_events(wins, 0.75, 0.88, 0.48, 2, 2.0)
    p17_ev = merge_phase17_events(wins, 0.75, 0.88, 0.48, 2, 2.0)
    cand_ev = candidate.merge_phase17_events(wins, 0.75, 0.88, 0.48, 2, 2.0)

    assert len(p14_ev) == 0, "Phase 14 failed Test A"
    assert len(p17_ev) == 1, "Phase 17 expected to exhibit defect (1 alert emitted on EOF flush)"
    assert len(cand_ev) == 0, "Candidate patch failed Test A"


def test_regression_test_b_unrelated_spikes_across_gap():
    """Test B: Unrelated spikes across 100s gap must not merge."""
    wins = [
        {"start_time": 0.0, "end_time": 0.975, "score": 0.78},
        {"start_time": 0.48, "end_time": 1.455, "score": 0.10},
        {"start_time": 0.96, "end_time": 1.935, "score": 0.10},
        {"start_time": 100.0, "end_time": 100.975, "score": 0.78},
        {"start_time": 100.48, "end_time": 101.455, "score": 0.10},
        {"start_time": 100.96, "end_time": 101.935, "score": 0.10}
    ]
    p14_ev = merge_phase14_events(wins, 0.75, 0.88, 0.48, 2, 2.0)
    p17_ev = merge_phase17_events(wins, 0.75, 0.88, 0.48, 2, 2.0)
    cand_ev = candidate.merge_phase17_events(wins, 0.75, 0.88, 0.48, 2, 2.0)

    assert len(p14_ev) == 0, "Phase 14 failed Test B"
    assert len(p17_ev) == 1, "Phase 17 expected to exhibit defect (merged spikes across 100s)"
    assert p17_ev[0]["duration"] > 50.0, "Phase 17 did not synthesize multi-second event"
    assert len(cand_ev) == 0, "Candidate patch failed Test B"


def test_regression_test_c_consecutive_confirmation():
    """Test C: Consecutive 2-window confirmation must emit 1 alert across all."""
    wins = [
        {"start_time": 0.0, "end_time": 0.975, "score": 0.78},
        {"start_time": 0.48, "end_time": 1.455, "score": 0.79},
        {"start_time": 0.96, "end_time": 1.935, "score": 0.10}
    ]
    p14_ev = merge_phase14_events(wins, 0.75, 0.88, 0.48, 2, 2.0)
    p17_ev = merge_phase17_events(wins, 0.75, 0.88, 0.48, 2, 2.0)
    cand_ev = candidate.merge_phase17_events(wins, 0.75, 0.88, 0.48, 2, 2.0)

    assert len(p14_ev) == 1
    assert len(p17_ev) == 1
    assert len(cand_ev) == 1


def test_regression_test_d_recording_boundary():
    """Test D: Boundary reset across independent files."""
    wins_f1 = [
        {"start_time": 0.0, "end_time": 0.975, "score": 0.10},
        {"start_time": 0.48, "end_time": 1.455, "score": 0.78}
    ]
    wins_f2 = [
        {"start_time": 0.0, "end_time": 0.975, "score": 0.78},
        {"start_time": 0.48, "end_time": 1.455, "score": 0.10}
    ]
    assert len(merge_phase14_events(wins_f1, 0.75, 0.88, 0.48, 2, 2.0)) == 0
    assert len(merge_phase14_events(wins_f2, 0.75, 0.88, 0.48, 2, 2.0)) == 0

    # Phase 17 fails on File 1 due to unguarded EOF flush
    assert len(merge_phase17_events(wins_f1, 0.75, 0.88, 0.48, 2, 2.0)) == 1

    # Candidate patch passes on both
    assert len(candidate.merge_phase17_events(wins_f1, 0.75, 0.88, 0.48, 2, 2.0)) == 0
    assert len(candidate.merge_phase17_events(wins_f2, 0.75, 0.88, 0.48, 2, 2.0)) == 0


def test_regression_test_e_immediate_qualification():
    """Test E: Immediate qualification must emit 1 alert on sharp high spike."""
    wins = [
        {"start_time": 0.0, "end_time": 0.975, "score": 0.92},
        {"start_time": 0.48, "end_time": 1.455, "score": 0.10}
    ]
    p14_ev = merge_phase14_events(wins, 0.75, 0.88, 0.48, 2, 2.0, crest_factor_db=15.0)
    p17_ev = merge_phase17_events(wins, 0.75, 0.88, 0.48, 2, 2.0, crest_factor_db=15.0)
    cand_ev = candidate.merge_phase17_events(wins, 0.75, 0.88, 0.48, 2, 2.0, crest_factor_db=15.0)

    assert len(p14_ev) == 1
    assert len(p17_ev) == 1
    assert len(cand_ev) == 1


# =============================================================================
# 4. ANIMAL SUPPRESSION & COUNTERFACTUAL REPRODUCTION TESTS
# =============================================================================
def test_animal_suppression_parameter_values():
    """Verify exact parameter definitions in frozen Phase 17."""
    cfg = candidate.Phase17ExperimentalGunshotDetector.PROFILES["balanced"]
    assert cfg["threshold_base"] == 0.75
    assert cfg["threshold_high"] == 0.88
    assert cfg["threshold_off"] == 0.48
    assert cfg["confirm_windows"] == 2
    assert cfg["cooldown_secs"] == 2.0
    assert cfg["animal_thresh"] == 0.35
    assert cfg["animal_ratio"] == 2.0


def test_aircraft_counterfactual_classification():
    """Verify classifications across all 25 aircraft overflights."""
    df = pd.read_csv(REPORTS_DIR / "phase31_suppression_counterfactual.csv")
    assert len(df) == 25
    counts = df["causal_classification"].value_counts().to_dict()
    assert counts["CONFIRMED_ANIMAL_SUPPRESSION_FRAGMENTATION"] == 11
    assert counts["NOT_OBSERVED_PURE_ACOUSTIC_FLUCTUATION"] == 9
    assert counts["PARTIALLY_CONFIRMED_ANIMAL_ACTIVE_NO_DIRECT_DROP"] == 5


# =============================================================================
# 5. STATISTICAL INFERENCE REPRODUCTION TESTS
# =============================================================================
def test_statistical_inferences_reproduction():
    """Verify Wilcoxon signed-rank, Sign test, and LOCO calculations."""
    df = pd.read_csv(REPORTS_DIR / "phase31_recording_master_registry.csv")
    p14_alerts = pd.read_csv(REPORTS_DIR / "phase31_alert_reconciliation.csv")["p14_alerts"].values
    p17_alerts = pd.read_csv(REPORTS_DIR / "phase31_alert_reconciliation.csv")["p17_alerts"].values

    diffs = p14_alerts - p17_alerts
    assert (diffs > 0).sum() == 3   # 3 recordings favor P17
    assert (diffs < 0).sum() == 5   # 5 recordings favor P14
    assert (diffs == 0).sum() == 15  # 15 recordings tied

    # Wilcoxon test (Wilcox convention)
    w_res = stats.wilcoxon(p14_alerts, p17_alerts, zero_method="wilcox")
    assert w_res.statistic == 8.0
    assert abs(w_res.pvalue - 0.15626) < 0.0001
    assert w_res.pvalue > 0.05, "Wilcoxon test must be non-significant"

    # Exact sign test
    s_res = stats.binomtest(3, 8, 0.5, alternative="two-sided")
    assert abs(s_res.pvalue - 0.72656) < 0.0001
    assert s_res.pvalue > 0.05, "Sign test must be non-significant"


def test_loco_subsets_non_significance():
    """Verify that all LOCO subsets are non-significant."""
    df_alerts = pd.read_csv(REPORTS_DIR / "phase31_alert_reconciliation.csv")
    for cid in df_alerts["campaign_id"].unique():
        sub = df_alerts[df_alerts["campaign_id"] != cid]
        d = sub["p14_alerts"].values - sub["p17_alerts"].values
        nz = d[d != 0]
        if len(nz) > 0:
            w = stats.wilcoxon(sub["p14_alerts"], sub["p17_alerts"], zero_method="wilcox")
            assert w.pvalue > 0.05, f"LOCO excluding {cid} unexpectedly significant: p={w.pvalue}"
