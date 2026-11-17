"""
# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.
#
# Phase 30 Diagnostic Instrumented Detection Architecture
# Non-invasive, mathematically invariant intermediate state tracer
# for acoustic gunshot detection baseline verification and suppression forensics.
#
# This software is an experimental ML research demonstration prototype.
# NEVER deploy for autonomous emergency dispatch, tactical police response,
# active-shooter alerting, automated evacuation, or life-critical security.
"""

import os
import sys
import math
import time
import gc
from typing import Dict, List, Any, Tuple, Optional
import numpy as np
import pandas as pd

# Import project configuration and frozen modules without modifying them
import config
from model import load_model_bundle
from feature_extractor import YAMNetFeatureExtractor
from model_phase14 import (
    compute_physical_crest_factor_db,
    merge_phase14_events,
    _create_phase14_event_record,
    YAMNET_CLASS_GUNSHOT,
    YAMNET_CLASS_MACHINE_GUN,
    YAMNET_CLASS_ARTILLERY,
    YAMNET_CLASS_CAP_GUN,
    YAMNET_CLASS_THUNDERSTORM,
    YAMNET_CLASS_THUNDER,
    YAMNET_CLASS_FIREWORKS,
    YAMNET_CLASS_FIRECRACKER,
    YAMNET_CLASS_DOG,
    YAMNET_CLASS_BARK,
    YAMNET_CLASS_YIP,
    YAMNET_CLASS_CANIDAE,
    YAMNET_CLASS_FIRE,
    YAMNET_CLASS_CRACKLE,
    YAMNET_CLASS_POLICE_CAR,
    YAMNET_CLASS_AMBULANCE,
    YAMNET_CLASS_FIRE_ENGINE,
    YAMNET_CLASS_SIREN,
    YAMNET_CLASS_CIVIL_DEFENSE
)
from model_phase17 import (
    merge_phase17_events,
    YAMNET_ANIMAL_CLASSES
)

class InstrumentedDetector:
    """
    Diagnostic Instrumentation Layer for Phase 14 Balanced & Phase 17 Experimental.
    Strictly preserves mathematical invariance while logging full intermediate traces:
    - Window timestamps and sub-window feature states
    - Raw ensemble scores
    - Phase 14 semantic gating scores and suppression reasons
    - Animal classifier outputs and suppression activation states
    - Applied suppression penalties (0.30x vs 1.0x)
    - Post-suppression Phase 17 scores
    - Hysteresis states: in_event, had_decayed, active_cluster, cooldown_until
    - Assertion, maintenance, and termination decisions
    """

    def __init__(self, models_dir: Optional[str] = None):
        self.fe = YAMNetFeatureExtractor()
        bundle_dir = models_dir or (config.MODELS_DIR / "gunshot_yamnet_bundle")
        self.ensemble_model, self.bundle_info = load_model_bundle(bundle_dir)

        # Frozen threshold constants common to both detectors
        self.threshold_base = 0.75
        self.threshold_high = 0.88
        self.threshold_off = 0.48
        self.confirm_windows = 2
        self.cooldown_secs = 2.0
        self.min_crest_factor_db = 8.8
        self.single_win_min_crest_db = 12.0

        # Phase 17 animal suppression constants
        self.animal_thresh = 0.35
        self.animal_ratio = 2.0
        self.animal_penalty = 0.30

    def process_waveform(
        self,
        waveform: np.ndarray,
        recording_id: str,
        sample_rate: int = 16000,
        crest_factor_db: Optional[float] = None,
        allow_short_clip_exception: bool = True
    ) -> Dict[str, Any]:
        """
        Execute instrumented inference over continuous waveform.
        Computes Phase 14, Phase 17, and analytical Counterfactual (Phase 17 without animal suppression).
        """
        dur_s = len(waveform) / float(sample_rate)
        if crest_factor_db is None:
            crest_factor_db = compute_physical_crest_factor_db(waveform)

        import tensorflow as tf
        tensor = tf.convert_to_tensor(waveform, dtype=tf.float32)
        yamnet_scores, embeddings, _ = self.fe.model(tensor)
        yamnet_scores = yamnet_scores.numpy()
        embeddings = embeddings.numpy()
        del tensor

        n_windows = len(embeddings)
        raw_scores = self.ensemble_model.predict(embeddings, verbose=0).flatten()

        hop_sec = config.HOP_SAMPLES / float(sample_rate)
        win_sec = config.WINDOW_SAMPLES / float(sample_rate)

        p14_windows = []
        p17_windows = []
        p17_cf_windows = [] # Counterfactual: Phase 17 without animal suppression

        sub_window_traces = []

        # Iterate over all windows and extract intermediate states
        for w_idx in range(n_windows):
            st = round(w_idx * hop_sec, 3)
            et = round(st + win_sec, 3)
            r_score = float(raw_scores[w_idx])

            # Semantic class outputs
            gun_s = max(
                yamnet_scores[w_idx, YAMNET_CLASS_GUNSHOT],
                yamnet_scores[w_idx, YAMNET_CLASS_MACHINE_GUN],
                yamnet_scores[w_idx, YAMNET_CLASS_ARTILLERY],
                yamnet_scores[w_idx, YAMNET_CLASS_CAP_GUN]
            )
            thun_s = max(
                yamnet_scores[w_idx, YAMNET_CLASS_THUNDERSTORM],
                yamnet_scores[w_idx, YAMNET_CLASS_THUNDER]
            )
            fire_s = max(
                yamnet_scores[w_idx, YAMNET_CLASS_FIREWORKS],
                yamnet_scores[w_idx, YAMNET_CLASS_FIRECRACKER]
            )
            dog_s = max(
                yamnet_scores[w_idx, YAMNET_CLASS_DOG],
                yamnet_scores[w_idx, YAMNET_CLASS_BARK],
                yamnet_scores[w_idx, YAMNET_CLASS_YIP],
                yamnet_scores[w_idx, YAMNET_CLASS_CANIDAE]
            )
            crackle_s = max(
                yamnet_scores[w_idx, YAMNET_CLASS_FIRE],
                yamnet_scores[w_idx, YAMNET_CLASS_CRACKLE]
            )
            siren_s = max(
                yamnet_scores[w_idx, YAMNET_CLASS_POLICE_CAR],
                yamnet_scores[w_idx, YAMNET_CLASS_AMBULANCE],
                yamnet_scores[w_idx, YAMNET_CLASS_FIRE_ENGINE],
                yamnet_scores[w_idx, YAMNET_CLASS_SIREN],
                yamnet_scores[w_idx, YAMNET_CLASS_CIVIL_DEFENSE]
            )

            # Phase 14 semantic gating
            p14_score = r_score
            supp14 = None
            if thun_s > 0.25 and thun_s >= gun_s * 1.5:
                p14_score *= 0.30
                supp14 = "thunder"
            elif fire_s > 0.35 and fire_s >= gun_s * 2.0 and gun_s < 0.05:
                p14_score *= 0.35
                supp14 = "fireworks"
            elif dog_s > 0.30 and dog_s >= gun_s * 1.5:
                p14_score *= 0.35
                supp14 = "dog_bark"
            elif crackle_s > 0.25 and crackle_s >= gun_s * 1.5:
                p14_score *= 0.40
                supp14 = "crackle"
            elif siren_s > 0.30 and siren_s >= gun_s * 1.5:
                p14_score *= 0.40
                supp14 = "siren"

            p14_windows.append({
                "window_index": w_idx,
                "start_time": st,
                "end_time": et,
                "score": round(p14_score, 4),
                "raw_score": round(r_score, 4),
                "suppressed": supp14 is not None,
                "suppression_reason": supp14
            })

            # Counterfactual Phase 17 without animal suppression
            p17_cf_windows.append({
                "window_index": w_idx,
                "start_time": st,
                "end_time": et,
                "score": round(p14_score, 4),
                "raw_ensemble_score": round(r_score, 4),
                "suppressed": supp14 is not None,
                "suppression_reason": supp14
            })

            # Phase 17 animal suppression logic
            p17_score = p14_score
            supp17 = supp14
            animal_s = max(yamnet_scores[w_idx, cls_idx] for cls_idx in YAMNET_ANIMAL_CLASSES)
            animal_supp_active = False
            penalty_applied = 1.0

            if animal_s > self.animal_thresh and animal_s >= gun_s * self.animal_ratio:
                animal_supp_active = True
                penalty_applied = self.animal_penalty
                p17_score *= self.animal_penalty
                supp17 = "animal_vocalization"

            p17_windows.append({
                "window_index": w_idx,
                "start_time": st,
                "end_time": et,
                "score": round(p17_score, 4),
                "raw_ensemble_score": round(r_score, 4),
                "suppressed": supp17 is not None,
                "suppression_reason": supp17
            })

            # Record detailed trace
            sub_window_traces.append({
                "recording_id": recording_id,
                "window_index": w_idx,
                "start_time_s": st,
                "end_time_s": et,
                "raw_score": round(r_score, 4),
                "gun_semantic_score": round(float(gun_s), 4),
                "animal_semantic_score": round(float(animal_s), 4),
                "thunder_score": round(float(thun_s), 4),
                "fireworks_score": round(float(fire_s), 4),
                "dog_score": round(float(dog_s), 4),
                "siren_score": round(float(siren_s), 4),
                "p14_score": round(p14_score, 4),
                "p14_suppression_reason": supp14,
                "animal_suppression_active": animal_supp_active,
                "animal_suppression_penalty": penalty_applied,
                "p17_score": round(p17_score, 4),
                "p17_suppression_reason": supp17,
                "threshold_base": self.threshold_base,
                "threshold_high": self.threshold_high,
                "threshold_off": self.threshold_off
            })

        # Run official event mergers to obtain canonical event sets
        p14_events = merge_phase14_events(
            p14_windows,
            threshold_base=self.threshold_base,
            threshold_high=self.threshold_high,
            threshold_off=self.threshold_off,
            confirm_windows=self.confirm_windows,
            cooldown_secs=self.cooldown_secs,
            audio_duration_sec=dur_s,
            allow_short_clip_exception=allow_short_clip_exception,
            crest_factor_db=crest_factor_db,
            min_crest_factor_db=self.min_crest_factor_db,
            single_win_min_crest_db=self.single_win_min_crest_db
        )

        p17_events = merge_phase17_events(
            p17_windows,
            threshold_base=self.threshold_base,
            threshold_high=self.threshold_high,
            threshold_off=self.threshold_off,
            confirm_windows=self.confirm_windows,
            cooldown_secs=self.cooldown_secs,
            audio_duration_sec=dur_s,
            allow_short_clip_exception=allow_short_clip_exception,
            crest_factor_db=crest_factor_db,
            min_crest_factor_db=self.min_crest_factor_db,
            single_win_min_crest_db=self.single_win_min_crest_db
        )

        p17_cf_events = merge_phase17_events(
            p17_cf_windows,
            threshold_base=self.threshold_base,
            threshold_high=self.threshold_high,
            threshold_off=self.threshold_off,
            confirm_windows=self.confirm_windows,
            cooldown_secs=self.cooldown_secs,
            audio_duration_sec=dur_s,
            allow_short_clip_exception=allow_short_clip_exception,
            crest_factor_db=crest_factor_db,
            min_crest_factor_db=self.min_crest_factor_db,
            single_win_min_crest_db=self.single_win_min_crest_db
        )

        # Trace state transitions step by step
        has_sharp_crest = (crest_factor_db is None or crest_factor_db >= self.single_win_min_crest_db)

        # Instrument Phase 14 State Machine
        p14_in_event = False
        p14_had_decayed = True
        p14_cooldown_until = -1.0
        p14_active_cluster = []
        p14_event_idx = 0

        # Instrument Phase 17 State Machine
        p17_in_event = False
        p17_had_decayed = True
        p17_cooldown_until = -1.0
        p17_active_cluster = []
        p17_event_idx = 0

        for w_idx in range(n_windows):
            tr = sub_window_traces[w_idx]
            st = tr["start_time_s"]
            p14_sc = tr["p14_score"]
            p17_sc = tr["p17_score"]

            # --- Phase 14 state machine step ---
            p14_qualifies_immediate = (p14_sc >= self.threshold_high and has_sharp_crest)
            p14_asserted = False
            p14_terminated = False
            p14_event_label = None

            if not p14_in_event:
                if p14_sc < self.threshold_off:
                    p14_had_decayed = True

                if st < p14_cooldown_until:
                    if p14_had_decayed and (p14_qualifies_immediate or p14_sc >= self.threshold_base):
                        p14_active_cluster.append(p14_windows[w_idx])
                        if p14_qualifies_immediate or len(p14_active_cluster) >= self.confirm_windows:
                            p14_in_event = True
                            p14_had_decayed = False
                            p14_asserted = True
                            p14_event_idx += 1
                else:
                    if p14_qualifies_immediate:
                        p14_active_cluster = [p14_windows[w_idx]]
                        p14_in_event = True
                        p14_had_decayed = False
                        p14_asserted = True
                        p14_event_idx += 1
                    elif p14_sc >= self.threshold_base:
                        p14_active_cluster.append(p14_windows[w_idx])
                        if len(p14_active_cluster) >= self.confirm_windows:
                            p14_in_event = True
                            p14_had_decayed = False
                            p14_asserted = True
                            p14_event_idx += 1
                    else:
                        p14_active_cluster = []
            else:
                if p14_sc >= self.threshold_off:
                    p14_active_cluster.append(p14_windows[w_idx])
                else:
                    p14_terminated = True
                    p14_cooldown_until = max(w["end_time"] for w in p14_active_cluster) + self.cooldown_secs
                    p14_active_cluster = []
                    p14_in_event = False
                    p14_had_decayed = True

            if p14_in_event:
                p14_event_label = f"P14-EV-{p14_event_idx:03d}"

            tr["p14_in_event"] = p14_in_event
            tr["p14_had_decayed"] = p14_had_decayed
            tr["p14_cooldown_until_s"] = round(p14_cooldown_until, 3)
            tr["p14_alert_asserted"] = p14_asserted
            tr["p14_alert_terminated"] = p14_terminated
            tr["p14_active_event_id"] = p14_event_label

            # --- Phase 17 state machine step ---
            p17_qualifies_immediate = (p17_sc >= self.threshold_high and has_sharp_crest)
            p17_asserted = False
            p17_terminated = False
            p17_event_label = None

            if not p17_in_event:
                if p17_sc < self.threshold_off:
                    p17_had_decayed = True

                if st < p17_cooldown_until:
                    if p17_had_decayed and (p17_qualifies_immediate or p17_sc >= self.threshold_base):
                        p17_active_cluster.append(p17_windows[w_idx])
                        if p17_qualifies_immediate or len(p17_active_cluster) >= self.confirm_windows:
                            p17_in_event = True
                            p17_had_decayed = False
                            p17_asserted = True
                            p17_event_idx += 1
                else:
                    if p17_qualifies_immediate:
                        p17_active_cluster = [p17_windows[w_idx]]
                        p17_in_event = True
                        p17_had_decayed = False
                        p17_asserted = True
                        p17_event_idx += 1
                    elif p17_sc >= self.threshold_base:
                        p17_active_cluster.append(p17_windows[w_idx])
                        if len(p17_active_cluster) >= self.confirm_windows:
                            p17_in_event = True
                            p17_had_decayed = False
                            p17_asserted = True
                            p17_event_idx += 1
                    else:
                        p17_active_cluster = []
            else:
                if p17_sc >= self.threshold_off:
                    p17_active_cluster.append(p17_windows[w_idx])
                else:
                    p17_terminated = True
                    p17_cooldown_until = max(w["end_time"] for w in p17_active_cluster) + self.cooldown_secs
                    p17_active_cluster = []
                    p17_in_event = False
                    p17_had_decayed = True

            if p17_in_event:
                p17_event_label = f"P17-EV-{p17_event_idx:03d}"

            tr["p17_in_event"] = p17_in_event
            tr["p17_had_decayed"] = p17_had_decayed
            tr["p17_cooldown_until_s"] = round(p17_cooldown_until, 3)
            tr["p17_alert_asserted"] = p17_asserted
            tr["p17_alert_terminated"] = p17_terminated
            tr["p17_active_event_id"] = p17_event_label

        return {
            "recording_id": recording_id,
            "duration_s": dur_s,
            "crest_factor_db": crest_factor_db,
            "p14_events": p14_events,
            "p17_events": p17_events,
            "p17_cf_events": p17_cf_events,
            "sub_window_traces": sub_window_traces
        }

