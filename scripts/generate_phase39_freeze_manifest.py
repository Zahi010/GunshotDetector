import json
import hashlib
import pathlib
import datetime

REPO_ROOT = pathlib.Path("E:/gunshot/gunshot")
P39_DIR = REPO_ROOT / "experiments" / "phase39"
P39_DIR.mkdir(parents=True, exist_ok=True)

artifacts = {
    "model_phase14.py": {
        "path": REPO_ROOT / "model_phase14.py",
        "role": "DEFAULT_RESEARCH_BASELINE"
    },
    "model_phase17.py": {
        "path": REPO_ROOT / "model_phase17.py",
        "role": "SELECTABLE_EXPERIMENTAL_PROFILE_KNOWN_DEFECT"
    },
    "model_phase17_state_reset_candidate.py": {
        "path": REPO_ROOT / "experiments" / "phase31" / "model_phase17_state_reset_candidate.py",
        "role": "QUARANTINED_DIAGNOSTIC_REFERENCE"
    },
    "model_phase36.py": {
        "path": REPO_ROOT / "experiments" / "phase36" / "model_phase36.py",
        "role": "EXPERIMENTAL_RESEARCH_BRANCH_V1"
    },
    "feature_extractor.py": {
        "path": REPO_ROOT / "feature_extractor.py",
        "role": "FROZEN_FEATURE_EXTRACTION_PIPELINE"
    },
    "config.py": {
        "path": REPO_ROOT / "config.py",
        "role": "FROZEN_BASELINE_CONFIGURATION"
    },
    "event_state_machine.py": {
        "path": REPO_ROOT / "experiments" / "phase36" / "event_state_machine.py",
        "role": "EXPERIMENTAL_FINITE_STATE_MACHINE_LOGIC"
    },
    "acoustic_features.py": {
        "path": REPO_ROOT / "experiments" / "phase36" / "acoustic_features.py",
        "role": "EXPERIMENTAL_ACOUSTIC_SUPPRESSION_AND_DSP"
    },
    "config_phase36.json": {
        "path": REPO_ROOT / "experiments" / "phase36" / "config_phase36.json",
        "role": "EXPERIMENTAL_BRANCH_CONFIGURATION"
    }
}

manifest = {
    "phase": "PHASE_39",
    "mandatory_safety_designation": "RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY",
    "timestamp_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "audit_directive": "Freeze all historical detector artifacts without modification or retraining",
    "artifacts": {}
}

print("Computing actual on-disk SHA-256 hashes and file sizes:")
for name, meta in artifacts.items():
    file_path = meta["path"]
    if not file_path.exists():
        print(f"ERROR: File missing: {file_path}")
        continue
    raw_bytes = file_path.read_bytes()
    sha256 = hashlib.sha256(raw_bytes).hexdigest()
    size_bytes = len(raw_bytes)
    
    manifest["artifacts"][name] = {
        "relative_path": str(file_path.relative_to(REPO_ROOT)).replace("\\", "/"),
        "role": meta["role"],
        "size_bytes": size_bytes,
        "sha256": sha256
    }
    print(f"  {name:38s} | {size_bytes:6d} bytes | {sha256}")

out_manifest_path = P39_DIR / "phase39_detector_freeze_manifest.json"
with open(out_manifest_path, "w", encoding="utf-8") as f:
    json.dump(manifest, f, indent=2)

print(f"\nManifest successfully written to: {out_manifest_path}")

