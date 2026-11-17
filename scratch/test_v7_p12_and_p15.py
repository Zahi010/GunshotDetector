"""
Test proposed V7 improvements on Phase 12 and Phase 15 holdouts, plus Phase 12 continuous stream.
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

def evaluate_v6_vs_v7_waveform(y, sr=16000):
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
    v7_events = 0
    v6_events = 0
    
    detector.reset()
    fsm_v6 = detector.fsm
    cand_scores_v7 = []
    fsm_state_v7 = EventState.IDLE
    
    for w in range(n_wins):
        win = y_proc[w*hop_size : w*hop_size + win_size]
        feat, ys, acoustics = detector.extract_features(win)
        crest, flat, hi, mid, lo, m2l, rolloff, cent, rms, peak = acoustics
        mode, _, _ = detector.estimator.update(rolloff, hi, mid, lo, m2l, w * 0.48, w)
        raw_s = float(fusion_model.predict_proba(feat.reshape(1, -1))[:, 1][0])
        
        # --- V6 ---
        supp_v6 = detector.suppression.apply_suppression(raw_s, ys, acoustics, fsm_v6.state == EventState.CONFIRMED)
        adj_v6 = supp_v6["adjusted_score"]
        v6_max_adj = max(v6_max_adj, adj_v6)
        st_v6, ev_v6 = fsm_v6.step(adj_v6, crest, w * 0.48, acoustics, mode)
        if ev_v6 is not None:
            v6_detected = True
            v6_events += 1
            
        # --- Proposed V7 ---
        def _get_s(c): return float(ys.get(c, 0.0))
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
        
        if rms < 1e-4 or peak < 1e-3:
            adj_v7 = 0.0
            supp_v7 = True
            cat_v7 = "zero_energy_silence"
            
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
                    
        if not supp_v7:
            # Backfire / Sub-bass discrimination
            if cap_gun_s >= 0.35 and (cap_gun_s >= pure_gun * 1.5 or pure_gun < 0.20) and lo >= 0.70:
                adj_v7 *= 0.25
                supp_v7 = True
                cat_v7 = "sub_bass_thud"
                
        if not supp_v7:
            # Thunder physical rumble with ballistic shockwave protection
            is_thun_phys = (lo >= 0.65 and m2l < 0.55)
            if is_thun_phys and pure_gun < 0.15 and bal_s < 0.20:
                adj_v7 *= 0.30
                supp_v7 = True
                cat_v7 = "thunder_rumble"
                
        if not supp_v7:
            if imp_s >= 0.25 and imp_s / (pure_gun + 1e-4) >= 1.5 and pure_gun < 0.20:
                adj_v7 *= 0.35
                supp_v7 = True
                cat_v7 = "mechanical_impact"
                
        if not supp_v7:
            if pure_gun < 0.08 and bal_s < 0.10:
                adj_v7 *= 0.20
                supp_v7 = True
                cat_v7 = "ballistic_incoherence"
                
        v7_max_adj = max(v7_max_adj, adj_v7)
        
        # V7 FSM
        single_allowed = (crest >= 13.5) or (adj_v7 >= 0.85 and crest >= 11.5)
        if mode == OperatingMode.CLEAR_NORMAL:
            single_allowed = (crest >= 12.0)
        elif mode == OperatingMode.DEGRADED_OCCLUDED:
            single_allowed = (crest >= 10.5)
            
        if fsm_state_v7 == EventState.IDLE:
            if single_allowed and adj_v7 >= 0.70:
                fsm_state_v7 = EventState.CONFIRMED
                v7_detected = True
                v7_events += 1
            elif adj_v7 >= 0.70:
                fsm_state_v7 = EventState.CANDIDATE
                cand_scores_v7 = [adj_v7]
        elif fsm_state_v7 == EventState.CANDIDATE:
            if adj_v7 >= 0.70:
                cand_scores_v7.append(adj_v7)
                if len(cand_scores_v7) >= 2:
                    fsm_state_v7 = EventState.CONFIRMED
                    v7_detected = True
                    v7_events += 1
            elif adj_v7 < 0.40:
                fsm_state_v7 = EventState.IDLE
                cand_scores_v7 = []
        elif fsm_state_v7 == EventState.CONFIRMED:
            if adj_v7 < 0.40:
                fsm_state_v7 = EventState.IDLE
                cand_scores_v7 = []
                
    return {
        "v6_detected": v6_detected,
        "v7_detected": v7_detected,
        "v6_peak": v6_max_adj,
        "v7_peak": v7_max_adj,
        "v6_events": v6_events,
        "v7_events": v7_events
    }

# 1. Phase 12 Discrete
p12_manifest = pd.read_csv("data/phase12_independent_test/manifest.csv")
p12_discrete = p12_manifest[~p12_manifest["recording_id"].str.contains("continuous", case=False)].copy()

p12_pos = p12_discrete[p12_discrete["ground_truth_gunshot"] == 1]
p12_neg = p12_discrete[p12_discrete["ground_truth_gunshot"] == 0]

print(f"\nEvaluating Phase 12 Discrete ({len(p12_discrete)} files: {len(p12_pos)} pos, {len(p12_neg)} neg)...")
p12_v6_hits, p12_v7_hits = 0, 0
p12_v6_fas, p12_v7_fas = 0, 0

for _, r in p12_pos.iterrows():
    y, sr = sf.read(r["filepath"])
    res = evaluate_v6_vs_v7_waveform(y, sr)
    if res["v6_detected"]: p12_v6_hits += 1
    if res["v7_detected"]: p12_v7_hits += 1
    if not res["v6_detected"] and res["v7_detected"]:
        print(f"  P12 RECOVERED: {r['recording_id']} ({r['condition_category']}) V6={res['v6_peak']:.4f} -> V7={res['v7_peak']:.4f}")

for _, r in p12_neg.iterrows():
    y, sr = sf.read(r["filepath"])
    res = evaluate_v6_vs_v7_waveform(y, sr)
    if res["v6_detected"]: p12_v6_fas += 1
    if res["v7_detected"]: p12_v7_fas += 1
    if not res["v6_detected"] and res["v7_detected"]:
        print(f"  P12 NEW FA: {r['recording_id']} ({r['event_classification']})")
    elif res["v6_detected"] and not res["v7_detected"]:
        print(f"  P12 FA ELIMINATED: {r['recording_id']}")

print(f"Phase 12 Discrete Positive Recall: V6 = {p12_v6_hits}/{len(p12_pos)} ({p12_v6_hits/len(p12_pos)*100:.1f}%) | V7 = {p12_v7_hits}/{len(p12_pos)} ({p12_v7_hits/len(p12_pos)*100:.1f}%)")
print(f"Phase 12 Discrete False Alarms: V6 = {p12_v6_fas}/{len(p12_neg)} | V7 = {p12_v7_fas}/{len(p12_neg)}")

# 2. Phase 12 Continuous Stream (sampled blocks)
p12_cont_path = "data/phase12_independent_test/continuous_ambient/phase12_continuous_stream_01_urban_and_environmental_2hr.wav"
print("\nEvaluating Phase 12 Continuous Stream...")
cont_v6_events, cont_v7_events = 0, 0
block_len = 16000 * 30
sample_stride = 10
with sf.SoundFile(p12_cont_path) as f:
    tot_samples = f.frames
    tested = 0
    blk_cnt = 0
    while f.tell() < tot_samples:
        block = f.read(block_len, dtype='float32')
        if len(block) == 0: break
        if blk_cnt % sample_stride == 0:
            res = evaluate_v6_vs_v7_waveform(block, 16000)
            cont_v6_events += res["v6_events"]
            cont_v7_events += res["v7_events"]
        blk_cnt += 1

print(f"Phase 12 Continuous Stream Alerts: V6 = {cont_v6_events} | V7 = {cont_v7_events}")

