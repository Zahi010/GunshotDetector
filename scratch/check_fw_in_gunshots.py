import numpy as np
import pandas as pd
import pathlib

df = pd.read_csv("experiments/detector_improvement_v1/recording_level_predictions.csv")
inv = pd.read_csv("experiments/phase41/phase41_recording_inventory.csv")
merged = pd.merge(df, inv, on="recording_id", how="left")
pos_clips = merged[merged["ground_truth_gunshot"] == 1]

p38_cache = pathlib.Path("experiments/phase38/feature_cache")
fw_classes = [426, 427]
gun_classes = [421, 422, 424, 425]

max_fw_in_gunshots = []
for _, r in pos_clips.iterrows():
    npz = np.load(p38_cache / f"{r['recording_id']}.npz")
    ys = npz["yamnet_scores"]
    max_fw_in_gunshots.append(float(np.max(ys[:, fw_classes])))

max_fw_in_gunshots = np.array(max_fw_in_gunshots)
print(f"Max fireworks score in genuine gunshots (N={len(max_fw_in_gunshots)}):")
print(f"Max: {np.max(max_fw_in_gunshots):.3f}")
print(f"Quantiles: 50%={np.percentile(max_fw_in_gunshots, 50):.3f}, 75%={np.percentile(max_fw_in_gunshots, 75):.3f}, 90%={np.percentile(max_fw_in_gunshots, 90):.3f}, 95%={np.percentile(max_fw_in_gunshots, 95):.3f}")
print(f"Gunshots with max_fw > 0.30: {(max_fw_in_gunshots > 0.30).sum()}")
for idx in np.where(max_fw_in_gunshots > 0.30)[0]:
    r = pos_clips.iloc[idx]
    print(f"  Gunshot with high fw: {r['recording_id']}, max_fw={max_fw_in_gunshots[idx]:.3f}")

