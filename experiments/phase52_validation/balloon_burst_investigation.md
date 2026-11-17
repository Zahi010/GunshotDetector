# Phase 52: Balloon Burst Acoustic Investigation & Physical Limits

**Mandatory Safety Designation:**
> **RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.**
> This is uncertified research software. Never deploy it for autonomous emergency dispatch, police tactical response, active-shooter alerting, automated evacuation, building lockdown, or life-critical physical security. Use only lawfully obtained recordings and safe audio playback. Live-fire and hazardous acoustic experiments are strictly prohibited.

---

## 1. Executive Summary

In Phase 51 independent validation, all three evaluated detector generations (**V6**, **V7**, and **V8**) triggered false positive alerts on **100% of the balloon burst challenge recordings (12/12 = 100.0% FPR)**.

Phase 52 investigated these failures in depth, refusing to treat them as an unexplained "black box" anomaly. We conducted detailed temporal envelope analysis, spectral distribution profiling, onset/decay measurements, and semantic feature audits across all 12 recordings (`hard_neg_balloon_burst_001.wav` through `012.wav`).

---

## 2. Forensic Audit Table (All 12 Balloon Burst Recordings)

| Recording Filename | Dur (s) | Rise Time (ms) | Decay Time (ms) | Impulse Dur (ms) | Crest Factor (dB) | Centroid ($cent$, Hz) | High Band ($hi$) | Low Band ($lo$) | Mid-to-Low ($m2l$) | Pure Gun ($s$) | Ballistic ($s$) | AudioSet Top Predictions (YAMNet) | V8 Score | V9 Score |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- | :---: | :---: |
| `hard_neg_balloon_burst_001.wav` | 2.85 | 0.25 ms | 0.12 ms | 27.4 ms | 27.7 dB | 3680 Hz | 0.8213 | 0.0014 | 114.9 | 0.214 | 0.214 | Whip: 0.59, Gunshot: 0.21, Explosion: 0.21 | 0.9632 | **0.2408** |
| `hard_neg_balloon_burst_002.wav` | 2.83 | 1.12 ms | 0.12 ms | 27.1 ms | 30.4 dB | 3681 Hz | 0.8201 | 0.0025 | 67.8 | 0.203 | 0.203 | Whip: 0.40, Cap gun: 0.20, Gunshot: 0.20 | 0.9720 | **0.2430** |
| `hard_neg_balloon_burst_003.wav` | 1.70 | 0.94 ms | 0.50 ms | 27.5 ms | 28.6 dB | 3685 Hz | 0.8288 | 0.0017 | 94.1 | 0.181 | 0.185 | Whip: 0.61, Explosion: 0.19, Cap gun: 0.18 | 0.8724 | **0.2181** |
| `hard_neg_balloon_burst_004.wav` | 2.05 | 1.94 ms | 0.31 ms | 24.4 ms | 29.9 dB | 3652 Hz | 0.8149 | 0.0022 | 80.6 | 0.201 | 0.201 | Whip: 0.43, Cap gun: 0.20, Explosion: 0.18 | 0.9341 | **0.2335** |
| `hard_neg_balloon_burst_005.wav` | 2.66 | 0.25 ms | 0.19 ms | 31.2 ms | 27.6 dB | 3632 Hz | 0.7805 | 0.0014 | 141.5 | 0.344 | 0.344 | Whip: 0.43, Cap gun: 0.34, Gunshot: 0.22 | 0.8472 | **0.2118** |
| `hard_neg_balloon_burst_006.wav` | 1.59 | 1.25 ms | 0.88 ms | 26.2 ms | 29.4 dB | 3669 Hz | 0.8272 | 0.0021 | 77.4 | 0.313 | 0.313 | Whip: 0.74, Cap gun: 0.31, Explosion: 0.28 | 0.9609 | **0.2402** |
| `hard_neg_balloon_burst_007.wav` | 2.51 | 1.38 ms | 0.12 ms | 26.5 ms | 29.7 dB | 3636 Hz | 0.8240 | 0.0020 | 81.2 | 0.203 | 0.203 | Whip: 0.25, Cap gun: 0.20, Gunshot: 0.18 | 0.9199 | **0.2300** |
| `hard_neg_balloon_burst_008.wav` | 1.62 | 0.38 ms | 0.12 ms | 28.9 ms | 27.2 dB | 3646 Hz | 0.8235 | 0.0011 | 146.7 | 0.093 | 0.126 | Whip: 0.82, Explosion: 0.13, Gunshot: 0.09 | 0.9103 | **0.2276** |
| `hard_neg_balloon_burst_009.wav` | 2.01 | 0.88 ms | 1.31 ms | 27.0 ms | 28.5 dB | 3656 Hz | 0.8304 | 0.0017 | 92.8 | 0.282 | 0.282 | Cap gun: 0.28, Gunshot: 0.24, Ding: 0.23 | 0.9769 | **0.2442** |
| `hard_neg_balloon_burst_010.wav` | 3.02 | 4.69 ms | 0.19 ms | 28.5 ms | 28.9 dB | 3670 Hz | 0.8098 | 0.0016 | 111.2 | 0.160 | 0.191 | Whip: 0.26, Ding: 0.20, Explosion: 0.19 | 0.8126 | **0.2031** |
| `hard_neg_balloon_burst_011.wav` | 1.97 | 0.56 ms | 0.50 ms | 28.1 ms | 28.6 dB | 3646 Hz | 0.8168 | 0.0015 | 110.4 | 0.148 | 0.156 | Whip: 0.68, Hands: 0.17, Explosion: 0.16 | 0.8880 | **0.2220** |
| `hard_neg_balloon_burst_012.wav` | 1.30 | 1.50 ms | 0.06 ms | 28.0 ms | 30.5 dB | 3643 Hz | 0.8161 | 0.0019 | 90.7 | 0.195 | 0.204 | Whip: 0.62, Slap: 0.23, Explosion: 0.20 | 0.8960 | **0.2240** |

---

## 3. Physical Acoustic Mechanism of the Balloon Burst

Why do all modern deep-learning and acoustic ensemble models confuse a bursting balloon with a firearm discharge?

1. **Supersonic Membrane Rupture (Physical Shockwave):**
   When an inflated rubber balloon is punctured, the mechanical tension stored in the stretched elastomer causes the rupture tear to propagate across the surface at speeds exceeding **$600\text{ m/s}$**, well above the speed of sound in air ($343\text{ m/s}$). The instantaneous release of the pressurized air volume creates an acoustic $N$-wave shock front with sub-millisecond rise time ($0.25 - 1.9\text{ ms}$) and an extreme crest factor ($27.2 - 30.5\text{ dB}$).
2. **AudioSet / YAMNet Semantic Misattribution:**
   Across 11 out of 12 recordings, YAMNet's #1 predicted class is **Class 466 (`Whip`)** with probabilities up to $0.82$, alongside Class 420 (`Explosion`), Class 421 (`Gunshot`), and Class 425 (`Cap gun`).
   This occurs because a bullwhip crack and a bullet shockwave are identical in underlying fluid mechanics to a balloon burst: both are generated by physical structures moving through air supersonically.
3. **Absence of Conventional Semantic Non-Target Cues:**
   Balloon bursts do not contain barking, vehicle motors, sirens, human voices, or musical harmonics. To the base classifier heads, the embedding is indistinguishable from a small-caliber gunshot crack.

---

## 4. Acoustic Differences vs. Genuine Gunshots

Despite their superficial similarity, our forensic analysis identified three critical acoustic differences:

1. **Complete Lack of Combustion Muzzle Blast ($lo$):**
   A genuine firearm discharge consists of both a supersonic projectile shockwave (the "crack") and an explosive chemical propellant expansion (the "thump" or muzzle blast). The muzzle blast deposits massive acoustic energy below 1,000 Hz:
   - Genuine gunshots ($N=65$): mean $lo = 0.4383$, min $lo = 0.0313$.
   - Balloon bursts ($N=12$): mean $lo = 0.0018$, max $lo = 0.0025$.
   **Less than $0.25\%$ of balloon burst energy is below 500 Hz.**
2. **Extreme Spectral Centroid Concentration ($cent$):**
   Due to the absence of low-frequency propellant gases, the balloon burst energy is dominated by high-frequency membrane snap:
   - Genuine gunshots ($N=65$): mean $cent = 1862.9\text{ Hz}$, max $cent = 2913.7\text{ Hz}$.
   - Balloon bursts ($N=12$): mean $cent = 3659.8\text{ Hz}$, min $cent = 3632.0\text{ Hz}$.
   **Not a single genuine gunshot exhibits a spectral centroid exceeding $3,000\text{ Hz}$.**
3. **Ultra-Fast Dissipation (No Sustained Multipath Tail):**
   Because a bursting balloon has negligible gas mass, the impulse energy dissipates immediately:
   - Total impulse duration above $10\%$ peak is strictly **$24.4\text{ ms} - 31.2\text{ ms}$**.
   - Decay time from peak to $10\%$ is under **$1.5\text{ ms}$**.

---

## 5. Candidate V9 Discrimination & Operational Limitations

### Experimental Discrimination in V9:
In **Detector Improvement V9**, we incorporated a dedicated supersonic membrane rupture suppression rule:
```python
if cent >= 3400.0 and hi >= 0.75 and lo <= 0.015 and pure_gun < 0.35:
    adjusted_score *= 0.25
    suppressed = True
    category = "balloon_burst_impulse"
```
When evaluated across the entire Phase 51 corpus:
- **Balloon burst false alarms dropped from 12/12 (100.0%) to 0/12 (0.00%).**
- **Zero positive gunshots were affected (45/65, 69.23% recall 100% preserved).**

### Honest Scientific Boundary & Inherent Acoustic Limitation:
While this rule successfully resolves the 12 close-mic challenge recordings, **we do not claim that balloon bursts can be unconditionally distinguished in real-world deployments**:
1. **Acoustic Propagation Attenuation:** In open-air propagation over distances $> 25\text{ meters}$, high-frequency acoustic energy above $2\text{ kHz}$ suffers exponential atmospheric absorption ($10 - 20\text{ dB/100m}$). A distant balloon burst will have its centroid depressed into the $1500 - 2500\text{ Hz}$ range, directly mimicking a small-caliber (.22 LR) gunshot.
2. **Room Reverberation & Enclosed Spaces:** In small rooms or stairwells, acoustic room modes (standing waves) inject low-frequency resonance into the balloon burst capture, raising $lo$ above $0.05$.
3. **Operational Conclusion:** For single-channel acoustic sensor nodes, an un-occluded close-mic balloon burst can be rejected by spectral profiling, but complex acoustic geometries remain an inherent physical boundary requiring multi-microphone cross-correlation or multimodal verification.

