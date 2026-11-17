# PHASE 41 AUDIO SIMILARITY & SOURCE INDEPENDENCE METHODOLOGY REPORT
## Quantitative Acoustic Embedding Analysis & Clustered Provenance Audit

> [!CAUTION]
> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.**
> This software is uncertified research code. It must never be deployed for autonomous emergency dispatch, police tactical response, active-shooter alerting, automated evacuation, building lockdown, or life-critical physical security.
> Use lawfully obtained recordings and safe audio playback only. Live-fire testing and hazardous acoustic experiments are strictly prohibited.

---

## 1. Executive Summary & Purpose

This audit establishes the mathematical methodology and comprehensive empirical results for evaluating source-level independence and pairwise acoustic similarity across all 368 evaluation audio recordings evaluated in Phase 41.

Earlier phases (e.g. Phase 40) restricted audio similarity scans to the fireworks partition (100 clips) and positive clips (120 clips), omitting other distractors (120 clips) and continuous streams (28 streams). Phase 41 completes the full four-partition audit across all 368 recordings (367 unique waveforms).

### Key Empirical Findings:
1. **Waveform Uniqueness (367 / 368 Unique Waveforms):**
   Across all 368 evaluation clips, exactly one duplicate waveform pair exists: `fsd50k_gun_51749` (uploaded by `erkanozan`) and `fsd50k_gun_115295` (uploaded by `warriorsfan12331`) share identical SHA-256 (`6b272b5b52c6766f...`) and pairwise cosine similarity of exactly 1.000000. All other 366 recordings are physically unique waveforms.
2. **High Source Independence in Short Clips:**
   - **Positive Gunshots:** 120 clips across 120 distinct uploaders (ratio 1.00 clips/uploader).
   - **Fireworks Challenge:** 100 clips across 87 unique uploaders (ratio 1.15 clips/uploader; top uploader 2.0%).
   - **Other Distractors:** 120 clips across 109 unique uploaders (ratio 1.10 clips/uploader; top uploader 2.5%).
   - **All Discrete Distractors:** 220 clips across 188 unique uploaders (ratio 1.17 clips/uploader; top uploader 1.82%).
3. **Clustered Source Provenance in Continuous Streams:**
   - The 28 continuous background streams (4.2182 hours) originate from 19 unique recordists.
   - Recordist `duseigne` (Marc Namblard / Radio Aporee archive) contributed 8 streams (28.57% of streams, 1.2583 hours), generating 28 uploader-correlated stream pairs.
   - This recordist clustering necessitates clustered sandwich standard errors or recordist-grouped Wilcoxon tests for continuous-stream FAR evaluations.

---

## 2. Mathematical Methodology & Metric Formulation

### 2.1 Feature Representation via Transfer Learning
To evaluate acoustic similarity independently of simple time-domain amplitude scaling, each audio recording $i$ is mapped through the frozen YAMNet architecture:
1. Audio is resampled to 16,000 Hz single-channel mono.
2. A Short-Time Fourier Transform (STFT) computes log-mel spectrogram frames using 0.96-second analysis windows with a 0.48-second hop (50% overlap).
3. The convolutional layers extract a 1024-dimensional feature embedding $\mathbf{x}_{i, t} \in \mathbb{R}^{1024}$ for each hop $t \in [1, T_i]$.
4. The recording-level acoustic representation $\mathbf{e}_i$ is obtained by temporal mean-pooling over all $T_i$ valid windows:
$$\mathbf{e}_i = \frac{1}{T_i} \sum_{t=1}^{T_i} \mathbf{x}_{i, t}$$

### 2.2 Pairwise Cosine Similarity
For any pair of recordings $(i, j)$ within an evaluation partition, the acoustic embedding similarity $S(i, j)$ is computed as the inner product of the normalized vectors:
$$S(i, j) = \frac{\mathbf{e}_i \cdot \mathbf{e}_j}{\|\mathbf{e}_i\| \|\mathbf{e}_j\|} = \frac{\sum_{k=1}^{1024} e_{i, k} e_{j, k}}{\sqrt{\sum_{k=1}^{1024} e_{i, k}^2} \sqrt{\sum_{k=1}^{1024} e_{j, k}^2}}$$

Because YAMNet penultimate embeddings undergo ReLU activation before global pooling, $e_{i, k} \ge 0$, constraining $S(i, j) \in [0.0, 1.0]$.

### 2.3 Categorical Risk Stratification
Pairs are categorized according to cryptographic and acoustic similarity criteria:
- **`EXACT_DUPLICATE`:** Physical file SHA-256 collision ($S(i, j) = 1.000000$).
- **`HIGH_ACOUSTIC_SIMILARITY`:** $S(i, j) \ge 0.9000$.
- **`MODERATE_ACOUSTIC_SIMILARITY`:** $0.8500 \le S(i, j) < 0.9000$.
- **`LOW_SIMILARITY_SAME_UPLOADER`:** $S(i, j) < 0.8500$ with identical `uploader_or_recordist`.

Independence status is designated:
- `EXACT_DUPLICATE_WAVEFORM` if identical SHA-256.
- `CORRELATED_SESSION` if uploaded by the same individual or from the same recording session.
- `ACOUSTICALLY_SIMILAR_INDEPENDENT` if uploaded by distinct individuals without shared session metadata.

---

## 3. Partition Source-Lineage Summary Table

| Evaluation Partition | Total Files | Unique Waves | Duration (hr) | Unique Uploaders | Ratio (Files/Up) | Top Uploader | Top Share (%) | Risk Level | Evidence Label |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---|
| `PARTITION_PROSPECTIVE_POSITIVE` | 120 | 119 | 0.1442 | 120 | 1.00 | Single clip | 0.83% | LOW | `VERIFIED_FROM_PHYSICAL_FILE` |
| `PARTITION_FIREWORKS_CHALLENGE` | 100 | 100 | 0.3041 | 87 | 1.15 | 2 clips | 2.00% | LOW | `VERIFIED_FROM_PHYSICAL_FILE` |
| `PARTITION_OTHER_DISTRACTORS` | 120 | 120 | 0.2740 | 109 | 1.10 | 3 clips | 2.50% | LOW | `VERIFIED_FROM_PHYSICAL_FILE` |
| `PARTITION_ALL_DISTRACTORS` | 220 | 220 | 0.5782 | 188 | 1.17 | 4 clips | 1.82% | LOW | `VERIFIED_FROM_PHYSICAL_FILE` |
| `PARTITION_CONTINUOUS_AMBIENT` | 28 | 28 | 4.2182 | 19 | 1.47 | `duseigne` (8) | 28.57% | MODERATE | `VERIFIED_FROM_PHYSICAL_FILE` |
| **TOTAL EVALUATION CORPUS** | **368** | **367** | **4.9406** | **310** | **1.19** | `duseigne` (8) | **2.17%** | **LOW** | `VERIFIED_FROM_PHYSICAL_FILE` |

---

## 4. Pairwise Similarity Audit Results

| Partition | Total Candidates | High Sim ($\ge 0.90$) | Mod Sim ($[0.85, 0.90)$) | Exact Dups | Same-Uploader Pairs | Total Logged Pairs |
|---|:---:|:---:|:---:|:---:|:---:|:---:|
| `PROSPECTIVE_POSITIVE` | 7,140 | 85 | 314 | 1 | 0 | 399 |
| `DISTRACTOR_FIREWORKS` | 4,950 | 258 | 278 | 0 | 13 | 545 |
| `DISTRACTOR_OTHER` | 7,140 | 67 | 173 | 0 | 12 | 251 |
| `CONTINUOUS_AMBIENT` | 387 | 1 | 12 | 0 | 30 | 39 |
| **Total Across Groups** | **19,617** | **411** | **777** | **1** | **55** | **1,234** |

Full machine-readable outputs:
- Lineage dataset: [phase41_source_lineage.csv](file:///E:/gunshot/gunshot/experiments/phase41/phase41_source_lineage.csv)
- Pairwise similarity matrix: [phase41_similarity_results.csv](file:///E:/gunshot/gunshot/experiments/phase41/phase41_similarity_results.csv)
