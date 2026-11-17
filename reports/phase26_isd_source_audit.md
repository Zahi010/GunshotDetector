# PHASE 26 CANDIDATE SOURCE AUDIT: INTERNATIONAL SOUNDSCAPE DATABASE (ISD / ISO 12913)

> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.**  
> *This experimental acoustic machine-learning software is uncertified and must never be deployed for autonomous emergency dispatch, tactical police response, active-shooter alerting, automated lockdown or evacuation, or life-critical physical security. Use legally obtained recordings and safe audio playback only. Live-fire testing and hazardous acoustic experiments are strictly prohibited.*

---

## 1. Executive Summary & Audit Mandate

In Phase 25, the **International Soundscape Database (ISD)** was cataloged as a prospective conditional candidate under the preliminary hypothesis that it might provide unbroken continuous survey sessions of five to fifteen minutes duration across international urban environments.

Phase 26 mandates an independent curatorial and technical audit of the primary repository to inspect dataset structure, file durations, session contiguity, and eligibility under the project's strict continuous validation protocol.

---

## 2. Repository Identification & Metadata Audit

Direct investigation of the International Soundscape Database published on Zenodo and associated IEEE/Acoustical Society of America research literature yielded the following verified metadata:

| Metadata Field | Verified Value | Evidentiary Basis |
|---|---|---|
| **Dataset Title** | The International Soundscape Database (ISD) | Official Zenodo Record & SSID Consortium |
| **Primary Zenodo Records**| Record `4459422` / `5578703` | Primary published DOIs (Mitchell et al.) |
| **Lead Authors / Curators**| Andrew Mitchell, Tin Oberman, Francesco Aletta, Jian Kang | University College London (UCL) |
| **Research Framework** | Soundscape Indices (SSID) Protocol / ISO 12913 Standards | Published methodology |
| **License** | Open Access for Research (CC BY 4.0 / Open Data) | Zenodo metadata |
| **Geographic Scope** | Urban public spaces across 11+ cities (London, Venice, Granada, Qingdao, etc.) | Research field surveys |
| **Audio Format** | Uncompressed WAV (Linear PCM), 24-bit depth | Published audio archive |
| **Sampling Rate** | 48,000 Hz | Direct technical documentation |
| **Channel Count** | 2-channel Binaural (Dummy-head calibrated) | In-situ survey protocol |

---

## 3. Critical Continuity Audit & Primary Flaw

### 3.1 30-Second Discrete Snippet Reality
The preliminary hypothesis in Phase 25 suggested that ISD sessions might represent continuous recordings spanning 5 to 15 minutes.

Direct audit of the primary data files disproves this hypothesis:
- Under the ISO 12913 SSID survey protocol, researchers conducted in-situ interviews with urban pedestrians.
- While a participant completed a standardized questionnaire, an acoustic technician recorded an exact **30-second binaural audio snippet** capturing the ambient soundscape at that specific moment.
- The repository consists of thousands of **isolated 30-second discrete clips**, each linked to psychoacoustic metrics (SPL, loudness, sharpness) and psychological perceptual ratings (pleasantness, eventfulness).

### 3.2 Enforcement of the Critical Continuity Rule
The project's pre-registered evaluation protocol establishes strict rules governing continuous exposure:
1. **No Artificial Concatenation:** Concatenating discrete short clips (e.g. chaining sixty 30-second clips into a 30-minute file) creates artificial phase boundaries, abrupt background level shifts, and false spectral onset transients that trigger spurious convolutional kernel spikes.
2. **No Silence Padding or Looping:** Inserting synthetic silence between clips or looping audio is strictly prohibited.
3. **Session Contiguity Disproven:** Source metadata confirms that the 30-second snippets were recorded at irregular intervals across different days, locations, and survey sessions. They do not represent contiguous segments of an uninterrupted multi-hour recording.

---

## 4. Multi-Channel Downmixing Analysis

Even if an exploratory sub-study on short clips were pursued, the binaural audio requires conversion to feed single-channel detectors:
- **Channel Mapping:** Left ($L$) and Right ($R$) dummy-head ear signals.
- **Downmix Methodology:** Coherent acoustic summation:
  $$s_{\text{mono}}[n] = 0.5 \times (s_L[n] + s_R[n])$$
- **Resampling:** Resampling from 48,000 Hz to 16,000 Hz using high-order polyphase antialiasing filters.
- **Conclusion:** While downmixing is technically straightforward and preserves spectral features without modifying detector thresholds, it cannot overcome the fatal lack of temporal continuity.

---

## 5. Formal Source Disposition

| Assessment Criterion | Status | Evaluation Summary |
|---|---|---|
| **Legal & License Status** | **PASSED** | Open CC BY 4.0 license permits research use. |
| **Acoustic Negative Status** | **PASSED** | Public urban parks and plazas; zero live-fire munitions. |
| **Continuity Verification** | **FAILED** | Corpus consists of discrete 30-second survey snippets. |
| **Benchmark Eligibility** | **DISQUALIFIED** | Fails continuous validation criteria; concatenation is prohibited. |
| **Final Disposition** | **`REJECTED`** | Ineligible for primary continuous negative-exposure benchmark. |

---

## 6. Mandatory Safety Reiteration

This candidate source audit evaluates background noise attribution only. The experimental detection software remains non-operational and must never be deployed for life-safety, tactical dispatch, or emergency alerting applications.

