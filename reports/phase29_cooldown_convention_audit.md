# RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY

> [!CAUTION]
> **MANDATORY SAFETY DESIGNATION**  
> **RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.**  
> This experimental acoustic machine-learning research software is uncertified and must never be deployed for autonomous emergency dispatch, tactical police response, active-shooter alerting, automated evacuation, building lockdown, or life-critical physical security.  
> Use legally obtained recordings and safe audio playback only. Live-fire testing and hazardous acoustic experiments are strictly prohibited.

---

# PHASE 29 FORENSIC AUDIT REPORT
## Cooldown Accounting Conventions, Monitoring Availability & Exposure Denominator Forensics

**Document Identifier:** `PHASE29-REP-COOLDOWN-CONVENTION-AUDIT`  
**Phase:** `PHASE_29_CONFIGURATION_VERIFICATION_AIRCRAFT_VALIDATION_ROBUSTNESS_AUDIT`  
**Focus:** Independent Verification of Cooldown Exclusion Conventions (Convention A vs Convention B), Interval Union Logic, and Exposure Accounting

---

## 1. Executive Summary

In acoustic event detection benchmarking, the calculation of false-alert rates (FAR) requires dividing the number of observed non-target alerts by a temporal denominator. When detectors implement refractory cooldown logic to suppress secondary acoustic echoes and reverberation, the time interval during which the detector is refractory or actively alerting represents non-monitored "dead time."

Phase 28 established two distinct accounting conventions:
- **Convention A (Instantaneous Alert Union):** $[t_{\text{start}}, t_{\text{start}} + 2.0\text{ s}]$
- **Convention B (Cluster-Extended Union):** $[t_{\text{start}}, t_{\text{end}} + 2.0\text{ s}]$

This forensic audit rigorously verified the implementation of both conventions across the entire 23-stream cumulative negative audio benchmark (45,525.575 gross seconds / 12.6460 gross hours) across both Phase 14 Balanced and Phase 17 Experimental.

### Headline Findings:
1. **Mathematical Divergence:**
   - Under **Convention A**, total cooldown exclusions are **255.84 seconds** for Phase 14 (0.56% of monitored time) and **316.56 seconds** for Phase 17 (0.70% of monitored time).
   - Under **Convention B**, total cooldown exclusions expand to **453.92 seconds** for Phase 14 (1.00% of monitored time) and **6,385.20 seconds** for Phase 17 (**14.03% of cumulative time**, and **29.09% of AeroSonicDB time**).
2. **Conceptual Difference:** Convention A measures refractory dead-time assuming alerts are point events, whereas Convention B measures true operational "system unavailability" (the period during which the detector is either continuously sounding an active alert or in post-event reset).
3. **Strict Policy:** The two conventions must never be blended in the same headline comparison. When citing eligible exposure or eligible alert rate, the convention must be explicitly labeled.

---

## 2. Mathematical Definition of Cooldown Conventions

Let a stream contain $K$ detected alerts indexed by $k \in \{1, \dots, K\}$, where each alert record $k$ possesses an onset timestamp $s_k$ and a termination timestamp $e_k \ge s_k$. The refractory parameter is $\tau_{\text{cd}} = 2.0\text{ seconds}$, and the gross stream duration is $T_{\text{gross}}$.

### 2.1 Convention A: Instantaneous Alert Union
Convention A treats each alert as an instantaneous trigger occurring at $s_k$, projecting a fixed 2.0-second refractory window:
$$I_k^{(A)} = [s_k, \min(s_k + \tau_{\text{cd}}, T_{\text{gross}})]$$
The total excluded duration under Convention A is the Lebesgue measure of the union of all intervals:
$$D_{\text{ex}}^{(A)} = \lambda\left( \bigcup_{k=1}^K I_k^{(A)} \right)$$
Eligible monitoring exposure under Convention A is:
$$T_{\text{elig}}^{(A)} = T_{\text{gross}} - D_{\text{ex}}^{(A)}$$

### 2.2 Convention B: Cluster-Extended Union
Convention B recognizes that multi-window alerts span an active duration $[s_k, e_k]$. The detector is actively tracking the event throughout this span and remains blind to new initiations until $\tau_{\text{cd}}$ seconds after the event concludes:
$$I_k^{(B)} = [s_k, \min(e_k + \tau_{\text{cd}}, T_{\text{gross}})]$$
The total excluded duration under Convention B is:
$$D_{\text{ex}}^{(B)} = \lambda\left( \bigcup_{k=1}^K I_k^{(B)} \right)$$
Eligible monitoring exposure under Convention B is:
$$T_{\text{elig}}^{(B)} = T_{\text{gross}} - D_{\text{ex}}^{(B)}$$

Because $e_k \ge s_k$ for all $k$, it is a mathematical identity that $I_k^{(A)} \subseteq I_k^{(B)}$, and therefore:
$$D_{\text{ex}}^{(B)} \ge D_{\text{ex}}^{(A)} \implies T_{\text{elig}}^{(B)} \le T_{\text{elig}}^{(A)}$$

---

## 3. Comprehensive Metric Comparison Table

The following table presents the independent, stream-by-stream verified figures across all 23 recordings for both detectors:

| Metric | Phase 14 Balanced (Default Baseline) | Phase 17 Experimental (Selectable Profile) | Difference (P17 - P14) |
| :--- | :---: | :---: | :---: |
| **Gross Audio Duration (s)** | 45,525.575 s | 45,525.575 s | 0.000 s |
| **Gross Audio Duration (hr)** | 12.6460 h | 12.6460 h | 0.0000 h |
| **Total Observed Alerts** | 128 | 159 | +31 alerts (+24.2%) |
| **Gross False-Alert Rate (FAR)** | **10.1218 / hr** | **12.5732 / hr** | **+2.4514 / hr** |
| **Convention A Excluded Time (s)** | 255.84 s | 316.56 s | +60.72 s |
| **Convention A Excluded Proportion**| 0.56% | 0.70% | +0.14% |
| **Convention A Eligible Time (hr)** | 12.5749 h | 12.5581 h | -0.0168 h |
| **Convention A Eligible FAR** | **10.1790 / hr** | **12.6612 / hr** | **+2.4822 / hr** |
| **Convention B Excluded Time (s)** | 453.92 s | 6,385.20 s | +5,931.28 s (+1,306%) |
| **Convention B Excluded Proportion**| 1.00% | 14.03% | +13.03% |
| **Convention B Eligible Time (hr)** | 12.5199 h | 10.8723 h | -1.6476 h (-13.1%) |
| **Convention B Eligible FAR** | **10.2237 / hr** | **14.6243 / hr** | **+4.4005 / hr** |

---

## 4. Operational Meaning of the Convention B Denominator Collapse

Under Convention A, both models exhibit nearly identical exposure denominators ($\sim 12.56$ hours), and the alert rate difference reflects the raw alert count (+2.48 alerts/hr).

However, under Convention B, an operational pathology in Phase 17 becomes apparent:
1. In the six AeroSonicDB airport perimeter streams, Phase 17's alert clusters during jet flyovers spanned prolonged multi-second durations.
2. In stream `P27-AERO-STR-01`, Phase 17 logged 28 alerts spanning 1,189.60 seconds of excluded time (33.0% of the hour).
3. In stream `P27-AERO-STR-05`, Phase 17 logged 25 alerts spanning 1,466.88 seconds of excluded time (40.7% of the hour).
4. In stream `P27-AERO-STR-06`, Phase 17 logged 23 alerts spanning 1,607.52 seconds of excluded time (**44.7% of the hour**).

Across the entire 6 hours of AeroSonicDB, Phase 17 excluded **6,283.28 seconds (1.7454 hours)**. Phase 17 was deaf for **29.09% of the monitored time**. In contrast, Phase 14 excluded only **342.00 seconds (1.58% of the time)**.

Because Convention B properly penalizes this massive system unavailability by subtracting it from the denominator, Phase 17's eligible alert rate surges to **14.6243 alerts/hr** (+43.0% higher than Phase 14's 10.2237 alerts/hr).

---

## 5. Audit Recommendations & Governance Rules

1. **Retain Convention B for System Availability Reporting:** Convention B must be retained because it reflects real-world operational availability. A detector that is continuously asserting an active alert cannot detect a secondary incoming gunshot.
2. **Explicit Labeling:** All technical tables must explicitly state whether rates are computed against `Gross Exposure`, `Convention A Eligible Exposure`, or `Convention B Eligible Exposure`.
3. **No Blending:** Never present Phase 14 under Convention A and Phase 17 under Convention B, or vice versa, in comparative evaluations.

