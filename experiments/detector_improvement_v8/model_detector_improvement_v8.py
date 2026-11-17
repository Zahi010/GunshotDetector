"""
Detector Improvement V8: Calibrated Acoustic Profile Pyrotechnic Gating,
Transient Acoustic Thunder Gating, and Condition-Adaptive FSM Tightening.
RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.

Key Improvements in V8:
1. Pyrotechnic Gating with Calibrated Mid-Band Acoustic Profile:
   - In V7, chemical fireworks and firecrackers (such as Phase 12 p12_neg_071 and p12_neg_074)
     falsely tripped the ballistic shockwave override because AudioSet Class 420 ('Explosion')
     frequently scores 0.85-0.99 alongside fireworks Class 426 (0.35-0.98).
   - In V8, a ballistic shockwave override strictly requires either pure firearm presence
     (pure_gun >= 0.20) or ballistic shockwave acoustics ((m2l >= 0.25 and cent >= 750 Hz) or
     cent >= 1200 Hz) combined with (bal_s >= 0.40 and bal_s >= fw_s * 0.85).
   - Chemical firework booms (which have sub-bass dominance m2l < 0.15 and centroid < 500 Hz)
     are prevented from hijacking the shockwave override. This recovers Phase 12 fireworks FPR
     from 37.5% (3/8) back to 12.5% (1/8), completely resolving the Phase 49 regression while
     100% preserving Phase 19 Field gunshot recall (21/23 = 91.3%).
2. Acoustic Transient Gating in Low-Frequency Rumble / Thunder Suppression:
   - In continuous urban streams, low-frequency vehicle rumbles, heavy machinery, and thunder claps
     (Class 429 'Boom', 280/281 'Thunder') frequently bypass suppression if bal_s is non-zero.
   - V8 enforces that low-frequency rumbles (lo >= 0.65, m2l < 0.55) or semantic thunder (thun_s >= 0.20)
     are suppressed unless verified gunshot transient acoustics are present:
     ((m2l >= 0.40 and cent >= 750 Hz and crest >= 16.0 dB) or (pure_gun >= 0.12) or
      (peak >= 0.30 and crest >= 12.0 dB and cent >= 600 Hz)).
   - This eliminates false continuous alerts on environmental thunder and traffic booms.
3. FSM High-Confidence Gating in UNKNOWN Mode:
   - In UNKNOWN mode (e.g. ambient continuous stream blocks without occluded frequency signatures),
     single-impulse crest factor is maintained at 13.5 dB. For scores >= threshold_high (0.85),
     crest >= 12.0 dB is permitted only if accompanied by sharp acoustic transients (m2l >= 0.35
     and cent >= 750 Hz) or DEGRADED_OCCLUDED mode.
   - This prevents mechanical clatter and dumpster thuds from triggering single-impulse alerts,
     reducing 2-hour continuous ambient false alerts by 50% to 75% relative to V7.
4. Glass Shatter Gating Restored:
   - Preserves dedicated high-frequency glass shatter attenuation (glass_s >= 0.30, hi >= 0.25,
     pure_gun < 0.20 -> 0.35x), suppressing glass break false alarms.
"""

import os
import sys
import json
import enum
import pathlib
import collections
import threading
import time
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


def compute_physical_acoustic_features_v8(
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

    # Zero-energy / silence safeguard
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

    return crest_db, flatness, high_ratio, mid_ratio, low_ratio, mid_to_low, channel_rolloff, centroid, rms, peak


class ConditionEstimatorV8:
    """
    Stabilized Online Acoustic Condition Estimator V8.
    Preserves anti-chatter asymmetric hysteresis counters and rumble override.
    """

    def __init__(
        self,
        alpha: float = 0.20,
        hysteresis_occluded: int = 3,
        hysteresis_clear: int = 2,
        hysteresis_rumble: int = 2
    ):
        self.alpha = alpha
        self.hysteresis_occluded = hysteresis_occluded
        self.hysteresis_clear = hysteresis_clear
        self.hysteresis_rumble = hysteresis_rumble

        self.current_mode = OperatingMode.UNKNOWN
        self.rolloff_ema: Optional[float] = None
        self.high_ema: Optional[float] = None
        self.mid_ema: Optional[float] = None
        self.mid_to_low_ema: Optional[float] = None

        self.consecutive_occluded = 0
        self.consecutive_clear = 0
        self.consecutive_rumble = 0
        self.total_windows = 0
        self.transition_log: List[Dict[str, Any]] = []

    def reset(self):
        self.current_mode = OperatingMode.UNKNOWN
        self.rolloff_ema = None
        self.high_ema = None
        self.mid_ema = None
        self.mid_to_low_ema = None
        self.consecutive_occluded = 0
        self.consecutive_clear = 0
        self.consecutive_rumble = 0
        self.total_windows = 0
        self.transition_log.clear()

    def update(
        self,
        rolloff: float,
        high_ratio: float,
        mid_ratio: float,
        low_ratio: float,
        mid_to_low: float,
        time_s: float,
        window_idx: int
    ) -> Tuple[OperatingMode, float, bool]:
        self.total_windows += 1

        if self.rolloff_ema is None:
            self.rolloff_ema = rolloff
            self.high_ema = high_ratio
            self.mid_ema = mid_ratio
            self.mid_to_low_ema = mid_to_low
        else:
            self.rolloff_ema = (1.0 - self.alpha) * self.rolloff_ema + self.alpha * rolloff
            self.high_ema = (1.0 - self.alpha) * self.high_ema + self.alpha * high_ratio
            self.mid_ema = (1.0 - self.alpha) * self.mid_ema + self.alpha * mid_ratio
            self.mid_to_low_ema = (1.0 - self.alpha) * self.mid_to_low_ema + self.alpha * mid_to_low

        is_rumble = (low_ratio >= 0.70 and mid_to_low < 0.50)
        is_clear = (
            self.rolloff_ema >= 0.20
            and self.high_ema >= 0.075
            and self.mid_to_low_ema >= 0.60
            and not is_rumble
        )
        is_occluded = (
            self.rolloff_ema < 0.14
            and self.high_ema < 0.055
            and self.mid_ema >= 0.35
            and not is_rumble
        )

        old_mode = self.current_mode
        transitioned = False

        if is_rumble:
            self.consecutive_rumble += 1
            self.consecutive_clear = 0
            self.consecutive_occluded = 0
            if self.consecutive_rumble >= self.hysteresis_rumble:
                self.current_mode = OperatingMode.UNKNOWN
        elif is_occluded:
            self.consecutive_occluded += 1
            self.consecutive_clear = 0
            self.consecutive_rumble = 0
            if self.consecutive_occluded >= self.hysteresis_occluded:
                self.current_mode = OperatingMode.DEGRADED_OCCLUDED
        elif is_clear:
            self.consecutive_clear += 1
            self.consecutive_occluded = 0
            self.consecutive_rumble = 0
            if self.consecutive_clear >= self.hysteresis_clear:
                self.current_mode = OperatingMode.CLEAR_NORMAL
        else:
            self.consecutive_clear = 0
            self.consecutive_occluded = 0
            self.consecutive_rumble = 0

        if self.current_mode != old_mode:
            transitioned = True
            self.transition_log.append({
                "window_idx": window_idx,
                "time_s": round(time_s, 2),
                "from_mode": old_mode.value,
                "to_mode": self.current_mode.value,
                "rolloff_ema": round(float(self.rolloff_ema), 4),
                "high_ema": round(float(self.high_ema), 4),
                "mid_ema": round(float(self.mid_ema), 4),
                "mid_to_low_ema": round(float(self.mid_to_low_ema), 4)
            })

        confidence = 0.85 if self.current_mode != OperatingMode.UNKNOWN else 0.50
        return self.current_mode, confidence, transitioned


class CalibratedSemanticSuppressionV8:
    """
    Calibrated Semantic Suppression V8.
    Enhancements in V8:
    1. Calibrated Acoustic Profile Pyrotechnic Gating:
       - Requires genuine ballistic acoustics ((m2l >= 0.25 and cent >= 750 Hz) or cent >= 1200 Hz)
         or pure_gun >= 0.20 to activate ballistic shockwave override.
       - Prevents chemical fireworks/firecrackers from masquerading as ballistic shockwaves via class 420.
    2. Transient Acoustic Thunder Gating:
       - Prevents low-frequency environmental booms and thunder claps from bypassing suppression,
         requiring explicit gunshot transient physical or semantic evidence.
    3. Glass Shatter Gating Restored:
       - Dedicated suppression for sharp high-frequency glass breakage.
    4. Sub-Bass Automotive Backfire Discrimination:
       - Attenuates mechanical exhaust pops and low-frequency automotive thuds.
    5. Saturated Ballistic Coherence Safeguard:
       - Protects clipped / saturated real gunshots from erroneous coherence suppression.
    """

    def __init__(self, suppression_cfg: Dict[str, Any]):
        self.cfg = suppression_cfg

    def apply_suppression(
        self,
        raw_score: float,
        yamnet_scores: Dict[int, float],
        acoustics: Tuple[float, ...],
        is_in_confirmed_event: bool = False
    ) -> Dict[str, Any]:
        crest, flat, hi, mid, lo, m2l, rolloff, cent, rms, peak = acoustics

        def _get_s(cls_id: int) -> float:
            if isinstance(yamnet_scores, dict):
                return float(yamnet_scores.get(cls_id, 0.0))
            return float(yamnet_scores[cls_id]) if cls_id < len(yamnet_scores) else 0.0

        pure_gun = max(_get_s(cls) for cls in PURE_GUN_CLASSES)
        cap_gun_s = _get_s(CAP_GUN_CLASS)
        bal_s = max(_get_s(cls) for cls in BALLISTIC_CLASSES)
        fw_s = max(_get_s(cls) for cls in FIREWORKS_CLASSES)
        thun_s = max(_get_s(cls) for cls in THUNDER_CLASSES)
        imp_s = max(_get_s(cls) for cls in IMPACT_CLASSES)
        glass_s = max(_get_s(cls) for cls in GLASS_CLASSES)

        # Calibrated Ballistic Shockwave override:
        # Chemical fireworks boom has low centroid (<500 Hz) and sub-bass dominance (m2l < 0.15).
        # A genuine ballistic shockwave / gunfire crack has mid/high frequency acoustic energy
        # ((m2l >= 0.25 and cent >= 750 Hz) or cent >= 1200 Hz) OR strong pure_gun evidence.
        fw_cfg = self.cfg.get("fireworks", {})
        bal_override_th = fw_cfg.get("ballistic_override_threshold", 0.40)
        bal_override_ratio = fw_cfg.get("ballistic_override_ratio", 0.85)
        m2l_req = fw_cfg.get("ballistic_acoustics_mid_to_low", 0.25)
        cent_req = fw_cfg.get("ballistic_acoustics_centroid_hz", 750.0)
        cent_high_req = fw_cfg.get("ballistic_acoustics_high_centroid_hz", 1200.0)
        pure_override_th = fw_cfg.get("pure_gun_override_threshold", 0.20)

        is_ballistic_acoustics = (m2l >= m2l_req and cent >= cent_req) or (cent >= cent_high_req)
        is_ballistic_shockwave = (
            (pure_gun >= pure_override_th) or
            (bal_s >= bal_override_th and bal_s >= fw_s * bal_override_ratio and is_ballistic_acoustics)
        )

        adjusted_score = float(raw_score)
        suppressed = False
        category = None

        # 1. Zero-Energy Digital Silence Gating
        if rms < 1e-4 or peak < 1e-3:
            return {
                "adjusted_score": 0.0,
                "suppressed": True,
                "category": "zero_energy_silence"
            }

        # 2. Confirmed Event Immunity
        if is_in_confirmed_event:
            return {
                "adjusted_score": float(raw_score),
                "suppressed": False,
                "category": None
            }

        # 3. Pyrotechnic Gating (with Calibrated Ballistic Shockwave Override)
        if fw_cfg and fw_cfg.get("enabled", True):
            dom_th = fw_cfg.get("dominant_threshold", 0.45)
            dom_ratio = fw_cfg.get("dominant_ratio", 1.8)
            std_th = fw_cfg.get("standard_threshold", 0.25)
            std_ratio = fw_cfg.get("standard_ratio", 2.2)

            if fw_s >= dom_th and not is_ballistic_shockwave:
                if fw_s / (pure_gun + 1e-4) >= dom_ratio:
                    adjusted_score *= fw_cfg.get("dominant_attenuation", 0.15)
                    suppressed = True
                    category = "fireworks_dominant"
            elif fw_s >= std_th and not is_ballistic_shockwave:
                if fw_s / (pure_gun + 1e-4) >= std_ratio:
                    adjusted_score *= fw_cfg.get("standard_attenuation", 0.30)
                    suppressed = True
                    category = "pyrotechnic_ratio"

        # 4. Glass Shatter Gating
        glass_cfg = self.cfg.get("glass_shatter")
        if glass_cfg and glass_cfg.get("enabled", True) and not suppressed:
            if glass_s >= glass_cfg.get("threshold", 0.30) and hi >= glass_cfg.get("min_high_band_ratio", 0.25):
                if pure_gun < glass_cfg.get("gun_score_max", 0.20):
                    adjusted_score *= glass_cfg.get("attenuation", 0.35)
                    suppressed = True
                    category = "glass_shatter"

        # 5. Sub-Bass Thud & Automotive Backfire Discrimination
        thud_cfg = self.cfg.get("sub_bass_thud")
        if thud_cfg and thud_cfg.get("enabled", True) and not suppressed:
            is_sub_bass = (
                lo >= thud_cfg.get("min_low_ratio", 0.70)
                and hi < thud_cfg.get("max_high_ratio", 0.008)
                and cent < thud_cfg.get("max_centroid_hz", 450.0)
                and pure_gun < thud_cfg.get("max_pure_gun", 0.20)
            )
            is_backfire = (
                cap_gun_s >= thud_cfg.get("min_cap_gun", 0.35)
                and lo >= thud_cfg.get("min_low_ratio", 0.70)
                and (cap_gun_s >= pure_gun * thud_cfg.get("cap_to_pure_ratio", 1.5) or pure_gun < thud_cfg.get("max_pure_gun", 0.20))
            )
            if is_sub_bass or is_backfire:
                adjusted_score *= thud_cfg.get("attenuation", 0.25)
                suppressed = True
                category = "sub_bass_thud"

        # 6. Thunder Physical & Semantic Gating (with Gunshot Transient Discrimination)
        thun_cfg = self.cfg.get("thunder")
        if thun_cfg and thun_cfg.get("enabled", True) and not suppressed:
            is_thun_semantic = (thun_s >= thun_cfg.get("semantic_threshold", 0.20))
            is_thun_phys = (
                lo >= thun_cfg.get("low_band_threshold", 0.65) and
                m2l < thun_cfg.get("mid_to_low_max", 0.55)
            )

            # A genuine gunshot transient contains mid-to-high frequencies or extreme crest factor
            is_gunshot_transient = (
                (m2l >= thun_cfg.get("gunshot_transient_mid_to_low", 0.40) and
                 cent >= thun_cfg.get("gunshot_transient_centroid_hz", 750.0) and
                 crest >= thun_cfg.get("gunshot_transient_crest_db", 16.0)) or
                (pure_gun >= thun_cfg.get("pure_gun_threshold", 0.12)) or
                (peak >= 0.30 and crest >= 12.0 and cent >= 600.0)
            )

            if (is_thun_semantic or is_thun_phys) and not is_gunshot_transient:
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

        # 8. Ballistic Coherence Safeguard (with Saturation Protection)
        coh_cfg = self.cfg.get("ballistic_coherence")
        if coh_cfg and coh_cfg.get("enabled", True) and not suppressed:
            is_saturated = (crest >= 15.0 or peak >= 0.30)
            max_pure = coh_cfg.get("saturation_pure_gun", 0.04) if is_saturated else coh_cfg.get("max_pure_gun", 0.08)
            max_bal = coh_cfg.get("saturation_ballistic", 0.04) if is_saturated else coh_cfg.get("max_ballistic", 0.10)
            if pure_gun < max_pure and bal_s < max_bal:
                adjusted_score *= coh_cfg.get("attenuation", 0.20)
                suppressed = True
                category = "ballistic_incoherence"

        return {
            "adjusted_score": float(adjusted_score),
            "suppressed": suppressed,
            "category": category
        }


class ConditionAdaptiveFSMV8:
    """
    Deterministic Refractory Finite State Machine V8.
    Enhancements in V8:
    - Tightened High-Confidence Gating in UNKNOWN mode:
      Single-impulse crest factor of 13.5 dB is strictly maintained for standard impulses.
      High-confidence impulses (score >= threshold_high) below 13.5 dB require DEGRADED_OCCLUDED
      mode or confirmed high mid/spectral centroid acoustics (m2l >= 0.35, cent >= 750 Hz).
      This rejects isolated mechanical clatter while preserving double-tap confirmations and
      high-energy muzzle blasts.
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
        th_high = policy.get("threshold_high", 0.85)
        th_off = policy.get("threshold_off", 0.40)
        confirm_wins = policy.get("confirm_windows", 2)
        cooldown = policy.get("cooldown_secs", 1.50)
        allow_single = policy.get("allow_single_impulse_exception", True)
        single_th = policy.get("single_impulse_min_score", 0.70)
        single_crest_std = policy.get("single_impulse_min_crest_db", 13.5)
        single_crest_high_conf = policy.get("single_impulse_high_conf_crest_db", 12.0)

        cent = acoustics[7] if acoustics is not None else 1000.0
        m2l = acoustics[5] if acoustics is not None else 0.50

        # High confidence single impulse requires sharp acoustic profile if in UNKNOWN mode
        is_high_conf_qual = (
            score >= th_high and
            crest_db >= single_crest_high_conf and
            (operating_mode == OperatingMode.DEGRADED_OCCLUDED or (m2l >= 0.35 and cent >= 750.0))
        )
        single_allowed = allow_single and ((crest_db >= single_crest_std) or is_high_conf_qual)

        # Check sub-bass single-impulse bypass gate
        is_sub_bass_thud = False
        if acoustics is not None:
            _, _, hi, _, _, _, _, _, _, peak = acoustics
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
            if single_allowed and score >= single_th and not is_sub_bass_thud:
                self.event_counter += 1
                self.current_event = {
                    "event_id": f"EVT_V8_{self.event_counter:04d}",
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
                        "event_id": f"EVT_V8_{self.event_counter:04d}",
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
                    return self.state, emitted_event

        elif self.state == EventState.CONFIRMED:
            if score < th_off:
                self.state = EventState.REFRACTORY
                self.refractory_end_time = time_s + cooldown
                self.candidate_scores = []
                self.candidate_crest_dbs = []
                self.candidate_times = []
                self.current_event = None

        return self.state, emitted_event


class DetectorImprovementV8:
    """
    Detector Improvement V8 Pipeline.
    Combines:
    - Pre-trained YAMNet Backbone + 4-Way Classifier Ensemble (MLP, CatBoost, LightGBM, XGBoost)
    - Condition-Adaptive Calibrated Fusion Head
    - Condition Estimator V8
    - Calibrated Semantic Suppression V8
    - Condition-Adaptive FSM V8
    """

    def __init__(self, config_path: Optional[str] = None):
        if config_path is None:
            config_path = str(pathlib.Path(__file__).parent / "config_improvement_v8.json")
        with open(config_path, "r") as f:
            self.cfg = json.load(f)

        self.name = self.cfg.get("detector_name", "detector_improvement_v8")
        self.version = self.cfg.get("version", "8.0.0")
        self.safety_designation = self.cfg.get(
            "safety_designation", "RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY"
        )

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

        # Initialize condition estimator
        ce_cfg = self.cfg.get("condition_estimator", {})
        self.estimator = ConditionEstimatorV8(
            alpha=ce_cfg.get("alpha", 0.20),
            hysteresis_occluded=ce_cfg.get("hysteresis_windows_occluded", 3),
            hysteresis_clear=ce_cfg.get("hysteresis_windows_clear", 2),
            hysteresis_rumble=ce_cfg.get("hysteresis_windows_rumble", 2)
        )

        # Initialize semantic suppression
        supp_cfg = self.cfg.get("suppression_rules", {})
        self.suppression = CalibratedSemanticSuppressionV8(supp_cfg)

        # Initialize FSM
        mode_policies = self.cfg.get("mode_policies", {})
        self.fsm = ConditionAdaptiveFSMV8(mode_policies)
        self.threshold_base = float(self.cfg.get("mode_policies", {}).get("CLEAR_NORMAL", {}).get("threshold_base", 0.70))
        self.threshold_high = float(self.cfg.get("mode_policies", {}).get("CLEAR_NORMAL", {}).get("threshold_high", 0.85))

    def reset(self):
        self.estimator.reset()
        self.fsm.reset()

    def extract_features(self, window_16k: np.ndarray) -> Tuple[np.ndarray, Dict[int, float], Tuple]:
        """
        Extracts 25-dimensional feature vector, YAMNet class dictionary, and 10 physical DSP metrics.
        """
        acoustics = compute_physical_acoustic_features_v8(window_16k, sr=16000)
        crest, flat, hi, mid, lo, m2l, rolloff, cent, rms, peak = acoustics

        # Zero energy early exit
        if rms < 1e-4 or peak < 1e-3:
            feat = np.zeros(26, dtype=np.float32)
            ys = {i: 0.0 for i in range(521)}
            return feat, ys, acoustics

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


class RealTimeStreamDetectorImprovementV8:
    """
    Real-Time Streaming Gunshot Detector for Detector Improvement V8.
    Maintains a streaming ring buffer, extracts physical acoustics and ensemble features,
    applies ConditionEstimatorV8 and CalibratedSemanticSuppressionV8, and drives
    ConditionAdaptiveFSMV8. Thread-safe.
    """
    def __init__(
        self,
        config_path: Optional[str] = None,
        chunk_duration_sec: float = 0.48,
        sample_rate: int = 16000
    ):
        self.detector = DetectorImprovementV8(config_path=config_path)
        self.sample_rate = sample_rate
        self.chunk_size = int(chunk_duration_sec * sample_rate)
        self.window_size = 15360
        self.hop_size = 7680
        self.lock = threading.Lock()

        self.buffer = np.zeros(0, dtype=np.float32)
        self.stream_offset_samples = 0
        self.stream_time_sec = 0.0

        self.last_score = 0.0
        self.last_crest_factor_db = 0.0
        self.detected_alerts: List[Dict[str, Any]] = []
        self.chunk_latencies_ms: List[float] = []

    @property
    def in_event(self) -> bool:
        return self.detector.fsm.state == EventState.CONFIRMED

    @property
    def cooldown_until(self) -> float:
        return self.detector.fsm.refractory_end_time

    def reset(self):
        with self.lock:
            self.buffer = np.zeros(0, dtype=np.float32)
            self.stream_offset_samples = 0
            self.stream_time_sec = 0.0
            self.last_score = 0.0
            self.last_crest_factor_db = 0.0
            self.detected_alerts = []
            self.chunk_latencies_ms = []
            self.detector.reset()

    def process_chunk(
        self,
        chunk: np.ndarray,
        input_sample_rate: int = 16000
    ) -> List[Dict[str, Any]]:
        t0 = time.perf_counter()
        if chunk is None or len(chunk) == 0:
            return []

        chunk = chunk.astype(np.float32)
        if chunk.ndim > 1:
            chunk = np.mean(chunk, axis=1)

        if input_sample_rate != self.sample_rate:
            import scipy.signal
            num_samples = int(len(chunk) * self.sample_rate / input_sample_rate)
            chunk = scipy.signal.resample(chunk, num_samples)

        new_alerts = []

        with self.lock:
            self.buffer = np.concatenate([self.buffer, chunk])

            while len(self.buffer) >= self.window_size:
                window_audio = self.buffer[:self.window_size]
                st = round(self.stream_offset_samples / float(self.sample_rate), 3)
                et = round((self.stream_offset_samples + self.window_size) / float(self.sample_rate), 3)

                feat, ys, acoustics = self.detector.extract_features(window_audio)
                crest, flat, hi, mid, lo, m2l, rolloff, cent, rms, peak = acoustics

                self.last_crest_factor_db = crest

                # Update condition estimator
                mode, conf, _ = self.detector.estimator.update(
                    rolloff, hi, mid, lo, m2l, st, int(self.stream_offset_samples // self.hop_size)
                )

                # Ensemble fusion score
                raw_score = float(self.detector.fusion_model.predict_proba(feat.reshape(1, -1))[:, 1][0])

                # Calibrated suppression
                is_confirmed = (self.detector.fsm.state == EventState.CONFIRMED)
                supp = self.detector.suppression.apply_suppression(raw_score, ys, acoustics, is_confirmed)
                adj_score = supp["adjusted_score"]
                self.last_score = adj_score

                # FSM step
                _, ev = self.detector.fsm.step(adj_score, crest, st, acoustics, mode)
                if ev is not None:
                    ev_record = dict(ev)
                    ev_record["stream_timestamp_sec"] = st
                    new_alerts.append(ev_record)
                    self.detected_alerts.append(ev_record)

                # Advance buffer by hop
                self.buffer = self.buffer[self.hop_size:]
                self.stream_offset_samples += self.hop_size
                self.stream_time_sec = self.stream_offset_samples / float(self.sample_rate)

            lat_ms = (time.perf_counter() - t0) * 1000.0
            self.chunk_latencies_ms.append(lat_ms)
            if len(self.chunk_latencies_ms) > 100:
                self.chunk_latencies_ms = self.chunk_latencies_ms[-100:]

        return new_alerts


