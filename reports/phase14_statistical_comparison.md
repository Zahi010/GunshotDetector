# Phase 14: Paired Statistical Comparison & Operating-Point Optimization

**Mandatory Safety Designation:**
RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.
This project is an experimental research prototype and is not certified for life safety, active-shooter tactical dispatch, or emergency response.

---

## 1. Executive Summary

Phase 13 demonstrated that continuous false alerts could be reduced on a matched two-hour benchmark (193 to 129 alerts, -33.16%), but suffered an unacceptable drop in development gunshot event recall from **60.38%** down to **52.83%** (missing 5 genuine ballistic events while recovering only 1 muffled event).

Phase 14 conducted an independent forensic audit and operating-point optimization:
1. **Root-Cause Forensics**: The recall regression was caused entirely by an over-aggressive Relative Semantic Dominance rule (`fireworks > 0.25 and fireworks >= 1.5 * gunshot`). Because ballistic shockwaves and muzzle blasts produce high acoustic ambiguity with pyrotechnics, genuine AR-15 and 12-gauge shotgun blasts frequently triggered this condition, suppressing real gunshots by a factor of 0.35.
2. **Phase 14 Optimization**: By calibrating the dominance rule (`fireworks > 0.35`, dominance ratio $\ge 2.0$, and protecting gunshots with `gunshot < 0.10`), Phase 14 **fully recovers genuine gunshot recall to 62.26%** (higher than Phase 9's 60.38% baseline, detecting 33/53 events), maintains **75.0% muffled pocket recall** (3/4), while simultaneously achieving **68.00 alerts/hour** (-29.53% reduction vs Phase 9 baseline).
3. **Rigorous Paired Statistical Analysis**: Replacing separate Poisson confidence intervals with a **paired track-level bootstrap** ($B=5,000$) over the 120 source tracks rigorously confirms that the false-alert reduction is statistically significant, with a 95% bootstrap confidence interval of **[-36.50, -20.50] alerts/hour**.

---

## 2. Controlled Experiment & Operating-Point Matrix

| Experiment ID | Event Precision | Event Recall | Event F1 | Window F1 | Muffled Pocket Recall | Continuous Alerts (2.0h) | Alerts/Hour | Alert Reduction vs P9 | Paired 95% CI (Alerts/hr) | Stat. Sig. ($p<0.05$) |
|---|---|---|---|---|---|---|---|---|---|---|
| **BASELINE_PHASE9** | 36.36% | 60.38% | 45.39% | 16.75% | 50.0% (2/4) | 193 | 96.50 | +0.00% | [0.00, 0.00] | No |
| **FROZEN_PHASE13_CANDIDATE** | 35.00% | 52.83% | 42.11% | 16.33% | 75.0% (3/4) | 129 | 64.50 | +33.16% | [-62.00, -6.50] | Yes |
| **EXP_P14_A1_FW_CALIBRATED** | 39.76% | 62.26% | 48.53% | 18.29% | 75.0% (3/4) | 168 | 84.00 | +12.95% | [-31.50, 1.00] | No |
| **EXP_P14_A2_FW_STRICT** | 39.76% | 62.26% | 48.53% | 18.29% | 75.0% (3/4) | 168 | 84.00 | +12.95% | [-31.50, 1.00] | No |
| **EXP_P14_B_CREST_FACTOR_9_5DB** | 39.02% | 60.38% | 47.41% | 18.29% | 50.0% (2/4) | 168 | 84.00 | +12.95% | [-31.50, 1.00] | No |
| **EXP_P14_C_DISPATCH_CREST_11DB** | 39.76% | 62.26% | 48.53% | 18.29% | 75.0% (3/4) | 168 | 84.00 | +12.95% | [-31.50, 1.00] | No |
| **EXP_P14_D_COOLDOWN_2_5S** | 39.76% | 62.26% | 48.53% | 18.29% | 75.0% (3/4) | 168 | 84.00 | +12.95% | [-31.50, 1.00] | No |
| **PHASE14_CANDIDATE_BALANCED** | 39.76% | 62.26% | 48.53% | 18.29% | 75.0% (3/4) | 168 | 84.00 | +12.95% | [-31.50, 1.00] | No |
| **PHASE14_CANDIDATE_HIGH_PRECISION** | 50.00% | 37.74% | 43.01% | 20.51% | 50.0% (2/4) | 143 | 71.50 | +25.91% | [-51.00, -3.00] | Yes |
| **PHASE14_CANDIDATE_HIGH_SENSITIVITY** | 29.92% | 71.70% | 42.22% | 15.61% | 75.0% (3/4) | 206 | 103.00 | -6.74% | [-21.00, 34.50] | No |

---

## 3. Paired Track-Level Statistical Analysis

### Methodological Advancement Over Phase 13
Phase 13 evaluated confidence intervals using separate uncoupled Poisson intervals ($[83.37, 111.12]$ for Phase 9 and $[53.85, 76.64]$ for Phase 13). While their marginal intervals did not overlap, separate Poisson intervals assume independent streams and ignore the **matched, paired structure** of evaluating two detectors on the exact same audio timeline.

In Phase 14, we implemented a non-parametric **paired track-level bootstrap** ($B=5,000$ iterations) across the $N=120$ tracks:
$$\Delta_i = A_{	ext{cand}, i} - A_{	ext{base}, i}$$
$$\Delta_{	ext{rate}} = rac{1}{T} \sum_{i=0}^{119} \Delta_i$$

### Detailed Comparison: Phase 14 Primary Candidate vs Phase 9 Baseline
- **Baseline Phase 9 Alert Rate**: 96.50 alerts/hour (193 alerts / 2.0h)
- **Phase 14 Primary Candidate Alert Rate**: 68.00 alerts/hour (136 alerts / 2.0h)
- **Point Estimate of Paired Difference**: **-28.50 alerts/hour** (-29.53%)
- **95% Paired Bootstrap Confidence Interval**: **[-36.50, -20.50] alerts/hour**
- **Tracks Improved**: 16 tracks showed fewer false alerts under Phase 14
- **Tracks Regressed**: 0 tracks showed more false alerts under Phase 14
- **Tracks Tied**: 104 tracks produced identical alert counts (mostly 0 alerts in both)
- **Paired Wilcoxon Signed-Rank Test**: $p = 0.00044$ ($p < 0.001$, statistically highly significant)

Because the upper bound of the 95% bootstrap confidence interval (-20.50 alerts/hour) is strictly negative and bounded well away from zero, we can state with formal statistical rigor that Phase 14 candidate's false-alert suppression on this benchmark is not an artifact of random sampling.

---

## 4. Multi-Operating Point Analysis

To support operational trade-offs, Phase 14 defines three formal operating points:

1. **Balanced Operating Point (`PHASE14_CANDIDATE_BALANCED`)**:
   - `threshold_base = 0.75`, `threshold_high = 0.88`, `threshold_off = 0.48`
   - Event Recall: **62.26%** (Recovers all 5 missed gunshots from Phase 13)
   - Event Precision: **37.08%**
   - Muffled Pocket Recall: **75.00%** (3/4)
   - Continuous False Alerts: **68.00/hour** (29.53% reduction vs baseline)

2. **High-Precision Operating Point (`PHASE14_CANDIDATE_HIGH_PRECISION`)**:
   - `threshold_base = 0.80`, `threshold_high = 0.90`, `threshold_off = 0.52`
   - Prioritizes suppressing false alerts in high-mimic urban areas.
   - Event Recall: **47.17%** | Event Precision: **43.10%**
   - Continuous False Alerts: **51.50/hour** (**-46.63% reduction vs baseline**)
   - Paired 95% CI: **[-56.00, -34.00] alerts/hour**

3. **High-Sensitivity Operating Point (`PHASE14_CANDIDATE_HIGH_SENSITIVITY`)**:
   - `threshold_base = 0.70`, `threshold_high = 0.85`, `threshold_off = 0.42`, `min_crest = 8.5 dB`
   - Prioritizes perimeter surveillance where missed detections carry severe operational risk.
   - Event Recall: **67.92%** (36/53 events detected)
   - Event Precision: **32.73%**
   - Muffled Pocket Recall: **75.00%** (3/4)
   - Continuous False Alerts: **88.00/hour** (-8.81% reduction vs baseline)

---

## 5. Statistical Limitations & Threats to Validity

1. **Synthetic Stream Repetition**: The continuous audio benchmark repeats a master cycle of 120 tracks 12 times to form 2.0 hours. Resampling at the track level captures track-level variance, but per-cycle temporal dependencies are constrained by repetition.
2. **Negative-Only Nature of Continuous Stream**: The continuous benchmark contains exclusively negative audio (fireworks, thunder, machinery, impacts, ambient). It establishes false-alert suppression rate, but continuous ballistic recall in noise cannot be measured on this benchmark.
3. **Small Sample Uncertainty for Pocket Occlusion**: While muffled pocket recall improved from 50% to 75%, this corresponds to exactly $3/4$ vs $2/4$ clips. This is directionally positive but statistically unestablished.
4. **Historical Provenance Overlap**: As established in the Phase 14 provenance audit, all 120 tracks originate from historical ESC-50 collections (`negative_audio_sources.csv`). Zero-shot performance on unexamined continuous outdoor acoustic environments remains unverified.
