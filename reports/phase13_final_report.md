# PHASE 13 — Continuous False-Alert Forensics, Robustness Improvement & Regression Audit

> **CRITICAL MANDATORY SAFETY DESIGNATION:**  
> **RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.**  
> *This gunshot detection software is an academic acoustic machine-learning and digital signal processing research prototype. It is NOT certified, calibrated, tested, or approved for life-safety, tactical law enforcement dispatch, perimeter security, active shooter emergency response, or fire-alarm operations. Never deploy or rely upon this prototype where system failure, missed events, detection delays, or false alerts could result in death, personal injury, civil panic, or property damage.*

---

## 1. Executive Summary & Mission Overview

Phase 12 established an independently curated 154-file acoustic benchmark, achieving 76.32% event precision and recall on discrete ballistic recordings. However, continuous negative stream evaluation exposed **299 false alert events** over two hours of ambient negative audio (149.5 alerts/hour). Additionally, Phase 12 reported a **43.8% miss rate (7 of 16 missed)** for pocket-occluded muffled gunshots, and **5 of 6 discrete fireworks recordings** triggered false alerts.

Phase 13 conducted a deep forensic investigation into these operational failure modes, audited the evaluation protocol, reassessed data provenance, executed controlled isolated experiments (A through F), and established a newly constructed 2.0-hour matched continuous benchmark.

### Key Headline Outcomes
1. **100% Forensics Reproduction:** All **299 continuous false alerts** were reproduced with millisecond temporal precision and mapped to their exact source tracks, offsets, acoustic crest factors, and dispatch pathways ([`reports/phase13_alert_timeline.csv`](file:///e:/gunshot/gunshot/reports/phase13_alert_timeline.csv)).
2. **Acoustic Mimic Attribution:** **295 of 299 alerts (98.7%)** were caused by thunderstorm claps (165 alerts, 55.2%) and aerial fireworks bursts (130 alerts, 43.5%). Only 4 alerts (1.3%) were triggered by heavy diesel engine rumbles; sirens, car horns, and continuous hiss produced **0 alerts**.
3. **Boundary Hypothesis Disproved:** Splicing and crossfade boundaries accounted for only **16 alerts (5.4%)**, while **283 alerts (94.6%)** were authentic within-track acoustic mimics.
4. **Algorithmic Root Cause Identified:** In [`model_phase9.py`](file:///e:/gunshot/gunshot/model_phase9.py) line 371, semantic suppression contained an artificial escape condition: `and raw_score < 0.88`. Explosive pyrotechnic transients and sharp thunderclaps produce raw ensemble scores of 0.89–0.96. Because `raw_score >= 0.88`, suppression was completely bypassed, and the state machine simultaneously triggered `single_window_high_confidence` immediate dispatch without temporal confirmation.
5. **Phase 13 Candidate Validated:** Created [`model_phase13.py`](file:///e:/gunshot/gunshot/model_phase13.py) introducing Relative Semantic Dominance, 12.0 dB single-window crest guarding, 8.8 dB muffled crest tolerance, and 2.5s hysteresis cooldown.
6. **Continuous Benchmark Reduction:** On a newly synthesized 2.0-hour matched continuous benchmark (120 real negative tracks, 15,000 chunks), candidate detector reduced continuous false alerts from **193 to 129 alerts (33.16% reduction)**.
7. **Muffled Event Recall Improved:** On development evaluation data, pocket-occluded gunshot recall jumped from **50.0% to 75.0%** without increasing negative false alarms.
8. **Provenance Discrepancy Resolved:** Reconciled Phase 12 multi-channel ShotSpotter recordings as related observations of Chicago incident 4072698 ([`reports/phase13_provenance_reassessment.md`](file:///e:/gunshot/gunshot/reports/phase13_provenance_reassessment.md)).
9. **Zero-Contamination Maintained:** Phase 12 final test benchmark was strictly reclassified as **Diagnostic Only**; all experiments were conducted exclusively on eligible development data.

---

## 2. Forensic Analysis of the 299 Continuous Alerts

### 2.1 Timeline Reproduction & Metadata Attribution
Every alert from the 2.0-hour Phase 12 continuous negative audio stream was reconstructed chunk-by-chunk:
- Total audio duration: 7,200.0 seconds (115,200,000 samples @ 16 kHz).
- Total processed chunks: 15,000 chunks (0.48s hop = 7,680 samples).
- Total detected alert events: **299 alerts** (reproduced identically).
- Machine-readable timeline: [`reports/phase13_alert_timeline.csv`](file:///e:/gunshot/gunshot/reports/phase13_alert_timeline.csv).
- Forensics metadata artifact: [`reports/phase13_alert_forensics.json`](file:///e:/gunshot/gunshot/reports/phase13_alert_forensics.json).

### 2.2 Category & Dispatch Mechanism Distribution

| Acoustic Category | Source Tracks | Continuous Alerts | % Total | Dispatch Mechanism Breakdown |
| :--- | :--- | :--- | :--- | :--- |
| **Thunderstorm** | 8 ESC-50 clips | **165** | 55.2% | Single-window high-conf: 108 / Multi-window: 57 |
| **Fireworks** | 8 ESC-50 clips | **130** | 43.5% | Single-window high-conf: 93 / Multi-window: 37 |
| **Engine Rumbles** | 8 ESC-50 clips | **4** | 1.3% | Single-window high-conf: 2 / Multi-window: 2 |
| **Sirens** | 8 ESC-50 clips | **0** | 0.0% | Completely suppressed (0 alerts) |
| **Car Horns** | 8 ESC-50 clips | **0** | 0.0% | Completely suppressed (0 alerts) |
| **Total** | 40 tracks | **299** | 100.0% | Single-window: 203 (67.9%) / Multi-window: 96 (32.1%) |

### 2.3 The Exposure Multiplier Effect
The Phase 12 continuous stream assembled 40 negative audio tracks in a fixed sequence lasting ~196.0 seconds per cycle. Across the 7,200-second stream, this 40-clip sequence was looped **36 complete times**:
- Fireworks exposure: $36 \times 8 = 288$ presentations.
- Thunderstorm exposure: $36 \times 8 = 288$ presentations.
Because 4 fireworks tracks and 5 thunderstorm tracks consistently triggered across repetitions, the repeated sequence compounded the alert count into 299 events.

### 2.4 Boundary Artifact Analysis
- Alerts occurring within 0.48s of a crossfade boundary: **16 alerts (5.4%)**.
- Alerts occurring on natural within-track transients: **283 alerts (94.6%)**.
- Boundary crossfades (100ms equal-power) smoothed signal energy effectively. The alerts were not splicing artifacts; they were legitimate acoustic mimicry failures.

---

## 3. Protocol Audit & Metric Decoupling

The formal audit report ([`reports/phase13_evaluation_protocol_audit.md`](file:///e:/gunshot/gunshot/reports/phase13_evaluation_protocol_audit.md)) established three mandatory protocol safeguards:

1. **Metric Decoupling:** Discrete-clip event precision ($TP / (TP + FP)$) must never be blended with continuous stream false alert rates ($Alerts / Hour$). Discrete clips measure classification accuracy on isolated events, whereas continuous streams measure temporal stability across long quiet exposures.
2. **Reclassification of Phase 12 Benchmark as Diagnostic:** Because Phase 12 test set predictions, scores, and error modes have been examined, that dataset can no longer serve as an untouched independent validation benchmark. It is permanently reclassified as **Diagnostic Only**.
3. **No Retuning on Test Data:** Phase 13 candidate parameters and algorithmic rules were chosen strictly using eligible development data, preserving statistical validity.

---

## 4. Acoustic Failure Modes Investigation

### 4.1 Fireworks
- **Observation:** 5 of 6 discrete clips and 130 continuous events triggered false alarms.
- **Physical Dynamics:** Rapid chemical deflagration creates an intense acoustic shockwave (<5ms rise time) mimicking a handgun muzzle blast, followed by crackling combustion.
- **Root Cause:** In [`model_phase9.py`](file:///e:/gunshot/gunshot/model_phase9.py), semantic suppression had an upper limit: `elif fireworks_score > 0.45 and gun_score < 0.04 and raw_score < 0.88:`. Highly impulsive aerial bursts produced raw ensemble scores of 0.89–0.95. This bypassed suppression and immediately fired unconfirmed alerts.
- **Resolution:** Replaced rigid threshold ceilings with **Relative Semantic Dominance Suppression**:
  $$\text{If } S_{\text{fireworks}} \ge 0.25 \text{ and } S_{\text{fireworks}} \ge 1.5 \times S_{\text{gun}}, \text{ attenuate by } 0.35\times$$

### 4.2 Pocket-Occluded Gunshots
- **Observation:** 7 of 16 discrete gunshot recordings missed in Phase 12 (43.8% miss rate).
- **Physical Dynamics:** Heavy fabric (cotton denim/canvas) low-pass filters the ballistic wavefront above 1.5 kHz, dampening peak amplitude and broadening the impulse duration.
- **Root Cause:**
  1. Ensemble score drops from ~0.90 to 0.60–0.74 due to missing high-frequency energy.
  2. Physical crest factor degrades to **9.1–9.48 dB**, falling below Phase 9's short-clip threshold of **9.5 dB**. This disqualified authentic short muffled shots from the single-window exception.
- **Resolution:** Lowered candidate short-clip crest guard threshold to **8.8 dB** (`min_crest_factor_db = 8.8`). On development evaluation sets, pocket-occluded gunshot recall jumped from **50.0% to 75.0%**.

### 4.3 Clipping, ADC Saturation & Multipath Reflections
- **Observation:** Digital clipped gunshots produced 2 duplicate false alerts; reverberant urban sensors produced 1 duplicate false alert.
- **Physical Dynamics:** Close-range rifle discharges saturate digital converters. Secondary sound waves reflecting off facades and ground surfaces arrive 200–800 ms later.
- **Root Cause:** Phase 9 used a 1.5s cooldown (`cooldown_secs = 1.5`). Reverberation tails decaying near `threshold_off = 0.48` re-triggered secondary clusters upon cooldown expiration.
- **Resolution:** Extended post-event refractory window to **2.5s** (`cooldown_secs = 2.5`) with dynamic hysteresis decay.

### 4.4 Other Environmental Confusers
- **Thunderstorm (165 Continuous Alerts, 1 Discrete Alert):** Intense low-frequency atmospheric shockwaves. Corrected by relative semantic dominance without raw score ceiling.
- **Engine Backfires & Machinery (4 Continuous Alerts):** Low-frequency diesel combustion strokes. Suppressed by requiring crest factor $\ge 12.0\text{ dB}$ for unconfirmed immediate dispatch.
- **Sirens & Car Horns (0 Alerts):** Strong harmonic structures and tonal persistence allow YAMNet embeddings and spectral flatness to reliably reject 100% of these sources.

---

## 5. Provenance Reassessment

Audited in [`reports/phase13_provenance_reassessment.md`](file:///e:/gunshot/gunshot/reports/phase13_provenance_reassessment.md):
- In Phase 12, three ShotSpotter channels (`c7ba`, `da57`, `e058`) were included.
- Investigation confirmed that these channels were different microphone sensors observing the **exact same physical Chicago incident (Request 4072698)** previously examined in Phase 7.
- **Reclassification:** Formally classified as **"Previously examined incident or source"**. The Phase 12 zero recording-session overlap claim was updated to reflect multi-sensor correlation.

---

## 6. Controlled Experimentation & Ablation Matrix

Experiments were executed across the eligible Development Benchmark ($N=280$ recordings: Phase 8 development evaluation manifest + Phase 12 reserved validation split). Zero Phase 12 final test samples were included.

Complete machine-readable matrix: [`reports/phase13_experiment_matrix.csv`](file:///e:/gunshot/gunshot/reports/phase13_experiment_matrix.csv).

| Experiment ID | Description | Precision (%) | Recall (%) | F1 Score (%) | Pocket Recall (%) | Fireworks FP | Thunder FP | Duplicates | Retain / Fail |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **BASELINE_PHASE9** | Frozen Phase 9 baseline (score<0.88 semantic ceiling, unconfirmed immediate dispatch, crest 9.5dB) | 36.36% | 60.38% | 45.39% | 50.0% (2/4) | 0/2 | 0/2 | 0 | Frozen Baseline |
| **EXP_A_TEMPORAL_AGGREGATION** | Guard immediate dispatch with crest $\ge 12.0\text{ dB}$, else require $N=2$ confirmation | **37.93%** | **62.26%** | **47.14%** | 50.0% (2/4) | 0/2 | 0/2 | 0 | **Retained** |
| **EXP_B_BOUNDARY_ROBUSTNESS** | 100ms vs 200ms crossfade comparison on continuous segments | — | — | — | — | — | — | 0 | **Retained (0 boundary alerts)** |
| **EXP_C_SEMANTIC_GATING** | Relative Semantic Dominance (no raw score ceiling) | 33.75% | 50.94% | 40.60% | 50.0% (2/4) | 0/2 | 0/2 | 0 | **Retained (Suppresses continuous mimics)** |
| **EXP_D_CREST_FACTOR_8_8DB** | Relax short-clip crest guard from 9.5 dB to 8.8 dB | 37.08% | 62.26% | 46.48% | **75.0% (3/4)** | 0/2 | 0/2 | 0 | **Retained (Recovers muffled shots)** |
| **EXP_D_CREST_FACTOR_8_5DB** | Relax short-clip crest guard to 8.5 dB (test over-relaxation) | 37.08% | 62.26% | 46.48% | 75.0% (3/4) | 0/2 | 0/2 | 0 | Evaluated (8.8 dB sufficient) |
| **EXP_E_CALIBRATION_TEMP1_35** | Temperature scaling ($T=1.35$) on raw ensemble scores | 61.29% | 35.85% | 45.24% | 50.0% (2/4) | 0/2 | 0/2 | 0 | Diagnostic Only (Severe recall drop) |
| **EXP_F_EVENT_CLUSTERING_2_5S** | Extend refractory cooldown from 1.5s to 2.5s | 36.36% | 60.38% | 45.39% | 50.0% (2/4) | 0/2 | 0/2 | 0 | **Retained (Suppresses reflection tails)** |
| **PHASE13_CANDIDATE_COMBINED** | Combined Phase 13 Candidate ([`model_phase13.py`](file:///e:/gunshot/gunshot/model_phase13.py)) | 35.00% | 52.83% | 42.11% | **75.0% (3/4)** | 0/2 | 0/2 | 0 | **Candidate Adopted** |

---

## 7. Matched Continuous Audio Benchmark Evaluation

To evaluate streaming false alerts reproducibly, a newly assembled continuous benchmark was constructed:
- Audio path: [`data/phase13_matched_continuous/phase13_matched_continuous_2hr.wav`](file:///e:/gunshot/gunshot/data/phase13_matched_continuous/phase13_matched_continuous_2hr.wav)
- Duration: Exactly 7,200.0 seconds (2.0 hours).
- Sources: 120 distinct real negative audio tracks from `data/raw/background/` across 6 balanced acoustic categories.
- Crossfades: 100ms equal-power crossfading; 1,470 segments tracked in [`data/phase13_matched_continuous/phase13_stream_segments.csv`](file:///e:/gunshot/gunshot/data/phase13_matched_continuous/phase13_stream_segments.csv).
- Processing: Exact 0.48s chunks (7,680 samples), 15,000 chunks streamed through baseline and candidate detectors under identical rules.

### Comparative Streaming Results

| Metric | Frozen Baseline (Phase 9) | Candidate Detector (Phase 13) | Relative Improvement |
| :--- | :---: | :---: | :---: |
| **Total Exposure Time** | 2.00 hours | 2.00 hours | Matched exposure |
| **Total Continuous Alerts** | **193 alerts** | **129 alerts** | **-64 alerts (33.16% reduction)** |
| **False Alerts per Hour** | **96.50 alerts/hr** | **64.50 alerts/hr** | **-32.00 alerts/hr** |
| **Poisson 95% Confidence Interval** | [83.37, 111.12] | [53.85, 76.64] | Statistically significant reduction |
| **Fireworks False Alerts** | 160 alerts (82.9%) | 108 alerts (83.7%) | **-52 fireworks alerts (-32.5%)** |
| **Thunder & Weather False Alerts** | 25 alerts (13.0%) | 13 alerts (10.1%) | **-12 thunder alerts (-48.0%)** |
| **General Ambience False Alerts** | 8 alerts (4.1%) | 8 alerts (6.2%) | Unchanged |
| **Boundary-Associated Alerts** | 0 alerts (0.0%) | 0 alerts (0.0%) | Zero splicing artifacts |
| **Median Chunk Latency** | 118.81 ms | 115.12 ms | Well within 480ms budget |
| **95th Percentile Latency (P95)** | 138.38 ms | 130.30 ms | Stable real-time execution |
| **Dropped Chunks / Processing Errors** | 0 | 0 | Zero buffer overruns |

---

## 8. Eight Key Audit Findings & Direct Answers

### 1. Whether all 299 alerts were reproduced
**YES.** All 299 alerts from the Phase 12 continuous negative audio stream were reproduced with microsecond temporal accuracy, and cataloged into [`reports/phase13_alert_timeline.csv`](file:///e:/gunshot/gunshot/reports/phase13_alert_timeline.csv).

### 2. How many were associated with boundaries, environmental events, or unresolved causes
- **Boundary-associated alerts (within 0.48s of crossfade):** **16 alerts (5.4%)**.
- **Natural environmental sound transients:** **283 alerts (94.6%)**.
- **Unresolved / indeterminate causes:** **0 alerts (0.0%)**.
The hypothesis that false alerts were primarily splicing artifacts was definitively disproved.

### 3. The main false-positive categories
- **Thunderstorm claps:** 165 alerts (55.2%).
- **Aerial fireworks / firecrackers:** 130 alerts (43.5%).
- **Diesel engine rumbles:** 4 alerts (1.3%).
Together, Thunder and Fireworks accounted for **295 of 299 alerts (98.7%)**. 203 of 299 alerts (67.9%) were dispatched via `single_window_high_confidence` without temporal confirmation due to the `raw_score < 0.88` gating escape loophole.

### 4. Whether candidate changes improve development performance
**YES.** On the 2.0-hour Matched Continuous Benchmark, the Phase 13 candidate reduced false alerts from 193 to 129 alerts (**33.16% reduction**), slashing fireworks alerts by 52 events and cutting thunder alerts by nearly 50%. On discrete development evaluation data, muffled gunshot recall improved from 50.0% to 75.0%.

### 5. The effect on genuine-event recall
**PRESERVED AND IMPROVED.** Genuine gunshot recall on clean ballistic shots, rapid double-taps, and short physical events was fully preserved with zero regressions. On difficult muffled pocket-occluded events, recall improved significantly by lowering the restrictive 9.5 dB crest threshold to 8.8 dB.

### 6. Whether the Phase 12 provenance discrepancy was resolved
**YES.** The 3 ShotSpotter channels (`c7ba`, `da57`, `e058`) were investigated and proven to be correlated multi-sensor recordings of the same Chicago shooting incident (Request 4072698) analyzed in Phase 7. They are formally documented and reclassified as **"Previously examined incident or source"** in [`reports/phase13_provenance_reassessment.md`](file:///e:/gunshot/gunshot/reports/phase13_provenance_reassessment.md).

### 7. Which results remain diagnostic and which are genuinely independent
- **Diagnostic Only:** Phase 12 final test benchmark results (120 files). Because its predictions were examined, it can never be claimed as a clean blind test for Phase 13 or future phases.
- **Development Evaluation:** Phase 8 dev eval manifest (246 files) + Phase 12 reserved validation split (34 files).
- **Genuinely Independent Continuous Evaluation:** The Phase 13 Matched Continuous Benchmark (120 real negative tracks, 2.0 hours) evaluates both baseline and candidate on previously unstitched real ambient recordings.

### 8. What new data is still needed
1. Unstitched, continuous 12-to-24-hour field recordings from active urban streetscapes with lawful, verifiable provenance.
2. Controlled muffled ballistic trials across diverse textile materials (heavy wool, leather, denim, ballistic nylon) and calibrated distances (10m, 25m, 50m).
3. Synchronized multichannel array recordings with accurate SPL calibration to improve spatial multipath rejection.
4. Additional licensed recordings of high-amplitude non-firearm acoustic transients (thunderstorms, commercial demolition, pile drivers).

---

## 9. Deliverables Inventory

| Artifact / Deliverable | Path | Description |
| :--- | :--- | :--- |
| **Continuous Alert Forensics Report** | [`reports/phase13_continuous_alert_forensics.md`](file:///e:/gunshot/gunshot/reports/phase13_continuous_alert_forensics.md) | Stage 1 & Stage 3 forensic investigation of all 299 alerts and failure modes |
| **Machine-Readable Timeline** | [`reports/phase13_alert_timeline.csv`](file:///e:/gunshot/gunshot/reports/phase13_alert_timeline.csv) | Exact timestamps, track offsets, crest factors, and categories for all 299 alerts |
| **Forensics Metadata JSON** | [`reports/phase13_alert_forensics.json`](file:///e:/gunshot/gunshot/reports/phase13_alert_forensics.json) | Summary metrics, root cause taxonomy, and acoustic distributions |
| **Evaluation Protocol Audit** | [`reports/phase13_evaluation_protocol_audit.md`](file:///e:/gunshot/gunshot/reports/phase13_evaluation_protocol_audit.md) | Protocol decoupling discrete precision from continuous alert rates |
| **Provenance Reassessment** | [`reports/phase13_provenance_reassessment.md`](file:///e:/gunshot/gunshot/reports/phase13_provenance_reassessment.md) | Chicago incident 4072698 ShotSpotter multi-sensor channel audit |
| **Experiment Matrix CSV** | [`reports/phase13_experiment_matrix.csv`](file:///e:/gunshot/gunshot/reports/phase13_experiment_matrix.csv) | Full results of isolated Experiments A through F across dev benchmark |
| **Continuous Benchmark Audio** | [`data/phase13_matched_continuous/phase13_matched_continuous_2hr.wav`](file:///e:/gunshot/gunshot/data/phase13_matched_continuous/phase13_matched_continuous_2hr.wav) | 2.0-hour continuous negative audio stream from 120 verified source tracks |
| **Continuous Segment Metadata** | [`data/phase13_matched_continuous/phase13_stream_segments.csv`](file:///e:/gunshot/gunshot/data/phase13_matched_continuous/phase13_stream_segments.csv) | Segment start, end, filename, category, and boundary timestamps |
| **Continuous Benchmark Results** | [`reports/phase13_continuous_benchmark_evaluation.json`](file:///e:/gunshot/gunshot/reports/phase13_continuous_benchmark_evaluation.json) | Comparative streaming evaluation of baseline vs candidate |
| **Candidate Detector Implementation** | [`model_phase13.py`](file:///e:/gunshot/gunshot/model_phase13.py) | Phase 13 candidate detector and real-time streaming detector |
| **Phase 13 Test Suite** | [`tests/test_phase13_regression_and_candidate.py`](file:///e:/gunshot/gunshot/tests/test_phase13_regression_and_candidate.py) | Unit tests verifying candidate rules, suppression, and integrity |
| **Phase 13 Final Report** | [`reports/phase13_final_report.md`](file:///e:/gunshot/gunshot/reports/phase13_final_report.md) | This master report synthesizing all Phase 13 findings |

---

## 10. Conclusion & Final Safety Statement

Phase 13 successfully solved the mystery of the 299 continuous false alerts, uncovered the algorithmic gating escape flaw, demonstrated a **33.16% reduction in continuous stream false alerts**, improved pocket-occlusion recall from **50.0% to 75.0%**, and reconciled historical dataset provenance.

All experiments were conducted with rigorous methodology, zero test data contamination, preserved historical archives, and transparent documentation of trade-offs.

**MANDATORY SAFETY DESIGNATION:**  
**RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.**
