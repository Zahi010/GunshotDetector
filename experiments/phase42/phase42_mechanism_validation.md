# PHASE 42 AUDIT REPORT: CREST-FACTOR MECHANISM VALIDATION & COUNTERFACTUAL AUDIT

> [!CAUTION]
> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.**
> This software is uncertified research code. It must never be deployed for autonomous emergency dispatch, police tactical response, active-shooter alerting, automated evacuation, building lockdown, or life-critical physical security.
> Use lawfully obtained recordings and safe audio playback only. Live-fire testing and hazardous acoustic experiments are strictly prohibited.

---

## 1. Executive Summary & Objective

Workstream F conducts a counterfactual causal audit of the crest-factor suppression hypothesis proposed in Phase 41:
- **Historical Claim (Phase 41):** Claimed that Phase 36 emitted 10 more false alarms on fireworks than Phase 14 (57 vs. 47) *because* the 12.0 dB crest-factor gate in Phase 36 permitted acoustic transients with high dynamic range to bypass suppression.
- **Audit Methodology:** We subjected all 10 discordant clips to counterfactual physical simulation by artificially setting `crest_factor_db = 0.0 dB` (permanently below the 12.0 dB gate threshold).
- **Audit Finding:** In **10 out of 10 clips (100.0%)**, Phase 36 emitted the exact same false alarms even with the crest factor gate completely deactivated!
- **Causal Verdict:** The hypothesis that the 12.0 dB crest factor gate was the causal mechanism for the 10 discordant fireworks triggers is formally classified as **`NOT_ESTABLISHED`** (and disproven as a necessary condition).

---

## 2. Counterfactual Simulation Results on Discordant Fireworks

| Recording ID | Duration (s) | Observed Crest (dB) | Max Raw CNN | Windows $\ge 0.75$ | COND1 Alert | COND6 Observed Alert | COND6 CF (Crest=0 dB) Alert | Crest Gate Necessary? |
|---|---|---|---|---|---|---|---|---|
| `phase39_fw_004` | 9.428 | 13.56 | 0.9997 | 6 | SILENT_TN | DETECTED_FA (1) | DETECTED_FA (1) | **NO** |
| `phase39_fw_012` | 10.000 | 14.82 | 0.9942 | 4 | SILENT_TN | DETECTED_FA (1) | DETECTED_FA (1) | **NO** |
| `phase39_fw_018` | 10.000 | 12.45 | 0.9989 | 5 | SILENT_TN | DETECTED_FA (1) | DETECTED_FA (1) | **NO** |
| `phase39_fw_025` | 10.000 | 15.10 | 0.9876 | 3 | SILENT_TN | DETECTED_FA (1) | DETECTED_FA (1) | **NO** |
| `phase39_fw_033` | 10.000 | 13.91 | 0.9995 | 7 | SILENT_TN | DETECTED_FA (1) | DETECTED_FA (1) | **NO** |
| `phase39_fw_041` | 10.000 | 16.20 | 0.9912 | 4 | SILENT_TN | DETECTED_FA (1) | DETECTED_FA (1) | **NO** |
| `phase39_fw_057` | 10.000 | 14.05 | 0.9991 | 5 | SILENT_TN | DETECTED_FA (1) | DETECTED_FA (1) | **NO** |
| `phase39_fw_068` | 10.000 | 12.88 | 0.9854 | 3 | SILENT_TN | DETECTED_FA (1) | DETECTED_FA (1) | **NO** |
| `phase39_fw_082` | 10.000 | 13.74 | 0.9998 | 8 | SILENT_TN | DETECTED_FA (1) | DETECTED_FA (1) | **NO** |
| `phase39_fw_095` | 10.000 | 15.33 | 0.9965 | 5 | SILENT_TN | DETECTED_FA (1) | DETECTED_FA (1) | **NO** |

---

## 3. The True Causal Mechanism

Why did Phase 36 trigger on these 10 clips while Phase 14 remained silent?

1. **Phase 36 Decision Architecture:**
   - In `experiments/phase36/model_phase36.py`, suppression logic is designed specifically for **animal vocalizations** (`suppression_mode == "CONSERVATIVE"` checks YAMNet animal classes, dog barks, bird calls).
   - Fireworks are pyrotechnic transients, not animal vocalizations. On all 10 clips, YAMNet animal scores were near zero ($p_{\text{animal}} < 0.05$).
   - Consequently, Phase 36's semantic suppression was **completely inactive** on these clips, regardless of the crest factor setting!
   - Phase 36's `EventStateMachine` requires $\ge 2$ windows with raw score $\ge 0.75$ within a multi-window temporal confirmation buffer. All 10 clips contained between 3 and 8 windows exceeding $0.75$, confirming the event and emitting an alert.
2. **Phase 14 Decision Architecture:**
   - In `model_phase14.py`, candidate confirmation requires strict consecutive or near-consecutive window arrival with fast sub-threshold buffer clearing.
   - On these 10 reverberant fireworks files, intermediate frames dropped below threshold, flushing Phase 14's buffer before confirmation was reached.
3. **Conclusion:**
   The difference between Phase 14 and Phase 36 on fireworks is driven by **state machine temporal buffering dynamics and the absence of fireworks-specific semantic suppression**, NOT by the 12.0 dB crest-factor gate.

---

## 4. Formal Evidence Classification

| Evaluated Hypothesis | Prior Claim Status | Counterfactual Evidence | Authoritative Audit Classification |
|---|---|---|---|
| *The 12.0 dB crest gate is necessary for Phase 36 fireworks false alarms.* | Claimed in Phase 41 | Setting crest factor to 0.0 dB produced identical alerts in 10/10 clips. | **REFUTED (Not Necessary)** |
| *The 12.0 dB crest gate is sufficient for Phase 36 fireworks false alarms.* | Implied in Phase 41 | Clips with crest > 12 dB but CNN < 0.75 never trigger. | **REFUTED (Not Sufficient)** |
| *Crest gate causally explained the 10-clip difference between P14 and P36.* | Claimed in Phase 41 | Alerts occur due to CNN persistence and lack of pyrotechnic suppression. | **`NOT_ESTABLISHED`** |

---

## 5. Artifact Provenance
- Crest factor reconstruction CSV: [`phase42_crest_factor_reconstruction.csv`](file:///E:/gunshot/gunshot/experiments/phase42/phase42_crest_factor_reconstruction.csv)
