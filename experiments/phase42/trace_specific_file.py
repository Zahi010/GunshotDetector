import sys
import pathlib
REPO = pathlib.Path(".")
if str(REPO.resolve()) not in sys.path:
    sys.path.insert(0, str(REPO.resolve()))

import numpy as np
from model_phase14 import merge_phase14_events

npz = np.load("experiments/phase39/feature_cache/p39_dist_DISTRACTOR_FIREWORKS_273320.npz")
raw = npz["raw_scores"]
dur = float(npz["duration_seconds"])
crest = float(npz["crest_factor_db"])
print(f"p39_dist_DISTRACTOR_FIREWORKS_273320: dur={dur}, crest={crest}")

wins = []
for i in range(len(raw)):
    wins.append({
        "window_index": i, "start_time": round(i*0.48, 3), "end_time": round(i*0.48+0.96, 3),
        "score": float(raw[i]), "raw_ensemble_score": float(raw[i])
    })

ev1 = merge_phase14_events(wins, 0.75, 0.88, 0.48, 2, 2.0, dur, True, crest, 8.8, 12.0)
print(f"Events produced: {len(ev1)}")
for ev in ev1:
    print(ev)
