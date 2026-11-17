"""
Phase 19 Versioned Archive Packager
MANDATORY SAFETY DESIGNATION:
RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.

Packages all Phase 19 code, frozen models, reports, test suites, and independent data into:
E:/gunshot/gunshot_detection_phase19.zip
Validates integrity using zipfile.testzip() and outputs reports/phase19_artifact_manifest.json.
"""

import os
import sys
import json
import zipfile
import hashlib
from pathlib import Path

ROOT = Path("E:/gunshot/gunshot")
ZIP_OUT = Path("E:/gunshot/gunshot_detection_phase19.zip")
REPORTS_DIR = ROOT / "reports"

def sha256_of_file(filepath: Path) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

print("=== Packaging Phase 19 Archive ===")

# Items to include
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
    
    # Scripts
    "scripts/freeze_phase19_baseline.py",
    "scripts/ingest_phase19_data.py",
    "scripts/generate_phase19_lineage_matrix.py",
    "scripts/run_phase19_independent_evaluation.py",
    "scripts/reproduce_phase19_independent_evaluation.py",
    "scripts/package_phase19_archive.py",
    
    # Tests
    "tests/test_phase19_independent_evaluation.py",
    
    # Phase 19 Reports
    "reports/phase19_baseline_freeze.json",
    "reports/phase19_source_registry.csv",
    "reports/phase19_positive_recording_manifest.csv",
    "reports/phase19_event_annotation_manifest.csv",
    "reports/phase19_source_lineage_matrix.csv",
    "reports/phase19_acquisition_audit.md",
    "reports/phase19_evaluation_protocol.md",
    "reports/phase19_independent_event_results.csv",
    "reports/phase19_independent_session_results.csv",
    "reports/phase19_category_comparison.csv",
    "reports/phase19_negative_comparison.json",
    "reports/phase19_evaluation_summary.json",
    "reports/phase19_statistical_analysis.md",
    "reports/phase19_final_report.md",
    "reports/phase19_test_results.txt",
    
    # Phase 19 Data
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
                    arcname = f"gunshot/{p.relative_to(ROOT)}"
                    zf.write(p, arcname)
        elif target.is_file():
            arcname = f"gunshot/{pat}"
            zf.write(target, arcname)
        elif target.is_dir():
            for root, _, files in os.walk(target):
                for f in files:
                    fp = Path(root) / f
                    arcname = f"gunshot/{fp.relative_to(ROOT)}"
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
    "phase": "PHASE_19_SOURCE_INDEPENDENT_EVALUATION",
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
    }
}

with open(REPORTS_DIR / "phase19_artifact_manifest.json", "w") as f:
    json.dump(manifest, f, indent=2)
print("Saved reports/phase19_artifact_manifest.json")

