# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY

**MANDATORY SAFETY DESIGNATION:**
This experimental acoustic machine-learning software is uncertified and must never be deployed for autonomous emergency dispatch, tactical police response, active-shooter alerting, automated evacuation, building lockdown, or life-critical physical security.

Use legally obtained recordings and safe audio playback only. Live-fire testing and hazardous acoustic experiments are strictly prohibited.

---

# PHASE 27 FINAL TECHNICAL AUDIT REPORT
## Authorized AeroSonicDB Acquisition, Independent Continuous-Audio Ingestion & Statistical Inference Correction

**Phase Designation:** `PHASE_27_AUTHORIZED_AEROSONICDB_ACQUISITION_AND_STATISTICAL_CORRECTION`  
**Evaluation Status:** `COMPLETED_AEROSONIC_INGESTION_AND_STATISTICAL_CORRECTION`  
**Default Research Baseline:** `Phase 14 Balanced` (`model_phase14.py`, SHA-256: `a268551604ae8b73068435ff10ab3d265065f56e0679757fca5b6bf0f061c065`)  
**Selectable Experimental Profile:** `Phase 17 Experimental` (`model_phase17.py`, SHA-256: `e2b262b866fdd5d7f1a4ab91a7b8b9bac189ee8cc7a78603b3544ca1579fb819`)  
**Baseline Retention Decision:** **`RETAIN_PHASE_14_BALANCED_AS_DEFAULT_RESEARCH_BASELINE`** (Phase 17 promotion conclusively **`REJECTED`**)

---

## 1. Executive Summary

Phase 27 executed a multi-workstream expansion of the acoustic gunshot detection continuous negative-audio benchmark, resolving key data acquisition challenges, correcting historical statistical reporting discrepancies, and conducting an extensive matched evaluation across 23 continuous field recordings.

### Key Milestones Achieved:
1. **Lawful, Authorized Data Acquisition (Workstream A):**
   - Successfully acquired the **AeroSonicDB / YPAD-0523** environmental audio archive (`env_audio.zip`) via Zenodo's official InvenioRDM REST API endpoint (`https://zenodo.org/api/records/10215080/files/env_audio.zip/content`).
   - Resolved the Phase 26 HTTP 403 Cloudflare blockage without bypassing, intercepting, or spoofing any anti-bot security controls, strictly adhering to research compliance protocols.
   - Verified archive integrity: exact size 495,276,974 bytes (~472.33 MiB), MD5 `8c042dc817f459e80ac2491ffc8dd1cd` (exact match to Zenodo repository manifest), SHA-256 `7ebfb4aec3ec41a64db326b7b28789c0d6346a6439182ceb1e9d22f401f3438a`, and 100% clean zip CRC check (`zipfile.testzip()`).
2. **Audio Forensic Validation & Expansion (Workstream B):**
   - Extracted six 1-hour unbroken continuous recordings (`1_AUDIO.wav` through `6_AUDIO.wav`) recorded in the civilian airspace and residential perimeter of Adelaide International Airport (YPAD), South Australia, Australia.
   - Verified signal integrity: zero sample dropouts, zero digital clipping, silence ratio < 0.01%, 100% decoding success.
   - Standardized from native 22,050 Hz to 16,000 Hz using high-order polyphase rational factor filtering (`resample_poly(320, 441)`).
   - Provenance audit confirmed zero munitions discharge and zero firearm events, qualifying all 6.0000 gross hours as `VERIFIED_NEGATIVE`.
   - The cumulative continuous negative benchmark expanded from 17 streams (6.6460 gross hours) to **23 streams (12.6460 gross hours / 45,525.58 seconds)** across 4 geographically independent campaigns (UK, Spain, France, Australia).
3. **Historical Statistical Reconciliation (Workstream C):**
   - Proven that the historical reported statistic $W = 10.0, p = 0.125$ for $N_r = 3$ discordant pairs was mathematically impossible (maximum possible rank sum for $n=3$ is $(3 \times 4)/2 = 6.0$); established that $W = 10.0$ was a transcription error from Phase 21 LOPO analysis (`+10.0%`), and $p = 0.125$ was an exact **one-sided sign test probability** ($(1/2)^3 = 0.125$, two-sided $p = 0.250$).
   - Proven that the historical reported count-level Variance-to-Mean Ratio (VMR > 8.0) was mathematically distorted by an **11.27x variation in stream durations**; normalized rate overdispersion reflects spatial heterogeneity across differing urban acoustic environments.
4. **Frozen Model Continuous Evaluation (Workstream D):**
   - On the 6 newly acquired AeroSonicDB streams (6.0000 hours), Phase 14 Balanced triggered **72 false alerts** (12.0000 alerts/hr), while Phase 17 Experimental triggered **108 false alerts** (18.0000 alerts/hr).
   - Forensic distractor analysis discovered that Phase 17 suffers from **alert cluster fragmentation**: elevated release hysteresis (`0.48` vs `0.40`) and animal-suppression micro-dips prematurely terminate active continuous aircraft flyover alerts and immediately re-trigger, fragmenting single flyovers into 2 to 4 separate false alerts.
   - Across the entire cumulative 23-stream benchmark (12.6460 gross hours), Phase 14 logged **128 false alerts** (10.1218 /hr) versus Phase 17's **159 false alerts** (12.5732 /hr). Phase 14 produced **31 fewer false alerts** (-19.5%).
   - Paired Wilcoxon signed-rank test across all 23 streams yielded **$W = 8.0, p = 0.1953 \ge 0.05$** (two-sided) and **$p = 0.9258$** (one-sided for Phase 17 superiority).
   - **Conclusion:** Phase 17 Experimental provides zero statistically significant benefit and performs drastically worse on continuous aviation distractors (+50% alerts). Phase 14 Balanced is retained as the default research baseline.

---

## 2. Frozen Baseline Verification

In strict accordance with the Mandatory Frozen-Model Policy, all detector architectures, weights, and configurations were verified prior to evaluation. No model files were modified.

| Model File | Detector Role | Expected SHA-256 | Actual SHA-256 | Size (Bytes) | Verification Status |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `model_phase14.py` | **Default Research Baseline** | `a268551604ae8b73068435ff10ab3d265065f56e0679757fca5b6bf0f061c065` | `a268551604ae8b73068435ff10ab3d265065f56e0679757fca5b6bf0f061c065` | 23,340 | **MATCH_CONFIRMED** |
| `model_phase17.py` | **Selectable Experimental Profile** | `e2b262b866fdd5d7f1a4ab91a7b8b9bac189ee8cc7a78603b3544ca1579fb819` | `e2b262b866fdd5d7f1a4ab91a7b8b9bac189ee8cc7a78603b3544ca1579fb819` | 29,067 | **MATCH_CONFIRMED** |
| `model_phase13.py` | Historical Comparator | `68585039a4a4fdb7978a99f5e2a72c0ad5a9523127ec24a1338fbedd1c1231e6` | `68585039a4a4fdb7978a99f5e2a72c0ad5a9523127ec24a1338fbedd1c1231e6` | 22,252 | **MATCH_CONFIRMED** |
| `model_phase9.py` | Historical Comparator | `85cedd9f5b988ecafb1eae7de9630ee3d6a387ded6ef732e0efb7c3b496f132a` | `85cedd9f5b988ecafb1eae7de9630ee3d6a387ded6ef732e0efb7c3b496f132a` | 17,719 | **MATCH_CONFIRMED** |

All historical release archives (Phase 26 through Phase 20) in `E:/gunshot` were verified:
- `gunshot_detection_phase26.zip`: `df8d3e0165c98b1b093e93d6edf12a43a6c831c6818122a23da4c3db29ea5c01` (8,218,546 B) — **MATCH_CONFIRMED**
- `gunshot_detection_phase25.zip`: `cc2349c46ebaeed859ed300a0b2f402e62bf9c20994d2112a15ec47cd656425e` (8,213,032 B) — **MATCH_CONFIRMED**
- `gunshot_detection_phase24.zip`: `3e732e0716160f2d77b71ceff3e01a49f3d933e397bf29bf222fec771a8832b8` (8,215,859 B) — **MATCH_CONFIRMED**
- `gunshot_detection_phase23.zip`: `5ce4e64715829d9b52111b6d6322f251976e1ce99e829d9dfbe0858a7e1644c8` (8,194,616 B) — **MATCH_CONFIRMED**
- `gunshot_detection_phase22.zip`: `160d327072c3515e945ca5cdf89038f14b6ef1919b1e4865278affab52ad4de5` (8,199,741 B) — **MATCH_CONFIRMED**
- `gunshot_detection_phase21.zip`: `b065747b0e6118d228336bee7f8c3811890b638a25070d3ce2a047c329b3e225` (8,211,219 B) — **MATCH_CONFIRMED**
- `gunshot_detection_phase20.zip`: `dda7427f2dbffcb178f6d9ade0abb80fbfc491751f04de5dc0db1b4731c31c89` (8,205,938 B) — **MATCH_CONFIRMED**

---

## 3. Workstream A — Source Metadata Verification & Authorized Data Acquisition

### 3.1 Metadata Verification
The original source records on Zenodo were reverified:
- **Zenodo Record ID:** `10215080` (Concept: `8000468`, Release: `8371595`)
- **Digital Object Identifier (DOI):** `10.5281/zenodo.10215080`
- **Title:** AeroSonicDB: An aerial acoustic dataset for aircraft detection and classification
- **Publication Date:** 2023-11-20
- **Authors:** Blake Downward (acknowledged Jon Nordby, Soundsensing AS)
- **Associated Publication:** arXiv:2311.06368
- **License Verification:** The repository license was audited. While Phase 26 literature references indicated CC BY 4.0, direct inspection of `LICENSE.txt` and repository metadata confirmed the true license is **CC BY-NC 4.0** (Creative Commons Attribution NonCommercial 4.0 International). This permits non-commercial academic research reproduction, but prohibits commercial deployment.

### 3.2 Resolution of Acquisition Path (Cloudflare vs. REST API)
- **Historical Barrier in Phase 26:** Automated requests targeting the public web URL `https://zenodo.org/record/10215080/files/env_audio.zip` received an HTTP 403 Forbidden response caused by Cloudflare bot management. In Phase 26, the agent properly halted to avoid bypassing anti-bot controls.
- **Phase 27 Sanctioned Access Resolution:** CERN / Zenodo operates an official InvenioRDM REST API designed specifically for programmatic retrieval of research data. The official endpoint `https://zenodo.org/api/records/10215080/files/env_audio.zip/content` is completely open, documented, and requires no authentication or web scraping.
- **Acquisition Execution:** A standard Python HTTP streaming request to the sanctioned REST API endpoint succeeded with HTTP 200, downloading `env_audio.zip` (495,276,974 bytes) in 38.6 seconds.
- **Compliance Certification:** Zero access controls were bypassed, zero credentials spoofed, zero CAPTCHAs solved, and zero bot-detection measures circumvented.

### 3.3 Archive Download Integrity
- **Target File:** `env_audio.zip`
- **Expected Size:** 495,276,974 bytes (~472.33 MiB)
- **Expected MD5 (from Zenodo API):** `8c042dc817f459e80ac2491ffc8dd1cd`
- **Computed Local MD5:** `8c042dc817f459e80ac2491ffc8dd1cd` (**EXACT MATCH**)
- **Computed Local SHA-256:** `7ebfb4aec3ec41a64db326b7b28789c0d6346a6439182ceb1e9d22f401f3438a`
- **Zip CRC Integrity:** Complete extraction via Python `zipfile` tested 0 corrupted files across all members.

---

## 4. Workstream B — Audio Forensic Validation & Benchmark Expansion

### 4.1 Ingestion and Signal Inspection
All six raw audio files (`1_AUDIO.wav` to `6_AUDIO.wav`) were extracted to `data/phase27/original_audio/env_audio/` and forensically audited:
- **Audio Format:** 16-bit PCM Mono WAV at 22,050 Hz.
- **Duration:** Exactly 3,600.00 seconds (1.0000 hour / 79,380,000 samples) per recording. Total duration: 21,600.00 seconds (6.0000 gross hours).
- **Decoding & Framing Integrity:** 100% decoding success; zero corrupt frames or header anomalies.
- **Front-End Clipping:** 0 clipped samples (|amp| >= 0.9999). Peak signal levels ranged between 0.412 and 0.884 full-scale.
- **Silence Audit:** Signal dropout ratio (|amp| < 0.0001) was < 0.01% across all files.

### 4.2 Standardized Resampling Lineage
- **Method:** Standardized to detector native sample rate (16,000 Hz) using high-order polyphase rational factor filtering (`scipy.signal.resample_poly(arr, 320, 441)`).
- **Derived Files:** Written to `data/phase27/derived_audio/` as `1_AUDIO_16k.wav` through `6_AUDIO_16k.wav` (each exactly 115,200,044 bytes, 57,600,000 samples, 3,600.00 seconds).

### 4.3 Negative-Label Eligibility Verification
- **Geographic Setting:** Adelaide Airport (YPAD) perimeter and surrounding suburban corridors in South Australia, Australia.
- **Regulatory Framework:** Monitored civilian airspace under Airservices Australia and South Australia Police jurisdiction. Live firearm discharge is illegal in suburban airport perimeters.
- **Dataset Ground Truth:** AeroSonicDB is curated exclusively for aircraft acoustics (commercial jet airliners, turboprops, helicopters, and urban background). Annotations contain zero ballistic, explosive, or impulsive firearm events.
- **Eligibility Determination:** All six recordings (`P27-AERO-STR-01` to `P27-AERO-STR-06`) meet all criteria for **`VERIFIED_NEGATIVE`** status.

### 4.4 Cumulative Benchmark Composition (23 Streams / 4 Campaigns)
The continuous negative audio benchmark now comprises:
1. `CAMPAIGN-RPISOUND-UK`: 4 recordings, 2.5000 hours (Industrial compressor, ventilation, pump, generator).
2. `CAMPAIGN-DCASE2020-ES`: 7 recordings, 2.1460 hours (Spanish urban parks, public squares, suburban streets).
3. `CAMPAIGN-URBANSOUND8K-FR`: 6 recordings, 2.0000 hours (French street ambiance, construction, street music).
4. `CAMPAIGN-AEROSONIC-AU`: 6 recordings, 6.0000 hours (Australian airport perimeter, jet flyovers, aviation ambient).
**Total Cumulative Exposure:** **12.6460 gross hours (45,525.58 seconds)**.

---

## 5. Workstream C — Historical Statistical Reconciliation

Phase 27 audited the mathematical foundations and reporting anomalies from previous phases (Phases 23–26).

### 5.1 Reconciliation of Historical Wilcoxon Statistic ($W = 10.0, p = 0.125$)
- **The Historical Anomaly:** Phase 24 and Phase 26 reported a paired Wilcoxon signed-rank result of $W = 10.0, p = 0.125$ for the comparison of Phase 14 vs Phase 17 across 17 streams.
- **Mathematical Infeasibility:** Across the 17 streams, exactly 3 streams had non-zero differences (`[2, 2, 1]`, all in favor of Phase 17), while 14 streams were tied (`d = 0`). For $N_r = 3$ non-zero pairs, the maximum possible rank sum is:
  $$\sum_{i=1}^3 i = \frac{3 \times 4}{2} = 6.0$$
  Therefore, an obtained rank sum of $W = 10.0$ is **mathematically impossible**.
- **Root Cause Identified:** 
  1. In Phase 21, the LOPO generalization analysis reported a $+10.0\%$ round-recall improvement. This string was inadvertently transcribed into the Wilcoxon summary.
  2. The actual Wilcoxon test statistic for differences `[2, 2, 1]` is $W^+ = 6.0, W^- = 0.0, W = \min(W^+, W^-) = 0.0$.
  3. The reported $p = 0.125$ was not a Wilcoxon p-value, but the **exact one-sided sign test probability**:
     $$P(X \ge 3 \mid n=3, p=0.5) = (0.5)^3 = 0.125$$
  4. The true two-sided sign-test p-value was $p = 0.250$, and the exact two-sided Wilcoxon p-value was $p = 0.250$ (when ties are discarded). Neither metric reached statistical significance ($\alpha = 0.05$).

### 5.2 Resolution of Count-Level VMR vs. Spatial Overdispersion
- **The Historical Claim:** Phase 26 asserted that because count-level Variance-to-Mean Ratio (VMR) exceeded 8.0, the Poisson distribution was invalidated, casting doubt on Garwood confidence intervals.
- **Mathematical Audit:**
  - In the 17 historical streams, stream durations varied by **11.27x** (from 319.4 seconds to 3,600.0 seconds).
  - Even under an identical underlying Poisson rate $\lambda$, count variance is inflated when sampling exposure $T_i$ varies:
    $$\text{Var}(K_i) = \lambda \cdot E[T_i] + \lambda^2 \cdot \text{Var}(T_i)$$
  - When normalized to standardized hourly rates (/hr), the mean rate is $8.4261$ alerts/hr with an empirical variance of $604.22$, yielding an apparent rate dispersion of $71.7$.
- **Scientific Reconciliation:**
  - This overdispersion is **not a violation of temporal Poisson stationary arrivals within a stream**; it is the direct manifestation of **spatial heterogeneity across distinct environments** (e.g., quiet residential parks with 0.0 alerts/hr versus active industrial construction with 107.8 alerts/hr).
  - Consequently, the exact Garwood Poisson confidence interval remains the mathematically correct, conservative bound for the true arrival rate **conditioned on a specific acoustic environment**.
  - Cross-campaign aggregate uncertainty must be modeled using compound Poisson or negative binomial formulations rather than unweighted count pooling.

---

## 6. Workstream D — Frozen Model Evaluation on Expanded Benchmark

### 6.1 AeroSonicDB Evaluation Results (6.0000 Gross Hours)

| Recording ID | Filename | Environment | Phase 14 Alerts | P14 Rate (/hr) | P14 Cooldown Excl (s) | Phase 17 Alerts | P17 Rate (/hr) | P17 Cooldown Excl (s) | Delta Alerts (P14 - P17) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `P27-AERO-STR-01` | `1_AUDIO_16k.wav` | Aviation / Urban | 15 | 15.00 | 55.28 s | 23 | 23.00 | 677.28 s | **-8 (Phase 14 +8)** |
| `P27-AERO-STR-02` | `2_AUDIO_16k.wav` | Aviation / Urban | 3 | 3.00 | 9.76 s | 5 | 5.00 | 668.40 s | **-2 (Phase 14 +2)** |
| `P27-AERO-STR-03` | `3_AUDIO_16k.wav` | Aviation / Urban | 7 | 7.00 | 32.72 s | 7 | 7.00 | 2574.16 s | **0 (Tied)** |
| `P27-AERO-STR-04` | `4_AUDIO_16k.wav` | Aviation / Urban | 8 | 8.00 | 29.84 s | 10 | 10.00 | 614.48 s | **-2 (Phase 14 +2)** |
| `P27-AERO-STR-05` | `5_AUDIO_16k.wav` | Aviation / Urban | 17 | 17.00 | 92.48 s | 28 | 28.00 | 1009.84 s | **-11 (Phase 14 +11)** |
| `P27-AERO-STR-06` | `6_AUDIO_16k.wav` | Aviation / Urban | 22 | 22.00 | 121.92 s | 35 | 35.00 | 739.12 s | **-13 (Phase 14 +13)** |
| **AeroSonicDB Subtotal** | **6 Recordings** | **6.0000 hr** | **72** | **12.0000** | **342.00 s** | **108** | **18.0000** | **6,283.28 s** | **-36 (Phase 14 Superior)** |

### 6.2 Forensic Distractor Analysis: Cluster Fragmentation in Phase 17
In AeroSonicDB, Phase 17 produced **36 more false alerts** (+50.0%) than Phase 14 Balanced. Detailed signal forensics isolated the physical and algorithmic mechanism:
1. **Prolonged Broadband Disturbance:** Commercial jet aircraft flyovers generate intense acoustic pressure lasting 30 to 80 seconds, with broadband energy spanning 100 Hz to 3 kHz and elevated crest factors (12–16 dB).
2. **Phase 14 Hysteresis Clustering:** Phase 14 utilizes an activation threshold `threshold_on = 0.55` and release threshold `threshold_off = 0.40`. During a 60-second flyover, the continuous jet roar stays above 0.40, causing Phase 14 to log **exactly one single alert** with a 2.0-second cooldown window.
3. **Phase 17 Threshold Dips & Animal Suppression:** Phase 17 raised `threshold_off = 0.48` and added an animal-sound suppression heuristic. During high-velocity jet shearing and turbulent gusts, micro-fluctuations in high-frequency spectral ratios periodically trigger the animal classifier or cause intermediate scores to dip below 0.48 for 200–300 ms.
4. **Premature Termination & Re-triggering:** Phase 17 prematurely terminates the alert event. As the aircraft continues overhead, the score re-exceeds 0.55 within hundreds of milliseconds, triggering a second, third, or fourth alert for the **same physical airplane**.
5. **Operational Blindness:** Because Phase 17 fragmented flyovers into repeated alerts, its post-alert cooldown suppression excluded **6,283.28 seconds (1.7454 hours)** across the 6-hour exposure, blinding the detector for **29.1% of the entire monitored duration**.

---

## 7. Cumulative 23-Stream Head-to-Head Comparison

### 7.1 Tripartite Denominator Accounting Across Full Benchmark

| Evaluation Metric | Phase 14 Balanced (Default Research Baseline) | Phase 17 Experimental (Selectable Profile) | Delta (P17 - P14) | Assessment |
| :--- | :--- | :--- | :--- | :--- |
| **Monitored Continuous Streams** | 23 | 23 | 0 | Matched |
| **Independent Urban Campaigns** | 4 | 4 | 0 | Matched |
| **Gross Monitored Duration** | 12.6460 hrs (45,525.58 s) | 12.6460 hrs (45,525.58 s) | 0.0 hrs | Matched |
| **Total Observed False Alerts** | **128** | **159** | **+31 alerts (+24.2%)** | **Phase 14 Superior** |
| **Gross False Alert Rate** | **10.1218 /hr** | **12.5732 /hr** | **+2.4514 /hr** | **Phase 14 Superior** |
| **Total Cooldown Excluded Time** | 455.52 s (0.1265 hr) | 6,381.76 s (1.7727 hr) | +5,926.24 s (+1301%) | **Phase 14 Vastly Superior** |
| **Net Eligible Exposure** | 12.5195 hrs | 10.8732 hrs | -1.6463 hrs (-13.1%) | Phase 14 Retains 99.0% |
| **Eligible False Alert Rate** | **10.2241 /hr** | **14.6231 /hr** | **+4.3990 /hr (+43.0%)** | **Phase 14 Superior** |
| **95% Poisson Garwood CI** | [8.5303, 12.1643] /hr | [12.4419, 17.0772] /hr | Disjoint Lower Bound | **Phase 14 Superior** |
| **Mean Time Between False Alerts** | 0.0978 hr (5.87 min) | 0.0684 hr (4.10 min) | -0.0294 hr (-30.1%) | **Phase 14 Superior** |

### 7.2 Paired Non-Parametric Hypothesis Testing (23 Streams)
Comparing stream-by-stream false alert counts ($d_i = \text{Alerts}_{P14, i} - \text{Alerts}_{P17, i}$):
- **Tied Streams ($d_i = 0$):** 15 streams (65.2% of benchmark).
- **Phase 14 Superior ($d_i < 0$):** 5 streams ($-8, -2, -2, -11, -13$).
- **Phase 17 Superior ($d_i > 0$):** 3 streams ($+2, +2, +1$).
- **Wilcoxon Signed-Rank Test (Exact):**
  - Sum of positive ranks: $W^+ = 8.0$
  - Sum of negative ranks: $W^- = 28.0$
  - Test Statistic: $W = \min(W^+, W^-) = 8.0$
  - Exact Two-Sided p-value: **$p = 0.1953125$**
  - Exact One-Sided p-value (Testing $H_1: \text{P17 has fewer alerts}$): **$p = 0.92578125$**
- **Conclusion:** There is zero statistically significant evidence that Phase 17 suppresses false alarms. In fact, Phase 14 Balanced is empirically superior in total alerts, alert rate, and stream-level counts.

---

## 8. What Phase 27 Does NOT Establish

In compliance with rigorous scientific integrity guidelines, this report explicitly defines the operational and physical boundaries of these findings:

1. **Does NOT Establish Reliable Detection of Unexpected Criminal Gunfire:**
   The evaluation conducted in Phase 27 is strictly a negative-background false-alarm benchmark. It measures the detector's ability to reject non-target acoustic noise (traffic, machinery, aircraft). It does **not** evaluate detection sensitivity, probability of detection ($P_d$), or localization accuracy against unexpected, concealed, or suppressed criminal gunfire.
2. **Does NOT Establish Generalization to Arbitrary Cities:**
   The 23 continuous recordings represent four specific geographic campaigns (the UK, Spain, France, and Australia). Urban acoustic environments vary widely in building geometries, street canyons, meteorological inversions, reverberation, and cultural noise profiles. These findings cannot be extrapolated to predict performance in arbitrary uncharacterized cities.
3. **Does NOT Establish Municipal-Scale Operational False-Alert Feasibility:**
   While Phase 14 Balanced outperformed Phase 17, an eligible false alert rate of **10.22 alerts/hour** is completely unacceptable for operational emergency dispatch. In a municipal deployment of 100 sensor nodes, this rate would generate approximately **24,500 false gunshot dispatches every 24 hours**. Operational viability requires false alert rates several orders of magnitude lower (e.g., < 0.001 alerts/hour/sensor).
4. **Does NOT Establish Public-Safety or Emergency-Response Suitability:**
   This prototype software lacks fault-tolerant architecture, encrypted sensor telemetry, tamper detection, real-time fail-over clustering, and automated health monitoring required for life-critical public-safety systems.
5. **Does NOT Establish Superiority of Phase 17 Across Independent Campaigns:**
   Phase 17 Experimental was conclusively demonstrated to be inferior on continuous aviation noise (+50% false alerts) and showed no statistically significant advantage across the cumulative benchmark ($p = 0.1953$). Phase 17 promotion is formally rejected.

---

## 9. Baseline Decision and Architectural Direction

### Definitive Recommendation:
- **`Phase 14 Balanced` is CONFIRMED and RETAINED as the DEFAULT RESEARCH BASELINE.**
- **`Phase 17 Experimental` is CONCLUDED and REJECTED as a replacement baseline.** It will remain documented solely as a historical selectable experimental profile.
- **Future Architectural Work:** Must address continuous distractor hysteresis clustering and spatial background adaptation before any candidate model can be considered for baseline promotion.

---

**RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.**

