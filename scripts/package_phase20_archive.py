"""
Phase 20 Versioned Archive Packager
MANDATORY SAFETY DESIGNATION:
RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.

Packages all Phase 20 code, frozen models, reports, test suites, and audited data into:
E:/gunshot/gunshot_detection_phase20.zip
Validates integrity using zipfile.testzip() and outputs reports/phase20_artifact_manifest.json.
"""

import os
import sys
import json
import zipfile
import hashlib
from pathlib import Path

ROOT = Path("E:/gunshot/gunshot")
ZIP_OUT = Path("E:/gunshot/gunshot_detection_phase20.zip")
REPORTS_DIR = ROOT / "reports"

def sha256_of_file(filepath: Path) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

print("=" * 75)
print("PACKAGING PHASE 20 RESEARCH ARCHIVE")
print("MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY")
print("=" * 75)

include_patterns = [
    # Core frozen models
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
    
    # Models bundle
    "models/gunshot_yamnet_bundle",
    
    # Phase 20 Scripts
    "scripts/freeze_phase20_baseline.py",
    "scripts/generate_phase20_dataset_inventory.py",
    "scripts/generate_phase20_continuity_audit.py",
    "scripts/build_phase20_canonical_manifest.py",
    "scripts/generate_phase20_geographic_lineage.py",
    "scripts/run_phase20_mcnemar_audit.py",
    "scripts/reproduce_phase20_pittsburgh_evaluation.py",
    "scripts/package_phase20_archive.py",
    
    # Phase 20 Tests
    "tests/test_phase20_pittsburgh_audit.py",
    
    # Phase 20 Reports
    "reports/phase20_baseline_freeze.json",
    "reports/phase20_original_dataset_inventory.csv",
    "reports/phase20_dataset_source_verification.md",
    "reports/phase20_license_attribution.md",
    "reports/phase20_continuity_audit.csv",
    "reports/phase20_recording_transformation_lineage.md",
    "reports/phase20_canonical_event_manifest.csv",
    "reports/phase20_event_accounting.json",
    "reports/phase20_event_accounting_audit.md",
    "reports/phase20_geographic_lineage.csv",
    "reports/phase20_session_independence_audit.md",
    "reports/phase20_paired_model_comparison.csv",
    "reports/phase20_mcnemar_audit.md",
    "reports/phase20_round_vs_incident_analysis.md",
    "reports/phase20_false_alert_exposure_audit.md",
    "reports/phase20_cross_category_interpretation.md",
    "reports/phase20_final_report.md",
    "reports/phase20_test_results.txt",
    
    # Positive Data
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
    "phase": "PHASE_20_PITTSBURGH_AUDIT",
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
    "frozen_historical_comparators": [
        {
            "model": "Phase 13 Balanced",
            "file": "model_phase13.py",
            "sha256": "68585039a4a4fdb7978a99f5e2a72c0ad5a9523127ec24a1338fbedd1c1231e6"
        },
        {
            "model": "Phase 9 Balanced",
            "file": "model_phase9.py",
            "sha256": "85cedd9f5b988ecafb1eae7de9630ee3d6a387ded6ef732e0efb7c3b496f132a"
        }
    ],
    "category_a_event_metrics": {
        "total_events": 50,
        "phase_14_balanced_detected": 27,
        "phase_14_balanced_recall": 0.54,
        "phase_17_experimental_detected": 33,
        "phase_17_experimental_recall": 0.66,
        "mcnemar_exact_p_value": 0.03125,
        "statistically_significant": True
    },
    "key_deliverables": [
        "reports/phase20_baseline_freeze.json",
        "reports/phase20_original_dataset_inventory.csv",
        "reports/phase20_dataset_source_verification.md",
        "reports/phase20_license_attribution.md",
        "reports/phase20_continuity_audit.csv",
        "reports/phase20_recording_transformation_lineage.md",
        "reports/phase20_canonical_event_manifest.csv",
        "reports/phase20_event_accounting.json",
        "reports/phase20_event_accounting_audit.md",
        "reports/phase20_geographic_lineage.csv",
        "reports/phase20_session_independence_audit.md",
        "reports/phase20_paired_model_comparison.csv",
        "reports/phase20_mcnemar_audit.md",
        "reports/phase20_round_vs_incident_analysis.md",
        "reports/phase20_false_alert_exposure_audit.md",
        "reports/phase20_cross_category_interpretation.md",
        "reports/phase20_final_report.md",
        "reports/phase20_test_results.txt",
        "tests/test_phase20_pittsburgh_audit.py",
        "scripts/reproduce_phase20_pittsburgh_evaluation.py"
    ]
}

out_manifest = REPORTS_DIR / "phase20_artifact_manifest.json"
with open(out_manifest, "w", encoding="utf-8") as f:
    json.dump(manifest, f, indent=2, ensure_ascii=False)
print(f"Saved artifact manifest to {out_manifest}")

