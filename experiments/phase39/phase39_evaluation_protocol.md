# PHASE 39 PROSPECTIVE EVALUATION PROTOCOL
## Continuous Ambient Expansion, Statistical Robustness & Expanded Distractor Challenge

> [!CAUTION]
> ### MANDATORY SAFETY DESIGNATION
> **RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.**
> 
> This experimental software is uncertified research code. It must never be deployed for autonomous emergency dispatch, police tactical response, active-shooter alerting, automated evacuation, building lockdown, or life-critical physical security. Use lawfully obtained recordings and safe audio playback only. Live-fire testing and hazardous acoustic experiments are strictly prohibited.

---

## 1. Protocol Pre-Registration & Methodological Freeze

- **Protocol Version:** 1.0.0-FROZEN
- **Phase Designation:** Phase 39 Prospective Evaluation
- **Freeze Status:** This protocol is authored, cryptographically frozen, and its SHA-256 hash recorded **PRIOR** to data acquisition, feature extraction, or prospective evaluation of the expanded corpus.
- **Governing Directives:**
  1. No detector model, classifier head, threshold, suppression parameter, or state machine logic shall be altered, retrained, or tuned.
  2. Continuous exposure shall be measured from authentic, unconcatenated field recordings. No audio looping, synthetic silence, or artificial concatenation shall be counted toward exposure.
  3. Ground truth for positive clips shall be classified as **Clip-Level Detection**, strictly distinguishing it from timestamped event-level or round-level ballistic recall.
  4. Distractor clips shall be expanded without filtering or cherry-picking to favor any detector architecture.

---

## 2. Research Questions

- **RQ1 (Continuous Ambient Generalization):** Does Phase 36 maintain lower false alarm rates (Gross FAR and Eligible FAR under Convention A and B) compared to Phase 14 Balanced across multi-hour, multi-environment continuous ambient field recordings?
- **RQ2 (Fireworks & Pyrotechnic False Triggers):** On a statistically robust challenge set of at least 100 distinct fireworks and pyrotechnic recordings, what is the exact empirical difference in false trigger rates between Phase 14 Balanced and Phase 36 Experimental, and is the difference statistically significant under paired McNemar testing?
- **RQ3 (Broad-Spectrum Distractor Specificity):** Across challenge categories including door slams/impacts, thunder, glass breakage, vehicle backfires, screaming, and tool impacts, does Phase 36 maintain specificity parity with Phase 14?
- **RQ4 (Duplicate Alert Reduction Parity):** Does Phase 36 maintain its demonstrated ~50% reduction in redundant duplicate alerts during active gunfire audio while preserving clip-level sensitivity?

---

## 3. Standardized Evaluation Conditions

The prospective evaluation executes identically across six standardized conditions:

| Condition ID | Architecture / Profile | State-Machine Implementation | Suppression Engine Mode | Operational Role |
|:---:|---|---|---|---|
| **`COND1`** | Phase 14 Balanced | Legacy Phase 14 Event Consolidation | Phase 14 Semantic Attenuation | Authoritative Baseline (`DEFAULT_RESEARCH_BASELINE`) |
| **`COND2`** | Phase 17 Experimental | Phase 17 FSM (Unconfirmed Leakage Defect) | Phase 17 Animal Suppression | Selectable Profile (`SELECTABLE_EXPERIMENTAL_PROFILE`) |
| **`COND3`** | Phase 31 State Reset | Phase 17 FSM with Forced State Reset | Phase 17 Animal Suppression | Quarantined Reference (`QUARANTINED_DIAGNOSTIC_REFERENCE`) |
| **`COND4`** | Phase 36 FSM Only | Phase 36 Clean Finite State Machine | `NONE` (Ablation Baseline) | Experimental Branch Ablation (`EXPERIMENTAL_RESEARCH_BRANCH_V1`) |
| **`COND5`** | Phase 36 Legacy Suppression | Phase 36 Clean Finite State Machine | `LEGACY_ANIMAL` (Phase 17 logic) | Experimental Branch Ablation (`EXPERIMENTAL_RESEARCH_BRANCH_V1`) |
| **`COND6`** | Phase 36 Complete | Phase 36 Clean Finite State Machine | `CONSERVATIVE` (Context-aware) | Experimental Branch Candidate (`EXPERIMENTAL_RESEARCH_BRANCH_V1`) |

---

## 4. Evaluation Data Partitions & Acquisition Constraints

### Partition A: Expanded Continuous Ambient Negative
- **Source:** Independently sourced unedited continuous field recordings from legal open archives (e.g. Radio Aporee on Archive.org).
- **Target:** Extend exposure toward cumulative 20 hours across at least 5 independent campaigns and geographic environments.
- **Reporting Rule:** If lawful bandwidth or repository boundaries limit the total continuous duration, the exact duration shall be honestly reported without synthetic padding.
- **Exclusion Check:** Automated SHA-256 exact-match and filename matching against all 2,252 historical repository audio assets.

### Partition B: Expanded Distractor Challenge Corpus
- **Target:** At least 100 distinct fireworks and pyrotechnic clips (FSD50K Dev Set) to ensure statistical power for RQ2.
- **Additional Categories:** Door slams & impacts (20 clips), Thunder & lightning (20 clips), Glass breakage (20 clips), Vehicle backfires / engine transients (20 clips), Screaming & yelling (20 clips), Power tools & construction impacts (20 clips).
- **Independence:** Unique audio files with zero overlap with historical training sets.

### Partition C: Positive Gunfire Reference Set
- **Target:** 120 positive gunshot clips from FSD50K Dev set (evaluated under clip-level detection criteria).

---

## 5. Metric Definitions & Formulas

1. **Continuous Gross False Alarm Rate (FAR):**
   $$\text{Gross FAR} = \frac{\text{Total Confirmed Alerts}}{\text{Total Continuous Exposure (Hours)}}$$

2. **Convention A Eligible FAR:**
   $$\text{Eligible Duration}_A = \max\left(1.0\text{ s}, T_{\text{total}} - 10.0\text{ s} \times \text{Alerts}\right)$$
   $$\text{Conv A FAR} = \frac{\text{Total Confirmed Alerts}}{\text{Eligible Duration}_A\text{ (Hours)}}$$

3. **Convention B Eligible FAR:**
   $$\text{Eligible Duration}_B = \max\left(1.0\text{ s}, T_{\text{total}} - \sum (\text{Alert Event Duration} + 10.0\text{ s})\right)$$
   $$\text{Conv B FAR} = \frac{\text{Total Confirmed Alerts}}{\text{Eligible Duration}_B\text{ (Hours)}}$$

4. **Exact Poisson 95% Confidence Intervals for Count $k$ and Hours $H$:**
   $$\text{Lower} = \frac{0.5 \times \chi^2_{\alpha/2, 2k}}{H}, \quad \text{Upper} = \frac{0.5 \times \chi^2_{1 - \alpha/2, 2(k+1)}}{H}$$
   *(When $k=0$, $\text{Lower}=0$ and $\text{Upper} = 0.5 \times \chi^2_{1-\alpha, 2} / H$)*

5. **Clip-Level Positive Detection Rate (Recall):**
   $$\text{Clip-Level Recall} = \frac{\text{Clips with } \ge 1 \text{ Confirmed Alert}}{\text{Total Positive Gunshot Clips}}$$

6. **Exact Clopper-Pearson 95% Confidence Intervals for Binomial $k/n$:**
   $$\text{Lower} = \text{Beta}(\alpha/2, k, n - k + 1), \quad \text{Upper} = \text{Beta}(1 - \alpha/2, k + 1, n - k)$$

7. **Duplicate Alert Rate on Positive Clips:**
   $$\text{Duplicate Alert Rate} = \frac{\sum (k_i - 1)}{\sum k_i} \quad \text{for clips with } k_i \ge 1$$
   *(Unit: Emitted alerts; measures the proportion of emitted alerts that represent fragmentation within already-detected clips).*

8. **Paired McNemar Test on Fireworks Triggers:**
   $$\chi^2 = \frac{(|b - c| - 1)^2}{b + c}$$
   where $b$ is the number of fireworks clips triggered by Phase 36 but not Phase 14, and $c$ is the number triggered by Phase 14 but not Phase 36.

---

## 6. Stopping & Amendment Rules

1. Any discrepancy between pre-registered protocol and final execution must be documented as a formal protocol amendment.
2. Results must be presented alongside exact sample sizes and confidence intervals.
3. No model promotion is permitted without formal authorization and real-world pilot certification.

