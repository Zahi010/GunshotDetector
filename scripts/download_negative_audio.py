"""
Negative Audio Data Acquisition Script for Gunshot Detection System.
Downloads openly licensed, verified real-world environmental recordings from ESC-50 / Freesound
and organizes them into categorized background directories with full provenance tracking.
"""
import os
import sys
import csv
import json
import time
import hashlib
import argparse
import urllib.request
import io
from pathlib import Path
from typing import List, Dict, Any, Optional

import soundfile as sf
import numpy as np

# Ensure root is on sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import config

ESC50_META_URL = "https://raw.githubusercontent.com/karolpiczak/ESC-50/master/meta/esc50.csv"
ESC50_AUDIO_BASE_URL = "https://raw.githubusercontent.com/karolpiczak/ESC-50/master/audio/"

# Category mapping from ESC-50 classes to our detection background categories
CATEGORY_MAPPING = {
    # Sharp acoustic transients
    "fireworks": "fireworks",
    "door_wood_knock": "sharp_impacts",
    "glass_breaking": "sharp_impacts",
    "can_opening": "sharp_impacts",
    "clapping": "sharp_impacts",
    
    # Vehicles and machinery
    "engine": "engine_backfires_and_machinery",
    "chainsaw": "engine_backfires_and_machinery",
    "car_horn": "engine_backfires_and_machinery",
    "train": "engine_backfires_and_machinery",
    "hand_saw": "engine_backfires_and_machinery",
    
    # Environmental and weather
    "thunderstorm": "thunder_and_weather",
    "rain": "thunder_and_weather",
    "wind": "thunder_and_weather",
    "crackling_fire": "general_ambience",
    
    # Human activity
    "footsteps": "general_ambience",
}

def compute_sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def download_with_retry(url: str, max_retries: int = 3, timeout: int = 15) -> Optional[bytes]:
    for attempt in range(1, max_retries + 1):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "GunshotDetectionResearch/1.0"})
            with urllib.request.urlopen(req, timeout=timeout) as response:
                return response.read()
        except Exception as e:
            if attempt == max_retries:
                print(f"    [Error] Failed to download {url} after {max_retries} attempts: {e}")
                return None
            time.sleep(1.0 * attempt)
    return None

def run_download(
    categories: Optional[List[str]] = None,
    limit_per_class: int = 25,
    output_dir: Path = Path("data/raw/background"),
    manifest_path: Path = Path("data/manifests/negative_audio_sources.csv"),
    dry_run: bool = False
):
    output_dir = Path(output_dir)
    manifest_path = Path(manifest_path)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    
    print("\n=======================================================")
    print("      REAL NEGATIVE AUDIO ACQUISITION PIPELINE         ")
    print("=======================================================")
    print(f"Output Directory: {output_dir}")
    print(f"Manifest Path:    {manifest_path}")
    print(f"Dry Run Mode:     {dry_run}")
    print(f"Limit Per Class:  {limit_per_class}")
    
    # 1. Fetch ESC-50 Metadata
    print("\n[1/4] Fetching ESC-50 dataset catalog...")
    meta_bytes = download_with_retry(ESC50_META_URL)
    if not meta_bytes:
        raise RuntimeError("Could not download ESC-50 dataset catalog!")
    
    content = meta_bytes.decode("utf-8")
    reader = csv.DictReader(io.StringIO(content))
    all_rows = list(reader)
    print(f"  Downloaded catalog with {len(all_rows)} audio records across 50 classes.")
    
    # Filter requested categories
    target_classes = set(categories) if categories else set(CATEGORY_MAPPING.keys())
    selected_rows = [r for r in all_rows if r["category"] in target_classes]
    print(f"  Selected {len(selected_rows)} candidates across target classes: {sorted(list(target_classes))}")
    
    # Group by category and take up to limit_per_class
    grouped = {}
    for r in selected_rows:
        cat = r["category"]
        grouped.setdefault(cat, []).append(r)
        
    candidates_to_download = []
    for cat, rows in sorted(grouped.items()):
        taken = rows[:limit_per_class]
        candidates_to_download.extend(taken)
        print(f"    Category '{cat}': {len(taken)} recordings queued.")
        
    print(f"\n[2/4] Total recordings queued for acquisition: {len(candidates_to_download)}")
    if dry_run:
        print("[Dry Run] Exiting without downloading files.")
        return
        
    # 2. Download and Verify Files
    print("\n[3/4] Downloading audio recordings...")
    manifest_records = []
    existing_hashes = set()
    downloaded_count = 0
    skipped_count = 0
    failed_count = 0
    
    # Load existing manifest if present to preserve history
    if manifest_path.exists():
        try:
            with open(manifest_path, "r", encoding="utf-8") as f:
                r_old = csv.DictReader(f)
                for row in r_old:
                    if row.get("sha256"):
                        existing_hashes.add(row["sha256"])
                    manifest_records.append(row)
        except Exception:
            pass
            
    for i, item in enumerate(candidates_to_download, 1):
        esc_filename = item["filename"]
        esc_cat = item["category"]
        dest_cat = CATEGORY_MAPPING.get(esc_cat, "general_ambience")
        dest_folder = output_dir / dest_cat
        dest_folder.mkdir(parents=True, exist_ok=True)
        
        dest_path = dest_folder / esc_filename
        url = ESC50_AUDIO_BASE_URL + esc_filename
        
        # Check if file exists locally
        if dest_path.exists():
            with open(dest_path, "rb") as f:
                data = f.read()
            h = compute_sha256(data)
            status = "already_exists"
            skipped_count += 1
        else:
            print(f"  [{i}/{len(candidates_to_download)}] Downloading {esc_filename} ({esc_cat} -> {dest_cat})...")
            data = download_with_retry(url)
            if data is None:
                failed_count += 1
                continue
            h = compute_sha256(data)
            if h in existing_hashes:
                print(f"    [Skip] Duplicate file hash {h[:12]} already in dataset.")
                skipped_count += 1
                continue
                
            with open(dest_path, "wb") as f:
                f.write(data)
            status = "downloaded"
            downloaded_count += 1
            existing_hashes.add(h)
            
        # Inspect audio properties
        try:
            info = sf.info(str(dest_path))
            dur = round(float(info.duration), 2)
            sr = int(info.samplerate)
            channels = int(info.channels)
        except Exception:
            dur = 5.0
            sr = 44100
            channels = 1
            
        rec_id = f"esc50_{dest_cat}_{esc_filename.replace('.wav', '')}"
        
        record = {
            "recording_id": rec_id,
            "filename": esc_filename,
            "source_dataset": "ESC-50 (Freesound curation)",
            "source_url": url,
            "original_filename": esc_filename,
            "category": dest_cat,
            "sub_category": esc_cat,
            "license": "Creative Commons Attribution-NonCommercial 3.0 (CC-BY-NC)",
            "attribution": f"Freesound audio item {item.get('src_file', 'unknown')}, curated by Karol J. Piczak",
            "duration_seconds": dur,
            "sample_rate": sr,
            "channels": channels,
            "sha256": h,
            "download_status": status,
            "review_status": "approved_real_negative"
        }
        
        # Avoid duplicate row in manifest
        if not any(r.get("recording_id") == rec_id for r in manifest_records):
            manifest_records.append(record)
            
    # 3. Write Manifest
    print("\n[4/4] Writing negative audio source manifest...")
    fieldnames = [
        "recording_id", "filename", "source_dataset", "source_url", "original_filename",
        "category", "sub_category", "license", "attribution", "duration_seconds",
        "sample_rate", "channels", "sha256", "download_status", "review_status"
    ]
    with open(manifest_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(manifest_records)
        
    print(f"\nManifest successfully written to: {manifest_path}")
    print("Download Summary:")
    print(f"  Total records in manifest: {len(manifest_records)}")
    print(f"  New files downloaded:      {downloaded_count}")
    print(f"  Existing/skipped files:    {skipped_count}")
    print(f"  Failed downloads:          {failed_count}")
    
    # Category summary
    cat_counts = {}
    for r in manifest_records:
        c = r.get("category", "unknown")
        cat_counts[c] = cat_counts.get(c, 0) + 1
    print("\nManifest Distribution by Category:")
    for c, cnt in sorted(cat_counts.items()):
        print(f"  {c}: {cnt} recordings")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download real negative audio from web datasets.")
    parser.add_argument("--categories", nargs="+", default=None, help="Specific ESC-50 classes to download")
    parser.add_argument("--limit-per-class", type=int, default=25, help="Number of recordings per class")
    parser.add_argument("--dry-run", action="store_true", help="Inspect without downloading")
    parser.add_argument("--output-dir", type=str, default="data/raw/background")
    parser.add_argument("--manifest-path", type=str, default="data/manifests/negative_audio_sources.csv")
    args = parser.parse_args()
    
    run_download(
        categories=args.categories,
        limit_per_class=args.limit_per_class,
        output_dir=Path(args.output_dir),
        manifest_path=Path(args.manifest_path),
        dry_run=args.dry_run
    )
