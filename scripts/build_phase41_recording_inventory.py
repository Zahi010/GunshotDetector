import hashlib
import pathlib
import soundfile as sf
import pandas as pd

REPO = pathlib.Path("E:/gunshot/gunshot")
P38_DIR = REPO / "experiments" / "phase38"
P39_DIR = REPO / "experiments" / "phase39"
P40_DIR = REPO / "experiments" / "phase40"
P41_DIR = REPO / "experiments" / "phase41"

# 1. Load registries
pos_df = pd.read_csv(P38_DIR / "dataset" / "phase38_positive_catalog.csv")
dist_df = pd.read_csv(P39_DIR / "phase39_distractor_registry.csv")
cont_df = pd.read_csv(P40_DIR / "dataset" / "phase40_continuous_dataset_registry.csv")

inventory_rows = []

# Process Positives (120 rows)
pos_dir = P38_DIR / "dataset" / "positive"
for _, r in pos_df.iterrows():
    rid = r["recording_id"]
    fn = r["filename"]
    p = pos_dir / fn
    assert p.exists(), f"Missing positive file: {p}"
    
    data = p.read_bytes()
    sha = hashlib.sha256(data).hexdigest()
    sz = len(data)
    info = sf.info(str(p))
    
    inventory_rows.append({
        "recording_id": rid,
        "filename": fn,
        "relative_path": f"experiments/phase38/dataset/positive/{fn}",
        "evaluation_partition": "POSITIVE_GUNSHOT",
        "evaluation_role": "PROSPECTIVE_POSITIVE_EVALUATION",
        "sub_category": r["annotated_event_type"],
        "is_fireworks_eval": False,
        "is_distractor_eval": False,
        "is_continuous_eval": False,
        "source_dataset": r["source_dataset"],
        "uploader_or_recordist": r["uploader_session"],
        "session_or_location": r["uploader_session"],
        "campaign_id": "FSD50K_GUNSHOT_DEV",
        "license": r["license"],
        "duration_seconds": round(float(info.duration), 4),
        "sample_rate_hz": int(info.samplerate),
        "channel_count": int(info.channels),
        "format": info.format,
        "subtype_codec": info.subtype,
        "file_size_bytes": sz,
        "sha256": sha
    })

# Process Distractors (220 rows)
# Look in phase39/dataset/distractor or phase38/dataset/distractors
dist_dirs = [P39_DIR / "dataset" / "distractor", P38_DIR / "dataset" / "distractors"]
for _, r in dist_df.iterrows():
    rid = r["recording_id"]
    fn = r["filename"]
    p = None
    for dd in dist_dirs:
        cand = dd / fn
        if cand.exists():
            p = cand
            break
    assert p is not None and p.exists(), f"Missing distractor file: {fn}"
    
    data = p.read_bytes()
    sha = hashlib.sha256(data).hexdigest()
    sz = len(data)
    info = sf.info(str(p))
    
    is_fw = (r["category"] == "DISTRACTOR_FIREWORKS")

    inventory_rows.append({
        "recording_id": rid,
        "filename": fn,
        "relative_path": p.relative_to(REPO).as_posix(),
        "evaluation_partition": "DISTRACTOR_NOISE",
        "evaluation_role": "FIREWORKS_CHALLENGE_AND_DISTRACTOR" if is_fw else "GENERAL_DISTRACTOR_EVALUATION",
        "sub_category": r["category"],
        "is_fireworks_eval": is_fw,
        "is_distractor_eval": True,
        "is_continuous_eval": False,
        "source_dataset": r["source_dataset"],
        "uploader_or_recordist": r["uploader_or_creator"],
        "session_or_location": r["campaign_or_session"],
        "campaign_id": r["campaign_or_session"],
        "license": r["license"],
        "duration_seconds": round(float(info.duration), 4),
        "sample_rate_hz": int(info.samplerate),
        "channel_count": int(info.channels),
        "format": info.format,
        "subtype_codec": info.subtype,
        "file_size_bytes": sz,
        "sha256": sha
    })

# Process Continuous (28 rows)
for _, r in cont_df.iterrows():
    rid = r["recording_id"]
    fn = r["filename"]
    rel_p = r["relative_path"]
    p = REPO / rel_p
    assert p.exists(), f"Missing continuous file: {p}"
    
    data = p.read_bytes()
    sha = hashlib.sha256(data).hexdigest()
    sz = len(data)
    info = sf.info(str(p))

    inventory_rows.append({
        "recording_id": rid,
        "filename": fn,
        "relative_path": rel_p,
        "evaluation_partition": "CONTINUOUS_AMBIENT",
        "evaluation_role": "CONTINUOUS_FALSE_ALARM_BENCHMARK",
        "sub_category": "LONG_AMBIENT_STREAM",
        "is_fireworks_eval": False,
        "is_distractor_eval": False,
        "is_continuous_eval": True,
        "source_dataset": r["source_dataset"],
        "uploader_or_recordist": r["uploader_or_creator"],
        "session_or_location": r.get("location_metadata", r["campaign_or_session"]),
        "campaign_id": r["campaign_or_session"],
        "license": r["license"],
        "duration_seconds": round(float(info.duration), 4),
        "sample_rate_hz": int(info.samplerate),
        "channel_count": int(info.channels),
        "format": info.format,
        "subtype_codec": info.subtype,
        "file_size_bytes": sz,
        "sha256": sha
    })

inv_df = pd.DataFrame(inventory_rows)
out_csv = P41_DIR / "phase41_recording_inventory.csv"
inv_df.to_csv(out_csv, index=False)
print(f"Saved recording inventory: {out_csv} ({len(inv_df)} rows)")

# Arithmetic Reconciliation Summary
n_pos = len(inv_df[inv_df["evaluation_partition"] == "POSITIVE_GUNSHOT"])
n_dist = len(inv_df[inv_df["evaluation_partition"] == "DISTRACTOR_NOISE"])
n_fw = len(inv_df[inv_df["is_fireworks_eval"] == True])
n_other_dist = n_dist - n_fw
n_cont = len(inv_df[inv_df["evaluation_partition"] == "CONTINUOUS_AMBIENT"])

n_total_entries = len(inv_df)
n_unique_sha = inv_df["sha256"].nunique()

print(f"\nInventory Reconciliation Breakdown:")
print(f"  Positive gunshot clips: {n_pos}")
print(f"  Distractor noise clips: {n_dist}")
print(f"    - Fireworks challenge clips: {n_fw}")
print(f"    - Other distractor noise clips: {n_other_dist}")
print(f"  Continuous ambient streams: {n_cont}")
print(f"  Total evaluation entries: {n_total_entries}")
print(f"  Total unique physical waveforms (SHA-256): {n_unique_sha}")
print(f"  Duplicate physical files: {n_total_entries - n_unique_sha} (within positive gunshot: fsd50k_gun_51749 and fsd50k_gun_115295)")

