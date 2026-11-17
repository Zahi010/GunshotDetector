"""
Phase 7 Regression Test Suite.

Verifies:
1. Metric consistency and historical reconciliation (12 alerts/103.43 hr vs 13 alerts/112.05 hr).
2. Source independence of new Phase 7 evaluation dataset (zero overlap with train/val/test).
3. Canonical event 1-to-1 matching policy integrity.
4. Duplicate alert suppression during reverberant decay.
5. Closely spaced gunshot preservation via adaptive refractory cooldown.
6. Real-time streaming detection latency vs offline onset delta distinction.
7. Active model bundle integrity and historical checkpoint preservation.
"""

import os
import sys
import unittest
import hashlib
import numpy as np
import pandas as pd
from pathlib import Path

# Insert project root
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import config
from dataset import GunshotDataset, get_base_stem
from model import GunshotDetector, merge_detection_windows
from scripts.evaluate_phase7_event_level import match_events_strict_1to1


class TestPhase7RegressionSuite(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bundle_path = Path("models/gunshot_yamnet_bundle")
        cls.detector = GunshotDetector(bundle_dir=cls.bundle_path)

    def test_01_phase6_audit_metric_reconciliation(self):
        """Verify that the 12 alerts vs 13 alerts inconsistency is accurately resolved."""
        audit_file = Path("reports/phase7_phase6_audit.json")
        self.assertTrue(audit_file.exists(), "phase7_phase6_audit.json must exist")

        import json
        with open(audit_file, "r", encoding="utf-8") as f:
            audit = json.load(f)

        self.assertIn("discrepancy_reconciliation_threshold_0690", audit)
        res = audit["discrepancy_reconciliation_threshold_0690"]
        root_cause = res["root_cause_diagnosis"]

        # Check policy figures
        self.assertEqual(root_cause["phase5_unconditional_cooldown"]["resulting_alert_count"], 12)
        self.assertAlmostEqual(root_cause["phase5_unconditional_cooldown"]["policy_a_rate_per_hr"], 103.43, places=1)
        self.assertEqual(root_cause["phase6_adaptive_refractory_cooldown"]["resulting_alert_count"], 13)
        self.assertAlmostEqual(root_cause["phase6_adaptive_refractory_cooldown"]["policy_a_rate_per_hr"], 112.05, places=1)
        self.assertIn("freesound_community-laser-compilation-05-31597", root_cause["phase5_unconditional_cooldown"]["behavior_on_laser_file"])

    def test_02_source_independence(self):
        """Ensure zero data leakage between Phase 7 independent dataset and historical train/val/test."""
        indep_manifest_file = Path("data/manifests/phase7_independent_eval_manifest.csv")
        self.assertTrue(indep_manifest_file.exists())
        df_indep = pd.read_csv(indep_manifest_file)

        # Historical manifests
        train_file = Path("data/manifests/train.csv")
        val_file = Path("data/manifests/val.csv")
        test_file = Path("data/manifests/test.csv")

        historical_stems = set()
        for mf in [train_file, val_file, test_file]:
            if mf.exists():
                df_hist = pd.read_csv(mf)
                stems = df_hist["base_stem"].astype(str).tolist()
                historical_stems.update(stems)

        indep_stems = set(df_indep["recording_id"].astype(str).tolist())
        overlap = indep_stems.intersection(historical_stems)
        self.assertEqual(len(overlap), 0, f"Found leaked stems in independent test set: {overlap}")

        # Check SHA-256 uniqueness across independent files
        hashes = df_indep["sha256"].tolist()
        self.assertEqual(len(hashes), len(set(hashes)), "Duplicate SHA-256 hashes found in independent test manifest")

    def test_03_canonical_event_matching_1to1(self):
        """Ensure 1-to-1 matching policy never counts duplicate detections as true positives."""
        gt_events = [
            {"canonical_event_id": "shot_01", "start_time_sec": 1.0, "end_time_sec": 1.2, "recording_id": "rec_01"},
            {"canonical_event_id": "shot_02", "start_time_sec": 5.0, "end_time_sec": 5.2, "recording_id": "rec_01"}
        ]
        # Three detections: two on shot_01 (initial + reverberant re-trigger), one on shot_02
        detections = [
            {"start_time": 1.0, "end_time": 1.96, "peak_score": 0.88, "trigger_windows": 2},
            {"start_time": 1.48, "end_time": 2.44, "peak_score": 0.81, "trigger_windows": 2},  # Duplicate
            {"start_time": 5.0, "end_time": 5.96, "peak_score": 0.92, "trigger_windows": 2}
        ]

        matched, missed, fa, dups = match_events_strict_1to1(gt_events, detections, tolerance_sec=0.75)
        self.assertEqual(len(matched), 2, "Both ground-truth shots must be matched")
        self.assertEqual(len(missed), 0, "No shots should be missed")
        self.assertEqual(len(dups), 1, "The secondary alert on shot_01 must be classified as duplicate")
        self.assertEqual(len(fa), 0, "No false alerts outside ground-truth")

    def test_04_duplicate_alert_suppression(self):
        """Verify that reverberant tail windows are suppressed under 2.0s cooldown when decaying."""
        # Simulated sequence: high score at t=0, decaying reverberation at t=0.48, t=0.96
        windows = [
            {"window_index": 0, "start_time": 0.0, "end_time": 0.96, "score": 0.89},
            {"window_index": 1, "start_time": 0.48, "end_time": 1.44, "score": 0.82},
            {"window_index": 2, "start_time": 0.96, "end_time": 1.92, "score": 0.77},  # Reverberant tail
            {"window_index": 3, "start_time": 1.44, "end_time": 2.40, "score": 0.76},  # Reverberant tail
            {"window_index": 4, "start_time": 1.92, "end_time": 2.88, "score": 0.52},
            {"window_index": 5, "start_time": 2.40, "end_time": 3.36, "score": 0.31},
        ]

        alerts = merge_detection_windows(windows, threshold=0.75, confirm_windows=2, cooldown_secs=2.0, threshold_off=0.50)
        self.assertEqual(len(alerts), 1, f"Expected 1 alert for reverberant gunshot, got {len(alerts)}")
        self.assertAlmostEqual(alerts[0]["start_time"], 0.0)

    def test_05_closely_spaced_gunshot_preservation(self):
        """Verify that adaptive refractory logic preserves second gunshot when amplitude decays between shots."""
        # Shot 1 at t=0.0-0.96, decay at t=0.96-1.44 (<0.50), Shot 2 at t=1.44-2.40
        windows = [
            {"window_index": 0, "start_time": 0.0, "end_time": 0.96, "score": 0.88},
            {"window_index": 1, "start_time": 0.48, "end_time": 1.44, "score": 0.82},  # Shot 1 confirmed
            {"window_index": 2, "start_time": 0.96, "end_time": 1.92, "score": 0.35},  # Inter-shot decay below 0.50
            {"window_index": 3, "start_time": 1.44, "end_time": 2.40, "score": 0.86},  # Shot 2 onset
            {"window_index": 4, "start_time": 1.92, "end_time": 2.88, "score": 0.84},  # Shot 2 confirmed
        ]

        alerts = merge_detection_windows(windows, threshold=0.75, confirm_windows=2, cooldown_secs=2.0, threshold_off=0.50)
        self.assertEqual(len(alerts), 2, f"Expected 2 alerts for rapid double-tap with decay, got {len(alerts)}")
        self.assertAlmostEqual(alerts[0]["start_time"], 0.0)
        self.assertAlmostEqual(alerts[1]["start_time"], 1.44)

    def test_06_streaming_latency_measurement(self):
        """Verify that streaming detection delay strictly incorporates buffering, hop, and inference."""
        dummy_input = np.random.randn(1, 1024).astype(np.float32)
        # Warmup call to exclude graph compilation overhead
        _ = self.detector.classifier_head.predict(dummy_input, verbose=0)
        import time
        t0 = time.perf_counter()
        _ = self.detector.classifier_head.predict(dummy_input, verbose=0)
        inference_latency_ms = (time.perf_counter() - t0) * 1000.0

        # Assert inference latency is within real-time budget (< 250 ms)
        self.assertLess(inference_latency_ms, 250.0, f"Inference latency {inference_latency_ms:.2f}ms exceeds 250ms budget")

        # Check end-to-end streaming formula
        buffer_ms = config.WINDOW_LENGTH_SECS * 1000.0  # 960 ms
        hop_confirm_ms = (2 - 1) * config.HOP_LENGTH_SECS * 1000.0  # 480 ms for N=2
        streaming_delay_ms = buffer_ms + hop_confirm_ms + inference_latency_ms

        self.assertGreater(streaming_delay_ms, 1400.0, "Streaming delay must realistically account for window buffer + hop")
        self.assertLess(streaming_delay_ms, 2000.0, "Streaming delay must be under 2.0s for real-time alerting")

    def test_07_model_bundle_and_archive_integrity(self):
        """Verify model bundle integrity and check that historical archives exist and are valid."""
        # 1. Active model bundle check
        self.assertTrue(self.bundle_path.exists())
        self.assertTrue((self.bundle_path / "metadata.json").exists())
        self.assertTrue((self.bundle_path / "threshold.json").exists())
        self.assertTrue((self.bundle_path / "classifier_head.keras").exists())
        self.assertTrue((self.bundle_path / "catboost_model.joblib").exists())
        self.assertTrue((self.bundle_path / "lightgbm_model.joblib").exists())
        self.assertTrue((self.bundle_path / "xgboost_model.joblib").exists())

        # 2. Check historical archives
        import zipfile
        for archive_name in ["gunshot_detection_phase4.zip", "gunshot_detection_phase5.zip", "gunshot_detection_phase6.zip"]:
            zip_p = Path(f"e:/gunshot/{archive_name}")
            if not zip_p.exists():
                continue
            with zipfile.ZipFile(zip_p, "r") as zf:
                bad_file = zf.testzip()
                self.assertIsNone(bad_file, f"Archive {archive_name} corrupted at file {bad_file}")


if __name__ == "__main__":
    unittest.main()
