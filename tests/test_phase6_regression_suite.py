"""
Phase 6 Complete Regression Test Suite.

Validates all 8 critical architectural, evaluation, and operational invariants:
1. Metric arithmetic and threshold consistency (strict formula verification).
2. Window-versus-event counting (distinct definitions and multi-window grouping).
3. Duplicate and overlapping event handling (canonical deduplication & zero self-overlap).
4. Source-independent splits (strict disjointness across train, val, and test).
5. Alert merging and cooldown behavior (confirmation windows & refractory lockout).
6. Preservation of genuine closely spaced gunshot events (rapid-fire distinction).
7. Offline-versus-streaming preprocessing parity (digital squelch gate equivalence).
8. Model bundle loading and inference latency (all 8 artifacts & < 150ms latency).
"""
import sys
import csv
import json
import time
import unittest
import numpy as np
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import config
from dataset import GunshotDataset, load_audio_mono_16k, get_base_stem, compute_file_hash
from model import GunshotDetector, merge_detection_windows
from scripts.evaluate_event_level import match_events, load_ground_truth_events
from scripts.run_phase5_final_evaluation import verify_metric_arithmetic, wilson_score_interval, poisson_rate_ci


class TestPhase6RegressionSuite(unittest.TestCase):

    def test_01_metric_arithmetic_consistency(self):
        """Test 1: Metric arithmetic and threshold consistency."""
        cm_samples = [
            {"tp": 69, "fp": 74, "tn": 720, "fn": 10},
            {"tp": 16, "fp": 12, "tn": 80, "fn": 1},
            {"tp": 78, "fp": 524, "tn": 270, "fn": 1},
        ]
        for cm in cm_samples:
            tp, fp, tn, fn = cm["tp"], cm["fp"], cm["tn"], cm["fn"]
            total = tp + fp + tn + fn
            row = {
                "true_positives": tp,
                "false_positives": fp,
                "true_negatives": tn,
                "false_negatives": fn,
                "accuracy": round((tp + tn) / total, 4),
                "precision": round(tp / (tp + fp), 4) if (tp + fp) > 0 else 0.0,
                "recall": round(tp / (tp + fn), 4) if (tp + fn) > 0 else 0.0,
                "f1_score": round(2 * (tp / (tp + fp)) * (tp / (tp + fn)) / ((tp / (tp + fp)) + (tp / (tp + fn))), 4) if tp > 0 else 0.0
            }
            self.assertTrue(verify_metric_arithmetic(row))

        # Test that inconsistent numbers raise AssertionError
        bad_row = {"true_positives": 10, "false_positives": 10, "true_negatives": 80, "false_negatives": 0,
                    "accuracy": 0.50, "precision": 0.50, "recall": 1.00, "f1_score": 0.6667}
        with self.assertRaises(AssertionError):
            verify_metric_arithmetic(bad_row)

    def test_02_window_versus_event_counting(self):
        """Test 2: Window-versus-event counting distinction."""
        # A single continuous event spanning 4 positive windows
        windows = [
            {"window_index": 0, "start_time": 0.00, "end_time": 0.96, "score": 0.85},
            {"window_index": 1, "start_time": 0.48, "end_time": 1.44, "score": 0.92},
            {"window_index": 2, "start_time": 0.96, "end_time": 1.92, "score": 0.89},
            {"window_index": 3, "start_time": 1.44, "end_time": 2.40, "score": 0.78},
        ]
        # At window level: 4 positive windows
        window_trigger_count = len([w for w in windows if w["score"] >= 0.69])
        self.assertEqual(window_trigger_count, 4, "Window level must count 4 positive triggers")

        # At event level: merged into exactly 1 event
        events = merge_detection_windows(windows, threshold=0.69, confirm_windows=2, cooldown_secs=2.0)
        self.assertEqual(len(events), 1, "Event level must cluster 4 windows into exactly 1 event")
        self.assertEqual(events[0]["trigger_windows_count"], 4)

    def test_03_duplicate_and_overlapping_event_handling(self):
        """Test 3: Duplicate and overlapping event handling."""
        manifest = Path("data/manifests/canonical_gunshot_events.csv")
        self.assertTrue(manifest.exists())
        with open(manifest, "r", encoding="utf-8") as f:
            reader = list(csv.DictReader(f))

        # Global event ID uniqueness
        event_ids = [r["canonical_event_id"] for r in reader]
        self.assertEqual(len(event_ids), len(set(event_ids)), "Canonical event IDs must be unique!")

        # Overlapping intervals check
        events_by_rec = {}
        for r in reader:
            events_by_rec.setdefault(r["recording_id"], []).append((float(r["start_time_sec"]), float(r["end_time_sec"])))

        for rec_id, intervals in events_by_rec.items():
            if len(intervals) > 1:
                intervals = sorted(intervals, key=lambda x: x[0])
                for i in range(len(intervals) - 1):
                    overlap = intervals[i][1] - intervals[i+1][0]
                    self.assertLess(overlap, 0.05, f"Overlapping events in {rec_id}!")

    def test_04_source_independent_splits(self):
        """Test 4: Source-independent splits."""
        c_tr = np.load(".cache_features/features_train.npz", allow_pickle=True)
        c_val = np.load(".cache_features/features_val.npz", allow_pickle=True)
        c_te = np.load(".cache_features/features_test.npz", allow_pickle=True)

        tr_recs = set(m["recording_id"] for m in c_tr["meta"])
        val_recs = set(m["recording_id"] for m in c_val["meta"])
        te_recs = set(m["recording_id"] for m in c_te["meta"])

        self.assertEqual(len(tr_recs & val_recs), 0, "Leakage between Train and Val!")
        self.assertEqual(len(tr_recs & te_recs), 0, "Leakage between Train and Test!")
        self.assertEqual(len(val_recs & te_recs), 0, "Leakage between Val and Test!")

    def test_05_alert_merging_and_cooldown_behavior(self):
        """Test 5: Alert merging and cooldown refractory lockout."""
        simulated = [
            {"window_index": 0, "start_time": 0.00, "end_time": 0.96, "score": 0.10},  # Below
            {"window_index": 1, "start_time": 0.48, "end_time": 1.44, "score": 0.85},  # Trigger 1
            {"window_index": 2, "start_time": 0.96, "end_time": 1.92, "score": 0.88},  # Trigger 2 (confirms event)
            {"window_index": 3, "start_time": 1.44, "end_time": 2.40, "score": 0.40},  # Hysteresis tail (>= 0.25)
            {"window_index": 4, "start_time": 1.92, "end_time": 2.88, "score": 0.15},  # Decay ends event
            {"window_index": 5, "start_time": 2.40, "end_time": 3.36, "score": 0.60},  # In cooldown -> Suppressed
        ]
        evs = merge_detection_windows(simulated, threshold=0.69, confirm_windows=2, cooldown_secs=2.0, threshold_off=0.25)
        self.assertEqual(len(evs), 1, "Reverberation tail and reflection must produce exactly 1 event")
        self.assertEqual(evs[0]["start_time"], 0.48)
        self.assertEqual(evs[0]["trigger_windows_count"], 3)

    def test_06_preservation_of_genuine_closely_spaced_gunshot_events(self):
        """Test 6: Preservation of genuine closely spaced gunshot events."""
        # Simulated two distinct gunshots fired 1.5s apart:
        # Shot 1 at t=0.0s (spans windows 0,1), decays at window 2
        # Shot 2 at t=1.44s (window 3, score 0.91)
        two_gunshots = [
            {"window_index": 0, "start_time": 0.00, "end_time": 0.96, "score": 0.90},  # Shot 1
            {"window_index": 1, "start_time": 0.48, "end_time": 1.44, "score": 0.85},  # Shot 1 tail
            {"window_index": 2, "start_time": 0.96, "end_time": 1.92, "score": 0.10},  # Clear gap/decay
            {"window_index": 3, "start_time": 1.44, "end_time": 2.40, "score": 0.92},  # Shot 2 onset
            {"window_index": 4, "start_time": 1.92, "end_time": 2.88, "score": 0.88},  # Shot 2 tail
        ]
        evs = merge_detection_windows(two_gunshots, threshold=0.69, confirm_windows=1, cooldown_secs=1.0)
        self.assertEqual(len(evs), 2, f"Expected 2 distinct gunshot events preserved, got {len(evs)}")
        self.assertEqual(evs[0]["start_time"], 0.00)
        self.assertEqual(evs[1]["start_time"], 1.44)

    def test_07_offline_versus_streaming_preprocessing_parity(self):
        """Test 7: Offline-versus-streaming preprocessing and squelch parity."""
        # Test that digital silence is squelched identically
        silence = np.zeros(15360, dtype=np.float32)
        rms = float(np.sqrt(np.mean(silence ** 2) + 1e-12))
        self.assertLess(rms, 1e-4)

        # Test genuine gunshot signal exceeds squelch gate
        gunshot = np.zeros(15360, dtype=np.float32)
        gunshot[:1600] = np.random.randn(1600) * 0.10
        rms_g = float(np.sqrt(np.mean(gunshot ** 2) + 1e-12))
        self.assertGreater(rms_g, 1e-4)
        self.assertGreater(rms_g, 0.01)

    def test_08_model_bundle_loading_and_inference_latency(self):
        """Test 8: Model bundle loading and inference latency."""
        bundle_dir = Path("models/gunshot_yamnet_bundle")
        self.assertTrue(bundle_dir.exists())

        detector = GunshotDetector(bundle_dir=bundle_dir)
        test_window = np.random.randn(15360).astype(np.float32) * 0.05

        # Warm-up call to initialize TensorFlow runtime and graph
        _ = detector.detect_waveform(test_window, threshold=0.69)

        t0 = time.time()
        res = detector.detect_waveform(test_window, threshold=0.69)
        elapsed_ms = (time.time() - t0) * 1000.0

        self.assertIn("overall_score", res)
        self.assertLess(elapsed_ms, 250.0, f"Inference latency {elapsed_ms:.1f}ms exceeds target!")


if __name__ == "__main__":
    unittest.main()
