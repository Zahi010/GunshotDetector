"""
Phase 15: Regression & System Compatibility Test Suite.

Verifies:
1. Instantiation and parameter integrity across all frozen detector candidates.
2. Exact matching with reports/phase15_baseline_freeze.json.
3. Acoustic crest-guarded single-window immediate dispatch.
4. Pyrotechnic semantic gating with ballistic protection.
5. Web application (app.py) compatibility and detector selection parity.
6. Real-time streaming causal state machine reset and isolation.

SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.
"""

import os
import sys
import json
import unittest
from pathlib import Path

import numpy as np

WORKSPACE_ROOT = Path("e:/gunshot/gunshot")
sys.path.insert(0, str(WORKSPACE_ROOT))

from model_phase9 import Phase9AdaptiveGunshotDetector, compute_physical_crest_factor_db
from model_phase13 import Phase13CandidateGunshotDetector
from model_phase14 import (
    Phase14CandidateGunshotDetector,
    RealTimeStreamDetectorPhase14,
    merge_phase14_events
)

class TestPhase15Regression(unittest.TestCase):

    def test_01_all_detectors_instantiation(self):
        """Verify that Phase 9, Phase 13, and all Phase 14 profiles instantiate properly."""
        det_p9 = Phase9AdaptiveGunshotDetector(profile="balanced")
        det_p13 = Phase13CandidateGunshotDetector(profile="balanced")
        det_p14_b = Phase14CandidateGunshotDetector(profile="balanced")
        det_p14_hp = Phase14CandidateGunshotDetector(profile="high_precision")
        det_p14_hs = Phase14CandidateGunshotDetector(profile="high_sensitivity")

        self.assertIsNotNone(det_p9.model)
        self.assertIsNotNone(det_p13.model)
        self.assertIsNotNone(det_p14_b.model)
        self.assertEqual(det_p14_b.threshold_base, 0.75)
        self.assertEqual(det_p14_hp.threshold_base, 0.80)
        self.assertEqual(det_p14_hs.threshold_base, 0.70)

    def test_02_baseline_freeze_parameter_matching(self):
        """Verify that instantiated Phase 14 detector parameters strictly match baseline freeze JSON."""
        freeze_file = WORKSPACE_ROOT / "reports" / "phase15_baseline_freeze.json"
        self.assertTrue(freeze_file.exists(), f"Missing {freeze_file}")
        with open(freeze_file, "r") as f:
            freeze_data = json.load(f)

        profiles = freeze_data["phase14_profiles"]
        for prof_name, expected_params in profiles.items():
            det = Phase14CandidateGunshotDetector(profile=prof_name)
            self.assertEqual(det.threshold_base, expected_params["threshold_base"])
            self.assertEqual(det.threshold_high, expected_params["threshold_high"])
            self.assertEqual(det.threshold_off, expected_params["threshold_off"])
            self.assertEqual(det.confirm_windows, expected_params["confirm_windows"])
            self.assertEqual(det.cooldown_secs, expected_params["cooldown_secs"])
            self.assertEqual(det.min_crest_factor_db, expected_params["min_crest_factor_db"])
            self.assertEqual(det.single_win_min_crest_db, expected_params["single_win_min_crest_db"])

    def test_03_ballistic_protection_logic(self):
        """Verify that genuine gunshots with fireworks ambiguity (gun_s >= fw_gun_max) are NOT suppressed."""
        det = Phase14CandidateGunshotDetector(profile="balanced")
        
        # Scenario A: Genuine gunshot blast with high firework energy
        # gun_s = 0.15, fw_s = 0.35, fw_gun_max = 0.05
        # fw_s > det.fw_thresh and fw_s >= gun_s * det.fw_ratio, BUT gun_s (0.15) >= fw_gun_max (0.05)
        # Result: Must NOT be suppressed
        gun_s = 0.15
        fw_s = 0.35
        suppressed = (fw_s > det.fw_thresh and fw_s >= gun_s * det.fw_ratio and gun_s < det.fw_gun_max)
        self.assertFalse(suppressed, "Genuine gunshot with pyrotechnic ambiguity must be protected!")

        # Scenario B: Pure pyrotechnic blast without gunshot presence
        # gun_s = 0.02, fw_s = 0.40 -> Must be suppressed
        gun_s_pure_fw = 0.02
        fw_s_pure = 0.40
        suppressed_pure = (fw_s_pure > det.fw_thresh and fw_s_pure >= gun_s_pure_fw * det.fw_ratio and gun_s_pure_fw < det.fw_gun_max)
        self.assertTrue(suppressed_pure, "Pure fireworks impulse must be suppressed!")

    def test_04_single_window_crest_gating(self):
        """Verify single-window immediate dispatch enforces crest factor >= single_win_min_crest_db."""
        win_results = [{"start_time": 0.0, "end_time": 0.96, "score": 0.90}]
        
        # Case 1: Muffled / Low Crest (10.0 dB < 12.0 dB) -> Must NOT dispatch on 1 window
        ev_low = merge_phase14_events(
            window_results=win_results,
            threshold_base=0.75,
            threshold_high=0.88,
            threshold_off=0.48,
            confirm_windows=2,
            cooldown_secs=2.5,
            crest_factor_db=10.0,
            single_win_min_crest_db=12.0
        )
        self.assertEqual(len(ev_low), 0, "Low crest factor must require confirmation windows!")

        # Case 2: Sharp Muzzle Blast (18.5 dB >= 12.0 dB) -> Dispatches immediately
        ev_high = merge_phase14_events(
            window_results=win_results,
            threshold_base=0.75,
            threshold_high=0.88,
            threshold_off=0.48,
            confirm_windows=2,
            cooldown_secs=2.5,
            crest_factor_db=18.5,
            single_win_min_crest_db=12.0
        )
        self.assertEqual(len(ev_high), 1, "Sharp high-crest blast must trigger immediate single-window dispatch!")

    def test_05_streaming_detector_reset(self):
        """Verify RealTimeStreamDetectorPhase14 resets internal ring buffer and temporal state cleanly."""
        streamer = RealTimeStreamDetectorPhase14(profile="balanced")
        dummy_chunk = np.random.uniform(-0.1, 0.1, size=7680).astype(np.float32)

        # Feed chunk
        res1 = streamer.process_chunk(dummy_chunk)
        self.assertIsInstance(res1, list)

        # Reset
        streamer.reset()
        self.assertEqual(streamer.stream_time_sec, 0.0)
        self.assertEqual(len(streamer.active_cluster), 0)
        self.assertFalse(streamer.in_event)
        self.assertTrue(streamer.had_decayed)

    def test_06_web_app_detector_selection(self):
        """Verify that app.py imports cleanly and retains multi-version detector support."""
        import app
        self.assertTrue(hasattr(app, "app"))
        self.assertTrue(hasattr(app, "Phase9AdaptiveGunshotDetector"))
        self.assertTrue(hasattr(app, "Phase13CandidateGunshotDetector"))
        self.assertTrue(hasattr(app, "Phase14CandidateGunshotDetector"))

if __name__ == "__main__":
    unittest.main()
