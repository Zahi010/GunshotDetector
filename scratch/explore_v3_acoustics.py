"""
Explore physical acoustic feature distributions on genuine gunshots,
fireworks, environmental distractors, and continuous background.
"""

import pathlib
import librosa
import numpy as np
import pandas as pd

# Load dev partition
parts = pd.read_csv("scratch/v2_partitions.csv")
inv = pd.read_csv("experiments/phase41/phase41_recording_inventory.csv")
merged = pd.merge(inv, parts[['recording_id', 'v2_partition']], on='recording_id')

dev_df = merged[merged['v2_partition'] == 'development'].copy()
print(f"Loaded {len(dev_df)} development recordings.")

p38 = pathlib.Path("experiments/phase38/dataset")
p39 = pathlib.Path("experiments/phase39/dataset")
p40 = pathlib.Path("experiments/phase40/dataset")

def find_audio_file(row):
    fn = row['filename']
    role = row['evaluation_role']
    # Check paths
    candidates = [
        p38 / "positive" / fn,
        p38 / "distractors" / fn,
        p38 / "continuous" / fn,
        p39 / "distractor" / fn,
        p39 / "continuous" / fn,
        p40 / "continuous" / fn
    ]
    for c in candidates:
        if c.exists():
            return c
    return None

def extract_window_acoustics(y, sr=16000):
    if len(y) == 0:
        return {}
    peak = np.max(np.abs(y))
    rms = np.sqrt(np.mean(y**2) + 1e-12)
    crest_db = 20 * np.log10(max(peak / (rms + 1e-12), 1.0))
    
    # STFT
    stft = np.abs(librosa.stft(y, n_fft=512, hop_length=128))
    freqs = librosa.fft_frequencies(sr=sr, n_fft=512)
    
    low_e = np.sum(stft[freqs < 250, :]**2)
    mid_e = np.sum(stft[(freqs >= 250) & (freqs < 2000), :]**2)
    high_e = np.sum(stft[(freqs >= 2000) & (freqs < 5000), :]**2)
    vhigh_e = np.sum(stft[freqs >= 5000, :]**2)
    tot_e = low_e + mid_e + high_e + vhigh_e + 1e-12
    
    centroid = float(np.mean(librosa.feature.spectral_centroid(y=y, sr=sr)))
    rolloff = float(np.mean(librosa.feature.spectral_rolloff(y=y, sr=sr)))
    flatness = float(np.mean(librosa.feature.spectral_flatness(y=y)))
    
    # Rise time & decay ratio
    pk_idx = np.argmax(np.abs(y))
    th10 = 0.10 * peak
    pre = np.abs(y[:pk_idx])
    below = np.where(pre < th10)[0]
    rise_idx = below[-1] if len(below) > 0 else 0
    rise_ms = (pk_idx - rise_idx) / float(sr) * 1000.0
    
    post_idx = min(len(y), pk_idx + int(0.20 * sr))
    post_snip = y[pk_idx:post_idx]
    post_rms = np.sqrt(np.mean(post_snip**2) + 1e-12)
    decay_ratio = post_rms / (peak + 1e-12)
    
    return {
        "crest_db": crest_db,
        "centroid": centroid,
        "rolloff": rolloff,
        "flatness": flatness,
        "low_ratio": low_e / tot_e,
        "mid_ratio": mid_e / tot_e,
        "high_ratio": high_e / tot_e,
        "vhigh_ratio": vhigh_e / tot_e,
        "rise_ms": rise_ms,
        "decay_ratio": decay_ratio
    }

print("Extracting physical acoustics across development groups...")
records = []
for idx, r in dev_df.iterrows():
    fpath = find_audio_file(r)
    if fpath is None:
        continue
    # Load audio
    y, sr = librosa.load(fpath, sr=16000, mono=True)
    if len(y) > 16000 * 10:
        # Sample first 60 seconds if continuous
        y = y[:16000 * 60]
    
    # Peak 0.96s window
    win_len = 15360
    if len(y) <= win_len:
        y_win = y
    else:
        # find peak amplitude window
        pk_sample = np.argmax(np.abs(y))
        st = max(0, pk_sample - win_len // 2)
        ed = min(len(y), st + win_len)
        y_win = y[st:ed]
        
    m = extract_window_acoustics(y_win, sr=16000)
    m['recording_id'] = r['recording_id']
    m['sub_category'] = r['sub_category']
    m['ground_truth'] = 1 if r['evaluation_role'] == 'PROSPECTIVE_POSITIVE_EVALUATION' else 0
    records.append(m)

df_feat = pd.DataFrame(records)
print(f"Extracted features for {len(df_feat)} development recordings.")

# Compare across categories
for sc in sorted(df_feat['sub_category'].unique()):
    sub = df_feat[df_feat['sub_category'] == sc]
    print(f"\n--- {sc} (N={len(sub)}) ---")
    print(sub[['crest_db', 'centroid', 'flatness', 'low_ratio', 'mid_ratio', 'high_ratio', 'vhigh_ratio', 'decay_ratio']].mean().round(4))
