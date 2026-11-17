"""
Phase 12 Deployment Packaging and Integrity Verification Script.

Packages the verified Phase 12 workspace into gunshot_detection_phase12.zip,
verifies zip readability using testzip(), computes its SHA-256 checksum,
verifies immutability of all prior archives (Phases 8-11),
and generates reports/phase12_artifact_manifest.json.
"""

import os
import sys
import zipfile
import hashlib
import json
import time
from pathlib import Path

ROOT = Path("e:/gunshot/gunshot").resolve()
ZIP_PATH = Path("e:/gunshot/gunshot_detection_phase12.zip").resolve()
SAFETY_DESIGNATION = "RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY"


def compute_file_sha256(path: Path) -> str:
    hasher = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()


def main():
    print(f"Packaging {ROOT} into {ZIP_PATH}...")
    file_count = 0

    # Ensure any temporary lock or cache is handled cleanly
    with zipfile.ZipFile(ZIP_PATH, "w", compression=zipfile.ZIP_DEFLATED) as z:
        for dirpath, dirnames, filenames in os.walk(ROOT):
            dirnames[:] = [d for d in dirnames if d not in ("__pycache__", ".git", ".pytest_cache")]
            for f in filenames:
                if f.endswith(".pyc") or f.endswith(".tmp"):
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
    sha12 = compute_file_sha256(ZIP_PATH)
    size_bytes = ZIP_PATH.stat().st_size
    size_mb = size_bytes / (1024 * 1024)

    print("\n" + "=" * 60)
    print("PHASE 12 DEPLOYMENT ARCHIVE SUMMARY")
    print("=" * 60)
    print(f"Path:       {ZIP_PATH}")
    print(f"Size:       {size_mb:.2f} MB ({size_bytes} bytes)")
    print(f"Files:      {file_count}")
    print(f"SHA-256:    {sha12}")
    print("Integrity:  VERIFIED (testzip passed)")
    print("=" * 60 + "\n")

    # Verify all prior archives
    prior_archives = [
        ("phase8_zip", Path("e:/gunshot/gunshot_detection_phase8.zip"), "c8bd26d09b5a41903ae8308b7bcac42f37ecd00d95eb6abfa4295365e074d353"),
        ("phase9_zip", Path("e:/gunshot/gunshot_detection_phase9.zip"), "96ff780eaa38737ea66851195301beebc576a31a48319f3b0a71083c4dee2ff0"),
        ("phase10_zip", Path("e:/gunshot/gunshot_detection_phase10.zip"), "d8edb26b71d69d6e76a1834cc741bda272c71b475287d7bd7fe2f33be95c459d"),
        ("phase11_zip", Path("e:/gunshot/gunshot_detection_phase11.zip"), "c50a9b07ffe93f01118fbc2a26130fd73c800d717b6a372d2e76291c735404ef")
    ]

    deployment_data = {}
    for name, p, expected_sha in prior_archives:
        actual_sha = compute_file_sha256(p)
        if actual_sha != expected_sha:
            raise RuntimeError(f"FATAL: Prior archive {name} corrupted! Expected {expected_sha}, got {actual_sha}")
        with zipfile.ZipFile(p, "r") as z:
            bad = z.testzip()
            if bad is not None:
                raise RuntimeError(f"FATAL: Prior archive {name} testzip() failed: {bad}")
        deployment_data[name] = {
            "path": str(p),
            "sha256": actual_sha,
            "size_bytes": p.stat().st_size,
            "integrity_testzip": "PASSED",
            "historical_immutability": "VERIFIED_MATCH"
        }
        print(f"Verified prior archive {name}: intact and matching {expected_sha[:8]}...")

    deployment_data["phase12_zip"] = {
        "path": str(ZIP_PATH),
        "sha256": sha12,
        "size_bytes": size_bytes,
        "file_count": file_count,
        "integrity_testzip": "PASSED"
    }

    # Generate reports/phase12_artifact_manifest.json
    manifest_p = ROOT / "reports" / "phase12_artifact_manifest.json"
    manifest_data = {
        "audit_phase": "Phase 12",
        "audit_timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "safety_designation": SAFETY_DESIGNATION,
        "environment": {
            "python_version": sys.version,
            "platform": sys.platform
        },
        "model_bundle_artifacts": {
            "catboost_model.joblib": compute_file_sha256(ROOT / "models/gunshot_yamnet_bundle/catboost_model.joblib"),
            "classifier_head.keras": compute_file_sha256(ROOT / "models/gunshot_yamnet_bundle/classifier_head.keras"),
            "lightgbm_model.joblib": compute_file_sha256(ROOT / "models/gunshot_yamnet_bundle/lightgbm_model.joblib"),
            "xgboost_model.joblib": compute_file_sha256(ROOT / "models/gunshot_yamnet_bundle/xgboost_model.joblib"),
            "threshold.json": compute_file_sha256(ROOT / "models/gunshot_yamnet_bundle/threshold.json"),
            "model_config.json": compute_file_sha256(ROOT / "models/gunshot_yamnet_bundle/model_config.json")
        },
        "deployment_archives": deployment_data,
        "manifest_artifacts": {
            "phase10_evaluation_manifest.csv": compute_file_sha256(ROOT / "data/manifests/phase10_evaluation_manifest.csv"),
            "phase11_field_collection_manifest.csv": compute_file_sha256(ROOT / "data/manifests/phase11_field_collection_manifest.csv"),
            "phase12_independent_eval_manifest.csv": compute_file_sha256(ROOT / "data/manifests/phase12_independent_eval_manifest.csv")
        },
        "reports_artifacts": {
            "phase12_dataset_inventory.md": compute_file_sha256(ROOT / "reports/phase12_dataset_inventory.md"),
            "phase12_existing_data_provenance.json": compute_file_sha256(ROOT / "reports/phase12_existing_data_provenance.json"),
            "phase12_duplicate_and_overlap_audit.json": compute_file_sha256(ROOT / "reports/phase12_duplicate_and_overlap_audit.json"),
            "phase12_annotation_protocol.md": compute_file_sha256(ROOT / "reports/phase12_annotation_protocol.md"),
            "phase12_annotation_quality.json": compute_file_sha256(ROOT / "reports/phase12_annotation_quality.json"),
            "phase12_evaluation_results.json": compute_file_sha256(ROOT / "reports/phase12_evaluation_results.json"),
            "phase12_final_report.md": compute_file_sha256(ROOT / "reports/phase12_final_report.md")
        }
    }

    with open(manifest_p, "w", encoding="utf-8") as f:
        json.dump(manifest_data, f, indent=2)
    print(f"Generated {manifest_p}")


if __name__ == "__main__":
    main()
