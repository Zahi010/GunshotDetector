import os
import json
import hashlib
import pandas as pd
import soundfile as sf
import librosa
import numpy as np

# Load FSD50K eval ground truth and metadata
eval_df = pd.read_csv('e:/FSD50K.dev_audio/FSD50K.ground_truth/eval.csv')
with open('e:/FSD50K.dev_audio/FSD50K.metadata/eval_clips_info_FSD50K.json') as f:
    clip_info = json.load(f)

audio_dir = 'e:/FSD50K.dev_audio/FSD50K.eval_audio/FSD50K.eval_audio'

# Target output directory for Phase 54 validation corpus
out_dir = 'e:/gunshot/gunshot/experiments/phase54_final_validation'
os.makedirs(out_dir, exist_ok=True)
manifest_path = os.path.join(out_dir, 'phase54_evaluation_manifest.csv')

def get_clip_text(fname):
    info = clip_info.get(str(fname), {})
    return (info.get("title", "") + " " + info.get("description", "") + " " + " ".join(info.get("tags", []))).lower()

curated_records = []

# 1. Positives: All 134 Gunshot_and_gunfire files
gun_df = eval_df[eval_df['labels'].str.contains('Gunshot_and_gunfire', na=False)]
for _, row in gun_df.iterrows():
    fname = int(row['fname'])
    fpath = os.path.join(audio_dir, f"{fname}.wav")
    if not os.path.exists(fpath):
        continue
    info = clip_info.get(str(fname), {})
    text = get_clip_text(fname)
    
    # Categorize recording condition
    if any(k in text for k in ['burst', 'rapid', 'full auto', 'machine', 'automatic', 'spray']):
        cond = 'rapid_cadence_burst'
    elif any(k in text for k in ['reverb', 'echo', 'hall', 'tunnel', 'canyon', 'forest', 'indoor']):
        cond = 'reverberant_indoor'
    elif any(k in text for k in ['distant', 'far', 'distance', 'away']):
        cond = 'distant_field'
    elif any(k in text for k in ['distort', 'clip', 'loud', 'overload']):
        cond = 'clipped_high_energy'
    else:
        cond = 'clean_open_air'
        
    curated_records.append({
        'fname': fname,
        'filepath': fpath,
        'title': info.get('title', ''),
        'uploader': info.get('uploader', 'unknown'),
        'license': info.get('license', ''),
        'ground_truth_label': 1,
        'category': 'genuine_gunshot',
        'sub_category': cond,
        'acoustic_condition': cond
    })

print(f"Curated {len(curated_records)} positive gunshot recordings.")

# 2. Hard Negatives: Fireworks (up to 30)
fw_df = eval_df[eval_df['labels'].str.contains('Fireworks', na=False)]
fw_count = 0
for _, row in fw_df.iterrows():
    fname = int(row['fname'])
    if fname in [r['fname'] for r in curated_records]: continue
    fpath = os.path.join(audio_dir, f"{fname}.wav")
    if not os.path.exists(fpath): continue
    info = clip_info.get(str(fname), {})
    curated_records.append({
        'fname': fname,
        'filepath': fpath,
        'title': info.get('title', ''),
        'uploader': info.get('uploader', 'unknown'),
        'license': info.get('license', ''),
        'ground_truth_label': 0,
        'category': 'hard_negative',
        'sub_category': 'fireworks_pyrotechnics',
        'acoustic_condition': 'pyrotechnic_combustion'
    })
    fw_count += 1
    if fw_count >= 30: break

# 3. Hard Negatives: Balloon bursts
balloon_count = 0
for fname_str, info in clip_info.items():
    fname = int(fname_str)
    if fname in [r['fname'] for r in curated_records]: continue
    fpath = os.path.join(audio_dir, f"{fname}.wav")
    if not os.path.exists(fpath): continue
    text = get_clip_text(fname)
    if 'balloon' in text and any(w in text for w in ['pop', 'burst', 'blow', 'punct']):
        curated_records.append({
            'fname': fname,
            'filepath': fpath,
            'title': info.get('title', ''),
            'uploader': info.get('uploader', 'unknown'),
            'license': info.get('license', ''),
            'ground_truth_label': 0,
            'category': 'hard_negative',
            'sub_category': 'balloon_bursts',
            'acoustic_condition': 'membrane_rupture'
        })
        balloon_count += 1

# 4. Hard Negatives: Door slams
door_count = 0
for fname_str, info in clip_info.items():
    fname = int(fname_str)
    if fname in [r['fname'] for r in curated_records]: continue
    fpath = os.path.join(audio_dir, f"{fname}.wav")
    if not os.path.exists(fpath): continue
    text = get_clip_text(fname)
    if 'door' in text and any(w in text for w in ['slam', 'close', 'shut', 'bang']):
        curated_records.append({
            'fname': fname,
            'filepath': fpath,
            'title': info.get('title', ''),
            'uploader': info.get('uploader', 'unknown'),
            'license': info.get('license', ''),
            'ground_truth_label': 0,
            'category': 'hard_negative',
            'sub_category': 'heavy_door_slams',
            'acoustic_condition': 'structural_impact'
        })
        door_count += 1
        if door_count >= 25: break

# 5. Hard Negatives: Vehicle backfires
backfire_count = 0
for fname_str, info in clip_info.items():
    fname = int(fname_str)
    if fname in [r['fname'] for r in curated_records]: continue
    fpath = os.path.join(audio_dir, f"{fname}.wav")
    if not os.path.exists(fpath): continue
    text = get_clip_text(fname)
    if 'backfire' in text:
        curated_records.append({
            'fname': fname,
            'filepath': fpath,
            'title': info.get('title', ''),
            'uploader': info.get('uploader', 'unknown'),
            'license': info.get('license', ''),
            'ground_truth_label': 0,
            'category': 'hard_negative',
            'sub_category': 'vehicle_backfires',
            'acoustic_condition': 'automotive_combustion'
        })
        backfire_count += 1

# 6. Hard Negatives: Glass breakage
glass_count = 0
glass_df = eval_df[eval_df['labels'].str.contains('Glass', na=False)]
for _, row in glass_df.iterrows():
    fname = int(row['fname'])
    if fname in [r['fname'] for r in curated_records]: continue
    fpath = os.path.join(audio_dir, f"{fname}.wav")
    if not os.path.exists(fpath): continue
    text = get_clip_text(fname)
    if any(w in text for w in ['break', 'shatter', 'smash', 'crack', 'fall']):
        info = clip_info.get(str(fname), {})
        curated_records.append({
            'fname': fname,
            'filepath': fpath,
            'title': info.get('title', ''),
            'uploader': info.get('uploader', 'unknown'),
            'license': info.get('license', ''),
            'ground_truth_label': 0,
            'category': 'hard_negative',
            'sub_category': 'glass_breakage',
            'acoustic_condition': 'resonant_shatter'
        })
        glass_count += 1
        if glass_count >= 25: break

# 7. Hard Negatives: Metal Hammer Impacts
hammer_count = 0
hammer_df = eval_df[eval_df['labels'].str.contains('Hammer', na=False)]
for _, row in hammer_df.iterrows():
    fname = int(row['fname'])
    if fname in [r['fname'] for r in curated_records]: continue
    fpath = os.path.join(audio_dir, f"{fname}.wav")
    if not os.path.exists(fpath): continue
    text = get_clip_text(fname)
    if any(w in text for w in ['hit', 'pound', 'strike', 'anvil', 'metal', 'clang']):
        info = clip_info.get(str(fname), {})
        curated_records.append({
            'fname': fname,
            'filepath': fpath,
            'title': info.get('title', ''),
            'uploader': info.get('uploader', 'unknown'),
            'license': info.get('license', ''),
            'ground_truth_label': 0,
            'category': 'hard_negative',
            'sub_category': 'metal_hammer_impacts',
            'acoustic_condition': 'metallic_impact'
        })
        hammer_count += 1
        if hammer_count >= 25: break

# 8. Hard Negatives: Thunder Rumbles
thunder_count = 0
thunder_df = eval_df[eval_df['labels'].str.contains('Thunder', na=False)]
for _, row in thunder_df.iterrows():
    fname = int(row['fname'])
    if fname in [r['fname'] for r in curated_records]: continue
    fpath = os.path.join(audio_dir, f"{fname}.wav")
    if not os.path.exists(fpath): continue
    info = clip_info.get(str(fname), {})
    curated_records.append({
        'fname': fname,
        'filepath': fpath,
        'title': info.get('title', ''),
        'uploader': info.get('uploader', 'unknown'),
        'license': info.get('license', ''),
        'ground_truth_label': 0,
        'category': 'hard_negative',
        'sub_category': 'thunder_rumbles',
        'acoustic_condition': 'infrasonic_atmospheric'
    })
    thunder_count += 1
    if thunder_count >= 25: break

# 9. Environmental Negatives: Urban Traffic & Sirens (25 files)
traffic_count = 0
for _, row in eval_df[eval_df['labels'].str.contains('Motorcycle|Bus|Truck|Siren', na=False)].iterrows():
    fname = int(row['fname'])
    if fname in [r['fname'] for r in curated_records]: continue
    fpath = os.path.join(audio_dir, f"{fname}.wav")
    if not os.path.exists(fpath): continue
    info = clip_info.get(str(fname), {})
    curated_records.append({
        'fname': fname,
        'filepath': fpath,
        'title': info.get('title', ''),
        'uploader': info.get('uploader', 'unknown'),
        'license': info.get('license', ''),
        'ground_truth_label': 0,
        'category': 'environmental_negative',
        'sub_category': 'urban_transit_sirens',
        'acoustic_condition': 'urban_mechanical'
    })
    traffic_count += 1
    if traffic_count >= 25: break

# 10. Environmental Negatives: Bioacoustic & Human Vocalizations (25 files: bark, cough, cry)
bio_count = 0
for _, row in eval_df[eval_df['labels'].str.contains('Bark|Cough|Crying_and_sobbing', na=False)].iterrows():
    fname = int(row['fname'])
    if fname in [r['fname'] for r in curated_records]: continue
    fpath = os.path.join(audio_dir, f"{fname}.wav")
    if not os.path.exists(fpath): continue
    info = clip_info.get(str(fname), {})
    curated_records.append({
        'fname': fname,
        'filepath': fpath,
        'title': info.get('title', ''),
        'uploader': info.get('uploader', 'unknown'),
        'license': info.get('license', ''),
        'ground_truth_label': 0,
        'category': 'environmental_negative',
        'sub_category': 'bioacoustic_human_vocalizations',
        'acoustic_condition': 'organic_transients'
    })
    bio_count += 1
    if bio_count >= 25: break

# 11. Environmental Negatives: Natural Outdoor Ambience (25 files: wind, rain, waves)
nat_count = 0
for _, row in eval_df[eval_df['labels'].str.contains('Wind|Rain|Waves_and_surf', na=False)].iterrows():
    fname = int(row['fname'])
    if fname in [r['fname'] for r in curated_records]: continue
    fpath = os.path.join(audio_dir, f"{fname}.wav")
    if not os.path.exists(fpath): continue
    info = clip_info.get(str(fname), {})
    curated_records.append({
        'fname': fname,
        'filepath': fpath,
        'title': info.get('title', ''),
        'uploader': info.get('uploader', 'unknown'),
        'license': info.get('license', ''),
        'ground_truth_label': 0,
        'category': 'environmental_negative',
        'sub_category': 'natural_outdoor_ambience',
        'acoustic_condition': 'weather_hydrodynamic'
    })
    nat_count += 1
    if nat_count >= 25: break

print(f"Total curated records: {len(curated_records)}")
df_cur = pd.DataFrame(curated_records)

# Calculate duration and SHA256 for all curated records
durations = []
hashes = []
for idx, r in df_cur.iterrows():
    with open(r['filepath'], 'rb') as fp:
        h = hashlib.sha256(fp.read()).hexdigest()
    hashes.append(h)
    inf = sf.info(r['filepath'])
    durations.append(round(inf.duration, 3))

df_cur['duration_sec'] = durations
df_cur['sha256'] = hashes

df_cur.to_csv(manifest_path, index=False)
print(f"Manifest written to {manifest_path}")
print(df_cur.groupby(['category', 'sub_category']).size())

