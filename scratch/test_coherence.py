"""
Test the Non-Ballistic Acoustic Coherence Safeguard on the DEV set.
"""
import numpy as np
import pandas as pd
import pathlib

inv = pd.read_csv("experiments/phase41/phase41_recording_inventory.csv")
parts = pd.read_csv("scratch/v2_partitions.csv")
v1_df = pd.read_csv("experiments/detector_improvement_v1/recording_level_predictions.csv")

merged = pd.merge(v1_df, parts[['recording_id', 'v2_partition']], on='recording_id')
merged = pd.merge(merged, inv[['recording_id', 'sub_category', 'duration_seconds']], on='recording_id')
dev_df = merged[merged['v2_partition'] == 'development'].copy()

p38 = pathlib.Path('experiments/phase38/feature_cache')
p39 = pathlib.Path('experiments/phase39/feature_cache')
p40 = pathlib.Path('experiments/phase40/feature_cache')

def get_cache(rid):
    for c in [p40, p39, p38]:
        f = c / f"{rid}.npz"
        if f.exists():
            return f
    return None

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

BALLISTIC_EXP_CLASSES = [420, 421, 422, 424, 425, 428, 434, 460]
GUN_CLASSES = [421, 422, 424, 425]
FW_CLASSES = [426, 427]
THUN_CLASSES = [280, 281]
DOG_CLASSES = [69, 70, 75, 117]
CRACKLE_CLASSES = [292, 293]
SIREN_CLASSES = [317, 318, 319, 390, 391]
WIND_CLASSES = [277, 279]
IMPACT_CLASSES = [58, 352, 353, 413, 414]

# Semantic non-target classes (Speech, Animal, Vehicle, Outside)
NON_TARGET_CLASSES = [
    0,  # Speech
    67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, # Animal
    300, 301, 302, 303, 304, 305, 306, 307, 308, 309, 310, 311, 312, 313, 314, 315, 316, 317, 318, 319, 320, 321, 322, 323, 324, 325, 326, 327, 328, 329, 330, # Vehicle
    502, 503, 504 # Outside
]

def run_simulation(
    fw_gun_max=0.25,
    th_high=0.88,
    single_crest=12.0,
    enable_coherence_guard=True,
    enable_single_impulse_dispatch=False
):
    pos_det = 0
    pos_total = 0
    fw_fps = 0
    fw_total = 0
    env_fps = 0
    env_total = 0
    cont_events = 0
    bxl_events = 0

    for d in dev_data:
        raw_s = d['raw_scores']
        ys = d['yamnet_scores']
        crest = d['crest_factor_db']
        dur = d['duration_sec']
        n_win = len(raw_s)
        sc = d['sub_category']
        gt = d['ground_truth']
        rid = d['recording_id']

        if gt == 1:
            pos_total += 1
        elif sc == 'DISTRACTOR_FIREWORKS':
            fw_total += 1
        elif sc.startswith('DISTRACTOR_'):
            env_total += 1

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
            ballistic_s = max(y[c] for c in BALLISTIC_EXP_CLASSES)
            non_target_s = max(y[c] for c in NON_TARGET_CLASSES)

            adj = raw

            # Coherence safeguard
            if enable_coherence_guard and (ballistic_s < 0.015 and non_target_s >= 0.12):
                adj *= 0.20
            # Thunder
            elif thun_s > 0.25 and thun_s >= gun_s * 1.5:
                adj *= 0.30
            # Fireworks (two-tier)
            elif (fw_s >= 0.45 and fw_s >= gun_s * 1.8 and gun_s < fw_gun_max):
                adj *= 0.30
            elif (fw_s >= 0.30 and fw_s >= gun_s * 1.5 and gun_s < 0.12):
                adj *= 0.35
            # Wind buffeting
            elif (wind_s >= 0.25 and wind_s >= gun_s * 1.5):
                adj *= 0.25
            # Mechanical impact
            elif (impact_s >= 0.30 and impact_s >= gun_s * 1.5 and gun_s < 0.20):
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

            qual_imm = (s >= th_high and has_sharp) or (is_short and s >= 0.75)

            if not in_cand:
                if qual_imm:
                    events.append(i)
                    cooldown_until = t + 2.0
                elif s >= 0.75:
                    in_cand = True
                    cand_win = (i, t, s)
            else:
                if qual_imm:
                    events.append(i)
                    in_cand = False
                    cooldown_until = t + 2.0
                elif s >= 0.75:
                    events.append(cand_win[0])
                    in_cand = False
                    cooldown_until = t + 2.0
                else:
                    if enable_single_impulse_dispatch and cand_win[2] >= 0.82 and crest >= 15.0 and dur <= 5.0:
                        events.append(cand_win[0])
                        cooldown_until = cand_win[1] + 2.0
                    in_cand = False

        is_det = len(events) > 0
        if gt == 1 and is_det:
            pos_det += 1
        elif sc == 'DISTRACTOR_FIREWORKS' and is_det:
            fw_fps += 1
        elif sc.startswith('DISTRACTOR_') and is_det:
            env_fps += 1
        elif sc == 'LONG_AMBIENT_STREAM':
            cont_events += len(events)
            if rid == 'p40_cont_03_bruxelles':
                bxl_events = len(events)

    return {
        "pos_recall": pos_det / pos_total,
        "pos_count": pos_det,
        "fw_fps": fw_fps,
        "env_fps": env_fps,
        "cont_events": cont_events,
        "bxl_events": bxl_events
    }

print("Testing Coherence Guard and Dispatch combinations on DEV set...")
for cg in [False, True]:
    for disp in [False, True]:
        for fmax in [0.10, 0.25]:
            r = run_simulation(fw_gun_max=fmax, enable_coherence_guard=cg, enable_single_impulse_dispatch=disp)
            print(f"CG={str(cg):5s} | Disp={str(disp):5s} | FwMax={fmax:.2f} -> Pos: {r['pos_count']}/72 ({r['pos_recall']*100:.1f}%), FW_FP: {r['fw_fps']}/59, Env_FP: {r['env_fps']}/72, Cont_Evs: {r['cont_events']} (Bruxelles: {r['bxl_events']})")

