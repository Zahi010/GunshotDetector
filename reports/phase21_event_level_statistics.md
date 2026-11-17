# Phase 21: Unadjusted Event-Level Reproduction & Paired Contingency Analysis

> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY**  
> *This experimental acoustic machine-learning system is not certified and must never be used for autonomous emergency dispatch, police response, active-shooter alerting, automated evacuation, or critical physical security. Use legally obtained recorded audio and safe playback only. No live-fire testing or hazardous acoustic experiments.*

---

## 1. Executive Summary

Phase 21 verifies the unadjusted event-level detection performance of the default baseline (**Phase 14 Balanced**) versus the experimental candidate (**Phase 17 Experimental**) on the 50 canonical physical gunshot rounds of Category A (ShotSpotter Pittsburgh PA DQV 2018).

This reproduction confirms:
1. Exact replication of the $2 \times 2$ event-level contingency matrix:
   - **Both detected:** 27 rounds ($54.0\%$)
   - **Phase 14 only detected:** 0 rounds ($0.0\%$)
   - **Phase 17 only detected:** 6 rounds ($12.0\%$)
   - **Neither detected:** 17 rounds ($34.0\%$)
2. Overall round recall:
   - **Phase 14 Balanced:** $54.00\%$ (27 of 50 rounds)
   - **Phase 17 Experimental:** $66.00\%$ (33 of 50 rounds)
   - **Absolute Difference:** $+12.00$ percentage points
3. Exact two-sided binomial McNemar $p$-value:
   $$p = 2 \cdot \binom{6}{0} (0.5)^6 = 2 \cdot \frac{1}{64} = 0.03125$$
   The unadjusted event-level result is verified as statistically significant at $\alpha = 0.05$.

---

## 2. Paired Event-Level Contingency Table

```
                           Phase 17 Experimental
                           Detected     Missed     Total
Phase 14       Detected       27           0         27  (54.0%)
Balanced       Missed          6          17         23  (46.0%)
               Total          33          17         50  (100.0%)
                            (66.0%)     (34.0%)
```

### Discordant Pair Characterization
The 6 discordant events ($b=0, c=6$) where Phase 17 detected a gunshot missed by Phase 14 are:
1. `P19-CAT-A-FP1-test_004-EV01`: FP1, single shot, $t=3.562\text{ s}$ (.45 ACP Handgun)
2. `P19-CAT-A-FP1-test_013-EV01`: FP1, burst round 1, $t=3.763\text{ s}$ (9x19mm Handgun)
3. `P19-CAT-A-FP3-test_037-EV01`: FP3, burst round 1, $t=2.828\text{ s}$ (.45 ACP Handgun)
4. `P19-CAT-A-FP4-test_055-EV03`: FP4, burst round 3, $t=4.603\text{ s}$ (.45 ACP Handgun)
5. `P19-CAT-A-FP4-test_067-EV01`: FP4, burst round 1, $t=3.786\text{ s}$ (9x19mm Handgun)
6. `P19-CAT-A-FP4-test_067-EV02`: FP4, burst round 2, $t=4.311\text{ s}$ (9x19mm Handgun)

Crucially, **Phase 14 never detected an event that Phase 17 missed** ($b = 0$).

---

## 3. Assumptions and Vulnerabilities of the Event-Level McNemar Test

The exact McNemar test relies on the fundamental assumption that **each paired observation is independent and identically distributed (i.i.d.)**.
In the Pittsburgh dataset, this assumption is severely challenged by physical clustering:
- **Hierarchical Nesting:** The 50 rounds are nested within only 20 recordings, 5 firing positions, and 1 municipal testing campaign.
- **Acoustic Covariance:** Multiple rounds in the same recording share identical propagation geometry, building facades, atmospheric temperature, and sensor hardware.
- **Refractory Interaction:** Successive rounds in three-round bursts occur within milliseconds, interacting directly with detector cooldown logic.

Consequently, while $p = 0.03125$ is the exact mathematical result under the i.i.d. event assumption, cluster-aware validation is essential to evaluate the true stability of this effect.

---
*Report certified under Phase 21 Forensic Audit protocol.*
