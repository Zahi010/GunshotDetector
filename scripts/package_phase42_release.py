#!/usr/bin/env python3
"""
scripts/package_phase42_release.py

Phase 42 Benchmark Denominator Reconciliation & Independent Statistical Validation
Release Packaging, Cryptographic Hash Manifest Generation & Integrity Check

Produces:
  - E:/gunshot/gunshot_detection_phase42_audit.zip
  - experiments/phase42/phase42_output_hash_manifest.json
"""

import hashlib
import json
import pathlib
import zipfile
import time

REPO_ROOT = pathlib.Path("E:/gunshot/gunshot")
PROJECT_ROOT = pathlib.Path("E:/gunshot")
P42_DIR = REPO_ROOT / "experiments" / "phase42"
ZIP_PATH = PROJECT_ROOT / "gunshot_detection_phase42_audit.zip"
MANIFEST_PATH = P42_DIR / "phase42_output_hash_manifest.json"

FILES_TO_PACKAGE = [
    # Baseline protection
    "experiments/phase42/phase42_protected_file_hashes.json",
    
    # Workstream A: Continuous Exposure Denominator Reconciliation
    "experiments/phase42/phase42_continuous_exposure_reconciliation.csv",
    "experiments/phase42/phase42_stream_level_results.csv",
    "experiments/phase42/phase42_continuous_reconciliation.md",
    
    # Workstream B: Phase 17 Fireworks Discrepancy
    "experiments/phase42/phase42_fireworks_decision_reconciliation.csv",
    "experiments/phase42/phase42_fireworks_reconciliation.md",
    
    # Workstream C: Confidence Interval Methodology
    "experiments/phase42/phase42_confidence_interval_audit.csv",
    "experiments/phase42/phase42_statistical_methods.md",
    
    # Workstream D: Recordist-Level Dependence Audit
    "experiments/phase42/phase42_recordist_analysis.csv",
    "experiments/phase42/phase42_cluster_inference_report.md",
    
    # Workstream E: Positive Audio Deduplication & Recall Sensitivity
    "experiments/phase42/phase42_positive_deduplication_audit.csv",
    "experiments/phase42/phase42_positive_recall_sensitivity.md",
    
    # Workstream F: Crest Factor Mechanism Validation
    "experiments/phase42/phase42_crest_factor_reconstruction.csv",
    "experiments/phase42/phase42_mechanism_validation.md",
    
    # Workstream G: Authoritative Benchmark & Registers
    "experiments/phase42/phase42_authoritative_benchmark.csv",
    "experiments/phase42/phase42_discrepancy_register.csv",
    "experiments/phase42/phase42_claim_evidence_matrix.csv",
    
    # Test Suite & Execution Log
    "tests/test_phase42_audit.py",
    "experiments/phase42/phase42_test_execution_log.txt",
    
    # Final Reports & Release Notes
    "experiments/phase42/phase42_final_audit_report.md",
    "reports/phase42_final_audit_report.md",
    "experiments/phase42/phase42_release_notes.md"
]

def sha256_file(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

def verify_protected_hashes():
    print("Verifying protected baseline files before packaging...")
    hashes_path = P42_DIR / "phase42_protected_file_hashes.json"
    with open(hashes_path, "r", encoding="utf-8") as f:
        protected = json.load(f)
        if "protected_files" in protected:
            protected = protected["protected_files"]
        
    for rel_path, meta in protected.items():
        fpath = REPO_ROOT / rel_path
        assert fpath.exists(), f"Protected file missing: {rel_path}"
        actual_hash = sha256_file(fpath)
        actual_size = fpath.stat().st_size
        assert actual_hash == meta["sha256"], f"Protected hash altered: {rel_path}"
        assert actual_size == meta["byte_size"], f"Protected size altered: {rel_path}"
        print(f"  [OK] {rel_path} ({actual_size} bytes)")
    print("All protected baseline files match pre-audit baseline hashes exactly!\n")

def main():
    print("=== Packaging Phase 42 Audit Release ===")
    verify_protected_hashes()
    
    manifest = {
        "phase": "PHASE_42",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "mandatory_safety_designation": "RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY",
        "description": "Cryptographic SHA-256 hash manifest for Phase 42 deliverables",
        "files": {}
    }
    
    # First verify all files exist and compute hashes
    for rel_str in FILES_TO_PACKAGE:
        fpath = REPO_ROOT / rel_str
        if not fpath.exists():
            raise FileNotFoundError(f"Missing required artifact: {rel_str}")
        file_hash = sha256_file(fpath)
        file_size = fpath.stat().st_size
        manifest["files"][rel_str] = {
            "sha256": file_hash,
            "byte_size": file_size
        }
        print(f"  Hashed: {rel_str} ({file_size} B, {file_hash[:16]}...)")
        
    # Write output hash manifest
    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
    print(f"\nSaved manifest: {MANIFEST_PATH}")
    
    # Also add manifest itself to zip
    all_files_to_zip = FILES_TO_PACKAGE + ["experiments/phase42/phase42_output_hash_manifest.json"]
    
    # Create ZIP archive
    print(f"\nCreating ZIP archive: {ZIP_PATH}...")
    with zipfile.ZipFile(ZIP_PATH, "w", zipfile.ZIP_DEFLATED) as zf:
        for rel_str in all_files_to_zip:
            fpath = REPO_ROOT / rel_str
            # Store in zip with repo-relative path under gunshot/
            arcname = f"gunshot/{rel_str}"
            zf.write(fpath, arcname=arcname)
            print(f"  Added: {arcname}")
            
    zip_size = ZIP_PATH.stat().st_size
    zip_hash = sha256_file(ZIP_PATH)
    print(f"\n[SUCCESS] Package created: {ZIP_PATH}")
    print(f"  Size: {zip_size} bytes ({zip_size / 1024 / 1024:.2f} MB)")
    print(f"  SHA-256: {zip_hash}")

if __name__ == "__main__":
    main()
