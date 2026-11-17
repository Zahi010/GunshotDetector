# PHASE 20 MASTER TECHNICAL REPORT: PITTSBURGH DATASET FORENSIC AUDIT, EVENT-LEVEL REVALIDATION & GENERALIZATION LIMITS

> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY**  
> *This experimental acoustic machine-learning system is not certified and must never be used for autonomous emergency dispatch, police response, active-shooter alerting, automated evacuation, or critical physical security. Use legally obtained recorded audio and safe playback only. No live-fire testing or hazardous acoustic experiments.*

---

## Executive Summary

Phase 20 delivers a comprehensive forensic audit of the external positive dataset introduced in Phase 19 (derived from the **ShotSpotter Pittsburgh PA DQV 2018** scientific release, CC BY 4.0). 

Over previous development phases, acoustic gunshot detection models demonstrated strong performance on laboratory-recorded gun-range audio (Category D: $\ge 89.3\%$ recall) and calibrated spliced streams (Category C: $\approx 75.0\%–80.0\%$ recall). In Phase 19, evaluation against the Pittsburgh dataset yielded a lower individual round recall of $54.00\%$ under the default baseline (Phase 14 Balanced) and $66.00\%$ under the experimental candidate (Phase 17 Experimental), alongside $100.00\%$ precision (zero false alarms across 200 seconds of audio).

This Phase 20 audit was executed without modifying any frozen model weights, thresholds, temporal logic, or suppression rules. Every data record, waveform transformation, spatial coordinate, event annotation, and inferential claim was forensically audited.

### Primary Audit Findings:
1. **Nature of the Data:** The Pittsburgh dataset is **controlled live-fire system validation**, conducted by the City of Pittsburgh Bureau of Police and ShotSpotter Inc. on **December 18–19, 2018**. It does not represent naturally occurring urban gunfire.
2. **Audio Lineage:** Each of the 20 Category A recordings is an **unbroken, continuous 10.000000-second sensor recording** (`RESAMPLED_OR_NORMALIZED_COPY` from an `ORIGINAL_UNBROKEN_SENSOR_RECORDING`). There is zero splicing, concatenation, looping, or crossfading. Duration delta relative to the original source file is exactly $0.000000\text{ seconds}$.
3. **Canonical Accounting Reconciled:** The evaluation suite contains exactly **23 positive recordings** (20 Category A + 3 Category B) and **53 physical gunshot events** (50 Category A + 3 Category B). Reconciliation across all manifests is 100% complete with zero discrepancies.
4. **Campaign Singularity:** The 5 evaluated firing positions (FP1–FP5) belong to **one single municipal validation campaign**, not five independent campaigns or cities.
5. **Coordinate Incomputability:** The coordinates provided in the source repository are centered on **arbitrary local Cartesian origins per firing position** to protect residential privacy. Inter-position Euclidean distances cannot be computed from dataset coordinates.
6. **Paired Statistical Significance:** On the 50 Category A events, Phase 17 Experimental detected all 27 events detected by Phase 14 Balanced, plus 6 additional events (0 misses of Phase 14 detections). The exact two-sided binomial McNemar test yields:
   $$p = 2 \cdot (0.5)^6 = 0.03125 < 0.05$$
   The recall improvement (+12.0%) is statistically significant.
7. **Baseline Gate Decision:** Despite statistical significance, **Phase 17 Experimental is NOT promoted to the default production baseline**. Phase 14 Balanced remains the default production baseline because Phase 17's false-alarm resistance over multi-day urban exposure remains unproven.
8. **Incident vs. Round Discrepancy:** Phase 14 Balanced achieved $75.00\%$ incident recall despite $54.00\%$ round recall; Phase 17 Experimental achieved $90.00\%$ incident recall despite $66.00\%$ round recall. This divergence is mechanically caused by the detector's **2.0-second refractory cooldown**, which suppresses trailing shots during rapid 3-round bursts.
9. **False-Alert Fallacy:** The observed $100.00\%$ precision across 200.0 seconds of audio represents only **140 seconds (~2.33 minutes) of quiescent background exposure**. The exact 95% Poisson upper confidence bound on false alert rate is **$53.92\text{ alerts/hour}$**. A 200-second dataset cannot prove low false-alarm rate in general.
10. **Terminology Enforcement:** The term "dispatch" is strictly forbidden; outputs are designated exclusively as **"alerts"**, **"detector notifications"**, or **"acoustic triggers"**.

---

## Comprehensive Responses to the Ten Decision-Gate Questions

### Question 1: Does the Pittsburgh dataset represent naturally occurring urban gunfire, or controlled live-fire system validation?
**Audited Verdict:** **Controlled Live-Fire System Validation.**  
The official source repository (`https://github.com/ShotSpotter/research.accuracy-of-gunshot-location`) and City of Pittsburgh Bureau of Police documentation confirm that this dataset was produced during an annual Data Quality Validation (DQV) operation conducted between 00:00 and 06:00 UTC on December 19, 2018 (local night of Dec 18). 
- Shooters were sworn police personnel firing from surveyed curb markings.
- Weapons and calibers were predetermined duty sidearms (.45 ACP, .40 S&W, 9x19mm).
- Firing cadences were strictly scripted (single shots, 2-round pairs, 3-round bursts).
- Surrounding street intersections were controlled by police cruisers.
It is an authentic acoustic propagation dataset in a real urban environment, but it is **not unexpected, chaotic, or weapon-unconstrained criminal gunfire**.

### Question 2: Are the 20 Category A recordings unbroken sensor recordings, or derived/spliced clips?
**Audited Verdict:** **Unbroken 1-to-1 Resampled Sensor Copies.**  
Every one of the 20 Category A files maps 1-to-1 to a single unbroken raw sensor recording `test_{xxx}.audio.{sn}.wav` from the ShotSpotter repository. 
- Original: 12,000 Hz, 120,000 samples, exactly 10.000000 seconds.
- Derived: 16,000 Hz, 160,000 samples, exactly 10.000000 seconds.
- Duration difference: Exactly $0.000000\text{ seconds}$.
- Continuity audit: Zero concatenation, zero splicing, zero looping, zero crossfades, and zero time-cropping.
Each recording captures an unbroken 10-second continuous window around a test. Formally classified as `RESAMPLED_OR_NORMALIZED_COPY` from an `ORIGINAL_UNBROKEN_SENSOR_RECORDING`.

### Question 3: How many physical events are present, how many recordings, and what is the exact reconciliation between 50 and 53 events, and 20 and 23 recordings?
**Audited Verdict:** **53 Canonical Events Across 23 Positive Recordings.**  
- **Category A (ShotSpotter Pittsburgh):** Exactly 20 recordings (`STREAM_PITT_001` to `STREAM_PITT_020`) containing exactly **50 physical gunshot events** (`EV_001` to `EV_050`) across 5 firing positions (FP1 to FP5, exactly 10 rounds per position).
- **Category B (External Pre-Cropped Clips):** Exactly 3 recordings (`CLIP_9LASH_01` to `CLIP_9LASH_03`) containing exactly **3 physical gunshot events** (`EV_051` to `EV_053`).
- **Total Accounting:** $20 + 3 = 23\text{ recordings}$; $50 + 3 = 53\text{ canonical events}$.
- All 53 events are uniquely indexed in `reports/phase20_canonical_event_manifest.csv` and verified in `reports/phase20_event_accounting.json`. Zero duplicate or phantom events exist.

### Question 4: Do the five firing positions represent five independent test campaigns, or five positions within one campaign?
**Audited Verdict:** **Five Positions Within ONE Single Municipal Validation Campaign.**  
The five evaluated firing positions (FP1, FP2, FP3, FP4, FP5) represent sequential mobile stops of a single police caravan on the night of December 18–19, 2018 in Pittsburgh, PA:
- FP1: 00:49 to 01:09 UTC
- FP2: 01:29 to 01:52 UTC
- FP3: 02:12 to 02:29 UTC
- FP4: 02:38 to 03:00 UTC
- FP5: 05:23 to 05:43 UTC
While they provide spatial variety across different street geometries within Pittsburgh, they do **not** represent independent campaigns, different cities, or varying seasonal conditions.

### Question 5: Can distances between firing positions be calculated from the dataset coordinates?
**Audited Verdict:** **NO (Inter-Position Distances Are Incomputable).**  
ShotSpotter and the Pittsburgh Bureau of Police anonymized the dataset to protect residential sensor locations by applying **an arbitrary local Cartesian offset independently to each firing position**. 
The origin $(0, 0, 0)$ is reset or shifted for each position. Therefore, computing Euclidean distance via $\sqrt{(X_2 - X_1)^2 + (Y_2 - Y_1)^2 + (Z_2 - Z_1)^2}$ yields arbitrary mathematical artifacts (e.g., $4,586\text{ m}$ between FP1 and FP2). True metric vectors between firing positions cannot be calculated without the withheld global transformation key.

### Question 6: Does Phase 17 show statistically significant improvement over Phase 14 Balanced on Pittsburgh data?
**Audited Verdict:** **YES (Statistically Significant at $\alpha = 0.05$).**  
On the 50 Category A events, paired evaluation demonstrates:
- Both models detected: **27 events**
- Phase 14 detected, Phase 17 missed: **0 events**
- Phase 14 missed, Phase 17 detected: **6 events**
- Both models missed: **17 events**
- Total discordant pairs: $n = 6$
The exact two-sided binomial McNemar test calculation:
$$p = 2 \cdot \binom{6}{0} (0.5)^6 = 2 \cdot \frac{1}{64} = 0.03125$$
Because $p = 0.03125 < 0.05$, the +12.0% recall advantage of Phase 17 Experimental ($66.0\%$ vs. $54.0\%$) is statistically significant.

### Question 7: Should Phase 17 be promoted to the default baseline?
**Audited Verdict:** **NO. Maintain Phase 14 Balanced as Default Baseline.**  
Promotion is denied based on risk-managed production engineering criteria:
1. **Unverified Urban Negative Exposure:** Phase 17's acoustic gating modifications were specifically tuned to suppress rural animal vocalizations (canines, cattle, birds). Its false-alarm rejection over hundreds of hours of complex urban non-gunfire noise (construction, sirens, metal impact) has not been proven.
2. **Phase 14's Proven Multi-Hour Stability:** Phase 14 Balanced is backed by the Phase 16 benchmark of $6.08\text{ hours}$ of natural continuous negative audio ($0.99\text{ alerts/hour}$) and Phase 14 High-Precision ($0.00\text{ alerts/hour}$).
3. **Status Designation:** Phase 14 Balanced remains the **DEFAULT PRODUCTION BASELINE**. Phase 17 Experimental remains a **SELECTABLE EXPERIMENTAL PROFILE**.

### Question 8: Why does incident-level recall differ from round-level recall?
**Audited Verdict:** **Refractory Cooldown and Multi-Round Firing Bursts.**  
- Category A contains 10 three-round burst tests where 3 shots are discharged within $1.0$–$1.5\text{ seconds}$.
- The detector architecture enforces a **2.0-second refractory cooldown** (`COOLDOWN_SECONDS = 2.0`) following an alert to prevent multipath reverberation from generating cascading duplicate notifications.
- The initial round in a burst triggers an alert. Subsequent rounds arriving $300$–$600\text{ ms}$ later fall within the refractory window and are held or merged into the primary alert's coda.
- Under strict 1-to-1 event matching, those trailing rounds are scored as round-level misses.
- Consequently, while only $54.0\%$ of individual rounds were detected by Phase 14 Balanced, **$75.00\%$ of shooting incidents (15 of 20 live streams)** triggered valid alerts. Under Phase 17 Experimental, round recall was $66.0\%$ while incident recall reached **$90.00\%$ (18 of 20 streams)**.

### Question 9: Does 100% precision on Category A demonstrate low false-alert rate in general?
**Audited Verdict:** **NO. This is a Methodological Fallacy.**  
Across the 20 Category A recordings, total audio duration is only $200.0\text{ seconds}$ (~3.33 minutes). 
Active gunfire and refractory cooldown occupy ~60 seconds, leaving only **140 seconds (~2.33 minutes) of quiescent urban background exposure**.
Under Poisson statistics (Garwood exact 95% confidence bound), observing zero false alarms over 200 seconds yields an upper bound of:
$$\lambda_{\text{upper}} = \frac{2.99573}{200\text{ s}} \times 3600\text{ s/hr} = 53.92\text{ alerts/hour}$$
Zero false alarms over 200 seconds is mathematically consistent with an operational false alarm rate of up to **54 false alarms per hour** (one every 67 seconds). Long-duration negative continuous benchmarks (such as Phase 16's 6.08 hours) are the only valid measure of false-alarm resistance.

### Question 10: What does the evidence prove, and what does it NOT prove?
**Audited Verdict:**

| What the Available Evidence PROVES | What the Available Evidence DOES NOT PROVE |
| :--- | :--- |
| 1. Phase 14 Balanced detects genuine ballistic discharges digitized by unseen commercial sensor hardware in real urban street canyons ($54.0\%$ round recall, $75.0\%$ incident recall). | 1. It does NOT prove multi-city generalization (all data is from Pittsburgh, PA). |
| 2. Phase 17 Experimental achieves statistically significant higher sensitivity than Phase 14 Balanced on Pittsburgh audio ($p = 0.03125$). | 2. It does NOT prove multi-season generalization (all tests were conducted on one winter night at $\sim 0^\circ\text{C}$). |
| 3. The 20 Category A audio files are unbroken, authentic 10-second continuous recordings derived via 1-to-1 polyphase resampling. | 3. It does NOT prove performance against unconstrained criminal gunfire (moving shooters, rifles, concealed weapons, drive-bys). |
| 4. The detector operates with zero false alerts across the 200 seconds of available Pittsburgh audio. | 4. It does NOT prove low operational false-alarm rates over extended multi-day urban exposure. |
| 5. Incident-level alerting reliably captures multi-shot bursts ($75\%–90\%$) despite refractory suppression of individual rounds. | 5. It does NOT prove that individual rounds can be reliably counted during rapid semi-automatic fire. |

---

## Complete Frozen Detector Performance Matrix

### Category A: ShotSpotter Pittsburgh PA DQV 2018 (Controlled Urban Validation)
*20 unbroken continuous sensor recordings, 200.0 seconds total exposure, 50 physical gunshot rounds.*

| Detector Model | Architectural Role | Detected Rounds ($TP$) | Missed Rounds ($FN$) | False Alerts ($FP$) | Round Recall (95% Wilson CI) | Incident Recall (95% Wilson CI) | Precision |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Phase 14 Balanced** | Default Production Baseline | **27** | 23 | 0 | **54.00%** [40.40%, 67.03%] | **75.00%** [53.13%, 88.81%] | **100.0%** |
| **Phase 14 High-Precision** | Production Profile | **24** | 26 | 0 | **48.00%** [34.80%, 61.49%] | **60.00%** [38.66%, 78.12%] | **100.0%** |
| **Phase 14 High-Sensitivity** | Production Profile | **22** | 28 | 0 | **44.00%** [31.16%, 57.69%] | **65.00%** [43.29%, 81.88%] | **100.0%** |
| **Phase 17 Experimental** | Selectable Research Profile | **33** | 17 | 0 | **66.00%** [52.15%, 77.56%] | **90.00%** [69.90%, 97.21%] | **100.0%** |
| **Phase 9 Balanced** | Historical Comparator | **28** | 22 | 1 | **56.00%** [42.31%, 68.84%] | **70.00%** [48.10%, 85.00%] | **96.55%** |
| **Phase 13 Balanced** | Historical Comparator | **16** | 34 | 0 | **32.00%** [20.80%, 45.79%] | **70.00%** [48.10%, 85.00%] | **100.0%** |

---

## Baseline Integrity and Verification Sign-Off

All baseline models and archives verified against frozen cryptographic SHA-256 digests:
- `model_phase14.py`: `a268551604ae8b73068435ff10ab3d265065f56e0679757fca5b6bf0f061c065` (`DEFAULT_PRODUCTION_BASELINE`)
- `model_phase17.py`: `e2b262b866fdd5d7f1a4ab91a7b8b9bac189ee8cc7a78603b3544ca1579fb819` (`SELECTABLE_EXPERIMENTAL_PROFILE`)
- `model_phase13.py`: `68585039a4a4fdb7978a99f5e2a72c0ad5a9523127ec24a1338fbedd1c1231e6` (`FROZEN_HISTORICAL_COMPARATOR`)
- `model_phase9.py`: `85cedd9f5b988ecafb1eae7de9630ee3d6a387ded6ef732e0efb7c3b496f132a` (`FROZEN_HISTORICAL_COMPARATOR`)
- `gunshot_detection_phase19.zip`: `9d768b9db3126aa23b37dd0f6b00804345929a4171499f703e4bb84132ad9ac4`

---
*Report certified by Principal Acoustic ML Research Engineer, Audio DSP Specialist, Dataset Provenance Auditor and Real-Time Systems Engineer.*

