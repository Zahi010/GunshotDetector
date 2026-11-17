# PHASE 39 SUPPRESSION BEHAVIOUR & REPRODUCIBILITY REPORT
## Forensic Analysis of COND5 (Legacy Animal Suppression) vs COND6 (Conservative Suppression)

> [!CAUTION]
> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.**
> This software is uncertified research code. It must never be deployed for autonomous emergency dispatch, police tactical response, active-shooter alerting, automated evacuation, building lockdown, or life-critical physical security.
> Use lawfully obtained recordings and safe audio playback only. Live-fire testing and hazardous acoustic experiments are strictly prohibited.

---

## 1. Executive Summary

Phase 38 reported identical event-level metrics between `COND5` (Phase 36 with Legacy Animal Suppression) and `COND6` (Phase 36 with Conservative Suppression):
- Continuous Background FAR: 1.5359 / hr (3 alerts, 88.50 s excluded)
- Positive Clip Recall: 64.2% (77 / 120 clips detected, 14.4% duplicate rate)
- Distractor Trigger Rate: 19.2% (23 / 120 clips triggered)

This forensic investigation proves that **COND5 and COND6 possess distinctly different internal mechanics and produce different numerical scores on thousands of windows**. Their identical final event metrics occur because **all active suppression occurs strictly below the event-initiation threshold ($s < 0.75$)**.

---

## 2. Quantitative Window-Level Comparison

An exhaustive trace across all 17,995 sliding analysis windows in the Phase 38 evaluation corpus reveals:

| Suppression Metric | COND4 (No Suppression) | COND5 (Legacy Animal Suppression) | COND6 (Conservative Suppression) | Numerical Delta (COND5 vs COND6) |
|---|:---:|:---:|:---:|:---:|
| **Suppression Engine Mode** | `NONE` | `LEGACY_ANIMAL` | `CONSERVATIVE` | Architectural Difference |
| **Active Suppressed Windows** | 0 / 17,995 (0.0%) | **7,571 / 17,995 (42.07%)** | **6,264 / 17,995 (34.81%)** | **+1,307 windows suppressed in COND5** |
| **Attenuation Multiplier** | 1.00 (None) | $0.30\\times$ ($70\\%$ attenuation) | $0.50\\times$ ($50\\%$ attenuation) | Stronger attenuation in COND5 |
| **Animal Threshold Required** | N/A | $s_{\\text{animal}} > 0.35$ | $s_{\\text{animal}} \\ge 0.50$ | Stricter threshold in COND6 |
| **Animal / Raw Score Ratio** | N/A | $\\ge 2.0\\times$ | $\\ge 2.5\\times$ | Stricter ratio in COND6 |
| **Aviation Override Active** | N/A | False (Aviation ignored) | True (Aviation protected) | COND6 prevents aviation dips |
| **Suppressed Windows with $s_{\\text{raw}} \\ge 0.75$** | 0 | **0 (0.0%)** | **0 (0.0%)** | **Zero threshold crossings** |
| **Suppressed Windows with $s_{\\text{raw}} \\ge 0.48$** | 0 | **8 (0.04%)** | **0 (0.0%)** | 8 windows attenuated below 0.48 |
| **Final Emitted Alert Events** | 104 events | 103 events | 103 events | **Identical Event Decisions** |

---

## 3. Detailed Trace of Borderline Windows ($s_{\\text{raw}} \\ge 0.48$)

Exactly 8 windows across the 247 recordings had a raw score in the range $[0.48, 0.50)$ while qualifying for COND5 suppression:

1. `p38_cont_04_courcelles` (win 177): $s_{\\text{raw}} = 0.4975 \\rightarrow s_{\\text{cond5}} = 0.1492$, $s_{\\text{cond6}} = 0.4975$
2. `p38_cont_04_courcelles` (win 190): $s_{\\text{raw}} = 0.4920 \\rightarrow s_{\\text{cond5}} = 0.1476$, $s_{\\text{cond6}} = 0.4920$
3. `fsd50k_dist_DISTRACTOR_ANIMAL_BARK_341178` (win 0): $s_{\\text{raw}} = 0.4861 \\rightarrow s_{\\text{cond5}} = 0.1458$, $s_{\\text{cond6}} = 0.4861$
4. `fsd50k_dist_DISTRACTOR_ANIMAL_BARK_341178` (win 3): $s_{\\text{raw}} = 0.4846 \\rightarrow s_{\\text{cond5}} = 0.1454$, $s_{\\text{cond6}} = 0.4846$
5. `fsd50k_dist_DISTRACTOR_ANIMAL_BARK_341178` (win 7): $s_{\\text{raw}} = 0.4903 \\rightarrow s_{\\text{cond5}} = 0.1471$, $s_{\\text{cond6}} = 0.4903$
6. `fsd50k_dist_DISTRACTOR_ANIMAL_BARK_341178` (win 12): $s_{\\text{raw}} = 0.4940 \\rightarrow s_{\\text{cond5}} = 0.1482$, $s_{\\text{cond6}} = 0.4940$
7. `fsd50k_dist_DISTRACTOR_ANIMAL_BARK_34872` (win 6): $s_{\\text{raw}} = 0.4943 \\rightarrow s_{\\text{cond5}} = 0.1483$, $s_{\\text{cond6}} = 0.4943$
8. `fsd50k_dist_DISTRACTOR_ANIMAL_BARK_33849` (win 9): $s_{\\text{raw}} = 0.4951 \\rightarrow s_{\\text{cond5}} = 0.1485$, $s_{\\text{cond6}} = 0.4951$

### State-Machine Decision Mechanics:
- In the Phase 36 Finite State Machine (`EventStateMachine`), a transition from `IDLE` to `CANDIDATE` or `CONFIRMED` requires $s \\ge \\text{threshold\\_base} = 0.75$.
- A score of $0.49$ is below $0.75$. Therefore, in an idle state machine, a window with score $0.49$ produces **no transition**.
- Scores between $0.48$ and $0.75$ can only sustain an *already confirmed* event or prevent an active event from terminating. None of these 8 windows occurred during an active gunshot event.
- Consequently, whether the score remained $0.49$ (COND6) or dropped to $0.15$ (COND5), the state machine remained in `IDLE`.

---

## 4. Why COND5 and COND6 Outperformed COND4

In continuous stream `p38_cont_01_goussainville` at window 3,314:
- In COND4 (No Suppression), a transient dog bark combined with background acoustic hiss generated an ensemble spike that sustained an event.
- In both COND5 and COND6, animal suppression activated on the preceding window, preventing candidate cluster accumulation.
- Both COND5 and COND6 successfully prevented this single false alert, reducing continuous false alerts from 4 (COND4) to 3 (COND5/6).
- COND6 achieved this with much more conservative thresholds ($0.50$ vs $0.35$, $2.5\\times$ vs $2.0\\times$, and aviation masking protection), avoiding unnecessary score dips on 1,307 innocent windows.

---

## 5. Conclusion & Governance

1. **Suppression is Fully Functional:** The suppression modules are active and divergent. The identical metrics reflect the high specificity of the base ensemble ($s < 0.75$ on animal audio), not dead code.
2. **Conservative Mode Validated:** COND6 provides equal false-alert suppression while preserving acoustic stability and aviation protection.
3. **No Retuning Authorized:** All parameters remain strictly frozen in accordance with governance directives.

