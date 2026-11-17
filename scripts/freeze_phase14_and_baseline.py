"""
Phase 15 Freeze Verification Script.

Cryptographically freezes Phase 14 candidate, verifies historical archives (Phases 8-14),
records configuration values, thresholds, DSP parameters, and outputs reports/phase15_baseline_freeze.json.

SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.
"""

import os
import sys
import json
import hashlib
from pathlib import Path

# Workspace paths
WORKSPACE_ROOT = Path("e:/gunshot/gunshot")
PROJECT_ROOT = Path("e:/gunshot")

def compute_sha256(filepath: Path) -> str:
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()

def verify_and_freeze():
    print("=== PHASE 15 BASELINE VERIFICATION & FREEZE ===")

    # 1. Historical archives to verify
    archives = {
        "phase8": PROJECT_ROOT / "gunshot_detection_phase8.zip",
        "phase9": PROJECT_ROOT / "gunshot_detection_phase9.zip",
        "phase10": PROJECT_ROOT / "gunshot_detection_phase10.zip",
        "phase11": PROJECT_ROOT / "gunshot_detection_phase11.zip",
        "phase12": PROJECT_ROOT / "gunshot_detection_phase12.zip",
        "phase13": PROJECT_ROOT / "gunshot_detection_phase13.zip",
        "phase14": PROJECT_ROOT / "gunshot_detection_phase14.zip",
    }

    archive_hashes = {}
    for name, path in archives.items():
        if not path.exists():
            raise FileNotFoundError(f"Archive missing: {path}")
        h = compute_sha256(path)
        sz_mb = path.stat().st_size / (1024 * 1024)
        archive_hashes[name] = {
            "path": str(path),
            "sha256": h,
            "size_mb": round(sz_mb, 2)
        }
        print(f"Archive {name}: {h} ({sz_mb:.2f} MB)")

    # 2. Verify model_phase14.py
    model_p14_path = WORKSPACE_ROOT / "model_phase14.py"
    if not model_p14_path.exists():
        raise FileNotFoundError(f"Missing {model_p14_path}")
    model_p14_hash = compute_sha256(model_p14_path)
    print(f"model_phase14.py SHA-256: {model_p14_hash}")

    # Also verify model_phase9.py and model_phase13.py for frozen comparators
    model_p9_path = WORKSPACE_ROOT / "model_phase9.py"
    model_p9_hash = compute_sha256(model_p9_path) if model_p9_path.exists() else None
    model_p13_path = WORKSPACE_ROOT / "model_phase13.py"
    model_p13_hash = compute_sha256(model_p13_path) if model_p13_path.exists() else None

    # 3. Import Phase 14 profiles and config
    sys.path.insert(0, str(WORKSPACE_ROOT))
    import config
    from model_phase14 import Phase14CandidateGunshotDetector

    p14_profiles = Phase14CandidateGunshotDetector.PROFILES

    dsp_settings = {
        "sample_rate": config.SAMPLE_RATE,
        "window_duration_sec": config.WINDOW_LENGTH_SECS,
        "hop_duration_sec": config.HOP_LENGTH_SECS,
        "window_samples": config.WINDOW_SAMPLES,
        "hop_samples": config.HOP_SAMPLES,
        "embedding_dim": config.EMBEDDING_DIM,
        "n_classes": len(config.CLASS_NAMES),
        "class_names": config.CLASS_NAMES,
        "semantic_gating_classes": {
            "gunshot": [421, 422, 424, 425],
            "thunder": [280, 281],
            "fireworks": [426, 427],
            "canine": [69, 70, 75, 117],
            "fire_crackle": [292, 293],
            "siren": [317, 318, 319, 390, 391]
        }
    }

    freeze_data = {
        "phase": 15,
        "action": "BASELINE_FREEZE",
        "safety_designation": "RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY",
        "historical_archives": archive_hashes,
        "models": {
            "model_phase14": {
                "path": str(model_p14_path),
                "sha256": model_p14_hash
            },
            "model_phase13": {
                "path": str(model_p13_path),
                "sha256": model_p13_hash
            },
            "model_phase9": {
                "path": str(model_p9_path),
                "sha256": model_p9_hash
            }
        },
        "phase14_profiles": p14_profiles,
        "dsp_settings": dsp_settings,
        "event_aggregation_protocol": {
            "state_machine": "merge_phase14_events",
            "decay_requirement": "Threshold off reset before re-triggering within cluster",
            "guarded_immediate_dispatch": "crest_factor_db >= single_win_min_crest_db AND score >= threshold_high",
            "consensus_dispatch": "active_cluster length >= confirm_windows (2 windows)",
            "short_isolated_clip_rule": "duration <= 1.05s AND single window AND crest_factor >= min_crest_factor_db",
            "cooldown_refractory": "cooldown_secs post event end"
        }
    }

    reports_dir = WORKSPACE_ROOT / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    out_file = reports_dir / "phase15_baseline_freeze.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(freeze_data, f, indent=2)

    print(f"Successfully saved frozen baseline manifest to {out_file}")

if __name__ == "__main__":
    verify_and_freeze()
