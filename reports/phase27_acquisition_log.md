# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY

**MANDATORY SAFETY DESIGNATION:**
This experimental acoustic machine-learning software is uncertified and must never be deployed for autonomous emergency dispatch, tactical police response, active-shooter alerting, automated evacuation, building lockdown, or life-critical physical security.

Use legally obtained recordings and safe audio playback only. Live-fire testing and hazardous acoustic experiments are strictly prohibited.


# PHASE 27 — AUTHORIZED DATA ACQUISITION AND INGESTION LOG

## 1. Executive Summary
Phase 27 executed the lawful, authorized acquisition and continuous ingestion of the **AeroSonicDB / YPAD-0523** environmental audio archive (`env_audio.zip`) from Zenodo (Record ID `10215080`, Concept `8000468`, Release `8371595`). 

In Phase 26, automated scrapers targeting web URLs (`https://zenodo.org/record/10215080/files/env_audio.zip`) received HTTP 403 Forbidden responses due to Cloudflare anti-bot bot-management challenges. In strict compliance with guidelines prohibiting anti-bot evasion, scraping was halted. In Phase 27, inquiry established that CERN/Zenodo InvenioRDM officially exposes open REST API endpoints designed specifically for automated research retrieval (`https://zenodo.org/api/records/10215080/files/env_audio.zip/content`). This sanctioned API route completed with HTTP 200 without bypassing, spoofing, or encountering any anti-bot challenge.

## 2. Preflight Storage Audit
- **Target Volume:** `E:`
- **Free Space Available Prior to Download:** 73.37 GB (78,781,775,872 bytes)
- **Minimum Required Space:** 6.0 GB (Archive: ~0.5 GB, Extracted Audio: ~1.0 GB, Resampled Audio: ~0.7 GB)
- **Margin of Safety:** > 12x required storage capacity
- **Preflight Determination:** APPROVED.

## 3. Metadata and Source Verification
- **Zenodo API Query:** `https://zenodo.org/api/records/10215080`
- **Record Title:** AeroSonicDB: An aerial acoustic dataset for aircraft detection and classification
- **Creators:** Blake Downward (acknowledged Jon Nordby, Soundsensing AS)
- **Publication Date:** 2023-11-20
- **True License:** **CC BY-NC 4.0** (Creative Commons Attribution NonCommercial 4.0 International). *Note: Phase 26 literature review listed CC BY 4.0; empirical audit confirms the restrictive NonCommercial clause.*
- **Associated Publication:** arXiv:2311.06368
- **Auxiliary Files Retrieved:**
  - `README.md` (1,058 B)
  - `LICENSE.txt` (19,446 B)
  - `locations.json` (1,085 B)
  - `environment_class_mappings.csv` (106 B)
  - `environment_mappings_raw.csv` (483 B)

## 4. Archive Acquisition and Verification
- **Source URL:** `https://zenodo.org/api/records/10215080/files/env_audio.zip/content`
- **Destination Path:** `E:/gunshot/gunshot/data/phase27/original_archive/env_audio.zip`
- **Archive Size:** 495,276,974 bytes (~472.33 MiB, well below the conservative 2.6 GB estimate from preliminary uncompressed reports)
- **Repository MD5 Checksum:** `8c042dc817f459e80ac2491ffc8dd1cd`
- **Computed Local MD5:** `8c042dc817f459e80ac2491ffc8dd1cd` (MATCH CONFIRMED)
- **Computed Local SHA-256:** `7ebfb4aec3ec41a64db326b7b28789c0d6346a6439182ceb1e9d22f401f3438a`
- **Zip CRC Integrity Test:** `zipfile.testzip()` completed with 0 errors across all 6 members.

## 5. Uncompressed Extraction
All 6 files extracted into `data/phase27/original_audio/env_audio/`:
1. `1_AUDIO.wav`: 158,760,044 B, 22,050 Hz, 16-bit PCM mono, exactly 3,600.00 s (1.0000 hr)
2. `2_AUDIO.wav`: 158,760,044 B, 22,050 Hz, 16-bit PCM mono, exactly 3,600.00 s (1.0000 hr)
3. `3_AUDIO.wav`: 158,760,044 B, 22,050 Hz, 16-bit PCM mono, exactly 3,600.00 s (1.0000 hr)
4. `4_AUDIO.wav`: 158,760,044 B, 22,050 Hz, 16-bit PCM mono, exactly 3,600.00 s (1.0000 hr)
5. `5_AUDIO.wav`: 158,760,044 B, 22,050 Hz, 16-bit PCM mono, exactly 3,600.00 s (1.0000 hr)
6. `6_AUDIO.wav`: 158,760,044 B, 22,050 Hz, 16-bit PCM mono, exactly 3,600.00 s (1.0000 hr)
**Total Gross Extracted Duration:** Exactly 21,600.00 seconds (6.0000 hours).

## 6. Signal Inspection and Resampling Lineage
Each original recording was inspected for digital anomalies:
- **Corrupted Frames / Decoding Errors:** None. All 79,380,000 samples per file decoded cleanly.
- **Front-End Clipping:** 0 clipped samples (|amplitude| >= 0.9999). Peak amplitudes ranged from 0.412 to 0.884.
- **Silence Analysis:** Silence ratio (|amplitude| < 0.0001) is < 0.01% across all files.
- **Standardized Resampling:** Converted from native 22,050 Hz to detector baseline 16,000 Hz using high-order polyphase rational factor filtering (`scipy.signal.resample_poly(arr, 320, 441)`).
- **Derived Audio Output:** Stored in `data/phase27/derived_audio/` as 16-bit PCM mono WAV (`1_AUDIO_16k.wav` through `6_AUDIO_16k.wav`), each exactly 115,200,044 bytes and 57,600,000 samples (3,600.00 s).
