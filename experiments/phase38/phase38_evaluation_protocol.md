# PHASE 38 EVALUATION PROTOCOL: PROSPECTIVE HOLDOUT EVALUATION

> [!CAUTION]
> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.**
> This experimental acoustic gunshot detection software is uncertified research software. It must never be deployed for autonomous emergency dispatch, police tactical response, active-shooter alerting, automated evacuation, building lockdown, or life-critical physical security.
> Use legally obtained recordings and safe audio playback only. Live-fire testing and hazardous acoustic experiments are strictly prohibited.

---

## 1. Research Question

Does the frozen Phase 36 experimental event-state architecture (`model_phase36.py`) generalize to previously unseen, lawfully obtained out-of-sample recordings without degradation in sensitivity, and does it reduce false alerts compared to the frozen Phase 14 Balanced baseline?

### Primary Hypotheses:
1. **False Alert Reduction:** Phase 36 reduces continuous ambient false alerts relative to Phase 14 Balanced and eliminates the catastrophic candidate accumulation defect of Phase 17.
2. **Sensitivity Parity or Improvement:** Phase 36 maintains or improves positive event-level and round-level recall on previously unseen gunfire audio compared to Phase 14 Balanced.
3. **Distractor Robustness:** Phase 36 achieves equal or superior rejection of impulsive and non-impulsive non-gunshot acoustic distractors (fireworks, thunder, doors, animals, tools, aviation).

---

## 2. Evaluation Conditions & Frozen Detectors

The prospective evaluation compares six standardized conditions:

| Condition ID | Architecture / Model Profile | Script / Module | Frozen SHA-256 Hash | Profile Role |
|:---:|---|---|---|---|
| **`COND1`** | Phase 14 Balanced Baseline | `model_phase14.py` | `a268551604ae8b73068435ff10ab3d265065f56e0679757fca5b6bf0f061c065` | Default Research Baseline |
| **`COND2`** | Phase 17 Experimental Frozen Profile | `model_phase17.py` | `e2b262b866fdd5d7f1a4ab91a7b8b9bac189ee8cc7a78603b3544ca1579fb819` | Historical Comparator (Known State Defect) |
| **`COND3`** | Phase 17 Reset Candidate | `model_phase17_state_reset_candidate.py` | `c144b917b56532787e2a9198f2cad4a77dc2095b57962f31d11d250a4d5d9ea5` | Quarantined Diagnostic Reference |
| **`COND4`** | Phase 36 Raw State Machine | `model_phase36.py` | `2774ab4cae0fca6d2f3646b443694fefa40d6837ff195f1d216ae7ff7732563a` | Experimental Branch (Suppression Disabled) |
| **`COND5`** | Phase 36 Legacy Suppression | `model_phase36.py` | `2774ab4cae0fca6d2f3646b443694fefa40d6837ff195f1d216ae7ff7732563a` | Experimental Branch (Legacy 0.30x Multiplier) |
| **`COND6`** | Phase 36 Conservative Suppression | `model_phase36.py` | `2774ab4cae0fca6d2f3646b443694fefa40d6837ff195f1d216ae7ff7732563a` | Default Phase 36 Configuration |

### Parameter Freeze:
No thresholds, feature extraction parameters, suppression multipliers, or state machine constants may be tuned, fitted, or altered against the prospective evaluation dataset.

---

## 3. Input Audio Requirements & Preprocessing

- **Format:** Single-channel (mono), 16-bit linear PCM audio.
- **Sampling Rate:** 16,000 Hz ($16\text{ kHz}$).
- **Resampling:** Multi-channel audio is averaged to mono. Non-16 kHz audio is resampled to 16 kHz using high-quality anti-aliasing interpolation (consistent with `feature_extractor.py`).
- **Framing & Windowing:** 0.96-second sliding analysis windows with 0.48-second hop (50% overlap).
- **Acoustic Features:** 64-dimensional log-mel spectrogram frames, spectral flux, zero-crossing rate, crest factor, and YAMNet pre-trained acoustic embeddings.

---

## 4. Ground-Truth Annotations & Matching Criteria

### 4.1 Annotation Format
Each positive event is defined by:
`recording_id, event_id, start_time_seconds, end_time_seconds, peak_time_seconds, event_type, source_dataset, license`

### 4.2 Matching Tolerance
A detector alert is eligible to match an annotated event if its reported alert timestamp $t_{\text{alert}}$ satisfies:
$$|t_{\text{alert}} - t_{\text{annotated}}| \le 0.75\text{ seconds}$$
If an event duration interval $[t_{\text{start}}, t_{\text{end}}]$ is annotated, an alert is eligible if $t_{\text{start}} - 0.50\text{s} \le t_{\text{alert}} \le t_{\text{end}} + 0.50\text{s}$.

### 4.3 Strict One-to-One Matching Algorithm
To prevent artificial inflation of sensitivity:
1. Candidate matches are evaluated greedily in order of temporal proximity $|t_{\text{alert}} - t_{\text{annotated}}|$.
2. Each ground-truth event can match at most ONE alert. Once matched, the event is marked `MATCHED` and removed from candidate pools.
3. Each detector alert can match at most ONE event. Once matched, the alert is classified as `TRUE_POSITIVE (TP)`.
4. Any remaining annotated event without an alert is classified as `FALSE_NEGATIVE (FN)`.
5. Any detector alert outside the matching tolerance of all annotated events is classified as `FALSE_POSITIVE (FP)`.

### 4.4 Duplicate Alert Treatment
If a detector emits multiple alerts during a single physical event (e.g. within 2.0 seconds after a confirmed alert):
- The first alert is credited as the matching alert.
- Subsequent alerts within the event window are classified as `DUPLICATE_ALERT`.
- Duplicate alerts do not increase True Positives and are tracked separately in the duplicate rate:
$$\text{Duplicate Rate} = \frac{\text{Duplicate Alerts}}{\text{Total Alerts}}$$

### 4.5 Burst-Fire Distinction
For rapid multi-round sequences (burst fire):
- **Round-Level Strict 1-to-1:** 1 alert matches 1 round only. (Remaining rounds in the same sustained event are counted as FN under strict 1-to-1).
- **Burst Overlap (Incident-Level):** Evaluates whether each round's physical time overlaps an active confirmed detector interval. Both metrics must be reported side-by-side.

---

## 5. Continuous Exposure & False Alert Calculations

### 5.1 Eligible Exposure Definitions
- **Gross Exposure ($T_{\text{gross}}$):** Total continuous audio duration in hours.
- **Convention A (10.0s Cooldown):** Excludes 10.0 seconds from exposure following every confirmed alert:
$$T_{\text{eligible, Conv A}} = T_{\text{gross}} - \sum \Delta t_{\text{cooldown, Conv A}}$$
- **Convention B (Post-Clearance Cooldown):** Excludes the event duration plus 10.0 seconds of post-clearance quiet time:
$$T_{\text{eligible, Conv B}} = T_{\text{gross}} - \sum \Delta t_{\text{cooldown, Conv B}}$$

### 5.2 False Alarm Rate (FAR) Metrics
- **Gross FAR:** $\text{FAR}_{\text{gross}} = \frac{N_{\text{alerts}}}{T_{\text{gross}}}\quad (\text{alerts/hour})$
- **Eligible FAR:** $\text{FAR}_{\text{eligible}} = \frac{N_{\text{alerts}}}{T_{\text{eligible}}}\quad (\text{alerts/hour})$

---

## 6. Distractor Evaluation Protocol

- Non-target clips must be human-reviewed or certified ground truth from authoritative datasets (e.g. FSD50K).
- Categorized into:
  - `Aviation`: Airplanes, helicopters, propeller aircraft
  - `Animal`: Dog barking, birds, wildlife
  - `Impulsive Urban`: Door slams, metal clangs, construction impacts, hammer blows
  - `Explosive / Transient`: Fireworks, explosions, thunder
- **Trigger Rate:** $\frac{N_{\text{clips with }\ge 1\text{ alert}}}{N_{\text{total clips in category}}}$

---

## 7. Statistical Uncertainty & Clustering

- **Poisson 95% Confidence Intervals:** Computed using exact chi-square quantiles for event rates.
- **Binomial 95% Confidence Intervals:** Computed using Clopper-Pearson exact intervals for precision and recall.
- **Clustering:** Recordings originating from the same session, uploader, or location must be aggregated at the session/campaign level to avoid treating correlated windows as independent observations.

---

## 8. Exclusion Criteria & Missing Data Policy

1. **Historical Overlap Exclusion:** Any recording sharing a SHA-256 hash or verified acoustic identity with files in Phases 1–37 must be excluded from the prospective evaluation set.
2. **Audio Integrity:** Recordings that fail decoding, contain unresolvable corruptions, or have zero energy across all channels are excluded with logged reasons.
3. **No Synthetic Inflation:** Under no circumstances may short clips be concatenated to simulate continuous exposure.

