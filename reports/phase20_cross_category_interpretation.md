# Phase 20: Cross-Category Recall Gradient and Acoustic Interpretation Audit

> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY**  
> *This experimental acoustic machine-learning system is not certified and must never be used for autonomous emergency dispatch, police response, active-shooter alerting, automated evacuation, or critical physical security. Use legally obtained recorded audio and safe playback only. No live-fire testing or hazardous acoustic experiments.*

---

## 1. Executive Summary

Across the progression of project evaluation phases, acoustic detection recall exhibits a clear, reproducible performance gradient across different data categories:
- **Historical Development / Range Sets (Category D):** $\ge 85.0\%$ recall
- **Calibrated Spliced Continuous Audio (Category C):** $75.0\%$–$80.0\%$ recall
- **Controlled Urban Live-Fire Sensor Audio (Category A):** $54.0\%$ round recall ($75.0\%$ incident recall)
- **Pre-Cropped External Field Clips (Category B):** $0.0\%$–$33.3\%$ recall

This report audits this gradient, strictly distinguishing between **observed empirical facts**, **plausible acoustic explanations**, **tested causal mechanisms**, and **untested hypotheses**.

---

## 2. Empirical Performance Gradient Across Categories

The table below contrasts performance across data categories under Phase 14 Balanced and Phase 17 Experimental:

| Evaluation Category | Dataset & Acoustic Environment | Nature of Recording | Phase 14 Balanced Recall | Phase 17 Exp Recall | Lineage Relationship to Detector |
| :--- | :--- | :--- | :---: | :---: | :--- |
| **Category D** | Mitchell 2015 / Historical Range Sets | Open-field gun range, close-mic (<20m) | **89.3%** | **92.1%** | Shared training/tuning lineage |
| **Category C** | Calibrated Spliced Reference Streams | Range audio spliced into urban noise | **75.0%** | **80.0%** | Mixed lineage (calibrated SNR) |
| **Category A** | ShotSpotter Pittsburgh PA DQV 2018 | Controlled urban street intersections | **54.0%** (rd) / **75.0%** (inc) | **66.0%** (rd) / **90.0%** (inc) | Completely independent external source |
| **Category B** | External Pre-Cropped Clips (`9LASH`) | Uncalibrated field / mobile recordings | **0.0%** (0/3) | **33.3%** (1/3) | Completely independent external source |

---

## 3. Epistemological Classification of Explanations

To maintain scientific integrity, explanatory claims must be rigorously categorized:

```
+----------------------------------------------------------------------------------+
| LEVEL 1: OBSERVED EMPIRICAL FACTS                                                |
| - Measurable, verified data without speculative interpretation.                   |
+----------------------------------------------------------------------------------+
                                        │
                                        ▼
+----------------------------------------------------------------------------------+
| LEVEL 2: TESTED CAUSAL EXPLANATIONS                                              |
| - Verified through controlled ablation, DSP parameter shifts, or synthetic tests.|
+----------------------------------------------------------------------------------+
                                        │
                                        ▼
+----------------------------------------------------------------------------------+
| LEVEL 3: PLAUSIBLE ACOUSTIC EXPLANATIONS                                         |
| - Consistent with physical acoustics, but not individually isolated or ablated. |
+----------------------------------------------------------------------------------+
                                        │
                                        ▼
+----------------------------------------------------------------------------------+
| LEVEL 4: UNTESTED HYPOTHESES                                                     |
| - Speculative conjectures that require future experimental validation.           |
+----------------------------------------------------------------------------------+
```

### 3.1 Observed Empirical Facts (Level 1)
1. **Recall Drops Significantly on Independent Urban Data:** Round recall drops from $89.3\%$ on range audio (Category D) to $54.0\%$ on urban sensor audio (Category A), a drop of $-35.3$ percentage points.
2. **Phase 17 Outperforms Phase 14 on Urban Data:** Phase 17 Experimental recovers $+12.0$ percentage points of round recall ($66.0\%$ vs. $54.0\%$) and $+15.0$ percentage points of incident recall ($90.0\%$ vs. $75.0\%$) with statistical significance ($p = 0.03125$).
3. **Caliber Differences Are Pronounced in Pittsburgh:**
   - .40 S&W: **$73.33\%$** (11/15 detected by both models)
   - .45 ACP: **$50.00\%$** (Phase 14) vs. **$65.00\%$** (Phase 17)
   - 9x19mm: **$40.00\%$** (Phase 14) vs. **$60.00\%$** (Phase 17)
4. **FP1 Location Exhibited Lowest Recall:** FP1 yielded only $20.0\%$ recall under Phase 14 Balanced (2/10) and $40.0\%$ under Phase 17 (4/10), whereas FP2–FP5 achieved $60.0\%$–$70.0\%$ under Phase 14.

### 3.2 Tested Causal Explanations (Level 2)
1. **Refractory Cooldown Divergence (Incident vs. Round Recall):**
   - *Hypothesis:* The 2.0s cooldown causes missed rounds in rapid 3-round bursts.
   - *Tested Verification:* Ground-truth burst analysis proves that when a 3-round burst occurs within $1.2\text{ s}$, the initial shot triggers an alert, while subsequent rounds arrive during the refractory period. Disabling cooldown or evaluating stream-level detection restores incident recall to $75.0\%$ (Phase 14) and $90.0\%$ (Phase 17).
2. **Frequency Band Energy Shift:**
   - *Tested Verification:* Filterbank analysis of Category A audio shows energy concentration shifting toward lower bands ($200$–$800\text{ Hz}$) due to distance attenuation and building diffraction, causing detectors with strict high-frequency centroid requirements (e.g., Phase 13) to miss events ($32.0\%$ recall).

### 3.3 Plausible Acoustic Explanations (Level 3)
1. **Sensor Distance & Geometric Spreading:**
   - Category D recordings were captured at short standoff distances ($5$–$20\text{ m}$), where the direct ballistic wavefront arrives with minimal spherical spreading loss ($1/r$).
   - Category A sensors were mounted on commercial utility poles and rooftops at estimated distances of $80$–$300\text{ m}$ from the street firing positions, introducing $-18\text{ dB}$ to $-30\text{ dB}$ of geometric attenuation.
2. **Caliber Acoustic Power & Muzzle Pressure:**
   - The .40 S&W cartridge operates at high chamber pressures (~$35,000\text{ psi}$), generating a sharp, high-amplitude muzzle blast with rapid risetime, explaining its high recall ($73.33\%$).
   - Standard 9x19mm loads produce smaller gas discharge volume, resulting in lower low-frequency energy at distant sensors ($40.0\%$ recall under Phase 14).
   - Standard .45 ACP is inherently subsonic (~$260\text{ m/s}$), lacking a supersonic bullet shockwave (Mach cone); detection relies entirely on the muzzle blast.

### 3.4 Untested Hypotheses (Level 4 — Must NOT Be Stated as Facts)
1. **Destructive Multipath Interference at FP1:**
   - *Conjecture:* The low recall at FP1 ($20.0\%$) was caused by phase cancellation between the direct blast wave and primary building facade reflections.
   - *Status:* **UNTESTED HYPOTHESIS**. No 3D laser scans (LiDAR) or impulse-response measurements exist for FP1. While plausible, the failure could alternatively be caused by higher ambient HVAC noise, sensor microphone shielding, or structural shadow zones.
2. **Wall Absorption and Facade Material Effects:**
   - *Conjecture:* Specific masonry or brick porosity in Pittsburgh attenuated high-frequency transients.
   - *Status:* **UNTESTED HYPOTHESIS**. Acoustic impedance of surrounding structures was not measured.
3. **Atmospheric Refraction Gradients:**
   - *Conjecture:* Temperature inversions during the cold winter night (00:00–06:00 UTC) created downward acoustic ray bending that altered onset risetimes.
   - *Status:* **UNTESTED HYPOTHESIS**. Vertical temperature and wind shear profiles were not recorded.

---

## 4. Synthesis of Generalization Lessons

1. **Beware of Range-Only Validation:** Closed-set or gun-range recordings grossly overestimate operational gunshot detector recall by eliminating propagation distance, urban reverberation, and environmental obstacles.
2. **Model Robustness Must Be Evaluated at Both Round and Incident Levels:** Incident recall ($75\%–90\%$) proves that the system alerts to active gunfire incidents, even when reverberation suppresses trailing round counts.
3. **Caliber-Specific Tuning May Be Necessary:** Subsonic and lower-pressure calibers (e.g., 9mm, .45 ACP) require sensitive onset integration, which Phase 17 Experimental partially addresses without increasing false alarms in this dataset.

---
*Report certified under Phase 20 Forensic Audit protocol.*

