import json
import math
import pathlib
import sys
import hashlib
import time

REPO = pathlib.Path("E:/gunshot/gunshot")
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

import numpy as np
import pandas as pd
import scipy.signal
import soundfile as sf
import joblib
import tensorflow as tf
from scipy import stats

from feature_extractor import YAMNetFeatureExtractor
from model_phase14 import merge_phase14_events
from model_phase17 import merge_phase17_events
from experiments.phase31.model_phase17_state_reset_candidate import merge_phase17_events as merge_phase31_events
from experiments.phase36.model_phase36 import EventStateMachine, EventState, AcousticSuppressionEngine, SuppressionMode
from scripts.run_phase39_prospective_evaluation import calculate_poisson_ci_exact, calculate_clopper_pearson_ci, evaluate_condition_on_features

P38_DIR = REPO / "experiments" / "phase38"
P39_DIR = REPO / "experiments" / "phase39"
P40_DIR = REPO / "experiments" / "phase40"
CACHE_DIR = P40_DIR / "feature_cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

def compute_physical_crest_factor_db(audio: np.ndarray) -> float:
    if len(audio) == 0:
        return 0.0
    peak = np.max(np.abs(audio))
    rms = np.sqrt(np.mean(audio ** 2))
    if rms < 1e-9 or peak < 1e-9:
        return 0.0
    return float(20.0 * np.log10(peak / rms))

class Phase40FeatureManager:
    """Extracts and caches features for prospective streams."""
    def __init__(self):
        print("[Feature Manager] Initializing YAMNet backbone and classifiers...")
        self.fe = YAMNetFeatureExtractor()
        self.models_dir = REPO / "models" / "gunshot_yamnet_bundle"
        self.catboost = joblib.load(self.models_dir / "catboost_model.joblib")
        self.lightgbm = joblib.load(self.models_dir / "lightgbm_model.joblib")
        self.xgboost = joblib.load(self.models_dir / "xgboost_model.joblib")
        self.keras_head = tf.keras.models.load_model(self.models_dir / "classifier_head.keras", compile=False)
        self.weights = {"catboost": 0.30, "lightgbm": 0.30, "xgboost": 0.20, "keras_head": 0.20}

    def compute_ensemble_scores(self, embeddings: np.ndarray) -> np.ndarray:
        if len(embeddings) == 0:
            return np.array([], dtype=np.float32)
        p_cb = self.catboost.predict_proba(embeddings)[:, 1]
        p_lgb = self.lightgbm.predict_proba(embeddings)[:, 1]
        p_xgb = self.xgboost.predict_proba(embeddings)[:, 1]
        p_keras = self.keras_head.predict(embeddings, verbose=0).ravel()
        w = self.weights
        score = w["catboost"] * p_cb + w["lightgbm"] * p_lgb + w["xgboost"] * p_xgb + w["keras_head"] * p_keras
        return score.astype(np.float32)

    def get_or_extract_features(self, rel_path: str, recording_id: str) -> dict:
        # Check caches across phases: P40, P39, P38
        c40 = CACHE_DIR / f"{recording_id}.npz"
        c39 = P39_DIR / "feature_cache" / f"{recording_id}.npz"
        c38 = P38_DIR / "feature_cache" / f"{recording_id}.npz"
        
        target = c40 if c40.exists() else c39 if c39.exists() else c38 if c38.exists() else None
        if target is not None:
            data = np.load(target)
            return {
                "embeddings": data["embeddings"],
                "yamnet_scores": data["yamnet_scores"],
                "raw_scores": data["raw_scores"],
                "crest_factor_db": float(data["crest_factor_db"]),
                "duration_seconds": float(data["duration_seconds"]),
                "sample_rate": int(data["sample_rate"])
            }

        full_path = REPO / rel_path
        print(f"Extracting features for {recording_id} ({full_path.name})...")
        waveform, sr = sf.read(str(full_path))
        if waveform.ndim > 1:
            waveform = np.mean(waveform, axis=1)
        if sr != 16000:
            gcd = math.gcd(16000, sr)
            waveform = scipy.signal.resample_poly(waveform, 16000 // gcd, sr // gcd)
            sr = 16000

        waveform = waveform.astype(np.float32)
        dur_sec = len(waveform) / sr
        crest_db = compute_physical_crest_factor_db(waveform)

        if len(waveform) < 15360:
            waveform_padded = np.pad(waveform, (0, 15360 - len(waveform)))
        else:
            waveform_padded = waveform

        wave_tensor = tf.convert_to_tensor(waveform_padded, dtype=tf.float32)
        scores_tf, embeddings_tf, _ = self.fe.model(wave_tensor)
        embeddings = embeddings_tf.numpy()
        yamnet_scores = scores_tf.numpy()
        raw_scores = self.compute_ensemble_scores(embeddings)

        np.savez_compressed(
            c40,
            embeddings=embeddings,
            yamnet_scores=yamnet_scores,
            raw_scores=raw_scores,
            crest_factor_db=crest_db,
            duration_seconds=dur_sec,
            sample_rate=sr
        )
        return {
            "embeddings": embeddings,
            "yamnet_scores": yamnet_scores,
            "raw_scores": raw_scores,
            "crest_factor_db": crest_db,
            "duration_seconds": dur_sec,
            "sample_rate": sr
        }

def compute_convention_b_excluded_time(events: list, total_duration: float, cooldown_s: float = 2.0) -> float:
    if not events:
        return 0.0
    intervals = []
    for ev in events:
        st = max(0.0, float(ev["start_time"]))
        et = min(total_duration, float(ev["end_time"]) + cooldown_s)
        intervals.append((st, et))
    intervals.sort()
    merged = []
    for s, e in intervals:
        if not merged:
            merged.append([s, e])
        else:
            if s <= merged[-1][1]:
                merged[-1][1] = max(merged[-1][1], e)
            else:
                merged.append([s, e])
    return sum(e - s for s, e in merged)

print("Phase 40 Continuous Evaluation script ready.")

