# ANTIGRAVITY MASTER REPORT — PHASE 33
## Phase 32 Reproducibility, Campaign Provenance & Statistical Integrity Audit

> **MANDATORY SAFETY DESIGNATION**  
> **RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY**  
> *This experimental acoustic machine-learning software is uncertified and must never be deployed for autonomous emergency dispatch, tactical police response, active-shooter alerting, automated evacuation, building lockdown, or life-critical physical security. Use legally obtained recordings and safe audio playback only. Live-fire testing and hazardous acoustic experiments are strictly prohibited.*

---

## 1. Executive Summary

Phase 33 conducted an independent, read-only forensic audit of Phase 32, resolving all material inconsistencies across campaign identities, exposure duration calculations, statistical significance claims, historical controlled-validation event-matching, state-machine regression test counts, and release manifests.

The core results of Phase 33 are summarized below:

| Workstream | Investigation Focus | Phase 32 Claim / Report | Phase 33 Authoritative Audit Finding | Formal Status |
| :--- | :--- | :--- | :--- | :---: |
| **WS-1** | 23-Stream Campaign Provenance & Exposure Duration | 4 campaigns: RPISOUND (7), DCASE2020 (5), URBANSOUND-PL (5), AeroSonic (6); 45,526.0s (12.6461h). | 4 campaigns: RPISOUND / Southampton (10), Chew Magna (1), Bilbao (6), Adelaide (6); exact sum = 45,525.5755s (12.6460h). Fictional DCASE/UrbanSound-PL labels debunked. | `REPRODUCED WITH CORRECTION` |
| **WS-2** | Factorial Defect Ablation Reproduction | Cond A: 108, Cond B: 130, Cond C: 66, Cond D: 72 alerts. Main effects: +42/+58, -22/-6, interaction: -16. | All 4 condition counts and interaction effects reproduced bit-for-bit. Cond D confirmed identical in timing to Phase 14 baseline, but has schema divergence (`CORRECTED-CANDIDATE / SUPPRESSION-OFF`). Aircraft fragmentation confirmed (+6/+5). | `REPRODUCED WITH CORRECTION` |
| **WS-3** | Wilcoxon & Paired Statistical Inference | Discrepancies across phases: p = 0.125, 0.156, 0.195, 0.211. Claimed equivalence. | Discrepancies resolved purely as methodology choices (SciPy asymptotic: 0.15626, exact untied: 0.19531, exact tied: 0.21094, Pratt: 0.36754, sign test: 0.72656). Non-significance is due to low power (N=8 non-zero pairs); does not prove equivalence. | `REPRODUCED WITH CORRECTION` |
| **WS-4** | Pittsburgh Controlled Event-Matching Audit | Historical P17 superiority: 33 vs 27 rounds (p = 0.03125). Multi-credit reuse suspected. | Proved historical p = 0.03125 was driven by duplicate alert reuse across burst sequences. Under strict 1-to-1 matching: 15 P14 vs 19 P17 rounds (McNemar p = 0.21875). Recording level: 15 vs 18 (p = 0.2500). Not significant. | `REPRODUCED` |
| **WS-5** | State-Machine Test Count Resolution | Executive summary stated "Failed 6/12 vectors", but enumerated 8 vector IDs. | True failure count is exactly 8/12 (66.7% failure rate): VEC-01, VEC-02, VEC-03, VEC-04, VEC-07, VEC-09, VEC-10, VEC-12. Pass count is 4/12 (33.3%). "6/12" was a clerical typo. | `REPRODUCED WITH CORRECTION` |
| **WS-6** | Deliverables, Hashes & Release Integrity | 17 vs 18 deliverables; archive size 4,545,869 bytes, SHA-256 `b27bbb...`. | Archive verified (4,545,869 bytes, hash match, CRC PASS, 41 entries). 17 workspace deliverables vs 18 items including zip archive. All frozen baseline hashes verified bit-for-bit. | `REPRODUCED` |

---

## 2. Scope and Safety Designation

### 2.1 Research Prototype Boundary
This software is an uncertified academic research prototype. It has not undergone formal lifecycle verification, environmental hazard qualification, hardware-in-the-loop stress testing, or safety-critical software compliance certification (e.g., DO-178C, IEC 61508, ISO 26262, UL 2524).

### 2.2 Operational Deployment Prohibition
Deployment of this software, in whole or in part, for life-critical physical security, automated facility lockdowns, mass evacuation alarming, active-shooter tactical alerting, or autonomous 911 dispatch is strictly and explicitly prohibited.

### 2.3 Acoustic Testing Constraints
All analyses in this phase were executed exclusively upon legally archived acoustic recordings and synthetic discrete test signals. Live-fire weapons testing, pyrotechnic discharge, or hazardous acoustic field experiments are strictly prohibited.

---

## 3. Frozen Artifact Integrity

Under the Phase 33 audit charter, no model files were retrained, modified, tuned, or re-exported. All historical release archives and baseline model code were cryptographically audited using SHA-256 checksums and verified to remain bit-for-bit identical to their frozen state.

### 3.1 Model & Architecture Checksums

| Component / Artifact | Relative Path | Size (Bytes) | SHA-256 Checksum | Invariance Status |
| :--- | :--- | :---: | :--- | :---: |
| **Phase 14 Balanced Baseline** | `gunshot/model_phase14.py` | 23,340 | `a268551604ae8b73068435ff10ab3d265065f56e0679757fca5b6bf0f061c065` | `VERIFIED_FROZEN` |
| **Phase 17 Experimental Profile** | `gunshot/model_phase17.py` | 29,067 | `e2b262b866fdd5d7f1a4ab91a7b8b9bac189ee8cc7a78603b3544ca1579fb819` | `VERIFIED_FROZEN` |
| **Phase 13 Baseline Profile** | `gunshot/model_phase13.py` | 22,252 | `68585039a4a4fdb7978a99f5e2a72c0ad5a9523127ec24a1338fbedd1c1231e6` | `VERIFIED_FROZEN` |
| **Phase 9 Baseline Profile** | `gunshot/model_phase9.py` | 17,719 | `85cedd9f5b988ecafb1eae7de9630ee3d6a387ded6ef732e0efb7c3b496f132a` | `VERIFIED_FROZEN` |
| **Phase 17 State-Reset Candidate** | `experiments/phase31/...` | 29,718 | `c144b917b56532787e2a9198f2cad4a77dc2095b57962f31d11d250a4d5d9ea5` | `VERIFIED_FROZEN` |
| **Feature Extraction Engine** | `gunshot/feature_extractor.py` | 6,218 | `1c665b7c1749de98337da0726627710fffe0dcfa56335291b666ae7abcbae94f` | `VERIFIED_FROZEN` |
| **System Configuration** | `gunshot/config.py` | 2,619 | `55749f9d46d561d131fad374064021b73c08274e2a79954efd08570b029b1858` | `VERIFIED_FROZEN` |

### 3.2 Historical Release Archive Checksums

| Archive File | Absolute Path | Size (Bytes) | SHA-256 Checksum | Verification Status |
| :--- | :--- | :---: | :--- | :---: |
| `gunshot_detection_phase29.zip` | `E:/gunshot/gunshot_detection_phase29.zip` | 4,593,850 | `23a3f8af3dc74db6bc71b0babbc813bb0e96d1bbd4ca2001cb508b8756081dd5` | `PASS` |
| `gunshot_detection_phase30.zip` | `E:/gunshot/gunshot_detection_phase30.zip` | 5,451,607 | `a50cc30c13f840f1d68cb111b868242562262e979d9b211d902b6573ab14ada4` | `PASS` |
| `gunshot_detection_phase31.zip` | `E:/gunshot/gunshot_detection_phase31.zip` | 4,564,376 | `92a4f4d9882d0d69edf1cacc390244ef480fea09a1bc80351787297c0e361c47` | `PASS` |
| `gunshot_detection_phase32.zip` | `E:/gunshot/gunshot_detection_phase32.zip` | 4,545,869 | `b27bbb6336e3d0bb229ac10ade6c669b3d917d5ba58e91617c5c3cdd1eadddfb` | `PASS` |

---

## 4. Canonical 23-Stream Provenance & Duration Arithmetic

A complete forensic analysis was conducted on all 23 audio files comprising the continuous negative-exposure benchmark.

### 4.1 Canonical Stream Registry
The full per-stream registry is documented in [phase33_canonical_stream_registry.csv](file:///E:/gunshot/gunshot/reports/phase33_canonical_stream_registry.csv).

- **Total Streams:** Exactly 23 distinct WAV audio files.
- **Physical Existence:** 23 / 23 files present on disk with valid headers.
- **Total Duration:** Exactly **45,525.5755 seconds**, which equals **12.64599319 hours**, rounding to **12.6460 hours**.

### 4.2 Resolution of the Phase 32 Duration Discrepancy
Phase 32 prose reported the benchmark duration as **45,526.0 seconds (12.6461 hours)**, introducing a $+0.4245$ s ($+0.0001$ h) discrepancy against earlier phases.

The audit proved this discrepancy was entirely a **narrative rounding artifact**. Phase 32 computed its total by summing pre-rounded campaign durations:
$$\text{RPISOUND (9,860.0 s)} + \text{DCASE (7,030.0 s)} + \text{URBANSOUND (7,036.0 s)} + \text{AEROSONIC (21,600.0 s)} = 45,526.0\text{ s}$$
When evaluated from the physical WAV headers:
- Southampton / RPISOUND: $9,860.0000\text{ s}$
- Bilbao: $14,065.5755\text{ s}$ (split by Phase 32 narrative into $7030.0 + 7036.0 = 14,066.0\text{ s}$, adding $+0.4245\text{ s}$)
- Adelaide AeroSonicDB: $21,600.0000\text{ s}$
- Exact Sum: $9860.0000 + 14065.5755 + 21600.0000 = \mathbf{45,525.5755\text{ s}} = \mathbf{12.645993...\text{ h}} \approx \mathbf{12.6460\text{ h}}$.

The authoritative duration of the 23-stream continuous benchmark is formally established as **12.6460 hours**.

---

## 5. Phase 31 vs Phase 32 Campaign Provenance Reconciliation

A critical finding of Phase 33 is the resolution of the conflicting campaign identities reported across Phases 31 and 32.

### 5.1 The Fictional Campaign Identifiers in Phase 32
In Phase 32 narrative reports, the 23 streams were attributed to:
- `CAMPAIGN-RPISOUND-UK` (7 streams)
- `CAMPAIGN-DCASE2020-ES` (5 streams)
- `CAMPAIGN-URBANSOUND-PL` (5 streams)
- `CAMPAIGN-AEROSONIC-AU` (6 streams)

**Forensic Audit Finding:** `CAMPAIGN-DCASE2020-ES` and `CAMPAIGN-URBANSOUND-PL` are **completely fabricated campaign identities**. None of the 23 continuous benchmark files originated from DCASE 2020 Task 1/5 or UrbanSound8K. In Phase 23, TAU DCASE and UrbanSound were formally evaluated and rejected because they consist of short 10-second isolated snippets rather than continuous audio streams.

### 5.2 Authoritative Campaign Mapping
As documented in [phase33_source_provenance_report.md](file:///E:/gunshot/gunshot/reports/phase33_source_provenance_report.md) and [phase33_campaign_reconciliation.csv](file:///E:/gunshot/gunshot/reports/phase33_campaign_reconciliation.csv), the 23 streams originate from four verified European and Australian continuous recording campaigns:

| Authoritative Campaign | Physical Geographic Location | Physical Stream Count | Total Duration (s) | Total Duration (hr) | Historical Phase 31 Identifier | False Phase 32 Narrative Label |
| :--- | :--- | :---: | :---: | :---: | :--- | :--- |
| **CAMPAIGN-SOUTHAMPTON-EXP1** | Southampton, Hampshire, UK | 10 streams | 8,970.0000 s | 2.4917 hr | `CAMPAIGN-RPISOUND-UK` | `CAMPAIGN-RPISOUND-UK` (in part) |
| **CAMPAIGN-CHEW-MAGNA** | Chew Magna, Somerset, UK | 1 stream | 890.0000 s | 0.2472 hr | `CAMPAIGN-CHEWMAGNA-UK` | `CAMPAIGN-RPISOUND-UK` (in part) |
| **CAMPAIGN-BILBAO** | Bilbao, Basque Country, Spain | 6 streams | 14,065.5755 s | 3.9071 hr | `CAMPAIGN-BILBAO-ES` | Falsely split into `DCASE2020` & `URBANSOUND-PL` |
| **CAMPAIGN-ADELAIDE-AEROSONIC** | Adelaide (YPAD), SA, Australia | 6 streams | 21,600.0000 s | 6.0000 hr | `CAMPAIGN-AEROSONIC-AU` | `CAMPAIGN-AEROSONIC-AU` |
| **Total Benchmark** | **4 Distinct Campaigns** | **23 streams** | **45,525.5755 s** | **12.6460 hr** | **Verified Ground Truth** | **Clerical Error Corrected** |

---

## 6. Factorial Defect Ablation Reproduction

Phase 33 fully reproduced the $2 \times 2$ factorial diagnostic ablation on the 6 AeroSonicDB continuous streams (6.0 hours, 21,600 seconds) using the raw instrumented traces from Phase 30.

### 6.1 Condition Alert Counts & Interaction Contrasts

| Condition ID | State-Machine Reset Logic | Animal Suppression Filter | Total Alerts | Gross FAR (alerts/hr) | Main Effect Contrasts |
| :---: | :---: | :---: | :---: | :---: | :--- |
| **Condition A** | Defective (Phase 17 Frozen) | **ON** | **108** | 18.00 | Baseline Defective Profile |
| **Condition B** | Defective (Phase 17 Frozen) | **OFF** | **130** | 21.67 | Suppr Effect (Defective): **-22 alerts** (-16.9%) |
| **Condition C** | Corrected (`else: active = []`) | **ON** | **66** | 11.00 | Reset Effect (Suppr ON): **+42 alerts** (+63.6%) |
| **Condition D** | Corrected (`else: active = []`) | **OFF** | **72** | 12.00 | Reset Effect (Suppr OFF): **+58 alerts** (+80.6%) |
| **Contrast** | **Interaction Effect** | — | — | — | **Interaction Contrast: -16 alerts** |

$$\text{Interaction Contrast} = (A - B) - (C - D) = (108 - 130) - (66 - 72) = -22 - (-6) = \mathbf{-16\text{ alerts}}$$

**Key Insight:** Animal suppression in a corrected state machine reduces false alerts by only **6 alerts (8.3%)**, whereas in the defective Phase 17 state machine it appeared to reduce alerts by **22 alerts (16.9%)**. The defective unconfirmed cluster retention artificially magnified the apparent benefit of animal suppression by **$3.67\times$** ($22 / 6$).

### 6.2 Condition D Audit: Equivalence vs Schema Divergence
A detailed comparison of Condition D vs the Phase 14 Balanced baseline established:
1. **Detection Timing:** Across all 6 streams and 72 alerts, Condition D produces **100% identical detection start and end timestamps ($0.0\text{ s}$ delta)** to Phase 14 Balanced.
2. **Schema Divergence:** Condition D uses `_create_phase17_event_record` (`duration`, float `score`, `raw_ensemble_score`, `crest_factor_db`), whereas Phase 14 returns `_create_phase14_event_record` (`duration_seconds`, rounded `peak_score`, `dispatch_path`, `verdict`).
3. **Formal Designation:** Condition D is officially labeled **`CORRECTED-CANDIDATE / SUPPRESSION-OFF`**.

### 6.3 Aircraft Flyover Fragmentation vs Ambient Noise Suppression
Analysis of the 25 aircraft overflight windows documented in [phase33_event_level_reconciliation.csv](file:///E:/gunshot/gunshot/reports/phase33_event_level_reconciliation.csv) revealed a striking split in suppression behavior:

| Acoustic Context | Window Exposure | Cond A (Suppr ON) | Cond B (Suppr OFF) | Suppression Delta | Acoustic Mechanism |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Aircraft Flyovers** (25 sequences) | 2,866.5 s (0.796 hr) | **78 alerts** | **72 alerts** | **+6 alerts (+8.3%)** | **Alert Fragmentation:** Continuous tonal jet/propeller noise drops below suppression thresholds, repeatedly splitting single events into bursts. |
| **Ambient / Non-Flyover** | 18,733.5 s (5.204 hr) | **30 alerts** | **58 alerts** | **-28 alerts (-48.3%)** | **True Suppression:** Suppresses intermittent broadband animal vocalizations and outdoor environmental noise. |
| **Total AeroSonicDB** | **21,600.0 s (6.000 hr)** | **108 alerts** | **130 alerts** | **-22 alerts (-16.9%)** | Net reduction conceals severe local overflight fragmentation. |

---

## 7. Wilcoxon and Statistical Reproduction

Phase 33 reconstructed all 23 stream-level paired observations between Phase 14 Balanced and Phase 17 Experimental, evaluated all 256 possible sign permutations, and resolved all historical $p$-value discrepancies.

### 7.1 Reconstructed Paired Observations
- Total Paired Streams: $N = 23$.
- Zero Differences ($D_i = 0$): **15 streams (65.2%)**.
- Non-Zero Differences ($D_i \neq 0$): **8 streams (34.8%)**.
- Observed Non-Zero Deltas ($P14 - P17$): $[+1, +2, +2, -2, -2, -8, -11, -13]$.
- Absolute Ranks: $[1.0, 3.5, 3.5, 3.5, 3.5, 6.0, 7.0, 8.0]$.
- Rank Sums: $W^+ = 8.0, W^- = 28.0$. Test statistic $T = \min(W^+, W^-) = \mathbf{8.0}$.

### 7.2 Complete Statistical Recomputation Matrix

| Statistical Test Variant | Test Statistic | Two-Sided $p$-Value | Methodological Basis & Formula | Concordance |
| :--- | :---: | :---: | :--- | :---: |
| **Exact Tied Permutation** | $W = 8.0$ | **$0.2109375$** | Enumeration of all $2^8 = 256$ sign permutations using actual tied ranks ($54 / 256$). | `REPRODUCED` |
| **Exact Untied Combinatorial** | $W = 8.0$ | **$0.1953125$** | Classical Wilcoxon null table with untied integer ranks $1 \dots 8$ ($50 / 256$). | `REPRODUCED` |
| **SciPy Asymptotic Normal** | $z = -1.41776$ | **$0.1562601$** | Normal approximation with tie-corrected variance $\text{Var} = 49.75$. | `REPRODUCED` |
| **Pratt Zero-Handling** | $W = 53.0$ | **$0.3675438$** | Ranks all 23 pairs including zeros; discards zero ranks post-computation. | `REPRODUCED` |
| **Exact Sign Test** | $k = 3, n = 8$ | **$0.7265625$** | Two-sided binomial test on positive vs negative signs ($3 \text{ vs } 5$). | `REPRODUCED` |

### 7.3 Methodological Resolution & Statistical Nuance
The variation in $p$-values reported across Phases 29 through 32 ($0.125 \to 0.156 \to 0.195 \to 0.211$) was entirely an artifact of differing test parameters (exact permutation vs. normal asymptotic approximation, tied vs. untied ranks, and zero-exclusion rules).

**Critical Statistical Nuance:**
All five statistical tests yield $p > 0.15$, confirming there is **no statistically significant difference** in false-alert rates between Phase 14 Balanced and Phase 17 Experimental. However, this failure to reject the null hypothesis is heavily driven by **low statistical power**: with only $n = 8$ informative non-zero pairs out of 23 streams, the benchmark is underpowered to detect moderate effect sizes. **Failure to reject the null hypothesis does NOT establish equivalence or non-inferiority.**

---

## 8. Pittsburgh Event-Matching Reproduction

Phase 33 audited the historical controlled gunfire validation results from the Pittsburgh DQV 2018 dataset (50 physical rounds across 20 audio recordings).

### 8.1 Resolution of Historical $p = 0.03125$ Superiority Claim
Phase 20 and Phase 22 historically reported that Phase 17 detected 33 rounds vs Phase 14's 27 rounds, claiming a statistically significant superiority ($p = 0.03125$ via one-sided sign test).

The forensic audit revealed that this claim was an **artifact of multi-credit alert reuse**:
- In rapid multi-shot burst sequences, single detector alerts were credited repeatedly against multiple physical round annotations.
- Phase 17 claimed **14 duplicate credits**; Phase 14 claimed **12 duplicate credits**.
- Under strict, physically valid **1-to-1 temporal matching** ($\pm 1.5\text{ s}$ matching window, one alert per round), the true physical detection counts drop dramatically.

### 8.2 Strict One-to-One Matching Contingency Analysis

| Metric / Level | Phase 14 Balanced | Phase 17 Experimental | Discordant Pairs | Exact Two-Sided McNemar $p$ | Statistical Verdict |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Physical Round Level** ($N = 50$) | **15 / 50 (30.0%)** | **19 / 50 (38.0%)** | **6 pairs** ($1 \text{ vs } 5$) | **$p = 0.21875$** | **Not Significant** |
| **Incident / Recording Level** ($N = 20$) | **15 / 20 (75.0%)** | **18 / 20 (90.0%)** | **3 pairs** ($0 \text{ vs } 3$) | **$p = 0.25000$** | **Not Significant** |

**Conclusion:** Strict 1-to-1 event matching eliminates the historical $p = 0.03125$ result. Phase 17 provides **no statistically significant improvement in controlled gunfire detection** over Phase 14 Balanced.

---

## 9. State-Machine Test Count Reconciliation

Phase 33 audited the 12 deterministic state-machine regression test vectors documented in [phase33_state_machine_audit.md](file:///E:/gunshot/gunshot/reports/phase33_state_machine_audit.md).

### 9.1 Verification of Failure and Pass Counts

| Profile / Model | Total Vectors | Vectors Passed | Vectors Failed | Pass Rate | True Failure Rate | Status |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Phase 14 Balanced** | 12 | **12** | 0 | 100.0% | 0.0% | `PASS_BASELINE` |
| **Phase 17 State-Reset Candidate** | 12 | **12** | 0 | 100.0% | 0.0% | `PASS_CANDIDATE` |
| **Phase 17 Experimental** | 12 | **4** | **8** | 33.3% | **66.7%** | `FAIL_DEFECT` |

### 9.2 Enumeration of Phase 17 Vector Results
- **8 Failing Vectors (66.7%):**
  - `VEC-01` (Single subthreshold ping flush)
  - `VEC-02` (Two subthreshold pings flush)
  - `VEC-03` (Subthreshold ping followed by quiet gap)
  - `VEC-04` (Subthreshold cluster followed by true event)
  - `VEC-07` (Alternating subthreshold pings)
  - `VEC-09` (Cooldown boundary unconfirmed retention)
  - `VEC-10` (Rapid subthreshold burst flush)
  - `VEC-12` (Subthreshold ping at file boundary)
- **4 Passing Vectors (33.3%):**
  - `VEC-05` (Clean confirmed single event)
  - `VEC-06` (Clean confirmed multi-frame event)
  - `VEC-08` (Silence baseline)
  - `VEC-11` (Clean dual-event sequence)

### 9.3 Clerical Error Resolution
The Phase 32 executive summary statement that Phase 17 "Failed 6/12 vectors" was a typographical clerical error ($12 - 6 = 6$). All data tables and test scripts in Phase 32 correctly enumerated 8 failing vectors. Phase 33 officially records the true Phase 17 failure rate as **8 / 12 (66.7%)**.

---

## 10. Deliverable and Archive Audit

Phase 33 audited the Phase 32 distribution archive and established the release package for Phase 33.

### 10.1 Phase 32 Distribution Archive Audit
- **Path:** `E:/gunshot/gunshot_detection_phase32.zip`
- **File Size:** **4,545,869 bytes** (Exact Match)
- **SHA-256 Checksum:** `b27bbb6336e3d0bb229ac10ade6c669b3d917d5ba58e91617c5c3cdd1eadddfb` (Exact Match)
- **Zip CRC Validation:** `PASS` (`testzip() -> None`)
- **Entries Count:** 41 entries (40 pre-manifest files + 1 manifest).
- **Deliverables Reconciliation:** Resolved the 17 workspace deliverables vs. 18 items in the deliverables index (Item 18 is the zip file itself).

### 10.2 Phase 33 Deliverables Index

#### Comprehensive Reports (7 files)
1. [phase33_final_report.md](file:///E:/gunshot/gunshot/reports/phase33_final_report.md) — Master Synthesis & Governance Resolution
2. [phase33_source_provenance_report.md](file:///E:/gunshot/gunshot/reports/phase33_source_provenance_report.md) — Workstream 1: Provenance & Duration Reconciliation
3. [phase33_factorial_reproduction.md](file:///E:/gunshot/gunshot/reports/phase33_factorial_reproduction.md) — Workstream 2: Factorial Defect Ablation Reproduction
4. [phase33_wilcoxon_reproduction.md](file:///E:/gunshot/gunshot/reports/phase33_wilcoxon_reproduction.md) — Workstream 3: Statistical Inference & Paired Permutation
5. [phase33_pittsburgh_reproduction.md](file:///E:/gunshot/gunshot/reports/phase33_pittsburgh_reproduction.md) — Workstream 4: Controlled Gunfire Event-Matching Audit
6. [phase33_state_machine_audit.md](file:///E:/gunshot/gunshot/reports/phase33_state_machine_audit.md) — Workstream 5: State-Machine Vector Count Resolution
7. [phase33_release_verification.md](file:///E:/gunshot/gunshot/reports/phase33_release_verification.md) — Workstream 6: Archive Integrity & Frozen Model Hashes

#### Data Records & Registries (11 files)
8. [phase33_canonical_stream_registry.csv](file:///E:/gunshot/gunshot/reports/phase33_canonical_stream_registry.csv) — 23-Stream WAV Header Registry
9. [phase33_campaign_reconciliation.csv](file:///E:/gunshot/gunshot/reports/phase33_campaign_reconciliation.csv) — Phase 31 vs Phase 32 Campaign Mappings
10. [phase33_duration_reconciliation.csv](file:///E:/gunshot/gunshot/reports/phase33_duration_reconciliation.csv) — Stream Duration Arithmetic & Rounding Resolution
11. [phase33_factorial_reproduction.csv](file:///E:/gunshot/gunshot/reports/phase33_factorial_reproduction.csv) — 4-Condition Stream Metrics (A=108, B=130, C=66, D=72)
12. [phase33_condition_config_hashes.json](file:///E:/gunshot/gunshot/reports/phase33_condition_config_hashes.json) — Condition D Trace & Model Hashes
13. [phase33_event_level_reconciliation.csv](file:///E:/gunshot/gunshot/reports/phase33_event_level_reconciliation.csv) — 25 Aircraft Overflights Log & Fragmentation Deltas
14. [phase33_paired_observations.csv](file:///E:/gunshot/gunshot/reports/phase33_paired_observations.csv) — 23 Paired Benchmark Deltas & Abs Ranks
15. [phase33_rank_and_permutation_audit.csv](file:///E:/gunshot/gunshot/reports/phase33_rank_and_permutation_audit.csv) — Full 256 Permutation Combinatorial Ranks
16. [phase33_statistical_test_results.json](file:///E:/gunshot/gunshot/reports/phase33_statistical_test_results.json) — Wilcoxon, Pratt, SciPy & Sign Test Results
17. [phase33_pittsburgh_matching_assignments.csv](file:///E:/gunshot/gunshot/reports/phase33_pittsburgh_matching_assignments.csv) — 50-Round Strict 1-to-1 Match Assignments
18. [phase33_pittsburgh_contingency_table.csv](file:///E:/gunshot/gunshot/reports/phase33_pittsburgh_contingency_table.csv) — Pittsburgh McNemar Contingency Tables

#### Code, Test Harness & Verification Records (4 files)
19. [reproduce_phase33_audit.py](file:///E:/gunshot/gunshot/scripts/reproduce_phase33_audit.py) — Independent Reproduction Engine
20. [test_phase33_reproduction.py](file:///E:/gunshot/gunshot/tests/test_phase33_reproduction.py) — Automated Pytest Verification Suite (15/15 PASS)
21. [phase33_test_execution_log.txt](file:///E:/gunshot/gunshot/reports/phase33_test_execution_log.txt) — Pytest Execution Log
22. [phase33_input_hash_manifest.json](file:///E:/gunshot/gunshot/reports/phase33_input_hash_manifest.json) — Comprehensive Input Hash Registry

---

## 11. Unresolved Issues and Limitations

1. **Benchmark Statistical Power:** With only $N = 23$ continuous streams and only $n = 8$ non-zero paired differences, the negative-exposure benchmark lacks statistical power to detect small-to-moderate improvements. Expanding the benchmark with independent continuous recordings remains necessary.
2. **Aircraft Overflight Susceptibility:** Both Phase 14 and Phase 17 exhibit high false-alert rates on low-altitude aircraft flyovers. Animal suppression exacerbates this by fragmenting single continuous flyovers into multiple discrete false alerts. A dedicated acoustic flight-path or Doppler classifier is required.
3. **State-Machine Architecture Defect:** Phase 17's state-machine defect (`active_cluster` retention across unconfirmed frames) remains present in `model_phase17.py` and renders it unsuitable for operational baseline deployment.
4. **Candidate Patch Quarantine:** The state-reset candidate patch resolves the 12 regression test vectors (12/12 PASS), but introduces schema divergence against Phase 14 baseline. It must remain quarantined as an experimental diagnostic tool.

---

## 12. Final Governance Decision

Based on the forensic audit findings across all six workstreams, the project governance board formally ratifies the following binding decisions:

1. **Phase 14 Balanced Retained as Default Research Baseline:**  
   Phase 14 Balanced remains the sole authoritative baseline model for all ongoing research and comparative evaluations. It is structurally sound and free from state-machine cluster retention defects.
2. **Phase 17 Experimental Promotion Rejection Reaffirmed:**  
   Phase 17 Experimental is definitively rejected for promotion to baseline. Its confirmed state-machine defect (8/12 test vector failure rate) and susceptibility to aircraft alert fragmentation make it unacceptable as an operational or baseline standard.
3. **Candidate Reset Patch Quarantined:**  
   The experimental state-reset patch (`experiments/phase31/model_phase17_state_reset_candidate.py`) is preserved strictly as a diagnostic reference. It will not be integrated into main release builds.
4. **Authoritative Benchmark Standards Established:**  
   The continuous negative-exposure benchmark is formally established as **23 streams, 4 campaigns (Southampton, Chew Magna, Bilbao, Adelaide), and 12.6460 hours (45,525.5755 seconds)**. Fictional campaign labels are permanently retired.
5. **Mandatory Life-Safety Operational Prohibition Reaffirmed:**  
   Under no circumstances may this experimental prototype be deployed for autonomous emergency response, active-shooter alerting, automated evacuation, or physical security.

