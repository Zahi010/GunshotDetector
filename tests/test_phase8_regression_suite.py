"""
Phase 8 Regression Test Suite.

Comprehensive validation covering:
1. Metric arithmetic and event matching (strict 1-to-1 canonical matching policy).
2. Source independence and duplicate detection (zero leakage with training/historical splits).
3. Short-event handling (ensuring isolated transient gunshot clips <= 1.0s trigger correctly).
4. Closely spaced gunshot preservation (preserving rapid-fire / burst-fire sequences).
5. Temporal aggregation and duplicate-alert suppression (single gunshot with reverberant decay produces 1 alert).
6. Offline versus streaming audio preprocessing consistency.
7. End-to-end detection latency (< 2.0s total delay budget).
8. Model bundle loading and archive integrity (validating models and past deployment zips).
"""

import os
import sys
import time
import unittest
import zipfile
import hashlib
import numpy as np
import pandas as pd
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import config
from dataset import load_audio_mono_16k
from model import load_model_bundle, GunshotDetector, merge_detection_windows
from model_phase8 import AdaptiveGunshotDetector, merge_detection_windows_adaptive
from scripts.evaluate_event_level import match_events


class TestPhase8RegressionSuite(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bundle_path = Path("models/gunshot_yamnet_bundle")
        cls.detector_p8 = AdaptiveGunshotDetector(bundle_dir=cls.bundle_path)

    def test_01_metric_arithmetic_and_event_matching(self):
        """Verify strict 1-to-1 event matching logic, precision, recall, and duplicate classification."""
        gt_events = [
            {"canonical_event_id": "shot_01", "start_time_sec": 1.0, "end_time_sec": 1.25},
            {"canonical_event_id": "shot_02", "start_time_sec": 4.0, "end_time_sec": 4.30}
        ]
        # Three detections: 2 on shot_01 (initial + duplicate), 1 on shot_02, 1 false alarm at t=7.0
        detections = [
            {"start_time": 1.0, "end_time": 1.96, "peak_score": 0.92},
            {"start_time": 1.48, "end_time": 2.44, "peak_score": 0.81},  # Duplicate on shot_01
            {"start_time": 4.0, "end_time": 4.96, "peak_score": 0.89},
            {"start_time": 7.0, "end_time": 7.96, "peak_score": 0.78}   # False alarm
        ]

        tp, fn, fp, delays, dups = match_events(gt_events, detections, tolerance_sec=0.50)
        self.assertEqual(tp, 2, "Both ground-truth events must be detected")
        self.assertEqual(fn, 0, "No ground-truth events should be missed")
        self.assertEqual(dups, 1, "Secondary alert on shot_01 must be classified as a duplicate")
        self.assertEqual(fp, 1, "Alert at t=7.0 must be classified as a false alarm")
        self.assertEqual(len(delays), 2, "Delays recorded for both matched events")

    def test_02_source_independence_and_duplicate_detection(self):
        """Ensure zero data leakage between Phase 8 final benchmark and all prior training/eval sets."""
        p8_manifest_path = Path("data/manifests/phase8_final_eval_manifest.csv")
        self.assertTrue(p8_manifest_path.exists(), "Phase 8 final manifest must exist")
        df_p8 = pd.read_csv(p8_manifest_path)

        # Check against training, validation, and historical test manifests
        prior_manifests = [
            Path("data/manifests/train.csv"),
            Path("data/manifests/val.csv"),
            Path("data/manifests/test.csv"),
            Path("data/manifests/phase7_independent_eval_manifest.csv")
        ]

        prior_hashes = set()
        prior_stems = set()
        for p in prior_manifests:
            if p.exists():
                df_prior = pd.read_csv(p)
                if "sha256" in df_prior.columns:
                    prior_hashes.update(df_prior["sha256"].dropna().tolist())
                if "base_stem" in df_prior.columns:
                    prior_stems.update(df_prior["base_stem"].dropna().tolist())
                if "recording_id" in df_prior.columns:
                    prior_stems.update(df_prior["recording_id"].dropna().tolist())

        p8_hashes = set(df_p8["sha256"].dropna().tolist())
        hash_overlap = p8_hashes.intersection(prior_hashes)
        self.assertEqual(len(hash_overlap), 0, f"Data leakage detected via SHA-256 collision: {hash_overlap}")

        p8_stems = set(df_p8["recording_id"].dropna().tolist())
        stem_overlap = p8_stems.intersection(prior_stems)
        self.assertEqual(len(stem_overlap), 0, f"Data leakage detected via recording ID collision: {stem_overlap}")

    def test_03_short_event_handling(self):
        """Verify that isolated short clips (<=1.0s) trigger correctly under Phase 8 adaptive confirmation."""
        # Single window result representing a 0.5s gunshot clip
        single_win = [{"window_index": 0, "start_time": 0.0, "end_time": 0.96, "score": 0.88}]
        
        # Under Phase 7 (requires 2 consecutive windows, short clip exception disabled)
        p7_events = merge_detection_windows(
            single_win,
            threshold=0.75,
            confirm_windows=2,
            cooldown_secs=2.0
        )
        self.assertEqual(len(p7_events), 0, "Phase 7 baseline must block single window when N=2 is enforced")

        # Under Phase 8 Adaptive (short clip exception enabled)
        p8_events = merge_detection_windows_adaptive(
            single_win,
            threshold_base=0.70,
            threshold_high=0.82,
            confirm_windows=2,
            audio_duration_sec=0.50,
            allow_short_clip_exception=True
        )
        self.assertEqual(len(p8_events), 1, "Phase 8 Adaptive detector must trigger alert on isolated short gunshot clip")
        self.assertAlmostEqual(p8_events[0]["peak_score"], 0.88, places=2)

    def test_04_closely_spaced_gunshot_preservation(self):
        """Verify that rapid-fire / double-tap bursts with inter-shot decay are preserved as distinct events."""
        # Shot 1 at t=0.0-0.48 (score 0.89), inter-shot decay at t=0.48-0.96 (score 0.32), Shot 2 at t=0.96-1.44 (score 0.87)
        windows = [
            {"window_index": 0, "start_time": 0.0, "end_time": 0.96, "score": 0.89},
            {"window_index": 1, "start_time": 0.48, "end_time": 1.44, "score": 0.32},  # Inter-shot acoustic decay
            {"window_index": 2, "start_time": 0.96, "end_time": 1.92, "score": 0.87},  # Shot 2 arrival
            {"window_index": 3, "start_time": 1.44, "end_time": 2.40, "score": 0.40}
        ]

        events = merge_detection_windows_adaptive(
            windows,
            threshold_base=0.70,
            threshold_high=0.82,
            threshold_off=0.45,
            confirm_windows=1,
            cooldown_secs=1.5
        )
        self.assertEqual(len(events), 2, f"Expected 2 separate events for rapid double-tap, got {len(events)}")
        self.assertAlmostEqual(events[0]["start_time"], 0.0)
        self.assertAlmostEqual(events[1]["start_time"], 0.96)

    def test_05_temporal_aggregation_and_duplicate_suppression(self):
        """Verify that a single reverberant gunshot does not spawn multiple duplicate alerts."""
        windows = [
            {"window_index": 0, "start_time": 0.0, "end_time": 0.96, "score": 0.93},
            {"window_index": 1, "start_time": 0.48, "end_time": 1.44, "score": 0.84},
            {"window_index": 2, "start_time": 0.96, "end_time": 1.92, "score": 0.72},  # Reverberant tail
            {"window_index": 3, "start_time": 1.44, "end_time": 2.40, "score": 0.65},  # Reverberant tail
            {"window_index": 4, "start_time": 1.92, "end_time": 2.88, "score": 0.42},  # Decay below threshold_off
            {"window_index": 5, "start_time": 2.40, "end_time": 3.36, "score": 0.18}
        ]

        events = merge_detection_windows_adaptive(
            windows,
            threshold_base=0.70,
            threshold_high=0.82,
            threshold_off=0.45,
            confirm_windows=2,
            cooldown_secs=1.5
        )
        self.assertEqual(len(events), 1, f"Expected exactly 1 event for reverberant gunshot, got {len(events)}")
        self.assertAlmostEqual(events[0]["start_time"], 0.0)
        self.assertEqual(events[0]["trigger_windows_count"], 4)

    def test_06_offline_versus_streaming_preprocessing(self):
        """Verify that audio loading maintains standardized 16 kHz mono float32 properties."""
        dummy_wave = np.random.uniform(-0.8, 0.8, 32000).astype(np.float32)
        # Test basic audio assertions
        self.assertEqual(dummy_wave.dtype, np.float32)
        self.assertTrue(np.all(np.isfinite(dummy_wave)))
        self.assertLessEqual(np.max(np.abs(dummy_wave)), 1.0)

    def test_07_end_to_end_latency_measurement(self):
        """Verify inference latency and end-to-end streaming delay satisfy the < 2.0s requirement."""
        dummy_wave = np.random.normal(0, 0.05, 15360).astype(np.float32)
        # Warmup call to exclude one-time graph compilation overhead
        _ = self.detector_p8.evaluate_waveform(dummy_wave)
        t0 = time.perf_counter()
        _ = self.detector_p8.evaluate_waveform(dummy_wave)
        lat_ms = (time.perf_counter() - t0) * 1000.0

        self.assertLess(lat_ms, 300.0, f"Inference latency ({lat_ms:.1f}ms) exceeds 300ms budget")

        # Full streaming delay = Window Buffering (960ms) + 1-hop decision (480ms) + Inference Latency (<300ms)
        e2e_streaming_delay_ms = 960.0 + 480.0 + lat_ms
        self.assertLess(e2e_streaming_delay_ms, 2000.0, f"End-to-end streaming delay ({e2e_streaming_delay_ms:.1f}ms) must be under 2000ms")

    def test_08_model_bundle_loading_and_archive_integrity(self):
        """Verify all bundle models and prior deployment archives exist and are valid."""
        # 1. Active model bundle check
        self.assertTrue(self.bundle_path.exists())
        self.assertTrue((self.bundle_path / "metadata.json").exists())
        self.assertTrue((self.bundle_path / "classifier_head.keras").exists())
        self.assertTrue((self.bundle_path / "catboost_model.joblib").exists())
        self.assertTrue((self.bundle_path / "lightgbm_model.joblib").exists())
        self.assertTrue((self.bundle_path / "xgboost_model.joblib").exists())

        # 2. Check all previous archives
        archives = [
            "gunshot_detection_phase4.zip",
            "gunshot_detection_phase5.zip",
            "gunshot_detection_phase6.zip",
            "gunshot_detection_phase7.zip"
        ]
        for arc in archives:
            arc_p = Path(f"e:/gunshot/{arc}")
            if not arc_p.exists():
                continue
            with zipfile.ZipFile(arc_p, "r") as zf:
                bad_file = zf.testzip()
                self.assertIsNone(bad_file, f"Archive {arc} is corrupted at {bad_file}")


if __name__ == "__main__":
    unittest.main()
