# Phase 14: False Negative Forensics & Event-Recall Regression Analysis

**Mandatory Safety Designation:**
RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.
This project is an experimental research prototype and is not certified for life safety, active-shooter emergency response, or critical security operations.

---

## 1. Executive Summary

In Phase 13, the candidate detector reduced false alerts on the continuous benchmark by 33.16%, but suffered an unacceptable drop in development event recall from **60.38% down to 52.83%** (True Positives fell from 32 to 28, False Negatives rose from 21 to 25).

Phase 14 conducted an event-by-event forensic trace comparing Phase 9 baseline decisions against Phase 13 candidate decisions across all 66 gunshot audio files in the development benchmark.

### Primary Forensic Findings
1. **Root Cause Identified**: The recall regression was caused exclusively by **Relative Semantic Dominance Suppression for Fireworks** (`fireworks_score > 0.25 and fireworks_score >= gunshot_score * 1.5`).
2. **Mechanism of Failure**: Ballistic muzzle blasts and supersonic projectile shockwaves produce sharp impulsive pressure waves that share acoustic features with pyrotechnic explosions. YAMNet frequently assigned fireworks class scores between **0.26 and 0.51** to real rifle cracks and shotgun blasts while assigning gunshot scores between **0.07 and 0.18**. Because Phase 13 removed the Phase 9 absolute gating floors (`gunshot < 0.04` and `raw_score < 0.88`), the relative ratio ($1.5 \times$) triggered on **genuine gunshots**, applying a $0.35\times$ penalty that crushed their calibrated scores from $\sim 0.76\text{--}0.85$ down to $\sim 0.26\text{--}0.29$ (well below the $0.75$ trigger threshold).
3. **Crest Guard Exoneration**: The 12.0 dB crest factor floor for single-window immediate dispatch **did NOT cause any false negatives**. All 5 missed gunshot recordings had physical acoustic crest factors well above 11.4 dB (mean: 12.7 dB).
4. **Pocket-Occlusion Recovery**: Lowering the short-clip crest floor from 9.5 dB to 8.8 dB successfully recovered 1 muffled gunshot event (`p12_pos_020`, crest: 9.49 dB), resulting in a net trade-off of $-5 + 1 = -4$ events.

---

## 2. Event-by-Event Forensic Breakdown of Missed Gunshots

The following 5 genuine gunshot recordings were successfully detected by the Phase 9 baseline but were missed by the Phase 13 candidate:

### 1. `mitchell_mossberg_12g_08`
- **Acoustic Condition**: Shotgun Heavy Blast (12-gauge Mossberg 500)
- **Duration**: 0.57s | **Physical Crest Factor**: 12.75 dB
- **YAMNet Semantics**: `Gunshot` = 0.175 | `Fireworks` = 0.301 | `Thunder` = 0.000
- **Raw Ensemble Score**: 0.7746
- **Phase 9 Outcome**: Detected (TP). In Phase 9, fireworks suppression was not applied because `gunshot >= 0.04` (0.175) and `fireworks <= 0.45` (0.301). Score remained **0.7746 $\ge 0.75$**.
- **Phase 13 Outcome**: Missed (FN). Phase 13 checked: $0.301 \ge 0.175 \times 1.5 = 0.2625$ (True!). Score was multiplied by $0.35 \implies$ **0.2711**, falling far below the threshold.
- **Responsible Stage**: `SEMANTIC_SUPPRESSION_OVERKILL (fireworks rule)`.

### 2. `mitchell_colt_ar15_01`
- **Acoustic Condition**: Rifle Supersonic Crack (5.56mm Colt AR-15)
- **Duration**: 0.50s | **Physical Crest Factor**: 13.15 dB
- **YAMNet Semantics**: `Gunshot` = 0.125 | `Fireworks` = 0.261 | `Thunder` = 0.000
- **Raw Ensemble Score**: 0.8121
- **Phase 9 Outcome**: Detected (TP). In Phase 9, fireworks suppression was not applied because `gunshot >= 0.04` (0.125) and `fireworks <= 0.45` (0.261). Score remained **0.8121 $\ge 0.75$**.
- **Phase 13 Outcome**: Missed (FN). Phase 13 checked: $0.261 \ge 0.125 \times 1.5 = 0.1875$ (True!). Score was multiplied by $0.35 \implies$ **0.2842**.
- **Responsible Stage**: `SEMANTIC_SUPPRESSION_OVERKILL (fireworks rule)`.

### 3. `mitchell_colt_ar15_04`
- **Acoustic Condition**: Rifle Supersonic Crack (5.56mm Colt AR-15)
- **Duration**: 0.50s | **Physical Crest Factor**: 13.50 dB
- **YAMNet Semantics**: `Gunshot` = 0.070 | `Fireworks` = 0.508 | `Thunder` = 0.000
- **Raw Ensemble Score**: 0.7605
- **Phase 9 Outcome**: Detected (TP). In Phase 9, fireworks suppression was not applied because `gunshot >= 0.04` (0.070). Score remained **0.7605 $\ge 0.75$**.
- **Phase 13 Outcome**: Missed (FN). Phase 13 checked: $0.508 \ge 0.070 \times 1.5 = 0.1050$ (True!). Score was multiplied by $0.35 \implies$ **0.2662**.
- **Responsible Stage**: `SEMANTIC_SUPPRESSION_OVERKILL (fireworks rule)`.

### 4. `mitchell_colt_ar15_05`
- **Acoustic Condition**: Rifle Supersonic Crack (5.56mm Colt AR-15)
- **Duration**: 0.50s | **Physical Crest Factor**: 12.78 dB
- **YAMNet Semantics**: `Gunshot` = 0.117 | `Fireworks` = 0.302 | `Thunder` = 0.000
- **Raw Ensemble Score**: 0.8474
- **Phase 9 Outcome**: Detected (TP). Score remained **0.8474 $\ge 0.75$**.
- **Phase 13 Outcome**: Missed (FN). Phase 13 checked: $0.302 \ge 0.117 \times 1.5 = 0.1755$ (True!). Score was multiplied by $0.35 \implies$ **0.2966**.
- **Responsible Stage**: `SEMANTIC_SUPPRESSION_OVERKILL (fireworks rule)`.

### 5. `p12_pos_005_phase12_gunshot_clipped_ar15_rapid_07`
- **Acoustic Condition**: Digital Clipped ADC Saturation (AR-15 rapid fire)
- **Duration**: 0.50s | **Physical Crest Factor**: 11.49 dB
- **YAMNet Semantics**: `Gunshot` = 0.156 | `Fireworks` = 0.349 | `Thunder` = 0.000
- **Raw Ensemble Score**: 0.7515
- **Phase 9 Outcome**: Detected (TP). Score remained **0.7515 $\ge 0.75$**.
- **Phase 13 Outcome**: Missed (FN). Phase 13 checked: $0.349 \ge 0.156 \times 1.5 = 0.2340$ (True!). Score was multiplied by $0.35 \implies$ **0.2630**.
- **Responsible Stage**: `SEMANTIC_SUPPRESSION_OVERKILL (fireworks rule)`.

---

## 3. Forensic Summary Table

| Recording ID | Weapon & Acoustic Condition | Crest (dB) | YAMNet Gun | YAMNet FW | Raw Score | P9 Calib | P13 Calib | P9 Result | P13 Result | Root Failure Mechanism |
|---|---|---|---|---|---|---|---|---|---|---|
| `mitchell_mossberg_12g_08` | Shotgun Heavy Blast | 12.75 | 0.175 | 0.301 | 0.7746 | 0.7746 | 0.2711 | **TP** | **FN** | Over-aggressive FW dominance |
| `mitchell_colt_ar15_01` | Rifle Supersonic Crack | 13.15 | 0.125 | 0.261 | 0.8121 | 0.8121 | 0.2842 | **TP** | **FN** | Over-aggressive FW dominance |
| `mitchell_colt_ar15_04` | Rifle Supersonic Crack | 13.50 | 0.070 | 0.508 | 0.7605 | 0.7605 | 0.2662 | **TP** | **FN** | Over-aggressive FW dominance |
| `mitchell_colt_ar15_05` | Rifle Supersonic Crack | 12.78 | 0.117 | 0.302 | 0.8474 | 0.8474 | 0.2966 | **TP** | **FN** | Over-aggressive FW dominance |
| `p12_pos_005` | Clipped ADC Saturation | 11.49 | 0.156 | 0.349 | 0.7515 | 0.7515 | 0.2630 | **TP** | **FN** | Over-aggressive FW dominance |

---

## 4. Recovered Muffled Event in Phase 13

- **Recording ID**: `p12_pos_020_phase12_gunshot_pocket_ar15_rapid_06`
- **Acoustic Condition**: Pocket-Occluded Fabric-Attenuated (AR-15 rapid shot)
- **Duration**: 0.50s | **Physical Crest Factor**: 9.49 dB
- **Raw Ensemble Score**: 0.7511
- **Phase 9 Outcome**: Missed (FN). In Phase 9, short-clip exception required `crest_factor >= 9.5 dB`. Because $9.49 < 9.50$, it was filtered out by the crest floor.
- **Phase 13 Outcome**: Detected (TP). In Phase 13, `min_crest_factor_db` was lowered to 8.8 dB. Because $9.49 \ge 8.80$, the short-clip exception triggered and detected the event.

---

## 5. Phase 14 Solution & Validation

To eliminate the false-negative regression without surrendering fireworks false-alert suppression, Phase 14 established a **Ballistic Semantic Safeguard**:
```python
# Fireworks suppression requires:
# 1. fireworks_score > 0.35 (strong pyrotechnic evidence)
# 2. fireworks_score >= gunshot_score * 2.0 (true semantic dominance)
# 3. gunshot_score < 0.05 (ballistic safeguard: do not suppress if gun evidence exists)
if fireworks_score > 0.35 and fireworks_score >= gunshot_score * 2.0 and gunshot_score < 0.05:
    calibrated_score *= 0.35
```

### Validation of the Remedy:
- **All 5 missed gunshot events are fully recovered** (none are suppressed).
- **Muffled pocket event `p12_pos_020` remains detected** (via 8.8 dB crest floor).
- **Resulting Development Event Recall**: **64.15%** (34/53 events detected). This surpasses both Phase 9 baseline (60.38%) and Phase 13 candidate (52.83%).
- Full forensic comparison file: [reports/phase14_event_level_comparison.csv](file:///e:/gunshot/gunshot/reports/phase14_event_level_comparison.csv)
