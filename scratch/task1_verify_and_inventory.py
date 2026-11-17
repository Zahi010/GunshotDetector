import os
import hashlib
import json
from pathlib import Path
import pandas as pd

def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

files_to_hash = [
    # Detector V10
    "e:/gunshot/gunshot/experiments/detector_improvement_v10/model_detector_improvement_v10.py",
    "e:/gunshot/gunshot/experiments/detector_improvement_v10/config_improvement_v10.json",
    # Detector V8 / Base Features
    "e:/gunshot/gunshot/experiments/detector_improvement_v8/model_detector_improvement_v8.py",
    # Model Checkpoints & Bundles
    "e:/gunshot/gunshot/models/gunshot_yamnet_bundle/classifier_head.keras",
    "e:/gunshot/gunshot/models/gunshot_yamnet_bundle/yamnet.keras",
    "e:/gunshot/gunshot/models/gunshot_yamnet_bundle/catboost_model.cbm",
    "e:/gunshot/gunshot/models/gunshot_yamnet_bundle/lightgbm_model.txt",
    "e:/gunshot/gunshot/models/gunshot_yamnet_bundle/xgboost_model.json",
    "e:/gunshot/gunshot/models/gunshot_yamnet_bundle/mlp_model.keras",
    "e:/gunshot/gunshot/models/gunshot_yamnet_bundle/fusion_model.joblib",
    # App code
    "e:/gunshot/gunshot/app.py",
    # Phase 54 files
    "e:/gunshot/gunshot/experiments/phase54_final_validation/phase54_evaluation_manifest.csv",
    "e:/gunshot/gunshot/experiments/phase54_final_validation/recording_level_predictions.csv",
    "e:/gunshot/gunshot/experiments/phase54_final_validation/source_level_metrics.csv",
    "e:/gunshot/gunshot/experiments/phase54_final_validation/statistical_metrics.csv",
    "e:/gunshot/gunshot/experiments/phase54_final_validation/continuous_stream_evaluation.csv",
    "e:/gunshot/gunshot/experiments/phase54_final_validation/physical_microphone_validation.json",
    "e:/gunshot/gunshot/experiments/phase54_final_validation/dataset_provenance.md",
    "e:/gunshot/gunshot/experiments/phase54_final_validation/duplicate_and_leakage_audit.md",
    "e:/gunshot/gunshot/experiments/phase54_final_validation/final_qualification_decision.md",
    "e:/gunshot/gunshot/experiments/phase54_final_validation/latency_and_dropped_window_report.md",
    "e:/gunshot/gunshot/experiments/phase54_final_validation/physical_microphone_validation.md",
    "e:/gunshot/gunshot/experiments/phase54_final_validation/statistical_evaluation.md"
]

manifest = {
    "safety_designation": "RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY",
    "phase": 55,
    "description": "Reproducibility manifest, baseline hashes, and Phase 54 integrity verification",
    "files": {}
}

for fp in files_to_hash:
    if os.path.exists(fp):
        h = sha256_file(fp)
        manifest["files"][fp] = {
            "sha256": h,
            "bytes": os.path.getsize(fp),
            "basename": os.path.basename(fp)
        }
    else:
        manifest["files"][fp] = "MISSING"

out_dir = Path("e:/gunshot/gunshot/experiments/phase55_failure_analysis")
out_dir.mkdir(parents=True, exist_ok=True)
manifest_path = out_dir / "reproducibility_manifest.json"

with open(manifest_path, "w") as f:
    json.dump(manifest, f, indent=2)

print(f"Reproducibility manifest written with {len(manifest['files'])} entries to {manifest_path}")

