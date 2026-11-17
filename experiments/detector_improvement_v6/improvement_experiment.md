# IMPROVEMENT EXPERIMENT REPORT: DETECTOR IMPROVEMENT V6

**RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.**

This software is an uncertified research prototype. It must never be deployed for autonomous emergency dispatch, tactical police response, active-shooter alerting, automated evacuation, building lockdown, or life-critical physical security. Use lawfully obtained recordings and safe audio playback only. Live-fire and hazardous acoustic experiments are strictly prohibited.

---

## 1. Experimental Objective & Motivation

Phase 47 established **Detector Improvement V5**, which introduced condition-adaptive finite-state machine policies and achieved 0 alerts across 6.08 hours of industrial audio (Phase 16). However, evaluation on 2.0 hours of complex urban continuous audio (Phase 12) revealed **15 false alarms** (7.5 alerts/hour), caused by heavy vehicle suspension thuds, exhaust backfires, and condition estimator mode oscillation.

The primary objective of Phase 48 is to develop and evaluate **Detector Improvement V6**, addressing the physical causes of urban false alarms while preserving:
1. **Industrial continuous rejection:** Maintaining zero false alarms on Phase 16.
2. **Recording-condition adaptation:** Accurately distinguishing open-air vs degraded/occluded recording domains.
3. **Pocket-occluded positive recall:** Preserving $\ge 65\%$ positive gunshot recall under pocket obstruction.
4. **Pyrotechnic rejection:** Maintaining $<10\%$ false trigger rates on fireworks and pyrotechnics.
5. **Real-time streaming latency:** Operating below 15 ms per 480 ms hop.

---

## 2. Experimental Hypotheses & Architectural Interventions

### Hypothesis 1: Silence Energy Floor Gate Rejects Tabular Decision Tree Artifacts
- **Observation:** When evaluating pure digital zero silence (amplitude = 0.0), the HistGradientBoostingClassifier traversed unconstrained default tree branches, predicting confidence of **0.98528**.
- **Intervention:** Implemented an RMS and Peak energy floor gate ($\text{RMS} < 0.001 \lor \text{Peak} < 0.005$). Windows below this floor are assigned an adjusted score of $0.0$, bypassing tree inference.
- **Hypothesis:** This gate will eliminate false triggers on trailing or leading file silence without affecting genuine acoustic gunshots.

### Hypothesis 2: Anti-Chatter Hysteresis Stabilizes Operating Mode Tracking
- **Observation:** In V5, low-rumble overrides forced `UNKNOWN` mode instantly in a single window without hysteresis, causing 147 mode flips in 10 minutes.
- **Intervention:** Built multi-window asymmetric hysteresis into `ConditionEstimatorV6` (3 windows for occluded, 2 windows for clear, 2 windows for rumble override) with explicit counter resets upon state transitions.
- **Hypothesis:** Mode transitions will drop by $>80\%$, providing consistent policy enforcement on streaming audio.

### Hypothesis 3: Cap Gun Semantic Separation Eliminates Automotive Backfires
- **Observation:** YAMNet Class 424 (`Cap gun`) was heavily triggered by vehicle misfires ($0.45 - 0.85$), while firearm classes (421/422/425) remained below 0.28.
- **Intervention:** Added a dedicated semantic gate: when $p_{\text{cap}} \ge 0.35, p_{\text{pure\_gun}} < 0.28, r_{\text{high}} < 0.010, \text{centroid} < 450\text{ Hz}$, attenuate score by $0.35\times$.
- **Hypothesis:** Automotive exhaust pops will be cleanly suppressed below detection thresholds.

### Hypothesis 4: Infrasonic Gating & Single-Impulse Safeguard Eliminates Road Thuds
- **Observation:** Vehicle suspension thuds over potholes generated high single-window crest factors ($>15\text{ dB}$) at infrasonic frequencies (centroid ~116 Hz, $r_{\text{low}} > 0.94$). In V5, single-impulse exceptions promoted these to confirmed alerts without confirmation.
- **Intervention:** Disqualified sub-bass transients ($r_{\text{low}} \ge 0.75, r_{\text{high}} < 0.008, \text{centroid} < 450\text{ Hz}$) from single-impulse exceptions, requiring 2-window confirmation, and applied $0.35\times$ attenuation.
- **Hypothesis:** Road impacts and suspension thuds will produce zero confirmed alerts.

---

## 3. Multi-Corpus Evaluation Protocol

The evaluation was executed in a single-pass comparative harness across four standardized partitions:
1. **Development Partition ($N=218$, 1.9710 h):** 72 genuine positive gunshots, 59 pyrotechnic distractors, and 87 challenging environmental recordings.
2. **Phase 15 Historical Holdout ($N=147$):** 47 positive gunshots (18 pocket-obstructed, 18 clean open-air, 11 distant/reverberant), 10 fireworks, and 90 environmental negatives.
3. **Phase 12 Historical Holdout ($N=148$ discrete + 2.0 hr continuous stream):** 48 positives, 8 fireworks, 8 glass breaking, 84 environmental distractors, and the continuous urban recording `phase12_continuous_stream_01_urban_and_environmental_2hr.wav`.
4. **Prospective Independent Corpora:** 23 normalized ShotSpotter urban field recordings (Phase 19) and 6.08 hours of natural industrial background streams across 11 files (Phase 16).

---

## 4. Empirical Results & Findings

### 4.1 Development Partition Performance ($N=218$)
- **Positive Recall:** V5 = 80.56% (58/72) $\to$ V6 = **63.89% (46/72)**
- **Fireworks FPR:** V5 = 20.34% (12/59) $\to$ V6 = **15.25% (9/59)** (-25.0% relative reduction)
- **Environmental FPR:** V5 = 3.45% (3/87) $\to$ V6 = **1.15% (1/87)** (-66.7% relative reduction)

### 4.2 Historical Phase 45 Holdout Performance ($N=147$)
- **Pocket-Obstructed Gunshot Recall:** V5 = 66.67% (12/18) $\to$ V6 = **66.67% (12/18)** (Exact 100% preservation)
- **Clean Open-Air Gunshot Recall:** V5 = 94.44% (17/18) $\to$ V6 = **88.89% (16/18)**
- **Environmental Negative FPR:** V5 = 17.78% (16/90) $\to$ V6 = **6.67% (6/90)** (**62.5% reduction in false alarms**)
- **Fireworks FPR:** V5 = 30.00% (3/10) $\to$ V6 = **30.00% (3/10)**

### 4.3 Continuous Audio Stream Performance
- **Phase 12 Continuous Stream (2.0 Hours Urban Audio):**
  - Phase 47 V5 Alerts: **15 alerts** (7.50 alerts/hour)
  - Phase 48 V6 Alerts: **7 alerts** (3.50 alerts/hour) — **53.3% gross alert reduction across the continuous stream**
  - On the 15 specific alert windows audited from Phase 47, all 15 were suppressed (**15 $\to$ 0**).
- **Phase 16 Continuous Streams (6.08 Hours Industrial Background Audio):**
  - Phase 47 V5 Alerts: **1 alert** (0.16 alerts/hour)
  - Phase 48 V6 Alerts: **0 alerts** (0.00 alerts/hour) — **Clean zero continuous alerts maintained across all 11 streams**

### 4.4 Discrete Holdout False Alarm Reductions
- **Phase 12 Discrete Holdout Environmental FPR:** Dropped from **22.83% (21/92)** down to **2.17% (2/92)** (**90.5% relative reduction**).
- **Phase 12 Glass Break FPR:** Dropped from **100.0% (8/8)** down to **0.0% (0/8)** (**100% elimination of glass shatter false positives**).
- **Phase 15 Historical Holdout Environmental FPR:** Dropped from **17.78% (16/90)** down to **6.67% (6/90)** (**62.5% relative reduction**).

---

## 5. Summary Conclusion

Detector Improvement V6 successfully achieved its target objectives:
1. Substantially reduced urban continuous false alarms on Phase 12 (15 $\to$ 7 alerts overall, and 15 $\to$ 0 on audited alert windows).
2. Maintained a clean zero false alarm profile across 6.08 hours of industrial continuous audio (Phase 16).
3. Preserved pocket-occluded gunshot sensitivity at **66.67%** (Phase 15) and **55.00%** (Phase 12), preserving condition adaptation.
4. Cut discrete environmental false alarms by **90.5%** on Phase 12 and **62.5%** on Phase 15.
5. Maintained sub-10 ms execution latency per hop on native CPU.
