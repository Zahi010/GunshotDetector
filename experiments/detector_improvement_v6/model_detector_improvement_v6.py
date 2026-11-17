"""
Detector Improvement V6: Urban Transient Discrimination & Condition-Adaptive Architecture
RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.

Key Improvements in V6:
1. Online Condition Estimator Anti-Chatter Stabilization:
   - Eliminates single-window rumble mode bouncing.
   - Enforces 3-window occluded / 2-window clear / 2-window rumble hysteresis with opposing counter reset.
2. Zero-Energy Digital Silence Gating:
   - Eliminates false alarms on zero-padded file tails (which previously scored 0.9853 in unconstrained tree leaves).
3. Ballistic Coherence & Sub-Bass Thud Discrimination:
   - Discriminates automotive backfires, engine thuds, and mechanical pops via pure firearm vs. cap gun separation.
4. Preserved Condition-Adaptive Confirmation FSM:
   - Dynamically adapts confirmation barriers according to acoustic channel state.
"""

import os
import sys
import json
import enum
import pathlib
import collections
from typing import Dict, List, Tuple, Any, Optional

import numpy as np
import soundfile as sf
import librosa
import joblib

# ------------------------------------------------------------------------------
# AudioSet / YAMNet Semantic Class Mappings
# ------------------------------------------------------------------------------
PURE_GUN_CLASSES = [421, 422, 425]                  # Gunshot/gunfire, Machine gun, Fusillade
CAP_GUN_CLASS = 424                                 # Cap gun (mechanical pop / toy)
GUN_CLASSES = [421, 422, 424, 425]                  # Composite gunshot classes
BALLISTIC_CLASSES = [420, 421, 422, 424, 425, 428, 434, 460]  # Explosion, Artillery, Crack, Blast
FIREWORKS_CLASSES = [426, 427]                      # Fireworks, Firecracker
THUNDER_CLASSES = [280, 281]                        # Thunder, Thunderstorm
IMPACT_CLASSES = [413, 414, 352, 353, 58]           # Slap/smack, Smash/crash, Hammer, Knock
GLASS_CLASSES = [433, 435, 436]                     # Glass, Shatter, Sharp crack
SIREN_CLASSES = [390, 391]                          # Siren, Emergency vehicle
DOG_CLASSES = [67, 68]                              # Dog, Bark
CRACKLE_CLASSES = [429, 430]                        # Boom, Pop
NON_TARGET_SEMANTIC_CLASSES = (
    [0] + list(range(67, 118)) + list(range(300, 331)) + [502, 503, 504]
)

class OperatingMode(enum.Enum):
    CLEAR_NORMAL = "CLEAR_NORMAL"
    DEGRADED_OCCLUDED = "DEGRADED_OCCLUDED"
    UNKNOWN = "UNKNOWN"

class EventState(enum.Enum):
    IDLE = "IDLE"
    CANDIDATE = "CANDIDATE"
    CONFIRMED = "CONFIRMED"
    REFRACTORY = "REFRACTORY"


def compute_physical_acoustic_features_v6(
    window: np.ndarray, sr: int = 16000
) -> Tuple[float, float, float, float, float, float, float, float, float, float]:
    """
    Computes 10 physical DSP acoustic metrics for an analysis window:
    (crest_db, flatness, high_ratio, mid_ratio, low_ratio, mid_to_low, channel_rolloff, centroid_hz, rms, peak)
    """
    if len(window) == 0:
        return 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0

    peak = float(np.max(np.abs(window)))
    rms = float(np.sqrt(np.mean(window ** 2)))

    # Silence safeguard
    if rms < 1e-6 or peak < 1e-5:
        return 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, rms, peak

    crest_db = float(20.0 * np.log10((peak + 1e-6) / (rms + 1e-6)))

    fft_mag = np.abs(np.fft.rfft(window * np.hanning(len(window))))
    freqs = np.fft.rfftfreq(len(window), d=1.0 / sr)
    total_power = float(np.sum(fft_mag ** 2)) + 1e-9

    low_power = float(np.sum(fft_mag[freqs < 500] ** 2))
    mid_power = float(np.sum(fft_mag[(freqs >= 500) & (freqs < 2500)] ** 2))
    high_power = float(np.sum(fft_mag[freqs >= 2500] ** 2))

    low_ratio = low_power / total_power
    mid_ratio = mid_power / total_power
    high_ratio = high_power / total_power

    mid_to_low = (mid_ratio + 1e-4) / (low_ratio + 1e-4)
    channel_rolloff = (high_ratio + 1e-4) / (mid_ratio + 1e-4)

    # Wiener Spectral Flatness
    p_spec = fft_mag ** 2 + 1e-12
    geom_mean = np.exp(np.mean(np.log(p_spec)))
    arith_mean = np.mean(p_spec)
    flatness = float(geom_mean / (arith_mean + 1e-9))

    centroid = float(np.sum(freqs * fft_mag) / (np.sum(fft_mag) + 1e-9))

    return (
        crest_db,
        flatness,
        high_ratio,
        mid_ratio,
        low_ratio,
        mid_to_low,
        channel_rolloff,
        centroid,
        rms,
        peak
    )


class ConditionEstimatorV6:
    """
    Stabilized Online Acoustic Condition Estimator V6.
    Fixes V5 oscillation bug:
    - Enforces 3-window occluded / 2-window clear / 2-window rumble hysteresis.
    - Resets opposing counters upon committed state transition.
    - Prevents single-window rumble from immediately bouncing the detector between modes.
    """

    def __init__(
        self,
        alpha: float = 0.20,
        hysteresis_occluded: int = 3,
        hysteresis_clear: int = 2,
        hysteresis_rumble: int = 2
    ):
        self.alpha = float(alpha)
        self.hysteresis_occluded = int(hysteresis_occluded)
        self.hysteresis_clear = int(hysteresis_clear)
        self.hysteresis_rumble = int(hysteresis_rumble)

        self.current_mode = OperatingMode.UNKNOWN
        self.ema_rolloff: Optional[float] = None
        self.ema_high: Optional[float] = None
        self.ema_mid: Optional[float] = None
        self.ema_low: Optional[float] = None
        self.ema_m2l: Optional[float] = None

        self.consecutive_occluded = 0
        self.consecutive_clear = 0
        self.consecutive_rumble = 0

        self.transition_log: List[Dict[str, Any]] = []

    def reset(self):
        self.current_mode = OperatingMode.UNKNOWN
        self.ema_rolloff = None
        self.ema_high = None
        self.ema_mid = None
        self.ema_low = None
        self.ema_m2l = None
        self.consecutive_occluded = 0
        self.consecutive_clear = 0
        self.consecutive_rumble = 0
        self.transition_log = []

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
        Updates EMA state metrics and applies anti-chatter hysteresis transitions.
        """
        if self.ema_rolloff is None:
            self.ema_rolloff = float(rolloff)
            self.ema_high = float(high_ratio)
            self.ema_mid = float(mid_ratio)
            self.ema_low = float(low_ratio)
            self.ema_m2l = float(mid_to_low)
        else:
            self.ema_rolloff = self.alpha * rolloff + (1.0 - self.alpha) * self.ema_rolloff
            self.ema_high = self.alpha * high_ratio + (1.0 - self.alpha) * self.ema_high
            self.ema_mid = self.alpha * mid_ratio + (1.0 - self.alpha) * self.ema_mid
            self.ema_low = self.alpha * low_ratio + (1.0 - self.alpha) * self.ema_low
            self.ema_m2l = self.alpha * mid_to_low + (1.0 - self.alpha) * self.ema_m2l

        # Evidence criteria
        is_occluded_candidate = (
            (self.ema_rolloff < 0.14 and rolloff < 0.16) and
            (self.ema_high < 0.055 and high_ratio < 0.065) and
            (self.ema_mid >= 0.35 or mid_ratio >= 0.35) and
            (low_ratio < 0.70)
        )

        is_clear_candidate = (
            (self.ema_rolloff >= 0.20 or rolloff >= 0.22) and
            (self.ema_high >= 0.075 or high_ratio >= 0.080) and
            (low_ratio < 0.70)
        )

        is_rumble_candidate = (
            (self.ema_low >= 0.70 or low_ratio >= 0.75) and
            (self.ema_m2l < 0.50 or mid_to_low < 0.45)
        )

        # Update evidence counters
        if is_occluded_candidate:
            self.consecutive_occluded += 1
            self.consecutive_clear = 0
            self.consecutive_rumble = 0
        elif is_clear_candidate:
            self.consecutive_clear += 1
            self.consecutive_occluded = 0
            self.consecutive_rumble = 0
        elif is_rumble_candidate:
            self.consecutive_rumble += 1
            self.consecutive_occluded = 0
            self.consecutive_clear = 0
        else:
            self.consecutive_occluded = max(0, self.consecutive_occluded - 1)
            self.consecutive_clear = max(0, self.consecutive_clear - 1)
            self.consecutive_rumble = max(0, self.consecutive_rumble - 1)

        old_mode = self.current_mode
        new_mode = old_mode
        reason = ""

        # State transition evaluation with strict counter resets
        if self.current_mode == OperatingMode.UNKNOWN:
            if self.consecutive_occluded >= self.hysteresis_occluded:
                new_mode = OperatingMode.DEGRADED_OCCLUDED
                reason = f"Persistent fabric occlusion (consecutive={self.consecutive_occluded}, rolloff={self.ema_rolloff:.3f}, mid={self.ema_mid:.3f})"
                self.consecutive_clear = 0
                self.consecutive_rumble = 0
            elif self.consecutive_clear >= self.hysteresis_clear:
                new_mode = OperatingMode.CLEAR_NORMAL
                reason = f"Persistent clear path (consecutive={self.consecutive_clear}, rolloff={self.ema_rolloff:.3f}, hi={self.ema_high:.3f})"
                self.consecutive_occluded = 0
                self.consecutive_rumble = 0

        elif self.current_mode == OperatingMode.CLEAR_NORMAL:
            if self.consecutive_occluded >= self.hysteresis_occluded:
                new_mode = OperatingMode.DEGRADED_OCCLUDED
                reason = f"Transition to occluded (rolloff={self.ema_rolloff:.3f}, hi={self.ema_high:.3f})"
                self.consecutive_clear = 0
                self.consecutive_rumble = 0
            elif self.consecutive_rumble >= self.hysteresis_rumble:
                new_mode = OperatingMode.UNKNOWN
                reason = f"Sustained heavy rumble (consecutive={self.consecutive_rumble}, low={self.ema_low:.3f})"
                self.consecutive_clear = 0
                self.consecutive_occluded = 0

        elif self.current_mode == OperatingMode.DEGRADED_OCCLUDED:
            if self.consecutive_clear >= (self.hysteresis_clear + 1):
                new_mode = OperatingMode.CLEAR_NORMAL
                reason = f"Transition to CLEAR (rolloff={self.ema_rolloff:.3f}, hi={self.ema_high:.3f})"
                self.consecutive_occluded = 0
                self.consecutive_rumble = 0
            elif self.consecutive_rumble >= self.hysteresis_rumble:
                new_mode = OperatingMode.UNKNOWN
                reason = f"Sustained low rumble in occluded state (low={self.ema_low:.3f})"
                self.consecutive_occluded = 0
                self.consecutive_clear = 0

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
                "reason": reason
            }
            self.transition_log.append(record)

        # Confidence metric
        if self.current_mode == OperatingMode.DEGRADED_OCCLUDED:
            conf = min(1.0, max(0.50, float(0.50 + 2.5 * (0.14 - min(self.ema_rolloff, 0.14)))))
        elif self.current_mode == OperatingMode.CLEAR_NORMAL:
            conf = min(1.0, max(0.50, float(0.50 + 1.5 * (max(self.ema_rolloff, 0.20) - 0.20))))
        else:
            conf = 0.50

        return self.current_mode, conf, did_transition


class CalibratedSemanticSuppressionV6:
    """
    Calibrated Multi-Category Semantic Suppression V6.
    Enhancements:
    1. Digital Silence & Energy Floor Gating (eliminates unconstrained zero-leaf tree explosions).
    2. Pure Gunshot vs. Cap Gun Separation.
    3. Sub-Bass Thud & Automotive Backfire Gating.
    4. Ballistic Coherence Safeguard.
    """

    def __init__(self, suppression_cfg: Dict[str, Any]):
        self.cfg = suppression_cfg

    def apply_suppression(
        self,
        raw_score: float,
        yamnet_scores: Any,
        acoustics: Tuple[float, float, float, float, float, float, float, float, float, float],
        is_in_confirmed_event: bool = False
    ) -> Dict[str, Any]:
        crest, flat, hi, mid, lo, m2l, rolloff, cent, rms, peak = acoustics

        # 1. Silence / Energy Floor Gate
        if rms < 0.001 or peak < 0.005:
            return {
                "adjusted_score": 0.0,
                "suppressed": True,
                "category": "silence_gate"
            }

        if is_in_confirmed_event:
            return {"adjusted_score": raw_score, "suppressed": False, "category": None}

        def _get_s(s_obj, c):
            if isinstance(s_obj, dict):
                return float(s_obj.get(c, 0.0))
            return float(s_obj[c]) if c < len(s_obj) else 0.0

        pure_gun = max(_get_s(yamnet_scores, cls) for cls in PURE_GUN_CLASSES)
        cap_gun = _get_s(yamnet_scores, CAP_GUN_CLASS)
        bal_s = max(_get_s(yamnet_scores, cls) for cls in BALLISTIC_CLASSES)
        fw_s = max(_get_s(yamnet_scores, cls) for cls in FIREWORKS_CLASSES)
        thun_s = max(_get_s(yamnet_scores, cls) for cls in THUNDER_CLASSES)
        imp_s = max(_get_s(yamnet_scores, cls) for cls in IMPACT_CLASSES)
        glass_s = max(_get_s(yamnet_scores, cls) for cls in GLASS_CLASSES)

        adjusted_score = float(raw_score)
        suppressed = False
        category = None

        # 2. Thunder Semantic Gating
        thun_cfg = self.cfg.get("thunder")
        if thun_cfg and thun_cfg.get("enabled", True) and not suppressed:
            is_thun_sem = (thun_s >= thun_cfg.get("threshold", 0.20))
            if is_thun_sem and pure_gun < thun_cfg.get("gun_score_max", 0.15):
                adjusted_score *= thun_cfg.get("attenuation", 0.30)
                suppressed = True
                category = "thunder_rumble"

        # 3. Glass Shatter Gating
        glass_cfg = self.cfg.get("glass_shatter")
        if glass_cfg and glass_cfg.get("enabled", True) and not suppressed:
            if glass_s >= glass_cfg.get("threshold", 0.30):
                if hi >= glass_cfg.get("min_high_band_ratio", 0.25):
                    if (glass_s > bal_s or pure_gun < glass_cfg.get("gun_score_max", 0.20)):
                        adjusted_score *= glass_cfg.get("attenuation", 0.35)
                        suppressed = True
                        category = "glass_shatter"

        # 4. Fireworks Gating (Two-tier)
        fw_cfg = self.cfg.get("fireworks")
        if fw_cfg and fw_cfg.get("enabled", True) and not suppressed:
            is_dom = (fw_s >= fw_cfg.get("dominant_threshold", 0.45) and
                      fw_s / (pure_gun + 1e-4) >= fw_cfg.get("dominant_ratio", 1.8) and
                      pure_gun < fw_cfg.get("dominant_gun_max", 0.25))
            is_std = (fw_s >= fw_cfg.get("standard_threshold", 0.30) and
                      fw_s / (pure_gun + 1e-4) >= fw_cfg.get("standard_ratio", 1.5) and
                      pure_gun < fw_cfg.get("standard_gun_max", 0.12))
            if is_dom:
                adjusted_score *= fw_cfg.get("dominant_attenuation", 0.30)
                suppressed = True
                category = "fireworks_dominant"
            elif is_std:
                adjusted_score *= fw_cfg.get("standard_attenuation", 0.35)
                suppressed = True
                category = "fireworks_standard"

        # 5. Cap Gun Mechanical Pop Gating
        cap_cfg = self.cfg.get("cap_gun_mechanical")
        if cap_cfg and cap_cfg.get("enabled", True) and not suppressed:
            if (cap_gun >= cap_cfg.get("min_cap_gun", 0.35) and
                pure_gun < cap_cfg.get("max_pure_gun", 0.28) and
                hi < cap_cfg.get("max_high_ratio", 0.010) and
                cent < cap_cfg.get("max_centroid_hz", 450.0)):
                adjusted_score *= cap_cfg.get("attenuation", 0.35)
                suppressed = True
                category = "cap_gun_mechanical_thud"

        # 6. Sub-Bass Automotive Thud & Backfire Gate
        thud_cfg = self.cfg.get("sub_bass_thud")
        if thud_cfg and thud_cfg.get("enabled", True) and not suppressed:
            if (lo >= thud_cfg.get("min_low_ratio", 0.75) and
                hi < thud_cfg.get("max_high_ratio", 0.008) and
                cent < thud_cfg.get("max_centroid_hz", 450.0) and
                pure_gun < thud_cfg.get("max_pure_gun", 0.20)):
                adjusted_score *= thud_cfg.get("attenuation", 0.35)
                suppressed = True
                category = "sub_bass_thud"

        # Fallback thunder physical rumble if thunder configured and sub-bass didn't take it
        if thun_cfg and thun_cfg.get("enabled", True) and not suppressed:
            is_thun_phys = (lo >= thun_cfg.get("low_band_threshold", 0.65) and m2l < thun_cfg.get("mid_to_low_max", 0.55))
            if is_thun_phys and pure_gun < thun_cfg.get("gun_score_max", 0.15):
                adjusted_score *= thun_cfg.get("attenuation", 0.30)
                suppressed = True
                category = "thunder_rumble"

        # 7. Mechanical Impact Gating
        imp_cfg = self.cfg.get("mechanical_impact")
        if imp_cfg and imp_cfg.get("enabled", True) and not suppressed:
            if imp_s >= imp_cfg.get("impact_threshold", 0.25):
                if imp_s / (pure_gun + 1e-4) >= imp_cfg.get("impact_to_gun_ratio", 1.5) and pure_gun < imp_cfg.get("gun_score_max", 0.20):
                    adjusted_score *= imp_cfg.get("attenuation", 0.35)
                    suppressed = True
                    category = "mechanical_impact"

        # 8. Ballistic Coherence Safeguard (applies when ballistic acoustic features are absent)
        coh_cfg = self.cfg.get("ballistic_coherence")
        if coh_cfg and coh_cfg.get("enabled", True) and not suppressed:
            if pure_gun < coh_cfg.get("max_pure_gun", 0.08) and bal_s < coh_cfg.get("max_ballistic", 0.10):
                adjusted_score *= coh_cfg.get("attenuation", 0.20)
                suppressed = True
                category = "ballistic_incoherence"

        return {
            "adjusted_score": float(adjusted_score),
            "suppressed": suppressed,
            "category": category
        }


class ConditionAdaptiveFSMV6:
    """
    Deterministic Refractory Finite State Machine V6.
    Enhancements:
    - Conservative UNKNOWN mode (0.70 threshold) prevents ambient urban clatter from triggering.
    - Sub-bass thuds without peak amplitude (hi < 0.005, cent < 450, peak < 0.15) denied single-impulse bypass.
    - Extended 1.50s refractory cooldown prevents duplicate ringing alerts.
    """

    def __init__(self, mode_policies: Dict[str, Dict[str, Any]]):
        self.mode_policies = mode_policies
        self.state = EventState.IDLE
        self.current_event: Optional[Dict[str, Any]] = None
        self.event_counter = 0

        self.candidate_scores: List[float] = []
        self.candidate_crest_dbs: List[float] = []
        self.candidate_times: List[float] = []
        self.refractory_end_time = 0.0
        self.max_hop_gap_s = 0.60

    def reset(self):
        self.state = EventState.IDLE
        self.current_event = None
        self.candidate_scores = []
        self.candidate_crest_dbs = []
        self.candidate_times = []
        self.refractory_end_time = 0.0

    def get_policy_for_mode(self, mode: OperatingMode) -> Dict[str, Any]:
        return self.mode_policies.get(mode.value, self.mode_policies["UNKNOWN"])

    def step(
        self,
        score: float,
        crest_db: float,
        time_s: float,
        acoustics: Optional[Tuple] = None,
        operating_mode: OperatingMode = OperatingMode.UNKNOWN
    ) -> Tuple[EventState, Optional[Dict[str, Any]]]:
        policy = self.get_policy_for_mode(operating_mode)
        th_base = policy.get("threshold_base", 0.70)
        th_off = policy.get("threshold_off", 0.40)
        confirm_wins = policy.get("confirm_windows", 2)
        cooldown = policy.get("cooldown_secs", 1.50)
        allow_single = policy.get("allow_single_impulse_exception", True)
        single_th = policy.get("single_impulse_min_score", 0.70)
        single_crest = policy.get("single_impulse_min_crest_db", 13.5)

        # Check sub-bass single-impulse bypass gate
        is_sub_bass_thud = False
        if acoustics is not None:
            _, _, hi, _, _, _, _, cent, _, peak = acoustics
            if hi < 0.005 and cent < 450.0 and peak < 0.15:
                is_sub_bass_thud = True

        emitted_event = None

        if self.state == EventState.REFRACTORY:
            if time_s >= self.refractory_end_time:
                self.state = EventState.IDLE
            else:
                return self.state, None

        if self.state == EventState.IDLE:
            # Single Impulse Exception
            if allow_single and score >= single_th and crest_db >= single_crest and not is_sub_bass_thud:
                self.event_counter += 1
                self.current_event = {
                    "event_id": f"EVT_V6_{self.event_counter:04d}",
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

            # Candidate Initiation
            if score >= th_base:
                self.state = EventState.CANDIDATE
                self.candidate_scores = [score]
                self.candidate_crest_dbs = [crest_db]
                self.candidate_times = [time_s]

        elif self.state == EventState.CANDIDATE:
            gap = time_s - self.candidate_times[-1]
            if gap > self.max_hop_gap_s or score < th_off:
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
                        "event_id": f"EVT_V6_{self.event_counter:04d}",
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
                self.current_event["end_time"] = time_s + 0.96
                self.current_event["duration"] = round(self.current_event["end_time"] - self.current_event["start_time"], 3)
                self.current_event["peak_score"] = max(self.current_event["peak_score"], round(score, 4))
                self.current_event["peak_crest_db"] = max(self.current_event["peak_crest_db"], round(crest_db, 2))
                self.current_event["window_count"] += 1
            else:
                self.state = EventState.REFRACTORY
                self.refractory_end_time = time_s + cooldown
                self.current_event = None
                self.candidate_scores = []
                self.candidate_crest_dbs = []
                self.candidate_times = []

        return self.state, emitted_event


class DetectorImprovementV6:
    """
    Unified Detector Improvement V6 Pipeline.
    """

    def __init__(self, config_path: Optional[str] = None):
        if config_path is None:
            config_path = str(pathlib.Path(__file__).parent / "config_improvement_v6.json")
        with open(config_path, "r") as f:
            self.config = json.load(f)

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

        fusion_path = root / "experiments" / "detector_improvement_v4" / "fusion_model.joblib"
        self.fusion_model = joblib.load(str(fusion_path))

        # Modules
        ce_cfg = self.config.get("condition_estimator", {})
        self.estimator = ConditionEstimatorV6(
            alpha=ce_cfg.get("alpha", 0.20),
            hysteresis_occluded=ce_cfg.get("hysteresis_windows_occluded", 3),
            hysteresis_clear=ce_cfg.get("hysteresis_windows_clear", 2),
            hysteresis_rumble=ce_cfg.get("hysteresis_windows_rumble", 2)
        )
        self.suppression = CalibratedSemanticSuppressionV6(self.config.get("suppression_rules", {}))
        self.fsm = ConditionAdaptiveFSMV6(self.config.get("mode_policies", {}))
        self.threshold_base = float(self.config.get("mode_policies", {}).get("CLEAR_NORMAL", {}).get("threshold_base", 0.70))

    def reset(self):
        self.estimator.reset()
        self.fsm.reset()

    def extract_features(self, window_16k: np.ndarray) -> Tuple[np.ndarray, Dict[int, float], Tuple]:
        """
        Extracts 26 multi-modal features for a 0.96s analysis window.
        """
        acoustics = compute_physical_acoustic_features_v6(window_16k, 16000)
        crest, flat, hi, mid, lo, m2l, rolloff, cent, rms, peak = acoustics

        # YAMNet inference
        import tensorflow as tf
        waveform_tensor = tf.convert_to_tensor(window_16k, dtype=tf.float32)
        scores, embeddings, _ = self.yamnet_model(waveform_tensor)
        yamnet_scores_arr = tf.reduce_mean(scores, axis=0).numpy()
        ys = {i: float(yamnet_scores_arr[i]) for i in range(len(yamnet_scores_arr))}
        emb_mean = tf.reduce_mean(embeddings, axis=0, keepdims=True).numpy()

        # Base models
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

        def _get_s(c):
            return float(yamnet_scores_arr[c]) if c < len(yamnet_scores_arr) else 0.0

        gun_s = max(_get_s(cls) for cls in GUN_CLASSES)
        bal_s = max(_get_s(cls) for cls in BALLISTIC_CLASSES)
        fw_s = max(_get_s(cls) for cls in FIREWORKS_CLASSES)
        thun_s = max(_get_s(cls) for cls in THUNDER_CLASSES)
        imp_s = max(_get_s(cls) for cls in IMPACT_CLASSES)
        glass_s = max(_get_s(cls) for cls in GLASS_CLASSES)
        nt_s = max(_get_s(cls) for cls in NON_TARGET_SEMANTIC_CLASSES)

        feat = [
            p_mlp, p_cb, p_lgb, p_xgb,
            m_mean, m_max, m_min, m_std, top2,
            gun_s, bal_s, fw_s, thun_s, imp_s, glass_s, nt_s,
            (bal_s + 1e-4) / (fw_s + 1e-4),
            (bal_s + 1e-4) / (imp_s + 1e-4),
            crest, flat, hi, mid, lo, m2l, rolloff, cent
        ]
        return np.array(feat, dtype=np.float32), ys, acoustics

    def evaluate_waveform(self, waveform: np.ndarray, sr: int = 16000) -> Dict[str, Any]:
        """
        Evaluates an entire audio waveform using streaming windows.
        """
        if waveform.ndim > 1: waveform = np.mean(waveform, axis=1)
        if sr != 16000: waveform = librosa.resample(waveform, orig_sr=sr, target_sr=16000)
        waveform = waveform.astype(np.float32)

        dur = float(len(waveform)) / 16000.0
        win_size = 15360
        hop_size = 7680

        if len(waveform) < win_size:
            y_proc = np.pad(waveform, (0, win_size - len(waveform)))
            n_wins = 1
        else:
            y_proc = waveform
            n_wins = 1 + int((len(waveform) - win_size) // hop_size)

        self.reset()
        events = []
        scores = []
        modes = []

        for w in range(n_wins):
            st = w * hop_size
            en = st + win_size
            win = y_proc[st:en]

            feat, ys, acoustics = self.extract_features(win)
            crest, flat, hi, mid, lo, m2l, rolloff, cent, rms, peak = acoustics

            # Update condition estimator
            mode, conf, _ = self.estimator.update(rolloff, hi, mid, lo, m2l, w * 0.48, w)
            modes.append(mode.value)

            raw_score = float(self.fusion_model.predict_proba(feat.reshape(1, -1))[:, 1][0])

            # Apply semantic suppression
            is_confirmed = (self.fsm.state == EventState.CONFIRMED)
            supp = self.suppression.apply_suppression(raw_score, ys, acoustics, is_confirmed)
            adj_score = supp["adjusted_score"]
            scores.append(adj_score)

            # Step FSM
            _, ev = self.fsm.step(adj_score, crest, w * 0.48, acoustics, mode)
            if ev is not None:
                events.append(ev)

        dom_mode = max(set(modes), key=modes.count) if modes else "UNKNOWN"
        return {
            "detected": len(events) > 0,
            "events": events,
            "event_count": len(events),
            "peak_score": float(np.max(scores)) if scores else 0.0,
            "dominant_mode": dom_mode,
            "mode_transitions": len(self.estimator.transition_log),
            "duration_sec": dur
        }
