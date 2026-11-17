import pandas as pd
import numpy as np
import pathlib
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from scripts.run_phase39_prospective_evaluation import evaluate_condition_on_features

p38_cache = REPO_ROOT / "experiments" / "phase38" / "feature_cache"
inv = pd.read_csv(REPO_ROOT / "experiments" / "phase41" / "phase41_recording_inventory.csv")
pos_clips = inv[inv["evaluation_partition"] == "POSITIVE_GUNSHOT"]

missed_p36 = []
detected_p36 = []

missed_p14 = []
detected_p14 = []

for _, r in pos_clips.iterrows():
    rid = r["recording_id"]
    npz = np.load(p38_cache / f"{rid}.npz")
    feats = {
        "embeddings": npz["embeddings"],
        "yamnet_scores": npz["yamnet_scores"],
        "raw_scores": npz["raw_scores"],
        "crest_factor_db": float(npz["crest_factor_db"]),
        "duration_seconds": float(npz["duration_seconds"]),
        "sample_rate": int(npz["sample_rate"])
    }
    alerts_p36 = evaluate_condition_on_features("COND6", feats, rid)
    alerts_p14 = evaluate_condition_on_features("COND1", feats, rid)
    
    max_raw = float(np.max(npz["raw_scores"])) if len(npz["raw_scores"]) > 0 else 0.0
    n_wins = len(npz["raw_scores"])
    n_above_75 = int(np.sum(npz["raw_scores"] >= 0.75))
    crest = float(npz["crest_factor_db"])
    
    info = {
        "rid": rid,
        "dur": float(npz["duration_seconds"]),
        "n_wins": n_wins,
        "n_above_75": n_above_75,
        "max_raw": max_raw,
        "crest": crest
    }
    
    if len(alerts_p36) == 0:
        missed_p36.append(info)
    else:
        detected_p36.append(rid)
        
    if len(alerts_p14) == 0:
        missed_p14.append(info)
    else:
        detected_p14.append(rid)

print(f"Phase 36: Total={len(pos_clips)}, Detected={len(detected_p36)}, Missed={len(missed_p36)}")
print(f"Phase 14: Total={len(pos_clips)}, Detected={len(detected_p14)}, Missed={len(missed_p14)}")

df_m36 = pd.DataFrame(missed_p36)
print("\n=== Phase 36 Missed Clips Breakdown ===")
print("  Max raw < 0.50 (low model confidence):", len(df_m36[df_m36["max_raw"] < 0.50]))
print("  Max raw 0.50 - 0.75 (sub-threshold):", len(df_m36[(df_m36["max_raw"] >= 0.50) & (df_m36["max_raw"] < 0.75)]))
print("  Max raw >= 0.75 (reached threshold):", len(df_m36[df_m36["max_raw"] >= 0.75]))

high_conf_m36 = df_m36[df_m36["max_raw"] >= 0.75]
print(f"\nClips with max_raw >= 0.75 missed by Phase 36 ({len(high_conf_m36)} clips):")
for _, row in high_conf_m36.iterrows():
    print(f"  {row['rid']}: dur={row['dur']:.2f}s, n_wins={row['n_wins']}, n_above_75={row['n_above_75']}, max_raw={row['max_raw']:.4f}, crest={row['crest']:.2f}dB")

