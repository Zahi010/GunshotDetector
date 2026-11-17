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

def evaluate_v10_full():
    manifest_path = "e:/gunshot/gunshot/experiments/phase51_validation/phase51_evaluation_manifest.csv"
    df = pd.read_csv(manifest_path)
    
    det = DetectorImprovementV9()
    
    results = []
    
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
        max_adj = 0.0
        v10_events = []
        candidate_scores = []
        
        for w in range(n_wins):
            st = w * hop_size
            en = st + win_size
            win = y_proc[st:en]
            
            feat, ys, acoustics = det.extract_features(win)
            crest, flat, hi, mid, lo, m2l, rolloff, cent, rms, peak = acoustics
            mode, conf, _ = det.estimator.update(rolloff, hi, mid, lo, m2l, w * 0.48, w)
            
            # Base models
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
            
            # 1. Base Model Consensus Calibration (BMCC)
            cal_score = raw_score
            if m_min >= 0.65 and crest >= 12.0 and peak >= 0.20:
                cal_score = max(raw_score, 0.70 * m_mean + 0.30 * raw_score)
            elif m_mean >= 0.70 and m_std < 0.12 and crest >= 12.0 and peak >= 0.20:
                cal_score = max(raw_score, 0.60 * m_mean + 0.40 * raw_score)
                
            # 2. V10 Enhanced Suppression:
            # First apply base suppression
            supp = det.suppression.apply_suppression(cal_score, ys, acoustics, len(v10_events) > 0)
            adj = supp["adjusted_score"]
            cat = supp["category"]
            
            pure_gun = max(ys.get(c, 0.0) for c in PURE_GUN_CLASSES)
            
            # Balloon burst refinement (hi >= 0.70 instead of 0.75)
            if not supp["suppressed"] and pure_gun < 0.35:
                if cent >= 3400.0 and hi >= 0.70 and lo <= 0.015:
                    adj *= 0.25
                    supp["suppressed"] = True
                    cat = "balloon_burst_impulse"
                    
            # Thunder rumble bypass (C4) for high-frequency sharp muzzle blasts
            c4_bypass = (cent >= 1050.0 and crest >= 16.0 and peak >= 0.35 and pure_gun >= 0.04)
            if supp["suppressed"] and cat == "thunder_rumble" and c4_bypass:
                adj = cal_score
                supp["suppressed"] = False
                cat = "c4_rescued"
                
            max_adj = max(max_adj, adj)
            
            # 3. V10 Adaptive FSM Logic:
            # Policy selection
            policy = det.fsm.get_policy_for_mode(mode)
            single_crest_min = policy.get("single_impulse_min_crest_db", 13.5)
            # If in window 0 with clear acoustics, use clear threshold 12.0 dB
            if mode == OperatingMode.UNKNOWN and m2l >= 0.30 and cent >= 750.0:
                single_crest_min = 12.0
                
            single_allowed = (crest >= single_crest_min and adj >= 0.70)
            
            if len(v10_events) == 0:
                if single_allowed:
                    v10_events.append({"trigger": "single_impulse", "score": adj})
                elif adj >= 0.70:
                    candidate_scores.append(adj)
                    if len(candidate_scores) >= 2:
                        v10_events.append({"trigger": "cluster", "score": max(candidate_scores)})
                else:
                    candidate_scores = []
                    
        results.append({
            "filename": row["filename"],
            "ground_truth_label": row["ground_truth_label"],
            "primary_category": row["primary_category"],
            "sub_category": row["sub_category"],
            "condition": row["condition_category"],
            "v10_detected": len(v10_events) > 0,
            "v10_peak_score": round(max_adj, 4)
        })
        
    res_df = pd.DataFrame(results)
    res_df.to_csv("e:/gunshot/gunshot/scratch/v10_full_eval_results.csv", index=False)
    
    pos = res_df[res_df["ground_truth_label"] == 1]
    neg = res_df[res_df["ground_truth_label"] == 0]
    
    print("\n" + "=" * 70)
    print("V10 REFINED EVALUATION SUMMARY:")
    print("=" * 70)
    print(f"Positive Gunshot Recall: {pos['v10_detected'].sum()} / {len(pos)} ({pos['v10_detected'].mean()*100:.2f}%)")
    print(f"Negative Control FPR:    {neg['v10_detected'].sum()} / {len(neg)} ({neg['v10_detected'].mean()*100:.2f}%)")
    
    # Specific challenge categories
    for subcat in [
        "hard_negative_door_slam",
        "hard_negative_balloon_burst",
        "hard_negative_fireworks",
        "esc50_glass_breaking_untouched",
        "hard_negative_metal_hammer_impact",
        "hard_negative_thunder_rumble",
        "hard_negative_vehicle_backfire"
    ]:
        sub_df = neg[neg["sub_category"] == subcat]
        print(f"  {subcat:35s} (N={len(sub_df):2d}): {sub_df['v10_detected'].sum()} false alerts ({sub_df['v10_detected'].mean()*100:.2f}%)")

if __name__ == "__main__":
    evaluate_v10_full()

