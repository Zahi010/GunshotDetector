# Phase 55 — V10 Heuristic Failure Forensic Analysis

**MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.**

*This uncertified research prototype must never be deployed for autonomous emergency dispatch, tactical police response, active-shooter alerting, automated evacuation, building lockdown, or life-critical physical security.*

---

## 1. Executive Summary

In Phase 54 independent qualification testing, Detector Improvement V10 suffered an unacceptable negative challenge False Positive Rate (FPR) of **22.12% (48 false alarms across 217 challenge negative recordings)**, leading to its formal rejection (`OPTION B: NOT QUALIFIED`).

A granular acoustic and algorithmic audit was performed across all 48 false-positive recordings to determine why the handcrafted scalar suppression heuristics in V10 failed to reject these non-gunshot acoustic events.

The audit revealed that **100% of the false positives were caused by fundamental architectural limitations of scalar thresholding**:
1. **Curse of Axis-Aligned Cuts:** Real-world acoustic transients inhabit complex, correlated multidimensional manifolds. Unidimensional threshold checks (e.g., `centroid >= 3400 Hz`, `high_ratio >= 0.70`, `crest_factor >= 12 dB`) fail when non-target acoustic sources vary across recording environments, distances, and microphone transducers.
2. **Pyrotechnic Mimicry:** 45.8% (22/48) of all false positives were fireworks. Supersonic bottle rocket bursts, aerial shells, and mortar blasts possess explosive shockwave onsets indistinguishable in rise time (< 15 ms) and crest factor (> 18 dB) from muffled or small-caliber firearms.
3. **Rescue Rule Side Effects:** The addition of Clause 4 ground-blast rescue heuristics (`c4_ground_blast_rescued`) designed to prevent false negatives on heavy explosive detonations directly inverted suppression decisions on impulsive non-gunshot sounds (such as heavy door slams and close balloon bursts).

---

## 2. False Positive Distribution by Challenge Sub-Category

The 48 false positives are distributed across challenge sound classes as follows:

| Challenge Sub-Category | Total Files in Corpus ($N$) | False Positives ($FP$) | Sub-Category FPR (%) | Primary Acoustic Failure Mechanism |
| :--- | :---: | :---: | :---: | :--- |
| **fireworks_pyrotechnics** | 30 | 22 | **73.33%** | Explosive rise time mimics gunfire; YAMNet semantic head misclassification (`pure_gun` $\ge 0.70$) |
| **thunder_rumbles** | 15 | 6 | **40.00%** | Close lightning/thunder crack impulse satisfies crest factor ($\ge 15\text{ dB}$); low-frequency resonance mimics indoor gunfire |
| **heavy_door_slams** | 15 | 5 | **33.33%** | Heavy acoustic impact produces impulsive low-mid frequency peak; rescues bypass suppression |
| **metal_hammer_impacts** | 15 | 5 | **33.33%** | Ballistic crest factor ($\ge 20-30\text{ dB}$) and sub-millisecond metal ping onset mimics gunshot crack |
| **balloon_bursts** | 7 | 4 | **57.14%** | Spectral centroid ($1544-3360\text{ Hz}$) falls below hardcoded 3400 Hz cutoff; room reverberation elevates low ratio |
| **glass_breakage** | 20 | 3 | **15.00%** | Rolling/shattering bottles yield low YAMNet glass semantic confidence ($< 0.12$) or centroid $< 3000\text{ Hz}$ |
| **bioacoustic_human_vocalizations** | 25 | 2 | **8.00%** | Sudden coughing and baby crying produce sharp transient onsets matching ballistic crest criteria |
| **urban_transit_sirens** | 15 | 1 | **6.67%** | Transit rail/wheel screeches generate transient burst satisfying FSM single impulse criteria |
| **Total Negatives** | **217** | **48** | **22.12%** | **Combined Benchmark FPR** |

---

## 3. Deep Forensic Breakdown of Failure Mechanisms

### 3.1 Balloon Burst Heuristic Failure (4 False Positives out of 7)
In V10, balloon burst suppression was implemented using the following rule:
```python
if not supp["suppressed"] and pure_gun < 0.35:
    if cent >= 3400.0 and hi >= 0.70 and lo <= 0.015:
        adj_score *= 0.25
        supp["suppressed"] = True
        cat = "balloon_burst_impulse"
```
**Why it failed:**
- **In-the-wild Spectral Variations:** The rule assumed balloon bursts possess extreme high frequencies (`cent >= 3400 Hz`, `hi >= 0.70`) and negligible bass (`lo <= 0.015`). However, in the Phase 54 independent holdout corpus:
  - File `408103` (*Balloon Popping.wav*): `cent = 3360.1 Hz` (missed by 40 Hz!), `hi = 0.507` (below 0.70), `lo = 0.0779` (exceeds 0.015).
  - File `403570` (*Balloon_Pop.wav*): `cent = 2570.3 Hz`, `hi = 0.155`, `lo = 0.388`.
  - File `326658` (*Wet thump or splash*): `cent = 3788.4 Hz`, `hi = 0.632` (below 0.70), `lo = 0.0944` (exceeds 0.015).
  - File `400801` (*balloon .wav*): `cent = 1544.3 Hz`, `hi = 0.0028`, `lo = 0.9952`. In addition, this recording triggered `c4_ground_blast_rescued`, which actively unsuppressed it!
- **Conclusion:** Balloon acoustics depend heavily on room volume, balloon membrane thickness, distance, and microphone polar response. Scalar bounds on centroid and band energy are fundamentally brittle.

### 3.2 Fireworks & Pyrotechnics Heuristic Failure (22 False Positives out of 30)
In V9/V10, fireworks suppression relied on combustion rise time (`rise_time > 0.035 s`) and spectral low-frequency energy ratios.
**Why it failed:**
1. **Explosive Detonation Physics:** Aerial fireworks shells and bottle rockets do not exhibit slow combustion; they detonate with black powder or flash powder charges yielding shockwave rise times < 15 ms, exactly matching the explosive rise times of firearms.
2. **Semantic Model Confusion:** In 13 out of 22 fireworks false positives, the YAMNet semantic head produced elevated `pure_gun` class activations:
   - File `60905` (*bottleRockets3.wav*): `pure_gun = 0.8979`, `raw_score = 0.8658`.
   - File `56579` (*fireworks 3bursts sizzle.wav*): `pure_gun = 0.8563`, `raw_score = 0.9163`.
   - File `253605` (*Fireworks-close-01nov2014.wav*): `pure_gun = 0.7026`, `raw_score = 0.9167`.
   Because `pure_gun >= 0.35`, the heuristic filters specifically ignored them, believing them to be genuine gunshots.
3. **Distant Firework Acoustic Rolloff:** In 9 recordings, the sound was from distant fireworks (`sw_Fireworks_Distant_01`, `02`, `03`, `06`, `07`, `192659`). The high frequencies were attenuated by atmospheric absorption (`hi < 0.01`, `cent = 584 - 1392 Hz`), creating low-frequency rumbles that passed through the crest factor check (`crest = 15.5 - 32.7 dB`) and bypassed combustion heuristics.

### 3.3 Heavy Door Slams (5 False Positives out of 15)
- Impulsive door slams (e.g., `425676`, `393374`, `386735`, `408046`, `408709`) generate transient mechanical impacts.
- File `408046` (*Lock Unlocking.wav*) had `crest = 30.15 dB`, `cent = 3554.9 Hz`, `hi = 0.6086`. The fusion classifier output a raw score of 0.9511.
- In file `386735` (*Close_Door.wav*), the door slam was initially suppressed as low-frequency rumble, but V10's Clause 4 ground-blast rescue rule (`c4_ground_blast_rescued`) restored the score from suppressed to 0.822 because `cent = 1500 Hz`, `crest = 18.96 dB`, and `peak = 0.73`.

### 3.4 Metal Hammer Impacts (5 False Positives out of 15)
- Heavy hammer strikes on metal plates or spikes (e.g., `351312` *Sledgehammer Hitting Spike*, `344438`, `323795`, `396530`, `127992`) produce sharp, supersonic-like acoustic shocks with crest factors ranging from 16.2 dB to 30.8 dB.
- File `351312` yielded a YAMNet `pure_gun` score of 0.9388 and fusion model score of 0.9579. The model completely failed to recognize the harmonic metallic ringing following the strike because the window-level feature representation flattened temporal ringing into static spectral bands.

### 3.5 Thunder Rumbles (6 False Positives out of 15)
- Rolling thunder and lightning cracks (e.g., `30303`, `121943`, `127127`, `396984`, `37774`, `87963`) possess intense low-frequency energy ($< 250\text{ Hz}$) accompanied by high-frequency acoustic cracks.
- In V10, files like `121943` (*Crackling_thunder_far_away.wav*) exhibited `crest = 20.96 dB`, `cent = 995.3 Hz`, and raw score of 0.8275. Because the base classifier was trained without diverse outdoor thunderclaps, it attributed this acoustic energy to heavy caliber gunfire.

### 3.6 Glass Breakage (3 False Positives out of 20)
- In V10, glass breakage was suppressed if `glass_s >= 0.12` and `cent >= 3000 Hz` and `hi >= 0.30` and `pure_gun < 0.30`.
- Three files bypassed this rule:
  - File `403578` (*Glass_Bottle_Fall_Roll.wav*): `glass_s = 0.418` but `cent = 1022.1 Hz` (a bottle rolling on wood before breaking produces low centroid, failing `cent >= 3000 Hz`).
  - File `98650` (*beer bottle break 2.wav*): `cent = 3347.6 Hz`, `hi = 0.7562`, but `glass_s = 0.054` (below 0.12 threshold).
  - File `343756` (*Glass_Smash.wav*): `cent = 3737.9 Hz`, `hi = 0.7140`, but `glass_s = 0.082` (below 0.12 threshold).
- Hardcoding the semantic threshold to 0.12 caused false positive leakage whenever YAMNet's confidence was mildly attenuated.

---

## 4. The Rescue Rule Paradox

V10 introduced "Clause 4 Ground-Blast Thunder Bypass":
```python
c4_ground_blast = (cent >= 1050.0 and crest >= 16.0 and peak >= 0.35 and pure_gun >= 0.04)
if supp["suppressed"] and "rumble" in cat and c4_ground_blast:
    adj_score = cal_score
    supp["suppressed"] = False
    cat = "c4_ground_blast_rescued"
```
While intended to salvage genuine high-energy C4 or distant artillery gunshots from being suppressed as rumble, this rule caused direct regressions:
1. File `400801` (*balloon .wav*): Ground-truth balloon pop, correctly tagged as rumble/impulse, was un-suppressed by Clause 4 and triggered an alert.
2. File `386735` (*Close_Door.wav*): Heavy door slam, correctly suppressed by acoustic filters, was un-suppressed by Clause 4 and triggered an alert.

This exemplifies the **Rescue Paradox** in rule-based systems: every heuristic override introduced to patch a false negative opens a backdoor for false positives.

---

## 5. Architectural Conclusions & Solution Path

Handcrafted scalar heuristics are no longer viable for this acoustic detection pipeline. They suffer from:
1. **Hyper-Sensitivity to Calibration:** Thresholds tuned on specific audio files inevitably fail when tested on out-of-distribution audio with different acoustics, bitrates, and transducers.
2. **Inability to Learn Complex Decision Boundaries:** Real non-gunshot transients (fireworks, balloons, doors, glass) differ from gunshots across a combination of 10+ acoustic dimensions (attack time, decay envelope, harmonicity, spectral flux, frequency-dependent damping, and semantic logits).
3. **Fragility Under Chaining:** Cascading if-else statements create edge cases and conflicting rules that become impossible to maintain or audit.

**Recommendation:** Replace all scalar suppression heuristics with a **Learned Multi-Feature Rejection Classifier** trained specifically on challenge negative distributions.

