"""
Unit Test Suite for Detector Improvement V7
RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY
"""

import sys
import os
import pathlib
sys.path.insert(0, "E:/gunshot/gunshot")
os.chdir("E:/gunshot/gunshot")

import pytest
import numpy as np

from experiments.detector_improvement_v7.model_detector_improvement_v7 import (
    compute_physical_acoustic_features_v7,
    ConditionEstimatorV7,
    CalibratedSemanticSuppressionV7,
    ConditionAdaptiveFSMV7,
    DetectorImprovementV7,
    OperatingMode,
    EventState
)


class TestDetectorImprovementV7:

    def test_01_silence_energy_floor_gate(self):
        """Test that pure digital silence returns 0.0 adjusted score without tree leaf traversal."""
        supp_cfg = {
            "ballistic_coherence": {"enabled": True, "max_pure_gun": 0.08, "max_ballistic": 0.10, "attenuation": 0.20}
        }
        supp = CalibratedSemanticSuppressionV7(supp_cfg)

        # Digital zero
        zero_win = np.zeros(15360, dtype=np.float32)
        acoustics = compute_physical_acoustic_features_v7(zero_win)
        res = supp.apply_suppression(0.9853, {}, acoustics)
        assert res["adjusted_score"] == 0.0
        assert res["suppressed"] is True
        assert res["category"] == "zero_energy_silence"

        # Sub-threshold noise
        quiet_win = np.random.uniform(-0.0001, 0.0001, 15360).astype(np.float32)
        acoustics_q = compute_physical_acoustic_features_v7(quiet_win)
        res_q = supp.apply_suppression(0.85, {}, acoustics_q)
        assert res_q["adjusted_score"] == 0.0

    def test_02_condition_estimator_anti_chatter(self):
        """Test that condition estimator suppresses half-second chatter and requires hysteresis."""
        ce = ConditionEstimatorV7(alpha=0.20, hysteresis_occluded=3, hysteresis_clear=2, hysteresis_rumble=2)

        assert ce.current_mode == OperatingMode.UNKNOWN

        # 1 window of occluded evidence -> still UNKNOWN
        mode, _, did_t = ce.update(rolloff=0.08, high_ratio=0.03, mid_ratio=0.45, low_ratio=0.52, mid_to_low=0.86, time_s=0.48, window_idx=1)
        assert mode == OperatingMode.UNKNOWN
        assert did_t is False

        # 2nd window -> still UNKNOWN
        mode, _, did_t = ce.update(rolloff=0.08, high_ratio=0.03, mid_ratio=0.45, low_ratio=0.52, mid_to_low=0.86, time_s=0.96, window_idx=2)
        assert mode == OperatingMode.UNKNOWN
        assert did_t is False

        # 3rd window -> TRANSITIONS to DEGRADED_OCCLUDED
        mode, _, did_t = ce.update(rolloff=0.08, high_ratio=0.03, mid_ratio=0.45, low_ratio=0.52, mid_to_low=0.86, time_s=1.44, window_idx=3)
        assert mode == OperatingMode.DEGRADED_OCCLUDED
        assert did_t is True

        # 1 window of rumble -> does NOT instantly bounce
        mode, _, did_t = ce.update(rolloff=0.08, high_ratio=0.03, mid_ratio=0.15, low_ratio=0.82, mid_to_low=0.18, time_s=1.92, window_idx=4)
        assert mode == OperatingMode.DEGRADED_OCCLUDED
        assert did_t is False

        # 2nd window of rumble -> transitions to UNKNOWN
        mode, _, did_t = ce.update(rolloff=0.08, high_ratio=0.03, mid_ratio=0.15, low_ratio=0.82, mid_to_low=0.18, time_s=2.40, window_idx=5)
        assert mode == OperatingMode.UNKNOWN
        assert did_t is True

    def test_03_ballistic_shockwave_pyrotechnic_override(self):
        """Test that gunshot with ballistic shockwave is exempt from pyrotechnic attenuation."""
        supp_cfg = {
            "fireworks": {
                "enabled": True, "dominant_threshold": 0.45, "dominant_ratio": 1.8, "dominant_attenuation": 0.15,
                "ballistic_override_threshold": 0.40, "ballistic_override_ratio": 0.85
            }
        }
        supp = CalibratedSemanticSuppressionV7(supp_cfg)
        acoustics = (18.5, 0.05, 0.12, 0.55, 0.33, 1.66, 0.22, 1450.0, 0.08, 0.55)

        # Case A: Pure fireworks (fw_s=0.60, bal_s=0.20, pure_gun=0.05) -> Suppressed
        yamnet_fw = {426: 0.60, 420: 0.20, 421: 0.05}
        res_fw = supp.apply_suppression(0.92, yamnet_fw, acoustics)
        assert res_fw["suppressed"] is True
        assert res_fw["adjusted_score"] == pytest.approx(0.92 * 0.15, rel=1e-3)
        assert res_fw["category"] == "fireworks_dominant"

        # Case B: Field gunshot (fw_s=0.55, bal_s=0.75, pure_gun=0.25) -> OVERRIDE! (bal_s >= 0.40 and bal_s >= 0.85 * fw_s)
        yamnet_gun = {426: 0.55, 420: 0.75, 421: 0.25}
        res_gun = supp.apply_suppression(0.95, yamnet_gun, acoustics)
        assert res_gun["suppressed"] is False
        assert res_gun["adjusted_score"] == 0.95
        assert res_gun["category"] is None

    def test_04_thunder_reverberation_protection(self):
        """Test that reverberant gunshots are protected from false thunder attenuation."""
        supp_cfg = {
            "thunder": {
                "enabled": True, "threshold": 0.20, "low_band_threshold": 0.65,
                "mid_to_low_max": 0.55, "gun_score_max": 0.15, "ballistic_shockwave_max": 0.20,
                "attenuation": 0.30
            }
        }
        supp = CalibratedSemanticSuppressionV7(supp_cfg)
        # Reverberant tail acoustics: lo=0.72, m2l=0.38
        acoustics = (14.2, 0.005, 0.005, 0.27, 0.72, 0.38, 0.02, 380.0, 0.05, 0.22)

        # Case A: Real thunder (pure_gun=0.02, bal_s=0.05, thun=0.50) -> Suppressed
        yamnet_thun = {280: 0.50, 421: 0.02, 420: 0.05}
        res_thun = supp.apply_suppression(0.80, yamnet_thun, acoustics)
        assert res_thun["suppressed"] is True
        assert res_thun["adjusted_score"] == pytest.approx(0.80 * 0.30, rel=1e-3)
        assert res_thun["category"] == "thunder_rumble"

        # Case B: Reverberant gunshot (pure_gun=0.10, bal_s=0.65) -> PROTECTED by bal_s >= 0.20
        yamnet_reverb_gun = {280: 0.00, 421: 0.10, 420: 0.65}
        res_reverb = supp.apply_suppression(0.88, yamnet_reverb_gun, acoustics)
        assert res_reverb["suppressed"] is False
        assert res_reverb["adjusted_score"] == 0.88

    def test_05_sub_bass_automotive_backfire_suppression(self):
        """Test that automotive backfires with cap gun pops and heavy low frequencies are attenuated."""
        supp_cfg = {
            "sub_bass_thud": {
                "enabled": True, "min_low_ratio": 0.70, "max_high_ratio": 0.008,
                "max_centroid_hz": 450.0, "min_cap_gun": 0.35, "cap_to_pure_ratio": 1.5,
                "max_pure_gun": 0.20, "attenuation": 0.25
            }
        }
        supp = CalibratedSemanticSuppressionV7(supp_cfg)
        # Backfire acoustics: lo=0.81, hi=0.001, cent=696 Hz (matches Window 28 in Block 80)
        acoustics = (14.8, 0.001, 0.001, 0.18, 0.81, 0.22, 0.005, 696.0, 0.08, 0.46)
        # Cap gun=0.55, pure_gun=0.23 (cap_gun >= pure_gun * 1.5)
        yamnet_backfire = {424: 0.55, 421: 0.23, 420: 0.25}
        res = supp.apply_suppression(0.82, yamnet_backfire, acoustics)
        assert res["suppressed"] is True
        assert res["adjusted_score"] == pytest.approx(0.82 * 0.25, rel=1e-3)
        assert res["category"] == "sub_bass_thud"

    def test_06_high_confidence_single_impulse_adaptation(self):
        """Test that high confidence (score >= 0.85) in UNKNOWN mode allows crest >= 11.5 dB."""
        policy = {
            "UNKNOWN": {
                "threshold_base": 0.70, "threshold_high": 0.85, "confirm_windows": 2,
                "single_impulse_min_crest_db": 13.5, "single_impulse_high_conf_crest_db": 11.5,
                "single_impulse_min_score": 0.70, "allow_single_impulse_exception": True
            }
        }
        fsm = ConditionAdaptiveFSMV7(policy)
        acoustics_clean = (12.2, 0.02, 0.05, 0.45, 0.50, 0.90, 0.10, 850.0, 0.08, 0.35)

        # Standard confidence (0.75) with crest 12.2 dB -> Denied single impulse (requires 13.5)
        st, ev = fsm.step(0.75, 12.2, 0.48, acoustics_clean, OperatingMode.UNKNOWN)
        assert ev is None
        assert st == EventState.CANDIDATE

        # Reset and test High confidence (0.91) with crest 12.2 dB -> Confirmed! (allows crest >= 11.5)
        fsm.reset()
        st2, ev2 = fsm.step(0.91, 12.2, 0.48, acoustics_clean, OperatingMode.UNKNOWN)
        assert ev2 is not None
        assert st2 == EventState.CONFIRMED
        assert ev2["trigger_type"] == "single_impulse_exception"

    def test_07_ballistic_coherence_saturation_safeguard(self):
        """Test that saturated / clipped high amplitude transients use saturation threshold."""
        supp_cfg = {
            "ballistic_coherence": {
                "enabled": True, "max_pure_gun": 0.08, "max_ballistic": 0.10,
                "saturation_pure_gun": 0.04, "saturation_ballistic": 0.04,
                "attenuation": 0.20
            }
        }
        supp = CalibratedSemanticSuppressionV7(supp_cfg)
        # Saturated audio: peak = 0.45, crest = 16.5 dB
        acoustics_sat = (16.5, 0.05, 0.08, 0.55, 0.37, 1.48, 0.14, 1150.0, 0.10, 0.45)

        # If pure_gun = 0.06 and bal_s = 0.08:
        # Under standard threshold (0.08, 0.10), it would be suppressed.
        # Under saturation threshold (0.04, 0.04), it is NOT suppressed!
        yamnet_sat = {421: 0.06, 420: 0.08}
        res = supp.apply_suppression(0.78, yamnet_sat, acoustics_sat)
        assert res["suppressed"] is False
        assert res["adjusted_score"] == 0.78

    def test_08_physical_features_computation(self):
        """Verify 10 physical DSP feature dimensions."""
        sr = 16000
        t = np.linspace(0, 0.96, int(sr * 0.96), endpoint=False)
        y = 0.5 * np.sin(2 * np.pi * 1000 * t).astype(np.float32)
        crest, flat, hi, mid, lo, m2l, rolloff, cent, rms, peak = compute_physical_acoustic_features_v7(y, sr)

        assert crest > 2.5 and crest < 4.0
        assert mid > 0.90
        assert cent > 950 and cent < 1050
        assert rms > 0.30 and rms < 0.40
        assert peak > 0.49 and peak < 0.51

    def test_09_end_to_end_detector_evaluation(self):
        """Test full detector evaluation on synthetic waveforms."""
        detector = DetectorImprovementV7()
        sr = 16000

        # Silence
        silence = np.zeros(sr * 2, dtype=np.float32)
        res_silence = detector.evaluate_waveform(silence, sr)
        assert res_silence["detected"] is False
        assert res_silence["event_count"] == 0

        # Impulse
        t = np.linspace(0, 2.0, sr * 2, endpoint=False)
        noise = np.random.normal(0, 0.01, len(t)).astype(np.float32)
        impulse_len = int(sr * 0.05)
        t_imp = np.linspace(0, 0.05, impulse_len, endpoint=False)
        pulse = 0.8 * np.exp(-t_imp / 0.008) * np.sin(2 * np.pi * 1200 * t_imp)
        noise[int(sr * 0.5) : int(sr * 0.5) + impulse_len] += pulse.astype(np.float32)

        res_impulse = detector.evaluate_waveform(noise, sr)
        assert "detected" in res_impulse
        assert "dominant_mode" in res_impulse

