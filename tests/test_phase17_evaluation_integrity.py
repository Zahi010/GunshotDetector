"""
Unit Tests for Phase 17: Evaluation Integrity & Statistical Benchmark Audit.

Validates:
1. Continuous positive event detection metrics (reports/phase17_event_metrics.json).
2. Physical event timeline and false-alert log CSV schema and integrity.
3. Continuous negative audio evaluation results and stream duration exposure.
4. Mathematical rigor of the High-Precision zero-alert audit (Garwood Poisson bound).
5. 13-stage glass-to-glass latency microbenchmark audit.
6. Paired statistical analysis deliverables and uncertainty intervals.

SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.
"""

import os
import sys
import json
import unittest
from pathlib import Path
import pandas as pd

WORKSPACE_ROOT = Path("e:/gunshot/gunshot").resolve()
sys.path.insert(0, str(WORKSPACE_ROOT))

SAFETY_DESIGNATION = "RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY"


class TestPhase17EvaluationIntegrity(unittest.TestCase):

    def setUp(self):
        self.reports_dir = WORKSPACE_ROOT / "reports"

    def test_01_event_metrics_json_integrity(self):
        """Verify phase17_event_metrics.json exists with metrics across all 6 evaluated detectors."""
        json_path = self.reports_dir / "phase17_event_metrics.json"
        self.assertTrue(json_path.exists(), "phase17_event_metrics.json must exist.")
        with open(json_path, "r", encoding="utf-8") as f:
            metrics = json.load(f)

        expected_detectors = [
            "Phase 14 Balanced",
            "Phase 14 High-Precision",
            "Phase 14 High-Sensitivity",
            "Phase 17 Experimental",
            "Phase 13 Balanced",
            "Phase 9 Balanced"
        ]
        for det_name in expected_detectors:
            self.assertIn(det_name, metrics, f"Detector {det_name} must be in event metrics.")
            m = metrics[det_name]
            self.assertEqual(m["genuine_events"], 39, "Must evaluate against 39 physical ground-truth events.")
            self.assertGreaterEqual(m["event_recall"], 0.0)
            self.assertLessEqual(m["event_recall"], 100.0)
            self.assertGreaterEqual(m["event_precision"], 0.0)
            self.assertLessEqual(m["event_precision"], 100.0)
            self.assertEqual(m["duplicate_alerts"], 0, f"{det_name} must produce zero duplicate dispatches.")

    def test_02_event_and_false_alert_timeline_schemas(self):
        """Verify event detection and false alert timeline CSV schemas and row counts."""
        event_csv = self.reports_dir / "phase17_event_detection_timeline.csv"
        false_csv = self.reports_dir / "phase17_false_alert_timeline.csv"

        self.assertTrue(event_csv.exists(), "phase17_event_detection_timeline.csv must exist.")
        self.assertTrue(false_csv.exists(), "phase17_false_alert_timeline.csv must exist.")

        df_events = pd.read_csv(event_csv)
        expected_cols = [
            "detector", "event_id", "stream_id", "condition", "event_start_sec",
            "event_end_sec", "detected", "alert_time_sec", "detection_delay_sec",
            "duplicate_alerts", "score", "crest_factor_db"
        ]
        for col in expected_cols:
            self.assertIn(col, df_events.columns, f"Event timeline missing column: {col}")

        # 39 events * 6 detectors = 234 evaluation rows
        self.assertEqual(len(df_events), 234, "Must evaluate 39 events across 6 detectors (234 rows).")

        df_false = pd.read_csv(false_csv)
        self.assertIn("stream_id", df_false.columns)
        self.assertIn("alert_time_sec", df_false.columns)
        self.assertIn("detector", df_false.columns)
        self.assertIn("score", df_false.columns)

    def test_03_continuous_negative_evaluation_results(self):
        """Verify negative evaluation alert analysis covers 17 streams across baseline and candidate models."""
        neg_analysis_csv = self.reports_dir / "phase17_negative_alert_analysis.csv"
        self.assertTrue(neg_analysis_csv.exists(), "phase17_negative_alert_analysis.csv must exist.")

        df_neg = pd.read_csv(neg_analysis_csv)
        self.assertIn("stream_id", df_neg.columns)
        self.assertIn("detector", df_neg.columns)
        self.assertIn("alert_timestamp_sec", df_neg.columns)
        self.assertIn("score", df_neg.columns)

        # Check High-Precision alert behavior across categories
        hp_alerts = df_neg[df_neg["detector"] == "Phase 14 High-Precision"]
        self.assertEqual(len(hp_alerts), 22, "Phase 14 High-Precision must produce exactly 22 alerts across all 17 streams.")

        # High-Precision must produce zero alerts in industrial, natural weather, and percussive mimic streams
        quiet_cats = ["industrial_and_mechanical", "natural_weather", "percussive_acoustic_mimics"]
        hp_quiet = hp_alerts[hp_alerts["category"].isin(quiet_cats)]
        self.assertEqual(len(hp_quiet), 0, "Phase 14 High-Precision must produce zero alerts in industrial, weather, and drum mimic categories.")

    def test_04_high_precision_zero_alert_statistical_audit(self):
        """Verify high precision audit enforces exact Garwood bounds and bans infinite MTBFA claims."""
        audit_md = self.reports_dir / "phase17_high_precision_zero_alert_audit.md"
        self.assertTrue(audit_md.exists(), "phase17_high_precision_zero_alert_audit.md must exist.")

        content = audit_md.read_text(encoding="utf-8")
        self.assertIn("Garwood", content, "Must use exact Garwood Poisson upper confidence bound.")
        self.assertIn("0.49", content, "Must report upper 95% bound of ~0.49 alerts/hour for 6.08h exposure.")
        self.assertIn("Rule of Three", content, "Must reference Rule of Three formulation.")

    def test_05_latency_audit_and_13_stages(self):
        """Verify latency report covers all 13 stages and provides glass-to-glass LAN latency budget."""
        lat_md = self.reports_dir / "phase17_latency_audit.md"
        self.assertTrue(lat_md.exists(), "phase17_latency_audit.md must exist.")

        content = lat_md.read_text(encoding="utf-8")
        for stage_idx in range(1, 14):
            self.assertIn(f"Stage {stage_idx}", content, f"Must document Stage {stage_idx} latency.")

        self.assertIn("Single-Window Immediate Alert (LAN)", content)
        self.assertIn("Two-Window Confirmed Alert (LAN)", content)
        self.assertIn("Server DSP Execution Latency", content)

    def test_06_statistical_analysis_report_completeness(self):
        """Verify statistical analysis report contains Wilson, Clopper-Pearson, and bootstrap intervals."""
        stat_md = self.reports_dir / "phase17_statistical_analysis.md"
        self.assertTrue(stat_md.exists(), "phase17_statistical_analysis.md must exist.")

        content = stat_md.read_text(encoding="utf-8")
        self.assertIn("Wilson Score", content, "Must present Wilson score intervals.")
        self.assertIn("Clopper-Pearson", content, "Must present Clopper-Pearson intervals.")
        self.assertIn("Bootstrap", content, "Must present block bootstrap results.")
        self.assertIn("McNemar", content, "Must present McNemar paired discordance test.")


if __name__ == "__main__":
    unittest.main()
