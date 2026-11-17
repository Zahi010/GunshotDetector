"""
Project Reorganization and Audio Dataset Consolidation Script.

Consolidates all audio files into a clean, logical, and self-contained directory hierarchy:
├── data/
│   ├── README.md
│   ├── raw/
│   │   ├── gunshots/
│   │   ├── background/
│   │   └── synthetic/
│   ├── processed/
│   │   ├── train/
│   │   │   ├── gunshots/
│   │   │   └── background/
│   │   ├── validation/
│   │   │   ├── gunshots/
│   │   │   └── background/
│   │   └── test/
│   │       ├── gunshots/
│   │       └── background/
│   ├── hard_negatives/
│   │   ├── pending_review/
│   │   ├── approved/
│   │   └── rejected/
│   └── manifests/
│       ├── train.csv
│       ├── validation.csv
│       ├── test.csv
│       ├── migration_log.json
│       └── dataset_inventory.json
├── models/
├── scripts/
├── reports/
├── tests/
├── configs/
├── requirements.txt
└── README.md
"""
import os
import csv
import json
import shutil
import hashlib
from pathlib import Path
from typing import Dict, List, Any

import soundfile as sf
import librosa
import numpy as np

import config
from inventory import get_base_stem, AUDIO_EXTENSIONS
from dataset import compute_file_hash, GunshotDataset
from audit_dataset import audit_classify_file


def run_reorganization(project_root: Path = config.BASE_DIR):
    project_root = Path(project_root)
    print(f"\n=======================================================")
    print(f"   PROJECT & DATASET REORGANIZATION: {project_root}")
    print(f"=======================================================\n")

    # 1. Create target directory structure
    dirs_to_create = [
        project_root / "data" / "raw" / "gunshots",
        project_root / "data" / "raw" / "background",
        project_root / "data" / "raw" / "synthetic",
        project_root / "data" / "processed" / "train" / "gunshots",
        project_root / "data" / "processed" / "train" / "background",
        project_root / "data" / "processed" / "validation" / "gunshots",
        project_root / "data" / "processed" / "validation" / "background",
        project_root / "data" / "processed" / "test" / "gunshots",
        project_root / "data" / "processed" / "test" / "background",
        project_root / "data" / "hard_negatives" / "pending_review",
        project_root / "data" / "hard_negatives" / "approved",
        project_root / "data" / "hard_negatives" / "rejected",
        project_root / "data" / "manifests",
        project_root / "scripts",
        project_root / "reports",
        project_root / "tests",
        project_root / "configs"
    ]
    for d in dirs_to_create:
        d.mkdir(parents=True, exist_ok=True)

    # 2. Inventory all audio files in the project
    print("[1/6] Scanning and inventorying all audio files in workspace...")
    all_audio_files = []
    for ext in AUDIO_EXTENSIONS:
        all_audio_files.extend(list(project_root.glob(f"*{ext}")))
        all_audio_files.extend(list((project_root / "data").rglob(f"*{ext}")))

    # Deduplicate paths
    unique_paths = sorted(list(set(all_audio_files)))
    print(f"      Discovered {len(unique_paths)} audio file references across workspace.")

    # 3. Read dataset manifest to identify class, subcategory, and split assignments
    manifest_csv = project_root / "dataset_manifest.csv"
    manifest_info = {}
    if manifest_csv.exists():
        with open(manifest_csv, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                manifest_info[row["filename"]] = row

    # Also get the exact split assignments from GunshotDataset
    ds = GunshotDataset(data_dir=project_root / "data")
    ds.index_files()
    group_to_split = {}
    for sp in ["train", "val", "test"]:
        for g in ds.splits[sp]:
            group_to_split[g] = sp

    # 4. Migrate and consolidate raw audio files into data/raw/
    print("\n[2/6] Consolidating audio files into data/raw/...")
    migration_log = []
    moved_count = 0
    duplicate_count = 0
    seen_hashes = {}

    for fpath in unique_paths:
        # Skip files already in data/processed or data/hard_negatives/approved snippets
        if "data\\processed" in str(fpath) or "data/processed" in str(fpath):
            continue
        if "hard_negatives\\approved" in str(fpath) or "hard_negatives/approved" in str(fpath):
            continue
        if "hard_negatives\\pending_review" in str(fpath) or "hard_negatives/pending_review" in str(fpath):
            continue

        fname = fpath.name
        fhash = compute_file_hash(fpath)
        base_stem = get_base_stem(fname)

        # Determine category & class
        if fname in manifest_info:
            subcat = manifest_info[fname]["sound_subcategory"]
            cls_name = manifest_info[fname]["assigned_class"]
        else:
            subcat, cls_name, _ = audit_classify_file(fname)

        # Determine target raw directory
        if "synth" in fname.lower() or "synthetic" in str(fpath).lower():
            target_raw_dir = project_root / "data" / "raw" / "synthetic"
        elif cls_name == "gunshot":
            target_raw_dir = project_root / "data" / "raw" / "gunshots"
        else:
            target_raw_dir = project_root / "data" / "raw" / "background"

        target_file = target_raw_dir / fname

        # If file is in project root, move it to data/raw/
        is_in_root = (fpath.parent == project_root)
        action_taken = "already_in_place"

        if is_in_root:
            if not target_file.exists():
                shutil.move(str(fpath), str(target_file))
                action_taken = "moved_from_root_to_raw"
                moved_count += 1
            else:
                # Already present in data/raw, remove redundant root copy
                os.remove(fpath)
                action_taken = "consolidated_root_duplicate_to_raw"
                moved_count += 1
            current_fpath = target_file
        else:
            current_fpath = fpath

        # Check duplicate by hash
        is_hash_duplicate = fhash in seen_hashes
        if is_hash_duplicate:
            duplicate_count += 1
        seen_hashes[fhash] = fname

        migration_log.append({
            "filename": fname,
            "original_path": str(fpath.relative_to(project_root)),
            "consolidated_path": str(current_fpath.relative_to(project_root)),
            "md5_hash": fhash,
            "is_duplicate": is_hash_duplicate,
            "base_stem": base_stem,
            "class": cls_name,
            "subcategory": subcat,
            "action": action_taken
        })

    print(f"      Consolidated {moved_count} audio files into data/raw/.")
    print(f"      Identified {duplicate_count} bit-for-bit duplicate files.")

    # 5. Populate data/processed/ (standardized 16kHz mono copies per split)
    print("\n[3/6] Standardizing processed audio copies into train/val/test splits...")
    # Re-index files from data/raw
    raw_ds = GunshotDataset(data_dir=project_root / "data" / "raw")
    raw_ds.index_files()

    split_manifests = {"train": [], "val": [], "test": []}

    for sp in ["train", "val", "test"]:
        sp_name = "validation" if sp == "val" else sp
        for g_key in raw_ds.splits[sp]:
            g_info = raw_ds.groups[g_key]
            lbl = g_info["label"]
            cls_folder = "gunshots" if lbl == 1 else "background"
            target_processed_dir = project_root / "data" / "processed" / sp_name / cls_folder

            for raw_f in g_info["files"]:
                proc_target = target_processed_dir / f"{raw_f.stem}.wav"
                if not proc_target.exists():
                    try:
                        wave = librosa.load(str(raw_f), sr=16000, mono=True)[0]
                        sf.write(str(proc_target), wave, 16000, subtype='PCM_16')
                    except Exception as e:
                        print(f"Skipping {raw_f}: {e}")

                split_manifests[sp].append({
                    "filename": raw_f.name,
                    "processed_wav": proc_target.name,
                    "split": sp,
                    "class": "gunshot" if lbl == 1 else "background",
                    "base_stem": g_info["base_stem"],
                    "relative_path": str(proc_target.relative_to(project_root))
                })

    # 6. Save split manifests & migration log
    print("\n[4/6] Exporting manifests to data/manifests/...")
    for sp in ["train", "val", "test"]:
        sp_file = project_root / "data" / "manifests" / f"{sp}.csv"
        rows = split_manifests[sp]
        if rows:
            with open(sp_file, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
                writer.writeheader()
                writer.writerows(rows)
            print(f"      Exported {len(rows)} entries to data/manifests/{sp}.csv")

    # Save migration log JSON
    with open(project_root / "data" / "manifests" / "migration_log.json", "w", encoding="utf-8") as f:
        json.dump(migration_log, f, indent=2)

    # 7. Generate Dataset Inventory Report
    print("\n[5/6] Generating comprehensive dataset inventory report...")
    raw_gunshots = list((project_root / "data" / "raw" / "gunshots").glob("*.*"))
    raw_background = list((project_root / "data" / "raw" / "background").glob("*.*"))
    raw_synthetic = list((project_root / "data" / "raw" / "synthetic").glob("*.*"))
    proc_train = list((project_root / "data" / "processed" / "train").rglob("*.wav"))
    proc_val = list((project_root / "data" / "processed" / "validation").rglob("*.wav"))
    proc_test = list((project_root / "data" / "processed" / "test").rglob("*.wav"))
    hn_approved = list((project_root / "data" / "hard_negatives" / "approved").glob("*.wav"))

    inventory_report = {
        "project_root": str(project_root),
        "total_raw_audio_files": len(raw_gunshots) + len(raw_background) + len(raw_synthetic),
        "raw_counts": {
            "gunshots": len(raw_gunshots),
            "background": len(raw_background),
            "synthetic": len(raw_synthetic)
        },
        "processed_counts": {
            "train": len(proc_train),
            "validation": len(proc_val),
            "test": len(proc_test)
        },
        "hard_negatives": {
            "approved_snippets_count": len(hn_approved),
            "approved_manifest_exists": (project_root / "data" / "hard_negatives" / "approved" / "approved_hard_negatives.json").exists()
        },
        "splits_composition": {
            "train_recordings": len(split_manifests["train"]),
            "validation_recordings": len(split_manifests["val"]),
            "test_recordings": len(split_manifests["test"])
        }
    }
    with open(project_root / "data" / "manifests" / "dataset_inventory.json", "w", encoding="utf-8") as f:
        json.dump(inventory_report, f, indent=2)
    with open(project_root / "reports" / "dataset_inventory_report.json", "w", encoding="utf-8") as f:
        json.dump(inventory_report, f, indent=2)

    print(f"      Total Raw Audio Files:       {inventory_report['total_raw_audio_files']}")
    print(f"        - Raw Gunshots:            {inventory_report['raw_counts']['gunshots']}")
    print(f"        - Raw Background:          {inventory_report['raw_counts']['background']}")
    print(f"        - Raw Synthetic:           {inventory_report['raw_counts']['synthetic']}")
    print(f"      Processed 16kHz WAVs:")
    print(f"        - Train Split:             {inventory_report['processed_counts']['train']}")
    print(f"        - Validation Split:        {inventory_report['processed_counts']['validation']}")
    print(f"        - Test Split:              {inventory_report['processed_counts']['test']}")
    print(f"      Approved Hard Negatives:     {inventory_report['hard_negatives']['approved_snippets_count']}")

    # 8. Copy utility scripts into scripts/ and tests into tests/
    print("\n[6/6] Organizing scripts/ and tests/...")
    script_files = [
        "audit_dataset.py", "generate_hard_negatives.py", "generate_negatives.py",
        "hard_negative_miner.py", "inventory.py", "record_background.py",
        "train_finetune.py", "run_experiments.py"
    ]
    for sf_name in script_files:
        src_f = project_root / sf_name
        if src_f.exists():
            dst_f = project_root / "scripts" / sf_name
            shutil.copy(str(src_f), str(dst_f))

    test_files = ["sanity_check.py"]
    for tf_name in test_files:
        src_f = project_root / tf_name
        if src_f.exists():
            dst_f = project_root / "tests" / tf_name
            shutil.copy(str(src_f), str(dst_f))

    print("\n[OK] Project and Audio Dataset Reorganization Completed Successfully!")
    return inventory_report


if __name__ == "__main__":
    run_reorganization()
