"""
Phase 24 Baseline Freeze & Cryptographic Verification
MANDATORY SAFETY DESIGNATION:
RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.

Verifies SHA-256 hashes of:
- model_phase14.py (Default Research Baseline)
- model_phase17.py (Selectable Experimental Profile)
- model_phase13.py (Historical Comparator)
- model_phase9.py (Historical Comparator)
- gunshot_detection_phase23.zip (Phase 23 Archive)
- gunshot_detection_phase22.zip (Phase 22 Archive)
- gunshot_detection_phase21.zip (Phase 21 Archive)
- gunshot_detection_phase20.zip (Phase 20 Archive)
- reports/phase20_canonical_event_manifest.csv (Canonical Ground Truth)

Outputs reports/phase24_baseline_freeze.json.
"""

import json
import hashlib
from pathlib import Path

ROOT = Path("E:/gunshot/gunshot")
REPORTS_DIR = ROOT / "reports"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

EXPECTED_HASHES = {
    "model_phase14.py": {
        "role": "DEFAULT_RESEARCH_BASELINE",
        "sha256": "a268551604ae8b73068435ff10ab3d265065f56e0679757fca5b6bf0f061c065",
        "size_bytes": 23340
    },
    "model_phase17.py": {
        "role": "SELECTABLE_EXPERIMENTAL_PROFILE",
        "sha256": "e2b262b866fdd5d7f1a4ab91a7b8b9bac189ee8cc7a78603b3544ca1579fb819",
        "size_bytes": 29067
    },
    "model_phase13.py": {
        "role": "FROZEN_HISTORICAL_COMPARATOR",
        "sha256": "68585039a4a4fdb7978a99f5e2a72c0ad5a9523127ec24a1338fbedd1c1231e6",
        "size_bytes": 22252
    },
    "model_phase9.py": {
        "role": "FROZEN_HISTORICAL_COMPARATOR",
        "sha256": "85cedd9f5b988ecafb1eae7de9630ee3d6a387ded6ef732e0efb7c3b496f132a",
        "size_bytes": 17719
    },
    "gunshot_detection_phase23.zip": {
        "role": "FROZEN_HISTORICAL_RELEASE_ARCHIVE_P23",
        "path": "E:/gunshot/gunshot_detection_phase23.zip",
        "sha256": "5ce4e64715829d9b52111b6d6322f251976e1ce99e829d9dfbe0858a7e1644c8",
        "size_bytes": 8194616
    },
    "gunshot_detection_phase22.zip": {
        "role": "FROZEN_HISTORICAL_RELEASE_ARCHIVE_P22",
        "path": "E:/gunshot/gunshot_detection_phase22.zip",
        "sha256": "160d327072c3515e945ca5cdf89038f14b6ef1919b1e4865278affab52ad4de5",
        "size_bytes": 8199741
    },
    "gunshot_detection_phase21.zip": {
        "role": "FROZEN_HISTORICAL_RELEASE_ARCHIVE_P21",
        "path": "E:/gunshot/gunshot_detection_phase21.zip",
        "sha256": "b065747b0e6118d228336bee7f8c3811890b638a25070d3ce2a047c329b3e225",
        "size_bytes": 8211219
    },
    "gunshot_detection_phase20.zip": {
        "role": "FROZEN_HISTORICAL_RELEASE_ARCHIVE_P20",
        "path": "E:/gunshot/gunshot_detection_phase20.zip",
        "sha256": "dda7427f2dbffcb178f6d9ade0abb80fbfc491751f04de5dc0db1b4731c31c89",
        "size_bytes": 8205938
    },
    "phase20_canonical_event_manifest.csv": {
        "role": "CANONICAL_GROUND_TRUTH_MANIFEST",
        "path": "E:/gunshot/gunshot/reports/phase20_canonical_event_manifest.csv",
        "sha256": "6c3e5d5c07cb5102ee7160c0272e90d5c98cdb4659538ee58ad276855d971691",
        "size_bytes": 16427
    }
}


def sha256_file(filepath: Path) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def main():
    print("=" * 80)
    print("PHASE 24 BASELINE FREEZE VERIFICATION")
    print("MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.")
    print("=" * 80)

    results = {
        "safety_designation": "RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY",
        "phase": "PHASE_24_MUNICIPAL_AUDIO_AND_FALSE_ALERT_RATE_AUDIT",
        "verification_timestamp": "2026-11-14T19:40:00Z",
        "models": {},
        "archives": {},
        "canonical_data_verification": {},
        "freeze_status": "PASS"
    }

    all_passed = True

    for name, meta in EXPECTED_HASHES.items():
        if "path" in meta:
            target_path = Path(meta["path"])
        else:
            target_path = ROOT / name

        if not target_path.exists():
            print(f"[FAIL] Missing target file: {target_path}")
            all_passed = False
            continue

        actual_sha = sha256_file(target_path)
        actual_size = target_path.stat().st_size
        expected_sha = meta["sha256"]
        expected_size = meta["size_bytes"]

        status = "VERIFIED" if (actual_sha == expected_sha and actual_size == expected_size) else "MISMATCH"
        if status != "VERIFIED":
            print(f"[FAIL] Checksum mismatch on {name}!")
            print(f"  Expected: {expected_sha} ({expected_size} bytes)")
            print(f"  Actual:   {actual_sha} ({actual_size} bytes)")
            all_passed = False
        else:
            print(f"[OK] {name} verified ({actual_sha[:16]}...)")

        entry = {
            "file": name,
            "path": str(target_path),
            "role": meta["role"],
            "expected_sha256": expected_sha,
            "actual_sha256": actual_sha,
            "expected_size_bytes": expected_size,
            "actual_size_bytes": actual_size,
            "status": status
        }

        if name.startswith("model_"):
            results["models"][name] = entry
        elif name.endswith(".zip"):
            results["archives"][name] = entry
        else:
            results["canonical_data_verification"][name] = entry

    results["freeze_status"] = "PASS" if all_passed else "FAIL"

    out_file = REPORTS_DIR / "phase24_baseline_freeze.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print(f"\nFreeze verification complete. Status: {results['freeze_status']}")
    print(f"Output saved to: {out_file}")

    if not all_passed:
        raise RuntimeError("Phase 24 baseline freeze verification FAILED!")


if __name__ == "__main__":
    main()

