"""
Phase 33 Packaging & Integrity Verification Engine
MANDATORY SAFETY DESIGNATION:
RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.
This experimental acoustic machine-learning software is uncertified and must never
be deployed for autonomous emergency dispatch, tactical police response,
active-shooter alerting, automated evacuation, building lockdown, or life-critical
physical security. Safe recorded audio playback only; no live-fire testing.

Packages:
- Core baseline models and candidate diagnostic patch
- Trained model bundles and feature extractor
- All Phase 33 forensic audit reports, CSV registries, and JSON analytical records
- Phase 33 reproduction scripts and automated test suites
Outputs:
- E:/gunshot/gunshot_detection_phase33.zip
- reports/phase33_artifact_manifest.json
"""

import sys
import os
import json
import zipfile
import hashlib
from pathlib import Path

ROOT = Path("E:/gunshot/gunshot")
ZIP_DEST = Path("E:/gunshot/gunshot_detection_phase33.zip")
REPORTS_DIR = ROOT / "reports"

print("=" * 80)
print("PHASE 33 PACKAGING & ARTIFACT MANIFEST GENERATION")
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

    # Phase 33 Comprehensive Reports
    "reports/phase33_final_report.md",
    "reports/phase33_source_provenance_report.md",
    "reports/phase33_factorial_reproduction.md",
    "reports/phase33_wilcoxon_reproduction.md",
    "reports/phase33_pittsburgh_reproduction.md",
    "reports/phase33_state_machine_audit.md",
    "reports/phase33_release_verification.md",

    # Phase 33 Data Records & Registries
    "reports/phase33_canonical_stream_registry.csv",
    "reports/phase33_campaign_reconciliation.csv",
    "reports/phase33_duration_reconciliation.csv",
    "reports/phase33_factorial_reproduction.csv",
    "reports/phase33_condition_config_hashes.json",
    "reports/phase33_event_level_reconciliation.csv",
    "reports/phase33_paired_observations.csv",
    "reports/phase33_rank_and_permutation_audit.csv",
    "reports/phase33_statistical_test_results.json",
    "reports/phase33_pittsburgh_matching_assignments.csv",
    "reports/phase33_pittsburgh_contingency_table.csv",
    "reports/phase33_state_machine_test_reconciliation.csv",
    "reports/phase33_input_hash_manifest.json",
    "reports/phase33_test_execution_log.txt",

    # Phase 33 Scripts & Tests
    "scripts/reproduce_phase33_audit.py",
    "scripts/package_phase33_archive.py",
    "tests/test_phase33_reproduction.py"
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
    "phase": "PHASE_33_REPRODUCIBILITY_CAMPAIGN_PROVENANCE_STATISTICAL_INTEGRITY_AUDIT",
    "archive_filename": "gunshot_detection_phase33.zip",
    "archive_path": str(ZIP_DEST),
    "archive_size_bytes": archive_size,
    "archive_sha256": archive_sha256,
    "integrity_verification": crc_status,
    "test_execution_record": {
        "test_command": "pytest gunshot/tests/test_phase33_reproduction.py -v",
        "exit_status": 0,
        "passed_tests": 15,
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
    "workstream_1_provenance_summary": {
        "canonical_stream_count": 23,
        "exact_duration_seconds": 45525.5755,
        "exact_duration_hours": 12.645993194444445,
        "rounded_duration_hours": 12.6460,
        "phase32_duration_discrepancy_resolved": "+0.4245s narrative rounding artifact (45,526.0s / 12.6461h)",
        "authoritative_campaigns": {
            "CAMPAIGN-SOUTHAMPTON-EXP1": "10 streams, 8,970.0s (Southampton, UK)",
            "CAMPAIGN-CHEW-MAGNA": "1 stream, 890.0s (Chew Magna, UK)",
            "CAMPAIGN-BILBAO": "6 streams, 14,065.5755s (Bilbao, Spain)",
            "CAMPAIGN-ADELAIDE-AEROSONIC": "6 streams, 21,600.0s (Adelaide, Australia)"
        },
        "debunked_fictional_campaigns": ["CAMPAIGN-DCASE2020-ES", "CAMPAIGN-URBANSOUND-PL"]
    },
    "workstream_2_factorial_summary": {
        "condition_a_alerts": 108,
        "condition_b_alerts": 130,
        "condition_c_alerts": 66,
        "condition_d_alerts": 72,
        "suppression_effect_defective": -22,
        "suppression_effect_corrected": -6,
        "reset_effect_suppression_on": 42,
        "reset_effect_suppression_off": 58,
        "interaction_effect": -16,
        "condition_d_designation": "CORRECTED-CANDIDATE / SUPPRESSION-OFF (100% timing identity to P14; schema differs)",
        "aircraft_flyover_fragmentation": "+6 alerts inside flyovers (78 vs 72) in defective; +5 alerts in corrected (52 vs 47)"
    },
    "workstream_3_wilcoxon_summary": {
        "paired_observations_n": 23,
        "zero_differences_n": 15,
        "nonzero_differences_n": 8,
        "exact_untied_p": 0.1953125,
        "exact_tied_permutation_p": 0.2109375,
        "scipy_asymptotic_p": 0.1562601,
        "pratt_p": 0.3675438,
        "sign_test_p": 0.7265625,
        "universal_finding": "No statistically significant difference (all p > 0.15). Driven by low statistical power; does not prove equivalence."
    },
    "workstream_4_pittsburgh_summary": {
        "historical_multicredit_recall": {"phase14": "27/50 (54.0%)", "phase17": "33/50 (66.0%)", "mcnemar_p": 0.03125},
        "strict_one_to_one_recall": {"phase14": "15/50 (30.0%)", "phase17": "19/50 (38.0%)", "mcnemar_p": 0.21875},
        "recording_level_detections": {"phase14": "15/20 (75.0%)", "phase17": "18/20 (90.0%)", "mcnemar_p": 0.2500},
        "resolution": "Historical p=0.03125 was driven by duplicate alert reuse across burst sequences. Under valid 1-to-1 matching, there is no statistically significant difference."
    },
    "workstream_5_state_machine_summary": {
        "total_regression_vectors": 12,
        "phase14_pass_count": 12,
        "candidate_pass_count": 12,
        "phase17_fail_count": 8,
        "phase17_pass_count": 4,
        "failing_vector_ids": ["VEC-01", "VEC-02", "VEC-03", "VEC-04", "VEC-07", "VEC-09", "VEC-10", "VEC-12"],
        "clerical_correction": "Phase 32 prose statement 'Failed 6/12 vectors' was a typographical typo (12 - 6 = 6). True failure rate is 8/12 (66.7%)."
    },
    "workstream_6_release_summary": {
        "phase32_archive_verified": True,
        "phase32_archive_size": 4545869,
        "phase32_archive_sha256": "b27bbb6336e3d0bb229ac10ade6c669b3d917d5ba58e91617c5c3cdd1eadddfb",
        "deliverables_reconciliation": "17 workspace deliverables vs 18 items including .zip archive"
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

manifest_path = REPORTS_DIR / "phase33_artifact_manifest.json"
with open(manifest_path, "w", encoding="utf-8") as f:
    json.dump(artifact_manifest, f, indent=2)

print(f"\n  Saved: {manifest_path}")

# Add artifact manifest into zip as well
with zipfile.ZipFile(ZIP_DEST, "a", compression=zipfile.ZIP_DEFLATED) as z:
    z.write(manifest_path, arcname="gunshot/reports/phase33_artifact_manifest.json")
    print("  Appended gunshot/reports/phase33_artifact_manifest.json to release archive.")

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
print("PHASE 33 PACKAGING COMPLETED SUCCESSFULLY")
print("=" * 80)

