"""
Deterministic Source-Cluster Partition for Phase 44 V2 Evaluation.
Partitions the 368 benchmark recordings into:
- Development Group (~60%)
- Locked Holdout Group (~40%)
Disjoint strictly by uploader_or_recordist to avoid source contamination.
"""

import pandas as pd
import numpy as np

inv_path = "experiments/phase41/phase41_recording_inventory.csv"
df = pd.read_csv(inv_path)

# Cluster strictly by uploader_or_recordist
df['cluster_key'] = df['uploader_or_recordist'].astype(str)

rng = np.random.RandomState(44)

# We want stratified partitioning across sub_category
dev_clusters = set()
holdout_clusters = set()

subcats = df['sub_category'].unique()

for sc in sorted(subcats):
    sc_df = df[df['sub_category'] == sc]
    # Unique uploaders in this subcategory that haven't been assigned yet
    unassigned_clusters = sorted([c for c in sc_df['cluster_key'].unique() if c not in dev_clusters and c not in holdout_clusters])
    rng.shuffle(unassigned_clusters)
    
    # Check current dev / holdout ratio in this subcategory
    assigned_sc = sc_df[sc_df['cluster_key'].isin(dev_clusters.union(holdout_clusters))]
    n_dev_current = len(assigned_sc[assigned_sc['cluster_key'].isin(dev_clusters)])
    n_holdout_current = len(assigned_sc[assigned_sc['cluster_key'].isin(holdout_clusters)])
    
    for c in unassigned_clusters:
        # Assign to balance ~60% dev, 40% holdout
        rec_count = len(sc_df[sc_df['cluster_key'] == c])
        total_assigned = n_dev_current + n_holdout_current
        current_dev_ratio = n_dev_current / total_assigned if total_assigned > 0 else 0.5
        
        if current_dev_ratio <= 0.60:
            dev_clusters.add(c)
            n_dev_current += rec_count
        else:
            holdout_clusters.add(c)
            n_holdout_current += rec_count

# Assign partition
df['v2_partition'] = df['cluster_key'].apply(lambda c: 'development' if c in dev_clusters else 'locked_holdout')

print("=== PARTITION BREAKDOWN ===")
ct = pd.crosstab(df['sub_category'], df['v2_partition'], margins=True)
print(ct)

# Check source overlap
dev_uploaders = set(df[df['v2_partition'] == 'development']['uploader_or_recordist'])
holdout_uploaders = set(df[df['v2_partition'] == 'locked_holdout']['uploader_or_recordist'])
overlap = dev_uploaders.intersection(holdout_uploaders)
print(f"\nUploader overlap between dev and holdout: {len(overlap)}")
assert len(overlap) == 0, f"Overlapping uploaders: {overlap}"

# Check total recordings
print("\nTotal recordings by partition:")
print(df['v2_partition'].value_counts())
print("\nTotal duration (hours) by partition:")
print((df.groupby('v2_partition')['duration_seconds'].sum() / 3600.0).round(3))

# Save partition mapping
df[['recording_id', 'v2_partition', 'sub_category', 'cluster_key', 'duration_seconds']].to_csv("scratch/v2_partitions.csv", index=False)
print("Saved partition map to scratch/v2_partitions.csv")
