# PHASE 38 DATASET ACQUISITION & PROVENANCE REPORT
## Prospective Evaluation Corpus: Lineage, Licensing & Overlap Audit

> [!CAUTION]
> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.**
> This experimental acoustic gunshot detection software is uncertified research software. It must never be deployed for autonomous emergency dispatch, police tactical response, active-shooter alerting, automated evacuation, building lockdown, or life-critical physical security.
> Use legally obtained recordings and safe audio playback only. Live-fire testing and hazardous acoustic experiments are strictly prohibited.

---

## 1. Executive Summary

Phase 38 acquired a **100.0% newly sourced, out-of-sample evaluation corpus** comprising **247 audio recordings** with **zero historical overlap** across three distinct evaluation partitions:
1. **Prospective Continuous Ambient Negative Streams:** 7 authentic continuous field recording streams totalling **1.9534 hours** ($7,032.35\text{ seconds}$) across 7 independent recording campaigns in 5 European nations (France, Belgium, Germany, Lithuania, UK).
2. **Prospective Positive Gunfire Audio:** 120 human-annotated gunshot recordings across **120 unique uploaders/recording sessions** from the peer-reviewed Freesound Dataset 50K (FSD50K) under Creative Commons licenses (CC0 / CC BY 3.0 / CC BY 4.0 / CC BY-NC 3.0).
3. **Prospective Reviewed Non-Target Distractors:** 120 certified non-gunshot acoustic clips across **120 unique uploaders** covering 6 challenging distractor classes (Fireworks, Thunder/Explosion, Animal Barking, Aircraft/Aviation, Door Slams, and Power Tools/Impacts).

---

## 2. Historical Overlap Audit (`VERIFIED FROM PHYSICAL FILE`)

A cryptographic SHA-256 exclusion audit was conducted by comparing every candidate recording in Phase 38 against all **2,252 historical audio files** and manifests spanning Phases 1 through 37:

| Evaluation Partition | Total Candidate Files | Exact SHA-256 Historical Matches | Near-Duplicate / Filename Overlap | Genuinely New Files | Independence Audit Status |
|---|:---:|:---:|:---:|:---:|:---:|
| **Continuous Ambient Negative** | 7 | **0 (0.0%)** | 0 (0.0%) | **7 (100.0%)** | `VERIFIED_GENUINELY_NEW` |
| **Controlled Positive Gunfire** | 120 | **0 (0.0%)** | 0 (0.0%) | **120 (100.0%)** | `VERIFIED_GENUINELY_NEW` |
| **Reviewed Distractor Clips** | 120 | **0 (0.0%)** | 0 (0.0%) | **120 (100.0%)** | `VERIFIED_GENUINELY_NEW` |
| **Total Evaluation Corpus** | **247** | **0 (0.0%)** | **0 (0.0%)** | **247 (100.0%)** | `VERIFIED_GENUINELY_NEW` |

Full audit details are documented in [phase38_historical_overlap_audit.csv](file:///E:/gunshot/gunshot/experiments/phase38/dataset/phase38_historical_overlap_audit.csv).

---

## 3. Continuous Ambient Exposure Summary & Limitations

The research protocol targeted up to 20 hours of continuous ambient audio across multiple campaigns.

### Actual Acquired Exposure:
- **Total Streams:** 7 continuous ambient audio files
- **Total Duration:** 7,032.35 seconds = **1.9534 hours** (14,642 sliding windows of 0.96s)
- **Geographic Representation:**
  - `France (Val-d'Oise)`: Abandoned urban zone, Goussainville (1.0000 hr continuous)
  - `Belgium (Hainaut)`: Industrial spoil pile, Binche (0.5667 hr continuous)
  - `France (Nord)`: Suburban residential, Hautmont (0.1667 hr continuous)
  - `Belgium (Hainaut)`: Factory perimeter, Courcelles (0.1000 hr continuous)
  - `Germany (Niedersachsen)`: Active passenger railway station, Hameln (0.0393 hr continuous)
  - `Lithuania (Curonian Spit)`: Forest nature preserve, Neringos (0.0501 hr continuous)
  - `UK (Devon)`: Rural windy soundscape, Dartington Hall (0.0307 hr continuous)
- **Research Transparency & Anti-Fabrication Boundary:**
  In strict adherence to governance instructions:
  > *"Twenty hours is a research target, not a guarantee of adequate false-alert characterization. If the target cannot be achieved lawfully, report the actual exposure and limitations. Never manufacture or synthetically inflate continuous exposure."*
  
  The exposure was **not** synthetically inflated, loop-padded, or manufactured from concatenated short clips. All 7 streams are continuous, unedited field recordings. The achieved exposure of 1.9534 hours provides an initial prospective snapshot, but statistical confidence bounds (exact Poisson 95% CIs) are wider than a 20-hour exposure would yield, which is honestly documented in the statistical evaluation.

---

## 4. Positive Evaluation Set Provenance

- **Source:** FSD50K (Freesound Dataset 50K, Fonseca et al., IEEE/ACM TASLP 2021).
- **Class:** `Gunshot_and_gunfire` (id 92, mid `/m/032s66`).
- **Composition:** 120 distinct clips selected from 120 independent uploaders/sessions to eliminate recording session correlation.
- **Event Types:** Single rounds (handguns, shotguns, rifles), burst fire (submachine guns, automatic rifles), indoor/outdoor reverberant acoustics.
- **Total Annotated Gunfire Rounds:** 148 physical rounds (106 single-round events + 14 burst-fire incidents containing 42 individual rounds).

---

## 5. Reviewed Distractor Set Provenance

- **Composition:** 120 certified non-target clips across 120 unique uploaders from FSD50K, strictly excluding any clip with `Gunshot_and_gunfire` labels.
- **Class Breakdown (20 clips each):**
  1. `Fireworks`: Aerial shells, firecrackers, sparklers, rockets
  2. `Thunder / Explosion`: Distant thunder claps, blasting, detonating transients
  3. `Animal / Bark`: Dog barking, guard dogs, canine vocalizations
  4. `Aircraft / Aviation`: Low-altitude propeller airplanes, helicopters, jet passes
  5. `Impulsive Urban Door / Slam`: Heavy metal door slams, car doors, cabinet closures
  6. `Construction / Tools Impact`: Hammer strikes, pneumatic drills, metal crushing, power tools

---

## 6. License & Access Register Summary

All acquired assets are governed by legally recognized open-access licenses recorded in [phase38_dataset_license_register.csv](file:///E:/gunshot/gunshot/experiments/phase38/dataset/phase38_dataset_license_register.csv):

| License Regime | Recording Count | Commercial Use | Redistribution | Attribution Requirements |
|---|:---:|:---:|:---:|---|
| **Public Domain Mark 1.0 / CC0** | 104 | Unrestricted | Unrestricted | No attribution required (public domain) |
| **Creative Commons Attribution (CC BY 3.0 / 4.0)** | 128 | Permitted | Permitted | Attribution to uploader/creator required |
| **Creative Commons Non-Commercial (CC BY-NC 3.0 / 4.0)** | 14 | Non-Commercial Research Only | Permitted for Research | Attribution required; non-commercial only |
| **Creative Commons No-Derivatives (CC BY-NC-ND 3.0)** | 1 | Non-Commercial Research Only | Unmodified redistribution only | Attribution required |

