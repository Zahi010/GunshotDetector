import json
import pandas as pd

eval_df = pd.read_csv('e:/FSD50K.dev_audio/FSD50K.ground_truth/eval.csv')
gun_df = eval_df[eval_df['labels'].str.contains('Gunshot_and_gunfire', na=False)]
with open('e:/FSD50K.dev_audio/FSD50K.metadata/eval_clips_info_FSD50K.json') as f:
    info = json.load(f)

found = 0
for fname in gun_df['fname']:
    clip = info.get(str(fname), {})
    text = (clip.get("title", "") + " " + clip.get("description", "") + " " + " ".join(clip.get("tags", []))).lower()
    if any(k in text for k in ['pocket', 'muffle', 'conceal', 'bag', 'cloth', 'fabric', 'obstruct', 'indoor']):
        print(f"Match: {fname}: {clip.get('title')} | {clip.get('description')}")
        found += 1
print(f"Total matching: {found}")

