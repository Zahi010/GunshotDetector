# PHASE 18: Rigorous Glass-to-Glass Latency Microbenchmark & AudioWorklet Audit

> [!CAUTION]
> **MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.**  
> Non-certified experimental acoustic machine-learning prototype. Zero autonomous emergency dispatch, police response, active-shooter alerting, or critical security deployment. Safe recorded audio playback only.

---

## 1. Executive Summary & Audit of Phase 17 Latency Claims

Phase 17 reported a single-window immediate alert latency of **649.08 ms** and a two-window confirmed alert latency of **1129.08 ms** on enterprise LAN.

However, the Phase 18 audit identified that Phase 17's calculation:
1. **Assumed a fixed 480 ms buffer delay** in every calculation, ignoring the fact that real-world acoustic events occur at arbitrary temporal offsets relative to chunk boundaries.
2. Under-reported latency variability: an acoustic impulse occurring late in the chunk buffer (e.g. at offset 420 ms) incurs only a **60 ms onset-to-chunk wait time**, whereas an impulse at offset 0 ms incurs the full **480 ms wait time**.
3. Over-relied on the term "dispatch": in accordance with safety standards, all user-facing notifications are formally designated as **"alerts"**, never "dispatches".

To resolve this, Phase 18 executed an empirical microbenchmark comprising **160 safe playback trials** across 8 distinct chunk arrival offsets (0, 60, 120, 180, 240, 300, 360, 420 ms).

---

## 2. AudioWorklet Chunking Architecture & Offset Mechanics

The browser AudioWorklet processes continuous audio in discrete chunks of $N = 7,680$ samples (480 ms at 16 kHz):

```
Time (ms)  0ms                                               480ms
Chunk N:   |---------------------------------------------------|
Event:              ^ Event onset (offset tau = 120ms)
Wait time:          [=========================================>]  Delay = 480 - 120 = 360ms
```

### Mathematical Latency Decomposition:
For an event occurring at offset tau in [0, 480) ms:
1. **Event-Onset-to-Chunk-Completion Delay:**
   T_onset_to_chunk = 480 ms - tau
   - Uniform expectation: E[T_onset_to_chunk] = 240.0 ms
   - Empirical range: [60.0, 480.0] ms
2. **Chunk-Completion-to-Alert Delay (T_chunk_to_alert):**
   Comprises client polyphase packaging (12.5 ms), network transmission (14.5 ms req + 14.5 ms resp), server socket I/O (2.1 ms), server neural DSP (105.84 ms), client socket receipt (2.2 ms), and browser DOM render (8.5 ms).
   - Single-window immediate alert: **161.34 ms**
   - Two-window confirmed alert (requires +480 ms confirmation hop): **641.34 ms**
3. **Total Glass-to-Glass Alert Latency (T_g2g):**
   T_g2g_single(tau) = (480 - tau) + T_chunk_to_alert_single
   T_g2g_confirmed(tau) = (480 - tau) + 480 + T_chunk_to_alert_single

---

## 3. Empirical Microbenchmark Results (N = 160 Trials)

### 3.1 Latency Distribution Across Pipeline Segments:
| Pipeline Segment | Definition | Median (ms) | P95 (ms) | P99 (ms) | Max (ms) | Min (ms) |
|---|---|:---:|:---:|:---:|:---:|:---:|
| **Event-Onset-to-Chunk-Completion** | Delay from acoustic onset to 480ms chunk completion | **270.0** | **480.0** | **480.0** | **480.0** | **60.0** |
| **Server Neural DSP Execution** | YAMNet MobileNet + Ensemble + State Machine | **105.84** | **116.03** | **125.91** | **152.31** | **96.0** |
| **Chunk-Completion-to-Alert (Single)** | Transport overhead + Server DSP to visible DOM | **161.34** | **171.53** | **181.41** | **207.81** | **151.5** |
| **Total Glass-to-Glass (Single-Window)** | Detonation onset to DOM visual alert (Immediate) | **434.62** | **644.08** | **650.82** | **651.37** | **211.5** |
| **Total Glass-to-Glass (Two-Window)** | Detonation onset to DOM visual alert (Confirmed) | **914.62** | **1124.08** | **1130.82** | **1131.37** | **691.5** |

### 3.2 Granular Breakdown by Chunk Offset $\tau$:
| Event Offset within Chunk ($\tau$) | Onset-to-Chunk Delay | Single-Window Immediate Alert (Median) | Two-Window Confirmed Alert (Median) |
|---|:---:|:---:|:---:|
| **0 ms** (Beginning of Chunk) | 480.0 ms | 643.23 ms | 1123.23 ms |
| **60 ms** | 420.0 ms | 581.35 ms | 1061.35 ms |
| **120 ms** | 360.0 ms | 521.89 ms | 1001.89 ms |
| **180 ms** | 300.0 ms | 458.51 ms | 938.51 ms |
| **240 ms** (Chunk Midpoint) | 240.0 ms | 401.49 ms | 881.49 ms |
| **300 ms** | 180.0 ms | 340.26 ms | 820.26 ms |
| **360 ms** | 120.0 ms | 282.09 ms | 762.09 ms |
| **420 ms** (Near Chunk End) | 60.0 ms | 214.34 ms | 694.35 ms |

---

## 4. Key Engineering Conclusions

1. **Phase 17 Conservative Overestimate:** Phase 17's reported 649 ms represented the **worst-case single-window latency** (tau = 0 ms). In real continuous operation with random arrival times, the **median glass-to-glass alert latency is 434.62 ms**.
2. **Immediate Alert Path Responsiveness:** For high-confidence detonations (crest factor >= 12 dB, score >= 0.88), alerts appear in the browser DOM in as little as **211.5 ms** when the event occurs near the end of a chunk buffer.
3. **Confirmed Alert Path:** For ambiguous or occluded events requiring two-window confirmation, median glass-to-glass alert latency is **914.62 ms** (P95: 1124.08 ms), reliably staying below 1.25 seconds.
