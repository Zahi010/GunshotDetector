# ANTIGRAVITY MASTER REPORT — PHASE 34
## Final Stream-Level Provenance Reconciliation & Benchmark Exposure Integrity Audit

> **MANDATORY SAFETY DESIGNATION**  
> **RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY**  
> *This experimental acoustic machine-learning software is uncertified and must never be deployed for autonomous emergency dispatch, tactical police response, active-shooter alerting, automated evacuation, building lockdown, or life-critical physical security. Use legally obtained recordings and safe audio playback only. Live-fire testing and hazardous acoustic experiments are strictly prohibited.*

---

## 1. Executive Summary

Phase 34 executed an exhaustive, read-only forensic audit to resolve the material campaign-duration discrepancy between Phase 31 and Phase 33. The audit examined all 23 physical benchmark audio files at the binary WAV header level, evaluated original dataset repositories, reconstructed stream-level and campaign-level detector metrics under both Cooldown Conventions A and B, audited campaign independence and cluster skew, and established the definitive historical discrepancy and statistical method registers.

### Workstream Formal Classification Summary

| Workstream | Investigation Focus | Key Finding / Resolution | Formal Status |
| :--- | :--- | :--- | :---: |
| **WS-1** | Exact 23-File Inventory & Provenance | 23 physical WAV files verified on disk with unique SHA-256 hashes, exact sample counts, and valid repository DOIs. | `REPRODUCED` |
| **WS-2** | Duration Discrepancy Reconciliation | Phase 31 duration allocations (5.5000h, 0.5833h, 0.5627h, 6.0000h) match physical WAV headers exactly. Phase 33 text report Section 5.2 contained an accidental clerical transposition from Phase 32 narrative. | `REPRODUCED WITH CORRECTION` |
| **WS-3** | Stream & Campaign Detector Metrics | Full reconstruction of alerts, gross exposure, and Cooldown Conventions A & B. Phase 17's massive Convention B excluded time on AeroSonic (6,283.28s) confirmed. | `REPRODUCED` |
| **WS-4** | Campaign Independence & Clustering | Only 4 genuinely independent campaigns exist. Adelaide accounts for 47.5% of exposure and 62.7% of alerts. Campaign-level testing ($K=4$) is fundamentally underpowered. | `REPRODUCED` |
| **WS-5** | Authoritative Statistical Method Register | Definitive mathematical classification of all historical tests. Exact tied permutation ($p = 0.2109375$) distinguished from untied combinatorial ($p = 0.1953125$) and asymptotic normal ($p = 0.1562601$). | `REPRODUCED` |
| **WS-6** | Historical Discrepancy Register & Retractions | Master register compiling 9 key historical discrepancies across Phases 27–33 with explicit blacklisted citations. | `REPRODUCED` |
| **WS-7** | Automated Test Harness & Release Package | 12 / 12 automated pytest verification tests passed (100%). Packaged `gunshot_detection_phase34.zip` with verified CRC. | `REPRODUCED` |

---

## 2. Safety Designation & Operational Boundary

### 2.1 Research Boundary
This experimental software is an uncertified research demonstration prototype. It has not undergone formal lifecycle safety verification, fault-tree hazard analysis, environmental stress screening, or mission-critical software compliance certification (e.g., DO-178C, IEC 61508, ISO 26262, UL 2524).

### 2.2 Operational Deployment Prohibition
Deployment of this software, in whole or in part, for life-critical physical security, autonomous 911 emergency dispatch, police tactical alerting, mass evacuation systems, or automated facility lockdowns is strictly and unconditionally prohibited.

### 2.3 Acoustic Testing Constraints
All analyses were conducted exclusively on legally acquired passive audio recordings and synthetic test vectors. Live-fire testing, pyrotechnic discharge, or hazardous acoustic field experiments are strictly prohibited.

---

## 3. Exact Physical Recording Inventory

The continuous negative-exposure benchmark consists of exactly **23 unique audio recordings** residing in the workspace repository. Every file was inspected via binary header analysis to verify its integrity:

| Stable File ID | Physical Filename | Relative Workspace Path | Size (Bytes) | SHA-256 (Truncated) | Native SR | Channels | Sample Count | Exact WAV Duration |
| :--- | :--- | :--- | :---: | :--- | :---: | :---: | :---: | :---: |
| `P27-NAT-STR-01` | `phase16_industrial_compressor_pneumatic_60min.wav` | `data/phase16_natural_continuous/...` | 115,200,044 | `d418574854a3...` | 16,000 | 1 | 57,600,000 | 3,600.0000 s (1.0000 h) |
| `P27-NAT-STR-02` | `phase16_industrial_exhaust_ventilation_30min.wav` | `data/phase16_natural_continuous/...` | 57,600,044 | `b1a463a68c5d...` | 16,000 | 1 | 28,800,000 | 1,800.0000 s (0.5000 h) |
| `P27-NAT-STR-03` | `phase16_industrial_concrete_mixer_30min.wav` | `data/phase16_natural_continuous/...` | 57,600,044 | `a850d9e6cb08...` | 16,000 | 1 | 28,800,000 | 1,800.0000 s (0.5000 h) |
| `P27-NAT-STR-04` | `phase16_industrial_monoblock_pump_30min.wav` | `data/phase16_natural_continuous/...` | 57,600,044 | `aea5bc9a3b7d...` | 16,000 | 1 | 28,800,000 | 1,800.0000 s (0.5000 h) |
| `P27-NAT-STR-05` | `phase16_traffic_road_arterial_30min.wav` | `data/phase16_natural_continuous/...` | 57,600,044 | `7943f8a208f4...` | 16,000 | 1 | 28,800,000 | 1,800.0000 s (0.5000 h) |
| `P27-NAT-STR-06` | `phase16_traffic_transit_train_30min.wav` | `data/phase16_natural_continuous/...` | 57,600,044 | `42a7747d3c55...` | 16,000 | 1 | 28,800,000 | 1,800.0000 s (0.5000 h) |
| `P27-NAT-STR-07` | `phase16_public_space_canteen_plaza_30min.wav` | `data/phase16_natural_continuous/...` | 57,600,044 | `344ac487063b...` | 16,000 | 1 | 28,800,000 | 1,800.0000 s (0.5000 h) |
| `P27-NAT-STR-08` | `phase16_percussion_acoustic_drums_30min.wav` | `data/phase16_natural_continuous/...` | 57,600,044 | `202788e0df6b...` | 16,000 | 1 | 28,800,000 | 1,800.0000 s (0.5000 h) |
| `P27-NAT-STR-09` | `phase16_indoor_appliance_washing_machine_30min.wav` | `data/phase16_natural_continuous/...` | 57,600,044 | `57920c070d66...` | 16,000 | 1 | 28,800,000 | 1,800.0000 s (0.5000 h) |
| `P27-NAT-STR-10` | `phase16_indoor_interior_laptop_exhaust_30min.wav` | `data/phase16_natural_continuous/...` | 57,600,044 | `16cce45702d2...` | 16,000 | 1 | 28,800,000 | 1,800.0000 s (0.5000 h) |
| `P27-NAT-STR-11` | `phase16_natural_weather_aquatic_reservoir_35min.wav` | `data/phase16_natural_continuous/...` | 67,200,044 | `017038b7395f...` | 16,000 | 1 | 33,600,000 | 2,100.0000 s (0.5833 h) |
| `P27-NAT-STR-12` | `phase17_urban_exterior_plaza_30min.wav` | `data/phase17_natural_continuous/...` | 10,326,702 | `12ed235135ad...` | 16,000 | 1 | 5,163,329 | 322.7081 s (0.0896 h) |
| `P27-NAT-STR-13` | `phase17_urban_interior_commercial_30min.wav` | `data/phase17_natural_continuous/...` | 10,472,616 | `22c86116a8eb...` | 16,000 | 1 | 5,236,286 | 327.2679 s (0.0909 h) |
| `P27-NAT-STR-14` | `phase17_urban_exterior_walkway_30min.wav` | `data/phase17_natural_continuous/...` | 11,323,952 | `506829204c5b...` | 16,000 | 1 | 5,661,954 | 353.8721 s (0.0983 h) |
| `P27-NAT-STR-15` | `phase17_urban_exterior_terrace_30min.wav` | `data/phase17_natural_continuous/...` | 10,327,584 | `1829d58075a8...` | 16,000 | 1 | 5,163,770 | 322.7356 s (0.0896 h) |
| `P27-NAT-STR-16` | `phase17_urban_interior_arcade_30min.wav` | `data/phase17_natural_continuous/...` | 12,145,660 | `5aa6cf560aa3...` | 16,000 | 1 | 6,072,808 | 379.5505 s (0.1054 h) |
| `P27-NAT-STR-17` | `phase17_urban_interior_hall_30min.wav` | `data/phase17_natural_continuous/...` | 10,222,166 | `4845470ae919...` | 16,000 | 1 | 5,111,061 | 319.4413 s (0.0887 h) |
| `P27-AERO-STR-01` | `1_AUDIO_16k.wav` | `data/phase27/derived_audio/...` | 115,200,044 | `1b6e241fe314...` | 16,000 | 1 | 57,600,000 | 3,600.0000 s (1.0000 h) |
| `P27-AERO-STR-02` | `2_AUDIO_16k.wav` | `data/phase27/derived_audio/...` | 115,200,044 | `75be01bb0c12...` | 16,000 | 1 | 57,600,000 | 3,600.0000 s (1.0000 h) |
| `P27-AERO-STR-03` | `3_AUDIO_16k.wav` | `data/phase27/derived_audio/...` | 115,200,044 | `358fa98be820...` | 16,000 | 1 | 57,600,000 | 3,600.0000 s (1.0000 h) |
| `P27-AERO-STR-04` | `4_AUDIO_16k.wav` | `data/phase27/derived_audio/...` | 115,200,044 | `4caa3539abaa...` | 16,000 | 1 | 57,600,000 | 3,600.0000 s (1.0000 h) |
| `P27-AERO-STR-05` | `5_AUDIO_16k.wav` | `data/phase27/derived_audio/...` | 115,200,044 | `8ef0f4f24baa...` | 16,000 | 1 | 57,600,000 | 3,600.0000 s (1.0000 h) |
| `P27-AERO-STR-06` | `6_AUDIO_16k.wav` | `data/phase27/derived_audio/...` | 115,200,044 | `77dcfb06a4bb...` | 16,000 | 1 | 57,600,000 | 3,600.0000 s (1.0000 h) |

Full registry with detector input details is saved in [phase34_canonical_23_stream_registry.csv](file:///E:/gunshot/gunshot/reports/phase34_canonical_23_stream_registry.csv).

---

## 4. Provenance Evidence

All 23 files map directly to publicly verifiable, persistent scholarly acoustic archives under open licenses:
1. **Southampton Industrial & Urban Ambient (10 files):**  
   - Source: *Raspberry Pi Sound Logger Project*, University of Southampton.
   - Persistent DOI: `10.5281/zenodo.7493820`. License: Creative Commons Attribution 4.0 International (CC BY 4.0).
2. **Chew Magna Rural Aquatic Soundscape (1 file):**  
   - Source: *Chew Magna Rural Soundscape Survey*, Somerset, UK.
   - Persistent DOI: `10.5281/zenodo.3938837`. License: CC BY 4.0.
3. **Bilbao Old Town Urban Soundscape (6 files):**  
   - Source: *Bilbao Old Town (Casco Viejo) Urban Acoustic Monitoring*, Bilbao, Spain.
   - Persistent DOI: `10.5281/zenodo.18716205` / `18561165`. License: CC BY 4.0.
4. **Adelaide Airport Perimeter Aviation Noise (6 files):**  
   - Source: *AeroSonicDB / YPAD-0523*, Blake Downward & Jon Nordby.
   - Persistent DOI: `10.5281/zenodo.10215080` / `8371595`. Associated Paper: arXiv:2311.06556. License: CC BY 4.0.

---

## 5. Phase 31 vs Phase 32 vs Phase 33 Duration Reconciliation

As detailed in [phase34_duration_discrepancy_analysis.md](file:///E:/gunshot/gunshot/reports/phase34_duration_discrepancy_analysis.md), the campaign duration discrepancy is fully resolved at the individual file level:

```
Campaign Allocations Across Reports vs. Physical Ground Truth:

1. Southampton (10 files):
   - Physical WAV Header: 19,800.0000 s = 5.5000 hr
   - Phase 31 Report:     19,800.0000 s = 5.5000 hr  [EXACT MATCH]
   - Phase 33 CSV:        19,800.0000 s = 5.5000 hr  [EXACT MATCH]
   - Phase 33 Text:        8,970.0000 s = 2.4917 hr  [DISCREPANCY: -3.0083 hr]

2. Chew Magna (1 file):
   - Physical WAV Header:  2,100.0000 s = 0.5833 hr
   - Phase 31 Report:      2,100.0000 s = 0.5833 hr  [EXACT MATCH]
   - Phase 33 CSV:         2,100.0000 s = 0.5833 hr  [EXACT MATCH]
   - Phase 33 Text:          890.0000 s = 0.2472 hr  [DISCREPANCY: -0.3361 hr]

3. Bilbao (6 files):
   - Physical WAV Header:  2,025.5755 s = 0.5627 hr
   - Phase 31 Report:      2,025.5755 s = 0.5627 hr  [EXACT MATCH]
   - Phase 33 CSV:         2,025.5755 s = 0.5627 hr  [EXACT MATCH]
   - Phase 33 Text:       14,065.5755 s = 3.9071 hr  [DISCREPANCY: +3.3444 hr]

4. Adelaide (6 files):
   - Physical WAV Header: 21,600.0000 s = 6.0000 hr
   - Phase 31 Report:     21,600.0000 s = 6.0000 hr  [EXACT MATCH]
   - Phase 33 CSV:        21,600.0000 s = 6.0000 hr  [EXACT MATCH]
   - Phase 33 Text:       21,600.0000 s = 6.0000 hr  [EXACT MATCH]
```

### Forensic Diagnosis of the Discrepancy
- **Phase 31 was physically correct:** Its duration figures match the WAV headers of all 23 files to 4 decimal places.
- **Phase 33's CSV registry was ALSO physically correct:** Summing the duration columns in `phase33_canonical_stream_registry.csv` yields 5.5000h for Southampton, 0.5833h for Chew Magna, and 0.5627h for Bilbao.
- **The Phase 33 text report Section 5.2 contained an accidental clerical transposition:**  
  When writing the narrative report, the author attempted to reconcile Phase 32's fabricated campaign totals ($9,860.0\text{ s}$ for UK, $14,066.0\text{ s}$ for Spain) and inadvertently mapped $14,065.5755\text{ s}$ to Bilbao, while splitting the $9,860.0\text{ s}$ into Southampton ($8,970\text{ s}$) and Chew Magna ($890\text{ s}$).
- **Authoritative Resolution:** The Phase 33 text report numbers are officially retracted. The authoritative campaign durations are **Southampton: 5.5000h, Chew Magna: 0.5833h, Bilbao: 0.5627h, Adelaide: 6.0000h (Total: 12.6460h)**.

---

## 6. Campaign Mapping and Independence

As established in [phase34_campaign_independence_audit.md](file:///E:/gunshot/gunshot/reports/phase34_campaign_independence_audit.md):
1. **Number of Genuinely Independent Campaigns:** Exactly **4 campaigns**.
2. **Acoustic and Hardware Coupling:**
   - The 10 Southampton files share acquisition hardware and British municipal background acoustics.
   - The 6 Bilbao files represent 6 spatial slices of Casco Viejo pedestrian canyons, sharing stone architectural reverberation.
   - The 6 Adelaide files share continuous airfield perimeter acoustic profiles and low-altitude jet overflights.
3. **Severe Exposure and Alert Skew:**
   - Adelaide accounts for **47.5% of gross exposure** and **62.7% of all observed alerts** (180 / 287 alerts).
   - Bilbao accounts for only **4.5% of exposure** ($0.5627\text{ hr}$) but generated **21.3% of all alerts** (61 alerts).
   - Southampton accounts for **43.5% of exposure** ($5.5000\text{ hr}$) but generated only **16.0% of alerts** (46 alerts).
4. **Statistical Testing Limitation:** Campaign-level comparisons have only $K = 4$ clusters ($k_{\text{eff}} = 3$ non-tied pairs), making campaign-level statistical hypothesis testing mathematically incapable of reaching $\alpha = 0.05$ significance.

---

## 7. Stream-Level Detector Metrics

The full 23-stream detector ledger is documented in [phase34_stream_level_detector_metrics.csv](file:///E:/gunshot/gunshot/reports/phase34_stream_level_detector_metrics.csv).

Key observations:
- **Zero-Alert Streams:** 7 streams produced zero alerts under both Phase 14 and Phase 17 (`P27-NAT-STR-01, 03, 04, 08, 09, 10, 11`).
- **Highest Alert Density:** `P27-AERO-STR-06` produced 22 P14 alerts and 35 P17 alerts; `P27-AERO-STR-05` produced 17 P14 alerts and 28 P17 alerts.
- **Urban Hotspot:** `P27-NAT-STR-05` (Southampton arterial traffic) produced 20 P14 alerts and 18 P17 alerts.

---

## 8. Campaign-Level Detector Metrics

Reconstructed from [phase34_campaign_level_metrics.csv](file:///E:/gunshot/gunshot/reports/phase34_campaign_level_metrics.csv):

| Campaign ID | Physical Streams | Gross Duration (hr) | P14 Alerts | P17 Alerts | P14 Gross FAR | P17 Gross FAR | P14 Conv A FAR | P17 Conv A FAR | P14 Conv B FAR | P17 Conv B FAR | Favored Detector |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Southampton** | 10 | 5.5000 h | 24 | 22 | 4.36 / hr | 4.00 / hr | 4.37 / hr | 4.01 / hr | 4.37 / hr | 4.01 / hr | Phase 17 (-2 alerts) |
| **Chew Magna** | 1 | 0.5833 h | 0 | 0 | 0.00 / hr | 0.00 / hr | 0.00 / hr | 0.00 / hr | 0.00 / hr | 0.00 / hr | Tied (0 alerts) |
| **Bilbao** | 6 | 0.5627 h | 32 | 29 | 56.87 / hr | 51.54 / hr | 58.72 / hr | 53.06 / hr | 58.72 / hr | 53.06 / hr | Phase 17 (-3 alerts) |
| **Adelaide** | 6 | 6.0000 h | 72 | 108 | 12.00 / hr | 18.00 / hr | 12.08 / hr | 18.18 / hr | 12.19 / hr | 25.38 / hr | Phase 14 (-36 alerts) |
| **Total Benchmark** | **23** | **12.6460 h** | **128** | **159** | **10.12 / hr** | **12.57 / hr** | **10.18 / hr** | **12.66 / hr** | **10.22 / hr** | **14.62 / hr** | **Phase 14 (-31 alerts)** |

---

## 9. Cooldown Exposure Recalculation

As detailed in [phase34_exposure_reproduction.md](file:///E:/gunshot/gunshot/reports/phase34_exposure_reproduction.md):
- **Convention A (Fixed 2-Second Blackout):**
  - Phase 14 excluded time: $255.84\text{ s}$ ($0.0711\text{ h}$), eligible exposure: $12.5749\text{ h}$, eligible FAR: **$10.18/\text{hr}$**.
  - Phase 17 excluded time: $316.56\text{ s}$ ($0.0879\text{ h}$), eligible exposure: $12.5581\text{ h}$, eligible FAR: **$12.66/\text{hr}$**.
- **Convention B (Event Span + Trailing Cooldown):**
  - Phase 14 excluded time: $453.92\text{ s}$ ($0.1261\text{ h}$), eligible exposure: $12.5199\text{ h}$, eligible FAR: **$10.22/\text{hr}$**.
  - Phase 17 excluded time: **$6,385.20\text{ s}$ ($1.7737\text{ h}$)**, eligible exposure: **$10.8723\text{ h}$**, eligible FAR: **$14.62/\text{hr}$**.
  - In Adelaide AeroSonicDB, Phase 17 excluded **$6,283.28\text{ s}$ (29.1% of exposure)**, proving severe aircraft overflight fragmentation and cluster retention pathology.

---

## 10. Statistical Method Register

As recorded in [phase34_authoritative_statistical_method_register.csv](file:///E:/gunshot/gunshot/reports/phase34_authoritative_statistical_method_register.csv) and [phase34_statistical_reconciliation.md](file:///E:/gunshot/gunshot/reports/phase34_statistical_reconciliation.md):

| Method ID | Method Description | Unit of Analysis | $n_{\text{eff}}$ | Test Statistic | Two-Sided $p$-Value | Status & Governance Note |
| :---: | :--- | :---: | :---: | :---: | :---: | :--- |
| `STAT-01` | **SciPy Asymptotic Normal** | Stream ($N=23$) | 8 | $z = -1.4178$ | **$0.1562601$** | Valid software approximation with tie-corrected variance ($\text{Var}=49.75$). |
| `STAT-02` | **Exact Tied Permutation** | Stream ($N=23$) | 8 | $W = 8.0$ | **$0.2109375$** | **Definitive gold-standard exact test for discrete tied ranks ($54/256$).** |
| `STAT-03` | **Exact Untied Combinatorial** | Stream ($N=23$) | 8 | $W = 8.0$ | **$0.1953125$** | Classical Wilcoxon table ($50/256$). Do not cite as tied result. |
| `STAT-04` | **Pratt Zero-Handling** | Stream ($N=23$) | 23 | $W = 53.0$ | **$0.3675438$** | Overly conservative zero-ranking method. |
| `STAT-05` | **Exact Binomial Sign Test** | Stream ($N=23$) | 8 | $k = 3$ | **$0.7265625$** | Sign test on positive vs negative signs ($3 \text{ vs } 5$). |
| `STAT-06` | **Historical Multi-Credit Sign Test** | Round ($N=50$) | 6 | $k = 0$ | $0.03125$ | **Retracted historical artifact**; driven by multi-credit alert reuse. |
| `STAT-07` | **Strict 1-to-1 McNemar (Pittsburgh)** | Round ($N=50$) | 6 | Discordant 1 vs 5 | **$0.21875$** | Valid exact test on 50 physical rounds (15 P14 vs 19 P17). Not significant. |
| `STAT-08` | **Incident McNemar (Pittsburgh)** | Recording ($N=20$) | 3 | Discordant 0 vs 3 | **$0.25000$** | Valid exact test on 20 recordings (15 P14 vs 18 P17). Not significant. |

**Doctrine:** All valid statistical tests confirm $p > 0.15$. However, this is heavily driven by low statistical power ($n_{\text{eff}} = 8$). **Failure to reject the null hypothesis does NOT establish equivalence or non-inferiority.**

---

## 11. Historical Report Discrepancy Register

Compiled in [phase34_historical_discrepancy_register.csv](file:///E:/gunshot/gunshot/reports/phase34_historical_discrepancy_register.csv) and [phase34_historical_corrections.md](file:///E:/gunshot/gunshot/reports/phase34_historical_corrections.md).

All past references to fictional campaigns (`DCASE2020-ES`, `URBANSOUND-PL`), fabricated stream counts (`7, 5, 5, 6`), rounded durations (`45,526.0s / 12.6461h`), prose typos (`Failed 6/12 vectors`), transposed Phase 33 narrative durations (`8,970s / 890s / 14,065.6s`), and multi-credit gunfire significance ($p = 0.03125$) are **permanently retracted**.

---

## 12. Reproducibility Results

All Phase 34 calculations and registers are fully automated and verified:
- Independent engine: [reproduce_phase34_audit.py](file:///E:/gunshot/gunshot/scripts/reproduce_phase34_audit.py).
- Automated test suite: [test_phase34_reproduction.py](file:///E:/gunshot/gunshot/tests/test_phase34_reproduction.py).
- Test execution log: [phase34_test_execution_log.txt](file:///E:/gunshot/gunshot/reports/phase34_test_execution_log.txt) confirms **12 / 12 tests PASSED (100.0%)** in 1.81 seconds.
- Input hash registry: [phase34_input_hash_manifest.json](file:///E:/gunshot/gunshot/reports/phase34_input_hash_manifest.json) confirms bit-for-bit invariance of all baseline model inputs and historical zip archives.

---

## 13. Unresolved Issues & Limitations

1. **Benchmark Statistical Power:** With only 8 non-zero difference streams out of 23, the benchmark cannot detect small-to-moderate performance differences. Expanding the benchmark with continuous audio from independent geographic regions remains necessary.
2. **Aircraft Overflight Susceptibility:** Both Phase 14 and Phase 17 exhibit severe false alerting on low-altitude aircraft flyovers. Animal suppression exacerbates this by fragmenting single flyovers into alert bursts.
3. **State-Machine Architecture Defect:** Phase 17's state-machine defect (`active_cluster` retention across unconfirmed frames) remains present in `model_phase17.py`, resulting in an 8/12 regression test failure rate.
4. **Candidate Patch Quarantine:** The state-reset candidate patch resolves the 12 regression test vectors (12/12 PASS), but introduces schema divergence against Phase 14 baseline. It remains quarantined as an experimental diagnostic tool.

---

## 14. Final Governance Decision

Based on the forensic audit findings across all seven workstreams, the project governance board formally ratifies the following binding decisions:

1. **Phase 14 Balanced Reaffirmed as Sole Default Research Baseline:**  
   Phase 14 Balanced remains the default research baseline for all ongoing evaluations. It is structurally sound, verified in timing, and free from state-machine cluster retention defects.
2. **Rejection of Phase 17 Promotion Reaffirmed:**  
   Phase 17 Experimental is definitively rejected for baseline promotion due to its confirmed state-machine reset defect (8/12 failure rate) and acoustic aircraft-alert fragmentation.
3. **Candidate Reset Patch Quarantined:**  
   The experimental state-reset patch (`experiments/phase31/model_phase17_state_reset_candidate.py`) is preserved strictly as a diagnostic prototype.
4. **Authoritative Benchmark Standards Established:**  
   The continuous negative-exposure benchmark is formally established as **23 streams, 4 campaigns (Southampton: 5.5000h, Chew Magna: 0.5833h, Bilbao: 0.5627h, Adelaide: 6.0000h), and exactly 45,525.5755 seconds (12.6460 hours)**.
5. **Absolute Prohibition on Life-Safety Operational Deployment:**  
   This software is an uncertified research prototype. Operational deployment for active-shooter alerting, automated evacuation, or physical security remains strictly prohibited.

