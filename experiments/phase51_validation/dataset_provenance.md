# Phase 51: Independent Evaluation Corpus & Dataset Provenance

**Mandatory Safety Designation:**
> **RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.**
> This is uncertified research software. Never deploy it for autonomous emergency dispatch, police tactical response, active-shooter alerting, automated evacuation, building lockdown, or life-critical physical security. Use only lawfully obtained recordings and safe audio playback. Live-fire and hazardous acoustic experiments are strictly prohibited.

---

## 1. Executive Summary

Phase 51 establishes an independent, un-tuned acoustic validation corpus to evaluate the true generalization capability of **Detector Improvement V8** alongside prior candidates **V7** and **V6**. To eliminate benchmark overfitting, data leakage, and confirmation bias, all candidate detectors were strictly frozen prior to evaluation.

The Phase 51 evaluation corpus consists of two major components:
1. **Discrete Acoustic Evaluation Corpus ($N=373$):** 65 genuine gunshot recordings spanning diverse calibers, acoustic environments, and recording geometries, paired with 308 rigorous non-gunshot negative controls (hard transients, pyrotechnics, environmental distractors, and acoustic impostors).
2. **Continuous Uncut Acoustic Exposure Corpus ($T=12.0\text{ hours}$):** 15 long-form continuous background streams across 3 independent recording campaigns (urban streetscapes, airport perimeter surveillance, and mixed domestic/transit ambiences) with zero injected gunfire.

Every audio file in this benchmark was verified for provenance, format standardization (16 kHz, 16-bit mono PCM), and cryptographic integrity.

---

## 2. Discrete Evaluation Corpus ($N=373$)

The 373 discrete recordings are organized into distinct acoustic groups to validate both positive sensitivity across degraded acoustics and false-alarm rejection across challenging environmental impostors.

### 2.1 Genuine Gunshot Positives ($N=65$)

All 65 positive recordings were drawn from lawfully obtained, historical independent ballistic recording archives that were never included in the training splits or tuning benchmarks of V1 through V8:

| Source Provenance | Origin / Campaign | Count | Acoustic Profile | Key Characteristics |
| :--- | :--- | :---: | :--- | :--- |
| **Mitchell Roberts Ballistic Archive** | Phase 8 Final Evaluation Archive | 43 | Multi-caliber open-air ballistic recordings | Handguns (.22 LR, 9mm, .40 S&W, .45 ACP), rifles (5.56 NATO, 7.62x39mm, .308 Win), shotguns (12 ga). Includes near-field, mid-field, and reverberant forest recordings. |
| **Mitchell Roberts GunshotClassifier** | Phase 7 Independent Field Test | 19 | Curated ballistic test captures | High-gain, high-energy open-air shots, multi-shot bursts, and unclipped ambient distance captures. |
| **ShotSpotter Research Archive** | Phase 7 Chicago Urban Canyon (Sensor 5, 6, 7) | 3 | Real-world urban acoustic sensor recordings | Distant urban street canyon acoustics, multipath building reflections, and environmental noise masking. |
| **Total Positives** | — | **65** | — | — |

#### Acoustic Subgroup Distribution of Positives:
- **Clean Open-Air ($N=35$):** Unobscured direct line-of-sight discharges with prominent supersonic shockwaves and muzzle blasts.
- **High-Energy Clipped / Saturated ($N=15$):** Near-field microphone saturation where peaks exceed digital ceiling ($\text{peak} \ge 0.95$), testing saturation resilience.
- **Rapid Cadence / Bursts ($N=9$):** Rapid semi-automatic and burst sequences, testing multi-window clustering and FSM cooldown behavior.
- **Pocket-Occluded / Degraded ($N=3$):** Concealed or muffled recordings characterized by severe high-frequency attenuation ($\text{rolloff} < 1800\text{ Hz}$).
- **Distant / Reverb ($N=3$):** Low SNR shots dominated by late diffuse reverberation tails.

---

### 2.2 Hard Negative Challenge & Environmental Controls ($N=308$)

To rigorously evaluate specificity and verify that the detectors do not trigger on acoustic impostors, 308 non-target recordings were assembled:

| Category | Source | Count | Acoustic Profile & Impostor Mechanism |
| :--- | :--- | :---: | :--- |
| **Fireworks & Pyrotechnics** | Curated Hard Negative Corpus | 12 | Aerial shells, roman candles, firecrackers; tests mid-to-low frequency pyrotechnic discrimination. |
| **Glass Shatter** | ESC-50 Class 39 (Folds 1–3 Untouched) | 20 | High-frequency shattering, breaking windowpanes, bottle impacts; tests high-band spectral centroid gating. |
| **Metal Hammer Impacts** | Curated Hard Negative Corpus | 12 | Sharp anvils, structural steel impacts, heavy metallic clangs; tests harmonic resonance decay rejection. |
| **Heavy Door Slams** | Curated Hard Negative Corpus | 12 | Industrial fire door slams, automotive hatch closures; tests sub-bass energy concentration. |
| **Thunder Rumbles** | Curated Hard Negative Corpus | 12 | Rolling atmospheric thunderclaps, low-frequency pressure waves; tests rumble suppression. |
| **Vehicle Backfires** | Curated Hard Negative Corpus | 12 | Automotive exhaust backfires and pop tunes; tests combustion impulse signature separation. |
| **Toy Gun Pops** | Curated Hard Negative Corpus | 12 | Plastic cap guns and friction poppers; tests ballistic energy and crest factor thresholds. |
| **Balloon Bursts** | Curated Hard Negative Corpus | 12 | Supersonic membrane ruptures; physical shockwave producing real N-waves (acoustic benchmark stress test). |
| **Percussion Transients** | Curated Hard Negative Corpus | 12 | Snare drum rimshots, orchestral woodblocks, castanets; tests musical transient rejection. |
| **Laser Contact Mic Transients**| Curated Hard Negative Corpus | 12 | Piezo and laser surface pickups of structural transients; tests artificial sensor impulse rejection. |
| **Urban Environmental Non-Targets**| ESC-50 Benchmark (9 Diverse Classes) | 180 | 20 recordings each across 9 non-gunshot acoustic classes: coughing, crying babies, barking dogs, emergency sirens, footsteps, helicopter rotors, pouring water, rooster calls, and sea waves. |
| **Total Negatives** | — | **308** | — |

---

## 3. Continuous Acoustic Exposure Corpus ($T=12.0\text{ Hours}$)

The continuous evaluation corpus measures the false alarm rate under realistic, unbroken operational conditions. It consists of 15 distinct streams totaling 12.0 hours of continuous audio:

| Stream Identifier | Campaign / Provenance | Duration | Environment Description |
| :--- | :--- | :---: | :--- |
| `phase17_urban_exterior_plaza_30min.wav` | Phase 17 Field Recording | 0.09 hr (5.5 min) | Open civic pedestrian plaza with foot traffic, distant buses, and fountain water. |
| `phase17_urban_exterior_terrace_30min.wav` | Phase 17 Field Recording | 0.09 hr (5.6 min) | Elevated commercial terrace with ventilation machinery and street traffic. |
| `phase17_urban_exterior_walkway_30min.wav` | Phase 17 Field Recording | 0.10 hr (5.9 min) | Urban covered walkway with reverberant footfalls, conversation, and doors. |
| `phase17_urban_interior_arcade_30min.wav` | Phase 17 Field Recording | 0.11 hr (6.4 min) | Indoor retail shopping arcade with reverberant background chatter and music. |
| `phase17_urban_interior_commercial_30min.wav`| Phase 17 Field Recording | 0.09 hr (5.5 min) | Commercial office concourse with HVAC hum, elevator dings, and foot traffic. |
| `phase17_urban_interior_hall_30min.wav` | Phase 17 Field Recording | 0.09 hr (5.5 min) | High-ceilinged institutional hall with heavy echoes and closing doors. |
| `1_AUDIO_16k.wav` | Phase 27 AeroSonic Aviation Campaign | 1.00 hr | Adelaide Airport (YPAD) perimeter: jet engine spool-ups, taxiing turboprops, wind shear. |
| `2_AUDIO_16k.wav` | Phase 27 AeroSonic Aviation Campaign | 1.00 hr | YPAD perimeter: ground support vehicles, heavy aircraft takeoff roll, reverse thrusters. |
| `3_AUDIO_16k.wav` | Phase 27 AeroSonic Aviation Campaign | 1.00 hr | YPAD perimeter: ambient tarmac idling, baggage tugs, distant highway roar. |
| `4_AUDIO_16k.wav` | Phase 27 AeroSonic Aviation Campaign | 1.00 hr | YPAD perimeter: heavy jet takeoff overflights, aerodynamic wake turbulence. |
| `5_AUDIO_16k.wav` | Phase 27 AeroSonic Aviation Campaign | 1.00 hr | YPAD perimeter: windy apron conditions, ground power units, transient vehicle bumps. |
| `6_AUDIO_16k.wav` | Phase 27 AeroSonic Aviation Campaign | 1.00 hr | YPAD perimeter: regional turboprop operations, maintenance hangar activities. |
| `continuous_stream_01_urban_transit_sirens_1hr.wav` | Phase 8 Acoustic Archive | 1.00 hr | High-density metropolitan traffic, emergency vehicle siren passes, transit buses. |
| `continuous_stream_02_domestic_interior_transients_1hr.wav`| Phase 8 Acoustic Archive | 1.00 hr | Domestic interior: kitchen utensils, cupboard thuds, television dialogue, footsteps. |
| `continuous_stream_03_outdoor_natural_ambience_1hr.wav` | Phase 8 Acoustic Archive | 1.00 hr | Rural outdoor woodland: wind through trees, bird calls, distant road murmur. |
| **Total Exposure** | **3 Distinct Campaigns** | **12.00 hr** | **15 Continuous Audio Streams** |

---

## 4. Signal Standardization & Cryptographic Verification

All 388 evaluation audio files (373 discrete + 15 continuous) were audited using an automated ingest verification pipeline:
1. **Sampling Rate:** Verified at 16,000 Hz single-channel (mono) PCM.
2. **Dynamic Range:** Audited for digital clipping, valid sample amplitude bounds ($-1.0 \le y[n] \le +1.0$), and absence of NaN or Inf values.
3. **Cryptographic Hashes:** Every file was hashed with SHA-256 to establish an unalterable chain of custody and facilitate exact duplicate checking.
4. **Manifest Archival:** All metadata, durations, sample counts, and hashes are permanently recorded in [`phase51_evaluation_manifest.csv`](file:///E:/gunshot/gunshot/experiments/phase51_validation/phase51_evaluation_manifest.csv).

