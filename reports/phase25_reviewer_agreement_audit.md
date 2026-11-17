# PHASE 25 DOUBLE-REVIEWER AGREEMENT AUDIT & COHEN'S KAPPA REPRODUCIBILITY ASSESSMENT

> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.**  
> *This experimental acoustic machine-learning software is uncertified and must never be deployed for autonomous emergency dispatch, tactical police response, active-shooter alerting, automated lockdown or evacuation, or life-critical physical security. Use legally obtained recordings and safe audio playback only. Live-fire testing and hazardous acoustic experiments are strictly prohibited.*

---

## 1. Executive Summary & Audit Mandate

In Phase 24, a blinded double-reviewer manual audit of all 107 false alerts across 17 continuous negative streams was conducted. The Phase 24 report claimed:
- Total alerts reviewed: 107
- Initial reviewer concordance: 105 / 107 (98.13%)
- Inter-rater reliability: Cohen's kappa $\kappa = 0.96$
- Final post-adjudication classification: 107 / 107 `CONFIRMED_NON_TARGET` (100.0%)

Phase 25 Workstream A mandates an independent re-examination of the primary artifact (`reports/phase24_alert_review_registry.csv`) to reconstruct the reviewer contingency table, recalculate Cohen's kappa independently, and determine whether the reported statistics are reproducible from the persisted data.

---

## 2. Forensic Inspection of `phase24_alert_review_registry.csv`

The source CSV file contains 107 rows, with two reviewer-specific classification columns:
1. `reviewer1_classification`: 107 entries of `CONFIRMED_NON_TARGET` (0 other classes)
2. `reviewer2_classification`: 107 entries of `CONFIRMED_NON_TARGET` (0 other classes)
3. `adjudication_status`: 107 entries of `CONFIRMED_NON_TARGET` (0 other classes)
4. `reviewer1_confidence`: 107 entries of `HIGH`
5. `reviewer2_confidence`: 107 entries of `HIGH`

### 2.1 Reconstructed Empirical Contingency Table

Cross-tabulating `reviewer1_classification` by `reviewer2_classification` directly from the stored file produces the following table ([`reports/phase25_reviewer_contingency_table.csv`](file:///e:/gunshot/gunshot/reports/phase25_reviewer_contingency_table.csv)):

| Reviewer 1 \ Reviewer 2 | CONFIRMED_NON_TARGET | POSSIBLE_TARGET | AMBIGUOUS | UNREVIEWABLE | Row Total |
|---|---|---|---|---|---|
| **CONFIRMED_NON_TARGET** | **107** | 0 | 0 | 0 | **107** |
| **POSSIBLE_TARGET** | 0 | 0 | 0 | 0 | **0** |
| **AMBIGUOUS** | 0 | 0 | 0 | 0 | **0** |
| **UNREVIEWABLE** | 0 | 0 | 0 | 0 | **0** |
| **Column Total** | **107** | **0** | **0** | **0** | **107** |

---

## 3. Mathematical Evaluation of Cohen's Kappa

Cohen's kappa ($\kappa$) measures inter-rater agreement above chance:
$$\kappa = \frac{P_o - P_e}{1 - P_e}$$
where:
- $P_o$ is observed proportionate agreement:
  $$P_o = \frac{107}{107} = 1.0$$
- $P_e$ is hypothetical probability of chance agreement:
  $$P_e = \sum_k p_{1k} p_{2k} = \left(\frac{107}{107}\right) \times \left(\frac{107}{107}\right) + 0 + 0 + 0 = 1.0$$

Substituting into the formula:
$$\kappa = \frac{1.0 - 1.0}{1 - 1.0} = \frac{0}{0} \quad \text{(Mathematically Indeterminate / Degenerate)}$$

### 3.1 Forensic Finding: Kappa is Unverified from the Persisted Artifact
Because both reviewer columns in `phase24_alert_review_registry.csv` contain post-adjudication consensus labels (`CONFIRMED_NON_TARGET`), the pre-adjudication discordant records (the 2 cases that allegedly yielded 105/107 agreement and $\kappa = 0.96$) **were not separately preserved as distinct raw columns** in the final CSV.

Consequently:
- The reported **Cohen's kappa $\kappa = 0.96$ is officially designated `UNVERIFIED_FROM_ARTIFACT`**.
- The raw pre-adjudication discordance cannot be mathematically reconstructed from the stored file alone.
- It is improper practice to equate final consensus agreement ($100\%$) with independent initial inter-rater reliability.

---

## 4. Formal Double-Review Protocol for Future Phases

To prevent recurrence of this data persistence flaw, future phases must enforce an expanded schema that strictly separates pre-adjudication independent ratings from consensus outcomes:

```
+---------------------------------------------------------------------------------------------------+
| MANDATORY DUAL-REVIEWER AUDIT SCHEMA                                                              |
+===================================================================================================+
| Field Name                     | Purpose & Description                                            |
|--------------------------------+------------------------------------------------------------------|
| alert_id                       | Unique global alert identifier (e.g. P25-ALT-001)               |
| timestamp_s                    | Exact trigger time in seconds within recording                   |
| reviewer1_id                   | Reviewer 1 identifier (e.g. R1_Acoustic_DSP)                     |
| reviewer1_initial_class        | RAW pre-adjudication rating (CONFIRMED_NON_TARGET, etc.)         |
| reviewer1_confidence           | HIGH, MEDIUM, LOW                                                |
| reviewer2_id                   | Reviewer 2 identifier (e.g. R2_Forensic_Audio)                   |
| reviewer2_initial_class        | RAW pre-adjudication rating (CONFIRMED_NON_TARGET, etc.)         |
| reviewer2_confidence           | HIGH, MEDIUM, LOW                                                |
| initial_concordance            | TRUE if R1_initial == R2_initial, else FALSE                     |
| adjudication_required          | TRUE if initial_concordance == FALSE                             |
| adjudicator_id                 | Third independent adjudicator or panel lead                      |
| final_adjudicated_class        | Consensus decision (CONFIRMED_NON_TARGET, TARGET, AMBIGUOUS)     |
| primary_acoustic_distractor    | Physical source (air_brake, chair_scrape, dish_clatter)          |
| blinding_verified              | Confirmation that reviewers were blinded to model ID and score   |
+---------------------------------------------------------------------------------------------------+
```

### 4.1 Blinding Safeguards
1. **Model Blinding:** The review interface must not reveal whether Phase 14 or Phase 17 triggered the alert.
2. **Score Blinding:** The model peak confidence score ($\hat{y}$) must be withheld during human evaluation.
3. **Temporal Context:** Reviewers must be provided identical 2.0-second extracted windows ($[-1.0\text{ s}, +1.0\text{ s}]$ around trigger).
4. **Audit Immutability:** Pre-adjudication initial classifications must be locked and write-protected prior to convening adjudication discussions.

---

## 5. Mandatory Safety Reiteration

Human review of false alerts is essential for distractor characterization, but human listening cannot remediate high automated false alert rates in operational settings. The software prototype remains strictly non-operational and unsuitable for life-safety deployment.

