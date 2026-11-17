import sys
import pathlib
import pandas as pd
import soundfile as sf
import numpy as np
import librosa

sys.path.insert(0, "e:/gunshot/gunshot")
from experiments.detector_improvement_v9.model_detector_improvement_v9 import (
    compute_physical_acoustic_features_v9,
    EventState,
    OperatingMode,
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
from experiments.detector_improvement_v9.model_detector_improvement_v9 import DetectorImprovementV9

def run_test():
    det9 = DetectorImprovementV9()
    
    # Load manifest
    manifest_path = "e:/gunshot/gunshot/experiments/phase51_validation/phase51_evaluation_manifest.csv"
    df = pd.read_csv(manifest_path)
    
    # Test positive recall
    pos_df = df[df["ground_truth_label"] == 1]
    
    recovered = 0
    v9_pos = 0
    v10_pos = 0
    
    for idx, row in pos_df.iterrows():
        p = pathlib.Path("e:/gunshot/gunshot") / row["filepath"]
        if not p.exists(): p = pathlib.Path(row["filepath"])
        audio, sr = sf.read(str(p), dtype='float32')
        if audio.ndim > 1: audio = np.mean(audio, axis=1)
        if sr != 16000: audio = librosa.resample(audio, orig_sr=sr, target_sr=16000)
        audio = audio.astype(np.float32)
        
        # Test V9
        r9 = det9.evaluate_waveform(audio, 16000)
        if r9["detected"]: v9_pos += 1
        
        # Test V10 logic
        dur = float(len(audio)) / 16000.0
        win_size = 15360
        hop_size = 7680
        if len(audio) < win_size:
            y_proc = np.pad(audio, (0, win_size - len(audio)))
            n_wins = 1
        else:
            y_proc = audio
            n_wins = 1 + int((len(audio) - win_size) // hop_size)
            
        det9.reset()
        v10_events = []
        for w in range(n_wins):
            st = w * hop_size
            en = st + win_size
            win = y_proc[st:en]
            
            feat, ys, acoustics = det9.extract_features(win)
            crest, flat, hi, mid, lo, m2l, rolloff, cent, rms, peak = acoustics
            mode, conf, _ = det9.estimator.update(rolloff, hi, mid, lo, m2l, w * 0.48, w)
            
            raw_score = float(det9.fusion_model.predict_proba(feat.reshape(1, -1))[:, 1][0])
            
            # Base model probabilities
            p_mlp, p_cb, p_lgb, p_xgb = feat[0], feat[1], feat[2], feat[3]
            m_mean = feat[4]
            m_min = feat[6]
            m_std = feat[7]
            
            # BMCC calibration
            cal_score = raw_score
            if m_min >= 0.65 and crest >= 12.0 and peak >= 0.20:
                cal_score = max(raw_score, m_mean)
            elif m_mean >= 0.70 and m_std < 0.12 and crest >= 12.0 and peak >= 0.20:
                cal_score = max(raw_score, m_mean)
            elif m_mean >= 0.68 and crest >= 18.0 and peak >= 0.40:
                cal_score = max(raw_score, m_mean)
                
            is_confirmed = (det9.fsm.state == EventState.CONFIRMED)
            supp = det9.suppression.apply_suppression(cal_score, ys, acoustics, is_confirmed)
            adj = supp["adjusted_score"]
            cat = supp["category"]
            
            pure_gun = max(ys.get(c, 0.0) for c in PURE_GUN_CLASSES)
            
            # Balloon burst refinement (hi >= 0.70 instead of 0.75)
            if not supp["suppressed"] and pure_gun < 0.35:
                if cent >= 3400.0 and hi >= 0.70 and lo <= 0.015:
                    adj *= 0.25
                    supp["suppressed"] = True
                    cat = "balloon_burst_impulse"
                    
            # Thunder rumble bypass (C4)
            c4_bypass = (cent >= 1050.0 and crest >= 16.0 and peak >= 0.35 and pure_gun >= 0.04)
            if supp["suppressed"] and cat == "thunder_rumble" and c4_bypass:
                adj = cal_score
                supp["suppressed"] = False
                cat = "c4_rescued"
                
            # Adaptive FSM with window 0 threshold
            policy = det9.fsm.get_policy_for_mode(mode)
            single_crest_std = policy.get("single_impulse_min_crest_db", 13.5)
            if mode == OperatingMode.UNKNOWN and m2l >= 0.30 and cent >= 750.0:
                single_crest_std = 12.0
                
            # Step FSM
            _, ev = det9.fsm.step(adj, crest, w * 0.48, acoustics, mode)
            if ev is not None:
                v10_events.append(ev)
                
        if len(v10_events) > 0:
            v10_pos += 1
            
    print(f"Positive Recall Comparison (N={len(pos_df)}):")
    print(f"  V9:  {v9_pos} / {len(pos_df)} ({v9_pos/len(pos_df)*100:.2f}%)")
    print(f"  V10: {v10_pos} / {len(pos_df)} ({v10_pos/len(pos_df)*100:.2f}%)")

if __name__ == "__main__":
    run_test()

