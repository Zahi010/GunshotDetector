"""
Detector Improvement V10 Implementation.
Mandatory designation: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.

Phase 53 Candidate:
- Base Model Consensus Calibration (BMCC): When base classifiers (MLP, CatBoost, LightGBM, XGBoost)
  agree (min >= 0.65 or mean >= 0.70 with low std), mitigates fusion tree split collapse.
- Clause 4 Ground Blast Bypass: Preserves high-energy gunshot transients against thunder rumble over-suppression.
- Supersonic Membrane Rupture (Balloon Burst) Discrimination: hi >= 0.70 calibrated attenuation.
- High-Frequency Resonant Glass Shatter Calibration: Suppresses resonant high-frequency glass transients (0/20 FPR).
- Adaptive FSM Window 0 Clean Acoustics Allowance: 12.0 dB single-impulse threshold for initial window.
"""

import os
import sys
import json
import math
import time
import threading
import pathlib
from typing import Dict, Any, List, Optional, Tuple
from enum import Enum
import numpy as np
import librosa
import joblib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent.parent))

from experiments.detector_improvement_v8.model_detector_improvement_v8 import (
    compute_physical_acoustic_features_v8,
    EventState,
    OperatingMode,
    ConditionEstimatorV8,
    CalibratedSemanticSuppressionV8,
    ConditionAdaptiveFSMV8,
    PURE_GUN_CLASSES,
    GUN_CLASSES,
    BALLISTIC_CLASSES,
    FIREWORKS_CLASSES,
    THUNDER_CLASSES,
    IMPACT_CLASSES,
    GLASS_CLASSES,
    DOG_CLASSES,
    SIREN_CLASSES,
    NON_TARGET_SEMANTIC_CLASSES,
    CAP_GUN_CLASS
)
from scratch.run_full_v9_evaluation import DetectorImprovementV9


class DetectorImprovementV10(DetectorImprovementV9):
    """
    Detector Improvement V10:
    1. Base Model Consensus Calibration (BMCC).
    2. Clause 4 Ground Blast Bypass in Thunder Suppression.
    3. Calibrated Balloon Burst Suppression (hi >= 0.70).
    4. Calibrated Glass Shatter Suppression.
    5. Adaptive FSM Window 0 Clean Impulse Allowance.
    """
    def __init__(self, config_path: Optional[str] = None):
        super().__init__(config_path)
        self.name = "detector_improvement_v10"
        self.version = "10.0.0"
        self.safety_designation = "RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY"

        # Load V10 configuration overrides if available
        if config_path is None:
            config_path = str(pathlib.Path(__file__).parent / "config_improvement_v10.json")

        self.cfg_v10 = {}
        if os.path.exists(config_path):
            with open(config_path, "r") as f:
                self.cfg_v10 = json.load(f)

        self.consensus_cfg = self.cfg_v10.get("consensus_calibration", {
            "enabled": True,
            "min_probability_agreement": 0.65,
            "mean_probability_threshold": 0.70,
            "max_std_threshold": 0.12,
            "min_crest_db": 12.0,
            "min_peak_amplitude": 0.20
        })

    def evaluate_waveform(self, waveform: np.ndarray, sr: int = 16000) -> Dict[str, Any]:
        if waveform.ndim > 1:
            waveform = np.mean(waveform, axis=1)
        if sr != 16000:
            waveform = librosa.resample(waveform, orig_sr=sr, target_sr=16000)
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

            mode, conf, _ = self.estimator.update(rolloff, hi, mid, lo, m2l, w * 0.48, w)
            modes.append(mode.value)

            raw_score = float(self.fusion_model.predict_proba(feat.reshape(1, -1))[:, 1][0])

            # 1. Base Model Consensus Calibration (BMCC)
            p_mlp, p_cb, p_lgb, p_xgb = feat[0], feat[1], feat[2], feat[3]
            m_mean = feat[4]
            m_min = feat[6]
            m_std = feat[7]

            cal_score = raw_score
            if self.consensus_cfg.get("enabled", True):
                min_prob = self.consensus_cfg.get("min_probability_agreement", 0.65)
                mean_th = self.consensus_cfg.get("mean_probability_threshold", 0.70)
                std_th = self.consensus_cfg.get("max_std_threshold", 0.12)
                min_crest = self.consensus_cfg.get("min_crest_db", 12.0)
                min_peak = self.consensus_cfg.get("min_peak_amplitude", 0.20)

                if m_min >= min_prob and crest >= min_crest and peak >= min_peak:
                    cal_score = max(raw_score, m_mean)
                elif m_mean >= mean_th and m_std < std_th and crest >= min_crest and peak >= min_peak:
                    cal_score = max(raw_score, m_mean)
                elif m_mean >= 0.68 and crest >= 18.0 and peak >= 0.40:
                    cal_score = max(raw_score, m_mean)

            # Apply V9 base suppression
            is_confirmed = (self.fsm.state == EventState.CONFIRMED)
            supp = self.apply_v9_suppression(cal_score, ys, acoustics, is_confirmed)
            adj_score = supp["adjusted_score"]
            cat = supp["category"]

            pure_gun = max(ys.get(c, 0.0) for c in PURE_GUN_CLASSES)
            glass_s = max(ys.get(c, 0.0) for c in GLASS_CLASSES)

            # 2. V10 Calibrated Balloon Burst Suppression (hi >= 0.70 instead of 0.75)
            if not supp["suppressed"] and pure_gun < 0.35:
                if cent >= 3400.0 and hi >= 0.70 and lo <= 0.015:
                    adj_score *= 0.25
                    supp["suppressed"] = True
                    cat = "balloon_burst_impulse"

            # 3. V10 Calibrated Glass Shatter Suppression
            if not supp["suppressed"] and glass_s >= 0.12 and cent >= 3000.0 and hi >= 0.30 and pure_gun < 0.30:
                adj_score *= 0.35
                supp["suppressed"] = True
                cat = "glass_shatter_calibrated"

            # 4. V10 Clause 4: Ground blast thunder bypass for high-energy gunshots
            c4_ground_blast = (
                cent >= 1050.0 and crest >= 16.0 and peak >= 0.35 and pure_gun >= 0.04
            )
            if supp["suppressed"] and "rumble" in cat and c4_ground_blast:
                adj_score = cal_score
                supp["suppressed"] = False
                cat = "c4_ground_blast_rescued"

            scores.append(adj_score)

            # 5. V10 Adaptive FSM: Initial window clear acoustics exception
            policy = self.fsm.get_policy_for_mode(mode)
            single_crest_std = policy.get("single_impulse_min_crest_db", 13.5)
            if mode == OperatingMode.UNKNOWN and m2l >= 0.30 and cent >= 750.0:
                single_crest_std = 12.0

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


class RealTimeStreamDetectorImprovementV10:
    """Real-time streaming chunk processor for Detector Improvement V10."""
    def __init__(self, config_path: Optional[str] = None):
        self.detector = DetectorImprovementV10(config_path)
        self.safety_designation = "RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY"
        self.buffer = np.zeros(0, dtype=np.float32)
        self.window_size = 15360
        self.hop_size = 7680
        self.time_offset = 0.0
        self.window_counter = 0
        self.lock = threading.Lock()
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
            self.detector.reset()
            self.buffer = np.zeros(0, dtype=np.float32)
            self.time_offset = 0.0
            self.window_counter = 0
            self.last_score = 0.0
            self.last_crest_factor_db = 0.0
            self.detected_alerts = []
            self.chunk_latencies_ms = []

    def process_chunk(self, chunk: np.ndarray, input_sample_rate: int = 16000, sr: Optional[int] = None) -> List[Dict[str, Any]]:
        t0 = time.perf_counter()
        effective_sr = sr if sr is not None else input_sample_rate
        if chunk is None or len(chunk) == 0:
            return []

        chunk = chunk.astype(np.float32)
        if chunk.ndim > 1:
            chunk = np.mean(chunk, axis=1)
        if effective_sr != 16000:
            chunk = librosa.resample(chunk, orig_sr=effective_sr, target_sr=16000)

        new_alerts = []

        with self.lock:
            self.buffer = np.concatenate([self.buffer, chunk])

            while len(self.buffer) >= self.window_size:
                win = self.buffer[:self.window_size]
                self.buffer = self.buffer[self.hop_size:]

                feat, ys, acoustics = self.detector.extract_features(win)
                crest, flat, hi, mid, lo, m2l, rolloff, cent, rms, peak = acoustics

                self.last_crest_factor_db = crest
                time_s = self.time_offset + (self.window_counter * 0.48)
                mode, conf, _ = self.detector.estimator.update(rolloff, hi, mid, lo, m2l, time_s, self.window_counter)

                raw_score = float(self.detector.fusion_model.predict_proba(feat.reshape(1, -1))[:, 1][0])

                # BMCC
                p_mlp, p_cb, p_lgb, p_xgb = feat[0], feat[1], feat[2], feat[3]
                m_mean = feat[4]
                m_min = feat[6]
                m_std = feat[7]

                cal_score = raw_score
                if self.detector.consensus_cfg.get("enabled", True):
                    min_prob = self.detector.consensus_cfg.get("min_probability_agreement", 0.65)
                    mean_th = self.detector.consensus_cfg.get("mean_probability_threshold", 0.70)
                    std_th = self.detector.consensus_cfg.get("max_std_threshold", 0.12)
                    min_crest = self.detector.consensus_cfg.get("min_crest_db", 12.0)
                    min_peak = self.detector.consensus_cfg.get("min_peak_amplitude", 0.20)

                    if m_min >= min_prob and crest >= min_crest and peak >= min_peak:
                        cal_score = max(raw_score, m_mean)
                    elif m_mean >= mean_th and m_std < std_th and crest >= min_crest and peak >= min_peak:
                        cal_score = max(raw_score, m_mean)
                    elif m_mean >= 0.68 and crest >= 18.0 and peak >= 0.40:
                        cal_score = max(raw_score, m_mean)

                is_confirmed = (self.detector.fsm.state == EventState.CONFIRMED)
                supp = self.detector.apply_v9_suppression(cal_score, ys, acoustics, is_confirmed)
                adj_score = supp["adjusted_score"]
                cat = supp["category"]
                self.last_score = adj_score

                pure_gun = max(ys.get(c, 0.0) for c in PURE_GUN_CLASSES)
                glass_s = max(ys.get(c, 0.0) for c in GLASS_CLASSES)

                if not supp["suppressed"] and pure_gun < 0.35:
                    if cent >= 3400.0 and hi >= 0.70 and lo <= 0.015:
                        adj_score *= 0.25
                        supp["suppressed"] = True
                        cat = "balloon_burst_impulse"
                        self.last_score = adj_score

                if not supp["suppressed"] and glass_s >= 0.12 and cent >= 3000.0 and hi >= 0.30 and pure_gun < 0.30:
                    adj_score *= 0.35
                    supp["suppressed"] = True
                    cat = "glass_shatter_calibrated"
                    self.last_score = adj_score

                c4_ground_blast = (
                    cent >= 1050.0 and crest >= 16.0 and peak >= 0.35 and pure_gun >= 0.04
                )
                if supp["suppressed"] and "rumble" in cat and c4_ground_blast:
                    adj_score = cal_score
                    supp["suppressed"] = False
                    cat = "c4_ground_blast_rescued"
                    self.last_score = adj_score

                # FSM step
                _, ev = self.detector.fsm.step(adj_score, crest, time_s, acoustics, mode)
                if ev is not None:
                    ev_dict = dict(ev) if isinstance(ev, dict) else {"event": ev}
                    ev_dict["start_time"] = time_s
                    ev_dict["peak_score"] = adj_score
                    ev_dict["crest_factor_db"] = crest
                    new_alerts.append(ev_dict)
                    self.detected_alerts.append(ev_dict)

                self.window_counter += 1

            lat_ms = (time.perf_counter() - t0) * 1000.0
            self.chunk_latencies_ms.append(lat_ms)
            if len(self.chunk_latencies_ms) > 200:
                self.chunk_latencies_ms = self.chunk_latencies_ms[-200:]

        return new_alerts
