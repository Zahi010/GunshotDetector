import pandas as pd
df = pd.read_csv("e:/gunshot/gunshot/scratch/sim_neg_results.csv")
print(df[df["sub_category"] == "hard_negative_balloon_burst"][["filename", "v9_detected", "v10_detected", "v9_peak", "v10_peak"]].to_string())

