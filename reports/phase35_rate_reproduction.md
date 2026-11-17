# Phase 35 Technical Report: Cooldown-Adjusted Rate Reproduction & Unrounded Benchmark Accounting

> [!CAUTION]
> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.**
> This experimental acoustic machine-learning software is uncertified and must never be deployed for autonomous emergency dispatch, police tactical response, active-shooter alerting, automated evacuation, building lockdown, or life-critical physical security.
> Use legally obtained recordings and safe audio playback only. Live-fire testing and hazardous acoustic experiments are strictly prohibited.

---

## 1. Executive Summary

This report establishes the final, authoritative, unrounded rate calculations across individual stream, campaign, and corpus levels for both frozen detector profiles:
- **Phase 14 Balanced** (`DEFAULT_RESEARCH_BASELINE`)
- **Phase 17 Experimental** (`SELECTABLE_EXPERIMENTAL_PROFILE`)

All calculations utilize unrounded physical audio exposure seconds derived from physical WAV headers across the 23-stream continuous benchmark ($45,525.5755\text{ seconds} = 12.645993...\text{ gross hours}$).

### Headline Benchmark Totals

| Detector Profile | Alerts | Gross Exposure (h) | Gross FAR (/h) | Conv A Excluded (s) | Conv A Eligible (h) | Conv A FAR (/h) | Conv B Excluded (s) | Conv B Eligible (h) | Conv B FAR (/h) |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Phase 14 Balanced** | 128 | 12.6460 | **10.1218** | 255.8400 | 12.5749 | **10.1790** | 453.9200 | 12.5199 | **10.2237** |
| **Phase 17 Experimental** | 159 | 12.6460 | **12.5732** | 316.5600 | 12.5581 | **12.6612** | 6,385.2000 | 10.8723 | **14.6243** |
| **Delta (P14 - P17)** | -31 | 0.0000 | -2.4514 | -60.7200 | +0.0169 | -2.4822 | -5,931.2800 | +1.6476 | **-4.4006** |

---

## 2. Campaign-Level Rate Breakdown

### 2.1 Phase 14 Balanced (`DEFAULT_RESEARCH_BASELINE`)

| Campaign Identifier | Streams | Gross Duration (h) | Alerts | Gross FAR (/h) | Conv A Excl (s) | Conv A FAR (/h) | Conv B Excl (s) | Conv B FAR (/h) |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| `CAMPAIGN-SOUTHAMPTON-EXP1` | 10 | 5.5000 | 24 | 4.3636 | 48.0000 | 4.3742 | 48.0000 | 4.3742 |
| `CAMPAIGN-CHEW-MAGNA` | 1 | 0.5833 | 0 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| `CAMPAIGN-BILBAO` | 6 | 0.5627 | 32 | 56.8727 | 63.9200 | 58.7247 | 63.9200 | 58.7247 |
| `CAMPAIGN-ADELAIDE-AEROSONIC` | 6 | 6.0000 | 72 | 12.0000 | 143.9200 | 12.0805 | 342.0000 | 12.1931 |
| **CORPUS TOTAL** | **23** | **12.6460** | **128** | **10.1218** | **255.8400** | **10.1790** | **453.9200** | **10.2237** |

### 2.2 Phase 17 Experimental (`SELECTABLE_EXPERIMENTAL_PROFILE`)

| Campaign Identifier | Streams | Gross Duration (h) | Alerts | Gross FAR (/h) | Conv A Excl (s) | Conv A FAR (/h) | Conv B Excl (s) | Conv B FAR (/h) |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| `CAMPAIGN-SOUTHAMPTON-EXP1` | 10 | 5.5000 | 22 | 4.0000 | 44.0000 | 4.0089 | 44.0000 | 4.0089 |
| `CAMPAIGN-CHEW-MAGNA` | 1 | 0.5833 | 0 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| `CAMPAIGN-BILBAO` | 6 | 0.5627 | 29 | 51.5409 | 57.9200 | 53.0579 | 57.9200 | 53.0579 |
| `CAMPAIGN-ADELAIDE-AEROSONIC` | 6 | 6.0000 | 108 | 18.0000 | 214.6400 | 18.1808 | 6,283.2800 | 25.3840 |
| **CORPUS TOTAL** | **23** | **12.6460** | **159** | **12.5732** | **316.5600** | **12.6612** | **6,385.2000** | **14.6243** |

---

## 3. Cooldown Blindness and Inflation Analysis

Convention B cluster-extended cooldown introduces substantial exposure blindness in Phase 17:
- **Phase 14 Total Blindness:** $453.92\text{ s} / 45,525.5755\text{ s} = \mathbf{0.997\%}$ of total audio exposure.
- **Phase 17 Total Blindness:** $6,385.20\text{ s} / 45,525.5755\text{ s} = \mathbf{14.025\%}$ of total audio exposure.
- **In Adelaide Alone:** Phase 17 excludes $6,283.28\text{ s} / 21,600.00\text{ s} = \mathbf{29.089\%}$ of total stream exposure under Convention B.

Because Phase 17 suffers from state-machine fragmentation during continuous acoustic disturbances, its Convention B eligible denominator collapses from $6.0000\text{ h}$ to $4.2546\text{ h}$ in Adelaide, driving its false alert rate up to **$25.3840/\text{hr}$**.

See [phase35_final_rate_table.csv](file:///e:/gunshot/gunshot/reports/phase35_final_rate_table.csv) for full stream-by-stream unrounded rate entries.
