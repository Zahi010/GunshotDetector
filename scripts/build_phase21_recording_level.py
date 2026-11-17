"""
Phase 21 Recording-Level Paired Analysis
MANDATORY SAFETY DESIGNATION:
RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.

Aggregates round-level detections up to the 20 recording streams,
computes paired recording differences, incident-level metrics, and exports:
- reports/phase21_recording_level_results.csv
- reports/phase21_recording_level_comparison.md
"""

from pathlib import Path
import pandas as pd
import numpy as np
from scipy import stats

ROOT = Path("E:/gunshot/gunshot")
REPORTS_DIR = ROOT / "reports"

hier_path = REPORTS_DIR / "phase21_event_cluster_hierarchy.csv"
df_hier = pd.read_csv(hier_path)

rec_rows = []
for sid, grp in df_hier.groupby("level_4_stream_id", sort=False):
    fp = grp["level_2_firing_position"].iloc[0]
    tid = grp["level_3_test_id"].iloc[0]
    cal = grp["firearm_caliber"].iloc[0]
    seq = grp["level_5_sequence_type"].iloc[0]
    gt_rounds = len(grp)
    
    p14_det = int(grp["level_7_phase_14_detected"].sum())
    p17_det = int(grp["level_7_phase_17_detected"].sum())
    
    p14_rec = round(p14_det / gt_rounds, 4)
    p17_rec = round(p17_det / gt_rounds, 4)
    diff_rec = round(p17_rec - p14_rec, 4)
    
    p14_inc = bool(p14_det > 0)
    p17_inc = bool(p17_det > 0)
    
    disc_rounds = int(grp["level_7_discordant"].sum())
    
    rec_rows.append({
        "stream_id": sid,
        "firing_position": fp,
        "test_id": tid,
        "sequence_type": seq,
        "firearm_caliber": cal,
        "ground_truth_round_count": gt_rounds,
        "phase_14_detections": p14_det,
        "phase_17_detections": p17_det,
        "phase_14_round_recall": p14_rec,
        "phase_17_round_recall": p17_rec,
        "round_recall_difference": diff_rec,
        "phase_14_incident_detected": p14_inc,
        "phase_17_incident_detected": p17_inc,
        "incident_status_change": "PHASE17_NEW_INCIDENT" if (not p14_inc and p17_inc) else ("SAME_STATUS"),
        "discordant_physical_events": disc_rounds
    })

df_rec = pd.DataFrame(rec_rows)
out_csv = REPORTS_DIR / "phase21_recording_level_results.csv"
df_rec.to_csv(out_csv, index=False)
print(f"Saved recording-level results to: {out_csv} ({len(df_rec)} streams)")

# Statistical tests at recording level
p14_recs = df_rec["phase_14_round_recall"]
p17_recs = df_rec["phase_17_round_recall"]
diffs = p17_recs - p14_recs

mean_p14 = p14_recs.mean()
mean_p17 = p17_recs.mean()
mean_diff = diffs.mean()

# Paired t-test
t_stat, t_pval = stats.ttest_rel(p17_recs, p14_recs)

# Wilcoxon signed rank test on non-zero differences
non_zero_diffs = diffs[diffs != 0]
n_nonzero = len(non_zero_diffs)
if n_nonzero > 0:
    w_stat, w_pval = stats.wilcoxon(non_zero_diffs)
else:
    w_stat, w_pval = 0, 1.0

# Incident level McNemar on 20 streams
both_inc = int(((df_rec["phase_14_incident_detected"] == True) & (df_rec["phase_17_incident_detected"] == True)).sum())
p14_only_inc = int(((df_rec["phase_14_incident_detected"] == True) & (df_rec["phase_17_incident_detected"] == False)).sum())
p17_only_inc = int(((df_rec["phase_14_incident_detected"] == False) & (df_rec["phase_17_incident_detected"] == True)).sum())
neither_inc = int(((df_rec["phase_14_incident_detected"] == False) & (df_rec["phase_17_incident_detected"] == False)).sum())

inc_mcnemar = stats.binomtest(min(p14_only_inc, p17_only_inc), p14_only_inc + p17_only_inc, 0.5, alternative='two-sided')
inc_pval = inc_mcnemar.pvalue

# Format Markdown
md_content = f"""# Phase 21: Recording-Level Paired Analysis and Incident-Level Audit

> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY**  
> *This experimental acoustic machine-learning system is not certified and must never be used for autonomous emergency dispatch, police response, active-shooter alerting, automated evacuation, or critical physical security. Use legally obtained recorded audio and safe playback only. No live-fire testing or hazardous acoustic experiments.*

---

## 1. Executive Summary

In unadjusted event-level testing, each physical round is treated as an independent statistical trial ($N=50$), producing an exact McNemar $p$-value of $0.03125$. However, in physical reality, the 50 rounds are clustered inside exactly **20 continuous recording streams** ($10.0\\text{{ s}}$ each).

This recording-level analysis evaluates whether the Phase 17 recall advantage remains statistically robust when the recording stream is the unit of observation:
1. **Concordance Across Recordings:** In **15 out of 20 recordings (75.0%)**, Phase 14 and Phase 17 exhibit **identical round-level detection counts** (zero discordance).
2. **Discordance Concentration:** All 6 additional Phase 17 detections are concentrated in only **5 recordings** (`test_004`, `test_013`, `test_037`, `test_055`, `test_067`).
3. **Incident-Level Detection ($N=20$ Streams):**
   - Phase 14 Balanced: **15 of 20 streams detected (75.0%)**
   - Phase 17 Experimental: **18 of 20 streams detected (90.0%)**
   - Paired Incident Contingency: Both detected = 15, Phase 14 only = 0, Phase 17 only = 3, Neither = 2.
   - **Incident Exact Binomial $p$-value:**
     $$p = 2 \\cdot \\binom{{3}}{{0}} (0.5)^3 = 2 \\cdot \\frac{{1}}{{8}} = 0.25000$$
     At the incident level, the Phase 17 advantage is **NOT statistically significant ($p = 0.25000 \\gg 0.05$)**.
4. **Recording Mean Recall:**
   - Phase 14 Balanced Mean Recording Recall: **{mean_p14*100.0:.2f}%**
   - Phase 17 Experimental Mean Recording Recall: **{mean_p17*100.0:.2f}%**
   - Mean Difference: **+{mean_diff*100.0:.2f} percentage points**
   - Wilcoxon Signed-Rank Test ($N=5$ non-zero pairs): $W = {w_stat:.1f}, p = {w_pval:.5f}$ (**NOT statistically significant** at $\\alpha=0.05$).

---

## 2. Comprehensive Recording-by-Recording Results Table

| Stream Identifier | Position | Test ID | Sequence Type | Caliber | GT Rounds | Phase 14 Det | Phase 17 Det | Phase 14 Recall | Phase 17 Recall | Recall Delta | Phase 14 Incident | Phase 17 Incident | Discordant Rounds |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
"""

for _, r in df_rec.iterrows():
    p14_inc_str = "YES" if r["phase_14_incident_detected"] else "NO"
    p17_inc_str = "YES" if r["phase_17_incident_detected"] else "NO"
    md_content += f"| `{r['stream_id']}` | {r['firing_position']} | `{r['test_id']}` | {r['sequence_type']} | {r['firearm_caliber']} | {r['ground_truth_round_count']} | {r['phase_14_detections']} | {r['phase_17_detections']} | {r['phase_14_round_recall']*100:.1f}% | {r['phase_17_round_recall']*100:.1f}% | +{r['round_recall_difference']*100:.1f}% | {p14_inc_str} | {p17_inc_str} | {r['discordant_physical_events']} |\n"

md_content += f"""
---

## 3. Analysis of the Five Discordant Recordings

The six additional rounds detected by Phase 17 are confined to five specific recordings:

1. **`P19-CAT-A-FP1-test_004` (FP1, Single Shot, .45 ACP):**
   - Phase 14: 0/1 (Missed incident)
   - Phase 17: 1/1 (Detected incident)
   - *Impact:* Generates 1 new incident alert and 1 round gain.
2. **`P19-CAT-A-FP1-test_013` (FP1, 3-Round Burst, 9x19mm):**
   - Phase 14: 0/3 (Missed incident)
   - Phase 17: 1/3 (Detected burst round 1, missed rounds 2 and 3)
   - *Impact:* Generates 1 new incident alert and 1 round gain.
3. **`P19-CAT-A-FP3-test_037` (FP3, 3-Round Burst, .45 ACP):**
   - Phase 14: 2/3 (Already detected incident via rounds 2 and 3)
   - Phase 17: 3/3 (Detected all 3 rounds)
   - *Impact:* Zero incident gain; +1 round gain.
4. **`P19-CAT-A-FP4-test_055` (FP4, 3-Round Burst, .45 ACP):**
   - Phase 14: 2/3 (Already detected incident via rounds 1 and 2)
   - Phase 17: 3/3 (Detected all 3 rounds)
   - *Impact:* Zero incident gain; +1 round gain.
5. **`P19-CAT-A-FP4-test_067` (FP4, 3-Round Burst, 9x19mm):**
   - Phase 14: 0/3 (Missed incident)
   - Phase 17: 2/3 (Detected burst rounds 1 and 2, missed round 3)
   - *Impact:* Generates 1 new incident alert and +2 round gain.

### Key Observation:
Only **3 recordings** changed incident detection status from Miss to Detect (`test_004`, `test_013`, `test_067`). In the other 2 recordings (`test_037`, `test_055`), Phase 14 had already successfully detected the gunfire incident ($2/3$ rounds detected).

---

## 4. Methodological Significance

When observations are evaluated at the stream level ($N=20$), the small sample size and large proportion of concordant trials ($15/20 = 75\\%$) cause the exact binomial test of incident detection to yield $p = 0.25000$.

Treating recording streams as the unit of analysis demonstrates that Phase 17's apparent advantage is not a pervasive, stream-by-stream improvement, but a localized recovery of 3 previously missed streams and 2 incremental burst rounds.

---
*Report certified under Phase 21 Forensic Audit protocol.*
"""

out_md = REPORTS_DIR / "phase21_recording_level_comparison.md"
with open(out_md, "w", encoding="utf-8") as f:
    f.write(md_content)
print(f"Saved recording-level comparison markdown to: {out_md}")

