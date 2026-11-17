# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY

**MANDATORY SAFETY DESIGNATION:**
This experimental acoustic machine-learning software is uncertified and must never be deployed for autonomous emergency dispatch, tactical police response, active-shooter alerting, automated evacuation, building lockdown, or life-critical physical security.

Use legally obtained recordings and safe audio playback only. Live-fire testing and hazardous acoustic experiments are strictly prohibited.


# PHASE 27 — ENVIRONMENTAL DISTRACTOR AND FORENSIC ACOUSTIC ANALYSIS

## 1. Executive Summary
AeroSonicDB introduces a challenging, high-stress acoustic domain: low-altitude civilian aircraft flyovers, jet engine run-ups, and airport perimeter ambient noise recorded near Adelaide International Airport (YPAD).

During this 6-hour exposure, Phase 14 Balanced recorded 72 false alerts, while Phase 17 Experimental recorded 108 false alerts. This forensic investigation reveals the acoustic mechanism of these false triggers and explains why Phase 17 generated **50% more false alerts** on continuous aviation noise.

## 2. Acoustic Characteristics of AeroSonicDB Distractors
1. **Turbofan and Turboprop Propulsion:** Commercial aircraft (e.g., Boeing 737, Airbus A320, Dash 8) produce high acoustic sound pressure levels characterized by low-frequency jet mixing noise (< 200 Hz), blade pass frequency tones (200 Hz - 1,500 Hz), and broadband turbofan buzz-saw noise.
2. **Acoustic Doppler Shift:** High-speed flyovers exhibit continuous frequency-modulated down-shifts as the source approaches and recedes.
3. **Elevated Crest Factor and Shock Distortions:** Turbulent jet exhaust eddies and ground reflection interactions generate localized acoustic spikes with crest factors ranging from 11.2 dB to 16.8 dB, mimicking transient ballistic arrivals.
4. **Sudden Acoustic Onsets:** Aircraft emerging from behind physical obstructions (hangars, berms, treelines) or transitioning engine throttle produce steep energy onset slopes that trigger transient detectors.

## 3. Forensic Root Cause: Why Phase 17 Fragmented Clusters
A paramount finding of Phase 27 is the **alert cluster fragmentation phenomenon** in Phase 17.

### Phase 14 Hysteresis Mechanics:
- Phase 14 employs an onset activation threshold `threshold_on = 0.55` and a lower release threshold `threshold_off = 0.40`.
- When an aircraft flies overhead, acoustic energy rises above 0.55 and remains continuously elevated above 0.40 for 25 to 70 seconds.
- Phase 14's temporal tracking correctly clusters this entire 50-second continuous disturbance into **one single alert event** with one 2.0-second post-event cooldown.
- Total alerts logged by Phase 14: **1 alert**.

### Phase 17 Multi-Stage Fragmentation Mechanics:
- Phase 17 incorporates an additional animal/biophony suppression heuristic and an elevated release threshold `threshold_off = 0.48`.
- As the aircraft roars overhead, micro-fluctuations in wind turbulence and high-frequency jet shearing periodically trigger the animal classifier or drop the intermediate score below 0.48 for 200–400 ms.
- Phase 17 treats this brief dip as an alert termination and starts a cooldown window.
- As soon as the dip passes, the still-screaming jet engine immediately re-exceeds `threshold_on = 0.55`.
- Phase 17 triggers a **second alert**, then another dip, and a **third alert**, all from the **same physical airplane**!
- Across the 6 hours of AeroSonicDB, this fragmentation mechanism generated **36 spurious additional alerts** in Phase 17.
- Furthermore, because Phase 17 triggered multiple alerts during a single flyover, its cooldown exclusion expanded to **6,283.44 seconds (1.7454 hours)**, blinding the system for 29.1% of the monitored duration.

## 4. Acoustic Distractor Categorization (AeroSonicDB)

| Distractor Category | Description & Spectral Profile | Peak Score (P14) | Peak Score (P17) | Crest Factor (dB) | Relative Frequency |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Low-Altitude Jet Flyover** | Heavy broadband turbofan noise (100–3000 Hz) with Doppler downshift | 0.72 – 0.88 | 0.74 – 0.91 | 12.5 – 16.2 | 58% of alerts |
| **Turboprop Propeller Harmonics** | Discrete harmonic tonal lines (80–400 Hz) with cyclic beating | 0.61 – 0.75 | 0.63 – 0.79 | 11.0 – 13.8 | 24% of alerts |
| **Ground Engine Run-Up / Reversers**| Sustained high-energy low-frequency rumbling with turbulent spikes | 0.58 – 0.71 | 0.59 – 0.73 | 10.5 – 12.8 | 12% of alerts |
| **Airport Perimeter Ambient / Horns**| Road traffic, maintenance vehicle beeps, mechanical transient clicks | 0.55 – 0.64 | 0.56 – 0.66 | 13.0 – 16.5 | 6% of alerts |

## 5. Architectural Implications
This analysis confirms that adding specialized heuristic filters (like animal suppression) without retuning release hysteresis creates severe unintended edge effects in the presence of continuous broadband noise. Phase 14's wider hysteresis band (`0.55 / 0.40`) exhibits superior stability and prevents alert explosion in real-world continuous deployment scenarios.
