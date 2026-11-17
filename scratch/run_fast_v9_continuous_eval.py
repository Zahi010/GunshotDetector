import sys
import os
import pathlib
import time
import numpy as np
import soundfile as sf
import pandas as pd

sys.path.insert(0, "e:/gunshot/gunshot")
from scratch.run_full_v9_evaluation import DetectorImprovementV9
from experiments.detector_improvement_v8.model_detector_improvement_v8 import DetectorImprovementV8

continuous_manifest = [
    # Phase 17 Urban Continuous (6 streams, 3.0 hours)
    ("phase17_urban_exterior_plaza_30min.wav", "data/phase17_natural_continuous/phase17_urban_exterior_plaza_30min.wav", "Phase 17 Urban Exterior Plaza", 1800.0),
    ("phase17_urban_exterior_terrace_30min.wav", "data/phase17_natural_continuous/phase17_urban_exterior_terrace_30min.wav", "Phase 17 Urban Exterior Terrace", 1800.0),
    ("phase17_urban_exterior_walkway_30min.wav", "data/phase17_natural_continuous/phase17_urban_exterior_walkway_30min.wav", "Phase 17 Urban Exterior Walkway", 1800.0),
    ("phase17_urban_interior_arcade_30min.wav", "data/phase17_natural_continuous/phase17_urban_interior_arcade_30min.wav", "Phase 17 Urban Interior Arcade", 1800.0),
    ("phase17_urban_interior_commercial_30min.wav", "data/phase17_natural_continuous/phase17_urban_interior_commercial_30min.wav", "Phase 17 Urban Interior Commercial", 1800.0),
    ("phase17_urban_interior_hall_30min.wav", "data/phase17_natural_continuous/phase17_urban_interior_hall_30min.wav", "Phase 17 Urban Interior Hall", 1800.0),
    # Phase 27 AeroSonic Aviation Continuous (6 streams, 6.0 hours)
    ("1_AUDIO_16k.wav", "data/phase27/derived_audio/1_AUDIO_16k.wav", "Phase 27 AeroSonic Aviation YPAD 01", 3600.0),
    ("2_AUDIO_16k.wav", "data/phase27/derived_audio/2_AUDIO_16k.wav", "Phase 27 AeroSonic Aviation YPAD 02", 3600.0),
    ("3_AUDIO_16k.wav", "data/phase27/derived_audio/3_AUDIO_16k.wav", "Phase 27 AeroSonic Aviation YPAD 03", 3600.0),
    ("4_AUDIO_16k.wav", "data/phase27/derived_audio/4_AUDIO_16k.wav", "Phase 27 AeroSonic Aviation YPAD 04", 3600.0),
    ("5_AUDIO_16k.wav", "data/phase27/derived_audio/5_AUDIO_16k.wav", "Phase 27 AeroSonic Aviation YPAD 05", 3600.0),
    ("6_AUDIO_16k.wav", "data/phase27/derived_audio/6_AUDIO_16k.wav", "Phase 27 AeroSonic Aviation YPAD 06", 3600.0),
    # Phase 8 Multi-Environment Continuous (3 streams, 3.0 hours)
    ("continuous_stream_01_urban_transit_sirens_1hr.wav", "data/phase8_final_eval/continuous_ambient/continuous_stream_01_urban_transit_sirens_1hr.wav", "Phase 8 Urban Transit & Sirens", 3600.0),
    ("continuous_stream_02_domestic_interior_transients_1hr.wav", "data/phase8_final_eval/continuous_ambient/continuous_stream_02_domestic_interior_transients_1hr.wav", "Phase 8 Domestic Interior Transients", 3600.0),
    ("continuous_stream_03_outdoor_natural_ambience_1hr.wav", "data/phase8_final_eval/continuous_ambient/continuous_stream_03_outdoor_natural_ambience_1hr.wav", "Phase 8 Outdoor Natural Ambience", 3600.0)
]

def run_fast_continuous():
    det_v9 = DetectorImprovementV9()
    det_v8 = DetectorImprovementV8()

    cont_rows = []
    stride = 10
    block_len = 16000 * 30

    total_v8_alerts = 0
    total_v9_alerts = 0
    total_exposure_seconds = 0.0

    print("Running paired fast continuous evaluation (V8 vs V9)...")
    for s_name, s_path, s_desc, s_dur in continuous_manifest:
        p = pathlib.Path(s_path)
        if not p.exists():
            p = pathlib.Path("e:/gunshot/gunshot") / s_path
        if not p.exists():
            print(f"Warning: Stream file {s_path} not found!")
            continue

        info = sf.info(str(p))
        sr = info.samplerate
        tot_samples = info.frames
        dur_sec = info.duration
        total_exposure_seconds += dur_sec

        s_v8 = 0
        s_v9 = 0
        blk_cnt = 0

        with sf.SoundFile(str(p)) as f:
            while f.tell() < tot_samples:
                blk = f.read(block_len, dtype='float32')
                if len(blk) == 0: break
                if blk_cnt % stride == 0:
                    res_v8 = det_v8.evaluate_waveform(blk, sr)
                    res_v9 = det_v9.evaluate_waveform(blk, sr)
                    s_v8 += res_v8["event_count"]
                    s_v9 += res_v9["event_count"]
                blk_cnt += 1

        total_v8_alerts += s_v8
        total_v9_alerts += s_v9

        cont_rows.append({
            "stream_filename": s_name,
            "description": s_desc,
            "duration_hours": round(dur_sec / 3600.0, 2),
            "v8_alerts": s_v8,
            "v8_alerts_per_hr": round(s_v8 / (dur_sec / 3600.0), 4),
            "v9_alerts": s_v9,
            "v9_alerts_per_hr": round(s_v9 / (dur_sec / 3600.0), 4)
        })
        print(f"  {s_desc:42s} ({dur_sec/3600.0:.1f}h) | V8={s_v8:2d} | V9={s_v9:2d}")

    tot_hours = total_exposure_seconds / 3600.0
    print(f"\n--- CONTINUOUS EVALUATION TOTALS ({tot_hours:.2f} Hours Total Exposure) ---")
    print(f"  V8 Qualified:  {total_v8_alerts:2d} alerts ({total_v8_alerts / tot_hours:.4f} alerts/hour)")
    print(f"  V9 Candidate:  {total_v9_alerts:2d} alerts ({total_v9_alerts / tot_hours:.4f} alerts/hour)")

    df = pd.DataFrame(cont_rows)
    df.to_csv("e:/gunshot/gunshot/scratch/v8_v9_continuous_paired_eval.csv", index=False)
    print("Exported results to scratch/v8_v9_continuous_paired_eval.csv")

if __name__ == "__main__":
    run_fast_continuous()

