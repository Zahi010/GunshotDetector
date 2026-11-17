"""
Automated Pytest Reproduction & Forensic Verification Suite for Phase 34.

MANDATORY SAFETY DESIGNATION:
RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY
This experimental acoustic machine-learning software is uncertified and must never
be deployed for autonomous emergency dispatch, tactical police response,
active-shooter alerting, automated evacuation, building lockdown, or life-critical
physical security. Safe recorded audio playback only; no live-fire testing.
"""

import os
import sys
import wave
import json
import zipfile
import hashlib
import numpy as np
import pandas as pd
import pytest
from pathlib import Path

WORKSPACE_ROOT = Path(r"E:\gunshot\gunshot")
REPORTS_DIR = WORKSPACE_ROOT / "reports"
ARCHIVE_ROOT = Path(r"E:\gunshot")

def sha256_file(filepath):
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


class TestWorkstream1PhysicalInventory:
    """Workstream 1: 23 physical benchmark audio files, hashes, sample counts, and headers."""

    def test_canonical_23_streams_existence_and_hashes(self):
        csv_path = REPORTS_DIR / "phase34_canonical_23_stream_registry.csv"
        assert csv_path.is_file(), "Phase 34 canonical stream registry must exist"
        df = pd.read_csv(csv_path)
        assert len(df) == 23, "Must contain exactly 23 unique recording records"
        assert df["stable_file_id"].nunique() == 23, "All stable file IDs must be unique"
        assert df["sha256"].nunique() == 23, "All SHA-256 hashes must be distinct (no duplicates)"

        for _, row in df.iterrows():
            abs_path = WORKSPACE_ROOT / row["exact_relative_path"]
            assert abs_path.is_file(), f"File {abs_path} must exist on disk"
            disk_size = abs_path.stat().st_size
            assert disk_size == row["file_size_bytes"], f"Size mismatch for {row['stable_file_id']}"
            disk_hash = sha256_file(abs_path)
            assert disk_hash == row["sha256"], f"Hash mismatch for {row['stable_file_id']}"

    def test_wav_header_sample_consistency(self):
        csv_path = REPORTS_DIR / "phase34_canonical_23_stream_registry.csv"
        df = pd.read_csv(csv_path)

        total_duration_s = 0.0
        for _, row in df.iterrows():
            abs_path = WORKSPACE_ROOT / row["exact_relative_path"]
            with wave.open(str(abs_path), "rb") as w:
                sr = w.getframerate()
                nch = w.getnchannels()
                nf = w.getnframes()
                calc_dur = nf / sr

                assert sr == row["native_sample_rate_hz"], f"Sample rate mismatch for {row['stable_file_id']}"
                assert nch == row["number_of_channels"], f"Channel mismatch for {row['stable_file_id']}"
                assert nf == row["sample_count"], f"Sample count mismatch for {row['stable_file_id']}"
                assert abs(calc_dur - row["wav_header_duration_s"]) < 0.0001, (
                    f"WAV duration calculation mismatch for {row['stable_file_id']}"
                )
                total_duration_s += calc_dur

        assert abs(total_duration_s - 45525.5755) < 0.01, f"Corpus total duration must be 45525.5755s, got {total_duration_s}"
        assert round(total_duration_s / 3600.0, 4) == 12.6460, "Corpus hours must round to 12.6460"


class TestWorkstream2DurationDiscrepancy:
    """Workstream 2: File-level campaign duration sums and Phase 31/32/33 comparison."""

    def test_campaign_duration_totals_from_headers(self):
        csv_path = REPORTS_DIR / "phase34_campaign_mapping_comparison.csv"
        assert csv_path.is_file(), "Campaign mapping comparison CSV must exist"
        df = pd.read_csv(csv_path)
        assert len(df) == 4, "Must contain exactly 4 genuine campaigns"

        camp_map = dict(zip(df["campaign_id"], df["actual_wav_duration_s"]))
        assert abs(camp_map["CAMPAIGN-SOUTHAMPTON-EXP1"] - 19800.0) < 0.01, "Southampton must be 19800.0s (5.5h)"
        assert abs(camp_map["CAMPAIGN-CHEW-MAGNA"] - 2100.0) < 0.01, "Chew Magna must be 2100.0s (0.5833h)"
        assert abs(camp_map["CAMPAIGN-BILBAO"] - 2025.5755) < 0.01, "Bilbao must be 2025.5755s (0.5627h)"
        assert abs(camp_map["CAMPAIGN-ADELAIDE-AEROSONIC"] - 21600.0) < 0.01, "Adelaide must be 21600.0s (6.0h)"

    def test_phase31_vs_phase33_comparison_arithmetic(self):
        csv_path = REPORTS_DIR / "phase34_campaign_mapping_comparison.csv"
        df = pd.read_csv(csv_path)

        for _, row in df.iterrows():
            camp = row["campaign_id"]
            wav_s = row["actual_wav_duration_s"]
            p31_s = row["phase31_reported_s"]
            p33_text_s = row["phase33_text_report_s"]
            p33_csv_s = row["phase33_csv_registry_s"]

            # Phase 31 matches physical WAV headers to < 0.01s across all campaigns
            assert abs(wav_s - p31_s) < 0.01, f"Phase 31 must match actual WAV header for {camp}"
            # Phase 33 CSV registry also matches physical WAV headers
            assert abs(wav_s - p33_csv_s) < 0.01, f"Phase 33 CSV registry must match actual WAV header for {camp}"

            # Document specific discrepancy in Phase 33 text report
            if camp == "CAMPAIGN-SOUTHAMPTON-EXP1":
                assert p33_text_s == 8970.0, "Phase 33 text report had 8970.0s (2.4917h)"
                assert wav_s - p33_text_s == 10830.0, "Delta must be +10830.0s (+3.0083h)"
            elif camp == "CAMPAIGN-CHEW-MAGNA":
                assert p33_text_s == 890.0, "Phase 33 text report had 890.0s (0.2472h)"
                assert wav_s - p33_text_s == 1210.0, "Delta must be +1210.0s (+0.3361h)"
            elif camp == "CAMPAIGN-BILBAO":
                assert abs(p33_text_s - 14065.5755) < 0.01, "Phase 33 text report had 14065.5755s (3.9071h)"
                assert abs(wav_s - p33_text_s - (-12040.0)) < 0.01, "Delta must be -12040.0s (-3.3444h)"
            elif camp == "CAMPAIGN-ADELAIDE-AEROSONIC":
                assert p33_text_s == 21600.0, "Adelaide had 21600.0s (6.0h)"
                assert wav_s - p33_text_s == 0.0, "Delta must be 0.0s"


class TestWorkstream3DetectorMetrics:
    """Workstream 3: Stream-level and campaign-level detector metrics under Conventions A and B."""

    def test_alert_count_consistency_and_sums(self):
        csv_path = REPORTS_DIR / "phase34_stream_level_detector_metrics.csv"
        assert csv_path.is_file(), "Stream level detector metrics CSV must exist"
        df = pd.read_csv(csv_path)
        assert len(df) == 23, "Must contain 23 streams"

        tot_p14_alerts = df["phase14_alerts"].sum()
        tot_p17_alerts = df["phase17_alerts"].sum()
        assert tot_p14_alerts == 128, f"Phase 14 total alerts must be 128, got {tot_p14_alerts}"
        assert tot_p17_alerts == 159, f"Phase 17 total alerts must be 159, got {tot_p17_alerts}"
        assert tot_p14_alerts - tot_p17_alerts == -31, "Total difference must be -31 alerts"

    def test_campaign_level_metrics_sums(self):
        csv_path = REPORTS_DIR / "phase34_campaign_level_metrics.csv"
        assert csv_path.is_file(), "Campaign level metrics CSV must exist"
        df = pd.read_csv(csv_path)

        tot_row = df[df["campaign_id"] == "CUMULATIVE_BENCHMARK_TOTAL"].iloc[0]
        assert tot_row["stream_count"] == 23
        assert tot_row["phase14_alerts"] == 128
        assert tot_row["phase17_alerts"] == 159
        assert abs(tot_row["gross_duration_s"] - 45525.5755) < 0.01
        assert abs(tot_row["gross_duration_hr"] - 12.6460) < 0.001

        # Check Convention A and B excluded times
        assert abs(tot_row["phase14_conv_a_cd_s"] - 255.84) < 0.01
        assert abs(tot_row["phase14_conv_b_cd_s"] - 453.92) < 0.01
        assert abs(tot_row["phase17_conv_a_cd_s"] - 316.56) < 0.01
        assert abs(tot_row["phase17_conv_b_cd_s"] - 6385.20) < 0.01

        # Check Convention B inflation in Phase 17
        aero_row = df[df["campaign_id"] == "CAMPAIGN-ADELAIDE-AEROSONIC"].iloc[0]
        assert abs(aero_row["phase17_conv_b_cd_s"] - 6283.28) < 0.01, (
            "Phase 17 Convention B excluded time on AeroSonic must be 6,283.28s"
        )


class TestWorkstream4CampaignIndependence:
    """Workstream 4: Campaign independence, clustering, and paired differences."""

    def test_campaign_count_and_cluster_skew(self):
        csv_path = REPORTS_DIR / "phase34_campaign_level_metrics.csv"
        df = pd.read_csv(csv_path)
        camps = df[df["campaign_id"] != "CUMULATIVE_BENCHMARK_TOTAL"]
        assert len(camps) == 4, "Must identify exactly 4 genuine campaigns"

        aero = camps[camps["campaign_id"] == "CAMPAIGN-ADELAIDE-AEROSONIC"].iloc[0]
        tot_alerts = camps["phase14_alerts"].sum() + camps["phase17_alerts"].sum()
        aero_alerts = aero["phase14_alerts"] + aero["phase17_alerts"]
        aero_alert_share = aero_alerts / tot_alerts
        # Adelaide generates > 60% of all alerts
        assert aero_alert_share > 0.60, f"Adelaide must generate >60% of alerts, got {aero_alert_share:.2%}"

    def test_paired_metrics_reconciliation(self):
        csv_path = REPORTS_DIR / "phase34_paired_metric_reconciliation.csv"
        assert csv_path.is_file(), "Paired metric reconciliation CSV must exist"
        df = pd.read_csv(csv_path)
        assert len(df) == 23, "Must contain 23 stream pairs"

        zeros = df[df["is_zero_difference"] == True]
        assert len(zeros) == 15, f"Must have exactly 15 zero-difference pairs, got {len(zeros)}"

        non_zeros = df[df["is_zero_difference"] == False]
        assert len(non_zeros) == 8, f"Must have exactly 8 non-zero difference pairs, got {len(non_zeros)}"
        sorted_diffs = sorted(non_zeros["difference_p14_minus_p17"].tolist())
        assert sorted_diffs == [-13, -11, -8, -2, -2, 1, 2, 2]


class TestWorkstream5StatisticalMethodRegister:
    """Workstream 5: Authoritative statistical method register integrity."""

    def test_statistical_method_register_entries(self):
        csv_path = REPORTS_DIR / "phase34_authoritative_statistical_method_register.csv"
        assert csv_path.is_file(), "Method register CSV must exist"
        df = pd.read_csv(csv_path)
        assert len(df) >= 8, "Must contain at least 8 historical method classifications"

        # Check exact method p-values
        methods = dict(zip(df["method_id"], df["exact_p_value"]))
        assert abs(methods["STAT-01"] - 0.1562601) < 1e-5 # SciPy asymptotic
        assert abs(methods["STAT-02"] - 0.2109375) < 1e-6 # Exact tied permutation
        assert abs(methods["STAT-03"] - 0.1953125) < 1e-6 # Exact untied combinatorial
        assert abs(methods["STAT-04"] - 0.3675438) < 1e-5 # Pratt method
        assert abs(methods["STAT-05"] - 0.7265625) < 1e-6 # Sign test
        assert abs(methods["STAT-06"] - 0.0312500) < 1e-6 # Historical multi-credit sign test
        assert abs(methods["STAT-07"] - 0.2187500) < 1e-5 # Pittsburgh 1-to-1 McNemar
        assert abs(methods["STAT-08"] - 0.2500000) < 1e-5 # Pittsburgh incident McNemar


class TestWorkstream6HistoricalCorrections:
    """Workstream 6: Historical report discrepancy register integrity."""

    def test_historical_discrepancy_register_entries(self):
        csv_path = REPORTS_DIR / "phase34_historical_discrepancy_register.csv"
        assert csv_path.is_file(), "Discrepancy register CSV must exist"
        df = pd.read_csv(csv_path)
        assert len(df) >= 9, "Must contain at least 9 documented discrepancy entries"

        phases_audited = df["phase"].unique().tolist()
        for p in ["Phase 27", "Phase 28", "Phase 30", "Phase 31", "Phase 32", "Phase 33"]:
            assert p in phases_audited, f"Phase {p} must be audited in discrepancy register"


class TestWorkstream7ReleaseHygieneAndSafety:
    """Workstream 7: Baseline immutability, safety banner enforcement, and release archive integrity."""

    def test_frozen_baseline_model_invariance(self):
        p14_path = WORKSPACE_ROOT / "model_phase14.py"
        p17_path = WORKSPACE_ROOT / "model_phase17.py"
        cand_path = WORKSPACE_ROOT / "experiments/phase31/model_phase17_state_reset_candidate.py"

        assert sha256_file(p14_path) == "a268551604ae8b73068435ff10ab3d265065f56e0679757fca5b6bf0f061c065"
        assert sha256_file(p17_path) == "e2b262b866fdd5d7f1a4ab91a7b8b9bac189ee8cc7a78603b3544ca1579fb819"
        assert sha256_file(cand_path) == "c144b917b56532787e2a9198f2cad4a77dc2095b57962f31d11d250a4d5d9ea5"

    def test_safety_designation_banner_in_reports(self):
        reports = [f for f in os.listdir(REPORTS_DIR) if f.startswith("phase34_") and f.endswith(".md")]
        assert len(reports) >= 4, "Must contain Phase 34 markdown reports"
        for r in reports:
            with open(REPORTS_DIR / r, "r", encoding="utf-8") as f:
                content = f.read()
            assert "RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY" in content, (
                f"Missing safety banner in {r}"
            )

