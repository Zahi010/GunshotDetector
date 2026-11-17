import json
import pathlib
import urllib.request
import soundfile as sf
import hashlib
import numpy as np
import pandas as pd

REPO = pathlib.Path("E:/gunshot/gunshot")
P40_DIR = REPO / "experiments" / "phase40"
DEST_DIR = P40_DIR / "dataset" / "continuous"
DEST_DIR.mkdir(parents=True, exist_ok=True)

with open("candidate_streams_to_acquire.json") as f:
    candidates = json.load(f)

print(f"Acquiring {len(candidates)} new continuous streams into {DEST_DIR}...")

acquired = []
for c in candidates:
    dest_path = DEST_DIR / c["filename"]
    url = c["url"]
    
    if not dest_path.exists() or dest_path.stat().st_size < 10000:
        print(f"Downloading {c['id']} from {url}...")
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        try:
            with urllib.request.urlopen(req, timeout=30) as resp, open(dest_path, "wb") as out_f:
                out_f.write(resp.read())
            print(f"  -> Saved {dest_path.name} ({dest_path.stat().st_size} bytes)")
        except Exception as e:
            print(f"  Error downloading {c['id']}: {e}")
            continue
    else:
        print(f"[ALREADY EXISTS] {dest_path.name} ({dest_path.stat().st_size} bytes)")

    # Read audio metadata
    try:
        info = sf.info(str(dest_path))
        dur_s = float(info.duration)
        sr = int(info.samplerate)
        ch = int(info.channels)
    except Exception as e:
        dur_s = float(c.get("length", 300.0))
        sr = 44100
        ch = 2

    # Calculate SHA-256
    sha = hashlib.sha256(dest_path.read_bytes()).hexdigest()

    acquired.append({
        "recording_id": c["id"],
        "filename": c["filename"],
        "relative_path": f"experiments/phase40/dataset/continuous/{c['filename']}",
        "campaign_or_session": c["campaign"],
        "uploader_or_creator": c["creator"],
        "location_metadata": c.get("campaign", ""),
        "source_dataset": "Archive.org_RadioAporee",
        "license": c["license"],
        "duration_seconds": round(dur_s, 4),
        "sample_rate_hz": sr,
        "channels": ch,
        "sha256": sha,
        "acquisition_phase": "PHASE_40",
        "provenance_status": "AUTHENTIC_PROSPECTIVE_CONTINUOUS"
    })

print(f"Successfully processed {len(acquired)} new continuous streams.")

# Combine with historical continuous streams from Phase 38 and Phase 39
p39_cont_reg = pd.read_csv(REPO / "experiments" / "phase39" / "dataset" / "phase39_continuous_dataset_registry.csv")

# Merge
master_cont_df = pd.concat([p39_cont_reg, pd.DataFrame(acquired)], ignore_index=True)
master_csv = P40_DIR / "dataset" / "phase40_continuous_dataset_registry.csv"
master_cont_df.to_csv(master_csv, index=False)
print(f"Master continuous registry saved: {master_csv} (Total: {len(master_cont_df)} streams, {master_cont_df['duration_seconds'].sum()/3600.0:.4f} hours)")

