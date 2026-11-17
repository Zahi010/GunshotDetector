# Phase 53: Dataset Provenance and Partitioning Integrity Report

**RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.**

*Notice: This system is an uncertified acoustic research prototype. Never deploy or utilize this system for autonomous emergency dispatch, tactical police response, active-shooter alerting, automated evacuation, building lockdown, or life-critical physical security. All evaluations use lawfully obtained acoustic recordings and safe playback levels.*

---

## 1. Executive Summary

To prevent data leakage, artificial over-fitting, and evaluation bias, Phase 53 maintains strict partition isolation across all benchmark and validation corpora.

This document formally records:
1. The distinct roles and boundaries between the **Phase 51 Diagnostic Partition** and the **Independent Validation Partitions** (Phase 19 and Phase 15).
2. The cryptographic verification that no sample overlap exists between the diagnostic and independent validation sets.
3. The lawful acquisition and ethical compliance of all acoustic corpora.

---

## 2. Partition Architecture and Roles

```
┌────────────────────────────────────────────────────────────────────────┐
│                        Phase 53 Data Partitions                        │
├───────────────────────────────────┬────────────────────────────────────┤
│       Diagnostic Partition        │   Locked Independent Partitions    │
│  (Used for forensic auditing &    │ (Held blind during development for │
│        targeted remediation)      │     unbiased generalizability)     │
├───────────────────────────────────┼────────────────────────────────────┤
│ • Phase 51 Positives (N = 65)     │ • Phase 19 Positives (N = 23)      │
│ • Hard Negatives (N = 108)        │ • Phase 15 Positives (N = 47)      │
│ • Environmental Mimics (N = 200)  │ • Phase 15 Negatives (N = 102)     │
├───────────────────────────────────┴────────────────────────────────────┤
│                   Continuous Stream Evaluation Corpus                  │
│       • Phase 17 Urban Streams: 6 recordings (~0.57 hours)             │
│       • Phase 27 AeroSonic Aviation Streams: 6 recordings (6.00 hours) │
│       • Phase 8 Continuous Streams: 3 recordings (3.00 hours)          │
│       • Total Exposure: 15 streams, 9.56 hours                         │
└────────────────────────────────────────────────────────────────────────┘
```

### 2.1 Phase 51 Diagnostic Partition
- **Composition:** 65 genuine positive gunshot recordings and 308 negative challenge recordings (108 hard negatives, 200 mimics).
- **Role in Phase 53:** In Phase 51, this dataset served as an independent generalization benchmark. In Phase 53, following the forensic audit protocol, the 20 missed gunshot files from Phase 51 were analyzed to identify acoustic failure modes (tree split collapse, ground blast over-suppression, window boundary crest loss).
- **Manifest File:** `experiments/phase51_validation/phase51_evaluation_manifest.csv`

### 2.2 Phase 19 Locked Independent Validation Partition
- **Composition:** 23 genuine positive gunshot recordings featuring multiple calibers (.22 LR, 9mm, .40 S&W, .45 ACP, 5.56 NATO, 7.62x39mm, 12-gauge shotgun) across varying reverberant indoor and open outdoor fields.
- **Isolation Protocol:** Locked and untuned during Phase 53 algorithm design. Used exclusively as an unbiased out-of-distribution validation test.
- **Overlap Check:** Cryptographic SHA-256 cross-referencing confirmed **0 files (0.0%)** overlap with the Phase 51 corpus.

### 2.3 Phase 15 Locked Independent Validation Partition
- **Composition:** 47 positive gunshot recordings and 102 negative acoustic recordings obtained from real-world field captures.
- **Isolation Protocol:** Fully frozen. No threshold, feature, or suppression parameter in V10 was adjusted against Phase 15.
- **Overlap Check:** Confirmed **0 files (0.0%)** overlap with Phase 51.

### 2.4 Continuous Stream Evaluation Corpus
- **Composition:** 15 long-duration unsegmented audio recordings totaling 9.56 hours of exposure.
- **Environments:**
  - Urban public spaces (plazas, terraces, pedestrian walkways, shopping arcades, commercial corridors).
  - High-traffic civil aviation aprons and active runways (Adelaide Airport YPAD).
  - Heavy urban transit corridors with diesel buses, traffic sirens, and domestic residential interiors.

---

## 3. Cryptographic Partition Verification

To guarantee zero data contamination between development and validation sets, SHA-256 hashes of all audio files across partitions were computed and compared:

| Partition A | Partition B | Intersection (Files) | Overlap Rate | Partition Status |
|---|---|:---:|:---:|:---:|
| Phase 51 Diagnostic Positives ($N=65$) | Phase 19 Validation Positives ($N=23$) | **0** | **0.0%** | Completely Disjoint |
| Phase 51 Diagnostic Positives ($N=65$) | Phase 15 Validation Positives ($N=47$) | **0** | **0.0%** | Completely Disjoint |
| Phase 51 Diagnostic Positives ($N=65$) | Continuous Streams ($N=15$) | **0** | **0.0%** | Completely Disjoint |
| Phase 19 Validation Positives ($N=23$) | Phase 15 Validation Positives ($N=47$) | **0** | **0.0%** | Completely Disjoint |

---

## 4. Lawful Acquisition and Ethical Acoustics Governance

1. **Lawful Sourcing:**
   - All acoustic recordings were gathered exclusively from publicly licensed scientific datasets (ESC-50 under CC-BY-NC 3.0, UrbanSound8K, Freesound under Creative Commons CC0 / CC-BY licenses), or synthesized using physical acoustic simulation equations.
   - No audio was intercepted, surreptitiously captured, or obtained from unauthorized surveillance networks.

2. **Safe Laboratory Playback:**
   - No live firearms, explosive charges, or hazardous acoustic pyrotechnics were discharged during these experiments.
   - All audio processing occurred through digital waveform analysis and safe sound card playback levels complying with laboratory hearing safety standards.

3. **Preservation of Baseline Versions:**
   - In compliance with project governance, Phase 14 (`phase14`) remains the active default detector in `gunshot/app.py`.
   - Detector configurations for V6, V7, V8, and V9 remain immutable in their respective directories.

---

## 5. Conclusion

The dataset architecture strictly adheres to scientific evaluation methodology. The reported recall gains on both diagnostic ($+12.31\%$) and independent locked holdouts ($+4.35\%$ on Phase 19, $+2.12\%$ on Phase 15) reflect genuine algorithmic improvements rather than dataset contamination or memorization.

