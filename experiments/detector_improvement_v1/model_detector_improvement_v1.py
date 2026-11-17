"""
Detector Improvement V1 - Production Experimental Gunshot Detector
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


class CalibratedAcousticSuppressionV1:
    """
    Calibrated multi-category acoustic suppression engine with ballistic impulse protection.
    Suppresses non-target impulsivity from pyrotechnics, thunder, canine vocalizations,
    fire crackle, and emergency transit sirens while protecting authentic gunshot transients.
    """

    def __init__(self, suppression_cfg: Dict[str, Any]):
        self.enabled = suppression_cfg.get("enabled", True)
        self.thun_cfg = suppression_cfg.get("thunder", {"threshold": 0.25, "ratio": 1.5, "attenuation": 0.30})
        self.fw_cfg = suppression_cfg.get("fireworks", {"threshold": 0.30, "ratio": 1.5, "gun_max": 0.10, "attenuation": 0.35})
        self.dog_cfg = suppression_cfg.get("canine", {"threshold": 0.30, "ratio": 1.5, "attenuation": 0.35})
        self.crackle_cfg = suppression_cfg.get("fire_crackle", {"threshold": 0.25, "ratio": 1.5, "attenuation": 0.35})
        self.siren_cfg = suppression_cfg.get("siren", {"threshold": 0.35, "ratio": 1.5, "attenuation": 0.30})

    def apply_suppression(
        self,
        raw_score: float,
        yamnet_scores: Optional[np.ndarray],
        is_in_confirmed_event: bool = False
    ) -> Dict[str, Any]:
        """
        Calculates calibrated score after evaluating multi-category semantic probabilities.
        """
        if not self.enabled or yamnet_scores is None or is_in_confirmed_event:
            return {
                "adjusted_score": float(raw_score),
                "suppression_active": False,
                "suppression_category": None,
                "suppression_strength": 1.0,
                "suppression_reason": None
            }

        gun_score = max(
            float(yamnet_scores[YAMNET_CLASS_GUNSHOT]),
            float(yamnet_scores[YAMNET_CLASS_MACHINE_GUN]),
            float(yamnet_scores[YAMNET_CLASS_ARTILLERY]),
            float(yamnet_scores[YAMNET_CLASS_CAP_GUN])
        )
        thunder_score = max(
            float(yamnet_scores[YAMNET_CLASS_THUNDERSTORM]),
            float(yamnet_scores[YAMNET_CLASS_THUNDER])
        )
        fireworks_score = max(
            float(yamnet_scores[YAMNET_CLASS_FIREWORKS]),
            float(yamnet_scores[YAMNET_CLASS_FIRECRACKER])
        )
        dog_score = max(
            float(yamnet_scores[YAMNET_CLASS_DOG]),
            float(yamnet_scores[YAMNET_CLASS_BARK]),
            float(yamnet_scores[YAMNET_CLASS_YIP]),
            float(yamnet_scores[YAMNET_CLASS_CANIDAE])
        )
        crackle_score = max(
            float(yamnet_scores[YAMNET_CLASS_FIRE]),
            float(yamnet_scores[YAMNET_CLASS_CRACKLE])
        )
        siren_score = max(
            float(yamnet_scores[YAMNET_CLASS_POLICE_CAR]),
            float(yamnet_scores[YAMNET_CLASS_AMBULANCE]),
            float(yamnet_scores[YAMNET_CLASS_FIRE_ENGINE]),
            float(yamnet_scores[YAMNET_CLASS_SIREN]),
            float(yamnet_scores[YAMNET_CLASS_CIVIL_DEFENSE])
        )

        adj_score = float(raw_score)
        supp_cat = None
        strength = 1.0

        # Thunder suppression
        if thunder_score > self.thun_cfg["threshold"] and thunder_score >= gun_score * self.thun_cfg["ratio"]:
            strength = self.thun_cfg["attenuation"]
            adj_score *= strength
            supp_cat = "thunder"

        # Fireworks suppression with ballistic safeguard
        elif (
            fireworks_score > self.fw_cfg["threshold"]
            and fireworks_score >= gun_score * self.fw_cfg["ratio"]
            and gun_score < self.fw_cfg["gun_max"]
        ):
            strength = self.fw_cfg["attenuation"]
            adj_score *= strength
            supp_cat = "fireworks"

        # Canine vocalization suppression
        elif dog_score > self.dog_cfg["threshold"] and dog_score >= gun_score * self.dog_cfg["ratio"]:
            strength = self.dog_cfg["attenuation"]
            adj_score *= strength
            supp_cat = "canine_bark"

        # Fire crackle suppression
        elif crackle_score > self.crackle_cfg["threshold"] and crackle_score >= gun_score * self.crackle_cfg["ratio"]:
            strength = self.crackle_cfg["attenuation"]
            adj_score *= strength
            supp_cat = "fire_crackle"

        # Siren / Transit acoustic suppression
        elif siren_score > self.siren_cfg["threshold"] and siren_score >= gun_score * self.siren_cfg["ratio"]:
            strength = self.siren_cfg["attenuation"]
            adj_score *= strength
            supp_cat = "siren"

        return {
            "adjusted_score": float(round(adj_score, 4)),
            "suppression_active": supp_cat is not None,
            "suppression_category": supp_cat,
            "suppression_strength": float(strength),
            "suppression_reason": supp_cat
        }


class DetectorImprovementV1:
    """
    Detector Improvement V1:
    Integrates Calibrated Multi-Category Semantic Suppression V1 with
    a Deterministic 4-State Refractory Event State Machine.
    """

    CONFIG_PATH = Path(__file__).resolve().parent / "config_improvement_v1.json"

    def __init__(
        self,
        bundle_dir: Path = config.MODELS_DIR / "gunshot_yamnet_bundle",
        profile: str = "balanced"
    ):
        self.bundle_dir = Path(bundle_dir)
        with open(self.CONFIG_PATH, "r", encoding="utf-8") as f:
            self.full_config = json.load(f)

        self.branch_id = self.full_config.get("branch_identifier", "DETECTOR_IMPROVEMENT_V1")
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

        # Semantic suppression engine
        self.suppression_engine = CalibratedAcousticSuppressionV1(self.cfg.get("suppression", {}))

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
        Evaluates a complete waveform using Calibrated Semantic Suppression V1
        and the Deterministic 4-State Refractory State Machine.
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

        fsm = EventStateMachine(
            threshold_base=self.threshold_base,
            threshold_high=self.threshold_high,
            threshold_off=self.threshold_off,
            confirm_windows=self.confirm_windows,
            cooldown_secs=self.cooldown_secs,
            max_hop_gap_s=self.max_hop_gap_s,
            min_crest_factor_db=self.min_crest_factor_db,
            single_win_min_crest_db=self.single_win_min_crest_db,
            allow_short_clip_exception=allow_short
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


class RealTimeStreamDetectorImprovementV1:
    """
    Real-Time Streaming Gunshot Detector for Detector Improvement V1.
    Maintains a streaming ring buffer, applies Calibrated Semantic Suppression V1,
    and drives the Deterministic 4-State Refractory State Machine. Thread-safe.
    """

    def __init__(
        self,
        profile: str = "balanced",
        chunk_duration_sec: float = 0.48,
        sample_rate: int = config.SAMPLE_RATE
    ):
        self.detector = DetectorImprovementV1(profile=profile)
        self.chunk_size = int(chunk_duration_sec * sample_rate)
        self.window_size = config.WINDOW_SAMPLES
        self.hop_size = config.HOP_SAMPLES
        self.sample_rate = sample_rate
        self.lock = threading.Lock()

        self.buffer = np.zeros(0, dtype=np.float32)
        self.stream_offset_samples = 0
        self.stream_time_sec = 0.0

        self.fsm = EventStateMachine(
            threshold_base=self.detector.threshold_base,
            threshold_high=self.detector.threshold_high,
            threshold_off=self.detector.threshold_off,
            confirm_windows=self.detector.confirm_windows,
            cooldown_secs=self.detector.cooldown_secs,
            max_hop_gap_s=self.detector.max_hop_gap_s,
            min_crest_factor_db=self.detector.min_crest_factor_db,
            single_win_min_crest_db=self.detector.single_win_min_crest_db,
            allow_short_clip_exception=self.detector.allow_short_clip_exception
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
