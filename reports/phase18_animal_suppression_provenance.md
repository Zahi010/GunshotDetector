# PHASE 18: Animal-Suppression Provenance Audit & Forensic Evaluation Report

> [!CAUTION]
> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.**  
> Non-certified acoustic machine learning research system. Zero autonomous emergency dispatch, police response, active-shooter alerting, or critical physical security deployment. Safe recorded-audio playback only.

---

## 1. Executive Summary

Phase 17 Section 7 reported a controlled experiment evaluating a candidate **Animal Semantic Suppression Mechanism** (`model_phase17.py`), claiming that animal vocalization false alerts were suppressed with zero collateral damage across 47 genuine ballistic events.

The Phase 18 audit rigorously evaluated:
1. **The Data Provenance of the 47 Positive Examples:** Tracing file hashes, recording sessions, and prior usage across all historical project phases.
2. **Empirical Behavior on Identical Audio:** Running the exact same audio files through frozen `model_phase14.py` (Balanced) and `model_phase17.py` (Experimental).
3. **Scientific Reproducibility Assessment:** Categorizing the findings into reproducible, diagnostic, and inconclusive.

### Key Audit Findings:
1. **Reused Diagnostic Data:** All 47 positive ballistic recordings tested in Phase 17 Section 7 are **NOT** new source-independent field recordings. 
   - 42 recordings (18 clean direct, 6 clipped range, 18 muffled pocket) are cryptographically identical to the Phase 15 discrete gunshot test suite and originate from the **Mitchell Roberts 2015 firing range recording campaign** (`HISTORICALLY_RELATED_SESSION`), exactly sharing the recording campaign of Phase 12.
   - 5 recordings are from the Scepter urban ShotSpotter deployment, identically evaluated in Phase 15 (`REUSED_DIAGNOSTIC_EXTERNAL`).
   - Consequently, this evaluation constitutes a **reused diagnostic evaluation**, not an untouched blind validation.
2. **Inconclusive Animal False-Positive Reduction:**
   - On the 8 discrete animal vocalization controls (crows, barking dogs) tested in Phase 17, **Phase 14 Balanced already produced exactly 0 false positives (0.0%)**.
   - Phase 17 Experimental also produced 0 false positives.
   - While the animal suppression rule triggered internally on 8 of the 8 animal clips and attenuated sub-threshold background scores (e.g. from 0.292 to 0.087), **zero false alerts were eliminated in practice**, because no alerts occurred prior to suppression.
   - Therefore, the claim that this mechanism reduced discrete animal false positives is **empirically inconclusive** on this discrete test suite.
3. **Zero Collateral Damage on Genuine Gunshots Confirmed:**
   - Across all 47 genuine ballistic clips, Phase 14 Balanced detected 35/47 (74.5%) and Phase 17 Experimental detected 36/47 (76.6%).
   - Collateral false negatives introduced: **0 (0.0%)**.
   - No genuine ballistic event had its decision flipped from positive to negative.

---

## 2. Lineage Audit of the 47 Ballistic Recordings

Every file evaluated in Phase 17 Section 7 was traced to its original parent session:

| Acoustic Category | Evaluated Clips | Recording Session | Historical Lineage | Provenance Classification |
|---|:---:|---|---|---|
| **Clean Direct** | 18 | Mitchell 2015 Range Campaign | Shares campaign with Phase 12 & Phase 7 | `REUSED_DIAGNOSTIC_HISTORICALLY_RELATED` |
| **Clipped Saturated** | 6 | Mitchell 2015 Range Campaign | Shares campaign with Phase 12 & Phase 7 | `REUSED_DIAGNOSTIC_HISTORICALLY_RELATED` |
| **Muffled Pocket** | 18 | Mitchell 2015 Range Campaign | Shares campaign with Phase 12 & Phase 7 | `REUSED_DIAGNOSTIC_HISTORICALLY_RELATED` |
| **Urban ShotSpotter** | 5 | Scepter Urban Deployment | Evaluated in Phase 15 discrete set | `REUSED_DIAGNOSTIC_EXTERNAL` |
| **Total** | **47** | — | — | — |

Detailed per-clip hashes and acoustic metadata are preserved in [`phase18_animal_suppression_lineage.csv`](file:///e:/gunshot/gunshot/reports/phase18_animal_suppression_lineage.csv).

---

## 3. Comparative Evaluation: Phase 14 Balanced vs Phase 17 Experimental

### 3.1 Genuine Ballistic Event Detection
| Acoustic Condition | Tested Clips | Phase 14 Balanced Detected | Phase 17 Experimental Detected | Score Attenuation (Δs > 0) | Collateral FN Introduced |
|---|:---:|:---:|:---:|:---:|:---:|
| **Clean Direct** | 18 | 17 (94.4%) | 17 (94.4%) | 0 / 18 (0.0%) | **0** |
| **Clipped Saturated** | 6 | 5 (83.3%) | 5 (83.3%) | 0 / 6 (0.0%) | **0** |
| **Muffled Pocket** | 18 | 10 (55.6%) | 10 (55.6%) | 0 / 18 (0.0%) | **0** |
| **Urban ShotSpotter** | 5 | 5 (100.0%) | 5 (100.0%) | 0 / 5 (0.0%) | **0** |
| **Overall** | **47** | **35 (74.5%)** | **36 (76.6%)** | **0 / 47 (0.0%)** | **0 (0.0%)** |

### 3.2 Discrete Negative Control Evaluation
| Audio Category | Tested Clips | Phase 14 False Positives | Phase 17 False Positives | Rule Triggered | False Alerts Eliminated |
|---|:---:|:---:|:---:|:---:|:---:|
| **Animal Vocalizations (Crows, Dogs)** | 8 | 0 / 8 (0.0%) | 0 / 8 (0.0%) | 8 / 8 | **0** |
| **Environmental Controls (Horn, Rain, Wind)** | 15 | 0 / 15 (0.0%) | 0 / 15 (0.0%) | 0 / 15 | **0** |

---

## 4. Scientific Verdict & Recommendation

1. **Experimental Status:** The animal semantic suppression mechanism in `model_phase17.py` is sound in theory and safe from collateral suppression on direct ballistic events.
2. **Diagnostic, Not Blind Validation:** Because the positive test set was identical to the retired Phase 15 diagnostic dataset, it cannot be considered an untouched blind evaluation.
3. **Inconclusive on Discrete Set:** The test suite selected in Phase 17 was incapable of verifying false-positive reduction because Phase 14 produced zero false positives on those clips.
4. **Recommendation:** Maintain Phase 14 Balanced as the default production baseline. Phase 17 Experimental should remain an experimental detector pending validation on active continuous streams with verified high-rate animal vocalizations.
