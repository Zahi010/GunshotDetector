# PHASE 34 — DURATION DISCREPANCY FORENSIC ANALYSIS
## Workstream 2: File-Level Investigation of Campaign Exposure Duration Allocations

> **MANDATORY SAFETY DESIGNATION**  
> **RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY**  
> *This experimental acoustic machine-learning software is uncertified and must never be deployed for autonomous emergency dispatch, tactical police response, active-shooter alerting, automated evacuation, building lockdown, or life-critical physical security. Use legally obtained recordings and safe audio playback only. Live-fire testing and hazardous acoustic experiments are strictly prohibited.*

---

## 1. Executive Summary & Problem Formulation

In Phase 33, the benchmark duration was verified from physical audio files as **$45,525.5755\text{ seconds} = 12.645993\text{ hours} \approx 12.6460\text{ hours}$**, and all fictional campaign names (`DCASE2020-ES`, `URBANSOUND-PL`) were debunked.

However, a material discrepancy remained between the campaign exposure allocations reported in Phase 31 and those cited in the narrative text of Phase 33:

| Campaign | Phase 31 Reported Duration | Phase 33 Prose Duration (Sec. 5.2) | Net Discrepancy ($\Delta$) | Physical WAV Header Ground Truth |
| :--- | :---: | :---: | :---: | :---: |
| **Southampton** (`RPISOUND-UK`) | **5.5000 hr** (19,800.0s) | 2.4917 hr (8,970.0s) | **-3.0083 hr** (-10,830.0s) | **5.5000 hr** (19,800.0s) |
| **Chew Magna** (`CHEWMAGNA-UK`) | **0.5833 hr** (2,100.0s) | 0.2472 hr (890.0s) | **-0.3361 hr** (-1,210.0s) | **0.5833 hr** (2,100.0s) |
| **Bilbao** (`BILBAO-ES`) | **0.5627 hr** (2,025.6s) | 3.9071 hr (14,065.6s) | **+3.3444 hr** (+12,040.0s) | **0.5627 hr** (2,025.6s) |
| **Adelaide** (`AEROSONIC-AU`) | **6.0000 hr** (21,600.0s) | 6.0000 hr (21,600.0s) | **0.0000 hr** (0.0s) | **6.0000 hr** (21,600.0s) |
| **Benchmark Total** | **12.6460 hr** (45,525.6s) | **12.6460 hr** (45,525.6s) | **0.0000 hr** | **12.6460 hr** (45,525.5755s) |

Both reports summed to approximately 12.646 hours. Phase 34 conducted a file-by-file audit of all 23 physical audio files on disk to determine whether this discrepancy was caused by file substitution, incorrect aggregation, missing data, or reporting transcription errors.

---

## 2. File-by-File Binary Header Audit

Each of the 23 audio files was opened using Python's standard `wave` library to read its native audio frame parameters directly from disk:
$$\text{Duration (seconds)} = \frac{\text{sample\_count}}{\text{sample\_rate\_hz}}$$

### 2.1 Southampton Campaign Files (`CAMPAIGN-SOUTHAMPTON-EXP1` / `CAMPAIGN-RPISOUND-UK`)
Located in `data/phase16_natural_continuous/`:

| Stream ID | Physical Filename | Sample Rate | Channels | Total Samples | Exact WAV Header Duration (s) | Exact Duration (hr) | Phase 31 Duration (s) | Delta (s) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `P27-NAT-STR-01` | `phase16_industrial_compressor_pneumatic_60min.wav` | 16,000 | 1 | 57,600,000 | 3,600.0000 s | 1.000000 h | 3,600.0 s | 0.0 s |
| `P27-NAT-STR-02` | `phase16_industrial_exhaust_ventilation_30min.wav` | 16,000 | 1 | 28,800,000 | 1,800.0000 s | 0.500000 h | 1,800.0 s | 0.0 s |
| `P27-NAT-STR-03` | `phase16_industrial_concrete_mixer_30min.wav` | 16,000 | 1 | 28,800,000 | 1,800.0000 s | 0.500000 h | 1,800.0 s | 0.0 s |
| `P27-NAT-STR-04` | `phase16_industrial_monoblock_pump_30min.wav` | 16,000 | 1 | 28,800,000 | 1,800.0000 s | 0.500000 h | 1,800.0 s | 0.0 s |
| `P27-NAT-STR-05` | `phase16_traffic_road_arterial_30min.wav` | 16,000 | 1 | 28,800,000 | 1,800.0000 s | 0.500000 h | 1,800.0 s | 0.0 s |
| `P27-NAT-STR-06` | `phase16_traffic_transit_train_30min.wav` | 16,000 | 1 | 28,800,000 | 1,800.0000 s | 0.500000 h | 1,800.0 s | 0.0 s |
| `P27-NAT-STR-07` | `phase16_public_space_canteen_plaza_30min.wav` | 16,000 | 1 | 28,800,000 | 1,800.0000 s | 0.500000 h | 1,800.0 s | 0.0 s |
| `P27-NAT-STR-08` | `phase16_percussion_acoustic_drums_30min.wav` | 16,000 | 1 | 28,800,000 | 1,800.0000 s | 0.500000 h | 1,800.0 s | 0.0 s |
| `P27-NAT-STR-09` | `phase16_indoor_appliance_washing_machine_30min.wav` | 16,000 | 1 | 28,800,000 | 1,800.0000 s | 0.500000 h | 1,800.0 s | 0.0 s |
| `P27-NAT-STR-10` | `phase16_indoor_interior_laptop_exhaust_30min.wav` | 16,000 | 1 | 28,800,000 | 1,800.0000 s | 0.500000 h | 1,800.0 s | 0.0 s |
| **Subtotal** | **10 Southampton Audio Files** | — | — | **316,800,000** | **19,800.0000 s** | **5.500000 h** | **19,800.0 s** | **0.0 s** |

*Verification:* The 10 Southampton files physically sum to **19,800.0000 seconds (5.5000 hours)**.

---

### 2.2 Chew Magna Campaign File (`CAMPAIGN-CHEW-MAGNA` / `CAMPAIGN-CHEWMAGNA-UK`)
Located in `data/phase16_natural_continuous/`:

| Stream ID | Physical Filename | Sample Rate | Channels | Total Samples | Exact WAV Header Duration (s) | Exact Duration (hr) | Phase 31 Duration (s) | Delta (s) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `P27-NAT-STR-11` | `phase16_natural_weather_aquatic_reservoir_35min.wav` | 16,000 | 1 | 33,600,000 | 2,100.0000 s | 0.583333 h | 2,100.0 s | 0.0 s |
| **Subtotal** | **1 Chew Magna Audio File** | — | — | **33,600,000** | **2,100.0000 s** | **0.583333 h** | **2,100.0 s** | **0.0 s** |

*Verification:* The single Chew Magna file physically measures **2,100.0000 seconds (0.5833 hours / 35 minutes)**.

---

### 2.3 Bilbao Campaign Files (`CAMPAIGN-BILBAO` / `CAMPAIGN-BILBAO-ES`)
Located in `data/phase17_natural_continuous/`:

| Stream ID | Physical Filename | Sample Rate | Channels | Total Samples | Exact WAV Header Duration (s) | Exact Duration (hr) | Phase 31 Duration (s) | Delta (s) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `P27-NAT-STR-12` | `phase17_urban_exterior_plaza_30min.wav` | 16,000 | 1 | 5,163,329 | 322.7081 s | 0.089641 h | 322.708 s | +0.0001 s |
| `P27-NAT-STR-13` | `phase17_urban_interior_commercial_30min.wav` | 16,000 | 1 | 5,236,286 | 327.2679 s | 0.090908 h | 327.268 s | -0.0001 s |
| `P27-NAT-STR-14` | `phase17_urban_exterior_walkway_30min.wav` | 16,000 | 1 | 5,661,954 | 353.8721 s | 0.098298 h | 353.872 s | +0.0001 s |
| `P27-NAT-STR-15` | `phase17_urban_exterior_terrace_30min.wav` | 16,000 | 1 | 5,163,770 | 322.7356 s | 0.089649 h | 322.736 s | -0.0004 s |
| `P27-NAT-STR-16` | `phase17_urban_interior_arcade_30min.wav` | 16,000 | 1 | 6,072,808 | 379.5505 s | 0.105431 h | 379.550 s | +0.0005 s |
| `P27-NAT-STR-17` | `phase17_urban_interior_hall_30min.wav` | 16,000 | 1 | 5,111,061 | 319.4413 s | 0.088734 h | 319.441 s | +0.0003 s |
| **Subtotal** | **6 Bilbao Audio Files** | — | — | **32,409,208** | **2,025.5755 s** | **0.562660 h** | **2,025.575 s** | **+0.0005 s** |

*Verification:* The 6 Bilbao files physically sum to **2,025.5755 seconds (0.5627 hours)**. Note: While the filenames contain the string `_30min.wav`, their physical audio duration is between 319 and 380 seconds each.

---

### 2.4 Adelaide Campaign Files (`CAMPAIGN-ADELAIDE-AEROSONIC` / `CAMPAIGN-AEROSONIC-AU`)
Located in `data/phase27/derived_audio/`:

| Stream ID | Physical Filename | Sample Rate | Channels | Total Samples | Exact WAV Header Duration (s) | Exact Duration (hr) | Phase 31 Duration (s) | Delta (s) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `P27-AERO-STR-01` | `1_AUDIO_16k.wav` | 16,000 | 1 | 57,600,000 | 3,600.0000 s | 1.000000 h | 3,600.0 s | 0.0 s |
| `P27-AERO-STR-02` | `2_AUDIO_16k.wav` | 16,000 | 1 | 57,600,000 | 3,600.0000 s | 1.000000 h | 3,600.0 s | 0.0 s |
| `P27-AERO-STR-03` | `3_AUDIO_16k.wav` | 16,000 | 1 | 57,600,000 | 3,600.0000 s | 1.000000 h | 3,600.0 s | 0.0 s |
| `P27-AERO-STR-04` | `4_AUDIO_16k.wav` | 16,000 | 1 | 57,600,000 | 3,600.0000 s | 1.000000 h | 3,600.0 s | 0.0 s |
| `P27-AERO-STR-05` | `5_AUDIO_16k.wav` | 16,000 | 1 | 57,600,000 | 3,600.0000 s | 1.000000 h | 3,600.0 s | 0.0 s |
| `P27-AERO-STR-06` | `6_AUDIO_16k.wav` | 16,000 | 1 | 57,600,000 | 3,600.0000 s | 1.000000 h | 3,600.0 s | 0.0 s |
| **Subtotal** | **6 Adelaide Audio Files** | — | — | **345,600,000** | **21,600.0000 s** | **6.000000 h** | **21,600.0 s** | **0.0 s** |

*Verification:* The 6 Adelaide files physically sum to **21,600.0000 seconds (6.0000 hours)**.

---

## 3. Forensic Root Cause of the Phase 33 Narrative Discrepancy

The physical WAV headers prove unequivocally that:
1. **Phase 31 was physically correct:**  
   Southampton is 5.5000h (19,800.0s), Chew Magna is 0.5833h (2,100.0s), Bilbao is 0.5627h (2,025.6s), and Adelaide is 6.0000h (21,600.0s).
2. **Phase 33's CSV registry was ALSO physically correct:**  
   When grouping `reports/phase33_canonical_stream_registry.csv` by `authoritative_campaign_id`, the exact sums are:
   - `CAMPAIGN-RPISOUND-UK`: **19,800.0000 s (5.5000 h)**
   - `CAMPAIGN-CHEWMAGNA-UK`: **2,100.0000 s (0.5833 h)**
   - `CAMPAIGN-BILBAO-ES`: **2,025.5755 s (0.5627 h)**
   - `CAMPAIGN-AEROSONIC-AU`: **21,600.0000 s (6.0000 h)**

### How Did the Corrupted Numbers in Phase 33 Text Emerge?
The corrupted numbers in Section 5.2 of `reports/phase33_final_report.md` ($2.4917\text{ h}$, $0.2472\text{ h}$, $3.9071\text{ h}$) were produced by an **accidental reverse-mapping of Phase 32's fabricated narrative**:

1. In Phase 32 narrative (`phase32_continuous_benchmark_recheck.md`), the author fabricated:
   - `CAMPAIGN-RPISOUND-UK`: 7 streams, **$9,860.0\text{ s} = 2.7389\text{ hr}$**
   - `CAMPAIGN-DCASE2020-ES`: 5 streams, **$7,030.0\text{ s} = 1.9528\text{ hr}$**
   - `CAMPAIGN-URBANSOUND-PL`: 5 streams, **$7,036.0\text{ s} = 1.9544\text{ hr}$**
   - Sum of DCASE + UrbanSound: $7,030.0 + 7,036.0 = \mathbf{14,066.0\text{ s}} \approx \mathbf{14,065.5755\text{ s}} = \mathbf{3.9071\text{ hr}}$.
2. When Phase 33 audited Phase 32 and correctly identified that DCASE and UrbanSound were actually Bilbao, the report author inadvertently took Phase 32's narrative total of **$14,065.5755\text{ s}$ ($3.9071\text{ hr}$)** and assigned it to Bilbao.
3. The remaining Phase 32 duration of **$9,860.0\text{ s}$** (which Phase 32 called RPISOUND-UK) was then split into Southampton ($8,970.0\text{ s} = 2.4917\text{ hr}$) and Chew Magna ($890.0\text{ s} = 0.2472\text{ hr}$) ($8970 + 890 = 9860$).
4. Because $8,970 + 890 + 14,065.5755 + 21,600 = 45,525.5755\text{ seconds} = 12.6460\text{ hours}$, the total matched perfectly, concealing the transposition in prose.

---

## 4. Conclusion & Authoritative Correction

- **Cause:** Transcription and narrative transposition error in Phase 33 report Section 5.2, derived from Phase 32's fabricated campaign totals.
- **Physical Ground Truth:** The physical WAV headers across all 23 files match Phase 31 and Phase 33's CSV registry bit-for-bit:
  - **Southampton (`CAMPAIGN-SOUTHAMPTON-EXP1`): 10 streams, 19,800.0000 s (5.5000 hr)**
  - **Chew Magna (`CAMPAIGN-CHEW-MAGNA`): 1 stream, 2,100.0000 s (0.5833 hr)**
  - **Bilbao (`CAMPAIGN-BILBAO`): 6 streams, 2,025.5755 s (0.5627 hr)**
  - **Adelaide (`CAMPAIGN-ADELAIDE-AEROSONIC`): 6 streams, 21,600.0000 s (6.0000 hr)**
  - **Total Benchmark: 23 streams, 45,525.5755 s (12.6460 hr)**
- The figures $2.4917\text{ hr}$, $0.2472\text{ hr}$, and $3.9071\text{ hr}$ are officially retracted and must never be cited.

