"""
Benchmark Script for Detector Improvement V2 vs V1, Phase 36, and Phase 14.
Generates:
1. development_results.csv
2. holdout_results.csv
3. recording_level_predictions.csv
MANDATORY SAFETY DESIGNATION:
RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY
"""

import os
import sys
import json
import time
import pathlib
import numpy as np
import pandas as pd

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from experiments.detector_improvement_v2.model_detector_improvement_v2 import (
    CalibratedAcousticSuppressionV2,
    EventStateMachineV2
)
from experiments.detector_improvement_v1.model_detector_improvement_v1 import (
    CalibratedAcousticSuppressionV1
)
from experiments.phase36.event_state_machine import EventStateMachine, EventState

OUTPUT_DIR = pathlib.Path(__file__).resolve().parent
p38_cache = REPO_ROOT / "experiments" / "phase38" / "feature_cache"
p39_cache = REPO_ROOT / "experiments" / "phase39" / "feature_cache"
p40_cache = REPO_ROOT / "experiments" / "phase40" / "feature_cache"

inv = pd.read_csv(REPO_ROOT / "experiments" / "phase41" / "phase41_recording_inventory.csv")
v1_preds = pd.read_csv(REPO_ROOT / "experiments" / "detector_improvement_v1" / "recording_level_predictions.csv")
partitions = pd.read_csv(REPO_ROOT / "scratch" / "v2_partitions.csv")

with open(OUTPUT_DIR / "config_improvement_v2.json", "r", encoding="utf-8") as f:
    config_v2 = json.load(f)


def load_feature_dict(recording_id: str):
    for p in [p40_cache, p39_cache, p38_cache]:
        fpath = p / f"{recording_id}.npz"
        if fpath.exists():
            npz = np.load(fpath)
            return {
                "embeddings": npz["embeddings"],
                "yamnet_scores": npz["yamnet_scores"],
                "raw_scores": npz["raw_scores"],
                "crest_factor_db": float(npz["crest_factor_db"]),
                "duration_seconds": float(npz["duration_seconds"]),
                "sample_rate": int(npz["sample_rate"])
            }
    raise FileNotFoundError(f"Features for {recording_id} not found in caches.")


def evaluate_v2_on_features(feats, profile="balanced"):
    cfg = config_v2["profiles"][profile]
    supp_engine = CalibratedAcousticSuppressionV2(cfg["suppression"])

    raw_scores = feats["raw_scores"]
    yamnet_scores = feats["yamnet_scores"]
    crest_db = feats["crest_factor_db"]
    dur_sec = feats["duration_seconds"]
    n_windows = len(raw_scores)

    if n_windows == 0:
        return [], 0.0, None

    fsm = EventStateMachineV2(
        threshold_base=cfg["threshold_base"],
        threshold_high=cfg["threshold_high"],
        threshold_off=cfg["threshold_off"],
        confirm_windows=cfg["confirm_windows"],
        cooldown_secs=cfg["cooldown_secs"],
        max_hop_gap_s=cfg["max_hop_gap_s"],
        min_crest_factor_db=cfg["min_crest_factor_db"],
        single_win_min_crest_db=cfg["single_win_min_crest_db"],
        allow_short_clip_exception=cfg["allow_short_clip_exception"],
        allow_single_impulse_exception=cfg.get("allow_single_impulse_exception", True),
        single_impulse_min_score=cfg.get("single_impulse_min_score", 0.82),
        single_impulse_min_crest_db=cfg.get("single_impulse_min_crest_db", 14.0),
        single_impulse_max_dur_sec=cfg.get("single_impulse_max_dur_sec", 5.0)
    )

    hop_sec = 0.48
    win_sec = 0.96
    adj_scores = []
    supp_categories = []

    for i in range(n_windows):
        st = round(i * hop_sec, 3)
        et = min(round(dur_sec, 3), round(st + win_sec, 3))
        raw_s = float(raw_scores[i])
        ym_s = yamnet_scores[i] if (yamnet_scores is not None and i < len(yamnet_scores)) else None

        is_in_conf = (fsm.state == EventState.CONFIRMED)
        supp_res = supp_engine.apply_suppression(
            raw_score=raw_s,
            yamnet_scores=ym_s,
            is_in_confirmed_event=is_in_conf
        )

        adj_scores.append(supp_res["adjusted_score"])
        if supp_res["suppression_active"]:
            supp_categories.append(supp_res["suppression_category"])

        win_rec = {
            "window_index": i,
            "start_time": st,
            "end_time": et,
            "raw_score": raw_s,
            "score": supp_res["adjusted_score"],
            "crest_factor_db": crest_db,
            "suppression_active": supp_res["suppression_active"],
            "suppression_category": supp_res["suppression_category"],
            "suppression_strength": supp_res["suppression_strength"],
            "suppression_reason": supp_res["suppression_reason"]
        }
        fsm.process_window(
            win_rec,
            crest_factor_db=crest_db,
            audio_duration_sec=dur_sec,
            total_windows_in_stream=n_windows
        )

    fsm.flush()
    peak_score = float(np.max(adj_scores)) if adj_scores else 0.0
    primary_supp = supp_categories[0] if supp_categories else None
    return fsm.events_emitted, peak_score, primary_supp


def main():
    print(f"[Benchmark V2] Evaluating {len(inv)} recordings across all partitions...")
    
    # Merge inventory with partitions and previous predictions
    df_all = pd.merge(inv, partitions[['recording_id', 'v2_partition']], on='recording_id', how='left')
    df_all = pd.merge(df_all, v1_preds[[
        'recording_id', 'p14_detected', 'p14_event_count', 'p14_peak_score',
        'p36_detected', 'p36_event_count', 'p36_peak_score',
        'v1_detected', 'v1_event_count', 'v1_peak_score', 'v1_dispatch_path'
    ]], on='recording_id', how='left')

    v2_records = []
    t0 = time.time()

    for idx, row in df_all.iterrows():
        rec_id = row["recording_id"]
        feats = load_feature_dict(rec_id)
        events, peak_sc, supp_cat = evaluate_v2_on_features(feats, profile="balanced")

        v2_det = 1 if len(events) > 0 else 0
        v2_cnt = len(events)
        first_disp = events[0]["dispatch_path"] if events else "none"

        v2_records.append({
            "recording_id": rec_id,
            "v2_partition": row["v2_partition"],
            "evaluation_partition": row["evaluation_partition"],
            "evaluation_role": row["evaluation_role"],
            "sub_category": row["sub_category"],
            "ground_truth_gunshot": 1 if row["evaluation_role"] == "PROSPECTIVE_POSITIVE_EVALUATION" else 0,
            "duration_sec": round(feats["duration_seconds"], 3),
            "crest_factor_db": round(feats["crest_factor_db"], 2),
            "p14_detected": row["p14_detected"],
            "p14_event_count": row["p14_event_count"],
            "p14_peak_score": row["p14_peak_score"],
            "p36_detected": row["p36_detected"],
            "p36_event_count": row["p36_event_count"],
            "p36_peak_score": row["p36_peak_score"],
            "v1_detected": row["v1_detected"],
            "v1_event_count": row["v1_event_count"],
            "v1_peak_score": row["v1_peak_score"],
            "v1_dispatch_path": row["v1_dispatch_path"],
            "v2_detected": v2_det,
            "v2_event_count": v2_cnt,
            "v2_peak_score": round(peak_sc, 4),
            "v2_dispatch_path": first_disp,
            "v2_suppression_category": supp_cat if supp_cat else "none"
        })

    elapsed = time.time() - t0
    print(f"[Benchmark V2] Completed evaluation of {len(v2_records)} recordings in {elapsed:.2f}s.")

    pred_df = pd.DataFrame(v2_records)
    pred_path = OUTPUT_DIR / "recording_level_predictions.csv"
    pred_df.to_csv(pred_path, index=False)
    print(f"[Saved] {pred_path}")

    # Generate development_results.csv
    dev_df = pred_df[pred_df["v2_partition"] == "development"]
    dev_summary = generate_summary_table(dev_df, "DEVELOPMENT SET")
    dev_path = OUTPUT_DIR / "development_results.csv"
    dev_summary.to_csv(dev_path, index=False)
    print(f"[Saved] {dev_path}")

    # Generate holdout_results.csv
    holdout_df = pred_df[pred_df["v2_partition"] == "locked_holdout"]
    holdout_summary = generate_summary_table(holdout_df, "LOCKED HOLDOUT SET")
    holdout_path = OUTPUT_DIR / "holdout_results.csv"
    holdout_summary.to_csv(holdout_path, index=False)
    print(f"[Saved] {holdout_path}")

    # Print summary tables to terminal
    print("\n" + "="*80)
    print("DEVELOPMENT RESULTS SUMMARY:")
    print("="*80)
    print(dev_summary.to_string())

    print("\n" + "="*80)
    print("LOCKED HOLDOUT RESULTS SUMMARY:")
    print("="*80)
    print(holdout_summary.to_string())


def generate_summary_table(df_subset, partition_label):
    rows = []
    subcats = sorted(df_subset["sub_category"].unique())

    for sc in subcats:
        sub = df_subset[df_subset["sub_category"] == sc]
        n_recs = len(sub)
        total_dur_h = sub["duration_sec"].sum() / 3600.0
        gt = sub["ground_truth_gunshot"].iloc[0]

        p14_det = int(sub["p14_detected"].sum())
        p14_evs = int(sub["p14_event_count"].sum())
        p36_det = int(sub["p36_detected"].sum())
        p36_evs = int(sub["p36_event_count"].sum())
        v1_det = int(sub["v1_detected"].sum())
        v1_evs = int(sub["v1_event_count"].sum())
        v2_det = int(sub["v2_detected"].sum())
        v2_evs = int(sub["v2_event_count"].sum())

        rows.append({
            "partition": partition_label,
            "sub_category": sc,
            "ground_truth": gt,
            "recording_count": n_recs,
            "duration_hours": round(total_dur_h, 4),
            "p14_detected_recs": p14_det,
            "p14_total_events": p14_evs,
            "p36_detected_recs": p36_det,
            "p36_total_events": p36_evs,
            "v1_detected_recs": v1_det,
            "v1_total_events": v1_evs,
            "v2_detected_recs": v2_det,
            "v2_total_events": v2_evs,
            "v2_vs_v1_rec_diff": v2_det - v1_det,
            "v2_vs_v1_ev_diff": v2_evs - v1_evs
        })

    # Add Macro Totals: Positives, Fireworks, Environmental, Continuous
    for grp_name, mask in [
        ("TOTAL_POSITIVE_GUNSHOTS", df_subset["ground_truth_gunshot"] == 1),
        ("TOTAL_FIREWORKS_DISTRACTORS", df_subset["sub_category"] == "DISTRACTOR_FIREWORKS"),
        ("TOTAL_ENVIRONMENTAL_DISTRACTORS", df_subset["sub_category"].str.startswith("DISTRACTOR_") & (df_subset["sub_category"] != "DISTRACTOR_FIREWORKS")),
        ("TOTAL_CONTINUOUS_BENCHMARK", df_subset["sub_category"] == "LONG_AMBIENT_STREAM"),
        ("ALL_RECORDINGS_COMBINED", pd.Series(True, index=df_subset.index))
    ]:
        sub = df_subset[mask]
        if len(sub) == 0:
            continue
        rows.append({
            "partition": partition_label,
            "sub_category": f"== {grp_name} ==",
            "ground_truth": -1 if "COMBINED" in grp_name else (1 if "POSITIVE" in grp_name else 0),
            "recording_count": len(sub),
            "duration_hours": round(sub["duration_sec"].sum() / 3600.0, 4),
            "p14_detected_recs": int(sub["p14_detected"].sum()),
            "p14_total_events": int(sub["p14_event_count"].sum()),
            "p36_detected_recs": int(sub["p36_detected"].sum()),
            "p36_total_events": int(sub["p36_event_count"].sum()),
            "v1_detected_recs": int(sub["v1_detected"].sum()),
            "v1_total_events": int(sub["v1_event_count"].sum()),
            "v2_detected_recs": int(sub["v2_detected"].sum()),
            "v2_total_events": int(sub["v2_event_count"].sum()),
            "v2_vs_v1_rec_diff": int(sub["v2_detected"].sum() - sub["v1_detected"].sum()),
            "v2_vs_v1_ev_diff": int(sub["v2_event_count"].sum() - sub["v1_event_count"].sum())
        })

    return pd.DataFrame(rows)


if __name__ == "__main__":
    main()

