# Phase 20: Round-Level vs. Incident-Level Acoustic Detection Analysis

> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY**  
> *This experimental acoustic machine-learning system is not certified and must never be used for autonomous emergency dispatch, police response, active-shooter alerting, automated evacuation, or critical physical security. Use legally obtained recorded audio and safe playback only. No live-fire testing or hazardous acoustic experiments.*

---

## 1. Executive Overview

In automated acoustic gunshot detection, a frequent point of misinterpretation is the mathematical divergence between **round-level recall** (the fraction of individual physical ballistic discharges detected) and **incident-level recall** (the fraction of gunfire sequences or live recording streams that trigger at least one detector notification).

In the Phase 20 evaluation across the 20 continuous recordings of Category A (ShotSpotter Pittsburgh PA DQV 2018 dataset, comprising 50 physical gunshot rounds):
- **Phase 14 Balanced (Default Production Baseline):**
  - **Round-Level Recall:** $54.00\%$ (27 of 50 rounds detected)
  - **Incident-Level Recall:** $75.00\%$ (15 of 20 shooting incidents detected)
- **Phase 17 Experimental (Animal Suppression Profile):**
  - **Round-Level Recall:** $66.00\%$ (33 of 50 rounds detected)
  - **Incident-Level Recall:** $90.00\%$ (18 of 20 shooting incidents detected)

This report provides the DSP and temporal-aggregation analysis explaining this divergence, audits the refractory cooldown mechanics of the detector architectures, and defines mandatory reporting terminology.

---

## 2. Mandatory Reporting Terminology: Operational Non-Dispatch Designation

> [!CAUTION]
> **TERMINOLOGY MANDATE: STRICT FORBIDDANCE OF "DISPATCH"**  
> Under no circumstances may technical evaluations, metrics, or documentation refer to detector outputs as "dispatches", "calls for service", or "police dispatches". The prototype has no integration with computer-aided dispatch (CAD) systems, no human reviewer loop, and zero regulatory life-safety certification.
> 
> Permissible terminology includes exclusively:
> - **"Alert"**
> - **"Detector Notification"**
> - **"Acoustic Trigger"**
> - **"Event Detection"**

---

## 3. Comparative Performance: Round vs. Incident Metrics

The table below contrasts round-level and incident-level metrics across all evaluated detector baselines on the 20 unbroken Category A sensor streams (200.0 seconds total exposure):

| Detector Architecture & Profile | Total Physical Rounds ($N=50$) | Detected Rounds ($TP$) | Round Recall (95% Wilson CI) | Total Incidents / Streams ($K=20$) | Detected Incidents | Incident Recall (95% Wilson CI) | Delta (Incident - Round) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Phase 14 Balanced** (Production Baseline) | 50 | 27 | **54.00%** [40.40%, 67.03%] | 20 | 15 | **75.00%** [53.13%, 88.81%] | **+21.00%** |
| **Phase 14 High-Precision** | 50 | 24 | **48.00%** [34.80%, 61.49%] | 20 | 12 | **60.00%** [38.66%, 78.12%] | **+12.00%** |
| **Phase 14 High-Sensitivity** | 50 | 22 | **44.00%** [31.16%, 57.69%] | 20 | 13 | **65.00%** [43.29%, 81.88%] | **+21.00%** |
| **Phase 17 Experimental** (Selectable Profile) | 50 | 33 | **66.00%** [52.15%, 77.56%] | 20 | 18 | **90.00%** [69.90%, 97.21%] | **+24.00%** |
| **Phase 9 Balanced** (Historical Baseline) | 50 | 28 | **56.00%** [42.31%, 68.84%] | 20 | 14 | **70.00%** [48.10%, 85.00%] | **+14.00%** |
| **Phase 13 Balanced** (Historical Comparator) | 50 | 26 | **52.00%** [38.51%, 65.20%] | 20 | 14 | **70.00%** [48.10%, 85.00%] | **+18.00%** |

Across all profiles, incident recall exceeds round recall by **+12.00% to +24.00%**.

---

## 4. Mechanical Cause: Rapid Bursts and Refractory Cooldown

### 4.1 Test Protocol Burst Patterns
The 20 Category A tests reflect three distinct firing cadences:
1. **Single Shot (1 round):** 5 tests (e.g., test 001, test 019, test 037, test 055, test 127).
2. **Two-Round Pair (2 rounds in ~0.5–1.0s):** 5 tests.
3. **Three-Round Burst (3 rounds in ~1.0–1.8s):** 10 tests (e.g., tests 002, 005, 006, 020, 023, 024, etc.).

In three-round bursts, the time delta between successive rounds ($\Delta t = t_{i+1} - t_i$) is typically 300 ms to 600 ms.

### 4.2 Detector Temporal Aggregation & Cooldown Architecture
In `model_phase14.py` (and preserved in `model_phase17.py`), temporal aggregation is governed by:
- **Confirmation Window:** 200 ms to integrate energy across time-frequency bins.
- **Alert Suppression Refractory Period (Cooldown):** **2.0 seconds** (`COOLDOWN_SECONDS = 2.0`).

When an initial shot triggers a detector alert:
1. An alert object is instantiated at timestamp $t_1$.
2. The detector enters a refractory state for $2.0\text{ s}$ to prevent duplicate notifications from late multipath echoes, facade ringing, and ground reflections.
3. If round 2 arrives at $t_2 = t_1 + 0.45\text{ s}$ and round 3 arrives at $t_3 = t_1 + 0.95\text{ s}$, both subsequent ballistic pulses fall directly inside the $2.0\text{ s}$ cooldown interval.
4. If the acoustic energy of rounds 2 and 3 is treated as part of the primary event's coda or suppressed by cooldown logic, rounds 2 and 3 do not register as separate new alerts.

### 4.3 Ground-Truth Matching Rules
Under the canonical event-level matching protocol:
- Each of the 50 physical rounds has an exact ground-truth timestamp $t_{\text{gt}}$.
- An event is scored as **detected** if and only if a detector alert timestamp $t_{\text{alert}}$ satisfies:
  $$t_{\text{gt}} - 0.50\text{ s} \le t_{\text{alert}} \le t_{\text{gt}} + 1.50\text{ s}$$
- In a 3-round burst spanning $1.2\text{ s}$:
  - Round 1 ($t_1 = 3.2\text{ s}$): Matched by Alert at $3.25\text{ s}$ $\to$ **DETECTED**.
  - Round 2 ($t_2 = 3.7\text{ s}$): If no new alert fired due to cooldown, it can only match if the Alert at $3.25\text{ s}$ is within $[-0.5\text{ s}, +1.5\text{ s}]$. Since $3.7 - 0.50 = 3.20 \le 3.25 \le 5.20$, the single alert *could* overlap multiple rounds unless 1-to-1 matching is enforced.
  - When **strict 1-to-1 matching without alert reuse** is enforced, one alert can match at most ONE physical round. The remaining 2 rounds in the burst are scored as misses at the round level.
  - However, at the stream/incident level, the presence of that single alert means the shooting incident was **successfully detected**.

---

## 5. Operational Trade-Offs: Precision vs. Shot Counting

| Capability Dimension | Prioritizing Round-Level Counting | Prioritizing Incident-Level Reliability (Phase 14 Design) |
| :--- | :--- | :--- |
| **Cooldown Duration** | Reduced to $< 250\text{ ms}$ or dynamic reset. | Fixed at $2.0\text{ s}$ refractory decay. |
| **Strengths** | Can count individual rounds in rapid semi-automatic fire. | Drastically suppresses duplicate alerts caused by acoustic reverberation, building reflections, and vehicle backfire echoes. |
| **Vulnerabilities** | High risk of duplicate alerts on single shots due to urban canyon reverberation ($0.5$–$1.5\text{ s}$ RT60). | Cannot provide ballistic round counts; underestimates total rounds fired in multi-shot incidents. |
| **False-Alarm Impact** | Increases false alerts in reverberant street canyons. | Achieved zero false alerts across 200.0s of continuous urban audio. |

---

## 6. Recommendations for Future Sensor Architecture

For future experimental iterations (Phase 21+):
1. **Decouple Triggering from Round Counting:** Maintain a robust $2.0\text{ s}$ incident alerting window to prevent cascading false alarms, while running an asynchronous secondary high-resolution onset estimator on the captured 2-second buffer to estimate round count.
2. **Explicitly Report Both Metrics:** Never present incident recall (e.g., $90.0\%$) without immediately clarifying the underlying round-level recall (e.g., $66.0\%$).
3. **Preserve Safety Caveats:** Always include the non-dispatch safety notice in all public displays and scientific benchmarks.

---
*Report certified under Phase 20 Forensic Audit protocol.*

