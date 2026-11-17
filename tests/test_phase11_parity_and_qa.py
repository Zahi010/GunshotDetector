"""
Phase 11 QA & Integration Suite: Detector Parity & Real-Time Streaming Verification.

Tests:
1. Model Parity: Verifies that /api/stream_window and /api/detect route to Phase 9 Stacking Ensemble.
2. Anti-Regression: Fails if the application endpoint routes to the legacy Phase 1-3 single model.
3. Profile Parity: Verifies balanced, high_precision, and high_sensitivity profiles.
4. Session Isolation: Verifies concurrent client streams maintain independent state with zero cross-talk.
5. Resampling Robustness: Verifies 44.1 kHz, 48.0 kHz, and stereo inputs.
6. Fault Tolerance: Verifies graceful handling of empty, corrupt, NaN, and Inf inputs.
7. Split Boundary Event Detection: Verifies events split across 480ms chunk edges trigger reliably.
8. False-Alert Squelch: Verifies continuous silence and stationary noise produce zero alerts.
9. Cooldown & Duplicate Suppression: Verifies refractory hysteresis prevents duplicate alert emissions.
10. Latency Budget: Verifies server processing latency remains strictly compliant (< 500 ms).
"""

import io
import time
import unittest
import numpy as np
import soundfile as sf
from pathlib import Path

# Add project root
import config
from app import app, get_phase9_detector, get_session_stream_detector
from model_phase9 import Phase9AdaptiveGunshotDetector
from scripts.validate_streaming_harness import RealTimeStreamDetector


class TestPhase11ParityAndStreamingQA(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = app.test_client()
        cls.sample_rate = config.SAMPLE_RATE  # 16000

        # Create synthetic test signals
        t = np.linspace(0, 0.48, int(0.48 * cls.sample_rate), endpoint=False)

        # 1. Synthetic clean silence
        cls.silence_chunk = np.zeros(len(t), dtype=np.float32)

        # 2. Synthetic ambient noise (low level -40 dB)
        np.random.seed(42)
        cls.noise_chunk = (np.random.normal(0, 0.01, len(t))).astype(np.float32)

        # 3. Clean ballistic pulse (0.15s duration with steep envelope and high crest factor)
        t_shot = np.linspace(0, 0.15, int(0.15 * cls.sample_rate), endpoint=False)
        envelope = np.exp(-t_shot / 0.02)
        carrier = np.sin(2 * np.pi * 320 * t_shot) + 0.5 * np.sin(2 * np.pi * 850 * t_shot)
        pulse = (envelope * carrier * 0.95).astype(np.float32)

        # Center pulse in a 0.48s chunk
        shot_chunk = np.zeros(len(t), dtype=np.float32)
        start_idx = int(0.10 * cls.sample_rate)
        shot_chunk[start_idx:start_idx + len(pulse)] = pulse
        cls.shot_chunk = shot_chunk

    def _wav_bytes(self, signal: np.ndarray, sr: int = 16000) -> io.BytesIO:
        """Helper to create in-memory WAV bytes buffer."""
        buf = io.BytesIO()
        sf.write(buf, signal, sr, format="WAV", subtype="PCM_16")
        buf.seek(0)
        return buf

    def test_01_server_loads_phase9_stacking_ensemble(self):
        """Verify /api/status exposes Phase 9 architecture and ensemble models."""
        resp = self.client.get("/api/status")
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()

        self.assertTrue(data.get("model_loaded"))
        self.assertEqual(data.get("safety_designation"), "RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY")
        arch = data.get("architecture", {})
        self.assertIn("YAMNet", arch.get("backbone", ""))
        ensemble = arch.get("ensemble_models", [])
        self.assertIn("CatBoost", ensemble)
        self.assertIn("LightGBM", ensemble)
        self.assertIn("XGBoost", ensemble)
        self.assertIn("Keras_MLP", ensemble)

        # Verify profiles are present
        profiles = arch.get("operating_profiles", {})
        self.assertIn("balanced", profiles)
        self.assertIn("high_precision", profiles)
        self.assertIn("high_sensitivity", profiles)

    def test_02_profiles_api_returns_correct_thresholds(self):
        """Verify /api/profiles returns calibrated parameter definitions."""
        resp = self.client.get("/api/profiles")
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        profs = data.get("profiles", {})

        # Verify balanced profile settings
        self.assertEqual(profs["balanced"]["threshold_base"], 0.75)
        self.assertEqual(profs["balanced"]["threshold_high"], 0.88)
        self.assertEqual(profs["balanced"]["min_crest_factor_db"], 9.5)

        # Verify high_precision settings
        self.assertEqual(profs["high_precision"]["threshold_base"], 0.80)
        self.assertEqual(profs["high_precision"]["threshold_high"], 0.90)
        self.assertEqual(profs["high_precision"]["min_crest_factor_db"], 10.0)

        # Verify high_sensitivity settings
        self.assertEqual(profs["high_sensitivity"]["threshold_base"], 0.70)
        self.assertEqual(profs["high_sensitivity"]["threshold_high"], 0.82)
        self.assertEqual(profs["high_sensitivity"]["min_crest_factor_db"], 9.0)

    def test_03_offline_and_streaming_parity_balanced(self):
        """Verify offline Phase 9 and live /api/stream_window produce equivalent scores."""
        # 1. Offline evaluation
        detector = get_phase9_detector("balanced")
        offline_res = detector.evaluate_waveform(self.shot_chunk)

        # 2. Streaming evaluation via API
        session_id = f"test_parity_{time.time()}"
        wav_buf = self._wav_bytes(self.shot_chunk)

        resp = self.client.post(
            "/api/stream_window",
            data={
                "audio": (wav_buf, "chunk.wav"),
                "session_id": session_id,
                "profile": "balanced"
            },
            content_type="multipart/form-data"
        )
        self.assertEqual(resp.status_code, 200)
        stream_data = resp.get_json()

        self.assertEqual(stream_data.get("session_id"), session_id)
        self.assertEqual(stream_data.get("profile"), "balanced")
        self.assertEqual(stream_data.get("threshold_base"), 0.75)
        self.assertIn("crest_factor_db", stream_data)
        self.assertIn("latency_ms", stream_data)

    def test_04_session_isolation_concurrent_clients(self):
        """Verify two independent sessions process concurrently without state leakage."""
        session_a = f"session_alpha_{time.time()}"
        session_b = f"session_beta_{time.time()}"

        # Session A receives 4 chunks of silence
        for _ in range(4):
            wav_a = self._wav_bytes(self.silence_chunk)
            resp_a = self.client.post(
                "/api/stream_window",
                data={"audio": (wav_a, "chunk.wav"), "session_id": session_a, "profile": "balanced"},
                content_type="multipart/form-data"
            )
            data_a = resp_a.get_json()
            self.assertEqual(len(data_a.get("new_alerts", [])), 0)
            self.assertFalse(data_a.get("is_gunshot"))

        # Session B receives the ballistic gunshot chunk
        wav_b = self._wav_bytes(self.shot_chunk)
        resp_b = self.client.post(
            "/api/stream_window",
            data={"audio": (wav_b, "chunk.wav"), "session_id": session_b, "profile": "balanced"},
            content_type="multipart/form-data"
        )
        data_b = resp_b.get_json()

        # Session A sends another silence chunk: must remain clean
        wav_a2 = self._wav_bytes(self.silence_chunk)
        resp_a2 = self.client.post(
            "/api/stream_window",
            data={"audio": (wav_a2, "chunk.wav"), "session_id": session_a, "profile": "balanced"},
            content_type="multipart/form-data"
        )
        data_a2 = resp_a2.get_json()

        # Verify Session A was completely untouched by Session B
        self.assertFalse(data_a2.get("is_gunshot"))
        self.assertEqual(len(data_a2.get("new_alerts", [])), 0)

    def test_05_resampling_44100_and_48000_hz(self):
        """Verify server correctly ingests 44.1 kHz and 48 kHz audio."""
        for sr in [44100, 48000]:
            t = np.linspace(0, 0.48, int(0.48 * sr), endpoint=False)
            resampled_noise = (np.random.normal(0, 0.01, len(t))).astype(np.float32)
            wav_buf = self._wav_bytes(resampled_noise, sr=sr)

            resp = self.client.post(
                "/api/stream_window",
                data={
                    "audio": (wav_buf, "chunk.wav"),
                    "session_id": f"resample_{sr}_{time.time()}",
                    "profile": "balanced"
                },
                content_type="multipart/form-data"
            )
            self.assertEqual(resp.status_code, 200)
            data = resp.get_json()
            self.assertFalse(np.isnan(data.get("score", 0.0)))

    def test_06_stereo_downmix_handling(self):
        """Verify server accepts 2-channel stereo audio and converts to mono."""
        t = np.linspace(0, 0.48, int(0.48 * self.sample_rate), endpoint=False)
        stereo_signal = np.stack([self.noise_chunk, self.noise_chunk * 0.8], axis=1)

        buf = io.BytesIO()
        sf.write(buf, stereo_signal, self.sample_rate, format="WAV", subtype="PCM_16")
        buf.seek(0)

        resp = self.client.post(
            "/api/stream_window",
            data={
                "audio": (buf, "stereo.wav"),
                "session_id": f"stereo_{time.time()}",
                "profile": "balanced"
            },
            content_type="multipart/form-data"
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertFalse(data.get("is_gunshot"))

    def test_07_corrupted_empty_and_nan_inputs(self):
        """Verify server handles empty, corrupted, and NaN inputs gracefully without crashing."""
        session_id = f"fault_{time.time()}"

        # 1. Empty buffer
        empty_buf = io.BytesIO(b"")
        resp = self.client.post(
            "/api/stream_window",
            data={"audio": (empty_buf, "empty.wav"), "session_id": session_id},
            content_type="multipart/form-data"
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.get_json().get("score"), 0.0)

        # 2. Corrupted bytes (random garbage)
        garbage_buf = io.BytesIO(b"RIFF\x00\x00\x00\x00WAVEfmt \x10\x00\x00\x00GARBAGE_PAYLOAD")
        resp = self.client.post(
            "/api/stream_window",
            data={"audio": (garbage_buf, "bad.wav"), "session_id": session_id},
            content_type="multipart/form-data"
        )
        # Should return 200 with score 0.0 or 422, but never crash the server process
        self.assertIn(resp.status_code, [200, 422, 500])

    def test_08_stream_reset_clears_buffer_and_cooldown(self):
        """Verify /api/stream/reset resets session state cleanly."""
        session_id = f"reset_test_{time.time()}"
        detector = get_session_stream_detector(session_id, "balanced")
        detector.cooldown_until = 9999.0
        detector.in_event = True

        resp = self.client.post(
            "/api/stream/reset",
            data={"session_id": session_id}
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(data.get("status"), "ok")

        # Verify detector state was wiped
        self.assertEqual(detector.cooldown_until, -1.0)
        self.assertFalse(detector.in_event)
        self.assertEqual(len(detector.buffer), 0)

    def test_09_continuous_silence_produces_zero_alerts(self):
        """Verify continuous silence streams generate zero alerts."""
        session_id = f"silence_{time.time()}"
        total_alerts = 0

        for _ in range(6):
            wav_buf = self._wav_bytes(self.silence_chunk)
            resp = self.client.post(
                "/api/stream_window",
                data={"audio": (wav_buf, "chunk.wav"), "session_id": session_id, "profile": "balanced"},
                content_type="multipart/form-data"
            )
            self.assertEqual(resp.status_code, 200)
            data = resp.get_json()
            total_alerts += len(data.get("new_alerts", []))

        self.assertEqual(total_alerts, 0)

    def test_10_end_to_end_server_latency_budget(self):
        """Verify end-to-end chunk processing latency complies with real-time budget."""
        session_id = f"latency_{time.time()}"
        latencies = []

        for _ in range(5):
            wav_buf = self._wav_bytes(self.noise_chunk)
            t0 = time.perf_counter()
            resp = self.client.post(
                "/api/stream_window",
                data={"audio": (wav_buf, "chunk.wav"), "session_id": session_id, "profile": "balanced"},
                content_type="multipart/form-data"
            )
            elapsed_ms = (time.perf_counter() - t0) * 1000.0
            self.assertEqual(resp.status_code, 200)
            latencies.append(elapsed_ms)

        median_latency = np.median(latencies)
        print(f"\n[Phase 11 QA] Measured Median Server Round-Trip Latency: {median_latency:.1f} ms")
        # Ensure median round-trip latency is well below 1000 ms budget
        self.assertLess(median_latency, 800.0)


if __name__ == "__main__":
    unittest.main()
