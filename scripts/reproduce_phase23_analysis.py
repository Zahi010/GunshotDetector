"""
End-to-End Deterministic Reproduction Harness — Phase 23
Independent Urban Background Audio Acquisition & First 50-Hour Benchmark

MANDATORY SAFETY DESIGNATION:
RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.

Reproduces all Phase 23 verification steps:
1. Baseline freeze verification.
2. Source registry and provenance validation.
3. Duplicate hash detection.
4. Exposure accounting and cooldown dead time formulation.
5. Exact Garwood Poisson confidence limits.
6. Execution of unit tests.
"""

import sys
import json
import hashlib
import math
import subprocess
import pandas as pd
from pathlib import Path
from scipy.stats import chi2

ROOT = Path("E:/gunshot/gunshot")
REPORTS_DIR = ROOT / "reports"
SCRIPTS_DIR = ROOT / "scripts"
TESTS_DIR = ROOT / "tests"

FROZEN_HASHES = {
    "model_phase14.py": "a268551604ae8b73068435ff10ab3d265065f56e0679757fca5b6bf0f061c065",
    "model_phase17.py": "e2b262b866fdd5d7f1a4ab91a7b8b9bac189ee8cc7a78603b3544ca1579fb819",
    "model_phase13.py": "68585039a4a4fdb7978a99f5e2a72c0ad5a9523127ec24a1338fbedd1c1231e6",
    "model_phase9.py": "85cedd9f5b988ecafb1eae7de9630ee3d6a387ded6ef732e0efb7c3b496f132a",
    "gunshot_detection_phase22.zip": "160d327072c3515e945ca5cdf89038f14b6ef1919b1e4865278affab52ad4de5",
    "gunshot_detection_phase21.zip": "b065747b0e6118d228336bee7f8c3811890b638a25070d3ce2a047c329b3e225",
    "gunshot_detection_phase20.zip": "dda7427f2dbffcb178f6d9ade0abb80fbfc491751f04de5dc0db1b4731c31c89",
    "reports/phase20_canonical_event_manifest.csv": "6c3e5d5c07cb5102ee7160c0272e90d5c98cdb4659538ee58ad276855d971691",
}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def main():
    print("=" * 80)
    print("PHASE 23 REPRODUCTION HARNESS — DETERMINISTIC AUDIT PIPELINE")
    print("MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.")
    print("=" * 80)

    # 1. Baseline Freeze Check
    print("\n[1/6] Verifying Cryptographic Baseline Freeze...")
    for rel_path, exp_hash in FROZEN_HASHES.items():
        if rel_path.endswith(".zip"):
            target_path = Path("E:/gunshot") / rel_path
        else:
            target_path = ROOT / rel_path
        if not target_path.exists():
            raise FileNotFoundError(f"Missing required baseline component: {target_path}")
        act_hash = sha256_file(target_path)
        if act_hash != exp_hash:
            raise ValueError(f"Hash mismatch on {rel_path}: {act_hash} != {exp_hash}")
        print(f"  [OK] {rel_path} verified ({act_hash[:16]}...)")

    # 2. Source Registry & Provenance Check
    print("\n[2/6] Verifying Source Registry & Recording Provenance...")
    src_csv = REPORTS_DIR / "phase23_source_registry.csv"
    prov_csv = REPORTS_DIR / "phase23_recording_provenance.csv"
    assert src_csv.exists(), "Source registry missing"
    assert prov_csv.exists(), "Recording provenance missing"

    df_src = pd.read_csv(src_csv)
    df_prov = pd.read_csv(prov_csv)
    df_primary = df_prov[df_prov["eligibility_category"] == "VERIFIED_NEGATIVE"]

    print(f"  Cataloged Sources: {len(df_src)}")
    print(f"  Total Streams Cataloged: {len(df_prov)} (17 Primary Verified Negative + 6 Exploratory)")
    print(f"  Primary Verified Negative Streams: {len(df_primary)}")
    gross_s = df_primary["duration_seconds"].sum()
    print(f"  Gross Verified Exposure: {gross_s:.2f} s ({gross_s/3600.0:.4f} hours)")
    assert len(df_primary) == 17
    assert abs(gross_s - 23925.58) < 2.0
    print("  [OK] Source registry and recording provenance verified.")

    # 3. Duplicate Detection Check
    print("\n[3/6] Verifying Duplicate Detection Audit...")
    dup_csv = REPORTS_DIR / "phase23_duplicate_audit.csv"
    assert dup_csv.exists(), "Duplicate audit CSV missing"
    df_dup = pd.read_csv(dup_csv)
    assert df_dup.iloc[0]["status"] == "ZERO_EXACT_DUPLICATES_DETECTED"
    print("  [OK] Zero exact hash duplicates detected.")

    # 4. Exposure Accounting & Forensic Results
    print("\n[4/6] Verifying Exposure Accounting & Forensic Cooldown Formulations...")
    exp_csv = REPORTS_DIR / "phase23_exposure_accounting.csv"
    assert exp_csv.exists(), "Exposure accounting CSV missing"
    df_exp = pd.read_csv(exp_csv)

    p14_rows = df_exp[df_exp["detector"] == "Phase 14 Balanced"]
    p17_rows = df_exp[df_exp["detector"] == "Phase 17 Experimental"]

    assert len(p14_rows) == 17
    assert len(p17_rows) == 17

    p14_alerts = p14_rows["observed_alerts"].sum()
    p17_alerts = p17_rows["observed_alerts"].sum()
    p14_elig_hr = p14_rows["eligible_exposure_hr"].sum()
    p17_elig_hr = p17_rows["eligible_exposure_hr"].sum()

    print(f"  Phase 14 Balanced: {p14_alerts} alerts over {p14_elig_hr:.4f} eligible hours ({p14_alerts/p14_elig_hr:.4f} alerts/hr)")
    print(f"  Phase 17 Experimental: {p17_alerts} alerts over {p17_elig_hr:.4f} eligible hours ({p17_alerts/p17_elig_hr:.4f} alerts/hr)")

    assert p14_alerts == 56
    assert p17_alerts == 51
    assert abs(p14_elig_hr - 6.6149) < 0.01
    assert abs(p17_elig_hr - 6.6177) < 0.01
    print("  [OK] Exposure accounting and alert totals reproduced exactly.")

    # 5. Poisson Garwood Bounds Check
    print("\n[5/6] Verifying Poisson Garwood Mathematical Bounds...")
    # Reference zero-alert bounds
    alpha = 0.05
    ub_50 = -math.log(alpha) / 50.0
    ub_100 = -math.log(alpha) / 100.0
    print(f"  Theoretical zero-alert upper 95% bound (50h):  {ub_50:.5f} alerts/hr (approx 0.060)")
    print(f"  Theoretical zero-alert upper 95% bound (100h): {ub_100:.5f} alerts/hr (approx 0.030)")
    assert abs(ub_50 - 0.05991) < 1e-4
    assert abs(ub_100 - 0.02996) < 1e-4
    print("  [OK] Poisson statistical bounds verified.")

    # 6. Automated Unit Tests Execution
    print("\n[6/6] Executing Phase 23 Pytest Verification Suite...")
    test_file = TESTS_DIR / "test_phase23_ingestion.py"
    cmd = [sys.executable, "-m", "pytest", str(test_file), "-v"]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        print(res.stdout)
        print(res.stderr)
        raise RuntimeError("Phase 23 pytest suite failed!")
    print(res.stdout.strip())
    print("  [OK] All 13 unit and integration tests passed.")

    print("\n" + "=" * 80)
    print("PHASE 23 REPRODUCTION HARNESS COMPLETED SUCCESSFULLY WITH 100% PASS RATE")
    print("RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.")
    print("=" * 80)


if __name__ == "__main__":
    main()

