"""
Phase 16 Baseline Freeze Script.

Cryptographically locks the candidate and baseline models:
1. model_phase14.py (candidate)
2. model_phase13.py (frozen comparator)
3. model_phase9.py (frozen comparator)
4. Historical archives: Phases 8-15
5. Full configuration parameters across all profiles
6. Saves reports/phase16_baseline_freeze.json

SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.
"""

import os
import sys
import json
import hashlib
from pathlib import Path

ROOT = Path("e:/gunshot/gunshot")
sys.path.insert(0, str(ROOT))

import config
from model_phase14 import Phase14CandidateGunshotDetector
from model_phase13 import Phase13CandidateGunshotDetector
from model_phase9 import Phase9AdaptiveGunshotDetector

def compute_sha256(path: Path) -> str:
    hasher = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()

def main():
    print("================================================================================")
    print("   PHASE 16: BASELINE FREEZE & CRYPTOGRAPHIC VERIFICATION                      ")
    print("   Safety Designation: RESEARCH DEMONSTRATION PROTOTYPE - NOT FOR LIFE SAFETY   ")
    print("================================================================================\n")

    # 1. Historical Archives
    archive_paths = {
        "Phase 8": Path("e:/gunshot/gunshot_detection_phase8.zip"),
        "Phase 9": Path("e:/gunshot/gunshot_detection_phase9.zip"),
        "Phase 10": Path("e:/gunshot/gunshot_detection_phase10.zip"),
        "Phase 11": Path("e:/gunshot/gunshot_detection_phase11.zip"),
        "Phase 12": Path("e:/gunshot/gunshot_detection_phase12.zip"),
        "Phase 13": Path("e:/gunshot/gunshot_detection_phase13.zip"),
        "Phase 14": Path("e:/gunshot/gunshot_detection_phase14.zip"),
        "Phase 15": Path("e:/gunshot/gunshot_detection_phase15.zip")
    }

    archive_records = {}
    for name, p in archive_paths.items():
        if not p.exists():
            raise FileNotFoundError(f"Missing archive: {p}")
        sha = compute_sha256(p)
        size_mb = p.stat().st_size / (1024 * 1024)
        archive_records[name] = {
            "path": str(p),
            "sha256": sha,
            "size_mb": round(size_mb, 2)
        }
        print(f"[*] {name:10s} | SHA: {sha[:16]}... | Size: {size_mb:8.2f} MB")

    # 2. Frozen Models
    model_paths = {
        "model_phase14": ROOT / "model_phase14.py",
        "model_phase13": ROOT / "model_phase13.py",
        "model_phase9": ROOT / "model_phase9.py"
    }

    model_records = {}
    for name, p in model_paths.items():
        if not p.exists():
            raise FileNotFoundError(f"Missing model file: {p}")
        sha = compute_sha256(p)
        model_records[name] = {
            "path": str(p),
            "sha256": sha
        }
        print(f"[+] {name:15s} | SHA-256: {sha}")

    # 3. Parameters across profiles
    p14_profiles = Phase14CandidateGunshotDetector.PROFILES
    p13_profiles = Phase13CandidateGunshotDetector.PROFILES
    p9_profiles = Phase9AdaptiveGunshotDetector.PROFILES

    freeze_data = {
        "phase": 16,
        "action": "BASELINE_FREEZE",
        "safety_designation": "RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY",
        "historical_archives": archive_records,
        "models": model_records,
        "phase14_profiles": p14_profiles,
        "phase13_profiles": p13_profiles,
        "phase9_profiles": p9_profiles,
        "dsp_configuration": {
            "sample_rate": config.SAMPLE_RATE,
            "window_samples": config.WINDOW_SAMPLES,
            "hop_samples": config.HOP_SAMPLES,
            "window_duration_sec": config.WINDOW_LENGTH_SECS,
            "hop_duration_sec": config.HOP_LENGTH_SECS
        },
        "diagnostic_status": {
            "phase12_final_test": "PERMANENTLY_DIAGNOSTIC_ONLY",
            "phase15_blind_evaluation": "INSPECTED_DIAGNOSTIC_EVIDENCE_NOT_UNTOUCHED"
        }
    }

    out_json = ROOT / "reports" / "phase16_baseline_freeze.json"
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(freeze_data, f, indent=2)

    print(f"\n[+] Saved baseline freeze manifest: {out_json}")

if __name__ == "__main__":
    main()
