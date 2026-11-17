"""
Phase 21 Event Cluster Hierarchy Generator
MANDATORY SAFETY DESIGNATION:
RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.

Constructs full 7-level nesting hierarchy for all 50 physical rounds in Category A:
1. Municipal testing campaign
2. Firing position
3. Original test identifier
4. Original sensor recording
5. Burst or firing sequence
6. Physical round in sequence
7. Detector alert status (Phase 14 & Phase 17)

Outputs reports/phase21_event_cluster_hierarchy.csv.
"""

from pathlib import Path
import pandas as pd

ROOT = Path("E:/gunshot/gunshot")
REPORTS_DIR = ROOT / "reports"

manifest_path = REPORTS_DIR / "phase20_canonical_event_manifest.csv"
continuity_path = REPORTS_DIR / "phase20_continuity_audit.csv"

df = pd.read_csv(manifest_path)
cat_a = df[df["category"] == "CATEGORY_A_NATURAL_CONTINUOUS"].copy()
df_cont = pd.read_csv(continuity_path)

cont_map = {r["stream_id"]: r for _, r in df_cont.iterrows()}

hierarchy_rows = []

# Group by stream to determine round ordering
for sid, grp in cat_a.groupby("stream_id", sort=False):
    grp_sorted = grp.sort_values("ground_truth_round_timestamp")
    total_rounds = len(grp_sorted)
    seq_type = "SINGLE_SHOT" if total_rounds == 1 else f"{total_rounds}_ROUND_BURST"
    c_info = cont_map.get(sid, {})
    
    for round_idx, (_, r) in enumerate(grp_sorted.iterrows(), start=1):
        if total_rounds == 1:
            round_role = "SINGLE_ROUND"
        elif round_idx == 1:
            round_role = "BURST_LEADING_ROUND"
        elif round_idx == total_rounds:
            round_role = "BURST_TRAILING_ROUND"
        else:
            round_role = "BURST_INTERMEDIATE_ROUND"
            
        hierarchy_rows.append({
            "event_id": r["event_id"],
            "level_1_campaign_id": "PittsburghPA_DQV_2018-12-18",
            "level_1_campaign_name": "ShotSpotter City of Pittsburgh Bureau of Police Annual DQV",
            "level_1_campaign_date": "2018-12-18 / 2018-12-19",
            "level_2_firing_position": r["firing_position"],
            "level_2_position_origin_status": "Arbitrary Cartesian Local Origin",
            "level_3_test_id": r["original_source_test_id"],
            "level_4_stream_id": sid,
            "level_4_original_sensor_file": r["original_sensor_file"],
            "level_4_sensor_serial": c_info.get("sensor_serial_number", 2476),
            "level_4_stream_duration_s": 10.0,
            "level_5_sequence_type": seq_type,
            "level_5_total_rounds_in_sequence": total_rounds,
            "level_6_physical_round_index": round_idx,
            "level_6_round_role": round_role,
            "level_6_ground_truth_timestamp_s": r["ground_truth_round_timestamp"],
            "firearm_caliber": r["firearm_category"],
            "snr_db": r["snr_db"],
            "spl_db": r["spl_db"],
            "level_7_phase_14_detected": bool(r["phase_14_balanced_detected"]),
            "level_7_phase_17_detected": bool(r["phase_17_experimental_detected"]),
            "level_7_discordant": bool(r["phase_14_balanced_detected"]) != bool(r["phase_17_experimental_detected"]),
            "level_7_discordance_direction": "PHASE17_ONLY" if (not r["phase_14_balanced_detected"] and r["phase_17_experimental_detected"]) else ("PHASE14_ONLY" if (r["phase_14_balanced_detected"] and not r["phase_17_experimental_detected"]) else "CONCORDANT")
        })

df_hier = pd.DataFrame(hierarchy_rows)
out_csv = REPORTS_DIR / "phase21_event_cluster_hierarchy.csv"
df_hier.to_csv(out_csv, index=False)
print(f"Saved event cluster hierarchy to: {out_csv} ({len(df_hier)} rows)")

# Assertions
assert len(df_hier) == 50
assert len(df_hier["level_2_firing_position"].unique()) == 5
assert len(df_hier["level_4_stream_id"].unique()) == 20
assert (df_hier["level_5_sequence_type"] == "SINGLE_SHOT").sum() == 5
assert (df_hier["level_5_sequence_type"] == "3_ROUND_BURST").sum() == 45
assert df_hier["level_7_discordant"].sum() == 6
print("Cluster hierarchy assertions passed successfully.")

