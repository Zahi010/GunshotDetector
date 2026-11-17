"""
Phase 21 Versioned Archive Packager
MANDATORY SAFETY DESIGNATION:
RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.

Packages all Phase 21 code, models, cluster-aware reports, test suites, and data into:
E:/gunshot/gunshot_detection_phase21.zip
Validates CRC integrity with zipfile.testzip() and outputs reports/phase21_artifact_manifest.json.
"""

import os
import sys
import json
import zipfile
import hashlib
from pathlib import Path

ROOT = Path("E:/gunshot/gunshot")
ZIP_OUT = Path("E:/gunshot/gunshot_detection_phase21.zip")
REPORTS_DIR = ROOT / "reports"

def sha256_of_file(filepath: Path) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

print("=" * 80)
print("PACKAGING PHASE 21 RESEARCH ARCHIVE")
print("MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY")
print("=" * 80)

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
    
    # Phase 21 Scripts
    "scripts/freeze_phase21_baseline.py",
    "scripts/reproduce_phase21_event_level.py",
    "scripts/build_phase21_event_cluster_hierarchy.py",
    "scripts/build_phase21_recording_level.py",
    "scripts/build_phase21_position_level.py",
    "scripts/build_phase21_burst_analysis.py",
    "scripts/run_phase21_clustered_statistics.py",
    "scripts/build_phase21_false_alert_exposure.py",
    "scripts/build_phase21_category_d_reconciliation.py",
    "scripts/build_phase21_all_model_comparisons.py",
    "scripts/reproduce_phase21_cluster_aware_analysis.py",
    "scripts/package_phase21_archive.py",
    
    # Phase 21 Tests
    "tests/test_phase21_cluster_aware_audit.py",
    
    # Phase 21 Reports
    "reports/phase21_baseline_freeze.json",
    "reports/phase21_event_cluster_hierarchy.csv",
    "reports/phase21_event_level_reproduction.csv",
    "reports/phase21_event_contingency.json",
    "reports/phase21_event_level_statistics.md",
    "reports/phase21_recording_level_results.csv",
    "reports/phase21_recording_level_comparison.md",
    "reports/phase21_position_level_results.csv",
    "reports/phase21_burst_analysis.csv",
    "reports/phase21_clustered_statistics.md",
    "reports/phase21_cluster_bootstrap_results.json",
    "reports/phase21_leave_one_position_out.csv",
    "reports/phase21_negative_exposure_timeline.csv",
    "reports/phase21_false_alert_statistics.json",
    "reports/phase21_false_alert_exposure_correction.md",
    "reports/phase21_category_d_reconciliation.md",
    "reports/phase21_category_d_corrected_metrics.json",
    "reports/phase21_all_model_comparisons.csv",
    "reports/phase21_final_report.md",
    "reports/phase21_test_results.txt",
    
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
    "phase": "PHASE_21_CLUSTER_AWARE_VALIDATION",
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
    "statistical_summary": {
        "unadjusted_event_mcnemar_p_value": 0.03125,
        "incident_level_mcnemar_p_value": 0.25000,
        "holm_adjusted_mcnemar_p_value": 0.12500,
        "lopo_exclude_fp4_p_value": 0.25000,
        "category_a_quiescent_background_seconds": 140.416,
        "garwood_95_upper_bound_alerts_per_hour": 77.033,
        "category_d_phase_14_balanced_recall": 0.8333
    },
    "key_deliverables": [
        "reports/phase21_final_report.md",
        "reports/phase21_baseline_freeze.json",
        "reports/phase21_event_cluster_hierarchy.csv",
        "reports/phase21_event_level_reproduction.csv",
        "reports/phase21_event_contingency.json",
        "reports/phase21_event_level_statistics.md",
        "reports/phase21_recording_level_results.csv",
        "reports/phase21_recording_level_comparison.md",
        "reports/phase21_position_level_results.csv",
        "reports/phase21_burst_analysis.csv",
        "reports/phase21_clustered_statistics.md",
        "reports/phase21_cluster_bootstrap_results.json",
        "reports/phase21_leave_one_position_out.csv",
        "reports/phase21_negative_exposure_timeline.csv",
        "reports/phase21_false_alert_statistics.json",
        "reports/phase21_false_alert_exposure_correction.md",
        "reports/phase21_category_d_reconciliation.md",
        "reports/phase21_category_d_corrected_metrics.json",
        "reports/phase21_all_model_comparisons.csv",
        "reports/phase21_test_results.txt",
        "tests/test_phase21_cluster_aware_audit.py",
        "scripts/reproduce_phase21_cluster_aware_analysis.py"
    ]
}

out_manifest = REPORTS_DIR / "phase21_artifact_manifest.json"
with open(out_manifest, "w", encoding="utf-8") as f:
    json.dump(manifest, f, indent=2, ensure_ascii=False)
print(f"Saved artifact manifest to: {out_manifest}")

