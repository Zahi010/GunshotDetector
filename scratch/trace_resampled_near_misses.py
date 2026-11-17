import sys
import pathlib
import pandas as pd
import soundfile as sf
import numpy as np
import librosa

sys.path.insert(0, "e:/gunshot/gunshot")
from experiments.detector_improvement_v10.model_detector_improvement_v10 import DetectorImprovementV10

det10 = DetectorImprovementV10()

targets = [
    "mitchell_ak47_762_01.wav",
    "mitchell_ar15_double_01.wav",
    "mitchell_ar15_single_04.wav",
    "mitchell_glock17_9mm_08.wav",
    "mitchell_beretta_rapid_01.wav",
    "mitchell_colt_govt_02.wav"
]

manifest_path = "e:/gunshot/gunshot/experiments/phase51_validation/phase51_evaluation_manifest.csv"
df = pd.read_csv(manifest_path)

for t in targets:
    row = df[df["filename"] == t].iloc[0]
    p = pathlib.Path("e:/gunshot/gunshot") / row["filepath"]
    audio, sr = sf.read(str(p), dtype="float32")
    if audio.ndim > 1: audio = np.mean(audio, axis=1)
    if sr != 16000:
        audio = librosa.resample(audio, orig_sr=sr, target_sr=16000)
    audio = audio.astype(np.float32)
    
    win_size = 15360
    if len(audio) < win_size:
        win = np.pad(audio, (0, win_size - len(audio)))
    else:
        win = audio[:win_size]
        
    feat, ys, acoustics, m_mean = det10.extract_features(win)
    crest, flat, hi, mid, lo, m2l, rolloff, cent, rms, peak = acoustics
    p_mlp, p_cb, p_lgb, p_xgb = feat[0], feat[1], feat[2], feat[3]
    m_min = min(p_mlp, p_cb, p_lgb, p_xgb)
    m_std = feat[7]
    raw_score = float(det10.fusion_model.predict_proba(feat.reshape(1, -1))[:, 1][0])
    
    # BMCC
    cal_score = raw_score
    if m_min >= 0.65 and crest >= 12.0 and peak >= 0.20:
        cal_score = max(raw_score, 0.70 * m_mean + 0.30 * raw_score)
    elif m_mean >= 0.70 and m_std < 0.12 and crest >= 12.0 and peak >= 0.20:
        cal_score = max(raw_score, 0.60 * m_mean + 0.40 * raw_score)
        
    supp = det10.suppression.apply_suppression(cal_score, ys, acoustics, False)
    
    print("=" * 60)
    print(f"File: {t} (len={len(audio)} samples, {len(audio)/16000:.3f}s)")
    print(f"  Base probs: MLP={p_mlp:.3f}, CB={p_cb:.3f}, LGB={p_lgb:.3f}, XGB={p_xgb:.3f}")
    print(f"  Mean={m_mean:.3f}, Min={m_min:.3f}, Std={m_std:.3f}")
    print(f"  Raw={raw_score:.3f}, Cal={cal_score:.3f}, Crest={crest:.1f} dB, Peak={peak:.3f}, Centroid={cent:.1f} Hz")
    print(f"  Suppression: cat={supp['category']}, supp={supp['suppressed']}, adj={supp['adjusted_score']:.3f}")

