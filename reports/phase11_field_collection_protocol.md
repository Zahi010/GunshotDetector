# PHASE 11 FIELD COLLECTION PROTOCOL: Safe, Controlled Acoustic Data Capture

> [!CAUTION]
> **MANDATORY SAFETY DESIGNATION**  
> **RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY**  
> Testing of this acoustic detection system must **NEVER** involve hazardous acoustic practices, unauthorized live firearm discharges, or automated emergency dispatch. The prototype is strictly a research tool.

---

## 1. Scope & Core Directives

Phase 10 confirmed that 100% of physical gunshot audio in the repository originates from previously examined diagnostic corpora (AudioSet, FreeSound, or Mitchell Roberts). True zero-shot physical generalization to unseen deployment terrains remains formally **UNVERIFIED**.

This document establishes the scientific, operational, and legal protocol for collecting genuinely new acoustic field recordings to govern future Phase 12 validation.

### Non-Negotiable Collection Directives:
1. **Safety & Legality:** Under no circumstances should test personnel discharge live firearms or organize hazardous acoustic experiments. Data collection must utilize:
   - Licensed firing range facilities under certified range safety officer (RSO) supervision.
   - Legally acquired, calibrated field audio recordings with verified chain of custody.
   - Calibrated acoustic loudspeaker replay of ballistic reference waveforms in controlled, non-populated test sites with municipal awareness.
2. **No Emergency Service Integration:** The test system must never be linked to municipal dispatch, law enforcement, private security, or automated notification networks.
3. **Pristine Held-Out Partitioning:** The proposed field collection dataset must remain strictly partitioned from model training, threshold tuning, and suppression-rule selection.

---

## 2. Target Acoustic Environments & Exposure Matrix

Field data collection must encompass a minimum of **24 cumulative exposure hours** across 8 distinct acoustic environments:

| Environment ID | Environmental Category | Target Exposure Duration | Target Impulsive Negative Mimics | Physical Acoustic Characteristics |
|---|---|---:|---|---|
| **ENV-01** | Open Rural Field / Farmland | 4.0 Hours | Bird calls, wind buffeting, tractors | Free-field propagation, minimal multipath reflection, high wind noise |
| **ENV-02** | Urban Street Canyon | 4.0 Hours | Vehicle horns, sirens, bus air-brakes | High ambient noise, severe multipath flutter echo from glass/concrete |
| **ENV-03** | Semi-Enclosed Perimeter (Parking Structure) | 3.0 Hours | Door slams, tire squeals, shopping carts | Pronounced reverberant ring-down (RT60 > 1.2s), impulse smearing |
| **ENV-04** | Residential Suburban Yard | 3.0 Hours | Canine barking bouts, lawn mowers | High impulsive canine vocalizations, children, leaf blowers |
| **ENV-05** | Forested Wooded Terrain | 3.0 Hours | Snapping branches, woodpeckers, wind | High acoustic scattering from tree trunks, dampening of high frequencies |
| **ENV-06** | Severe Weather Environment | 3.0 Hours | Thunder rumbles, heavy rain on roof/ground | Elevated continuous RMS energy (-15 dBFS), transient lightning crack |
| **ENV-07** | Construction / Industrial Site | 2.0 Hours | Pneumatic nail guns, pile drivers, hammer strikes | High-amplitude mechanical transients mimicking ballistic crest factors |
| **ENV-08** | Controlled Pyrotechnic Demonstration | 2.0 Hours | Firecrackers, aerial mortars, bottle rockets | Fast explosive chemical shock fronts, secondary crackle trails |

---

## 3. Hardware Deployment & Transducer Specifications

To guarantee acoustic realism and prevent transducer bias, field trials must simultaneously record across three distinct hardware tiers:

```
+---------------------------------------------------------------------------------------------------+
| HARDWARE TIER 1: Calibrated Reference Class                                                       |
|  - Transducer: 1/2" Free-Field Measurement Microphone (e.g. PCB 378B02 or Earthworks M30)         |
|  - Polar Pattern: Omnidirectional, flat frequency response (20 Hz - 40 kHz +/- 1 dB)              |
|  - ADC: 24-bit / 96 kHz low-noise studio interface                                               |
|  - Primary Role: Absolute ground-truth acoustic reference and unclipped pressure measurement     |
+---------------------------------------------------------------------------------------------------+
| HARDWARE TIER 2: Commercial Security Appliance Tier                                              |
|  - Transducer: Outdoor Weatherproof MEMS Microphone Array (e.g. Knowles SPH0645LM4H)              |
|  - Polar Pattern: Cardioid / Array beamforming                                                    |
|  - ADC: 16-bit / 16 kHz or 48 kHz standard embedded microcontroller ADC                           |
|  - Primary Role: Deployment target simulation on edge IoT devices                                |
+---------------------------------------------------------------------------------------------------+
| HARDWARE TIER 3: Consumer Edge Device Tier                                                        |
|  - Transducer: Standard smartphone / laptop internal electret microphone capsule                   |
|  - Signal Chain: Built-in hardware codec with automatic gain staging                              |
|  - Primary Role: Simulating web application browser streaming capture                             |
+---------------------------------------------------------------------------------------------------+
```

### Acoustic Gain Staging & Wind Protection:
- **Wind Protection:** All outdoor microphone capsules must be fitted with open-cell acoustic foam windscreens and synthetic fur "deadcat" windjammers to suppress turbulence below 500 Hz.
- **Headroom Management:** Analog pre-amplifier gain must be adjusted to maintain **at least 12 dB of digital headroom** above typical gunshot shock peaks ($< -12\text{ dBFS}$) to avoid digital hard clipping.

---

## 4. Metadata Logging & Manifest Integration

Every captured audio file must be entered into [`data/manifests/phase11_field_collection_manifest.csv`](file:///e:/gunshot/gunshot/data/manifests/phase11_field_collection_manifest.csv) before ingestion.

The 28 required fields capture:
1. `field_recording_id`: Stable UUID (e.g., `P11-FLD-202611-0001`).
2. `file_sha256`: Cryptographic digest calculated immediately after capture.
3. `collection_date`: YYYY-MM-DD.
4. `source_provenance`: Institutional recording source and permit reference.
5. `microphone_placement`: Exact stand-off distance (meters), azimuth (degrees), and elevation.
6. `weather_conditions`: Ambient temperature ($^\circ\text{C}$), wind velocity ($\text{m/s}$), and humidity ($\%$).
7. `ground_truth_label`: `1` (Confirmed Gunshot), `0` (Confirmed Negative), or `-1` (Ambiguous/Uncertain).
8. `clipping_observed`: Binary flag (`1` if waveform touches $\pm 1.0$, `0` otherwise).

---

## 5. Storage Security & Chain of Custody

1. **Checksum Verification:** Raw audio WAV files must have SHA-256 digests computed at the collection terminal and verified upon transfer to permanent storage.
2. **Immutability:** Field recordings must be marked read-only upon ingestion.
3. **Data Protection:** No audio containing identifiable human speech or private residential communications may be uploaded or distributed without privacy redaction.
