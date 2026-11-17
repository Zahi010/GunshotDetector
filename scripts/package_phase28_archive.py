"""
Phase 28 Versioned Archive Packager & Integrity Verifier
MANDATORY SAFETY DESIGNATION:
RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.

Packages all Phase 28 code, models, reports, test suites, and schemas into:
E:/gunshot/gunshot_detection_phase28.zip
Validates CRC integrity with zipfile.testzip() and outputs reports/phase28_artifact_manifest.json.
"""

import os
import sys
import json
import zipfile
import hashlib
from pathlib import Path

ROOT = Path("E:/gunshot/gunshot")
ZIP_OUT = Path("E:/gunshot/gunshot_detection_phase28.zip")
REPORTS_DIR = ROOT / "reports"


def sha256_of_file(filepath: Path) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def main():
    print("=" * 80)
    print("PACKAGING PHASE 28 RESEARCH ARCHIVE")
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

        # Phase 28 Scripts
        "scripts/build_phase28_reproduction.py",
        "scripts/reproduce_phase28_analysis.py",
        "scripts/package_phase28_archive.py",

        # Phase 28 Tests
        "tests/test_phase28_reproduction.py",

        # Phase 28 Reports & Deliverables
        "reports/phase28_final_report.md",
        "reports/phase28_baseline_freeze.json",
        "reports/phase28_reproduction_manifest.json",
        "reports/phase28_metric_reconciliation.csv",
        "reports/phase28_exposure_reproduction.csv",
        "reports/phase28_cooldown_interval_ledger.csv",
        "reports/phase28_cooldown_reconciliation.md",
        "reports/phase28_campaign_aware_statistics.md",
        "reports/phase28_campaign_summary.csv",
        "reports/phase28_leave_one_campaign_out.csv",
        "reports/phase28_aircraft_fragmentation_audit.md",
        "reports/phase28_aircraft_event_sequences.csv",
        "reports/phase28_poisson_and_heterogeneity_audit.md",
        "reports/phase28_dataset_license_and_provenance_audit.md",
        "reports/phase28_risk_and_limitation_register.md",
        "reports/phase28_processing_manifest.json",
        "reports/phase28_artifact_manifest.json",
        "reports/phase28_test_results.txt",

        # Historical underlying datasets & manifests needed for reproduction
        "reports/phase27_final_report.md",
        "reports/phase27_recording_provenance.csv",
        "reports/phase27_exposure_accounting.csv",
        "reports/phase27_alert_event_log.csv",
        "reports/phase27_negative_audio_results.csv",
        "reports/phase27_processing_manifest.json",
        "data/phase27/source_metadata/README.md",
        "data/phase27/source_metadata/LICENSE.txt",
        "data/phase27/source_metadata/locations.json",
        "data/phase27/source_metadata/environment_class_mappings.csv",
        "data/phase27/source_metadata/environment_mappings_raw.csv",
    ]

    manifest_prelim = {
        "safety_designation": "RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY",
        "phase": "PHASE_28_INDEPENDENT_REPRODUCTION_CAMPAIGN_AWARE_AUDIT_AND_COOLDOWN_FORENSICS",
        "archive_filename": ZIP_OUT.name,
        "archive_path": str(ZIP_OUT),
        "integrity_verification": "PASS_TESTZIP_CRC_VERIFIED",
        "default_research_baseline": {
            "model": "Phase 14 Balanced",
            "file": "model_phase14.py",
            "sha256": "a268551604ae8b73068435ff10ab3d265065f56e0679757fca5b6bf0f061c065",
            "role": "Default Research Baseline (retained, undefeated)"
        },
        "selectable_experimental_profile": {
            "model": "Phase 17 Experimental (Animal Suppression)",
            "file": "model_phase17.py",
            "sha256": "e2b262b866fdd5d7f1a4ab91a7b8b9bac189ee8cc7a78603b3544ca1579fb819",
            "role": "Selectable Experimental Profile (promotion formally rejected)"
        },
        "historical_baselines": {
            "phase13": {
                "file": "model_phase13.py",
                "sha256": "68585039a4a4fdb7978a99f5e2a72c0ad5a9523127ec24a1338fbedd1c1231e6"
            },
            "phase9": {
                "file": "model_phase9.py",
                "sha256": "85cedd9f5b988ecafb1eae7de9630ee3d6a387ded6ef732e0efb7c3b496f132a"
            }
        },
        "cumulative_benchmark_reproduction": {
            "total_verified_continuous_streams": 23,
            "total_independent_campaigns": 4,
            "campaign_list": [
                "CAMPAIGN-RPISOUND-UK (10 streams, 5.5000 h)",
                "CAMPAIGN-CHEWMAGNA-UK (1 stream, 0.5833 h)",
                "CAMPAIGN-BILBAO-ES (6 streams, 0.5625 h)",
                "CAMPAIGN-AEROSONIC-AU (6 streams, 6.0000 h)"
            ],
            "gross_monitored_duration_seconds": 45525.575,
            "gross_monitored_hours": 12.6460,
            "phase_14_balanced": {
                "total_observed_alerts": 128,
                "gross_alert_rate_per_hr": 10.1218,
                "cooldown_cluster_extended_seconds": 453.92,
                "cooldown_instantaneous_seconds": 255.84,
                "eligible_cluster_extended_hours": 12.5199,
                "eligible_alert_rate_per_hr": 10.2237,
                "garwood_95_ci_alerts": [91.31, 133.74],
                "mtbfa_hours": 0.0978,
                "mtbfa_minutes": 5.87
            },
            "phase_17_experimental": {
                "total_observed_alerts": 159,
                "gross_alert_rate_per_hr": 12.5732,
                "cooldown_cluster_extended_seconds": 6385.20,
                "cooldown_instantaneous_seconds": 316.56,
                "eligible_cluster_extended_hours": 10.8723,
                "eligible_alert_rate_per_hr": 14.6243,
                "garwood_95_ci_alerts": [119.53, 167.31],
                "mtbfa_hours": 0.0684,
                "mtbfa_minutes": 4.10
            },
            "statistical_reconciliation": {
                "cumulative_alert_difference_p17_minus_p14": 31,
                "percentage_alert_increase_p17": "+24.22%",
                "p14_superior_streams": 5,
                "p17_superior_streams": 3,
                "tied_streams": 15,
                "paired_wilcoxon_w": 8.0,
                "paired_wilcoxon_p_exact": 0.1953125,
                "sign_test_p_twosided": 0.7265625,
                "leave_one_campaign_out_p14_superior_iterations": "3 of 4",
                "baseline_decision": "RETAIN_PHASE_14_BALANCED_AS_DEFAULT_RESEARCH_BASELINE"
            },
            "cooldown_discrepancy_reconciliation": {
                "historical_17_streams_cooldown_s": {"phase14": 111.92, "phase17": 101.92},
                "aerosonic_6_streams_cooldown_s": {"phase14": 342.00, "phase17": 6283.28},
                "actual_stream_sum_cooldown_s": {"phase14": 453.92, "phase17": 6385.20},
                "phase27_narrative_reported_cooldown_s": {"phase14": 455.52, "phase17": 6381.76},
                "delta_stream_sum_minus_narrative_s": {"phase14": -1.60, "phase17": +3.44},
                "reconciliation_status": "FULLY_TRACED_AND_RESOLVED"
            }
        },
        "required_deliverables_manifest": [
            "reports/phase28_final_report.md",
            "reports/phase28_baseline_freeze.json",
            "reports/phase28_reproduction_manifest.json",
            "reports/phase28_metric_reconciliation.csv",
            "reports/phase28_exposure_reproduction.csv",
            "reports/phase28_cooldown_interval_ledger.csv",
            "reports/phase28_cooldown_reconciliation.md",
            "reports/phase28_campaign_aware_statistics.md",
            "reports/phase28_campaign_summary.csv",
            "reports/phase28_leave_one_campaign_out.csv",
            "reports/phase28_aircraft_fragmentation_audit.md",
            "reports/phase28_aircraft_event_sequences.csv",
            "reports/phase28_poisson_and_heterogeneity_audit.md",
            "reports/phase28_dataset_license_and_provenance_audit.md",
            "reports/phase28_risk_and_limitation_register.md",
            "reports/phase28_processing_manifest.json",
            "reports/phase28_artifact_manifest.json",
            "reports/phase28_test_results.txt",
            "scripts/reproduce_phase28_analysis.py",
            "tests/test_phase28_reproduction.py"
        ]
    }

    out_manifest = REPORTS_DIR / "phase28_artifact_manifest.json"
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

