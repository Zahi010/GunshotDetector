"""
Prototype test script for Detector Improvement V2 ideas.
Evaluates on the DEVELOPMENT SET (218 recordings) only.
Compares V1 vs V2 candidate rules.
"""

import numpy as np
import pandas as pd
import pathlib

# Load inventory and partitions and crest factors
v1_df = pd.read_csv("experiments/detector_improvement_v1/recording_level_predictions.csv")
parts = pd.read_csv("scratch/v2_partitions.csv")
inv = pd.read_csv("experiments/phase41/phase41_recording_inventory.csv")

merged = pd.merge(v1_df, parts[['recording_id', 'v2_partition']], on='recording_id')
merged = pd.merge(merged, inv[['recording_id', 'sub_category', 'is_fireworks_eval', 'is_distractor_eval', 'is_continuous_eval']], on='recording_id')

dev_df = merged[merged['v2_partition'] == 'development'].copy()
print(f"Loaded {len(dev_df)} development recordings.")

# Feature caches
p38_cache = pathlib.Path("experiments/phase38/feature_cache")
p39_cache = pathlib.Path("experiments/phase39/feature_cache")
p40_cache = pathlib.Path("experiments/phase40/feature_cache")

def get_cache_file(rec_id):
    for c in [p38_cache, p39_cache, p40_cache]:
        f = c / f"{rec_id}.npz"
        if f.exists():
            return f
    return None

GUN_CLASSES = [421, 422, 424, 425]
FW_CLASSES = [426, 427]
THUN_CLASSES = [280, 281]
DOG_CLASSES = [69, 70, 75, 117]
CRACKLE_CLASSES = [292, 293]
SIREN_CLASSES = [317, 318, 319, 390, 391]
WIND_CLASSES = [277, 279]
IMPACT_CLASSES = [58, 352, 353, 413, 414]

def apply_v1_suppression(raw_score, ys):
    if ys is None or len(ys) == 0:
        return raw_score, None
    gun_s = max(ys[c] for c in GUN_CLASSES)
    fw_s = max(ys[c] for c in FW_CLASSES)
    thun_s = max(ys[c] for c in THUN_CLASSES)
    dog_s = max(ys[c] for c in DOG_CLASSES)
    crackle_s = max(ys[c] for c in CRACKLE_CLASSES)
    siren_s = max(ys[c] for c in SIREN_CLASSES)
    
    adj = float(raw_score)
    cat = None
    if thun_s > 0.25 and thun_s >= gun_s * 1.5:
        adj *= 0.30
        cat = "thunder"
    elif fw_s > 0.30 and fw_s >= gun_s * 1.5 and gun_s < 0.10:
        adj *= 0.35
        cat = "fireworks"
    elif dog_s > 0.30 and dog_s >= gun_s * 1.5:
        adj *= 0.35
        cat = "dog"
    elif crackle_s > 0.25 and crackle_s >= gun_s * 1.5:
        adj *= 0.35
        cat = "crackle"
    elif siren_s > 0.35 and siren_s >= gun_s * 1.5:
        adj *= 0.30
        cat = "siren"
    return adj, cat

def apply_v2_suppression(raw_score, ys):
    if ys is None or len(ys) == 0:
        return raw_score, None
    gun_s = max(ys[c] for c in GUN_CLASSES)
    fw_s = max(ys[c] for c in FW_CLASSES)
    thun_s = max(ys[c] for c in THUN_CLASSES)
    dog_s = max(ys[c] for c in DOG_CLASSES)
    crackle_s = max(ys[c] for c in CRACKLE_CLASSES)
    siren_s = max(ys[c] for c in SIREN_CLASSES)
    wind_s = max(ys[c] for c in WIND_CLASSES)
    impact_s = max(ys[c] for c in IMPACT_CLASSES)
    
    adj = float(raw_score)
    cat = None
    # 1. Thunder
    if thun_s > 0.25 and thun_s >= gun_s * 1.5:
        adj *= 0.30
        cat = "thunder"
    # 2. Fireworks - refined two tier
    elif (fw_s >= 0.45 and fw_s >= gun_s * 1.8 and gun_s < 0.28):
        adj *= 0.30
        cat = "fireworks_dominant"
    elif (fw_s >= 0.30 and fw_s >= gun_s * 1.5 and gun_s < 0.12):
        adj *= 0.35
        cat = "fireworks_standard"
    # 3. Wind buffeting
    elif (wind_s >= 0.25 and wind_s >= gun_s * 1.5):
        adj *= 0.25
        cat = "wind"
    # 4. Mechanical impact / tools
    elif (impact_s >= 0.30 and impact_s >= gun_s * 1.5 and gun_s < 0.20):
        adj *= 0.35
        cat = "mechanical_impact"
    # 5. Canine
    elif dog_s > 0.30 and dog_s >= gun_s * 1.5:
        adj *= 0.35
        cat = "canine"
    # 6. Crackle
    elif crackle_s > 0.25 and crackle_s >= gun_s * 1.5:
        adj *= 0.35
        cat = "crackle"
    # 7. Siren
    elif siren_s > 0.35 and siren_s >= gun_s * 1.5:
        adj *= 0.30
        cat = "siren"
    return adj, cat

def run_fsm_sim(scores, crest_db, dur_sec, n_win, allow_v2_single_impulse=False):
    events = []
    in_cand = False
    cand_win = None
    cooldown_until = -1.0
    
    has_sharp = (crest_db >= 12.0)
    is_short = (dur_sec <= 1.05 and n_win == 1 and crest_db >= 8.8)
    
    for i, s in enumerate(scores):
        t = i * 0.48
        if t < cooldown_until:
            continue
            
        qual_imm = (s >= 0.88 and has_sharp) or (is_short and s >= 0.75)
        
        if not in_cand:
            if qual_imm:
                events.append({"win": i, "t": t, "score": s, "dispatch": "immediate"})
                cooldown_until = t + 2.0
            elif s >= 0.75:
                in_cand = True
                cand_win = (i, t, s)
        else:
            # currently in CANDIDATE
            if qual_imm:
                events.append({"win": i, "t": t, "score": s, "dispatch": "immediate"})
                in_cand = False
                cooldown_until = t + 2.0
            elif s >= 0.75:
                # 2-window confirmed!
                events.append({"win": cand_win[0], "t": cand_win[1], "score": cand_win[2], "dispatch": "multi_window"})
                in_cand = False
                cooldown_until = t + 2.0
            else:
                # decayed below 0.75
                if allow_v2_single_impulse:
                    if cand_win[2] >= 0.78 and crest_db >= 14.0:
                        events.append({"win": cand_win[0], "t": cand_win[1], "score": cand_win[2], "dispatch": "single_round_impulse"})
                        cooldown_until = cand_win[1] + 2.0
                in_cand = False
    return events

# Run simulation
results = []
for _, r in dev_df.iterrows():
    rec_id = r['recording_id']
    cf = get_cache_file(rec_id)
    if cf is None:
        continue
    npz = np.load(cf)
    raw_s = npz['raw_scores']
    ys = npz['yamnet_scores']
    crest = r['crest_factor_db']
    dur = r['duration_sec']
    n_win = len(raw_s)
    
    # V1 scores
    v1_scores = [apply_v1_suppression(raw_s[i], ys[i])[0] for i in range(n_win)]
    v1_evs = run_fsm_sim(v1_scores, crest, dur, n_win, allow_v2_single_impulse=False)
    
    # V2 scores
    v2_scores = [apply_v2_suppression(raw_s[i], ys[i])[0] for i in range(n_win)]
    v2_evs = run_fsm_sim(v2_scores, crest, dur, n_win, allow_v2_single_impulse=True)
    
    results.append({
        "recording_id": rec_id,
        "sub_category": r['sub_category'],
        "ground_truth": r['ground_truth_gunshot'],
        "crest_db": crest,
        "v1_det": len(v1_evs) > 0,
        "v1_count": len(v1_evs),
        "v2_det": len(v2_evs) > 0,
        "v2_count": len(v2_evs)
    })

res_df = pd.DataFrame(results)

print("\n=== DEVELOPMENT SET PERFORMANCE COMPARISON ===")
for sc in sorted(res_df['sub_category'].unique()):
    sub = res_df[res_df['sub_category'] == sc]
    gt = sub['ground_truth'].iloc[0]
    n_recs = len(sub)
    v1_dets = sub['v1_det'].sum()
    v2_dets = sub['v2_det'].sum()
    v1_ev_sum = sub['v1_count'].sum()
    v2_ev_sum = sub['v2_count'].sum()
    print(f"{sc:26s} (N={n_recs:2d}, GT={gt}): V1 det={v1_dets:2d} (events={v1_ev_sum:2d}) -> V2 det={v2_dets:2d} (events={v2_ev_sum:2d})")

# Summary metrics
pos = res_df[res_df['ground_truth'] == 1]
fw = res_df[res_df['sub_category'] == 'DISTRACTOR_FIREWORKS']
env = res_df[res_df['sub_category'].str.startswith('DISTRACTOR_') & (res_df['sub_category'] != 'DISTRACTOR_FIREWORKS')]
cont = res_df[res_df['sub_category'] == 'LONG_AMBIENT_STREAM']

print("\n--- SUMMARY TOTALS ON DEV SET ---")
print(f"Positive Gunshots Recall: V1={pos['v1_det'].sum()}/{len(pos)} ({pos['v1_det'].mean()*100:.1f}%) -> V2={pos['v2_det'].sum()}/{len(pos)} ({pos['v2_det'].mean()*100:.1f}%)")
print(f"Fireworks False Alarms:   V1={fw['v1_det'].sum()}/{len(fw)} -> V2={fw['v2_det'].sum()}/{len(fw)} (reduction: {fw['v1_det'].sum() - fw['v2_det'].sum()})")
print(f"Environmental FAs:       V1={env['v1_det'].sum()}/{len(env)} -> V2={env['v2_det'].sum()}/{len(env)}")
print(f"Continuous Alerts (evs):  V1={cont['v1_count'].sum()} -> V2={cont['v2_count'].sum()} (reduction: {cont['v1_count'].sum() - cont['v2_count'].sum()})")
