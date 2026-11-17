import pandas as pd
df_pos = pd.read_csv("scratch/positives_lo_m2l.csv")
df_bb = pd.read_csv("scratch/balloon_burst_forensics.csv")

bb_matches = ((df_bb["cent_at_peak"] >= 3400) & (df_bb["hi_at_peak"] >= 0.75) & (df_bb["lo_at_peak"] <= 0.015)).sum()
pos_matches = ((df_pos["cent"] >= 3400) & (df_pos["hi"] >= 0.75) & (df_pos["lo"] <= 0.015)).sum()

print(f"Balloon bursts matching rule: {bb_matches} / {len(df_bb)} ({bb_matches / len(df_bb) * 100:.1f}%)")
print(f"Genuine gunshots matching rule: {pos_matches} / {len(df_pos)} ({pos_matches / len(df_pos) * 100:.1f}%)")

