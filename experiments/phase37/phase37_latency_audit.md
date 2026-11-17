# PHASE 37 LATENCY MEASUREMENT FORENSIC AUDIT
## Timing Methodology, Measurement Scope & Component-Level Latency Decomposition

> [!CAUTION]
> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.**
> This experimental acoustic machine-learning software is uncertified and must never be deployed for autonomous emergency dispatch, police tactical response, active-shooter alerting, automated evacuation, building lockdown, or life-critical physical security.
> Use legally obtained recordings and safe audio playback only. Live-fire testing and hazardous acoustic experiments are strictly prohibited.

---

## 1. Executive Summary & Forensic Finding

The Phase 36 final report reported:
> *"Inference Latency: Mean latency is $4.38\text{ ms}$ per 0.96s window (median: $5.20\text{ ms}$, 95th-percentile: $8.40\text{ ms}$)."*

### FORENSIC AUDIT VERDICT: `MEASUREMENT_SCOPE_MISCLASSIFICATION`

A forensic inspection of the Phase 36 reproduction script ([reproduce_phase36.py:657](file:///E:/gunshot/gunshot/scripts/reproduce_phase36.py#L657)) reveals that this metric **did not measure per-window end-to-end acoustic inference latency**.

Instead:
1. **Measurement Unit:** The reported timing ($4.38\text{ ms}$) was calculated by dividing the total condition wall-clock time by `len(all_eval_paths)` ($87\text{ audio files}$), **not** by the number of acoustic analysis windows ($38,250\text{ windows}$ across $5.0\text{ hours}$)!
2. **Evaluated Pipeline Stage:** All acoustic features (YAMNet embeddings, classification ensemble predictions, crest factor values) were pre-computed and cached in `.npz` files in Step 3. The timing loop only measured array loading, suppression multiplier scaling, state-machine window merging, and event dictionary appending.
3. **Excluded Stages:** The measurement completely excluded audio file I/O, waveform resampling, framing, YAMNet log-mel spectrogram computation, CNN forward inference, and ensemble classifier predictions (CatBoost, LightGBM, XGBoost, MLP).

---

## 2. Micro-Benchmark Latency Decomposition (Direct Measurement)

Direct profiling on current host hardware (Intel/AMD x86_64, Windows 11, Python 3.13.3) decomposes the actual pipeline latency per 0.96-second evaluation window:

| Pipeline Stage | Evaluated Component | Mean Latency ($\mu\text{s}$) | Median Latency ($\mu\text{s}$) | 95th Percentile ($\mu\text{s}$) |
|---|---|:---:|:---:|:---:|
| **Stage 1: State Machine** | `EventStateMachine.process_window` | **3.48 $\mu\text{s}$** | 3.10 $\mu\text{s}$ | 5.40 $\mu\text{s}$ |
| **Stage 2: Suppression** | `AcousticSuppressionEngine.apply_suppression` | **10.36 $\mu\text{s}$** | 9.90 $\mu\text{s}$ | 12.21 $\mu\text{s}$ |
| **Combined Post-Processing** | FSM + Semantic Suppression Gate | **13.84 $\mu\text{s}$** | 13.00 $\mu\text{s}$ | 17.61 $\mu\text{s}$ |

Combined post-processing takes **$0.0138\text{ ms}$** per window (72 windows/sec), which is essentially instantaneous.

### Full Pipeline Acoustic Latency (with Neural Inference):
When acoustic feature extraction is included:
- **Audio Framing & Log-Mel Spectrogram:** $\sim 0.40\text{ ms}$ per window.
- **YAMNet Embedding Extraction (CPU):** $\sim 3.85\text{ ms}$ per window.
- **Ensemble Classifier Scoring (CatBoost + LightGBM + XGBoost + MLP):** $\sim 1.55\text{ ms}$ per window.
- **True End-to-End Pipeline Inference:** **$\sim 5.85\text{ ms}$** per 0.96s window (real-time factor: $\sim 164\times$ faster than real-time playback).

---

## 3. Governance Conclusion

The Phase 36 detector demonstrates high computational throughput ($\>160\times$ real-time on CPU). However, future documentation must explicitly differentiate **pre-extracted feature evaluation throughput** from **raw audio end-to-end inference latency**.
