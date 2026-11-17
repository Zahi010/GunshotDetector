# PHASE 20 — RECORDING TRANSFORMATION LINEAGE & CONTINUITY AUDIT

> [!CAUTION]
> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.**
> This experimental acoustic machine-learning system is not certified and must never be used for autonomous emergency dispatch, police response, active-shooter alerting, automated evacuation, or critical physical security.
> Use legally obtained recorded audio and safe playback only. No live-fire testing or hazardous acoustic experiments.

---

## 1. Executive Summary

Phase 20 executed an exhaustive forensic signal processing audit to establish the exact physical and digital lineage of the **20 audio streams evaluated in Category A**.
The audit resolved whether these files represent genuine unbroken sensor recordings, cropped test clips, concatenated compilations, or multi-sensor composites.

### Core Audit Verdict:
1. **Source Singularity:** Every one of the 20 Category A audio files is derived from **exactly one original sensor recording** captured by a single municipal acoustic sensor. No multi-sensor mixing or audio channel blending occurred.
2. **Temporal Integrity:** Original source durations are exactly **10.000000 seconds** (120,000 samples at 12,000 Hz). Derived evaluation durations are exactly **10.000000 seconds** (160,000 samples at 16,000 Hz). The duration delta is **0.000000 seconds**.
3. **Absence of Artificial Artifacts:** Forensic inspection confirmed **zero concatenation, zero crossfades, zero looping, zero zero-padding, and zero temporal cropping**.
4. **Standardized Classification:**
   - Parent source: `ORIGINAL_UNBROKEN_SENSOR_RECORDING`
   - Evaluated derivative: `RESAMPLED_OR_NORMALIZED_COPY`
5. **Continuity Scope Limitation:** While each recording is internally unbroken for its full 10.0-second duration, the 20 files represent **twenty discrete 10.0-second sensor capture windows** spaced across a 5-hour testing campaign, rather than a single 200-second continuous continuous block.

---

## 2. Signal Transformation Pipeline & Forensic Verification

The transformation pipeline applied in Phase 19 (`scripts/ingest_phase19_data.py`) was audited mathematically:

```
[Original ShotSpotter Pole Sensor]
           │
           ▼
[Raw Audio: 12,000 Hz, 16-bit Mono PCM, 120,000 samples (10.000 s)]
   File: test_{xxx}.audio.{sensor_sn}.wav (SHA-256 verified)
           │
           │  1-to-1 Polyphase Sinc Resampling (scipy.signal.resample)
           │  Sample Count: 120,000 * (16,000 / 12,000) = 160,000 samples
           │  Peak Normalization: Verified (no digital clipping)
           ▼
[Normalized Evaluation Stream: 16,000 Hz, 16-bit Mono PCM, 160,000 samples (10.000 s)]
   File: P19-CAT-A-{FP}-{test_id}.wav
```

### 2.1. Mathematical Duration & Sample Continuity Audit
For all 20 recordings, the sample ratio satisfies:
$$\frac{N_{\text{derived}}}{N_{\text{original}}} = \frac{160,000}{120,000} = \frac{4}{3} = \frac{16,000\text{ Hz}}{12,000\text{ Hz}}$$
This proves mathematically that no samples were trimmed from the head or tail, and no padding was inserted.

---

## 3. Detailed File-by-File Lineage & Cryptographic Tracking

| Stream ID | Original Sensor File | Original SHA-256 | Derived SHA-256 | Original Samples | Derived Samples | Duration (s) | Continuity Status |
| :--- | :--- | :--- | :--- | :---: | :---: | :---: | :--- |
| `P19-CAT-A-FP1-test_001` | `test_001.audio.SCP-00-BNQ-1409.wav` | `9b740510...` | `ebcfb4ea...` | 120,000 | 160,000 | 10.000000 | `RESAMPLED_OR_NORMALIZED_COPY` |
| `P19-CAT-A-FP1-test_004` | `test_004.audio.SCP-00-BNQ-1120.wav` | `a165b4c4...` | `a5f45811...` | 120,000 | 160,000 | 10.000000 | `RESAMPLED_OR_NORMALIZED_COPY` |
| `P19-CAT-A-FP1-test_007` | `test_007.audio.SCP-00-BNQ-1635.wav` | `b30521e1...` | `0228d77f...` | 120,000 | 160,000 | 10.000000 | `RESAMPLED_OR_NORMALIZED_COPY` |
| `P19-CAT-A-FP1-test_013` | `test_013.audio.SCP-00-BNG-5567.wav` | `1160d5fc...` | `3683f2dc...` | 120,000 | 160,000 | 10.000000 | `RESAMPLED_OR_NORMALIZED_COPY` |
| `P19-CAT-A-FP2-test_019` | `test_019.audio.SCP-00-BNQ-0559.wav` | `a276182a...` | `ae82c7f4...` | 120,000 | 160,000 | 10.000000 | `RESAMPLED_OR_NORMALIZED_COPY` |
| `P19-CAT-A-FP2-test_022` | `test_022.audio.SCP-00-BNQ-0559.wav` | `43274fd6...` | `b231ff68...` | 120,000 | 160,000 | 10.000000 | `RESAMPLED_OR_NORMALIZED_COPY` |
| `P19-CAT-A-FP2-test_025` | `test_025.audio.SCP-00-BNQ-0559.wav` | `bf8f7d98...` | `438f4d99...` | 120,000 | 160,000 | 10.000000 | `RESAMPLED_OR_NORMALIZED_COPY` |
| `P19-CAT-A-FP2-test_031` | `test_031.audio.SCP-00-BNQ-0559.wav` | `9d5599b4...` | `9e65e648...` | 120,000 | 160,000 | 10.000000 | `RESAMPLED_OR_NORMALIZED_COPY` |
| `P19-CAT-A-FP3-test_037` | `test_037.audio.SCP-00-BNQ-2143.wav` | `4c8d1797...` | `fa93c200...` | 120,000 | 160,000 | 10.000000 | `RESAMPLED_OR_NORMALIZED_COPY` |
| `P19-CAT-A-FP3-test_040` | `test_040.audio.SCP-00-BNG-5545.wav` | `295a1ee4...` | `0d8e8ea4...` | 120,000 | 160,000 | 10.000000 | `RESAMPLED_OR_NORMALIZED_COPY` |
| `P19-CAT-A-FP3-test_043` | `test_043.audio.SCP-00-BNQ-2143.wav` | `9b50e7b9...` | `2d6677f4...` | 120,000 | 160,000 | 10.000000 | `RESAMPLED_OR_NORMALIZED_COPY` |
| `P19-CAT-A-FP3-test_049` | `test_049.audio.SCP-00-BNQ-2143.wav` | `0b7754f0...` | `2231c6a6...` | 120,000 | 160,000 | 10.000000 | `RESAMPLED_OR_NORMALIZED_COPY` |
| `P19-CAT-A-FP4-test_055` | `test_055.audio.SCP-00-BNQ-1651.wav` | `a36d2e6b...` | `cfaad05f...` | 120,000 | 160,000 | 10.000000 | `RESAMPLED_OR_NORMALIZED_COPY` |
| `P19-CAT-A-FP4-test_058` | `test_058.audio.SCP-00-BNG-5606.wav` | `8c603fc6...` | `6c1032b4...` | 120,000 | 160,000 | 10.000000 | `RESAMPLED_OR_NORMALIZED_COPY` |
| `P19-CAT-A-FP4-test_061` | `test_061.audio.SCP-00-BNG-5573.wav` | `bc6732cf...` | `ce9c9b46...` | 120,000 | 160,000 | 10.000000 | `RESAMPLED_OR_NORMALIZED_COPY` |
| `P19-CAT-A-FP4-test_067` | `test_067.audio.SCP-00-BNQ-1705.wav` | `863dfc82...` | `5c735661...` | 120,000 | 160,000 | 10.000000 | `RESAMPLED_OR_NORMALIZED_COPY` |
| `P19-CAT-A-FP5-test_127` | `test_127.audio.SCP-00-BNQ-1392.wav` | `111ceb6f...` | `c5fce067...` | 120,000 | 160,000 | 10.000000 | `RESAMPLED_OR_NORMALIZED_COPY` |
| `P19-CAT-A-FP5-test_130` | `test_130.audio.SCP-00-BNQ-2167.wav` | `6c382f6f...` | `52528731...` | 120,000 | 160,000 | 10.000000 | `RESAMPLED_OR_NORMALIZED_COPY` |
| `P19-CAT-A-FP5-test_133` | `test_133.audio.SCP-00-BNQ-0933.wav` | `f3a69a23...` | `26d18104...` | 120,000 | 160,000 | 10.000000 | `RESAMPLED_OR_NORMALIZED_COPY` |
| `P19-CAT-A-FP5-test_139` | `test_139.audio.SCP-00-BNQ-1493.wav` | `df95349e...` | `ce605804...` | 120,000 | 160,000 | 10.000000 | `RESAMPLED_OR_NORMALIZED_COPY` |

Complete cryptographic hashes and metadata are archived in [`reports/phase20_continuity_audit.csv`](file:///e:/gunshot/gunshot/reports/phase20_continuity_audit.csv).

