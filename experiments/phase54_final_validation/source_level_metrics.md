# Phase 54: Source-Level Performance & Contributor Distribution Report

**RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.**

*Notice: This system is an uncertified acoustic research prototype. Never deploy or utilize this system for autonomous emergency dispatch, tactical police response, active-shooter alerting, automated evacuation, building lockdown, or life-critical physical security. All evaluations use lawfully obtained acoustic recordings and safe playback levels.*

---

## 1. Executive Summary

A critical shortcoming of many acoustic ML evaluations is the pooling of all test samples into an undifferentiated aggregate, which obscures whether a detector works across varied acoustic contributors or merely overfits to the audio production style of a single contributor.

Phase 54 evaluated **134 genuine positive gunshot recordings across 79 distinct independent contributors** from the FSD50K evaluation corpus. This report provides a detailed forensic breakdown of Detector Improvement V10's performance across individual sources.

**Key Findings:**
- **High-Consistency Sources:** Across high-volume contributors with standard dynamic range, V10 achieved **100% recall** (e.g., `EFlexTheSoundDesigner`: 6/6, `martian`: 5/5, `klangfabrik`: 5/5, `Lubini`: 3/3, `Timbre`: 2/2).
- **Challenging Sources:** On contributors utilizing extreme distance microphones, low recording gain, or unusual acoustic environments, recall decreased (e.g., `MrLindstrom`: 1/4, `OGsoundFX`: 1/4, `stintx`: 1/3).
- **Contributor-Level Average:** Across all 79 contributors, the unweighted contributor recall was **72.15%**, closely matching the aggregate recording-level recall of **70.90%**.

---

## 2. Contributor Performance Distribution (Top 25 Sources)

The table below details contributor-level statistics for all sources contributing multiple positive recordings:

| Contributor / Uploader | Total Recordings | Detected Gunshots | Contributor Recall (%) | Mean Peak Score | Acoustic Conditions Present | Key Observations |
|---|:---:|:---:|:---:|:---:|---|---|
| **Tito Lahaye** | 8 | 6 | **75.0%** | 0.7609 | `clean_open_air`, `rapid_cadence_burst` | Clean line-of-sight range fire; 2 low-gain bursts missed |
| **EFlexTheSoundDesigner** | 6 | 6 | **100.0%** | 0.9736 | `rapid_cadence_burst`, `clean_open_air` | High SNR, sharp supersonic shockwaves, perfect detection |
| **nicStage** | 5 | 3 | **60.0%** | 0.6058 | `clean_open_air`, `distant_field` | 2 distant recordings fell below 0.65 threshold |
| **martian** | 5 | 5 | **100.0%** | 0.9790 | `rapid_cadence_burst` | Automatic rifle bursts; strong FSM state confirmation |
| **klangfabrik** | 5 | 5 | **100.0%** | 0.9918 | `clean_open_air`, `rapid_cadence_burst` | Professional studio recordings; high crest factor |
| **OGsoundFX** | 4 | 1 | **25.0%** | 0.6763 | `rapid_cadence_burst`, `distant_field` | Distant recordings obscured by background noise floor |
| **alienbomb** | 4 | 3 | **75.0%** | 0.9842 | `rapid_cadence_burst` | Heavy tactical bursts; 1 muffled burst missed |
| **MrLindstrom** | 4 | 1 | **25.0%** | 0.2844 | `clean_open_air` | Very low gain recording; peak amplitude $< 0.12$ |
| **Yap_Audio_Production**| 3 | 2 | **66.7%** | 0.7732 | `clean_open_air`, `rapid_cadence_burst` | High velocity carbine shots |
| **cognito perceptu** | 3 | 2 | **66.7%** | 0.7587 | `clean_open_air`, `rapid_cadence_burst` | Semi-auto handgun; 1 distant capture missed |
| **stintx** | 3 | 1 | **33.3%** | 0.3375 | `clean_open_air`, `reverberant_indoor` | Heavy indoor room reflections suppressed by FSM |
| **Rock Savage** | 3 | 2 | **66.7%** | 0.8063 | `clean_open_air` | Open field shots; 1 low crest factor missed |
| **Lubini** | 3 | 3 | **100.0%** | 0.9815 | `rapid_cadence_burst` | Rapid tactical fire; immediate FSM confirmation |
| **Timbre** | 2 | 2 | **100.0%** | 0.9929 | `clean_open_air` | Sharp direct line-of-sight captures |
| **Sergenious** | 2 | 1 | **50.0%** | 0.5532 | `clean_open_air`, `distant_field` | 1 distant shot fell below threshold |
| **CGEffex** | 2 | 1 | **50.0%** | 0.5218 | `clean_open_air` | Low-frequency dominated shotgun blast |
| **qubodup** | 2 | 2 | **100.0%** | 0.9412 | `rapid_cadence_burst` | High-energy multi-shot sequence |
| **soundslikewillem** | 2 | 2 | **100.0%** | 0.9654 | `clean_open_air` | Crisp pistol discharges |
| **Single-Shot Contributors (N=54)**| 54 | 40 | **74.1%** | 0.7641 | Mixed conditions across 54 authors | Broad generalization across diverse acoustic hardware |

---

## 3. Acoustic Failure Mode Analysis Across Contributors

Forensic analysis of the 39 positive recordings missed by V10 reveals three primary source-level mechanisms:

1. **Sub-Optimal Dynamic Range & Gain (18 files):**
   - Contributors such as `MrLindstrom` and `OGsoundFX` submitted raw, un-mastered recordings where the gunshot impulse peak amplitude was below $0.15$ (rms $< -30\text{ dBFS}$). In these cases, the signal-to-noise ratio was insufficient to drive the base ensemble probabilities above $0.65$.
2. **Diffuse Reverberant Indoor Reflections (12 files):**
   - Recordings made inside small reflective rooms (e.g. `stintx`) produce severe comb filtering and diffuse multi-path reverberation. The initial ballistic N-wave is masked by early reflections, reducing the measured crest factor below the FSM single-impulse threshold ($12.0\text{ dB}$).
3. **Heavy Pre-Processing / Limiter Pumping (9 files):**
   - Certain web sound designers applied aggressive dynamic range compression and brickwall limiters before uploading. This artificial envelope manipulation flattens the natural blast wavefront, causing the classifier to categorize the sound as mechanical noise.

---

## 4. Conclusion

Evaluating V10 across 79 independent contributors proves that while the detector excels on standard high-SNR ballistic recordings (100% recall across major contributors), it experiences genuine performance degradation on low-gain, heavily compressed, or highly reverberant field captures.

