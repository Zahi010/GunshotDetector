import pandas as pd
import json
import pathlib

meta_path = pathlib.Path('E:/FSD50K.dev_audio/FSD50K.metadata/dev_clips_info_FSD50K.json')
with open(meta_path) as f:
    dev_info = json.load(f)

dev_df = pd.read_csv('E:/FSD50K.dev_audio/FSD50K.ground_truth/dev.csv')
gun_df = dev_df[dev_df['labels'].str.contains('Gunshot_and_gunfire', na=False)].copy()

print(f"Total Gunshot_and_gunfire clips in dev.csv: {len(gun_df)}")

audio_dir = pathlib.Path('E:/FSD50K.dev_audio/FSD50K.dev_audio')
existing_guns = []
for idx, row in gun_df.iterrows():
    fn = f"{row['fname']}.wav"
    p = audio_dir / fn
    if p.exists():
        info = dev_info.get(str(row['fname']), {})
        existing_guns.append({
            'fname': row['fname'],
            'path': str(p),
            'size': p.stat().st_size,
            'labels': row['labels'],
            'uploader': info.get('uploader', 'unknown'),
            'license': info.get('license', 'unknown'),
            'title': info.get('title', '')
        })

print(f"Existing audio files on disk: {len(existing_guns)}")
eg_df = pd.DataFrame(existing_guns)
print(f"Unique uploaders: {eg_df['uploader'].nunique()}")
print("License breakdown:")
print(eg_df['license'].value_counts())
print("\nTop uploaders:")
print(eg_df['uploader'].value_counts().head(10))

