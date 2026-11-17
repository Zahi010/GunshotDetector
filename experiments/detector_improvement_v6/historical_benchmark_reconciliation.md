# HISTORICAL BENCHMARK RECONCILIATION: PHASE 46 vs PHASE 47

**RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.**

This software is an uncertified research prototype. It must never be deployed for autonomous emergency dispatch, tactical police response, active-shooter alerting, automated evacuation, building lockdown, or life-critical physical security.

---

## 1. Executive Summary

During the Phase 47 evaluation of Detector Improvement V5, a discrepancy was noted between the reported performance of Detector Improvement V4 in Phase 46 and the inline simulation of V4 evaluated in Phase 47's `run_fast_v5_evaluation.py`:

| Benchmark Metric | Phase 46 Reported (V4 Native) | Phase 47 Reported (V4 Simulation) | Discrepancy |
| :--- | :---: | :---: | :---: |
| **Phase 12 Discrete Positive Recall** | **79.17% (38 / 48)** | **72.92% (35 / 48)** | -3 detections (-6.25%) |
| **Phase 15 Discrete Positive Recall** | **85.11% (40 / 47)** | **82.98% (39 / 47)** | -1 detection (-2.13%) |
| **Phase 12 Continuous 2.0-hr Alerts** | **21 alerts** (10.5 / hr) | **21 alerts** (10.5 / hr) | Exact match (0.00%) |
| **Phase 16 Continuous 6.08-hr Alerts** | **8 alerts** (1.32 / hr) | **8 alerts** (1.32 / hr) | Exact match (0.00%) |

This audit provides complete forensic reconciliation of the underlying code, model weights, and signal processing differences explaining this delta.

---

## 2. Root Cause Analysis of Benchmark Differences

Forensic inspection of the execution scripts revealed two concrete code differences between native `DetectorImprovementV4` (`experiments/detector_improvement_v4/model_detector_improvement_v4.py`) and the inline simulation inside `scratch/run_fast_v5_evaluation.py`:

### 2.1 Omission of `is_ballistic_shockwave` Override in Simulation
In native V4, the suppression logic contained an explicit ballistic shockwave override:
```python
is_ballistic_shockwave = (bal_max >= 0.40 and bal_max >= fw_max * 0.85)
if is_ballistic_shockwave:
    # Protect genuine ballistic shockwaves from spurious suppression
    suppression_factor = 1.0
```
In `scratch/run_fast_v5_evaluation.py`, the simulation of V4 applied fixed multiplicative rules directly:
```python
if fw_s >= 0.45 and fw_s / (gun_s + 1e-4) >= 1.8 and gun_s < 0.25:
    adj_v4 *= 0.30
```
Because clipped AR-15 recordings in Phase 12 exhibited high pyrotechnic crackle scores alongside ballistic shockwaves, the omission of the `is_ballistic_shockwave` protection caused 3 clipped positive recordings (`phase12_gunshot_clipped_ar15_01.wav`, `phase12_gunshot_clipped_ar15_03.wav`, and `phase12_gunshot_clipped_ar15_04.wav`) to be attenuated from 0.74–0.78 down to ~0.23, turning 3 genuine detections into false negatives.

### 2.2 FSM Cooldown Discrepancy
In Phase 46, native V4 operated with an FSM refractory cooldown of **0.80 seconds**. In Phase 47, the comparative harness passed the unified V5 FSM configuration which enforced a cooldown of **1.50 seconds**. For rapid burst-fire recordings in Phase 15, the longer cooldown merged secondary burst confirmations, slightly reducing single-event boundary detection on 1 file.

### 2.3 Reconciliation Conclusion
When native `DetectorImprovementV4` is evaluated directly with its frozen code and configuration, the canonical Phase 46 numbers are reproduced identically:
- Phase 12 Positive Recall: **79.17% (38/48)**
- Phase 15 Positive Recall: **85.11% (40/47)**
- Phase 12 Continuous 2hr: **21 alerts**

The Phase 47 table reflected an approximate inline simulation rather than a change in the frozen V4 model.

---

## 3. Cryptographic Hashes & Artifact Provenance

| Artifact | File Path | SHA256 Hash |
| :--- | :--- | :--- |
| **V4 Model Code** | `experiments/detector_improvement_v4/model_detector_improvement_v4.py` | `05b2a3fa410b029ca2b95fa78385bb32fe0fc161ec9c79247cfaefd6fc48bc95` |
| **V4 Fusion Model** | `experiments/detector_improvement_v4/fusion_model.joblib` | `1e9a2636605bd2ca778848db700a944358bbd7f2a1b9f71c4c83fca385a42099` |
| **V5 Model Code** | `experiments/detector_improvement_v5/model_detector_improvement_v5.py` | `1054b1f6927da8ee5d9c2409f6b645167eb28ce196020c242c7aa33b1eb1b12b` |
| **V6 Model Code** | `experiments/detector_improvement_v6/model_detector_improvement_v6.py` | `d72023cbca73c71177651c51a7be47e246be8d62689622d104523d4c3c3a9f03` |
| **V6 Config** | `experiments/detector_improvement_v6/config_improvement_v6.json` | `ca2f074a3f124c6e9a0f0237aa0a56fe1f28b26e2581699741a3cbce1cf55243` |
| **Phase 12 Continuous Audio** | `data/phase12_independent_test/continuous_ambient/phase12_continuous_stream_01_urban_and_environmental_2hr.wav` | `5c73917a0eeef23506cfdfdf4905260faae1355c7b396e47d104d41beecfaaf2` |

All benchmark scripts are fully reproducible from the repository state.

