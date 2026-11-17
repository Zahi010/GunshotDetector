import pandas as pd
import numpy as np
import pathlib
import sys

REPO = pathlib.Path(".")
if str(REPO.resolve()) not in sys.path:
    sys.path.insert(0, str(REPO.resolve()))

inv = pd.read_csv("experiments/phase41/phase41_recording_inventory.csv")
fw_clips = inv[inv["is_fireworks_eval"] == True].copy()
cache_dir = REPO / "experiments" / "phase39" / "feature_cache"

from model_phase17 import merge_phase17_events
from experiments.phase31.model_phase17_state_reset_candidate import merge_phase17_events as merge_phase31_events

# Let's grid search thresholds and suppression parameters on Phase 17
print("Searching parameter grid for Phase 17 to see if 58 or 62 triggers ever occur:")
for th_base in [0.70, 0.72, 0.75, 0.78, 0.80]:
    for th_high in [0.85, 0.88, 0.90]:
        for dog_thresh in [0.25, 0.30, 0.35, 0.40]:
            cnt_c2 = 0
            cnt_c3 = 0
            for _, row in fw_clips.iterrows():
                rid = row["recording_id"]
                npz = np.load(cache_dir / f"{rid}.npz")
                raw = npz["raw_scores"]
                yam = npz["yamnet_scores"]
                dur = float(npz["duration_seconds"])
                crest = float(npz["crest_factor_db"])
                
                wins = []
                for i in range(len(raw)):
                    r_s = float(raw[i])
                    c_s = r_s
                    d_s = max(yam[i, c] for c in [74, 75, 76, 77] if c < yam.shape[1])
                    if d_s > dog_thresh:
                        c_s *= 0.30
                    wins.append({
                        "window_index": i, "start_time": round(i*0.48, 3), "end_time": round(i*0.48+0.96, 3),
                        "score": round(c_s, 4), "raw_ensemble_score": round(r_s, 4),
                        "triggered": c_s >= th_base
                    })
                
                ev2 = merge_phase17_events(wins, th_base, th_high, 0.48, 2, 2.0, dur, True, crest, 8.8, 12.0)
                ev3 = merge_phase31_events(wins, th_base, th_high, 0.48, 2, 2.0, dur, True, crest, 8.8, 12.0)
                if len(ev2) > 0: cnt_c2 += 1
                if len(ev3) > 0: cnt_c3 += 1
                
            if cnt_c2 in [58, 62] or cnt_c3 in [58, 62]:
                print(f"MATCH! th_base={th_base}, th_high={th_high}, dog_th={dog_thresh}: COND2={cnt_c2}, COND3={cnt_c3}")
print("Grid search finished.")
