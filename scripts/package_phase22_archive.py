"""
Phase 22 Versioned Archive Packager & Integrity Verifier
MANDATORY SAFETY DESIGNATION:
RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.

Packages all Phase 22 code, models, forensic reports, validation protocols, test suites, and schemas into:
E:/gunshot/gunshot_detection_phase22.zip
Validates CRC integrity with zipfile.testzip() and outputs reports/phase22_artifact_manifest.json.
"""

import os
import sys
import json
import zipfile
import hashlib
from pathlib import Path

ROOT = Path("E:/gunshot/gunshot")
ZIP_OUT = Path("E:/gunshot/gunshot_detection_phase22.zip")
REPORTS_DIR = ROOT / "reports"


def sha256_of_file(filepath: Path) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def main():
    print("=" * 80)
    print("PACKAGING PHASE 22 RESEARCH ARCHIVE")
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

        # Phase 22 Scripts
        "scripts/freeze_phase22_baseline.py",
        "scripts/run_phase22_burst_cooldown_forensics.py",
        "scripts/reproduce_phase22_analysis.py",
        "scripts/package_phase22_archive.py",

        # Phase 22 Tests
        "tests/test_phase22_validation_protocol.py",

        # Phase 22 Reports & Protocols
        "reports/phase22_baseline_freeze.json",
        "reports/phase22_burst_cooldown_forensics.csv",
        "reports/phase22_alert_event_timeline.csv",
        "reports/phase22_burst_cooldown_analysis.md",
        "reports/phase22_independent_validation_protocol.md",
        "reports/phase22_preregistered_analysis_plan.md",
        "reports/phase22_dataset_provenance_schema.json",
        "reports/phase22_dataset_acquisition_plan.md",
        "reports/phase22_negative_audio_protocol.md",
        "reports/phase22_model_promotion_criteria.md",
        "reports/phase22_risk_and_limitation_register.md",
        "reports/phase22_final_report.md",
        "reports/phase22_test_results.txt",

        # Essential Canonical Manifests
        "reports/phase20_canonical_event_manifest.csv",
        "reports/phase20_continuity_audit.csv",

        # Independent Data
        "data/phase19_independent_positive/normalized_16k",
        "data/phase19_independent_positive/raw/*.json"
    ]

    if ZIP_OUT.exists():
        ZIP_OUT.unlink()

    with zipfile.ZipFile(ZIP_OUT, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as zf:
        for pat in include_patterns:
            target = ROOT / pat
            if "*" in pat:
                parent = ROOT / Path(pat).parent
                glob_pat = Path(pat).name
                if parent.exists():
                    for p in parent.glob(glob_pat):
                        arcname = f"gunshot/{p.relative_to(ROOT).as_posix()}"
                        zf.write(p, arcname)
            elif target.is_file():
                arcname = f"gunshot/{pat}"
                zf.write(target, arcname)
            elif target.is_dir():
                for root, _, files in os.walk(target):
                    for f in files:
                        fp = Path(root) / f
                        arcname = f"gunshot/{fp.relative_to(ROOT).as_posix()}"
                        zf.write(fp, arcname)

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

    # Generate artifact manifest
    manifest = {
        "safety_designation": "RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY",
        "phase": "PHASE_22_VALIDATION_PROTOCOL_AND_BURST_COOLDOWN_FORENSICS",
        "archive_filename": ZIP_OUT.name,
        "archive_path": str(ZIP_OUT),
        "archive_size_bytes": zip_size,
        "archive_sha256": zip_sha256,
        "total_archive_entries": file_count,
        "integrity_verification": "PASS_TESTZIP_CRC_VERIFIED",
        "default_production_baseline": {
            "model": "Phase 14 Balanced",
            "file": "model_phase14.py",
            "sha256": "a268551604ae8b73068435ff10ab3d265065f56e0679757fca5b6bf0f061c065"
        },
        "selectable_experimental_profile": {
            "model": "Phase 17 Experimental (Animal Suppression)",
            "file": "model_phase17.py",
            "sha256": "e2b262b866fdd5d7f1a4ab91a7b8b9bac189ee8cc7a78603b3544ca1579fb819"
        },
        "forensic_audit_summary": {
            "total_physical_rounds_audited": 50,
            "phase_14_balanced": {
                "detected_with_independent_alert": 27,
                "detected_but_merged_into_earlier_alert": 5,
                "missed_while_in_refractory_cooldown": 2,
                "missed_while_eligible": 16,
                "ambiguous_due_to_insufficient_precision": 0
            },
            "phase_17_experimental": {
                "detected_with_independent_alert": 33,
                "detected_but_merged_into_earlier_alert": 6,
                "missed_while_in_refractory_cooldown": 3,
                "missed_while_eligible": 8,
                "ambiguous_due_to_insufficient_precision": 0
            },
            "primary_miss_root_cause": "Acoustic energy attenuation below detection threshold while eligible (16/23 Phase 14 misses, 69.6%), NOT refractory cooldown dead time (2/23 Phase 14 misses, 8.7%)."
        },
        "negative_audio_protocol_summary": {
            "target_exposure_hours": 100.0,
            "idealized_zero_alert_poisson_95_upper_bound_alerts_per_hr": 0.02996,
            "minimum_mtbfa_hours": 33.38
        },
        "key_deliverables": [
            "reports/phase22_final_report.md",
            "reports/phase22_baseline_freeze.json",
            "reports/phase22_burst_cooldown_forensics.csv",
            "reports/phase22_alert_event_timeline.csv",
            "reports/phase22_burst_cooldown_analysis.md",
            "reports/phase22_independent_validation_protocol.md",
            "reports/phase22_preregistered_analysis_plan.md",
            "reports/phase22_dataset_provenance_schema.json",
            "reports/phase22_dataset_acquisition_plan.md",
            "reports/phase22_negative_audio_protocol.md",
            "reports/phase22_model_promotion_criteria.md",
            "reports/phase22_risk_and_limitation_register.md",
            "reports/phase22_test_results.txt",
            "tests/test_phase22_validation_protocol.py",
            "scripts/reproduce_phase22_analysis.py"
        ]
    }

    out_manifest = REPORTS_DIR / "phase22_artifact_manifest.json"
    with open(out_manifest, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    print(f"Saved artifact manifest to: {out_manifest}")


if __name__ == "__main__":
    main()

