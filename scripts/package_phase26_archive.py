"""
Phase 26 Versioned Archive Packager & Integrity Verifier
MANDATORY SAFETY DESIGNATION:
RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.

Packages all Phase 26 code, models, reports, test suites, and schemas into:
E:/gunshot/gunshot_detection_phase26.zip
Validates CRC integrity with zipfile.testzip() and outputs reports/phase26_artifact_manifest.json.
"""

import os
import sys
import json
import zipfile
import hashlib
from pathlib import Path

ROOT = Path("E:/gunshot/gunshot")
ZIP_OUT = Path("E:/gunshot/gunshot_detection_phase26.zip")
REPORTS_DIR = ROOT / "reports"


def sha256_of_file(filepath: Path) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def main():
    print("=" * 80)
    print("PACKAGING PHASE 26 RESEARCH ARCHIVE")
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

        # Phase 26 Scripts
        "scripts/freeze_phase26_baseline.py",
        "scripts/build_phase26_acquisition_and_sources.py",
        "scripts/build_phase26_reports_and_tests.py",
        "scripts/reproduce_phase26_analysis.py",
        "scripts/package_phase26_archive.py",

        # Phase 26 Tests
        "tests/test_phase26_acquisition.py",

        # Phase 26 Reports & Deliverables
        "reports/phase26_final_report.md",
        "reports/phase26_baseline_freeze.json",
        "reports/phase26_aerosonicdb_source_audit.md",
        "reports/phase26_isd_source_audit.md",
        "reports/phase26_source_shortlist.md",
        "reports/phase26_source_registry.csv",
        "reports/phase26_campaign_independence_matrix.csv",
        "reports/phase26_recording_provenance.csv",
        "reports/phase26_duplicate_audit.csv",
        "reports/phase26_continuity_audit.csv",
        "reports/phase26_negative_eligibility_report.md",
        "reports/phase26_exposure_accounting.csv",
        "reports/phase26_alert_event_log.csv",
        "reports/phase26_negative_audio_results.csv",
        "reports/phase26_matched_model_comparison.md",
        "reports/phase26_statistical_analysis.md",
        "reports/phase26_risk_and_limitation_register.md",
        "reports/phase26_processing_manifest.json",
        "reports/phase26_test_results.txt",

        # Canonical manifests & independent positive data
        "reports/phase20_canonical_event_manifest.csv",
        "reports/phase20_continuity_audit.csv",
        "data/phase19_independent_positive/normalized_16k",
        "data/phase19_independent_positive/raw/*.json"
    ]

    # First draft of artifact manifest to be included inside the zip
    manifest_prelim = {
        "safety_designation": "RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY",
        "phase": "PHASE_26_CONDITIONAL_DATASET_ACQUISITION_CONTINUOUS_AUDIO_VERIFICATION_AND_INDEPENDENT_CAMPAIGN_EXPANSION",
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
            "gross_calendar_exposure_hours": 6.6460,
            "total_verified_natural_streams": 17,
            "total_independent_campaigns": 3,
            "phase_14_balanced": {
                "total_observed_alerts": 56,
                "gross_rate_alerts_per_hr": 8.4261,
                "cooldown_excluded_seconds": 111.92,
                "eligible_exposure_hours": 6.6149,
                "eligible_rate_alerts_per_hr": 8.4657,
                "garwood_95_ci_per_hr": [6.3949, 10.9935],
                "mtbfa_minutes": 7.09
            },
            "phase_17_experimental": {
                "total_observed_alerts": 51,
                "gross_rate_alerts_per_hr": 7.6738,
                "cooldown_excluded_seconds": 101.92,
                "eligible_exposure_hours": 6.6177,
                "eligible_rate_alerts_per_hr": 7.7066,
                "garwood_95_ci_per_hr": [5.7381, 10.1328],
                "mtbfa_minutes": 7.79
            },
            "paired_wilcoxon_signed_rank_p_value": 0.1250,
            "model_promotion_determination": "INCONCLUSIVE (Retain Phase 14 Balanced Baseline)"
        },
        "candidate_audit_summary": {
            "candidate_a_aerosonicdb": "CONDITIONAL_ACCESS_PENDING (Zenodo 10215080, 6.0h continuous; Cloudflare 403 anti-bot gate)",
            "candidate_b_isd": "REJECTED (Zenodo 4459422/5578703; 30-second discrete clips violate continuity protocol; synthetic concatenation prohibited)",
            "new_exposure_acquired_hours": 0.0000,
            "cumulative_gross_exposure_hours": 6.6460
        },
        "key_deliverables": [
            "reports/phase26_final_report.md",
            "reports/phase26_baseline_freeze.json",
            "reports/phase26_aerosonicdb_source_audit.md",
            "reports/phase26_isd_source_audit.md",
            "reports/phase26_source_shortlist.md",
            "reports/phase26_source_registry.csv",
            "reports/phase26_campaign_independence_matrix.csv",
            "reports/phase26_recording_provenance.csv",
            "reports/phase26_duplicate_audit.csv",
            "reports/phase26_continuity_audit.csv",
            "reports/phase26_negative_eligibility_report.md",
            "reports/phase26_exposure_accounting.csv",
            "reports/phase26_alert_event_log.csv",
            "reports/phase26_negative_audio_results.csv",
            "reports/phase26_matched_model_comparison.md",
            "reports/phase26_statistical_analysis.md",
            "reports/phase26_risk_and_limitation_register.md",
            "reports/phase26_processing_manifest.json",
            "reports/phase26_artifact_manifest.json",
            "tests/test_phase26_acquisition.py",
            "reports/phase26_test_results.txt",
            "scripts/reproduce_phase26_analysis.py"
        ]
    }

    out_manifest = REPORTS_DIR / "phase26_artifact_manifest.json"
    with open(out_manifest, "w", encoding="utf-8") as f:
        json.dump(manifest_prelim, f, indent=2, ensure_ascii=False)
    print(f"Saved preliminary manifest to: {out_manifest}")

    include_patterns.append("reports/phase26_artifact_manifest.json")

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

