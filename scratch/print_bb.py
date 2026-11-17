import pandas as pd
df = pd.read_csv("scratch/balloon_burst_forensics.csv")
print("Balloon bursts spectral breakdown:")
for _, r in df.iterrows():
    print(f"{r['filename']}: lo={r['lo_at_peak']:.4f}, mid={r['mid_at_peak']:.4f}, hi={r['hi_at_peak']:.4f}, m2l={r['m2l_at_peak']:.4f}, cent={r['cent_at_peak']:.0f}Hz")

