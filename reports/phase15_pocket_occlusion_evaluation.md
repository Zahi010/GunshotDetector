# Phase 15 Pocket-Occlusion Robustness Evaluation

**Safety Designation: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.**

## 1. Context & Motivation

Phase 14 identified a severe evaluation limitation: only four pocket-occluded recordings were available in historical test splits (`Pocket01`–`Pocket04`), precluding any statistically meaningful robustness claims.

In Phase 15, we acquired and audited **18 genuinely unexamined pocket-occluded gunshot recordings** from Mitchell et al. testing dataset (`Ar15SinglePocket`, `Ar15RapidPocket`, `BerettaSinglePocket`, `BerettaRapidPocket`), spanning both long guns (AR-15 .223 rifle) and handguns (Beretta 92FS 9mm).

---

## 2. Quantitative Performance Across Detectors (N = 18 Independent Samples)

| Detector Profile | Pocket Samples Evaluated | Detected (TP) | Missed (FN) | Pocket Recall (%) | 95% Wilson Confidence Interval |
|---|---|---|---|---|---|
| **Phase 9 Baseline** | 18 | 10 | 8 | **55.56%** | [33.7%, 75.4%] |
| **Phase 13 Candidate** | 18 | 9 | 9 | **50.00%** | [29.0%, 71.0%] |
| **Phase 14 Balanced** | 18 | 10 | 8 | **55.56%** | [33.7%, 75.4%] |
| **Phase 14 High-Precision** | 18 | 6 | 12 | **33.33%** | [16.3%, 56.2%] |
| **Phase 14 High-Sensitivity** | 18 | 13 | 5 | **72.22%** | [49.1%, 87.5%] |

---

## 3. Acoustic Forensics & Occlusion Physics

Pocket occlusion imposes physical acoustic filtering:
1. **Low-Pass Attenuation:** Heavy fabrics (denim, wool, canvas) absorb high-frequency sound energy above 3 kHz by 12–25 dB.
2. **Crest Factor Muffling:** The sharp acoustic N-wave shockwave is blunted, lowering peak-to-RMS crest factor from direct-line-of-sight levels (18–24 dB) down to 10–14 dB.
3. **Phase 14 Calibrated Recovery:**
   - In Phase 13, the rigid crest factor threshold (14.0 dB) suppressed muffled pocket shots as ambient noise.
   - In Phase 14, the calibrated crest gating (8.8 dB min for short clips, 12.0 dB single-window dispatch) recovers genuine pocket impulses while maintaining semantic gating.

---

## 4. Explicit Limitations & Boundaries

1. **Not Field-Certified:** Even with 18 independent test samples, this remains a laboratory evaluation. Real-world pocket occlusion involves body shadowing, varying fabric layers, movement friction, and orientation shifts.
2. **Uncertainty Bounds:** The 95% Wilson confidence interval spans [33.7%, 75.4%]. Claiming absolute pocket robustness is unscientific and unsafe.
