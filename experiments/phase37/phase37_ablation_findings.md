# PHASE 37 SUPPRESSION ABLATION & EQUIVALENCE AUDIT
## Forensic Investigation of the Identical Aggregate Metrics Across COND4, COND5, and COND6

> [!CAUTION]
> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.**
> This experimental acoustic machine-learning software is uncertified and must never be deployed for autonomous emergency dispatch, police tactical response, active-shooter alerting, automated evacuation, building lockdown, or life-critical physical security.
> Use legally obtained recordings and safe audio playback only. Live-fire testing and hazardous acoustic experiments are strictly prohibited.

---

## 1. The Core Scientific Puzzle

In Phase 36, three distinct experimental branch configurations were evaluated:
- **`COND4`:** Phase 36 Raw State Machine (Suppression `NONE`).
- **`COND5`:** Phase 36 Legacy Suppression (Suppression `LEGACY_ANIMAL`, 0.30x factor).
- **`COND6`:** Phase 36 Conservative Suppression (Suppression `CONSERVATIVE`, 0.50x factor, aviation/vehicle protection).

All three conditions reported **identical aggregate metrics**:
- Continuous False Alert Rate: **$13.2000/\text{hr}$** ($66\text{ alerts} / 5.0\text{h}$).
- Convention B Excluded Time: **$300.48\text{ s}$**.
- Positive Ballistic Recall: **$30.2\%$** ($16/53\text{ rounds}$).
- Positive Precision: **$84.2\%$** ($16/19\text{ alerts}$).
- Distractor Trigger Rate: **$10.0\%$** ($6/60\text{ clips}$).

---

## 2. Forensic Investigation & Findings

A line-by-line audit of the 3,297 logged state transitions ([phase36_state_transition_log.csv](file:///E:/gunshot/gunshot/reports/phase36_state_transition_log.csv)) was performed to resolve whether the configurations differed in practice.

### Key Audit Findings:
1. **Configurations Were Correctly Wired & Functionally Active:**
   The suppression engine was actively invoked in all conditions. Across the 5.0 hours of continuous negative audio, exactly **23 transition windows** had active score attenuation ([phase37_suppression_ablation_audit.csv](file:///E:/gunshot/gunshot/experiments/phase37/phase37_suppression_ablation_audit.csv)).
2. **Score Attenuations Differed Between Conditions:**
   - In `COND4` (Raw), scores were unattenuated.
   - In `COND5` (Legacy), scores were attenuated by $0.30\times$ (e.g. $0.4623 \rightarrow 0.1387$).
   - In `COND6` (Conservative), 11 windows were protected from attenuation by aviation overrides, while 12 windows were attenuated by $0.50\times$.
3. **Why Aggregate Alerts Were Identical (The Sub-Threshold Mechanism):**
   In every single one of the 23 attenuated windows, the **unsuppressed raw score ($s_{\text{raw}}$) was ALREADY below the operating threshold**:
   - 13 windows were at `CANDIDATE -> IDLE` transitions where $s_{\text{raw}} < 0.75$ (e.g. $0.4623, 0.4495, 0.3659$). In `COND4`, the candidate was already discarded; attenuating the score further in `COND5` and `COND6` could not change the decay to `IDLE`.
   - 8 windows were at `CONFIRMED -> COOLDOWN` transitions where $s_{\text{raw}} < 0.48$ (e.g. $0.2346, 0.1246$). In `COND4`, the event had already terminated below off-threshold; attenuating the score further could not alter the alert termination or emission timestamp.
   - 2 windows were at `COOLDOWN -> IDLE` where the timer had expired.
4. **Distractor & Positive Partitions:**
   Zero windows in the 60 distractor clips or 23 positive streams triggered animal vocalization suppression.

### Forensic Conclusion:
`COND4`, `COND5`, and `COND6` exhibited **genuine internal score divergence** on continuous audio. However, because all attenuated scores were already below operating thresholds on this specific corpus, **zero state transitions crossed an active decision boundary**. The identical aggregate metrics are an honest, reproducible consequence of acoustic score distribution on this dataset.
