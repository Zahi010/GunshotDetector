import sys
import json
import io
import numpy as np
import soundfile as sf

sys.path.insert(0, "e:/gunshot/gunshot")
from app import app

def test_endpoints():
    client = app.test_client()

    # 1. Health endpoint
    res_health = client.get("/api/health")
    assert res_health.status_code == 200
    data_health = res_health.get_json()
    print("Health response:", data_health)
    assert data_health["status"] in ["healthy", "ok"]
    assert data_health.get("default_detector") == "phase14"
    assert "detector_improvement_v10" in data_health.get("supported_detectors", [])
    assert "detector_improvement_v10" in data_health.get("experimental_detectors", [])

    # 2. Devices endpoint
    res_devices = client.get("/api/devices")
    assert res_devices.status_code == 200
    data_devices = res_devices.get_json()
    print(f"Devices response: {len(data_devices.get('devices', []))} devices found")

    # 3. Stream window endpoint with Phase 14 default
    wav_io = io.BytesIO()
    sf.write(wav_io, np.zeros(7680, dtype=np.float32), 16000, format="WAV")
    wav_io.seek(0)
    data = {"audio": (wav_io, "chunk.wav")}
    res_stream = client.post("/api/stream_window", data=data, content_type="multipart/form-data")
    assert res_stream.status_code == 200
    data_stream = res_stream.get_json()
    print("Stream window (Phase 14 default) response:", data_stream)
    assert data_stream["is_gunshot"] is False

    # 4. Stream window endpoint with V9
    wav_io_v9 = io.BytesIO()
    sf.write(wav_io_v9, np.zeros(7680, dtype=np.float32), 16000, format="WAV")
    wav_io_v9.seek(0)
    data_v9 = {"audio": (wav_io_v9, "chunk.wav"), "model": "detector_improvement_v9"}
    res_stream_v9 = client.post("/api/stream_window", data=data_v9, content_type="multipart/form-data")
    assert res_stream_v9.status_code == 200
    data_stream_v9 = res_stream_v9.get_json()
    print("Stream window (V9) response:", data_stream_v9)
    assert data_stream_v9["is_gunshot"] is False

    # 5. Stream window endpoint with V10
    wav_io_v10 = io.BytesIO()
    sf.write(wav_io_v10, np.zeros(7680, dtype=np.float32), 16000, format="WAV")
    wav_io_v10.seek(0)
    data_v10 = {"audio": (wav_io_v10, "chunk.wav"), "model": "detector_improvement_v10"}
    res_stream_v10 = client.post("/api/stream_window", data=data_v10, content_type="multipart/form-data")
    assert res_stream_v10.status_code == 200
    data_stream_v10 = res_stream_v10.get_json()
    print("Stream window (V10) response:", data_stream_v10)
    assert data_stream_v10["is_gunshot"] is False

    print("\n>>> ALL API ENDPOINTS TESTED AND VERIFIED CLEANLY WITH V10! <<<")

if __name__ == "__main__":
    test_endpoints()
