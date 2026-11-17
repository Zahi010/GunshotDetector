"""
YAMNet Audio Feature Extractor.

Loads Google's pretrained YAMNet model (AudioSet MobileNet architecture)
and extracts 1024-dimensional feature embeddings from 16 kHz mono audio waveforms.
The YAMNet backbone is kept completely frozen.
"""
import os
import kagglehub
import numpy as np
import tensorflow as tf
from pathlib import Path
from typing import Tuple, List, Optional, Dict
import config


class YAMNetFeatureExtractor:
    """
    Wrapper around pretrained YAMNet SavedModel for extracting 1024-d embeddings.
    """
    def __init__(self, model_handle: str = "google/yamnet/tensorFlow2/yamnet"):
        self.model_handle = model_handle
        self.model = None
        self._load_model()

    def _load_model(self) -> None:
        """Download or retrieve cached YAMNet SavedModel and load into memory."""
        # Check if local path or kagglehub
        if os.path.exists(self.model_handle):
            model_path = self.model_handle
        else:
            model_path = kagglehub.model_download(self.model_handle)

        self.model_path = model_path
        self.model = tf.saved_model.load(model_path)

    def extract_single_window(self, waveform: np.ndarray) -> np.ndarray:
        """
        Extract 1024-d embedding for a single 15360-sample (0.96s) window.
        Returns shape (1024,).
        """
        if len(waveform) < config.WINDOW_SAMPLES:
            waveform = np.pad(waveform, (0, config.WINDOW_SAMPLES - len(waveform)))
        elif len(waveform) > config.WINDOW_SAMPLES:
            waveform = waveform[:config.WINDOW_SAMPLES]

        waveform = tf.convert_to_tensor(waveform, dtype=tf.float32)
        _, embeddings, _ = self.model(waveform)
        # embeddings shape: (1, 1024)
        return embeddings.numpy()[0]

    def extract_batch_windows(self, waveforms: List[np.ndarray], batch_size: int = 64) -> np.ndarray:
        """
        Extract 1024-d embeddings for a list of 15360-sample windows.
        Returns shape (N, 1024).
        """
        embeddings_list = []
        n = len(waveforms)
        for i in range(0, n, batch_size):
            batch = waveforms[i:i + batch_size]
            for wave in batch:
                emb = self.extract_single_window(wave)
                embeddings_list.append(emb)

        return np.vstack(embeddings_list).astype(np.float32)

    def extract_continuous_recording(
        self,
        waveform: np.ndarray
    ) -> Tuple[np.ndarray, List[Tuple[float, float]]]:
        """
        Extract embeddings and window timestamps for an entire audio recording.
        YAMNet internally slides a 0.96s window with a 0.48s hop.
        Returns:
            embeddings: (T, 1024) array
            timestamps: list of (start_seconds, end_seconds) for each window
        """
        # Ensure minimum length
        if len(waveform) < config.WINDOW_SAMPLES:
            waveform = np.pad(waveform, (0, config.WINDOW_SAMPLES - len(waveform)))

        wave_tensor = tf.convert_to_tensor(waveform, dtype=tf.float32)
        scores, embeddings, _ = self.model(wave_tensor)
        emb_arr = embeddings.numpy()

        n_windows = emb_arr.shape[0]
        timestamps = []
        hop_sec = config.HOP_LENGTH_SECS
        win_sec = config.WINDOW_LENGTH_SECS

        for i in range(n_windows):
            start_t = round(i * hop_sec, 3)
            end_t = round(start_t + win_sec, 3)
            timestamps.append((start_t, end_t))

        return emb_arr, timestamps


def cache_extracted_features(
    dataset,
    extractor: YAMNetFeatureExtractor,
    cache_dir: Path = Path(".cache_features")
) -> Dict[str, Tuple[np.ndarray, np.ndarray, List[Dict]]]:
    """
    Extract and cache YAMNet embeddings for train, val, and test splits.
    Respects group splits and training-only augmentation.
    """
    cache_dir = Path(cache_dir)
    cache_dir.mkdir(parents=True, exist_ok=True)

    result = {}
    for split in ["train", "val", "test"]:
        cache_file = cache_dir / f"features_{split}.npz"
        if cache_file.exists():
            print(f"Loading cached {split} embeddings from {cache_file}...")
            data = np.load(str(cache_file), allow_pickle=True)
            X = data["X"]
            y = data["y"]
            meta = list(data["meta"])
            result[split] = (X, y, meta)
        else:
            print(f"Extracting YAMNet embeddings for {split} split...")
            windows = dataset.get_split_windows(split)
            if not windows:
                X = np.empty((0, config.EMBEDDING_DIM), dtype=np.float32)
                y = np.empty((0,), dtype=np.int32)
                meta = []
            else:
                waves = [w["waveform"] for w in windows]
                X = extractor.extract_batch_windows(waves, batch_size=128)
                y = np.array([w["label"] for w in windows], dtype=np.int32)
                y_whole = np.array([w.get("whole_file_label", w["label"]) for w in windows], dtype=np.int32)
                meta = [
                    {
                        "recording_id": w["recording_id"],
                        "start_time": w["start_time"],
                        "end_time": w["end_time"],
                        "label": w["label"],
                        "whole_file_label": w.get("whole_file_label", w["label"]),
                        "max_overlap_sec": w.get("max_overlap_sec", 0.0),
                        "is_ambiguous": w.get("is_ambiguous", False)
                    }
                    for w in windows
                ]

            np.savez_compressed(
                str(cache_file),
                X=X,
                y=y,
                y_whole_file=y_whole if 'y_whole' in locals() else y,
                meta=np.array(meta, dtype=object)
            )
            print(f"Saved {split} embeddings to {cache_file} (shape: {X.shape})")
            result[split] = (X, y, meta)

    return result


if __name__ == "__main__":
    from dataset import GunshotDataset
    print("Testing YAMNet feature extractor...")
    extractor = YAMNetFeatureExtractor()
    test_wave = np.zeros(15360, dtype=np.float32)
    emb = extractor.extract_single_window(test_wave)
    print("Single window embedding shape:", emb.shape)
