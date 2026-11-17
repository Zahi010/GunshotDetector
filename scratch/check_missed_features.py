"""
Deep forensic comparison of the 18 missed single-round gunshots (raw_score in [0.75, 0.88))
vs the fireworks and continuous false positives.
"""
import pandas as pd
import numpy as np
import pathlib

inv = pd.read_csv("experiments/phase41/phase41_recording_inventory.csv")
v1_df = pd.read_csv("experiments/detector_improvement_v1/recording_level_predictions.csv")
merged = pd.merge(v1_df, inv, on="recording_id")

p38_cache = pathlib.Path("experiments/phase38/feature_cache")
p39_cache = pathlib.Path("experiments/phase39/feature_cache")
p40_cache = pathlib.Path("experiments/phase40/feature_cache")

def get_cache(rid):
    for c in [p38_cache, p39_cache, p40_cache]:
        f = c / f"{rid}.npz"
        if f.exists():
            return f
    return None

# Find the 18 missed gunshots with raw in [0.75, 0.88)
pos_missed = merged[(merged["ground_truth_gunshot"] == 1) & (merged["v1_detected"] == 0)]
missed_records = []
for _, r in pos_missed.iterrows():
    cf = get_cache(r['recording_id'])
    if cf:
        npz = np.load(cf)
        raw_s = npz['raw_scores']
        ys = npz['yamnet_scores']
        mx = np.max(raw_s) if len(raw_s) > 0 else 0
        if mx >= 0.75:
            pk_win = np.argmax(raw_s)
            gun_yam = max(ys[pk_win, [421, 422, 424, 425]])
            fw_yam = max(ys[pk_win, [426, 427]])
            thun_yam = max(ys[pk_win, [280, 281]])
            missed_records.append({
                "recording_id": r['recording_id'],
                "sub_category": r['sub_category'],
                "duration_sec": r['duration_sec'],
                "crest_factor_db": r['crest_factor_db'],
                "max_raw": mx,
                "gun_yam": gun_yam,
                "fw_yam": fw_yam,
                "thun_yam": thun_yam,
                "n_windows": len(raw_s)
            })

df_missed = pd.DataFrame(missed_records)
print(f"=== 18 MISSED HIGH-RAW GUNSHOTS ===")
print(df_missed[['recording_id', 'max_raw', 'gun_yam', 'fw_yam', 'crest_factor_db', 'n_windows', 'duration_sec']])
print("\nSummary of missed gunshots:")
print(f"Mean max_raw: {df_missed['max_raw'].mean():.3f}")
print(f"Mean gun_yam: {df_missed['gun_yam'].mean():.3f}")
print(f"Mean fw_yam:  {df_missed['fw_yam'].mean():.3f}")
print(f"Min gun_yam:  {df_missed['gun_yam'].min():.3f}")
print(f"Max fw_yam:   {df_missed['fw_yam'].max():.3f}")

