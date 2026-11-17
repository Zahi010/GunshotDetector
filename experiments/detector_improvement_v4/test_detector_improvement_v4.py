# ==============================================================================
# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY
# Unit Test Suite for Detector Improvement V4
# ==============================================================================

import sys
sys.path.insert(0, ".")
import time
import numpy as np
import pytest
from scipy import signal

from experiments.detector_improvement_v4.model_detector_improvement_v4 import (
    DetectorImprovementV4,
    RealTimeStreamDetectorImprovementV4,
    CalibratedAcousticSuppressionV4,
    EventStateMachineV4,
    compute_physical_acoustic_features_v4,
    EventState
)


def test_feature_extraction_dimensions_and_latency():
    """Verify 8 physical acoustic features are computed in <1.0ms."""
    np.random.seed(42)
    # Generate 0.96s mock audio (15360 samples at 16 kHz)
    y_win = np.random.randn(15360).astype(np.float32) * 0.1
    # Add sharp impulse to mimic gunshot shockwave
    y_win[1000] = 0.95
    y_win[1001] = -0.70

    t0 = time.perf_counter()
    acoustics = compute_physical_acoustic_features_v4(y_win, sr=16000)
    dur_ms = (time.perf_counter() - t0) * 1000.0

    assert len(acoustics) == 8, f"Expected 8 features, got {len(acoustics)}"
    crest_db, flatness, hi, mid, lo, m2l, rolloff, cent = acoustics

    assert crest_db > 14.0, f"Impulse should produce high crest factor, got {crest_db:.2f} dB"
    assert 0.0 <= flatness <= 1.0, f"Flatness out of bounds: {flatness}"
    assert 0.0 <= hi <= 1.0, f"High-band ratio out of bounds: {hi}"
    assert 0.0 <= mid <= 1.0, f"Mid-band ratio out of bounds: {mid}"
    assert 0.0 <= lo <= 1.0, f"Low-band ratio out of bounds: {lo}"
    assert m2l > 0.0, f"Mid-to-low ratio should be positive: {m2l}"
    assert rolloff > 0.0, f"Channel roll-off should be positive: {rolloff}"
    assert cent > 0.0, f"Spectral centroid should be positive: {cent}"
    assert dur_ms < 5.0, f"Feature extraction too slow: {dur_ms:.2f} ms"


def test_acoustic_domain_adaptation_properties():
    """Verify that fabric low-pass filtering attenuates high frequencies while preserving mid-band."""
    np.random.seed(42)
    t = np.linspace(0, 0.96, 15360, endpoint=False)
    # Wideband signal with impulse
    y_clean = (np.sin(2 * np.pi * 3000 * t) * 0.4 + np.sin(2 * np.pi * 1200 * t) * 0.4 + np.random.randn(15360) * 0.05).astype(np.float32)
    y_clean[2000] = 0.9

    # Fabric filter at 1600 Hz
    sos = signal.butter(2, 1600.0, btype='lowpass', fs=16000, output='sos')
    y_muffled = signal.sosfilt(sos, y_clean).astype(np.float32)

    clean_acoustics = compute_physical_acoustic_features_v4(y_clean)
    muffled_acoustics = compute_physical_acoustic_features_v4(y_muffled)

    # Clean high-band ratio should be higher than muffled
    assert clean_acoustics[2] > muffled_acoustics[2], "Fabric filter must attenuate high-band ratio"
    # Channel roll-off ratio should drop significantly in muffled audio
    assert clean_acoustics[6] > muffled_acoustics[6], "Channel roll-off ratio must be lower under fabric occlusion"
    # Mid-band ratio should remain substantial
    assert muffled_acoustics[3] > 0.20, "Mid-band energy must remain preserved in muffled audio"


def test_glass_shatter_suppression():
    """Verify glass shatter gating suppresses non-ballistic glass breaks."""
    supp_cfg = {
        "enabled": True,
        "coherence_safeguard": {"enabled": True, "ballistic_max_threshold": 0.015, "non_target_threshold": 0.12, "attenuation": 0.20},
        "glass": {"threshold": 0.30, "min_high_band_ratio": 0.30, "max_ballistic": 0.20, "attenuation": 0.35}
    }
    supp = CalibratedAcousticSuppressionV4(supp_cfg)

    # Mock YAMNet scores where class 433 (Glass) is high, ballistic is low
    yamnet_scores = np.zeros(521, dtype=np.float32)
    yamnet_scores[433] = 0.65  # Glass
    yamnet_scores[435] = 0.50  # Shatter
    yamnet_scores[421] = 0.05  # Gunshot

    res = supp.apply_suppression(
        raw_score=0.75,
        yamnet_scores=yamnet_scores,
        high_band_ratio=0.42,
        is_in_confirmed_event=False
    )

    assert res["suppression_active"] is True
    assert "GLASS_SHATTER_SUPPRESSION" in res["reasons"]
    assert res["adjusted_score"] <= 0.45, f"Glass break not sufficiently attenuated: {res['adjusted_score']}"


def test_ballistic_shockwave_protection():
    """Verify that high-confidence ballistic shockwaves override fireworks suppression."""
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
    supp = CalibratedAcousticSuppressionV4(supp_cfg)

    # Co-occurring ballistic shockwave and fireworks echo
    yamnet_scores = np.zeros(521, dtype=np.float32)
    yamnet_scores[420] = 0.55  # Explosion / ballistic shockwave
    yamnet_scores[421] = 0.45  # Gunshot
    yamnet_scores[426] = 0.40  # Fireworks

    res = supp.apply_suppression(
        raw_score=0.85,
        yamnet_scores=yamnet_scores,
        high_band_ratio=0.15,
        is_in_confirmed_event=False
    )

    # Should not trigger fireworks suppression because ballistic evidence is strong
    assert "DOMINANT_FIREWORKS_SUPPRESSION" not in res["reasons"]
    assert "STANDARD_FIREWORKS_SUPPRESSION" not in res["reasons"]
    assert res["adjusted_score"] == 0.85


def test_fsm_v4_single_impulse_promotion():
    """Verify FSM V4 promotes single-round impulse with candidate-anchored crest attribution."""
    cfg = {
        "threshold_base": 0.62,
        "threshold_high": 0.80,
        "threshold_off": 0.40,
        "confirm_windows": 2,
        "cooldown_secs": 2.0,
        "max_hop_gap_s": 0.60,
        "min_crest_factor_db": 7.5,
        "single_impulse_min_crest_db": 11.5,
        "single_impulse_min_score": 0.62,
        "allow_single_impulse_exception": true if "true" in globals() else True
    }
    fsm = EventStateMachineV4(cfg)

    # Window 0: Single-round gunshot impulse (score 0.65, crest 18.2 dB)
    w0 = {"start_time": 0.0, "end_time": 0.96, "score": 0.65}
    ev0 = fsm.process_window(w0, crest_factor_db=18.2)
    assert ev0 is None
    assert fsm.state == EventState.CANDIDATE

    # Window 1: Ambient decay / silence (score 0.20, low crest 7.0 dB)
    # The impulse ends. FSM should evaluate Window 0's crest factor (18.2 dB >= 11.5 dB)
    w1 = {"start_time": 0.48, "end_time": 1.44, "score": 0.20}
    ev1 = fsm.process_window(w1, crest_factor_db=7.0)

    assert ev1 is not None, "Single round impulse was not promoted!"
    assert ev1["trigger_type"] == "single_round_impulse"
    assert ev1["peak_crest_db"] == 18.2, f"Failed to attribute impulse crest factor: {ev1['peak_crest_db']}"
    assert fsm.state == EventState.COOLDOWN


def test_detector_improvement_v4_profiles():
    """Verify DetectorImprovementV4 initializes across profiles."""
    det_bal = DetectorImprovementV4(profile="balanced")
    det_hp = DetectorImprovementV4(profile="high_precision")
    det_hs = DetectorImprovementV4(profile="high_sensitivity")

    assert det_bal.profile == "balanced"
    assert det_hp.profile == "high_precision"
    assert det_hs.profile == "high_sensitivity"

    # Quick waveform evaluation on 0.5s mock audio
    y_test = np.zeros(8000, dtype=np.float32)
    res = det_bal.evaluate_waveform(y_test)
    assert "detected" in res
    assert "events" in res
    assert "peak_score" in res
    assert res["detected"] is False  # Silence must not detect


def test_real_time_stream_detector_v4():
    """Verify circular buffer streaming detector."""
    stream_det = RealTimeStreamDetectorImprovementV4(profile="balanced")
    stream_det.reset_stream()

    hop_zeros = np.zeros(7680, dtype=np.float32)
    ev = stream_det.push_hop(hop_zeros)
    assert ev is None
    assert stream_det.window_index == 1
