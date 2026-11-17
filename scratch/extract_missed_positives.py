import pandas as pd

df = pd.read_csv('e:/gunshot/gunshot/experiments/phase52_validation/v8_v9_discrete_eval.csv')
pos = df[df['label'] == 1]
print(f"Total gunshots: {len(pos)}")
print(f"V9 detected: {pos['v9_detected'].sum()}")
missed = pos[~pos['v9_detected']]
print(f"V9 missed: {len(missed)}")
print(missed[['filename', 'sub_category', 'condition_category', 'v8_detected', 'v9_detected', 'v9_peak_score']].to_string())
missed.to_csv('e:/gunshot/gunshot/scratch/v9_missed_positives_raw.csv', index=False)

