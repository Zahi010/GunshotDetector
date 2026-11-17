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

logger = logging.getLogger("detector_improvement_v3")

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

GUN_CLASSES = [YAMNET_CLASS_GUNSHOT, YAMNET_CLASS_MACHINE_GUN, YAMNET_CLASS_ARTILLERY, YAMNET_CLASS_CAP_GUN]
BALLISTIC_CLASSES = [YAMNET_CLASS_EXPLOSION, YAMNET_CLASS_GUNSHOT, YAMNET_CLASS_MACHINE_GUN, YAMNET_CLASS_ARTILLERY, YAMNET_CLASS_CAP_GUN, YAMNET_CLASS_BURST_POP, YAMNET_CLASS_CRACK, YAMNET_CLASS_BANG]
FIREWORKS_CLASSES = [YAMNET_CLASS_FIREWORKS, YAMNET_CLASS_FIRECRACKER]
THUNDER_CLASSES = [YAMNET_CLASS_THUNDERSTORM, YAMNET_CLASS_THUNDER]
DOG_CLASSES = [YAMNET_CLASS_DOG, YAMNET_CLASS_BARK, YAMNET_CLASS_YIP, YAMNET_CLASS_CANIDAE]
CRACKLE_CLASSES = [YAMNET_CLASS_FIRE, YAMNET_CLASS_CRACKLE]
SIREN_CLASSES = [YAMNET_CLASS_POLICE_CAR, YAMNET_CLASS_AMBULANCE, YAMNET_CLASS_FIRE_ENGINE, YAMNET_CLASS_SIREN, YAMNET_CLASS_CIVIL_DEFENSE]
WIND_CLASSES = [YAMNET_CLASS_WIND, YAMNET_CLASS_WIND_NOISE_MIC]
IMPACT_CLASSES = [YAMNET_CLASS_HAMMER, YAMNET_CLASS_JACKHAMMER, YAMNET_CLASS_SLAM, YAMNET_CLASS_KNOCK, YAMNET_CLASS_CLAP]

NON_TARGET_SEMANTIC_CLASSES = (
    [0] + # Speech
    list(range(67, 118)) + # Animal vocalizations
    list(range(300, 331)) + # Motor vehicles and traffic
    [502, 503, 504] # Outside / Natural ambient
)


def extract_fast_acoustics(y_win: np.ndarray, sr: int = 16000) -> Tuple[float, float, float, float, float]:
    """
    Computes physical acoustic features on a single evaluation window in <0.3ms:
    1. crest_factor_db: 20 * log10(peak / RMS)
    2. spectral_flatness: exp(mean(log(P))) / mean(P)
    3. high_freq_ratio: energy >= 2500 Hz / total energy
    4. low_freq_ratio: energy < 500 Hz / total energy
    5. spectral_centroid: sum(f * P) / total energy
    """
    if len(y_win) == 0:
        return 0.0, 0.0, 0.0, 0.0, 0.0
    pk = float(np.max(np.abs(y_win)))
    rms = float(np.sqrt(np.mean(y_win**2) + 1e-12))
    crest_db = float(20.0 * np.log10(max(pk / (rms + 1e-12), 1.0)))

    # Fast power spectrum
    P = np.abs(np.fft.rfft(y_win))**2
    freqs = np.fft.rfftfreq(len(y_win), d=1.0 / float(sr))

    # Flatness
    log_p = np.log(P + 1e-12)
    flatness = float(np.exp(np.mean(log_p)) / (np.mean(P) + 1e-12))

    tot_e = float(np.sum(P) + 1e-12)
    low_e = float(np.sum(P[freqs < 500.0]))
    high_e = float(np.sum(P[freqs >= 2500.0]))
    centroid = float(np.sum(freqs * P) / tot_e)

    return crest_db, flatness, (high_e / tot_e), (low_e / tot_e), centroid


class CalibratedAcousticSuppressionV3:
    """
    Calibrated Multi-Category Semantic Suppression V3:
    - Ballistic Coherence Safeguard (rejects tabular artifacts on purely non-ballistic audio).
    - Ballistic Shockwave Protection: Prevents authentic gunshot explosions from being
      erroneously suppressed by fireworks filters when ballistic explosive evidence is strong.
    - Two-tier Pyrotechnic Gating (standard vs dominant fireworks).
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
            "standard_attenuation": 0.35,
            "ballistic_override_threshold": 0.45
        })
        self.wind_cfg = suppression_cfg.get("wind_buffeting", {"threshold": 0.25, "ratio": 1.5, "attenuation": 0.25})
        self.impact_cfg = suppression_cfg.get("mechanical_impact", {"threshold": 0.30, "ratio": 1.5, "gun_max": 0.20, "attenuation": 0.35})
        self.dog_cfg = suppression_cfg.get("canine", {"threshold": 0.30, "ratio": 1.5, "attenuation": 0.35})
        self.crackle_cfg = suppression_cfg.get("fire_crackle", {"threshold": 0.25, "ratio": 1.5, "attenuation": 0.35})
        self.siren_cfg = suppression_cfg.get("siren", {"threshold": 0.35, "ratio": 1.5, "attenuation": 0.30})

    def apply_suppression(
        self,
        raw_score: float,
        yamnet_scores: Optional[np.ndarray],
        is_in_confirmed_event: bool = False
    ) -> Dict[str, Any]:
        """Calculates calibrated score after evaluating multi-category acoustic semantics."""
        if not self.enabled or yamnet_scores is None or len(yamnet_scores) == 0 or is_in_confirmed_event:
            return {
                "adjusted_score": float(raw_score),
                "suppression_active": False,
                "suppression_category": None,
                "suppression_strength": 1.0,
                "suppression_reason": None
            }

        gun_score = max(float(yamnet_scores[c]) for c in GUN_CLASSES)
        ballistic_score = max(float(yamnet_scores[c]) for c in BALLISTIC_CLASSES)
        fw_score = max(float(yamnet_scores[c]) for c in FIREWORKS_CLASSES)
        thun_score = max(float(yamnet_scores[c]) for c in THUNDER_CLASSES)
        dog_score = max(float(yamnet_scores[c]) for c in DOG_CLASSES)
        crackle_score = max(float(yamnet_scores[c]) for c in CRACKLE_CLASSES)
        siren_score = max(float(yamnet_scores[c]) for c in SIREN_CLASSES)
        wind_score = max(float(yamnet_scores[c]) for c in WIND_CLASSES)
        impact_score = max(float(yamnet_scores[c]) for c in IMPACT_CLASSES)
        non_target_score = max(float(yamnet_scores[c]) for c in NON_TARGET_SEMANTIC_CLASSES)

        adj_score = float(raw_score)
        supp_cat = None
        strength = 1.0

        # Ballistic shockwave protection check
        ballistic_override = (
            ballistic_score >= self.fw_cfg.get("ballistic_override_threshold", 0.45)
            or ballistic_score >= fw_score * 0.90
        )

        # 1. Non-ballistic acoustic coherence safeguard
        if (
            self.coherence_cfg.get("enabled", True)
            and ballistic_score < self.coherence_cfg.get("ballistic_max_threshold", 0.015)
            and non_target_score >= self.coherence_cfg.get("non_target_threshold", 0.12)
        ):
            strength = float(self.coherence_cfg.get("attenuation", 0.20))
            adj_score *= strength
            supp_cat = "non_ballistic_coherence_rejection"

        # 2. Thunder suppression
        elif thun_score > self.thun_cfg["threshold"] and thun_score >= gun_score * self.thun_cfg["ratio"]:
            strength = float(self.thun_cfg["attenuation"])
            adj_score *= strength
            supp_cat = "thunder"

        # 3. Fireworks suppression (protected by ballistic override)
        elif (
            not ballistic_override
            and fw_score >= self.fw_cfg["dominant_threshold"]
            and fw_score >= gun_score * self.fw_cfg["dominant_ratio"]
            and gun_score < self.fw_cfg["dominant_gun_max"]
        ):
            strength = float(self.fw_cfg["dominant_attenuation"])
            adj_score *= strength
            supp_cat = "fireworks_dominant"

        elif (
            not ballistic_override
            and fw_score >= self.fw_cfg["standard_threshold"]
            and fw_score >= gun_score * self.fw_cfg["standard_ratio"]
            and gun_score < self.fw_cfg["standard_gun_max"]
        ):
            strength = float(self.fw_cfg["standard_attenuation"])
            adj_score *= strength
            supp_cat = "fireworks_standard"

        # 4. Wind buffeting / infrasonic rumble
        elif wind_score >= self.wind_cfg["threshold"] and wind_score >= gun_score * self.wind_cfg["ratio"]:
            strength = float(self.wind_cfg["attenuation"])
            adj_score *= strength
            supp_cat = "wind_buffeting"

        # 5. Mechanical impacts / heavy tools
        elif (
            impact_score >= self.impact_cfg["threshold"]
            and impact_score >= gun_score * self.impact_cfg["ratio"]
            and gun_score < self.impact_cfg["gun_max"]
        ):
            strength = float(self.impact_cfg["attenuation"])
            adj_score *= strength
            supp_cat = "mechanical_impact"

        # 6. Canine vocalization
        elif dog_score > self.dog_cfg["threshold"] and dog_score >= gun_score * self.dog_cfg["ratio"]:
            strength = float(self.dog_cfg["attenuation"])
            adj_score *= strength
            supp_cat = "canine_bark"

        # 7. Fire crackle
        elif crackle_score > self.crackle_cfg["threshold"] and crackle_score >= gun_score * self.crackle_cfg["ratio"]:
            strength = float(self.crackle_cfg["attenuation"])
            adj_score *= strength
            supp_cat = "fire_crackle"

        # 8. Siren / Emergency transit
        elif siren_score > self.siren_cfg["threshold"] and siren_score >= gun_score * self.siren_cfg["ratio"]:
            strength = float(self.siren_cfg["attenuation"])
            adj_score *= strength
            supp_cat = "siren"

        return {
            "adjusted_score": float(adj_score),
            "suppression_active": supp_cat is not None,
            "suppression_category": supp_cat,
            "suppression_strength": float(strength),
            "suppression_reason": f"Suppressed via {supp_cat} (factor {strength:.2f})" if supp_cat else None
        }


class EventStateMachineV3(EventStateMachine):
    """
    Deterministic 4-State Refractory State Machine V3:
    1. Stores crest_factor_db directly inside each window dict in candidate_windows.
    2. Corrects candidate decay evaluation: verifies the candidate impulse window's
       OWN crest factor, not the subsequent quiet reverberation window.
    3. Stream-Duration Invariant: Removes the arbitrary <= 5.0s clip length restriction
       so authentic single-impulse gunshots in long files or continuous streams are
       correctly confirmed.
    """

    def __init__(
        self,
        threshold_base: float = 0.68,
        threshold_high: float = 0.83,
        threshold_off: float = 0.43,
        confirm_windows: int = 2,
        cooldown_secs: float = 2.0,
        max_hop_gap_s: float = 0.60,
        min_crest_factor_db: float = 8.0,
        single_win_min_crest_db: float = 10.5,
        allow_short_clip_exception: bool = True,
        allow_single_impulse_exception: bool = True,
        single_impulse_min_score: float = 0.68,
        single_impulse_min_crest_db: float = 8.5,
        single_impulse_max_dur_sec: float = 999.0
    ):
        super().__init__(
            threshold_base=threshold_base,
            threshold_high=threshold_high,
            threshold_off=threshold_off,
            confirm_windows=confirm_windows,
            cooldown_secs=cooldown_secs,
            max_hop_gap_s=max_hop_gap_s,
            min_crest_factor_db=min_crest_factor_db,
            single_win_min_crest_db=single_win_min_crest_db,
            allow_short_clip_exception=allow_short_clip_exception
        )
        self.allow_single_impulse_exception = allow_single_impulse_exception
        self.single_impulse_min_score = single_impulse_min_score
        self.single_impulse_min_crest_db = single_impulse_min_crest_db
        self.single_impulse_max_dur_sec = single_impulse_max_dur_sec

    def process_window(
        self,
        window: Dict[str, Any],
        crest_factor_db: Optional[float] = None,
        audio_duration_sec: Optional[float] = None,
        total_windows_in_stream: Optional[int] = None
    ) -> Optional[Dict[str, Any]]:
        # Ensure window dictionary carries crest_factor_db
        if crest_factor_db is not None and "crest_factor_db" not in window:
            window["crest_factor_db"] = float(crest_factor_db)

        st = float(window["start_time"])
        score = float(window["score"])

        # Check decaying candidate state before calling parent state machine
        if self.state == EventState.CANDIDATE:
            time_gap = (st - self.last_window_time) if self.last_window_time is not None else 0.0
            is_gap = (time_gap > self.max_hop_gap_s)
            is_decay = (score < self.threshold_base)

            if (is_gap or is_decay) and self.allow_single_impulse_exception and len(self.candidate_windows) == 1:
                cand = self.candidate_windows[0]
                cand_score = float(cand.get("score", 0.0))
                # Explicitly retrieve candidate window's own crest factor
                cand_crest = cand.get("crest_factor_db")
                if cand_crest is None:
                    cand_crest = crest_factor_db
                cand_suppressed = bool(cand.get("suppression_active", False))

                qualifies_impulse = (
                    cand_score >= self.single_impulse_min_score
                    and (cand_crest is not None and cand_crest >= self.single_impulse_min_crest_db)
                    and (audio_duration_sec is None or audio_duration_sec <= self.single_impulse_max_dur_sec)
                    and not cand_suppressed
                )

                if qualifies_impulse:
                    self.confirmed_windows = [cand]
                    self.candidate_windows = []
                    self._record_transition(
                        EventState.CANDIDATE,
                        EventState.CONFIRMED,
                        TransitionReason.IMMEDIATE_HIGH_CONFIDENCE,
                        timestamp_s=float(cand["start_time"]),
                        score=cand_score,
                        raw_score=float(cand.get("raw_score", cand_score)),
                        window_start_s=float(cand["start_time"]),
                        window_end_s=float(cand["end_time"])
                    )
                    self.state = EventState.CONFIRMED

                    emitted = self._create_event_record(self.confirmed_windows, "single_round_impulse")
                    self.events_emitted.append(emitted)
                    self.cooldown_until = emitted["end_time"] + self.cooldown_secs

                    self._record_transition(
                        EventState.CONFIRMED,
                        EventState.COOLDOWN,
                        TransitionReason.EVENT_DECAYED_BELOW_OFF,
                        timestamp_s=st,
                        score=score,
                        raw_score=float(window.get("raw_score", score)),
                        window_start_s=st,
                        window_end_s=float(window["end_time"])
                    )
                    self.confirmed_windows = []
                    self.state = EventState.COOLDOWN
                    self.last_window_time = st
                    return emitted

        return super().process_window(
            window=window,
            crest_factor_db=crest_factor_db,
            audio_duration_sec=audio_duration_sec,
            total_windows_in_stream=total_windows_in_stream
        )


class DetectorImprovementV3:
    """
    Detector Improvement V3 Offline Evaluator.
    Incorporates:
    - YAMNet Feature Extractor (1024-d embedding + 521 AudioSet semantics)
    - 4 Pretrained Base Classifiers (MLP, CatBoost, LightGBM, XGBoost)
    - Calibrated Acoustic Fusion Model V3 (blends model outputs + semantics + physical acoustics)
    - Calibrated Acoustic Suppression V3 with Ballistic Shockwave Protection
    - Refractory Event State Machine V3
    """

    def __init__(
        self,
        config_path: Optional[Union[str, pathlib.Path]] = None,
        profile: str = "balanced"
    ):
        if config_path is None:
            config_path = pathlib.Path(__file__).parent / "config_improvement_v3.json"
        config_path = pathlib.Path(config_path)

        with open(config_path, "r", encoding="utf-8") as f:
            self.full_config = json.load(f)

        self.profile_name = profile
        if profile not in self.full_config.get("profiles", {}):
            raise ValueError(f"Unknown profile '{profile}'. Available: {list(self.full_config.get('profiles', {}).keys())}")

        self.cfg = self.full_config["profiles"][profile]
        self.dsp_cfg = self.full_config.get("dsp", {
            "target_sample_rate": 16000,
            "window_size_samples": 15360,
            "hop_size_samples": 7680,
            "window_duration_seconds": 0.96,
            "hop_duration_seconds": 0.48
        })

        # Load models
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

        # Load Fusion Model V3
        fusion_path = pathlib.Path(__file__).parent / "fusion_model.joblib"
        if not fusion_path.exists():
            fusion_path = pathlib.Path(__file__).resolve().parents[2] / "experiments" / "detector_improvement_v3" / "fusion_model.joblib"
        self.fusion_model = joblib.load(str(fusion_path))

        # Suppression and State Machine
        self.suppression = CalibratedAcousticSuppressionV3(self.cfg.get("suppression", {}))
        self.fsm = EventStateMachineV3(
            threshold_base=float(self.cfg.get("threshold_base", 0.68)),
            threshold_high=float(self.cfg.get("threshold_high", 0.83)),
            threshold_off=float(self.cfg.get("threshold_off", 0.43)),
            confirm_windows=int(self.cfg.get("confirm_windows", 2)),
            cooldown_secs=float(self.cfg.get("cooldown_secs", 2.0)),
            max_hop_gap_s=float(self.cfg.get("max_hop_gap_s", 0.60)),
            min_crest_factor_db=float(self.cfg.get("min_crest_factor_db", 8.0)),
            single_win_min_crest_db=float(self.cfg.get("single_win_min_crest_db", 10.5)),
            allow_short_clip_exception=bool(self.cfg.get("allow_short_clip_exception", True)),
            allow_single_impulse_exception=bool(self.cfg.get("allow_single_impulse_exception", True)),
            single_impulse_min_score=float(self.cfg.get("single_impulse_min_score", 0.68)),
            single_impulse_min_crest_db=float(self.cfg.get("single_impulse_min_crest_db", 8.5)),
            single_impulse_max_dur_sec=float(self.cfg.get("single_impulse_max_dur_sec", 999.0))
        )

    def evaluate_waveform(
        self,
        audio_16k: np.ndarray,
        precomputed_embeddings: Optional[np.ndarray] = None,
        precomputed_yamnet_scores: Optional[np.ndarray] = None
    ) -> Dict[str, Any]:
        """Evaluates a 16kHz mono audio waveform."""
        if audio_16k.ndim > 1:
            audio_16k = np.mean(audio_16k, axis=1)
        audio_16k = audio_16k.astype(np.float32)

        duration_sec = float(len(audio_16k)) / 16000.0

        # Extract YAMNet embeddings if not precomputed
        if precomputed_embeddings is not None and precomputed_yamnet_scores is not None:
            embs = precomputed_embeddings
            ys = precomputed_yamnet_scores
        else:
            wave_tensor = tf.convert_to_tensor(audio_16k, dtype=tf.float32)
            yamnet_scores_tf, embeddings_tf, _ = self.yamnet_model(wave_tensor)
            embs = embeddings_tf.numpy()
            ys = yamnet_scores_tf.numpy()

        if len(embs) == 0:
            return {
                "detected": False,
                "event_count": 0,
                "overall_score": 0.0,
                "peak_score": 0.0,
                "events": [],
                "windows": [],
                "profile": self.profile_name
            }

        # Model predictions
        p_mlp = self.mlp.predict(embs, verbose=0).flatten()
        p_cb = self.cb.predict_proba(embs)[:, 1]
        p_lgb = self.lgb.predict_proba(embs)[:, 1]
        p_xgb = self.xgb.predict_proba(embs)[:, 1]

        # Extract physical acoustics and assemble features per window
        win_records = []
        fusion_features = []
        hop_samples = self.dsp_cfg["hop_size_samples"]
        win_samples = self.dsp_cfg["window_size_samples"]

        for w in range(len(embs)):
            st_s = w * self.dsp_cfg["hop_duration_seconds"]
            et_s = st_s + self.dsp_cfg["window_duration_seconds"]

            st_sample = w * hop_samples
            ed_sample = st_sample + win_samples
            y_win = audio_16k[st_sample:ed_sample] if st_sample < len(audio_16k) else np.zeros(win_samples, dtype=np.float32)
            if len(y_win) < win_samples:
                y_win = np.pad(y_win, (0, win_samples - len(y_win)))

            crest_db, flat, hi, lo, cent = extract_fast_acoustics(y_win, sr=16000)

            m, c, l, x = p_mlp[w], p_cb[w], p_lgb[w], p_xgb[w]
            m_mean = (m + c + l + x) / 4.0
            m_max = max(m, c, l, x)
            m_min = min(m, c, l, x)
            m_std = float(np.std([m, c, l, x]))
            sorted_m = sorted([m, c, l, x], reverse=True)
            top2 = (sorted_m[0] + sorted_m[1]) / 2.0

            gun_s = max(float(ys[w][cls]) for cls in GUN_CLASSES)
            bal_s = max(float(ys[w][cls]) for cls in BALLISTIC_CLASSES)
            fw_s = max(float(ys[w][cls]) for cls in FIREWORKS_CLASSES)
            thun_s = max(float(ys[w][cls]) for cls in THUNDER_CLASSES)
            imp_s = max(float(ys[w][cls]) for cls in IMPACT_CLASSES)
            nt_s = max(float(ys[w][cls]) for cls in NON_TARGET_SEMANTIC_CLASSES)

            feat = [
                m, c, l, x,
                m_mean, m_max, m_min, m_std, top2,
                gun_s, bal_s, fw_s, thun_s, imp_s, nt_s,
                (bal_s + 1e-4) / (fw_s + 1e-4),
                (bal_s + 1e-4) / (imp_s + 1e-4),
                crest_db, flat, hi, lo, cent
            ]
            fusion_features.append(feat)
            win_records.append({
                "window_index": w,
                "start_time": st_s,
                "end_time": et_s,
                "crest_factor_db": crest_db,
                "yamnet_scores": ys[w]
            })

        X_fusion = np.array(fusion_features, dtype=np.float32)
        raw_scores = self.fusion_model.predict_proba(X_fusion)[:, 1]

        # Reset state machine
        self.fsm.reset()
        events = []
        processed_windows = []

        for w, rec in enumerate(win_records):
            raw_s = float(raw_scores[w])
            supp_res = self.suppression.apply_suppression(
                raw_score=raw_s,
                yamnet_scores=rec["yamnet_scores"],
                is_in_confirmed_event=(self.fsm.state == EventState.CONFIRMED)
            )

            adj_s = float(supp_res["adjusted_score"])
            win_dict = {
                "window_index": w,
                "start_time": rec["start_time"],
                "end_time": rec["end_time"],
                "score": adj_s,
                "raw_score": raw_s,
                "crest_factor_db": rec["crest_factor_db"],
                "suppression_active": supp_res["suppression_active"],
                "suppression_category": supp_res["suppression_category"],
                "suppression_strength": supp_res["suppression_strength"]
            }
            processed_windows.append(win_dict)

            ev = self.fsm.process_window(
                window=win_dict,
                crest_factor_db=rec["crest_factor_db"],
                audio_duration_sec=duration_sec,
                total_windows_in_stream=len(win_records)
            )
            if ev is not None:
                events.append(ev)

        # Flush any trailing event
        flush_ev = self.fsm.flush()
        if flush_ev is not None:
            events.append(flush_ev)

        detected = len(events) > 0
        peak_score = float(max((w["score"] for w in processed_windows), default=0.0))
        overall_score = float(max((e["peak_score"] for e in events), default=peak_score))

        return {
            "detected": detected,
            "event_count": len(events),
            "overall_score": overall_score,
            "peak_score": peak_score,
            "events": events,
            "windows": processed_windows,
            "profile": self.profile_name
        }


class RealTimeStreamDetectorImprovementV3:
    """
    Online Streaming Audio Gunshot Detector Improvement V3.
    Processes continuous incoming audio streams in 0.96s windows with 0.48s hops.
    Invokes alert_callback upon confirmed gunshot detection.
    """

    def __init__(
        self,
        config_path: Optional[Union[str, pathlib.Path]] = None,
        profile: str = "balanced",
        alert_callback: Optional[Any] = None
    ):
        self.detector = DetectorImprovementV3(config_path=config_path, profile=profile)
        self.alert_callback = alert_callback
        self.sr = 16000
        self.win_samples = 15360 # 0.96s
        self.hop_samples = 7680  # 0.48s
        self.buffer = np.zeros(0, dtype=np.float32)
        self.stream_position_sec = 0.0
        self.total_windows_processed = 0

    def ingest_audio(self, audio_chunk: np.ndarray) -> List[Dict[str, Any]]:
        """Ingests incoming audio samples and returns any triggered events."""
        if audio_chunk.ndim > 1:
            audio_chunk = np.mean(audio_chunk, axis=1)
        audio_chunk = audio_chunk.astype(np.float32)

        self.buffer = np.concatenate([self.buffer, audio_chunk])
        emitted_events = []

        while len(self.buffer) >= self.win_samples:
            window_audio = self.buffer[:self.win_samples]
            # Evaluate window through offline detector core
            res = self.detector.evaluate_waveform(window_audio)

            for ev in res["events"]:
                ev["stream_timestamp_s"] = self.stream_position_sec
                emitted_events.append(ev)
                if self.alert_callback:
                    try:
                        self.alert_callback(ev)
                    except Exception as ex:
                        logger.error(f"Error in alert callback: {ex}")

            # Advance by hop
            self.buffer = self.buffer[self.hop_samples:]
            self.stream_position_sec += (self.hop_samples / float(self.sr))
            self.total_windows_processed += 1

        return emitted_events
