"""
Phase 8: Comprehensive Event-Level and Continuous-Audio Evaluation Suite.

Performs rigorous, side-by-side comparative evaluation of:
1. Phase 7 Frozen Baseline Detector (tau=0.75, N=2, cooldown=2.0s)
2. Phase 8 Adaptive Gunshot Detector (tau_base=0.70, tau_high=0.82, tau_off=0.45,
   short-clip exception, dynamic reverberation hysteresis, semantic mimic gating)

Evaluated Across:
A. Phase 7 Diagnostic Independent Set (230 recordings, 27 physical events, 200 mimics)
B. Phase 8 Untouched Final Evaluation Benchmark (43 pristine ballistic gunshots, 200 unseen ESC-50 mimics)
C. 3.0 Hours of Continuous Multi-Environment Negative Audio Streams

Produces:
- reports/phase8_event_level_evaluation.json
- reports/phase8_continuous_audio_evaluation.json
"""

import os
import sys
import json
import time
import hashlib
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import config
from dataset import load_audio_mono_16k, get_base_stem
from model import load_model_bundle, GunshotDetector
from model_phase8 import AdaptiveGunshotDetector
from scripts.evaluate_event_level import match_events
from evaluate import poisson_rate_confidence_interval


def load_canonical_events_from_csv(csv_path: Path) -> Dict[str, List[Dict[str, Any]]]:
    """Load canonical events indexed by recording_id, primary filename, and stem."""
    events_by_key = {}
    if not csv_path.exists():
        print(f"Warning: Events manifest not found at {csv_path}")
        return events_by_key

    df = pd.read_csv(csv_path)
    for _, row in df.iterrows():
        rec_id = str(row.get("recording_id", "")).strip()
        fn = str(row.get("primary_filename", "")).strip() or str(row.get("filename", "")).strip()
        stem = Path(fn).stem if fn else rec_id
        ev = {
            "canonical_event_id": str(row.get("canonical_event_id", "")),
            "recording_id": rec_id,
            "primary_filename": fn,
            "event_index": int(row.get("event_index", 1)),
            "start_time_sec": float(row.get("start_time_sec", 0.0)),
            "end_time_sec": float(row.get("end_time_sec", 0.0)),
            "peak_time_sec": float(row.get("peak_time_sec", 0.0)),
            "duration_sec": float(row.get("duration_sec", 0.0)),
            "estimated_snr_db": float(row.get("estimated_snr_db", 20.0)),
            "acoustic_condition": str(row.get("acoustic_condition", "standard")),
            "source": str(row.get("source", ""))
        }
        for k in {rec_id, fn, stem, ev["canonical_event_id"]}:
            if k:
                if k not in events_by_key:
                    events_by_key[k] = []
                already = any(
                    abs(e["start_time_sec"] - ev["start_time_sec"]) < 0.05 and
                    abs(e["end_time_sec"] - ev["end_time_sec"]) < 0.05
                    for e in events_by_key[k]
                )
                if not already:
                    events_by_key[k].append(ev)

    return events_by_key


def evaluate_dataset_event_level(
    manifest_csv: Path,
    events_csv: Path,
    detector_p7: GunshotDetector,
    detector_p8: AdaptiveGunshotDetector,
    benchmark_name: str
) -> Dict[str, Any]:
    print(f"\n=======================================================")
    print(f"   EVALUATING BENCHMARK: {benchmark_name}")
    print(f"=======================================================")

    manifest_df = pd.read_csv(manifest_csv)
    events_by_key = load_canonical_events_from_csv(events_csv)
    
    # Filter out continuous streams from discrete event evaluation
    discrete_df = manifest_df[manifest_df["category"] != "continuous_ambient_stream"].copy()
    gunshot_df = discrete_df[discrete_df["label"] == 1].copy()
    negative_df = discrete_df[discrete_df["label"] == 0].copy()

    print(f"Total discrete files: {len(discrete_df)} (Gunshots: {len(gunshot_df)}, Negatives/Mimics: {len(negative_df)})")

    # Evaluate for both models
    models_to_test = [
        ("Phase 7 Frozen Baseline (tau=0.75, N=2)", "phase7", detector_p7),
        ("Phase 8 Adaptive Detector", "phase8", detector_p8)
    ]

    benchmark_results = {}

    for model_name, model_tag, detector in models_to_test:
        print(f"\n--- Running: {model_name} ---")
        
        tp_total = 0
        fn_total = 0
        fp_total = 0
        duplicate_alerts_total = 0
        all_delays_ms = []
        matched_events_list = []
        missed_events_list = []
        false_alert_list = []

        pos_recs_total = len(gunshot_df)
        pos_recs_detected = 0
        total_gt_events = 0

        # 1. Evaluate Gunshot Files
        for _, row in gunshot_df.iterrows():
            rec_id = str(row["recording_id"])
            fn = str(row["filename"])
            fp = Path(row["filepath"])
            cond = str(row.get("acoustic_condition", "gunshot"))

            if not fp.exists():
                print(f"Warning: File not found: {fp}")
                continue

            wave = load_audio_mono_16k(fp)
            dur = len(wave) / 16000.0

            # Ground truth events
            gt_evs = events_by_key.get(rec_id, []) or events_by_key.get(fn, []) or events_by_key.get(fp.stem, [])
            if not gt_evs:
                gt_evs = [{
                    "canonical_event_id": f"EV-{rec_id}",
                    "recording_id": rec_id,
                    "event_index": 1,
                    "start_time_sec": 0.0,
                    "end_time_sec": dur,
                    "peak_time_sec": dur / 2.0,
                    "duration_sec": dur,
                    "acoustic_condition": cond
                }]

            total_gt_events += len(gt_evs)

            # Detect
            if model_tag == "phase7":
                res = detector.detect_waveform(wave, threshold=0.75, confirm_windows=2, cooldown_secs=2.0)
                det_evs = res.get("events", [])
            else:
                res = detector.evaluate_waveform(wave)
                det_evs = res.get("events", [])

            if len(det_evs) > 0:
                pos_recs_detected += 1

            tp, fn, _, delays, dups = match_events(gt_evs, det_evs, tolerance_sec=0.50)
            tp_total += tp
            fn_total += fn
            duplicate_alerts_total += dups
            all_delays_ms.extend(delays)

            # Itemize for reporting
            sorted_gt = sorted(gt_evs, key=lambda x: x["start_time_sec"])
            sorted_det = sorted(det_evs, key=lambda x: x["start_time"])

            for g_idx, g_ev in enumerate(sorted_gt):
                ev_id = g_ev.get("canonical_event_id", f"EV-{rec_id}")
                is_hit = False
                for d_ev in sorted_det:
                    d_st = d_ev["start_time"]
                    d_et = d_ev["end_time"]
                    g_st = g_ev["start_time_sec"]
                    g_et = g_ev["end_time_sec"]
                    if (max(d_st, g_st) < min(d_et, g_et)) or abs(d_st - g_st) <= 0.50:
                        is_hit = True
                        matched_events_list.append({
                            "canonical_event_id": ev_id,
                            "recording_id": rec_id,
                            "filename": fn,
                            "acoustic_condition": cond,
                            "gt_start_sec": g_st,
                            "gt_end_sec": g_et,
                            "det_start_sec": d_st,
                            "det_end_sec": d_et,
                            "peak_score": d_ev.get("peak_score", 0.0),
                            "onset_delay_ms": round(max(0.0, (d_st - g_st) * 1000.0), 1)
                        })
                        break
                if not is_hit:
                    missed_events_list.append({
                        "canonical_event_id": ev_id,
                        "recording_id": rec_id,
                        "filename": fn,
                        "acoustic_condition": cond,
                        "gt_start_sec": g_ev["start_time_sec"],
                        "gt_end_sec": g_ev["end_time_sec"],
                        "duration_sec": g_ev.get("duration_sec", dur),
                        "overall_score": res.get("overall_score", 0.0)
                    })

        # 2. Evaluate Negative / Mimic Files
        for _, row in negative_df.iterrows():
            rec_id = str(row["recording_id"])
            fn = str(row["filename"])
            fp = Path(row["filepath"])
            cond = str(row.get("acoustic_condition", "negative"))

            if not fp.exists():
                continue

            wave = load_audio_mono_16k(fp)
            if model_tag == "phase7":
                res = detector.detect_waveform(wave, threshold=0.75, confirm_windows=2, cooldown_secs=2.0)
                det_evs = res.get("events", [])
            else:
                res = detector.evaluate_waveform(wave)
                det_evs = res.get("events", [])

            if len(det_evs) > 0:
                fp_total += len(det_evs)
                for d in det_evs:
                    false_alert_list.append({
                        "recording_id": rec_id,
                        "filename": fn,
                        "acoustic_condition": cond,
                        "start_time_sec": d["start_time"],
                        "end_time_sec": d["end_time"],
                        "peak_score": d.get("peak_score", 0.0),
                        "verdict": "False Alert"
                    })

        event_recall = (tp_total / total_gt_events * 100.0) if total_gt_events > 0 else 0.0
        event_prec = (tp_total / (tp_total + fp_total) * 100.0) if (tp_total + fp_total) > 0 else 0.0
        event_f1 = (2 * event_prec * event_recall / (event_prec + event_recall)) if (event_prec + event_recall) > 0 else 0.0
        rec_recall = (pos_recs_detected / pos_recs_total * 100.0) if pos_recs_total > 0 else 0.0
        mean_delay = float(np.mean(all_delays_ms)) if all_delays_ms else 0.0

        print(f"Results for {model_name}:")
        print(f"  Physical Events: {total_gt_events} | TP: {tp_total} | FN: {fn_total} | FP (Mimics): {fp_total}")
        print(f"  Event Recall:    {event_recall:.2f}% | Precision: {event_prec:.2f}% | F1: {event_f1:.2f}%")
        print(f"  Recording Recall:{rec_recall:.2f}% ({pos_recs_detected}/{pos_recs_total})")
        print(f"  Duplicate Alerts:{duplicate_alerts_total} | Mean Delay: {mean_delay:.1f}ms")

        benchmark_results[model_tag] = {
            "model_name": model_name,
            "total_annotated_physical_events": total_gt_events,
            "true_positive_events_tp": tp_total,
            "missed_physical_events_fn": fn_total,
            "false_alert_events_fp": fp_total,
            "duplicate_alerts_count": duplicate_alerts_total,
            "event_recall": round(event_recall, 2),
            "event_precision": round(event_prec, 2),
            "event_f1": round(event_f1, 2),
            "recording_level_recall": round(rec_recall, 2),
            "mean_detection_delay_ms": round(mean_delay, 1),
            "matched_events": matched_events_list,
            "missed_events": missed_events_list,
            "false_alerts_sample": false_alert_list[:30]
        }

    return benchmark_results


def evaluate_continuous_audio_streams(
    manifest_csv: Path,
    detector_p7: GunshotDetector,
    detector_p8: AdaptiveGunshotDetector
) -> Dict[str, Any]:
    print(f"\n=======================================================")
    print(f"   EVALUATING 3.0 HOURS OF CONTINUOUS NEGATIVE AUDIO   ")
    print(f"=======================================================")

    manifest_df = pd.read_csv(manifest_csv)
    stream_rows = manifest_df[manifest_df["category"] == "continuous_ambient_stream"]

    continuous_results = {
        "evaluation_title": "Continuous Multi-Environment Negative Audio Robustness Evaluation",
        "evaluator": "Senior Acoustic ML Researcher",
        "safety_designation": "RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY",
        "total_exposure_hours": 3.00,
        "models_evaluated": {}
    }

    for model_name, model_tag, detector in [
        ("Phase 7 Frozen Baseline (tau=0.75, N=2)", "phase7", detector_p7),
        ("Phase 8 Adaptive Detector", "phase8", detector_p8)
    ]:
        print(f"\n--- Testing Continuous Audio: {model_name} ---")
        total_fps = 0
        total_secs = 0.0
        stream_breakdowns = []
        alerts_detail = []

        for _, row in stream_rows.iterrows():
            stream_id = str(row["recording_id"])
            fp = Path(row["filepath"])
            fn = row["filename"]
            cond = row["acoustic_condition"]

            if not fp.exists():
                print(f"Warning: Stream file {fp} not found!")
                continue

            wave = load_audio_mono_16k(fp)
            s_dur = len(wave) / 16000.0
            total_secs += s_dur

            t0 = time.perf_counter()
            if model_tag == "phase7":
                res = detector.detect_waveform(wave, threshold=0.75, confirm_windows=2, cooldown_secs=2.0)
                det_evs = res.get("events", [])
            else:
                res = detector.evaluate_waveform(wave)
                det_evs = res.get("events", [])
            elapsed = time.perf_counter() - t0

            ev_count = len(det_evs)
            total_fps += ev_count

            stream_hr = s_dur / 3600.0
            st_rate = ev_count / stream_hr if stream_hr > 0 else 0.0
            ci_l, ci_u = poisson_rate_confidence_interval(ev_count, stream_hr)

            print(f"   Stream: {fn} ({stream_hr:.2f} hr)")
            print(f"     False Alert Events: {ev_count} | Rate: {st_rate:.2f} alerts/hr (95% CI: [{ci_l:.1f}, {ci_u:.1f}])")

            stream_breakdowns.append({
                "stream_id": stream_id,
                "filename": fn,
                "acoustic_condition": cond,
                "exposure_seconds": s_dur,
                "exposure_hours": round(stream_hr, 3),
                "false_alerts_count": ev_count,
                "false_alerts_per_hour": round(st_rate, 2),
                "poisson_95_ci": [round(ci_l, 2), round(ci_u, 2)],
                "inference_time_sec": round(elapsed, 2)
            })

            for d in det_evs:
                alerts_detail.append({
                    "stream_id": stream_id,
                    "filename": fn,
                    "start_time_sec": d["start_time"],
                    "end_time_sec": d["end_time"],
                    "duration_sec": d.get("duration_seconds", round(d["end_time"] - d["start_time"], 2)),
                    "peak_score": d.get("peak_score", 0.0)
                })

        total_hours = total_secs / 3600.0
        overall_rate = total_fps / total_hours if total_hours > 0 else 0.0
        tot_ci_l, tot_ci_u = poisson_rate_confidence_interval(total_fps, total_hours)

        print(f"\nTotal Overall for {model_name}:")
        print(f"  Exposure: {total_hours:.2f} hours | Total False Alerts: {total_fps}")
        print(f"  Overall False Alert Rate: {overall_rate:.2f} alerts/hr (95% CI: [{tot_ci_l:.2f}, {tot_ci_u:.2f}])")

        continuous_results["models_evaluated"][model_tag] = {
            "model_name": model_name,
            "total_exposure_seconds": total_secs,
            "total_exposure_hours": round(total_hours, 3),
            "total_false_alert_events": total_fps,
            "overall_false_alerts_per_hour": round(overall_rate, 2),
            "overall_poisson_95_ci": [round(tot_ci_l, 2), round(tot_ci_u, 2)],
            "streams_breakdown": stream_breakdowns,
            "all_false_alerts": alerts_detail
        }

    return continuous_results


def run_full_phase8_evaluations():
    print("====================================================================")
    print("   STARTING PHASE 8 FINAL SYSTEM EVALUATIONS                        ")
    print("====================================================================\n")

    p7_detector = GunshotDetector(bundle_dir=config.MODELS_DIR / "gunshot_yamnet_bundle", threshold=0.75)
    p8_detector = AdaptiveGunshotDetector(bundle_dir=config.MODELS_DIR / "gunshot_yamnet_bundle")

    # 1. Evaluate Diagnostic Phase 7 Independent Benchmark
    p7_manifest = Path("data/manifests/phase7_independent_eval_manifest.csv")
    p7_events = Path("data/manifests/phase7_canonical_gunshot_events.csv")
    diag_p7_results = evaluate_dataset_event_level(
        p7_manifest, p7_events, p7_detector, p8_detector,
        benchmark_name="Phase 7 Diagnostic Independent Evaluation Set"
    )

    # 2. Evaluate Untouched Phase 8 Final Benchmark
    p8_manifest = Path("data/manifests/phase8_final_eval_manifest.csv")
    p8_events = Path("data/manifests/phase8_canonical_gunshot_events.csv")
    final_p8_results = evaluate_dataset_event_level(
        p8_manifest, p8_events, p7_detector, p8_detector,
        benchmark_name="Phase 8 Final Source-Independent Evaluation Set"
    )

    # 3. Evaluate 3.0 Hours of Continuous Negative Audio
    continuous_results = evaluate_continuous_audio_streams(
        p8_manifest, p7_detector, p8_detector
    )

    # Package and Save Event-Level Report
    event_level_report = {
        "report_title": "Phase 8 Comprehensive Event-Level Acoustic Evaluation Report",
        "evaluator": "Senior Acoustic ML Researcher",
        "safety_designation": "RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY",
        "diagnostic_phase7_independent_set": diag_p7_results,
        "phase8_final_source_independent_set": final_p8_results
    }

    out_ev = Path("reports/phase8_event_level_evaluation.json")
    with open(out_ev, "w", encoding="utf-8") as f:
        json.dump(event_level_report, f, indent=2)
    print(f"\nSaved Event-Level Evaluation to: {out_ev}")

    # Package and Save Continuous Audio Report
    out_cont = Path("reports/phase8_continuous_audio_evaluation.json")
    with open(out_cont, "w", encoding="utf-8") as f:
        json.dump(continuous_results, f, indent=2)
    print(f"Saved Continuous Audio Evaluation to: {out_cont}")


if __name__ == "__main__":
    run_full_phase8_evaluations()
