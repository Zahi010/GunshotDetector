import pandas as pd
import numpy as np
import pathlib
import sys

REPO = pathlib.Path(".")
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from scripts.run_phase39_prospective_evaluation import evaluate_condition_on_features

print("=== PHASE 39 DISTRACTOR RESULTS TABLE ===")
p39_res = pd.read_csv("experiments/phase39/phase39_distractor_results.csv")
for _, r in p39_res.iterrows():
    print(f"{r['condition_id']} ({r['architecture_profile']}): total_trig={r['total_triggered_clips']}/220, fw_trig={r['distractor_fireworks_count']}/100")

print("\n=== PHASE 40 CONDITION COMPARISON TABLE ===")
p40_res = pd.read_csv("experiments/phase40/phase40_condition_comparison.csv")
for _, r in p40_res.iterrows():
    print(f"{r['condition_id']} ({r['condition_name']}): dist_rate={r['distractor_trigger_rate_220']}, fw_rate={r['fireworks_trigger_rate_100']}")

# Now let's evaluate all 100 fireworks clips using evaluate_condition_on_features for COND1, COND2, COND3, COND4, COND5, COND6
inv = pd.read_csv("experiments/phase41/phase41_recording_inventory.csv")
fw_clips = inv[inv["is_fireworks_eval"] == True].copy()
cache_dir = REPO / "experiments" / "phase39" / "feature_cache"

print(f"\nEvaluating {len(fw_clips)} fireworks clips with evaluate_condition_on_features...")

results_by_cond = {c: [] for c in ["COND1", "COND2", "COND3", "COND4", "COND5", "COND6"]}

for _, row in fw_clips.iterrows():
    rid = row["recording_id"]
    npz_p = cache_dir / f"{rid}.npz"
    npz = np.load(npz_p)
    feats = {
        "embeddings": npz["embeddings"],
        "yamnet_scores": npz["yamnet_scores"],
        "raw_scores": npz["raw_scores"],
        "crest_factor_db": float(npz["crest_factor_db"]),
        "duration_seconds": float(npz["duration_seconds"]),
        "sample_rate": int(npz["sample_rate"])
    }
    
    for cond in ["COND1", "COND2", "COND3", "COND4", "COND5", "COND6"]:
        ev = evaluate_condition_on_features(cond, feats, rid)
        results_by_cond[cond].append({
            "recording_id": rid,
            "triggered": len(ev) > 0,
            "alert_count": len(ev)
        })

for cond in ["COND1", "COND2", "COND3", "COND4", "COND5", "COND6"]:
    df_c = pd.DataFrame(results_by_cond[cond])
    n_trig = df_c["triggered"].sum()
    print(f"Re-evaluated {cond}: Triggered = {n_trig} / {len(fw_clips)}")

