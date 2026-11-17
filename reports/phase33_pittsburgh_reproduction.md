# Phase 33: Pittsburgh DQV 2018 Event-Matching Reproduction Report
## Independent Audit of One-to-One Matching, Multi-Credit Alert Reuse & Significance Collapse

**Document ID:** `REPORT-PHASE33-PITTSBURGH-001`  
**Phase:** 33 (Independent Forensic Audit)  
**Date:** November 2026  
**Status:** FULLY REPRODUCED — MULTI-CREDIT FALLACY AUDITED — MCNEMAR P = 0.21875 VERIFIED  

---

### MANDATORY SAFETY DESIGNATION
> [!CAUTION]
> **RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.**  
> This experimental acoustic machine-learning software is uncertified and must never be deployed for autonomous emergency dispatch, tactical police response, active-shooter alerting, automated evacuation, building lockdown, or life-critical physical security. Use legally obtained recordings and safe audio playback only. Live-fire testing and hazardous acoustic experiments are strictly prohibited. Historical controlled-validation recordings may be analysed only as existing research data; do not conduct new firing experiments.

---

## 1. Executive Summary & Reproduction Status

Phase 33 conducted an independent, read-only forensic reproduction of the Pittsburgh Data Quality Validation (DQV) 2018 controlled gunfire evaluation across all 50 annotated physical rounds (Category A, 20 audio recordings, 200.0s gross duration).

### Reproduction Verdict: `REPRODUCED WITH CONFIRMED METHODOLOGICAL ARTIFACT`
1. **Total Physical Alerts Emitted:**  
   Across the 20 recordings, **Phase 14 generated only 15 distinct alerts**, and **Phase 17 generated only 19 distinct alerts**.
2. **Historical Multi-Credit Artifact (Phase 20):**  
   The historical report that Phase 14 detected 27 rounds and Phase 17 detected 33 rounds ($p = 0.03125$) occurred because single alerts spanning multi-shot bursts were credited repeatedly to multiple consecutive rounds (e.g. 1 alert credited 3 times in `test_031`, `test_043`, `test_061`, `test_133`, `test_139`). Exactly **12 detections in Phase 14** and **14 detections in Phase 17** were duplicate credits.
3. **Strict One-to-One Matching ($p = 0.21875$):**  
   Under the mandatory rule that each detector alert can match at most one physical round:
   - Phase 14 detected **15 / 50 rounds (30.0%)**.
   - Phase 17 detected **19 / 50 rounds (38.0%)**.
   - Discordant pairs: Exactly 6 pairs ($b = 1$ Phase-14-only, $c = 5$ Phase-17-only).
   - Exact Two-Sided McNemar Test: **$p = \mathbf{0.21875}$** ($p > 0.05$).
4. **Recording-Level Incident Detection ($p = 0.2500$):**  
   At the incident level ($N = 20$ recordings):
   - Phase 14 detected an incident in **15 / 20 recordings (75.0%)**.
   - Phase 17 detected an incident in **18 / 20 recordings (90.0%)**.
   - Discordant recordings: Exactly 3 recordings ($0$ vs $3$).
   - Exact Two-Sided McNemar Test: **$p = \mathbf{0.2500}$** ($p > 0.05$).

---

## 2. One-to-One Matching Algorithm & Tie-Breaking Rules

The matching protocol between annotated rounds and emitted alerts enforces the following formal constraints:
1. **Temporal Matching Tolerance:** An alert is eligible to match a physical round if the round timestamp $t_{\text{round}}$ falls within the alert window $[t_{\text{start}} - 0.5\text{s}, t_{\text{end}} + 0.5\text{s}]$ or if $|t_{\text{alert\_start}} - t_{\text{round}}| \le 1.0\text{s}$.
2. **One-to-One Invariance:** Each physical alert can be assigned to **at most one** physical round. Once an alert is assigned to a round, it is consumed and cannot match any subsequent round in the sequence.
3. **Tie-Breaking Rule:** When multiple unassigned rounds fall within a single alert window, the alert is assigned to the nearest round in time:
   $$\text{Round}^* = \arg\min_j |t_{\text{alert\_peak}} - t_{\text{round}, j}|$$
   Any remaining rounds within that alert interval are classified as `MERGED_INTO_EARLIER_ALERT` or `IN_REFRACTORY_COOLDOWN`.

The complete round-by-round assignment table is preserved in [phase33_pittsburgh_matching_assignments.csv](file:///E:/gunshot/gunshot/reports/phase33_pittsburgh_matching_assignments.csv).

---

## 3. Paired Contingency Tables & McNemar Exact Test

Audit data preserved in [phase33_pittsburgh_contingency_table.csv](file:///E:/gunshot/gunshot/reports/phase33_pittsburgh_contingency_table.csv):

### 3.1. Round-Level 1-to-1 Paired Contingency Table ($N = 50$ Rounds)

$$\begin{pmatrix} \text{Both Detected} & \text{Phase 14 Only} \\ \text{Phase 17 Only} & \text{Neither Detected} \end{pmatrix} = \begin{pmatrix} 14 & 1 \\ 5 & 30 \end{pmatrix}$$

- **Concordant Pairs:** Both Detected = $14$, Neither Detected = $30$. Total concordant = $44$.
- **Discordant Pairs:**
  - $b = 1$ (Phase 14 Only): In `test_037`, Phase 14's late alert matched Round 3 ($t=4.440\text{s}$), whereas Phase 17's early alert matched Round 1 ($t=2.828\text{s}$).
  - $c = 5$ (Phase 17 Only):
    - `test_004-EV01` (.45 ACP Single Shot)
    - `test_013-EV01` (9mm Burst)
    - `test_067-EV01` (9mm Burst)
    - `test_037-EV01` (.45 ACP Burst, Round 1 matched by early P17 alert)
    - `test_055-EV03` (.45 ACP Burst, Round 3 matched by P17's second alert)
- **Exact Two-Sided McNemar Binomial Test:**
  $$P(K \le 1 \text{ or } K \ge 5 \mid N = 6, p = 0.5) = 2 \times \left[ \binom{6}{0} + \binom{6}{1} \right] \times (0.5)^6 = 2 \times \frac{1 + 6}{64} = \frac{14}{64} = \mathbf{0.21875}$$
- **Verdict:** **NOT STATISTICALLY SIGNIFICANT** ($p = 0.21875 > 0.05$).

### 3.2. Recording-Level Incident Contingency Table ($N = 20$ Recordings)

$$\begin{pmatrix} \text{Both Detected} & \text{Phase 14 Only} \\ \text{Phase 17 Only} & \text{Neither Detected} \end{pmatrix} = \begin{pmatrix} 15 & 0 \\ 3 & 2 \end{pmatrix}$$

- **Discordant Recordings:** $b = 0, c = 3$ (`test_004`, `test_013`, `test_067` detected by P17 only).
- **Exact Two-Sided McNemar Binomial Test:**
  $$p = 2 \times (0.5)^3 = \frac{2}{8} = \mathbf{0.2500}$$
- **Verdict:** **NOT STATISTICALLY SIGNIFICANT** ($p = 0.2500 > 0.05$).

---

## 4. Controlled Validation Boundaries & Safety Prohibition

1. **Powerlessness to Evaluate Operational FAR:**  
   The entire Pittsburgh DQV 2018 dataset contains only $140.0\text{ seconds}$ of background audio without gunshot acoustics. The Garwood 95% Poisson upper confidence limit for a zero-alert observation in 140 seconds is:
   $$\text{FAR}_{95\%} = \frac{-\ln(0.05)}{140.0\text{ s}} \times 3600 = \mathbf{77.03\text{ false alerts/hour}}$$
   A detector with an unacceptably high false-alert rate of $50\text{ alerts/hour}$ would produce zero false alarms in 140 seconds with $> 85\%$ probability!
2. **Acoustic Artificiality:**  
   Controlled live-fire recordings have high SNR, stationary sensors, and lack moving urban noise sources or building diffraction.
3. **Strict Ban on Live-Fire Testing:**  
   Live-fire testing and hazardous acoustic experiments are strictly prohibited. These historical controlled recordings represent frozen research archives and must never be used to claim operational life-safety readiness.

