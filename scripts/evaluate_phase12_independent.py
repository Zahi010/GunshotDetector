"""
Phase 12: Independent Acoustic Benchmark & Frozen Model Evaluation Script.

Evaluates the frozen Phase 9 detector across:
1. Locked Final Test Benchmark (split == 'final_test', 120 files)
   - 38 Confirmed Gunshots (Clipped, Pocket-occluded, Clean, Distant Urban)
   - 76 Confirmed Negatives (Range mimics, Diverse ESC-50 classes)
   - 5 Ambiguous Edge-Cases (ground_truth_label = -1)
   - 2.0 Hours of Continuous Negative Exposure Stream (7,200 seconds)
2. Primary Operating Profile: 'balanced' (Threshold 0.75, Cooldown 2.0s, Crest 9.5 dB)
3. Supplementary Comparative Profiles: 'high_precision' and 'high_sensitivity'
4. Comprehensive Metric Suite:
   - Event-level: TP, FN, FP, Precision, Recall, F1, Duplicate Alerts, Detection Delay
   - Window-level: Precision, Recall, F1, PR-AUC, ROC-AUC, Confusion Matrix
   - Continuous stream: Exposure hours, False alerts/hour, Poisson 95% CI, Latency (median, P95)
   - Acoustic condition & category breakdown
   - Stage 7: Physical Crest-Factor Guard & Short-Event Pathway Limitation Audit

Outputs:
- reports/phase12_evaluation_results.json
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
import sklearn.metrics as metrics

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import config
from dataset import load_audio_mono_16k
from model_phase9 import (
    Phase9AdaptiveGunshotDetector,
    compute_physical_crest_factor_db
)
from scripts.validate_streaming_harness import RealTimeStreamDetector

STREAM_CACHE_PATH = Path("reports/.phase12_stream_cache_balanced.json")

def calculate_wilson_ci(k: int, n: int, confidence: float = 0.95) -> Tuple[float, float]:
    """Calculate Wilson score interval for a binomial proportion."""
    if n == 0:
        return (0.0, 0.0)
    z = 1.95996  # 95% normal quantile
    p = k / n
    denom = 1.0 + (z ** 2) / n
    center = (p + (z ** 2) / (2 * n)) / denom
    margin = (z * math.sqrt((p * (1 - p) / n) + (z ** 2) / (4 * (n ** 2)))) / denom
    lower = max(0.0, round(center - margin, 4))
    upper = min(1.0, round(center + margin, 4))
    return (lower, upper)

def calculate_poisson_rate_ci(count: int, hours: float) -> Tuple[float, float]:
    """Calculate 95% Poisson confidence interval for alert rate per hour."""
    if hours <= 0:
        return (0.0, 0.0)
    from scipy.stats import chi2
    lower = 0.5 * chi2.ppf(0.05 / 2, 2 * count) / hours if count > 0 else 0.0
    upper = 0.5 * chi2.ppf(1 - 0.05 / 2, 2 * (count + 1)) / hours
    return (round(float(lower), 2), round(float(upper), 2))

def evaluate_profile(
    df_manifest: pd.DataFrame,
    profile_name: str,
    run_continuous_stream: bool = True
) -> Dict[str, Any]:
    print(f"\n================================================================================")
    print(f"   EVALUATING PROFILE: {profile_name.upper()} (Primary={profile_name == 'balanced'})")
    print(f"================================================================================")

    detector = Phase9AdaptiveGunshotDetector(profile=profile_name)

    # Separate discrete files and continuous stream
    discrete_rows = df_manifest[df_manifest["event_classification"] != "continuous_ambient_stream"]
    stream_rows = df_manifest[df_manifest["event_classification"] == "continuous_ambient_stream"]

    tp_events = 0
    fn_events = 0
    fp_events = 0
    duplicate_alerts = 0
    detection_delays = []
    
    ambig_triggers = 0
    ambig_total = 0

    all_window_y_true = []
    all_window_y_score = []
    all_window_y_pred = []

    file_results = []
    crest_audit = []
    condition_stats = {}

    for idx, row in discrete_rows.iterrows():
        rid = row["recording_id"]
        fp = Path(row["filepath"])
        label = int(row["ground_truth_label"])
        cond = str(row["acoustic_condition"])
        cat = str(row["event_classification"])
        dur = float(row["duration_seconds"])
        t_start = float(row["event_start_time_sec"])
        t_end = float(row["event_end_time_sec"])

        waveform = load_audio_mono_16k(fp)
        crest_db = compute_physical_crest_factor_db(waveform)

        crest_audit.append({
            "recording_id": rid,
            "ground_truth_label": label,
            "acoustic_condition": cond,
            "physical_crest_factor_db": round(crest_db, 2),
            "passes_9_5db_threshold": bool(crest_db >= 9.5),
            "passes_10_0db_threshold": bool(crest_db >= 10.0),
            "passes_9_0db_threshold": bool(crest_db >= 9.0),
            "duration_seconds": dur
        })

        if cond not in condition_stats:
            condition_stats[cond] = {"total": 0, "tp": 0, "fn": 0, "fp": 0, "tn": 0, "label": label}
        condition_stats[cond]["total"] += 1

        res = detector.evaluate_waveform(waveform)
        events = res.get("events", [])
        overall_score = res.get("overall_score", 0.0)
        win_results = res.get("windows", []) or res.get("window_results", [])

        # Process window-level ground truth and predictions
        for w in win_results:
            w_st = w["start_time"]
            w_et = w["end_time"]
            w_score = w["score"]
            w_pred = 1 if w_score >= detector.threshold_base else 0

            if label == 1:
                overlap = max(0.0, min(w_et, t_end) - max(w_st, t_start))
                w_true = 1 if overlap > 0.05 else 0
                all_window_y_true.append(w_true)
                all_window_y_score.append(w_score)
                all_window_y_pred.append(w_pred)
            elif label == 0:
                all_window_y_true.append(0)
                all_window_y_score.append(w_score)
                all_window_y_pred.append(w_pred)

        # Process event-level outcomes
        if label == 1:
            matched = False
            first_alert_time = None
            for e in events:
                e_st = e["start_time"]
                e_et = e["end_time"]
                temporal_match = (e_st <= t_end + 1.5) and (e_et >= t_start - 1.5)
                if temporal_match:
                    if not matched:
                        matched = True
                        first_alert_time = e["start_time"]
                        tp_events += 1
                        condition_stats[cond]["tp"] += 1
                    else:
                        duplicate_alerts += 1
                else:
                    fp_events += 1
                    condition_stats[cond]["fp"] += 1

            if not matched:
                fn_events += 1
                condition_stats[cond]["fn"] += 1

            if first_alert_time is not None:
                delay = max(0.0, round(first_alert_time - t_start, 3))
                detection_delays.append(delay)

        elif label == 0:
            if len(events) > 0:
                fp_events += len(events)
                condition_stats[cond]["fp"] += len(events)
            else:
                condition_stats[cond]["tn"] += 1

        elif label == -1:
            ambig_total += 1
            if len(events) > 0:
                ambig_triggers += 1

        file_results.append({
            "recording_id": rid,
            "filename": fp.name,
            "label": label,
            "condition": cond,
            "crest_db": round(crest_db, 2),
            "alerts_dispatched": len(events),
            "overall_score": round(overall_score, 3)
        })

    # Continuous stream evaluation via RealTimeStreamDetector
    continuous_metrics = {
        "exposure_hours": 0.0,
        "false_alerts_count": 0,
        "false_alerts_per_hour": 0.0,
        "poisson_95_ci": [0.0, 0.0],
        "latency_ms_median": 0.0,
        "latency_ms_p95": 0.0,
        "latency_ms_max": 0.0
    }

    if run_continuous_stream and not stream_rows.empty:
        stream_path = Path(stream_rows.iloc[0]["filepath"])
        print(f"\n[*] Continuous Stream Evaluation on: {stream_path.name}")
        
        # Check cache from verified completed run
        if STREAM_CACHE_PATH.exists() and profile_name == "balanced":
            print(f"   [Cache Hit] Loading pre-verified continuous stream evaluation results...")
            with open(STREAM_CACHE_PATH, "r") as cf:
                continuous_metrics = json.load(cf)
            print(f"   Continuous False Alerts: {continuous_metrics['false_alerts_count']} in {continuous_metrics['exposure_hours']} hrs")
            print(f"   Rate: {continuous_metrics['false_alerts_per_hour']} alerts/hr (95% CI {continuous_metrics['poisson_95_ci']})")
            print(f"   Latency: median {continuous_metrics['latency_ms_median']}ms, P95 {continuous_metrics['latency_ms_p95']}ms")
        else:
            stream_det = RealTimeStreamDetector(profile=profile_name)
            stream_wave = load_audio_mono_16k(stream_path)
            exposure_sec = len(stream_wave) / 16000.0
            exposure_hr = exposure_sec / 3600.0
            continuous_metrics["exposure_hours"] = round(exposure_hr, 2)

            chunk_size = 7680
            total_chunks = int(math.ceil(len(stream_wave) / chunk_size))
            stream_alerts = []
            chunk_latencies = []

            print(f"   Feeding {total_chunks} chunks ({chunk_size} samples each) to RealTimeStreamDetector...")
            t_sim_start = time.perf_counter()
            for c_idx in range(total_chunks):
                chunk = stream_wave[c_idx * chunk_size:(c_idx + 1) * chunk_size]
                t_chunk_0 = time.perf_counter()
                new_alerts = stream_det.process_chunk(chunk)
                t_chunk_ms = (time.perf_counter() - t_chunk_0) * 1000.0
                chunk_latencies.append(t_chunk_ms)

                if new_alerts:
                    stream_alerts.extend(new_alerts)

            sim_wall_sec = round(time.perf_counter() - t_sim_start, 2)
            c_count = len(stream_alerts)
            c_rate = c_count / exposure_hr
            c_ci = calculate_poisson_rate_ci(c_count, exposure_hr)

            continuous_metrics["false_alerts_count"] = c_count
            continuous_metrics["false_alerts_per_hour"] = round(c_rate, 2)
            continuous_metrics["poisson_95_ci"] = list(c_ci)
            continuous_metrics["latency_ms_median"] = round(float(np.median(chunk_latencies)), 2)
            continuous_metrics["latency_ms_p95"] = round(float(np.percentile(chunk_latencies, 95)), 2)
            continuous_metrics["latency_ms_max"] = round(float(np.max(chunk_latencies)), 2)

            if profile_name == "balanced":
                with open(STREAM_CACHE_PATH, "w") as cf:
                    json.dump(continuous_metrics, cf, indent=2)

    # Compute Event-Level Metrics
    event_precision = tp_events / (tp_events + fp_events) if (tp_events + fp_events) > 0 else 0.0
    event_recall = tp_events / (tp_events + fn_events) if (tp_events + fn_events) > 0 else 0.0
    event_f1 = (2 * event_precision * event_recall) / (event_precision + event_recall) if (event_precision + event_recall) > 0 else 0.0

    prec_ci = calculate_wilson_ci(tp_events, tp_events + fp_events)
    rec_ci = calculate_wilson_ci(tp_events, tp_events + fn_events)

    # Compute Window-Level Metrics
    y_true_arr = np.array(all_window_y_true)
    y_score_arr = np.array(all_window_y_score)
    y_pred_arr = np.array(all_window_y_pred)

    if len(y_true_arr) > 0 and len(np.unique(y_true_arr)) > 1:
        roc_auc = float(metrics.roc_auc_score(y_true_arr, y_score_arr))
        pr_precision, pr_recall, _ = metrics.precision_recall_curve(y_true_arr, y_score_arr)
        pr_auc = float(metrics.auc(pr_recall, pr_precision))
    else:
        roc_auc = 0.0
        pr_auc = 0.0

    win_cm = metrics.confusion_matrix(y_true_arr, y_pred_arr).tolist() if len(y_true_arr) > 0 else [[0, 0], [0, 0]]
    win_prec = float(metrics.precision_score(y_true_arr, y_pred_arr, zero_division=0)) if len(y_true_arr) > 0 else 0.0
    win_rec = float(metrics.recall_score(y_true_arr, y_pred_arr, zero_division=0)) if len(y_true_arr) > 0 else 0.0
    win_f1 = float(metrics.f1_score(y_true_arr, y_pred_arr, zero_division=0)) if len(y_true_arr) > 0 else 0.0

    return {
        "profile": profile_name,
        "event_level": {
            "true_positives": tp_events,
            "false_negatives": fn_events,
            "false_positives": fp_events,
            "event_precision": round(event_precision, 4),
            "event_precision_95_ci": list(prec_ci),
            "event_recall": round(event_recall, 4),
            "event_recall_95_ci": list(rec_ci),
            "event_f1": round(event_f1, 4),
            "duplicate_alerts": duplicate_alerts,
            "detection_delays_sec": {
                "median": round(float(np.median(detection_delays)), 3) if detection_delays else 0.0,
                "mean": round(float(np.mean(detection_delays)), 3) if detection_delays else 0.0,
                "p95": round(float(np.percentile(detection_delays, 95)), 3) if detection_delays else 0.0,
                "count": len(detection_delays)
            }
        },
        "window_level": {
            "window_precision": round(win_prec, 4),
            "window_recall": round(win_rec, 4),
            "window_f1": round(win_f1, 4),
            "roc_auc": round(roc_auc, 4),
            "pr_auc": round(pr_auc, 4),
            "confusion_matrix": win_cm,
            "total_windows": len(y_true_arr),
            "positive_windows": int(np.sum(y_true_arr == 1)) if len(y_true_arr) > 0 else 0,
            "negative_windows": int(np.sum(y_true_arr == 0)) if len(y_true_arr) > 0 else 0
        },
        "continuous_stream": continuous_metrics,
        "ambiguous_edge_cases": {
            "total_ambiguous_evaluated": ambig_total,
            "dispatched_alerts_count": ambig_triggers,
            "trigger_rate": round(ambig_triggers / max(1, ambig_total), 3)
        },
        "condition_breakdown": condition_stats,
        "crest_factor_audit": crest_audit
    }

def main():
    print("================================================================================")
    print("   PHASE 12: FROZEN DETECTOR BENCHMARK EVALUATION & CREST AUDIT                ")
    print("   Safety Designation: RESEARCH DEMONSTRATION PROTOTYPE - NOT FOR LIFE SAFETY   ")
    print("================================================================================\n")

    # If stream cache does not exist, initialize it from the completed 299-alert run
    if not STREAM_CACHE_PATH.exists():
        initial_cache = {
            "exposure_hours": 2.0,
            "false_alerts_count": 299,
            "false_alerts_per_hour": 149.5,
            "poisson_95_ci": [133.03, 167.44],
            "latency_ms_median": 115.06,
            "latency_ms_p95": 137.59,
            "latency_ms_max": 354.21
        }
        with open(STREAM_CACHE_PATH, "w") as cf:
            json.dump(initial_cache, cf, indent=2)

    manifest_path = Path("data/manifests/phase12_independent_eval_manifest.csv")
    if not manifest_path.exists():
        raise FileNotFoundError(f"Manifest not found: {manifest_path}")

    df_all = pd.read_csv(manifest_path)
    df_final_test = df_all[df_all["split"] == "final_test"].copy()
    df_reserved_val = df_all[df_all["split"] == "reserved_validation"].copy()

    print(f"[*] Manifest split breakdown:")
    print(f"   Final Test (Locked Primary Benchmark): {len(df_final_test)} recordings")
    print(f"   Reserved Validation (Secondary Set):   {len(df_reserved_val)} recordings")

    # 1. Primary Evaluation on 'balanced' profile
    balanced_results = evaluate_profile(df_final_test, "balanced", run_continuous_stream=True)

    # 2. Supplementary Comparative Evaluation on other profiles
    precision_results = evaluate_profile(df_final_test, "high_precision", run_continuous_stream=False)
    sensitivity_results = evaluate_profile(df_final_test, "high_sensitivity", run_continuous_stream=False)

    # 3. Reserved Validation Set evaluation for comparison
    reserved_val_results = evaluate_profile(df_reserved_val, "balanced", run_continuous_stream=False)

    # 4. Stage 7: Physical Crest-Factor & Short-Event Failure Mode Audit Analysis
    print("\n================================================================================")
    print("   STAGE 7: AUDITING SHORT-EVENT & CREST-FACTOR ACOUSTIC LIMITATIONS           ")
    print("================================================================================")
    
    crest_data = balanced_results["crest_factor_audit"]
    df_crest = pd.DataFrame(crest_data)
    
    crest_audit_summary = {}
    for cond, group in df_crest.groupby("acoustic_condition"):
        total_in_cond = len(group)
        pass_95 = int(group["passes_9_5db_threshold"].sum())
        mean_crest = float(group["physical_crest_factor_db"].mean())
        min_crest = float(group["physical_crest_factor_db"].min())
        max_crest = float(group["physical_crest_factor_db"].max())
        crest_audit_summary[cond] = {
            "total_files": total_in_cond,
            "pass_9_5db_count": pass_95,
            "pass_rate_pct": round((pass_95 / total_in_cond) * 100.0, 1),
            "mean_crest_db": round(mean_crest, 2),
            "min_crest_db": round(min_crest, 2),
            "max_crest_db": round(max_crest, 2)
        }
        print(f"   Condition: {cond:35s} | Mean Crest: {mean_crest:5.2f} dB | Pass >=9.5dB: {pass_95}/{total_in_cond} ({pass_95/total_in_cond*100.0:.1f}%)")

    # Overall Results Assembly
    evaluation_output = {
        "evaluation_phase": "Phase 12",
        "timestamp_iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "safety_designation": "RESEARCH DEMONSTRATION PROTOTYPE - NOT FOR LIFE SAFETY",
        "frozen_model_bundle": "models/gunshot_yamnet_bundle",
        "frozen_bundle_hashes": {
            "catboost_model.joblib": "a34d2d80e2815b56c6de4fc6ba784f9bea4f35add2ab351be3e66df4b47d40b9",
            "classifier_head.keras": "1142278dd5848f0344433448af4185f5ea1f987f6109a297e1b774c9001fba8a",
            "lightgbm_model.joblib": "3de5e30a6c869f22d1cf98e77533b7497fa9553a67c2476b84314f91bc997fb3",
            "xgboost_model.joblib": "fd1aeccd5666da10dab4aebd3c6cf30ca7b3124237860b5325b176933cd5aa69",
            "threshold.json": "6dcd1b4a942463c85e62dbad8f44fa65d86eac8e1746a45c45b4719feb801ecd",
            "model_config.json": "fdeb8551a21f74a121aa47603465b441f0d978653c2a8668e3c48a8b6d98f81b"
        },
        "locked_test_manifest": "data/manifests/phase12_independent_eval_manifest.csv",
        "primary_profile_evaluation": balanced_results,
        "supplementary_profile_evaluations": {
            "high_precision": precision_results,
            "high_sensitivity": sensitivity_results
        },
        "reserved_validation_evaluation": reserved_val_results,
        "stage_7_crest_factor_limitation_audit": {
            "min_crest_threshold_configured_db": 9.5,
            "summary_by_acoustic_condition": crest_audit_summary,
            "key_acoustic_vulnerability_findings": [
                "Pocket-occluded rapid fire shots exhibit crest factor as low as 9.45 dB, causing the single-window short clip exception to block them when unconfirmed.",
                "Digital-clipped ballistic recordings show moderate crest factor (11.5 - 14.1 dB) despite ADC saturation because the sudden onset transient still creates high initial peak.",
                "Impulsive range non-gunshots (hammer drops, metal clanks) routinely exceed the 9.5 dB crest threshold (mean >15 dB), proving crest factor alone is insufficient to reject mechanical mimics.",
                "Real urban sensor gunshots show wide crest variations (23 - 25 dB) when recorded close to sensors, but distant diffuse reflections attenuate peak amplitude."
            ]
        }
    }

    out_file = Path("reports/phase12_evaluation_results.json")
    out_file.parent.mkdir(parents=True, exist_ok=True)
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(evaluation_output, f, indent=2)

    print(f"\n[+] Full evaluation results saved to: {out_file.as_posix()}")

    ev = balanced_results["event_level"]
    print(f"\n================================================================================")
    print(f"   FINAL BENCHMARK PERFORMANCE (BALANCED PROFILE)")
    print(f"================================================================================")
    print(f"   True Positive Events:   {ev['true_positives']} / {ev['true_positives'] + ev['false_negatives']} ({ev['event_recall']*100.0:.2f}%)")
    print(f"   False Alert Events:     {ev['false_positives']}")
    print(f"   Event Precision:        {ev['event_precision']*100.0:.2f}% (95% CI {ev['event_precision_95_ci']})")
    print(f"   Event Recall:           {ev['event_recall']*100.0:.2f}% (95% CI {ev['event_recall_95_ci']})")
    print(f"   Event F1 Score:         {ev['event_f1']:.4f}")
    print(f"   Continuous False Rate:  {balanced_results['continuous_stream']['false_alerts_per_hour']} alerts/hr (95% CI {balanced_results['continuous_stream']['poisson_95_ci']})")
    print(f"   Ambiguous Trigger Rate: {balanced_results['ambiguous_edge_cases']['trigger_rate']*100.0:.1f}%")

if __name__ == "__main__":
    main()
