"""
Generate Phase 20 Original Dataset Inventory
MANDATORY SAFETY DESIGNATION:
RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.

Catalogs the original ShotSpotter Pittsburgh PA DQV 2018 dataset files,
including the 20 selected tests across FP1-FP5, their sensor recordings,
survey metadata, pulses, and cryptographic checksums.
"""

import json
import hashlib
import soundfile as sf
import pandas as pd
from pathlib import Path

ROOT = Path("E:/gunshot/gunshot")
RAW_DIR = ROOT / "data" / "phase19_independent_positive" / "raw"
REPORTS_DIR = ROOT / "reports"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

COMMIT_SHA = "b0dc2840cf61c3c532756c01d49f636725c2b9ff"
RETRIEVAL_DATE = "2026-11-13 / 2026-11-14"
REPO_URL = "https://github.com/ShotSpotter/research.accuracy-of-gunshot-location"
LICENSE = "Creative Commons Attribution 4.0 International (CC BY 4.0)"
CREATOR = "ShotSpotter, Inc. & City of Pittsburgh Bureau of Police"

tests = [
    ("FP1", "test_001", "SCP-00-BNQ-1409"),
    ("FP1", "test_004", "SCP-00-BNQ-1120"),
    ("FP1", "test_007", "SCP-00-BNQ-1635"),
    ("FP1", "test_013", "SCP-00-BNG-5567"),
    ("FP2", "test_019", "SCP-00-BNQ-0559"),
    ("FP2", "test_022", "SCP-00-BNQ-0559"),
    ("FP2", "test_025", "SCP-00-BNQ-0559"),
    ("FP2", "test_031", "SCP-00-BNQ-0559"),
    ("FP3", "test_037", "SCP-00-BNQ-2143"),
    ("FP3", "test_040", "SCP-00-BNG-5545"),
    ("FP3", "test_043", "SCP-00-BNQ-2143"),
    ("FP3", "test_049", "SCP-00-BNQ-2143"),
    ("FP4", "test_055", "SCP-00-BNQ-1651"),
    ("FP4", "test_058", "SCP-00-BNG-5606"),
    ("FP4", "test_061", "SCP-00-BNG-5573"),
    ("FP4", "test_067", "SCP-00-BNQ-1705"),
    ("FP5", "test_127", "SCP-00-BNQ-1392"),
    ("FP5", "test_130", "SCP-00-BNQ-2167"),
    ("FP5", "test_133", "SCP-00-BNQ-0933"),
    ("FP5", "test_139", "SCP-00-BNQ-1493")
]

def sha256_of_file(filepath: Path) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

rows = []

for fp, tname, sn in tests:
    wav_file = RAW_DIR / f"{tname}.audio.{sn}.wav"
    meta_file = RAW_DIR / f"{tname}.audio.{sn}.json"
    survey_file = RAW_DIR / f"{tname}.survey.json"
    pulses_file = RAW_DIR / f"{tname}.allpulses.json"
    
    with open(survey_file, "r", encoding="utf-8") as f:
        s_data = json.load(f)
    with open(meta_file, "r", encoding="utf-8") as f:
        m_data = json.load(f)
    with open(pulses_file, "r", encoding="utf-8") as f:
        p_data = json.load(f)
        
    info = sf.info(wav_file)
    wav_sha = sha256_of_file(wav_file)
    meta_sha = sha256_of_file(meta_file)
    survey_sha = sha256_of_file(survey_file)
    pulses_sha = sha256_of_file(pulses_file)
    
    # Pulse metrics for this sensor
    sensor_pulses = [p for p in p_data if p["serial_number"] == sn]
    max_snr = max([p["signal_to_noise_dB"] for p in sensor_pulses]) if sensor_pulses else 0.0
    max_spl = max([p["power_dB_SPL"] for p in sensor_pulses]) if sensor_pulses else 0.0
    
    rows.append({
        "repository": "ShotSpotter/research.accuracy-of-gunshot-location",
        "commit_sha": COMMIT_SHA,
        "retrieval_date": RETRIEVAL_DATE,
        "campaign_id": "PittsburghPA_DQV_2018-12-18",
        "campaign_date": "2018-12-18 / 2018-12-19",
        "firing_position": fp,
        "test_id": tname,
        "test_sequence_index": s_data.get("test_id"),
        "firearm_label": s_data.get("firearm"),
        "rounds_ground_truth": s_data.get("num_rounds"),
        "sensor_serial_number": sn,
        "original_audio_filename": wav_file.name,
        "original_audio_sha256": wav_sha,
        "original_file_md5_header": m_data.get("original_file_md5", "N/A"),
        "file_size_bytes": wav_file.stat().st_size,
        "duration_seconds": info.duration,
        "sample_rate_hz": info.samplerate,
        "channels": info.channels,
        "format": f"{info.format} ({info.subtype})",
        "sensor_start_time_utc": m_data.get("timestamp"),
        "survey_approximate_time_utc": s_data.get("approximate_time_utc"),
        "survey_location_x": s_data.get("survey_location", {}).get("x"),
        "survey_location_y": s_data.get("survey_location", {}).get("y"),
        "survey_location_z": s_data.get("survey_location", {}).get("z"),
        "sensor_location_x": m_data.get("location", {}).get("x"),
        "sensor_location_y": m_data.get("location", {}).get("y"),
        "sensor_location_z": m_data.get("location", {}).get("z"),
        "coordinate_origin_type": "Arbitrary Cartesian Origin per Firing Position",
        "total_sensor_pulses": len(sensor_pulses),
        "sensor_max_snr_db": max_snr,
        "sensor_max_spl_db": max_spl,
        "license": LICENSE,
        "license_verified": True,
        "creator": CREATOR
    })

df = pd.DataFrame(rows)
out_csv = REPORTS_DIR / "phase20_original_dataset_inventory.csv"
df.to_csv(out_csv, index=False)
print(f"Original dataset inventory saved to {out_csv} ({len(df)} tests cataloged).")

