"""
Phase 19 Source-Independent Evaluation Runner
MANDATORY SAFETY DESIGNATION:
RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.

Evaluates frozen detectors against:
- Category A: Natural Continuous Urban Streams (ShotSpotter Pittsburgh DQV 2018, 20 streams, 50 physical events)
- Category B: Pre-Cropped External Clips (9lash, 3 clips, 3 physical events)
- Compares against Category C (Phase 17/18 reference) and Category D (Mitchell 2015 historical reference).
"""

import os
import sys
import json
import math
from pathlib import Path
from typing import Dict, List, Any, Tuple

ROOT = Path("E:/gunshot/gunshot")
sys.path.insert(0, str(ROOT))

import soundfile as sf
import numpy as np
import pandas as pd

from model_phase14 import Phase14CandidateGunshotDetector
from model_phase17 import Phase17ExperimentalGunshotDetector
from model_phase9 import Phase9AdaptiveGunshotDetector

REPORTS_DIR = ROOT / "reports"
DATA_DIR = ROOT / "data" / "phase19_independent_positive" / "normalized_16k"

def wilson_score_interval(k: int, n: int, confidence: float = 0.95) -> Tuple[float, float]:
    """Calculate exact two-sided Wilson score confidence interval."""
    if n == 0:
        return (0.0, 0.0)
    z = 1.959964  # for 95% confidence
    p = float(k) / float(n)
    denom = 1.0 + (z**2) / float(n)
    center = (p + (z**2) / (2.0 * float(n))) / denom
    margin = (z * math.sqrt((p * (1.0 - p) / float(n)) + ((z**2) / (4.0 * (float(n)**2))))) / denom
    ci_lower = max(0.0, center - margin)
    ci_upper = min(1.0, center + margin)
    return (round(ci_lower * 100.0, 2), round(ci_upper * 100.0, 2))

print("=== Phase 19 Source-Independent Positive Evaluation ===")

# Load ground-truth manifests
df_recordings = pd.read_csv(REPORTS_DIR / "phase19_positive_recording_manifest.csv")
df_events = pd.read_csv(REPORTS_DIR / "phase19_event_annotation_manifest.csv")

print(f"Loaded {len(df_recordings)} test streams and {len(df_events)} ground-truth physical events.")

# Initialize frozen detector models
models = {
    "Phase 14 Balanced (Default Baseline)": Phase14CandidateGunshotDetector(profile="balanced"),
    "Phase 14 High-Precision": Phase14CandidateGunshotDetector(profile="high_precision"),
    "Phase 14 High-Sensitivity": Phase14CandidateGunshotDetector(profile="high_sensitivity"),
    "Phase 17 Experimental (Animal Suppression)": Phase17ExperimentalGunshotDetector(profile="balanced_animal_suppressed"),
    "Phase 9 Balanced (Historical Baseline)": Phase9AdaptiveGunshotDetector(profile="balanced")
}

model_keys = [
    "phase_14_balanced",
    "phase_14_high_precision",
    "phase_14_high_sensitivity",
    "phase_17_experimental",
    "phase_9_balanced"
]

model_map = {
    "phase_14_balanced": models["Phase 14 Balanced (Default Baseline)"],
    "phase_14_high_precision": models["Phase 14 High-Precision"],
    "phase_14_high_sensitivity": models["Phase 14 High-Sensitivity"],
    "phase_17_experimental": models["Phase 17 Experimental (Animal Suppression)"],
    "phase_9_balanced": models["Phase 9 Balanced (Historical Baseline)"]
}

# Data structures to store detailed results
event_results = []
for _, ev in df_events.iterrows():
    row = ev.to_dict()
    for mkey in model_keys:
        row[f"{mkey}_detected"] = False
        row[f"{mkey}_latency_ms"] = None
        row[f"{mkey}_alert_score"] = None
        row[f"{mkey}_alert_id"] = None
        row[f"{mkey}_dispatch_path"] = None
    event_results.append(row)

# Track alerts per model and stream
stream_alerts = {mkey: {} for mkey in model_keys}
stream_metrics = {mkey: {} for mkey in model_keys}

print("\nRunning inference across all models and streams...")

for _, rec in df_recordings.iterrows():
    stream_id = rec["stream_id"]
    wav_path = DATA_DIR / rec["normalized_filename"]
    audio, sr = sf.read(wav_path)
    
    # Ground truth events for this stream
    stream_evs = [ev for ev in event_results if ev["stream_id"] == stream_id]
    
    for mkey in model_keys:
        detector = model_map[mkey]
        res = detector.evaluate_waveform(audio)
        alerts = res.get("events", [])
        
        # Save raw alerts
        stream_alerts[mkey][stream_id] = alerts
        
        # Match alerts to events
        # A ground truth event at t_pulse matches alert if:
        # t_pulse - 0.50 <= t_alert_start <= t_pulse + 1.50 OR t_pulse - 0.50 <= t_alert_peak <= t_pulse + 1.50
        matched_alerts = set()
        
        for ev in stream_evs:
            t_pulse = ev["nominal_pulse_time_s"]
            # Candidate alerts in window
            candidates = []
            for a_idx, a in enumerate(alerts):
                a_st = a["start_time"]
                a_et = a["end_time"]
                a_pk = a.get("peak_time", (a_st + a_et) / 2.0)
                
                # Check matching tolerance [-0.5s, +1.5s]
                if (t_pulse - 0.50 <= a_st <= t_pulse + 1.50) or (t_pulse - 0.50 <= a_pk <= t_pulse + 1.50):
                    candidates.append((a_idx, a, a_pk))
                    
            if candidates:
                # Primary match: closest candidate
                candidates.sort(key=lambda c: abs(c[2] - t_pulse))
                best_idx, best_alert, best_pk = candidates[0]
                latency_ms = round((best_pk - t_pulse) * 1000.0, 1)
                
                ev[f"{mkey}_detected"] = True
                ev[f"{mkey}_latency_ms"] = latency_ms
                ev[f"{mkey}_alert_score"] = best_alert.get("peak_score", best_alert.get("score", 0.0))
                ev[f"{mkey}_alert_id"] = f"{stream_id}-ALERT-{best_idx+1:02d}"
                ev[f"{mkey}_dispatch_path"] = best_alert.get("dispatch_path", "standard")
                
                matched_alerts.add(best_idx)

print("Inference and matching complete.")

# Write per-event results
df_out_events = pd.DataFrame(event_results)
df_out_events.to_csv(REPORTS_DIR / "phase19_independent_event_results.csv", index=False)
print("Saved reports/phase19_independent_event_results.csv")

# Compute aggregate metrics per model and category
summary_metrics = {
    "safety_designation": "RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY",
    "evaluation_phase": "PHASE_19_SOURCE_INDEPENDENT_EVALUATION",
    "timestamp": "2026-11-13 UTC",
    "models": {}
}

category_comparison_rows = []

for mkey in model_keys:
    # Model name
    mname = [k for k, v in models.items() if model_map[mkey] is v][0]
    
    # Category A: Natural Continuous
    cat_a_evs = [ev for ev in event_results if ev["category"] == "CATEGORY_A_NATURAL_CONTINUOUS"]
    n_a = len(cat_a_evs)
    tp_a = sum(1 for ev in cat_a_evs if ev[f"{mkey}_detected"])
    fn_a = n_a - tp_a
    
    # False alerts in Category A: alerts that didn't match any GT event
    fp_a = 0
    dup_a = 0
    for rec in df_recordings[df_recordings["category"] == "CATEGORY_A_NATURAL_CONTINUOUS"].itertuples():
        sid = rec.stream_id
        alerts = stream_alerts[mkey].get(sid, [])
        s_evs = [ev for ev in cat_a_evs if ev["stream_id"] == sid]
        
        # Which alerts matched an event?
        matched_alert_ids = set()
        for ev in s_evs:
            aid = ev.get(f"{mkey}_alert_id")
            if aid:
                matched_alert_ids.add(aid)
                
        # Total alerts minus matched alerts = false alerts
        # Duplicate alerts: if multiple alerts fell in window
        if len(alerts) > len(matched_alert_ids):
            # Check if extra alerts are inside gunshot windows (duplicate) or outside (false alarm)
            for a_idx, a in enumerate(alerts):
                aid = f"{sid}-ALERT-{a_idx+1:02d}"
                if aid not in matched_alert_ids:
                    a_pk = a.get("peak_time", (a["start_time"] + a["end_time"]) / 2.0)
                    in_any_window = any(abs(a_pk - ev["nominal_pulse_time_s"]) <= 1.50 for ev in s_evs)
                    if in_any_window:
                        dup_a += 1
                    else:
                        fp_a += 1
                        
    recall_a = tp_a / float(n_a) if n_a > 0 else 0.0
    prec_a = tp_a / float(tp_a + fp_a) if (tp_a + fp_a) > 0 else 0.0
    f1_a = (2.0 * prec_a * recall_a) / (prec_a + recall_a) if (prec_a + recall_a) > 0 else 0.0
    ci_a = wilson_score_interval(tp_a, n_a)
    
    latencies_a = [ev[f"{mkey}_latency_ms"] for ev in cat_a_evs if ev[f"{mkey}_detected"] and ev[f"{mkey}_latency_ms"] is not None]
    med_lat_a = float(np.median(latencies_a)) if latencies_a else 0.0
    p95_lat_a = float(np.percentile(latencies_a, 95)) if latencies_a else 0.0
    
    # Category B: Pre-Cropped External Clips
    cat_b_evs = [ev for ev in event_results if ev["category"] == "CATEGORY_B_PRE_CROPPED_EXTERNAL"]
    n_b = len(cat_b_evs)
    tp_b = sum(1 for ev in cat_b_evs if ev[f"{mkey}_detected"])
    fn_b = n_b - tp_b
    fp_b = 0
    recall_b = tp_b / float(n_b) if n_b > 0 else 0.0
    prec_b = tp_b / float(tp_b + fp_b) if (tp_b + fp_b) > 0 else 0.0
    f1_b = (2.0 * prec_b * recall_b) / (prec_b + recall_b) if (prec_b + recall_b) > 0 else 0.0
    ci_b = wilson_score_interval(tp_b, n_b)
    
    summary_metrics["models"][mname] = {
        "category_a_natural_continuous": {
            "total_events": n_a,
            "detected_events": tp_a,
            "missed_events": fn_a,
            "false_alerts": fp_a,
            "duplicate_alerts": dup_a,
            "recall_pct": round(recall_a * 100.0, 2),
            "precision_pct": round(prec_a * 100.0, 2),
            "f1_score": round(f1_a, 4),
            "wilson_95_ci_pct": list(ci_a),
            "median_latency_ms": med_lat_a,
            "p95_latency_ms": p95_lat_a
        },
        "category_b_pre_cropped_external": {
            "total_events": n_b,
            "detected_events": tp_b,
            "missed_events": fn_b,
            "false_alerts": fp_b,
            "recall_pct": round(recall_b * 100.0, 2),
            "precision_pct": round(prec_b * 100.0, 2),
            "f1_score": round(f1_b, 4),
            "wilson_95_ci_pct": list(ci_b)
        }
    }
    
    category_comparison_rows.append({
        "model": mname,
        "category": "Category A (Natural Continuous Pittsburgh)",
        "provenance": "SOURCE_INDEPENDENT_EXTERNAL",
        "total_events": n_a,
        "detected": tp_a,
        "missed": fn_a,
        "false_alerts": fp_a,
        "recall_pct": round(recall_a * 100.0, 2),
        "precision_pct": round(prec_a * 100.0, 2),
        "f1_score": round(f1_a, 4),
        "wilson_95_ci_lower_pct": ci_a[0],
        "wilson_95_ci_upper_pct": ci_a[1],
        "median_latency_ms": med_lat_a
    })
    category_comparison_rows.append({
        "model": mname,
        "category": "Category B (Pre-Cropped External 9lash)",
        "provenance": "PRE_CROPPED_EXTERNAL_CLIP",
        "total_events": n_b,
        "detected": tp_b,
        "missed": fn_b,
        "false_alerts": fp_b,
        "recall_pct": round(recall_b * 100.0, 2),
        "precision_pct": round(prec_b * 100.0, 2),
        "f1_score": round(f1_b, 4),
        "wilson_95_ci_lower_pct": ci_b[0],
        "wilson_95_ci_upper_pct": ci_b[1],
        "median_latency_ms": 0.0
    })

# Add Category C & Category D reference rows for Phase 14 Balanced
cat_c_ref = {
    "model": "Phase 14 Balanced (Default Baseline)",
    "category": "Category C (Calibrated Transparent Streams Phase 17/18)",
    "provenance": "CALIBRATED_TRANSPARENT_EVALUATION",
    "total_events": 33,
    "detected": 23,
    "missed": 10,
    "false_alerts": 8,
    "recall_pct": 69.70,
    "precision_pct": 74.19,
    "f1_score": 0.7188,
    "wilson_95_ci_lower_pct": 52.68,
    "wilson_95_ci_upper_pct": 82.64,
    "median_latency_ms": 625.0
}
cat_d_ref = {
    "model": "Phase 14 Balanced (Default Baseline)",
    "category": "Category D (Historically Related Mitchell Range 2015)",
    "provenance": "HISTORICALLY_RELATED_SESSION",
    "total_events": 42,
    "detected": 35,
    "missed": 7,
    "false_alerts": 5,
    "recall_pct": 83.33,
    "precision_pct": 87.50,
    "f1_score": 0.8537,
    "wilson_95_ci_lower_pct": 69.24,
    "wilson_95_ci_upper_pct": 91.88,
    "median_latency_ms": 480.0
}
category_comparison_rows.extend([cat_c_ref, cat_d_ref])

# Save Category Comparison
df_cat = pd.DataFrame(category_comparison_rows)
df_cat.to_csv(REPORTS_DIR / "phase19_category_comparison.csv", index=False)
print("Saved reports/phase19_category_comparison.csv")

# Compute Session Results (Category A: FP1 to FP5)
session_rows = []
for sess_id in ["FP1", "FP2", "FP3", "FP4", "FP5", "SESSION_9LASH"]:
    s_evs = [ev for ev in event_results if ev["session_id"] == sess_id]
    n_s = len(s_evs)
    
    for mkey in model_keys:
        mname = [k for k, v in models.items() if model_map[mkey] is v][0]
        tp_s = sum(1 for ev in s_evs if ev[f"{mkey}_detected"])
        rec_s = tp_s / float(n_s) if n_s > 0 else 0.0
        ci_s = wilson_score_interval(tp_s, n_s)
        
        session_rows.append({
            "session_id": sess_id,
            "model": mname,
            "total_events": n_s,
            "detected": tp_s,
            "missed": n_s - tp_s,
            "recall_pct": round(rec_s * 100.0, 2),
            "wilson_95_ci_lower_pct": ci_s[0],
            "wilson_95_ci_upper_pct": ci_s[1]
        })

df_sess = pd.DataFrame(session_rows)
df_sess.to_csv(REPORTS_DIR / "phase19_independent_session_results.csv", index=False)
print("Saved reports/phase19_independent_session_results.csv")

# Save complete summary JSON
with open(REPORTS_DIR / "phase19_evaluation_summary.json", "w") as f:
    json.dump(summary_metrics, f, indent=2)
print("Saved reports/phase19_evaluation_summary.json")

print("\n=== Category A Summary Results (50 Physical Gunshot Events, Natural Continuous) ===")
for mname, mdata in summary_metrics["models"].items():
    res_a = mdata["category_a_natural_continuous"]
    print(f"[{mname}]")
    print(f"  Detected: {res_a['detected_events']}/{res_a['total_events']} ({res_a['recall_pct']}%) | 95% CI: [{res_a['wilson_95_ci_pct'][0]}%, {res_a['wilson_95_ci_pct'][1]}%]")
    print(f"  Precision: {res_a['precision_pct']}% | False Alerts: {res_a['false_alerts']} | Duplicate Alerts: {res_a['duplicate_alerts']}")
    print(f"  Median Latency: {res_a['median_latency_ms']} ms | P95 Latency: {res_a['p95_latency_ms']} ms")

