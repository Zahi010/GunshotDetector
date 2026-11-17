import sys
import pathlib
import time
import numpy as np
import soundfile as sf
import pandas as pd

sys.path.insert(0, "e:/gunshot/gunshot")
from scratch.run_full_v9_evaluation import DetectorImprovementV9
from experiments.detector_improvement_v8.model_detector_improvement_v8 import DetectorImprovementV8

def run_continuous_eval():
    streams_csv = pathlib.Path("e:/gunshot/gunshot/experiments/phase51_validation/continuous_stream_evaluation.csv")
    sdf = pd.read_csv(streams_csv)
    print(f"Loaded {len(sdf)} continuous streams.")

    # Find stream file paths
    all_wavs = list(pathlib.Path("e:/gunshot/gunshot/data").glob("**/*.wav"))
    path_map = {p.name: p for p in all_wavs}

    det_v9 = DetectorImprovementV9()
    det_v8 = DetectorImprovementV8()

    results = []

    for _, row in sdf.iterrows():
        sname = row["stream_filename"]
        fpath = path_map.get(sname)
        if not fpath or not fpath.exists():
            print(f"Warning: Stream {sname} not found!")
            continue

        audio, sr = sf.read(str(fpath))
        if audio.ndim > 1: audio = np.mean(audio, axis=1)
        if sr != 16000:
            import librosa
            audio = librosa.resample(audio, orig_sr=sr, target_sr=16000)
        audio = audio.astype(np.float32)

        dur_hr = len(audio) / 16000.0 / 3600.0

        res_v9 = det_v9.evaluate_waveform(audio, 16000)
        v9_alerts = res_v9["event_count"]

        v8_alerts = int(row["v8_alerts"])

        results.append({
            "stream_filename": sname,
            "description": row["description"],
            "duration_hours": round(dur_hr, 3),
            "v8_alerts": v8_alerts,
            "v8_alerts_per_hr": round(v8_alerts / max(dur_hr, 0.001), 2),
            "v9_alerts": v9_alerts,
            "v9_alerts_per_hr": round(v9_alerts / max(dur_hr, 0.001), 2)
        })
        print(f"{sname} ({dur_hr:.2f} hr): V8 alerts={v8_alerts}, V9 alerts={v9_alerts}")

    res_df = pd.DataFrame(results)
    out_csv = pathlib.Path("e:/gunshot/gunshot/scratch/v8_v9_continuous_eval.csv")
    res_df.to_csv(out_csv, index=False)
    print(f"\nContinuous stream evaluation results saved to {out_csv}")

    tot_hr = res_df["duration_hours"].sum()
    tot_v8 = res_df["v8_alerts"].sum()
    tot_v9 = res_df["v9_alerts"].sum()
    print(f"Total Hours: {tot_hr:.2f}")
    print(f"Total V8 Alerts: {tot_v8} ({tot_v8/tot_hr:.4f}/hr)")
    print(f"Total V9 Alerts: {tot_v9} ({tot_v9/tot_hr:.4f}/hr)")

if __name__ == "__main__":
    run_continuous_eval()

