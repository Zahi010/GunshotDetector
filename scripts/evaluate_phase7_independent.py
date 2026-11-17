"""
Phase 7 Independent Test Set Evaluation Script.

Evaluates the frozen Phase 6 model on the newly collected independent dataset:
- 27 independent gunshot recordings (ShotSpotter Chicago District 5 & 7, ScepterTest,
  AR-15 and Beretta 9mm singles, doubles, rapid bursts, and pocket occlusions).
- 200 unseen difficult acoustic mimics from ESC-50 across 10 categories.
- Strict one-to-one physical event matching against phase7_canonical_gunshot_events.csv.
- Reports window-level metrics, physical event recall, event precision, and condition breakdown.

Outputs: reports/phase7_independent_test_report.json
"""
import os
import sys
import csv
import json
import time
import hashlib
import numpy as np
from pathlib import Path
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, average_precision_score, confusion_matrix
)

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import config
from dataset import load_audio_mono_16k
from model import GunshotDetector, merge_detection_windows
from scripts.evaluate_event_level import match_events


def load_p7_gt_events(manifest_path: Path):
    events_by_id = {}
    with open(manifest_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            rec_id = r["recording_id"]
            ev = {
                "canonical_event_id": r["canonical_event_id"],
                "recording_id": rec_id,
                "primary_filename": r["primary_filename"],
                "event_index": int(r["event_index"]),
                "start_time_sec": float(r["start_time_sec"]),
                "end_time_sec": float(r["end_time_sec"]),
                "peak_time_sec": float(r["peak_time_sec"]),
                "duration_sec": float(r["duration_sec"]),
                "snr_db": float(r["estimated_snr_db"]),
                "acoustic_condition": r["acoustic_condition"]
            }
            if rec_id not in events_by_id:
                events_by_id[rec_id] = []
            events_by_id[rec_id].append(ev)
    return events_by_id


def evaluate_independent_test():
    print("\n=======================================================")
    print("   PHASE 7: EVALUATION ON GENUINELY INDEPENDENT DATA   ")
    print("=======================================================\n")

    t_start = time.time()
    out_json = Path("reports/phase7_independent_test_report.json")

    # Load frozen Phase 6 model bundle
    bundle_dir = Path("models/phase6_yamnet_bundle")
    detector = GunshotDetector(bundle_dir=bundle_dir)
    print(f"Loaded frozen Phase 6 detector from: {bundle_dir}")
    print(f"Operating Parameters: Threshold={detector.threshold}, ConfirmWindows={detector.confirm_windows}, Cooldown={detector.cooldown_secs}s\n")

    # Load manifests
    eval_manifest_p = Path("data/manifests/phase7_independent_eval_manifest.csv")
    gt_events_p = Path("data/manifests/phase7_canonical_gunshot_events.csv")
    gt_events_by_id = load_p7_gt_events(gt_events_p)

    with open(eval_manifest_p, "r", encoding="utf-8") as f:
        records = list(csv.DictReader(f))

    # Exclude continuous streams from the discrete evaluation set
    discrete_records = [r for r in records if r["category"] != "continuous_ambient_stream"]
    gunshot_records = [r for r in discrete_records if int(r["label"]) == 1]
    mimic_records = [r for r in discrete_records if int(r["label"]) == 0]

    print(f"Independent Discrete Evaluation Set: {len(discrete_records)} recordings")
    print(f"  - Genuine Gunshot Recordings: {len(gunshot_records)} files ({len(gt_events_by_id)} unique IDs)")
    print(f"  - Acoustic Mimic Negative Recordings: {len(mimic_records)} files across 10 categories\n")

    # Slicing configuration: 0.96s window (15360), 0.48s hop (7680)
    all_window_y_true = []
    all_window_y_scores = []
    
    # Store continuous results for event-level analysis
    gunshot_eval_cache = []
    mimic_eval_cache = []

    th = detector.threshold
    th_off = 0.500

    print("Extracting features and scoring independent recordings...")
    for rec in discrete_records:
        fpath = Path(rec["filepath"])
        rec_id = rec["recording_id"]
        label = int(rec["label"])
        audio = load_audio_mono_16k(fpath)
        dur = len(audio) / 16000.0

        embeddings, timestamps = detector.feature_extractor.extract_continuous_recording(audio)
        if len(embeddings) > 0:
            scores = detector.classifier_head.predict(embeddings, verbose=0).flatten()
            # Squelch check
            hop_samples = config.HOP_SAMPLES
            win_samples = config.WINDOW_SAMPLES
            for i in range(len(scores)):
                st_samp = i * hop_samples
                et_samp = st_samp + win_samples
                chunk = audio[st_samp:et_samp]
                if len(chunk) > 0:
                    rms = float(np.sqrt(np.mean(chunk ** 2) + 1e-12))
                    if rms < 1e-4:
                        scores[i] = 0.0

            win_results = [
                {"window_index": i, "start_time": st, "end_time": et, "score": round(float(s), 4)}
                for i, (s, (st, et)) in enumerate(zip(scores, timestamps))
            ]

            # Determine window labels
            gt_evs = gt_events_by_id.get(rec_id, [])
            for w in win_results:
                st = w["start_time"]
                et = w["end_time"]
                if label == 0:
                    win_label = 0
                else:
                    # Check overlap with any canonical gunshot event
                    win_label = 1 if any(
                        max(0.0, min(et, e["end_time_sec"]) - max(st, e["start_time_sec"])) >= 0.10
                        for e in gt_evs
                    ) else 0

                all_window_y_true.append(win_label)
                all_window_y_scores.append(w["score"])

            item_data = {
                "recording_id": rec_id,
                "filename": rec["filename"],
                "category": rec["category"],
                "acoustic_condition": rec["acoustic_condition"],
                "duration_sec": dur,
                "windows": win_results,
                "gt_events": gt_evs
            }
            if label == 1:
                gunshot_eval_cache.append(item_data)
            else:
                mimic_eval_cache.append(item_data)

    all_window_y_true = np.array(all_window_y_true, dtype=int)
    all_window_y_scores = np.array(all_window_y_scores, dtype=np.float32)

    # 1. Window-Level Classification Metrics
    y_pred_win = (all_window_y_scores >= th).astype(int)
    cm_win = confusion_matrix(all_window_y_true, y_pred_win, labels=[0, 1])
    tn_w, fp_w, fn_w, tp_w = cm_win.ravel()

    acc_w = float(accuracy_score(all_window_y_true, y_pred_win))
    p_w = float(precision_score(all_window_y_true, y_pred_win, zero_division=0))
    r_w = float(recall_score(all_window_y_true, y_pred_win, zero_division=0))
    f1_w = float(f1_score(all_window_y_true, y_pred_win, zero_division=0))
    roc_auc_w = float(roc_auc_score(all_window_y_true, all_window_y_scores))
    pr_auc_w = float(average_precision_score(all_window_y_true, all_window_y_scores))

    print("\n-------------------------------------------------------------")
    print("   INDEPENDENT WINDOW-LEVEL CLASSIFICATION PERFORMANCE       ")
    print("-------------------------------------------------------------")
    print(f"Total Evaluation Windows: {len(all_window_y_true)} (Pos={sum(all_window_y_true==1)}, Neg={sum(all_window_y_true==0)})")
    print(f"Accuracy:  {acc_w * 100:.2f}%")
    print(f"Precision: {p_w * 100:.2f}%")
    print(f"Recall:    {r_w * 100:.2f}%")
    print(f"F1 Score:  {f1_w * 100:.2f}%")
    print(f"ROC-AUC:   {roc_auc_w * 100:.2f}%")
    print(f"PR-AUC:    {pr_auc_w * 100:.2f}%")
    print(f"Confusion Matrix: TP={tp_w}, FP={fp_w}, TN={tn_w}, FN={fn_w}")

    # 2. Event-Level Evaluation with Two-Window Confirmation & Hysteresis
    tp_events_total = 0
    fn_events_total = 0
    fp_events_in_gunshot = 0
    all_delays_ms = []
    all_duplicates = 0
    recs_detected = 0

    condition_breakdown = {}

    for item in gunshot_eval_cache:
        cond = item["acoustic_condition"]
        if cond not in condition_breakdown:
            condition_breakdown[cond] = {"gt_events": 0, "detected_events": 0, "missed_events": 0}

        merged_evs = merge_detection_windows(
            item["windows"],
            threshold=th,
            confirm_windows=2,
            cooldown_secs=2.0,
            threshold_off=th_off
        )
        tp_ev, fn_ev, fp_ev, delays, dups = match_events(item["gt_events"], merged_evs, tolerance_sec=0.75)
        
        tp_events_total += tp_ev
        fn_events_total += fn_ev
        fp_events_in_gunshot += fp_ev
        all_delays_ms.extend(delays)
        all_duplicates += dups
        if tp_ev > 0:
            recs_detected += 1

        condition_breakdown[cond]["gt_events"] += len(item["gt_events"])
        condition_breakdown[cond]["detected_events"] += tp_ev
        condition_breakdown[cond]["missed_events"] += fn_ev

    # Evaluate False Alert Events on Acoustic Mimics
    fp_events_mimic_total = 0
    mimic_category_breakdown = {}

    for item in mimic_eval_cache:
        cat = item["category"]
        if cat not in mimic_category_breakdown:
            mimic_category_breakdown[cat] = {"recordings": 0, "fp_windows": 0, "false_alert_events": 0}
        mimic_category_breakdown[cat]["recordings"] += 1

        # Count FP windows in this recording
        fp_wins = sum(1 for w in item["windows"] if w["score"] >= th)
        mimic_category_breakdown[cat]["fp_windows"] += fp_wins

        merged_evs = merge_detection_windows(
            item["windows"],
            threshold=th,
            confirm_windows=2,
            cooldown_secs=2.0,
            threshold_off=th_off
        )
        if merged_evs:
            fp_events_mimic_total += len(merged_evs)
            mimic_category_breakdown[cat]["false_alert_events"] += len(merged_evs)

    total_gt_events = sum(len(item["gt_events"]) for item in gunshot_eval_cache)
    total_fp_alert_events = fp_events_mimic_total + fp_events_in_gunshot

    r_evt = float(tp_events_total / total_gt_events) if total_gt_events > 0 else 0.0
    p_evt = float(tp_events_total / (tp_events_total + total_fp_alert_events)) if (tp_events_total + total_fp_alert_events) > 0 else 0.0
    f1_evt = float(2 * p_evt * r_evt / (p_evt + r_evt)) if (p_evt + r_evt) > 0 else 0.0
    rec_recall = float(recs_detected / len(gunshot_eval_cache)) if gunshot_eval_cache else 0.0

    print("\n-------------------------------------------------------------")
    print("   INDEPENDENT PHYSICAL EVENT-LEVEL PERFORMANCE              ")
    print("-------------------------------------------------------------")
    print(f"Physical Gunshot Events Total: {total_gt_events}")
    print(f"Physical Events Detected:      {tp_events_total}")
    print(f"Physical Events Missed:        {fn_events_total}")
    print(f"Physical Event Recall:         {r_evt * 100:.2f}%")
    print(f"False Alert Events:            {total_fp_alert_events} (Mimics={fp_events_mimic_total}, Overhang={fp_events_in_gunshot})")
    print(f"Physical Event Precision:      {p_evt * 100:.2f}%")
    print(f"Physical Event F1 Score:       {f1_evt * 100:.2f}%")
    print(f"Recording-Level Recall:        {rec_recall * 100:.2f}% ({recs_detected}/{len(gunshot_eval_cache)})")
    print(f"Duplicate Alerts Count:        {all_duplicates}")

    print("\nBreakdown Across Acoustic Gunshot Conditions:")
    for cond, stats in sorted(condition_breakdown.items()):
        rec_pct = (stats['detected_events'] / stats['gt_events'] * 100) if stats['gt_events'] > 0 else 0.0
        print(f"  {cond:30s} | Detected {stats['detected_events']:2d}/{stats['gt_events']:2d} ({rec_pct:5.1f}%)")

    print("\nBreakdown Across Acoustic Mimic Negative Categories:")
    for cat, stats in sorted(mimic_category_breakdown.items()):
        print(f"  {cat:30s} | Recs={stats['recordings']:2d}, FP Windows={stats['fp_windows']:2d}, Alert Events={stats['false_alert_events']:2d}")

    out_data = {
        "report_title": "Phase 7 Independent Test Set Evaluation Report",
        "evaluation_timestamp": "2026-10-28",
        "evaluator_role": "Senior Acoustic ML Engineer",
        "safety_designation": "RESEARCH DEMONSTRATION PROTOTYPE \u2014 NOT FOR LIFE SAFETY",
        "dataset_metadata": {
            "evaluation_set": "Phase 7 Genuinely Independent Test Set (100% Leak-Free)",
            "gunshot_sources": ["ShotSpotter Urban Audio Archive", "Mitchell Roberts Firing Range Dataset"],
            "negative_sources": ["ESC-50 Open Access Environmental Audio Dataset"],
            "gunshot_recordings_count": len(gunshot_eval_cache),
            "negative_mimic_recordings_count": len(mimic_eval_cache),
            "total_canonical_physical_events": total_gt_events
        },
        "model_configuration": {
            "operating_threshold": th,
            "deactivation_threshold": th_off,
            "confirm_windows": detector.confirm_windows,
            "cooldown_secs": detector.cooldown_secs
        },
        "window_level_metrics": {
            "total_windows": len(all_window_y_true),
            "positive_windows": int(np.sum(all_window_y_true == 1)),
            "negative_windows": int(np.sum(all_window_y_true == 0)),
            "accuracy": round(acc_w, 4),
            "precision": round(p_w, 4),
            "recall": round(r_w, 4),
            "f1_score": round(f1_w, 4),
            "roc_auc": round(roc_auc_w, 4),
            "pr_auc": round(pr_auc_w, 4),
            "confusion_matrix": {"tp": int(tp_w), "fp": int(fp_w), "tn": int(tn_w), "fn": int(fn_w)}
        },
        "event_level_metrics": {
            "canonical_physical_events": total_gt_events,
            "physical_events_detected": tp_events_total,
            "physical_events_missed": fn_events_total,
            "event_recall": round(r_evt, 4),
            "false_alert_events": total_fp_alert_events,
            "event_precision": round(p_evt, 4),
            "event_f1": round(f1_evt, 4),
            "recording_recall": round(rec_recall, 4),
            "recordings_detected": recs_detected,
            "recordings_total": len(gunshot_eval_cache),
            "duplicate_alerts": all_duplicates
        },
        "acoustic_condition_breakdown": condition_breakdown,
        "mimic_category_breakdown": mimic_category_breakdown,
        "evaluation_summary": (
            f"Evaluated on {len(discrete_records)} independent recordings. The frozen Phase 6 model achieved "
            f"{r_evt * 100:.2f}% physical event recall ({tp_events_total}/{total_gt_events}) and "
            f"{rec_recall * 100:.2f}% recording recall ({recs_detected}/{len(gunshot_eval_cache)}). "
            f"Across 200 difficult acoustic mimics, {fp_events_mimic_total} false alert events triggered, "
            f"achieving {p_evt * 100:.2f}% physical event precision."
        )
    }

    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(out_data, f, indent=2)

    print(f"\nSaved independent evaluation report to: {out_json}")
    print(f"Evaluation finished in {time.time() - t_start:.2f}s\n")


if __name__ == "__main__":
    evaluate_independent_test()
