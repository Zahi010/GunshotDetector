# PHASE 34 — CAMPAIGN INDEPENDENCE & CLUSTERING AUDIT
## Workstream 4: Evaluation of Environmental Correlation, Acquisition Coupling & Cluster Effects

> **MANDATORY SAFETY DESIGNATION**  
> **RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY**  
> *This experimental acoustic machine-learning software is uncertified and must never be deployed for autonomous emergency dispatch, tactical police response, active-shooter alerting, automated evacuation, building lockdown, or life-critical physical security. Use legally obtained recordings and safe audio playback only. Live-fire testing and hazardous acoustic experiments are strictly prohibited.*

---

## 1. Executive Summary & Objective

Workstream 4 investigates the statistical independence and environmental clustering of the 23 continuous audio recordings comprising the benchmark.

A persistent vulnerability in earlier phases was the implicit assumption that the 23 streams could be modeled as independent, identically distributed (i.i.d.) statistical units. This audit rigorously examines:
1. The true number of genuinely independent acoustic acquisition campaigns ($K = 4$).
2. Intra-campaign coupling, hardware sharing, and temporal/environmental correlations.
3. The validity of campaign-level vs. recording-level comparisons.
4. The overwhelming exposure and alert dominance exerted by the Adelaide AeroSonicDB campaign.

---

## 2. Inventory of Acquisition Campaigns & Coupling Forensics

Forensic examination of original repository records, metadata manifests, and acoustic profiles establishes that the 23 streams originate from **only four distinct acquisition campaigns**:

```
[23 Continuous Audio Streams]
 ├── Campaign 1: Southampton Industrial & Urban (10 streams | 5.50 hr | 43.5% duration)
 ├── Campaign 2: Chew Magna Aquatic Reservoir   ( 1 stream  | 0.58 hr |  4.6% duration)
 ├── Campaign 3: Bilbao Old Town Urban Corridor ( 6 streams | 0.56 hr |  4.5% duration)
 └── Campaign 4: Adelaide Airport Perimeter     ( 6 streams | 6.00 hr | 47.5% duration)
```

### 2.1 Campaign 1: Southampton Industrial & Urban Ambient (`CAMPAIGN-SOUTHAMPTON-EXP1`)
- **Repository DOI:** `10.5281/zenodo.7493820` (Raspberry Pi Sound Logger Project)
- **Geographic Location:** Southampton, Hampshire, United Kingdom
- **Stream Inventory (10 files):** `phase16_industrial_compressor_pneumatic_60min.wav`, `exhaust_ventilation`, `concrete_mixer`, `monoblock_pump`, `traffic_road_arterial`, `traffic_transit_train`, `canteen_plaza`, `percussion_acoustic_drums`, `washing_machine`, `laptop_exhaust`.
- **Intra-Campaign Coupling:**
  - Files share the same custom Raspberry Pi MEMS/USB acoustic acquisition hardware and pre-amplification chain.
  - While acoustic scenarios differ (industrial yard, transit line, domestic interior), they reflect common urban background reverberation and regional atmospheric properties.
  - Streams are not mutually independent from a sensor-hardware or recording-campaign perspective.

### 2.2 Campaign 2: Chew Magna Rural Soundscape (`CAMPAIGN-CHEW-MAGNA`)
- **Repository DOI:** `10.5281/zenodo.3938837` (Chew Magna Soundscape Survey)
- **Geographic Location:** Chew Magna, Somerset, United Kingdom
- **Stream Inventory (1 file):** `phase16_natural_weather_aquatic_reservoir_35min.wav` (2,100 s / 0.5833 hr).
- **Intra-Campaign Coupling:**
  - Single isolated environmental recording session at an outdoor reservoir. Zero intra-campaign clustering.
  - Characterized by water flow, wind turbulence, and distant avians.

### 2.3 Campaign 3: Bilbao Old Town Urban Soundscape (`CAMPAIGN-BILBAO`)
- **Repository DOI:** `10.5281/zenodo.18716205` / `18561165` (Bilbao Soundscape)
- **Geographic Location:** Casco Viejo (Old Town), Bilbao, Basque Country, Spain
- **Stream Inventory (6 files):** `phase17_urban_exterior_plaza_30min.wav`, `interior_commercial`, `exterior_walkway`, `exterior_terrace`, `interior_arcade`, `interior_hall`.
- **Intra-Campaign Coupling:**
  - **Severe Geographic & Acoustic Coupling:** All 6 files were captured in the narrow, cobblestone pedestrian canyons and interior arcades of Casco Viejo within a concentrated acquisition period.
  - **Shared Acoustic Signatures:** Heavy architectural reverberation, footsteps on paving, muffled Spanish conversational babble, delivery cart rattles, and distant urban traffic echoes.
  - Treating these 6 short files (~330 s each) as 6 independent statistical observations artificially inflates degrees of freedom. They represent 6 spatial slices of a single urban soundscape campaign.

### 2.4 Campaign 4: Adelaide Airport Perimeter Aviation Audio (`CAMPAIGN-ADELAIDE-AEROSONIC`)
- **Repository DOI:** `10.5281/zenodo.10215080` / `8371595` (AeroSonicDB / YPAD-0523)
- **Geographic Location:** Adelaide Airport (YPAD), South Australia, Australia
- **Stream Inventory (6 files):** `1_AUDIO_16k.wav` through `6_AUDIO_16k.wav` (3,600 s each = 6.0000 hr total).
- **Intra-Campaign Coupling:**
  - **High Acoustic Homogeneity:** Captured continuously along the airfield perimeter fence line.
  - **Identical Environmental Conditions:** All files feature low-altitude jet takeoff/landing profiles, turboprop climb-outs, ground auxiliary power units (APUs), and open-field wind noise.
  - Highly coupled temporal and atmospheric characteristics across consecutive 1-hour segments.

---

## 3. Exposure and Alert Skew Analysis

The four campaigns do not contribute equal exposure or alert density:

```
Exposure Share (% of 12.6460 hr):
  Adelaide Airport:     [████████████████████████] 47.45% (6.0000 hr)
  Southampton:          [████████████████████    ] 43.49% (5.5000 hr)
  Chew Magna:           [██                      ]  4.61% (0.5833 hr)
  Bilbao:               [██                      ]  4.45% (0.5627 hr)

Observed Alerts Share (% of 287 total alerts across P14 + P17):
  Adelaide Airport:     [██████████████████████████████] 62.72% (180 alerts)
  Bilbao:               [██████████                    ] 21.25% ( 61 alerts)
  Southampton:          [████████                      ] 16.03% ( 46 alerts)
  Chew Magna:           [                              ]  0.00% (  0 alerts)
```

### Critical Observations
1. **Adelaide Dominance:** AeroSonicDB accounts for **47.5% of total exposure** and **62.7% of all observed alerts**. Consequently, aggregate corpus metrics (such as corpus-wide gross FAR) primarily measure detector behavior on Adelaide aircraft noise rather than general urban environments.
2. **Bilbao Disproportion:** Bilbao represents only **4.45% of total exposure** ($0.5627\text{ hr}$), yet generated **21.3% of all alerts** (61 alerts). Bilbao's gross FAR ($56.87/\text{hr}$ in P14, $51.54/\text{hr}$ in P17) is an extreme outlier, driven by pedestrian echoes and resonant stone alley acoustics.
3. **Southampton Quiescence:** Southampton represents **43.5% of exposure** ($5.5000\text{ hr}$) but generated only 46 alerts (16.0%), with a low FAR of $4.36/\text{hr}$.

---

## 4. Implications for Statistical Hypothesis Testing

### 4.1 The Unit-of-Analysis Dilemma
- **Stream-Level Testing ($N = 23$):**  
  Treating each of the 23 files as an independent pair assumes that the difference observed in `P27-NAT-STR-12` (Bilbao Plaza) is independent of `P27-NAT-STR-13` (Bilbao Commercial). In reality, intra-campaign correlation inflates Type I error rates.
  Furthermore, because 15 out of 23 streams have $d = 0$, the effective sample size for Wilcoxon testing collapses to $n_{\text{eff}} = 8$, yielding inadequate statistical power.
- **Campaign-Level Testing ($K = 4$):**  
  Aggregating to the campaign level eliminates intra-campaign pseudo-replication:
  - Southampton: $24 - 22 = \mathbf{+2}$ (favors P17)
  - Chew Magna: $0 - 0 = \mathbf{0}$ (tied)
  - Bilbao: $32 - 29 = \mathbf{+3}$ (favors P17)
  - Adelaide: $72 - 108 = \mathbf{-36}$ (favors P14)
  However, with only $K = 4$ campaigns (and one tie), the effective sample size is $k_{\text{eff}} = 3$. A two-sided binomial sign test on $k = 3$ can yield at best $p = 2 \times 0.5^3 = 0.2500$, which **mathematically cannot achieve statistical significance ($\alpha = 0.05$) under any outcome**.

### 4.2 Guidance for Statistical Interpretation
1. **Do not claim equivalence:** Non-significant test results ($p = 0.156$ asymptotic, $p = 0.211$ tied permutation) must never be reported as evidence that Phase 14 and Phase 17 perform equally. The sample size ($N = 23, n_{\text{eff}} = 8$) is fundamentally underpowered.
2. **Context-Specific Superiority:**
   - In European urban, industrial, and pedestrian corridors (Southampton + Bilbao, 6.06 hr exposure), Phase 17 reduced false alerts from 56 to 51 ($-5$ alerts, $-8.9\%$).
   - In aviation environments (Adelaide, 6.00 hr exposure), Phase 17 increased false alerts from 72 to 108 ($+36$ alerts, $+50.0\%$) due to aircraft drone fragmentation.
3. **Conclusion:** Phase 17's performance is highly environment-dependent, not uniformly superior or inferior across campaigns.

