# PHASE 42 AUDIT REPORT: POSITIVE AUDIO DEDUPLICATION & RECALL SENSITIVITY

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
2. Reduces detected True Positives by exactly 1 ($k 	o k - 1$).
3. Leaves False Negative count completely unchanged ($FN = 119 - (k - 1) = 120 - k$).
4. Leaves duplicate alert count completely unchanged.

---

## 3. Entry-Level ($N=120$) vs. Deduplicated ($N=119$) Sensitivity Comparison

| Condition ID | Architecture / Model Profile | Entry-Level Recall ($N=120$) | Entry-Level 95% CI | Deduplicated Recall ($N=119$) | Deduplicated 95% CI | Recall $\Delta$ | Entry Dup Alert Rate | Dedup Dup Alert Rate |
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
   $$\text{COND2} (76.5\%) > \text{COND3-6} (63.9\%) > \text{COND1} (61.3\%)$$
3. **Dual Reporting Requirement:** To maintain uncompromising forensic hygiene, all authoritative benchmark tables in Phase 42 report both Entry-Level ($N=120$) and Deduplicated ($N=119$) figures.

---

## 5. Artifact Provenance
- Positive deduplication CSV: [`phase42_positive_deduplication_audit.csv`](file:///E:/gunshot/gunshot/experiments/phase42/phase42_positive_deduplication_audit.csv)
