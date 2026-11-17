import zipfile
import hashlib
import pathlib
import json

ROOT = pathlib.Path("E:/gunshot")
REPO = ROOT / "gunshot"
P39 = REPO / "experiments" / "phase39"

archive_path = ROOT / "gunshot_detection_phase39_evaluation.zip"

# Collect files to package (no audio, no npz caches)
files_to_pack = [
    # Protocols and manifests
    P39 / "phase39_evaluation_protocol.md",
    P39 / "phase39_detector_freeze_manifest.json",
    
    # Provenance and reconciliation
    P39 / "phase39_hash_reconciliation.csv",
    P39 / "phase39_archive_reconciliation.csv",
    P39 / "phase39_provenance_findings.md",
    P39 / "provenance" / "phase39_hash_reconciliation.csv",
    P39 / "provenance" / "phase39_archive_reconciliation.csv",
    P39 / "provenance" / "phase39_provenance_findings.md",
    
    # Annotation audit and reproduction
    P39 / "phase39_positive_annotation_audit.csv",
    P39 / "phase39_positive_annotation_report.md",
    P39 / "phase39_phase38_reproduction.csv",
    P39 / "phase39_metric_reconciliation.md",
    
    # Dataset registries and overlap
    P39 / "phase39_continuous_dataset_registry.csv",
    P39 / "phase39_distractor_registry.csv",
    P39 / "phase39_audio_overlap_audit.csv",
    P39 / "phase39_continuous_acquisition_report.md",
    P39 / "dataset" / "phase39_continuous_dataset_registry.csv",
    P39 / "dataset" / "phase39_distractor_registry.csv",
    P39 / "dataset" / "phase39_audio_overlap_audit.csv",
    P39 / "dataset" / "phase39_continuous_acquisition_report.md",
    
    # Results and error analyses
    P39 / "phase39_continuous_results.csv",
    P39 / "phase39_distractor_results.csv",
    P39 / "phase39_positive_results.csv",
    P39 / "phase39_condition_comparison.csv",
    P39 / "phase39_fireworks_error_analysis.md",
    P39 / "phase39_suppression_reproducibility.md",
    
    # Reports and test suite
    P39 / "phase39_final_report.md",
    P39 / "phase39_test_execution_log.txt",
    REPO / "tests" / "test_phase39_evaluation.py",
    P39 / "tests" / "test_phase39_evaluation.py"
]

print(f"Packaging {len(files_to_pack)} deliverables into {archive_path.name}...")

with zipfile.ZipFile(archive_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
    for f in files_to_pack:
        if f.exists():
            arcname = str(f.relative_to(REPO)).replace("\\", "/")
            zf.write(f, arcname=arcname)
            print(f"  Added: {arcname}")
        else:
            print(f"  WARNING: File missing: {f}")

# Verify archive
with zipfile.ZipFile(archive_path, "r") as zf:
    bad_file = zf.testzip()
    file_count = len(zf.namelist())
    crc_status = "PASS" if bad_file is None else f"FAIL_{bad_file}"

raw_bytes = archive_path.read_bytes()
archive_size = len(raw_bytes)
archive_sha = hashlib.sha256(raw_bytes).hexdigest()

print("\n" + "=" * 60)
print("RELEASE ARCHIVE VERIFICATION")
print("=" * 60)
print(f"Archive Filename: {archive_path.name}")
print(f"Archive File Path: {archive_path}")
print(f"File Count: {file_count}")
print(f"Byte Size: {archive_size} bytes")
print(f"SHA-256 Hash: {archive_sha}")
print(f"ZIP CRC Status: {crc_status}")

# Generate phase39_output_hash_manifest.json
output_manifest = {
    "phase": "PHASE_39",
    "mandatory_safety_designation": "RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY",
    "release_archive": {
        "filename": archive_path.name,
        "byte_size": archive_size,
        "sha256": archive_sha,
        "zip_crc_status": crc_status,
        "file_count": file_count
    },
    "artifacts": {}
}

for f in files_to_pack:
    if f.exists():
        rel_p = str(f.relative_to(REPO)).replace("\\", "/")
        b = f.read_bytes()
        output_manifest["artifacts"][rel_p] = {
            "size_bytes": len(b),
            "sha256": hashlib.sha256(b).hexdigest()
        }

out_manifest_path = P39 / "phase39_output_hash_manifest.json"
with open(out_manifest_path, "w", encoding="utf-8") as f:
    json.dump(output_manifest, f, indent=2)

print(f"\nSaved output hash manifest to: {out_manifest_path}")

