import pandas as pd

df = pd.read_csv("e:/gunshot/gunshot/experiments/phase51_validation/recording_level_predictions.csv")
pos = df[df["ground_truth_label"] == 1]
print(f"Total positive gunshots in Phase 51: {len(pos)}")
print(f"V8 detected: {pos['v8_detected'].sum()} / {len(pos)} ({pos['v8_detected'].mean()*100:.2f}%)")

missed_v8 = pos[pos["v8_detected"] == 0]
print(f"V8 missed count: {len(missed_v8)}")
print(missed_v8[["filename", "sub_category", "condition_category", "v6_detected", "v7_detected", "v8_detected", "v8_peak_score"]].to_string())
missed_v8.to_csv("e:/gunshot/gunshot/scratch/phase51_v8_missed_20.csv", index=False)

