"""
Phase 17 Packaging, Artifact Manifest Generation, and Cryptographic Verification Script.

Packages the verified Phase 17 workspace into gunshot_detection_phase17.zip:
1. Verifies zip readability using testzip() (ensures 0 CRC corruption errors).
2. Computes the archive SHA-256 checksum and size.
3. Cryptographically validates immutability of Phase 16 baseline archive.
4. Generates comprehensive reports/phase17_artifact_manifest.json.

SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.
"""

import os
import sys
import zipfile
import hashlib
import json
import time
from pathlib import Path

ROOT = Path("e:/gunshot/gunshot").resolve()
ZIP_PATH = Path("e:/gunshot/gunshot_detection_phase17.zip").resolve()
SAFETY_DESIGNATION = "RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY"

HISTORICAL_ARCHIVES = [
    ("Phase 16", Path("e:/gunshot/gunshot_detection_phase16.zip"), "386298c4a4a251b4728d14d5903265ebe18c63404f87d0eba47bbcce442f65b4"),
]

def compute_file_sha256(path: Path) -> str:
    hasher = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()

def main():
    print("=" * 80)
    print("   PHASE 17: PACKAGING & CRYPTOGRAPHIC INTEGRITY VERIFICATION")
    print(f"   Safety Designation: {SAFETY_DESIGNATION}")
    print("=" * 80 + "\n")

    # 1. Package workspace
    print(f"[*] Packaging {ROOT} into {ZIP_PATH}...")
    file_count = 0

    with zipfile.ZipFile(ZIP_PATH, "w", compression=zipfile.ZIP_DEFLATED) as z:
        for dirpath, dirnames, filenames in os.walk(ROOT):
            dirnames[:] = [d for d in dirnames if d not in ("__pycache__", ".git", ".pytest_cache")]
            for f in filenames:
                if f.endswith(".pyc") or f.endswith(".tmp") or f.startswith(".phase13_dev_features_cache"):
                    continue
                full_p = Path(dirpath) / f
                rel_p = full_p.relative_to(ROOT)
                z.write(full_p, rel_p)
                file_count += 1

    print(f"[+] Successfully packaged {file_count} files into {ZIP_PATH}.")

    # 2. Verify archive integrity
    print("[*] Verifying archive integrity with testzip()...")
    with zipfile.ZipFile(ZIP_PATH, "r") as z:
        err = z.testzip()
        if err is not None:
            raise RuntimeError(f"Corrupted file found in archive: {err}")
        print("[+] Archive testzip() verification: PASSED (None - zero corruption).")

    # 3. Compute SHA-256
    print("[*] Computing SHA-256 checksum...")
    sha17 = compute_file_sha256(ZIP_PATH)
    size_bytes = ZIP_PATH.stat().st_size
    size_mb = size_bytes / (1024 * 1024)

    print("\n" + "=" * 70)
    print("PHASE 17 DEPLOYMENT ARCHIVE SUMMARY")
    print("=" * 70)
    print(f"Path:       {ZIP_PATH}")
    print(f"Size:       {size_mb:.2f} MB ({size_bytes} bytes)")
    print(f"Files:      {file_count}")
    print(f"SHA-256:    {sha17}")
    print("Integrity:  VERIFIED (testzip passed)")
    print("=" * 70 + "\n")

    # 4. Verify baseline archive
    print("[*] Cryptographically validating baseline Phase 16 archive...")
    for name, p, exp_hash in HISTORICAL_ARCHIVES:
        if not p.exists():
            print(f"[FAIL] Baseline archive missing: {p}")
            continue
        actual_hash = compute_file_sha256(p)
        if actual_hash == exp_hash:
            print(f"[PASS] {name} Archive Verified: {actual_hash}")
        else:
            print(f"[FAIL] {name} Hash Mismatch! Exp: {exp_hash}, Act: {actual_hash}")

    # 5. Generate Artifact Manifest
    manifest_path = ROOT / "reports" / "phase17_artifact_manifest.json"
    print(f"\n[*] Generating Phase 17 Artifact Manifest: {manifest_path}")

    manifest_data = {
        "phase": 17,
        "title": "Continuous Positive Event Detection, Long-Duration Reliability & Animal Suppression Validation",
        "safety_designation": SAFETY_DESIGNATION,
        "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "deployment_archive": {
            "filename": ZIP_PATH.name,
            "path": str(ZIP_PATH),
            "sha256": sha17,
            "size_bytes": size_bytes,
            "size_mb": round(size_mb, 2),
            "file_count": file_count,
            "testzip_integrity": "PASSED_ZERO_CORRUPTION"
        },
        "frozen_models": {
            "model_phase14.py": {
                "sha256": compute_file_sha256(ROOT / "model_phase14.py"),
                "status": "FROZEN_BASELINE_UNTOUCHED"
            },
            "model_phase13.py": {
                "sha256": compute_file_sha256(ROOT / "model_phase13.py"),
                "status": "FROZEN_HISTORICAL_COMPARATOR"
            },
            "model_phase9.py": {
                "sha256": compute_file_sha256(ROOT / "model_phase9.py"),
                "status": "FROZEN_HISTORICAL_COMPARATOR"
            },
            "model_phase17.py": {
                "sha256": compute_file_sha256(ROOT / "model_phase17.py"),
                "status": "EXPERIMENTAL_ANIMAL_SUPPRESSION_CANDIDATE"
            }
        },
        "key_reports": [
            "reports/phase17_positive_continuous_provenance.md",
            "reports/phase17_annotation_audit.md",
            "reports/phase17_long_duration_negative_evaluation.md",
            "reports/phase17_animal_suppression_experiment.md",
            "reports/phase17_high_precision_zero_alert_audit.md",
            "reports/phase17_continuous_event_results.md",
            "reports/phase17_latency_audit.md",
            "reports/phase17_statistical_analysis.md",
            "reports/phase17_final_report.md"
        ],
        "key_datasets": {
            "continuous_positive": "data/phase17_continuous_positive/ (4 evaluation streams, 39 physical events)",
            "continuous_negative": "data/phase17_natural_continuous/ (6 new urban streams + 11 Phase 16 baseline streams, 6.65 hours total)"
        },
        "regression_suites": [
            "tests/test_phase17_provenance_integrity.py",
            "tests/test_phase17_evaluation_integrity.py",
            "tests/test_phase17_regression.py"
        ]
    }

    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest_data, f, indent=2)

    print(f"[+] Saved Artifact Manifest: {manifest_path}")

if __name__ == "__main__":
    main()

