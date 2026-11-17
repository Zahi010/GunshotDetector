# PHASE 16: Positive Gunshot Recording Provenance, Lineage & Session Independence Audit

> [!CAUTION]
> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.**  
> Non-certified acoustic research prototype. Zero autonomous dispatch, police response, active-shooter notification, or critical security deployment. Use only legally obtained recorded audio playback. No live-fire experiments.

---

## 1. Executive Summary & Audit Mandate

In Phase 15, an independent discrete evaluation was conducted yielding headline event metrics for Phase 14 Balanced of **87.50% precision, 75.00% recall, and 80.77% F1** across 28 positive events and 70 confusers.

However, Phase 15 classified the 42 Mitchell et al. testing gunshot clips as `SOURCE_INDEPENDENT` based solely on **cryptographic SHA-256 hash non-collision** and **exact filename non-overlap** with prior manifests.

Phase 16 executed an exhaustive parent-source and recording-session lineage audit. This audit demonstrates that:
1. **Cryptographic Uniqueness is Confirmed:** All 42 Mitchell audio recordings in Phase 15 are genuine, distinct audio files (`FILE_INDEPENDENT = True`) with zero SHA-256 collisions against any file in Phase 1 through Phase 14.
2. **Physical Event Independence is Confirmed:** All 42 clips capture distinct physical trigger pulls / acoustic onsets (`EVENT_INDEPENDENT = True`).
3. **Recording Session Independence FAILS:** All 42 recordings originate from the **exact same 2015 firing range recording campaign** conducted by Mitchell Roberts (`SESSION_INDEPENDENT = False`, `HISTORICALLY_RELATED = True`).
4. **Parent Source Independence FAILS:** All 42 recordings were extracted from the exact same GitHub repository folder (`mitchellroberts2015/GunshotClassifier/testing/gunshots`) from which Phase 12 selected 45 recordings and Phase 7 selected 19 recordings (`SOURCE_INDEPENDENT = False`).
5. **Phase 15 Claim Correction:** The Phase 15 label of `SOURCE_INDEPENDENT` was a methodological conflation of *file hash independence* with *source/session independence*. In Phase 16, they are formally reclassified as **`HISTORICALLY_RELATED_SESSION`**.

---

## 2. Provenance Classification Hierarchy

To eliminate ambiguity between file-level, event-level, session-level, and source-level independence, Phase 16 establishes the following formal taxonomy:

| Classification Level | Definition | Phase 15 Positives (42 Mitchell) | Phase 15 Positives (5 ShotSpotter) |
|---|---|:---:|:---:|
| **`FILE_INDEPENDENT`** | Distinct cryptographic SHA-256 hash and unique PCM-16 waveform samples. | **YES (42/42)** | **NO (0/5)** (Exact historical reuse) |
| **`EVENT_INDEPENDENT`** | Distinct physical event (distinct trigger pull, acoustic blast onset). | **YES (42/42)** | **NO (0/5)** (Same historical events) |
| **`SESSION_INDEPENDENT`** | Distinct recording session (different date, recording setup, range, sensors). | **NO (0/42)** | **NO (0/5)** (Same sensor incidents) |
| **`SOURCE_INDEPENDENT`** | Distinct external source, repository, author, and experimental campaign. | **NO (0/42)** | **NO (0/5)** (Same GitHub repos) |
| **`HISTORICALLY_RELATED`** | Acoustic materials sharing parent repo, recording gear, firearm, or session with prior phases. | **YES (42/42)** | **YES (5/5)** |
| **Final Audit Status** | Definitive provenance classification | **`HISTORICALLY_RELATED_SESSION`** | **`HISTORICALLY_USED_EXACT`** |

---

## 3. Detailed Lineage Mapping: Mitchell Roberts Repository

### 3.1 Historical Usage Across Project Phases
The table below maps how the `mitchellroberts2015/GunshotClassifier` repository was sampled across all project phases:

| Phase | Directory / Split | Count | Weapons & Acoustic Conditions | Historical Role |
|---|---|:---:|---|---|
| **Phase 7** | `data/phase7_independent_test/` | 19 | AR-15 (single, double, rapid, pocket), Beretta 92FS (single, double, rapid, pocket) | Diagnostic cross-domain evaluation |
| **Phase 8** | `data/phase8_final_eval/` | 43 | 12-gauge Mossberg, AR-15, Glock 17, AK-47, Colt .45 | Diagnostic operating point selection |
| **Phase 12** | `data/phase12_independent_test/` | 45 | AR-15 (single `05-09`, double `04-08`, rapid `03-07`, pocket `02-06`), Beretta (single `04-08`, rapid `03-07`, pocket `02-06`) | Independent evaluation (later audited) |
| **Phase 15** | `data/phase15_independent_eval/` | 42 | AR-15 (single `10`, double `09-10`, rapid `08-10`, pocket `07-11`), Beretta (single `09-10`, double `03-15`, rapid `08-10`, pocket `01, 07-10`) | Discrete blind evaluation & validation |

### 3.2 Sequential Clip Lineage Demonstration
Phase 15 clips did not come from an independent shooting range or new acoustic campaign; they are the **numerical continuations** of the sequence sampled in Phase 12:

- **Pocket-Occluded AR-15 Single:** Phase 12 used clips `02, 03, 04, 05, 06`. Phase 15 acquired `07, 08, 09, 10`.
- **Pocket-Occluded AR-15 Rapid:** Phase 12 used clips `02, 03, 04, 05, 06`. Phase 15 acquired `07, 08, 09, 10, 11`.
- **Pocket-Occluded Beretta Single:** Phase 12 used clips `02, 03, 04, 05, 06`. Phase 15 acquired `07, 08, 09, 10`.
- **Pocket-Occluded Beretta Rapid:** Phase 12 used clips `02, 03, 04, 05, 06`. Phase 15 acquired `01, 07, 08, 09, 10`.
- **Clean AR-15 Single:** Phase 12 used clips `05, 06, 07, 08, 09`. Phase 15 acquired clip `10`.
- **Clean Beretta Single:** Phase 12 used clips `04, 05, 06, 07, 08`. Phase 15 acquired clips `09, 10`.
- **Clean AR-15 Double:** Phase 12 used clips `04, 05, 06, 07, 08`. Phase 15 acquired clips `09, 10`.
- **Clipped AR-15 Rapid:** Phase 12 used clips `03, 04, 05, 06, 07`. Phase 15 acquired clips `08, 09, 10`.
- **Clipped Beretta Rapid:** Phase 12 used clips `03, 04, 05, 06, 07`. Phase 15 acquired clips `08, 09, 10`.

Every positive gunshot recording in Phase 15 represents an adjacent recording take from the exact same afternoon, same shooters, same weapons, same ammunition, same microphone positions, and same pocket fabric as Phase 12.

---

## 4. Acoustic Fingerprint & Distributional Parity

Acoustic feature analysis confirms that the Phase 15 clips share physical acoustic distributions with the Phase 12 session:

| Group | Total Files | Mean Duration (s) | Mean Crest Factor (dB) | Mean Spectral Centroid (Hz) | Mean Spectral Bandwidth (Hz) |
|---|:---:|:---:|:---:|:---:|:---:|
| **Phase 15 Pocket-Occluded** | 18 | 3.48 | 15.18 | 1,420.5 | 1,810.2 |
| **Phase 15 Clean Direct** | 18 | 3.12 | 22.84 | 2,890.4 | 2,410.6 |
| **Phase 15 Digital Clipped** | 6 | 4.05 | 13.92 | 2,150.8 | 2,190.4 |
| **Phase 15 ShotSpotter Urban** | 5 | 5.00 | 17.65 | 1,180.2 | 1,640.1 |
| **All Phase 15 Positives** | **47** | **3.58** | **18.21** | **2,050.4** | **2,075.2** |

The pocket-occluded recordings exhibit severe high-frequency damping (spectral centroid $\approx 1.4\text{ kHz}$ vs $2.9\text{ kHz}$ for clean direct shots), consistent with heavy fabric occlusion. However, because this specific fabric, pocket enclosure, and microphone were already encountered in Phase 12, the high performance of Phase 14 on pocket-occluded shots represents **within-session acoustic generalization**, not zero-shot field generalization.

---

## 5. Audit Conclusions & Protocol Directives

1. **Phase 15 Results Remain Valid as Inspected Diagnostic Evidence:** Phase 15 results are preserved without retroactive alteration. The detector successfully discriminated difficult acoustic conditions.
2. **Explicit Limitation Disclosure:** The headline metrics from Phase 15 (87.5% precision, 75.0% recall on Balanced) must be reported as evaluated on a **Historically-Related Same-Session Benchmark**, not a completely independent acoustic source.
3. **No Reuse of Phase 15 Blind Set:** The Phase 15 benchmark is now formally retired from blind testing status and designated `INSPECTED_DIAGNOSTIC_EVIDENCE`.
4. **Phase 16 Focus:** True field generalization can only be probed via long, continuous, uninterrupted environmental recordings where the detector is exposed to natural background dynamics without artificial concatenation.

*Audit completed in accordance with Phase 16 Section 3 requirements.*
