"""
Comprehensive evaluation of Detector Improvement V2 on the DEVELOPMENT SET (218 recordings).
Prints complete confusion matrix, subcategory breakdown, and event metrics.
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
GUN_CLASSES = [421, 422, 424, 425]
FW_CLASSES = [426, 427]
THUN_CLASSES = [280, 281]
DOG_CLASSES = [69, 70, 75, 117]
CRACKLE_CLASSES = [292, 293]
SIREN_CLASSES = [317, 318, 319, 390, 391]
WIND_CLASSES = [277, 279]
IMPACT_CLASSES = [58, 352, 353, 413, 414]

NON_TARGET_CLASSES = [
    0,  # Speech
    67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117,
    300, 301, 302, 303, 304, 305, 306, 307, 308, 309, 310, 311, 312, 313, 314, 315, 316, 317, 318, 319, 320, 321, 322, 323, 324, 325, 326, 327, 328, 329, 330,
    502, 503, 504
]

class CalibratedAcousticSuppressionV2:
    def __init__(self):
        pass

    def apply_suppression(self, raw_score: float, ys: np.ndarray, is_in_confirmed_event: bool = False):
        if ys is None or len(ys) == 0 or is_in_confirmed_event:
            return {"score": float(raw_score), "active": False, "category": None, "strength": 1.0}

        gun_s = max(ys[c] for c in GUN_CLASSES)
        fw_s = max(ys[c] for c in FW_CLASSES)
        thun_s = max(ys[c] for c in THUN_CLASSES)
        dog_s = max(ys[c] for c in DOG_CLASSES)
        crackle_s = max(ys[c] for c in CRACKLE_CLASSES)
        siren_s = max(ys[c] for c in SIREN_CLASSES)
        wind_s = max(ys[c] for c in WIND_CLASSES)
        impact_s = max(ys[c] for c in IMPACT_CLASSES)
        ballistic_s = max(ys[c] for c in BALLISTIC_EXP_CLASSES)
        non_target_s = max(ys[c] for c in NON_TARGET_CLASSES)

        adj = float(raw_score)
        cat = None
        strength = 1.0

        # 1. Non-ballistic acoustic coherence safeguard (rejects tree ensemble artifacts on non-ballistic audio)
        if ballistic_s < 0.015 and non_target_s >= 0.12:
            strength = 0.20
            adj *= strength
            cat = "non_ballistic_coherence_rejection"

        # 2. Thunder
        elif thun_s > 0.25 and thun_s >= gun_s * 1.5:
            strength = 0.30
            adj *= strength
            cat = "thunder"

        # 3. Fireworks (two-tier refined)
        elif fw_s >= 0.45 and fw_s >= gun_s * 1.8 and gun_s < 0.25:
            strength = 0.30
            adj *= strength
            cat = "fireworks_dominant"
        elif fw_s >= 0.30 and fw_s >= gun_s * 1.5 and gun_s < 0.12:
            strength = 0.35
            adj *= strength
            cat = "fireworks_standard"

        # 4. Wind buffeting / infrasonic rumble
        elif wind_s >= 0.25 and wind_s >= gun_s * 1.5:
            strength = 0.25
            adj *= strength
            cat = "wind_buffeting"

        # 5. Mechanical impacts / heavy tools
        elif impact_s >= 0.30 and impact_s >= gun_s * 1.5 and gun_s < 0.20:
            strength = 0.35
            adj *= strength
            cat = "mechanical_impact"

        # 6. Canine vocalization
        elif dog_s > 0.30 and dog_s >= gun_s * 1.5:
            strength = 0.35
            adj *= strength
            cat = "canine_bark"

        # 7. Fire crackle
        elif crackle_s > 0.25 and crackle_s >= gun_s * 1.5:
            strength = 0.35
            adj *= strength
            cat = "fire_crackle"

        # 8. Emergency transit siren
        elif siren_s > 0.35 and siren_s >= gun_s * 1.5:
            strength = 0.30
            adj *= strength
            cat = "siren"

        return {
            "score": float(round(adj, 4)),
            "active": cat is not None,
            "category": cat,
            "strength": float(strength)
        }

supp_v2 = CalibratedAcousticSuppressionV2()

results = []
for _, r in dev_df.iterrows():
    rid = r['recording_id']
    cf = get_cache(rid)
    if cf is None:
        continue
    npz = np.load(cf)
    raw_s = npz['raw_scores']
    ys = npz['yamnet_scores']
    crest = r['crest_factor_db']
    dur = r['duration_sec']
    n_win = len(raw_s)

    # Process windows
    win_adj = []
    win_supp = []
    for i in range(n_win):
        res = supp_v2.apply_suppression(raw_s[i], ys[i])
        win_adj.append(res['score'])
        win_supp.append(res['active'])

    # FSM
    events = []
    in_cand = False
    cand_win = None
    cooldown_until = -1.0
    has_sharp = (crest >= 12.0)
    is_short = (dur <= 1.05 and n_win == 1 and crest >= 8.8)

    for i, s in enumerate(win_adj):
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
            if qual_imm:
                events.append({"win": i, "t": t, "score": s, "dispatch": "immediate"})
                in_cand = False
                cooldown_until = t + 2.0
            elif s >= 0.75:
                events.append({"win": cand_win[0], "t": cand_win[1], "score": cand_win[2], "dispatch": "multi_window"})
                in_cand = False
                cooldown_until = t + 2.0
            else:
                # Impulse decay exception for authentic sharp single rounds
                if cand_win[2] >= 0.82 and crest >= 14.0 and dur <= 5.0 and not win_supp[cand_win[0]]:
                    events.append({"win": cand_win[0], "t": cand_win[1], "score": cand_win[2], "dispatch": "single_round_impulse"})
                    cooldown_until = cand_win[1] + 2.0
                in_cand = False

    results.append({
        "recording_id": rid,
        "sub_category": r['sub_category'],
        "ground_truth": r['ground_truth_gunshot'],
        "duration_sec": dur,
        "crest_factor_db": crest,
        "v1_detected": r['v1_detected'],
        "v1_count": r['v1_event_count'],
        "v2_detected": int(len(events) > 0),
        "v2_count": len(events),
        "v2_peak_score": round(float(np.max(win_adj)), 4) if len(win_adj) > 0 else 0.0,
        "v2_first_dispatch": events[0]['dispatch'] if len(events) > 0 else "none"
    })

dev_res_df = pd.DataFrame(results)
print("=== V2 PERFORMANCE ON DEVELOPMENT SET (N=218) ===")
summary_rows = []
for sc in sorted(dev_res_df['sub_category'].unique()):
    sub = dev_res_df[dev_res_df['sub_category'] == sc]
    gt = sub['ground_truth'].iloc[0]
    n = len(sub)
    v1_det = sub['v1_detected'].sum()
    v1_cnt = sub['v1_count'].sum()
    v2_det = sub['v2_detected'].sum()
    v2_cnt = sub['v2_count'].sum()
    print(f"{sc:26s} | N={n:2d} GT={gt} | V1: {v1_det:2d} recs ({v1_cnt:2d} evs) -> V2: {v2_det:2d} recs ({v2_cnt:2d} evs)")

print("\n--- MACRO METRICS ON DEV SET ---")
pos = dev_res_df[dev_res_df['ground_truth'] == 1]
fw = dev_res_df[dev_res_df['sub_category'] == 'DISTRACTOR_FIREWORKS']
env = dev_res_df[dev_res_df['sub_category'].str.startswith('DISTRACTOR_') & (dev_res_df['sub_category'] != 'DISTRACTOR_FIREWORKS')]
cont = dev_res_df[dev_res_df['sub_category'] == 'LONG_AMBIENT_STREAM']

print(f"Positive Gunshot Recall:  V1 = {pos['v1_detected'].sum():2d}/{len(pos)} ({pos['v1_detected'].mean()*100:.1f}%) -> V2 = {pos['v2_detected'].sum():2d}/{len(pos)} ({pos['v2_detected'].mean()*100:.1f}%)  [+{pos['v2_detected'].sum()-pos['v1_detected'].sum()}]")
print(f"Fireworks False Alarms:   V1 = {fw['v1_detected'].sum():2d}/{len(fw)} ({fw['v1_detected'].mean()*100:.1f}%) -> V2 = {fw['v2_detected'].sum():2d}/{len(fw)} ({fw['v2_detected'].mean()*100:.1f}%)  [-{fw['v1_detected'].sum()-fw['v2_detected'].sum()}]")
print(f"Environmental FAs:        V1 = {env['v1_detected'].sum():2d}/{len(env)} ({env['v1_detected'].mean()*100:.1f}%) -> V2 = {env['v2_detected'].sum():2d}/{len(env)} ({env['v2_detected'].mean()*100:.1f}%)  [-{env['v1_detected'].sum()-env['v2_detected'].sum()}]")
print(f"Continuous Alerts (evs):  V1 = {cont['v1_count'].sum():2d} events       -> V2 = {cont['v2_count'].sum():2d} events       [-{cont['v1_count'].sum()-cont['v2_count'].sum()}]")

