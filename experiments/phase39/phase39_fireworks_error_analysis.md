# PHASE 39 FIREWORKS & PYROTECHNIC ERROR ANALYSIS REPORT
## Forensic Failure Analysis of 100 Pyrotechnic Clips & Paired McNemar Hypothesis Test

> [!CAUTION]
> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.**
> This software is uncertified research code. It must never be deployed for autonomous emergency dispatch, police tactical response, active-shooter alerting, automated evacuation, building lockdown, or life-critical physical security.
> Use lawfully obtained recordings and safe audio playback only. Live-fire testing and hazardous acoustic experiments are strictly prohibited.

---

## 1. Executive Summary

Phase 38 observed that fireworks produced elevated trigger rates (Phase 14: 8/20 = 40.0%; Phase 36: 11/20 = 55.0%), but noted that $N=20$ was too small to establish statistical significance.

In Phase 39, the fireworks challenge set was expanded to **100 genuinely distinct pyrotechnic clips** from the FSD50K Dev set (aerial shells, firecrackers, bottle rockets, ground fountains, Roman candles, multi-shot mortars).

### Key Empirical Findings:
1. **Trigger Rates on N = 100 Fireworks Clips:**
   - **Phase 14 Balanced Baseline (COND1):** **47 / 100 (47.0%)**
   - **Phase 36 Complete Branch (COND6):** **57 / 100 (57.0%)**
   - **Phase 17 Defective Profile (COND2):** **71 / 100 (71.0%)**
2. **Paired 2x2 Contingency Table (Phase 14 vs Phase 36):**
   - Both Triggered: **47 clips**
   - Triggered by Phase 36 Only: **10 clips**
   - Triggered by Phase 14 Only: **0 clips**
   - Neither Triggered: **43 clips**
3. **Statistical Hypothesis Test (Paired McNemar Test):**
   - $\chi^2 = 8.1000$ (degrees of freedom = 1)
   - $p\text{-value} = 0.0044$
   - **Statistical Interpretation:** The difference is statistically significant (p < 0.05).

---

## 2. Acoustic Root-Cause Analysis: Why Pyrotechnics Mimic Gunshots

Detailed spectral and waveform decomposition of false triggers reveals why both Phase 14 and Phase 36 struggle with pyrotechnics:

1. **Shockwave-Like Blast Transients:**
   Aerial firecracker detonations and exploding mortar shells produce supersonic blast waves with rapid acoustic rise times ($< 0.5\text{ ms}$) and sharp compression phases that closely mimic muzzle blasts.
2. **High Physical Crest Factor:**
   In 57 pyrotechnic clips that triggered Phase 36, the calculated physical crest factor exceeded $14.5\text{ dB}$, bypassing the physical impulse filter (threshold: $8.8\text{ dB}$).
3. **YAMNet Semantic Ambiguity:**
   YAMNet's semantic head frequently assigns non-zero probabilities to `Gunshot_and_gunfire` (classes 427–430) during firecracker bursts, while the fireworks class score ($s_{\text{fireworks}}$) often remains below the semantic suppression activation threshold ($0.35$ or $0.50$).
4. **State Machine Event Confirmation:**
   Phase 36 requires two consecutive confirmation windows. In multi-shot Roman candles or firecracker strings, rapid successive explosions occur across adjacent $0.48\text{ s}$ analysis hops, satisfying the two-window confirmation requirement and firing a confirmed alert.

---

## 3. Governance Implications

1. **Known Physical Limitation:** Fireworks constitute a fundamental physical confounder for passive acoustic gunshot detection prototypes. No acoustic classifier can reliably separate all pyrotechnic shockwaves from gunfire without auxiliary modalities (e.g. optical flash detection, infrared thermal imaging, or multi-sensor spatial triangulation).
2. **Rejection of Premature Promotion:** Phase 36's failure to reject fireworks confirms that it is an **experimental research prototype**, not ready for baseline promotion or life-critical deployment.
