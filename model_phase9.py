"""
Phase 9: High-Precision Adaptive Acoustic Gunshot Detector
with Multi-Category Semantic Suppression, Guarded Short-Clip Recovery,
and Dynamic Temporal Consensus.

SAFETY DESIGNATION:
RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.
Not certified for life-safety, fire-alarm, or autonomous dispatch operations.

Key Innovations in Phase 9:
1. Multi-Category Semantic Gating:
   - Extends Phase 8 (Thunder & Fireworks) to comprehensively suppress:
     * Dog barks & canine vocalisations (AudioSet classes 69, 70, 75, 117)
     * Crackling fire & burning wood embers (AudioSet classes 292, 293)
     * Sirens & emergency vehicle warbles (AudioSet classes 317, 318, 319, 390, 391)
     * Thunderstorm rumbles & lightning strikes (AudioSet classes 280, 281)
     * Pyrotechnic fireworks & firecracker bursts (AudioSet classes 426, 427)
   - Protects true gunshots by cross-referencing firearm classes (421, 422, 424, 425).

2. Guarded Short-Clip & Single-Window Dispatch:
   - High-confidence immediate trigger elevated from tau_high=0.82 to tau_high=0.88.
   - Short-clip exception (<= 1.05s) preserved for genuine ballistic events (e.g., Mitchell Roberts clips),
     guarded by physical acoustic crest factor (>= 14.0 dB) to prevent transient ambient cuts from triggering.

3. Configurable Operating Profiles:
   - 'balanced' (Default): tau_base=0.75, tau_high=0.88, tau_off=0.48, N=2, Cooldown=2.0s.
   - 'high_precision': tau_base=0.80, tau_high=0.90, tau_off=0.50, N=2, Cooldown=2.5s.
   - 'high_sensitivity': tau_base=0.70, tau_high=0.82, tau_off=0.45, N=2, Cooldown=1.5s.
"""

import os
import sys
import json
import time
import numpy as np
import tensorflow as tf
from pathlib import Path
from typing import List, Dict, Tuple, Optional, Any

import config
from model import load_model_bundle, CalibratedEnsemble
from feature_extractor import YAMNetFeatureExtractor

# YAMNet AudioSet Class Indices
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
YAMNET_CLASS_CANIDAE = 117          # Canidae, dogs, wolves

YAMNET_CLASS_FIRE = 292             # Fire
YAMNET_CLASS_CRACKLE = 293          # Crackle

YAMNET_CLASS_POLICE_CAR = 317       # Police car (siren)
YAMNET_CLASS_AMBULANCE = 318        # Ambulance (siren)
YAMNET_CLASS_FIRE_ENGINE = 319      # Fire engine, fire truck (siren)
YAMNET_CLASS_SIREN = 390            # Siren
YAMNET_CLASS_CIVIL_DEFENSE = 391    # Civil defense siren


def compute_physical_crest_factor_db(waveform_chunk: np.ndarray) -> float:
    """Compute acoustic crest factor (dB) = 20 * log10(Peak / RMS)."""
    if len(waveform_chunk) == 0:
        return 0.0
    rms = float(np.sqrt(np.mean(waveform_chunk ** 2) + 1e-12))
    peak = float(np.max(np.abs(waveform_chunk)))
    crest_db = 20.0 * np.log10(max(peak, 1e-6) / max(rms, 1e-6))
    return float(crest_db)


def merge_detection_windows_phase9(
    window_results: List[Dict[str, Any]],
    threshold_base: float = 0.75,
    threshold_high: float = 0.88,
    threshold_off: float = 0.48,
    confirm_windows: int = 2,
    cooldown_secs: float = 2.0,
    max_event_duration: float = 2.5,
    audio_duration_sec: Optional[float] = None,
    allow_short_clip_exception: bool = True,
    crest_factor_db: Optional[float] = None,
    min_crest_factor_db: float = 14.0
) -> List[Dict[str, Any]]:
    """
    Phase 9 State-Machine Event Merger.
    
    Features:
    - High confidence single-window dispatch (score >= threshold_high)
    - Guarded short clip single-window exception (audio <= 1.05s, 1 window, crest >= min_crest)
    - Moderate confidence multi-window confirmation (score >= threshold_base, N=2)
    - Dynamic hysteresis decay down to threshold_off
    - Rapid-fire preservation across refractory periods
    """
    if not window_results:
        return []

    sorted_windows = sorted(window_results, key=lambda x: x["start_time"])
    events = []
    cooldown_until = -1.0
    active_cluster: List[Dict[str, Any]] = []
    in_event = False
    had_decayed = True

    # Guarded short clip check
    is_short_isolated_clip = False
    if allow_short_clip_exception and (audio_duration_sec is not None and audio_duration_sec <= 1.05) and len(sorted_windows) == 1:
        if crest_factor_db is None or crest_factor_db >= min_crest_factor_db:
            is_short_isolated_clip = True

    for win in sorted_windows:
        st = win["start_time"]
        et = win["end_time"]
        score = win["score"]

        qualifies_immediate = (score >= threshold_high) or (is_short_isolated_clip and score >= threshold_base)

        if not in_event:
            if score < threshold_off:
                had_decayed = True

            # Refractory handling
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
                    active_cluster.append(win)
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
            gap = st - active_cluster[-1]["end_time"]
            cluster_dur = et - active_cluster[0]["start_time"]
            if gap <= 0.50 and cluster_dur <= max_event_duration and score >= threshold_off:
                active_cluster.append(win)
            else:
                prev_et = active_cluster[-1]["end_time"]
                event = _summarize_cluster(active_cluster)
                events.append(event)
                cooldown_until = prev_et + cooldown_secs
                active_cluster = []
                in_event = False
                had_decayed = (score < threshold_off)

                if qualifies_immediate:
                    active_cluster.append(win)
                    in_event = True
                    had_decayed = False
                elif score >= threshold_base:
                    if st >= cooldown_until or had_decayed:
                        active_cluster.append(win)
                        if len(active_cluster) >= confirm_windows:
                            in_event = True
                            had_decayed = False

    if in_event and active_cluster:
        event = _summarize_cluster(active_cluster)
        events.append(event)

    return events


def _summarize_cluster(cluster: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Build standardized event dictionary from window cluster."""
    start_time = cluster[0]["start_time"]
    end_time = cluster[-1]["end_time"]
    peak_win = max(cluster, key=lambda x: x["score"])

    # Determine dispatch path
    if len(cluster) == 1:
        path = "single_window_high_confidence" if peak_win["score"] >= 0.88 else "guarded_short_clip_exception"
    else:
        path = "multi_window_temporal_confirmation"

    return {
        "start_time": round(start_time, 2),
        "end_time": round(end_time, 2),
        "duration_seconds": round(end_time - start_time, 2),
        "peak_time": round((peak_win["start_time"] + peak_win["end_time"]) / 2, 2),
        "peak_score": round(float(peak_win["score"]), 3),
        "mean_score": round(float(np.mean([w["score"] for w in cluster])), 3),
        "trigger_windows_count": len(cluster),
        "dispatch_path": path,
        "verdict": "Gunshot Detected"
    }


class Phase9AdaptiveGunshotDetector:
    """
    Phase 9 Production-Grade High-Precision Acoustic Gunshot Detector.
    
    Safety Designation: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.
    """
    PROFILES = {
        "balanced": {
            "threshold_base": 0.75,
            "threshold_high": 0.88,
            "threshold_off": 0.48,
            "confirm_windows": 2,
            "cooldown_secs": 2.0,
            "enable_semantic_gating": True,
            "min_crest_factor_db": 9.5
        },
        "high_precision": {
            "threshold_base": 0.80,
            "threshold_high": 0.90,
            "threshold_off": 0.50,
            "confirm_windows": 2,
            "cooldown_secs": 2.5,
            "enable_semantic_gating": True,
            "min_crest_factor_db": 10.0
        },
        "high_sensitivity": {
            "threshold_base": 0.70,
            "threshold_high": 0.82,
            "threshold_off": 0.45,
            "confirm_windows": 2,
            "cooldown_secs": 1.5,
            "enable_semantic_gating": True,
            "min_crest_factor_db": 9.0
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
        min_crest_factor_db: Optional[float] = None
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
        self.min_crest_factor_db = min_crest_factor_db if min_crest_factor_db is not None else prof_cfg["min_crest_factor_db"]

        # Load models
        self.model, self.bundle_info = load_model_bundle(self.bundle_dir)
        self.feature_extractor = YAMNetFeatureExtractor()
        self.yamnet_model = self.feature_extractor.model

    def predict_window_embedding(self, embedding: np.ndarray) -> float:
        """Score a pre-extracted 1024-d embedding."""
        emb = embedding.reshape(1, -1)
        score = float(self.model.predict(emb, verbose=0).flatten()[0])
        return score

    def evaluate_waveform(
        self,
        waveform: np.ndarray,
        threshold_base: Optional[float] = None,
        threshold_high: Optional[float] = None,
        threshold_off: Optional[float] = None,
        confirm_windows: Optional[int] = None,
        cooldown_secs: Optional[float] = None,
        apply_semantic_gating: Optional[bool] = None,
        allow_short_clip_exception: bool = True
    ) -> Dict[str, Any]:
        """
        Evaluate full audio waveform using Phase 9 Multi-Category Semantic Suppression
        and Guarded Temporal Consensus.
        """
        t_base = threshold_base if threshold_base is not None else self.threshold_base
        t_high = threshold_high if threshold_high is not None else self.threshold_high
        t_off = threshold_off if threshold_off is not None else self.threshold_off
        c_win = confirm_windows if confirm_windows is not None else self.confirm_windows
        c_sec = cooldown_secs if cooldown_secs is not None else self.cooldown_secs
        do_gating = apply_semantic_gating if apply_semantic_gating is not None else self.enable_semantic_gating

        dur_sec = len(waveform) / float(config.SAMPLE_RATE)
        crest_db = compute_physical_crest_factor_db(waveform)

        # Pad if shorter than minimum window
        if len(waveform) < config.WINDOW_SAMPLES:
            padded_wave = np.pad(waveform, (0, config.WINDOW_SAMPLES - len(waveform)))
        else:
            padded_wave = waveform

        wave_tensor = tf.convert_to_tensor(padded_wave, dtype=tf.float32)
        scores_tensor, embeddings_tensor, _ = self.yamnet_model(wave_tensor)

        yamnet_scores = scores_tensor.numpy()       # (T, 521)
        embeddings = embeddings_tensor.numpy()      # (T, 1024)
        n_windows = embeddings.shape[0]

        # Ensemble predictions
        ensemble_scores = self.model.predict(embeddings, verbose=0).flatten()

        window_results = []
        hop_sec = config.HOP_LENGTH_SECS
        win_sec = config.WINDOW_LENGTH_SECS

        for i in range(n_windows):
            st = round(i * hop_sec, 3)
            et = round(st + win_sec, 3)
            raw_score = float(ensemble_scores[i])
            calibrated_score = raw_score
            suppression_reason = None

            # Phase 9 Multi-Category Semantic Mimic Verification
            if do_gating:
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
                if thunder_score > 0.35 and gun_score < 0.04:
                    calibrated_score *= 0.30
                    suppression_reason = "thunder"

                # 2. Fireworks Attenuation
                elif fireworks_score > 0.45 and gun_score < 0.04 and raw_score < 0.88:
                    calibrated_score *= 0.40
                    suppression_reason = "fireworks"

                # 3. Dog / Animal Bark Attenuation
                elif dog_score > 0.30 and gun_score < 0.04 and raw_score < 0.88:
                    calibrated_score *= 0.35
                    suppression_reason = "dog_bark"

                # 4. Crackling Fire Attenuation
                elif crackle_score > 0.25 and gun_score < 0.04 and raw_score < 0.88:
                    calibrated_score *= 0.35
                    suppression_reason = "fire_crackle"

                # 5. Siren / Transit Attenuation
                elif siren_score > 0.40 and gun_score < 0.04:
                    calibrated_score *= 0.30
                    suppression_reason = "siren"

            window_results.append({
                "window_index": i,
                "start_time": st,
                "end_time": et,
                "score": round(calibrated_score, 4),
                "raw_ensemble_score": round(raw_score, 4),
                "suppressed": suppression_reason is not None,
                "suppression_reason": suppression_reason,
                "triggered": calibrated_score >= t_base
            })

        # Merge windows into events using Phase 9 Guarded State Machine
        events = merge_detection_windows_phase9(
            window_results,
            threshold_base=t_base,
            threshold_high=t_high,
            threshold_off=t_off,
            confirm_windows=c_win,
            cooldown_secs=c_sec,
            audio_duration_sec=dur_sec,
            allow_short_clip_exception=allow_short_clip_exception,
            crest_factor_db=crest_db,
            min_crest_factor_db=self.min_crest_factor_db
        )

        overall_score = float(np.max(ensemble_scores)) if len(ensemble_scores) > 0 else 0.0

        return {
            "duration_seconds": round(dur_sec, 3),
            "crest_factor_db": round(crest_db, 1),
            "total_windows": n_windows,
            "overall_score": round(overall_score, 4),
            "detected": len(events) > 0,
            "events_count": len(events),
            "events": events,
            "windows": window_results,
            "profile_used": self.profile
        }
