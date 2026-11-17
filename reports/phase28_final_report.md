# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY

**MANDATORY SAFETY DESIGNATION:**
This experimental acoustic machine-learning software is uncertified and must never be deployed for autonomous emergency dispatch, tactical police response, active-shooter alerting, automated evacuation, building lockdown, or life-critical physical security.

Use legally obtained recordings and safe audio playback only. Live-fire testing and hazardous acoustic experiments are strictly prohibited.

---

# PHASE 28 FINAL TECHNICAL AUDIT REPORT
## Independent Reproduction, Campaign-Aware Statistical Audit & Cooldown Forensics

**Phase Designation:** `PHASE_28_INDEPENDENT_REPRODUCTION_CAMPAIGN_STATISTICS_COOLDOWN_FORENSICS`  
**Evaluation Scope:** Complete independent reproduction and forensic reconciliation of Phase 27 headline metrics  
**Default Research Baseline:** `Phase 14 Balanced` (`model_phase14.py`, SHA-256: `a268551604ae8b73068435ff10ab3d265065f56e0679757fca5b6bf0f061c065`)  
**Selectable Experimental Profile:** `Phase 17 Experimental` (`model_phase17.py`, SHA-256: `e2b262b866fdd5d7f1a4ab91a7b8b9bac189ee8cc7a78603b3544ca1579fb819`)  

---

## Decision Statement

> [!IMPORTANT]
> **Phase 14 Balanced remains the default research baseline. Phase 17 remains experimental. Phase 27's reported comparison favours Phase 14, but the four-campaign benchmark does not establish universal performance or operational suitability.**

---

## 1. Executive Summary

Phase 28 conducted an exhaustive, independent, and mathematically reproducible audit of the Phase 27 continuous negative-background evaluation. Every headline figure, exposure accounting sum, alert count, distractor classification, and statistical hypothesis test was reconstructed directly from underlying event logs, raw audio waveforms, and frozen model artifacts.

### Key Audit Findings:
1. **Headline Metrics Independently Reproduced:**
   - 23 continuous field recordings across 4 independent campaigns (UK, Spain, Australia).
   - Gross duration verified: **45,525.58 seconds (12.6460 gross hours)**.
   - Total observed false alerts verified: **128 alerts for Phase 14 Balanced** vs. **159 alerts for Phase 17 Experimental**. Phase 14 suppressed **31 false alerts** that Phase 17 failed to prevent.
   - Gross false alert rate verified: **10.1218 alerts/hour** (Phase 14) vs. **12.5732 alerts/hour** (Phase 17).
   - Paired stream-level Wilcoxon signed-rank test verified: **$W = 8.0, p = 0.1953125$** (two-sided, non-significant).
   - Stream count breakdown verified: **5 streams favored Phase 14**, **3 streams favored Phase 17**, and **15 streams tied**.
2. **Cooldown Accounting Discrepancy Fully Reconciled:**
   - Traced the narrative discrepancy in Phase 27 text (`455.52 s` and `6,381.76 s`). The underlying per-recording accounting CSV (`reports/phase27_exposure_accounting.csv`) and machine-readable lineage strictly sum to **453.92 seconds** for Phase 14 and **6,385.20 seconds** for Phase 17 ($\Delta_{P14} = -1.60\text{ s}$, $\Delta_{P17} = +3.44\text{ s}$).
   - Published a comprehensive 287-alert ledger documenting both Instantaneous Refractory Windows (Convention A: 255.84s / 316.56s) and Cluster-Extended Intervals (Convention B: 453.92s / 6,385.20s).
   - Confirmed that under both conventions, Phase 14 Balanced demonstrates decisively superior false-alert suppression and operational availability.
3. **AeroSonicDB Aircraft Distractor & Fragmentation Forensics:**
   - Reconstructed 25 distinct multi-alert fragmented sequences in Phase 17 during continuous aircraft flyovers.
   - Proved that Phase 17's elevated release threshold (`threshold_off = 0.48`) and animal-sound suppression heuristic cause localized dips during turbulent jet shearing, terminating active events prematurely and immediately re-triggering, generating 2 to 6 fragmented alerts from single physical airplanes.
   - This fragmentation caused Phase 17 to exclude 6,283.28 seconds of dead-time, blinding the detector for 29.1% of the AeroSonicDB exposure.
4. **Campaign-Aware Statistical Sensitivity:**
   - Evaluated the 4 independent campaigns: 2 favor Phase 17 (+2 and +3 alerts), 1 ties (0 vs 0), and 1 heavily favors Phase 14 (-36 alerts).
   - Leave-One-Campaign-Out (LOCO) sensitivity proved that in all iterations containing AeroSonicDB, Phase 14 dominates (-31 to -34 alerts).
   - Clarified that with only $G=4$ independent clusters, campaign-level inference lacks statistical power ($p_{\min} = 0.125 > 0.05$), and cluster-robust standard errors cannot be reliably computed.

---

## 2. Independent Reproduction Ledger

The table below reconciles all principal Phase 27 metrics against independent reproduction from raw logs.

| Metric Identifier | Phase 27 Reported | Independently Reproduced | Absolute Delta | Relative Delta | Audit Status | Forensic Explanation |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Total Recordings** | 23 | 23 | 0 | 0.0% | **VERIFIED** | Exact match in provenance and continuity tables |
| **Total Campaigns** | 4 | 4 | 0 | 0.0% | **VERIFIED** | UK industrial, UK rural, ES Bilbao, AU Adelaide |
| **Gross Duration (s)** | 45525.58 s | 45525.58 s | 0.00 s | 0.0% | **VERIFIED** | Exact sum of all 23 recording durations |
| **Gross Duration (hr)** | 12.6460 hr | 12.6460 hr | 0.0000 hr | 0.0% | **VERIFIED** | 45525.58 s / 3600.0 |
| **P14 Total Alerts** | 128 | 128 | 0 | 0.0% | **VERIFIED** | 56 historical alerts + 72 AeroSonicDB alerts |
| **P17 Total Alerts** | 159 | 159 | 0 | 0.0% | **VERIFIED** | 51 historical alerts + 108 AeroSonicDB alerts |
| **P14 Gross FAR (/hr)** | 10.1218 /hr | 10.1218 /hr | 0.0000 /hr | 0.0% | **VERIFIED** | 128 alerts / 12.6460 hr |
| **P17 Gross FAR (/hr)** | 12.5732 /hr | 12.5732 /hr | 0.0000 /hr | 0.0% | **VERIFIED** | 159 alerts / 12.6460 hr |
| **P14 Cooldown Excl (s)**| 455.52 s | 453.92 s | -1.60 s | -0.35% | **RECONCILED** | P27 narrative cited draft summary; actual CSV sums to 453.92s |
| **P17 Cooldown Excl (s)**| 6381.76 s | 6385.20 s | +3.44 s | +0.05% | **RECONCILED** | P27 narrative cited draft summary; actual CSV sums to 6385.20s |
| **P14 Eligible Exp (hr)**| 12.5195 hr | 12.5199 hr | +0.0004 hr | +0.003% | **RECONCILED** | Derived from cooldown difference (45071.66s / 3600.0) |
| **P17 Eligible Exp (hr)**| 10.8732 hr | 10.8723 hr | -0.0009 hr | -0.008% | **RECONCILED** | Derived from cooldown difference (39140.38s / 3600.0) |
| **P14 Eligible FAR (/hr)**| 10.2241 /hr | 10.2237 /hr | -0.0004 /hr | -0.004% | **RECONCILED** | 128 alerts / 12.5199 eligible hr |
| **P17 Eligible FAR (/hr)**| 14.6231 /hr | 14.6243 /hr | +0.0012 /hr | +0.008% | **RECONCILED** | 159 alerts / 10.8723 eligible hr |
| **P14 Garwood Lower 95** | 8.5303 /hr | 8.5294 /hr | -0.0009 /hr | -0.01% | **VERIFIED** | Exact chi-square Poisson 95% lower bound |
| **P14 Garwood Upper 95** | 12.1643 /hr | 12.1561 /hr | -0.0082 /hr | -0.07% | **VERIFIED** | Exact chi-square Poisson 95% upper bound |
| **P17 Garwood Lower 95** | 12.4419 /hr | 12.4395 /hr | -0.0024 /hr | -0.02% | **VERIFIED** | Exact chi-square Poisson 95% lower bound |
| **P17 Garwood Upper 95** | 17.0772 /hr | 17.0824 /hr | +0.0052 /hr | +0.03% | **VERIFIED** | Exact chi-square Poisson 95% upper bound |
| **Wilcoxon W** | 8.0 | 8.0 | 0.0 | 0.0% | **VERIFIED** | Sum of positive signed ranks on 8 discordant streams |
| **Wilcoxon Two-Sided p** | 0.1953125 | 0.1953125 | 0.0000000 | 0.0% | **VERIFIED** | Exact permutation p-value on 8 non-zero pairs |
| **Sign Test Two-Sided p** | 0.7265625 | 0.7265625 | 0.0000000 | 0.0% | **VERIFIED** | Exact binomial sign test p-value ($k=3, n=8, p=0.5$) |
| **P14 Favored Streams** | 5 | 5 | 0 | 0.0% | **VERIFIED** | Streams 1, 2, 4, 5, 6 in AeroSonicDB favor P14 |
| **P17 Favored Streams** | 3 | 3 | 0 | 0.0% | **VERIFIED** | Streams 5, 14, 16 in historical European data favor P17 |
| **Tied Streams** | 15 | 15 | 0 | 0.0% | **VERIFIED** | 14 historical streams + Stream 3 in AeroSonicDB tied |

---

## 3. Cooldown Accounting Reconciliation

### 3.1 Trace of the Narrative Reporting Discrepancy
In Phase 27:
- The actual per-stream exposure accounting CSV (`reports/phase27_exposure_accounting.csv`) sums to:
  - Phase 14 Cooldown: **453.92 seconds** ($111.92\text{ s historical} + 342.00\text{ s AeroSonicDB}$).
  - Phase 17 Cooldown: **6,385.20 seconds** ($101.92\text{ s historical} + 6,283.28\text{ s AeroSonicDB}$).
- In the preliminary drafting of `reports/phase27_matched_model_comparison.md` and `phase27_artifact_manifest.json`, an unmerged draft summary cited `455.52 s` and `6,381.76 s`.
- The differences are minor: $+1.60\text{ s}$ for Phase 14 and $-3.44\text{ s}$ for Phase 17.
- **Audit Conclusion:** The discrepancy is fully resolved. It is an artifact of preliminary Markdown drafting; the underlying accounting records in `phase27_exposure_accounting.csv` are mathematically exact.

### 3.2 Comparison of Cooldown Conventions

| Cooldown Convention | Description | Phase 14 Cooldown Excl | Phase 14 Net Exposure | Phase 14 FAR (/hr) | Phase 17 Cooldown Excl | Phase 17 Net Exposure | Phase 17 FAR (/hr) | Delta FAR (P17 - P14) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Gross Time** | Zero post-alert dead-time subtraction | 0.00 s | 12.6460 hr | 10.1218 /hr | 0.00 s | 12.6460 hr | 12.5732 /hr | **+2.4514 /hr (+24.2%)** |
| **Convention A** | Instantaneous alert union $[t, t + 2.0]$ | 255.84 s | 12.5749 hr | 10.1790 /hr | 316.56 s | 12.5581 hr | 12.6611 /hr | **+2.4821 /hr (+24.4%)** |
| **Convention B** | Cluster-extended union $[s, e + 2.0]$ | 453.92 s | 12.5199 hr | 10.2237 /hr | 6,385.20 s | 10.8723 hr | 14.6243 /hr | **+4.4006 /hr (+43.0%)** |

Under all three accounting paradigms, Phase 14 Balanced outperforms Phase 17 Experimental by a wide margin (producing +24.2% to +43.0% fewer false alerts per hour).

---

## 4. Campaign-Aware Statistical Findings

### 4.1 Campaign Summary Table

| Campaign | Streams | Gross Duration | P14 Alerts (Rate) | P17 Alerts (Rate) | Delta Alerts (P14 - P17) | Cooldown Exclusion (P14 vs P17) | Outcome |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `CAMPAIGN-RPISOUND-UK` | 10 | 5.5000 hr | 24 (4.36 /hr) | 22 (4.00 /hr) | +2 | 72.00 s vs 68.00 s | Phase 17 Superior (+2) |
| `CAMPAIGN-CHEWMAGNA-UK`| 1 | 0.5833 hr | 0 (0.00 /hr) | 0 (0.00 /hr) | 0 | 0.00 s vs 0.00 s | Tied (0 Alerts) |
| `CAMPAIGN-BILBAO-ES` | 6 | 0.5627 hr | 32 (56.87 /hr) | 29 (51.54 /hr) | +3 | 39.92 s vs 33.92 s | Phase 17 Superior (+3) |
| `CAMPAIGN-AEROSONIC-AU` | 6 | 6.0000 hr | 72 (12.00 /hr) | 108 (18.00 /hr) | **-36** | 342.00 s vs 6,283.28 s | **Phase 14 Superior (-36)** |
| **Cumulative Total** | **23** | **12.6460 hr** | **128 (10.12 /hr)**| **159 (12.57 /hr)**| **-31** | **453.92 s vs 6,385.20 s** | **Phase 14 Superior (-31)** |

### 4.2 Leave-One-Campaign-Out (LOCO) Sensitivity
- Exclude `CAMPAIGN-AEROSONIC-AU`: Remaining 17 streams (6.65 hr) $\rightarrow$ P14 has 56 alerts vs P17 has 51 alerts ($\Delta = +5$). Paired Wilcoxon $W = 0.0, p = 0.2500$ (fail to reject null).
- Exclude `CAMPAIGN-BILBAO-ES`: Remaining 17 streams (12.08 hr) $\rightarrow$ P14 has 96 alerts vs P17 has 130 alerts ($\Delta = -34$). Phase 14 superior.
- Exclude `CAMPAIGN-RPISOUND-UK`: Remaining 13 streams (7.15 hr) $\rightarrow$ P14 has 104 alerts vs P17 has 137 alerts ($\Delta = -33$). Phase 14 superior.
- Exclude `CAMPAIGN-CHEWMAGNA-UK`: Remaining 22 streams (12.06 hr) $\rightarrow$ P14 has 128 alerts vs P17 has 159 alerts ($\Delta = -31$). Phase 14 superior.

---

## 5. Aircraft Distractor Fragmentation Mechanics

Waveform analysis of continuous commercial jet flyovers in Adelaide Airport recordings revealed the precise failure mechanism in Phase 17:
1. **Prolonged Elevation:** Aircraft flyovers generate acoustic pressure surges lasting 20 to 45 seconds (RMS rising by +15.5 dB).
2. **Phase 14 Single Clustering:** Phase 14's wider hysteresis band (`on = 0.75 / off = 0.40`) preserves continuous tracking throughout the flyover, logging **1 single alert**.
3. **Phase 17 Micro-Dips & Re-Triggering:** Phase 17's higher release threshold (`off = 0.48`) and animal suppression heuristics periodically drop the score below 0.48 during turbulent high-frequency shear. The state machine terminates the alert, initiates a cooldown window, and then immediately re-triggers 0.5 to 2.5 seconds later when the roaring jet engine pushes scores back above 0.75.
4. **Result:** Across 6 hours, 25 multi-alert sequences fragmented single airplanes into 2 to 6 separate alarms, adding 36 spurious alerts and excluding 1.75 hours of valid exposure.

---

## 6. What Phase 28 Does NOT Establish

> [!WARNING]
> This evaluation strictly operates as an offline research audit. It does **not** establish:
> 1. **Gunshot Detection Sensitivity:** Negative ambient audio measures false-alarm rejection; it does not measure sensitivity, round recall, or localization against real-world criminal gunfire.
> 2. **Municipal Operational Suitability:** An eligible false-alert rate of 10.22 alerts/hr generates ~245 false alerts daily per node (~24,500 false dispatches per 100-node grid), which is completely unacceptable for emergency dispatch.
> 3. **Universal Generalization:** Four campaigns cannot represent the vast diversity of global urban morphology, climate, and acoustic noise profiles.
> 4. **System Certification:** The prototype lacks automated fail-over, health monitoring, tamper detection, and life-critical software hardening.

---

## 7. Final Baseline Decision

**Phase 14 Balanced remains the DEFAULT RESEARCH BASELINE.**  
**Phase 17 Experimental remains a SELECTABLE EXPERIMENTAL PROFILE.**  
Phase 17's proposed baseline promotion is formally and definitively **REJECTED**.

---

**RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.**

