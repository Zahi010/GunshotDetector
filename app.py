"""
Flask Web Application for Gunshot Sound Detection (Phase 11 End-to-End Integration).

Architecture:
- YAMNet 1024-d backbone feature extraction
- Phase 9 Four-Model Stacking Ensemble (CatBoost, LightGBM, XGBoost, Keras MLP)
- RealTimeStreamDetector: Continuous ring-buffer streaming state machine
- Multi-Category Semantic Suppression (Thunder, Fireworks, Barking, Crackling Fire, Sirens)
- Physical Crest-Factor Guard Floor (>= 9.5 dB)
- Three Calibrated Operating Profiles: balanced, high_precision, high_sensitivity
- Thread-safe session management for concurrent browser client isolation
- Opt-in alert audio retention (privacy by default)

MANDATORY SAFETY NOTICE:
RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY.
This system is an experimental research prototype and must NEVER be relied upon
for life safety, fire protection, or automated emergency response.
"""

import os
import io
import time
import datetime
import tempfile
import threading
import traceback
from pathlib import Path
from typing import Dict, Tuple, Optional, Any

from flask import Flask, request, jsonify, render_template, send_from_directory
from werkzeug.utils import secure_filename
import numpy as np
import soundfile as sf
import librosa

import config
from dataset import load_audio_mono_16k
from model_phase9 import Phase9AdaptiveGunshotDetector
from scripts.validate_streaming_harness import RealTimeStreamDetector
from model_phase13 import Phase13CandidateGunshotDetector, RealTimeStreamDetectorPhase13
from model_phase14 import Phase14CandidateGunshotDetector, RealTimeStreamDetectorPhase14
from model_phase17 import Phase17ExperimentalGunshotDetector, RealTimeStreamDetectorPhase17
from experiments.detector_improvement_v1.model_detector_improvement_v1 import (
    DetectorImprovementV1,
    RealTimeStreamDetectorImprovementV1
)
from experiments.detector_improvement_v2.model_detector_improvement_v2 import (
    DetectorImprovementV2,
    RealTimeStreamDetectorImprovementV2
)

SAFETY_DESIGNATION = "RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY"

app = Flask(__name__, static_folder="static", template_folder="templates")
app.config["MAX_CONTENT_LENGTH"] = config.MAX_CONTENT_LENGTH

# Global Detector Cache & Session State: key = (version, profile)
DETECTOR_CACHE: Dict[Tuple[str, str], Any] = {}
SESSION_STREAM_DETECTORS: Dict[str, Tuple[Any, float, str, str]] = {}
SESSION_LOCK = threading.Lock()
DETECTOR_LOCK = threading.Lock()
MODEL_LOAD_ERROR: Optional[str] = None


def get_detector(version: str = "phase14", profile: str = "balanced") -> Optional[Any]:
    """Retrieve or lazily instantiate requested detector version and profile."""
    global MODEL_LOAD_ERROR
    valid_versions = [
        "phase9", "phase13", "phase14", "phase17",
        "detector_improvement_v1", "v1", "detector_improvement_v2", "v2",
        "detector_improvement_v5", "v5", "detector_improvement_v6", "v6",
        "detector_improvement_v7", "v7", "detector_improvement_v8", "v8",
        "detector_improvement_v9", "v9", "detector_improvement_v10", "v10"
    ]
    version = version.lower() if version in valid_versions else "phase14"
    valid_profiles = [
        "balanced", "high_precision", "high_sensitivity",
        "balanced_animal_suppressed", "high_precision_animal_suppressed",
        "high_sensitivity_animal_suppressed", "experimental_animal_suppression"
    ]
    profile = profile if profile in valid_profiles else "balanced"
    key = (version, profile)
    
    with DETECTOR_LOCK:
        if key not in DETECTOR_CACHE:
            bundle_path = config.MODELS_DIR / "gunshot_yamnet_bundle"
            if not (bundle_path / "classifier_head.keras").exists():
                MODEL_LOAD_ERROR = (
                    f"Model bundle not found at {bundle_path}. "
                    "Ensure Phase 9 model bundle is present."
                )
                return None
            try:
                if version in ["detector_improvement_v10", "v10"]:
                    from experiments.detector_improvement_v10.model_detector_improvement_v10 import DetectorImprovementV10
                    DETECTOR_CACHE[key] = DetectorImprovementV10()
                elif version in ["detector_improvement_v9", "v9"]:
                    from experiments.detector_improvement_v9.model_detector_improvement_v9 import DetectorImprovementV9
                    DETECTOR_CACHE[key] = DetectorImprovementV9()
                elif version in ["detector_improvement_v8", "v8"]:
                    from experiments.detector_improvement_v8.model_detector_improvement_v8 import DetectorImprovementV8
                    DETECTOR_CACHE[key] = DetectorImprovementV8()
                elif version in ["detector_improvement_v7", "v7"]:
                    from experiments.detector_improvement_v7.model_detector_improvement_v7 import DetectorImprovementV7
                    DETECTOR_CACHE[key] = DetectorImprovementV7()
                elif version in ["detector_improvement_v6", "v6"]:
                    from experiments.detector_improvement_v6.model_detector_improvement_v6 import DetectorImprovementV6
                    DETECTOR_CACHE[key] = DetectorImprovementV6()
                elif version in ["detector_improvement_v5", "v5"]:
                    from experiments.detector_improvement_v5.model_detector_improvement_v5 import DetectorImprovementV5
                    DETECTOR_CACHE[key] = DetectorImprovementV5()
                elif version in ["detector_improvement_v2", "v2"]:
                    DETECTOR_CACHE[key] = DetectorImprovementV2(
                        bundle_dir=bundle_path,
                        profile=profile
                    )
                elif version in ["detector_improvement_v1", "v1"]:
                    DETECTOR_CACHE[key] = DetectorImprovementV1(
                        bundle_dir=bundle_path,
                        profile=profile
                    )
                elif version == "phase17":
                    DETECTOR_CACHE[key] = Phase17ExperimentalGunshotDetector(
                        bundle_dir=bundle_path,
                        profile=profile
                    )
                elif version == "phase14":
                    DETECTOR_CACHE[key] = Phase14CandidateGunshotDetector(
                        bundle_dir=bundle_path,
                        profile=profile
                    )
                elif version == "phase13":
                    DETECTOR_CACHE[key] = Phase13CandidateGunshotDetector(
                        bundle_dir=bundle_path,
                        profile=profile
                    )
                else:
                    DETECTOR_CACHE[key] = Phase9AdaptiveGunshotDetector(
                        bundle_dir=bundle_path,
                        profile=profile
                    )
            except Exception as e:
                MODEL_LOAD_ERROR = f"Error loading {version} model: {str(e)}"
                traceback.print_exc()
                return None
        return DETECTOR_CACHE[key]


def get_phase9_detector(profile: str = "balanced") -> Optional[Phase9AdaptiveGunshotDetector]:
    """Backwards compatible getter for Phase 9 detector."""
    return get_detector("phase9", profile)


def get_session_stream_detector(session_id: str, version: str = "phase14", profile: str = "balanced") -> Any:
    """Retrieve or create a stateful streaming detector instance for the given session."""
    now = time.time()
    valid_versions = [
        "phase9", "phase13", "phase14", "phase17",
        "detector_improvement_v1", "v1", "detector_improvement_v2", "v2",
        "detector_improvement_v5", "v5", "detector_improvement_v6", "v6",
        "detector_improvement_v7", "v7", "detector_improvement_v8", "v8",
        "detector_improvement_v9", "v9", "detector_improvement_v10", "v10"
    ]
    version = version.lower() if version in valid_versions else "phase14"
    valid_profiles = [
        "balanced", "high_precision", "high_sensitivity",
        "balanced_animal_suppressed", "high_precision_animal_suppressed",
        "high_sensitivity_animal_suppressed", "experimental_animal_suppression"
    ]
    profile = profile if profile in valid_profiles else "balanced"

    with SESSION_LOCK:
        # Prune sessions older than 15 minutes
        expired = [sid for sid, (_, last_seen, _, _) in SESSION_STREAM_DETECTORS.items() if now - last_seen > 900.0]
        for sid in expired:
            del SESSION_STREAM_DETECTORS[sid]

        if session_id in SESSION_STREAM_DETECTORS:
            detector, _, cur_ver, cur_prof = SESSION_STREAM_DETECTORS[session_id]
            # If version or profile changed, reinitialize for this session
            if cur_ver != version or cur_prof != profile:
                if version in ["detector_improvement_v10", "v10"]:
                    from experiments.detector_improvement_v10.model_detector_improvement_v10 import (
                        DetectorImprovementV10, RealTimeStreamDetectorImprovementV10
                    )
                    detector = RealTimeStreamDetectorImprovementV10()
                elif version in ["detector_improvement_v9", "v9"]:
                    from scratch.run_full_v9_evaluation import DetectorImprovementV9
                    detector = DetectorImprovementV9()
                elif version in ["detector_improvement_v8", "v8"]:
                    from experiments.detector_improvement_v8.model_detector_improvement_v8 import (
                        DetectorImprovementV8, RealTimeStreamDetectorImprovementV8
                    )
                    detector = RealTimeStreamDetectorImprovementV8()
                elif version in ["detector_improvement_v7", "v7"]:
                    from experiments.detector_improvement_v7.model_detector_improvement_v7 import DetectorImprovementV7
                    detector = DetectorImprovementV7()
                elif version in ["detector_improvement_v6", "v6"]:
                    from experiments.detector_improvement_v6.model_detector_improvement_v6 import DetectorImprovementV6
                    detector = DetectorImprovementV6()
                elif version in ["detector_improvement_v5", "v5"]:
                    from experiments.detector_improvement_v5.model_detector_improvement_v5 import DetectorImprovementV5
                    detector = DetectorImprovementV5()
                elif version in ["detector_improvement_v2", "v2"]:
                    detector = RealTimeStreamDetectorImprovementV2(profile=profile)
                elif version in ["detector_improvement_v1", "v1"]:
                    detector = RealTimeStreamDetectorImprovementV1(profile=profile)
                elif version == "phase17":
                    detector = RealTimeStreamDetectorPhase17(profile=profile)
                elif version == "phase14":
                    detector = RealTimeStreamDetectorPhase14(profile=profile)
                elif version == "phase13":
                    detector = RealTimeStreamDetectorPhase13(profile=profile)
                else:
                    detector = RealTimeStreamDetector(profile=profile)
            SESSION_STREAM_DETECTORS[session_id] = (detector, now, version, profile)
            return detector

        # Create new session detector
        if version in ["detector_improvement_v10", "v10"]:
            from experiments.detector_improvement_v10.model_detector_improvement_v10 import (
                DetectorImprovementV10, RealTimeStreamDetectorImprovementV10
            )
            detector = RealTimeStreamDetectorImprovementV10()
        elif version in ["detector_improvement_v9", "v9"]:
            from scratch.run_full_v9_evaluation import DetectorImprovementV9
            detector = DetectorImprovementV9()
        elif version in ["detector_improvement_v8", "v8"]:
            from experiments.detector_improvement_v8.model_detector_improvement_v8 import (
                DetectorImprovementV8, RealTimeStreamDetectorImprovementV8
            )
            detector = RealTimeStreamDetectorImprovementV8()
        elif version in ["detector_improvement_v7", "v7"]:
            from experiments.detector_improvement_v7.model_detector_improvement_v7 import DetectorImprovementV7
            detector = DetectorImprovementV7()
        elif version in ["detector_improvement_v6", "v6"]:
            from experiments.detector_improvement_v6.model_detector_improvement_v6 import DetectorImprovementV6
            detector = DetectorImprovementV6()
        elif version in ["detector_improvement_v5", "v5"]:
            from experiments.detector_improvement_v5.model_detector_improvement_v5 import DetectorImprovementV5
            detector = DetectorImprovementV5()
        elif version in ["detector_improvement_v2", "v2"]:
            detector = RealTimeStreamDetectorImprovementV2(profile=profile)
        elif version in ["detector_improvement_v1", "v1"]:
            detector = RealTimeStreamDetectorImprovementV1(profile=profile)
        elif version == "phase17":
            detector = RealTimeStreamDetectorPhase17(profile=profile)
        elif version == "phase14":
            detector = RealTimeStreamDetectorPhase14(profile=profile)
        elif version == "phase13":
            detector = RealTimeStreamDetectorPhase13(profile=profile)
        else:
            detector = RealTimeStreamDetector(profile=profile)
        SESSION_STREAM_DETECTORS[session_id] = (detector, now, version, profile)
        return detector


def decode_audio_bytes_to_mono_16k(audio_bytes: bytes, filename: str = "audio.wav") -> np.ndarray:
    """Decode audio bytes to 16 kHz mono Float32 numpy array, using memory first with disk fallback."""
    # Try in-memory soundfile decode
    try:
        data, sr = sf.read(io.BytesIO(audio_bytes), dtype="float32")
        if data.ndim > 1:
            data = np.mean(data, axis=1)
        if sr != config.SAMPLE_RATE:
            data = librosa.resample(data, orig_sr=sr, target_sr=config.SAMPLE_RATE)
        return data.astype(np.float32)
    except Exception:
        pass

    # Disk fallback via load_audio_mono_16k
    suffix = Path(filename).suffix.lower() or ".wav"
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        tmp.write(audio_bytes)
        tmp_path = Path(tmp.name)
    try:
        return load_audio_mono_16k(tmp_path)
    except Exception:
        # Return empty array for unparseable / corrupt audio chunks
        return np.zeros(0, dtype=np.float32)
    finally:
        if tmp_path.exists():
            try:
                os.remove(tmp_path)
            except Exception:
                pass


@app.route("/")
def index():
    """Render main application interface."""
    det = get_phase9_detector("balanced")
    status_info = {
        "model_loaded": det is not None,
        "load_error": MODEL_LOAD_ERROR,
        "safety_designation": SAFETY_DESIGNATION,
        "active_profile": "balanced",
        "profiles": Phase9AdaptiveGunshotDetector.PROFILES,
        "default_threshold": det.threshold_base if det else 0.75,
        "threshold_high": det.threshold_high if det else 0.88,
        "cooldown_secs": det.cooldown_secs if det else 2.0,
        "min_crest_factor_db": det.min_crest_factor_db if det else 9.5
    }
    return render_template("index.html", status=status_info)


IMPROVEMENT_V1_PROFILES = {
    "balanced": {
        "threshold_base": 0.75,
        "threshold_high": 0.88,
        "threshold_off": 0.48,
        "confirm_windows": 2,
        "cooldown_secs": 2.0,
        "min_crest_factor_db": 8.8,
        "single_win_min_crest_db": 12.0,
        "description": "Recommended Baseline: 4-State Refractory FSM + Calibrated Semantic Suppression"
    },
    "high_precision": {
        "threshold_base": 0.80,
        "threshold_high": 0.90,
        "threshold_off": 0.52,
        "confirm_windows": 2,
        "cooldown_secs": 2.5,
        "min_crest_factor_db": 9.5,
        "single_win_min_crest_db": 13.0,
        "description": "Ultra-Low False Alarms: 3.56 alerts/hr on continuous audio"
    },
    "high_sensitivity": {
        "threshold_base": 0.70,
        "threshold_high": 0.85,
        "threshold_off": 0.42,
        "confirm_windows": 2,
        "cooldown_secs": 1.5,
        "min_crest_factor_db": 8.0,
        "single_win_min_crest_db": 11.0,
        "description": "High Recall: 69.17% gunshot detection rate"
    }
}

IMPROVEMENT_V2_PROFILES = {
    "balanced": {
        "threshold_base": 0.75,
        "threshold_high": 0.88,
        "threshold_off": 0.48,
        "confirm_windows": 2,
        "cooldown_secs": 2.0,
        "min_crest_factor_db": 8.8,
        "single_win_min_crest_db": 12.0,
        "allow_single_impulse_exception": True,
        "single_impulse_min_score": 0.82,
        "single_impulse_min_crest_db": 14.0,
        "description": "Recommended Experimental: Coherence Guard + Refined Pyrotechnic Gating + Single Impulse Exception"
    },
    "high_precision": {
        "threshold_base": 0.80,
        "threshold_high": 0.90,
        "threshold_off": 0.52,
        "confirm_windows": 2,
        "cooldown_secs": 2.5,
        "min_crest_factor_db": 9.5,
        "single_win_min_crest_db": 13.0,
        "allow_single_impulse_exception": False,
        "single_impulse_min_score": 0.85,
        "single_impulse_min_crest_db": 15.0,
        "description": "Ultra-Low False Alarms: Zero alerts on continuous urban wind/ambient"
    },
    "high_sensitivity": {
        "threshold_base": 0.70,
        "threshold_high": 0.85,
        "threshold_off": 0.42,
        "confirm_windows": 2,
        "cooldown_secs": 1.5,
        "min_crest_factor_db": 8.0,
        "single_win_min_crest_db": 11.0,
        "allow_single_impulse_exception": True,
        "single_impulse_min_score": 0.78,
        "single_impulse_min_crest_db": 13.0,
        "description": "High Recall: Single impulse capture with crest factor floor >= 13 dB"
    }
}


@app.route("/api/status", methods=["GET"])
def api_status():
    """Return model status, Phase 9/14/17 architecture, and operating profiles."""
    det = get_detector("phase14", "balanced")
    if det is None:
        det = get_phase9_detector("balanced")
    if det is None:
        return jsonify({
            "status": "error",
            "model_loaded": False,
            "error": MODEL_LOAD_ERROR,
            "safety_designation": SAFETY_DESIGNATION
        }), 503

    return jsonify({
        "status": "ok",
        "model_loaded": True,
        "safety_designation": SAFETY_DESIGNATION,
        "default_version": "phase14",
        "supported_versions": ["phase9", "phase13", "phase14", "phase17", "detector_improvement_v1", "detector_improvement_v2", "detector_improvement_v5", "detector_improvement_v6", "detector_improvement_v7", "detector_improvement_v8"],
        "experimental_versions": ["phase17", "detector_improvement_v1", "detector_improvement_v2", "detector_improvement_v5", "detector_improvement_v6", "detector_improvement_v7", "detector_improvement_v8"],
        "architecture": {
            "backbone": "Google YAMNet (1024-d acoustic embeddings)",
            "ensemble_models": ["CatBoost", "LightGBM", "XGBoost", "Keras_MLP"],
            "semantic_suppression_categories": [
                "coherence_safeguard", "thunder", "fireworks_dominant", "fireworks_standard", "wind_buffeting", "mechanical_impact", "barking", "crackling_fire", "sirens"
            ],
            "operating_profiles": Phase9AdaptiveGunshotDetector.PROFILES,
            "phase14_profiles": Phase14CandidateGunshotDetector.PROFILES,
            "phase17_profiles": Phase17ExperimentalGunshotDetector.PROFILES,
            "detector_improvement_v1_profiles": IMPROVEMENT_V1_PROFILES,
            "detector_improvement_v2_profiles": IMPROVEMENT_V2_PROFILES
        },
        "default_profile": "balanced",
        "current_threshold_base": det.threshold_base,
        "current_threshold_high": det.threshold_high,
        "crest_factor_floor_db": det.min_crest_factor_db,
        "disclaimer": (
            "RESEARCH DEMONSTRATION PROTOTYPE — NOT FOR LIFE SAFETY. "
            "Classification is driven by neural acoustic features and statistical consensus. "
            "Not certified for emergency 911 dispatch or life-critical applications."
        )
    })


@app.route("/api/health", methods=["GET"])
def api_health():
    """Service health and readiness check endpoint."""
    det = get_detector("phase14", "balanced")
    healthy = det is not None
    return jsonify({
        "status": "healthy" if healthy else "degraded",
        "model_loaded": healthy,
        "default_detector": "phase14",
        "default_profile": "balanced",
        "supported_detectors": ["phase9", "phase13", "phase14", "phase17", "detector_improvement_v1", "detector_improvement_v2", "detector_improvement_v5", "detector_improvement_v6", "detector_improvement_v7", "detector_improvement_v8", "detector_improvement_v9", "detector_improvement_v10"],
        "experimental_detectors": ["phase17", "detector_improvement_v1", "detector_improvement_v2", "detector_improvement_v5", "detector_improvement_v6", "detector_improvement_v7", "detector_improvement_v8", "detector_improvement_v9", "detector_improvement_v10"],
        "safety_designation": SAFETY_DESIGNATION,
        "timestamp": time.time()
    }), (200 if healthy else 503)


@app.route("/api/profiles", methods=["GET"])
def api_profiles():
    """Return available operating profiles and their parameters."""
    return jsonify({
        "status": "ok",
        "safety_designation": SAFETY_DESIGNATION,
        "profiles": Phase9AdaptiveGunshotDetector.PROFILES,
        "phase14_profiles": Phase14CandidateGunshotDetector.PROFILES,
        "phase17_profiles": Phase17ExperimentalGunshotDetector.PROFILES,
        "detector_improvement_v1_profiles": IMPROVEMENT_V1_PROFILES,
        "detector_improvement_v2_profiles": IMPROVEMENT_V2_PROFILES
    })


@app.route("/api/demo_samples", methods=["GET"])
def api_demo_samples():
    """Return pre-recorded audio demonstration samples for senior walkthrough."""
    samples = [
        {
            "id": "gunshot_positive",
            "name": "Authentic Gunshot (FSD50K Ballistic Transient)",
            "filename": "gunshot_positive_demo.wav",
            "url": "/static/demo_samples/gunshot_positive_demo.wav",
            "category": "positive",
            "expected_verdict": "Gunshot Alert",
            "description": "True positive impulse showing sharp onset and high crest factor (>15 dB)."
        },
        {
            "id": "fireworks_distractor",
            "name": "Fireworks / Pyrotechnic Challenge",
            "filename": "fireworks_distractor_demo.wav",
            "url": "/static/demo_samples/fireworks_distractor_demo.wav",
            "category": "distractor",
            "expected_verdict": "Suppressed (No Gunshot Alert)",
            "description": "Challenging aerial salute suppressed by Calibrated Semantic Suppression V1."
        },
        {
            "id": "urban_ambient",
            "name": "Urban Environmental Ambient Noise",
            "filename": "urban_ambient_demo.wav",
            "url": "/static/demo_samples/urban_ambient_demo.wav",
            "category": "ambient",
            "expected_verdict": "Clean Background",
            "description": "Typical ambient background audio with continuous non-ballistic noise."
        }
    ]
    return jsonify({
        "status": "ok",
        "safety_designation": SAFETY_DESIGNATION,
        "samples": samples
    })


@app.route("/api/detect", methods=["POST"])
def api_detect():
    """
    Run gunshot detection on uploaded audio file.
    Parameters:
        audio: multipart file upload
        profile: str ('balanced', 'high_precision', 'high_sensitivity', default: 'balanced')
        detector_version: str ('phase9', 'phase13', 'phase14', 'phase17', default: 'phase14')
    """
    profile = request.form.get("profile", "balanced")
    version = request.form.get("detector_version", "phase14")
    det = get_detector(version, profile)
    if det is None:
        return jsonify({
            "error": f"Model bundle for version '{version}' is not loaded.",
            "details": MODEL_LOAD_ERROR
        }), 503

    if "audio" not in request.files:
        return jsonify({"error": "No audio file provided in request (expected 'audio' field)."}), 400

    audio_file = request.files["audio"]
    if audio_file.filename == "":
        return jsonify({"error": "Empty filename provided."}), 400

    original_name = secure_filename(audio_file.filename) or "recording.wav"
    audio_bytes = audio_file.read()
    if len(audio_bytes) == 0:
        return jsonify({"error": "Empty audio file received (0 bytes)."}), 400

    try:
        waveform = decode_audio_bytes_to_mono_16k(audio_bytes, original_name)
    except Exception as decode_err:
        return jsonify({
            "error": "Failed to decode audio file. Format may be unsupported or corrupted.",
            "details": str(decode_err)
        }), 422

    if len(waveform) == 0:
        return jsonify({"error": "Audio contains 0 samples after decoding."}), 400

    try:
        t0 = time.time()
        # Evaluate using selected detector
        eval_result = det.evaluate_waveform(waveform)
        inference_latency_ms = round((time.time() - t0) * 1000.0, 1)

        eval_result["filename"] = original_name
        eval_result["profile"] = profile
        eval_result["detector_version"] = version
        eval_result["inference_latency_ms"] = inference_latency_ms
        eval_result["safety_designation"] = SAFETY_DESIGNATION

        # Preserve backward-compatible fields for UI
        eval_result["is_gunshot"] = eval_result.get("detected", eval_result.get("gunshot_detected", False))
        eval_result["threshold"] = det.threshold_base

        return jsonify(eval_result)

    except Exception as e:
        traceback.print_exc()
        return jsonify({
            "error": "Internal inference error.",
            "details": str(e)
        }), 500


@app.route("/api/stream_window", methods=["POST"])
@app.route("/api/stream/chunk", methods=["POST"])
def api_stream_window():
    """
    Real-time streaming window endpoint for continuous live microphone detection.
    Processes chunk via session-isolated streaming detector.
    Parameters:
        profile: str ('balanced', 'high_precision', 'high_sensitivity')
        detector_version: str ('phase9', 'phase13', 'phase14', 'phase17', default: 'phase14')
        session_id: str
    """
    profile = request.form.get("profile", "balanced")
    version = request.form.get("detector_version", "phase14")
    session_id = request.form.get("session_id") or request.headers.get("X-Session-ID") or "default_session"

    if "audio" not in request.files:
        return jsonify({"error": "No audio chunk provided"}), 400

    audio_file = request.files["audio"]
    audio_bytes = audio_file.read()
    if len(audio_bytes) == 0:
        return jsonify({
            "score": 0.0,
            "is_gunshot": False,
            "rms_db": -99.0,
            "crest_factor_db": 0.0,
            "latency_ms": 0.0,
            "new_alerts": []
        })

    try:
        t0 = time.time()
        waveform = decode_audio_bytes_to_mono_16k(audio_bytes, "chunk.wav")

        if len(waveform) == 0:
            return jsonify({
                "score": 0.0,
                "is_gunshot": False,
                "rms_db": -99.0,
                "crest_factor_db": 0.0,
                "latency_ms": 0.0,
                "new_alerts": []
            })

        rms = float(np.sqrt(np.mean(waveform ** 2) + 1e-12))
        rms_db = round(float(20 * np.log10(max(rms, 1e-6))), 1)

        # Retrieve session-isolated streaming detector for version
        stream_det = get_session_stream_detector(session_id, version, profile)
        new_alerts = stream_det.process_chunk(waveform, input_sample_rate=config.SAMPLE_RATE)
        latency_ms = round((time.time() - t0) * 1000.0, 1)

        latest_score = round(float(stream_det.last_score), 4)
        crest_factor_db = round(float(stream_det.last_crest_factor_db), 2)
        is_gunshot = bool(len(new_alerts) > 0 or stream_det.in_event)

        # Format alerts with human-readable timestamps and qualifier
        formatted_alerts = []
        for a in new_alerts:
            formatted_alerts.append({
                "alert_id": len(stream_det.detected_alerts),
                "timestamp_sec": a.get("start_time", 0.0),
                "end_sec": a.get("end_time", 0.0),
                "score": a.get("peak_score", latest_score),
                "crest_factor_db": a.get("crest_factor_db", crest_factor_db),
                "dispatch_path": a.get("dispatch_path", "temporal_consensus"),
                "event_type": "Gunshot-like acoustic event",
                "status": "Confirmed Acoustic Event"
            })

        return jsonify({
            "session_id": session_id,
            "profile": profile,
            "score": latest_score,
            "is_gunshot": is_gunshot,
            "rms_db": rms_db,
            "crest_factor_db": crest_factor_db,
            "threshold_base": stream_det.detector.threshold_base,
            "threshold_high": stream_det.detector.threshold_high,
            "cooldown_until": stream_det.cooldown_until,
            "in_event": stream_det.in_event,
            "new_alerts": formatted_alerts,
            "latency_ms": latency_ms,
            "safety_designation": SAFETY_DESIGNATION
        })

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route("/api/stream/reset", methods=["POST"])
def api_stream_reset():
    """Reset streaming state for the specified session."""
    session_id = None
    if request.form and "session_id" in request.form:
        session_id = request.form.get("session_id")
    elif request.is_json and request.json and "session_id" in request.json:
        session_id = request.json.get("session_id")
    elif "session_id" in request.args:
        session_id = request.args.get("session_id")

    if not session_id:
        session_id = request.headers.get("X-Session-ID", "default_session")

    with SESSION_LOCK:
        if session_id in SESSION_STREAM_DETECTORS:
            detector, _, cur_ver, cur_prof = SESSION_STREAM_DETECTORS[session_id]
            detector.reset()
            SESSION_STREAM_DETECTORS[session_id] = (detector, time.time(), cur_ver, cur_prof)

    return jsonify({
        "status": "ok",
        "session_id": session_id,
        "message": "Streaming state reset successfully."
    })


@app.route("/api/save_alert", methods=["POST"])
def api_save_alert():
    """
    Opt-in storage for confirmed gunshot alert audio clips.
    Saves audio clip to `saved_alerts/` directory.
    """
    if "audio" not in request.files:
        return jsonify({"error": "No audio file provided"}), 400

    audio_file = request.files["audio"]
    score = request.form.get("score", "0.0")
    profile = request.form.get("profile", "balanced")
    timestamp_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    out_name = f"gunshot_alert_{timestamp_str}_{profile}_score{float(score):.2f}.wav"
    out_path = config.SAVED_ALERTS_DIR / out_name

    try:
        audio_bytes = audio_file.read()
        wave = decode_audio_bytes_to_mono_16k(audio_bytes, "alert.wav")
        sf.write(str(out_path), wave, config.SAMPLE_RATE)
        return jsonify({
            "saved": True,
            "filename": out_name,
            "path": str(out_path),
            "message": f"Audio clip saved to {out_path}"
        })
    except Exception as e:
        return jsonify({"error": f"Failed to save alert: {str(e)}"}), 500


@app.route("/api/devices", methods=["GET"])
def api_devices():
    """Return list of native microphone devices available on host."""
    try:
        import sounddevice as sd
        devices = []
        for idx, d in enumerate(sd.query_devices()):
            if d["max_input_channels"] > 0:
                devices.append({
                    "id": idx,
                    "name": d["name"],
                    "channels": d["max_input_channels"],
                    "default_sr": int(d["default_samplerate"])
                })
        default_in = int(sd.default.device[0]) if sd.default.device[0] >= 0 else 0
        return jsonify({
            "default_device": default_in,
            "devices": devices
        })
    except Exception as e:
        return jsonify({"devices": [], "error": str(e)})


if __name__ == "__main__":
    print(f"Starting Gunshot Detection Web Application on http://{config.WEB_HOST}:{config.WEB_PORT}")
    print(f"Safety Designation: {SAFETY_DESIGNATION}")
    app.run(host=config.WEB_HOST, port=config.WEB_PORT, debug=False)
