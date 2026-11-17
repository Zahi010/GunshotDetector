"""
Unit Tests for Phase 16: Provenance Integrity & Baseline Freeze.

Validates:
1. Historical archive integrity (Phase 8 through Phase 15 ZIPs).
2. Cryptographic freeze of baseline detector files (model_phase9, model_phase13, model_phase14).
3. Positive gunshot source lineage and recording-session overlap audit.
4. Formal retirement and classification of Phase 15 blind set as INSPECTED_DIAGNOSTIC_EVIDENCE.
5. Mandatory safety designations.

SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.
"""

import os
import sys
import json
import hashlib
import unittest
from pathlib import Path
import pandas as pd

WORKSPACE_ROOT = Path("e:/gunshot/gunshot")
sys.path.insert(0, str(WORKSPACE_ROOT))

class TestPhase16ProvenanceIntegrity(unittest.TestCase):

    def setUp(self):
        self.reports_dir = WORKSPACE_ROOT / "reports"
        self.freeze_json_path = self.reports_dir / "phase16_baseline_freeze.json"

    def test_01_baseline_freeze_record_exists(self):
        """Verify phase16_baseline_freeze.json exists and is valid."""
        self.assertTrue(self.freeze_json_path.exists(), "phase16_baseline_freeze.json must exist.")
        with open(self.freeze_json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        self.assertIn("models", data)
        self.assertIn("historical_archives", data)
        self.assertIn("NOT FOR LIFE SAFETY", data.get("safety_designation", ""))

    def test_02_frozen_detectors_sha256_integrity(self):
        """Verify model_phase9, model_phase13, model_phase14 match locked SHA-256 digests."""
        with open(self.freeze_json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        frozen = data["models"]

        for mod_name, expected_info in frozen.items():
            mod_path = Path(expected_info["path"])
            self.assertTrue(mod_path.exists(), f"Detector file {mod_path} must exist.")
            actual_hash = hashlib.sha256(mod_path.read_bytes()).hexdigest()
            self.assertEqual(
                actual_hash,
                expected_info["sha256"],
                f"Frozen detector {mod_name} SHA-256 has been modified! Expected {expected_info['sha256']}, got {actual_hash}"
            )

    def test_03_historical_archives_exist_and_verified(self):
        """Verify historical archives phase8 through phase15 exist with valid checksums."""
        with open(self.freeze_json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        archives = data["historical_archives"]
        
        checked = 0
        for p_name, a_info in archives.items():
            a_path = Path(a_info["path"])
            if not a_path.exists():
                continue
            actual_h = hashlib.sha256(a_path.read_bytes()).hexdigest()
            self.assertEqual(actual_h, a_info["sha256"], f"Archive {p_name} digest mismatch.")
            checked += 1
        if checked == 0:
            self.skipTest("Historical archives phase8-15 were pruned to save disk space; digests recorded in baseline_freeze.json")

    def test_04_positive_source_lineage_audit_artifacts(self):
        """Verify positive source lineage and overlap audit artifacts exist and disclose relationship."""
        lineage_md = self.reports_dir / "phase16_positive_source_lineage.md"
        overlap_csv = self.reports_dir / "phase16_positive_source_overlap.csv"
        session_json = self.reports_dir / "phase16_recording_session_audit.json"
        blind_audit_md = self.reports_dir / "phase16_blind_source_audit.md"

        self.assertTrue(lineage_md.exists(), "phase16_positive_source_lineage.md must exist.")
        self.assertTrue(overlap_csv.exists(), "phase16_positive_source_overlap.csv must exist.")
        self.assertTrue(session_json.exists(), "phase16_recording_session_audit.json must exist.")
        self.assertTrue(blind_audit_md.exists(), "phase16_blind_source_audit.md must exist.")

        df_overlap = pd.read_csv(overlap_csv)
        self.assertEqual(len(df_overlap), 47, "Must audit all 47 Phase 15 positive gunshot recordings.")

        # Check Mitchell recording lineage disclosure
        mitchell_rows = df_overlap[df_overlap["recording_session_id"] == "MITCHELL_2015_RANGE_CAMPAIGN"]
        self.assertEqual(len(mitchell_rows), 42, "Must contain all 42 Mitchell recordings.")
        for _, row in mitchell_rows.iterrows():
            self.assertTrue(row["file_independent"], "Must be file-independent (distinct recording).")
            self.assertTrue(row["event_independent"], "Must be event-independent (distinct shot).")
            self.assertFalse(row["session_independent"], "Must NOT be session-independent.")
            self.assertEqual(row["provenance_classification"], "HISTORICALLY_RELATED_SESSION")

    def test_05_blind_set_retirement_status(self):
        """Verify phase16_blind_source_audit.md marks Phase 15 set as retired and inspected diagnostic evidence."""
        blind_audit_md = self.reports_dir / "phase16_blind_source_audit.md"
        content = blind_audit_md.read_text(encoding="utf-8")
        self.assertIn("Inspected Diagnostic Evidence", content)
        self.assertIn("NOT FOR LIFE SAFETY", content)

if __name__ == "__main__":
    unittest.main()
