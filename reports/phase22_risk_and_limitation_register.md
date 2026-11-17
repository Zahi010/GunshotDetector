# Acoustic Gunshot Detection Risk & Limitation Register
## Comprehensive Catalog of Physical, Algorithmic, Environmental, and Operational Failure Modes

**Document ID:** `REPORT-PHASE22-RISK-001`  
**Version:** 1.0  
**Date:** November 2026  
**Status:** ACTIVE RISK REGISTER  

---

### MANDATORY SAFETY DESIGNATION
> [!CAUTION]
> **RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.**  
> This experimental acoustic machine-learning system is uncertified and must never be deployed for autonomous emergency dispatch, tactical police response, active-shooter alerting, automated lockdown/evacuation, or life-critical physical security. Use legally obtained recordings and safe audio playback only. Live-fire testing and hazardous acoustic experiments are strictly prohibited.

---

## 1. Scope & Risk Taxonomy

Acoustic gunshot detection is governed by complex acoustic propagation physics, severe environmental noise distributions, and stringent operational requirements. This register classifies and tracks all identified risks, failure modes, and technical limitations across five core domains:

1. **Acoustic Physics & Propagation Limitations (PHYS)**
2. **Signal Processing & Algorithmic Failure Modes (ALGO)**
3. **Sensor Hardware, Transducer & Network Drift (HARD)**
4. **Statistical, Data Lineage & Evaluation Biases (STAT)**
5. **Operational & Life-Safety Hazards (SAFE)**

---

## 2. Risk Matrix & Severity Definitions

| Risk ID | Domain | Hazard Description | Pre-Mitigation Severity | Post-Mitigation Residual Risk | Mitigation Strategy & Protocol Status |
|---|---|---|---|---|---|
| **PHYS-01** | Acoustic Physics | **Non-Line-of-Sight (NLOS) Diffraction & Acoustic Shadowing:** Buildings, terrain, and barriers attenuate high frequencies ($>2\text{ kHz}$) and destroy shockwave N-waves, causing acoustic smearing and missed detections at long standoff. | **CRITICAL** | **HIGH** | Explicitly modeled in Phase 22 validation protocol via standoff distance binning ($50\text{ m}$ to $400\text{ m}$). Cannot be completely mitigated by single-channel ML without spatial array processing. |
| **PHYS-02** | Acoustic Physics | **Atmospheric Inversion & Wind Gradient Refraction:** Temperature inversions and high downwind gradients curve sound rays, causing unpredictable multi-second arrival delays, severe amplitude fluctuations, or complete shadow zones. | **HIGH** | **MEDIUM** | Ingestion checklist requires documenting atmospheric and weather conditions; validation stratified across windy and calm days. |
| **ALGO-01** | Algorithmic | **Refractory Cooldown Burst Suppression:** Internal 2.0-second alert dead time blinds the detector to closely spaced successive rounds in automatic or rapid-fire bursts, causing undercounting. | **HIGH** | **LOW (Forensic)** | Phase 22 forensic classification categorized all 50 rounds into 5 mutually exclusive states. Future architecture designs must separate event detection from multi-round burst counting. |
| **ALGO-02** | Algorithmic | **Impulsive Noise False Positives (Dog Barks, Fireworks, Tailgates):** Acoustic distractors with high crest factors and fast rise times mimic muzzle blast profiles, triggering false alarms. | **CRITICAL** | **MEDIUM** | Phase 14 multi-profile thresholds and Phase 17 harmonic/spectral suppression filter dog barks. 100-hour continuous negative validation protocol measures empirical operational FAR. |
| **HARD-01** | Hardware Drift | **Microphone Transducer Degradation & Acoustic Enclosure Clogging:** Outdoor environmental exposure (rain, dust, insect nesting in wind grills) alters transducer frequency response and attenuates high frequencies by $>12\text{ dB}$. | **HIGH** | **HIGH** | Protocol specifies baseline testing across multiple sensor hardware types; long-term hardware health monitoring required prior to any physical edge deployment. |
| **HARD-02** | Hardware Drift | **Analog Front-End Preamplifier Clipping:** High-SPL muzzle blast transients close to the microphone ($<50\text{ m}$, $>140\text{ dB SPL}$) drive standard electret/MEMS preamplifiers into hard saturation, creating severe harmonic distortion and flat-topping. | **HIGH** | **MEDIUM** | Digital clipping detection filter integrated in feature preprocessing pipeline; clips flagged during data ingestion. |
| **STAT-01** | Statistics | **Pseudo-Replication & Cluster Over-Confidence:** Treating multiple rounds in a rapid burst or multiple sensor channels in a single campaign as independent samples inflates degrees of freedom and creates spurious statistical significance. | **CRITICAL** | **LOW** | Phase 22 preregistered 7-level evaluation hierarchy and cluster-aware statistical analysis plan (McNemar, Wilcoxon, Holm-Bonferroni, Newcombe paired score CIs). |
| **STAT-02** | Statistics | **Synthetic Concatenation Boundary Artifacts:** Splicing short audio clips creates sharp unphysical sample transitions that trigger false alerts (as discovered in Phase 15 ESC-50 benchmark). | **HIGH** | **CONTROLLED** | Strictly prohibited in Phase 22; continuous negative benchmarks must consist of unbroken natural audio streams $\ge 60\text{ minutes}$. |
| **SAFE-01** | Life Safety | **Unauthorized Deployment in Life-Safety Dispatch:** Erroneous assumption by third parties that an experimental research prototype is suitable for automated emergency dispatch, active-shooter notification, or lockdown. | **FATAL** | **GOVERNED** | Mandatory prominent safety banners on all software artifacts, documentation, and user interfaces. Explicit legal disclaimers of liability and prohibition of life-safety use. |
| **SAFE-02** | Operational | **Alert Fatigue & Resource Exhaustion:** Even an idealized false alert rate of 0.03 alerts/channel-hour generates 720 false calls per day across a 1,000-sensor metropolitan array, overwhelming emergency services. | **CRITICAL** | **GOVERNED** | Model promotion criteria mandate stringent Poisson bounds and recording-level validation. Prototype strictly isolated from operational CAD systems. |

---

## 3. Deep-Dive on Core Physical & Algorithmic Failure Modes

### 3.1 The Burst-Cooldown Trade-off
The empirical findings from Phase 22 forensics establish:
- A $2.0\text{-second}$ refractory cooldown is essential to prevent a single physical gunshot with multi-path reverberation from triggering 3 to 5 separate duplicate alerts.
- However, when a firearm discharges in semi-automatic or fully automatic mode (cadence $0.15\text{ to }0.40\text{ seconds}$ per round), subsequent rounds fall directly into the refractory interval or ongoing alert window.
- **Audited Outcome:** 5 rounds in Category A were merged into active alerts, and 2 rounds were suppressed by cooldown dead time. A detector optimizing for round counting will suffer severe reverberation false duplicates; a detector optimizing for incident alerting will undercount rapid rounds.

### 3.2 Non-Line-of-Sight (NLOS) Propagation in Urban Canyons
When sound propagates around a building corner:
- The direct acoustic shockwave (conical Mach wave) does not diffract efficiently and is lost.
- The muzzle blast diffracts over building edges, attenuating frequencies above $1.5\text{ kHz}$ by 15–25 dB.
- The resulting acoustic signature at the sensor resembles a generic low-frequency thump or industrial rumble, explaining why rounds in `test_049` and `test_127` failed to trigger detections across all tested models.

---

## 4. Governance Action Plan for Residual Risks

1. **Continuous Documentation Updates:** This risk register must be re-evaluated and versioned at the conclusion of every research phase.
2. **Zero-Trust Code Auditing:** All analysis scripts must execute automated unit tests verifying that safety checks, hash freezes, and data constraints are actively enforced before generating reports.

---

*Authored by Principal Acoustic ML Research Engineer & Systems Safety Auditor.*  
*Antigravity Gunshot Detection Research Consortium — Phase 22.*

