"""
Detector Improvement V2 - Production Experimental Gunshot Detector
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
import threading
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import numpy as np

# Ensure workspace root is in sys.path
WORKSPACE_ROOT = Path("E:/gunshot/gunshot")
if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))

# Event state machine from phase36 branch
PHASE36_DIR = WORKSPACE_ROOT / "experiments" / "phase36"
if str(PHASE36_DIR) not in sys.path:
    sys.path.insert(0, str(PHASE36_DIR))

from event_state_machine import EventStateMachine, EventState, TransitionReason
from acoustic_features import compute_physical_crest_factor_db

import config
from feature_extractor import YAMNetFeatureExtractor
from model import load_model_bundle

# YAMNet semantic class indices
YAMNET_CLASS_GUNSHOT = 421
YAMNET_CLASS_MACHINE_GUN = 422
YAMNET_CLASS_ARTILLERY = 424
YAMNET_CLASS_CAP_GUN = 425

YAMNET_CLASS_EXPLOSION = 420
YAMNET_CLASS_BURST_POP = 428
YAMNET_CLASS_CRACK = 434
YAMNET_CLASS_BANG = 460

YAMNET_CLASS_THUNDERSTORM = 280
YAMNET_CLASS_THUNDER = 281
YAMNET_CLASS_FIREWORKS = 426
YAMNET_CLASS_FIRECRACKER = 427

YAMNET_CLASS_DOG = 69
YAMNET_CLASS_BARK = 70
YAMNET_CLASS_YIP = 75
YAMNET_CLASS_CANIDAE = 117

YAMNET_CLASS_FIRE = 292
YAMNET_CLASS_CRACKLE = 293

YAMNET_CLASS_POLICE_CAR = 317
YAMNET_CLASS_AMBULANCE = 318
YAMNET_CLASS_FIRE_ENGINE = 319
YAMNET_CLASS_SIREN = 390
YAMNET_CLASS_CIVIL_DEFENSE = 391

YAMNET_CLASS_WIND = 277
YAMNET_CLASS_WIND_NOISE_MIC = 279

YAMNET_CLASS_HAMMER = 413
YAMNET_CLASS_JACKHAMMER = 414
YAMNET_CLASS_SLAM = 352
YAMNET_CLASS_KNOCK = 353
YAMNET_CLASS_CLAP = 58

GUN_CLASSES = [YAMNET_CLASS_GUNSHOT, YAMNET_CLASS_MACHINE_GUN, YAMNET_CLASS_ARTILLERY, YAMNET_CLASS_CAP_GUN]
BALLISTIC_CLASSES = [YAMNET_CLASS_EXPLOSION, YAMNET_CLASS_GUNSHOT, YAMNET_CLASS_MACHINE_GUN, YAMNET_CLASS_ARTILLERY, YAMNET_CLASS_CAP_GUN, YAMNET_CLASS_BURST_POP, YAMNET_CLASS_CRACK, YAMNET_CLASS_BANG]
FIREWORKS_CLASSES = [YAMNET_CLASS_FIREWORKS, YAMNET_CLASS_FIRECRACKER]
THUNDER_CLASSES = [YAMNET_CLASS_THUNDERSTORM, YAMNET_CLASS_THUNDER]
DOG_CLASSES = [YAMNET_CLASS_DOG, YAMNET_CLASS_BARK, YAMNET_CLASS_YIP, YAMNET_CLASS_CANIDAE]
CRACKLE_CLASSES = [YAMNET_CLASS_FIRE, YAMNET_CLASS_CRACKLE]
SIREN_CLASSES = [YAMNET_CLASS_POLICE_CAR, YAMNET_CLASS_AMBULANCE, YAMNET_CLASS_FIRE_ENGINE, YAMNET_CLASS_SIREN, YAMNET_CLASS_CIVIL_DEFENSE]
WIND_CLASSES = [YAMNET_CLASS_WIND, YAMNET_CLASS_WIND_NOISE_MIC]
IMPACT_CLASSES = [YAMNET_CLASS_HAMMER, YAMNET_CLASS_JACKHAMMER, YAMNET_CLASS_SLAM, YAMNET_CLASS_KNOCK, YAMNET_CLASS_CLAP]

# Non-target semantic broad categories (Speech, Animals, Vehicles, Outside)
NON_TARGET_SEMANTIC_CLASSES = (
    [0] + # Speech
    list(range(67, 118)) + # Animal vocalizations
    list(range(300, 331)) + # Motor vehicles and traffic
    [502, 503, 504] # Outside / Natural ambient
)


class CalibratedAcousticSuppressionV2:
    """
    Calibrated Multi-Category Semantic Suppression V2 with:
    1. Ballistic Acoustic Coherence Safeguard (rejects tabular tree artifacts on non-ballistic audio).
    2. Two-tier Pyrotechnic Gating (standard vs dominant fireworks).
    3. Infrasonic Rumble & Wind Buffeting Attenuation.
    4. Mechanical Impact & Clatter Suppression.
    5. Prior categories (thunder, canine, crackle, siren) preserved with calibrated thresholds.
    """

    def __init__(self, suppression_cfg: Dict[str, Any]):
        self.enabled = suppression_cfg.get("enabled", True)
        self.coherence_cfg = suppression_cfg.get("coherence_safeguard", {
            "enabled": True,
            "ballistic_max_threshold": 0.015,
            "non_target_threshold": 0.12,
            "attenuation": 0.20
        })
        self.thun_cfg = suppression_cfg.get("thunder", {"threshold": 0.25, "ratio": 1.5, "attenuation": 0.30})
        self.fw_cfg = suppression_cfg.get("fireworks", {
            "dominant_threshold": 0.45,
            "dominant_ratio": 1.8,
            "dominant_gun_max": 0.25,
            "dominant_attenuation": 0.30,
            "standard_threshold": 0.30,
            "standard_ratio": 1.5,
            "standard_gun_max": 0.12,
            "standard_attenuation": 0.35
        })
        self.wind_cfg = suppression_cfg.get("wind_buffeting", {"threshold": 0.25, "ratio": 1.5, "attenuation": 0.25})
        self.impact_cfg = suppression_cfg.get("mechanical_impact", {"threshold": 0.30, "ratio": 1.5, "gun_max": 0.20, "attenuation": 0.35})
        self.dog_cfg = suppression_cfg.get("canine", {"threshold": 0.30, "ratio": 1.5, "attenuation": 0.35})
        self.crackle_cfg = suppression_cfg.get("fire_crackle", {"threshold": 0.25, "ratio": 1.5, "attenuation": 0.35})
        self.siren_cfg = suppression_cfg.get("siren", {"threshold": 0.35, "ratio": 1.5, "attenuation": 0.30})

    def apply_suppression(
        self,
        raw_score: float,
        yamnet_scores: Optional[np.ndarray],
        is_in_confirmed_event: bool = False
    ) -> Dict[str, Any]:
        """Calculates calibrated score after evaluating multi-category acoustic semantics."""
        if not self.enabled or yamnet_scores is None or len(yamnet_scores) == 0 or is_in_confirmed_event:
            return {
                "adjusted_score": float(raw_score),
                "suppression_active": False,
                "suppression_category": None,
                "suppression_strength": 1.0,
                "suppression_reason": None
            }

        gun_score = max(float(yamnet_scores[c]) for c in GUN_CLASSES)
        ballistic_score = max(float(yamnet_scores[c]) for c in BALLISTIC_CLASSES)
        fw_score = max(float(yamnet_scores[c]) for c in FIREWORKS_CLASSES)
        thun_score = max(float(yamnet_scores[c]) for c in THUNDER_CLASSES)
        dog_score = max(float(yamnet_scores[c]) for c in DOG_CLASSES)
        crackle_score = max(float(yamnet_scores[c]) for c in CRACKLE_CLASSES)
        siren_score = max(float(yamnet_scores[c]) for c in SIREN_CLASSES)
        wind_score = max(float(yamnet_scores[c]) for c in WIND_CLASSES)
        impact_score = max(float(yamnet_scores[c]) for c in IMPACT_CLASSES)
        non_target_score = max(float(yamnet_scores[c]) for c in NON_TARGET_SEMANTIC_CLASSES)

        adj_score = float(raw_score)
        supp_cat = None
        strength = 1.0

        # 1. Non-ballistic acoustic coherence safeguard
        if (
            self.coherence_cfg.get("enabled", True)
            and ballistic_score < self.coherence_cfg.get("ballistic_max_threshold", 0.015)
            and non_target_score >= self.coherence_cfg.get("non_target_threshold", 0.12)
        ):
            strength = float(self.coherence_cfg.get("attenuation", 0.20))
            adj_score *= strength
            supp_cat = "non_ballistic_coherence_rejection"

        # 2. Thunder suppression
        elif thun_score > self.thun_cfg["threshold"] and thun_score >= gun_score * self.thun_cfg["ratio"]:
            strength = float(self.thun_cfg["attenuation"])
            adj_score *= strength
            supp_cat = "thunder"

        # 3. Fireworks suppression (Two-tier refined)
        elif (
            fw_score >= self.fw_cfg["dominant_threshold"]
            and fw_score >= gun_score * self.fw_cfg["dominant_ratio"]
            and gun_score < self.fw_cfg["dominant_gun_max"]
        ):
            strength = float(self.fw_cfg["dominant_attenuation"])
            adj_score *= strength
            supp_cat = "fireworks_dominant"

        elif (
            fw_score >= self.fw_cfg["standard_threshold"]
            and fw_score >= gun_score * self.fw_cfg["standard_ratio"]
            and gun_score < self.fw_cfg["standard_gun_max"]
        ):
            strength = float(self.fw_cfg["standard_attenuation"])
            adj_score *= strength
            supp_cat = "fireworks_standard"

        # 4. Wind buffeting / infrasonic rumble
        elif wind_score >= self.wind_cfg["threshold"] and wind_score >= gun_score * self.wind_cfg["ratio"]:
            strength = float(self.wind_cfg["attenuation"])
            adj_score *= strength
            supp_cat = "wind_buffeting"

        # 5. Mechanical impacts / heavy tools
        elif (
            impact_score >= self.impact_cfg["threshold"]
            and impact_score >= gun_score * self.impact_cfg["ratio"]
            and gun_score < self.impact_cfg["gun_max"]
        ):
            strength = float(self.impact_cfg["attenuation"])
            adj_score *= strength
            supp_cat = "mechanical_impact"

        # 6. Canine vocalization
        elif dog_score > self.dog_cfg["threshold"] and dog_score >= gun_score * self.dog_cfg["ratio"]:
            strength = float(self.dog_cfg["attenuation"])
            adj_score *= strength
            supp_cat = "canine_bark"

        # 7. Fire crackle
        elif crackle_score > self.crackle_cfg["threshold"] and crackle_score >= gun_score * self.crackle_cfg["ratio"]:
            strength = float(self.crackle_cfg["attenuation"])
            adj_score *= strength
            supp_cat = "fire_crackle"

        # 8. Siren / Emergency transit
        elif siren_score > self.siren_cfg["threshold"] and siren_score >= gun_score * self.siren_cfg["ratio"]:
            strength = float(self.siren_cfg["attenuation"])
            adj_score *= strength
            supp_cat = "siren"

        return {
            "adjusted_score": float(round(adj_score, 4)),
            "suppression_active": supp_cat is not None,
            "suppression_category": supp_cat,
            "suppression_strength": float(strength),
            "suppression_reason": supp_cat
        }


class EventStateMachineV2(EventStateMachine):
    """
    Deterministic 4-State Refractory State Machine V2:
    Extends the Phase 36 FSM with a calibrated Single-Round Impulse Exception:
    Promotes authentic high-impulse isolated candidates that decay before Window 2,
    provided they exhibit sharp crest factor (>= min_crest) and have not been suppressed.
    """

    def __init__(
        self,
        threshold_base: float = 0.75,
        threshold_high: float = 0.88,
        threshold_off: float = 0.48,
        confirm_windows: int = 2,
        cooldown_secs: float = 2.0,
        max_hop_gap_s: float = 0.60,
        min_crest_factor_db: float = 8.8,
        single_win_min_crest_db: float = 12.0,
        allow_short_clip_exception: bool = True,
        allow_single_impulse_exception: bool = True,
        single_impulse_min_score: float = 0.82,
        single_impulse_min_crest_db: float = 14.0,
        single_impulse_max_dur_sec: float = 5.0
    ):
        super().__init__(
            threshold_base=threshold_base,
            threshold_high=threshold_high,
            threshold_off=threshold_off,
            confirm_windows=confirm_windows,
            cooldown_secs=cooldown_secs,
            max_hop_gap_s=max_hop_gap_s,
            min_crest_factor_db=min_crest_factor_db,
            single_win_min_crest_db=single_win_min_crest_db,
            allow_short_clip_exception=allow_short_clip_exception
        )
        self.allow_single_impulse_exception = allow_single_impulse_exception
        self.single_impulse_min_score = single_impulse_min_score
        self.single_impulse_min_crest_db = single_impulse_min_crest_db
        self.single_impulse_max_dur_sec = single_impulse_max_dur_sec

    def process_window(
        self,
        window: Dict[str, Any],
        crest_factor_db: Optional[float] = None,
        audio_duration_sec: Optional[float] = None,
        total_windows_in_stream: Optional[int] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Process a single acoustic evaluation window through FSM V2.
        If a decaying candidate qualifies under the Single-Round Impulse Exception,
        promotes it to CONFIRMED before entering COOLDOWN.
        """
        st = float(window["start_time"])
        et = float(window["end_time"])
        score = float(window["score"])
        raw_score = float(window.get("raw_score", score))

        # Check decaying candidate state before parent process_window
        if self.state == EventState.CANDIDATE:
            time_gap = (st - self.last_window_time) if self.last_window_time is not None else 0.0
            is_gap = (time_gap > self.max_hop_gap_s)
            is_decay = (score < self.threshold_base)

            if (is_gap or is_decay) and self.allow_single_impulse_exception and len(self.candidate_windows) == 1:
                cand = self.candidate_windows[0]
                cand_score = float(cand.get("score", 0.0))
                cand_crest = cand.get("crest_factor_db") or crest_factor_db
                cand_suppressed = bool(cand.get("suppression_active", False))

                qualifies_impulse = (
                    cand_score >= self.single_impulse_min_score
                    and (cand_crest is not None and cand_crest >= self.single_impulse_min_crest_db)
                    and (audio_duration_sec is None or audio_duration_sec <= self.single_impulse_max_dur_sec)
                    and not cand_suppressed
                )

                if qualifies_impulse:
                    # Promote candidate under single-round impulse exception
                    self.confirmed_windows = [cand]
                    self.candidate_windows = []
                    self._record_transition(
                        EventState.CANDIDATE,
                        EventState.CONFIRMED,
                        TransitionReason.IMMEDIATE_HIGH_CONFIDENCE,
                        timestamp_s=float(cand["start_time"]),
                        score=cand_score,
                        raw_score=float(cand.get("raw_score", cand_score)),
                        window_start_s=float(cand["start_time"]),
                        window_end_s=float(cand["end_time"])
                    )
                    self.state = EventState.CONFIRMED

                    # Terminate event and enter cooldown
                    emitted = self._create_event_record(self.confirmed_windows, "single_round_impulse")
                    self.events_emitted.append(emitted)
                    self.cooldown_until = emitted["end_time"] + self.cooldown_secs

                    self._record_transition(
                        EventState.CONFIRMED,
                        EventState.COOLDOWN,
                        TransitionReason.EVENT_DECAYED_BELOW_OFF,
                        timestamp_s=st,
                        score=score,
                        raw_score=raw_score,
                        window_start_s=st,
                        window_end_s=et
                    )
                    self.confirmed_windows = []
                    self.state = EventState.COOLDOWN
                    self.last_window_time = st
                    return emitted

        return super().process_window(
            window=window,
            crest_factor_db=crest_factor_db,
            audio_duration_sec=audio_duration_sec,
            total_windows_in_stream=total_windows_in_stream
        )

    def flush(self) -> Optional[Dict[str, Any]]:
        """Flush unconfirmed candidates or active events at stream EOF."""
        if self.state == EventState.CANDIDATE and self.allow_single_impulse_exception and len(self.candidate_windows) == 1:
            cand = self.candidate_windows[0]
            cand_score = float(cand.get("score", 0.0))
            cand_crest = cand.get("crest_factor_db")
            cand_suppressed = bool(cand.get("suppression_active", False))

            if (
                cand_score >= self.single_impulse_min_score
                and (cand_crest is not None and cand_crest >= self.single_impulse_min_crest_db)
                and not cand_suppressed
            ):
                self.confirmed_windows = [cand]
                self.candidate_windows = []
                self.state = EventState.CONFIRMED
                emitted = self._create_event_record(self.confirmed_windows, "single_round_impulse")
                self.events_emitted.append(emitted)
                self.cooldown_until = emitted["end_time"] + self.cooldown_secs
                self.confirmed_windows = []
                self.state = EventState.COOLDOWN
                return emitted

        return super().flush()


class DetectorImprovementV2:
    """
    Detector Improvement V2:
    Integrates Calibrated Multi-Category Semantic Suppression V2 with
    the Deterministic Refractory Event State Machine V2.
    """

    CONFIG_PATH = Path(__file__).resolve().parent / "config_improvement_v2.json"

    def __init__(
        self,
        bundle_dir: Path = config.MODELS_DIR / "gunshot_yamnet_bundle",
        profile: str = "balanced"
    ):
        self.bundle_dir = Path(bundle_dir)
        with open(self.CONFIG_PATH, "r", encoding="utf-8") as f:
            self.full_config = json.load(f)

        self.branch_id = self.full_config.get("branch_identifier", "DETECTOR_IMPROVEMENT_V2")
        self.profiles = self.full_config.get("profiles", {})
        self.profile = profile if profile in self.profiles else "balanced"
        self.cfg = self.profiles[self.profile]

        self.threshold_base = float(self.cfg["threshold_base"])
        self.threshold_high = float(self.cfg["threshold_high"])
        self.threshold_off = float(self.cfg["threshold_off"])
        self.confirm_windows = int(self.cfg["confirm_windows"])
        self.cooldown_secs = float(self.cfg["cooldown_secs"])
        self.max_hop_gap_s = float(self.cfg["max_hop_gap_s"])
        self.min_crest_factor_db = float(self.cfg["min_crest_factor_db"])
        self.single_win_min_crest_db = float(self.cfg["single_win_min_crest_db"])
        self.allow_short_clip_exception = bool(self.cfg["allow_short_clip_exception"])
        self.allow_single_impulse_exception = bool(self.cfg.get("allow_single_impulse_exception", True))
        self.single_impulse_min_score = float(self.cfg.get("single_impulse_min_score", 0.82))
        self.single_impulse_min_crest_db = float(self.cfg.get("single_impulse_min_crest_db", 14.0))
        self.single_impulse_max_dur_sec = float(self.cfg.get("single_impulse_max_dur_sec", 5.0))

        # Semantic suppression engine V2
        self.suppression_engine = CalibratedAcousticSuppressionV2(self.cfg.get("suppression", {}))

        # Load models
        self.model, self.bundle_info = load_model_bundle(self.bundle_dir)
        self.feature_extractor = YAMNetFeatureExtractor()
        self.yamnet_model = self.feature_extractor.model

    def compute_ensemble_score(self, embeddings: np.ndarray) -> np.ndarray:
        """Computes calibrated ensemble probability for given embeddings."""
        if embeddings is None or len(embeddings) == 0:
            return np.array([], dtype=np.float32)
        preds = self.model.predict(embeddings)
        return np.asarray(preds, dtype=np.float32).flatten()

    def evaluate_waveform(
        self,
        waveform: np.ndarray,
        sample_rate: int = config.SAMPLE_RATE,
        allow_short_clip_exception: Optional[bool] = None
    ) -> Dict[str, Any]:
        """
        Evaluates a complete waveform using Calibrated Semantic Suppression V2
        and the Deterministic 4-State Refractory State Machine V2.
        """
        t0 = time.perf_counter()
        if waveform.ndim > 1:
            waveform = np.mean(waveform, axis=1)

        dur_sec = len(waveform) / float(sample_rate)
        crest_db = compute_physical_crest_factor_db(waveform)

        if len(waveform) < config.WINDOW_SAMPLES:
            padded_wave = np.pad(waveform, (0, config.WINDOW_SAMPLES - len(waveform)))
        else:
            padded_wave = waveform

        import tensorflow as tf
        wave_tensor = tf.convert_to_tensor(padded_wave, dtype=tf.float32)
        yamnet_scores_tf, embeddings_tf, _ = self.yamnet_model(wave_tensor)
        yamnet_scores = yamnet_scores_tf.numpy()
        embeddings = embeddings_tf.numpy()

        n_windows = len(embeddings)
        if n_windows == 0:
            return {
                "duration_seconds": round(dur_sec, 3),
                "crest_factor_db": round(crest_db, 1),
                "total_windows": 0,
                "overall_score": 0.0,
                "detected": False,
                "is_gunshot": False,
                "events_count": 0,
                "events": [],
                "windows": [],
                "transition_log": [],
                "profile_used": self.profile,
                "latency_ms": round((time.perf_counter() - t0) * 1000.0, 1)
            }

        raw_scores = self.compute_ensemble_score(embeddings)
        allow_short = self.allow_short_clip_exception if allow_short_clip_exception is None else allow_short_clip_exception

        fsm = EventStateMachineV2(
            threshold_base=self.threshold_base,
            threshold_high=self.threshold_high,
            threshold_off=self.threshold_off,
            confirm_windows=self.confirm_windows,
            cooldown_secs=self.cooldown_secs,
            max_hop_gap_s=self.max_hop_gap_s,
            min_crest_factor_db=self.min_crest_factor_db,
            single_win_min_crest_db=self.single_win_min_crest_db,
            allow_short_clip_exception=allow_short,
            allow_single_impulse_exception=self.allow_single_impulse_exception,
            single_impulse_min_score=self.single_impulse_min_score,
            single_impulse_min_crest_db=self.single_impulse_min_crest_db,
            single_impulse_max_dur_sec=self.single_impulse_max_dur_sec
        )

        window_results = []
        hop_sec = config.HOP_SAMPLES / float(sample_rate)
        win_sec = config.WINDOW_SAMPLES / float(sample_rate)

        for i in range(n_windows):
            st = round(i * hop_sec, 3)
            et = min(round(dur_sec, 3), round(st + win_sec, 3))
            raw_sc = float(raw_scores[i])
            ym_sc = yamnet_scores[i] if (yamnet_scores is not None and i < len(yamnet_scores)) else None

            is_in_conf = (fsm.state == EventState.CONFIRMED)
            supp_res = self.suppression_engine.apply_suppression(
                raw_score=raw_sc,
                yamnet_scores=ym_sc,
                is_in_confirmed_event=is_in_conf
            )

            win_record = {
                "window_index": i,
                "start_time": st,
                "end_time": et,
                "raw_score": raw_sc,
                "raw_ensemble_score": round(raw_sc, 4),
                "score": supp_res["adjusted_score"],
                "crest_factor_db": crest_db,
                "suppression_active": supp_res["suppression_active"],
                "suppression_category": supp_res["suppression_category"],
                "suppression_strength": supp_res["suppression_strength"],
                "suppression_reason": supp_res["suppression_reason"],
                "triggered": supp_res["adjusted_score"] >= self.threshold_base
            }
            window_results.append(win_record)

            fsm.process_window(
                win_record,
                crest_factor_db=crest_db,
                audio_duration_sec=dur_sec,
                total_windows_in_stream=n_windows
            )

        fsm.flush()
        events = fsm.events_emitted
        scores = [w["score"] for w in window_results]
        max_score = float(np.max(scores)) if scores else 0.0

        return {
            "duration_seconds": round(dur_sec, 3),
            "crest_factor_db": round(crest_db, 1),
            "total_windows": n_windows,
            "overall_score": max_score,
            "detected": len(events) > 0,
            "is_gunshot": len(events) > 0,
            "events_count": len(events),
            "events": events,
            "windows": window_results,
            "transition_log": fsm.transition_log,
            "profile_used": self.profile,
            "latency_ms": round((time.perf_counter() - t0) * 1000.0, 1)
        }


class RealTimeStreamDetectorImprovementV2:
    """
    Real-Time Streaming Gunshot Detector for Detector Improvement V2.
    Maintains a streaming ring buffer, applies Calibrated Semantic Suppression V2,
    and drives the Deterministic Refractory State Machine V2. Thread-safe.
    """

    def __init__(
        self,
        profile: str = "balanced",
        chunk_duration_sec: float = 0.48,
        sample_rate: int = config.SAMPLE_RATE
    ):
        self.detector = DetectorImprovementV2(profile=profile)
        self.chunk_size = int(chunk_duration_sec * sample_rate)
        self.window_size = config.WINDOW_SAMPLES
        self.hop_size = config.HOP_SAMPLES
        self.sample_rate = sample_rate
        self.lock = threading.Lock()

        self.buffer = np.zeros(0, dtype=np.float32)
        self.stream_offset_samples = 0
        self.stream_time_sec = 0.0

        self.fsm = EventStateMachineV2(
            threshold_base=self.detector.threshold_base,
            threshold_high=self.detector.threshold_high,
            threshold_off=self.detector.threshold_off,
            confirm_windows=self.detector.confirm_windows,
            cooldown_secs=self.detector.cooldown_secs,
            max_hop_gap_s=self.detector.max_hop_gap_s,
            min_crest_factor_db=self.detector.min_crest_factor_db,
            single_win_min_crest_db=self.detector.single_win_min_crest_db,
            allow_short_clip_exception=self.detector.allow_short_clip_exception,
            allow_single_impulse_exception=self.detector.allow_single_impulse_exception,
            single_impulse_min_score=self.detector.single_impulse_min_score,
            single_impulse_min_crest_db=self.detector.single_impulse_min_crest_db,
            single_impulse_max_dur_sec=self.detector.single_impulse_max_dur_sec
        )

        self.last_score = 0.0
        self.last_crest_factor_db = 0.0
        self.detected_alerts: List[Dict[str, Any]] = []
        self.chunk_latencies_ms: List[float] = []

    @property
    def in_event(self) -> bool:
        return self.fsm.state == EventState.CONFIRMED

    @property
    def cooldown_until(self) -> float:
        return self.fsm.cooldown_until

    def reset(self) -> None:
        """Thread-safe reset for stream boundaries."""
        with self.lock:
            self.buffer = np.zeros(0, dtype=np.float32)
            self.stream_offset_samples = 0
            self.stream_time_sec = 0.0
            self.fsm.reset()
            self.last_score = 0.0
            self.last_crest_factor_db = 0.0
            self.detected_alerts = []
            self.chunk_latencies_ms = []

    def process_chunk(
        self,
        chunk: np.ndarray,
        input_sample_rate: int = config.SAMPLE_RATE
    ) -> List[Dict[str, Any]]:
        """
        Consumes an incoming audio chunk, manages the ring buffer, evaluates windows,
        and returns any events confirmed in this slice.
        """
        t0 = time.perf_counter()
        if chunk is None or len(chunk) == 0:
            return []

        chunk = chunk.astype(np.float32)
        if chunk.ndim > 1:
            chunk = np.mean(chunk, axis=1)

        new_alerts = []

        with self.lock:
            self.buffer = np.concatenate([self.buffer, chunk])

            while len(self.buffer) >= self.window_size:
                window_audio = self.buffer[:self.window_size]
                st = round(self.stream_offset_samples / float(self.sample_rate), 3)
                et = round((self.stream_offset_samples + self.window_size) / float(self.sample_rate), 3)

                crest_db = compute_physical_crest_factor_db(window_audio)
                self.last_crest_factor_db = crest_db

                # Extract features
                import tensorflow as tf
                wave_tensor = tf.convert_to_tensor(window_audio, dtype=tf.float32)
                ym_scores_tf, emb_tf, _ = self.detector.yamnet_model(wave_tensor)
                ym_scores = ym_scores_tf.numpy()
                emb = emb_tf.numpy()

                if len(emb) > 0:
                    raw_sc = float(self.detector.compute_ensemble_score(emb)[0])
                    ym = ym_scores[0] if (ym_scores is not None and len(ym_scores) > 0) else None

                    is_in_conf = (self.fsm.state == EventState.CONFIRMED)
                    supp_res = self.detector.suppression_engine.apply_suppression(
                        raw_score=raw_sc,
                        yamnet_scores=ym,
                        is_in_confirmed_event=is_in_conf
                    )

                    score = supp_res["adjusted_score"]
                    self.last_score = score

                    win_record = {
                        "window_index": int(self.stream_offset_samples // self.hop_size),
                        "start_time": st,
                        "end_time": et,
                        "raw_score": raw_sc,
                        "raw_ensemble_score": round(raw_sc, 4),
                        "score": score,
                        "crest_factor_db": crest_db,
                        "suppression_active": supp_res["suppression_active"],
                        "suppression_category": supp_res["suppression_category"],
                        "suppression_strength": supp_res["suppression_strength"],
                        "suppression_reason": supp_res["suppression_reason"],
                        "triggered": score >= self.detector.threshold_base
                    }

                    ev = self.fsm.process_window(win_record, crest_factor_db=crest_db)
                    if ev is not None:
                        new_alerts.append(ev)
                        self.detected_alerts.append(ev)

                # Advance buffer by hop
                self.buffer = self.buffer[self.hop_size:]
                self.stream_offset_samples += self.hop_size
                self.stream_time_sec = self.stream_offset_samples / float(self.sample_rate)

            lat_ms = (time.perf_counter() - t0) * 1000.0
            self.chunk_latencies_ms.append(lat_ms)
            if len(self.chunk_latencies_ms) > 100:
                self.chunk_latencies_ms = self.chunk_latencies_ms[-100:]

        return new_alerts

