"""
Test Suite for Detector Improvement V2
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
import pandas as pd

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

EXP_DIR = REPO_ROOT / "experiments" / "detector_improvement_v2"
if str(EXP_DIR) not in sys.path:
    sys.path.insert(0, str(EXP_DIR))

import config
from app import app
from experiments.detector_improvement_v2.model_detector_improvement_v2 import (
    CalibratedAcousticSuppressionV2,
    EventStateMachineV2,
    DetectorImprovementV2,
    RealTimeStreamDetectorImprovementV2,
    YAMNET_CLASS_GUNSHOT,
    YAMNET_CLASS_FIREWORKS,
    YAMNET_CLASS_WIND,
    YAMNET_CLASS_HAMMER
)
from experiments.phase36.event_state_machine import EventState


@pytest.fixture
def flask_client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


# ==============================================================================
# 1. Configuration and Profile Initialization Tests
# ==============================================================================

def test_config_and_profiles_exist():
    config_file = EXP_DIR / "config_improvement_v2.json"
    assert config_file.exists(), "config_improvement_v2.json must exist."
    with open(config_file, "r", encoding="utf-8") as f:
        cfg = json.load(f)
    assert cfg["system_designation"] == "RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY"
    assert "balanced" in cfg["profiles"]
    assert "high_precision" in cfg["profiles"]
    assert "high_sensitivity" in cfg["profiles"]
    assert cfg["profiles"]["balanced"]["allow_single_impulse_exception"] is True


def test_detector_v2_initialization():
    for prof in ["balanced", "high_precision", "high_sensitivity"]:
        det = DetectorImprovementV2(profile=prof)
        assert det.profile == prof
        assert det.threshold_base > 0.0
        assert det.threshold_high > det.threshold_base
        assert det.threshold_off < det.threshold_base
        assert det.cooldown_secs >= 1.5
        assert det.single_impulse_min_score >= 0.75


# ==============================================================================
# 2. Semantic Suppression V2 Engine Tests
# ==============================================================================

def test_suppression_coherence_guard():
    supp_cfg = {
        "enabled": True,
        "coherence_safeguard": {
            "enabled": True,
            "ballistic_max_threshold": 0.015,
            "non_target_threshold": 0.12,
            "attenuation": 0.20
        }
    }
    engine = CalibratedAcousticSuppressionV2(supp_cfg)

    # Synthetic non-ballistic YAMNet vector (e.g. Speech active, zero ballistic)
    yamnet_vec = np.zeros(521, dtype=np.float32)
    yamnet_vec[0] = 0.35 # Speech (Class 0)
    # Ballistic classes are all 0.0

    res = engine.apply_suppression(0.85, yamnet_vec, is_in_confirmed_event=False)
    assert res["suppression_active"] is True
    assert res["suppression_category"] == "non_ballistic_coherence_rejection"
    assert res["adjusted_score"] == pytest.approx(0.85 * 0.20, abs=1e-3)


def test_suppression_two_tier_fireworks():
    supp_cfg = {
        "enabled": True,
        "fireworks": {
            "dominant_threshold": 0.45,
            "dominant_ratio": 1.8,
            "dominant_gun_max": 0.25,
            "dominant_attenuation": 0.30,
            "standard_threshold": 0.30,
            "standard_ratio": 1.5,
            "standard_gun_max": 0.12,
            "standard_attenuation": 0.35
        }
    }
    engine = CalibratedAcousticSuppressionV2(supp_cfg)

    # Dominant tier: fw = 0.65, gun = 0.18 (would leak in V1 because gun > 0.10)
    yamnet_vec = np.zeros(521, dtype=np.float32)
    yamnet_vec[YAMNET_CLASS_FIREWORKS] = 0.65
    yamnet_vec[YAMNET_CLASS_GUNSHOT] = 0.18

    res = engine.apply_suppression(0.90, yamnet_vec, is_in_confirmed_event=False)
    assert res["suppression_active"] is True
    assert res["suppression_category"] == "fireworks_dominant"
    assert res["adjusted_score"] == pytest.approx(0.90 * 0.30, abs=1e-3)


def test_suppression_wind_buffeting():
    supp_cfg = {
        "enabled": True,
        "wind_buffeting": {"threshold": 0.25, "ratio": 1.5, "attenuation": 0.25}
    }
    engine = CalibratedAcousticSuppressionV2(supp_cfg)

    yamnet_vec = np.zeros(521, dtype=np.float32)
    yamnet_vec[YAMNET_CLASS_WIND] = 0.40
    yamnet_vec[YAMNET_CLASS_GUNSHOT] = 0.01

    res = engine.apply_suppression(0.82, yamnet_vec, is_in_confirmed_event=False)
    assert res["suppression_active"] is True
    assert res["suppression_category"] == "wind_buffeting"
    assert res["adjusted_score"] == pytest.approx(0.82 * 0.25, abs=1e-3)


def test_suppression_mechanical_impact():
    supp_cfg = {
        "enabled": True,
        "mechanical_impact": {"threshold": 0.30, "ratio": 1.5, "gun_max": 0.20, "attenuation": 0.35}
    }
    engine = CalibratedAcousticSuppressionV2(supp_cfg)

    yamnet_vec = np.zeros(521, dtype=np.float32)
    yamnet_vec[YAMNET_CLASS_HAMMER] = 0.50
    yamnet_vec[YAMNET_CLASS_GUNSHOT] = 0.05

    res = engine.apply_suppression(0.84, yamnet_vec, is_in_confirmed_event=False)
    assert res["suppression_active"] is True
    assert res["suppression_category"] == "mechanical_impact"
    assert res["adjusted_score"] == pytest.approx(0.84 * 0.35, abs=1e-3)


def test_ballistic_protection_preserves_genuine_gunshots():
    supp_cfg = {
        "enabled": True,
        "coherence_safeguard": {"enabled": True, "ballistic_max_threshold": 0.015, "non_target_threshold": 0.12, "attenuation": 0.20},
        "fireworks": {
            "dominant_threshold": 0.45, "dominant_ratio": 1.8, "dominant_gun_max": 0.25, "dominant_attenuation": 0.30,
            "standard_threshold": 0.30, "standard_ratio": 1.5, "standard_gun_max": 0.12, "standard_attenuation": 0.35
        }
    }
    engine = CalibratedAcousticSuppressionV2(supp_cfg)

    # Genuine gunshot: high gunshot score (0.65) accompanied by fireworks class 0.40
    yamnet_vec = np.zeros(521, dtype=np.float32)
    yamnet_vec[YAMNET_CLASS_GUNSHOT] = 0.65
    yamnet_vec[YAMNET_CLASS_FIREWORKS] = 0.40

    res = engine.apply_suppression(0.88, yamnet_vec, is_in_confirmed_event=False)
    assert res["suppression_active"] is False, "Genuine gunshot with gun_score=0.65 must not be suppressed"
    assert res["adjusted_score"] == 0.88


# ==============================================================================
# 3. State Machine V2 and Single-Round Impulse Exception Tests
# ==============================================================================

def test_single_round_impulse_dispatch_on_decay():
    fsm = EventStateMachineV2(
        threshold_base=0.75,
        threshold_high=0.88,
        threshold_off=0.48,
        confirm_windows=2,
        cooldown_secs=2.0,
        allow_single_impulse_exception=True,
        single_impulse_min_score=0.82,
        single_impulse_min_crest_db=14.0,
        single_impulse_max_dur_sec=5.0
    )

    # Window 0: Genuine single gunshot impulse (score 0.84, crest 18 dB)
    win0 = {
        "window_index": 0, "start_time": 0.0, "end_time": 0.96,
        "score": 0.84, "raw_score": 0.84, "crest_factor_db": 18.0,
        "suppression_active": False
    }
    # Window 1: Fast decay (reverberation drops to 0.40)
    win1 = {
        "window_index": 1, "start_time": 0.48, "end_time": 1.44,
        "score": 0.40, "raw_score": 0.40, "crest_factor_db": 18.0,
        "suppression_active": False
    }

    fsm.process_window(win0, crest_factor_db=18.0, audio_duration_sec=2.5, total_windows_in_stream=4)
    assert fsm.state == EventState.CANDIDATE

    # Process decay window
    ev = fsm.process_window(win1, crest_factor_db=18.0, audio_duration_sec=2.5, total_windows_in_stream=4)
    assert ev is not None, "Candidate must be promoted under single_round_impulse upon decay"
    assert ev["dispatch_path"] == "single_round_impulse"
    assert fsm.state == EventState.COOLDOWN
    assert len(fsm.events_emitted) == 1


# ==============================================================================
# 4. Waveform Evaluation and Streaming Ring Buffer Tests
# ==============================================================================

def test_evaluate_waveform_clean_audio_v2():
    det = DetectorImprovementV2(profile="balanced")
    clean_audio = np.random.randn(16000).astype(np.float32) * 0.01
    res = det.evaluate_waveform(clean_audio)

    assert "duration_seconds" in res
    assert "crest_factor_db" in res
    assert "total_windows" in res
    assert res["detected"] is False
    assert len(res["events"]) == 0


def test_streaming_ring_buffer_chunk_processing_v2():
    stream_det = RealTimeStreamDetectorImprovementV2(profile="balanced")
    chunk_480ms = np.random.randn(7680).astype(np.float32) * 0.01

    alerts1 = stream_det.process_chunk(chunk_480ms)
    alerts2 = stream_det.process_chunk(chunk_480ms)
    alerts3 = stream_det.process_chunk(chunk_480ms)

    assert isinstance(alerts1, list)
    assert isinstance(alerts2, list)
    assert isinstance(alerts3, list)
    assert stream_det.stream_time_sec >= 0.96
    assert len(stream_det.chunk_latencies_ms) > 0


# ==============================================================================
# 5. Web Application Route Integration Tests
# ==============================================================================

def test_api_health_endpoint_v2(flask_client):
    res = flask_client.get("/api/health")
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "healthy"
    assert "detector_improvement_v2" in data["supported_detectors"]
    assert "detector_improvement_v2" in data["experimental_detectors"]


def test_api_status_endpoint_v2(flask_client):
    res = flask_client.get("/api/status")
    assert res.status_code == 200
    data = res.get_json()
    assert "detector_improvement_v2" in data["supported_versions"]
    assert "detector_improvement_v2_profiles" in data["architecture"]


def test_api_profiles_endpoint_v2(flask_client):
    res = flask_client.get("/api/profiles")
    assert res.status_code == 200
    data = res.get_json()
    assert "detector_improvement_v2_profiles" in data
    assert "balanced" in data["detector_improvement_v2_profiles"]


def test_api_detect_with_improvement_v2(flask_client):
    audio_sig = np.random.randn(16000).astype(np.float32) * 0.02
    bio = io.BytesIO()
    sf.write(bio, audio_sig, 16000, format="WAV")
    bio.seek(0)

    res = flask_client.post(
        "/api/detect",
        data={
            "audio": (bio, "test_audio.wav"),
            "detector_version": "detector_improvement_v2",
            "profile": "balanced"
        }
    )
    assert res.status_code == 200
    data = res.get_json()
    assert data["detector_version"] == "detector_improvement_v2"
    assert "is_gunshot" in data
    assert "inference_latency_ms" in data


def test_api_stream_window_with_improvement_v2(flask_client):
    chunk = np.random.randn(7680).astype(np.float32) * 0.02
    bio = io.BytesIO()
    sf.write(bio, chunk, 16000, format="WAV")
    bio.seek(0)

    res = flask_client.post(
        "/api/stream_window",
        data={
            "audio": (bio, "chunk.wav"),
            "session_id": "test_pytest_session_v2",
            "detector_version": "detector_improvement_v2",
            "profile": "balanced"
        }
    )
    assert res.status_code == 200
    data = res.get_json()
    assert "score" in data
    assert "crest_factor_db" in data
    assert "latency_ms" in data


# ==============================================================================
# 6. Benchmark Output Artifacts Integrity Tests
# ==============================================================================

def test_benchmark_v2_csvs_exist_and_verify_improvements():
    pred_file = EXP_DIR / "recording_level_predictions.csv"
    dev_file = EXP_DIR / "development_results.csv"
    holdout_file = EXP_DIR / "holdout_results.csv"

    assert pred_file.exists(), "recording_level_predictions.csv must exist."
    assert dev_file.exists(), "development_results.csv must exist."
    assert holdout_file.exists(), "holdout_results.csv must exist."

    df_pred = pd.read_csv(pred_file)
    assert len(df_pred) == 368, f"Expected 368 recordings in predictions, got {len(df_pred)}"

    # Check partitions
    assert set(df_pred["v2_partition"].unique()) == {"development", "locked_holdout"}
    assert (df_pred["v2_partition"] == "development").sum() == 218
    assert (df_pred["v2_partition"] == "locked_holdout").sum() == 150

    # Macro improvements
    pos = df_pred[df_pred["ground_truth_gunshot"] == 1]
    fw = df_pred[df_pred["sub_category"] == "DISTRACTOR_FIREWORKS"]
    cont = df_pred[df_pred["sub_category"] == "LONG_AMBIENT_STREAM"]

    v2_pos_recall = pos["v2_detected"].sum()
    v1_pos_recall = pos["v1_detected"].sum()
    assert v2_pos_recall >= v1_pos_recall, "V2 positive gunshot recall must be >= V1"

    v2_fw_fps = fw["v2_detected"].sum()
    v1_fw_fps = fw["v1_detected"].sum()
    assert v2_fw_fps < v1_fw_fps, "V2 must reduce fireworks false alarms vs V1"

    v2_cont_evs = cont["v2_event_count"].sum()
    v1_cont_evs = cont["v1_event_count"].sum()
    assert v2_cont_evs < v1_cont_evs, "V2 must reduce continuous background false alert events vs V1"

