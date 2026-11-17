# Phase 50 Experiment: Detector Improvement V8

**RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.**

> [!WARNING]
> **RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.**
> This is an uncertified research prototype developed strictly for acoustic signal processing and forensic audio experimentation. It must never be deployed for autonomous emergency dispatch, police tactical response, active-shooter alerting, automated evacuation, building lockdown, or life-critical physical security. Use lawfully obtained recordings and safe audio playback only. Live-fire testing and hazardous acoustic experiments are strictly prohibited.

---

## 1. Context and Objective

Phase 49 qualified **Detector Improvement V7** as the leading positive-detection candidate, improving global positive recall from $66.84\%$ to $82.63\%$ and recovering 30 additional positive recordings (+21.73% on Phase 19 Field gunshots).

However, Phase 49 identified two crucial regressions:
1. **Phase 12 Continuous Ambient Stream Alerts:** Increased from 7 to 16 alerts across 2 hours (3.5 to 8.0 alerts/hour).
2. **Phase 12 Fireworks False Alarm Rate:** Increased from 12.5% to 37.5% (3/8 vs 1/8).

The objective of Phase 50 was to construct **Detector Improvement V8** to recover from these false alarm regressions without losing V7's positive detection recovery.

---

## 2. Experimental Hypotheses

1. **Hypothesis 1 (Pyrotechnic Acoustic Profile):**
   Chemical fireworks mortars produce low-centroid, sub-bass dominant explosions ($m2l < 0.15, cent < 500\text{ Hz}$). Requiring supersonic ballistic shockwave acoustic energy ($m2l \ge 0.25 \land cent \ge 750\text{ Hz}$, or $cent \ge 1200\text{ Hz}$) to activate the pyrotechnic override will suppress chemical fireworks without attenuating genuine field gunshots.
2. **Hypothesis 2 (Transient Acoustic Thunder Gating):**
   Low-frequency environmental booms and thunder claps lack sharp acoustic impulse transients. Requiring verified gunshot transient acoustics ($m2l \ge 0.40 \land cent \ge 750\text{ Hz} \land crest \ge 16.0\text{ dB}$, or $pure\_gun \ge 0.12$) to bypass thunder suppression will eliminate continuous stream thunder/boom alerts.
3. **Hypothesis 3 (FSM UNKNOWN Tightening):**
   In UNKNOWN mode, isolated mechanical impacts lack both high crest factors ($\ge 13.5\text{ dB}$) and sharp high-frequency acoustics ($m2l \ge 0.35 \land cent \ge 750\text{ Hz}$). Requiring these criteria for single-impulse exception will eliminate isolated mechanical thuds in continuous urban streams while multi-window confirmed gunshots remain fully detectable.

---

## 3. Results Summary

- **Continuous Urban Ambient False Alerts:** Dropped from 16 in V7 to **5 in V8** (**-68.75%**), outperforming baseline V6 (7 alerts).
- **Phase 12 Fireworks False Alarms:** Cured from 3/8 (37.5%) in V7 down to **1/8 (12.5%) in V8**, completely resolving the Phase 49 regression.
- **Phase 19 Field Positive Recall:** Preserved at **91.30% (21/23)**, matching V7 and outperforming V6 (69.57%).
- **Phase 12 Discrete Positives:** Preserved at **79.17% (38/48)**, matching V7 and outperforming V6 (66.67%).
- **Phase 15 Discrete Positives:** Preserved at **85.11% (40/47)**, matching V7 and outperforming V6 (70.21%).
- **Phase 16 Industrial Continuous Audio:** Maintained at **0 alerts (0.0000 alerts/hour)** across 6.08 hours.

---

## 4. Final Conclusion & Recommendation

All three hypotheses were verified by rigorous multi-corpus benchmarking.
Detector Improvement V8 achieves the desired false alarm recovery while maintaining high sensitivity across all holdouts.
**Detector Improvement V8 is qualified as the new leading experimental candidate.**

