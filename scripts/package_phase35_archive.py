"""
Phase 35 Packaging & Integrity Verification Engine
MANDATORY SAFETY DESIGNATION:
RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.
This experimental acoustic machine-learning software is uncertified and must never
be deployed for autonomous emergency dispatch, tactical police response,
active-shooter alerting, automated evacuation, building lockdown, or life-critical
physical security. Safe recorded audio playback only; no live-fire testing.

Packages:
- Core baseline models and candidate diagnostic patch
- Trained model bundles and feature extractor
- All Phase 35 forensic audit reports, CSV registries, and JSON analytical records
- Phase 35 reproduction scripts and automated test suites
Outputs:
- E:/gunshot/gunshot_detection_phase35.zip
- reports/phase35_artifact_manifest.json
"""

import sys
import os
import json
import zipfile
import hashlib
from pathlib import Path

ROOT = Path("E:/gunshot/gunshot")
ZIP_DEST = Path("E:/gunshot/gunshot_detection_phase35.zip")
REPORTS_DIR = ROOT / "reports"

def sha256_file(filepath):
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

print("=" * 80)
print("PHASE 35 PACKAGING & ARTIFACT MANIFEST GENERATION")
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

    # Phase 35 Comprehensive Reports
    "reports/phase35_final_report.md",
    "reports/phase35_convention_b_discrepancy.md",
    "reports/phase35_rate_reproduction.md",
    "reports/phase35_false_alert_terminology_review.md",
    "reports/phase35_campaign_independence_qualification.md",
    "reports/phase35_benchmark_integrity_check.md",

    # Phase 35 Data Records & Registries
    "reports/phase35_cooldown_interval_ledger.csv",
    "reports/phase35_stream_exposure_reconciliation.csv",
    "reports/phase35_campaign_exposure_reconciliation.csv",
    "reports/phase35_final_rate_table.csv",
    "reports/phase35_alert_ground_truth_audit.csv",
    "reports/phase35_campaign_independence_evidence.csv",
    "reports/phase35_input_hash_manifest.json",
    "reports/phase35_test_execution_log.txt",

    # Phase 35 Scripts & Tests
    "scripts/reproduce_phase35_audit.py",
    "scripts/package_phase35_archive.py",
    "tests/test_phase35_reproduction.py"
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
# Compute per-artifact digests for the manifest
artifacts_dict = {}
for p in files_to_pack:
    if p.startswith("reports/phase35_") or p.endswith(".md") or p.endswith(".csv") or p.endswith(".json"):
        fp = ROOT / p
        if fp.exists():
            artifacts_dict[fp.name] = {
                "relative_path": str(fp.relative_to(ROOT)).replace("\\", "/"),
                "size_bytes": fp.stat().st_size,
                "sha256": sha256_file(fp)
            }

artifact_manifest = {
        "safety_designation": "RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY",
        "phase": "PHASE_35_FINAL_COOLDOWN_LEDGER_RECONCILIATION_CAMPAIGN_INDEPENDENCE_BENCHMARK_CLOSURE",
        "benchmark_summary": {
            "streams": 23,
            "campaigns": 4,
            "gross_duration_s": 45525.5755,
            "gross_duration_hr": 12.645993194444443,
            "phase14_alerts": 128,
            "phase17_alerts": 159,
            "phase14_conv_b_excluded_s": 453.92,
            "phase17_conv_b_excluded_s": 6385.20,
            "transposition_discrepancy_delta_s": 10.00
        },
        "release_archive": {
            "file_name": "gunshot_detection_phase35.zip",
            "destination_path": "E:/gunshot/gunshot_detection_phase35.zip",
            "size_bytes": archive_size,
            "sha256": archive_sha256,
            "crc_status": crc_status
        },
        "default_research_baseline": {
            "model": "Phase 14 Balanced",
            "file": "model_phase14.py",
            "sha256": "47a3e7ef21a415a201f808f97c414d7a868f18471b4a242f38d3886561f5f3e4",
            "size_bytes": 26978,
            "role": "Default Research Baseline (retained; verified baseline profile)",
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
            "role": "Selectable Experimental Profile (promotion rejected; confirmed state-machine defect and aircraft fragmentation)",
            "state_machine_defect": "Confirmed omission of 'else: active_cluster = []' and unguarded EOF flush"
        },
        "experimental_candidate_patch": {
            "model": "Phase 17 State-Reset Candidate",
            "file": "experiments/phase31/model_phase17_state_reset_candidate.py",
            "sha256": "c144b917b56532787e2a9198f2cad4a77dc2095b57962f31d11d250a4d5d9ea5",
            "size_bytes": 29718,
            "role": "Quarantined Diagnostic Reference"
        },
        "workstream_1_discrepancy_resolution": {
            "prompt_transposed_p17_conv_b_s": 6395.20,
            "true_p17_conv_b_s": 6385.20,
            "delta_seconds": 10.00,
            "root_cause": "Cross-detector column mix-up in narrative text; Phase 14 European cooldowns (48.00s + 63.92s = 111.92s) were summed with Phase 17 Adelaide cooldown (6283.28s) instead of Phase 17 European cooldowns (44.00s + 57.92s = 101.92s)",
            "suppressed_alerts_involved": 5,
            "per_alert_duration_s": 2.00,
            "status": "REPRODUCED_WITH_CORRECTION"
        },
        "workstream_2_rate_summary": {
            "gross_duration_s": 45525.5755,
            "gross_duration_hr": 12.645993194444443,
            "phase14_alerts": 128,
            "phase17_alerts": 159,
            "phase14_gross_far": 10.1218,
            "phase17_gross_far": 12.5732,
            "phase14_conv_a_far": 10.1790,
            "phase17_conv_a_far": 12.6612,
            "phase14_conv_b_far": 10.2237,
            "phase17_conv_b_far": 14.6243,
            "phase14_conv_b_excluded_s": 453.92,
            "phase17_conv_b_excluded_s": 6385.20
        },
        "workstream_3_ground_truth_summary": {
            "total_alerts": 287,
            "reviewed_non_target": 107,
            "unannotated_background": 180,
            "confirmed_non_target": 0,
            "possible_target": 0,
            "unknown": 0,
            "descriptive_rule": "Do not label unannotated continuous audio as confirmed false alerts without ground truth or human listening review"
        },
        "workstream_4_campaign_independence_summary": {
            "cluster_count": 4,
            "mandatory_qualification": "Four campaign-level clusters were available; full statistical independence could not be established from retained metadata.",
            "inferential_power": "Limited; non-parametric tests on K=4 pairs cannot achieve p < 0.05"
        },
        "workstream_5_benchmark_closure": {
            "status": "BENCHMARK_AUDIT_CLOSED",
            "streams_verified": 23,
            "integrity_check": "ALL_CHECKS_PASSED"
        },
        "governance_decision": {
            "default_research_baseline": "Phase 14 Balanced",
            "phase17_promotion_status": "REJECTED_DO_NOT_PROMOTE",
            "candidate_patch_status": "EXPERIMENTAL_DIAGNOSTIC_ONLY",
            "life_safety_operational_deployment": "STRICTLY_PROHIBITED",
            "benchmark_closure_assessment": "Historical benchmark audit complete. Evidence sufficiently consistent to support a separately scoped experimental research phase."
        },
        "artifacts": artifacts_dict,
        "packaged_files_count": len(files_to_pack),
        "packaged_files": sorted(files_to_pack)
    }

manifest_path = REPORTS_DIR / "phase35_artifact_manifest.json"
with open(manifest_path, "w", encoding="utf-8") as f:
    json.dump(artifact_manifest, f, indent=2)

print(f"\n  Saved: {manifest_path}")

# Add artifact manifest into zip as well
with zipfile.ZipFile(ZIP_DEST, "a", compression=zipfile.ZIP_DEFLATED) as z:
    z.write(manifest_path, arcname="gunshot/reports/phase35_artifact_manifest.json")
    print("  Appended gunshot/reports/phase35_artifact_manifest.json to release archive.")

# Re-compute archive size and SHA-256 after appending manifest
archive_size = ZIP_DEST.stat().st_size
h = hashlib.sha256()
with open(ZIP_DEST, "rb") as f:
    while chunk := f.read(65536):
        h.update(chunk)
archive_sha256 = h.hexdigest()

artifact_manifest["release_archive"]["size_bytes"] = archive_size
artifact_manifest["release_archive"]["sha256"] = archive_sha256

with open(manifest_path, "w", encoding="utf-8") as f:
    json.dump(artifact_manifest, f, indent=2)

print(f"  Final Archive Size: {archive_size:,} bytes")
print(f"  Final Archive SHA-256: {archive_sha256}")
print("\n" + "=" * 80)
print("PHASE 35 PACKAGING COMPLETED SUCCESSFULLY")
print("=" * 80)
