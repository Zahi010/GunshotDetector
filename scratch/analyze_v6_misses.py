import pandas as pd
import numpy as np
import pathlib

df = pd.read_csv("experiments/detector_improvement_v6/recording_level_predictions.csv")

print("=== RECORDING COUNTS BY PARTITION ===")
print(df.groupby(["partition", "ground_truth_gunshot"])[["v5_adaptive_detected", "v6_discriminated_detected"]].agg(["count", "sum"]))

pos = df[df["ground_truth_gunshot"] == 1]
missed = pos[pos["v6_discriminated_detected"] == 0]

print("\n=== MISSED POSITIVES SUMMARY ===")
print(missed.groupby("partition")["recording_id"].count())

print("\n=== MISSED POSITIVES IN PHASE 12 (N={}) ===".format(len(missed[missed["partition"] == "phase12_historical_holdout"])))
p12_miss = missed[missed["partition"] == "phase12_historical_holdout"]
for idx, r in p12_miss.iterrows():
    print(f"  {r['recording_id']:45s} | sub: {str(r['sub_category']):15s} | cond: {str(r['condition_category']):20s} | v5_det: {r['v5_adaptive_detected']} | v5_sc: {r['v5_adaptive_peak_score']:.4f} | v6_sc: {r['v6_discriminated_peak_score']:.4f} | mode: {r['v6_dominant_mode']}")

print("\n=== MISSED POSITIVES IN PHASE 15 (N={}) ===".format(len(missed[missed["partition"] == "phase15_historical_holdout"])))
p15_miss = missed[missed["partition"] == "phase15_historical_holdout"]
for idx, r in p15_miss.iterrows():
    print(f"  {r['recording_id']:45s} | sub: {str(r['sub_category']):25s} | v5_det: {r['v5_adaptive_detected']} | v5_sc: {r['v5_adaptive_peak_score']:.4f} | v6_sc: {r['v6_discriminated_peak_score']:.4f} | mode: {r['v6_dominant_mode']}")

print("\n=== MISSED POSITIVES IN PHASE 19 (N={}) ===".format(len(missed[missed["partition"] == "phase19_independent_positive"])))
p19_miss = missed[missed["partition"] == "phase19_independent_positive"]
for idx, r in p19_miss.iterrows():
    print(f"  {r['recording_id']:45s} | sub: {str(r['sub_category']):25s} | v5_det: {r['v5_adaptive_detected']} | v5_sc: {r['v5_adaptive_peak_score']:.4f} | v6_sc: {r['v6_discriminated_peak_score']:.4f} | mode: {r['v6_dominant_mode']}")

print("\n=== REMAINING FALSE ALARMS IN V6 ===")
neg = df[df["ground_truth_gunshot"] == 0]
false_alarms = neg[neg["v6_discriminated_detected"] == 1]
print(false_alarms.groupby("partition")["recording_id"].count())
for idx, r in false_alarms.iterrows():
    print(f"  {r['recording_id']:45s} | part: {r['partition']:28s} | sub: {str(r['sub_category']):20s} | v6_sc: {r['v6_discriminated_peak_score']:.4f}")

