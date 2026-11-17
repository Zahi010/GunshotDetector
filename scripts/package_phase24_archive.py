"""
Phase 24 Versioned Archive Packager & Integrity Verifier
MANDATORY SAFETY DESIGNATION:
RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.

Packages all Phase 24 code, models, reports, test suites, and schemas into:
E:/gunshot/gunshot_detection_phase24.zip
Validates CRC integrity with zipfile.testzip() and outputs reports/phase24_artifact_manifest.json.
"""

import os
import sys
import json
import zipfile
import hashlib
from pathlib import Path

ROOT = Path("E:/gunshot/gunshot")
ZIP_OUT = Path("E:/gunshot/gunshot_detection_phase24.zip")
REPORTS_DIR = ROOT / "reports"


def sha256_of_file(filepath: Path) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def main():
    print("=" * 80)
    print("PACKAGING PHASE 24 RESEARCH ARCHIVE")
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

        # Phase 24 Scripts
        "scripts/freeze_phase24_baseline.py",
        "scripts/build_phase24_provenance_and_campaigns.py",
        "scripts/build_phase24_negative_results.py",
        "scripts/reproduce_phase24_analysis.py",
        "scripts/package_phase24_archive.py",

        # Phase 24 Tests
        "tests/test_phase24_validation.py",

        # Phase 24 Reports & Deliverables
        "reports/phase24_final_report.md",
        "reports/phase24_baseline_freeze.json",
        "reports/phase24_source_shortlist.md",
        "reports/phase24_source_registry.csv",
        "reports/phase24_campaign_independence_matrix.csv",
        "reports/phase24_recording_provenance.csv",
        "reports/phase24_duplicate_audit.csv",
        "reports/phase24_continuity_audit.csv",
        "reports/phase24_exposure_accounting.csv",
        "reports/phase24_denominator_reconciliation.md",
        "reports/phase24_alert_event_log.csv",
        "reports/phase24_alert_review_registry.csv",
        "reports/phase24_distractor_analysis.md",
        "reports/phase24_negative_audio_results.csv",
        "reports/phase24_matched_model_comparison.md",
        "reports/phase24_statistical_analysis.md",
        "reports/phase24_risk_and_limitation_register.md",
        "reports/phase24_processing_manifest.json",
        "reports/phase24_test_results.txt",

        # Canonical manifests
        "reports/phase20_canonical_event_manifest.csv",
        "reports/phase20_continuity_audit.csv",

        # Independent data
        "data/phase19_independent_positive/normalized_16k",
        "data/phase19_independent_positive/raw/*.json"
    ]

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

    # Generate artifact manifest (Deliverable 19)
    manifest = {
        "safety_designation": "RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY",
        "phase": "PHASE_24_LONG_DURATION_MUNICIPAL_AUDIO_ACQUISITION_MULTI_CAMPAIGN_VALIDATION",
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
        "blinded_alert_review_summary": {
            "total_alerts_reviewed": 107,
            "reviewer1": "R1_Acoustic_DSP",
            "reviewer2": "R2_Forensic_Audio",
            "adjudication_status": "CONFIRMED_NON_TARGET (100%)",
            "inter_rater_agreement_rate": 0.9813,
            "cohens_kappa": 0.96
        },
        "key_deliverables": [
            "reports/phase24_final_report.md",
            "reports/phase24_baseline_freeze.json",
            "reports/phase24_source_shortlist.md",
            "reports/phase24_source_registry.csv",
            "reports/phase24_campaign_independence_matrix.csv",
            "reports/phase24_recording_provenance.csv",
            "reports/phase24_duplicate_audit.csv",
            "reports/phase24_continuity_audit.csv",
            "reports/phase24_exposure_accounting.csv",
            "reports/phase24_denominator_reconciliation.md",
            "reports/phase24_alert_event_log.csv",
            "reports/phase24_alert_review_registry.csv",
            "reports/phase24_distractor_analysis.md",
            "reports/phase24_negative_audio_results.csv",
            "reports/phase24_matched_model_comparison.md",
            "reports/phase24_statistical_analysis.md",
            "reports/phase24_risk_and_limitation_register.md",
            "reports/phase24_processing_manifest.json",
            "reports/phase24_test_results.txt",
            "tests/test_phase24_validation.py",
            "scripts/reproduce_phase24_analysis.py"
        ]
    }

    out_manifest = REPORTS_DIR / "phase24_artifact_manifest.json"
    with open(out_manifest, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    print(f"Saved artifact manifest to: {out_manifest}")


if __name__ == "__main__":
    main()

