# Phase 55 — Gunshot Detection Architecture Recommendation

**MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.**

*This uncertified research prototype must never be deployed for autonomous emergency dispatch, tactical police response, active-shooter alerting, automated evacuation, building lockdown, or life-critical physical security.*

---

## 1. Executive Summary

Phase 54 qualification testing revealed that handcrafted scalar heuristics in Detector Improvement V10 suffered an unacceptable **22.12% false-positive rate on challenge negatives**, driven primarily by pyrotechnics (73.33% FPR), balloon bursts (57.14% FPR), and heavy mechanical impacts (33.33% FPR). 

At the same time, Phase 55 failure audits proved that:
1. Scalar threshold rules cannot separate multi-dimensional acoustic distributions without severe false-negative or false-positive regressions.
2. Handcrafted "rescue rules" (such as Clause 4 ground-blast bypass) create dangerous backdoors that unsuppress true negatives.
3. Offline machine learning experiments demonstrate that a **Learned Rejection Classifier** operating over multi-dimensional acoustic and semantic descriptors reduces challenge negative false alarms by over 75% compared to heuristic rules while adding less than 0.05 ms of latency.

This document formally details the architectural recommendation for subsequent detector generations.

---

## 2. Evaluation of Candidate Architectural Patterns

| Architectural Pattern | Mechanism | Strengths | Weaknesses | Suitability Verdict |
| :--- | :--- | :--- | :--- | :---: |
| **Pattern 1: Pre-Classifier Gating** | Hard thresholding on raw DSP features (crest, energy, spectral tilt) prior to neural inference | Zero neural inference cost on rejected frames; extremely fast. | Coarse thresholds discard muffled, distant, or pocket-occluded gunshots; impossible to separate fireworks from gunshots on raw DSP alone. | **Unsuitable as sole rejection mechanism** |
| **Pattern 2: Post-Classifier Rejection** | Base neural ensemble generates candidate score; dedicated learned rejection model filters false positives | Decoupled modular training; full access to deep semantic embeddings, acoustic metrics, and temporal envelopes; zero retraining of base ensemble required. | Runs inference on all candidate windows; requires high-quality negative training distributions. | **RECOMMENDED** |
| **Pattern 3: Joint Multi-Task Deep Backbone** | Single neural network jointly trained with multi-head loss for gunshot detection and challenge class rejection | End-to-end representation sharing; joint feature space optimization. | High risk of catastrophic forgetting of rare gunshot signatures; requires massive unified retraining whenever new nuisance noise classes emerge. | **High Complexity / Fragile** |

---

## 3. Recommended Pipeline: Cascaded Two-Stage Architecture

The recommended production architecture consists of a **Cascaded Two-Stage Inference Engine with Learned Post-Classification Gating**:

```
[Raw Audio Stream: 16 kHz Mono]
               │
               ▼
┌──────────────────────────────┐
│ Stage 0: Transient Trigger   │  Energy / Crest factor check (Crest >= 10 dB OR Peak >= 0.15)
└──────────────┬───────────────┘
               │ (Pass)
               ▼
┌──────────────────────────────┐
│ Stage 1: Acoustic-Semantic   │  YAMNet (1024-d) + V8 Acoustic Features (10-d)
│          Fusion Ensemble     │  Gradient Boosted / MLP Consensus (Outputs Raw Probability P_base)
└──────────────┬───────────────┘
               │ (If P_base >= 0.60)
               ▼
┌──────────────────────────────┐
│ Stage 2: Learned Rejection   │  GBDT Rejection Head on 15 Multidimensional Features
│          Classifier (ML)     │  (Centroid, Flux, Rise Time, Decay Half-life, YAMNet Logits)
└──────────────┬───────────────┘  Outputs Adjusted Score: P_adj = P_base * (1.0 - P_reject)
               │ (If P_adj >= Threshold)
               ▼
┌──────────────────────────────┐
│ Stage 3: Hysteresis FSM      │  2-Window Temporal Confirmation + 2.5s Refractory Cooldown
└──────────────┬───────────────┘
               │ (Confirmed)
               ▼
      [DISPATCH ALERT]
```

### Stage Details

1. **Stage 0 — Lightweight Transient Gating (DSP):**
   - Evaluates fast time-domain metrics (crest factor and peak amplitude).
   - If crest factor $< 10.0\text{ dB}$ and peak amplitude $< 0.15$, the frame is immediately classified as ambient noise, bypassing YAMNet and ensemble computation. This saves over 90% of CPU cycles during ambient streaming.

2. **Stage 1 — Deep Acoustic-Semantic Fusion:**
   - Computes YAMNet 1024-dimensional transfer learning embeddings and V8 acoustic features (centroid, rolloff, band energy ratios, spectral flatness).
   - Generates calibrated probability $P_{\text{base}}$ using the frozen multi-model ensemble (MLP + CatBoost + LightGBM + XGBoost).

3. **Stage 2 — Learned Rejection Classifier (Post-Gating):**
   - Active only when $P_{\text{base}} \ge 0.60$.
   - A trained Gradient Boosted Decision Tree (GBDT) evaluates 15 multi-dimensional features:
     - `crest_factor_db`, `spectral_centroid_hz`, `spectral_flatness`, `spectral_rolloff_hz`
     - Energy ratios: `high_ratio`, `mid_ratio`, `low_ratio`, `mid_to_low_ratio`
     - Temporal envelopes: `rise_time_ms` (10% to 90% peak onset), `decay_half_life_ms` (peak to 50% decay)
     - Semantic activations: `pure_gun_score`, `glass_score`, `base_raw_score`
   - Yields rejection probability $P_{\text{reject}} \in [0, 1]$.
   - Computes adjusted detection score:
     $$P_{\text{adj}} = P_{\text{base}} \cdot (1.0 - P_{\text{reject}})$$
   - Completely eliminates handcrafted `if-else` scalar cutoffs and Clause 4 bypass rules.

4. **Stage 3 — Temporal Finite State Machine (FSM):**
   - Manages state transitions across consecutive windows (`IDLE` $\rightarrow$ `SUSPECTED` $\rightarrow$ `CONFIRMED` $\rightarrow$ `REFRACTORY_COOLDOWN`).
   - Requires two consecutive elevated windows or a single ultra-confident ballistic event ($P_{\text{adj}} \ge 0.88$ with ballistic crest $> 16\text{ dB}$) to confirm.
   - Enforces a 2.5-second refractory cooldown period to prevent alert chatter.

---

## 4. Latency and Compute Budget

The cascaded design operates comfortably within the 480 ms real-time streaming constraint:

| Pipeline Stage | Implementation | Mean Execution Latency | Worst-Case Latency | Latency Budget (%) |
| :--- | :--- | :---: | :---: | :---: |
| **Stage 0: Transient Gate** | Vectorized NumPy | 0.02 ms | 0.05 ms | 0.01% |
| **Stage 1: YAMNet Embedding** | TensorFlow CPU (ONEDNN) | 11.20 ms | 18.50 ms | 2.33% |
| **Stage 1: Fusion Ensemble** | Scikit-Learn / LightGBM | 0.35 ms | 0.70 ms | 0.07% |
| **Stage 2: Learned Rejection** | Scikit-Learn GBDT (100 trees) | 0.04 ms | 0.08 ms | 0.01% |
| **Stage 3: FSM State Machine** | Pure Python Logic | 0.01 ms | 0.02 ms | 0.002% |
| **Total Pipeline Latency** | Full End-to-End | **11.62 ms** | **19.35 ms** | **2.42%** |

*Margin of Safety: 480 ms window deadline vs 11.62 ms mean latency provides a **41x real-time safety margin**.*

---

## 5. Summary Recommendation

1. **Retire Handcrafted Heuristics:** Formally deprecate scalar suppression rules for balloon bursts, fireworks, and door slams.
2. **Adopt Two-Stage Cascaded Post-Classification:** Retain the frozen base fusion model and append the learned rejection classifier head.
3. **Formal Decision:** Proceed to learned rejection model development using contributor-isolated training partitions.

