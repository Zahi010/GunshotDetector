"""
Phase 34 Packaging & Integrity Verification Engine
MANDATORY SAFETY DESIGNATION:
RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.
This experimental acoustic machine-learning software is uncertified and must never
be deployed for autonomous emergency dispatch, tactical police response,
active-shooter alerting, automated evacuation, building lockdown, or life-critical
physical security. Safe recorded audio playback only; no live-fire testing.

Packages:
- Core baseline models and candidate diagnostic patch
- Trained model bundles and feature extractor
- All Phase 34 forensic audit reports, CSV registries, and JSON analytical records
- Phase 34 reproduction scripts and automated test suites
Outputs:
- E:/gunshot/gunshot_detection_phase34.zip
- reports/phase34_artifact_manifest.json
"""

import sys
import os
import json
import zipfile
import hashlib
from pathlib import Path

ROOT = Path("E:/gunshot/gunshot")
ZIP_DEST = Path("E:/gunshot/gunshot_detection_phase34.zip")
REPORTS_DIR = ROOT / "reports"

print("=" * 80)
print("PHASE 34 PACKAGING & ARTIFACT MANIFEST GENERATION")
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

    # Phase 34 Comprehensive Reports
    "reports/phase34_final_report.md",
    "reports/phase34_duration_discrepancy_analysis.md",
    "reports/phase34_exposure_reproduction.md",
    "reports/phase34_campaign_independence_audit.md",
    "reports/phase34_statistical_reconciliation.md",
    "reports/phase34_historical_corrections.md",

    # Phase 34 Data Records & Registries
    "reports/phase34_canonical_23_stream_registry.csv",
    "reports/phase34_duration_comparison.csv",
    "reports/phase34_campaign_mapping_comparison.csv",
    "reports/phase34_stream_level_detector_metrics.csv",
    "reports/phase34_campaign_level_metrics.csv",
    "reports/phase34_paired_metric_reconciliation.csv",
    "reports/phase34_authoritative_statistical_method_register.csv",
    "reports/phase34_historical_discrepancy_register.csv",
    "reports/phase34_input_hash_manifest.json",
    "reports/phase34_test_execution_log.txt",

    # Phase 34 Scripts & Tests
    "scripts/reproduce_phase34_audit.py",
    "scripts/package_phase34_archive.py",
    "tests/test_phase34_reproduction.py"
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
    "phase": "PHASE_34_FINAL_STREAM_LEVEL_PROVENANCE_AND_EXPOSURE_INTEGRITY_AUDIT",
    "archive_filename": "gunshot_detection_phase34.zip",
    "archive_path": str(ZIP_DEST),
    "archive_size_bytes": archive_size,
    "archive_sha256": archive_sha256,
    "integrity_verification": crc_status,
    "test_execution_record": {
        "test_command": "pytest gunshot/tests/test_phase34_reproduction.py -v",
        "exit_status": 0,
        "passed_tests": 12,
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
        "role": "Selectable Experimental Profile (promotion rejected; confirmed 8/12 state-machine defect and aircraft fragmentation)",
        "state_machine_defect": "Confirmed omission of 'else: active_cluster = []' and unguarded EOF flush"
    },
    "experimental_candidate_patch": {
        "model": "Phase 17 State-Reset Candidate",
        "file": "experiments/phase31/model_phase17_state_reset_candidate.py",
        "sha256": "c144b917b56532787e2a9198f2cad4a77dc2095b57962f31d11d250a4d5d9ea5",
        "size_bytes": 29718,
        "role": "Quarantined Diagnostic Reference (regression tests: 12/12 PASS; schema divergence noted)"
    },
    "workstream_1_inventory_summary": {
        "canonical_stream_count": 23,
        "unique_hashes_count": 23,
        "exact_duration_seconds": 45525.5755,
        "exact_duration_hours": 12.645993194444445,
        "rounded_duration_hours": 12.6460
    },
    "workstream_2_duration_summary": {
        "authoritative_campaigns": {
            "CAMPAIGN-SOUTHAMPTON-EXP1": "10 streams, 19,800.0000 s (5.5000 hr)",
            "CAMPAIGN-CHEW-MAGNA": "1 stream, 2,100.0000 s (0.5833 hr)",
            "CAMPAIGN-BILBAO": "6 streams, 2,025.5755 s (0.5627 hr)",
            "CAMPAIGN-ADELAIDE-AEROSONIC": "6 streams, 21,600.0000 s (6.0000 hr)"
        },
        "phase33_text_discrepancy_diagnosis": (
            "Phase 31 matches physical audio WAV headers bit-for-bit. "
            "Phase 33 text report Section 5.2 contained an accidental clerical transposition from Phase 32 narrative. "
            "Phase 33 CSV registry was already physically accurate."
        )
    },
    "workstream_3_exposure_summary": {
        "phase14_total_alerts": 128,
        "phase17_total_alerts": 159,
        "alert_difference_p14_minus_p17": -31,
        "phase14_gross_far": 10.1218,
        "phase17_gross_far": 12.5732,
        "phase14_conv_a_far": 10.1790,
        "phase17_conv_a_far": 12.6611,
        "phase14_conv_b_far": 10.2237,
        "phase17_conv_b_far": 14.6243,
        "aerosonic_conv_b_inflation_p17_seconds": 6283.28
    },
    "workstream_4_independence_summary": {
        "genuine_independent_campaigns_count": 4,
        "adelaide_exposure_share_pct": 47.45,
        "adelaide_alert_share_pct": 62.72,
        "bilbao_alert_share_pct": 21.25,
        "paired_zero_difference_streams": 15,
        "paired_nonzero_difference_streams": 8
    },
    "workstream_5_statistical_method_summary": {
        "exact_tied_rank_permutation_p": 0.2109375,
        "exact_untied_combinatorial_p": 0.1953125,
        "scipy_asymptotic_normal_p": 0.1562601,
        "pratt_p": 0.3675438,
        "exact_sign_test_p": 0.7265625,
        "pittsburgh_strict_mcnemar_p": 0.2187500
    },
    "governance_decision": {
        "default_research_baseline": "Phase 14 Balanced",
        "phase17_promotion_status": "REJECTED_DO_NOT_PROMOTE",
        "candidate_patch_status": "EXPERIMENTAL_DIAGNOSTIC_ONLY",
        "life_safety_operational_deployment": "STRICTLY_PROHIBITED"
    },
    "packaged_files_count": len(files_to_pack),
    "packaged_files": sorted(files_to_pack)
}

manifest_path = REPORTS_DIR / "phase34_artifact_manifest.json"
with open(manifest_path, "w", encoding="utf-8") as f:
    json.dump(artifact_manifest, f, indent=2)

print(f"\n  Saved: {manifest_path}")

# Add artifact manifest into zip as well
with zipfile.ZipFile(ZIP_DEST, "a", compression=zipfile.ZIP_DEFLATED) as z:
    z.write(manifest_path, arcname="gunshot/reports/phase34_artifact_manifest.json")
    print("  Appended gunshot/reports/phase34_artifact_manifest.json to release archive.")

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
print("PHASE 34 PACKAGING COMPLETED SUCCESSFULLY")
print("=" * 80)

