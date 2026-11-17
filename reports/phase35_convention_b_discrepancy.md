# Phase 35 Forensic Investigation: Convention B Ten-Second Discrepancy Resolution

> [!CAUTION]
> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.**
> This experimental acoustic machine-learning software is uncertified and must never be deployed for autonomous emergency dispatch, police tactical response, active-shooter alerting, automated evacuation, building lockdown, or life-critical physical security.
> Use legally obtained recordings and safe audio playback only. Live-fire testing and hazardous acoustic experiments are strictly prohibited.

---

## 1. Executive Summary

Phase 34 reports the following campaign-level Convention B cooldown excluded intervals:
- **Southampton:** $48.00\text{ s}$
- **Chew Magna:** $0.00\text{ s}$
- **Bilbao:** $63.92\text{ s}$
- **Adelaide:** $6,283.28\text{ s}$

These values sum to **$6,395.20\text{ seconds}$** ($1.7764\text{ h}$).

However, historical records from Phase 28 ([phase28_exposure_reproduction.csv](file:///e:/gunshot/gunshot/reports/phase28_exposure_reproduction.csv)) and Phase 31 ([phase31_exposure_reconciliation.csv](file:///e:/gunshot/gunshot/reports/phase31_exposure_reconciliation.csv)) reported a cumulative Phase 17 Convention B exclusion of **$6,385.20\text{ seconds}$** ($1.7737\text{ h}$).

There is an apparent **$10.00\text{-second discrepancy}$** ($6,395.20 - 6,385.20 = +10.00\text{ s}$).

This forensic investigation audited every individual alert, stream, and campaign ledger across Phase 28, Phase 31, Phase 33, and Phase 34.

### Primary Forensic Conclusion: `REPRODUCED WITH CORRECTION`
The $10.00\text{-second}$ discrepancy is **not an error in any physical recording calculation or underlying data ledger**. 
Rather, it is a **cross-detector column transposition error** in the narrative presentation of the Phase 34 table:
1. The values **$48.00\text{ s}$** (Southampton) and **$63.92\text{ s}$** (Bilbao) are the **Phase 14 Balanced** Convention B exclusions.
2. The true **Phase 17 Experimental** Convention B exclusions for those campaigns are **$44.00\text{ s}$** (Southampton) and **$57.92\text{ s}$** (Bilbao).
3. Summing Phase 14's European exclusions ($48.00 + 63.92 = 111.92\text{ s}$) with Phase 17's Adelaide exclusion ($6,283.28\text{ s}$) produces exactly **$6,395.20\text{ seconds}$**.
4. Summing the true Phase 17 European exclusions ($44.00 + 57.92 = 101.92\text{ s}$) with Phase 17's Adelaide exclusion ($6,283.28\text{ s}$) yields exactly **$6,385.20\text{ seconds}$**.
5. The difference $(48.00 - 44.00) + (63.92 - 57.92) = +4.00\text{ s} + +6.00\text{ s} = \mathbf{+10.00\text{ seconds}}$ accounts for the discrepancy with mathematical perfection.
6. The underlying physical event ledger has remained completely stable at **$6,385.20\text{ s}$** across Phase 28, Phase 31, and Phase 34.

---

## 2. Mathematical & Algorithmic Ledger Audit

### 2.1 Convention Definitions
- **Convention A (Instantaneous Cooldown):** Cooldown window is defined per alert as $[t_{\text{start}}, \min(T_{\text{gross}}, t_{\text{start}} + 2.0\text{ s})]$. Overlapping windows within a stream are merged into contiguous disjoint union intervals $[s_i, e_i]$, and excluded exposure is $\sum (e_i - s_i)$.
- **Convention B (Cluster-Extended Cooldown):** Cooldown window is defined from event onset to 2 seconds past the end of the sustained detector cluster $[t_{\text{start}}, \min(T_{\text{gross}}, t_{\text{end}} + 2.0\text{ s})]$.

### 2.2 Campaign-by-Campaign Discrepancy Breakdown

| Campaign Identifier | Stream Count | Phase 14 Conv B (s) | Phase 17 Conv B (s) | Transposed Table Value in Prompt | Transposition Error |
|---|:---:|:---:|:---:|:---:|:---:|
| `CAMPAIGN-SOUTHAMPTON-EXP1` | 10 | **48.00** | **44.00** | 48.00 | **+4.00 s** |
| `CAMPAIGN-CHEW-MAGNA` | 1 | **0.00** | **0.00** | 0.00 | **0.00 s** |
| `CAMPAIGN-BILBAO` | 6 | **63.92** | **57.92** | 63.92 | **+6.00 s** |
| `CAMPAIGN-ADELAIDE-AEROSONIC` | 6 | **342.00** | **6,283.28** | 6,283.28 | **0.00 s** |
| **CUMULATIVE CORPUS TOTAL** | **23** | **453.92** | **6,385.20** | **6,395.20** | **+10.00 s** |

$$\Delta_{\text{discrepancy}} = (48.00 - 44.00) + (0.00 - 0.00) + (63.92 - 57.92) + (6,283.28 - 6,283.28) = 4.00 + 6.00 = \mathbf{+10.00\text{ seconds}}$$

---

## 3. Identification of the Exact Suppressed Alerts Responsible

The $10.00\text{-second}$ difference corresponds to exactly **5 alerts** in the European campaigns that were triggered by Phase 14 Balanced but suppressed by Phase 17 Experimental's animal-sound filter.

Because all European alerts are instantaneous point transients ($t_{\text{end}} - t_{\text{start}} = 0.0\text{ s}$) without temporal overlap, each alert contributes exactly **$2.00\text{ seconds}$** of cooldown exclusion under both Convention A and Convention B.

$$\text{Total Transposition Delta} = 5\text{ alerts} \times 2.00\text{ s/alert} = \mathbf{10.00\text{ seconds}}$$

### 3.1 The 2 Southampton Suppressed Alerts ($+4.00\text{ s}$)
In stream `P27-NAT-STR-05` (domestic garden with poultry), Phase 14 triggered 20 alerts while Phase 17 triggered 18 alerts ($20 - 18 = 2$ suppressed alerts):
1. **Alert 1:** Phase 14 `P27-ALT-005` at $t = 42.72\text{ s}$, peak score $0.8129$, Conv B cooldown $[42.72, 44.72]$ ($2.00\text{ s}$). Suppressed in Phase 17 by animal filter (`hen_cluck`).
2. **Alert 2:** Phase 14 `P27-ALT-019` at $t = 1224.48\text{ s}$, peak score $0.7522$, Conv B cooldown $[1224.48, 1226.48]$ ($2.00\text{ s}$). Suppressed in Phase 17 by animal filter (`rooster_crow`).
- **Southampton Cooldown Impact:** Phase 14 exclusion = $48.00\text{ s}$; Phase 17 exclusion = $44.00\text{ s}$ (Delta = $+4.00\text{ s}$).

### 3.2 The 3 Bilbao Suppressed Alerts ($+6.00\text{ s}$)
In Bilbao urban recordings, Phase 14 triggered 32 alerts while Phase 17 triggered 29 alerts ($32 - 29 = 3$ suppressed alerts):
1. **Alert 3:** Stream `P27-NAT-STR-14`, Phase 14 `P27-ALT-069` at $t = 48.96\text{ s}$, peak score $0.7671$, Conv B cooldown $[48.96, 50.96]$ ($2.00\text{ s}$).
2. **Alert 4:** Stream `P27-NAT-STR-14`, Phase 14 `P27-ALT-070` at $t = 91.68\text{ s}$, peak score $0.7571$, Conv B cooldown $[91.68, 93.68]$ ($2.00\text{ s}$).
3. **Alert 5:** Stream `P27-NAT-STR-16`, Phase 14 `P27-ALT-095` at $t = 276.00\text{ s}$, peak score $0.7623$, Conv B cooldown $[276.00, 278.00]$ ($2.00\text{ s}$).
- **Bilbao Cooldown Impact:** Phase 14 exclusion = $63.92\text{ s}$; Phase 17 exclusion = $57.92\text{ s}$ (Delta = $+6.00\text{ s}$).

---

## 4. Cross-Phase Reconciliation Audit

We audited the per-recording Convention B cooldowns across Phase 28, Phase 31, Phase 33, and Phase 34:
- `phase28_exposure_reproduction.csv`: Phase 17 Conv B total = **$6,385.20\text{ s}$** (0 stream-level discrepancies).
- `phase31_exposure_reconciliation.csv`: Phase 17 Conv B total = **$6,385.20\text{ s}$** (0 stream-level discrepancies).
- `phase34_stream_level_detector_metrics.csv`: Phase 17 Conv B total = **$6,385.20\text{ s}$** (0 stream-level discrepancies).
- `phase34_campaign_level_metrics.csv`: Phase 17 Conv B total = **$6,385.20\text{ s}$** (0 campaign-level discrepancies).

### Audit Verdict:
No recording contributed a different interval total across any historical phase. The physical benchmark exposure remains completely reproducible and uncorrupted. The prompt's $6,395.20\text{ s}$ sum was entirely caused by reading Phase 14's European campaign values into Phase 17's calculation.
