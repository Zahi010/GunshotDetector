"""
Phase 21 Event-Level Reproduction & Paired Contingency Audit
MANDATORY SAFETY DESIGNATION:
RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.

Loads canonical 50-event Pittsburgh dataset, reproduces paired event-level contingency table,
computes exact two-sided binomial McNemar test, and exports:
- reports/phase21_event_level_reproduction.csv
- reports/phase21_event_contingency.json
- reports/phase21_event_level_statistics.md
"""

import json
from pathlib import Path
import pandas as pd
from scipy import stats

ROOT = Path("E:/gunshot/gunshot")
REPORTS_DIR = ROOT / "reports"

# Load canonical event manifest
manifest_path = REPORTS_DIR / "phase20_canonical_event_manifest.csv"
df = pd.read_csv(manifest_path)
cat_a = df[df["category"] == "CATEGORY_A_NATURAL_CONTINUOUS"].copy()
assert len(cat_a) == 50, f"Expected 50 Category A events, got {len(cat_a)}"

# Verification of event fields
repro_rows = []
for _, r in cat_a.iterrows():
    p14 = bool(r["phase_14_balanced_detected"])
    p17 = bool(r["phase_17_experimental_detected"])
    
    if p14 and p17:
        pair_state = "BOTH_DETECTED"
    elif p14 and not p17:
        pair_state = "PHASE14_ONLY"
    elif not p14 and p17:
        pair_state = "PHASE17_ONLY"
    else:
        pair_state = "NEITHER_DETECTED"
        
    repro_rows.append({
        "event_id": r["event_id"],
        "stream_id": r["stream_id"],
        "firing_position": r["firing_position"],
        "firearm_category": r["firearm_category"],
        "ground_truth_round_timestamp": r["ground_truth_round_timestamp"],
        "snr_db": r["snr_db"],
        "spl_db": r["spl_db"],
        "phase_14_balanced_detected": p14,
        "phase_17_experimental_detected": p17,
        "pairing_classification": pair_state,
        "is_discordant": p14 != p17
    })

df_repro = pd.DataFrame(repro_rows)
out_csv = REPORTS_DIR / "phase21_event_level_reproduction.csv"
df_repro.to_csv(out_csv, index=False)
print(f"Saved event-level reproduction to: {out_csv}")

# Contingency Matrix
both = int(((df_repro["phase_14_balanced_detected"] == True) & (df_repro["phase_17_experimental_detected"] == True)).sum())
p14_only = int(((df_repro["phase_14_balanced_detected"] == True) & (df_repro["phase_17_experimental_detected"] == False)).sum())
p17_only = int(((df_repro["phase_14_balanced_detected"] == False) & (df_repro["phase_17_experimental_detected"] == True)).sum())
neither = int(((df_repro["phase_14_balanced_detected"] == False) & (df_repro["phase_17_experimental_detected"] == False)).sum())

assert both == 27, f"Expected both=27, got {both}"
assert p14_only == 0, f"Expected p14_only=0, got {p14_only}"
assert p17_only == 6, f"Expected p17_only=6, got {p17_only}"
assert neither == 17, f"Expected neither=17, got {neither}"

total_events = both + p14_only + p17_only + neither
assert total_events == 50

p14_recall = (both + p14_only) / total_events
p17_recall = (both + p17_only) / total_events
diff_recall = p17_recall - p14_recall

n_discordant = p14_only + p17_only
mcnemar_res = stats.binomtest(min(p14_only, p17_only), n_discordant, 0.5, alternative='two-sided')
p_value = mcnemar_res.pvalue

assert abs(p_value - 0.03125) < 0.0001

contingency_data = {
    "safety_designation": "RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY",
    "evaluation_scope": "Category A (ShotSpotter Pittsburgh PA DQV 2018)",
    "total_physical_rounds": total_events,
    "contingency_table": {
        "cell_a_both_detected": both,
        "cell_b_phase14_only": p14_only,
        "cell_c_phase17_only": p17_only,
        "cell_d_neither_detected": neither
    },
    "model_metrics": {
        "phase_14_balanced": {
            "detected_rounds": both + p14_only,
            "total_rounds": total_events,
            "round_recall": p14_recall,
            "round_recall_percent": round(p14_recall * 100.0, 2)
        },
        "phase_17_experimental": {
            "detected_rounds": both + p17_only,
            "total_rounds": total_events,
            "round_recall": p17_recall,
            "round_recall_percent": round(p17_recall * 100.0, 2)
        },
        "absolute_recall_difference_pp": round(diff_recall * 100.0, 2)
    },
    "hypothesis_testing": {
        "test_name": "Exact Two-Sided Binomial McNemar Test",
        "null_hypothesis": "Marginal homogeneity: discordant events are equally likely under Phase 14 and Phase 17 (p=0.5)",
        "total_discordant_pairs": n_discordant,
        "discordant_b": p14_only,
        "discordant_c": p17_only,
        "exact_two_sided_p_value": round(float(p_value), 5),
        "statistically_significant_alpha_05": bool(p_value < 0.05),
        "reproduction_status": "EXACT_REPRODUCTION_VERIFIED"
    }
}

out_json = REPORTS_DIR / "phase21_event_contingency.json"
with open(out_json, "w", encoding="utf-8") as f:
    json.dump(contingency_data, f, indent=2, ensure_ascii=False)
print(f"Saved event contingency JSON to: {out_json}")

# Markdown report
md_content = f"""# Phase 21: Unadjusted Event-Level Reproduction & Paired Contingency Analysis

> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY**  
> *This experimental acoustic machine-learning system is not certified and must never be used for autonomous emergency dispatch, police response, active-shooter alerting, automated evacuation, or critical physical security. Use legally obtained recorded audio and safe playback only. No live-fire testing or hazardous acoustic experiments.*

---

## 1. Executive Summary

Phase 21 verifies the unadjusted event-level detection performance of the default baseline (**Phase 14 Balanced**) versus the experimental candidate (**Phase 17 Experimental**) on the 50 canonical physical gunshot rounds of Category A (ShotSpotter Pittsburgh PA DQV 2018).

This reproduction confirms:
1. Exact replication of the $2 \\times 2$ event-level contingency matrix:
   - **Both detected:** 27 rounds ($54.0\\%$)
   - **Phase 14 only detected:** 0 rounds ($0.0\\%$)
   - **Phase 17 only detected:** 6 rounds ($12.0\\%$)
   - **Neither detected:** 17 rounds ($34.0\\%$)
2. Overall round recall:
   - **Phase 14 Balanced:** $54.00\\%$ (27 of 50 rounds)
   - **Phase 17 Experimental:** $66.00\\%$ (33 of 50 rounds)
   - **Absolute Difference:** $+12.00$ percentage points
3. Exact two-sided binomial McNemar $p$-value:
   $$p = 2 \\cdot \\binom{{6}}{{0}} (0.5)^6 = 2 \\cdot \\frac{{1}}{{64}} = 0.03125$$
   The unadjusted event-level result is verified as statistically significant at $\\alpha = 0.05$.

---

## 2. Paired Event-Level Contingency Table

```
                           Phase 17 Experimental
                           Detected     Missed     Total
Phase 14       Detected       27           0         27  (54.0%)
Balanced       Missed          6          17         23  (46.0%)
               Total          33          17         50  (100.0%)
                            (66.0%)     (34.0%)
```

### Discordant Pair Characterization
The 6 discordant events ($b=0, c=6$) where Phase 17 detected a gunshot missed by Phase 14 are:
1. `P19-CAT-A-FP1-test_004-EV01`: FP1, single shot, $t=3.562\\text{{ s}}$ (.45 ACP Handgun)
2. `P19-CAT-A-FP1-test_013-EV01`: FP1, burst round 1, $t=3.763\\text{{ s}}$ (9x19mm Handgun)
3. `P19-CAT-A-FP3-test_037-EV01`: FP3, burst round 1, $t=2.828\\text{{ s}}$ (.45 ACP Handgun)
4. `P19-CAT-A-FP4-test_055-EV03`: FP4, burst round 3, $t=4.603\\text{{ s}}$ (.45 ACP Handgun)
5. `P19-CAT-A-FP4-test_067-EV01`: FP4, burst round 1, $t=3.786\\text{{ s}}$ (9x19mm Handgun)
6. `P19-CAT-A-FP4-test_067-EV02`: FP4, burst round 2, $t=4.311\\text{{ s}}$ (9x19mm Handgun)

Crucially, **Phase 14 never detected an event that Phase 17 missed** ($b = 0$).

---

## 3. Assumptions and Vulnerabilities of the Event-Level McNemar Test

The exact McNemar test relies on the fundamental assumption that **each paired observation is independent and identically distributed (i.i.d.)**.
In the Pittsburgh dataset, this assumption is severely challenged by physical clustering:
- **Hierarchical Nesting:** The 50 rounds are nested within only 20 recordings, 5 firing positions, and 1 municipal testing campaign.
- **Acoustic Covariance:** Multiple rounds in the same recording share identical propagation geometry, building facades, atmospheric temperature, and sensor hardware.
- **Refractory Interaction:** Successive rounds in three-round bursts occur within milliseconds, interacting directly with detector cooldown logic.

Consequently, while $p = 0.03125$ is the exact mathematical result under the i.i.d. event assumption, cluster-aware validation is essential to evaluate the true stability of this effect.

---
*Report certified under Phase 21 Forensic Audit protocol.*
"""

out_md = REPORTS_DIR / "phase21_event_level_statistics.md"
with open(out_md, "w", encoding="utf-8") as f:
    f.write(md_content)
print(f"Saved event-level statistics markdown to: {out_md}")
