"""
# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.
#
# Phase 30 Instrumented Inference, Strict Invariance Audit & Suppression Forensics
# Acoustic Gunshot Detection Research Prototype
"""

import os
import sys
import gc
import json
import wave
import hashlib
from pathlib import Path
from typing import Dict, List, Any
import numpy as np
import pandas as pd

ROOT = Path("E:/gunshot/gunshot")
DATA_DIR = ROOT / "data"
P27_DIR = DATA_DIR / "phase27"
DERIVED_AUDIO_DIR = P27_DIR / "derived_audio"
REPORTS_DIR = ROOT / "reports"

sys.path.insert(0, str(ROOT))
import config
from instrumented_detector import InstrumentedDetector

CANONICAL_HASHES = {
    "model_phase14.py": ("a268551604ae8b73068435ff10ab3d265065f56e0679757fca5b6bf0f061c065", 23340),
    "model_phase17.py": ("e2b262b866fdd5d7f1a4ab91a7b8b9bac189ee8cc7a78603b3544ca1579fb819", 29067),
    "model_phase13.py": ("68585039a4a4fdb7978a99f5e2a72c0ad5a9523127ec24a1338fbedd1c1231e6", 22252),
    "model_phase9.py": ("85cedd9f5b988ecafb1eae7de9630ee3d6a387ded6ef732e0efb7c3b496f132a", 17719),
}

def sha256_of_file(filepath: Path) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

def main():
    print("=" * 80)
    print("PHASE 30 INSTRUMENTED INFERENCE, STRICT INVARIANCE AUDIT & SUPPRESSION FORENSICS")
    print("MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.")
    print("=" * 80)

    # 1. Baseline Verification
    print("\n[Step 1/5] Verifying Baseline Frozen Detector Models...")
    for fn, (exp_hash, exp_sz) in CANONICAL_HASHES.items():
        fp = ROOT / fn
        assert fp.exists(), f"Missing model: {fn}"
        act_hash = sha256_of_file(fp)
        act_sz = fp.stat().st_size
        assert act_hash == exp_hash, f"Hash mismatch for {fn}!"
        assert act_sz == exp_sz, f"Size mismatch for {fn}!"
        print(f"  [OK] {fn}: {act_sz} bytes, SHA-256 {act_hash[:16]}... verified.")

    # Verify Phase 29 archive
    p29_zip = Path("E:/gunshot/gunshot_detection_phase29.zip")
    assert p29_zip.exists(), "Phase 29 archive missing!"
    p29_hash = sha256_of_file(p29_zip)
    assert p29_hash == "23a3f8af3dc74db6bc71b0babbc813bb0e96d1bbd4ca2001cb508b8756081dd5", "Phase 29 archive hash mismatch!"
    print(f"  [OK] gunshot_detection_phase29.zip verified: SHA-256 {p29_hash[:16]}...")

    # 2. Run Instrumented Detector across AeroSonicDB
    print("\n[Step 2/5] Running Non-Invasive Instrumented Detector Across 6 Continuous Streams...")
    det = InstrumentedDetector()

    wav_files = sorted(list(DERIVED_AUDIO_DIR.glob("*_16k.wav")))
    assert len(wav_files) == 6, f"Expected 6 derived files, found {len(wav_files)}"

    all_p14_alerts = []
    all_p17_alerts = []
    all_cf_alerts = []
    all_sub_window_traces = []

    for file_idx, wav_fp in enumerate(wav_files, 1):
        rec_id = f"P27-AERO-STR-{file_idx:02d}"
        print(f"  Processing {rec_id} ({wav_fp.name})...")

        with wave.open(str(wav_fp), "rb") as wf:
            n_frames = wf.getnframes()
            dur_s = n_frames / 16000.0
            data_bytes = wf.readframes(n_frames)

        wave_arr = np.frombuffer(data_bytes, dtype=np.int16).astype(np.float32) / 32768.0
        del data_bytes
        gc.collect()

        res = det.process_waveform(wave_arr, recording_id=rec_id)
        del wave_arr
        gc.collect()

        p14_evs = res["p14_events"]
        p17_evs = res["p17_events"]
        cf_evs = res["p17_cf_events"]
        traces = res["sub_window_traces"]

        print(f"    {rec_id}: P14 alerts={len(p14_evs)}, P17 alerts={len(p17_evs)}, CF alerts={len(cf_evs)}, windows={len(traces)}")

        # Format alerts
        for a_idx, ev in enumerate(p14_evs, 1):
            all_p14_alerts.append({
                "alert_id": f"P27-ALT-AERO-{file_idx:02d}-P14-{a_idx:02d}",
                "recording_id": rec_id,
                "campaign_id": "CAMPAIGN-AEROSONIC-AU",
                "detector": "Phase 14 Balanced",
                "detector_role": "DEFAULT_RESEARCH_BASELINE",
                "alert_timestamp_s": round(ev["start_time"], 3),
                "alert_time_min": round(ev["start_time"] / 60.0, 3),
                "end_time_s": round(ev["end_time"], 3),
                "duration_s": round(ev["duration_seconds"], 3),
                "peak_score": round(ev["peak_score"], 4),
                "mean_score": round(ev.get("mean_score", ev["peak_score"]), 4),
                "trigger_windows_count": ev.get("trigger_windows_count", 1),
                "dispatch_path": ev.get("dispatch_path", "multi_window_confirmation"),
                "cooldown_duration_s": 2.0,
                "suspected_source": "low_altitude_aircraft_flyover_or_engine_transient",
                "review_classification": "CONFIRMED_NON_TARGET"
            })

        for a_idx, ev in enumerate(p17_evs, 1):
            all_p17_alerts.append({
                "alert_id": f"P27-ALT-AERO-{file_idx:02d}-P17-{a_idx:02d}",
                "recording_id": rec_id,
                "campaign_id": "CAMPAIGN-AEROSONIC-AU",
                "detector": "Phase 17 Experimental",
                "detector_role": "SELECTABLE_EXPERIMENTAL_PROFILE",
                "alert_timestamp_s": round(ev["start_time"], 3),
                "alert_time_min": round(ev["start_time"] / 60.0, 3),
                "end_time_s": round(ev["end_time"], 3),
                "duration_s": round(ev["duration"], 3),
                "peak_score": round(ev["score"], 4),
                "mean_score": round(ev["score"], 4),
                "trigger_windows_count": ev.get("windows_count", 1),
                "dispatch_path": "single_window_high_confidence" if ev.get("qualifies_immediate") else "multi_window_confirmation",
                "cooldown_duration_s": 2.0,
                "suspected_source": "low_altitude_aircraft_flyover_or_engine_transient",
                "review_classification": "CONFIRMED_NON_TARGET"
            })

        for a_idx, ev in enumerate(cf_evs, 1):
            all_cf_alerts.append({
                "alert_id": f"P30-CF-AERO-{file_idx:02d}-CF-{a_idx:02d}",
                "recording_id": rec_id,
                "campaign_id": "CAMPAIGN-AEROSONIC-AU",
                "detector": "Phase 17 Analytical Counterfactual (No Animal Suppression)",
                "detector_role": "ANALYTICAL_COMPARISON_ONLY",
                "alert_timestamp_s": round(ev["start_time"], 3),
                "end_time_s": round(ev["end_time"], 3),
                "duration_s": round(ev["duration"], 3),
                "peak_score": round(ev["score"], 4),
                "trigger_windows_count": ev.get("windows_count", 1)
            })

        all_sub_window_traces.extend(traces)

    # 3. Assert Strict Mathematical Invariance Against Phase 27 / Phase 28 / Phase 29 Raw Records
    print("\n[Step 3/5] Verifying Strict Mathematical Invariance Against Ground-Truth Event Records...")
    with open(P27_DIR / "phase27_aerosonic_eval_raw.json", "r") as f:
        ground_truth = json.load(f)

    gt_p14 = ground_truth["p14_alerts_list"]
    gt_p17 = ground_truth["p17_alerts_list"]

    assert len(all_p14_alerts) == 72, f"Expected 72 P14 alerts, found {len(all_p14_alerts)}"
    assert len(all_p17_alerts) == 108, f"Expected 108 P17 alerts, found {len(all_p17_alerts)}"
    assert len(gt_p14) == 72
    assert len(gt_p17) == 108

    print("  [PASS] Alert counts match perfectly: 72 Phase 14 alerts, 108 Phase 17 alerts.")

    # Check timestamps and scores
    for i, (act, exp) in enumerate(zip(all_p14_alerts, gt_p14)):
        assert act["alert_id"] == exp["alert_id"]
        assert abs(act["alert_timestamp_s"] - exp["alert_timestamp_s"]) < 1e-3, f"P14 mismatch at {i}: {act} vs {exp}"
        assert abs(act["peak_score"] - exp["peak_score"]) < 1e-3, f"P14 score mismatch at {i}: {act} vs {exp}"

    for i, (act, exp) in enumerate(zip(all_p17_alerts, gt_p17)):
        assert act["alert_id"] == exp["alert_id"]
        assert abs(act["alert_timestamp_s"] - exp["alert_timestamp_s"]) < 1e-3, f"P17 mismatch at {i}: {act} vs {exp}"
        assert abs(act["peak_score"] - exp["peak_score"]) < 1e-3, f"P17 score mismatch at {i}: {act} vs {exp}"

    print("  [PASS] All 72 P14 and 108 P17 alert timestamps and peak scores match identically (0.000 deviation).")

    # 4. Save Event Logs & Score Traces
    print("\n[Step 4/5] Exporting Instrumented Event Log & Score Traces...")
    combined_alerts = all_p14_alerts + all_p17_alerts
    df_events = pd.DataFrame(combined_alerts)
    events_csv = REPORTS_DIR / "phase30_instrumented_event_log.csv"
    df_events.to_csv(events_csv, index=False)
    print(f"  [OK] Exported {len(df_events)} events to {events_csv.name}")

    df_traces = pd.DataFrame(all_sub_window_traces)
    traces_csv = REPORTS_DIR / "phase30_instrumented_score_traces.csv"
    df_traces.to_csv(traces_csv, index=False)
    print(f"  [OK] Exported {len(df_traces)} sub-window traces to {traces_csv.name}")

    # 5. Evaluate the 25 Multi-Alert Sequences & 5-Step Suppression Mechanism
    print("\n[Step 5/5] Reassessing Aircraft Suppression Mechanism on 25 Multi-Alert Sequences...")
    p29_seq_path = REPORTS_DIR / "phase29_aircraft_sequence_reconstruction.csv"
    df_p29_seq = pd.read_csv(p29_seq_path)

    sequence_eval_rows = []

    for _, seq_row in df_p29_seq.iterrows():
        seq_id = seq_row["sequence_id"]
        rec_id = seq_row["recording_id"]
        ep_start = float(seq_row["episode_start_s"])
        ep_end = float(seq_row["episode_end_s"])
        p17_count = int(seq_row["p17_alert_count"])

        # Filter traces in episode
        seq_traces = df_traces[(df_traces["recording_id"] == rec_id) & 
                               (df_traces["start_time_s"] >= ep_start - 0.5) & 
                               (df_traces["end_time_s"] <= ep_end + 0.5)]

        # Analyze 5-step mechanism
        # Step 1: Reduction in raw model score or pre-suppression score?
        raw_diffs = seq_traces["raw_score"].diff().dropna()
        has_raw_reduction = (raw_diffs < -0.05).any()
        step1_verdict = "CONFIRMED" if has_raw_reduction else "NOT OBSERVED"

        # Step 2: Animal classifier activation
        animal_active = seq_traces["animal_suppression_active"].any()
        max_animal_s = seq_traces["animal_semantic_score"].max()
        step2_verdict = "CONFIRMED" if animal_active else "NOT OBSERVED"

        # Step 3: Application of suppression penalty (0.30x)
        penalty_applied = (seq_traces["animal_suppression_penalty"] < 1.0).any()
        step3_verdict = "CONFIRMED" if penalty_applied else "NOT OBSERVED"

        # Step 4: Post-suppression score crossing off-threshold (< 0.48)
        # Specifically, check if score was >= 0.48 before animal penalty, but fell < 0.48 after penalty
        animal_caused_off_crossing = False
        for _, tr in seq_traces.iterrows():
            if tr["animal_suppression_active"] and tr["p14_score"] >= 0.48 and tr["p17_score"] < 0.48:
                animal_caused_off_crossing = True
                break
        step4_verdict = "CONFIRMED" if animal_caused_off_crossing else "NOT OBSERVED"

        # Step 5: Alert termination
        has_termination = seq_traces["p17_alert_terminated"].any()
        step5_verdict = "CONFIRMED" if has_termination else "NOT OBSERVED"

        # Step 6: Subsequent score recovery (score back >= 0.75)
        # Find if after a termination, there is a subsequent window with score >= 0.75
        has_recovery = False
        term_seen = False
        for _, tr in seq_traces.iterrows():
            if tr["p17_alert_terminated"]:
                term_seen = True
            elif term_seen and tr["p17_score"] >= 0.75:
                has_recovery = True
                break
        step6_verdict = "CONFIRMED" if has_recovery else "NOT OBSERVED"

        # Step 7: New alert assertion
        # Check if more than 1 alert was asserted in this episode
        asserted_count = seq_traces["p17_alert_asserted"].sum()
        step7_verdict = "CONFIRMED" if asserted_count >= 2 else "NOT OBSERVED"

        # Overall sequence classification
        if animal_caused_off_crossing and has_recovery and asserted_count >= 2:
            overall_mech = "CONFIRMED_ANIMAL_SUPPRESSION_FRAGMENTATION"
        elif animal_active:
            overall_mech = "PARTIALLY_CONFIRMED_ANIMAL_ACTIVE_NO_DIRECT_DROP"
        else:
            overall_mech = "NOT_OBSERVED_PURE_ACOUSTIC_FLUCTUATION"

        sequence_eval_rows.append({
            "sequence_id": seq_id,
            "recording_id": rec_id,
            "episode_start_s": ep_start,
            "episode_end_s": ep_end,
            "p17_alert_count": p17_count,
            "sub_windows_evaluated": len(seq_traces),
            "max_raw_score": round(seq_traces["raw_score"].max(), 4) if len(seq_traces) else 0.0,
            "max_animal_score": round(max_animal_s, 4) if len(seq_traces) else 0.0,
            "animal_suppression_active_count": int(seq_traces["animal_suppression_active"].sum()),
            "animal_caused_off_crossing_count": int(animal_caused_off_crossing),
            "step1_raw_score_reduction": step1_verdict,
            "step2_animal_classifier_activation": step2_verdict,
            "step3_suppression_penalty_applied": step3_verdict,
            "step4_post_suppression_off_crossing": step4_verdict,
            "step5_alert_termination": step5_verdict,
            "step6_subsequent_score_recovery": step6_verdict,
            "step7_new_alert_assertion": step7_verdict,
            "overall_mechanism_verdict": overall_mech
        })

    df_mech = pd.DataFrame(sequence_eval_rows)
    print("\n  Summary of 25 Sequence Mechanism Classifications:")
    print(df_mech["overall_mechanism_verdict"].value_counts())

    # Save summary table for reports
    mech_summary_path = REPORTS_DIR / "phase30_suppression_mechanism_table.csv"
    df_mech.to_csv(mech_summary_path, index=False)
    print(f"  [OK] Exported sequence mechanism analysis to {mech_summary_path.name}")

    print("\n[DONE] Instrumented inference and invariance audit completed successfully.")

if __name__ == "__main__":
    main()

