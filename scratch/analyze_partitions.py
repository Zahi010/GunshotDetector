import pandas as pd
import numpy as np

df = pd.read_csv("experiments/detector_improvement_v1/recording_level_predictions.csv")
inv = pd.read_csv("experiments/phase41/phase41_recording_inventory.csv")
merged = pd.merge(df, inv, on="recording_id", how="left")

pos_detected = merged[(merged["ground_truth_gunshot"] == 1) & (merged["v1_detected"] == 1)]
pos_missed = merged[(merged["ground_truth_gunshot"] == 1) & (merged["v1_detected"] == 0)]
fw_triggered = merged[(merged["is_fireworks_eval"] == True) & (merged["v1_detected"] == 1)]
fw_clean = merged[(merged["is_fireworks_eval"] == True) & (merged["v1_detected"] == 0)]
dist_clean = merged[(merged["is_distractor_eval"] == True) & (merged["is_fireworks_eval"] == False) & (merged["v1_detected"] == 0)]
dist_triggered = merged[(merged["is_distractor_eval"] == True) & (merged["is_fireworks_eval"] == False) & (merged["v1_detected"] == 1)]

print("=== COMPARATIVE SUMMARY OF DATASET PARTITIONS ===")
print(f"Detected Gunshots    (N={len(pos_detected):2d}): crest={pos_detected['crest_factor_db'].mean():.1f}dB, dur={pos_detected['duration_sec'].mean():.2f}s, v1_peak={pos_detected['v1_peak_score'].mean():.3f}")
print(f"Missed Gunshots      (N={len(pos_missed):2d}): crest={pos_missed['crest_factor_db'].mean():.1f}dB, dur={pos_missed['duration_sec'].mean():.2f}s, v1_peak={pos_missed['v1_peak_score'].mean():.3f}, p14_peak={pos_missed['p14_peak_score'].mean():.3f}")
print(f"Triggered Fireworks  (N={len(fw_triggered):2d}): crest={fw_triggered['crest_factor_db'].mean():.1f}dB, dur={fw_triggered['duration_sec'].mean():.2f}s, v1_peak={fw_triggered['v1_peak_score'].mean():.3f}")
print(f"Clean Fireworks      (N={len(fw_clean):2d}): crest={fw_clean['crest_factor_db'].mean():.1f}dB, dur={fw_clean['duration_sec'].mean():.2f}s, p14_peak={fw_clean['p14_peak_score'].mean():.3f}")
print(f"Triggered Distractors(N={len(dist_triggered):2d}): crest={dist_triggered['crest_factor_db'].mean():.1f}dB, dur={dist_triggered['duration_sec'].mean():.2f}s, v1_peak={dist_triggered['v1_peak_score'].mean():.3f}")
print(f"Clean Distractors    (N={len(dist_clean):2d}): crest={dist_clean['crest_factor_db'].mean():.1f}dB, dur={dist_clean['duration_sec'].mean():.2f}s, p14_peak={dist_clean['p14_peak_score'].mean():.3f}")

print("\n=== MISSED GUNSHOT ANALYSIS ===")
# Why were the 46 gunshots missed?
print("Score distribution of missed gunshots:")
print("p_max < 0.48 (no windows above off threshold):", (pos_missed['v1_peak_score'] < 0.48).sum())
print("0.48 <= p_max < 0.75 (windows reached candidate floor but below base):", ((pos_missed['v1_peak_score'] >= 0.48) & (pos_missed['v1_peak_score'] < 0.75)).sum())
print("p_max >= 0.75 (reached base threshold):", (pos_missed['v1_peak_score'] >= 0.75).sum())
print(pos_missed[pos_missed['v1_peak_score'] >= 0.75][['recording_id', 'duration_sec', 'crest_factor_db', 'v1_peak_score', 'p14_peak_score', 'p36_peak_score']])

