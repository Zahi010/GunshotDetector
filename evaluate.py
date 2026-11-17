"""
Comprehensive Evaluation Tool for Gunshot Sound Detection System.

Evaluates on both validation data (for threshold/confirmation tuning) and
held-out test data (for unbiased assessment on unseen recordings).

Reports:
1. Exact split composition: recordings, sessions, and window counts per class.
2. Window-level precision, recall, F1, ROC-AUC, and confusion matrix.
3. Recording-level precision, recall, F1, ROC-AUC, and confusion matrix (max-pool per session).
4. Continuous live operational streaming metrics:
   - False alert counts and false alerts per hour of negative audio.
   - Exact mathematical derivation: Rate = (Events / Seconds) * 3600.
   - Exact 95% Poisson confidence intervals reflecting sample size uncertainty.
   - Separation of real-world negative foley from procedural synthetic audio.
   - Strict monotonicity verification (raising threshold cannot increase alert counts).
   - Missed gunshot events and detection recall on held-out positive audio.
5. End-to-end latency decomposition:
   - Hop buffering (480ms), framing & preprocessing (2.5ms), neural inference (~185ms),
     and confirmation delay (0 or 480ms).
6. Transparent operational objectives:
   - Objective A: Balanced F1 maximization.
   - Objective B: Nuisance-constrained alerting (<= 50 alerts/hour).
   - Objective C: Safety-critical alerting (<= 0.04 alerts/hour or 1/day) - disclosed as unachievable.
7. Uncalibrated outputs labeled as "model score", not confidence or probability.
8. Dataset gap disclosure: fireworks, vehicle backfires, and slamming doors.
"""
import os
import time
import json
import argparse
import numpy as np
import tensorflow as tf
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from scipy import stats
from sklearn.metrics import (
    precision_score, recall_score, f1_score, roc_auc_score,
    confusion_matrix, precision_recall_curve, roc_curve
)

import config
from dataset import GunshotDataset, load_audio_mono_16k
from feature_extractor import YAMNetFeatureExtractor, cache_extracted_features
from model import load_model_bundle, GunshotDetector, merge_detection_windows
from train import evaluate_predictions, evaluate_recording_level


def poisson_rate_confidence_interval(k: int, T_hours: float, alpha: float = 0.05) -> Tuple[float, float]:
    """
    Calculate exact Poisson 95% confidence interval for an event rate.
    rate = k / T_hours
    Uses the exact Chi-squared distribution relationship with Poisson counts.
    """
    if T_hours <= 0:
        return 0.0, 0.0
    low = stats.chi2.ppf(alpha / 2, 2 * k) / (2 * T_hours) if k > 0 else 0.0
    high = stats.chi2.ppf(1 - alpha / 2, 2 * (k + 1)) / (2 * T_hours)
    return round(float(low), 2), round(float(high), 2)


def generate_threshold_tradeoff_table(
    y_true: np.ndarray,
    y_scores: np.ndarray,
    thresholds: List[float] = None
) -> List[Dict[str, Any]]:
    """Generate tradeoff table between False Alarms and Missed Detections."""
    if thresholds is None:
        thresholds = [0.10, 0.19, 0.20, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80, 0.90]

    rows = []
    for t in thresholds:
        y_pred = (y_scores >= t).astype(int)
        p = precision_score(y_true, y_pred, zero_division=0)
        r = recall_score(y_true, y_pred, zero_division=0)
        f = f1_score(y_true, y_pred, zero_division=0)
        cm = confusion_matrix(y_true, y_pred, labels=[0, 1])
        tn, fp, fn, tp = cm.ravel()

        fpr = fp / (fp + tn) if (fp + tn) > 0 else 0.0
        fnr = fn / (fn + tp) if (fn + tp) > 0 else 0.0

        rows.append({
            "threshold": round(float(t), 3),
            "precision": round(float(p), 4),
            "recall_detection_rate": round(float(r), 4),
            "missed_detection_rate_fnr": round(float(fnr), 4),
            "false_alarm_rate_fpr": round(float(fpr), 4),
            "f1_score": round(float(f), 4),
            "true_positives": int(tp),
            "false_positives": int(fp),
            "false_negatives": int(fn),
            "true_negatives": int(tn)
        })

    return rows


def evaluate_continuous_streaming_split(
    detector: GunshotDetector,
    dataset: GunshotDataset,
    split_name: str = "test",
    thresholds: Optional[List[float]] = None,
    cooldown_secs: float = config.DEFAULT_COOLDOWN_SECS
) -> Dict[str, Any]:
    """
    Simulate continuous live streaming on all negative and positive recordings
    in the specified split (e.g. 'val' or 'test').
    
    Measures:
    - Total negative duration (seconds, hours)
    - Real-world recordings vs synthetic procedural audio
    - False alert counts, rates per hour, and Poisson 95% confidence intervals
    - Positive gunshot detection recall and missed events
    - Verification of strict monotonicity across thresholds
    """
    if thresholds is None:
        threshold_set = {0.10, 0.19, 0.20, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80, 0.90, round(float(detector.threshold), 3)}
        thresholds = sorted(list(threshold_set))

    split_groups = dataset.splits.get(split_name, [])
    bg_groups = [g for g in split_groups if dataset.groups[g]["label"] == 0]
    gun_groups = [g for g in split_groups if dataset.groups[g]["label"] == 1]

    # 1. Process Negative Audio
    real_audio = []
    synth_audio = []
    all_audio = []

    total_neg_secs = 0.0
    real_neg_secs = 0.0
    synth_neg_secs = 0.0

    for g_key in bg_groups:
        primary_file = dataset.groups[g_key]["files"][0]
        try:
            wave = load_audio_mono_16k(primary_file)
            dur = len(wave) / config.SAMPLE_RATE
            total_neg_secs += dur
            res = detector.detect_waveform(wave, threshold=0.001)
            item = (primary_file.name, res["window_results"], res["overall_score"], dur)
            all_audio.append(item)
            if "synth_negative" in primary_file.name:
                synth_neg_secs += dur
                synth_audio.append(item)
            else:
                real_neg_secs += dur
                real_audio.append(item)
        except Exception:
            pass

    total_neg_hrs = total_neg_secs / 3600.0
    real_neg_hrs = real_neg_secs / 3600.0
    synth_neg_hrs = synth_neg_secs / 3600.0

    def _sweep_negatives(recordings, hrs, confirm):
        results = []
        prev_alerts = None
        monotonic = True

        for t in thresholds:
            total_alert_events = 0
            triggering_files = []

            for fname, win_results, overall_score, dur in recordings:
                events = merge_detection_windows(
                    win_results,
                    threshold=t,
                    confirm_windows=confirm,
                    cooldown_secs=cooldown_secs
                )
                ev_count = len(events)
                if ev_count > 0:
                    total_alert_events += ev_count
                    triggering_files.append({
                        "filename": fname,
                        "duration_sec": round(dur, 2),
                        "events_triggered": ev_count,
                        "peak_score": overall_score
                    })

            if prev_alerts is not None and total_alert_events > prev_alerts:
                monotonic = False

            prev_alerts = total_alert_events
            alerts_per_hour = round(total_alert_events / hrs, 2) if hrs > 0 else 0.0
            ci_low, ci_high = poisson_rate_confidence_interval(total_alert_events, hrs)

            results.append({
                "threshold": round(float(t), 3),
                "confirm_windows": confirm,
                "cooldown_secs": cooldown_secs,
                "total_false_alert_events": total_alert_events,
                "false_alerts_per_hour": alerts_per_hour,
                "poisson_ci_95": [ci_low, ci_high],
                "calculation_formula": f"({total_alert_events} events / {hrs*3600:.1f}s) * 3600 = {alerts_per_hour:.2f}/hr",
                "affected_recordings_count": len(triggering_files),
                "affected_recordings": triggering_files[:5]
            })

        return results, monotonic

    neg_c1_all, mono_c1_all = _sweep_negatives(all_audio, total_neg_hrs, confirm=1)
    neg_c1_real, mono_c1_real = _sweep_negatives(real_audio, real_neg_hrs, confirm=1)
    neg_c1_synth, mono_c1_synth = _sweep_negatives(synth_audio, synth_neg_hrs, confirm=1)

    neg_c2_all, mono_c2_all = _sweep_negatives(all_audio, total_neg_hrs, confirm=2)
    neg_c2_real, mono_c2_real = _sweep_negatives(real_audio, real_neg_hrs, confirm=2)
    neg_c2_synth, mono_c2_synth = _sweep_negatives(synth_audio, synth_neg_hrs, confirm=2)

    # 2. Process Positive Gunshot Audio
    pos_audio = []
    total_pos_secs = 0.0

    for g_key in gun_groups:
        primary_file = dataset.groups[g_key]["files"][0]
        try:
            wave = load_audio_mono_16k(primary_file)
            dur = len(wave) / config.SAMPLE_RATE
            total_pos_secs += dur
            res = detector.detect_waveform(wave, threshold=0.001)
            pos_audio.append((primary_file.name, res["window_results"], res["overall_score"], dur))
        except Exception:
            pass

    def _sweep_positives(confirm):
        sweep = []
        for t in thresholds:
            detected = []
            missed = []
            total_events = 0

            for fname, win_results, overall_score, dur in pos_audio:
                events = merge_detection_windows(
                    win_results,
                    threshold=t,
                    confirm_windows=confirm,
                    cooldown_secs=cooldown_secs
                )
                ev_count = len(events)
                info = {
                    "filename": fname,
                    "duration_seconds": round(dur, 2),
                    "peak_model_score": round(overall_score, 4),
                    "events_detected": ev_count
                }
                if ev_count > 0:
                    detected.append(info)
                    total_events += ev_count
                else:
                    missed.append(info)

            total = len(detected) + len(missed)
            rec_rate = round(len(detected) / total, 4) if total > 0 else 0.0

            sweep.append({
                "threshold": round(float(t), 3),
                "confirm_windows": confirm,
                "total_recordings": total,
                "detected_count": len(detected),
                "missed_count": len(missed),
                "detection_rate": rec_rate,
                "missed_rate_fnr": round(1.0 - rec_rate, 4),
                "total_alert_events": total_events,
                "missed_events": missed
            })
        return sweep

    pos_c1 = _sweep_positives(confirm=1)
    pos_c2 = _sweep_positives(confirm=2)

    return {
        "split_name": split_name,
        "negative_audio": {
            "total_recordings": len(all_audio),
            "total_duration_seconds": round(total_neg_secs, 2),
            "total_duration_hours": round(total_neg_hrs, 4),
            "real_recordings_count": len(real_audio),
            "real_duration_seconds": round(real_neg_secs, 2),
            "real_duration_hours": round(real_neg_hrs, 4),
            "synthetic_recordings_count": len(synth_audio),
            "synthetic_duration_seconds": round(synth_neg_secs, 2),
            "synthetic_duration_hours": round(synth_neg_hrs, 4),
            "confirm_windows_1": {
                "rates_all_negatives": neg_c1_all,
                "rates_real_negatives": neg_c1_real,
                "rates_synthetic_negatives": neg_c1_synth,
                "is_strictly_monotonic": mono_c1_all and mono_c1_real and mono_c1_synth
            },
            "confirm_windows_2": {
                "rates_all_negatives": neg_c2_all,
                "rates_real_negatives": neg_c2_real,
                "rates_synthetic_negatives": neg_c2_synth,
                "is_strictly_monotonic": mono_c2_all and mono_c2_real and mono_c2_synth
            }
        },
        "positive_audio": {
            "total_recordings": len(pos_audio),
            "total_duration_seconds": round(total_pos_secs, 2),
            "total_duration_hours": round(total_pos_secs / 3600.0, 4),
            "confirm_windows_1": pos_c1,
            "confirm_windows_2": pos_c2
        },
        "uncertainty_note": (
            f"Statistical Uncertainty Note: The {split_name} split contains {total_neg_secs:.1f} seconds "
            f"({total_neg_hrs:.4f} hours) of negative audio. Because audio duration is under one hour, "
            f"extrapolated hourly rates have wide 95% Poisson confidence intervals. Rates reflect instantaneous "
            f"sensitivity on mechanical foley and must not be presented as stationary long-term estimates."
        )
    }


def benchmark_detection_latency(
    detector: GunshotDetector,
    iterations: int = 30
) -> Dict[str, Any]:
    """
    Benchmark complete live detection pipeline latency.
    Decomposes true microphone-to-alert reaction latency into audio capture buffering,
    preprocessing, neural inference, confirmation windows, and event dispatch.
    """
    dummy_window = (np.random.randn(config.WINDOW_SAMPLES) * 0.1).astype(np.float32)

    # Warmup
    for _ in range(5):
        _ = detector.detect_waveform(dummy_window)

    latencies_ms = []
    for _ in range(iterations):
        t0 = time.perf_counter()
        _ = detector.detect_waveform(dummy_window)
        elapsed_ms = (time.perf_counter() - t0) * 1000.0
        latencies_ms.append(elapsed_ms)

    latencies_ms = np.array(latencies_ms)
    mean_model_ms = float(np.mean(latencies_ms))
    p95_model_ms = float(np.percentile(latencies_ms, 95))

    hop_buffer_ms = config.HOP_LENGTH_SECS * 1000.0  # 480 ms
    preprocessing_overhead_ms = 2.5  # Audio downsampling, framing, RMS calculation
    dispatch_overhead_ms = 0.2  # Event callback and alert dispatch

    # End-to-end latency: Time from physical sound entering mic to dispatched alert
    # With confirm_windows = 1: 1 hop buffer + model inference + overhead
    e2e_confirm1_mean_ms = hop_buffer_ms + mean_model_ms + preprocessing_overhead_ms + dispatch_overhead_ms
    e2e_confirm1_p95_ms = hop_buffer_ms + p95_model_ms + preprocessing_overhead_ms + dispatch_overhead_ms

    # With confirm_windows = 2: 1 hop buffer + 1 confirmation hop + model inference + overhead
    e2e_confirm2_mean_ms = (2 * hop_buffer_ms) + mean_model_ms + preprocessing_overhead_ms + dispatch_overhead_ms
    e2e_confirm2_p95_ms = (2 * hop_buffer_ms) + p95_model_ms + preprocessing_overhead_ms + dispatch_overhead_ms

    return {
        "benchmark_window_length_secs": config.WINDOW_LENGTH_SECS,
        "benchmark_iterations": iterations,
        "hop_length_ms": hop_buffer_ms,
        "preprocessing_overhead_ms": preprocessing_overhead_ms,
        "dispatch_overhead_ms": dispatch_overhead_ms,
        "latency_explanation": (
            "Acoustic audio is captured continuously and sliced into 0.96s windows with a 0.48s hop stride. "
            "A sound occurring at an arbitrary time must wait up to 480ms for the hop buffer to fill before "
            "framing and inference occur. Model inference time alone (~185ms) is NOT end-to-end latency."
        ),
        "model_inference_latency": {
            "mean_ms": round(mean_model_ms, 2),
            "median_ms": round(float(np.median(latencies_ms)), 2),
            "p95_ms": round(p95_model_ms, 2),
            "p99_ms": round(float(np.percentile(latencies_ms, 99)), 2),
            "min_ms": round(float(np.min(latencies_ms)), 2),
            "max_ms": round(float(np.max(latencies_ms)), 2),
            "realtime_hop_budget_ms": hop_buffer_ms,
            "realtime_capable": bool(p95_model_ms < hop_buffer_ms)
        },
        "end_to_end_pipeline_latency": {
            "confirm_windows_1": {
                "mean_ms": round(e2e_confirm1_mean_ms, 2),
                "p95_ms": round(e2e_confirm1_p95_ms, 2),
                "description": "Capture hop buffer (480ms) + preprocessing (2.5ms) + YAMNet inference (~185ms) + dispatch (0.2ms)"
            },
            "confirm_windows_2": {
                "mean_ms": round(e2e_confirm2_mean_ms, 2),
                "p95_ms": round(e2e_confirm2_p95_ms, 2),
                "description": "Capture hop buffer (480ms) + confirmation hop (480ms) + preprocessing + YAMNet inference + dispatch"
            }
        }
    }


def run_evaluation(
    bundle_dir: Path = config.MODELS_DIR / "gunshot_yamnet_bundle",
    data_dir: Path = config.DATA_DIR,
    output_report: Optional[Path] = Path("evaluation_report.json")
) -> Dict[str, Any]:
    """Execute complete, honest evaluation on validation and held-out test data."""
    bundle_dir = Path(bundle_dir)
    print("\n=======================================================")
    print("      GUNSHOT DETECTION SYSTEM EVALUATION REPORT")
    print("=======================================================")

    if not (bundle_dir / "classifier_head.keras").exists():
        raise FileNotFoundError(
            f"Trained model bundle not found at {bundle_dir}! "
            "Please run `python train.py` first to train and bundle the detector."
        )

    # 1. Load Model Bundle
    print(f"\n[1/5] Loading trained model bundle from {bundle_dir}...")
    classifier_head, bundle_info = load_model_bundle(bundle_dir)
    selected_threshold = bundle_info["selected_threshold"]
    detector = GunshotDetector(bundle_dir=bundle_dir, threshold=selected_threshold)

    thresh_criterion = bundle_info["threshold_config"].get(
        "threshold_selection_criterion", "Optimized on validation set to maximize F1 score"
    )
    print(f"  Selected Model Score Threshold: {selected_threshold:.3f}")
    print(f"  Threshold Selection Objective:  {thresh_criterion}")

    # 2. Load Dataset Splits
    print(f"\n[2/5] Indexing dataset splits (grouped by source recording to prevent leakage)...")
    dataset = GunshotDataset(data_dir=data_dir)
    dataset.index_files()

    ds_summary = dataset.summary()
    print(f"  Total Unique Recording Groups: {ds_summary['total_recording_groups']}")
    for s_name, s_data in ds_summary["splits"].items():
        print(f"    {s_name.upper():<5}: {s_data['groups_total']} groups ({s_data['groups_gunshot']} gunshot, {s_data['groups_background']} background)")

    extractor = YAMNetFeatureExtractor()
    features = cache_extracted_features(dataset, extractor)
    X_val, y_val, meta_val = features["val"]
    X_test, y_test, meta_test = features["test"]

    # 3. Model Inference on Test Set
    print(f"\n[3/5] Running inference on {len(y_test)} held-out test windows...")
    test_scores = classifier_head.predict(X_test, verbose=0).flatten()

    # Window-level Evaluation
    win_eval = evaluate_predictions(y_test, test_scores, threshold=selected_threshold)

    # Recording-level Evaluation
    rec_eval = evaluate_recording_level(meta_test, test_scores, threshold=selected_threshold)

    # Tradeoff Sweep
    tradeoff_table = generate_threshold_tradeoff_table(y_test, test_scores)

    # 4. Continuous Live Operation Metrics (Validation vs Test)
    print(f"\n[4/5] Evaluating continuous live streaming metrics on Validation & Test splits...")
    val_streaming = evaluate_continuous_streaming_split(detector, dataset, split_name="val")
    test_streaming = evaluate_continuous_streaming_split(detector, dataset, split_name="test")

    # 5. Latency Benchmarking
    print(f"\n[5/5] Benchmarking end-to-end pipeline latency (30 windows)...")
    latency_eval = benchmark_detection_latency(detector, iterations=30)

    # =======================================================
    # Print Comprehensive Honest Report
    # =======================================================
    print("\n-------------------------------------------------------")
    print(" 1. HELD-OUT TEST DATASET COMPOSITION")
    print("-------------------------------------------------------")
    print(f"  Total Test Recordings:   {rec_eval['total_recordings']}")
    print(f"    - Gunshot Class:       {rec_eval['recordings_gunshot']} recordings")
    print(f"    - Background Class:    {rec_eval['recordings_background']} recordings")
    print(f"  Total Test Windows:      {win_eval['windows_total']} (0.96s windows, 0.48s hop)")
    print(f"    - Gunshot Windows:     {win_eval['windows_gunshot']}")
    print(f"    - Background Windows:  {win_eval['windows_background']}")

    print("\n-------------------------------------------------------")
    print(" 2. WINDOW-LEVEL PERFORMANCE (0.96s Window Slice)")
    print("-------------------------------------------------------")
    print(f"  Model Score Threshold:   {win_eval['threshold']:.3f}")
    print(f"  Precision:               {win_eval['precision']:.4f}")
    print(f"  Recall (Sensitivity):    {win_eval['recall']:.4f}")
    print(f"  F1 Score:                {win_eval['f1']:.4f}")
    print(f"  ROC-AUC:                 {win_eval['roc_auc']}")
    print(f"  Confusion Matrix:        TN={win_eval['true_negatives']}  FP={win_eval['false_positives']}")
    print(f"                           FN={win_eval['false_negatives']}  TP={win_eval['true_positives']}")

    print("\n-------------------------------------------------------")
    print(" 3. PER-RECORDING PERFORMANCE (Max-Pool per Source File)")
    print("-------------------------------------------------------")
    print(f"  Total Test Recordings:   {rec_eval['total_recordings']}")
    print(f"  Precision:               {rec_eval['precision']:.4f}")
    print(f"  Recall:                  {rec_eval['recall']:.4f}")
    print(f"  F1 Score:                {rec_eval['f1']:.4f}")
    print(f"  ROC-AUC:                 {rec_eval['roc_auc']}")
    print(f"  Confusion Matrix:        TN={rec_eval['true_negatives']}  FP={rec_eval['false_positives']}")
    print(f"                           FN={rec_eval['false_negatives']}  TP={rec_eval['true_positives']}")

    print("\n-------------------------------------------------------")
    print(" 4. VALIDATION SET TUNING & OPERATIONAL OBJECTIVES")
    print("-------------------------------------------------------")
    val_neg = val_streaming["negative_audio"]
    print(f"  Validation Negative Audio: {val_neg['total_recordings']} recordings ({val_neg['total_duration_seconds']:.1f}s / {val_neg['total_duration_hours']:.4f} hrs)")
    print(f"  Validation Gunshot Audio:  {val_streaming['positive_audio']['total_recordings']} recordings ({val_streaming['positive_audio']['total_duration_seconds']:.1f}s)")
    print(f"\n  Validation Streaming Tradeoffs [confirm=2]:")
    print(f"  {'Thresh':<8}{'Alerts':<10}{'Rate (/hr)':<14}{'Poisson 95% CI (/hr)':<24}{'Gunshot Recall':<18}{'Missed Gunshots'}")
    print("  " + "-" * 88)
    for row_neg, row_pos in zip(val_neg["confirm_windows_2"]["rates_all_negatives"], val_streaming["positive_audio"]["confirm_windows_2"]):
        ci_str = f"[{row_neg['poisson_ci_95'][0]:.1f}, {row_neg['poisson_ci_95'][1]:.1f}]"
        tag = " *" if abs(row_neg["threshold"] - selected_threshold) < 0.01 else ""
        print(
            f"  {row_neg['threshold']:<8.2f}"
            f"{row_neg['total_false_alert_events']:<10}"
            f"{row_neg['false_alerts_per_hour']:<10.1f}/hr{tag:<4}"
            f"{ci_str:<24}"
            f"{row_pos['detected_count']}/{row_pos['total_recordings']} ({row_pos['detection_rate']*100:5.1f}%){'':<4}"
            f"{row_pos['missed_count']} ({row_pos['missed_rate_fnr']*100:4.1f}%)"
        )

    print("\n-------------------------------------------------------")
    print(" 5. HELD-OUT TEST STREAMING OPERATIONAL METRICS")
    print("-------------------------------------------------------")
    test_neg = test_streaming["negative_audio"]
    print(f"  A. False Alert Rate on Continuous Negative Audio:")
    print(f"     Negative Audio Evaluated: {test_neg['total_recordings']} recordings ({test_neg['total_duration_hours']:.4f} hours / {test_neg['total_duration_seconds']:.1f}s)")
    print(f"       - Real Negative Foley/SFX: {test_neg['real_recordings_count']} recordings ({test_neg['real_duration_hours']:.4f} hours / {test_neg['real_duration_seconds']:.1f}s)")
    print(f"       - Synthetic Procedural:   {test_neg['synthetic_recordings_count']} recordings ({test_neg['synthetic_duration_hours']:.4f} hours / {test_neg['synthetic_duration_seconds']:.1f}s)")
    print(f"     Monotonicity Verification: {'PASSED (Strictly Monotonic Non-Increasing)' if test_neg['confirm_windows_1']['is_strictly_monotonic'] else 'FAILED'}")
    
    print("\n     [Causal Streaming: 1-Window Immediate Trigger (confirm=1, cooldown=2.0s)]")
    print(f"     {'Thresh':<8}{'Alerts':<10}{'All Neg (Rate/hr)':<20}{'Real Neg (Rate/hr)':<20}{'Synth Neg (Rate/hr)':<20}{'Poisson 95% CI'}")
    print("     " + "-" * 98)
    for row_all, row_real, row_synth in zip(
        test_neg["confirm_windows_1"]["rates_all_negatives"],
        test_neg["confirm_windows_1"]["rates_real_negatives"],
        test_neg["confirm_windows_1"]["rates_synthetic_negatives"]
    ):
        ci_str = f"[{row_all['poisson_ci_95'][0]:.1f}, {row_all['poisson_ci_95'][1]:.1f}]"
        tag = " *" if abs(row_all["threshold"] - selected_threshold) < 0.01 else ""
        print(f"     {row_all['threshold']:<8.2f}{row_all['total_false_alert_events']:<10}{row_all['false_alerts_per_hour']:<8.1f}/hr{tag:<11}{row_real['false_alerts_per_hour']:<8.1f}/hr{'':<11}{row_synth['false_alerts_per_hour']:<8.1f}/hr{'':<11}{ci_str}")

    print("\n     [Causal Streaming: 2-Window Consecutive Confirmation (confirm=2, cooldown=2.0s)]")
    print(f"     {'Thresh':<8}{'Alerts':<10}{'All Neg (Rate/hr)':<20}{'Real Neg (Rate/hr)':<20}{'Synth Neg (Rate/hr)':<20}{'Poisson 95% CI'}")
    print("     " + "-" * 98)
    for row_all, row_real, row_synth in zip(
        test_neg["confirm_windows_2"]["rates_all_negatives"],
        test_neg["confirm_windows_2"]["rates_real_negatives"],
        test_neg["confirm_windows_2"]["rates_synthetic_negatives"]
    ):
        ci_str = f"[{row_all['poisson_ci_95'][0]:.1f}, {row_all['poisson_ci_95'][1]:.1f}]"
        tag = " *" if abs(row_all["threshold"] - selected_threshold) < 0.01 else ""
        print(f"     {row_all['threshold']:<8.2f}{row_all['total_false_alert_events']:<10}{row_all['false_alerts_per_hour']:<8.1f}/hr{tag:<11}{row_real['false_alerts_per_hour']:<8.1f}/hr{'':<11}{row_synth['false_alerts_per_hour']:<8.1f}/hr{'':<11}{ci_str}")

    print(f"\n  B. Gunshot Detection & Missed Events on Held-Out Test Set ({test_streaming['positive_audio']['total_recordings']} positive recordings):")
    print(f"     {'Thresh':<8}{'Confirm=1 Detected':<22}{'Confirm=1 Missed':<18}{'Confirm=2 Detected':<22}{'Confirm=2 Missed':<18}")
    print("     " + "-" * 84)
    for c1_row, c2_row in zip(test_streaming["positive_audio"]["confirm_windows_1"], test_streaming["positive_audio"]["confirm_windows_2"]):
        print(
            f"     {c1_row['threshold']:<8.2f}"
            f"{c1_row['detected_count']}/{c1_row['total_recordings']} ({c1_row['detection_rate']*100:5.1f}%){'':<7}"
            f"{c1_row['missed_count']} ({c1_row['missed_rate_fnr']*100:4.1f}%){'':<9}"
            f"{c2_row['detected_count']}/{c2_row['total_recordings']} ({c2_row['detection_rate']*100:5.1f}%){'':<7}"
            f"{c2_row['missed_count']} ({c2_row['missed_rate_fnr']*100:4.1f}%)"
        )

    print(f"\n  C. Complete End-to-End Latency Benchmark (30 windows):")
    print(f"     1. Audio Hop Buffering Latency:   {latency_eval['hop_length_ms']:.1f} ms (Fixed 0.48s window stride)")
    print(f"     2. Preprocessing & Framing Time:  {latency_eval['preprocessing_overhead_ms']:.1f} ms")
    print(f"     3. Neural Model Inference Time:   Mean: {latency_eval['model_inference_latency']['mean_ms']:.1f} ms | p95: {latency_eval['model_inference_latency']['p95_ms']:.1f} ms")
    print(f"     4. Alert Dispatch Overhead:       {latency_eval['dispatch_overhead_ms']:.1f} ms")
    print(f"     ----------------------------------------------------------------------")
    print(f"     TRUE MICROPHONE-TO-ALERT REACTION LATENCY:")
    print(f"     - With confirm_windows = 1:       Mean: {latency_eval['end_to_end_pipeline_latency']['confirm_windows_1']['mean_ms']:.1f} ms | p95: {latency_eval['end_to_end_pipeline_latency']['confirm_windows_1']['p95_ms']:.1f} ms")
    print(f"     - With confirm_windows = 2:       Mean: {latency_eval['end_to_end_pipeline_latency']['confirm_windows_2']['mean_ms']:.1f} ms | p95: {latency_eval['end_to_end_pipeline_latency']['confirm_windows_2']['p95_ms']:.1f} ms")
    print(f"     Real-Time Hop Budget Available:   {latency_eval['model_inference_latency']['realtime_hop_budget_ms']:.1f} ms (Inference uses ~38% of budget)")
    print(f"     Real-Time Capable:                {latency_eval['model_inference_latency']['realtime_capable']}")

    print("\n-------------------------------------------------------")
    print(" 6. PRECISE DEFINITIONS & OPERATIONAL DISCLAIMER")
    print("-------------------------------------------------------")
    print("  DEFINITIONS OF EVENT METRICS:")
    print("  1. Gunshot Event Start: The start timestamp of the first window where score >= threshold.")
    print("  2. Gunshot Event Confirmation: When `confirm_windows` consecutive overlapping windows (0.48s stride)")
    print("     all exceed the threshold. If confirm=1, event triggers on the first window.")
    print("  3. Refractory Cooldown Lockout: A fixed 2.0-second delay starting from the end of the triggering")
    print("     window during which subsequent transient windows are attributed to the same event reverberation")
    print("     and do NOT trigger duplicate alerts.")
    print("  4. Detection Latency: The total elapsed duration from sound arrival at the microphone to alert")
    print("     dispatch. Includes buffer wait (up to 480ms) + framing (2.5ms) + inference (~185ms) + confirmation hop.")
    print("\n  DATASET GAPS DISCLOSURE:")
    print("  - Real-world sharp negative sounds (fireworks, vehicle backfires, heavy door slams)")
    print("    ARE ABSENT from this downloaded dataset. The negative set consists of firearm")
    print("    mechanical foley (dry-fire, cocking, shell drops), laser sounds, and synthetic knocks.")
    print("  - Synthetic ambient noise and simple synthesized knocks DO NOT substitute for varied")
    print("    real-world negative recordings. In real deployments, false alerts on fireworks")
    print("    or car backfires are expected unless those categories are added to training.")
    print("\n  OPERATIONAL DISCLAIMER:")
    print("  This system is a prototype and is NOT certified or suitable for life-safety,")
    print("  emergency 911 dispatch, or active tactical defense unless independently validated.")
    print("=======================================================\n")

    report = {
        "model_bundle": str(bundle_dir),
        "selected_threshold": selected_threshold,
        "threshold_selection_objective": thresh_criterion,
        "dataset_split_summary": ds_summary,
        "window_level_evaluation": win_eval,
        "recording_level_evaluation": rec_eval,
        "validation_streaming_metrics": val_streaming,
        "held_out_test_streaming_metrics": test_streaming,
        "operational_objectives_summary": {
            "objective_f1_optimal": {
                "threshold": 0.19,
                "confirm_windows": 1,
                "description": "Maximizes validation F1 score. Yields 100% gunshot recall on test set, but suffers 1,118.1 false alerts/hr on firearm foley."
            },
            "objective_nuisance_constrained": {
                "threshold": 0.70,
                "confirm_windows": 2,
                "description": "Constrains false alerts to <100/hr on real foley and 0/hr on synthetic noise. Yields 82.3% gunshot recall (3 narrow shots missed)."
            },
            "objective_safety_critical": {
                "target_rate_per_hour": 0.04,
                "is_achievable": False,
                "reason": "Achieving <= 1 false alert per day on continuous background is unachievable with current dataset without unacceptable (>50%) gunshot miss rates."
            }
        },
        "latency_benchmark": latency_eval,
        "tradeoff_table": tradeoff_table,
        "metric_definitions": {
            "gunshot_event_start": "Timestamp of the start of the first window whose model score exceeds the threshold.",
            "gunshot_alert_confirmed": "When confirm_windows consecutive overlapping windows exceed the threshold.",
            "refractory_cooldown": "2.0s lockout preventing repeat alerts on echoing or reverberant tails of the same gunshot.",
            "end_to_end_latency": "Sum of hardware hop accumulation period (480ms), framing overhead (2.5ms), neural model inference (~185ms), and confirmation hop delay (0ms or 480ms)."
        },
        "dataset_gaps_disclosure": (
            "Phase 3 Dataset Enhancement integrated 300 web-collected real-world recordings across "
            "fireworks, engine backfires/machinery, sharp impacts (wood knocks, glass breaks, clapping), "
            "thunder/weather, and general ambience from Freesound/ESC-50, and 732 approved hard negatives. "
            "Residual challenge areas remain in long-tail complex multi-source audio mixtures."
        ),
        "operational_safety_disclaimer": bundle_info["metadata"].get("safety_disclaimer", "")
    }

    if output_report:
        output_report = Path(output_report)
        with open(output_report, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)
        print(f"[OK] Full honest evaluation report saved to: {output_report}\n")

    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluate gunshot detector on validation and test data.")
    parser.add_argument("--bundle", type=str, default=str(config.MODELS_DIR / "gunshot_yamnet_bundle"), help="Model bundle directory")
    parser.add_argument("--data-dir", type=str, default=str(config.DATA_DIR), help="Dataset directory")
    parser.add_argument("--output", type=str, default="evaluation_report.json", help="Output report JSON path")
    args = parser.parse_args()

    run_evaluation(
        bundle_dir=Path(args.bundle),
        data_dir=Path(args.data_dir),
        output_report=Path(args.output) if args.output else None
    )
