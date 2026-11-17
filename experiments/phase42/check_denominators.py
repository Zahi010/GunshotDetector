import pandas as pd
import soundfile as sf
import pathlib

inv = pd.read_csv("experiments/phase41/phase41_recording_inventory.csv")
print("=== INVENTORY PARTITION COUNTS & SUMS ===")
for p, g in inv.groupby("evaluation_partition"):
    print(f"Partition {p}: {len(g)} files, {g['duration_seconds'].sum():.2f} s ({g['duration_seconds'].sum()/3600:.4f} hr)")

print(f"Total inventory: {len(inv)} files, {inv['duration_seconds'].sum():.2f} s ({inv['duration_seconds'].sum()/3600:.4f} hr)")

cont_inv = inv[inv["evaluation_partition"] == "CONTINUOUS_AMBIENT"].copy()
print("\n=== CONTINUOUS STREAMS IN INVENTORY ===")
print(f"Count of continuous streams: {len(cont_inv)}")
print(f"Sum of continuous duration_seconds: {cont_inv['duration_seconds'].sum():.2f} s ({cont_inv['duration_seconds'].sum()/3600:.4f} hr)")

recon = pd.read_csv("experiments/phase41/phase41_continuous_reconstruction.csv")
recon_cond1 = recon[recon["condition_id"] == "COND1"]
print(f"Reconstruction COND1 count: {len(recon_cond1)}")
print(f"Sum of reconstruction duration_seconds: {recon_cond1['duration_seconds'].sum():.2f} s ({recon_cond1['duration_seconds'].sum()/3600:.4f} hr)")

diff = inv['duration_seconds'].sum() - recon_cond1['duration_seconds'].sum()
print(f"\nDifference (Total Inventory - Continuous Reconstruction): {diff:.2f} s ({diff/3600:.4f} hr)")

# Check the short clips sum:
short_clips = inv[inv["evaluation_partition"] != "CONTINUOUS_AMBIENT"]
print(f"Short clips sum: {short_clips['duration_seconds'].sum():.2f} s ({short_clips['duration_seconds'].sum()/3600:.4f} hr)")

