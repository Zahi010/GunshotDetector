import sys
import io
import numpy as np
import soundfile as sf

sys.path.insert(0, "e:/gunshot/gunshot")
from app import app

client = app.test_client()

print("Testing /api/health...")
r_health = client.get("/api/health")
print("Status:", r_health.status_code, r_health.get_json())

def make_wav_io():
    wav_io = io.BytesIO()
    silence = np.zeros(16000, dtype=np.float32)
    sf.write(wav_io, silence, 16000, format="WAV")
    wav_io.seek(0)
    return wav_io

print("\nTesting /api/stream_window with Phase 14 (default)...")
r_p14 = client.post("/api/stream_window", data={
    "audio": (make_wav_io(), "chunk.wav"),
    "detector_version": "phase14",
    "session_id": "test_p14"
})
print("Phase 14 Status:", r_p14.status_code)
res_p14 = r_p14.get_json()
print("Phase 14 Result: score =", res_p14.get("score"), "latency_ms =", res_p14.get("latency_ms"), "safety:", res_p14.get("safety_designation"))

print("\nTesting /api/stream_window with V8...")
r_v8 = client.post("/api/stream_window", data={
    "audio": (make_wav_io(), "chunk.wav"),
    "detector_version": "v8",
    "session_id": "test_v8"
})
print("V8 Status:", r_v8.status_code)
res_v8 = r_v8.get_json()
print("V8 Result: score =", res_v8.get("score"), "latency_ms =", res_v8.get("latency_ms"), "safety:", res_v8.get("safety_designation"))

print("\nTesting /api/detect (batch WAV upload) with V8...")
r_detect = client.post("/api/detect", data={
    "audio": (make_wav_io(), "test.wav"),
    "detector_version": "v8"
})
print("Detect Status:", r_detect.status_code)
res_detect = r_detect.get_json()
print("Detect Result: detected =", res_detect.get("detected"), "inference_latency_ms =", res_detect.get("inference_latency_ms"), "safety:", res_detect.get("safety_designation"))
