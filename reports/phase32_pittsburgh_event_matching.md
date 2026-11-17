# Phase 32: Pittsburgh Event-Matching Audit Report
## Forensic Reconstruction of Historical Firing Recall, Multi-Credit Alert Reuse & One-to-One Reassessment

**Document ID:** `REPORT-PHASE32-PITTSBURGH-001`  
**Phase:** 32 (Historical Event-Matching Audit)  
**Date:** November 2026  
**Status:** COMPLETE FORENSIC AUDIT — MCNEMAR SIGNIFICANCE COLLAPSE CONFIRMED  

---

### MANDATORY SAFETY DESIGNATION
> [!CAUTION]
> **RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.**  
> This experimental acoustic machine-learning software is uncertified and must never be deployed for autonomous emergency dispatch, tactical police response, active-shooter alerting, automated evacuation, building lockdown, or life-critical physical security. Use legally obtained recordings and safe audio playback only. Live-fire testing and hazardous acoustic experiments are strictly prohibited. Historical controlled-validation recordings may be analysed only as existing research data; do not conduct new firing experiments.

---

## 1. Executive Summary & Audit Mission

Historical evaluations in Phase 20 and Phase 21 reported that on the Pittsburgh Data Quality Validation (DQV) 2018 controlled gunfire dataset:
- Phase 17 Experimental detected **33 out of 50 rounds (66.0% recall)**.
- Phase 14 Balanced detected **27 out of 50 rounds (54.0% recall)**.
- Paired McNemar exact binomial test yielded **$p = 0.03125$ ($6\text{ discordant pairs}, 0\text{ vs }6$)**, suggesting a statistically significant sensitivity advantage for Phase 17.

Phase 32 conducted a comprehensive forensic audit of the round-to-alert matching mechanics across all 20 recordings, comparing the historical multi-credit matching protocol against a **strict 1-to-1 event matching standard** (where each physical alert can match at most one ground-truth round).

### Critical Audit Findings
1. **Physical Alert Count Inadequacy:**  
   Across the 20 recordings (50 total rounds), **Phase 14 generated only 15 distinct alerts**, and **Phase 17 generated only 19 distinct alerts**.
2. **The Multi-Credit Fallacy:**  
   The historical report of 27 detections for Phase 14 and 33 detections for Phase 17 occurred because single, sustained alerts covering rapid-fire bursts were credited simultaneously to 2 or 3 separate physical rounds. Exactly **12 detections in Phase 14** ($44.4\%$) and **14 detections in Phase 17** ($42.4\%$) were duplicate credits from already-counted alerts.
3. **Statistical Significance Collapse ($p = 0.03125 \to p = 0.21875$):**  
   Under strict 1-to-1 event matching:
   - Phase 14 detected **15 / 50 rounds (30.0%)**.
   - Phase 17 detected **19 / 50 rounds (38.0%)**.
   - Discordant pairs: 6 pairs ($1\text{ vs }5$).
   - Exact two-sided McNemar binomial test: **$p = \mathbf{0.21875}$** ($p > 0.05$).
4. **Recording-Level Incident Significance ($p = 0.2500$):**  
   At the incident level ($N=20$ recordings):
   - Phase 14 detected an incident in 15 of 20 recordings (75.0%).
   - Phase 17 detected an incident in 18 of 20 recordings (90.0%).
   - Discordant recordings: 3 recordings ($0\text{ vs }3$).
   - Exact two-sided McNemar binomial test: **$p = \mathbf{0.2500}$** ($p > 0.05$).

> [!IMPORTANT]
> **Definitive Conclusion:**  
> The historical claim that Phase 17 demonstrated statistically significant superior gunshot detection sensitivity ($p = 0.03125$) is **REFUTED**. The apparent significance was an artifact of multi-credit alert reuse across burst sequences. Under standard 1-to-1 matching, there is zero statistically significant difference between Phase 14 and Phase 17 ($p = 0.21875$).

---

## 2. Pittsburgh DQV 2018 Dataset Overview

The historical controlled test set comprises 20 short audio recordings (10.0s each, total duration 200.0s = 0.0556 hr) captured across 5 municipal firing positions (FP1 to FP5) using three firearm calibers (.45 ACP, .40 S&W, 9x19mm Luger).

| Recording / Stream ID | Position | Caliber | Sequence Type | Ground Truth Rounds | P14 Physical Alerts | P17 Physical Alerts | Hist P14 Rounds Credited | Hist P17 Rounds Credited |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `P19-CAT-A-FP1-test_001` | FP1 | .45 ACP | 3-Round Burst | 3 | 1 | 1 | 1 | 1 |
| `P19-CAT-A-FP1-test_004` | FP1 | .45 ACP | Single Shot | 1 | 0 | 1 | 0 | 1 |
| `P19-CAT-A-FP1-test_007` | FP1 | .40 S&W | 3-Round Burst | 3 | 1 | 1 | 1 | 1 |
| `P19-CAT-A-FP1-test_013` | FP1 | 9x19mm | 3-Round Burst | 3 | 0 | 1 | 0 | 1 |
| `P19-CAT-A-FP2-test_019` | FP2 | .45 ACP | 3-Round Burst | 3 | 1 | 1 | 1 | 1 |
| `P19-CAT-A-FP2-test_022` | FP2 | .45 ACP | Single Shot | 1 | 1 | 1 | 1 | 1 |
| `P19-CAT-A-FP2-test_025` | FP2 | .40 S&W | 3-Round Burst | 3 | 1 | 1 | 1 | 1 |
| `P19-CAT-A-FP2-test_031` | FP2 | 9x19mm | 3-Round Burst | 3 | 1 | 1 | **3** (1 alert reused 3x) | **3** (1 alert reused 3x) |
| `P19-CAT-A-FP3-test_037` | FP3 | .45 ACP | 3-Round Burst | 3 | 1 | 1 | **2** (1 alert reused 2x) | **3** (1 alert reused 3x) |
| `P19-CAT-A-FP3-test_040` | FP3 | .45 ACP | Single Shot | 1 | 1 | 1 | 1 | 1 |
| `P19-CAT-A-FP3-test_043` | FP3 | .40 S&W | 3-Round Burst | 3 | 1 | 1 | **3** (1 alert reused 3x) | **3** (1 alert reused 3x) |
| `P19-CAT-A-FP3-test_049` | FP3 | 9x19mm | 3-Round Burst | 3 | 0 | 0 | 0 | 0 |
| `P19-CAT-A-FP4-test_055` | FP4 | .45 ACP | 3-Round Burst | 3 | 1 | 2 | **2** (1 alert reused 2x) | **3** (2 alerts reused 3x) |
| `P19-CAT-A-FP4-test_058` | FP4 | .45 ACP | Single Shot | 1 | 1 | 1 | 1 | 1 |
| `P19-CAT-A-FP4-test_061` | FP4 | .40 S&W | 3-Round Burst | 3 | 1 | 1 | **3** (1 alert reused 3x) | **3** (1 alert reused 3x) |
| `P19-CAT-A-FP4-test_067` | FP4 | 9x19mm | 3-Round Burst | 3 | 0 | 1 | 0 | **2** (1 alert reused 2x) |
| `P19-CAT-A-FP5-test_127` | FP5 | .45 ACP | 3-Round Burst | 3 | 0 | 0 | 0 | 0 |
| `P19-CAT-A-FP5-test_130` | FP5 | .45 ACP | Single Shot | 1 | 1 | 1 | 1 | 1 |
| `P19-CAT-A-FP5-test_133` | FP5 | .40 S&W | 3-Round Burst | 3 | 1 | 1 | **3** (1 alert reused 3x) | **3** (1 alert reused 3x) |
| `P19-CAT-A-FP5-test_139` | FP5 | 9x19mm | 3-Round Burst | 3 | 1 | 1 | **3** (1 alert reused 3x) | **3** (1 alert reused 3x) |
| **TOTALS** | — | — | — | **50** | **15** | **19** | **27** | **33** |

---

## 3. Forensic Analysis of Multi-Credit Alert Reuse

### 3.1. Case Study: `test_031` (9mm 3-Round Burst)
- Ground Truth Rounds:
  - Round 1: $t = 3.562\text{ s}$
  - Round 2: $t = 4.150\text{ s}$
  - Round 3: $t = 4.895\text{ s}$
- Phase 14 Detection:
  - Emitted **exactly one alert**: $[3.36\text{s}, 5.28\text{s}]$ ($\text{duration} = 1.92\text{s}$).
  - In Phase 20 scoring, because all three round timestamps fell within $[3.36\text{s}, 5.28\text{s}]$, EV01, EV02, and EV03 were **all marked `True`**.
  - A single physical dispatch alert was counted as 3 independent detections.
- Phase 17 Detection:
  - Emitted **exactly one alert**: $[0.96\text{s}, 5.28\text{s}]$ ($\text{duration} = 4.32\text{s}$).
  - Similarly, all three rounds fell within this window, and EV01, EV02, and EV03 were **all marked `True`**.

### 3.2. Quantitative Extent of Multi-Crediting
- Out of 50 scheduled rounds, 45 rounds were part of 15 3-round bursts, and 5 rounds were single shots.
- In 6 burst sequences (`test_031`, `test_037`, `test_043`, `test_055`, `test_061`, `test_133`, `test_139`), a single detector alert spanned across multiple rounds.
- Phase 14 gained **12 phantom round detections** from 5 multi-credited alerts ($3 \times 1 + 2 \times 1 + 3 \times 1 + 2 \times 1 + 3 \times 1 + 3 \times 1 + 3 \times 1 - 7 = 12$).
- Phase 17 gained **14 phantom round detections** from 7 multi-credited alerts.

---

## 4. Re-Evaluation Under Strict 1-to-1 Event Matching

Under strict 1-to-1 event matching, an alert can be assigned to at most **one** ground-truth round (assigned to the nearest round in time, provided $|t_{\text{alert}} - t_{\text{round}}| \le 1.0\text{s}$). Any subsequent rounds occurring during the same alert are classified as `MERGED_INTO_EARLIER_ALERT` or `IN_REFRACTORY_COOLDOWN`.

### 4.1. Round-Level 1-to-1 Contingency Table

$$\begin{pmatrix} \text{Both Detected} & \text{Phase 14 Only} \\ \text{Phase 17 Only} & \text{Neither Detected} \end{pmatrix} = \begin{pmatrix} 14 & 1 \\ 5 & 30 \end{pmatrix}$$

- Phase 14 Detected: $14 + 1 = \mathbf{15 / 50\text{ rounds (30.0\%)}}$
- Phase 17 Detected: $14 + 5 = \mathbf{19 / 50\text{ rounds (38.0\%)}}$
- Concordant Pairs: $14 + 30 = 44$
- Discordant Pairs: $b = 1$ (Phase 14 only), $c = 5$ (Phase 17 only). Total discordant = $6$.

### 4.2. Exact McNemar Binomial Test (1-to-1 Standard)
Under the null hypothesis that Phase 14 and Phase 17 have identical round detection sensitivity:
$$P(K \le 1 \text{ or } K \ge 5 \mid N = 6, p = 0.5) = 2 \times \left[ \binom{6}{0}(0.5)^6 + \binom{6}{1}(0.5)^6 \right] = 2 \times \frac{1 + 6}{64} = \frac{14}{64} = \mathbf{0.21875}$$

> [!CAUTION]
> **Loss of Statistical Significance:**  
> The two-sided $p$-value is **$0.21875$**, which is far above the conventional significance threshold ($\alpha = 0.05$). The historical claim of statistical superiority ($p = 0.03125$) is an artifact of multi-crediting.

---

## 5. Recording-Level (Incident-Level) Reassessment

In operational security and dispatch contexts, the critical metric is whether an acoustic system alerts on a gunfire **incident**, regardless of whether individual rounds in a rapid burst are resolved.

Across the $N=20$ recordings:
- Phase 14 detected an incident in **15 / 20 recordings (75.0%)**.
- Phase 17 detected an incident in **18 / 20 recordings (90.0%)**.
- Neither model detected an incident in `test_049` (FP3, 9mm) or `test_127` (FP5, .45 ACP).
- Discordant Recordings: Exactly 3 recordings were detected by Phase 17 but missed by Phase 14:
  - `test_004` (FP1, .45 ACP single shot)
  - `test_013` (FP1, 9mm burst)
  - `test_067` (FP4, 9mm burst)

### 5.1. Incident-Level Contingency Table

$$\begin{pmatrix} \text{Both Detected} & \text{Phase 14 Only} \\ \text{Phase 17 Only} & \text{Neither Detected} \end{pmatrix} = \begin{pmatrix} 15 & 0 \\ 3 & 2 \end{pmatrix}$$

- Discordant Pairs: $b = 0, c = 3$. Total discordant = $3$.
- Exact Two-Sided McNemar Binomial Test:
  $$p = 2 \times (0.5)^3 = \frac{2}{8} = \mathbf{0.2500}$$
- The recording-level difference is **NOT statistically significant** ($p = 0.2500 > 0.05$).

---

## 6. Methodological Limits of Controlled Data & Safety Mandates

1. **Extreme Exposure Limitation (140 Seconds of Silence):**  
   The entire 20-recording dataset contains only $140.0\text{ seconds}$ of quiescent background audio. The Garwood 95% Poisson confidence limit on false alerts is:
   $$\text{FAR}_{\text{upper}} = \frac{-\ln(0.05)}{140.0\text{ s}} \times 3600 = \mathbf{77.03\text{ alerts/hour}}$$
   A detector with an unacceptably high operational false-alarm rate (e.g. 50 false alarms per hour) would produce zero false alarms in 140 seconds with $86\%$ probability. Controlled firing data cannot evaluate false-alarm susceptibility.
2. **Artificial Acoustics:**  
   Stationary microphones, pre-arranged firing lanes, and known calibers do not represent real-world acoustic multipath, urban canyon reverberation, or moving vehicular occlusion.
3. **Mandatory Research Designation:**  
   Live-fire testing and hazardous acoustic experiments are strictly prohibited. These historical controlled recordings represent archival research artifacts and must never be used to claim operational life-safety readiness.

