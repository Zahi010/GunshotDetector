"""
Acquire verified real-world difficult negatives (metallic church bells / chimes) from ESC-50.
These are open-access CC-BY-NC licensed recordings with full provenance.
Outputs:
- data/raw/background/metallic_chimes_and_bells/
- Appends to data/manifests/negative_audio_sources.csv
"""
import os
import sys
import csv
import io
import time
import hashlib
import urllib.request
from pathlib import Path

ESC50_META_URL = "https://raw.githubusercontent.com/karolpiczak/ESC-50/master/meta/esc50.csv"
ESC50_AUDIO_BASE_URL = "https://raw.githubusercontent.com/karolpiczak/ESC-50/master/audio/"

def compute_sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def download_with_retry(url: str, max_retries: int = 3, timeout: int = 15):
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

def acquire_metallic_chimes():
    out_dir = Path("data/raw/background/metallic_chimes_and_bells")
    out_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = Path("data/manifests/negative_audio_sources.csv")

    print("\nFetching ESC-50 catalog to acquire church bells & metallic resonance recordings...")
    meta_bytes = download_with_retry(ESC50_META_URL)
    if not meta_bytes:
        raise RuntimeError("Could not fetch ESC-50 metadata!")

    reader = csv.DictReader(io.StringIO(meta_bytes.decode("utf-8")))
    target_rows = [r for r in reader if r["category"] == "church_bells"]
    print(f"Found {len(target_rows)} church_bells recordings in catalog.")

    downloaded = 0
    new_manifest_rows = []

    for r in target_rows:
        fn = r["filename"]
        target_path = out_dir / fn
        if target_path.exists():
            downloaded += 1
            continue

        url = ESC50_AUDIO_BASE_URL + fn
        print(f"  Downloading {fn}...")
        data = download_with_retry(url)
        if data:
            with open(target_path, "wb") as f:
                f.write(data)
            sha = compute_sha256(data)
            downloaded += 1
            new_manifest_rows.append({
                "recording_id": f"esc50_chimes_{Path(fn).stem}",
                "filename": fn,
                "source_dataset": "ESC-50 (Freesound curation)",
                "source_url": url,
                "original_filename": fn,
                "category": "metallic_chimes_and_bells",
                "sub_category": "church_bells",
                "license": "Creative Commons Attribution-NonCommercial 3.0 (CC-BY-NC)",
                "attribution": f"Freesound audio item {r.get('src_id', 'unknown')}, curated by Karol J. Piczak",
                "duration_seconds": 5.0,
                "sample_rate": 44100,
                "channels": 1,
                "sha256": sha,
                "download_status": "downloaded",
                "review_status": "approved_real_negative"
            })

    if new_manifest_rows and manifest_path.exists():
        with open(manifest_path, "a", newline="", encoding="utf-8") as f:
            fieldnames = [
                "recording_id", "filename", "source_dataset", "source_url", "original_filename",
                "category", "sub_category", "license", "attribution", "duration_seconds",
                "sample_rate", "channels", "sha256", "download_status", "review_status"
            ]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            for row in new_manifest_rows:
                writer.writerow(row)
        print(f"Appended {len(new_manifest_rows)} entries to {manifest_path}")

    print(f"[Done] Total metallic chimes & bells available: {downloaded}/{len(target_rows)}")

if __name__ == "__main__":
    acquire_metallic_chimes()
