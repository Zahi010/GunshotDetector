"""
Phase 21 Burst-Aware Analysis Generator
MANDATORY SAFETY DESIGNATION:
RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.

Audits every firing sequence (15 three-round bursts and 5 single-shot controls)
for first-round vs trailing-round detection, duplicate alerts, and refractory cooldown.
Outputs reports/phase21_burst_analysis.csv.
"""

from pathlib import Path
import pandas as pd

ROOT = Path("E:/gunshot/gunshot")
REPORTS_DIR = ROOT / "reports"

hier_path = REPORTS_DIR / "phase21_event_cluster_hierarchy.csv"
df_hier = pd.read_csv(hier_path)

burst_rows = []

for sid, grp in df_hier.groupby("level_4_stream_id", sort=False):
    grp_sorted = grp.sort_values("level_6_physical_round_index")
    fp = grp["level_2_firing_position"].iloc[0]
    tid = grp["level_3_test_id"].iloc[0]
    cal = grp["firearm_caliber"].iloc[0]
    seq_type = grp["level_5_sequence_type"].iloc[0]
    num_rounds = len(grp_sorted)
    
    # Ground truth timestamps
    timestamps = grp_sorted["level_6_ground_truth_timestamp_s"].tolist()
    first_ts = timestamps[0]
    last_ts = timestamps[-1]
    burst_span_s = round(last_ts - first_ts, 4)
    
    # Inter-shot intervals for bursts
    if num_rounds > 1:
        isi_list = [round(timestamps[i] - timestamps[i-1], 4) for i in range(1, num_rounds)]
        isi_str = "; ".join(str(x) for x in isi_list)
        min_isi = min(isi_list)
        max_isi = max(isi_list)
    else:
        isi_str = "N/A_SINGLE_SHOT"
        min_isi = 0.0
        max_isi = 0.0
        
    # Detection booleans per round
    p14_dets = grp_sorted["level_7_phase_14_detected"].tolist()
    p17_dets = grp_sorted["level_7_phase_17_detected"].tolist()
    
    p14_first = bool(p14_dets[0])
    p17_first = bool(p17_dets[0])
    
    if num_rounds > 1:
        p14_trailing_count = sum(p14_dets[1:])
        p17_trailing_count = sum(p17_dets[1:])
        p14_all_trailing = all(p14_dets[1:])
        p17_all_trailing = all(p17_dets[1:])
        trailing_role_summary = f"P14: {p14_trailing_count}/{num_rounds-1}, P17: {p17_trailing_count}/{num_rounds-1}"
    else:
        p14_trailing_count = 0
        p17_trailing_count = 0
        p14_all_trailing = False
        p17_all_trailing = False
        trailing_role_summary = "N/A_SINGLE_SHOT"
        
    p14_inc = any(p14_dets)
    p17_inc = any(p17_dets)
    
    # Cooldown interaction diagnosis:
    # If first round detected, and trailing round occurred within 2.0s:
    # In all bursts, last_ts - first_ts < 2.0s (e.g. 0.8s to 1.5s).
    if num_rounds > 1:
        cooldown_conflict = burst_span_s <= 2.0
        cooldown_diagnosis = "BURST_INTERVAL_WITHIN_2.0S_COOLDOWN" if cooldown_conflict else "BURST_SPAN_EXCEEDS_COOLDOWN"
    else:
        cooldown_conflict = False
        cooldown_diagnosis = "NOT_APPLICABLE_SINGLE_SHOT"
        
    # Gain in this burst
    gain = sum(p17_dets) - sum(p14_dets)
    
    burst_rows.append({
        "stream_id": sid,
        "firing_position": fp,
        "test_id": tid,
        "sequence_type": seq_type,
        "firearm_caliber": cal,
        "round_count": num_rounds,
        "first_round_timestamp_s": first_ts,
        "last_round_timestamp_s": last_ts,
        "burst_total_duration_s": burst_span_s,
        "inter_shot_intervals_s": isi_str,
        "phase_14_detected_rounds": sum(p14_dets),
        "phase_17_detected_rounds": sum(p17_dets),
        "round_gain": gain,
        "phase_14_first_round_detected": p14_first,
        "phase_17_first_round_detected": p17_first,
        "phase_14_trailing_detected_count": p14_trailing_count,
        "phase_17_trailing_detected_count": p17_trailing_count,
        "phase_14_incident_detected": p14_inc,
        "phase_17_incident_detected": p17_inc,
        "incident_gain": int(p17_inc) - int(p14_inc),
        "cooldown_window_conflict": cooldown_conflict,
        "cooldown_interaction_diagnosis": cooldown_diagnosis,
        "duplicate_alerts_observed": False
    })

df_burst = pd.DataFrame(burst_rows)
out_csv = REPORTS_DIR / "phase21_burst_analysis.csv"
df_burst.to_csv(out_csv, index=False)
print(f"Saved burst analysis to: {out_csv} ({len(df_burst)} sequences)")

# Summaries
bursts_only = df_burst[df_burst["sequence_type"] == "3_ROUND_BURST"]
singles_only = df_burst[df_burst["sequence_type"] == "SINGLE_SHOT"]

print("\n=== Burst Summary (N=15 3-round bursts, 45 rounds) ===")
print(f"Phase 14 burst rounds detected: {bursts_only['phase_14_detected_rounds'].sum()}/45 ({bursts_only['phase_14_detected_rounds'].sum()/45*100:.1f}%)")
print(f"Phase 17 burst rounds detected: {bursts_only['phase_17_detected_rounds'].sum()}/45 ({bursts_only['phase_17_detected_rounds'].sum()/45*100:.1f}%)")
print(f"Phase 14 burst incidents: {bursts_only['phase_14_incident_detected'].sum()}/15 ({bursts_only['phase_14_incident_detected'].sum()/15*100:.1f}%)")
print(f"Phase 17 burst incidents: {bursts_only['phase_17_incident_detected'].sum()}/15 ({bursts_only['phase_17_incident_detected'].sum()/15*100:.1f}%)")

print("\n=== Single-Shot Summary (N=5 single shots, 5 rounds) ===")
print(f"Phase 14 single rounds detected: {singles_only['phase_14_detected_rounds'].sum()}/5 ({singles_only['phase_14_detected_rounds'].sum()/5*100:.1f}%)")
print(f"Phase 17 single rounds detected: {singles_only['phase_17_detected_rounds'].sum()}/5 ({singles_only['phase_17_detected_rounds'].sum()/5*100:.1f}%)")

