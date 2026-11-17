# Phase 21: Category D (Mitchell Range 2015) Recall Discrepancy Reconciliation

> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY**  
> *This experimental acoustic machine-learning system is not certified and must never be used for autonomous emergency dispatch, police response, active-shooter alerting, automated evacuation, or critical physical security. Use legally obtained recorded audio and safe playback only. No live-fire testing or hazardous acoustic experiments.*

---

## 1. Executive Summary

A metric discrepancy was identified between project reports:
- **Phase 19 Report:** Reported Category D recall as **$83.33\%$**.
- **Phase 20 Cross-Category Report:** Reported Category D recall as **$89.3\%$** for Phase 14 Balanced.

This forensic audit inspected all historical evaluation manifests, model profiles, and event denominators from Phases 15 through 20. 

### Core Audit Finding:
Both numbers are physically authentic historical evaluation outputs, but they represent **different model profiles** and **different evaluation denominators**:
1. **$83.33\%$ ($35 / 42$)** is the exact round-level recall of **Phase 14 Balanced** on the comprehensive 42-clip Mitchell range set (Category D in Phase 19).
2. **$89.29\% \approx 89.3\%$ ($25 / 28$)** is the event recall of **Phase 14 High-Sensitivity** on the 28-event blind discrete test set (Phase 15/16).
3. In Phase 20's `phase20_cross_category_interpretation.md`, the author mistakenly copied the High-Sensitivity figure ($89.3\%$) into the table row for Phase 14 Balanced. On that same 28-event set, Phase 14 Balanced achieved **$75.00\%$ ($21 / 28$)**.
4. Furthermore, **$83.33\%$** also appeared in Phase 15 as the event precision of Phase 14 High-Sensitivity ($25/30$) and as Phase 14 Balanced recall on ADC-clipped waveforms ($5/6$).

---

## 2. Forensic Reconciliation Matrix

| Metric Value | Authentic Source Phase | Evaluated Model Profile | Denominator ($N$) | Detected ($TP$) | True Metric Identity | Status & Context |
| :---: | :---: | :--- | :---: | :---: | :--- | :--- |
| **83.33%** | Phase 19 | **Phase 14 Balanced** | **42 clips** | **35** | **Category D Event Recall** | **CANONICAL BASELINE:** Comprehensive Mitchell 2015 range benchmark ($35/42 = 83.33\%$). |
| **89.29% (~89.3%)** | Phase 15 & 16 | **Phase 14 High-Sensitivity** | **28 events** | **25** | High-Sensitivity Event Recall | **PROFILE CONFLATION:** Belongs to High-Sensitivity profile, NOT Balanced profile. |
| **75.00%** | Phase 15 & 16 | **Phase 14 Balanced** | **28 events** | **21** | Balanced Event Recall | Balanced profile recall on the 28-event discrete blind set. |
| **83.33%** | Phase 15 & 16 | **Phase 14 High-Sensitivity** | **30 alerts** | **25** | Event Precision | High-Sensitivity event precision ($25 / (25+5) = 83.33\%$). |
| **83.33%** | Phase 15 | **Phase 14 Balanced** | **6 clips** | **5** | Clipped Sub-Recall | Clipped ADC-saturated ballistic recordings ($5/6 = 83.33\%$). |

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

1. **Category D (Mitchell 2015 Range Sets):** **$83.33\%$** ($35/42$ rounds detected). Close-mic open field with shared lineage.
2. **Category C (Calibrated Spliced Audio):** **$69.70\%$** ($23/33$ rounds detected). Semi-synthetic benchmark.
3. **Category A (ShotSpotter Pittsburgh PA DQV):** **$54.00\%$** ($27/50$ rounds detected). Controlled urban live-fire validation.
4. **Category B (External Pre-Cropped Clips):** **$33.33\%$** ($1/3$ rounds detected). Uncalibrated field captures.

---

## 4. Audit Sign-Off

- Discrepancy successfully resolved.
- Root cause traced to profile conflation between Phase 14 Balanced and High-Sensitivity.
- Correct canonical metrics archived in `reports/phase21_category_d_corrected_metrics.json`.

---
*Report certified under Phase 21 Forensic Audit protocol.*
