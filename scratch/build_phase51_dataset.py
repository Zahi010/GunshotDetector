"""
Build Independent Evaluation Dataset & Run Duplicate/Leakage Audit for Phase 51
RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.
"""

import sys
import os
import pathlib
import hashlib
import json
import soundfile as sf
import pandas as pd
import numpy as np

sys.path.insert(0, "E:/gunshot/gunshot")
os.chdir("E:/gunshot/gunshot")

out_dir = pathlib.Path("experiments/phase51_validation")
out_dir.mkdir(parents=True, exist_ok=True)

def file_sha256(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        while c := f.read(65536):
            h.update(c)
    return h.hexdigest()

def audio_sha256(p):
    try:
        y, sr = sf.read(str(p))
        if y.ndim > 1: y = np.mean(y, axis=1)
        return hashlib.sha256(y.astype(np.float32).tobytes()).hexdigest()
    except Exception as e:
        return None

print("=== STEP 1: CATALOGING ALL HISTORICAL HASHES (TRAINING & BENCHMARKS) ===")

# 1. Historical V8 Benchmark Files
v8_benchmark_hashes = {}
v8_df = pd.read_csv("experiments/detector_improvement_v8/recording_level_predictions.csv")
p12_rca = pd.read_csv("experiments/detector_improvement_v4/recording_condition_analysis.csv")
p15_manifest = pd.read_csv("reports/phase15_dataset_manifest.csv")

for _, r in p12_rca.iterrows():
    p = pathlib.Path(r["filepath"])
    if p.exists():
        v8_benchmark_hashes[file_sha256(p)] = ("phase12_holdout", r["recording_id"], str(p))
for _, r in p15_manifest.iterrows():
    p = pathlib.Path(r["filepath"])
    if p.exists():
        v8_benchmark_hashes[file_sha256(p)] = ("phase15_holdout", r["recording_id"], str(p))

p19_dir = pathlib.Path("data/phase19_independent_positive/normalized_16k")
for p in p19_dir.glob("*.wav"):
    v8_benchmark_hashes[file_sha256(p)] = ("phase19_holdout", p.stem, str(p))

p16_dir = pathlib.Path("data/phase16_natural_continuous")
for p in p16_dir.glob("*.wav"):
    v8_benchmark_hashes[file_sha256(p)] = ("phase16_continuous", p.stem, str(p))

p12_cont = pathlib.Path("data/phase12_independent_test/continuous_ambient/phase12_continuous_stream_01_urban_and_environmental_2hr.wav")
if p12_cont.exists():
    v8_benchmark_hashes[file_sha256(p12_cont)] = ("phase12_continuous", p12_cont.stem, str(p12_cont))

print(f"Total V8 Benchmark Unique Hashes Cataloged: {len(v8_benchmark_hashes)}")

# 2. Historical Training/Validation/Test Splits
train_hashes = {}
for m_name in ["train.csv", "val.csv", "test.csv"]:
    m_path = pathlib.Path(f"data/manifests/{m_name}")
    if m_path.exists():
        df_m = pd.read_csv(m_path)
        for _, r in df_m.iterrows():
            rel_p = pathlib.Path(r["relative_path"])
            if rel_p.exists():
                train_hashes[file_sha256(rel_p)] = (m_name, r.get("base_stem", rel_p.stem), str(rel_p))

print(f"Total Historical Training/Val/Test Hashes Cataloged: {len(train_hashes)}")


print("\n=== STEP 2: ASSEMBLING PHASE 51 CANDIDATE EVALUATION SET ===")

candidate_items = []
leakage_records = []

# --- A. Positive Recordings (Phase 8 + Phase 7 Non-Duplicates) ---
# Phase 8 Gunshots (43 recordings)
p8_manifest = pd.read_csv("data/manifests/phase8_final_eval_manifest.csv")
p8_pos = p8_manifest[p8_manifest["label"] == 1]
for _, r in p8_pos.iterrows():
    p = pathlib.Path(r["filepath"])
    f_hash = file_sha256(p)
    cond = r["acoustic_condition"]
    
    # Classify condition category for reporting
    if "pocket" in cond.lower():
        cond_cat = "pocket_occluded"
    elif "crack" in cond.lower() or "sharp" in cond.lower():
        cond_cat = "clean_open_air"
    elif "blast" in cond.lower() or "heavy" in cond.lower() or "high_energy" in cond.lower():
        cond_cat = "high_energy_clipped"
    else:
        cond_cat = "clean_open_air"

    if f_hash in v8_benchmark_hashes:
        leakage_records.append({
            "candidate_id": r["recording_id"], "filepath": str(p),
            "sha256": f_hash, "leakage_type": "v8_benchmark_overlap",
            "matched_source": v8_benchmark_hashes[f_hash][0]
        })
    elif f_hash in train_hashes:
        leakage_records.append({
            "candidate_id": r["recording_id"], "filepath": str(p),
            "sha256": f_hash, "leakage_type": "training_set_overlap",
            "matched_source": train_hashes[f_hash][0]
        })
    else:
        candidate_items.append({
            "recording_id": f"P51_POS_{r['recording_id']}",
            "filename": p.name,
            "filepath": str(p).replace("\\", "/"),
            "ground_truth_label": 1,
            "primary_category": "gunshot_positive",
            "sub_category": cond,
            "condition_category": cond_cat,
            "source_provenance": "Mitchell Roberts Ballistic Archive (Phase 8 Final Eval)",
            "duration_sec": round(float(r["duration_sec"]), 3),
            "sha256": f_hash,
            "is_independent": True
        })

# Phase 7 Gunshots (27 candidates, 5 duplicates to be audited and rejected)
p7_manifest = pd.read_csv("data/manifests/phase7_independent_eval_manifest.csv")
p7_pos = p7_manifest[p7_manifest["label"] == 1]
for _, r in p7_pos.iterrows():
    p = pathlib.Path(r["filepath"])
    f_hash = file_sha256(p)
    cond = r["acoustic_condition"]
    
    if "pocket" in cond.lower():
        cond_cat = "pocket_occluded"
    elif "canyon" in cond.lower() or "reverberant" in cond.lower():
        cond_cat = "reverberant_urban"
    elif "burst" in cond.lower() or "double" in cond.lower():
        cond_cat = "rapid_cadence"
    else:
        cond_cat = "clean_open_air"

    if f_hash in v8_benchmark_hashes:
        leakage_records.append({
            "candidate_id": r["recording_id"], "filepath": str(p),
            "sha256": f_hash, "leakage_type": "v8_benchmark_overlap",
            "matched_source": f"{v8_benchmark_hashes[f_hash][0]}:{v8_benchmark_hashes[f_hash][1]}"
        })
    elif f_hash in train_hashes:
        leakage_records.append({
            "candidate_id": r["recording_id"], "filepath": str(p),
            "sha256": f_hash, "leakage_type": "training_set_overlap",
            "matched_source": f"{train_hashes[f_hash][0]}:{train_hashes[f_hash][1]}"
        })
    else:
        candidate_items.append({
            "recording_id": f"P51_POS_{r['recording_id']}",
            "filename": p.name,
            "filepath": str(p).replace("\\", "/"),
            "ground_truth_label": 1,
            "primary_category": "gunshot_positive",
            "sub_category": cond,
            "condition_category": cond_cat,
            "source_provenance": f"{r['source']} (Phase 7 Independent Test)",
            "duration_sec": round(float(r["duration_sec"]), 3),
            "sha256": f_hash,
            "is_independent": True
        })

# --- B. Negative Challenge Recordings (Hard Negatives + Untouched ESC-50) ---
# 1. Dedicated Hard Negatives (108 files)
hn_root = pathlib.Path("data/background/hard_negatives")
for cat_dir in sorted(hn_root.iterdir()):
    if cat_dir.is_dir():
        cat_name = cat_dir.name
        for p in sorted(cat_dir.glob("*.wav")):
            f_hash = file_sha256(p)
            dur = sf.info(str(p)).duration
            if f_hash in v8_benchmark_hashes or f_hash in train_hashes:
                leakage_records.append({
                    "candidate_id": p.stem, "filepath": str(p),
                    "sha256": f_hash, "leakage_type": "known_overlap",
                    "matched_source": "benchmark_or_training"
                })
            else:
                candidate_items.append({
                    "recording_id": f"P51_NEG_HN_{cat_name}_{p.stem}",
                    "filename": p.name,
                    "filepath": str(p).replace("\\", "/"),
                    "ground_truth_label": 0,
                    "primary_category": cat_name,
                    "sub_category": f"hard_negative_{cat_name}",
                    "condition_category": "acoustic_impulse_challenge",
                    "source_provenance": f"Curated Hard Negative Corpus ({cat_name})",
                    "duration_sec": round(dur, 3),
                    "sha256": f_hash,
                    "is_independent": True
                })

# 2. Untouched Glass Breakage (20 files from ESC-50 Folds 1-3)
glass_p = pathlib.Path("data/raw/background/sharp_impacts")
for p in sorted(glass_p.glob("*-39.wav")):
    f_hash = file_sha256(p)
    dur = sf.info(str(p)).duration
    if f_hash in v8_benchmark_hashes or f_hash in train_hashes:
        leakage_records.append({
            "candidate_id": p.stem, "filepath": str(p),
            "sha256": f_hash, "leakage_type": "known_overlap",
            "matched_source": "benchmark_or_training"
        })
    else:
        candidate_items.append({
            "recording_id": f"P51_NEG_GLASS_{p.stem}",
            "filename": p.name,
            "filepath": str(p).replace("\\", "/"),
            "ground_truth_label": 0,
            "primary_category": "glass_shatter",
            "sub_category": "esc50_glass_breaking_untouched",
            "condition_category": "high_frequency_shatter",
            "source_provenance": "ESC-50 Class 39 (Untouched Folds 1-3)",
            "duration_sec": round(dur, 3),
            "sha256": f_hash,
            "is_independent": True
        })

# 3. Untouched ESC-50 Environmental Classes from Phase 8 (180 files)
p8_neg = p8_manifest[(p8_manifest["label"] == 0) & (~p8_manifest["category"].str.contains("crackling_fire|continuous", case=False))]
for _, r in p8_neg.iterrows():
    p = pathlib.Path(r["filepath"])
    f_hash = file_sha256(p)
    if f_hash in v8_benchmark_hashes or f_hash in train_hashes:
        leakage_records.append({
            "candidate_id": r["recording_id"], "filepath": str(p),
            "sha256": f_hash, "leakage_type": "known_overlap",
            "matched_source": "benchmark_or_training"
        })
    else:
        candidate_items.append({
            "recording_id": f"P51_NEG_ENV_{r['recording_id']}",
            "filename": p.name,
            "filepath": str(p).replace("\\", "/"),
            "ground_truth_label": 0,
            "primary_category": "urban_environmental",
            "sub_category": r["category"],
            "condition_category": "environmental_ambient",
            "source_provenance": f"ESC-50 Dataset ({r['category']})",
            "duration_sec": round(float(r["duration_sec"]), 3),
            "sha256": f_hash,
            "is_independent": True
        })

df_candidates = pd.DataFrame(candidate_items)
df_candidates.to_csv(out_dir / "phase51_evaluation_manifest.csv", index=False)

df_leakage = pd.DataFrame(leakage_records)
df_leakage.to_csv(out_dir / "duplicate_and_leakage_analysis.csv", index=False)

print(f"\nPhase 51 Manifest Created: {len(df_candidates)} discrete recordings.")
print(f"  Positives: {len(df_candidates[df_candidates['ground_truth_label'] == 1])}")
print(f"    - Pocket-occluded: {len(df_candidates[df_candidates['condition_category'] == 'pocket_occluded'])}")
print(f"    - Clean open-air: {len(df_candidates[df_candidates['condition_category'] == 'clean_open_air'])}")
print(f"    - High-energy / clipped: {len(df_candidates[df_candidates['condition_category'] == 'high_energy_clipped'])}")
print(f"    - Rapid cadence / burst: {len(df_candidates[df_candidates['condition_category'] == 'rapid_cadence'])}")
print(f"  Negatives: {len(df_candidates[df_candidates['ground_truth_label'] == 0])}")
print(f"    - Fireworks / Pyrotechnics: {len(df_candidates[df_candidates['primary_category'] == 'fireworks'])}")
print(f"    - Glass Shatter: {len(df_candidates[df_candidates['primary_category'] == 'glass_shatter'])}")
print(f"    - Metal Hammer Impacts: {len(df_candidates[df_candidates['primary_category'] == 'metal_hammer_impact'])}")
print(f"    - Door Slams: {len(df_candidates[df_candidates['primary_category'] == 'door_slam'])}")
print(f"    - Thunder / Low-Frequency: {len(df_candidates[df_candidates['primary_category'] == 'thunder_rumble'])}")
print(f"    - Vehicle Backfires: {len(df_candidates[df_candidates['primary_category'] == 'vehicle_backfire'])}")
print(f"    - Impulsive Transients (Toy gun, Balloon, Percussion, Laser): {len(df_candidates[df_candidates['primary_category'].isin(['toy_gun_pop', 'balloon_burst', 'percussion_transient', 'laser_contact_mic'])])}")
print(f"    - Urban Environmental (ESC-50 9 Untouched Classes): {len(df_candidates[df_candidates['primary_category'] == 'urban_environmental'])}")

print(f"\nDuplicates / Leakage Detected & Excluded: {len(df_leakage)} files.")
for l_type, grp in df_leakage.groupby("leakage_type"):
    print(f"  - {l_type}: {len(grp)} files")
    for _, r in grp.iterrows():
        print(f"      {r['candidate_id']} -> {r['matched_source']}")

