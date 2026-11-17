import pandas as pd
import json
import pathlib
import shutil
import hashlib
import soundfile as sf

meta_path = pathlib.Path('E:/FSD50K.dev_audio/FSD50K.metadata/dev_clips_info_FSD50K.json')
with open(meta_path) as f:
    dev_info = json.load(f)

dev_df = pd.read_csv('E:/FSD50K.dev_audio/FSD50K.ground_truth/dev.csv')
gun_df = dev_df[dev_df['labels'].str.contains('Gunshot_and_gunfire', na=False)].copy()

audio_dir = pathlib.Path('E:/FSD50K.dev_audio/FSD50K.dev_audio')
dest_dir = pathlib.Path('E:/gunshot/gunshot/experiments/phase38/dataset/positive')
dest_dir.mkdir(parents=True, exist_ok=True)

# Select 120 clips across distinct uploaders
# Group by uploader to ensure high session diversity (at least 30+ distinct uploaders)
uploader_groups = {}
for idx, row in gun_df.iterrows():
    fn = f"{row['fname']}.wav"
    p = audio_dir / fn
    if p.exists():
        info = dev_info.get(str(row['fname']), {})
        up = info.get('uploader', 'unknown')
        if up not in uploader_groups:
            uploader_groups[up] = []
        uploader_groups[up].append({
            'fname': row['fname'],
            'path': p,
            'info': info,
            'labels': row['labels']
        })

print(f"Total uploaders with gunshot audio: {len(uploader_groups)}")

selected_clips = []
# Round-robin selection across uploaders to maximize diversity
max_per_uploader = 5
while len(selected_clips) < 120:
    added_in_round = 0
    for up, clips in uploader_groups.items():
        if len(selected_clips) >= 120:
            break
        # Take up to max_per_uploader
        taken = [c for c in selected_clips if c['uploader'] == up]
        if len(taken) < max_per_uploader and len(clips) > len(taken):
            c_candidate = clips[len(taken)]
            selected_clips.append({
                'recording_id': f"fsd50k_gun_{c_candidate['fname']}",
                'original_fname': f"{c_candidate['fname']}.wav",
                'src_path': c_candidate['path'],
                'uploader': up,
                'license': c_candidate['info'].get('license', 'CC BY 4.0'),
                'title': c_candidate['info'].get('title', ''),
                'labels': c_candidate['labels'],
                'tags': ",".join(c_candidate['info'].get('tags', []))
            })
            added_in_round += 1
    if added_in_round == 0:
        break

print(f"Selected {len(selected_clips)} positive gunshot clips across {len(set(c['uploader'] for c in selected_clips))} distinct uploaders.")

# Copy and catalog
positive_catalog = []
for c in selected_clips:
    dest_path = dest_dir / c['original_fname']
    if not dest_path.exists():
        shutil.copy2(c['src_path'], dest_path)
    
    data = dest_path.read_bytes()
    sha = hashlib.sha256(data).hexdigest()
    info = sf.info(str(dest_path))
    
    # Check if title/tags indicate burst or automatic fire
    title_lower = (c['title'] + " " + c['tags']).lower()
    is_burst = any(w in title_lower for w in ['burst', 'automatic', 'machine gun', 'mg42', 'ak47', 'm4', 'm16', 'rapid', 'triple', 'double'])
    
    positive_catalog.append({
        'recording_id': c['recording_id'],
        'filename': c['original_fname'],
        'partition': 'PARTITION_PROSPECTIVE_POSITIVE',
        'source_dataset': 'FSD50K_dev',
        'uploader_session': c['uploader'],
        'license': c['license'],
        'title': c['title'],
        'tags': c['tags'],
        'duration_seconds': round(info.duration, 4),
        'sample_rate_hz': info.samplerate,
        'channels': info.channels,
        'sha256': sha,
        'annotated_event_type': 'BURST_FIRE' if is_burst else 'SINGLE_ROUND',
        'annotated_rounds_count': 3 if is_burst else 1,
        'peak_time_seconds': round(info.duration / 2.0, 3) # default center peak
    })

cat_df = pd.DataFrame(positive_catalog)
out_csv = pathlib.Path('E:/gunshot/gunshot/experiments/phase38/dataset/phase38_positive_catalog.csv')
cat_df.to_csv(out_csv, index=False)
print(f"Saved positive catalog to {out_csv} ({len(cat_df)} clips)")

