"""
Phase 13 Deployment Packaging and Integrity Verification Script.

Packages the verified Phase 13 workspace into gunshot_detection_phase13.zip,
verifies zip readability using testzip(), computes its SHA-256 checksum,
verifies immutability of all prior archives (Phases 8-12),
and generates reports/phase13_artifact_manifest.json.

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
ZIP_PATH = Path("e:/gunshot/gunshot_detection_phase13.zip").resolve()
SAFETY_DESIGNATION = "RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY"

def compute_file_sha256(path: Path) -> str:
    hasher = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()

def main():
    print("================================================================================")
    print("   PHASE 13 PACKAGING & CRYPTOGRAPHIC INTEGRITY VERIFICATION")
    print("================================================================================\n")
    print(f"Packaging {ROOT} into {ZIP_PATH}...")
    file_count = 0

    with zipfile.ZipFile(ZIP_PATH, "w", compression=zipfile.ZIP_DEFLATED) as z:
        for dirpath, dirnames, filenames in os.walk(ROOT):
            dirnames[:] = [d for d in dirnames if d not in ("__pycache__", ".git", ".pytest_cache")]
            for f in filenames:
                if f.endswith(".pyc") or f.endswith(".tmp") or f.startswith(".dev_features_cache"):
                    continue
                full_p = Path(dirpath) / f
                rel_p = full_p.relative_to(ROOT)
                z.write(full_p, rel_p)
                file_count += 1

    print(f"Successfully packaged {file_count} files into {ZIP_PATH}.")

    # Verify integrity
    print("Verifying archive integrity with testzip()...")
    with zipfile.ZipFile(ZIP_PATH, "r") as z:
        err = z.testzip()
        if err is not None:
            raise RuntimeError(f"Corrupted file found in archive: {err}")
        print("Archive testzip() verification: PASSED (None - zero corruption).")

    # Compute SHA-256
    print("Computing SHA-256 checksum...")
    sha13 = compute_file_sha256(ZIP_PATH)
    size_bytes = ZIP_PATH.stat().st_size
    size_mb = size_bytes / (1024 * 1024)

    print("\n" + "=" * 60)
    print("PHASE 13 DEPLOYMENT ARCHIVE SUMMARY")
    print("=" * 60)
    print(f"Path:       {ZIP_PATH}")
    print(f"Size:       {size_mb:.2f} MB ({size_bytes} bytes)")
    print(f"Files:      {file_count}")
    print(f"SHA-256:    {sha13}")
    print("Integrity:  VERIFIED (testzip passed)")
    print("=" * 60 + "\n")

    # Verify all prior archives
    prior_archives = [
        ("Phase 8", Path("e:/gunshot/gunshot_detection_phase8.zip"), "c8bd26d09b5a41903ae8308b7bcac42f37ecd00d95eb6abfa4295365e074d353"),
        ("Phase 9", Path("e:/gunshot/gunshot_detection_phase9.zip"), "96ff780eaa38737ea66851195301beebc576a31a48319f3b0a71083c4dee2ff0"),
        ("Phase 10", Path("e:/gunshot/gunshot_detection_phase10.zip"), "d8edb26b71d69d6e76a1834cc741bda272c71b475287d7bd7fe2f33be95c459d"),
        ("Phase 11", Path("e:/gunshot/gunshot_detection_phase11.zip"), "c50a9b07ffe93f01118fbc2a26130fd73c800d717b6a372d2e76291c735404ef"),
        ("Phase 12", Path("e:/gunshot/gunshot_detection_phase12.zip"), "8c674902761d469760928c81596813a08a942262440d977a423e58007055241a")
    ]

    all_prior_intact = True
    prior_status = {}
    for name, p, exp_hash in prior_archives:
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
            print(f"[OK] {name} archive verified: {actual_hash[:16]}... ({p.stat().st_size / (1024*1024):.2f} MB)")
            prior_status[name] = {"status": "VERIFIED_INTACT", "sha256": actual_hash}

    if not all_prior_intact:
        raise RuntimeError("Prior archive integrity check failed! Archive immutability violated.")
    print("\nAll prior deployment archives (Phases 8-12) confirmed 100% intact and immutable.")

    manifest = {
        "phase": 13,
        "safety_designation": SAFETY_DESIGNATION,
        "archive_filename": ZIP_PATH.name,
        "archive_path": str(ZIP_PATH),
        "archive_sha256": sha13,
        "archive_size_bytes": size_bytes,
        "archive_size_mb": round(size_mb, 2),
        "file_count": file_count,
        "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "key_deliverables": [
            "reports/phase13_continuous_alert_forensics.md",
            "reports/phase13_alert_timeline.csv",
            "reports/phase13_alert_forensics.json",
            "reports/phase13_evaluation_protocol_audit.md",
            "reports/phase13_provenance_reassessment.md",
            "reports/phase13_experiment_matrix.csv",
            "reports/phase13_continuous_benchmark_evaluation.json",
            "reports/phase13_final_report.md",
            "data/phase13_matched_continuous/phase13_matched_continuous_2hr.wav",
            "data/phase13_matched_continuous/phase13_stream_segments.csv",
            "model_phase13.py",
            "tests/test_phase13_regression_and_candidate.py"
        ],
        "prior_archives_verified": prior_status
    }

    manifest_path = Path("reports/phase13_artifact_manifest.json")
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
    print(f"Phase 13 artifact manifest saved to: {manifest_path}")

if __name__ == "__main__":
    main()
