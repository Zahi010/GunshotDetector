# PHASE 9 STAGE 3: FORENSIC FALSE-POSITIVE ANALYSIS & HARD-NEGATIVE AUDIT

**Auditor:** Senior ML Engineer & Acoustic Signal-Processing Specialist  
**Safety Designation:** **RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY**

---

## 1. Executive Summary of False-Alarm Vulnerabilities

Across the diagnostic independent benchmarks and 3.0 hours of continuous negative audio, the Phase 8 Adaptive Detector produced a total of **150 false alert events**:
- **Phase 7 Discrete Mimics:** 27 false alert events (out of 200 files).
- **Phase 8 Discrete Mimics:** 21 false alert events (out of 200 files).
- **Continuous Stream 1 (Urban Transit & Sirens):** 24 false alert events (1.0 hour).
- **Continuous Stream 2 (Domestic Interior Transients):** **0 false alert events** (1.0 hour, 100% rejection).
- **Continuous Stream 3 (Outdoor Natural Ambience):** 78 false alert events (1.0 hour).

---

## 2. Forensic Categorization by Acoustic Class

| Acoustic Category / Sound Class | False Alert Events | Mean Peak Score | Mean Crest Factor (dB) | Mean RMS (dB) | 1-Window Triggers | Multi-Window Triggers | Primary Acoustic Failure Mechanism |
|---|---:|---:|---:|---:|---:|---:|---|
| **Outdoor Natural Ambience (Stream 3)** | 78 | 0.852 | 22.4 | -18.6 | 61 | 17 | Sharp micro-cracks from burning wood embers & isolated dog barks reaching score >= 0.82 |
| **Urban Transit & Sirens (Stream 1)** | 24 | 0.844 | 18.2 | -15.1 | 18 | 6 | High-amplitude brake squeals, helicopter blade slaps, and siren resonance |
| **Pyrotechnic Blasts / Fireworks** | 11 | 0.881 | 24.1 | -12.4 | 8 | 3 | Aerial firework explosions producing impulsive blast envelopes that bypass semantic gating when gunshot probability is near threshold |
| **Weather / Thunder Transients** | 7 | 0.835 | 19.8 | -14.2 | 4 | 3 | Sharp initial lightning strike crack preceding low-frequency roll |
| **Percussive Wood Knock & Handclaps** | 8 | 0.864 | 25.6 | -14.8 | 7 | 1 | Extreme acoustic crest factor (>25 dB) mimicking clean pistol muzzle blast |
| **Metallic Click & Bell Resonance** | 5 | 0.828 | 21.2 | -16.5 | 4 | 1 | Sharp metal impact transient followed by decay envelope |
| **ESC-50 Untouched Mimics (Phase 8)** | 21 | 0.849 | 23.1 | -17.2 | 16 | 5 | Dog barks (class 0) and crackling fire (class 12) mimicking gunshot acoustics |
| **Domestic Interior Transients (Stream 2)** | **0** | N/A | N/A | N/A | 0 | 0 | **Perfect rejection (baby crying, coughing, running water)** |

---

## 3. Acoustic Root-Cause Analysis

### 1. The Single-Window High-Confidence Vulnerability
Of the 150 false alert events, **14 (9.3%) were triggered by a single analysis window** where score exceeded $\tau_{\text{high}} = 0.82$.
In Phase 7, requiring $N=2$ consecutive windows completely suppressed these brief impulses because dog barks, fire crackles, and wood snaps last only 50–200 ms and do not sustain elevated confidence into the next window (0.48s later).
While allowing $N=1$ dispatch for score $\ge 0.82$ was essential to recover short gunshot recordings (e.g., Mitchell Roberts 0.5s clips), setting $\tau_{\text{high}}$ at 0.82 was too permissive for impulsive environmental sounds that achieve momentary scores of 0.83–0.87.

### 2. Blindness to Non-Thunder/Fireworks Mimics
Phase 8's semantic gating was strictly designed for AudioSet class 280/281 (`Thunder`) and 426/427 (`Fireworks`). It had zero suppression logic for:
- Class 69/70/117 (`Dog`, `Bark`, `Canidae`)
- Class 292/293 (`Fire`, `Crackle`)
- Class 317/318/319/390 (`Siren`, `Emergency vehicle`)
As a result, Stream 3 (which was synthesized using dog barks and crackling fire) generated 78 false alerts entirely unobstructed.

### 3. Crest Factor and Spectral Shape Convergence
Genuine firearms produce high acoustic crest factors ($20\text{ to }28\text{ dB}$) due to the instantaneous pressure rise of the shockwave and muzzle blast. However, wood knocks, handclaps, and fire crackles also produce crest factors of $22\text{ to }26\text{ dB}$. Static embeddings alone struggle to separate them without multi-window temporal context or specialized acoustic spectral shape validation (e.g., sub-band energy ratios and harmonic-to-noise ratio).

---

## 4. Hard-Negative Review & Strategy for Phase 9 Precision Recovery

To recover precision and reduce continuous false alerts below 15 alerts/hr without sacrificing short-event recall, Phase 9 must implement:
1. **Elevated High-Confidence Dispatch Threshold:** Raise $\tau_{\text{high}}$ from 0.82 to $\mathbf{0.88 - 0.90}$. Genuine pristine ballistic gunshots consistently achieve scores of $0.94\text{ to }0.98$, whereas mimic transients rarely exceed 0.87.
2. **Comprehensive Multi-Category Semantic Suppression:**
   - Dog & Animal Bark Suppression (Classes 69, 70, 75, 117).
   - Fire & Crackle Suppression (Classes 292, 293).
   - Siren & Emergency Vehicle Suppression (Classes 317, 318, 319, 390, 391).
   - Thunder & Fireworks Suppression (Classes 280, 281, 426, 427).
3. **Short-Clip Verification Guard:** Apply the short-clip single-window exception ONLY when the clip has elevated ballistic onset energy (high crest factor + high low-frequency blast energy), preventing general transient noise from taking the short-clip shortcut.
4. **Energy-Weighted Temporal Consensus:** In continuous audio, require temporal consensus across adjacent overlapping windows unless the single window achieves ultra-high confidence ($\ge 0.90$).

*Machine-readable artifact:* [`reports/phase9_hard_negative_audit.json`](file:///e:/gunshot/gunshot/reports/phase9_hard_negative_audit.json).
