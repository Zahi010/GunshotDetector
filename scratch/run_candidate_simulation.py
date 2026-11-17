import sys
import pathlib
import numpy as np
import pandas as pd
import soundfile as sf
import librosa

sys.path.insert(0, "e:/gunshot/gunshot")
from experiments.detector_improvement_v9.model_detector_improvement_v9 import (
    DetectorImprovementV9,
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

def run_candidate_simulation():
    det = DetectorImprovementV9()
    manifest_path = "e:/gunshot/gunshot/experiments/phase51_validation/phase51_evaluation_manifest.csv"
    df = pd.read_csv(manifest_path)
    
    print(f"Total recordings in manifest: {len(df)}")
    
    # We test Candidate V10 logic:
    # 1. Base Model Consensus Calibration (BMCC):
    #    When all 4 base models agree (min >= 0.65) or mean >= 0.70 with low std (< 0.12),
    #    and crest >= 13.0 dB, peak >= 0.20:
    #    calibrated_score = max(raw_score, 0.70 * m_mean + 0.30 * raw_score)
    #
    # 2. Refined Thunder Rumble Bypass (C4):
    #    If cent >= 1050.0 Hz and crest >= 16.0 dB and peak >= 0.35 and pure_gun >= 0.04:
    #    override thunder_rumble suppression (not thunder, but sharp gunshot with ground wave).
    #
    # 3. Single-impulse exception in FSM:
    #    If n_windows == 1 and score >= 0.70 and crest >= 13.0 dB:
    #    allow single impulse exception (prevent 0.5s audio files from starving candidate queue).
    
    pos_results = []
    neg_results = []
    
    for idx, row in df.iterrows():
        p = pathlib.Path("e:/gunshot/gunshot") / row["filepath"]
        if not p.exists(): p = pathlib.Path(row["filepath"])
        
        audio, sr = sf.read(str(p), dtype='float32')
        if audio.ndim > 1: audio = np.mean(audio, axis=1)
        if sr != 16000: audio = librosa.resample(audio, orig_sr=sr, target_sr=16000)
        audio = audio.astype(np.float32)
        
        win_size = 15360
        hop_size = 7680
        if len(audio) < win_size:
            y_proc = np.pad(audio, (0, win_size - len(audio)))
            n_wins = 1
        else:
            y_proc = audio
            n_wins = 1 + int((len(audio) - win_size) // hop_size)
            
        det.reset()
        detected_v9 = False
        detected_v10 = False
        max_v9 = 0.0
        max_v10 = 0.0
        
        events_v10 = []
        candidate_scores_v10 = []
        
        for w in range(n_wins):
            st = w * hop_size
            en = st + win_size
            win = y_proc[st:en]
            
            feat, ys, acoustics = det.extract_features(win)
            crest, flat, hi, mid, lo, m2l, rolloff, cent, rms, peak = acoustics
            mode, conf, _ = det.estimator.update(rolloff, hi, mid, lo, m2l, w * 0.48, w)
            
            import tensorflow as tf
            scores_raw, embeddings, _ = det.yamnet_model(tf.convert_to_tensor(win, dtype=tf.float32))
            emb_mean = tf.reduce_mean(embeddings, axis=0, keepdims=True).numpy()
            p_mlp = float(det.classifier_head(emb_mean, training=False).numpy()[0, 0])
            p_cb = float(det.cb_model.predict_proba(emb_mean)[0, 1])
            p_lgb = float(det.lgb_model.predict_proba(emb_mean)[0, 1])
            p_xgb = float(det.xgb_model.predict_proba(emb_mean)[0, 1])
            
            m_mean = (p_mlp + p_cb + p_lgb + p_xgb) / 4.0
            m_min = min(p_mlp, p_cb, p_lgb, p_xgb)
            m_std = float(np.std([p_mlp, p_cb, p_lgb, p_xgb]))
            
            raw_score = float(det.fusion_model.predict_proba(feat.reshape(1, -1))[:, 1][0])
            
            # --- V9 Baseline ---
            supp_v9 = det.suppression.apply_suppression(raw_score, ys, acoustics, (det.fsm.state == EventState.CONFIRMED))
            adj_v9 = supp_v9["adjusted_score"]
            max_v9 = max(max_v9, adj_v9)
            _, ev_v9 = det.fsm.step(adj_v9, crest, w * 0.48, acoustics, mode)
            if ev_v9 is not None: detected_v9 = True
            
            # --- V10 Candidate ---
            # 1. Base Model Consensus Calibration
            cal_score = raw_score
            if m_min >= 0.65 and crest >= 13.0 and peak >= 0.20:
                cal_score = max(raw_score, 0.70 * m_mean + 0.30 * raw_score)
            elif m_mean >= 0.70 and m_std < 0.12 and crest >= 13.0 and peak >= 0.20:
                cal_score = max(raw_score, 0.60 * m_mean + 0.40 * raw_score)
                
            # 2. Suppression with C4 Bypass
            supp_v10 = det.suppression.apply_suppression(cal_score, ys, acoustics, len(events_v10) > 0)
            adj_v10 = supp_v10["adjusted_score"]
            
            pure_gun = max(ys.get(c, 0.0) for c in PURE_GUN_CLASSES)
            c4_bypass = (cent >= 1050.0 and crest >= 16.0 and peak >= 0.35 and pure_gun >= 0.04)
            if supp_v10["suppressed"] and supp_v10["category"] == "thunder_rumble" and c4_bypass:
                adj_v10 = cal_score
                
            max_v10 = max(max_v10, adj_v10)
            
            # 3. FSM step with single-window logic
            # Single impulse check
            single_allowed = (crest >= 13.0 and adj_v10 >= 0.70)
            if len(events_v10) == 0:
                if single_allowed:
                    events_v10.append({"trigger": "single_impulse", "score": adj_v10})
                    detected_v10 = True
                elif adj_v10 >= 0.70:
                    candidate_scores_v10.append(adj_v10)
                    if len(candidate_scores_v10) >= 2:
                        events_v10.append({"trigger": "cluster", "score": max(candidate_scores_v10)})
                        detected_v10 = True
                else:
                    candidate_scores_v10 = []
                    
        rec_data = {
            "filename": row["filename"],
            "sub_category": row["sub_category"],
            "condition": row["condition_category"],
            "v9_detected": detected_v9,
            "v10_detected": detected_v10,
            "v9_peak": round(max_v9, 4),
            "v10_peak": round(max_v10, 4)
        }
        if row["ground_truth_label"] == 1:
            pos_results.append(rec_data)
        else:
            neg_results.append(rec_data)
            
    pos_df = pd.DataFrame(pos_results)
    neg_df = pd.DataFrame(neg_results)
    
    print("\n" + "=" * 60)
    print("SIMULATION RESULTS:")
    print("=" * 60)
    print(f"Positive Gunshot Recall (N={len(pos_df)}):")
    print(f"  V9:  {pos_df['v9_detected'].sum()} / {len(pos_df)} ({pos_df['v9_detected'].mean()*100:.2f}%)")
    print(f"  V10: {pos_df['v10_detected'].sum()} / {len(pos_df)} ({pos_df['v10_detected'].mean()*100:.2f}%)")
    
    print(f"\nNegative False Positive Rate (N={len(neg_df)}):")
    print(f"  V9:  {neg_df['v9_detected'].sum()} / {len(neg_df)} ({neg_df['v9_detected'].mean()*100:.2f}%)")
    print(f"  V10: {neg_df['v10_detected'].sum()} / {len(neg_df)} ({neg_df['v10_detected'].mean()*100:.2f}%)")
    
    # Check challenge negative subgroups
    door_slams = neg_df[neg_df["sub_category"] == "heavy_door_slam"]
    balloon_bursts = neg_df[neg_df["sub_category"] == "balloon_burst_impulse"]
    fireworks = neg_df[neg_df["sub_category"] == "fireworks_mortar_burst"]
    glass = neg_df[neg_df["sub_category"] == "glass_breakage"]
    
    print("\nChallenge Subgroup False Positive Rates:")
    print(f"  Heavy Door Slams (N={len(door_slams)}):   V9={door_slams['v9_detected'].sum()} | V10={door_slams['v10_detected'].sum()}")
    print(f"  Balloon Bursts (N={len(balloon_bursts)}):     V9={balloon_bursts['v9_detected'].sum()} | V10={balloon_bursts['v10_detected'].sum()}")
    print(f"  Fireworks (N={len(fireworks)}):          V9={fireworks['v9_detected'].sum()} | V10={fireworks['v10_detected'].sum()}")
    print(f"  Glass Breakage (N={len(glass)}):     V9={glass['v9_detected'].sum()} | V10={glass['v10_detected'].sum()}")

    pos_df.to_csv("e:/gunshot/gunshot/scratch/sim_pos_results.csv", index=False)
    neg_df.to_csv("e:/gunshot/gunshot/scratch/sim_neg_results.csv", index=False)

if __name__ == "__main__":
    run_candidate_simulation()

