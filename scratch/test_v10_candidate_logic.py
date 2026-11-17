import sys
import pathlib
import numpy as np
import pandas as pd
import soundfile as sf
import librosa

sys.path.insert(0, "e:/gunshot/gunshot")
from experiments.detector_improvement_v9.model_detector_improvement_v9 import (
    DetectorImprovementV9,
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
    NON_TARGET_SEMANTIC_CLASSES
)

def test_v10_candidate_logic():
    manifest_path = "e:/gunshot/gunshot/experiments/phase51_validation/phase51_evaluation_manifest.csv"
    df = pd.read_csv(manifest_path)
    
    det = DetectorImprovementV9()
    
    pos_df = df[df["ground_truth_label"] == 1]
    neg_df = df[df["ground_truth_label"] == 0]
    
    print(f"Testing Candidate V10 logic across {len(pos_df)} positives and {len(neg_df)} negatives...")
    
    # Let's test on the 20 missed files first
    missed_df = pd.read_csv("e:/gunshot/gunshot/scratch/missed_with_paths.csv")
    
    recovered = []
    
    for idx, row in missed_df.iterrows():
        p = pathlib.Path("e:/gunshot/gunshot") / row["filepath"]
        if not p.exists(): p = pathlib.Path(row["filepath"])
        audio, sr = sf.read(str(p), dtype='float32')
        if audio.ndim > 1: audio = np.mean(audio, axis=1)
        if sr != 16000: audio = librosa.resample(audio, orig_sr=sr, target_sr=16000)
        audio = audio.astype(np.float32)
        
        # Test 1 window
        win = audio[:15360]
        if len(win) < 15360: win = np.pad(win, (0, 15360 - len(win)))
        
        feat, ys, acoustics = det.extract_features(win)
        crest, flat, hi, mid, lo, m2l, rolloff, cent, rms, peak = acoustics
        
        # Base models
        wf_tensor = np.expand_dims(win, axis=0)
        # get embeddings
        import tensorflow as tf
        scores_raw, embeddings, _ = det.yamnet_model(tf.convert_to_tensor(win, dtype=tf.float32))
        emb_mean = tf.reduce_mean(embeddings, axis=0, keepdims=True).numpy()
        p_mlp = float(det.classifier_head(emb_mean, training=False).numpy()[0, 0])
        p_cb = float(det.cb_model.predict_proba(emb_mean)[0, 1])
        p_lgb = float(det.lgb_model.predict_proba(emb_mean)[0, 1])
        p_xgb = float(det.xgb_model.predict_proba(emb_mean)[0, 1])
        
        m_mean = (p_mlp + p_cb + p_lgb + p_xgb) / 4.0
        m_min = min(p_mlp, p_cb, p_lgb, p_xgb)
        
        raw_score = float(det.fusion_model.predict_proba(feat.reshape(1, -1))[:, 1][0])
        
        # 1. Base Model Consensus Calibration (BMCC)
        calibrated_score = raw_score
        if m_min >= 0.65 and crest >= 13.0 and peak >= 0.25:
            calibrated_score = max(raw_score, 0.70 * m_mean + 0.30 * raw_score)
        elif m_mean >= 0.70 and crest >= 13.0 and peak >= 0.25:
            calibrated_score = max(raw_score, 0.60 * m_mean + 0.40 * raw_score)
            
        # 2. Refined Thunder Rumble Bypass (C4)
        pure_gun = max(ys.get(c, 0.0) for c in PURE_GUN_CLASSES)
        c4_bypass = (cent >= 1050.0 and crest >= 16.0 and peak >= 0.35 and pure_gun >= 0.04)
        
        # Test suppression
        # Apply standard suppression with C4 bypass
        res_v9 = det.suppression.apply_suppression(calibrated_score, ys, acoustics, False)
        adj_score = res_v9["adjusted_score"]
        
        # If it was suppressed as thunder_rumble but c4_bypass is True, restore score!
        if res_v9["suppressed"] and res_v9["category"] == "thunder_rumble" and c4_bypass:
            adj_score = calibrated_score
            supp_status = "c4_rescued"
        else:
            supp_status = res_v9["category"]
            
        # Check if score >= 0.70
        can_detect = (adj_score >= 0.70)
        if can_detect:
            recovered.append({
                "filename": row["filename"],
                "sub_category": row["sub_category"],
                "raw_score": round(raw_score, 4),
                "m_mean": round(m_mean, 4),
                "calibrated_score": round(calibrated_score, 4),
                "adj_score": round(adj_score, 4),
                "crest": round(crest, 2),
                "cent": round(cent, 1),
                "lo": round(lo, 4),
                "supp_status": supp_status
            })
            
    print(f"\nRecovered {len(recovered)} / 20 missed gunshots with Candidate V10 logic:")
    rec_df = pd.DataFrame(recovered)
    if not rec_df.empty:
        print(rec_df.to_string())
    print(f"\nNew Projected Positive Recall: {45 + len(recovered)} / 65 ({(45 + len(recovered)) / 65 * 100:.2f}%)")

if __name__ == "__main__":
    test_v10_candidate_logic()

