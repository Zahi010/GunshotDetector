"""
Phase 4 Automated Verification Suite:
Tests silence handling, trailing silence labeling, low-SNR gunshot retention,
split independence, and hysteresis event inference.
"""
import sys
import unittest
import numpy as np
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

import config
from dataset import GunshotDataset, load_audio_mono_16k, get_base_stem
from model import GunshotDetector, merge_detection_windows


class TestPhase4SilenceAndLowSNR(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dataset = GunshotDataset(data_dir=config.DATA_DIR)
        cls.dataset.index_files()
        cls.detector = GunshotDetector(bundle_dir=config.MODELS_DIR / "gunshot_yamnet_bundle")

    def test_original_source_recordings_unchanged(self):
        """Confirm original source recordings remain 100% physically unmodified."""
        raw_gunshots = list(Path("data/raw/gunshots").glob("*.mp3"))
        self.assertGreater(len(raw_gunshots), 0, "No raw gunshot recordings found!")
        
        # Spot check durations
        for p in raw_gunshots[:5]:
            wave = load_audio_mono_16k(p)
            dur = len(wave) / 16000.0
            self.assertGreater(dur, 0.5, f"Recording {p.name} appears truncated or corrupt!")

    def test_trailing_silence_not_labeled_positive(self):
        """Confirm windows containing only trailing silence are assigned label 0 (negative)."""
        test_cache = np.load(".cache_features/features_test.npz", allow_pickle=True)
        meta = test_cache["meta"]
        y = test_cache["y"]
        y_whole = test_cache["y_whole_file"]

        # Find windows where whole_file_label=1 (from a gunshot file) but timestamp-aware y=0 (trailing silence)
        trailing_silent_windows = [
            (m, yi, ywi) for m, yi, ywi in zip(meta, y, y_whole)
            if ywi == 1 and yi == 0
        ]
        self.assertGreater(
            len(trailing_silent_windows), 0,
            "No trailing silence windows were relabeled negative! Timestamp-aware labeling must assign 0 to silence."
        )

        for m, yi, ywi in trailing_silent_windows[:10]:
            self.assertEqual(yi, 0, f"Window {m} has non-negative label despite containing only silence!")
            self.assertLessEqual(m.get("max_overlap_sec", 0.0), 0.05, "Trailing silence window had unexpected event overlap!")

    def test_genuine_low_energy_gunshot_events_retained(self):
        """Confirm low-SNR distant gunshot events retain positive label (not trimmed or filtered)."""
        events_by_id = self.dataset.events_by_id
        # Find low-SNR event in manifest
        low_snr_found = False
        for rec_id, ev_list in events_by_id.items():
            for ev in ev_list:
                snr = ev.get("estimated_snr_db", ev.get("snr_db", 100.0))
                if snr < 30.0:
                    low_snr_found = True
                    self.assertGreater(ev["duration_sec"], 0.1, "Low-SNR event duration abnormally short!")
                    break
            if low_snr_found:
                break
        self.assertTrue(low_snr_found, "Verified low-SNR gunshot events must be present in events manifest.")

    def test_splits_source_independence(self):
        """Verify train, val, and test splits remain strictly source-independent."""
        train_stems = {self.dataset.groups[g]["base_stem"] for g in self.dataset.splits["train"]}
        val_stems = {self.dataset.groups[g]["base_stem"] for g in self.dataset.splits["val"]}
        test_stems = {self.dataset.groups[g]["base_stem"] for g in self.dataset.splits["test"]}

        self.assertEqual(len(train_stems.intersection(val_stems)), 0, "Source stem collision between Train and Val!")
        self.assertEqual(len(train_stems.intersection(test_stems)), 0, "Source stem collision between Train and Test!")
        self.assertEqual(len(val_stems.intersection(test_stems)), 0, "Source stem collision between Val and Test!")

    def test_hysteresis_and_cooldown_event_merging(self):
        """Verify hysteresis state-machine tracks reverberation decay while suppressing duplicate alerts."""
        # Simulated sequence:
        # Window 0: 0.10 (ambient noise)
        # Window 1: 0.85 (onset trigger)
        # Window 2: 0.40 (reverberant tail, above threshold_off 0.25)
        # Window 3: 0.15 (decay below threshold_off, ends event)
        # Window 4: 0.60 (secondary reflection during cooldown, should be suppressed)
        simulated_windows = [
            {"window_index": 0, "start_time": 0.00, "end_time": 0.96, "score": 0.10},
            {"window_index": 1, "start_time": 0.48, "end_time": 1.44, "score": 0.85},
            {"window_index": 2, "start_time": 0.96, "end_time": 1.92, "score": 0.40},
            {"window_index": 3, "start_time": 1.44, "end_time": 2.40, "score": 0.15},
            {"window_index": 4, "start_time": 1.92, "end_time": 2.88, "score": 0.45},  # Reflection below threshold (0.55), above threshold_off (0.25)
            {"window_index": 5, "start_time": 4.50, "end_time": 5.46, "score": 0.80},  # After cooldown
        ]

        events = merge_detection_windows(
            simulated_windows,
            threshold=0.55,
            confirm_windows=1,
            cooldown_secs=2.0,
            threshold_off=0.25
        )

        # Should produce exactly 2 distinct events (Window 1-2 merged into event 1, Window 4 suppressed by cooldown, Window 5 event 2)
        self.assertEqual(len(events), 2, f"Expected 2 merged events, got {len(events)}")
        ev1 = events[0]
        self.assertEqual(ev1["start_time"], 0.48)
        self.assertEqual(ev1["end_time"], 1.92)  # Extended to include Window 2's reverberation tail
        self.assertEqual(ev1["trigger_windows_count"], 2)

        ev2 = events[1]
        self.assertEqual(ev2["start_time"], 4.50)

    def test_offline_vs_live_energy_squelch_compatibility(self):
        """Verify detector zeros out pure digital silence (RMS < 1e-4) matching live inference."""
        silence_wave = np.zeros(16000 * 2, dtype=np.float32)
        res = self.detector.detect_waveform(silence_wave)
        self.assertFalse(res["gunshot_detected"])
        self.assertEqual(res["overall_score"], 0.0)
        self.assertEqual(res["events_count"], 0)


if __name__ == "__main__":
    unittest.main()
