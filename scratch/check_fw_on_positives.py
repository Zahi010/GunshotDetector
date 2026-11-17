import sys, os, pathlib
sys.path.insert(0, os.path.abspath("."))
sys.path.insert(0, os.path.abspath("src"))

import soundfile as sf
import numpy as np
import pandas as pd
import librosa
from experiments.detector_improvement_v6.model_detector_improvement_v6 import DetectorImprovementV6

v6 = DetectorImprovementV6()

def check_positives(manifest_path, name):
    print(f"\n--- Checking {name} ---")
    df = pd.read_csv(manifest_path)
    gt_col = [c for c in df.columns if "ground_truth" in c or "label" in c][0]
    pos_df = df[df[gt_col] == 1]
    
    fw_supp_count = 0
    total_pos = 0
    for _, r in pos_df.iterrows():
        fpath = r.get("filepath") or r.get("relative_path")
        if not os.path.exists(fpath):
            fpath = os.path.join("data", fpath) if os.path.exists(os.path.join("data", fpath)) else fpath
        if not os.path.exists(fpath):
            continue
            
        y, sr = sf.read(fpath)
        if y.ndim > 1: y = np.mean(y, axis=1)
        if sr != 16000: y = librosa.resample(y, orig_sr=sr, target_sr=16000)
        y = y.astype(np.float32)
        
        total_pos += 1
        win_size = 15360
        hop_size = 7680
        n_wins = 1 + int((len(y) - win_size) // hop_size) if len(y) >= win_size else 1
        v6.reset()
        file_fw_supp = False
        for w in range(n_wins):
            win = y[w*hop_size : w*hop_size + win_size] if len(y) >= win_size else np.pad(y, (0, win_size - len(y)))
            feat, ys, acoustics = v6.extract_features(win)
            crest, flat, hi, mid, lo, m2l, rolloff, cent, rms, peak = acoustics
            raw_s = float(v6.fusion_model.predict_proba(feat.reshape(1, -1))[:, 1][0])
            supp = v6.suppression.apply_suppression(raw_s, ys, acoustics)
            if "firework" in (supp["category"] or ""):
                file_fw_supp = True
        if file_fw_supp:
            fw_supp_count += 1
            print(f"  Pos file had FW supp: {fpath}")
    print(f"Total pos with FW supp: {fw_supp_count} / {total_pos}")

check_positives("reports/phase15_dataset_manifest.csv", "Phase 15 Positives")
