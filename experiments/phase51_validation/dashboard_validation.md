# Phase 51: Web Application & Dashboard Validation

**Mandatory Safety Designation:**
> **RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.**
> This is uncertified research software. Never deploy it for autonomous emergency dispatch, police tactical response, active-shooter alerting, automated evacuation, building lockdown, or life-critical physical security. Use only lawfully obtained recordings and safe audio playback. Live-fire and hazardous acoustic experiments are strictly prohibited.

---

## 1. Web Application Architecture & Endpoint Audit

The web application (`gunshot/app.py`) provides an interactive interface and REST API for batch acoustic file evaluation and live streaming audio detection.

### Endpoint Validation Summary:

| Route | HTTP Method | Validated Parameters | Tested Status | Output Verification |
| :--- | :---: | :--- | :---: | :--- |
| `/api/health` | `GET` | None | **HTTP 200** | Returns system status, model loaded flag, supported versions, and mandatory safety banner. |
| `/api/status` | `GET` | None | **HTTP 200** | Reports active cache statistics, loaded models, and memory status. |
| `/api/profiles` | `GET` | None | **HTTP 200** | Lists operational profiles (`balanced`, `high_precision`, `high_sensitivity`). |
| `/api/detect` | `POST` | `audio` (file), `detector_version`, `profile` | **HTTP 200** | Full waveform batch inference, score breakdown, latency reporting, and verdict. |
| `/api/stream_window` | `POST` | `audio` (chunk), `detector_version`, `profile`, `session_id` | **HTTP 200** | Stateful ring-buffer stream chunk evaluation, FSM transition, cooldown tracking. |
| `/api/stream/reset` | `POST` | `session_id` | **HTTP 200** | Resets streaming buffer and refractory state for specified session. |

---

## 2. Default Configuration & Backward Compatibility

1. **Preservation of Phase 14 as Default:**
   In accordance with research governance mandates, **Phase 14 remains the default detector** across all endpoints and frontend initializations:
   - Requesting `/api/health` returns `"default_detector": "phase14"`.
   - Any API call omitting `detector_version` defaults immediately to `phase14`.
   - The frontend model dropdown initializes with `Phase 14 Candidate (Baseline Default)` selected.
2. **Experimental Candidate Selection:**
   Users can explicitly select experimental versions via UI dropdown or API parameters:
   - `detector_improvement_v8` (`v8`)
   - `detector_improvement_v7` (`v7`)
   - `detector_improvement_v6` (`v6`)
   - `detector_improvement_v5` (`v5`)
   - `detector_improvement_v2` (`v2`)
   - `detector_improvement_v1` (`v1`)
   - `phase17`, `phase14`, `phase13`, `phase9`

---

## 3. Real-Time Streaming Pipeline Integration (V8)

In Phase 51, `RealTimeStreamDetectorImprovementV8` was formally integrated into `gunshot/app.py` and `experiments/detector_improvement_v8/model_detector_improvement_v8.py`.

### Technical Architecture:
- **Thread Safety:** Enforced via `threading.Lock()` on all session buffers.
- **Session Isolation:** Streaming state (ring buffer, condition estimator history, and refractory cooldown) is partitioned per `session_id`. Expired sessions (>15 min idle) are automatically pruned.
- **Ring Buffer Management:** Processes incoming audio chunks, maintains a 15,360-sample (0.96s) analysis window, advances by 7,680 samples (0.48s hop), and computes real-time crest factors and running spectral centroids.
- **API Response Verification:**
  ```json
  {
    "session_id": "test_v8",
    "profile": "balanced",
    "score": 0.0,
    "is_gunshot": false,
    "rms_db": -99.0,
    "crest_factor_db": 0.0,
    "threshold_base": 0.70,
    "threshold_high": 0.85,
    "cooldown_until": 0.0,
    "in_event": false,
    "new_alerts": [],
    "latency_ms": 38.8,
    "safety_designation": "RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY"
  }
  ```

---

## 4. Hardware and Microphone Testing Disclosure

> [!CAUTION]
> **AUDIT AND VALIDATION DISCLOSURE:**
> All continuous streaming and chunk ingestion tests documented in this phase were executed via automated synthetic HTTP test clients and file-backed PCM audio streaming buffers.
> **No live acoustic room microphone testing or physical transducer calibration was performed.**
> The web interface provides browser AudioWorklet microphone capture for demonstration purposes only, requiring explicit user browser permissions. This system has never been calibrated, tested, or certified for life safety, physical security, or acoustic sensor hardware deployments.

