# PHASE 11 PIPELINE AUDIT: Browser-to-Model Real-Time Acoustic Pathway

> [!CAUTION]
> **SAFETY DESIGNATION: RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY**  
> This acoustic gunshot detection system is strictly an experimental research prototype. It is **NOT** a certified gunshot detection system, life-safety apparatus, or automated emergency dispatch trigger. It must **NEVER** be relied upon for life safety, physical security, or autonomous emergency decision-making.

---

## 1. Executive Summary & Purpose

Phase 11 Stage 1 executed an architectural audit of the entire real-time detection pathway from browser microphone capture to server-side model inference and user interface alert rendering. 

The audit verified each stage against actual code in [`app.py`](file:///e:/gunshot/gunshot/app.py), [`static/js/app.js`](file:///e:/gunshot/gunshot/static/js/app.js), [`templates/index.html`](file:///e:/gunshot/gunshot/templates/index.html), [`model.py`](file:///e:/gunshot/gunshot/model.py), and [`model_phase9.py`](file:///e:/gunshot/gunshot/model_phase9.py).

### Core Audit Findings:
1. **Critical Model Discrepancy in `app.py`:**  
   `app.py` historically imported and instantiated `GunshotDetector` from `model.py` (the legacy Phase 1–3 single-model prototype), completely bypassing the frozen Phase 9 four-model stacking ensemble (`CatBoost`, `LightGBM`, `XGBoost`, `Keras MLP`), multi-category semantic suppression, and physical crest-factor guard.
2. **Stateless Server Window Processing:**  
   The HTTP endpoint `/api/stream_window` received isolated 0.96s audio windows and evaluated them statelessly. Temporal confirmation was delegated to naive integer counting in client-side JavaScript, leaving the system vulnerable to network latency jitter, browser tab throttling, and lost state.
3. **Absence of Calibrated Operating Profiles:**  
   The web UI lacked support for the three Phase 9 calibrated operating profiles (`balanced`, `high_precision`, and `high_sensitivity`). Instead, the UI exposed an uncalibrated sensitivity slider defaulting to `0.19` (an obsolete Phase 2 setting).
4. **Improper Alert Wording:**  
   The live alert banner displayed categorical certainty (`GUNSHOT DETECTED!`), violating the safety standard requiring probabilistic qualification (`Gunshot-like acoustic event detected`).

---

## 2. End-to-End Pathway Trace

The following diagram maps the complete physical data flow through the existing code:

```
+-------------------------------------------------------------------------------------------------------+
|                                    VERIFIED PHYSICAL AUDIO PATHWAY                                    |
+-------------------------------------------------------------------------------------------------------+
|                                                                                                       |
|  [ 1. BROWSER MICROPHONE CAPTURE ]                                                                    |
|    Module: static/js/app.js :: startContinuousListening()                                             |
|    API: navigator.mediaDevices.getUserMedia({ audio: { echoCancellation: false, ... } })             |
|    Native Sample Rate: 44.1 kHz / 48.0 kHz Mono Float32                                               |
|       |                                                                                               |
|       v                                                                                               |
|  [ 2. CLIENT RESAMPLING & WINDOW BUFFERING ]                                                          |
|    Module: static/js/app.js :: downsampleTo16kHz() & appendAudioSamples()                              |
|    Linear interpolation from native rate -> 16,000 Hz                                                 |
|    Windowing: 15,360 samples (0.96s) with 7,680 sample hop (0.48s)                                    |
|       |                                                                                               |
|       v                                                                                               |
|  [ 3. CLIENT ENCODING & TRANSPORT ]                                                                   |
|    Module: static/js/app.js :: evaluateLiveWindow() & float32ToWavBlob()                             |
|    Encoding: PCM 16-bit Little-Endian Mono WAV container                                              |
|    Transport: HTTP POST multipart/form-data to /api/stream_window                                      |
|       |                                                                                               |
|       v                                                                                               |
|  [ 4. SERVER RECEPTION & DECODING ]                                                                   |
|    Module: app.py :: api_stream_window()                                                              |
|    File Handling: tempfile.NamedTemporaryFile(suffix=".wav")                                          |
|    Decoder: dataset.py :: load_audio_mono_16k() via librosa.load(sr=16000, mono=True)              |
|       |                                                                                               |
|       v                                                                                               |
|  [ 5. MODEL INFERENCE -- AUDIT DISCREPANCY IDENTIFIED ]                                               |
|    Historical (FLAWED): model.py :: GunshotDetector.detect_waveform()                                 |
|      -> Only runs Keras MLP head on YAMNet embeddings; NO stacking ensemble, NO semantic gating       |
|    Required (TARGET): model_phase9.py :: Phase9AdaptiveGunshotDetector                                |
|      -> 4-Model Stacking (CatBoost + LightGBM + XGBoost + MLP)                                        |
|      -> Multi-Category Semantic Suppression (Thunder, Fireworks, Barking, Fire, Sirens)               |
|      -> Physical Crest-Factor Guard (>= 9.5 dB floor)                                                 |
|       |                                                                                               |
|       v                                                                                               |
|  [ 6. TEMPORAL STATE MACHINE -- AUDIT DISCREPANCY IDENTIFIED ]                                        |
|    Historical (FLAWED): Handled naively in browser JS (consecutivePositives >= confirmRequired)       |
|    Required (TARGET): Server-side RealTimeStreamDetector maintaining session-isolated ring buffer,     |
|      dual-threshold hysteresis (tau_base, tau_high, tau_off), and refractory cooldown                 |
|       |                                                                                               |
|       v                                                                                               |
|  [ 7. ALERT EMISSION & UI RENDERING ]                                                                 |
|    Module: static/js/app.js :: handleLiveInferenceResult() & triggerLiveGunshotAlert()                |
|    UI: templates/index.html :: #liveAlertBanner                                                       |
|    Telemetry: Latency (ms), RMS (dB), Score (0-1), Operating Profile                                  |
|                                                                                                       |
+-------------------------------------------------------------------------------------------------------+
```

---

## 3. Comprehensive Stage-by-Stage Component Inspection

### Stage 1: Microphone Capture
- **Source Code:** `static/js/app.js:218-283`
- **Method:** `navigator.mediaDevices.getUserMedia()`
- **Audio DSP Bypass:** User-selectable checkbox (`rawAudioDspCheckbox`). When enabled, requests `{ echoCancellation: { ideal: false }, noiseSuppression: { ideal: false }, autoGainControl: { ideal: false } }`.
- **Audit Assessment:** **Compliant.** Disabling browser speech enhancement is essential for gunshot detection because browser AGC and noise suppression distort sharp ballistic transients and crush impulsive crest factors.

### Stage 2: Client Resampling and Windowing
- **Source Code:** `static/js/app.js:359-391`
- **Sampling:** Resamples native AudioContext buffer (44.1 kHz or 48.0 kHz) to 16,000 Hz using linear interpolation.
- **Buffer Geometry:** Window size = 15,360 samples ($0.96\text{s}$), Hop size = 7,680 samples ($0.48\text{s}$).
- **Audit Assessment:** **Compliant.** Window and hop sizes exactly match the YAMNet specification.

### Stage 3: Client Encoding & Transport
- **Source Code:** `static/js/app.js:393-419`
- **Payload:** Packages Float32Array into a compliant 16-bit PCM RIFF/WAV header and sends as `multipart/form-data` via HTTP POST.
- **Audit Assessment:** **Compliant.** HTTP multipart transmission avoids proprietary binary framing and maintains interoperability.

### Stage 4: Server Reception & Decoding
- **Source Code:** `app.py:192-250`
- **Handler:** Saves chunk to a temporary file and decodes with `load_audio_mono_16k(tmp_path)`.
- **Audit Assessment:** **Functional but unbuffered.** Writing each chunk to a temporary disk file adds $1.5\text{--}3.0\text{ ms}$ disk I/O latency. Direct in-memory buffer decoding using `io.BytesIO` and `soundfile.read` is preferable for high throughput.

### Stage 5: Model Inference (CRITICAL DISCREPANCY)
- **Source Code:** `app.py:27, 47, 228`
- **Observed Behavior:**
  ```python
  from model import load_model_bundle, GunshotDetector
  ...
  det = GunshotDetector(bundle_dir=bundle_path)
  ...
  res = det.detect_waveform(waveform, threshold=threshold)
  ```
- **Audit Finding:** `GunshotDetector` is the Phase 1–3 single-model detector. The four-model ensemble, CatBoost, LightGBM, XGBoost, and the five semantic suppression classes in `model_phase9.py` are completely bypassed during live browser streaming!
- **Severity:** **HIGH.** Must be refactored to use `model_phase9.py` and `RealTimeStreamDetector`.

### Stage 6: Temporal Confirmation & Session State
- **Source Code:** `static/js/app.js:421-451`
- **Observed Behavior:** Server returns a raw float score for each window. The browser maintains a local JavaScript counter `consecutivePositives`.
- **Audit Finding:** If network packets arrive out of order, or if the browser tab drops a frame, client-side confirmation becomes corrupted. Furthermore, the dual-threshold override ($\tau_{\text{high}} = 0.88$ for instant single-window recovery) is missing in the client.
- **Severity:** **HIGH.** Temporal confirmation must be executed server-side in a stateful `RealTimeStreamDetector` instance keyed by `session_id`.

### Stage 7: Alert Wording and Operator Interface
- **Source Code:** `templates/index.html:59` and `static/js/app.js:464`
- **Observed Behavior:** Heading says `GUNSHOT DETECTED!` in bold red with `ACTIVE ALARM`.
- **Audit Finding:** Non-compliant with safety guidelines. The alert must state `Gunshot-like acoustic event detected` and prominently retain the safety disclaimer.

---

## 4. Remediation Plan

To achieve complete architectural integrity and true Phase 9 parity:

1. **Refactor `app.py`:**
   - Import `Phase9AdaptiveGunshotDetector` and `RealTimeStreamDetector` from `model_phase9.py`.
   - Implement thread-safe session management (`SessionStreamManager`) maintaining a `RealTimeStreamDetector` per `session_id`.
   - Support profile switching (`balanced`, `high_precision`, `high_sensitivity`).
   - Use direct in-memory WAV decoding via `io.BytesIO` to eliminate disk I/O overhead.
2. **Update Frontend (`templates/index.html` & `static/js/app.js`):**
   - Add Operating Profile dropdown selector (`balanced`, `high_precision`, `high_sensitivity`).
   - Pass `session_id` and selected `profile` in `/api/stream_window` and `/api/detect`.
   - Update alert banner wording to `Gunshot-like acoustic event detected`.
   - Exclude simulated scores or mock detections; display real server telemetry.
3. **Automate Parity & QA Tests:**
   - Create integration tests in `tests/test_phase11_parity_and_qa.py` to ensure the browser endpoint matches offline Phase 9 inference exactly.
