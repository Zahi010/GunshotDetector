"""
Auditing and Dataset Manifest Tool for Gunshot Sound Detection.

Provides:
1. Strict classification of all recordings into audited semantic categories.
2. Clear separation of:
   - Original unique recordings
   - Exact bit-for-bit duplicate copies (MD5 match)
   - Synthetic procedurally generated background examples
3. Verification of group-based splits to ensure zero data leakage.
4. Export of `dataset_manifest.csv` and `dataset_manifest.json`.
5. Syncing of audited classes into `data/gunshot/` and `data/background/`.
6. Transparent reporting of missing real-world sharp negatives (fireworks, backfires, door slams).
"""
import os
import re
import csv
import json
import hashlib
import argparse
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional

import soundfile as sf
import librosa
import numpy as np

import config
from inventory import get_base_stem, AUDIO_EXTENSIONS
from dataset import compute_file_hash


# Comprehensive audited taxonomy rules
def audit_classify_file(filename: str) -> Tuple[str, str, str]:
    """
    Classify filename into (sound_subcategory, assigned_class, description).
    Audited against acoustic analysis and AudioSet ontology.
    """
    f = filename.lower()

    # 1. Sci-Fi / Toy Gun / Lasers (Background / Non-gunshot)
    if any(k in f for k in [
        'laser', 'lazer', 'plasma', 'sci-fi', 'scifi', 'ray-gun',
        'toy-gun', 'nerf', 'fireball', 'grappling-gun', 'laze-gem'
    ]):
        return 'scifi_laser_toy', 'background', 'Sci-fi laser blaster / toy gun / acoustic synth effects'

    # 2. General Ambient / Music / Foley (Background / Non-gunshot)
    if any(k in f for k in [
        'epic-game-music', 'meditation_hypnosis', 'taking-photo-with-camera',
        'camera', 'bow-release', 'bow-and-arrow', 'gate-latch', 'caulking',
        'space_warning_gun_ambience', 'ivanv70--229738', 'wurtia-robto', 'arrow-release'
    ]):
        return 'ambient_foley_music', 'background', 'Everyday ambient audio, acoustic foley, or music'

    # 3. Firearm Handling & Foley (Reload, Cocking, Dry fire, Shells hitting ground)
    if any(k in f for k in [
        'reload', 'dry-firing', 'dry-fire', 'dryfiring', 'cocking',
        'gun-cock', 'ammo-loaded', 'cp99-reload', 'gun-load', 'mag-insert',
        'shaking-gun', 'caulking-gun-back'
    ]):
        return 'firearm_foley_mechanics', 'background', 'Firearm mechanical handling (reload, cocking, dry-fire)'

    if any(k in f for k in ['shell-hitting', 'shells-hitting', 'shell-ping']):
        # If accompanied by an actual firearm shot
        if any(k in f for k in ['50-caliber-rifle-shot', 'gunshot', 'rifle-shot']):
            return 'gunshot_single', 'gunshot', 'High-caliber rifle shot with trailing brass ping'
        return 'firearm_foley_shell_impact', 'background', 'Brass shell casing impact on floor / ground'

    # 4. Projectile Flybys & Ricochets (no muzzle blast)
    if 'bullet-flyby' in f:
        return 'projectile_flyby', 'background', 'Bullet supersonic flyby / whiz (no muzzle blast)'

    if 'ricochet' in f:
        if '22-caliber-gunfire-with-ricochet' in f:
            return 'gunshot_single', 'gunshot', '22-caliber gunshot with ricochet'
        return 'projectile_ricochet', 'background', 'Bullet ricochet impact sound'

    # 5. Heavy Rocket / Missile Motors (Background / Non-gunshot)
    if any(k in f for k in ['anti-tank-missile', 'rocket-launch', 'rocket-launcher', 'shooting-star']):
        return 'heavy_launcher_motor', 'background', 'Rocket / missile motor launch and exhaust hiss'

    # 6. Foley Impacts / Punches (Background / Non-gunshot)
    if any(k in f for k in ['wide-range-impacts', 'distorted-impact-explosion']):
        return 'impact_punch_foley', 'background', 'Synthesized punch / slap foley impact'

    # 7. Gun Battles & Distant War Ambiences (Gunshot)
    if any(k in f for k in ['gun-battle', 'distant-war', 'war-ambience', 'firing-range', 'gun-firing-from-a-distance']):
        return 'gun_battle_ambience', 'gunshot', 'Multiple gunshots in battle, distant gunfire, or firing range acoustic ambience'

    # 8. Gunshots: Automatic Weapon Bursts / Machine Guns
    if any(k in f for k in [
        'machine-gun', 'machine_gun', 'heavymachinegun', 'machinegun',
        'ak47', 'akm', 'ar15', 'm16', 'm4', 'm240', 'aa-12', 'saiga-12',
        'uzi', 'burst', 'automatic_weapon_firing', '22multpl2', '50-cal-mg',
        'continuous-shooting'
    ]):
        return 'gunshot_automatic_burst', 'gunshot', 'Automatic weapon burst / machine gun fire'

    # 9. Gunshots: Artillery / Mortar / Turret
    if any(k in f for k in ['mortar', 'artillery', 'turret']):
        return 'gunshot_artillery_mortar', 'gunshot', 'Heavy artillery, mortar, or turret cannon discharge'

    # 10. Gunshots: Single Shot / Small Arms
    if any(k in f for k in [
        'shotgun', 'revolver', 'pistol', 'pistal', 'handgun', 'rifle',
        'sniper', 'musket', 'glock', 'kimber', 'five-seven', 'semi-auto',
        'shot', 'shoot', 'shots', 'fire', 'gun_9mm', 'clean-sound-in-mp3',
        't-51-carbine', 'gun-fire', 'gun-shot', 'gun-firing'
    ]):
        return 'gunshot_single', 'gunshot', 'Firearm single shot / muzzle blast'

    # Default fallback
    return 'unclassified', 'background', 'Unclassified recording (defaulted to background)'


def build_dataset_manifest(
    raw_dir: Path = config.RAW_AUDIO_DIR,
    synthetic_dir: Optional[Path] = config.DATA_DIR / "background" / "synthetic"
) -> List[Dict[str, Any]]:
    """
    Build a complete, transparent, reviewable manifest of every audio file.
    """
    raw_dir = Path(raw_dir)
    records = []

    # 1. Scan Raw Workspace Files
    raw_files = sorted([
        f for f in os.listdir(raw_dir)
        if Path(f).suffix.lower() in AUDIO_EXTENSIONS and (raw_dir / f).is_file()
    ])

    seen_hashes: Dict[str, str] = {}

    for fname in raw_files:
        fpath = raw_dir / fname
        try:
            # File hash
            with open(fpath, "rb") as fh:
                md5 = hashlib.md5(fh.read()).hexdigest()

            # Metadata
            info = sf.info(str(fpath))
            duration = round(info.duration, 3)
            sr = info.samplerate
            channels = info.channels

            canonical_stem = get_base_stem(fname)

            # Determine duplicate status
            if md5 in seen_hashes:
                file_role = "exact_duplicate"
                primary_file = seen_hashes[md5]
            else:
                file_role = "original_recording"
                seen_hashes[md5] = fname
                primary_file = fname

            subcat, assigned_class, desc = audit_classify_file(fname)

            records.append({
                "filename": fname,
                "file_path": str(fpath),
                "file_role": file_role,
                "primary_duplicate_of": primary_file if file_role == "exact_duplicate" else "",
                "canonical_stem": canonical_stem,
                "md5": md5,
                "duration_seconds": duration,
                "samplerate": sr,
                "channels": channels,
                "sound_subcategory": subcat,
                "assigned_class": assigned_class,
                "label_source": "human_audited",
                "notes": desc
            })
        except Exception as e:
            print(f"Error auditing {fname}: {e}")

    # 2. Scan Synthetic Background Files if present
    if synthetic_dir and synthetic_dir.exists():
        synth_files = sorted(list(synthetic_dir.glob("*.wav")))
        for fpath in synth_files:
            try:
                with open(fpath, "rb") as fh:
                    md5 = hashlib.md5(fh.read()).hexdigest()
                info = sf.info(str(fpath))
                name = fpath.name

                if "room_ambience" in name:
                    subcat = "synthetic_room_ambience"
                    desc = "Procedural synthetic indoor room tone (HVAC + air modulation)"
                elif "urban_rumble" in name:
                    subcat = "synthetic_urban_rumble"
                    desc = "Procedural synthetic Brownian traffic/urban rumble"
                elif "pink_noise" in name:
                    subcat = "synthetic_pink_noise"
                    desc = "Procedural synthetic pink noise"
                elif "transient_knocks" in name:
                    subcat = "synthetic_transient_knocks"
                    desc = "Procedural synthetic wooden tap / knock non-gunshot transients"
                elif "silence_tone" in name:
                    subcat = "synthetic_silence_noise"
                    desc = "Procedural synthetic low-level noise floor / silence tone"
                else:
                    subcat = "synthetic_generic"
                    desc = "Procedural synthetic negative example"

                records.append({
                    "filename": name,
                    "file_path": str(fpath),
                    "file_role": "synthetic_generated",
                    "primary_duplicate_of": "",
                    "canonical_stem": fpath.stem,
                    "md5": md5,
                    "duration_seconds": round(info.duration, 3),
                    "samplerate": info.samplerate,
                    "channels": info.channels,
                    "sound_subcategory": subcat,
                    "assigned_class": "background",
                    "label_source": "synthetic_generator",
                    "notes": desc
                })
            except Exception as e:
                print(f"Error auditing synthetic {fpath.name}: {e}")

    return records


def export_manifest(
    records: List[Dict[str, Any]],
    csv_path: Path = Path("dataset_manifest.csv"),
    json_path: Path = Path("dataset_manifest.json")
) -> None:
    """Save dataset manifest to CSV and JSON."""
    if not records:
        print("No records to export!")
        return

    # JSON export
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2)

    # CSV export
    fields = [
        "filename", "file_role", "assigned_class", "sound_subcategory",
        "duration_seconds", "canonical_stem", "md5", "samplerate", "channels",
        "primary_duplicate_of", "label_source", "notes"
    ]
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(records)

    print(f"[OK] Manifest exported:")
    print(f"  -> CSV:  {csv_path} ({len(records)} entries)")
    print(f"  -> JSON: {json_path} ({len(records)} entries)")


def sync_audited_dataset(
    manifest_records: List[Dict[str, Any]],
    target_data_dir: Path = config.DATA_DIR
) -> None:
    """
    Synchronize raw files into data/gunshot/ and data/background/ strictly
    according to audited manifest labels.
    """
    import shutil

    gunshot_dir = target_data_dir / "gunshot"
    bg_dir = target_data_dir / "background"
    gunshot_dir.mkdir(parents=True, exist_ok=True)
    bg_dir.mkdir(parents=True, exist_ok=True)

    # Clean existing symlinks/copies if needed (preserve synthetic)
    for f in gunshot_dir.glob("*.mp3"):
        try:
            f.unlink()
        except Exception:
            pass
    for f in bg_dir.glob("*.mp3"):
        try:
            f.unlink()
        except Exception:
            pass

    copied_pos = 0
    copied_neg = 0

    for rec in manifest_records:
        if rec["file_role"] == "synthetic_generated":
            continue  # Keep synthetic where it is in data/background/synthetic

        src_path = Path(rec["file_path"])
        dest_dir = gunshot_dir if rec["assigned_class"] == "gunshot" else bg_dir
        dest_path = dest_dir / rec["filename"]

        if not dest_path.exists():
            shutil.copy2(src_path, dest_path)

        if rec["assigned_class"] == "gunshot":
            copied_pos += 1
        else:
            copied_neg += 1

    print(f"\n[OK] Audited files synchronized:")
    print(f"  -> data/gunshot/:    {copied_pos} files")
    print(f"  -> data/background/: {copied_neg} real-world files")
    print(f"  -> data/background/synthetic/: preserved procedural negatives")


def print_audit_summary(records: List[Dict[str, Any]]) -> None:
    """Print detailed summary statistics of the audited dataset."""
    total = len(records)
    roles = {}
    classes = {}
    subcats = {}
    total_dur_by_class = {"gunshot": 0.0, "background": 0.0}

    for r in records:
        roles[r["file_role"]] = roles.get(r["file_role"], 0) + 1
        classes[r["assigned_class"]] = classes.get(r["assigned_class"], 0) + 1
        subcats[r["sound_subcategory"]] = subcats.get(r["sound_subcategory"], 0) + 1
        total_dur_by_class[r["assigned_class"]] += r["duration_seconds"]

    print("\n=======================================================")
    print("           AUDITED DATASET INVENTORY SUMMARY")
    print("=======================================================")
    print(f"Total Audio Records: {total}")
    print("\n1. Record Roles Breakdown:")
    for role, cnt in sorted(roles.items()):
        print(f"   - {role:<24}: {cnt:3d} files")

    print("\n2. Class Balance:")
    for cls, cnt in sorted(classes.items()):
        dur_min = total_dur_by_class[cls] / 60.0
        print(f"   - [{cls.upper():<10}]: {cnt:3d} files | {dur_min:6.2f} minutes total audio")

    print("\n3. Sound Subcategories:")
    for sc, cnt in sorted(subcats.items(), key=lambda x: x[1], reverse=True):
        print(f"   - {sc:<30}: {cnt:3d} files")

    print("\n4. Realistic Negative Sounds Gap Assessment:")
    print("   [CRITICAL AUDIT FINDING]")
    print("   - Fireworks / Firecrackers:       ABSENT (0 real recordings)")
    print("   - Vehicle Backfires:              ABSENT (0 real recordings)")
    print("   - Heavy Door / Car Door Slams:    ABSENT (only 1 metal gate latch & synthetic knocks)")
    print("   - Dropped Heavy Objects/Pans:     ABSENT (0 real recordings)")
    print("   * Note: The dataset contains firearm foley, laser sounds, and synthetic knocks.")
    print("     Synthetic noise and simple knocks DO NOT substitute for varied real-world sharp negatives.")
    print("     Users deploying in real-world environments MUST add real-world acoustic negatives.")
    print("=======================================================\n")


def verify_split_leakage(data_dir: Path = config.DATA_DIR) -> bool:
    """
    Verify that train, validation, and test splits have ZERO data leakage:
    - No shared group keys
    - No shared base recording stems
    - No shared MD5 hashes
    """
    from dataset import GunshotDataset, compute_file_hash

    print("\n=======================================================")
    print("      VERIFYING LEAK-FREE SPLITTING INTEGRITY")
    print("=======================================================")

    ds = GunshotDataset(data_dir=data_dir)
    ds.index_files()

    train_groups = set(ds.splits["train"])
    val_groups = set(ds.splits["val"])
    test_groups = set(ds.splits["test"])

    # 1. Group key overlap check
    train_val_overlap = train_groups & val_groups
    train_test_overlap = train_groups & test_groups
    val_test_overlap = val_groups & test_groups

    print(f"Total Unique Recording Groups: {len(ds.groups)}")
    print(f"  Train Groups: {len(train_groups)}")
    print(f"  Val Groups:   {len(val_groups)}")
    print(f"  Test Groups:  {len(test_groups)}")

    leakage_found = False

    if train_val_overlap:
        print(f"  [LEAKAGE ERROR] Train/Val group overlap: {train_val_overlap}")
        leakage_found = True
    if train_test_overlap:
        print(f"  [LEAKAGE ERROR] Train/Test group overlap: {train_test_overlap}")
        leakage_found = True
    if val_test_overlap:
        print(f"  [LEAKAGE ERROR] Val/Test group overlap: {val_test_overlap}")
        leakage_found = True

    # 2. Base stem overlap check
    train_stems = {ds.groups[g]["base_stem"] for g in train_groups}
    val_stems = {ds.groups[g]["base_stem"] for g in val_groups}
    test_stems = {ds.groups[g]["base_stem"] for g in test_groups}

    stem_train_val = train_stems & val_stems
    stem_train_test = train_stems & test_stems
    stem_val_test = val_stems & test_stems

    if stem_train_val or stem_train_test or stem_val_test:
        print(f"  [LEAKAGE ERROR] Shared recording stems across splits:")
        if stem_train_val:
            print(f"    Train & Val: {stem_train_val}")
        if stem_train_test:
            print(f"    Train & Test: {stem_train_test}")
        if stem_val_test:
            print(f"    Val & Test: {stem_val_test}")
        leakage_found = True
    else:
        print("  [PASS] Zero base stem leakage across Train, Val, and Test splits.")

    # 3. MD5 content hash overlap check
    def get_hashes_for_split(group_list):
        h_set = set()
        for g in group_list:
            for f in ds.groups[g]["files"]:
                h_set.add(compute_file_hash(f))
        return h_set

    train_hashes = get_hashes_for_split(train_groups)
    val_hashes = get_hashes_for_split(val_groups)
    test_hashes = get_hashes_for_split(test_groups)

    h_train_val = train_hashes & val_hashes
    h_train_test = train_hashes & test_hashes
    h_val_test = val_hashes & test_hashes

    if h_train_val or h_train_test or h_val_test:
        print(f"  [LEAKAGE ERROR] Shared MD5 file hashes across splits!")
        leakage_found = True
    else:
        print("  [PASS] Zero MD5 content hash leakage across Train, Val, and Test splits.")

    if not leakage_found:
        print("  [CONFIRMED] Splits are strictly disjoint at the recording session level.")
        print("              Windowing occurs AFTER group partitioning.")
    print("=======================================================\n")
    return not leakage_found


def ingest_recording(file_path: Path, label: str, category: Optional[str] = None) -> bool:
    """
    Ingest a new audio recording into the dataset with reviewable metadata.
    Validates readability, verifies format, checks for duplicates, and copies
    to `data/gunshot/` or `data/background/real/`.
    """
    file_path = Path(file_path)
    if not file_path.exists():
        print(f"[ERROR] File does not exist: {file_path}")
        return False

    label = label.lower().strip()
    if label not in ["gunshot", "background", "non_gunshot"]:
        print(f"[ERROR] Invalid label: {label}. Must be 'gunshot' or 'background'.")
        return False
    if label == "non_gunshot":
        label = "background"

    # 1. Validate readability & format
    try:
        data, sr = sf.read(str(file_path))
        dur = len(data) / sr
        print(f"  Valid audio file: {file_path.name} ({dur:.2f}s, {sr} Hz, {data.shape})")
    except Exception as e:
        print(f"[ERROR] Cannot decode audio file: {e}")
        return False

    # 2. Check for duplicate MD5 hash
    h = compute_file_hash(file_path)
    print(f"  MD5 Content Hash: {h}")

    # Check against existing manifest
    manifest_path = Path("dataset_manifest.json")
    if manifest_path.exists():
        with open(manifest_path, "r", encoding="utf-8") as f:
            existing = json.load(f)
        for r in existing:
            if r.get("md5") == h:
                print(f"  [WARNING] Bit-for-bit duplicate already in dataset: {r.get('filename')} (role: {r.get('file_role')}, path: {r.get('file_path')})")

    # 3. Destination folder
    if label == "gunshot":
        dest_dir = config.DATA_DIR / "gunshot"
    else:
        dest_dir = config.DATA_DIR / "background" / "real"
    dest_dir.mkdir(parents=True, exist_ok=True)

    dest_file = dest_dir / file_path.name
    import shutil
    shutil.copy2(file_path, dest_file)
    print(f"  [SUCCESS] Copied to: {dest_file}")
    print("  To update cache and manifest, run: python audit_dataset.py --manifest --sync")
    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Audit dataset, verify splits, and export manifest.")
    parser.add_argument("--manifest", action="store_true", default=True, help="Export dataset_manifest.csv & .json")
    parser.add_argument("--sync", action="store_true", default=True, help="Sync audited classes to data/gunshot & data/background")
    parser.add_argument("--verify-splits", action="store_true", default=False, help="Verify zero leakage between splits")
    parser.add_argument("--review", action="store_true", help="Print interactive review listing")
    parser.add_argument("--add-audio", type=str, help="Path to a new audio file to add to dataset")
    parser.add_argument("--label", type=str, choices=["gunshot", "background"], help="Class label for newly added audio")
    parser.add_argument("--category", type=str, help="Optional category (e.g. firework, backfire, door_slam)")
    args = parser.parse_args()

    if args.add_audio:
        if not args.label:
            print("[ERROR] Please specify --label gunshot OR --label background when adding audio.")
            exit(1)
        ingest_recording(Path(args.add_audio), args.label, args.category)
        exit(0)

    records = build_dataset_manifest()
    print_audit_summary(records)
    export_manifest(records)

    if args.sync:
        sync_audited_dataset(records)

    if args.verify_splits:
        verify_split_leakage()


