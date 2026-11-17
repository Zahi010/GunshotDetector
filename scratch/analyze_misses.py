import pandas as pd
import numpy as np
import pathlib

df = pd.read_csv("experiments/detector_improvement_v1/recording_level_predictions.csv")
inv = pd.read_csv("experiments/phase41/phase41_recording_inventory.csv")
merged = pd.merge(df, inv, on="recording_id", how="left")
pos_missed = merged[(merged["ground_truth_gunshot"] == 1) & (merged["v1_detected"] == 0)]

p38_cache = pathlib.Path("experiments/phase38/feature_cache")
raw_maxes = []
for _, r in pos_missed.iterrows():
    npz = np.load(p38_cache / f"{r['recording_id']}.npz")
    raw_s = npz["raw_scores"]
    raw_maxes.append(float(np.max(raw_s)) if len(raw_s) > 0 else 0.0)

raw_maxes = np.array(raw_maxes)
print("Actual max raw scores for the 46 missed gunshots:")
print(f"raw_max < 0.20: {(raw_maxes < 0.20).sum()}")
print(f"0.20 <= raw_max < 0.48: {((raw_maxes >= 0.20) & (raw_maxes < 0.48)).sum()}")
print(f"0.48 <= raw_max < 0.75: {((raw_maxes >= 0.48) & (raw_maxes < 0.75)).sum()}")
print(f"0.75 <= raw_max < 0.88: {((raw_maxes >= 0.75) & (raw_maxes < 0.88)).sum()}")
print(f"raw_max >= 0.88: {(raw_maxes >= 0.88).sum()}")

high_indices = np.where(raw_maxes >= 0.70)[0]
for idx in high_indices:
    r = pos_missed.iloc[idx]
    print(f"High raw miss: {r['recording_id']}, raw_max={raw_maxes[idx]:.3f}, dur={r['duration_sec']:.2f}s, crest={r['crest_factor_db']:.1f}dB, subcat={r['sub_category']}")

