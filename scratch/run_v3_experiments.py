"""
Phase 45 Experiment Harness:
Evaluates candidate improvements on the DEVELOPMENT SET (218 recordings) only.
Tests Experiment 1, Experiment 2, Experiment 3 against V2 baseline.
"""

import pathlib
import librosa
import numpy as np
import pandas as pd
import joblib
import tensorflow as tf
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.model_selection import GroupKFold
from sklearn.preprocessing import StandardScaler
from sklearn.calibration import CalibratedClassifierCV

# Load dev partition
parts = pd.read_csv("scratch/v2_partitions.csv")
inv = pd.read_csv("experiments/phase41/phase41_recording_inventory.csv")
v2_pred = pd.read_csv("experiments/detector_improvement_v2/recording_level_predictions.csv")

merged = pd.merge(inv, parts[['recording_id', 'v2_partition']], on='recording_id')
merged = pd.merge(merged, v2_pred[['recording_id', 'v2_detected', 'v2_event_count', 'v2_peak_score']], on='recording_id')
dev_df = merged[merged['v2_partition'] == 'development'].copy()

p38_cache = pathlib.Path("experiments/phase38/feature_cache")
p39_cache = pathlib.Path("experiments/phase39/feature_cache")
p40_cache = pathlib.Path("experiments/phase40/feature_cache")

def get_cache(rid):
    for c in [p40_cache, p39_cache, p38_cache]:
        f = c / f"{rid}.npz"
        if f.exists():
            return f
    return None

bundle_dir = pathlib.Path("models/gunshot_yamnet_bundle")
mlp = tf.keras.models.load_model(str(bundle_dir / "classifier_head.keras"))
cb = joblib.load(str(bundle_dir / "catboost_model.joblib"))
lgb = joblib.load(str(bundle_dir / "lightgbm_model.joblib"))
xgb = joblib.load(str(bundle_dir / "xgboost_model.joblib"))

# Load precomputed features or raw audio
p38_ds = pathlib.Path("experiments/phase38/dataset")
p39_ds = pathlib.Path("experiments/phase39/dataset")
p40_ds = pathlib.Path("experiments/phase40/dataset")

def find_audio(r):
    fn = r['filename']
    for p in [p38_ds / "positive" / fn, p38_ds / "distractors" / fn, p38_ds / "continuous" / fn,
             p39_ds / "distractor" / fn, p39_ds / "continuous" / fn, p40_ds / "continuous" / fn]:
        if p.exists(): return p
    return None

print(f"Loaded {len(dev_df)} development recordings.")

