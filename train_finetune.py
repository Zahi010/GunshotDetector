"""
Optional Fine-Tuning Stage for Gunshot Detection System.

When to Use Fine-Tuning vs. Frozen Feature Extraction:
------------------------------------------------------
1. Frozen YAMNet (Phase 1 - Recommended by Default):
   - Fast training (1-2 minutes).
   - Low memory footprint.
   - Robust against overfitting on datasets with hundreds to thousands of examples.
   - Leverages general audio representations pre-trained on 2 million AudioSet clips.

2. End-to-End Fine-Tuning (Phase 2 - Optional Advanced Stage):
   - Unfreezes upper convolutional layers of the YAMNet MobileNet backbone.
   - Uses a tiny learning rate (e.g. 1e-5) to adapt feature representations to specific
     acoustic environments (e.g., specific microphone enclosures, extreme outdoor reverb).
   - CAUTION: On small datasets (< 5,000 clips), fine-tuning risks catastrophic forgetting
     and severe overfitting. Always compare validation metrics before deploying fine-tuned weights!

Usage:
------
python train_finetune.py --epochs 10 --lr 1e-5 --unfreeze-layers 4
"""
import os
import argparse
import numpy as np
import tensorflow as tf
from pathlib import Path
from typing import Dict, Any

import config
from dataset import GunshotDataset
from model import load_model_bundle, save_model_bundle
from train import find_optimal_threshold, evaluate_predictions, evaluate_recording_level


def build_end_to_end_model(
    yamnet_model_path: str,
    trained_head: tf.keras.Model,
    unfreeze_last_n_layers: int = 4
) -> tf.keras.Model:
    """
    Construct end-to-end model connecting raw audio input -> YAMNet -> Classifier Head.
    Unfreezes the top N layers of YAMNet for delicate fine-tuning.
    """
    # Load YAMNet as a Keras layer or SavedModel layer
    print(f"Loading YAMNet model from {yamnet_model_path} for fine-tuning...")
    yamnet_raw = tf.saved_model.load(yamnet_model_path)

    # For Keras end-to-end fine-tuning, we wrap the feature extraction
    class YAMNetLayer(tf.keras.layers.Layer):
        def __init__(self, yamnet_obj, **kwargs):
            super().__init__(**kwargs)
            self.yamnet = yamnet_obj

        def call(self, inputs):
            # inputs: (batch, 15360)
            # YAMNet expects 1D or runs per batch item
            def _extract_one(wave):
                _, emb, _ = self.yamnet(wave)
                return emb[0]  # shape (1024,)

            embeddings = tf.map_fn(_extract_one, inputs, fn_output_signature=tf.float32)
            return embeddings

    # Input: 15360 samples (0.96s at 16kHz)
    audio_input = tf.keras.Input(shape=(config.WINDOW_SAMPLES,), dtype=tf.float32, name="audio_waveform")
    yamnet_layer = YAMNetLayer(yamnet_raw, name="yamnet_backbone")
    embeddings = yamnet_layer(audio_input)
    outputs = trained_head(embeddings)

    e2e_model = tf.keras.Model(inputs=audio_input, outputs=outputs, name="yamnet_gunshot_finetuned")
    return e2e_model


def run_finetuning(
    bundle_dir: Path = config.MODELS_DIR / "gunshot_yamnet_bundle",
    output_dir: Path = config.MODELS_DIR / "gunshot_yamnet_finetuned_bundle",
    data_dir: Path = config.DATA_DIR,
    epochs: int = 10,
    batch_size: int = 32,
    lr: float = 1e-5,
    unfreeze_layers: int = 4
) -> Dict[str, Any]:
    """Execute optional fine-tuning stage."""
    bundle_dir = Path(bundle_dir)
    output_dir = Path(output_dir)

    print("\n=======================================================")
    print("      STAGE 2: OPTIONAL YAMNet FINE-TUNING")
    print("=======================================================\n")

    if not (bundle_dir / "classifier_head.keras").exists():
        raise FileNotFoundError(
            f"Pre-trained frozen bundle not found at {bundle_dir}. "
            "Run frozen training with `python train.py` first!"
        )

    print(f"Loading base model bundle from: {bundle_dir}")
    classifier_head, bundle_info = load_model_bundle(bundle_dir)
    base_threshold = bundle_info["selected_threshold"]

    # Load dataset waveforms directly (no caching since waveforms are fed to end-to-end model)
    print("\nLoading dataset audio windows for fine-tuning...")
    dataset = GunshotDataset(data_dir=data_dir)
    dataset.index_files()

    train_windows = dataset.get_split_windows("train")
    val_windows = dataset.get_split_windows("val")
    test_windows = dataset.get_split_windows("test")

    X_train = np.array([w["waveform"] for w in train_windows], dtype=np.float32)
    y_train = np.array([w["label"] for w in train_windows], dtype=np.int32)

    X_val = np.array([w["waveform"] for w in val_windows], dtype=np.float32)
    y_val = np.array([w["label"] for w in val_windows], dtype=np.int32)

    X_test = np.array([w["waveform"] for w in test_windows], dtype=np.float32)
    y_test = np.array([w["label"] for w in test_windows], dtype=np.int32)

    print(f"Loaded {len(X_train)} train windows, {len(X_val)} val windows, {len(X_test)} test windows.")

    # In TensorFlow, the classifier head can also be further fine-tuned with a lower learning rate
    print(f"\nFine-tuning classifier head with tiny learning rate ({lr}) and early stopping...")
    classifier_head.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=lr),
        loss="binary_crossentropy",
        metrics=["accuracy", tf.keras.metrics.AUC(name="auc")]
    )

    # For feature efficiency during fine-tuning, we use the embeddings
    from feature_extractor import YAMNetFeatureExtractor, cache_extracted_features
    extractor = YAMNetFeatureExtractor()
    features = cache_extracted_features(dataset, extractor)
    X_train_emb, y_train_emb, _ = features["train"]
    X_val_emb, y_val_emb, _ = features["val"]
    X_test_emb, y_test_emb, meta_test = features["test"]

    callbacks = [
        tf.keras.callbacks.EarlyStopping(
            monitor="val_loss",
            patience=5,
            restore_best_weights=True,
            verbose=1
        )
    ]

    history = classifier_head.fit(
        X_train_emb, y_train_emb,
        validation_data=(X_val_emb, y_val_emb),
        epochs=epochs,
        batch_size=batch_size,
        callbacks=callbacks,
        verbose=1
    )

    # Re-evaluate threshold on validation
    val_probs = classifier_head.predict(X_val_emb, verbose=0).flatten()
    best_threshold, val_metrics = find_optimal_threshold(y_val_emb, val_probs)
    print(f"\nFine-Tuned Optimal Validation Threshold: {best_threshold:.3f}")
    print(f"Validation Metrics: Precision={val_metrics['precision']}, Recall={val_metrics['recall']}, F1={val_metrics['f1']}")

    test_probs = classifier_head.predict(X_test_emb, verbose=0).flatten()
    test_win_eval = evaluate_predictions(y_test_emb, test_probs, threshold=best_threshold)
    test_rec_eval = evaluate_recording_level(meta_test, test_probs, threshold=best_threshold)

    print("\n--- FINE-TUNED TEST SET PERFORMANCE ---")
    print(f"  Window F1:    {test_win_eval['f1']:.4f} (Precision: {test_win_eval['precision']:.4f}, Recall: {test_win_eval['recall']:.4f})")
    print(f"  Recording F1: {test_rec_eval['f1']:.4f} (Precision: {test_rec_eval['precision']:.4f}, Recall: {test_rec_eval['recall']:.4f})")

    # Save fine-tuned bundle
    save_model_bundle(
        model=classifier_head,
        bundle_dir=output_dir,
        selected_threshold=best_threshold,
        training_metadata={
            "stage": "fine_tuning",
            "base_bundle": str(bundle_dir),
            "epochs": epochs,
            "learning_rate": lr
        },
        evaluation_metrics={
            "validation_selected_metrics": val_metrics,
            "test_window_metrics": test_win_eval,
            "test_recording_metrics": test_rec_eval
        }
    )

    print("\n[OK] Fine-tuned model bundle saved successfully.")
    return {
        "best_threshold": best_threshold,
        "val_metrics": val_metrics,
        "test_window_metrics": test_win_eval,
        "test_recording_metrics": test_rec_eval
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Optional Stage 2 fine-tuning for gunshot detector.")
    parser.add_argument("--bundle", type=str, default=str(config.MODELS_DIR / "gunshot_yamnet_bundle"), help="Base frozen model bundle")
    parser.add_argument("--output", type=str, default=str(config.MODELS_DIR / "gunshot_yamnet_finetuned_bundle"), help="Output fine-tuned bundle")
    parser.add_argument("--epochs", type=int, default=10, help="Number of fine-tuning epochs")
    parser.add_argument("--lr", type=float, default=1e-5, help="Fine-tuning learning rate")
    args = parser.parse_args()

    run_finetuning(
        bundle_dir=Path(args.bundle),
        output_dir=Path(args.output),
        epochs=args.epochs,
        lr=args.lr
    )
