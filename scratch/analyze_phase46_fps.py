"""
Forensic investigation of Phase 46 False Alarms
"""
import sys, os
sys.path.insert(0, "E:/gunshot/gunshot")
os.chdir("E:/gunshot/gunshot")

import pathlib, json
import numpy as np
import pandas as pd
import soundfile as sf
import librosa
from experiments.detector_improvement_v4.model_detector_improvement_v4 import (
    DetectorImprovementV4,
    compute_physical_acoustic_features_v4
)

v4 = DetectorImprovementV4(profile='balanced')
rca = pd.read_csv('experiments/detector_improvement_v4/recording_condition_analysis.csv')
p46_preds = pd.read_csv('experiments/detector_improvement_v4/recording_level_predictions.csv')

# Look at Phase 12 false positives
p12_fps = p46_preds[(p46_preds['partition'] == 'phase12_new_independent_holdout') & 
                    (p46_preds['ground_truth_gunshot'] == 0) & 
                    (p46_preds['v4_detected'] == 1)]

print(f"Total Phase 12 V4 False Positives: {len(p12_fps)}")

results = []
for idx, r in p12_fps.iterrows():
    rid = r['recording_id']
    match = rca[rca['recording_id'] == rid]
    if len(match) == 0:
        continue
    m = match.iloc[0]
    fpath = pathlib.Path(m['filepath'])
    
    # Load audio and inspect window-level scores
    y, sr = sf.read(str(fpath))
    if y.ndim > 1: y = np.mean(y, axis=1)
    if sr != 16000: y = librosa.resample(y, orig_sr=sr, target_sr=16000)
    y = y.astype(np.float32)
    
    v4.fsm.reset()
    res = v4.evaluate_waveform(y)
    
    # Check top YAMNet classes in peak window
    peak_win_idx = np.argmax(res.get('window_scores', [0])) if len(res.get('window_scores', [])) > 0 else 0
    top_ys = res.get('yamnet_scores', [{}])[peak_win_idx] if peak_win_idx < len(res.get('yamnet_scores', [])) else {}
    sorted_ys = sorted(top_ys.items(), key=lambda kv: kv[1], reverse=True)[:3] if top_ys else []
    
    results.append({
        'id': rid.split('_')[-1],
        'sub_cat': r['sub_category'],
        'v4_peak': round(r['v4_peak_score'], 4),
        'v3_peak': round(r['v3_peak_score'], 4),
        'v2_peak': round(r['v2_peak_score'], 4),
        'crest_db': round(m['crest_factor_db'], 2),
        'hi_ratio': round(m['high_band_ratio_ge_2500hz'], 3),
        'mid_ratio': round(m['mid_band_ratio_500_2500hz'], 3),
        'lo_ratio': round(m['low_band_ratio_lt_500hz'], 3),
        'rolloff': round(m['channel_rolloff_ratio'], 3),
        'm2l': round(m['mid_to_low_energy_ratio'], 3),
        'flat': round(m['spectral_flatness'], 3),
        'top_classes': str([(k, round(v, 2)) for k, v in sorted_ys])
    })

df_res = pd.DataFrame(results)
print(df_res.to_string())
