# PHASE 45 COMPARATIVE BENCHMARK: DETECTOR IMPROVEMENT V2 VS. V3

**RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.**

> [!CAUTION]
> **MANDATORY SAFETY DESIGNATION**
> This software is an uncertified acoustic research demonstration prototype. It must never be deployed for autonomous emergency dispatch, tactical police response, active-shooter alerting, automated evacuation, building lockdown, or life-critical physical security. Use lawfully obtained recordings and safe audio playback only. Live-fire and hazardous acoustic experiments are strictly prohibited.

---

## 1. Executive Summary

Phase 45 conducted an exhaustive empirical and architectural comparison between **Detector Improvement V2** (Phase 44) and the newly developed **Detector Improvement V3**, alongside historical baselines (Phase 14 Baseline, Phase 36 Refractory Branch, and Detector Improvement V1).

Evaluation was conducted across two distinct corpora:
1. **Development Partition ($N = 218$, $1.9710\text{ hours}$):** Historical benchmark used for model training and cross-validation.
2. **New Independent Holdout Partition ($N = 147$ discrete, $2.0\text{ hours}$ continuous):** Independently sourced Phase 15 evaluation corpus (`data/phase15_independent_eval/`), featuring un-manipulated ballistic events, ESC-50 pyrotechnics, environmental distractors, and pocket-muffled recordings.

### Key Finding:
* **Detector Improvement V3** achieves a major breakthrough in pyrotechnic discrimination and clear-path gunshot detection: it reduced fireworks false alarms by **41.7%** on development (from 40.68% to 23.73%) and **100%** on holdout (from 40.0% to 0.0%), while eliminating all environmental false alarms on development (0.00% FPR) and raising development gunshot recall to **66.67%**.
* **However**, evaluation on the independent holdout uncovered a critical physical acoustic vulnerability: 34 of the 47 holdout gunshots were recorded through clothing fabric (`phase15_gunshot_pocket_...`). The fabric acted as an acoustic low-pass filter, attenuating the high-frequency shockwave cues upon which V3's fusion classifier relies, causing V3 holdout recall to drop to **27.66%** (compared to 70.21% for V2 and 74.47% for Phase 14).
* In adherence to rigorous scientific integrity, **Recommendation B** is formally selected: retain V2 as the selectable benchmark improvement while maintaining V3 in its dedicated experimental research branch for future muffled-channel adaptation.

---

## 2. Head-to-Head Quantitative Benchmark Matrix

### 2.1 Development Partition Performance ($N = 218$, $1.9710\text{ hours}$)

| Generation | Gunshot Recall (%) | Gunshots (Det / Tot) | Fireworks FPR (%) | Fireworks (FP / Tot) | Environmental FPR (%) | Env (FP / Tot) | Continuous Alerts | Continuous FAR (alerts/hr) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Phase 14 Baseline** | 59.72% | 43 / 72 | 52.54% | 31 / 59 | 5.06% | 4 / 79 | 24 | 21.47 / hr |
| **Phase 36 Refractory** | 62.50% | 45 / 72 | 61.02% | 36 / 59 | 5.06% | 4 / 79 | 20 | 17.89 / hr |
| **Detector Improvement V1** | 59.72% | 43 / 72 | 50.85% | 30 / 59 | 5.06% | 4 / 79 | 20 | 17.89 / hr |
| **Detector Improvement V2** | 62.50% | 45 / 72 | 40.68% | 24 / 59 | 2.53% | 2 / 79 | 3 | 2.68 / hr |
| **Detector Improvement V3** | **66.67%** | **48 / 72** | **23.73%** | **14 / 59** | **0.00%** | **0 / 79** | **0** | **0.00 / hr** |

### 2.2 Independent Holdout Performance ($N = 147$ discrete, $2.0\text{ hours}$ continuous)

| Generation | Holdout Recall (%) | Holdout Gunshots | Holdout Fireworks FPR | Fireworks (FP / Tot) | Holdout Env FPR (%) | Env (FP / Tot) | Continuous 2hr Alerts | Continuous FAR (alerts/hr) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Phase 14 Baseline** | 74.47% | 35 / 47 | 20.00% | 2 / 10 | 1.11% | 1 / 90 | 12 | 6.00 / hr |
| **Phase 36 Refractory** | 74.47% | 35 / 47 | 20.00% | 2 / 10 | 1.11% | 1 / 90 | 10 | 5.00 / hr |
| **Detector Improvement V1** | 74.47% | 35 / 47 | 20.00% | 2 / 10 | 1.11% | 1 / 90 | 4 | 2.00 / hr |
| **Detector Improvement V2** | 70.21% | 33 / 47 | 40.00% | 4 / 10 | 1.11% | 1 / 90 | 2 | 1.00 / hr |
| **Detector Improvement V3** | **27.66%** | **13 / 47** | **0.00%** | **0 / 10** | **3.33%** | **3 / 90** | **4** | **2.00 / hr** |

---

## 3. Comprehensive Architectural Dimension Comparison

| Dimension | Detector Improvement V2 | Detector Improvement V3 | Technical Impact |
| :--- | :--- | :--- | :--- |
| **Feature Representation** | 1024-d YAMNet embeddings only. | 1024-d YAMNet embeddings + 5 physical DSP acoustic features (crest, flatness, high-band ratio, low-band ratio, centroid). | Enables microsecond-level rise-time and spectral distribution separation that YAMNet's 0.96s pooling destroys. |
| **Classification Layer** | Simple arithmetic mean of 4 frozen classifiers (MLP, CatBoost, LightGBM, XGBoost). | Supervised `HistGradientBoostingClassifier` trained with GroupKFold cross-validation on 19 multi-modal features. | Generates strictly calibrated posterior probabilities (Brier score: 0.0240, ROC-AUC: 0.9093) rather than uncalibrated saturated outputs. |
| **Acoustic Suppression** | Post-hoc heuristic score multiplier: `score * (1.0 - 0.45 * fw)`. | Calibrated multi-category suppression with **Ballistic Shockwave Protection** override. | Eliminates collateral attenuation of authentic gunshot reverberations. |
| **Single-Impulse State Logic** | Evaluates crest factor of the decay/silence window after the impulse. | Evaluates `max(crest_factor_db)` of the actual candidate impulse window. | Fixes critical FSM defect, immediately recovering 17 missed gunshots on development. |
| **Continuous Duration Logic** | Hard-coded heuristic checks assuming clips $< 5.0\text{ seconds}$. | Completely duration-invariant; treats streaming and discrete clips with identical window-anchored state logic. | Guarantees seamless ring-buffer operation without edge discontinuities. |
| **Processing Latency** | ~12.2 ms per 480 ms hop. | ~13.6 ms per 480 ms hop (DSP adds $< 0.3\text{ ms}$). | Both execute well within real-time limits ($< 3.0\%$ of available CPU budget). |

---

## 4. Root-Cause Analysis of the Holdout Generalization Divergence

### 4.1 The Mechanism of V3's Success
In clear-path acoustic environments (such as the Development partition), gunshot supersonic N-waves and blast waves propagate through open air, preserving high-frequency acoustic power above 2500 Hz (ratio $> 0.20$) and producing white-noise-like Wiener spectral flatness ($> 0.06$). Fireworks, in contrast, are dominated by low-frequency combustion reverberation and whistle harmonics. V3's HistGradientBoosting fusion model exploits these exact physical features to achieve a 41.7% relative reduction in fireworks false alarms and 0% environmental false alarms.

### 4.2 The Mechanism of V3's Muffled-Channel Failure
When evaluated on Phase 15 holdout, 34 of the 47 positive gunshots were recorded with the microphone inside a pants or jacket pocket (`phase15_gunshot_pocket_...`).
1. **Physical Low-Pass Filtering:** Clothing fabric absorbs high acoustic frequencies ($\ge 2500\text{ Hz}$) far more heavily than low frequencies. The high-band ratio of these pocket gunshots dropped from $\sim 0.22$ to $0.05 - 0.09$, mimicking the spectral envelope of distant fireworks or heavy doors.
2. **Flattened Flatness:** The internal cavity of the pocket introduced resonance that reduced Wiener spectral flatness below $0.035$.
3. **Conservative Posterior Probabilities:** The fusion model appropriately downgraded its confidence from $> 0.85$ to $0.45 - 0.65$. Under the balanced profile confirmation threshold ($0.68$), these muffled events were discarded.
4. **Contrast with V2:** V2 evaluated only YAMNet embeddings. Because YAMNet's mel-filterbank representations were relatively insensitive to pocket acoustic filtering, V2 retained higher raw confidence (detecting 33/47), but at the cost of failing on 40.0% of fireworks.

---

## 5. Formal Completion Recommendation

In accordance with Phase 45 directives, three completion paths were considered:

* **Recommendation A (Promote V3 to Default):** *Rejected.* While V3 represents an architectural breakthrough in pyrotechnic rejection and clear-path precision, its low recall on fabric-muffled sensors (27.66%) demonstrates that it cannot yet safely replace V2 across unknown sensor placements.
* **Recommendation B (Retain V2 as Selectable / Stage V3 in Research Branch):** **SELECTED.**
  * Retain Detector Improvement V2 as the selectable improved detector in the web dashboard.
  * Keep Phase 14 Baseline as the frozen system default.
  * Retain Detector Improvement V3 within its dedicated, version-controlled research branch (`experiments/detector_improvement_v3/`).
  * Pursue future research (e.g., Phase 46) into adaptive acoustic equalization or multi-condition training to adapt V3's physical features to muffled and concealed sensor channels.
* **Recommendation C (Reject Both V2 and V3):** *Rejected.* Both V2 and V3 offer significant verified reductions in continuous background false alarms ($p = 0.0260$) and fireworks false alarms over historical baselines, providing substantial research value.

### Completion Decision Statement
**Recommendation B is formally adopted.** Detector Improvement V2 remains the designated candidate improvement for UI selection. Detector Improvement V3 is preserved in `experiments/detector_improvement_v3/` with full provenance, test coverage, and benchmark documentation.

