# PHASE 34 — HISTORICAL CORRECTIONS & RETRACTION REGISTER
## Workstream 6: Discrepancy Register & Retraction of Earlier Benchmark Citations

> **MANDATORY SAFETY DESIGNATION**  
> **RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY**  
> *This experimental acoustic machine-learning software is uncertified and must never be deployed for autonomous emergency dispatch, tactical police response, active-shooter alerting, automated evacuation, building lockdown, or life-critical physical security. Use legally obtained recordings and safe audio playback only. Live-fire testing and hazardous acoustic experiments are strictly prohibited.*

---

## 1. Executive Summary & Policy

To preserve archival provenance and auditability, historical release archives (`phase27.zip` through `phase33.zip`) and their markdown deliverables remain **permanently frozen and immutable**. Under no circumstances are past reports retroactively edited.

However, to maintain scientific rigor, this document serves as the **authoritative retraction and correction register**. Any past claim, metric, or campaign identifier formally identified herein as superseded or erroneous **must never be cited in ongoing research or governance evaluations**.

---

## 2. Master Historical Discrepancy Register (Phases 27–33)

As compiled in [phase34_historical_discrepancy_register.csv](file:///E:/gunshot/gunshot/reports/phase34_historical_discrepancy_register.csv):

| Phase | Field | Historical Value | Reconstructed Value | Difference ($\Delta$) | Root Cause Diagnosis | Governance Status |
| :---: | :--- | :--- | :--- | :---: | :--- | :---: |
| **Phase 27** | Continuous Benchmark Exposure | Southampton (5.5h), Chew Magna (0.5833h), Bilbao (0.5627h), Adelaide (6.0h); Total = 12.6460h | Southampton (5.5h), Chew Magna (0.5833h), Bilbao (0.5627h), Adelaide (6.0h); Total = 12.6460h | 0.0 s | Baseline continuous audio ingestion was physically accurate and matches disk WAV headers. | `VALID_HISTORICAL_RECORD` |
| **Phase 28** | Wilcoxon Paired $p$-Value | $p = 0.125$ or $p = 0.156$ | SciPy Asymptotic: $p = 0.1562601$; Exact Tied Permutation: $p = 0.2109375$ | $-0.031$ to $-0.055$ | Variations caused by uncorrected preliminary normal approximations and zero-exclusion rules. | `SUPERSEDED_BY_EXACT_REGISTER` |
| **Phase 30** | Benchmark Campaign Identities | RPISOUND-UK (10), CHEWMAGNA-UK (1), BILBAO-ES (6), AEROSONIC-AU (6) | Southampton (10), Chew Magna (1), Bilbao (6), Adelaide (6) | None | Correctly preserved all 4 true campaign identities and 23 physical streams. | `VALID_HISTORICAL_RECORD` |
| **Phase 31** | Campaign Duration Allocations | Southampton: 5.5000h, Chew Magna: 0.5833h, Bilbao: 0.5627h, Adelaide: 6.0000h (Total 12.6460h) | Southampton: 5.5000h, Chew Magna: 0.5833h, Bilbao: 0.5627h, Adelaide: 6.0000h (Total 12.6460h) | 0.0 s | Fully concordant with physical audio WAV headers across all 23 files. | `AUTHORITATIVE_GROUND_TRUTH` |
| **Phase 32** | Benchmark Campaign Names | `CAMPAIGN-RPISOUND-UK` (7), `CAMPAIGN-DCASE2020-ES` (5), `CAMPAIGN-URBANSOUND-PL` (5), `AEROSONIC-AU` (6) | Southampton (10), Chew Magna (1), Bilbao (6), Adelaide (6) | Fictional 7/5/5 split and fictitious campaign names | Clerical fabrication. DCASE and UrbanSound were rejected in Phase 23; Bilbao was falsely split. | `RETRACTED_FABRICATED_PROSE` |
| **Phase 32** | Total Benchmark Duration | 45,526.0 s (12.6461 h) | 45,525.5755 s (12.6460 h) | +0.4245 s (+0.0001 h) | Narrative rounding artifact from summing pre-rounded campaign durations ($9860 + 7030 + 7036 + 21600$). | `RETRACTED_ROUNDING_ERROR` |
| **Phase 32** | State-Machine Failure Count | "Failed 6/12 vectors" | Failed 8/12 vectors (66.7% failure rate) | +2 failing vectors | Typographical clerical error in Phase 32 executive summary text ($12 - 6 = 6$). | `CORRECTED_IN_PHASE33` |
| **Phase 33** | Section 5.2 Prose Duration Table | Southampton: 2.4917h (8970s), Chew Magna: 0.2472h (890s), Bilbao: 3.9071h (14065.6s), Adelaide: 6.0h | Southampton: 5.5000h (19800s), Chew Magna: 0.5833h (2100s), Bilbao: 0.5627h (2025.6s), Adelaide: 6.0h | Soton: -3.0083h; Chew: -0.3361h; Bilbao: +3.3444h | Clerical transposition. Report author erroneously copied Phase 32's fabricated split (9860s UK, 14066s Spain). | `CORRECTED_IN_PHASE34` |
| **Phase 33** | Canonical Stream Registry CSV | Southampton: 19800s (5.5h), Chew Magna: 2100s (0.5833h), Bilbao: 2025.5755s (0.5627h), Adelaide: 21600s | Southampton: 19800s (5.5h), Chew Magna: 2100s (0.5833h), Bilbao: 2025.5755s (0.5627h), Adelaide: 21600s | 0.0 s | Underlying CSV data in Phase 33 was physically accurate and 100% concordant with Phase 31. | `VALID_GROUND_TRUTH_DATA` |

---

## 3. Explicit Citations Blacklist & Permitted Standards

The following historical claims and values are **permanently retired from active use**:

### 3.1 Blacklisted Claims & Retracted Numbers (DO NOT CITE)
1. **DO NOT CITE:** `CAMPAIGN-DCASE2020-ES` or `CAMPAIGN-URBANSOUND-PL` as continuous negative benchmark sources.
   - *Reason:* Neither TAU DCASE nor UrbanSound8K contributed continuous audio files to this benchmark. Both consist of isolated 10-second clips.
2. **DO NOT CITE:** Benchmark stream counts of `7, 5, 5, 6`.
   - *Reason:* The physical inventory consists of `10, 1, 6, 6` streams.
3. **DO NOT CITE:** Total continuous benchmark duration of `45,526.0 seconds` or `12.6461 hours`.
   - *Reason:* Artifact of narrative rounding ($+0.4245\text{ s}$). True duration is **45,525.5755 seconds (12.6460 hours)**.
4. **DO NOT CITE:** Phase 33 Section 5.2 narrative durations: Southampton as `2.4917 hours` (8,970 s), Chew Magna as `0.2472 hours` (890 s), or Bilbao as `3.9071 hours` (14,065.6 s).
   - *Reason:* Accidental reverse-transposition of Phase 32's fabricated split. True durations are **5.5000h, 0.5833h, and 0.5627h**.
5. **DO NOT CITE:** Phase 17 state-machine defect failure rate as `6/12 vectors (50.0%)`.
   - *Reason:* True failure rate is **8/12 vectors (66.7%)**.
6. **DO NOT CITE:** Historical controlled gunfire validation recall of `33 vs 27 rounds (p = 0.03125)`.
   - *Reason:* Proved to be an artifact of multi-credit alert reuse across bursts. Valid 1-to-1 matching yields **19 vs 15 rounds ($p = 0.21875$, not significant)**.
7. **DO NOT CITE:** Untied combinatorial comparison ($p = 0.1953125$) as the exact tied-rank permutation result.
   - *Reason:* The exact tied-rank permutation result is **$p = 0.2109375$** ($54 / 256$).

### 3.2 Permitted Authoritative Standards (ACTIVE CANON)
- **Continuous Negative Benchmark Inventory:** Exactly **23 streams, 4 campaigns, 45,525.5755 seconds (12.6460 hours)**.
- **Campaign Allocations:**
  - `CAMPAIGN-SOUTHAMPTON-EXP1` (Southampton, UK): **10 streams, 19,800.0000 s (5.5000 hr)**
  - `CAMPAIGN-CHEW-MAGNA` (Chew Magna, UK): **1 stream, 2,100.0000 s (0.5833 hr)**
  - `CAMPAIGN-BILBAO` (Bilbao, Spain): **6 streams, 2,025.5755 s (0.5627 hr)**
  - `CAMPAIGN-ADELAIDE-AEROSONIC` (Adelaide, Australia): **6 streams, 21,600.0000 s (6.0000 hr)**
- **Baseline Models:** Phase 14 Balanced remains the Default Research Baseline (`model_phase14.py`). Phase 17 Experimental promotion is rejected. State-reset candidate patch is quarantined.
- **Life Safety Prohibition:** Uncertified research prototype; zero operational life-safety deployment.

