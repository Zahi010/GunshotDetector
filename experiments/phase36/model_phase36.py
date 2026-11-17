"""
Phase 36 Experimental Acoustic Event Detector
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
import time
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import numpy as np

# Ensure root is in sys.path
WORKSPACE_ROOT = Path("E:/gunshot/gunshot")
if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))

PHASE36_DIR = WORKSPACE_ROOT / "experiments" / "phase36"
if str(PHASE36_DIR) not in sys.path:
    sys.path.insert(0, str(PHASE36_DIR))

from event_state_machine import EventStateMachine, EventState, TransitionReason, merge_phase36_events
from acoustic_features import (
    SuppressionMode,
    AcousticSuppressionEngine,
    compute_physical_crest_factor_db
)

# Import read-only baseline feature extractor and models
import joblib
import tensorflow as tf
from feature_extractor import YAMNetFeatureExtractor


class Phase36CandidateGunshotDetector:
    """
    Phase 36 Experimental Gunshot Detector.
    Features:
    1. Deterministic 4-state event state machine (IDLE, CANDIDATE, CONFIRMED, COOLDOWN).
    2. Explicit candidate continuity rule with strictly guarded EOF handling.
    3. Isolated, switchable acoustic suppression factor (NONE, LEGACY_ANIMAL, CONSERVATIVE).
    4. Complete auditability: logs raw scores, adjusted scores, and all state transitions.
    """

    def __init__(
        self,
        config_path: Optional[str] = None,
        suppression_mode: SuppressionMode = SuppressionMode.CONSERVATIVE,
        models_dir: Optional[str] = None
    ):
        if config_path is None:
            config_path = str(PHASE36_DIR / "config_phase36.json")
        with open(config_path, "r", encoding="utf-8") as f:
            self.config = json.load(f)

        self.branch_id = self.config.get("branch_identifier", "PHASE36_EXPERIMENTAL_V1")
        self.thresholds = self.config["thresholds"]
        self.crest_cfg = self.config["crest_factor_gates"]
        self.supp_cfg = self.config["suppression"]
        self.ensemble_weights = self.config["ensemble"]["weights"]

        # Suppression mode
        if isinstance(suppression_mode, str):
            suppression_mode = SuppressionMode(suppression_mode)
        self.suppression_mode = suppression_mode

        # Initialize suppression engine
        legacy_cfg = self.supp_cfg.get("legacy_animal", {})
        cons_cfg = self.supp_cfg.get("conservative", {})
        self.suppression_engine = AcousticSuppressionEngine(
            mode=self.suppression_mode,
            legacy_animal_thresh=legacy_cfg.get("animal_thresh", 0.35),
            legacy_animal_ratio=legacy_cfg.get("animal_ratio", 2.0),
            legacy_attenuation=legacy_cfg.get("attenuation", 0.30),
            conservative_animal_thresh=cons_cfg.get("animal_thresh", 0.50),
            conservative_animal_ratio=cons_cfg.get("animal_ratio", 2.5),
            conservative_attenuation=cons_cfg.get("attenuation", 0.50),
            conservative_min_crest_db=cons_cfg.get("min_crest_db", 12.0)
        )

        # Load trained frozen model bundle
        if models_dir is None:
            models_dir = str(WORKSPACE_ROOT / "models" / "gunshot_yamnet_bundle")
        self.models_dir = Path(models_dir)

        print(f"[Phase 36 Detector] Initializing branch {self.branch_id} (Suppression: {self.suppression_mode.value})...")
        self.feature_extractor = YAMNetFeatureExtractor()
        self.yamnet_model = self.feature_extractor.model
        self._load_bundle()

    def _load_bundle(self) -> None:
        """Load frozen classifier models from existing bundle."""
        self.catboost = joblib.load(self.models_dir / "catboost_model.joblib")
        self.lightgbm = joblib.load(self.models_dir / "lightgbm_model.joblib")
        self.xgboost = joblib.load(self.models_dir / "xgboost_model.joblib")
        self.keras_head = tf.keras.models.load_model(
            self.models_dir / "classifier_head.keras",
            compile=False
        )

    def compute_ensemble_score(self, embeddings: np.ndarray) -> np.ndarray:
        """Computes weighted ensemble probability from 1024-d YAMNet embeddings."""
        if embeddings is None or len(embeddings) == 0:
            return np.array([], dtype=np.float32)

        p_cb = self.catboost.predict_proba(embeddings)[:, 1]
        p_lgb = self.lightgbm.predict_proba(embeddings)[:, 1]
        p_xgb = self.xgboost.predict_proba(embeddings)[:, 1]
        p_keras = self.keras_head.predict(embeddings, verbose=0).ravel()

        w = self.ensemble_weights
        ensemble_score = (
            w["catboost"] * p_cb +
            w["lightgbm"] * p_lgb +
            w["xgboost"] * p_xgb +
            w["keras_head"] * p_keras
        )
        return ensemble_score.astype(np.float32)

    def evaluate_waveform(
        self,
        waveform: np.ndarray,
        sample_rate: int = 16000,
        filename: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Executes end-to-end evaluation on a continuous or discrete audio waveform.
        Returns:
        - events: Confirmed detected events
        - windows: Per-window scores and suppression tracking
        - transition_log: Full state-machine transition history
        - metrics: Processing latency and throughput
        """
        t0 = time.perf_counter()
        if waveform.ndim > 1:
            waveform = np.mean(waveform, axis=1)
        dur_s = len(waveform) / float(sample_rate)

        # 1. Compute physical crest factor
        crest_db = compute_physical_crest_factor_db(waveform)

        # 2. Extract YAMNet embeddings and class predictions
        min_samples = 15360 # 0.96s
        if len(waveform) < min_samples:
            pad_len = min_samples - len(waveform)
            eval_wave = np.pad(waveform, (0, pad_len), mode="constant")
        else:
            eval_wave = waveform

        yamnet_scores, embeddings, _ = self.yamnet_model(eval_wave)
        yamnet_scores = yamnet_scores.numpy()
        embeddings = embeddings.numpy()

        if len(embeddings) == 0:
            return {
                "events": [],
                "windows": [],
                "transition_log": [],
                "crest_factor_db": crest_db,
                "duration_seconds": dur_s,
                "latency_ms": (time.perf_counter() - t0) * 1000.0
            }

        # 3. Compute raw ensemble scores
        raw_scores = self.compute_ensemble_score(embeddings)

        # 4. Window timing definitions
        hop_s = 0.48
        win_len_s = 0.96
        num_windows = len(raw_scores)

        # 5. Process windows with suppression and state-machine
        windows = []
        fsm = EventStateMachine(
            threshold_base=self.thresholds["threshold_base"],
            threshold_high=self.thresholds["threshold_high"],
            threshold_off=self.thresholds["threshold_off"],
            confirm_windows=self.thresholds["confirm_windows"],
            cooldown_secs=self.thresholds["cooldown_secs"],
            max_hop_gap_s=self.thresholds["max_hop_gap_s"],
            min_crest_factor_db=self.crest_cfg["min_crest_factor_db"],
            single_win_min_crest_db=self.crest_cfg["single_win_min_crest_db"],
            allow_short_clip_exception=self.crest_cfg["allow_short_clip_exception"]
        )

        for i in range(num_windows):
            st = i * hop_s
            et = min(dur_s, st + win_len_s)
            raw_sc = float(raw_scores[i])
            ym_sc = yamnet_scores[i] if (yamnet_scores is not None and i < len(yamnet_scores)) else None

            # Apply suppression
            is_in_conf = (fsm.state == EventState.CONFIRMED)
            supp_result = self.suppression_engine.apply_suppression(
                raw_score=raw_sc,
                yamnet_scores=ym_sc,
                crest_factor_db=crest_db,
                is_in_confirmed_event=is_in_conf,
                threshold_off=self.thresholds["threshold_off"]
            )

            win_record = {
                "window_index": i,
                "start_time": round(st, 3),
                "end_time": round(et, 3),
                "raw_score": raw_sc,
                "score": supp_result["adjusted_score"],
                "crest_factor_db": crest_db,
                "suppression_active": supp_result["suppression_active"],
                "suppression_category": supp_result["suppression_category"],
                "suppression_strength": supp_result["suppression_strength"],
                "suppression_reason": supp_result["suppression_reason"]
            }
            windows.append(win_record)

            # Feed to state machine
            fsm.process_window(
                win_record,
                crest_factor_db=crest_db,
                audio_duration_sec=dur_s,
                total_windows_in_stream=num_windows
            )

        # End of stream flush
        fsm.flush()
        t1 = time.perf_counter()

        return {
            "branch_identifier": self.branch_id,
            "filename": filename,
            "duration_seconds": round(dur_s, 4),
            "crest_factor_db": round(crest_db, 2),
            "suppression_mode": self.suppression_mode.value,
            "events": fsm.events_emitted,
            "windows": windows,
            "transition_log": fsm.transition_log,
            "windows_count": num_windows,
            "latency_ms": round((t1 - t0) * 1000.0, 2)
        }


class RealTimeStreamDetectorPhase36:
    """
    Streaming Phase 36 Audio Detector for real-time buffer processing.
    """

    def __init__(
        self,
        config_path: Optional[str] = None,
        suppression_mode: SuppressionMode = SuppressionMode.CONSERVATIVE
    ):
        self.detector = Phase36CandidateGunshotDetector(
            config_path=config_path,
            suppression_mode=suppression_mode
        )
        self.sample_rate = self.detector.config["dsp"]["target_sample_rate"]
        self.window_samples = self.detector.config["dsp"]["window_size_samples"]  # 15360 = 0.96s
        self.hop_samples = self.detector.config["dsp"]["hop_size_samples"]        # 7680 = 0.48s

        self.audio_buffer = np.array([], dtype=np.float32)
        self.stream_offset_samples = 0
        self.fsm = EventStateMachine(
            threshold_base=self.detector.thresholds["threshold_base"],
            threshold_high=self.detector.thresholds["threshold_high"],
            threshold_off=self.detector.thresholds["threshold_off"],
            confirm_windows=self.detector.thresholds["confirm_windows"],
            cooldown_secs=self.detector.thresholds["cooldown_secs"],
            max_hop_gap_s=self.detector.thresholds["max_hop_gap_s"],
            min_crest_factor_db=self.detector.crest_cfg["min_crest_factor_db"],
            single_win_min_crest_db=self.detector.crest_cfg["single_win_min_crest_db"],
            allow_short_clip_exception=self.detector.crest_cfg["allow_short_clip_exception"]
        )

    def reset(self) -> None:
        """Deterministic reset across streaming stream boundaries."""
        self.audio_buffer = np.array([], dtype=np.float32)
        self.stream_offset_samples = 0
        self.fsm.reset()

    def process_chunk(self, chunk: np.ndarray) -> List[Dict[str, Any]]:
        """
        Consumes an audio chunk and returns any events that confirmed/completed.
        """
        if chunk is None or len(chunk) == 0:
            return []

        self.audio_buffer = np.concatenate([self.audio_buffer, chunk.astype(np.float32)])
        emitted_events = []

        while len(self.audio_buffer) >= self.window_samples:
            window_audio = self.audio_buffer[:self.window_samples]
            st = self.stream_offset_samples / float(self.sample_rate)
            et = (self.stream_offset_samples + self.window_samples) / float(self.sample_rate)

            # Compute features
            crest_db = compute_physical_crest_factor_db(window_audio)
            emb, ym_scores = self.detector.feature_extractor.extract_features(window_audio, self.sample_rate)
            if len(emb) > 0:
                raw_sc = float(self.detector.compute_ensemble_score(emb)[0])
                ym = ym_scores[0] if (ym_scores is not None and len(ym_scores) > 0) else None

                is_in_conf = (self.fsm.state == EventState.CONFIRMED)
                supp_res = self.detector.suppression_engine.apply_suppression(
                    raw_score=raw_sc,
                    yamnet_scores=ym,
                    crest_factor_db=crest_db,
                    is_in_confirmed_event=is_in_conf,
                    threshold_off=self.detector.thresholds["threshold_off"]
                )

                win_rec = {
                    "start_time": st,
                    "end_time": et,
                    "raw_score": raw_sc,
                    "score": supp_res["adjusted_score"],
                    "crest_factor_db": crest_db,
                    "suppression_active": supp_res["suppression_active"],
                    "suppression_category": supp_res["suppression_category"],
                    "suppression_strength": supp_res["suppression_strength"]
                }

                ev = self.fsm.process_window(win_rec, crest_factor_db=crest_db)
                if ev is not None:
                    emitted_events.append(ev)

            # Advance by hop
            self.audio_buffer = self.audio_buffer[self.hop_samples:]
            self.stream_offset_samples += self.hop_samples

        return emitted_events
