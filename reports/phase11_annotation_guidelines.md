# PHASE 11 ANNOTATION GUIDELINES: Standard Operating Procedure for Acoustic Event Labeling

> [!CAUTION]
> **SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY**  
> Acoustic annotation criteria define ground truth for experimental evaluation. They do not constitute legal or forensic ballistics certification.

---

## 1. Objectives & Principles

Accurate model validation depends strictly on objective, reproducible annotation of physical acoustic events. In past phases, labeling inconsistencies (such as duplicate event collisions, ambiguous firework recordings, and subjective transient boundaries) distorted event recall and precision metrics.

This document establishes the canonical standard operating procedure for annotating field recordings.

---

## 2. Event Classification Taxonomy

Every physical acoustic event in a field recording must be assigned to one of three mutually exclusive categories:

```
+---------------------------------------------------------------------------------------------------+
| GROUND TRUTH LABEL TAXONOMY                                                                       |
+---------------------------------------------------------------------------------------------------+
| 1. Confirmed Gunshot (ground_truth_label = 1)                                                     |
|    - Verified ballistic discharge from a real firearm (rifle, shotgun, handgun).                  |
|    - Visual or direct telemetry corroboration (e.g., synchronized range camera, timer, or RSO log).|
|    - Waveform exhibits definitive supersonic shockwave (N-wave) and/or explosive muzzle blast.    |
|                                                                                                   |
| 2. Confirmed Negative Mimic (ground_truth_label = 0)                                              |
|    - Verified non-firearm acoustic source (thunder, fireworks, dog barks, vehicle exhaust,       |
|      pneumatic tool, door slam, metal clatter, hail, wind gust).                                  |
|    - Source verified by visual documentation, operator log, or controlled playback protocol.      |
|                                                                                                   |
| 3. Uncertain / Ambiguous Transient (ground_truth_label = -1)                                      |
|    - Acoustic event cannot be definitively confirmed by corroborating evidence.                  |
|    - Severe background masking (SNR < 3 dB), clipped saturation, or muffled distance (> 500m).     |
|    - MANDATORY RULE: Never force ambiguous audio into positive (1) or negative (0) labels!        |
|      Uncertain audio is tracked separately and excluded from primary F1 score calculations.       |
+---------------------------------------------------------------------------------------------------+
```

---

## 3. Physical Event Boundary Definition

A ballistic gunshot consists of two primary acoustic components:
1. **Supersonic Shock Front (N-Wave):** Generated if the projectile exceeds the local speed of sound ($c \approx 343\text{ m/s}$). Extremely rapid rise time ($< 10\ \mu\text{s}$) with duration of $100\text{--}300\ \mu\text{s}$.
2. **Muzzle Blast:** Omnidirectional explosive expansion of high-pressure combustion propellant gases exiting the barrel. Typical duration: $2\text{--}10\text{ ms}$, followed by an environmental reverberant decay tail.

### Boundary Annotation Protocol:
- **Event Start Time ($T_{\text{start}}$):**  
  The exact sample timestamp where acoustic pressure deviates from the baseline ambient noise floor by $> 3\sigma$ (standard deviations), corresponding to the first pressure rise of either the shock front or muzzle blast.
- **Event End Time ($T_{\text{end}}$):**  
  The timestamp where the direct blast and immediate high-energy early reflections have decayed to within $6\text{ dB}$ of the baseline noise floor (typically $0.15\text{--}0.35\text{ seconds}$ after onset).  
  *Rule:* **Do NOT extend $T_{\text{end}}$ across prolonged low-frequency reverberant decay tails (> 0.5s)**; long tails belong to environmental acoustic response, not the physical projectile event.

---

## 4. Rapid Fire, Bursts & Multi-Shot Aggregation

When multiple ballistic discharges occur in close succession (automatic fire, bursts, or double-taps):
- **Inter-Shot Interval $\ge 0.50\text{ seconds}$:**  
  Each discharge must be labeled as an independent physical event with distinct $T_{\text{start}}$ and $T_{\text{end}}$.
- **Inter-Shot Interval $< 0.50\text{ seconds}$ (Rapid Burst):**  
  Each individual shot must still receive an individual onset annotation. In addition, the burst sequence must be tagged with a common `burst_id` so that evaluation scripts can evaluate both individual shot recall and burst-level alert aggregation.

---

## 5. Event Matching Tolerance & One-to-One Bipartite Matching

To prevent a single detector alert from claiming credit for multiple physical gunshots, evaluation must adhere to strict **one-to-one Hungarian / bipartite matching**:

1. **Matching Tolerance Window ($\Delta t$):**  
   An emitted detector alert at timestamp $T_{\text{alert}}$ matches a ground-truth gunshot event $[T_{\text{start}}, T_{\text{end}}]$ if:
   $$|T_{\text{alert}} - T_{\text{start}}| \le 0.75\text{ seconds}$$
2. **One-to-One Matching:**  
   Once a ground-truth event is matched to an alert, it is marked **consumed**. Subsequent alerts falling within the same interval are classified as **Duplicate Alerts**, not True Positives.
3. **Metric Classification:**
   - **True Positive (TP):** Unmatched ground-truth event paired with an alert within $\pm 0.75\text{s}$.
   - **Missed Event / False Negative (FN):** Ground-truth event with no alert within $\pm 0.75\text{s}$.
   - **False Alert (FP):** Alert emitted when no ground-truth gunshot event exists within $\pm 0.75\text{s}$.
   - **Duplicate Alert (DUP):** Secondary alert emitted within cooldown of an already matched event.

---

## 6. Reviewer Adjudication Protocol

Every annotated recording must undergo dual-reviewer adjudication:
1. **Primary Annotator:** Inspects spectrogram and waveform in Audacity / Praat, marks onsets, assigns preliminary label (`1`, `0`, `-1`).
2. **Secondary Reviewer:** Independently verifies onset alignment and label classification against field logs.
3. **Resolution of Discrepancies:** If annotators disagree on whether an event is a gunshot or mimic, the event is automatically assigned `ground_truth_label = -1` (Uncertain).

```
+---------------------------------------------------------------------------------------------------+
| ANNOTATION QUALITY GATE:                                                                          |
|  - Minimum inter-annotator agreement (Cohen's Kappa): kappa >= 0.92                               |
|  - Disputed acoustic events are strictly quarantined to ground_truth_label = -1                  |
|  - Final evaluation manifest is frozen prior to running model predictions.                        |
+---------------------------------------------------------------------------------------------------+
```
