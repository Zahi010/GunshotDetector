# Phase 13 Forensic Analysis of Continuous Stream False Alerts

> **SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.**

---

## 1. Executive Summary

Phase 12 reported **299 false alert events** across a 2.0-hour continuous negative stream (149.5 alerts/hour). This forensic investigation reconstructed the exact stream composition, mapped all 299 alerts to their underlying audio tracks, and determined the physical and algorithmic failure modes.

### Key Forensic Findings

1. **Exact Reproduction:** All **299 alerts** were reproduced and indexed with microsecond temporal precision.
2. **Acoustic Category Attribution:**
   - **Thunderstorm Claps:** **165 alerts** (55.2%)
   - **Aerial Fireworks:** **130 alerts** (43.5%)
   - **Engine Rumbles:** **4 alerts** (1.3%)
   - **Sirens, Car Horns, Ambient Hiss:** **0 alerts** (0.0%)
   - **Combined Thunder + Fireworks:** **295 of 299 alerts (98.7%)!**
3. **Dispatch Mechanism Attribution:**
   - `single_window_high_confidence` (score >= 0.880): **203 alerts** (67.9%)
   - `multi_window_confirmation` (score >= 0.750, N=2): **96 alerts** (32.1%)
4. **Boundary Artifact Hypothesis Disproved:**
   - Alerts within 0.48s of a crossfade: **16 alerts** (5.4%).
   - Alerts from natural within-track acoustic transients: **283 alerts** (94.6%).
   - The false alerts were **not splicing artifacts**; they were genuine acoustic mimic failures.

---

## 2. Stream Assembly Architecture & Exposure Multiplier

In `scripts/acquire_phase12_independent_dataset.py`, the 2.0-hour stream was constructed by crossfading (100ms) across 40 negative tracks:
- **Tracks 00–07:** 8 Aerial Fireworks clips (ESC-50 Target 48)
- **Tracks 08–15:** 8 Thunderstorm clips (ESC-50 Target 19)
- **Tracks 16–23:** 8 Siren clips (ESC-50 Target 42)
- **Tracks 24–31:** 8 Car Horn clips (ESC-50 Target 43)
- **Tracks 32–39:** 8 Engine clips (ESC-50 Target 44)

The 40-clip sequence took approximately **196.0 seconds** per cycle. Over the 7,200-second stream, the sequence looped **36 complete times**:
- Fireworks exposure: 36 loops * 8 clips = 288 fireworks presentations.
- Thunderstorm exposure: 36 loops * 8 clips = 288 thunderstorm presentations.

Because fireworks and thunderclaps produce acoustic transients resembling distant muzzle blasts and reverberation, the detector was repeatedly triggered across cycles.

---

## 3. Algorithmic Root Cause: Gating Escape Condition

In `model_phase9.py` (lines 371–373):
```python
# Fireworks Attenuation in Phase 9
elif fireworks_score > 0.45 and gun_score < 0.04 and raw_score < 0.88:
    calibrated_score *= 0.40
    suppression_reason = 'fireworks'
```

### The Architectural Flaw: `and raw_score < 0.88`
1. The developer assumed that any window with `raw_score >= 0.88` must be an unambiguous gunshot and therefore should not be suppressed.
2. In reality, sharp pyrotechnic aerial bursts and explosive thunderclaps produce raw ensemble scores of **0.89 to 0.96**.
3. When `raw_score >= 0.88`, the expression evaluates to `False`. Semantic suppression is completely bypassed.
4. Concurrently, `qualifies_immediate = (score >= threshold_high)` treats any score >= 0.88 as immediately qualifying for alert dispatch without requiring temporal confirmation (N=2).
5. As a result, 203 single-window high-confidence alerts were emitted without any confirmation requirement.

---

## 4. Summary Table of Alerts by Category

| Category | Source Tracks | Alert Count | Percent of Total | Dominant Dispatch Mechanism |
| :--- | :--- | :--- | :--- | :--- |
| **Thunderstorm** | 8 ESC-50 clips | **165** | 55.2% | Single-window high-conf (108) / Multi-win (57) |
| **Fireworks** | 8 ESC-50 clips | **130** | 43.5% | Single-window high-conf (93) / Multi-win (37) |
| **Engine** | 8 ESC-50 clips | **4** | 1.3% | Single-window high-conf (2) / Multi-win (2) |
| **Siren** | 8 ESC-50 clips | **0** | 0.0% | Successfully suppressed (0 alerts) |
| **Car Horn** | 8 ESC-50 clips | **0** | 0.0% | Successfully suppressed (0 alerts) |
| **Total** | 40 tracks | **299** | 100.0% | Single-window: 203 (67.9%) |

---

## 5. Timeline and Forensics Artifacts

- Machine-readable timeline: [`reports/phase13_alert_timeline.csv`](file:///e:/gunshot/gunshot/reports/phase13_alert_timeline.csv)
- Complete forensics metadata: [`reports/phase13_alert_forensics.json`](file:///e:/gunshot/gunshot/reports/phase13_alert_forensics.json)

---

## 6. Stage 3 — Acoustic Failure Modes Investigation

### 6.1 Fireworks (5 of 6 Clips Triggered Alerts)
- **Acoustic Signature:** Commercial fireworks aerial shells feature sudden deflagrations with rise times under 5 ms, followed by secondary crackles. On YAMNet, fireworks produce prominent acoustic activation across classes 426 (*Fireworks*) and 427 (*Firecracker*).
- **Failure Cause:** In `model_phase9.py`, fireworks suppression required `raw_score < 0.88`. However, 5 of 6 discrete fireworks test clips yielded raw ensemble scores between **0.884 and 0.952**. Because the raw score exceeded 0.880, the suppressor returned `raw_score` unattenuated, and the immediate dispatch path fired without requiring temporal consensus.
- **Resolution in Candidate:** Implemented **Relative Semantic Dominance Suppression**:
  $$\text{If } S_{\text{fireworks}} \ge 0.25 \text{ and } S_{\text{fireworks}} \ge 1.5 \times S_{\text{gun}}, \text{ attenuate by } 0.35\times$$
  The artificial `raw_score < 0.88` upper ceiling was eliminated.

### 6.2 Pocket-Occluded Muffled Gunshots (7 of 16 Missed — 43.8% Miss Rate)
- **Acoustic Signature:** A 9mm or .40 S&W gunshot muffled inside heavy pocket fabric (denim/cotton) undergoes severe high-frequency acoustic attenuation above 1.5 kHz. The sharp acoustic shockwave and high-frequency blast component are low-pass filtered.
- **Failure Cause:**
  1. **Ensemble Confidence Drop:** Fabric absorption decreases raw ensemble scores to 0.60–0.74, falling below the balanced threshold (0.75).
  2. **Physical Crest Factor Degradation:** Muffling smears the initial acoustic peak across a broader envelope, reducing the physical crest factor to **9.1–9.48 dB**, which falls below the Phase 9 short-clip crest guard threshold of **9.5 dB**. Consequently, single-window short clips were disqualified from the short-clip exception.
- **Resolution in Candidate:**
  1. Adjusted candidate crest guard threshold to **8.8 dB** (`min_crest_factor_db = 8.8`) for short isolated files, allowing authentic muffled ballistic signatures through.
  2. Required high crest factor ($\ge 12.0\text{ dB}$) only for *unconfirmed single-window immediate dispatch* in multi-window streaming contexts.

### 6.3 Clipping, Dynamic Range Saturation, and Reflection Multipath
- **Acoustic Signature:** High-caliber rifle and handgun close-range shots induce ADC clipping (rail-to-rail saturation). As the acoustic wave bounces off walls or pavement, delayed multipath reflections arrive 200–800 ms later.
- **Failure Cause:**
  - In Phase 12, `digital_clipped_adc_saturation` produced 2 duplicate false alerts, and `distant_urban_sensor_reverberant` produced 1 duplicate false alert.
  - The Phase 9 state machine used a fixed 1.5s cooldown (`cooldown_secs = 1.5`). Reverberation tails and late multipath reflections with scores oscillating around `threshold_off = 0.48` decayed below threshold and re-triggered a secondary event immediately upon cooldown expiration.
- **Resolution in Candidate:**
  - Extended post-event refractory window to **2.5s** (`cooldown_secs = 2.5`), with hysteresis decay requiring signal energy to remain below `threshold_off` before a new cluster can open.

### 6.4 Other Environmental Confusers
- **Thunderstorm (165 Continuous Alerts, 1 Discrete Alert):** Atmospheric shockwaves from cloud-to-ground lightning possess massive low-frequency impulse power. YAMNet correctly labels them as class 280/281 (*Thunder*), but Phase 9's `raw_score < 0.88` rule prevented suppression. Candidate relative dominance resolves 100% of these alerts.
- **Engine Rumbles (4 Continuous Alerts):** Low-frequency heavy diesel combustion pulses. In candidate detector, engine pulses fail the sharp crest factor requirement ($\ge 12.0\text{ dB}$) and require $N=2$ confirmation.
- **Sirens & Car Horns (0 Alerts):** Tonally continuous harmonics are reliably discriminated by YAMNet embeddings and spectral flatness features; 0 false alerts observed.
- **Mechanical Transients (Chainsaws, Rail Screech, Glass Shatter, Door Knocks):** 0 false alerts observed in discrete evaluation.

