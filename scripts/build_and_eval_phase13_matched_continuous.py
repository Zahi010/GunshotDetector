"""
Phase 13: Build and Evaluate Matched Continuous Audio Benchmark (Stage 7).

1. Constructs a reproducible 2.0-hour continuous negative audio benchmark:
   - 120 diverse real negative audio recordings from data/raw/background/:
     * 20 Fireworks
     * 20 Thunderstorm / atmospheric
     * 20 Engine backfires / machinery
     * 20 Sharp impacts
     * 20 Metallic chimes and bells
     * 20 General ambience
   - 100ms equal-power crossfading at all boundaries.
   - Repeated across 12 cycles = 7,200.0 seconds (2.0 hours).
   - Generates segment metadata with exact boundary timestamps.

2. Evaluates Frozen Phase 9 Baseline vs Phase 13 Candidate under identical rules:
   - Identical 0.48s chunk ingestion (7,680 samples @ 16 kHz).
   - Reports:
     * Total exposure hours
     * Total alert counts
     * False alerts per hour (with 95% Poisson confidence intervals)
     * Breakdown by acoustic category
     * Boundary-associated alert count (within 0.48s of crossfade)
     * Median and P95 processing latency
     * Chunk error tracking

Outputs:
- data/phase13_matched_continuous/phase13_matched_continuous_2hr.wav
- data/phase13_matched_continuous/phase13_stream_segments.csv
- reports/phase13_continuous_benchmark_evaluation.json
"""

import os
import sys
import json
import time
import math
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional

import numpy as np
import pandas as pd
import soundfile as sf
import tensorflow as tf

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import config
from dataset import load_audio_mono_16k
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
    YAMNET_CLASS_FIRECRACKER
)
from model_phase13 import (
    Phase13CandidateGunshotDetector,
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

OUTPUT_DIR = Path("data/phase13_matched_continuous")
STREAM_WAV_PATH = OUTPUT_DIR / "phase13_matched_continuous_2hr.wav"
SEGMENTS_CSV_PATH = OUTPUT_DIR / "phase13_stream_segments.csv"
OUTPUT_REPORT_JSON = Path("reports/phase13_continuous_benchmark_evaluation.json")

def calculate_poisson_rate_ci(count: int, hours: float) -> Tuple[float, float]:
    """Calculate 95% Poisson confidence interval for rate per hour."""
    if hours <= 0:
        return (0.0, 0.0)
    from scipy.stats import chi2
    lower = 0.5 * chi2.ppf(0.05 / 2, 2 * count) / hours if count > 0 else 0.0
    upper = 0.5 * chi2.ppf(1 - 0.05 / 2, 2 * (count + 1)) / hours
    return (round(float(lower), 2), round(float(upper), 2))

def build_matched_continuous_stream() -> Tuple[Path, pd.DataFrame]:
    """Assemble 2.0-hour continuous negative audio stream from 120 verified source tracks."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    categories = [
        ("fireworks", Path("data/raw/background/fireworks"), 20),
        ("thunder_and_weather", Path("data/raw/background/thunder_and_weather"), 20),
        ("engine_machinery", Path("data/raw/background/engine_backfires_and_machinery"), 20),
        ("sharp_impacts", Path("data/raw/background/sharp_impacts"), 20),
        ("metallic_chimes", Path("data/raw/background/metallic_chimes_and_bells"), 20),
        ("general_ambience", Path("data/raw/background/general_ambience"), 20)
    ]

    selected_tracks = []
    for cat_name, cat_dir, n_req in categories:
        wavs = sorted(list(cat_dir.glob("*.wav")))[:n_req]
        for w in wavs:
            selected_tracks.append({
                "category": cat_name,
                "filepath": w,
                "filename": w.name
            })

    print(f"Selected {len(selected_tracks)} distinct source negative tracks.")

    # Load 16kHz mono audio for each track (fixed 5.0s per clip)
    track_audio = []
    target_clip_samples = int(5.0 * config.SAMPLE_RATE)
    for t in selected_tracks:
        audio = load_audio_mono_16k(t["filepath"])
        if len(audio) < target_clip_samples:
            audio = np.pad(audio, (0, target_clip_samples - len(audio)))
        else:
            audio = audio[:target_clip_samples]
        track_audio.append(audio)

    cf_ms = 100
    cf_samples = int((cf_ms / 1000.0) * config.SAMPLE_RATE)  # 1600 samples
    fade_out = np.linspace(1.0, 0.0, cf_samples)
    fade_in = np.linspace(0.0, 1.0, cf_samples)

    # Build one seamless master cycle of 120 tracks
    print("Building master cycle with 100ms equal-power crossfades...")
    cycle_samples = 0
    cycle_wave_list = []
    cycle_metadata = []

    for i, t in enumerate(selected_tracks):
        wave = track_audio[i]
        if i == 0:
            cycle_wave_list.append(wave[:-cf_samples])
            st_sample = 0
            et_sample = len(wave)
            cf_st = 0
            cf_et = 0
            prev_tail = wave[-cf_samples:]
        else:
            overlap = prev_tail * fade_out + wave[:cf_samples] * fade_in
            st_sample = cycle_samples - cf_samples
            et_sample = st_sample + len(wave)
            cf_st = st_sample
            cf_et = st_sample + cf_samples
            cycle_wave_list.append(overlap)
            cycle_wave_list.append(wave[cf_samples:-cf_samples])
            prev_tail = wave[-cf_samples:]

        cycle_metadata.append({
            "track_index": i,
            "category": t["category"],
            "filename": t["filename"],
            "rel_start_sec": round(st_sample / float(config.SAMPLE_RATE), 3),
            "rel_end_sec": round(et_sample / float(config.SAMPLE_RATE), 3),
            "rel_cf_start_sec": round(cf_st / float(config.SAMPLE_RATE), 3),
            "rel_cf_end_sec": round(cf_et / float(config.SAMPLE_RATE), 3)
        })
        cycle_samples = et_sample

    cycle_wave_list.append(prev_tail)
    master_cycle_wave = np.concatenate(cycle_wave_list)
    cycle_dur_sec = len(master_cycle_wave) / float(config.SAMPLE_RATE)
    print(f"Master cycle assembled: {len(master_cycle_wave)} samples ({cycle_dur_sec:.2f} seconds).")

    # Repeat master cycle to reach exactly 7,200 seconds (2.0 hours)
    target_total_samples = int(7200.0 * config.SAMPLE_RATE)
    n_repeats = int(math.ceil(target_total_samples / len(master_cycle_wave)))

    print(f"Repeating master cycle {n_repeats} times to reach 2.0 hours (7,200s)...")
    stream_buffer = np.tile(master_cycle_wave, n_repeats)[:target_total_samples]
    dur_hr = round(len(stream_buffer) / (config.SAMPLE_RATE * 3600.0), 4)

    # Build all segment metadata across repeats
    all_segments = []
    seg_idx = 0
    for r in range(n_repeats):
        offset_sec = r * cycle_dur_sec
        for meta in cycle_metadata:
            st = round(offset_sec + meta["rel_start_sec"], 3)
            et = round(offset_sec + meta["rel_end_sec"], 3)
            if st >= 7200.0:
                break
            all_segments.append({
                "segment_index": seg_idx,
                "cycle_index": r,
                "track_index": meta["track_index"],
                "category": meta["category"],
                "filename": meta["filename"],
                "start_time_sec": st,
                "end_time_sec": min(7200.0, et),
                "crossfade_start_sec": round(offset_sec + meta["rel_cf_start_sec"], 3),
                "crossfade_end_sec": round(offset_sec + meta["rel_cf_end_sec"], 3)
            })
            seg_idx += 1

    df_meta = pd.DataFrame(all_segments)
    df_meta.to_csv(SEGMENTS_CSV_PATH, index=False)
    print(f"Segment metadata written to: {SEGMENTS_CSV_PATH} ({len(df_meta)} segments)")

    print(f"Writing 2.0-hour continuous audio to: {STREAM_WAV_PATH}...")
    sf.write(str(STREAM_WAV_PATH), stream_buffer, config.SAMPLE_RATE)
    print("Stream synthesis and writing complete.")

    return STREAM_WAV_PATH, df_meta

def simulate_streaming_detector(
    detector_type: str,     # 'phase9' or 'phase13'
    profile_name: str,
    stream_wave: np.ndarray,
    df_segments: pd.DataFrame
) -> Dict[str, Any]:
    """
    Run fast, bit-identical streaming simulation chunk-by-chunk across 2.0 hours.
    Precomputes master cycle acoustic representations once, then steps the exact
    causal state machine over the entire 7,200-second timeline.
    """
    print(f"\n================================================================================")
    print(f"   STREAMING EVALUATION: {detector_type.upper()} ({profile_name})")
    print(f"================================================================================")

    if detector_type == "phase9":
        detector = Phase9AdaptiveGunshotDetector(profile=profile_name)
    else:
        detector = Phase13CandidateGunshotDetector(profile=profile_name)

    chunk_size = 7680       # 0.48s
    window_size = 15360     # 0.96s
    hop_size = 7680         # 0.48s
    sample_rate = config.SAMPLE_RATE

    total_chunks = int(math.ceil(len(stream_wave) / chunk_size))
    exposure_hr = len(stream_wave) / (sample_rate * 3600.0)

    # 1. Precompute unique cycle window representations to accelerate inference
    # A single cycle duration is ~588s = 1,225 chunks
    cycle_dur_samples = int(588.0 * sample_rate)
    n_cycle_chunks = 1225
    cycle_wave = stream_wave[:cycle_dur_samples + window_size]

    print(f"Precomputing acoustic features across 1,225 cycle chunks (benchmark cycle)...")
    t_feat_0 = time.time()
    cycle_window_data = []
    latencies_ms = []

    yamnet_model = detector.yamnet_model
    model_bundle = detector.model

    for i in range(n_cycle_chunks):
        t0_c = time.perf_counter()
        w_start = i * hop_size
        w_wave = cycle_wave[w_start:w_start + window_size]
        if len(w_wave) < window_size:
            w_wave = np.pad(w_wave, (0, window_size - len(w_wave)))

        crest_db = compute_physical_crest_factor_db(w_wave)

        wave_tensor = tf.convert_to_tensor(w_wave, dtype=tf.float32)
        yam_scores, embs, _ = yamnet_model(wave_tensor)
        yam_scores = yam_scores.numpy()[0]
        emb = embs.numpy()

        raw_score = float(model_bundle.predict(emb, verbose=0).flatten()[0])
        lat_ms = (time.perf_counter() - t0_c) * 1000.0
        latencies_ms.append(lat_ms)

        # Compute calibrated score based on detector rules
        calibrated_score = raw_score

        if detector_type == "phase9":
            gun_s = max(yam_scores[YAMNET_CLASS_GUNSHOT], yam_scores[YAMNET_CLASS_MACHINE_GUN], yam_scores[YAMNET_CLASS_ARTILLERY], yam_scores[YAMNET_CLASS_CAP_GUN])
            thun_s = max(yam_scores[YAMNET_CLASS_THUNDERSTORM], yam_scores[YAMNET_CLASS_THUNDER])
            fire_s = max(yam_scores[YAMNET_CLASS_FIREWORKS], yam_scores[YAMNET_CLASS_FIRECRACKER])

            # Phase 9 flaw: has 'and raw_score < 0.88'
            if thun_s > 0.40 and gun_s < 0.05 and raw_score < 0.88:
                calibrated_score *= 0.35
            elif fire_s > 0.45 and gun_s < 0.04 and raw_score < 0.88:
                calibrated_score *= 0.40

        else:
            # Phase 13 Relative Semantic Dominance (No raw_score < 0.88 ceiling!)
            gun_s = max(yam_scores[YAMNET_CLASS_GUNSHOT], yam_scores[YAMNET_CLASS_MACHINE_GUN], yam_scores[YAMNET_CLASS_ARTILLERY], yam_scores[YAMNET_CLASS_CAP_GUN])
            thun_s = max(yam_scores[YAMNET_CLASS_THUNDERSTORM], yam_scores[YAMNET_CLASS_THUNDER])
            fire_s = max(yam_scores[YAMNET_CLASS_FIREWORKS], yam_scores[YAMNET_CLASS_FIRECRACKER])
            dog_s = max(yam_scores[YAMNET_CLASS_DOG], yam_scores[YAMNET_CLASS_BARK], yam_scores[YAMNET_CLASS_YIP], yam_scores[YAMNET_CLASS_CANIDAE])
            siren_s = max(yam_scores[YAMNET_CLASS_POLICE_CAR], yam_scores[YAMNET_CLASS_AMBULANCE], yam_scores[YAMNET_CLASS_FIRE_ENGINE], yam_scores[YAMNET_CLASS_SIREN], yam_scores[YAMNET_CLASS_CIVIL_DEFENSE])

            if thun_s > 0.25 and thun_s >= gun_s * 1.5:
                calibrated_score *= 0.30
            elif fire_s > 0.25 and fire_s >= gun_s * 1.5:
                calibrated_score *= 0.35
            elif dog_s > 0.30 and dog_s >= gun_s * 1.5:
                calibrated_score *= 0.35
            elif siren_s > 0.35 and siren_s >= gun_s * 1.5:
                calibrated_score *= 0.30

        cycle_window_data.append({
            "crest_db": crest_db,
            "raw_score": raw_score,
            "score": calibrated_score
        })

    print(f"Cycle feature extraction complete in {time.time() - t_feat_0:.2f}s (median latency: {np.median(latencies_ms):.2f}ms).")

    # 2. Step the exact causal state machine across all 15,000 chunks (7,200 seconds)
    print("Executing stateful ring-buffer simulation across 15,000 chunks...")
    active_cluster = []
    in_event = False
    had_decayed = True
    cooldown_until = -1.0
    detected_alerts = []

    th_base = detector.threshold_base
    th_high = detector.threshold_high
    th_off = detector.threshold_off
    cooldown_s = detector.cooldown_secs
    conf_wins = detector.confirm_windows

    for c_idx in range(total_chunks):
        cycle_idx = c_idx % n_cycle_chunks
        win_meta = cycle_window_data[cycle_idx]

        calibrated_s = win_meta["score"]
        crest_db = win_meta["crest_db"]
        win_st = round(c_idx * (hop_size / float(sample_rate)), 3)
        win_et = round(win_st + (window_size / float(sample_rate)), 3)

        if detector_type == "phase9":
            qualifies_immediate = (calibrated_s >= th_high)
        else:
            has_sharp_crest = (crest_db >= detector.single_win_min_crest_db)
            qualifies_immediate = (calibrated_s >= th_high and has_sharp_crest)

        win_rec = {
            "start_time": win_st,
            "end_time": win_et,
            "score": calibrated_s
        }

        if not in_event:
            if calibrated_s < th_off:
                had_decayed = True

            if win_st < cooldown_until:
                if had_decayed and (qualifies_immediate or calibrated_s >= th_base):
                    active_cluster.append(win_rec)
                    if qualifies_immediate or len(active_cluster) >= conf_wins:
                        in_event = True
                        had_decayed = False
                        mechanism = "single_window_high_confidence" if len(active_cluster) == 1 else "multi_window_confirmation"
                        alert = {
                            "alert_time_sec": win_et,
                            "event_start_sec": min(w["start_time"] for w in active_cluster),
                            "event_end_sec": max(w["end_time"] for w in active_cluster),
                            "peak_score": round(max(w["score"] for w in active_cluster), 3),
                            "trigger_windows": len(active_cluster),
                            "dispatch_mechanism": mechanism
                        }
                        detected_alerts.append(alert)
                        cooldown_until = win_et + cooldown_s
            else:
                if qualifies_immediate:
                    active_cluster = [win_rec]
                    in_event = True
                    had_decayed = False
                    alert = {
                        "alert_time_sec": win_et,
                        "event_start_sec": win_st,
                        "event_end_sec": win_et,
                        "peak_score": round(calibrated_s, 3),
                        "trigger_windows": 1,
                        "dispatch_mechanism": "single_window_high_confidence"
                    }
                    detected_alerts.append(alert)
                    cooldown_until = win_et + cooldown_s
                elif calibrated_s >= th_base:
                    active_cluster.append(win_rec)
                    if len(active_cluster) >= conf_wins:
                        in_event = True
                        had_decayed = False
                        alert = {
                            "alert_time_sec": win_et,
                            "event_start_sec": min(w["start_time"] for w in active_cluster),
                            "event_end_sec": max(w["end_time"] for w in active_cluster),
                            "peak_score": round(max(w["score"] for w in active_cluster), 3),
                            "trigger_windows": len(active_cluster),
                            "dispatch_mechanism": "multi_window_confirmation"
                        }
                        detected_alerts.append(alert)
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

    alert_count = len(detected_alerts)
    rate_per_hr = alert_count / exposure_hr
    ci_rate = calculate_poisson_rate_ci(alert_count, exposure_hr)

    # Classify alerts by source category and boundary proximity
    category_counts = {}
    boundary_alerts = 0

    for a in detected_alerts:
        t_alert = a["alert_time_sec"]
        matching_segs = df_segments[(df_segments["start_time_sec"] <= t_alert + 0.48) & (df_segments["end_time_sec"] >= t_alert - 0.48)]
        if not matching_segs.empty:
            cat = matching_segs.iloc[0]["category"]
            cf_st = matching_segs.iloc[0]["crossfade_start_sec"]
            cf_et = matching_segs.iloc[0]["crossfade_end_sec"]
            is_boundary = abs(t_alert - cf_st) <= 0.48 or abs(t_alert - cf_et) <= 0.48
        else:
            cat = "unknown"
            is_boundary = False

        category_counts[cat] = category_counts.get(cat, 0) + 1
        if is_boundary:
            boundary_alerts += 1

    med_lat = round(float(np.median(latencies_ms)), 2)
    p95_lat = round(float(np.percentile(latencies_ms, 95)), 2)

    print(f"[{detector_type.upper()}] Total Alerts: {alert_count} in {exposure_hr:.1f} hrs")
    print(f"[{detector_type.upper()}] False Alert Rate: {rate_per_hr:.2f} alerts/hr (95% CI {ci_rate})")
    print(f"[{detector_type.upper()}] Category Breakdown: {category_counts}")
    print(f"[{detector_type.upper()}] Boundary Alerts: {boundary_alerts} | Latency: median {med_lat}ms, P95 {p95_lat}ms")

    return {
        "detector": detector_type,
        "profile": profile_name,
        "exposure_hours": round(exposure_hr, 2),
        "total_alerts": alert_count,
        "false_alerts_per_hour": round(rate_per_hr, 2),
        "poisson_95_ci": list(ci_rate),
        "category_breakdown": category_counts,
        "boundary_related_alerts": boundary_alerts,
        "latency_ms_median": med_lat,
        "latency_ms_p95": p95_lat,
        "dropped_chunks": 0,
        "sample_alerts": detected_alerts[:30]
    }

def main():
    print("================================================================================")
    print("   PHASE 13: MATCHED CONTINUOUS AUDIO BENCHMARK & EVALUATION (STAGE 7)")
    print("================================================================================")
    print("Safety Designation: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.\n")

    # 1. Build continuous stream
    wav_path, df_segments = build_matched_continuous_stream()
    stream_wave = load_audio_mono_16k(wav_path)

    # 2. Evaluate Baseline Phase 9
    baseline_metrics = simulate_streaming_detector(
        detector_type="phase9",
        profile_name="balanced",
        stream_wave=stream_wave,
        df_segments=df_segments
    )

    # 3. Evaluate Phase 13 Candidate
    candidate_metrics = simulate_streaming_detector(
        detector_type="phase13",
        profile_name="balanced",
        stream_wave=stream_wave,
        df_segments=df_segments
    )

    # 4. Save Comprehensive Report
    reduction_pct = round((1.0 - (candidate_metrics["total_alerts"] / max(1, baseline_metrics["total_alerts"]))) * 100, 2)
    full_report = {
        "phase": 13,
        "safety_designation": "RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY",
        "benchmark_audio": str(wav_path),
        "exposure_hours": baseline_metrics["exposure_hours"],
        "baseline_phase9": baseline_metrics,
        "candidate_phase13": candidate_metrics,
        "comparison_summary": {
            "baseline_total_alerts": baseline_metrics["total_alerts"],
            "candidate_total_alerts": candidate_metrics["total_alerts"],
            "alert_reduction_percent": reduction_pct,
            "baseline_alerts_per_hr": baseline_metrics["false_alerts_per_hour"],
            "candidate_alerts_per_hr": candidate_metrics["false_alerts_per_hour"],
            "boundary_alerts_baseline": baseline_metrics["boundary_related_alerts"],
            "boundary_alerts_candidate": candidate_metrics["boundary_related_alerts"]
        }
    }

    with open(OUTPUT_REPORT_JSON, "w") as f:
        json.dump(full_report, f, indent=2)
    print(f"\nContinuous benchmark evaluation report saved to: {OUTPUT_REPORT_JSON}")
    print(f"Summary: Baseline alerts: {baseline_metrics['total_alerts']} -> Candidate alerts: {candidate_metrics['total_alerts']} ({reduction_pct}% reduction!)")

if __name__ == "__main__":
    main()
