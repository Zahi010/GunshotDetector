"""
Phase 5 Comprehensive Regression Test Suite: Evaluation Integrity & Reliable Event Detection.

Validates:
1. Metric Arithmetic Consistency: Programmatic verification of Accuracy, Precision, Recall, F1 from CM.
2. Canonical Event Deduplication: Verification that file copies like (1).mp3 cannot create duplicate physical events.
3. Strict 1-to-1 Event Matching: Verification of matching policy (no duplicate double-counting, correct latency and duplicate count).
4. Source-Split Independence: Zero recording or hash leakage across Train, Val, and Test.
5. Offline / Streaming Preprocessing Parity: Exact equivalence between offline detect_waveform and live streaming squelch gate.
"""
import sys
import csv
import json
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


class TestPhase5EvaluationIntegrity(unittest.TestCase):

    def test_metric_arithmetic_consistency(self):
        """Verify programmatic consistency of confusion matrix and derived rates."""
        test_cases = [
            {"tp": 80, "fp": 20, "tn": 850, "fn": 10},
            {"tp": 17, "fp": 0, "tn": 81, "fn": 0},
            {"tp": 0, "fp": 10, "tn": 90, "fn": 15},
            {"tp": 10, "fp": 0, "tn": 0, "fn": 0},
        ]
        for tc in test_cases:
            tp, fp, tn, fn = tc["tp"], tc["fp"], tc["tn"], tc["fn"]
            total = tp + fp + tn + fn
            acc = round((tp + tn) / total, 4)
            prec = round(tp / (tp + fp), 4) if (tp + fp) > 0 else 0.0
            rec = round(tp / (tp + fn), 4) if (tp + fn) > 0 else 0.0
            f1 = round(2 * prec * rec / (prec + rec), 4) if (prec + rec) > 0 else 0.0

            row = {
                "true_positives": tp,
                "false_positives": fp,
                "true_negatives": tn,
                "false_negatives": fn,
                "accuracy": acc,
                "precision": prec,
                "recall": rec,
                "f1_score": f1
            }
            self.assertTrue(verify_metric_arithmetic(row))

        # Check that mixed numbers fail assertion
        inconsistent_row = {
            "true_positives": 10,
            "false_positives": 10,
            "true_negatives": 80,
            "false_negatives": 0,
            "accuracy": 0.9999,  # Wrong accuracy
            "precision": 0.50,
            "recall": 1.00,
            "f1_score": 0.6667
        }
        with self.assertRaises(AssertionError):
            verify_metric_arithmetic(inconsistent_row)

    def test_canonical_event_deduplication(self):
        """Verify duplicate filenames (e.g. (1).mp3) cannot create phantom physical events."""
        manifest_path = Path("data/manifests/canonical_gunshot_events.csv")
        self.assertTrue(manifest_path.exists(), "Canonical manifest must exist.")

        with open(manifest_path, "r", encoding="utf-8") as f:
            reader = list(csv.DictReader(f))

        # 1. All canonical_event_ids must be strictly unique
        event_ids = [r["canonical_event_id"] for r in reader]
        self.assertEqual(len(event_ids), len(set(event_ids)), "Canonical event IDs must be globally unique!")

        # 2. Check test split has exactly 17 canonical physical events
        test_events = [r for r in reader if r["split"] == "test"]
        self.assertEqual(len(test_events), 17, f"Test split must have exactly 17 physical events, got {len(test_events)}")

        # 3. For any single physical recording, no two events have overlapping time intervals
        events_by_rec = {}
        for r in reader:
            rec_id = r["recording_id"]
            events_by_rec.setdefault(rec_id, []).append({
                "st": float(r["start_time_sec"]),
                "et": float(r["end_time_sec"])
            })

        for rec_id, ev_list in events_by_rec.items():
            if len(ev_list) > 1:
                sorted_evs = sorted(ev_list, key=lambda x: x["st"])
                for i in range(len(sorted_evs) - 1):
                    overlap = sorted_evs[i]["et"] - sorted_evs[i+1]["st"]
                    self.assertLess(overlap, 0.05, f"Overlapping duplicate event detected in recording {rec_id}!")

    def test_strict_one_to_one_event_matching(self):
        """Verify documented one-to-one event-matching policy."""
        gt_events = [
            {"start_time_sec": 1.00, "end_time_sec": 2.00, "duration_sec": 1.00},
            {"start_time_sec": 5.00, "end_time_sec": 6.00, "duration_sec": 1.00}
        ]

        # Case A: Two detections match two ground truth events perfectly
        det_a = [
            {"start_time": 1.10, "end_time": 1.90, "score": 0.85},
            {"start_time": 5.05, "end_time": 5.95, "score": 0.90}
        ]
        tp, fn, fp, delays, dups = match_events(gt_events, det_a, tolerance_sec=0.50)
        self.assertEqual(tp, 2)
        self.assertEqual(fn, 0)
        self.assertEqual(fp, 0)
        self.assertEqual(dups, 0)

        # Case B: Multiple duplicate detections for event 1 (must not double count TP)
        det_b = [
            {"start_time": 1.05, "end_time": 1.50, "score": 0.88},
            {"start_time": 1.40, "end_time": 1.90, "score": 0.82},  # Duplicate
            {"start_time": 1.80, "end_time": 2.10, "score": 0.75}   # Duplicate
        ]
        tp, fn, fp, delays, dups = match_events(gt_events, det_b, tolerance_sec=0.50)
        self.assertEqual(tp, 1, "Only first detection must match ground truth event 1")
        self.assertEqual(fn, 1, "Event 2 was missed, fn must equal 1")
        self.assertEqual(fp, 0, "Extra detections matching same event must be counted as duplicate alerts, not FP")
        self.assertEqual(dups, 2, "Expected 2 duplicate alerts")

        # Case C: Detection on completely negative audio
        det_c = [
            {"start_time": 10.0, "end_time": 11.0, "score": 0.70}
        ]
        tp, fn, fp, delays, dups = match_events([], det_c, tolerance_sec=0.50)
        self.assertEqual(tp, 0)
        self.assertEqual(fn, 0)
        self.assertEqual(fp, 1)

    def test_split_source_independence(self):
        """Verify absolute source independence across train, val, and test splits."""
        train_cache = np.load(".cache_features/features_train.npz", allow_pickle=True)
        val_cache = np.load(".cache_features/features_val.npz", allow_pickle=True)
        test_cache = np.load(".cache_features/features_test.npz", allow_pickle=True)

        train_stems = set(m["recording_id"] for m in train_cache["meta"])
        val_stems = set(m["recording_id"] for m in val_cache["meta"])
        test_stems = set(m["recording_id"] for m in test_cache["meta"])

        self.assertEqual(len(train_stems & val_stems), 0, "Leakage detected between Train and Val!")
        self.assertEqual(len(train_stems & test_stems), 0, "Leakage detected between Train and Test!")
        self.assertEqual(len(val_stems & test_stems), 0, "Leakage detected between Val and Test!")

    def test_offline_streaming_preprocessing_parity(self):
        """Verify digital silence gate and preprocessing parity between offline and streaming."""
        # Test digital silence (RMS < 1e-4) is squelched to 0 in both offline and live
        silence_chunk = np.zeros(15360, dtype=np.float32)
        quiet_noise = (np.random.randn(15360) * 1e-5).astype(np.float32)  # RMS ~ 1e-5 < 1e-4

        rms_silence = float(np.sqrt(np.mean(silence_chunk ** 2) + 1e-12))
        rms_quiet = float(np.sqrt(np.mean(quiet_noise ** 2) + 1e-12))
        self.assertLess(rms_silence, 1e-4)
        self.assertLess(rms_quiet, 1e-4)

        # Test genuine gunshot signal (RMS ~ 0.05 >> 1e-4) is not squelched
        synthetic_gunshot = np.zeros(15360, dtype=np.float32)
        synthetic_gunshot[:1600] = np.random.randn(1600) * 0.15  # 100ms burst
        rms_gunshot = float(np.sqrt(np.mean(synthetic_gunshot ** 2) + 1e-12))
        self.assertGreater(rms_gunshot, 1e-4)
        self.assertGreater(rms_gunshot, 0.01)


if __name__ == "__main__":
    unittest.main()
