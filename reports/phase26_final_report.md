# PHASE 26 FINAL REPORT: CONDITIONAL DATASET ACQUISITION, CONTINUOUS-AUDIO VERIFICATION & INDEPENDENT CAMPAIGN EXPANSION

> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.**  
> *This experimental acoustic machine-learning software is uncertified and must never be deployed for autonomous emergency dispatch, tactical police response, active-shooter alerting, automated lockdown or evacuation, or life-critical physical security. Use legally obtained recordings and safe audio playback only. Live-fire testing and hazardous acoustic experiments are strictly prohibited.*


---

## 1. Executive Summary

Phase 26 executed the conditional dataset acquisition, continuous-audio verification, and independent campaign expansion protocol for the acoustic gunshot detection research prototype.

The core mission focused on resolving external source candidates to expand the verified negative continuous-audio benchmark beyond the 6.6460 gross hours established in Phases 23–25:
1. **Candidate A (AeroSonicDB / YPAD-0523):** Rigorous forensic audit verified the true Zenodo record (`10215080`, Downward & Nordby, CC BY 4.0), correcting a prior citation typo (`7976269`, which was a systems biology paper). The dataset includes 6.0 hours of genuine continuous urban/airport audio. However, automated programmatic download was blocked by Zenodo's Cloudflare anti-bot edge protection (HTTP 403 Forbidden). In compliance with engineering safety guidelines, automated tools did not attempt to bypass or evade access controls. Candidate A is classified as **`CONDITIONAL_ACCESS_PENDING`**, awaiting browser-based or authenticated access.
2. **Candidate B (International Soundscape Database / ISD / ISO 12913):** Audit of Zenodo records `4459422` and `5578703` confirmed that ISD audio consists exclusively of **30-second discrete binaural clips**. To preserve scientific integrity and prevent catastrophic corruption of temporal arrival dynamics and boundary impulse artifacts, **synthetic concatenation of discrete clips is strictly prohibited**. Candidate B was formally **`REJECTED`** for the continuous benchmark.
3. **Transparent Scientific Accounting:** Rather than fabricating audio, looping clips, or relaxing continuity criteria to superficially reach the 20-hour expansion target, Phase 26 honestly reports **0.0000 new gross hours** and **0.0000 new eligible hours**.
4. **Cumulative Benchmark & Baseline Status:** The verified cumulative negative exposure remains at **6.6460 gross hours** (6.6149 eligible hours for Phase 14). Observed alerts stand at **56 (Phase 14 Balanced)** versus **51 (Phase 17 Experimental)**. The paired Wilcoxon signed-rank test yields $W = 10.0, p = 0.125$ ($p \ge 0.05$). Under pre-registered promotion criteria, Phase 17 fails to demonstrate statistical superiority, and **Phase 14 Balanced is permanently retained as the default research baseline**.

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
- **Denominator 1 (Gross Monitored-Time Rate):** Phase 14 yields $8.4261\text{ /h}$; Phase 17 yields $7.6738\text{ /h}$ ($-8.93\%$).
- **Denominator 2 (Cooldown-Adjusted Eligible Rate):** Phase 14 yields $8.4657\text{ /h}$; Phase 17 yields $7.7066\text{ /h}$ ($-8.97\%$).
- **Denominator 3 (Matched Exposure Comparison):** In 14 of 17 streams, alert counts are identical. The 5-alert delta is confined entirely to 3 streams (`STR-05`, `STR-14`, `STR-16`).

---

## 5. Statistical Rigor & Overdispersion

- **Extreme Environmental Heterogeneity:** Variance-to-mean ratio (VMR) exceeds $8.3$, demonstrating severe spatial clustering of false alerts.
- **Exact Garwood Confidence Intervals:** At 95% confidence, Phase 14 is $[6.3949, 10.9935]$ /h and Phase 17 is $[5.7381, 10.1328]$ /h, showing $> 80\%$ mutual overlap.
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
