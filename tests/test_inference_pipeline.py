"""
Regression Test: Verify real-time inference pipeline and edge cases.
"""
import sys
import unittest
import numpy as np
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import config
from model import GunshotDetector


class TestInferencePipeline(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.detector = GunshotDetector(bundle_dir=config.MODELS_DIR / "gunshot_yamnet_bundle")

    def test_detector_initialization(self):
        """Verify detector initialized with valid thresholds and config."""
        self.assertIsNotNone(self.detector.classifier_head)
        self.assertGreater(self.detector.threshold, 0.0)
        self.assertLess(self.detector.threshold, 1.0)

    def test_pure_silence_input(self):
        """Verify zero-filled array returns zero score without errors."""
        silence = np.zeros(16000 * 2, dtype=np.float32)
        res = self.detector.detect_waveform(silence)
        self.assertEqual(res["overall_score"], 0.0)
        self.assertFalse(res["gunshot_detected"])
        self.assertEqual(len(res["events"]), 0)

    def test_empty_waveform_input(self):
        """Verify 0-length waveform handled gracefully."""
        empty = np.array([], dtype=np.float32)
        res = self.detector.detect_waveform(empty)
        self.assertEqual(res["overall_score"], 0.0)
        self.assertFalse(res["gunshot_detected"])

    def test_inference_latency_budget(self):
        """Verify sustained inference latency is within real-time streaming budget (< 480 ms)."""
        test_audio = np.random.randn(15360).astype(np.float32) * 0.05
        # 1. Warm-up call (JIT trace & graph initialization)
        _ = self.detector.detect_waveform(test_audio)
        # 2. Sustained streaming call
        res = self.detector.detect_waveform(test_audio)
        self.assertIn("inference_time_ms", res)
        self.assertLess(res["inference_time_ms"], 480.0, "Sustained inference latency exceeded 480ms streaming hop budget!")


if __name__ == "__main__":
    unittest.main()
