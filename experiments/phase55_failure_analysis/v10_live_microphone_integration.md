# Phase 55 — V10 Dashboard Live Microphone Integration Architecture

**MANDATORY SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.**

*This uncertified research prototype must never be deployed for autonomous emergency dispatch, tactical police response, active-shooter alerting, automated evacuation, building lockdown, or life-critical physical security.*

---

## 1. Executive Summary

To enable live acoustic testing of Detector Improvement V10 on physical hardware, a dedicated **V10 Live Microphone Testing Panel** was integrated into the web dashboard interface (`templates/index.html` and `static/js/app.js`).

The live streaming architecture provides an end-to-end, real-time audio ingestion pipeline connecting client browser microphones to the server-side V10 inference engine, featuring:
- Browser-native Web Audio API capture with device selection.
- High-fidelity in-browser downsampling from native rates (44.1 kHz / 48 kHz) to 16,000 Hz mono PCM.
- Dual-window sliding accumulation (0.96s analysis window, 0.48s hop).
- Session-isolated streaming inference via `RealTimeStreamDetectorImprovementV10`.
- Sub-20 ms server processing latency providing a 24x real-time safety margin against the 480 ms window arrival rate.
- Interactive telemetry reflecting 4-state FSM transitions (`IDLE`, `SUSPECTED`, `CONFIRMED`, `REFRACTORY_COOLDOWN`), level meters, latency counters, and alert logs.

---

## 2. System Architecture & Signal Path

```
┌────────────────────────────────────────────────────────┐
│ BROWSER CLIENT (Web Audio API)                         │
│                                                        │
│  [Physical Microphone]                                 │
│          │                                             │
│          ▼ (Native Sample Rate: 44.1/48 kHz)           │
│  [navigator.mediaDevices.getUserMedia]                 │
│          │                                             │
│          ▼                                             │
│  [MediaStreamAudioSourceNode]                          │
│          │                                             │
│          ▼                                             │
│  [ScriptProcessorNode (bufferSize=4096)]               │
│          │                                             │
│          ├──> [Level Meter: RMS dBFS Display]          │
│          │                                             │
│          ▼ (Linear Resampler: downsampleTo16kHz)       │
│  [16 kHz Mono Float32 Ring Buffer]                     │
│          │                                             │
│          ▼ (Accumulate 15,360 samples, stride 7,680)   │
│  [WAV Blob Packager (float32ToWavBlob)]                │
│          │                                             │
│          ▼ (HTTP POST /api/stream_window)              │
└──────────┼─────────────────────────────────────────────┘
           │
           │ Multipart Form-Data (chunk.wav, session_id, detector_improvement_v10)
           ▼
┌────────────────────────────────────────────────────────┐
│ FLASK BACKEND SERVER (app.py)                          │
│                                                        │
│  [@app.route('/api/stream_window')]                    │
│          │                                             │
│          ▼                                             │
│  [decode_audio_bytes_to_mono_16k]                      │
│          │                                             │
│          ▼                                             │
│  [get_session_stream_detector(session_id, v10)]        │
│          │ (Session Isolation Lock)                    │
│          ▼                                             │
│  [RealTimeStreamDetectorImprovementV10.process_chunk]  │
│          │                                             │
│          ├──> YAMNet 1024-d Embedding Extraction       │
│          ├──> DSP Feature Vector (Crest, Centroid,...) │
│          ├──> BMCC Consensus & Calibration             │
│          ├──> Calibrated Suppression Rules             │
│          └──> Adaptive 4-State FSM Step                │
│          │                                             │
│          ▼ (JSON Response)                             │
│  { score, crest_factor_db, in_event, latency_ms,... }  │
└──────────┼─────────────────────────────────────────────┘
           │
           ▼
┌────────────────────────────────────────────────────────┐
│ CLIENT TELEMETRY & EVENT LOGGING                       │
│                                                        │
│  ├──> FSM State Badge: IDLE / SUSPECTED / CONFIRMED    │
│  ├──> Adjusted Confidence Score Bar                    │
│  ├──> Processing Latency Display (ms)                  │
│  ├──> Dropped Window Backpressure Counter              │
│  ├──> Confirmed Event History Table                    │
│  └──> Real-Time Diagnostic Console Log                 │
└────────────────────────────────────────────────────────┘
```

---

## 3. Key Component Implementation Details

### 3.1 Client Resampling & Window Accumulation (`static/js/app.js`)
Modern operating systems and audio drivers capture microphone input at 44,100 Hz or 48,000 Hz. V10 requires strictly 16,000 Hz mono Float32 audio.
```javascript
// Downsamples arbitrary native audio buffer to 16,000 Hz
function downsampleTo16kHz(buffer, inputSampleRate, targetSampleRate) {
    if (inputSampleRate === targetSampleRate) return buffer;
    const ratio = inputSampleRate / targetSampleRate;
    const newLength = Math.round(buffer.length / ratio);
    const result = new Float32Array(newLength);
    for (let i = 0; i < newLength; i++) {
        const origPos = i * ratio;
        const low = Math.floor(origPos);
        const high = Math.min(low + 1, buffer.length - 1);
        const frac = origPos - low;
        result[i] = buffer[low] * (1 - frac) + buffer[high] * frac;
    }
    return result;
}
```
Audio chunks are accumulated in `v10Buffer16k`. Once the buffer reaches 15,360 samples (0.96s), it slices a processing chunk and advances by 7,680 samples (0.48s), ensuring continuous 50% overlap.

### 3.2 Server Session Isolation (`app.py`)
To prevent session cross-talk when multiple clients or tests run concurrently, `app.py` isolates detector instances by session ID:
```python
SESSION_STREAM_DETECTORS = {}  # session_id -> (detector, timestamp, version, profile)

if version in ["detector_improvement_v10", "v10"]:
    from experiments.detector_improvement_v10.model_detector_improvement_v10 import (
        DetectorImprovementV10, RealTimeStreamDetectorImprovementV10
    )
    detector = RealTimeStreamDetectorImprovementV10()
```
Each instance maintains its own ring buffer, temporal FSM state, noise floor estimator, and refractory cooldown timer.

### 3.3 Diagnostic Console & Operator Controls (`templates/index.html`)
The V10 Live Test Panel exposes comprehensive operator controls:
- **Audio Device Dropdown (`#v10AudioDeviceSelect`):** Enumerates all connected hardware microphones; switching devices automatically hot-reconnects the audio graph.
- **Controls (`Start`, `Stop`, `Reset Session`, `Clear History`):** Allows starting and pausing streaming, resetting backend session states via `/api/stream/reset`, and clearing historical event tables.
- **Real-Time Log Console (`#v10LogConsole`):** Displays timestamped diagnostic events, permission status, connection events, dropped chunk warnings, and confirmed gunshot detections.

---

## 4. Safety Constraints & Production Isolation

1. **Default Production Baseline Preserved:**
   - Phase 14 Balanced Baseline remains the default production detector across `/` and standard API endpoints.
   - V10 is explicitly sandboxed to testing endpoints (`detector_version="detector_improvement_v10"`).
2. **Prominent Safety Designation:**
   - Every UI card, banner, and JSON response prominently bears the mandatory notice:
     `RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY. Experimental acoustic detection only. Do not use for emergency response, tactical decisions, evacuation, lockdown or life-critical security.`

