import pandas as pd

pos = pd.read_csv("e:/gunshot/gunshot/scratch/sim_pos_results.csv")
print("Total pos:", len(pos))
print("V9 detected:", pos["v9_detected"].sum())
print("V10 detected:", pos["v10_detected"].sum())
print("\nV10 new detections:")
new_det = pos[pos["v10_detected"] & ~pos["v9_detected"]]
print(new_det[["filename", "sub_category", "condition", "v9_peak", "v10_peak"]].to_string())
print(f"Total new detections: {len(new_det)}")

still_missed = pos[~pos["v10_detected"]]
print(f"\nStill missed by V10: {len(still_missed)}")
print(still_missed[["filename", "sub_category", "condition", "v9_peak", "v10_peak"]].to_string())

