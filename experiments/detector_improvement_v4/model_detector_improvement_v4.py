# ==============================================================================
# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY
#
# Uncertified acoustic research software. Never deploy for autonomous emergency
# dispatch, tactical police response, active-shooter alerting, automated evacuation,
# lockdown, or life-critical physical security. Safe recorded audio playback only;
# no live-fire testing.
# ==============================================================================

import json
import logging
import os
import pathlib
from typing import Any, Dict, List, Optional, Tuple, Union

import joblib
import numpy as np
import tensorflow as tf
import soundfile as sf

from experiments.phase36.event_state_machine import (
    EventState,
    EventStateMachine,
    TransitionReason
)

logger = logging.getLogger("detector_improvement_v4")

# ------------------------------------------------------------------------------
# YAMNet Semantic Class Mappings
# ------------------------------------------------------------------------------
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
YAMNET_CLASS_GLASS = 433
YAMNET_CLASS_SHATTER = 435
YAMNET_CLASS_SHARP_CRACK = 436

GUN_CLASSES = [YAMNET_CLASS_GUNSHOT, YAMNET_CLASS_MACHINE_GUN, YAMNET_CLASS_ARTILLERY, YAMNET_CLASS_CAP_GUN]
BALLISTIC_CLASSES = [
    YAMNET_CLASS_EXPLOSION, YAMNET_CLASS_GUNSHOT, YAMNET_CLASS_MACHINE_GUN,
    YAMNET_CLASS_ARTILLERY, YAMNET_CLASS_CAP_GUN, YAMNET_CLASS_BURST_POP,
    YAMNET_CLASS_CRACK, YAMNET_CLASS_BANG
]
FIREWORKS_CLASSES = [YAMNET_CLASS_FIREWORKS, YAMNET_CLASS_FIRECRACKER]
THUNDER_CLASSES = [YAMNET_CLASS_THUNDERSTORM, YAMNET_CLASS_THUNDER]
DOG_CLASSES = [YAMNET_CLASS_DOG, YAMNET_CLASS_BARK, YAMNET_CLASS_YIP, YAMNET_CLASS_CANIDAE]
CRACKLE_CLASSES = [YAMNET_CLASS_FIRE, YAMNET_CLASS_CRACKLE]
SIREN_CLASSES = [YAMNET_CLASS_POLICE_CAR, YAMNET_CLASS_AMBULANCE, YAMNET_CLASS_FIRE_ENGINE, YAMNET_CLASS_SIREN, YAMNET_CLASS_CIVIL_DEFENSE]
WIND_CLASSES = [YAMNET_CLASS_WIND, YAMNET_CLASS_WIND_NOISE_MIC]
IMPACT_CLASSES = [YAMNET_CLASS_HAMMER, YAMNET_CLASS_JACKHAMMER, YAMNET_CLASS_SLAM, YAMNET_CLASS_KNOCK, YAMNET_CLASS_CLAP]
GLASS_CLASSES = [YAMNET_CLASS_GLASS, YAMNET_CLASS_SHATTER, YAMNET_CLASS_SHARP_CRACK]

NON_TARGET_SEMANTIC_CLASSES = (
    [0] + # Speech
    list(range(67, 118)) + # Animal vocalizations
    list(range(300, 331)) + # Motor vehicles and traffic
    [502, 503, 504] # Outside / Natural ambient
)


def compute_physical_acoustic_features_v4(y_win: np.ndarray, sr: int = 16000) -> Tuple[float, float, float, float, float, float, float, float]:
    """
    Computes 8 physical acoustic features in <0.28ms on a 0.96-second window:
    1. crest_factor_db: 20 * log10(peak / RMS)
    2. spectral_flatness: exp(mean(log(P))) / mean(P)
    3. high_band_ratio: energy >= 2500 Hz / total energy
    4. mid_band_ratio: energy in [500 Hz, 2500 Hz] / total energy
    5. low_band_ratio: energy < 500 Hz / total energy
    6. mid_to_low_ratio: (mid + 1e-4) / (low + 1e-4)
    7. channel_rolloff_ratio: (high + 1e-4) / (mid + 1e-4)
    8. spectral_centroid_hz: sum(f * P) / total energy
    """
    if len(y_win) == 0:
        return 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0
    pk = float(np.max(np.abs(y_win)))
    rms = float(np.sqrt(np.mean(y_win**2) + 1e-12))
    crest_db = float(20.0 * np.log10(max(pk / (rms + 1e-12), 1.0)))

    # Vectorized fast power spectrum
    P = np.abs(np.fft.rfft(y_win))**2
    freqs = np.fft.rfftfreq(len(y_win), d=1.0 / float(sr))

    log_p = np.log(P + 1e-12)
    flatness = float(np.exp(np.mean(log_p)) / (np.mean(P) + 1e-12))

    tot_e = float(np.sum(P) + 1e-12)
    low_e = float(np.sum(P[freqs < 500.0]))
    mid_e = float(np.sum(P[(freqs >= 500.0) & (freqs < 2500.0)]))
    high_e = float(np.sum(P[freqs >= 2500.0]))

    low_ratio = float(low_e / tot_e)
    mid_ratio = float(mid_e / tot_e)
    high_ratio = float(high_e / tot_e)

    mid_to_low = float((mid_ratio + 1e-4) / (low_ratio + 1e-4))
    rolloff = float((high_ratio + 1e-4) / (mid_ratio + 1e-4))
    centroid = float(np.sum(freqs * P) / tot_e)

    return crest_db, flatness, high_ratio, mid_ratio, low_ratio, mid_to_low, rolloff, centroid


class CalibratedAcousticSuppressionV4:
    """
    Calibrated Multi-Category Semantic Suppression V4:
    - Ballistic Coherence Safeguard.
    - Ballistic Shockwave Protection: Prevents authentic gunshot explosions from being
      erroneously suppressed by fireworks filters when ballistic explosive evidence is strong.
    - Two-tier Pyrotechnic Gating (standard vs dominant fireworks).
    - Glass Shatter & High-Frequency Non-Ballistic Gating (resolves V3 false positives).
    - Infrasonic Rumble & Wind Buffeting Attenuation.
    - Mechanical Impact & Clatter Suppression.
    - Calibrated Thunder, Canine, Fire Crackle, and Siren Suppression.
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
        self.glass_cfg = suppression_cfg.get("glass", {
            "threshold": 0.30,
            "min_high_band_ratio": 0.30,
            "max_ballistic": 0.20,
            "attenuation": 0.35
        })
        self.canine_cfg = suppression_cfg.get("canine", {"threshold": 0.30, "attenuation": 0.25})
        self.crackle_cfg = suppression_cfg.get("crackle", {"threshold": 0.35, "attenuation": 0.30})
        self.siren_cfg = suppression_cfg.get("siren", {"threshold": 0.25, "attenuation": 0.20})
        self.impact_cfg = suppression_cfg.get("mechanical_impact", {
            "enabled": True,
            "impact_threshold": 0.25,
            "impact_to_gun_ratio": 1.6,
            "gun_score_max": 0.20,
            "attenuation": 0.35
        })

    def apply_suppression(
        self,
        raw_score: float,
        yamnet_scores: np.ndarray,
        high_band_ratio: float = 0.10,
        is_in_confirmed_event: bool = False
    ) -> Dict[str, Any]:
        if not self.enabled:
            return {
                "adjusted_score": raw_score,
                "suppression_active": False,
                "reasons": []
            }

        adjusted_score = float(raw_score)
        reasons = []

        gun_max = max(float(yamnet_scores[cls]) for cls in GUN_CLASSES)
        bal_max = max(float(yamnet_scores[cls]) for cls in BALLISTIC_CLASSES)
        fw_max = max(float(yamnet_scores[cls]) for cls in FIREWORKS_CLASSES)
        thun_max = max(float(yamnet_scores[cls]) for cls in THUNDER_CLASSES)
        dog_max = max(float(yamnet_scores[cls]) for cls in DOG_CLASSES)
        crackle_max = max(float(yamnet_scores[cls]) for cls in CRACKLE_CLASSES)
        siren_max = max(float(yamnet_scores[cls]) for cls in SIREN_CLASSES)
        impact_max = max(float(yamnet_scores[cls]) for cls in IMPACT_CLASSES)
        glass_max = max(float(yamnet_scores[cls]) for cls in GLASS_CLASSES)
        nt_max = max(float(yamnet_scores[cls]) for cls in NON_TARGET_SEMANTIC_CLASSES)

        # 1. Ballistic Coherence Safeguard
        if self.coherence_cfg.get("enabled", True):
            if (bal_max < self.coherence_cfg["ballistic_max_threshold"] and
                nt_max > self.coherence_cfg["non_target_threshold"] and
                raw_score > 0.40):
                adjusted_score = max(0.0, adjusted_score - self.coherence_cfg["attenuation"])
                reasons.append("BALLISTIC_INCOHERENCE")

        # 2. Thunder & Infrasonic Rumble
        if thun_max > self.thun_cfg["threshold"] and (thun_max > self.thun_cfg["ratio"] * gun_max):
            adjusted_score = max(0.0, adjusted_score - self.thun_cfg["attenuation"])
            reasons.append("THUNDER_SUPPRESSION")

        # 3. Ballistic Shockwave Protection vs Fireworks Gating
        is_ballistic_shockwave = (bal_max >= 0.40 and bal_max >= fw_max * 0.85)

        if not is_ballistic_shockwave:
            # Dominant fireworks
            if (fw_max > self.fw_cfg["dominant_threshold"] and
                (fw_max > self.fw_cfg["dominant_ratio"] * gun_max) and
                gun_max < self.fw_cfg["dominant_gun_max"]):
                adjusted_score = max(0.0, adjusted_score - self.fw_cfg["dominant_attenuation"])
                reasons.append("DOMINANT_FIREWORKS_SUPPRESSION")
            # Standard fireworks
            elif (fw_max > self.fw_cfg["standard_threshold"] and
                  (fw_max > self.fw_cfg["standard_ratio"] * gun_max) and
                  gun_max < self.fw_cfg["standard_gun_max"]):
                adjusted_score = max(0.0, adjusted_score - self.fw_cfg["standard_attenuation"])
                reasons.append("STANDARD_FIREWORKS_SUPPRESSION")

        # 4. Glass Shatter & High-Frequency Non-Ballistic Gating (NEW IN V4)
        if (glass_max > self.glass_cfg["threshold"] and
            high_band_ratio > self.glass_cfg["min_high_band_ratio"] and
            bal_max < self.glass_cfg["max_ballistic"]):
            adjusted_score = max(0.0, adjusted_score - self.glass_cfg["attenuation"])
            reasons.append("GLASS_SHATTER_SUPPRESSION")

        # 5. Mechanical Impact Gating
        if self.impact_cfg.get("enabled", True):
            if (impact_max > self.impact_cfg["impact_threshold"] and
                (impact_max > self.impact_cfg["impact_to_gun_ratio"] * gun_max) and
                gun_max < self.impact_cfg["gun_score_max"]):
                adjusted_score = max(0.0, adjusted_score - self.impact_cfg["attenuation"])
                reasons.append("MECHANICAL_IMPACT_SUPPRESSION")

        # 6. Environmental non-targets (Canine, Fire Crackle, Sirens)
        if dog_max > self.canine_cfg["threshold"] and dog_max > 2.0 * gun_max:
            adjusted_score = max(0.0, adjusted_score - self.canine_cfg["attenuation"])
            reasons.append("CANINE_SUPPRESSION")

        if crackle_max > self.crackle_cfg["threshold"] and crackle_max > 2.0 * gun_max:
            adjusted_score = max(0.0, adjusted_score - self.crackle_cfg["attenuation"])
            reasons.append("CRACKLE_SUPPRESSION")

        if siren_max > self.siren_cfg["threshold"] and siren_max > 2.0 * gun_max:
            adjusted_score = max(0.0, adjusted_score - self.siren_cfg["attenuation"])
            reasons.append("SIREN_SUPPRESSION")

        # Hysteresis dampening
        if is_in_confirmed_event and len(reasons) > 0:
            adjusted_score = min(adjusted_score + 0.10, raw_score)

        return {
            "adjusted_score": float(np.clip(adjusted_score, 0.0, 1.0)),
            "suppression_active": len(reasons) > 0,
            "reasons": reasons
        }


class EventStateMachineV4:
    """
    Deterministic 4-State Refractory Finite State Machine V4:
    IDLE -> CANDIDATE -> CONFIRMED -> COOLDOWN -> IDLE
    Key Fixes:
    - Candidate-bound instantaneous crest factor evaluation.
    - Duration-invariant single-round impulse promotion.
    - Native multi-shot cluster tracking.
    """

    def __init__(self, config: Dict[str, Any]):
        self.state = EventState.IDLE
        self.threshold_base = float(config.get("threshold_base", 0.62))
        self.threshold_high = float(config.get("threshold_high", 0.80))
        self.threshold_off = float(config.get("threshold_off", 0.40))
        self.confirm_windows = int(config.get("confirm_windows", 2))
        self.cooldown_secs = float(config.get("cooldown_secs", 2.0))
        self.max_hop_gap_s = float(config.get("max_hop_gap_s", 0.60))
        self.min_crest_factor_db = float(config.get("min_crest_factor_db", 7.5))
        self.single_impulse_min_crest_db = float(config.get("single_impulse_min_crest_db", 11.5))
        self.single_impulse_min_score = float(config.get("single_impulse_min_score", 0.62))
        self.allow_single_impulse_exception = bool(config.get("allow_single_impulse_exception", True))

        self.candidate_windows: List[Dict[str, Any]] = []
        self.confirmed_windows: List[Dict[str, Any]] = []
        self.cooldown_until_s = 0.0
        self.last_seen_time_s = 0.0
        self.event_counter = 0

    def reset(self) -> None:
        self.state = EventState.IDLE
        self.candidate_windows.clear()
        self.confirmed_windows.clear()
        self.cooldown_until_s = 0.0
        self.last_seen_time_s = 0.0
        self.event_counter = 0

    def process_window(
        self,
        window: Dict[str, Any],
        crest_factor_db: float,
        audio_duration_sec: float = 999.0,
        total_windows_in_stream: int = 999
    ) -> Optional[Dict[str, Any]]:
        w_start = float(window["start_time"])
        w_end = float(window["end_time"])
        w_score = float(window["score"])
        self.last_seen_time_s = w_end

        # In COOLDOWN state
        if self.state == EventState.COOLDOWN:
            if w_start >= self.cooldown_until_s:
                self.state = EventState.IDLE
            else:
                return None

        # State transitions
        if self.state == EventState.IDLE:
            if w_score >= self.threshold_base and crest_factor_db >= self.min_crest_factor_db:
                win_copy = dict(window)
                win_copy["crest_factor_db"] = crest_factor_db
                self.candidate_windows = [win_copy]
                
                # Check immediate high-confidence confirmation
                if w_score >= self.threshold_high or (self.confirm_windows == 1 and w_score >= self.threshold_base):
                    self.state = EventState.CONFIRMED
                    self.confirmed_windows = list(self.candidate_windows)
                    self.candidate_windows.clear()
                else:
                    self.state = EventState.CANDIDATE
            return None

        elif self.state == EventState.CANDIDATE:
            gap = w_start - self.candidate_windows[-1]["start_time"]
            if gap > self.max_hop_gap_s or w_score < self.threshold_off:
                # Impulse ended. Check if candidate qualifies as a single-round impulse
                if self.allow_single_impulse_exception and len(self.candidate_windows) > 0:
                    cand_peak_score = max(w["score"] for w in self.candidate_windows)
                    cand_peak_crest = max(w.get("crest_factor_db", 0.0) for w in self.candidate_windows)
                    
                    if cand_peak_score >= self.single_impulse_min_score and cand_peak_crest >= self.single_impulse_min_crest_db:
                        # Promote single impulse
                        ev = self._create_event_record(self.candidate_windows, "single_round_impulse")
                        self.candidate_windows.clear()
                        self.state = EventState.COOLDOWN
                        self.cooldown_until_s = w_start + self.cooldown_secs
                        return ev

                self.candidate_windows.clear()
                self.state = EventState.IDLE
                return None

            win_copy = dict(window)
            win_copy["crest_factor_db"] = crest_factor_db
            self.candidate_windows.append(win_copy)

            if len(self.candidate_windows) >= self.confirm_windows and w_score >= self.threshold_base:
                self.state = EventState.CONFIRMED
                self.confirmed_windows = list(self.candidate_windows)
                self.candidate_windows.clear()
            return None

        elif self.state == EventState.CONFIRMED:
            gap = w_start - self.confirmed_windows[-1]["start_time"]
            if gap > self.max_hop_gap_s or w_score < self.threshold_off:
                ev = self._create_event_record(self.confirmed_windows, "sustained_cluster")
                self.confirmed_windows.clear()
                self.state = EventState.COOLDOWN
                self.cooldown_until_s = w_start + self.cooldown_secs
                return ev

            win_copy = dict(window)
            win_copy["crest_factor_db"] = crest_factor_db
            self.confirmed_windows.append(win_copy)
            return None

        return None

    def flush(self) -> Optional[Dict[str, Any]]:
        if self.state == EventState.CONFIRMED and len(self.confirmed_windows) > 0:
            ev = self._create_event_record(self.confirmed_windows, "flush_confirmed")
            self.confirmed_windows.clear()
            self.state = EventState.IDLE
            return ev
        elif self.state == EventState.CANDIDATE and len(self.candidate_windows) > 0:
            cand_peak_score = max(w["score"] for w in self.candidate_windows)
            cand_peak_crest = max(w.get("crest_factor_db", 0.0) for w in self.candidate_windows)
            if cand_peak_score >= self.single_impulse_min_score and cand_peak_crest >= self.single_impulse_min_crest_db:
                ev = self._create_event_record(self.candidate_windows, "flush_single_impulse")
                self.candidate_windows.clear()
                self.state = EventState.IDLE
                return ev
            self.candidate_windows.clear()
            self.state = EventState.IDLE
        return None

    def _create_event_record(self, windows: List[Dict[str, Any]], trigger_type: str) -> Dict[str, Any]:
        self.event_counter += 1
        scores = [w["score"] for w in windows]
        crests = [w.get("crest_factor_db", 0.0) for w in windows]
        t_start = windows[0]["start_time"]
        t_end = windows[-1]["end_time"]
        return {
            "event_id": f"EVT_V4_{self.event_counter:04d}",
            "start_time": round(float(t_start), 3),
            "end_time": round(float(t_end), 3),
            "duration": round(float(t_end - t_start), 3),
            "peak_score": round(float(max(scores)), 4),
            "mean_score": round(float(np.mean(scores)), 4),
            "peak_crest_db": round(float(max(crests)), 2),
            "window_count": len(windows),
            "trigger_type": trigger_type
        }


class DetectorImprovementV4:
    """
    Detector Improvement V4:
    - Condition-Robust Multi-Modal Acoustic Discrimination.
    - 26-Dimensional Feature Extractor with Sub-Band Dynamics & Channel Roll-Off Estimation.
    - Calibrated Multi-Category Semantic Suppression V4 with Glass Shatter & Pyrotechnic Protection.
    - Deterministic 4-State Refractory FSM V4.
    """

    def __init__(
        self,
        config_path: str = "experiments/detector_improvement_v4/config_improvement_v4.json",
        profile: str = "balanced"
    ):
        self.config_path = config_path
        self.profile = profile

        if os.path.exists(config_path):
            with open(config_path, "r", encoding="utf-8") as f:
                self.raw_config = json.load(f)
        else:
            self.raw_config = {}

        profiles = self.raw_config.get("profiles", {})
        self.cfg = profiles.get(profile, {})

        # Load base ensemble classifiers
        bundle_dir = pathlib.Path("models/gunshot_yamnet_bundle")
        if not bundle_dir.exists():
            bundle_dir = pathlib.Path(__file__).resolve().parents[2] / "models" / "gunshot_yamnet_bundle"

        self.mlp = tf.keras.models.load_model(str(bundle_dir / "classifier_head.keras"))
        self.cb = joblib.load(str(bundle_dir / "catboost_model.joblib"))
        self.lgb = joblib.load(str(bundle_dir / "lightgbm_model.joblib"))
        self.xgb = joblib.load(str(bundle_dir / "xgboost_model.joblib"))

        # Load YAMNet feature extractor
        from feature_extractor import YAMNetFeatureExtractor
        self.feature_extractor = YAMNetFeatureExtractor()
        self.yamnet_model = self.feature_extractor.model

        # Load V4 fusion model
        fusion_path = pathlib.Path(__file__).parent / "fusion_model.joblib"
        if not fusion_path.exists():
            fusion_path = pathlib.Path(__file__).resolve().parents[2] / "experiments" / "detector_improvement_v4" / "fusion_model.joblib"
        self.fusion_model = joblib.load(str(fusion_path))

        # Initialize Suppression & FSM V4
        supp_cfg = self.cfg.get("suppression", {})
        self.suppression = CalibratedAcousticSuppressionV4(supp_cfg)
        self.fsm = EventStateMachineV4(self.cfg)

    def extract_features(self, y_win: np.ndarray) -> Tuple[np.ndarray, np.ndarray, Tuple]:
        acoustics = compute_physical_acoustic_features_v4(y_win)
        crest_db, flatness, hi, mid, lo, m2l, rolloff, cent = acoustics

        wave_tensor = tf.convert_to_tensor(y_win, dtype=tf.float32)
        yamnet_out = self.yamnet_model(wave_tensor)
        scores_t, embs_t = yamnet_out[0], yamnet_out[1]
        emb = embs_t.numpy()
        ys = scores_t.numpy()[0]

        p_mlp = float(self.mlp.predict(emb, verbose=0).flatten()[0])
        p_cb = float(self.cb.predict_proba(emb)[:, 1][0])
        p_lgb = float(self.lgb.predict_proba(emb)[:, 1][0])
        p_xgb = float(self.xgb.predict_proba(emb)[:, 1][0])

        m_mean = (p_mlp + p_cb + p_lgb + p_xgb) / 4.0
        m_max = max(p_mlp, p_cb, p_lgb, p_xgb)
        m_min = min(p_mlp, p_cb, p_lgb, p_xgb)
        m_std = float(np.std([p_mlp, p_cb, p_lgb, p_xgb]))
        sorted_m = sorted([p_mlp, p_cb, p_lgb, p_xgb], reverse=True)
        top2 = (sorted_m[0] + sorted_m[1]) / 2.0

        gun_s = max(float(ys[cls]) for cls in GUN_CLASSES)
        bal_s = max(float(ys[cls]) for cls in BALLISTIC_CLASSES)
        fw_s = max(float(ys[cls]) for cls in FIREWORKS_CLASSES)
        thun_s = max(float(ys[cls]) for cls in THUNDER_CLASSES)
        imp_s = max(float(ys[cls]) for cls in IMPACT_CLASSES)
        glass_s = max(float(ys[cls]) for cls in GLASS_CLASSES)
        nt_s = max(float(ys[cls]) for cls in NON_TARGET_SEMANTIC_CLASSES)

        feat = [
            p_mlp, p_cb, p_lgb, p_xgb,
            m_mean, m_max, m_min, m_std, top2,
            gun_s, bal_s, fw_s, thun_s, imp_s, glass_s, nt_s,
            (bal_s + 1e-4) / (fw_s + 1e-4),
            (bal_s + 1e-4) / (imp_s + 1e-4),
            crest_db, flatness, hi, mid, lo, m2l, rolloff, cent
        ]
        return np.array(feat, dtype=np.float32), ys, acoustics

    def evaluate_waveform(self, y: np.ndarray, sr: int = 16000) -> Dict[str, Any]:
        if y.ndim > 1:
            y = np.mean(y, axis=1)
        if sr != 16000:
            import librosa
            y = librosa.resample(y, orig_sr=sr, target_sr=16000)
        y = y.astype(np.float32)

        duration_sec = float(len(y)) / 16000.0
        win_size = 15360  # 0.96s
        hop_size = 7680   # 0.48s

        if len(y) < win_size:
            y_proc = np.pad(y, (0, win_size - len(y)))
            n_wins = 1
        else:
            y_proc = y
            n_wins = 1 + int((len(y) - win_size) // hop_size)

        self.fsm.reset()
        window_records = []
        events = []

        for w in range(n_wins):
            st = w * hop_size
            en = st + win_size
            y_win = y_proc[st:en]

            feat, ys, acoustics = self.extract_features(y_win)
            raw_score = float(self.fusion_model.predict_proba(feat.reshape(1, -1))[:, 1][0])

            supp_res = self.suppression.apply_suppression(
                raw_score=raw_score,
                yamnet_scores=ys,
                high_band_ratio=acoustics[2],
                is_in_confirmed_event=(self.fsm.state == EventState.CONFIRMED)
            )
            adj_score = supp_res["adjusted_score"]

            win_record = {
                "start_time": w * 0.48,
                "end_time": w * 0.48 + 0.96,
                "score": adj_score,
                "raw_score": raw_score,
                "crest_factor_db": acoustics[0],
                "suppression_active": supp_res["suppression_active"],
                "suppression_reasons": supp_res["reasons"]
            }
            window_records.append(win_record)

            ev = self.fsm.process_window(
                window=win_record,
                crest_factor_db=acoustics[0],
                audio_duration_sec=duration_sec,
                total_windows_in_stream=n_wins
            )
            if ev is not None:
                events.append(ev)

        flush_ev = self.fsm.flush()
        if flush_ev is not None:
            events.append(flush_ev)

        peak_score = float(max((w["score"] for w in window_records), default=0.0))
        peak_crest = float(max((w["crest_factor_db"] for w in window_records), default=0.0))

        return {
            "detected": len(events) > 0,
            "event_count": len(events),
            "events": events,
            "peak_score": round(peak_score, 4),
            "peak_crest_db": round(peak_crest, 2),
            "window_count": len(window_records),
            "duration_sec": round(duration_sec, 3),
            "profile": self.profile
        }

    def evaluate_file(self, filepath: Union[str, pathlib.Path]) -> Dict[str, Any]:
        y, sr = sf.read(str(filepath))
        return self.evaluate_waveform(y, sr=sr)


class RealTimeStreamDetectorImprovementV4:
    """
    Circular-buffer real-time streaming detector V4 for continuous audio feeds.
    Processing budget: <14ms per 480ms hop.
    """

    def __init__(
        self,
        config_path: str = "experiments/detector_improvement_v4/config_improvement_v4.json",
        profile: str = "balanced"
    ):
        self.detector = DetectorImprovementV4(config_path=config_path, profile=profile)
        self.buffer = np.zeros(15360, dtype=np.float32)
        self.hop_size = 7680
        self.window_index = 0

    def reset_stream(self) -> None:
        self.buffer.fill(0.0)
        self.detector.fsm.reset()
        self.window_index = 0

    def push_hop(self, hop_samples: np.ndarray) -> Optional[Dict[str, Any]]:
        if len(hop_samples) != self.hop_size:
            raise ValueError(f"Expected exactly {self.hop_size} samples (480ms), got {len(hop_samples)}")

        # Shift circular buffer
        self.buffer[:self.hop_size] = self.buffer[self.hop_size:]
        self.buffer[self.hop_size:] = hop_samples.astype(np.float32)

        feat, ys, acoustics = self.detector.extract_features(self.buffer)
        raw_score = float(self.detector.fusion_model.predict_proba(feat.reshape(1, -1))[:, 1][0])

        supp_res = self.detector.suppression.apply_suppression(
            raw_score=raw_score,
            yamnet_scores=ys,
            high_band_ratio=acoustics[2],
            is_in_confirmed_event=(self.detector.fsm.state == EventState.CONFIRMED)
        )
        adj_score = supp_res["adjusted_score"]

        win_record = {
            "start_time": self.window_index * 0.48,
            "end_time": self.window_index * 0.48 + 0.96,
            "score": adj_score,
            "raw_score": raw_score,
            "crest_factor_db": acoustics[0],
            "suppression_active": supp_res["suppression_active"],
            "suppression_reasons": supp_res["reasons"]
        }
        self.window_index += 1

        ev = self.detector.fsm.process_window(
            window=win_record,
            crest_factor_db=acoustics[0],
            audio_duration_sec=999999.0,
            total_windows_in_stream=999999
        )
        return ev
