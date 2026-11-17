"""
Phase 8: Adaptive Acoustic Gunshot Detector with Transient Generalization,
Semantic Mimic Rejection, and Short-Event Recovery.

Key Architectural Advancements:
1. Dual-Threshold Evidence Confirmation:
   - High-confidence trigger (tau_high >= 0.82): Immediate single-window alert dispatch (N=1).
   - Moderate-confidence trigger (tau >= 0.70): Requires two-window temporal confirmation (N=2).
2. Short-Clip / Isolated Event Recovery:
   - If audio clip duration <= 1.0s and only a single analysis window exists,
     a score >= tau is dispatched immediately, preventing the Phase 7 short-clip truncation trap.
3. Semantic Context Mimic Attenuation:
   - Inspects YAMNet 521-class probabilities alongside the 1024-d embedding.
   - Rejects thunder and fireworks transients when YAMNet indicates high thunder/fireworks probability
     AND gunshot probability is near zero (< 0.03), while preserving muffled urban gunshots.
4. Dynamic Reverberation Hysteresis & Rapid-Fire Preservation:
   - Dynamic threshold_off (0.45) tracks room reverberation without duplicate alerts.
   - Refractory cooldown resets when signal decays below threshold_off and a new distinct onset arrives.
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
YAMNET_CLASS_GUNSHOT = 421      # Gunshot, gunfire
YAMNET_CLASS_MACHINE_GUN = 422  # Machine gun
YAMNET_CLASS_ARTILLERY = 424    # Artillery fire
YAMNET_CLASS_CAP_GUN = 425      # Cap gun

YAMNET_CLASS_THUNDERSTORM = 280 # Thunderstorm
YAMNET_CLASS_THUNDER = 281      # Thunder
YAMNET_CLASS_FIREWORKS = 426    # Fireworks
YAMNET_CLASS_FIRECRACKER = 427  # Firecracker


def merge_detection_windows_adaptive(
    window_results: List[Dict[str, Any]],
    threshold_base: float = 0.70,
    threshold_high: float = 0.82,
    threshold_off: float = 0.45,
    confirm_windows: int = 2,
    cooldown_secs: float = 1.5,
    max_event_duration: float = 2.5,
    audio_duration_sec: Optional[float] = None,
    allow_short_clip_exception: bool = True
) -> List[Dict[str, Any]]:
    """
    Phase 8 Adaptive State-Machine Event Merger.
    
    Handles:
    - High confidence single-window dispatch (score >= threshold_high)
    - Moderate confidence multi-window confirmation (score >= threshold_base, N=2)
    - Short clip single-window exception (audio <= 1.0s and exactly 1 window)
    - Dynamic hysteresis decay down to threshold_off
    - Rapid-fire gunshot preservation past refractory reset
    """
    if not window_results:
        return []

    sorted_windows = sorted(window_results, key=lambda x: x["start_time"])
    events = []
    cooldown_until = -1.0
    active_cluster: List[Dict[str, Any]] = []
    in_event = False
    had_decayed = True

    # Short clip check: if total duration <= 1.0s and only 1 window is analyzed
    is_short_isolated_clip = (
        allow_short_clip_exception and
        (audio_duration_sec is not None and audio_duration_sec <= 1.05) and
        len(sorted_windows) == 1
    )

    for win in sorted_windows:
        st = win["start_time"]
        et = win["end_time"]
        score = win["score"]

        # Check if single window qualifies for high confidence or short-clip trigger
        qualifies_immediate = (score >= threshold_high) or (is_short_isolated_clip and score >= threshold_base)

        if not in_event:
            if score < threshold_off:
                had_decayed = True

            # Refractory period handling
            if st < cooldown_until:
                # In cooldown: only a new strong onset after decay can trigger
                if had_decayed and (qualifies_immediate or score >= threshold_base):
                    active_cluster.append(win)
                    if qualifies_immediate or len(active_cluster) >= confirm_windows:
                        in_event = True
                        had_decayed = False
                else:
                    continue
            else:
                # Normal evaluation past cooldown
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
            # Active event: track reverberant tail
            gap = st - active_cluster[-1]["end_time"]
            cluster_dur = et - active_cluster[0]["start_time"]
            if gap <= 0.50 and cluster_dur <= max_event_duration and score >= threshold_off:
                active_cluster.append(win)
            else:
                # Close previous event
                prev_et = active_cluster[-1]["end_time"]
                event = _summarize_cluster(active_cluster)
                events.append(event)
                cooldown_until = prev_et + cooldown_secs
                active_cluster = []
                in_event = False
                had_decayed = (score < threshold_off)

                # Evaluate current window for immediate new onset trigger
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

    # Close trailing open event
    if in_event and active_cluster:
        event = _summarize_cluster(active_cluster)
        events.append(event)

    return events


def _summarize_cluster(cluster: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Build standardized event dictionary from window cluster."""
    start_time = cluster[0]["start_time"]
    end_time = cluster[-1]["end_time"]
    peak_win = max(cluster, key=lambda x: x["score"])

    return {
        "start_time": round(start_time, 2),
        "end_time": round(end_time, 2),
        "duration_seconds": round(end_time - start_time, 2),
        "peak_time": round((peak_win["start_time"] + peak_win["end_time"]) / 2, 2),
        "peak_score": round(float(peak_win["score"]), 3),
        "mean_score": round(float(np.mean([w["score"] for w in cluster])), 3),
        "trigger_windows_count": len(cluster),
        "verdict": "Gunshot Detected"
    }


class AdaptiveGunshotDetector:
    """
    Phase 8 Production-Grade Acoustic Gunshot Detector.
    
    Combines:
    - Pretrained YAMNet backbone with semantic class scoring.
    - Calibrated stacking ensemble (MLP + CatBoost + LightGBM + XGBoost).
    - Semantic mimic attenuation (Thunder & Fireworks suppression).
    - Adaptive multi-threshold state machine (Single-window high confidence & short clip recovery).
    """
    def __init__(
        self,
        bundle_dir: Path = config.MODELS_DIR / "gunshot_yamnet_bundle",
        threshold_base: float = 0.70,
        threshold_high: float = 0.82,
        threshold_off: float = 0.45,
        confirm_windows: int = 2,
        cooldown_secs: float = 1.5,
        enable_semantic_gating: bool = True
    ):
        self.bundle_dir = Path(bundle_dir)
        self.threshold_base = threshold_base
        self.threshold_high = threshold_high
        self.threshold_off = threshold_off
        self.confirm_windows = confirm_windows
        self.cooldown_secs = cooldown_secs
        self.enable_semantic_gating = enable_semantic_gating

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
        apply_semantic_gating: Optional[bool] = None
    ) -> Dict[str, Any]:
        """
        Evaluate full audio waveform.
        Returns window-level details, semantic predictions, and merged physical events.
        """
        t_base = threshold_base if threshold_base is not None else self.threshold_base
        t_high = threshold_high if threshold_high is not None else self.threshold_high
        t_off = threshold_off if threshold_off is not None else self.threshold_off
        c_win = confirm_windows if confirm_windows is not None else self.confirm_windows
        c_sec = cooldown_secs if cooldown_secs is not None else self.cooldown_secs
        do_gating = apply_semantic_gating if apply_semantic_gating is not None else self.enable_semantic_gating

        dur_sec = len(waveform) / float(config.SAMPLE_RATE)
        
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

            # Semantic Mimic Verification
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

                # 1. Thunder Attenuation: high thunder, near zero gunshot
                if thunder_score > 0.40 and gun_score < 0.03:
                    calibrated_score *= 0.35

                # 2. Fireworks Attenuation: high fireworks, near zero gunshot, ensemble < 0.85
                if fireworks_score > 0.60 and gun_score < 0.03 and raw_score < 0.85:
                    calibrated_score *= 0.50

            window_results.append({
                "window_index": i,
                "start_time": st,
                "end_time": et,
                "score": calibrated_score,
                "raw_ensemble_score": raw_score,
                "triggered": calibrated_score >= t_base
            })

        # Merge windows into events using Phase 8 Adaptive State Machine
        events = merge_detection_windows_adaptive(
            window_results,
            threshold_base=t_base,
            threshold_high=t_high,
            threshold_off=t_off,
            confirm_windows=c_win,
            cooldown_secs=c_sec,
            audio_duration_sec=dur_sec,
            allow_short_clip_exception=True
        )

        overall_score = float(np.max(ensemble_scores)) if len(ensemble_scores) > 0 else 0.0
        
        return {
            "duration_seconds": round(dur_sec, 3),
            "total_windows": n_windows,
            "overall_score": round(overall_score, 4),
            "detected": len(events) > 0,
            "events_count": len(events),
            "events": events,
            "windows": window_results
        }
