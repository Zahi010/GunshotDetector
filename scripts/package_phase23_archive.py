"""
Phase 23 Versioned Archive Packager & Integrity Verifier
MANDATORY SAFETY DESIGNATION:
RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.

Packages all Phase 23 code, models, reports, test suites, and schemas into:
E:/gunshot/gunshot_detection_phase23.zip
Validates CRC integrity with zipfile.testzip() and outputs reports/phase23_artifact_manifest.json.
"""

import os
import sys
import json
import zipfile
import hashlib
from pathlib import Path

ROOT = Path("E:/gunshot/gunshot")
ZIP_OUT = Path("E:/gunshot/gunshot_detection_phase23.zip")
REPORTS_DIR = ROOT / "reports"


def sha256_of_file(filepath: Path) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def main():
    print("=" * 80)
    print("PACKAGING PHASE 23 RESEARCH ARCHIVE")
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

        # Phase 23 Scripts
        "scripts/freeze_phase23_baseline.py",
        "scripts/build_phase23_provenance_and_sources.py",
        "scripts/build_phase23_negative_benchmark.py",
        "scripts/reproduce_phase23_analysis.py",
        "scripts/package_phase23_archive.py",

        # Phase 23 Tests
        "tests/test_phase23_ingestion.py",

        # Phase 23 Reports & Artifacts
        "reports/phase23_baseline_freeze.json",
        "reports/phase23_source_shortlist.md",
        "reports/phase23_source_registry.csv",
        "reports/phase23_recording_provenance.csv",
        "reports/phase23_duplicate_audit.csv",
        "reports/phase23_source_eligibility_report.md",
        "reports/phase23_exposure_accounting.csv",
        "reports/phase23_negative_audio_results.csv",
        "reports/phase23_model_comparison.md",
        "reports/phase23_processing_manifest.json",
        "reports/phase23_risk_and_limitation_register.md",
        "reports/phase23_final_report.md",
        "reports/phase23_test_results.txt",

        # Canonical manifests
        "reports/phase20_canonical_event_manifest.csv",
        "reports/phase20_continuity_audit.csv",

        # Independent data
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
        "phase": "PHASE_23_FIRST_50_HOUR_NEGATIVE_EXPOSURE_BENCHMARK",
        "archive_filename": ZIP_OUT.name,
        "archive_path": str(ZIP_OUT),
        "archive_size_bytes": zip_size,
        "archive_sha256": zip_sha256,
        "total_archive_entries": file_count,
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
        "negative_exposure_summary": {
            "target_exposure_hours": 50.0,
            "achieved_verified_natural_exposure_hours": 6.6149,
            "shortfall_hours": 43.3851,
            "total_verified_natural_streams": 17,
            "total_independent_campaigns": 3,
            "phase_14_balanced": {
                "total_alerts": 56,
                "eligible_rate_alerts_per_hr": 8.4657,
                "garwood_95_ci_per_hr": [6.3949, 10.9935],
                "mtbfa_minutes": 7.1
            },
            "phase_17_experimental": {
                "total_alerts": 51,
                "eligible_rate_alerts_per_hr": 7.7066,
                "garwood_95_ci_per_hr": [5.7381, 10.1328],
                "mtbfa_minutes": 7.8
            },
            "wilcoxon_paired_recording_level_p_value": 0.1250,
            "model_promotion_determination": "INCONCLUSIVE (Retain Phase 14 Balanced Baseline)"
        },
        "key_deliverables": [
            "reports/phase23_final_report.md",
            "reports/phase23_source_shortlist.md",
            "reports/phase23_source_registry.csv",
            "reports/phase23_recording_provenance.csv",
            "reports/phase23_duplicate_audit.csv",
            "reports/phase23_source_eligibility_report.md",
            "reports/phase23_exposure_accounting.csv",
            "reports/phase23_negative_audio_results.csv",
            "reports/phase23_model_comparison.md",
            "reports/phase23_baseline_freeze.json",
            "reports/phase23_processing_manifest.json",
            "reports/phase23_risk_and_limitation_register.md",
            "reports/phase23_test_results.txt",
            "tests/test_phase23_ingestion.py",
            "scripts/reproduce_phase23_analysis.py"
        ]
    }

    out_manifest = REPORTS_DIR / "phase23_artifact_manifest.json"
    with open(out_manifest, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    print(f"Saved artifact manifest to: {out_manifest}")


if __name__ == "__main__":
    main()

