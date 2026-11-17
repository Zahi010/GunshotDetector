# AI Gunshot Acoustic Sound Detection System (Phase 55 / V10)

> [!CAUTION]
> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.**  
> This acoustic gunshot detection research prototype is uncertified and must **NEVER** be deployed for autonomous emergency dispatch, tactical police response, active-shooter alerting, automated evacuation, building lockdown, or life-critical physical security. All operations must rely exclusively on lawfully obtained recordings and safe audio reproduction.

---

## 1. Project Overview

The **AI Gunshot Acoustic Sound Detection System** is an edge-capable acoustic event recognition platform designed for real-time detection, temporal confirmation, and forensic analysis of firearm discharges. 

The architecture combines Google's frozen **YAMNet** neural network (AudioSet MobileNet backbone, 1024-dimensional embeddings) with high-speed Digital Signal Processing (DSP) acoustic feature extraction and a **Calibrated Quad-Model Stacking Ensemble** (Deep Residual MLP, CatBoost, LightGBM, and XGBoost).

Over 55 progressive research and evaluation phases, the system has advanced from basic window-level classification to a robust, condition-adaptive real-time streaming pipeline. The leading experimental candidate, **Detector Improvement V10**, incorporates:
- **Best-Model Consensus Calibration (BMCC):** Combines individual tree and neural probabilities with strict variance and probability agreement thresholds.
- **Recording-Condition Adaptation:** Automatically classifies operating environments (`CLEAN`, `POCKET_OCCLUDED`, `REVERBERANT`, `NOISY`) and adjusts FSM confirmation thresholds dynamically.
- **4-State Adaptive Finite State Machine (FSM):** Manages temporal state transitions (`IDLE` $\rightarrow$ `SUSPECTED` $\rightarrow$ `CONFIRMED` $\rightarrow$ `REFRACTORY_COOLDOWN`) with a 2.5-second refractory cooldown to eliminate false alert chatter.
- **Acoustic Impostor Suppression:** Handcrafted and learned rejection heads for fireworks, balloon bursts, glassware impacts, and metallic transients.
- **Continuous Live Streaming Dashboard:** A real-time Flask web application with Web Audio API browser capture, in-browser 16 kHz resampling, and sub-20 ms chunk processing latency (24x real-time margin).

---

## 2. System Architecture & Repository Layout

```text
gunshot/
├── app.py                                   # Flask web server & streaming API (port 5000)
├── config.py                                # Centralized DSP thresholds, paths & hyperparameters
├── dataset.py                               # Audio loading, augmentation & window slicing
├── evaluate.py                              # Comprehensive offline evaluation harness
├── feature_extractor.py                     # Frozen YAMNet 1024-d extraction & caching
├── model.py                                 # Core neural architectures, ensemble & baseline detector
├── model_phase14.py                         # Production Default Baseline Detector (Phase 14)
│
├── configs/
│   └── config.py                            # Baseline configuration definitions
│
├── data/
│   ├── README.md                            # Dataset architecture & provenance guidelines
│   ├── manifests/                           # Certified dataset manifests & split tables
│   │   ├── canonical_gunshot_events.csv     # Deduplicated canonical positive gunshot events
│   │   ├── negative_audio_sources.csv       # Provenance, SHA-256 & licensing for web negatives
│   │   ├── phase8_final_eval_manifest.csv   # Phase 8 evaluation corpus
│   │   ├── phase12_independent_eval_manifest.csv # Phase 12 multi-hour continuous manifest
│   │   └── train.csv / val.csv / test.csv   # Zero-leakage contributor-grouped partitions
│   └── hard_negatives/                      # Hard negative mining archives (approved & pending)
│
├── experiments/                             # Phased experimental detector lineages
│   ├── detector_improvement_v1/             # 4-State FSM + Calibrated Suppression
│   ├── detector_improvement_v2/             # Coherence Guard + Pyrotechnic Gating
│   ├── detector_improvement_v5/             # Condition-Adaptive FSM
│   ├── detector_improvement_v6/             # Urban Transient Discrimination
│   ├── detector_improvement_v7/             # Recovered Shockwaves + Backfire Discrimination
│   ├── detector_improvement_v8/             # Pyrotechnic Gating & FSM Tightening
│   ├── detector_improvement_v9/             # Targeted Door Slam & Balloon Remediation
│   ├── detector_improvement_v10/            # Candidate V10: 4-State Adaptive FSM + BMCC Calibration
│   │   ├── model_detector_improvement_v10.py # Full V10 offline & streaming detector engine
│   │   ├── config_improvement_v10.json      # Calibrated thresholds, FSM policies & gate configs
│   │   └── v10_diagnostic_report.md         # Diagnostic validation report
│   ├── phase51_validation/                  # Phase 51 large-scale independent validation
│   ├── phase54_final_validation/            # Phase 54 final independent qualification audit
│   └── phase55_failure_analysis/            # Phase 55 failure forensics & learned rejection research
│       ├── phase55_report.md                # Comprehensive failure post-mortem & reconciliation
│       ├── corpus_accounting_audit.csv      # Certified Phase 54 corpus audit (N=351)
│       ├── heuristic_failure_analysis.md    # Investigation of scalar heuristic breakdown
│       ├── gain_normalisation_experiments.md # Diagnostic gain normalization evaluation
│       ├── learned_rejection_research.md    # GBDT learned rejection model benchmark
│       ├── architecture_recommendation.md   # Two-stage cascaded inference architecture
│       ├── future_holdout_design.md         # Specification for future N=500 qualification holdout
│       ├── v10_live_microphone_integration.md # Web Audio streaming architecture
│       └── v10_live_microphone_test_report.md # Automated hardware streaming benchmark
│
├── models/                                  # Trained neural & ensemble checkpoints
│   ├── gunshot_yamnet_bundle/               # Production Quad-Model Stacking Ensemble
│   │   ├── classifier_head.keras            # Deep Residual MLP weights
│   │   ├── catboost_model.joblib            # CatBoost GBDT checkpoint
│   │   ├── lightgbm_model.joblib            # LightGBM GBDT checkpoint
│   │   ├── xgboost_model.joblib             # XGBoost GBDT checkpoint
│   │   ├── threshold.json                   # Operating profile presets (Balanced, Precision, Sensitivity)
│   │   └── model_config.json                # Feature mappings & ensemble weights
│   └── baseline_yamnet_bundle/              # Preserved historical baseline models
│
├── reports/                                 # Historical audit & benchmark documentation
├── static/
│   ├── css/style.css                        # Modern responsive dark-mode styling
│   └── js/app.js                            # Web Audio API engine, live resampler & telemetry UI
├── templates/
│   └── index.html                           # Multi-mode web dashboard & V10 Live Testing Panel
├── tests/                                   # Regression, sanity, and integration test suites
└── scratch/                                 # Diagnostic scripts, forensic tools & microbenchmarks
```

---

## 3. Phase-by-Phase Performance Progression

| Performance Metric | Phase 1 (Baseline) | Phase 3 (Quad Ensemble) | Phase 14 (Production Default) | Detector Improvement V10 |
| :--- | :---: | :---: | :---: | :---: |
| **Model Architecture** | Single Dense Head | Stacking Ensemble (4 Models) | FSM + Quad Ensemble + DSP | Adaptive FSM + BMCC + V10 Gates |
| **Evaluation Window Size** | 0.96s (Hop 0.48s) | 0.96s (Hop 0.48s) | 0.96s (Hop 0.48s) | 0.96s (Hop 0.48s) |
| **Independent Positive Recall** | 64.9% | 100.0% (17/17) | 88.2% (Phase 14 Test) | **85.9%** (Benchmark) / **70.9%** (Phase 54) |
| **Fireworks Rejection (FPR)** | ~75.0% FPR | ~30.0% FPR | 12.5% FPR | 0.0% (Bench) / 73.3% (Holdout) |
| **Heavy Door Slam Rejection** | 50.0% FPR | 25.0% FPR | 15.0% FPR | **0.0% FPR (V10 Benchmark)** |
| **Balloon Burst Rejection** | 100.0% FPR | 60.0% FPR | 40.0% FPR | **0.0% FPR (V10 Benchmark)** |
| **Continuous False Alerts** | 801.6 alerts/hr | 120.7 alerts/hr | 1.83 alerts/hr | **0.732 alerts/hr (Phase 54 Stream)** |
| **Mean Stream Latency** | ~185 ms | 112.0 ms | 18.5 ms | **12.50 ms / chunk** (8.4x real-time) |
| **Streaming Buffer Stability** | Not supported | File-based streaming | Sub-window buffering | **Zero Dropped Windows (30 min mic)** |

---

## 4. Key Architectural Pillars of Detector Improvement V10

### 4.1 Hybrid Acoustic-Semantic Feature Engine
Input audio is ingested in 0.96s analysis windows (15,360 samples at 16 kHz) with a 50% stride (0.48s hop). For every window, two complementary feature vectors are extracted:
1. **Semantic Embeddings (1024-d):** Extracted from the penultimate layer of Google's frozen YAMNet model, capturing rich semantic environmental acoustics.
2. **Acoustic Waveform Descriptors (10-d):**
   - **Crest Factor ($dB$):** Ratio of peak waveform amplitude to RMS energy ($20 \log_{10}(\text{Peak}/\text{RMS})$). Differentiates sharp ballistic shockwaves ($> 12\text{ dB}$) from continuous hums.
   - **Spectral Centroid ($Hz$) & Rolloff ($Hz$):** Measures frequency distribution and high-frequency roll-off.
   - **Multi-Band Energy Ratios:** Low ($< 500\text{ Hz}$), Mid ($500 - 2000\text{ Hz}$), and High ($> 2000\text{ Hz}$) energy fractions.
   - **Spectral Flatness & Peak Amplitude:** Quantifies acoustic impulsiveness and tonality.

### 4.2 Best-Model Consensus Calibration (BMCC)
Rather than a simple unweighted probability average, V10 employs consensus gating:
```python
if m_min >= min_prob and crest >= min_crest and peak >= min_peak:
    cal_score = max(raw_score, m_mean)
elif m_mean >= mean_th and m_std < std_th and crest >= min_crest and peak >= min_peak:
    cal_score = max(raw_score, m_mean)
elif m_mean >= 0.68 and crest >= 18.0 and peak >= 0.40:
    cal_score = max(raw_score, m_mean)
```
This enables high sensitivity on genuine distant or muffled discharges while requiring strong model agreement on ambiguous acoustic transients.

### 4.3 4-State Adaptive Finite State Machine (FSM)
To eliminate false alarms caused by isolated acoustic clicks while preventing multi-alert chatter during sustained gunfire, V10 features a stateful temporal FSM:
- **`IDLE`:** Default monitoring state. Low energy frames bypass neural computation.
- **`SUSPECTED`:** Triggered when a window exceeds the base threshold ($P \ge 0.70$). Requires temporal confirmation in the subsequent window.
- **`CONFIRMED`:** Transitioned when two consecutive windows confirm elevated probability, OR when a single window exhibits high ballistic confidence ($P \ge 0.88$ with crest factor $\ge 13.5\text{ dB}$). An alert event is dispatched.
- **`REFRACTORY_COOLDOWN`:** Active for 2.5 seconds following confirmation. Mutes subsequent alert triggers to prevent event duplication while recording ongoing acoustic energy.

---

## 5. Real-Time Web Application & Live Dashboard

The project includes a standalone Flask web application (`app.py`) providing an interactive browser interface:

```
http://127.0.0.1:5000
```

### Dashboard Modes:
1. **Continuous Live Microphone Detection:**
   - Real-time streaming listener via browser Web Audio API.
   - Dynamic profile selection: **Balanced** (Base 0.75, High 0.88), **High-Precision** (Base 0.80, High 0.90), or **High-Sensitivity** (Base 0.70, High 0.82).
   - Live VU level meter, latency indicators, and animated alert banners.
2. **Audio File Upload & Forensic Analysis:**
   - Upload WAV, MP3, FLAC, or OGG files for full forensic analysis.
   - Interactive waveform display highlighting exact detection timestamps.
   - Detailed event table listing timestamp spans, peak probabilities, and ballistic crest factors.
3. **V10 Dedicated Live Test Panel:**
   - Isolated testing laboratory specifically locked to `detector_improvement_v10`.
   - Hardware microphone selector dropdown with hot-reconnect support.
   - Real-time 4-state FSM badge (`IDLE`, `SUSPECTED`, `CONFIRMED`, `REFRACTORY_COOLDOWN`).
   - Telemetry monitors: Chunk Latency, Processed Windows, Dropped Windows, and live Diagnostic Log Console.

---

## 6. Quick Start & Execution Guide

### 6.1 Environment Setup
Tested on Windows 10/11, Ubuntu 22.04 LTS, and macOS with Python 3.10 – 3.13.

```powershell
# 1. Clone repository
git clone https://github.com/<YOUR_USERNAME>/gunshot-prototype.git
cd gunshot-prototype

# 2. Create and activate virtual environment
python -m venv venv
.\venv\Scripts\activate      # Windows
source venv/bin/activate    # Linux / macOS

# 3. Install dependencies
pip install -r requirements.txt
```

### 6.2 Launch the Real-Time Web Dashboard
```powershell
python app.py
```
Open your browser to `http://127.0.0.1:5000`.

### 6.3 Run Integration & Verification Test Suites
```powershell
# Run detector sanity check
python tests/sanity_check.py

# Run streaming pipeline unit tests
python -m unittest discover tests

# Run V10 Live Streaming automated microbenchmark
python scratch/test_v10_live_microphone.py
```

### 6.4 Evaluate Detector Candidates
```powershell
# Evaluate Phase 14 Production Default Baseline
python evaluate.py

# Evaluate Detector Improvement V10 on benchmark data
python -c "from experiments.detector_improvement_v10.model_detector_improvement_v10 import DetectorImprovementV10; det = DetectorImprovementV10(); print('V10 initialized successfully!')"
```

---

## 7. Phase 55 Findings & Research Horizon

Phase 55 completed an exhaustive audit of V10 failures on out-of-distribution audio:
- **Heuristic Limitations:** Proved that handcrafted scalar thresholding (`centroid >= 3400 Hz`, `high_ratio >= 0.70`) is structurally fragile. Real-world fireworks exhibit explosive rise times $< 15\text{ ms}$, while room acoustics alter balloon burst centroids into the 1,500–3,300 Hz range.
- **Learned Post-Classification Rejection:** Demonstrated that replacing heuristic rules with a trained Gradient Boosted Decision Tree (GBDT) evaluating 15 multidimensional acoustic and semantic features achieves **83.33% recall with just 1.00% FPR** on an independent test split at negligible computational overhead (0.053 ms latency).
- **Future Direction:** Formal qualification of the Two-Stage Cascaded Architecture with a cryptographically sealed $N=500$ evaluation holdout corpus.

---

## 8. License & Safety Disclaimer

This project is distributed for academic research, algorithmic benchmarking, and educational demonstration purposes.

> [!WARNING]
> **CRITICAL OPERATIONAL DISCLAIMER:**  
> This acoustic gunshot detection software is an experimental prototype. It is **NOT CERTIFIED** for life-safety applications, autonomous emergency 911 dispatch, tactical law enforcement response, active-shooter alerting, automated evacuation, building lockdown, or physical security trigger systems. Acoustic recognition models are subject to acoustic interference, reverberation, environmental masking, and out-of-distribution false positives. Any mission-critical operational deployment requires certified hardware, fail-safe redundant sensors, and mandatory human-in-the-loop verification.
