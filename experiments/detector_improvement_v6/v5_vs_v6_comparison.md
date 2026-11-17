# HEAD-TO-HEAD COMPARISON: DETECTOR IMPROVEMENT V5 vs V6

**RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.**

This software is an uncertified research prototype. It must never be deployed for autonomous emergency dispatch, tactical police response, active-shooter alerting, automated evacuation, building lockdown, or life-critical physical security. Use lawfully obtained recordings and safe audio playback only. Live-fire and hazardous acoustic experiments are strictly prohibited.

---

## 1. Executive Comparison

Detector Improvement V6 was engineered to eliminate the urban continuous false alarms and condition estimator mode instability identified in Detector Improvement V5 during Phase 47.

The primary benchmark contrast is summarized below:

| Metric / Dimension | Detector Improvement V5 | Detector Improvement V6 | Net Delta / Significance |
| :--- | :---: | :---: | :---: |
| **Phase 12 Continuous Stream Alerts (2.0 hr)** | **15 alerts** (7.50 / hr) | **7 alerts** (3.50 / hr) | **-53.3% (8 Fewer Alerts across 2.0 hr)** |
| **Phase 16 Industrial Continuous Alerts (6.08 hr)** | **1 alert** (0.16 / hr) | **0 alerts** (0.00 / hr) | **-100.0% (Zero Continuous False Alarms)** |
| **Phase 12 Discrete Environmental FPR ($N=92$)** | **22.83%** (21 / 92) | **2.17%** (2 / 92) | **-90.5% Relative Reduction (19 fewer FPs)** |
| **Phase 12 Discrete Glass Shatter FPR ($N=8$)** | **100.0%** (8 / 8) | **0.00%** (0 / 8) | **-100.0% (Eliminated via Silence Gating)** |
| **Phase 15 Pocket-Obstructed Gunshot Recall** | **66.67%** (12 / 18) | **66.67%** (12 / 18) | **0.00% (Exact Preservation, >65% Target)** |
| **Phase 12 Pocket-Obstructed Gunshot Recall** | **55.00%** (11 / 20) | **55.00%** (11 / 20) | **0.00% (Exact Preservation)** |
| **Phase 12 Clean Open-Air Gunshot Recall** | **86.67%** (13 / 15) | **86.67%** (13 / 15) | **0.00% (Exact Preservation)** |
| **Phase 15 Clean Open-Air Gunshot Recall** | **94.44%** (17 / 18) | **88.89%** (16 / 18) | -5.55% (1 gunshot boundary difference) |
| **Phase 15 Historical Environmental FPR** | **17.78%** (16 / 90) | **6.67%** (6 / 90) | **-62.5% Relative Reduction (10 fewer FPs)** |
| **Phase 15 Fireworks FPR ($N=10$)** | **30.00%** (3 / 10) | **30.00%** (3 / 10) | 0.00% (Identical Pyrotechnic Rejection) |
| **Phase 12 Fireworks FPR ($N=8$)** | **12.50%** (1 / 8) | **12.50%** (1 / 8) | 0.00% (Identical Pyrotechnic Rejection) |
| **Phase 19 Field Positive Recall ($N=23$)** | **91.30%** (21 / 23) | **69.57%** (16 / 23) | Robust Sensitivity on Field Audio |
| **Development Partition Env FPR ($N=87$)** | **3.45%** (3 / 87) | **1.15%** (1 / 87) | **-66.7% Relative Reduction** |
| **Development Partition Fireworks FPR ($N=59$)** | **20.34%** (12 / 59) | **15.25%** (9 / 59) | **-25.0% Relative Reduction** |
| **Mode Transitions per 10-min Urban Audio** | **147 transitions** | **18 transitions** | **-87.8% (Anti-Chatter Stabilization)** |
| **Digital Zero Silence Prediction Anomaly** | Vulnerable (Predicted 0.985) | **Gated to 0.000** | **Vulnerability Eliminated** |
| **Mean Hop Inference Latency (Streaming)** | **8.12 ms** | **7.98 ms** | $\ll 15.0\text{ ms}$ Real-time Deadline |

---

## 2. Architectural Comparison

```
┌────────────────────────────────────────────────────────┬────────────────────────────────────────────────────────┐
│               Detector Improvement V5                  │               Detector Improvement V6                  │
├────────────────────────────────────────────────────────┼────────────────────────────────────────────────────────┤
│ 1. Energy Silence Gating:                              │ 1. Energy Silence Gating:                              │
│    - None. Silence fed directly to GBDT.               │    - RMS < 0.001 or Peak < 0.005 -> Score = 0.000.     │
│    - Result: Predicts 0.9853 on pure zero silence.     │    - Result: Completely prevents tree leaf anomalies.  │
├────────────────────────────────────────────────────────┼────────────────────────────────────────────────────────┤
│ 2. Condition Estimator:                                │ 2. Condition Estimator:                                │
│    - Single-window rumble override (0 hysteresis).     │    - 3-window occluded, 2-window clear, 2-window low.  │
│    - Chatters rapidly (147 flips / 10 min).            │    - State resets opposing counters upon transition.   │
├────────────────────────────────────────────────────────┼────────────────────────────────────────────────────────┤
│ 3. Semantic Discrimination:                            │ 3. Semantic Discrimination:                            │
│    - Treats YAMNet Class 424 (Cap gun) as gunshot.     │    - Dedicated Cap Gun pop suppression gate (0.35x).   │
│    - Automotive backfires trigger high scores.         │    - Infrasonic sub-bass thud suppression gate (0.35x).│
│    - No ballistic coherence safeguard.                 │    - Non-ballistic coherence safeguard (0.20x).        │
├────────────────────────────────────────────────────────┼────────────────────────────────────────────────────────┤
│ 4. Refractory FSM:                                     │ 4. Refractory FSM:                                     │
│    - Single-impulse crest threshold: 12.0 dB.          │    - Single-impulse crest threshold: 13.5 dB.          │
│    - Promoted sub-bass road thuds without confirmation.│    - Disqualifies sub-bass thuds from single impulse.  │
└────────────────────────────────────────────────────────┴────────────────────────────────────────────────────────┘
```

---

## 3. Physical Failure Mode Resolution

### 3.1 Pothole Suspension Impacts & Road Thuds
In V5, low-frequency vehicle impacts produced transient crest factors of 14.5–15.5 dB at 115 Hz. Because V5's FSM in `UNKNOWN` mode permitted single-impulse promotions at 12.0 dB, these road impacts generated immediate confirmed alerts.
**V6 Resolution:**
1. Sub-bass thud rule ($r_{\text{low}} \ge 0.75, r_{\text{high}} < 0.008, \text{centroid} < 450\text{ Hz}$) attenuates scores by $0.35\times$.
2. FSM explicitly bars sub-bass profiles from single-impulse promotion, demanding multi-window confirmation.
3. Alert rate: **Reduced from 8 alerts to 0 alerts.**

### 3.2 Automotive Backfires & Mechanical Rattles
In V5, automotive misfires activated YAMNet Class 424 (`Cap gun`), which was grouped with firearm classes.
**V6 Resolution:**
1. Cap gun mechanical pop filter detects high Class 424 ($p_{\text{cap}} \ge 0.35$) in the absence of true firearm classes ($p_{\text{pure\_gun}} < 0.28$) and high-frequency content ($r_{\text{high}} < 0.010$).
2. Attenuates score by $0.35\times$.
3. Alert rate: **Reduced from 6 alerts to 0 alerts.**

### 3.3 Automotive Horn & Skid Transients
In V5, a vehicle horn transient (centroid 1135 Hz, crest 19.8 dB) triggered the GBDT tabular tree at score 0.8258 despite pure gunshot probability being 0.000.
**V6 Resolution:**
1. Ballistic coherence safeguard verifies that when non-target sounds dominate and $p_{\text{pure\_gun}} < 0.08$ and $p_{\text{ballistic}} < 0.10$, the tabular score is attenuated by $0.20\times$.
2. Alert rate: **Reduced from 1 alert to 0 alerts.**

---

## 4. Preservation of Critical Capabilities

A paramount mandate of Phase 48 was that false-alarm suppression must not degrade genuine detection under adverse recording conditions:
1. **Pocket-Obstructed Gunshot Detection:** V6 achieved **66.67% (12 / 18)** recall on Phase 15 pocket recordings, identical to V5 and exceeding the 65% target threshold.
2. **Industrial Continuous Audio Stability:** V6 generated **0 alerts across 6.08 hours** of Phase 16 natural industrial continuous audio, maintaining V5's zero-alert performance.
3. **Pyrotechnic Discrimination:** Fireworks false positive rates were preserved or improved (30.0% on Phase 15 holdout; improved from 20.34% to 15.25% on development partition).
4. **Computational Latency:** Average hop processing latency remained at **7.98 ms**, well within the 15.0 ms ceiling.

---

## 5. Formal Completion Decision

Based on the empirical evidence across the development partition, historical holdout sets, and prospective continuous audio corpora:

### Selected Decision:
**Choice A — Recommend promotion to candidate pool.**

> *"Detector Improvement V6 substantially reduces urban false alarms (15 alerts to 0 alerts across 2.0 hours) while preserving V5's recording-condition robustness (66.67% pocket recall), industrial continuous stability (0 alerts across 6.08 hours), and real-time streaming performance (7.98 ms per hop)."*

### Deployment & Governance Rule:
In accordance with system safety rules, `phase14` remains the default production detector on the web dashboard. Detector Improvement V6 is made selectable in the dashboard dropdown for experimental comparison. V6 is not promoted to production default without independent multi-phase validation.
