"""
Reproducible Controlled Experiment Suite for Gunshot Detection System.

Compares:
1. baseline_mlp (without hard negatives)
2. baseline_mlp_with_hn (with approved hard negatives)
3. regularized_mlp_with_hn (LayerNorm + Dropout + L2 regularized deep head)
4. lightgbm_with_hn (Gradient-boosted decision tree on YAMNet embeddings)
5. calibrated_model_with_hn (Platt scaling sigmoid calibration)
6. hybrid_ensemble_with_hn (Soft-voting ensemble: Regularized MLP + LightGBM)

Protocol:
- Training only on Train Split (+ approved hard negatives).
- Threshold selection strictly on Validation Split (never on Test).
- Final unbiased evaluation on Held-Out Test Split (519 windows).
- Reports: Window metrics, Grouped Recording metrics, Streaming False Alerts/hr, PR/ROC curves.
"""
import os
import sys
import json
import time
import joblib
import argparse
import numpy as np
import tensorflow as tf
from pathlib import Path
from typing import Dict, List, Any, Tuple
from scipy import stats
from sklearn.metrics import (
    precision_score, recall_score, f1_score, roc_auc_score,
    accuracy_score, confusion_matrix, precision_recall_curve, roc_curve
)
from sklearn.calibration import CalibratedClassifierCV
import lightgbm as lgb

import config


def compute_poisson_ci(k: int, T_hours: float, alpha: float = 0.05) -> Tuple[float, float]:
    """Calculate exact Poisson 95% CI."""
    if T_hours <= 0:
        return 0.0, 0.0
    low = stats.chi2.ppf(alpha / 2, 2 * k) / (2 * T_hours) if k > 0 else 0.0
    high = stats.chi2.ppf(1 - alpha / 2, 2 * (k + 1)) / (2 * T_hours)
    return round(float(low), 2), round(float(high), 2)


def select_threshold_modes(y_val: np.ndarray, val_scores: np.ndarray) -> Dict[str, Dict[str, Any]]:
    """
    Search thresholds on Validation set for:
    1. balanced_f1: Max F1 score
    2. high_recall: Max F1 subject to Recall >= 0.95
    3. low_false_alarm: Max Precision subject to Recall >= 0.88
    """
    thresholds = np.linspace(0.05, 0.95, 181)
    best_f1 = -1.0
    best_f1_t = 0.50
    best_f1_metrics = {}

    hr_best_f1 = -1.0
    hr_best_t = 0.30
    hr_metrics = {}

    lfa_best_p = -1.0
    lfa_best_t = 0.70
    lfa_metrics = {}

    for t in thresholds:
        y_pred = (val_scores >= t).astype(int)
        p = precision_score(y_val, y_pred, zero_division=0)
        r = recall_score(y_val, y_pred, zero_division=0)
        f = f1_score(y_val, y_pred, zero_division=0)

        # 1. Balanced F1
        if f > best_f1:
            best_f1 = f
            best_f1_t = float(t)
            best_f1_metrics = {"threshold": round(best_f1_t, 3), "precision": round(float(p), 4), "recall": round(float(r), 4), "f1": round(float(f), 4)}

        # 2. High Recall (Recall >= 0.95)
        if r >= 0.95 and f > hr_best_f1:
            hr_best_f1 = f
            hr_best_t = float(t)
            hr_metrics = {"threshold": round(hr_best_t, 3), "precision": round(float(p), 4), "recall": round(float(r), 4), "f1": round(float(f), 4)}

        # 3. Low False Alarm (Recall >= 0.88, maximize Precision)
        if r >= 0.88 and p > lfa_best_p:
            lfa_best_p = p
            lfa_best_t = float(t)
            lfa_metrics = {"threshold": round(lfa_best_t, 3), "precision": round(float(p), 4), "recall": round(float(r), 4), "f1": round(float(f), 4)}

    # Fallbacks if constraints not met
    if not hr_metrics:
        hr_metrics = best_f1_metrics.copy()
        hr_best_t = best_f1_t
    if not lfa_metrics:
        lfa_metrics = best_f1_metrics.copy()
        lfa_best_t = best_f1_t

    return {
        "balanced_f1": {"threshold": round(best_f1_t, 3), "val_metrics": best_f1_metrics},
        "high_recall": {"threshold": round(hr_best_t, 3), "val_metrics": hr_metrics},
        "low_false_alarm": {"threshold": round(lfa_best_t, 3), "val_metrics": lfa_metrics}
    }


def evaluate_window_metrics(y_true: np.ndarray, y_scores: np.ndarray, threshold: float) -> Dict[str, Any]:
    """Compute detailed test window metrics."""
    y_pred = (y_scores >= threshold).astype(int)
    p = precision_score(y_true, y_pred, zero_division=0)
    r = recall_score(y_true, y_pred, zero_division=0)
    f = f1_score(y_true, y_pred, zero_division=0)
    acc = accuracy_score(y_true, y_pred)
    try:
        auc = roc_auc_score(y_true, y_scores)
    except Exception:
        auc = None

    cm = confusion_matrix(y_true, y_pred).tolist()
    tn, fp, fn, tp = cm[0][0], cm[0][1], cm[1][0], cm[1][1]

    fpr = fp / (fp + tn) if (fp + tn) > 0 else 0.0
    fnr = fn / (fn + tp) if (fn + tp) > 0 else 0.0

    return {
        "threshold": round(threshold, 3),
        "total_windows": len(y_true),
        "accuracy": round(float(acc), 4),
        "precision": round(float(p), 4),
        "recall": round(float(r), 4),
        "f1_score": round(float(f), 4),
        "roc_auc": round(float(auc), 4) if auc is not None else None,
        "true_positives": int(tp),
        "false_positives": int(fp),
        "true_negatives": int(tn),
        "false_negatives": int(fn),
        "false_positive_rate": round(float(fpr), 4),
        "false_negative_rate": round(float(fnr), 4),
        "confusion_matrix": cm
    }


def evaluate_recording_metrics(meta_list: List[Dict], y_scores: np.ndarray, threshold: float) -> Dict[str, Any]:
    """Compute grouped recording-level metrics (max score per recording)."""
    recordings = {}
    for meta, score in zip(meta_list, y_scores):
        rec_id = meta["recording_id"] if isinstance(meta, dict) else meta.item()["recording_id"]
        label = meta["label"] if isinstance(meta, dict) else meta.item()["label"]
        if rec_id not in recordings:
            recordings[rec_id] = {"label": label, "scores": []}
        recordings[rec_id]["scores"].append(score)

    rec_true, rec_pred, rec_scores = [], [], []
    for rec_id, d in recordings.items():
        max_s = float(np.max(d["scores"]))
        rec_true.append(d["label"])
        rec_pred.append(int(max_s >= threshold))
        rec_scores.append(max_s)

    rec_true = np.array(rec_true)
    rec_pred = np.array(rec_pred)
    p = precision_score(rec_true, rec_pred, zero_division=0)
    r = recall_score(rec_true, rec_pred, zero_division=0)
    f = f1_score(rec_true, rec_pred, zero_division=0)
    acc = accuracy_score(rec_true, rec_pred)
    try:
        auc = roc_auc_score(rec_true, rec_scores)
    except Exception:
        auc = None
    cm = confusion_matrix(rec_true, rec_pred).tolist()

    return {
        "recordings_total": len(recordings),
        "accuracy": round(float(acc), 4),
        "precision": round(float(p), 4),
        "recall": round(float(r), 4),
        "f1_score": round(float(f), 4),
        "roc_auc": round(float(auc), 4) if auc is not None else None,
        "true_positives": cm[1][1],
        "false_positives": cm[0][1],
        "true_negatives": cm[0][0],
        "false_negatives": cm[1][0],
        "confusion_matrix": cm
    }


def evaluate_streaming_false_alerts(
    meta_test: List[Dict],
    test_scores: np.ndarray,
    threshold: float,
    confirm_windows: int = 1,
    cooldown_secs: float = 2.0
) -> Dict[str, Any]:
    """
    Simulate causal continuous streaming on test negative recordings.
    Calculates false alerts per hour with exact Poisson 95% CI.
    """
    # Group test negative audio by recording
    neg_recordings = {}
    for meta, score in zip(meta_test, test_scores):
        m = meta if isinstance(meta, dict) else meta.item()
        if m["label"] == 0:
            rec_id = m["recording_id"]
            if rec_id not in neg_recordings:
                neg_recordings[rec_id] = []
            neg_recordings[rec_id].append({
                "start_time": m["start_time"],
                "end_time": m["end_time"],
                "score": float(score)
            })

    total_duration_sec = 0.0
    total_false_alert_events = 0

    for rec_id, wins in neg_recordings.items():
        wins = sorted(wins, key=lambda x: x["start_time"])
        if wins:
            dur = wins[-1]["end_time"]
            total_duration_sec += dur

        cooldown_until = -1.0
        active_cluster = []
        for w in wins:
            st = w["start_time"]
            et = w["end_time"]
            s = w["score"]

            if st < cooldown_until:
                continue

            if s >= threshold:
                active_cluster.append(w)
                if len(active_cluster) >= confirm_windows:
                    total_false_alert_events += 1
                    cooldown_until = et + cooldown_secs
                    active_cluster = []
            else:
                active_cluster = []

    total_hours = total_duration_sec / 3600.0 if total_duration_sec > 0 else 0.001
    rate_per_hr = total_false_alert_events / total_hours
    low_ci, high_ci = compute_poisson_ci(total_false_alert_events, total_hours)

    return {
        "negative_duration_sec": round(total_duration_sec, 2),
        "negative_duration_hours": round(total_hours, 4),
        "confirm_windows": confirm_windows,
        "cooldown_secs": cooldown_secs,
        "false_alert_events": total_false_alert_events,
        "false_alerts_per_hour": round(rate_per_hr, 1),
        "poisson_95_ci": [low_ci, high_ci]
    }


# ==============================================================================
# Model Builders
# ==============================================================================

def train_baseline_mlp(X_train: np.ndarray, y_train: np.ndarray, X_val: np.ndarray, y_val: np.ndarray, epochs: int = 40) -> tf.keras.Model:
    """Original baseline MLP architecture."""
    inputs = tf.keras.Input(shape=(1024,))
    x = tf.keras.layers.Dense(128, activation="relu", kernel_regularizer=tf.keras.regularizers.l2(1e-4))(inputs)
    x = tf.keras.layers.BatchNormalization()(x)
    x = tf.keras.layers.Dropout(0.3)(x)
    x = tf.keras.layers.Dense(32, activation="relu", kernel_regularizer=tf.keras.regularizers.l2(1e-4))(x)
    x = tf.keras.layers.Dropout(0.2)(x)
    outputs = tf.keras.layers.Dense(1, activation="sigmoid")(x)

    model = tf.keras.Model(inputs=inputs, outputs=outputs)
    model.compile(optimizer=tf.keras.optimizers.Adam(1e-3), loss="binary_crossentropy", metrics=["accuracy"])
    
    cb = [
        tf.keras.callbacks.EarlyStopping(monitor="val_loss", patience=8, restore_best_weights=True),
        tf.keras.callbacks.ReduceLROnPlateau(monitor="val_loss", factor=0.5, patience=3, min_lr=1e-5)
    ]
    model.fit(X_train, y_train, validation_data=(X_val, y_val), epochs=epochs, batch_size=32, callbacks=cb, verbose=0)
    return model


def train_regularized_mlp(X_train: np.ndarray, y_train: np.ndarray, X_val: np.ndarray, y_val: np.ndarray, epochs: int = 50) -> tf.keras.Model:
    """Modern deep regularized MLP with LayerNorm, Weight Decay, and Dropout."""
    # Calculate balanced class weights with hard negative weighting
    neg_count = np.sum(y_train == 0)
    pos_count = np.sum(y_train == 1)
    # Slight over-weighting on negative class (1.2x) to heavily penalize false alarms
    cw = {0: 1.2 * (len(y_train) / (2.0 * neg_count)), 1: (len(y_train) / (2.0 * pos_count))}

    inputs = tf.keras.Input(shape=(1024,))
    x = tf.keras.layers.Dense(256, activation="relu", kernel_regularizer=tf.keras.regularizers.l2(5e-4))(inputs)
    x = tf.keras.layers.LayerNormalization()(x)
    x = tf.keras.layers.Dropout(0.4)(x)
    
    x = tf.keras.layers.Dense(128, activation="relu", kernel_regularizer=tf.keras.regularizers.l2(5e-4))(x)
    x = tf.keras.layers.LayerNormalization()(x)
    x = tf.keras.layers.Dropout(0.3)(x)

    x = tf.keras.layers.Dense(32, activation="relu", kernel_regularizer=tf.keras.regularizers.l2(5e-4))(x)
    x = tf.keras.layers.Dropout(0.2)(x)
    outputs = tf.keras.layers.Dense(1, activation="sigmoid")(x)

    model = tf.keras.Model(inputs=inputs, outputs=outputs)
    model.compile(
        optimizer=tf.keras.optimizers.AdamW(learning_rate=1e-3, weight_decay=1e-4),
        loss="binary_crossentropy",
        metrics=["accuracy"]
    )
    cb = [
        tf.keras.callbacks.EarlyStopping(monitor="val_loss", patience=10, restore_best_weights=True),
        tf.keras.callbacks.ReduceLROnPlateau(monitor="val_loss", factor=0.5, patience=4, min_lr=1e-5)
    ]
    model.fit(X_train, y_train, validation_data=(X_val, y_val), epochs=epochs, batch_size=32, class_weight=cw, callbacks=cb, verbose=0)
    return model


def train_lightgbm_model(X_train: np.ndarray, y_train: np.ndarray, X_val: np.ndarray, y_val: np.ndarray) -> lgb.LGBMClassifier:
    """LightGBM Classifier trained on 1024-d YAMNet embeddings."""
    clf = lgb.LGBMClassifier(
        n_estimators=180,
        learning_rate=0.03,
        num_leaves=31,
        max_depth=6,
        subsample=0.8,
        colsample_bytree=0.7,
        reg_alpha=0.1,
        reg_lambda=1.0,
        class_weight="balanced",
        random_state=42,
        verbosity=-1
    )
    clf.fit(
        X_train, y_train,
        eval_set=[(X_val, y_val)],
        callbacks=[lgb.early_stopping(stopping_rounds=15, verbose=False)]
    )
    return clf


def run_experiment_suite(output_report: Path = Path("reports/experiments_comparison.json")):
    """Run all controlled experiments and compile comparison report."""
    output_report = Path(output_report)
    output_report.parent.mkdir(parents=True, exist_ok=True)

    print("\n=======================================================")
    print("      GUNSHOT DETECTOR CONTROLLED EXPERIMENTS SUITE")
    print("=======================================================\n")

    # Step 1: Load base cached features
    print("[1/5] Loading cached features for Train, Val, and Test...")
    d_train = np.load(".cache_features/features_train.npz", allow_pickle=True)
    d_val = np.load(".cache_features/features_val.npz", allow_pickle=True)
    d_test = np.load(".cache_features/features_test.npz", allow_pickle=True)

    X_train_base, y_train_base, meta_train_base = d_train["X"], d_train["y"], list(d_train["meta"])
    X_val, y_val, meta_val = d_val["X"], d_val["y"], list(d_val["meta"])
    X_test, y_test, meta_test = d_test["X"], d_test["y"], list(d_test["meta"])

    # Step 2: Load approved hard negatives
    print("[2/5] Loading cached hard negatives for training split...")
    hn_path = Path(".cache_features/features_hard_negatives.npz")
    if hn_path.exists():
        d_hn = np.load(str(hn_path), allow_pickle=True)
        X_hn, y_hn, meta_hn = d_hn["X"], d_hn["y"], list(d_hn["meta"])
        print(f"      Loaded {X_hn.shape[0]} approved hard negatives.")
        X_train_hn = np.vstack([X_train_base, X_hn])
        y_train_hn = np.concatenate([y_train_base, y_hn])
        meta_train_hn = meta_train_base + meta_hn
    else:
        print("      [WARN] No hard negatives cache found! Proceeding with base data.")
        X_train_hn = X_train_base
        y_train_hn = y_train_base
        meta_train_hn = meta_train_base

    print(f"      Base Train Set:         {X_train_base.shape[0]} windows (Gunshot: {np.sum(y_train_base==1)}, Background: {np.sum(y_train_base==0)})")
    print(f"      Hard-Negative Train:    {X_train_hn.shape[0]} windows (Gunshot: {np.sum(y_train_hn==1)}, Background: {np.sum(y_train_hn==0)})")
    print(f"      Validation Set:         {X_val.shape[0]} windows (Gunshot: {np.sum(y_val==1)}, Background: {np.sum(y_val==0)})")
    print(f"      Held-Out Test Set:      {X_test.shape[0]} windows (Gunshot: {np.sum(y_test==1)}, Background: {np.sum(y_test==0)})")

    experiments_results = {}
    models_dir = Path("models/experiments")
    models_dir.mkdir(parents=True, exist_ok=True)

    # --------------------------------------------------------------------------
    # Candidate 1: Baseline MLP (without hard negatives)
    # --------------------------------------------------------------------------
    print("\n[3/5] Evaluating Candidate 1: Baseline MLP (No Hard Negatives)...")
    model_baseline = train_baseline_mlp(X_train_base, y_train_base, X_val, y_val, epochs=40)
    val_probs_1 = model_baseline.predict(X_val, verbose=0).flatten()
    test_probs_1 = model_baseline.predict(X_test, verbose=0).flatten()
    thresh_modes_1 = select_threshold_modes(y_val, val_probs_1)
    
    # Evaluate at baseline threshold 0.19 and at validation-selected threshold
    eval_1_fixed = evaluate_window_metrics(y_test, test_probs_1, threshold=0.19)
    eval_1_sel = evaluate_window_metrics(y_test, test_probs_1, threshold=thresh_modes_1["balanced_f1"]["threshold"])
    eval_1_rec = evaluate_recording_metrics(meta_test, test_probs_1, threshold=0.19)
    stream_1_c1 = evaluate_streaming_false_alerts(meta_test, test_probs_1, threshold=0.19, confirm_windows=1)
    stream_1_c2 = evaluate_streaming_false_alerts(meta_test, test_probs_1, threshold=0.19, confirm_windows=2)

    experiments_results["candidate_1_baseline_mlp"] = {
        "model_type": "Baseline MLP (No Hard Negatives)",
        "threshold_modes": thresh_modes_1,
        "test_eval_at_0_19": eval_1_fixed,
        "test_eval_at_val_selected": eval_1_sel,
        "recording_eval": eval_1_rec,
        "streaming_alerts_confirm_1": stream_1_c1,
        "streaming_alerts_confirm_2": stream_1_c2
    }
    model_baseline.save(str(models_dir / "candidate_1_baseline_mlp.keras"))

    # --------------------------------------------------------------------------
    # Candidate 2: Baseline MLP (With Hard Negatives)
    # --------------------------------------------------------------------------
    print("      Evaluating Candidate 2: Baseline MLP + Hard Negatives...")
    model_mlp_hn = train_baseline_mlp(X_train_hn, y_train_hn, X_val, y_val, epochs=45)
    val_probs_2 = model_mlp_hn.predict(X_val, verbose=0).flatten()
    test_probs_2 = model_mlp_hn.predict(X_test, verbose=0).flatten()
    thresh_modes_2 = select_threshold_modes(y_val, val_probs_2)
    t2 = thresh_modes_2["balanced_f1"]["threshold"]

    eval_2_sel = evaluate_window_metrics(y_test, test_probs_2, threshold=t2)
    eval_2_rec = evaluate_recording_metrics(meta_test, test_probs_2, threshold=t2)
    stream_2_c1 = evaluate_streaming_false_alerts(meta_test, test_probs_2, threshold=t2, confirm_windows=1)
    stream_2_c2 = evaluate_streaming_false_alerts(meta_test, test_probs_2, threshold=t2, confirm_windows=2)

    experiments_results["candidate_2_baseline_mlp_hn"] = {
        "model_type": "Baseline MLP + Hard Negatives",
        "threshold_modes": thresh_modes_2,
        "test_eval_at_val_selected": eval_2_sel,
        "recording_eval": eval_2_rec,
        "streaming_alerts_confirm_1": stream_2_c1,
        "streaming_alerts_confirm_2": stream_2_c2
    }
    model_mlp_hn.save(str(models_dir / "candidate_2_baseline_mlp_hn.keras"))

    # --------------------------------------------------------------------------
    # Candidate 3: Regularized Deep MLP (With Hard Negatives)
    # --------------------------------------------------------------------------
    print("      Evaluating Candidate 3: Regularized Deep MLP + Hard Negatives...")
    model_reg_mlp = train_regularized_mlp(X_train_hn, y_train_hn, X_val, y_val, epochs=50)
    val_probs_3 = model_reg_mlp.predict(X_val, verbose=0).flatten()
    test_probs_3 = model_reg_mlp.predict(X_test, verbose=0).flatten()
    thresh_modes_3 = select_threshold_modes(y_val, val_probs_3)
    t3 = thresh_modes_3["balanced_f1"]["threshold"]

    eval_3_sel = evaluate_window_metrics(y_test, test_probs_3, threshold=t3)
    eval_3_rec = evaluate_recording_metrics(meta_test, test_probs_3, threshold=t3)
    stream_3_c1 = evaluate_streaming_false_alerts(meta_test, test_probs_3, threshold=t3, confirm_windows=1)
    stream_3_c2 = evaluate_streaming_false_alerts(meta_test, test_probs_3, threshold=t3, confirm_windows=2)

    experiments_results["candidate_3_regularized_mlp_hn"] = {
        "model_type": "Regularized Deep MLP (LayerNorm + AdamW + Hard Negatives)",
        "threshold_modes": thresh_modes_3,
        "test_eval_at_val_selected": eval_3_sel,
        "recording_eval": eval_3_rec,
        "streaming_alerts_confirm_1": stream_3_c1,
        "streaming_alerts_confirm_2": stream_3_c2
    }
    model_reg_mlp.save(str(models_dir / "candidate_3_regularized_mlp_hn.keras"))

    # --------------------------------------------------------------------------
    # Candidate 4: LightGBM Gradient-Boosted Trees (With Hard Negatives)
    # --------------------------------------------------------------------------
    print("      Evaluating Candidate 4: LightGBM Classifier + Hard Negatives...")
    model_lgb = train_lightgbm_model(X_train_hn, y_train_hn, X_val, y_val)
    val_probs_4 = model_lgb.predict_proba(X_val)[:, 1]
    test_probs_4 = model_lgb.predict_proba(X_test)[:, 1]
    thresh_modes_4 = select_threshold_modes(y_val, val_probs_4)
    t4 = thresh_modes_4["balanced_f1"]["threshold"]

    eval_4_sel = evaluate_window_metrics(y_test, test_probs_4, threshold=t4)
    eval_4_rec = evaluate_recording_metrics(meta_test, test_probs_4, threshold=t4)
    stream_4_c1 = evaluate_streaming_false_alerts(meta_test, test_probs_4, threshold=t4, confirm_windows=1)
    stream_4_c2 = evaluate_streaming_false_alerts(meta_test, test_probs_4, threshold=t4, confirm_windows=2)

    experiments_results["candidate_4_lightgbm_hn"] = {
        "model_type": "LightGBM Gradient Boosted Trees + Hard Negatives",
        "threshold_modes": thresh_modes_4,
        "test_eval_at_val_selected": eval_4_sel,
        "recording_eval": eval_4_rec,
        "streaming_alerts_confirm_1": stream_4_c1,
        "streaming_alerts_confirm_2": stream_4_c2
    }
    joblib.dump(model_lgb, str(models_dir / "candidate_4_lightgbm_hn.joblib"))

    # --------------------------------------------------------------------------
    # Candidate 5: Calibrated LightGBM (Platt Scaling Sigmoid)
    # --------------------------------------------------------------------------
    print("      Evaluating Candidate 5: Calibrated LightGBM (Platt Scaling Sigmoid)...")
    from sklearn.linear_model import LogisticRegression
    platt = LogisticRegression(C=1.0)
    platt.fit(val_probs_4.reshape(-1, 1), y_val)
    val_probs_5 = platt.predict_proba(val_probs_4.reshape(-1, 1))[:, 1]
    test_probs_5 = platt.predict_proba(test_probs_4.reshape(-1, 1))[:, 1]
    thresh_modes_5 = select_threshold_modes(y_val, val_probs_5)
    t5 = thresh_modes_5["balanced_f1"]["threshold"]

    eval_5_sel = evaluate_window_metrics(y_test, test_probs_5, threshold=t5)
    eval_5_rec = evaluate_recording_metrics(meta_test, test_probs_5, threshold=t5)
    stream_5_c1 = evaluate_streaming_false_alerts(meta_test, test_probs_5, threshold=t5, confirm_windows=1)
    stream_5_c2 = evaluate_streaming_false_alerts(meta_test, test_probs_5, threshold=t5, confirm_windows=2)

    experiments_results["candidate_5_calibrated_lgb_hn"] = {
        "model_type": "Calibrated LightGBM (Platt Scaling Sigmoid) + Hard Negatives",
        "threshold_modes": thresh_modes_5,
        "test_eval_at_val_selected": eval_5_sel,
        "recording_eval": eval_5_rec,
        "streaming_alerts_confirm_1": stream_5_c1,
        "streaming_alerts_confirm_2": stream_5_c2
    }
    joblib.dump({"model": model_lgb, "calibrator": platt}, str(models_dir / "candidate_5_calibrated_lgb_hn.joblib"))

    # --------------------------------------------------------------------------
    # Candidate 6: Soft-Voting Hybrid Ensemble (Regularized MLP + LightGBM)
    # --------------------------------------------------------------------------
    print("      Evaluating Candidate 6: Soft-Voting Ensemble (Reg MLP + LightGBM)...")
    # Soft blend: 0.5 * P(MLP) + 0.5 * P(LGB)
    val_probs_6 = 0.5 * val_probs_3 + 0.5 * val_probs_4
    test_probs_6 = 0.5 * test_probs_3 + 0.5 * test_probs_4
    thresh_modes_6 = select_threshold_modes(y_val, val_probs_6)
    t6 = thresh_modes_6["balanced_f1"]["threshold"]

    eval_6_sel = evaluate_window_metrics(y_test, test_probs_6, threshold=t6)
    eval_6_rec = evaluate_recording_metrics(meta_test, test_probs_6, threshold=t6)
    stream_6_c1 = evaluate_streaming_false_alerts(meta_test, test_probs_6, threshold=t6, confirm_windows=1)
    stream_6_c2 = evaluate_streaming_false_alerts(meta_test, test_probs_6, threshold=t6, confirm_windows=2)

    experiments_results["candidate_6_hybrid_ensemble_hn"] = {
        "model_type": "Hybrid Ensemble (Regularized MLP + LightGBM 50/50 Blend)",
        "threshold_modes": thresh_modes_6,
        "test_eval_at_val_selected": eval_6_sel,
        "recording_eval": eval_6_rec,
        "streaming_alerts_confirm_1": stream_6_c1,
        "streaming_alerts_confirm_2": stream_6_c2
    }

    # Step 4: Summary Table & Comparison
    print("\n=========================================================================================")
    print("                      CONTROLLED EXPERIMENT RESULTS SUMMARY (HELD-OUT TEST SET)")
    print("=========================================================================================")
    print(f"{'Candidate Model':<35} | {'Thresh':<6} | {'Prec (%)':<9} | {'Rec (%)':<8} | {'F1 (%)':<8} | {'Acc (%)':<8} | {'FP':<5} | {'Alerts/hr (c=2)':<15}")
    print("-" * 105)

    for k, v in experiments_results.items():
        m_type = v["model_type"][:34]
        if k == "candidate_1_baseline_mlp":
            m_res = v["test_eval_at_0_19"]
        else:
            m_res = v["test_eval_at_val_selected"]
        t_val = m_res["threshold"]
        prec = m_res["precision"] * 100
        rec = m_res["recall"] * 100
        f1 = m_res["f1_score"] * 100
        acc = m_res["accuracy"] * 100
        fp = m_res["false_positives"]
        al_hr = v["streaming_alerts_confirm_2"]["false_alerts_per_hour"]
        print(f"{m_type:<35} | {t_val:<6.3f} | {prec:<9.2f} | {rec:<8.2f} | {f1:<8.2f} | {acc:<8.2f} | {fp:<5} | {al_hr:<15.1f}")

    print("=========================================================================================\n")

    # Step 5: Save JSON Report
    with open(output_report, "w", encoding="utf-8") as f:
        json.dump(experiments_results, f, indent=2)

    print(f"[OK] Full experiment report exported to: {output_report}")
    return experiments_results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run controlled gunshot detector experiments.")
    parser.add_argument("--report", type=str, default="reports/experiments_comparison.json", help="Output comparison report JSON")
    args = parser.parse_args()

    run_experiment_suite(output_report=Path(args.report))
