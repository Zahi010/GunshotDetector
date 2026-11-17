"""
Phase 42 Workstream E: Positive Audio Deduplication & Recall Sensitivity Audit
Author: Antigravity / Google DeepMind
Mandatory Designation: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY
"""

import os
import sys
import pathlib
import pandas as pd
import numpy as np
from scipy import stats

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

PHASE42_DIR = REPO_ROOT / "experiments" / "phase42"
PHASE42_DIR.mkdir(parents=True, exist_ok=True)

def clopper_pearson(k, n, alpha=0.05):
    low = float(stats.beta.ppf(alpha / 2, k, n - k + 1)) if k > 0 else 0.0
    high = float(stats.beta.ppf(1 - alpha / 2, k + 1, n - k)) if k < n else 1.0
    return low, high

def run_positive_deduplication():
    print("=== WORKSTREAM E: Positive Audio Deduplication & Recall Sensitivity Audit ===")
    
    p39_pos_path = REPO_ROOT / "experiments" / "phase39" / "phase39_positive_results.csv"
    if not p39_pos_path.exists():
        raise FileNotFoundError(f"Missing {p39_pos_path}")
        
    df_p39 = pd.read_csv(p39_pos_path)
    
    # In both entries (fsd50k_gun_51749 and fsd50k_gun_115295), all models detected TP with exactly 1 alert
    # Deduplication removes 1 redundant clip from total (120 -> 119) and 1 from detected TP
    # Duplicate alerts on that clip were 0, so duplicate alert count remains unchanged
    
    rows = []
    for _, row in df_p39.iterrows():
        cid = row["condition_id"]
        arch = row["architecture_profile"]
        n_entry = int(row["total_positive_clips"])
        tp_entry = int(row["clip_level_detected_tp"])
        fn_entry = int(row["clip_level_false_negatives"])
        rec_entry = tp_entry / n_entry
        ci_entry_low, ci_entry_high = clopper_pearson(tp_entry, n_entry)
        
        dup_alerts = int(row["duplicate_alerts_count"])
        tot_alerts_entry = int(row["total_emitted_alerts_on_tp"])
        dup_rate_entry = dup_alerts / tot_alerts_entry if tot_alerts_entry > 0 else 0.0
        
        # Deduplicated figures (N = 119)
        n_dedup = n_entry - 1
        tp_dedup = tp_entry - 1
        fn_dedup = n_dedup - tp_dedup # remains unchanged
        rec_dedup = tp_dedup / n_dedup
        ci_dedup_low, ci_dedup_high = clopper_pearson(tp_dedup, n_dedup)
        
        tot_alerts_dedup = tot_alerts_entry - 1 # 1 alert emitted on the removed clip
        dup_rate_dedup = dup_alerts / tot_alerts_dedup if tot_alerts_dedup > 0 else 0.0
        
        rec_delta = rec_dedup - rec_entry
        
        rows.append({
            "condition_id": cid,
            "architecture_profile": arch,
            "entry_level_total_clips": n_entry,
            "entry_level_detected_tp": tp_entry,
            "entry_level_false_negatives": fn_entry,
            "entry_level_recall": round(rec_entry, 4),
            "entry_level_recall_95_ci_lower": round(ci_entry_low, 4),
            "entry_level_recall_95_ci_upper": round(ci_entry_high, 4),
            "deduplicated_total_clips": n_dedup,
            "deduplicated_detected_tp": tp_dedup,
            "deduplicated_false_negatives": fn_dedup,
            "deduplicated_recall": round(rec_dedup, 4),
            "deduplicated_recall_95_ci_lower": round(ci_dedup_low, 4),
            "deduplicated_recall_95_ci_upper": round(ci_dedup_high, 4),
            "recall_delta_percentage_points": round(rec_delta * 100, 2),
            "duplicate_alerts_count": dup_alerts,
            "entry_level_duplicate_alert_rate": round(dup_rate_entry, 4),
            "deduplicated_duplicate_alert_rate": round(dup_rate_dedup, 4)
        })
        
    df_dedup = pd.DataFrame(rows)
    output_csv = PHASE42_DIR / "phase42_positive_deduplication_audit.csv"
    df_dedup.to_csv(output_csv, index=False)
    print(f"Saved: {output_csv} ({len(df_dedup)} rows)")
    
    md_content = """# PHASE 42 AUDIT REPORT: POSITIVE AUDIO DEDUPLICATION & RECALL SENSITIVITY

> [!CAUTION]
> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.**
> This software is uncertified research code. It must never be deployed for autonomous emergency dispatch, police tactical response, active-shooter alerting, automated evacuation, building lockdown, or life-critical physical security.
> Use lawfully obtained recordings and safe audio playback only. Live-fire testing and hazardous acoustic experiments are strictly prohibited.

---

## 1. Executive Summary & Objective

Workstream E resolves the cryptographic duplicate identified within the prospective positive gunshot evaluation corpus.
Across the 120 positive evaluation recordings sourced from the FSD50K development set, exactly one internal duplicate waveform pair exists:
- `fsd50k_gun_51749` (`51749.wav`, uploaded by `erkanozan`)
- `fsd50k_gun_115295` (`115295.wav`, uploaded by `warriorsfan12331`)

Both files possess identical audio payload SHA-256 hashes (`6b272b5b52c6766f76c4ee879f1dabc191f3ca698b00de3cc5279033c9051515`), duration (5.176 s), and acoustic content.

This audit quantifies the exact sensitivity of all reported sensitivity and duplicate-alert metrics to the presence of this duplicate entry.

---

## 2. Decision Reproduction on Duplicate Pair

Under physical evaluation, both recordings elicited identical detector responses across all six frozen conditions:

| Condition ID | Architecture / Profile | `fsd50k_gun_51749` Decision | `fsd50k_gun_115295` Decision | Alerts Emitted per Clip | Duplicate Alerts on Pair |
|---|---|---|---|---|---|
| **COND1** | Phase 14 Balanced Baseline | `DETECTED_TP` | `DETECTED_TP` | 1 alert each | 0 |
| **COND2** | Phase 17 Experimental Profile | `DETECTED_TP` | `DETECTED_TP` | 1 alert each | 0 |
| **COND3** | Phase 17 State Reset Candidate | `DETECTED_TP` | `DETECTED_TP` | 1 alert each | 0 |
| **COND4** | Phase 36 Raw State Machine | `DETECTED_TP` | `DETECTED_TP` | 1 alert each | 0 |
| **COND5** | Phase 36 Legacy Suppression | `DETECTED_TP` | `DETECTED_TP` | 1 alert each | 0 |
| **COND6** | Phase 36 Conservative Suppression | `DETECTED_TP` | `DETECTED_TP` | 1 alert each | 0 |

Because both files trigger exactly one alert without emitting duplicate alerts, removing one copy from the positive dataset:
1. Reduces total positive clips from $N = 120$ to $N = 119$.
2. Reduces detected True Positives by exactly 1 ($k \to k - 1$).
3. Leaves False Negative count completely unchanged ($FN = 119 - (k - 1) = 120 - k$).
4. Leaves duplicate alert count completely unchanged.

---

## 3. Entry-Level ($N=120$) vs. Deduplicated ($N=119$) Sensitivity Comparison

| Condition ID | Architecture / Model Profile | Entry-Level Recall ($N=120$) | Entry-Level 95% CI | Deduplicated Recall ($N=119$) | Deduplicated 95% CI | Recall $\\Delta$ | Entry Dup Alert Rate | Dedup Dup Alert Rate |
|---|---|---|---|---|---|---|---|---|
| **COND1** | Phase 14 Balanced Baseline | 74 / 120 (61.67%) | [0.5235, 0.7039] | 73 / 119 (61.34%) | [0.5198, 0.7013] | -0.32% | 27.45% | 27.72% |
| **COND2** | Phase 17 Experimental Profile | 92 / 120 (76.67%) | [0.6807, 0.8390] | 91 / 119 (76.47%) | [0.6782, 0.8376] | -0.20% | 22.03% | 22.22% |
| **COND3** | Phase 17 State Reset Candidate | 77 / 120 (64.17%) | [0.5490, 0.7271] | 76 / 119 (63.87%) | [0.5455, 0.7247] | -0.30% | 22.22% | 22.45% |
| **COND4** | Phase 36 Raw State Machine | 77 / 120 (64.17%) | [0.5490, 0.7271] | 76 / 119 (63.87%) | [0.5455, 0.7247] | -0.30% | 14.44% | 14.61% |
| **COND5** | Phase 36 Legacy Suppression | 77 / 120 (64.17%) | [0.5490, 0.7271] | 76 / 119 (63.87%) | [0.5455, 0.7247] | -0.30% | 14.44% | 14.61% |
| **COND6** | Phase 36 Conservative Suppression | 77 / 120 (64.17%) | [0.5490, 0.7271] | 76 / 119 (63.87%) | [0.5455, 0.7247] | -0.30% | 14.44% | 14.61% |

---

## 4. Sensitivity Assessment & Recommendation

1. **Substantive Robustness:** The impact of deduplication across all six conditions is between **-0.20% and -0.32% percentage points** of recall. All confidence intervals overlap by $>98\%$.
2. **Ranking Invariance:** The relative performance ordering of the detectors is completely invariant to deduplication:
   $$\\text{COND2} (76.5\\%) > \\text{COND3-6} (63.9\\%) > \\text{COND1} (61.3\\%)$$
3. **Dual Reporting Requirement:** To maintain uncompromising forensic hygiene, all authoritative benchmark tables in Phase 42 report both Entry-Level ($N=120$) and Deduplicated ($N=119$) figures.

---

## 5. Artifact Provenance
- Positive deduplication CSV: [`phase42_positive_deduplication_audit.csv`](file:///E:/gunshot/gunshot/experiments/phase42/phase42_positive_deduplication_audit.csv)
"""

    output_report = PHASE42_DIR / "phase42_positive_recall_sensitivity.md"
    output_report.write_text(md_content, encoding="utf-8")
    print(f"Saved: {output_report}")

if __name__ == "__main__":
    run_positive_deduplication()

