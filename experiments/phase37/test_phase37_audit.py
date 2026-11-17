"""
Automated Test Suite for Phase 37 Forensic Audit
MANDATORY SAFETY DESIGNATION:
RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY
This experimental acoustic machine-learning software is uncertified and must never
be deployed for autonomous emergency dispatch, tactical police response,
active-shooter alerting, automated evacuation, building lockdown, or life-critical
physical security. Safe recorded audio playback only; no live-fire testing.
"""

import os
import sys
import json
import zipfile
import hashlib
from pathlib import Path
import numpy as np
import pandas as pd
import pytest

WORKSPACE_ROOT = Path("E:/gunshot/gunshot")
PHASE37_DIR = WORKSPACE_ROOT / "experiments" / "phase37"
REPORTS_DIR = WORKSPACE_ROOT / "reports"


def compute_sha256(filepath: Path) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


# =============================================================================
# 1. FROZEN MODEL & HISTORICAL ASSET IMMUTABILITY
# =============================================================================

class TestFrozenModelImmutability:
    """Verifies that historical detectors, candidates, and archives remain 100% frozen."""

    EXPECTED_HASHES = {
        "model_phase14.py": "a268551604ae8b73068435ff10ab3d265065f56e0679757fca5b6bf0f061c065",
        "model_phase17.py": "e2b262b866fdd5d7f1a4ab91a7b8b9bac189ee8cc7a78603b3544ca1579fb819",
        "experiments/phase31/model_phase17_state_reset_candidate.py": "c144b917b56532787e2a9198f2cad4a77dc2095b57962f31d11d250a4d5d9ea5",
        "feature_extractor.py": "1c665b7c1749de98337da0726627710fffe0dcfa56335291b666ae7abcbae94f",
        "config.py": "55749f9d46d561d131fad374064021b73c08274e2a79954efd08570b029b1858",
        "experiments/phase36/model_phase36.py": "2774ab4cae0fca6d2f3646b443694fefa40d6837ff195f1d216ae7ff7732563a",
        "experiments/phase36/event_state_machine.py": "a91e9bc6d0ab9ca805817a406857d31e1f482f7d8815b0eaf7fee9075cd23c31",
        "experiments/phase36/acoustic_features.py": "5cc775f97b8e9f2c62018efe6f3fc6d64913cfcb5ffd470a1daba625c6510a51",
        "experiments/phase36/config_phase36.json": "1aaffd5423e116958807372855d989e294d3ff12b614052e10df78346d62e363",
        "E:/gunshot/gunshot_detection_phase34.zip": "1c961893c89285a48c5bf2a61a09b3dd71860febc12ac2fb56f0e43fd2a41208",
        "E:/gunshot/gunshot_detection_phase35.zip": "142402f6d48c8167124807d0a5389ed322dd9e57e676f3dd5c3971ab8635f707",
        "E:/gunshot/gunshot_detection_phase36.zip": "44240bd32145fe0972cee5e7b088fe9524b2504b0b3d30a602703ba837174385"
    }

    def test_all_frozen_hashes(self):
        for rel_path, exp_hash in self.EXPECTED_HASHES.items():
            p = Path(rel_path) if rel_path.startswith("E:/") else WORKSPACE_ROOT / rel_path
            assert p.exists(), f"Missing frozen file: {p}"
            act_hash = compute_sha256(p)
            assert act_hash == exp_hash, f"Hash divergence on {rel_path}! Exp: {exp_hash}, Act: {act_hash}"


# =============================================================================
# 2. DATASET LINEAGE & EVALUATION INDEPENDENCE AUDIT
# =============================================================================

class TestDatasetLineageAndIndependence:
    """Verifies that all 87 evaluation recordings are accurately classified as repeated historical assets."""

    def test_lineage_registry_structure(self):
        csv_path = PHASE37_DIR / "phase37_dataset_lineage.csv"
        assert csv_path.exists()
        df = pd.read_csv(csv_path)
        assert len(df) == 87
        assert "provenance_classification" in df.columns
        assert "historical_phase_first_used" in df.columns

    def test_positive_recordings_historical_overlap(self):
        """100% of Phase 36 positive recordings match Phase 19 normalized 16k files bit-for-bit."""
        df_lineage = pd.read_csv(PHASE37_DIR / "phase37_dataset_lineage.csv")
        pos_df = df_lineage[df_lineage["partition"] == "PARTITION_2_CONTROLLED_POSITIVE"]
        assert len(pos_df) == 23

        # Every recording must be classified as EXACT_MATCH_TO_HISTORICAL_RECORDING
        assert (pos_df["provenance_classification"] == "EXACT_MATCH_TO_HISTORICAL_RECORDING").all()
        assert (pos_df["historical_phase_first_used"] == "Phase 19").all()
        assert (pos_df["recording_level_independence"] == "REPEATED_HISTORICAL_RECORDING").all()

    def test_continuous_negative_streams_historical_overlap(self):
        """All 4 continuous streams originated from Phase 8 (UrbanSound) and Phase 15."""
        df_lineage = pd.read_csv(PHASE37_DIR / "phase37_dataset_lineage.csv")
        bg_df = df_lineage[df_lineage["partition"] == "PARTITION_1_CONTINUOUS_NEGATIVE"]
        assert len(bg_df) == 4
        assert (bg_df["provenance_classification"] == "EXACT_MATCH_TO_HISTORICAL_RECORDING").all()
        assert set(bg_df["historical_phase_first_used"].values) == {"Phase 8", "Phase 15"}

    def test_distractor_clips_historical_lineage(self):
        """All 60 distractor clips originated from Phase 2/4 and Phase 15 repository libraries."""
        df_lineage = pd.read_csv(PHASE37_DIR / "phase37_dataset_lineage.csv")
        dist_df = df_lineage[df_lineage["partition"] == "PARTITION_3_REVIEWED_NON_TARGET"]
        assert len(dist_df) == 60
        assert (dist_df["provenance_classification"] == "EXACT_MATCH_TO_HISTORICAL_RECORDING").all()
        assert (dist_df["available_during_model_development"] == True).all()


# =============================================================================
# 3. SUPPRESSION ABLATION & EQUIVALENCE AUDIT
# =============================================================================

class TestSuppressionAblationAudit:
    """Verifies suppression activation and explains why COND4, COND5, COND6 aggregate metrics matched."""

    def test_attenuated_transition_windows_count(self):
        csv_path = PHASE37_DIR / "phase37_suppression_ablation_audit.csv"
        assert csv_path.exists()
        df = pd.read_csv(csv_path)
        # Exactly 23 transition windows experienced score attenuation
        assert len(df) == 23

    def test_sub_threshold_attenuation_mechanism(self):
        """Zero attenuated windows crossed a decision boundary (all raw scores already below threshold)."""
        df = pd.read_csv(PHASE37_DIR / "phase37_suppression_ablation_audit.csv")
        assert (df["decision_boundary_crossed"] == False).all()

        # Check candidate vs confirmed decays
        cand_decays = df[df["previous_state"] == "CANDIDATE"]
        conf_decays = df[df["previous_state"] == "CONFIRMED"]

        # In all candidate decays, raw score was already below 0.75
        assert (cand_decays["raw_score"] < 0.75).all()
        # In all confirmed decays, raw score was already below 0.48
        assert (conf_decays["raw_score"] < 0.48).all()

    def test_pairwise_condition_metrics(self):
        csv_path = PHASE37_DIR / "phase37_condition_pairwise_comparison.csv"
        assert csv_path.exists()
        df = pd.read_csv(csv_path)
        
        # COND4 vs COND5 and COND4 vs COND6
        c4_c5 = df[df["pair_label"].str.contains("Raw FSM vs Phase 36 Legacy")].iloc[0]
        c4_c6 = df[df["pair_label"].str.contains("Raw FSM vs Phase 36 Conservative")].iloc[0]

        assert c4_c5["delta_continuous_alerts"] == 0
        assert c4_c5["delta_positive_tp"] == 0
        assert int(c4_c5["transition_score_differences_count"]) == 23
        assert int(c4_c5["transition_state_differences_count"]) == 0

        assert c4_c6["delta_continuous_alerts"] == 0
        assert c4_c6["delta_positive_tp"] == 0
        assert int(c4_c6["transition_score_differences_count"]) == 12
        assert int(c4_c6["transition_state_differences_count"]) == 0


# =============================================================================
# 4. BALLISTIC EVENT-MATCHING & REPRODUCTION
# =============================================================================

class TestBallisticEventMatchingAudit:
    """Verifies round-by-round event matching and metric reproduction."""

    def test_annotated_rounds_accounting(self):
        csv_path = PHASE37_DIR / "phase37_ballistic_matching_audit.csv"
        assert csv_path.exists()
        df = pd.read_csv(csv_path)
        assert len(df) == 53
        assert (df["category"].str.startswith("CATEGORY_A")).sum() == 50
        assert (df["category"].str.startswith("CATEGORY_B")).sum() == 3

    def test_recall_and_precision_reproduction(self):
        df = pd.read_csv(PHASE37_DIR / "phase37_ballistic_matching_audit.csv")
        
        # Strict 1-to-1 matching reproduction
        assert int(df["cond1_strict_1to1_hit"].sum()) == 16  # Phase 14 Baseline: 16/53 (30.19% recall)
        assert int(df["cond4_strict_1to1_hit"].sum()) == 16  # Phase 36 Raw FSM: 16/53 (30.19% recall)
        assert int(df["cond6_strict_1to1_hit"].sum()) == 16  # Phase 36 Conservative: 16/53 (30.19% recall)
        assert int(df["cond2_strict_1to1_hit"].sum()) == 19  # Phase 17 Defective: 19/53 (elevated due to EOF defect)
        assert int(df["cond3_strict_1to1_hit"].sum()) == 17  # Phase 17 Reset Candidate: 17/53

        # Incident-level temporal overlap reproduction
        assert int(df["cond1_temporal_overlap"].sum()) == 27  # Incident burst-coalesced overlap (27 rounds)


# =============================================================================
# 5. CONTINUOUS BACKGROUND & ARCHIVE INTEGRITY
# =============================================================================

class TestContinuousBackgroundAndArchiveIntegrity:
    """Verifies continuous background metrics, exposure calculations, and zip CRCs."""

    def test_background_metrics_reproduction(self):
        csv_path = PHASE37_DIR / "phase37_background_metrics_reproduction.csv"
        assert csv_path.exists()
        df = pd.read_csv(csv_path)
        
        c1 = df[df["condition_id"] == "COND1_PHASE14_BALANCED_BASELINE"]
        assert c1["alerts_count"].sum() == 68
        assert round(c1["conv_b_cooldown_s"].sum(), 2) == 306.16

        c2 = df[df["condition_id"] == "COND2_PHASE17_EXPERIMENTAL_LEGACY"]
        assert c2["alerts_count"].sum() == 145
        assert round(c2["conv_b_cooldown_s"].sum(), 2) == 5131.36

        c4 = df[df["condition_id"] == "COND4_PHASE36_RAW_STATE_MACHINE"]
        assert c4["alerts_count"].sum() == 66
        assert round(c4["conv_b_cooldown_s"].sum(), 2) == 300.48

    def test_archive_reconciliation_and_crc(self):
        for zip_name, exp_sz, exp_h in [
            ("gunshot_detection_phase34.zip", 4552249, "1c961893c89285a48c5bf2a61a09b3dd71860febc12ac2fb56f0e43fd2a41208"),
            ("gunshot_detection_phase35.zip", 4561967, "142402f6d48c8167124807d0a5389ed322dd9e57e676f3dd5c3971ab8635f707"),
            ("gunshot_detection_phase36.zip", 137665, "44240bd32145fe0972cee5e7b088fe9524b2504b0b3d30a602703ba837174385"),
        ]:
            zp = Path("E:/gunshot") / zip_name
            assert zp.exists()
            assert zp.stat().st_size == exp_sz
            assert compute_sha256(zp) == exp_h
            with zipfile.ZipFile(zp, "r") as zf:
                assert zf.testzip() is None

    def test_phase37_audit_archive_crc(self):
        zp = Path("E:/gunshot/gunshot_detection_phase37_audit.zip")
        assert zp.exists()
        with zipfile.ZipFile(zp, "r") as zf:
            corrupted = zf.testzip()
            assert corrupted is None
            names = zf.namelist()
            assert len(names) >= 14
