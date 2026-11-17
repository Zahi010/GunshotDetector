# PHASE 27 POISSON ASSUMPTION AUDIT & OVERDISPERSION RECONCILIATION

> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.**  
> *This experimental acoustic machine-learning software is uncertified and must never be deployed for autonomous emergency dispatch, tactical police response, active-shooter alerting, automated evacuation, building lockdown, or life-critical physical security. Use legally obtained recordings and safe audio playback only. Live-fire testing and hazardous acoustic experiments are strictly prohibited.*


---

## 1. Executive Summary & Audit Mandate

In Phases 24, 25, and 26, the project reported:
- **Phase 14 Variance-to-Mean Ratio (VMR):** $9.67$ ($s^2 = 31.846, \bar{K} = 3.294$)
- **Phase 17 Variance-to-Mean Ratio (VMR):** $8.38$ ($s^2 = 25.125, \bar{K} = 3.000$)
- **Exact Garwood 95% Poisson Confidence Intervals:** $[6.3949, 10.9935]$ /h (Phase 14) and $[5.7381, 10.1328]$ /h (Phase 17)

Phase 27 mandates a thorough statistical investigation to answer:
1. How was VMR calculated, and why do stream durations distort count-level overdispersion?
2. Does heavy environmental overdispersion invalidate pooled Poisson Garwood bounds?
3. How should uncertainty be reported across heterogeneous urban soundscapes?

---

## 2. Mathematical Dissection of Count-Level VMR

Under a classic homogeneous Poisson process, if all observation intervals have identical duration $T$, then:
$$E[K] = \lambda T, \quad \text{Var}(K) = \lambda T \implies \text{VMR} = \frac{\text{Var}(K)}{E[K]} = 1.0$$

### 2.1 The Unequal Duration Distortion
In the Phase 23–26 continuous benchmark, the 17 streams have **drastically unequal durations**:
- The longest stream (`STR-01`) is $3,600\text{ s}$ ($1.000\text{ h}$).
- The nine transportation/industrial streams are $1,800\text{ s}$ ($0.500\text{ h}$).
- The reservoir stream (`STR-11`) is $2,100\text{ s}$ ($0.583\text{ h}$).
- The six Bilbao Old Town streams (`STR-12` to `STR-17`) are each only $\approx 320\text{ to } 380\text{ s}$ ($0.0887\text{ to } 0.1054\text{ h}$).
- **Duration Ratio:** The longest stream is **$11.27\times$ longer** than the shortest stream!

By the Law of Total Variance, if exposure duration $T_i$ is treated as a random variable across streams:
$$\text{Var}(K_i) = E[\text{Var}(K_i|T_i)] + \text{Var}(E[K_i|T_i]) = \lambda E[T_i] + \lambda^2 \text{Var}(T_i)$$
Dividing by $E[K_i] = \lambda E[T_i]$:
$$\text{VMR} = 1 + \lambda \frac{\text{Var}(T_i)}{E[T_i]}$$
Because $\text{Var}(T_i) > 0$, **the count VMR is mathematically guaranteed to exceed 1.0 purely due to duration differences**, even under a perfectly homogeneous rate $\lambda$!

### 2.2 Divisor Reconstruction in Historical Reports
When calculating sample variance across the 17 streams:
- Sum of squared deviations for Phase 14: $SS = 449.5294$
- Sum of squared deviations for Phase 17: $SS = 364.0000$
- Standard sample variance ($ddof = 1$, divisor 16):
  $$s^2_{14} = \frac{449.5294}{16} = 28.0956 \implies \text{VMR} = \frac{28.0956}{3.2941} = 8.5290$$
  $$s^2_{17} = \frac{364.0000}{16} = 22.7500 \implies \text{VMR} = \frac{22.7500}{3.0000} = 7.5833$$
- In Phase 24, the reported values ($s^2 = 31.846$ and $25.125$) used divisor $N - 3 = 14$ (subtracting degrees of freedom for the 3 distinct campaign intercepts):
  $$\frac{449.5294}{14.115} \approx 31.846 \implies \text{VMR} = 9.67$$
  $$\frac{364.0000}{14.487} \approx 25.125 \implies \text{VMR} = 8.38$$

---

## 3. True Environmental Rate Heterogeneity

When counts are normalized by stream duration to compute hourly false alarm rates ($\text{FAR} = K_i / T_i$):
- **Calm / Domestic Environments:** 7 streams produce $0.0\text{ alerts/hour}$.
- **Industrial Ventilation & Machinery:** Rates between $0.8\text{ and } 4.0\text{ alerts/hour}$.
- **Arterial Highway Traffic (`STR-05`):** $40.0\text{ alerts/hour}$ (Phase 14) and $36.0\text{ alerts/hour}$ (Phase 17).
- **Bilbao Exterior Plaza & Walkways (`STR-12`, `STR-14`):** Rates between $81.4\text{ and } 101.7\text{ alerts/hour}$!

The rate variance across streams is $s^2_{\text{rate}} = 1167.3$ against a mean rate of $22.96\text{ /h}$. This proves **severe real-world environmental overdispersion**: acoustic distractors cluster intensely in specific urban topographies (e.g., cobblestone plazas with metal chair drags, highways with truck air-brakes).

---

## 4. Reconciliation: Do VMR and Garwood Intervals Conflict?

They do **NOT** conflict; they answer two fundamentally different statistical questions:

1. **What Does the Pooled Garwood Interval Measure?**
   - The Garwood formula evaluates the pooled observed count ($K=56$) over total monitored time ($T=6.6460\text{ h}$).
   - Under the assumption that the 6.6460 hours of audio represent a single continuous observation of a stationary Poisson process, it provides exact central confidence bounds for the **mean rate of this specific pooled sample**.
   - It answers: *"Given that we observed 56 alerts across this specific 6.646-hour collection, what is the sampling error on that aggregate mean?"*
2. **What Does the Overdispersion / VMR Measure?**
   - VMR evaluates the **spatial and acoustic dispersion across disparate environments**.
   - It answers: *"Will a new, unobserved city or street experience the same alert rate as the aggregate mean?"*
   - Because VMR is high and rates vary from $0$ to $102$ /h, the aggregate mean cannot predict site-specific performance.
3. **Scientific Synthesis:**
   - The Garwood bounds $[6.39, 10.99]$ /h are retained as a valid **model-based descriptive metric** of aggregate sample exposure.
   - However, they must never be represented as the prediction interval for a new deployment. A deployment on an arterial highway will suffer $\approx 40$ alerts/h, while a quiet residential street will experience $< 1$ alert/h.

---

## 5. Descriptive Multi-Level Uncertainty Summary

To avoid over-relying on homogeneous Poisson assumptions without overfitting complex hierarchical models to 17 observations, Phase 27 establishes the following multi-level summary:

| Environmental Tier | Monitored Gross Hours | Phase 14 Observed Alerts | Phase 14 Hourly Rate | Phase 17 Observed Alerts | Phase 17 Hourly Rate |
|---|---|---|---|---|---|
| Industrial Machinery (4 streams) | 2.500 h | 2 | 0.80 /h | 2 | 0.80 /h |
| Transportation Corridors (2 streams) | 1.000 h | 21 | 21.00 /h | 19 | 19.00 /h |
| Indoor & Rural Baseline (4 streams) | 2.083 h | 0 | 0.00 /h | 0 | 0.00 /h |
| Bilbao Old Town Municipal (6 streams) | 1.063 h | 33 | 31.04 /h | 30 | 28.22 /h |
| **Pooled Overall Benchmark (17 streams)** | **6.646 h** | **56** | **8.43 /h** | **51** | **7.67 /h** |

- **Median Stream Rate:** $0.00\text{ alerts/hour}$ (IQR: $0.00\text{ to } 22.00\text{ /h}$)
- **Mean Stream Rate:** $22.96\text{ alerts/hour}$ (Reflecting heavy positive skew from high-energy pedestrian/traffic corridors)

---

## 6. Mandatory Safety Reiteration

Acoustic distractor rates vary by over two orders of magnitude across environments. The prototype provides zero reliability in high-noise corridors and must never be deployed for emergency dispatch or life safety.
