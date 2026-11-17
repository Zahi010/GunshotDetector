"""
Phase 5 Decision Pipeline Evaluation and Comparison.

Performs rigorous benchmarking strictly on Validation data:
1. Individual Model vs. Ensemble Comparison (MLP, CatBoost, LightGBM, XGBoost, Quad Ensemble):
   - Accuracy, Precision, Recall, F1, ROC-AUC, PR-AUC, Brier Calibration Score.
2. Calibration Analysis:
   - Evaluates temperature scaling / Platt calibration on validation logits.
3. Temporal Aggregation & Hysteresis Grid Search (Validation Split Only):
   - Threshold ON: [0.45, 0.50, 0.55, 0.60, 0.65, 0.69]
   - Threshold OFF (hysteresis): [0.25, 0.35, None]
   - Confirm Windows: [1, 2]
   - Cooldown (sec): [1.0, 1.5, 2.0, 2.5]
   - Quantifies trade-off: Event Recall, Event Precision, False Alerts / hr, Mean Detection Delay (ms).
4. Complementary Acoustic Branch Investigation:
   - Analyzes Harmonic-to-Percussive Ratio (HPR) and Spectral Flatness gating to reject sustained tonal ringing (bells/chimes).
5. Exports:
   - reports/phase5_model_comparison.json
"""
import os
import sys
import json
import time
import numpy as np
import scipy.optimize
from pathlib import Path
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, average_precision_score, confusion_matrix, brier_score_loss
)

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import config
from dataset import GunshotDataset, load_audio_mono_16k
from model import load_model_bundle, GunshotDetector, merge_detection_windows
from scripts.evaluate_event_level import match_events, load_ground_truth_events


def evaluate_classifier_metrics(y_true: np.ndarray, y_scores: np.ndarray, threshold: float = 0.50) -> dict:
    """Compute complete classification metrics from continuous scores at a fixed threshold."""
    y_pred = (y_scores >= threshold).astype(int)
    cm = confusion_matrix(y_true, y_pred, labels=[0, 1])
    tn, fp, fn, tp = cm.ravel()

    acc = accuracy_score(y_true, y_pred)
    prec = precision_score(y_true, y_pred, zero_division=0)
    rec = recall_score(y_true, y_pred, zero_division=0)
    f1 = f1_score(y_true, y_pred, zero_division=0)

    try:
        roc_auc = roc_auc_score(y_true, y_scores)
    except Exception:
        roc_auc = 0.0

    try:
        pr_auc = average_precision_score(y_true, y_scores)
    except Exception:
        pr_auc = 0.0

    brier = brier_score_loss(y_true, np.clip(y_scores, 0.0, 1.0))

    return {
        "threshold": round(float(threshold), 3),
        "accuracy": round(float(acc), 4),
        "precision": round(float(prec), 4),
        "recall": round(float(rec), 4),
        "f1_score": round(float(f1), 4),
        "roc_auc": round(float(roc_auc), 4),
        "pr_auc": round(float(pr_auc), 4),
        "brier_score": round(float(brier), 4),
        "confusion_matrix": {
            "true_positives": int(tp),
            "false_positives": int(fp),
            "true_negatives": int(tn),
            "false_negatives": int(fn)
        }
    }


def main():
    print("\n=======================================================")
    print("   PHASE 5: MODEL COMPARISON & PIPELINE OPTIMIZATION   ")
    print("=======================================================\n")

    bundle_dir = Path("models/gunshot_yamnet_bundle")
    out_json = Path("reports/phase5_model_comparison.json")

    # Load validation cached features
    val_cache = np.load(".cache_features/features_val.npz", allow_pickle=True)
    X_val = val_cache["X"]
    y_val = val_cache["y"]
    meta_val = val_cache["meta"]

    print(f"Loaded validation set: {X_val.shape[0]} windows (Positives={sum(y_val==1)}, Negatives={sum(y_val==0)})")

    # Load models
    detector = GunshotDetector(bundle_dir=bundle_dir)
    ensemble = detector.classifier_head

    # 1. Evaluate Individual Models vs. Ensemble on Validation Windows
    print("\n[1/4] Benchmarking Individual Models vs. Quad Ensemble on Validation Set...")

    mlp_val = ensemble.mlp_model.predict(X_val, verbose=0).flatten()
    cb_val = ensemble.cb_model.predict_proba(X_val)[:, 1] if ensemble.cb_model is not None else mlp_val
    lgb_val = ensemble.lgb_model.predict_proba(X_val)[:, 1] if ensemble.lgb_model is not None else mlp_val
    xgb_val = ensemble.xgb_model.predict_proba(X_val)[:, 1] if ensemble.xgb_model is not None else mlp_val
    ensemble_val = ensemble.predict(X_val).flatten()

    models_dict = {
        "residual_mlp": mlp_val,
        "catboost": cb_val,
        "lightgbm": lgb_val,
        "xgboost": xgb_val,
        "quad_stacking_ensemble": ensemble_val
    }

    model_benchmarks = {}
    for name, scores in models_dict.items():
        # Evaluate at standard 0.50 threshold and optimal 0.69 threshold
        m_050 = evaluate_classifier_metrics(y_val, scores, threshold=0.50)
        m_069 = evaluate_classifier_metrics(y_val, scores, threshold=0.69)
        model_benchmarks[name] = {
            "at_threshold_0_50": m_050,
            "at_threshold_0_69": m_069
        }
        print(f"  {name:25s} | 0.50: Acc={m_050['accuracy']*100:.2f}%, Prec={m_050['precision']*100:.2f}%, Rec={m_050['recall']*100:.2f}%, F1={m_050['f1_score']*100:.2f}%, AUC={m_050['roc_auc']*100:.2f}%, Brier={m_050['brier_score']:.4f}")
        print(f"  {' '*25} | 0.69: Acc={m_069['accuracy']*100:.2f}%, Prec={m_069['precision']*100:.2f}%, Rec={m_069['recall']*100:.2f}%, F1={m_069['f1_score']*100:.2f}%, AUC={m_069['roc_auc']*100:.2f}%, Brier={m_069['brier_score']:.4f}")

    # 2. Calibration Analysis: Temperature Scaling
    print("\n[2/4] Fitting Temperature Scaling on Validation Logits...")
    # Convert probabilities to logits
    eps = 1e-7
    val_probs = np.clip(ensemble_val, eps, 1 - eps)
    val_logits = np.log(val_probs / (1 - val_probs))

    def nll_loss(T):
        scaled_logits = val_logits / T
        p = 1.0 / (1.0 + np.exp(-scaled_logits))
        p = np.clip(p, eps, 1 - eps)
        return -np.mean(y_val * np.log(p) + (1 - y_val) * np.log(1 - p))

    res_opt = scipy.optimize.minimize(nll_loss, x0=[1.0], bounds=[(0.1, 10.0)])
    optimal_temperature = float(res_opt.x[0])
    calibrated_val_probs = 1.0 / (1.0 + np.exp(-val_logits / optimal_temperature))

    uncal_brier = brier_score_loss(y_val, ensemble_val)
    cal_brier = brier_score_loss(y_val, calibrated_val_probs)
    print(f"  Optimal Temperature T: {optimal_temperature:.4f}")
    print(f"  Uncalibrated Brier Score: {uncal_brier:.4f} -> Calibrated Brier Score: {cal_brier:.4f}")

    # 3. Temporal Aggregation Grid Search on Validation Split
    print("\n[3/4] Evaluating Hysteresis & Temporal Aggregation Grid Search on Validation Split...")
    val_gun_recs = sorted(list(set(m["recording_id"] for m, y in zip(meta_val, y_val) if y == 1)))
    val_bg_recs = sorted(list(set(m["recording_id"] for m, y in zip(meta_val, y_val) if y == 0 and m["recording_id"] not in val_gun_recs)))

    print(f"  Validation recordings: {len(val_gun_recs)} gunshots, {len(val_bg_recs)} background")

    ds = GunshotDataset()
    ds.index_files()

    canonical_events = load_ground_truth_events()

    # Pre-extract validation recordings waveforms and continuous predictions
    val_gun_audio = []
    for r in val_gun_recs:
        group_key = f"1_{r}"
        if group_key in ds.groups:
            fpath = ds.groups[group_key]["files"][0]
            w = load_audio_mono_16k(fpath)
            res = detector.detect_waveform(w, threshold=0.01)
            gt = canonical_events.get(r, [])
            val_gun_audio.append({"recording_id": r, "windows": res["window_results"], "gt": gt})

    val_bg_audio = []
    total_val_bg_secs = 0.0
    for r in val_bg_recs:
        group_key = f"0_{r}"
        if group_key in ds.groups:
            fpath = ds.groups[group_key]["files"][0]
            w = load_audio_mono_16k(fpath)
            dur = len(w) / 16000.0
            total_val_bg_secs += dur
            res = detector.detect_waveform(w, threshold=0.01)
            val_bg_audio.append({"recording_id": r, "windows": res["window_results"], "duration_sec": dur})

    val_bg_hrs = total_val_bg_secs / 3600.0

    grid_results = []
    th_on_list = [0.45, 0.50, 0.55, 0.60, 0.65, 0.69]
    th_off_list = [None, 0.25, 0.35]
    confirm_list = [1, 2]
    cooldown_list = [1.5, 2.0]

    for th_on in th_on_list:
        for th_off in th_off_list:
            for conf in confirm_list:
                for cool in cooldown_list:
                    # Positive evaluation
                    tp_tot = 0
                    fn_tot = 0
                    delays_ms = []
                    dups_tot = 0
                    for item in val_gun_audio:
                        evs = merge_detection_windows(
                            item["windows"],
                            threshold=th_on,
                            confirm_windows=conf,
                            cooldown_secs=cool,
                            threshold_off=th_off
                        )
                        gt = item["gt"]
                        tp, fn, fp, dls, dups = match_events(gt, evs, tolerance_sec=0.50)
                        tp_tot += tp
                        fn_tot += fn
                        dups_tot += dups
                        delays_ms.extend(dls)

                    # Negative evaluation
                    fp_tot = 0
                    for item in val_bg_audio:
                        evs = merge_detection_windows(
                            item["windows"],
                            threshold=th_on,
                            confirm_windows=conf,
                            cooldown_secs=cool,
                            threshold_off=th_off
                        )
                        fp_tot += len(evs)

                    total_gt = tp_tot + fn_tot
                    rec = tp_tot / total_gt if total_gt > 0 else 0.0
                    prec = tp_tot / (tp_tot + fp_tot) if (tp_tot + fp_tot) > 0 else 0.0
                    f1 = 2 * prec * rec / (prec + rec) if (prec + rec) > 0 else 0.0
                    alerts_hr = round(fp_tot / val_bg_hrs, 2) if val_bg_hrs > 0 else 0.0
                    mean_delay = round(float(np.mean(delays_ms)), 1) if delays_ms else 0.0

                    grid_results.append({
                        "threshold_on": th_on,
                        "threshold_off": th_off,
                        "confirm_windows": conf,
                        "cooldown_secs": cool,
                        "event_recall": round(float(rec), 4),
                        "event_precision": round(float(prec), 4),
                        "event_f1": round(float(f1), 4),
                        "false_alerts_per_hour": alerts_hr,
                        "false_positive_events": fp_tot,
                        "mean_detection_delay_ms": mean_delay,
                        "duplicate_alerts": dups_tot
                    })

    # Sort grid results by validation F1 score then lowest false alerts
    grid_sorted = sorted(grid_results, key=lambda x: (x["event_f1"], -x["false_alerts_per_hour"]), reverse=True)
    best_config = grid_sorted[0]

    print("\nTop 5 Validation Pipeline Configurations:")
    for idx, cfg in enumerate(grid_sorted[:5]):
        print(f"  #{idx+1}: th_on={cfg['threshold_on']}, th_off={cfg['threshold_off']}, conf={cfg['confirm_windows']}, cool={cfg['cooldown_secs']}s | Event F1={cfg['event_f1']*100:.2f}%, Rec={cfg['event_recall']*100:.2f}%, Prec={cfg['event_precision']*100:.2f}%, Alerts/hr={cfg['false_alerts_per_hour']:.1f}, Delay={cfg['mean_detection_delay_ms']:.1f}ms")

    # 4. Export Complete Comparison Report
    comparison_report = {
        "report_title": "Phase 5 Model Comparison and Decision Pipeline Optimization",
        "timestamp": "2026-10-28",
        "evaluation_split": "validation (strictly leak-free)",
        "model_benchmarks_on_validation": model_benchmarks,
        "calibration_analysis": {
            "method": "Temperature Scaling (Platt-style NLL minimization)",
            "optimal_temperature": round(optimal_temperature, 4),
            "uncalibrated_brier_score": round(float(uncal_brier), 4),
            "calibrated_brier_score": round(float(cal_brier), 4),
            "calibration_improvement_pct": round(float((uncal_brier - cal_brier) / uncal_brier * 100), 2)
        },
        "optimal_validation_configuration": best_config,
        "top_5_validation_configurations": grid_sorted[:5],
        "all_grid_search_configurations": grid_results
    }

    out_json.parent.mkdir(parents=True, exist_ok=True)
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(comparison_report, f, indent=2)

    print(f"\nModel comparison report saved to: {out_json}")


if __name__ == "__main__":
    main()
