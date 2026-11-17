# PHASE 47 FORENSIC FAILURE ANALYSIS & CONDITION ESTIMATION INVESTIGATION

**RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.**

> [!CAUTION]
> **MANDATORY SAFETY DESIGNATION**
> This software is an uncertified acoustic research demonstration prototype. It must never be deployed for autonomous emergency dispatch, tactical police response, active-shooter alerting, automated evacuation, building lockdown, or life-critical physical security. Use lawfully obtained recordings and safe audio playback only. Live-fire and hazardous acoustic experiments are strictly prohibited.

---

## 1. Executive Summary

Phase 46 developed **Detector Improvement V4**, which successfully solved the acute pocket-occlusion recall collapse of V3 by restoring positive recall to **79.17%** on the Phase 12 holdout and **85.11%** on the Phase 15 holdout. However, this sensitivity recovery came at the cost of elevated environmental false alarms:
1. **Continuous Urban False Alarms:** Continuous alerts surged to **21 alerts across 2 hours (10.5 alerts/hour)** on the Phase 12 continuous urban stream (compared to 2 alerts for V3). On the Phase 16 continuous benchmark, V4 produced **15 false alarms** in a single 30-minute industrial exhaust stream (`phase16_industrial_exhaust_ventilation_30min.wav`).
2. **Glass Breaking False Triggers:** Despite adding glass shatter suppression logic in V4, glass breaking recordings continued to trigger false alarms. Forensic auditing revealed an algorithmic deadlock: sharp glass shattering activated YAMNet's explosive crack classes (classes 434 and 436), driving ballistic confidence ($p_{\text{bal}} \approx 0.50$) and causing the `bal_s < 0.20` safeguard to completely block suppression.
3. **Atmospheric Thunder & Low-Frequency Transients:** Distant thunder and heavy vehicle rumbles bypassed semantic suppression due to low YAMNet raw confidence ($p_{\text{thunder}} < 0.25$), triggering false impulses when combined with low-frequency rumble peaks.

This forensic analysis investigates the acoustic, mathematical, and state-machine mechanisms behind these failures and documents the empirical boundaries of acoustic condition estimation.

---

## 2. Forensic Investigation of Phase 46 Environmental False Alarms

### 2.1 The Continuous Industrial & Urban Stream Breakdown

In continuous background monitoring, an effective detector must maintain near-zero false alarms during sustained non-ballistic acoustic exposure. When V4 was evaluated on continuous audio, two distinct failure modes emerged:

```
Continuous Audio Stream False Alarm Audit (Phase 46 V4 vs. Prior Versions):

Stream Corpus               Duration    V2 Alerts    V3 Alerts    V4 Alerts    Primary Failure Acoustic Mechanism
-----------------------------------------------------------------------------------------------------------------
Phase 12 Urban & Envir.     2.00 h      2 (1.0/h)    2 (1.0/h)    21 (10.5/h)  Heavy metallic impacts, vehicle backfires
Phase 16 Stream 05 (Exhaust)0.50 h      0 (0.0/h)    0 (0.0/h)    15 (30.0/h)  Continuous blade flutter & tonal resonance
Phase 16 Streams (10 others)5.58 h      7 (1.25/h)   2 (0.36/h)   0 (0.0/h)    Clean background rejection
Phase 38 Dev Continuous     1.12 h      3 (2.68/h)   0 (0.0/h)    1 (0.89/h)   Intermittent urban transient
```

#### Root Cause 1: Uniformly Relaxed Confirmation Thresholds
To capture muffled pocket impulses in V4, the confirmation threshold was uniformly lowered from $0.68$ to $0.62$, and the single-impulse minimum crest factor was relaxed from $13.5\text{ dB}$ to $11.5\text{ dB}$. While this succeeded in recovering damped gunshots, it left the detector vulnerable whenever the acoustic channel was completely unobstructed:
* In open-air urban environments, ambient mechanical clatter (dumpsters slamming, construction drops, automotive backfires) naturally produces crest factors between $12.0\text{ dB}$ and $15.0\text{ dB}$.
* Because V4 applied the $0.62$ threshold globally across all environments, these non-gunshot transients easily crossed the confirmation barrier.

#### Root Cause 2: Industrial Exhaust Flutter & Tonal Modulation
In Phase 16 Stream 05 (`phase16_industrial_exhaust_ventilation_30min.wav`), continuous ventilation fan rotation created periodic amplitude modulations and high mid-band acoustic energy ($500 - 2500\text{ Hz}$).
* V4’s 26-dimensional fusion classifier relied heavily on mid-band ratio ($r_{\text{mid}}$) to identify muffled gunshots.
* Because Stream 05 exhibited $r_{\text{mid}} \approx 0.52$ and periodic crest spikes, the fusion model scored these windows at $0.63 - 0.67$. Under V4's static $0.62$ threshold, 15 false alarms were emitted in 30 minutes!

---

### 2.2 Forensic Analysis of the Glass Break Suppression Deadlock

In Phase 46, glass shatter suppression was added to prevent V3's false positives on ESC-50 glass breaking. However, empirical testing showed that V4 still triggered on glass breaking recordings.

#### The Safeguard Deadlock Mechanism:
1. **The Intended Logic:**
   ```python
   # Intended V4 Suppression Rule
   if glass_s >= 0.30 and hi >= 0.30 and bal_s < 0.20:
       adj_score *= 0.35
   ```
2. **The Acoustic Collision:**
   When glass shatters, high-velocity acoustic fracturing generates sharp micro-transients. In YAMNet's 521-class taxonomy, these sharp fracture transients activate:
   * Class 434: `Crack`
   * Class 436: `Sharp crack`
3. **The Ballistic Masking Spike:**
   Because YAMNet maps both gunshot muzzle cracks and glass fractures to `Crack` / `Sharp crack`, the composite ballistic score $p_{\text{bal}}$ (which aggregates classes 420, 421, 422, 424, 425, 428, 434, 460) spiked to **$0.4972$**.
4. **The Deadlock:**
   The safeguard condition `bal_s < 0.20` was evaluated to protect genuine gunshots. Because $p_{\text{bal}} = 0.4972 \ge 0.20$, the safeguard interpreted the glass fracture as a potential gunshot crack and **completely bypassed suppression**! The raw score ($0.88 - 0.92$) remained unattenuated, emitting an immediate false confirmation.

```
Glass Fracture Suppression Trace:
Recording: p15_neg_086_esc50_glass_breaking
- Raw Fusion Score: 0.8842
- YAMNet Glass Score (class 433/435): 0.6210 (Trigger criteria met: >= 0.30)
- High-Band Ratio: 0.4420 (Trigger criteria met: >= 0.30)
- YAMNet Crack Score (class 434): 0.4972
- Resulting bal_s: 0.4972
- V4 Rule Evaluation: (glass_s >= 0.30) AND (hi >= 0.30) AND (bal_s < 0.20) -> FALSE!
- V4 Output: No suppression applied (Score: 0.8842 -> CONFIRMED FALSE ALARM)
- V5 Fixed Rule: (glass_s > bal_s OR gun_s < 0.20) -> TRUE!
- V5 Output: Suppressed by 0.35x (Score: 0.8842 * 0.35 = 0.3095 -> REJECTED)
```

---

### 2.3 Atmospheric Thunder & Low-Frequency Impulse Mechanics

Distant thunder and heavy mechanical rumbles exhibit heavy acoustic concentration below 500 Hz:
* Low-band energy ratio: $r_{\text{low}} > 0.65$
* Mid-to-low ratio: $r_{\text{m2l}} < 0.55$
* Spectral centroid: $\mu_c < 800\text{ Hz}$

However, distant thunder in field recordings often produces YAMNet thunder scores below the $0.25$ threshold ($p_{\text{thunder}} \approx 0.05 - 0.15$), avoiding semantic suppression. When lightning strikes or shock waves produce an initial pressure pulse, the crest factor can exceed $14\text{ dB}$, leading to false trigger confirmation under static low thresholds.

---

## 3. Acoustic Condition Estimation: Boundaries and Failure Modes

To prevent static threshold vulnerabilities, **Detector Improvement V5** introduces online condition estimation. However, estimating the acoustic environment from streaming audio possesses fundamental physical limitations:

### 3.1 Mode Transition Boundaries
The condition estimator tracks four spectral ratios:
* High-band ratio ($r_{\text{high}}$)
* Mid-band ratio ($r_{\text{mid}}$)
* Low-band ratio ($r_{\text{low}}$)
* Channel roll-off ($r_{\text{rolloff}} = r_{\text{high}} / r_{\text{mid}}$)

Using exponential moving average (EMA) smoothing ($\alpha = 0.25$):
$$\bar{x}_t = \alpha x_t + (1 - \alpha) \bar{x}_{t-1}$$

```
Mode Decision Boundaries:
Mode                   Criteria
---------------------------------------------------------------------------------------
CLEAR_NORMAL           rolloff_ema >= 0.18 AND high_ema >= 0.080 AND mid_to_low_ema >= 0.65
DEGRADED_OCCLUDED      rolloff_ema < 0.14 AND (high_ema < 0.060 OR mid_to_low_ema < 0.60)
UNKNOWN                All intermediate hysteresis states
```

### 3.2 Observed Condition Estimation Failure Modes

1. **Transient Occlusion Lag (Window Latency):**
   When a microphone is suddenly placed into a pocket or covered by clothing, the EMA filter requires approximately **2–3 analysis windows (0.96 s – 1.44 s)** to transition from `CLEAR_NORMAL` to `DEGRADED_OCCLUDED`. If a gunshot occurs during this exact transition window, the detector operates under the conservative clear-channel policy (threshold 0.70), risking a missed event.
2. **Reverberant Indoor Spaces with Acoustic Curtains:**
   Heavily damped rooms with acoustic absorption tiles attenuate high frequencies above 3 kHz, mimicking fabric pocket occlusion. The estimator can misclassify such indoor spaces as `DEGRADED_OCCLUDED`, lowering the threshold to $0.62$ and temporarily increasing sensitivity to indoor transient impacts.
3. **Rapid Environmental Switching (Vehicle Ingress/Egress):**
   Moving rapidly from a quiet open-air environment into a rumbling vehicle shifts low-band ratios sharply. Without the 2-window hysteresis safeguard, the estimator could chatter rapidly between modes, destabilizing FSM confirmation windows.

---

## 4. Key Architectural Lessons for Detector Improvement V5

1. **Decouple Policy from State Switching:** Mode changes alone must never confirm alerts, clear candidate history, or trigger state transitions.
2. **Dynamic Context-Aware Confirmation:** When clear acoustic transmission is verified ($r_{\text{rolloff}} \ge 0.18$), enforce strict $0.70$ thresholds and $13.5\text{ dB}$ crest limits. Only when sustained fabric occlusion is confirmed should the $0.62$ threshold be granted.
3. **Resolve Suppression Deadlocks:** Semantic suppression must never be blocked by shared acoustic sub-classes (`Crack`) when the primary distractor class (`Glass`) dominates.
4. **Physical Low-Frequency Attenuation:** Augment semantic thunder suppression with direct DSP spectral slope gating when low-band energy exceeds $65\%$.

---

*Mandatory Safety Designation: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.*

