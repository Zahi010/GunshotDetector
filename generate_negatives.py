"""
Negative Audio Dataset Preparation and Synthetic Background Generator.

Why a Gunshot Detector Needs Diverse Negative (Background) Examples:
-------------------------------------------------------------------
A machine learning classifier trained only on gunshot sounds has no baseline for
what the world sounds like when firearms are NOT firing. In real-world deployment,
an audio detector is exposed to 99.999% non-gunshot audio:
- Environmental ambience: wind, rain, AC rumble, car engines, distant traffic.
- Acoustic transients: doors slamming, fireworks, thunder, car backfires, drum beats,
  hand claps, dropped objects, construction hammering.
- Speech and indoor activity: voices, footsteps, laughter, keyboard clicks.
- Silence and low-level microphone noise.

Without varied negative examples, the classifier suffers from:
1. Catastrophic False Alarms: triggering on any sudden loud noise or ambient peak.
2. Degenerate Decision Boundaries: learning spurious recording artifacts (e.g.,
   microphone hiss, MP3 compression quirks) rather than genuine acoustic gunshot features.

This module:
1. Curates non-gunshot files from the existing workspace (foley, reloading, dry fire, lasers, music).
2. Procedurally synthesizes realistic background audio (urban rumble, pink noise,
   room tone, transient thuds, taps, knocks, and silence) at 16 kHz.
3. Organizes them into `data/gunshot/` and `data/background/`.
4. Makes it effortless to drop custom negative recordings into `data/background/`.
"""
import os
import re
import shutil
import argparse
import numpy as np
import soundfile as sf
from pathlib import Path
from typing import Dict, List, Any
import config
from inventory import get_base_stem, categorize_filename, AUDIO_EXTENSIONS


def generate_pink_noise(duration_sec: float, sr: int = 16000) -> np.ndarray:
    """Generate pink noise using Voss-McCartney algorithm."""
    num_samples = int(duration_sec * sr)
    num_rows = 16
    array = np.random.randn(num_rows, num_samples // num_rows + 1)
    array = np.repeat(array, num_rows, axis=1)[:, :num_samples]
    pink = np.sum(array, axis=0)
    pink = pink - np.mean(pink)
    peak = np.max(np.abs(pink))
    return (pink / (peak + 1e-8) * 0.15).astype(np.float32)


def generate_brown_noise(duration_sec: float, sr: int = 16000) -> np.ndarray:
    """Generate Brownian / red noise (random walk, mimics traffic/engine rumble)."""
    num_samples = int(duration_sec * sr)
    white = np.random.randn(num_samples)
    brown = np.cumsum(white)
    # High-pass filter drift removal
    brown = brown - np.convolve(brown, np.ones(500)/500, mode='same')
    peak = np.max(np.abs(brown))
    return (brown / (peak + 1e-8) * 0.20).astype(np.float32)


def generate_room_ambience(duration_sec: float, sr: int = 16000) -> np.ndarray:
    """Generate synthetic indoor room tone (HVAC hum + gentle filtered noise)."""
    num_samples = int(duration_sec * sr)
    t = np.linspace(0, duration_sec, num_samples, endpoint=False)
    # 50 Hz and 120 Hz electrical/HVAC harmonics
    hum = 0.03 * np.sin(2 * np.pi * 60 * t) + 0.015 * np.sin(2 * np.pi * 120 * t)
    air = generate_pink_noise(duration_sec, sr) * 0.3
    # Gentle amplitude modulation (breathing/air flow)
    mod = 1.0 + 0.2 * np.sin(2 * np.pi * 0.2 * t)
    signal = (hum + air) * mod
    return signal.astype(np.float32)


def generate_transient_knocks(duration_sec: float, sr: int = 16000, num_knocks: int = 3) -> np.ndarray:
    """Generate non-gunshot acoustic transients (door knocks, table taps, footsteps)."""
    num_samples = int(duration_sec * sr)
    signal = np.zeros(num_samples, dtype=np.float32)
    # Add quiet background
    signal += generate_pink_noise(duration_sec, sr) * 0.02

    times = np.random.uniform(0.2, max(0.3, duration_sec - 0.4), size=num_knocks)
    for t_pos in times:
        idx = int(t_pos * sr)
        # Transient decay ~50ms
        decay_samples = int(0.08 * sr)
        if idx + decay_samples >= num_samples:
            continue
        t_decay = np.linspace(0, 0.08, decay_samples)
        # Resonance frequency around 150 - 300 Hz (wooden tap/knock)
        freq = np.random.uniform(150, 320)
        env = np.exp(-t_decay * np.random.uniform(30, 60))
        impulse = np.sin(2 * np.pi * freq * t_decay) * env * np.random.uniform(0.3, 0.7)
        signal[idx:idx + decay_samples] += impulse.astype(np.float32)

    peak = np.max(np.abs(signal))
    if peak > 0.95:
        signal = signal / peak * 0.90
    return signal.astype(np.float32)


def generate_synthetic_negatives(output_dir: Path, count: int = 40, sr: int = 16000) -> List[Path]:
    """Generate a diverse library of synthetic negative recordings."""
    output_dir.mkdir(parents=True, exist_ok=True)
    created = []

    types = [
        ("room_ambience", generate_room_ambience, (2.0, 5.0)),
        ("urban_rumble", generate_brown_noise, (2.0, 5.0)),
        ("pink_noise", generate_pink_noise, (2.0, 4.0)),
        ("transient_knocks", generate_transient_knocks, (2.0, 4.0)),
        ("silence_tone", lambda d, s: np.random.randn(int(d*s)).astype(np.float32) * 1e-4, (1.5, 3.0)),
    ]

    for i in range(count):
        kind, gen_fn, dur_range = types[i % len(types)]
        dur = np.random.uniform(*dur_range)
        audio = gen_fn(dur, sr)
        fname = f"synth_negative_{kind}_{i+1:03d}.wav"
        fpath = output_dir / fname
        sf.write(str(fpath), audio, sr)
        created.append(fpath)

    return created


def organize_dataset(
    source_dir: Path = config.RAW_AUDIO_DIR,
    target_dir: Path = config.DATA_DIR,
    num_synthetic_negatives: int = 50
) -> Dict[str, Any]:
    """
    Organize downloaded audio files and synthetic backgrounds into:
    - data/gunshot/
    - data/background/
    Creates file copies or links and outputs dataset summary.
    """
    source_dir = Path(source_dir)
    target_dir = Path(target_dir)

    gunshot_dir = target_dir / "gunshot"
    bg_dir = target_dir / "background"

    gunshot_dir.mkdir(parents=True, exist_ok=True)
    bg_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n=======================================================")
    print(f"      DATASET STRUCTURING & NEGATIVE EXPANSION")
    print(f"=======================================================")
    print(f"Source Directory: {source_dir}")
    print(f"Target Directory: {target_dir}")

    files = [
        f for f in os.listdir(source_dir)
        if Path(f).suffix.lower() in AUDIO_EXTENSIONS
    ]

    copied_gunshots = 0
    copied_foley_negatives = 0

    for f in files:
        src_path = source_dir / f
        cat = categorize_filename(f)
        stem = get_base_stem(f)

        if cat == "gunshot":
            dest = gunshot_dir / f
            if not dest.exists():
                shutil.copy2(src_path, dest)
            copied_gunshots += 1
        elif cat in ("firearm_foley_mechanics", "laser_scifi_toy", "ambient_music_other"):
            dest = bg_dir / f
            if not dest.exists():
                shutil.copy2(src_path, dest)
            copied_foley_negatives += 1
        else:
            # For unclassified files, inspect if it's weapon fire vs ambient/debris
            low = f.lower()
            if any(w in low for w in ["machinegun", "rifle", "shots", "semi-automatic", "aa-12", "m240", "saiga"]):
                dest = gunshot_dir / f
                if not dest.exists():
                    shutil.copy2(src_path, dest)
                copied_gunshots += 1
            else:
                dest = bg_dir / f
                if not dest.exists():
                    shutil.copy2(src_path, dest)
                copied_foley_negatives += 1

    print(f"\nOrganized downloaded workspace recordings:")
    print(f"  -> Gunshot examples in {gunshot_dir.name}/:    {copied_gunshots} files")
    print(f"  -> Real-world negative examples (foley/ambient) in {bg_dir.name}/: {copied_foley_negatives} files")

    # Generate synthetic negatives to augment background diversity
    synthetic_dir = bg_dir / "synthetic"
    synthetic_files = generate_synthetic_negatives(synthetic_dir, count=num_synthetic_negatives, sr=config.SAMPLE_RATE)
    print(f"  -> Generated synthetic background examples: {len(synthetic_files)} files (ambient, urban, knocks, silence)")

    total_gunshots = len([f for f in gunshot_dir.glob("*.*") if f.suffix.lower() in AUDIO_EXTENSIONS])
    total_negatives = len([f for f in bg_dir.rglob("*.*") if f.suffix.lower() in AUDIO_EXTENSIONS])

    print(f"\nTotal Dataset Balance:")
    print(f"  [Positive] Gunshot class:    {total_gunshots} files")
    print(f"  [Negative] Background class: {total_negatives} files")
    print(f"  Total examples:              {total_gunshots + total_negatives} files")
    print(f"=======================================================\n")

    return {
        "gunshot_count": total_gunshots,
        "background_count": total_negatives,
        "gunshot_dir": str(gunshot_dir),
        "background_dir": str(bg_dir)
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Prepare dataset and generate negative background examples.")
    parser.add_argument("--source", type=str, default=str(config.RAW_AUDIO_DIR), help="Source audio directory")
    parser.add_argument("--target", type=str, default=str(config.DATA_DIR), help="Target data directory")
    parser.add_argument("--synth-count", type=int, default=50, help="Number of synthetic negative files to generate")
    args = parser.parse_args()

    organize_dataset(Path(args.source), Path(args.target), args.synth_count)
