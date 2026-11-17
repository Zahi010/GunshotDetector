"""
Unit and Regression Test Suite for Phase 36: Experimental Acoustic Event Detection Branch
MANDATORY SAFETY DESIGNATION:
RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY
This experimental acoustic machine-learning software is uncertified and must never
be deployed for autonomous emergency dispatch, tactical police response,
active-shooter alerting, automated evacuation, building lockdown, or life-critical
physical security. Safe recorded audio playback only; no live-fire testing.
"""

import os
import sys
import json
import zipfile
import hashlib
from pathlib import Path
import numpy as np
import pandas as pd
import pytest

WORKSPACE_ROOT = Path("E:/gunshot/gunshot")
sys.path.insert(0, str(WORKSPACE_ROOT))
sys.path.insert(0, str(WORKSPACE_ROOT / "experiments" / "phase36"))

from event_state_machine import (
    EventStateMachine,
    EventState,
    TransitionReason,
    merge_phase36_events
)
from acoustic_features import (
    SuppressionMode,
    AcousticSuppressionEngine,
    compute_physical_crest_factor_db,
    YAMNET_ANIMAL_CLASSES,
    YAMNET_AVIATION_VEHICLE_CLASSES
)


def compute_sha256(filepath: Path) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


# =============================================================================
# 1. BASELINE FREEZE INTEGRITY TESTS
# =============================================================================

class TestBaselineFreezeIntegrity:
    """Verifies that historical baselines and artifacts remain 100% frozen."""

    EXPECTED_HASHES = {
        "model_phase14.py": "a268551604ae8b73068435ff10ab3d265065f56e0679757fca5b6bf0f061c065",
        "model_phase17.py": "e2b262b866fdd5d7f1a4ab91a7b8b9bac189ee8cc7a78603b3544ca1579fb819",
        "experiments/phase31/model_phase17_state_reset_candidate.py": "c144b917b56532787e2a9198f2cad4a77dc2095b57962f31d11d250a4d5d9ea5",
        "feature_extractor.py": "1c665b7c1749de98337da0726627710fffe0dcfa56335291b666ae7abcbae94f",
        "config.py": "55749f9d46d561d131fad374064021b73c08274e2a79954efd08570b029b1858",
        "E:/gunshot/gunshot_detection_phase35.zip": "142402f6d48c8167124807d0a5389ed322dd9e57e676f3dd5c3971ab8635f707"
    }

    def test_frozen_baseline_hashes(self):
        for rel_path, exp_hash in self.EXPECTED_HASHES.items():
            p = Path(rel_path) if rel_path.startswith("E:/") else WORKSPACE_ROOT / rel_path
            assert p.exists(), f"Missing frozen file: {p}"
            act_hash = compute_sha256(p)
            assert act_hash == exp_hash, (
                f"Frozen baseline file {rel_path} hash modified! Exp: {exp_hash}, Act: {act_hash}"
            )


# =============================================================================
# 2. STATE MACHINE 10 UNIT TEST SCENARIOS (WORKSTREAM 2)
# =============================================================================

class TestEventStateMachineScenarios:
    """Rigorous unit tests covering all 10 state machine scenarios from Workstream 2."""

    def test_scenario_1_isolated_threshold_crossing(self):
        """Scenario 1: Single isolated hop above threshold. Must decay to IDLE; 0 events."""
        sm = EventStateMachine(threshold_base=0.75, confirm_windows=2, max_hop_gap_s=0.60)
        
        # Hop 0 at t=0.0s: score 0.80 -> transitions to CANDIDATE
        ev = sm.step(window_index=0, start_time=0.0, end_time=0.96, score=0.80)
        assert ev is None
        assert sm.state == EventState.CANDIDATE
        assert len(sm.candidate_windows) == 1

        # Hop 1 at t=0.48s: score 0.30 -> decay to IDLE
        ev = sm.step(window_index=1, start_time=0.48, end_time=1.44, score=0.30)
        assert ev is None
        assert sm.state == EventState.IDLE
        assert len(sm.candidate_windows) == 0

        # Flush at EOF
        final_evs = sm.flush_stream(audio_duration_sec=2.0)
        assert len(final_evs) == 0

    def test_scenario_2_multiple_separated_transients(self):
        """Scenario 2: Multiple transients separated by gap > 0.60s. Must decay; 0 events."""
        sm = EventStateMachine(threshold_base=0.75, confirm_windows=2, max_hop_gap_s=0.60)

        # Transient 1 at t=1.0s
        sm.step(window_index=0, start_time=1.0, end_time=1.96, score=0.82)
        assert sm.state == EventState.CANDIDATE

        # Gap of 1.0s (> 0.60s): Transient 2 arrives at t=2.0s
        sm.step(window_index=1, start_time=2.0, end_time=2.96, score=0.82)
        # Transient 1 should have decayed due to gap violation, transient 2 becomes candidate
        assert sm.state == EventState.CANDIDATE
        assert len(sm.candidate_windows) == 1

        # Silence at t=2.48s
        sm.step(window_index=2, start_time=2.48, end_time=3.44, score=0.10)
        assert sm.state == EventState.IDLE

        final_evs = sm.flush_stream(audio_duration_sec=5.0)
        assert len(final_evs) == 0

    def test_scenario_3_consecutive_qualifying_windows(self):
        """Scenario 3: Two consecutive qualifying windows within 0.60s. Promotes to CONFIRMED."""
        sm = EventStateMachine(threshold_base=0.75, confirm_windows=2, max_hop_gap_s=0.60, cooldown_secs=2.0)

        # Hop 0: score 0.78
        sm.step(window_index=0, start_time=0.0, end_time=0.96, score=0.78)
        assert sm.state == EventState.CANDIDATE

        # Hop 1: score 0.81 (gap 0.48s <= 0.60s)
        sm.step(window_index=1, start_time=0.48, end_time=1.44, score=0.81)
        assert sm.state == EventState.CONFIRMED

        # Hop 2: score drops below off-threshold (0.50) -> transitions to COOLDOWN and emits event
        ev = sm.step(window_index=2, start_time=0.96, end_time=1.92, score=0.40)
        assert ev is not None
        assert sm.state == EventState.COOLDOWN
        assert ev["start_time"] == 0.0
        assert ev["end_time"] == 1.44
        assert ev["peak_score"] == 0.81

    def test_scenario_4_silence_gaps(self):
        """Scenario 4: Silence gap > 0.60s forces candidate decay to IDLE."""
        sm = EventStateMachine(threshold_base=0.75, confirm_windows=2, max_hop_gap_s=0.60)
        sm.step(window_index=0, start_time=0.0, end_time=0.96, score=0.85)
        assert sm.state == EventState.CANDIDATE

        # Next hop arrives 1.5 seconds later (gap 1.5s > 0.60s)
        sm.step(window_index=1, start_time=1.5, end_time=2.46, score=0.20)
        assert sm.state == EventState.IDLE
        assert len(sm.candidate_windows) == 0

    def test_scenario_5_recording_boundaries(self):
        """Scenario 5: Stream boundary reset clears all candidate states without carryover."""
        sm = EventStateMachine(threshold_base=0.75, confirm_windows=2)
        sm.step(window_index=0, start_time=0.0, end_time=0.96, score=0.80)
        assert sm.state == EventState.CANDIDATE
        assert len(sm.candidate_windows) == 1

        # Recording ends -> reset()
        sm.reset()
        assert sm.state == EventState.IDLE
        assert len(sm.candidate_windows) == 0
        assert sm.active_event is None
        assert sm.cooldown_until_s == 0.0

    def test_scenario_6_eof_flush_handling(self):
        """Scenario 6: Guarded EOF handling strictly discards unconfirmed candidates."""
        sm = EventStateMachine(threshold_base=0.75, confirm_windows=2)
        
        # Stream 1 ends while in CANDIDATE state
        sm.step(window_index=0, start_time=10.0, end_time=10.96, score=0.79)
        assert sm.state == EventState.CANDIDATE
        evs = sm.flush_stream(audio_duration_sec=11.0, discard_unconfirmed=True)
        assert len(evs) == 0  # Discarded!
        assert sm.state == EventState.IDLE

        # Stream 2 ends while in CONFIRMED state
        sm.reset()
        sm.step(window_index=0, start_time=1.0, end_time=1.96, score=0.80)
        sm.step(window_index=1, start_time=1.48, end_time=2.44, score=0.82)
        assert sm.state == EventState.CONFIRMED
        evs2 = sm.flush_stream(audio_duration_sec=3.0)
        assert len(evs2) == 1  # Preserved!
        assert evs2[0]["start_time"] == 1.0

    def test_scenario_7_streaming_chunk_boundaries(self):
        """Scenario 7: Chunk boundary streaming yields identical event boundaries."""
        windows = [
            {"window_index": 0, "start_time": 0.0, "end_time": 0.96, "score": 0.20},
            {"window_index": 1, "start_time": 0.48, "end_time": 1.44, "score": 0.85},
            {"window_index": 2, "start_time": 0.96, "end_time": 1.92, "score": 0.88},
            {"window_index": 3, "start_time": 1.44, "end_time": 2.40, "score": 0.30},
            {"window_index": 4, "start_time": 1.92, "end_time": 2.88, "score": 0.10},
        ]
        
        # Batch merge
        evs_batch, _ = merge_phase36_events(windows, threshold_base=0.75, threshold_off=0.50, cooldown_secs=2.0)
        assert len(evs_batch) == 1
        assert evs_batch[0]["start_time"] == 0.48
        assert evs_batch[0]["end_time"] == 1.92

        # Step by step simulation
        sm = EventStateMachine(threshold_base=0.75, threshold_off=0.50, cooldown_secs=2.0)
        stream_evs = []
        for w in windows:
            ev = sm.step(w["window_index"], w["start_time"], w["end_time"], w["score"])
            if ev:
                stream_evs.append(ev)
        stream_evs.extend(sm.flush_stream(audio_duration_sec=3.0))
        
        assert len(stream_evs) == 1
        assert stream_evs[0]["start_time"] == evs_batch[0]["start_time"]
        assert stream_evs[0]["end_time"] == evs_batch[0]["end_time"]

    def test_scenario_8_overlapping_candidate_immediate_promotion(self):
        """Scenario 8: High confidence transient with sharp crest factor triggers immediate promotion."""
        sm = EventStateMachine(threshold_base=0.75, threshold_high=0.88, single_win_min_crest_db=12.0)
        
        # Window with score 0.90 and sharp crest factor (14.5 dB) -> immediate CONFIRMED
        sm.step(window_index=0, start_time=0.5, end_time=1.46, score=0.90, crest_factor_db=14.5)
        assert sm.state == EventState.CONFIRMED
        assert sm.active_event is not None
        assert sm.active_event["confirmed"] is True

    def test_scenario_9_cooldown_refractory(self):
        """Scenario 9: Cooldown refractory period blocks repeated event triggers."""
        sm = EventStateMachine(threshold_base=0.75, cooldown_secs=2.0)
        
        # Window 0 & 1 confirm event
        sm.step(window_index=0, start_time=1.0, end_time=1.96, score=0.80)
        sm.step(window_index=1, start_time=1.48, end_time=2.44, score=0.82)
        assert sm.state == EventState.CONFIRMED

        # Window 2 drops below threshold -> emits event, enters COOLDOWN until 2.44 + 2.0 = 4.44s
        ev = sm.step(window_index=2, start_time=1.96, end_time=2.92, score=0.30)
        assert ev is not None
        assert sm.state == EventState.COOLDOWN
        assert sm.cooldown_until_s == pytest.approx(4.44, 0.01)

        # Window 3 at t=2.44s with high score (0.95) arrives during cooldown
        ev_suppressed = sm.step(window_index=3, start_time=2.44, end_time=3.40, score=0.95)
        assert ev_suppressed is None
        assert sm.state == EventState.COOLDOWN  # Remains in cooldown! No new event!

    def test_scenario_10_long_continuous_background_tones(self):
        """Scenario 10: Steady background tone at score 0.55 < base 0.75 remains in IDLE throughout."""
        sm = EventStateMachine(threshold_base=0.75)
        for i in range(25):
            ev = sm.step(window_index=i, start_time=i * 0.48, end_time=i * 0.48 + 0.96, score=0.55)
            assert ev is None
            assert sm.state == EventState.IDLE
        assert len(sm.candidate_windows) == 0
        evs = sm.flush_stream(audio_duration_sec=15.0)
        assert len(evs) == 0


# =============================================================================
# 3. ACOUSTIC SUPPRESSION & CREST FACTOR TESTS
# =============================================================================

class TestAcousticSuppressionAndCrestFactor:
    """Verifies suppression modes, aviation protection, and crest factor DSP."""

    def test_suppression_mode_none(self):
        engine = AcousticSuppressionEngine(mode=SuppressionMode.NONE)
        # Mock dog bark YAMNet scores
        yamnet_scores = np.zeros(521)
        yamnet_scores[73] = 0.90  # Dog
        res = engine.apply_suppression(raw_score=0.80, yamnet_scores=yamnet_scores)
        assert res["adjusted_score"] == 0.80
        assert res["suppression_active"] is False

    def test_suppression_mode_legacy_animal(self):
        engine = AcousticSuppressionEngine(mode=SuppressionMode.LEGACY_ANIMAL, legacy_attenuation=0.30)
        yamnet_scores = np.zeros(521)
        yamnet_scores[73] = 0.90  # Dog
        res = engine.apply_suppression(raw_score=0.40, yamnet_scores=yamnet_scores)
        assert res["adjusted_score"] == pytest.approx(0.40 * 0.30, 0.01)
        assert res["suppression_active"] is True
        assert res["suppression_category"] == "animal_vocalization_legacy"

    def test_suppression_mode_conservative_aviation_protection(self):
        """Aviation sound (e.g. Helicopter 338) must NOT be suppressed by animal factor."""
        engine = AcousticSuppressionEngine(mode=SuppressionMode.CONSERVATIVE, conservative_attenuation=0.50)
        yamnet_scores = np.zeros(521)
        yamnet_scores[73] = 0.40   # Weak animal
        yamnet_scores[338] = 0.85  # Strong helicopter
        res = engine.apply_suppression(raw_score=0.80, yamnet_scores=yamnet_scores)
        assert res["suppression_active"] is False
        assert res["adjusted_score"] == 0.80

    def test_crest_factor_dsp(self):
        """Sine wave crest factor is ~3.01 dB; impulsive spike is > 12 dB."""
        sr = 16000
        # 1. Pure sine wave: peak = 1.0, rms = 1 / sqrt(2) -> peak/rms = sqrt(2) -> 20*log10(sqrt(2)) = 3.01 dB
        t = np.linspace(0, 1, sr, endpoint=False)
        sine_wave = np.sin(2 * np.pi * 440 * t)
        cf_sine = compute_physical_crest_factor_db(sine_wave)
        assert cf_sine == pytest.approx(3.01, abs=0.2)

        # 2. Impulsive click in quiet background
        click_wave = np.zeros(sr, dtype=np.float32)
        click_wave[100:105] = 1.0
        cf_click = compute_physical_crest_factor_db(click_wave)
        assert cf_click > 15.0


# =============================================================================
# 4. CONFIGURATION & ARTIFACT INTEGRITY TESTS
# =============================================================================

class TestPhase36ConfigAndDatasetIntegrity:
    """Verifies Phase 36 configuration, dataset registry, and release archive."""

    def test_config_phase36_json(self):
        cfg_path = WORKSPACE_ROOT / "experiments" / "phase36" / "config_phase36.json"
        assert cfg_path.exists()
        with open(cfg_path, "r", encoding="utf-8") as f:
            cfg = json.load(f)
        assert cfg["branch_identifier"] == "PHASE36_EXPERIMENTAL_EVENT_STATE_BRANCH_V1"
        assert cfg["thresholds"]["threshold_base"] == 0.75
        assert cfg["thresholds"]["threshold_high"] == 0.88
        assert cfg["thresholds"]["threshold_off"] == 0.48
        assert cfg["thresholds"]["confirm_windows"] == 2
        assert cfg["thresholds"]["max_hop_gap_s"] == 0.60
        assert "CONSERVATIVE" in cfg["suppression"]["supported_modes"]

    def test_dataset_registry_partition_isolation(self):
        reg_path = WORKSPACE_ROOT / "reports" / "phase36_dataset_registry.csv"
        assert reg_path.exists()
        df = pd.read_csv(reg_path)
        assert len(df) == 87, f"Expected 87 evaluation files, found {len(df)}"

        # Assert zero overlap with 23-stream historical benchmark
        hist_streams = [
            "170502-001", "170502-002", "170502-003", "170502-004", "170502-005",
            "170502-006", "170502-007", "170502-008", "170502-009", "170502-010",
            "2022-02-19_06-00-00",
            "stream_01", "stream_02", "stream_03", "stream_04", "stream_05", "stream_06",
            "2023-05-23_06-00-00", "2023-05-23_07-00-00", "2023-05-23_08-00-00",
            "2023-05-23_09-00-00", "2023-05-23_10-00-00", "2023-05-23_11-00-00"
        ]
        rec_ids = set(df["recording_id"].values)
        for s in hist_streams:
            assert s not in rec_ids, (
                f"Historical benchmark stream {s} leaked into independent evaluation corpus!"
            )

    def test_release_zip_crc_integrity(self):
        zip_path = Path("E:/gunshot/gunshot_detection_phase36.zip")
        if zip_path.exists():
            with zipfile.ZipFile(zip_path, "r") as zf:
                corrupted = zf.testzip()
                assert corrupted is None, f"Corrupted file in Phase 36 zip archive: {corrupted}"
