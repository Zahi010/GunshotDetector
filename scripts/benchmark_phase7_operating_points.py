"""
Phase 7 Validation Operating Point Optimization & Candidate Comparison.

Strictly uses validation data (.cache_features/features_val.npz and validation recordings)
to evaluate candidate operating configurations.

Metrics evaluated:
1. Window precision, recall, F1, and accuracy.
2. Event precision, recall, and F1 using 1-to-1 canonical matching.
3. Recording-level recall.
4. False alert events and false alerts per hour (Policy A and Policy B).
5. Detection delay (incorporating hop buffering, window accumulation, and model inference latency).
6. Duplicate alert count.
7. Inference latency (mean, p50, p95, p99 ms per window) and process memory footprint.

Selection Rule:
Selects the Pareto-optimal operating point that achieves Event Recall >= 90%
while minimizing false alert rate and maximizing Event F1.

Exports: reports/phase7_model_comparison.json
"""

import os
import sys
import json
import time
import os
import sys
import json
import time
import ctypes
from ctypes import wintypes
import numpy as np
import pandas as pd
from pathlib import Path
from scipy import stats

def get_process_memory_mb():
    try:
        class PROCESS_MEMORY_COUNTERS(ctypes.Structure):
            _fields_ = [
                ("cb", wintypes.DWORD),
                ("PageFaultCount", wintypes.DWORD),
                ("PeakWorkingSetSize", ctypes.c_size_t),
                ("WorkingSetSize", ctypes.c_size_t),
                ("QuotaPeakPagedPoolUsage", ctypes.c_size_t),
                ("QuotaPagedPoolUsage", ctypes.c_size_t),
                ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
                ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
                ("PagefileUsage", ctypes.c_size_t),
                ("PeakPagefileUsage", ctypes.c_size_t),
            ]
        counters = PROCESS_MEMORY_COUNTERS()
        counters.cb = ctypes.sizeof(PROCESS_MEMORY_COUNTERS)
        handle = ctypes.windll.kernel32.GetCurrentProcess()
        if ctypes.windll.psapi.GetProcessMemoryInfo(handle, ctypes.byref(counters), counters.cb):
            return counters.WorkingSetSize / (1024 * 1024)
    except Exception:
        pass
    return 0.0
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, average_precision_score, confusion_matrix
)

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import config
from dataset import GunshotDataset, load_audio_mono_16k
from model import GunshotDetector, merge_detection_windows
from scripts.evaluate_event_level import load_ground_truth_events, match_events
from evaluate import poisson_rate_confidence_interval


def benchmark_operating_points():
    print("====================================================================")
    print("   PHASE 7: VALIDATION-ONLY OPERATING POINT OPTIMIZATION           ")
    print("====================================================================\n")

    out_json = Path("reports/phase7_model_comparison.json")
    mem_initial_mb = get_process_memory_mb()

    # 1. Load validation features
    val_cache = np.load(".cache_features/features_val.npz", allow_pickle=True)
    X_val = val_cache["X"]
    y_val = val_cache["y"]
    meta_val = val_cache["meta"]

    n_val_windows = len(y_val)
    n_pos_win = int(np.sum(y_val == 1))
    n_neg_win = int(np.sum(y_val == 0))
    print(f"Validation Windows: Total={n_val_windows}, Positive={n_pos_win}, Negative={n_neg_win}")

    # 2. Load GunshotDetector Quad Stacking Ensemble
    bundle_path = Path("models/gunshot_yamnet_bundle")
    detector = GunshotDetector(bundle_dir=bundle_path)

    # Benchmark inference latency per window
    print("Measuring inference latency across validation windows...")
    latencies = []
    # Warmup
    _ = detector.classifier_head.predict(X_val[:5], verbose=0)
    for i in range(min(200, len(X_val))):
        t0 = time.perf_counter()
        _ = detector.classifier_head.predict(X_val[i:i+1], verbose=0)
        latencies.append((time.perf_counter() - t0) * 1000.0)

    mean_inf_ms = float(np.mean(latencies))
    p50_inf_ms = float(np.percentile(latencies, 50))
    p95_inf_ms = float(np.percentile(latencies, 95))
    p99_inf_ms = float(np.percentile(latencies, 99))
    print(f"Inference Latency: mean={mean_inf_ms:.2f}ms, p50={p50_inf_ms:.2f}ms, p95={p95_inf_ms:.2f}ms, p99={p99_inf_ms:.2f}ms")

    # Predict full validation set
    y_val_scores = detector.classifier_head.predict(X_val, verbose=0).flatten()
    val_roc_auc = float(roc_auc_score(y_val, y_val_scores))
    val_pr_auc = float(average_precision_score(y_val, y_val_scores))
    print(f"Validation ROC-AUC: {val_roc_auc * 100:.2f}%, PR-AUC: {val_pr_auc * 100:.2f}%")

    # 3. Load Validation Audio and Ground Truth Events
    gt_events_by_id = load_ground_truth_events(Path("data/manifests/canonical_gunshot_events.csv"))
    val_manifest = pd.read_csv("data/manifests/val.csv")

    gunshot_val_files = val_manifest[val_manifest["class"] == "gunshot"].to_dict("records")
    bg_val_files = val_manifest[val_manifest["class"] == "background"].to_dict("records")

    print(f"Validation Files: Gunshot={len(gunshot_val_files)}, Background={len(bg_val_files)}")

    # Pre-extract streaming windows for validation background files
    bg_audio_cache = []
    total_bg_sec = 0.0
    for rec in bg_val_files:
        fpath = Path(rec["relative_path"])
        waveform = load_audio_mono_16k(fpath)
        dur = len(waveform) / 16000.0
        total_bg_sec += dur

        embeddings, timestamps = detector.feature_extractor.extract_continuous_recording(waveform)
        if len(embeddings) > 0:
            raw_scores = detector.classifier_head.predict(embeddings, verbose=0).flatten()
            hop_samples = config.HOP_SAMPLES
            win_samples = config.WINDOW_SAMPLES
            for i in range(len(raw_scores)):
                chunk = waveform[i * hop_samples: i * hop_samples + win_samples]
                if len(chunk) > 0 and float(np.sqrt(np.mean(chunk ** 2) + 1e-12)) < 1e-4:
                    raw_scores[i] = 0.0

            win_scores = [
                {"window_index": i, "start_time": st, "end_time": et, "score": round(float(score), 4)}
                for i, (score, (st, et)) in enumerate(zip(raw_scores, timestamps))
            ]
        else:
            win_scores = []

        bg_audio_cache.append({
            "recording_id": rec["base_stem"],
            "filename": rec["filename"],
            "duration_sec": dur,
            "windows": win_scores
        })

    # Pre-extract streaming windows for validation gunshot files
    gunshot_audio_cache = []
    total_physical_events = 0
    non_gunshot_in_gunshot_sec = 0.0

    for rec in gunshot_val_files:
        fpath = Path(rec["relative_path"])
        waveform = load_audio_mono_16k(fpath)
        dur = len(waveform) / 16000.0

        stem = rec["base_stem"]
        gt_evs = gt_events_by_id.get(stem, [])
        total_physical_events += len(gt_evs)

        ev_dur = sum(e["duration_sec"] for e in gt_evs)
        non_gunshot_in_gunshot_sec += max(0.0, dur - ev_dur)

        embeddings, timestamps = detector.feature_extractor.extract_continuous_recording(waveform)
        if len(embeddings) > 0:
            raw_scores = detector.classifier_head.predict(embeddings, verbose=0).flatten()
            hop_samples = config.HOP_SAMPLES
            win_samples = config.WINDOW_SAMPLES
            for i in range(len(raw_scores)):
                chunk = waveform[i * hop_samples: i * hop_samples + win_samples]
                if len(chunk) > 0 and float(np.sqrt(np.mean(chunk ** 2) + 1e-12)) < 1e-4:
                    raw_scores[i] = 0.0

            win_scores = [
                {"window_index": i, "start_time": st, "end_time": et, "score": round(float(score), 4)}
                for i, (score, (st, et)) in enumerate(zip(raw_scores, timestamps))
            ]
        else:
            win_scores = []

        gunshot_audio_cache.append({
            "recording_id": stem,
            "filename": rec["filename"],
            "duration_sec": dur,
            "windows": win_scores,
            "gt_events": gt_evs
        })

    policy_a_hours = total_bg_sec / 3600.0
    policy_b_hours = (total_bg_sec + non_gunshot_in_gunshot_sec) / 3600.0

    print(f"Validation Exposure: Policy A (Pure BG)={total_bg_sec:.2f}s ({policy_a_hours:.4f}h)")
    print(f"Validation Exposure: Policy B (Total Non-Gunshot)={(total_bg_sec + non_gunshot_in_gunshot_sec):.2f}s ({policy_b_hours:.4f}h)")
    print(f"Canonical Physical Events in Validation: {total_physical_events} across {len(gunshot_val_files)} recordings\n")

    # 4. Define candidate configurations
    candidate_configs = [
        {"threshold": 0.500, "threshold_off": 0.400, "confirm_windows": 1, "cooldown_secs": 2.0, "name": "Permissive Single-Window (tau=0.50)"},
        {"threshold": 0.600, "threshold_off": 0.400, "confirm_windows": 2, "cooldown_secs": 2.0, "name": "Low Threshold Multi-Window (tau=0.60)"},
        {"threshold": 0.650, "threshold_off": 0.450, "confirm_windows": 2, "cooldown_secs": 2.0, "name": "Intermediate Multi-Window (tau=0.65)"},
        {"threshold": 0.690, "threshold_off": 0.400, "confirm_windows": 2, "cooldown_secs": 2.0, "name": "Phase 5 Baseline Operating Point (tau=0.69)"},
        {"threshold": 0.700, "threshold_off": 0.450, "confirm_windows": 2, "cooldown_secs": 2.0, "name": "Balanced Multi-Window (tau=0.70)"},
        {"threshold": 0.720, "threshold_off": 0.500, "confirm_windows": 2, "cooldown_secs": 2.0, "name": "High Precision Candidate A (tau=0.72)"},
        {"threshold": 0.750, "threshold_off": 0.500, "confirm_windows": 2, "cooldown_secs": 2.0, "name": "Phase 6 Recommended Operating Point (tau=0.75)"},
        {"threshold": 0.780, "threshold_off": 0.550, "confirm_windows": 2, "cooldown_secs": 2.0, "name": "High Precision Candidate B (tau=0.78)"},
        {"threshold": 0.800, "threshold_off": 0.600, "confirm_windows": 2, "cooldown_secs": 2.0, "name": "Aggressive False-Alarm Suppression (tau=0.80)"},
        {"threshold": 0.850, "threshold_off": 0.650, "confirm_windows": 2, "cooldown_secs": 2.0, "name": "Extreme Precision (tau=0.85)"},
        {"threshold": 0.750, "threshold_off": 0.500, "confirm_windows": 1, "cooldown_secs": 1.5, "name": "Low Latency Fast-Trigger (tau=0.75, N=1)"},
    ]

    mem_final_mb = get_process_memory_mb()
    mem_usage_delta_mb = round(mem_final_mb - mem_initial_mb, 2)

    results_table = []
    print("------------------------------------------------------------------------------------------------------------------------------")
    print("Config Name                 | Tau   | N_win | Acc%  | WinP% | WinR% | WinF1 | EvtP% | EvtR% | EvtF1 | RecR% | Alerts/h (A) | Del(ms)")
    print("------------------------------------------------------------------------------------------------------------------------------")

    for cfg in candidate_configs:
        th = cfg["threshold"]
        th_off = cfg["threshold_off"]
        c_win = cfg["confirm_windows"]
        cool = cfg["cooldown_secs"]

        # Window-level metrics on validation cache
        y_pred = (y_val_scores >= th).astype(int)
        cm = confusion_matrix(y_val, y_pred, labels=[0, 1])
        tn, fp, fn, tp = cm.ravel()

        acc = float(accuracy_score(y_val, y_pred)) * 100.0
        p_win = float(precision_score(y_val, y_pred, zero_division=0)) * 100.0
        r_win = float(recall_score(y_val, y_pred, zero_division=0)) * 100.0
        f1_win = float(f1_score(y_val, y_pred, zero_division=0)) * 100.0

        # Event-level matching on continuous gunshot recordings
        tp_ev_total = 0
        fn_ev_total = 0
        fp_ev_gunshot = 0
        delays = []
        dups = 0
        recs_detected = 0

        for item in gunshot_audio_cache:
            merged = merge_detection_windows(item["windows"], threshold=th, confirm_windows=c_win,
                                             cooldown_secs=cool, threshold_off=th_off)
            t_tp, t_fn, t_fp, t_delays, t_dups = match_events(item["gt_events"], merged, tolerance_sec=0.75)
            tp_ev_total += t_tp
            fn_ev_total += t_fn
            fp_ev_gunshot += t_fp
            delays.extend(t_delays)
            dups += t_dups
            if t_tp > 0:
                recs_detected += 1

        rec_recall = (recs_detected / len(gunshot_val_files)) * 100.0 if gunshot_val_files else 0.0

        # False alarms on continuous background recordings
        fp_ev_bg = 0
        for item in bg_audio_cache:
            merged = merge_detection_windows(item["windows"], threshold=th, confirm_windows=c_win,
                                             cooldown_secs=cool, threshold_off=th_off)
            fp_ev_bg += len(merged)

        total_fp_events = fp_ev_bg + fp_ev_gunshot
        evt_rec = (tp_ev_total / total_physical_events) * 100.0 if total_physical_events > 0 else 0.0
        evt_prec = (tp_ev_total / (tp_ev_total + total_fp_events)) * 100.0 if (tp_ev_total + total_fp_events) > 0 else 0.0
        evt_f1 = (2 * evt_prec * evt_rec / (evt_prec + evt_rec)) if (evt_prec + evt_rec) > 0 else 0.0

        rate_a = fp_ev_bg / policy_a_hours if policy_a_hours > 0 else 0.0
        rate_b = total_fp_events / policy_b_hours if policy_b_hours > 0 else 0.0
        ci_a_low, ci_a_high = poisson_rate_confidence_interval(fp_ev_bg, policy_a_hours)

        # End-to-end streaming latency calculation:
        # Buffer accumulation = window duration (0.96s = 960ms) if N=1;
        # if N=2, second window requires waiting 1 hop (0.48s = 480ms) after window onset.
        # Plus mean inference latency (mean_inf_ms).
        # Plus acoustic onset offset (mean onset-to-window delay).
        onset_offset_ms = float(np.mean(delays)) if delays else 0.0
        streaming_latency_ms = (config.WINDOW_LENGTH_SECS * 1000.0 if c_win == 1 else (config.WINDOW_LENGTH_SECS + (c_win - 1) * config.HOP_LENGTH_SECS) * 1000.0) + mean_inf_ms

        res_row = {
            "name": cfg["name"],
            "threshold": th,
            "threshold_off": th_off,
            "confirm_windows": c_win,
            "cooldown_secs": cool,
            "window_metrics": {
                "accuracy": round(acc, 2),
                "precision": round(p_win, 2),
                "recall": round(r_win, 2),
                "f1": round(f1_win, 2),
                "roc_auc": round(val_roc_auc * 100.0, 2),
                "pr_auc": round(val_pr_auc * 100.0, 2),
                "confusion_matrix": {"tp": int(tp), "fp": int(fp), "tn": int(tn), "fn": int(fn)}
            },
            "event_metrics": {
                "physical_events_total": total_physical_events,
                "tp_events": tp_ev_total,
                "fn_events": fn_ev_total,
                "fp_events_bg": fp_ev_bg,
                "fp_events_gunshot": fp_ev_gunshot,
                "total_fp_events": total_fp_events,
                "event_recall": round(evt_rec, 2),
                "event_precision": round(evt_prec, 2),
                "event_f1": round(evt_f1, 2),
                "recording_recall": round(rec_recall, 2),
                "duplicate_alerts": dups
            },
            "false_alert_rates": {
                "rate_policy_a_per_hr": round(rate_a, 2),
                "rate_policy_b_per_hr": round(rate_b, 2),
                "poisson_95_ci_a": [round(ci_a_low, 2), round(ci_a_high, 2)]
            },
            "timing_and_latency": {
                "mean_detection_delay_ms": round(onset_offset_ms, 2),
                "model_inference_latency_ms": round(mean_inf_ms, 2),
                "end_to_end_streaming_delay_ms": round(streaming_latency_ms, 2)
            }
        }
        results_table.append(res_row)

        print(f"{cfg['name'][:27]:<27} | {th:.3f} | {c_win:^5} | {acc:5.1f} | {p_win:5.1f} | {r_win:5.1f} | {f1_win:5.1f} | {evt_prec:5.1f} | {evt_rec:5.1f} | {evt_f1:5.1f} | {rec_recall:5.1f} | {rate_a:12.1f} | {streaming_latency_ms:6.1f}")

    print("------------------------------------------------------------------------------------------------------------------------------\n")

    # Validation Selection Rule Implementation:
    # 1. Filter candidates with Event Recall >= 90.0%
    # 2. Among these, rank by minimizing Policy A false alerts/hour
    # 3. Break ties with Event F1
    valid_candidates = [r for r in results_table if r["event_metrics"]["event_recall"] >= 90.0]
    if valid_candidates:
        selected_config = min(valid_candidates, key=lambda x: (x["false_alert_rates"]["rate_policy_a_per_hr"], -x["event_metrics"]["event_f1"]))
    else:
        selected_config = max(results_table, key=lambda x: x["event_metrics"]["event_f1"])

    print(f">>> VALIDATION-SELECTED OPTIMAL OPERATING POINT:")
    print(f"    Name: {selected_config['name']}")
    print(f"    Threshold: {selected_config['threshold']}")
    print(f"    Confirm Windows: {selected_config['confirm_windows']}")
    print(f"    Cooldown: {selected_config['cooldown_secs']}s")
    print(f"    Validation Event Recall: {selected_config['event_metrics']['event_recall']}%")
    print(f"    Validation Event Precision: {selected_config['event_metrics']['event_precision']}%")
    print(f"    Validation False Alerts/hr (Policy A): {selected_config['false_alert_rates']['rate_policy_a_per_hr']}")
    print(f"    End-to-End Streaming Latency: {selected_config['timing_and_latency']['end_to_end_streaming_delay_ms']} ms\n")

    output_payload = {
        "report_title": "Phase 7 Validation Operating Point Optimization & Model Comparison Report",
        "evaluator": "Senior Acoustic ML Engineer",
        "dataset_split": "Validation Split Only (No Independent Test Set Exposure)",
        "safety_designation": "RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY",
        "system_profiling": {
            "initial_memory_mb": round(mem_initial_mb, 2),
            "final_memory_mb": round(mem_final_mb, 2),
            "memory_usage_delta_mb": mem_usage_delta_mb,
            "inference_latency_ms": {
                "mean": round(mean_inf_ms, 2),
                "p50": round(p50_inf_ms, 2),
                "p95": round(p95_inf_ms, 2),
                "p99": round(p99_inf_ms, 2)
            }
        },
        "validation_selection_rule": (
            "Select operating point on validation data that satisfies Event Recall >= 90.0% "
            "while minimizing false alert rate per hour under continuous background audio, breaking ties with Event F1."
        ),
        "selected_configuration": selected_config,
        "candidate_grid_results": results_table
    }

    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(output_payload, f, indent=2)

    print(f"Saved complete validation model comparison to: {out_json}")


if __name__ == "__main__":
    benchmark_operating_points()
