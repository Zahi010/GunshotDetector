"""
Test Suite for Detector Improvement V1
MANDATORY SAFETY DESIGNATION:
RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY

This software is an uncertified research prototype. Never deploy for autonomous
emergency dispatch, police tactical response, active-shooter alerting, automated
evacuation, building lockdown, or life-critical physical security.
"""

import os
import io
import sys
import json
import pathlib
import pytest
import numpy as np
import soundfile as sf

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

EXP_DIR = REPO_ROOT / "experiments" / "detector_improvement_v1"
if str(EXP_DIR) not in sys.path:
    sys.path.insert(0, str(EXP_DIR))

import config
from app import app
from experiments.detector_improvement_v1.model_detector_improvement_v1 import (
    CalibratedAcousticSuppressionV1,
    DetectorImprovementV1,
    RealTimeStreamDetectorImprovementV1
)
from experiments.phase36.event_state_machine import EventState


@pytest.fixture
def flask_client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


# ==============================================================================
# 1. Initialization and Profile Configuration Tests
# ==============================================================================

def test_config_and_profiles_exist():
    config_file = EXP_DIR / "config_improvement_v1.json"
    assert config_file.exists(), "config_improvement_v1.json must exist."
    with open(config_file, "r", encoding="utf-8") as f:
        cfg = json.load(f)
    assert cfg["system_designation"] == "RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY"
    assert "balanced" in cfg["profiles"]
    assert "high_precision" in cfg["profiles"]
    assert "high_sensitivity" in cfg["profiles"]


def test_detector_initialization():
    for prof in ["balanced", "high_precision", "high_sensitivity"]:
        det = DetectorImprovementV1(profile=prof)
        assert det.profile == prof
        assert det.threshold_base > 0.0
        assert det.threshold_high > det.threshold_base
        assert det.threshold_off < det.threshold_base
        assert det.cooldown_secs >= 1.5


# ==============================================================================
# 2. Semantic Suppression Engine Tests
# ==============================================================================

def test_semantic_suppression_fireworks():
    supp_cfg = {
        "enabled": True,
        "fireworks": {"threshold": 0.30, "ratio": 1.5, "gun_max": 0.10, "attenuation": 0.35}
    }
    engine = CalibratedAcousticSuppressionV1(supp_cfg)

    # Synthetic YAMNet vector (521 classes)
    yamnet_vec = np.zeros(521, dtype=np.float32)
    yamnet_vec[426] = 0.85 # Fireworks class
    yamnet_vec[421] = 0.02 # Gunshot class (below 0.10)

    # Raw ensemble score 0.82
    res = engine.apply_suppression(0.82, yamnet_vec, is_in_confirmed_event=False)
    assert res["suppression_active"] is True
    assert res["suppression_category"] == "fireworks"
    assert res["adjusted_score"] < 0.50 # Strongly attenuated


def test_semantic_suppression_ballistic_protection():
    supp_cfg = {
        "enabled": True,
        "fireworks": {"threshold": 0.30, "ratio": 1.5, "gun_max": 0.10, "attenuation": 0.35}
    }
    engine = CalibratedAcousticSuppressionV1(supp_cfg)

    # Genuine gunshot accompanied by high energy
    yamnet_vec = np.zeros(521, dtype=np.float32)
    yamnet_vec[426] = 0.50 # Fireworks class
    yamnet_vec[421] = 0.60 # High genuine gunshot score (> 0.10 ceiling)

    res = engine.apply_suppression(0.85, yamnet_vec, is_in_confirmed_event=False)
    assert res["suppression_active"] is False # Ballistic protection protects the gunshot!
    assert res["adjusted_score"] == 0.85


# ==============================================================================
# 3. Waveform Evaluation and State Machine Lifecycle Tests
# ==============================================================================

def test_evaluate_waveform_clean_audio():
    det = DetectorImprovementV1(profile="balanced")
    clean_audio = np.random.randn(16000).astype(np.float32) * 0.01
    res = det.evaluate_waveform(clean_audio)

    assert "duration_seconds" in res
    assert "crest_factor_db" in res
    assert "total_windows" in res
    assert res["detected"] is False
    assert len(res["events"]) == 0


def test_streaming_ring_buffer_chunk_processing():
    stream_det = RealTimeStreamDetectorImprovementV1(profile="balanced")
    chunk_480ms = np.random.randn(7680).astype(np.float32) * 0.01

    # Feed 3 sequential chunks (1.44s total audio)
    alerts1 = stream_det.process_chunk(chunk_480ms)
    alerts2 = stream_det.process_chunk(chunk_480ms)
    alerts3 = stream_det.process_chunk(chunk_480ms)

    assert isinstance(alerts1, list)
    assert isinstance(alerts2, list)
    assert isinstance(alerts3, list)
    assert stream_det.stream_time_sec >= 0.96
    assert len(stream_det.chunk_latencies_ms) > 0


# ==============================================================================
# 4. Web Application Route Integration Tests
# ==============================================================================

def test_api_health_endpoint(flask_client):
    res = flask_client.get("/api/health")
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "healthy"
    assert "detector_improvement_v1" in data["supported_detectors"]
    assert "detector_improvement_v1" in data["experimental_detectors"]


def test_api_status_endpoint(flask_client):
    res = flask_client.get("/api/status")
    assert res.status_code == 200
    data = res.get_json()
    assert "detector_improvement_v1" in data["supported_versions"]
    assert "detector_improvement_v1_profiles" in data["architecture"]


def test_api_profiles_endpoint(flask_client):
    res = flask_client.get("/api/profiles")
    assert res.status_code == 200
    data = res.get_json()
    assert "detector_improvement_v1_profiles" in data
    assert "balanced" in data["detector_improvement_v1_profiles"]


def test_api_demo_samples_endpoint(flask_client):
    res = flask_client.get("/api/demo_samples")
    assert res.status_code == 200
    data = res.get_json()
    assert len(data["samples"]) >= 3
    sample_ids = [s["id"] for s in data["samples"]]
    assert "gunshot_positive" in sample_ids
    assert "fireworks_distractor" in sample_ids
    assert "urban_ambient" in sample_ids


def test_api_detect_with_improvement_v1(flask_client):
    audio_sig = np.random.randn(16000).astype(np.float32) * 0.02
    bio = io.BytesIO()
    sf.write(bio, audio_sig, 16000, format="WAV")
    bio.seek(0)

    res = flask_client.post(
        "/api/detect",
        data={
            "audio": (bio, "test_audio.wav"),
            "detector_version": "detector_improvement_v1",
            "profile": "balanced"
        }
    )
    assert res.status_code == 200
    data = res.get_json()
    assert data["detector_version"] == "detector_improvement_v1"
    assert "is_gunshot" in data
    assert "inference_latency_ms" in data


def test_api_stream_window_with_improvement_v1(flask_client):
    chunk = np.random.randn(7680).astype(np.float32) * 0.02
    bio = io.BytesIO()
    sf.write(bio, chunk, 16000, format="WAV")
    bio.seek(0)

    res = flask_client.post(
        "/api/stream_window",
        data={
            "audio": (bio, "chunk.wav"),
            "session_id": "test_pytest_session",
            "detector_version": "detector_improvement_v1",
            "profile": "balanced"
        }
    )
    assert res.status_code == 200
    data = res.get_json()
    assert "score" in data
    assert "crest_factor_db" in data
    assert "latency_ms" in data


def test_api_stream_reset(flask_client):
    res = flask_client.post("/api/stream/reset", data={"session_id": "test_pytest_session"})
    assert res.status_code == 200
    assert res.get_json()["status"] == "ok"


# ==============================================================================
# 5. Benchmark Output Artifacts Integrity Tests
# ==============================================================================

def test_benchmark_csvs_exist_and_non_empty():
    pred_file = EXP_DIR / "recording_level_predictions.csv"
    base_file = EXP_DIR / "baseline_results.csv"
    exp_file = EXP_DIR / "experimental_results.csv"

    assert pred_file.exists(), "recording_level_predictions.csv must exist."
    assert base_file.exists(), "baseline_results.csv must exist."
    assert exp_file.exists(), "experimental_results.csv must exist."

    import pandas as pd
    df_pred = pd.read_csv(pred_file)
    assert len(df_pred) == 368, f"Expected 368 recordings in predictions, got {len(df_pred)}"

    df_base = pd.read_csv(base_file)
    assert len(df_base) == 2, "Expected 2 baseline detectors (Phase 14 & Phase 36)"

    df_exp = pd.read_csv(exp_file)
    assert len(df_exp) == 3, "Expected 3 experimental profiles (Balanced, Precision, Sensitivity)"

    # Verify key quantitative improvement: fireworks false alarm reduction vs Phase 36
    v1_bal = df_exp[df_exp["detector_id"] == "v1_balanced"].iloc[0]
    p36 = df_base[df_base["detector_id"] == "phase36"].iloc[0]
    p14 = df_base[df_base["detector_id"] == "phase14"].iloc[0]

    assert v1_bal["fireworks_triggers_count"] < p36["fireworks_triggers_count"], "V1 must reduce fireworks false alarms vs Phase 36"
    assert v1_bal["tp_duplicate_alerts"] < p14["tp_duplicate_alerts"], "V1 must reduce duplicate alerts vs Phase 14"
