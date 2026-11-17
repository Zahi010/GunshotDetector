"""
Detector Improvement V5: Condition-Adaptive Gunshot Detection Architecture

MANDATORY SAFETY DESIGNATION:
RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.
This software is an uncertified research prototype. Never deploy for autonomous
emergency dispatch, police tactical response, active-shooter alerting, automated
evacuation, building lockdown, or life-critical physical security. Use lawfully
obtained recordings and safe audio playback only. Live-fire and hazardous acoustic
experiments are strictly prohibited.
"""

import os
import sys
import json
import enum
import time
import pathlib
from typing import Dict, List, Any, Optional, Tuple

import numpy as np
import joblib

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


def compute_physical_acoustic_features_v5(y_win: np.ndarray, sr: int = 16000) -> Tuple[float, float, float, float, float, float, float, float]:
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

    # Fast power spectrum via real FFT
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
    channel_rolloff = float((high_ratio + 1e-4) / (mid_ratio + 1e-4))
    centroid_hz = float(np.sum(freqs * P) / tot_e)

    return (
        crest_db,
        flatness,
        high_ratio,
        mid_ratio,
        low_ratio,
        mid_to_low,
        channel_rolloff,
        centroid_hz
    )


class OperatingMode(enum.Enum):
    CLEAR_NORMAL = "CLEAR_NORMAL"
    DEGRADED_OCCLUDED = "DEGRADED_OCCLUDED"
    UNKNOWN = "UNKNOWN"


class ConditionEstimatorV5:
    """
    Estimates recording condition and maintains persistent smoothed metrics
    with hysteresis to prevent single-window mode switching.
    """
    def __init__(self, alpha: float = 0.25, hysteresis_windows: int = 2):
        self.alpha = alpha
        self.hysteresis_windows = hysteresis_windows
        self.reset()

    def reset(self):
        self.current_mode = OperatingMode.UNKNOWN
        self.ema_rolloff: Optional[float] = None
        self.ema_high: Optional[float] = None
        self.ema_mid: Optional[float] = None
        self.ema_low: Optional[float] = None
        self.ema_m2l: Optional[float] = None
        self.consecutive_occluded_evidence = 0
        self.consecutive_clear_evidence = 0
        self.transition_log: List[Dict[str, Any]] = []

    def update(
        self,
        rolloff: float,
        high_ratio: float,
        mid_ratio: float,
        low_ratio: float,
        mid_to_low: float,
        time_s: float = 0.0,
        window_idx: int = 0
    ) -> Tuple[OperatingMode, float, bool]:
        """
        Updates EMA condition metrics and evaluates mode transition.
        Returns: (current_mode, confidence_score, did_transition)
        """
        if self.ema_rolloff is None:
            self.ema_rolloff = rolloff
            self.ema_high = high_ratio
            self.ema_mid = mid_ratio
            self.ema_low = low_ratio
            self.ema_m2l = mid_to_low
        else:
            self.ema_rolloff = self.alpha * rolloff + (1.0 - self.alpha) * self.ema_rolloff
            self.ema_high = self.alpha * high_ratio + (1.0 - self.alpha) * self.ema_high
            self.ema_mid = self.alpha * mid_ratio + (1.0 - self.alpha) * self.ema_mid
            self.ema_low = self.alpha * low_ratio + (1.0 - self.alpha) * self.ema_low
            self.ema_m2l = self.alpha * mid_to_low + (1.0 - self.alpha) * self.ema_m2l

        # Evidence evaluation
        is_occluded_candidate = (
            (self.ema_rolloff < 0.18 or rolloff < 0.16) and
            (self.ema_high < 0.075 or high_ratio < 0.070) and
            (mid_ratio >= 0.38 or self.ema_mid >= 0.38) and
            (mid_to_low >= 0.85 or self.ema_m2l >= 0.85) and
            (low_ratio < 0.65)  # Must not be dominant low rumble like thunder
        )

        is_clear_candidate = (
            (self.ema_rolloff >= 0.22 or rolloff >= 0.25) and
            (self.ema_high >= 0.080 or high_ratio >= 0.090) and
            (low_ratio < 0.70)
        )

        is_heavy_low_rumble = (low_ratio >= 0.65 or mid_to_low < 0.60)

        # Update hysteresis counters
        if is_occluded_candidate:
            self.consecutive_occluded_evidence += 1
            self.consecutive_clear_evidence = 0
        elif is_clear_candidate:
            self.consecutive_clear_evidence += 1
            self.consecutive_occluded_evidence = 0
        else:
            self.consecutive_occluded_evidence = max(0, self.consecutive_occluded_evidence - 1)
            self.consecutive_clear_evidence = max(0, self.consecutive_clear_evidence - 1)

        old_mode = self.current_mode
        new_mode = old_mode
        transition_reason = ""

        # State transition logic with hysteresis
        if self.current_mode == OperatingMode.UNKNOWN:
            if self.consecutive_occluded_evidence >= self.hysteresis_windows:
                new_mode = OperatingMode.DEGRADED_OCCLUDED
                transition_reason = f"Persistent occluded evidence (consecutive={self.consecutive_occluded_evidence}, rolloff={self.ema_rolloff:.3f}, mid={self.ema_mid:.3f})"
            elif self.consecutive_clear_evidence >= self.hysteresis_windows:
                new_mode = OperatingMode.CLEAR_NORMAL
                transition_reason = f"Persistent clear evidence (consecutive={self.consecutive_clear_evidence}, rolloff={self.ema_rolloff:.3f}, hi={self.ema_high:.3f})"
        elif self.current_mode == OperatingMode.CLEAR_NORMAL:
            if self.consecutive_occluded_evidence >= self.hysteresis_windows:
                new_mode = OperatingMode.DEGRADED_OCCLUDED
                transition_reason = f"Transition to occluded (rolloff={self.ema_rolloff:.3f} < 0.18, mid={self.ema_mid:.3f} >= 0.38)"
            elif is_heavy_low_rumble and self.consecutive_clear_evidence == 0:
                new_mode = OperatingMode.UNKNOWN
                transition_reason = f"Transition to UNKNOWN due to heavy low-frequency rumble (low={low_ratio:.3f}, m2l={mid_to_low:.3f})"
        elif self.current_mode == OperatingMode.DEGRADED_OCCLUDED:
            # Need 3 windows of clear evidence to leave occluded mode
            if self.consecutive_clear_evidence >= (self.hysteresis_windows + 1):
                new_mode = OperatingMode.CLEAR_NORMAL
                transition_reason = f"Transition to CLEAR (rolloff={self.ema_rolloff:.3f} >= 0.22, hi={self.ema_high:.3f} >= 0.08)"
            elif is_heavy_low_rumble:
                new_mode = OperatingMode.UNKNOWN
                transition_reason = f"Transition to UNKNOWN due to low-frequency dominance (low={low_ratio:.3f})"

        did_transition = (new_mode != old_mode)
        if did_transition:
            self.current_mode = new_mode
            record = {
                "window_idx": window_idx,
                "timestamp_s": round(time_s, 3),
                "from_mode": old_mode.value,
                "to_mode": new_mode.value,
                "ema_rolloff": round(float(self.ema_rolloff), 4),
                "ema_high": round(float(self.ema_high), 4),
                "ema_mid": round(float(self.ema_mid), 4),
                "ema_low": round(float(self.ema_low), 4),
                "ema_m2l": round(float(self.ema_m2l), 4),
                "reason": transition_reason
            }
            self.transition_log.append(record)

        # Confidence calculation
        if self.current_mode == OperatingMode.DEGRADED_OCCLUDED:
            conf = min(1.0, max(0.50, float(0.50 + 2.5 * (0.18 - min(self.ema_rolloff, 0.18)))))
        elif self.current_mode == OperatingMode.CLEAR_NORMAL:
            conf = min(1.0, max(0.50, float(0.50 + 1.5 * (max(self.ema_rolloff, 0.22) - 0.22))))
        else:
            conf = 0.50

        return self.current_mode, conf, did_transition


class EventState(enum.Enum):
    IDLE = "IDLE"
    CANDIDATE = "CANDIDATE"
    CONFIRMED = "CONFIRMED"
    REFRACTORY = "REFRACTORY"


class ConditionAdaptiveFSMV5:
    """
    Deterministic 4-State Refractory FSM with condition-adaptive thresholding,
    safeguards against rapid mode changes, and candidate-bound crest attribution.
    """
    def __init__(self, mode_policies: Dict[str, Any], max_hop_gap_s: float = 0.60):
        self.mode_policies = mode_policies
        self.max_hop_gap_s = max_hop_gap_s
        self.reset()

    def reset(self):
        self.state = EventState.IDLE
        self.candidate_scores: List[float] = []
        self.candidate_crest_dbs: List[float] = []
        self.candidate_times: List[float] = []
        self.current_event: Optional[Dict[str, Any]] = None
        self.refractory_end_time = -1.0
        self.event_counter = 0

    def get_policy_for_mode(self, mode: OperatingMode) -> Dict[str, Any]:
        mode_key = mode.value
        return self.mode_policies.get(mode_key, self.mode_policies.get("UNKNOWN", {}))

    def step(
        self,
        score: float,
        crest_db: float,
        time_s: float,
        operating_mode: OperatingMode = OperatingMode.UNKNOWN
    ) -> Tuple[EventState, Optional[Dict[str, Any]]]:
        """
        Executes one FSM step under the current condition-adaptive policy.
        """
        policy = self.get_policy_for_mode(operating_mode)
        th_base = policy.get("threshold_base", 0.68)
        th_high = policy.get("threshold_high", 0.83)
        th_off = policy.get("threshold_off", 0.42)
        confirm_wins = policy.get("confirm_windows", 2)
        cooldown = policy.get("cooldown_secs", 2.0)
        allow_single = policy.get("allow_single_impulse_exception", True)
        single_th = policy.get("single_impulse_min_score", 0.68)
        single_crest = policy.get("single_impulse_min_crest_db", 13.0)

        emitted_event = None

        # Check refractory timeout
        if self.state == EventState.REFRACTORY:
            if time_s >= self.refractory_end_time:
                self.state = EventState.IDLE
            else:
                return self.state, None

        if self.state == EventState.IDLE:
            # Condition-adaptive Single Impulse Promotion
            if allow_single and score >= single_th and crest_db >= single_crest:
                self.event_counter += 1
                self.current_event = {
                    "event_id": f"EVT_V5_{self.event_counter:04d}",
                    "start_time": time_s,
                    "end_time": time_s + 0.96,
                    "duration": 0.96,
                    "peak_score": round(score, 4),
                    "mean_score": round(score, 4),
                    "peak_crest_db": round(crest_db, 2),
                    "window_count": 1,
                    "operating_mode": operating_mode.value,
                    "trigger_type": "single_impulse_exception"
                }
                self.state = EventState.CONFIRMED
                emitted_event = dict(self.current_event)
                return self.state, emitted_event

            # Multi-window Candidate Start
            if score >= th_base:
                self.state = EventState.CANDIDATE
                self.candidate_scores = [score]
                self.candidate_crest_dbs = [crest_db]
                self.candidate_times = [time_s]

        elif self.state == EventState.CANDIDATE:
            gap = time_s - self.candidate_times[-1]
            if gap > self.max_hop_gap_s or score < th_off:
                # Candidate expired or dropped below cutoff
                self.state = EventState.IDLE
                self.candidate_scores = []
                self.candidate_crest_dbs = []
                self.candidate_times = []
            elif score >= th_base:
                self.candidate_scores.append(score)
                self.candidate_crest_dbs.append(crest_db)
                self.candidate_times.append(time_s)

                if len(self.candidate_scores) >= confirm_wins:
                    self.event_counter += 1
                    self.current_event = {
                        "event_id": f"EVT_V5_{self.event_counter:04d}",
                        "start_time": self.candidate_times[0],
                        "end_time": self.candidate_times[-1] + 0.96,
                        "duration": round((self.candidate_times[-1] + 0.96) - self.candidate_times[0], 3),
                        "peak_score": round(float(np.max(self.candidate_scores)), 4),
                        "mean_score": round(float(np.mean(self.candidate_scores)), 4),
                        "peak_crest_db": round(float(np.max(self.candidate_crest_dbs)), 2),
                        "window_count": len(self.candidate_scores),
                        "operating_mode": operating_mode.value,
                        "trigger_type": "sustained_cluster"
                    }
                    self.state = EventState.CONFIRMED
                    emitted_event = dict(self.current_event)

        elif self.state == EventState.CONFIRMED:
            if score >= th_off:
                # Event continues
                self.current_event["end_time"] = time_s + 0.96
                self.current_event["duration"] = round(self.current_event["end_time"] - self.current_event["start_time"], 3)
                self.current_event["peak_score"] = max(self.current_event["peak_score"], round(score, 4))
                self.current_event["peak_crest_db"] = max(self.current_event["peak_crest_db"], round(crest_db, 2))
                self.current_event["window_count"] += 1
            else:
                # Event finished; enter refractory cooldown
                self.state = EventState.REFRACTORY
                self.refractory_end_time = time_s + cooldown
                self.current_event = None
                self.candidate_scores = []
                self.candidate_crest_dbs = []
                self.candidate_times = []

        return self.state, emitted_event


class CalibratedSemanticSuppressionV5:
    """
    Calibrated Multi-Category Semantic Suppression V5 with enhanced
    glass-shatter discrimination, thunder/low-rumble gating, and ballistic protection.
    """
    def __init__(self, suppression_cfg: Dict[str, Any]):
        self.suppression_cfg = suppression_cfg

    def apply_suppression(
        self,
        raw_score: float,
        yamnet_scores: Dict[int, float],
        high_band_ratio: float,
        low_band_ratio: float,
        mid_to_low: float,
        is_in_confirmed_event: bool = False
    ) -> Dict[str, Any]:
        """
        Applies semantic attenuation when non-target acoustic presence is dominant.
        """
        if is_in_confirmed_event:
            return {"adjusted_score": raw_score, "suppressed": False, "category": None}

        adjusted_score = raw_score
        suppressed = False
        suppression_category = None

        def _get_s(s_obj, c):
            if isinstance(s_obj, dict):
                return float(s_obj.get(c, 0.0))
            return float(s_obj[c]) if c < len(s_obj) else 0.0

        gun_s = max(_get_s(yamnet_scores, cls) for cls in GUN_CLASSES)
        bal_s = max(_get_s(yamnet_scores, cls) for cls in BALLISTIC_CLASSES)
        fw_s = max(_get_s(yamnet_scores, cls) for cls in FIREWORKS_CLASSES)
        thun_s = max(_get_s(yamnet_scores, cls) for cls in THUNDER_CLASSES)
        imp_s = max(_get_s(yamnet_scores, cls) for cls in IMPACT_CLASSES)
        glass_s = max(_get_s(yamnet_scores, cls) for cls in GLASS_CLASSES)
        nt_s = max(_get_s(yamnet_scores, cls) for cls in NON_TARGET_SEMANTIC_CLASSES)

        # 1. Glass Shatter Suppression (Enhanced V5)
        # Fixes V4 bug: If glass_s >= 0.30 and high_band_ratio >= 0.30, verify that glass
        # dominates ballistic score or genuine gun class is low.
        glass_cfg = self.suppression_cfg.get("glass", {})
        if glass_cfg.get("enabled", True):
            if glass_s >= glass_cfg.get("threshold", 0.30):
                if high_band_ratio >= glass_cfg.get("min_high_band_ratio", 0.30):
                    if (glass_s > bal_s or gun_s < glass_cfg.get("gun_score_max", 0.20)):
                        adjusted_score *= glass_cfg.get("attenuation", 0.35)
                        suppressed = True
                        suppression_category = "glass_shatter"

        # 2. Thunder / Low-Frequency Rumble Suppression (Enhanced V5)
        thunder_cfg = self.suppression_cfg.get("thunder", {})
        if thunder_cfg.get("enabled", True) and not suppressed:
            is_thunder_semantic = (thun_s >= thunder_cfg.get("threshold", 0.20))
            is_low_rumble_physical = (
                low_band_ratio >= thunder_cfg.get("low_band_threshold", 0.65) and
                mid_to_low < thunder_cfg.get("mid_to_low_max", 0.55)
            )
            if (is_thunder_semantic or is_low_rumble_physical) and gun_s < thunder_cfg.get("gun_score_max", 0.15):
                adjusted_score *= thunder_cfg.get("attenuation", 0.30)
                suppressed = True
                suppression_category = "thunder_or_low_rumble"

        # 3. Two-Tier Fireworks Suppression (Preserved from V4)
        fw_cfg = self.suppression_cfg.get("fireworks", {})
        if fw_cfg.get("enabled", True) and not suppressed:
            is_dominant = (
                fw_s >= fw_cfg.get("dominant_threshold", 0.45) and
                fw_s / (gun_s + 1e-4) >= fw_cfg.get("dominant_ratio", 1.8) and
                gun_s < fw_cfg.get("dominant_gun_max", 0.25)
            )
            is_standard = (
                fw_s >= fw_cfg.get("standard_threshold", 0.30) and
                fw_s / (gun_s + 1e-4) >= fw_cfg.get("standard_ratio", 1.5) and
                gun_s < fw_cfg.get("standard_gun_max", 0.12)
            )
            if is_dominant:
                adjusted_score *= fw_cfg.get("dominant_attenuation", 0.30)
                suppressed = True
                suppression_category = "fireworks_dominant"
            elif is_standard:
                adjusted_score *= fw_cfg.get("standard_attenuation", 0.35)
                suppressed = True
                suppression_category = "fireworks_standard"

        # 4. Mechanical Impact Suppression
        imp_cfg = self.suppression_cfg.get("mechanical_impact", {})
        if imp_cfg.get("enabled", True) and not suppressed:
            if imp_s >= imp_cfg.get("impact_threshold", 0.25):
                if imp_s / (gun_s + 1e-4) >= imp_cfg.get("impact_to_gun_ratio", 1.5) and gun_s < imp_cfg.get("gun_score_max", 0.20):
                    adjusted_score *= imp_cfg.get("attenuation", 0.35)
                    suppressed = True
                    suppression_category = "mechanical_impact"

        # 5. Emergency Siren Suppression
        siren_cfg = self.suppression_cfg.get("siren", {})
        if siren_cfg.get("enabled", True) and not suppressed:
            siren_s = max(_get_s(yamnet_scores, cls) for cls in SIREN_CLASSES)
            if siren_s >= siren_cfg.get("threshold", 0.25) and gun_s < 0.15:
                adjusted_score *= siren_cfg.get("attenuation", 0.20)
                suppressed = True
                suppression_category = "emergency_siren"

        # 6. Canine Bark Suppression
        canine_cfg = self.suppression_cfg.get("canine", {})
        if canine_cfg.get("enabled", True) and not suppressed:
            dog_s = max(_get_s(yamnet_scores, cls) for cls in DOG_CLASSES)
            if dog_s >= canine_cfg.get("threshold", 0.30) and gun_s < 0.15:
                adjusted_score *= canine_cfg.get("attenuation", 0.25)
                suppressed = True
                suppression_category = "canine_vocalization"

        # 7. Non-Target Background Coherence Safeguard
        nt_cfg = self.suppression_cfg.get("coherence_safeguard", {})
        if nt_cfg.get("enabled", True) and not suppressed:
            if bal_s < nt_cfg.get("ballistic_max_threshold", 0.015) and nt_s >= nt_cfg.get("non_target_threshold", 0.12):
                adjusted_score *= nt_cfg.get("attenuation", 0.20)
                suppressed = True
                suppression_category = "coherence_safeguard"

        return {
            "adjusted_score": float(adjusted_score),
            "suppressed": suppressed,
            "category": suppression_category
        }


class DetectorImprovementV5:
    """
    Detector Improvement V5: Condition-Adaptive Gunshot Detector.
    Preserves V4's domain-adapted sensitivity under degraded recording conditions
    while dynamically adopting a conservative confirmation policy under clear
    open-air monitoring to reduce environmental continuous false alarms.
    """
    def __init__(self, config_path: Optional[str] = None, profile: str = "condition_adaptive"):
        if config_path is None:
            config_path = str(pathlib.Path(__file__).parent / "config_improvement_v5.json")

        with open(config_path, "r", encoding="utf-8") as f:
            self.config = json.load(f)

        self.profile_name = profile
        self.profile_cfg = self.config["profiles"].get(profile, self.config["profiles"]["condition_adaptive"])

        # Provenance components
        self.mode_policies = self.config["provenance"]["condition_adaptation"]["modes"]
        self.condition_estimator = ConditionEstimatorV5(
            alpha=self.config["provenance"]["condition_adaptation"].get("ema_alpha", 0.25),
            hysteresis_windows=self.config["provenance"]["condition_adaptation"].get("hysteresis_min_windows", 2)
        )

        mode_policies_fsm = {
            m: cfg["confirmation_policy"] for m, cfg in self.mode_policies.items()
        }

        self.fsm = ConditionAdaptiveFSMV5(
            mode_policies=mode_policies_fsm,
            max_hop_gap_s=self.profile_cfg.get("max_hop_gap_s", 0.60)
        )

        self.suppression = CalibratedSemanticSuppressionV5(
            suppression_cfg=self.config["provenance"]["semantic_suppression"]
        )

        # Load models
        self._load_models()

    def _load_models(self):
        root = pathlib.Path(__file__).resolve().parents[2]
        import tensorflow as tf
        from feature_extractor import YAMNetFeatureExtractor

        self.yamnet_fe = YAMNetFeatureExtractor()
        self.yamnet_model = self.yamnet_fe.model

        bundle_dir = root / "models" / "gunshot_yamnet_bundle"
        head_path = bundle_dir / "classifier_head.keras"
        self.classifier_head = tf.keras.models.load_model(str(head_path), compile=False)

        cb_path = bundle_dir / "catboost_model.joblib"
        self.cb_model = joblib.load(str(cb_path))

        lgb_path = bundle_dir / "lightgbm_model.joblib"
        self.lgb_model = joblib.load(str(lgb_path))

        xgb_path = bundle_dir / "xgboost_model.joblib"
        self.xgb_model = joblib.load(str(xgb_path))

        # Fusion model trained in Phase 46 with physical Butterworth LPF and dynamic saturation
        fusion_path = root / "experiments" / "detector_improvement_v4" / "fusion_model.joblib"
        self.fusion_model = joblib.load(str(fusion_path))

    def extract_features(self, y_win: np.ndarray) -> Tuple[np.ndarray, Dict[int, float], Tuple[float, ...]]:
        """
        Extracts 26 multi-modal features for a 0.96-second window.
        """
        acoustics = compute_physical_acoustic_features_v5(y_win)
        crest_db, flatness, hi, mid, lo, m2l, rolloff, cent = acoustics

        # YAMNet inference
        import tensorflow as tf
        waveform_tensor = tf.convert_to_tensor(y_win, dtype=tf.float32)
        scores, embeddings, _ = self.yamnet_model(waveform_tensor)
        ys_arr = tf.reduce_mean(scores, axis=0).numpy()
        ys = {i: float(ys_arr[i]) for i in range(len(ys_arr))}

        emb_mean = tf.reduce_mean(embeddings, axis=0, keepdims=True).numpy()

        # 4 Base models
        p_mlp = float(self.classifier_head(emb_mean, training=False).numpy()[0, 0])
        p_cb = float(self.cb_model.predict_proba(emb_mean)[0, 1])
        p_lgb = float(self.lgb_model.predict_proba(emb_mean)[0, 1])
        p_xgb = float(self.xgb_model.predict_proba(emb_mean)[0, 1])

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
        """
        Streaming-accurate offline evaluation of a full waveform.
        """
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
        self.condition_estimator.reset()
        events = []
        scores_out = []
        crests_out = []
        modes_out = []

        for w in range(n_wins):
            st = w * hop_size
            en = st + win_size
            y_win = y_proc[st:en]

            feat, ys, acoustics = self.extract_features(y_win)
            crest_db, flat, hi, mid, lo, m2l, rolloff, cent = acoustics

            # Update condition estimator
            mode, conf, _ = self.condition_estimator.update(
                rolloff=rolloff,
                high_ratio=hi,
                mid_ratio=mid,
                low_ratio=lo,
                mid_to_low=m2l,
                time_s=w * 0.48,
                window_idx=w
            )
            modes_out.append(mode.value)

            raw_score = float(self.fusion_model.predict_proba(feat.reshape(1, -1))[:, 1][0])

            # Semantic suppression V5
            supp_res = self.suppression.apply_suppression(
                raw_score=raw_score,
                yamnet_scores=ys,
                high_band_ratio=hi,
                low_band_ratio=lo,
                mid_to_low=m2l,
                is_in_confirmed_event=(self.fsm.state == EventState.CONFIRMED)
            )
            adj_score = supp_res["adjusted_score"]
            scores_out.append(adj_score)
            crests_out.append(crest_db)

            # Determine operating mode to use in FSM
            if self.profile_cfg.get("mode") == "fixed_clear":
                eval_mode = OperatingMode.CLEAR_NORMAL
            elif self.profile_cfg.get("mode") == "fixed_v4_balanced":
                eval_mode = OperatingMode.DEGRADED_OCCLUDED
            else:
                eval_mode = mode

            state, ev = self.fsm.step(
                score=adj_score,
                crest_db=crest_db,
                time_s=w * 0.48,
                operating_mode=eval_mode
            )
            if ev is not None:
                events.append(ev)

        peak_score = float(np.max(scores_out)) if scores_out else 0.0
        peak_crest = float(np.max(crests_out)) if crests_out else 0.0

        return {
            "detected": len(events) > 0,
            "event_count": len(events),
            "events": events,
            "peak_score": peak_score,
            "peak_crest_db": peak_crest,
            "window_count": n_wins,
            "duration_sec": round(duration_sec, 3),
            "profile": self.profile_name,
            "dominant_operating_mode": max(set(modes_out), key=modes_out.count) if modes_out else "UNKNOWN",
            "mode_transitions": len(self.condition_estimator.transition_log)
        }
