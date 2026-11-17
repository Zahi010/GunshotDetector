import pandas as pd
import numpy as np
import pathlib

df = pd.read_csv("experiments/detector_improvement_v1/recording_level_predictions.csv")
inv = pd.read_csv("experiments/phase41/phase41_recording_inventory.csv")
merged = pd.merge(df, inv, on="recording_id", how="left")
fw_triggered = merged[(merged["is_fireworks_eval"] == True) & (merged["v1_detected"] == 1)]

p39_cache = pathlib.Path("experiments/phase39/feature_cache")

print(f"=== INSPECTING THE 45 TRIGGERED FIREWORKS RECORDINGS ===")
# Check why semantic suppression did not attenuate them
fw_classes = [426, 427] # fireworks, firecracker
gun_classes = [421, 422, 424, 425]

n_suppressed = 0
n_fw_score_low = 0
n_gun_score_high = 0

for _, r in fw_triggered.iterrows():
    npz = np.load(p39_cache / f"{r['recording_id']}.npz")
    ys = npz["yamnet_scores"] # (T, 521)
    raws = npz["raw_scores"]
    max_fw = np.max(ys[:, fw_classes])
    max_gun = np.max(ys[:, gun_classes])
    peak_win = np.argmax(raws)
    pk_fw = np.max(ys[peak_win, fw_classes])
    pk_gun = np.max(ys[peak_win, gun_classes])
    print(f"FW FP: {r['recording_id']}: max_raw={np.max(raws):.3f}, pk_win_raw={raws[peak_win]:.3f}, pk_fw={pk_fw:.3f}, pk_gun={pk_gun:.3f}, max_fw_ever={max_fw:.3f}")

