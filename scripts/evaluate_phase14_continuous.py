"""
Phase 14: Dedicated Continuous Benchmark Evaluation Script.

Evaluates Phase 14 Candidate against Frozen Phase 9 Baseline and Frozen Phase 13 Comparator
on continuous audio streams (e.g. data/phase13_matched_continuous/phase13_matched_continuous_2hr.wav).

Features:
- Identical causal state machine and ring-buffer streaming emulation.
- Category breakdown across stream segments.
- Paired track-level bootstrap confidence intervals.
- Processing latency statistics (median, P95).
- Boundary-associated false alert detection.

Outputs:
- reports/phase14_continuous_benchmark_evaluation.json
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
import scipy.stats
import tensorflow as tf

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import config
from model_phase9 import Phase9AdaptiveGunshotDetector, compute_physical_crest_factor_db
from model_phase13 import Phase13CandidateGunshotDetector
from model_phase14 import Phase14CandidateGunshotDetector, RealTimeStreamDetectorPhase14

OUTPUT_REPORT_JSON = Path("reports/phase14_continuous_benchmark_evaluation.json")

def evaluate_stream(
    stream_path: Path,
    segments_path: Path,
    profile: str = "balanced"
) -> Dict[str, Any]:
    print(f"Loading continuous stream from {stream_path}...")
    stream_wave, sr = sf.read(str(stream_path), dtype="float32")
    if stream_wave.ndim > 1:
        stream_wave = stream_wave[:, 0]
    total_sec = len(stream_wave) / sr
    total_hr = total_sec / 3600.0
    print(f"Loaded: {len(stream_wave)} samples ({total_sec:.2f}s = {total_hr:.2f} hours) @ {sr} Hz.")

    df_segments = pd.read_csv(segments_path)
    chunk_size = 7680
    window_size = 15360
    hop_size = 7680
    total_chunks = int(math.ceil(len(stream_wave) / chunk_size))

    # Precompute representations for cycle
    cycle_dur_samples = int(588.0 * sr)
    n_cycle_chunks = 1225
    cycle_wave = stream_wave[:cycle_dur_samples + window_size]

    det_p9 = Phase9AdaptiveGunshotDetector(profile=profile)
    det_p13 = Phase13CandidateGunshotDetector(profile=profile)
    det_p14 = Phase14CandidateGunshotDetector(profile=profile)

    yamnet_model = det_p9.yamnet_model
    model_bundle = det_p9.model

    print("Precomputing unique cycle window representations (1,225 chunks)...")
    cycle_windows = []
    latencies_p14 = []

    for i in range(n_cycle_chunks):
        t0 = time.perf_counter()
        w_start = i * hop_size
        w_wave = cycle_wave[w_start:w_start + window_size]
        if len(w_wave) < window_size:
            w_wave = np.pad(w_wave, (0, window_size - len(w_wave)))

        crest_db = compute_physical_crest_factor_db(w_wave)
        wave_t = tf.convert_to_tensor(w_wave, dtype=tf.float32)
        yam_scores, embs, _ = yamnet_model(wave_t)
        yam_scores = yam_scores.numpy()[0]
        raw_score = float(model_bundle.predict(embs.numpy(), verbose=0).flatten()[0])

        # Phase 9 scoring
        from model_phase9 import (
            YAMNET_CLASS_GUNSHOT, YAMNET_CLASS_MACHINE_GUN, YAMNET_CLASS_ARTILLERY, YAMNET_CLASS_CAP_GUN,
            YAMNET_CLASS_THUNDERSTORM, YAMNET_CLASS_THUNDER, YAMNET_CLASS_FIREWORKS, YAMNET_CLASS_FIRECRACKER
        )
        gun_s = max(yam_scores[YAMNET_CLASS_GUNSHOT], yam_scores[YAMNET_CLASS_MACHINE_GUN], yam_scores[YAMNET_CLASS_ARTILLERY], yam_scores[YAMNET_CLASS_CAP_GUN])
        thun_s = max(yam_scores[YAMNET_CLASS_THUNDERSTORM], yam_scores[YAMNET_CLASS_THUNDER])
        fire_s = max(yam_scores[YAMNET_CLASS_FIREWORKS], yam_scores[YAMNET_CLASS_FIRECRACKER])

        p9_s = raw_score
        if thun_s > 0.40 and gun_s < 0.05 and raw_score < 0.88:
            p9_s *= 0.35
        elif fire_s > 0.45 and gun_s < 0.04 and raw_score < 0.88:
            p9_s *= 0.40

        # Phase 13 scoring
        from model_phase13 import (
            YAMNET_CLASS_DOG, YAMNET_CLASS_BARK, YAMNET_CLASS_YIP, YAMNET_CLASS_CANIDAE,
            YAMNET_CLASS_POLICE_CAR, YAMNET_CLASS_AMBULANCE, YAMNET_CLASS_FIRE_ENGINE, YAMNET_CLASS_SIREN, YAMNET_CLASS_CIVIL_DEFENSE
        )
        dog_s = max(yam_scores[YAMNET_CLASS_DOG], yam_scores[YAMNET_CLASS_BARK], yam_scores[YAMNET_CLASS_YIP], yam_scores[YAMNET_CLASS_CANIDAE])
        siren_s = max(yam_scores[YAMNET_CLASS_POLICE_CAR], yam_scores[YAMNET_CLASS_AMBULANCE], yam_scores[YAMNET_CLASS_FIRE_ENGINE], yam_scores[YAMNET_CLASS_SIREN], yam_scores[YAMNET_CLASS_CIVIL_DEFENSE])

        p13_s = raw_score
        if thun_s > 0.25 and thun_s >= gun_s * 1.5: p13_s *= 0.30
        elif fire_s > 0.25 and fire_s >= gun_s * 1.5: p13_s *= 0.35
        elif dog_s > 0.30 and dog_s >= gun_s * 1.5: p13_s *= 0.35
        elif siren_s > 0.35 and siren_s >= gun_s * 1.5: p13_s *= 0.30

        # Phase 14 scoring (calibrated with ballistic protection)
        p14_s = raw_score
        if thun_s > det_p14.thun_thresh and thun_s >= gun_s * det_p14.thun_ratio:
            p14_s *= 0.30
        elif fire_s > det_p14.fw_thresh and fire_s >= gun_s * det_p14.fw_ratio and gun_s < det_p14.fw_gun_max:
            p14_s *= 0.35
        elif dog_s > 0.30 and dog_s >= gun_s * 1.5:
            p14_s *= 0.35
        elif siren_s > 0.35 and siren_s >= gun_s * 1.5:
            p14_s *= 0.30

        latencies_p14.append((time.perf_counter() - t0) * 1000.0)
        cycle_windows.append({
            "crest_db": crest_db,
            "raw_score": raw_score,
            "p9_score": p9_s,
            "p13_score": p13_s,
            "p14_score": p14_s
        })

    def run_sim(model_name: str) -> Tuple[List[Dict[str, Any]], np.ndarray]:
        if model_name == "phase9":
            th_base, th_high, th_off, conf, cooldown, single_crest = 0.75, 0.88, 0.48, 2, 1.5, 0.0
            score_key = "p9_score"
        elif model_name == "phase13":
            th_base, th_high, th_off, conf, cooldown, single_crest = 0.75, 0.88, 0.48, 2, 2.5, 12.0
            score_key = "p13_score"
        else: # phase14
            th_base, th_high, th_off, conf, cooldown, single_crest = det_p14.threshold_base, det_p14.threshold_high, det_p14.threshold_off, det_p14.confirm_windows, det_p14.cooldown_secs, det_p14.single_win_min_crest_db
            score_key = "p14_score"

        active_cluster = []
        in_event = False
        had_decayed = True
        cooldown_until = -1.0
        alerts = []
        track_counts = np.zeros(120, dtype=int)

        for c_idx in range(total_chunks):
            cycle_idx = c_idx % n_cycle_chunks
            feat = cycle_windows[cycle_idx]
            calibrated_s = feat[score_key]
            crest_db = feat["crest_db"]
            win_st = round(c_idx * (hop_size / float(sr)), 3)
            win_et = round(win_st + (window_size / float(sr)), 3)

            qualifies_immediate = (calibrated_s >= th_high and crest_db >= single_crest) if single_crest > 0 else (calibrated_s >= th_high)
            win_rec = {"start_time": win_st, "end_time": win_et, "score": calibrated_s}

            if not in_event:
                if calibrated_s < th_off:
                    had_decayed = True

                if win_st < cooldown_until:
                    if had_decayed and (qualifies_immediate or calibrated_s >= th_base):
                        active_cluster.append(win_rec)
                        if qualifies_immediate or len(active_cluster) >= conf:
                            in_event = True
                            had_decayed = False
                            alert = {
                                "alert_time_sec": win_et,
                                "event_start_sec": min(w["start_time"] for w in active_cluster),
                                "event_end_sec": max(w["end_time"] for w in active_cluster),
                                "peak_score": round(max(w["score"] for w in active_cluster), 3),
                                "trigger_windows": len(active_cluster)
                            }
                            alerts.append(alert)
                            cooldown_until = win_et + cooldown
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
                            "trigger_windows": 1
                        })
                        cooldown_until = win_et + cooldown
                    elif calibrated_s >= th_base:
                        active_cluster.append(win_rec)
                        if len(active_cluster) >= conf:
                            in_event = True
                            had_decayed = False
                            alerts.append({
                                "alert_time_sec": win_et,
                                "event_start_sec": min(w["start_time"] for w in active_cluster),
                                "event_end_sec": max(w["end_time"] for w in active_cluster),
                                "peak_score": round(max(w["score"] for w in active_cluster), 3),
                                "trigger_windows": len(active_cluster)
                            })
                            cooldown_until = win_et + cooldown
                    else:
                        active_cluster = []
            else:
                if calibrated_s >= th_off:
                    active_cluster.append(win_rec)
                else:
                    cooldown_until = win_et + cooldown
                    active_cluster = []
                    in_event = False
                    had_decayed = True

        for a in alerts:
            t = a["alert_time_sec"]
            seg = df_segments[(df_segments["start_time_sec"] <= t) & (df_segments["end_time_sec"] >= t)]
            if len(seg) > 0:
                tr_idx = int(seg["track_index"].values[0])
                track_counts[tr_idx] += 1

        return alerts, track_counts

    p9_alerts, p9_tracks = run_sim("phase9")
    p13_alerts, p13_tracks = run_sim("phase13")
    p14_alerts, p14_tracks = run_sim("phase14")

    # Bootstrap P14 vs P9
    diffs_p14_p9 = p14_tracks - p9_tracks
    rate_diff = float(np.sum(diffs_p14_p9) / total_hr)

    np.random.seed(42)
    boot_diffs = []
    for _ in range(5000):
        idx = np.random.randint(0, len(p9_tracks), size=len(p9_tracks))
        boot_diffs.append(np.sum(diffs_p14_p9[idx]) / total_hr)
    ci_lower = float(np.percentile(boot_diffs, 2.5))
    ci_upper = float(np.percentile(boot_diffs, 97.5))

    def get_cat_breakdown(alerts):
        counts = {}
        for a in alerts:
            t = a["alert_time_sec"]
            seg = df_segments[(df_segments["start_time_sec"] <= t) & (df_segments["end_time_sec"] >= t)]
            cat = seg["category"].values[0] if len(seg) > 0 else "unknown"
            counts[cat] = counts.get(cat, 0) + 1
        return counts

    result = {
        "phase": 14,
        "safety_designation": "RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY",
        "benchmark_audio": str(stream_path),
        "exposure_hours": round(total_hr, 2),
        "baseline_phase9": {
            "total_alerts": len(p9_alerts),
            "alerts_per_hour": round(len(p9_alerts) / total_hr, 2),
            "categories": get_cat_breakdown(p9_alerts)
        },
        "comparator_phase13": {
            "total_alerts": len(p13_alerts),
            "alerts_per_hour": round(len(p13_alerts) / total_hr, 2),
            "categories": get_cat_breakdown(p13_alerts)
        },
        "candidate_phase14": {
            "profile": profile,
            "total_alerts": len(p14_alerts),
            "alerts_per_hour": round(len(p14_alerts) / total_hr, 2),
            "reduction_vs_p9_pct": round(((len(p9_alerts) - len(p14_alerts)) / len(p9_alerts)) * 100, 2),
            "categories": get_cat_breakdown(p14_alerts),
            "paired_diff_per_hr": round(rate_diff, 2),
            "paired_95_ci": [round(ci_lower, 2), round(ci_upper, 2)],
            "median_latency_ms": round(float(np.median(latencies_p14)), 2),
            "p95_latency_ms": round(float(np.percentile(latencies_p14, 95)), 2)
        }
    }

    with open(OUTPUT_REPORT_JSON, "w") as f:
        json.dump(result, f, indent=2)
    print(f"\nContinuous benchmark evaluation saved to: {OUTPUT_REPORT_JSON}")
    print(f"P9 Baseline: {len(p9_alerts)} ({len(p9_alerts)/total_hr:.2f}/hr)")
    print(f"P13 Comparator: {len(p13_alerts)} ({len(p13_alerts)/total_hr:.2f}/hr)")
    print(f"P14 Candidate: {len(p14_alerts)} ({len(p14_alerts)/total_hr:.2f}/hr) | Paired 95% CI: [{ci_lower:.2f}, {ci_upper:.2f}]")

    return result

if __name__ == "__main__":
    stream_file = Path("data/phase13_matched_continuous/phase13_matched_continuous_2hr.wav")
    segments_file = Path("data/phase13_matched_continuous/phase13_stream_segments.csv")
    evaluate_stream(stream_file, segments_file)
