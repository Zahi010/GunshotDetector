import pandas as pd
import json
import pathlib

meta_path = pathlib.Path('E:/FSD50K.dev_audio/FSD50K.metadata/dev_clips_info_FSD50K.json')
with open(meta_path) as f:
    dev_info = json.load(f)

dev_df = pd.read_csv('E:/FSD50K.dev_audio/FSD50K.ground_truth/dev.csv')

# Exclude any clip that has Gunshot_and_gunfire
dev_neg = dev_df[~dev_df['labels'].str.contains('Gunshot_and_gunfire', na=False)].copy()

categories = {
    'Fireworks': 'Fireworks',
    'Explosion': 'Explosion',
    'Thunder': 'Thunder',
    'Bark': 'Bark',
    'Aircraft': 'Aircraft',
    'Slam_Door': 'Slam|Door',
    'Tools_Impact': 'Power_tool|Drill|Hammer|Crushing|Chink_and_clink'
}

for cat_name, pattern in categories.items():
    matched = dev_neg[dev_neg['labels'].str.contains(pattern, na=False)]
    print(f"Category '{cat_name}': {len(matched)} clips available in FSD50K")

