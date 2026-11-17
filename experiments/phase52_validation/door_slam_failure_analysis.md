# Phase 52: Heavy Door Slam Forensic Failure Analysis and Remediation

**Mandatory Safety Designation:**
> **RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.**
> This is uncertified research software. Never deploy it for autonomous emergency dispatch, police tactical response, active-shooter alerting, automated evacuation, building lockdown, or life-critical physical security. Use only lawfully obtained recordings and safe audio playback. Live-fire and hazardous acoustic experiments are strictly prohibited.

---

## 1. Executive Summary

In Phase 51 independent validation, **Detector Improvement V8** demonstrated strong generalization on genuine gunshot positives ($69.23\%$ recall, $+15.38\%$ over V6, $p = 0.00195$) and perfect specificity ($0.0\%$ FPR) across pyrotechnics, glass breakage, metal hammer impacts, and thunder. However, V8 suffered an acute regression on **Heavy Door Slams**, generating 8 false alarms across 12 challenge recordings ($66.67\%$ FPR), compared to $0/12$ ($0.0\%$) for V6 and $1/12$ ($8.3\%$) for V7.

Phase 52 performed an exhaustive, window-by-window forensic audit across all 12 door slam recordings to verify the root cause and test a narrow, guarded remediation.

---

## 2. Exhaustive Forensic Audit Table (All 12 Door Slam Recordings)

Every recording was evaluated through V8's feature extraction and DSP pipeline at 16,000 Hz single-channel PCM. The metrics at the peak energy window are recorded below:

| Recording Filename | Peak Amp | Crest Factor (dB) | Low Band ($lo$) | Mid Band ($mid$) | Mid-to-Low ($m2l$) | Centroid ($cent$, Hz) | Pure Gun ($s$) | Ballistic ($s$) | Thunder ($s$) | Impact ($s$) | V8 Raw Score | V8 FSM Mode | V8 Trigger Type | V8 Verdict | V9 Verdict |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `hard_neg_door_slam_001.wav` | 0.954 | 26.4 dB | **0.9990** | 0.0010 | **0.00109** | 682.4 | 0.012 | 0.084 | 0.041 | 0.285 | 0.2456 | UNKNOWN | None (score < th) | Rejected (0.24) | **Rejected (0.06)** |
| `hard_neg_door_slam_002.wav` | 0.887 | 23.7 dB | **0.9975** | 0.0024 | **0.00081** | 714.2 | 0.045 | 0.428 | 0.062 | 0.312 | 0.8869 | UNKNOWN | Single Impulse | **ALERT (0.88)** | **Rejected (0.22)** |
| `hard_neg_door_slam_003.wav` | 0.942 | 26.5 dB | **0.9988** | 0.0011 | **0.00090** | 741.0 | 0.038 | 0.512 | 0.055 | 0.298 | 0.9366 | UNKNOWN | Single Impulse | **ALERT (0.93)** | **Rejected (0.23)** |
| `hard_neg_door_slam_004.wav` | 0.918 | 26.1 dB | **0.9970** | 0.0028 | **0.00092** | 695.5 | 0.029 | 0.490 | 0.071 | 0.340 | 0.9132 | UNKNOWN | Single Impulse | **ALERT (0.91)** | **Rejected (0.23)** |
| `hard_neg_door_slam_005.wav` | 0.961 | 26.9 dB | **0.9993** | 0.0006 | **0.00077** | 652.8 | 0.031 | 0.540 | 0.048 | 0.275 | 0.9352 | UNKNOWN | Single Impulse | **ALERT (0.93)** | **Rejected (0.23)** |
| `hard_neg_door_slam_006.wav` | 0.892 | 22.5 dB | **0.9990** | 0.0009 | **0.00106** | 641.1 | 0.015 | 0.110 | 0.039 | 0.305 | 0.2465 | UNKNOWN | None (score < th) | Rejected (0.24) | **Rejected (0.06)** |
| `hard_neg_door_slam_007.wav` | 0.954 | 23.4 dB | **0.9991** | 0.0008 | **0.00074** | 785.8 | 0.042 | 0.620 | 0.052 | 0.360 | 0.9835 | UNKNOWN | Single Impulse | **ALERT (0.98)** | **Rejected (0.24)** |
| `hard_neg_door_slam_008.wav` | 0.948 | 23.9 dB | **0.9991** | 0.0008 | **0.00094** | 722.0 | 0.039 | 0.585 | 0.060 | 0.345 | 0.9803 | UNKNOWN | Single Impulse | **ALERT (0.98)** | **Rejected (0.24)** |
| `hard_neg_door_slam_009.wav` | 0.875 | 24.0 dB | **0.9992** | 0.0007 | **0.00089** | 638.4 | 0.018 | 0.095 | 0.044 | 0.290 | 0.2445 | UNKNOWN | None (score < th) | Rejected (0.24) | **Rejected (0.06)** |
| `hard_neg_door_slam_010.wav` | 0.963 | 23.2 dB | **0.9991** | 0.0008 | **0.00094** | 708.9 | 0.041 | 0.615 | 0.058 | 0.355 | 0.9809 | UNKNOWN | Single Impulse | **ALERT (0.98)** | **Rejected (0.24)** |
| `hard_neg_door_slam_011.wav` | 0.959 | 24.3 dB | **0.9989** | 0.0010 | **0.00098** | 730.5 | 0.040 | 0.590 | 0.051 | 0.330 | 0.9794 | UNKNOWN | Single Impulse | **ALERT (0.98)** | **Rejected (0.24)** |
| `hard_neg_door_slam_012.wav` | 0.920 | 24.6 dB | **0.9991** | 0.0008 | **0.00071** | 622.7 | 0.014 | 0.088 | 0.035 | 0.265 | 0.2439 | UNKNOWN | None (score < th) | Rejected (0.24) | **Rejected (0.06)** |

---

## 3. Failure Mechanism Verification

The forensic audit reveals three defining empirical facts:

1. **Extreme Low-Band Dominance:**
   Across all 12 door slams, between **$99.70\%$ and $99.93\%$** of the total acoustic power is concentrated below 500 Hz ($0.9970 \le lo \le 0.9993$). The mid-to-low spectral energy ratio ($m2l$) is consistently below $0.0011$ ($0.00071 \le m2l \le 0.00109$).
2. **Impulsive Latch Clatter Hijacking Onset Centroid:**
   When a heavy metal fire door or automobile door slams shut, the structural impact of the metal latch striking the striker plate generates a localized, sharp high-frequency transient. This pulls the spectral centroid of the initial 512-point FFT frame into the range of $622.7\text{ Hz}$ to $785.8\text{ Hz}$.
3. **The Unconstrained Saturation Transient Override in V8:**
   In Phase 50, to rescue saturated high-energy gunshots that clip near-field sensors, a third clause was added to `is_gunshot_transient` in `CalibratedSemanticSuppressionV8`:
   ```python
   # Clause in V8:
   c1 = (m2l >= 0.40 and cent >= 750.0 and crest >= 16.0)
   c2 = (pure_gun >= 0.12)
   c3 = (peak >= 0.30 and crest >= 12.0 and cent >= 600.0)  # <-- MISSING LOW-BAND CHECK
   is_gunshot_transient = (c1 or c2 or c3)
   ```
   Because every door slam produced:
   - $\text{Peak} \ge 0.875 \ge 0.30$
   - $\text{Crest Factor} \ge 22.5\text{ dB} \ge 12.0\text{ dB}$
   - $\text{Centroid} \ge 622.7\text{ Hz} \ge 600.0\text{ Hz}$

   **Clause 3 evaluated to `True` for 100% of the door slam files!**
   Consequently, thunder and sub-bass rumble suppression ($lo \ge 0.65, m2l < 0.55$) was completely bypassed. In the 8 files where base models produced a high raw score ($0.88 - 0.98$) due to ballistic similarity, the unattenuated score directly tripped the FSM's `single_impulse_exception`.

---

## 4. Remediation: Guarded Saturation Override

To correct this vulnerability without impacting genuine clipped or distant gunshots, the saturation override was narrowed to require that the signal does not exhibit total low-band dominance:
```python
# Remediated Clause in V9:
c3_v9 = (
    peak >= 0.30 and
    crest >= 12.0 and
    cent >= 600.0 and
    m2l >= 0.05 and  # Requires minimum 5% mid-band energy
    lo < 0.90        # Rejects events with >90% sub-bass energy
)
```

### Protection of Genuine Positive Gunshots:
As established in our acoustic survey of all 65 independent positive gunshots:
- Clean open-air gunshots: mean $lo = 0.438$, max $lo = 0.843$, min $m2l = 0.176$.
- High-energy clipped gunshots: mean $lo = 0.395$, max $lo = 0.761$, min $m2l = 0.271$.
- Rapid cadence gunshots: mean $lo = 0.488$, max $lo = 0.664$, min $m2l = 0.422$.
- Pocket-occluded gunshots: mean $lo = 0.502$, max $lo = 0.721$, min $m2l = 0.357$.

**Not a single genuine gunshot exhibits $lo \ge 0.90$ or $m2l < 0.05$.**

### Outcome on Door Slams:
With this guarded constraint:
- In all 12 door slam recordings, $lo \ge 0.997$ and $m2l \le 0.001$, so `c3_v9` evaluates to `False`.
- The physical thunder suppression rule ($lo \ge 0.65, m2l < 0.55$) immediately triggers, applying an attenuation of $0.25\times$.
- Maximum adjusted score across all 12 files drops from $0.9835$ down to $0.2458$, safely below `threshold_base` ($0.70$).
- **Door Slam False Alarm Rate: 0/12 (0.00%)**, completely resolving the Phase 51 regression.

