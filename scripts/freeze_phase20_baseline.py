"""
Phase 20 Baseline Freeze Verification Script
MANDATORY SAFETY DESIGNATION:
RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.

Verifies SHA-256 digests and file sizes of:
- model_phase14.py (Default Production Baseline)
- model_phase17.py (Selectable Experimental Profile)
- model_phase13.py (Historical Comparator)
- model_phase9.py (Historical Comparator)
- gunshot_detection_phase19.zip
- gunshot_detection_phase18.zip
- gunshot_detection_phase17.zip
- gunshot_detection_phase16.zip

Outputs reports/phase20_baseline_freeze.json.
"""

import os
import sys
import json
import hashlib
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path("E:/gunshot/gunshot")
PARENT = ROOT.parent
REPORTS_DIR = ROOT / "reports"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

EXPECTED_DIGESTS = {
    "model_phase14.py": {
        "path": ROOT / "model_phase14.py",
        "expected_sha256": "a268551604ae8b73068435ff10ab3d265065f56e0679757fca5b6bf0f061c065",
        "expected_bytes": 23340,
        "role": "DEFAULT_PRODUCTION_BASELINE"
    },
    "model_phase17.py": {
        "path": ROOT / "model_phase17.py",
        "expected_sha256": "e2b262b866fdd5d7f1a4ab91a7b8b9bac189ee8cc7a78603b3544ca1579fb819",
        "expected_bytes": 29067,
        "role": "SELECTABLE_EXPERIMENTAL_PROFILE"
    },
    "model_phase13.py": {
        "path": ROOT / "model_phase13.py",
        "expected_sha256": "68585039a4a4fdb7978a99f5e2a72c0ad5a9523127ec24a1338fbedd1c1231e6",
        "expected_bytes": 22252,
        "role": "FROZEN_HISTORICAL_COMPARATOR"
    },
    "model_phase9.py": {
        "path": ROOT / "model_phase9.py",
        "expected_sha256": "85cedd9f5b988ecafb1eae7de9630ee3d6a387ded6ef732e0efb7c3b496f132a",
        "expected_bytes": 17719,
        "role": "FROZEN_HISTORICAL_COMPARATOR"
    },
    "gunshot_detection_phase19.zip": {
        "path": PARENT / "gunshot_detection_phase19.zip",
        "expected_sha256": "9d768b9db3126aa23b37dd0f6b00804345929a4171499f703e4bb84132ad9ac4",
        "expected_bytes": 8191423,
        "role": "PHASE_19_ARCHIVE"
    },
    "gunshot_detection_phase18.zip": {
        "path": PARENT / "gunshot_detection_phase18.zip",
        "expected_sha256": "90963ba0e8a70bee9f408473964f10ad0d4a94fcc46173961905761f3ada6b6c",
        "expected_bytes": 2418935811,
        "role": "PHASE_18_ARCHIVE"
    },
    "gunshot_detection_phase17.zip": {
        "path": PARENT / "gunshot_detection_phase17.zip",
        "expected_sha256": "028bb95bced4456020e5d9860cb01ddca3d2944779d31db76ba2b20f99e2bc41",
        "expected_bytes": 2418868636,
        "role": "PHASE_17_ARCHIVE"
    },
    "gunshot_detection_phase16.zip": {
        "path": PARENT / "gunshot_detection_phase16.zip",
        "expected_sha256": "386298c4a4a251b4728d14d5903265ebe18c63404f87d0eba47bbcce442f65b4",
        "expected_bytes": 1997721700,
        "role": "PHASE_16_ARCHIVE"
    }
}

def compute_sha256(filepath):
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

results = {
    "safety_designation": "RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY",
    "phase": "PHASE_20_PITTSBURGH_AUDIT",
    "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
    "status": "FROZEN_UNMODIFIED",
    "default_production_baseline": "Phase 14 Balanced",
    "selectable_experimental_profile": "Phase 17 Experimental",
    "models": {},
    "archives": {}
}

all_passed = True

for name, meta in EXPECTED_DIGESTS.items():
    p = meta["path"]
    is_model = "model_" in name
    category = "models" if is_model else "archives"
    
    if not p.exists():
        results[category][name] = {
            "path": str(p),
            "status": "MISSING"
        }
        all_passed = False
        continue
        
    actual_sha = compute_sha256(p)
    actual_size = p.stat().st_size
    expected_sha = meta["expected_sha256"]
    expected_size = meta["expected_bytes"]
    
    match_sha = (actual_sha == expected_sha)
    match_size = (actual_size == expected_size)
    
    results[category][name] = {
        "path": str(p),
        "sha256": actual_sha,
        "expected_sha256": expected_sha,
        "size_bytes": actual_size,
        "expected_bytes": expected_size,
        "sha256_match": match_sha,
        "size_match": match_size,
        "role": meta["role"],
        "verification": "VERIFIED_MATCH" if (match_sha and match_size) else "DISCREPANCY"
    }
    
    if not (match_sha and match_size):
        all_passed = False
        print(f"DISCREPANCY: {name} sha match={match_sha}, size match={match_size}")
    else:
        print(f"VERIFIED: {name} -> {actual_sha} ({actual_size:,} bytes)")

out_path = REPORTS_DIR / "phase20_baseline_freeze.json"
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print(f"\nBaseline freeze report saved to {out_path}")
if not all_passed:
    sys.exit(1)

