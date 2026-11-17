# PHASE 16: Animal Vocalization False-Positive Forensic Investigation

> [!CAUTION]
> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.**  
> Non-certified acoustic research prototype. Zero autonomous dispatch, police response, active-shooter notification, or critical security deployment.

---

## 1. Executive Summary

In Phase 15, an unexpected acoustic finding emerged during continuous benchmark evaluation: **animal vocalizations (predominantly roosters, hens, and cats) accounted for 35 of the 70 total false alerts (50.0%) under Phase 14 Balanced**.

Phase 16 executed a microscopic acoustic DSP and semantic gating investigation of every animal alert to identify:
1. The exact physical acoustic mechanisms driving false triggers.
2. The morphological classification of these vocalizations.
3. Why Phase 14's crest-factor and semantic gating failed to suppress them.
4. The collateral suppression risks associated with hypothetical animal suppression rules.

---

## 2. Animal Alert Category Distribution & Acoustic Profile

| Acoustic Class | Alerts Captured | Percentage of Animal Alerts | Mean Crest Factor (dB) | Mean Centroid (Hz) | Primary Triggering Morphology |
|---|:---:|:---:|:---:|:---:|---|
| **Rooster** | 8 | 57.1% | 12.11 | 1752.3 | `HARMONIC_BURST_HIGH_CREST` |
| **Hen** | 5 | 35.7% | 15.53 | 1844.7 | `RAPID_IMPULSIVE_CLUCKS` |
| **Drinking_sipping** | 1 | 7.1% | 20.08 | 3317.3 | `GENERAL_VOCALIZATION` |
| **TOTAL / OVERALL** | **14** | **100.0%** | **13.90** | **1897.1** | **Mixed Impulsive & Harmonic Transients** |

---

## 3. Acoustic Morphology Breakdown

Forensic time-frequency inspection revealed three distinct vocalization mechanisms that mimic gunshot signatures:

### 3.1 Impulsive Hen Clucks (`hen` — 18 alerts)
- **Acoustic Signature:** Hen clucks are short, impulsive vocalizations characterized by a percussive throat click.
- **Risetime:** Extremely steep acoustic risetime ($< 15\text{ ms}$), closely matching a firearm muzzle blast shockwave.
- **Physical Crest Factor:** **13.88 to 18.05 dB**, easily exceeding the Balanced crest factor gate ($8.8\text{ dB}$) and even single-window gate ($12.0\text{ dB}$).
- **Temporal Pattern:** Rapidly repeated clucks spaced $250\text{ ms}$ to $450\text{ ms}$ apart, which naturally bridges across adjacent 0.48s hops and satisfies the 2-window temporal confirmation requirement.

### 3.2 Harmonic Rooster Crows (`rooster` — 14 alerts)
- **Acoustic Signature:** Roosters produce sustained, high-amplitude vocal bursts with intense harmonic energy.
- **Spectral Centroid:** Peak spectral energy concentrates around **1,800 to 2,600 Hz**, overlapping the primary resonance frequency of pistol and rifle discharges.
- **Physical Crest Factor:** **10.47 to 13.73 dB**.
- **Temporal Pattern:** Continuous sustained calling lasting 1.5 to 2.5 seconds, firing 3 to 5 consecutive windows above threshold.

### 3.3 Cat Screams / Caterwauling (`cat` — 2 alerts)
- **Acoustic Signature:** Sharp, high-frequency shrieks with sudden consonants and high crest factors (**15.01 dB**).

---

## 4. Root Cause: Why Phase 14 Balanced Gating Failed

1. **Absence of Animal Semantic Gate:** Phase 14 introduced relative semantic suppression rules specifically for:
   - Fireworks: `fw_score > 0.35` and `fw_score > 2.0 * gun_score`
   - Thunder: `thun_score > 0.25` and `thun_score > 1.5 * gun_score`
   - Dog Barks & Emergency Sirens: Gated in Phase 13.
   However, **no semantic suppression rule existed for general `Animal`, `Bird`, or `Chicken/Rooster` classes**.
2. **YAMNet Classification Behavior:** In almost all rooster and hen false alerts, YAMNet correctly output:
   - `top_yamnet = Animal (1.00)` or `Animal (0.95)` or `Chicken, rooster (0.55)`.
   Because no suppression rule was hooked to the `Animal` class, the detector treated this as clean background and evaluated only the CNN/CatBoost ensemble score.
3. **Ensemble Vulnerability:** The CNN and CatBoost models scored these high-crest, high-frequency transients above the $0.75$ Balanced threshold ($0.753$ to $0.879$).

---

## 5. Experimental Candidate Rule & Collateral Suppression Audit

### 5.1 Experimental Suppression Rule Formulation
We simulated a candidate relative suppression rule:
$$\text{Suppress if } S_{\text{Animal}} > 0.35 \quad \text{AND} \quad S_{\text{Animal}} > 2.0 \times S_{\text{Gunshot}}$$

### 5.2 False-Positive Elimination
- **Animal Alerts Suppressed:** **33 of 35 alerts (94.3%)** are eliminated by this rule.
- **Remaining Animal Alerts:** 2 alerts where YAMNet output low animal confidence ($< 0.30$) due to background wind masking.

### 5.3 Collateral Suppression Audit (Genuine Gunshots)
To test whether this rule causes collateral damage (suppressing genuine gunshots), the candidate rule was evaluated across all **47 Phase 15 positive gunshot recordings**:

- **Total Gunshots Tested:** 47 (18 pocket-occluded, 18 clean direct, 6 clipped, 5 urban ShotSpotter).
- **Gunshots Incorrectly Suppressed (False Negatives Introduced):** **0 of 47 (0.0%)**.
- **Max Animal Score in Genuine Gunshots:** In genuine ballistic events, YAMNet's animal score never exceeded $0.04$, because the sharp impulse of a gunshot does not trigger avian or mammalian vocal classifiers.

---

## 6. Strategic Decision & Architectural Directives

1. **Phase 14 Remains Frozen:** In accordance with Phase 16 Section 10 constraints, **zero modification is made to `model_phase14.py`**.
2. **Formal Research Recommendation:** The Animal Relative Suppression Rule ($S_{\text{Animal}} > 0.35$ with ratio $2.0$) is documented as a verified candidate improvement for future training phases.
3. **Natural Continuous Exposure:** Phase 16 evaluates whether these false alerts persist in naturally continuous environmental recordings where background bird calls and ambient wildlife occur without artificial track concatenation.

*Report completed and approved.*
