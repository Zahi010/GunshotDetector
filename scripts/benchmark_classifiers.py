"""
Benchmark Classifiers for Phase 3:
Controlled comparison of acoustic classifiers on the exact same train/val/test splits.
Models compared:
1. Regularized Deep MLP (Residual blocks, LayerNorm, Dropout, AdamW)
2. LightGBM (Gradient-boosted decision trees)
3. XGBoost
4. CatBoost
5. Calibrated Hybrid Stacking Ensemble

Threshold calibration is performed STRICTLY on the validation split.
Window-level and recording-level metrics are computed and exported to reports/phase3_model_comparison.json.
Evaluates under both:
- Timestamp-Aware Protocol (Physical acoustic ground truth)
- Legacy Whole-File Protocol (Phase 2 backward compatibility)
"""
import sys, os, time, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import numpy as np
import tensorflow as tf
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, average_precision_score, confusion_matrix
)
import lightgbm as lgb
import xgboost as xgb
from catboost import CatBoostClassifier

def load_data():
    train_data = np.load(".cache_features/features_train.npz", allow_pickle=True)
    val_data = np.load(".cache_features/features_val.npz", allow_pickle=True)
    test_data = np.load(".cache_features/features_test.npz", allow_pickle=True)
    
    X_train, y_train = train_data["X"], train_data["y"]
    X_val, y_val = val_data["X"], val_data["y"]
    X_test, y_test = test_data["X"], test_data["y"]
    
    y_val_whole = val_data["y_whole_file"] if "y_whole_file" in val_data else y_val
    y_test_whole = test_data["y_whole_file"] if "y_whole_file" in test_data else y_test
    meta_test = list(test_data["meta"]) if "meta" in test_data else []
    
    # Add approved hard negatives strictly to train split (zero leakage)
    hn_path = Path(".cache_features/features_hard_negatives.npz")
    if hn_path.exists():
        hn_data = np.load(hn_path, allow_pickle=True)
        X_hn, y_hn = hn_data["X"], hn_data["y"]
        X_train = np.vstack([X_train, X_hn])
        y_train = np.concatenate([y_train, y_hn])
        print(f"Loaded {len(y_hn)} approved hard negatives. Total train: {len(y_train)} windows.")
        
    print(f"Split shapes: Train={X_train.shape} (pos={int(sum(y_train==1))}, neg={int(sum(y_train==0))}), Val={X_val.shape}, Test={X_test.shape}")
    return X_train, y_train, X_val, y_val, X_test, y_test, y_val_whole, y_test_whole, meta_test

def eval_predictions(y_true, scores, threshold):
    preds = (scores >= threshold).astype(int)
    cm = confusion_matrix(y_true, preds, labels=[0, 1])
    tn, fp, fn, tp = cm.ravel()
    acc = accuracy_score(y_true, preds)
    prec = precision_score(y_true, preds, zero_division=0)
    rec = recall_score(y_true, preds, zero_division=0)
    f1 = f1_score(y_true, preds, zero_division=0)
    try:
        auc = roc_auc_score(y_true, scores)
    except:
        auc = 0.0
    try:
        pr_auc = average_precision_score(y_true, scores)
    except:
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

def find_best_threshold_val(y_val, scores_val, min_recall=0.85):
    """Calibrate optimal threshold on validation predictions only."""
    best_f1 = -1.0
    best_th = 0.50
    for th in np.arange(0.10, 0.90, 0.01):
        m = eval_predictions(y_val, scores_val, th)
        if m["recall"] >= min_recall and m["f1_score"] > best_f1:
            best_f1 = m["f1_score"]
            best_th = th
    if best_f1 < 0:
        for th in np.arange(0.10, 0.90, 0.01):
            m = eval_predictions(y_val, scores_val, th)
            if m["f1_score"] > best_f1:
                best_f1 = m["f1_score"]
                best_th = th
    return round(float(best_th), 3)

def eval_recording_level(meta, scores, threshold):
    rec_scores = {}
    rec_labels = {}
    for i, m in enumerate(meta):
        rid = m.get("recording_id", f"rec_{i}")
        lbl = m.get("whole_file_label", m.get("label", 0))
        if rid not in rec_scores:
            rec_scores[rid] = []
            rec_labels[rid] = lbl
        rec_scores[rid].append(scores[i])
        
    pos_recs = [r for r, l in rec_labels.items() if l == 1]
    neg_recs = [r for r, l in rec_labels.items() if l == 0]
    
    tp_recs = sum(1 for r in pos_recs if max(rec_scores[r]) >= threshold)
    fn_recs = len(pos_recs) - tp_recs
    tn_recs = sum(1 for r in neg_recs if max(rec_scores[r]) < threshold)
    fp_recs = len(neg_recs) - tn_recs
    
    prec = tp_recs / (tp_recs + fp_recs) if (tp_recs + fp_recs) > 0 else 0.0
    rec = tp_recs / len(pos_recs) if len(pos_recs) > 0 else 0.0
    f1 = 2 * prec * rec / (prec + rec) if (prec + rec) > 0 else 0.0
    
    return {
        "threshold": round(float(threshold), 3),
        "total_recordings": len(rec_labels),
        "gunshot_recordings_total": len(pos_recs),
        "gunshot_recordings_detected": tp_recs,
        "gunshot_recording_recall": round(float(rec), 4),
        "negative_recordings_total": len(neg_recs),
        "negative_recordings_rejected": tn_recs,
        "negative_recording_rejection_rate": round(float(tn_recs) / len(neg_recs), 4) if len(neg_recs) > 0 else 0.0,
        "recording_precision": round(float(prec), 4),
        "recording_f1_score": round(float(f1), 4)
    }

def run_benchmarks():
    print("\n=======================================================")
    print("   PHASE 3: COMPREHENSIVE CLASSIFIER BENCHMARKING      ")
    print("=======================================================")
    
    X_train, y_train, X_val, y_val, X_test, y_test, y_val_whole, y_test_whole, meta_test = load_data()
    comparison_results = {}
    
    # 1. LightGBM
    print("\n[1/5] Training LightGBM Classifier...")
    t0 = time.time()
    lgb_clf = lgb.LGBMClassifier(
        n_estimators=220,
        learning_rate=0.035,
        max_depth=5,
        num_leaves=28,
        min_child_samples=15,
        subsample=0.85,
        colsample_bytree=0.85,
        scale_pos_weight=1.0,
        random_state=42,
        verbose=-1
    )
    lgb_clf.fit(X_train, y_train)
    val_lgb = lgb_clf.predict_proba(X_val)[:, 1]
    test_lgb = lgb_clf.predict_proba(X_test)[:, 1]
    train_time_lgb = round(time.time() - t0, 2)
    th_lgb = find_best_threshold_val(y_val, val_lgb)
    
    m_val_lgb = eval_predictions(y_val, val_lgb, th_lgb)
    m_test_lgb = eval_predictions(y_test, test_lgb, th_lgb)
    m_test_lgb_whole = eval_predictions(y_test_whole, test_lgb, th_lgb)
    rec_lgb = eval_recording_level(meta_test, test_lgb, th_lgb)
    
    print(f"  LightGBM (Val Thresh {th_lgb:.3f}):")
    print(f"    Val:               Acc={m_val_lgb['accuracy']:.4f}, Prec={m_val_lgb['precision']:.4f}, Rec={m_val_lgb['recall']:.4f}, F1={m_val_lgb['f1_score']:.4f}, AUC={m_val_lgb['roc_auc']:.4f}")
    print(f"    Test (Timestamp):  Acc={m_test_lgb['accuracy']:.4f}, Prec={m_test_lgb['precision']:.4f}, Rec={m_test_lgb['recall']:.4f}, F1={m_test_lgb['f1_score']:.4f}, AUC={m_test_lgb['roc_auc']:.4f}, FP={m_test_lgb['false_positives']}, FN={m_test_lgb['false_negatives']}")
    print(f"    Test (Whole-File): Acc={m_test_lgb_whole['accuracy']:.4f}, Prec={m_test_lgb_whole['precision']:.4f}, Rec={m_test_lgb_whole['recall']:.4f}, F1={m_test_lgb_whole['f1_score']:.4f}")
    
    comparison_results["LightGBM"] = {
        "model_family": "Gradient Boosted Trees (LightGBM)",
        "train_time_sec": train_time_lgb,
        "selected_threshold": th_lgb,
        "val_metrics": m_val_lgb,
        "test_metrics_timestamp_aware": m_test_lgb,
        "test_metrics_legacy_whole_file": m_test_lgb_whole,
        "recording_level_metrics": rec_lgb
    }
    
    # 2. XGBoost
    print("\n[2/5] Training XGBoost Classifier...")
    t0 = time.time()
    xgb_clf = xgb.XGBClassifier(
        n_estimators=220,
        learning_rate=0.035,
        max_depth=4,
        subsample=0.85,
        colsample_bytree=0.85,
        gamma=0.2,
        reg_alpha=0.1,
        reg_lambda=1.0,
        random_state=42,
        eval_metric="logloss"
    )
    xgb_clf.fit(X_train, y_train)
    val_xgb = xgb_clf.predict_proba(X_val)[:, 1]
    test_xgb = xgb_clf.predict_proba(X_test)[:, 1]
    train_time_xgb = round(time.time() - t0, 2)
    th_xgb = find_best_threshold_val(y_val, val_xgb)
    
    m_val_xgb = eval_predictions(y_val, val_xgb, th_xgb)
    m_test_xgb = eval_predictions(y_test, test_xgb, th_xgb)
    m_test_xgb_whole = eval_predictions(y_test_whole, test_xgb, th_xgb)
    rec_xgb = eval_recording_level(meta_test, test_xgb, th_xgb)
    
    print(f"  XGBoost (Val Thresh {th_xgb:.3f}):")
    print(f"    Val:               Acc={m_val_xgb['accuracy']:.4f}, Prec={m_val_xgb['precision']:.4f}, Rec={m_val_xgb['recall']:.4f}, F1={m_val_xgb['f1_score']:.4f}, AUC={m_val_xgb['roc_auc']:.4f}")
    print(f"    Test (Timestamp):  Acc={m_test_xgb['accuracy']:.4f}, Prec={m_test_xgb['precision']:.4f}, Rec={m_test_xgb['recall']:.4f}, F1={m_test_xgb['f1_score']:.4f}, AUC={m_test_xgb['roc_auc']:.4f}, FP={m_test_xgb['false_positives']}, FN={m_test_xgb['false_negatives']}")
    
    comparison_results["XGBoost"] = {
        "model_family": "Gradient Boosted Trees (XGBoost)",
        "train_time_sec": train_time_xgb,
        "selected_threshold": th_xgb,
        "val_metrics": m_val_xgb,
        "test_metrics_timestamp_aware": m_test_xgb,
        "test_metrics_legacy_whole_file": m_test_xgb_whole,
        "recording_level_metrics": rec_xgb
    }

    # 3. CatBoost
    print("\n[3/5] Training CatBoost Classifier...")
    t0 = time.time()
    cb_clf = CatBoostClassifier(
        iterations=250,
        learning_rate=0.04,
        depth=5,
        l2_leaf_reg=3.5,
        random_seed=42,
        verbose=0
    )
    cb_clf.fit(X_train, y_train)
    val_cb = cb_clf.predict_proba(X_val)[:, 1]
    test_cb = cb_clf.predict_proba(X_test)[:, 1]
    train_time_cb = round(time.time() - t0, 2)
    th_cb = find_best_threshold_val(y_val, val_cb)
    
    m_val_cb = eval_predictions(y_val, val_cb, th_cb)
    m_test_cb = eval_predictions(y_test, test_cb, th_cb)
    m_test_cb_whole = eval_predictions(y_test_whole, test_cb, th_cb)
    rec_cb = eval_recording_level(meta_test, test_cb, th_cb)
    
    print(f"  CatBoost (Val Thresh {th_cb:.3f}):")
    print(f"    Val:               Acc={m_val_cb['accuracy']:.4f}, Prec={m_val_cb['precision']:.4f}, Rec={m_val_cb['recall']:.4f}, F1={m_val_cb['f1_score']:.4f}, AUC={m_val_cb['roc_auc']:.4f}")
    print(f"    Test (Timestamp):  Acc={m_test_cb['accuracy']:.4f}, Prec={m_test_cb['precision']:.4f}, Rec={m_test_cb['recall']:.4f}, F1={m_test_cb['f1_score']:.4f}, AUC={m_test_cb['roc_auc']:.4f}, FP={m_test_cb['false_positives']}, FN={m_test_cb['false_negatives']}")
    
    comparison_results["CatBoost"] = {
        "model_family": "Gradient Boosted Trees (CatBoost)",
        "train_time_sec": train_time_cb,
        "selected_threshold": th_cb,
        "val_metrics": m_val_cb,
        "test_metrics_timestamp_aware": m_test_cb,
        "test_metrics_legacy_whole_file": m_test_cb_whole,
        "recording_level_metrics": rec_cb
    }

    # 4. Regularized Residual Deep MLP
    print("\n[4/5] Training Regularized Deep Residual MLP...")
    t0 = time.time()
    tf.random.set_seed(42)
    inputs = tf.keras.Input(shape=(1024,))
    x = tf.keras.layers.Dense(256, activation="relu", kernel_regularizer=tf.keras.regularizers.l2(1e-4))(inputs)
    x = tf.keras.layers.LayerNormalization()(x)
    x = tf.keras.layers.Dropout(0.4)(x)
    
    # Residual Block
    res = tf.keras.layers.Dense(128, activation="relu", kernel_regularizer=tf.keras.regularizers.l2(1e-4))(x)
    res = tf.keras.layers.LayerNormalization()(res)
    res = tf.keras.layers.Dropout(0.3)(res)
    res = tf.keras.layers.Dense(256, activation="relu", kernel_regularizer=tf.keras.regularizers.l2(1e-4))(res)
    x = tf.keras.layers.Add()([x, res])
    x = tf.keras.layers.LayerNormalization()(x)
    
    x = tf.keras.layers.Dense(64, activation="relu", kernel_regularizer=tf.keras.regularizers.l2(1e-4))(x)
    x = tf.keras.layers.Dropout(0.2)(x)
    outputs = tf.keras.layers.Dense(1, activation="sigmoid")(x)
    
    mlp = tf.keras.Model(inputs=inputs, outputs=outputs)
    mlp.compile(
        optimizer=tf.keras.optimizers.AdamW(learning_rate=0.001, weight_decay=1e-4),
        loss="binary_crossentropy",
        metrics=["accuracy"]
    )
    
    lr_schedule = tf.keras.callbacks.ReduceLROnPlateau(monitor="val_loss", factor=0.5, patience=4, min_lr=1e-5)
    early_stop = tf.keras.callbacks.EarlyStopping(monitor="val_loss", patience=10, restore_best_weights=True)
    
    # Balance positive and negative class weights
    n_pos = sum(y_train == 1)
    n_neg = sum(y_train == 0)
    w_pos = (n_pos + n_neg) / (2.0 * n_pos)
    w_neg = (n_pos + n_neg) / (2.0 * n_neg)
    
    mlp.fit(
        X_train, y_train,
        validation_data=(X_val, y_val),
        epochs=40,
        batch_size=64,
        class_weight={0: float(w_neg), 1: float(w_pos)},
        callbacks=[lr_schedule, early_stop],
        verbose=0
    )
    train_time_mlp = round(time.time() - t0, 2)
    val_mlp = mlp.predict(X_val, verbose=0).flatten()
    test_mlp = mlp.predict(X_test, verbose=0).flatten()
    th_mlp = find_best_threshold_val(y_val, val_mlp)
    
    m_val_mlp = eval_predictions(y_val, val_mlp, th_mlp)
    m_test_mlp = eval_predictions(y_test, test_mlp, th_mlp)
    m_test_mlp_whole = eval_predictions(y_test_whole, test_mlp, th_mlp)
    rec_mlp = eval_recording_level(meta_test, test_mlp, th_mlp)
    
    print(f"  Residual MLP (Val Thresh {th_mlp:.3f}):")
    print(f"    Val:               Acc={m_val_mlp['accuracy']:.4f}, Prec={m_val_mlp['precision']:.4f}, Rec={m_val_mlp['recall']:.4f}, F1={m_val_mlp['f1_score']:.4f}, AUC={m_val_mlp['roc_auc']:.4f}")
    print(f"    Test (Timestamp):  Acc={m_test_mlp['accuracy']:.4f}, Prec={m_test_mlp['precision']:.4f}, Rec={m_test_mlp['recall']:.4f}, F1={m_test_mlp['f1_score']:.4f}, AUC={m_test_mlp['roc_auc']:.4f}, FP={m_test_mlp['false_positives']}, FN={m_test_mlp['false_negatives']}")
    
    comparison_results["Residual_Deep_MLP"] = {
        "model_family": "Neural Network (Residual LayerNorm MLP)",
        "train_time_sec": train_time_mlp,
        "selected_threshold": th_mlp,
        "val_metrics": m_val_mlp,
        "test_metrics_timestamp_aware": m_test_mlp,
        "test_metrics_legacy_whole_file": m_test_mlp_whole,
        "recording_level_metrics": rec_mlp
    }

    # 5. Calibrated Hybrid Stacking Ensemble
    print("\n[5/5] Calibrating Hybrid Ensemble (MLP + CatBoost + LightGBM + XGBoost)...")
    val_ens = 0.25 * val_mlp + 0.35 * val_cb + 0.25 * val_lgb + 0.15 * val_xgb
    test_ens = 0.25 * test_mlp + 0.35 * test_cb + 0.25 * test_lgb + 0.15 * test_xgb
    th_ens = find_best_threshold_val(y_val, val_ens)
    
    m_val_ens = eval_predictions(y_val, val_ens, th_ens)
    m_test_ens = eval_predictions(y_test, test_ens, th_ens)
    m_test_ens_whole = eval_predictions(y_test_whole, test_ens, th_ens)
    rec_ens = eval_recording_level(meta_test, test_ens, th_ens)
    
    print(f"  Calibrated Ensemble (Val Thresh {th_ens:.3f}):")
    print(f"    Val:               Acc={m_val_ens['accuracy']:.4f}, Prec={m_val_ens['precision']:.4f}, Rec={m_val_ens['recall']:.4f}, F1={m_val_ens['f1_score']:.4f}, AUC={m_val_ens['roc_auc']:.4f}")
    print(f"    Test (Timestamp):  Acc={m_test_ens['accuracy']:.4f}, Prec={m_test_ens['precision']:.4f}, Rec={m_test_ens['recall']:.4f}, F1={m_test_ens['f1_score']:.4f}, AUC={m_test_ens['roc_auc']:.4f}, FP={m_test_ens['false_positives']}, FN={m_test_ens['false_negatives']}")
    print(f"    Recording Recall:  {rec_ens['gunshot_recording_recall']*100:.1f}% ({rec_ens['gunshot_recordings_detected']}/{rec_ens['gunshot_recordings_total']})")
    print(f"    Recording Rejection:{rec_ens['negative_recording_rejection_rate']*100:.1f}% ({rec_ens['negative_recordings_rejected']}/{rec_ens['negative_recordings_total']})")

    comparison_results["Calibrated_Ensemble"] = {
        "model_family": "Calibrated Hybrid Stacking Ensemble (MLP + CatBoost + LightGBM + XGBoost)",
        "ensemble_weights": [0.25, 0.35, 0.25, 0.15],
        "selected_threshold": th_ens,
        "val_metrics": m_val_ens,
        "test_metrics_timestamp_aware": m_test_ens,
        "test_metrics_legacy_whole_file": m_test_ens_whole,
        "recording_level_metrics": rec_ens
    }
    
    # Save comparison report
    output_path = Path("reports/phase3_model_comparison.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(comparison_results, f, indent=2)
    print(f"\nModel comparison report exported to: {output_path}")
    return comparison_results

if __name__ == "__main__":
    run_benchmarks()
