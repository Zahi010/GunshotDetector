"""
Audio Inventory and Dataset Analysis Tool.

Inspects all audio files in the workspace or target directory:
- Identifies formats, sample rates, channel counts, and durations.
- Identifies corrupted or unreadable audio files.
- Identifies exact bit-level duplicate files (MD5) and filename stem duplicates (e.g. '(1).mp3').
- Categorizes recordings into potential classes (gunshots vs. firearm foley vs. lasers/sci-fi vs. ambient/music).
- Outputs comprehensive statistics and saves a detailed JSON report.
"""
import os
import re
import json
import hashlib
import argparse
from pathlib import Path
from typing import Dict, List, Any
import soundfile as sf
import config

AUDIO_EXTENSIONS = {".mp3", ".wav", ".ogg", ".flac", ".m4a"}

# Semantic keyword patterns for classification
GUNSHOT_PATTERNS = [
    r"gunshot", r"gun-shot", r"shot", r"shoot", r"gun-fire", r"gunfire",
    r"rifle", r"pistol", r"pistal", r"machine-gun", r"\bmg\b", r"uzi",
    r"ar15", r"glock", r"revolver", r"ak47", r"akm", r"burst", r"turret",
    r"handgun", r"mortar", r"artillery", r"musket", r"shotgun", r"semi-auto",
    r"continuous-shooting", r"firing-range", r"shots-fired", r"sniper"
]

FOLEY_MECHANICS_PATTERNS = [
    r"reload", r"dry-firing", r"dry-fire", r"dryfiring", r"cocking",
    r"gun-cock", r"\bload\b", r"magazine", r"\bammo\b", r"mag-insert",
    r"shaking-gun", r"shell-hitting", r"shells-hitting", r"gate-latch",
    r"caulking", r"shell-ping"
]

LASER_SCIFI_PATTERNS = [
    r"laser", r"lazer", r"plasma", r"sci-fi", r"scifi", r"ray-gun",
    r"toy-gun", r"nerf", r"fireball", r"grappling-gun"
]

AMBIENT_OTHER_PATTERNS = [
    r"music", r"ambience", r"hypnosis", r"camera", r"bow-release",
    r"bow-and-arrow", r"distant-war", r"war-ambience", r"desert-gun-battle"
]


def get_base_stem(filename: str) -> str:
    """Strip duplicate markers like ' (1).mp3', ' (2).mp3' from filename."""
    stem = Path(filename).stem
    # Match trailing space and parentheses with number, e.g., 'foo (1)' -> 'foo'
    cleaned = re.sub(r"\s*\(\d+\)$", "", stem)
    return cleaned


def categorize_filename(filename: str) -> str:
    """Categorize audio recording using audited semantic taxonomy."""
    try:
        from audit_dataset import audit_classify_file
        subcat, _, _ = audit_classify_file(filename)
        return subcat
    except Exception:
        low = filename.lower()
        for pat in FOLEY_MECHANICS_PATTERNS:
            if re.search(pat, low):
                return "firearm_foley_mechanics"
        for pat in LASER_SCIFI_PATTERNS:
            if re.search(pat, low):
                return "laser_scifi_toy"
        for pat in AMBIENT_OTHER_PATTERNS:
            if re.search(pat, low):
                return "ambient_music_other"
        for pat in GUNSHOT_PATTERNS:
            if re.search(pat, low):
                return "gunshot"
        return "unclassified"


def run_inventory(directory: Path, output_json: Path = None) -> Dict[str, Any]:
    """Scan directory and build comprehensive audio inventory."""
    directory = Path(directory)
    print(f"\n=======================================================")
    print(f"      AUDIO DATASET INVENTORY: {directory}")
    print(f"=======================================================\n")

    files = [
        f for f in os.listdir(directory)
        if Path(f).suffix.lower() in AUDIO_EXTENSIONS
    ]
    files.sort()

    total_files = len(files)
    if total_files == 0:
        print(f"No audio files found in {directory}!")
        return {"total_files": 0}

    print(f"Discovered {total_files} audio files. Analyzing metadata...")

    hash_map: Dict[str, str] = {}
    duplicates: List[Dict[str, str]] = []
    readable_records: List[Dict[str, Any]] = []
    unreadable_records: List[Dict[str, str]] = []

    sample_rate_dist: Dict[int, int] = {}
    format_dist: Dict[str, int] = {}
    channel_dist: Dict[int, int] = {}
    durations: List[float] = []

    category_counts: Dict[str, int] = {}
    category_files: Dict[str, List[str]] = {}
    group_map: Dict[str, List[str]] = {}

    for f in files:
        file_path = directory / f
        try:
            # Check bitwise duplicate using MD5
            with open(file_path, "rb") as fp:
                file_hash = hashlib.md5(fp.read()).hexdigest()

            is_dup = False
            if file_hash in hash_map:
                duplicates.append({
                    "duplicate_file": f,
                    "original_file": hash_map[file_hash],
                    "hash": file_hash
                })
                is_dup = True
            else:
                hash_map[file_hash] = f

            # Audio info using soundfile
            info = sf.info(str(file_path))
            sr = info.samplerate
            channels = info.channels
            duration = info.duration
            fmt = info.format

            sample_rate_dist[sr] = sample_rate_dist.get(sr, 0) + 1
            format_dist[fmt] = format_dist.get(fmt, 0) + 1
            channel_dist[channels] = channel_dist.get(channels, 0) + 1
            durations.append(duration)

            base_stem = get_base_stem(f)
            group_map.setdefault(base_stem, []).append(f)

            cat = categorize_filename(f)
            category_counts[cat] = category_counts.get(cat, 0) + 1
            category_files.setdefault(cat, []).append(f)

            readable_records.append({
                "filename": f,
                "base_stem": base_stem,
                "category": cat,
                "format": fmt,
                "samplerate": sr,
                "channels": channels,
                "duration_seconds": round(duration, 3),
                "is_content_duplicate": is_dup,
                "md5": file_hash
            })

        except Exception as err:
            unreadable_records.append({
                "filename": f,
                "error": str(err)
            })

    total_duration = sum(durations)
    unique_recordings_count = len(group_map)

    # Print Inventory Report
    print(f"Total audio files found:       {total_files}")
    print(f"Unreadable / corrupted files:  {len(unreadable_records)}")
    print(f"Bit-for-bit duplicate copies:  {len(duplicates)}")
    print(f"Unique recording groups (stem): {unique_recordings_count}")
    print(f"Total audio duration:          {total_duration / 60:.2f} minutes ({total_duration:.1f}s)")
    if durations:
        print(f"Audio duration range:          min {min(durations):.2f}s, max {max(durations):.2f}s, avg {total_duration/len(durations):.2f}s")

    print("\n--- Audio Formats ---")
    for fmt, count in format_dist.items():
        print(f"  {fmt}: {count} files")

    print("\n--- Sample Rate Distribution ---")
    for sr, count in sorted(sample_rate_dist.items()):
        print(f"  {sr} Hz: {count} files ({count/total_files*100:.1f}%)")

    print("\n--- Channel Distribution ---")
    for ch, count in sorted(channel_dist.items()):
        ch_name = "Mono" if ch == 1 else ("Stereo" if ch == 2 else f"{ch}-channel")
        print(f"  {ch_name} ({ch}): {count} files")

    print("\n--- Content Semantic Breakdown ---")
    for cat, count in sorted(category_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  {cat.replace('_', ' ').title():<28}: {count:>3} files")

    if unreadable_records:
        print("\n[WARNING] Unreadable Files:")
        for u in unreadable_records:
            print(f"  - {u['filename']}: {u['error']}")

    report = {
        "summary": {
            "total_files": total_files,
            "readable_files": len(readable_records),
            "unreadable_files": len(unreadable_records),
            "duplicate_copies": len(duplicates),
            "unique_recording_groups": unique_recordings_count,
            "total_duration_minutes": round(total_duration / 60, 2),
            "min_duration_seconds": round(min(durations), 2) if durations else 0,
            "max_duration_seconds": round(max(durations), 2) if durations else 0,
            "mean_duration_seconds": round(total_duration / len(durations), 2) if durations else 0,
        },
        "formats": format_dist,
        "sample_rates": sample_rate_dist,
        "channels": channel_dist,
        "categories": category_counts,
        "duplicates": duplicates,
        "unreadable": unreadable_records,
        "files": readable_records
    }

    if output_json:
        output_json = Path(output_json)
        with open(output_json, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)
        print(f"\n[OK] Detailed inventory report saved to: {output_json}")

    print("=======================================================\n")
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Inventory and inspect workspace audio files.")
    parser.add_argument("--dir", type=str, default=str(config.RAW_AUDIO_DIR), help="Directory to inspect")
    parser.add_argument("--output", type=str, default="inventory_report.json", help="Output JSON path")
    args = parser.parse_args()

    run_inventory(Path(args.dir), Path(args.output) if args.output else None)
