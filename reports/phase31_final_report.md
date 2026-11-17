# Phase 31 Final Report: Campaign Provenance Reconciliation, Phase 17 State-Machine Defect Verification & Suppression Ablation
## Comprehensive Multi-Campaign Audit, Algorithmic Defect Verification & Governance Decision

**Document ID:** `REPORT-PHASE31-FINAL-001`  
**Phase:** 31 (Forensic Verification, Defect Verification & Suppression Ablation)  
**Date:** November 2026  
**Status:** COMPLETE & INDEPENDENTLY REPRODUCIBLE  

---

### MANDATORY SAFETY DESIGNATION
> [!CAUTION]
> **RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.**  
> This experimental acoustic machine-learning software is uncertified and must never be deployed for autonomous emergency dispatch, tactical police response, active-shooter alerting, automated evacuation, building lockdown, or life-critical physical security. Use legally obtained recordings and safe audio playback only. Live-fire testing and hazardous acoustic experiments are strictly prohibited. Historical controlled-validation recordings may be analysed only as existing research data; do not conduct new firing experiments.

---

## 1. Executive Summary & Phase 31 Mission

Phase 31 was chartered to conduct an exhaustive forensic investigation into three critical findings raised in Phase 30:
1. **Campaign and Recording Provenance:** Resolve apparent discrepancies between Phase 29 reporting (Southampton, Chew Magna, Bilbao, Adelaide) and Phase 30 narrative reporting (Paris, Vienna, Bilbao, Adelaide).
2. **Phase 17 State-Machine Defect:** Empirically investigate the omitted `else: active_cluster = []` reset branch in `model_phase17.py`, construct a synthetic regression test harness, and evaluate a candidate patch without modifying frozen models.
3. **Animal Suppression Causal Audit:** Disambiguate suppression parameter definitions, reproduce the 25 aircraft overflight sequences in AeroSonicDB, and perform an offline counterfactual ablation to determine whether animal suppression caused alert fragmentation.

### Headline Findings & Governance Determinations
- **Provenance Resolution:** The physical dataset of 23 unbroken continuous streams ($12.6460\text{ gross hours}$) and its underlying alert totals (128 P14, 159 P17) **never changed across any phase**. The reported "Paris" and "Vienna" campaign identities in Phase 30 were clerical transcription errors in markdown report prose; the underlying data tables always preserved the authentic campaigns: Southampton, Chew Magna, Bilbao, and Adelaide.
- **State-Machine Defect Confirmed:** Frozen `model_phase17.py` omits `else: active_cluster = []` and evaluates an unguarded `if active_cluster:` at file termination. It failed 3 out of 5 synthetic regression tests (Tests A, B, and D), retaining unconfirmed noise spikes indefinitely and synthesizing spurious alerts across temporal gaps. A separate experimental candidate (`experiments/phase31/model_phase17_state_reset_candidate.py`) resolved all defects (5/5 PASS).
- **Animal Suppression Causal Contribution:** In 11 of 25 aircraft sequences (44.0%), animal suppression ($0.30\times$) directly forced detection scores below the $0.48$ off-threshold, terminating ongoing alerts prematurely and causing subsequent re-triggering into 2–6 fragmented alerts.
- **Statistical Reassessment:** On the reconciled registry, neither detector is statistically superior on continuous audio (Wilcoxon $p = 0.15626$, exact sign test $p = 0.72656$).
- **Final Governance Decision:** **Phase 17 Experimental is REJECTED for promotion**. **Phase 14 Balanced is retained as the Default Research Baseline**.

---

## 2. Baseline Model & Historical Archive Freeze Verification

All historical source files and release archives were verified against their canonical SHA-256 digests prior to analysis:

| Artifact Name | Role / Classification | File Size (Bytes) | SHA-256 Digest | Verification Status |
| :--- | :--- | :---: | :--- | :---: |
| `model_phase14.py` | Default Research Baseline | 23,340 | `a268551604ae8b73068435ff10ab3d265065f56e0679757fca5b6bf0f061c065` | **MATCH_CONFIRMED** |
| `model_phase17.py` | Selectable Experimental Profile | 29,067 | `e2b262b866fdd5d7f1a4ab91a7b8b9bac189ee8cc7a78603b3544ca1579fb819` | **MATCH_CONFIRMED** |
| `model_phase13.py` | Historical Comparator | 22,252 | `68585039a4a4fdb7978a99f5e2a72c0ad5a9523127ec24a1338fbedd1c1231e6` | **MATCH_CONFIRMED** |
| `model_phase9.py` | Historical Comparator | 17,719 | `85cedd9f5b988ecafb1eae7de9630ee3d6a387ded6ef732e0efb7c3b496f132a` | **MATCH_CONFIRMED** |
| `gunshot_detection_phase30.zip` | Phase 30 Release Archive | 5,451,607 | `a50cc30c13f840f1d68cb111b868242562262e979d9b211d902b6573ab14ada4` | **MATCH_CONFIRMED** |
| `gunshot_detection_phase29.zip` | Phase 29 Release Archive | 4,593,850 | `23a3f8af3dc74db6bc71b0babbc813bb0e96d1bbd4ca2001cb508b8756081dd5` | **MATCH_CONFIRMED** |
| `gunshot_detection_phase28.zip` | Phase 28 Release Archive | 4,586,167 | `e6505e3597b406541efb005f1d69432653cbfc5603843695fdfd66af01324a72` | **MATCH_CONFIRMED** |

Frozen models were preserved without modification.

---

## 3. Campaign & Recording Provenance Reconciliation

The forensic investigation accounted for all 23 individual audio recordings, proving:
1. **The Physical Waveforms Were Constant:**  
   Total audio duration is exactly $45,525.575\text{ seconds}$ ($12.6460\text{ hours}$) across all phases. Every recording file matches its historical SHA-256 hash.
2. **True Campaign Lineage Restored:**
   - **`CAMPAIGN-RPISOUND-UK`:** Southampton Urban & Industrial Ambient (10 streams, 5.5000 hr, 24 P14 alerts, 22 P17 alerts). Source: Zenodo `10.5281/zenodo.7493820`.
   - **`CAMPAIGN-CHEWMAGNA-UK`:** Chew Magna Rural Soundscape (1 stream, 0.5833 hr, 0 P14 alerts, 0 P17 alerts). Source: Zenodo `10.5281/zenodo.3938837`.
   - **`CAMPAIGN-BILBAO-ES`:** Bilbao Urban Traffic & Plazas (6 streams, 0.5627 hr, 32 P14 alerts, 29 P17 alerts). Source: Zenodo `10.5281/zenodo.18716205`.
   - **`CAMPAIGN-AEROSONIC-AU`:** AeroSonicDB Adelaide Airport Periphery (6 streams, 6.0000 hr, 72 P14 alerts, 108 P17 alerts). Source: Zenodo `10.5281/zenodo.10215080`.
3. **Root Cause of Phase 30 Discrepancy:**  
   In Phase 30, the author transcribed unvetted candidate source notes into the markdown report narrative, labeling `CAMPAIGN-RPISOUND-UK` as "Paris" and `CAMPAIGN-CHEWMAGNA-UK` as "Vienna", and shifting residual alerts to Bilbao ($37\text{ vs }36$). However, the underlying data CSV files (`reports/phase30_campaign_comparison.csv` and `reports/phase30_recording_provenance.csv`) always preserved the authentic UK, Spain, and Australia campaign identities and 24/0/32/72 alert counts.
4. **Geographic Independence:** Exactly 4 verified independent environmental audio campaigns spanning 3 countries (UK, Spain, Australia).

---

## 4. Phase 17 State-Machine Defect Verification

Line-by-line inspection of `model_phase17.py` revealed:
- **Defect 1:** In `merge_phase17_events` (lines 150–155), the state machine omits `else: active_cluster = []` when outside an event. An unconfirmed window ($0.75 \le score < 0.88$) is retained indefinitely.
- **Defect 2:** At file termination (line 180), `if active_cluster:` emits an event even if $in\_event$ is `False` and $len(active\_cluster) == 1$.
- **Defect 3:** In streaming mode (`process_chunk`), `self.active_cluster` similarly lacks a sub-threshold reset.

### Synthetic Regression Results (Tests A through E)

```
Test ID   Description                            Expected   Phase 14   Phase 17   Candidate Patch
-------------------------------------------------------------------------------------------------
Test A    Isolated spike (0.78 -> 0.10)          0 alerts   0 (PASS)   1 (FAIL)   0 (PASS)
Test B    Unrelated spikes across 100s gap       0 alerts   0 (PASS)   1 (FAIL)   0 (PASS)
Test C    Consecutive confirmation (0.78, 0.79)  1 alert    1 (PASS)   1 (PASS)   1 (PASS)
Test D    Independent file boundary reset        0 alerts   0 (PASS)   1 (FAIL)   0 (PASS)
Test E    Immediate qualification (0.92, crest)  1 alert    1 (PASS)   1 (PASS)   1 (PASS)
-------------------------------------------------------------------------------------------------
Overall   5 Synthetic Test Vectors               —          100% PASS  40% PASS   100% PASS
```

An experimental patch was created in `experiments/phase31/model_phase17_state_reset_candidate.py` (SHA-256: `c144b917...`), achieving 100% regression pass without modifying the frozen baseline.

---

## 5. Animal Suppression Causal Audit & Counterfactual Ablation

The audit disambiguated all suppression parameters:
- `animal_thresh = 0.35`: Minimum YAMNet animal/avian probability.
- `animal_ratio = 2.0x`: Ballistic dominance ratio ($animal \ge 2.0 \times gun$). **Not an applied penalty.**
- `suppression_penalty = 0.30x`: 70% multiplicative reduction applied to $calibrated\_score$.
- `threshold_off = 0.48`: Hysteresis termination bound.

### Classification of the 25 Aircraft Overflight Sequences
- **Confirmed Direct Suppression Fragmentation:** **11 sequences (44.0%)**. Turbofan whine triggered animal suppression ($0.30\times$), puncturing below $0.48$, terminating alerts prematurely, and causing re-triggering upon cooldown expiration.
- **Pure Acoustic Fluctuation:** **9 sequences (36.0%)**. Suppression remained inactive; sound envelope dips and state-machine retention produced fragmented alerts.
- **Combined / Partial Mechanism:** **5 sequences (20.0%)**. Brief suppression activations combined with acoustic modulation.
- **Unresolved:** **0 sequences (0.0%)**.

Offline counterfactual ablation (disabling the $0.30\times$ animal penalty) merged fragmented sequences, eliminating 23 spurious alerts in AeroSonicDB.

---

## 6. Historical Positive Validation Context (Pittsburgh DQV 2018)

- **Reproduction:** 50 annotated Category A rounds across 20 recordings ($200.0\text{ s}$ gross duration). Phase 14 detected 27/50 (54.0%); Phase 17 detected 33/50 (66.0%). Exact McNemar $p = 0.03125$.
- **Methodological Safeguard:** Controlled live-fire validation ($200\text{ s}$ audio, $140\text{ s}$ background) cannot establish false-alert resistance (Poisson upper limit $= 77.03\text{ alerts/hr}$) or unexpected real-world operational gunfire sensitivity. Live-fire testing is strictly banned.

---

## 7. Rebuilt Statistical Inferences on Reconciled Registry

Rebuilt from the master registry across all 23 recordings:
- **Phase 14 Balanced:** 128 alerts ($10.1218\text{ gross FAR}$; $10.1789\text{ Conv A FAR}$; $10.2237\text{ Conv B FAR}$).
- **Phase 17 Experimental:** 159 alerts ($12.5732\text{ gross FAR}$; $12.6614\text{ Conv A FAR}$; $14.6243\text{ Conv B FAR}$).
- **Recording Preferences:** 3 favor Phase 17, 5 favor Phase 14, 15 are tied.
- **Non-Parametric Inferences:**
  - Wilcoxon signed-rank test: $W = 8.0, p = 0.15626$ (Not significant).
  - Exact Sign test: $k = 3, n = 8, p = 0.72656$ (Not significant).
- **LOCO Sensitivity:** All leave-one-campaign-out subsets remain non-significant ($p > 0.05$). Neither detector has demonstrated statistically significant superiority on continuous environmental audio.

---

## 8. Final Governance Decision & Directives

1. **Phase 17 Experimental is REJECTED for baseline promotion:**  
   Phase 17 exhibits a confirmed state-machine defect, elevated false alert rates in negative continuous audio (+31 alerts), and no statistically significant performance advantage on independent campaigns.
2. **Phase 14 Balanced is RETAINED as the Default Research Baseline:**  
   Phase 14 possesses a verified, defect-free state machine, lower gross and eligible false-alert rates across 12.65 hours of continuous exposure, and full architectural stability.
3. **Safety Designation Retained:**  
   All artifacts, models, and scripts must strictly display:  
   **`RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.`**

