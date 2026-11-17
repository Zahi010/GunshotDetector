# PHASE 37 FINAL FORENSIC AUDIT REPORT
## Dataset Lineage, Evaluation Independence & Multi-Condition Ablation Audit

> [!CAUTION]
> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.**
> This experimental acoustic machine-learning software is uncertified and must never be deployed for autonomous emergency dispatch, police tactical response, active-shooter alerting, automated evacuation, building lockdown, or life-critical physical security.
> Use legally obtained recordings and safe audio playback only. Live-fire testing and hazardous acoustic experiments are strictly prohibited.

---

## 1. Executive Summary

Phase 37 conducted an exhaustive, independent forensic audit of the newly established experimental research branch (`experiments/phase36/`) and its evaluation claims.

### Definitive Audit Findings:

1. **Dataset Lineage & Evaluation Independence (`REPEATED_HISTORICAL_EVALUATION`):**
   - **0 out of 87 recordings (0.0%)** in the Phase 36 evaluation corpus were new out-of-sample acquisitions.
   - **87 out of 87 recordings (100.0%)** were exact SHA-256 bit-for-bit matches to pre-existing files in the repository.
   - All 23 positive recordings and all 53 annotated ballistic rounds were identical to the normalized corpus evaluated in Phases 19, 20, 21, and 32 (ShotSpotter Pittsburgh DQV 2018).
   - Zero overlap with the 23-stream continuous negative benchmark did **not** establish dataset independence; Phase 36 was a multi-dataset regression re-evaluation on historical assets.
2. **Suppression Ablation & Behavioral Divergence (`TRACE_VERIFIED`):**
   - The suppression engine in COND4 (Raw), COND5 (Legacy), and COND6 (Conservative) was actively wired and functioning.
   - Exactly **23 transition windows** in continuous audio experienced active score attenuation.
   - Aggregate metrics were identical because every single attenuated window had an unsuppressed score that was **already below operating thresholds** ($s < 0.48$ or $s < 0.75$). Thus, internal numerical divergence occurred without flipping any state transition boundary.
3. **Ballistic Event Matching & Sensitivity Parity (`REPRODUCED`):**
   - Phase 36 achieved **16 True Positives out of 53 rounds ($30.19\%\text{ Recall}$)**, matching Phase 14 Balanced exactly. **Phase 36 did not improve ballistic sensitivity.**
   - Phase 36 improved Precision from **$80.00\%$ to $84.21\%$** (16 TP, 3 FP vs 16 TP, 4 FP) and reduced duplicate alerts from 2 to 1.
4. **Continuous Background Exposure & Cooldown Integrity (`REPRODUCED`):**
   - Phase 14 Balanced: 68 alerts ($13.6000/\text{hr}$ gross FAR, $306.16\text{ s}$ Conv B excluded).
   - Phase 17 Defective: 145 alerts ($29.0000/\text{hr}$ gross FAR, $5,131.36\text{ s}$ Conv B excluded) due to candidate leakage.
   - Phase 36 Experimental: 66 alerts ($13.2000/\text{hr}$ gross FAR, $300.48\text{ s}$ Conv B excluded).
5. **Latency Measurement Scope (`MEASUREMENT_SCOPE_MISCLASSIFICATION`):**
   - The reported $4.38\text{ ms}$ latency in Phase 36 measured **per-file wall-clock execution on pre-extracted feature caches**, not per-window acoustic inference.
   - Combined post-processing (FSM + suppression) takes **$0.0138\text{ ms}$** per window. True end-to-end inference including YAMNet and ensemble classifiers takes **$\sim 5.85\text{ ms}$** per 0.96s window on CPU.
6. **Archive Provenance Reconciled (`VERIFIED FROM FILES`):**
   - The Phase 34/35 hash collision was traced to a text copy-paste transposition in historical prompts. The physical on-disk files are distinct, intact, and pass CRC verification.

---

## 2. Factorial Experiment Reproduction Summary

| Condition ID | Architecture / Model | Continuous Gross FAR (/hr) | Conv B Excluded (s) | Positive Recall (53 Rounds) | Positive Precision | Positive F1 | Distractor Trigger Rate (60 Clips) | Audit Status |
|:---:|---|:---:|:---:|:---:|:---:|:---:|:---:|---|
| **`COND1`** | Phase 14 Balanced Baseline | **13.6000** | 306.16 | **30.2% (16/53)** | **80.0%** | **0.4384** | 10.0% (6/60) | `REPRODUCED` |
| **`COND2`** | Phase 17 Experimental Frozen Profile | **29.0000** | 5,131.36 | **35.9% (19/53)\*** | **82.6%** | **0.5000** | 10.0% (6/60) | `REPRODUCED` |
| **`COND3`** | Phase 17 Reset Candidate | **13.6000** | 306.16 | **32.1% (17/53)** | **85.0%** | **0.4658** | 10.0% (6/60) | `REPRODUCED` |
| **`COND4`** | Phase 36 Raw State Machine | **13.2000** | 300.48 | **30.2% (16/53)** | **84.2%** | **0.4444** | 10.0% (6/60) | `REPRODUCED` |
| **`COND5`** | Phase 36 Legacy Suppression | **13.2000** | 300.48 | **30.2% (16/53)** | **84.2%** | **0.4444** | 10.0% (6/60) | `REPRODUCED` |
| **`COND6`** | Phase 36 Conservative | **13.2000** | 300.48 | **30.2% (16/53)** | **84.2%** | **0.4444** | 10.0% (6/60) | `REPRODUCED` |

*\*Note: Phase 17's apparent 35.9% recall is driven by unconfirmed candidate leakage at recording boundaries.*

---

## 3. Deliverables and Audit Directory Table

All Phase 37 audit deliverables are preserved under `experiments/phase37/`:

| Deliverable Name | Local File Link | Description |
|---|---|---|
| **Dataset Lineage Registry** | [phase37_dataset_lineage.csv](file:///E:/gunshot/gunshot/experiments/phase37/phase37_dataset_lineage.csv) | Full audit of all 87 evaluation recordings and historical phase provenance |
| **Dataset Independence Report** | [phase37_dataset_independence_report.md](file:///E:/gunshot/gunshot/experiments/phase37/phase37_dataset_independence_report.md) | Forensic evaluation of dataset overlap and independence claims |
| **Suppression Ablation Audit** | [phase37_suppression_ablation_audit.csv](file:///E:/gunshot/gunshot/experiments/phase37/phase37_suppression_ablation_audit.csv) | Analysis of all 23 attenuated transition windows |
| **Condition Pairwise Comparison** | [phase37_condition_pairwise_comparison.csv](file:///E:/gunshot/gunshot/experiments/phase37/phase37_condition_pairwise_comparison.csv) | Direct pairwise metric and transition deltas across conditions |
| **Ablation Findings Report** | [phase37_ablation_findings.md](file:///E:/gunshot/gunshot/experiments/phase37/phase37_ablation_findings.md) | Detailed explanation of sub-threshold score attenuation |
| **Ballistic Matching Audit** | [phase37_ballistic_matching_audit.csv](file:///E:/gunshot/gunshot/experiments/phase37/phase37_ballistic_matching_audit.csv) | Round-by-round detection audit across 53 annotated ballistic events |
| **Ballistic Metrics Report** | [phase37_ballistic_metrics_reproduction.md](file:///E:/gunshot/gunshot/experiments/phase37/phase37_ballistic_metrics_reproduction.md) | Independent reproduction of TP, FP, FN, precision, recall, and duplicate rates |
| **Background Reproduction CSV** | [phase37_background_metrics_reproduction.csv](file:///E:/gunshot/gunshot/experiments/phase37/phase37_background_metrics_reproduction.csv) | Per-recording continuous ambient exposure and Poisson 95% CIs |
| **Background Audit Report** | [phase37_background_audit.md](file:///E:/gunshot/gunshot/experiments/phase37/phase37_background_audit.md) | Convention A and B exposure analysis and false alert rates |
| **Latency Audit Report** | [phase37_latency_audit.md](file:///E:/gunshot/gunshot/experiments/phase37/phase37_latency_audit.md) | Measurement scope audit and component-level micro-benchmarks |
| **Archive Provenance Audit** | [phase37_archive_provenance_audit.md](file:///E:/gunshot/gunshot/experiments/phase37/phase37_archive_provenance_audit.md) | Resolution of Phase 34/35/36 ZIP byte size and SHA-256 hashes |
| **Input Hash Manifest** | [phase37_input_hash_manifest.json](file:///E:/gunshot/gunshot/experiments/phase37/phase37_input_hash_manifest.json) | Pre-audit SHA-256 baseline hashes |
| **Output Hash Manifest** | [phase37_output_hash_manifest.json](file:///E:/gunshot/gunshot/experiments/phase37/phase37_output_hash_manifest.json) | Post-audit SHA-256 manifest of generated audit artifacts |

---

## 4. Final Governance & Research Directives

1. **Phase 14 Balanced** remains the authoritative **Default Research Baseline** (`DEFAULT_RESEARCH_BASELINE`).
2. **Phase 17 Experimental** remains a frozen **Selectable Experimental Profile** (`SELECTABLE_EXPERIMENTAL_PROFILE`).
3. **Phase 31 State Reset Candidate** remains a **Quarantined Diagnostic Reference** (`QUARANTINED_DIAGNOSTIC_REFERENCE`).
4. **Phase 36** is confirmed as an active **Experimental Research Branch** (`PHASE36_EXPERIMENTAL_EVENT_STATE_BRANCH_V1`). While it successfully cures state-machine candidate leakage and improves precision, its evaluation was conducted on historical repository data and its recall remains identical to Phase 14 ($30.19\%$).
5. **Phase 36 must remain an experimental branch.** Any future promotion would require genuinely independent, prospectively collected out-of-sample field validation.
6. **No Life-Safety Deployment:** Uncertified experimental demonstration prototype only.
