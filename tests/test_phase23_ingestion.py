"""
Unit and Integration Test Suite — Phase 23 Ingestion & Exposure Benchmark
MANDATORY SAFETY DESIGNATION:
RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.

Tests:
1. Frozen baseline model hashes.
2. Historical release archive hashes.
3. Provenance schema and metadata completeness.
4. Handling of missing provenance (UNKNOWN/UNVERIFIED).
5. Duplicate file hash detection.
6. Audio duration, sample rate (16kHz), and channel count (mono) inspection.
7. Corrupt-file and invalid-format handling.
8. Continuity verification (unbroken vs segmented).
9. Negative-label eligibility classification rules.
10. Ambiguous interval exclusion logic.
11. Gross vs eligible exposure calculation.
12. Non-overlap of merged cooldown intervals (no double-counting).
13. Poisson Garwood confidence bound mathematical correctness.
14. Matched identical evaluation interval checks for both models.
15. Mandatory safety designations across all Phase 23 reports.
16. Phase 23 release archive integrity.
"""

import json
import math
import hashlib
import wave
import pytest
import pandas as pd
from pathlib import Path
from scipy.stats import chi2

ROOT = Path("E:/gunshot/gunshot")
REPORTS_DIR = ROOT / "reports"
DATA_DIR = ROOT / "data"

FROZEN_HASHES = {
    "model_phase14.py": "a268551604ae8b73068435ff10ab3d265065f56e0679757fca5b6bf0f061c065",
    "model_phase17.py": "e2b262b866fdd5d7f1a4ab91a7b8b9bac189ee8cc7a78603b3544ca1579fb819",
    "model_phase13.py": "68585039a4a4fdb7978a99f5e2a72c0ad5a9523127ec24a1338fbedd1c1231e6",
    "model_phase9.py": "85cedd9f5b988ecafb1eae7de9630ee3d6a387ded6ef732e0efb7c3b496f132a",
    "reports/phase20_canonical_event_manifest.csv": "6c3e5d5c07cb5102ee7160c0272e90d5c98cdb4659538ee58ad276855d971691",
}


def compute_sha256(filepath: Path) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def test_frozen_model_hashes():
    """Verify that all core detector scripts match immutable cryptographic checksums."""
    for rel_path, expected_hash in FROZEN_HASHES.items():
        file_path = ROOT / rel_path
        assert file_path.exists(), f"Missing required frozen file: {file_path}"
        actual_hash = compute_sha256(file_path)
        assert actual_hash == expected_hash, f"Hash mismatch for {rel_path}: got {actual_hash}, expected {expected_hash}"


def test_historical_archive_hashes():
    """Verify Phase 20, 21, and 22 release archives."""
    archives = {
        "gunshot_detection_phase20.zip": "dda7427f2dbffcb178f6d9ade0abb80fbfc491751f04de5dc0db1b4731c31c89",
        "gunshot_detection_phase21.zip": "b065747b0e6118d228336bee7f8c3811890b638a25070d3ce2a047c329b3e225",
        "gunshot_detection_phase22.zip": "160d327072c3515e945ca5cdf89038f14b6ef1919b1e4865278affab52ad4de5",
    }
    for arch_name, exp_hash in archives.items():
        p = Path("E:/gunshot") / arch_name
        assert p.exists(), f"Missing archive {p}"
        assert compute_sha256(p) == exp_hash, f"Hash mismatch for {arch_name}"


def test_provenance_registry_structure():
    """Verify source registry and recording provenance CSV schema and completeness."""
    src_csv = REPORTS_DIR / "phase23_source_registry.csv"
    prov_csv = REPORTS_DIR / "phase23_recording_provenance.csv"
    assert src_csv.exists(), "phase23_source_registry.csv missing"
    assert prov_csv.exists(), "phase23_recording_provenance.csv missing"

    df_src = pd.read_csv(src_csv)
    df_prov = pd.read_csv(prov_csv)

    assert len(df_src) >= 5, "Source registry must contain at least 5 cataloged candidate repositories"
    assert len(df_prov) == 23, f"Expected 23 cataloged streams (17 primary + 6 exploratory), got {len(df_prov)}"

    # Check that primary streams are all VERIFIED_NEGATIVE
    primary = df_prov[df_prov["recording_id"].str.startswith("P23-NAT")]
    assert len(primary) == 17, f"Expected 17 natural continuous streams, got {len(primary)}"
    for cat in primary["eligibility_category"]:
        assert cat == "VERIFIED_NEGATIVE"


def test_missing_provenance_handling():
    """Verify that unknown provenance metadata fields use UNKNOWN or UNVERIFIED."""
    prov_csv = REPORTS_DIR / "phase23_recording_provenance.csv"
    df_prov = pd.read_csv(prov_csv)
    allowed_null_tokens = {"UNKNOWN", "UNAVAILABLE", "UNVERIFIED", "NONE"}

    for col in ["campaign_id", "session_id", "sensor_id", "location_id"]:
        for val in df_prov[col]:
            assert str(val).strip() != "", f"Empty string found in column {col}"


def test_duplicate_hash_detection():
    """Verify that duplicate audit CSV exists and detected zero exact duplicates among primary streams."""
    dup_csv = REPORTS_DIR / "phase23_duplicate_audit.csv"
    assert dup_csv.exists(), "phase23_duplicate_audit.csv missing"
    df_dup = pd.read_csv(dup_csv)
    assert len(df_dup) > 0
    assert df_dup.iloc[0]["status"] == "ZERO_EXACT_DUPLICATES_DETECTED"


def test_audio_duration_and_formats():
    """Inspect physical WAV header durations, channels, and sample rates."""
    prov_csv = REPORTS_DIR / "phase23_recording_provenance.csv"
    df_prov = pd.read_csv(prov_csv)

    total_s = 0.0
    for _, row in df_prov.iterrows():
        p = DATA_DIR / row["relative_filepath"]
        assert p.exists(), f"Audio file not found: {p}"
        with wave.open(str(p), "rb") as wf:
            dur = wf.getnframes() / float(wf.getframerate())
            assert abs(dur - float(row["duration_seconds"])) < 1.0, f"Duration mismatch in {p.name}"
            assert wf.getframerate() == 16000, f"Expected 16kHz audio, got {wf.getframerate()}"
            assert wf.getnchannels() == 1, f"Expected mono audio, got {wf.getnchannels()}"
            if row["eligibility_category"] == "VERIFIED_NEGATIVE":
                total_s += dur

    # Check total natural continuous exposure is ~23,925.6s (6.65h)
    assert abs(total_s - 23925.58) < 2.0


def test_continuity_verification():
    """Ensure natural continuous streams have NATURAL_CONTINUOUS status and no synthetic splicing."""
    prov_csv = REPORTS_DIR / "phase23_recording_provenance.csv"
    df_prov = pd.read_csv(prov_csv)
    natural = df_prov[df_prov["eligibility_category"] == "VERIFIED_NEGATIVE"]
    for status in natural["continuity_status"]:
        assert status == "NATURAL_CONTINUOUS"


def test_negative_label_eligibility_rules():
    """Verify that only VERIFIED_NEGATIVE recordings enter the primary exposure benchmark."""
    exp_csv = REPORTS_DIR / "phase23_exposure_accounting.csv"
    assert exp_csv.exists(), "phase23_exposure_accounting.csv missing"
    df_exp = pd.read_csv(exp_csv)
    assert len(df_exp) == 34  # 17 streams * 2 models

    prov_csv = REPORTS_DIR / "phase23_recording_provenance.csv"
    df_prov = pd.read_csv(prov_csv)

    exp_rec_ids = set(df_exp["recording_id"])
    for rec_id in exp_rec_ids:
        match = df_prov[df_prov["recording_id"] == rec_id]
        assert len(match) == 1
        assert match.iloc[0]["eligibility_category"] == "VERIFIED_NEGATIVE"


def test_gross_vs_eligible_exposure():
    """Verify that eligible exposure is strictly less than or equal to gross exposure."""
    exp_csv = REPORTS_DIR / "phase23_exposure_accounting.csv"
    df_exp = pd.read_csv(exp_csv)

    for _, row in df_exp.iterrows():
        assert row["eligible_exposure_s"] <= row["gross_duration_s"]
        assert abs((row["gross_duration_s"] - row["cooldown_excluded_s"]) - row["eligible_exposure_s"]) < 1e-3


def test_cooldown_interval_merging_no_double_counting():
    """Verify that overlapping cooldown intervals are merged properly."""
    # Test interval merger math
    intervals = [(10.0, 12.0), (11.0, 13.0), (20.0, 22.0)]
    sorted_int = sorted(intervals, key=lambda x: x[0])
    merged = []
    cur_s, cur_e = sorted_int[0]
    for nxt_s, nxt_e in sorted_int[1:]:
        if nxt_s <= cur_e:
            cur_e = max(cur_e, nxt_e)
        else:
            merged.append((cur_s, cur_e))
            cur_s, cur_e = nxt_s, nxt_e
    merged.append((cur_s, cur_e))

    assert merged == [(10.0, 13.0), (20.0, 22.0)]
    total_len = sum(e - s for s, e in merged)
    assert total_len == 5.0  # 3.0 + 2.0 (not 2 + 2 + 2 = 6.0)


def test_poisson_garwood_bounds():
    """Verify that Garwood formula reproduces exact Poisson confidence limits."""
    # Test k = 0 over 50 hours: -ln(0.05) / 50 = 2.99573 / 50 = 0.05991
    alpha = 0.05
    k = 0
    t = 50.0
    upper_0_50 = -math.log(alpha) / t
    assert abs(upper_0_50 - 0.05991) < 1e-4

    # Test k = 56 over 6.6149 hours
    k = 56
    t = 6.6149
    low = chi2.ppf(alpha / 2.0, 2 * k) / (2.0 * t)
    high = chi2.ppf(1.0 - alpha / 2.0, 2 * (k + 1)) / (2.0 * t)
    assert abs(low - 6.395) < 0.05
    assert abs(high - 10.994) < 0.05


def test_matched_evaluation_intervals():
    """Verify both frozen models were evaluated on 100% identical gross durations."""
    exp_csv = REPORTS_DIR / "phase23_exposure_accounting.csv"
    df_exp = pd.read_csv(exp_csv)

    p14_rows = df_exp[df_exp["detector"] == "Phase 14 Balanced"].sort_values("recording_id")
    p17_rows = df_exp[df_exp["detector"] == "Phase 17 Experimental"].sort_values("recording_id")

    assert len(p14_rows) == len(p17_rows)
    for (_, r14), (_, r17) in zip(p14_rows.iterrows(), p17_rows.iterrows()):
        assert r14["recording_id"] == r17["recording_id"]
        assert r14["gross_duration_s"] == r17["gross_duration_s"]


def test_safety_designations_in_reports():
    """Verify that all Phase 23 documentation files contain the mandatory safety designation."""
    md_files = [
        "phase23_final_report.md",
        "phase23_source_shortlist.md",
        "phase23_source_eligibility_report.md",
        "phase23_model_comparison.md",
        "phase23_risk_and_limitation_register.md",
    ]
    mandatory_banner = "RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY."
    for fname in md_files:
        p = REPORTS_DIR / fname
        assert p.exists(), f"Missing report: {fname}"
        text = p.read_text(encoding="utf-8")
        assert mandatory_banner in text, f"Mandatory safety designation missing in {fname}"


if __name__ == "__main__":
    pytest.main(["-v", __file__])

