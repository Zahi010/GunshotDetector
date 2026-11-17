# PHASE 40 EVALUATION PROTOCOL & PRE-REGISTRATION SPECIFICATION
## Frozen Benchmark Protocol for Prospective Acoustic Event Detection & Continuous Exposure

> [!CAUTION]
> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.**
> This software is uncertified research code. It must never be deployed for autonomous emergency dispatch, police tactical response, active-shooter alerting, automated evacuation, building lockdown, or life-critical physical security.
> Use lawfully obtained recordings and safe audio playback only. Live-fire testing and hazardous acoustic experiments are strictly prohibited.

---

## 1. Scope & Objective

This document specifies the formal pre-registered evaluation protocol for Phase 40.
The objective is to establish an uncompromised, reproducible benchmark of six frozen detector conditions on independent, prospective continuous audio streams and challenge partitions without altering any model parameter, threshold, feature extraction routine, or decision logic.

---

## 2. Frozen Detector Conditions

All six evaluated conditions are strictly frozen to their verified physical implementations:

| Condition ID | Architecture / Profile | Source Implementation Path | Authoritative Physical SHA-256 | Benchmark Role |
|---|---|---|---|---|
| **`COND1`** | Phase 14 Balanced Baseline | `gunshot/model_phase14.py` | `a268551604ae8b73068435ff10ab3d265065f56e0679757fca5b6bf0f061c065` | `DEFAULT_RESEARCH_BASELINE` |
| **`COND2`** | Phase 17 Experimental (Defective) | `gunshot/model_phase17.py` | `e2b262b866fdd5d7f1a4ab91a7b8b9bac189ee8cc7a78603b3544ca1579fb819` | `SELECTABLE_EXPERIMENTAL_PROFILE` (Diagnostic) |
| **`COND3`** | Phase 17 State Reset Candidate | `gunshot/experiments/phase31/model_phase17_state_reset_candidate.py` | `c144b917b56532787e2a9198f2cad4a77dc2095b57962f31d11d250a4d5d9ea5` | `QUARANTINED_DIAGNOSTIC_REFERENCE` |
| **`COND4`** | Phase 36 Raw State Machine | `gunshot/experiments/phase36/model_phase36.py` | `2774ab4cae0fca6d2f3646b443694fefa40d6837ff195f1d216ae7ff7732563a` | `EXPERIMENTAL_RESEARCH_BRANCH_V1` (Suppression: `NONE`) |
| **`COND5`** | Phase 36 Legacy Suppression | `gunshot/experiments/phase36/model_phase36.py` | `2774ab4cae0fca6d2f3646b443694fefa40d6837ff195f1d216ae7ff7732563a` | `EXPERIMENTAL_RESEARCH_BRANCH_V1` (Suppression: `LEGACY_ANIMAL`) |
| **`COND6`** | Phase 36 Conservative Suppression | `gunshot/experiments/phase36/model_phase36.py` | `2774ab4cae0fca6d2f3646b443694fefa40d6837ff195f1d216ae7ff7732563a` | `EXPERIMENTAL_RESEARCH_BRANCH_V1` (Suppression: `CONSERVATIVE`) |

---

## 3. Mathematical Metric Definitions

### 3.1 Continuous Ambient Exposure Metrics
For each recording stream $i \in \{1, \dots, M\}$ with duration $d_i$ seconds:
1. **Total Gross Exposure Time ($T_{\text{gross}}$):**
   $$T_{\text{gross}} = \frac{\sum_{i=1}^M d_i}{3600.0} \quad \text{[hours]}$$
2. **Gross False Alarm Rate ($\text{FAR}_{\text{gross}}$, Convention A):**
   $$\text{FAR}_{\text{gross}} = \frac{N_{\text{alerts}}}{T_{\text{gross}}} \quad \text{[alerts / hour]}$$
3. **Exact Poisson 95% Confidence Intervals (Garwood Formula):**
   $$\left[ \frac{\chi^2(2 k, \, \alpha/2)}{2 \, T_{\text{gross}}}, \; \frac{\chi^2(2 k + 2, \, 1 - \alpha/2)}{2 \, T_{\text{gross}}} \right]$$
   where $k = N_{\text{alerts}}$, $\alpha = 0.05$, and $\chi^2(\nu, p)$ is the quantile function of the chi-squared distribution with $\nu$ degrees of freedom.
4. **Convention B Excluded Exposure ($T_{\text{excluded}}$):**
   For each emitted alert $j$ spanning $[t_{s, j}, t_{e, j}]$ with refractory cooldown $t_{\text{cool}} = 2.0\text{ s}$:
   $$I_j = [t_{s, j}, t_{e, j} + t_{\text{cool}}]$$
   $$T_{\text{excluded}} = \frac{\mu\left(\bigcup_j I_j\right)}{3600.0} \quad \text{[hours]}$$
   where $\mu$ denotes the Lebesgue measure (merging overlapping cooldown intervals).
5. **Convention B Eligible Exposure & FAR ($\text{FAR}_{\text{eligible}}$):**
   $$T_{\text{eligible}} = T_{\text{gross}} - T_{\text{excluded}} \quad \text{[hours]}$$
   $$\text{FAR}_{\text{eligible}} = \frac{N_{\text{alerts}}}{T_{\text{eligible}}} \quad \text{[alerts / eligible hour]}$$

### 3.2 Positive Sensitivity & Event Boundary Metrics
1. **Clip-Level True Positive Recall:**
   $$\text{Recall}_{\text{clip}} = \frac{\text{True Positive Clips}}{\text{Total Annotated Clips}} = \frac{\sum_{i=1}^N \mathbb{I}(k_i \ge 1)}{N}$$
2. **Duplicate Alert Rate:**
   $$\text{Duplicate Alert Rate} = \frac{\text{Duplicate Alerts}}{\text{True Positive Clips} + \text{Duplicate Alerts}} = \frac{\sum_{i: k_i \ge 1} (k_i - 1)}{\sum_{i: k_i \ge 1} k_i}$$

### 3.3 Paired Distractor & Challenge Metrics
1. **Continuity-Corrected McNemar Test ($\chi^2$):**
   $$\chi^2 = \frac{(|b - c| - 1)^2}{b + c}, \quad \text{df} = 1$$
   where $b$ is Phase 36-only triggers and $c$ is Phase 14-only triggers.
2. **Exact Paired Binomial Test:**
   Under null hypothesis $H_0: p = 0.5$ for discordant pairs:
   $$p = 2 \times \sum_{x = \max(b, c)}^{b+c} \binom{b+c}{x} (0.5)^{b+c}$$

---

## 4. Dataset Lineage & Independence Governance

1. **Lawful Provenance:** All audio files must be sourced from lawful public domain or Creative Commons archives (FSD50K, Freesound, Radio Aporee via Archive.org).
2. **Cryptographic Non-Overlap:** Every evaluated audio file must possess a unique SHA-256 hash verified against all historical benchmarks (Phases 1–39).
3. **Pre-Registration Hash:** This protocol document must be hashed via SHA-256 and committed before executing prospective evaluations on newly acquired continuous audio.
