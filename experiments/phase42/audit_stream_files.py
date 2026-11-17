import pandas as pd
import numpy as np
import soundfile as sf
import pathlib

REPO = pathlib.Path(".")
inv = pd.read_csv("experiments/phase41/phase41_recording_inventory.csv")
cont_inv = inv[inv["evaluation_partition"] == "CONTINUOUS_AMBIENT"].copy()

print(f"Total continuous streams in inventory: {len(cont_inv)}")

stream_audit = []
for idx, row in cont_inv.iterrows():
    rid = row["recording_id"]
    rel_p = row["relative_path"]
    full_p = REPO / rel_p
    
    # 1. Physical audio file check
    file_exists = full_p.exists()
    if file_exists:
        info = sf.info(full_p)
        source_sr = info.samplerate
        source_channels = info.channels
        source_frames = info.frames
        source_dur = info.duration
        source_format = info.format
        source_subtype = info.subtype
    else:
        source_sr = source_channels = source_frames = source_dur = 0
        source_format = source_subtype = "MISSING"

    # 2. Check feature cache (.npz)
    # Search in phase39 and phase40 feature caches
    cache_p = None
    for cdir in ["experiments/phase40/feature_cache", "experiments/phase39/feature_cache", "experiments/phase38/feature_cache"]:
        cand = REPO / cdir / f"{rid}.npz"
        if cand.exists():
            cache_p = cand
            break
            
    if cache_p:
        npz = np.load(cache_p)
        cache_dur = float(npz["duration_seconds"])
        n_windows = len(npz["raw_scores"])
        crest_db = float(npz["crest_factor_db"])
        cache_sr = int(npz["sample_rate"])
    else:
        cache_dur = 0.0
        n_windows = 0
        crest_db = 0.0
        cache_sr = 0

    # 3. Check evaluated results in Phase 41 continuous reconstruction
    recon = pd.read_csv("experiments/phase41/phase41_continuous_reconstruction.csv")
    recon_stream = recon[recon["recording_id"] == rid]
    conditions_evaluated = recon_stream["condition_id"].tolist()
    
    stream_audit.append({
        "recording_id": rid,
        "filename": row["filename"],
        "relative_path": rel_p,
        "file_exists": file_exists,
        "source_format": source_format,
        "source_subtype": source_subtype,
        "source_sr": source_sr,
        "source_channels": source_channels,
        "source_frames": source_frames,
        "source_dur_s": round(source_dur, 3),
        "inventory_dur_s": round(row["duration_seconds"], 3),
        "cache_exists": cache_p is not None,
        "cache_dur_s": round(cache_dur, 3),
        "n_windows": n_windows,
        "evaluated_in_recon": len(conditions_evaluated) == 6,
        "conditions_count": len(conditions_evaluated)
    })

df_audit = pd.DataFrame(stream_audit)
print(df_audit[["recording_id", "file_exists", "source_dur_s", "inventory_dur_s", "cache_dur_s", "n_windows", "evaluated_in_recon"]])
print("\nAny duration mismatch between physical audio and inventory?")
mismatch = df_audit[abs(df_audit["source_dur_s"] - df_audit["inventory_dur_s"]) > 0.01]
print(f"Mismatches: {len(mismatch)}")
if len(mismatch) > 0:
    print(mismatch)

print("\nSum of physical decoded source durations:", df_audit["source_dur_s"].sum())
print("Sum of inventory durations:", df_audit["inventory_dur_s"].sum())
print("Sum of cache durations:", df_audit["cache_dur_s"].sum())

