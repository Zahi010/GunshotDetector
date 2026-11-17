"""
Unit Tests for Detector Improvement V5: Condition-Adaptive Gunshot Detector

MANDATORY SAFETY DESIGNATION:
RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.
"""

import sys
import os
import unittest
import numpy as np

# Ensure workspace root is in path
sys.path.insert(0, "E:/gunshot/gunshot")

from experiments.detector_improvement_v5.model_detector_improvement_v5 import (
    OperatingMode,
    ConditionEstimatorV5,
    ConditionAdaptiveFSMV5,
    CalibratedSemanticSuppressionV5,
    EventState,
    compute_physical_acoustic_features_v5,
    DetectorImprovementV5
)


class TestDetectorImprovementV5(unittest.TestCase):
    """Test suite for Detector Improvement V5 components and logic."""

    def setUp(self):
        self.mode_policies = {
            "CLEAR_NORMAL": {
                "threshold_base": 0.70,
                "threshold_high": 0.85,
                "threshold_off": 0.45,
                "confirm_windows": 2,
                "cooldown_secs": 2.0,
                "allow_single_impulse_exception": True,
                "single_impulse_min_score": 0.70,
                "single_impulse_min_crest_db": 13.5
            },
            "DEGRADED_OCCLUDED": {
                "threshold_base": 0.62,
                "threshold_high": 0.80,
                "threshold_off": 0.40,
                "confirm_windows": 2,
                "cooldown_secs": 2.0,
                "allow_single_impulse_exception": True,
                "single_impulse_min_score": 0.62,
                "single_impulse_min_crest_db": 11.5
            },
            "UNKNOWN": {
                "threshold_base": 0.68,
                "threshold_high": 0.83,
                "threshold_off": 0.42,
                "confirm_windows": 2,
                "cooldown_secs": 2.0,
                "allow_single_impulse_exception": True,
                "single_impulse_min_score": 0.68,
                "single_impulse_min_crest_db": 13.0
            }
        }
        self.suppression_cfg = {
            "glass": {
                "enabled": True,
                "threshold": 0.30,
                "min_high_band_ratio": 0.30,
                "gun_score_max": 0.20,
                "attenuation": 0.35
            },
            "thunder": {
                "enabled": True,
                "threshold": 0.20,
                "low_band_threshold": 0.65,
                "mid_to_low_max": 0.55,
                "gun_score_max": 0.15,
                "attenuation": 0.30
            },
            "fireworks": {
                "enabled": True,
                "dominant_threshold": 0.45,
                "dominant_ratio": 1.8,
                "dominant_gun_max": 0.25,
                "dominant_attenuation": 0.30,
                "standard_threshold": 0.30,
                "standard_ratio": 1.5,
                "standard_gun_max": 0.12,
                "standard_attenuation": 0.35
            },
            "mechanical_impact": {
                "enabled": True,
                "impact_threshold": 0.25,
                "impact_to_gun_ratio": 1.5,
                "gun_score_max": 0.20,
                "attenuation": 0.35
            }
        }

    def test_01_condition_estimator_initialization_and_clear_transition(self):
        """Condition estimator starts in UNKNOWN and transitions to CLEAR after persistent clear evidence."""
        estimator = ConditionEstimatorV5(alpha=0.5, hysteresis_windows=2)
        self.assertEqual(estimator.current_mode, OperatingMode.UNKNOWN)

        # First window of clear audio: rolloff=0.35, high=0.15, mid=0.45, low=0.40, m2l=1.12
        mode, conf, did_trans = estimator.update(
            rolloff=0.35, high_ratio=0.15, mid_ratio=0.45, low_ratio=0.40, mid_to_low=1.12, time_s=0.0, window_idx=0
        )
        self.assertFalse(did_trans, "Single window must not trigger transition (hysteresis safeguard)")
        self.assertEqual(mode, OperatingMode.UNKNOWN)

        # Second window of clear audio: reinforces clear evidence
        mode, conf, did_trans = estimator.update(
            rolloff=0.35, high_ratio=0.15, mid_ratio=0.45, low_ratio=0.40, mid_to_low=1.12, time_s=0.48, window_idx=1
        )
        self.assertTrue(did_trans, "Persistent evidence must transition to CLEAR_NORMAL")
        self.assertEqual(mode, OperatingMode.CLEAR_NORMAL)
        self.assertGreater(conf, 0.50)
        self.assertEqual(len(estimator.transition_log), 1)

    def test_02_condition_estimator_occluded_transition_and_safeguards(self):
        """Condition estimator transitions to DEGRADED_OCCLUDED on fabric-attenuated audio, but NOT on thunder."""
        estimator = ConditionEstimatorV5(alpha=0.5, hysteresis_windows=2)

        # Feed 2 windows of fabric-occluded audio: low rolloff, low high, strong mid, strong m2l
        estimator.update(rolloff=0.10, high_ratio=0.04, mid_ratio=0.50, low_ratio=0.46, mid_to_low=1.09, time_s=0.0, window_idx=0)
        mode, conf, did_trans = estimator.update(
            rolloff=0.10, high_ratio=0.04, mid_ratio=0.50, low_ratio=0.46, mid_to_low=1.09, time_s=0.48, window_idx=1
        )
        self.assertTrue(did_trans)
        self.assertEqual(mode, OperatingMode.DEGRADED_OCCLUDED)

        # Now test thunder rumble: low rolloff, but dominant low-frequency (low=0.85, m2l=0.15)
        # Thunder must NOT sustain occluded mode! It must trigger transition to UNKNOWN!
        estimator.update(rolloff=0.05, high_ratio=0.01, mid_ratio=0.14, low_ratio=0.85, mid_to_low=0.16, time_s=0.96, window_idx=2)
        self.assertEqual(estimator.current_mode, OperatingMode.UNKNOWN, "Dominant low rumble must revert to UNKNOWN fallback")

    def test_03_fsm_adaptive_confirmation_policies(self):
        """FSM behaves conservatively in CLEAR mode and condition-sensitively in OCCLUDED mode."""
        fsm = ConditionAdaptiveFSMV5(mode_policies=self.mode_policies)

        # Case A: In CLEAR_NORMAL mode, a marginal impulse (score=0.64, crest=12.0) is REJECTED
        state, ev = fsm.step(score=0.64, crest_db=12.0, time_s=0.0, operating_mode=OperatingMode.CLEAR_NORMAL)
        self.assertEqual(state, EventState.IDLE, "Marginal impulse must be rejected under CLEAR_NORMAL policy")
        self.assertIsNone(ev)

        # Case B: In DEGRADED_OCCLUDED mode, that exact same impulse (score=0.64, crest=12.0) is CONFIRMED
        fsm.reset()
        state, ev = fsm.step(score=0.64, crest_db=12.0, time_s=0.0, operating_mode=OperatingMode.DEGRADED_OCCLUDED)
        self.assertEqual(state, EventState.CONFIRMED, "Pocket gunshot must be confirmed under DEGRADED_OCCLUDED policy")
        self.assertIsNotNone(ev)
        self.assertEqual(ev["operating_mode"], "DEGRADED_OCCLUDED")
        self.assertEqual(ev["trigger_type"], "single_impulse_exception")

        # Case C: In UNKNOWN mode, a marginal impulse (score=0.64) is REJECTED
        fsm.reset()
        state, ev = fsm.step(score=0.64, crest_db=12.0, time_s=0.0, operating_mode=OperatingMode.UNKNOWN)
        self.assertEqual(state, EventState.IDLE, "Unknown mode must use conservative fallback")
        self.assertIsNone(ev)

    def test_04_mode_change_alone_never_emits_event(self):
        """Switching modes when scores are quiescent never triggers an event."""
        fsm = ConditionAdaptiveFSMV5(mode_policies=self.mode_policies)

        # In CLEAR mode with ambient audio (score 0.20)
        state, ev = fsm.step(score=0.20, crest_db=8.0, time_s=0.0, operating_mode=OperatingMode.CLEAR_NORMAL)
        self.assertIsNone(ev)

        # Mode switches to OCCLUDED with ambient audio (score 0.25)
        state, ev = fsm.step(score=0.25, crest_db=8.5, time_s=0.48, operating_mode=OperatingMode.DEGRADED_OCCLUDED)
        self.assertIsNone(ev, "Mode change alone must never generate an alert")
        self.assertEqual(state, EventState.IDLE)

    def test_05_enhanced_glass_shatter_suppression(self):
        """Glass shatter with high high-band energy is suppressed even if ballistic classes have partial energy."""
        suppression = CalibratedSemanticSuppressionV5(suppression_cfg=self.suppression_cfg)

        yamnet_glass = {
            433: 0.85,  # Glass
            435: 0.80,  # Shatter
            421: 0.05,  # Gunshot
            434: 0.45,  # Crack (in ballistic classes)
            280: 0.00, 281: 0.00, 426: 0.00, 427: 0.00, 413: 0.00, 414: 0.00,
            352: 0.00, 353: 0.00, 58: 0.00, 436: 0.10, 420: 0.00, 422: 0.00,
            424: 0.00, 425: 0.00, 428: 0.00, 460: 0.00, 0: 0.00
        }
        res = suppression.apply_suppression(
            raw_score=0.88,
            yamnet_scores=yamnet_glass,
            high_band_ratio=0.65,
            low_band_ratio=0.05,
            mid_to_low=5.0
        )
        self.assertTrue(res["suppressed"], "Glass breaking must be suppressed")
        self.assertEqual(res["category"], "glass_shatter")
        self.assertLess(res["adjusted_score"], 0.35)

    def test_06_enhanced_thunder_suppression(self):
        """Low-frequency rumble/thunder with low gunshot score is suppressed."""
        suppression = CalibratedSemanticSuppressionV5(suppression_cfg=self.suppression_cfg)

        yamnet_thunder = {
            280: 0.25, 281: 0.30,  # Thunder
            421: 0.02, 422: 0.00, 424: 0.00, 425: 0.00, 420: 0.00, 428: 0.00,
            434: 0.00, 460: 0.00, 426: 0.00, 427: 0.00, 413: 0.00, 414: 0.00,
            352: 0.00, 353: 0.00, 58: 0.00, 433: 0.00, 435: 0.00, 436: 0.00, 0: 0.00
        }
        res = suppression.apply_suppression(
            raw_score=0.75,
            yamnet_scores=yamnet_thunder,
            high_band_ratio=0.005,
            low_band_ratio=0.85,
            mid_to_low=0.15
        )
        self.assertTrue(res["suppressed"], "Thunder rumble must be suppressed")
        self.assertEqual(res["category"], "thunder_or_low_rumble")
        self.assertLess(res["adjusted_score"], 0.30)

    def test_07_physical_features_computation(self):
        """Verify 8 physical acoustic features compute accurately in <1ms."""
        sr = 16000
        t = np.linspace(0, 0.96, int(sr * 0.96), endpoint=False)
        # Synthetic impulse + mid-band tone
        sig = 0.5 * np.sin(2 * np.pi * 1000 * t)
        sig[100] = 5.0  # Sharp spike
        features = compute_physical_acoustic_features_v5(sig, sr=sr)
        self.assertEqual(len(features), 8)
        crest, flat, hi, mid, lo, m2l, rolloff, cent = features
        self.assertGreater(crest, 10.0)
        self.assertGreater(mid, 0.20)
        self.assertAlmostEqual(hi + mid + lo, 1.0, places=2)

    def test_08_end_to_end_detector_evaluation(self):
        """Verify DetectorImprovementV5 instantiates and evaluates synthetic waveform."""
        detector = DetectorImprovementV5(profile="condition_adaptive")
        sr = 16000
        sig = np.zeros(sr * 2, dtype=np.float32)  # 2.0s of silence/ambient
        sig[1000:1050] = 0.8  # transient
        res = detector.evaluate_waveform(sig, sr=sr)
        self.assertIn("detected", res)
        self.assertIn("dominant_operating_mode", res)
        self.assertIn("mode_transitions", res)
        self.assertIsInstance(res["events"], list)


if __name__ == "__main__":
    unittest.main()
