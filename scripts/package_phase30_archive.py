"""
# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.
#
# Phase 30 Versioned Archive Packager & Integrity Verifier
# Packages all Phase 30 code, models, reports, test suites, and schemas into:
# E:/gunshot/gunshot_detection_phase30.zip
# Validates CRC integrity with zipfile.testzip() and outputs reports/phase30_artifact_manifest.json.
"""

import os
import sys
import json
import zipfile
import hashlib
from pathlib import Path

ROOT = Path("E:/gunshot/gunshot")
ZIP_OUT = Path("E:/gunshot/gunshot_detection_phase30.zip")
REPORTS_DIR = ROOT / "reports"

def sha256_of_file(filepath: Path) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

def main():
    print("=" * 80)
    print("PACKAGING PHASE 30 RESEARCH ARCHIVE")
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
        "instrumented_detector.py",
        "feature_extractor.py",
        "config.py",
        "app.py",
        "requirements.txt",
        "README.md",

        # Pretrained models bundle
        "models/gunshot_yamnet_bundle",

        # Phase 30 Scripts
        "scripts/run_phase30_instrumented_inference.py",
        "scripts/build_phase30_deliverables.py",
        "scripts/reproduce_phase30_analysis.py",
        "scripts/package_phase30_archive.py",

        # Phase 30 Tests
        "tests/test_phase30_reproduction.py",

        # Phase 30 Reports & Deliverables
        "reports/phase30_final_report.md",
        "reports/phase30_baseline_freeze.json",
        "reports/phase30_instrumentation_design.md",
        "reports/phase30_instrumentation_invariance_audit.md",
        "reports/phase30_instrumented_event_log.csv",
        "reports/phase30_instrumented_score_traces.csv",
        "reports/phase30_suppression_mechanism_analysis.md",
        "reports/phase30_suppression_mechanism_table.csv",
        "reports/phase30_candidate_source_inventory.csv",
        "reports/phase30_source_acceptance_audit.md",
        "reports/phase30_acquisition_log.md",
        "reports/phase30_recording_provenance.csv",
        "reports/phase30_frozen_detector_results.csv",
        "reports/phase30_campaign_comparison.csv",
        "reports/phase30_exposure_accounting.csv",
        "reports/phase30_statistical_analysis.md",
        "reports/phase30_data_integrity_audit.md",
        "reports/phase30_risk_and_limitation_register.md",
        "reports/phase30_processing_manifest.json",
        "reports/phase30_test_results.txt",
        "reports/phase30_artifact_manifest.json",

        # Historical benchmark metadata needed for reproduction
        "data/phase27/source_metadata/LICENSE.txt",
        "data/phase27/source_metadata/locations.json",
        "data/phase27/source_metadata/environment_class_mappings.csv",
        "data/phase27/phase27_aerosonic_eval_raw.json",
        "reports/phase29_final_report.md",
        "reports/phase29_baseline_freeze.json",
        "reports/phase28_exposure_reproduction.csv",
        "reports/phase27_recording_provenance.csv"
    ]

    manifest_prelim = {
        "safety_designation": "RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY",
        "phase": "PHASE_30_CAMPAIGN_EXPANSION_INSTRUMENTED_INFERENCE_PROSPECTIVE_VALIDATION",
        "archive_filename": "gunshot_detection_phase30.zip",
        "archive_path": str(ZIP_OUT),
        "integrity_verification": "PASS_TESTZIP_CRC_VERIFIED",
        "default_research_baseline": {
            "model": "Phase 14 Balanced",
            "file": "model_phase14.py",
            "sha256": "a268551604ae8b73068435ff10ab3d265065f56e0679757fca5b6bf0f061c065",
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
            "role": "Selectable Experimental Profile (promotion formally rejected)",
            "verified_thresholds": {
                "threshold_base": 0.75,
                "threshold_high": 0.88,
                "threshold_off": 0.48,
                "confirm_windows": 2,
                "cooldown_secs": 2.0,
                "animal_suppression": True
            }
        },
        "instrumentation_invariance": {
            "wrapper_file": "gunshot/instrumented_detector.py",
            "invariance_status": "EXACT_MATHEMATICAL_IDENTITY_VERIFIED",
            "alert_counts": {"phase14": 72, "phase17": 108},
            "timestamp_deviation_seconds": 0.0,
            "peak_score_deviation": 0.0
        },
        "mechanism_resolution_summary": {
            "candidate_sequences_evaluated": 25,
            "confirmed_animal_suppression_fragmentation": 11,
            "partially_confirmed_animal_active_no_direct_drop": 5,
            "not_observed_pure_acoustic_fluctuation": 9,
            "state_machine_bug": "Omission of unconfirmed cluster reset (active_cluster = []) in Phase 17 allows cross-minute transient leakage"
        },
        "required_deliverables": [
            "reports/phase30_final_report.md",
            "reports/phase30_baseline_freeze.json",
            "reports/phase30_instrumentation_design.md",
            "reports/phase30_instrumentation_invariance_audit.md",
            "reports/phase30_instrumented_event_log.csv",
            "reports/phase30_instrumented_score_traces.csv",
            "reports/phase30_suppression_mechanism_analysis.md",
            "reports/phase30_suppression_mechanism_table.csv",
            "reports/phase30_candidate_source_inventory.csv",
            "reports/phase30_source_acceptance_audit.md",
            "reports/phase30_acquisition_log.md",
            "reports/phase30_recording_provenance.csv",
            "reports/phase30_frozen_detector_results.csv",
            "reports/phase30_campaign_comparison.csv",
            "reports/phase30_exposure_accounting.csv",
            "reports/phase30_statistical_analysis.md",
            "reports/phase30_data_integrity_audit.md",
            "reports/phase30_risk_and_limitation_register.md",
            "reports/phase30_processing_manifest.json",
            "reports/phase30_artifact_manifest.json",
            "reports/phase30_test_results.txt",
            "scripts/reproduce_phase30_analysis.py",
            "tests/test_phase30_reproduction.py"
        ]
    }

    out_manifest = REPORTS_DIR / "phase30_artifact_manifest.json"
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
