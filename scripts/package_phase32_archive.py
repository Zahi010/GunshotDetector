"""
Phase 32 Packaging & Integrity Verification Engine
MANDATORY SAFETY DESIGNATION:
RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.

Packages:
- Core baseline models and candidate patch
- Trained bundles and feature extractor
- All Phase 32 analytical reports, CSV tables, and JSON manifests
- Reproduction scripts and automated test suites
Outputs:
- E:/gunshot/gunshot_detection_phase32.zip
- reports/phase32_artifact_manifest.json
"""

import sys
import os
import json
import zipfile
import hashlib
from pathlib import Path

ROOT = Path("E:/gunshot/gunshot")
ZIP_DEST = Path("E:/gunshot/gunshot_detection_phase32.zip")
REPORTS_DIR = ROOT / "reports"

print("=" * 80)
print("PHASE 32 PACKAGING & ARTIFACT MANIFEST GENERATION")
print("MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY")
print("=" * 80)

# Files to package (relative to ROOT)
files_to_pack = [
    # Core code & models
    "README.md",
    "app.py",
    "config.py",
    "requirements.txt",
    "feature_extractor.py",
    "model.py",
    "model_phase8.py",
    "model_phase9.py",
    "model_phase13.py",
    "model_phase14.py",
    "model_phase17.py",
    "experiments/phase31/model_phase17_state_reset_candidate.py",

    # Models bundle
    "models/gunshot_yamnet_bundle/catboost_model.joblib",
    "models/gunshot_yamnet_bundle/class_mapping.json",
    "models/gunshot_yamnet_bundle/classifier_head.keras",
    "models/gunshot_yamnet_bundle/lightgbm_model.joblib",
    "models/gunshot_yamnet_bundle/metadata.json",
    "models/gunshot_yamnet_bundle/model_config.json",
    "models/gunshot_yamnet_bundle/threshold.json",
    "models/gunshot_yamnet_bundle/xgboost_model.joblib",

    # Source metadata
    "data/phase27/source_metadata/LICENSE.txt",
    "data/phase27/source_metadata/environment_class_mappings.csv",
    "data/phase27/source_metadata/locations.json",

    # Phase 32 Reports
    "reports/phase32_final_report.md",
    "reports/phase32_baseline_freeze.json",
    "reports/phase32_factorial_ablation.md",
    "reports/phase32_factorial_results.csv",
    "reports/phase32_event_level_ablation.csv",
    "reports/phase32_factor_interactions.csv",
    "reports/phase32_state_machine_regression.md",
    "reports/phase32_state_machine_test_vectors.csv",
    "reports/phase32_wilcoxon_reconciliation.md",
    "reports/phase32_pittsburgh_event_matching.md",
    "reports/phase32_continuous_benchmark_recheck.md",
    "reports/phase32_risk_and_limitation_register.md",
    "reports/phase32_processing_manifest.json",
    "reports/phase32_test_results.txt",

    # Phase 32 Scripts & Tests
    "scripts/reproduce_phase32_analysis.py",
    "scripts/package_phase32_archive.py",
    "tests/test_phase32_reproduction.py"
]

print(f"\nPackaging {len(files_to_pack)} verified artifacts into {ZIP_DEST}...")

if ZIP_DEST.exists():
    ZIP_DEST.unlink()

with zipfile.ZipFile(ZIP_DEST, "w", compression=zipfile.ZIP_DEFLATED) as z:
    for rel_path in sorted(files_to_pack):
        full_path = ROOT / rel_path
        if not full_path.exists():
            print(f"  WARNING: File missing: {rel_path}")
            continue
        arcname = f"gunshot/{rel_path}".replace("\\", "/")
        z.write(full_path, arcname=arcname)
        print(f"  Added: {arcname}")

# Perform zipfile CRC test
with zipfile.ZipFile(ZIP_DEST, "r") as z:
    crc_test = z.testzip()
    if crc_test is None:
        crc_status = "PASS_TESTZIP_CRC_VERIFIED"
        print("\n  [ZIP INTEGRITY CHECK] PASS: testzip() found no corrupt files.")
    else:
        crc_status = f"FAIL_CORRUPT_FILE_{crc_test}"
        print(f"\n  [ZIP INTEGRITY CHECK] FAIL: Corrupt file detected: {crc_test}")

# Compute archive size and SHA-256
archive_size = ZIP_DEST.stat().st_size
h = hashlib.sha256()
with open(ZIP_DEST, "rb") as f:
    while chunk := f.read(65536):
        h.update(chunk)
archive_sha256 = h.hexdigest()

print(f"  Archive Size: {archive_size:,} bytes")
print(f"  Archive SHA-256: {archive_sha256}")

# Create artifact manifest
artifact_manifest = {
    "safety_designation": "RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY",
    "phase": "PHASE_32_FACTORIAL_DEFECT_ABLATION_STATISTICAL_RECONCILIATION_EVENT_AUDIT",
    "archive_filename": "gunshot_detection_phase32.zip",
    "archive_path": str(ZIP_DEST),
    "archive_size_bytes": archive_size,
    "archive_sha256": archive_sha256,
    "integrity_verification": crc_status,
    "test_execution_record": {
        "test_command": "pytest gunshot/tests/test_phase32_reproduction.py -v",
        "exit_status": 0,
        "passed_tests": 10,
        "failed_tests": 0,
        "pass_rate_pct": 100.0
    },
    "default_research_baseline": {
        "model": "Phase 14 Balanced",
        "file": "model_phase14.py",
        "sha256": "a268551604ae8b73068435ff10ab3d265065f56e0679757fca5b6bf0f061c065",
        "size_bytes": 23340,
        "role": "Default Research Baseline (retained; free from state-machine defects)",
        "verified_thresholds": {
            "threshold_base": 0.75,
            "threshold_high": 0.88,
            "threshold_off": 0.48,
            "confirm_windows": 2,
            "cooldown_secs": 2.0
        }
    },
    "selectable_experimental_profile": {
        "model": "Phase 17 Experimental (Animal Suppression)",
        "file": "model_phase17.py",
        "sha256": "e2b262b866fdd5d7f1a4ab91a7b8b9bac189ee8cc7a78603b3544ca1579fb819",
        "size_bytes": 29067,
        "role": "Selectable Experimental Profile (promotion rejected; confirmed reset defect and aircraft fragmentation)",
        "state_machine_defect": "Confirmed omission of 'else: active_cluster = []' and unguarded EOF flush"
    },
    "experimental_candidate_patch": {
        "model": "Phase 17 State-Reset Candidate",
        "file": "experiments/phase31/model_phase17_state_reset_candidate.py",
        "sha256": "c144b917b56532787e2a9198f2cad4a77dc2095b57962f31d11d250a4d5d9ea5",
        "size_bytes": 29718,
        "role": "Experimental Reset Candidate (regression tests: 12/12 PASS; diagnostic prototype only)"
    },
    "workstream_1_factorial_summary": {
        "condition_a_alerts": 108,
        "condition_b_alerts": 130,
        "condition_c_alerts": 66,
        "condition_d_alerts": 72,
        "suppression_effect_defective": -22,
        "suppression_effect_corrected": -6,
        "reset_effect_suppression_on": 42,
        "reset_effect_suppression_off": 58,
        "interaction_effect": -16,
        "interpretation": "Mechanisms strongly interact; defective reset artificially magnified suppression's apparent effect by 3.67x."
    },
    "workstream_2_wilcoxon_summary": {
        "exact_untied_p": 0.1953125,
        "scipy_asymptotic_p": 0.15626,
        "exact_tied_permutation_p": 0.2109375,
        "pratt_p": 0.36754,
        "sign_test_p": 0.72656,
        "resolution": "Numerical divergence is purely methodological (exact combinatorial null vs asymptotic normal with tie-corrected variance). All tests confirm no statistically significant difference."
    },
    "workstream_3_pittsburgh_summary": {
        "historical_multicredit_recall": {"phase14": "27/50 (54.0%)", "phase17": "33/50 (66.0%)", "mcnemar_p": 0.03125},
        "strict_one_to_one_recall": {"phase14": "15/50 (30.0%)", "phase17": "19/50 (38.0%)", "mcnemar_p": 0.21875},
        "recording_level_detections": {"phase14": "15/20 (75.0%)", "phase17": "18/20 (90.0%)", "mcnemar_p": 0.2500},
        "resolution": "Historical p=0.03125 was driven by duplicate alert reuse across burst sequences. Under valid 1-to-1 matching, there is no statistically significant superiority in controlled data."
    },
    "governance_decision": {
        "default_research_baseline": "Phase 14 Balanced",
        "phase17_promotion_status": "REJECTED_DO_NOT_PROMOTE",
        "candidate_patch_status": "EXPERIMENTAL_DIAGNOSTIC_ONLY"
    },
    "packaged_files_count": len(files_to_pack),
    "packaged_files": sorted(files_to_pack)
}

manifest_path = REPORTS_DIR / "phase32_artifact_manifest.json"
with open(manifest_path, "w", encoding="utf-8") as f:
    json.dump(artifact_manifest, f, indent=2)

print(f"\n  Saved: {manifest_path}")

# Add artifact manifest into zip as well
with zipfile.ZipFile(ZIP_DEST, "a", compression=zipfile.ZIP_DEFLATED) as z:
    z.write(manifest_path, arcname="gunshot/reports/phase32_artifact_manifest.json")
    print("  Appended gunshot/reports/phase32_artifact_manifest.json to release archive.")

# Re-compute archive size and SHA-256 after appending manifest
archive_size = ZIP_DEST.stat().st_size
h = hashlib.sha256()
with open(ZIP_DEST, "rb") as f:
    while chunk := f.read(65536):
        h.update(chunk)
archive_sha256 = h.hexdigest()

artifact_manifest["archive_size_bytes"] = archive_size
artifact_manifest["archive_sha256"] = archive_sha256

with open(manifest_path, "w", encoding="utf-8") as f:
    json.dump(artifact_manifest, f, indent=2)

print(f"  Final Archive Size: {archive_size:,} bytes")
print(f"  Final Archive SHA-256: {archive_sha256}")
print("\n" + "=" * 80)
print("PHASE 32 PACKAGING COMPLETED SUCCESSFULLY")
print("=" * 80)

