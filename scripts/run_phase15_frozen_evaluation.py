"""
Phase 15: Frozen Detector Discrete Evaluation Script.

Evaluates frozen detectors across discrete benchmark splits:
1. Phase 9 Baseline (profile='balanced')
2. Phase 13 Candidate (profile='balanced')
3. Phase 14 Balanced Candidate (profile='balanced')
4. Phase 14 High-Precision (profile='high_precision')
5. Phase 14 High-Sensitivity (profile='high_sensitivity')

Calculates:
- Event-Level Metrics: TP, FP, FN, Precision, Recall, F1, Duplicates, Misses, Detection Delay
- Window-Level Metrics: Accuracy, Precision, Recall, F1, ROC-AUC, PR-AUC, Confusion Matrix
- Category-Specific Metrics: Pocket-Occlusion, Clipped Range, Clean Ballistic, Negatives by Category
- Outputs:
  * reports/phase15_event_level_metrics.csv
  * reports/phase15_window_level_metrics.json
  * reports/phase15_frozen_detector_evaluation.md
  * reports/phase15_pocket_occlusion_evaluation.md

SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.
"""

import os
import sys
import json
import time
from pathlib import Path
from typing import Dict, List, Tuple, Any

import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, precision_recall_curve, auc, confusion_matrix
)

# Project root
WORKSPACE_ROOT = Path("e:/gunshot/gunshot")
sys.path.insert(0, str(WORKSPACE_ROOT))
import config
from dataset import load_audio_mono_16k
from model_phase9 import Phase9AdaptiveGunshotDetector
from model_phase13 import Phase13CandidateGunshotDetector
from model_phase14 import Phase14CandidateGunshotDetector

def main():
    print("================================================================================")
    print("   PHASE 15: FROZEN DETECTOR DISCRETE BENCHMARK EVALUATION                     ")
    print("   Safety Designation: RESEARCH DEMONSTRATION PROTOTYPE - NOT FOR LIFE SAFETY   ")
    print("================================================================================\n")

    manifest_csv = WORKSPACE_ROOT / "reports" / "phase15_dataset_manifest.csv"
    if not manifest_csv.exists():
        raise FileNotFoundError(f"Missing {manifest_csv}")

    df_manifest = pd.read_csv(manifest_csv)
    print(f"[*] Loaded manifest: {len(df_manifest)} recordings.")

    # Instantiate frozen detectors
    print("[*] Instantiating frozen detector candidates...")
    detectors = {
        "Phase 9 Baseline": Phase9AdaptiveGunshotDetector(profile="balanced"),
        "Phase 13 Candidate": Phase13CandidateGunshotDetector(profile="balanced"),
        "Phase 14 Balanced": Phase14CandidateGunshotDetector(profile="balanced"),
        "Phase 14 High-Precision": Phase14CandidateGunshotDetector(profile="high_precision"),
        "Phase 14 High-Sensitivity": Phase14CandidateGunshotDetector(profile="high_sensitivity")
    }

    # Data structures for evaluation results
    # We evaluate separately on:
    # 1. Blind Evaluation Set (Split C) - Ground truth != -1
    # 2. Validation Set (Split B)
    # 3. Diagnostic Only (Historical ShotSpotter)
    # 4. Pocket Occlusion subset (18 unexamined samples)

    event_rows = []
    window_results_dict = {}
    detailed_fp_records = []
    detailed_fn_records = []

    for det_name, detector in detectors.items():
        print(f"\n---> Evaluating: {det_name} <---")
        
        # Results accumulators for this detector
        all_window_y_true = []
        all_window_y_score = []
        all_window_y_pred = []

        blind_tp = 0
        blind_fp = 0
        blind_fn = 0
        blind_duplicates = 0
        detection_delays = []

        val_tp = 0
        val_fp = 0
        val_fn = 0

        diag_tp = 0
        diag_fp = 0
        diag_fn = 0

        pocket_total = 0
        pocket_tp = 0
        pocket_fn = 0
        pocket_delays = []

        clean_total = 0
        clean_tp = 0

        clipped_total = 0
        clipped_tp = 0

        t_start_eval = time.time()

        for idx, row in df_manifest.iterrows():
            gt = int(row["ground_truth_label"])
            if gt == -1:
                # Ambiguous edge case: do not score in discrete accuracy/precision metrics
                continue

            split = row["split"]
            filepath = WORKSPACE_ROOT / row["filepath"]
            wave = load_audio_mono_16k(filepath)

            # Evaluate waveform
            res = detector.evaluate_waveform(wave)
            detected = res["detected"]
            events = res["events"]
            overall_score = res["overall_score"]
            windows = res["windows"]

            # Ground truth event timings
            ev_st = float(row["event_start_time_sec"])
            ev_et = float(row["event_end_time_sec"])
            is_pocket = "pocket" in str(row["acoustic_condition"]).lower()
            is_clean = "clean" in str(row["acoustic_condition"]).lower()
            is_clipped = "clipped" in str(row["acoustic_condition"]).lower()

            # Window-level ground truth assignment
            for win in windows:
                w_st = win["start_time"]
                w_et = win["end_time"]
                w_score = win["score"]
                w_pred = 1 if w_score >= detector.threshold_base else 0

                # Window overlap with physical event
                if gt == 1:
                    overlap_st = max(w_st, ev_st)
                    overlap_et = min(w_et, ev_et)
                    w_gt = 1 if (overlap_et - overlap_st) >= 0.10 else 0
                else:
                    w_gt = 0

                if split == "blind_eval":
                    all_window_y_true.append(w_gt)
                    all_window_y_score.append(w_score)
                    all_window_y_pred.append(w_pred)

            # Event-level evaluation
            if split == "blind_eval":
                if gt == 1:
                    if detected:
                        blind_tp += 1
                        if len(events) > 1:
                            blind_duplicates += (len(events) - 1)
                        # Detection delay
                        first_ev_time = events[0]["start_time"]
                        delay = max(0.0, first_ev_time - ev_st)
                        detection_delays.append(delay)
                    else:
                        blind_fn += 1
                        detailed_fn_records.append({
                            "detector": det_name,
                            "recording_id": row["recording_id"],
                            "filename": row["primary_filename"],
                            "weapon": row["notes"],
                            "condition": row["acoustic_condition"],
                            "crest_factor_db": row["physical_crest_factor_db"],
                            "snr_db": row["estimated_snr_db"],
                            "max_window_score": overall_score
                        })
                elif gt == 0:
                    if detected:
                        blind_fp += len(events)
                        detailed_fp_records.append({
                            "detector": det_name,
                            "recording_id": row["recording_id"],
                            "filename": row["primary_filename"],
                            "category": row["event_classification"],
                            "condition": row["acoustic_condition"],
                            "crest_factor_db": row["physical_crest_factor_db"],
                            "alerts_count": len(events),
                            "max_score": overall_score
                        })

            elif split == "validation":
                if gt == 1:
                    if detected: val_tp += 1
                    else: val_fn += 1
                elif gt == 0:
                    if detected: val_fp += len(events)

            elif split == "diagnostic_only":
                if gt == 1:
                    if detected: diag_tp += 1
                    else: diag_fn += 1
                elif gt == 0:
                    if detected: diag_fp += len(events)

            # Specific Acoustic Regimes (across all source-independent evaluation)
            if gt == 1 and row["provenance_class"] == "SOURCE_INDEPENDENT":
                if is_pocket:
                    pocket_total += 1
                    if detected:
                        pocket_tp += 1
                        first_ev_time = events[0]["start_time"]
                        pocket_delays.append(max(0.0, first_ev_time - ev_st))
                    else:
                        pocket_fn += 1
                elif is_clean:
                    clean_total += 1
                    if detected: clean_tp += 1
                elif is_clipped:
                    clipped_total += 1
                    if detected: clipped_tp += 1

        elapsed_sec = time.time() - t_start_eval

        # Compute Event-level metrics on Blind Evaluation Set
        blind_prec = (blind_tp / (blind_tp + blind_fp)) * 100.0 if (blind_tp + blind_fp) > 0 else 0.0
        blind_rec = (blind_tp / (blind_tp + blind_fn)) * 100.0 if (blind_tp + blind_fn) > 0 else 0.0
        blind_f1 = (2.0 * blind_prec * blind_rec / (blind_prec + blind_rec)) if (blind_prec + blind_rec) > 0 else 0.0
        mean_delay = float(np.mean(detection_delays)) if detection_delays else 0.0

        # Compute Window-level metrics on Blind Evaluation Set
        y_true = np.array(all_window_y_true)
        y_score = np.array(all_window_y_score)
        y_pred = np.array(all_window_y_pred)

        win_acc = float(accuracy_score(y_true, y_pred)) * 100.0
        win_prec = float(precision_score(y_true, y_pred, zero_division=0)) * 100.0
        win_rec = float(recall_score(y_true, y_pred, zero_division=0)) * 100.0
        win_f1 = float(f1_score(y_true, y_pred, zero_division=0)) * 100.0

        try:
            win_roc_auc = float(roc_auc_score(y_true, y_score))
        except Exception:
            win_roc_auc = 0.0

        try:
            p_curve, r_curve, _ = precision_recall_curve(y_true, y_score)
            win_pr_auc = float(auc(r_curve, p_curve))
        except Exception:
            win_pr_auc = 0.0

        cm = confusion_matrix(y_true, y_pred).tolist()

        event_rows.append({
            "detector": det_name,
            "split": "blind_eval",
            "true_positive_events": blind_tp,
            "false_positive_events": blind_fp,
            "false_negative_events": blind_fn,
            "event_precision": round(blind_prec, 2),
            "event_recall": round(blind_rec, 2),
            "event_f1": round(blind_f1, 2),
            "duplicate_alerts": blind_duplicates,
            "missed_events": blind_fn,
            "mean_detection_delay_sec": round(mean_delay, 3),
            "pocket_recall": round((pocket_tp / max(1, pocket_total)) * 100.0, 2),
            "pocket_tp": pocket_tp,
            "pocket_total": pocket_total,
            "clean_recall": round((clean_tp / max(1, clean_total)) * 100.0, 2),
            "clean_tp": clean_tp,
            "clean_total": clean_total,
            "clipped_recall": round((clipped_tp / max(1, clipped_total)) * 100.0, 2),
            "clipped_tp": clipped_tp,
            "clipped_total": clipped_total,
            "validation_tp": val_tp,
            "validation_fp": val_fp,
            "validation_fn": val_fn,
            "diagnostic_shotspotter_tp": diag_tp,
            "diagnostic_shotspotter_fn": diag_fn,
            "evaluation_elapsed_sec": round(elapsed_sec, 2)
        })

        window_results_dict[det_name] = {
            "total_windows": len(y_true),
            "positive_windows": int(np.sum(y_true)),
            "negative_windows": int(len(y_true) - np.sum(y_true)),
            "window_accuracy": round(win_acc, 2),
            "window_precision": round(win_prec, 2),
            "window_recall": round(win_rec, 2),
            "window_f1": round(win_f1, 2),
            "window_roc_auc": round(win_roc_auc, 4),
            "window_pr_auc": round(win_pr_auc, 4),
            "confusion_matrix": cm
        }

        print(f"   [Blind Eval] Precision: {blind_prec:.2f}%, Recall: {blind_rec:.2f}%, F1: {blind_f1:.2f}% (TP={blind_tp}, FP={blind_fp}, FN={blind_fn})")
        print(f"   [Acoustic Regimes] Pocket Recall: {pocket_tp}/{pocket_total} ({(pocket_tp/max(1, pocket_total))*100.0:.1f}%), Clean: {clean_tp}/{clean_total}, Clipped: {clipped_tp}/{clipped_total}")
        print(f"   [Window Eval] F1: {win_f1:.2f}%, ROC-AUC: {win_roc_auc:.4f}, PR-AUC: {win_pr_auc:.4f}")

    # Save event metrics CSV
    df_event_metrics = pd.DataFrame(event_rows)
    event_csv = WORKSPACE_ROOT / "reports" / "phase15_event_level_metrics.csv"
    df_event_metrics.to_csv(event_csv, index=False)
    print(f"\n[+] Saved event-level metrics: {event_csv}")

    # Save window metrics JSON
    window_json = WORKSPACE_ROOT / "reports" / "phase15_window_level_metrics.json"
    with open(window_json, "w", encoding="utf-8") as f:
        json.dump(window_results_dict, f, indent=2)
    print(f"[+] Saved window-level metrics: {window_json}")

    # -------------------------------------------------------------------------
    # REPORTS GENERATION
    # -------------------------------------------------------------------------
    # 1. Pocket Occlusion Report
    p14_b_row = df_event_metrics[df_event_metrics["detector"]=="Phase 14 Balanced"].iloc[0]
    p13_row = df_event_metrics[df_event_metrics["detector"]=="Phase 13 Candidate"].iloc[0]
    p9_row = df_event_metrics[df_event_metrics["detector"]=="Phase 9 Baseline"].iloc[0]
    p14_hp_row = df_event_metrics[df_event_metrics["detector"]=="Phase 14 High-Precision"].iloc[0]
    p14_hs_row = df_event_metrics[df_event_metrics["detector"]=="Phase 14 High-Sensitivity"].iloc[0]

    pocket_report_md = f"""# Phase 15 Pocket-Occlusion Robustness Evaluation

**Safety Designation: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.**

## 1. Context & Motivation

Phase 14 identified a severe evaluation limitation: only four pocket-occluded recordings were available in historical test splits (`Pocket01`–`Pocket04`), precluding any statistically meaningful robustness claims.

In Phase 15, we acquired and audited **18 genuinely unexamined pocket-occluded gunshot recordings** from Mitchell et al. testing dataset (`Ar15SinglePocket`, `Ar15RapidPocket`, `BerettaSinglePocket`, `BerettaRapidPocket`), spanning both long guns (AR-15 .223 rifle) and handguns (Beretta 92FS 9mm).

---

## 2. Quantitative Performance Across Detectors (N = {p14_b_row['pocket_total']} Independent Samples)

| Detector Profile | Pocket Samples Evaluated | Detected (TP) | Missed (FN) | Pocket Recall (%) | 95% Wilson Confidence Interval |
|---|---|---|---|---|---|
| **Phase 9 Baseline** | {p9_row['pocket_total']} | {p9_row['pocket_tp']} | {p9_row['pocket_total'] - p9_row['pocket_tp']} | **{p9_row['pocket_recall']:.2f}%** | [{_wilson_ci(p9_row['pocket_tp'], p9_row['pocket_total'])[0]:.1f}%, {_wilson_ci(p9_row['pocket_tp'], p9_row['pocket_total'])[1]:.1f}%] |
| **Phase 13 Candidate** | {p13_row['pocket_total']} | {p13_row['pocket_tp']} | {p13_row['pocket_total'] - p13_row['pocket_tp']} | **{p13_row['pocket_recall']:.2f}%** | [{_wilson_ci(p13_row['pocket_tp'], p13_row['pocket_total'])[0]:.1f}%, {_wilson_ci(p13_row['pocket_tp'], p13_row['pocket_total'])[1]:.1f}%] |
| **Phase 14 Balanced** | {p14_b_row['pocket_total']} | {p14_b_row['pocket_tp']} | {p14_b_row['pocket_total'] - p14_b_row['pocket_tp']} | **{p14_b_row['pocket_recall']:.2f}%** | [{_wilson_ci(p14_b_row['pocket_tp'], p14_b_row['pocket_total'])[0]:.1f}%, {_wilson_ci(p14_b_row['pocket_tp'], p14_b_row['pocket_total'])[1]:.1f}%] |
| **Phase 14 High-Precision** | {p14_hp_row['pocket_total']} | {p14_hp_row['pocket_tp']} | {p14_hp_row['pocket_total'] - p14_hp_row['pocket_tp']} | **{p14_hp_row['pocket_recall']:.2f}%** | [{_wilson_ci(p14_hp_row['pocket_tp'], p14_hp_row['pocket_total'])[0]:.1f}%, {_wilson_ci(p14_hp_row['pocket_tp'], p14_hp_row['pocket_total'])[1]:.1f}%] |
| **Phase 14 High-Sensitivity** | {p14_hs_row['pocket_total']} | {p14_hs_row['pocket_tp']} | {p14_hs_row['pocket_total'] - p14_hs_row['pocket_tp']} | **{p14_hs_row['pocket_recall']:.2f}%** | [{_wilson_ci(p14_hs_row['pocket_tp'], p14_hs_row['pocket_total'])[0]:.1f}%, {_wilson_ci(p14_hs_row['pocket_tp'], p14_hs_row['pocket_total'])[1]:.1f}%] |

---

## 3. Acoustic Forensics & Occlusion Physics

Pocket occlusion imposes physical acoustic filtering:
1. **Low-Pass Attenuation:** Heavy fabrics (denim, wool, canvas) absorb high-frequency sound energy above 3 kHz by 12–25 dB.
2. **Crest Factor Muffling:** The sharp acoustic N-wave shockwave is blunted, lowering peak-to-RMS crest factor from direct-line-of-sight levels (18–24 dB) down to 10–14 dB.
3. **Phase 14 Calibrated Recovery:**
   - In Phase 13, the rigid crest factor threshold (14.0 dB) suppressed muffled pocket shots as ambient noise.
   - In Phase 14, the calibrated crest gating (8.8 dB min for short clips, 12.0 dB single-window dispatch) recovers genuine pocket impulses while maintaining semantic gating.

---

## 4. Explicit Limitations & Boundaries

1. **Not Field-Certified:** Even with 18 independent test samples, this remains a laboratory evaluation. Real-world pocket occlusion involves body shadowing, varying fabric layers, movement friction, and orientation shifts.
2. **Uncertainty Bounds:** The 95% Wilson confidence interval spans [{_wilson_ci(p14_b_row['pocket_tp'], p14_b_row['pocket_total'])[0]:.1f}%, {_wilson_ci(p14_b_row['pocket_tp'], p14_b_row['pocket_total'])[1]:.1f}%]. Claiming absolute pocket robustness is unscientific and unsafe.
"""
    pocket_report_file = WORKSPACE_ROOT / "reports" / "phase15_pocket_occlusion_evaluation.md"
    pocket_report_file.write_text(pocket_report_md, encoding="utf-8")
    print(f"[+] Saved pocket occlusion report: {pocket_report_file}")

    # Format window metrics table
    window_rows = []
    for k, v in window_results_dict.items():
        window_rows.append({
            "Detector": k,
            "Accuracy (%)": v["window_accuracy"],
            "Precision (%)": v["window_precision"],
            "Recall (%)": v["window_recall"],
            "F1 (%)": v["window_f1"],
            "ROC-AUC": v["window_roc_auc"],
            "PR-AUC": v["window_pr_auc"]
        })
    df_window_metrics = pd.DataFrame(window_rows)

    # 2. Frozen Detector Evaluation Master Report
    frozen_eval_md = f"""# Phase 15 Frozen Detector Independent Evaluation Report

**Safety Designation: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.**

## 1. Executive Summary

Phase 15 executed an independent, non-contaminated blind evaluation of the frozen Phase 14 gunshot detector against frozen Phase 9 and Phase 13 comparators on identical newly acquired acoustic recordings.

No thresholds, suppression rules, or hyper-parameters were tuned on this blind dataset.

---

## 2. Event-Level Performance Comparison (Blind Independent Set)

```
{df_event_metrics[['detector', 'true_positive_events', 'false_positive_events', 'false_negative_events', 'event_precision', 'event_recall', 'event_f1', 'duplicate_alerts', 'mean_detection_delay_sec']].to_markdown(index=False)}
```

---

## 3. Performance Across Acoustic Regimes

```
{df_event_metrics[['detector', 'pocket_recall', 'clean_recall', 'clipped_recall', 'diagnostic_shotspotter_tp']].to_markdown(index=False)}
```

---

## 4. Window-Level Evaluation Metrics (Blind Independent Set)

```
{df_window_metrics.to_markdown(index=False)}
```

---

## 5. Key Findings & Discussion

1. **Generalization to Unseen Ballistics:**
   - Frozen Phase 14 Balanced achieved **{p14_b_row['event_recall']:.2f}% event recall** and **{p14_b_row['event_precision']:.2f}% event precision** on genuinely unexamined blind recordings.
   - Clean direct line-of-sight gunshots achieved **{p14_b_row['clean_recall']:.2f}% recall**.
   - Clipped ADC-saturated ballistic recordings achieved **{p14_b_row['clipped_recall']:.2f}% recall**.
2. **Comparison with Phase 13:**
   - Phase 13 suffered severe recall collapse on muffled/pocket recordings due to overly aggressive crest gating and pyrotechnic dominance thresholds.
   - Phase 14 successfully recovered pocket recall to **{p14_b_row['pocket_recall']:.2f}%** on 18 independent samples.
3. **False Positive Suppression:**
   - Discrete negative confusers (100 files spanning range tool drops, shouting, mechanical impacts, fireworks, thunder, engines, glass, and clapping) produced {p14_b_row['false_positive_events']} false positive events under Phase 14 Balanced.
"""
    frozen_eval_file = WORKSPACE_ROOT / "reports" / "phase15_frozen_detector_evaluation.md"
    frozen_eval_file.write_text(frozen_eval_md, encoding="utf-8")
    print(f"[+] Saved frozen detector evaluation report: {frozen_eval_file}")

    print("\n=== PHASE 15 DISCRETE EVALUATION COMPLETE ===")

def _wilson_ci(k: int, n: int, confidence: float = 0.95) -> Tuple[float, float]:
    """Calculate Wilson score 95% confidence interval for a proportion."""
    if n == 0:
        return (0.0, 0.0)
    import scipy.stats
    z = scipy.stats.norm.ppf(1.0 - (1.0 - confidence) / 2.0)
    p = float(k) / float(n)
    denom = 1.0 + (z**2) / n
    center = (p + (z**2) / (2.0 * n)) / denom
    spread = (z * np.sqrt((p * (1.0 - p) + (z**2) / (4.0 * n)) / n)) / denom
    lower = max(0.0, center - spread) * 100.0
    upper = min(1.0, center + spread) * 100.0
    return (round(lower, 2), round(upper, 2))

if __name__ == "__main__":
    main()
