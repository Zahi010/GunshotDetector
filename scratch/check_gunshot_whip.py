import sys
import os
import pathlib
import numpy as np
import soundfile as sf
import pandas as pd

sys.path.insert(0, "e:/gunshot/gunshot")
from experiments.detector_improvement_v8.model_detector_improvement_v8 import (
    DetectorImprovementV8,
    PURE_GUN_CLASSES,
    GUN_CLASSES,
    BALLISTIC_CLASSES
)

def inspect_gunshot_whip():
    det = DetectorImprovementV8()
    p51_path = pathlib.Path("e:/gunshot/gunshot/experiments/phase51_validation/phase51_evaluation_manifest.csv")
    df = pd.read_csv(p51_path)
    positives = df[df["ground_truth_label"] == 1]

    records = []
    for _, row in positives.iterrows():
        fpath = pathlib.Path(row["filepath"])
        if not fpath.exists():
            fpath = pathlib.Path("e:/gunshot") / row["filepath"]
        if not fpath.exists():
            fpath = pathlib.Path("e:/gunshot/gunshot") / row["filepath"]

        audio, sr = sf.read(str(fpath))
        if audio.ndim > 1: audio = np.mean(audio, axis=1)
        if sr != 16000:
            import librosa
            audio = librosa.resample(audio, orig_sr=sr, target_sr=16000)
        audio = audio.astype(np.float32)

        win_size = 15360
        hop_size = 7680
        if len(audio) < win_size:
            y_proc = np.pad(audio, (0, win_size - len(audio)))
            n_wins = 1
        else:
            y_proc = audio
            n_wins = 1 + int((len(audio) - win_size) // hop_size)

        for w in range(n_wins):
            st = w * hop_size
            en = st + win_size
            win = y_proc[st:en]
            feat, ys, acoustics = det.extract_features(win)
            crest, flat, hi, mid, lo, m2l, rolloff, cent, rms, peak = acoustics

            pure_gun = max(ys.get(c, 0.0) for c in PURE_GUN_CLASSES)
            gun_s = max(ys.get(c, 0.0) for c in GUN_CLASSES)
            bal_s = max(ys.get(c, 0.0) for c in BALLISTIC_CLASSES)
            whip_s = ys.get(466, 0.0)
            ding_s = ys.get(477, 0.0)
            slap_s = ys.get(461, 0.0)

            records.append({
                "filename": fpath.name,
                "category": row.get("condition_category", "unknown"),
                "window": w,
                "pure_gun": pure_gun,
                "gun_s": gun_s,
                "bal_s": bal_s,
                "whip_s": whip_s,
                "ding_s": ding_s,
                "slap_s": slap_s,
                "cent": cent,
                "crest": crest,
                "peak": peak
            })

    pdf = pd.DataFrame(records)
    print(f"Total positive windows analyzed: {len(pdf)}")
    peak_windows = pdf.loc[pdf.groupby("filename")["peak"].idxmax()]
    print("\n--- Genuine Gunshots: Whip (Class 466) vs Gunshot (Class 421) ---")
    print(f"Mean Pure Gun: {peak_windows['pure_gun'].mean():.4f}")
    print(f"Mean Whip: {peak_windows['whip_s'].mean():.4f}")
    print(f"Max Whip on gunshots: {peak_windows['whip_s'].max():.4f}")
    print(f"Whip > Pure Gun on gunshots: {(peak_windows['whip_s'] > peak_windows['pure_gun']).sum()} / {len(peak_windows)}")
    print(f"Whip > 0.30 on gunshots: {(peak_windows['whip_s'] > 0.30).sum()} / {len(peak_windows)}")

    whip_heavy_gunshots = peak_windows[peak_windows['whip_s'] > 0.30]
    for _, r in whip_heavy_gunshots.iterrows():
        print(f"  {r['filename']} ({r['category']}): Whip={r['whip_s']:.3f}, PureGun={r['pure_gun']:.3f}, Bal={r['bal_s']:.3f}")

if __name__ == "__main__":
    inspect_gunshot_whip()

