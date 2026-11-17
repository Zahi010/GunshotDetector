import sys
sys.path.insert(0, ".")
import pathlib
import time
import numpy as np
import pandas as pd
import soundfile as sf
import librosa
import tensorflow as tf
import joblib
from scipy import signal
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.model_selection import GroupKFold
from sklearn.metrics import roc_auc_score, brier_score_loss

print("Initializing V4 Training Pipeline...")
from experiments.detector_improvement_v3.model_detector_improvement_v3 import DetectorImprovementV3

v3 = DetectorImprovementV3(profile="balanced")

def compute_v4_acoustics(y_win: np.ndarray, sr: int = 16000):
    if len(y_win) == 0:
        return 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0
    pk = float(np.max(np.abs(y_win)))
    rms = float(np.sqrt(np.mean(y_win**2) + 1e-12))
    crest_db = float(20.0 * np.log10(max(pk / (rms + 1e-12), 1.0)))
    
    P = np.abs(np.fft.rfft(y_win))**2
    freqs = np.fft.rfftfreq(len(y_win), d=1.0 / float(sr))
    
    log_p = np.log(P + 1e-12)
    flatness = float(np.exp(np.mean(log_p)) / (np.mean(P) + 1e-12))
    
    tot_e = float(np.sum(P) + 1e-12)
    low_e = float(np.sum(P[freqs < 500.0]))
    mid_e = float(np.sum(P[(freqs >= 500.0) & (freqs < 2500.0)]))
    high_e = float(np.sum(P[freqs >= 2500.0]))
    
    low_ratio = low_e / tot_e
    mid_ratio = mid_e / tot_e
    high_ratio = high_e / tot_e
    
    mid_to_low = (mid_ratio + 1e-4) / (low_ratio + 1e-4)
    rolloff = (high_ratio + 1e-4) / (mid_ratio + 1e-4)
    centroid = float(np.sum(freqs * P) / tot_e)
    
    return crest_db, flatness, high_ratio, mid_ratio, low_ratio, mid_to_low, rolloff, centroid

def extract_window_v4_features(y_win: np.ndarray):
    crest_db, flatness, high_ratio, mid_ratio, low_ratio, mid_to_low, rolloff, centroid = compute_v4_acoustics(y_win)
    
    wave_tensor = tf.convert_to_tensor(y_win, dtype=tf.float32)
    yamnet_out = v3.yamnet_model(wave_tensor)
    scores_t, embs_t = yamnet_out[0], yamnet_out[1]
    emb = embs_t.numpy()
    ys = scores_t.numpy()[0]
    
    p_mlp = float(v3.mlp.predict(emb, verbose=0).flatten()[0])
    p_cb = float(v3.cb.predict_proba(emb)[:, 1][0])
    p_lgb = float(v3.lgb.predict_proba(emb)[:, 1][0])
    p_xgb = float(v3.xgb.predict_proba(emb)[:, 1][0])
    
    m_mean = (p_mlp + p_cb + p_lgb + p_xgb) / 4.0
    m_max = max(p_mlp, p_cb, p_lgb, p_xgb)
    m_min = min(p_mlp, p_cb, p_lgb, p_xgb)
    m_std = float(np.std([p_mlp, p_cb, p_lgb, p_xgb]))
    sorted_m = sorted([p_mlp, p_cb, p_lgb, p_xgb], reverse=True)
    top2 = (sorted_m[0] + sorted_m[1]) / 2.0
    
    gun_s = max(float(ys[cls]) for cls in [421, 422, 424, 425])
    bal_s = max(float(ys[cls]) for cls in [420, 421, 422, 424, 425, 428, 434, 460])
    fw_s = max(float(ys[cls]) for cls in [426, 427])
    thun_s = max(float(ys[cls]) for cls in [280, 281])
    imp_s = max(float(ys[cls]) for cls in [413, 414, 352, 353, 58])
    glass_s = max(float(ys[cls]) for cls in [433, 435, 436])
    nt_s = max(float(ys[cls]) for cls in ([0] + list(range(67, 118)) + list(range(300, 331)) + [502, 503, 504]))
    
    feat = [
        # Ensemble models (9)
        p_mlp, p_cb, p_lgb, p_xgb,
        m_mean, m_max, m_min, m_std, top2,
        # Semantics (7)
        gun_s, bal_s, fw_s, thun_s, imp_s, glass_s, nt_s,
        # Ratios (2)
        (bal_s + 1e-4) / (fw_s + 1e-4),
        (bal_s + 1e-4) / (imp_s + 1e-4),
        # Physical acoustics (8)
        crest_db, flatness, high_ratio, mid_ratio, low_ratio, mid_to_low, rolloff, centroid
    ]
    return feat, ys

# Apply fabric low-pass filter
def apply_fabric_filter(y: np.ndarray, sr: int = 16000, cutoff_hz: float = 1800.0):
    sos = signal.butter(2, cutoff_hz, btype='lowpass', fs=sr, output='sos')
    return signal.sosfilt(sos, y).astype(np.float32)

# Load Development partition cache
v3_dev_cache = joblib.load("scratch/v3_dev_features.joblib")
print(f"Loaded {len(v3_dev_cache)} development recordings from cache.")

# Map recording ID to file path to allow domain adaptation
v2_preds = pd.read_csv("experiments/detector_improvement_v2/recording_level_predictions.csv")
v2_dev = v2_preds[v2_preds["v2_partition"] == "development"].copy()

p38 = pathlib.Path("experiments/phase38/dataset")
p39 = pathlib.Path("experiments/phase39/dataset")
p40 = pathlib.Path("experiments/phase40/dataset")

def find_audio_path(rid):
    fn = rid + ".wav"
    for cand in [
        p38 / "positive" / fn,
        p38 / "distractors" / fn,
        p38 / "continuous" / fn,
        p39 / "distractor" / fn,
        p39 / "continuous" / fn,
        p40 / "continuous" / fn
    ]:
        if cand.exists(): return cand
    return None

X_train_list = []
y_train_list = []
groups_list = []

print("\nExtracting V4 training features with domain adaptation...")
t0 = time.time()
pos_count = 0
neg_count = 0

for item in v3_dev_cache:
    rid = item["recording_id"]
    n_wins = item["n_windows"]
    gt = int(item["ground_truth"])
    fpath = find_audio_path(rid)
    
    # Load raw audio if available
    audio_data = None
    if fpath is not None and fpath.exists():
        y_raw, sr = sf.read(str(fpath))
        if y_raw.ndim > 1: y_raw = np.mean(y_raw, axis=1)
        if sr != 16000: y_raw = librosa.resample(y_raw, orig_sr=sr, target_sr=16000)
        audio_data = y_raw.astype(np.float32)
        
    for w in range(n_wins):
        # 1. Original window
        if audio_data is not None:
            st = int(w * 0.48 * 16000)
            en = st + 15360
            y_w = audio_data[st:en]
            if len(y_w) < 15360:
                y_w = np.pad(y_w, (0, 15360 - len(y_w)))
            feat, _ = extract_window_v4_features(y_w)
        else:
            # Reconstruct from cache with default mid/lo
            crest, flat, hi, lo, cent = item["win_acoustics"][w]
            mid = max(1.0 - hi - lo, 0.0)
            m2l = (mid + 1e-4) / (lo + 1e-4)
            rolloff = (hi + 1e-4) / (mid + 1e-4)
            
            p_mlp = item["p_mlp"][w]
            p_cb = item["p_cb"][w]
            p_lgb = item["p_lgb"][w]
            p_xgb = item["p_xgb"][w]
            m_mean = (p_mlp + p_cb + p_lgb + p_xgb) / 4.0
            m_max = max(p_mlp, p_cb, p_lgb, p_xgb)
            m_min = min(p_mlp, p_cb, p_lgb, p_xgb)
            m_std = float(np.std([p_mlp, p_cb, p_lgb, p_xgb]))
            sorted_m = sorted([p_mlp, p_cb, p_lgb, p_xgb], reverse=True)
            top2 = (sorted_m[0] + sorted_m[1]) / 2.0
            
            ys = item["yamnet_scores"][w]
            gun_s = max(float(ys[cls]) for cls in [421, 422, 424, 425])
            bal_s = max(float(ys[cls]) for cls in [420, 421, 422, 424, 425, 428, 434, 460])
            fw_s = max(float(ys[cls]) for cls in [426, 427])
            thun_s = max(float(ys[cls]) for cls in [280, 281])
            imp_s = max(float(ys[cls]) for cls in [413, 414, 352, 353, 58])
            glass_s = max(float(ys[cls]) for cls in [433, 435, 436])
            nt_s = max(float(ys[cls]) for cls in ([0] + list(range(67, 118)) + list(range(300, 331)) + [502, 503, 504]))
            
            feat = [
                p_mlp, p_cb, p_lgb, p_xgb,
                m_mean, m_max, m_min, m_std, top2,
                gun_s, bal_s, fw_s, thun_s, imp_s, glass_s, nt_s,
                (bal_s + 1e-4) / (fw_s + 1e-4),
                (bal_s + 1e-4) / (imp_s + 1e-4),
                crest, flat, hi, mid, lo, m2l, rolloff, cent
            ]
            
        X_train_list.append(feat)
        y_train_list.append(gt)
        groups_list.append(rid)
        
        # 2. Domain adaptation for positive windows (apply fabric transmission simulation)
        if gt == 1 and audio_data is not None:
            # Fabric simulation 1: 1800 Hz cutoff
            y_muffled1 = apply_fabric_filter(y_w, cutoff_hz=1800.0)
            feat_muf1, _ = extract_window_v4_features(y_muffled1)
            X_train_list.append(feat_muf1)
            y_train_list.append(1)
            groups_list.append(rid)
            
            # Fabric simulation 2: 1400 Hz cutoff (heavy denim/canvas)
            y_muffled2 = apply_fabric_filter(y_w, cutoff_hz=1400.0)
            feat_muf2, _ = extract_window_v4_features(y_muffled2)
            X_train_list.append(feat_muf2)
            y_train_list.append(1)
            groups_list.append(rid)

X_all = np.array(X_train_list, dtype=np.float32)
y_all = np.array(y_train_list, dtype=np.int32)
groups_all = np.array(groups_list)

print(f"Dataset compiled in {time.time() - t0:.1f}s: {len(X_all)} windows across {len(set(groups_all))} recording groups.")
print(f"Positives: {np.sum(y_all == 1)}, Negatives: {np.sum(y_all == 0)}")

# 5-Fold GroupKFold Cross-Validation
gkf = GroupKFold(n_splits=5)
aucs = []
briers = []

for fold, (train_idx, val_idx) in enumerate(gkf.split(X_all, y_all, groups_all)):
    X_tr, y_tr = X_all[train_idx], y_all[train_idx]
    X_va, y_val = X_all[val_idx], y_all[val_idx]
    
    clf = HistGradientBoostingClassifier(
        max_iter=150,
        max_depth=5,
        learning_rate=0.08,
        l2_regularization=1.5,
        min_samples_leaf=20,
        random_state=42 + fold
    )
    clf.fit(X_tr, y_tr)
    preds = clf.predict_proba(X_va)[:, 1]
    
    auc = roc_auc_score(y_val, preds)
    brier = brier_score_loss(y_val, preds)
    aucs.append(auc)
    briers.append(brier)
    print(f"  Fold {fold+1}: ROC-AUC = {auc:.4f}, Brier = {brier:.4f}")

print(f"\nMean CV ROC-AUC: {np.mean(aucs):.4f} +/- {np.std(aucs):.4f}")
print(f"Mean CV Brier Score: {np.mean(briers):.4f} +/- {np.std(briers):.4f}")

# Train final production model on full development set
final_clf = HistGradientBoostingClassifier(
    max_iter=150,
    max_depth=5,
    learning_rate=0.08,
    l2_regularization=1.5,
    min_samples_leaf=20,
    random_state=42
)
final_clf.fit(X_all, y_all)

out_model_path = pathlib.Path("experiments/detector_improvement_v4/fusion_model.joblib")
joblib.dump(final_clf, out_model_path)
print(f"\nSuccessfully trained and saved V4 fusion model to {out_model_path}!")

