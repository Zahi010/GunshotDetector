# PHASE 12 DATASET INVENTORY: Provenance, Overlap & Independence Audit

> [!CAUTION]
> **SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY**  
> Complete transparency regarding training and diagnostic data provenance is essential to avoid invalid claims of zero-shot field generalization.

---

## 1. Executive Summary

Phase 12 Stage 1 executed an exhaustive audit across all audio files in the repository to trace the provenance of every recording, discover exact and near-duplicates, and establish which data has been historically examined.

### Core Inventory Findings:
1. **Total Files Audited:** **2,486 audio files** across 7 primary storage locations.
2. **Unique Cryptographic Hashes:** **1,867 distinct SHA-256 digests**.
3. **Exact Duplicates:** **453 hash collisions** identified across different folders (e.g., raw files copied into training and diagnostic directories).
4. **Near-Duplicate Filename Clusters:** **186 stem clusters** where identical audio files exist under alternate encodings or suffix variants (e.g., `(1).mp3`, `(2).mp3`).
5. **Cross-Partition Contamination:**
   - **Zero Train-to-Test Leakage:** 0 hashes overlap between training and diagnostic evaluation sets.
   - **Phase 7 vs. Phase 8 Overlap:** Verified **0 hashes** shared between the Phase 7 benchmark (ShotSpotter/Mitchell testing) and the Phase 8 benchmark (Mitchell training/ESC-50).
6. **Independence Reality:** Because both Phase 7 and Phase 8 benchmarks were actively used in prior phases to analyze failure modes, tune thresholds, and select operating profiles, **neither set qualifies as a virgin, untouched final evaluation set for Phase 12**.

---

## 2. Audio File Distribution by Historical Partition

| Historical Project Partition / Directory | File Count | Primary Acoustic Content | Historical Development Role |
|---|---:|---|---|
| **`data/processed/train/`** | 176 | AudioSet/FreeSound Gunshots & Negatives | Used for model training in Phases 1–4 |
| **`data/processed/validation/`** | 34 | AudioSet/FreeSound Gunshots & Negatives | Used for validation & early stopping |
| **`data/processed/test/`** | 47 | AudioSet/FreeSound Test Subset | Used for testing in Phases 5–6 |
| **`data/phase7_independent_test/`** | 239 | 8 ShotSpotter, 19 Mitchell, 200 ESC-50 | Used for cross-domain evaluation in Phase 7 |
| **`data/phase8_final_eval/`** | 246 | 43 Mitchell ballistic, 200 ESC-50, 3 hrs streams | Used for diagnostic tuning in Phases 8–10 |
| **`data/hard_negatives/`** | 732 | Mined hard negatives (doors, fireworks) | Used for stacking ensemble training |
| **`data/gunshot/` (Raw Pool)** | 150 | FreeSound / Pixabay raw MP3 downloads | Raw ingestion pool |
| **`data/background/` (Raw Pool)**| 265 | FreeSound / Pixabay raw MP3 downloads | Raw ingestion pool |
| **`data/raw/synthetic/`** | 597 | Synthetic pulse and reverberant blends | Experimental synthesis pool |
| **TOTAL INVENTORIED FILES** | **2,486** | **All Categories on Disk** | **Audited and Cataloged** |

---

## 3. Duplicate and Near-Duplicate Analysis

### 1. Exact Duplicate Hash Collisions (453 Groups)
Numerous files in `data/gunshot/` and `data/background/` exist as exact byte-for-byte duplicates due to multi-session web downloads where browser auto-renaming appended suffixes like `(1).mp3` and `(2).mp3`. For example:
- `49053354-machine-gun-307468 (1).mp3` $\equiv$ `49053354-machine-gun-307468.mp3`
- `ajhartman42295-50-caliber-rifle-shot-with-shell-ping-132079 (1).mp3` $\equiv$ `... (2).mp3`
- `alice_soundz-gun-shot-sound-effect-224087 (1).mp3` $\equiv$ `... (2).mp3`

### 2. Cross-Split Overlap & Leakage Audit
- **Train vs. Validation Overlap:** **0 hashes**
- **Train vs. Test Overlap:** **0 hashes**
- **Train vs. Phase 7 Overlap:** **0 hashes**
- **Train vs. Phase 8 Overlap:** **0 hashes**
- **Phase 7 vs. Phase 8 Overlap:** **0 hashes**

*Conclusion:* The repository maintains strict cryptographic separation between its partitions. However, because Phase 7 and Phase 8 benchmarks have already been examined, a truly independent benchmark requires acquiring genuinely unexamined recordings.
