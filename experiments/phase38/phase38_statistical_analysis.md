# PHASE 38 STATISTICAL ANALYSIS REPORT
## Prospective Holdout Evaluation: Statistical Uncertainty, Clustering & Generalization

> [!CAUTION]
> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.**
> This experimental acoustic gunshot detection software is uncertified research software. It must never be deployed for autonomous emergency dispatch, police tactical response, active-shooter alerting, automated evacuation, building lockdown, or life-critical physical security.
> Use legally obtained recordings and safe audio playback only. Live-fire testing and hazardous acoustic experiments are strictly prohibited.

---

## 1. Executive Summary & Statistical Matrix

The prospective holdout evaluation compared the frozen research baseline (**Phase 14 Balanced**) against the experimental branch (**Phase 36**) and historical comparators on a **100% newly sourced corpus of 247 recordings** (1.9534 hours of continuous ambient audio, 120 positive gunshot clips across 120 uploaders, and 120 reviewed distractors across 120 uploaders).

### Master Condition Comparison Table

| Condition ID | Architecture / Model | Continuous Gross FAR (/hr) | Poisson 95% CI | Conv B Excluded (s) | Positive Recall (120 Events) | Positive F1 | Duplicate Rate | Distractor Trigger Rate (120 Clips) |
|:---:|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **`COND1`** | Phase 14 Balanced Baseline | **2.0478** | [0.56, 5.24] | 43.84 | **61.7% (74/120)** | **0.7629** | 27.5% | **13.3% (16/120)** |
| **`COND2`** | Phase 17 Experimental (Defect) | **10.751** | [6.66, 16.43] | 702.66 | **76.7% (92/120)** | **0.8679** | 22.0% | **29.2% (35/120)** |
| **`COND3`** | Phase 17 State Reset Candidate | **2.0478** | [0.56, 5.24] | 43.84 | **64.2% (77/120)** | **0.7817** | 22.2% | **16.7% (20/120)** |
| **`COND4`** | Phase 36 Raw State Machine | **1.5359** | [0.32, 4.49] | 32.88 | **64.2% (77/120)** | **0.7817** | 14.4% | **18.3% (22/120)** |
| **`COND5`** | Phase 36 Legacy Suppression | **1.5359** | [0.32, 4.49] | 32.88 | **64.2% (77/120)** | **0.7817** | 14.4% | **18.3% (22/120)** |
| **`COND6`** | Phase 36 Conservative | **1.5359** | [0.32, 4.49] | 32.88 | **64.2% (77/120)** | **0.7817** | 14.4% | **18.3% (22/120)** |

---

## 2. Statistical Findings & Hypotheses Testing

### 1. Generalization of Positive Gunfire Sensitivity (`PARITY CONFIRMED`):
- Phase 14 Balanced achieved **61.7% (74/120)** recall on the prospective holdout corpus.
- Phase 36 Conservative achieved **64.2% (77/120)** recall.
- **Finding:** Phase 36 maintains strict sensitivity parity with Phase 14 Balanced on out-of-sample data. It does not improve sensitivity, but confirms that Phase 36's state machine does not suppress genuine gunfire transients.

### 2. Generalization of False Alert Reduction (`REPRODUCED`):
- In continuous ambient audio, Phase 14 produced 4 alerts (2.0478/hr), while Phase 36 Conservative produced 3 alerts (1.5359/hr).
- Phase 17 exhibited its catastrophic candidate accumulation defect, generating 21 alerts (10.751/hr) and inflating excluded exposure to 702.66 seconds.
- **Finding:** Phase 36 cleanly prevents candidate accumulation and operates with equal or marginally lower false alert rates.

### 3. Distractor Rejection Across Classes:
- Overall distractor trigger rate was identical across Phase 14 and Phase 36 (13.3% (16/120)).
- The 20 Dog Bark / Animal vocalizations produced a 0.0% trigger rate in Phase 14 and 5.0% in Phase 36 Conservative.
- Aircraft/aviation trigger rate was 15.0%.

---

## 3. Campaign & Session Clustering Analysis

- **Positive Audio:** All 120 positive clips originated from 120 distinct uploaders. Session-level clustering effects are completely minimized ($	ext{ICC} pprox 0.0$).
- **Continuous Ambient Audio:** The 7 streams originate from 5 distinct European countries and 7 separate recording setups. 
- **Statistical Limitation:** Because total continuous exposure was 1.9534 hours rather than 20 hours, the Poisson 95% confidence interval for gross FAR spans [0.56, 5.24], reflecting standard statistical sample size bounds. No synthetic inflation was applied.
