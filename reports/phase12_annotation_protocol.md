# Phase 12 Annotation Quality Control & Adjudication Protocol

> **SAFETY DESIGNATION:** RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.  
> This acoustic benchmark is curated exclusively for statistical validation, generalization auditing, and failure-mode analysis. It is not rated, tested, or certified for life-safety alerting or mission-critical physical security applications.

---

## 1. Scope and Objective

This protocol governs the acquisition, labeling, temporal bounding, quality assurance, and adjudication for the Phase 12 Independent Acoustic Benchmark (`data/manifests/phase12_independent_eval_manifest.csv`).

The primary mission is to evaluate the frozen Phase 9 detector (`RealTimeStreamDetector` stateful pipeline) on genuinely unexamined, independently sourced recordings spanning diverse acoustic conditions without corrupting the locked test split.

---

## 2. Labeling Taxonomy and Decision Rules

Each audio recording in the Phase 12 benchmark is assigned one of three canonical ground truth labels:

### 2.1 Positive Ballistic Events (`ground_truth_label = 1`)
- **Definition:** Verified acoustic emission of a firearm discharge, including muzzle blast, supersonic projectile shockwave (ballistic crack), and immediate acoustic reflections.
- **Verification Criteria:**
  1. Verifiable provenance from controlled ballistic experimental ranges or authenticated urban acoustic sensor incident records.
  2. Audible muzzle blast or projectile shockwave confirmed via visual spectrographic analysis.
  3. Physical evidence of firing pin release, mechanical cycling, or calibrated sensor alert data.
  4. Precise event timestamps ($T_{\text{start}}, T_{\text{end}}$) bounding the energy onset and decay.
- **Rule on Pseudo-Labels:** Under no circumstances are YAMNet classifications, intermediate ML model probabilities, or automated threshold triggers accepted as ground truth evidence. Ground truth is strictly grounded in physical recording provenance.

### 2.2 Verified Negative Recordings (`ground_truth_label = 0`)
- **Definition:** Non-gunshot acoustic audio representing real-world ambient environments, urban transit, industrial machinery, weather phenomena, and impulsive non-firearm acoustic transients.
- **Verification Criteria:**
  1. Sourced from authentic non-gunshot acoustic repositories (e.g., ESC-50 unexamined classes, firearm range tool drops, ambient city street recordings).
  2. Free of any underlying gunfire, explosive detonation, or simulated firearm discharge.
  3. Event timestamps set to $-1.0, -1.0$.

### 2.3 Ambiguous / Uncertain Acoustic Events (`ground_truth_label = -1`)
- **Definition:** Acoustic events where physical origin cannot be definitively adjudicated as either a firearm discharge or a benign transient from a single acoustic sensor channel without external ground truth (e.g., video, physical ballistic evidence, or multi-sensor spatial triangulation).
- **Inclusion Mandate:** Five specific physical edge cases are retained in the benchmark with `ground_truth_label = -1`:
  1. Distant low-frequency atmospheric blast with slow rise time ($>40$ ms).
  2. Diffuse reverberant firecracker tail without clear initial supersonic shockwave.
  3. Heavy resonant metal drum impact with low-frequency mechanical ringing.
  4. Pneumatic nail gun discharge inside an enclosed reverberant room.
  5. Synthetic band-limited transient spike.
- **Evaluation Handling:** Ambiguous samples (`-1`) are evaluated separately in error audits. They are excluded from the primary binary F1 / Precision / Recall denominator so as not to bias the true-positive or false-positive metrics.

---

## 3. Acoustic Condition Stratification

To expose acoustic vulnerabilities (particularly the 9.5 dB crest-factor guard and short-event recovery path), recordings are stratified across five distinct physical conditions:

| Acoustic Condition | Target Physics | Sample Count | Source Provenance |
| :--- | :--- | :--- | :--- |
| **Digital-Clipped Ballistic** | High SPL muzzle blast exceeding ADC dynamic range; flat-topped waveform; reduced crest factor. | 10 | Mitchell Roberts Testing `ClippedRange` |
| **Pocket-Occluded Muffled** | Microphone enclosed in clothing; fabric acoustic low-pass filtering; attenuated high frequencies; muffled transient. | 20 | Mitchell Roberts Testing `gunshots/` |
| **Clean Direct Ballistic** | Unobstructed line-of-sight range recordings; sharp rise time ($<5$ ms); high SNR. | 15 | Mitchell Roberts Testing `gunshots/` |
| **Distant Urban Sensor** | Real building-mounted acoustic sensors; street reflections, multi-path echo, distance attenuation (250–340m), urban traffic noise. | 3 | ShotSpotter Chicago District 7 (Unexamined Sensors) |
| **Impulsive Range Mimics** | Heavy metal clanks, hammer drops, firearm mechanical cycling on outdoor ballistic range. | 20 | Mitchell Roberts Testing `non-gunshots/` |
| **Diverse Environmental Negatives** | Fireworks, thunder, sirens, car horns, train, engine, glass breaking, door wood knock, chainsaw, animal calls. | 80 | ESC-50 Untouched Folds / Novel Categories |
| **Ambiguous Edge Cases** | Physical borderline transients for uncertainty quantification (`label = -1`). | 5 | Phase 12 Edge-Case Benchmark Suite |
| **Continuous Exposure Stream** | 2.0 continuous hours (7,200s) of uninterrupted multi-environment negative audio. | 1 | Phase 12 Continuous Exposure Benchmark Suite |

---

## 4. Source Grouping and Cross-Split Leakage Prevention

To prevent data leakage across evaluation boundaries:
1. **Source Grouping:** All recordings originating from the same physical firing session or incident are grouped together (e.g., `Ar15RapidPocket`, `BerettaRapidPocket`, `ChicagoILDistrict7_312`).
2. **Deterministic Partitioning:**
   - 120 files ($77.9\%$) locked into `final_test`.
   - 34 files ($22.1\%$) reserved in `reserved_validation`.
3. **Cryptographic Integrity:** Every recording is fingerprinted with SHA-256. Zero hashes overlap with any Phase 1–11 training, validation, or diagnostic dataset.

---

## 5. Adjudication and Quality Assurance Checklist

Prior to locking the manifest, the dataset curator and validation engineer must execute and verify:
- [x] Every file referenced in the manifest physically exists on disk.
- [x] SHA-256 checksum of every file matches the manifest entry exactly.
- [x] Sample rate is confirmed at 16,000 Hz mono.
- [x] Event start/end timestamps are strictly within file duration.
- [x] No duplicate hashes exist within the manifest.
- [x] No manifest hash collides with Phase 1–4 training or validation partitions.
- [x] All 5 ambiguous recordings are explicitly labeled `ground_truth_label = -1`.
- [x] Continuous negative stream duration verified at $\ge 7,200.0$ seconds.
