# Phase 35 Benchmark Integrity & Provenance Consistency Audit

> [!CAUTION]
> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.**
> This experimental acoustic machine-learning software is uncertified and must never be deployed for autonomous emergency dispatch, police tactical response, active-shooter alerting, automated evacuation, building lockdown, or life-critical physical security.
> Use legally obtained recordings and safe audio playback only. Live-fire testing and hazardous acoustic experiments are strictly prohibited.

---

## 1. Executive Summary

This audit re-confirms the complete integrity, provenance consistency, and mathematical alignment of the authoritative 23-stream continuous benchmark established in Phase 34.

### 1.1 Authoritative 23-Stream Inventory

| Campaign Identifier | Recording Files | Gross Duration (s) | Gross Duration (hr) | Phase 14 Alerts | Phase 17 Alerts |
|---|:---:|:---:|:---:|:---:|:---:|
| `CAMPAIGN-SOUTHAMPTON-EXP1` | 10 | 19,800.0000 | 5.5000 | 24 | 22 |
| `CAMPAIGN-CHEW-MAGNA` | 1 | 2,100.0000 | 0.5833 | 0 | 0 |
| `CAMPAIGN-BILBAO` | 6 | 2,025.5755 | 0.5627 | 32 | 29 |
| `CAMPAIGN-ADELAIDE-AEROSONIC` | 6 | 21,600.0000 | 6.0000 | 72 | 108 |
| **CUMULATIVE BENCHMARK TOTAL** | **23** | **45,525.5755** | **12.6460** | **128** | **159** |

---

## 2. Seven-Point Consistency Verification

1. **File Hashes Match Phase 34 Registry:**
   All 23 audio files in `data/phase16_natural_continuous/`, `data/phase17_natural_continuous/`, and `data/phase27/` match their registered SHA-256 digests in [phase34_canonical_23_stream_registry.csv](file:///e:/gunshot/gunshot/reports/phase34_canonical_23_stream_registry.csv).
2. **Durations Match Physical WAV Headers:**
   Physical byte extraction of `nframes / framerate` confirms Southampton = $19,800.0000\text{ s}$, Chew Magna = $2,100.0000\text{ s}$, Bilbao = $2,025.5755\text{ s}$, and Adelaide = $21,600.0000\text{ s}$. Cumulative corpus duration is exactly **$45,525.5755\text{ seconds}$** ($12.645993...\text{ gross hours}$).
3. **Campaign Labels Match Source Provenance:**
   Campaign identities align with primary Zenodo upload metadata and geographic acquisition sites (UK, Spain, Australia).
4. **Alert Counts Match Source Event Logs:**
   Phase 14 Balanced generates exactly **128 alerts**; Phase 17 Experimental generates exactly **159 alerts** (Total = 287 alerts).
5. **Campaign Aggregations Equal Corpus Totals:**
   Every campaign duration sum and alert sum equals the respective corpus total with zero floating-point error.
6. **Phase 31 and Phase 34 Allocations Agree:**
   The Phase 31 duration allocation (Southampton 5.5h, Chew Magna 0.5833h, Bilbao 0.5627h, Adelaide 6.0h) is verified as physically correct.
7. **Phase 33 Transposed Narrative Values Remain Explicitly Retracted:**
   The erroneous narrative durations reported in Phase 33 Section 1 (Southampton 2.49h, Chew Magna 0.25h, Bilbao 3.91h) remain permanently retracted.

### Integrity Verdict: `ALL_CHECKS_PASSED`
The benchmark inventory is closed, consistent, and immutable.
