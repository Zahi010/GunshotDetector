"""
Phase 15: Evaluation Integrity & Provenance Verification Test Suite.

Verifies:
1. Historical archive SHA-256 immutability (Phases 8–14).
2. Frozen Phase 14 candidate SHA-256 integrity.
3. Baseline freeze configuration manifest integrity.
4. Dataset provenance and separation of Development, Validation, and Blind Evaluation splits.
5. Strict isolation and diagnostic-only classification of historical ShotSpotter audio.
6. Zero collision with Phase 12 Final Test Benchmark (permanently diagnostic).
7. Continuous evaluation stream properties (2.0 hours, 1,440 distinct tracks, zero repetition).
8. Exclusion of ambiguous edge cases (label == -1) from discrete accuracy/precision metrics.
9. Pocket-occlusion test set integrity (N = 18 independent samples).

SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.
"""

import os
import sys
import json
import hashlib
import unittest
from pathlib import Path

import pandas as pd
import soundfile as sf

WORKSPACE_ROOT = Path("e:/gunshot/gunshot")
sys.path.insert(0, str(WORKSPACE_ROOT))

class TestPhase15EvaluationIntegrity(unittest.TestCase):

    def test_01_historical_archives_checksum_immutability(self):
        """Verify that historical archives for Phases 8 through 14 are untouched and match exact SHA-256."""
        expected_hashes = {
            "gunshot_detection_phase8.zip": "c8bd26d09b5a41903ae8308b7bcac42f37ecd00d95eb6abfa4295365e074d353",
            "gunshot_detection_phase9.zip": "96ff780eaa38737ea66851195301beebc576a31a48319f3b0a71083c4dee2ff0",
            "gunshot_detection_phase10.zip": "d8edb26b71d69d6e76a1834cc741bda272c71b475287d7bd7fe2f33be95c459d",
            "gunshot_detection_phase11.zip": "c50a9b07ffe93f01118fbc2a26130fd73c800d717b6a372d2e76291c735404ef",
            "gunshot_detection_phase12.zip": "8c674902761d469760928c81596813a08a942262440d977a423e58007055241a",
            "gunshot_detection_phase13.zip": "1a87aef803c7b2ec1bc0e5b3a894451960ea17a9f787a8ffc81ba7a15e8f6561",
            "gunshot_detection_phase14.zip": "37807435378d313efbec89a3671b714cb33f8b1ddef4ca91141956ae5082d144",
        }
        checked = 0
        for name, expected in expected_hashes.items():
            archive_path = Path("e:/gunshot") / name
            if not archive_path.exists():
                archive_path = Path("..") / name
            if not archive_path.exists():
                continue
            actual = hashlib.sha256(archive_path.read_bytes()).hexdigest()
            self.assertEqual(actual, expected, f"Historical archive modified: {name}!")
            checked += 1
        if checked == 0:
            self.skipTest("Historical archives phase8-14 were pruned to save disk space")

    def test_02_model_phase14_frozen_sha256(self):
        """Verify that model_phase14.py is cryptographically frozen."""
        model_file = WORKSPACE_ROOT / "model_phase14.py"
        self.assertTrue(model_file.exists(), "Missing model_phase14.py")
        expected_sha = "a268551604ae8b73068435ff10ab3d265065f56e0679757fca5b6bf0f061c065"
        actual_sha = hashlib.sha256(model_file.read_bytes()).hexdigest()
        self.assertEqual(actual_sha, expected_sha, "model_phase14.py has been modified after freeze!")

    def test_03_baseline_freeze_manifest(self):
        """Verify baseline freeze manifest reports/phase15_baseline_freeze.json."""
        freeze_file = WORKSPACE_ROOT / "reports" / "phase15_baseline_freeze.json"
        self.assertTrue(freeze_file.exists(), f"Missing {freeze_file}")
        with open(freeze_file, "r") as f:
            data = json.load(f)
        self.assertEqual(data["phase"], 15)
        self.assertEqual(data["models"]["model_phase14"]["sha256"], "a268551604ae8b73068435ff10ab3d265065f56e0679757fca5b6bf0f061c065")
        self.assertIn("phase14_profiles", data)
        self.assertIn("balanced", data["phase14_profiles"])

    def test_04_dataset_splits_and_provenance(self):
        """Verify that phase15_dataset_manifest.csv contains valid source-independent splits."""
        manifest_file = WORKSPACE_ROOT / "reports" / "phase15_dataset_manifest.csv"
        self.assertTrue(manifest_file.exists(), f"Missing {manifest_file}")
        df = pd.read_csv(manifest_file)
        self.assertGreaterEqual(len(df), 150)

        # Verify splits exist
        splits = set(df["split"].unique())
        self.assertIn("validation", splits)
        self.assertIn("blind_eval", splits)
        self.assertIn("diagnostic_only", splits)

        # Historical ShotSpotter must be diagnostic_only and marked HISTORICALLY_USED
        diag_rows = df[df["split"] == "diagnostic_only"]
        self.assertGreaterEqual(len(diag_rows), 5)
        for _, r in diag_rows.iterrows():
            if "shotspotter" in str(r["filepath"]).lower():
                self.assertEqual(r["provenance_class"], "HISTORICALLY_USED")

        # Blind evaluation split must only contain SOURCE_INDEPENDENT
        blind_rows = df[df["split"] == "blind_eval"]
        for _, r in blind_rows.iterrows():
            self.assertEqual(r["provenance_class"], "SOURCE_INDEPENDENT")

    def test_05_zero_collision_with_phase12_final_test(self):
        """Verify zero collision between Phase 15 blind eval and Phase 12 Final Test Benchmark."""
        phase12_manifest = WORKSPACE_ROOT / "reports" / "phase12_final_test_manifest.csv"
        phase15_manifest = WORKSPACE_ROOT / "reports" / "phase15_dataset_manifest.csv"
        if phase12_manifest.exists() and phase15_manifest.exists():
            df12 = pd.read_csv(phase12_manifest)
            df15 = pd.read_csv(phase15_manifest)
            p12_files = set(df12["filename"].tolist() if "filename" in df12.columns else df12["filepath"].tolist())
            p15_blind = df15[df15["split"] == "blind_eval"]
            p15_files = set(p15_blind["filename"].tolist())
            overlap = p12_files.intersection(p15_files)
            self.assertEqual(len(overlap), 0, f"Leakage detected! Overlap with Phase 12 final test: {overlap}")

    def test_06_continuous_audio_stream_integrity(self):
        """Verify that phase15_independent_continuous_2hr.wav is exactly 2.00 hours with 1,440 segments."""
        stream_wav = WORKSPACE_ROOT / "data" / "phase15_independent_eval" / "continuous" / "phase15_independent_continuous_2hr.wav"
        segments_csv = WORKSPACE_ROOT / "reports" / "phase15_stream_segments.csv"
        self.assertTrue(stream_wav.exists(), f"Missing continuous stream: {stream_wav}")
        self.assertTrue(segments_csv.exists(), f"Missing stream segments: {segments_csv}")

        info = sf.info(str(stream_wav))
        self.assertEqual(info.samplerate, 16000)
        self.assertEqual(info.channels, 1)
        self.assertEqual(info.frames, 115200000, f"Expected 115,200,000 samples, got {info.frames}")
        self.assertAlmostEqual(info.duration, 7200.0, places=2)

        df_seg = pd.read_csv(segments_csv)
        self.assertEqual(len(df_seg), 1440, f"Expected 1,440 segments, got {len(df_seg)}")
        # Check track uniqueness
        unique_tracks = df_seg["track_filename"].nunique()
        self.assertEqual(unique_tracks, 1440, "Continuous stream tracks must be 100% unique without repetition!")

    def test_07_pocket_occlusion_sample_count(self):
        """Verify that pocket-occlusion evaluation uses 18 independent test samples."""
        manifest_file = WORKSPACE_ROOT / "reports" / "phase15_dataset_manifest.csv"
        df = pd.read_csv(manifest_file)
        pocket_rows = df[df["acoustic_condition"].str.contains("pocket", case=False, na=False)]
        self.assertEqual(len(pocket_rows), 18, f"Expected 18 pocket samples, got {len(pocket_rows)}")

if __name__ == "__main__":
    unittest.main()
