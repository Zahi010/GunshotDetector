# Phase 31: Risk and Limitation Register
## Governance, Algorithmic Failure Modes, Statistical Power & Safety Constraints

**Document ID:** `REPORT-PHASE31-RISK-001`  
**Phase:** 31 (Risk and Limitation Governance)  
**Date:** November 2026  
**Status:** AUDITED RISK REGISTER  

---

### MANDATORY SAFETY DESIGNATION
> [!CAUTION]
> **RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.**  
> This experimental acoustic machine-learning software is uncertified and must never be deployed for autonomous emergency dispatch, tactical police response, active-shooter alerting, automated evacuation, building lockdown, or life-critical physical security. Use legally obtained recordings and safe audio playback only. Live-fire testing and hazardous acoustic experiments are strictly prohibited.

---

## 1. Risk Register Matrix

| Risk ID | Risk Title & Domain | Severity | Likelihood | Impact on Research Prototype | Mitigation & Governance Action | Status |
| :--- | :--- | :---: | :---: | :--- | :--- | :---: |
| **RSK-31-01** | **Unauthorized Life-Safety Deployment** (Operational Safety) | **CRITICAL** | Very Low | Catastrophic failure if experimental ML is used for emergency dispatch or tactical alerting. | Mandatory safety banners on all files, reports, and manifests. Clear disclaimer of uncertified status. | **MITIGATED / ENFORCED** |
| **RSK-31-02** | **Phase 17 State-Machine Defect** (Algorithmic / Defect) | **HIGH** | High | Unconfirmed clusters retained indefinitely; unrelated noise spikes merged across 100s gaps; spurious alerts at EOF. | Frozen `model_phase17.py` preserved; officially designated defective; experimental patch created; Phase 17 rejected for promotion. | **CONFIRMED & MITIGATED** |
| **RSK-31-03** | **Aviation Semantic Suppression Fragmentation** (Model Vulnerability) | **HIGH** | High | Aircraft turbofans falsely trigger avian classes, forcing $score < 0.48$ and multiplying single flyovers into 2–6 alerts. | Documented via 25-sequence audit; animal suppression disabled in default baseline (`model_phase14.py`). | **CONFIRMED & ISOLATED** |
| **RSK-31-04** | **Small-Sample Statistical Power Limit** (Methodological) | **MEDIUM** | High | With $G=4$ campaigns and $N=8$ non-zero pairs, Wilcoxon test has low power to detect modest real differences. | Report non-significance transparently; do not claim equivalence or universal superiority; mandate prospective campaign expansion. | **ACKNOWLEDGED & GOVERNED** |
| **RSK-31-05** | **Conflation of Controlled Firing with Field Performance** (Scientific) | **HIGH** | Medium | Assuming 66% controlled recall on 200s audio translates to operational sensitivity or acceptable false alarm rates. | Strict tripartite domain taxonomy: Scheduled Controlled vs Ambient Continuous vs Unexpected Real-World. Live-fire testing banned. | **ENFORCED** |
| **RSK-31-06** | **Documentation-to-Data Discrepancy** (Quality Assurance) | **MEDIUM** | Medium | Markdown narrative tables diverging from underlying CSV registries (e.g. Phase 30 Paris/Vienna error). | Rebuilt automated master registry (`reports/phase31_recording_master_registry.csv`); automated tests derive truths from underlying files. | **RESOLVED & PREVENTED** |
| **RSK-31-07** | **Automated Download API Restrictions** (Data Ingestion) | **MEDIUM** | High | Remote repositories (Zenodo) returning HTTP 403 Forbidden under automated bot scraping rules. | Enforce strict compliance with Terms of Service; no WAF/CAPTCHA circumvention; utilize sanctioned mirrors and metadata inspection. | **CONTROLLED** |
| **RSK-31-08** | **Local Storage Constraints** (Infrastructure) | **LOW** | Low | Multi-hour raw PCM audio exhausting available disk space (72 GB free). | Retain metadata-first inspection; derived audio stored in compact 16kHz mono PCM; avoid duplicate large raw corpora. | **MONITORED** |

---

## 2. In-Depth Risk & Limitation Analyses

### 2.1. RSK-31-01: Life-Safety Deployment Prohibition
Under no circumstances should this experimental research code be integrated into physical sirens, building alarm panels, automated 911 dispatch, or police active-shooter networks. Experimental ML models trained on limited public environmental corpora lack the environmental robustness, fail-safe hardware redundancy, and certified reliability required for life-critical physical security.

### 2.2. RSK-31-02: State-Machine Defect in Phase 17
Our empirical regression tests established that `model_phase17.py` omits the `else: active_cluster = []` reset branch. This creates a severe algorithmic flaw:
- An isolated sub-threshold noise spike ($0.75 \le score < 0.88$) that should be rejected within $0.48\text{ s}$ remains in memory indefinitely.
- If a second isolated disturbance occurs minutes or hours later, the state machine merges them and fires a continuous alert that spans the entire duration between them.
- At file termination, any trailing unconfirmed candidate is flushed as a valid detection.
**Action:** Phase 17 is unsuitable for production or baseline use. Phase 14 Balanced remains the default research baseline.

### 2.3. RSK-31-04: Multi-Campaign Generalization & Power Limits
The cumulative continuous benchmark comprises 23 streams from 4 campaigns (12.65 hours). While this represents a solid foundation for continuous evaluation, 4 collection campaigns cannot capture the vast acoustic diversity of global municipal environments (e.g., tropical climates, snow-muffled streets, desert wind corridors, dense subway tunnels).
- Non-significant Wilcoxon ($p = 0.156$) and Sign test ($p = 0.727$) results demonstrate that neither detector has established general superiority.
- Claims of broad domain generalization are unjustified until the benchmark reaches $\ge 50$ hours across $\ge 10$ distinct global campaigns.

### 2.4. RSK-31-06: Prevention of Documentation-to-Data Divergence
Phase 30 demonstrated the hazard of manual transcription errors between analytical drafts and final report prose. Phase 31 implements automated validation:
- All summary tables in Phase 31 reports are derived directly from immutable CSV and JSON manifests.
- Automated tests in `tests/test_phase31_reproduction.py` verify that report metrics match underlying data row-for-row.

