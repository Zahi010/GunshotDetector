import pandas as pd
import numpy as np
import pathlib
import sys

REPO = pathlib.Path(".")
if str(REPO.resolve()) not in sys.path:
    sys.path.insert(0, str(REPO.resolve()))

from scripts.run_phase39_prospective_evaluation import evaluate_condition_on_features

inv = pd.read_csv("experiments/phase41/phase41_recording_inventory.csv")
fw_clips = inv[inv["is_fireworks_eval"] == True].copy()
cache_dir = REPO / "experiments" / "phase39" / "feature_cache"

rows = []
for _, row in fw_clips.iterrows():
    rid = row["recording_id"]
    npz = np.load(cache_dir / f"{rid}.npz")
    feats = {
        "embeddings": npz["embeddings"],
        "yamnet_scores": npz["yamnet_scores"],
        "raw_scores": npz["raw_scores"],
        "crest_factor_db": float(npz["crest_factor_db"]),
        "duration_seconds": float(npz["duration_seconds"]),
        "sample_rate": int(npz["sample_rate"])
    }
    
    ev1 = evaluate_condition_on_features("COND1", feats, rid)
    ev2 = evaluate_condition_on_features("COND2", feats, rid)
    ev3 = evaluate_condition_on_features("COND3", feats, rid)
    ev6 = evaluate_condition_on_features("COND6", feats, rid)
    
    raw_max = float(np.max(npz["raw_scores"])) if len(npz["raw_scores"]) > 0 else 0.0
    
    rows.append({
        "recording_id": rid,
        "uploader_or_creator": row["uploader_or_recordist"],
        "duration_seconds": round(float(npz["duration_seconds"]), 3),
        "crest_factor_db": round(float(npz["crest_factor_db"]), 2),
        "max_raw_score": round(raw_max, 4),
        "cond1_phase14_triggered": len(ev1) > 0,
        "cond2_phase17_triggered": len(ev2) > 0,
        "cond3_phase31_triggered": len(ev3) > 0,
        "cond6_phase36_triggered": len(ev6) > 0,
        "cond1_alerts": len(ev1),
        "cond2_alerts": len(ev2),
        "cond3_alerts": len(ev3),
        "cond6_alerts": len(ev6),
    })

df = pd.DataFrame(rows)
print("=== TRIGGER TOTALS (/100) ===")
print("COND1 (Phase 14):", df["cond1_phase14_triggered"].sum())
print("COND2 (Phase 17):", df["cond2_phase17_triggered"].sum())
print("COND3 (Phase 31):", df["cond3_phase31_triggered"].sum())
print("COND6 (Phase 36):", df["cond6_phase36_triggered"].sum())

# Breakdown of COND2 vs COND3 (where candidate defect causes extra fireworks triggers)
diff_c2_c3 = df[df["cond2_phase17_triggered"] != df["cond3_phase31_triggered"]]
print(f"\nDiscordant clips between COND2 and COND3: {len(diff_c2_c3)}")
print(diff_c2_c3[["recording_id", "uploader_or_creator", "crest_factor_db", "cond2_phase17_triggered", "cond3_phase31_triggered"]])

# Breakdown of COND2 vs COND1
diff_c2_c1 = df[df["cond2_phase17_triggered"] != df["cond1_phase14_triggered"]]
print(f"\nDiscordant clips between COND2 and COND1: {len(diff_c2_c1)}")

# Breakdown of COND6 vs COND1 (The 10 discordant clips)
diff_c6_c1 = df[df["cond6_phase36_triggered"] != df["cond1_phase14_triggered"]]
print(f"\nDiscordant clips between COND6 and COND1: {len(diff_c6_c1)}")
assert len(diff_c6_c1) == 10
assert (diff_c6_c1["cond6_phase36_triggered"] == True).all()
assert (diff_c6_c1["cond1_phase14_triggered"] == False).all()
print("Phase 14 vs Phase 36 paired 2x2 matrix matches exactly (10 discordant clips)!")

