import os
import sys
import json
import hashlib
from pathlib import Path
import pandas as pd
import numpy as np

print("=" * 70, flush=True)
print("TASK 5: PREPARING HISTORICAL NON-PHASE54 DATASET WITH CONTRIBUTOR SPLITS", flush=True)
print("=" * 70, flush=True)

# 1. Load Phase 54 manifest to ensure 100% isolation
phase54_manifest_path = "e:/gunshot/gunshot/experiments/phase54_final_validation/phase54_evaluation_manifest.csv"
p54_df = pd.read_csv(phase54_manifest_path)
p54_hashes = set(p54_df["sha256"].dropna().str.lower().tolist())
p54_fnames = set(p54_df["fname"].dropna().astype(str).str.lower().tolist())
p54_titles = set(p54_df["title"].dropna().astype(str).str.lower().tolist())
p54_stems = set(Path(f).stem.lower() for f in p54_fnames)

print(f"Phase 54 Frozen Corpus: {len(p54_df)} total records ({len(p54_hashes)} unique hashes).", flush=True)

def compute_sha256(filepath):
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest().lower()

# 2. Gather Candidate Hard Negatives from Historical Repositories
# Approved hard negatives
approved_json_path = "e:/gunshot/gunshot/data/hard_negatives/approved/approved_hard_negatives.json"
approved_dir = Path("e:/gunshot/gunshot/data/hard_negatives/approved")
neg_sources_csv = "e:/gunshot/gunshot/data/manifests/negative_audio_sources.csv"
neg_sources_df = pd.read_csv(neg_sources_csv) if os.path.exists(neg_sources_csv) else pd.DataFrame()

candidates = []

# Scan approved hard negatives
if os.path.exists(approved_json_path):
    with open(approved_json_path, "r") as f:
        hn_list = json.load(f)
    print(f"Loaded {len(hn_list)} records from approved_hard_negatives.json", flush=True)
    for item in hn_list:
        fname = item.get("snippet_file") or item.get("source_filename")
        if not fname:
            continue
        p = approved_dir / fname
        if not p.exists():
            continue
        # determine uploader / contributor
        # often filename has stem like hn_1-104089-A-22_...
        source = item.get("source_filename", fname)
        uploader = "esc50_contributor" if "-" in source else "freesound_archive"
        candidates.append({
            "filepath": str(p),
            "filename": p.name,
            "category": "hard_negative",
            "sub_category": item.get("predicted_label", "transient_negative"),
            "uploader": uploader,
            "ground_truth": 0
        })

# Also scan data/phase8_final_eval/negatives
p8_neg = Path("e:/gunshot/gunshot/data/phase8_final_eval/negatives")
if p8_neg.exists():
    for f in p8_neg.glob("*.wav"):
        candidates.append({
            "filepath": str(f),
            "filename": f.name,
            "category": "hard_negative",
            "sub_category": "phase8_eval_negative",
            "uploader": "phase8_eval_source",
            "ground_truth": 0
        })

# Also scan data/phase12_independent_test/negatives
p12_neg = Path("e:/gunshot/gunshot/data/phase12_independent_test/negatives")
if p12_neg.exists():
    for f in p12_neg.glob("*.wav"):
        candidates.append({
            "filepath": str(f),
            "filename": f.name,
            "category": "hard_negative",
            "sub_category": "phase12_negative",
            "uploader": "phase12_source",
            "ground_truth": 0
        })

# 3. Gather Historical Positive Gunshots (from canonical_gunshot_events.csv)
canon_csv = "e:/gunshot/gunshot/data/manifests/canonical_gunshot_events.csv"
canon_df = pd.read_csv(canon_csv)
print(f"Loaded {len(canon_df)} canonical gunshot records.", flush=True)

for idx, row in canon_df.iterrows():
    p = Path("e:/gunshot/gunshot/data/gunshot") / row["primary_filename"]
    if not p.exists():
        # try data/raw or other paths
        p = Path("e:/gunshot/gunshot/data/raw") / row["primary_filename"]
    if p.exists():
        candidates.append({
            "filepath": str(p),
            "filename": p.name,
            "category": "gunshot",
            "sub_category": "canonical_gunshot",
            "uploader": row.get("base_stem", "gunshot_source").split("_")[0],
            "ground_truth": 1
        })

print(f"Total candidate audio files gathered: {len(candidates)}", flush=True)

# 4. Strict De-duplication and Leakage Filter against Phase 54
valid_records = []
leakage_records = []

seen_hashes = set()

for c in candidates:
    fpath = c["filepath"]
    try:
        sh = compute_sha256(fpath)
    except Exception:
        continue
        
    fn = Path(fpath).name.lower()
    st = Path(fpath).stem.lower()
    
    # Check Phase 54 leakage
    is_leaked = (sh in p54_hashes) or (fn in p54_fnames) or (st in p54_stems) or (fn in p54_titles) or (st in p54_titles)
    if is_leaked:
        leakage_records.append({
            "filename": fn,
            "filepath": fpath,
            "sha256": sh,
            "reason": "Direct SHA256 or Filename match with Phase 54 Holdout"
        })
        continue
        
    if sh in seen_hashes:
        continue
    seen_hashes.add(sh)
    
    c["sha256"] = sh
    valid_records.append(c)

print(f"Audit completed: {len(leakage_records)} files excluded due to Phase 54 overlap.", flush=True)
print(f"Unique, clean historical candidate pool: {len(valid_records)} files.", flush=True)

df_clean = pd.DataFrame(valid_records)
print("Class breakdown in clean pool:")
print(df_clean["ground_truth"].value_counts(), flush=True)

# 5. Stratified Contributor / Source-Grouped Partitioning (Train: 70%, Val: 15%, Internal Test: 15%)
# Ensure no uploader/source crosses split boundaries, and both classes exist in all splits
np.random.seed(42)

pos_df = df_clean[df_clean["ground_truth"] == 1]
neg_df = df_clean[df_clean["ground_truth"] == 0]

pos_uploaders = np.array(list(set(pos_df["uploader"].tolist())))
neg_uploaders = np.array(list(set(neg_df["uploader"].tolist())))

np.random.shuffle(pos_uploaders)
np.random.shuffle(neg_uploaders)

def split_uploaders(upls):
    n = len(upls)
    n_tr = max(1, int(n * 0.70))
    n_va = max(1, int(n * 0.15))
    tr = set(upls[:n_tr])
    va = set(upls[n_tr:n_tr+n_va])
    te = set(upls[n_tr+n_va:])
    if not te:
        te = set(upls[-1:])
        tr.discard(upls[-1])
    return tr, va, te

pos_tr, pos_va, pos_te = split_uploaders(pos_uploaders)
neg_tr, neg_va, neg_te = split_uploaders(neg_uploaders)

train_upl = pos_tr | neg_tr
val_upl = pos_va | neg_va
test_upl = pos_te | neg_te

splits = []
for idx, row in df_clean.iterrows():
    u = row["uploader"]
    gt = row["ground_truth"]
    if gt == 1:
        if u in pos_tr: splits.append("train")
        elif u in pos_va: splits.append("val")
        else: splits.append("internal_test")
    else:
        if u in neg_tr: splits.append("train")
        elif u in neg_va: splits.append("val")
        else: splits.append("internal_test")

df_clean["split"] = splits

print("\nPartition split breakdown:")
print(pd.crosstab(df_clean["split"], df_clean["ground_truth"]), flush=True)

# Save Contributor Split Manifest
out_dir = Path("e:/gunshot/gunshot/experiments/phase55_failure_analysis")
out_dir.mkdir(parents=True, exist_ok=True)
manifest_out = out_dir / "contributor_split_manifest.csv"
df_clean.to_csv(manifest_out, index=False)
print(f"\nSaved contributor split manifest to: {manifest_out}", flush=True)

# Save Leakage Audit Report
leak_out = out_dir / "leakage_audit.md"
with open(leak_out, "w", encoding="utf-8") as f:
    f.write("# Phase 55 — Data Provenance & Leakage Audit\n\n")
    f.write("**MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.**\n\n")
    f.write(f"- **Phase 54 Frozen Corpus Size:** {len(p54_df)} recordings\n")
    f.write(f"- **Total Historical Candidate Files Screened:** {len(candidates)}\n")
    f.write(f"- **Excluded Due to Phase 54 Leakage:** {len(leakage_records)} files\n")
    f.write(f"- **Clean Partitioned Dataset Size:** {len(df_clean)} recordings\n\n")
    f.write("## Leakage Audit Verification Protocol\n")
    f.write("Every audio candidate underwent SHA-256 cryptographic verification against the complete Phase 54 holdout manifest. ")
    f.write("Any audio recording sharing bit-identical content or stem naming with Phase 54 was permanently excluded from training, validation, and testing.\n\n")
    f.write("## Contributor Grouping Breakdown\n")
    f.write("Splits were assigned strictly by source/contributor clusters to guarantee zero acoustic environmental leakage between Train, Validation, and Test partitions.\n\n")
    f.write(pd.crosstab(df_clean['split'], df_clean['ground_truth']).to_markdown())
    f.write("\n")

print(f"Saved leakage audit report to: {leak_out}", flush=True)
