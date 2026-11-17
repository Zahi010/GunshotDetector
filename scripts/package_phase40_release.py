import hashlib
import json
import pathlib
import zipfile

REPO_ROOT = pathlib.Path("E:/gunshot/gunshot")
ROOT = pathlib.Path("E:/gunshot")
P40_DIR = REPO_ROOT / "experiments" / "phase40"
ZIP_PATH = ROOT / "gunshot_detection_phase40_audit.zip"

files_to_package = [
    # Reports and CSVs
    REPO_ROOT / "experiments" / "phase40" / "phase40_phase38_phase39_metric_diff.csv",
    REPO_ROOT / "experiments" / "phase40" / "phase40_clip_level_decision_diff.csv",
    REPO_ROOT / "experiments" / "phase40" / "phase40_reproduction_findings.md",
    REPO_ROOT / "experiments" / "phase40" / "phase40_hash_history.csv",
    REPO_ROOT / "experiments" / "phase40" / "phase40_hash_reconciliation.md",
    REPO_ROOT / "experiments" / "phase40" / "phase40_source_lineage.csv",
    REPO_ROOT / "experiments" / "phase40" / "phase40_audio_similarity_audit.csv",
    REPO_ROOT / "experiments" / "phase40" / "phase40_source_independence_report.md",
    REPO_ROOT / "experiments" / "phase40" / "phase40_fireworks_pairwise_audit.csv",
    REPO_ROOT / "experiments" / "phase40" / "phase40_fireworks_statistical_report.md",
    REPO_ROOT / "experiments" / "phase40" / "phase40_evaluation_protocol.md",
    REPO_ROOT / "experiments" / "phase40" / "dataset" / "phase40_continuous_dataset_registry.csv",
    REPO_ROOT / "experiments" / "phase40" / "dataset" / "phase40_continuous_overlap_audit.csv",
    REPO_ROOT / "experiments" / "phase40" / "dataset" / "phase40_continuous_acquisition_report.md",
    REPO_ROOT / "experiments" / "phase40" / "phase40_continuous_results.csv",
    REPO_ROOT / "experiments" / "phase40" / "phase40_per_recording_results.csv",
    REPO_ROOT / "experiments" / "phase40" / "phase40_campaign_level_results.csv",
    REPO_ROOT / "experiments" / "phase40" / "phase40_statistical_analysis.md",
    REPO_ROOT / "experiments" / "phase40" / "phase40_condition_comparison.csv",
    REPO_ROOT / "experiments" / "phase40" / "phase40_test_execution_log.txt",
    REPO_ROOT / "experiments" / "phase40" / "phase40_final_audit_report.md",
    REPO_ROOT / "reports" / "phase40_final_audit_report.md",
    
    # Tests
    REPO_ROOT / "tests" / "test_phase40_audit.py",
    
    # Scripts
    REPO_ROOT / "scripts" / "run_phase40_reproduction_audit.py",
    REPO_ROOT / "scripts" / "run_phase40_hash_reconciliation.py",
    REPO_ROOT / "scripts" / "run_phase40_source_audit.py",
    REPO_ROOT / "scripts" / "run_phase40_fireworks_statistical_audit.py",
    REPO_ROOT / "scripts" / "acquire_phase40_continuous_streams.py",
    REPO_ROOT / "scripts" / "run_phase40_continuous_audit_and_eval.py",
    REPO_ROOT / "scripts" / "execute_phase40_continuous_pipeline.py",
    REPO_ROOT / "scripts" / "run_phase40_statistical_analysis.py"
]

print(f"Packaging {len(files_to_package)} files into {ZIP_PATH}...")

with zipfile.ZipFile(ZIP_PATH, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as z:
    for f in files_to_package:
        assert f.exists(), f"File missing: {f}"
        arcname = "gunshot/" + f.relative_to(REPO_ROOT).as_posix()
        z.write(f, arcname)
        print(f"  + Added {arcname} ({f.stat().st_size} bytes)")

# Test ZIP CRC
with zipfile.ZipFile(ZIP_PATH, "r") as z:
    crc_bad = z.testzip()
    namelist = z.namelist()
    assert crc_bad is None, f"ZIP CRC error on {crc_bad}"

zip_bytes = ZIP_PATH.read_bytes()
zip_sha = hashlib.sha256(zip_bytes).hexdigest()
zip_size = len(zip_bytes)

print(f"\nPackage complete:")
print(f"  Archive: {ZIP_PATH.name}")
print(f"  Size: {zip_size:,} bytes")
print(f"  SHA-256: {zip_sha}")
print(f"  Files: {len(namelist)}")
print(f"  CRC Status: PASS (testzip() is None)")

# Write manifest of all Phase 40 deliverables
manifest = {
    "phase": "PHASE_40",
    "phase_title": "Cross-Phase Reproducibility, Source-Cluster Audit & Continuous Exposure Expansion",
    "release_archive": {
        "filename": ZIP_PATH.name,
        "byte_size": zip_size,
        "sha256": zip_sha,
        "internal_file_count": len(namelist),
        "crc_status": "PASS"
    },
    "deliverables": {}
}

for f in files_to_package:
    rel = f.relative_to(REPO_ROOT).as_posix()
    data = f.read_bytes()
    manifest["deliverables"][rel] = {
        "byte_size": len(data),
        "sha256": hashlib.sha256(data).hexdigest()
    }

manifest_path = P40_DIR / "phase40_output_hash_manifest.json"
manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
print(f"Saved manifest: {manifest_path}")

