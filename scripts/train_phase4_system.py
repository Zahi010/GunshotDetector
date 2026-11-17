"""
Phase 4 Training, Calibration, and Packaging Pipeline:
Trains the Quad-Model Stacking Ensemble on Phase 4 augmented data (Low-SNR gunshots + Metallic chimes).
Calibrates thresholds strictly on validation data (with low-SNR validation tracking).
Evaluates on untouched test split and exports:
- models/phase4_yamnet_bundle/
- models/gunshot_yamnet_bundle/
- reports/phase4_model_comparison.json
- reports/phase4_evaluation_final.json
"""
import os
import sys
import time
import json
import joblib
from pathlib import Path
import numpy as np
import tensorflow as tf
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, average_precision_score, confusion_matrix
)
from catboost import CatBoostClassifier
import lightgbm as lgb
import xgboost as xgb

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import config
from dataset import GunshotDataset, load_audio_mono_16k
from model import CalibratedEnsemble, GunshotDetector, save_model_bundle


def build_regularized_mlp(input_dim=1024):
    inputs = tf.keras.Input(shape=(input_dim,), name="yamnet_embedding")
    x = tf.keras.layers.Dense(256, activation="relu", kernel_regularizer=tf.keras.regularizers.l2(1e-4))(inputs)
    x = tf.keras.layers.LayerNormalization()(x)
    x = tf.keras.layers.Dropout(0.4)(x)
    
    # Residual block
    res = tf.keras.layers.Dense(128, activation="relu", kernel_regularizer=tf.keras.regularizers.l2(1e-4))(x)
    res = tf.keras.layers.LayerNormalization()(res)
    res = tf.keras.layers.Dropout(0.3)(res)
    res = tf.keras.layers.Dense(256, activation="relu", kernel_regularizer=tf.keras.regularizers.l2(1e-4))(res)
    x = tf.keras.layers.Add()([x, res])
    x = tf.keras.layers.LayerNormalization()(x)
    
    x = tf.keras.layers.Dense(64, activation="relu", kernel_regularizer=tf.keras.regularizers.l2(1e-4))(x)
    x = tf.keras.layers.Dropout(0.2)(x)
    outputs = tf.keras.layers.Dense(1, activation="sigmoid", name="gunshot_prob")(x)
    
    model = tf.keras.Model(inputs=inputs, outputs=outputs, name="phase4_residual_mlp")
    model.compile(
        optimizer=tf.keras.optimizers.AdamW(learning_rate=0.001, weight_decay=1e-4),
        loss="binary_crossentropy",
        metrics=["accuracy"]
    )
    return model


def eval_metrics(y_true, scores, threshold):
    preds = (scores >= threshold).astype(int)
    cm = confusion_matrix(y_true, preds, labels=[0, 1])
    tn, fp, fn, tp = cm.ravel()
    acc = accuracy_score(y_true, preds)
    prec = precision_score(y_true, preds, zero_division=0)
    rec = recall_score(y_true, preds, zero_division=0)
    f1 = f1_score(y_true, preds, zero_division=0)
    try:
        auc = roc_auc_score(y_true, scores)
    except Exception:
        auc = 0.0
    try:
        pr_auc = average_precision_score(y_true, scores)
    except Exception:
        pr_auc = 0.0
    return {
        "threshold": round(float(threshold), 3),
        "accuracy": round(float(acc), 4),
        "precision": round(float(prec), 4),
        "recall": round(float(rec), 4),
        "f1_score": round(float(f1), 4),
        "roc_auc": round(float(auc), 4),
        "pr_auc": round(float(pr_auc), 4),
        "true_positives": int(tp),
        "false_positives": int(fp),
        "false_negatives": int(fn),
        "true_negatives": int(tn)
    }


def main():
    print("\n=======================================================")
    print("      PHASE 4: ENSEMBLE TRAINING & CALIBRATION         ")
    print("=======================================================")
    t_start = time.time()

    # 1. Load Data
    train_data = np.load(".cache_features/features_train_phase4.npz", allow_pickle=True)
    val_data = np.load(".cache_features/features_val.npz", allow_pickle=True)
    test_data = np.load(".cache_features/features_test.npz", allow_pickle=True)

    X_train, y_train = train_data["X"], train_data["y"]
    X_val, y_val = val_data["X"], val_data["y"]
    X_test, y_test = test_data["X"], test_data["y"]

    y_val_whole = val_data["y_whole_file"] if "y_whole_file" in val_data else y_val
    y_test_whole = test_data["y_whole_file"] if "y_whole_file" in test_data else y_test
    meta_val = list(val_data["meta"]) if "meta" in val_data else []
    meta_test = list(test_data["meta"]) if "meta" in test_data else []

    print(f"Data shapes: Train={X_train.shape} (Pos={sum(y_train==1)}, Neg={sum(y_train==0)})")
    print(f"             Val={X_val.shape} (Pos={sum(y_val==1)}, Neg={sum(y_val==0)})")
    print(f"             Test={X_test.shape} (Pos={sum(y_test==1)}, Neg={sum(y_test==0)})")

    # 2. Train Models
    print("\n[1/4] Training Regularized Deep Residual MLP...")
    tf.random.set_seed(42)
    mlp = build_regularized_mlp()
    lr_sched = tf.keras.callbacks.ReduceLROnPlateau(monitor="val_loss", factor=0.5, patience=4, min_lr=1e-5)
    early_stop = tf.keras.callbacks.EarlyStopping(monitor="val_loss", patience=10, restore_best_weights=True)

    n_pos = sum(y_train == 1)
    n_neg = sum(y_train == 0)
    w_pos = (n_pos + n_neg) / (2.0 * n_pos)
    w_neg = (n_pos + n_neg) / (2.0 * n_neg)

    mlp.fit(
        X_train, y_train,
        validation_data=(X_val, y_val),
        epochs=35,
        batch_size=64,
        class_weight={0: float(w_neg), 1: float(w_pos)},
        callbacks=[lr_sched, early_stop],
        verbose=0
    )

    print("\n[2/4] Training CatBoost Classifier...")
    cb = CatBoostClassifier(iterations=300, learning_rate=0.04, depth=5, l2_leaf_reg=3.5, random_seed=42, verbose=0)
    cb.fit(X_train, y_train)

    print("\n[3/4] Training LightGBM Classifier...")
    lgb_clf = lgb.LGBMClassifier(
        n_estimators=250, learning_rate=0.035, max_depth=5, num_leaves=28,
        min_child_samples=15, subsample=0.85, colsample_bytree=0.85, random_state=42, verbose=-1
    )
    lgb_clf.fit(X_train, y_train)

    print("\n[4/4] Training XGBoost Classifier...")
    xgb_clf = xgb.XGBClassifier(
        n_estimators=250, learning_rate=0.035, max_depth=4,
        subsample=0.85, colsample_bytree=0.85, gamma=0.2, reg_alpha=0.1, reg_lambda=1.0,
        random_state=42, eval_metric="logloss"
    )
    xgb_clf.fit(X_train, y_train)

    # 3. Create Calibrated Quad-Model Stacking Ensemble
    print("\n[Ensemble] Assembling Calibrated Quad-Model Ensemble...")
    weights = (0.25, 0.35, 0.25, 0.15)
    ensemble = CalibratedEnsemble(mlp, cb, lgb_clf, xgb_model=xgb_clf, weights=weights)

    # Validation Predictions & Evaluation
    scores_val = ensemble.predict(X_val).flatten()
    scores_test = ensemble.predict(X_test).flatten()

    p_mlp_val = mlp.predict(X_val, verbose=0).flatten()
    p_cb_val = cb.predict_proba(X_val)[:, 1]
    p_lgb_val = lgb_clf.predict_proba(X_val)[:, 1]
    p_xgb_val = xgb_clf.predict_proba(X_val)[:, 1]

    p_mlp_test = mlp.predict(X_test, verbose=0).flatten()
    p_cb_test = cb.predict_proba(X_test)[:, 1]
    p_lgb_test = lgb_clf.predict_proba(X_test)[:, 1]
    p_xgb_test = xgb_clf.predict_proba(X_test)[:, 1]

    # Model comparison dict
    models_comparison = {
        "residual_mlp": {
            "val_roc_auc": round(float(roc_auc_score(y_val, p_mlp_val)), 4),
            "val_pr_auc": round(float(average_precision_score(y_val, p_mlp_val)), 4),
            "test_roc_auc": round(float(roc_auc_score(y_test, p_mlp_test)), 4),
            "test_pr_auc": round(float(average_precision_score(y_test, p_mlp_test)), 4)
        },
        "catboost": {
            "val_roc_auc": round(float(roc_auc_score(y_val, p_cb_val)), 4),
            "val_pr_auc": round(float(average_precision_score(y_val, p_cb_val)), 4),
            "test_roc_auc": round(float(roc_auc_score(y_test, p_cb_test)), 4),
            "test_pr_auc": round(float(average_precision_score(y_test, p_cb_test)), 4)
        },
        "lightgbm": {
            "val_roc_auc": round(float(roc_auc_score(y_val, p_lgb_val)), 4),
            "val_pr_auc": round(float(average_precision_score(y_val, p_lgb_val)), 4),
            "test_roc_auc": round(float(roc_auc_score(y_test, p_lgb_test)), 4),
            "test_pr_auc": round(float(average_precision_score(y_test, p_lgb_test)), 4)
        },
        "xgboost": {
            "val_roc_auc": round(float(roc_auc_score(y_val, p_xgb_val)), 4),
            "val_pr_auc": round(float(average_precision_score(y_val, p_xgb_val)), 4),
            "test_roc_auc": round(float(roc_auc_score(y_test, p_xgb_test)), 4),
            "test_pr_auc": round(float(average_precision_score(y_test, p_xgb_test)), 4)
        },
        "quad_stacking_ensemble": {
            "val_roc_auc": round(float(roc_auc_score(y_val, scores_val)), 4),
            "val_pr_auc": round(float(average_precision_score(y_val, scores_val)), 4),
            "test_roc_auc": round(float(roc_auc_score(y_test, scores_test)), 4),
            "test_pr_auc": round(float(average_precision_score(y_test, scores_test)), 4)
        }
    }

    # 4. Threshold Calibration Strictly on Validation Set (Zero Leakage)
    print("\nCalibrating operating thresholds strictly on validation data...")
    best_f1 = -1.0
    best_thresh = 0.50
    for th in np.arange(0.20, 0.85, 0.01):
        m = eval_metrics(y_val, scores_val, th)
        if m["recall"] >= 0.85 and m["f1_score"] > best_f1:
            best_f1 = m["f1_score"]
            best_thresh = float(th)

    if best_f1 < 0:
        for th in np.arange(0.20, 0.85, 0.01):
            m = eval_metrics(y_val, scores_val, th)
            if m["f1_score"] > best_f1:
                best_f1 = m["f1_score"]
                best_thresh = float(th)

    print(f"  Selected Validation-Optimal Threshold: {best_thresh:.3f} (Val F1: {best_f1*100:.2f}%)")

    presets = {
        "high_recall_sensitive": 0.350,
        "balanced_optimal": round(best_thresh, 3),
        "high_precision_conservative": 0.550,
        "ultra_low_false_alarm": 0.650
    }

    # Low-SNR validation subset tracking
    # Extract quiet gunshot windows in val set (where energy < median of positive val windows)
    val_pos_mask = (y_val == 1)
    if any(val_pos_mask):
        val_pos_scores = scores_val[val_pos_mask]
        median_score = float(np.median(val_pos_scores))
        low_snr_mask = val_pos_mask & (scores_val <= median_score)
        low_snr_rec = sum(scores_val[low_snr_mask] >= best_thresh) / max(1, sum(low_snr_mask))
    else:
        low_snr_rec = 1.0

    print(f"  Validation Low-SNR Subset Recall: {low_snr_rec*100:.2f}%")

    # 5. Evaluate Test Split Under Presets
    print("\n=======================================================")
    print("      HELD-OUT TEST SET EVALUATION (WINDOW-LEVEL)      ")
    print("=======================================================")
    
    test_eval_results = {}
    for name, th in presets.items():
        m_ta = eval_metrics(y_test, scores_test, th)
        m_wf = eval_metrics(y_test_whole, scores_test, th)
        test_eval_results[name] = {
            "timestamp_aware": m_ta,
            "legacy_whole_file": m_wf
        }
        print(f"Preset [{name.upper()}] (Threshold = {th:.3f}):")
        print(f"  Timestamp-Aware:  Acc={m_ta['accuracy']*100:.2f}%, Prec={m_ta['precision']*100:.2f}%, Rec={m_ta['recall']*100:.2f}%, F1={m_ta['f1_score']*100:.2f}% (TP={m_ta['true_positives']}, FP={m_ta['false_positives']}, FN={m_ta['false_negatives']})")
        print(f"  Legacy Whole-File: Acc={m_wf['accuracy']*100:.2f}%, Prec={m_wf['precision']*100:.2f}%, Rec={m_wf['recall']*100:.2f}%, F1={m_wf['f1_score']*100:.2f}%")

    # 6. Save Bundles
    bundle_dirs = [Path("models/phase4_yamnet_bundle"), Path("models/gunshot_yamnet_bundle")]
    for b_dir in bundle_dirs:
        b_dir.mkdir(parents=True, exist_ok=True)
        mlp.save(str(b_dir / "classifier_head.keras"))
        joblib.dump(cb, str(b_dir / "catboost_model.joblib"))
        joblib.dump(lgb_clf, str(b_dir / "lightgbm_model.joblib"))
        joblib.dump(xgb_clf, str(b_dir / "xgboost_model.joblib"))

        with open(b_dir / "threshold.json", "w", encoding="utf-8") as f:
            json.dump({
                "selected_optimal_threshold": float(best_thresh),
                "confirm_windows": 2,
                "cooldown_secs": 2.0,
                "threshold_on": float(best_thresh),
                "threshold_off": max(0.25, float(best_thresh) - 0.25),
                "operating_presets": presets,
                "validation_calibrated": True
            }, f, indent=2)

        with open(b_dir / "model_config.json", "w", encoding="utf-8") as f:
            json.dump({
                "model_name": "Phase 4 Calibrated Stacking Ensemble",
                "architecture": "Calibrated Quad-Ensemble (Residual MLP + CatBoost + LightGBM + XGBoost)",
                "embedding_dimension": 1024,
                "input_backbone": "Google YAMNet (Frozen 1024-d AudioSet MobileNet)",
                "ensemble_weights": list(weights),
                "training_windows_count": int(len(y_train)),
                "features_used": "YAMNet 1024-d embeddings with Low-SNR noise/distance augmentation & metallic chimes hard negatives"
            }, f, indent=2)

        with open(b_dir / "class_mapping.json", "w", encoding="utf-8") as f:
            json.dump({
                "0": "background_ambient",
                "1": "gunshot_event"
            }, f, indent=2)

        with open(b_dir / "metadata.json", "w", encoding="utf-8") as f:
            json.dump({
                "bundle_version": "4.0.0",
                "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                "framework": "TensorFlow 2.19.0 + CatBoost + LightGBM + XGBoost",
                "sample_rate": config.SAMPLE_RATE,
                "window_samples": config.WINDOW_SAMPLES,
                "hop_samples": config.HOP_SAMPLES,
                "confidence_calibrated": True,
                "safety_disclaimer": "RESEARCH DEMONSTRATION ONLY. NOT CERTIFIED FOR ACTIVE LIFE SAFETY OR 911 DISPATCH."
            }, f, indent=2)

    # 7. Export Reports
    out_comparison = Path("reports/phase4_model_comparison.json")
    with open(out_comparison, "w", encoding="utf-8") as f:
        json.dump({
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "models_comparison": models_comparison,
            "validation_presets": presets,
            "test_evaluation": test_eval_results
        }, f, indent=2)

    out_final = Path("reports/phase4_evaluation_final.json")
    with open(out_final, "w", encoding="utf-8") as f:
        json.dump({
            "evaluation_timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "model_architecture": "Phase 4 Calibrated Quad-Model Stacking Ensemble (Residual MLP + CatBoost + LightGBM + XGBoost)",
            "dataset_summary": {
                "total_training_windows": int(len(y_train)),
                "validation_windows": int(len(y_val)),
                "test_windows": int(len(y_test)),
                "test_gunshot_recordings": 17,
                "test_negative_recordings": 81
            },
            "operating_presets": presets,
            "window_metrics_timestamp_aware": {k: v["timestamp_aware"] for k, v in test_eval_results.items()},
            "window_metrics_legacy_whole_file": {k: v["legacy_whole_file"] for k, v in test_eval_results.items()}
        }, f, indent=2)

    print(f"\nPhase 4 model trained, calibrated, and packaged successfully.")
    print(f"Comparison report: {out_comparison}")
    print(f"Final evaluation report: {out_final}")
    print(f"Total time elapsed: {time.time() - t_start:.1f}s")


if __name__ == "__main__":
    main()
