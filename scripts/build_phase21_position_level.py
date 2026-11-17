"""
Phase 21 Firing-Position-Level Analysis
MANDATORY SAFETY DESIGNATION:
RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.

Calculates round-level and recording-level performance broken down by each of the
five surveyed urban street intersections (FP1 through FP5).
Outputs reports/phase21_position_level_results.csv.
"""

from pathlib import Path
import pandas as pd

ROOT = Path("E:/gunshot/gunshot")
REPORTS_DIR = ROOT / "reports"

hier_path = REPORTS_DIR / "phase21_event_cluster_hierarchy.csv"
rec_path = REPORTS_DIR / "phase21_recording_level_results.csv"

df_hier = pd.read_csv(hier_path)
df_rec = pd.read_csv(rec_path)

pos_rows = []
for fp, grp in df_hier.groupby("level_2_firing_position", sort=True):
    pos_rec = df_rec[df_rec["firing_position"] == fp]
    
    total_rounds = len(grp)
    p14_det = int(grp["level_7_phase_14_detected"].sum())
    p14_miss = total_rounds - p14_det
    p17_det = int(grp["level_7_phase_17_detected"].sum())
    p17_miss = total_rounds - p17_det
    
    p14_rec = round(p14_det / total_rounds, 4)
    p17_rec = round(p17_det / total_rounds, 4)
    diff_rec = round(p17_rec - p14_rec, 4)
    diff_count = p17_det - p14_det
    
    num_streams = len(pos_rec)
    num_single = (pos_rec["sequence_type"] == "SINGLE_SHOT").sum()
    num_burst = (pos_rec["sequence_type"] == "3_ROUND_BURST").sum()
    
    p14_inc_det = int(pos_rec["phase_14_incident_detected"].sum())
    p17_inc_det = int(pos_rec["phase_17_incident_detected"].sum())
    
    pos_rows.append({
        "firing_position": fp,
        "campaign_id": "PittsburghPA_DQV_2018-12-18",
        "physical_rounds_total": total_rounds,
        "recording_streams_total": num_streams,
        "single_shot_streams": num_single,
        "burst_streams": num_burst,
        "phase_14_detected_rounds": p14_det,
        "phase_14_missed_rounds": p14_miss,
        "phase_14_round_recall": p14_rec,
        "phase_17_detected_rounds": p17_det,
        "phase_17_missed_rounds": p17_miss,
        "phase_17_round_recall": p17_rec,
        "round_recall_difference": diff_rec,
        "round_detection_gain": diff_count,
        "phase_14_incidents_detected": p14_inc_det,
        "phase_17_incidents_detected": p17_inc_det,
        "incident_detection_gain": p17_inc_det - p14_inc_det,
        "gain_distribution_share_pct": round(diff_count / 6.0 * 100.0, 2),
        "position_concentration_verdict": "CONCENTRATED_HIGH_GAIN" if diff_count >= 3 else ("MODERATE_GAIN" if diff_count > 0 else "ZERO_GAIN_IDENTICAL_PERFORMANCE")
    })

df_pos = pd.DataFrame(pos_rows)
out_csv = REPORTS_DIR / "phase21_position_level_results.csv"
df_pos.to_csv(out_csv, index=False)
print(f"Saved position-level results to: {out_csv} ({len(df_pos)} positions)")
print(df_pos[["firing_position", "phase_14_detected_rounds", "phase_17_detected_rounds", "round_detection_gain", "gain_distribution_share_pct", "position_concentration_verdict"]].to_string())

# Verification
assert len(df_pos) == 5
assert df_pos["physical_rounds_total"].sum() == 50
assert df_pos["round_detection_gain"].sum() == 6
assert df_pos[df_pos["firing_position"] == "FP4"]["round_detection_gain"].iloc[0] == 3
assert df_pos[df_pos["firing_position"] == "FP2"]["round_detection_gain"].iloc[0] == 0
assert df_pos[df_pos["firing_position"] == "FP5"]["round_detection_gain"].iloc[0] == 0
print("Position-level assertions passed successfully.")

