# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY

> [!CAUTION]
> **MANDATORY SAFETY DESIGNATION**  
> **RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.**  
> This experimental acoustic machine-learning research software is uncertified and must never be deployed for autonomous emergency dispatch, tactical police response, active-shooter alerting, automated evacuation, building lockdown, or life-critical physical security.  
> Use legally obtained recordings and safe audio playback only. Live-fire testing and hazardous acoustic experiments are strictly prohibited.

---

# PHASE 29 FORENSIC AUDIT REPORT
## Phase 14 Threshold Discrepancy Resolution & Runtime Configuration Provenance

**Document Identifier:** `PHASE29-REP-THRESHOLD-PROVENANCE-AUDIT`  
**Phase:** `PHASE_29_CONFIGURATION_VERIFICATION_AIRCRAFT_VALIDATION_ROBUSTNESS_AUDIT`  
**Focus:** Reconciliation of Discrepant Operational Thresholds (`0.55/0.40` vs `0.75/0.48`) Across Source Artifacts, Manifests, and Runtime Code

---

## 1. Executive Summary

Phase 27 narrative documentation ([phase27_final_report.md](file:///e:/gunshot/gunshot/reports/phase27_final_report.md) and [phase27_distractor_analysis.md](file:///e:/gunshot/gunshot/reports/phase27_distractor_analysis.md)) described Phase 14 Balanced as operating with:
$$\text{threshold\_on} = 0.55, \quad \text{threshold\_off} = 0.40$$
In contrast, Phase 28 technical documentation ([phase28_aircraft_fragmentation_audit.md](file:///e:/gunshot/gunshot/reports/phase28_aircraft_fragmentation_audit.md) and [phase28_final_report.md](file:///e:/gunshot/gunshot/reports/phase28_final_report.md)) described Phase 14 Balanced as operating with:
$$\text{threshold\_base} = 0.75, \quad \text{threshold\_high} = 0.88, \quad \text{threshold\_off} = 0.48$$

Because a variation in activation threshold from $0.55$ to $0.75$ represents a major change in sensitivity, this audit conducted a comprehensive line-by-line inspection of:
1. Frozen detector source code ([model_phase14.py](file:///e:/gunshot/gunshot/model_phase14.py) and [model_phase17.py](file:///e:/gunshot/gunshot/model_phase17.py)).
2. Configuration files and bundle presets ([config.py](file:///e:/gunshot/gunshot/config.py), [models/gunshot_yamnet_bundle/threshold.json](file:///e:/gunshot/gunshot/models/gunshot_yamnet_bundle/threshold.json)).
3. Runtime evaluation scripts ([scripts/evaluate_phase27_aerosonic.py](file:///e:/gunshot/gunshot/scripts/evaluate_phase27_aerosonic.py), [scripts/run_phase17_negative_evaluation.py](file:///e:/gunshot/gunshot/scripts/run_phase17_negative_evaluation.py)).
4. Historical baseline manifests and event generators.

### Principal Finding: Narrative Error in Phase 27 Report
The investigation definitively concludes that **the discrepancy is a documentation/narrative error in Phase 27's written markdown reports**. 
At no point during Phase 17, Phase 27, or Phase 28 did the running Python evaluation code execute with $\text{threshold\_on} = 0.55$ or $\text{threshold\_off} = 0.40$. Across all 23 evaluated continuous streams, the actual runtime parameters loaded into memory were strictly:
$$\mathbf{threshold\_base = 0.75}, \quad \mathbf{threshold\_high = 0.88}, \quad \mathbf{threshold\_off = 0.48}, \quad \mathbf{confirm\_windows = 2}$$

Furthermore, the narrative claim in Phase 27 that "Phase 17 raised `threshold_off` from 0.40 to 0.48" was **factually incorrect**: both Phase 14 and Phase 17 executed with an identical `threshold_off = 0.48`. The sole functional difference between the two models in Python code was the boolean toggle for animal vocalization suppression.

---

## 2. Source-Level Code Audit

### 2.1 Frozen Model Definition (`model_phase14.py`)
In `model_phase14.py` (SHA-256: `a268551604ae8b73068435ff10ab3d265065f56e0679757fca5b6bf0f061c065`, file size: 23,340 bytes), the canonical profile dictionary defines:

```python
# model_phase14.py, Lines 171-185:
PROFILES = {
    "balanced": {
        "threshold_base": 0.75,
        "threshold_high": 0.88,
        "threshold_off": 0.48,
        "confirm_windows": 2,
        "cooldown_secs": 2.0,
        "enable_semantic_gating": True,
        "min_crest_factor_db": 8.8,
        "single_win_min_crest_db": 12.0,
        "fw_thresh": 0.35,
        "fw_ratio": 2.0,
        "fw_gun_max": 0.05,
        "thun_thresh": 0.25,
        "thun_ratio": 1.5
    },
    ...
```

No profile in `model_phase14.py` contains `threshold_base = 0.55` or `threshold_off = 0.40`.

### 2.2 Frozen Model Definition (`model_phase17.py`)
In `model_phase17.py` (SHA-256: `e2b262b866fdd5d7f1a4ab91a7b8b9bac189ee8cc7a78603b3544ca1579fb819`, file size: 29,067 bytes), the experimental profile dictionary defines:

```python
# model_phase17.py, Lines 275-295:
"experimental_animal_suppression": {
    "threshold_base": 0.75,
    "threshold_high": 0.88,
    "threshold_off": 0.48,
    "confirm_windows": 2,
    "cooldown_secs": 2.0,
    "enable_semantic_gating": True,
    "enable_animal_suppression": True,
    "min_crest_factor_db": 8.8,
    "single_win_min_crest_db": 12.0,
    "fw_thresh": 0.35,
    "fw_ratio": 2.0,
    "fw_gun_max": 0.05,
    "thun_thresh": 0.25,
    "thun_ratio": 1.5,
    "animal_thresh": 0.35,
    "animal_ratio": 2.0
}
```

A direct diff between `model_phase14.py` (`balanced`) and `model_phase17.py` (`experimental_animal_suppression`) confirms that all temporal, hysteresis, crest factor, and ballistic thresholds are **bit-for-bit identical**:
- `threshold_base`: **0.75** (Identical)
- `threshold_high`: **0.88** (Identical)
- `threshold_off`: **0.48** (Identical)
- `confirm_windows`: **2** (Identical)
- `cooldown_secs`: **2.0** (Identical)
- `enable_animal_suppression`: **False** in Phase 14 vs **True** in Phase 17 (The only difference).

---

## 3. Runtime Script Inspection Across All 23 Streams

To verify whether thresholds were overridden dynamically at runtime, every evaluation script was audited:

### 3.1 Streams 01 to 17 (UK Industrial, UK Rural, Spain Bilbao)
Evaluated in Phase 17 via `scripts/run_phase17_negative_evaluation.py`:
```python
# run_phase17_negative_evaluation.py, Lines 185-194:
"Phase 14 Balanced": {
    "model_obj": det_p14_b,
    "threshold_base": 0.75,
    "threshold_high": 0.88,
    "threshold_off": 0.48,
    "confirm_windows": 2,
    "cooldown": 2.0,
    "min_crest": 8.8,
    "single_crest": 12.0
}
```
**Conclusion:** Phase 14 was loaded with `0.75 / 0.88 / 0.48`.

### 3.2 Streams 18 to 23 (Australia AeroSonicDB)
Evaluated in Phase 27 via `scripts/evaluate_phase27_aerosonic.py`:
```python
# evaluate_phase27_aerosonic.py, Lines 333-346:
p14_events = merge_phase14_events(
    p14_windows,
    threshold_base=0.75,
    threshold_high=0.88,
    threshold_off=0.48,
    confirm_windows=2,
    cooldown_secs=2.0,
    audio_duration_sec=dur_s,
    allow_short_clip_exception=True,
    crest_factor_db=crest_db,
    min_crest_factor_db=8.8,
    single_win_min_crest_db=12.0
)
```
**Conclusion:** Phase 14 was explicitly invoked with `0.75 / 0.88 / 0.48`.

---

## 4. Origin of the Discrepant `0.55 / 0.40` Figures

Where did the erroneous `0.55 / 0.40` narrative in Phase 27 originate?
1. In `models/gunshot_yamnet_bundle/threshold.json` (created during Phase 4–6 development), the JSON file lists:
   `"operating_presets": { "high_precision_conservative": 0.55 }`
2. During Phase 6 calibration (`models/phase6_yamnet_bundle/threshold.json`), operating points included `high_recall_sensitive: 0.55`.
3. In Phase 27, when authoring the technical distractor narrative ([reports/phase27_distractor_analysis.md](file:///e:/gunshot/gunshot/reports/phase27_distractor_analysis.md)), the report drafter incorrectly referenced prototype notes describing a hypothetical $0.55$ activation threshold and a hypothetical $0.40$ release threshold, asserting that Phase 17 "raised the release threshold to 0.48".
4. This markdown narrative was copy-pasted into [reports/phase27_final_report.md](file:///e:/gunshot/gunshot/reports/phase27_final_report.md) without cross-checking the actual arguments passed to `merge_phase14_events()` in `evaluate_phase27_aerosonic.py`.

---

## 5. Configuration Provenance Table Across Evaluated Streams

The following table summarizes the verified configuration loaded across the benchmark streams:

| Stream Range | Physical Campaign | Detector Profile | Threshold Base | Threshold High | Threshold Off | Confirm Wins | Provenance Status |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :--- |
| `P16-STR-01..10` | `CAMPAIGN-RPISOUND-UK` | Phase 14 Balanced | **0.75** | **0.88** | **0.48** | 2 | Verified Source Eval |
| `P16-STR-01..10` | `CAMPAIGN-RPISOUND-UK` | Phase 17 Experimental | **0.75** | **0.88** | **0.48** | 2 | Verified Source Eval |
| `P16-STR-11` | `CAMPAIGN-CHEWMAGNA-UK` | Phase 14 Balanced | **0.75** | **0.88** | **0.48** | 2 | Verified Source Eval |
| `P16-STR-11` | `CAMPAIGN-CHEWMAGNA-UK` | Phase 17 Experimental | **0.75** | **0.88** | **0.48** | 2 | Verified Source Eval |
| `P17-STR-12..17` | `CAMPAIGN-BILBAO-ES` | Phase 14 Balanced | **0.75** | **0.88** | **0.48** | 2 | Verified Source Eval |
| `P17-STR-12..17` | `CAMPAIGN-BILBAO-ES` | Phase 17 Experimental | **0.75** | **0.88** | **0.48** | 2 | Verified Source Eval |
| `P27-STR-18..23` | `CAMPAIGN-AEROSONIC-AU` | Phase 14 Balanced | **0.75** | **0.88** | **0.48** | 2 | Verified Source Eval |
| `P27-STR-18..23` | `CAMPAIGN-AEROSONIC-AU` | Phase 17 Experimental | **0.75** | **0.88** | **0.48** | 2 | Verified Source Eval |

A machine-readable version of this complete audit is available in [reports/phase29_runtime_configuration_manifest.csv](file:///e:/gunshot/gunshot/reports/phase29_runtime_configuration_manifest.csv).

---

## 6. Audit Verdict

1. **Resolution:** The Phase 14 threshold discrepancy is **100% resolved**.
2. **Classification:** The `0.55 / 0.40` values in Phase 27 were a **clerical documentation error**.
3. **Model Integrity:** Phase 14 Balanced and Phase 17 Experimental were evaluated under identical baseline hysteresis thresholds (`0.75 / 0.88 / 0.48`).
4. **Historical Event Validity:** All event logs, cooldown ledgers, and false alert counts across Phases 17–28 remain fully valid and originate from the true `0.75 / 0.88 / 0.48` configuration.

