/**
 * Gunshot Sound Detection - Interactive Frontend Application
 * Supports:
 * 1. Continuous Live Microphone Streaming Detection (Real-Time)
 * 2. Audio File Upload & Forensic Analysis
 * 3. Audible Alerts & Desktop Notifications
 * 4. Opt-in Audio Clip Saving to saved_alerts/
 */

// ==========================================
// Global State & Audio Nodes
// ==========================================
let activeMode = 'live'; // 'live' or 'upload'

// Live Audio Streaming State
let liveAudioContext = null;
let liveStream = null;
let liveSource = null;
let liveAnalyser = null;
let liveProcessor = null;
let isLiveListening = false;
let liveStartTime = 0;
let liveTimerInterval = null;

// Streaming Audio Buffer (Ring Buffer at 16 kHz)
const TARGET_SR = 16000;
const WINDOW_SAMPLES = 15360; // 0.96s at 16kHz
const HOP_SAMPLES = 7680;    // 0.48s at 16kHz
let audioBuffer16k = new Float32Array(0);
let isProcessingWindow = false;

// Client Session ID for Server State Isolation
const clientSessionId = 'session_' + Math.random().toString(36).substring(2, 10) + '_' + Date.now();

// Alert Logic State
let consecutivePositives = 0;
let lastAlertTimestamp = 0;
let alertCounter = 0;
let liveAlertsList = [];

// File Upload Analysis State
let activeUploadBlob = null;
let uploadAudioBuffer = null;
let uploadAudioContext = null;
let audioElement = new Audio();
let currentDetectionData = null;

// ==========================================
// DOM Element References
// ==========================================
// Tabs & Views
const tabLiveBtn = document.getElementById('tabLiveBtn');
const tabUploadBtn = document.getElementById('tabUploadBtn');
const liveDetectionView = document.getElementById('liveDetectionView');
const fileUploadView = document.getElementById('fileUploadView');
const alertBox = document.getElementById('alertBox');
const alertMsg = document.getElementById('alertMsg');

// Live Controls
const micDeviceSelect = document.getElementById('micDeviceSelect');
const startLiveBtn = document.getElementById('startLiveBtn');
const stopLiveBtn = document.getElementById('stopLiveBtn');
const liveStatusDot = document.getElementById('liveStatusDot');
const liveStatusText = document.getElementById('liveStatusText');
const liveTimerDisplay = document.getElementById('liveTimerDisplay');
const micRmsDisplay = document.getElementById('micRmsDisplay');
const micMeterFill = document.getElementById('micMeterFill');
const liveLatencyDisplay = document.getElementById('liveLatencyDisplay');
const rawAudioDspCheckbox = document.getElementById('rawAudioDspCheckbox');
const liveScoreDisplay = document.getElementById('liveScoreDisplay');
const scoreMeterFill = document.getElementById('scoreMeterFill');
const thresholdMarker = document.getElementById('thresholdMarker');
const liveSensitivitySlider = document.getElementById('liveSensitivitySlider');
const liveSensitivityValue = document.getElementById('liveSensitivityValue');
const confirmWindowsSelect = document.getElementById('confirmWindowsSelect');
const liveCooldownSlider = document.getElementById('liveCooldownSlider');
const liveCooldownValue = document.getElementById('liveCooldownValue');
const soundAlertCheckbox = document.getElementById('soundAlertCheckbox');
const desktopNotifyCheckbox = document.getElementById('desktopNotifyCheckbox');
const optInSaveClipsCheckbox = document.getElementById('optInSaveClipsCheckbox');
const liveAlertBanner = document.getElementById('liveAlertBanner');
const liveAlertTime = document.getElementById('liveAlertTime');
const liveAlertScore = document.getElementById('liveAlertScore');
const liveAlertProfile = document.getElementById('liveAlertProfile');
const operatingProfileSelect = document.getElementById('operatingProfileSelect');
const liveAlertsTableBody = document.getElementById('liveAlertsTableBody');
const noLiveAlertsRow = document.getElementById('noLiveAlertsRow');
const liveAlertsCountBadge = document.getElementById('liveAlertsCountBadge');

// Upload Controls
const dropzone = document.getElementById('dropzone');
const audioFileInput = document.getElementById('audioFileInput');
const fileInfo = document.getElementById('fileInfo');
const fileNameDisplay = document.getElementById('fileNameDisplay');
const sensitivitySlider = document.getElementById('sensitivitySlider');
const sensitivityValue = document.getElementById('sensitivityValue');
const mergeWindowSlider = document.getElementById('mergeWindowSlider');
const mergeWindowValue = document.getElementById('mergeWindowValue');
const runDetectionBtn = document.getElementById('runDetectionBtn');
const resultsSection = document.getElementById('resultsSection');
const verdictBanner = document.getElementById('verdictBanner');
const verdictTitle = document.getElementById('verdictTitle');
const verdictSubtitle = document.getElementById('verdictSubtitle');
const scoreDisplay = document.getElementById('scoreDisplay');
const waveformCanvas = document.getElementById('waveformCanvas');
const playPauseBtn = document.getElementById('playPauseBtn');
const timeDisplay = document.getElementById('timeDisplay');
const eventsTableBody = document.getElementById('eventsTableBody');
const noEventsRow = document.getElementById('noEventsRow');

// ==========================================
// Initialization
// ==========================================
window.addEventListener('DOMContentLoaded', () => {
    initNavigationTabs();
    initLiveControls();
    initUploadControls();
    initDemoReplayControls();
    initV10LivePanel();
    populateAudioInputDevices();
    requestNotificationPermission();
    fetchSystemStatus();
});

async function fetchSystemStatus() {
    try {
        const res = await fetch('/api/status');
        if (res.ok) {
            const data = await res.json();
            const thresh = parseFloat(data.current_threshold_base || data.default_threshold || 0.75);
            liveSensitivitySlider.value = thresh;
            liveSensitivityValue.textContent = thresh.toFixed(2);
            thresholdMarker.style.left = `${(thresh * 100).toFixed(1)}%`;
            sensitivitySlider.value = thresh;
            sensitivityValue.textContent = thresh.toFixed(2);
        }
    } catch (e) {
        console.warn('Could not fetch server status:', e);
    }
}

function showAlert(msg) {
    alertMsg.textContent = msg;
    alertBox.style.display = 'block';
    setTimeout(() => alertBox.scrollIntoView({ behavior: 'smooth', block: 'nearest' }), 50);
}

function hideAlert() {
    alertBox.style.display = 'none';
}

function requestNotificationPermission() {
    if ('Notification' in window && Notification.permission === 'default') {
        Notification.requestPermission();
    }
}

// Navigation Tabs
function initNavigationTabs() {
    const tabV10LiveBtn = document.getElementById('tabV10LiveBtn');
    const v10LiveDetectionView = document.getElementById('v10LiveDetectionView');

    tabLiveBtn.addEventListener('click', () => {
        activeMode = 'live';
        tabLiveBtn.classList.add('active');
        tabUploadBtn.classList.remove('active');
        if (tabV10LiveBtn) tabV10LiveBtn.classList.remove('active');
        liveDetectionView.style.display = 'block';
        fileUploadView.style.display = 'none';
        if (v10LiveDetectionView) v10LiveDetectionView.style.display = 'none';
        hideAlert();
    });

    tabUploadBtn.addEventListener('click', () => {
        activeMode = 'upload';
        tabUploadBtn.classList.add('active');
        tabLiveBtn.classList.remove('active');
        if (tabV10LiveBtn) tabV10LiveBtn.classList.remove('active');
        liveDetectionView.style.display = 'none';
        fileUploadView.style.display = 'block';
        if (v10LiveDetectionView) v10LiveDetectionView.style.display = 'none';
        hideAlert();
    });

    if (tabV10LiveBtn) {
        tabV10LiveBtn.addEventListener('click', () => {
            activeMode = 'v10_live';
            tabV10LiveBtn.classList.add('active');
            tabLiveBtn.classList.remove('active');
            tabUploadBtn.classList.remove('active');
            liveDetectionView.style.display = 'none';
            fileUploadView.style.display = 'none';
            if (v10LiveDetectionView) v10LiveDetectionView.style.display = 'block';
            hideAlert();
            populateV10AudioDevices();
        });
    }
}

// ==========================================
// 1. LIVE CONTINUOUS MICROPHONE DETECTION
// ==========================================
async function populateAudioInputDevices() {
    try {
        if (!navigator.mediaDevices || !navigator.mediaDevices.enumerateDevices) return;
        const devices = await navigator.mediaDevices.enumerateDevices();
        const audioInputs = devices.filter(d => d.kind === 'audioinput');

        const currentVal = micDeviceSelect.value;
        micDeviceSelect.innerHTML = '<option value="default">Default System Microphone</option>';

        audioInputs.forEach((device, idx) => {
            if (device.deviceId && device.deviceId !== 'default' && device.deviceId !== '') {
                const opt = document.createElement('option');
                opt.value = device.deviceId;
                opt.textContent = device.label || `Microphone ${idx + 1}`;
                if (device.deviceId === currentVal) opt.selected = true;
                micDeviceSelect.appendChild(opt);
            }
        });
    } catch (e) {
        console.warn('Could not enumerate audio devices:', e);
    }
}

function initLiveControls() {
    // Detector Engine Selector
    const detectorEngineSelect = document.getElementById('detectorEngineSelect');
    if (detectorEngineSelect) {
        detectorEngineSelect.addEventListener('change', () => {
            const fd = new FormData();
            fd.append('session_id', clientSessionId);
            fetch('/api/stream/reset', { method: 'POST', body: fd }).catch(() => {});
        });
    }

    // Operating Profile Selector
    if (operatingProfileSelect) {
        operatingProfileSelect.addEventListener('change', (e) => {
            const prof = e.target.value;
            const defs = {
                balanced: { base: 0.75, high: 0.88, cooldown: 2.0 },
                high_precision: { base: 0.80, high: 0.90, cooldown: 2.5 },
                high_sensitivity: { base: 0.70, high: 0.82, cooldown: 1.5 }
            };
            const cfg = defs[prof] || defs.balanced;
            liveSensitivitySlider.value = cfg.base;
            liveSensitivityValue.textContent = cfg.base.toFixed(2);
            thresholdMarker.style.left = `${(cfg.base * 100).toFixed(1)}%`;
            liveCooldownSlider.value = cfg.cooldown;
            liveCooldownValue.textContent = cfg.cooldown.toFixed(1) + 's';
            
            // Notify server to switch/reset profile for this session
            const fd = new FormData();
            fd.append('session_id', clientSessionId);
            fetch('/api/stream/reset', { method: 'POST', body: fd }).catch(() => {});
        });
    }

    // Sensitivity Slider
    liveSensitivitySlider.addEventListener('input', (e) => {
        const val = parseFloat(e.target.value);
        liveSensitivityValue.textContent = val.toFixed(2);
        thresholdMarker.style.left = `${(val * 100).toFixed(1)}%`;
    });

    // Cooldown Slider
    liveCooldownSlider.addEventListener('input', (e) => {
        liveCooldownValue.textContent = parseFloat(e.target.value).toFixed(1) + 's';
    });

    // Start / Stop Listening
    startLiveBtn.addEventListener('click', startContinuousListening);
    stopLiveBtn.addEventListener('click', stopContinuousListening);
}

async function startContinuousListening() {
    hideAlert();
    if (isLiveListening) return;

    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        showAlert('Microphone audio capture is not supported in this browser.');
        return;
    }

    try {
        const selectedDeviceId = micDeviceSelect.value;
        let stream = null;

        // Progressive fallback for maximum cross-browser/hardware driver compatibility
        try {
            const bypassDsp = rawAudioDspCheckbox && rawAudioDspCheckbox.checked;
            const audioConstraints = {
                echoCancellation: bypassDsp ? { ideal: false } : { ideal: true },
                noiseSuppression: bypassDsp ? { ideal: false } : { ideal: true },
                autoGainControl: bypassDsp ? { ideal: false } : { ideal: true }
            };
            if (selectedDeviceId && selectedDeviceId !== 'default') {
                audioConstraints.deviceId = { ideal: selectedDeviceId };
            }
            stream = await navigator.mediaDevices.getUserMedia({ audio: audioConstraints });
        } catch (constraintErr) {
            console.warn('Constraint error, falling back to default audio stream:', constraintErr);
            // Fallback: request default microphone stream without constraints
            stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        }

        liveStream = stream;

        // Inspect and log negotiated browser DSP settings
        const audioTrack = liveStream.getAudioTracks()[0];
        if (audioTrack && audioTrack.getSettings) {
            const trackSettings = audioTrack.getSettings();
            console.log('Applied Microphone Audio Settings:', trackSettings);
            const appliedBadge = document.getElementById('appliedDspBadge');
            if (appliedBadge) {
                const aec = trackSettings.echoCancellation === false ? 'AEC: Off' : 'AEC: On';
                const agc = trackSettings.autoGainControl === false ? 'AGC: Off' : 'AGC: On';
                const ns = trackSettings.noiseSuppression === false ? 'NS: Off' : 'NS: On';
                appliedBadge.textContent = `[Active: ${aec}, ${agc}, ${ns}]`;
                appliedBadge.style.display = 'inline';
            }
        }

        // Refresh device labels now that microphone permission is granted
        populateAudioInputDevices();

        liveAudioContext = new (window.AudioContext || window.webkitAudioContext)({ sampleRate: 44100 });
        if (liveAudioContext.state === 'suspended') {
            await liveAudioContext.resume();
        }

        liveSource = liveAudioContext.createMediaStreamSource(liveStream);
        liveAnalyser = liveAudioContext.createAnalyser();
        liveAnalyser.fftSize = 512;
        liveSource.connect(liveAnalyser);

        // ScriptProcessorNode to capture raw float32 samples (compatible across all modern browsers)
        liveProcessor = liveAudioContext.createScriptProcessor(4096, 1, 1);
        liveSource.connect(liveProcessor);
        liveProcessor.connect(liveAudioContext.destination);

        audioBuffer16k = new Float32Array(0);
        isLiveListening = true;

        startLiveBtn.style.display = 'none';
        stopLiveBtn.style.display = 'inline-block';
        liveStatusDot.className = 'status-dot listening';
        liveStatusText.textContent = 'Listening Continuously (AI Active)';
        liveStartTime = Date.now();
        liveTimerInterval = setInterval(updateLiveTimer, 1000);

        // Start VU meter animation loop
        requestAnimationFrame(updateVuMeter);

        // Audio frame accumulator
        liveProcessor.onaudioprocess = (e) => {
            if (!isLiveListening) return;
            const inputData = e.inputBuffer.getChannelData(0);
            // Downsample native buffer to 16 kHz
            const resampled = downsampleTo16kHz(inputData, liveAudioContext.sampleRate, TARGET_SR);
            appendAudioSamples(resampled);
        };

    } catch (err) {
        console.error('Failed to start microphone:', err);
        if (err.name === 'NotAllowedError' || err.name === 'PermissionDeniedError') {
            showAlert('Microphone permission was denied. Please allow microphone access in your browser to start live detection.');
        } else {
            showAlert(`Microphone error: ${err.message || err.name}`);
        }
        stopContinuousListening();
    }
}

function stopContinuousListening() {
    isLiveListening = false;
    if (liveStream) {
        liveStream.getTracks().forEach(t => t.stop());
        liveStream = null;
    }
    if (liveProcessor) {
        liveProcessor.disconnect();
        liveProcessor = null;
    }
    if (liveSource) {
        liveSource.disconnect();
        liveSource = null;
    }
    if (liveAudioContext && liveAudioContext.state !== 'closed') {
        liveAudioContext.close();
        liveAudioContext = null;
    }

    clearInterval(liveTimerInterval);
    startLiveBtn.style.display = 'inline-block';
    stopLiveBtn.style.display = 'none';
    liveStatusDot.className = 'status-dot standby';
    liveStatusText.textContent = 'Standby (Stopped)';
    micMeterFill.style.width = '0%';
    micRmsDisplay.textContent = '-inf dB';
    scoreMeterFill.style.width = '0%';
    liveScoreDisplay.textContent = '0.000';
    if (liveLatencyDisplay) liveLatencyDisplay.textContent = 'Latency: -- ms';
    const appliedBadge = document.getElementById('appliedDspBadge');
    if (appliedBadge) appliedBadge.style.display = 'none';
    liveAlertBanner.style.display = 'none';

    // Reset server session stream state
    const fd = new FormData();
    fd.append('session_id', clientSessionId);
    fetch('/api/stream/reset', { method: 'POST', body: fd }).catch(() => {});
}

function updateLiveTimer() {
    const elapsed = Math.floor((Date.now() - liveStartTime) / 1000);
    const h = String(Math.floor(elapsed / 3600)).padStart(2, '0');
    const m = String(Math.floor((elapsed % 3600) / 60)).padStart(2, '0');
    const s = String(elapsed % 60).padStart(2, '0');
    liveTimerDisplay.textContent = `${h}:${m}:${s}`;
}

// Resampling helper: downsamples float32 array to 16 kHz
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

// Append samples to buffer and trigger window evaluation every HOP_SAMPLES
function appendAudioSamples(newSamples) {
    const combined = new Float32Array(audioBuffer16k.length + newSamples.length);
    combined.set(audioBuffer16k);
    combined.set(newSamples, audioBuffer16k.length);
    audioBuffer16k = combined;

    // Check if we have at least 1 full window (0.96s)
    if (audioBuffer16k.length >= WINDOW_SAMPLES && !isProcessingWindow) {
        // Extract 0.96s slice
        const windowToProcess = audioBuffer16k.slice(0, WINDOW_SAMPLES);
        // Slide by HOP_SAMPLES (0.48s)
        audioBuffer16k = audioBuffer16k.slice(HOP_SAMPLES);

        evaluateLiveWindow(windowToProcess);
    }
}

// Send window to backend /api/stream_window
async function evaluateLiveWindow(windowFloat32) {
    isProcessingWindow = true;
    try {
        const prof = operatingProfileSelect ? operatingProfileSelect.value : 'balanced';
        const engineSelect = document.getElementById('detectorEngineSelect');
        const engineVer = engineSelect ? engineSelect.value : 'phase14';
        const wavBlob = float32ToWavBlob(windowFloat32, TARGET_SR);

        const formData = new FormData();
        formData.append('audio', wavBlob, 'stream_window.wav');
        formData.append('session_id', clientSessionId);
        formData.append('profile', prof);
        formData.append('detector_version', engineVer);

        const res = await fetch('/api/stream_window', {
            method: 'POST',
            body: formData
        });

        if (!res.ok) throw new Error('Stream window API returned non-200');
        const data = await res.json();

        handleLiveInferenceResult(data, windowFloat32);

    } catch (e) {
        console.warn('Live stream inference error:', e);
    } finally {
        isProcessingWindow = false;
    }
}

// Process detection outcome from backend RealTimeStreamDetector
function handleLiveInferenceResult(result, windowWaveform) {
    const score = result.score || 0.0;
    const threshold = result.threshold_base || parseFloat(liveSensitivitySlider.value);

    // Update Live Score Bar & Latency
    liveScoreDisplay.textContent = score.toFixed(3);
    if (liveLatencyDisplay && result.latency_ms !== undefined) {
        liveLatencyDisplay.textContent = `Latency: ${result.latency_ms} ms`;
    }
    const crestEl = document.getElementById('liveCrestDisplay');
    if (crestEl && result.crest_factor_db !== undefined) {
        crestEl.textContent = `Crest: ${result.crest_factor_db} dB`;
    }
    const stateEl = document.getElementById('liveStateDisplay');
    if (stateEl) {
        if (result.in_event) {
            stateEl.textContent = 'State: CONFIRMED';
            stateEl.style.color = '#ef4444';
        } else if (result.cooldown_until && result.cooldown_until > 0) {
            stateEl.textContent = 'State: COOLDOWN';
            stateEl.style.color = '#3b82f6';
        } else {
            stateEl.textContent = 'State: IDLE';
            stateEl.style.color = '#f59e0b';
        }
    }
    const scorePct = Math.min(100, Math.max(0, score * 100));
    scoreMeterFill.style.width = `${scorePct.toFixed(1)}%`;

    // Process server-side dispatched alerts from RealTimeStreamDetector
    if (result.new_alerts && result.new_alerts.length > 0) {
        for (const alert of result.new_alerts) {
            triggerLiveGunshotAlert(alert.score, threshold, windowWaveform, alert);
        }
    }
}

// Trigger Confirmed Gunshot Alert
async function triggerLiveGunshotAlert(score, threshold, windowWaveform, alertObj = null) {
    alertCounter++;
    const nowDt = new Date();
    const timeStr = nowDt.toLocaleTimeString();
    const profileName = (alertObj && alertObj.profile) || (operatingProfileSelect ? operatingProfileSelect.value : 'balanced');

    // 1. Visual Alert Banner (Compliant wording)
    liveAlertBanner.style.display = 'flex';
    liveAlertTime.textContent = timeStr;
    liveAlertScore.textContent = score.toFixed(3);
    if (liveAlertProfile) liveAlertProfile.textContent = profileName;
    liveStatusDot.className = 'status-dot alert';
    liveStatusText.textContent = `ALERT: Gunshot-like Acoustic Event (${score.toFixed(3)})`;

    // 2. Audible Sound Alert (Synthesized dual-tone siren)
    if (soundAlertCheckbox.checked) {
        playAudibleAlarm();
    }

    // 3. Desktop Notification
    if (desktopNotifyCheckbox.checked && 'Notification' in window && Notification.permission === 'granted') {
        new Notification('GUNSHOT-LIKE SOUND EVENT DETECTED', {
            body: `Gunshot-like acoustic pattern score ${score.toFixed(3)} detected at ${timeStr}. (PROTOTYPE - NOT FOR LIFE SAFETY)`,
            icon: '/static/img/alert-icon.png'
        });
    }

    // 4. Opt-in Audio Clip Saving to saved_alerts/
    let savedInfo = 'Not saved (Privacy)';
    if (optInSaveClipsCheckbox.checked) {
        savedInfo = 'Saving...';
        const wavBlob = float32ToWavBlob(windowWaveform, TARGET_SR);
        const fd = new FormData();
        fd.append('audio', wavBlob, 'alert_clip.wav');
        fd.append('score', score.toFixed(3));
        fd.append('profile', profileName);

        try {
            const resp = await fetch('/api/save_alert', { method: 'POST', body: fd });
            const sData = await resp.json();
            if (sData.saved) {
                savedInfo = `Saved: ${sData.filename}`;
            }
        } catch (err) {
            savedInfo = 'Failed to save';
        }
    }

    // 5. Add to Live Alert History Table
    addAlertToHistoryTable(alertCounter, timeStr, score, savedInfo);

    // Auto-dismiss visual alert banner after cooldown
    const cooldownSecs = parseFloat(liveCooldownSlider.value);
    setTimeout(() => {
        if (isLiveListening) {
            liveAlertBanner.style.display = 'none';
            liveStatusDot.className = 'status-dot listening';
            liveStatusText.textContent = 'Listening Continuously (AI Active)';
        }
    }, Math.max(2500, cooldownSecs * 1000));
}

function addAlertToHistoryTable(idx, timeStr, score, savedInfo) {
    noLiveAlertsRow.style.display = 'none';
    liveAlertsCountBadge.textContent = `${idx} Alert${idx > 1 ? 's' : ''}`;

    const tr = document.createElement('tr');
    tr.innerHTML = `
        <td>#${idx}</td>
        <td><strong>${timeStr}</strong></td>
        <td><strong style="color: #ff334b;">${score.toFixed(3)}</strong></td>
        <td><span class="badge-danger">Gunshot Alert</span></td>
        <td style="font-size: 11px; color: var(--text-muted);">${savedInfo}</td>
    `;
    liveAlertsTableBody.insertBefore(tr, liveAlertsTableBody.firstChild);
}

// Audible Alarm (Synthesizes acoustic warble/siren in Web Audio)
function playAudibleAlarm() {
    try {
        const ctx = new (window.AudioContext || window.webkitAudioContext)();
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();

        osc.type = 'sawtooth';
        osc.frequency.setValueAtTime(800, ctx.currentTime);
        osc.frequency.linearRampToValueAtTime(1400, ctx.currentTime + 0.15);
        osc.frequency.linearRampToValueAtTime(800, ctx.currentTime + 0.3);

        gain.gain.setValueAtTime(0.3, ctx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 0.4);

        osc.connect(gain);
        gain.connect(ctx.destination);

        osc.start();
        osc.stop(ctx.currentTime + 0.4);
    } catch (e) {
        console.warn('Alarm audio error:', e);
    }
}

// VU Meter Loop
function updateVuMeter() {
    if (!isLiveListening || !liveAnalyser) return;

    const dataArray = new Uint8Array(liveAnalyser.frequencyBinCount);
    liveAnalyser.getByteTimeDomainData(dataArray);

    let sumSquares = 0;
    for (let i = 0; i < dataArray.length; i++) {
        const normalized = (dataArray[i] - 128) / 128;
        sumSquares += normalized * normalized;
    }
    const rms = Math.sqrt(sumSquares / dataArray.length);
    const db = 20 * Math.log10(Math.max(rms, 1e-4));

    // Map -60 dB -> 0%, 0 dB -> 100%
    const meterPct = Math.min(100, Math.max(0, ((db + 60) / 60) * 100));
    micMeterFill.style.width = `${meterPct.toFixed(1)}%`;
    micRmsDisplay.textContent = `${db.toFixed(1)} dB`;

    requestAnimationFrame(updateVuMeter);
}

// Convert float32 array to WAV Blob
function float32ToWavBlob(samples, sampleRate) {
    const buffer = new ArrayBuffer(44 + samples.length * 2);
    const view = new DataView(buffer);

    // RIFF chunk descriptor
    writeString(view, 0, 'RIFF');
    view.setUint32(4, 36 + samples.length * 2, true);
    writeString(view, 8, 'WAVE');
    // FMT sub-chunk
    writeString(view, 12, 'fmt ');
    view.setUint32(16, 16, true);
    view.setUint16(20, 1, true); // PCM
    view.setUint16(22, 1, true); // Mono
    view.setUint32(24, sampleRate, true);
    view.setUint32(28, sampleRate * 2, true); // Byte rate
    view.setUint16(32, 2, true); // Block align
    view.setUint16(34, 16, true); // Bits per sample
    // Data sub-chunk
    writeString(view, 36, 'data');
    view.setUint32(40, samples.length * 2, true);

    // Write samples
    let offset = 44;
    for (let i = 0; i < samples.length; i++, offset += 2) {
        const s = Math.max(-1, Math.min(1, samples[i]));
        view.setInt16(offset, s < 0 ? s * 0x8000 : s * 0x7FFF, true);
    }

    return new Blob([view], { type: 'audio/wav' });
}

function writeString(view, offset, string) {
    for (let i = 0; i < string.length; i++) {
        view.setUint8(offset + i, string.charCodeAt(i));
    }
}

// ==========================================
// 2. AUDIO FILE UPLOAD & FORENSIC ANALYSIS
// ==========================================
function initUploadControls() {
    sensitivitySlider.addEventListener('input', (e) => {
        const val = parseFloat(e.target.value);
        sensitivityValue.textContent = val.toFixed(2);
        if (currentDetectionData) reclusterClientSide(val, parseFloat(mergeWindowSlider.value));
    });

    mergeWindowSlider.addEventListener('input', (e) => {
        const val = parseFloat(e.target.value);
        mergeWindowValue.textContent = val.toFixed(1) + 's';
        if (currentDetectionData) reclusterClientSide(parseFloat(sensitivitySlider.value), val);
    });

    dropzone.addEventListener('click', () => audioFileInput.click());
    dropzone.addEventListener('dragover', (e) => { e.preventDefault(); dropzone.classList.add('dragover'); });
    dropzone.addEventListener('dragleave', () => dropzone.classList.remove('dragover'));
    dropzone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropzone.classList.remove('dragover');
        if (e.dataTransfer.files.length > 0) handleSelectedFile(e.dataTransfer.files[0]);
    });
    audioFileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) handleSelectedFile(e.target.files[0]);
    });

    playPauseBtn.addEventListener('click', () => {
        if (!audioElement.src) return;
        if (audioElement.paused) {
            audioElement.play();
            playPauseBtn.innerHTML = '&#10074;&#10074;';
        } else {
            audioElement.pause();
            playPauseBtn.innerHTML = '&#9658;';
        }
    });

    audioElement.addEventListener('timeupdate', () => {
        const cur = audioElement.currentTime;
        const dur = audioElement.duration || 0;
        timeDisplay.textContent = `${formatTime(cur)} / ${formatTime(dur)}`;
        if (uploadAudioBuffer) {
            const events = currentDetectionData ? currentDetectionData.events : [];
            drawWaveform(uploadAudioBuffer, events, cur / dur);
        }
    });

    audioElement.addEventListener('ended', () => { playPauseBtn.innerHTML = '&#9658;'; });

    runDetectionBtn.addEventListener('click', runFileDetection);
}

function handleSelectedFile(file) {
    hideAlert();
    const allowed = ['.mp3', '.wav', '.ogg', '.flac', '.m4a'];
    const ext = '.' + file.name.split('.').pop().toLowerCase();
    if (!allowed.includes(ext)) {
        showAlert(`Unsupported audio format (${ext}). Supported: MP3, WAV, FLAC, OGG, M4A.`);
        return;
    }
    if (file.size === 0) {
        showAlert('The selected audio file is empty (0 bytes).');
        return;
    }

    activeUploadBlob = file;
    fileNameDisplay.textContent = `${file.name} (${(file.size / 1024).toFixed(1)} KB)`;
    fileInfo.style.display = 'block';

    loadAudioForVisualizer(file);
}

async function loadAudioForVisualizer(file) {
    try {
        if (!uploadAudioContext) uploadAudioContext = new (window.AudioContext || window.webkitAudioContext)();
        const arrayBuffer = await file.arrayBuffer();
        uploadAudioBuffer = await uploadAudioContext.decodeAudioData(arrayBuffer);

        audioElement.src = URL.createObjectURL(file);
        audioElement.load();

        drawWaveform(uploadAudioBuffer, []);
    } catch (err) {
        console.error('Audio decode error:', err);
        showAlert('Could not decode audio. File may be corrupt or encoded in an unsupported format.');
    }
}

async function runFileDetection() {
    hideAlert();
    if (!activeUploadBlob) {
        showAlert('Please choose an audio file to analyze first.');
        return;
    }

    runDetectionBtn.disabled = true;
    runDetectionBtn.textContent = 'Analyzing with YAMNet...';

    const formData = new FormData();
    const uploadProf = document.getElementById('uploadOperatingProfileSelect');
    const prof = uploadProf ? uploadProf.value : 'balanced';
    const uploadEng = document.getElementById('uploadDetectorEngineSelect');
    const engineVer = uploadEng ? uploadEng.value : 'phase14';
    formData.append('audio', activeUploadBlob, activeUploadBlob.name || 'file.mp3');
    formData.append('profile', prof);
    formData.append('detector_version', engineVer);
    formData.append('threshold', sensitivitySlider.value);
    formData.append('merge_window', mergeWindowSlider.value);

    try {
        const response = await fetch('/api/detect', { method: 'POST', body: formData });
        const data = await response.json();
        if (!response.ok) throw new Error(data.error || data.details || 'Detection failed');

        currentDetectionData = data;
        displayFileResults(data);

    } catch (err) {
        showAlert(`Error: ${err.message}`);
    } finally {
        runDetectionBtn.disabled = false;
        runDetectionBtn.textContent = 'Analyze Audio File';
    }
}

function displayFileResults(data) {
    resultsSection.style.display = 'flex';
    document.getElementById('emptyState').style.display = 'none';

    scoreDisplay.textContent = (data.overall_score !== undefined ? data.overall_score : 0.0).toFixed(3);

    const eventCount = (data.events ? data.events.length : 0) || data.events_count || 0;
    if (data.gunshot_detected || data.is_gunshot) {
        verdictBanner.className = 'verdict-banner positive';
        verdictTitle.textContent = `ALERT: Gunshot-like Acoustic Event Detected (${eventCount} Event${eventCount > 1 ? 's' : ''})`;
        verdictTitle.style.color = '#ff334b';
        verdictSubtitle.textContent = `Pattern matched ballistic profile with peak score ${(data.overall_score || 0).toFixed(3)}. RESEARCH PROTOTYPE - NOT FOR LIFE SAFETY.`;
    } else {
        verdictBanner.className = 'verdict-banner negative';
        verdictTitle.textContent = 'CLEAN: No Gunshot-like Event Detected';
        verdictTitle.style.color = '#10b981';
        verdictSubtitle.textContent = `Max score ${(data.overall_score || 0).toFixed(3)} remained safely below threshold.`;
    }

    renderEventsTable(data.events);
    if (uploadAudioBuffer) drawWaveform(uploadAudioBuffer, data.events);
}

function reclusterClientSide(threshold, mergeWindowSecs) {
    if (!currentDetectionData || !currentDetectionData.window_results) return;

    const positiveWindows = currentDetectionData.window_results.filter(w => w.score >= threshold);
    let events = [];

    if (positiveWindows.length > 0) {
        positiveWindows.sort((a, b) => a.start_time - b.start_time);
        let cluster = [positiveWindows[0]];

        for (let i = 1; i < positiveWindows.length; i++) {
            const win = positiveWindows[i];
            const prev = cluster[cluster.length - 1];
            if (win.start_time <= prev.end_time + mergeWindowSecs) {
                cluster.push(win);
            } else {
                events.push(summarizeCluster(cluster));
                cluster = [win];
            }
        }
        if (cluster.length > 0) events.push(summarizeCluster(cluster));
    }

    currentDetectionData.events = events;
    currentDetectionData.events_count = events.length;
    currentDetectionData.selected_threshold = threshold;
    currentDetectionData.gunshot_detected = events.length > 0;

    displayFileResults(currentDetectionData);
}

function summarizeCluster(cluster) {
    const start_time = cluster[0].start_time;
    const end_time = cluster[cluster.length - 1].end_time;
    let peakWin = cluster[0];
    let sum = 0;
    cluster.forEach(w => {
        sum += w.score;
        if (w.score > peakWin.score) peakWin = w;
    });

    return {
        start_time: Number(start_time.toFixed(2)),
        end_time: Number(end_time.toFixed(2)),
        duration_seconds: Number((end_time - start_time).toFixed(2)),
        peak_time: Number(((peakWin.start_time + peakWin.end_time) / 2).toFixed(2)),
        peak_score: Number(peakWin.score.toFixed(3)),
        trigger_windows_count: cluster.length,
        verdict: 'Gunshot Detected'
    };
}

function renderEventsTable(events) {
    eventsTableBody.innerHTML = '';
    if (!events || events.length === 0) {
        noEventsRow.style.display = 'table-row';
        eventsTableBody.appendChild(noEventsRow);
        return;
    }

    noEventsRow.style.display = 'none';
    events.forEach((ev, idx) => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>#${idx + 1}</td>
            <td><strong>${ev.start_time}s</strong> &rarr; <strong>${ev.end_time}s</strong></td>
            <td>${ev.peak_time}s</td>
            <td>${ev.duration_seconds}s (${ev.trigger_windows_count} win)</td>
            <td><strong style="color: #ff334b;">${ev.peak_score.toFixed(3)}</strong></td>
            <td><span class="badge-danger">Gunshot</span></td>
        `;
        tr.style.cursor = 'pointer';
        tr.addEventListener('click', () => {
            if (audioElement.duration) {
                audioElement.currentTime = ev.start_time;
                audioElement.play();
                playPauseBtn.innerHTML = '&#10074;&#10074;';
            }
        });
        eventsTableBody.appendChild(tr);
    });
}

function drawWaveform(buffer, events = [], playheadRatio = 0) {
    const canvas = waveformCanvas;
    const ctx = canvas.getContext('2d');
    const width = canvas.width = canvas.offsetWidth * window.devicePixelRatio;
    const height = canvas.height = canvas.offsetHeight * window.devicePixelRatio;

    ctx.clearRect(0, 0, width, height);

    const channelData = buffer.getChannelData(0);
    const totalSamples = channelData.length;
    const totalDuration = buffer.duration;
    const step = Math.ceil(totalSamples / width);
    const amp = height / 2;

    // Draw Event Markers (Red Highlight Bands)
    events.forEach(ev => {
        const startX = (ev.start_time / totalDuration) * width;
        const endX = (ev.end_time / totalDuration) * width;
        const w = Math.max(endX - startX, 4);

        ctx.fillStyle = 'rgba(255, 51, 75, 0.25)';
        ctx.fillRect(startX, 0, w, height);

        ctx.strokeStyle = 'rgba(255, 51, 75, 0.8)';
        ctx.lineWidth = 2;
        ctx.strokeRect(startX, 0, w, height);
    });

    // Waveform
    ctx.fillStyle = '#00f0ff';
    for (let i = 0; i < width; i++) {
        let min = 1.0;
        let max = -1.0;
        for (let j = 0; j < step; j++) {
            const datum = channelData[(i * step) + j];
            if (datum < min) min = datum;
            if (datum > max) max = datum;
        }
        const yTop = (1 + min) * amp;
        const yBottom = Math.max(1, (max - min) * amp);
        ctx.fillRect(i, yTop, 1, yBottom);
    }

    // Playhead
    if (playheadRatio > 0 && playheadRatio <= 1) {
        const x = playheadRatio * width;
        ctx.strokeStyle = '#ffffff';
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.moveTo(x, 0);
        ctx.lineTo(x, height);
        ctx.stroke();
    }
}

function formatTime(secs) {
    const m = Math.floor(secs / 60);
    const s = Math.floor(secs % 60);
    return `${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`;
}

// ==========================================
// Senior Walkthrough WAV Replay Controls
// ==========================================
let isDemoReplaying = false;
let demoReplayInterval = null;

function initDemoReplayControls() {
    const demoGunshotBtn = document.getElementById('demoGunshotBtn');
    const demoFireworksBtn = document.getElementById('demoFireworksBtn');
    const demoAmbientBtn = document.getElementById('demoAmbientBtn');
    const demoCustomFileBtn = document.getElementById('demoCustomFileBtn');
    const demoCustomFileInput = document.getElementById('demoCustomFileInput');
    const stopDemoReplayBtn = document.getElementById('stopDemoReplayBtn');

    if (demoGunshotBtn) {
        demoGunshotBtn.addEventListener('click', () => startDemoReplay('/static/demo_samples/gunshot_positive_demo.wav', 'Gunshot Demo'));
    }
    if (demoFireworksBtn) {
        demoFireworksBtn.addEventListener('click', () => startDemoReplay('/static/demo_samples/fireworks_distractor_demo.wav', 'Fireworks Demo'));
    }
    if (demoAmbientBtn) {
        demoAmbientBtn.addEventListener('click', () => startDemoReplay('/static/demo_samples/urban_ambient_demo.wav', 'Ambient Demo'));
    }
    if (demoCustomFileBtn && demoCustomFileInput) {
        demoCustomFileBtn.addEventListener('click', () => demoCustomFileInput.click());
        demoCustomFileInput.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                const file = e.target.files[0];
                const fileUrl = URL.createObjectURL(file);
                startDemoReplay(fileUrl, file.name);
            }
        });
    }
    if (stopDemoReplayBtn) {
        stopDemoReplayBtn.addEventListener('click', stopDemoReplay);
    }
}

async function startDemoReplay(audioUrl, label) {
    stopDemoReplay();
    if (isLiveListening) {
        stopContinuousListening();
    }

    const statusEl = document.getElementById('demoReplayStatus');
    const stopBtn = document.getElementById('stopDemoReplayBtn');
    if (statusEl) {
        statusEl.style.display = 'block';
        statusEl.textContent = `Loading ${label}...`;
    }
    if (stopBtn) stopBtn.style.display = 'inline-block';

    try {
        const resp = await fetch(audioUrl);
        const ab = await resp.arrayBuffer();
        const ctx = new (window.AudioContext || window.webkitAudioContext)();
        const decoded = await ctx.decodeAudioData(ab);

        // Convert to mono Float32 at 16 kHz
        let mono16k;
        if (decoded.sampleRate === 16000) {
            mono16k = decoded.getChannelData(0);
        } else {
            mono16k = downsampleTo16kHz(decoded.getChannelData(0), decoded.sampleRate, 16000);
        }

        // Reset server session stream
        const fd = new FormData();
        fd.append('session_id', clientSessionId);
        await fetch('/api/stream/reset', { method: 'POST', body: fd }).catch(() => {});

        isDemoReplaying = true;
        let offset = 0;
        const chunkSize = 7680; // 0.48s at 16 kHz
        const totalChunks = Math.ceil(mono16k.length / chunkSize);
        let chunkIndex = 0;

        liveStatusDot.className = 'status-dot listening';
        liveStatusText.textContent = `REPLAYING: ${label}`;

        demoReplayInterval = setInterval(async () => {
            if (!isDemoReplaying || offset >= mono16k.length) {
                stopDemoReplay();
                if (statusEl) statusEl.textContent = `Completed replay of ${label}.`;
                return;
            }

            const chunk = mono16k.slice(offset, offset + chunkSize);
            offset += chunkSize;
            chunkIndex++;

            // Update VU meter simulation
            let sumSq = 0;
            for (let i = 0; i < chunk.length; i++) sumSq += chunk[i] * chunk[i];
            const rms = Math.sqrt(sumSq / chunk.length);
            const db = 20 * Math.log10(Math.max(rms, 0.0001));
            const meterPct = Math.min(100, Math.max(0, ((db + 60) / 60) * 100));
            micMeterFill.style.width = `${meterPct.toFixed(1)}%`;
            micRmsDisplay.textContent = `${db.toFixed(1)} dB`;

            if (statusEl) {
                statusEl.textContent = `Streaming ${label}: chunk ${chunkIndex}/${totalChunks} (${(offset / 16000).toFixed(1)}s / ${(mono16k.length / 16000).toFixed(1)}s)`;
            }

            // Append chunk to audio buffer for window processing
            appendAudioSamples(chunk);
        }, 480);

    } catch (err) {
        console.error('Demo replay error:', err);
        if (statusEl) statusEl.textContent = `Replay error: ${err.message}`;
        stopDemoReplay();
    }
}

function stopDemoReplay() {
    isDemoReplaying = false;
    if (demoReplayInterval) {
        clearInterval(demoReplayInterval);
        demoReplayInterval = null;
    }
    const stopBtn = document.getElementById('stopDemoReplayBtn');
    if (stopBtn) stopBtn.style.display = 'none';
    liveStatusDot.className = 'status-dot standby';
    liveStatusText.textContent = 'Standby (Ready to Listen)';
}

// ==========================================
// 5. V10 DEDICATED LIVE MICROPHONE TEST PANEL
// ==========================================
let v10AudioContext = null;
let v10Stream = null;
let v10Source = null;
let v10Processor = null;
let isV10Listening = false;
let v10StartTime = 0;
let v10TimerInterval = null;
let v10Buffer16k = new Float32Array(0);
let isV10Processing = false;
let v10ProcessedCount = 0;
let v10DroppedCount = 0;
let v10EventsCount = 0;
let v10SessionId = 'v10_session_' + Math.random().toString(36).substring(2, 10) + '_' + Date.now();

function initV10LivePanel() {
    const v10StartBtn = document.getElementById('v10StartBtn');
    const v10StopBtn = document.getElementById('v10StopBtn');
    const v10ResetBtn = document.getElementById('v10ResetBtn');
    const v10ClearBtn = document.getElementById('v10ClearBtn');
    const v10AudioDeviceSelect = document.getElementById('v10AudioDeviceSelect');

    if (v10StartBtn) v10StartBtn.addEventListener('click', startV10Streaming);
    if (v10StopBtn) v10StopBtn.addEventListener('click', stopV10Streaming);
    if (v10ResetBtn) v10ResetBtn.addEventListener('click', resetV10Session);
    if (v10ClearBtn) v10ClearBtn.addEventListener('click', clearV10History);

    if (v10AudioDeviceSelect) {
        v10AudioDeviceSelect.addEventListener('change', async () => {
            if (isV10Listening) {
                logV10('[DEVICE] Audio device changed during streaming. Reconnecting...');
                stopV10Streaming();
                setTimeout(startV10Streaming, 300);
            }
        });
    }

    populateV10AudioDevices();
}

function logV10(msg) {
    const logEl = document.getElementById('v10LogConsole');
    if (!logEl) return;
    const now = new Date();
    const ts = now.toTimeString().split(' ')[0] + '.' + String(now.getMilliseconds()).padStart(3, '0');
    const line = document.createElement('div');
    line.textContent = `[${ts}] ${msg}`;
    logEl.appendChild(line);
    logEl.scrollTop = logEl.scrollHeight;
}

async function populateV10AudioDevices() {
    const select = document.getElementById('v10AudioDeviceSelect');
    if (!select || !navigator.mediaDevices || !navigator.mediaDevices.enumerateDevices) return;
    try {
        const devices = await navigator.mediaDevices.enumerateDevices();
        const audioInputs = devices.filter(d => d.kind === 'audioinput');
        const curVal = select.value;
        select.innerHTML = '<option value="">Default System Microphone</option>';
        audioInputs.forEach((d, i) => {
            if (d.deviceId && d.deviceId !== 'default' && d.deviceId !== '') {
                const opt = document.createElement('option');
                opt.value = d.deviceId;
                opt.textContent = d.label || `Microphone ${i + 1}`;
                if (d.deviceId === curVal) opt.selected = true;
                select.appendChild(opt);
            }
        });
    } catch (e) {
        console.warn('Could not populate V10 audio devices:', e);
    }
}

async function startV10Streaming() {
    if (isV10Listening) return;

    const v10StartBtn = document.getElementById('v10StartBtn');
    const v10StopBtn = document.getElementById('v10StopBtn');
    const v10StatusDot = document.getElementById('v10StatusDot');
    const v10ConnectionBadge = document.getElementById('v10ConnectionBadge');
    const v10AudioDeviceSelect = document.getElementById('v10AudioDeviceSelect');

    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        logV10('[ERROR] getUserMedia is not supported in this environment.');
        return;
    }

    try {
        const selectedId = v10AudioDeviceSelect ? v10AudioDeviceSelect.value : '';
        const constraints = {
            audio: selectedId ? { deviceId: { exact: selectedId }, echoCancellation: false, noiseSuppression: false, autoGainControl: false }
                              : { echoCancellation: false, noiseSuppression: false, autoGainControl: false }
        };

        logV10(`[SETUP] Requesting microphone access (ID: ${selectedId || 'default'})...`);
        try {
            v10Stream = await navigator.mediaDevices.getUserMedia(constraints);
        } catch (strictErr) {
            logV10('[WARN] Exact device constraints failed. Falling back to default audio stream.');
            v10Stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        }

        populateV10AudioDevices();

        const track = v10Stream.getAudioTracks()[0];
        logV10(`[AUDIO] Connected: ${track.label || 'Microphone Track'}`);

        v10AudioContext = new (window.AudioContext || window.webkitAudioContext)({ sampleRate: 44100 });
        if (v10AudioContext.state === 'suspended') {
            await v10AudioContext.resume();
        }

        v10Source = v10AudioContext.createMediaStreamSource(v10Stream);
        v10Processor = v10AudioContext.createScriptProcessor(4096, 1, 1);
        v10Source.connect(v10Processor);
        v10Processor.connect(v10AudioContext.destination);

        v10Buffer16k = new Float32Array(0);
        isV10Listening = true;
        v10StartTime = Date.now();

        if (v10StartBtn) v10StartBtn.disabled = true;
        if (v10StopBtn) v10StopBtn.disabled = false;
        if (v10StatusDot) v10StatusDot.className = 'status-dot listening';
        if (v10ConnectionBadge) {
            v10ConnectionBadge.textContent = 'Streaming (Active)';
            v10ConnectionBadge.style.color = '#10b981';
        }

        v10TimerInterval = setInterval(updateV10Timer, 1000);
        logV10(`[STREAM] Streaming to /api/stream_window with detector_improvement_v10 (Session: ${v10SessionId}).`);

        v10Processor.onaudioprocess = (e) => {
            if (!isV10Listening) return;
            const input = e.inputBuffer.getChannelData(0);

            // Compute RMS for VU meter
            let sum = 0;
            for (let i = 0; i < input.length; i++) sum += input[i] * input[i];
            const rms = Math.sqrt(sum / input.length);
            const db = 20 * Math.log10(Math.max(rms, 0.00001));
            updateV10Meter(db);

            // Resample to 16,000 Hz mono
            const resampled = downsampleTo16kHz(input, v10AudioContext.sampleRate, 16000);

            // Append to buffer
            const comb = new Float32Array(v10Buffer16k.length + resampled.length);
            comb.set(v10Buffer16k);
            comb.set(resampled, v10Buffer16k.length);
            v10Buffer16k = comb;

            // Window accumulation (0.96s window = 15360 samples, 0.48s hop = 7680 samples)
            if (v10Buffer16k.length >= 15360) {
                if (isV10Processing) {
                    v10DroppedCount++;
                    const dropEl = document.getElementById('v10DroppedCount');
                    if (dropEl) dropEl.textContent = String(v10DroppedCount);
                    if (v10DroppedCount % 5 === 0) {
                        logV10(`[WARN] Dropped ${v10DroppedCount} windows due to processing latency backpressure.`);
                    }
                    v10Buffer16k = v10Buffer16k.slice(7680);
                } else {
                    const chunkToProcess = v10Buffer16k.slice(0, 15360);
                    v10Buffer16k = v10Buffer16k.slice(7680);
                    sendV10Window(chunkToProcess);
                }
            }
        };

    } catch (err) {
        logV10(`[ERROR] Failed to start microphone: ${err.message || err.name}`);
        stopV10Streaming();
    }
}

function updateV10Meter(db) {
    const rmsEl = document.getElementById('v10RmsDisplay');
    const fillEl = document.getElementById('v10MeterFill');
    if (rmsEl) rmsEl.textContent = `${db.toFixed(1)} dBFS`;
    if (fillEl) {
        const pct = Math.min(100, Math.max(0, ((db + 60) / 60) * 100));
        fillEl.style.width = `${pct.toFixed(1)}%`;
    }
}

function updateV10Timer() {
    const timerEl = document.getElementById('v10SessionTimer');
    if (!timerEl) return;
    const elapsed = Math.floor((Date.now() - v10StartTime) / 1000);
    const h = String(Math.floor(elapsed / 3600)).padStart(2, '0');
    const m = String(Math.floor((elapsed % 3600) / 60)).padStart(2, '0');
    const s = String(elapsed % 60).padStart(2, '0');
    timerEl.textContent = `${h}:${m}:${s}`;
}

async function sendV10Window(samples) {
    isV10Processing = true;
    try {
        const wavBlob = float32ToWavBlob(samples, 16000);
        const fd = new FormData();
        fd.append('audio', wavBlob, 'v10_chunk.wav');
        fd.append('session_id', v10SessionId);
        fd.append('detector_version', 'detector_improvement_v10');
        fd.append('profile', 'balanced');

        const t0 = performance.now();
        const res = await fetch('/api/stream_window', {
            method: 'POST',
            body: fd
        });

        const roundTripMs = Math.round(performance.now() - t0);

        if (!res.ok) {
            logV10(`[HTTP ${res.status}] stream_window returned error.`);
            return;
        }

        const data = await res.json();
        v10ProcessedCount++;
        const procEl = document.getElementById('v10ProcessedCount');
        if (procEl) procEl.textContent = String(v10ProcessedCount);

        const latEl = document.getElementById('v10LatencyDisplay');
        if (latEl) latEl.textContent = `${data.latency_ms || roundTripMs} ms`;

        const scoreEl = document.getElementById('v10ScoreDisplay');
        if (scoreEl) scoreEl.textContent = (data.score || 0.0).toFixed(4);

        const crestEl = document.getElementById('v10CrestDisplay');
        if (crestEl) crestEl.textContent = `${data.crest_factor_db || 0.0} dB`;

        // Update FSM state badge
        updateV10FsmState(data);

        // Record Confirmed Alerts
        if (data.new_alerts && data.new_alerts.length > 0) {
            data.new_alerts.forEach(a => recordV10Alert(a));
        }

    } catch (e) {
        logV10(`[NET ERROR] ${e.message}`);
    } finally {
        isV10Processing = false;
    }
}

function updateV10FsmState(data) {
    const badge = document.getElementById('v10FsmStateBadge');
    if (!badge) return;

    if (data.in_event || data.is_gunshot) {
        badge.textContent = 'CONFIRMED';
        badge.style.color = '#ef4444';
    } else if (data.cooldown_until && data.cooldown_until > 0) {
        badge.textContent = 'REFRACTORY_COOLDOWN';
        badge.style.color = '#a78bfa';
    } else if (data.score >= 0.65) {
        badge.textContent = 'SUSPECTED';
        badge.style.color = '#f59e0b';
    } else {
        badge.textContent = 'IDLE';
        badge.style.color = '#10b981';
    }
}

function recordV10Alert(alert) {
    v10EventsCount++;
    const tbody = document.getElementById('v10EventsTableBody');
    const noEvents = document.getElementById('v10NoEventsRow');
    if (noEvents) noEvents.style.display = 'none';

    const now = new Date();
    const ts = now.toTimeString().split(' ')[0];

    const row = document.createElement('tr');
    row.style.background = 'rgba(239, 68, 68, 0.15)';
    row.innerHTML = `
        <td style="font-weight: 700; color: #f87171;">#${v10EventsCount}</td>
        <td style="font-family: 'JetBrains Mono', monospace;">${ts}</td>
        <td style="font-family: 'JetBrains Mono', monospace; font-weight: 700; color: #ef4444;">${(alert.score || 0.0).toFixed(4)}</td>
        <td style="font-family: 'JetBrains Mono', monospace;">${alert.crest_factor_db || '--'} dB</td>
        <td><span class="badge-danger" style="font-size: 11px; padding: 2px 8px;">CONFIRMED</span></td>
    `;

    if (tbody) tbody.insertBefore(row, tbody.firstChild);
    logV10(`[ALERT # ${v10EventsCount}] CONFIRMED GUNSHOT-LIKE EVENT! Score: ${(alert.score || 0.0).toFixed(4)}, Crest: ${alert.crest_factor_db || '--'} dB.`);
}

function stopV10Streaming() {
    isV10Listening = false;
    if (v10Stream) {
        v10Stream.getTracks().forEach(t => t.stop());
        v10Stream = null;
    }
    if (v10Processor) {
        v10Processor.disconnect();
        v10Processor = null;
    }
    if (v10Source) {
        v10Source.disconnect();
        v10Source = null;
    }
    if (v10AudioContext && v10AudioContext.state !== 'closed') {
        v10AudioContext.close();
        v10AudioContext = null;
    }

    clearInterval(v10TimerInterval);

    const v10StartBtn = document.getElementById('v10StartBtn');
    const v10StopBtn = document.getElementById('v10StopBtn');
    const v10StatusDot = document.getElementById('v10StatusDot');
    const v10ConnectionBadge = document.getElementById('v10ConnectionBadge');
    const fillEl = document.getElementById('v10MeterFill');
    const rmsEl = document.getElementById('v10RmsDisplay');

    if (v10StartBtn) v10StartBtn.disabled = false;
    if (v10StopBtn) v10StopBtn.disabled = true;
    if (v10StatusDot) v10StatusDot.className = 'status-dot standby';
    if (v10ConnectionBadge) {
        v10ConnectionBadge.textContent = 'Disconnected';
        v10ConnectionBadge.style.color = '#94a3b8';
    }
    if (fillEl) fillEl.style.width = '0%';
    if (rmsEl) rmsEl.textContent = '-99.0 dBFS';

    // Flush backend detector session
    const fd = new FormData();
    fd.append('session_id', v10SessionId);
    fetch('/api/stream/reset', { method: 'POST', body: fd }).catch(() => {});

    logV10('[STREAM] Microphone disconnected and stream stopped.');
}

function resetV10Session() {
    if (isV10Listening) stopV10Streaming();
    v10ProcessedCount = 0;
    v10DroppedCount = 0;
    const procEl = document.getElementById('v10ProcessedCount');
    const dropEl = document.getElementById('v10DroppedCount');
    const latEl = document.getElementById('v10LatencyDisplay');
    const scoreEl = document.getElementById('v10ScoreDisplay');
    const crestEl = document.getElementById('v10CrestDisplay');
    const timerEl = document.getElementById('v10SessionTimer');
    const badge = document.getElementById('v10FsmStateBadge');

    if (procEl) procEl.textContent = '0';
    if (dropEl) dropEl.textContent = '0';
    if (latEl) latEl.textContent = '-- ms';
    if (scoreEl) scoreEl.textContent = '0.0000';
    if (crestEl) crestEl.textContent = '-- dB';
    if (timerEl) timerEl.textContent = '00:00:00';
    if (badge) {
        badge.textContent = 'IDLE';
        badge.style.color = '#10b981';
    }

    v10SessionId = 'v10_session_' + Math.random().toString(36).substring(2, 10) + '_' + Date.now();
    const fd = new FormData();
    fd.append('session_id', v10SessionId);
    fetch('/api/stream/reset', { method: 'POST', body: fd }).catch(() => {});

    logV10(`[SYSTEM] Session reset. New session ID: ${v10SessionId}`);
}

function clearV10History() {
    v10EventsCount = 0;
    const tbody = document.getElementById('v10EventsTableBody');
    if (tbody) {
        tbody.innerHTML = `
            <tr id="v10NoEventsRow">
                <td colspan="5" style="text-align: center; color: var(--text-muted); padding: 16px;">
                    No confirmed acoustic events recorded in this session.
                </td>
            </tr>
        `;
    }
    logV10('[SYSTEM] Event history table cleared.');
}
