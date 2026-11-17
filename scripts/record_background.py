"""
Background Audio Recording and Ingestion Tool for Gunshot Detection System.

Facilitates collecting, annotating, and cataloging long real-world background
recordings to address dataset gaps and evaluate realistic false-alert rates.

Supported Categories:
- quiet_room: Indoor room tone, quiet office, HVAC, low-level white noise
- street_traffic: Urban street noise, passing cars, horns, engine rumbles
- door_slam: Front door, interior door, or car door slamming transients
- dropped_object: Metal pans, dropped cutlery, heavy books, falling items
- clapping_balloons: Hand applause, loud claps, balloon popping transients
- fireworks: Firecrackers, bottle rockets, ground flowers, aerial shells
- vehicle_backfire: Engine backfires, unburnt fuel exhaust detonations
- construction: Pneumatic nailers, hammering, drilling, jackhammer noise
- general_ambient: Park sounds, wind, footsteps, conversation, background music

Usage:
------
# 1. List available microphone devices:
python record_background.py --list-devices

# 2. Record 60 seconds of quiet room ambience:
python record_background.py --device 1 --duration 60 --category quiet_room --notes "Quiet bedroom with HVAC hum"

# 3. Record continuous street traffic until Ctrl+C:
python record_background.py --device 1 --duration 0 --category street_traffic --notes "Window facing main street traffic"

# 4. Ingest an existing pre-recorded long WAV or MP3 file:
python record_background.py --import-file "C:\\path\\to\\30min_office_noise.wav" --category quiet_room --notes "30 min office sound"
"""
import os
import sys
import time
import json
import hashlib
import argparse
import datetime
from pathlib import Path
from typing import Optional, Dict, Any

import soundfile as sf
import numpy as np

# Audio hardware interface
try:
    import sounddevice as sd
except ImportError:
    sd = None

import config
from dataset import load_audio_mono_16k, compute_file_hash


VALID_CATEGORIES = [
    "quiet_room",
    "street_traffic",
    "door_slam",
    "dropped_object",
    "clapping_balloons",
    "fireworks",
    "vehicle_backfire",
    "construction",
    "general_ambient"
]


def list_recording_devices():
    """Print available microphone and input devices."""
    if sd is None:
        print("[ERROR] sounddevice library not installed.")
        return

    print("\n=======================================================")
    print("      AVAILABLE AUDIO RECORDING / INPUT DEVICES")
    print("=======================================================")
    devices = sd.query_devices()
    default_in = sd.default.device[0]
    in_count = 0

    for idx, d in enumerate(devices):
        if d["max_input_channels"] > 0:
            is_def = " (DEFAULT)" if idx == default_in else ""
            print(f"  [{idx:2d}] {d['name']}{is_def}")
            print(f"       Channels: {d['max_input_channels']} | Default SR: {int(d['default_samplerate'])} Hz")
            in_count += 1

    if in_count == 0:
        print("  [ERROR] No microphone or audio input devices detected!")
    print("=======================================================\n")


def record_live_session(
    device: Optional[int],
    duration_secs: float,
    category: str,
    notes: str = "",
    output_dir: Path = config.DATA_DIR / "background" / "real"
) -> Optional[Path]:
    """
    Record continuous audio session from microphone, standardize to 16 kHz mono,
    verify integrity, and log session metadata.
    """
    if sd is None:
        print("[ERROR] sounddevice library is required for live recording.")
        return None

    if category not in VALID_CATEGORIES:
        print(f"[ERROR] Invalid category '{category}'. Must be one of:\n  {', '.join(VALID_CATEGORIES)}")
        return None

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    session_id = f"session_{category}_{timestamp}"
    filename = f"{session_id}.wav"
    dest_path = output_dir / filename

    print("\n=======================================================")
    print("        STARTING LIVE BACKGROUND RECORDING SESSION")
    print("=======================================================")
    print(f"  Category:       {category}")
    print(f"  Duration:       {duration_secs}s ({'Manual Ctrl+C' if duration_secs <= 0 else f'{duration_secs/60:.2f} min'})")
    print(f"  Device Index:   {device if device is not None else 'Default'}")
    print(f"  Destination:    {dest_path}")
    print(f"  Notes:          {notes}")
    print("=======================================================")

    sr = 16000
    channels = 1
    recorded_chunks = []

    def callback(indata, frames, time_info, status):
        if status:
            print(f"\n[Recording Warning] {status}", file=sys.stderr)
        recorded_chunks.append(indata[:, 0].copy())

    try:
        with sd.InputStream(
            samplerate=sr,
            channels=channels,
            dtype="float32",
            device=device,
            callback=callback
        ):
            print(f"\n[RECORDING IN PROGRESS] Listening and buffering audio... Press Ctrl+C to stop.")
            t0 = time.time()
            if duration_secs > 0:
                while time.time() - t0 < duration_secs:
                    elapsed = time.time() - t0
                    print(f"\r  Elapsed: {elapsed:5.1f}s / {duration_secs:5.1f}s [{int((elapsed/duration_secs)*100)}%]", end="", flush=True)
                    time.sleep(0.5)
            else:
                while True:
                    elapsed = time.time() - t0
                    print(f"\r  Elapsed: {elapsed:5.1f}s (Recording continuous stream...)", end="", flush=True)
                    time.sleep(0.5)

    except KeyboardInterrupt:
        print("\n\n[INFO] Recording stopped by user.")
    except Exception as e:
        print(f"\n[ERROR] Audio recording stream failed: {e}")
        return None

    if not recorded_chunks:
        print("\n[ERROR] No audio data recorded.")
        return None

    audio_data = np.concatenate(recorded_chunks, axis=0)
    actual_duration = len(audio_data) / sr

    # Save audio as 16 kHz 16-bit PCM WAV
    sf.write(str(dest_path), audio_data, sr, subtype="PCM_16")

    # Compute MD5
    file_hash = compute_file_hash(dest_path)

    session_record = {
        "session_id": session_id,
        "filename": filename,
        "file_path": str(dest_path),
        "category": category,
        "duration_seconds": round(actual_duration, 2),
        "duration_hours": round(actual_duration / 3600.0, 4),
        "sample_rate": sr,
        "channels": channels,
        "device_used": str(device) if device is not None else "default",
        "md5": file_hash,
        "created_at": datetime.datetime.now().isoformat(),
        "notes": notes
    }

    _update_sessions_manifest(session_record)

    print(f"\n[SUCCESS] Saved session recording:")
    print(f"  File:     {dest_path}")
    print(f"  Duration: {actual_duration:.2f}s ({actual_duration/60:.2f} minutes)")
    print(f"  MD5:      {file_hash}")
    print(f"  Manifest: data/background/sessions_manifest.json updated.")
    print("  Run `python audit_dataset.py --manifest --sync` to integrate into the dataset.")
    return dest_path


def import_existing_file(
    file_path: Path,
    category: str,
    notes: str = "",
    output_dir: Path = config.DATA_DIR / "background" / "real"
) -> Optional[Path]:
    """
    Import an existing external audio file (WAV, MP3, FLAC), validate, convert to 16 kHz mono,
    check for duplicate hashes, and register in sessions manifest.
    """
    file_path = Path(file_path)
    if not file_path.exists():
        print(f"[ERROR] Source file not found: {file_path}")
        return None

    if category not in VALID_CATEGORIES:
        print(f"[ERROR] Invalid category '{category}'. Must be one of:\n  {', '.join(VALID_CATEGORIES)}")
        return None

    try:
        wave = load_audio_mono_16k(file_path)
        actual_duration = len(wave) / 16000.0
    except Exception as e:
        print(f"[ERROR] Failed to load/decode audio file: {e}")
        return None

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    dest_name = f"imported_{category}_{file_path.stem}_{timestamp}.wav"
    dest_path = output_dir / dest_name

    sf.write(str(dest_path), wave, 16000, subtype="PCM_16")
    file_hash = compute_file_hash(dest_path)

    session_record = {
        "session_id": dest_name,
        "filename": dest_name,
        "file_path": str(dest_path),
        "category": category,
        "duration_seconds": round(actual_duration, 2),
        "duration_hours": round(actual_duration / 3600.0, 4),
        "sample_rate": 16000,
        "channels": 1,
        "device_used": "file_import",
        "md5": file_hash,
        "created_at": datetime.datetime.now().isoformat(),
        "notes": notes or f"Imported from {file_path.name}"
    }

    _update_sessions_manifest(session_record)

    print(f"\n[SUCCESS] Imported negative recording:")
    print(f"  Source:   {file_path}")
    print(f"  Saved To: {dest_path}")
    print(f"  Duration: {actual_duration:.2f}s ({actual_duration/60:.2f} min)")
    print(f"  MD5:      {file_hash}")
    return dest_path


def _update_sessions_manifest(record: Dict[str, Any]) -> None:
    """Append session metadata to sessions_manifest.json."""
    manifest_path = config.DATA_DIR / "background" / "sessions_manifest.json"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)

    sessions = []
    if manifest_path.exists():
        try:
            with open(manifest_path, "r", encoding="utf-8") as f:
                sessions = json.load(f)
        except Exception:
            sessions = []

    # Check duplicate MD5
    for s in sessions:
        if s.get("md5") == record["md5"]:
            print(f"  [NOTE] Recording already registered in sessions manifest ({s.get('session_id')}).")
            return

    sessions.append(record)
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(sessions, f, indent=2)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Record and ingest real-world background audio.")
    parser.add_argument("--list-devices", action="store_true", help="List audio input devices and exit")
    parser.add_argument("--device", type=int, default=None, help="Audio input device index")
    parser.add_argument("--duration", type=float, default=60.0, help="Recording duration in seconds (0 = manual stop with Ctrl+C)")
    parser.add_argument("--category", type=str, choices=VALID_CATEGORIES, default="quiet_room", help="Background sound category")
    parser.add_argument("--notes", type=str, default="", help="Description or environmental notes")
    parser.add_argument("--import-file", type=str, default=None, help="Path to an existing audio file to import as negative")
    args = parser.parse_args()

    if args.list_devices:
        list_recording_devices()
        sys.exit(0)

    if args.import_file:
        import_existing_file(Path(args.import_file), category=args.category, notes=args.notes)
    else:
        record_live_session(
            device=args.device,
            duration_secs=args.duration,
            category=args.category,
            notes=args.notes
        )
