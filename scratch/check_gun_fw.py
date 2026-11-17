import sys
sys.path.insert(0, '.')
from scratch.test_coherence import dev_data, GUN_CLASSES, FW_CLASSES

for d in dev_data:
    if d['ground_truth'] != 1: continue
    raw_s = d['raw_scores']
    ys = d['yamnet_scores']
    for i in range(len(raw_s)):
        fw = max(ys[i, FW_CLASSES])
        gun = max(ys[i, GUN_CLASSES])
        if fw >= 0.40:
            print(f"{d['recording_id']} win {i}: fw={fw:.3f}, gun={gun:.3f}, raw={raw_s[i]:.3f}")

