import pandas as pd

manifest = pd.read_csv('e:/gunshot/gunshot/experiments/phase51_validation/phase51_evaluation_manifest.csv')
missed = pd.read_csv('e:/gunshot/gunshot/scratch/v9_missed_positives_raw.csv')

merged = pd.merge(missed, manifest, on='filename', suffixes=('', '_manifest'))
print(merged[['filename', 'sub_category', 'condition_category', 'filepath', 'source_provenance']].to_string())
merged.to_csv('e:/gunshot/gunshot/scratch/missed_with_paths.csv', index=False)
