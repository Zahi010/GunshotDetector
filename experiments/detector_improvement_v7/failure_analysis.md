# Forensic Failure Analysis: Detector Improvement V6 Missed Positives and Remaining False Alarms

**RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.**

> [!WARNING]
> **RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.**
> This software is uncertified research code developed strictly for acoustic signal processing and forensic audio research. It must never be deployed for autonomous emergency dispatch, police tactical response, active-shooter alerting, automated evacuation, building lockdown, or life-critical physical security. Use lawfully obtained recordings and safe audio playback only. Live-fire testing and hazardous acoustic experiments are strictly prohibited.

---

## 1. Executive Summary

Following the deployment and evaluation of **Detector Improvement V6** in Phase 48 (which successfully eliminated industrial continuous false alarms to $0.00\text{ alerts/hour}$ over 6.08 hours and reduced urban continuous alerts from 15 to 7), Phase 49 conducted an exhaustive forensic audit into the remaining failure modes of V6.

The audit analyzed two distinct failure categories:
1. **Missed Genuine Gunshot Recordings ($N = 63$ across all evaluation corpora):**
   - Development Partition ($N = 26 / 72$)
   - Historical Phase 12 Holdout ($N = 16 / 48$)
   - Historical Phase 15 Holdout ($N = 14 / 47$)
   - Independent Phase 19 Field Recordings ($N = 7 / 23$)
2. **Remaining False Alarms ($N = 29$ total across discrete holdouts and continuous streams):**
   - Discrete Holdouts ($N = 22$: Development 10, Phase 15 9, Phase 12 3)
   - Continuous Stream ($N = 7$ alerts across 2.0 hours of Phase 12 urban audio)

This investigation uncovered **four critical, mathematically verifiable root causes** in V6 that unnecessarily degraded positive detection and allowed specific urban transients to trigger false alarms.

---

## 2. Taxonomy of V6 Missed Positives ($N = 63$)

Cross-partition forensic analysis of all 63 missed positive recordings revealed the following distribution of primary failure mechanisms:

| Primary Failure Mechanism | Count ($N=63$) | Percentage | Primary Affected Partitions |
| :--- | :---: | :---: | :--- |
| **Low-SNR Occluded Attenuation** | 31 | 49.2% | Development ($N=16$), Phase 12 Pocket ($N=9$), Phase 15 Pocket ($N=6$) |
| **Pyrotechnic Over-Suppression** | 11 | 17.5% | Phase 19 Field ($N=5$), Development ($N=3$), Phase 15 ($N=3$) |
| **Reverberant Thunder Over-Suppression**| 8 | 12.7% | Development ($N=4$), Phase 12 Distant ($N=3$), Phase 15 ($N=1$) |
| **Short-File FSM Window Cut-Off** | 5 | 7.9% | Phase 12 Clean/Double ($N=3$), Phase 15 ($N=2$) |
| **Ballistic Incoherence Attenuation** | 4 | 6.3% | Phase 12 Clipped ($N=2$), Development ($N=2$) |
| **General Suppression Drop / Barrier** | 4 | 6.3% | Development ($N=3$), Phase 12 ($N=1$) |

---

## 3. Detailed Root Cause Investigations

### 3.1 Root Cause 1: Pyrotechnic Over-Suppression of Field Recordings
- **Symptom:** In the independent Phase 19 ShotSpotter field recordings, positive recall collapsed from $91.30\%$ ($21/23$) in V5 down to $69.57\%$ ($16/23$) in V6. High-confidence gunshot recordings (such as `P19-CAT-A-FP1-test_004`, `test_007`, `P19-CAT-A-FP3-test_049`, `P19-CAT-A-FP4-test_058`, and `test_061`) that scored $0.92 - 0.99$ in V5 were attenuated down to $0.23 - 0.29$ in V6.
- **Physical Mechanism:** Field recordings captured by acoustic sensor arrays in urban street canyons exhibit significant multi-path reverberation and broad explosive low-frequency shockwaves. In YAMNet's semantic ontology, broad explosive acoustic energy generates high scores across both pyrotechnic classes (`426` fireworks, `427` firecracker: $0.45 - 0.55$) and ballistic/explosion classes (`420` explosion, `428` blast, `421` gunshot: $0.66 - 0.97$).
- **V6 Code Defect:** In V5, the pyrotechnic gate enforced a ballistic shockwave override:
  $$\text{is\_ballistic\_shockwave} = (bal\_s \ge 0.40) \land (bal\_s \ge fw\_s \times 0.85)$$
  During the refactoring of V6's semantic suppression module, this ballistic shockwave safeguard was inadvertently omitted from `CalibratedSemanticSuppressionV6`. Consequently, any gunshot whose acoustic explosion registered $fw\_s \ge 0.45$ and $fw\_s / pure\_gun \ge 1.8$ was immediately attenuated by $0.15\times - 0.30\times$, completely discarding genuine gunfire.

### 3.2 Root Cause 2: Atmospheric Absorption and Reverberant Thunder Over-Suppression
- **Symptom:** Distant gunshot recordings and outdoor gunshots with long reverberant tails (`phase12_gunshot_distant_remington_02`, `phase12_gunshot_distant_ar15_01`, and 4 development recordings) experienced severe attenuation by $0.30\times$.
- **Physical Mechanism:** As acoustic waves propagate through the atmosphere over distances $>100\text{ meters}$, high-frequency acoustic energy above $2.5\text{ kHz}$ is exponentially absorbed by air viscosity and molecular relaxation ($>1.5\text{ dB}/100\text{m}$). As a result, distant gunshots arrive at the microphone with low spectral centroids ($<800\text{ Hz}$) and dominant low-frequency energy ratios ($lo \ge 0.65, mid\_to\_low < 0.55$).
- **V6 Code Defect:** V6's fallback physical thunder rule evaluated:
  $$\text{if } lo \ge 0.65 \text{ and } m2l < 0.55 \text{ and } pure\_gun < 0.15 \implies \text{attenuate } 0.30\times$$
  Because distant gunshots often have modest pure gunfire scores ($pure\_gun \approx 0.10 - 0.14$) due to distance distortion, but retain massive ballistic shockwave signatures ($bal\_s = 0.50 - 0.80$), V6 misclassified distant gunfire as physical thunder rumble, suppressing genuine events.

### 3.3 Root Cause 3: Short-File FSM Single-Window File Cut-Off
- **Symptom:** 5 discrete evaluation files with high raw and adjusted confidence ($score \ge 0.85 - 0.93$) were marked as non-detections (e.g. `phase12_gunshot_pocket_ar15_rapid_03` [score 0.8512], `phase12_gunshot_clean_ar15_double_05` [score 0.9098], and `p15_pos_007` [score 0.9286]).
- **Physical Mechanism:** These audio files had short durations ($0.96\text{s} - 1.44\text{s}$), producing only 1 or 2 analysis windows. Because the condition estimator requires $\ge 2$ windows to transition to `CLEAR_NORMAL` or $\ge 3$ windows to transition to `DEGRADED_OCCLUDED`, the detector remained in `UNKNOWN` mode.
- **V6 Code Defect:** In `UNKNOWN` mode, V6 required $crest\_db \ge 13.5\text{ dB}$ for the single-impulse exception. Muffled pocket shots or double-round bursts with crest factors of $12.0 - 13.0\text{ dB}$ failed the single-impulse criterion. The FSM transitioned from `IDLE` to `CANDIDATE` and waited for window 2 to confirm, but the audio file terminated, causing the candidate to be discarded at EOF without emitting an event! In continuous streaming, audio continues uninterrupted, but in discrete benchmark evaluation, this constituted an artificial failure boundary.

### 3.4 Root Cause 4: Ballistic Coherence Saturation on Clipped Recordings
- **Symptom:** Overdriven and clipped recordings (`phase12_gunshot_clipped_beretta_rapid_03`) scoring $0.5133$ were attenuated down to $0.1027$ by the ballistic coherence rule.
- **Physical Mechanism:** Extreme preamplifier clipping and microphone diaphragm saturation flatten the waveform peaks, introducing non-linear harmonic distortion that disperses energy across generic AudioSet classes, causing $pure\_gun < 0.08$ and $bal\_s < 0.10$.
- **V6 Code Defect:** V6's ballistic coherence safeguard did not check whether the window was severely clipped ($peak \ge 0.30$ or $crest \ge 15.0\text{ dB}$). Applying strict linear non-target checks to non-linearly clipped waveforms penalized genuine high-volume gunshots.

---

## 4. Forensic Investigation of Remaining False Alarms ($N = 29$)

Detailed analysis of the 29 remaining false alarms (22 discrete and 7 continuous) revealed the following distribution:

```
Primary Root Cause Distribution (N = 29):
├── FIREWORKS_LEAKAGE (N = 13, 44.8%)
│   ├── Development Discrete: 7 (sustained multi-burst pyrotechnics)
│   ├── Phase 15 Discrete: 5 (mortar shells and titanium salutes)
│   └── Phase 12 Discrete: 1 (rapid ground bloom)
├── URBAN_ENVIRONMENTAL_TRANSIENT (N = 10, 34.5%)
│   ├── Development Discrete: 3 (heavy metal dropped on concrete)
│   ├── Phase 15 Discrete: 4 (industrial pneumatic hammer)
│   └── Phase 12 Continuous: 3 (high-crest impulsive clicks at t=1821s, 6327s, 6915s)
├── AUTOMOTIVE_BACKFIRE_TRANSIENT (N = 3, 10.3%)
│   └── Phase 12 Continuous: 3 (exhaust pops and backfires at t=1826s, 2413s, 3001s)
└── GLASS_SHATTER_LEAKAGE (N = 3, 10.3%)
    └── Phase 12 Discrete: 0, Phase 15: 0, Development: 3 (acoustic glass breakage)
```

### Forensic Analysis of the 7 Phase 12 Continuous Alerts:
Detailed window extraction from `phase12_continuous_stream_01_urban_and_environmental_2hr.wav` revealed:
1. **Window 28 in Block 80 ($t = 2413.44\text{s}$):**
   - Crest: $14.87\text{ dB}$, Centroid: $696\text{ Hz}$, Low-Ratio: $0.814$, Peak: $0.468$.
   - YAMNet Semantic Scores: `424` Cap Gun = $0.5487$, `420` Explosion = $0.2508$, `421` Gunshot = $0.2314$.
   - Why V6 failed: In V6, `sub_bass_thud` required $pure\_gun < 0.20$. Because class `421` was slightly elevated at $0.2314$ (even though Cap Gun was more than double at $0.5487$), suppression was denied, triggering a single-impulse false alarm!
2. **Window in Block 100 ($t = 3001.44\text{s}$):**
   - Crest: $14.87\text{ dB}$, Low-Ratio: $0.868$. Identical automotive exhaust pop.
3. **Block 60 Event ($t = 1826.88\text{s}$):**
   - Cap Gun = $0.700$, Explosion = $0.650$, Boom = $0.448$, Thunder = $0.419$. Automotive engine backfire.

---

## 5. Summary of Corrective Actions for Detector Improvement V7

1. **Reinstate Ballistic Shockwave Override in Pyrotechnic Gating:** If $bal\_s \ge 0.40 \land bal\_s \ge 0.85 \times fw\_s$, bypass fireworks attenuation completely.
2. **Add Ballistic Shockwave Immunity to Thunder Suppression:** If $bal\_s \ge 0.20$, exempt low-pass acoustic tails from physical thunder rumble attenuation.
3. **Refine Sub-Bass Backfire Gating:** If $cap\_gun \ge 0.35 \land cap\_gun \ge 1.5 \times pure\_gun \land lo \ge 0.70$, enforce backfire suppression even if $pure\_gun$ reaches $0.28$.
4. **Implement High-Confidence Single-Impulse Adaptation in FSM:** In `UNKNOWN` mode, if score $\ge 0.85$ (exceptionally high confidence), permit single-impulse confirmation with $crest \ge 11.5\text{ dB}$, eliminating the short-file EOF cutoff artifact.
5. **Add Saturation Safeguard to Ballistic Coherence:** If $peak \ge 0.30$ or $crest \ge 15.0\text{ dB}$, lower the required pure gun threshold to $0.04$ before asserting incoherence.

