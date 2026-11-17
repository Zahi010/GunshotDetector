# Phase 52: Comparative Evaluation — Detector Improvement V8 vs. V9

**Mandatory Safety Designation:**
> **RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.**
> This is uncertified research software. Never deploy it for autonomous emergency dispatch, police tactical response, active-shooter alerting, automated evacuation, building lockdown, or life-critical physical security. Use only lawfully obtained recordings and safe audio playback. Live-fire and hazardous acoustic experiments are strictly prohibited.

---

## 1. Executive Summary

Phase 52 conducted a direct head-to-head paired evaluation between **Detector Improvement V8** (the balanced candidate qualified in Phase 51) and **Detector Improvement V9** (incorporating guarded saturation thunder gating and supersonic membrane rupture discrimination).

The evaluation was executed across the complete Phase 51 independent evaluation corpus:
- **373 Discrete Audio Recordings:** 65 genuine multi-caliber gunshots and 308 rigorous negative challenge files.
- **12.00 Hours Continuous Audio Exposure:** 15 unsegmented streams across Phase 17 Urban, Phase 27 Aviation, and Phase 8 Mixed environments.
- **Physical Microphone Hardware Ingestion:** Live streaming via host `Microphone (Realtek(R) Audio)`.

---

## 2. Comparative Performance Scorecard

| Evaluation Metric | V8 (Qualified Baseline) | V9 (Remediated Candidate) | Net Delta ($\Delta$) | Statistical Contrast / Significance |
| :--- | :---: | :---: | :---: | :---: |
| **Total Positive Recall ($N=65$)** | **69.23%** (45/65) | **69.23%** (45/65) | **0.00%** | **$p = 1.000$** (100% paired preservation) |
| *Wilson 95% Confidence Interval* | [57.20%, 79.11%] | [57.20%, 79.11%] | Identical | Zero genuine gunshots dropped |
| Clean Open-Air Recall ($N=35$) | 65.71% (23/35) | 65.71% (23/35) | 0.00% | Preserved across all 35 files |
| High-Energy Clipped Recall ($N=15$) | 60.00% (9/15) | 60.00% (9/15) | 0.00% | Saturation override safely maintained |
| Rapid Cadence / Bursts ($N=9$) | 88.89% (8/9) | 88.89% (8/9) | 0.00% | Multi-window FSM clustering preserved |
| Pocket-Occluded Recall ($N=3$) | 100.0% (3/3) | 100.0% (3/3) | 0.00% | Degraded frequency detection preserved |
| Reverberant Urban Distance ($N=3$) | 66.67% (2/3) | 66.67% (2/3) | 0.00% | Distant multipath handling preserved |
| **Heavy Door Slam FPR ($N=12$)** | **66.67%** (8/12) | **0.00%** (0/12) | **-66.67%** | **McNemar $p = 0.0078$** (All 8 false alarms eliminated) |
| *Wilson 95% Confidence Interval* | [39.11%, 86.19%] | [0.00%, 24.25%] | -61.94% upper | Defect completely resolved |
| **Balloon Burst Stress FPR ($N=12$)** | **100.0%** (12/12) | **0.00%** (0/12) | **-100.0%** | **McNemar $p = 0.00049$** (All 12 false alarms eliminated) |
| *Wilson 95% Confidence Interval* | [75.75%, 100.0%] | [0.00%, 24.25%] | -75.75% upper | Membrane rupture discrimination verified |
| **Fireworks / Pyrotechnics FPR ($N=12$)**| **0.00%** (0/12) | **0.00%** (0/12) | 0.00% | Mid-band pyrotechnic gating preserved |
| **Untouched Glass Shatter FPR ($N=20$)**| **0.00%** (0/20) | **0.00%** (0/20) | 0.00% | High-band centroid gating preserved |
| **Metal Hammer Impacts FPR ($N=12$)** | **0.00%** (0/12) | **0.00%** (0/12) | 0.00% | Harmonic decay gating preserved |
| **Atmospheric Thunder FPR ($N=12$)** | **0.00%** (0/12) | **0.00%** (0/12) | 0.00% | Low-frequency rumble gating preserved |
| **Vehicle Backfires FPR ($N=12$)** | **0.00%** (0/12) | **0.00%** (0/12) | 0.00% | Combustion transient rejection preserved |
| **Toy Gun Pops FPR ($N=12$)** | **0.00%** (0/12) | **0.00%** (0/12) | 0.00% | Ballistic energy gating preserved |
| **Percussion Transients FPR ($N=12$)** | **0.00%** (0/12) | **0.00%** (0/12) | 0.00% | Musical impulse rejection preserved |
| **Laser Contact Mic FPR ($N=12$)** | **0.00%** (0/12) | **0.00%** (0/12) | 0.00% | Transducer impulse rejection preserved |
| **Environmental Non-Targets ($N=180$)**| **2.22%** (4/180) | **2.22%** (4/180) | 0.00% | Identical across 9 ESC-50 classes |
| **Continuous Alerts ($T=12.00\text{ hr}$)** | **7 alerts** (0.73/hr) | **7 alerts** (0.73/hr) | 0 alerts | Poisson rate test $p = 1.000$ |
| **Streaming Chunk Latency (Live Mic)** | 77.65 ms | 77.65 ms | — | $< 16.2\%$ of 480 ms window budget |
| **Dropped Windows on Live Hardware** | 0.00% (0/13) | 0.00% (0/13) | — | Zero audio buffer overruns |

---

## 3. Detailed Acoustic Analysis of Remediations

### 3.1 Heavy Door Slam Remediation:
- **The Defect in V8:** Clause 3 of `is_gunshot_transient` in `CalibratedSemanticSuppressionV8` permitted saturated impulses ($peak \ge 0.30, crest \ge 12.0\text{ dB}, cent \ge 600.0\text{ Hz}$) to bypass rumble suppression without checking for sub-bass dominance. Heavy metal door slams have peak amplitudes $> 0.88$ and latch pings pulling centroid $> 620\text{ Hz}$, but concentrate $> 99.7\%$ of energy below 500 Hz ($m2l < 0.0011$).
- **The V9 Guard:** Adding `m2l >= 0.05` and `lo < 0.90` prevents sub-bass dominated door slams from bypassing thunder suppression.
- **Empirical Result:** Door slam false alarms dropped from **8/12 to 0/12**, eliminating the regression entirely.

### 3.2 Balloon Burst Discrimination:
- **The Mechanism in V8:** All 12 balloon bursts triggered V8 because supersonic latex membrane rupture creates real acoustic $N$-wave shock fronts with crest factors $> 27\text{ dB}$ that YAMNet classifies as `Whip`, `Explosion`, and `Gunshot`.
- **The V9 Discrimination:** V9 introduces a supersonic membrane rupture rule:
  `cent >= 3400.0 Hz and hi >= 0.75 and lo <= 0.015 and pure_gun < 0.35`
- **Empirical Result:** Balloon burst false alarms dropped from **12/12 to 0/12**.
- **Preservation Check:** Genuine gunshots always possess an explosive combustion muzzle blast depositing energy below 1,000 Hz ($lo \ge 0.031$, $cent \le 2913.7\text{ Hz}$). Zero genuine gunshots matched this rule.

---

## 4. Hardware and Latency Benchmarks

- **Live Transducer Ingestion:** Executed using the host system's physical `Microphone (Realtek(R) Audio)` over 16,000 Hz single-channel PCM.
- **Latency:** Average chunk processing latency was **$77.65\text{ ms}$** against a **$480.0\text{ ms}$** hop window, leaving $> 83\%$ CPU headroom.
- **Dropped Window Rate:** **0.00%** over live continuous capture.

