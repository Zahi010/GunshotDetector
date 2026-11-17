"""
Phase 14 Candidate Adaptive Gunshot Detector.

Implements calibrated robustness improvements audited in Phase 14:
1. Calibrated Semantic Gating with Ballistic Protection:
   - Thunder, Dog, Siren, and Crackle relative semantic suppression preserved.
   - Fireworks Relative Semantic Dominance calibrated: requires fire_score > 0.35,
     dominance ratio >= 2.0 * gun_score, AND gun_score < 0.05.
     This strictly prevents collateral suppression of genuine AR-15 rifle cracks and
     heavy shotgun blasts that exhibit pyrotechnic acoustic ambiguity.
2. Guarded Consensus Temporal Logic:
   - Single-window immediate dispatch requires acoustic crest factor >= 12.0 dB (or N=2 consensus).
   - Short isolated clip exception threshold set to 8.8 dB for muffled gunshot recovery.
3. Thread-safe streaming ring-buffer with explicit reset and latency profiling.
4. Backwards compatibility with Phase 9 / Phase 13 model bundles.

SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.
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

def compute_physical_crest_factor_db(waveform_chunk: np.ndarray) -> float:
    """Compute acoustic crest factor (dB) = 20 * log10(Peak / RMS)."""
    if len(waveform_chunk) == 0:
        return 0.0
    peak = float(np.max(np.abs(waveform_chunk)))
    rms = float(np.sqrt(np.mean(waveform_chunk ** 2)))
    if rms < 1e-9:
        return 0.0
    return float(20.0 * np.log10(max(peak, 1e-6) / max(rms, 1e-6)))

def merge_phase14_events(
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
    Phase 14 State-Machine Event Merger.
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
                events.append(_create_phase14_event_record(active_cluster))
                cooldown_until = max(w["end_time"] for w in active_cluster) + cooldown_secs
                active_cluster = []
                in_event = False
                had_decayed = True

    if in_event and active_cluster:
        events.append(_create_phase14_event_record(active_cluster))

    return events

def _create_phase14_event_record(cluster: List[Dict[str, Any]]) -> Dict[str, Any]:
    start_time = min(w["start_time"] for w in cluster)
    end_time = max(w["end_time"] for w in cluster)
    peak_win = max(cluster, key=lambda w: w["score"])
    path = "single_window_high_confidence" if len(cluster) == 1 else "multi_window_confirmation"

    return {
        "start_time": round(start_time, 2),
        "end_time": round(end_time, 2),
        "duration_seconds": round(end_time - start_time, 2),
        "peak_time": round((peak_win["start_time"] + peak_win["end_time"]) / 2, 2),
        "peak_score": round(float(peak_win["score"]), 3),
        "mean_score": round(float(np.mean([w["score"] for w in cluster])), 3),
        "trigger_windows_count": len(cluster),
        "dispatch_path": path,
        "verdict": "Gunshot-like acoustic event detected"
    }

class Phase14CandidateGunshotDetector:
    """
    Phase 14 Calibrated Gunshot Detector with Ballistic Protection
    and Guarded Consensus Temporal Logic.
    """
    PROFILES = {
        "balanced": {
            "threshold_base": 0.75,
            "threshold_high": 0.88,
            "threshold_off": 0.48,
            "confirm_windows": 2,
            "cooldown_secs": 2.0,
            "enable_semantic_gating": True,
            "min_crest_factor_db": 8.8,
            "single_win_min_crest_db": 12.0,
            "fw_thresh": 0.35,
            "fw_ratio": 2.0,
            "fw_gun_max": 0.05,
            "thun_thresh": 0.25,
            "thun_ratio": 1.5
        },
        "high_precision": {
            "threshold_base": 0.80,
            "threshold_high": 0.90,
            "threshold_off": 0.52,
            "confirm_windows": 2,
            "cooldown_secs": 2.5,
            "enable_semantic_gating": True,
            "min_crest_factor_db": 8.8,
            "single_win_min_crest_db": 12.0,
            "fw_thresh": 0.35,
            "fw_ratio": 2.0,
            "fw_gun_max": 0.05,
            "thun_thresh": 0.25,
            "thun_ratio": 1.5
        },
        "high_sensitivity": {
            "threshold_base": 0.70,
            "threshold_high": 0.85,
            "threshold_off": 0.42,
            "confirm_windows": 2,
            "cooldown_secs": 1.5,
            "enable_semantic_gating": True,
            "min_crest_factor_db": 8.5,
            "single_win_min_crest_db": 11.0,
            "fw_thresh": 0.40,
            "fw_ratio": 2.5,
            "fw_gun_max": 0.06,
            "thun_thresh": 0.25,
            "thun_ratio": 1.5
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
        min_crest_factor_db: Optional[float] = None,
        single_win_min_crest_db: Optional[float] = None,
        fw_thresh: Optional[float] = None,
        fw_ratio: Optional[float] = None,
        fw_gun_max: Optional[float] = None
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
        self.single_win_min_crest_db = single_win_min_crest_db if single_win_min_crest_db is not None else prof_cfg["single_win_min_crest_db"]
        self.fw_thresh = fw_thresh if fw_thresh is not None else prof_cfg["fw_thresh"]
        self.fw_ratio = fw_ratio if fw_ratio is not None else prof_cfg["fw_ratio"]
        self.fw_gun_max = fw_gun_max if fw_gun_max is not None else prof_cfg["fw_gun_max"]
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
        """Evaluate full waveform with Phase 14 Calibrated Semantic Gating."""
        dur_sec = len(waveform) / float(config.SAMPLE_RATE)
        crest_db = compute_physical_crest_factor_db(waveform)

        if len(waveform) < config.WINDOW_SAMPLES:
            padded_wave = np.pad(waveform, (0, config.WINDOW_SAMPLES - len(waveform)))
        else:
            padded_wave = waveform

        import tensorflow as tf
        wave_tensor = tf.convert_to_tensor(padded_wave, dtype=tf.float32)
        yamnet_scores, embeddings, _ = self.yamnet_model(wave_tensor)
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

                # 1. Thunder Attenuation (Distinct acoustics)
                if thunder_score > self.thun_thresh and thunder_score >= gun_score * self.thun_ratio:
                    calibrated_score *= 0.30
                    suppression_reason = "thunder"

                # 2. Fireworks Attenuation with Ballistic Safeguard
                # Only suppress if fire_s > thresh AND dominates gun_s by fw_ratio AND gun_s < fw_gun_max
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

        events = merge_phase14_events(
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

        scores = [w["score"] for w in window_results]
        return {
            "duration_seconds": round(dur_sec, 3),
            "crest_factor_db": round(crest_db, 1),
            "total_windows": n_windows,
            "overall_score": float(np.max(scores)) if scores else 0.0,
            "detected": len(events) > 0,
            "events_count": len(events),
            "events": events,
            "windows": window_results,
            "profile_used": self.profile
        }

class RealTimeStreamDetectorPhase14:
    """
    Phase 14 Real-Time Streaming Gunshot Detector.
    Implements streaming ring-buffer with Phase 14 calibrated semantic gating
    and guarded single-window dispatch. Thread-safe.
    """
    def __init__(
        self,
        profile: str = "balanced",
        chunk_duration_sec: float = 0.48,
        sample_rate: int = config.SAMPLE_RATE
    ):
        self.detector = Phase14CandidateGunshotDetector(profile=profile)
        self.chunk_size = int(chunk_duration_sec * sample_rate)
        self.window_size = config.WINDOW_SAMPLES
        self.hop_size = config.HOP_SAMPLES
        self.sample_rate = sample_rate
        self.lock = threading.Lock()

        self.buffer = np.zeros(0, dtype=np.float32)
        self.stream_time_sec = 0.0

        self.active_cluster: List[Dict[str, Any]] = []
        self.in_event = False
        self.had_decayed = True
        self.cooldown_until = -1.0
        self.last_score = 0.0
        self.last_crest_factor_db = 0.0
        self.detected_alerts: List[Dict[str, Any]] = []
        self.chunk_latencies_ms: List[float] = []

    def reset(self):
        with self.lock:
            self.buffer = np.zeros(0, dtype=np.float32)
            self.stream_time_sec = 0.0
            self.active_cluster = []
            self.in_event = False
            self.had_decayed = True
            self.cooldown_until = -1.0
            self.last_score = 0.0
            self.last_crest_factor_db = 0.0
            self.detected_alerts = []
            self.chunk_latencies_ms = []

    def process_chunk(self, chunk: np.ndarray, input_sample_rate: Optional[int] = None) -> List[Dict[str, Any]]:
        t_start = time.perf_counter()
        new_alerts = []

        if chunk is None or len(chunk) == 0:
            return []

        if np.isnan(chunk).any() or np.isinf(chunk).any():
            chunk = np.nan_to_num(chunk, nan=0.0, posinf=0.0, neginf=0.0)

        if input_sample_rate is not None and input_sample_rate != self.sample_rate:
            import scipy.signal
            num_samples = int(len(chunk) * self.sample_rate / input_sample_rate)
            chunk = scipy.signal.resample(chunk, num_samples)

        with self.lock:
            self.buffer = np.concatenate([self.buffer, chunk.astype(np.float32)])

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
    peak_s = max(w["score"] for w in cluster)
    path = "single_window_high_confidence" if len(cluster) == 1 else "multi_window_confirmation"

    return {
        "alert_id": f"phase14_alert_{int(alert_time_sec * 1000)}",
        "alert_time_sec": round(alert_time_sec, 3),
        "event_start_sec": round(st, 3),
        "event_end_sec": round(et, 3),
        "duration_sec": round(et - st, 3),
        "peak_score": round(float(peak_s), 3),
        "trigger_windows_count": len(cluster),
        "dispatch_path": path,
        "classification": "GUNSHOT_ALERT",
        "safety_warning": "RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY"
    }
