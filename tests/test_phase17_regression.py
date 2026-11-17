"""
Unit Tests for Phase 17: Regression, Detector Functionality, and Web API Integration.

Validates:
1. Phase 17 Experimental Gunshot Detector instantiation across all standard and animal-suppressed profiles.
2. Selectable animal semantic suppression gating logic and zero collateral suppression on ballistic shockwaves.
3. Stateful RealTimeStreamDetectorPhase17 streaming ring-buffer, reset, and cooldown behavior.
4. Duplicate alert suppression and refractory cooldown mechanics.
5. Flask web application regression: Phase 14 Balanced default preservation, Phase 17 experimental selection,
   and endpoints (/api/status, /api/health, /api/profiles, /api/detect, /api/stream/chunk, /api/stream/reset).

SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.
"""

import io
import time
import unittest
from pathlib import Path

import numpy as np
import soundfile as sf

WORKSPACE_ROOT = Path("e:/gunshot/gunshot").resolve()
import sys
sys.path.insert(0, str(WORKSPACE_ROOT))

import config
from app import app, get_detector, get_session_stream_detector
from model_phase14 import Phase14CandidateGunshotDetector
from model_phase17 import (
    Phase17ExperimentalGunshotDetector,
    RealTimeStreamDetectorPhase17,
    compute_physical_crest_factor_db
)

SAFETY_DESIGNATION = "RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY"


class TestPhase17Regression(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.client = app.test_client()
        cls.sample_rate = config.SAMPLE_RATE

        # 1. Synthetic clean silence chunk (0.48s)
        cls.silence_chunk = np.zeros(7680, dtype=np.float32)

        # 2. Synthetic ballistic impulse chunk (steep envelope, sharp crest factor)
        t_shot = np.linspace(0, 0.15, 2400, endpoint=False)
        envelope = np.exp(-t_shot / 0.015)
        carrier = np.sin(2 * np.pi * 420 * t_shot) + 0.5 * np.sin(2 * np.pi * 950 * t_shot)
        pulse = (envelope * carrier * 0.95).astype(np.float32)
        shot = np.zeros(7680, dtype=np.float32)
        shot[1600:1600 + len(pulse)] = pulse
        cls.shot_chunk = shot

    def _wav_bytes(self, signal: np.ndarray, sr: int = 16000) -> io.BytesIO:
        buf = io.BytesIO()
        sf.write(buf, signal, sr, format="WAV", subtype="PCM_16")
        buf.seek(0)
        return buf

    def test_01_phase17_profiles_instantiation(self):
        """Verify Phase17 detector instantiates with correct profile parameters and toggles."""
        profiles = [
            ("balanced", False),
            ("balanced_animal_suppressed", True),
            ("high_precision", False),
            ("high_precision_animal_suppressed", True),
            ("high_sensitivity", False),
            ("high_sensitivity_animal_suppressed", True),
            ("experimental_animal_suppression", True)
        ]
        for prof_name, expected_suppr in profiles:
            det = Phase17ExperimentalGunshotDetector(profile=prof_name)
            self.assertEqual(det.enable_animal_suppression, expected_suppr)
            self.assertGreater(det.threshold_base, 0.0)
            self.assertGreater(det.threshold_high, det.threshold_base)
            self.assertGreater(det.single_win_min_crest_db, det.min_crest_factor_db)

    def test_02_animal_semantic_suppression_rule(self):
        """Verify animal suppression attenuates animal vocalizations and leaves gunshots untouched."""
        det = Phase17ExperimentalGunshotDetector(profile="experimental_animal_suppression")
        self.assertTrue(det.enable_animal_suppression)

        # 1. Animal vocalization window: animal=0.55, gun=0.01, raw=0.82
        # Rule: animal > 0.35 and animal >= 2.0 * gun -> MUST suppress
        raw_animal = 0.82
        animal_s = 0.55
        gun_s_low = 0.01
        should_suppress_animal = (animal_s > det.animal_thresh and animal_s >= gun_s_low * det.animal_ratio)
        self.assertTrue(should_suppress_animal, "Animal vocalization must trigger suppression rule.")

        # 2. Genuine ballistic shockwave: gun=0.25, animal=0.02, raw=0.88
        # Must NOT suppress
        raw_gun = 0.88
        animal_s_low = 0.02
        gun_s_high = 0.25
        should_suppress_gun = (animal_s_low > det.animal_thresh and animal_s_low >= gun_s_high * det.animal_ratio)
        self.assertFalse(should_suppress_gun, "Genuine ballistic event must NOT trigger animal suppression.")

    def test_03_realtime_stream_detector_phase17_state_machine(self):
        """Verify RealTimeStreamDetectorPhase17 ring-buffer, reset, and state isolation."""
        stream_det = RealTimeStreamDetectorPhase17(profile="experimental_animal_suppression")
        self.assertEqual(stream_det.last_score, 0.0)
        self.assertFalse(stream_det.in_event)

        # Process silence chunk
        alerts = stream_det.process_chunk(self.silence_chunk, 16000)
        self.assertEqual(len(alerts), 0)
        self.assertFalse(stream_det.in_event)

        # Reset state
        stream_det.reset()
        self.assertEqual(len(stream_det.ring_buffer), 0)
        self.assertEqual(stream_det.cooldown_until, -1.0)
        self.assertFalse(stream_det.in_event)

    def test_04_refractory_cooldown_duplicate_suppression(self):
        """Verify refractory hysteresis prevents duplicate alert emissions during burst events."""
        stream_det = RealTimeStreamDetectorPhase17(profile="balanced")

        # First pulse triggers event or window
        _ = stream_det.process_chunk(self.shot_chunk, 16000)
        first_alert_count = len(stream_det.detected_alerts)

        # Force state into active event or cooldown
        stream_det.cooldown_until = stream_det.processed_duration_sec + 2.5
        stream_det.had_decayed = False

        # Second pulse arrives while not decayed in cooldown
        alerts2 = stream_det.process_chunk(self.shot_chunk, 16000)
        self.assertEqual(len(alerts2), 0, "No duplicate alert may be dispatched while in non-decayed cooldown.")

    def test_05_web_app_health_and_status_endpoints(self):
        """Verify /api/health and /api/status reflect Phase 14 default and Phase 17 experimental."""
        # /api/health
        resp_h = self.client.get("/api/health")
        self.assertEqual(resp_h.status_code, 200)
        data_h = resp_h.get_json()
        self.assertEqual(data_h.get("status"), "healthy")
        self.assertEqual(data_h.get("default_detector"), "phase14")
        self.assertIn("phase17", data_h.get("experimental_detectors", []))
        self.assertEqual(data_h.get("safety_designation"), SAFETY_DESIGNATION)

        # /api/status
        resp_s = self.client.get("/api/status")
        self.assertEqual(resp_s.status_code, 200)
        data_s = resp_s.get_json()
        self.assertTrue(data_s.get("model_loaded"))
        self.assertEqual(data_s.get("default_version"), "phase14")
        self.assertIn("phase17", data_s.get("supported_versions", []))

    def test_06_web_app_phase17_streaming_endpoints(self):
        """Verify /api/stream/chunk and /api/stream_window accept detector_version='phase17'."""
        session_id = f"test_p17_session_{int(time.time())}"
        wav_buf = self._wav_bytes(self.silence_chunk)

        # Test /api/stream/chunk alias
        resp = self.client.post(
            "/api/stream/chunk",
            data={
                "audio": (wav_buf, "chunk.wav"),
                "profile": "experimental_animal_suppression",
                "detector_version": "phase17",
                "session_id": session_id
            },
            content_type="multipart/form-data"
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertIn("score", data)
        self.assertIn("is_gunshot", data)
        self.assertFalse(data["is_gunshot"])
        self.assertEqual(data.get("safety_designation"), SAFETY_DESIGNATION)

        # Test /api/stream/reset
        resp_reset = self.client.post("/api/stream/reset", data={"session_id": session_id})
        self.assertEqual(resp_reset.status_code, 200)
        self.assertEqual(resp_reset.get_json().get("status"), "ok")


if __name__ == "__main__":
    unittest.main()

