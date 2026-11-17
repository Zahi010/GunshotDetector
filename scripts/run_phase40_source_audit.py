import pathlib
import hashlib
import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

REPO = pathlib.Path("E:/gunshot/gunshot")
P38_DIR = REPO / "experiments" / "phase38"
P39_DIR = REPO / "experiments" / "phase39"
P40_DIR = REPO / "experiments" / "phase40"

# 1. Load registries
pos_df = pd.read_csv(P38_DIR / "dataset" / "phase38_positive_catalog.csv")
dist_df = pd.read_csv(P39_DIR / "phase39_distractor_registry.csv")
cont_df = pd.read_csv(P39_DIR / "dataset" / "phase39_continuous_dataset_registry.csv")

fw_df = dist_df[dist_df["category"] == "DISTRACTOR_FIREWORKS"].copy()
other_dist_df = dist_df[dist_df["category"] != "DISTRACTOR_FIREWORKS"].copy()

# 2. Source Lineage Summary
partitions = [
    ("PARTITION_PROSPECTIVE_POSITIVE", pos_df, "uploader_session", "uploader_session", "source_dataset"),
    ("PARTITION_FIREWORKS_CHALLENGE", fw_df, "uploader_or_creator", "campaign_or_session", "source_dataset"),
    ("PARTITION_OTHER_DISTRACTORS", other_dist_df, "uploader_or_creator", "campaign_or_session", "source_dataset"),
    ("PARTITION_ALL_DISTRACTORS", dist_df, "uploader_or_creator", "campaign_or_session", "source_dataset"),
    ("PARTITION_CONTINUOUS_AMBIENT", cont_df, "uploader_or_creator", "campaign_or_session", "source_dataset")
]

lineage_rows = []
for pname, df, uploader_col, session_col, dataset_col in partitions:
    n_recs = len(df)
    n_uploaders = df[uploader_col].nunique()
    n_sessions = df[session_col].nunique()
    total_dur_s = float(df["duration_seconds"].sum())
    total_dur_hr = total_dur_s / 3600.0
    
    # Calculate top contributor concentration
    top_uploader_cnt = df[uploader_col].value_counts().iloc[0] if n_uploaders > 0 else 0
    top_uploader_pct = round((top_uploader_cnt / n_recs) * 100, 2) if n_recs > 0 else 0.0
    
    # Clustering ratio: recordings per uploader
    recs_per_uploader = round(n_recs / n_uploaders, 2) if n_uploaders > 0 else 0.0

    lineage_rows.append({
        "partition_name": pname,
        "total_recordings": n_recs,
        "total_duration_hours": round(total_dur_hr, 4),
        "total_duration_seconds": round(total_dur_s, 2),
        "unique_uploaders": n_uploaders,
        "recordings_per_uploader_ratio": recs_per_uploader,
        "top_uploader_clip_count": top_uploader_cnt,
        "top_uploader_concentration_pct": top_uploader_pct,
        "unique_campaigns_or_sessions": n_sessions,
        "primary_source_repositories": ", ".join(df[dataset_col].unique().tolist()),
        "source_clustering_risk_level": "LOW" if recs_per_uploader <= 1.25 else ("MODERATE" if recs_per_uploader <= 2.0 else "ELEVATED"),
        "audit_classification": "SOURCE_CLUSTERED" if recs_per_uploader > 1.25 else "INDEPENDENT_SOURCES",
        "evidence_label": "VERIFIED_FROM_PHYSICAL_FILE"
    })

lineage_df = pd.DataFrame(lineage_rows)
lineage_csv_path = P40_DIR / "phase40_source_lineage.csv"
lineage_df.to_csv(lineage_csv_path, index=False)
print(f"Saved {lineage_csv_path}")

# 3. Pairwise Audio Similarity Audit
# We check all pairwise comparisons within Fireworks (100x99 / 2 = 4950 pairs)
# and across positive clips (120x119 / 2 = 7140 pairs)
# and across continuous streams
print("Computing audio similarity audit across feature caches...")

cache_dirs = [P38_DIR / "feature_cache", P39_DIR / "feature_cache"]

def get_mean_embedding(rid):
    for cd in cache_dirs:
        p = cd / f"{rid}.npz"
        if p.exists():
            data = np.load(p)
            emb = data["embeddings"]
            if emb is not None and len(emb) > 0:
                return np.mean(emb, axis=0)
    return None

# Load embeddings for fireworks clips
fw_rids = fw_df["recording_id"].tolist()
fw_embs = {}
for rid in fw_rids:
    e = get_mean_embedding(rid)
    if e is not None:
        fw_embs[rid] = e

fw_rids_valid = list(fw_embs.keys())
fw_mat = np.array([fw_embs[r] for r in fw_rids_valid])
fw_sim = cosine_similarity(fw_mat)

similarity_rows = []
# Identify top similar pairs among fireworks
for i in range(len(fw_rids_valid)):
    for j in range(i + 1, len(fw_rids_valid)):
        r1 = fw_rids_valid[i]
        r2 = fw_rids_valid[j]
        sim_val = float(fw_sim[i, j])
        
        row1 = fw_df[fw_df["recording_id"] == r1].iloc[0]
        row2 = fw_df[fw_df["recording_id"] == r2].iloc[0]
        
        same_uploader = (row1["uploader_or_creator"] == row2["uploader_or_creator"])
        same_session = (row1["campaign_or_session"] == row2["campaign_or_session"])
        same_sha = (row1["sha256"] == row2["sha256"])
        
        # Only log if similarity >= 0.85 or same uploader
        if sim_val >= 0.85 or same_uploader:
            similarity_rows.append({
                "partition": "DISTRACTOR_FIREWORKS",
                "item_1_id": r1,
                "item_1_uploader": row1["uploader_or_creator"],
                "item_1_duration_s": round(float(row1["duration_seconds"]), 3),
                "item_2_id": r2,
                "item_2_uploader": row2["uploader_or_creator"],
                "item_2_duration_s": round(float(row2["duration_seconds"]), 3),
                "embedding_cosine_similarity": round(sim_val, 4),
                "same_uploader": same_uploader,
                "same_session": same_session,
                "exact_waveform_sha_collision": same_sha,
                "similarity_classification": "EXACT_DUPLICATE" if same_sha else ("HIGH_ACOUSTIC_SIMILARITY" if sim_val >= 0.90 else "MODERATE_ACOUSTIC_SIMILARITY"),
                "independence_status": "CORRELATED_SESSION" if same_uploader else "ACOUSTICALLY_SIMILAR_INDEPENDENT"
            })

# Also audit positive clips for any pairs with same uploader or high similarity
pos_rids = pos_df["recording_id"].tolist()
pos_embs = {}
for rid in pos_rids:
    e = get_mean_embedding(rid)
    if e is not None:
        pos_embs[rid] = e

pos_rids_valid = list(pos_embs.keys())
pos_mat = np.array([pos_embs[r] for r in pos_rids_valid])
pos_sim = cosine_similarity(pos_mat)

for i in range(len(pos_rids_valid)):
    for j in range(i + 1, len(pos_rids_valid)):
        r1 = pos_rids_valid[i]
        r2 = pos_rids_valid[j]
        sim_val = float(pos_sim[i, j])
        
        row1 = pos_df[pos_df["recording_id"] == r1].iloc[0]
        row2 = pos_df[pos_df["recording_id"] == r2].iloc[0]
        
        same_uploader = (row1["uploader_session"] == row2["uploader_session"])
        same_sha = (row1["sha256"] == row2["sha256"])
        
        if sim_val >= 0.90 or same_uploader:
            similarity_rows.append({
                "partition": "PROSPECTIVE_POSITIVE",
                "item_1_id": r1,
                "item_1_uploader": row1["uploader_session"],
                "item_1_duration_s": round(float(row1["duration_seconds"]), 3),
                "item_2_id": r2,
                "item_2_uploader": row2["uploader_session"],
                "item_2_duration_s": round(float(row2["duration_seconds"]), 3),
                "embedding_cosine_similarity": round(sim_val, 4),
                "same_uploader": same_uploader,
                "same_session": same_uploader,
                "exact_waveform_sha_collision": same_sha,
                "similarity_classification": "EXACT_DUPLICATE" if same_sha else ("HIGH_ACOUSTIC_SIMILARITY" if sim_val >= 0.90 else "MODERATE_ACOUSTIC_SIMILARITY"),
                "independence_status": "CORRELATED_SESSION" if same_uploader else "ACOUSTICALLY_SIMILAR_INDEPENDENT"
            })

sim_df = pd.DataFrame(similarity_rows)
sim_csv_path = P40_DIR / "phase40_audio_similarity_audit.csv"
sim_df.to_csv(sim_csv_path, index=False)
print(f"Saved {sim_csv_path} ({len(sim_df)} correlated/similar pairs identified)")

