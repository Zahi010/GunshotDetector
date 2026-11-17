# ==============================================================================
# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY
#
# Uncertified acoustic research software. Never deploy for autonomous emergency
# dispatch, tactical police response, active-shooter alerting, automated evacuation,
# lockdown, or life-critical physical security. Safe recorded audio playback only;
# no live-fire testing.
# ==============================================================================

import sys
import pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

import json
import pytest
import numpy as np

from experiments.detector_improvement_v3.model_detector_improvement_v3 import (
    extract_fast_acoustics,
    CalibratedAcousticSuppressionV3,
    EventStateMachineV3,
    DetectorImprovementV3,
    RealTimeStreamDetectorImprovementV3
)


def test_v3_config_integrity():
    cfg_path = pathlib.Path("experiments/detector_improvement_v3/config_improvement_v3.json")
    assert cfg_path.exists(), "config_improvement_v3.json must exist"

    with open(cfg_path, "r", encoding="utf-8") as f:
        cfg = json.load(f)

    assert "RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY" in cfg["system_designation"]
    assert "Uncertified acoustic research software" in cfg["disclaimer"]
    assert cfg["branch_identifier"] == "DETECTOR_IMPROVEMENT_V3"
    assert "balanced" in cfg["profiles"]
    assert "high_precision" in cfg["profiles"]
    assert "high_sensitivity" in cfg["profiles"]
    assert cfg["dsp"]["target_sample_rate"] == 16000
    assert cfg["dsp"]["window_size_samples"] == 15360


def test_v3_fast_acoustics():
    # Synthetic impulse (high crest, high high-frequency ratio)
    impulse = np.zeros(15360, dtype=np.float32)
    impulse[1000] = 1.0
    crest, flat, hi, lo, cent = extract_fast_acoustics(impulse, sr=16000)
    assert crest > 20.0, "Impulse crest factor should be > 20 dB"
    assert hi > 0.05, "Impulse should contain high frequency components"

    # White noise (high spectral flatness)
    np.random.seed(42)
    noise = np.random.randn(15360).astype(np.float32) * 0.1
    crest_n, flat_n, hi_n, lo_n, cent_n = extract_fast_acoustics(noise, sr=16000)
    assert flat_n > 0.30, "White noise should have high spectral flatness"

    # Pure low-frequency sine wave (low centroid, low flatness)
    t = np.linspace(0, 0.96, 15360, endpoint=False)
    sine = np.sin(2 * np.pi * 100 * t).astype(np.float32)
    crest_s, flat_s, hi_s, lo_s, cent_s = extract_fast_acoustics(sine, sr=16000)
    assert flat_s < 0.05, "Pure sine wave should have low spectral flatness"
    assert lo_s > 0.80, "100 Hz sine wave should concentrate energy in low band"


def test_v3_suppression_ballistic_override():
    supp = CalibratedAcousticSuppressionV3({
        "enabled": True,
        "fireworks": {
            "dominant_threshold": 0.40,
            "dominant_ratio": 1.5,
            "dominant_gun_max": 0.25,
            "dominant_attenuation": 0.30,
            "standard_threshold": 0.30,
            "standard_ratio": 1.5,
            "standard_gun_max": 0.12,
            "standard_attenuation": 0.35,
            "ballistic_override_threshold": 0.45
        }
    })

    # Case 1: Pure fireworks (ballistic score low, fireworks score high)
    ys_fw = np.zeros(521, dtype=np.float32)
    ys_fw[426] = 0.85 # Fireworks
    ys_fw[421] = 0.05 # Gunshot
    res_fw = supp.apply_suppression(raw_score=0.80, yamnet_scores=ys_fw)
    assert res_fw["suppression_active"] is True
    assert res_fw["suppression_category"] == "fireworks_dominant"
    assert res_fw["adjusted_score"] < 0.30

    # Case 2: Gunshot shockwave with fireworks ambiguity (ballistic score high)
    ys_gun = np.zeros(521, dtype=np.float32)
    ys_gun[420] = 0.85 # Explosion / Ballistic
    ys_gun[426] = 0.80 # Fireworks mimic
    ys_gun[421] = 0.05
    res_gun = supp.apply_suppression(raw_score=0.85, yamnet_scores=ys_gun)
    assert res_gun["suppression_active"] is False, "Ballistic override should protect authentic explosive blast"
    assert res_gun["adjusted_score"] == 0.85


def test_v3_event_state_machine():
    fsm = EventStateMachineV3(
        threshold_base=0.68,
        threshold_high=0.83,
        threshold_off=0.43,
        confirm_windows=2,
        cooldown_secs=1.5,
        min_crest_factor_db=8.0,
        single_win_min_crest_db=10.5,
        allow_single_impulse_exception=True,
        single_impulse_min_score=0.68,
        single_impulse_min_crest_db=8.5
    )

    # Window 0: Background
    ev0 = fsm.process_window({"start_time": 0.0, "end_time": 0.96, "score": 0.20}, crest_factor_db=6.0)
    assert ev0 is None
    assert fsm.state.name == "IDLE"

    # Window 1: High-impulse candidate (Gunshot blast)
    ev1 = fsm.process_window({"start_time": 0.48, "end_time": 1.44, "score": 0.78}, crest_factor_db=14.0)
    assert ev1 is None
    assert fsm.state.name == "CANDIDATE"

    # Window 2: Quick decay (reverberation drops below threshold_base)
    # Single-impulse exception should promote Window 1 to CONFIRMED and emit event
    ev2 = fsm.process_window({"start_time": 0.96, "end_time": 1.92, "score": 0.35}, crest_factor_db=7.0)
    assert ev2 is not None, "Single-impulse exception must emit confirmed event upon decay"
    assert ev2["peak_score"] >= 0.78
    assert fsm.state.name == "COOLDOWN"

    # Window 3: Refractory cooldown prevents duplicate trigger
    ev3 = fsm.process_window({"start_time": 1.44, "end_time": 2.40, "score": 0.90}, crest_factor_db=15.0)
    assert ev3 is None, "Cooldown must block duplicate trigger within refractory window"


def test_v3_detector_instantiation_and_silence():
    det = DetectorImprovementV3(profile="balanced")
    assert det.profile_name == "balanced"

    # Evaluate pure silence
    silence = np.zeros(16000 * 2, dtype=np.float32)
    res = det.evaluate_waveform(silence)
    assert res["detected"] is False
    assert res["event_count"] == 0
    assert len(res["windows"]) > 0
    assert res["peak_score"] < 0.20


def test_v3_realtime_stream_detector():
    events_received = []

    def callback(ev):
        events_received.append(ev)

    streamer = RealTimeStreamDetectorImprovementV3(profile="balanced", alert_callback=callback)

    # Ingest 3 chunks of 8000 samples (silence)
    chunk = np.zeros(8000, dtype=np.float32)
    for _ in range(3):
        emitted = streamer.ingest_audio(chunk)
        assert len(emitted) == 0

    assert streamer.total_windows_processed >= 1
    assert len(events_received) == 0
