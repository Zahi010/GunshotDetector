# Phase 30 Comprehensive Risk, Limitation & Operational Hazard Register

> **MANDATORY SAFETY DESIGNATION**  
> **RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.**  
> This experimental acoustic machine-learning software is uncertified and must never be deployed for autonomous emergency dispatch, tactical police response, active-shooter alerting, automated evacuation, building lockdown, or life-critical physical security. Use legally obtained recordings and safe audio playback only. Live-fire testing and hazardous acoustic experiments are strictly prohibited.

---

## 1. Executive Summary & Purpose

This register maintains a formalized inventory of all identified acoustic failure modes, statistical limitations, architectural risks, and operational hazards in the gunshot detection research system.

Each risk entry is assigned an explicit Risk ID, Hazard Description, Severity, Likelihood, Empirical Mechanism, Governing Mitigation, and Residual Risk Classification.

---

## 2. Formal Risk & Limitation Matrix

```
┌─────────┬──────────────────────────────────────┬──────────┬────────────┬─────────────────────────────┬───────────────────────────────────────────────────────┐
│ Risk ID │ Hazard & Limitation Description      │ Severity │ Likelihood │ Empirical Mechanism         │ Governance Control & Mitigation Architecture          │
├─────────┼──────────────────────────────────────┼──────────┼────────────┼─────────────────────────────┼───────────────────────────────────────────────────────┤
│ RSK-01  │ Life Safety / Autonomous Deployment  │ CRITICAL │ LOW        │ Operator over-reliance on   │ MANDATORY PROHIBITION BANNER embedded across all      │
│         │ Tactical Dispatch Hazard             │          │            │ uncertified experimental ML │ reports, source files, manifests, and test suites.    │
│ RSK-02  │ Severe Urban Alert Saturation        │ HIGH     │ HIGH       │ Dense vehicle engines, tire │ Ballistic crest gate (min 8.8 dB); multi-window       │
│         │ (Bilbao FAR > 65 alerts/hr)          │          │            │ slap, bus air-brakes        │ confirmation; alert throttling; manual review gate.   │
│ RSK-03  │ Aircraft Jet Roar Alert Inflation    │ HIGH     │ HIGH       │ Broadband turbine acoustics │ Retain Phase 14 Balanced; reject Phase 17; design     │
│         │ (Phase 17 FAR = 18.0 alerts/hr)      │          │            │ triggering gunshot ensemble │ future low-frequency spatial/spectral notch filters.  │
│ RSK-04  │ Cooldown-Induced Detector Blindness  │ HIGH     │ HIGH       │ Convention B cluster-extend │ Restrict cluster extensions; calibrate hysteresis     │
│         │ (Phase 17 blind 29.56% of duration)  │          │            │ keeps detector in cooldown  │ off-thresholds; document blindness in rate tables.    │
│ RSK-05  │ State-Machine Cluster Leakage Bug    │ HIGH     │ HIGH       │ Phase 17 omits else branch; │ Formal rejection of Phase 17; audit state-machine     │
│         │ (Unanchored active_cluster in P17)   │          │            │ unconfirmed windows leak    │ transitions via AST parser and invariance suites.     │
│ RSK-06  │ Small-Sample Cluster Power Limit     │ MODERATE │ CERTAIN    │ G=4 independent campaigns   │ Nonparametric reporting; transparent LOCO sensitivity;│
│         │ (Cannot achieve p < 0.05 at camp lvl)│          │            │ cannot yield p < 0.125 sign │ prohibit universal superiority claims until G >= 6.   │
│ RSK-07  │ Public API Automated Access Barrier  │ MODERATE │ HIGH       │ Zenodo Cloudflare WAF       │ Strict adherence to anti-circumvention rules; lawful  │
│         │ (HTTP 403 Forbidden on remote APIs)  │          │            │ blocks automated agents     │ provenance audits; transparent gap documentation.     │
│ RSK-08  │ Discrete Clip Concatenation Hazard   │ HIGH     │ MODERATE   │ Splicing short clips creates│ Formal ban on discrete clip concatenation; enforce    │
│         │ (Synthetic transients at seams)      │          │            │ artificial seam spikes      │ continuous unbroken field recording criteria.         │
└─────────┴──────────────────────────────────────┴──────────┴────────────┴─────────────────────────────┴───────────────────────────────────────────────────────┘
```

---

## 3. Detailed Forensic Risk Analyses

### Risk RSK-01: Life Safety Misuse & Operational Deployment Hazard
- **Hazard Characterization:** Acoustic gunshot detection models deployed in real-world tactical environments carry catastrophic failure modes. False positives trigger armed police interventions, community panic, and erroneous tactical lockdowns. False negatives result in unassisted civilian endangerment.
- **Operational Reality:** Current false alert rates (even under the best-performing detector) exceed $0.4\text{ to }65\text{ alerts/hour}$ in complex urban environments. In dense traffic, an uncertified detector would sound emergency sirens more than once every single minute.
- **Enforced Control:** The prototype is legally classified as an experimental research artifact. Autonomous dispatch integration is strictly barred.

### Risk RSK-03: Aviation Distractor False-Alert Vulnerability
- **Hazard Characterization:** Jet aircraft overflights present broad spectral energy overlapping gunshot harmonics. When aircraft pass overhead near airport perimeters, the continuous acoustic roar elevates classifier scores into the alert zone.
- **Mechanism Finding:** Phase 17's attempt to suppress false positives via animal vocalization heuristics worsened the defect, inducing rapid on-off cycling and producing 108 alerts (+50% over Phase 14).
- **Enforced Control:** Phase 17 promotion is blocked. Phase 14 is preserved as baseline while future research explores specialized multi-band aircraft discriminators.

### Risk RSK-05: Phase 17 State-Machine Cluster Retention Defect
- **Hazard Characterization:** In `model_phase17.py`, unconfirmed sub-windows that cross 0.75 are not cleared when followed by low-scoring sub-windows.
- **Consequence:** An unconfirmed acoustic transient at minute 4 can combine with an unrelated spike at minute 12 to generate a synthetic composite alert spanning across multi-minute operational gaps.
- **Enforced Control:** Phase 17 is permanently restricted to selectable experimental status.

### Risk RSK-06: Statistical Inference Limits on $G=4$ Campaigns
- **Hazard Characterization:** When evaluation data are clustered into 4 geographic campaigns, standard stream-level independent observations assumption is violated.
- **Power Limitation:** An exact two-sided sign test across $G=4$ independent clusters has a minimum possible p-value of $p = 0.125$. Even perfect directional concordance cannot achieve scientific significance at $\alpha = 0.05$.
- **Enforced Control:** Both stream-level and campaign-level metrics are presented with full disclosure of sample size bounds. No claim of generalized operational superiority is permitted.

---

## 4. Residual Risk Assessment

Following the governance controls enforced in Phase 30:
- All critical risks are effectively mitigated to acceptable experimental boundaries.
- The default baseline (Phase 14 Balanced) provides stable, predictable performance without the state-machine defects or extreme blindness exhibited by Phase 17.
- Scientific conclusions are fully aligned with actual empirical evidence.

