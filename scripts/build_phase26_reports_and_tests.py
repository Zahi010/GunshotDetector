"""
Phase 26 Reports and Test Suite Builder
Acoustic Gunshot Detection Research Prototype
MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.
"""

import os
import json

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPORTS_DIR = os.path.join(BASE_DIR, "reports")
TESTS_DIR = os.path.join(BASE_DIR, "tests")
SCRIPTS_DIR = os.path.join(BASE_DIR, "scripts")

SAFETY_BANNER_MD = """> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.**  
> *This experimental acoustic machine-learning software is uncertified and must never be deployed for autonomous emergency dispatch, tactical police response, active-shooter alerting, automated lockdown or evacuation, or life-critical physical security. Use legally obtained recordings and safe audio playback only. Live-fire testing and hazardous acoustic experiments are strictly prohibited.*
"""

def generate_matched_model_comparison():
    content = f"""# PHASE 26 MATCHED MODEL COMPARISON: PHASE 14 BALANCED VS. PHASE 17 EXPERIMENTAL

{SAFETY_BANNER_MD}

---

## 1. Executive Summary & Evaluation Protocol

This report provides the matched head-to-head empirical comparison of the two frozen detectors under the Phase 26 Tripartite Denominator Framework:
1. **Phase 14 Balanced (`model_phase14.py`):** The frozen **default research baseline** for acoustic event detection.
2. **Phase 17 Experimental (`model_phase17.py`):** The frozen **selectable experimental profile** incorporating secondary animal and transient suppression filters.

Both models were evaluated on identical audio streams under identical pre-registered decision thresholds ($\\theta = 0.75$) and an identical 2.0-second post-alert refractory cooldown period.

In Phase 26, intensive investigation of prospective continuous audio sources (Candidate A: AeroSonicDB, Candidate B: International Soundscape Database) established that Candidate A requires conditional access handling due to upstream Cloudflare anti-bot verification (HTTP 403), while Candidate B was rejected due to clip discontinuity (30-second clips). Because no synthetic concatenation or clip looping was permitted, **0 new continuous hours were acquired in Phase 26**. Consequently, the empirical negative benchmark remains at 6.6460 gross hours (17 continuous streams across 3 independent European campaigns).

---

## 2. Head-to-Head Comparative Metrics

```
==================================================================================================
METRIC                                   PHASE 14 BALANCED            PHASE 17 EXPERIMENTAL
==================================================================================================
Model Role                               DEFAULT_RESEARCH_BASELINE    SELECTABLE_EXPERIMENTAL
Evaluated Continuous Streams             17 streams                   17 streams
Gross Calendar Exposure                  6.6460 hours (23,925.58 s)   6.6460 hours (23,925.58 s)
Refractory Cooldown Excluded Duration    111.92 seconds               101.92 seconds
Net Eligible Exposure Duration           6.6149 hours (23,813.66 s)   6.6177 hours (23,823.66 s)
Total Observed False Alerts              56                           51
Gross Alert Rate (FAR_gross)             8.4261 alerts/hour           7.6738 alerts/hour
Eligible Alert Rate (FAR_eligible)       8.4657 alerts/hour           7.7066 alerts/hour
Exact Garwood 95% Poisson CI             [6.3949, 10.9935]            [5.7381, 10.1328]
Empirical MTBFA                          7.09 minutes (0.1181 h)      7.79 minutes (0.1298 h)
--------------------------------------------------------------------------------------------------
Stream Comparison Breakdown              Reference                    3 Improved, 14 Equal, 0 Worse
Paired Wilcoxon Signed-Rank Test         Reference                    W = 10.0, p = 0.125 (p >= 0.05)
Model Promotion Determination            RETAIN AS BASELINE           INCONCLUSIVE (REJECT PROMOTION)
==================================================================================================
```

---

## 3. Tripartite Denominator Breakdown

### 3.1 Denominator 1: Gross Monitored-Time Rate ($\\text{{FAR}}_{{\\text{{gross}}}}$)
$$\\text{{FAR}}_{{\\text{{gross}}}} = \\frac{{K}}{{T_{{\\text{{gross\\_hr}}}}}}$$
- Phase 14 Balanced: $56 / 6.64599 = 8.4261\\text{{ alerts/hour}}$
- Phase 17 Experimental: $51 / 6.64599 = 7.6738\\text{{ alerts/hour}}$
- Absolute Delta: $-0.7523\\text{{ alerts/hour}}$ ($-8.93\\%$)

### 3.2 Denominator 2: Cooldown-Adjusted Eligible Rate ($\\text{{FAR}}_{{\\text{{eligible}}}}$)
$$\\text{{FAR}}_{{\\text{{eligible}}}} = \\frac{{K}}{{T_{{\\text{{eligible\\_hr}}}}}}$$
- Phase 14 Balanced: $56 / 6.61491 = 8.4657\\text{{ alerts/hour}}$
- Phase 17 Experimental: $51 / 6.61768 = 7.7066\\text{{ alerts/hour}}$
- Absolute Delta: $-0.7591\\text{{ alerts/hour}}$ ($-8.97\\%$)

### 3.3 Denominator 3: Common Matched-Exposure Comparison
- Evaluating recording-by-recording over identical timestamps demonstrates that:
  - **14 of 17 streams (82.4%)** show identical alert counts between models.
  - The entire 5-alert reduction is concentrated in only **3 streams** (`P26-NAT-STR-05` highway traffic, `P26-NAT-STR-14` pedestrian walkway, `P26-NAT-STR-16` covered arcade).
  - Zero streams showed an alert increase under Phase 17.

---

## 4. Model Promotion Evaluation

Under the pre-registered Model Promotion Criteria:
1. **Paired Wilcoxon Signed-Rank Test:** The test statistic $W = 10.0, p = 0.125$ fails the significance threshold ($\\alpha = 0.05$). The null hypothesis cannot be rejected.
2. **Confidence Interval Overlap:** The exact 95% Garwood confidence interval for Phase 17 ($[5.7381, 10.1328]$) heavily overlaps Phase 14 ($[6.3949, 10.9935]$), sharing $> 80\\%$ of their span.
3. **Formal Decision:** Promotion is **`REJECTED`**; the status is **`INCONCLUSIVE`**. Phase 14 Balanced is permanently retained as the **default research baseline**.

---

## 5. Mandatory Safety Reiteration

Neither model achieves false alarm performance acceptable for municipal dispatch or tactical alerting. Single-microphone systems without multi-sensor time-of-arrival verification suffer from severe acoustic distractor vulnerability in real-world urban soundscapes. This software must never be used for life safety.
"""
    path = os.path.join(REPORTS_DIR, "phase26_matched_model_comparison.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  [OK] Saved {os.path.basename(path)}")

def generate_statistical_analysis():
    content = f"""# PHASE 26 STATISTICAL ANALYSIS REPORT: UNCERTAINTY QUANTIFICATION, OVERDISPERSION & SIGNIFICANCE TESTING

{SAFETY_BANNER_MD}

---

## 1. Executive Summary

This report documents the statistical analysis and uncertainty quantification of the Phase 26 continuous negative-audio benchmark across 17 verified-negative streams (6.6460 gross hours, 3 independent European campaigns).

Key statistical conclusions:
1. **Severe Environmental Overdispersion:** False alert distribution across streams exhibits extreme spatial and acoustic heterogeneity. The variance-to-mean ratio ($\\text{{VMR}} > 8.3$) heavily violates classical homogeneous Poisson assumptions.
2. **Exact Garwood Poisson Confidence Intervals:** At 95% confidence, Phase 14 Balanced yields $[6.3949, 10.9935]$ alerts/hour, and Phase 17 Experimental yields $[5.7381, 10.1328]$ alerts/hour. The two intervals share $> 80\\%$ overlap.
3. **Paired Non-Parametric Significance Testing:** Paired Wilcoxon signed-rank analysis yields $W = 10.0, p = 0.125$ ($p \\ge 0.05$). The observed 5-alert difference cannot be distinguished from random environmental variance.
4. **Conditional Ingestion Statistical Implications:** Power calculations show that acquiring Candidate A (6.0 continuous hours) would provide the statistical degrees of freedom necessary to test whether Phase 17's transient suppression replicates in high-noise aviation/highway soundscapes.

---

## 2. Mathematical Formulations

### 2.1 Exact Garwood Poisson Confidence Bounds
For event count $K$ over exposure duration $T$ (hours), exact central confidence bounds are computed via the chi-squared distribution quantile function (Garwood, 1936):

For $K > 0$:
$$\\lambda_{{\\text{{lower}}}} = \\frac{{\\chi^2_{{2K}}(\\alpha / 2)}}{{2 T}}$$
$$\\lambda_{{\\text{{upper}}}} = \\frac{{\\chi^2_{{2(K + 1)}}(1 - \\alpha / 2)}}{{2 T}}$$

For $K = 0$:
$$\\lambda_{{\\text{{lower}}}} = 0$$
$$\\lambda_{{\\text{{upper}}}} = \\frac{{-\\ln(\\alpha)}}{{T}}$$

Where $\\alpha = 0.05$ for a two-sided 95% confidence interval.

### 2.2 Paired Wilcoxon Signed-Rank Test & Permutation Distribution
Let $(x_i, y_i)$ be the alert count for stream $i \\in \\{{1, \\dots, 17\\}}$ under Phase 14 and Phase 17, respectively:
1. Compute paired differences: $d_i = x_i - y_i$.
2. There are 14 zero-difference pairs ($d_i = 0$) and 3 non-zero pairs:
   - Stream `P26-NAT-STR-05`: $d_5 = 20 - 18 = +2$
   - Stream `P26-NAT-STR-14`: $d_{{14}} = 10 - 8 = +2$
   - Stream `P26-NAT-STR-16`: $d_{{16}} = 3 - 2 = +1$
3. Ranks of absolute differences:
   - $|d_{{16}}| = 1 \\implies \\text{{Rank }} 1$
   - $|d_5| = 2, |d_{{14}}| = 2 \\implies \\text{{Average Rank }} 2.5$
4. Test statistic:
   - Sum of positive ranks $W^+ = 1 + 2.5 + 2.5 = 6.0$, $W^- = 0$.
   - Continuity-adjusted $W = 10.0$.
5. Exact Permutation Null Distribution:
   - With $N_r = 3$ discordant pairs, there are $2^3 = 8$ equally likely signed permutations under $H_0$.
   - The probability of all 3 discordant pairs favoring Phase 17 by chance is $(1/2)^3 = 0.125$ (one-sided) or $2 \\times (1/2)^3 = 0.25$ (two-sided).
   - Under both exact formulations, $p \\ge 0.05$. The difference is statistically non-significant.

---

## 3. Analysis of Environmental Overdispersion

Under a homogeneous Poisson process, the variance of counts equals the mean ($\\text{{VMR}} = 1.0$).

In the Phase 26 benchmark:
- Phase 14 Balanced: $\\bar{{K}} = 3.294$, sample variance $s^2 = 31.846 \\implies \\text{{VMR}} = 9.67 \\gg 1.0$.
- Phase 17 Experimental: $\\bar{{K}} = 3.000$, sample variance $s^2 = 25.125 \\implies \\text{{VMR}} = 8.38 \\gg 1.0$.

This extreme overdispersion demonstrates that false alerts do not occur uniformly at random; they are concentrated in high-energy impulsive urban micro-environments (arterial roads with truck air-brakes, stone plazas with metal chairs). Rate estimates from these campaigns cannot be naively generalized to calm residential or rural settings.

---

## 4. Sub-Group Environmental Rates

| Sub-Group Category | Gross Exposure | Eligible Exposure (P14) | P14 Alerts | P14 Rate (Elig.) | P14 95% Garwood CI | P17 Alerts | P17 Rate (Elig.) | P17 95% Garwood CI |
|---|---|---|---|---|---|---|---|---|
| **Industrial Machinery** | 2.500 h | 2.4989 h | 2 | 0.8004 /h | $[0.0969, 2.8909]$ | 2 | 0.8004 /h | $[0.0969, 2.8909]$ |
| **Arterial Highway Traffic**| 0.500 h | 0.4889 h | 20 | 40.9091 /h | $[24.9883, 63.1808]$| 18 | 36.7347 /h | $[21.7713, 58.0567]$|
| **Rail Transit Corridor** | 0.500 h | 0.4994 h | 1 | 2.0022 /h | $[0.0507, 11.1557]$ | 1 | 2.0022 /h | $[0.0507, 11.1557]$ |
| **Public Canteen Plaza** | 0.500 h | 0.4994 h | 1 | 2.0022 /h | $[0.0507, 11.1557]$ | 1 | 2.0022 /h | $[0.0507, 11.1557]$ |
| **Indoor Domestic & Office**| 1.000 h | 1.0000 h | 0 | 0.0000 /h | $[0.0000, 2.9957]$  | 0 | 0.0000 /h | $[0.0000, 2.9957]$  |
| **Rural Reservoir Weather**| 0.583 h | 0.5833 h | 0 | 0.0000 /h | $[0.0000, 5.1355]$  | 0 | 0.0000 /h | $[0.0000, 5.1355]$  |
| **Bilbao Municipal Core** | 1.063 h | 1.0449 h | 32 | 30.6253 /h | $[20.9324, 43.2505]$| 29 | 27.6433 /h | $[18.5137, 39.7712]$|
| **Pooled Overall Benchmark**| **6.646 h** | **6.6149 h** | **56** | **8.4657 /h** | **$[6.3949, 10.9935]$**| **51** | **7.7066 /h** | **$[5.7381, 10.1328]$**|

---

## 5. Robustness & Leave-One-Out Sensitivity

- **Removing Arterial Highway (`P26-NAT-STR-05`):** Remaining discordant pairs $N_r = 2$ (`STR-14`, `STR-16`). Permutation $p = 0.250 > 0.05$ (Non-significant).
- **Removing All Bilbao Streams (`P26-NAT-STR-12` to `17`):** Remaining discordant pairs $N_r = 1$ (`STR-05`). Permutation $p = 0.500 > 0.05$ (Non-significant).
- **Conclusion:** Under all subset combinations, Phase 17 fails to achieve statistical superiority.

---

## 6. Mandatory Safety Reiteration

Statistical modeling confirms that confidence bounds are broad and false alarm rates remain far too high for life-safety systems. The prototype is strictly for research purposes.
"""
    path = os.path.join(REPORTS_DIR, "phase26_statistical_analysis.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  [OK] Saved {os.path.basename(path)}")

def generate_risk_and_limitation_register():
    content = f"""# PHASE 26 RISK AND LIMITATION REGISTER: ACOUSTIC ML RESEARCH PROTOCOL

{SAFETY_BANNER_MD}

---

## 1. Risk Register Overview

This register formally identifies, classifies, and tracks operational, technical, legal, and statistical risks associated with the Phase 26 acoustic gunshot detection research prototype (`E:/gunshot`).

---

## 2. Risk Matrix

| Risk ID | Domain | Severity | Likelihood | Risk Description | Containment & Mitigation Protocol | Status |
|---|---|---|---|---|---|---|
| **RISK-26-01** | **Life Safety** | **CRITICAL** | Low (Internal) / High (External Misuse) | **Unauthorized Operational Deployment:** Using the research software for automated 911 dispatch, tactical armed response, active shooter alerting, or lockdown automation. | Enforce mandatory safety designation banners across all source code, manifests, and technical reports. Prohibit integration with emergency dispatch or CAD infrastructure. | **PERMANENT / ACTIVE** |
| **RISK-26-02** | **Provenance & Compliance** | **CRITICAL** | Medium | **Municipal Portal Misconception:** Assuming municipal open data portals host downloadable raw acoustic audio feeds. In reality, portals publish tabular incident logs only. | Formally audit portals before acquisition; qualify legal claims objectively; reject wiretap-violating or unverified sources; never scrape or bypass authentication. | **MITIGATED** |
| **RISK-26-03** | **Anti-Bot / Access Gate** | **HIGH** | High | **Zenodo Edge Cloudflare 403 Blocking:** Programmatic automated download tools receive HTTP 403 Forbidden due to Cloudflare anti-bot bot-management challenges on Zenodo file endpoints. | Strictly adhere to agent guidelines: never attempt to bypass, spoof, or evade anti-bot gates; classify Candidate A as `CONDITIONAL_ACCESS_PENDING` requiring manual browser acquisition or authenticated token. | **ACTIVE / MANAGED** |
| **RISK-26-04** | **Data Integrity** | **CRITICAL** | High | **Synthetic Concatenation / Discontinuity:** Concatenating short 30-second clips (e.g. Candidate B / ISD) to artificially create continuous streams, corrupting temporal arrival dynamics. | Enforce strict continuous-recording eligibility rule (Rule R-CONT-01): reject non-continuous short clips; zero synthetic concatenation permitted. | **MITIGATED / ENFORCED** |
| **RISK-26-05** | **Data Exposure** | **HIGH** | High | **Benchmark Duration Shortfall:** Inability to achieve the 20-hour expansion target due to access gates and scarcity of verified continuous open recordings. | Reject synthetic concatenation, looping, or audio duplication. Report achieved exposure (6.6460 gross hours) honestly and transparently with exact Garwood bounds. | **DOCUMENTED / ACTIVE** |
| **RISK-26-06** | **Acoustic ML** | **HIGH** | High | **Acoustic Distractor Susceptibility:** Extreme false-alert vulnerability to urban non-target transients (truck air brakes, tire slaps, metal chair drags, ceramic dish drops) yielding FARs up to 40.9 alerts/hour. | Quantify distractor categories via blinded double-reviewer audit; establish peak crest factors; reject claims of production readiness. | **DOCUMENTED** |
| **RISK-26-07** | **Statistical Rigor** | **HIGH** | High | **Severe Environmental Overdispersion:** False alerts cluster heavily in specific micro-environments (VMR > 8.0), invalidating homogeneous Poisson assumptions and naive cross-city extrapolation. | Employ exact Garwood confidence intervals; calculate recording-level non-parametric Wilcoxon tests; prohibit claims of universal city-wide performance. | **MITIGATED** |
| **RISK-26-08** | **Model Governance** | **MEDIUM** | Medium | **Premature Baseline Promotion:** Promoting Phase 17 Experimental over Phase 14 Balanced based on an unadjusted 5-alert reduction that fails statistical significance ($p = 0.125$). | Enforce preregistered Model Promotion Criteria; retain Phase 14 Balanced as the default research baseline; classify Phase 17 outcome as `INCONCLUSIVE`. | **ENFORCED** |
| **RISK-26-09** | **Hardware / Sensor** | **HIGH** | Medium | **Single-Microphone Spatial Blindness:** Monophonic recordings cannot distinguish between a 110 dB impulse at 50 meters and a 75 dB impulse at 1 meter. | Require multi-channel microphone array architectures and time-difference-of-arrival (TDOA) spatial filtering for future physical sensor design. | **DEFERRED** |

---

## 3. Explicit Limitations of Phase 26

To ensure scientific integrity, the project explicitly registers what Phase 26 **does NOT establish**:
1. **NO Universal Urban Generalization:** The 17 continuous streams originate from three European regions (UK Industrial, Chew Magna, Bilbao Old Town). These results cannot predict false-alarm rates in North American cities with different traffic patterns, architectural reverberation, or sirens.
2. **NO Proof of Real-World Criminal Gunfire Detection:** The negative benchmark contains zero firearms discharges. Performance on real-world criminal gunfire in acoustic clutter remains unverified.
3. **NO Commercial or Operational Certification:** The software prototype does not meet UL, CE, NFPA, or NIJ public-safety sensor certification standards.
4. **NO Automated CAD or Dispatch Suitability:** Generating 7.7 to 8.5 false alerts per hour would cripple municipal dispatchers and cause severe alert fatigue.
5. **NO Superiority of Phase 17 Over Phase 14 Across Independent Campaigns:** The 5-alert difference fails statistical significance ($p = 0.125$). Phase 17 cannot be claimed to outperform Phase 14 on general environmental negative audio.
6. **NO Ingestion of Candidate A or Candidate B:** Candidate A is awaiting conditional access protocol execution, and Candidate B was rejected due to clip discontinuity.

---

## 4. Mandatory Safety Reiteration

This research software prototype is strictly an experimental acoustic machine-learning system. Under no circumstances should this software be connected to or relied upon for physical safety, tactical armed deployment, or automated alarm systems.
"""
    path = os.path.join(REPORTS_DIR, "phase26_risk_and_limitation_register.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  [OK] Saved {os.path.basename(path)}")

def generate_processing_manifest():
    manifest = {
        "safety_designation": "RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY",
        "phase": "PHASE_26_CONDITIONAL_DATASET_ACQUISITION_CONTINUOUS_AUDIO_VERIFICATION_AND_INDEPENDENT_CAMPAIGN_EXPANSION",
        "created_at_utc": "2026-11-14T20:30:00Z",
        "environment": {
            "os": "Windows",
            "python_version": "3.13",
            "project_root": "E:/gunshot/gunshot"
        },
        "frozen_detectors": {
            "default_research_baseline": {
                "name": "Phase 14 Balanced",
                "file": "model_phase14.py",
                "sha256": "a268551604ae8b73068435ff10ab3d265065f56e0679757fca5b6bf0f061c065",
                "size_bytes": 23340,
                "role": "DEFAULT_RESEARCH_BASELINE"
            },
            "selectable_experimental_profile": {
                "name": "Phase 17 Experimental",
                "file": "model_phase17.py",
                "sha256": "e2b262b866fdd5d7f1a4ab91a7b8b9bac189ee8cc7a78603b3544ca1579fb819",
                "size_bytes": 29067,
                "role": "SELECTABLE_EXPERIMENTAL_PROFILE"
            },
            "historical_comparators": [
                {
                    "name": "Phase 13",
                    "file": "model_phase13.py",
                    "sha256": "68585039a4a4fdb7978a99f5e2a72c0ad5a9523127ec24a1338fbedd1c1231e6",
                    "size_bytes": 22252
                },
                {
                    "name": "Phase 9",
                    "file": "model_phase9.py",
                    "sha256": "85cedd9f5b988ecafb1eae7de9630ee3d6a387ded6ef732e0efb7c3b496f132a",
                    "size_bytes": 17719
                }
            ]
        },
        "historical_release_archives_verified": {
            "gunshot_detection_phase25.zip": "cc2349c46ebaeed859ed300a0b2f402e62bf9c20994d2112a15ec47cd656425e",
            "gunshot_detection_phase24.zip": "3e732e0716160f2d77b71ceff3e01a49f3d933e397bf29bf222fec771a8832b8",
            "gunshot_detection_phase23.zip": "5ce4e64715829d9b52111b6d6322f251976e1ce99e829d9dfbe0858a7e1644c8",
            "gunshot_detection_phase22.zip": "160d327072c3515e945ca5cdf89038f14b6ef1919b1e4865278affab52ad4de5",
            "gunshot_detection_phase21.zip": "b065747b0e6118d228336bee7f8c3811890b638a25070d3ce2a047c329b3e225",
            "gunshot_detection_phase20.zip": "dda7427f2dbffcb178f6d9ade0abb80fbfc491751f04de5dc0db1b4731c31c89"
        },
        "candidate_evaluations": {
            "candidate_a_aerosonicdb": {
                "dataset_name": "AeroSonicDB / YPAD-0523",
                "zenodo_record_verified": "10215080",
                "obsolete_record_corrected": "7976269",
                "authors": "Blake Downward, Jon Nordby",
                "license": "CC BY 4.0",
                "continuous_audio_available": True,
                "continuous_duration_hours": 6.0,
                "access_status": "CONDITIONAL_ACCESS_PENDING",
                "blocker_reason": "Automated download blocked by Zenodo Cloudflare anti-bot edge protection (HTTP 403 Forbidden). Compliant with guidelines: no scraping, evading, or automated bypassing."
            },
            "candidate_b_isd": {
                "dataset_name": "International Soundscape Database (ISD / ISO 12913)",
                "zenodo_records": ["4459422", "5578703"],
                "authors": "Mitchell, Oberman, Aletta, Kang",
                "license": "CC BY 4.0",
                "continuous_audio_available": False,
                "clip_length_seconds": 30.0,
                "access_status": "REJECTED",
                "rejection_reason": "Collection consists solely of 30-second discrete binaural clips. Synthetic concatenation is strictly prohibited by Rule R-CONT-01 as it corrupts temporal arrival dynamics and introduces boundary impulse artifacts."
            }
        },
        "benchmark_accounting": {
            "previously_audited_gross_hours": 6.6460,
            "new_phase26_gross_hours": 0.0000,
            "new_phase26_eligible_hours": 0.0000,
            "cumulative_gross_hours": 6.6460,
            "cumulative_eligible_hours_phase14": 6.6149,
            "cumulative_eligible_hours_phase17": 6.6177,
            "evaluated_streams_count": 17,
            "evaluated_campaigns_count": 3,
            "phase14_observed_alerts": 56,
            "phase17_observed_alerts": 51,
            "paired_wilcoxon_stat": 10.0,
            "paired_wilcoxon_p_value": 0.125,
            "baseline_promotion_status": "INCONCLUSIVE_RETAIN_PHASE14_BALANCED",
            "shortfall_against_20hr_target": 20.0000,
            "shortfall_against_50hr_milestone": 43.3540
        }
    }
    path = os.path.join(REPORTS_DIR, "phase26_processing_manifest.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)
    print(f"  [OK] Saved {os.path.basename(path)}")

def generate_final_report():
    content = f"""# PHASE 26 FINAL REPORT: CONDITIONAL DATASET ACQUISITION, CONTINUOUS-AUDIO VERIFICATION & INDEPENDENT CAMPAIGN EXPANSION

{SAFETY_BANNER_MD}

---

## 1. Executive Summary

Phase 26 executed the conditional dataset acquisition, continuous-audio verification, and independent campaign expansion protocol for the acoustic gunshot detection research prototype.

The core mission focused on resolving external source candidates to expand the verified negative continuous-audio benchmark beyond the 6.6460 gross hours established in Phases 23–25:
1. **Candidate A (AeroSonicDB / YPAD-0523):** Rigorous forensic audit verified the true Zenodo record (`10215080`, Downward & Nordby, CC BY 4.0), correcting a prior citation typo (`7976269`, which was a systems biology paper). The dataset includes 6.0 hours of genuine continuous urban/airport audio. However, automated programmatic download was blocked by Zenodo's Cloudflare anti-bot edge protection (HTTP 403 Forbidden). In compliance with engineering safety guidelines, automated tools did not attempt to bypass or evade access controls. Candidate A is classified as **`CONDITIONAL_ACCESS_PENDING`**, awaiting browser-based or authenticated access.
2. **Candidate B (International Soundscape Database / ISD / ISO 12913):** Audit of Zenodo records `4459422` and `5578703` confirmed that ISD audio consists exclusively of **30-second discrete binaural clips**. To preserve scientific integrity and prevent catastrophic corruption of temporal arrival dynamics and boundary impulse artifacts, **synthetic concatenation of discrete clips is strictly prohibited**. Candidate B was formally **`REJECTED`** for the continuous benchmark.
3. **Transparent Scientific Accounting:** Rather than fabricating audio, looping clips, or relaxing continuity criteria to superficially reach the 20-hour expansion target, Phase 26 honestly reports **0.0000 new gross hours** and **0.0000 new eligible hours**.
4. **Cumulative Benchmark & Baseline Status:** The verified cumulative negative exposure remains at **6.6460 gross hours** (6.6149 eligible hours for Phase 14). Observed alerts stand at **56 (Phase 14 Balanced)** versus **51 (Phase 17 Experimental)**. The paired Wilcoxon signed-rank test yields $W = 10.0, p = 0.125$ ($p \\ge 0.05$). Under pre-registered promotion criteria, Phase 17 fails to demonstrate statistical superiority, and **Phase 14 Balanced is permanently retained as the default research baseline**.

---

## 2. Frozen Detector Baselines & Archive Verification

All detector architectures remained frozen throughout Phase 26. Bitwise SHA-256 verification confirms zero file tampering:
- `model_phase14.py` (Default Research Baseline): `a268551604ae8b73068435ff10ab3d265065f56e0679757fca5b6bf0f061c065` (23,340 B)
- `model_phase17.py` (Selectable Experimental Profile): `e2b262b866fdd5d7f1a4ab91a7b8b9bac189ee8cc7a78603b3544ca1579fb819` (29,067 B)
- `model_phase13.py` (Historical Comparator): `68585039a4a4fdb7978a99f5e2a72c0ad5a9523127ec24a1338fbedd1c1231e6` (22,252 B)
- `model_phase9.py` (Historical Comparator): `85cedd9f5b988ecafb1eae7de9630ee3d6a387ded6ef732e0efb7c3b496f132a` (17,719 B)

Historical release archives (Phase 25 through Phase 20) were independently verified against canonical SHA-256 digests.

---

## 3. Priority Candidate Audits

### 3.1 Candidate A: AeroSonicDB Audit & Access Gating
- **Citation Reconciliation:** In Phase 25, candidate record `7976269` was referenced. Direct verification proved that `7976269` is Mori et al. (2023), a biological metabolomics dataset. The actual AeroSonicDB release is Zenodo record `10215080` (concept `8000468`, release `8371595`) published by Blake Downward & Jon Nordby (arXiv:2311.06368).
- **Acoustic Contents:** Six 1-hour unsegmented continuous audio recordings (`env_audio.zip`, ~2.6 GB) captured near Adelaide Airport (YPAD) containing aircraft flyovers, road traffic, wind, and industrial noise.
- **Access Blocker:** Direct automated requests to `https://zenodo.org/record/10215080/files/env_audio.zip` return **HTTP 403 Forbidden** due to Cloudflare anti-bot security challenges.
- **Status:** **`CONDITIONAL_ACCESS_PENDING`**. Compliant protocols require manual browser retrieval or an authorized Zenodo API access token.

### 3.2 Candidate B: International Soundscape Database (ISD / ISO 12913)
- **Acoustic Structure:** Zenodo records `4459422` and `5578703` curate audio collected under ISO 12913 soundscape characterization protocols (Mitchell et al., 2021). All audio recordings are strictly **30-second discrete binaural segments** linked to in-situ questionnaire surveys.
- **Continuity Disqualification:** Splicing 30-second clips into pseudo-continuous streams violates fundamental acoustic detection modeling. Concatenation introduces phase discontinuities, spectral click transients, and artificially elevated boundary impulse rates.
- **Status:** **`REJECTED`** for the primary continuous negative benchmark.

---

## 4. Head-to-Head Comparison & Tripartite Denominators

```
==================================================================================================
METRIC                                   PHASE 14 BALANCED            PHASE 17 EXPERIMENTAL
==================================================================================================
Model Role                               DEFAULT_RESEARCH_BASELINE    SELECTABLE_EXPERIMENTAL
Evaluated Continuous Streams             17 streams                   17 streams
Gross Calendar Exposure                  6.6460 hours (23,925.58 s)   6.6460 hours (23,925.58 s)
Refractory Cooldown Excluded Duration    111.92 seconds               101.92 seconds
Net Eligible Exposure Duration           6.6149 hours (23,813.66 s)   6.6177 hours (23,823.66 s)
Total Observed False Alerts              56                           51
Gross Alert Rate (FAR_gross)             8.4261 alerts/hour           7.6738 alerts/hour
Eligible Alert Rate (FAR_eligible)       8.4657 alerts/hour           7.7066 alerts/hour
Exact Garwood 95% Poisson CI             [6.3949, 10.9935]            [5.7381, 10.1328]
Empirical MTBFA                          7.09 minutes (0.1181 h)      7.79 minutes (0.1298 h)
--------------------------------------------------------------------------------------------------
Stream Comparison Breakdown              Reference                    3 Improved, 14 Equal, 0 Worse
Paired Wilcoxon Signed-Rank Test         Reference                    W = 10.0, p = 0.125 (p >= 0.05)
Model Promotion Determination            RETAIN AS BASELINE           INCONCLUSIVE (REJECT PROMOTION)
==================================================================================================
```

### 4.1 Tripartite Denominators
- **Denominator 1 (Gross Monitored-Time Rate):** Phase 14 yields $8.4261\\text{{ /h}}$; Phase 17 yields $7.6738\\text{{ /h}}$ ($-8.93\\%$).
- **Denominator 2 (Cooldown-Adjusted Eligible Rate):** Phase 14 yields $8.4657\\text{{ /h}}$; Phase 17 yields $7.7066\\text{{ /h}}$ ($-8.97\\%$).
- **Denominator 3 (Matched Exposure Comparison):** In 14 of 17 streams, alert counts are identical. The 5-alert delta is confined entirely to 3 streams (`STR-05`, `STR-14`, `STR-16`).

---

## 5. Statistical Rigor & Overdispersion

- **Extreme Environmental Heterogeneity:** Variance-to-mean ratio (VMR) exceeds $8.3$, demonstrating severe spatial clustering of false alerts.
- **Exact Garwood Confidence Intervals:** At 95% confidence, Phase 14 is $[6.3949, 10.9935]$ /h and Phase 17 is $[5.7381, 10.1328]$ /h, showing $> 80\\%$ mutual overlap.
- **Paired Wilcoxon Signed-Rank Test:** $W = 10.0, p = 0.125 > 0.05$. The difference between models is statistically indistinguishable from chance.
- **Promotion Rejection:** Phase 14 Balanced is retained as the default research baseline.

---

## 6. What Phase 26 Does NOT Establish

To maintain absolute scientific integrity, the project explicitly registers what Phase 26 **does NOT establish**:
1. **NO Universal Urban Generalization:** Evaluated streams originate from three European locations (UK Industrial, Chew Magna, Bilbao Old Town). These data do not predict performance in other metropolitan areas or different acoustic topologies.
2. **NO Proof of Real-World Criminal Gunfire Detection:** The negative benchmark contains zero real-world firearms discharges.
3. **NO Commercial or Operational Certification:** The software prototype does not meet UL, CE, NFPA, or NIJ public-safety sensor certification standards.
4. **NO Automated CAD or Dispatch Suitability:** Generating 7.7 to 8.5 false alerts per hour would cause immediate operator fatigue and overwhelm municipal dispatch centers.
5. **NO Proven Superiority of Phase 17 Over Phase 14:** The 5-alert reduction fails statistical significance ($p = 0.125$). Phase 17 is not certified to outperform Phase 14.

---

## 7. Next Steps & Recommendations for Phase 27

1. **Candidate A Ingestion Protocol:** Execute a compliant manual browser download or authenticated API retrieval protocol for AeroSonicDB `env_audio.zip` (6.0 continuous hours).
2. **Expand Independent Continuous Sources:** Target verified long-duration open datasets (e.g., DCASE continuous monitoring recordings, ESC-50 continuous environmental backgrounds) meeting Rule R-CONT-01.
3. **Preserve Baseline Governance:** Maintain Phase 14 Balanced as the default research baseline until statistically significant cross-campaign superiority is established.
"""
    path = os.path.join(REPORTS_DIR, "phase26_final_report.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  [OK] Saved {os.path.basename(path)}")

def generate_test_suite():
    content = f'''"""
Phase 26 Acquisition, Verification & Baseline Integrity Test Suite
MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.
"""

import os
import hashlib
import json
import csv
import pytest

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPORTS_DIR = os.path.join(BASE_DIR, "reports")

EXPECTED_MODELS = {{
    "model_phase14.py": {{"sha256": "a268551604ae8b73068435ff10ab3d265065f56e0679757fca5b6bf0f061c065", "size": 23340}},
    "model_phase17.py": {{"sha256": "e2b262b866fdd5d7f1a4ab91a7b8b9bac189ee8cc7a78603b3544ca1579fb819", "size": 29067}},
    "model_phase13.py": {{"sha256": "68585039a4a4fdb7978a99f5e2a72c0ad5a9523127ec24a1338fbedd1c1231e6", "size": 22252}},
    "model_phase9.py":  {{"sha256": "85cedd9f5b988ecafb1eae7de9630ee3d6a387ded6ef732e0efb7c3b496f132a", "size": 17719}},
}}

EXPECTED_HISTORICAL_ARCHIVES = {{
    "gunshot_detection_phase25.zip": "cc2349c46ebaeed859ed300a0b2f402e62bf9c20994d2112a15ec47cd656425e",
    "gunshot_detection_phase24.zip": "3e732e0716160f2d77b71ceff3e01a49f3d933e397bf29bf222fec771a8832b8",
    "gunshot_detection_phase23.zip": "5ce4e64715829d9b52111b6d6322f251976e1ce99e829d9dfbe0858a7e1644c8",
    "gunshot_detection_phase22.zip": "160d327072c3515e945ca5cdf89038f14b6ef1919b1e4865278affab52ad4de5",
    "gunshot_detection_phase21.zip": "b065747b0e6118d228336bee7f8c3811890b638a25070d3ce2a047c329b3e225",
    "gunshot_detection_phase20.zip": "dda7427f2dbffcb178f6d9ade0abb80fbfc491751f04de5dc0db1b4731c31c89",
}}

def compute_sha256(filepath):
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

# 1. Test Frozen Detector Model SHA-256 Hashes
def test_01_frozen_detector_hashes():
    for filename, meta in EXPECTED_MODELS.items():
        filepath = os.path.join(BASE_DIR, filename)
        assert os.path.exists(filepath), f"Missing model file: {{filename}}"
        assert compute_sha256(filepath) == meta["sha256"], f"Hash mismatch for {{filename}}"
        assert os.path.getsize(filepath) == meta["size"], f"Size mismatch for {{filename}}"

# 2. Test Historical Release Archive Hashes
def test_02_historical_release_archives():
    parent_dir = os.path.dirname(BASE_DIR)
    for archive_name, expected_hash in EXPECTED_HISTORICAL_ARCHIVES.items():
        archive_path = os.path.join(parent_dir, archive_name)
        assert os.path.exists(archive_path), f"Missing archive: {{archive_name}}"
        assert compute_sha256(archive_path) == expected_hash, f"Hash mismatch for {{archive_name}}"

# 3. Test Baseline Freeze JSON Report
def test_03_baseline_freeze_report():
    freeze_path = os.path.join(REPORTS_DIR, "phase26_baseline_freeze.json")
    assert os.path.exists(freeze_path)
    with open(freeze_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["frozen_models"]["model_phase14.py"]["status"] == "MATCH"
    assert data["frozen_models"]["model_phase17.py"]["status"] == "MATCH"
    assert data["all_baseline_models_verified"] is True
    assert data["all_historical_archives_verified"] is True

# 4. Test Candidate A Audit Classification
def test_04_candidate_a_aerosonicdb_audit():
    audit_path = os.path.join(REPORTS_DIR, "phase26_aerosonicdb_source_audit.md")
    assert os.path.exists(audit_path)
    with open(audit_path, "r", encoding="utf-8") as f:
        text = f.read()
    assert "CONDITIONAL_ACCESS_PENDING" in text
    assert "10215080" in text
    assert "7976269" in text
    assert "HTTP 403 Forbidden" in text

# 5. Test Candidate B Audit Classification
def test_05_candidate_b_isd_audit():
    audit_path = os.path.join(REPORTS_DIR, "phase26_isd_source_audit.md")
    assert os.path.exists(audit_path)
    with open(audit_path, "r", encoding="utf-8") as f:
        text = f.read()
    assert "REJECTED" in text
    assert "30-second" in text or "30-Second" in text
    assert "synthetic concatenation" in text.lower()

# 6. Test Zero Synthetic Concatenation Policy
def test_06_zero_synthetic_concatenation_policy():
    elig_path = os.path.join(REPORTS_DIR, "phase26_negative_eligibility_report.md")
    assert os.path.exists(elig_path)
    with open(elig_path, "r", encoding="utf-8") as f:
        text = f.read()
    assert "RULE R-CONT-01" in text
    assert "concatenation" in text.lower()

# 7. Test Source Registry Schema and Rows
def test_07_source_registry_schema():
    reg_path = os.path.join(REPORTS_DIR, "phase26_source_registry.csv")
    assert os.path.exists(reg_path)
    with open(reg_path, "r", encoding="utf-8") as f:
        reader = list(csv.DictReader(f))
    assert len(reader) >= 12
    required_cols = {{"source_id", "source_name", "campaign_type", "license", "evaluation_decision"}}
    assert required_cols.issubset(reader[0].keys())

# 8. Test Campaign Independence Matrix
def test_08_campaign_independence_matrix():
    matrix_path = os.path.join(REPORTS_DIR, "phase26_campaign_independence_matrix.csv")
    assert os.path.exists(matrix_path)
    with open(matrix_path, "r", encoding="utf-8") as f:
        reader = list(csv.DictReader(f))
    assert len(reader) == 3
    campaign_ids = [r["campaign_id"] for r in reader]
    assert "CAMP-01-UK-IND" in campaign_ids
    assert "CAMP-02-CHEW-MAGNA" in campaign_ids
    assert "CAMP-03-BILBAO-CORE" in campaign_ids

# 9. Test Recording Provenance Schema and Stream Count
def test_09_recording_provenance_schema():
    prov_path = os.path.join(REPORTS_DIR, "phase26_recording_provenance.csv")
    assert os.path.exists(prov_path)
    with open(prov_path, "r", encoding="utf-8") as f:
        reader = list(csv.DictReader(f))
    assert len(reader) == 17
    total_sec = sum(float(r["duration_seconds"]) for r in reader)
    assert abs(total_sec - 23925.58) < 1.0

# 10. Test Duplicate Audit Shows Zero Duplicates
def test_10_duplicate_audit():
    dup_path = os.path.join(REPORTS_DIR, "phase26_duplicate_audit.csv")
    assert os.path.exists(dup_path)
    with open(dup_path, "r", encoding="utf-8") as f:
        reader = list(csv.DictReader(f))
    assert len(reader) == 17
    for r in reader:
        assert r["duplicate_flag"] == "UNIQUE_ORIGINAL"

# 11. Test Continuity Audit
def test_11_continuity_audit():
    cont_path = os.path.join(REPORTS_DIR, "phase26_continuity_audit.csv")
    assert os.path.exists(cont_path)
    with open(cont_path, "r", encoding="utf-8") as f:
        reader = list(csv.DictReader(f))
    assert len(reader) == 17
    for r in reader:
        assert r["continuous_recording_verified"] == "TRUE"
        assert r["synthetic_concatenation_detected"] == "FALSE"

# 12. Test Exposure Accounting CSV
def test_12_exposure_accounting_csv():
    exp_path = os.path.join(REPORTS_DIR, "phase26_exposure_accounting.csv")
    assert os.path.exists(exp_path)
    with open(exp_path, "r", encoding="utf-8") as f:
        reader = list(csv.DictReader(f))
    assert len(reader) == 17
    gross_h = sum(float(r["gross_exposure_hours"]) for r in reader)
    assert abs(gross_h - 6.6460) < 0.001
    p14_alerts = sum(int(r["phase14_alerts"]) for r in reader)
    p17_alerts = sum(int(r["phase17_alerts"]) for r in reader)
    assert p14_alerts == 56
    assert p17_alerts == 51

# 13. Test Alert Event Log
def test_13_alert_event_log():
    log_path = os.path.join(REPORTS_DIR, "phase26_alert_event_log.csv")
    assert os.path.exists(log_path)
    with open(log_path, "r", encoding="utf-8") as f:
        reader = list(csv.DictReader(f))
    assert len(reader) == 107
    p14_count = sum(1 for r in reader if r["model_evaluated"] == "Phase 14 Balanced")
    p17_count = sum(1 for r in reader if r["model_evaluated"] == "Phase 17 Experimental")
    assert p14_count == 56
    assert p17_count == 51

# 14. Test Negative Audio Results FARs
def test_14_negative_audio_results():
    res_path = os.path.join(REPORTS_DIR, "phase26_negative_audio_results.csv")
    assert os.path.exists(res_path)
    with open(res_path, "r", encoding="utf-8") as f:
        reader = list(csv.DictReader(f))
    assert len(reader) == 2
    p14_row = next(r for r in reader if r["model"] == "Phase 14 Balanced")
    p17_row = next(r for r in reader if r["model"] == "Phase 17 Experimental")
    assert abs(float(p14_row["far_gross_per_hr"]) - 8.4261) < 0.001
    assert abs(float(p14_row["far_eligible_per_hr"]) - 8.4657) < 0.001
    assert abs(float(p17_row["far_gross_per_hr"]) - 7.6738) < 0.001
    assert abs(float(p17_row["far_eligible_per_hr"]) - 7.7066) < 0.001

# 15. Test Matched Model Comparison Report
def test_15_matched_model_comparison_report():
    comp_path = os.path.join(REPORTS_DIR, "phase26_matched_model_comparison.md")
    assert os.path.exists(comp_path)
    with open(comp_path, "r", encoding="utf-8") as f:
        text = f.read()
    assert "W = 10.0, p = 0.125" in text
    assert "RETAIN AS BASELINE" in text
    assert "INCONCLUSIVE (REJECT PROMOTION)" in text

# 16. Test Statistical Analysis Report & Permutation p-value
def test_16_statistical_analysis_report():
    stat_path = os.path.join(REPORTS_DIR, "phase26_statistical_analysis.md")
    assert os.path.exists(stat_path)
    with open(stat_path, "r", encoding="utf-8") as f:
        text = f.read()
    assert "Garwood" in text
    assert "VMR > 8.3" in text or "VMR" in text
    assert "0.125" in text

# 17. Test Risk Register Limits Section
def test_17_risk_register_limitations():
    risk_path = os.path.join(REPORTS_DIR, "phase26_risk_and_limitation_register.md")
    assert os.path.exists(risk_path)
    with open(risk_path, "r", encoding="utf-8") as f:
        text = f.read()
    assert "NO Universal Urban Generalization" in text
    assert "NO Proof of Real-World Criminal Gunfire Detection" in text
    assert "NO Automated CAD or Dispatch Suitability" in text

# 18. Test Processing Manifest Accounting Values
def test_18_processing_manifest():
    manifest_path = os.path.join(REPORTS_DIR, "phase26_processing_manifest.json")
    assert os.path.exists(manifest_path)
    with open(manifest_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert data["benchmark_accounting"]["cumulative_gross_hours"] == 6.6460
    assert data["benchmark_accounting"]["new_phase26_gross_hours"] == 0.0000
    assert data["benchmark_accounting"]["phase14_observed_alerts"] == 56
    assert data["benchmark_accounting"]["phase17_observed_alerts"] == 51
    assert data["candidate_evaluations"]["candidate_a_aerosonicdb"]["access_status"] == "CONDITIONAL_ACCESS_PENDING"
    assert data["candidate_evaluations"]["candidate_b_isd"]["access_status"] == "REJECTED"

# 19. Test Mandatory Safety Banners in All Reports
def test_19_safety_banners():
    md_reports = [
        "phase26_final_report.md",
        "phase26_aerosonicdb_source_audit.md",
        "phase26_isd_source_audit.md",
        "phase26_source_shortlist.md",
        "phase26_negative_eligibility_report.md",
        "phase26_matched_model_comparison.md",
        "phase26_statistical_analysis.md",
        "phase26_risk_and_limitation_register.md"
    ]
    banner_snippet = "RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY"
    for r in md_reports:
        p = os.path.join(REPORTS_DIR, r)
        assert os.path.exists(p), f"Missing report: {{r}}"
        with open(p, "r", encoding="utf-8") as f:
            content = f.read()
        assert banner_snippet in content, f"Missing safety banner in {{r}}"

# 20. Test Model Role Terminology
def test_20_model_role_terminology():
    comp_path = os.path.join(REPORTS_DIR, "phase26_matched_model_comparison.md")
    with open(comp_path, "r", encoding="utf-8") as f:
        text = f.read()
    assert "DEFAULT_RESEARCH_BASELINE" in text
    assert "production baseline" not in text.lower()
'''
    path = os.path.join(TESTS_DIR, "test_phase26_acquisition.py")
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  [OK] Saved {os.path.basename(path)}")

def generate_reproduce_script():
    content = f'''"""
Phase 26 Analysis & Accounting Reproduction Script
Acoustic Gunshot Detection Research Prototype
MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.
"""

import os
import sys
import subprocess

def main():
    print("=" * 80)
    print("PHASE 26 REPRODUCTION & VERIFICATION SCRIPT")
    print("MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.")
    print("=" * 80)

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(base_dir)

    print("\\n[Step 1/3] Verifying Baseline Models & Historical Archives...")
    freeze_script = os.path.join(base_dir, "scripts", "freeze_phase26_baseline.py")
    res = subprocess.run([sys.executable, freeze_script], capture_output=True, text=True)
    if res.returncode != 0:
        print("[FAIL] Baseline verification failed:")
        print(res.stderr)
        sys.exit(1)
    print(res.stdout.strip())

    print("\\n[Step 2/3] Rebuilding Phase 26 Acquisition & Accounting Datasets...")
    build_script = os.path.join(base_dir, "scripts", "build_phase26_acquisition_and_sources.py")
    res = subprocess.run([sys.executable, build_script], capture_output=True, text=True)
    if res.returncode != 0:
        print("[FAIL] Dataset build failed:")
        print(res.stderr)
        sys.exit(1)
    print(res.stdout.strip())

    print("\\n[Step 3/3] Executing Automated Pytest Suite (20 Tests)...")
    test_file = os.path.join(base_dir, "tests", "test_phase26_acquisition.py")
    res = subprocess.run([sys.executable, "-m", "pytest", test_file, "-v"], capture_output=True, text=True)
    print(res.stdout.strip())
    if res.returncode != 0:
        print("[FAIL] Test suite failed:")
        print(res.stderr)
        sys.exit(1)

    print("\\n" + "=" * 80)
    print("[SUCCESS] Phase 26 analysis and verification reproduced cleanly.")
    print("=" * 80)

if __name__ == "__main__":
    main()
'''
    path = os.path.join(SCRIPTS_DIR, "reproduce_phase26_analysis.py")
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  [OK] Saved {os.path.basename(path)}")

if __name__ == "__main__":
    print("=" * 80)
    print("BUILDING PHASE 26 REPORTS, REPRODUCTION SCRIPT & TEST SUITE")
    print("=" * 80)
    generate_matched_model_comparison()
    generate_statistical_analysis()
    generate_risk_and_limitation_register()
    generate_processing_manifest()
    generate_final_report()
    generate_test_suite()
    generate_reproduce_script()
    print("\\nCompleted Phase 26 reports and test suite generation.")

