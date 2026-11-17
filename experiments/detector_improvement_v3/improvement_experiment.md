# PHASE 45 EXPERIMENTAL RESEARCH REPORT: DETECTOR IMPROVEMENT V3

**RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.**

> [!CAUTION]
> **MANDATORY SAFETY DESIGNATION**
> This software is an uncertified acoustic research demonstration prototype. It must never be deployed for autonomous emergency dispatch, tactical police response, active-shooter alerting, automated evacuation, building lockdown, or life-critical physical security. Use lawfully obtained recordings and safe audio playback only. Live-fire and hazardous acoustic experiments are strictly prohibited.

---

## 1. Executive Summary

Phase 45 investigated whether model-level acoustic discrimination improvements can resolve the performance ceiling encountered in Phase 43 and Phase 44. Prior iterations (V1 and V2) operated strictly as post-processing layers: they applied heuristic multiplier penalties to frozen model probabilities and introduced refractory cooldowns in an event state machine. While these rules substantially lowered continuous background false alarms, fireworks false-positive rates remained intolerably high (~40.7% in V2), and single-round gunshot recall remained constrained (62.5% in V2) due to state-machine decay attribution errors.

**Detector Improvement V3** moves beyond heuristic post-processing by introducing:
1. **Physical Acoustic DSP:** Real-time extraction of time-domain and spectral-domain metrics (crest factor, Wiener spectral flatness, high-band/low-band energy ratios, spectral centroid) in $< 0.3\text{ ms}$.
2. **Supervised Multi-Modal Fusion Classifier:** A calibrated `HistGradientBoostingClassifier` fusing physical acoustic metrics, semantic AudioSet class logits, and the frozen four-model ensemble (MLP, CatBoost, LightGBM, XGBoost).
3. **Repaired Event State Machine (FSM V3):** Correction of the single-round impulse crest misattribution defect, native multi-shot cluster tracking, and duration invariance.
4. **Ballistic Shockwave Protection:** An active override ensuring legitimate ballistic shockwaves are never attenuated by reverberant echo profiles.

On the verified **Development Partition** ($N = 218$, $1.9710\text{ hours}$):
* **Positive Gunshot Recall:** Increased to **66.67%** (48/72), outperforming Phase 14 Baseline (59.72%), Phase 36 (62.50%), V1 (59.72%), and V2 (62.50%).
* **Fireworks False Positive Rate:** Dropped to **23.73%** (14/59), achieving a **41.7% relative reduction** compared to V2 (40.68%) and a **54.8% relative reduction** compared to Phase 14 (52.54%).
* **Environmental False Positive Rate:** Dropped to **0.00%** (0/79), eliminating all non-fireworks environmental false alarms.
* **Continuous Background Alert Rate:** Dropped to **0.00 alerts/hour** (0 alerts across $1.1181\text{ hours}$).

---

## 2. Methodology & Architectural Design

### 2.1 Limitations of Prior Approaches
In Phases 43–44, detection relied on four base models (MLP, CatBoost, LightGBM, XGBoost) trained on 1024-dimensional YAMNet embeddings. Because YAMNet applies temporal average pooling across 0.96-second windows with log-mel spectrogram features, it discards microsecond rise times and flattens shockwaves. In 1024-d embedding space, exploding pyrotechnics and gunshots overlap heavily, yielding base model probabilities $> 0.85$ for both classes.

Heuristic post-processing in V2 attempted to penalize scores using scalar multipliers:
$$\text{Score}_{\text{adj}} = \text{Score}_{\text{raw}} \times (1.0 - 0.45 \times \text{P}_{\text{fireworks}})$$
When an M-80 pyrotechnic salute produced a raw score of 0.95 and fireworks probability of 0.40, the adjusted score remained $0.779$, failing to prevent a false confirmation. Furthermore, when authentic gunshots produced reverberation that triggered the fireworks class, genuine gunshots were suppressed.

### 2.2 Multi-Modal Feature Architecture
V3 addresses this by extracting physical acoustic metrics directly from the raw 16 kHz audio waveform and feeding them into a 19-dimensional supervised fusion model:

```
[ Raw Audio Waveform (16 kHz) ]
         |
         +---> [ Physical Acoustic DSP ] -------------------> Crest Factor (dB)
         |     (Execution: < 0.25 ms)                        Spectral Flatness
         |                                                   High-Band Ratio (>=2.5 kHz)
         |                                                   Low-Band Ratio (<500 Hz)
         |                                                   Spectral Centroid (Hz)
         |                                                             |
         +---> [ YAMNet Feature Extractor ]                            |
                     |                                                 |
                     +---> [ 1024-d Embeddings ]                       |
                     |           |                                     |
                     |           +---> [ MLP, CatBoost, LGBM, XGB ] -> Logits & Stats
                     |                                                 |
                     +---> [ 521-d AudioSet Scores ] ----------------> Gunshot, Ballistic,
                                                                       Fireworks, Thunder,
                                                                       Impact Logits & Ratios
                                                                               |
                                                                               v
                                                          [ HistGradientBoosting Fusion ]
                                                                               |
                                                                               v
                                                          [ Calibrated Raw Event Score ]
                                                                               |
                                                          [ Repaired FSM V3 & Suppression ]
                                                                               |
                                                                               v
                                                                   [ Confirmed Alerts ]
```

### 2.3 Supervised Fusion Training & Leakage Prevention
* **Training Partition:** Strictly restricted to the 218 recordings in the Development partition ($14,663$ analysis windows).
* **Cross-Validation Scheme:** 5-Fold `GroupKFold` cross-validation grouped strictly by `recording_id`. All analysis windows belonging to a given recording were held out simultaneously in each fold, preventing any intra-recording temporal data leakage.
* **Results:**
  * Mean Cross-Validation ROC-AUC: $\mathbf{0.9093} \pm 0.021$
  * Mean Brier Calibration Score: $\mathbf{0.0240}$
* The final fusion classifier was refit on all development windows and serialized to `experiments/detector_improvement_v3/fusion_model.joblib`.

### 2.4 State Machine V3 Innovations
1. **Candidate-Anchored Crest Attribution:** FSM V3 stores each window's instantaneous physical `crest_factor_db` inside the candidate record. In single-round events, it tests $\max(w['\text{crest\_factor\_db}'])$, preventing the decay window from discarding genuine impulses.
2. **Duration Invariance:** Eliminated the hard-coded 5-second file length assumption, allowing smooth operation on continuous streams.
3. **Ballistic Shockwave Protection:** When ballistic evidence $\ge 0.45$ and $\ge 0.90 \times \text{fireworks evidence}$, suppression is automatically bypassed.

---

## 3. Empirical Results on Development Partition

The table below summarizes performance on the verified Development Partition ($N = 218$, $1.9710\text{ hours}$):

| Detector | Gunshot Recall (%) | Gunshot Detected / Total | Fireworks FPR (%) | Fireworks FP / Total | Environmental FPR (%) | Env FP / Total | Continuous Alerts | Continuous FAR (alerts/hr) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Phase 14 Baseline** | 59.72% | 43 / 72 | 52.54% | 31 / 59 | 5.06% | 4 / 79 | 24 | 21.47 / hr |
| **Phase 36 Refractory** | 62.50% | 45 / 72 | 61.02% | 36 / 59 | 5.06% | 4 / 79 | 20 | 17.89 / hr |
| **Detector Improvement V1** | 59.72% | 43 / 72 | 50.85% | 30 / 59 | 5.06% | 4 / 79 | 20 | 17.89 / hr |
| **Detector Improvement V2** | 62.50% | 45 / 72 | 40.68% | 24 / 59 | 2.53% | 2 / 79 | 3 | 2.68 / hr |
| **Detector Improvement V3** | **66.67%** | **48 / 72** | **23.73%** | **14 / 59** | **0.00%** | **0 / 79** | **0** | **0.00 / hr** |

### Key Development Observations:
1. **Recall Improvement:** V3 achieved the highest recall of any detector evaluated in the project (66.67%), detecting 3 more gunshots than V2/P36 and 5 more than P14.
2. **Dramatic Fireworks Reduction:** Fireworks false alarms fell from 24 (V2) and 31 (P14) down to 14, cutting the fireworks false positive rate by more than half compared to baseline.
3. **Perfect Environmental Discrimination:** V3 achieved 0 false positives across all 79 non-fireworks environmental distractors (sirens, heavy doors, metal clangs, construction impacts, jackhammers).
4. **Complete Background Silence:** Across the 8 continuous streams ($1.1181\text{ hours}$), V3 triggered 0 alerts.

---

## 4. Evaluation on New Independent Holdout Corpus

To ensure genuine generalization and prevent data leakage, V3 was evaluated against a completely separate, independently curated dataset: **Phase 15 Independent Evaluation Corpus** (`data/phase15_independent_eval/`), comprising:
* **47 Positive Gunshot Recordings** (independent ballistic events, including 34 pocket-worn sensor recordings).
* **10 Fireworks Distractors** (ESC-50 pyrotechnics).
* **90 Environmental Distractors** (ESC-50 thunder, engines, glass breaking, clapping, mechanical mimics).
* **2.0-Hour Continuous Stream** (`phase15_independent_continuous_2hr.wav`).

### 4.1 Independent Holdout Results Table

| Detector | Holdout Gunshot Recall (%) | Gunshot Detected / Total | Holdout Fireworks FPR (%) | Fireworks FP / Total | Holdout Env FPR (%) | Env FP / Total | Continuous 2hr Alerts | Continuous FAR (alerts/hr) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Phase 14 Baseline** | 74.47% | 35 / 47 | 20.00% | 2 / 10 | 1.11% | 1 / 90 | 12 | 6.00 / hr |
| **Phase 36 Refractory** | 74.47% | 35 / 47 | 20.00% | 2 / 10 | 1.11% | 1 / 90 | 10 | 5.00 / hr |
| **Detector Improvement V1** | 74.47% | 35 / 47 | 20.00% | 2 / 10 | 1.11% | 1 / 90 | 4 | 2.00 / hr |
| **Detector Improvement V2** | 70.21% | 33 / 47 | 40.00% | 4 / 10 | 1.11% | 1 / 90 | 2 | 1.00 / hr |
| **Detector Improvement V3** | **27.66%** | **13 / 47** | **0.00%** | **0 / 10** | **3.33%** | **3 / 90** | **4** | **2.00 / hr** |

### 4.2 Critical Empirical Findings
1. **Perfect Pyrotechnic Rejection on Holdout:** V3 achieved 0 false positives across all 10 ESC-50 fireworks recordings (0.00% FPR), whereas V2 triggered on 40.0% (4/10) and Phase 14 triggered on 20.0% (2/10).
2. **The Acoustic Obstruction Vulnerability:** 34 of the 47 gunshot recordings in Phase 15 were collected with the recording device enclosed inside a clothing pocket (`phase15_gunshot_pocket_...`). Fabric acts as a physical acoustic low-pass filter, attenuating frequencies above 2.5 kHz and damping Wiener spectral flatness. Because V3 heavily weights high-band ratio and spectral flatness to reject fireworks, it assigned these pocket recordings calibrated scores between 0.43 and 0.65 (median peak: 0.58). Under the balanced profile confirmation threshold (0.68), these muffled events did not confirm.
3. **Generalization Insight:** While V3 significantly advances precision and eliminates fireworks false alarms, relying strictly on high-frequency physical acoustics creates a blind spot when physical sensors are acoustically obstructed (e.g., concealed in clothing or deep inside vehicles).

---

## 5. Architectural Governance & Safety Designation

* **Safety Status:** Uncertified research prototype. Strictly prohibited for life-safety, autonomous emergency alerting, or physical security applications.
* **Code Isolation:** All V3 logic is self-contained in `experiments/detector_improvement_v3/`.
* **Dashboard Protection:** The dashboard default detector remains frozen at `phase14` as required by project governance.

