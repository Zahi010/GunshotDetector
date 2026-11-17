import librosa
import numpy as np
import pandas as pd
import pathlib

p38_pos = pathlib.Path("experiments/phase38/dataset/positive")
p39_dist = pathlib.Path("experiments/phase39/dataset/distractor")
inv = pd.read_csv("experiments/phase41/phase41_recording_inventory.csv")

def extract_physical_acoustic_metrics(y, sr=16000):
    # 1. Peak & RMS
    peak = np.max(np.abs(y))
    rms = np.sqrt(np.mean(y**2) + 1e-12)
    crest_db = 20 * np.log10(max(peak / (rms + 1e-12), 1.0))
    
    # 2. Spectral energy distribution in sub-bands:
    # Sub-band 1: Infrasonic/Sub-bass (< 250 Hz)
    # Sub-band 2: Mid blast (250 Hz - 2000 Hz)
    # Sub-band 3: High/Crackle (> 2000 Hz)
    stft = np.abs(librosa.stft(y, n_fft=512, hop_length=128))
    freqs = librosa.fft_frequencies(sr=sr, n_fft=512)
    
    low_band_energy = np.sum(stft[freqs < 250, :]**2)
    mid_band_energy = np.sum(stft[(freqs >= 250) & (freqs < 2000), :]**2)
    high_band_energy = np.sum(stft[freqs >= 2000, :]**2)
    total_energy = low_band_energy + mid_band_energy + high_band_energy + 1e-12
    
    low_ratio = low_band_energy / total_energy
    mid_ratio = mid_band_energy / total_energy
    high_ratio = high_band_energy / total_energy
    
    # 3. Spectral centroid & rolloff
    centroid = float(np.mean(librosa.feature.spectral_centroid(y=y, sr=sr)))
    rolloff = float(np.mean(librosa.feature.spectral_rolloff(y=y, sr=sr)))
    flatness = float(np.mean(librosa.feature.spectral_flatness(y=y)))
    
    # 4. Temporal rise time: time from 10% of peak amplitude to peak amplitude
    peak_idx = np.argmax(np.abs(y))
    threshold_10 = 0.10 * peak
    pre_peak = np.abs(y[:peak_idx])
    indices_below = np.where(pre_peak < threshold_10)[0]
    rise_idx = indices_below[-1] if len(indices_below) > 0 else 0
    rise_time_ms = (peak_idx - rise_idx) / float(sr) * 1000.0
    
    # 5. Envelope decay: energy in 200ms following peak vs peak
    post_idx = min(len(y), peak_idx + int(0.20 * sr))
    post_peak_snip = y[peak_idx:post_idx]
    post_rms = np.sqrt(np.mean(post_peak_snip**2) + 1e-12)
    decay_ratio = post_rms / (peak + 1e-12)
    
    return {
        "crest_db": crest_db,
        "low_ratio": low_ratio,
        "mid_ratio": mid_ratio,
        "high_ratio": high_ratio,
        "centroid": centroid,
        "rolloff": rolloff,
        "flatness": flatness,
        "rise_time_ms": rise_time_ms,
        "decay_ratio": decay_ratio
    }

# Analyze 20 random genuine gunshots, 20 fireworks false alarms, 20 clean fireworks, and continuous gate
pos_files = list(p38_pos.glob("*.wav"))[:30]
fw_fp_cids = inv[inv['is_fireworks_eval'] == True]['filename'].tolist()[:30]

print("Analyzing acoustic features on genuine gunshots vs fireworks...")
pos_metrics = []
for p in pos_files:
    y, sr = librosa.load(p, sr=16000, mono=True)
    pos_metrics.append(extract_physical_acoustic_metrics(y, sr))

fw_metrics = []
for fname in fw_fp_cids:
    fpath = p39_dist / fname
    if fpath.exists():
        y, sr = librosa.load(fpath, sr=16000, mono=True)
        fw_metrics.append(extract_physical_acoustic_metrics(y, sr))

df_pos = pd.DataFrame(pos_metrics)
df_fw = pd.DataFrame(fw_metrics)

print("\n--- GENUINE GUNSHOTS (N=30) ---")
print(df_pos.mean())

print("\n--- FIREWORKS CHALLENGE (N=30) ---")
print(df_fw.mean())

