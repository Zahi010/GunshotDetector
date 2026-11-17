# Phase 21: Recording-Level Paired Analysis and Incident-Level Audit

> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY**  
> *This experimental acoustic machine-learning system is not certified and must never be used for autonomous emergency dispatch, police response, active-shooter alerting, automated evacuation, or critical physical security. Use legally obtained recorded audio and safe playback only. No live-fire testing or hazardous acoustic experiments.*

---

## 1. Executive Summary

In unadjusted event-level testing, each physical round is treated as an independent statistical trial ($N=50$), producing an exact McNemar $p$-value of $0.03125$. However, in physical reality, the 50 rounds are clustered inside exactly **20 continuous recording streams** ($10.0\text{ s}$ each).

This recording-level analysis evaluates whether the Phase 17 recall advantage remains statistically robust when the recording stream is the unit of observation:
1. **Concordance Across Recordings:** In **15 out of 20 recordings (75.0%)**, Phase 14 and Phase 17 exhibit **identical round-level detection counts** (zero discordance).
2. **Discordance Concentration:** All 6 additional Phase 17 detections are concentrated in only **5 recordings** (`test_004`, `test_013`, `test_037`, `test_055`, `test_067`).
3. **Incident-Level Detection ($N=20$ Streams):**
   - Phase 14 Balanced: **15 of 20 streams detected (75.0%)**
   - Phase 17 Experimental: **18 of 20 streams detected (90.0%)**
   - Paired Incident Contingency: Both detected = 15, Phase 14 only = 0, Phase 17 only = 3, Neither = 2.
   - **Incident Exact Binomial $p$-value:**
     $$p = 2 \cdot \binom{3}{0} (0.5)^3 = 2 \cdot \frac{1}{8} = 0.25000$$
     At the incident level, the Phase 17 advantage is **NOT statistically significant ($p = 0.25000 \gg 0.05$)**.
4. **Recording Mean Recall:**
   - Phase 14 Balanced Mean Recording Recall: **58.33%**
   - Phase 17 Experimental Mean Recording Recall: **71.67%**
   - Mean Difference: **+13.33 percentage points**
   - Wilcoxon Signed-Rank Test ($N=5$ non-zero pairs): $W = 0.0, p = 0.06250$ (**NOT statistically significant** at $\alpha=0.05$).

---

## 2. Comprehensive Recording-by-Recording Results Table

| Stream Identifier | Position | Test ID | Sequence Type | Caliber | GT Rounds | Phase 14 Det | Phase 17 Det | Phase 14 Recall | Phase 17 Recall | Recall Delta | Phase 14 Incident | Phase 17 Incident | Discordant Rounds |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `P19-CAT-A-FP1-test_001` | FP1 | `test_001` | 3_ROUND_BURST | .45 ACP Handgun | 3 | 1 | 1 | 33.3% | 33.3% | +0.0% | YES | YES | 0 |
| `P19-CAT-A-FP1-test_004` | FP1 | `test_004` | SINGLE_SHOT | .45 ACP Handgun | 1 | 0 | 1 | 0.0% | 100.0% | +100.0% | NO | YES | 1 |
| `P19-CAT-A-FP1-test_007` | FP1 | `test_007` | 3_ROUND_BURST | .40 S&W Handgun | 3 | 1 | 1 | 33.3% | 33.3% | +0.0% | YES | YES | 0 |
| `P19-CAT-A-FP1-test_013` | FP1 | `test_013` | 3_ROUND_BURST | 9x19mm Handgun | 3 | 0 | 1 | 0.0% | 33.3% | +33.3% | NO | YES | 1 |
| `P19-CAT-A-FP2-test_019` | FP2 | `test_019` | 3_ROUND_BURST | .45 ACP Handgun | 3 | 1 | 1 | 33.3% | 33.3% | +0.0% | YES | YES | 0 |
| `P19-CAT-A-FP2-test_022` | FP2 | `test_022` | SINGLE_SHOT | .45 ACP Handgun | 1 | 1 | 1 | 100.0% | 100.0% | +0.0% | YES | YES | 0 |
| `P19-CAT-A-FP2-test_025` | FP2 | `test_025` | 3_ROUND_BURST | .40 S&W Handgun | 3 | 1 | 1 | 33.3% | 33.3% | +0.0% | YES | YES | 0 |
| `P19-CAT-A-FP2-test_031` | FP2 | `test_031` | 3_ROUND_BURST | 9x19mm Handgun | 3 | 3 | 3 | 100.0% | 100.0% | +0.0% | YES | YES | 0 |
| `P19-CAT-A-FP3-test_037` | FP3 | `test_037` | 3_ROUND_BURST | .45 ACP Handgun | 3 | 2 | 3 | 66.7% | 100.0% | +33.3% | YES | YES | 1 |
| `P19-CAT-A-FP3-test_040` | FP3 | `test_040` | SINGLE_SHOT | .45 ACP Handgun | 1 | 1 | 1 | 100.0% | 100.0% | +0.0% | YES | YES | 0 |
| `P19-CAT-A-FP3-test_043` | FP3 | `test_043` | 3_ROUND_BURST | .40 S&W Handgun | 3 | 3 | 3 | 100.0% | 100.0% | +0.0% | YES | YES | 0 |
| `P19-CAT-A-FP3-test_049` | FP3 | `test_049` | 3_ROUND_BURST | 9x19mm Handgun | 3 | 0 | 0 | 0.0% | 0.0% | +0.0% | NO | NO | 0 |
| `P19-CAT-A-FP4-test_055` | FP4 | `test_055` | 3_ROUND_BURST | .45 ACP Handgun | 3 | 2 | 3 | 66.7% | 100.0% | +33.3% | YES | YES | 1 |
| `P19-CAT-A-FP4-test_058` | FP4 | `test_058` | SINGLE_SHOT | .45 ACP Handgun | 1 | 1 | 1 | 100.0% | 100.0% | +0.0% | YES | YES | 0 |
| `P19-CAT-A-FP4-test_061` | FP4 | `test_061` | 3_ROUND_BURST | .40 S&W Handgun | 3 | 3 | 3 | 100.0% | 100.0% | +0.0% | YES | YES | 0 |
| `P19-CAT-A-FP4-test_067` | FP4 | `test_067` | 3_ROUND_BURST | 9x19mm Handgun | 3 | 0 | 2 | 0.0% | 66.7% | +66.7% | NO | YES | 2 |
| `P19-CAT-A-FP5-test_127` | FP5 | `test_127` | 3_ROUND_BURST | .45 ACP Handgun | 3 | 0 | 0 | 0.0% | 0.0% | +0.0% | NO | NO | 0 |
| `P19-CAT-A-FP5-test_130` | FP5 | `test_130` | SINGLE_SHOT | .45 ACP Handgun | 1 | 1 | 1 | 100.0% | 100.0% | +0.0% | YES | YES | 0 |
| `P19-CAT-A-FP5-test_133` | FP5 | `test_133` | 3_ROUND_BURST | .40 S&W Handgun | 3 | 3 | 3 | 100.0% | 100.0% | +0.0% | YES | YES | 0 |
| `P19-CAT-A-FP5-test_139` | FP5 | `test_139` | 3_ROUND_BURST | 9x19mm Handgun | 3 | 3 | 3 | 100.0% | 100.0% | +0.0% | YES | YES | 0 |

---

## 3. Analysis of the Five Discordant Recordings

The six additional rounds detected by Phase 17 are confined to five specific recordings:

1. **`P19-CAT-A-FP1-test_004` (FP1, Single Shot, .45 ACP):**
   - Phase 14: 0/1 (Missed incident)
   - Phase 17: 1/1 (Detected incident)
   - *Impact:* Generates 1 new incident alert and 1 round gain.
2. **`P19-CAT-A-FP1-test_013` (FP1, 3-Round Burst, 9x19mm):**
   - Phase 14: 0/3 (Missed incident)
   - Phase 17: 1/3 (Detected burst round 1, missed rounds 2 and 3)
   - *Impact:* Generates 1 new incident alert and 1 round gain.
3. **`P19-CAT-A-FP3-test_037` (FP3, 3-Round Burst, .45 ACP):**
   - Phase 14: 2/3 (Already detected incident via rounds 2 and 3)
   - Phase 17: 3/3 (Detected all 3 rounds)
   - *Impact:* Zero incident gain; +1 round gain.
4. **`P19-CAT-A-FP4-test_055` (FP4, 3-Round Burst, .45 ACP):**
   - Phase 14: 2/3 (Already detected incident via rounds 1 and 2)
   - Phase 17: 3/3 (Detected all 3 rounds)
   - *Impact:* Zero incident gain; +1 round gain.
5. **`P19-CAT-A-FP4-test_067` (FP4, 3-Round Burst, 9x19mm):**
   - Phase 14: 0/3 (Missed incident)
   - Phase 17: 2/3 (Detected burst rounds 1 and 2, missed round 3)
   - *Impact:* Generates 1 new incident alert and +2 round gain.

### Key Observation:
Only **3 recordings** changed incident detection status from Miss to Detect (`test_004`, `test_013`, `test_067`). In the other 2 recordings (`test_037`, `test_055`), Phase 14 had already successfully detected the gunfire incident ($2/3$ rounds detected).

---

## 4. Methodological Significance

When observations are evaluated at the stream level ($N=20$), the small sample size and large proportion of concordant trials ($15/20 = 75\%$) cause the exact binomial test of incident detection to yield $p = 0.25000$.

Treating recording streams as the unit of analysis demonstrates that Phase 17's apparent advantage is not a pervasive, stream-by-stream improvement, but a localized recovery of 3 previously missed streams and 2 incremental burst rounds.

---
*Report certified under Phase 21 Forensic Audit protocol.*
