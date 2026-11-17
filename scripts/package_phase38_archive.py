import hashlib
import json
import pathlib
import zipfile

repo = pathlib.Path('E:/gunshot/gunshot')
root = pathlib.Path('E:/gunshot')
p38_dir = repo / 'experiments/phase38'

artifacts_to_package = [
    # Protocol & Freeze Manifests
    ('experiments/phase38/phase38_evaluation_protocol.md', p38_dir / 'phase38_evaluation_protocol.md'),
    ('experiments/phase38/phase38_detector_freeze_manifest.json', p38_dir / 'phase38_detector_freeze_manifest.json'),
    ('experiments/phase38/phase38_baseline_test_log.txt', p38_dir / 'phase38_baseline_test_log.txt'),
    
    # Dataset Registry & Lineage Audits
    ('experiments/phase38/dataset/phase38_dataset_registry.csv', p38_dir / 'dataset/phase38_dataset_registry.csv'),
    ('experiments/phase38/dataset/phase38_dataset_license_register.csv', p38_dir / 'dataset/phase38_dataset_license_register.csv'),
    ('experiments/phase38/dataset/phase38_historical_overlap_audit.csv', p38_dir / 'dataset/phase38_historical_overlap_audit.csv'),
    ('experiments/phase38/dataset/phase38_dataset_acquisition_report.md', p38_dir / 'dataset/phase38_dataset_acquisition_report.md'),
    ('experiments/phase38/dataset/phase38_positive_catalog.csv', p38_dir / 'dataset/phase38_positive_catalog.csv'),
    ('experiments/phase38/dataset/phase38_distractor_catalog.csv', p38_dir / 'dataset/phase38_distractor_catalog.csv'),
    
    # Provenance & Archive Reconciliation
    ('experiments/phase38/provenance/phase38_frozen_asset_hash_reconciliation.csv', p38_dir / 'provenance/phase38_frozen_asset_hash_reconciliation.csv'),
    ('experiments/phase38/provenance/phase38_frozen_asset_provenance.md', p38_dir / 'provenance/phase38_frozen_asset_provenance.md'),
    ('experiments/phase38/provenance/phase38_archive_history_reconciliation.md', p38_dir / 'provenance/phase38_archive_history_reconciliation.md'),
    
    # Prospective Evaluation Result CSVs & Statistical Analysis
    ('experiments/phase38/phase38_background_results.csv', p38_dir / 'phase38_background_results.csv'),
    ('experiments/phase38/phase38_positive_event_results.csv', p38_dir / 'phase38_positive_event_results.csv'),
    ('experiments/phase38/phase38_distractor_results.csv', p38_dir / 'phase38_distractor_results.csv'),
    ('experiments/phase38/phase38_condition_comparison.csv', p38_dir / 'phase38_condition_comparison.csv'),
    ('experiments/phase38/phase38_statistical_analysis.md', p38_dir / 'phase38_statistical_analysis.md'),
    
    # Test Suite & Logs
    ('tests/test_phase38_prospective.py', repo / 'tests/test_phase38_prospective.py'),
    ('experiments/phase38/tests/test_phase38_prospective.py', p38_dir / 'tests/test_phase38_prospective.py'),
    ('experiments/phase38/phase38_test_execution_log.txt', p38_dir / 'phase38_test_execution_log.txt'),
    
    # Final Report
    ('experiments/phase38/phase38_final_evaluation_report.md', p38_dir / 'phase38_final_evaluation_report.md')
]

# Generate Output Hash Manifest
output_manifest = {}
for rel_zip, path in artifacts_to_package:
    assert path.exists(), f"File {path} missing!"
    data = path.read_bytes()
    sha = hashlib.sha256(data).hexdigest()
    output_manifest[rel_zip] = {
        'size_bytes': len(data),
        'sha256': sha
    }

manifest_path = p38_dir / 'phase38_output_hash_manifest.json'
manifest_path.write_text(json.dumps(output_manifest, indent=2), encoding='utf-8')
print(f"Saved output hash manifest to {manifest_path} ({len(output_manifest)} files)")

# Add manifest itself to package
artifacts_to_package.append(('experiments/phase38/phase38_output_hash_manifest.json', manifest_path))

# Package Zip File
zip_path = root / 'gunshot_detection_phase38_prospective_evaluation.zip'
with zipfile.ZipFile(zip_path, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
    for rel_zip, path in artifacts_to_package:
        zf.write(path, arcname=f"gunshot/{rel_zip}")

print(f"\nCreated archive: {zip_path}")
zip_data = zip_path.read_bytes()
zip_sha = hashlib.sha256(zip_data).hexdigest()
zip_size = len(zip_data)

# Test ZIP CRC
with zipfile.ZipFile(zip_path, 'r') as zf:
    corrupt = zf.testzip()
    assert corrupt is None, f"Corrupted file in zip: {corrupt}"

print(f"[ZIP CRC CHECK] PASS (0 corrupt files)")
print(f"Archive Size: {zip_size} bytes")
print(f"Archive SHA-256: {zip_sha}")

