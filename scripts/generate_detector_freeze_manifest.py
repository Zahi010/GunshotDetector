import hashlib
import json
import pathlib
import subprocess
import sys

repo = pathlib.Path('E:/gunshot/gunshot')
root = pathlib.Path('E:/gunshot')
out_dir = repo / 'experiments/phase38'
out_dir.mkdir(parents=True, exist_ok=True)

# 1. Run Phase 36 tests and preserve log
test_cmd = [sys.executable, '-m', 'pytest', 'experiments/phase36/tests/test_phase36_unit.py', '-v']
res = subprocess.run(test_cmd, cwd=str(repo), capture_output=True, text=True)
test_log_path = out_dir / 'phase38_baseline_test_log.txt'
test_log_path.write_text(res.stdout + ("\n" + res.stderr if res.stderr else ""), encoding='utf-8')
print(f"Preserved Phase 36 baseline test log to {test_log_path} (Exit code: {res.returncode})")

# 2. Frozen components to record
frozen_components = {
    'model_phase14.py': {
        'path': 'gunshot/model_phase14.py',
        'role': 'DEFAULT_RESEARCH_BASELINE',
        'expected_sha256': 'a268551604ae8b73068435ff10ab3d265065f56e0679757fca5b6bf0f061c065'
    },
    'model_phase17.py': {
        'path': 'gunshot/model_phase17.py',
        'role': 'SELECTABLE_EXPERIMENTAL_PROFILE_KNOWN_DEFECT',
        'expected_sha256': 'e2b262b866fdd5d7f1a4ab91a7b8b9bac189ee8cc7a78603b3544ca1579fb819'
    },
    'model_phase17_state_reset_candidate.py': {
        'path': 'gunshot/experiments/phase31/model_phase17_state_reset_candidate.py',
        'role': 'QUARANTINED_DIAGNOSTIC_REFERENCE',
        'expected_sha256': 'c144b917b56532787e2a9198f2cad4a77dc2095b57962f31d11d250a4d5d9ea5'
    },
    'feature_extractor.py': {
        'path': 'gunshot/feature_extractor.py',
        'role': 'FROZEN_FEATURE_EXTRACTION_PIPELINE',
        'expected_sha256': '1c665b7c1749de98337da0726627710fffe0dcfa56335291b666ae7abcbae94f'
    },
    'config.py': {
        'path': 'gunshot/config.py',
        'role': 'FROZEN_BASELINE_CONFIGURATION',
        'expected_sha256': '55749f9d46d561d131fad374064021b73c08274e2a79954efd08570b029b1858'
    },
    'model_phase36.py': {
        'path': 'gunshot/experiments/phase36/model_phase36.py',
        'role': 'EXPERIMENTAL_EVENT_STATE_BRANCH_V1',
        'expected_sha256': '2774ab4cae0fca6d2f3646b443694fefa40d6837ff195f1d216ae7ff7732563a'
    },
    'event_state_machine.py': {
        'path': 'gunshot/experiments/phase36/event_state_machine.py',
        'role': 'EXPERIMENTAL_FINITE_STATE_MACHINE_LOGIC',
        'expected_sha256': 'a91e9bc6d0ab9ca805817a406857d31e1f482f7d8815b0eaf7fee9075cd23c31'
    },
    'acoustic_features.py': {
        'path': 'gunshot/experiments/phase36/acoustic_features.py',
        'role': 'EXPERIMENTAL_ACOUSTIC_SUPPRESSION_AND_DSP',
        'expected_sha256': '5cc775f97b8e9f2c62018efe6f3fc6d64913cfcb5ffd470a1daba625c6510a51'
    },
    'config_phase36.json': {
        'path': 'gunshot/experiments/phase36/config_phase36.json',
        'role': 'EXPERIMENTAL_BRANCH_CONFIGURATION',
        'expected_sha256': '1aaffd5423e116958807372855d989e294d3ff12b614052e10df78346d62e363'
    }
}

manifest = {
    'protocol_name': 'PHASE_38_PROSPECTIVE_HOLDOUT_EVALUATION',
    'safety_designation': 'RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY',
    'timestamp_iso': '2026-11-15T21:55:00Z',
    'preprocessing_parameters': {
        'sample_rate_hz': 16000,
        'window_length_samples': 15360, # 0.96s
        'hop_length_samples': 7680,     # 0.48s
        'n_mels': 64,
        'fmin_hz': 125,
        'fmax_hz': 7500,
        'embedding_dim': 1024,
        'embedding_source': 'yamnet_tf2'
    },
    'conditions': {
        'COND1': {'name': 'Phase 14 Balanced Baseline', 'model': 'model_phase14.py'},
        'COND2': {'name': 'Phase 17 Experimental Profile (Known State Defect)', 'model': 'model_phase17.py'},
        'COND3': {'name': 'Phase 17 State Reset Candidate', 'model': 'model_phase17_state_reset_candidate.py'},
        'COND4': {'name': 'Phase 36 Raw State Machine', 'model': 'model_phase36.py', 'suppression': 'NONE'},
        'COND5': {'name': 'Phase 36 Legacy Suppression', 'model': 'model_phase36.py', 'suppression': 'LEGACY_ANIMAL'},
        'COND6': {'name': 'Phase 36 Conservative Suppression', 'model': 'model_phase36.py', 'suppression': 'CONSERVATIVE_WITH_AVIATION_PROTECTION'}
    },
    'frozen_artifacts': {}
}

all_matched = True
for name, cinfo in frozen_components.items():
    p = root / cinfo['path']
    if not p.exists():
        print(f"ERROR: {p} does not exist!")
        all_matched = False
        continue
    data = p.read_bytes()
    sha = hashlib.sha256(data).hexdigest()
    matched = (sha == cinfo['expected_sha256'])
    if not matched:
        print(f"MISMATCH in {name}: got {sha}, expected {cinfo['expected_sha256']}")
        all_matched = False
    manifest['frozen_artifacts'][name] = {
        'relative_path': cinfo['path'],
        'role': cinfo['role'],
        'size_bytes': len(data),
        'sha256': sha,
        'matches_freeze_baseline': matched
    }

out_manifest_path = out_dir / 'phase38_detector_freeze_manifest.json'
out_manifest_path.write_text(json.dumps(manifest, indent=2), encoding='utf-8')
print(f"Saved detector freeze manifest to {out_manifest_path} (All baseline hashes matched: {all_matched})")

