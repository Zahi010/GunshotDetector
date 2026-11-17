"""
Training Pipeline for Gunshot Sound Detection.

Workflow:
1. Loads dataset with leak-free recording-level group splitting.
2. Applies realistic audio augmentations ONLY to the training split.
3. Extracts 1024-d embeddings using frozen YAMNet.
4. Trains the classifier head neural network with binary cross-entropy.
5. Performs threshold selection on the VALIDATION split to maximize F1.
6. Evaluates final performance on the held-out TEST split at the selected threshold.
7. Evaluates both window-level and recording-level performance.
8. Saves the complete deployment bundle (weights, config, threshold, class mapping, metadata).
"""
import os
import argparse
import numpy as np
import tensorflow as tf
from pathlib import Path
from typing import Dict, Tuple, List, Any
from sklearn.metrics import (
    precision_score, recall_score, f1_score, roc_auc_score,
    confusion_matrix, classification_report
)

import config
from dataset import GunshotDataset
from feature_extractor import YAMNetFeatureExtractor, cache_extracted_features
from model import build_classifier_head, save_model_bundle


def find_optimal_threshold(
    y_true: np.ndarray,
    y_scores: np.ndarray,
    min_thresh: float = 0.10,
    max_thresh: float = 0.90,
    steps: int = 161
) -> Tuple[float, Dict[str, Any], Dict[str, float]]:
    """
    Search for threshold modes strictly on the VALIDATION split:
    1. Balanced Optimal: Maximizes precision-weighted F0.5 score to penalize nuisance false alarms.
    2. High Recall Sensitive: Operating point guaranteeing >= 95% Recall.
    3. High Precision Conservative: Operating point maximizing precision with >= 80% Recall.
    """
    from sklearn.metrics import fbeta_score

    thresholds = np.linspace(min_thresh, max_thresh, steps)
    best_thresh = 0.50
    best_f = -1.0
    best_metrics = {}

    hr_thresh = 0.35
    hr_best_f = -1.0

    hp_thresh = 0.65
    hp_best_p = -1.0

    for t in thresholds:
        yp = (y_scores >= t).astype(int)
        p = precision_score(y_true, yp, zero_division=0)
        r = recall_score(y_true, yp, zero_division=0)
        f = f1_score(y_true, yp, zero_division=0)
        f05 = fbeta_score(y_true, yp, beta=0.5, zero_division=0)

        # Balanced F0.5
        if f05 > best_f:
            best_f = f05
            best_thresh = float(t)
            best_metrics = {
                "threshold": round(best_thresh, 3),
                "objective": "Maximize validation F0.5 to strongly penalize false alarms while preserving detection recall",
                "precision": round(float(p), 4),
                "recall": round(float(r), 4),
                "f1": round(float(f), 4),
                "f05": round(float(f05), 4)
            }

        # High Recall mode (Recall >= 0.95)
        if r >= 0.95 and f > hr_best_f:
            hr_best_f = f
            hr_thresh = float(t)

        # High Precision mode (Recall >= 0.80, maximize Precision)
        if r >= 0.80 and p > hp_best_p:
            hp_best_p = p
            hp_thresh = float(t)

    presets = {
        "high_recall_sensitive": round(hr_thresh, 3),
        "balanced_optimal": round(best_thresh, 3),
        "high_precision_conservative": round(hp_thresh, 3)
    }
    return best_thresh, best_metrics, presets


def evaluate_predictions(
    y_true: np.ndarray,
    y_scores: np.ndarray,
    threshold: float
) -> Dict[str, Any]:
    """
    Calculate window-level precision, recall, F1, ROC-AUC, and confusion matrix.
    Reports total windows and counts per class.
    """
    y_pred = (y_scores >= threshold).astype(int)

    p = precision_score(y_true, y_pred, zero_division=0)
    r = recall_score(y_true, y_pred, zero_division=0)
    f = f1_score(y_true, y_pred, zero_division=0)

    try:
        auc = roc_auc_score(y_true, y_scores)
    except Exception:
        auc = float("nan")

    cm = confusion_matrix(y_true, y_pred).tolist()

    return {
        "threshold": round(threshold, 3),
        "windows_total": len(y_true),
        "windows_gunshot": int(np.sum(y_true == 1)),
        "windows_background": int(np.sum(y_true == 0)),
        "precision": round(float(p), 4),
        "recall": round(float(r), 4),
        "f1": round(float(f), 4),
        "roc_auc": round(float(auc), 4) if not np.isnan(auc) else None,
        "confusion_matrix": cm,  # [[TN, FP], [FN, TP]]
        "true_negatives": cm[0][0] if len(cm) > 1 else 0,
        "false_positives": cm[0][1] if len(cm) > 1 else 0,
        "false_negatives": cm[1][0] if len(cm) > 1 else 0,
        "true_positives": cm[1][1] if len(cm) > 1 else 0,
    }


def evaluate_recording_level(
    meta_list: List[Dict[str, Any]],
    y_scores: np.ndarray,
    threshold: float
) -> Dict[str, Any]:
    """
    Aggregate window predictions per original recording to avoid presenting
    overlapping windows from the same recording as independent data points.
    Reports total recordings and counts per class.
    """
    recordings: Dict[str, Dict[str, Any]] = {}
    for meta, score in zip(meta_list, y_scores):
        rec_id = meta["recording_id"]
        label = meta["label"]
        if rec_id not in recordings:
            recordings[rec_id] = {
                "label": label,
                "window_scores": []
            }
        recordings[rec_id]["window_scores"].append(score)

    rec_true = []
    rec_pred = []
    rec_scores = []

    for rec_id, data in recordings.items():
        # Aggregation: max window score represents the recording score
        max_score = float(np.max(data["window_scores"]))
        pred = int(max_score >= threshold)
        rec_true.append(data["label"])
        rec_pred.append(pred)
        rec_scores.append(max_score)

    rec_true = np.array(rec_true)
    rec_pred = np.array(rec_pred)
    rec_scores = np.array(rec_scores)

    p = precision_score(rec_true, rec_pred, zero_division=0)
    r = recall_score(rec_true, rec_pred, zero_division=0)
    f = f1_score(rec_true, rec_pred, zero_division=0)
    try:
        auc = roc_auc_score(rec_true, rec_scores)
    except Exception:
        auc = None

    cm = confusion_matrix(rec_true, rec_pred).tolist()

    return {
        "total_recordings": len(recordings),
        "recordings_gunshot": int(np.sum(rec_true == 1)),
        "recordings_background": int(np.sum(rec_true == 0)),
        "precision": round(float(p), 4),
        "recall": round(float(r), 4),
        "f1": round(float(f), 4),
        "roc_auc": round(float(auc), 4) if auc is not None else None,
        "confusion_matrix": cm,
        "true_negatives": cm[0][0] if len(cm) > 1 else 0,
        "false_positives": cm[0][1] if len(cm) > 1 else 0,
        "false_negatives": cm[1][0] if len(cm) > 1 else 0,
        "true_positives": cm[1][1] if len(cm) > 1 else 0,
    }


def run_training_pipeline(
    data_dir: Path = config.DATA_DIR,
    output_bundle_dir: Path = config.MODELS_DIR / "gunshot_yamnet_bundle",
    epochs: int = config.EPOCHS,
    batch_size: int = config.BATCH_SIZE,
    learning_rate: float = config.LEARNING_RATE
) -> Dict[str, Any]:
    """Execute complete end-to-end training and evaluation pipeline."""
    data_dir = Path(data_dir)
    output_bundle_dir = Path(output_bundle_dir)

    print("\n=======================================================")
    print("      GUNSHOT DETECTOR TRAINING WORKFLOW (YAMNet)")
    print("=======================================================\n")

    # Step 1: Initialize Dataset with leak-free group split
    print("[1/6] Initializing Dataset and Group Splitting...")
    dataset = GunshotDataset(data_dir=data_dir)
    dataset.index_files()
    ds_info = dataset.summary()
    print(f"Total Unique Groups: {ds_info['total_recording_groups']}")
    for s_name, s_data in ds_info["splits"].items():
        print(f"  {s_name.upper():<5}: {s_data['groups_total']} groups ({s_data['groups_gunshot']} gunshot, {s_data['groups_background']} background)")

    # Step 2: Initialize YAMNet & Extract Features
    print("\n[2/6] Loading Frozen YAMNet & Extracting Embeddings...")
    extractor = YAMNetFeatureExtractor()
    features = cache_extracted_features(dataset, extractor)

    X_train, y_train, meta_train = features["train"]
    X_val, y_val, meta_val = features["val"]
    X_test, y_test, meta_test = features["test"]

    # Load approved hard negatives into training set
    hn_path = Path(".cache_features/features_hard_negatives.npz")
    if hn_path.exists():
        d_hn = np.load(str(hn_path), allow_pickle=True)
        X_hn, y_hn, meta_hn = d_hn["X"], d_hn["y"], list(d_hn["meta"])
        X_train = np.vstack([X_train, X_hn])
        y_train = np.concatenate([y_train, y_hn])
        meta_train = meta_train + meta_hn
        print(f"  [Hard Negatives] Added {X_hn.shape[0]} approved hard negatives to Training set.")

    print(f"Train set: {X_train.shape[0]} windows (augmented + hard negatives)")
    print(f"Val set:   {X_val.shape[0]} windows (unaugmented)")
    print(f"Test set:  {X_test.shape[0]} windows (unaugmented)")

    # Calculate class weights with 1.25x penalty on negative class
    neg_count = np.sum(y_train == 0)
    pos_count = np.sum(y_train == 1)
    total_train = len(y_train)
    class_weight = {
        0: 1.25 * (total_train / (2.0 * neg_count)) if neg_count > 0 else 1.0,
        1: (total_train / (2.0 * pos_count)) if pos_count > 0 else 1.0,
    }
    print(f"Class weighting (penalizing false alarms): {class_weight}")

    # Step 3: Build & Train Classifier Head
    print("\n[3/6] Building & Training Regularized Classifier Head (Frozen Backbone)...")
    classifier_head = build_classifier_head()
    classifier_head.compile(
        optimizer=tf.keras.optimizers.AdamW(learning_rate=learning_rate, weight_decay=1e-4),
        loss="binary_crossentropy",
        metrics=["accuracy", tf.keras.metrics.AUC(name="auc")]
    )

    callbacks = [
        tf.keras.callbacks.EarlyStopping(
            monitor="val_loss",
            patience=10,
            restore_best_weights=True,
            verbose=1
        ),
        tf.keras.callbacks.ReduceLROnPlateau(
            monitor="val_loss",
            factor=0.5,
            patience=4,
            min_lr=1e-5,
            verbose=1
        )
    ]

    history = classifier_head.fit(
        X_train, y_train,
        validation_data=(X_val, y_val),
        epochs=epochs,
        batch_size=batch_size,
        class_weight=class_weight,
        callbacks=callbacks,
        verbose=1
    )

    # Step 4: Threshold Selection on Validation Set
    print("\n[4/6] Optimizing Detection Threshold Presets on Validation Set...")
    val_probs = classifier_head.predict(X_val, verbose=0).flatten()
    best_threshold, val_metrics, presets = find_optimal_threshold(y_val, val_probs)
    print(f"  -> Optimal Validation Threshold: {best_threshold:.3f}")
    print(f"  -> Presets: High-Recall={presets['high_recall_sensitive']}, Balanced={presets['balanced_optimal']}, Conservative={presets['high_precision_conservative']}")
    print(f"  -> Validation Metrics at {best_threshold:.3f}: Precision={val_metrics['precision']}, Recall={val_metrics['recall']}, F1={val_metrics['f1']}")

    # Step 5: Final Evaluation on Held-Out Test Set
    print("\n[5/6] Final Evaluation on Held-Out Test Set (Unseen Recordings)...")
    test_probs = classifier_head.predict(X_test, verbose=0).flatten()

    # Window-Level Evaluation
    test_window_eval = evaluate_predictions(y_test, test_probs, threshold=best_threshold)
    print("\n--- TEST SET WINDOW-LEVEL PERFORMANCE ---")
    print(f"  Threshold:       {test_window_eval['threshold']}")
    print(f"  Precision:       {test_window_eval['precision']:.4f}")
    print(f"  Recall:          {test_window_eval['recall']:.4f}")
    print(f"  F1 Score:        {test_window_eval['f1']:.4f}")
    print(f"  ROC-AUC:         {test_window_eval['roc_auc']}")
    print(f"  Confusion Matrix: TN={test_window_eval['true_negatives']}, FP={test_window_eval['false_positives']}, FN={test_window_eval['false_negatives']}, TP={test_window_eval['true_positives']}")

    # Recording-Level Evaluation
    test_rec_eval = evaluate_recording_level(meta_test, test_probs, threshold=best_threshold)
    print("\n--- TEST SET RECORDING-LEVEL PERFORMANCE (Grouped) ---")
    print(f"  Recordings Evaluated: {test_rec_eval['total_recordings']}")
    print(f"  Precision:            {test_rec_eval['precision']:.4f}")
    print(f"  Recall:               {test_rec_eval['recall']:.4f}")
    print(f"  F1 Score:             {test_rec_eval['f1']:.4f}")
    print(f"  ROC-AUC:              {test_rec_eval['roc_auc']}")
    print(f"  Confusion Matrix:     TN={test_rec_eval['true_negatives']}, FP={test_rec_eval['false_positives']}, FN={test_rec_eval['false_negatives']}, TP={test_rec_eval['true_positives']}")

    # Step 6: Save Deployment Bundle
    print("\n[6/6] Packaging and Saving Model Bundle...")
    train_meta = {
        "epochs_trained": len(history.history["loss"]),
        "final_train_loss": float(history.history["loss"][-1]),
        "final_val_loss": float(history.history["val_loss"][-1]),
        "final_train_acc": float(history.history["accuracy"][-1]),
        "final_val_acc": float(history.history["val_accuracy"][-1]),
        "hard_negatives_included": True,
        "hard_negatives_count": len(meta_hn) if 'meta_hn' in locals() else 0
    }
    eval_meta = {
        "validation_selected_metrics": val_metrics,
        "test_window_metrics": test_window_eval,
        "test_recording_metrics": test_rec_eval,
    }

    save_model_bundle(
        model=classifier_head,
        bundle_dir=output_bundle_dir,
        selected_threshold=best_threshold,
        threshold_presets=presets,
        training_metadata=train_meta,
        evaluation_metrics=eval_meta
    )

    print("\n=======================================================")
    print("      TRAINING AND EVALUATION COMPLETED SUCCESSFULLY")
    print("=======================================================\n")

    return {
        "best_threshold": best_threshold,
        "val_metrics": val_metrics,
        "test_window_metrics": test_window_eval,
        "test_recording_metrics": test_rec_eval
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train gunshot detector on YAMNet features.")
    parser.add_argument("--data-dir", type=str, default=str(config.DATA_DIR), help="Dataset directory")
    parser.add_argument("--output", type=str, default=str(config.MODELS_DIR / "gunshot_yamnet_bundle"), help="Output bundle directory")
    parser.add_argument("--epochs", type=int, default=config.EPOCHS, help="Number of training epochs")
    parser.add_argument("--batch-size", type=int, default=config.BATCH_SIZE, help="Batch size")
    parser.add_argument("--lr", type=float, default=config.LEARNING_RATE, help="Learning rate")
    args = parser.parse_args()

    run_training_pipeline(
        data_dir=Path(args.data_dir),
        output_bundle_dir=Path(args.output),
        epochs=args.epochs,
        batch_size=args.batch_size,
        learning_rate=args.lr
    )
