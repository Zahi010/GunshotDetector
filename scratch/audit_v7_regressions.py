"""
Detailed Audit of V7 Regressions:
1. 16 Continuous Alerts on Phase 12 2.0hr stream
2. Fireworks False Alarms on Phase 12 and Phase 15
Outputs exact acoustic and semantic parameters to identify root causes.

RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.
"""

import sys, os, pathlib
sys.path.insert(0, "E:/gunshot/gunshot")
sys.path.insert(0, "E:/gunshot/gunshot/src")
os.chdir("E:/gunshot/gunshot")

import json
import soundfile as sf
import numpy as np
import pandas as pd
import librosa

from experiments.detector_improvement_v6.model_detector_improvement_v6 import DetectorImprovementV6
from experiments.detector_improvement_v7.model_detector_improvement_v7 import (
    DetectorImprovementV7,
    EventState,
    OperatingMode,
    GUN_CLASSES,
    PURE_GUN_CLASSES,
    BALLISTIC_CLASSES,
    FIREWORKS_CLASSES,
    CAP_GUN_CLASS
)

v6 = DetectorImprovementV6()
v7 = DetectorImprovementV7()

p12_cont_path = "data/phase12_independent_test/continuous_ambient/phase12_continuous_stream_01_urban_and_environmental_2hr.wav"

info = sf.info(p12_cont_path)
tot_samples = info.frames
sr = info.samplerate
block_len = 16000 * 30
sample_stride = 10

alerts_v7 = []
alerts_v6 = []

print("Running single-pass continuous block audit...")
with sf.SoundFile(p12_cont_path) as f:
    blk_cnt = 0
    while f.tell() < tot_samples:
        pos_samples = f.tell()
        block = f.read(block_len, dtype='float32')
        if len(block) == 0: break
        if blk_cnt % sample_stride == 0:
            block_start_s = pos_samples / 16000.0
            
            # Evaluate V6
            v6.reset()
            res_v6 = v6.evaluate_waveform(block, sr)
            for ev in res_v6["events"]:
                ev_copy = dict(ev)
                ev_copy["block_idx"] = blk_cnt
                ev_copy["file_time_s"] = round(block_start_s + ev["start_time"], 2)
                alerts_v6.append(ev_copy)
                
            # Evaluate V7
            v7.reset()
            res_v7 = v7.evaluate_waveform(block, sr)
            for ev in res_v7["events"]:
                ev_copy = dict(ev)
                ev_copy["block_idx"] = blk_cnt
                ev_copy["file_time_s"] = round(block_start_s + ev["start_time"], 2)
                alerts_v7.append(ev_copy)
                
        blk_cnt += 1

print(f"\nTotal V6 Alerts on 2hr stream: {len(alerts_v6)}")
print(f"Total V7 Alerts on 2hr stream: {len(alerts_v7)}")

# Now for each V7 alert, extract window-level acoustic details
detailed_v7 = []
for idx, a in enumerate(alerts_v7):
    file_t = a["file_time_s"]
    blk_idx = a["block_idx"]
    blk_start_s = blk_idx * 30.0
    # Read block
    with sf.SoundFile(p12_cont_path) as f:
        f.seek(blk_idx * block_len)
        blk = f.read(block_len, dtype='float32')
        
    win_size = 15360
    hop_size = 7680
    n_wins = 1 + int((len(blk) - win_size) // hop_size)
    
    # Track through V6 and V7 to compare window by window
    v6.reset()
    v7.reset()
    
    match_win = None
    for w in range(n_wins):
        win = blk[w*hop_size : w*hop_size + win_size]
        feat, ys, acoustics = v7.extract_features(win)
        crest, flat, hi, mid, lo, m2l, rolloff, cent, rms, peak = acoustics
        
        mode_v7, _, _ = v7.estimator.update(rolloff, hi, mid, lo, m2l, w * 0.48, w)
        raw_s = float(v7.fusion_model.predict_proba(feat.reshape(1, -1))[:, 1][0])
        
        # V6 supp
        supp_v6 = v6.suppression.apply_suppression(raw_s, ys, acoustics, v6.fsm.state == EventState.CONFIRMED)
        adj_v6 = supp_v6["adjusted_score"]
        st_v6, ev_v6 = v6.fsm.step(adj_v6, crest, w * 0.48, acoustics, mode_v7)
        
        # V7 supp
        supp_v7 = v7.suppression.apply_suppression(raw_s, ys, acoustics, v7.fsm.state == EventState.CONFIRMED)
        adj_v7 = supp_v7["adjusted_score"]
        st_v7, ev_v7 = v7.fsm.step(adj_v7, crest, w * 0.48, acoustics, mode_v7)
        
        win_time = round(blk_start_s + w * 0.48, 2)
        if abs(win_time - file_t) < 0.50 or (ev_v7 is not None and abs(round(blk_start_s + ev_v7["start_time"], 2) - file_t) < 0.1):
            top_classes = sorted([(k, v) for k, v in ys.items() if v > 0.05], key=lambda x: x[1], reverse=True)[:5]
            cls_str = "; ".join([f"{k}:{v:.3f}" for k, v in top_classes])
            pure_gun = max(ys.get(c, 0.0) for c in PURE_GUN_CLASSES)
            cap_gun = ys.get(CAP_GUN_CLASS, 0.0)
            bal_s = max(ys.get(c, 0.0) for c in BALLISTIC_CLASSES)
            fw_s = max(ys.get(c, 0.0) for c in FIREWORKS_CLASSES)
            
            detailed_v7.append({
                "alert_idx": idx + 1,
                "file_time_s": file_t,
                "block_idx": blk_idx,
                "raw_score": round(raw_s, 4),
                "v6_adj_score": round(adj_v6, 4),
                "v7_adj_score": round(adj_v7, 4),
                "v6_supp_cat": supp_v6["category"] or "none",
                "v7_supp_cat": supp_v7["category"] or "none",
                "v6_triggered": ev_v6 is not None,
                "v7_trigger_type": a["trigger_type"],
                "crest_db": round(crest, 2),
                "peak": round(peak, 4),
                "centroid_hz": round(cent, 1),
                "low_ratio": round(lo, 3),
                "mid_to_low": round(m2l, 3),
                "pure_gun": round(pure_gun, 3),
                "cap_gun": round(cap_gun, 3),
                "bal_s": round(bal_s, 3),
                "fw_s": round(fw_s, 3),
                "top_yamnet": cls_str
            })
            break

df_cont_alerts = pd.DataFrame(detailed_v7)
out_dir = pathlib.Path("scratch")
df_cont_alerts.to_csv(out_dir / "v7_continuous_alerts_audit.csv", index=False)
print("\n=== V7 16 CONTINUOUS ALERTS AUDIT ===")
print(df_cont_alerts[["alert_idx", "file_time_s", "raw_score", "v6_adj_score", "v7_adj_score", "v6_supp_cat", "v7_supp_cat", "v6_triggered", "crest_db", "centroid_hz", "v7_trigger_type"]].to_string(index=False))

