# Audio Dataset Architecture & Operational Guide (Phase 3)

This document describes the structure, provenance, split policy, and curation workflows for the **AI-Powered Gunshot Sound Detection System** following the Phase 3 dataset engineering enhancements.

---

## 1. Directory Structure

```text
data/
├── README.md                      # This documentation guide
├── raw/                           # Original, non-destructively preserved audio files
│   ├── gunshots/                  # 150 original raw gunshot recordings (muzzle blasts, bursts, battles)
│   ├── background/                # 407+ real-world non-gunshot negative audio recordings:
│   │   ├── fireworks/             # 20 real firework & crackle recordings (Freesound / ESC-50)
│   │   ├── sharp_impacts/         # 80 sharp transient impacts (glass break, wood knock, clapping)
│   │   ├── engine_backfires/      # 100 engine backfires, chainsaws, vehicle horns, trains
│   │   ├── thunder_and_weather/   # 60 thunderclaps, rain, wind recordings
│   │   └── general_ambience/      # 40 crackling fire, footsteps, environmental ambience
│   └── synthetic/                 # 50 procedural background noise & acoustic room recordings
├── processed/                     # Standardized 16 kHz mono float32 PCM WAV copies per split
│   ├── train/
│   │   ├── gunshots/              # Standardized training gunshots
│   │   └── background/            # Standardized training background
│   ├── validation/
│   │   ├── gunshots/              # Strictly unaugmented validation gunshots
│   │   └── background/            # Strictly unaugmented validation background
│   └── test/
│       ├── gunshots/              # Held-out test gunshots (unseen recordings)
│       └── background/            # Held-out test background (81 independent unseen recordings)
├── hard_negatives/                # Difficult negative acoustic examples & mining queues
│   ├── pending_review/            # Detected false-positive windows awaiting human verification
│   ├── approved/                  # 732 approved hard negative snippets + approved_hard_negatives.json
│   └── rejected/                  # Rejected non-negative or ambiguous audio windows
└── manifests/                     # Audited catalogs and zero-leakage split manifests
    ├── negative_audio_sources.csv # Full provenance, URLs, SHA256, and licenses for web negative audio
    ├── gunshot_events.csv         # 351 timestamp-aware verified gunshot blast intervals
    ├── train.csv                  # Exact recordings in the Train split
    ├── val.csv                    # Exact recordings in the Validation split
    ├── test.csv                   # Exact recordings in the Held-Out Test split
    ├── migration_log.json         # Complete audit trail of original vs consolidated file paths & MD5 hashes
    └── dataset_inventory.json     # Quantitative inventory summary counts
```

---

## 2. Web-Acquired Real Negative Audio (Task Two)

To eliminate the domain gap between artificial noise and real acoustic environments, **300 legitimate audio recordings** were collected from the web via official repositories (Freesound and ESC-50) under Creative Commons licenses (CC0, CC-BY 3.0, CC-BY 4.0):

| Category | Source Repositories | Count | Acoustic Mimic Profile |
|---|---|---|---|
| **Fireworks & Crackers** | Freesound / ESC-50 (Cat 48) | 20 | Rapid impulsive bursts, propellant explosions, high-frequency crackle |
| **Sharp Acoustic Impacts** | Freesound / ESC-50 (Cats 12, 19, 22) | 80 | Wood knocks, glass breaks, can openings, sharp clapping |
| **Engine Backfires & Machinery** | Freesound / ESC-50 (Cats 34, 38, 41-43) | 100 | Vehicle exhaust pops, chainsaws, train horns, industrial tools |
| **Thunder & Weather** | Freesound / ESC-50 (Cats 17, 18) | 60 | Thunderclaps, lightning cracks, downpours, wind gusts |
| **General Ambience** | Freesound / ESC-50 (Cats 13, 24) | 40 | Crackling fire, footsteps, crowd background |
| **Total Web Audio Acquired** | Curated & Verified | **300** | Full provenance cataloged in `data/manifests/negative_audio_sources.csv` |

Every file was downloaded with integrity verification, SHA-256 fingerprinting, deduplication, and full provenance tracking.

---

## 3. Timestamp-Aware Gunshot Event Annotations (Task Three)

### The Weak Labeling Weakness (Identified in Phase 2)
In the original dataset, several gunshot recordings were 5 to 230 seconds long, but the actual gunshot blast lasted only 0.5 to 1.5 seconds. The remainder of the audio consisted of pure silence, background hiss, or distant echoes. In the legacy pipeline, every window sliced from that recording was labeled `1` (positive). As a result, when the model's silence gate or classifier correctly predicted `0` on trailing silence, it was penalized as a "false negative."

### Acoustic Profiling & Event Detection
Using `scripts/annotate_gunshot_events.py`, every positive recording was profiled using:
- Short-time RMS energy (40 ms window, 15 ms hop).
- Attack rise-time rate ($\ge 12$ dB above estimated noise floor).
- Noise floor estimation (15th percentile of lowest 50% energy).
- Signal-to-Noise Ratio (SNR) in dB and peak blast amplitude.

**Results:**
- **351 distinct gunshot blast intervals** annotated across 150 recordings.
- **45 recordings** identified with long trailing silence ($>1.5$ seconds).
- Saved in `data/manifests/gunshot_events.csv` with start/end timestamps, SNR, and review status.

### Overlap Policy for Window Labeling
When `timestamp_aware=True`:
1. **Positive Window (`label = 1`):** Overlaps an annotated gunshot event by $\ge 0.15$ seconds.
2. **Negative Window (`label = 0`):** Overlap $\le 0.02$ seconds and energy is low (silence / ambient pause).
3. **Ambiguous Window:** Overlap between 0.02s and 0.15s. Excluded during training to prevent gradient noise at event boundaries.

---

## 4. Zero-Leakage Group Splitting Guarantee

- Audio files are grouped by their base recording stem (stripping duplicate markers like ` (1).mp3`) and MD5 content hashes.
- Splitting into **Train (70%)**, **Validation (15%)**, and **Test (15%)** is performed at the **recording group level BEFORE windowing**.
- Windows or duplicate copies from the same recording NEVER appear across more than one split.
- **Split Breakdown:**
  * **Train:** 450 groups (77 gunshot, 373 background) $\rightarrow$ 6,319 training windows (with 732 approved hard negatives).
  * **Validation:** 96 groups (16 gunshot, 80 background) $\rightarrow$ 779 unaugmented windows.
  * **Test:** 98 groups (17 gunshot, 81 background) $\rightarrow$ 873 unaugmented windows.

---

## 5. Hard-Negative Mining Pipeline (Task Four)

To systematically suppress false alarms on acoustic mimics:
```bash
# Step 1: Scan training negative audio with detector (Strict Zero-Leakage: only scans train split)
python scripts/hard_negative_miner.py --split train --min-score 0.20 --threshold 0.48 --auto-approve

# Step 2: Extract embeddings for newly approved hard negatives
python -c "from feature_extractor import YAMNetFeatureExtractor; ..."
```
Approved snippets are stored in `data/hard_negatives/approved/` and added **strictly to the training split**, leaving the validation and test evaluation sets completely unpolluted.
