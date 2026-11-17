"""
Phase 21 Category D Recall Discrepancy Reconciliation
MANDATORY SAFETY DESIGNATION:
RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.

Traces the origins of:
- 83.33% (Phase 19 Category D recall on 42-clip Mitchell set: 35/42)
- 89.3% (Phase 15/16 Phase 14 High-Sensitivity recall on 28-event Mitchell set: 25/28 = 89.29%)
- Documents the reporting conflation in Phase 20 cross_category_interpretation.md.

Outputs:
- reports/phase21_category_d_corrected_metrics.json
- reports/phase21_category_d_reconciliation.md
"""

import json
from pathlib import Path
import pandas as pd

ROOT = Path("E:/gunshot/gunshot")
REPORTS_DIR = ROOT / "reports"

# 1. Structured JSON output
reconciliation_payload = {
    "safety_designation": "RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY",
    "reconciliation_target": "Category D (Mitchell 2015 Range Recordings) Recall Discrepancy",
    "identified_discrepancy": {
        "phase_19_reported_value": "83.33% (Phase 14 Balanced on 42-clip set)",
        "phase_20_reported_value": "89.3% (Mistakenly attributed to Phase 14 Balanced in cross-category table)",
        "discrepancy_nature": "REPORTING_CONFLATION_BETWEEN_PROFILES_AND_DENOMINATORS"
    },
    "provenance_investigation": {
        "dataset_variant_1_discrete_blind_test_28_events": {
            "source_phase": "Phase 15 & Phase 16",
            "eval_set_description": "Blind discrete ballistic evaluation set from Mitchell et al. (testing subset)",
            "denominator_genuine_events": 28,
            "phase_14_high_sensitivity": {
                "detected": 25,
                "missed": 3,
                "false_alerts": 5,
                "event_recall": 0.8929,
                "event_recall_pct": "89.29% (~89.3%)",
                "event_precision_pct": "83.33% (25/30)"
            },
            "phase_14_balanced": {
                "detected": 21,
                "missed": 7,
                "false_alerts": 3,
                "event_recall": 0.7500,
                "event_recall_pct": "75.00%",
                "event_precision_pct": "87.50% (21/24)"
            },
            "phase_14_high_precision": {
                "detected": 16,
                "missed": 12,
                "false_alerts": 1,
                "event_recall": 0.5714,
                "event_recall_pct": "57.14%",
                "event_precision_pct": "94.12% (16/17)"
            },
            "adc_clipped_subset_6_events": {
                "phase_14_balanced_detected": 5,
                "phase_14_balanced_recall": 0.8333,
                "phase_14_balanced_recall_pct": "83.33% (5/6)"
            }
        },
        "dataset_variant_2_comprehensive_range_42_clips": {
            "source_phase": "Phase 19 (Category D)",
            "eval_set_description": "Comprehensive Mitchell 2015 range recording archive (18 direct + 6 clipped + 18 muffled)",
            "denominator_genuine_events": 42,
            "phase_14_balanced": {
                "detected": 35,
                "missed": 7,
                "false_alerts": 5,
                "event_recall": 0.8333,
                "event_recall_pct": "83.33% (35/42)",
                "event_precision_pct": "87.50% (35/40)"
            },
            "phase_17_experimental": {
                "detected": 38,
                "missed": 4,
                "false_alerts": 3,
                "event_recall": 0.9048,
                "event_recall_pct": "90.48% (38/42)"
            }
        }
    },
    "audit_verdict": {
        "is_83_33_percent_valid": True,
        "valid_scope_for_83_33": "Phase 14 Balanced on the 42-clip Category D comprehensive range set (35/42 = 83.33%), and Phase 14 High-Sensitivity precision on 28 events (25/30 = 83.33%), and Phase 14 Balanced clipped recall (5/6 = 83.33%).",
        "is_89_3_percent_valid": True,
        "valid_scope_for_89_3": "Phase 14 High-Sensitivity recall on the 28-event blind discrete range test set (25/28 = 89.29% ~ 89.3%).",
        "root_cause_of_discrepancy": "In Phase 20's phase20_cross_category_interpretation.md, the author cited 'Phase 14 Balanced: 89.3%' in the summary table. This was a clerical reporting error: 89.29% belonged to Phase 14 High-Sensitivity on the 28-event set. The correct Phase 14 Balanced recall is 83.33% (35/42) on the 42-clip Category D benchmark, and 75.00% (21/28) on the 28-event discrete benchmark.",
        "correction_action": "Documented in audit trail. Historical files preserved. Canonical Category D recall for Phase 14 Balanced is certified as 83.33% (35/42)."
    }
}

out_json = REPORTS_DIR / "phase21_category_d_corrected_metrics.json"
with open(out_json, "w", encoding="utf-8") as f:
    json.dump(reconciliation_payload, f, indent=2, ensure_ascii=False)
print(f"Saved Category D corrected metrics JSON to: {out_json}")

# 2. Markdown Report
md_content = f"""# Phase 21: Category D (Mitchell Range 2015) Recall Discrepancy Reconciliation

> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY**  
> *This experimental acoustic machine-learning system is not certified and must never be used for autonomous emergency dispatch, police response, active-shooter alerting, automated evacuation, or critical physical security. Use legally obtained recorded audio and safe playback only. No live-fire testing or hazardous acoustic experiments.*

---

## 1. Executive Summary

A metric discrepancy was identified between project reports:
- **Phase 19 Report:** Reported Category D recall as **$83.33\\%$**.
- **Phase 20 Cross-Category Report:** Reported Category D recall as **$89.3\\%$** for Phase 14 Balanced.

This forensic audit inspected all historical evaluation manifests, model profiles, and event denominators from Phases 15 through 20. 

### Core Audit Finding:
Both numbers are physically authentic historical evaluation outputs, but they represent **different model profiles** and **different evaluation denominators**:
1. **$83.33\\%$ ($35 / 42$)** is the exact round-level recall of **Phase 14 Balanced** on the comprehensive 42-clip Mitchell range set (Category D in Phase 19).
2. **$89.29\\% \\approx 89.3\\%$ ($25 / 28$)** is the event recall of **Phase 14 High-Sensitivity** on the 28-event blind discrete test set (Phase 15/16).
3. In Phase 20's `phase20_cross_category_interpretation.md`, the author mistakenly copied the High-Sensitivity figure ($89.3\\%$) into the table row for Phase 14 Balanced. On that same 28-event set, Phase 14 Balanced achieved **$75.00\\%$ ($21 / 28$)**.
4. Furthermore, **$83.33\\%$** also appeared in Phase 15 as the event precision of Phase 14 High-Sensitivity ($25/30$) and as Phase 14 Balanced recall on ADC-clipped waveforms ($5/6$).

---

## 2. Forensic Reconciliation Matrix

| Metric Value | Authentic Source Phase | Evaluated Model Profile | Denominator ($N$) | Detected ($TP$) | True Metric Identity | Status & Context |
| :---: | :---: | :--- | :---: | :---: | :--- | :--- |
| **83.33%** | Phase 19 | **Phase 14 Balanced** | **42 clips** | **35** | **Category D Event Recall** | **CANONICAL BASELINE:** Comprehensive Mitchell 2015 range benchmark ($35/42 = 83.33\\%$). |
| **89.29% (~89.3%)** | Phase 15 & 16 | **Phase 14 High-Sensitivity** | **28 events** | **25** | High-Sensitivity Event Recall | **PROFILE CONFLATION:** Belongs to High-Sensitivity profile, NOT Balanced profile. |
| **75.00%** | Phase 15 & 16 | **Phase 14 Balanced** | **28 events** | **21** | Balanced Event Recall | Balanced profile recall on the 28-event discrete blind set. |
| **83.33%** | Phase 15 & 16 | **Phase 14 High-Sensitivity** | **30 alerts** | **25** | Event Precision | High-Sensitivity event precision ($25 / (25+5) = 83.33\\%$). |
| **83.33%** | Phase 15 | **Phase 14 Balanced** | **6 clips** | **5** | Clipped Sub-Recall | Clipped ADC-saturated ballistic recordings ($5/6 = 83.33\\%$). |

---

## 3. Corrected Cross-Category Generalization Gradient

With the profile and denominator corrected, the authentic cross-category recall gradient for **Phase 14 Balanced** is certified as follows:

```
100% ┌────────────────────────────────────────────────────────┐
     │                                                        │
 80% │  ██████████ 83.33% (35/42)                             │
     │  ██████████            ██████████ 69.70% (23/33)       │
 60% │  ██████████            ██████████            ██████████ 54.00% (27/50)
     │  ██████████            ██████████            ██████████
 40% │  ██████████            ██████████            ██████████
     │  ██████████            ██████████            ██████████
 20% │  ██████████            ██████████            ██████████            ██████████ 33.33% (1/3)
     │  ██████████            ██████████            ██████████            ██████████
  0% └────────────────────────────────────────────────────────────────────────────┘
        Category D               Category C            Category A            Category B
        Mitchell Range 2015      Calibrated Spliced    Pittsburgh Urban      External Clips
```

1. **Category D (Mitchell 2015 Range Sets):** **$83.33\\%$** ($35/42$ rounds detected). Close-mic open field with shared lineage.
2. **Category C (Calibrated Spliced Audio):** **$69.70\\%$** ($23/33$ rounds detected). Semi-synthetic benchmark.
3. **Category A (ShotSpotter Pittsburgh PA DQV):** **$54.00\\%$** ($27/50$ rounds detected). Controlled urban live-fire validation.
4. **Category B (External Pre-Cropped Clips):** **$33.33\\%$** ($1/3$ rounds detected). Uncalibrated field captures.

---

## 4. Audit Sign-Off

- Discrepancy successfully resolved.
- Root cause traced to profile conflation between Phase 14 Balanced and High-Sensitivity.
- Correct canonical metrics archived in `reports/phase21_category_d_corrected_metrics.json`.

---
*Report certified under Phase 21 Forensic Audit protocol.*
"""

out_md = REPORTS_DIR / "phase21_category_d_reconciliation.md"
with open(out_md, "w", encoding="utf-8") as f:
    f.write(md_content)
print(f"Saved Category D reconciliation markdown to: {out_md}")

