# Phase 22: Prospective Independent Validation Protocol & Study Design

> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY..**  
> *This experimental acoustic machine-learning system is not certified and must never be used for autonomous emergency dispatch, police response, active-shooter alerting, automated evacuation, or critical physical security.*  
> *Use legally obtained recordings and safe playback only. No live-fire testing or hazardous acoustic experiments.*

---

## 1. Executive Summary

Phase 20 and Phase 21 established that evaluating gunshot detectors on a single municipal live-fire dataset (ShotSpotter Pittsburgh PA DQV 2018) provides valuable initial acoustic validation, but **cannot substantiate claims of geographic, environmental, or multi-city generalization**.

This protocol defines the formal, preregistered prospective study design required to test candidate acoustic gunshot detection models on genuinely independent external data.

### Fundamental Study Design Principles:
1. **Multi-Campaign Requirement:** Prospective evaluation requires a minimum of **three independent metropolitan recording campaigns** conducted under distinct operational authorities, seasons, and urban topographies.
2. **Separation of Statistical Levels:** Firing positions, recordings, and gunshot rounds must never be conflated with campaigns. A dataset with 100 rounds from one campaign has $N_{\text{campaign}} = 1$.
3. **Lawful Sourcing Only:** All evaluation audio must be legally obtained from open research releases, municipal public records, or authorized partner archives. **Zero live-fire testing or hazardous field experiments are permitted.**
4. **Primary and Secondary Endpoint Decoupling:** Stream-level incident detection and negative-audio false-alert rates serve as primary operational endpoints; round-level recall and burst counting serve as secondary diagnostic endpoints.

---

## 2. Evaluation Hierarchy and Unit of Independence

To prevent pseudoreplication and false claims of sample size, the validation protocol defines a strict seven-level statistical hierarchy:

```
Level 1: Independent Municipal Campaign (N ≥ 3 required for multi-city claims)
  └── Level 2: Firing Position / Spatial Location (Street geometry & setbacks)
        └── Level 3: Recording Session (Operational test window & weather)
              └── Level 4: Sensor Stream / Recording (Continuous unbroken file)
                    └── Level 5: Firing Sequence / Incident (Single shot vs. burst)
                          └── Level 6: Physical Ballistic Round (Ground-truth impulse)
                                └── Level 7: Detector Alert (System output notification)
```

### Hierarchy Rules:
- **Campaign ($N_{\text{camp}}$):** Represents the top-level independent experimental unit. Each campaign must originate from an independent geographic region, separate organizational sponsor, and independent sensor deployment.
- **Position ($N_{\text{pos}}$):** Distinct physical coordinates within a campaign. Multiple positions in one city are **nested spatial clusters**, not independent campaigns.
- **Recording Stream ($N_{\text{stream}}$):** Continuous unbroken audio file. The primary unit for false-alarm exposure and incident detection.
- **Physical Event ($N_{\text{round}}$):** Individual ballistic discharge. Multiple rounds within a burst are **temporally clustered** and share propagation multipath.

---

## 3. Independent Campaign Acquisition Targets

To demonstrate generalizability beyond Pittsburgh, prospective validation targets three distinct operational environments:

| Target Campaign ID | Target Environment | Urban Geometry & Facade Acoustic Profile | Target Standoff Distances | Environmental & Climate Target | Target Sensor Hardware |
| :--- | :--- | :--- | :---: | :--- | :--- |
| **CAMPAIGN-01 (Baseline)** | Mid-Atlantic Humid Metro (e.g., Pittsburgh PA DQV) | High-density brick and stone masonry street canyons, deep reverberant ringing | $80\text{ m}$ to $300\text{ m}$ | Freezing winter ($0^\circ\text{C}$ to $3^\circ\text{C}$), high relative humidity | Commercial rooftop sensor nodes (12 kHz native) |
| **CAMPAIGN-02 (Arid Grid)** | Arid Southwestern Metro (e.g., Phoenix / Tucson / Las Vegas) | Low-density concrete block, stucco facades, wide multi-lane boulevards, minimal foliage | $100\text{ m}$ to $450\text{ m}$ | Extreme dry heat ($30^\circ\text{C}$ to $42^\circ\text{C}$), strong thermal updrafts | Pole-mounted public safety microphone arrays (16 kHz) |
| **CAMPAIGN-03 (Coastal Dense)** | Dense Coastal Metropolis (e.g., Chicago / Boston / Baltimore) | High-rise steel, glass, and granite canyons with heavy urban transit and HVAC background | $50\text{ m}$ to $250\text{ m}$ | Maritime temperate, wind shear ($15\text{–}30\text{ km/h}$), wet street reflection | Mixed municipal acoustic monitoring networks |

> [!IMPORTANT]
> **Planning Target vs. Statistical Power:** Achieving evaluation across three campaigns is a **minimum exploratory planning target**, not a proof of unconstrained universal generalization. Claims of generalizability must remain strictly bounded by the evaluated topographies and calibers.

---

## 4. Source Provenance and Anti-Contamination Protocol

Every prospective audio file must undergo mandatory provenance ingestion governed by [phase22_dataset_provenance_schema.json](file:///e:/gunshot/gunshot/reports/phase22_dataset_provenance_schema.json).

### Ingestion Validation Gates:
1. **Legal and License Clearance:**
   - Permitted licenses: `CC_BY_4.0`, `CC0`, `ODC_BY_1.0`, or formally executed `ACADEMIC_RESEARCH_USE_AGREEMENT`.
   - Explicit confirmation of research use, commercial non-infringement, and public release authorization.
2. **Cryptographic Deduplication:**
   - Pre-computation of SHA-256 hash.
   - Rejection of any file matching previously evaluated test or training sets (UrbanSound8K, ESC-50, Mitchell 2015, ShotSpotter 2018).
3. **Acoustic Similarity Fingerprinting:**
   - Chromaprint / acoustic fingerprint comparison to detect cropped, resampled, or re-encoded duplicates of known files.
   - Any file sharing $> 90\%$ acoustic similarity with prior training sets is flagged as `CONTAMINATED_HISTORICAL_DERIVATIVE` and excluded.
4. **Independent Ground-Truth Verification:**
   - Ground-truth timestamps must be verified via independent documentation (e.g., laser surveyed curb marks, video cross-referencing, multi-channel microsecond arrival logs).
   - Recordings with self-labeled or synthetic labels are segregated into exploratory benchmarks.

---

## 5. Primary and Secondary Endpoints

### 5.1 Primary Endpoints (Prespecified)
1. **Recording-Level Incident Detection Recall:**
   $$\text{Recall}_{\text{incident}} = \frac{\text{Detected Incidents}}{\text{Total Firing Incidents / Streams}}$$
   Evaluated at the stream level ($N_{\text{stream}}$), robust against intra-burst cooldown artifacts.
2. **Eligible-Hour False-Alert Rate (FAR):**
   $$\text{FAR} = \frac{\text{Observed False Alerts}}{\text{Eligible Quiescent Background Exposure Hours}}$$
   Evaluated over long-duration continuous negative audio with exact Garwood Poisson upper confidence bounds.
3. **Cross-Campaign Consistency Metric:**
   $$\Delta_{\text{campaign}} = \max_j(\text{Recall}_j) - \min_j(\text{Recall}_j)$$
   Evaluates whether detector performance remains stable across the three campaigns ($\Delta_{\text{campaign}} \le 15.0\%$).

### 5.2 Secondary Endpoints (Diagnostic Only)
1. **Strict Physical-Round Recall:** Fraction of individual physical rounds matched by independent alerts under strict 1-to-1 matching.
2. **Burst Detection Probability:** Probability of detecting at least one round in multi-shot bursts.
3. **Time-to-First-Alert (TTFA):** Latency from the first ballistic wavefront arrival to detector alert dispatch.
4. **Alert Duplication Index:** Number of redundant alerts generated within $3.0\text{ seconds}$ of an initial trigger.

---
*Report certified under Phase 22 Forensic Protocol.*
