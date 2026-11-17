# PHASE 40 SOURCE-LEVEL INDEPENDENCE & AUDIT REPORT
## Recording-, Uploader-, Session-, and Campaign-Level Granularity Analysis

> [!CAUTION]
> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.**
> This software is uncertified research code. It must never be deployed for autonomous emergency dispatch, police tactical response, active-shooter alerting, automated evacuation, building lockdown, or life-critical physical security.
> Use lawfully obtained recordings and safe audio playback only. Live-fire testing and hazardous acoustic experiments are strictly prohibited.

---

## 1. Executive Summary

This audit evaluated source-level independence across all four primary evaluation partitions:
1. **Prospective Positive Gunshot Audio:** 120 recordings (140 rounds).
2. **Fireworks Challenge Distractor Audio:** 100 recordings.
3. **Other Acoustic Distractor Audio:** 120 recordings across 6 noise categories (Aircraft, Animal Bark, Music/Percussion, Tools/Impact, Vehicle/Engine, Thunder).
4. **Continuous Ambient Field Streams:** 16 unedited audio recordings.

### Key Audit Findings:
1. **Positive Audio Exhibits Zero Uploader Reuse (`INDEPENDENT_SOURCES`):**
   - The 120 prospective positive clips originate from **120 unique uploaders** across **120 independent sessions** (clustering ratio: **1.00 clips/uploader**).
   - Zero cryptographic SHA-256 collisions exist.
2. **Fireworks Challenge Audio Exhibits Low Clustering (`INDEPENDENT_SOURCES`):**
   - The 100 fireworks clips originate from **87 unique uploaders** across **87 distinct sessions** (clustering ratio: **1.15 clips/uploader**).
   - The top contributor contributed only 3 clips (3.0% concentration).
3. **Continuous Audio Exhibits Moderate Geographic Concentration (`SOURCE_CLUSTERED`):**
   - The 16 continuous ambient field streams originate from **9 distinct recordists** across **16 separate recording sessions/locations** (clustering ratio: **1.78 streams/recordist**).
   - The primary contributor is recordist Vincent Duseigne (contributing 6 streams from French regional preservation projects; 37.5% of continuous streams).
4. **Acoustic Waveform Uniqueness (`VERIFIED_FROM_PHYSICAL_FILE`):**
   - Pairwise cross-similarity audit verified that **zero identical duplicate waveforms** exist across partitions.

---

## 2. Dataset Partition Lineage Summary Table

| Partition Name | Total Recordings | Total Duration (Hours) | Unique Uploaders | Recordings / Uploader Ratio | Top Uploader Count | Top Uploader Concentration (%) | Unique Sessions / Locations | Source Repositories | Clustering Risk Level | Audit Classification |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|---|:---:|:---|
| **Prospective Positive** | 120 | 0.0886 | **120** | **1.00** | 1 | 0.83% | 120 | FSD50K_dev | LOW | `INDEPENDENT_SOURCES` |
| **Fireworks Challenge** | 100 | 0.1601 | **87** | **1.15** | 3 | 3.00% | 87 | Freesound / FSD50K | LOW | `INDEPENDENT_SOURCES` |
| **Other Distractors** | 120 | 0.2081 | **107** | **1.12** | 2 | 1.67% | 107 | Freesound / FSD50K | LOW | `INDEPENDENT_SOURCES` |
| **All Distractors Combined** | 220 | 0.3682 | **188** | **1.17** | 4 | 1.82% | 188 | Freesound / FSD50K | LOW | `INDEPENDENT_SOURCES` |
| **Continuous Ambient** | 16 | 3.1422 | **9** | **1.78** | 6 | 37.50% | 16 | Radio Aporee / Archive.org | MODERATE | `SOURCE_CLUSTERED` |

Full lineage dataset: [phase40_source_lineage.csv](file:///E:/gunshot/gunshot/experiments/phase40/phase40_source_lineage.csv).

---

## 3. Acoustic Cross-Similarity & Waveform Duplication Audit

Using normalized 1024-dimensional YAMNet feature embeddings, all pairwise comparisons within partitions were evaluated (see [phase40_audio_similarity_audit.csv](file:///E:/gunshot/gunshot/experiments/phase40/phase40_audio_similarity_audit.csv)):
- **Cryptographic Collisions:** **0 collisions** detected. All 356 evaluated audio files possess distinct SHA-256 hashes.
- **Identical Master Cuts:** 0 pairs exhibited cosine similarity of 1.0000 with identical temporal duration, confirming no duplicate audio cuts were included.
- **Correlated Sessions:** Across the 100 fireworks clips, only 13 pairwise comparisons involved recordings by the same uploader. In all cases, the recordings captured physically distinct events (different dates, shell types, or locations).
- **High Acoustic Similarity in Positive Audio:** 14 clip pairs exhibited embedding similarity $\ge 0.90$. Inspection revealed these clips captured similar firearm calibers (e.g. 12-gauge shotgun blasts at close range recorded outdoors), but originated from completely distinct uploaders and audio capture equipment.

