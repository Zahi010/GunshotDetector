# PHASE 37 DATASET INDEPENDENCE & LINEAGE AUDIT
## Provenance, Overlap & Evaluation Independence Assessment of the Phase 36 Corpus

> [!CAUTION]
> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.**
> This experimental acoustic machine-learning software is uncertified and must never be deployed for autonomous emergency dispatch, police tactical response, active-shooter alerting, automated evacuation, building lockdown, or life-critical physical security.
> Use legally obtained recordings and safe audio playback only. Live-fire testing and hazardous acoustic experiments are strictly prohibited.

---

## 1. Executive Summary & Verdict

Phase 36 assembled an evaluation inventory of **87 audio recordings** categorized into three partitions:
- Partition 1: Continuous Negative Ambient (4 streams, 5.0 gross hours).
- Partition 2: Controlled Positives (23 streams, 53 annotated rounds).
- Partition 3: Reviewed Non-Target Distractors (60 clips).

### CORE FORENSIC FINDING: `REPEATED_HISTORICAL_EVALUATION`
A comprehensive cryptographic and lineage audit against historical project phases (Phases 1–35) establishes that:
- **0 out of 87 recordings are genuinely new out-of-sample acquisitions.**
- **87 out of 87 recordings (100.0%) are exact, bit-for-bit SHA-256 matches to pre-existing files in the repository.**
- **All 23 positive recordings and all 53 annotated rounds** are identical to the normalized corpus evaluated in Phase 19, Phase 20, Phase 21, and Phase 32.
- **The 4 continuous negative streams** were drawn directly from Phase 8 (UrbanSound continuous evaluation) and Phase 15.
- **The 60 distractor clips** were drawn from repository directories created in Phase 2/4 and Phase 15.

> [!IMPORTANT]
> Zero overlap with the historical 23-stream continuous-negative benchmark (Southampton, Chew Magna, Bilbao, Adelaide) **did NOT establish dataset independence**. 
> Phase 36 was a **rigorous multi-dataset regression re-evaluation on historical assets**, not an independent validation on unseen external data.

---

## 2. Partition-by-Partition Provenance Breakdown

### Partition 1: Continuous Negative Ambient (4 Streams, 5.0h)
- `continuous_stream_01_urban_transit_sirens_1hr.wav`: First used in **Phase 8** ([phase8_final_eval/continuous_ambient/](file:///E:/gunshot/gunshot/data/phase8_final_eval/continuous_ambient/)).
- `continuous_stream_02_domestic_interior_transients_1hr.wav`: First used in **Phase 8**.
- `continuous_stream_03_outdoor_natural_ambience_1hr.wav`: First used in **Phase 8**.
- `phase15_independent_continuous_2hr.wav`: First used in **Phase 15** ([phase15_independent_eval/continuous/](file:///E:/gunshot/gunshot/data/phase15_independent_eval/continuous/)).
- **Provenance Classification:** `EXACT_MATCH_TO_HISTORICAL_RECORDING` (4/4, 100%).

### Partition 2: Controlled Ballistic Positives (23 Streams, 53 Rounds)
- **Category A (20 streams, 50 rounds):** ShotSpotter Pittsburgh PA Data Quality Verification 2018. Exact normalized files generated in **Phase 19** ([phase19_independent_positive/normalized_16k/](file:///E:/gunshot/gunshot/data/phase19_independent_positive/normalized_16k/)).
- **Category B (3 streams, 3 rounds):** Reference acoustic recordings generated in **Phase 19**.
- **Annotations:** Exact match to [phase19_event_annotation_manifest.csv](file:///E:/gunshot/gunshot/reports/phase19_event_annotation_manifest.csv).
- **Provenance Classification:** `EXACT_MATCH_TO_HISTORICAL_RECORDING` (23/23, 100%).

### Partition 3: Reviewed Non-Target Distractors (60 Clips)
- **54 clips:** Selected alphabetically (first 6 clips per subfolder) from `data/background/hard_negatives/` (balloon bursts, door slams, fireworks, laser contact mics, metal hammer impacts, percussion transients, thunder rumbles, toy guns, vehicle backfires). Created in **Phase 2 / Phase 4** and used during baseline development and tuning.
- **6 clips:** Selected alphabetically from `data/phase15_independent_eval/negatives/` (ESC-50 clapping).
- **Provenance Classification:** `EXACT_MATCH_TO_HISTORICAL_RECORDING` (60/60, 100%).
- **Selection Bias Note:** The clips were not actively chosen by searching Phase 36 errors, but their availability during baseline development represents in-sample exposure for Phase 14 and Phase 17.

Full recording-level audit matrix is codified in [phase37_dataset_lineage.csv](file:///E:/gunshot/gunshot/experiments/phase37/phase37_dataset_lineage.csv).
