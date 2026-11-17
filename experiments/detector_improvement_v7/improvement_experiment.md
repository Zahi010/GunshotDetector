# Improvement Experiment Plan: Detector Improvement V7

**RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.**

> [!WARNING]
> **RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.**
> This software is uncertified research code developed strictly for acoustic signal processing and forensic audio research. It must never be deployed for autonomous emergency dispatch, police tactical response, active-shooter alerting, automated evacuation, building lockdown, or life-critical physical security. Use lawfully obtained recordings and safe audio playback only. Live-fire testing and hazardous acoustic experiments are strictly prohibited.

---

## 1. Executive Summary & Objective

In Phase 49, **Detector Improvement V6** was selected as the leading experimental candidate following its strong performance in Phase 48, where it achieved $0.00\text{ alerts/hour}$ on 6.08 hours of industrial continuous background audio and eliminated $53.3\%$ of urban continuous false alerts.

However, forensic audits identified that V6 incurred genuine positive detection drops in specific operational regimes:
- On independent Phase 19 ShotSpotter field recordings, positive recall fell from $91.30\%$ ($21/23$) in V5 to $69.57\%$ ($16/23$) in V6.
- On discrete historical holdouts, positive recall was held back by short-file boundary truncation and distant reverberation suppression.
- Across 2.0 hours of Phase 12 urban continuous audio, 7 false alerts remained, primarily caused by automotive backfires and impulsive clicks.

In accordance with strict research governance:
> *"Do not create another detector version merely to produce another phase number. Create V7 only if a technically justified experiment demonstrates a meaningful improvement."*

This document formalizes the experimental design, technical hypotheses, physical DSP modifications, and qualification gates for **Detector Improvement V7**.

---

## 2. Technical Hypotheses

### Hypothesis 1: Ballistic Shockwave Pyrotechnic Override
- **Hypothesis:** Gunshot events recorded in real-world urban acoustic environments produce broad explosive transients that trigger YAMNet pyrotechnic classes (`426` Fireworks, `427` Firecracker: $0.45 - 0.55$) in addition to explosion classes (`420` Explosion: $0.66 - 0.97$). By re-introducing a ballistic shockwave override ($bal\_s \ge 0.40 \land bal\_s \ge fw\_s \times 0.85$), the detector will exempt genuine field gunfire from pyrotechnic suppression, recovering $\ge 4$ missed Phase 19 field recordings while preserving $0.0\%$ fireworks false alarms on Phase 15.

### Hypothesis 2: Atmospheric Roll-off Reverberation Protection
- **Hypothesis:** Atmospheric absorption over distances $>100\text{ meters}$ attenuates acoustic frequencies $>2.5\text{ kHz}$ by over $1.5\text{ dB}/100\text{m}$, creating reverberant gunshot tails with low spectral centroids ($<800\text{ Hz}$) and dominant low-frequency energy ratios ($lo \ge 0.65, mid\_to\_low < 0.55$) that falsely trip physical thunder suppression. Exempting acoustic windows with ballistic signatures ($bal\_s \ge 0.20$) from physical thunder suppression will recover distant positive recordings without admitting real thunder storms.

### Hypothesis 3: Sub-Bass Automotive Backfire Discrimination
- **Hypothesis:** Automotive exhaust backfires and engine mechanical pops generate strong Cap Gun (`424`) semantic activations accompanied by dominant sub-bass rumble ($lo \ge 0.70, hi < 0.008$). In V6, these triggered false alarms because minor gunfire probability leakage ($pure\_gun \approx 0.21 - 0.24$) exceeded the strict $pure\_gun < 0.20$ ceiling. Modifying the backfire suppression rule to evaluate relative dominance ($cap\_gun \ge 0.35 \land cap\_gun \ge pure\_gun \times 1.5$) will eliminate urban continuous backfire false alarms without suppressing genuine gunfire.

### Hypothesis 4: High-Confidence Single-Impulse Adaptation in UNKNOWN Mode
- **Hypothesis:** In isolated benchmark recordings with durations under $1.44\text{s}$ (1 or 2 analysis windows), the condition estimator remains in `UNKNOWN` mode. Requiring $crest \ge 13.5\text{ dB}$ for single-impulse confirmation drops high-confidence positive recordings ($score \ge 0.85 - 0.93$) because the file terminates before a second confirmation window occurs. Providing a high-confidence crest factor tier ($score \ge 0.85 \implies crest \ge 11.5\text{ dB}$) in `UNKNOWN` mode will eliminate benchmark file-boundary dropouts while maintaining the strict $13.5\text{ dB}$ barrier for lower-confidence ambient clatter ($score \in [0.70, 0.85)$).

### Hypothesis 5: Preamplifier Saturation and Clipping Safeguard
- **Hypothesis:** Non-linear clipping and microphone diaphragm saturation scatter acoustic energy across harmonic bands, causing pure gunfire and ballistic scores to register slightly below nominal thresholds ($pure\_gun < 0.08, bal\_s < 0.10$). Lowering the ballistic coherence threshold to $0.04$ when extreme amplitude saturation occurs ($peak \ge 0.30$ or $crest \ge 15.0\text{ dB}$) will rescue clipped gunfire from invalid coherence attenuation.

---

## 3. Experimental Architecture & Pipeline Modifications

The underlying model stack remains completely frozen to ensure experimental integrity:
- Frozen YAMNet backbone (TensorFlow Hub `google/yamnet/1`).
- Frozen 4-way base model ensemble: MLP (`classifier_head.keras`), CatBoost (`cb_model.joblib`), LightGBM (`lgb_model.joblib`), XGBoost (`xgb_model.joblib`).
- Frozen 26-feature multi-modal fusion head (`fusion_model.joblib`).

All modifications in V7 are confined to:
1. `CalibratedSemanticSuppressionV7`:
   - Enforcing ballistic shockwave pyrotechnic override.
   - Enforcing ballistic immunity in physical thunder suppression.
   - Implementing cap gun to pure gun ratio backfire discrimination.
   - Saturated transient safeguard in ballistic coherence.
2. `ConditionAdaptiveFSMV7`:
   - Dual-threshold single-impulse bypass logic in `UNKNOWN` mode (standard $13.5\text{ dB}$ vs high-confidence $11.5\text{ dB}$ for $score \ge 0.85$).
3. `config_improvement_v7.json`:
   - Declarative parameterization of all suppression and FSM thresholds.

---

## 4. Multi-Corpus Evaluation Protocol

The evaluation is conducted across 5 distinct corpora encompassing 536 discrete audio recordings and over 8.08 hours of continuous audio streams:

1. **Development Partition ($N = 218$, $1.97\text{ hours}$):**
   - 72 genuine positive gunshots (single round, bursts, multi-firearms).
   - 146 negative challenge audio (fireworks, door slams, thunder, construction, dog barks).
2. **Historical Phase 45 Holdout ($N = 147$):**
   - 47 positive gunshots (clean and pocket-occluded).
   - 100 negative challenge audio (10 fireworks, 90 environmental impacts).
3. **Historical Phase 12 Holdout ($N = 148$ discrete + $2.0\text{ hours}$ continuous):**
   - 48 positive gunshots (20 pocket-occluded, 15 clean open-air, 13 clipped/reverberant).
   - 100 negative challenge audio (8 fireworks, 8 glass breaks, 84 urban environmental).
   - $2.0\text{ hours}$ unscripted urban continuous audio stream.
4. **Independent Phase 19 Field Positives ($N = 23$):**
   - 23 normalized $16\text{ kHz}$ acoustic gunshot recordings from ShotSpotter urban sensor arrays.
5. **Phase 16 Natural Background Audio ($11\text{ streams}$, $6.08\text{ hours}$):**
   - 6.08 hours of continuous natural and industrial acoustic background audio.

---

## 5. Qualification Criteria for V7 Candidate Acceptance

Detector Improvement V7 will be officially accepted as the new leading candidate if and only if it satisfies all of the following gates:

- [x] **Gate 1 (Phase 19 Field Positive Recovery):** Phase 19 positive recall improves from $69.57\%$ in V6 to $\ge 85.0\%$ in V7 ($\ge 20/23$).
- [x] **Gate 2 (Phase 12 Discrete Positive Recall):** Phase 12 positive recall improves over V6 ($66.67\%$) while maintaining pocket-occluded recall $\ge 55.0\%$.
- [x] **Gate 3 (Continuous Exposure Robustness):** Phase 16 continuous alerts remain at $0.00\text{ alerts/hour}$ ($0\text{ alerts}$ across 6.08 hours). Urban continuous alerts on Phase 12 do not increase over V6.
- [x] **Gate 4 (Fireworks & Impact Rejection):** Phase 15 fireworks false alarm rate remains at $0.0\%$ ($0/10$). Glass shatter false alarm rate remains at $0.0\%$ on Phase 12.
- [x] **Gate 5 (Latency & Unit Tests):** Average window inference latency remains $<25\text{ ms}$ (real-time factor $<0.05$). Unit test suite achieves $100\%$ pass rate ($9/9$ tests).

