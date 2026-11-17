"""
Statistical investigation of condition classification features
"""
import sys, os
sys.path.insert(0, "E:/gunshot/gunshot")
os.chdir("E:/gunshot/gunshot")

import pandas as pd
import numpy as np

rca = pd.read_csv("experiments/detector_improvement_v4/recording_condition_analysis.csv")

print("Recording count by condition category:")
print(rca['condition_category'].value_counts())

metrics = [
    'channel_rolloff_ratio',
    'high_band_ratio_ge_2500hz',
    'mid_band_ratio_500_2500hz',
    'low_band_ratio_lt_500hz',
    'mid_to_low_energy_ratio',
    'spectral_centroid_hz',
    'spectral_flatness',
    'crest_factor_db'
]

print("\n" + "="*80)
print("MEAN AND STD ACROSS CONDITION CATEGORIES")
print("="*80)

grouped = rca.groupby('condition_category')[metrics].agg(['mean', 'std'])
for col in metrics:
    print(f"\n--- {col} ---")
    s = rca.groupby('condition_category')[col].agg(['count', 'mean', 'std', 'min', 'max'])
    print(s.to_string())

# Detailed look at Pocket vs Clear vs Ambient
print("\n" + "="*80)
print("POCKET VS CLEAR VS AMBIENT PERCENTILES FOR CHANNEL ROLLOFF")
print("="*80)
for cat in ['pocket_obstructed', 'clear_open_mic', 'clipped_overload', 'distant_urban_sensor', 'outdoor_ambient_mimic', 'indoor_ambient_mimic']:
    subset = rca[rca['condition_category'] == cat]['channel_rolloff_ratio']
    if len(subset) > 0:
        print(f"{cat:25s}: N={len(subset):2d}, mean={subset.mean():.4f}, median={subset.median():.4f}, P10={subset.quantile(0.10):.4f}, P90={subset.quantile(0.90):.4f}, Min={subset.min():.4f}, Max={subset.max():.4f}")

print("\n" + "="*80)
print("MID-TO-LOW ENERGY RATIO PERCENTILES")
print("="*80)
for cat in ['pocket_obstructed', 'clear_open_mic', 'clipped_overload', 'distant_urban_sensor', 'outdoor_ambient_mimic', 'indoor_ambient_mimic', 'pyrotechnic_mimic']:
    subset = rca[rca['condition_category'] == cat]['mid_to_low_energy_ratio']
    if len(subset) > 0:
        print(f"{cat:25s}: N={len(subset):2d}, mean={subset.mean():.4f}, median={subset.median():.4f}, P10={subset.quantile(0.10):.4f}, P90={subset.quantile(0.90):.4f}, Min={subset.min():.4f}, Max={subset.max():.4f}")

