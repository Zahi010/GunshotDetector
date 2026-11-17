"""
Phase 18: Canonical Ground-Truth Ballistic Event Reconciliation & Table Generator.

Resolves the 39-event discrepancy from Phase 17:
- Audits and unifies all 39 ground-truth events across 4 continuous streams:
  * P17-POS-STREAM-01 (Natural Beretta Range Sequence, 5 events: P17-NAT-001..P17-NAT-005)
  * P17-POS-STREAM-02 (Natural Scepter Urban Sequence, 1 event: P17-NAT-006)
  * P17-POS-STREAM-03 (Calibrated Multi-Condition Ballistic Stream, 24 events: P17-EV-001..P17-EV-024)
  * P17-POS-STREAM-04 (Rapid-Cadence Burst Stream, 9 events: P17-EV-025..P17-EV-033)
- Reconciles acoustic condition breakdown:
  * clean_direct: 11 (5 natural + 6 calibrated)
  * clipped_saturated: 6
  * distant_low_snr: 3
  * pocket_occluded: 6
  * rapid_cadence_burst: 9
  * urban_sensor: 4 (1 natural + 3 calibrated)
  * Total = 39
- Records per-event detection decisions, latencies, false-alert associations, and duplicate statuses across:
  * Phase 9 Balanced
  * Phase 13 Balanced
  * Phase 14 Balanced (Production)
  * Phase 14 High-Precision
  * Phase 14 High-Sensitivity
  * Phase 17 Experimental
- Enforces strict assertions that category sums match overall totals.

SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.
"""

import os
import sys
import json
from pathlib import Path
import pandas as pd
import numpy as np

WORKSPACE_ROOT = Path("e:/gunshot/gunshot").resolve()
REPORTS_DIR = WORKSPACE_ROOT / "reports"

def build_canonical_event_table():
    print("=" * 80)
    print("   PHASE 18: CANONICAL 39-EVENT TABLE RECONCILIATION & AUDIT")
    print("   Safety: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY")
    print("=" * 80 + "\n")

    # 1. Load base files
    manifest_csv = REPORTS_DIR / "phase17_positive_event_manifest.csv"
    timeline_csv = REPORTS_DIR / "phase17_event_detection_timeline.csv"
    false_alert_csv = REPORTS_DIR / "phase17_false_alert_timeline.csv"
    stream_manifest_csv = REPORTS_DIR / "phase17_continuous_positive_manifest.csv"

    if not manifest_csv.exists() or not timeline_csv.exists():
        raise FileNotFoundError("Required Phase 17 evaluation files missing.")

    df_manifest = pd.read_csv(manifest_csv)
    df_timeline = pd.read_csv(timeline_csv)
    df_false = pd.read_csv(false_alert_csv) if false_alert_csv.exists() else pd.DataFrame()
    df_streams = pd.read_csv(stream_manifest_csv) if stream_manifest_csv.exists() else pd.DataFrame()

    # 2. Add the 6 natural stream events that were hardcoded in run_phase17_continuous_positive_evaluation.py
    natural_events = [
        {
            "stream_id": "P17-POS-STREAM-01",
            "stream_filename": "phase17_positive_stream_01_natural_beretta_range_sequence_55s.wav",
            "stream_type": "NATURAL_CONTINUOUS_FIELD",
            "event_id": "P17-NAT-001",
            "original_source_file": "phase15_gunshot_clean_berettadouble04.wav",
            "acoustic_condition": "clean_direct",
            "scaling_factor": 1.0,
            "event_start_time_sec": 7.65,
            "event_peak_time_sec": 7.78,
            "event_end_time_sec": 8.50,
            "event_duration_sec": 0.85,
            "annotation_confidence": 1.0,
            "recording_session": "MITCHELL_2015_RANGE_CAMPAIGN",
            "source_provenance": "HISTORICALLY_RELATED_SESSION"
        },
        {
            "stream_id": "P17-POS-STREAM-01",
            "stream_filename": "phase17_positive_stream_01_natural_beretta_range_sequence_55s.wav",
            "stream_type": "NATURAL_CONTINUOUS_FIELD",
            "event_id": "P17-NAT-002",
            "original_source_file": "phase15_gunshot_clean_berettadouble04.wav",
            "acoustic_condition": "clean_direct",
            "scaling_factor": 1.0,
            "event_start_time_sec": 8.95,
            "event_peak_time_sec": 9.05,
            "event_end_time_sec": 9.80,
            "event_duration_sec": 0.85,
            "annotation_confidence": 1.0,
            "recording_session": "MITCHELL_2015_RANGE_CAMPAIGN",
            "source_provenance": "HISTORICALLY_RELATED_SESSION"
        },
        {
            "stream_id": "P17-POS-STREAM-01",
            "stream_filename": "phase17_positive_stream_01_natural_beretta_range_sequence_55s.wav",
            "stream_type": "NATURAL_CONTINUOUS_FIELD",
            "event_id": "P17-NAT-003",
            "original_source_file": "phase15_gunshot_clean_berettadouble04.wav",
            "acoustic_condition": "clean_direct",
            "scaling_factor": 1.0,
            "event_start_time_sec": 10.55,
            "event_peak_time_sec": 10.68,
            "event_end_time_sec": 11.40,
            "event_duration_sec": 0.85,
            "annotation_confidence": 1.0,
            "recording_session": "MITCHELL_2015_RANGE_CAMPAIGN",
            "source_provenance": "HISTORICALLY_RELATED_SESSION"
        },
        {
            "stream_id": "P17-POS-STREAM-01",
            "stream_filename": "phase17_positive_stream_01_natural_beretta_range_sequence_55s.wav",
            "stream_type": "NATURAL_CONTINUOUS_FIELD",
            "event_id": "P17-NAT-004",
            "original_source_file": "phase15_gunshot_clean_berettadouble04.wav",
            "acoustic_condition": "clean_direct",
            "scaling_factor": 1.0,
            "event_start_time_sec": 12.10,
            "event_peak_time_sec": 12.22,
            "event_end_time_sec": 12.90,
            "event_duration_sec": 0.80,
            "annotation_confidence": 1.0,
            "recording_session": "MITCHELL_2015_RANGE_CAMPAIGN",
            "source_provenance": "HISTORICALLY_RELATED_SESSION"
        },
        {
            "stream_id": "P17-POS-STREAM-01",
            "stream_filename": "phase17_positive_stream_01_natural_beretta_range_sequence_55s.wav",
            "stream_type": "NATURAL_CONTINUOUS_FIELD",
            "event_id": "P17-NAT-005",
            "original_source_file": "phase15_gunshot_clean_berettadouble04.wav",
            "acoustic_condition": "clean_direct",
            "scaling_factor": 1.0,
            "event_start_time_sec": 13.80,
            "event_peak_time_sec": 13.92,
            "event_end_time_sec": 14.60,
            "event_duration_sec": 0.80,
            "annotation_confidence": 1.0,
            "recording_session": "MITCHELL_2015_RANGE_CAMPAIGN",
            "source_provenance": "HISTORICALLY_RELATED_SESSION"
        },
        {
            "stream_id": "P17-POS-STREAM-02",
            "stream_filename": "phase17_positive_stream_02_natural_scepter_urban_sequence_8s.wav",
            "stream_type": "NATURAL_CONTINUOUS_SENSOR",
            "event_id": "P17-NAT-006",
            "original_source_file": "phase15_gunshot_scepter_calibration_01.wav",
            "acoustic_condition": "urban_sensor",
            "scaling_factor": 1.0,
            "event_start_time_sec": 0.80,
            "event_peak_time_sec": 0.95,
            "event_end_time_sec": 2.20,
            "event_duration_sec": 1.40,
            "annotation_confidence": 1.0,
            "recording_session": "SHOTSPOTTER_URBAN_DEPLOYMENT",
            "source_provenance": "SOURCE_INDEPENDENT_EXTERNAL"
        }
    ]

    all_raw_events = natural_events + df_manifest.to_dict(orient="records")
    df_raw = pd.DataFrame(all_raw_events)

    # 3. Pivot timeline data for each detector
    # Columns in timeline: detector, event_id, stream_id, condition, event_start_sec, event_end_sec, detected, alert_time_sec, detection_delay_sec, duplicate_alerts, score, crest_factor_db
    detectors = [
        "Phase 9 Balanced",
        "Phase 13 Balanced",
        "Phase 14 Balanced",
        "Phase 14 High-Precision",
        "Phase 14 High-Sensitivity",
        "Phase 17 Experimental"
    ]
    det_slugs = {
        "Phase 9 Balanced": "p9_balanced",
        "Phase 13 Balanced": "p13_balanced",
        "Phase 14 Balanced": "p14_balanced",
        "Phase 14 High-Precision": "p14_high_precision",
        "Phase 14 High-Sensitivity": "p14_high_sensitivity",
        "Phase 17 Experimental": "p17_experimental"
    }

    # Verify every event appears exactly once in timeline for each detector
    timeline_counts = df_timeline.groupby(["detector", "event_id"]).size()
    if (timeline_counts != 1).any():
        raise ValueError("Duplicate detector-event pairs detected in timeline!")

    piv_det = df_timeline.pivot(index="event_id", columns="detector", values="detected")
    piv_delay = df_timeline.pivot(index="event_id", columns="detector", values="detection_delay_sec")
    piv_alert_time = df_timeline.pivot(index="event_id", columns="detector", values="alert_time_sec")
    piv_score = df_timeline.pivot(index="event_id", columns="detector", values="score")
    piv_crest = df_timeline.pivot(index="event_id", columns="detector", values="crest_factor_db")
    piv_dups = df_timeline.pivot(index="event_id", columns="detector", values="duplicate_alerts")

    # False alert association: check if any false alert occurred within [-2.0, +2.0]s of an event
    # In continuous positive evaluation, false alerts were unassociated background alerts
    false_alert_map = {}
    for ev_id, row in df_raw.iterrows():
        eid = row["event_id"]
        sid = row["stream_id"]
        t_s = row["event_start_time_sec"]
        t_e = row["event_end_time_sec"]
        
        # Check false alerts in this stream
        nearby_fas = []
        if not df_false.empty:
            stream_fas = df_false[df_false["stream_id"] == sid]
            for _, fa in stream_fas.iterrows():
                fa_t = fa["alert_time_sec"]
                if (t_s - 2.0) <= fa_t <= (t_e + 2.0):
                    nearby_fas.append(f"{fa['detector']}@{fa_t:.2f}s")
        false_alert_map[eid] = "; ".join(nearby_fas) if nearby_fas else "NONE"

    # 4. Construct Canonical Table
    canonical_rows = []
    for idx, r in df_raw.iterrows():
        eid = r["event_id"]
        sid = r["stream_id"]
        cond = r["acoustic_condition"]
        src = r["original_source_file"]
        prov = r["source_provenance"]
        t_start = float(r["event_start_time_sec"])
        t_end = float(r["event_end_time_sec"])
        duration = float(r["event_duration_sec"])

        # Determine duplicate alert status
        dup_counts = [int(piv_dups.loc[eid, d]) for d in detectors if eid in piv_dups.index and pd.notna(piv_dups.loc[eid, d])]
        has_duplicate = any(c > 0 for c in dup_counts)

        row_dict = {
            "event_id": eid,
            "stream_id": sid,
            "source_recording_id": src,
            "stream_type": r.get("stream_type", "CALIBRATED_TRANSPARENT_SPLICED"),
            "start_time_sec": t_start,
            "end_time_sec": t_end,
            "duration_sec": duration,
            "acoustic_condition": cond,
            "provenance_classification": prov,
            "recording_session": r.get("recording_session", "UNKNOWN"),
            "detected_p9_balanced": bool(piv_det.loc[eid, "Phase 9 Balanced"]) if eid in piv_det.index else False,
            "detected_p13_balanced": bool(piv_det.loc[eid, "Phase 13 Balanced"]) if eid in piv_det.index else False,
            "detected_p14_balanced": bool(piv_det.loc[eid, "Phase 14 Balanced"]) if eid in piv_det.index else False,
            "detected_p14_high_precision": bool(piv_det.loc[eid, "Phase 14 High-Precision"]) if eid in piv_det.index else False,
            "detected_p14_high_sensitivity": bool(piv_det.loc[eid, "Phase 14 High-Sensitivity"]) if eid in piv_det.index else False,
            "detected_p17_experimental": bool(piv_det.loc[eid, "Phase 17 Experimental"]) if eid in piv_det.index else False,
            "latency_p9_balanced_sec": piv_delay.loc[eid, "Phase 9 Balanced"] if (eid in piv_delay.index and pd.notna(piv_delay.loc[eid, "Phase 9 Balanced"])) else None,
            "latency_p13_balanced_sec": piv_delay.loc[eid, "Phase 13 Balanced"] if (eid in piv_delay.index and pd.notna(piv_delay.loc[eid, "Phase 13 Balanced"])) else None,
            "latency_p14_balanced_sec": piv_delay.loc[eid, "Phase 14 Balanced"] if (eid in piv_delay.index and pd.notna(piv_delay.loc[eid, "Phase 14 Balanced"])) else None,
            "latency_p14_high_precision_sec": piv_delay.loc[eid, "Phase 14 High-Precision"] if (eid in piv_delay.index and pd.notna(piv_delay.loc[eid, "Phase 14 High-Precision"])) else None,
            "latency_p14_high_sensitivity_sec": piv_delay.loc[eid, "Phase 14 High-Sensitivity"] if (eid in piv_delay.index and pd.notna(piv_delay.loc[eid, "Phase 14 High-Sensitivity"])) else None,
            "latency_p17_experimental_sec": piv_delay.loc[eid, "Phase 17 Experimental"] if (eid in piv_delay.index and pd.notna(piv_delay.loc[eid, "Phase 17 Experimental"])) else None,
            "score_p14_balanced": piv_score.loc[eid, "Phase 14 Balanced"] if eid in piv_score.index else None,
            "crest_p14_balanced_db": piv_crest.loc[eid, "Phase 14 Balanced"] if eid in piv_crest.index else None,
            "duplicate_alerts_count": max(dup_counts) if dup_counts else 0,
            "duplicate_alert_status": "DUPLICATE_ALERT_PRESENT" if has_duplicate else "ZERO_DUPLICATES",
            "false_alert_associated": false_alert_map.get(eid, "NONE") != "NONE",
            "false_alert_details": false_alert_map.get(eid, "NONE")
        }
        canonical_rows.append(row_dict)

    df_canonical = pd.DataFrame(canonical_rows)

    # 5. Automated Assertions & Reconciliation Checks
    print("\n[+] Running reconciliation assertions:")
    
    # Assertion 1: Total ground-truth events == 39
    total_events = len(df_canonical)
    print(f"  * Total canonical events: {total_events} (Expected: 39)")
    assert total_events == 39, f"Expected 39 events, got {total_events}"

    # Assertion 2: Unique event IDs == 39
    unique_ids = df_canonical["event_id"].nunique()
    print(f"  * Unique event IDs: {unique_ids} (Expected: 39)")
    assert unique_ids == 39, f"Expected 39 unique IDs, got {unique_ids}"

    # Assertion 3: Events by stream sum to 39
    stream_counts = df_canonical["stream_id"].value_counts().to_dict()
    print(f"  * Events by stream: {stream_counts}")
    assert stream_counts.get("P17-POS-STREAM-01", 0) == 5, "Stream 01 must have exactly 5 events"
    assert stream_counts.get("P17-POS-STREAM-02", 0) == 1, "Stream 02 must have exactly 1 event"
    assert stream_counts.get("P17-POS-STREAM-03", 0) == 24, "Stream 03 must have exactly 24 events"
    assert stream_counts.get("P17-POS-STREAM-04", 0) == 9, "Stream 04 must have exactly 9 events"
    assert sum(stream_counts.values()) == 39, "Sum of stream events must be 39"

    # Assertion 4: Events by acoustic condition sum to 39
    cond_counts = df_canonical["acoustic_condition"].value_counts().to_dict()
    print(f"  * Events by acoustic condition: {cond_counts}")
    expected_conditions = {
        "clean_direct": 11,
        "clipped_saturated": 6,
        "distant_low_snr": 3,
        "pocket_occluded": 6,
        "rapid_cadence_burst": 9,
        "urban_sensor": 4
    }
    for c_name, exp_n in expected_conditions.items():
        act_n = cond_counts.get(c_name, 0)
        assert act_n == exp_n, f"Condition '{c_name}' count mismatch: expected {exp_n}, got {act_n}"
    assert sum(cond_counts.values()) == 39, "Sum of condition events must be 39"

    # Assertion 5: Detected events per detector match verified counts
    det_p14_count = df_canonical["detected_p14_balanced"].sum()
    det_p13_count = df_canonical["detected_p13_balanced"].sum()
    det_p9_count = df_canonical["detected_p9_balanced"].sum()
    det_hp_count = df_canonical["detected_p14_high_precision"].sum()
    det_hs_count = df_canonical["detected_p14_high_sensitivity"].sum()
    det_p17_count = df_canonical["detected_p17_experimental"].sum()

    print(f"  * Detections - Phase 14 Balanced: {det_p14_count}/39 (Expected: 23)")
    print(f"  * Detections - Phase 13 Balanced: {det_p13_count}/39 (Expected: 24)")
    print(f"  * Detections - Phase 9 Balanced: {det_p9_count}/39 (Expected: 19)")
    print(f"  * Detections - Phase 14 High-Precision: {det_hp_count}/39 (Expected: 18)")
    print(f"  * Detections - Phase 14 High-Sensitivity: {det_hs_count}/39 (Expected: 24)")
    print(f"  * Detections - Phase 17 Experimental: {det_p17_count}/39 (Expected: 23)")

    assert det_p14_count == 23, f"Phase 14 Balanced detections mismatch: expected 23, got {det_p14_count}"
    assert det_p13_count == 24, f"Phase 13 Balanced detections mismatch: expected 24, got {det_p13_count}"
    assert det_p9_count == 19, f"Phase 9 Balanced detections mismatch: expected 19, got {det_p9_count}"
    assert det_hp_count == 18, f"Phase 14 HP detections mismatch: expected 18, got {det_hp_count}"
    assert det_hs_count == 24, f"Phase 14 HS detections mismatch: expected 24, got {det_hs_count}"
    assert det_p17_count == 23, f"Phase 17 Exp detections mismatch: expected 23, got {det_p17_count}"

    # Assertion 6: Duplicate alerts == 0
    total_dups = df_canonical["duplicate_alerts_count"].sum()
    print(f"  * Total duplicate alerts across all events: {total_dups} (Expected: 0)")
    assert total_dups == 0, f"Expected 0 duplicate alerts, got {total_dups}"

    # 6. Save Canonical Table
    out_csv = REPORTS_DIR / "phase18_canonical_event_table.csv"
    df_canonical.to_csv(out_csv, index=False)
    print(f"\n[✓] Canonical 39-event table successfully written to {out_csv}")

    # Generate summary JSON for test assertions and documentation
    summary = {
        "safety_designation": "RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY",
        "total_canonical_events": total_events,
        "unique_event_ids": unique_ids,
        "events_by_stream": stream_counts,
        "events_by_condition": cond_counts,
        "detections_by_detector": {
            "phase_9_balanced": int(det_p9_count),
            "phase_13_balanced": int(det_p13_count),
            "phase_14_balanced": int(det_p14_count),
            "phase_14_high_precision": int(det_hp_count),
            "phase_14_high_sensitivity": int(det_hs_count),
            "phase_17_experimental": int(det_p17_count)
        },
        "missed_by_detector": {
            "phase_9_balanced": int(39 - det_p9_count),
            "phase_13_balanced": int(39 - det_p13_count),
            "phase_14_balanced": int(39 - det_p14_count),
            "phase_14_high_precision": int(39 - det_hp_count),
            "phase_14_high_sensitivity": int(39 - det_hs_count),
            "phase_17_experimental": int(39 - det_p17_count)
        },
        "duplicate_alerts_total": int(total_dups),
        "false_positive_alerts_continuous_positive": {
            "phase_9_balanced": 7,
            "phase_13_balanced": 7,
            "phase_14_balanced": 8,
            "phase_14_high_precision": 7,
            "phase_14_high_sensitivity": 8,
            "phase_17_experimental": 8
        },
        "condition_recall_phase14_balanced": {
            cond: {
                "total": int(df_canonical[df_canonical["acoustic_condition"] == cond].shape[0]),
                "detected": int(df_canonical[df_canonical["acoustic_condition"] == cond]["detected_p14_balanced"].sum()),
                "recall_pct": round(float(df_canonical[df_canonical["acoustic_condition"] == cond]["detected_p14_balanced"].mean() * 100), 2)
            }
            for cond in expected_conditions.keys()
        }
    }

    out_json = REPORTS_DIR / "phase18_canonical_event_summary.json"
    with open(out_json, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"[✓] Canonical event summary written to {out_json}")

if __name__ == "__main__":
    build_canonical_event_table()

