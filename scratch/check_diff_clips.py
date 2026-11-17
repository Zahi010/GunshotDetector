import pandas as pd
import numpy as np
import pathlib
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from scratch.test_v1_benchmark import evaluate_integrated_v1
from scripts.run_phase39_prospective_evaluation import evaluate_condition_on_features

p38_cache = REPO_ROOT / "experiments" / "phase38" / "feature_cache"
inv = pd.read_csv(REPO_ROOT / "experiments" / "phase41" / "phase41_recording_inventory.csv")
pos_clips = inv[inv["evaluation_partition"] == "POSITIVE_GUNSHOT"]

for _, r in pos_clips.iterrows():
    npz = np.load(p38_cache / f"{r['recording_id']}.npz")
    feats = {
        "embeddings": npz["embeddings"], "yamnet_scores": npz["yamnet_scores"],
        "raw_scores": npz["raw_scores"], "crest_factor_db": float(npz["crest_factor_db"]),
        "duration_seconds": float(npz["duration_seconds"]), "sample_rate": int(npz["sample_rate"])
    }
    ev36 = evaluate_condition_on_features("COND6", feats, r["recording_id"])
    ev_v1 = evaluate_integrated_v1(feats, r["recording_id"])
    if len(ev36) > 0 and len(ev_v1) == 0:
        print(f"Diff clip: {r['recording_id']}, raw_max={np.max(npz['raw_scores']):.3f}, crest={float(npz['crest_factor_db']):.1f}dB, dur={float(npz['duration_seconds']):.2f}s")

