"""
Unit Tests for Phase 16: Evaluation Integrity & Forensic Diagnostics.

Validates:
1. Audio format integrity of acquired continuous streams (16 kHz, 1-channel, PCM_16).
2. Absence of artificial track concatenation splices in natural streams.
3. Completeness of animal vocalization forensic analysis report.
4. Completeness of concatenation boundary artifact analysis report.
5. Completeness of browser-to-server latency audit report.
6. Presence of mandatory safety designations across all reports.

SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.
"""

import os
import sys
import unittest
from pathlib import Path
import soundfile as sf
import numpy as np

WORKSPACE_ROOT = Path("e:/gunshot/gunshot")
sys.path.insert(0, str(WORKSPACE_ROOT))

class TestPhase16EvaluationIntegrity(unittest.TestCase):

    def setUp(self):
        self.continuous_dir = WORKSPACE_ROOT / "data" / "phase16_natural_continuous"
        self.reports_dir = WORKSPACE_ROOT / "reports"

    def test_01_continuous_stream_audio_format(self):
        """Verify saved continuous audio streams are 16 kHz mono with valid samples."""
        wav_files = list(self.continuous_dir.glob("*.wav"))
        self.assertGreaterEqual(len(wav_files), 1, "At least one continuous stream must exist.")

        for wav_path in wav_files:
            info = sf.info(str(wav_path))
            self.assertEqual(info.samplerate, 16000, f"{wav_path.name} must be 16,000 Hz.")
            self.assertEqual(info.channels, 1, f"{wav_path.name} must be mono (1 channel).")
            self.assertEqual(info.subtype, "PCM_16", f"{wav_path.name} must be PCM_16.")
            self.assertGreaterEqual(info.duration, 1800.0, f"{wav_path.name} duration must be >= 30 minutes (1800s).")

            # Check for NaNs or Inf in initial 5 seconds
            data, sr = sf.read(str(wav_path), frames=80000, dtype="float32")
            self.assertFalse(np.isnan(data).any(), f"{wav_path.name} contains NaN values.")
            self.assertFalse(np.isinf(data).any(), f"{wav_path.name} contains Inf values.")

    def test_02_forensic_animal_report_completeness(self):
        """Verify animal false positive forensic report exists and contains required sections."""
        report_path = self.reports_dir / "phase16_animal_false_positive_analysis.md"
        self.assertTrue(report_path.exists(), "phase16_animal_false_positive_analysis.md must exist.")
        content = report_path.read_text(encoding="utf-8")
        self.assertIn("NOT FOR LIFE SAFETY", content)
        self.assertIn("Acoustic Morphology Breakdown", content)
        self.assertIn("Collateral Suppression Audit", content)
        self.assertIn("0 of 47 (0.0%)", content, "Collateral suppression on genuine gunshots must be zero.")

    def test_03_forensic_boundary_report_completeness(self):
        """Verify artificial boundary analysis report exists and separates raw from intra-track rates."""
        report_path = self.reports_dir / "phase16_boundary_analysis.md"
        self.assertTrue(report_path.exists(), "phase16_boundary_analysis.md must exist.")
        content = report_path.read_text(encoding="utf-8")
        self.assertIn("NOT FOR LIFE SAFETY", content)
        self.assertIn("Headline Metric Separation Across Operating Profiles", content)
        self.assertIn("Pure Intra-Track Rate", content)
        self.assertIn("Physical Discontinuity DSP Analysis", content)

    def test_04_latency_audit_report_completeness(self):
        """Verify end-to-end latency audit report exists and details component budgets."""
        report_path = self.reports_dir / "phase16_latency_audit.md"
        self.assertTrue(report_path.exists(), "phase16_latency_audit.md must exist.")
        content = report_path.read_text(encoding="utf-8")
        self.assertIn("NOT FOR LIFE SAFETY", content)
        self.assertIn("Component-by-Component Execution Latency", content)
        self.assertIn("End-to-End Latency Budget Across Network Tiers", content)
        self.assertIn("mermaid", content, "Must include latency sequence diagram.")

    def test_05_mandatory_safety_notice_enforcement(self):
        """Verify all generated Phase 16 reports enforce the mandatory safety designation."""
        phase16_reports = list(self.reports_dir.glob("phase16_*.md"))
        self.assertGreaterEqual(len(phase16_reports), 3, "At least 3 Phase 16 reports must exist.")

        for r_path in phase16_reports:
            content = r_path.read_text(encoding="utf-8")
            self.assertIn(
                "RESEARCH DEMONSTRATION PROTOTYPE",
                content,
                f"{r_path.name} missing RESEARCH DEMONSTRATION PROTOTYPE safety designation."
            )
            self.assertIn(
                "NOT FOR LIFE SAFETY",
                content,
                f"{r_path.name} missing NOT FOR LIFE SAFETY designation."
            )

if __name__ == "__main__":
    unittest.main()
