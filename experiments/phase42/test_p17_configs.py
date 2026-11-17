import pandas as pd
import numpy as np
import pathlib
import sys

REPO = pathlib.Path(".")
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from model_phase17 import merge_phase17_events
from experiments.phase31.model_phase17_state_reset_candidate import merge_phase17_events as merge_phase31_events

inv = pd.read_csv("experiments/phase41/phase41_recording_inventory.csv")
fw_clips = inv[inv["is_fireworks_eval"] == True].copy()
cache_dir = REPO / "experiments" / "phase39" / "feature_cache"

YAMNET_CLASS_DOG = 74
YAMNET_CLASS_BARK = 75
YAMNET_CLASS_YIP = 76
YAMNET_CLASS_CANIDAE = 77

# Test various parameter combinations for Phase 17 on fireworks
configs = [
    ("P17_standard (allow_short=True, crest=12.0)", True, 12.0, 8.8, False),
    ("P17_no_short_clip (allow_short=False, crest=12.0)", False, 12.0, 8.8, False),
    ("P17_no_crest_gate (crest=None)", True, None, None, False),
    ("P17_high_crest_gate (crest=14.0)", True, 14.0, 8.8, False),
    ("P17_reset_candidate (COND3)", True, 12.0, 8.8, True),
    ("P17_reset_candidate_no_short", False, 12.0, 8.8, True),
]

for name, allow_short, single_crest, min_crest, is_reset in configs:
    trig_cnt = 0
    fn = merge_phase31_events if is_reset else merge_phase17_events
    for _, row in fw_clips.iterrows():
        rid = row["recording_id"]
        npz = np.load(cache_dir / f"{rid}.npz")
        raw_scores = npz["raw_scores"]
        yamnet_scores = npz["yamnet_scores"]
        dur_sec = float(npz["duration_seconds"])
        crest_db = float(npz["crest_factor_db"])
        
        n_windows = len(raw_scores)
        window_results = []
        for i in range(n_windows):
            raw_s = float(raw_scores[i])
            cal_s = raw_s
            dog_s = max(yamnet_scores[i, c] for c in [74, 75, 76, 77] if c < yamnet_scores.shape[1])
            if dog_s > 0.35:
                cal_s *= 0.30
            window_results.append({
                "window_index": i, "start_time": round(i*0.48, 3), "end_time": round(i*0.48+0.96, 3),
                "score": round(cal_s, 4), "raw_ensemble_score": round(raw_s, 4),
                "triggered": cal_s >= 0.75
            })
            
        ev = fn(
            window_results=window_results,
            threshold_base=0.75,
            threshold_high=0.88,
            threshold_off=0.48,
            confirm_windows=2,
            cooldown_secs=2.0,
            audio_duration_sec=dur_sec,
            allow_short_clip_exception=allow_short,
            crest_factor_db=crest_db if single_crest is not None else None,
            min_crest_factor_db=min_crest if min_crest is not None else 8.8,
            single_win_min_crest_db=single_crest if single_crest is not None else 12.0
        )
        if len(ev) > 0:
            trig_cnt += 1
    print(f"{name}: {trig_cnt} / 100 triggered")

