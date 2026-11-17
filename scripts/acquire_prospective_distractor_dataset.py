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
# Strictly exclude any clip containing Gunshot_and_gunfire
dev_neg = dev_df[~dev_df['labels'].str.contains('Gunshot_and_gunfire', na=False)].copy()

audio_dir = pathlib.Path('E:/FSD50K.dev_audio/FSD50K.dev_audio')
dest_dir = pathlib.Path('E:/gunshot/gunshot/experiments/phase38/dataset/distractors')
dest_dir.mkdir(parents=True, exist_ok=True)

categories = {
    'DISTRACTOR_FIREWORKS': ('Fireworks', 20),
    'DISTRACTOR_THUNDER_EXPLOSION': ('Thunder|Explosion', 20),
    'DISTRACTOR_ANIMAL_BARK': ('Bark|Dog', 20),
    'DISTRACTOR_AIRCRAFT': ('Aircraft', 20),
    'DISTRACTOR_SLAM_DOOR': ('Slam|Door', 20),
    'DISTRACTOR_TOOLS_IMPACT': ('Power_tool|Drill|Hammer|Crushing', 20)
}

selected_distractors = []
seen_fnames = set()

for cat_name, (pattern, target_count) in categories.items():
    matched = dev_neg[dev_neg['labels'].str.contains(pattern, na=False)]
    # Pick distinct uploaders and unseen fnames
    uploader_clips = {}
    for idx, row in matched.iterrows():
        fn = f"{row['fname']}.wav"
        if row['fname'] in seen_fnames:
            continue
        p = audio_dir / fn
        if p.exists():
            info = dev_info.get(str(row['fname']), {})
            up = info.get('uploader', 'unknown')
            if up not in uploader_clips:
                uploader_clips[up] = []
            uploader_clips[up].append((row, p, info))
    
    cat_selected = []
    for up, clips in uploader_clips.items():
        if len(cat_selected) >= target_count:
            break
        row, p, info = clips[0]
        seen_fnames.add(row['fname'])
        cat_selected.append({
            'recording_id': f"fsd50k_dist_{cat_name}_{row['fname']}",
            'filename': f"{row['fname']}.wav",
            'category': cat_name,
            'src_path': p,
            'uploader': up,
            'license': info.get('license', 'CC BY 4.0'),
            'title': info.get('title', ''),
            'labels': row['labels'],
            'tags': ",".join(info.get('tags', []))
        })
    selected_distractors.extend(cat_selected)
    print(f"Category {cat_name}: selected {len(cat_selected)} clips across {len(cat_selected)} distinct uploaders.")

# Copy and catalog
distractor_catalog = []
for d in selected_distractors:
    dest_path = dest_dir / d['filename']
    if not dest_path.exists():
        shutil.copy2(d['src_path'], dest_path)
    
    data = dest_path.read_bytes()
    sha = hashlib.sha256(data).hexdigest()
    info = sf.info(str(dest_path))
    
    distractor_catalog.append({
        'recording_id': d['recording_id'],
        'filename': d['filename'],
        'partition': 'PARTITION_PROSPECTIVE_DISTRACTOR',
        'distractor_category': d['category'],
        'source_dataset': 'FSD50K_dev',
        'uploader_session': d['uploader'],
        'license': d['license'],
        'title': d['title'],
        'labels': d['labels'],
        'tags': d['tags'],
        'duration_seconds': round(info.duration, 4),
        'sample_rate_hz': info.samplerate,
        'channels': info.channels,
        'sha256': sha
    })

dist_df = pd.DataFrame(distractor_catalog)
out_csv = pathlib.Path('E:/gunshot/gunshot/experiments/phase38/dataset/phase38_distractor_catalog.csv')
dist_df.to_csv(out_csv, index=False)
print(f"Saved distractor catalog to {out_csv} ({len(dist_df)} clips)")
