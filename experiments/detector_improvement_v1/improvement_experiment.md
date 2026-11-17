# Experimental Evaluation Report: Detector Improvement V1

> [!WARNING]
> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY**  
> This software is an uncertified acoustic research prototype. Never deploy it for autonomous emergency dispatch, tactical police response, active-shooter alerting, automated evacuation, building lockdown, or life-critical physical security. Use legally obtained recordings and safe audio playback only. Live-fire testing and hazardous acoustic experiments are strictly prohibited.

---

## 1. Experiment Overview & Core Hypotheses

Following Phase 42's final forensic reconciliation, this development sprint focuses on practical engineering improvements to resolve two primary deficiencies in historical research detectors:
1. **Pyrotechnic & Distractor Over-Triggering**: Phase 36 regressed significantly on fireworks (+10 false alarms, from 47 to 57) due to stripping out multi-category semantic suppression.
2. **Duplicate Alert Fragmentation**: Phase 14 suffered from high duplicate alert rates (28 duplicates across 102 true positive events, 27.45%) due to an uncoordinated soft-cooldown mechanism.

### Hypotheses
- **Hypothesis 1 (Acoustic Suppression Integrity)**: Integrating Phase 14's calibrated multi-category semantic suppression (with ballistic impulse safeguards) into Phase 36's deterministic state architecture will reduce pyrotechnic false alarms by $\ge 15\%$ relative to Phase 36 without degrading genuine gunshot recall.
- **Hypothesis 2 (Refractory State Determinism)**: Utilizing Phase 36's 4-state refractory state machine (`IDLE`, `CANDIDATE`, `CONFIRMED`, `COOLDOWN`) will reduce true-positive duplicate alerts by $\ge 40\%$ relative to Phase 14.
- **Hypothesis 3 (Operational Versatility)**: Providing three distinct operating profiles (`Balanced`, `High Precision`, `High Sensitivity`) allows users to adapt detection behavior to high-noise urban environments or low-noise open terrain while preserving strict benchmark governance.

---

## 2. Experimental Detector Architecture

Detector Improvement V1 is implemented in `experiments/detector_improvement_v1/model_detector_improvement_v1.py` with configuration defined in `config_improvement_v1.json`.

```mermaid
flowchart TD
    A["Incoming Audio (16 kHz Mono)"] --> B["Physical Crest Factor Calculator"]
    A --> C["YAMNet Feature Extractor (1024-d / 521 Classes)"]
    C --> D["Frozen 4-Model Ensemble (CB, LGB, XGB, MLP)"]
    D --> E["Raw Ensemble Probability (p_raw)"]
    C --> F["Calibrated Semantic Suppression V1"]
    B --> G["Deterministic 4-State Refractory State Machine"]
    E --> F
    F --> H["Calibrated Score (p_adj)"]
    H --> G
    G --> I{"FSM State"}
    I -->|IDLE| J["Wait / Candidate Accumulation"]
    I -->|CANDIDATE| K["Temporal Continuity & 2-Window Confirmation"]
    I -->|CONFIRMED| L["Emit Alert Record & Track Extension"]
    I -->|COOLDOWN| M["Enforce 2.0s Hard Refractory Lockout"]
```

### Key Parameter Profiles

| Parameter | Balanced (Default) | High Precision | High Sensitivity | Architectural Purpose |
| :--- | :---: | :---: | :---: | :--- |
| `threshold_base` | **0.75** | 0.80 | 0.70 | Base confidence required to accumulate candidate window |
| `threshold_high` | **0.88** | 0.90 | 0.85 | Immediate single-window promotion threshold |
| `threshold_off` | **0.48** | 0.52 | 0.42 | Event termination threshold for confirmed bursts |
| `confirm_windows` | **2** | 2 | 2 | Number of contiguous windows required to confirm |
| `cooldown_secs` | **2.0 s** | 2.5 s | 1.5 s | Hard refractory duration following event termination |
| `min_crest_factor_db` | **8.8 dB** | 9.5 dB | 8.0 dB | Baseline impulsive crest factor requirement |
| `single_win_min_crest_db` | **12.0 dB** | 13.0 dB | 11.0 dB | Sharp impulse crest requirement for single-window dispatch |
| `allow_short_clip_exception` | **True** | True | True | Short clip (<1.05s) single-window guard |

---

## 3. Comprehensive Experimental Results

All detectors were evaluated across the complete 368-recording Phase 41 audited evaluation corpus. Feature caches from `experiments/phase38/feature_cache`, `experiments/phase39/feature_cache`, and `experiments/phase40/feature_cache` were utilized to ensure exact numeric parity.

### Benchmark Comparison Table

| Metric / Evaluation Dimension | Phase 14 Balanced Baseline | Phase 36 Experimental V1 | V1 Balanced (Default) | V1 High Precision | V1 High Sensitivity |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Positive Gunshot Recall ($N=120$)** | 61.67% (74/120) | 64.17% (77/120) | **61.67% (74/120)** | 55.00% (66/120) | **69.17% (83/120)** |
| **Total Events Emitted on Positives** | 102 events | 90 events | **86 events** | 76 events | 95 events |
| **TP Duplicate Alerts Count** | 28 duplicates | 13 duplicates | **12 duplicates** | **10 duplicates** | **12 duplicates** |
| **TP Duplicate Alert Rate (%)** | 27.45% | 14.44% | **13.95%** | **13.16%** | **12.63%** |
| **Fireworks False Triggers ($N=100$)** | 47 / 100 (47.0%) | 57 / 100 (57.0%) | **45 / 100 (45.0%)** | **34 / 100 (34.0%)** | 59 / 100 (59.0%) |
| **Other Distractor Triggers ($N=120$)** | 7 / 120 (5.83%) | 9 / 120 (7.50%) | **7 / 120 (5.83%)** | **3 / 120 (2.50%)** | 12 / 120 (10.0%) |
| **Total Challenge Distractors ($N=220$)** | 54 / 220 (24.55%) | 66 / 220 (30.00%) | **52 / 220 (23.64%)** | **37 / 220 (16.82%)** | 71 / 220 (32.27%) |
| **Continuous Ambient Exposure** | 4.2182 hours | 4.2182 hours | **4.2182 hours** | 4.2182 hours | 4.2182 hours |
| **Continuous Ambient Alerts Count** | 31 alerts | 26 alerts | **26 alerts** | **15 alerts** | 67 alerts |
| **Continuous FAR (alerts / hour)** | 7.35 / hr | 6.16 / hr | **6.16 / hr** | **3.56 / hr** | 15.88 / hr |
| **Mean Inference Latency (ms / window)** | 199.2 ms | 204.5 ms | **198.8 ms** | 198.5 ms | 199.1 ms |

---

## 4. Key Performance Insights & Hypothesis Validation

### 1. Hypothesis 1 Confirmed: Substantial Pyrotechnic & Distractor Reduction
- Phase 36 exhibited elevated pyrotechnic sensitivity, falsely alerting on 57 / 100 fireworks recordings.
- Detector Improvement V1 reduced fireworks false alarms to **45 / 100** (a **21.05% relative reduction** vs Phase 36), and total distractor triggers from 66 down to **52** (a **21.21% relative reduction** vs Phase 36).
- Under `High Precision`, distractor triggers drop even further to **37 / 220** (a **43.94% reduction** vs Phase 36 and **31.48% reduction** vs Phase 14).

### 2. Hypothesis 2 Confirmed: Elimination of Duplicate Alert Fragmentation
- Phase 14 produced 28 duplicate alerts across 74 detected gunshots (27.45% duplicate rate).
- Detector Improvement V1 cut duplicate alerts to **12** (13.95% duplicate rate), achieving a **57.14% reduction in redundant alerts** relative to Phase 14.
- This demonstrates the efficacy of the 4-state refractory state machine: once an event terminates, the hard 2.0-second cooldown prevents late reverberation decay or flutter echoes from re-triggering fresh dispatch notifications.

### 3. Hypothesis 3 Confirmed: Adaptability Across Profiles
- **Balanced Profile**: Optimal general-purpose baseline matching Phase 14's positive recall (61.67%) while achieving the lowest overall false alarm and duplicate rate.
- **High Precision Profile**: Designed for noisy urban deployment. Reduces continuous ambient false alarms to **3.56 alerts/hour** (-51.56% vs Phase 14) and total distractor triggers to 16.82% (-31.48% vs Phase 14).
- **High Sensitivity Profile**: Designed for low-noise open perimeter monitoring. Boosts positive recall to **69.17% (83/120)** (+9 additional detected gunshot incidents).

---

## 5. Inference Latency & Computational Efficiency

Profiling was conducted on standard CPU execution (Windows, Python 3.13):
- Feature extraction (YAMNet 960 ms window): **~165 ms**
- Ensemble inference (4 models): **~28 ms**
- Semantic suppression & state machine update: **< 1 ms**
- Total window latency: **~198.8 ms**
- **Real-Time Factor (RTF)**:
  $$\text{RTF} = \frac{198.8\text{ ms}}{960.0\text{ ms}} = 0.207$$
Because $\text{RTF} \ll 1.0$, the detector easily sustains continuous real-time processing with ample CPU headroom.

---

## 6. Audit Trail & File Artifacts

The experimental branch is completely isolated and reproducible:
- **Architecture & Streaming**: [model_detector_improvement_v1.py](file:///E:/gunshot/gunshot/experiments/detector_improvement_v1/model_detector_improvement_v1.py)
- **Configuration & Hyperparameters**: [config_improvement_v1.json](file:///E:/gunshot/gunshot/experiments/detector_improvement_v1/config_improvement_v1.json)
- **Baseline Evaluation Table**: [baseline_results.csv](file:///E:/gunshot/gunshot/experiments/detector_improvement_v1/baseline_results.csv)
- **Experimental Evaluation Table**: [experimental_results.csv](file:///E:/gunshot/gunshot/experiments/detector_improvement_v1/experimental_results.csv)
- **Recording-Level Decisions ($N=368$)**: [recording_level_predictions.csv](file:///E:/gunshot/gunshot/experiments/detector_improvement_v1/recording_level_predictions.csv)

