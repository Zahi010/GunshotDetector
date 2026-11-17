import pandas as pd
import json
import pathlib
import shutil
import hashlib
import soundfile as sf

REPO = pathlib.Path("E:/gunshot/gunshot")
P39 = REPO / "experiments" / "phase39"
dest_dir = P39 / "dataset" / "distractor"
dest_dir.mkdir(parents=True, exist_ok=True)

# Load FSD50K dev ground truth and metadata
meta_path = pathlib.Path("E:/FSD50K.dev_audio/FSD50K.metadata/dev_clips_info_FSD50K.json")
with open(meta_path, "r", encoding="utf-8") as f:
    dev_info = json.load(f)

dev_df = pd.read_csv("E:/FSD50K.dev_audio/FSD50K.ground_truth/dev.csv")
audio_dir = pathlib.Path("E:/FSD50K.dev_audio/FSD50K.dev_audio")

# Define target classes and counts
# Target: 100 Fireworks + 20 of each of 6 challenge classes = 220 total distinct clips
categories = [
    ("DISTRACTOR_FIREWORKS", "Fireworks", 100),
    ("DISTRACTOR_SLAM_DOOR", "Door", 20),
    ("DISTRACTOR_THUNDER", "Thunder", 20),
    ("DISTRACTOR_GLASS", "Glass", 20),
    ("DISTRACTOR_VEHICLE_ENGINE", "Motor_vehicle", 20),
    ("DISTRACTOR_SCREAMING", "Screaming", 20),
    ("DISTRACTOR_TOOLS_IMPACT", "Hammer", 20)
]

selected_distractors = []
seen_fnames = set()

for cat_name, label_keyword, target_n in categories:
    sub = dev_df[
        dev_df["labels"].str.contains(label_keyword, na=False) &
        ~dev_df["labels"].str.contains("Gunshot", na=False)
    ].copy()
    
    # Group by uploader to maximize session diversity
    uploader_groups = {}
    for _, row in sub.iterrows():
        fn = str(row["fname"])
        if fn in seen_fnames:
            continue
        p = audio_dir / f"{fn}.wav"
        if not p.exists():
            continue
        info = dev_info.get(fn, {})
        up = info.get("uploader", "unknown")
        if up not in uploader_groups:
            uploader_groups[up] = []
        uploader_groups[up].append({
            "fname": fn,
            "path": p,
            "info": info,
            "labels": row["labels"]
        })
    
    cat_selected = []
    # Round-robin selection across uploaders
    while len(cat_selected) < target_n:
        added_in_round = 0
        for up, clips in uploader_groups.items():
            if len(cat_selected) >= target_n:
                break
            taken_from_up = [c for c in cat_selected if c["uploader"] == up]
            if len(taken_from_up) < 2 and len(clips) > len(taken_from_up):
                cand = clips[len(taken_from_up)]
                cat_selected.append({
                    "category": cat_name,
                    "fname": cand["fname"],
                    "path": cand["path"],
                    "uploader": up,
                    "info": cand["info"],
                    "labels": cand["labels"]
                })
                seen_fnames.add(cand["fname"])
                added_in_round += 1
        if added_in_round == 0:
            # If uploaders exhausted, pick remaining available
            for up, clips in uploader_groups.items():
                for cand in clips:
                    if len(cat_selected) >= target_n:
                        break
                    if cand["fname"] not in seen_fnames:
                        cat_selected.append({
                            "category": cat_name,
                            "fname": cand["fname"],
                            "path": cand["path"],
                            "uploader": up,
                            "info": cand["info"],
                            "labels": cand["labels"]
                        })
                        seen_fnames.add(cand["fname"])
            break
            
    selected_distractors.extend(cat_selected)
    print(f"Selected {len(cat_selected)} clips for {cat_name} (target {target_n})")

print(f"\nTotal selected distractor clips: {len(selected_distractors)}")

# Copy and catalog
distractor_catalog = []
for c in selected_distractors:
    orig_name = f"{c['fname']}.wav"
    dest_path = dest_dir / orig_name
    if not dest_path.exists():
        shutil.copy2(c["path"], dest_path)
        
    data = dest_path.read_bytes()
    sha = hashlib.sha256(data).hexdigest()
    info = sf.info(str(dest_path))
    
    meta = c["info"]
    lic = meta.get("license", "http://creativecommons.org/licenses/by/3.0/")
    
    distractor_catalog.append({
        "recording_id": f"p39_dist_{c['category']}_{c['fname']}",
        "filename": orig_name,
        "relative_path": str(dest_path.relative_to(REPO)).replace("\\", "/"),
        "partition": "PARTITION_PROSPECTIVE_DISTRACTOR",
        "category": c["category"],
        "source_dataset": "FSD50K_dev",
        "campaign_or_session": f"fsd50k_session_{c['uploader']}",
        "uploader_or_creator": c["uploader"],
        "title": meta.get("title", ""),
        "fsd50k_labels": c["labels"],
        "license": lic,
        "duration_seconds": round(info.duration, 4),
        "sample_rate_hz": info.samplerate,
        "channels": info.channels,
        "sha256": sha
    })

cat_df = pd.DataFrame(distractor_catalog)
out_csv = P39 / "dataset" / "phase39_distractor_registry.csv"
cat_df.to_csv(out_csv, index=False)
cat_df.to_csv(P39 / "phase39_distractor_registry.csv", index=False)
print(f"Saved {out_csv} ({len(cat_df)} rows)")

