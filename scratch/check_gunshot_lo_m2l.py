import sys
import os
import pathlib
import numpy as np
import soundfile as sf
import pandas as pd

sys.path.insert(0, "e:/gunshot/gunshot")
from experiments.detector_improvement_v8.model_detector_improvement_v8 import (
    DetectorImprovementV8,
    compute_physical_acoustic_features_v8
)

def inspect_positives():
    det = DetectorImprovementV8()

    # Load Phase 51 manifest
    p51_path = pathlib.Path("e:/gunshot/gunshot/experiments/phase51_validation/phase51_evaluation_manifest.csv")
    df = pd.read_csv(p51_path)
    positives = df[df["ground_truth_label"] == 1]
    print(f"Loaded {len(positives)} positive files from Phase 51.")

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

        win_metrics = []
        for w in range(n_wins):
            st = w * hop_size
            en = st + win_size
            win = y_proc[st:en]
            acoustics = compute_physical_acoustic_features_v8(win, sr=16000)
            crest, flat, hi, mid, lo, m2l, rolloff, cent, rms, peak = acoustics
            win_metrics.append({
                "lo": lo, "mid": mid, "hi": hi, "m2l": m2l,
                "cent": cent, "crest": crest, "peak": peak, "rms": rms
            })

        # Peak energy window
        peak_win = max(win_metrics, key=lambda m: m["peak"])
        records.append({
            "filename": fpath.name,
            "category": row.get("condition_category", "unknown"),
            "lo": round(peak_win["lo"], 4),
            "mid": round(peak_win["mid"], 4),
            "hi": round(peak_win["hi"], 4),
            "m2l": round(peak_win["m2l"], 4),
            "cent": round(peak_win["cent"], 1),
            "crest": round(peak_win["crest"], 2),
            "peak": round(peak_win["peak"], 4)
        })

    pdf = pd.DataFrame(records)
    out_csv = pathlib.Path("e:/gunshot/gunshot/scratch/positives_lo_m2l.csv")
    pdf.to_csv(out_csv, index=False)
    print(f"Exported positive acoustics to {out_csv}")

    print("\n--- Summary by Subgroup ---")
    for cat, g in pdf.groupby("category"):
        print(f"Category: {cat} (N={len(g)})")
        print(f"  lo: mean={g['lo'].mean():.4f}, min={g['lo'].min():.4f}, max={g['lo'].max():.4f}")
        print(f"  m2l: mean={g['m2l'].mean():.4f}, min={g['m2l'].min():.4f}, max={g['m2l'].max():.4f}")
        print(f"  cent: mean={g['cent'].mean():.1f}, min={g['cent'].min():.1f}, max={g['cent'].max():.1f}")
        print(f"  peak: mean={g['peak'].mean():.4f}, min={g['peak'].min():.4f}, max={g['peak'].max():.4f}")

if __name__ == "__main__":
    inspect_positives()
