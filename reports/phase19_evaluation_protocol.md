# PHASE 19 — INDEPENDENT EVALUATION PROTOCOL

> [!CAUTION]
> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.**
> This is an experimental acoustic machine-learning research system. It is not certified and must never be used for autonomous emergency dispatch, police response, active-shooter alerting, automated evacuation, or critical physical security.
> Use only legally obtained recordings and safe recorded-audio playback. No live-fire testing or hazardous acoustic experiments.

---

## 1. Scope & Objective

This document pre-registers the evaluation methodology, temporal matching logic, statistical metrics, and decision rules for Phase 19. 
All evaluations are conducted under a strict **frozen model contract**: zero architecture modifications, zero threshold adjustments, zero post-hoc parameter adjustments, and zero data cherry-picking.

The objective is to establish the true out-of-domain generalization of the frozen detectors when tested against genuinely source-independent natural continuous urban gunshot audio.

---

## 2. Evaluated Detector Models & Configurations

Five frozen model configurations are evaluated:

| Model Identifier | Source File | Status & Role | Core Parameters |
| :--- | :--- | :--- | :--- |
| **Phase 14 Balanced** | `model_phase14.py` | **Default Production Baseline** | Conf thresh: 0.75, Crest factor thresh: 6.0 dB, Confirmation: 2 consecutive frames, Cooldown: 2.0 s |
| **Phase 14 High-Precision** | `model_phase14.py` | Operational Profile | Conf thresh: 0.85, Crest factor thresh: 8.0 dB, Confirmation: 3 consecutive frames, Cooldown: 3.0 s |
| **Phase 14 High-Sensitivity** | `model_phase14.py` | Operational Profile | Conf thresh: 0.60, Crest factor thresh: 4.5 dB, Confirmation: 1 frame, Cooldown: 1.5 s |
| **Phase 17 Experimental** | `model_phase17.py` | Selectable Research Profile | Phase 14 Balanced + animal/biological vocalization suppression filters (spectral flatness & harmonicity gating) |
| **Phase 9 Balanced** | `model_phase9.py` | Frozen Historical Comparator | Legacy acoustic baseline prior to continuous gating enhancements |

All model source code checksums are permanently verified and frozen in [`reports/phase19_baseline_freeze.json`](file:///e:/gunshot/gunshot/reports/phase19_baseline_freeze.json).

---

## 3. Input Audio Pipeline

1. **Standardized Format:** All test streams are ingested as single-channel (mono), 16,000 Hz, 16-bit PCM WAV audio.
2. **Dynamic Range:** Unmodified native sensor dynamic range; peak-normalized only in the event of digital clipping ($> 0\text{ dBFS}$).
3. **Continuous Streaming Simulation:** Audio is ingested continuously using a 1.0-second sliding analysis window with a 0.25-second hop size (4 inferences per second), accurately mirroring live edge-sensor buffer processing.

---

## 4. Ground-Truth Event Matching Logic

In continuous multi-shot acoustic recordings (e.g., rapid bursts and urban reverberations), alerts must be matched to physical gunshot ground truth using unambiguous, causal temporal rules.

### 4.1. Temporal Matching Window
For each ground-truth physical gunshot pulse arriving at timestamp $t_{\text{pulse}}$, an alert fired by the detector at $t_{\text{alert}}$ is matched if:

$$-0.50\text{ s} \le t_{\text{alert}} - t_{\text{pulse}} \le +1.50\text{ s}$$

- **Lead tolerance ($-0.50\text{ s}$):** Accounts for frame boundary buffering and front-edge window overlap in sliding 1.0-second analysis frames.
- **Lag tolerance ($+1.50\text{ s}$):** Accounts for multi-frame confirmation windows (e.g., 2 frames $\times 250\text{ ms} = 500\text{ ms}$) and reverberant acoustic decay.

### 4.2. Event Classification Rules
1. **True Positive (`TP` / `DETECTED`):** The first alert occurring within $[-0.50\text{ s}, +1.50\text{ s}]$ of a ground-truth physical gunshot event.
2. **Missed Event (`FN` / `MISSED`):** A ground-truth gunshot event that receives zero alerts within its valid temporal window.
3. **Duplicate Alert (`DUPLICATE_ALERT`):** Any secondary alert occurring within the valid window of an event that has already been matched to a prior alert in the same stream. Duplicate alerts are logged for temporal auditing but do not penalize precision as independent false alarms.
4. **False Alert (`FP` / `FALSE_ALERT`):** Any alert triggered outside the matching window of all ground-truth gunshot events.

### 4.3. Detection Latency
For every True Positive, empirical detection delay is computed as:

$$\Delta t_{\text{latency}} = t_{\text{alert}} - t_{\text{pulse}}$$

Median latency, 95th-percentile (P95) latency, and maximum latency are calculated across all detected events.

---

## 5. Evaluation Categories

To prevent misleading aggregate claims, evaluation results must be reported separately across four distinct acoustic categories:

- **Category A: Natural Continuous Positive Streams (Primary Target):** 20 unbroken 10.0-second recordings from ShotSpotter Pittsburgh DQV 2018 (50 physical events across 5 independent surveyed intersections).
- **Category B: Pre-Cropped External Positive Clips:** 3 independent clips from 9lash Acoustic Research (3 physical events).
- **Category C: Calibrated Transparent Reference Streams:** 8 semi-synthetic / calibrated streams from Phase 17/18 (33 physical events).
- **Category D: Historically Related Range Recordings:** 42 clips from Mitchell et al. 2015 (42 events).

---

## 6. Statistical Metrics & Confidence Intervals

1. **Event Recall:**
   $$\text{Recall} = \frac{TP}{TP + FN}$$
2. **Event Precision:**
   $$\text{Precision} = \frac{TP}{TP + FP}$$
3. **Event F1 Score:**
   $$\text{F1} = 2 \cdot \frac{\text{Precision} \cdot \text{Recall}}{\text{Precision} + \text{Recall}}$$
4. **Exact Wilson Score Confidence Intervals:** All proportions are bounded by two-sided 95% Wilson score intervals:
   $$w = \frac{\hat{p} + \frac{z^2}{2n} \pm z\sqrt{\frac{\hat{p}(1-\hat{p})}{n} + \frac{z^2}{4n^2}}}{1 + \frac{z^2}{n}}$$
   where $z = 1.95996$.
5. **Session-Level Clustered Variance:** Recall variance across the 5 independent physical firing points (FP1–FP5) is analyzed to verify spatial and environmental robustness.

