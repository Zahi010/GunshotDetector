"""
Scratch experiment testing proposed V7 enhancements against V6 baseline:
1. Ballistic Shockwave override in pyrotechnic suppression
2. Ballistic protection in thunder suppression
3. Sub-bass ratio in backfire suppression
4. High-confidence crest factor threshold in UNKNOWN mode

RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.
"""

import os
import sys
import pathlib
sys.path.insert(0, "E:/gunshot/gunshot")
sys.path.insert(0, "E:/gunshot/gunshot/src")
os.chdir("E:/gunshot/gunshot")

import json
import numpy as np
import pandas as pd
import soundfile as sf
import librosa
import joblib

from experiments.detector_improvement_v6.model_detector_improvement_v6 import (
    DetectorImprovementV6,
    EventState,
    OperatingMode,
    GUN_CLASSES,
    BALLISTIC_CLASSES,
    FIREWORKS_CLASSES,
    THUNDER_CLASSES,
    IMPACT_CLASSES,
    NON_TARGET_SEMANTIC_CLASSES,
    PURE_GUN_CLASSES,
    CAP_GUN_CLASS
)

detector = DetectorImprovementV6()
fusion_model = detector.fusion_model

# Let's inspect Phase 19 field positives under V6 vs V7 logic
p19_dir = pathlib.Path("data/phase19_independent_positive/normalized_16k")
p19_files = sorted(list(p19_dir.glob("*.wav")))

def evaluate_v6_vs_v7_file(filepath):
    y, sr = sf.read(filepath)
    if y.ndim > 1: y = np.mean(y, axis=1)
    if sr != 16000: y = librosa.resample(y, orig_sr=sr, target_sr=16000)
    y = y.astype(np.float32)
    
    win_size = 15360
    hop_size = 7680
    if len(y) < win_size:
        y_proc = np.pad(y, (0, win_size - len(y)))
        n_wins = 1
    else:
        y_proc = y
        n_wins = 1 + int((len(y) - win_size) // hop_size)
        
    v6_detected = False
    v7_detected = False
    v6_max_adj = 0.0
    v7_max_adj = 0.0
    
    # Reset FSMs
    detector.reset()
    fsm_v6 = detector.fsm
    
    # We will instantiate a mock V7 FSM and suppressor
    cand_scores_v7 = []
    fsm_state_v7 = EventState.IDLE
    
    for w in range(n_wins):
        win = y_proc[w*hop_size : w*hop_size + win_size]
        feat, ys, acoustics = detector.extract_features(win)
        crest, flat, hi, mid, lo, m2l, rolloff, cent, rms, peak = acoustics
        mode, _, _ = detector.estimator.update(rolloff, hi, mid, lo, m2l, w * 0.48, w)
        raw_s = float(fusion_model.predict_proba(feat.reshape(1, -1))[:, 1][0])
        
        # --- V6 Suppression ---
        supp_v6 = detector.suppression.apply_suppression(raw_s, ys, acoustics)
        adj_v6 = supp_v6["adjusted_score"]
        v6_max_adj = max(v6_max_adj, adj_v6)
        st_v6, ev_v6 = fsm_v6.step(adj_v6, crest, w * 0.48, acoustics, mode)
        if ev_v6 is not None:
            v6_detected = True
            
        # --- Proposed V7 Suppression ---
        def _get_s(c):
            return float(ys.get(c, 0.0))
        gun_s = max(_get_s(cls) for cls in GUN_CLASSES)
        pure_gun = max(_get_s(cls) for cls in PURE_GUN_CLASSES)
        cap_gun_s = _get_s(CAP_GUN_CLASS)
        bal_s = max(_get_s(cls) for cls in BALLISTIC_CLASSES)
        fw_s = max(_get_s(cls) for cls in FIREWORKS_CLASSES)
        thun_s = max(_get_s(cls) for cls in THUNDER_CLASSES)
        imp_s = max(_get_s(cls) for cls in IMPACT_CLASSES)
        
        is_ballistic_shockwave = (bal_s >= 0.40 and bal_s >= fw_s * 0.85)
        
        adj_v7 = raw_s
        supp_v7 = False
        cat_v7 = "none"
        
        # 1. Zero energy
        if rms < 1e-4 or peak < 1e-3:
            adj_v7 = 0.0
            supp_v7 = True
            cat_v7 = "zero_energy_silence"
        
        # 2. Pyrotechnic Gating with Ballistic Shockwave Override
        if not supp_v7:
            if fw_s >= 0.45 and not is_ballistic_shockwave:
                if fw_s / (pure_gun + 1e-4) >= 1.8:
                    adj_v7 *= 0.15
                    supp_v7 = True
                    cat_v7 = "fireworks_dominant"
            elif fw_s >= 0.25 and not is_ballistic_shockwave:
                if fw_s / (pure_gun + 1e-4) >= 2.5:
                    adj_v7 *= 0.30
                    supp_v7 = True
                    cat_v7 = "pyrotechnic_ratio"
                    
        # 3. Sub-Bass Thud / Backfire Gating with Cap Gun Ratio
        if not supp_v7:
            if cap_gun_s >= 0.35 and (cap_gun_s >= pure_gun * 1.5 or pure_gun < 0.20) and lo >= 0.70:
                adj_v7 *= 0.25
                supp_v7 = True
                cat_v7 = "sub_bass_thud"
                
        # 4. Thunder Physical Rumble with Ballistic Protection
        if not supp_v7:
            is_thun_phys = (lo >= 0.65 and m2l < 0.55)
            # Only suppress if not ballistic shockwave and thunder semantics present OR pure gun very low
            if is_thun_phys and pure_gun < 0.15 and bal_s < 0.20:
                adj_v7 *= 0.30
                supp_v7 = True
                cat_v7 = "thunder_rumble"
                
        # 5. Mechanical Impact
        if not supp_v7:
            if imp_s >= 0.25 and imp_s / (pure_gun + 1e-4) >= 1.5 and pure_gun < 0.20:
                adj_v7 *= 0.35
                supp_v7 = True
                cat_v7 = "mechanical_impact"
                
        # 6. Ballistic Coherence
        if not supp_v7:
            if pure_gun < 0.08 and bal_s < 0.10:
                adj_v7 *= 0.20
                supp_v7 = True
                cat_v7 = "ballistic_incoherence"
                
        v7_max_adj = max(v7_max_adj, adj_v7)
        
        # --- Proposed V7 FSM Logic ---
        # UNKNOWN Mode: th_base=0.70, confirm_wins=2, allow_single=True
        # Single impulse allowed if crest >= 13.5 OR (score >= 0.85 and crest >= 11.5)
        single_allowed = (crest >= 13.5) or (adj_v7 >= 0.85 and crest >= 11.5)
        if mode == OperatingMode.CLEAR_NORMAL:
            single_allowed = (crest >= 12.0)
        elif mode == OperatingMode.DEGRADED_OCCLUDED:
            single_allowed = (crest >= 10.5)
            
        if fsm_state_v7 == EventState.IDLE:
            if single_allowed and adj_v7 >= 0.70:
                fsm_state_v7 = EventState.CONFIRMED
                v7_detected = True
            elif adj_v7 >= 0.70:
                fsm_state_v7 = EventState.CANDIDATE
                cand_scores_v7 = [adj_v7]
        elif fsm_state_v7 == EventState.CANDIDATE:
            if adj_v7 >= 0.70:
                cand_scores_v7.append(adj_v7)
                if len(cand_scores_v7) >= 2:
                    fsm_state_v7 = EventState.CONFIRMED
                    v7_detected = True
            elif adj_v7 < 0.40:
                fsm_state_v7 = EventState.IDLE
                cand_scores_v7 = []
                
    return {
        "v6_detected": v6_detected,
        "v7_detected": v7_detected,
        "v6_peak": v6_max_adj,
        "v7_peak": v7_max_adj
    }

print("\n--- Testing Phase 19 Field Recordings (23 files) ---")
p19_v6_hits = 0
p19_v7_hits = 0
for fpath in p19_files:
    res = evaluate_v6_vs_v7_file(str(fpath))
    if res["v6_detected"]: p19_v6_hits += 1
    if res["v7_detected"]: p19_v7_hits += 1
    if not res["v6_detected"] and res["v7_detected"]:
        print(f"RECOVERED in V7: {fpath.stem} (V6={res['v6_peak']:.4f} -> V7={res['v7_peak']:.4f})")
    elif res["v6_detected"] and not res["v7_detected"]:
        print(f"REGRESSION in V7: {fpath.stem}")

print(f"Phase 19 Recall: V6 = {p19_v6_hits}/23 ({p19_v6_hits/23*100:.1f}%) | V7 = {p19_v7_hits}/23 ({p19_v7_hits/23*100:.1f}%)")
