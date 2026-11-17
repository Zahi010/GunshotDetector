# PHASE 20 — DATASET SOURCE VERIFICATION & FORENSIC AUDIT

> [!CAUTION]
> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.**
> This experimental acoustic machine-learning system is not certified and must never be used for autonomous emergency dispatch, police response, active-shooter alerting, automated evacuation, or critical physical security.
> Use legally obtained recorded audio and safe playback only. No live-fire testing or hazardous acoustic experiments.

---

## 1. Source Repository & Provenance Record

The positive continuous recordings evaluated in Phase 19 were sourced from the official public research repository maintained by ShotSpotter Inc.:

- **Repository Title:** ShotSpotter Sample Live Fire Test Data
- **Repository URL:** `https://github.com/ShotSpotter/research.accuracy-of-gunshot-location`
- **Verified Commit SHA:** `b0dc2840cf61c3c532756c01d49f636725c2b9ff`
- **Commit Date:** March 10, 2025, 20:36:38 UTC
- **Supporting Publication:** ShotSpotter Tech Note 098, *"Precision and accuracy of acoustic gunshot location in an urban environment"*
- **Author / Scientific Contact:** Dr. Robert Calhoun, ShotSpotter Inc. (`rcalhoun@shotspotter.com`)
- **Dataset License:** Creative Commons Attribution 4.0 International (CC BY 4.0)

---

## 2. Experimental Context: Controlled Validation vs. Naturally Occurring Gunfire

A central objective of Phase 20 is to resolve a critical semantic and scientific distinction in the project's data narrative:

> [!IMPORTANT]
> **Controlled Urban Live-Fire System Validation is NOT Naturally Occurring Urban Gunfire.**
> The ShotSpotter Pittsburgh dataset was created through an official, pre-scheduled, highly structured live-fire calibration campaign conducted on December 18–19, 2018, by sworn officers of the Pittsburgh Bureau of Police to validate sensor density prior to production deployment.
> Officers fired at predetermined surveyed locations, using specific handguns, with predetermined round counts and scheduled firing sequences.

While the acoustic propagation medium is an authentic municipal urban environment (complete with real street traffic, building reflections, and environmental noise), the events are **controlled live-fire tests**, not opportunistic captures of spontaneous, natural urban gunfire incidents. The project must strictly maintain this scientific distinction.

---

## 3. Architecture of the Original Pittsburgh DQV 2018 Dataset

The complete Pittsburgh dataset encompasses:
- **Campaign Identifier:** `PittsburghPA_DQV_2018-12-18`
- **Total Firing Positions:** **9 firing positions (`FP1` through `FP9`)**
- **Tests per Position:** Exactly 18 tests per firing position
- **Total Campaign Tests:** $9 \times 18 = 162$ discrete tests
- **Total Physical Rounds Fired in Campaign:** $162 \text{ tests} \times \text{weighted rounds} = 324 \text{ rounds}$

### 3.1. Standardized 18-Test Firing Protocol per Position
At every firing position, police officers executed an identical, standardized protocol:

| Test Sequence | Firearm Category | Round Pattern | Ground-Truth Rounds | Cumulative Rounds |
| :---: | :--- | :--- | :---: | :---: |
| Tests 01, 02, 03 | .45 ACP Automatic Handgun | 3-round rapid burst | 3 rounds each | 9 rounds |
| Tests 04, 05, 06 | .45 ACP Automatic Handgun | Single shot | 1 round each | 3 rounds |
| Tests 07, 08, 09 | .40 S&W Automatic Handgun | 3-round rapid burst | 3 rounds each | 9 rounds |
| Tests 10, 11, 12 | .40 S&W Automatic Handgun | Single shot | 1 round each | 3 rounds |
| Tests 13, 14, 15 | 9x19mm Automatic Handgun | 3-round rapid burst | 3 rounds each | 9 rounds |
| Tests 16, 17, 18 | 9x19mm Automatic Handgun | Single shot | 1 round each | 3 rounds |
| **Total per FP** | **3 Handgun Types** | **9 Bursts + 9 Singles** | **36 rounds** | **36 rounds** |

### 3.2. Sequential Numbering vs. Firing Position Mapping
The tests in the repository are numbered sequentially (1 to 162), reflecting the chronological sequence in which the police mobile unit traversed the city:

| Chronological Directory | Test ID Range | Firing Position | Local Testing Window (UTC) |
| :---: | :---: | :---: | :---: |
| `data/PittsburghPA_DQV_2018-12-18/FP1` | `test_001` to `test_018` | Firing Position 1 | 2018-12-19 00:49 to 01:09 UTC |
| `data/PittsburghPA_DQV_2018-12-18/FP2` | `test_019` to `test_036` | Firing Position 2 | 2018-12-19 01:29 to 01:52 UTC |
| `data/PittsburghPA_DQV_2018-12-18/FP3` | `test_037` to `test_054` | Firing Position 3 | 2018-12-19 02:12 to 02:29 UTC |
| `data/PittsburghPA_DQV_2018-12-18/FP4` | `test_055` to `test_072` | Firing Position 4 | 2018-12-19 02:38 to 03:00 UTC |
| `data/PittsburghPA_DQV_2018-12-18/FP8` | `test_073` to `test_090` | Firing Position 8 | 2018-12-19 03:19 to 03:38 UTC |
| `data/PittsburghPA_DQV_2018-12-18/FP7` | `test_091` to `test_108` | Firing Position 7 | 2018-12-19 03:59 to 04:19 UTC |
| `data/PittsburghPA_DQV_2018-12-18/FP6` | `test_109` to `test_126` | Firing Position 6 | 2018-12-19 04:39 to 04:59 UTC |
| `data/PittsburghPA_DQV_2018-12-18/FP5` | `test_127` to `test_144` | Firing Position 5 | 2018-12-19 05:23 to 05:43 UTC |
| `data/PittsburghPA_DQV_2018-12-18/FP9` | `test_145` to `test_162` | Firing Position 9 | 2018-12-19 06:05 to 06:27 UTC |

> [!NOTE]
> This chronological audit explains why FP5 contains tests numbered 127 through 144 rather than tests 73 through 90: the testing team routed from FP4 to FP8, FP7, and FP6 before arriving at FP5.

---

## 4. Phase 19 Selection Audit: The 20 Selected Tests

Phase 19 selected **20 tests** across 5 distinct firing positions (`FP1`, `FP2`, `FP3`, `FP4`, and `FP5`). 
For each firing position, Phase 19 sampled exactly 4 tests:
- 1st test (.45 ACP 3-round burst, 3 rounds)
- 4th test (.45 ACP single shot, 1 round)
- 7th test (.40 S&W 3-round burst, 3 rounds)
- 13th test (9mm 3-round burst, 3 rounds)

This sampling yielded exactly **10 physical rounds per firing position** across 5 firing positions:
$$5 \times 10 = 50 \text{ physical gunshot events}$$

Each selected test corresponds to an original, uncompressed, 12 kHz, 16-bit mono PCM sensor WAV file (`240,044` bytes = 120,000 audio samples = 10.000 seconds).

---

## 5. Sensor Audio & Coordinate Anonymization Audit

### 5.1. Audio File Specifications
- **Format:** Uncompressed Microsoft WAV (PCM 16-bit little-endian)
- **Native Sampling Rate:** 12,000 Hz
- **Channels:** 1 (Mono)
- **Duration:** 10.000 seconds (120,000 samples)
- **Sensor Hardware:** Municipal pole-mounted ShotSpotter acoustic sensor units with GPS receivers.

### 5.2. Coordinate Anonymization Mechanics
To prevent public disclosure of precise police sensor pole coordinates while enabling scientific multilateration research, ShotSpotter applied Cartesian coordinate anonymization:
- Latitude, longitude, and elevation coordinates were transformed into local Cartesian $(x, y, z)$ coordinates in meters.
- **Critical Caveat:** As explicitly documented in the ShotSpotter README:
  $$\text{"Each firing position has a different arbitrary origin."}$$
- Consequently, sensor coordinates reported in FP1 cannot be compared directly to sensor coordinates reported in FP2, FP3, FP4, or FP5 by simple Euclidean subtraction, because each firing position possesses an independent, unaligned local coordinate origin.

Full test-by-test inventory data is permanently recorded in [`reports/phase20_original_dataset_inventory.csv`](file:///e:/gunshot/gunshot/reports/phase20_original_dataset_inventory.csv).

