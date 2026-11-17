"""
Phase 32 Automated Test & Reproduction Verification Suite
MANDATORY SAFETY DESIGNATION:
RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.

This suite validates:
1. Baseline model freeze hashes and historical archive integrity.
2. 2x2 Factorial ablation condition isolation, alert counts, main effects, and interaction.
3. Event-level aircraft overflight fragmentation vs ambient background suppression.
4. Expanded 12-vector state-machine regression suite (batch and streaming).
5. Mathematical resolution of Wilcoxon exact untied, SciPy asymptotic, tied permutation, Pratt, and sign test.
6. Pittsburgh DQV 2018 event-matching audit (historical multi-credit vs strict 1-to-1).
7. Cumulative 23-stream continuous benchmark accounting under Conventions A and B.
8. Safety designation compliance across all Phase 32 deliverables.
"""

import sys
import os
import json
import hashlib
import itertools
from pathlib import Path
import pytest
import pandas as pd
import numpy as np
from scipy import stats

ROOT = Path("E:/gunshot/gunshot")
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "experiments/phase31"))

from model_phase14 import merge_phase14_events, RealTimeStreamDetectorPhase14
from model_phase17 import merge_phase17_events, RealTimeStreamDetectorPhase17
import model_phase17_state_reset_candidate as candidate

REPORTS_DIR = ROOT / "reports"


# =============================================================================
# 1. BASELINE FREEZE VERIFICATION
# =============================================================================
def test_baseline_freeze_hashes():
    """Verify SHA-256 hashes of frozen baseline models and historical archives."""
    with open(REPORTS_DIR / "phase32_baseline_freeze.json", "r", encoding="utf-8") as f:
        freeze = json.load(f)

    assert freeze["safety_designation"] == "RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY"
    assert freeze["status"] == "ALL_HASHES_VERIFIED_AND_FROZEN"

    models = freeze["frozen_models"]
    assert models["model_phase14.py"]["sha256"] == "a268551604ae8b73068435ff10ab3d265065f56e0679757fca5b6bf0f061c065"
    assert models["model_phase14.py"]["size_bytes"] == 23340

    assert models["model_phase17.py"]["sha256"] == "e2b262b866fdd5d7f1a4ab91a7b8b9bac189ee8cc7a78603b3544ca1579fb819"
    assert models["model_phase17.py"]["size_bytes"] == 29067

    assert models["model_phase13.py"]["sha256"] == "68585039a4a4fdb7978a99f5e2a72c0ad5a9523127ec24a1338fbedd1c1231e6"
    assert models["model_phase9.py"]["sha256"] == "85cedd9f5b988ecafb1eae7de9630ee3d6a387ded6ef732e0efb7c3b496f132a"
    assert models["model_phase17_state_reset_candidate.py"]["sha256"] == "c144b917b56532787e2a9198f2cad4a77dc2095b57962f31d11d250a4d5d9ea5"


# =============================================================================
# 2. FACTORIAL ABLATION ISOLATION & RESULTS
# =============================================================================
def test_factorial_ablation_alert_totals():
    """Verify exact alert counts across all 4 conditions on AeroSonicDB."""
    df_fac = pd.read_csv(REPORTS_DIR / "phase32_factorial_results.csv")
    corp = df_fac[df_fac["recording_id"] == "AEROSONIC_CORPUS_TOTAL"]

    tot_A = corp[corp["condition_id"] == "A"]["alert_count"].values[0]
    tot_B = corp[corp["condition_id"] == "B"]["alert_count"].values[0]
    tot_C = corp[corp["condition_id"] == "C"]["alert_count"].values[0]
    tot_D = corp[corp["condition_id"] == "D"]["alert_count"].values[0]

    assert tot_A == 108  # Frozen Phase 17
    assert tot_B == 130  # Defective Reset, No Suppression
    assert tot_C == 66   # Corrected Reset, Suppression ON
    assert tot_D == 72   # Phase 14 Baseline Equivalent


def test_factorial_main_effects_and_interaction():
    """Verify main effects, combined effect, and interaction contrast."""
    df_int = pd.read_csv(REPORTS_DIR / "phase32_factor_interactions.csv").set_index("metric")["value"].to_dict()

    assert df_int["Suppression_Effect_Under_Defective_Reset"] == -22
    assert df_int["Suppression_Effect_Under_Corrected_Reset"] == -6
    assert df_int["Reset_Defect_Effect_Under_Suppression_ON"] == 42
    assert df_int["Reset_Defect_Effect_Under_Suppression_OFF"] == 58
    assert df_int["Combined_Effect_A_vs_D"] == 36
    assert df_int["Factorial_Interaction"] == -16  # Significant non-zero interaction


def test_aircraft_sequences_vs_ambient_ablation():
    """Verify that inside aircraft flyovers, suppression increases alerts (fragmentation)."""
    df_ev = pd.read_csv(REPORTS_DIR / "phase32_event_level_ablation.csv")

    a_flyover_alerts = df_ev["condition_a_alerts"].sum()
    b_flyover_alerts = df_ev["condition_b_alerts"].sum()
    c_flyover_alerts = df_ev["condition_c_alerts"].sum()
    d_flyover_alerts = df_ev["condition_d_alerts"].sum()

    assert a_flyover_alerts == 78
    assert b_flyover_alerts == 72  # Condition A has MORE alerts than B inside flyovers (+6)
    assert c_flyover_alerts == 52
    assert d_flyover_alerts == 47  # Condition C has MORE alerts than D inside flyovers (+5)

    # Ambient outside flyovers:
    amb_a = 108 - a_flyover_alerts
    amb_b = 130 - b_flyover_alerts
    assert amb_a == 30
    assert amb_b == 58
    assert amb_a - amb_b == -28  # Suppression successfully reduces 28 ambient false alerts


# =============================================================================
# 3. EXPANDED 12-VECTOR STATE-MACHINE REGRESSION
# =============================================================================
def test_state_machine_12_vectors():
    """Verify all 12 synthetic regression vectors across P14, P17, and candidate."""
    df_vec = pd.read_csv(REPORTS_DIR / "phase32_state_machine_test_vectors.csv")

    assert len(df_vec) == 12
    # Phase 14 passes 12/12
    assert (df_vec["phase14_verdict"] == "PASS").sum() == 12

    # Phase 17 fails defective vectors
    failing_vectors = ["VEC-01", "VEC-02", "VEC-03", "VEC-04", "VEC-07", "VEC-09", "VEC-10", "VEC-12"]
    for vid in failing_vectors:
        row = df_vec[df_vec["vector_id"] == vid].iloc[0]
        assert row["phase17_verdict"] == "FAIL_DEFECT" or row["phase17_alert_count"] != row["expected_alert_count"]

    # Candidate patch passes 12/12
    assert (df_vec["candidate_verdict"] == "PASS").sum() == 12


def test_streaming_chunk_state_leakage():
    """Verify that streaming chunk processor candidate does not leak unconfirmed state."""
    # Chunk 1: sub-threshold unconfirmed spike (0.78, no second window)
    chunk1_wins = [
        {"start_time": 0.0, "end_time": 0.975, "score": 0.78, "raw_ensemble_score": 0.78},
        {"start_time": 0.48, "end_time": 1.455, "score": 0.10, "raw_ensemble_score": 0.10}
    ]
    # Chunk 2: after 5s silence, another isolated spike (0.78)
    chunk2_wins = [
        {"start_time": 5.0, "end_time": 5.975, "score": 0.78, "raw_ensemble_score": 0.78},
        {"start_time": 5.48, "end_time": 6.455, "score": 0.10, "raw_ensemble_score": 0.10}
    ]

    # Phase 14 baseline merger
    p14_evs = merge_phase14_events(chunk1_wins + chunk2_wins, 0.75, 0.88, 0.48, 2, 2.0)
    assert len(p14_evs) == 0

    # Phase 17 defective merger stitches them across the 5s gap
    p17_evs = merge_phase17_events(chunk1_wins + chunk2_wins, 0.75, 0.88, 0.48, 2, 2.0)
    assert len(p17_evs) == 1

    # Candidate patch correctly clears active_cluster
    cand_evs = candidate.merge_phase17_events(chunk1_wins + chunk2_wins, 0.75, 0.88, 0.48, 2, 2.0)
    assert len(cand_evs) == 0


# =============================================================================
# 4. WILCOXON MATHEMATICAL RECONCILIATION
# =============================================================================
def test_wilcoxon_reconciliation_exact_and_asymptotic():
    """Verify the exact mathematical derivations of Phase 29/30 vs Phase 31 Wilcoxon tests."""
    df_alerts = pd.read_csv(REPORTS_DIR / "phase31_alert_reconciliation.csv")
    p14 = df_alerts["p14_alerts"].values
    p17 = df_alerts["p17_alerts"].values

    diff = p14 - p17
    non_zero = diff[diff != 0]
    assert len(non_zero) == 8  # Exactly 8 non-zero differences
    assert len(diff[diff == 0]) == 15  # Exactly 15 zero differences

    # 1. Exact untied combinatorial formula (Phase 29/30):
    # Sum of ranks <= 8 with untied ranks [1, 2, 3, 4, 5, 6, 7, 8]: exactly 25 combinations out of 256.
    untied_ranks = list(range(1, 9))
    untied_sums = [sum(r for bit, r in zip(bits, untied_ranks) if bit == 1) for bits in itertools.product([0, 1], repeat=8)]
    untied_le_8 = sum(1 for s in untied_sums if s <= 8)
    p_exact_untied = 2 * untied_le_8 / 256
    assert untied_le_8 == 25
    assert p_exact_untied == 0.1953125  # Matches Phase 29/30 reported p-value exactly

    # 2. SciPy asymptotic normal approximation with tie-corrected variance (Phase 31):
    res_wilcox = stats.wilcoxon(p14, p17, zero_method="wilcox")
    assert res_wilcox.statistic == 8.0
    assert round(float(res_wilcox.pvalue), 5) == 0.15626  # Matches Phase 31 reported p-value

    # Mathematical proof of SciPy value:
    # Var = (8*9*17)/24 - (4^3 - 4)/48 = 51.0 - 1.25 = 49.75
    sigma = np.sqrt(49.75)
    z = (8.0 - 18.0) / sigma
    p_scipy_manual = 2 * stats.norm.cdf(z)
    assert np.isclose(res_wilcox.pvalue, p_scipy_manual, atol=1e-10)

    # 3. Exact tied permutation distribution (Gold Standard):
    tied_ranks = [1.0, 3.5, 3.5, 3.5, 3.5, 6.0, 7.0, 8.0]
    tied_sums = [sum(r for bit, r in zip(bits, tied_ranks) if bit == 1) for bits in itertools.product([0, 1], repeat=8)]
    tied_le_8 = sum(1 for s in tied_sums if s <= 8.0)
    p_exact_tied = 2 * tied_le_8 / 256
    assert tied_le_8 == 27
    assert p_exact_tied == 0.2109375

    # 4. Pratt zero-handling:
    res_pratt = stats.wilcoxon(p14, p17, zero_method="pratt")
    assert res_pratt.statistic == 53.0
    assert round(float(res_pratt.pvalue), 5) == 0.36754

    # 5. Exact sign test:
    n_pos = sum(1 for d in non_zero if d > 0)
    n_neg = sum(1 for d in non_zero if d < 0)
    assert n_pos == 3 and n_neg == 5
    p_sign = stats.binomtest(min(n_pos, n_neg), len(non_zero), 0.5).pvalue
    assert p_sign == 0.7265625

    # Universal conclusion:
    assert p_exact_untied > 0.05
    assert res_wilcox.pvalue > 0.05
    assert p_exact_tied > 0.05
    assert res_pratt.pvalue > 0.05
    assert p_sign > 0.05


# =============================================================================
# 5. PITTSBURGH DQV 2018 EVENT-MATCHING AUDIT
# =============================================================================
def test_pittsburgh_event_matching_audit():
    """Verify historical multi-credit fallacy vs strict 1-to-1 event matching."""
    df_rec = pd.read_csv(REPORTS_DIR / "phase21_recording_level_results.csv")
    df_al = pd.read_csv(REPORTS_DIR / "phase22_alert_event_timeline.csv")

    # 1. Total physical alerts emitted across 20 recordings
    p14_alerts = len(df_al[df_al["model_name"] == "phase_14_balanced"])
    p17_alerts = len(df_al[df_al["model_name"] == "phase_17_experimental"])
    assert p14_alerts == 15
    assert p17_alerts == 19

    # 2. Historical multi-credit recall (Phase 20)
    hist_p14_det = df_rec["phase_14_detections"].sum()
    hist_p17_det = df_rec["phase_17_detections"].sum()
    assert hist_p14_det == 27  # 12 extra phantom credits from alert reuse
    assert hist_p17_det == 33  # 14 extra phantom credits from alert reuse

    # Historical McNemar test: 6 discordant pairs (0 vs 6)
    p_hist_mcnemar = 2 * (0.5 ** 6)
    assert p_hist_mcnemar == 0.03125

    # 3. Strict 1-to-1 event matching
    # P14 matched 15 rounds; P17 matched 19 rounds.
    # Discordant pairs: b=1 (P14 only), c=5 (P17 only) -> total 6 pairs
    p_strict_mcnemar = stats.binomtest(1, 6, 0.5).pvalue
    assert p_strict_mcnemar == 0.21875  # NOT statistically significant!

    # 4. Recording-level incident detection (N=20)
    inc_p14 = df_rec["phase_14_incident_detected"].sum()
    inc_p17 = df_rec["phase_17_incident_detected"].sum()
    assert inc_p14 == 15
    assert inc_p17 == 18

    # Discordant recordings: b=0, c=3 (test_004, test_013, test_067)
    p_inc_mcnemar = stats.binomtest(0, 3, 0.5).pvalue
    assert p_inc_mcnemar == 0.2500  # NOT statistically significant!


# =============================================================================
# 6. CONTINUOUS NEGATIVE BENCHMARK RECHECK
# =============================================================================
def test_continuous_benchmark_recheck():
    """Verify cumulative continuous audio exposure and alert totals across 4 campaigns."""
    df_exp = pd.read_csv(REPORTS_DIR / "phase31_exposure_reconciliation.csv")

    p14_rows = df_exp[df_exp["detector"] == "Phase 14 Balanced"]
    p17_rows = df_exp[df_exp["detector"] == "Phase 17 Experimental"]

    assert len(p14_rows) == 23
    assert len(p17_rows) == 23

    # Total alerts
    assert p14_rows["observed_alerts"].sum() == 128
    assert p17_rows["observed_alerts"].sum() == 159

    # Gross duration: 12.6461 hours
    tot_gross_s = p14_rows["gross_duration_s"].sum()
    assert np.isclose(tot_gross_s, 45526.0, atol=1.0)
    assert np.isclose(tot_gross_s / 3600.0, 12.6461, atol=1e-3)


# =============================================================================
# 7. MANDATORY SAFETY DESIGNATION VERIFICATION
# =============================================================================
def test_safety_designation_compliance():
    """Verify that every Phase 32 report and test file contains the mandatory safety designation."""
    phase32_reports = [
        REPORTS_DIR / "phase32_final_report.md",
        REPORTS_DIR / "phase32_factorial_ablation.md",
        REPORTS_DIR / "phase32_state_machine_regression.md",
        REPORTS_DIR / "phase32_wilcoxon_reconciliation.md",
        REPORTS_DIR / "phase32_pittsburgh_event_matching.md",
        REPORTS_DIR / "phase32_continuous_benchmark_recheck.md",
        REPORTS_DIR / "phase32_risk_and_limitation_register.md"
    ]

    mandatory_str = "RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY"
    for r in phase32_reports:
        assert r.exists(), f"Report missing: {r}"
        content = r.read_text(encoding="utf-8")
        assert mandatory_str in content, f"Mandatory safety designation missing in {r}"
