"""
Unit Test Suite for Detector Improvement V6
RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY
"""

import sys, os, pathlib
sys.path.insert(0, "E:/gunshot/gunshot")
os.chdir("E:/gunshot/gunshot")

import pytest
import numpy as np

from experiments.detector_improvement_v6.model_detector_improvement_v6 import (
    compute_physical_acoustic_features_v6,
    ConditionEstimatorV6,
    CalibratedSemanticSuppressionV6,
    ConditionAdaptiveFSMV6,
    DetectorImprovementV6,
    OperatingMode,
    EventState
)

class TestDetectorImprovementV6:

    def test_01_silence_energy_floor_gate(self):
        """Test that pure digital silence returns 0.0 adjusted score without tree leaf traversal."""
        supp_cfg = {
            "ballistic_coherence": {"enabled": True, "max_pure_gun": 0.08, "max_ballistic": 0.10, "attenuation": 0.20}
        }
        supp = CalibratedSemanticSuppressionV6(supp_cfg)
        
        # Test digital zero
        zero_win = np.zeros(15360, dtype=np.float32)
        acoustics = compute_physical_acoustic_features_v6(zero_win)
        res = supp.apply_suppression(0.9853, {}, acoustics)
        assert res["adjusted_score"] == 0.0
        assert res["suppressed"] is True
        assert res["category"] == "silence_gate"

        # Test sub-threshold noise (RMS < 0.001)
        quiet_win = np.random.uniform(-0.0001, 0.0001, 15360).astype(np.float32)
        acoustics_q = compute_physical_acoustic_features_v6(quiet_win)
        res_q = supp.apply_suppression(0.85, {}, acoustics_q)
        assert res_q["adjusted_score"] == 0.0

    def test_02_condition_estimator_anti_chatter(self):
        """Test that condition estimator suppresses half-second chatter and requires hysteresis."""
        ce = ConditionEstimatorV6(alpha=0.20, hysteresis_occluded=3, hysteresis_clear=2, hysteresis_rumble=2)
        
        # Initial mode is UNKNOWN
        assert ce.current_mode == OperatingMode.UNKNOWN

        # Feed 1 window of occluded evidence -> should NOT transition yet
        mode, _, did_t = ce.update(rolloff=0.08, high_ratio=0.03, mid_ratio=0.45, low_ratio=0.52, mid_to_low=0.86, time_s=0.48, window_idx=1)
        assert mode == OperatingMode.UNKNOWN
        assert did_t is False

        # Feed 2nd window of occluded evidence -> still UNKNOWN (needs 3)
        mode, _, did_t = ce.update(rolloff=0.08, high_ratio=0.03, mid_ratio=0.45, low_ratio=0.52, mid_to_low=0.86, time_s=0.96, window_idx=2)
        assert mode == OperatingMode.UNKNOWN
        assert did_t is False

        # Feed 3rd window of occluded evidence -> TRANSITIONS to DEGRADED_OCCLUDED
        mode, _, did_t = ce.update(rolloff=0.08, high_ratio=0.03, mid_ratio=0.45, low_ratio=0.52, mid_to_low=0.86, time_s=1.44, window_idx=3)
        assert mode == OperatingMode.DEGRADED_OCCLUDED
        assert did_t is True

        # Now feed 1 single window of low rumble -> should NOT instantly bounce back to UNKNOWN
        mode, _, did_t = ce.update(rolloff=0.08, high_ratio=0.03, mid_ratio=0.15, low_ratio=0.82, mid_to_low=0.18, time_s=1.92, window_idx=4)
        assert mode == OperatingMode.DEGRADED_OCCLUDED
        assert did_t is False

        # Feed 2nd window of low rumble -> NOW transitions to UNKNOWN
        mode, _, did_t = ce.update(rolloff=0.08, high_ratio=0.03, mid_ratio=0.15, low_ratio=0.82, mid_to_low=0.18, time_s=2.40, window_idx=5)
        assert mode == OperatingMode.UNKNOWN
        assert did_t is True

    def test_03_sub_bass_thud_and_automotive_backfire_suppression(self):
        """Test that sub-bass vehicle thuds are attenuated and denied single-impulse exception."""
        supp_cfg = {
            "sub_bass_thud": {
                "enabled": True, "min_low_ratio": 0.75, "max_high_ratio": 0.008,
                "max_centroid_hz": 450.0, "max_pure_gun": 0.20, "attenuation": 0.35
            }
        }
        supp = CalibratedSemanticSuppressionV6(supp_cfg)
        
        # Sub-bass thud acoustics: lo=0.85, hi=0.001, cent=260Hz, peak=0.05
        acoustics = (14.2, 0.001, 0.001, 0.149, 0.850, 0.175, 0.001, 260.0, 0.035, 0.05)
        # Low pure gun score (e.g. 0.10)
        yamnet = {421: 0.10, 420: 0.45, 424: 0.30}
        res = supp.apply_suppression(0.85, yamnet, acoustics)
        assert res["adjusted_score"] == pytest.approx(0.85 * 0.35, rel=1e-3)
        assert res["category"] == "sub_bass_thud"

        # Verify FSM denies single impulse exception for sub-bass thud
        policy = {
            "UNKNOWN": {
                "threshold_base": 0.70, "confirm_windows": 2, "single_impulse_min_crest_db": 13.5,
                "single_impulse_min_score": 0.70, "allow_single_impulse_exception": True
            }
        }
        fsm = ConditionAdaptiveFSMV6(policy)
        # Even with high score (0.75) and high crest (14.0dB), acoustics has hi < 0.005, cent < 450, peak < 0.15
        st, ev = fsm.step(0.75, 14.0, 0.48, acoustics, OperatingMode.UNKNOWN)
        assert ev is None # Denied!
        assert st == EventState.CANDIDATE # Placed in candidate pool for multi-window verification

    def test_04_cap_gun_pop_discrimination(self):
        """Test that cap gun mechanical pops without pure gunshots are attenuated."""
        supp_cfg = {
            "cap_gun_mechanical": {
                "enabled": True, "min_cap_gun": 0.35, "max_pure_gun": 0.28,
                "max_high_ratio": 0.010, "max_centroid_hz": 450.0, "attenuation": 0.35
            }
        }
        supp = CalibratedSemanticSuppressionV6(supp_cfg)
        acoustics = (14.5, 0.001, 0.0005, 0.160, 0.839, 0.190, 0.003, 310.0, 0.05, 0.18)
        # Cap gun = 0.60, pure gun = 0.15
        yamnet = {424: 0.60, 421: 0.15, 420: 0.30}
        res = supp.apply_suppression(0.90, yamnet, acoustics)
        assert res["adjusted_score"] == pytest.approx(0.90 * 0.35, rel=1e-3)
        assert res["category"] == "cap_gun_mechanical_thud"

    def test_05_ballistic_coherence_safeguard(self):
        """Test that non-ballistic transients (pure_gun < 0.08, bal_s < 0.10) are attenuated."""
        supp_cfg = {
            "ballistic_coherence": {
                "enabled": True, "max_pure_gun": 0.08, "max_ballistic": 0.10, "attenuation": 0.20
            }
        }
        supp = CalibratedSemanticSuppressionV6(supp_cfg)
        acoustics = (19.8, 0.05, 0.08, 0.55, 0.37, 1.48, 0.14, 1150.0, 0.04, 0.42)
        # Horn/screech with near-zero ballistic score
        yamnet = {362: 0.45, 406: 0.35, 421: 0.02, 420: 0.03}
        res = supp.apply_suppression(0.82, yamnet, acoustics)
        assert res["adjusted_score"] == pytest.approx(0.82 * 0.20, rel=1e-3)
        assert res["category"] == "ballistic_incoherence"

    def test_06_glass_shatter_and_thunder_suppression(self):
        """Test enhanced glass shatter and physical thunder suppression."""
        supp_cfg = {
            "glass_shatter": {"enabled": True, "threshold": 0.30, "min_high_band_ratio": 0.25, "gun_score_max": 0.20, "attenuation": 0.35},
            "thunder": {"enabled": True, "threshold": 0.20, "low_band_threshold": 0.65, "mid_to_low_max": 0.55, "gun_score_max": 0.15, "attenuation": 0.30}
        }
        supp = CalibratedSemanticSuppressionV6(supp_cfg)

        # Glass shatter
        acoustics_g = (21.5, 0.20, 0.45, 0.35, 0.20, 1.75, 1.28, 2800.0, 0.08, 0.60)
        yamnet_g = {433: 0.70, 434: 0.48, 421: 0.05}
        res_g = supp.apply_suppression(0.88, yamnet_g, acoustics_g)
        assert res_g["adjusted_score"] == pytest.approx(0.88 * 0.35, rel=1e-3)
        assert res_g["category"] == "glass_shatter"

        # Thunder with low-frequency rumble
        acoustics_t = (13.5, 0.005, 0.005, 0.10, 0.895, 0.11, 0.05, 180.0, 0.06, 0.35)
        yamnet_t = {280: 0.40, 421: 0.02, 420: 0.15}
        res_t = supp.apply_suppression(0.80, yamnet_t, acoustics_t)
        assert res_t["adjusted_score"] == pytest.approx(0.80 * 0.30, rel=1e-3)
        assert res_t["category"] == "thunder_rumble"

    def test_07_physical_features_computation(self):
        """Verify 10 physical DSP feature dimensions."""
        sr = 16000
        # Synthesize a pure 1 kHz tone
        t = np.linspace(0, 0.96, int(sr * 0.96), endpoint=False)
        y = 0.5 * np.sin(2 * np.pi * 1000 * t).astype(np.float32)
        crest, flat, hi, mid, lo, m2l, rolloff, cent, rms, peak = compute_physical_acoustic_features_v6(y, sr)
        
        assert crest > 2.5 and crest < 4.0 # Sine crest factor is ~3.01 dB
        assert mid > 0.90 # Almost all energy in mid band (500-2500 Hz)
        assert cent > 950 and cent < 1050 # Centroid around 1000 Hz
        assert rms > 0.30 and rms < 0.40
        assert peak > 0.49 and peak < 0.51

    def test_08_end_to_end_detector_evaluation(self):
        """Test full detector evaluation on synthesized impulses."""
        detector = DetectorImprovementV6()
        sr = 16000

        # Ambient silence -> 0 events
        silence = np.zeros(sr * 2, dtype=np.float32)
        res_silence = detector.evaluate_waveform(silence, sr)
        assert res_silence["detected"] is False
        assert res_silence["event_count"] == 0

        # Impulse simulating a gunshot
        t = np.linspace(0, 2.0, sr * 2, endpoint=False)
        # Background noise
        noise = np.random.normal(0, 0.01, len(t)).astype(np.float32)
        # Sharp explosive pulse at 0.5s
        impulse_len = int(sr * 0.05)
        t_imp = np.linspace(0, 0.05, impulse_len, endpoint=False)
        pulse = 0.8 * np.exp(-t_imp / 0.008) * np.sin(2 * np.pi * 1200 * t_imp)
        noise[int(sr * 0.5) : int(sr * 0.5) + impulse_len] += pulse.astype(np.float32)

        res_impulse = detector.evaluate_waveform(noise, sr)
        assert "detected" in res_impulse
        assert "dominant_mode" in res_impulse
