import librosa
import numpy as np
import pathlib

audio_path = pathlib.Path("experiments/phase40/dataset/continuous/p40_cont_03_bruxelles.mp3")
y, sr = librosa.load(audio_path, sr=16000, mono=True)

alert_peak_wins = [17, 47, 99, 212, 274, 318, 331, 446, 459, 531, 563, 573]

metrics_list = []
for w in alert_peak_wins:
    st = int((w * 0.48) * sr)
    chunk = y[st : st + 15360]
    
    peak = np.max(np.abs(chunk))
    rms = np.sqrt(np.mean(chunk**2) + 1e-12)
    crest_db = 20 * np.log10(max(peak / (rms + 1e-12), 1.0))
    
    stft = np.abs(librosa.stft(chunk, n_fft=512, hop_length=128))
    freqs = librosa.fft_frequencies(sr=sr, n_fft=512)
    
    low_band_energy = np.sum(stft[freqs < 250, :]**2)
    mid_band_energy = np.sum(stft[(freqs >= 250) & (freqs < 2000), :]**2)
    high_band_energy = np.sum(stft[freqs >= 2000, :]**2)
    total_energy = low_band_energy + mid_band_energy + high_band_energy + 1e-12
    
    low_ratio = low_band_energy / total_energy
    mid_ratio = mid_band_energy / total_energy
    high_ratio = high_band_energy / total_energy
    
    centroid = float(np.mean(librosa.feature.spectral_centroid(y=chunk, sr=sr)))
    rolloff = float(np.mean(librosa.feature.spectral_rolloff(y=chunk, sr=sr)))
    flatness = float(np.mean(librosa.feature.spectral_flatness(y=chunk)))
    
    # Peak index within chunk
    peak_idx = np.argmax(np.abs(chunk))
    threshold_10 = 0.10 * peak
    pre_peak = np.abs(chunk[:peak_idx])
    indices_below = np.where(pre_peak < threshold_10)[0]
    rise_idx = indices_below[-1] if len(indices_below) > 0 else 0
    rise_time_ms = (peak_idx - rise_idx) / float(sr) * 1000.0
    
    metrics_list.append({
        "win": w, "t": w*0.48, "peak": peak, "rms": rms, "crest_db": crest_db,
        "low_ratio": low_ratio, "mid_ratio": mid_ratio, "high_ratio": high_ratio,
        "centroid": centroid, "rolloff": rolloff, "flatness": flatness, "rise_time_ms": rise_time_ms
    })

import pandas as pd
df_bxl = pd.DataFrame(metrics_list)
print("=== ACOUSTIC METRICS AT BRUXELLES ALERT WINDOWS ===")
print(df_bxl[["win", "t", "peak", "rms", "crest_db", "flatness", "centroid", "low_ratio", "mid_ratio"]])
print("\nMean across Bruxelles alert windows:")
print(df_bxl.mean())

