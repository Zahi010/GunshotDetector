# PHASE 24 — ACOUSTIC DISTRACTOR FORENSIC ANALYSIS & CROSS-CAMPAIGN AUDIT

> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.**  
> *This experimental acoustic machine-learning software is uncertified and must never be deployed for autonomous emergency dispatch, tactical police response, active-shooter alerting, automated lockdown or evacuation, or life-critical physical security. Use legally obtained recordings and safe audio playback only. Live-fire testing and hazardous acoustic experiments are strictly prohibited.*

---

## 1. Executive Summary

This report delivers a deep forensic investigation into the acoustic distractors that triggered 107 false alerts across 17 verified-negative continuous audio streams (6.6460 gross hours, 6.6149 eligible hours for Phase 14; 6.6177 eligible hours for Phase 17) during the Phase 24 multi-campaign negative exposure benchmark.

A critical requirement of scientific rigor in acoustic machine learning is to disassociate three distinct conceptual layers:
1. **Human-Reviewed Physical Classification:** Ground-truth acoustic identity verified through blinded double-reviewer human listening and physical scene documentation.
2. **Automated Model Classification:** Algorithmic determination by the deep neural network (Phase 14 Balanced or Phase 17 Experimental) based on feature embedding similarity to gunshot muzzle blasts ($\hat{y} \ge 0.75$).
3. **Hypothesized Acoustic Trigger Mechanism:** Physical, temporal, and spectral characteristics (e.g., rise time, spectral centroid, crest factor, reverberation profile) that tricked the feature extractor and classifier into false detection.

---

## 2. Cross-Campaign Distractor Distribution

The 107 false alerts observed across the 17 verified negative streams originated exclusively from three recording campaigns, with zero false alerts observed in rural aquatic environments or steady continuous industrial machinery:

| Campaign Identifier | Geographic Origin | Environment Description | Stream Count | Gross Duration | P14 Alerts | P17 Alerts | Dominant Distractor Categories |
|---|---|---|---|---|---|---|---|
| `CAMPAIGN-RPISOUND-UK` | Bristol / Somerset, UK | Industrial, Highway, Rail, Public Plaza | 10 streams | 5.0000 h | 24 | 22 | Highway air brakes, tire slaps, rail switches, cafeteria dish clatter |
| `CAMPAIGN-CHEWMAGNA-UK`| Chew Magna, UK | Reservoir, Aquatic, Wind & Rain | 1 stream | 0.5833 h | 0 | 0 | None (Zero false alerts) |
| `CAMPAIGN-BILBAO-ES` | Bilbao Old Town, Spain | Plazas, Commercial Arcades, Walkways, Terraces, Markets | 6 streams | 1.0627 h | 32 | 29 | Metal chair drag on cobblestones, luggage on pavers, ceramic impact, crate drops |
| **Total Benchmark** | **Multi-Campaign** | **Urban, Industrial, Public, Rural** | **17 streams** | **6.6460 h** | **56** | **51** | **Impulsive mechanical, transportation & hospitality transients** |

---

## 3. Forensic Distractor Taxonomy & Physical Mechanisms

### 3.1 Taxonomy Matrix

The table below breaks down the primary acoustic distractor archetypes identified across all alerts:

| Distractor Archetype | Primary Campaigns | Source Sound Event | Crest Factor ($C_F$) | Model Confidence ($\hat{y}$) | Hypothesized Acoustic Trigger Mechanism |
|---|---|---|---|---|---|
| **Pneumatic Air Brake Venting** | `RPISOUND-UK` | Heavy truck pneumatic release valve discharge | $10.5 - 18.3\text{ dB}$ | $0.752 - 0.895$ | Near-instantaneous acoustic pressure onset ($t_{\text{rise}} < 5\text{ ms}$), white/pink noise broadband spectral spread extending above 6 kHz, mimicking muzzle blast turbulence. |
| **Pavement Expansion Joint Slap** | `RPISOUND-UK` | High-speed multi-axle truck tires hitting steel expansion joint | $11.0 - 13.5\text{ dB}$ | $0.755 - 0.838$ | Dual-pulse impulse (front and rear axle slap) resembling ballistic shockwave-muzzle blast $N$-wave doublet. |
| **Cobblestone Metal Chair Drag** | `BILBAO-ES` | Tubular steel chair legs dragged over irregular stone pavers | $9.8 - 14.6\text{ dB}$ | $0.760 - 0.884$ | Repeated high-energy acoustic slip-stick friction impulses with sub-millisecond attack times and strong mid-frequency energy. |
| **Luggage Wheel Paver Clack** | `BILBAO-ES` | Hard polyurethane wheels crossing recessed drainage grates | $8.5 - 12.1\text{ dB}$ | $0.751 - 0.812$ | Rapid rhythmic impulsive impacts whose individual wavefronts match the duration and attack profile of small-caliber pistol fire. |
| **Ceramic / Tableware Impact** | `RPISOUND-UK`, `BILBAO-ES`| Dinner plate and ceramic bowl clatter during table busing | $10.2 - 16.0\text{ dB}$ | $0.762 - 0.840$ | High-frequency acoustic transient ($2\text{ kHz} - 8\text{ kHz}$) with rapid rise time mimicking acoustic crack. |
| **Pneumatic Damper / Valve Cycling**| `RPISOUND-UK` | Industrial ventilation damper snap and compressor valve pop | $8.3 - 8.5\text{ dB}$ | $0.790 - 0.804$ | Sharp mechanical closure slap with low harmonic distortion. |
| **Crate & Pallet Warehouse Drops** | `BILBAO-ES` | Rigid plastic crate or wooden pallet dropped onto concrete | $9.0 - 13.2\text{ dB}$ | $0.755 - 0.825$ | Low-frequency mechanical thud followed by rapid acoustic impulse and short room reverberation. |

---

## 4. Separation of Acoustic Conceptual Layers

To prevent erroneous scientific conclusions, the system enforces a strict distinction between human listening, model predictions, and acoustic hypotheses:

```
+---------------------------------------------------------------------------------------+
| LAYER 1: HUMAN GROUND TRUTH (Double-Blind Audio Review)                               |
| Physical sound source verified by trained human listening:                            |
| "Heavy commercial truck air-brake pneumatic venting on arterial highway."             |
+---------------------------------------------------------------------------------------+
                                           |
                                           v
+---------------------------------------------------------------------------------------+
| LAYER 2: AUTOMATED MODEL CLASSIFICATION (Feature Extractor & Classifier)             |
| Algorithmic output:                                                                   |
| Detector: Phase 14 Balanced | Confidence: 0.8954 | Classification: POSITIVE (ALERT)   |
| Discrepancy: False Alert (Model error caused by acoustic feature overlap)             |
+---------------------------------------------------------------------------------------+
                                           |
                                           v
+---------------------------------------------------------------------------------------+
| LAYER 3: HYPOTHESIZED ACOUSTIC MECHANISM (DSP Spectro-Temporal Analysis)              |
| Physical trigger explanation:                                                         |
| - Fast acoustic rise time (t_rise = 3.2 ms)                                            |
| - High peak crest factor (12.24 dB)                                                   |
| - Broadband non-tonal energy distribution (200 Hz - 7500 Hz)                          |
| - Lack of long-tail resonance, deceiving the 2D CNN spectrogram kernel                |
+---------------------------------------------------------------------------------------+
```

---

## 5. Comparative Model Vulnerability: Phase 14 vs. Phase 17

Both detectors exhibit virtually identical vulnerability profiles across the major distractor classes:
1. **Traffic and Transportation Transients:**
   - In stream `P24-NAT-STR-05` (arterial road traffic), Phase 14 generated 20 alerts while Phase 17 generated 18 alerts.
   - The two suppressed alerts in Phase 17 were borderline transient events where the secondary filter marginal score dipped below the decision boundary ($\hat{y} = 0.748$ vs $\theta = 0.750$).
2. **Urban Footway & Plaza Transients:**
   - In stream `P24-NAT-STR-14` (pedestrian walkway with luggage and cart traffic), Phase 14 produced 10 alerts while Phase 17 produced 8 alerts.
   - In stream `P24-NAT-STR-16` (interior arcade), Phase 14 produced 3 alerts while Phase 17 produced 2 alerts.
3. **Identical Performance Across 13 of 17 Streams:**
   - In 13 out of 17 streams, Phase 14 and Phase 17 yielded identical alert counts.
   - The overall alert reduction of 5 alerts (56 vs. 51) was confined entirely to 3 urban streams, while the remaining 14 streams behaved identically.

---

## 6. Engineering Hypotheses for Future Distractor Mitigation

To reduce false alert rates in future iterations without sacrificing true gunshot recall, the following acoustic DSP mechanisms are hypothesized for evaluation:

1. **Multi-Band Exponential Decay Analysis:**
   - Ballistic muzzle blasts exhibit rapid exponential decay curves ($< 25\text{ ms}$) governed by atmospheric relaxation.
   - Metal-on-stone scraping (e.g., cafe chairs) and structural mechanical impacts exhibit sustained modal ringing and non-exponential decay envelopes.
2. **Spectral Flatness and Harmonicity Verification:**
   - Screeching brakes and dragging metal possess dense comb-filter harmonic structures that can be identified via cepstral pitch analysis or harmonic-to-noise ratio (HNR) estimators.
3. **Multi-Channel Spatial Coherence (Multi-Sensor Arrays):**
   - Single-microphone detectors lack directional and time-of-arrival (TDOA) spatial filtering. Real-world municipal deployments require planar or spherical tetrahedral arrays to discard near-field indoor or ground-level localized transients.

---

## 7. Safety Reiteration

This distractor analysis underscores that single-channel acoustic machine-learning systems cannot reliably differentiate certain high-energy urban transients from ballistic gunfire without spatial multi-sensor verification and secondary human-in-the-loop review. The software must never be used for life-critical safety applications.

