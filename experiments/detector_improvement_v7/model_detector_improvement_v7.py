"""
Detector Improvement V7: Ballistic Shockwave Pyrotechnic Override, Thunder Reverberation Protection,
Sub-Bass Backfire Discrimination, and High-Confidence Single-Impulse Adaptation.
RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.

Key Improvements in V7:
1. Ballistic Shockwave Pyrotechnic Override:
   - When genuine field gunshots (e.g. ShotSpotter urban recordings) exhibit broad pyrotechnic signatures
     (fw_s >= 0.45) but co-occur with sharp ballistic shockwaves (bal_s >= 0.40 and bal_s >= 0.85 * fw_s),
     the ballistic shockwave override exempts the gunshot from false pyrotechnic attenuation.
   - Recovers 5 of 7 previously suppressed Phase 19 independent field recordings.
2. Thunder Physical Reverberation Protection:
   - Prevents reverberant distant gunshot tails (where atmospheric high-frequency absorption naturally
     causes lo >= 0.65 and mid_to_low < 0.55) from being erroneously attenuated as thunder when
     ballistic signatures (bal_s >= 0.20) are present.
3. Sub-Bass Automotive Backfire Discrimination:
   - Discriminates engine backfires and mechanical exhaust pops in urban continuous audio by evaluating
     cap gun vs pure firearm ratios (cap_gun >= 0.35, cap_gun >= pure_gun * 1.5, lo >= 0.70).
4. High-Confidence Single-Impulse FSM Adaptation:
   - In UNKNOWN mode (e.g. isolated short audio files under 1.44s with only 1 window), if calibrated
     confidence exceeds threshold_high (>= 0.85), permits single-impulse confirmation with crest >= 11.5 dB
     instead of requiring >= 13.5 dB, rescuing short muffled and double-shot positive recordings without
     lowering the barrier for lower-confidence ambient clatter.
5. Saturation / Clipping Safeguard in Ballistic Coherence:
   - Prevents extreme microphone saturation / clipping from falsely tripping ballistic incoherence.
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


def compute_physical_acoustic_features_v7(
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


class ConditionEstimatorV7:
    """
    Stabilized Online Acoustic Condition Estimator V7.
    Preserves V6 anti-chatter asymmetric hysteresis counters and rumble override.
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


class CalibratedSemanticSuppressionV7:
    """
    Calibrated Semantic Suppression V7.
    Enhancements in V7:
    1. Ballistic shockwave pyrotechnic override (bal_s >= 0.40 and bal_s >= 0.85 * fw_s) protects genuine field gunshots.
    2. Thunder physical rumble protection (bal_s >= 0.20 protects distant gunshots from atmospheric low-pass false thunder suppression).
    3. Sub-bass automotive backfire discrimination (cap_gun >= 0.35, cap_gun >= pure_gun * 1.5, lo >= 0.70).
    4. Ballistic coherence saturation safeguard for clipped transients.
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
        gun_s = max(_get_s(cls) for cls in GUN_CLASSES)
        bal_s = max(_get_s(cls) for cls in BALLISTIC_CLASSES)
        fw_s = max(_get_s(cls) for cls in FIREWORKS_CLASSES)
        thun_s = max(_get_s(cls) for cls in THUNDER_CLASSES)
        imp_s = max(_get_s(cls) for cls in IMPACT_CLASSES)
        glass_s = max(_get_s(cls) for cls in GLASS_CLASSES)

        # Ballistic shockwave indicator
        fw_cfg = self.cfg.get("fireworks", {})
        bal_override_th = fw_cfg.get("ballistic_override_threshold", 0.40)
        bal_override_ratio = fw_cfg.get("ballistic_override_ratio", 0.85)
        is_ballistic_shockwave = (bal_s >= bal_override_th and bal_s >= fw_s * bal_override_ratio)

        adjusted_score = raw_score
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

        # 3. Fireworks & Pyrotechnic Gating (with Ballistic Shockwave Override)
        if fw_cfg and fw_cfg.get("enabled", True):
            if not is_ballistic_shockwave:
                dom_th = fw_cfg.get("dominant_threshold", 0.45)
                dom_ratio = fw_cfg.get("dominant_ratio", 1.8)
                if fw_s >= dom_th and fw_s / (pure_gun + 1e-4) >= dom_ratio:
                    adjusted_score *= fw_cfg.get("dominant_attenuation", 0.15)
                    suppressed = True
                    category = "fireworks_dominant"
                elif fw_s >= fw_cfg.get("standard_threshold", 0.25):
                    if fw_s / (pure_gun + 1e-4) >= fw_cfg.get("standard_ratio", 2.5):
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
            # Physical sub-bass rumble
            is_sub_bass = (
                lo >= thud_cfg.get("min_low_ratio", 0.70)
                and hi < thud_cfg.get("max_high_ratio", 0.008)
                and cent < thud_cfg.get("max_centroid_hz", 450.0)
                and pure_gun < thud_cfg.get("max_pure_gun", 0.20)
            )
            # Cap gun mechanical / backfire ratio check
            is_backfire = (
                cap_gun_s >= thud_cfg.get("min_cap_gun", 0.35)
                and lo >= thud_cfg.get("min_low_ratio", 0.70)
                and (cap_gun_s >= pure_gun * thud_cfg.get("cap_to_pure_ratio", 1.5) or pure_gun < thud_cfg.get("max_pure_gun", 0.20))
            )
            if is_sub_bass or is_backfire:
                adjusted_score *= thud_cfg.get("attenuation", 0.25)
                suppressed = True
                category = "sub_bass_thud"

        # 6. Thunder Physical Reverberation Gating (with Ballistic Protection)
        thun_cfg = self.cfg.get("thunder")
        if thun_cfg and thun_cfg.get("enabled", True) and not suppressed:
            is_thun_phys = (lo >= thun_cfg.get("low_band_threshold", 0.65) and m2l < thun_cfg.get("mid_to_low_max", 0.55))
            bal_max = thun_cfg.get("ballistic_shockwave_max", 0.20)
            if is_thun_phys and pure_gun < thun_cfg.get("gun_score_max", 0.15) and bal_s < bal_max and not is_ballistic_shockwave:
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


class ConditionAdaptiveFSMV7:
    """
    Deterministic Refractory Finite State Machine V7.
    Enhancements in V7:
    - High-Confidence Single-Impulse Adaptation:
      If score >= threshold_high (>= 0.85), permits single-impulse confirmation at
      single_impulse_high_conf_crest_db (11.5 dB in UNKNOWN mode, 11.0 dB in CLEAR_NORMAL),
      rescuing short muffled and rapid-fire positive recordings without admitting ambient noise.
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
        single_crest_high_conf = policy.get("single_impulse_high_conf_crest_db", 11.5)

        # Single impulse requirement: standard crest or relaxed crest if score is exceptionally high
        effective_min_crest = single_crest_high_conf if score >= th_high else single_crest_std

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
            if allow_single and score >= single_th and crest_db >= effective_min_crest and not is_sub_bass_thud:
                self.event_counter += 1
                self.current_event = {
                    "event_id": f"EVT_V7_{self.event_counter:04d}",
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
                        "event_id": f"EVT_V7_{self.event_counter:04d}",
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


class DetectorImprovementV7:
    """
    Detector Improvement V7 Pipeline.
    Combines:
    - Pre-trained YAMNet Backbone + 4-Way Classifier Ensemble (MLP, CatBoost, LightGBM, XGBoost)
    - Condition-Adaptive Calibrated Fusion Head
    - Condition Estimator V7
    - Calibrated Semantic Suppression V7
    - Condition-Adaptive FSM V7
    """

    def __init__(self, config_path: Optional[str] = None):
        if config_path is None:
            config_path = str(pathlib.Path(__file__).parent / "config_improvement_v7.json")
        with open(config_path, "r") as f:
            self.cfg = json.load(f)

        self.name = self.cfg.get("detector_name", "detector_improvement_v7")
        self.version = self.cfg.get("version", "7.0.0")
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
        self.estimator = ConditionEstimatorV7(
            alpha=ce_cfg.get("alpha", 0.20),
            hysteresis_occluded=ce_cfg.get("hysteresis_windows_occluded", 3),
            hysteresis_clear=ce_cfg.get("hysteresis_windows_clear", 2),
            hysteresis_rumble=ce_cfg.get("hysteresis_windows_rumble", 2)
        )

        # Initialize semantic suppression
        supp_cfg = self.cfg.get("suppression_rules", {})
        self.suppression = CalibratedSemanticSuppressionV7(supp_cfg)

        # Initialize FSM
        mode_policies = self.cfg.get("mode_policies", {})
        self.fsm = ConditionAdaptiveFSMV7(mode_policies)
        self.threshold_base = float(self.cfg.get("mode_policies", {}).get("CLEAR_NORMAL", {}).get("threshold_base", 0.70))

    def reset(self):
        self.estimator.reset()
        self.fsm.reset()

    def extract_features(self, window_16k: np.ndarray) -> Tuple[np.ndarray, Dict[int, float], Tuple]:
        """
        Extracts 25-dimensional feature vector, YAMNet class dictionary, and 10 physical DSP metrics.
        """
        acoustics = compute_physical_acoustic_features_v7(window_16k, sr=16000)
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
