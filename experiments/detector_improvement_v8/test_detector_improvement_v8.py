"""
Unit Test Suite for Detector Improvement V8
RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY
"""

import sys
import os
import pathlib
sys.path.insert(0, "E:/gunshot/gunshot")
os.chdir("E:/gunshot/gunshot")

import pytest
import numpy as np

from experiments.detector_improvement_v8.model_detector_improvement_v8 import (
    compute_physical_acoustic_features_v8,
    ConditionEstimatorV8,
    CalibratedSemanticSuppressionV8,
    ConditionAdaptiveFSMV8,
    DetectorImprovementV8,
    OperatingMode,
    EventState
)


class TestDetectorImprovementV8:

    def test_01_silence_energy_floor_gate(self):
        """Test that pure digital silence returns 0.0 adjusted score without tree leaf traversal."""
        supp_cfg = {
            "ballistic_coherence": {"enabled": True, "max_pure_gun": 0.08, "max_ballistic": 0.10, "attenuation": 0.20}
        }
        supp = CalibratedSemanticSuppressionV8(supp_cfg)

        # Digital zero
        zero_win = np.zeros(15360, dtype=np.float32)
        acoustics = compute_physical_acoustic_features_v8(zero_win)
        res = supp.apply_suppression(0.9853, {}, acoustics)
        assert res["adjusted_score"] == 0.0
        assert res["suppressed"] is True
        assert res["category"] == "zero_energy_silence"

        # Sub-threshold noise
        quiet_win = np.random.uniform(-0.0001, 0.0001, 15360).astype(np.float32)
        acoustics_q = compute_physical_acoustic_features_v8(quiet_win)
        res_q = supp.apply_suppression(0.85, {}, acoustics_q)
        assert res_q["adjusted_score"] == 0.0

    def test_02_condition_estimator_anti_chatter(self):
        """Test that condition estimator suppresses rapid chatter with hysteresis."""
        ce = ConditionEstimatorV8(alpha=0.20, hysteresis_occluded=3, hysteresis_clear=2, hysteresis_rumble=2)

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

    def test_03_calibrated_pyrotechnic_gating(self):
        """Test calibrated pyrotechnic gating separates chemical fireworks from genuine gunshots."""
        supp_cfg = {
            "fireworks": {
                "enabled": True, "dominant_threshold": 0.45, "dominant_ratio": 1.8, "dominant_attenuation": 0.15,
                "ballistic_override_threshold": 0.40, "ballistic_override_ratio": 0.85,
                "ballistic_acoustics_mid_to_low": 0.25, "ballistic_acoustics_centroid_hz": 750.0,
                "ballistic_acoustics_high_centroid_hz": 1200.0, "pure_gun_override_threshold": 0.20
            }
        }
        supp = CalibratedSemanticSuppressionV8(supp_cfg)

        # Case A: Chemical fireworks boom (cent=410 Hz, m2l=0.08, bal_s=0.85, fw_s=0.50, pure_gun=0.02)
        # In V7, this hijacked the ballistic shockwave override. In V8, it is SUPPRESSED!
        acoustics_fw = (14.5, 0.01, 0.005, 0.07, 0.92, 0.08, 0.01, 410.0, 0.08, 0.45)
        yamnet_fw = {426: 0.50, 420: 0.85, 421: 0.02}
        res_fw = supp.apply_suppression(0.92, yamnet_fw, acoustics_fw)
        assert res_fw["suppressed"] is True
        assert res_fw["adjusted_score"] == pytest.approx(0.92 * 0.15, rel=1e-3)
        assert res_fw["category"] == "fireworks_dominant"

        # Case B: Field gunshot with sharp crack (cent=1450 Hz, m2l=1.66, bal_s=0.75, fw_s=0.55, pure_gun=0.05)
        # OVERRIDDEN because cent >= 1200 Hz and bal_s >= 0.85 * fw_s!
        acoustics_gun = (18.5, 0.05, 0.12, 0.55, 0.33, 1.66, 0.22, 1450.0, 0.08, 0.55)
        yamnet_gun = {426: 0.55, 420: 0.75, 421: 0.05}
        res_gun = supp.apply_suppression(0.95, yamnet_gun, acoustics_gun)
        assert res_gun["suppressed"] is False
        assert res_gun["adjusted_score"] == 0.95

        # Case C: Firearm with pure_gun >= 0.20 -> Always exempt from pyrotechnic attenuation
        yamnet_pure = {426: 0.60, 420: 0.30, 421: 0.25}
        res_pure = supp.apply_suppression(0.90, yamnet_pure, acoustics_fw)
        assert res_pure["suppressed"] is False
        assert res_pure["adjusted_score"] == 0.90

    def test_04_transient_acoustic_thunder_gating(self):
        """Test that environmental thunder/booms are suppressed while real gunfire transients are protected."""
        supp_cfg = {
            "thunder": {
                "enabled": True, "semantic_threshold": 0.20, "low_band_threshold": 0.65,
                "mid_to_low_max": 0.55, "gunshot_transient_mid_to_low": 0.40,
                "gunshot_transient_centroid_hz": 750.0, "gunshot_transient_crest_db": 16.0,
                "pure_gun_threshold": 0.12, "attenuation": 0.30
            }
        }
        supp = CalibratedSemanticSuppressionV8(supp_cfg)

        # Case A: Real thunder / industrial boom (lo=0.78, m2l=0.22, cent=420 Hz, crest=13.0 dB, pure_gun=0.02)
        # bal_s = 0.40 (often triggered by class 420 "Explosion")
        acoustics_thun = (13.0, 0.005, 0.005, 0.18, 0.78, 0.22, 0.02, 420.0, 0.06, 0.25)
        yamnet_thun = {280: 0.50, 420: 0.40, 421: 0.02}
        res_thun = supp.apply_suppression(0.82, yamnet_thun, acoustics_thun)
        assert res_thun["suppressed"] is True
        assert res_thun["adjusted_score"] == pytest.approx(0.82 * 0.30, rel=1e-3)
        assert res_thun["category"] == "thunder_rumble"

        # Case B: Reverberant real gunshot (lo=0.68, m2l=0.45, cent=820 Hz, crest=17.5 dB, pure_gun=0.05)
        # Protected because m2l >= 0.40, cent >= 750 Hz, and crest >= 16.0 dB
        acoustics_gun_reverb = (17.5, 0.03, 0.02, 0.30, 0.68, 0.45, 0.05, 820.0, 0.07, 0.40)
        res_reverb = supp.apply_suppression(0.88, yamnet_thun, acoustics_gun_reverb)
        assert res_reverb["suppressed"] is False
        assert res_reverb["adjusted_score"] == 0.88

    def test_05_glass_shatter_suppression(self):
        """Test that glass shatter transients are suppressed."""
        supp_cfg = {
            "glass_shatter": {
                "enabled": True, "threshold": 0.30, "min_high_band_ratio": 0.25,
                "gun_score_max": 0.20, "attenuation": 0.35
            }
        }
        supp = CalibratedSemanticSuppressionV8(supp_cfg)
        acoustics_glass = (16.0, 0.08, 0.35, 0.45, 0.20, 2.25, 0.77, 3400.0, 0.05, 0.30)
        yamnet_glass = {433: 0.45, 421: 0.05}
        res = supp.apply_suppression(0.80, yamnet_glass, acoustics_glass)
        assert res["suppressed"] is True
        assert res["adjusted_score"] == pytest.approx(0.80 * 0.35, rel=1e-3)
        assert res["category"] == "glass_shatter"

    def test_06_sub_bass_automotive_backfire_suppression(self):
        """Test that automotive backfires with cap gun pops and heavy low frequencies are attenuated."""
        supp_cfg = {
            "sub_bass_thud": {
                "enabled": True, "min_low_ratio": 0.70, "max_high_ratio": 0.008,
                "max_centroid_hz": 450.0, "min_cap_gun": 0.35, "cap_to_pure_ratio": 1.5,
                "max_pure_gun": 0.20, "attenuation": 0.25
            }
        }
        supp = CalibratedSemanticSuppressionV8(supp_cfg)
        acoustics = (14.8, 0.001, 0.001, 0.18, 0.81, 0.22, 0.005, 696.0, 0.08, 0.46)
        yamnet_backfire = {424: 0.55, 421: 0.23, 420: 0.25}
        res = supp.apply_suppression(0.82, yamnet_backfire, acoustics)
        assert res["suppressed"] is True
        assert res["adjusted_score"] == pytest.approx(0.82 * 0.25, rel=1e-3)
        assert res["category"] == "sub_bass_thud"

    def test_07_fsm_tightened_single_impulse_gating(self):
        """Test that single impulse in UNKNOWN mode requires sharp acoustics when crest < 13.5 dB."""
        policy = {
            "UNKNOWN": {
                "threshold_base": 0.70, "threshold_high": 0.85, "confirm_windows": 2,
                "single_impulse_min_crest_db": 13.5, "single_impulse_high_conf_crest_db": 12.0,
                "single_impulse_min_score": 0.70, "allow_single_impulse_exception": True
            },
            "DEGRADED_OCCLUDED": {
                "threshold_base": 0.62, "threshold_high": 0.80, "confirm_windows": 2,
                "single_impulse_min_crest_db": 10.5, "single_impulse_high_conf_crest_db": 10.0,
                "single_impulse_min_score": 0.62, "allow_single_impulse_exception": True
            }
        }
        fsm = ConditionAdaptiveFSMV8(policy)

        # Case A: UNKNOWN mode, high confidence (0.91), crest 12.5 dB, but dull acoustics (cent=520 Hz, m2l=0.20)
        # DENIED single impulse exception because m2l < 0.35 and cent < 750 Hz!
        acoustics_dull = (12.5, 0.01, 0.01, 0.18, 0.80, 0.20, 0.02, 520.0, 0.08, 0.35)
        st, ev = fsm.step(0.91, 12.5, 0.48, acoustics_dull, OperatingMode.UNKNOWN)
        assert ev is None
        assert st == EventState.CANDIDATE

        # Case B: UNKNOWN mode, high confidence (0.91), crest 12.5 dB, sharp acoustics (cent=950 Hz, m2l=0.85)
        # CONFIRMED single impulse exception!
        fsm.reset()
        acoustics_sharp = (12.5, 0.02, 0.05, 0.45, 0.50, 0.85, 0.10, 950.0, 0.08, 0.35)
        st2, ev2 = fsm.step(0.91, 12.5, 0.48, acoustics_sharp, OperatingMode.UNKNOWN)
        assert ev2 is not None
        assert st2 == EventState.CONFIRMED
        assert ev2["trigger_type"] == "single_impulse_exception"

        # Case C: DEGRADED_OCCLUDED mode, score 0.82, crest 10.2 dB -> Confirmed
        fsm.reset()
        st3, ev3 = fsm.step(0.82, 10.2, 0.48, acoustics_dull, OperatingMode.DEGRADED_OCCLUDED)
        assert ev3 is not None
        assert st3 == EventState.CONFIRMED

    def test_08_ballistic_coherence_saturation_safeguard(self):
        """Test that saturated / clipped high amplitude transients use saturation threshold."""
        supp_cfg = {
            "ballistic_coherence": {
                "enabled": True, "max_pure_gun": 0.08, "max_ballistic": 0.10,
                "saturation_pure_gun": 0.04, "saturation_ballistic": 0.04,
                "attenuation": 0.20
            }
        }
        supp = CalibratedSemanticSuppressionV8(supp_cfg)
        acoustics_sat = (16.5, 0.05, 0.08, 0.55, 0.37, 1.48, 0.14, 1150.0, 0.10, 0.45)
        yamnet_sat = {421: 0.06, 420: 0.08}
        res = supp.apply_suppression(0.78, yamnet_sat, acoustics_sat)
        assert res["suppressed"] is False
        assert res["adjusted_score"] == 0.78

    def test_09_physical_features_computation(self):
        """Verify 10 physical DSP feature dimensions."""
        sr = 16000
        t = np.linspace(0, 0.96, int(sr * 0.96), endpoint=False)
        y = 0.5 * np.sin(2 * np.pi * 1000 * t).astype(np.float32)
        crest, flat, hi, mid, lo, m2l, rolloff, cent, rms, peak = compute_physical_acoustic_features_v8(y, sr)

        assert crest > 2.5 and crest < 4.0
        assert mid > 0.90
        assert cent > 950 and cent < 1050
        assert rms > 0.30 and rms < 0.40
        assert peak > 0.49 and peak < 0.51

    def test_10_end_to_end_detector_evaluation(self):
        """Test full detector evaluation on synthetic waveforms."""
        detector = DetectorImprovementV8()
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

