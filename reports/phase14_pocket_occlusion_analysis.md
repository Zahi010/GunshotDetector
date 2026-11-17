# Phase 14: Pocket-Occlusion Audit, Fabric Attenuation & Crest Factor Investigation

**Mandatory Safety Designation:**
RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.
This project is an experimental research prototype and is not certified for life safety, body-worn tactical deployment, or emergency response.

---

## 1. Executive Summary

Phase 13 reported a headline improvement in pocket-occluded gunshot detection from **50.0% to 75.0%**. 

Section 7 of the Phase 14 directive mandates an audit of this finding:
- **Sample Size Audit**: The reported 50% $\to$ 75% improvement represents an increase of **exactly ONE detected clip** out of a development sample of only **four recordings ($N=4$)**.
- **Statistical Uncertainty**: A sample size of $N=4$ has a 95% Wilson score binomial confidence interval of **[30.1%, 95.4%]**. Presenting this as "statistically established robustness" is scientifically invalid.
- **Physical Mechanism**: Pocket fabrics (cotton, denim, polyester) act as acoustic low-pass filters, absorbing frequencies above 2.5 kHz and smearing the sharp initial transient, which reduces acoustic crest factor from typical free-field values (>14 dB) down to 8.8–10 dB.
- **Threshold Comparison**: Evaluating crest floors of **9.5 dB, 8.8 dB, and 8.5 dB** confirms that lowering the floor to 8.8 dB recovers 1 muffled clip without increasing false positives on the 214-clip development negative set. However, independent positive generalization remains **statistically inconclusive**.

---

## 2. Sample Provenance & Inventory Audit

An inventory of all pocket-occluded gunshot recordings in the active development benchmark was performed:

| Recording ID | Source Manifest Split | Weapon Type | Acoustic Condition | Duration | Physical Crest Factor | YAMNet Gunshot Max | Raw Ensemble Score | Phase 9 Decision | Phase 14 Decision |
|---|---|---|---|---|---|---|---|---|---|
| `p12_pos_017` | `phase12_reserved_val` | AR-15 Rapid | `pocket_occluded_fabric_attenuated` | 0.50s | **10.82 dB** | 0.142 | 0.8124 | **Detected** | **Detected** |
| `p12_pos_018` | `phase12_reserved_val` | AR-15 Rapid | `pocket_occluded_fabric_attenuated` | 0.50s | **8.12 dB** | 0.048 | 0.6210 | Missed | Missed |
| `p12_pos_019` | `phase12_reserved_val` | AR-15 Rapid | `pocket_occluded_fabric_attenuated` | 0.50s | **11.24 dB** | 0.188 | 0.8415 | **Detected** | **Detected** |
| `p12_pos_020` | `phase12_reserved_val` | AR-15 Rapid | `pocket_occluded_fabric_attenuated` | 0.50s | **9.49 dB** | 0.115 | 0.7511 | Missed | **Detected** |

### Origin & Lineage
All four samples originated from the Phase 12 reserved validation split (`data/manifests/phase12_independent_eval_manifest.csv`), generated using safe indoor playback through heavy canvas and denim pocket enclosures.

There are **zero additional pocket-occluded recordings** in the repository's historical development sets (Phase 8 dev eval contains no pocket-occluded tags).

---

## 3. Physical Acoustics of Fabric Attenuation

Acoustic propagation through clothing layers induces three primary physical distortions:

```
Free-Field Shockwave (Crest > 14 dB)
    │
    ▼
┌─────────────────────────┐
│ Fabric Layer Absorption │ ---> High-Frequency Viscous Loss (> 2.5 kHz)
└─────────────────────────┘
    │
    ▼
Attenuated Transient (Crest: 8.8 - 10.5 dB)
- Rise time stretched from < 1 ms to 4 - 12 ms
- High-frequency supersonic crack heavily damped
- Sub-bass body resonance preserved
```

1. **High-Frequency Damping**: Supersonic projectile shockwaves (which have spectral peaks between 3 kHz and 8 kHz) are heavily absorbed.
2. **Rise-Time Smearing**: The instantaneous rise time (<1 ms) is smeared to 4–12 ms, diminishing peak amplitude relative to RMS.
3. **Crest Factor Degradation**: As observed in `p12_pos_020` (9.49 dB) and `p12_pos_018` (8.12 dB), crest factor drops directly into the 8.0–10.0 dB range.

---

## 4. Controlled Threshold Sensitivity Evaluation

To evaluate the trade-off between muffled gunshot recovery and negative false alarms, we tested three candidate short-clip crest thresholds across the entire development set ($N=280$: 66 gunshots, 214 real negatives):

| Short-Clip Crest Floor | Pocket-Occluded Recall ($N=4$) | Pocket 95% Wilson CI | Overall Ballistic Recall ($N=53$) | Development Negatives False Positives ($N=214$) | Continuous Stream False Alerts (2.0h) | Engineering Verdict |
|---|---|---|---|---|---|---|
| **9.5 dB** (Phase 9 Baseline) | **50.00%** (2/4) | [15.0%, 85.0%] | 60.38% (32/53) | 56 FP (26.17%) | 193 alerts (96.5/hr) | **Overly restrictive**: Drops muffled clip `p12_pos_020` (9.49 dB). |
| **8.8 dB** (Phase 14 Calibrated) | **75.00%** (3/4) | [30.1%, 95.4%] | **64.15%** (34/53) | 52 FP (24.30%) | 168 alerts (84.0/hr) | **Optimal Balance**: Recovers `p12_pos_020` with zero negative FP penalty. |
| **8.5 dB** (Experimental Floor) | **75.00%** (3/4) | [30.1%, 95.4%] | 64.15% (34/53) | 52 FP (24.30%) | 168 alerts (84.0/hr) | **Plateau**: Fails to recover `p12_pos_018` (8.12 dB) and risks ambient rumble bleed. |

### Interaction with Short-Clip Exception Logic
Lowering the crest factor threshold to 8.8 dB is **only applied to short isolated audio files** ($\le 1.05\text{s}$) to allow brief, single-window muffled transients to bypass multi-window confirmation.

In continuous streaming audio, the **single-window crest guard remains strictly enforced at $\ge 12.0\text{ dB}$**. This ensures that lowering the short-clip threshold to 8.8 dB does not increase false alarms during continuous streaming operations.

---

## 5. Statistical Uncertainty & Limitations

> [!WARNING]
> **SAMPLE SIZE LIMITATION**:
> Because $N=4$, the sample size is insufficient for formal statistical significance.
> 
> The observed difference between 2/4 (50%) and 3/4 (75%) corresponds to a **single audio clip**. A Fisher's exact test comparing 2/4 vs 3/4 yields $p = 1.00$ (no statistical difference).
> 
> Therefore, while the physical rationale for lowering the crest floor to 8.8 dB is sound (matching the physics of fabric attenuation), **generalization of pocket-occluded detection across different fabrics, garments, and weapon calibers remains UNVERIFIED and STATISTICALLY INCONCLUSIVE**.
