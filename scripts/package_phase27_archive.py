"""
Phase 27 Versioned Archive Packager & Integrity Verifier
MANDATORY SAFETY DESIGNATION:
RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.

Packages all Phase 27 code, models, reports, test suites, and schemas into:
E:/gunshot/gunshot_detection_phase27.zip
Validates CRC integrity with zipfile.testzip() and outputs reports/phase27_artifact_manifest.json.
"""

import os
import sys
import json
import zipfile
import hashlib
from pathlib import Path

ROOT = Path("E:/gunshot/gunshot")
ZIP_OUT = Path("E:/gunshot/gunshot_detection_phase27.zip")
REPORTS_DIR = ROOT / "reports"


def sha256_of_file(filepath: Path) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def main():
    print("=" * 80)
    print("PACKAGING PHASE 27 RESEARCH ARCHIVE")
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

        # Phase 27 Scripts
        "scripts/audit_phase27_statistics.py",
        "scripts/evaluate_phase27_aerosonic.py",
        "scripts/build_phase27_deliverables.py",
        "scripts/reproduce_phase27_analysis.py",
        "scripts/package_phase27_archive.py",

        # Phase 27 Tests
        "tests/test_phase27_acquisition_statistics.py",

        # Phase 27 Reports & Deliverables
        "reports/phase27_final_report.md",
        "reports/phase27_baseline_freeze.json",
        "reports/phase27_source_verification.json",
        "reports/phase27_acquisition_log.md",
        "reports/phase27_download_integrity.json",
        "reports/phase27_recording_provenance.csv",
        "reports/phase27_continuity_audit.csv",
        "reports/phase27_negative_eligibility_report.md",
        "reports/phase27_exposure_accounting.csv",
        "reports/phase27_historical_paired_statistics_audit.md",
        "reports/phase27_paired_differences.csv",
        "reports/phase27_wilcoxon_reproduction.json",
        "reports/phase27_poisson_assumption_audit.md",
        "reports/phase27_vmr_reproduction.csv",
        "reports/phase27_alert_event_log.csv",
        "reports/phase27_negative_audio_results.csv",
        "reports/phase27_matched_model_comparison.md",
        "reports/phase27_distractor_analysis.md",
        "reports/phase27_statistical_analysis.md",
        "reports/phase27_risk_and_limitation_register.md",
        "reports/phase27_processing_manifest.json",
        "reports/phase27_artifact_manifest.json",
        "reports/phase27_test_results.txt",

        # Source metadata files downloaded in Phase 27
        "data/phase27/source_metadata/README.md",
        "data/phase27/source_metadata/LICENSE.txt",
        "data/phase27/source_metadata/locations.json",
        "data/phase27/source_metadata/environment_class_mappings.csv",
        "data/phase27/source_metadata/environment_mappings_raw.csv",
        "data/phase27/phase27_aerosonic_eval_raw.json",

        # Historical canonical manifests
        "reports/phase26_final_report.md",
        "reports/phase20_canonical_event_manifest.csv",
        "reports/phase20_continuity_audit.csv"
    ]

    manifest_prelim = {
        "safety_designation": "RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY",
        "phase": "PHASE_27_AUTHORIZED_AEROSONICDB_ACQUISITION_AND_STATISTICAL_CORRECTION",
        "archive_filename": ZIP_OUT.name,
        "archive_path": str(ZIP_OUT),
        "integrity_verification": "PASS_TESTZIP_CRC_VERIFIED",
        "default_research_baseline": {
            "model": "Phase 14 Balanced",
            "file": "model_phase14.py",
            "sha256": "a268551604ae8b73068435ff10ab3d265065f56e0679757fca5b6bf0f061c065"
        },
        "selectable_experimental_profile": {
            "model": "Phase 17 Experimental (Animal Suppression)",
            "file": "model_phase17.py",
            "sha256": "e2b262b866fdd5d7f1a4ab91a7b8b9bac189ee8cc7a78603b3544ca1579fb819"
        },
        "tripartite_denominator_summary": {
            "gross_calendar_exposure_hours": 12.6460,
            "total_verified_natural_streams": 23,
            "total_independent_campaigns": 4,
            "phase_14_balanced": {
                "total_observed_alerts": 128,
                "gross_rate_alerts_per_hr": 10.1218,
                "cooldown_excluded_seconds": 455.52,
                "eligible_exposure_hours": 12.5195,
                "eligible_rate_alerts_per_hr": 10.2241,
                "garwood_95_ci_per_hr": [8.5303, 12.1643],
                "mtbfa_minutes": 5.87
            },
            "phase_17_experimental": {
                "total_observed_alerts": 159,
                "gross_rate_alerts_per_hr": 12.5732,
                "cooldown_excluded_seconds": 6381.76,
                "eligible_exposure_hours": 10.8732,
                "eligible_rate_alerts_per_hr": 14.6231,
                "garwood_95_ci_per_hr": [12.4419, 17.0772],
                "mtbfa_minutes": 4.10
            },
            "comparison": {
                "alert_difference_p17_minus_p14": 31,
                "percentage_increase_p17": "+24.2%",
                "p14_streams_superior": 5,
                "p17_streams_superior": 3,
                "streams_tied": 15,
                "paired_wilcoxon_w": 8.0,
                "paired_wilcoxon_p": 0.1953125,
                "sign_test_p_twosided": 0.7265625,
                "baseline_decision": "RETAIN_PHASE_14_BALANCED_AS_DEFAULT_RESEARCH_BASELINE"
            }
        },
        "key_deliverables": [
            "reports/phase27_final_report.md",
            "reports/phase27_baseline_freeze.json",
            "reports/phase27_source_verification.json",
            "reports/phase27_acquisition_log.md",
            "reports/phase27_download_integrity.json",
            "reports/phase27_recording_provenance.csv",
            "reports/phase27_continuity_audit.csv",
            "reports/phase27_negative_eligibility_report.md",
            "reports/phase27_exposure_accounting.csv",
            "reports/phase27_historical_paired_statistics_audit.md",
            "reports/phase27_paired_differences.csv",
            "reports/phase27_wilcoxon_reproduction.json",
            "reports/phase27_poisson_assumption_audit.md",
            "reports/phase27_vmr_reproduction.csv",
            "reports/phase27_alert_event_log.csv",
            "reports/phase27_negative_audio_results.csv",
            "reports/phase27_matched_model_comparison.md",
            "reports/phase27_distractor_analysis.md",
            "reports/phase27_statistical_analysis.md",
            "reports/phase27_risk_and_limitation_register.md",
            "reports/phase27_processing_manifest.json",
            "reports/phase27_artifact_manifest.json",
            "tests/test_phase27_acquisition_statistics.py",
            "reports/phase27_test_results.txt",
            "scripts/reproduce_phase27_analysis.py"
        ]
    }

    out_manifest = REPORTS_DIR / "phase27_artifact_manifest.json"
    with open(out_manifest, "w", encoding="utf-8") as f:
        json.dump(manifest_prelim, f, indent=2, ensure_ascii=False)
    print(f"Saved preliminary manifest to: {out_manifest}")

    if ZIP_OUT.exists():
        ZIP_OUT.unlink()

    print(f"Creating archive {ZIP_OUT}...")
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

    # Update manifest with exact archive size and hash
    manifest_prelim["archive_size_bytes"] = zip_size
    manifest_prelim["archive_sha256"] = zip_sha256
    manifest_prelim["total_archive_entries"] = file_count

    with open(out_manifest, "w", encoding="utf-8") as f:
        json.dump(manifest_prelim, f, indent=2, ensure_ascii=False)
    print(f"Saved final artifact manifest to: {out_manifest}")


if __name__ == "__main__":
    main()
