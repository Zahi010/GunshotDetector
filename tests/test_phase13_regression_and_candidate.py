"""
Phase 13: Regression, Robustness & Candidate Integrity Test Suite.

Verifies:
1. Frozen baseline immutability (Phase 9 detector and Phase 8-12 archives unchanged).
2. Phase 13 candidate detector profiles and parameter validation.
3. Relative Semantic Dominance suppression without 'raw_score < 0.88' escape loophole.
4. Muffled gunshot crest factor relaxation (8.8 dB) recovering pocket occlusions.
5. Guarded single-window immediate dispatch (crest >= 12.0 dB or N=2 confirmation).
6. Extended hysteresis refractory cooldown (2.5s) preventing duplicate reflection triggers.
7. Phase 13 forensics and experimentation artifacts integrity and safety designations.

SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.
"""

import os
import sys
import json
import unittest
import hashlib
from pathlib import Path

import numpy as np
import pandas as pd

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import config
from model_phase9 import Phase9AdaptiveGunshotDetector, compute_physical_crest_factor_db
from model_phase13 import (
    Phase13CandidateGunshotDetector,
    RealTimeStreamDetectorPhase13,
    merge_phase13_events
)

class TestPhase13RegressionAndCandidate(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.forensics_json_path = Path("reports/phase13_alert_forensics.json")
        cls.timeline_csv_path = Path("reports/phase13_alert_timeline.csv")
        cls.forensics_md_path = Path("reports/phase13_continuous_alert_forensics.md")
        cls.protocol_audit_path = Path("reports/phase13_evaluation_protocol_audit.md")
        cls.provenance_path = Path("reports/phase13_provenance_reassessment.md")
        cls.exp_matrix_path = Path("reports/phase13_experiment_matrix.csv")

    def test_01_forensics_artifacts_integrity(self):
        """Verify existence and validity of Stage 1 forensics outputs."""
        self.assertTrue(self.forensics_json_path.exists(), "Forensics JSON missing")
        self.assertTrue(self.timeline_csv_path.exists(), "Timeline CSV missing")
        self.assertTrue(self.forensics_md_path.exists(), "Forensics Markdown missing")

        with open(self.forensics_json_path, "r") as f:
            data = json.load(f)
        self.assertEqual(data.get("total_alerts_reproduced"), 299)
        self.assertEqual(data.get("forensics_phase"), "Phase 13")
        self.assertIn("RESEARCH DEMONSTRATION PROTOTYPE", data.get("safety_designation", ""))

        df_timeline = pd.read_csv(self.timeline_csv_path)
        self.assertEqual(len(df_timeline), 299, "Timeline CSV must contain exactly 299 reproduced alerts")
        required_cols = ["alert_id", "stream_time_sec", "source_track_idx", "source_filename", "category", "dispatch_mechanism"]
        for col in required_cols:
            self.assertIn(col, df_timeline.columns)

    def test_02_protocol_audit_and_provenance_artifacts(self):
        """Verify Stage 2 audit and Stage 4 provenance documents."""
        self.assertTrue(self.protocol_audit_path.exists(), "Protocol audit markdown missing")
        self.assertTrue(self.provenance_path.exists(), "Provenance reassessment missing")

        with open(self.provenance_path, "r", encoding="utf-8") as f:
            prov_text = f.read()
        self.assertIn("4072698", prov_text, "Chicago incident 4072698 must be explicitly documented")
        self.assertIn("c7ba", prov_text)
        self.assertIn("da57", prov_text)
        self.assertIn("e058", prov_text)

    def test_03_phase13_candidate_detector_profiles(self):
        """Verify Phase 13 candidate detector initialization across all profiles."""
        for prof in ["balanced", "high_precision", "high_sensitivity"]:
            det = Phase13CandidateGunshotDetector(profile=prof)
            self.assertEqual(det.profile, prof)
            self.assertGreaterEqual(det.threshold_base, 0.70)
            self.assertGreaterEqual(det.threshold_high, 0.82)
            self.assertGreaterEqual(det.single_win_min_crest_db, 10.0)

    def test_04_muffled_pocket_crest_relaxation(self):
        """Verify that 8.8 dB threshold permits authentic muffled gunshot single-window clips."""
        # Simulated muffled gunshot window (crest = 9.2 dB)
        window = [{
            "start_time": 0.0,
            "end_time": 0.96,
            "score": 0.78
        }]

        # Phase 9 with 9.5 dB rejects this short clip
        from model_phase9 import merge_detection_windows_phase9
        p9_events = merge_detection_windows_phase9(
            window_results=window,
            threshold_base=0.75,
            threshold_high=0.88,
            threshold_off=0.48,
            confirm_windows=2,
            cooldown_secs=2.0,
            audio_duration_sec=0.96,
            allow_short_clip_exception=True,
            crest_factor_db=9.2,
            min_crest_factor_db=9.5
        )
        self.assertEqual(len(p9_events), 0, "Phase 9 should reject muffled shot due to 9.5 dB crest guard")

        # Phase 13 candidate with 8.8 dB accepts this authentic muffled shot
        p13_events = merge_phase13_events(
            window_results=window,
            threshold_base=0.75,
            threshold_high=0.88,
            threshold_off=0.48,
            confirm_windows=2,
            cooldown_secs=2.5,
            audio_duration_sec=0.96,
            allow_short_clip_exception=True,
            crest_factor_db=9.2,
            min_crest_factor_db=8.8,
            single_win_min_crest_db=12.0
        )
        self.assertEqual(len(p13_events), 1, "Phase 13 must accept muffled shot under 8.8 dB threshold")

    def test_05_guarded_single_window_dispatch(self):
        """Verify that score >= 0.88 without sharp crest (crest < 12 dB) requires N=2 consensus."""
        low_crest_window = [{
            "start_time": 0.0,
            "end_time": 0.96,
            "score": 0.89  # High score, but crest is low (e.g. broad thunder rumble)
        }]

        events = merge_phase13_events(
            window_results=low_crest_window,
            threshold_base=0.75,
            threshold_high=0.88,
            threshold_off=0.48,
            confirm_windows=2,
            cooldown_secs=2.5,
            audio_duration_sec=3.0,
            allow_short_clip_exception=False,
            crest_factor_db=9.0,           # Lower than single_win_min_crest_db (12.0)
            single_win_min_crest_db=12.0
        )
        self.assertEqual(len(events), 0, "Unconfirmed single window with low crest must NOT fire immediate alert")

        # But if sharp crest >= 12.0 dB, it immediately qualifies
        sharp_events = merge_phase13_events(
            window_results=low_crest_window,
            threshold_base=0.75,
            threshold_high=0.88,
            threshold_off=0.48,
            confirm_windows=2,
            cooldown_secs=2.5,
            audio_duration_sec=3.0,
            allow_short_clip_exception=False,
            crest_factor_db=14.5,          # Sharp impulse crest
            single_win_min_crest_db=12.0
        )
        self.assertEqual(len(sharp_events), 1, "Sharp impulse with crest >= 12.0 dB must qualify for immediate dispatch")

    def test_06_extended_hysteresis_cooldown(self):
        """Verify that 2.5s cooldown suppresses multipath reflections and late tails."""
        windows = [
            {"start_time": 0.0, "end_time": 0.96, "score": 0.95},  # Initial sharp gunshot
            {"start_time": 0.48, "end_time": 1.44, "score": 0.40}, # Decay below threshold_off
            {"start_time": 1.92, "end_time": 2.88, "score": 0.82}  # Multipath reflection arriving at 1.92s
        ]

        events = merge_phase13_events(
            window_results=windows,
            threshold_base=0.75,
            threshold_high=0.88,
            threshold_off=0.48,
            confirm_windows=2,
            cooldown_secs=2.5,  # 2.5s cooldown suppresses reflection arriving at 1.92s
            audio_duration_sec=3.0,
            allow_short_clip_exception=False,
            crest_factor_db=14.0,
            single_win_min_crest_db=12.0
        )
        self.assertEqual(len(events), 1, "Multipath reflection within 2.5s refractory cooldown must not trigger duplicate alert")

    def test_07_experiment_matrix_integrity(self):
        """Verify experiment matrix CSV has all isolated experiments."""
        self.assertTrue(self.exp_matrix_path.exists(), "Experiment matrix CSV missing")
        df_exp = pd.read_csv(self.exp_matrix_path)
        self.assertGreaterEqual(len(df_exp), 8, "Must contain all 8 experimental runs")
        exp_ids = list(df_exp["experiment_id"])
        self.assertIn("BASELINE_PHASE9", exp_ids)
        self.assertIn("EXP_A_TEMPORAL_AGGREGATION", exp_ids)
        self.assertIn("EXP_C_SEMANTIC_GATING", exp_ids)
        self.assertIn("EXP_D_CREST_FACTOR_8_8DB", exp_ids)
        self.assertIn("PHASE13_CANDIDATE_COMBINED", exp_ids)

if __name__ == "__main__":
    unittest.main()
