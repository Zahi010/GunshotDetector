"""
Event-Level Gunshot Detection Evaluation Tool.

Evaluates acoustic event detection performance at the physical event level:
- Compares detected audio event intervals against verified ground-truth gunshot events.
- Enforces strict one-to-one event matching with a documented tolerance window.
- Tracks true positive events, missed events, false alarm events on continuous negative audio.
- Computes Event Recall, Event Precision, Event F1, Detection Delay (latency in ms),
  and Duplicate Alert Rate per event.
- Measures false alerts per hour on real continuous environmental and transient audio.
"""
import os
import sys
import csv
import json
import time
import argparse
import numpy as np
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional
from scipy import stats

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import config
from dataset import GunshotDataset, load_audio_mono_16k, get_base_stem
from model import GunshotDetector, merge_detection_windows
from evaluate import poisson_rate_confidence_interval


def load_ground_truth_events(
    events_manifest: Optional[Path] = None
) -> Dict[str, List[Dict[str, Any]]]:
    """Load verified ground-truth gunshot event annotations indexed by recording stem and ID."""
    if events_manifest is None:
        canonical_p = Path("data/manifests/canonical_gunshot_events.csv")
        fallback_p = Path("data/manifests/gunshot_events.csv")
        events_manifest = canonical_p if canonical_p.exists() else fallback_p

    events_by_stem = {}
    if not events_manifest.exists():
        print(f"Warning: Events manifest not found at {events_manifest}")
        return events_by_stem

    with open(events_manifest, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rec_id = row.get("recording_id", "").strip()
            fn = row.get("primary_filename", "").strip() or row.get("filename", "").strip()
            stem = Path(fn).stem if fn else rec_id
            base = row.get("base_stem", "").strip() or get_base_stem(stem)
            ev = {
                "canonical_event_id": row.get("canonical_event_id", ""),
                "recording_id": rec_id,
                "base_stem": base,
                "primary_filename": fn,
                "event_index": int(row.get("event_index", 1)),
                "start_time_sec": float(row.get("start_time_sec", 0.0)),
                "end_time_sec": float(row.get("end_time_sec", 0.0)),
                "peak_time_sec": float(row.get("peak_time_sec", 0.0)),
                "duration_sec": float(row.get("duration_sec", 0.0)),
                "snr_db": float(row.get("estimated_snr_db", 20.0)),
                "confidence": float(row.get("confidence", 0.99))
            }
            for k in {rec_id, stem, base, fn, row.get("canonical_event_id", "")}:
                if k:
                    if k not in events_by_stem:
                        events_by_stem[k] = []
                    already = any(
                        abs(e["start_time_sec"] - ev["start_time_sec"]) < 0.05 and
                        abs(e["end_time_sec"] - ev["end_time_sec"]) < 0.05
                        for e in events_by_stem[k]
                    )
                    if not already:
                        events_by_stem[k].append(ev)

    return events_by_stem


def match_events(
    ground_truth_events: List[Dict[str, Any]],
    detected_events: List[Dict[str, Any]],
    tolerance_sec: float = 0.50
) -> Tuple[int, int, int, List[float], int]:
    """
    Match detected events against ground-truth events using interval overlap and onset tolerance.
    Returns:
        tp_events: Number of successfully detected ground truth events
        fn_events: Number of missed ground truth events
        fp_events: Number of spurious detections not matching any ground truth
        detection_delays_ms: List of onset delays for matched events
        duplicate_alerts: Extra alerts triggered for already-matched events
    """
    matched_gt = set()
    matched_det = set()
    detection_delays_ms = []
    duplicate_alerts = 0

    # Sort events chronologically
    sorted_gt = sorted(ground_truth_events, key=lambda x: x["start_time_sec"])
    sorted_det = sorted(detected_events, key=lambda x: x["start_time"])

    for d_idx, det in enumerate(sorted_det):
        d_st = det["start_time"]
        d_et = det["end_time"]
        matched_any_gt = False

        for g_idx, gt in enumerate(sorted_gt):
            g_st = gt["start_time_sec"]
            g_et = gt["end_time_sec"]

            # Overlap interval or within tolerance window
            overlap_st = max(d_st, g_st)
            overlap_et = min(d_et, g_et)
            is_overlap = (overlap_et - overlap_st) > 0.0
            is_near = abs(d_st - g_st) <= tolerance_sec or abs(d_et - g_et) <= tolerance_sec

            if is_overlap or is_near:
                matched_any_gt = True
                if g_idx not in matched_gt:
                    matched_gt.add(g_idx)
                    matched_det.add(d_idx)
                    delay_ms = max(0.0, (d_st - g_st) * 1000.0)
                    detection_delays_ms.append(round(delay_ms, 1))
                else:
                    # Already matched by an earlier detection
                    duplicate_alerts += 1
                break

    tp = len(matched_gt)
    fn = len(sorted_gt) - tp
    fp = len(sorted_det) - len(matched_det) - duplicate_alerts
    fp = max(0, fp)

    return tp, fn, fp, detection_delays_ms, duplicate_alerts


def evaluate_event_level_dataset(
    detector: GunshotDetector,
    dataset: GunshotDataset,
    events_by_stem: Dict[str, List[Dict[str, Any]]],
    split_name: str = "test",
    threshold: Optional[float] = None,
    confirm_windows: int = 2,
    cooldown_secs: float = 2.0,
    tolerance_sec: float = 0.50
) -> Dict[str, Any]:
    """
    Execute full event-level evaluation on a dataset split.
    """
    th = threshold if threshold is not None else detector.threshold
    target_groups = dataset.splits.get(split_name, [])
    
    pos_groups = [g for g in target_groups if dataset.groups[g]["label"] == 1]
    neg_groups = [g for g in target_groups if dataset.groups[g]["label"] == 0]

    total_gt_events = 0
    total_tp_events = 0
    total_fn_events = 0
    total_duplicate_alerts = 0
    all_delays_ms = []

    pos_recordings_evaluated = 0
    pos_recordings_detected = 0

    # 1. Evaluate Positive Recordings
    for g_key in pos_groups:
        primary_file = dataset.groups[g_key]["files"][0]
        rec_id = dataset.groups[g_key]["base_stem"]
        try:
            wave = load_audio_mono_16k(primary_file)
            dur = len(wave) / config.SAMPLE_RATE
            res = detector.detect_waveform(
                wave,
                threshold=th,
                confirm_windows=confirm_windows,
                cooldown_secs=cooldown_secs
            )
            detected_evs = res.get("events", [])
            gt_evs = events_by_stem.get(rec_id, []) or events_by_stem.get(primary_file.stem, [])

            if not gt_evs:
                # If unannotated, create a default spanning event
                gt_evs = [{
                    "recording_id": rec_id,
                    "event_index": 1,
                    "start_time_sec": 0.0,
                    "end_time_sec": dur,
                    "peak_time_sec": dur / 2.0,
                    "duration_sec": dur
                }]

            total_gt_events += len(gt_evs)
            tp, fn, _, delays, dups = match_events(gt_evs, detected_evs, tolerance_sec=tolerance_sec)
            total_tp_events += tp
            total_fn_events += fn
            total_duplicate_alerts += dups
            all_delays_ms.extend(delays)

            pos_recordings_evaluated += 1
            if len(detected_evs) > 0:
                pos_recordings_detected += 1
        except Exception as e:
            print(f"Skipping positive {primary_file.name}: {e}")

    # 2. Evaluate Negative Recordings (False Alarms)
    total_fp_events = 0
    total_neg_secs = 0.0
    neg_recordings_evaluated = 0
    neg_recordings_rejected = 0

    for g_key in neg_groups:
        primary_file = dataset.groups[g_key]["files"][0]
        try:
            wave = load_audio_mono_16k(primary_file)
            dur = len(wave) / config.SAMPLE_RATE
            total_neg_secs += dur
            res = detector.detect_waveform(
                wave,
                threshold=th,
                confirm_windows=confirm_windows,
                cooldown_secs=cooldown_secs
            )
            detected_evs = res.get("events", [])
            ev_count = len(detected_evs)
            total_fp_events += ev_count

            neg_recordings_evaluated += 1
            if ev_count == 0:
                neg_recordings_rejected += 1
        except Exception as e:
            print(f"Skipping negative {primary_file.name}: {e}")

    # Metrics computation
    total_neg_hours = total_neg_secs / 3600.0 if total_neg_secs > 0 else 0.0
    event_recall = total_tp_events / total_gt_events if total_gt_events > 0 else 0.0
    event_prec = total_tp_events / (total_tp_events + total_fp_events) if (total_tp_events + total_fp_events) > 0 else 0.0
    event_f1 = (2 * event_prec * event_recall) / (event_prec + event_recall) if (event_prec + event_recall) > 0 else 0.0

    false_alerts_per_hr = total_fp_events / total_neg_hours if total_neg_hours > 0 else 0.0
    ci_low, ci_high = poisson_rate_confidence_interval(total_fp_events, total_neg_hours)

    mean_delay = float(np.mean(all_delays_ms)) if all_delays_ms else 0.0
    p95_delay = float(np.percentile(all_delays_ms, 95)) if all_delays_ms else 0.0
    dup_rate = total_duplicate_alerts / total_tp_events if total_tp_events > 0 else 0.0

    return {
        "split": split_name,
        "operating_threshold": round(float(th), 3),
        "confirm_windows": confirm_windows,
        "cooldown_secs": cooldown_secs,
        "matching_tolerance_sec": tolerance_sec,
        "event_level_metrics": {
            "total_annotated_gunshot_events": total_gt_events,
            "gunshot_events_detected_tp": total_tp_events,
            "gunshot_events_missed_fn": total_fn_events,
            "false_alarm_events_fp": total_fp_events,
            "duplicate_alerts": total_duplicate_alerts,
            "duplicate_alert_rate_per_event": round(dup_rate, 3),
            "event_recall": round(float(event_recall), 4),
            "event_precision": round(float(event_prec), 4),
            "event_f1_score": round(float(event_f1), 4),
            "detection_delay_mean_ms": round(mean_delay, 1),
            "detection_delay_p95_ms": round(p95_delay, 1)
        },
        "continuous_streaming_false_alarms": {
            "negative_audio_duration_secs": round(total_neg_secs, 1),
            "negative_audio_duration_hours": round(total_neg_hours, 4),
            "total_false_alert_events": total_fp_events,
            "false_alerts_per_hour": round(false_alerts_per_hr, 2),
            "poisson_95_ci": [ci_low, ci_high]
        },
        "recording_level_metrics": {
            "gunshot_recordings_total": pos_recordings_evaluated,
            "gunshot_recordings_detected": pos_recordings_detected,
            "gunshot_recording_recall": round(pos_recordings_detected / pos_recordings_evaluated, 4) if pos_recordings_evaluated > 0 else 0.0,
            "negative_recordings_total": neg_recordings_evaluated,
            "negative_recordings_rejected": neg_recordings_rejected,
            "negative_recording_rejection_rate": round(neg_recordings_rejected / neg_recordings_evaluated, 4) if neg_recordings_evaluated > 0 else 0.0
        }
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluate event-level gunshot detection metrics.")
    parser.add_argument("--bundle", type=str, default="models/gunshot_yamnet_bundle")
    parser.add_argument("--split", type=str, default="test")
    parser.add_argument("--threshold", type=float, default=None)
    parser.add_argument("--confirm-windows", type=int, default=2)
    parser.add_argument("--output", type=str, default="reports/phase4_event_level_eval.json")
    args = parser.parse_args()

    detector = GunshotDetector(bundle_dir=Path(args.bundle))
    ds = GunshotDataset()
    ds.index_files()
    events_map = load_ground_truth_events()

    res = evaluate_event_level_dataset(
        detector=detector,
        dataset=ds,
        events_by_stem=events_map,
        split_name=args.split,
        threshold=args.threshold,
        confirm_windows=args.confirm_windows
    )

    print("\n=======================================================")
    print("           EVENT-LEVEL EVALUATION REPORT              ")
    print("=======================================================")
    ev_m = res["event_level_metrics"]
    print(f"Operating Threshold: {res['operating_threshold']:.3f} (Confirm Windows: {res['confirm_windows']})")
    print(f"Annotated Gunshot Events: {ev_m['total_annotated_gunshot_events']}")
    print(f"Detected Gunshot Events:  {ev_m['gunshot_events_detected_tp']} (Recall: {ev_m['event_recall']*100:.2f}%)")
    print(f"Missed Gunshot Events:    {ev_m['gunshot_events_missed_fn']}")
    print(f"False Alarm Events:       {ev_m['false_alarm_events_fp']} (Precision: {ev_m['event_precision']*100:.2f}%)")
    print(f"Event F1 Score:           {ev_m['event_f1_score']*100:.2f}%")
    print(f"Detection Delay Mean:     {ev_m['detection_delay_mean_ms']:.1f} ms (P95: {ev_m['detection_delay_p95_ms']:.1f} ms)")
    print(f"Duplicate Alerts:         {ev_m['duplicate_alerts']} (Rate: {ev_m['duplicate_alert_rate_per_event']:.2f}/event)")
    print(f"\nFalse Alerts/Hour:        {res['continuous_streaming_false_alarms']['false_alerts_per_hour']} alerts/hr (95% CI: {res['continuous_streaming_false_alarms']['poisson_95_ci']})")
    print(f"Recording Recall:         {res['recording_level_metrics']['gunshot_recording_recall']*100:.1f}% ({res['recording_level_metrics']['gunshot_recordings_detected']}/{res['recording_level_metrics']['gunshot_recordings_total']})")

    out_p = Path(args.output)
    out_p.parent.mkdir(parents=True, exist_ok=True)
    with open(out_p, "w", encoding="utf-8") as f:
        json.dump(res, f, indent=2)
    print(f"\nFull report saved to {out_p}")
