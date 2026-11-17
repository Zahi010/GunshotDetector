import pandas as pd
df = pd.read_csv("scratch/positives_lo_m2l.csv")
print("Top 10 highest centroid gunshots:")
print(df.sort_values(by="cent", ascending=False)[["filename", "category", "cent", "lo", "hi", "m2l"]].head(10))
print("\nLowest lo gunshots:")
print(df.sort_values(by="lo", ascending=True)[["filename", "category", "cent", "lo", "hi", "m2l"]].head(10))
print(f"Any gunshot with cent > 3200 Hz? {(df['cent'] > 3200).sum()}")
print(f"Any gunshot with lo < 0.02? {(df['lo'] < 0.02).sum()}")
print(f"Any gunshot with hi > 0.75? {(df['hi'] > 0.75).sum()}")

