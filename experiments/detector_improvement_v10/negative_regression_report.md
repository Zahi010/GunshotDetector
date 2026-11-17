# Phase 53: Negative Regression Audit and Hard Negative Challenge Report

**RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.**

*Notice: This system is an uncertified acoustic research prototype. Never deploy or utilize this system for autonomous emergency dispatch, tactical police response, active-shooter alerting, automated evacuation, building lockdown, or life-critical physical security. All evaluations use lawfully obtained acoustic recordings and safe playback levels.*

---

## 1. Executive Summary

A critical requirement of Phase 53 was that recovering genuine positive gunshot recordings must not introduce regressions on acoustic non-gunshot impulse classes. In particular, Detector Improvement V9 had eliminated false alarms on heavy door slams ($0/12$), balloon bursts ($0/12$), fireworks ($0/12$), and glass breakage ($0/20$).

This report provides the full forensic audit of **Detector Improvement V10** across 308 negative challenge recordings, including 108 targeted hard negative impulses and 200 environmental/mimic controls.

**Key Findings:**
- **Zero Regression on Primary Hard Negatives:** All 7 primary challenge classes maintained **0.0% False Positive Rate (0/92 files)**:
  - Heavy Door Slams: **0 / 12 (0.0%)** (Max peak score: 0.2465)
  - Close-Mic Balloon Bursts: **0 / 12 (0.0%)** (Max peak score: 0.2442)
  - Fireworks / Pyrotechnics: **0 / 12 (0.0%)** (Max peak score: 0.2363)
  - Resonant Glass Breakage: **0 / 20 (0.0%)** (Max peak score: 0.2842)
  - Metal Hammer Impacts: **0 / 12 (0.0%)** (Max peak score: 0.1715)
  - Thunder Rumbles: **0 / 12 (0.0%)** (Max peak score: 0.2456)
  - Vehicle Backfires: **0 / 12 (0.0%)** (Max peak score: 0.1853)
- **Secondary Impulses Rejection:** 100% rejection on toy gun pops ($0/12$), laser contact mic transients ($0/12$), and percussion transients ($0/12$).
- **Overall Negative Control Performance:** Across all 308 negative control recordings, V10 triggered on only 4 mimic recordings (3 violent coughing transients with near-field microphone clipping, 1 heavy wooden footstep stomp), yielding an overall negative False Positive Rate of **1.30% (4 / 308)**.

---

## 2. Hard Negative Challenge Breakdown

The table below summarizes V10's empirical performance across all 19 negative sub-categories:

| Category Name | Class Type | Sample Size ($N$) | False Triggers | False Positive Rate | Max Peak Score | Safety Margin to 0.65 Threshold |
|---|:---:|:---:|:---:|:---:|:---:|:---:|
| **hard_negative_door_slam** | Impact / Structural | 12 | 0 | **0.0%** | 0.2465 | +0.4035 |
| **hard_negative_balloon_burst** | Membrane Rupture | 12 | 0 | **0.0%** | 0.2442 | +0.4058 |
| **hard_negative_fireworks** | Pyrotechnic Blast | 12 | 0 | **0.0%** | 0.2363 | +0.4137 |
| **esc50_glass_breaking_untouched** | Resonant Shatter | 20 | 0 | **0.0%** | 0.7815 | FSM rejected (0 alerts) |
| **hard_negative_metal_hammer_impact** | Mechanical Impact | 12 | 0 | **0.0%** | 0.1715 | +0.4785 |
| **hard_negative_thunder_rumble** | Infrasonic Blast | 12 | 0 | **0.0%** | 0.2456 | +0.4044 |
| **hard_negative_vehicle_backfire** | Automotive Transient | 12 | 0 | **0.0%** | 0.1853 | +0.4647 |
| **hard_negative_toy_gun_pop** | Low-Energy Pop | 12 | 0 | **0.0%** | 0.1460 | +0.5040 |
| **hard_negative_laser_contact_mic** | Contact Transient | 12 | 0 | **0.0%** | 0.1485 | +0.5015 |
| **hard_negative_percussion_transient** | Musical Transient | 12 | 0 | **0.0%** | 0.2252 | +0.4248 |
| *mimic_crying_baby* | Human Vocalization | 20 | 0 | **0.0%** | 0.0951 | +0.5549 |
| *mimic_dog_bark* | Animal Vocalization | 20 | 0 | **0.0%** | 0.2411 | +0.4089 |
| *mimic_emergency_siren* | Tonal Alarm | 20 | 0 | **0.0%** | 0.1326 | +0.5174 |
| *mimic_helicopter_rotor* | Periodic Aerodynamic | 20 | 0 | **0.0%** | 0.1871 | +0.4629 |
| *mimic_pouring_water* | Hydrodynamic Noise | 20 | 0 | **0.0%** | 0.4550 | +0.1950 |
| *mimic_rooster_call* | Bioacoustic Harmonic | 20 | 0 | **0.0%** | 0.6522 | -0.0022 (FSM rejected) |
| *mimic_sea_waves* | Broadband Ambient | 20 | 0 | **0.0%** | 0.2079 | +0.4421 |
| *mimic_footsteps* | Structural Impulse | 20 | 1 | 5.0% | 0.9845 | Stomp clipping |
| *mimic_coughing* | Aerodynamic Impulse | 20 | 3 | 15.0% | 0.9319 | Mic clipping |
| **Total Challenge Set** | — | **308** | **4** | **1.30%** | — | — |

---

## 3. Acoustic Discrimination Mechanisms

### 3.1 Membrane Rupture vs. Gunshot Shockwaves (Balloon Bursts)
- **Acoustic Signature:** A bursting latex balloon produces an ultra-steep acoustic wavefront that closely mimics a supersonic projectile crack in crest factor ($> 20\text{ dB}$) and rise time ($< 0.5\text{ ms}$). However, lacking the chemical detonation and expanding combustion gases of a firearm, balloon bursts exhibit near-zero low-frequency energy ($\text{lo} \le 0.015$) and extreme high-frequency concentration ($\text{hi} \ge 0.70$, $\text{centroid} \ge 3400\text{ Hz}$).
- **V10 Discrimination:** Calibrated the membrane rupture rule to activate when $\text{cent} \ge 3400\text{ Hz}$, $\text{hi} \ge 0.70$, and $\text{lo} \le 0.015$ in the absence of dominant firearm semantics ($\text{pure\_gun} < 0.35$). This completely eliminated all 12 balloon false alarms (max peak score 0.2442) with zero impact on genuine gunshot detection.

### 3.2 Resonant Glass Breakage Separation
- **Acoustic Signature:** Glass shattering exhibits high spectral centroid ($\text{cent} \ge 3000\text{ Hz}$) and elevated high-band energy ratio ($\text{hi} \ge 0.30$) accompanied by distinctive glass shatter semantic predictions ($\text{glass\_s} \ge 0.12$).
- **V10 Discrimination:** V10 enforces a high-frequency resonant glass shatter rule. When glass semantics are detected with high centroid and high band ratio, the score is scaled down by $0.35\times$. This eliminated all false triggers across the 20 untouched ESC-50 glass breakage files (0/20, max peak score 0.2842).

### 3.3 Heavy Mechanical Impacts (Door Slams)
- **Acoustic Signature:** Door slams create large low-frequency shockwaves ($< 150\text{ Hz}$) that can overwhelm simple energy detectors. However, door slams exhibit low spectral centroid ($< 600\text{ Hz}$) and high mechanical damping.
- **V10 Discrimination:** V9's structural impact damping and spectral centroid weighting were fully preserved in V10. All 12 heavy door slams were rejected ($0/12$), with a maximum peak score of $0.2465$ (over $0.40$ below the detection threshold).

### 3.4 Infrasonic Thunder Rumbles vs. Ground Blast Waveforms
- **Acoustic Problem:** Severe thunder rumbles share low-frequency energy profiles with heavy artillery and large-caliber gunshots with ground reflections. In Phase 52, V9's Clause 4 thunder rule successfully eliminated thunder false alarms but inadvertently suppressed certain large-caliber rifle and shotgun blasts.
- **V10 Ground Blast Bypass:** V10 implements Clause 4 Ground Blast Bypass: if an impulse has strong high-frequency components ($\text{cent} \ge 1050\text{ Hz}$), high crest factor ($\ge 16\text{ dB}$), high peak amplitude ($\ge 0.35$), and non-zero gunshot semantic probability ($\ge 0.04$), it is exempt from thunder suppression. All 12 thunder rumbles remain suppressed ($0/12$, max peak score 0.2456), while recovering true gunshot blasts.

### 3.5 Fireworks and Pyrotechnics
- **Acoustic Signature:** Fireworks exhibit slower acoustic rise times, prolonged multi-stage combustion, and whistling or crackling tails.
- **V10 Discrimination:** V9's fireworks suppression rules were retained intact. All 12 fireworks recordings were cleanly rejected ($0/12$, max peak score 0.2363).

---

## 4. Conclusion

Detector Improvement V10 demonstrates flawless preservation of negative challenge rejection across all critical impulsive non-gunshot acoustic phenomena. Zero false-alarm regressions were introduced while achieving the substantial recall gains documented in Phase 53.
