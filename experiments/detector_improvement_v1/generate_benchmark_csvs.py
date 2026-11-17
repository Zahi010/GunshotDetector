"""
Benchmark Script for Detector Improvement V1 vs Baseline (Phase 14 & Phase 36).
Generates:
1. baseline_results.csv
2. experimental_results.csv
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

from experiments.detector_improvement_v1.model_detector_improvement_v1 import (
    CalibratedAcousticSuppressionV1
)
from experiments.phase36.event_state_machine import EventStateMachine, EventState
from scripts.run_phase39_prospective_evaluation import evaluate_condition_on_features

OUTPUT_DIR = pathlib.Path(__file__).resolve().parent
p38_cache = REPO_ROOT / "experiments" / "phase38" / "feature_cache"
p39_cache = REPO_ROOT / "experiments" / "phase39" / "feature_cache"
p40_cache = REPO_ROOT / "experiments" / "phase40" / "feature_cache"

inv = pd.read_csv(REPO_ROOT / "experiments" / "phase41" / "phase41_recording_inventory.csv")

with open(OUTPUT_DIR / "config_improvement_v1.json", "r", encoding="utf-8") as f:
    config_v1 = json.load(f)


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


def evaluate_v1_on_features(feats, profile="balanced"):
    cfg = config_v1["profiles"][profile]
    supp_engine = CalibratedAcousticSuppressionV1(cfg["suppression"])
    
    raw_scores = feats["raw_scores"]
    yamnet_scores = feats["yamnet_scores"]
    crest_db = feats["crest_factor_db"]
    dur_sec = feats["duration_seconds"]
    n_windows = len(raw_scores)

    if n_windows == 0:
        return []

    fsm = EventStateMachine(
        threshold_base=cfg["threshold_base"],
        threshold_high=cfg["threshold_high"],
        threshold_off=cfg["threshold_off"],
        confirm_windows=cfg["confirm_windows"],
        cooldown_secs=cfg["cooldown_secs"],
        max_hop_gap_s=cfg["max_hop_gap_s"],
        min_crest_factor_db=cfg["min_crest_factor_db"],
        single_win_min_crest_db=cfg["single_win_min_crest_db"],
        allow_short_clip_exception=cfg["allow_short_clip_exception"]
    )

    hop_sec = 0.48
    win_sec = 0.96

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
    return fsm.events_emitted


def main():
    print(f"[Benchmark] Evaluating {len(inv)} recordings across all partitions...")
    
    rec_level_rows = []
    
    # Trackers for summary tables
    models = ["phase14", "phase36", "v1_balanced", "v1_precision", "v1_sensitivity"]
    summary = {m: {
        "pos_detected": 0, "pos_total": 0, "pos_events": 0,
        "fw_detected": 0, "fw_total": 0, "fw_events": 0,
        "dist_detected": 0, "dist_total": 0, "dist_events": 0,
        "cont_hours": 0.0, "cont_events": 0
    } for m in models}

    for idx, r in inv.iterrows():
        cid = r["recording_id"]
        partition = r["evaluation_partition"]
        dur = float(r["duration_seconds"])
        is_pos = (partition == "POSITIVE_GUNSHOT")
        is_fw = bool(r.get("is_fireworks_eval", False))
        is_dist = bool(r.get("is_distractor_eval", False))
        is_cont = (partition == "CONTINUOUS_AMBIENT")

        feats = load_feature_dict(cid)
        crest_db = feats["crest_factor_db"]

        # Run P14 (COND1) and P36 (COND6)
        ev_p14 = evaluate_condition_on_features("COND1", feats, cid)
        ev_p36 = evaluate_condition_on_features("COND6", feats, cid)

        # Run V1 variants
        ev_v1_bal = evaluate_v1_on_features(feats, "balanced")
        ev_v1_prec = evaluate_v1_on_features(feats, "high_precision")
        ev_v1_sens = evaluate_v1_on_features(feats, "high_sensitivity")

        ev_map = {
            "phase14": ev_p14,
            "phase36": ev_p36,
            "v1_balanced": ev_v1_bal,
            "v1_precision": ev_v1_prec,
            "v1_sensitivity": ev_v1_sens
        }

        # Update summary counts
        for m in models:
            evs = ev_map[m]
            has_det = len(evs) > 0
            n_evs = len(evs)
            if is_pos:
                summary[m]["pos_total"] += 1
                if has_det: summary[m]["pos_detected"] += 1
                summary[m]["pos_events"] += n_evs
            elif is_fw:
                summary[m]["fw_total"] += 1
                if has_det: summary[m]["fw_detected"] += 1
                summary[m]["fw_events"] += n_evs
            elif is_dist:
                summary[m]["dist_total"] += 1
                if has_det: summary[m]["dist_detected"] += 1
                summary[m]["dist_events"] += n_evs
            elif is_cont:
                summary[m]["cont_hours"] += (dur / 3600.0)
                summary[m]["cont_events"] += n_evs

        # Detailed recording level record
        p14_peak = float(max([e["peak_score"] for e in ev_p14])) if ev_p14 else 0.0
        p36_peak = float(max([e["peak_score"] for e in ev_p36])) if ev_p36 else 0.0
        v1_peak = float(max([e["peak_score"] for e in ev_v1_bal])) if ev_v1_bal else 0.0
        v1_path = ev_v1_bal[0]["dispatch_path"] if ev_v1_bal else "none"

        rec_level_rows.append({
            "recording_id": cid,
            "partition": partition,
            "ground_truth_gunshot": 1 if is_pos else 0,
            "duration_sec": round(dur, 3),
            "crest_factor_db": round(crest_db, 2),
            "p14_detected": 1 if len(ev_p14) > 0 else 0,
            "p14_event_count": len(ev_p14),
            "p14_peak_score": round(p14_peak, 4),
            "p36_detected": 1 if len(ev_p36) > 0 else 0,
            "p36_event_count": len(ev_p36),
            "p36_peak_score": round(p36_peak, 4),
            "v1_detected": 1 if len(ev_v1_bal) > 0 else 0,
            "v1_event_count": len(ev_v1_bal),
            "v1_peak_score": round(v1_peak, 4),
            "v1_dispatch_path": v1_path
        })

    # Save recording-level predictions
    df_rec = pd.DataFrame(rec_level_rows)
    df_rec.to_csv(OUTPUT_DIR / "recording_level_predictions.csv", index=False)
    print(f"[Benchmark] Saved recording_level_predictions.csv ({len(df_rec)} rows)")

    # 1. baseline_results.csv
    baseline_rows = []
    base_models = [
        ("Phase 14 Balanced Baseline", "phase14", "model_phase14.py", "Legacy Gating + Soft Cooldown"),
        ("Phase 36 Experimental V1 (Conservative)", "phase36", "experiments/phase36", "4-State FSM + Conservative Animal Gating")
    ]
    for name, key, lineage, note in base_models:
        s = summary[key]
        pos_rec = (s["pos_detected"] / s["pos_total"]) * 100.0 if s["pos_total"] > 0 else 0.0
        dup_evs = max(0, s["pos_events"] - s["pos_detected"])
        dup_rate = (dup_evs / s["pos_events"]) * 100.0 if s["pos_events"] > 0 else 0.0
        fw_rate = (s["fw_detected"] / s["fw_total"]) * 100.0 if s["fw_total"] > 0 else 0.0
        dist_rate = (s["dist_detected"] / s["dist_total"]) * 100.0 if s["dist_total"] > 0 else 0.0
        tot_dist_det = s["fw_detected"] + s["dist_detected"]
        tot_dist_rate = (tot_dist_det / 220.0) * 100.0
        far_per_hr = s["cont_events"] / s["cont_hours"] if s["cont_hours"] > 0 else 0.0

        baseline_rows.append({
            "detector_id": key,
            "detector_name": name,
            "architecture_lineage": lineage,
            "temporal_mechanism": note,
            "positive_recall_pct": round(pos_rec, 2),
            "positive_detected_count": s["pos_detected"],
            "positive_total_count": s["pos_total"],
            "tp_duplicate_alerts": dup_evs,
            "tp_duplicate_rate_pct": round(dup_rate, 2),
            "fireworks_trigger_pct": round(fw_rate, 2),
            "fireworks_triggers_count": s["fw_detected"],
            "fireworks_total_count": s["fw_total"],
            "other_distractor_trigger_pct": round(dist_rate, 2),
            "other_distractor_triggers_count": s["dist_detected"],
            "other_distractor_total_count": s["dist_total"],
            "total_distractor_far_pct": round(tot_dist_rate, 2),
            "total_distractor_triggers": tot_dist_det,
            "continuous_exposure_hours": round(s["cont_hours"], 4),
            "continuous_alerts_count": s["cont_events"],
            "continuous_far_per_hour": round(far_per_hr, 2)
        })

    df_base = pd.DataFrame(baseline_rows)
    df_base.to_csv(OUTPUT_DIR / "baseline_results.csv", index=False)
    print(f"[Benchmark] Saved baseline_results.csv")

    # 2. experimental_results.csv
    exp_rows = []
    exp_models = [
        ("Balanced (Default)", "v1_balanced", 0.75, 0.88, 0.48, 2.0, 8.8, 12.0),
        ("High Precision", "v1_precision", 0.80, 0.90, 0.52, 2.5, 9.5, 13.0),
        ("High Sensitivity", "v1_sensitivity", 0.70, 0.85, 0.42, 1.5, 8.0, 11.0)
    ]
    p14_tot_dist = summary["phase14"]["fw_detected"] + summary["phase14"]["dist_detected"]
    p36_tot_dist = summary["phase36"]["fw_detected"] + summary["phase36"]["dist_detected"]
    p14_dup = max(0, summary["phase14"]["pos_events"] - summary["phase14"]["pos_detected"])

    for prof_name, key, th_b, th_h, th_o, cool, min_crest, single_crest in exp_models:
        s = summary[key]
        pos_rec = (s["pos_detected"] / s["pos_total"]) * 100.0 if s["pos_total"] > 0 else 0.0
        dup_evs = max(0, s["pos_events"] - s["pos_detected"])
        dup_rate = (dup_evs / s["pos_events"]) * 100.0 if s["pos_events"] > 0 else 0.0
        fw_rate = (s["fw_detected"] / s["fw_total"]) * 100.0 if s["fw_total"] > 0 else 0.0
        dist_rate = (s["dist_detected"] / s["dist_total"]) * 100.0 if s["dist_total"] > 0 else 0.0
        tot_dist_det = s["fw_detected"] + s["dist_detected"]
        tot_dist_rate = (tot_dist_det / 220.0) * 100.0
        far_per_hr = s["cont_events"] / s["cont_hours"] if s["cont_hours"] > 0 else 0.0

        rel_p36_red = ((p36_tot_dist - tot_dist_det) / float(p36_tot_dist)) * 100.0
        rel_p14_red = ((p14_tot_dist - tot_dist_det) / float(p14_tot_dist)) * 100.0
        rel_dup_red = ((p14_dup - dup_evs) / float(p14_dup)) * 100.0

        exp_rows.append({
            "profile_name": prof_name,
            "detector_id": key,
            "threshold_base": th_b,
            "threshold_high": th_h,
            "threshold_off": th_o,
            "cooldown_secs": cool,
            "min_crest_factor_db": min_crest,
            "single_win_min_crest_db": single_crest,
            "positive_recall_pct": round(pos_rec, 2),
            "positive_detected_count": s["pos_detected"],
            "positive_total_count": s["pos_total"],
            "tp_duplicate_alerts": dup_evs,
            "tp_duplicate_rate_pct": round(dup_rate, 2),
            "fireworks_trigger_pct": round(fw_rate, 2),
            "fireworks_triggers_count": s["fw_detected"],
            "fireworks_total_count": s["fw_total"],
            "other_distractor_trigger_pct": round(dist_rate, 2),
            "other_distractor_triggers_count": s["dist_detected"],
            "other_distractor_total_count": s["dist_total"],
            "total_distractor_far_pct": round(tot_dist_rate, 2),
            "total_distractor_triggers": tot_dist_det,
            "continuous_exposure_hours": round(s["cont_hours"], 4),
            "continuous_alerts_count": s["cont_events"],
            "continuous_far_per_hour": round(far_per_hr, 2),
            "rel_distractor_reduction_vs_p36_pct": round(rel_p36_red, 2),
            "rel_distractor_reduction_vs_p14_pct": round(rel_p14_red, 2),
            "rel_duplicate_reduction_vs_p14_pct": round(rel_dup_red, 2)
        })

    df_exp = pd.DataFrame(exp_rows)
    df_exp.to_csv(OUTPUT_DIR / "experimental_results.csv", index=False)
    print(f"[Benchmark] Saved experimental_results.csv")
    print(f"[Benchmark] Execution finished successfully.")

if __name__ == "__main__":
    main()

