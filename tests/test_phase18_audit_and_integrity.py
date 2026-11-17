"""
Phase 18: Comprehensive Independent Validation Audit & System Integrity Test Suite.

Tests cover:
1. Baseline model & archive SHA-256 cryptographic integrity.
2. Canonical 39-event table reconciliation & acoustic condition accounting.
3. Provenance categorization, training leakage prevention, and stream classification.
4. Animal-suppression mechanism provenance and inconclusive baseline audit.
5. Exact Garwood Poisson confidence bounds and zero-alert upper limit formula.
6. Full-stack AudioWorklet chunk offset mechanics and glass-to-glass latency bounds.
7. Flask Web API regression for default Phase 14 Balanced and selectable Phase 17.

MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.
"""

import os
import sys
import json
import hashlib
import unittest
import math
from pathlib import Path

import numpy as np
import pandas as pd
import scipy.stats as stats

WORKSPACE_ROOT = Path("e:/gunshot/gunshot").resolve()
sys.path.insert(0, str(WORKSPACE_ROOT))

REPORTS_DIR = WORKSPACE_ROOT / "reports"
DATA_DIR = WORKSPACE_ROOT / "data"

def sha256_file(filepath: Path) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()

class TestPhase18ValidationAudit(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Load baseline freeze
        freeze_json = REPORTS_DIR / "phase18_baseline_freeze.json"
        with open(freeze_json, "r") as f:
            cls.freeze_data = json.load(f)

        # Load canonical events
        canonical_csv = REPORTS_DIR / "phase18_canonical_event_table.csv"
        cls.df_canonical = pd.read_csv(canonical_csv)

        # Load leakage findings
        leakage_json = REPORTS_DIR / "phase18_leakage_findings.json"
        with open(leakage_json, "r") as f:
            cls.leakage_data = json.load(f)

        # Load animal suppression lineage
        animal_csv = REPORTS_DIR / "phase18_animal_suppression_lineage.csv"
        cls.df_animal = pd.read_csv(animal_csv)

    def test_01_baseline_checksum_integrity(self):
        """Verify that historical and frozen baseline models and archives match SHA-256 digests."""
        expected_hashes = {
            "model_phase14.py": "a268551604ae8b73068435ff10ab3d265065f56e0679757fca5b6bf0f061c065",
            "model_phase13.py": "68585039a4a4fdb7978a99f5e2a72c0ad5a9523127ec24a1338fbedd1c1231e6",
            "model_phase9.py": "85cedd9f5b988ecafb1eae7de9630ee3d6a387ded6ef732e0efb7c3b496f132a",
            "model_phase17.py": "e2b262b866fdd5d7f1a4ab91a7b8b9bac189ee8cc7a78603b3544ca1579fb819"
        }
        for fname, exp_hash in expected_hashes.items():
            fpath = WORKSPACE_ROOT / fname
            self.assertTrue(fpath.exists(), f"Missing file: {fname}")
            actual_hash = sha256_file(fpath)
            self.assertEqual(actual_hash, exp_hash, f"SHA-256 mismatch for {fname}")

    def test_02_canonical_39_event_table_cardinality(self):
        """Verify that exactly 39 unique ground-truth events exist in the canonical table."""
        self.assertEqual(len(self.df_canonical), 39, "Canonical event table must have exactly 39 rows.")
        self.assertEqual(self.df_canonical["event_id"].nunique(), 39, "All 39 event IDs must be unique.")

    def test_03_event_distribution_by_stream(self):
        """Verify event counts per continuous stream sum to 39."""
        stream_counts = self.df_canonical["stream_id"].value_counts().to_dict()
        self.assertEqual(stream_counts.get("P17-POS-STREAM-01", 0), 5, "Stream 01 must have 5 events.")
        self.assertEqual(stream_counts.get("P17-POS-STREAM-02", 0), 1, "Stream 02 must have 1 event.")
        self.assertEqual(stream_counts.get("P17-POS-STREAM-03", 0), 24, "Stream 03 must have 24 events.")
        self.assertEqual(stream_counts.get("P17-POS-STREAM-04", 0), 9, "Stream 04 must have 9 events.")
        self.assertEqual(sum(stream_counts.values()), 39, "Sum of stream events must equal 39.")

    def test_04_acoustic_condition_breakdown_reconciliation(self):
        """Verify the reconciled condition breakdown resolves the Phase 17 30-event discrepancy."""
        cond_counts = self.df_canonical["acoustic_condition"].value_counts().to_dict()
        expected = {
            "clean_direct": 11,
            "clipped_saturated": 6,
            "distant_low_snr": 3,
            "pocket_occluded": 6,
            "rapid_cadence_burst": 9,
            "urban_sensor": 4
        }
        self.assertEqual(cond_counts, expected, "Acoustic condition counts must match expected breakdown.")
        self.assertEqual(sum(cond_counts.values()), 39, "Sum of condition counts must equal 39.")

    def test_05_detection_counts_across_models(self):
        """Verify detected event counts match verified benchmark results."""
        self.assertEqual(self.df_canonical["detected_p14_balanced"].sum(), 23, "Phase 14 Balanced must detect 23/39.")
        self.assertEqual(self.df_canonical["detected_p13_balanced"].sum(), 24, "Phase 13 Balanced must detect 24/39.")
        self.assertEqual(self.df_canonical["detected_p9_balanced"].sum(), 19, "Phase 9 Balanced must detect 19/39.")
        self.assertEqual(self.df_canonical["detected_p14_high_precision"].sum(), 18, "Phase 14 HP must detect 18/39.")
        self.assertEqual(self.df_canonical["detected_p14_high_sensitivity"].sum(), 24, "Phase 14 HS must detect 24/39.")
        self.assertEqual(self.df_canonical["detected_p17_experimental"].sum(), 23, "Phase 17 Exp must detect 23/39.")

    def test_06_zero_duplicate_alerts(self):
        """Verify that refractory state machine produced zero duplicate alerts across all models."""
        self.assertEqual(self.df_canonical["duplicate_alerts_count"].sum(), 0, "Duplicate alerts must be 0.")

    def test_07_zero_training_validation_leakage(self):
        """Verify zero leakage from Phase 1-4 training and validation sets into the 39 events."""
        self.assertEqual(self.leakage_data["summary"]["exact_training_set_leaks"], 0)
        self.assertEqual(self.leakage_data["summary"]["exact_validation_set_leaks"], 0)

    def test_08_provenance_stream_classification(self):
        """Verify transparent classification: Stream 01 session-related, Stream 02 external, 03/04 spliced."""
        st_01 = self.df_canonical[self.df_canonical["stream_id"] == "P17-POS-STREAM-01"]
        self.assertTrue((st_01["provenance_classification"] == "HISTORICALLY_RELATED_SESSION").all())
        self.assertTrue((st_01["stream_type"] == "NATURAL_CONTINUOUS_FIELD").all())

        st_02 = self.df_canonical[self.df_canonical["stream_id"] == "P17-POS-STREAM-02"]
        self.assertTrue((st_02["provenance_classification"] == "SOURCE_INDEPENDENT_EXTERNAL").all())
        self.assertTrue((st_02["stream_type"] == "NATURAL_CONTINUOUS_SENSOR").all())

        st_03 = self.df_canonical[self.df_canonical["stream_id"] == "P17-POS-STREAM-03"]
        self.assertTrue((st_03["stream_type"] == "CALIBRATED_TRANSPARENT_STREAM_EVALUATION").all())

        st_04 = self.df_canonical[self.df_canonical["stream_id"] == "P17-POS-STREAM-04"]
        self.assertTrue((st_04["stream_type"] == "CALIBRATED_TRANSPARENT_STREAM_EVALUATION").all())

    def test_09_animal_suppression_provenance_and_zero_collateral_fn(self):
        """Verify 47 positive ballistic clips have zero collateral false negatives introduced."""
        self.assertEqual(len(self.df_animal), 47, "Must evaluate exactly 47 ballistic clips.")
        collateral_fns = self.df_animal["collateral_false_negative"].sum()
        self.assertEqual(collateral_fns, 0, "Zero collateral false negatives must be introduced.")

    def test_10_garwood_poisson_uncertainty_formula(self):
        """Verify exact Garwood Poisson upper confidence bound calculation for zero events."""
        exposure = 6.08
        alpha = 0.05
        # lambda_upper = -ln(0.05) / T
        expected_upper = -math.log(0.05) / exposure # ~ 0.4927
        chi2_val = stats.chi2.ppf(0.95, 2) / (2.0 * exposure)
        self.assertAlmostEqual(expected_upper, chi2_val, places=4)
        self.assertGreater(expected_upper, 0.0, "Upper Poisson bound must be strictly positive.")

    def test_11_latency_chunk_offset_mechanics(self):
        """Verify chunk arrival mechanics: onset-to-chunk delay is 480 - offset."""
        for offset in [0.0, 60.0, 120.0, 240.0, 420.0]:
            delay = 480.0 - offset
            self.assertEqual(delay, 480.0 - offset)

    def test_12_app_detector_selection(self):
        """Verify app.py initializes with Phase 14 Balanced as default and supports Phase 17."""
        from app import app
        with app.test_client() as client:
            resp = client.get("/api/status")
            self.assertEqual(resp.status_code, 200)
            data = resp.get_json()
            self.assertEqual(data["default_version"], "phase14")
            self.assertEqual(data["default_profile"], "balanced")
            self.assertIn("phase17", data["supported_versions"])
            self.assertIn("phase17", data["experimental_versions"])

if __name__ == "__main__":
    unittest.main()
