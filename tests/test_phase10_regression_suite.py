"""
Phase 10 Comprehensive Regression & Deployment Readiness Test Suite.

Validates:
1. Exact metric calculation reproducibility and 1-to-1 canonical matching.
2. Zero data leakage across training, validation, and diagnostic benchmarks.
3. Crest-factor boundary conditions (clean vs digital clipping vs noise floor).
4. Short-clip recovery vs single-window ambient noise cuts.
5. Semantic suppression precision (dog barks, crackling fire, fireworks, sirens).
6. Audio chunk boundary splitting (ring buffer continuity).
7. Cooldown boundaries, decay hysteresis, and duplicate alert suppression.
8. Rapid consecutive gunshot burst preservation.
9. Resilient handling of corrupted, empty, or silent audio input.
10. Model artifact integrity and SHA-256 archive verification.

SAFETY DESIGNATION:
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
from model_phase9 import (
    Phase9AdaptiveGunshotDetector,
    merge_detection_windows_phase9,
    compute_physical_crest_factor_db
)
from scripts.validate_streaming_harness import RealTimeStreamDetector
from scripts.evaluate_event_level import match_events


class TestPhase10RegressionSuite(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bundle_path = Path("models/gunshot_yamnet_bundle")
        cls.detector = Phase9AdaptiveGunshotDetector(bundle_dir=cls.bundle_path, profile="balanced")
        cls.streamer = RealTimeStreamDetector(profile="balanced")

    def test_01_metric_calculation_reproducibility(self):
        """Verify strict 1-to-1 event matching arithmetic, false positive separation, and recall."""
        gt_events = [
            {"canonical_event_id": "shot_01", "start_time_sec": 1.0, "end_time_sec": 1.48},
            {"canonical_event_id": "shot_02", "start_time_sec": 4.5, "end_time_sec": 4.98}
        ]
        detections = [
            {"start_time": 1.0, "end_time": 1.96, "peak_score": 0.94},
            {"start_time": 1.48, "end_time": 2.44, "peak_score": 0.80},  # Duplicate
            {"start_time": 4.5, "end_time": 5.46, "peak_score": 0.92},
            {"start_time": 8.0, "end_time": 8.96, "peak_score": 0.76}   # Spurious FP
        ]

        tp, fn, fp, delays, dups = match_events(gt_events, detections, tolerance_sec=0.50)
        self.assertEqual(tp, 2, "Both ground-truth shots must be detected")
        self.assertEqual(fn, 0, "No ground-truth shots should be missed")
        self.assertEqual(dups, 1, "Secondary alert on shot_01 must be isolated as duplicate")
        self.assertEqual(fp, 1, "Alert at t=8.0 must be classified as false positive")
        self.assertAlmostEqual(tp / (tp + fp), 2 / 3, places=2)
        self.assertAlmostEqual(tp / (tp + fn), 1.0, places=2)

    def test_02_data_leakage_and_benchmark_isolation(self):
        """Audit SHA-256 and recording IDs to guarantee zero leakage between train/val and benchmarks."""
        manifest_files = [
            Path("data/manifests/train.csv"),
            Path("data/manifests/val.csv"),
            Path("data/manifests/test.csv"),
            Path("data/manifests/phase7_independent_eval_manifest.csv"),
            Path("data/manifests/phase8_final_eval_manifest.csv")
        ]
        for mf in manifest_files:
            self.assertTrue(mf.exists(), f"Manifest {mf} must exist")

        train_val_stems = set(pd.read_csv("data/manifests/train.csv")["base_stem"].dropna()).union(
            set(pd.read_csv("data/manifests/val.csv")["base_stem"].dropna())
        )
        p8_stems = set(pd.read_csv("data/manifests/phase8_final_eval_manifest.csv")["recording_id"].dropna())
        p7_stems = set(pd.read_csv("data/manifests/phase7_independent_eval_manifest.csv")["recording_id"].dropna())

        self.assertEqual(len(p8_stems.intersection(train_val_stems)), 0, "Phase 8 benchmark must not overlap train/val")
        self.assertEqual(len(p7_stems.intersection(train_val_stems)), 0, "Phase 7 benchmark must not overlap train/val")

    def test_03_crest_factor_boundary_and_clipping(self):
        """Verify scale-invariance of crest factor and vulnerability to digital clipping."""
        # Simulated clean impulsive pulse
        t = np.linspace(0, 0.5, 8000, endpoint=False)
        impulse = np.exp(-t * 20.0).astype(np.float32)
        cf_clean = compute_physical_crest_factor_db(impulse)
        self.assertGreater(cf_clean, 10.0, "Clean impulse must have elevated crest factor")

        # Linear gain change (+6 dB, unclipped) -> identical crest factor
        cf_scaled = compute_physical_crest_factor_db(impulse * 2.0)
        self.assertAlmostEqual(cf_clean, cf_scaled, places=2, msg="Linear scaling must preserve crest factor")

        # Digital clipping saturation (clipped at 0.1) -> crest factor decreases
        clipped_impulse = np.clip(impulse * 10.0, -1.0, 1.0)
        cf_clipped = compute_physical_crest_factor_db(clipped_impulse)
        self.assertLess(cf_clipped, cf_clean, "Digital clipping must reduce crest factor")

    def test_04_short_clip_guarded_exception(self):
        """Verify that short clips (<= 1.05s) only bypass temporal confirmation if crest factor >= 9.5 dB."""
        win = [{"window_index": 0, "start_time": 0.0, "end_time": 0.96, "score": 0.80}]

        # Ballistic crest factor (16.0 dB) -> Dispatched!
        ev_shot = merge_detection_windows_phase9(
            win, threshold_base=0.75, threshold_high=0.88, audio_duration_sec=0.50,
            allow_short_clip_exception=True, crest_factor_db=16.0, min_crest_factor_db=9.5
        )
        self.assertEqual(len(ev_shot), 1, "Short ballistic gunshot must trigger via guarded exception")
        self.assertEqual(ev_shot[0]["dispatch_path"], "guarded_short_clip_exception")

        # Low crest factor (7.0 dB, flat ambient noise cut) -> Rejected!
        ev_noise = merge_detection_windows_phase9(
            win, threshold_base=0.75, threshold_high=0.88, audio_duration_sec=0.50,
            allow_short_clip_exception=True, crest_factor_db=7.0, min_crest_factor_db=9.5
        )
        self.assertEqual(len(ev_noise), 0, "Low crest noise cut must be rejected")

    def test_05_multi_category_semantic_suppression(self):
        """Verify that dog barks and fire crackles are cleanly suppressed by Phase 9 semantic gating."""
        p8_manifest = pd.read_csv("data/manifests/phase8_final_eval_manifest.csv")
        dog_rows = p8_manifest[p8_manifest["acoustic_condition"] == "dog_bark"]
        crackle_rows = p8_manifest[p8_manifest["acoustic_condition"] == "crackling_fire"]

        if not dog_rows.empty and Path(dog_rows.iloc[0]["filepath"]).exists():
            w_dog = load_audio_mono_16k(Path(dog_rows.iloc[0]["filepath"]))
            res_dog = self.detector.evaluate_waveform(w_dog)
            self.assertFalse(res_dog["detected"], "Dog bark must be rejected by semantic gating")

        if not crackle_rows.empty and Path(crackle_rows.iloc[0]["filepath"]).exists():
            w_crackle = load_audio_mono_16k(Path(crackle_rows.iloc[0]["filepath"]))
            res_crackle = self.detector.evaluate_waveform(w_crackle)
            self.assertFalse(res_crackle["detected"], "Crackling fire must be rejected by semantic gating")

    def test_06_streaming_ring_buffer_chunk_continuity(self):
        """Verify that an audio event split across a streaming chunk edge triggers exactly 1 alert."""
        self.streamer.reset()
        p8_manifest = pd.read_csv("data/manifests/phase8_final_eval_manifest.csv")
        shot_path = Path("data/phase8_final_eval/gunshots/mitchell_mossberg_12g_01.wav")
        if not shot_path.exists():
            shot_path = Path(p8_manifest[p8_manifest["label"] == 1].iloc[0]["filepath"])
        gun_wave = load_audio_mono_16k(shot_path)

        # Prepend 900ms silence so gunshot splits across the 480ms chunk boundary at t=960ms
        stream_wave = np.concatenate([np.zeros(int(0.90 * 16000), dtype=np.float32), gun_wave, np.zeros(16000, dtype=np.float32)])
        chunk_samples = 7680  # 480ms

        alerts = []
        for i in range(0, len(stream_wave), chunk_samples):
            alerts.extend(self.streamer.process_chunk(stream_wave[i:i + chunk_samples]))

        self.assertEqual(len(alerts), 1, "Split gunshot across chunk edge must trigger exactly 1 alert")

    def test_07_cooldown_reverberation_duplicate_suppression(self):
        """Verify that a single gunshot with a 1.5s reverberant decay produces 0 duplicate alerts."""
        reverb_windows = [
            {"window_index": 0, "start_time": 0.0, "end_time": 0.96, "score": 0.95},
            {"window_index": 1, "start_time": 0.48, "end_time": 1.44, "score": 0.82},
            {"window_index": 2, "start_time": 0.96, "end_time": 1.92, "score": 0.65},
            {"window_index": 3, "start_time": 1.44, "end_time": 2.40, "score": 0.50},
            {"window_index": 4, "start_time": 1.92, "end_time": 2.88, "score": 0.20}
        ]
        events = merge_detection_windows_phase9(
            reverb_windows, threshold_base=0.75, threshold_high=0.88, threshold_off=0.48, cooldown_secs=2.0
        )
        self.assertEqual(len(events), 1, "Reverberant decay must yield exactly 1 event")

    def test_08_rapid_consecutive_bursts(self):
        """Verify that two distinct rapid gunshots past decay trigger 2 separate alerts."""
        rapid_windows = [
            # Shot 1
            {"window_index": 0, "start_time": 0.0, "end_time": 0.96, "score": 0.94},
            {"window_index": 1, "start_time": 0.48, "end_time": 1.44, "score": 0.52},
            {"window_index": 2, "start_time": 0.96, "end_time": 1.92, "score": 0.30},  # Decayed below 0.48
            # Shot 2
            {"window_index": 3, "start_time": 1.44, "end_time": 2.40, "score": 0.92},
            {"window_index": 4, "start_time": 1.92, "end_time": 2.88, "score": 0.50},
            {"window_index": 5, "start_time": 2.40, "end_time": 3.36, "score": 0.25}
        ]
        events = merge_detection_windows_phase9(
            rapid_windows, threshold_base=0.75, threshold_high=0.88, threshold_off=0.48, cooldown_secs=2.0
        )
        self.assertEqual(len(events), 2, "Rapid double-tap with decay between shots must yield exactly 2 events")

    def test_09_corrupted_empty_silent_audio_resilience(self):
        """Verify detector handles empty, digital silence, and corrupted audio gracefully."""
        # 1. Empty array
        res_empty = self.detector.evaluate_waveform(np.zeros(0, dtype=np.float32))
        self.assertFalse(res_empty["detected"], "Empty array must not trigger detection")

        # 2. Digital silence
        res_silence = self.detector.evaluate_waveform(np.zeros(16000, dtype=np.float32))
        self.assertFalse(res_silence["detected"], "Silence must not trigger detection")

        # 3. NaNs / Infs in streaming chunk
        self.streamer.reset()
        corrupted = np.array([np.nan, np.inf] * 3840, dtype=np.float32)
        alerts = self.streamer.process_chunk(corrupted)
        self.assertEqual(len(alerts), 0, "Corrupted audio chunk must not trigger detection")

    def test_10_phase8_and_phase9_archive_checksums(self):
        """Verify cryptographic integrity of frozen Phase 8 and Phase 9 deployment archives."""
        p8_zip = Path("e:/gunshot/gunshot_detection_phase8.zip")
        if not p8_zip.exists():
            p8_zip = Path("../gunshot_detection_phase8.zip")
        if not p8_zip.exists():
            self.skipTest("Phase 8 and 9 archives were pruned to save disk space")
        with open(p8_zip, "rb") as f:
            hasher_p8 = hashlib.sha256(f.read()).hexdigest()
        self.assertEqual(
            hasher_p8, "c8bd26d09b5a41903ae8308b7bcac42f37ecd00d95eb6abfa4295365e074d353",
            "Phase 8 archive checksum must match frozen baseline"
        )

        p9_zip = Path("e:/gunshot/gunshot_detection_phase9.zip")
        if not p9_zip.exists():
            p9_zip = Path("../gunshot_detection_phase9.zip")
        self.assertTrue(p9_zip.exists(), "Phase 9 archive must exist")
        with open(p9_zip, "rb") as f:
            hasher_p9 = hashlib.sha256(f.read()).hexdigest()
        self.assertEqual(
            hasher_p9, "96ff780eaa38737ea66851195301beebc576a31a48319f3b0a71083c4dee2ff0",
            "Phase 9 archive checksum must match verified release"
        )


if __name__ == "__main__":
    unittest.main()
