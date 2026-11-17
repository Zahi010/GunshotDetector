import hashlib
import json
import pathlib

REPO_ROOT = pathlib.Path("E:/gunshot/gunshot")
P41_DIR = REPO_ROOT / "experiments" / "phase41"

protected_files = [
    "model_phase14.py",
    "model_phase17.py",
    "experiments/phase31/model_phase17_state_reset_candidate.py",
    "experiments/phase36/model_phase36.py",
    "experiments/phase36/event_state_machine.py",
    "experiments/phase36/acoustic_features.py",
    "feature_extractor.py",
    "config.py",
    "experiments/phase38/phase38_detector_freeze_manifest.json",
    "experiments/phase39/phase39_detector_freeze_manifest.json",
    "experiments/phase40/phase40_output_hash_manifest.json",
    "experiments/phase40/phase40_evaluation_protocol.md"
]

manifest = {
    "audit_phase": "PHASE_41",
    "description": "Pre-audit protected file baseline hashes recorded before executing Phase 41 audit workflows.",
    "timestamp": "2026-11-16T13:51:00Z",
    "protected_files": {}
}

for rel_path in protected_files:
    full_path = REPO_ROOT / rel_path
    assert full_path.exists(), f"Protected file missing: {rel_path}"
    data = full_path.read_bytes()
    sha = hashlib.sha256(data).hexdigest()
    size = len(data)
    manifest["protected_files"][rel_path] = {
        "byte_size": size,
        "sha256": sha
    }
    print(f"Recorded: {rel_path} | {size} bytes | {sha}")

out_path = P41_DIR / "phase41_protected_file_hashes.json"
out_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
print(f"\nSaved {out_path} ({len(manifest['protected_files'])} files protected)")

