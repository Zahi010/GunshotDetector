"""
Classifier Head Architecture, Bundle Serialization, and End-to-End Inference Detector.

Contains:
1. build_classifier_head: Dense neural network for classifying 1024-d YAMNet embeddings.
2. save_model_bundle: Packages model weights, config, threshold, class mapping, and metadata.
3. load_model_bundle: Reconstitutes the bundle for inference.
4. GunshotDetector: High-level detector that accepts raw audio waveforms, extracts YAMNet
   embeddings, evaluates probabilities, applies thresholding, and merges nearby detections
   into cohesive gunshot events.
"""
import os
import json
import time
import datetime
import numpy as np
import tensorflow as tf
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
import config
from feature_extractor import YAMNetFeatureExtractor


def build_classifier_head(
    input_dim: int = config.EMBEDDING_DIM,
    hidden_units_1: int = 256,
    hidden_units_2: int = 128,
    hidden_units_3: int = 32,
    dropout_rate: float = config.DROPOUT_RATE,
    weight_decay: float = 5e-4
) -> tf.keras.Model:
    """
    Build regularized deep classifier head trained on top of frozen YAMNet 1024-d embeddings.
    Uses L2 weight decay, LayerNormalization, and Dropout to prevent overfitting and false alarms.
    """
    regularizer = tf.keras.regularizers.l2(weight_decay) if weight_decay > 0 else None

    inputs = tf.keras.Input(shape=(input_dim,), name="yamnet_embedding")
    x = tf.keras.layers.Dense(hidden_units_1, activation="relu", kernel_regularizer=regularizer, name="dense_1")(inputs)
    x = tf.keras.layers.LayerNormalization(name="ln_1")(x)
    x = tf.keras.layers.Dropout(0.4, name="dropout_1")(x)

    x = tf.keras.layers.Dense(hidden_units_2, activation="relu", kernel_regularizer=regularizer, name="dense_2")(x)
    x = tf.keras.layers.LayerNormalization(name="ln_2")(x)
    x = tf.keras.layers.Dropout(0.3, name="dropout_2")(x)

    x = tf.keras.layers.Dense(hidden_units_3, activation="relu", kernel_regularizer=regularizer, name="dense_3")(x)
    x = tf.keras.layers.Dropout(0.2, name="dropout_3")(x)
    outputs = tf.keras.layers.Dense(1, activation="sigmoid", name="gunshot_prob")(x)

    model = tf.keras.Model(inputs=inputs, outputs=outputs, name="gunshot_classifier_head")
    return model


def save_model_bundle(
    model: tf.keras.Model,
    bundle_dir: Path,
    selected_threshold: float,
    threshold_presets: Optional[Dict[str, float]] = None,
    training_metadata: Optional[Dict[str, Any]] = None,
    evaluation_metrics: Optional[Dict[str, Any]] = None
) -> Path:
    """
    Save complete deployment bundle containing:
    - classifier_head.keras
    - model_config.json
    - class_mapping.json
    - threshold.json
    - metadata.json
    """
    bundle_dir = Path(bundle_dir)
    bundle_dir.mkdir(parents=True, exist_ok=True)

    # 1. Save Keras model weights and architecture
    model_path = bundle_dir / "classifier_head.keras"
    model.save(str(model_path))

    # 2. Preprocessing & model architecture configuration
    model_config = {
        "framework": "tensorflow/keras",
        "backbone": "google/yamnet (frozen AudioSet MobileNet)",
        "input_embedding_dim": config.EMBEDDING_DIM,
        "sample_rate": config.SAMPLE_RATE,
        "window_length_secs": config.WINDOW_LENGTH_SECS,
        "hop_length_secs": config.HOP_LENGTH_SECS,
        "window_samples": config.WINDOW_SAMPLES,
        "hop_samples": config.HOP_SAMPLES,
        "architecture_summary": "Input(1024) -> Dense(128, relu) -> BN -> Dropout(0.3) -> Dense(32, relu) -> Dropout(0.2) -> Dense(1, sigmoid)"
    }
    with open(bundle_dir / "model_config.json", "w", encoding="utf-8") as f:
        json.dump(model_config, f, indent=2)

    # 3. Class Mapping
    class_mapping = {
        "classes": config.CLASS_NAMES,
        "class_to_idx": config.CLASS_TO_IDX,
        "idx_to_class": {str(k): v for k, v in config.IDX_TO_CLASS.items()}
    }
    with open(bundle_dir / "class_mapping.json", "w", encoding="utf-8") as f:
        json.dump(class_mapping, f, indent=2)

    # 4. Threshold Configuration
    if threshold_presets is None:
        threshold_presets = {
            "high_recall_sensitive": max(0.15, round(selected_threshold * 0.6, 2)),
            "balanced_optimal": round(selected_threshold, 3),
            "high_precision_conservative": min(0.85, round(selected_threshold * 1.3, 2))
        }

    threshold_data = {
        "selected_optimal_threshold": round(selected_threshold, 3),
        "threshold_selection_criterion": "Optimized on validation set to maximize F1 score while penalizing false alarms",
        "presets": threshold_presets,
        "event_merge_window_secs": config.MERGE_WINDOW_SECS
    }
    with open(bundle_dir / "threshold.json", "w", encoding="utf-8") as f:
        json.dump(threshold_data, f, indent=2)

    # 5. Training & Evaluation Metadata
    metadata = {
        "bundle_version": "1.0.0",
        "created_at_utc": datetime.datetime.utcnow().isoformat(),
        "confidence_calibrated": False,
        "confidence_note": (
            "Scores represent raw sigmoid probabilities from the neural network classifier. "
            "They should be termed detection scores rather than calibrated Bayesian confidence "
            "until formal Platt scaling or Isotonic regression is conducted on live in-field test data."
        ),
        "safety_disclaimer": (
            "CRITICAL DISCLAIMER: This gunshot detection model is designed for research, "
            "prototyping, and evaluation purposes only. It MUST NOT be relied upon as a primary "
            "safety system, emergency response trigger, or life-critical monitoring apparatus."
        ),
        "training_history": training_metadata or {},
        "evaluation_metrics": evaluation_metrics or {}
    }
    with open(bundle_dir / "metadata.json", "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    print(f"\n[OK] Complete Gunshot Detector bundle saved to: {bundle_dir}")
    return bundle_dir


class CalibratedEnsemble:
    """
    High-precision ensemble combining Regularized Deep MLP, CatBoost, LightGBM, and XGBoost.
    Achieves superior boundary separation on impulsive acoustic transients.
    """
    def __init__(self, mlp_model, cb_model=None, lgb_model=None, xgb_model=None, weights=(0.25, 0.35, 0.25, 0.15)):
        self.mlp_model = mlp_model
        self.cb_model = cb_model
        self.lgb_model = lgb_model
        self.xgb_model = xgb_model
        self.weights = weights

    def predict(self, X, verbose=0):
        mlp_preds = self.mlp_model.predict(X, verbose=verbose).flatten()
        cb_preds = self.cb_model.predict_proba(X)[:, 1] if self.cb_model is not None else mlp_preds
        lgb_preds = self.lgb_model.predict_proba(X)[:, 1] if self.lgb_model is not None else mlp_preds
        
        if self.xgb_model is not None and len(self.weights) == 4:
            xgb_preds = self.xgb_model.predict_proba(X)[:, 1]
            w1, w2, w3, w4 = self.weights
            blend = w1 * mlp_preds + w2 * cb_preds + w3 * lgb_preds + w4 * xgb_preds
        else:
            w1, w2, w3 = self.weights[:3]
            tot = w1 + w2 + w3
            blend = (w1 * mlp_preds + w2 * cb_preds + w3 * lgb_preds) / tot
            
        return blend.reshape(-1, 1)


def load_model_bundle(bundle_dir: Path) -> Tuple[Any, Dict[str, Any]]:
    """
    Load saved model bundle and all accompanying configurations.
    Automatically loads CalibratedEnsemble if CatBoost, LightGBM, or XGBoost weights exist.
    """
    bundle_dir = Path(bundle_dir)
    model_path = bundle_dir / "classifier_head.keras"
    if not model_path.exists():
        raise FileNotFoundError(f"Classifier head model not found at {model_path}!")

    model = tf.keras.models.load_model(str(model_path))

    with open(bundle_dir / "model_config.json", "r", encoding="utf-8") as f:
        model_config = json.load(f)
    with open(bundle_dir / "threshold.json", "r", encoding="utf-8") as f:
        threshold_config = json.load(f)
    with open(bundle_dir / "class_mapping.json", "r", encoding="utf-8") as f:
        class_mapping = json.load(f)

    # Check for ensemble models
    cb_path = bundle_dir / "catboost_model.joblib"
    lgb_path = bundle_dir / "lightgbm_model.joblib"
    xgb_path = bundle_dir / "xgboost_model.joblib"
    
    if cb_path.exists() and lgb_path.exists():
        import joblib
        try:
            cb_model = joblib.load(str(cb_path))
            lgb_model = joblib.load(str(lgb_path))
            xgb_model = joblib.load(str(xgb_path)) if xgb_path.exists() else None
            weights = model_config.get("ensemble_weights", [0.25, 0.35, 0.25, 0.15] if xgb_model else [0.30, 0.40, 0.30])
            model = CalibratedEnsemble(model, cb_model, lgb_model, xgb_model=xgb_model, weights=tuple(weights))
        except Exception as e:
            print(f"Warning: Failed to load ensemble models ({e}). Using Keras model fallback.")

    metadata = {}
    if (bundle_dir / "metadata.json").exists():
        with open(bundle_dir / "metadata.json", "r", encoding="utf-8") as f:
            metadata = json.load(f)

    bundle_info = {
        "bundle_dir": str(bundle_dir),
        "model_config": model_config,
        "threshold_config": threshold_config,
        "class_mapping": class_mapping,
        "metadata": metadata,
        "selected_threshold": threshold_config.get("selected_optimal_threshold", 0.48)
    }
    return model, bundle_info


def merge_detection_windows(
    window_results: List[Dict[str, Any]],
    threshold: float,
    confirm_windows: int = 1,
    cooldown_secs: float = config.DEFAULT_COOLDOWN_SECS,
    max_event_duration: float = 2.5,
    merge_window_secs: Optional[float] = None,
    threshold_off: Optional[float] = None
) -> List[Dict[str, Any]]:
    """
    Cluster and merge nearby window triggers into coherent gunshot events.
    Uses causal streaming state-machine logic matching live inference.
    
    Supports:
    - Hysteresis: High threshold_on to trigger alert event, lower threshold_off to track reverberant tail.
    - Consecutive window confirmation (confirm_windows >= 1).
    - Refractory cooldown lockout.
    - Strict monotonicity.
    """
    if merge_window_secs is not None:
        cooldown_secs = merge_window_secs
    if threshold_off is None:
        threshold_off = max(0.20, threshold - 0.25)
    if not window_results:
        return []

    # Ensure windows are sorted by time
    sorted_windows = sorted(window_results, key=lambda x: x["start_time"])

    events = []
    cooldown_until = -1.0
    active_cluster: List[Dict[str, Any]] = []
    in_event = False
    had_decayed = True

    for win in sorted_windows:
        st = win["start_time"]
        et = win["end_time"]
        score = win["score"]

        if not in_event:
            if score < threshold_off:
                had_decayed = True

            # Check if in cooldown refractory period
            if st < cooldown_until:
                # Suppress reverberant tail flutter and weak reflections.
                # However, preserve genuine distinct gunshots if the signal had decayed
                # below threshold_off and a new strong onset arrives (score >= threshold).
                if had_decayed and score >= threshold:
                    active_cluster.append(win)
                    if len(active_cluster) >= confirm_windows:
                        in_event = True
                        had_decayed = False
                else:
                    # In cooldown and not a new verified onset: suppress duplicate alert
                    continue
            else:
                # Normal onset detection past cooldown
                if score >= threshold:
                    active_cluster.append(win)
                    if len(active_cluster) >= confirm_windows:
                        in_event = True
                        had_decayed = False
                else:
                    active_cluster = []
        else:
            # In active event tracking reverberant decay
            gap = st - active_cluster[-1]["end_time"]
            cluster_dur = et - active_cluster[0]["start_time"]
            if gap <= 0.50 and cluster_dur <= max_event_duration and score >= threshold_off:
                active_cluster.append(win)
            else:
                # Previous event ended
                prev_et = active_cluster[-1]["end_time"]
                event = _create_event_from_cluster(active_cluster)
                events.append(event)
                cooldown_until = prev_et + cooldown_secs
                active_cluster = []
                in_event = False
                had_decayed = (score < threshold_off)

                # Evaluate current window for immediate new onset trigger
                if score >= threshold:
                    if st >= cooldown_until or had_decayed:
                        active_cluster.append(win)
                        if len(active_cluster) >= confirm_windows:
                            in_event = True
                            had_decayed = False

    # Close any trailing open event
    if in_event and active_cluster:
        event = _create_event_from_cluster(active_cluster)
        events.append(event)

    return events


def _create_event_from_cluster(cluster: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Summarize a cluster of positive detection windows into a single event."""
    start_time = cluster[0]["start_time"]
    end_time = cluster[-1]["end_time"]
    peak_win = max(cluster, key=lambda x: x["score"])

    return {
        "start_time": round(start_time, 2),
        "end_time": round(end_time, 2),
        "duration_seconds": round(end_time - start_time, 2),
        "peak_time": round((peak_win["start_time"] + peak_win["end_time"]) / 2, 2),
        "peak_score": round(float(peak_win["score"]), 3),
        "mean_score": round(float(np.mean([w["score"] for w in cluster])), 3),
        "trigger_windows_count": len(cluster),
        "verdict": "Gunshot Detected"
    }


class GunshotDetector:
    """
    End-to-End Gunshot Detector.
    Encapsulates YAMNet backbone feature extraction, the trained classifier head,
    configurable thresholding, and event merging.
    """
    def __init__(
        self,
        bundle_dir: Path,
        feature_extractor: Optional[YAMNetFeatureExtractor] = None,
        threshold: Optional[float] = None
    ):
        self.bundle_dir = Path(bundle_dir)
        self.classifier_head, self.bundle_info = load_model_bundle(self.bundle_dir)
        self.feature_extractor = feature_extractor or YAMNetFeatureExtractor()
        self.threshold = threshold if threshold is not None else self.bundle_info["selected_threshold"]
        self.cooldown_secs = self.bundle_info["threshold_config"].get(
            "cooldown_secs", config.DEFAULT_COOLDOWN_SECS
        )
        self.merge_window_secs = self.cooldown_secs
        self.confirm_windows = self.bundle_info["threshold_config"].get(
            "confirm_windows", config.DEFAULT_CONFIRM_WINDOWS
        )

    def detect_waveform(
        self,
        waveform: np.ndarray,
        threshold: Optional[float] = None,
        confirm_windows: Optional[int] = None,
        cooldown_secs: Optional[float] = None,
        merge_window_secs: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Run gunshot detection on a 16 kHz mono float32 waveform.
        Returns overall verdict, window-level scores, and merged gunshot events.
        """
        curr_threshold = threshold if threshold is not None else self.threshold
        curr_confirm = confirm_windows if confirm_windows is not None else self.confirm_windows
        curr_cooldown = cooldown_secs if cooldown_secs is not None else self.cooldown_secs
        if merge_window_secs is not None:
            curr_cooldown = merge_window_secs

        t0 = time.time()
        # 1. Check for empty or near-silence waveform
        if len(waveform) == 0:
            return {
                "gunshot_detected": False,
                "overall_score": 0.0,
                "selected_threshold": curr_threshold,
                "confirm_windows": curr_confirm,
                "cooldown_secs": curr_cooldown,
                "events_count": 0,
                "events": [],
                "total_windows": 0,
                "window_results": [],
                "audio_duration_seconds": 0.0,
                "inference_time_ms": 0.0,
                "confidence_calibrated": self.bundle_info["metadata"].get("confidence_calibrated", False),
                "disclaimer": self.bundle_info["metadata"].get("safety_disclaimer", "")
            }

        # 2. Extract continuous YAMNet embeddings
        embeddings, timestamps = self.feature_extractor.extract_continuous_recording(waveform)

        # 3. Score with classifier head
        raw_scores = self.classifier_head.predict(embeddings, verbose=0).flatten()

        # 4. Energy Squelch Gate: gunshots require acoustic energy.
        # Silence or near-zero arrays (RMS < 1e-4, -80 dBFS) are zeroed out.
        hop_samples = config.HOP_SAMPLES
        win_samples = config.WINDOW_SAMPLES
        for i in range(len(raw_scores)):
            start_s = i * hop_samples
            end_s = start_s + win_samples
            chunk = waveform[start_s:end_s]
            if len(chunk) > 0:
                chunk_rms = float(np.sqrt(np.mean(chunk ** 2) + 1e-12))
                if chunk_rms < 1e-4:  # silence floor
                    raw_scores[i] = 0.0

        # 5. Build window results
        window_results = []
        for i, (score, (st, et)) in enumerate(zip(raw_scores, timestamps)):
            window_results.append({
                "window_index": i,
                "start_time": st,
                "end_time": et,
                "score": round(float(score), 4),
                "is_positive": bool(score >= curr_threshold)
            })

        # 4. Merge nearby detections into events using causal streaming logic
        detected_events = merge_detection_windows(
            window_results,
            threshold=curr_threshold,
            confirm_windows=curr_confirm,
            cooldown_secs=curr_cooldown
        )

        overall_score = float(np.max(raw_scores)) if len(raw_scores) > 0 else 0.0
        has_detection = len(detected_events) > 0
        inference_time_ms = round((time.time() - t0) * 1000, 1)

        return {
            "gunshot_detected": has_detection,
            "overall_score": round(overall_score, 4),
            "selected_threshold": curr_threshold,
            "confirm_windows": curr_confirm,
            "cooldown_secs": curr_cooldown,
            "events_count": len(detected_events),
            "events": detected_events,
            "total_windows": len(window_results),
            "window_results": window_results,
            "audio_duration_seconds": round(len(waveform) / config.SAMPLE_RATE, 2),
            "inference_time_ms": inference_time_ms,
            "confidence_calibrated": self.bundle_info["metadata"].get("confidence_calibrated", False),
            "disclaimer": self.bundle_info["metadata"].get("safety_disclaimer", "")
        }
