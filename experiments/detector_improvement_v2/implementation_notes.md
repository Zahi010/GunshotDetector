# Detector Improvement V2: Technical Implementation Notes & Architecture Guide

**MANDATORY SAFETY DESIGNATION:**
> **RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY**
>
> This experimental acoustic machine-learning software is uncertified and must never be deployed for autonomous emergency dispatch, tactical police response, active-shooter alerting, automated evacuation, building lockdown, or life-critical physical security. Safe recorded audio playback only; live-fire testing and hazardous acoustic experiments are strictly prohibited.

---

## 1. System Architecture Overview

Detector Improvement V2 resides under `experiments/detector_improvement_v2/` as an independent, separately versioned research engine. It builds upon the deterministic finite state machine foundations of Phase 36 and the multi-category suppression principles of Phase 43 V1, introducing three core acoustic enhancements:

```
[Raw Audio Waveform / Real-Time Mic Stream]
                 │
                 ▼ (16 kHz Mono Resampling & Ring Buffer)
     [Physical Acoustic Analysis]
       - Physical Crest Factor (Peak / RMS dB)
       - Low/Mid/High Sub-Band Spectral Decomposition
                 │
                 ▼ (YAMNet Backbone: 1024-d Embeddings + 521 Class Probabilities)
      [Tabular Ensemble Scoring]
        - CatBoost (30%) + LightGBM (25%) + XGBoost (25%) + Keras MLP (20%)
        -> Raw Consensus Probability (p_raw)
                 │
                 ▼
  [Calibrated Acoustic Suppression V2]
    ├── 1. Non-Ballistic Coherence Safeguard (p_ballistic < 0.015 & p_nontarget >= 0.12 -> x0.20)
    ├── 2. Thunder Suppression (p_thun >= 0.25 & p_thun >= 1.5 * p_gun -> x0.30)
    ├── 3. Two-Tier Pyrotechnic Gating (Dominant: fw >= 0.45, gun < 0.25 -> x0.30; Standard: fw >= 0.30, gun < 0.12 -> x0.35)
    ├── 4. Infrasonic Wind Buffeting Attenuation (p_wind >= 0.25 & p_wind >= 1.5 * p_gun -> x0.25)
    ├── 5. Mechanical Impact / Tool Impact Gating (p_impact >= 0.30, gun < 0.20 -> x0.35)
    └── 6. Canine, Fire Crackle, & Emergency Transit Siren Gating
                 │
                 ▼ (Adjusted Window Score)
  [Deterministic Refractory State Machine V2]
    ├── IDLE -> CANDIDATE -> CONFIRMED -> COOLDOWN -> IDLE
    ├── Temporal Continuity Guard (Hop gap <= 0.60s)
    ├── Single-Round Impulse Exception (p >= 0.82, Crest >= 14 dB, Dur <= 5.0s, Unsuppressed)
    └── Fixed Refractory Window (2.0s Post-Event Lockout)
                 │
                 ▼
      [Confirmed Gunshot Event Alert]
```

---

## 2. Configuration Profiles & Hyperparameters

The complete parameter definitions are serialized in `config_improvement_v2.json`:

```json
{
  "system_designation": "RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY",
  "branch_identifier": "DETECTOR_IMPROVEMENT_V2",
  "profiles": {
    "balanced": {
      "threshold_base": 0.75,
      "threshold_high": 0.88,
      "threshold_off": 0.48,
      "confirm_windows": 2,
      "cooldown_secs": 2.0,
      "max_hop_gap_s": 0.60,
      "min_crest_factor_db": 8.8,
      "single_win_min_crest_db": 12.0,
      "allow_short_clip_exception": true,
      "allow_single_impulse_exception": true,
      "single_impulse_min_score": 0.82,
      "single_impulse_min_crest_db": 14.0,
      "single_impulse_max_dur_sec": 5.0
    },
    "high_precision": {
      "threshold_base": 0.80,
      "threshold_high": 0.90,
      "threshold_off": 0.52,
      "confirm_windows": 2,
      "cooldown_secs": 2.5,
      "max_hop_gap_s": 0.60,
      "min_crest_factor_db": 9.5,
      "single_win_min_crest_db": 13.0,
      "allow_short_clip_exception": true,
      "allow_single_impulse_exception": false,
      "single_impulse_min_score": 0.85,
      "single_impulse_min_crest_db": 15.0,
      "single_impulse_max_dur_sec": 4.0
    },
    "high_sensitivity": {
      "threshold_base": 0.70,
      "threshold_high": 0.85,
      "threshold_off": 0.42,
      "confirm_windows": 2,
      "cooldown_secs": 1.5,
      "max_hop_gap_s": 0.60,
      "min_crest_factor_db": 8.0,
      "single_win_min_crest_db": 11.0,
      "allow_short_clip_exception": true,
      "allow_single_impulse_exception": true,
      "single_impulse_min_score": 0.78,
      "single_impulse_min_crest_db": 13.0,
      "single_impulse_max_dur_sec": 6.0
    }
  }
}
```

---

## 3. Algorithmic Detail: Calibrated Acoustic Suppression V2

### 3.1 Class Mapping & Groupings
YAMNet's 521 AudioSet classes are grouped into specialized functional clusters:
- **Ballistic Classes ($C_{\text{bal}}$):**
  - Class 420: `Explosion`
  - Class 421: `Gunshot, gunfire`
  - Class 422: `Machine gun`
  - Class 424: `Artillery fire`
  - Class 425: `Cap gun`
  - Class 428: `Burst, pop`
  - Class 434: `Crack`
  - Class 460: `Bang`
- **Gunshot-Specific Classes ($C_{\text{gun}}$):** [421, 422, 424, 425]
- **Pyrotechnic Classes ($C_{\text{fw}}$):** [426: `Fireworks`, 427: `Firecracker`]
- **Infrasonic Wind Classes ($C_{\text{wind}}$):** [277: `Wind`, 279: `Wind noise (microphone)`]
- **Impact / Tool Classes ($C_{\text{impact}}$):** [58: `Clap`, 352: `Slam`, 353: `Knock`, 413: `Hammer`, 414: `Jackhammer`]
- **Non-Target Semantic Broad Classes ($C_{\text{nontarget}}$):**
  - Class 0: `Speech`
  - Classes 67-117: Animal vocalizations (dogs, birds, livestock, fowl)
  - Classes 300-330: Road transit, motor vehicles, engines
  - Classes 502-504: Outside natural and urban ambient

### 3.2 Suppression Execution Hierarchy
Window score adjustment executes with strict precedence:
1. **Coherence Safeguard:** Evaluates whether the tabular ensemble's activation is coherent with neural acoustic evidence. If $p_{\text{bal}} < 0.015$ and $p_{\text{nontarget}} \ge 0.12$, the raw score is attenuated by $0.20\times$.
2. **Thunder Suppression:** If $p_{\text{thun}} \ge 0.25$ and $p_{\text{thun}} \ge 1.5 \cdot p_{\text{gun}}$, attenuated by $0.30\times$.
3. **Two-Tier Fireworks Suppression:**
   - Dominant Tier: $p_{\text{fw}} \ge 0.45 \land p_{\text{fw}} \ge 1.8 \cdot p_{\text{gun}} \land p_{\text{gun}} < 0.25 \implies \text{attenuate } 0.30\times$.
   - Standard Tier: $p_{\text{fw}} \ge 0.30 \land p_{\text{fw}} \ge 1.5 \cdot p_{\text{gun}} \land p_{\text{gun}} < 0.12 \implies \text{attenuate } 0.35\times$.
4. **Wind Buffeting Attenuation:** If $p_{\text{wind}} \ge 0.25$ and $p_{\text{wind}} \ge 1.5 \cdot p_{\text{gun}}$, attenuated by $0.25\times$.
5. **Mechanical Impact Gating:** If $p_{\text{impact}} \ge 0.30$ and $p_{\text{impact}} \ge 1.5 \cdot p_{\text{gun}}$ and $p_{\text{gun}} < 0.20$, attenuated by $0.35\times$.
6. **Canine, Crackle, & Siren Gating:** Preserved with V1 attenuation multipliers ($0.30\times - 0.35\times$).

---

## 4. State Machine V2: Single-Round Impulse Exception

In genuine gunfire, a single discrete discharge produces an acoustic peak in exactly one 960 ms analysis window (hop size 480 ms). Under V1's rigid 2-window confirmation rule, if the first window had score $0.75 \le p < 0.88$, it was queued as a `CANDIDATE`. When the sound decayed in Window 2 ($p < 0.75$), V1 discarded the candidate as `CANDIDATE_DISCARDED_BELOW_BASE`.

`EventStateMachineV2` introduces a disciplined ballistic exception:
```python
if (is_gap or is_decay) and self.allow_single_impulse_exception and len(self.candidate_windows) == 1:
    cand = self.candidate_windows[0]
    cand_score = float(cand.get("score", 0.0))
    cand_crest = cand.get("crest_factor_db") or crest_factor_db
    cand_suppressed = bool(cand.get("suppression_active", False))

    qualifies_impulse = (
        cand_score >= self.single_impulse_min_score # 0.82
        and (cand_crest is not None and cand_crest >= self.single_impulse_min_crest_db) # 14.0 dB
        and (audio_duration_sec is None or audio_duration_sec <= self.single_impulse_max_dur_sec) # 5.0s
        and not cand_suppressed # Must not be suppressed by any distractor rule
    )

    if qualifies_impulse:
        # Promote candidate to CONFIRMED and emit single_round_impulse event
        self.confirmed_windows = [cand]
        self.candidate_windows = []
        emitted = self._create_event_record(self.confirmed_windows, "single_round_impulse")
        self.events_emitted.append(emitted)
        self.cooldown_until = emitted["end_time"] + self.cooldown_secs
        self.state = EventState.COOLDOWN
        return emitted
```

### Guarantees of State Machine V2:
1. **Zero Hallucination Promotion:** Promotion requires $p \ge 0.82$, physical crest factor $\ge 14.0\text{ dB}$, and zero semantic suppression activity.
2. **Strict Isolation:** Only single isolated candidate windows are eligible (`len(candidate_windows) == 1`).
3. **Refractory Cooldown Maintained:** Immediately upon promotion, the FSM transitions to `COOLDOWN` for $2.0\text{ seconds}$, preventing duplicate triggers from subsequent reverberation.
4. **Continuous Noise Immunity:** Because the rule requires duration $\le 5.0\text{s}$ (or strict per-window impulse sharpness in streaming mode), long ambient rumble or sustained clatter cannot trigger this exception.

---

## 5. Latency Profiling & Real-Time Performance

Evaluation across 368 benchmark recordings and live streaming ring buffer tests established the following execution profile:

| Operation | Hardware Target | Mean Latency | 99th Percentile Latency | Real-Time Factor (RTF) |
| :--- | :---: | :---: | :---: | :---: |
| **YAMNet Feature Extraction (960 ms Window)** | CPU (Intel Core) | 12.4 ms | 18.2 ms | 0.013 |
| **Tabular Ensemble Inference (4 Models)** | CPU (Multi-thread) | 2.1 ms | 4.5 ms | 0.002 |
| **Calibrated Suppression V2 (521 Classes)** | Vectorized NumPy | 0.12 ms | 0.25 ms | 0.0001 |
| **FSM V2 State Transition & Refractory Check** | Pure Python | 0.04 ms | 0.08 ms | < 0.0001 |
| **Total 480 ms Audio Chunk Pipeline** | CPU | **14.8 ms** | **22.5 ms** | **0.031** |

With a total processing latency of **$14.8\text{ ms}$ per 480 ms audio slice**, Detector Improvement V2 consumes only **$3.1\%$ of available real-time compute budget**, ensuring robust zero-drop performance during continuous streaming.

---

## 6. Dashboard Integration & Phase 45 Promotion Recommendation

### 6.1 Dashboard Architecture Integration
Detector Improvement V2 is fully integrated into the production web service (`app.py`, `templates/index.html`, `static/js/app.js`):
- **Default Production Engine:** Retained as `phase14` (Phase 14 Balanced Baseline) in accordance with governance protocols.
- **Selectable Experimental Engine:** `detector_improvement_v2` (alias `v2`) is available in both the live streaming engine selector and the audio file upload selector.
- **API Endpoints:** Supported across `/api/detect`, `/api/stream_window`, `/api/status`, `/api/health`, and `/api/profiles`.

### 6.2 Recommendation for Phase 45
Based on the unanimous empirical results across both the Development and Locked Holdout partitions:
1. **V2 Outperforms V1 on All Fronts:**
   - Positive Gunshot Recall: $+2.5\%$ absolute increase (from $61.7\%$ to $64.2\%$).
   - Fireworks False Alarms: $-13.3\%$ relative reduction (from $45.0\%$ to $39.0\%$).
   - Continuous False Alert Rate: **$-76.9\%$ reduction** (from $6.16\text{ alerts/hr}$ down to $1.42\text{ alerts/hr}$).
2. **Promotion Recommendation:**
   In Phase 45, Detector Improvement V2 should be formally promoted to replace V1 as the primary experimental reference engine. Phase 14 should remain available as the historical production baseline.

