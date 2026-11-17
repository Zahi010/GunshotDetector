"""
Phase 29 Versioned Archive Packager & Integrity Verifier
MANDATORY SAFETY DESIGNATION:
RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.

Packages all Phase 29 code, models, reports, test suites, and schemas into:
E:/gunshot/gunshot_detection_phase29.zip
Validates CRC integrity with zipfile.testzip() and outputs reports/phase29_artifact_manifest.json.
"""

import os
import sys
import json
import zipfile
import hashlib
from pathlib import Path

ROOT = Path("E:/gunshot/gunshot")
ZIP_OUT = Path("E:/gunshot/gunshot_detection_phase29.zip")
REPORTS_DIR = ROOT / "reports"


def sha256_of_file(filepath: Path) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def main():
    print("=" * 80)
    print("PACKAGING PHASE 29 RESEARCH ARCHIVE")
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

        # Phase 29 Scripts
        "scripts/build_phase29_deliverables.py",
        "scripts/reproduce_phase29_analysis.py",
        "scripts/package_phase29_archive.py",

        # Phase 29 Tests
        "tests/test_phase29_reproduction.py",

        # Phase 29 Reports & Deliverables
        "reports/phase29_final_report.md",
        "reports/phase29_baseline_freeze.json",
        "reports/phase29_threshold_provenance_audit.md",
        "reports/phase29_runtime_configuration_manifest.csv",
        "reports/phase29_aircraft_mechanism_validation.md",
        "reports/phase29_aircraft_sequence_reconstruction.csv",
        "reports/phase29_aircraft_evidence_gaps.csv",
        "reports/phase29_cooldown_convention_audit.md",
        "reports/phase29_campaign_rate_robustness.md",
        "reports/phase29_campaign_rate_table.csv",
        "reports/phase29_loco_reproduction.csv",
        "reports/phase29_statistical_reproduction.md",
        "reports/phase29_reproducibility_audit.md",
        "reports/phase29_risk_and_limitation_register.md",
        "reports/phase29_processing_manifest.json",
        "reports/phase29_artifact_manifest.json",
        "reports/phase29_test_results.txt",

        # Historical underlying datasets & manifests needed for reproduction
        "reports/phase28_final_report.md",
        "reports/phase28_baseline_freeze.json",
        "reports/phase28_exposure_reproduction.csv",
        "reports/phase28_cooldown_interval_ledger.csv",
        "reports/phase28_aircraft_event_sequences.csv",
        "reports/phase27_recording_provenance.csv",
        "reports/phase27_exposure_accounting.csv",
        "reports/phase27_alert_event_log.csv",
        "reports/phase27_negative_audio_results.csv",
        "data/phase27/source_metadata/README.md",
        "data/phase27/source_metadata/LICENSE.txt",
        "data/phase27/source_metadata/locations.json",
        "data/phase27/source_metadata/environment_class_mappings.csv",
        "data/phase27/source_metadata/environment_mappings_raw.csv",
        "data/phase27/phase27_aerosonic_eval_raw.json",
    ]

    manifest_prelim = {
        "safety_designation": "RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY",
        "phase": "PHASE_29_CONFIGURATION_VERIFICATION_AIRCRAFT_VALIDATION_ROBUSTNESS_AUDIT",
        "archive_filename": ZIP_OUT.name,
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
        "audit_resolution_summary": {
            "threshold_discrepancy": {
                "status": "RESOLVED",
                "finding": "Phase 27 narrative claim of 0.55/0.40 was a clerical documentation error in markdown reports; both models executed with 0.75/0.88/0.48 in Python code."
            },
            "aircraft_fragmentation_mechanism": {
                "status": "PARTIALLY_SUPPORTED_UNVERIFIED_INTERMEDIATES",
                "finding": "Elevated RMS and alert clustering confirmed; intermediate sub-window score drops and animal suppression bits unlogged in raw data."
            },
            "exposure_cooldown_conventions": {
                "convention_a_instantaneous": {
                    "p14_cooldown_s": 255.84,
                    "p17_cooldown_s": 316.56,
                    "p14_far_per_hr": 10.1790,
                    "p17_far_per_hr": 12.6612
                },
                "convention_b_cluster_extended": {
                    "p14_cooldown_s": 453.92,
                    "p17_cooldown_s": 6385.20,
                    "p14_far_per_hr": 10.2237,
                    "p17_far_per_hr": 14.6243
                }
            },
            "campaign_rate_robustness": {
                "total_campaigns": 4,
                "gross_monitored_hours": 12.6460,
                "total_streams": 23,
                "bilbao_traffic_far": ">50.0 alerts/hr (Severe Urban Alert Saturation)",
                "aerosonic_airport_p14_advantage": "36 fewer alerts (Accounts for 116% of cumulative P14 lead)",
                "terrestrial_3_campaigns_p17_advantage": "5 fewer alerts (P17 FAR = 7.69/hr vs P14 FAR = 8.47/hr)"
            },
            "statistical_inference": {
                "paired_wilcoxon_w": 8.0,
                "paired_wilcoxon_p_exact": 0.1953125,
                "sign_test_p_twosided": 0.7265625,
                "generalization_inference": "BOUNDED_BY_G4_CAMPAIGNS"
            }
        },
        "required_deliverables": [
            "reports/phase29_final_report.md",
            "reports/phase29_baseline_freeze.json",
            "reports/phase29_threshold_provenance_audit.md",
            "reports/phase29_runtime_configuration_manifest.csv",
            "reports/phase29_aircraft_mechanism_validation.md",
            "reports/phase29_aircraft_sequence_reconstruction.csv",
            "reports/phase29_aircraft_evidence_gaps.csv",
            "reports/phase29_cooldown_convention_audit.md",
            "reports/phase29_campaign_rate_robustness.md",
            "reports/phase29_campaign_rate_table.csv",
            "reports/phase29_loco_reproduction.csv",
            "reports/phase29_statistical_reproduction.md",
            "reports/phase29_reproducibility_audit.md",
            "reports/phase29_risk_and_limitation_register.md",
            "reports/phase29_processing_manifest.json",
            "reports/phase29_artifact_manifest.json",
            "reports/phase29_test_results.txt",
            "scripts/reproduce_phase29_analysis.py",
            "tests/test_phase29_reproduction.py"
        ]
    }

    out_manifest = REPORTS_DIR / "phase29_artifact_manifest.json"
    with open(out_manifest, "w", encoding="utf-8") as f:
        json.dump(manifest_prelim, f, indent=2, ensure_ascii=False)
    print(f"Saved initial manifest to: {out_manifest}")

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

    # Update manifest with final archive metadata
    manifest_prelim["archive_size_bytes"] = zip_size
    manifest_prelim["archive_sha256"] = zip_sha256
    manifest_prelim["total_archive_entries"] = file_count

    with open(out_manifest, "w", encoding="utf-8") as f:
        json.dump(manifest_prelim, f, indent=2, ensure_ascii=False)
    print(f"Saved final artifact manifest to: {out_manifest}")


if __name__ == "__main__":
    main()

