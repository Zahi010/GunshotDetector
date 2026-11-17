"""
Phase 16 Packaging and Cryptographic Integrity Verification Script.

Packages the verified Phase 16 workspace into gunshot_detection_phase16.zip:
1. Verifies zip readability using testzip() (ensures 0 CRC corruption errors).
2. Computes the archive SHA-256 checksum and size.
3. Cryptographically validates immutability of all historical archives (Phases 8-15).
4. Generates comprehensive reports/phase16_artifact_manifest.json.

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
ZIP_PATH = Path("e:/gunshot/gunshot_detection_phase16.zip").resolve()
SAFETY_DESIGNATION = "RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY"

PRIOR_ARCHIVES = [
    ("Phase 8", Path("e:/gunshot/gunshot_detection_phase8.zip"), "c8bd26d09b5a41903ae8308b7bcac42f37ecd00d95eb6abfa4295365e074d353"),
    ("Phase 9", Path("e:/gunshot/gunshot_detection_phase9.zip"), "96ff780eaa38737ea66851195301beebc576a31a48319f3b0a71083c4dee2ff0"),
    ("Phase 10", Path("e:/gunshot/gunshot_detection_phase10.zip"), "d8edb26b71d69d6e76a1834cc741bda272c71b475287d7bd7fe2f33be95c459d"),
    ("Phase 11", Path("e:/gunshot/gunshot_detection_phase11.zip"), "c50a9b07ffe93f01118fbc2a26130fd73c800d717b6a372d2e76291c735404ef"),
    ("Phase 12", Path("e:/gunshot/gunshot_detection_phase12.zip"), "8c674902761d469760928c81596813a08a942262440d977a423e58007055241a"),
    ("Phase 13", Path("e:/gunshot/gunshot_detection_phase13.zip"), "1a87aef803c7b2ec1bc0e5b3a894451960ea17a9f787a8ffc81ba7a15e8f6561"),
    ("Phase 14", Path("e:/gunshot/gunshot_detection_phase14.zip"), "37807435378d313efbec89a3671b714cb33f8b1ddef4ca91141956ae5082d144"),
    ("Phase 15", Path("e:/gunshot/gunshot_detection_phase15.zip"), "9ae819de02b9520aa105ecad8db871aa583cc204778bca20e7b9d1018ea6b08c")
]

def compute_file_sha256(path: Path) -> str:
    hasher = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()

def main():
    print("================================================================================")
    print("   PHASE 16: PACKAGING & CRYPTOGRAPHIC INTEGRITY VERIFICATION                  ")
    print("   Safety Designation: RESEARCH DEMONSTRATION PROTOTYPE - NOT FOR LIFE SAFETY   ")
    print("================================================================================\n")

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
    sha16 = compute_file_sha256(ZIP_PATH)
    size_bytes = ZIP_PATH.stat().st_size
    size_mb = size_bytes / (1024 * 1024)

    print("\n" + "=" * 70)
    print("PHASE 16 DEPLOYMENT ARCHIVE SUMMARY")
    print("=" * 70)
    print(f"Path:       {ZIP_PATH}")
    print(f"Size:       {size_mb:.2f} MB ({size_bytes} bytes)")
    print(f"Files:      {file_count}")
    print(f"SHA-256:    {sha16}")
    print("Integrity:  VERIFIED (testzip passed)")
    print("=" * 70 + "\n")

    # 4. Verify all prior historical archives
    print("[*] Cryptographically validating historical archives (Phases 8-15)...")
    prior_status = {}
    all_prior_intact = True
    for name, p, exp_hash in PRIOR_ARCHIVES:
        if not p.exists():
            print(f"[FAIL] Prior archive missing: {p}")
            all_prior_intact = False
            prior_status[name] = {"status": "MISSING", "path": str(p)}
            continue
        actual_hash = compute_file_sha256(p)
        if actual_hash != exp_hash:
            print(f"[FAIL] Hash mismatch for {name}: {actual_hash} != {exp_hash}")
            all_prior_intact = False
            prior_status[name] = {"status": "HASH_MISMATCH", "expected": exp_hash, "actual": actual_hash}
        else:
            print(f"    [OK] {name}: {actual_hash[:16]}... (verified)")
            prior_status[name] = {"status": "VERIFIED_INTACT", "sha256": actual_hash, "path": str(p)}

    if not all_prior_intact:
        raise RuntimeError("Historical archive immutability violation detected!")

    print("[+] All historical archives verified intact.\n")

    # 5. Build Comprehensive Artifact Manifest
    manifest_path = ROOT / "reports" / "phase16_artifact_manifest.json"
    manifest_records = []

    key_files = [
        # Frozen models
        ("model_phase14.py", "PRIMARY_DETECTOR", "Phase 14 frozen detector implementation"),
        ("model_phase13.py", "BASELINE_COMPARATOR", "Phase 13 frozen detector implementation"),
        ("model_phase9.py", "BASELINE_COMPARATOR", "Phase 9 frozen detector implementation"),
        # Server
        ("app.py", "REALTIME_SERVER", "Flask real-time inference server and streaming endpoints"),
        # Key scripts
        ("scripts/freeze_phase16_baseline.py", "AUDIT_TOOL", "Historical archive and baseline freeze script"),
        ("scripts/run_phase16_source_audit.py", "AUDIT_TOOL", "Positive gunshot source lineage and overlap audit"),
        ("scripts/acquire_phase16_continuous_dataset.py", "ACQUISITION_PIPELINE", "Natural continuous audio acquisition & resampler"),
        ("scripts/run_phase16_animal_and_boundary_forensics.py", "DIAGNOSTIC_TOOL", "Animal vocalization and boundary artifact forensic analyzer"),
        ("scripts/run_phase16_continuous_evaluation.py", "EVALUATION_PIPELINE", "Continuous multi-detector streaming evaluation pipeline"),
        ("scripts/run_phase16_latency_audit.py", "BENCHMARK_TOOL", "Full-stack browser-to-server latency microbenchmark"),
        ("scripts/run_phase16_statistical_analysis.py", "STATISTICAL_TOOL", "Poisson uncertainty and paired bootstrap analyzer"),
        ("scripts/package_phase16_archive.py", "PACKAGING_TOOL", "Workspace packager and archive verifier"),
        # Tests
        ("tests/test_phase16_provenance_integrity.py", "UNIT_TEST", "Cryptographic provenance and baseline freeze test suite"),
        ("tests/test_phase16_evaluation_integrity.py", "UNIT_TEST", "Continuous audio and diagnostic report integrity test suite"),
        # Reports
        ("reports/phase16_baseline_freeze.json", "AUDIT_REPORT", "Cryptographic freeze digests of baselines and historical archives"),
        ("reports/phase16_positive_source_lineage.md", "AUDIT_REPORT", "Ballistic gunshot provenance and recording session disclosure"),
        ("reports/phase16_positive_source_overlap.csv", "DATA_MANIFEST", "Granular provenance classification for 47 positive gunshots"),
        ("reports/phase16_recording_session_audit.json", "AUDIT_REPORT", "Formal recording-session linkage and overlap counts"),
        ("reports/phase16_blind_source_audit.md", "AUDIT_REPORT", "Phase 15 discrete blind set post-evaluation audit & retirement"),
        ("reports/phase16_continuous_source_manifest.csv", "DATA_MANIFEST", "Natural continuous environmental audio metadata and hashes"),
        ("reports/phase16_continuous_provenance_audit.md", "AUDIT_REPORT", "Continuous environmental suite provenance and licensing audit"),
        ("reports/phase16_animal_false_positive_analysis.md", "FORENSIC_REPORT", "Animal vocalization false-positive deep-dive and candidate rule"),
        ("reports/phase16_boundary_analysis.md", "FORENSIC_REPORT", "Artificial concatenation boundary transient analysis and metric separation"),
        ("reports/phase16_latency_audit.md", "SYSTEM_REPORT", "Browser-to-server end-to-end latency audit and microbenchmarks"),
        ("reports/phase16_natural_continuous_comparison.md", "EVALUATION_REPORT", "Baseline comparison across 6+ hours of natural continuous audio"),
        ("reports/phase16_alert_timeline.csv", "EVALUATION_DATA", "Timestamped event timeline for all continuous false positive alerts"),
        ("reports/phase16_category_breakdown.csv", "EVALUATION_DATA", "Category-by-category false alert rates across operating profiles"),
        ("reports/phase16_continuous_metrics.json", "EVALUATION_DATA", "Structured JSON continuous evaluation metrics"),
        ("reports/phase16_statistical_analysis.md", "STATISTICAL_REPORT", "Poisson confidence intervals, rate ratios, and paired bootstrap"),
        ("reports/phase16_final_report.md", "MASTER_REPORT", "Phase 16 Master Technical Report")
    ]

    for rel_str, cat, desc in key_files:
        p = ROOT / rel_str
        if p.exists():
            h = compute_file_sha256(p)
            sz = p.stat().st_size
            manifest_records.append({
                "path": rel_str,
                "category": cat,
                "description": desc,
                "size_bytes": sz,
                "sha256": h,
                "status": "VERIFIED"
            })
        else:
            manifest_records.append({
                "path": rel_str,
                "category": cat,
                "description": desc,
                "status": "PENDING_OR_MISSING"
            })

    manifest_data = {
        "phase": 16,
        "title": "Natural Continuous Audio Validation, Source Independence & End-to-End System Audit",
        "safety_designation": SAFETY_DESIGNATION,
        "archive": {
            "path": str(ZIP_PATH),
            "size_bytes": size_bytes,
            "size_mb": round(size_mb, 2),
            "file_count": file_count,
            "sha256": sha16,
            "integrity_verified": True
        },
        "prior_archives": prior_status,
        "artifacts": manifest_records
    }

    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest_data, f, indent=2)

    print(f"[+] Saved Artifact Manifest: {manifest_path}")

if __name__ == "__main__":
    main()
