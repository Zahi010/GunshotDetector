import sys, pathlib
REPO = pathlib.Path(".")
if str(REPO.resolve()) not in sys.path:
    sys.path.insert(0, str(REPO.resolve()))

import numpy as np
from scripts.run_phase39_prospective_evaluation import evaluate_condition_on_features

npz = np.load("experiments/phase39/feature_cache/p39_dist_DISTRACTOR_FIREWORKS_273320.npz")
feats = {
    "embeddings": npz["embeddings"],
    "yamnet_scores": npz["yamnet_scores"],
    "raw_scores": npz["raw_scores"],
    "crest_factor_db": float(npz["crest_factor_db"]),
    "duration_seconds": float(npz["duration_seconds"]),
    "sample_rate": int(npz["sample_rate"])
}
ev1 = evaluate_condition_on_features("COND1", feats, "p39_dist_DISTRACTOR_FIREWORKS_273320")
print(f"evaluate_condition_on_features COND1: {len(ev1)}")

