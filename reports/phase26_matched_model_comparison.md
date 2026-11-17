# PHASE 26 MATCHED MODEL COMPARISON: PHASE 14 BALANCED VS. PHASE 17 EXPERIMENTAL

> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.**  
> *This experimental acoustic machine-learning software is uncertified and must never be deployed for autonomous emergency dispatch, tactical police response, active-shooter alerting, automated lockdown or evacuation, or life-critical physical security. Use legally obtained recordings and safe audio playback only. Live-fire testing and hazardous acoustic experiments are strictly prohibited.*


---

## 1. Executive Summary & Evaluation Protocol

This report provides the matched head-to-head empirical comparison of the two frozen detectors under the Phase 26 Tripartite Denominator Framework:
1. **Phase 14 Balanced (`model_phase14.py`):** The frozen **default research baseline** for acoustic event detection.
2. **Phase 17 Experimental (`model_phase17.py`):** The frozen **selectable experimental profile** incorporating secondary animal and transient suppression filters.

Both models were evaluated on identical audio streams under identical pre-registered decision thresholds ($\theta = 0.75$) and an identical 2.0-second post-alert refractory cooldown period.

In Phase 26, intensive investigation of prospective continuous audio sources (Candidate A: AeroSonicDB, Candidate B: International Soundscape Database) established that Candidate A requires conditional access handling due to upstream Cloudflare anti-bot verification (HTTP 403), while Candidate B was rejected due to clip discontinuity (30-second clips). Because no synthetic concatenation or clip looping was permitted, **0 new continuous hours were acquired in Phase 26**. Consequently, the empirical negative benchmark remains at 6.6460 gross hours (17 continuous streams across 3 independent European campaigns).

---

## 2. Head-to-Head Comparative Metrics

```
==================================================================================================
METRIC                                   PHASE 14 BALANCED            PHASE 17 EXPERIMENTAL
==================================================================================================
Model Role                               DEFAULT_RESEARCH_BASELINE    SELECTABLE_EXPERIMENTAL
Evaluated Continuous Streams             17 streams                   17 streams
Gross Calendar Exposure                  6.6460 hours (23,925.58 s)   6.6460 hours (23,925.58 s)
Refractory Cooldown Excluded Duration    111.92 seconds               101.92 seconds
Net Eligible Exposure Duration           6.6149 hours (23,813.66 s)   6.6177 hours (23,823.66 s)
Total Observed False Alerts              56                           51
Gross Alert Rate (FAR_gross)             8.4261 alerts/hour           7.6738 alerts/hour
Eligible Alert Rate (FAR_eligible)       8.4657 alerts/hour           7.7066 alerts/hour
Exact Garwood 95% Poisson CI             [6.3949, 10.9935]            [5.7381, 10.1328]
Empirical MTBFA                          7.09 minutes (0.1181 h)      7.79 minutes (0.1298 h)
--------------------------------------------------------------------------------------------------
Stream Comparison Breakdown              Reference                    3 Improved, 14 Equal, 0 Worse
Paired Wilcoxon Signed-Rank Test         Reference                    W = 10.0, p = 0.125 (p >= 0.05)
Model Promotion Determination            RETAIN AS BASELINE           INCONCLUSIVE (REJECT PROMOTION)
==================================================================================================
```

---

## 3. Tripartite Denominator Breakdown

### 3.1 Denominator 1: Gross Monitored-Time Rate ($\text{FAR}_{\text{gross}}$)
$$\text{FAR}_{\text{gross}} = \frac{K}{T_{\text{gross\_hr}}}$$
- Phase 14 Balanced: $56 / 6.64599 = 8.4261\text{ alerts/hour}$
- Phase 17 Experimental: $51 / 6.64599 = 7.6738\text{ alerts/hour}$
- Absolute Delta: $-0.7523\text{ alerts/hour}$ ($-8.93\%$)

### 3.2 Denominator 2: Cooldown-Adjusted Eligible Rate ($\text{FAR}_{\text{eligible}}$)
$$\text{FAR}_{\text{eligible}} = \frac{K}{T_{\text{eligible\_hr}}}$$
- Phase 14 Balanced: $56 / 6.61491 = 8.4657\text{ alerts/hour}$
- Phase 17 Experimental: $51 / 6.61768 = 7.7066\text{ alerts/hour}$
- Absolute Delta: $-0.7591\text{ alerts/hour}$ ($-8.97\%$)

### 3.3 Denominator 3: Common Matched-Exposure Comparison
- Evaluating recording-by-recording over identical timestamps demonstrates that:
  - **14 of 17 streams (82.4%)** show identical alert counts between models.
  - The entire 5-alert reduction is concentrated in only **3 streams** (`P26-NAT-STR-05` highway traffic, `P26-NAT-STR-14` pedestrian walkway, `P26-NAT-STR-16` covered arcade).
  - Zero streams showed an alert increase under Phase 17.

---

## 4. Model Promotion Evaluation

Under the pre-registered Model Promotion Criteria:
1. **Paired Wilcoxon Signed-Rank Test:** The test statistic $W = 10.0, p = 0.125$ fails the significance threshold ($\alpha = 0.05$). The null hypothesis cannot be rejected.
2. **Confidence Interval Overlap:** The exact 95% Garwood confidence interval for Phase 17 ($[5.7381, 10.1328]$) heavily overlaps Phase 14 ($[6.3949, 10.9935]$), sharing $> 80\%$ of their span.
3. **Formal Decision:** Promotion is **`REJECTED`**; the status is **`INCONCLUSIVE`**. Phase 14 Balanced is permanently retained as the **default research baseline**.

---

## 5. Mandatory Safety Reiteration

Neither model achieves false alarm performance acceptable for municipal dispatch or tactical alerting. Single-microphone systems without multi-sensor time-of-arrival verification suffer from severe acoustic distractor vulnerability in real-world urban soundscapes. This software must never be used for life safety.
