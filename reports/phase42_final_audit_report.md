# PHASE 42 FINAL FORENSIC AUDIT REPORT
## Benchmark Denominator Reconciliation, Forensic Inconsistency Resolution & Independent Statistical Validation

> [!CAUTION]
> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.**
> This software is uncertified research code. It must never be deployed for autonomous emergency dispatch, police tactical response, active-shooter alerting, automated evacuation, building lockdown, or life-critical physical security.
> Use lawfully obtained recordings and safe audio playback only. Live-fire testing and hazardous acoustic experiments are strictly prohibited.

---

## 1. Executive Summary & Governance Scope

Phase 42 was conducted as a strict, read-only forensic audit and statistical reconciliation of the prospective gunshot detection benchmarks established in Phases 38–41.
No detector logic was modified, no models were retrained, no thresholds were altered, and all frozen baseline implementations were maintained without mutation.

### Core Governance Classifications:
- **Phase 14 Balanced Baseline:** **`DEFAULT_RESEARCH_BASELINE`** (Verified authoritative reference).
- **Phase 17 Experimental Profile:** **`SELECTABLE_EXPERIMENTAL_PROFILE`** (Quarantined diagnostic profile exhibiting candidate accumulation defect).
- **Phase 31 State Reset Candidate:** **`QUARANTINED_DIAGNOSTIC_REFERENCE`** (Diagnostic demonstration of candidate flush on sub-threshold decay).
- **Phase 36 Experimental Architecture:** **`EXPERIMENTAL_RESEARCH_BRANCH_V1`** (Experimental research branch; **DO NOT PROMOTE** to production baseline).

---

## 2. Workstream A — Continuous Exposure Denominator Reconciliation

### The Problem:
Prior reports contained an apparent conflict between two reported evaluation durations:
- **17,786.33 seconds (4.9406 hours)** vs. **15,185.60 seconds (4.2182 hours)**.

### Forensic Finding:
The difference of **2,600.73 seconds (0.7224 hours)** is the exact physical duration of the 340 short challenge clips evaluated alongside the continuous streams.

$$\begin{aligned}
\text{Continuous Ambient Streams (28 files)} &= 15,185.60\text{ s} \quad (4.2182\text{ hours}) \\
\text{Prospective Positive Clips (120 files)} &= 519.29\text{ s} \quad (0.1442\text{ hours}) \\
\text{Fireworks Challenge Clips (100 files)} &= 1,094.87\text{ s} \quad (0.3041\text{ hours}) \\
\text{Other Distractor Clips (120 files)} &= 986.56\text{ s} \quad (0.2740\text{ hours}) \\
\hline
\textbf{Total Evaluation Corpus (368 files)} &= \textbf{17,786.33 s} \quad (\textbf{4.9406 hours})
\end{aligned}$$

### Authoritative Resolution:
- **15,185.60 seconds (4.2182 hours)** is the **sole authoritative denominator** for prospective continuous ambient False Alarm Rate (FAR).
- All 28 continuous audio streams were decoded without frame loss or truncation and evaluated in full under all 6 conditions.
- Artifacts:
  - [phase42_continuous_exposure_reconciliation.csv](file:///E:/gunshot/gunshot/experiments/phase42/phase42_continuous_exposure_reconciliation.csv)
  - [phase42_stream_level_results.csv](file:///E:/gunshot/gunshot/experiments/phase42/phase42_stream_level_results.csv)
  - [phase42_continuous_reconciliation.md](file:///E:/gunshot/gunshot/experiments/phase42/phase42_continuous_reconciliation.md)

---

## 3. Workstream B — Phase 17 Fireworks Discrepancy Reconciliation

### The Problem:
Conflicting values were reported for Phase 17 false alarms on the 100 fireworks challenge clips:
- Phase 40 Pipeline reported **62 / 100**.
- Phase 41 Section 2 Master Table reported **58 / 100**.
- Underlying physical artifacts indicated different numbers.

### Forensic Finding & Physical Verification:
1. **The 62 / 100 Count (Phase 40):** An unverified **hardcoded script placeholder** in `scripts/execute_phase40_continuous_pipeline.py` (lines 174–177): `fw_trig = 57 if cid in ["COND4", "COND5", "COND6"] else (47 if cid == "COND1" else 62)`.
2. **The 58 / 100 Count (Phase 41):** A **typographical transcription error** in the Phase 41 summary table.
3. **Physical Ground Truth Execution:**
   - **`COND1` (`model_phase14.py`):** **47 / 100 triggers (47.0%)**
   - **`COND2` (`model_phase17.py`):** **71 / 100 triggers (71.0%)** (Matches `phase39_distractor_results.csv` exactly)
   - **`COND3` (`model_phase17_state_reset_candidate.py`):** **57 / 100 triggers (57.0%)**
   - **`COND6` (`model_phase36.py`):** **57 / 100 triggers (57.0%)**

### Causal Mechanism:
The 14-clip elevation from 57 to 71 in Phase 17 is caused entirely by the **candidate-accumulation defect**. In `model_phase17.py`, candidate detections that exceed $p \ge 0.75$ accumulate across long multi-burst files without resetting on sub-threshold decay. In `model_phase17_state_reset_candidate.py`, clearing the candidate buffer upon sub-threshold drop suppresses all 14 false alarms, reducing triggers to 57.
- Artifacts:
  - [phase42_fireworks_decision_reconciliation.csv](file:///E:/gunshot/gunshot/experiments/phase42/phase42_fireworks_decision_reconciliation.csv)
  - [phase42_fireworks_reconciliation.md](file:///E:/gunshot/gunshot/experiments/phase42/phase42_fireworks_reconciliation.md)

---

## 4. Workstream C — Confidence Interval Methodology & Physical Validity

### The Problem:
Phase 41 applied naive linear Wald intervals ($\hat{\lambda} \pm 1.96 \cdot \text{SE}_{\text{cluster}}$) to physical event rates, producing physically impossible **negative lower bounds** (e.g. COND1: $[-2.3085, 17.0067]\text{ alerts/hr}$).

### Authoritative Resolution:
Physical false alarm rates are bounded strictly below by zero ($\lambda \ge 0$). Phase 42 standardizes two valid interval formulations:
1. **Exact Poisson Confidence Intervals (Garwood Formula):** Strictly positive lower bounds for all $k > 0$.
2. **Log-Transformed Cluster-Robust Wald Intervals:** Variance estimated on $\theta = \log(\lambda)$ via delta method ($\text{CV} = \text{SE}_{\text{cluster}} / \hat{\lambda}$), exponentiated back to the rate scale:
   $$\left[ \hat{\lambda} \cdot \exp(-t_{18, 0.975} \cdot \text{CV}), \; \hat{\lambda} \cdot \exp(+t_{18, 0.975} \cdot \text{CV}) \right]$$
   Guaranteed strictly positive for all $\hat{\lambda} > 0$.

### Reconciled Continuous Ambient FAR Intervals (Exposure = 4.2182 hr):
| Condition | Gross Alerts | Gross FAR (alerts/hr) | Poisson Exact 95% CI | Defective Naive Wald CI (Phase 41) | Authoritative Log-Cluster Wald 95% CI |
|---|---|---|---|---|---|
| **COND1** | 31 | 7.3491 | [4.9933, 10.4314] | [-3.0027, 17.7009] (z: [-2.31, 17.01]) | **[1.7968, 30.0589]** |
| **COND2** | 104 | 24.6550 | [20.1449, 29.8736] | [-0.6306, 49.9405] | **[8.8410, 68.7553]** |
| **COND3** | 31 | 7.3491 | [4.9933, 10.4314] | [-3.0027, 17.7009] | **[1.7968, 30.0589]** |
| **COND6** | 26 | 6.1637 | [4.0264, 9.0313] | [-2.4984, 14.8259] | **[1.5119, 25.1290]** |

### Rate Difference Confidence Interval:
For the paired difference $\hat{\Delta} = \hat{\lambda}_{\text{COND1}} - \hat{\lambda}_{\text{COND6}} = 1.1853\text{ alerts/hr}$:
- $\text{SE}_{\Delta, \text{cluster}} = 0.8494$ ($df = 18, t_{\text{crit}} = 2.1009$)
- **95% CI for Difference:** **$[-0.5992, \; 2.9699]\text{ alerts/hr}$**
- Because this interval **contains zero**, the 5-alert difference between Phase 14 and Phase 36 is **NOT statistically significant**.
- Artifacts:
  - [phase42_confidence_interval_audit.csv](file:///E:/gunshot/gunshot/experiments/phase42/phase42_confidence_interval_audit.csv)
  - [phase42_statistical_methods.md](file:///E:/gunshot/gunshot/experiments/phase42/phase42_statistical_methods.md)

---

## 5. Workstream D — Recordist-Level Dependence & Exact Permutation Inference

### The Problem:
Phase 41 reported identical Wilcoxon signed-rank results at both stream level ($N=28$) and recordist level ($K=19$): $W = 0.0, p = 0.1025$.

### Forensic Finding:
1. **Proof of Mathematical Identity:** The Wilcoxon test prunes zero-difference pairs. Across all 28 streams, only 3 streams had discordant alert counts between COND1 and COND6:
   - `p38_cont_01_goussainville`: $\Delta = +1$ (Recordist: Vincent Duseigne)
   - `p40_cont_03_bruxelles`: $\Delta = +3$ (Recordist: Flavien Gillié)
   - `p40_cont_11_fukutsu_japan`: $\Delta = +1$ (Recordist: Thomas Martin Nutt)
   Because each of these 3 streams belonged to a different recordist and all other streams had zero differences, the non-zero difference set was **identical at both levels: $\{+1, +3, +1\}$**.
2. **Exact Permutation Test ($n=3$):**
   The reported asymptotic p-value of $p = 0.1025$ is invalid for $n=3$. Under an exact permutation test with $2^3 = 8$ possible sign outcomes:
   $$p_{\text{exact}} = \frac{2}{8} = \mathbf{0.2500}$$
   There is **no statistically significant evidence of superiority** for Phase 36 over Phase 14.
- Artifacts:
  - [phase42_recordist_analysis.csv](file:///E:/gunshot/gunshot/experiments/phase42/phase42_recordist_analysis.csv)
  - [phase42_cluster_inference_report.md](file:///E:/gunshot/gunshot/experiments/phase42/phase42_cluster_inference_report.md)

---

## 6. Workstream E — Positive Audio Deduplication & Recall Sensitivity

### Finding:
Across the 120 prospective positive clips, exactly one duplicate waveform pair exists: `fsd50k_gun_51749` and `fsd50k_gun_115295` share identical audio SHA-256 (`6b272b5b52c6766f76c4ee879f1dabc191f3ca698b00de3cc5279033c9051515`). Both clips triggered as True Positives with exactly 1 alert across all 6 conditions.

### Sensitivity Comparison:
- **Phase 14 Balanced Baseline (COND1):**
  - Entry-Level ($N=120$): **74 / 120 (61.67%)** [95% CI: 0.5235, 0.7039]
  - Deduplicated ($N=119$): **73 / 119 (61.34%)** [95% CI: 0.5198, 0.7013] ($\Delta = -0.32\%$)
- **Phase 36 Conservative Suppression (COND6):**
  - Entry-Level ($N=120$): **77 / 120 (64.17%)** [95% CI: 0.5490, 0.7271]
  - Deduplicated ($N=119$): **76 / 119 (63.87%)** [95% CI: 0.5455, 0.7247] ($\Delta = -0.30\%$)

The effect of deduplication is negligible ($< 0.35$ percentage points) and preserves detector ranking perfectly. Both metrics are officially standardized.
- Artifacts:
  - [phase42_positive_deduplication_audit.csv](file:///E:/gunshot/gunshot/experiments/phase42/phase42_positive_deduplication_audit.csv)
  - [phase42_positive_recall_sensitivity.md](file:///E:/gunshot/gunshot/experiments/phase42/phase42_positive_recall_sensitivity.md)

---

## 7. Workstream F — Crest-Factor Suppression Mechanism Validation

### The Hypothesis:
Phase 41 hypothesized that Phase 36 emitted 10 more fireworks false alarms than Phase 14 (57 vs. 47) because its 12.0 dB crest-factor gate permitted high-dynamic-range pyrotechnics to bypass suppression.

### Counterfactual Physical Simulation:
We tested all 10 discordant clips under counterfactual simulation with `crest_factor_db = 0.0 dB` (permanently deactivating the gate).
- **Result:** In **10 out of 10 clips (100.0%)**, Phase 36 emitted the exact same false alarms!
- **True Physical Cause:** Phase 36 semantic suppression is specific to animal vocalizations; animal scores were near zero on fireworks, so suppression was completely inactive. Alerts were triggered by multi-window CNN persistence ($\ge 2$ windows with raw score $\ge 0.75$). Phase 14 remained silent due to its strict consecutive buffer reset upon sub-threshold drop.
- **Classification:** The causal claim for the 12.0 dB crest gate is formally classified as **`NOT_ESTABLISHED`** (and refuted as a necessary condition).
- Artifacts:
  - [phase42_crest_factor_reconstruction.csv](file:///E:/gunshot/gunshot/experiments/phase42/phase42_crest_factor_reconstruction.csv)
  - [phase42_mechanism_validation.md](file:///E:/gunshot/gunshot/experiments/phase42/phase42_mechanism_validation.md)

---

## 8. Authoritative Benchmark Matrix

| Metric Name | Condition | Architecture Profile | Numerator | Denominator | Point Estimate | 95% Confidence Interval | Method |
|---|---|---|---|---|---|---|---|
| **Continuous Gross FAR** | COND1 | Phase 14 Balanced Baseline | 31 | 4.2182 hr | **7.3491 alerts/hr** | [1.7968, 30.0589] | Log-Cluster Wald |
| **Continuous Gross FAR** | COND2 | Phase 17 Experimental Profile | 104 | 4.2182 hr | **24.6550 alerts/hr** | [8.8410, 68.7553] | Log-Cluster Wald |
| **Continuous Gross FAR** | COND3 | Phase 17 State Reset Candidate | 31 | 4.2182 hr | **7.3491 alerts/hr** | [1.7968, 30.0589] | Log-Cluster Wald |
| **Continuous Gross FAR** | COND6 | Phase 36 Conservative Suppression | 26 | 4.2182 hr | **6.1637 alerts/hr** | [1.5119, 25.1290] | Log-Cluster Wald |
| **Convention B FAR** | COND1 | Phase 14 Balanced Baseline | 31 | 4.1847 hr | **7.4079 alerts/hr** | [1.8112, 30.2995] | Log-Cluster Wald |
| **Convention B FAR** | COND6 | Phase 36 Conservative Suppression | 26 | 4.1919 hr | **6.2024 alerts/hr** | [1.5214, 25.2869] | Log-Cluster Wald |
| **Positive Recall (Entry)** | COND1 | Phase 14 Balanced Baseline | 74 | 120 clips | **61.67%** | [0.5235, 0.7039] | Clopper-Pearson |
| **Positive Recall (Entry)** | COND6 | Phase 36 Conservative Suppression | 77 | 120 clips | **64.17%** | [0.5490, 0.7271] | Clopper-Pearson |
| **Positive Recall (Dedup)** | COND1 | Phase 14 Balanced Baseline | 73 | 119 clips | **61.34%** | [0.5198, 0.7013] | Clopper-Pearson |
| **Positive Recall (Dedup)** | COND6 | Phase 36 Conservative Suppression | 76 | 119 clips | **63.87%** | [0.5455, 0.7247] | Clopper-Pearson |
| **Duplicate Alert Rate** | COND1 | Phase 14 Balanced Baseline | 28 | 102 alerts | **27.45%** | N/A | Emitted / TP Alerts |
| **Duplicate Alert Rate** | COND6 | Phase 36 Conservative Suppression | 13 | 90 alerts | **14.44%** | N/A | Emitted / TP Alerts |
| **Fireworks False Triggers**| COND1 | Phase 14 Balanced Baseline | 47 | 100 clips | **47.0%** | [0.3694, 0.5724] | Clopper-Pearson |
| **Fireworks False Triggers**| COND2 | Phase 17 Experimental Profile | 71 | 100 clips | **71.0%** | [0.6107, 0.7964] | Clopper-Pearson |
| **Fireworks False Triggers**| COND3 | Phase 17 State Reset Candidate | 57 | 100 clips | **57.0%** | [0.4671, 0.6686] | Clopper-Pearson |
| **Fireworks False Triggers**| COND6 | Phase 36 Conservative Suppression | 57 | 100 clips | **57.0%** | [0.4671, 0.6686] | Clopper-Pearson |

- Artifacts:
  - [phase42_authoritative_benchmark.csv](file:///E:/gunshot/gunshot/experiments/phase42/phase42_authoritative_benchmark.csv)
  - [phase42_discrepancy_register.csv](file:///E:/gunshot/gunshot/experiments/phase42/phase42_discrepancy_register.csv)
  - [phase42_claim_evidence_matrix.csv](file:///E:/gunshot/gunshot/experiments/phase42/phase42_claim_evidence_matrix.csv)

---

## 9. Governance Conclusion & Promotion Decision

1. **Phase 14 Remains Baseline:** `model_phase14.py` remains the verified, authoritative **`DEFAULT_RESEARCH_BASELINE`**.
2. **Phase 36 Promotion Rejected:** Phase 36 must remain **`EXPERIMENTAL_RESEARCH_BRANCH_V1`**. It must **NOT** be promoted to baseline because:
   - Its continuous ambient FAR reduction over Phase 14 is not statistically significant ($p = 0.2500$, difference 95% CI spans zero).
   - Its false alarm rate on fireworks challenge audio is substantially higher than Phase 14 (57% vs. 47%).
   - Its causal suppression mechanics remain unproven against complex non-animal transients.
3. **Mandatory Disclaimer:** This prototype is strictly for research and evaluation. It must never be deployed for life-critical public safety or tactical police operations.

