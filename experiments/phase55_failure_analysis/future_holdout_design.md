# Phase 55 — Future Independent Holdout Corpus Specification

**MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.**

*This uncertified research prototype must never be deployed for autonomous emergency dispatch, tactical police response, active-shooter alerting, automated evacuation, building lockdown, or life-critical physical security.*

---

## 1. Executive Summary

A critical lesson established across Phase 51, Phase 54, and Phase 55 is that **detector qualification requires an untouchable, rigorously curated, cryptographically sealed holdout corpus**.

Phase 54 exposed severe failure modes in V10 that were previously invisible in training partitions:
- Fireworks FPR reached 73.33% (22/30).
- Balloon burst FPR reached 57.14% (4/7).
- Occluded and low-gain positive gunshots suffered 38.5% false-negative rates due to dynamic range dampening.

To prevent benchmark overfitting and guarantee that future candidates (such as learned rejection models) are evaluated with scientific rigor, this document defines the formal specification, acoustic composition, and quarantine protocols for the **Phase 56 / Future Qualification Holdout Corpus**.

---

## 2. Corpus Architecture & Composition

The future evaluation benchmark will comprise exactly **$N = 500$ lawfully curated audio recordings** spanning 200 genuine gunshot events and 300 challenge negative acoustic events.

```
Total Evaluation Corpus: N = 500
├── Positive Gunshot Recordings: N = 200 (40.0%)
│   ├── Outdoor Direct-Path Ballistics (Handguns, Rifles, Shotguns): 80 (16.0%)
│   ├── Indoor & Enclosed Reverberant Firearm Discharges: 40 (8.0%)
│   ├── Degraded, Pocket-Occluded & Distant Discharges (> 100m): 50 (10.0%)
│   └── Low-Gain / Highly Attenuated Waveforms (Peak < -18 dBFS): 30 (6.0%)
│
└── Challenge Negative Recordings: N = 300 (60.0%)
    ├── Fireworks & Pyrotechnics (Aerial Shells, Bottle Rockets, Mortars): 60 (12.0%)
    ├── Heavy Mechanical Impacts (Metal Hammers, Industrial Drops): 40 (8.0%)
    ├── Door Slams & Elevator Gates: 30 (6.0%)
    ├── Balloon Bursts (Diverse volumes, rubber tensions, room sizes): 30 (6.0%)
    ├── Glass Shattering, Impacts & Rolling Bottles: 30 (6.0%)
    ├── Atmospheric Thunder & Lightning Cracks: 30 (6.0%)
    ├── Automotive Backfires & Engine Transients: 30 (6.0%)
    ├── Urban Ambience, Rail Transit & Siren Screeches: 25 (5.0%)
    └── Bioacoustics (Human Screams, Coughs, Dog Barks, Hand Claps): 25 (5.0%)
```

---

## 3. Acoustic Quality and Realism Requirements

To ensure direct applicability to physical microphone edge devices, all curated audio must adhere to strict acoustic standards:

1. **Native Transducer Diversity:**
   - At least 35% of recordings must originate from mobile phone or low-cost MEMS electret microphones.
   - High-fidelity studio recordings must not exceed 25% of the total dataset.
2. **Codec and Bitrate Variation:**
   - Raw audio must include lossy web codecs (AAC, MP3, Opus at 64 kbps to 320 kbps) as well as uncompressed PCM WAV, reflecting real-world streaming audio conditions.
3. **Dynamic Range & Noise Floor:**
   - Signal-to-Noise Ratio (SNR) must span from $-6\text{ dB}$ (heavily masked in ambient urban noise) up to $+35\text{ dB}$ (clean close-proximity captures).
   - Recordings must include varying room reverberation times ($RT_{60}$ from 0.1s to 2.5s).

---

## 4. Cryptographic Quarantine & Leakage Prevention Protocol

To maintain absolute independence and prevent data leakage:

1. **Cryptographic Sealing:**
   - Upon final curation, SHA-256 hashes for all 500 audio files will be compiled into `sealed_holdout_manifest.json` and signed with a read-only lock.
2. **Zero-Access Quarantine:**
   - The holdout directory will be strictly quarantined in an isolated, read-protected path.
   - Automated test scripts, hyperparameter tuning loops, feature selection pipelines, and threshold optimization routines are strictly forbidden from accessing this path.
3. **Single-Pass Final Qualification:**
   - The holdout may be loaded **exactly once** during the formal candidate qualification phase.
   - If a candidate fails qualification, the holdout cannot be reused for iterative tuning; any subsequent re-qualification requires new non-overlapping evaluation partitions.

---

## 5. Qualification Pass / Fail Criteria

To achieve formal qualification for physical demonstration readiness, a candidate detector must satisfy all of the following empirical criteria simultaneously:

| Metric | Minimum Qualification Threshold | Phase 54 V10 Baseline | Requirement Status |
| :--- | :---: | :---: | :---: |
| **Combined Positive Recall** | $\ge \mathbf{85.0\%}$ | 70.90% (95/134) | Mandatory |
| **Occluded / Degraded Recall** | $\ge \mathbf{75.0\%}$ | 61.5% | Mandatory |
| **Total Challenge Negative FPR** | $\le \mathbf{3.0\%}$ | 22.12% (48/217) | Mandatory |
| **Fireworks False-Positive Rate** | $\le \mathbf{5.0\%}$ | 73.33% (22/30) | Mandatory |
| **Balloon Burst False-Positive Rate** | $\le \mathbf{5.0\%}$ | 57.14% (4/7) | Mandatory |
| **Continuous Audio False Alert Rate**| $\le \mathbf{0.25\text{ alerts/hour}}$ | 0.732 alerts/hour | Mandatory |
| **Mean Stream Processing Latency** | $\le \mathbf{25.0\text{ ms/chunk}}$ | 12.50 ms/chunk | Mandatory |
| **Dropped Processing Windows** | $\mathbf{0\text{ dropped chunks}}$ | 0 dropped chunks | Mandatory |

