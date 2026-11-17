# Phase 3 Initial Audit & Baseline Verification Report

**Prepared by:** Senior Audio Machine-Learning & Acoustic AI Systems Engineer  
**Date:** October 28, 2026  
**Repository:** [e:/gunshot/gunshot](file:///e:/gunshot/gunshot)  
**Preserved Phase 2 Checkpoint:** [`models/phase2_yamnet_bundle/`](file:///e:/gunshot/gunshot/models/phase2_yamnet_bundle)  
**Preserved Baseline Checkpoint:** [`models/baseline_yamnet_bundle/`](file:///e:/gunshot/gunshot/models/baseline_yamnet_bundle)

---

## 1. Verified Phase 2 Baseline Metrics

The Phase 2 model bundle was evaluated on the untouched 519-window held-out test set (37 unseen recordings) at the selected operating threshold of **0.480**:

| Metric | Phase 2 Baseline Value | Target Requirement | Evaluation Status |
| :--- | :---: | :---: | :---: |
| **Total Test Windows** | 519 (245 gunshot, 274 background) | 519 | Verified exact match |
| **Window Precision** | **91.11%** | $\ge 90\%$ | **Target Achieved** |
| **Window Accuracy** | **88.44%** | $\ge 90\%$ | Needs +1.56% to reach 90% |
| **Window Recall** | **83.67%** | $\ge 90\%$ | Needs +6.33% to reach 90% |
| **Window F1 Score** | **87.23%** | $\ge 90\%$ | Needs +2.77% to reach 90% |
| **Window ROC-AUC** | **94.61%** | $\ge 95\%$ | Needs +0.39% to reach 95% |
| **False Positives (FP)** | **20 windows** (out of 274 bg) | Minimize | 88.5% reduction from baseline |
| **False Negatives (FN)** | **40 windows** (out of 245 gun) | Minimize | Mostly trailing silence |
| **Gunshot Recordings Detected**| **17 / 17 (100.0%)** | $\ge 90\%$ | **100% of Events Detected** |
| **Streaming False Alerts/hr** | **159.1 / hr** (Confirm=2) | Minimize | Dropped from 787.7/hr |
| **Sustained Inference Latency** | **105.0 ms** (mean) / **116.3 ms** (p95) | $< 480\text{ ms}$ | **~22% budget used** |

### Confusion Matrix at Threshold 0.480:
```text
                 Predicted Background    Predicted Gunshot
Actual Background         254                    20          (Precision: 91.11%)
Actual Gunshot             40                   205          (Window Recall: 83.67%)
```

---

## 2. Pipeline Preprocessing & Feature Consistency Audit

A forensic verification was performed comparing audio caching vs. live inference:
- **Sample Rate & Resampling:** Both caching ([`dataset.py`](file:///e:/gunshot/gunshot/dataset.py)) and real-time streaming ([`live_detector.py`](file:///e:/gunshot/gunshot/live_detector.py), [`app.py`](file:///e:/gunshot/gunshot/app.py)) convert all incoming audio to **16,000 Hz mono float32** with polyphase sinc resampling (`resample_poly`).
- **Framing & Hop Size:** Exactly 15,360 samples (0.96s) window length with 7,680 samples (0.48s) hop stride across all components.
- **YAMNet Feature Extraction:** Extracts identical 1024-dimensional bottleneck activations using frozen MobileNet AudioSet weights.
- **Silence Squelch Gate:** Both pipelines enforce RMS energy squelch ($RMS < 1\times 10^{-4}$ zeroes out score to `0.0`).
- **Verdict:** Preprocessing between training, evaluation, and live inference is **100% consistent**.

---

## 3. Identified Weaknesses & Failure Modes

### Weakness A: Whole-File Weak Labeling Contaminating Positive Windows
- In the current dataset, window labels inherit directly from whole-file labels (`label = 1`).
- When a gunshot recording is 5 to 30 seconds long, only 0.5s to 2.0s contains actual gunshot sound.
- The remaining duration consists of room tone, shooter breathing, wind hiss, or pure silence.
- 51 positive test windows have $RMS < 0.015$, including 8 windows in `soundreality-gun-shot-341144` with $RMS = 0.00000$ (pure dead silence).
- The model correctly predicts `0.0` on silence, but evaluation flags these as "false negatives".
- **Remedy:** Implement timestamp-aware event annotations (`data/manifests/gunshot_events.csv`) to distinguish actual gunshot intervals from trailing ambient silence.

### Weakness B: Insufficient Diversity of Real-World Negative Transients
- The original dataset contained room tone, music, and firearm mechanical foley, but lacked real recorded fireworks, vehicle backfires, balloon bursts, hammer strikes, and dropped objects.
- While synthetic acoustic modeling helped in Phase 2, real field deployment demands **real-world recorded negatives** with complex room acoustics and natural dispersion.
- **Remedy:** Execute web-based acquisition of openly licensed, high-fidelity real negative audio datasets (ESC-50, Freesound, AudioSet, FSD50K, BBC Sound Effects, Zenodo).

### Weakness C: Split Size & Streaming Duration Constraints
- Held-out test set currently comprises 37 recordings (519 windows).
- Continuous negative test audio is ~204 seconds.
- **Remedy:** Expand test audio with verified independent real negative audio to establish hours of continuous negative evaluation with robust Poisson confidence intervals.

---

## 4. Implementation Action Plan & Files to Modify

| Component | Target File | Planned Engineering Action |
| :--- | :--- | :--- |
| **Web Negative Audio Ingestion** | [`scripts/download_negative_audio.py`](file:///e:/gunshot/gunshot/scripts/download_negative_audio.py) | Implement automated download, metadata extraction, license logging, and hash deduplication from openly licensed sources (ESC-50, Zenodo, Freesound). |
| **Event-Level Timestamp Annotation** | [`scripts/annotate_gunshot_events.py`](file:///e:/gunshot/gunshot/scripts/annotate_gunshot_events.py) | Profile positive audio energy envelopes, detect onset/decay intervals, and generate `data/manifests/gunshot_events.csv`. |
| **Dataset Window Slicer** | [`dataset.py`](file:///e:/gunshot/gunshot/dataset.py) | Integrate event-interval window labeling: windows overlapping verified gunshot intervals = 1; trailing silence = 0. |
| **Hard-Negative Mining** | [`scripts/hard_negative_miner.py`](file:///e:/gunshot/gunshot/scripts/hard_negative_miner.py) | Scan newly downloaded real negative recordings, queue false positives, and ingest approved clips into training. |
| **Classifier & Stacking** | [`scripts/train_final_system.py`](file:///e:/gunshot/gunshot/scripts/train_final_system.py) | Train multi-model ensemble (Regularized MLP + CatBoost + LightGBM + XGBoost) on enriched dataset with timestamp-aware labels. |
| **Event-Level Evaluation** | [`scripts/evaluate_event_level.py`](file:///e:/gunshot/gunshot/scripts/evaluate_event_level.py) | Measure distinct event recall, detection delay, and false alarms per hour. |
| **Evaluation Reporting** | [`evaluate.py`](file:///e:/gunshot/gunshot/evaluate.py) | Update evaluation script to report both legacy window metrics and timestamp-aware event metrics. |
| **Packaging & Verification** | Archive generator | Verify regression test suite and package `e:/gunshot/gunshot_detection_phase3.zip`. |
