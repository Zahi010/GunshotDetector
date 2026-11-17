"""
Phase 17: Extended Continuous Negative Audio Acquisition Pipeline.

Acquires new independent continuous urban soundscapes from Zenodo Record 18561165
(Bilbao Old Town Urban Soundscape, Creative Commons Attribution 4.0):
1. 100% uninterrupted, natural continuous recordings.
2. Standardized to 16 kHz 16-bit PCM mono via scipy.signal.resample_poly.
3. Zero track splicing, zero looping, zero artificial crossfades.
4. Preserves Phase 16 streams as historical baseline.

SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.
"""

import os
import sys
import time
import urllib.request
import urllib.parse
import hashlib
from pathlib import Path

import numpy as np
import soundfile as sf
import scipy.signal

WORKSPACE_ROOT = Path("e:/gunshot/gunshot").resolve()
OUTPUT_DIR = WORKSPACE_ROOT / "data" / "phase17_natural_continuous"
SCRATCH_DIR = WORKSPACE_ROOT / "scratch"

TARGET_SR = 16000
SAFETY_DESIGNATION = "RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY"

ZENODO_BASE = "https://zenodo.org/api/records/18561165/files/"

NEW_STREAMS = [
    {
        "stream_id": "P17-STREAM-12",
        "remote_key": "CP_18_Exterior_30-06-16_18,30h.wav",
        "local_fn": "phase17_urban_exterior_plaza_30min.wav",
        "scratch_file": "CP_18_Exterior.wav",
        "category": "urban_outdoor_ambience",
        "environment": "historic_urban_exterior_plaza",
        "description": "Bilbao Old Town exterior pedestrian plaza with distant chatter, footsteps, urban acoustics"
    },
    {
        "stream_id": "P17-STREAM-13",
        "remote_key": "CP_14_Interior_30-06-16_12,55h.wav",
        "local_fn": "phase17_urban_interior_commercial_30min.wav",
        "scratch_file": None,
        "category": "general_indoor_ambience",
        "environment": "historic_commercial_interior",
        "description": "Bilbao Old Town interior ground-floor shop with indoor reverberation and street penetration"
    },
    {
        "stream_id": "P17-STREAM-14",
        "remote_key": "CP_21_Exterior_30-06-16_19,10h.wav",
        "local_fn": "phase17_urban_exterior_walkway_30min.wav",
        "scratch_file": None,
        "category": "urban_outdoor_ambience",
        "environment": "pedestrian_walkway",
        "description": "Pedestrian walkway ambience, distant delivery cart wheels, ambient street resonance"
    },
    {
        "stream_id": "P17-STREAM-15",
        "remote_key": "CP_17_Exterior_30-06-16_18,20h.wav",
        "local_fn": "phase17_urban_exterior_terrace_30min.wav",
        "scratch_file": None,
        "category": "public_spaces",
        "environment": "outdoor_cafe_terrace",
        "description": "Open-air cafe terrace with subtle glass tableware transients and conversation hum"
    },
    {
        "stream_id": "P17-STREAM-16",
        "remote_key": "CP_15_Interior_30-06-16_13,15h.wav",
        "local_fn": "phase17_urban_interior_arcade_30min.wav",
        "scratch_file": None,
        "category": "general_indoor_ambience",
        "environment": "covered_arcade_interior",
        "description": "Covered architectural arcade with high reverberation time and diffuse footsteps"
    },
    {
        "stream_id": "P17-STREAM-17",
        "remote_key": "CP_10_Interior_30-06-16_11,55h.wav",
        "local_fn": "phase17_urban_interior_hall_30min.wav",
        "scratch_file": None,
        "category": "general_indoor_ambience",
        "environment": "residential_entrance_hall",
        "description": "Residential ground floor entrance hall with quiet interior acoustic dynamics"
    }
]

def compute_sha256(filepath: Path) -> str:
    hasher = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            hasher.update(chunk)
    return hasher.hexdigest()

def main():
    print("=" * 80)
    print("   PHASE 17: EXTENDED NATURAL CONTINUOUS NEGATIVE AUDIO ACQUISITION")
    print(f"   Safety: {SAFETY_DESIGNATION}")
    print("=" * 80 + "\n")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

    for item in NEW_STREAMS:
        sid = item["stream_id"]
        dst_path = OUTPUT_DIR / item["local_fn"]
        if dst_path.exists():
            print(f"[SKIP] {sid} already exists at {dst_path}")
            continue

        raw_scratch = SCRATCH_DIR / (item["scratch_file"] or f"raw_{item['remote_key']}")
        if not raw_scratch.exists():
            # Download from Zenodo
            encoded_key = urllib.parse.quote(item["remote_key"])
            url = ZENODO_BASE + encoded_key + "/content"
            print(f"[*] Downloading {sid}: {item['remote_key']}...")
            req = urllib.request.Request(url, headers=headers)
            t0 = time.time()
            with urllib.request.urlopen(req, timeout=90) as resp, open(raw_scratch, "wb") as f:
                while chunk := resp.read(1024 * 1024):
                    f.write(chunk)
            print(f"    Downloaded {raw_scratch.stat().st_size / (1024*1024):.1f} MB in {time.time()-t0:.1f}s")

        # Resample to 16kHz mono float32
        print(f"[*] Standardizing {sid} to 16kHz mono PCM...")
        sig, in_sr = sf.read(raw_scratch)
        if sig.ndim > 1:
            sig = np.mean(sig, axis=1)
        if in_sr != TARGET_SR:
            # Resample in memory-safe 60-second blocks
            block_samples_in = int(60.0 * in_sr)
            resampled_blocks = []
            for start_idx in range(0, len(sig), block_samples_in):
                end_idx = min(start_idx + block_samples_in, len(sig))
                block_in = sig[start_idx:end_idx].astype(np.float32)
                block_out = scipy.signal.resample_poly(block_in, TARGET_SR, in_sr)
                resampled_blocks.append(block_out)
            sig_16k = np.concatenate(resampled_blocks)
        else:
            sig_16k = sig.astype(np.float32)

        # Write 16-bit PCM mono WAV
        sf.write(dst_path, sig_16k, TARGET_SR, subtype="PCM_16")
        dur_s = len(sig_16k) / TARGET_SR
        sz_mb = dst_path.stat().st_size / (1024 * 1024)
        print(f"[+] Saved {sid}: {dst_path.name} ({dur_s:.1f}s = {dur_s/60:.1f} min, {sz_mb:.1f} MB, SHA-256: {compute_sha256(dst_path)[:16]}...)")

    print("\n[+] Acquisition process complete.")

if __name__ == "__main__":
    main()

