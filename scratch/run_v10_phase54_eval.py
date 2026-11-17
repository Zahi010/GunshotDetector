import sys
import os
import time
import pandas as pd
import numpy as np
import soundfile as sf
import librosa

sys.path.insert(0, "e:/gunshot/gunshot")
from experiments.detector_improvement_v10.model_detector_improvement_v10 import DetectorImprovementV10

print("=" * 70)
print("PHASE 54: LOCKED V10 EVALUATION ON GENUINELY NEW CORPUS (N=351)")
print("=" * 70)

manifest_path = "e:/gunshot/gunshot/experiments/phase54_final_validation/phase54_evaluation_manifest.csv"
df = pd.read_csv(manifest_path)
print(f"Loaded manifest with {len(df)} files.")

det10 = DetectorImprovementV10()

results = []
t_start = time.time()

for idx, row in df.iterrows():
    fpath = row['filepath']
    try:
        audio, sr = sf.read(fpath, dtype='float32')
        if audio.ndim > 1:
            audio = np.mean(audio, axis=1)
        if sr != 16000:
            audio = librosa.resample(audio, orig_sr=sr, target_sr=16000)
        audio = audio.astype(np.float32)
        
        t0 = time.time()
        res = det10.evaluate_waveform(audio, 16000)
        elapsed_ms = (time.time() - t0) * 1000.0
        
        pred = 1 if res['detected'] else 0
        peak_score = round(float(res['peak_score']), 4)
        n_events = len(res['events'])
        
        results.append({
            'fname': row['fname'],
            'filepath': row['filepath'],
            'title': row['title'],
            'uploader': row['uploader'],
            'ground_truth_label': int(row['ground_truth_label']),
            'category': row['category'],
            'sub_category': row['sub_category'],
            'acoustic_condition': row['acoustic_condition'],
            'duration_sec': row['duration_sec'],
            'prediction': pred,
            'peak_score': peak_score,
            'num_events': n_events,
            'latency_ms': round(elapsed_ms, 2)
        })
        
        if (idx + 1) % 50 == 0 or (idx + 1) == len(df):
            print(f"Processed {idx + 1}/{len(df)} files ({(idx+1)/len(df)*100:.1f}%) in {time.time()-t_start:.1f}s...")
    except Exception as e:
        print(f"Error processing {fpath}: {e}")
        results.append({
            'fname': row['fname'],
            'filepath': row['filepath'],
            'title': row['title'],
            'uploader': row['uploader'],
            'ground_truth_label': int(row['ground_truth_label']),
            'category': row['category'],
            'sub_category': row['sub_category'],
            'acoustic_condition': row['acoustic_condition'],
            'duration_sec': row['duration_sec'],
            'prediction': 0,
            'peak_score': 0.0,
            'num_events': 0,
            'latency_ms': 0.0,
            'error': str(e)
        })

res_df = pd.DataFrame(results)

# Save recording level predictions
out_csv = "e:/gunshot/gunshot/experiments/phase54_final_validation/recording_level_predictions.csv"
res_df.to_csv(out_csv, index=False)
print(f"\nRecording-level predictions saved to {out_csv}")

# Summary Metrics
pos_df = res_df[res_df['ground_truth_label'] == 1]
neg_df = res_df[res_df['ground_truth_label'] == 0]

pos_rec = pos_df['prediction'].mean() * 100.0
neg_fpr = neg_df['prediction'].mean() * 100.0

print("\n" + "=" * 70)
print(f"OVERALL EVALUATION RESULTS (N={len(res_df)}):")
print(f"  Positive Recall:       {pos_df['prediction'].sum()}/{len(pos_df)} ({pos_rec:.2f}%)")
print(f"  Negative False Alarms: {neg_df['prediction'].sum()}/{len(neg_df)} (FPR: {neg_fpr:.2f}%)")
print("=" * 70)

print("\nRECALL BY ACOUSTIC CONDITION:")
for cond, g in pos_df.groupby('sub_category'):
    rec = g['prediction'].mean() * 100.0
    print(f"  {cond:30s} (N={len(g):2d}): {g['prediction'].sum()}/{len(g)} ({rec:5.1f}%), mean_peak={g['peak_score'].mean():.4f}")

print("\nFALSE POSITIVE RATE BY NEGATIVE CATEGORY:")
for cat, g in neg_df.groupby('sub_category'):
    fpr = g['prediction'].mean() * 100.0
    max_score = g['peak_score'].max()
    print(f"  {cat:32s} (N={len(g):2d}): {g['prediction'].sum()}/{len(g)} (FPR: {fpr:5.1f}%), max_peak={max_score:.4f}")

