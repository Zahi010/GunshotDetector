import pytest
import numpy as np
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
from experiments.detector_improvement_v9.model_detector_improvement_v9 import (
    DetectorImprovementV9,
    RealTimeStreamDetectorImprovementV9,
    compute_physical_acoustic_features_v9
)

def test_v9_initialization():
    det = DetectorImprovementV9()
    assert det.name == "detector_improvement_v9"
    assert det.version == "9.0.0"
    assert "RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY" in det.safety_designation
    assert det.threshold_base == 0.70
    assert det.threshold_high == 0.85

def test_v9_silent_waveform():
    det = DetectorImprovementV9()
    silence = np.zeros(16000, dtype=np.float32)
    res = det.evaluate_waveform(silence)
    assert res["detected"] is False
    assert res["event_count"] == 0
    assert res["peak_score"] < det.threshold_base

def test_v9_door_slam_suppression():
    det = DetectorImprovementV9()
    # Synthetic sub-bass dominated door slam: 99.8% energy below 500 Hz, peak 0.95
    t = np.linspace(0, 0.96, 15360, endpoint=False)
    sub_bass = 0.95 * np.sin(2 * np.pi * 60 * t) * np.exp(-t * 10)
    # add small onset tick
    sub_bass[:100] += 0.2 * np.sin(2 * np.pi * 1200 * t[:100])
    sub_bass = np.clip(sub_bass, -1.0, 1.0).astype(np.float32)

    acoustics = compute_physical_acoustic_features_v9(sub_bass)
    crest, flat, hi, mid, lo, m2l, rolloff, cent, rms, peak = acoustics
    assert lo > 0.85, f"Expected sub-bass dominance, got lo={lo}"

    # Feed to suppression
    dummy_ys = {i: 0.0 for i in range(521)}
    dummy_ys[420] = 0.85 # Explosion / blast trigger
    supp = det.suppression.apply_suppression(0.95, dummy_ys, acoustics)
    # V9 guarded override should not bypass rumble suppression
    assert supp["adjusted_score"] < 0.70, f"Expected suppression below base threshold, got {supp['adjusted_score']}"

def test_v9_streaming_detector():
    s_det = RealTimeStreamDetectorImprovementV9()
    chunk = np.zeros(7680, dtype=np.float32)
    alerts = s_det.process_chunk(chunk)
    assert len(alerts) == 0
    assert s_det.last_score == 0.0
    assert s_det.in_event is False
