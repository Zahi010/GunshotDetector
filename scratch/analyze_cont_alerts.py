"""
Inspect Continuous Stream Alerts for V4
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
p12_cont_path = pathlib.Path("data/phase12_independent_test/continuous_ambient/phase12_continuous_stream_01_urban_and_environmental_2hr.wav")

info = sf.info(str(p12_cont_path))
tot_samples = info.frames
sr = info.samplerate
block_len = 16000 * 30 # 30s blocks

print(f"Total duration: {info.duration:.2f}s ({info.duration/3600:.2f} hours), SR: {sr}")

alerts_detail = []
block_idx = 0
sample_stride = 10

with sf.SoundFile(str(p12_cont_path)) as f:
    while f.tell() < tot_samples:
        block = f.read(block_len, dtype='float32')
        if len(block) == 0: break
        if block.ndim > 1: block = np.mean(block, axis=1)
        if sr != 16000: block = librosa.resample(block, orig_sr=sr, target_sr=16000)
        
        if block_idx % sample_stride == 0:
            res = v4.evaluate_waveform(block)
            evs = res.get("events", [])
            if len(evs) > 0:
                crest_db, flatness, hi, mid, lo, m2l, rolloff, cent = compute_physical_acoustic_features_v4(block)
                for ev in evs:
                    alerts_detail.append({
                        "block_idx": block_idx,
                        "time_s": block_idx * 30 + ev.get("time_offset_s", 0.0),
                        "score": round(ev.get("score", 0.0), 4),
                        "crest_db": round(ev.get("crest_factor_db", 0.0), 2),
                        "block_rolloff": round(rolloff, 4),
                        "block_mid": round(mid, 4),
                        "block_hi": round(hi, 4),
                        "block_lo": round(lo, 4)
                    })
        block_idx += 1

print(f"Total alerts detected: {len(alerts_detail)}")
df_alerts = pd.DataFrame(alerts_detail)
print(df_alerts.head(15).to_string())
if len(df_alerts) > 0:
    print("\nSummary statistics of false alerts:")
    print(df_alerts[['score', 'crest_db', 'block_rolloff', 'block_mid', 'block_hi', 'block_lo']].describe().to_string())
