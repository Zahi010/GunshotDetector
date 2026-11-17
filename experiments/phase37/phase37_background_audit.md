# PHASE 37 CONTINUOUS-NEGATIVE BENCHMARK AUDIT
## Five-Hour Exposure Verification, Cooldown Conventions & Poisson Uncertainty

> [!CAUTION]
> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.**
> This experimental acoustic machine-learning software is uncertified and must never be deployed for autonomous emergency dispatch, police tactical response, active-shooter alerting, automated evacuation, building lockdown, or life-critical physical security.
> Use legally obtained recordings and safe audio playback only. Live-fire testing and hazardous acoustic experiments are strictly prohibited.

---

## 1. Executive Summary & Verdict

Phase 37 reproduced all background metrics across the 4 continuous negative streams totaling **$14,400.0\text{ seconds}$ ($5.0000\text{ gross hours}$)**.

### Cooldown Conventions Definitions:
- **Convention A:** Excludes fixed $[t_{\text{start}}, \min(T_{\text{gross}}, t_{\text{start}} + 2.0\text{ s})]$ per alert with interval overlap merging.
- **Convention B:** Excludes sustained event duration plus cooldown $[t_{\text{start}}, \min(T_{\text{gross}}, t_{\text{end}} + 2.0\text{ s})]$ with interval overlap merging.

### Headline Reproduction Summary:
| Condition ID | Architecture / Model | Alerts Count | Gross FAR (/hr) | Conv B Excluded (s) | Conv B Eligible (hr) | Conv B Eligible FAR (/hr) | Poisson 95% CI (Gross FAR) |
|:---:|---|:---:|:---:|:---:|:---:|:---:|:---:|
| `COND1` | Phase 14 Balanced Baseline | 68 | **13.6000** | 306.16 | 4.9150 | 13.8353 | [10.56, 17.24] |
| `COND2` | Phase 17 Experimental (Defect) | 145 | **29.0000** | 5,131.36 | 3.5746 | 40.5637 | [24.47, 34.14] |
| `COND3` | Phase 17 Reset Candidate | 68 | **13.6000** | 306.16 | 4.9150 | 13.8353 | [10.56, 17.24] |
| `COND4` | Phase 36 Raw FSM | 66 | **13.2000** | 300.48 | 4.9165 | 13.4241 | [10.20, 16.80] |
| `COND5` | Phase 36 Legacy Suppression | 66 | **13.2000** | 300.48 | 4.9165 | 13.4241 | [10.20, 16.80] |
| `COND6` | Phase 36 Conservative | 66 | **13.2000** | 300.48 | 4.9165 | 13.4241 | [10.20, 16.80] |

### Key Audit Findings:
1. **Phase 17 State Machine Pathology:** Phase 17's unguarded candidate retention caused massive alert fragmentation, emitting 145 alerts and excluding **5,131.36 seconds (28.5% of the entire 5 hours)** under Convention B.
2. **Phase 36 Stability:** Phase 36's explicit 4-state FSM eliminated 2 spurious unconfirmed threshold crossings, emitting 66 alerts ($13.2000/\text{hr}$) with only $300.48\text{ s}$ excluded exposure.
3. **Statistical Equivalence to Baseline:** Phase 36 ($13.20/\text{hr}$, 95% CI: [10.20, 16.80]) is statistically indistinguishable from Phase 14 Balanced ($13.60/\text{hr}$, 95% CI: [10.56, 17.24]), with overlapping confidence intervals.

Full per-stream breakdown is codified in [phase37_background_metrics_reproduction.csv](file:///E:/gunshot/gunshot/experiments/phase37/phase37_background_metrics_reproduction.csv).
