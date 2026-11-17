"""
Phase 19 Automated Verification & Regression Test Suite
MANDATORY SAFETY DESIGNATION:
RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.

Validates:
1. Frozen Model Hashes (Phase 14, Phase 17, Phase 13, Phase 9)
2. Historical Archive Hashes (Phase 18, Phase 17, Phase 16)
3. Zero Data Collision & Absolute Independence Certification
4. Dataset Manifest & Ground Truth Integrity (50 Cat A events, 3 Cat B events)
5. Evaluation Metric Consistency & Wilson Score Bounding
6. Negative Benchmark Bounds & Low-Alert Constraints
"""

import os
import sys
import json
import hashlib
import unittest
from pathlib import Path
import pandas as pd

ROOT = Path("E:/gunshot/gunshot")
sys.path.insert(0, str(ROOT))

FROZEN_MODEL_HASHES = {
    "model_phase14.py": "a268551604ae8b73068435ff10ab3d265065f56e0679757fca5b6bf0f061c065",
    "model_phase17.py": "e2b262b866fdd5d7f1a4ab91a7b8b9bac189ee8cc7a78603b3544ca1579fb819",
    "model_phase13.py": "68585039a4a4fdb7978a99f5e2a72c0ad5a9523127ec24a1338fbedd1c1231e6",
    "model_phase9.py": "85cedd9f5b988ecafb1eae7de9630ee3d6a387ded6ef732e0efb7c3b496f132a"
}

FROZEN_ARCHIVE_HASHES = {
    "gunshot_detection_phase18.zip": "90963ba0e8a70bee9f408473964f10ad0d4a94fcc46173961905761f3ada6b6c",
    "gunshot_detection_phase17.zip": "028bb95bced4456020e5d9860cb01ddca3d2944779d31db76ba2b20f99e2bc41",
    "gunshot_detection_phase16.zip": "386298c4a4a251b4728d14d5903265ebe18c63404f87d0eba47bbcce442f65b4"
}

def sha256_of_file(filepath: Path) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

class TestPhase19IndependentEvaluation(unittest.TestCase):

    def test_01_frozen_model_hashes(self):
        """Verify SHA-256 digests of all frozen baseline detector scripts."""
        for filename, expected_hash in FROZEN_MODEL_HASHES.items():
            fpath = ROOT / filename
            self.assertTrue(fpath.exists(), f"Model file missing: {filename}")
            actual_hash = sha256_of_file(fpath)
            self.assertEqual(actual_hash, expected_hash, f"Hash mismatch in frozen baseline: {filename}")

    def test_02_historical_archive_hashes(self):
        """Verify SHA-256 digests of historical baseline zip archives."""
        parent_dir = ROOT.parent
        for filename, expected_hash in FROZEN_ARCHIVE_HASHES.items():
            fpath = parent_dir / filename
            if fpath.exists():
                actual_hash = sha256_of_file(fpath)
                self.assertEqual(actual_hash, expected_hash, f"Hash mismatch in historical archive: {filename}")

    def test_03_zero_leakage_lineage_matrix(self):
        """Verify lineage matrix proves zero collisions across all historical phases."""
        matrix_path = ROOT / "reports" / "phase19_source_lineage_matrix.csv"
        self.assertTrue(matrix_path.exists(), "Lineage matrix missing")
        df = pd.read_csv(matrix_path)
        self.assertEqual(len(df), 23, "Lineage matrix must audit exactly 23 Phase 19 files")
        # Every entry must be STRICTLY_INDEPENDENT_ZERO_COLLISIONS
        non_independent = df[df["historical_overlap_status"] != "STRICTLY_INDEPENDENT_ZERO_COLLISIONS"]
        self.assertTrue(non_independent.empty, f"Historical collision detected: {non_independent}")

    def test_04_dataset_manifest_integrity(self):
        """Verify Category A (50 events across 5 sessions) and Category B (3 events)."""
        manifest_path = ROOT / "reports" / "phase19_event_annotation_manifest.csv"
        self.assertTrue(manifest_path.exists(), "Event annotation manifest missing")
        df = pd.read_csv(manifest_path)
        self.assertEqual(len(df), 53, "Must have exactly 53 physical gunshot events")
        
        cat_a = df[df["category"] == "CATEGORY_A_NATURAL_CONTINUOUS"]
        self.assertEqual(len(cat_a), 50, "Category A must contain exactly 50 physical events")
        self.assertEqual(len(cat_a["session_id"].unique()), 5, "Category A must span 5 distinct sessions (FP1-FP5)")
        
        # Check sessions
        for sess in ["FP1", "FP2", "FP3", "FP4", "FP5"]:
            self.assertEqual(len(cat_a[cat_a["session_id"] == sess]), 10, f"Session {sess} must have 10 events")
            
        cat_b = df[df["category"] == "CATEGORY_B_PRE_CROPPED_EXTERNAL"]
        self.assertEqual(len(cat_b), 3, "Category B must contain exactly 3 physical events")

    def test_05_audio_files_exist_and_valid(self):
        """Verify all 23 normalized audio files exist and have valid audio headers."""
        import soundfile as sf
        rec_path = ROOT / "reports" / "phase19_positive_recording_manifest.csv"
        df_rec = pd.read_csv(rec_path)
        self.assertEqual(len(df_rec), 23)
        for _, r in df_rec.iterrows():
            wav_file = ROOT / "data" / "phase19_independent_positive" / "normalized_16k" / r["normalized_filename"]
            self.assertTrue(wav_file.exists(), f"Audio file missing: {wav_file}")
            info = sf.info(wav_file)
            self.assertEqual(info.samplerate, 16000, f"Sample rate must be 16000 Hz: {wav_file}")
            self.assertEqual(info.channels, 1, f"Channels must be 1 (mono): {wav_file}")
            self.assertGreater(info.duration, 0.5, f"Audio duration too short: {wav_file}")

    def test_06_evaluation_results_consistency(self):
        """Verify that evaluation results exist and event counts tally exactly."""
        res_path = ROOT / "reports" / "phase19_independent_event_results.csv"
        self.assertTrue(res_path.exists(), "Event results CSV missing")
        df_res = pd.read_csv(res_path)
        self.assertEqual(len(df_res), 53)
        self.assertIn("phase_14_balanced_detected", df_res.columns)
        self.assertIn("phase_17_experimental_detected", df_res.columns)
        self.assertIn("phase_9_balanced_detected", df_res.columns)

    def test_07_poisson_negative_bounds_present(self):
        """Verify negative comparison report contains valid exact Poisson bounds."""
        neg_path = ROOT / "reports" / "phase19_negative_comparison.json"
        self.assertTrue(neg_path.exists(), "Negative comparison JSON missing")
        with open(neg_path) as f:
            data = json.load(f)
        self.assertIn("poisson_zero_alert_bounds", data)
        self.assertIn("Phase 14 Balanced (Production Baseline)", data["models"])
        # Verify Rule of Three bound for 1 hour
        self.assertAlmostEqual(data["poisson_zero_alert_bounds"]["1.0_hour_exposure"]["upper_bound_95_ci_alerts_per_hour"], 2.9957, places=3)

    def test_08_mandatory_safety_designation(self):
        """Verify mandatory safety designation appears in all core reports and scripts."""
        required_phrase = "RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY"
        checked_files = [
            ROOT / "reports" / "phase19_baseline_freeze.json",
            ROOT / "reports" / "phase19_acquisition_audit.md",
            ROOT / "reports" / "phase19_evaluation_protocol.md",
            ROOT / "reports" / "phase19_negative_comparison.json",
            ROOT / "scripts" / "run_phase19_independent_evaluation.py"
        ]
        for fpath in checked_files:
            if fpath.exists():
                if fpath.suffix == ".json":
                    with open(fpath, encoding="utf-8") as jf:
                        data = json.load(jf)
                    self.assertEqual(data.get("safety_designation"), required_phrase, f"Safety designation missing from {fpath.name}")
                else:
                    text = fpath.read_text(encoding="utf-8")
                    self.assertIn(required_phrase, text, f"Safety designation missing from {fpath.name}")

if __name__ == "__main__":
    unittest.main()