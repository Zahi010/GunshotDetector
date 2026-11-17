# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY

**MANDATORY SAFETY DESIGNATION:**
This experimental acoustic machine-learning software is uncertified and must never be deployed for autonomous emergency dispatch, tactical police response, active-shooter alerting, automated evacuation, building lockdown, or life-critical physical security.

Use legally obtained recordings and safe audio playback only. Live-fire testing and hazardous acoustic experiments are strictly prohibited.

---

# PHASE 28 TECHNICAL AUDIT REPORT
## AeroSonicDB Dataset License, Institutional Provenance & Acquisition Lineage Audit

**Document Identifier:** `PHASE28-REP-DATASET-LICENSE-PROVENANCE`  
**Phase:** `PHASE_28_INDEPENDENT_REPRODUCTION_CAMPAIGN_STATISTICS_COOLDOWN_FORENSICS`  
**Target Repository:** Zenodo Record `10215080` (AeroSonicDB / YPAD-0523)

---

## 1. Executive Summary

Phase 28 verified the complete legal, institutional, and technical provenance of the **AeroSonicDB** continuous environmental audio archive acquired in Phase 27. 

This audit confirms that:
1. The acquisition strictly utilized official, sanctioned InvenioRDM REST API endpoints without bypassing or evading access controls, CAPTCHAs, or anti-bot challenge gates.
2. The original source archive (`env_audio.zip`) is preserved completely unchanged in `data/phase27/original_archive/` and matches repository checksums exactly.
3. The true license governing the dataset is confirmed as **CC BY-NC 4.0** (Creative Commons Attribution NonCommercial 4.0 International). Research reproduction is authorized, but commercial exploitation is strictly prohibited without separate licensing from the rights holders.
4. Resampling lineage from native 22,050 Hz to detector baseline 16,000 Hz is documented with exact deterministic filter parameters and verified SHA-256 digests.

---

## 2. Institutional and Metadata Ground Truth

| Attribute | Canonical Verified Value | Verification Source |
| :--- | :--- | :--- |
| **Repository Platform** | CERN / Zenodo Open Science Repository | REST API Query `https://zenodo.org/api/records/10215080` |
| **Record Identifier** | `10215080` | Zenodo InvenioRDM Core Database |
| **Concept Identifier** | `8000468` | Zenodo Parent Concept Record |
| **Release Identifier** | `8371595` | Software Release Version |
| **Digital Object Identifier** | `10.5281/zenodo.10215080` | International DOI Foundation Registration |
| **Publication Date** | 2023-11-20 | Zenodo Publication Metadata |
| **Primary Creator** | Blake Downward | University of Adelaide / Independent Acoustic Research |
| **Acknowledged Collaborator**| Jon Nordby | Soundsensing AS (co-author of associated paper) |
| **Associated Publication** | arXiv:2311.06368 | *AeroSonicDB: An aerial acoustic dataset for aircraft detection and classification* |
| **Physical Recording Location**| Adelaide Airport (YPAD) Perimeter, South Australia, AU | Coordinates in `locations.json` (-34.945° S, 138.530° E) |
| **Acoustic Environment** | Civilian Aviation Approach & Urban Ambient | Continuous field environmental loggers |

---

## 3. License Verification and Commercial Restrictions

### 3.1 Creative Commons Attribution NonCommercial 4.0 International (CC BY-NC 4.0)
Inspection of `LICENSE.txt` and the Zenodo metadata confirmed that the archive is distributed under **CC BY-NC 4.0**:
- **Permitted Uses:** Academic research, experimental benchmarking, educational demonstrations, and reproducibility verification.
- **Prohibited Uses:** Commercial deployment, sale, integration into commercial surveillance products, or operational deployment without explicit commercial licensing from Blake Downward.
- **Attribution Requirement:** Any redistribution of results must credit:
  > *Downward, B., & Nordby, J. (2023). AeroSonicDB: An aerial acoustic dataset for aircraft detection and classification. Zenodo. https://doi.org/10.5281/zenodo.10215080*

---

## 4. Archive Checksums and Technical Verification

### 4.1 Original Archive Integrity (`env_audio.zip`)
- **File Path:** `E:/gunshot/gunshot/data/phase27/original_archive/env_audio.zip`
- **Archive Size:** Exactly `495,276,974 bytes` (~472.33 MiB)
- **Repository MD5:** `8c042dc817f459e80ac2491ffc8dd1cd` (**EXACT MATCH**)
- **Computed SHA-256:** `7ebfb4aec3ec41a64db326b7b28789c0d6346a6439182ceb1e9d22f401f3438a`
- **ZIP CRC Test:** `zipfile.testzip()` completed with 0 errors across all archive members.

### 4.2 Extracted Original WAV Files (Native 22,050 Hz)
Stored in `data/phase27/original_audio/env_audio/`:
1. `1_AUDIO.wav`: 158,760,044 B, 79,380,000 samples, 3,600.0s, SHA-256: `846ecdbc6022ce3e0e91f388b5e89178eec413ac79339e1f2cdda4ed83a76481`
2. `2_AUDIO.wav`: 158,760,044 B, 79,380,000 samples, 3,600.0s, SHA-256: `4ea662ff8a68bc0ae848f2257d76a7e0c05763cb88d5509ba249f39446d3ea7e`
3. `3_AUDIO.wav`: 158,760,044 B, 79,380,000 samples, 3,600.0s, SHA-256: `3b80b2a752220f837ceee6db6e6962f92f25b1ea3ea52b48d21b7987e9527ec5`
4. `4_AUDIO.wav`: 158,760,044 B, 79,380,000 samples, 3,600.0s, SHA-256: `00445d47e85c2bca393c5d8a8ee3c23ca41b694602f37a67137fa868875567a9`
5. `5_AUDIO.wav`: 158,760,044 B, 79,380,000 samples, 3,600.0s, SHA-256: `18f77366b51bf30eb8bf5511b8db257ff0e3265541e21b2ddcb221a8d0526e03`
6. `6_AUDIO.wav`: 158,760,044 B, 79,380,000 samples, 3,600.0s, SHA-256: `e06c74fb9d214a1c62f01f11a436e2f1d8c1171761b0c00efaa0ae3df54fbe29`

---

## 5. Resampling Lineage and Derived Audio Verification

### 5.1 Resampling Method
- **Input Parameters:** 16-bit PCM Mono, sample rate $f_{\text{in}} = 22,050\text{ Hz}$.
- **Target Parameters:** 16-bit PCM Mono, sample rate $f_{\text{out}} = 16,000\text{ Hz}$.
- **Rational Resampling Factor:**
  $$\frac{L}{M} = \frac{16,000}{22,050} = \frac{320}{441}$$
- **Algorithm:** Polyphase Kaiser-windowed anti-aliasing FIR filtering via `scipy.signal.resample_poly(arr, 320, 441)`.
- **Amplitude Scaling:** Rescaled to 16-bit signed integer full-scale range $[-32768, 32767]$ with clipping protection.

### 5.2 Derived 16 kHz Audio Files
Stored in `data/phase27/derived_audio/`:
1. `1_AUDIO_16k.wav`: 115,200,044 B, 57,600,000 samples, 3,600.0s, SHA-256: `1b6e241fe31478daf7adcc34880aab7c1d14b27e7061a65d69d01875968948eb`
2. `2_AUDIO_16k.wav`: 115,200,044 B, 57,600,000 samples, 3,600.0s, SHA-256: `57976e196417fae29c0b115450875e4dbca643e2f504cfcfebc00032b4b4594c`
3. `3_AUDIO_16k.wav`: 115,200,044 B, 57,600,000 samples, 3,600.0s, SHA-256: `785d18d451722e0e01ea3ee1dd85ec6696dbf20227926c0a0c9a7fc0a8a66205`
4. `4_AUDIO_16k.wav`: 115,200,044 B, 57,600,000 samples, 3,600.0s, SHA-256: `fdb37603c4f2bb1a09d3ee971fc0575d164d1f5d21a9954a1be213b190f84897`
5. `5_AUDIO_16k.wav`: 115,200,044 B, 57,600,000 samples, 3,600.0s, SHA-256: `fcbb2076211116c9fc6ae9bb2d744b82bc207038bb1090172bf43f25c76cc782`
6. `6_AUDIO_16k.wav`: 115,200,044 B, 57,600,000 samples, 3,600.0s, SHA-256: `09b6a22f3e8b4e72780e8e63080ff9f9ce6368d37446ca39ba99fb9e116e0b7a`

All original and derived files are preserved intact. Processing lineage is 100% deterministic and fully reproducible.

