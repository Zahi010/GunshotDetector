# PHASE 39 METRIC RECONCILIATION & PHASE 38 REPRODUCTION REPORT
## Independent Reproduction of False-Alert Rates, Positive Clip Sensitivity & Distractor Triggers

> [!CAUTION]
> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.**
> This software is uncertified research code. It must never be deployed for autonomous emergency dispatch, police tactical response, active-shooter alerting, automated evacuation, building lockdown, or life-critical physical security.
> Use lawfully obtained recordings and safe audio playback only. Live-fire testing and hazardous acoustic experiments are strictly prohibited.

---

## 1. Executive Summary

All primary metrics reported in Phase 38 have been reproduced with 100% numerical concordance from the frozen model files and feature caches.

### Key Audit Findings:
1. **Positive Sensitivity Reproduction:**
   - **Phase 14 Balanced (COND1):** Exactly **74/120 detected** (61.7% clip-level recall, 46 FN).
   - **Phase 36 Complete (COND6):** Exactly **77/120 detected** (64.2% clip-level recall, 43 FN).
   - False Positives on positive clips were 0 by construction ($FP = 0$), because any alert was attributed to the labeled gunshot clip.
2. **Continuous Background Exposure & FAR Reproduction:**
   - Evaluated Exposure: Exactly **7,032.35 seconds = 1.9534 hours** across 7 unedited field streams.
   - **Phase 14 (COND1):** Exactly 4 alerts -> Gross FAR = **2.0478 / hr** (Exact Poisson 95% CI: [0.56, 5.24]). Convention B excluded time = 108.00 s -> Conv B FAR = 2.0797 / hr.
   - **Phase 17 Defective (COND2):** Exactly 21 alerts -> Gross FAR = **10.7510 / hr** (Exact Poisson 95% CI: [6.66, 16.44]). Convention B excluded time = 702.66 s -> Conv B FAR = 11.9442 / hr. (Defect fully reproduced: unconfirmed cluster candidate leakage causes 5.2x FAR inflation).
   - **Phase 36 (COND6):** Exactly 3 alerts -> Gross FAR = **1.5359 / hr** (Exact Poisson 95% CI: [0.32, 4.49]). Convention B excluded time = 88.50 s -> Conv B FAR = 1.5554 / hr.
3. **The Duplicate-Alert Rate Formula Audit:**
   - **Exact Formula:**
     $$\text{Duplicate Alert Rate} = \frac{\text{Duplicate Alerts}}{\text{True Positive Clips} + \text{Duplicate Alerts}} = \frac{\sum (k_i - 1)}{\sum k_i}$$
     where $k_i$ is the number of alerts emitted in clip $i$ for clips with $k_i \ge 1$.
   - **Numerator:** The count of excess alerts emitted beyond the first alert on detected positive clips. (Phase 14: 28 excess alerts; Phase 36: 13 excess alerts).
   - **Denominator:** The total number of alerts emitted across all detected clips (Phase 14: $74 + 28 = 102$ alerts; Phase 36: $77 + 13 = 90$ alerts).
   - **Unit:** **Emitted alerts** (the proportion of emitted alerts that represent duplicate or fragmented triggers within already-detected clips).
   - **Result:**
     - Phase 14: $28 / 102 = 27.45\% \approx 27.5\%$
     - Phase 36: $13 / 90 = 14.44\% \approx 14.4\%$
     - Phase 36 almost halved the rate of redundant, fragmented alerts during active gunfire clips.
4. **Distractor Trigger Rates Reproduction:**
   - Phase 14 triggered on **16 / 120 distractor clips** (13.33%, 95% CI: [7.8%, 20.7%]).
   - Phase 36 triggered on **23 / 120 distractor clips** (19.17%, 95% CI: [12.6%, 27.4%]).
   - **Fireworks Challenge Set:**
     - Phase 14: 8 / 20 clips triggered (40.0%).
     - Phase 36: 11 / 20 clips triggered (55.0%).
     - Difference on fireworks: +15.0% absolute increase for Phase 36 due to pyrotechnic acoustic blast transients passing crest-factor and spectral energy tests.

---

## 2. Six-Condition Reproduction Matrix

| Condition ID | Architecture Profile | False Alerts (Conv A) | Gross FAR (/hr) | Conv B Excluded (s) | Positive Detected (TP) | Positive FN | Positive FP | Duplicate Rate | Distractor Triggers | Fireworks Triggers |
|---|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **COND1** | Phase 14 Balanced | 4 | 2.0478 | 108.00 s | 74 / 120 | 46 | 0 | 27.5% (28/102) | 16 / 120 (13.3%) | 8 / 20 (40.0%) |
| **COND2** | Phase 17 Defective | 21 | 10.7510 | 702.66 s | 81 / 120 | 39 | 0 | 22.5% (24/105) | 23 / 120 (19.2%) | 11 / 20 (55.0%) |
| **COND3** | Phase 31 State Reset | 4 | 2.0478 | 118.00 s | 75 / 120 | 45 | 0 | 22.5% (22/97) | 18 / 120 (15.0%) | 9 / 20 (45.0%) |
| **COND4** | Phase 36 Clean FSM | 4 | 2.0478 | 118.00 s | 77 / 120 | 43 | 0 | 14.4% (13/90) | 23 / 120 (19.2%) | 11 / 20 (55.0%) |
| **COND5** | Phase 36 Conservative | 3 | 1.5359 | 88.50 s | 77 / 120 | 43 | 0 | 14.4% (13/90) | 23 / 120 (19.2%) | 11 / 20 (55.0%) |
| **COND6** | Phase 36 Complete | 3 | 1.5359 | 88.50 s | 77 / 120 | 43 | 0 | 14.4% (13/90) | 23 / 120 (19.2%) | 11 / 20 (55.0%) |

All reproduced values match Phase 38 files bit-for-bit.

Full CSV table: [phase39_phase38_reproduction.csv](file:///E:/gunshot/gunshot/experiments/phase39/phase39_phase38_reproduction.csv).
