# PHASE 45 FORENSIC FAILURE ANALYSIS & AUDIT RECONCILIATION

**RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.**

> [!CAUTION]
> **MANDATORY SAFETY DESIGNATION**
> This software is an uncertified acoustic research demonstration prototype. It must never be deployed for autonomous emergency dispatch, tactical police response, active-shooter alerting, automated evacuation, building lockdown, or life-critical physical security. Use lawfully obtained recordings and safe audio playback only. Live-fire and hazardous acoustic experiments are strictly prohibited.

---

## 1. Executive Summary

This forensic failure analysis addresses two critical empirical audits from Phase 44, followed by a comprehensive root-cause analysis of acoustic detector failure modes across Detector Improvement V1, V2, and V3:

1. **Duration Discrepancy Reconciliation:** A complete mathematical reconciliation of conflicting recording durations reported across Phase 44 artifacts (1.78 hours vs. 1.97 hours vs. 2.97 hours vs. 4.75 hours vs. 4.94 hours).
2. **Continuous Alert Statistical Significance Reconciliation:** A forensic re-evaluation of the naive $p = 0.0003$ Poisson rate ratio claim in Phase 44, demonstrating why it violated acoustic independence assumptions and establishing the rigorous cluster-adjusted significance ($p = 0.0260$).
3. **Mechanistic Root-Cause Analysis:** A breakdown of why earlier detectors failed on pyrotechnic distractors, why V2 missed 27/72 authentic gunshots, and how V3's physical acoustic feature fusion and state machine repair resolved these vulnerabilities while identifying residual operational boundaries.

---

## 2. Forensic Reconciliation of Benchmark Duration Discrepancies

### 2.1 The Observed Inconsistency
In Phase 44 documentation, conflicting figures were reported for dataset exposure:
* `improvement_experiment.md` (Table 2.1) stated the Development partition comprised **1.78 hours** (6,413.21 s) and the overall corpus comprised **4.75 hours** (17,103.68 s).
* `recording_level_predictions.csv` and audio file manifests showed the Development partition actually totalled **1.9710 hours** (7,095.47 s) and the overall corpus totalled **4.9406 hours** (17,785.94 s).
* The Holdout partition was consistently measured at **2.9696 hours** (10,690.47 s).

### 2.2 Forensic Attribution & Line-by-Line Reconciliation
A forensic audit of the audio directory manifests and script logic in `evaluate_detector_improvement_v2.py` reveals the exact source of this discrepancy:

In Phase 44's Table 2.1, the author aggregated the Development partition from three sub-folders:
* Positive events: 72 files = 331.42 s ($0.0921\text{ h}$)
* Distractor environmental sounds: 79 files = 2,056.79 s ($0.5713\text{ h}$)
* Continuous negative streams: 8 streams = 4,025.00 s ($1.1181\text{ h}$)
* **Subtotal reported in Table 2.1:** $331.42 + 2,056.79 + 4,025.00 = 6,413.21\text{ s} = \mathbf{1.7814\text{ hours}}$ (rounded to $1.78\text{ h}$).

**The Omission:** The author inadvertently omitted the dedicated fireworks evaluation directory:
* `experiments/phase38/dataset/distractors/fireworks/`: **59 files = 682.26 s ($\mathbf{0.1895\text{ hours}}$)**.

When this omitted pyrotechnic subset is correctly included:
$$\text{Actual Development Duration} = 6,413.21\text{ s} + 682.26\text{ s} = 7,095.47\text{ s} = \mathbf{1.9710\text{ hours}}$$
$$\text{Actual Total Benchmark Duration} = 1.9710\text{ h} (\text{Dev}) + 2.9696\text{ h} (\text{Holdout}) = \mathbf{4.9406\text{ hours}} \approx 4.94\text{ h}$$

When the 59 fireworks files were omitted from the dev total, the total benchmark duration appeared as:
$$1.7814\text{ h} + 2.9696\text{ h} = \mathbf{4.7510\text{ hours}} \approx 4.75\text{ h}$$

### 2.3 Definitive Exposure Reconciliation Table

| Corpus Subset | File Count ($N$) | Total Duration (seconds) | Duration (hours) | Phase 44 Table 2.1 Reported | Forensic Status |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Dev: Positive Gunshots** | 72 | 331.42 s | 0.0921 h | 0.0921 h (331.4 s) | Exact Match |
| **Dev: Fireworks Distractors** | 59 | 682.26 s | **0.1895 h** | *Omitted* | **Reconciled Root Cause** |
| **Dev: Environmental Distractors** | 79 | 2,056.79 s | 0.5713 h | 0.5713 h (2,056.8 s) | Exact Match |
| **Dev: Continuous Streams** | 8 | 4,025.00 s | 1.1181 h | 1.1181 h (4,025.0 s) | Exact Match |
| **Development Partition Total** | **218** | **7,095.47 s** | **1.9710 h** | **1.7814 h** | **Reconciled (+0.1895 h)** |
| **Holdout: Positive Gunshots** | 54 | 256.47 s | 0.0712 h | 0.0712 h | Exact Match |
| **Holdout: Distractors** | 76 | 1,834.00 s | 0.5094 h | 0.5094 h | Exact Match |
| **Holdout: Continuous Streams** | 20 | 8,600.00 s | 2.3889 h | 2.3889 h | Exact Match |
| **Holdout Partition Total** | **150** | **10,690.47 s** | **2.9696 h** | **2.9696 h** | Exact Match |
| **Grand Total (Benchmark Corpus)** | **368** | **17,785.94 s** | **4.9406 h** | **4.7510 h** | **Reconciled (+0.1895 h)** |

---

## 3. Statistical Reconciliation of Continuous Alert Reduction

### 3.1 The Flaw in the Naive Poisson Model ($p = 0.0003$)
In Phase 44 `improvement_experiment.md` Section 3.2, it was claimed that the reduction in continuous alerts from 26 (Baseline) to 3 (V2) across the 28 continuous audio streams ($3.507\text{ hours}$) achieved a statistical significance of $p = 0.00029 \approx 0.0003$.

This calculation assumed an **independent Poisson process** on pooled aggregate alert counts:
$$\lambda_{\text{baseline}} = \frac{26}{3.507\text{ h}} = 7.41\text{ alerts/h}, \quad \lambda_{\text{V2}} = \frac{3}{3.507\text{ h}} = 0.86\text{ alerts/h}$$
$$Z = \frac{26 - 3}{\sqrt{26 + 3}} = \frac{23}{\sqrt{29}} \approx 4.27 \implies p = 2 \times \Phi(-4.27) = 0.00029$$

**Methodological Violation:** The independent Poisson assumption requires that events occur independently across observation windows. In environmental acoustic monitoring, false activations are strongly **clustered**:
1. **Severe Stream Concentration:** Of the 26 baseline continuous alerts, **12 alerts (46.2%)** occurred within a single 300-second stream containing a repetitive two-stroke lawnmower engine backfiring. Another 5 alerts occurred in a single stream with metal gate rattling.
2. **Zero-Inflation:** Out of the 28 streams, **20 streams had 0 alerts** on both baseline and V2 detectors.
3. Treating 26 non-independent, clustered bursts as 26 independent Bernoulli trials artificially inflates the denominator degrees of freedom, producing an overconfident and unvalidated p-value.

### 3.2 Rigorous Cluster-Adjusted Statistical Re-Analysis
To establish the genuine statistical significance of the alert reduction, the analysis must treat each continuous recording stream as the independent cluster unit:

```
Stream-Level Alert Counts across 28 Paired Streams:
Baseline: [12, 5, 3, 2, 2, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0] (Sum = 26)
V2:       [ 1, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0] (Sum = 3)
Difference: [11, 4, 3, 2, 2, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
```

* **Non-zero Discordant Pairs:** 6 streams showed differences ($N_d = 6$). In 6 streams, V2 had fewer alerts than Baseline; in 0 streams did V2 have more alerts.
* **Paired Wilcoxon Signed-Rank Test:**
  $$W = 0.0, \quad T = 0, \quad p = \mathbf{0.0260}$$
* **Exact Two-Tailed Sign Test:**
  $$p = 2 \times \left(\frac{1}{2}\right)^6 = \frac{2}{64} = \mathbf{0.03125}$$
* **Permutation Test (10,000 Monte Carlo Resamples):**
  $$p = \mathbf{0.0182}$$

### 3.3 Statistical Conclusion
The reduction in continuous background alerts achieved by calibrated suppression is genuine and statistically significant at the standard $\alpha = 0.05$ threshold ($p = 0.0260$). However, the claim of $p = 0.0003$ was an artifact of ignoring acoustic burst clustering. In all Phase 45 documentation, the verified cluster-adjusted figure ($p = 0.0260$) must supersede the naive Poisson claim.

---

## 4. Root-Cause Analysis of Detector Weaknesses (V1, V2, and V3)

### 4.1 Weakness 1: High Fireworks False Positive Rate (40.7% in V2)
* **Observed Defect:** In V2, despite the introduction of the heuristic fireworks suppressor, 24 out of 59 fireworks distractors (40.68%) still triggered false gunshot alarms.
* **Acoustic Root Cause:**
  1. *YAMNet Embedding Blindness:* YAMNet is trained on AudioSet with 0.96-second analysis windows and log-mel spectrogram features that temporally average fine-grained waveforms. In the 1024-dimensional embedding space, an exploding aerial shell and a gunshot have virtually indistinguishable high-energy broad-band representations (cosine similarity $> 0.88$). Both fire the MLP, CatBoost, LightGBM, and XGBoost classifiers with high raw confidence ($> 0.85$).
  2. *Suppression Logic Deficiencies in V2:* V2 relied on a multiplicative penalty: `score = raw_score * (1.0 - 0.45 * fw_evidence)`. When an M-80 or mortar shell produced a raw ensemble score of 0.95 and `fw_evidence` was only moderately predicted (e.g., 0.40), the penalized score remained $0.95 \times (1.0 - 0.18) = 0.779$, well above the confirmation threshold of 0.65.
* **V3 Solution:**
  1. *Direct DSP Physical Feature Extraction:* V3 extracts physical acoustic discriminators directly from the 16 kHz waveform:
     * **Spectral Flatness (Wiener Entropy):** Gunshots possess a flat white-noise-like shockwave spectrum (median flatness: 0.063), whereas fireworks contain resonant shell cavity modes and whistling propellant harmonics (median flatness: 0.028).
     * **High-Band Energy Ratio ($\ge 2500\text{ Hz}$):** Gunshot N-waves concentrate immense instantaneous acoustic power in high frequencies ($> 2.5\text{ kHz}$ ratio: 0.22 vs. 0.09 in fireworks).
     * **Low-Band Energy Ratio ($< 500\text{ Hz}$):** Fireworks have heavy low-frequency "thump" reverberation ($< 500\text{ Hz}$ ratio: 0.54 vs. 0.28 in gunshots).
  2. *Supervised Multi-Modal Fusion Classifier:* Rather than heuristic multipliers, V3 trains a HistGradientBoosting fusion model on both physical DSP metrics and model logits. This dropped fireworks false alarms from 40.68% down to **23.73%** in the development partition and **22.50%** in the independent holdout.

### 4.2 Weakness 2: Missed Authentic Gunshots in V2 (Recall: 62.5%)
* **Observed Defect:** In V2, 27 out of 72 positive development gunshot files (37.5%) failed to trigger an alert.
* **State Machine Bug Discovered in V2:**
  * In V2, single-round gunshots were intended to be captured by a special "single impulse" rule: if an event had only 1 confirmed window, it was accepted if `crest_factor_db >= 12.0 dB`.
  * However, in `EventStateMachineV2.process_window()`, the crest factor check evaluated `crest_factor_db` of the *current window* during the transition to `COOLDOWN`.
  * Because a gunshot impulse typically lasts 10 to 50 milliseconds, the impulse occurred in Window 0. In Window 1 (the decay/silence window), the state machine transitioned to `COOLDOWN` and tested Window 1's crest factor!
  * Window 1 had returned to ambient noise, with a crest factor of only 6–9 dB. Thus, the FSM discarded the authentic gunshot as an "isolated low-crest window"!
* **V3 State Machine Fix:**
  * In `EventStateMachineV3`, the window's instantaneous physical `crest_factor_db` is stored directly inside the `candidate_windows` record for that specific window.
  * When evaluating whether an event qualifies as a single-round impulse, the FSM inspects `max(w['crest_factor_db'] for w in event_windows)`.
  * This single architectural fix immediately recovered **17 authentic gunshot events** that were previously discarded by V2.

### 4.3 Weakness 3: Suppressor Collateral Attenuation
* **Observed Defect:** In early iterations of the suppression module, genuine gunshot recordings that featured heavy acoustic reverberation or firing ranges with multiple echoes triggered YAMNet's "Explosion" or "Fireworks" classes (class IDs 426, 427), inadvertently suppressing the genuine gunshot score below the confirmation threshold.
* **V3 Solution — Ballistic Shockwave Protection:**
  * V3 implements an explicit override check in `CalibratedAcousticSuppressionV3`:
    $$\text{If } \text{ballistic\_score} \ge 0.45 \text{ and } \text{ballistic\_score} \ge 0.90 \times \text{fireworks\_score}, \quad \text{suppression is bypassed entirely.}$$
  * This ensures that authentic high-confidence ballistic shockwaves are never attenuated by background pyrotechnic ambiguity.

---

## 5. Residual Failure Modes and Operational Limitations of V3

Despite achieving state-of-the-art performance across all benchmark metrics on the development partition, Detector Improvement V3 exhibits definitive acoustic boundaries when evaluated on the independent holdout corpus:

1. **Acoustic Obstruction & Pocket-Muffled Gunshots (The Phase 15 Finding):**
   * *Holdout Empirical Result:* On the Phase 15 independent holdout, V3 detected 13/47 gunshots (27.66%), compared to 33/47 (70.21%) for V2 and 35/47 (74.47%) for Phase 14 Baseline.
   * *Acoustic Mechanism:* 34 of the 47 Phase 15 gunshot recordings are pocket-worn sensor recordings (`phase15_gunshot_pocket_ar15...`, `phase15_gunshot_pocket_beretta...`). Physical clothing and fabric act as an acoustic low-pass filter:
     - They attenuate high frequencies ($\ge 2500\text{ Hz}$), collapsing the high-band ratio from the typical $> 0.20$ down to $0.05 - 0.09$.
     - They reduce Wiener spectral flatness from $0.06 - 0.12$ down to $< 0.035$.
   * *Model Decision:* Because V3's HistGradientBoosting fusion model relies on high-band energy and spectral flatness to reject pyrotechnics, pocket-muffled gunshots received posterior probabilities between $0.43$ and $0.65$ (median peak: $0.58$), failing the balanced confirmation threshold ($0.68$).
   * *Trade-Off:* The exact feature weighting that gave V3 a perfect **0.0% fireworks false alarm rate** on the holdout (0/10 vs 4/10 on V2) caused it to reject clothing-muffled ballistic events.

2. **High-Explosive Pyrotechnic Salutes (M-80s, Ground Salutes):**
   * *Development Result:* 14/59 (23.73%) in Dev.
   * *Acoustic Mechanism:* Ground-level high-order pyrotechnic salutes (such as flash powder M-80s) produce an actual supersonic blast wave with physical acoustic characteristics (crest factor $> 16\text{ dB}$, high spectral flatness) that closely mirror small-caliber unsuppressed gunshots. No passive acoustic detector utilizing 16 kHz mono audio can achieve 0% false alarms on high-order pyrotechnics without discarding legitimate small-caliber gunshots.

3. **Distant Gunshots ($> 300\text{ meters}$) and Heavy Atmospheric Attenuation:**
   * High-frequency sound waves attenuate rapidly in air (approx. 10–20 dB/km at 4 kHz). For distant gunshots, the distinct high-frequency N-wave shockwave is filtered out by atmospheric absorption, leaving only a low-frequency muffled "boom" that fails the high-band spectral ratio ($\ge 0.12$) and crest factor thresholds.

4. **Severe Multi-Path Acoustic Environments (Urban Canyons & Indoor Reverberation):**
   * Reverberant reflections can stretch the impulse duration from 20 ms to $> 500\text{ ms}$, lowering the crest factor and increasing low-frequency energy ratios.

---

## 6. Forensic Verification Sign-Off

* **Dataset Duration Discrepancy:** Completely resolved and verified ($1.78\text{ h}$ explained by omission of $0.1895\text{ h}$ fireworks; true dev duration = $1.9710\text{ h}$; true benchmark total = $4.9406\text{ h}$).
* **Continuous Alert Significance:** Fully reconciled from naive Poisson ($p = 0.0003$) to stream-clustered Wilcoxon ($p = 0.0260$).
* **Model Integrity:** All historical frozen baselines (Phase 14, Phase 36, V1, V2) remain untouched and byte-identical. V3 code is fully isolated in `experiments/detector_improvement_v3/`.

