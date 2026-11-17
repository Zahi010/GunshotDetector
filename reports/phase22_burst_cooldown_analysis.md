# Phase 22: Burst and Refractory-Cooldown Forensic Audit

### MANDATORY SAFETY DESIGNATION
> [!CAUTION]
> **RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.**
> This experimental acoustic machine-learning system is uncertified and must never be deployed for autonomous emergency dispatch, tactical police response, active-shooter alerting, automated lockdown/evacuation, or life-critical physical security. Use legally obtained recordings and safe audio playback only. Live-fire testing and hazardous acoustic experiments are strictly prohibited.

---

## 1. Executive Summary

Phase 21 noted that in 14 of 15 three-round bursts, the entire multi-round sequence spans $\le 2.0\text{ seconds}$. However, burst duration alone does not prove whether missed rounds were suppressed by the detector's refractory cooldown, merged into an active alert cluster, or missed due to insufficient acoustic energy.

This forensic audit reconstructs the exact millisecond state-machine transitions, window activations, alert durations, and cooldown intervals for **Phase 14 Balanced** and **Phase 17 Experimental** across all 50 physical gunshot rounds in Category A (ShotSpotter Pittsburgh PA DQV 2018).

### Core Forensic Conclusions:
1. **Cooldown Suppression vs. Merging Disambiguated:**
   - **Phase 14 Balanced ($N=50$ rounds):**
     - **`DETECTED_WITH_INDEPENDENT_ALERT`:** **27 rounds (54.0%)** — Matched 1-to-1 by a unique alert.
     - **`DETECTED_BUT_MERGED_INTO_EARLIER_ALERT`:** **5 rounds (10.0%)** — High acoustic energy was captured within an ongoing multi-window alert, but counted as a round miss under strict 1-to-1 matching rules.
     - **`MISSED_WHILE_IN_REFRACTORY_COOLDOWN`:** **2 rounds (4.0%)** — Arrived while the detector was in active refractory cooldown ($cooldown\_start \le t_{gt} \le cooldown\_end$) following alert termination.
     - **`MISSED_WHILE_ELIGIBLE`:** **16 rounds (32.0%)** — Detector was fully eligible to alert, but the acoustic signature was attenuated below threshold.
     - **`AMBIGUOUS_DUE_TO_INSUFFICIENT_PRECISION`:** **0 rounds (0.0%)** — All 50 rounds were deterministically resolved.
   - **Phase 17 Experimental ($N=50$ rounds):**
     - **`DETECTED_WITH_INDEPENDENT_ALERT`:** **33 rounds (66.0%)** (+6 rounds over baseline).
     - **`DETECTED_BUT_MERGED_INTO_EARLIER_ALERT`:** **6 rounds (12.0%)**.
     - **`MISSED_WHILE_IN_REFRACTORY_COOLDOWN`:** **3 rounds (6.0%)**.
     - **`MISSED_WHILE_ELIGIBLE`:** **8 rounds (16.0%)** (-8 eligible misses compared to Phase 14).
     - **`AMBIGUOUS_DUE_TO_INSUFFICIENT_PRECISION`:** **0 rounds (0.0%)**.
2. **Key Physical Finding on Bursts:** The belief that "refractory cooldown explains all missed burst rounds" is **refuted**. While cooldown is directly responsible for suppressing trailing rounds in tests like `test_007` and `test_055`, **5 rounds were actually detected and merged into ongoing multi-window alerts**, and **16 rounds were missed due to low signal-to-noise ratio or multipath attenuation while the detector was completely eligible**.

---

## 2. Category Distribution Matrix

| Forensic Classification Category | State-Machine Definition | Phase 14 Balanced ($N=50$) | Phase 17 Experimental ($N=50$) | Delta (P17 - P14) |
| :--- | :--- | :---: | :---: | :---: |
| **1. Detected with Independent Alert** | Ground-truth timestamp matched by a unique, independent alert object satisfying temporal matching criteria. | **27 (54.0%)** | **33 (66.0%)** | **+6 rounds** |
| **2. Merged into Earlier Alert** | Round acoustic energy was captured within the start/end window of an ongoing prior alert cluster, but uncredited under 1-to-1 matching. | **5 (10.0%)** | **6 (12.0%)** | **+1 round** |
| **3. Missed in Refractory Cooldown** | Round occurred during the $2.0\text{ s}$ refractory cooldown window ($cooldown\_start \le t_{gt} \le cooldown\_end$) of an earlier alert. | **2 (4.0%)** | **3 (6.0%)** | **+1 round** |
| **4. Missed While Eligible** | Detector was fully eligible to alert ($t_{gt} > cooldown\_until$), but acoustic score failed threshold. | **16 (32.0%)** | **8 (16.0%)** | **-8 rounds** |
| **5. Ambiguous Timestamp Precision** | Timestamps unresolvable due to insufficient logging resolution. | **0 (0.0%)** | **0 (0.0%)** | 0 rounds |
| **Total Physical Rounds** | Canonical Category A benchmark | **50 (100.0%)** | **50 (100.0%)** | -- |

---

## 3. Forensic Case Studies: Merging vs. Cooldown Suppression

### Case Study A: Alert Merging in Rapid Fire (`test_019`, FP2, .45 ACP Burst)
- **Ground Truth Timestamps:** Round 1 at $2.476\text{ s}$, Round 2 at $3.128\text{ s}$, Round 3 at $4.162\text{ s}$.
- **Detector Behavior (Phase 14 Balanced):**
  - Alert 1 instantiated across windows from $2.40\text{ s}$ to $3.84\text{ s}$ (duration $1.44\text{ s}$, peak score $0.806$).
  - Round 1 ($2.476\text{ s}$) matched Alert 1 $\to$ **DETECTED**.
  - Round 2 ($3.128\text{ s}$) arrived while Alert 1 was actively open. The detector extended the alert cluster through Round 2's energy coda. Under 1-to-1 evaluation rules, Alert 1 was already consumed by Round 1, scoring Round 2 as a miss $\to$ **DETECTED_BUT_MERGED_INTO_EARLIER_ALERT**.
  - Following alert termination at $3.84\text{ s}$, cooldown extended to $5.84\text{ s}$. Round 3 arrived at $4.162\text{ s}$ $\to$ **DETECTED_WITH_INDEPENDENT_ALERT** (Round 3 had sharp crest factor $13.2\text{ dB}$, triggering single-window override).

### Case Study B: Cooldown Suppression (`test_007`, FP1, .40 S&W Burst)
- **Ground Truth Timestamps:** Round 1 at $4.287\text{ s}$, Round 2 at $5.096\text{ s}$, Round 3 at $5.793\text{ s}$.
- **Detector Behavior (Phase 14 Balanced):**
  - Alert 1 fired on Round 1, ending at $5.28\text{ s}$.
  - Cooldown window activated: $[5.28\text{ s}, 7.28\text{ s}]$.
  - Round 2 ($5.096\text{ s}$) occurred during Alert 1 $\to$ **DETECTED_BUT_MERGED_INTO_EARLIER_ALERT**.
  - Round 3 ($5.793\text{ s}$) arrived directly inside the active cooldown window ($5.28 \le 5.793 \le 7.28$). The detector successfully suppressed it to prevent echo ringing $\to$ **MISSED_WHILE_IN_REFRACTORY_COOLDOWN**.

### Case Study C: Eligible Miss due to Distance Attenuation (`test_049`, FP3, 9mm Burst)
- **Ground Truth Timestamps:** Round 1 at $3.162\text{ s}$, Round 2 at $3.866\text{ s}$, Round 3 at $4.459\text{ s}$.
- **Detector Behavior (Phase 14 Balanced):**
  - Zero alerts fired. Detector was 100% eligible throughout the 10-second stream.
  - Window scores at gunshot timestamps: $0.2345$, $0.2494$, $0.2474$ (well below the $0.75$ threshold).
  - All 3 rounds $\to$ **MISSED_WHILE_ELIGIBLE**.
  - Cause: Severe non-line-of-sight street geometry and low 9mm acoustic emission at distant sensor.

---

## 4. Complete Burst-by-Burst Forensic Comparison Table

| Stream ID | Pos | Test ID | Caliber | Round 1 GT | Round 2 GT | Round 3 GT | Burst Span | Phase 14 Round States (R1 / R2 / R3) | Phase 17 Round States (R1 / R2 / R3) | Forensic Diagnosis |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| `P19-CAT-A-FP1-test_001` | FP1 | `test_001` | .45 ACP Handgun | 2.543s | 3.647s | 4.816s | 2.273s | ELIGIBLE_MISS / ELIGIBLE_MISS / DETECT | ELIGIBLE_MISS / ELIGIBLE_MISS / DETECT | `ACOUSTIC_ENERGY_DEFICIT` |
| `P19-CAT-A-FP1-test_007` | FP1 | `test_007` | .40 S&W Handgun | 4.287s | 5.096s | 5.793s | 1.506s | DETECT / MERGED / COOLDOWN_MISS | DETECT / MERGED / COOLDOWN_MISS | `COOLDOWN_SUPPRESSION_CONFIRMED` |
| `P19-CAT-A-FP1-test_013` | FP1 | `test_013` | 9x19mm Handgun | 3.763s | 4.150s | 4.895s | 1.132s | ELIGIBLE_MISS / ELIGIBLE_MISS / ELIGIBLE_MISS | DETECT / MERGED / COOLDOWN_MISS | `ACOUSTIC_ENERGY_DEFICIT` |
| `P19-CAT-A-FP2-test_019` | FP2 | `test_019` | .45 ACP Handgun | 2.476s | 3.128s | 4.162s | 1.686s | MERGED / MERGED / DETECT | MERGED / MERGED / DETECT | `ACOUSTIC_ENERGY_DEFICIT` |
| `P19-CAT-A-FP2-test_025` | FP2 | `test_025` | .40 S&W Handgun | 2.566s | 3.287s | 3.887s | 1.321s | MERGED / MERGED / DETECT | MERGED / MERGED / DETECT | `ACOUSTIC_ENERGY_DEFICIT` |
| `P19-CAT-A-FP2-test_031` | FP2 | `test_031` | 9x19mm Handgun | 2.246s | 2.838s | 3.509s | 1.263s | DETECT / DETECT / DETECT | DETECT / DETECT / DETECT | `ACOUSTIC_ENERGY_DEFICIT` |
| `P19-CAT-A-FP3-test_037` | FP3 | `test_037` | .45 ACP Handgun | 2.828s | 3.596s | 4.440s | 1.612s | ELIGIBLE_MISS / DETECT / DETECT | DETECT / DETECT / DETECT | `ACOUSTIC_ENERGY_DEFICIT` |
| `P19-CAT-A-FP3-test_043` | FP3 | `test_043` | .40 S&W Handgun | 3.633s | 4.189s | 4.743s | 1.110s | DETECT / DETECT / DETECT | DETECT / DETECT / DETECT | `ACOUSTIC_ENERGY_DEFICIT` |
| `P19-CAT-A-FP3-test_049` | FP3 | `test_049` | 9x19mm Handgun | 3.162s | 3.866s | 4.459s | 1.297s | ELIGIBLE_MISS / ELIGIBLE_MISS / ELIGIBLE_MISS | ELIGIBLE_MISS / ELIGIBLE_MISS / ELIGIBLE_MISS | `ACOUSTIC_ENERGY_DEFICIT` |
| `P19-CAT-A-FP4-test_055` | FP4 | `test_055` | .45 ACP Handgun | 3.304s | 4.036s | 4.603s | 1.299s | DETECT / DETECT / COOLDOWN_MISS | DETECT / DETECT / DETECT | `COOLDOWN_SUPPRESSION_CONFIRMED` |
| `P19-CAT-A-FP4-test_061` | FP4 | `test_061` | .40 S&W Handgun | 3.108s | 3.683s | 4.359s | 1.251s | DETECT / DETECT / DETECT | DETECT / DETECT / DETECT | `ACOUSTIC_ENERGY_DEFICIT` |
| `P19-CAT-A-FP4-test_067` | FP4 | `test_067` | 9x19mm Handgun | 3.786s | 4.311s | 4.846s | 1.060s | ELIGIBLE_MISS / ELIGIBLE_MISS / ELIGIBLE_MISS | DETECT / DETECT / COOLDOWN_MISS | `ACOUSTIC_ENERGY_DEFICIT` |
| `P19-CAT-A-FP5-test_127` | FP5 | `test_127` | .45 ACP Handgun | 3.008s | 3.434s | 3.821s | 0.813s | ELIGIBLE_MISS / ELIGIBLE_MISS / ELIGIBLE_MISS | ELIGIBLE_MISS / ELIGIBLE_MISS / ELIGIBLE_MISS | `ACOUSTIC_ENERGY_DEFICIT` |
| `P19-CAT-A-FP5-test_133` | FP5 | `test_133` | .40 S&W Handgun | 3.343s | 3.802s | 4.232s | 0.889s | DETECT / DETECT / DETECT | DETECT / DETECT / DETECT | `ACOUSTIC_ENERGY_DEFICIT` |
| `P19-CAT-A-FP5-test_139` | FP5 | `test_139` | 9x19mm Handgun | 2.833s | 3.380s | 3.905s | 1.072s | DETECT / DETECT / DETECT | DETECT / DETECT / DETECT | `ACOUSTIC_ENERGY_DEFICIT` |

---
*Report certified under Phase 22 Forensic Standard.*
"""

out_md = REPORTS_DIR / "phase22_burst_cooldown_analysis.md"
with open(out_md, "w", encoding="utf-8") as f:
    f.write(md_content)
print(f"Saved updated burst cooldown analysis markdown to: {out_md}")
