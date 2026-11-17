"""
Unit Tests for Detector Improvement V10.
MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.
"""

import pytest
import numpy as np
import pathlib
import soundfile as sf
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent.parent))

from experiments.detector_improvement_v10.model_detector_improvement_v10 import (
    DetectorImprovementV10,
    RealTimeStreamDetectorImprovementV10
)

MANDATORY_SAFETY_DESIGNATION = "RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY"


def test_v10_initialization_and_metadata():
    det = DetectorImprovementV10()
    assert det.name == "detector_improvement_v10"
    assert det.version == "10.0.0"
    assert det.safety_designation == MANDATORY_SAFETY_DESIGNATION
    assert det.consensus_cfg.get("enabled", True) is True


def test_v10_silent_waveform():
    det = DetectorImprovementV10()
    silent_audio = np.zeros(16000 * 3, dtype=np.float32)
    res = det.evaluate_waveform(silent_audio, sr=16000)
    assert res["detected"] is False
    assert len(res["events"]) == 0
    assert res["peak_score"] < 0.10


def test_v10_reset():
    det = DetectorImprovementV10()
    det.evaluate_waveform(np.random.normal(0, 0.01, 16000).astype(np.float32), sr=16000)
    det.reset()
    assert det.fsm.state.name == "IDLE"
    assert len(det.estimator.transition_log) == 0


def test_v10_door_slam_suppression():
    det = DetectorImprovementV10()
    slam_path = pathlib.Path(__file__).parent.parent.parent / "data/background/hard_negatives/door_slam/hard_neg_door_slam_001.wav"
    if slam_path.exists():
        audio, sr = sf.read(str(slam_path), dtype="float32")
        res = det.evaluate_waveform(audio, sr=sr)
        assert res["detected"] is False, "Door slam false alarm not suppressed!"


def test_v10_balloon_burst_suppression():
    det = DetectorImprovementV10()
    bb_path = pathlib.Path(__file__).parent.parent.parent / "data/background/hard_negatives/balloon_burst/hard_neg_balloon_burst_001.wav"
    if bb_path.exists():
        audio, sr = sf.read(str(bb_path), dtype="float32")
        res = det.evaluate_waveform(audio, sr=sr)
        assert res["detected"] is False, "Balloon burst false alarm not suppressed!"


def test_v10_streaming_detector():
    stream_det = RealTimeStreamDetectorImprovementV10()
    assert stream_det.safety_designation == MANDATORY_SAFETY_DESIGNATION
    chunk = np.zeros(16000, dtype=np.float32)
    events = stream_det.process_chunk(chunk, sr=16000)
    assert isinstance(events, list)
    assert len(events) == 0
    stream_det.reset()
    assert len(stream_det.buffer) == 0

