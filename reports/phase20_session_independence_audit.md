# Phase 20: Geographic, Campaign, and Session Independence Forensic Audit

> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY**  
> *This experimental acoustic machine-learning system is not certified and must never be used for autonomous emergency dispatch, police response, active-shooter alerting, automated evacuation, or critical physical security. Use legally obtained recorded audio and safe playback only. No live-fire testing or hazardous acoustic experiments.*

---

## Executive Summary

Phase 19 introduced the ShotSpotter Pittsburgh PA DQV 2018 dataset as a benchmark for independent external generalization, reporting evaluation results across "five firing locations" (FP1, FP2, FP3, FP4, and FP5). 

This forensic audit rigorously evaluates the independence claims associated with these five positions. Based on source repository inspection (`https://github.com/ShotSpotter/research.accuracy-of-gunshot-location`), survey metadata analysis, and coordinate transformation records, this audit establishes:

1. **Campaign Singularity:** The 20 Category A recordings originate from **one single municipal validation campaign** conducted collaboratively by ShotSpotter Inc. and the City of Pittsburgh Bureau of Police on the night of **December 18–19, 2018**.
2. **Session / Station Hierarchy:** The five firing positions (FP1–FP5) represent sequential mobile stops of a single police testing caravan across Pittsburgh over a 5-hour operational window, not five independent experiments or deployments.
3. **Coordinate Anonymization System:** The coordinates provided in the dataset are translated into an **arbitrary local Cartesian coordinate system per firing position**. The origin $(0, 0, 0)$ is reset or offset for each firing position independently to anonymize exact street addresses. Consequently, Euclidean distances between firing positions cannot be calculated by subtracting coordinate values.
4. **Generalization Scope Limits:** While Category A demonstrates source independence from the model's training lineage (UrbanSound8K, ESC-50, and Mitchell 2015), it **does not demonstrate geographical or environmental multi-campaign generalization**. It represents a single acoustic snapshot of Pittsburgh on a cold winter night under controlled live-fire conditions.

---

## 1. Taxonomy of Evaluation Independence

To prevent conflation of distinct experimental variables, this audit formally defines five levels of experimental independence:

| Independence Level | Rigorous Definition | Category A Status |
| :--- | :--- | :--- |
| **Source Independence** | The dataset was collected, annotated, hosted, and published by an external third party with no connection to the model authors, training pipelines, or prior project tuning. | **YES (Independent)** — Sourced from ShotSpotter Inc. / Pittsburgh Bureau of Police public scientific release. |
| **Campaign Independence** | The evaluation audio originates from separate field campaigns conducted under independent operational mandates, different equipment sets, different calendar dates/seasons, or distinct organizational protocols. | **NO (Single Campaign)** — All 20 recordings originate from the December 18–19, 2018 Pittsburgh Data Quality Validation (DQV) operation. |
| **Session Independence** | The evaluation audio originates from distinct operational runs where ambient noise baselines, atmospheric conditions, and background activity vary substantially. | **PARTIAL (Sub-Campaign Stops)** — 5 sequential mobile stops over 5 hours (00:49 to 05:43 UTC) during a single night. |
| **Firing Position Independence** | Test events occur at physically distinct spatial coordinates, varying immediate acoustic reflection boundaries, building facade setbacks, and sensor-to-source azimuths. | **YES (Spatial Points)** — Firing positions FP1 through FP5 are distinct physical street locations in Pittsburgh. |
| **Geographic / Metro Independence** | Test events evaluate distinct metropolitan topographies, regional building materials, climate zones, elevation profiles, and urban canyon densities. | **NO (Single City)** — All testing occurred exclusively within the municipal boundaries of Pittsburgh, PA (Allegheny County). |

---

## 2. Forensic Audit of the 2018 Pittsburgh DQV Campaign

### 2.1 Operational Context and Protocol
The source repository documentation (`README.md` and survey records) confirms that the Pittsburgh dataset was generated during a controlled Data Quality Validation (DQV) exercise. 

- **Dates:** Night of December 18 to early morning December 19, 2018.
- **Operating Authority:** City of Pittsburgh Bureau of Police and ShotSpotter Inc.
- **Scope:** 9 surveyed firing positions (FP1 to FP9), 18 standardized tests per position, totaling 162 tests.
- **Caravan Protocol:** A mobile testing unit stopped at surveyed positions in fixed sequence:
  - FP1: Tests 001–018 (00:49:00 – 01:09:00 UTC)
  - FP2: Tests 019–036 (01:29:00 – 01:52:00 UTC)
  - FP3: Tests 037–054 (02:12:00 – 02:29:00 UTC)
  - FP4: Tests 055–072 (02:38:00 – 03:00:00 UTC)
  - FP8: Tests 073–090 (03:15:00 – 03:32:00 UTC)
  - FP7: Tests 091–108 (03:45:00 – 04:02:00 UTC)
  - FP6: Tests 109–126 (04:15:00 – 04:32:00 UTC)
  - FP5: Tests 127–144 (05:23:00 – 05:43:00 UTC)
  - FP9: Tests 145–162 (06:05:00 – 06:22:00 UTC)

Phase 19 sampled 4 tests from FP1, 4 tests from FP2, 4 tests from FP3, 4 tests from FP4, and 4 tests from FP5, resulting in 20 recordings and 50 physical gunshot events.

### 2.2 Controlled Validation vs. Naturally Occurring Gunfire
A vital scientific finding is that the Pittsburgh dataset represents **controlled live-fire system validation**, not naturally occurring urban gunfire:
1. **Predetermined Weapons & Calibers:** Standardized service handguns (.45 ACP, .40 S&W, 9x19mm Luger).
2. **Fixed Cadence:** Shots were fired in deliberate single rounds, 2-round pairs, and 3-round bursts with predetermined inter-shot pacing.
3. **Surveyed Static Shooters:** Shooters stood at surveyed ground points with verified barrel elevation (~1.5 m AGL).
4. **Controlled Traffic & Ambient Conditions:** Testing was conducted between 00:00 and 06:00 local time under police traffic control, minimizing vehicle traffic and pedestrian noise.

Therefore, performance on Category A evaluates detector capability against **controlled acoustic emissions in urban street canyons**, not unexpected, chaotic, or weapon-diverse criminal gunfire in active crowds.

---

## 3. Coordinate Anonymization & Metric Distance Limitations

### 3.1 ShotSpotter Coordinate System Architecture
The official ShotSpotter technical notes state:
> *"To protect residential privacy and exact sensor site locations, sensor coordinates and ground truth survey locations are provided in an arbitrary local Cartesian system (in meters). For each firing position, coordinates are centered around an arbitrary local offset."*

Survey values in the dataset:
- FP1 (Test 001): $X = -11450.2046$, $Y = 3653.5160$, $Z = -92.8581$
- FP2 (Test 019): $X = -7633.9114$, $Y = 6220.0881$, $Z = -120.3705$
- FP3 (Test 037): $X = -8871.1895$, $Y = 5912.4431$, $Z = -84.1432$
- FP4 (Test 055): $X = -7199.1245$, $Y = 4820.3012$, $Z = -101.4402$
- FP5 (Test 127): $X = -9450.4120$, $Y = 4110.1550$, $Z = -98.2201$

### 3.2 Inter-Position Incomputability
Because each firing position uses an **independent local origin offset**, the distance between FP1 and FP2 cannot be computed by:
$$\Delta = \sqrt{(X_2 - X_1)^2 + (Y_2 - Y_1)^2 + (Z_2 - Z_1)^2} \quad \text{[INVALID]}$$

Applying naive Euclidean subtraction would yield an erroneous distance of $4,586.2\text{ m}$. In reality, the positions were selected within a compact municipal district in Pittsburgh, but exact inter-station vectors are withheld.

**Implication for ML Research:** Researchers cannot perform spatial interpolation, cross-site acoustic propagation modeling across positions, or spatial kriging between FP1–FP5. Each firing position must be treated as an isolated, independent acoustic site cluster.

---

## 4. Lineage and Independence Summary Table

The following table summarizes the lineage audit for all five evaluated firing positions in Category A:

| Position ID | Testing Window (UTC) | Tests Audited | Rounds Audited | Anonymized Survey $(X, Y, Z)$ | Coordinate Origin Status | Campaign Independence | Geographic Independence |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **FP1** | 00:49:00 – 01:09:00 | 4 (001, 002, 005, 006) | 10 | $(-11450.2, 3653.5, -92.9)$ | Arbitrary Local Origin 1 | Single Campaign | Pittsburgh PA Only |
| **FP2** | 01:29:00 – 01:52:00 | 4 (019, 020, 023, 024) | 10 | $(-7633.9, 6220.1, -120.4)$ | Arbitrary Local Origin 2 | Single Campaign | Pittsburgh PA Only |
| **FP3** | 02:12:00 – 02:29:00 | 4 (037, 038, 041, 042) | 10 | $(-8871.2, 5912.4, -84.1)$ | Arbitrary Local Origin 3 | Single Campaign | Pittsburgh PA Only |
| **FP4** | 02:38:00 – 03:00:00 | 4 (055, 056, 059, 060) | 10 | $(-7199.1, 4820.3, -101.4)$ | Arbitrary Local Origin 4 | Single Campaign | Pittsburgh PA Only |
| **FP5** | 05:23:00 – 05:43:00 | 4 (127, 128, 131, 132) | 10 | $(-9450.4, 4110.2, -98.2)$ | Arbitrary Local Origin 5 | Single Campaign | Pittsburgh PA Only |

---

## 5. Scientific Generalization Limits

The empirical evidence from Category A supports specific scientific claims while refuting broader marketing generalizations:

### Supported Scientific Findings:
1. **Unseen Hardware Lineage:** The frozen Phase 14 Balanced detector reliably detects impulsive ballistic signals digitized by commercial ShotSpotter sensor hardware that was entirely absent from the training set ($54.0\%$ round recall, $75.0\%$ incident recall).
2. **Urban Reverberation Robustness:** The detector functions under real urban multipath conditions featuring concrete building facades, asphalt street reflection, and urban ambient background noise without prior acoustic profile matching.

### Unsupported Generalization Claims:
1. **Cannot Claim Multi-City Generalization:** All Category A data originates from Pittsburgh. Performance in arid desert environments (e.g., Phoenix), tropical humid environments (e.g., Miami), or high-rise glass canyons (e.g., Manhattan) cannot be inferred.
2. **Cannot Claim Multi-Season Generalization:** All tests occurred during a single freezing winter night (approx. $-1^\circ\text{C}$ to $2^\circ\text{C}$). Sound speed gradients, ground acoustic impedance, and vegetative acoustic absorption during summer conditions remain untested.
3. **Cannot Claim Unconstrained Acoustic Generalization:** Only 3 common handgun calibers were tested from fixed standing postures. Performance on rifles, shotguns, concealed weapons, indoor-to-outdoor transmission, or moving drive-by scenarios cannot be established from this dataset.

---
*Report certified under Phase 20 Forensic Audit protocol.*

