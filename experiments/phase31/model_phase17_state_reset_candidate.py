# =============================================================================
# PHASE 31 EXPERIMENTAL CANDIDATE: STATE-MACHINE RESET PATCH
# MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY
# EXPERIMENTAL ARTIFACT ONLY — DO NOT OVERWRITE FROZEN model_phase17.py OR model_phase14.py
# Restores the missing 'else: active_cluster = []' reset branch and guards EOF flushing.
# =============================================================================
"""
Phase 17 Experimental Adaptive Gunshot Detector.

Implements the Phase 17 Experimental Animal Semantic Suppression Architecture:
1. Full preservation of Phase 14 calibrated semantic gating (Thunder, Fireworks, Dogs, Crackle, Siren)
   and crest-factor temporal state machine.
2. Selectable Experimental Relative Animal Suppression Gate:
   - Evaluates YAMNet animal/avian semantic classes (Animal, Pets, Cat, Caterwaul, Farm Animals,
     Fowl, Chicken/Rooster, Crowing, Wild Animals, Bird, Bird Song, Crow).
   - Candidate Rule: Suppress if animal_score > 0.35 AND animal_score >= 2.0 * gun_score.
   - Controlled attenuation: calibrated_score *= 0.30, suppression_reason = "animal_vocalization".
   - Disabled by default (enable_animal_suppression=False) to strictly preserve Phase 14 defaults.
   - Selectable via explicit profile (e.g., 'balanced_animal_suppressed', 'experimental_animal_suppression')
     or constructor argument (enable_animal_suppression=True).
3. Thread-safe streaming ring-buffer detector (RealTimeStreamDetectorPhase17).
4. Full backwards compatibility with Phase 14, Phase 13, and Phase 9 model bundles.

MANDATORY SAFETY DESIGNATION:
RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.
Not certified for life-safety, fire alarm, automated 911 dispatch, or critical security deployment.
"""

import os
import sys
import math
import time
import threading
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any

import numpy as np

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import config
from model import load_model_bundle, CalibratedEnsemble
from feature_extractor import YAMNetFeatureExtractor

SAFETY_DESIGNATION = "RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY"

# YAMNet Semantic Class Mappings (AudioSet Indices)
YAMNET_CLASS_GUNSHOT = 421          # Gunshot, gunfire
YAMNET_CLASS_MACHINE_GUN = 422      # Machine gun
YAMNET_CLASS_ARTILLERY = 424        # Artillery fire
YAMNET_CLASS_CAP_GUN = 425          # Cap gun
YAMNET_CLASS_THUNDERSTORM = 280     # Thunderstorm
YAMNET_CLASS_THUNDER = 281          # Thunder
YAMNET_CLASS_FIREWORKS = 426        # Fireworks
YAMNET_CLASS_FIRECRACKER = 427      # Firecracker
YAMNET_CLASS_DOG = 69               # Dog
YAMNET_CLASS_BARK = 70              # Bark
YAMNET_CLASS_YIP = 75               # Yip
YAMNET_CLASS_CANIDAE = 117          # Canidae
YAMNET_CLASS_FIRE = 292             # Fire
YAMNET_CLASS_CRACKLE = 293          # Crackle
YAMNET_CLASS_POLICE_CAR = 317       # Police car (siren)
YAMNET_CLASS_AMBULANCE = 318        # Ambulance (siren)
YAMNET_CLASS_FIRE_ENGINE = 319      # Fire engine (siren)
YAMNET_CLASS_SIREN = 390            # Siren
YAMNET_CLASS_CIVIL_DEFENSE = 391    # Civil defense siren

# Phase 17 Experimental Animal Semantic Classes
YAMNET_ANIMAL_CLASSES = [
    67,   # Animal
    68,   # Domestic animals, pets
    76,   # Cat
    80,   # Caterwaul
    81,   # Livestock, farm animals, working animals
    85,   # Cattle, bovinae
    93,   # Fowl
    94,   # Chicken, rooster
    96,   # Crowing, cock-a-doodle-doo
    103,  # Wild animals
    104,  # Roaring cats (lions, tigers)
    106,  # Bird
    107,  # Bird vocalization, bird call, bird song
    112,  # Crow
    116   # Bird flight, flapping wings
]

def compute_physical_crest_factor_db(waveform_chunk: np.ndarray) -> float:
    """Compute acoustic crest factor (dB) = 20 * log10(Peak / RMS)."""
    if len(waveform_chunk) == 0:
        return 0.0
    peak = float(np.max(np.abs(waveform_chunk)))
    rms = float(np.sqrt(np.mean(waveform_chunk ** 2)))
    if rms < 1e-9:
        return 0.0
    return float(20.0 * np.log10(max(peak, 1e-6) / max(rms, 1e-6)))

def merge_phase17_events(
    window_results: List[Dict[str, Any]],
    threshold_base: float,
    threshold_high: float,
    threshold_off: float,
    confirm_windows: int,
    cooldown_secs: float,
    audio_duration_sec: Optional[float] = None,
    allow_short_clip_exception: bool = True,
    crest_factor_db: Optional[float] = None,
    min_crest_factor_db: float = 8.8,
    single_win_min_crest_db: float = 12.0
) -> List[Dict[str, Any]]:
    """
    Phase 17 State-Machine Event Merger.
    Merges overlapping/consecutive detection windows with crest-guarded dispatch
    and refractory cooldown clustering.
    """
    if not window_results:
        return []

    sorted_windows = sorted(window_results, key=lambda x: x["start_time"])
    events = []
    cooldown_until = -1.0
    active_cluster: List[Dict[str, Any]] = []
    in_event = False
    had_decayed = True

    # Guarded short clip check (for discrete single-window files)
    is_short_isolated_clip = False
    if allow_short_clip_exception and (audio_duration_sec is not None and audio_duration_sec <= 1.05) and len(sorted_windows) == 1:
        if crest_factor_db is None or crest_factor_db >= min_crest_factor_db:
            is_short_isolated_clip = True

    for win in sorted_windows:
        st = win["start_time"]
        et = win["end_time"]
        score = win["score"]

        has_sharp_crest = (crest_factor_db is None or crest_factor_db >= single_win_min_crest_db)
        qualifies_immediate = (score >= threshold_high and has_sharp_crest) or (is_short_isolated_clip and score >= threshold_base)

        if not in_event:
            if score < threshold_off:
                had_decayed = True

            if st < cooldown_until:
                if had_decayed and (qualifies_immediate or score >= threshold_base):
                    active_cluster.append(win)
                    if qualifies_immediate or len(active_cluster) >= confirm_windows:
                        in_event = True
                        had_decayed = False
                else:
                    continue
            else:
                if qualifies_immediate:
                    active_cluster = [win]
                    in_event = True
                    had_decayed = False
                elif score >= threshold_base:
                    active_cluster.append(win)
                    if len(active_cluster) >= confirm_windows:
                        in_event = True
                        had_decayed = False
                else:
                    active_cluster = []
        else:
            if score >= threshold_off:
                active_cluster.append(win)
            else:
                # Event ended
                ev_start = min(w["start_time"] for w in active_cluster)
                ev_end = max(w["end_time"] for w in active_cluster)
                max_sc = max(w["score"] for w in active_cluster)
                raw_max = max(w.get("raw_ensemble_score", w["score"]) for w in active_cluster)
                cooldown_until = ev_end + cooldown_secs

                events.append({
                    "start_time": ev_start,
                    "end_time": ev_end,
                    "duration": round(ev_end - ev_start, 3),
                    "score": round(max_sc, 4),
                    "raw_ensemble_score": round(raw_max, 4),
                    "windows_count": len(active_cluster),
                    "qualifies_immediate": any(w["score"] >= threshold_high for w in active_cluster),
                    "crest_factor_db": round(crest_factor_db, 2) if crest_factor_db is not None else None
                })
                active_cluster = []
                in_event = False
                had_decayed = True

    if in_event and active_cluster:
        ev_start = min(w["start_time"] for w in active_cluster)
        ev_end = max(w["end_time"] for w in active_cluster)
        max_sc = max(w["score"] for w in active_cluster)
        raw_max = max(w.get("raw_ensemble_score", w["score"]) for w in active_cluster)
        events.append({
            "start_time": ev_start,
            "end_time": ev_end,
            "duration": round(ev_end - ev_start, 3),
            "score": round(max_sc, 4),
            "raw_ensemble_score": round(raw_max, 4),
            "windows_count": len(active_cluster),
            "qualifies_immediate": any(w["score"] >= threshold_high for w in active_cluster),
            "crest_factor_db": round(crest_factor_db, 2) if crest_factor_db is not None else None
        })

    return events


class Phase17ExperimentalGunshotDetector:
    """
    Phase 17 Experimental Adaptive Gunshot Detector.
    Supports selectable animal suppression while retaining full Phase 14 baseline equivalence.
    """
    PROFILES = {
        "balanced": {
            "threshold_base": 0.75,
            "threshold_high": 0.88,
            "threshold_off": 0.48,
            "confirm_windows": 2,
            "cooldown_secs": 2.0,
            "enable_semantic_gating": True,
            "enable_animal_suppression": False,
            "min_crest_factor_db": 8.8,
            "single_win_min_crest_db": 12.0,
            "fw_thresh": 0.35,
            "fw_ratio": 2.0,
            "fw_gun_max": 0.05,
            "thun_thresh": 0.25,
            "thun_ratio": 1.5,
            "animal_thresh": 0.35,
            "animal_ratio": 2.0
        },
        "balanced_animal_suppressed": {
            "threshold_base": 0.75,
            "threshold_high": 0.88,
            "threshold_off": 0.48,
            "confirm_windows": 2,
            "cooldown_secs": 2.0,
            "enable_semantic_gating": True,
            "enable_animal_suppression": True,
            "min_crest_factor_db": 8.8,
            "single_win_min_crest_db": 12.0,
            "fw_thresh": 0.35,
            "fw_ratio": 2.0,
            "fw_gun_max": 0.05,
            "thun_thresh": 0.25,
            "thun_ratio": 1.5,
            "animal_thresh": 0.35,
            "animal_ratio": 2.0
        },
        "high_precision": {
            "threshold_base": 0.80,
            "threshold_high": 0.90,
            "threshold_off": 0.52,
            "confirm_windows": 2,
            "cooldown_secs": 2.5,
            "enable_semantic_gating": True,
            "enable_animal_suppression": False,
            "min_crest_factor_db": 8.8,
            "single_win_min_crest_db": 12.0,
            "fw_thresh": 0.35,
            "fw_ratio": 2.0,
            "fw_gun_max": 0.05,
            "thun_thresh": 0.25,
            "thun_ratio": 1.5,
            "animal_thresh": 0.35,
            "animal_ratio": 2.0
        },
        "high_precision_animal_suppressed": {
            "threshold_base": 0.80,
            "threshold_high": 0.90,
            "threshold_off": 0.52,
            "confirm_windows": 2,
            "cooldown_secs": 2.5,
            "enable_semantic_gating": True,
            "enable_animal_suppression": True,
            "min_crest_factor_db": 8.8,
            "single_win_min_crest_db": 12.0,
            "fw_thresh": 0.35,
            "fw_ratio": 2.0,
            "fw_gun_max": 0.05,
            "thun_thresh": 0.25,
            "thun_ratio": 1.5,
            "animal_thresh": 0.35,
            "animal_ratio": 2.0
        },
        "high_sensitivity": {
            "threshold_base": 0.70,
            "threshold_high": 0.85,
            "threshold_off": 0.42,
            "confirm_windows": 2,
            "cooldown_secs": 1.5,
            "enable_semantic_gating": True,
            "enable_animal_suppression": False,
            "min_crest_factor_db": 8.5,
            "single_win_min_crest_db": 11.0,
            "fw_thresh": 0.40,
            "fw_ratio": 2.5,
            "fw_gun_max": 0.06,
            "thun_thresh": 0.25,
            "thun_ratio": 1.5,
            "animal_thresh": 0.35,
            "animal_ratio": 2.0
        },
        "high_sensitivity_animal_suppressed": {
            "threshold_base": 0.70,
            "threshold_high": 0.85,
            "threshold_off": 0.42,
            "confirm_windows": 2,
            "cooldown_secs": 1.5,
            "enable_semantic_gating": True,
            "enable_animal_suppression": True,
            "min_crest_factor_db": 8.5,
            "single_win_min_crest_db": 11.0,
            "fw_thresh": 0.40,
            "fw_ratio": 2.5,
            "fw_gun_max": 0.06,
            "thun_thresh": 0.25,
            "thun_ratio": 1.5,
            "animal_thresh": 0.35,
            "animal_ratio": 2.0
        },
        "experimental_animal_suppression": {
            "threshold_base": 0.75,
            "threshold_high": 0.88,
            "threshold_off": 0.48,
            "confirm_windows": 2,
            "cooldown_secs": 2.0,
            "enable_semantic_gating": True,
            "enable_animal_suppression": True,
            "min_crest_factor_db": 8.8,
            "single_win_min_crest_db": 12.0,
            "fw_thresh": 0.35,
            "fw_ratio": 2.0,
            "fw_gun_max": 0.05,
            "thun_thresh": 0.25,
            "thun_ratio": 1.5,
            "animal_thresh": 0.35,
            "animal_ratio": 2.0
        }
    }

    def __init__(
        self,
        bundle_dir: Path = config.MODELS_DIR / "gunshot_yamnet_bundle",
        profile: str = "balanced",
        threshold_base: Optional[float] = None,
        threshold_high: Optional[float] = None,
        threshold_off: Optional[float] = None,
        confirm_windows: Optional[int] = None,
        cooldown_secs: Optional[float] = None,
        enable_semantic_gating: Optional[bool] = None,
        enable_animal_suppression: Optional[bool] = None,
        min_crest_factor_db: Optional[float] = None,
        single_win_min_crest_db: Optional[float] = None,
        fw_thresh: Optional[float] = None,
        fw_ratio: Optional[float] = None,
        fw_gun_max: Optional[float] = None,
        animal_thresh: Optional[float] = None,
        animal_ratio: Optional[float] = None
    ):
        self.bundle_dir = Path(bundle_dir)
        prof_cfg = self.PROFILES.get(profile, self.PROFILES["balanced"]).copy()
        
        self.profile = profile
        self.threshold_base = threshold_base if threshold_base is not None else prof_cfg["threshold_base"]
        self.threshold_high = threshold_high if threshold_high is not None else prof_cfg["threshold_high"]
        self.threshold_off = threshold_off if threshold_off is not None else prof_cfg["threshold_off"]
        self.confirm_windows = confirm_windows if confirm_windows is not None else prof_cfg["confirm_windows"]
        self.cooldown_secs = cooldown_secs if cooldown_secs is not None else prof_cfg["cooldown_secs"]
        self.enable_semantic_gating = enable_semantic_gating if enable_semantic_gating is not None else prof_cfg["enable_semantic_gating"]
        self.enable_animal_suppression = enable_animal_suppression if enable_animal_suppression is not None else prof_cfg["enable_animal_suppression"]
        self.min_crest_factor_db = min_crest_factor_db if min_crest_factor_db is not None else prof_cfg["min_crest_factor_db"]
        self.single_win_min_crest_db = single_win_min_crest_db if single_win_min_crest_db is not None else prof_cfg["single_win_min_crest_db"]
        self.fw_thresh = fw_thresh if fw_thresh is not None else prof_cfg["fw_thresh"]
        self.fw_ratio = fw_ratio if fw_ratio is not None else prof_cfg["fw_ratio"]
        self.fw_gun_max = fw_gun_max if fw_gun_max is not None else prof_cfg["fw_gun_max"]
        self.animal_thresh = animal_thresh if animal_thresh is not None else prof_cfg["animal_thresh"]
        self.animal_ratio = animal_ratio if animal_ratio is not None else prof_cfg["animal_ratio"]
        self.thun_thresh = prof_cfg["thun_thresh"]
        self.thun_ratio = prof_cfg["thun_ratio"]

        # Load frozen model bundle
        self.model, self.bundle_info = load_model_bundle(self.bundle_dir)
        self.feature_extractor = YAMNetFeatureExtractor()
        self.yamnet_model = self.feature_extractor.model

    def evaluate_waveform(
        self,
        waveform: np.ndarray,
        allow_short_clip_exception: bool = True
    ) -> Dict[str, Any]:
        """Evaluate full waveform with Phase 17 Calibrated & Experimental Semantic Gating."""
        if waveform.ndim > 1:
            waveform = np.mean(waveform, axis=1)
        dur_sec = len(waveform) / float(config.SAMPLE_RATE)
        crest_db = compute_physical_crest_factor_db(waveform)

        if len(waveform) < config.WINDOW_SAMPLES:
            pad_len = config.WINDOW_SAMPLES - len(waveform)
            eval_wave = np.pad(waveform, (0, pad_len), mode="constant")
        else:
            eval_wave = waveform

        yamnet_scores, embeddings, _ = self.yamnet_model(eval_wave)
        yamnet_scores = yamnet_scores.numpy()
        embeddings = embeddings.numpy()

        n_windows = len(embeddings)
        window_results = []

        for i in range(n_windows):
            st = round(i * (config.HOP_SAMPLES / float(config.SAMPLE_RATE)), 3)
            et = round(st + (config.WINDOW_SAMPLES / float(config.SAMPLE_RATE)), 3)

            emb = embeddings[i:i+1]
            raw_score = float(self.model.predict(emb, verbose=0).flatten()[0])
            calibrated_score = raw_score
            suppression_reason = None

            if self.enable_semantic_gating:
                gun_score = max(
                    yamnet_scores[i, YAMNET_CLASS_GUNSHOT],
                    yamnet_scores[i, YAMNET_CLASS_MACHINE_GUN],
                    yamnet_scores[i, YAMNET_CLASS_ARTILLERY],
                    yamnet_scores[i, YAMNET_CLASS_CAP_GUN]
                )
                thunder_score = max(
                    yamnet_scores[i, YAMNET_CLASS_THUNDERSTORM],
                    yamnet_scores[i, YAMNET_CLASS_THUNDER]
                )
                fireworks_score = max(
                    yamnet_scores[i, YAMNET_CLASS_FIREWORKS],
                    yamnet_scores[i, YAMNET_CLASS_FIRECRACKER]
                )
                dog_score = max(
                    yamnet_scores[i, YAMNET_CLASS_DOG],
                    yamnet_scores[i, YAMNET_CLASS_BARK],
                    yamnet_scores[i, YAMNET_CLASS_YIP],
                    yamnet_scores[i, YAMNET_CLASS_CANIDAE]
                )
                crackle_score = max(
                    yamnet_scores[i, YAMNET_CLASS_FIRE],
                    yamnet_scores[i, YAMNET_CLASS_CRACKLE]
                )
                siren_score = max(
                    yamnet_scores[i, YAMNET_CLASS_POLICE_CAR],
                    yamnet_scores[i, YAMNET_CLASS_AMBULANCE],
                    yamnet_scores[i, YAMNET_CLASS_FIRE_ENGINE],
                    yamnet_scores[i, YAMNET_CLASS_SIREN],
                    yamnet_scores[i, YAMNET_CLASS_CIVIL_DEFENSE]
                )

                # 1. Thunder Attenuation
                if thunder_score > self.thun_thresh and thunder_score >= gun_score * self.thun_ratio:
                    calibrated_score *= 0.30
                    suppression_reason = "thunder"

                # 2. Fireworks Attenuation with Ballistic Safeguard
                elif fireworks_score > self.fw_thresh and fireworks_score >= gun_score * self.fw_ratio and gun_score < self.fw_gun_max:
                    calibrated_score *= 0.35
                    suppression_reason = "fireworks"

                # 3. Dog / Animal Bark Attenuation
                elif dog_score > 0.30 and dog_score >= gun_score * 1.5:
                    calibrated_score *= 0.35
                    suppression_reason = "dog_bark"

                # 4. Crackling Fire Attenuation
                elif crackle_score > 0.25 and crackle_score >= gun_score * 1.5:
                    calibrated_score *= 0.35
                    suppression_reason = "fire_crackle"

                # 5. Siren / Transit Attenuation
                elif siren_score > 0.35 and siren_score >= gun_score * 1.5:
                    calibrated_score *= 0.30
                    suppression_reason = "siren"

                # 6. Phase 17 Experimental Animal Vocalization Suppression
                elif self.enable_animal_suppression:
                    animal_score = max(yamnet_scores[i, cls_idx] for cls_idx in YAMNET_ANIMAL_CLASSES)
                    if animal_score > self.animal_thresh and animal_score >= gun_score * self.animal_ratio:
                        calibrated_score *= 0.30
                        suppression_reason = "animal_vocalization"

            window_results.append({
                "window_index": i,
                "start_time": st,
                "end_time": et,
                "score": round(calibrated_score, 4),
                "raw_ensemble_score": round(raw_score, 4),
                "suppressed": suppression_reason is not None,
                "suppression_reason": suppression_reason,
                "triggered": calibrated_score >= self.threshold_base
            })

        events = merge_phase17_events(
            window_results=window_results,
            threshold_base=self.threshold_base,
            threshold_high=self.threshold_high,
            threshold_off=self.threshold_off,
            confirm_windows=self.confirm_windows,
            cooldown_secs=self.cooldown_secs,
            audio_duration_sec=dur_sec,
            allow_short_clip_exception=allow_short_clip_exception,
            crest_factor_db=crest_db,
            min_crest_factor_db=self.min_crest_factor_db,
            single_win_min_crest_db=self.single_win_min_crest_db
        )

        overall_score = max([w["score"] for w in window_results]) if window_results else 0.0
        raw_overall = max([w["raw_ensemble_score"] for w in window_results]) if window_results else 0.0

        return {
            "detected": len(events) > 0,
            "prediction": int(len(events) > 0),
            "overall_score": round(overall_score, 4),
            "raw_ensemble_score": round(raw_overall, 4),
            "detected_events_count": len(events),
            "events_count": len(events),
            "events": events,
            "windows": window_results,
            "duration_seconds": round(dur_sec, 3),
            "audio_duration_sec": round(dur_sec, 3),
            "crest_factor_db": round(crest_db, 2),
            "profile": self.profile,
            "profile_used": self.profile,
            "enable_animal_suppression": self.enable_animal_suppression
        }


class RealTimeStreamDetectorPhase17:
    """
    Phase 17 Real-Time Streaming Audio Detector.
    Implements streaming ring-buffer with Phase 17 calibrated & experimental semantic gating.
    """
    def __init__(
        self,
        profile: str = "balanced",
        detector: Optional[Phase17ExperimentalGunshotDetector] = None,
        sample_rate: int = config.SAMPLE_RATE,
        window_size: int = config.WINDOW_SAMPLES,
        hop_size: int = config.HOP_SAMPLES
    ):
        if detector is not None:
            self.detector = detector
        else:
            self.detector = Phase17ExperimentalGunshotDetector(profile=profile)
        self.profile = profile
        self.sample_rate = sample_rate
        self.window_size = window_size
        self.hop_size = hop_size

        self.buffer = np.zeros(0, dtype=np.float32)
        self.stream_time_sec = 0.0
        self.cooldown_until = -1.0
        self.active_cluster: List[Dict[str, Any]] = []
        self.in_event = False
        self.had_decayed = True

        self.detected_alerts: List[Dict[str, Any]] = []
        self.chunk_latencies_ms: List[float] = []
        self.last_score: float = 0.0
        self.last_crest_factor_db: float = 0.0
        self._lock = threading.Lock()

    @property
    def ring_buffer(self) -> np.ndarray:
        return self.buffer

    @property
    def processed_duration_sec(self) -> float:
        return self.stream_time_sec

    def reset(self) -> None:
        """Reset internal streaming buffer and state machine."""
        with self._lock:
            self.buffer = np.zeros(0, dtype=np.float32)
            self.stream_time_sec = 0.0
            self.cooldown_until = -1.0
            self.active_cluster = []
            self.in_event = False
            self.had_decayed = True
            self.detected_alerts = []
            self.chunk_latencies_ms = []
            self.last_score = 0.0
            self.last_crest_factor_db = 0.0

    def process_chunk(self, audio_chunk: np.ndarray, input_sample_rate: Optional[int] = None) -> List[Dict[str, Any]]:
        """Process incoming audio chunk and return any newly fired alerts."""
        if audio_chunk is None or len(audio_chunk) == 0:
            return []

        # Sanitize corrupted audio
        if not np.all(np.isfinite(audio_chunk)):
            audio_chunk = np.nan_to_num(audio_chunk, nan=0.0, posinf=0.0, neginf=0.0)

        if audio_chunk.ndim > 1:
            audio_chunk = np.mean(audio_chunk, axis=1)

        t_start = time.perf_counter()
        new_alerts = []

        with self._lock:
            self.buffer = np.concatenate([self.buffer, audio_chunk.astype(np.float32)])

            while len(self.buffer) >= self.window_size:
                window_wave = self.buffer[:self.window_size]
                win_st = round(self.stream_time_sec, 3)
                win_et = round(win_st + (self.window_size / self.sample_rate), 3)

                res = self.detector.evaluate_waveform(window_wave, allow_short_clip_exception=False)
                calibrated_s = res["overall_score"]
                crest_db = compute_physical_crest_factor_db(window_wave)

                self.last_score = calibrated_s
                self.last_crest_factor_db = crest_db

                has_sharp_crest = (crest_db >= self.detector.single_win_min_crest_db)
                qualifies_immediate = (calibrated_s >= self.detector.threshold_high and has_sharp_crest)

                win_record = {
                    "start_time": win_st,
                    "end_time": win_et,
                    "score": calibrated_s
                }

                if not self.in_event:
                    if calibrated_s < self.detector.threshold_off:
                        self.had_decayed = True

                    if win_st < self.cooldown_until:
                        if self.had_decayed and (qualifies_immediate or calibrated_s >= self.detector.threshold_base):
                            self.active_cluster.append(win_record)
                            if qualifies_immediate or len(self.active_cluster) >= self.detector.confirm_windows:
                                self.in_event = True
                                self.had_decayed = False
                                alert = _create_streaming_alert_record(self.active_cluster, win_et)
                                new_alerts.append(alert)
                                self.detected_alerts.append(alert)
                                self.cooldown_until = win_et + self.detector.cooldown_secs
                    else:
                        if qualifies_immediate:
                            self.active_cluster = [win_record]
                            self.in_event = True
                            self.had_decayed = False
                            alert = _create_streaming_alert_record(self.active_cluster, win_et)
                            new_alerts.append(alert)
                            self.detected_alerts.append(alert)
                            self.cooldown_until = win_et + self.detector.cooldown_secs
                        elif calibrated_s >= self.detector.threshold_base:
                            self.active_cluster.append(win_record)
                            if len(self.active_cluster) >= self.detector.confirm_windows:
                                self.in_event = True
                                self.had_decayed = False
                                alert = _create_streaming_alert_record(self.active_cluster, win_et)
                                new_alerts.append(alert)
                                self.detected_alerts.append(alert)
                                self.cooldown_until = win_et + self.detector.cooldown_secs
                        else:
                            self.active_cluster = []
                else:
                    if calibrated_s >= self.detector.threshold_off:
                        self.active_cluster.append(win_record)
                    else:
                        self.cooldown_until = win_et + self.detector.cooldown_secs
                        self.active_cluster = []
                        self.in_event = False
                        self.had_decayed = True

                self.buffer = self.buffer[self.hop_size:]
                self.stream_time_sec += (self.hop_size / float(self.sample_rate))

            latency_ms = (time.perf_counter() - t_start) * 1000.0
            self.chunk_latencies_ms.append(latency_ms)

        return new_alerts

def _create_streaming_alert_record(cluster: List[Dict[str, Any]], alert_time_sec: float) -> Dict[str, Any]:
    st = min(w["start_time"] for w in cluster)
    et = max(w["end_time"] for w in cluster)
    max_score = max(w["score"] for w in cluster)
    return {
        "event_id": f"ALERT_{int(alert_time_sec * 1000)}",
        "timestamp_sec": round(alert_time_sec, 3),
        "start_time_sec": round(st, 3),
        "end_time_sec": round(et, 3),
        "duration_sec": round(et - st, 3),
        "score": round(max_score, 4),
        "confirmed_windows": len(cluster)
    }
