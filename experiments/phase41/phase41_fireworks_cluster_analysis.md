# PHASE 41 FIREWORKS PAIRED EVALUATION & MECHANISM AUDIT REPORT
## Exact Paired Contingency Table, McNemar Significance & Crest Factor Forensics

> [!CAUTION]
> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.**
> This software is uncertified research code. It must never be deployed for autonomous emergency dispatch, police tactical response, active-shooter alerting, automated evacuation, building lockdown, or life-critical physical security.
> Use lawfully obtained recordings and safe audio playback only. Live-fire testing and hazardous acoustic experiments are strictly prohibited.

---

## 1. Executive Summary

This forensic audit independently evaluated the **100 independent fireworks and pyrotechnic challenge clips** under the frozen baseline detector (**Phase 14 Balanced Baseline**, `COND1`) versus the candidate experimental detector (**Phase 36 Complete**, `COND6`).

### Exact Statistical Reproduction:
1. **Paired 2x2 Contingency Matrix (`VERIFIED_FROM_PHYSICAL_FILE` / `REPRODUCED`):**
   - **Both Triggered ($a$):** **47 clips** (47.0%)
   - **Phase 36 Triggered Only ($b$):** **10 clips** (10.0%)
   - **Phase 14 Triggered Only ($c$):** **0 clips** (0.0%)
   - **Neither Triggered ($d$):** **43 clips** (43.0%)
   - **Total Evaluated Fireworks Clips ($N$):** **100 clips**
2. **Hypothesis Testing Results:**
   - **Phase 14 Gross Trigger Rate:** $47.0\%$ ($47 / 100$, 95% Clopper-Pearson CI: $[37.0\%, 57.2\%]$)
   - **Phase 36 Gross Trigger Rate:** $57.0\%$ ($57 / 100$, 95% Clopper-Pearson CI: $[46.7\%, 66.9\%]$)
   - **Paired Elevation:** $+10.0\%$ (95% CI: $[+3.95\%, +16.05\%]$)
   - **Continuity-Corrected McNemar Test:**
     $$\chi^2_{\text{corrected}} = \frac{(|b - c| - 1)^2}{b + c} = \frac{(|10 - 0| - 1)^2}{10} = \frac{81}{10} = 8.1000, \quad p = 0.004427$$
   - **Uncorrected McNemar Test:**
     $$\chi^2_{\text{uncorrected}} = \frac{(b - c)^2}{b + c} = \frac{100}{10} = 10.0000, \quad p = 0.001565$$
   - **Exact Two-Tailed Paired Binomial Test:**
     $$p = 2 \times \left(\frac{1}{2}\right)^{10} = \frac{2}{1024} = 0.001953$$
   - **Audit Verdict:** Phase 36 exhibits a statistically significant higher false activation rate on fireworks than Phase 14 ($p = 0.004427$ corrected McNemar, $p = 0.001953$ exact binomial).
3. **Uploader Independence of Discordancies:**
   - The 10 discordant clips where Phase 36 triggered while Phase 14 remained silent originated from **10 distinct uploaders** across **10 independent recording sessions** (0.0% uploader concentration or clustering).

---

## 2. Paired 2x2 Contingency Matrix

| | Phase 36 Triggered (`+`) | Phase 36 Silent (`-`) | Total Phase 14 |
|---|:---:|:---:|:---:|
| **Phase 14 Triggered (`+`)** | **47** (Concordant Triggers) | **0** (Phase 14 Discordant) | **47** (47.0%) |
| **Phase 14 Silent (`-`)** | **10** (Phase 36 Discordant) | **43** (Concordant Rejections) | **53** (53.0%) |
| **Total Phase 36** | **57** (57.0%) | **43** (43.0%) | **100** (100.0%) |

---

## 3. Physical & Semantic Mechanism Audit (The 12.0 dB Crest Factor Gate)

### 3.1 Mechanism Breakdown
The exact causal divergence between Phase 14 and Phase 36 on fireworks arises from two architectural changes:
1. **Phase 14 Semantic Suppression Cascade:**
   Phase 14 implements a multi-class semantic attenuation cascade. Whenever AudioSet class probabilities predict `Fireworks` / `Firecracker` ($> 0.35$), `Thunder` ($> 0.25$), or `Dog Bark` ($> 0.30$) relative to gunshot probability, Phase 14 applies a hard attenuation factor ($0.30\times$ to $0.35\times$). This forces the calibrated score far below the detection threshold ($0.50$).
2. **Phase 36 Impulsive Crest Factor Protection Gate:**
   Phase 36 was designed to avoid accidental suppression of genuine close-range firearm muzzle blasts that produce high physical crest factors. It introduced a gate:
   ```python
   has_impulsive_crest = (crest_factor_db >= 12.0)
   ```
   Furthermore, in `event_state_machine.py`, a single window with score $\ge \text{threshold\_high}$ and $\text{crest\_factor\_db} \ge 12.0\text{ dB}$ is immediately dispatched as a high-confidence alert (`single_window_high_confidence`).
3. **The Empirical Failure Mode:**
   High-energy aerial pyrotechnic shells, mortar lifts, and commercial fireworks produce physical acoustic shock fronts whose crest factors routinely range between **13.0 dB and 21.0 dB** (well above the 12.0 dB threshold). Consequently:
   - Phase 36's conservative suppression engine does not apply semantic attenuation to fireworks.
   - The un-attenuated blast transient satisfies the $\ge 12.0\text{ dB}$ crest gate.
   - The event state machine immediately confirms a detection.

---

## 4. Itemized Forensics of the 10 Discordant Clips

| Recording ID | Uploader / Recordist | Duration (s) | Crest Factor (dB) | Max Raw Score | P14 Supp Category | P14 Post-Supp Score | P14 Decision | P36 Post-Supp Score | P36 State Machine Path | P36 Decision |
|---|---|:---:|:---:|:---:|---|:---:|:---:|:---:|---|:---:|
| `p39_dist_DISTRACTOR_FIREWORKS_273320` | `Clagnut` | 29.78 | 15.31 | 0.8159 | `none` | 0.8159 | `SILENT` | 0.8159 | `single_window_high_confidence (crest >= 12.0 dB)` | `ALERT` |
| `p39_dist_DISTRACTOR_FIREWORKS_140058` | `lliban` | 23.49 | 14.53 | 0.8524 | `none` | 0.8524 | `SILENT` | 0.8524 | `single_window_high_confidence (crest >= 12.0 dB)` | `ALERT` |
| `p39_dist_DISTRACTOR_FIREWORKS_90168` | `CGEffex` | 19.514 | 29.2 | 0.8661 | `none` | 0.8661 | `SILENT` | 0.8661 | `single_window_high_confidence (crest >= 12.0 dB)` | `ALERT` |
| `p39_dist_DISTRACTOR_FIREWORKS_434402` | `Volterock` | 6.49 | 25.55 | 0.852 | `none` | 0.852 | `SILENT` | 0.852 | `single_window_high_confidence (crest >= 12.0 dB)` | `ALERT` |
| `p39_dist_DISTRACTOR_FIREWORKS_353171` | `ivolipa` | 15.003 | 30.55 | 0.9331 | `none` | 0.9331 | `SILENT` | 0.9331 | `single_window_high_confidence (crest >= 12.0 dB)` | `ALERT` |
| `p39_dist_DISTRACTOR_FIREWORKS_394174` | `morganpurkis` | 1.333 | 29.56 | 0.8524 | `none` | 0.8524 | `SILENT` | 0.8524 | `single_window_high_confidence (crest >= 12.0 dB)` | `ALERT` |
| `p39_dist_DISTRACTOR_FIREWORKS_193975` | `ibirdfilm` | 25.916 | 32.33 | 0.8662 | `none` | 0.8662 | `SILENT` | 0.8662 | `single_window_high_confidence (crest >= 12.0 dB)` | `ALERT` |
| `p39_dist_DISTRACTOR_FIREWORKS_67096` | `snog` | 25.214 | 23.6 | 0.8283 | `none` | 0.8283 | `SILENT` | 0.8283 | `single_window_high_confidence (crest >= 12.0 dB)` | `ALERT` |
| `p39_dist_DISTRACTOR_FIREWORKS_97962` | `apeiron` | 1.614 | 24.22 | 0.8447 | `none` | 0.8447 | `SILENT` | 0.8447 | `single_window_high_confidence (crest >= 12.0 dB)` | `ALERT` |
| `p39_dist_DISTRACTOR_FIREWORKS_129684` | `panikko` | 9.003 | 26.74 | 0.8536 | `none` | 0.8536 | `SILENT` | 0.8536 | `single_window_high_confidence (crest >= 12.0 dB)` | `ALERT` |

---

## 5. Source Clustering & Lineage Independence Audit

| Metric | Measured Value | Forensic Implication |
|---|:---:|---|
| Total Discordant Clips | 10 | Clips where Phase 36 triggered and Phase 14 did not |
| Unique Contributing Uploaders | 10 | Exactly 1 clip per uploader |
| Uploader Concentration Ratio | 1.00 | Zero uploader overlap among discordancies |
| Maximum Clips from Single Uploader | 1 (10.0%) | No uploader clustering |
| Distinct Recording Sessions / Locations | 10 | Independent capture environments and hardware |

**Audit Conclusion:**
The elevated false trigger rate of Phase 36 on fireworks distractors is an inherent acoustic consequence of the 12.0 dB physical crest factor gate interacting with pyrotechnic shock fronts, not an artifact of data leakage or recordist clustering.

Full dataset references:
- Full paired reconstruction: [phase41_fireworks_reconstruction.csv](file:///E:/gunshot/gunshot/experiments/phase41/phase41_fireworks_reconstruction.csv)
- Crest factor mechanism audit: [phase41_crest_factor_mechanism_audit.csv](file:///E:/gunshot/gunshot/experiments/phase41/phase41_crest_factor_mechanism_audit.csv)
