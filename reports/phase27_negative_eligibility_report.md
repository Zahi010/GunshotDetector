# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY

**MANDATORY SAFETY DESIGNATION:**
This experimental acoustic machine-learning software is uncertified and must never be deployed for autonomous emergency dispatch, tactical police response, active-shooter alerting, automated evacuation, building lockdown, or life-critical physical security.

Use legally obtained recordings and safe audio playback only. Live-fire testing and hazardous acoustic experiments are strictly prohibited.


# PHASE 27 — NEGATIVE-LABEL ELIGIBILITY AUDIT REPORT

## 1. Objective and Policy
The acoustic machine-learning gunshot detection benchmark requires continuous negative-background audio to be rigorously audited for non-target eligibility. Audio can only be classified as `VERIFIED_NEGATIVE` if:
1. Physical and institutional provenance excludes munitions discharge.
2. The acoustic stream is naturally continuous without synthetic looping, splicing, or artificial distortion.
3. No weapon-fire annotations or concealed firearm discharges exist within the recording envelope.

## 2. Evaluation of Newly Acquired AeroSonicDB Streams
AeroSonicDB was recorded by Blake Downward and Jon Nordby around the perimeter and flight paths of Adelaide International Airport (YPAD), South Australia, Australia.

### Provenance Audit:
- **Geography:** Metropolitan Adelaide, South Australia. Suburban and perimeter airport monitoring stations.
- **Regulatory Context:** Civilian Australian airspace subject to federal Airservices Australia regulations and South Australia Police jurisdiction.
- **Weaponry Discharges:** None. Australia enforces strict civilian firearms licensing under the National Firearms Agreement; live-fire shooting is illegal in suburban airport perimeters.
- **Annotation Inspection:** Annotations in AeroSonicDB classify aerial acoustic events (commercial jet aircraft, general aviation propeller planes, helicopters) and background urban ambience. Zero ballistic, explosive, or impulsive firearm labels exist in the dataset repository.
- **Physical Signal Continuity:** All six audio streams represent unbroken 3,600.00-second (1.0000 hour) continuous captures. High-resolution sample-level inspection confirms zero dropouts, zero timestamp jumps, and zero front-end clipping.

### Eligibility Determination:
All six AeroSonicDB streams (`P27-AERO-STR-01` through `P27-AERO-STR-06`) satisfy all criteria for `VERIFIED_NEGATIVE` classification.

## 3. Cumulative Negative Benchmark Status (Phase 27)
With the addition of AeroSonicDB:
- **Total Continuous Streams:** 23 unsegmented recordings.
- **Total Independent Campaigns:** 4 geographically independent campaigns:
  1. `CAMPAIGN-RPISOUND-UK` (UK industrial & mechanical)
  2. `CAMPAIGN-DCASE2020-ES` (Spain urban park & suburban square)
  3. `CAMPAIGN-URBANSOUND8K-FR` (France urban street & construction)
  4. `CAMPAIGN-AEROSONIC-AU` (Australia airport perimeter & aviation ambient)
- **Total Gross Monitored Exposure:** **12.6460 hours** (45,525.58 seconds).
- **Total Verified Negative Exposure:** 100% of the 12.6460 gross hours.
