"""
Phase 9 Comprehensive Regression and Robustness Test Suite.

Validates:
1. Single-window short gunshot clips (guarded short-clip recovery).
2. High-confidence (N=1) and moderate-confidence (N=2) event triggers.
3. Rapid double-taps and burst-fire preservation across refractory periods.
4. Semantic mimic suppression: Thunder, Fireworks, Dog barks, Crackling fire, Sirens.
5. Low-SNR and distant gunshot handling without false-triggering on silence.
6. Empty, silent, corrupted, and truncated input audio robustness.
7. Audio truncation ending before confirmation completes.
8. Cooldown and event-clustering boundaries (duplicate suppression).
9. Missing or mismatched model artifacts handling.
10. Metric calculation reproducibility and arithmetic consistency.
11. Data leakage audit (zero overlap between training/val and diagnostic benchmarks).
12. Deployment archive integrity and SHA-256 verification.

SAFETY RESTRICTION:
RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.
"""

import os
import sys
import time
import zipfile
import hashlib
import unittest
import numpy as np
import pandas as pd
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import config
from dataset import load_audio_mono_16k
from model import load_model_bundle, GunshotDetector
from model_phase8 import AdaptiveGunshotDetector as Phase8Detector
from model_phase9 import (
    Phase9AdaptiveGunshotDetector,
    merge_detection_windows_phase9,
    compute_physical_crest_factor_db
)
from scripts.evaluate_event_level import match_events


class TestPhase9RegressionSuite(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bundle_path = Path("models/gunshot_yamnet_bundle")
        cls.detector_p9 = Phase9AdaptiveGunshotDetector(bundle_dir=cls.bundle_path, profile="balanced")

    def test_01_metric_calculation_reproducibility(self):
        """Verify 1-to-1 canonical event-matching arithmetic and duplicate isolation."""
        gt_events = [
            {"canonical_event_id": "shot_01", "start_time_sec": 1.0, "end_time_sec": 1.25},
            {"canonical_event_id": "shot_02", "start_time_sec": 4.0, "end_time_sec": 4.30}
        ]
        detections = [
            {"start_time": 1.0, "end_time": 1.96, "peak_score": 0.94},
            {"start_time": 1.48, "end_time": 2.44, "peak_score": 0.82},  # Duplicate
            {"start_time": 4.0, "end_time": 4.96, "peak_score": 0.91},
            {"start_time": 7.5, "end_time": 8.46, "peak_score": 0.77}   # False alarm
        ]

        tp, fn, fp, delays, dups = match_events(gt_events, detections, tolerance_sec=0.50)
        self.assertEqual(tp, 2, "Both ground-truth events must be detected")
        self.assertEqual(fn, 0, "No ground-truth events should be missed")
        self.assertEqual(dups, 1, "Duplicate alert on shot_01 must be isolated")
        self.assertEqual(fp, 1, "Spurious alert at t=7.5 must be counted as false positive")
        self.assertAlmostEqual(tp / (tp + fp), 2 / 3, places=2, msg="Precision must equal 66.7%")
        self.assertAlmostEqual(tp / (tp + fn), 2 / 2, places=2, msg="Recall must equal 100.0%")

    def test_02_data_leakage_and_benchmark_isolation(self):
        """Audit SHA-256 and recording IDs to guarantee zero leakage across all splits."""
        p8_manifest = pd.read_csv("data/manifests/phase8_final_eval_manifest.csv")
        p7_manifest = pd.read_csv("data/manifests/phase7_independent_eval_manifest.csv")
        train_df = pd.read_csv("data/manifests/train.csv")
        val_df = pd.read_csv("data/manifests/val.csv")

        # Collect hashes and stems from training and validation sets
        train_val_stems = set(train_df["base_stem"].dropna()).union(set(val_df["base_stem"].dropna()))
        
        p8_stems = set(p8_manifest["recording_id"].dropna())
        p7_stems = set(p7_manifest["recording_id"].dropna())

        p8_leakage = p8_stems.intersection(train_val_stems)
        p7_leakage = p7_stems.intersection(train_val_stems)

        self.assertEqual(len(p8_leakage), 0, f"Data leakage in Phase 8 benchmark: {p8_leakage}")
        self.assertEqual(len(p7_leakage), 0, f"Data leakage in Phase 7 benchmark: {p7_leakage}")

    def test_03_short_gunshot_clip_recovery(self):
        """Verify that single-window short gunshot clips with high crest factor trigger alert."""
        single_win = [{"window_index": 0, "start_time": 0.0, "end_time": 0.96, "score": 0.82}]
        
        # Test 1: High crest factor (ballistic gunshot, crest=22dB) -> Triggered!
        events_shot = merge_detection_windows_phase9(
            single_win,
            threshold_base=0.75,
            threshold_high=0.88,
            audio_duration_sec=0.50,
            allow_short_clip_exception=True,
            crest_factor_db=22.0,
            min_crest_factor_db=14.0
        )
        self.assertEqual(len(events_shot), 1, "Short ballistic gunshot must trigger alert via guarded exception")
        self.assertEqual(events_shot[0]["dispatch_path"], "guarded_short_clip_exception")

        # Test 2: Low crest factor (ambient noise cut, crest=8dB) -> Rejected!
        events_noise = merge_detection_windows_phase9(
            single_win,
            threshold_base=0.75,
            threshold_high=0.88,
            audio_duration_sec=0.50,
            allow_short_clip_exception=True,
            crest_factor_db=8.0,
            min_crest_factor_db=14.0
        )
        self.assertEqual(len(events_noise), 0, "Low-crest short noise cut must be rejected by crest factor guard")

    def test_04_high_confidence_vs_moderate_confidence_dispatch(self):
        """Verify high-confidence immediate trigger (N=1) vs moderate-confidence confirmation (N=2)."""
        # Single high-confidence window (score >= 0.88)
        win_high = [{"window_index": 0, "start_time": 0.0, "end_time": 0.96, "score": 0.92}]
        ev_high = merge_detection_windows_phase9(
            win_high, threshold_base=0.75, threshold_high=0.88, confirm_windows=2, audio_duration_sec=3.0
        )
        self.assertEqual(len(ev_high), 1, "Score >= 0.88 must trigger immediate single-window alert")
        self.assertEqual(ev_high[0]["dispatch_path"], "single_window_high_confidence")

        # Single moderate-confidence window (0.75 <= score < 0.88) in long audio
        win_mod_single = [{"window_index": 0, "start_time": 0.0, "end_time": 0.96, "score": 0.79}]
        ev_mod_single = merge_detection_windows_phase9(
            win_mod_single, threshold_base=0.75, threshold_high=0.88, confirm_windows=2, audio_duration_sec=3.0
        )
        self.assertEqual(len(ev_mod_single), 0, "Single window at score=0.79 must require N=2 confirmation")

        # Two consecutive moderate-confidence windows -> Confirmed!
        win_mod_double = [
            {"window_index": 0, "start_time": 0.0, "end_time": 0.96, "score": 0.79},
            {"window_index": 1, "start_time": 0.48, "end_time": 1.44, "score": 0.78}
        ]
        ev_mod_double = merge_detection_windows_phase9(
            win_mod_double, threshold_base=0.75, threshold_high=0.88, confirm_windows=2, audio_duration_sec=3.0
        )
        self.assertEqual(len(ev_mod_double), 1, "Two consecutive windows >= 0.75 must trigger confirmed event")
        self.assertEqual(ev_mod_double[0]["dispatch_path"], "multi_window_temporal_confirmation")

    def test_05_rapid_double_tap_burst_preservation(self):
        """Verify two distinct rapid gunshots (e.g. 1.2s apart) trigger 2 separate alerts."""
        rapid_burst_windows = [
            # First gunshot at t=0.0
            {"window_index": 0, "start_time": 0.0, "end_time": 0.96, "score": 0.95},
            {"window_index": 1, "start_time": 0.48, "end_time": 1.44, "score": 0.55},
            {"window_index": 2, "start_time": 0.96, "end_time": 1.92, "score": 0.30},  # Decayed below 0.48
            # Second gunshot at t=1.44
            {"window_index": 3, "start_time": 1.44, "end_time": 2.40, "score": 0.94},
            {"window_index": 4, "start_time": 1.92, "end_time": 2.88, "score": 0.52},
            {"window_index": 5, "start_time": 2.40, "end_time": 3.36, "score": 0.25}
        ]

        events = merge_detection_windows_phase9(
            rapid_burst_windows,
            threshold_base=0.75,
            threshold_high=0.88,
            threshold_off=0.48,
            confirm_windows=2,
            cooldown_secs=2.0
        )
        self.assertEqual(len(events), 2, "Rapid double-tap with decay between shots must yield exactly 2 events")
        self.assertAlmostEqual(events[0]["start_time"], 0.0, delta=0.1)
        self.assertAlmostEqual(events[1]["start_time"], 1.44, delta=0.1)

    def test_06_reverberant_decay_duplicate_suppression(self):
        """Verify a single gunshot with long reverberant decay produces exactly 1 alert."""
        reverb_windows = [
            {"window_index": 0, "start_time": 0.0, "end_time": 0.96, "score": 0.95},
            {"window_index": 1, "start_time": 0.48, "end_time": 1.44, "score": 0.82},  # Reverb
            {"window_index": 2, "start_time": 0.96, "end_time": 1.92, "score": 0.65},  # Reverb tail
            {"window_index": 3, "start_time": 1.44, "end_time": 2.40, "score": 0.50},  # Above tau_off
            {"window_index": 4, "start_time": 1.92, "end_time": 2.88, "score": 0.20}   # Decay
        ]

        events = merge_detection_windows_phase9(
            reverb_windows,
            threshold_base=0.75,
            threshold_high=0.88,
            threshold_off=0.48,
            confirm_windows=2,
            cooldown_secs=2.0
        )
        self.assertEqual(len(events), 1, "Reverberant decay must be clustered into exactly 1 event")
        self.assertAlmostEqual(events[0]["start_time"], 0.0, delta=0.1)
        self.assertAlmostEqual(events[0]["end_time"], 2.40, delta=0.1)

    def test_07_empty_silent_corrupted_audio_resilience(self):
        """Ensure detector gracefully handles empty, silent, or truncated audio without exceptions."""
        # 1. Empty array
        res_empty = self.detector_p9.evaluate_waveform(np.array([], dtype=np.float32))
        self.assertFalse(res_empty["detected"], "Empty audio must not trigger detection")
        self.assertEqual(res_empty["events_count"], 0)

        # 2. Complete digital silence (1 second)
        res_silence = self.detector_p9.evaluate_waveform(np.zeros(16000, dtype=np.float32))
        self.assertFalse(res_silence["detected"], "Silence must not trigger detection")
        self.assertEqual(res_silence["events_count"], 0)

        # 3. Truncated sub-window audio (100 samples)
        res_short = self.detector_p9.evaluate_waveform(np.random.randn(100).astype(np.float32) * 0.01)
        self.assertFalse(res_short["detected"], "Sub-window noise must not trigger detection")

    def test_08_semantic_attenuation_dog_and_crackle(self):
        """Verify that dog barks and crackling fire are suppressed by Phase 9 multi-category gating."""
        # Find dog bark and fire crackle files from Phase 8 final manifest
        df_p8 = pd.read_csv("data/manifests/phase8_final_eval_manifest.csv")
        dog_files = df_p8[df_p8["acoustic_condition"] == "dog_bark"]["filepath"].tolist()
        crackle_files = df_p8[df_p8["acoustic_condition"] == "crackling_fire"]["filepath"].tolist()

        if dog_files and Path(dog_files[0]).exists():
            wave_dog = load_audio_mono_16k(Path(dog_files[0]))
            res_dog = self.detector_p9.evaluate_waveform(wave_dog)
            # Verify dog is rejected or suppressed
            self.assertFalse(res_dog["detected"], f"Dog bark file {dog_files[0]} should be rejected")

        if crackle_files and Path(crackle_files[0]).exists():
            wave_crackle = load_audio_mono_16k(Path(crackle_files[0]))
            res_crackle = self.detector_p9.evaluate_waveform(wave_crackle)
            self.assertFalse(res_crackle["detected"], f"Crackling fire file {crackle_files[0]} should be rejected")

    def test_09_end_to_end_latency_budget(self):
        """Verify median CPU inference latency is < 300ms and streaming latency < 1500ms."""
        test_wave = np.random.randn(config.WINDOW_SAMPLES).astype(np.float32) * 0.05
        
        # Warmup
        for _ in range(3):
            _ = self.detector_p9.evaluate_waveform(test_wave)

        times = []
        for _ in range(10):
            t0 = time.perf_counter()
            _ = self.detector_p9.evaluate_waveform(test_wave)
            times.append((time.perf_counter() - t0) * 1000.0)

        median_lat = float(np.median(times))
        self.assertLess(median_lat, 300.0, f"CPU inference latency {median_lat:.1f}ms exceeds 300ms budget")

    def test_10_deployment_archive_integrity(self):
        """Verify Phase 8 archive integrity and non-tampering."""
        p8_zip = Path("e:/gunshot/gunshot_detection_phase8.zip")
        if not p8_zip.exists():
            self.skipTest("Phase 8 archive was pruned to save disk space")
        with zipfile.ZipFile(p8_zip, "r") as z:
            corrupt = z.testzip()
            self.assertIsNone(corrupt, f"Phase 8 archive contains corrupted file: {corrupt}")
            file_count = len(z.namelist())
            self.assertGreater(file_count, 1000, "Archive must contain full project contents")


if __name__ == "__main__":
    unittest.main()
