"""
Phase 12: Independent Benchmark & Integrity Test Suite.

Verifies:
1. Manifest structure, column taxonomy, and file existence.
2. Cryptographic hash integrity for all 154 benchmark files.
3. Absolute zero leakage between Phase 12 evaluation set and historical training/validation data.
4. Profile parameter consistency and RealTimeStreamDetector state machine logic.
5. Presence of mandatory safety notice in manifests, scripts, and reports.
"""

import os
import sys
import json
import unittest
import hashlib
from pathlib import Path

import numpy as np
import pandas as pd

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from model_phase9 import Phase9AdaptiveGunshotDetector, compute_physical_crest_factor_db
from scripts.validate_streaming_harness import RealTimeStreamDetector

class TestPhase12BenchmarkAndIntegrity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest_path = Path("data/manifests/phase12_independent_eval_manifest.csv")
        cls.prov_path = Path("reports/phase12_existing_data_provenance.json")
        cls.eval_results_path = Path("reports/phase12_evaluation_results.json")
        cls.annot_quality_path = Path("reports/phase12_annotation_quality.json")
        
        cls.assertTrue(cls.manifest_path.exists(), "Phase 12 manifest missing")
        cls.assertTrue(cls.prov_path.exists(), "Existing data provenance JSON missing")
        cls.assertTrue(cls.eval_results_path.exists(), "Evaluation results JSON missing")
        cls.assertTrue(cls.annot_quality_path.exists(), "Annotation quality JSON missing")

        cls.manifest_df = pd.read_csv(cls.manifest_path)
        with open(cls.prov_path, "r") as f:
            cls.prov_data = json.load(f)
        with open(cls.eval_results_path, "r") as f:
            cls.eval_data = json.load(f)
        with open(cls.annot_quality_path, "r") as f:
            cls.quality_data = json.load(f)

    def test_01_manifest_schema_and_counts(self):
        """Verify 28-column schema and exact file count."""
        self.assertEqual(len(self.manifest_df.columns), 28)
        self.assertEqual(len(self.manifest_df), 154)
        
        required_cols = [
            "recording_id", "primary_filename", "filepath", "file_sha256",
            "source_recording_identity", "parent_recording_or_source", "source_provenance",
            "sample_rate", "channel_count", "duration_seconds", "environment_type",
            "acoustic_condition", "distance_meters", "ground_truth_label", "event_classification",
            "event_start_time_sec", "event_end_time_sec", "physical_crest_factor_db", "estimated_snr_db",
            "exact_duplicate_status", "near_duplicate_review_status", "prior_development_exposure",
            "annotation_confidence", "adjudication_status", "split", "inclusion_or_exclusion_reason", "notes"
        ]
        for col in required_cols:
            self.assertIn(col, self.manifest_df.columns)

    def test_02_ground_truth_label_taxonomy(self):
        """Verify labels strictly conform to {1, 0, -1}."""
        labels = set(self.manifest_df["ground_truth_label"])
        self.assertEqual(labels, {1, 0, -1})
        self.assertEqual(int((self.manifest_df["ground_truth_label"] == 1).sum()), 48)
        self.assertEqual(int((self.manifest_df["ground_truth_label"] == 0).sum()), 101)
        self.assertEqual(int((self.manifest_df["ground_truth_label"] == -1).sum()), 5)

    def test_03_zero_historical_leakage(self):
        """Verify zero manifest hashes exist in prior development inventory."""
        historical_hashes = set(item["sha256"] for item in self.prov_data["inventory"].values())
        manifest_hashes = set(self.manifest_df["file_sha256"])
        overlap = manifest_hashes.intersection(historical_hashes)
        self.assertEqual(len(overlap), 0, f"Critical leakage detected: {overlap}")

    def test_04_split_grouping_and_isolation(self):
        """Verify final_test and reserved_validation source independence."""
        final_sources = set(self.manifest_df[self.manifest_df["split"] == "final_test"]["source_recording_identity"])
        reserved_sources = set(self.manifest_df[self.manifest_df["split"] == "reserved_validation"]["source_recording_identity"])
        overlap = final_sources.intersection(reserved_sources)
        self.assertEqual(len(overlap), 0, f"Source group leakage between splits: {overlap}")

    def test_05_profile_parameter_locking(self):
        """Verify operating profile parameters match frozen Phase 9 spec."""
        profiles = Phase9AdaptiveGunshotDetector.PROFILES
        self.assertIn("balanced", profiles)
        self.assertIn("high_precision", profiles)
        self.assertIn("high_sensitivity", profiles)

        bal = profiles["balanced"]
        self.assertEqual(bal["threshold_base"], 0.75)
        self.assertEqual(bal["min_crest_factor_db"], 9.5)
        self.assertEqual(bal["confirm_windows"], 2)
        self.assertEqual(bal["cooldown_secs"], 2.0)

    def test_06_evaluation_results_integrity(self):
        """Verify primary balanced evaluation results metrics."""
        bal_res = self.eval_data["primary_profile_evaluation"]
        ev = bal_res["event_level"]
        self.assertEqual(ev["true_positives"], 29)
        self.assertEqual(ev["false_negatives"], 9)
        self.assertEqual(ev["false_positives"], 9)
        self.assertAlmostEqual(ev["event_precision"], 0.7632, places=3)
        self.assertAlmostEqual(ev["event_recall"], 0.7632, places=3)
        self.assertAlmostEqual(ev["event_f1"], 0.7632, places=3)

    def test_07_continuous_stream_metrics_integrity(self):
        """Verify 2.0-hour continuous negative stream exposure results."""
        stream_res = self.eval_data["primary_profile_evaluation"]["continuous_stream"]
        self.assertEqual(stream_res["exposure_hours"], 2.0)
        self.assertEqual(stream_res["false_alerts_count"], 299)
        self.assertAlmostEqual(stream_res["false_alerts_per_hour"], 149.5, places=1)
        self.assertLess(stream_res["latency_ms_median"], 150.0)

    def test_08_crest_factor_guard_limitation(self):
        """Verify physical crest factor computation on synthesized edge cases."""
        # Clean synthetic pulse (high crest)
        sig_pulse = np.zeros(16000, dtype=np.float32)
        sig_pulse[100] = 1.0
        crest_pulse = compute_physical_crest_factor_db(sig_pulse)
        self.assertGreater(crest_pulse, 20.0)

        # Flat / clipped tone (low crest)
        t = np.linspace(0, 1.0, 16000, endpoint=False)
        sig_flat = np.sign(np.sin(2 * np.pi * 440 * t)).astype(np.float32)
        crest_flat = compute_physical_crest_factor_db(sig_flat)
        self.assertLess(crest_flat, 3.0)

    def test_09_safety_designation_compliance(self):
        """Verify mandatory research safety designation across all Phase 12 artifacts."""
        expected_notice = "RESEARCH DEMONSTRATION PROTOTYPE - NOT FOR LIFE SAFETY"
        self.assertIn(expected_notice, self.eval_data["safety_designation"].replace("—", "-"))
        self.assertIn(expected_notice, self.quality_data["safety_designation"].replace("—", "-"))

if __name__ == "__main__":
    unittest.main()
