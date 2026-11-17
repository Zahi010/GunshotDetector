"""
Phase 25 Baseline Freeze & Release Archive Integrity Verification
MANDATORY SAFETY DESIGNATION:
RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.

Cryptographically verifies:
1. Frozen detection baselines:
   - Phase 14 Balanced (DEFAULT_RESEARCH_BASELINE)
   - Phase 17 Experimental (SELECTABLE_EXPERIMENTAL_PROFILE)
   - Phase 13 Balanced (HISTORICAL_COMPARATOR)
   - Phase 9 Balanced (HISTORICAL_COMPARATOR)
2. Release archives:
   - gunshot_detection_phase24.zip
   - gunshot_detection_phase23.zip
   - gunshot_detection_phase22.zip
   - gunshot_detection_phase21.zip
   - gunshot_detection_phase20.zip
Outputs: reports/phase25_baseline_freeze.json
"""

import sys
import json
import hashlib
from pathlib import Path

ROOT = Path("E:/gunshot/gunshot")
PARENT_DIR = Path("E:/gunshot")
REPORTS_DIR = ROOT / "reports"

FROZEN_MODELS = {
    "model_phase14.py": {
        "expected_sha256": "a268551604ae8b73068435ff10ab3d265065f56e0679757fca5b6bf0f061c065",
        "role": "DEFAULT_RESEARCH_BASELINE",
        "description": "Frozen default research baseline detector"
    },
    "model_phase17.py": {
        "expected_sha256": "e2b262b866fdd5d7f1a4ab91a7b8b9bac189ee8cc7a78603b3544ca1579fb819",
        "role": "SELECTABLE_EXPERIMENTAL_PROFILE",
        "description": "Selectable experimental profile with secondary animal suppression filters"
    },
    "model_phase13.py": {
        "expected_sha256": "68585039a4a4fdb7978a99f5e2a72c0ad5a9523127ec24a1338fbedd1c1231e6",
        "role": "HISTORICAL_COMPARATOR",
        "description": "Historical comparator from Phase 13"
    },
    "model_phase9.py": {
        "expected_sha256": "85cedd9f5b988ecafb1eae7de9630ee3d6a387ded6ef732e0efb7c3b496f132a",
        "role": "HISTORICAL_COMPARATOR",
        "description": "Historical comparator from Phase 9"
    }
}

RELEASE_ARCHIVES = {
    "gunshot_detection_phase24.zip": "3e732e0716160f2d77b71ceff3e01a49f3d933e397bf29bf222fec771a8832b8",
    "gunshot_detection_phase23.zip": "5ce4e64715829d9b52111b6d6322f251976e1ce99e829d9dfbe0858a7e1644c8",
    "gunshot_detection_phase22.zip": "160d327072c3515e945ca5cdf89038f14b6ef1919b1e4865278affab52ad4de5",
    "gunshot_detection_phase21.zip": "b065747b0e6118d228336bee7f8c3811890b638a25070d3ce2a047c329b3e225",
    "gunshot_detection_phase20.zip": "dda7427f2dbffcb178f6d9ade0abb80fbfc491751f04de5dc0db1b4731c31c89",
}


def sha256_of_file(filepath: Path) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def main():
    print("=" * 80)
    print("PHASE 25 BASELINE FREEZE & ARCHIVE INTEGRITY AUDIT")
    print("MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.")
    print("=" * 80)

    results = {
        "safety_designation": "RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY",
        "phase": "PHASE_25_CROSS_PHASE_EVIDENCE_RECONCILIATION_AND_INDEPENDENT_ACQUISITION",
        "frozen_models": {},
        "release_archives": {},
        "status": "ALL_HASHES_VERIFIED"
    }

    # Verify models
    print("\n[1/2] Verifying Frozen Baseline Detectors...")
    for filename, meta in FROZEN_MODELS.items():
        p = ROOT / filename
        if not p.exists():
            print(f"ERROR: Missing model file {p}")
            sys.exit(1)
        actual_hash = sha256_of_file(p)
        size_bytes = p.stat().st_size
        assert actual_hash == meta["expected_sha256"], f"Hash mismatch on {filename}!"
        print(f"  [OK] {filename} ({meta['role']}): {actual_hash[:16]}... ({size_bytes} bytes)")
        results["frozen_models"][filename] = {
            "role": meta["role"],
            "sha256": actual_hash,
            "size_bytes": size_bytes,
            "verification": "MATCH_CONFIRMED"
        }

    # Verify archives
    print("\n[2/2] Verifying Release Archives...")
    for filename, expected_hash in RELEASE_ARCHIVES.items():
        p = PARENT_DIR / filename
        if not p.exists():
            print(f"ERROR: Missing archive file {p}")
            sys.exit(1)
        actual_hash = sha256_of_file(p)
        size_bytes = p.stat().st_size
        assert actual_hash == expected_hash, f"Hash mismatch on {filename}!"
        print(f"  [OK] {filename}: {actual_hash[:16]}... ({size_bytes:,} bytes)")
        results["release_archives"][filename] = {
            "sha256": actual_hash,
            "size_bytes": size_bytes,
            "verification": "MATCH_CONFIRMED"
        }

    out_file = REPORTS_DIR / "phase25_baseline_freeze.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved baseline freeze verification to: {out_file}")


if __name__ == "__main__":
    main()

