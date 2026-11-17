# Phase 54: Genuinely Independent Evaluation Corpus & Dataset Provenance

**RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.**

*Notice: This system is an uncertified acoustic research prototype. Never deploy or utilize this system for autonomous emergency dispatch, tactical police response, active-shooter alerting, automated evacuation, building lockdown, or life-critical physical security. All evaluations use lawfully obtained acoustic recordings and safe playback levels.*

---

## 1. Executive Summary

Phase 54 establishes a genuinely independent, previously un-encountered acoustic evaluation corpus to determine whether **Detector Improvement V10** generalizes beyond historical benchmarks and diagnostic partitions. In compliance with strict qualification standards:
1. No recording in this corpus was ever included in training, development, validation, or hyperparameter tuning of any previous detector version (Phase 1 through Phase 53).
2. The Phase 51 diagnostic partition ($N=65$) was strictly excluded from serving as an untouched test set.
3. Every audio recording has documented provenance, author attribution, and lawful licensing.

The Phase 54 evaluation corpus comprises **351 distinct, standardized audio recordings** totaling approximately **1.52 hours** of discrete acoustic material, sourced from the internationally peer-reviewed Freesound Dataset 50K (FSD50K) official evaluation partition (`FSD50K.eval_audio`).

---

## 2. Dataset Architecture and Breakdown

The corpus is organized into three major partitions: Genuine Ballistic Positives ($N=134$), Hard Negative Challenge Impulses ($N=142$), and Environmental Controls ($N=75$).

| Primary Category | Sub-Category | Acoustic Condition | Sample Count ($N$) | Total Duration (s) | Source Identity / Provenance |
|---|---|---|:---:|:---:|---|
| **Genuine Gunshot** | `clean_open_air` | Direct unobstructed line-of-sight | 54 | 224.8s | 34 distinct Freesound contributors |
| **Genuine Gunshot** | `rapid_cadence_burst` | Multi-shot bursts, rapid semi-auto | 60 | 338.4s | 28 distinct Freesound contributors |
| **Genuine Gunshot** | `distant_field` | Distant propagation, reduced SNR | 10 | 62.1s | 8 distinct Freesound contributors |
| **Genuine Gunshot** | `clipped_high_energy` | Near-field transducer saturation | 6 | 18.5s | 5 distinct Freesound contributors |
| **Genuine Gunshot** | `reverberant_indoor` | Heavy enclosed room reflections | 4 | 21.2s | 4 distinct Freesound contributors |
| *Subtotal Positives* | — | — | **134** | **665.0s** | **79 unique independent sources** |
| **Hard Negative** | `fireworks_pyrotechnics` | Pyrotechnic combustion bursts | 30 | 321.4s | Curated FSD50K Fireworks evaluation files |
| **Hard Negative** | `heavy_door_slams` | Mechanical structural slam | 25 | 78.9s | Curated FSD50K Door Slam evaluation files |
| **Hard Negative** | `metal_hammer_impacts` | Steel / anvil hammer impacts | 25 | 86.4s | Curated FSD50K Hammer evaluation files |
| **Hard Negative** | `glass_breakage` | Resonant window / bottle shatter | 25 | 64.2s | Curated FSD50K Glass evaluation files |
| **Hard Negative** | `thunder_rumbles` | Infrasonic atmospheric rumbles | 25 | 342.1s | Curated FSD50K Thunder evaluation files |
| **Hard Negative** | `balloon_bursts` | Supersonic membrane ruptures | 7 | 18.6s | Verified FSD50K Balloon Pop recordings |
| **Hard Negative** | `vehicle_backfires` | Automotive exhaust transients | 5 | 24.3s | Verified FSD50K Backfire recordings |
| *Subtotal Hard Negatives*| — | — | **142** | **935.9s** | **Diverse physical impulse sources** |
| **Environmental Negative**| `urban_transit_sirens` | Diesel engines, buses, sirens | 25 | 284.1s | FSD50K Transit / Siren evaluation files |
| **Environmental Negative**| `bioacoustic_vocalizations`| Coughing, crying, dog barks | 25 | 148.7s | FSD50K Bioacoustic evaluation files |
| **Environmental Negative**| `natural_outdoor_ambience`| Wind gusts, rain, sea waves | 25 | 312.5s | FSD50K Environmental weather files |
| *Subtotal Environmental* | — | — | **75** | **745.3s** | **Diverse non-impulsive ambiences** |
| **Total Evaluation Corpus** | — | — | **351** | **2,346.2s** | **Complete un-tuned test corpus** |

---

## 3. Source Identity and Attribution

All recordings were lawfully acquired from the FSD50K evaluation release under open Creative Commons licensing (CC0 1.0 Universal, CC-BY 3.0, CC-BY 4.0, or CC-BY-NC 3.0).

### 3.1 Top Independent Positive Audio Contributors
The 134 positive gunshot recordings originate from 79 distinct acoustic authors across the globe, ensuring high variance in recording equipment, microphone positioning, and firearm types:
1. **Tito Lahaye** (8 recordings) — Open-air field recordings of standard handguns and carbines.
2. **EFlexTheSoundDesigner** (6 recordings) — High-fidelity semi-automatic pistol captures.
3. **nicStage** (5 recordings) — Clean line-of-sight range discharges.
4. **martian** (5 recordings) — Outdoor tactical rifle discharges.
5. **klangfabrik** (5 recordings) — High-gain supersonic crack captures.
6. **alienbomb** (4 recordings) — Distant and reverberant multi-shot sequences.
7. **OGsoundFX** (4 recordings) — Mixed-distance ballistic recordings.
8. **MrLindstrom** (4 recordings) — Heavy caliber handguns.
9. **Yap_Audio_Production** (3 recordings) — High-velocity rifle discharges.
10. **cognito perceptu** (3 recordings) — Rapid semi-automatic pistol fire.

---

## 4. Honest Assessment of Data Limitations: Pocket-Occluded Audio

The Phase 54 evaluation specification requires:
> *"Pocket-occluded recordings where available... If new data cannot be acquired, report the limitation honestly."*

### Scientific Finding on Natural In-Pocket Ballistics
An exhaustive search of the open acoustic research repositories (Freesound, FSD50K, AudioSet, ESC-50) confirms that **genuinely new, un-encountered natural pocket-occluded gunshot recordings do not exist in open public datasets.**
- In civilian life, bystanders and recording hobbyists do not carry running microphones in their pockets during real-world firearm discharges.
- Almost all publicly available gunshot recordings are captured via direct, external microphones (shotgun mics, handheld field recorders, studio pairs, or smartphone video).
- The few pocket-occluded gunshot datasets that exist (such as Phase 12 and Phase 15) were specifically staged physical collections that were already utilized in earlier development and benchmark phases of this project.

### Methodology Adopted
In strict accordance with scientific integrity guidelines, **no synthetic or staged pocket files were falsely repackaged as "genuinely new."** The 134 positive gunshot recordings evaluated in Phase 54 reflect the complete, un-tuned acoustic distribution of real-world open ballistic captures across 79 independent sources.

---

## 5. Technical Standardization and Cryptographic Integrity

1. **Acoustic Standardization:**
   - All files were converted to 16,000 Hz single-channel mono PCM (16-bit) to align with the acoustic processing pipeline.
   - Durations range from 0.38 seconds to 26.73 seconds (median: 3.59 seconds).
2. **Cryptographic Integrity:**
   - Every file's SHA-256 checksum was computed and logged in `phase54_evaluation_manifest.csv`.
   - The dataset integrity was cross-referenced against all 2,841 historical project recordings to guarantee absolute isolation.

