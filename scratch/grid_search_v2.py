"""
Systematic parameter grid search on the DEVELOPMENT SET (218 recordings).
Evaluates recall on positive gunshots, false alarm count on fireworks,
false alarms on environmental distractors, and total events on continuous streams.
"""

import numpy as np
import pandas as pd
import pathlib

# Load inventory and partitions
inv = pd.read_csv("experiments/phase41/phase41_recording_inventory.csv")
parts = pd.read_csv("scratch/v2_partitions.csv")
v1_df = pd.read_csv("experiments/detector_improvement_v1/recording_level_predictions.csv")

merged = pd.merge(v1_df, parts[['recording_id', 'v2_partition']], on='recording_id')
merged = pd.merge(merged, inv[['recording_id', 'sub_category', 'duration_seconds']], on='recording_id')

dev_df = merged[merged['v2_partition'] == 'development'].copy()
print(f"Loaded {len(dev_df)} development recordings.")

p38_cache = pathlib.Path("experiments/phase38/feature_cache")
p39_cache = pathlib.Path("experiments/phase39/feature_cache")
p40_cache = pathlib.Path("experiments/phase40/feature_cache")

def get_cache(rid):
    for c in [p38_cache, p39_cache, p40_cache]:
        f = c / f"{rid}.npz"
        if f.exists():
            return f
    return None

# Pre-load cache data for dev set
dev_data = []
for _, r in dev_df.iterrows():
    rid = r['recording_id']
    cf = get_cache(rid)
    if cf is None:
        continue
    npz = np.load(cf)
    dev_data.append({
        "recording_id": rid,
        "sub_category": r['sub_category'],
        "ground_truth": r['ground_truth_gunshot'],
        "duration_sec": r['duration_sec'],
        "crest_factor_db": r['crest_factor_db'],
        "raw_scores": npz['raw_scores'],
        "yamnet_scores": npz['yamnet_scores']
    })

GUN_CLASSES = [421, 422, 424, 425]
FW_CLASSES = [426, 427]
THUN_CLASSES = [280, 281]
DOG_CLASSES = [69, 70, 75, 117]
CRACKLE_CLASSES = [292, 293]
SIREN_CLASSES = [317, 318, 319, 390, 391]
WIND_CLASSES = [277, 279]
IMPACT_CLASSES = [58, 352, 353, 413, 414]

def evaluate_dev(
    th_base=0.75,
    th_high=0.85,
    th_off=0.48,
    single_crest=13.0,
    fw_gun_max=0.25,
    fw_ratio=1.5,
    fw_th=0.30,
    wind_enabled=True,
    impact_enabled=True
):
    pos_detected = 0
    total_pos = 0
    fw_fps = 0
    total_fw = 0
    env_fps = 0
    total_env = 0
    cont_events = 0

    for d in dev_data:
        raw_s = d['raw_scores']
        ys = d['yamnet_scores']
        crest = d['crest_factor_db']
        dur = d['duration_sec']
        n_win = len(raw_s)
        sc = d['sub_category']
        gt = d['ground_truth']

        if gt == 1:
            total_pos += 1
        elif sc == 'DISTRACTOR_FIREWORKS':
            total_fw += 1
        elif sc.startswith('DISTRACTOR_'):
            total_env += 1

        # Calculate adjusted scores
        adj_scores = []
        for i in range(n_win):
            raw = float(raw_s[i])
            y = ys[i] if (ys is not None and i < len(ys)) else None
            if y is None or len(y) == 0:
                adj_scores.append(raw)
                continue

            gun_s = max(y[c] for c in GUN_CLASSES)
            fw_s = max(y[c] for c in FW_CLASSES)
            thun_s = max(y[c] for c in THUN_CLASSES)
            dog_s = max(y[c] for c in DOG_CLASSES)
            crackle_s = max(y[c] for c in CRACKLE_CLASSES)
            siren_s = max(y[c] for c in SIREN_CLASSES)
            wind_s = max(y[c] for c in WIND_CLASSES)
            impact_s = max(y[c] for c in IMPACT_CLASSES)

            adj = raw
            # Thunder
            if thun_s > 0.25 and thun_s >= gun_s * 1.5:
                adj *= 0.30
            # Fireworks
            elif fw_s >= fw_th and fw_s >= gun_s * fw_ratio and gun_s < fw_gun_max:
                adj *= 0.35
            # Wind
            elif wind_enabled and wind_s >= 0.25 and wind_s >= gun_s * 1.5:
                adj *= 0.25
            # Mechanical Impact
            elif impact_enabled and impact_s >= 0.30 and impact_s >= gun_s * 1.5 and gun_s < 0.20:
                adj *= 0.35
            # Canine
            elif dog_s > 0.30 and dog_s >= gun_s * 1.5:
                adj *= 0.35
            # Crackle
            elif crackle_s > 0.25 and crackle_s >= gun_s * 1.5:
                adj *= 0.35
            # Siren
            elif siren_s > 0.35 and siren_s >= gun_s * 1.5:
                adj *= 0.30

            adj_scores.append(adj)

        # FSM run
        events = []
        in_cand = False
        cand_win = None
        cooldown_until = -1.0
        has_sharp = (crest >= single_crest)
        is_short = (dur <= 1.05 and n_win == 1 and crest >= 8.8)

        for i, s in enumerate(adj_scores):
            t = i * 0.48
            if t < cooldown_until:
                continue

            qual_imm = (s >= th_high and has_sharp) or (is_short and s >= th_base)

            if not in_cand:
                if qual_imm:
                    events.append(i)
                    cooldown_until = t + 2.0
                elif s >= th_base:
                    in_cand = True
                    cand_win = (i, t, s)
            else:
                if qual_imm:
                    events.append(i)
                    in_cand = False
                    cooldown_until = t + 2.0
                elif s >= th_base:
                    events.append(cand_win[0])
                    in_cand = False
                    cooldown_until = t + 2.0
                else:
                    in_cand = False

        is_det = len(events) > 0
        if gt == 1 and is_det:
            pos_detected += 1
        elif sc == 'DISTRACTOR_FIREWORKS' and is_det:
            fw_fps += 1
        elif sc.startswith('DISTRACTOR_') and is_det:
            env_fps += 1
        elif sc == 'LONG_AMBIENT_STREAM':
            cont_events += len(events)

    return {
        "pos_recall": pos_detected / total_pos,
        "pos_count": pos_detected,
        "fw_fps": fw_fps,
        "env_fps": env_fps,
        "cont_events": cont_events
    }

print("Baseline V1 equivalent:")
res_v1 = evaluate_dev(th_base=0.75, th_high=0.88, th_off=0.48, single_crest=12.0, fw_gun_max=0.10, fw_ratio=1.5, fw_th=0.30, wind_enabled=False, impact_enabled=False)
print(f"V1: Recall={res_v1['pos_count']}/72 ({res_v1['pos_recall']*100:.1f}%), FW_FP={res_v1['fw_fps']}/59, Env_FP={res_v1['env_fps']}/72, Cont_Events={res_v1['cont_events']}")

# Test variations
print("\nTesting parameter configurations on DEV set...")
configs = [
    {"th_high": 0.88, "single_crest": 12.0, "fw_gun_max": 0.25, "fw_th": 0.30, "wind": True, "impact": True},
    {"th_high": 0.85, "single_crest": 13.0, "fw_gun_max": 0.25, "fw_th": 0.30, "wind": True, "impact": True},
    {"th_high": 0.84, "single_crest": 13.5, "fw_gun_max": 0.25, "fw_th": 0.30, "wind": True, "impact": True},
    {"th_high": 0.84, "single_crest": 14.0, "fw_gun_max": 0.28, "fw_th": 0.28, "wind": True, "impact": True},
    {"th_high": 0.83, "single_crest": 14.0, "fw_gun_max": 0.28, "fw_th": 0.28, "wind": True, "impact": True},
    {"th_high": 0.82, "single_crest": 14.0, "fw_gun_max": 0.28, "fw_th": 0.28, "wind": True, "impact": True},
]

for cfg in configs:
    r = evaluate_dev(
        th_base=0.75,
        th_high=cfg["th_high"],
        single_crest=cfg["single_crest"],
        fw_gun_max=cfg["fw_gun_max"],
        fw_th=cfg["fw_th"],
        wind_enabled=cfg["wind"],
        impact_enabled=cfg["impact"]
    )
    print(f"Cfg (th_high={cfg['th_high']}, crest={cfg['single_crest']}, fw_max={cfg['fw_gun_max']}): Recall={r['pos_count']}/72 ({r['pos_recall']*100:.1f}%), FW_FP={r['fw_fps']}/59, Env_FP={r['env_fps']}/72, Cont_Events={r['cont_events']}")

