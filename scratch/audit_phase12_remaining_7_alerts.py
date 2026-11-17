import os
import sys
sys.path.insert(0, os.path.abspath("."))
sys.path.insert(0, os.path.abspath("src"))

import soundfile as sf
import numpy as np
import pandas as pd
import pathlib

from experiments.detector_improvement_v6.model_detector_improvement_v6 import (
    DetectorImprovementV6,
    EventState
)

detector = DetectorImprovementV6()
p12_cont_path = "data/phase12_independent_test/continuous_ambient/phase12_continuous_stream_01_urban_and_environmental_2hr.wav"

info = sf.info(p12_cont_path)
tot_samples = info.frames
sr = info.samplerate
block_len = 16000 * 30 # 30s block
sample_stride = 10

alerts = []
tested_blocks = 0
blk_cnt = 0

with sf.SoundFile(p12_cont_path) as f:
    while f.tell() < tot_samples:
        pos_samples = f.tell()
        block = f.read(block_len, dtype='float32')
        if len(block) == 0:
            break
        if blk_cnt % sample_stride == 0:
            detector.reset()
            res = detector.evaluate_waveform(block, sr)
            if res["events"]:
                for ev in res["events"]:
                    alerts.append({
                        "block_idx": blk_cnt,
                        "block_start_s": round(pos_samples / 16000.0, 2),
                        "event_time_in_block": round(ev.get("time_s", ev.get("time", 0.0)), 2),
                        "exact_time_s": round(pos_samples / 16000.0 + ev.get("time_s", ev.get("time", 0.0)), 2),
                        "score": round(ev.get("score", 0.0), 4),
                        "mode": ev.get("mode", res.get("dominant_mode", "UNKNOWN")),
                        "crest_db": round(ev.get("crest_db", 0.0), 2)
                    })
        blk_cnt += 1

print(f"\nTotal Remaining Alerts on Phase 12 Continuous: {len(alerts)}")
df_alerts = pd.DataFrame(alerts)
print(df_alerts.to_string(index=False))

# Now let's extract acoustic and semantic features for each of these alerts
alert_details = []
for idx, a in enumerate(alerts):
    exact_s = a["exact_time_s"]
    start_sample = max(0, int((exact_s - 1.0) * 16000))
    # Read a 2.5s slice around the alert
    with sf.SoundFile(p12_cont_path) as f:
        f.seek(start_sample)
        slice_audio = f.read(int(2.5 * 16000), dtype='float32')
    
    # Evaluate slice to find exact window
    win_size = 15360
    hop_size = 7680
    n_wins = 1 + int((len(slice_audio) - win_size) // hop_size)
    detector.reset()
    for w in range(n_wins):
        win = slice_audio[w*hop_size : w*hop_size + win_size]
        feat, ys, acoustics = detector.extract_features(win)
        raw_s = float(detector.fusion_model.predict_proba(feat.reshape(1, -1))[:, 1][0])
        crest, flat, hi, mid, lo, m2l, rolloff, cent, rms, peak = acoustics
        supp_res = detector.suppression.apply_suppression(raw_s, ys, acoustics)
        adj_s = supp_res["adjusted_score"]
        if adj_s >= 0.70:
            top_classes = sorted([(k, v) for k, v in ys.items() if v > 0.08], key=lambda x: x[1], reverse=True)[:5]
            cls_str = "; ".join([f"{k}:{v:.3f}" for k, v in top_classes])
            alert_details.append({
                "alert_id": idx + 1,
                "exact_time_s": exact_s,
                "raw_score": round(raw_s, 4),
                "adjusted_score": round(adj_s, 4),
                "suppression_category": supp_res["category"] or "none",
                "crest_db": round(crest, 2),
                "low_ratio": round(lo, 4),
                "mid_ratio": round(mid, 4),
                "high_ratio": round(hi, 4),
                "centroid_hz": round(cent, 1),
                "peak_amplitude": round(peak, 4),
                "top_yamnet": cls_str
            })
            break

df_details = pd.DataFrame(alert_details)
print("\n=== ALERT ACOUSTIC DETAILS ===")
print(df_details.to_string(index=False))

