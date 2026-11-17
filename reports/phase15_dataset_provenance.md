# Phase 15 Dataset Provenance & Acoustic Inventory Audit

**Safety Designation: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.**

This document provides complete provenance tracking, licensing documentation, acoustic parameter characterization, and physical event boundaries for the Phase 15 Independent Acoustic Benchmark.

---

## 1. Provenance Verification Protocol

To prevent evaluation leakage and confirm generalization:
1. Every newly downloaded audio file was hashed using SHA-256 on the binary asset and SHA-256 on raw 16-bit PCM decoded mono 16 kHz audio.
2. Hashes were cross-referenced against all 10 historical project manifests (Phases 1 through 14).
3. 42 Mitchell et al. testing gunshot recordings were confirmed to have **zero historical exposure** in any phase.
4. 5 ShotSpotter recordings (Incident 556267 District 5 sensors and ScepterTest) were identified as having been examined in Phase 7. As required by Phase 15 Section 3, their historical provenance was explicitly disclosed and they were classified as `HISTORICALLY_USED` and locked into `diagnostic_only` partition.
5. All 100 discrete negative confusers were audited and verified as 100% `SOURCE_INDEPENDENT`.
6. The 2.0-hour continuous negative evaluation stream was constructed from 1,440 distinct ESC-50 tracks with zero reuse of the Phase 13/14 continuous benchmark files and zero looping.

---

## 2. Acoustic Regimes in Phase 15 Positives

The 47 positive gunshot recordings span four critical operational regimes:

1. **Pocket-Occluded Muffled Gunfire (18 recordings - 100% Source Independent):**
   - High-SPL ballistic impulses muffled by denim, cotton, and polyester fabrics.
   - Significant high-frequency attenuation (>4 kHz) and reduced acoustic crest factor (mean 12.4 dB).
   - Solves the sample size limitation of Phase 14 (which had only 4 pocket recordings).
2. **Clean Ballistic Range Shots (18 recordings - 100% Source Independent):**
   - Direct line-of-sight AR-15 .223 rifle and Beretta 92FS 9mm handgun discharges.
   - Single shots and rapid double-taps recorded at 7–10 meters.
3. **Digital Clipped High-SPL Saturation (6 recordings - 100% Source Independent):**
   - ADC saturation / hard-clipping at acoustic microphone diaphragm, generating high-frequency harmonic distortion.
4. **Real Urban Acoustic Gunfire Sensors (5 recordings - Historically Used / Diagnostic):**
   - ShotSpotter Chicago District 5 Incident 556267 multi-sensor recordings with street reverberation and building reflections.

---

## 3. Discrete Dataset Inventory Summary

- **Total Files:** 152
- **Confirmed Positives (`ground_truth_label = 1`):** 47 (42 Source Independent, 5 Historically Used)
- **Confirmed Negatives (`ground_truth_label = 0`):** 100 (100% Source Independent)
- **Ambiguous Edge Cases (`ground_truth_label = -1`):** 5 (100% Source Independent)

### Category Breakdown of Negatives (100 Files)
- **Mechanical Impulsive Mimics (12 files):** Tool drops, metal impacts, door slams from firearm range environments.
- **Ambient Transient Mimics (38 files):** Shouting, speech clatter, footsteps, environmental transient noises.
- **Pyrotechnics / Fireworks (10 files):** Aerial mortar shells, ground crackers, bottle rockets.
- **Thunderstorms (10 files):** Sharp thunderclaps, rolling atmospheric rumble, heavy rain transients.
- **Engine & Transportation (10 files):** Heavy diesel engines, motorcycle revs, train brakes, propeller aircraft.
- **Glass Breaking & Impacts (10 files):** Shattering plate glass, window breaks, bottle smashes.
- **Clapping & Crowd Clatter (10 files):** Sudden rhythmic hand clapping, outdoor crowd applause.

---

## 4. Continuous Evaluation Stream Inventory

- **File Location:** `data/phase15_independent_eval/continuous/phase15_independent_continuous_2hr.wav`
- **Duration:** Exactly 7,200.00 seconds (2.00 hours)
- **Source Dataset:** Karol Piczak ESC-50 Environmental Sound Classification Benchmark (Open Access / CC-BY-NC 3.0)
- **Track Selection:** 1,440 completely unexamined tracks sampled across 40+ non-gunshot acoustic classes.
- **Boundary Transition Tracking:** 1,439 boundary timestamps recorded in `reports/phase15_stream_segments.csv`.

---

## 5. Provenance Audit Conclusion

The Phase 15 evaluation dataset satisfies all independence, non-contamination, and split integrity criteria. No candidate model has been tuned or selected using the blind evaluation set.
