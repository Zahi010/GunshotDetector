#!/usr/bin/env python3
"""
scripts/package_phase41_release.py

Phase 41 Independent Evidence Reconciliation and Statistical Robustness Audit
Release Packaging and Output Hash Manifest Generation

Produces:
  - E:/gunshot/gunshot_detection_phase41_audit.zip
  - experiments/phase41/phase41_output_hash_manifest.json
"""

import hashlib
import json
import pathlib
import zipfile
import time

REPO_ROOT = pathlib.Path("E:/gunshot/gunshot")
PROJECT_ROOT = pathlib.Path("E:/gunshot")
P41_DIR = REPO_ROOT / "experiments" / "phase41"
ZIP_PATH = PROJECT_ROOT / "gunshot_detection_phase41_audit.zip"
MANIFEST_PATH = P41_DIR / "phase41_output_hash_manifest.json"

FILES_TO_PACKAGE = [
    # Metadata & Inventories
    "experiments/phase41/phase41_protected_file_hashes.json",
    "experiments/phase41/phase41_recording_inventory.csv",
    "experiments/phase41/phase41_inventory_reconciliation.md",
    
    # Hash Reconciliation
    "experiments/phase41/phase41_hash_reconciliation.csv",
    "experiments/phase41/phase41_hash_provenance_report.md",
    
    # Source Lineage & Similarity
    "experiments/phase41/phase41_source_lineage.csv",
    "experiments/phase41/phase41_similarity_results.csv",
    "experiments/phase41/phase41_similarity_methodology.md",
    
    # Fireworks Paired Audit
    "experiments/phase41/phase41_fireworks_reconstruction.csv",
    "experiments/phase41/phase41_crest_factor_mechanism_audit.csv",
    "experiments/phase41/phase41_fireworks_cluster_analysis.md",
    
    # Continuous Benchmark & Statistics
    "experiments/phase41/phase41_continuous_reconstruction.csv",
    "experiments/phase41/phase41_statistical_reproduction.json",
    "experiments/phase41/phase41_cluster_robust_analysis.md",
    
    # Claim Matrix & Scope Reconciliation
    "experiments/phase41/phase41_claim_evidence_matrix.csv",
    "experiments/phase41/phase41_audit_scope_reconciliation.md",
    
    # Test suite & Logs
    "tests/test_phase41_audit.py",
    "experiments/phase41/phase41_test_execution_log.txt",
    
    # Final Reports & Release Notes
    "experiments/phase41/phase41_final_audit_report.md",
    "experiments/phase41/phase41_release_notes.md",
    "reports/phase41_final_audit_report.md",
    
    # Scripts
    "scripts/record_phase41_protected_hashes.py",
    "scripts/build_phase41_recording_inventory.py",
    "scripts/build_phase41_hash_reconciliation.py",
    "scripts/run_phase41_source_and_similarity.py",
    "scripts/run_phase41_fireworks_mechanism_audit.py",
    "scripts/run_phase41_continuous_robustness.py",
    "scripts/build_phase41_claim_evidence_matrix.py",
    "scripts/package_phase41_release.py"
]

print(f"Creating release archive at {ZIP_PATH}...")
if ZIP_PATH.exists():
    ZIP_PATH.unlink()

file_entries = {}
with zipfile.ZipFile(ZIP_PATH, "w", compression=zipfile.ZIP_DEFLATED) as zf:
    for rel_str in FILES_TO_PACKAGE:
        full_p = REPO_ROOT / rel_str
        assert full_p.exists(), f"Missing deliverable: {rel_str}"
        data = full_p.read_bytes()
        sha = hashlib.sha256(data).hexdigest()
        size_b = len(data)
        
        # Store in ZIP with forward slash path
        arcname = rel_str.replace("\\", "/")
        zf.writestr(arcname, data)
        
        file_entries[arcname] = {
            "relative_path": arcname,
            "byte_size": size_b,
            "sha256": sha
        }

# Verify ZIP CRC
with zipfile.ZipFile(ZIP_PATH, "r") as zf:
    crc_check = zf.testzip()
    internal_count = len(zf.namelist())

assert crc_check is None, f"ZIP CRC failure: {crc_check}"
print(f"ZIP CRC check passed. Internal file count: {internal_count}")

# Check ZIP hash
zip_data = ZIP_PATH.read_bytes()
zip_sha = hashlib.sha256(zip_data).hexdigest()
zip_size = len(zip_data)

manifest_data = {
    "phase": "PHASE_41",
    "audit_name": "Independent Evidence Reconciliation and Statistical Robustness Audit",
    "mandatory_safety_designation": "RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY",
    "timestamp_iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    "governance_disposition": {
        "model_phase14.py": "DEFAULT_RESEARCH_BASELINE",
        "model_phase17.py": "SELECTABLE_EXPERIMENTAL_PROFILE_QUARANTINED_DEFECT",
        "experiments/phase31/model_phase17_state_reset_candidate.py": "QUARANTINED_DIAGNOSTIC_REFERENCE",
        "experiments/phase36/model_phase36.py": "EXPERIMENTAL_RESEARCH_BRANCH_V1_NOT_PROMOTED"
    },
    "release_archive": {
        "filename": "gunshot_detection_phase41_audit.zip",
        "byte_size": zip_size,
        "sha256": zip_sha,
        "internal_file_count": internal_count,
        "crc_status": "PASS"
    },
    "artifacts": file_entries
}

with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
    json.dump(manifest_data, f, indent=2)
print(f"Saved {MANIFEST_PATH}")
print(f"Phase 41 Release Archive SHA-256: {zip_sha} ({zip_size} bytes)")

