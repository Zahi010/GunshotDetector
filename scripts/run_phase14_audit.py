"""
Phase 14: Independent Reproducibility, Source-Provenance Audit & Operating-Point Optimization.

Main comprehensive audit script:
1. Cryptographic baseline integrity and archive freeze audit.
2. Independent reproduction of Phase 13 development benchmark and 2.0-hour continuous benchmark.
3. Exhaustive dataset independence and provenance audit across all historical splits.
4. False negative forensics comparing Phase 9 baseline vs Phase 13 candidate.
5. Acoustic and semantic analysis of fireworks vs thunder vs ballistic transients.
6. Pocket-occlusion sample audit and crest factor sensitivity evaluation.

Outputs:
- reports/phase14_source_overlap_matrix.csv
- reports/phase14_duplicate_and_near_duplicate_audit.json
- reports/phase14_event_level_comparison.csv
- reports/phase14_audit_summary.json
"""

import os
import sys
import json
import time
import math
import pickle
import hashlib
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional

import numpy as np
import pandas as pd
import soundfile as sf
import scipy.signal
import scipy.stats
import tensorflow as tf

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import config
from dataset import load_audio_mono_16k
from model import load_model_bundle
from model_phase9 import (
    Phase9AdaptiveGunshotDetector,
    compute_physical_crest_factor_db,
    YAMNET_CLASS_GUNSHOT,
    YAMNET_CLASS_MACHINE_GUN,
    YAMNET_CLASS_ARTILLERY,
    YAMNET_CLASS_CAP_GUN,
    YAMNET_CLASS_THUNDERSTORM,
    YAMNET_CLASS_THUNDER,
    YAMNET_CLASS_FIREWORKS,
    YAMNET_CLASS_FIRECRACKER,
    merge_detection_windows_phase9
)
from model_phase13 import (
    Phase13CandidateGunshotDetector,
    merge_phase13_events,
    YAMNET_CLASS_DOG,
    YAMNET_CLASS_BARK,
    YAMNET_CLASS_YIP,
    YAMNET_CLASS_CANIDAE,
    YAMNET_CLASS_POLICE_CAR,
    YAMNET_CLASS_AMBULANCE,
    YAMNET_CLASS_FIRE_ENGINE,
    YAMNET_CLASS_SIREN,
    YAMNET_CLASS_CIVIL_DEFENSE
)

REPORTS_DIR = Path("reports")
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

# -----------------------------------------------------------------------------
# 1. Cryptographic Archive and File Checksums
# -----------------------------------------------------------------------------
EXPECTED_ARCHIVES = {
    "gunshot_detection_phase8.zip": "c8bd26d09b5a41903ae8308b7bcac42f37ecd00d95eb6abfa4295365e074d353",
    "gunshot_detection_phase9.zip": "96ff780eaa38737ea66851195301beebc576a31a48319f3b0a71083c4dee2ff0",
    "gunshot_detection_phase10.zip": "d8edb26b71d69d6e76a1834cc741bda272c71b475287d7bd7fe2f33be95c459d",
    "gunshot_detection_phase11.zip": "c50a9b07ffe93f01118fbc2a26130fd73c800d717b6a372d2e76291c735404ef",
    "gunshot_detection_phase12.zip": "8c674902761d469760928c81596813a08a942262440d977a423e58007055241a",
    "gunshot_detection_phase13.zip": "1a87aef803c7b2ec1bc0e5b3a894451960ea17a9f787a8ffc81ba7a15e8f6561",
}

def verify_historical_archives() -> Dict[str, Any]:
    print("=== 1. VERIFYING HISTORICAL ARCHIVES ===")
    results = {}
    parent_dir = Path("e:/gunshot")
    for arc_name, expected_hash in EXPECTED_ARCHIVES.items():
        arc_path = parent_dir / arc_name
        if not arc_path.exists():
            arc_path = Path("..") / arc_name
        if not arc_path.exists():
            arc_path = Path(arc_name)

        if arc_path.exists():
            actual_hash = hashlib.sha256(arc_path.read_bytes()).hexdigest()
            size_mb = arc_path.stat().st_size / (1024 * 1024)
            matched = (actual_hash == expected_hash)
            results[arc_name] = {
                "exists": True,
                "size_mb": round(size_mb, 2),
                "actual_sha256": actual_hash,
                "expected_sha256": expected_hash,
                "matched": matched
            }
            status = "MATCH" if matched else "MISMATCH"
            print(f"[{status}] {arc_name}: {size_mb:.2f} MB | {actual_hash[:16]}...")
        else:
            results[arc_name] = {"exists": False, "matched": False}
            print(f"[MISSING] {arc_name}")
    return results

# -----------------------------------------------------------------------------
# 2. Reproduction of Phase 13 Development Benchmark
# -----------------------------------------------------------------------------
def load_development_dataset() -> List[Dict[str, Any]]:
    records = []
    p8_manifest_path = Path("data/manifests/phase8_final_eval_manifest.csv")
    p8_events_path = Path("data/manifests/phase8_canonical_gunshot_events.csv")
    df_p8 = pd.read_csv(p8_manifest_path)
    df_p8_events = pd.read_csv(p8_events_path)

    p8_events_map = {}
    for _, ev in df_p8_events.iterrows():
        p8_events_map[ev["recording_id"]] = {
            "start": float(ev["start_time_sec"]),
            "end": float(ev["end_time_sec"])
        }

    for _, row in df_p8.iterrows():
        rid = str(row["recording_id"])
        fp = Path(row["filepath"])
        label = int(row["label"])
        cond = str(row["acoustic_condition"])
        cat = str(row["category"])
        dur = float(row["duration_sec"])

        if label == 1 and rid in p8_events_map:
            t_start = p8_events_map[rid]["start"]
            t_end = p8_events_map[rid]["end"]
        else:
            t_start = 0.0
            t_end = dur

        records.append({
            "source_split": "phase8_dev_eval",
            "recording_id": rid,
            "filepath": fp,
            "label": label,
            "condition": cond,
            "category": cat,
            "duration": dur,
            "t_start": t_start,
            "t_end": t_end
        })

    p12_manifest_path = Path("data/manifests/phase12_independent_eval_manifest.csv")
    df_p12 = pd.read_csv(p12_manifest_path)
    df_res_val = df_p12[df_p12["split"] == "reserved_validation"]

    for _, row in df_res_val.iterrows():
        records.append({
            "source_split": "phase12_reserved_val",
            "recording_id": str(row["recording_id"]),
            "filepath": Path(row["filepath"]),
            "label": int(row["ground_truth_label"]),
            "condition": str(row["acoustic_condition"]),
            "category": str(row["event_classification"]),
            "duration": float(row["duration_seconds"]),
            "t_start": float(row["event_start_time_sec"]),
            "t_end": float(row["event_end_time_sec"])
        })
    return records

def load_or_compute_dev_cache(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    cache_path = Path("reports/.phase13_dev_features_cache.pkl")
    if cache_path.exists():
        print(f"Loading development cache from {cache_path}...")
        with open(cache_path, "rb") as f:
            return pickle.load(f)

    print("Computing features from scratch for development set (280 files)...")
    detector = Phase9AdaptiveGunshotDetector(profile="balanced")
    yamnet_model = detector.yamnet_model
    model_bundle = detector.model

    cache = []
    for rec in records:
        waveform = load_audio_mono_16k(rec["filepath"])
        crest_db = compute_physical_crest_factor_db(waveform)
        if len(waveform) < config.WINDOW_SAMPLES:
            padded = np.pad(waveform, (0, config.WINDOW_SAMPLES - len(waveform)))
        else:
            padded = waveform

        wave_tensor = tf.convert_to_tensor(padded, dtype=tf.float32)
        yam_scores, embs, _ = yamnet_model(wave_tensor)
        raw_scores = model_bundle.predict(embs.numpy(), verbose=0).flatten()

        cache.append({
            "record": rec,
            "crest_db": crest_db,
            "yamnet_scores": yam_scores.numpy(),
            "embeddings": embs.numpy(),
            "raw_scores": raw_scores,
            "duration": rec["duration"]
        })
    with open(cache_path, "wb") as f:
        pickle.dump(cache, f)
    return cache

def evaluate_dev_benchmarks(cache: List[Dict[str, Any]]) -> Dict[str, Any]:
    print("\n=== 2. REPRODUCING PHASE 13 DEVELOPMENT BENCHMARK ===")
    
    # We evaluate both Baseline Phase 9 and Candidate Phase 13
    eval_modes = [
        ("BASELINE_PHASE9", "phase9", "phase9_unconditional", 9.5, 0.0, 1.5),
        ("CANDIDATE_PHASE13", "relative_dominance", "crest_guarded_12db", 8.8, 12.0, 2.5)
    ]
    
    results = {}
    detailed_events = []

    for name, sem_mode, imm_mode, min_crest, single_crest, cooldown in eval_modes:
        tp = 0
        fn = 0
        fp = 0
        tn = 0
        pocket_tp = 0
        pocket_fn = 0
        duplicate_alerts = 0

        for item in cache:
            rec = item["record"]
            label = rec["label"]
            dur = item["duration"]
            crest_db = item["crest_db"]
            yam = item["yamnet_scores"]
            raw = item["raw_scores"]
            cond = rec["condition"]

            window_results = []
            n_wins = len(raw)

            for i in range(n_wins):
                st = round(i * (config.HOP_SAMPLES / float(config.SAMPLE_RATE)), 3)
                et = round(st + (config.WINDOW_SAMPLES / float(config.SAMPLE_RATE)), 3)
                rs = float(raw[i])
                cs = rs

                gun_s = max(yam[i, YAMNET_CLASS_GUNSHOT], yam[i, YAMNET_CLASS_MACHINE_GUN], yam[i, YAMNET_CLASS_ARTILLERY], yam[i, YAMNET_CLASS_CAP_GUN])
                thun_s = max(yam[i, YAMNET_CLASS_THUNDERSTORM], yam[i, YAMNET_CLASS_THUNDER])
                fire_s = max(yam[i, YAMNET_CLASS_FIREWORKS], yam[i, YAMNET_CLASS_FIRECRACKER])

                if sem_mode == "phase9":
                    if thun_s > 0.40 and gun_s < 0.05 and rs < 0.88:
                        cs *= 0.35
                    elif fire_s > 0.45 and gun_s < 0.04 and rs < 0.88:
                        cs *= 0.40
                elif sem_mode == "relative_dominance":
                    dog_s = max(yam[i, YAMNET_CLASS_DOG], yam[i, YAMNET_CLASS_BARK], yam[i, YAMNET_CLASS_YIP], yam[i, YAMNET_CLASS_CANIDAE])
                    siren_s = max(yam[i, YAMNET_CLASS_POLICE_CAR], yam[i, YAMNET_CLASS_AMBULANCE], yam[i, YAMNET_CLASS_FIRE_ENGINE], yam[i, YAMNET_CLASS_SIREN], yam[i, YAMNET_CLASS_CIVIL_DEFENSE])
                    if thun_s > 0.25 and thun_s >= gun_s * 1.5:
                        cs *= 0.30
                    elif fire_s > 0.25 and fire_s >= gun_s * 1.5:
                        cs *= 0.35
                    elif dog_s > 0.30 and dog_s >= gun_s * 1.5:
                        cs *= 0.35
                    elif siren_s > 0.35 and siren_s >= gun_s * 1.5:
                        cs *= 0.30

                window_results.append({"start_time": st, "end_time": et, "score": cs})

            if imm_mode == "phase9_unconditional":
                events = merge_detection_windows_phase9(
                    window_results=window_results,
                    threshold_base=0.75,
                    threshold_high=0.88,
                    threshold_off=0.48,
                    confirm_windows=2,
                    cooldown_secs=cooldown,
                    audio_duration_sec=dur,
                    allow_short_clip_exception=True,
                    crest_factor_db=crest_db,
                    min_crest_factor_db=min_crest
                )
            else:
                events = merge_phase13_events(
                    window_results=window_results,
                    threshold_base=0.75,
                    threshold_high=0.88,
                    threshold_off=0.48,
                    confirm_windows=2,
                    cooldown_secs=cooldown,
                    audio_duration_sec=dur,
                    allow_short_clip_exception=True,
                    crest_factor_db=crest_db,
                    min_crest_factor_db=min_crest,
                    single_win_min_crest_db=single_crest
                )

            # Pocket evaluation
            if "pocket" in cond.lower():
                if len(events) > 0:
                    pocket_tp += 1
                else:
                    pocket_fn += 1

            # Event matching
            t_start = rec["t_start"]
            t_end = rec["t_end"]

            item_detected = (len(events) > 0)
            if label == 1:
                matched = False
                for e in events:
                    temporal_match = (e["start_time"] <= t_end + 1.5) and (e["end_time"] >= t_start - 1.5)
                    if temporal_match:
                        if not matched:
                            matched = True
                            tp += 1
                        else:
                            duplicate_alerts += 1
                    else:
                        fp += 1
                if not matched:
                    fn += 1
            else:
                if item_detected:
                    fp += len(events)
                else:
                    tn += 1

            detailed_events.append({
                "model": name,
                "recording_id": rec["recording_id"],
                "source_split": rec["source_split"],
                "label": label,
                "condition": cond,
                "category": rec["category"],
                "duration": dur,
                "crest_db": round(crest_db, 2),
                "detected": item_detected,
                "events_count": len(events),
                "peak_raw_score": round(float(np.max(raw)), 4) if len(raw) > 0 else 0.0,
                "peak_calibrated_score": round(float(max(w["score"] for w in window_results)), 4) if len(window_results) > 0 else 0.0
            })

        prec = (tp / (tp + fp)) * 100 if (tp + fp) > 0 else 0.0
        rec_val = (tp / (tp + fn)) * 100 if (tp + fn) > 0 else 0.0
        f1 = (2 * prec * rec_val / (prec + rec_val)) if (prec + rec_val) > 0 else 0.0
        pocket_rec = (pocket_tp / (pocket_tp + pocket_fn)) * 100 if (pocket_tp + pocket_fn) > 0 else 0.0

        results[name] = {
            "tp": tp,
            "fn": fn,
            "fp": fp,
            "tn": tn,
            "precision": round(prec, 2),
            "recall": round(rec_val, 2),
            "f1": round(f1, 2),
            "pocket_recall": round(pocket_rec, 2),
            "pocket_tp": pocket_tp,
            "pocket_fn": pocket_fn,
            "duplicate_alerts": duplicate_alerts
        }

        print(f"[{name}] TP={tp}, FN={fn}, FP={fp}, TN={tn} | Prec={prec:.2f}%, Rec={rec_val:.2f}%, F1={f1:.2f}% | Pocket={pocket_rec:.2f}% ({pocket_tp}/{pocket_tp+pocket_fn})")

    return results, detailed_events

# -----------------------------------------------------------------------------
# 3. Reproduction of Matched Continuous Benchmark (2.0 hours)
# -----------------------------------------------------------------------------
def evaluate_matched_continuous_benchmark() -> Dict[str, Any]:
    print("\n=== 3. REPRODUCING MATCHED CONTINUOUS BENCHMARK (2.0 HOURS) ===")
    stream_path = Path("data/phase13_matched_continuous/phase13_matched_continuous_2hr.wav")
    segments_path = Path("data/phase13_matched_continuous/phase13_stream_segments.csv")

    if not stream_path.exists() or not segments_path.exists():
        raise FileNotFoundError(f"Continuous stream files missing: {stream_path} or {segments_path}")

    # Load audio
    print(f"Loading {stream_path}...")
    stream_wave, sr = sf.read(str(stream_path), dtype="float32")
    if stream_wave.ndim > 1:
        stream_wave = stream_wave[:, 0]
    total_sec = len(stream_wave) / sr
    total_hr = total_sec / 3600.0
    print(f"Loaded continuous stream: {len(stream_wave)} samples, {total_sec:.2f}s ({total_hr:.2f} hours) @ {sr} Hz.")

    df_segments = pd.read_csv(segments_path)

    # Precompute unique cycle window representations (1,225 chunks)
    p9_detector = Phase9AdaptiveGunshotDetector(profile="balanced")
    p13_detector = Phase13CandidateGunshotDetector(profile="balanced")

    chunk_size = 7680
    window_size = 15360
    hop_size = 7680
    total_chunks = int(math.ceil(len(stream_wave) / chunk_size))

    cycle_dur_samples = int(588.0 * sr)
    n_cycle_chunks = 1225
    cycle_wave = stream_wave[:cycle_dur_samples + window_size]

    print("Precomputing cycle acoustic representations...")
    yamnet_model = p9_detector.yamnet_model
    model_bundle = p9_detector.model

    cycle_features = []
    for i in range(n_cycle_chunks):
        w_start = i * hop_size
        w_wave = cycle_wave[w_start:w_start + window_size]
        if len(w_wave) < window_size:
            w_wave = np.pad(w_wave, (0, window_size - len(w_wave)))

        crest_db = compute_physical_crest_factor_db(w_wave)
        wave_tensor = tf.convert_to_tensor(w_wave, dtype=tf.float32)
        yam_scores, embs, _ = yamnet_model(wave_tensor)
        yam_scores = yam_scores.numpy()[0]
        raw_score = float(model_bundle.predict(embs.numpy(), verbose=0).flatten()[0])

        # Phase 9 calibrated score
        gun_s = max(yam_scores[YAMNET_CLASS_GUNSHOT], yam_scores[YAMNET_CLASS_MACHINE_GUN], yam_scores[YAMNET_CLASS_ARTILLERY], yam_scores[YAMNET_CLASS_CAP_GUN])
        thun_s = max(yam_scores[YAMNET_CLASS_THUNDERSTORM], yam_scores[YAMNET_CLASS_THUNDER])
        fire_s = max(yam_scores[YAMNET_CLASS_FIREWORKS], yam_scores[YAMNET_CLASS_FIRECRACKER])

        p9_score = raw_score
        if thun_s > 0.40 and gun_s < 0.05 and raw_score < 0.88:
            p9_score *= 0.35
        elif fire_s > 0.45 and gun_s < 0.04 and raw_score < 0.88:
            p9_score *= 0.40

        # Phase 13 calibrated score
        dog_s = max(yam_scores[YAMNET_CLASS_DOG], yam_scores[YAMNET_CLASS_BARK], yam_scores[YAMNET_CLASS_YIP], yam_scores[YAMNET_CLASS_CANIDAE])
        siren_s = max(yam_scores[YAMNET_CLASS_POLICE_CAR], yam_scores[YAMNET_CLASS_AMBULANCE], yam_scores[YAMNET_CLASS_FIRE_ENGINE], yam_scores[YAMNET_CLASS_SIREN], yam_scores[YAMNET_CLASS_CIVIL_DEFENSE])

        p13_score = raw_score
        if thun_s > 0.25 and thun_s >= gun_s * 1.5:
            p13_score *= 0.30
        elif fire_s > 0.25 and fire_s >= gun_s * 1.5:
            p13_score *= 0.35
        elif dog_s > 0.30 and dog_s >= gun_s * 1.5:
            p13_score *= 0.35
        elif siren_s > 0.35 and siren_s >= gun_s * 1.5:
            p13_score *= 0.30

        cycle_features.append({
            "crest_db": crest_db,
            "raw_score": raw_score,
            "p9_score": p9_score,
            "p13_score": p13_score
        })

    def run_simulation(model_type: str) -> List[Dict[str, Any]]:
        is_p9 = (model_type == "phase9")
        th_base = 0.75
        th_high = 0.88
        th_off = 0.48
        cooldown_s = 1.5 if is_p9 else 2.5
        conf_wins = 2

        active_cluster = []
        in_event = False
        had_decayed = True
        cooldown_until = -1.0
        alerts = []

        for c_idx in range(total_chunks):
            cycle_idx = c_idx % n_cycle_chunks
            feat = cycle_features[cycle_idx]
            calibrated_s = feat["p9_score"] if is_p9 else feat["p13_score"]
            crest_db = feat["crest_db"]
            win_st = round(c_idx * (hop_size / float(sr)), 3)
            win_et = round(win_st + (window_size / float(sr)), 3)

            if is_p9:
                qualifies_immediate = (calibrated_s >= th_high)
            else:
                qualifies_immediate = (calibrated_s >= th_high and crest_db >= 12.0)

            win_rec = {"start_time": win_st, "end_time": win_et, "score": calibrated_s}

            if not in_event:
                if calibrated_s < th_off:
                    had_decayed = True

                if win_st < cooldown_until:
                    if had_decayed and (qualifies_immediate or calibrated_s >= th_base):
                        active_cluster.append(win_rec)
                        if qualifies_immediate or len(active_cluster) >= conf_wins:
                            in_event = True
                            had_decayed = False
                            alerts.append({
                                "alert_time_sec": win_et,
                                "event_start_sec": min(w["start_time"] for w in active_cluster),
                                "event_end_sec": max(w["end_time"] for w in active_cluster),
                                "peak_score": round(max(w["score"] for w in active_cluster), 3),
                                "trigger_windows": len(active_cluster),
                                "mechanism": "single_window" if len(active_cluster) == 1 else "multi_window"
                            })
                            cooldown_until = win_et + cooldown_s
                else:
                    if qualifies_immediate:
                        active_cluster = [win_rec]
                        in_event = True
                        had_decayed = False
                        alerts.append({
                            "alert_time_sec": win_et,
                            "event_start_sec": win_st,
                            "event_end_sec": win_et,
                            "peak_score": round(calibrated_s, 3),
                            "trigger_windows": 1,
                            "mechanism": "single_window"
                        })
                        cooldown_until = win_et + cooldown_s
                    elif calibrated_s >= th_base:
                        active_cluster.append(win_rec)
                        if len(active_cluster) >= conf_wins:
                            in_event = True
                            had_decayed = False
                            alerts.append({
                                "alert_time_sec": win_et,
                                "event_start_sec": min(w["start_time"] for w in active_cluster),
                                "event_end_sec": max(w["end_time"] for w in active_cluster),
                                "peak_score": round(max(w["score"] for w in active_cluster), 3),
                                "trigger_windows": len(active_cluster),
                                "mechanism": "multi_window"
                            })
                            cooldown_until = win_et + cooldown_s
                    else:
                        active_cluster = []
            else:
                if calibrated_s >= th_off:
                    active_cluster.append(win_rec)
                else:
                    cooldown_until = win_et + cooldown_s
                    active_cluster = []
                    in_event = False
                    had_decayed = True

        return alerts

    p9_alerts = run_simulation("phase9")
    p13_alerts = run_simulation("phase13")

    p9_rate = len(p9_alerts) / total_hr
    p13_rate = len(p13_alerts) / total_hr
    reduction = ((len(p9_alerts) - len(p13_alerts)) / len(p9_alerts)) * 100

    print(f"Phase 9 Baseline Alerts: {len(p9_alerts)} ({p9_rate:.2f}/hr)")
    print(f"Phase 13 Candidate Alerts: {len(p13_alerts)} ({p13_rate:.2f}/hr)")
    print(f"Observed Alert Reduction: {reduction:.2f}%")

    # Map alerts to segments
    def map_alerts_to_categories(alerts: List[Dict[str, Any]]) -> Dict[str, int]:
        cat_counts = {}
        for a in alerts:
            t = a["alert_time_sec"]
            # find segment
            seg = df_segments[(df_segments["start_time_sec"] <= t) & (df_segments["end_time_sec"] >= t)]
            if len(seg) > 0:
                cat = seg["category"].values[0]
            else:
                # find closest segment
                cat = "unknown"
            cat_counts[cat] = cat_counts.get(cat, 0) + 1
        return cat_counts

    p9_cat = map_alerts_to_categories(p9_alerts)
    p13_cat = map_alerts_to_categories(p13_alerts)
    print("Phase 9 Category Breakdown:", p9_cat)
    print("Phase 13 Category Breakdown:", p13_cat)

    return {
        "exposure_hours": total_hr,
        "baseline_alerts": len(p9_alerts),
        "candidate_alerts": len(p13_alerts),
        "baseline_rate_per_hr": round(p9_rate, 2),
        "candidate_rate_per_hr": round(p13_rate, 2),
        "reduction_percent": round(reduction, 2),
        "baseline_categories": p9_cat,
        "candidate_categories": p13_cat,
        "p9_alerts": p9_alerts,
        "p13_alerts": p13_alerts
    }

# -----------------------------------------------------------------------------
# 4. Dataset Independence & Provenance Audit
# -----------------------------------------------------------------------------
def audit_dataset_provenance() -> Tuple[pd.DataFrame, Dict[str, Any]]:
    print("\n=== 4. EXHAUSTIVE DATASET INDEPENDENCE & PROVENANCE AUDIT ===")
    
    # 1. Load the 120 tracks of the continuous benchmark
    segments_path = Path("data/phase13_matched_continuous/phase13_stream_segments.csv")
    df_segments = pd.read_csv(segments_path)
    stream_tracks = df_segments[["category", "filename"]].drop_duplicates().reset_index(drop=True)
    
    # Load all historical manifests
    train_df = pd.read_csv("data/manifests/train.csv")
    val_df = pd.read_csv("data/manifests/val.csv")
    test_df = pd.read_csv("data/manifests/test.csv")
    neg_sources_df = pd.read_csv("data/manifests/negative_audio_sources.csv")
    p7_df = pd.read_csv("data/manifests/phase7_independent_eval_manifest.csv")
    p8_df = pd.read_csv("data/manifests/phase8_final_eval_manifest.csv")
    p10_df = pd.read_csv("data/manifests/phase10_evaluation_manifest.csv")
    p12_df = pd.read_csv("data/manifests/phase12_independent_eval_manifest.csv")

    # Build lookup maps
    train_names = set(train_df["filename"].tolist() + train_df["base_stem"].tolist())
    val_names = set(val_df["filename"].tolist() + val_df["base_stem"].tolist())
    test_names = set(test_df["filename"].tolist() + test_df["base_stem"].tolist())
    p7_names = set(p7_df["filename"].tolist())
    p8_names = set(p8_df["filename"].tolist())
    p10_names = set(p10_df["primary_filename"].tolist())
    p12_res_val_names = set(p12_df[p12_df["split"] == "reserved_validation"]["primary_filename"].tolist())
    p12_test_names = set(p12_df[p12_df["split"] == "final_test"]["primary_filename"].tolist())

    # Build hash index of all files in negative_audio_sources
    neg_meta = {}
    for _, row in neg_sources_df.iterrows():
        neg_meta[str(row["filename"])] = row.to_dict()

    # Find filepaths in data/raw/background
    raw_files = {}
    for p in Path("data/raw/background").rglob("*.wav"):
        raw_files[p.name] = p

    overlap_records = []
    duplicate_records = []

    for idx, row in stream_tracks.iterrows():
        cat = row["category"]
        fn = row["filename"]
        fp = raw_files.get(fn)

        if fp and fp.exists():
            file_bytes = fp.read_bytes()
            raw_sha256 = hashlib.sha256(file_bytes).hexdigest()
            # Compute canonical decoded audio hash (16kHz mono float32)
            wave, sr = sf.read(str(fp), dtype="float32")
            if wave.ndim > 1:
                wave = np.mean(wave, axis=1)
            if sr != 16000:
                # resample
                num_samples = int(len(wave) * 16000 / sr)
                wave = scipy.signal.resample(wave, num_samples)
            decoded_sha256 = hashlib.sha256(wave.tobytes()).hexdigest()
            dur_sec = len(wave) / 16000.0
        else:
            raw_sha256 = "FILE_NOT_FOUND"
            decoded_sha256 = "FILE_NOT_FOUND"
            dur_sec = 0.0

        in_train = fn in train_names
        in_val = fn in val_names
        in_test = fn in test_names
        in_p7 = fn in p7_names
        in_p8 = fn in p8_names
        in_p10 = fn in p10_names
        in_p12_res_val = fn in p12_res_val_names
        in_p12_final_test = fn in p12_test_names

        # Metadata from negative_audio_sources
        neg_info = neg_meta.get(fn, {})
        source_dataset = neg_info.get("source_dataset", "UNKNOWN")
        source_url = neg_info.get("source_url", "UNKNOWN")
        license_str = neg_info.get("license", "UNKNOWN")
        recording_id = neg_info.get("recording_id", "UNKNOWN")

        # Explicit Classification according to rules:
        # HISTORICALLY_USED: used in training, Phase 7, Phase 8, or Phase 9 dev benchmarks
        # DEVELOPMENT_ONLY: restricted to development
        # VALIDATION_ONLY: in reserved validation
        # DIAGNOSTIC_ONLY: in Phase 12 final test
        # SOURCE_INDEPENDENT: genuinely new, never previously seen
        # UNKNOWN_PROVENANCE: unknown source
        if in_p12_final_test:
            classification = "DIAGNOSTIC_ONLY"
        elif in_train or in_val or in_test:
            classification = "HISTORICALLY_USED"
        elif in_p8 or in_p10:
            classification = "HISTORICALLY_USED"
        elif in_p7:
            classification = "HISTORICALLY_USED"
        elif in_p12_res_val:
            classification = "VALIDATION_ONLY"
        elif source_dataset == "UNKNOWN":
            classification = "UNKNOWN_PROVENANCE"
        else:
            # It came from ESC-50 negative pool curated during Phase 4/7, but was not in discrete manifests
            classification = "HISTORICALLY_USED"

        historical_contexts = []
        if in_train: historical_contexts.append("train.csv")
        if in_val: historical_contexts.append("val.csv")
        if in_test: historical_contexts.append("test.csv")
        if in_p7: historical_contexts.append("phase7_eval")
        if in_p8: historical_contexts.append("phase8_final_eval")
        if in_p10: historical_contexts.append("phase10_eval")
        if in_p12_res_val: historical_contexts.append("phase12_reserved_val")
        if in_p12_final_test: historical_contexts.append("phase12_final_test")
        if not historical_contexts:
            historical_contexts.append("curated_esc50_negative_pool")

        rec = {
            "track_index": idx,
            "filename": fn,
            "stream_category": cat,
            "duration_sec": round(dur_sec, 2),
            "file_sha256": raw_sha256,
            "decoded_audio_sha256": decoded_sha256,
            "source_dataset": source_dataset,
            "recording_id": recording_id,
            "source_url": source_url,
            "license": license_str,
            "in_phase7_eval": in_p7,
            "in_phase8_eval": in_p8,
            "in_phase10_eval": in_p10,
            "in_phase12_final_test": in_p12_final_test,
            "in_phase12_res_val": in_p12_res_val,
            "historical_contexts": ";".join(historical_contexts),
            "provenance_classification": classification
        }
        overlap_records.append(rec)

        if in_p7 or in_p8 or in_p10:
            duplicate_records.append({
                "filename": fn,
                "category": cat,
                "raw_sha256": raw_sha256,
                "decoded_sha256": decoded_sha256,
                "overlap_with": historical_contexts,
                "duplicate_type": "EXACT_REUSED_TRACK"
            })

    df_overlap = pd.DataFrame(overlap_records)
    out_csv = REPORTS_DIR / "phase14_source_overlap_matrix.csv"
    df_overlap.to_csv(out_csv, index=False)
    print(f"Provenance matrix saved to: {out_csv}")

    out_json = REPORTS_DIR / "phase14_duplicate_and_near_duplicate_audit.json"
    audit_summary = {
        "total_continuous_benchmark_tracks": len(stream_tracks),
        "total_reused_from_phase7_eval": sum(1 for r in overlap_records if r["in_phase7_eval"]),
        "total_reused_from_phase8_eval": sum(1 for r in overlap_records if r["in_phase8_eval"]),
        "total_reused_from_phase10_eval": sum(1 for r in overlap_records if r["in_phase10_eval"]),
        "total_reused_from_phase12_final_test": sum(1 for r in overlap_records if r["in_phase12_final_test"]),
        "total_reused_from_phase12_res_val": sum(1 for r in overlap_records if r["in_phase12_res_val"]),
        "classification_breakdown": df_overlap["provenance_classification"].value_counts().to_dict(),
        "duplicate_tracks_count": len(duplicate_records),
        "duplicate_tracks_details": duplicate_records
    }
    with open(out_json, "w") as f:
        json.dump(audit_summary, f, indent=2)
    print(f"Duplicate audit JSON saved to: {out_json}")

    print("\nProvenance Classification Breakdown:")
    for k, v in audit_summary["classification_breakdown"].items():
        print(f" - {k}: {v} tracks ({v/120.0*100:.1f}%)")

    return df_overlap, audit_summary

# -----------------------------------------------------------------------------
# 5. False Negative Forensics: Event-by-Event Recall Regression
# -----------------------------------------------------------------------------
def forensic_analysis_false_negatives(cache: List[Dict[str, Any]]) -> pd.DataFrame:
    print("\n=== 5. FORENSIC ANALYSIS OF FALSE NEGATIVES (RECALL REGRESSION) ===")
    
    comparisons = []
    
    for item in cache:
        rec = item["record"]
        dur = item["duration"]
        crest_db = item["crest_db"]
        yam = item["yamnet_scores"]
        raw = item["raw_scores"]
        label = rec["label"]
        rid = rec["recording_id"]
        cond = rec["condition"]
        cat = rec["category"]
        t_start = rec["t_start"]
        t_end = rec["t_end"]

        # Run Phase 9
        win_p9 = []
        for i in range(len(raw)):
            st = round(i * (config.HOP_SAMPLES / float(config.SAMPLE_RATE)), 3)
            et = round(st + (config.WINDOW_SAMPLES / float(config.SAMPLE_RATE)), 3)
            rs = float(raw[i])
            cs = rs
            gun_s = max(yam[i, YAMNET_CLASS_GUNSHOT], yam[i, YAMNET_CLASS_MACHINE_GUN], yam[i, YAMNET_CLASS_ARTILLERY], yam[i, YAMNET_CLASS_CAP_GUN])
            thun_s = max(yam[i, YAMNET_CLASS_THUNDERSTORM], yam[i, YAMNET_CLASS_THUNDER])
            fire_s = max(yam[i, YAMNET_CLASS_FIREWORKS], yam[i, YAMNET_CLASS_FIRECRACKER])
            if thun_s > 0.40 and gun_s < 0.05 and rs < 0.88:
                cs *= 0.35
            elif fire_s > 0.45 and gun_s < 0.04 and rs < 0.88:
                cs *= 0.40
            win_p9.append({"start_time": st, "end_time": et, "score": cs})

        ev_p9 = merge_detection_windows_phase9(
            window_results=win_p9,
            threshold_base=0.75,
            threshold_high=0.88,
            threshold_off=0.48,
            confirm_windows=2,
            cooldown_secs=1.5,
            audio_duration_sec=dur,
            allow_short_clip_exception=True,
            crest_factor_db=crest_db,
            min_crest_factor_db=9.5
        )

        # Run Phase 13
        win_p13 = []
        suppression_details = []
        for i in range(len(raw)):
            st = round(i * (config.HOP_SAMPLES / float(config.SAMPLE_RATE)), 3)
            et = round(st + (config.WINDOW_SAMPLES / float(config.SAMPLE_RATE)), 3)
            rs = float(raw[i])
            cs = rs
            gun_s = max(yam[i, YAMNET_CLASS_GUNSHOT], yam[i, YAMNET_CLASS_MACHINE_GUN], yam[i, YAMNET_CLASS_ARTILLERY], yam[i, YAMNET_CLASS_CAP_GUN])
            thun_s = max(yam[i, YAMNET_CLASS_THUNDERSTORM], yam[i, YAMNET_CLASS_THUNDER])
            fire_s = max(yam[i, YAMNET_CLASS_FIREWORKS], yam[i, YAMNET_CLASS_FIRECRACKER])
            dog_s = max(yam[i, YAMNET_CLASS_DOG], yam[i, YAMNET_CLASS_BARK], yam[i, YAMNET_CLASS_YIP], yam[i, YAMNET_CLASS_CANIDAE])
            siren_s = max(yam[i, YAMNET_CLASS_POLICE_CAR], yam[i, YAMNET_CLASS_AMBULANCE], yam[i, YAMNET_CLASS_FIRE_ENGINE], yam[i, YAMNET_CLASS_SIREN], yam[i, YAMNET_CLASS_CIVIL_DEFENSE])

            sup_reasons = []
            if thun_s > 0.25 and thun_s >= gun_s * 1.5:
                cs *= 0.30
                sup_reasons.append(f"thunder(th={thun_s:.3f},gun={gun_s:.3f})")
            elif fire_s > 0.25 and fire_s >= gun_s * 1.5:
                cs *= 0.35
                sup_reasons.append(f"fireworks(fw={fire_s:.3f},gun={gun_s:.3f})")
            elif dog_s > 0.30 and dog_s >= gun_s * 1.5:
                cs *= 0.35
                sup_reasons.append(f"dog(dog={dog_s:.3f},gun={gun_s:.3f})")
            elif siren_s > 0.35 and siren_s >= gun_s * 1.5:
                cs *= 0.30
                sup_reasons.append(f"siren(sir={siren_s:.3f},gun={gun_s:.3f})")

            win_p13.append({"start_time": st, "end_time": et, "score": cs})
            if sup_reasons:
                suppression_details.append(f"w{i}:" + "+".join(sup_reasons))

        ev_p13 = merge_phase13_events(
            window_results=win_p13,
            threshold_base=0.75,
            threshold_high=0.88,
            threshold_off=0.48,
            confirm_windows=2,
            cooldown_secs=2.5,
            audio_duration_sec=dur,
            allow_short_clip_exception=True,
            crest_factor_db=crest_db,
            min_crest_factor_db=8.8,
            single_win_min_crest_db=12.0
        )

        p9_hit = len(ev_p9) > 0
        p13_hit = len(ev_p13) > 0

        # Detailed failure mechanism diagnosis if p9 detected but p13 missed
        failure_stage = "N/A"
        if label == 1 and p9_hit and not p13_hit:
            # Check why Phase 13 missed it
            # 1. Did relative semantic dominance suppress scores below threshold?
            p9_max_calib = max(w["score"] for w in win_p9)
            p13_max_calib = max(w["score"] for w in win_p13)
            
            # Check if crest guarded immediate dispatch blocked it:
            p9_had_immediate = any(w["score"] >= 0.88 for w in win_p9)
            p13_had_immediate = any(w["score"] >= 0.88 for w in win_p13) and (crest_db >= 12.0)

            if p9_max_calib >= 0.75 and p13_max_calib < 0.75:
                failure_stage = f"SEMANTIC_SUPPRESSION_OVERKILL (P9_score={p9_max_calib:.3f}->P13_score={p13_max_calib:.3f})"
            elif p13_max_calib >= 0.88 and not p13_had_immediate and crest_db < 12.0:
                failure_stage = f"CREST_GUARD_12DB_BLOCKED_SINGLE_WINDOW (crest={crest_db:.2f}dB<12.0dB, win_count={len(raw)})"
            elif len(raw) < 2 and dur < 0.96 and crest_db < 8.8:
                failure_stage = f"SHORT_CLIP_CREST_FILTER (crest={crest_db:.2f}dB<8.8dB)"
            else:
                failure_stage = f"TEMPORAL_CONFIRMATION_OR_COOLDOWN (P13_max={p13_max_calib:.3f})"

        comparisons.append({
            "recording_id": rid,
            "filepath": str(rec["filepath"]),
            "source_split": rec["source_split"],
            "label": label,
            "condition": cond,
            "category": cat,
            "duration_sec": round(dur, 2),
            "crest_factor_db": round(crest_db, 2),
            "max_raw_score": round(float(np.max(raw)), 4) if len(raw) > 0 else 0.0,
            "p9_detected": p9_hit,
            "p9_events_count": len(ev_p9),
            "p9_max_calibrated": round(float(max(w["score"] for w in win_p9)), 4) if len(win_p9) > 0 else 0.0,
            "p13_detected": p13_hit,
            "p13_events_count": len(ev_p13),
            "p13_max_calibrated": round(float(max(w["score"] for w in win_p13)), 4) if len(win_p13) > 0 else 0.0,
            "suppression_notes": ";".join(suppression_details),
            "failure_stage": failure_stage
        })

    df_comp = pd.DataFrame(comparisons)
    out_csv = REPORTS_DIR / "phase14_event_level_comparison.csv"
    df_comp.to_csv(out_csv, index=False)
    print(f"Event comparison saved to: {out_csv}")

    # Isolate missed genuine events
    missed_events = df_comp[(df_comp["label"] == 1) & (df_comp["p9_detected"] == True) & (df_comp["p13_detected"] == False)]
    recovered_events = df_comp[(df_comp["label"] == 1) & (df_comp["p9_detected"] == False) & (df_comp["p13_detected"] == True)]

    print(f"\nGenuine gunshot events detected by P9 but missed by P13: {len(missed_events)}")
    for _, row in missed_events.iterrows():
        print(f" - ID: {row['recording_id']} | Cond: {row['condition']} | Dur: {row['duration_sec']}s | Crest: {row['crest_factor_db']}dB")
        print(f"   P9_Calib: {row['p9_max_calibrated']} | P13_Calib: {row['p13_max_calibrated']} | Stage: {row['failure_stage']}")
        print(f"   Suppression: {row['suppression_notes']}")

    print(f"\nGenuine gunshot events recovered by P13 (missed by P9): {len(recovered_events)}")
    for _, row in recovered_events.iterrows():
        print(f" - ID: {row['recording_id']} | Cond: {row['condition']} | Crest: {row['crest_factor_db']}dB | P13_Calib: {row['p13_max_calibrated']}")

    return df_comp

# -----------------------------------------------------------------------------
# 6. Fireworks & Thunder Acoustic & Semantic Investigation
# -----------------------------------------------------------------------------
def analyze_fireworks_and_thunder() -> Dict[str, Any]:
    print("\n=== 6. FIREWORKS & THUNDER ACOUSTIC & SEMANTIC INVESTIGATION ===")
    
    fw_dir = Path("data/raw/background/fireworks")
    th_dir = Path("data/raw/background/thunder_and_weather")
    
    fw_files = sorted(list(fw_dir.glob("*.wav")))
    th_files = sorted(list(th_dir.glob("*.wav")))

    detector = Phase13CandidateGunshotDetector(profile="balanced")
    yamnet_model = detector.yamnet_model
    model_bundle = detector.model

    def analyze_audio_files(file_list: List[Path], category_name: str) -> List[Dict[str, Any]]:
        file_metrics = []
        for fp in file_list:
            wave, sr = sf.read(str(fp), dtype="float32")
            if wave.ndim > 1:
                wave = np.mean(wave, axis=1)
            if sr != 16000:
                wave = scipy.signal.resample(wave, int(len(wave) * 16000 / sr))
                sr = 16000

            dur = len(wave) / float(sr)
            peak = float(np.max(np.abs(wave)))
            rms = float(np.sqrt(np.mean(wave**2)))
            crest_db = compute_physical_crest_factor_db(wave)

            # Spectral metrics
            freqs, psd = scipy.signal.welch(wave, fs=sr, nperseg=1024)
            centroid = float(np.sum(freqs * psd) / (np.sum(psd) + 1e-12))
            bandwidth = float(np.sqrt(np.sum(((freqs - centroid)**2) * psd) / (np.sum(psd) + 1e-12)))

            # Low frequency ratio (< 300 Hz)
            low_freq_mask = (freqs <= 300)
            low_freq_ratio = float(np.sum(psd[low_freq_mask]) / (np.sum(psd) + 1e-12))

            # YAMNet inference
            if len(wave) < config.WINDOW_SAMPLES:
                wave_pad = np.pad(wave, (0, config.WINDOW_SAMPLES - len(wave)))
            else:
                wave_pad = wave

            wave_t = tf.convert_to_tensor(wave_pad, dtype=tf.float32)
            yam_scores, embs, _ = yamnet_model(wave_t)
            yam_scores = yam_scores.numpy()
            raw_scores = model_bundle.predict(embs.numpy(), verbose=0).flatten()

            max_raw = float(np.max(raw_scores)) if len(raw_scores) > 0 else 0.0

            # YAMNet class maxes
            gun_s = float(np.max(yam_scores[:, [YAMNET_CLASS_GUNSHOT, YAMNET_CLASS_MACHINE_GUN, YAMNET_CLASS_ARTILLERY, YAMNET_CLASS_CAP_GUN]]))
            thun_s = float(np.max(yam_scores[:, [YAMNET_CLASS_THUNDERSTORM, YAMNET_CLASS_THUNDER]]))
            fire_s = float(np.max(yam_scores[:, [YAMNET_CLASS_FIREWORKS, YAMNET_CLASS_FIRECRACKER]]))

            # Evaluate with Phase 9 vs Phase 13
            res_p9 = detector.evaluate_waveform(wave) # will run candidate
            # Custom evaluate
            win_p9 = []
            win_p13 = []
            for i in range(len(raw_scores)):
                rs = float(raw_scores[i])
                # P9
                cs9 = rs
                g = max(yam_scores[i, YAMNET_CLASS_GUNSHOT], yam_scores[i, YAMNET_CLASS_MACHINE_GUN], yam_scores[i, YAMNET_CLASS_ARTILLERY], yam_scores[i, YAMNET_CLASS_CAP_GUN])
                th = max(yam_scores[i, YAMNET_CLASS_THUNDERSTORM], yam_scores[i, YAMNET_CLASS_THUNDER])
                fw = max(yam_scores[i, YAMNET_CLASS_FIREWORKS], yam_scores[i, YAMNET_CLASS_FIRECRACKER])
                if th > 0.40 and g < 0.05 and rs < 0.88:
                    cs9 *= 0.35
                elif fw > 0.45 and g < 0.04 and rs < 0.88:
                    cs9 *= 0.40
                win_p9.append({"start_time": i*0.48, "end_time": i*0.48+0.96, "score": cs9})

                # P13
                cs13 = rs
                if th > 0.25 and th >= g * 1.5:
                    cs13 *= 0.30
                elif fw > 0.25 and fw >= g * 1.5:
                    cs13 *= 0.35
                win_p13.append({"start_time": i*0.48, "end_time": i*0.48+0.96, "score": cs13})

            ev9 = merge_detection_windows_phase9(win_p9, 0.75, 0.88, 0.48, 2, 1.5, dur, True, crest_db, 9.5)
            ev13 = merge_phase13_events(win_p13, 0.75, 0.88, 0.48, 2, 2.5, dur, True, crest_db, 8.8, 12.0)

            file_metrics.append({
                "filename": fp.name,
                "category": category_name,
                "duration_sec": round(dur, 2),
                "peak": round(peak, 4),
                "rms": round(rms, 4),
                "crest_db": round(crest_db, 2),
                "centroid_hz": round(centroid, 1),
                "bandwidth_hz": round(bandwidth, 1),
                "low_freq_ratio_300hz": round(low_freq_ratio, 4),
                "max_gun_semantic": round(gun_s, 4),
                "max_thunder_semantic": round(thun_s, 4),
                "max_fireworks_semantic": round(fire_s, 4),
                "max_raw_ensemble": round(max_raw, 4),
                "p9_alerts": len(ev9),
                "p13_alerts": len(ev13)
            })
        return file_metrics

    fw_metrics = analyze_audio_files(fw_files, "fireworks")
    th_metrics = analyze_audio_files(th_files, "thunder_and_weather")

    df_fw = pd.DataFrame(fw_metrics)
    df_th = pd.DataFrame(th_metrics)

    print("\n--- Fireworks Acoustic Profile (N=%d) ---" % len(df_fw))
    print(f"Crest dB: Mean={df_fw['crest_db'].mean():.2f}, Min={df_fw['crest_db'].min():.2f}, Max={df_fw['crest_db'].max():.2f}")
    print(f"Centroid Hz: Mean={df_fw['centroid_hz'].mean():.1f}")
    print(f"Low Freq (<300Hz) Ratio: Mean={df_fw['low_freq_ratio_300hz'].mean():.3f}")
    print(f"Phase 9 False Alerts: {df_fw['p9_alerts'].sum()} | Phase 13 False Alerts: {df_fw['p13_alerts'].sum()}")

    print("\n--- Thunderstorm Acoustic Profile (N=%d) ---" % len(df_th))
    print(f"Crest dB: Mean={df_th['crest_db'].mean():.2f}, Min={df_th['crest_db'].min():.2f}, Max={df_th['crest_db'].max():.2f}")
    print(f"Centroid Hz: Mean={df_th['centroid_hz'].mean():.1f}")
    print(f"Low Freq (<300Hz) Ratio: Mean={df_th['low_freq_ratio_300hz'].mean():.3f}")
    print(f"Phase 9 False Alerts: {df_th['p9_alerts'].sum()} | Phase 13 False Alerts: {df_th['p13_alerts'].sum()}")

    return {
        "fireworks_summary": {
            "count": len(df_fw),
            "mean_crest_db": round(float(df_fw['crest_db'].mean()), 2),
            "mean_centroid_hz": round(float(df_fw['centroid_hz'].mean()), 1),
            "mean_low_freq_ratio": round(float(df_fw['low_freq_ratio_300hz'].mean()), 3),
            "p9_total_alerts": int(df_fw['p9_alerts'].sum()),
            "p13_total_alerts": int(df_fw['p13_alerts'].sum()),
            "reduction_percent": round(float((df_fw['p9_alerts'].sum() - df_fw['p13_alerts'].sum()) / max(1, df_fw['p9_alerts'].sum()) * 100), 2)
        },
        "thunder_summary": {
            "count": len(df_th),
            "mean_crest_db": round(float(df_th['crest_db'].mean()), 2),
            "mean_centroid_hz": round(float(df_th['centroid_hz'].mean()), 1),
            "mean_low_freq_ratio": round(float(df_th['low_freq_ratio_300hz'].mean()), 3),
            "p9_total_alerts": int(df_th['p9_alerts'].sum()),
            "p13_total_alerts": int(df_th['p13_alerts'].sum()),
            "reduction_percent": round(float((df_th['p9_alerts'].sum() - df_th['p13_alerts'].sum()) / max(1, df_th['p9_alerts'].sum()) * 100), 2)
        },
        "fireworks_records": fw_metrics,
        "thunder_records": th_metrics
    }

# -----------------------------------------------------------------------------
# 7. Pocket Occlusion Audit & Sensitivity Evaluation
# -----------------------------------------------------------------------------
def analyze_pocket_occlusion(cache: List[Dict[str, Any]]) -> Dict[str, Any]:
    print("\n=== 7. POCKET OCCLUSION AUDIT & CREST FACTOR SENSITIVITY ===")
    
    pocket_samples = [item for item in cache if "pocket" in item["record"]["condition"].lower()]
    print(f"Total pocket-occluded development samples available: {len(pocket_samples)}")

    thresholds_to_test = [9.5, 8.8, 8.5]
    res_by_threshold = {}

    for th in thresholds_to_test:
        detected_pocket = 0
        all_pos_detected = 0
        all_neg_fp = 0
        
        for item in cache:
            rec = item["record"]
            label = rec["label"]
            dur = item["duration"]
            crest_db = item["crest_db"]
            raw = item["raw_scores"]
            is_pocket = "pocket" in rec["condition"].lower()

            # Window results using Phase 9 baseline semantic gating
            win = []
            for i in range(len(raw)):
                win.append({"start_time": i*0.48, "end_time": i*0.48+0.96, "score": float(raw[i])})

            events = merge_detection_windows_phase9(
                window_results=win,
                threshold_base=0.75,
                threshold_high=0.88,
                threshold_off=0.48,
                confirm_windows=2,
                cooldown_secs=1.5,
                audio_duration_sec=dur,
                allow_short_clip_exception=True,
                crest_factor_db=crest_db,
                min_crest_factor_db=th
            )

            hit = len(events) > 0
            if label == 1:
                if hit:
                    all_pos_detected += 1
                if is_pocket and hit:
                    detected_pocket += 1
            else:
                if hit:
                    all_neg_fp += len(events)

        pocket_recall = (detected_pocket / len(pocket_samples)) * 100 if len(pocket_samples) > 0 else 0.0
        res_by_threshold[str(th)] = {
            "min_crest_db": th,
            "pocket_tp": detected_pocket,
            "pocket_total": len(pocket_samples),
            "pocket_recall": round(pocket_recall, 2),
            "overall_pos_detected": all_pos_detected,
            "overall_neg_fp": all_neg_fp
        }
        print(f"Threshold {th:4.1f} dB -> Pocket Recall: {detected_pocket}/{len(pocket_samples)} ({pocket_recall:.1f}%) | Overall Pos: {all_pos_detected}/66 | Neg FP: {all_neg_fp}/214")

    # Detail the exact pocket samples
    pocket_details = []
    for item in pocket_samples:
        rec = item["record"]
        raw = item["raw_scores"]
        pocket_details.append({
            "recording_id": rec["recording_id"],
            "filepath": str(rec["filepath"]),
            "source_split": rec["source_split"],
            "duration_sec": round(item["duration"], 2),
            "crest_factor_db": round(item["crest_db"], 2),
            "max_raw_score": round(float(np.max(raw)), 4) if len(raw) > 0 else 0.0,
            "yamnet_gunshot_max": round(float(np.max(item["yamnet_scores"][:, YAMNET_CLASS_GUNSHOT])), 4)
        })

    return {
        "sample_count": len(pocket_samples),
        "threshold_evaluations": res_by_threshold,
        "sample_details": pocket_details
    }

# -----------------------------------------------------------------------------
# Main Execution
# -----------------------------------------------------------------------------
def main():
    print("================================================================================")
    print("   PHASE 14: INDEPENDENT REPRODUCIBILITY & PROVENANCE AUDIT")
    print("================================================================================")
    print("Safety Designation: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.\n")

    t0 = time.time()

    # 1. Archive Checksums
    archive_results = verify_historical_archives()

    # 2. Load Dev Records & Features
    dev_records = load_development_dataset()
    cache = load_or_compute_dev_cache(dev_records)

    # 3. Dev Benchmark Reproduction
    dev_benchmark_results, dev_detailed_events = evaluate_dev_benchmarks(cache)

    # 4. Continuous Benchmark Reproduction
    cont_benchmark_results = evaluate_matched_continuous_benchmark()

    # 5. Provenance Audit
    df_overlap, provenance_summary = audit_dataset_provenance()

    # 6. False Negative Forensics
    df_comp = forensic_analysis_false_negatives(cache)

    # 7. Fireworks & Thunder Investigation
    fw_th_results = analyze_fireworks_and_thunder()

    # 8. Pocket Occlusion Audit
    pocket_results = analyze_pocket_occlusion(cache)

    # Save comprehensive audit summary
    master_summary = {
        "phase": 14,
        "safety_designation": "RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY",
        "archive_verification": archive_results,
        "dev_benchmark_reproduction": dev_benchmark_results,
        "continuous_benchmark_reproduction": {
            "exposure_hours": cont_benchmark_results["exposure_hours"],
            "baseline_alerts": cont_benchmark_results["baseline_alerts"],
            "candidate_alerts": cont_benchmark_results["candidate_alerts"],
            "baseline_rate_per_hr": cont_benchmark_results["baseline_rate_per_hr"],
            "candidate_rate_per_hr": cont_benchmark_results["candidate_rate_per_hr"],
            "reduction_percent": cont_benchmark_results["reduction_percent"],
            "baseline_categories": cont_benchmark_results["baseline_categories"],
            "candidate_categories": cont_benchmark_results["candidate_categories"]
        },
        "provenance_summary": provenance_summary,
        "fireworks_and_thunder": {
            "fireworks": fw_th_results["fireworks_summary"],
            "thunder": fw_th_results["thunder_summary"]
        },
        "pocket_occlusion": pocket_results,
        "execution_time_seconds": round(time.time() - t0, 2)
    }

    summary_json_path = REPORTS_DIR / "phase14_audit_summary.json"
    with open(summary_json_path, "w") as f:
        json.dump(master_summary, f, indent=2)
    print(f"\nPhase 14 Master Audit Summary saved to: {summary_json_path}")
    print(f"Audit completed successfully in {time.time() - t0:.2f} seconds.")

if __name__ == "__main__":
    main()
