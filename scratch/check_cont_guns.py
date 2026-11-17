import numpy as np
import pandas as pd
import pathlib

inv = pd.read_csv('experiments/phase41/phase41_recording_inventory.csv')
cont = inv[inv['is_continuous_eval'] == True]
GUN_CLASSES = [421, 422, 424, 425]
p38 = pathlib.Path('experiments/phase38/feature_cache')
p39 = pathlib.Path('experiments/phase39/feature_cache')
p40 = pathlib.Path('experiments/phase40/feature_cache')

all_max_guns = []
for _, r in cont.iterrows():
    for c in [p40, p39, p38]:
        f = c / f"{r['recording_id']}.npz"
        if f.exists():
            npz = np.load(f)
            ys = npz['yamnet_scores']
            mg = np.max(ys[:, GUN_CLASSES])
            all_max_guns.append((r['recording_id'], mg, len(ys)))
            break

for rid, mg, nw in all_max_guns:
    print(f"{rid:30s}: max_gun={mg:.4f} ({nw:4d} windows)")

