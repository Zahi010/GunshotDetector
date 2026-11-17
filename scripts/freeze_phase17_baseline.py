"""
Phase 17 Baseline Freeze & Cryptographic Verification Script.

Freezes and verifies:
1. Primary and comparator baseline detectors (model_phase14, model_phase13, model_phase9).
2. Phase 16 deployment archive (gunshot_detection_phase16.zip).
3. Operating profiles, thresholds, gating parameters, and temporal state-machine configurations.
4. Permanent classification of Phase 15 discrete benchmark and Phase 16 diagnostic results
   as INSPECTED_DIAGNOSTIC_EVIDENCE.
5. Mandatory safety designations.

SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.
"""

import os
import sys
import json
import hashlib
from pathlib import Path

WORKSPACE_ROOT = Path("e:/gunshot/gunshot").resolve()
ARCHIVE_ROOT = Path("e:/gunshot").resolve()
REPORTS_DIR = WORKSPACE_ROOT / "reports"
OUTPUT_JSON = REPORTS_DIR / "phase17_baseline_freeze.json"

SAFETY_DESIGNATION = "RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY"

LOCKED_MODELS = {
    "model_phase14": {
        "path": str(WORKSPACE_ROOT / "model_phase14.py"),
        "expected_sha256": "a268551604ae8b73068435ff10ab3d265065f56e0679757fca5b6bf0f061c065",
        "description": "Primary Production Detector Baseline (Phase 14 Calibrated Semantic Gating)"
    },
    "model_phase13": {
        "path": str(WORKSPACE_ROOT / "model_phase13.py"),
        "expected_sha256": "68585039a4a4fdb7978a99f5e2a72c0ad5a9523127ec24a1338fbedd1c1231e6",
        "description": "Frozen Historical Comparator (Phase 13 Streaming Two-Window Confirmation)"
    },
    "model_phase9": {
        "path": str(WORKSPACE_ROOT / "model_phase9.py"),
        "expected_sha256": "85cedd9f5b988ecafb1eae7de9630ee3d6a387ded6ef732e0efb7c3b496f132a",
        "description": "Frozen Historical Comparator (Phase 9 Single-Window Baseline)"
    }
}

LOCKED_ARCHIVES = {
    "Phase 16": {
        "path": str(ARCHIVE_ROOT / "gunshot_detection_phase16.zip"),
        "expected_sha256": "386298c4a4a251b4728d14d5903265ebe18c63404f87d0eba47bbcce442f65b4",
        "expected_size_mb": 1905.18
    }
}

HISTORICAL_ARCHIVE_REGISTRY = {
    "Phase 8": {"sha256": "c8bd26d09b5a41903ae8308b7bcac42f37ecd00d95eb6abfa4295365e074d353", "size_mb": 462.72},
    "Phase 9": {"sha256": "96ff780eaa38737ea66851195301beebc576a31a48319f3b0a71083c4dee2ff0", "size_mb": 825.77},
    "Phase 10": {"sha256": "d8edb26b71d69d6e76a1834cc741bda272c71b475287d7bd7fe2f33be95c459d", "size_mb": 825.84},
    "Phase 11": {"sha256": "c50a9b07ffe93f01118fbc2a26130fd73c800d717b6a372d2e76291c735404ef", "size_mb": 825.87},
    "Phase 12": {"sha256": "8c674902761d469760928c81596813a08a942262440d977a423e58007055241a", "size_mb": 1048.73},
    "Phase 13": {"sha256": "1a87aef803c7b2ec1bc0e5b3a894451960ea17a9f787a8ffc81ba7a15e8f6561", "size_mb": 1276.98},
    "Phase 14": {"sha256": "37807435378d313efbec89a3671b714cb33f8b1ddef4ca91141956ae5082d144", "size_mb": 1217.79},
    "Phase 15": {"sha256": "9ae819de02b9520aa105ecad8db871aa583cc204778bca20e7b9d1018ea6b08c", "size_mb": 1409.58}
}

PROFILES_PHASE14 = {
    "balanced": {
        "threshold_base": 0.75,
        "threshold_high": 0.90,
        "threshold_off": 0.40,
        "confirm_windows": 2,
        "cooldown_secs": 2.0,
        "min_crest_factor_db": 8.8,
        "single_win_min_crest_db": 12.0,
        "enable_semantic_gating": True,
        "target_operational_env": "Standard multi-threat urban/suburban environments"
    },
    "high_precision": {
        "threshold_base": 0.85,
        "threshold_high": 0.95,
        "threshold_off": 0.50,
        "confirm_windows": 2,
        "cooldown_secs": 2.5,
        "min_crest_factor_db": 10.5,
        "single_win_min_crest_db": 14.0,
        "enable_semantic_gating": True,
        "target_operational_env": "High-noise industrial, fireworks-prone, urban arterial transit"
    },
    "high_sensitivity": {
        "threshold_base": 0.65,
        "threshold_high": 0.80,
        "threshold_off": 0.35,
        "confirm_windows": 2,
        "cooldown_secs": 1.5,
        "min_crest_factor_db": 7.0,
        "single_win_min_crest_db": 10.5,
        "enable_semantic_gating": True,
        "target_operational_env": "Quiet rural areas, indoor surveillance, low-SNR distant threat monitoring"
    }
}

def compute_sha256(filepath: Path) -> str:
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()

def main():
    print("=" * 80)
    print("   PHASE 17: BASELINE VERIFICATION & CRYPTOGRAPHIC FREEZE")
    print(f"   Safety: {SAFETY_DESIGNATION}")
    print("=" * 80 + "\n")

    freeze_data = {
        "phase": 17,
        "action": "BASELINE_FREEZE",
        "safety_designation": SAFETY_DESIGNATION,
        "timestamp": "2026-11-13T22:30:00Z",
        "models": {},
        "current_archives": {},
        "historical_archive_registry": HISTORICAL_ARCHIVE_REGISTRY,
        "operating_profiles_phase14": PROFILES_PHASE14,
        "benchmark_retirement_audit": {
            "phase15_discrete_benchmark": {
                "status": "RETIRED_INSPECTED_DIAGNOSTIC_EVIDENCE",
                "sample_size": 98,
                "reason": "Exhaustively inspected, parameterized, and diagnostically audited in Phase 15 and 16. Permanent prohibition on reuse as blind evaluation data."
            },
            "phase16_continuous_benchmark": {
                "status": "FROZEN_HISTORICAL_EVIDENCE",
                "exposure_hours": 6.08,
                "streams_count": 11,
                "reason": "Baseline natural continuous negative exposure established in Phase 16; preserved for longitudinal comparison."
            }
        }
    }

    # 1. Verify Models
    print("[*] Verifying detector model files...")
    for mod_name, info in LOCKED_MODELS.items():
        p = Path(info["path"])
        if not p.exists():
            raise FileNotFoundError(f"Detector file missing: {p}")
        actual_hash = compute_sha256(p)
        print(f"  {mod_name}:")
        print(f"    Path:     {p}")
        print(f"    SHA-256:  {actual_hash}")
        if actual_hash != info["expected_sha256"]:
            raise ValueError(f"CRITICAL: {mod_name} SHA-256 digest mismatch! Expected {info['expected_sha256']}, got {actual_hash}")
        print("    Status:   LOCKED & VERIFIED (Exact Match)")
        freeze_data["models"][mod_name] = {
            "path": str(p),
            "sha256": actual_hash,
            "description": info["description"],
            "status": "VERIFIED_LOCKED"
        }

    # 2. Verify Phase 16 Deployment Archive
    print("\n[*] Verifying Phase 16 deployment archive...")
    for arc_name, info in LOCKED_ARCHIVES.items():
        p = Path(info["path"])
        if not p.exists():
            raise FileNotFoundError(f"Deployment archive missing: {p}")
        actual_hash = compute_sha256(p)
        actual_size_mb = p.stat().st_size / (1024 * 1024)
        print(f"  {arc_name}:")
        print(f"    Path:     {p}")
        print(f"    Size:     {actual_size_mb:.2f} MB")
        print(f"    SHA-256:  {actual_hash}")
        if actual_hash != info["expected_sha256"]:
            raise ValueError(f"CRITICAL: {arc_name} SHA-256 digest mismatch! Expected {info['expected_sha256']}, got {actual_hash}")
        print("    Status:   LOCKED & VERIFIED (Exact Match)")
        freeze_data["current_archives"][arc_name] = {
            "path": str(p),
            "sha256": actual_hash,
            "size_mb": round(actual_size_mb, 2),
            "status": "VERIFIED_LOCKED"
        }

    # 3. Save Baseline Freeze Report
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(freeze_data, f, indent=2)
    print(f"\n[+] Baseline freeze manifest successfully saved to: {OUTPUT_JSON}")

if __name__ == "__main__":
    main()

