"""
Phase 18 Packaging, Artifact Manifest Generation, and Cryptographic Verification Script.

Packages the verified Phase 18 workspace into gunshot_detection_phase18.zip:
1. Verifies zip readability using testzip() (ensures 0 CRC corruption errors).
2. Computes the archive SHA-256 checksum and size.
3. Cryptographically validates immutability of Phase 16 and Phase 17 baseline archives.
4. Generates comprehensive reports/phase18_artifact_manifest.json.

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
ZIP_PATH = Path("e:/gunshot/gunshot_detection_phase18.zip").resolve()
SAFETY_DESIGNATION = "RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY"

HISTORICAL_ARCHIVES = [
    ("Phase 16", Path("e:/gunshot/gunshot_detection_phase16.zip"), "386298c4a4a251b4728d14d5903265ebe18c63404f87d0eba47bbcce442f65b4"),
    ("Phase 17", Path("e:/gunshot/gunshot_detection_phase17.zip"), "028bb95bced4456020e5d9860cb01ddca3d2944779d31db76ba2b20f99e2bc41")
]

def compute_file_sha256(path: Path) -> str:
    hasher = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()

def main():
    print("=" * 80)
    print("   PHASE 18: PACKAGING & CRYPTOGRAPHIC INTEGRITY VERIFICATION")
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
    sha18 = compute_file_sha256(ZIP_PATH)
    size_bytes = ZIP_PATH.stat().st_size
    size_mb = size_bytes / (1024 * 1024)

    print("\n" + "=" * 70)
    print("PHASE 18 DEPLOYMENT ARCHIVE SUMMARY")
    print("=" * 70)
    print(f"Path:       {ZIP_PATH}")
    print(f"Size:       {size_mb:.2f} MB ({size_bytes} bytes)")
    print(f"Files:      {file_count}")
    print(f"SHA-256:    {sha18}")
    print("Integrity:  VERIFIED (testzip passed)")
    print("=" * 70 + "\n")

    # 4. Verify baseline archives
    print("[*] Cryptographically validating baseline Phase 16 and Phase 17 archives...")
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
    manifest_path = ROOT / "reports" / "phase18_artifact_manifest.json"
    print(f"\n[*] Generating Phase 18 Artifact Manifest: {manifest_path}")

    manifest_data = {
        "phase": 18,
        "title": "Independent Validation Audit, Data Lineage Reconciliation & Reproducibility",
        "safety_designation": SAFETY_DESIGNATION,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
        "archive": {
            "filename": ZIP_PATH.name,
            "path": str(ZIP_PATH),
            "sha256": sha18,
            "size_bytes": size_bytes,
            "size_mb": round(size_mb, 2),
            "total_files": file_count,
            "testzip_integrity": "PASSED"
        },
        "baseline_detectors": {
            "model_phase14.py": {
                "sha256": "a268551604ae8b73068435ff10ab3d265065f56e0679757fca5b6bf0f061c065",
                "role": "DEFAULT_PRODUCTION_BASELINE"
            },
            "model_phase17.py": {
                "sha256": "e2b262b866fdd5d7f1a4ab91a7b8b9bac189ee8cc7a78603b3544ca1579fb819",
                "role": "SELECTABLE_EXPERIMENTAL_DETECTOR"
            },
            "model_phase13.py": {
                "sha256": "68585039a4a4fdb7978a99f5e2a72c0ad5a9523127ec24a1338fbedd1c1231e6",
                "role": "FROZEN_HISTORICAL_COMPARATOR"
            },
            "model_phase9.py": {
                "sha256": "85cedd9f5b988ecafb1eae7de9630ee3d6a387ded6ef732e0efb7c3b496f132a",
                "role": "FROZEN_HISTORICAL_COMPARATOR"
            }
        },
        "audit_deliverables": {
            "canonical_event_table": "reports/phase18_canonical_event_table.csv",
            "canonical_event_summary": "reports/phase18_canonical_event_summary.json",
            "animal_suppression_lineage": "reports/phase18_animal_suppression_lineage.csv",
            "animal_suppression_report": "reports/phase18_animal_suppression_provenance.md",
            "global_lineage_matrix": "reports/phase18_global_lineage_matrix.csv",
            "leakage_findings": "reports/phase18_leakage_findings.json",
            "independence_audit_report": "reports/phase18_evaluation_independence_audit.md",
            "reproduction_results": "reports/phase18_reproduction_results.json",
            "metric_consistency": "reports/phase18_metric_consistency.json",
            "reproducibility_report": "reports/phase18_reproducibility_report.md",
            "latency_microbenchmark": "reports/phase18_latency_microbenchmark.json",
            "latency_audit_report": "reports/phase18_latency_audit.md",
            "test_suite": "tests/test_phase18_audit_and_integrity.py",
            "test_results": "reports/phase18_test_results.txt",
            "master_final_report": "reports/phase18_final_report.md"
        },
        "key_reconciled_metrics": {
            "total_canonical_events": 39,
            "phase14_balanced_detections": 23,
            "phase14_balanced_recall_pct": 58.97,
            "duplicate_alerts_count": 0,
            "continuous_negative_exposure_hours": 6.65,
            "phase14_balanced_negative_alerts": 56,
            "phase14_balanced_alert_rate_per_hr": 8.43,
            "phase14_high_precision_alert_rate_per_hr": 3.31,
            "phase17_experimental_alert_rate_per_hr": 7.67,
            "median_single_window_latency_ms": 434.62,
            "median_two_window_confirmed_latency_ms": 914.62
        }
    }

    with open(manifest_path, "w") as f:
        json.dump(manifest_data, f, indent=2)

    print(f"[+] Artifact manifest successfully written to {manifest_path}.")
    print("\n[✓] Phase 18 packaging and verification complete.")

if __name__ == "__main__":
    main()

