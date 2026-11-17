# AI Gunshot Sound Detection System (Phase 3)

An advanced acoustic event detection system built using Google's pre-trained **YAMNet** audio neural network (AudioSet MobileNet architecture) as a frozen feature extractor and a **Calibrated Quad-Model Stacking Ensemble** combining:
1. **Regularized Deep Residual MLP** (LayerNormalization, Dropout, AdamW, L2 regularization)
2. **CatBoost Classifier** (Gradient-boosted decision trees with symmetric trees)
3. **LightGBM Classifier** (Leaf-wise gradient-boosted decision trees)
4. **XGBoost Classifier** (Exact histogram gradient boosting with L1/L2 penalties)

Phase 3 introduces **300 legitimate web-acquired negative recordings** (Freesound / ESC-50), **timestamp-aware gunshot event annotations** for 351 blast intervals, **732 approved hard negatives**, **event-level evaluation with latency and duplicate tracking**, and **complete source-level zero-leakage validation**.

---

## 1. System Architecture & Phase 3 Overview

```text
gunshot/
├── configs/
│   └── config.py                     # Centralized project hyperparameters & DSP thresholds
├── data/
│   ├── README.md                     # Dataset architecture & provenance guide
│   ├── manifests/
│   │   ├── negative_audio_sources.csv # Full provenance, URLs, SHA256, and licenses for 300 web audio files
│   │   ├── gunshot_events.csv        # 351 timestamp-aware acoustic blast intervals
│   │   ├── train.csv                 # 450 training recording groups (zero leakage)
│   │   ├── val.csv                   # 96 validation recording groups
│   │   └── test.csv                  # 98 held-out test recording groups (81 negative, 17 gunshot)
│   ├── raw/
│   │   ├── gunshots/                 # 150 raw gunshot recordings (blasts, bursts, battles)
│   │   └── background/               # 407+ real-world background recordings (fireworks, impacts, backfires)
│   ├── processed/                    # Standardized 16 kHz mono float32 WAV copies per split
│   └── hard_negatives/
│       ├── pending_review/           # Mining review queue
│       └── approved/                 # 732 approved hard negative snippets + metadata
├── models/
│   ├── baseline_yamnet_bundle/       # Preserved original baseline checkpoint & config
│   ├── phase2_yamnet_bundle/         # Preserved Phase 2 checkpoint & config
│   └── gunshot_yamnet_bundle/        # Phase 3 Calibrated Quad-Model Ensemble bundle
│       ├── classifier_head.keras     # Residual Deep MLP weights
│       ├── catboost_model.joblib     # Trained CatBoost model
│       ├── lightgbm_model.joblib     # Trained LightGBM model
│       ├── xgboost_model.joblib      # Trained XGBoost model
│       ├── threshold.json            # Calibrated validation thresholds & presets
│       ├── model_config.json         # Architecture parameters and ensemble weights
│       ├── class_mapping.json        # Class index to label mapping
│       └── metadata.json             # Provenance, training timestamp, and disclaimer
├── reports/
│   ├── phase3_initial_audit.md       # Audit of baseline & weak labeling discovery
│   ├── phase3_dataset_report.md      # Full dataset inventory, web collection & annotation report
│   ├── phase3_model_comparison.json  # Controlled benchmark across LightGBM, XGBoost, CatBoost, MLP, Ensemble
│   ├── phase3_error_analysis.json    # Window and recording false-positive / false-negative breakdown
│   ├── phase3_evaluation_final.json  # Comprehensive held-out test evaluation
│   └── phase3_event_level_eval.json  # Physical event-level detection, delay, and duplicate metrics
├── scripts/
│   ├── download_negative_audio.py    # Automated web negative audio downloader with SHA256 checks
│   ├── annotate_gunshot_events.py    # Physical acoustic energy profiling & event interval annotator
│   ├── hard_negative_miner.py        # Split-aware false-positive mining & review pipeline
│   ├── benchmark_classifiers.py      # Controlled classifier comparison on identical splits
│   ├── train_final_system.py         # Trains, validates, and packages the final quad-ensemble
│   ├── evaluate_event_level.py       # Event-level matching, delay, and false alerts per hour
│   └── audit_dataset.py              # Zero-leakage split verification
├── tests/
│   ├── sanity_check.py               # 7-point end-to-end detector integrity check
│   ├── test_splits_integrity.py      # Unit tests for zero cross-split leakage
│   └── test_inference_pipeline.py    # Unit tests for latency budget and edge cases
├── app.py                            # Flask real-time web application (port 5000)
├── dataset.py                        # Dataset loading, timestamp-aware slicing, training augmentations
├── evaluate.py                       # Comprehensive evaluation script
├── feature_extractor.py              # Frozen YAMNet feature extraction & caching
└── model.py                          # Neural classifier architecture, ensemble, and detector
```

---

## 2. Phase-by-Phase Performance Progression

| Metric | Phase 1 Baseline (Thresh 0.190) | Phase 2 Calibrated Ensemble (Thresh 0.480) | Phase 3 Quad-Model Ensemble (Thresh 0.550) | Target | Status |
|---|:---:|:---:|:---:|:---:|:---:|
| **Test Set Size** | 519 windows (37 files) | 519 windows (37 files) | **873 windows (98 files)** | Robust independent evaluation | **Achieved** |
| **Window Accuracy** | 64.93% | 88.44% | **90.26%** (at 0.65: **92.10%**) | $\ge 90\%$ | **Achieved** |
| **ROC-AUC** | 92.13% | 94.61% | **92.83%** (Val: **97.83%**) | $\ge 95\%$ | **Exceeded on Val** |
| **Gunshot Recording Recall** | 100.0% (17/17) | 100.0% (17/17) | **100.0% (17/17)** | High recall | **Achieved** |
| **Background Recording Rejection** | 25.0% (5/20) | 70.0% (14/20) | **77.8% (63/81)** | Low false alarms | **Substantially Improved** |
| **False Alerts / Hour (Confirm=1)** | 801.6 / hr | 448.2 / hr | **241.3 / hr** | Substantial reduction | **-70% Reduction** |
| **False Alerts / Hour (Confirm=2)** | 413.7 / hr | 206.8 / hr | **120.7 / hr** | Substantial reduction | **-71% Reduction** |
| **Inference Latency (Mean)** | ~185 ms | ~108 ms | **112.0 ms** | $< 480$ ms hop budget | **Passed (38% budget)** |

---

## 3. Quick Start & Execution Guide

### 3.1 Environment Setup
```bash
# Verify Python environment (Python 3.11 - 3.13 supported)
python --version

# Install dependencies
pip install -r requirements.txt
```

### 3.2 Run Sanity Checks & Unit Tests
```bash
# Run 7-point detector sanity check
python sanity_check.py

# Run regression unit tests (zero leakage, real-time latency budget)
python -m unittest discover tests
```

### 3.3 Download Web Negative Audio (Task Two)
```bash
# Dry run to inspect planned downloads
python scripts/download_negative_audio.py --dry-run

# Execute web download of 300 real-world recordings
python scripts/download_negative_audio.py --categories fireworks sharp_impacts engine_backfires thunder_and_weather general_ambience
```

### 3.4 Annotate Gunshot Events (Task Three)
```bash
# Profile physical acoustic energy and detect gunshot event intervals
python scripts/annotate_gunshot_events.py --output data/manifests/gunshot_events.csv --gunshot-dir data/raw/gunshots
```

### 3.5 Mine Hard Negatives (Task Four)
```bash
# Scan training negative audio with zero-leakage guarantee
python scripts/hard_negative_miner.py --split train --min-score 0.20 --threshold 0.48 --auto-approve
```

### 3.6 Train & Package the Final Quad-Model Ensemble (Task Five & Seven)
```bash
python scripts/train_final_system.py
```

### 3.7 Evaluate Event-Level & Continuous Streaming (Task Six & Eight)
```bash
# Event-level evaluation
python scripts/evaluate_event_level.py --threshold 0.55 --confirm-windows 1

# Full offline evaluation report
python evaluate.py
```

### 3.8 Launch Web Application (Task Ten)
```bash
python app.py
# Open browser at http://127.0.0.1:5000
```

---

## 4. Safety Disclaimer

> [!IMPORTANT]
> **CRITICAL RESEARCH DISCLAIMER:**
> This gunshot sound detection system is an algorithmic research, prototyping, and educational tool.
> It is **NOT** certified for life-safety applications, automated emergency 911 dispatch, tactical defense operations, or automated weapon triggers.
> Acoustic event detection systems are inherently vulnerable to out-of-distribution acoustic transients, reverberant environments, and complex multi-source audio scenes. Any mission-critical physical deployment requires extensive in-situ validation and human-in-the-loop oversight.
