# Phase 31: Historical Positive Validation Context Report
## Retrospective Audit of Pittsburgh DQV 2018 Controlled Data & Methodological Boundaries

**Document ID:** `REPORT-PHASE31-POSITIVE-001`  
**Phase:** 31 (Historical Positive Validation Context)  
**Date:** November 2026  
**Status:** REPRODUCED HISTORICAL BENCHMARK & METHODOLOGICAL SAFEGUARDS  

---

### MANDATORY SAFETY DESIGNATION
> [!CAUTION]
> **RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.**  
> This experimental acoustic machine-learning software is uncertified and must never be deployed for autonomous emergency dispatch, tactical police response, active-shooter alerting, automated evacuation, building lockdown, or life-critical physical security. Use legally obtained recordings and safe audio playback only. Live-fire testing and hazardous acoustic experiments are strictly prohibited. Historical controlled-validation recordings may be analysed only as existing research data; do not conduct new firing experiments.

---

## 1. Executive Summary & Contextual Boundaries

Historical discussions in Phase 20 and Phase 21 highlighted an unadjusted statistical result on the Pittsburgh DQV 2018 controlled gunfire validation dataset:
- Phase 17 Experimental detected 33 out of 50 annotated rounds (66.0% event-level recall).
- Phase 14 Balanced detected 27 out of 50 annotated rounds (54.0% event-level recall).
- The paired McNemar exact binomial test yielded $p = 0.03125$ ($6\text{ discordant pairs}, 0\text{ vs }6$).

Phase 31 conducted an independent reproduction of these historical results directly from `reports/phase20_canonical_event_manifest.csv` and `reports/phase20_event_accounting.json`, while formally establishing the **essential methodological distinctions** that prevent generalizing controlled firing scores to real-world operational safety.

---

## 2. Reproduction of Historical Pittsburgh Metrics

### 2.1. Dataset Composition
- **Source Corpus:** Pittsburgh Data Quality Validation (DQV) 2018 Controlled Firing Study.
- **Recording Count:** 20 short audio recordings (10.0 seconds each, total gross duration $= 200.0\text{ s} = 0.0556\text{ hr}$).
- **Firing Positions:** 5 distinct fixed municipal positions (unaligned arbitrary Cartesian coordinate origins).
- **Annotated Events:** Exactly 50 physical firearm discharge rounds (Category A: natural continuous multi-shot and single-shot sequences).
- **Quiescent Background Duration:** Only $140.0\text{ s}$ of audio represents background noise without gunshot transients.

### 2.2. Detector Performance Comparison (Category A, N=50)

| Detector Model | Architectural Role | Annotated Rounds | Detected Rounds | Event Recall | Paired vs Phase 14 |
| :--- | :--- | :---: | :---: | :---: | :--- |
| **Phase 14 Balanced** | Default Research Baseline | 50 | 27 | **54.0%** | Baseline |
| **Phase 17 Experimental** | Selectable Experimental Profile | 50 | 33 | **66.0%** | $+6$ rounds ($+12.0\%$) |
| **Phase 9 Balanced** | Historical Comparator | 50 | 28 | **56.0%** | $+1$ round ($+2.0\%$) |
| **Phase 14 High-Precision** | Historical Comparator | 50 | 24 | **48.0%** | $-3$ rounds ($-6.0\%$) |
| **Phase 14 High-Sensitivity** | Historical Comparator | 50 | 22 | **44.0%** | $-5$ rounds ($-10.0\%$) |
| **Phase 13 Balanced** | Historical Comparator | 50 | 16 | **32.0%** | $-11$ rounds ($-22.0\%$) |

### 2.3. Paired McNemar Contingency Table (Phase 14 vs Phase 17)

$$\begin{pmatrix} \text{Both Detected} & \text{Phase 14 Only} \\ \text{Phase 17 Only} & \text{Neither Detected} \end{pmatrix} = \begin{pmatrix} 27 & 0 \\ 6 & 17 \end{pmatrix}$$

- Total Discordant Pairs: $b + c = 0 + 6 = 6$
- Exact Two-Sided Binomial Test:
  $$p = 2 \times \left(\frac{1}{2}\right)^6 = \frac{2}{64} = 0.03125$$
- The historical event-level difference is **100% reproducible**.

---

## 3. Mandatory Methodological Safeguards & Three Distinct Acoustic Domains

It is scientifically invalid to combine controlled validation results with natural continuous negative exposure into a single undifferentiated summary metric. Phase 31 strictly demarcates three non-interchangeable domains:

```
+--------------------------------------------------------------------------------------------------+
|                                THREE ACOUSTIC RESEARCH DOMAINS                                   |
+------------------------------------+-----------------------------+-------------------------------+
| 1. Scheduled Controlled Firing     | 2. Continuous Ambient Audio | 3. Unexpected Real-World Gunfire |
+------------------------------------+-----------------------------+-------------------------------+
| - Stationary microphones           | - 12.65 hours of authentic  | - Complex multi-path reflection |
| - Known calibers and positions     |   unbroken background noise | - Occlusion by vehicles/walls |
| - High SNR, predictable acoustics  | - Urban, rural, aviation    | - Variable calibers/angles    |
| - Only 200s total exposure         | - Evaluates FALSE ALARMS    | - Human panic & urban echoes  |
| - Cannot measure operational FAR   | - Zero firearms discharge   | - UNTESTED & UNCERTIFIED      |
+------------------------------------+-----------------------------+-------------------------------+
```

### 3.1. Why Controlled Firing Cannot Measure False-Alert Rate
With only $140\text{ seconds}$ of quiescent audio in Pittsburgh DQV 2018:
$$\text{Garwood 95\% Poisson Upper Limit} = \frac{-\ln(0.05)}{140.0\text{ s}} \times 3600 = 77.03\text{ alerts/hour}$$
A detector that generates 70 false alarms per hour would exhibit zero false alarms during a 140-second test window with $> 95\%$ probability! Controlled datasets are statistically powerless to detect false-alarm vulnerability.

### 3.2. Why Controlled Recall Does Not Imply Real-World Sensitivity
In controlled live-fire tests, weapon orientations, distances, and calibers are pre-planned. The acoustic channel lacks the unpredictable acoustic scattering, building corner diffraction, moving vehicular noise floors, and atmospheric temperature inversions typical of unexpected municipal gunfire.

### 3.3. Ban on Live-Fire Testing
In accordance with project safety guidelines:
- No new live-fire testing or hazardous acoustic experiments shall be conducted.
- Historical controlled validation data is retained solely as frozen archival research records.
- Real-world detection sensitivity must never be claimed or inferred from historical controlled recordings.

