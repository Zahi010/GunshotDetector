# PHASE 11 PRE-REGISTERED EVALUATION PLAN: Independent Field Validation Protocol

> [!CAUTION]
> **SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY**  
> Pre-registration guarantees methodological integrity. Experimental evaluation metrics do not imply life-safety reliability.

---

## 1. Pre-Registration Rationale & Integrity Pledge

To eliminate post-hoc tuning, p-hacking, and selective metric reporting, this evaluation plan pre-registers all evaluation definitions, matching tolerances, statistical methodologies, and acceptance gates **prior to the collection or assessment of new field data**.

### Non-Negotiable Pre-Registration Commitments:
1. **Primary Target Profile:** The `balanced` profile ($\tau_{\text{base}} = 0.75$, $\tau_{\text{high}} = 0.88$, $N_{\text{confirm}} = 2$, cooldown = $2.0\text{s}$, crest floor = $9.5\text{ dB}$) is declared the primary benchmark target.
2. **Comparative Profiles:** `high_precision` and `high_sensitivity` will be evaluated concurrently as comparative baselines without altering their frozen parameters.
3. **No Final Test Tuning:** The final field validation partition will **NEVER** be used to select thresholds, adjust suppression rules, or re-tune model weights.
4. **Primary Units of Evaluation:** Physical acoustic events and exposure hours—not correlated windows—are the primary evaluation units.

---

## 2. Mathematical Definition of Primary Metrics

### Event-Level Metrics:
Adhering to one-to-one bipartite matching with tolerance $\Delta t = 0.75\text{s}$:
- **Event Recall ($R_{\text{event}}$):**
  $$R_{\text{event}} = \frac{\text{TP}_{\text{event}}}{N_{\text{ground\_truth\_gunshots}}}$$
- **Event Precision ($P_{\text{event}}$):**
  $$P_{\text{event}} = \frac{\text{TP}_{\text{event}}}{\text{TP}_{\text{event}} + \text{FP}_{\text{alert}}}$$
  *(Duplicate alerts within cooldown of a matched shot are counted as $\text{DUP}_{\text{alert}}$ and reported separately, but excluded from true positives).*
- **Event F1 Score ($F1_{\text{event}}$):**
  $$F1_{\text{event}} = 2 \cdot \frac{P_{\text{event}} \cdot R_{\text{event}}}{P_{\text{event}} + R_{\text{event}}}$$

### Continuous False-Alert Rate:
- **Continuous False-Alert Rate ($\text{FAR}_{\text{hour}}$):**
  $$\text{FAR}_{\text{hour}} = \frac{\text{Total Unmatched False Alerts on Verified Negative Audio}}{\text{Total Continuous Negative Exposure (Hours)}}$$

### End-to-End Latency Metrics:
Measured from physical audio event onset timestamp $T_{\text{onset}}$ to wall-clock emission timestamp $T_{\text{emission}}$:
- **Median Latency ($L_{50}$)**
- **95th Percentile Latency ($L_{95}$)**
- **Maximum Measured Latency ($L_{\max}$)**

---

## 3. Treatment of Uncertain & Ambiguous Audio

Field recordings tagged with `ground_truth_label = -1` (e.g., highly reverberant distant cracks, muffled transients, or severe clipping) will be handled as follows:
1. **Primary Benchmark:** Completely excluded from numerator and denominator of primary $P_{\text{event}}$, $R_{\text{event}}$, and $F1_{\text{event}}$ calculations.
2. **Sensitivity Analysis:** Evaluated separately in an auxiliary "Stress & Ambiguity Audit" to measure how the detector responds to edge cases without distorting baseline metrics.

---

## 4. Source Grouping & Independence Safeguards

To prevent intra-session correlation and near-duplicate leakage:
- Recordings captured on the same day, from the same firing line, or using the same recorder will share a common `source_session_id`.
- K-fold cross-validation (if subsequent retraining is ever approved) must employ **GroupKFold** grouped on `source_session_id`.
- The field test partition will contain zero overlap in physical location, recording hardware, or recording date with any training data.

---

## 5. Statistical Rigor & Confidence Intervals

- **Wilson Score Interval:** 95% binomial confidence intervals will be computed for event precision and recall:
  $$w = \frac{\hat{p} + \frac{z^2}{2n} \pm z \sqrt{\frac{\hat{p}(1-\hat{p})}{n} + \frac{z^2}{4n^2}}}{1 + \frac{z^2}{n}} \quad (z = 1.96)$$
- **Poisson Rate Intervals:** Computed for continuous false-alert rates per hour.
- **Minimum Sample Size Requirement:** A minimum of **50 physical gunshot events** and **24 continuous exposure hours** is required before statistical significance can be declared. If available data falls below these thresholds, results will be explicitly designated: **"INSUFFICIENT SAMPLE SIZE FOR STATISTICAL INFERENCE."**

---

## 6. Pre-Registration Summary Table

| Metric / Dimension | Pre-Registered Standard | Minimum Acceptance Criterion |
|---|---|---|
| **Primary Operating Profile** | `balanced` | $\tau_{\text{base}} = 0.75, \tau_{\text{high}} = 0.88, N_{\text{confirm}} = 2$ |
| **Event Matching Tolerance** | $\pm 0.75\text{ seconds}$ | One-to-one Hungarian bipartite matching |
| **Target Event Precision** | $\ge 70.0\%$ | 95% Confidence Interval Reported |
| **Target Event Recall** | $\ge 65.0\%$ | 95% Confidence Interval Reported |
| **Target False-Alert Rate** | $\le 10.0\text{ alerts/hour}$ | Across 24 hours of multi-environment audio |
| **End-to-End Latency Ceiling**| P95 $< 1,000\text{ ms}$ | Strict compliance with 2,000 ms real-time limit |
| **Zero-Shot Claim Rule** | Prohibited unless $\ge 50$ shots in novel site | Transparently disclose unverified status |
