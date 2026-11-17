import numpy as np
import pandas as pd
import pathlib

inv = pd.read_csv('experiments/phase41/phase41_recording_inventory.csv')
p38 = pathlib.Path('experiments/phase38/feature_cache')
p39 = pathlib.Path('experiments/phase39/feature_cache')
p40 = pathlib.Path('experiments/phase40/feature_cache')

def get_cache(rid):
    for c in [p40, p39, p38]:
        f = c / f"{rid}.npz"
        if f.exists():
            return f
    return None

BALLISTIC_EXP_CLASSES = [420, 421, 422, 424, 425, 428, 434, 460]

# Check on genuine gunshots (120 files)
pos_recs = inv[inv['evaluation_role'] == 'PROSPECTIVE_POSITIVE_EVALUATION']
pos_ballistic_maxes = []
for _, r in pos_recs.iterrows():
    f = get_cache(r['recording_id'])
    if f:
        npz = np.load(f)
        ys = npz['yamnet_scores']
        mx = np.max(ys[:, BALLISTIC_EXP_CLASSES])
        pos_ballistic_maxes.append((r['recording_id'], mx))

pos_vals = [m[1] for m in pos_ballistic_maxes]
print(f"Genuine gunshots (N={len(pos_vals)}):")
print(f"Min ballistic max: {np.min(pos_vals):.4f}")
print(f"5th percentile:   {np.percentile(pos_vals, 5):.4f}")
print(f"Median:           {np.median(pos_vals):.4f}")
print(f"Count < 0.05:     {sum(v < 0.05 for v in pos_vals)}")
print(f"Count < 0.02:     {sum(v < 0.02 for v in pos_vals)}")
print(f"Count < 0.01:     {sum(v < 0.01 for v in pos_vals)}")

# Check low cases
low_pos = [m for m in pos_ballistic_maxes if m[1] < 0.05]
for rid, v in low_pos:
    print(f"  Low gunshot: {rid} -> {v:.4f}")

# Check on Bruxelles alert windows
npz_bxl = np.load(p40 / "p40_cont_03_bruxelles.npz")
ys_bxl = npz_bxl['yamnet_scores']
print("\nBruxelles alert windows:")
for w in [17, 47, 99, 212, 274, 318, 331, 446, 459, 531, 563, 573]:
    mx_bxl = np.max(ys_bxl[w, BALLISTIC_EXP_CLASSES])
    print(f"  Bruxelles win {w:3d} ballistic max: {mx_bxl:.4f}")
