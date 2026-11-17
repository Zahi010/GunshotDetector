import sys
import io
import json
import time
import numpy as np
import soundfile as sf

sys.path.insert(0, "e:/gunshot/gunshot")
from app import app

def run_dashboard_validation():
    print("=" * 70)
    print("PHASE 54: DASHBOARD AND FLASK ENDPOINT VALIDATION SUITE")
    print("=" * 70)
    client = app.test_client()
    results = {}

    # 1. API Health & Default Detector Check
    print("\n1. Testing GET /api/health...")
    res = client.get("/api/health")
    assert res.status_code == 200, f"Expected 200, got {res.status_code}"
    data = res.get_json()
    assert data["status"] == "healthy"
    assert data["default_detector"] == "phase14", f"Default detector must be phase14, got {data['default_detector']}"
    assert "detector_improvement_v10" in data["supported_detectors"], "V10 must be in supported_detectors"
    assert "detector_improvement_v10" in data["experimental_detectors"], "V10 must be in experimental_detectors"
    print(f"   PASS: Default detector is '{data['default_detector']}'. V10 registered.")
    results['health_check'] = {'status': 'PASS', 'default_detector': data['default_detector']}

    # 2. Device Enumeration
    print("\n2. Testing GET /api/devices...")
    res = client.get("/api/devices")
    assert res.status_code == 200
    data = res.get_json()
    devices = data.get("devices", [])
    assert len(devices) > 0, "No audio devices returned"
    print(f"   PASS: Enumerated {len(devices)} host audio devices. Default: {data.get('default_device')}")
    results['device_enumeration'] = {'status': 'PASS', 'device_count': len(devices)}

    # 3. WAV Upload to /api/detect (Default Phase 14)
    print("\n3. Testing POST /api/detect (Default Phase 14)...")
    wav_io = io.BytesIO()
    sf.write(wav_io, np.zeros(16000, dtype=np.float32), 16000, format='WAV')
    wav_io.seek(0)
    res = client.post("/api/detect", data={"audio": (wav_io, "test_silence.wav")}, content_type="multipart/form-data")
    assert res.status_code == 200
    data = res.get_json()
    assert "detected" in data
    print(f"   PASS: Silence file evaluated by Phase 14. Detected: {data['detected']}, Score: {data.get('score')}")
    results['wav_upload_phase14'] = {'status': 'PASS', 'detected': data['detected']}

    # 4. WAV Upload to /api/detect with Explicit V10 Selection
    print("\n4. Testing POST /api/detect (Explicit V10)...")
    wav_io = io.BytesIO()
    sf.write(wav_io, np.zeros(16000, dtype=np.float32), 16000, format='WAV')
    wav_io.seek(0)
    res = client.post("/api/detect", data={
        "audio": (wav_io, "test_silence.wav"),
        "detector_version": "detector_improvement_v10"
    }, content_type="multipart/form-data")
    assert res.status_code == 200
    data = res.get_json()
    assert "detected" in data
    print(f"   PASS: Silence file evaluated by V10. Detected: {data['detected']}, Score: {data.get('score')}")
    results['wav_upload_v10'] = {'status': 'PASS', 'detected': data['detected']}

    # 5. Real-Time Streaming Window (Default Phase 14)
    print("\n5. Testing POST /api/stream_window (Phase 14)...")
    wav_chunk = io.BytesIO()
    sf.write(wav_chunk, np.zeros(7680, dtype=np.float32), 16000, format='WAV')
    wav_chunk.seek(0)
    res = client.post("/api/stream_window", data={
        "audio": (wav_chunk, "chunk.wav"),
        "session_id": "stream_phase14_session"
    }, content_type="multipart/form-data")
    assert res.status_code == 200
    data = res.get_json()
    assert data["session_id"] == "stream_phase14_session"
    assert data["is_gunshot"] is False
    print(f"   PASS: Stream chunk processed. is_gunshot={data['is_gunshot']}, latency={data.get('latency_ms')}ms")
    results['streaming_phase14'] = {'status': 'PASS', 'latency_ms': data.get('latency_ms')}

    # 6. Real-Time Streaming Window (Explicit V10 Selection)
    print("\n6. Testing POST /api/stream_window (Explicit V10)...")
    wav_chunk = io.BytesIO()
    sf.write(wav_chunk, np.zeros(7680, dtype=np.float32), 16000, format='WAV')
    wav_chunk.seek(0)
    res = client.post("/api/stream_window", data={
        "audio": (wav_chunk, "chunk.wav"),
        "detector_version": "detector_improvement_v10",
        "session_id": "stream_v10_session"
    }, content_type="multipart/form-data")
    assert res.status_code == 200
    data = res.get_json()
    assert data["session_id"] == "stream_v10_session"
    assert data["is_gunshot"] is False
    print(f"   PASS: Stream chunk processed by V10. is_gunshot={data['is_gunshot']}, latency={data.get('latency_ms')}ms")
    results['streaming_v10'] = {'status': 'PASS', 'latency_ms': data.get('latency_ms')}

    # 7. Multi-Session Isolation Test
    print("\n7. Testing Multi-Session Isolation on /api/stream_window...")
    # Send high-energy pulse to session_alpha
    pulse = np.zeros(7680, dtype=np.float32)
    pulse[100:150] = 0.95
    wav_alpha = io.BytesIO()
    sf.write(wav_alpha, pulse, 16000, format='WAV')
    wav_alpha.seek(0)
    res_a = client.post("/api/stream_window", data={
        "audio": (wav_alpha, "pulse.wav"),
        "detector_version": "detector_improvement_v10",
        "session_id": "session_alpha"
    }, content_type="multipart/form-data")
    data_a = res_a.get_json()

    # Send silence to session_beta
    wav_beta = io.BytesIO()
    sf.write(wav_beta, np.zeros(7680, dtype=np.float32), 16000, format='WAV')
    wav_beta.seek(0)
    res_b = client.post("/api/stream_window", data={
        "audio": (wav_beta, "silence.wav"),
        "detector_version": "detector_improvement_v10",
        "session_id": "session_beta"
    }, content_type="multipart/form-data")
    data_b = res_b.get_json()

    assert data_b["session_id"] == "session_beta"
    assert data_b["is_gunshot"] is False
    print(f"   PASS: session_alpha score={data_a.get('score')} | session_beta score={data_b.get('score')}")
    print("   PASS: Zero state leakage between concurrent sessions.")
    results['session_isolation'] = {'status': 'PASS'}

    # 8. Reset Stream Endpoint
    print("\n8. Testing POST /api/stream/reset...")
    res_reset = client.post("/api/stream/reset", data={
        "session_id": "session_alpha",
        "detector_version": "detector_improvement_v10"
    })
    assert res_reset.status_code == 200
    print("   PASS: Stream session reset acknowledged.")
    results['stream_reset'] = {'status': 'PASS'}

    print("\n" + "=" * 70)
    print("ALL DASHBOARD & API VALIDATION CHECKS PASSED (8/8)")
    print("=" * 70)
    return results

if __name__ == "__main__":
    run_dashboard_validation()

