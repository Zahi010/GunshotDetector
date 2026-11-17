# Phase 30 Final Engineering Report & Synthesis Audit

> **MANDATORY SAFETY DESIGNATION**  
> **RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.**  
> This experimental acoustic machine-learning software is uncertified and must never be deployed for autonomous emergency dispatch, tactical police response, active-shooter alerting, automated evacuation, building lockdown, or life-critical physical security. Use legally obtained recordings and safe audio playback only. Live-fire testing and hazardous acoustic experiments are strictly prohibited.

---

## 1. Executive Summary & Core Mission

Phase 30 executes an independent, prospective validation and forensic diagnostic audit of the acoustic gunshot detection project.

### Core Mission Achievements
1. **Baseline Freeze & Cryptographic Verification:** Verified the exact SHA-256 digests and file sizes of all frozen models (`model_phase14.py`, `model_phase17.py`, `model_phase13.py`, `model_phase9.py`) and historical release archives (`gunshot_detection_phase29.zip` through `phase20.zip`).
2. **Non-Invasive Diagnostic Instrumentation (`instrumented_detector.py`):** Constructed a cycle-accurate telemetry wrapper that logged 44,994 sub-windows across 6.000 hours of continuous audio, capturing raw model scores, semantic gating logits, animal classifier activations, suppression penalties, and state-machine transitions.
3. **Strict Invariance Verification:** Proved that the instrumented detector achieves **100.0% exact mathematical identity** with the frozen uninstrumented models, reproducing the exact 72 Phase 14 alerts and 108 Phase 17 alerts on AeroSonicDB with $\Delta t = 0.0000\text{ s}$ and $\Delta s = 0.0000$ score deviation.
4. **Resolution of Aircraft Suppression Mechanism:** Evaluated the 25 candidate multi-alert sequences from Phase 28/29. Proved that animal suppression directly caused alert fragmentation in 11 sequences (44.0%), while pure acoustic fluctuations caused fragmentation in 9 sequences (36.0%), and 5 sequences involved co-occurring mechanisms (20.0%).
5. **Discovery of Phase 17 State-Machine Defect:** Discovered that `model_phase17.py` omitted the `else: active_cluster = []` reset branch in its state machine, allowing isolated unconfirmed transient windows to leak across multi-minute gaps and compound false alerts.
6. **Independent Source Acceptance & Provenance Audit:** Evaluated 12 candidate audio repositories. Formally rejected discrete clip concatenation and synthetic audio. Documented public API WAF access barriers (`HTTP 403 Forbidden`) under strict anti-circumvention rules. Certified the 23-stream, 4-campaign continuous negative corpus ($45,525.575\text{ s}$, $12.6460\text{ hr}$).
7. **Cluster-Aware Statistical Analysis ($G=4$):** Demonstrated that while stream-level paired tests yield non-significant differences ($W=8.0, p=0.1953$; sign test $p=0.7266$), the small-sample limit of $G=4$ independent campaigns mathematically bounds statistical power ($p_{\min} = 0.125$).
8. **Final Baseline Governance Decision:** Definitively retained **Phase 14 Balanced as the Default Research Baseline**. Promotion of Phase 17 Experimental is rejected.

---

## 2. Separation of Findings

To ensure transparent scientific governance, findings are structured into distinct categories:

### A. Historical Findings (Phases 14–29)
- **Phase 14 Balanced** was established as the baseline with calibrated semantic gating (thunder, fireworks, dog bark, crackle, siren) and ballistic crest factor gating ($\ge 8.8\text{ dB}$).
- **Phase 17 Experimental** added an animal vocalization suppression heuristic ($\text{animal\_s} > 0.35 \land \text{animal\_s} \ge 2.0 \times \text{gun\_s}$, applying a $0.30\times$ penalty).
- Controlled live-fire testing in Pittsburgh (50 physical rounds across 20 recordings) favored Phase 17 in raw sensitivity (33/50 vs 27/50, unadjusted McNemar $p = 0.03125$).
- In Phase 27, AeroSonicDB evaluation revealed that Phase 17 produced 36 additional false alerts (+50.0%) and 1.77 hours of Convention B cooldown blindness.
- Phase 29 resolved the reported Phase 14 threshold discrepancy as a narrative documentation error (confirming that both models ran with $0.75 / 0.88 / 0.48$).

### B. Newly Acquired Empirical Evidence (Phase 30)
- **Candidate Source Screening:** Screened 12 candidate corpora against 10 strict criteria. Verified that existing continuous corpus (23 streams across 4 independent campaigns in UK, Austria, Spain, Australia totaling 12.6460 gross hours) represents the only uncompromised, non-concatenated, authentic continuous dataset currently accessible under lawful open protocols.
- **Access Boundary Logging:** Probed Zenodo REST APIs for large bioacoustic collections (Cornell Sapsucker Woods, DataSEC, Białowieża Forest); recorded `HTTP 403 Forbidden` WAF gates. Enforced anti-circumvention policy by refusing to bypass WAF challenges or inject unauthorized credentials.
- **Instrumented Score Traces:** Generated `reports/phase30_instrumented_score_traces.csv` containing 44,994 cycle-accurate 22-dimensional telemetry rows.

### C. Independently Reproduced Metrics
- **Gross Exposure:** $45,525.575\text{ seconds}$ ($12.6460\text{ gross hours}$).
- **Observed False Alerts:** Phase 14 Balanced = 128 alerts; Phase 17 Experimental = 159 alerts. Net difference = $+31$ alerts for Phase 17 (+24.2% inflation).
- **Gross Alert Rates:** Phase 14 = $10.1218/\text{hr}$; Phase 17 = $12.5731/\text{hr}$.
- **Convention A (Instantaneous Cooldown):** Phase 14 FAR = $10.1790/\text{hr}$ (excluded = $255.84\text{ s}$); Phase 17 FAR = $12.6612/\text{hr}$ (excluded = $316.56\text{ s}$).
- **Convention B (Cluster-Extended Cooldown):** Phase 14 FAR = $10.2237/\text{hr}$ (excluded = $453.92\text{ s}$); Phase 17 FAR = $14.6243/\text{hr}$ (excluded = $6,385.20\text{ s}$).

### D. Instrumented Mechanism Findings
- **Hypothesis Resolution:** In 11 of 25 multi-alert sequences (44.0%), the animal suppression penalty ($0.30\times$) directly forced sub-window scores below $\text{threshold\_off} = 0.48$, causing premature alert termination followed by score recovery and re-assertion.
- **Waveform Modulation:** In 9 of 25 sequences (36.0%), animal suppression was inactive, proving that jet engine throttle changes and multi-modal acoustics naturally oscillate across hysteresis thresholds.
- **State-Machine Leakage Defect:** Discovered that Phase 17 fails to clear unconfirmed candidate windows, allowing isolated sub-windows to accumulate across multi-minute temporal intervals.

---

## 3. Comprehensive Performance Comparison Table

```
┌──────────────────────────────────────┬──────────────────────┬────────────────────────┬────────────────────────────────────────┐
│ Evaluation Metric / Dimension        │ Phase 14 Balanced    │ Phase 17 Experimental  │ Engineering Determination / Variance   │
├──────────────────────────────────────┼──────────────────────┼────────────────────────┼────────────────────────────────────────┤
│ Official System Role                 │ Default Research Base│ Selectable Experimental│ Retained Baseline vs Rejected Profile  │
│ Threshold Base / High / Off          │ 0.75 / 0.88 / 0.48   │ 0.75 / 0.88 / 0.48     │ Verified Identical Runtime Parameters  │
│ Confirm Windows / Cooldown Secs      │ 2 windows / 2.0 s    │ 2 windows / 2.0 s      │ Verified Identical Hysteresis Settings │
│ Animal Vocalization Suppression      │ Disabled (False)     │ Enabled (0.35 / 2.0x)  │ Score attenuated by 0.30x when active  │
│ State Machine Architecture           │ Clears unconfirmed   │ Leaks unconfirmed      │ Phase 17 exhibits cluster retention bug│
├──────────────────────────────────────┼──────────────────────┼────────────────────────┼────────────────────────────────────────┤
│ Pittsburgh Controlled Live-Fire      │ 27 / 50 rounds (54%) │ 33 / 50 rounds (66%)   │ Phase 17 detects 6 more physical rounds│
│ Terrestrial Urban FAR (3 Campaigns)  │ 56 alerts (8.43/hr)  │ 51 alerts (7.67/hr)    │ Phase 17 has 5 fewer alerts in Europe  │
│ Aviation Distractor FAR (AeroSonicDB)│ 72 alerts (12.00/hr) │ 108 alerts (18.00/hr)  │ Phase 14 has 36 FEWER alerts (Superior)│
├──────────────────────────────────────┼──────────────────────┼────────────────────────┼────────────────────────────────────────┤
│ Cumulative False Alerts (12.65 hr)   │ 128 alerts           │ 159 alerts             │ Phase 14 has 31 FEWER alerts overall   │
│ Gross False Alert Rate               │ 10.1218 alerts/hr    │ 12.5731 alerts/hr      │ Phase 14 FAR is 2.45/hr lower          │
│ Convention A Eligible Rate           │ 10.1790 alerts/hr    │ 12.6612 alerts/hr      │ Phase 14 FAR is 2.48/hr lower          │
│ Convention B Eligible Rate           │ 10.2237 alerts/hr    │ 14.6243 alerts/hr      │ Phase 14 FAR is 4.40/hr lower          │
│ Convention B Cooldown Dead Time      │ 453.92 s (0.99%)     │ 6385.20 s (14.03%)     │ Phase 17 has 14x MORE dead time        │
│ AeroSonicDB Blindness Percentage     │ 1.77% of duration    │ 29.56% of duration     │ Phase 17 blind for nearly 1/3 of time  │
├──────────────────────────────────────┼──────────────────────┼────────────────────────┼────────────────────────────────────────┤
│ Paired Wilcoxon Signed-Rank Test     │ W = 8.0              │ W = 8.0                │ p = 0.1953125 (Statistically Non-Sig)  │
│ Paired Exact Binomial Sign Test      │ 5 favoring P14       │ 3 favoring P17         │ p = 0.7265625 (Statistically Non-Sig)  │
│ LOCO Sensitivity Stability           │ Robust across subsets│ Highly erratic         │ P17 advantage disappears without EU set│
└──────────────────────────────────────┴──────────────────────┴────────────────────────┴────────────────────────────────────────┘
```

---

## 4. Methodological & Governance Recommendations

1. **Definitive Baseline Preservation:**
   **Phase 14 Balanced** is officially confirmed and retained as the **Default Research Baseline**. It exhibits lower cumulative false alert rates, superior resilience against broadband aviation noise, 14 times less cooldown dead time, and an uncompromised state machine.
2. **Rejection of Phase 17 Experimental:**
   Phase 17 is permanently barred from baseline promotion. Its animal suppression mechanism induces severe false-alert fragmentation on aircraft overflights, and its merger logic suffers from state-machine cluster leakage.
3. **Future Aircraft Discriminator Hypothesis:**
   Future model development should not rely on heuristic animal-suppression multipliers. Instead, specialized low-frequency harmonic tracking and multi-band Doppler estimators should be trained on continuous aviation corpora.
4. **Mandatory Safety Disclaimer:**
   The software remains an experimental research demonstrator. Field deployment for life-safety or automated dispatch is strictly prohibited.

