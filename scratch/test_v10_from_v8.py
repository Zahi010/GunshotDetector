import sys
import pathlib
import pandas as pd
import soundfile as sf
import numpy as np

sys.path.insert(0, "e:/gunshot/gunshot")
from scratch.run_full_v9_evaluation import DetectorImprovementV9
from experiments.detector_improvement_v8.model_detector_improvement_v8 import (
    EventState,
    OperatingMode,
    PURE_GUN_CLASSES,
    GUN_CLASSES,
    BALLISTIC_CLASSES,
    FIREWORKS_CLASSES,
    THUNDER_CLASSES,
    IMPACT_CLASSES,
    GLASS_CLASSES,
    NON_TARGET_SEMANTIC_CLASSES
)

class DetectorImprovementV10(DetectorImprovementV9):
    def __init__(self, config_path=None):
        super().__init__(config_path)
        self.name = "detector_improvement_v10"
        self.version = "10.0.0"

    def evaluate_waveform(self, waveform: np.ndarray, sr: int = 16000):
        if waveform.ndim > 1: waveform = np.mean(waveform, axis=1)
        if sr != 16000:
            import librosa
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
            if m_min >= 0.65 and crest >= 12.0 and peak >= 0.20:
                cal_score = max(raw_score, m_mean)
            elif m_mean >= 0.70 and m_std < 0.12 and crest >= 12.0 and peak >= 0.20:
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
