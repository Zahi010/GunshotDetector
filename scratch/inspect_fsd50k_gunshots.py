import pandas as pd
import json

eval_df = pd.read_csv('e:/FSD50K.dev_audio/FSD50K.ground_truth/eval.csv')
gun_df = eval_df[eval_df['labels'].str.contains('Gunshot_and_gunfire', na=False)]

with open('e:/FSD50K.dev_audio/FSD50K.metadata/eval_clips_info_FSD50K.json') as f:
    info = json.load(f)

print(f'Total gunshot clips: {len(gun_df)}')
uploaders = {}
conditions = {'clean': 0, 'reverberant': 0, 'burst': 0, 'distant': 0, 'clipped': 0, 'other': 0}

for idx, fname in enumerate(gun_df['fname']):
    str_fn = str(fname)
    clip = info.get(str_fn, {})
    up = clip.get('uploader', 'unknown')
    uploaders[up] = uploaders.get(up, 0) + 1
    
    title = clip.get('title', '').lower()
    desc = clip.get('description', '').lower()
    tags = [t.lower() for t in clip.get('tags', [])]
    text = f"{title} {desc} {' '.join(tags)}"
    
    if any(k in text for k in ['burst', 'rapid', 'full auto', 'machine', 'automatic']):
        conditions['burst'] += 1
    elif any(k in text for k in ['reverb', 'echo', 'hall', 'tunnel', 'canyon', 'forest']):
        conditions['reverberant'] += 1
    elif any(k in text for k in ['distant', 'far', 'distance']):
        conditions['distant'] += 1
    elif any(k in text for k in ['distort', 'clip', 'loud', 'overload']):
        conditions['clipped'] += 1
    elif any(k in text for k in ['single', 'clean', 'outdoor', 'field', 'shot']):
        conditions['clean'] += 1
    else:
        conditions['other'] += 1

print(f'Unique uploaders/sources: {len(uploaders)}')
print('Conditions breakdown:', conditions)
print('\nTop uploaders:', sorted(uploaders.items(), key=lambda x: x[1], reverse=True)[:10])

