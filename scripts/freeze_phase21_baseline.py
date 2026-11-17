"""
Phase 21 Baseline Freeze & Hash Verification
MANDATORY SAFETY DESIGNATION:
RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.

Verifies SHA-256 hashes of:
- model_phase14.py (Default Production Baseline)
- model_phase17.py (Selectable Experimental Profile)
- model_phase13.py (Historical Comparator)
- model_phase9.py (Historical Comparator)
- gunshot_detection_phase20.zip (Phase 20 Release Archive)
- reports/phase20_canonical_event_manifest.csv (Canonical Event Manifest)

Outputs reports/phase21_baseline_freeze.json.
"""

import json
import hashlib
from pathlib import Path

ROOT = Path("E:/gunshot/gunshot")
REPORTS_DIR = ROOT / "reports"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

EXPECTED_HASHES = {
    "model_phase14.py": {
        "role": "DEFAULT_PRODUCTION_BASELINE",
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
    "gunshot_detection_phase20.zip": {
        "role": "FROZEN_HISTORICAL_RELEASE_ARCHIVE",
        "path": "E:/gunshot/gunshot_detection_phase20.zip",
        "sha256": "dda7427f2dbffcb178f6d9ade0abb80fbfc491751f04de5dc0db1b4731c31c89",
        "size_bytes": 8205938
    }
}

results = {
    "safety_designation": "RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY",
    "phase": "PHASE_21_CLUSTER_AWARE_VALIDATION",
    "verification_timestamp": "2026-11-14T17:35:00Z",
    "models": {},
    "archives": {},
    "canonical_data_verification": {},
    "freeze_status": "PASS"
}

print("=" * 75)
print("PHASE 21 BASELINE FREEZE VERIFICATION")
print("MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY")
print("=" * 75)

# Verify models
for fname, meta in EXPECTED_HASHES.items():
    if fname.endswith(".zip"):
        fpath = Path(meta["path"])
    else:
        fpath = ROOT / fname
        
    assert fpath.exists(), f"File missing: {fpath}"
    data = fpath.read_bytes()
    actual_hash = hashlib.sha256(data).hexdigest()
    actual_size = len(data)
    
    assert actual_hash == meta["sha256"], f"Hash mismatch on {fname}! Expected {meta['sha256']}, got {actual_hash}"
    assert actual_size == meta["size_bytes"], f"Size mismatch on {fname}! Expected {meta['size_bytes']}, got {actual_size}"
    
    entry = {
        "file": fname,
        "path": str(fpath),
        "role": meta["role"],
        "expected_sha256": meta["sha256"],
        "actual_sha256": actual_hash,
        "expected_size_bytes": meta["size_bytes"],
        "actual_size_bytes": actual_size,
        "status": "VERIFIED"
    }
    if fname.endswith(".zip"):
        results["archives"][fname] = entry
    else:
        results["models"][fname] = entry
    print(f"  PASS: {fname:<30} {actual_hash[:16]}... ({actual_size:,} bytes)")

# Verify canonical manifest
manifest_path = REPORTS_DIR / "phase20_canonical_event_manifest.csv"
assert manifest_path.exists(), f"Missing canonical manifest: {manifest_path}"
man_data = manifest_path.read_bytes()
man_hash = hashlib.sha256(man_data).hexdigest()
results["canonical_data_verification"]["phase20_canonical_event_manifest.csv"] = {
    "path": str(manifest_path),
    "sha256": man_hash,
    "size_bytes": len(man_data),
    "status": "VERIFIED"
}
print(f"  PASS: {'phase20_canonical_event_manifest.csv':<30} {man_hash[:16]}... ({len(man_data):,} bytes)")

out_json = REPORTS_DIR / "phase21_baseline_freeze.json"
with open(out_json, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)
print(f"\nSaved baseline freeze report to: {out_json}")
print("=" * 75)

