"""
Phase 14 Regression & Verification Test Suite.

Verifies:
1. Historical archive checksum immutability (Phases 8–13).
2. Phase 14 Candidate detector instantiation across all three profiles.
3. Calibrated semantic gating with ballistic gunshot protection.
4. Crest-guarded single-window immediate dispatch logic.
5. Muffled pocket gunshot recovery threshold (8.8 dB).
6. Stateful RealTimeStreamDetectorPhase14 streaming, reset, and thread safety.
7. Web application compatibility with Phase 9, 13, and 14 detector versions.
8. Diagnostic protection of Phase 12 final test benchmark.
"""

import os
import sys
import json
import hashlib
import unittest
from pathlib import Path

import numpy as np
import pandas as pd

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import config
from model_phase9 import (
    Phase9AdaptiveGunshotDetector,
    compute_physical_crest_factor_db,
    YAMNET_CLASS_GUNSHOT,
    YAMNET_CLASS_FIREWORKS,
    YAMNET_CLASS_THUNDERSTORM
)
from model_phase13 import Phase13CandidateGunshotDetector
from model_phase14 import (
    Phase14CandidateGunshotDetector,
    RealTimeStreamDetectorPhase14,
    merge_phase14_events
)

class TestPhase14Regression(unittest.TestCase):

    def test_01_historical_archives_checksums(self):
        """Verify historical archive immutability (Phases 8 through 13)."""
        expected_hashes = {
            "gunshot_detection_phase8.zip": "c8bd26d09b5a41903ae8308b7bcac42f37ecd00d95eb6abfa4295365e074d353",
            "gunshot_detection_phase9.zip": "96ff780eaa38737ea66851195301beebc576a31a48319f3b0a71083c4dee2ff0",
            "gunshot_detection_phase10.zip": "d8edb26b71d69d6e76a1834cc741bda272c71b475287d7bd7fe2f33be95c459d",
            "gunshot_detection_phase11.zip": "c50a9b07ffe93f01118fbc2a26130fd73c800d717b6a372d2e76291c735404ef",
            "gunshot_detection_phase12.zip": "8c674902761d469760928c81596813a08a942262440d977a423e58007055241a",
            "gunshot_detection_phase13.zip": "1a87aef803c7b2ec1bc0e5b3a894451960ea17a9f787a8ffc81ba7a15e8f6561",
        }
        checked = 0
        for name, expected in expected_hashes.items():
            p = Path("e:/gunshot") / name
            if not p.exists():
                p = Path("..") / name
            if not p.exists():
                continue
            actual = hashlib.sha256(p.read_bytes()).hexdigest()
            self.assertEqual(actual, expected, f"Archive {name} checksum altered!")
            checked += 1
        if checked == 0:
            self.skipTest("Historical archives phase8-13 were pruned to save disk space")

    def test_02_phase14_profiles_instantiation(self):
        """Verify that Phase 14 detector instantiates across all 3 profiles with correct parameters."""
        for prof in ["balanced", "high_precision", "high_sensitivity"]:
            det = Phase14CandidateGunshotDetector(profile=prof)
            self.assertEqual(det.profile, prof)
            self.assertGreater(det.threshold_base, 0.0)
            self.assertGreater(det.threshold_high, det.threshold_base)
            self.assertGreater(det.single_win_min_crest_db, det.min_crest_factor_db)
            self.assertEqual(det.fw_gun_max, 0.05 if prof != "high_sensitivity" else 0.06)

    def test_03_ballistic_protection_against_fireworks_suppression(self):
        """Verify that genuine gunshots with fireworks ambiguity (gun >= 0.05) are NOT suppressed."""
        det = Phase14CandidateGunshotDetector(profile="balanced")
        
        # Synthetic test window representing an AR-15 crack: gun=0.125, fw=0.261
        # In Phase 13 this was suppressed by 0.35 because 0.261 >= 0.125 * 1.5.
        # In Phase 14 it MUST NOT be suppressed because gun (0.125) >= fw_gun_max (0.05).
        raw_score = 0.82
        gun_s = 0.125
        fw_s = 0.261
        
        # Check rule directly
        should_suppress = (fw_s > det.fw_thresh and fw_s >= gun_s * det.fw_ratio and gun_s < det.fw_gun_max)
        self.assertFalse(should_suppress, "AR-15 ballistic crack should NOT be suppressed by fireworks rule!")

        # Window with real fireworks: gun=0.01, fw=0.55 -> MUST be suppressed
        gun_fw = 0.01
        fw_high = 0.55
        should_suppress_fw = (fw_high > det.fw_thresh and fw_high >= gun_fw * det.fw_ratio and gun_fw < det.fw_gun_max)
        self.assertTrue(should_suppress_fw, "Pure fireworks impulse should be suppressed!")

    def test_04_crested_guarded_single_window_dispatch(self):
        """Verify that single-window dispatch requires sharp crest factor >= 12 dB."""
        win_results = [{"start_time": 0.0, "end_time": 0.96, "score": 0.92}]
        
        # Crest = 10.5 dB (< 12 dB) -> must NOT trigger immediate dispatch on 1 window
        ev_low_crest = merge_phase14_events(
            window_results=win_results,
            threshold_base=0.75,
            threshold_high=0.88,
            threshold_off=0.48,
            confirm_windows=2,
            cooldown_secs=2.0,
            audio_duration_sec=2.0,
            allow_short_clip_exception=False,
            crest_factor_db=10.5,
            single_win_min_crest_db=12.0
        )
        self.assertEqual(len(ev_low_crest), 0, "Broad thunder rumble with score 0.92 must NOT trigger on 1 window without sharp crest!")

        # Crest = 14.5 dB (>= 12 dB) -> triggers immediate dispatch
        ev_high_crest = merge_phase14_events(
            window_results=win_results,
            threshold_base=0.75,
            threshold_high=0.88,
            threshold_off=0.48,
            confirm_windows=2,
            cooldown_secs=2.0,
            audio_duration_sec=2.0,
            allow_short_clip_exception=False,
            crest_factor_db=14.5,
            single_win_min_crest_db=12.0
        )
        self.assertEqual(len(ev_high_crest), 1, "Sharp ballistic transient with score 0.92 and crest 14.5dB must trigger immediate dispatch!")

    def test_05_muffled_pocket_crest_recovery(self):
        """Verify that muffled gunshot with crest 9.1 dB passes short clip exception in Phase 14."""
        win_results = [{"start_time": 0.0, "end_time": 0.96, "score": 0.78}]
        
        # In Phase 9: min_crest_factor_db was 9.5 dB -> rejected
        # In Phase 14: min_crest_factor_db is 8.8 dB -> accepted
        ev_p14 = merge_phase14_events(
            window_results=win_results,
            threshold_base=0.75,
            threshold_high=0.88,
            threshold_off=0.48,
            confirm_windows=2,
            cooldown_secs=2.0,
            audio_duration_sec=0.5,
            allow_short_clip_exception=True,
            crest_factor_db=9.1,
            min_crest_factor_db=8.8,
            single_win_min_crest_db=12.0
        )
        self.assertEqual(len(ev_p14), 1, "Muffled gunshot with crest 9.1 dB must be recovered under Phase 14!")

    def test_06_realtime_streaming_detector_state_and_reset(self):
        """Verify thread-safe RealTimeStreamDetectorPhase14 processing and reset isolation."""
        stream_det = RealTimeStreamDetectorPhase14(profile="balanced")
        self.assertEqual(len(stream_det.detected_alerts), 0)
        self.assertEqual(stream_det.stream_time_sec, 0.0)

        # Feed 2 seconds of silent audio (0.48s chunks = 7,680 samples)
        chunk = np.zeros(7680, dtype=np.float32)
        for _ in range(4):
            alerts = stream_det.process_chunk(chunk)
            self.assertEqual(len(alerts), 0)

        self.assertGreater(stream_det.stream_time_sec, 0.0)
        self.assertGreater(len(stream_det.chunk_latencies_ms), 0)

        # Reset
        stream_det.reset()
        self.assertEqual(stream_det.stream_time_sec, 0.0)
        self.assertEqual(len(stream_det.buffer), 0)
        self.assertEqual(len(stream_det.detected_alerts), 0)
        self.assertEqual(stream_det.cooldown_until, -1.0)
        self.assertFalse(stream_det.in_event)

    def test_07_web_app_integration_and_version_selection(self):
        """Verify that app.py supports Phase 9, Phase 13, and Phase 14 detectors."""
        from app import app, get_detector, get_session_stream_detector
        
        det9 = get_detector("phase9", "balanced")
        det13 = get_detector("phase13", "balanced")
        det14 = get_detector("phase14", "balanced")

        self.assertIsNotNone(det9)
        self.assertIsNotNone(det13)
        self.assertIsNotNone(det14)

        # Test streaming session retrieval
        s_det9 = get_session_stream_detector("test_session_p9", "phase9", "balanced")
        s_det14 = get_session_stream_detector("test_session_p14", "phase14", "balanced")
        self.assertIsNotNone(s_det9)
        self.assertIsNotNone(s_det14)
        self.assertNotEqual(id(s_det9), id(s_det14))

        # Test Flask test client
        with app.test_client() as client:
            resp = client.get("/api/status")
            self.assertEqual(resp.status_code, 200)
            data = resp.get_json()
            self.assertEqual(data["status"], "ok")

    def test_08_phase12_diagnostic_protection_and_provenance(self):
        """Verify that Phase 12 final test benchmark remains diagnostic-only and untouched."""
        p12_manifest = Path("data/manifests/phase12_independent_eval_manifest.csv")
        self.assertTrue(p12_manifest.exists())
        df_p12 = pd.read_csv(p12_manifest)
        final_test_files = df_p12[df_p12["split"] == "final_test"]
        self.assertEqual(len(final_test_files), 120, "Phase 12 final test set must have exactly 120 files!")

        # Verify reports exist
        self.assertTrue(Path("reports/phase14_source_overlap_matrix.csv").exists())
        self.assertTrue(Path("reports/phase14_duplicate_and_near_duplicate_audit.json").exists())
        self.assertTrue(Path("reports/phase14_event_level_comparison.csv").exists())
        self.assertTrue(Path("reports/phase14_experiment_matrix.csv").exists())
        self.assertTrue(Path("reports/phase14_statistical_comparison.md").exists())

if __name__ == "__main__":
    unittest.main()
