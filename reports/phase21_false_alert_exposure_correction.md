# Phase 21: Category A False-Alert Exposure Timeline Correction & Poisson Bound Audit

> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY**  
> *This experimental acoustic machine-learning system is not certified and must never be used for autonomous emergency dispatch, police response, active-shooter alerting, automated evacuation, or critical physical security. Use legally obtained recorded audio and safe playback only. No live-fire testing or hazardous acoustic experiments.*

---

## 1. Executive Summary

Phase 19 and Phase 20 reported that the frozen detectors achieved **100.00% precision (0 false alarms)** on the 20 Category A recordings (ShotSpotter Pittsburgh PA DQV 2018).

This audit corrects the exposure calculation:
1. **Total Recorded Audio:** 20 recordings $\times 10.0000\text{ s} = 200.0000\text{ s}$ ($0.0556\text{ hours}$).
2. **Event-Associated Audio:** Active gunshot waveforms and ground-truth matching windows $[t-0.5\text{ s}, t+1.5\text{ s}]$ occupy **59.584\text{ seconds}** (~59.6s).
3. **Refractory Cooldown Exclusion:** Detector refractory periods $[t-0.2\text{ s}, t+2.0\text{ s}]$ occupy **63.584\text{ seconds}** (~63.6s).
4. **Eligible Negative-Background Exposure:**
   - Under the ground-truth matching window definition: **140.416\text{ seconds}** (~$2.34\text{ minutes}$).
   - Under nominal rounded reporting: **140.0000\text{ seconds}** ($0.0389\text{ hours}$).
   - Under detector refractory exclusion: **136.416\text{ seconds}** ($0.0379\text{ hours}$).

### Key Finding:
Using the nominal 140-second negative exposure, the exact one-sided 95% Garwood Poisson upper confidence bound is:
$$\lambda_{\text{upper}} = \frac{-\ln(0.05)}{140 / 3600} = \frac{2.99573}{0.03889} = \mathbf{77.033\text{ alerts/hour}}$$
Observing zero false alarms over 140 seconds only allows us to conclude that the false alert rate is **below 77 false alarms per hour** (one false alarm every 47 seconds). 

**Category A provides zero statistical power to substantiate claims of low false-alarm rates in operational environments.**

---

## 2. Mathematical Poisson Upper Bounds Across Four Exposure Scenarios

| Exposure Definition | Duration (s) | Duration (hr) | Observed False Alerts ($k$) | Exact Garwood 95% Upper Bound ($\lambda_{\text{upper}}$) | Methodological Assessment |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **1. Total Recorded Audio** | $200.000\text{ s}$ | $0.0556\text{ hr}$ | 0 | **$53.923\text{ alerts/hr}$** | **Methodologically Flawed:** Erroneously treats active gunfire coda and cooldown as negative background. |
| **2. Eligible Matching Window** | $140.416\text{ s}$ | $0.03900\text{ hr}$ | 0 | **$76.805\text{ alerts/hr}$** | **Recommended:** Excludes ground-truth matching intervals $[t-0.5, t+1.5]$. |
| **3. Nominal 140s Baseline** | $140.000\text{ s}$ | $0.0389\text{ hr}$ | 0 | **$77.033\text{ alerts/hr}$** | **Canonical Formula:** Direct evaluation of $-\ln(0.05) / (140/3600)$. |
| **4. Strict Refractory Window** | $136.416\text{ s}$ | $0.03789\text{ hr}$ | 0 | **$79.057\text{ alerts/hr}$** | **Hardware Reality:** Excludes all intervals where detector was refractory-inhibited. |

---

## 3. Comparison with the Phase 18 Continuous Negative Benchmark

To assess operational false alarm rates, long-duration continuous audio with verified zero gunfire is required. The table below contrasts Category A against the benchmark established in Phase 16/18:

| Dataset / Benchmark | Nature of Audio | Total Exposure | Phase 14 Balanced False Alerts | Empirical FAR (alerts/hr) | Phase 14 High-Precision FAR |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **Phase 21 Category A (Pittsburgh)** | Controlled Live-Fire Urban Clips | **$0.0389\text{ hours}$** ($140\text{ s}$) | 0 | $\le \mathbf{77.03\text{ alerts/hr}}$ (95% bound) | $\le \mathbf{77.03\text{ alerts/hr}}$ (95% bound) |
| **Phase 18 Natural Continuous Negative** | Unbroken natural urban & environmental | **$6.0800\text{ hours}$** ($21,888\text{ s}$) | 6 | **$0.987\text{ alerts/hr}$** (95% CI: $[0.36, 2.15]$) | **$0.000\text{ alerts/hr}$** ($\le \mathbf{0.493\text{ alerts/hr}}$ bound) |

### Contrast:
- Phase 18 evaluated **$6.08\text{ hours}$** of unbroken audio, placing the High-Precision profile false-alarm upper bound at **$< 0.493\text{ alerts/hour}$**.
- Category A evaluated **$0.0389\text{ hours}$** of quiescent audio, yielding an upper bound of **$< 77.033\text{ alerts/hour}$** ($156\times$ looser).

---

## 4. Exposure Accounting by Stream

Detailed second-by-second breakdown across all 20 recordings is archived in [phase21_negative_exposure_timeline.csv](file:///e:/gunshot/gunshot/reports/phase21_negative_exposure_timeline.csv).

---
*Report certified under Phase 21 Forensic Audit protocol.*
