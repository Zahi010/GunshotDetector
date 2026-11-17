import os
import sys
sys.path.insert(0, os.path.abspath("."))
sys.path.insert(0, os.path.abspath("src"))

import soundfile as sf
import pandas as pd
import numpy as np

from experiments.detector_improvement_v6.model_detector_improvement_v6 import (
    DetectorImprovementV6,
    compute_physical_acoustic_features_v6,
    OperatingMode
)

detector = DetectorImprovementV6()
rca = pd.read_csv("experiments/detector_improvement_v4/recording_condition_analysis.csv")
p12_files = rca[rca["dataset_source"] == "phase12_independent"]

# Files with high scores that were missed
targets = [
    "phase12_gunshot_pocket_ar15_rapid_03",
    "phase12_gunshot_clean_ar15_double_05",
    "phase12_gunshot_pocket_beretta_single_06",
    "phase12_gunshot_pocket_beretta_single_05",
    "phase12_gunshot_clipped_beretta_rapid_03"
]

for t in targets:
    match = p12_files[p12_files["recording_id"].str.contains(t, case=False)]
    if len(match) == 0:
        continue
    r = match.iloc[0]
    fpath = r["filepath"]
    y, sr = sf.read(fpath)
    if y.ndim > 1:
        y = np.mean(y, axis=1)
    if sr != 16000:
        import librosa
        y = librosa.resample(y, orig_sr=sr, target_sr=16000)
    y = y.astype(np.float32)
    res = detector.evaluate_waveform(y, 16000)
    print(f"\n==================================================", flush=True)
    print(f"Target: {t}", flush=True)
    print(f"File: {fpath}", flush=True)
    print(f"Detected: {res['detected']}, Events: {len(res['events'])}, Peak: {res['peak_score']:.4f}", flush=True)
    
    # Detailed window step
    win_size = 15360
    hop_size = 7680
    if len(y) < win_size:
        y_proc = np.pad(y, (0, win_size - len(y)))
        n_wins = 1
    else:
        y_proc = y
        n_wins = 1 + int((len(y) - win_size) // hop_size)
    detector.reset()
    for w in range(n_wins):
        win = y_proc[w*hop_size : w*hop_size + win_size]
        feat, ys, acoustics = detector.extract_features(win)
        raw_s = float(detector.fusion_model.predict_proba(feat.reshape(1, -1))[:, 1][0])
        crest, flat, hi, mid, lo, m2l, rolloff, cent, rms, peak = acoustics
        
        mode, conf, reason = detector.estimator.update(rolloff, hi, mid, lo, m2l, w*0.48, w)
        supp_res = detector.suppression.apply_suppression(raw_s, ys, acoustics)
        adj_s = supp_res["adjusted_score"]
        
        st, ev = detector.fsm.step(adj_s, crest, w*0.48, acoustics, mode)
        print(f"  Win {w:02d} (t={w*0.48:.2f}s) | raw: {raw_s:.4f} -> adj: {adj_s:.4f} (cat: {supp_res['category']}) | FSM: {st.value} (ev={ev is not None}) | mode: {mode.value} | crest: {crest:.1f} dB, lo: {lo:.2f}, hi: {hi:.3f}, cent: {cent:.0f}", flush=True)
