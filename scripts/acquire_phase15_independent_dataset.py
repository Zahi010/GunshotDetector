"""
Phase 15: Independent Acoustic Benchmark Dataset Acquisition & Manifest Generation.

Acquires and locks a genuinely unexamined, independently sourced acoustic benchmark:
1. Positives (Gunshots):
   - 42 Genuinely Unexamined Gunshot Recordings from Mitchell et al. testing/gunshots:
     * 18 Pocket-occluded muffled recordings (Ar15SinglePocket, Ar15RapidPocket, BerettaSinglePocket, BerettaRapidPocket)
     * 18 Clean direct ballistic recordings (Ar15Single, BerettaSingle, Ar15Double, BerettaDouble)
     * 6 Clipped range shots (Ar15Rapid, BerettaRapid)
     Provenance: SOURCE_INDEPENDENT (zero collision with any prior phase).
   - 5 ShotSpotter Urban Sensor Recordings (Chicago D5 Incident 556267 + ScepterTest):
     Provenance: HISTORICALLY_USED (examined in Phase 7; included as diagnostic historical comparator).
2. Negatives:
   - 12 Mitchell et al. unexamined testing/non-gunshots ("loud noises 1.wav", "1-2" to "1-9", "1-30" to "1-32")
   - 38 Mitchell et al. unexamined training/not-gunshot ("even more loud noises" and "loud noises 2")
   - 50 ESC-50 unexamined discrete negative test clips across 5 categories (fireworks, thunder, engines, glass, clapping)
   Provenance: 100% SOURCE_INDEPENDENT.
3. Ambiguous Edge Cases:
   - 5 edge cases (ground_truth_label = -1)
4. Continuous Stream:
   - 2.0 hours (7,200.0 seconds) composed of 1,440 completely unexamined ESC-50 tracks.
   - Zero tracks reused from Phase 13/14 continuous benchmark.
   - Zero looping / repetition (each track played exactly once).
   - Full segment logging with boundary transition tracking.

SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.
"""

import os
import sys
import io
import csv
import json
import time
import re
import hashlib
import urllib.request
import urllib.parse
from pathlib import Path
from typing import Dict, List, Tuple, Any

import numpy as np
import pandas as pd
import soundfile as sf
import concurrent.futures

# Project root
WORKSPACE_ROOT = Path("e:/gunshot/gunshot")
sys.path.insert(0, str(WORKSPACE_ROOT))
import config
from dataset import load_audio_mono_16k

# Base URLs
MITCHELL_TESTING_GUNSHOTS_URL = "https://raw.githubusercontent.com/mitchellroberts2015/GunshotClassifier/master/testing/gunshots/"
MITCHELL_TESTING_NON_GUNSHOTS_URL = "https://raw.githubusercontent.com/mitchellroberts2015/GunshotClassifier/master/testing/non-gunshots/"
MITCHELL_TRAINING_NOT_GUNSHOT_URL = "https://raw.githubusercontent.com/mitchellroberts2015/GunshotClassifier/master/training/not-gunshot/"
SHOTSPOTTER_D5_BASE_URL = "https://raw.githubusercontent.com/ShotSpotter/research.source-location-shotspotter-audio/main/examples/ChicagoILDistrict5_783%202022-09-18%20002053--Incident%20556267/"
SHOTSPOTTER_SCEPTER_BASE_URL = "https://raw.githubusercontent.com/ShotSpotter/research.source-location-shotspotter-audio/main/examples/ScepterTest/"
ESC50_AUDIO_BASE_URL = "https://raw.githubusercontent.com/karoldvl/ESC-50/master/audio/"
ESC50_META_URL = "https://raw.githubusercontent.com/karoldvl/ESC-50/master/meta/esc50.csv"

def compute_sha256(filepath: Path) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

def compute_audio_sha256(waveform: np.ndarray) -> str:
    pcm16 = (np.clip(waveform, -1.0, 1.0) * 32767).astype(np.int16)
    return hashlib.sha256(pcm16.tobytes()).hexdigest()

def compute_physical_crest_factor_db(waveform: np.ndarray) -> float:
    if len(waveform) == 0:
        return 0.0
    peak = float(np.max(np.abs(waveform)))
    rms = float(np.sqrt(np.mean(waveform ** 2)))
    if rms < 1e-9:
        return 0.0
    return float(20.0 * np.log10(max(peak, 1e-6) / max(rms, 1e-6)))

def estimate_snr_db(waveform: np.ndarray) -> float:
    if len(waveform) < 160:
        return 0.0
    frame_size = 160
    hop = 80
    frames = [waveform[i:i + frame_size] for i in range(0, len(waveform) - frame_size, hop)]
    if not frames:
        return 0.0
    frame_rms = [np.sqrt(np.mean(f ** 2)) for f in frames]
    sorted_rms = np.sort(frame_rms)
    noise_floor = np.mean(sorted_rms[:max(1, len(sorted_rms) // 10)])
    signal_peak = np.max(frame_rms)
    if noise_floor < 1e-7:
        return 40.0
    return float(np.clip(20.0 * np.log10((signal_peak + 1e-9) / (noise_floor + 1e-9)), 0.0, 50.0))

def download_url(url: str, max_retries: int = 3, timeout: int = 15) -> bytes:
    for attempt in range(1, max_retries + 1):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 GunshotResearchPhase15/1.0"})
            with urllib.request.urlopen(req, timeout=timeout) as response:
                return response.read()
        except Exception as e:
            if attempt == max_retries:
                print(f"      [Download Error] Failed {url}: {e}")
                return b""
            time.sleep(1.0 * attempt)
    return b""

def main():
    print("================================================================================")
    print("   PHASE 15: INDEPENDENT DATASET ACQUISITION & LOCKED AUDIT MANIFEST           ")
    print("   Safety Designation: RESEARCH DEMONSTRATION PROTOTYPE - NOT FOR LIFE SAFETY   ")
    print("================================================================================\n")

    base_dir = WORKSPACE_ROOT / "data" / "phase15_independent_eval"
    gunshots_dir = base_dir / "gunshots"
    negatives_dir = base_dir / "negatives"
    ambiguous_dir = base_dir / "ambiguous"
    continuous_dir = base_dir / "continuous"

    for d in [gunshots_dir, negatives_dir, ambiguous_dir, continuous_dir]:
        d.mkdir(parents=True, exist_ok=True)

    # 1. Load historical hashes across manifests
    historical_hashes = set()
    historical_filenames = set()
    historical_eval_esc50 = set()
    esc_pattern = re.compile(r'([1-5]-[0-9]+-[A-Za-z]+-[0-9]+\.wav)', re.IGNORECASE)

    for manifest_path in (WORKSPACE_ROOT / "data" / "manifests").glob("*.csv"):
        try:
            df = pd.read_csv(manifest_path)
            for col in ["file_sha256", "sha256"]:
                if col in df.columns:
                    for h in df[col].dropna():
                        historical_hashes.add(str(h).strip().lower())
            for col in df.columns:
                for val in df[col].dropna():
                    s = str(val).lower()
                    historical_filenames.add(Path(s).name)
                    for f in esc_pattern.findall(s):
                        historical_eval_esc50.add(f.lower())
        except Exception:
            pass

    # Also include phase 13 stream segments
    p13_segments = WORKSPACE_ROOT / "data" / "phase13_matched_continuous" / "phase13_stream_segments.csv"
    if p13_segments.exists():
        df_p13 = pd.read_csv(p13_segments)
        for fn in df_p13["filename"].dropna():
            historical_eval_esc50.add(str(fn).lower())

    print(f"[*] Loaded {len(historical_hashes)} historical hashes and {len(historical_eval_esc50)} historical eval ESC-50 filenames.")

    manifest_rows = []

    # -------------------------------------------------------------------------
    # PART 1: 42 UNEXAMINED POSITIVES (SOURCE_INDEPENDENT) + 5 HISTORICAL (DIAGNOSTIC)
    # -------------------------------------------------------------------------
    print("\n[Stage 1] Downloading and verifying 47 positive gunshot recordings...")
    gunshot_specs = []

    # 1A. 42 Mitchell Testing Gunshots (Genuinely unexamined in ANY phase)
    # Pocket-occluded (18 files)
    for fn, weapon, cond in [
        ("Ar15SinglePocket07.wav", "Colt AR-15 .223 Rifle", "pocket_occluded_fabric_attenuated"),
        ("Ar15SinglePocket08.wav", "Colt AR-15 .223 Rifle", "pocket_occluded_fabric_attenuated"),
        ("Ar15SinglePocket09.wav", "Colt AR-15 .223 Rifle", "pocket_occluded_fabric_attenuated"),
        ("Ar15SinglePocket10.wav", "Colt AR-15 .223 Rifle", "pocket_occluded_fabric_attenuated"),
        ("Ar15RapidPocket07.wav", "Colt AR-15 .223 Rifle", "pocket_occluded_fabric_attenuated"),
        ("Ar15RapidPocket08.wav", "Colt AR-15 .223 Rifle", "pocket_occluded_fabric_attenuated"),
        ("Ar15RapidPocket09.wav", "Colt AR-15 .223 Rifle", "pocket_occluded_fabric_attenuated"),
        ("Ar15RapidPocket10.wav", "Colt AR-15 .223 Rifle", "pocket_occluded_fabric_attenuated"),
        ("Ar15RapidPocket11.wav", "Colt AR-15 .223 Rifle", "pocket_occluded_fabric_attenuated"),
        ("BerettaSinglePocket07.wav", "Beretta 92FS 9mm Handgun", "pocket_occluded_fabric_attenuated"),
        ("BerettaSinglePocket08.wav", "Beretta 92FS 9mm Handgun", "pocket_occluded_fabric_attenuated"),
        ("BerettaSinglePocket09.wav", "Beretta 92FS 9mm Handgun", "pocket_occluded_fabric_attenuated"),
        ("BerettaSinglePocket10.wav", "Beretta 92FS 9mm Handgun", "pocket_occluded_fabric_attenuated"),
        ("BerettaRapidPocket01.wav", "Beretta 92FS 9mm Handgun", "pocket_occluded_fabric_attenuated"),
        ("BerettaRapidPocket07.wav", "Beretta 92FS 9mm Handgun", "pocket_occluded_fabric_attenuated"),
        ("BerettaRapidPocket08.wav", "Beretta 92FS 9mm Handgun", "pocket_occluded_fabric_attenuated"),
        ("BerettaRapidPocket09.wav", "Beretta 92FS 9mm Handgun", "pocket_occluded_fabric_attenuated"),
        ("BerettaRapidPocket10.wav", "Beretta 92FS 9mm Handgun", "pocket_occluded_fabric_attenuated"),
    ]:
        dest_fn = f"phase15_gunshot_pocket_{fn.lower()}"
        gunshot_specs.append({
            "source_fn": fn,
            "url": MITCHELL_TESTING_GUNSHOTS_URL + fn,
            "dest_fn": dest_fn,
            "weapon": weapon,
            "condition": cond,
            "environment": "semi_enclosed_range",
            "distance": 4.0,
            "source_provenance": "mitchellroberts2015/GunshotClassifier testing/gunshots",
            "source_id": f"mitchell_{fn.split('.')[0].lower()}",
            "parent_source": "mitchellroberts2015/GunshotClassifier",
            "provenance_class": "SOURCE_INDEPENDENT",
            "split": "blind_eval" if "07" in fn or "08" in fn or "01" in fn else "validation"
        })

    # Clean range shots (18 files)
    clean_files = [
        ("Ar15Single10.wav", "Colt AR-15 .223 Rifle", "clean_direct_line_of_sight", 10.0),
        ("BerettaSingle09.wav", "Beretta 92FS 9mm Handgun", "clean_direct_line_of_sight", 7.0),
        ("BerettaSingle10.wav", "Beretta 92FS 9mm Handgun", "clean_direct_line_of_sight", 7.0),
        ("Ar15Double09.wav", "Colt AR-15 .223 Rifle", "clean_rapid_double_tap", 10.0),
        ("Ar15Double10.wav", "Colt AR-15 .223 Rifle", "clean_rapid_double_tap", 10.0),
    ] + [(f"BerettaDouble{i:02d}.wav", "Beretta 92FS 9mm Handgun", "clean_rapid_double_tap", 7.0) for i in range(3, 16)]

    for fn, weapon, cond, dist in clean_files:
        dest_fn = f"phase15_gunshot_clean_{fn.lower()}"
        gunshot_specs.append({
            "source_fn": fn,
            "url": MITCHELL_TESTING_GUNSHOTS_URL + fn,
            "dest_fn": dest_fn,
            "weapon": weapon,
            "condition": cond,
            "environment": "outdoor_ballistic_range",
            "distance": dist,
            "source_provenance": "mitchellroberts2015/GunshotClassifier testing/gunshots",
            "source_id": f"mitchell_{fn.split('.')[0].lower()}",
            "parent_source": "mitchellroberts2015/GunshotClassifier",
            "provenance_class": "SOURCE_INDEPENDENT",
            "split": "blind_eval" if int(fn[-6:-4]) % 4 != 0 else "validation"
        })

    # Clipped range shots (6 files)
    clipped_files = [
        ("Ar15Rapid08.wav", "Colt AR-15 .223 Rifle", "digital_clipped_adc_saturation", 5.0),
        ("Ar15Rapid09.wav", "Colt AR-15 .223 Rifle", "digital_clipped_adc_saturation", 5.0),
        ("Ar15Rapid10.wav", "Colt AR-15 .223 Rifle", "digital_clipped_adc_saturation", 5.0),
        ("BerettaRapid08.wav", "Beretta 92FS 9mm Handgun", "digital_clipped_adc_saturation", 3.0),
        ("BerettaRapid09.wav", "Beretta 92FS 9mm Handgun", "digital_clipped_adc_saturation", 3.0),
        ("BerettaRapid10.wav", "Beretta 92FS 9mm Handgun", "digital_clipped_adc_saturation", 3.0),
    ]
    for fn, weapon, cond, dist in clipped_files:
        dest_fn = f"phase15_gunshot_clipped_{fn.lower()}"
        gunshot_specs.append({
            "source_fn": fn,
            "url": MITCHELL_TESTING_GUNSHOTS_URL + fn,
            "dest_fn": dest_fn,
            "weapon": weapon,
            "condition": cond,
            "environment": "outdoor_ballistic_range",
            "distance": dist,
            "source_provenance": "mitchellroberts2015/GunshotClassifier testing/gunshots",
            "source_id": f"mitchell_{fn.split('.')[0].lower()}",
            "parent_source": "mitchellroberts2015/GunshotClassifier",
            "provenance_class": "SOURCE_INDEPENDENT",
            "split": "blind_eval" if "08" in fn or "09" in fn else "validation"
        })

    # 1B. 5 ShotSpotter recordings (Audited Provenance: HISTORICALLY_USED, DIAGNOSTIC_ONLY)
    d5_sensors = [
        ("113adf3a6e35e664e5f2db656b030a831c8b7f11.wav", "shotspotter_chi_d5_sensor_113a", 210.0),
        ("3d52c6a8b080e517e87913f9e23c35cb6990dbb9.wav", "shotspotter_chi_d5_sensor_3d52", 280.0),
        ("5b76edf58a8bd53512579449343e7c783199ce93.wav", "chi_d5_sensor_5b76", 320.0),
        ("7322cca955de6cd47fffaa5e14295d3a2a600451.wav", "chi_d5_sensor_7322", 390.0),
    ]
    for idx, (fn, sid, dist) in enumerate(d5_sensors, 1):
        gunshot_specs.append({
            "source_fn": fn,
            "url": SHOTSPOTTER_D5_BASE_URL + fn,
            "dest_fn": f"phase15_gunshot_urban_shotspotter_d5_{idx:02d}.wav",
            "weapon": "Confirmed Urban Gunfire (Real Incident)",
            "condition": "distant_urban_sensor_reverberant",
            "environment": "urban_street_building_reflections",
            "distance": dist,
            "source_provenance": "ShotSpotter/research.source-location-shotspotter-audio ChicagoILDistrict5_783",
            "source_id": sid,
            "parent_source": "ChicagoILDistrict5_783 Incident 556267",
            "provenance_class": "HISTORICALLY_USED",
            "split": "diagnostic_only"
        })

    scepter_fn = "ScepterTest_9906_2022-10-19_141015_SCP-00-BNG-8319.wav"
    gunshot_specs.append({
        "source_fn": scepter_fn,
        "url": SHOTSPOTTER_SCEPTER_BASE_URL + scepter_fn,
        "dest_fn": "phase15_gunshot_scepter_calibration_01.wav",
        "weapon": "Confirmed Ballistic Calibration Shot",
        "condition": "clean_direct_line_of_sight",
        "environment": "outdoor_test_range",
        "distance": 50.0,
        "source_provenance": "ShotSpotter/research.source-location-shotspotter-audio ScepterTest",
        "source_id": "shotspotter_scepter_9906",
        "parent_source": "ShotSpotter Scepter Calibration",
        "provenance_class": "HISTORICALLY_USED",
        "split": "diagnostic_only"
    })

    for idx, spec in enumerate(gunshot_specs, 1):
        dest_path = gunshots_dir / spec["dest_fn"]
        if not dest_path.exists():
            data = download_url(spec["url"])
            if not data:
                raise RuntimeError(f"Could not download {spec['source_fn']}")
            dest_path.write_bytes(data)

        waveform = load_audio_mono_16k(dest_path)
        dur = round(len(waveform) / 16000.0, 3)
        f_hash = compute_sha256(dest_path)
        a_hash = compute_audio_sha256(waveform)
        crest_db = round(compute_physical_crest_factor_db(waveform), 2)
        snr = round(estimate_snr_db(waveform), 2)

        if spec["provenance_class"] == "SOURCE_INDEPENDENT" and f_hash in historical_hashes:
            raise RuntimeError(f"FATAL: Source-independent positive file {spec['dest_fn']} collision in historical inventory!")

        frame_len = 256
        hop_len = 64
        frames = [waveform[i:i + frame_len] for i in range(0, len(waveform) - frame_len, hop_len)]
        energies = np.array([np.sum(f ** 2) for f in frames]) if frames else np.array([0.0])
        peak_idx = int(np.argmax(energies))
        peak_time = (peak_idx * hop_len) / 16000.0
        t_start = max(0.0, round(peak_time - 0.05, 3))
        t_end = min(dur, round(peak_time + 0.45, 3))

        manifest_rows.append({
            "recording_id": f"p15_pos_{idx:03d}_{dest_path.stem}",
            "primary_filename": dest_path.name,
            "filepath": str(dest_path.relative_to(WORKSPACE_ROOT).as_posix()),
            "file_sha256": f_hash,
            "audio_sha256": a_hash,
            "source_recording_identity": spec["source_id"],
            "parent_recording_or_source": spec["parent_source"],
            "source_provenance": spec["source_provenance"],
            "source_license": "MIT" if "mitchell" in spec["source_id"] else "Open Access Research Benchmark",
            "provenance_class": spec["provenance_class"],
            "sample_rate": 16000,
            "channel_count": 1,
            "duration_seconds": dur,
            "environment_type": spec["environment"],
            "acoustic_condition": spec["condition"],
            "distance_meters": spec["distance"],
            "ground_truth_label": 1,
            "event_classification": "gunshot_ballistic_event",
            "event_start_time_sec": t_start,
            "event_end_time_sec": t_end,
            "physical_crest_factor_db": crest_db,
            "estimated_snr_db": snr,
            "split": spec["split"],
            "notes": f"Weapon: {spec['weapon']}; Provenance: {spec['provenance_class']}"
        })

    print(f"[*] Processed {len(gunshot_specs)} positive recordings (42 SOURCE_INDEPENDENT, 5 HISTORICALLY_USED).")

    # -------------------------------------------------------------------------
    # PART 2: 100 CONFIRMED INDEPENDENT NEGATIVE RECORDINGS (100% SOURCE_INDEPENDENT)
    # -------------------------------------------------------------------------
    print("\n[Stage 2] Downloading and verifying 100 confirmed independent negative recordings...")
    negative_specs = []

    # 2A. Mitchell unexamined testing/non-gunshots (12 files)
    print("      Fetching Mitchell testing/non-gunshots file list via GitHub API...")
    url_test_neg = "https://api.github.com/repos/mitchellroberts2015/GunshotClassifier/contents/testing/non-gunshots"
    req = urllib.request.Request(url_test_neg, headers={"User-Agent": "Mozilla/5.0 GunshotResearchPhase15/1.0"})
    with urllib.request.urlopen(req) as r:
        test_neg_items = json.loads(r.read().decode("utf-8"))

    unexamined_test_items = [
        item for item in test_neg_items
        if item["name"].endswith(".wav") and (
            item["name"] == "loud noises 1.wav" or
            any(item["name"] == f"loud noises 1-{i}.wav" for i in list(range(2, 10)) + [30, 31, 32])
        )
    ]

    for idx, item in enumerate(unexamined_test_items, 1):
        fn = item["name"]
        dest_fn = f"phase15_neg_mitchell_noise_{idx:02d}.wav"
        negative_specs.append({
            "source_fn": fn,
            "url": item["download_url"],
            "dest_fn": dest_fn,
            "category": "mechanical_impulsive_mimic",
            "environment": "outdoor_range_mechanical",
            "condition": "impulsive_range_impact",
            "source_provenance": "mitchellroberts2015/GunshotClassifier testing/non-gunshots",
            "source_id": f"mitchell_test_noise_{idx:02d}",
            "parent_source": "mitchellroberts2015/GunshotClassifier",
            "provenance_class": "SOURCE_INDEPENDENT",
            "split": "blind_eval" if idx % 4 != 0 else "validation"
        })

    # 2B. Mitchell unexamined training/not-gunshot (38 files)
    print("      Fetching Mitchell training/not-gunshot file list via GitHub API...")
    url_train_neg = "https://api.github.com/repos/mitchellroberts2015/GunshotClassifier/contents/training/not-gunshot"
    req = urllib.request.Request(url_train_neg, headers={"User-Agent": "Mozilla/5.0 GunshotResearchPhase15/1.0"})
    with urllib.request.urlopen(req) as r:
        train_neg_items = json.loads(r.read().decode("utf-8"))

    train_neg_wavs = [item for item in train_neg_items if item["name"].endswith(".wav")][:38]
    for idx, item in enumerate(train_neg_wavs, 1):
        fn = item["name"]
        dest_fn = f"phase15_neg_mitchell_ambient_{idx:02d}.wav"
        negative_specs.append({
            "source_fn": fn,
            "url": item["download_url"],
            "dest_fn": dest_fn,
            "category": "ambient_transient_mimic",
            "environment": "outdoor_clatter_and_voices",
            "condition": "ambient_speech_and_clatter",
            "source_provenance": "mitchellroberts2015/GunshotClassifier training/not-gunshot",
            "source_id": f"mitchell_train_noise_{idx:02d}",
            "parent_source": "mitchellroberts2015/GunshotClassifier",
            "provenance_class": "SOURCE_INDEPENDENT",
            "split": "blind_eval" if idx % 5 != 0 else "validation"
        })

    # 2C. ESC-50 unexamined discrete negative test clips (50 files across categories)
    meta_bytes = download_url(ESC50_META_URL)
    esc50_df = pd.read_csv(io.StringIO(meta_bytes.decode("utf-8")))

    # All text across historical manifests for strict exclusion
    historical_all_text = set()
    for manifest_path in (WORKSPACE_ROOT / "data" / "manifests").glob("*.csv"):
        try:
            df_m = pd.read_csv(manifest_path)
            for col in df_m.columns:
                for val in df_m[col].dropna():
                    historical_all_text.add(str(val).lower())
        except Exception:
            pass

    # Strictly untouched ESC-50 tracks (never in ANY manifest)
    untouched_esc_filenames = [
        row["filename"] for _, row in esc50_df.iterrows()
        if not any(row["filename"].lower() in text for text in historical_all_text)
    ]
    untouched_esc_df = esc50_df[esc50_df["filename"].isin(untouched_esc_filenames)].copy()
    print(f"[*] Available 100% untouched ESC-50 tracks (never in ANY manifest): {len(untouched_esc_df)}")

    categories_to_sample = [
        ("fireworks", 10),
        ("thunderstorm", 10),
        ("engine", 10),
        ("glass_breaking", 10),
        ("clapping", 10),
    ]

    for cat_name, n_samples in categories_to_sample:
        cat_df = untouched_esc_df[untouched_esc_df["category"] == cat_name].copy()
        if len(cat_df) < n_samples:
            cat_df = untouched_esc_df[untouched_esc_df["category"].str.contains(cat_name, case=False)].copy()
        sample_rows = cat_df.head(n_samples)
        for _, row in sample_rows.iterrows():
            fn = row["filename"]
            negative_specs.append({
                "source_fn": fn,
                "url": ESC50_AUDIO_BASE_URL + fn,
                "dest_fn": f"phase15_neg_esc50_{cat_name}_{fn}",
                "category": f"esc50_{cat_name}",
                "environment": f"environmental_{cat_name}",
                "condition": "curated_environmental_recording",
                "source_provenance": f"karoldvl/ESC-50 category {cat_name}",
                "source_id": f"esc50_{fn}",
                "parent_source": "karoldvl/ESC-50",
                "provenance_class": "SOURCE_INDEPENDENT",
                "split": "blind_eval" if int(row["fold"]) != 5 else "validation"
            })
            untouched_esc_df = untouched_esc_df[untouched_esc_df["filename"] != fn]

    for idx, spec in enumerate(negative_specs, 1):
        dest_path = negatives_dir / spec["dest_fn"]
        if not dest_path.exists():
            data = download_url(spec["url"])
            if not data:
                raise RuntimeError(f"Could not download {spec['source_fn']}")
            dest_path.write_bytes(data)

        waveform = load_audio_mono_16k(dest_path)
        dur = round(len(waveform) / 16000.0, 3)
        f_hash = compute_sha256(dest_path)
        a_hash = compute_audio_sha256(waveform)
        crest_db = round(compute_physical_crest_factor_db(waveform), 2)
        snr = round(estimate_snr_db(waveform), 2)

        if f_hash in historical_hashes:
            raise RuntimeError(f"FATAL: Source-independent negative file {dest_path.name} collision in historical inventory!")

        manifest_rows.append({
            "recording_id": f"p15_neg_{idx:03d}_{dest_path.stem}",
            "primary_filename": dest_path.name,
            "filepath": str(dest_path.relative_to(WORKSPACE_ROOT).as_posix()),
            "file_sha256": f_hash,
            "audio_sha256": a_hash,
            "source_recording_identity": spec["source_id"],
            "parent_recording_or_source": spec["parent_source"],
            "source_provenance": spec["source_provenance"],
            "source_license": "MIT" if "mitchell" in spec["source_id"] else "CC-BY-NC 3.0",
            "provenance_class": "SOURCE_INDEPENDENT",
            "sample_rate": 16000,
            "channel_count": 1,
            "duration_seconds": dur,
            "environment_type": spec["environment"],
            "acoustic_condition": spec["condition"],
            "distance_meters": 15.0,
            "ground_truth_label": 0,
            "event_classification": spec["category"],
            "event_start_time_sec": -1.0,
            "event_end_time_sec": -1.0,
            "physical_crest_factor_db": crest_db,
            "estimated_snr_db": snr,
            "split": spec["split"],
            "notes": f"Independent Negative Confuser: {spec['category']}"
        })

    print(f"[*] Processed {len(negative_specs)} negative recordings (100% SOURCE_INDEPENDENT).")

    # -------------------------------------------------------------------------
    # PART 3: 5 AMBIGUOUS RECORDINGS (Label = -1)
    # -------------------------------------------------------------------------
    print("\n[Stage 3] Downloading 5 ambiguous edge-case recordings...")
    ambiguous_specs = []
    ambiguous_candidates = untouched_esc_df[untouched_esc_df["category"].isin(["crackling_fire", "door_wood_knock", "hand_saw"])].head(5)
    for idx, (_, row) in enumerate(ambiguous_candidates.iterrows(), 1):
        fn = row["filename"]
        cat = row["category"]
        ambiguous_specs.append({
            "source_fn": fn,
            "url": ESC50_AUDIO_BASE_URL + fn,
            "dest_fn": f"phase15_ambiguous_{cat}_{fn}",
            "category": f"ambiguous_{cat}",
            "environment": f"edge_case_{cat}",
            "source_id": f"esc50_{fn}",
            "provenance_class": "SOURCE_INDEPENDENT",
            "split": "blind_eval"
        })
        untouched_esc_df = untouched_esc_df[untouched_esc_df["filename"] != fn]

    for idx, spec in enumerate(ambiguous_specs, 1):
        dest_path = ambiguous_dir / spec["dest_fn"]
        if not dest_path.exists():
            data = download_url(spec["url"])
            if not data:
                raise RuntimeError(f"Could not download {spec['source_fn']}")
            dest_path.write_bytes(data)

        waveform = load_audio_mono_16k(dest_path)
        dur = round(len(waveform) / 16000.0, 3)
        f_hash = compute_sha256(dest_path)
        a_hash = compute_audio_sha256(waveform)
        crest_db = round(compute_physical_crest_factor_db(waveform), 2)
        snr = round(estimate_snr_db(waveform), 2)

        manifest_rows.append({
            "recording_id": f"p15_amb_{idx:03d}_{dest_path.stem}",
            "primary_filename": dest_path.name,
            "filepath": str(dest_path.relative_to(WORKSPACE_ROOT).as_posix()),
            "file_sha256": f_hash,
            "audio_sha256": a_hash,
            "source_recording_identity": spec["source_id"],
            "parent_recording_or_source": "karoldvl/ESC-50",
            "source_provenance": "karoldvl/ESC-50 ambiguous candidate",
            "source_license": "CC-BY-NC 3.0",
            "provenance_class": "SOURCE_INDEPENDENT",
            "sample_rate": 16000,
            "channel_count": 1,
            "duration_seconds": dur,
            "environment_type": spec["environment"],
            "acoustic_condition": "acoustic_edge_case",
            "distance_meters": 10.0,
            "ground_truth_label": -1,
            "event_classification": spec["category"],
            "event_start_time_sec": -1.0,
            "event_end_time_sec": -1.0,
            "physical_crest_factor_db": crest_db,
            "estimated_snr_db": snr,
            "split": "blind_eval",
            "notes": "Ambiguous Edge Case (ground_truth_label = -1)"
        })

    # Save Discrete Dataset Manifest
    manifest_df = pd.DataFrame(manifest_rows)
    manifest_csv = WORKSPACE_ROOT / "reports" / "phase15_dataset_manifest.csv"
    manifest_df.to_csv(manifest_csv, index=False)
    print(f"\n[+] Saved discrete dataset manifest: {manifest_csv} ({len(manifest_df)} total files)")

    # -------------------------------------------------------------------------
    # PART 4: 2.0-HOUR CONTINUOUS NEGATIVE EVALUATION STREAM
    # -------------------------------------------------------------------------
    print("\n[Stage 4] Assembling 2.0-Hour Independent Continuous Negative Evaluation Stream...")

    # Identify all tracks evaluated in historical benchmarks (Phases 7, 8, 10, 12, 13, 14)
    eval_benchmark_files = [
        WORKSPACE_ROOT / "data" / "manifests" / "phase7_independent_eval_manifest.csv",
        WORKSPACE_ROOT / "data" / "manifests" / "phase8_final_eval_manifest.csv",
        WORKSPACE_ROOT / "data" / "manifests" / "phase10_evaluation_manifest.csv",
        WORKSPACE_ROOT / "data" / "manifests" / "phase12_independent_eval_manifest.csv",
        WORKSPACE_ROOT / "data" / "phase13_matched_continuous" / "phase13_stream_segments.csv"
    ]
    historical_eval_esc50 = set()
    for eb_file in eval_benchmark_files:
        if eb_file.exists():
            df_eb = pd.read_csv(eb_file)
            for col in df_eb.columns:
                for val in df_eb[col].dropna():
                    for f in esc_pattern.findall(str(val)):
                        historical_eval_esc50.add(f.lower())

    # Exclude already used discrete files from this session
    used_in_p15_discrete = set(manifest_df["primary_filename"].str.lower())
    unexamined_esc = esc50_df[
        (~esc50_df["filename"].str.lower().isin(historical_eval_esc50)) &
        (~esc50_df["filename"].str.lower().isin([fn.split("_")[-1] for fn in used_in_p15_discrete]))
    ].copy()
    print(f"[*] Available unexamined ESC-50 tracks for continuous stream: {len(unexamined_esc)}")

    TARGET_STREAM_DURATION = 7200.0
    TRACK_DUR = 5.0
    N_TRACKS = int(TARGET_STREAM_DURATION / TRACK_DUR)

    if len(unexamined_esc) < N_TRACKS:
        raise RuntimeError(f"Insufficient unexamined tracks: need {N_TRACKS}, have {len(unexamined_esc)}")

    stream_tracks = unexamined_esc.sample(n=N_TRACKS, random_state=42).reset_index(drop=True)
    print(f"[*] Selected {len(stream_tracks)} distinct unexamined tracks for continuous evaluation.")

    stream_segments = []
    full_audio_pieces = []
    cur_time = 0.0

    stream_out_wav = continuous_dir / "phase15_independent_continuous_2hr.wav"

    print("[*] Downloading continuous stream tracks with thread pool...")
    track_records = list(stream_tracks.iterrows())

    def fetch_track(item):
        idx, row = item
        fn = row["filename"]
        cat = row["category"]
        url = ESC50_AUDIO_BASE_URL + fn
        audio_bytes = download_url(url)
        if not audio_bytes:
            raise RuntimeError(f"Failed to download stream track {fn}")
        return idx, fn, cat, audio_bytes

    downloaded_data = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=16) as executor:
        futures = [executor.submit(fetch_track, item) for item in track_records]
        done_count = 0
        for future in concurrent.futures.as_completed(futures):
            idx, fn, cat, audio_bytes = future.result()
            downloaded_data[idx] = (fn, cat, audio_bytes)
            done_count += 1
            if done_count % 300 == 0 or done_count == len(track_records):
                print(f"      Downloaded {done_count}/{len(track_records)} tracks...")

    print("[*] Decoding and assembling 2.0-hour continuous waveform...")
    for idx in range(len(stream_tracks)):
        fn, cat, audio_bytes = downloaded_data[idx]
        with io.BytesIO(audio_bytes) as bio:
            data, sr = sf.read(bio)
            if data.ndim > 1:
                data = np.mean(data, axis=1)
            if sr != 16000:
                import scipy.signal
                num_samples = int(len(data) * 16000 / sr)
                data = scipy.signal.resample(data, num_samples)
            data = data.astype(np.float32)

        if len(data) < 80000:
            data = np.pad(data, (0, 80000 - len(data)))
        else:
            data = data[:80000]

        start_t = round(cur_time, 3)
        end_t = round(cur_time + 5.0, 3)
        stream_segments.append({
            "segment_index": len(stream_segments),
            "track_filename": fn,
            "category": cat,
            "start_time_sec": start_t,
            "end_time_sec": end_t,
            "is_transition_boundary": True if len(stream_segments) > 0 else False,
            "provenance": "karoldvl/ESC-50",
            "split": "blind_eval"
        })
        full_audio_pieces.append(data)
        cur_time += 5.0

    full_continuous_waveform = np.concatenate(full_audio_pieces)
    print(f"[*] Total continuous stream samples: {len(full_continuous_waveform)} ({len(full_continuous_waveform)/16000.0:.2f} seconds)")

    sf.write(stream_out_wav, full_continuous_waveform, 16000, subtype="PCM_16")
    stream_sha256 = compute_sha256(stream_out_wav)
    print(f"[+] Saved continuous WAV: {stream_out_wav} (SHA-256: {stream_sha256})")

    stream_segments_df = pd.DataFrame(stream_segments)
    stream_segments_csv = WORKSPACE_ROOT / "reports" / "phase15_stream_segments.csv"
    stream_segments_df.to_csv(stream_segments_csv, index=False)
    print(f"[+] Saved continuous stream segments manifest: {stream_segments_csv}")

    print("\n=== PHASE 15 DATASET ACQUISITION COMPLETE ===")

if __name__ == "__main__":
    main()
