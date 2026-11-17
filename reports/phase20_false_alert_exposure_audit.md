# Phase 20: False-Alert Exposure and Negative Duration Audit

> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY**  
> *This experimental acoustic machine-learning system is not certified and must never be used for autonomous emergency dispatch, police response, active-shooter alerting, automated evacuation, or critical physical security. Use legally obtained recorded audio and safe playback only. No live-fire testing or hazardous acoustic experiments.*

---

## 1. Executive Summary

In Phase 19, the evaluation of Category A (ShotSpotter Pittsburgh PA DQV 2018 dataset) reported:
> *"100.00% Event Precision (0 False Alarms observed across 20 continuous recordings)."*

While technically accurate as a discrete accounting statistic over the evaluated files, interpreting this metric as evidence of a negligible false-alarm rate in operational deployments represents a serious methodological fallacy.

This forensic audit analyzes the actual temporal exposure of Category A, separates event-associated acoustic duration from quiescent background exposure, computes exact Poisson upper confidence limits, and contrasts Category A with the multi-hour continuous negative benchmarks established in Phase 16 and Phase 17.

---

## 2. Temporal Exposure Decomposition

Category A comprises exactly 20 recordings, each with a duration of $10.000000\text{ seconds}$, yielding:
$$\text{Total Exposure Duration} = 20 \times 10.000000\text{ s} = 200.000\text{ s} \quad (\approx 3\text{ minutes, } 20\text{ seconds})$$

### 2.1 Event-Associated vs. Quiescent Background Exposure
Each of the 20 recordings contains either a single shot, a 2-round pair, or a 3-round burst, along with ballistic reverberation and the detector's 2.0-second refractory cooldown:

- **Active Ballistic Duration:** Each physical discharge comprises the initial shockwave/blast ($10$–$50\text{ ms}$) and an urban reverberant decay coda ($0.5$–$1.2\text{ s}$).
- **Detector Refractory Cooldown:** Following an alert trigger, the detector enforces a $2.0\text{ s}$ refractory cooldown during which subsequent triggers are suppressed.
- **Event-Associated Exposure:** Across the 20 recordings, active firing sequences and their mandatory suppression windows occupy approximately **$2.5$ to $3.5\text{ seconds}$ per recording**, totaling:
  $$T_{\text{event}} \approx 20 \times 3.0\text{ s} = 60.0\text{ s}$$
- **Quiescent Ambient Exposure:** The remaining audio consists of pre-shot ambient lead-in ($1.5$–$3.5\text{ s}$) and post-shot tail ($2.5$–$4.5\text{ s}$):
  $$T_{\text{quiescent}} = 200.0\text{ s} - 60.0\text{ s} = 140.0\text{ s} \quad (\approx 2\text{ minutes, } 20\text{ seconds})$$

Consequently, claiming that Category A tests false-positive resistance relies on only **140 seconds (~2.33 minutes) of non-event urban acoustic background**.

---

## 3. Mathematical Poisson Upper Bounds on False Alarm Rate

When zero events ($k = 0$) are observed over an observation duration $T$, the true underlying event arrival rate $\lambda$ (under a homogeneous Poisson process) is bounded by the exact Garwood / Chi-Squared distribution. 

At a confidence level $1 - \alpha = 0.95$ ($\alpha = 0.05$):
$$\lambda_{\text{upper}} = \frac{-\ln(\alpha)}{T} = \frac{-\ln(0.05)}{T} \approx \frac{2.99573}{T}$$

### 3.1 Calculated Bounds for Category A

| Exposure Scope | Observation Time ($T$) | Observed False Alarms ($k$) | Upper 95% Bound ($\lambda_{\text{upper}}$) | Upper 95% False-Alert Rate (per hour) |
| :--- | :---: | :---: | :---: | :---: |
| **Total Audio Duration** | $200.0\text{ s}$ ($0.0556\text{ hr}$) | 0 | $0.01498\text{ alerts/s}$ | **$53.92\text{ alerts/hour}$** |
| **Quiescent Background Only** | $140.0\text{ s}$ ($0.0389\text{ hr}$) | 0 | $0.02140\text{ alerts/s}$ | **$77.03\text{ alerts/hour}$** |

### 3.2 Scientific Interpretation of the Bound
Observing zero false alarms over $200.0\text{ seconds}$ only allows us to conclude with 95% confidence that the false alert rate is **less than $53.9\text{ alerts per hour}$**. 

An alert rate of $50\text{ alerts/hour}$ is roughly **one false alarm every 72 seconds**—a catastrophic failure rate for any practical monitoring system. Thus, achieving 100% precision over $200\text{ seconds}$ is mathematically consistent with an unacceptably noisy detector.

---

## 4. Comparison with Validated Long-Duration Continuous Benchmarks

To obtain statistically meaningful bounds on false alarms, long continuous recordings with zero gunfire are required. The table below places Category A alongside the multi-hour continuous negative benchmarks evaluated in Phase 16 and Phase 17:

| Evaluation Dataset / Benchmark | Nature of Audio | Total Duration | Phase 14 Balanced False Alerts | Phase 14 Balanced FAR (alerts/hr) | Phase 14 High-Precision FAR |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **Phase 20 Category A (Pittsburgh)** | Controlled Live-Fire Urban Clips | **$0.056\text{ hours}$** ($200\text{ s}$) | 0 | $\le 53.92$ (95% CI bound) | $\le 53.92$ (95% CI bound) |
| **Phase 15 ESC-50 Spliced Continuous** | Spliced 5-second acoustic tracks | $2.00\text{ hours}$ | 70 | $35.00\text{ alerts/hr}$ | $20.00\text{ alerts/hr}$ |
| **Phase 16 Natural Continuous Negative** | Unbroken environmental audio | **$6.08\text{ hours}$** | 6 | **$0.99\text{ alerts/hr}$** | **$0.00\text{ alerts/hr}$** |
| **Phase 17 Animal Vocalization Negative** | Rural wildlife & domestic animals | $1.50\text{ hours}$ | 11 | $7.33\text{ alerts/hr}$ | $2.67\text{ alerts/hr}$ |

### Key Findings:
1. **Long-Duration Benchmarks Are Indispensable:** Only the Phase 16 benchmark ($6.08\text{ hours}$) possessed sufficient temporal duration to establish that Phase 14 Balanced achieves approximately $\sim 0.99\text{ alerts/hour}$ and Phase 14 High-Precision achieves zero observed alerts ($< 0.49\text{ alerts/hour}$ upper bound).
2. **Category A Is Exclusively a Sensitivity Benchmark:** Category A provides valuable validation of **detection recall under urban reverberation**, but provides **zero statistical power** to assess operational false-alarm resistance.

---

## 5. Methodological Recommendations

1. **Explicitly Label Category A as a Positive-Detection Benchmark:** In all technical reporting, Category A must be described as an acoustic sensitivity/recall evaluation set, not a false-alarm test.
2. **Never Quote Precision in Isolation:** Where precision is reported on brief positive clips, it must be accompanied by the total non-event duration and the Poisson upper rate limit.
3. **Maintain Phase 16/17 Continuous Negative Sets as Mandatory Gates:** Any future model candidate (e.g., Phase 17 Experimental) seeking production promotion must be evaluated across the full $6.08$-hour continuous negative benchmark before deployment consideration.

---
*Report certified under Phase 20 Forensic Audit protocol.*

