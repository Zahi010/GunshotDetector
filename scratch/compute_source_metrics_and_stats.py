import pandas as pd
import numpy as np

print("=" * 70)
print("PHASE 54: SOURCE-LEVEL METRICS & STATISTICAL ANALYSIS")
print("=" * 70)

pred_csv = "e:/gunshot/gunshot/experiments/phase54_final_validation/recording_level_predictions.csv"
df = pd.read_csv(pred_csv)
print(f"Loaded {len(df)} predictions from {pred_csv}")

# 1. Source-Level Metrics for Positives
pos_df = df[df['ground_truth_label'] == 1]
source_stats = []

for uploader, g in pos_df.groupby('uploader'):
    n_files = len(g)
    detected = g['prediction'].sum()
    rec_pct = (detected / n_files) * 100.0
    mean_score = g['peak_score'].mean()
    source_stats.append({
        'uploader_source': uploader,
        'total_recordings': n_files,
        'detected_gunshots': detected,
        'recall_pct': round(rec_pct, 2),
        'mean_peak_score': round(mean_score, 4),
        'acoustic_conditions': ", ".join(sorted(g['sub_category'].unique()))
    })

source_df = pd.DataFrame(source_stats).sort_values(by='total_recordings', ascending=False)
source_csv = "e:/gunshot/gunshot/experiments/phase54_final_validation/source_level_metrics.csv"
source_df.to_csv(source_csv, index=False)
print(f"Source-level metrics saved to {source_csv} ({len(source_df)} unique sources).")

# Print top 15 sources
print("\nTop 15 Sources by Volume:")
print(source_df[['uploader_source', 'total_recordings', 'detected_gunshots', 'recall_pct', 'mean_peak_score']].head(15).to_string(index=False))

# 2. Statistical Analysis & Confidence Intervals (Wilson Score)
def wilson_ci(k, n, confidence=0.95):
    if n == 0:
        return 0.0, 0.0
    z = 1.959964 # for 95%
    p = k / n
    denom = 1 + z**2 / n
    center = (p + z**2 / (2 * n)) / denom
    margin = (z * np.sqrt((p * (1 - p) + z**2 / (4 * n)) / n)) / denom
    lower = max(0.0, center - margin)
    upper = min(1.0, center + margin)
    return round(lower * 100.0, 2), round(upper * 100.0, 2)

stat_records = []

# Positives
pos_total = len(pos_df)
pos_det = pos_df['prediction'].sum()
pos_rec = (pos_det / pos_total) * 100.0
ci_l, ci_u = wilson_ci(pos_det, pos_total)
stat_records.append({
    'dataset_partition': 'Phase 54 Genuinely New Corpus (Positives)',
    'metric_name': 'Overall Positive Recall',
    'sample_size': pos_total,
    'success_count': pos_det,
    'point_estimate_pct': round(pos_rec, 2),
    'ci95_lower_pct': ci_l,
    'ci95_upper_pct': ci_u,
    'qualification_target_pct': 80.0,
    'target_status': 'MISSED' if pos_rec < 80.0 else 'MET'
})

# Conditions
for cond, g in pos_df.groupby('sub_category'):
    n = len(g)
    k = g['prediction'].sum()
    r = (k / n) * 100.0
    l, u = wilson_ci(k, n)
    stat_records.append({
        'dataset_partition': f'Condition: {cond}',
        'metric_name': 'Recall by Condition',
        'sample_size': n,
        'success_count': k,
        'point_estimate_pct': round(r, 2),
        'ci95_lower_pct': l,
        'ci95_upper_pct': u,
        'qualification_target_pct': 80.0,
        'target_status': 'MET' if r >= 80.0 else 'MISSED'
    })

# Negatives
neg_df = df[df['ground_truth_label'] == 0]
neg_total = len(neg_df)
neg_fa = neg_df['prediction'].sum()
neg_fpr = (neg_fa / neg_total) * 100.0
l, u = wilson_ci(neg_fa, neg_total)
stat_records.append({
    'dataset_partition': 'Phase 54 Genuinely New Corpus (All Negatives)',
    'metric_name': 'Overall False Positive Rate',
    'sample_size': neg_total,
    'success_count': neg_fa,
    'point_estimate_pct': round(neg_fpr, 2),
    'ci95_lower_pct': l,
    'ci95_upper_pct': u,
    'qualification_target_pct': 5.0,
    'target_status': 'REGRESSION' if neg_fpr > 5.0 else 'MET'
})

# Negatives by Sub-Category
for cat, g in neg_df.groupby('sub_category'):
    n = len(g)
    k = g['prediction'].sum()
    fpr = (k / n) * 100.0
    l, u = wilson_ci(k, n)
    stat_records.append({
        'dataset_partition': f'Negative: {cat}',
        'metric_name': 'False Positive Rate',
        'sample_size': n,
        'success_count': k,
        'point_estimate_pct': round(fpr, 2),
        'ci95_lower_pct': l,
        'ci95_upper_pct': u,
        'qualification_target_pct': 0.0 if 'hard' in cat or 'balloon' in cat or 'fireworks' in cat else 5.0,
        'target_status': 'REGRESSION' if k > 0 else 'MET'
    })

stat_df = pd.DataFrame(stat_records)
stat_csv = "e:/gunshot/gunshot/experiments/phase54_final_validation/statistical_metrics.csv"
stat_df.to_csv(stat_csv, index=False)
print(f"\nStatistical metrics saved to {stat_csv}")

print("\nKey Statistical Summary:")
print(stat_df[['dataset_partition', 'sample_size', 'point_estimate_pct', 'ci95_lower_pct', 'ci95_upper_pct', 'target_status']].to_string(index=False))

