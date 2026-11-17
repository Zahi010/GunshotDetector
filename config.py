"""
Central configuration for the Gunshot Sound Detection System.
All paths and parameters are configurable via this module or CLI overrides.
"""
import os
from pathlib import Path

# Base project paths
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = Path(os.environ.get("GUNSHOT_DATA_DIR", BASE_DIR / "data"))
MODELS_DIR = Path(os.environ.get("GUNSHOT_MODELS_DIR", BASE_DIR / "models"))
RAW_AUDIO_DIR = Path(os.environ.get("GUNSHOT_RAW_AUDIO_DIR", BASE_DIR))

# Create directories if needed
DATA_DIR.mkdir(parents=True, exist_ok=True)
MODELS_DIR.mkdir(parents=True, exist_ok=True)

# Audio Preprocessing Settings (standardized for YAMNet)
SAMPLE_RATE = 16000  # YAMNet strictly requires 16 kHz
WINDOW_LENGTH_SECS = 0.96  # Standard YAMNet input window (15360 samples at 16kHz)
HOP_LENGTH_SECS = 0.48  # 50% overlap (7680 samples hop)
WINDOW_SAMPLES = int(SAMPLE_RATE * WINDOW_LENGTH_SECS)
HOP_SAMPLES = int(SAMPLE_RATE * HOP_LENGTH_SECS)

# YAMNet Embedding Dimension
EMBEDDING_DIM = 1024

# Class Definitions
CLASS_NAMES = ["background", "gunshot"]
CLASS_TO_IDX = {"background": 0, "gunshot": 1, "non_gunshot": 0}
IDX_TO_CLASS = {0: "background", 1: "gunshot"}

# Dataset Split Ratios (strictly split by original recording group to prevent leakage)
TRAIN_RATIO = 0.70
VAL_RATIO = 0.15
TEST_RATIO = 0.15
RANDOM_SEED = 42

# Training Hyperparameters
BATCH_SIZE = 32
EPOCHS = 40
LEARNING_RATE = 1e-3
WEIGHT_DECAY = 1e-4
DROPOUT_RATE = 0.3

# Augmentation Parameters (Training Split ONLY)
AUGMENTATION = {
    "gain_db_range": (-6.0, 6.0),
    "time_shift_max_ratio": 0.20,
    "bg_mix_prob": 0.50,
    "bg_mix_snr_db_range": (5.0, 20.0),
}

# Detection and Event Merging Settings
DEFAULT_THRESHOLD = 0.19  # Calibrated on validation set to maximize F1 score
MERGE_WINDOW_SECS = 1.0  # Merge detections within 1.0 second into a single event
MIN_EVENT_SCORE = 0.30  # Minimum window score to consider candidate detection

# Live Real-Time Continuous Detection Settings
LIVE_STREAM_HOP_SECS = 0.48  # Hop between live analysis windows (seconds)
LIVE_STREAM_WINDOW_SECS = 0.96  # Analysis window length (seconds)
DEFAULT_COOLDOWN_SECS = 2.0  # Minimum delay between alerts to avoid repeat triggers
DEFAULT_CONFIRM_WINDOWS = 1  # Required consecutive positive windows before alerting
SAVED_ALERTS_DIR = Path(os.environ.get("GUNSHOT_SAVED_ALERTS_DIR", BASE_DIR / "saved_alerts"))
SAVED_ALERTS_DIR.mkdir(parents=True, exist_ok=True)

# Web Application Settings
WEB_HOST = "127.0.0.1"
WEB_PORT = 5000
MAX_CONTENT_LENGTH = 32 * 1024 * 1024  # 32 MB max upload
ALLOWED_EXTENSIONS = {".mp3", ".wav", ".ogg", ".flac", ".m4a"}
