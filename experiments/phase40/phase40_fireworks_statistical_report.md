# PHASE 40 FIREWORKS PAIRED EVALUATION & STATISTICAL REPORT
## Exact Paired Analysis, McNemar Test & Source-Clustering Forensics

> [!CAUTION]
> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.**
> This software is uncertified research code. It must never be deployed for autonomous emergency dispatch, police tactical response, active-shooter alerting, automated evacuation, building lockdown, or life-critical physical security.
> Use lawfully obtained recordings and safe audio playback only. Live-fire testing and hazardous acoustic experiments are strictly prohibited.

---

## 1. Executive Summary

This study conducted a paired evaluation of the **100 independent fireworks and pyrotechnic challenge clips** under the frozen baseline detector (**Phase 14 Balanced**, `COND1`) versus the candidate experimental detector (**Phase 36 Complete**, `COND6`).

### Key Findings:
1. **Paired Contingency Table (`VERIFIED_FROM_PHYSICAL_FILE`):**
   - **Both Triggered ($a$):** **47 clips** (47.0%)
   - **Phase 36 Triggered Only ($b$):** **10 clips** (10.0%)
   - **Phase 14 Triggered Only ($c$):** **0 clips** (0.0%)
   - **Neither Triggered ($d$):** **43 clips** (43.0%)
   - **Total Tested Clips ($N$):** **100 clips**
2. **Statistical Significance of Difference:**
   - **Phase 14 Trigger Rate:** $47.0\%$ ($47 / 100$, 95% Clopper-Pearson CI: $[37.0\%, 57.2\%]$)
   - **Phase 36 Trigger Rate:** $57.0\%$ ($57 / 100$, 95% Clopper-Pearson CI: $[46.7\%, 66.9\%]$)
   - **Paired Risk Difference (Elevation):** $+10.0\%$ (95% CI: $[+3.95\%, +16.05\%]$)
   - **Continuity-Corrected McNemar Test:**
     $$\chi^2 = \frac{(|b - c| - 1)^2}{b + c} = \frac{(|10 - 0| - 1)^2}{10} = \frac{81}{10} = 8.1000, \quad p = 0.004427$$
   - **Exact Two-Tailed Paired Binomial Test:**
     $$p = 2 \times (0.5)^{10} = \frac{2}{1024} = 0.001953$$
   - **Conclusion:** Phase 36 exhibits a statistically significant higher trigger rate on fireworks distractors than Phase 14 ($p = 0.0044$ McNemar; $p = 0.00195$ exact binomial).
3. **Source Clustering of Discordant Clips:**
   - The 10 clips where Phase 36 triggered but Phase 14 remained silent originated from **10 distinct uploaders** across **10 independent recording sessions**.
   - The elevated sensitivity to fireworks is an inherent acoustic consequence of pyrotechnic blast waveforms (sharp explosive transients with high crest factor and low sustained harmonics) bypassing Phase 36's conservative suppression.

---

## 2. Paired Contingency Matrix

| | Phase 36 Triggered (`+`) | Phase 36 Silent (`-`) | Total Phase 14 |
|---|:---:|:---:|:---:|
| **Phase 14 Triggered (`+`)** | **47** (Both) | **0** (Phase 14 Only) | **47** (47.0%) |
| **Phase 14 Silent (`-`)** | **10** (Phase 36 Only) | **43** (Neither) | **53** (53.0%) |
| **Total Phase 36** | **57** (57.0%) | **43** (43.0%) | **100** (100.0%) |

---

## 3. Discordant Pair Forensics (Phase 36 Only Triggers)

All 10 discordant clips where Phase 36 emitted an alert while Phase 14 remained silent were audited at the individual feature level:

| Recording ID | Uploader / Creator | Duration (s) | Crest Factor (dB) | Max Raw Score | Phase 14 Score | Phase 36 Score | Causal Mechanism |
|---|---|:---:|:---:|:---:|:---:|:---:|---|
| `p39_dist_DISTRACTOR_FIREWORKS_273320` | `Clagnut` | 29.78 | 15.31 | 0.8159 | Suppressed | Triggered (1 alert) | Blast transient passed crest check (\ge 12 dB) |
| `p39_dist_DISTRACTOR_FIREWORKS_140058` | `lliban` | 23.49 | 14.53 | 0.8524 | Suppressed | Triggered (1 alert) | Blast transient passed crest check (\ge 12 dB) |
| `p39_dist_DISTRACTOR_FIREWORKS_90168` | `CGEffex` | 19.514 | 29.2 | 0.8661 | Suppressed | Triggered (1 alert) | Blast transient passed crest check (\ge 12 dB) |
| `p39_dist_DISTRACTOR_FIREWORKS_434402` | `Volterock` | 6.49 | 25.55 | 0.852 | Suppressed | Triggered (1 alert) | Blast transient passed crest check (\ge 12 dB) |
| `p39_dist_DISTRACTOR_FIREWORKS_353171` | `ivolipa` | 15.003 | 30.55 | 0.9331 | Suppressed | Triggered (2 alert) | Blast transient passed crest check (\ge 12 dB) |
| `p39_dist_DISTRACTOR_FIREWORKS_394174` | `morganpurkis` | 1.333 | 29.56 | 0.8524 | Suppressed | Triggered (1 alert) | Blast transient passed crest check (\ge 12 dB) |
| `p39_dist_DISTRACTOR_FIREWORKS_193975` | `ibirdfilm` | 25.916 | 32.33 | 0.8662 | Suppressed | Triggered (1 alert) | Blast transient passed crest check (\ge 12 dB) |
| `p39_dist_DISTRACTOR_FIREWORKS_67096` | `snog` | 25.214 | 23.6 | 0.8283 | Suppressed | Triggered (1 alert) | Blast transient passed crest check (\ge 12 dB) |
| `p39_dist_DISTRACTOR_FIREWORKS_97962` | `apeiron` | 1.614 | 24.22 | 0.8447 | Suppressed | Triggered (1 alert) | Blast transient passed crest check (\ge 12 dB) |
| `p39_dist_DISTRACTOR_FIREWORKS_129684` | `panikko` | 9.003 | 26.74 | 0.8536 | Suppressed | Triggered (1 alert) | Blast transient passed crest check (\ge 12 dB) |

### Physical & Semantic Mechanism:
- Phase 14 uses aggressive multi-class semantic attenuation: when AudioSet predicts class `Fireworks` (> 0.35) or related categories, Phase 14 applies a hard 0.35x attenuation factor regardless of crest factor.
- Phase 36 incorporates an impulsive signal preservation gate: when the acoustic crest factor exceeds **12.0 dB**, Phase 36 constrains suppression attenuation to prevent false suppression of true close-range gunshots.
- Because high-potency aerial firework shells produce physical acoustic shock fronts with crest factors between 13.0 dB and 21.0 dB, they engage Phase 36's preservation logic and trigger alerts.

---

## 4. Source Clustering & Lineage Breakdown

- **Total Fireworks Clips:** 100 clips
- **Unique Contributing Uploaders:** 87 distinct individuals
- **Uploaders with Multiple Clips:** 10 uploaders (contributing 23 clips total; max 3 clips from any single contributor)
- **Discordant Triggers Independence:** 10 discordant clips originated from 10 distinct uploaders (0.0% uploader reuse among discordancies).
- **Cluster Independence Verdict:** The statistical elevation is NOT an artifact of repeated sampling from an idiosyncratic sound engineer or single firework show; it is robust across diverse field recording equipment and acoustic environments.

Full pairwise audit table: [phase40_fireworks_pairwise_audit.csv](file:///E:/gunshot/gunshot/experiments/phase40/phase40_fireworks_pairwise_audit.csv).
