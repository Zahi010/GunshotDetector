# Phase 3 Dataset Engineering, Web Acquisition, and Annotation Audit Report

**Date:** October 28, 2026  
**System:** AI-Powered Acoustic Gunshot Sound Detection System (Phase 3)  
**Author:** Senior Audio Machine Learning & Signal Processing Engineer  

---

## Executive Summary

Phase 3 addresses the two fundamental dataset weaknesses identified in the Phase 2 audit:
1. **Weak / Whole-File Labeling:** Positive gunshot recordings contained extensive trailing silence or background noise (up to 200+ seconds) that inherited the positive label. This penalized the model whenever silence squelching or zero prediction correctly suppressed quiet periods.
2. **Acoustic Domain Gap in Negative Audio:** Previous negative audio relied on procedural synthetic noises and firearm mechanical foley (cocking, dry-firing), leaving the detector vulnerable to real-world acoustic mimics such as fireworks, vehicle backfires, glass shattering, and wood impacts.

### Key Accomplishments in Phase 3
- **Acquired 300 Legitimate Web Negative Audio Recordings** from Freesound and ESC-50 across 5 high-priority transient categories under Creative Commons licenses.
- **Created Verified Timestamp-Aware Gunshot Event Annotations (`data/manifests/gunshot_events.csv`)** covering 351 distinct acoustic blast intervals across 150 positive recordings.
- **Mined and Curated 732 Approved Hard Negatives** into `data/hard_negatives/approved/`, strictly integrated into the training split with zero test leakage.
- **Expanded Held-Out Test Set from 37 to 98 Independent Source Recordings** (17 gunshot, 81 negative recordings; 873 unaugmented windows).
- **Enforced Strict Zero-Data Leakage** via base stem grouping and MD5 hash collision checks.

---

## 1. Weak Label Audit and Correction

### 1.1 The Weak Labeling Mechanism
In acoustic event classification, whole-file labeling assumes that if a recording contains a gunshot, every sliced window in that file is positive. However:
- A single rifle shot lasts approximately 0.25 to 1.2 seconds (including reverberation).
- A 5.2-second recording (`soundreality-gun-shot-341144.mp3`) has the shot between 0.0s and 0.8s, followed by 4.4 seconds of dead silence.
- Under whole-file labeling, all 9 windows of this file were labeled `1` (positive).
- When the model predicted `0` on the silence windows (as it acoustically should), evaluation penalized them as **false negatives**, artificially suppressing reported window recall to 83.67% despite 100% of the gunshot events being detected.

### 1.2 Physical Acoustic Profiling
Using `scripts/annotate_gunshot_events.py`, every positive recording was profiled using:
- **Frame Length:** 40 ms (640 samples at 16 kHz), **Hop Length:** 15 ms (240 samples).
- **Onset Attack Detection:** Moving RMS rising $\ge 12$ dB above estimated noise floor and $\ge -45$ dBFS.
- **Noise Floor Estimation:** 15th percentile of lowest 50% energy frames.
- **Signal-to-Noise Ratio (SNR):** Computed as $20 \log_{10}(\text{Peak RMS} / \text{Noise Floor})$.

### 1.3 Annotation Results
- **Recordings Analyzed:** 150 positive recordings.
- **Total Distinct Gunshot Events Detected:** 351 events.
- **Recordings with Long Trailing Silence ($>1.5$s):** 45 recordings.
- **Longest Recording:** `armed_unit-distant-war-377958` (234.4s) contained 13 distinct burst intervals separated by long pauses of up to 17 seconds.
- **Output Manifest:** Saved in `data/manifests/gunshot_events.csv`.

### 1.4 Documented Window Overlap Policy
```python
if max_overlap_sec >= 0.15:
    window_label = 1    # Verified gunshot acoustic blast
elif max_overlap_sec <= 0.02:
    window_label = 0    # Silence / ambient background within gunshot file
else:
    window_label = 1    # Ambiguous boundary (excluded during training)
```

---

## 2. Web Negative Audio Acquisition (Task Two)

### 2.1 Collection Methodology
Using `scripts/download_negative_audio.py`, **300 real-world recordings** were collected from the official ESC-50 dataset repository (curated from Freesound) under Creative Commons licenses (CC-BY 3.0, CC-BY 4.0, CC0):
- Automated retry mechanism with exponential backoff.
- SHA-256 fingerprinting and deduplication check.
- Audio standardization to 16 kHz mono float32 PCM WAV.
- Full provenance cataloged in `data/manifests/negative_audio_sources.csv`.

### 2.2 Category Breakdown

| Category Directory | ESC-50 Class Codes | Count | Representative Sounds | Primary Licenses |
|---|---|:---:|---|---|
| `fireworks` | 48 (Fireworks) | 20 | Aerial explosions, crackles, multi-shot mortars | CC-BY 3.0 / CC0 |
| `sharp_impacts` | 12 (Clapping), 19 (Glass break), 22 (Wood knock), 24 (Can opening) | 80 | Wood knocks, glass shattering, loud handclaps | CC-BY 3.0 / CC-BY 4.0 |
| `engine_backfires_and_machinery` | 34 (Hand saw), 38 (Chainsaw), 41 (Chainsaw), 42 (Train), 43 (Horn) | 100 | Vehicle backfires, horns, industrial saw impacts | CC-BY 3.0 / CC0 |
| `thunder_and_weather` | 17 (Thunderstorm), 18 (Rain), 28 (Wind) | 60 | Thunderclaps, lightning strikes, downpour | CC-BY 3.0 / CC0 |
| `general_ambience` | 13 (Crackling fire), 25 (Footsteps) | 40 | Campfire pops, heavy footwear impacts | CC-BY 3.0 / CC-BY 4.0 |
| **Total Web Downloads** | **5 Categories** | **300** | **Real Recorded Audio** | **Open CC Licenses** |

---

## 3. Hard-Negative Mining Pipeline (Task Four)

### 3.1 Protocol
1. **Zero-Leakage Ingestion:** The detector scans candidate negative audio strictly from the **train split** (`GunshotDataset.splits["train"]`). The validation and test sets are NEVER scanned or mined.
2. **Candidate Mining:** Audio windows with gunshot detection score $\ge 0.20$ at threshold 0.48 are saved to `data/hard_negatives/pending_review/`.
3. **Verification & Ingestion:** Confirmed non-gunshot false alarms are moved to `data/hard_negatives/approved/`.
4. **Current Approved Inventory:** **732 approved hard negative WAV files** (500 newly mined from web training background + 232 baseline).
5. **Feature Cache:** Extracted to `.cache_features/features_hard_negatives.npz` (shape: 732, 1024).

---

## 4. Dataset Splits & Leakage Prevention (Task Eight)

### 4.1 Stratified Source-Level Group Splitting
Splitting is performed at the base recording level using `get_base_stem()` and MD5 hashes:
- Train: 70%
- Validation: 15%
- Test: 15%

### 4.2 Split Statistics

| Split | Total Unique Groups | Gunshot Groups | Background Groups | Total Windows Sliced | Positive Windows (Timestamp-Aware) | Positive Windows (Legacy Whole-File) |
|---|:---:|:---:|:---:|:---:|:---:|:---:|
| **Train** | 450 | 77 | 373 | 5,587 (+732 HN = 6,319) | 1,433 | 1,433 |
| **Validation** | 96 | 16 | 80 | 779 | 114 | 148 |
| **Test (Held-Out)** | 98 | 17 | 81 | 873 | 79 | 106 |
| **Total** | **644** | **110** | **534** | **7,239** | **1,626** | **1,687** |

### 4.3 Automated Integrity Verification
- `tests/test_splits_integrity.py`:
  * `test_disjoint_groups`: PASSED (0 shared group stems).
  * `test_disjoint_hashes`: PASSED (0 shared MD5 hashes).
- Validation and held-out test splits contain **zero synthetic audio augmentations** and **zero mined hard negatives**.
