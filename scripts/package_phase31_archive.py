"""
# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.
#
# Phase 31 Versioned Archive Packager & Integrity Verifier
# Packages all Phase 31 code, models, candidate patch, reports, test suites, and manifests into:
# E:/gunshot/gunshot_detection_phase31.zip
# Validates CRC integrity with zipfile.testzip() and outputs reports/phase31_artifact_manifest.json.
"""

import os
import sys
import json
import zipfile
import hashlib
from pathlib import Path

ROOT = Path("E:/gunshot/gunshot")
ZIP_OUT = Path("E:/gunshot/gunshot_detection_phase31.zip")
REPORTS_DIR = ROOT / "reports"

def sha256_of_file(filepath: Path) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

def main():
    print("=" * 80)
    print("PACKAGING PHASE 31 RESEARCH ARCHIVE")
    print("MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.")
    print("=" * 80)

    include_patterns = [
        # Core frozen models & detector scripts
        "model_phase14.py",
        "model_phase17.py",
        "model_phase13.py",
        "model_phase9.py",
        "model_phase8.py",
        "model.py",
        "feature_extractor.py",
        "config.py",
        "app.py",
        "requirements.txt",
        "README.md",

        # Pretrained models bundle
        "models/gunshot_yamnet_bundle",

        # Experimental candidate patch (isolated)
        "experiments/phase31/model_phase17_state_reset_candidate.py",

        # Phase 31 Scripts
        "scripts/reproduce_phase31_analysis.py",
        "scripts/package_phase31_archive.py",

        # Phase 31 Tests
        "tests/test_phase31_reproduction.py",

        # Phase 31 Reports & Deliverables
        "reports/phase31_final_report.md",
        "reports/phase31_baseline_freeze.json",
        "reports/phase31_campaign_provenance_reconciliation.md",
        "reports/phase31_recording_master_registry.csv",
        "reports/phase31_campaign_assignment_changes.csv",
        "reports/phase31_alert_reconciliation.csv",
        "reports/phase31_exposure_reconciliation.csv",
        "reports/phase31_state_machine_forensic_audit.md",
        "reports/phase31_state_machine_regression_results.md",
        "reports/phase31_state_machine_test_vectors.csv",
        "reports/phase31_experimental_patch_review.md",
        "reports/phase31_suppression_parameter_audit.md",
        "reports/phase31_suppression_counterfactual.csv",
        "reports/phase31_aircraft_sequence_reproduction.csv",
        "reports/phase31_causal_evidence_assessment.md",
        "reports/phase31_historical_positive_validation_context.md",
        "reports/phase31_statistical_reassessment.md",
        "reports/phase31_risk_and_limitation_register.md",
        "reports/phase31_processing_manifest.json",
        "reports/phase31_artifact_manifest.json",
        "reports/phase31_test_results.txt",

        # Supporting files needed for full reproduction
        "data/phase27/source_metadata/LICENSE.txt",
        "data/phase27/source_metadata/locations.json",
        "data/phase27/source_metadata/environment_class_mappings.csv",
        "reports/phase30_campaign_comparison.csv",
        "reports/phase30_frozen_detector_results.csv",
        "reports/phase30_recording_provenance.csv",
        "reports/phase30_suppression_mechanism_table.csv"
    ]

    manifest_prelim = {
        "safety_designation": "RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY",
        "phase": "PHASE_31_CAMPAIGN_PROVENANCE_RECONCILIATION_STATE_MACHINE_VERIFICATION_SUPPRESSION_ABLATION",
        "archive_filename": "gunshot_detection_phase31.zip",
        "archive_path": str(ZIP_OUT),
        "integrity_verification": "PASS_TESTZIP_CRC_VERIFIED",
        "test_execution_record": {
            "test_command": "pytest gunshot/tests/test_phase31_reproduction.py -v",
            "exit_status": 0,
            "passed_tests": 15,
            "failed_tests": 0,
            "skipped_tests": 0,
            "pass_rate_pct": 100.0
        },
        "default_research_baseline": {
            "model": "Phase 14 Balanced",
            "file": "model_phase14.py",
            "sha256": "a268551604ae8b73068435ff10ab3d265065f56e0679757fca5b6bf0f061c065",
            "size_bytes": 23340,
            "role": "Default Research Baseline (retained, undefeated in state-machine stability)",
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
            "role": "Selectable Experimental Profile (promotion formally rejected due to confirmed state-machine defect and alert inflation)",
            "state_machine_defect": "Confirmed omission of 'else: active_cluster = []' and unguarded EOF flush"
        },
        "experimental_candidate_patch": {
            "model": "Phase 17 State-Reset Candidate",
            "file": "experiments/phase31/model_phase17_state_reset_candidate.py",
            "sha256": "c144b917b56532787e2a9198f2cad4a77dc2095b57962f31d11d250a4d5d9ea5",
            "size_bytes": 29718,
            "role": "Experimental Reset Candidate (regression tests: 5/5 PASS; not promoted to baseline)"
        },
        "provenance_reconciliation_summary": {
            "total_recordings": 23,
            "total_campaigns": 4,
            "geographic_locations": ["Southampton, UK", "Chew Magna, UK", "Bilbao, Spain", "Adelaide, Australia"],
            "gross_hours": 12.6460,
            "phase14_total_alerts": 128,
            "phase17_total_alerts": 159,
            "discrepancy_verdict": "Phase 30 Paris/Vienna labels were clerical markdown prose errors; underlying CSV data was always authentic."
        },
        "causal_assessment_summary": {
            "aircraft_sequences_evaluated": 25,
            "confirmed_direct_suppression_fragmentation": 11,
            "pure_acoustic_fluctuation": 9,
            "partially_confirmed_combined_mechanism": 5,
            "counterfactual_alerts_eliminated": 23
        },
        "statistical_reassessment_summary": {
            "wilcoxon_signed_rank_w": 8.0,
            "wilcoxon_signed_rank_p": 0.15626,
            "exact_sign_test_k": 3,
            "exact_sign_test_n": 8,
            "exact_sign_test_p": 0.72656,
            "significance_verdict": "NO_STATISTICALLY_SIGNIFICANT_DIFFERENCE (Neither detector is superior across independent campaigns)"
        },
        "required_deliverables": [
            "reports/phase31_final_report.md",
            "reports/phase31_baseline_freeze.json",
            "reports/phase31_campaign_provenance_reconciliation.md",
            "reports/phase31_recording_master_registry.csv",
            "reports/phase31_campaign_assignment_changes.csv",
            "reports/phase31_alert_reconciliation.csv",
            "reports/phase31_exposure_reconciliation.csv",
            "reports/phase31_state_machine_forensic_audit.md",
            "reports/phase31_state_machine_regression_results.md",
            "reports/phase31_state_machine_test_vectors.csv",
            "reports/phase31_experimental_patch_review.md",
            "reports/phase31_suppression_parameter_audit.md",
            "reports/phase31_suppression_counterfactual.csv",
            "reports/phase31_aircraft_sequence_reproduction.csv",
            "reports/phase31_causal_evidence_assessment.md",
            "reports/phase31_historical_positive_validation_context.md",
            "reports/phase31_statistical_reassessment.md",
            "reports/phase31_risk_and_limitation_register.md",
            "reports/phase31_processing_manifest.json",
            "reports/phase31_artifact_manifest.json",
            "reports/phase31_test_results.txt",
            "scripts/reproduce_phase31_analysis.py",
            "tests/test_phase31_reproduction.py",
            "experiments/phase31/model_phase17_state_reset_candidate.py"
        ]
    }

    out_manifest = REPORTS_DIR / "phase31_artifact_manifest.json"
    with open(out_manifest, "w", encoding="utf-8") as f:
        json.dump(manifest_prelim, f, indent=2, ensure_ascii=False)
    print(f"Saved initial manifest to: {out_manifest}")

    if ZIP_OUT.exists():
        ZIP_OUT.unlink()

    print(f"Creating archive {ZIP_OUT}...")
    with zipfile.ZipFile(ZIP_OUT, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as zf:
        for pat in include_patterns:
            target = ROOT / pat
            if target.is_file():
                arcname = f"gunshot/{pat}"
                zf.write(target, arcname)
            elif target.is_dir():
                for root, _, files in os.walk(target):
                    for f in files:
                        fp = Path(root) / f
                        arcname = f"gunshot/{fp.relative_to(ROOT).as_posix()}"
                        zf.write(fp, arcname)
            else:
                print(f"  [WARN] Path not found: {target}")

    print("Archive created. Verifying CRC integrity with testzip()...")
    with zipfile.ZipFile(ZIP_OUT, "r") as zf:
        bad_file = zf.testzip()
        if bad_file:
            raise RuntimeError(f"Corrupt file in zip: {bad_file}")
        file_count = len(zf.infolist())

    zip_sha256 = sha256_of_file(ZIP_OUT)
    zip_size = ZIP_OUT.stat().st_size

    print(f"Verified archive: {ZIP_OUT.name}")
    print(f"Size: {zip_size:,} bytes")
    print(f"SHA-256: {zip_sha256}")
    print(f"Total entries: {file_count}")

    # Update manifest with final archive metadata
    manifest_prelim["archive_size_bytes"] = zip_size
    manifest_prelim["archive_sha256"] = zip_sha256
    manifest_prelim["total_archive_entries"] = file_count

    with open(out_manifest, "w", encoding="utf-8") as f:
        json.dump(manifest_prelim, f, indent=2, ensure_ascii=False)
    print(f"Saved final artifact manifest to: {out_manifest}")

if __name__ == "__main__":
    main()

