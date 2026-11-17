"""
Phase 19: Baseline Freeze and Cryptographic Integrity Verification.

Records SHA-256 digests and configurations for:
- Phase 14 Balanced (Default Production Baseline)
- Phase 17 Experimental (Selectable Experimental Profile)
- Phase 13 Balanced (Frozen Historical Comparator)
- Phase 9 Balanced (Frozen Historical Comparator)
- Historical Archives: Phase 16, Phase 17, Phase 18

SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.
"""

import os
import sys
import hashlib
import json
import time
from pathlib import Path

WORKSPACE_ROOT = Path("e:/gunshot/gunshot").resolve()
REPORTS_DIR = WORKSPACE_ROOT / "reports"

SAFETY_DESIGNATION = "RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY"

def sha256_file(filepath: Path) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

def run_freeze():
    print("=" * 80)
    print("   PHASE 19: BASELINE MODEL & ARCHIVE CRYPTOGRAPHIC FREEZE")
    print(f"   Safety: {SAFETY_DESIGNATION}")
    print("=" * 80 + "\n")

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    models = [
        ("Phase 14 Balanced (Production Baseline)", WORKSPACE_ROOT / "model_phase14.py", "a268551604ae8b73068435ff10ab3d265065f56e0679757fca5b6bf0f061c065", "DEFAULT_PRODUCTION_BASELINE"),
        ("Phase 17 Experimental (Animal Suppression)", WORKSPACE_ROOT / "model_phase17.py", "e2b262b866fdd5d7f1a4ab91a7b8b9bac189ee8cc7a78603b3544ca1579fb819", "SELECTABLE_EXPERIMENTAL_PROFILE"),
        ("Phase 13 Balanced (Historical Candidate)", WORKSPACE_ROOT / "model_phase13.py", "68585039a4a4fdb7978a99f5e2a72c0ad5a9523127ec24a1338fbedd1c1231e6", "FROZEN_HISTORICAL_COMPARATOR"),
        ("Phase 9 Balanced (Historical Baseline)", WORKSPACE_ROOT / "model_phase9.py", "85cedd9f5b988ecafb1eae7de9630ee3d6a387ded6ef732e0efb7c3b496f132a", "FROZEN_HISTORICAL_COMPARATOR")
    ]

    archives = [
        ("Phase 18 Archive", Path("e:/gunshot/gunshot_detection_phase18.zip"), "90963ba0e8a70bee9f408473964f10ad0d4a94fcc46173961905761f3ada6b6c"),
        ("Phase 17 Archive", Path("e:/gunshot/gunshot_detection_phase17.zip"), "028bb95bced4456020e5d9860cb01ddca3d2944779d31db76ba2b20f99e2bc41"),
        ("Phase 16 Archive", Path("e:/gunshot/gunshot_detection_phase16.zip"), "386298c4a4a251b4728d14d5903265ebe18c63404f87d0eba47bbcce442f65b4")
    ]

    freeze_record = {
        "safety_designation": SAFETY_DESIGNATION,
        "phase": "PHASE_19_SOURCE_INDEPENDENT_EVALUATION",
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
        "status": "FROZEN_UNMODIFIED",
        "default_production_model": "Phase 14 Balanced",
        "selectable_experimental_model": "Phase 17 Experimental",
        "models": {},
        "historical_archives": {}
    }

    for name, fpath, exp_sha, role in models:
        if not fpath.exists():
            raise FileNotFoundError(f"Missing model: {fpath}")
        act_sha = sha256_file(fpath)
        sz = fpath.stat().st_size
        assert act_sha == exp_sha, f"SHA mismatch for {name}: expected {exp_sha}, got {act_sha}"
        print(f"[PASS] {name}: {act_sha} ({sz} bytes) - Role: {role}")
        freeze_record["models"][name] = {
            "path": str(fpath),
            "sha256": act_sha,
            "size_bytes": sz,
            "role": role,
            "verification": "VERIFIED_MATCH"
        }

    for name, apath, exp_sha in archives:
        if not apath.exists():
            print(f"[WARN] Archive missing: {apath}")
            continue
        act_sha = sha256_file(apath)
        sz = apath.stat().st_size
        assert act_sha == exp_sha, f"SHA mismatch for {name}: expected {exp_sha}, got {act_sha}"
        print(f"[PASS] {name}: {act_sha} ({sz} bytes)")
        freeze_record["historical_archives"][name] = {
            "path": str(apath),
            "sha256": act_sha,
            "size_bytes": sz,
            "verification": "VERIFIED_MATCH"
        }

    out_json = REPORTS_DIR / "phase19_baseline_freeze.json"
    with open(out_json, "w") as f:
        json.dump(freeze_record, f, indent=2)
    print(f"\n[✓] Baseline freeze successfully written to {out_json}")

if __name__ == "__main__":
    run_freeze()

