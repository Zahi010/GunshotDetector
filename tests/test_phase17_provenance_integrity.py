"""
Unit Tests for Phase 17: Provenance Integrity, Baseline Freeze, and Dataset Lineage.

Validates:
1. Baseline freeze manifest (reports/phase17_baseline_freeze.json).
2. Cryptographic immutability of frozen detectors (model_phase9, model_phase13, model_phase14).
3. Phase 16 archive integrity (gunshot_detection_phase16.zip SHA-256).
4. Positive continuous audio provenance audit and source lineage matrix.
5. Accurate disclosure of open-science unbroken continuous ballistic audio availability limitations.
6. Negative continuous audio provenance manifest (17 continuous soundscapes).
7. Mandatory safety designations across all Phase 17 deliverables.

SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.
"""

import os
import sys
import json
import hashlib
import unittest
from pathlib import Path
import pandas as pd

WORKSPACE_ROOT = Path("e:/gunshot/gunshot").resolve()
sys.path.insert(0, str(WORKSPACE_ROOT))

SAFETY_DESIGNATION = "RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY"


class TestPhase17ProvenanceIntegrity(unittest.TestCase):

    def setUp(self):
        self.reports_dir = WORKSPACE_ROOT / "reports"
        self.freeze_json_path = self.reports_dir / "phase17_baseline_freeze.json"

    def test_01_baseline_freeze_record_exists_and_valid(self):
        """Verify phase17_baseline_freeze.json exists and contains required sections."""
        self.assertTrue(self.freeze_json_path.exists(), "phase17_baseline_freeze.json must exist.")
        with open(self.freeze_json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.assertIn("models", data)
        self.assertIn("current_archives", data)
        self.assertIn("historical_archive_registry", data)
        self.assertIn("NOT FOR LIFE SAFETY", data.get("safety_designation", ""))
        self.assertEqual(data.get("phase"), 17)

    def test_02_frozen_detectors_sha256_immutability(self):
        """Verify model_phase9, model_phase13, model_phase14 match locked SHA-256 digests."""
        expected_hashes = {
            "model_phase14.py": "a268551604ae8b73068435ff10ab3d265065f56e0679757fca5b6bf0f061c065",
            "model_phase13.py": "68585039a4a4fdb7978a99f5e2a72c0ad5a9523127ec24a1338fbedd1c1231e6",
            "model_phase9.py": "85cedd9f5b988ecafb1eae7de9630ee3d6a387ded6ef732e0efb7c3b496f132a"
        }
        for fname, expected_hash in expected_hashes.items():
            fpath = WORKSPACE_ROOT / fname
            self.assertTrue(fpath.exists(), f"Frozen detector file {fname} must exist.")
            actual_hash = hashlib.sha256(fpath.read_bytes()).hexdigest()
            self.assertEqual(
                actual_hash,
                expected_hash,
                f"Frozen detector {fname} SHA-256 has been modified! Expected {expected_hash}, got {actual_hash}"
            )

    def test_03_phase16_archive_integrity(self):
        """Verify gunshot_detection_phase16.zip exists with verified SHA-256 checksum."""
        p16_zip = Path("e:/gunshot") / "gunshot_detection_phase16.zip"
        if not p16_zip.exists():
            p16_zip = WORKSPACE_ROOT.parent / "gunshot_detection_phase16.zip"
        self.assertTrue(p16_zip.exists(), "gunshot_detection_phase16.zip must exist in project root.")
        expected_hash = "386298c4a4a251b4728d14d5903265ebe18c63404f87d0eba47bbcce442f65b4"
        actual_hash = hashlib.sha256(p16_zip.read_bytes()).hexdigest()
        self.assertEqual(
            actual_hash,
            expected_hash,
            f"Phase 16 archive SHA-256 altered! Expected {expected_hash}, got {actual_hash}"
        )

    def test_04_positive_source_lineage_matrix(self):
        """Verify reports/phase17_source_lineage_matrix.csv and continuous manifest accurately document streams."""
        lineage_csv = self.reports_dir / "phase17_source_lineage_matrix.csv"
        manifest_csv = self.reports_dir / "phase17_continuous_positive_manifest.csv"
        self.assertTrue(lineage_csv.exists(), "phase17_source_lineage_matrix.csv must exist.")
        self.assertTrue(manifest_csv.exists(), "phase17_continuous_positive_manifest.csv must exist.")

        df_lineage = pd.read_csv(lineage_csv)
        self.assertEqual(len(df_lineage), 4, "Must audit all 4 repository sources.")

        # Verify Mitchell range campaign is classified as HISTORICALLY_RELATED_SESSION
        mitchell_repo = df_lineage[df_lineage["provenance_classification"] == "HISTORICALLY_RELATED_SESSION"]
        self.assertEqual(len(mitchell_repo), 1, "Must contain Mitchell range campaign.")

        df_man = pd.read_csv(manifest_csv)
        self.assertEqual(len(df_man), 4, "Must contain all 4 evaluation streams.")
        mitchell_stream = df_man[df_man["provenance_status"] == "HISTORICALLY_RELATED_SESSION"]
        self.assertEqual(len(mitchell_stream), 1, "Must classify Mitchell stream as HISTORICALLY_RELATED_SESSION.")

    def test_05_open_science_availability_disclosure(self):
        """Verify phase17_positive_continuous_provenance.md documents open-science repository limits."""
        prov_md = self.reports_dir / "phase17_positive_continuous_provenance.md"
        self.assertTrue(prov_md.exists(), "phase17_positive_continuous_provenance.md must exist.")
        content = prov_md.read_text(encoding="utf-8")
        self.assertIn("Zenodo", content, "Must audit Zenodo repository holdings.")
        self.assertIn("pre-cropped", content, "Must disclose that open-science recordings are pre-cropped.")
        self.assertIn("NOT FOR LIFE SAFETY", content, "Must feature mandatory safety designation.")

    def test_06_negative_continuous_source_manifest(self):
        """Verify phase17_negative_source_manifest.csv documents all 17 continuous soundscapes."""
        neg_csv = self.reports_dir / "phase17_negative_source_manifest.csv"
        self.assertTrue(neg_csv.exists(), "phase17_negative_source_manifest.csv must exist.")
        df = pd.read_csv(neg_csv)
        self.assertEqual(len(df), 17, "Must document all 17 continuous negative streams (11 Phase 16 + 6 Phase 17).")
        total_duration = df["duration_sec"].sum()
        self.assertGreaterEqual(total_duration, 23000.0, "Total negative exposure must exceed 6.4 hours.")

    def test_07_mandatory_safety_designation_in_reports(self):
        """Verify mandatory safety banner in all generated Phase 17 technical reports."""
        report_files = [
            "phase17_positive_continuous_provenance.md",
            "phase17_annotation_audit.md",
            "phase17_long_duration_negative_evaluation.md",
            "phase17_animal_suppression_experiment.md",
            "phase17_high_precision_zero_alert_audit.md",
            "phase17_continuous_event_results.md",
            "phase17_latency_audit.md",
            "phase17_statistical_analysis.md"
        ]
        for r_name in report_files:
            r_path = self.reports_dir / r_name
            self.assertTrue(r_path.exists(), f"Report {r_name} must exist.")
            content = r_path.read_text(encoding="utf-8")
            self.assertIn(
                SAFETY_DESIGNATION,
                content,
                f"Report {r_name} must contain mandatory safety designation: {SAFETY_DESIGNATION}"
            )


if __name__ == "__main__":
    unittest.main()
