# PHASE 34 — EXPOSURE REPRODUCTION & DETECTOR METRICS REPORT
## Workstream 3: Stream-Level and Campaign-Level Metrics Under Conventions A & B

> **MANDATORY SAFETY DESIGNATION**  
> **RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY**  
> *This experimental acoustic machine-learning software is uncertified and must never be deployed for autonomous emergency dispatch, tactical police response, active-shooter alerting, automated evacuation, building lockdown, or life-critical physical security. Use legally obtained recordings and safe audio playback only. Live-fire testing and hazardous acoustic experiments are strictly prohibited.*

---

## 1. Executive Summary

Workstream 3 independently reconstructs all exposure and performance metrics across the canonical 23-stream continuous negative-exposure benchmark for both **Phase 14 Balanced** (Default Research Baseline) and **Phase 17 Experimental** (Selectable Profile).

All metrics were computed directly from physical audio WAV headers, individual alert event logs, and timestamped cooldown intervals without relying on historical rounded summaries:

| Metric Category | Phase 14 Balanced Baseline | Phase 17 Experimental Profile | Difference (P14 - P17) | Reconciliation Status |
| :--- | :---: | :---: | :---: | :---: |
| **Total Benchmark Streams** | 23 streams | 23 streams | 0 | `EXACT_MATCH` |
| **Gross Exposure Duration** | **45,525.5755 s (12.6460 h)** | **45,525.5755 s (12.6460 h)** | 0.0 s | `EXACT_MATCH` |
| **Total Observed Alerts** | **128 alerts** | **159 alerts** | **-31 alerts** | `EXACT_MATCH` |
| **Gross False-Alert Rate (FAR)** | **10.1218 / hr** | **12.5732 / hr** | **-2.4514 / hr** | `EXACT_MATCH` |
| **Convention A Excluded Time** | **255.84 s (0.0711 h)** | **316.56 s (0.0879 h)** | -60.72 s | `EXACT_MATCH` |
| **Convention A Eligible Exposure** | **12.5749 h (45,269.74 s)** | **12.5581 h (45,209.02 s)** | +0.0168 h | `EXACT_MATCH` |
| **Convention A Eligible Rate** | **10.1790 / hr** | **12.6611 / hr** | **-2.4821 / hr** | `EXACT_MATCH` |
| **Convention B Excluded Time** | **453.92 s (0.1261 h)** | **6,385.20 s (1.7737 h)** | **-5,931.28 s** | `EXACT_MATCH` |
| **Convention B Eligible Exposure** | **12.5199 h (45,071.66 s)** | **10.8723 h (39,140.38 s)** | **+1.6476 h** | `EXACT_MATCH` |
| **Convention B Eligible Rate** | **10.2237 / hr** | **14.6243 / hr** | **-4.4006 / hr** | `EXACT_MATCH` |

---

## 2. Definitions of Cooldown Accounting Conventions

To prevent methodological ambiguity, Phase 34 strictly distinguishes between the two historical cooldown conventions evaluated across the research program:

### 2.1 Convention A: Fixed-Window Onset Cooldown
- **Rule:** When an alert triggers at timestamp $t_{\text{alert\_start}}$, a fixed 2.0-second blackout interval $[t_{\text{alert\_start}}, t_{\text{alert\_start}} + 2.0\text{ s}]$ is excluded from eligible exposure.
- **Purpose:** Suppresses immediate acoustic reverberation and echo-chamber ringing from a single transient impulse.
- **Behavior:** Excluded exposure scales linearly with alert count:
  $$\text{Excluded Time} \approx N_{\text{alerts}} \times 2.0\text{ seconds}$$
  (subject to boundary clipping and rare overlap).

### 2.2 Convention B: Extended Event Duration + Trailing Cooldown
- **Rule:** When an alert triggers, the entire active detector cluster duration $[t_{\text{event\_start}}, t_{\text{event\_end}}]$ PLUS a trailing 2.0-second cooldown $[t_{\text{event\_end}}, t_{\text{event\_end}} + 2.0\text{ s}]$ is excluded from eligible exposure:
  $$\text{Interval} = [t_{\text{event\_start}}, t_{\text{event\_end}} + 2.0\text{ s}]$$
- **Purpose:** Prevents penalizing a system multiple times during a prolonged, non-transient acoustic event (e.g., passing freight train, lawnmower, aircraft overflight).
- **Behavior:** In systems with clean state-machine resets (Phase 14), excluded exposure remains small ($453.92\text{ s}$, 1.0% of exposure). However, in systems with unconfirmed cluster retention defects (Phase 17), continuous aircraft signals fragment into overlapping long-duration clusters that exclude massive amounts of exposure.

---

## 3. Campaign-Level Metrics Reconstruction

Recomputing all metrics from the underlying stream-level ledger yields the exact campaign-level breakdown documented in [phase34_campaign_level_metrics.csv](file:///E:/gunshot/gunshot/reports/phase34_campaign_level_metrics.csv):

| Campaign ID | Physical Streams | Gross Duration (hr) | P14 Alerts | P17 Alerts | Delta (P14 - P17) | P14 Gross FAR | P17 Gross FAR | P14 Conv A FAR | P17 Conv A FAR | P14 Conv B FAR | P17 Conv B FAR | Favored Profile |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Southampton** (`RPISOUND-UK`) | 10 | 5.5000 h | 24 | 22 | +2 | 4.36 / hr | 4.00 / hr | 4.37 / hr | 4.01 / hr | 4.37 / hr | 4.01 / hr | Phase 17 (-2 alerts) |
| **Chew Magna** (`CHEWMAGNA-UK`) | 1 | 0.5833 h | 0 | 0 | 0 | 0.00 / hr | 0.00 / hr | 0.00 / hr | 0.00 / hr | 0.00 / hr | 0.00 / hr | Tied (0 alerts) |
| **Bilbao** (`BILBAO-ES`) | 6 | 0.5627 h | 32 | 29 | +3 | 56.87 / hr | 51.54 / hr | 58.72 / hr | 53.06 / hr | 58.72 / hr | 53.06 / hr | Phase 17 (-3 alerts) |
| **Adelaide** (`AEROSONIC-AU`) | 6 | 6.0000 h | 72 | 108 | -36 | 12.00 / hr | 18.00 / hr | 12.08 / hr | 18.18 / hr | 12.19 / hr | 25.38 / hr | Phase 14 (-36 alerts) |
| **Benchmark Total** | **23** | **12.6460 h** | **128** | **159** | **-31** | **10.12 / hr** | **12.57 / hr** | **10.18 / hr** | **12.66 / hr** | **10.22 / hr** | **14.62 / hr** | **Phase 14 (-31 alerts)** |

---

## 4. Forensic Analysis of Convention B Cooldown Inflation in Phase 17

A critical finding in Workstream 3 is the extreme divergence in Convention B excluded exposure between Phase 14 and Phase 17:

### 4.1 Cooldown Excluded Exposure Comparison by Campaign

```
Campaign 1: Southampton (5.50 hr exposure)
  - Phase 14: Conv A = 48.00 s | Conv B = 48.00 s (Ratio: 1.00x)
  - Phase 17: Conv A = 44.00 s | Conv B = 44.00 s (Ratio: 1.00x)

Campaign 2: Chew Magna (0.58 hr exposure)
  - Phase 14: Conv A =  0.00 s | Conv B =  0.00 s (Ratio: 1.00x)
  - Phase 17: Conv A =  0.00 s | Conv B =  0.00 s (Ratio: 1.00x)

Campaign 3: Bilbao (0.56 hr exposure)
  - Phase 14: Conv A = 63.92 s | Conv B = 63.92 s (Ratio: 1.00x)
  - Phase 17: Conv A = 57.92 s | Conv B = 57.92 s (Ratio: 1.00x)

Campaign 4: Adelaide AeroSonicDB (6.00 hr exposure)
  - Phase 14: Conv A = 143.92 s | Conv B =  342.00 s (Ratio:  2.38x)
  - Phase 17: Conv A = 214.64 s | Conv B = 6,283.28 s (Ratio: 29.27x!)
```

### 4.2 Mechanism of Phase 17 Cooldown Explosion
1. **In Southampton, Chew Magna, and Bilbao:** All acoustic false alerts were short impulsive transients ($< 0.5\text{ s}$). Consequently, the event duration plus trailing cooldown did not exceed the 2.0-second window, making Convention A and Convention B excluded times **100% identical**.
2. **In Adelaide (AeroSonicDB):** Low-altitude aircraft flyovers create continuous, fluctuating broadband and tonal acoustic energy lasting 30 to 180 seconds.
3. In Phase 17, the state-machine defect (`active_cluster` not cleared on subthreshold unconfirmed frames) causes the detector to latch onto these prolonged aircraft signatures, fragmenting single flyovers into bursts of alerts with prolonged active event spans.
4. Under Convention B, this resulted in **6,283.28 seconds (1.7454 hours, or 29.1% of the entire 6-hour AeroSonicDB recording)** being classified as "cooldown excluded" for Phase 17!
5. This massive reduction in eligible exposure ($6.0000\text{ h} \to 4.2547\text{ h}$) caused Phase 17's Convention B eligible false-alert rate to artificially inflate from $18.00/\text{hr}$ (gross) to **$25.38/\text{hr}$**.
6. By contrast, Phase 14 Balanced maintained clean state resets, excluding only 342.00 seconds (1.6% of exposure) and retaining an eligible FAR of $12.19/\text{hr}$.

---

## 5. Mathematical Concordance Verification

All stream-level metrics were summed and compared against corpus totals:
1. **Total Alerts:**
   $$\sum_{i=1}^{23} \text{Alerts}_{\text{P14}, i} = 24 + 0 + 32 + 72 = \mathbf{128\text{ alerts}}$$
   $$\sum_{i=1}^{23} \text{Alerts}_{\text{P17}, i} = 22 + 0 + 29 + 108 = \mathbf{159\text{ alerts}}$$
2. **Gross Duration:**
   $$\sum_{i=1}^{23} \text{Duration}_i = 19,800.0 + 2,100.0 + 2,025.5755 + 21,600.0 = \mathbf{45,525.5755\text{ s}} = \mathbf{12.6460\text{ hr}}$$
3. **Convention A Excluded Exposure:**
   $$\sum \text{P14}_{\text{ConvA\_CD}} = 48.0 + 0.0 + 63.92 + 143.92 = \mathbf{255.84\text{ s}}$$
   $$\sum \text{P17}_{\text{ConvA\_CD}} = 44.0 + 0.0 + 57.92 + 214.64 = \mathbf{316.56\text{ s}}$$
4. **Convention B Excluded Exposure:**
   $$\sum \text{P14}_{\text{ConvB\_CD}} = 48.0 + 0.0 + 63.92 + 342.00 = \mathbf{453.92\text{ s}}$$
   $$\sum \text{P17}_{\text{ConvB\_CD}} = 44.0 + 0.0 + 57.92 + 6,283.28 = \mathbf{6,385.20\text{ s}}$$

Every sum matches the reported corpus totals with zero rounding delta or missing records.

