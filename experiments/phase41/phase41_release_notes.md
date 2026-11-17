# PHASE 41 RELEASE NOTES
## Independent Evidence Reconciliation and Statistical Robustness Audit

> [!CAUTION]
> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.**
> This software is uncertified research code. It must never be deployed for autonomous emergency dispatch, police tactical response, active-shooter alerting, automated evacuation, building lockdown, or life-critical physical security.
> Use lawfully obtained recordings and safe audio playback only. Live-fire testing and hazardous acoustic experiments are strictly prohibited.

---

## Overview

Phase 41 delivers a complete, independent forensic audit of the evidence, statistics, and provenance claims supporting Phase 40 and historical phases of the gunshot detection research repository.

No models were trained, modified, tuned, or promoted. All frozen research baselines were preserved without modification.

---

## Key Audit Deliverables & Accomplishments

### 1. Workstream A: Recording Inventory Reconciliation
- **Canonical Inventory Catalog:** Published [phase41_recording_inventory.csv](file:///E:/gunshot/gunshot/experiments/phase41/phase41_recording_inventory.csv) containing all 368 evaluation audio entries across all four evaluation partitions:
  - `POSITIVE_GUNSHOT`: 120 recordings (119 unique waveforms, 0.1442 hours).
  - `DISTRACTOR_NOISE` (Fireworks): 100 recordings (100 unique waveforms, 0.3041 hours).
  - `DISTRACTOR_NOISE` (Other Distractors): 120 recordings (120 unique waveforms, 0.2740 hours).
  - `CONTINUOUS_AMBIENT`: 28 recordings (28 unique waveforms, 4.2182 hours).
  - **Total Exposure:** 17,786.33 seconds (4.9406 hours).
- **Denominator Discrepancy Resolved:** Proved that Phase 40's reported 356 recordings represented the pre-expansion dataset ($120 + 220 + 16$). Post-expansion dataset is 368 recordings ($120 + 220 + 28$).
- **Single Duplicate Waveform Pair:** Identified that `fsd50k_gun_51749` (`erkanozan`) and `fsd50k_gun_115295` (`warriorsfan12331`) share identical SHA-256 (`6b272b5b52c6766f...`), establishing $N_{\text{eff}} = 119$ unique positive waveforms.

### 2. Workstream B: Historical Hash & Provenance Reconstruction
- **Physical Model Verification:** Verified physical byte sizes and SHA-256 hashes for all 6 detector implementation scripts and 7 historical release archives (`phase34` through `phase40`), confirming 100% match with historical manifests.
- **Forensic Suffix Hallucination Provenance:** Traced the divergent hash `2774ab4cae0fca6db8905a96860a2fcdd21b44c6c06a92ec25f9b9a6fe402241` to Phase 37 Section 1 markdown text. Proved that characters 1–16 matched the real file (`2774ab4cae0fca6d...`) while characters 17–64 were hallucinated completions from a truncated console buffer. The machine JSON manifest on disk always held the true physical hash `...563a`.

### 3. Workstream C: Source-Level Independence & Audio Similarity
- **Comprehensive 368-Recording Audit:** Evaluated pairwise cosine similarities across all 368 evaluation recordings using YAMNet 1024-dimensional temporal mean embeddings.
- **High Independence in Short Clips:** 120 positive clips from 120 distinct uploaders (ratio 1.00); 100 fireworks from 87 uploaders (ratio 1.15); 120 other distractors from 109 uploaders (ratio 1.10). Overall discrete distractor ratio: 1.17 clips/uploader across 188 unique contributors.
- **Continuous Stream Clustering:** Identified that 28 continuous streams originate from 19 unique recordists (ratio 1.47), with `duseigne` (Marc Namblard / Radio Aporee archive) contributing 8 streams (28.57% of streams, 1.2583 hours).

### 4. Workstream D: Fireworks Paired Contingency & Mechanism Audit
- **Exact Paired 2x2 Contingency Table:** Reconstructed exact results across 100 fireworks clips: Both Triggered = 47, Phase 36 Only = 10, Phase 14 Only = 0, Neither = 43.
- **Statistical Significance Confirmed:** Continuity-corrected McNemar $\chi^2 = 8.1000, p = 0.004427$; Exact two-tailed paired binomial $p = 0.001953$. Phase 36 produces a statistically significant $+10.0\%$ elevation in false activations on fireworks.
- **12.0 dB Crest Factor Mechanism:** Proved that all 10 discordant clips exhibit physical crest factors between 13.1 dB and 19.8 dB (all $\ge 12.0\text{ dB}$). In Phase 36, this bypasses suppression and triggers immediate single-window alert dispatch, whereas Phase 14 applied hard semantic suppression ($0.35\times$).
- **Uploader Independence:** Confirmed that all 10 discordant clips originated from 10 distinct uploaders across 10 independent recording sessions (0.0% uploader clustering).

### 5. Workstream E: Continuous-Background Statistical Robustness
- **Benchmark Reproduction:** Evaluated all 28 streams (4.2182 hours) across COND1–COND6, confirming exact alert counts: COND1=31, COND2=104, COND3=31, COND4=26, COND5=26, COND6=26.
- **Phase 17 Defect Quantified:** Confirmed 3,440.00 seconds of Convention B cooldown exclusion under Phase 17 (22.7% monitoring loss).
- **Continuous FAR Superiority Refuted (`NOT_ESTABLISHED`):** Proved that the 16.1% gross alert reduction under Phase 36 (26 vs 31 alerts) does NOT achieve statistical significance:
  - Stream-level Wilcoxon signed-rank test: $W = 0.0, p = 0.1025 > 0.05$.
  - Recordist-clustered Wilcoxon signed-rank test: $W = 0.0, p = 0.1025 > 0.05$.
  - Cluster-robust sandwich difference $t$-test: $t = 1.3955, p = 0.1799 > 0.05$ (95% Clustered CI: $[-0.5992, +2.9699]$ alerts/hr).
  - Out of 28 streams, 25 showed zero alert count difference; only 3 streams differed. Claims of superior background quietness for Phase 36 are unestablished.

### 6. Workstream F: Claim-to-Evidence Matrix & Scope Cross-Mapping
- Published [phase41_claim_evidence_matrix.csv](file:///E:/gunshot/gunshot/experiments/phase41/phase41_claim_evidence_matrix.csv) auditing all 11 Phase 40 claims against physical evidence.
- Published [phase41_audit_scope_reconciliation.md](file:///E:/gunshot/gunshot/experiments/phase41/phase41_audit_scope_reconciliation.md) reconciling Phase 40's 11 prompt workstreams against report sections.

### 7. Workstream G: Automated Regression Test Suite
- Delivered [tests/test_phase41_audit.py](file:///E:/gunshot/gunshot/tests/test_phase41_audit.py) with 22 comprehensive assertions covering safety notices, cryptographic hashes, inventory counts, duplicate waveforms, fireworks contingency, crest mechanisms, Wilcoxon tests, and claim matrix validation.
- All 22 tests pass cleanly (see [phase41_test_execution_log.txt](file:///E:/gunshot/gunshot/experiments/phase41/phase41_test_execution_log.txt)).

---

## Architectural & Governance Dispositions

1. **Phase 14 Balanced Baseline:** Retained as `DEFAULT_RESEARCH_BASELINE`.
2. **Phase 17 Experimental Profile:** Retained as `SELECTABLE_EXPERIMENTAL_PROFILE` (quarantined defect active).
3. **Phase 31 State Reset Candidate:** Retained as `QUARANTINED_DIAGNOSTIC_REFERENCE`.
4. **Phase 36 Experimental Architecture:** Retained as `EXPERIMENTAL_RESEARCH_BRANCH_V1` (**NOT PROMOTED**).
"""

with open(P41_DIR / "phase41_release_notes.md", "w", encoding="utf-8") as f:
    f.write(md_content)
print("Saved phase41_release_notes.md")

