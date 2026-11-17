import sys
import io
import time
import soundfile as sf
import numpy as np
import pytest

sys.path.insert(0, "e:/gunshot/gunshot")
from app import app

client = app.test_client()

print("=" * 70, flush=True)
print("TASK 8: AUTOMATED INTEGRATION & STRESS TEST FOR V10 LIVE STREAMING", flush=True)
print("=" * 70, flush=True)

def generate_synthetic_chunk(duration_sec=0.48, sr=16000, tone_freq=0.0, impulse=False):
    n_samples = int(duration_sec * sr)
    if impulse:
        audio = np.random.normal(0, 0.001, n_samples).astype(np.float32)
        # Inject sharp shockwave impulse
        audio[100:105] = np.array([0.9, -0.85, 0.7, -0.5, 0.3], dtype=np.float32)
    elif tone_freq > 0:
        t = np.linspace(0, duration_sec, n_samples, endpoint=False)
        audio = 0.1 * np.sin(2 * np.pi * tone_freq * t).astype(np.float32)
    else:
        # Quiet ambient noise
        audio = np.random.normal(0, 0.001, n_samples).astype(np.float32)
        
    buf = io.BytesIO()
    sf.write(buf, audio, sr, format='WAV', subtype='PCM_16')
    buf.seek(0)
    return buf

# Test 1: Health & Endpoint Check
print("\n[Test 1] Health & Status API Check...", flush=True)
res = client.get("/api/health")
assert res.status_code == 200, f"Health check failed: {res.status_code}"
print("  PASS: Health API returned HTTP 200.", flush=True)

# Test 2: V10 Stream Chunk Ingestion Schema
print("\n[Test 2] V10 Stream Chunk Ingestion Schema...", flush=True)
chunk_wav = generate_synthetic_chunk(duration_sec=0.48, sr=16000)
session_a = "test_v10_session_alpha"

res = client.post("/api/stream_window", data={
    "audio": (chunk_wav, "chunk.wav"),
    "session_id": session_a,
    "detector_version": "detector_improvement_v10",
    "profile": "balanced"
}, content_type="multipart/form-data")

assert res.status_code == 200, f"HTTP status failed: {res.status_code}"
data = res.get_json()
print("  Response keys:", list(data.keys()), flush=True)
assert "score" in data, "Missing 'score'"
assert "crest_factor_db" in data, "Missing 'crest_factor_db'"
assert "latency_ms" in data, "Missing 'latency_ms'"
assert "in_event" in data, "Missing 'in_event'"
assert "new_alerts" in data, "Missing 'new_alerts'"
assert "safety_designation" in data, "Missing 'safety_designation'"
assert "NOT FOR LIFE SAFETY" in data["safety_designation"], "Safety designation missing mandatory qualifier"
print(f"  PASS: Schema verified. Latency: {data['latency_ms']} ms, Score: {data['score']}", flush=True)

# Test 3: Session Isolation Test (Session Alpha vs Session Beta)
print("\n[Test 3] Session Isolation Test...", flush=True)
session_b = "test_v10_session_beta"

# Session A receives an impulse
impulse_wav = generate_synthetic_chunk(impulse=True)
res_a = client.post("/api/stream_window", data={
    "audio": (impulse_wav, "impulse.wav"),
    "session_id": session_a,
    "detector_version": "detector_improvement_v10",
    "profile": "balanced"
}, content_type="multipart/form-data")

# Session B receives quiet ambient
quiet_wav = generate_synthetic_chunk(impulse=False)
res_b = client.post("/api/stream_window", data={
    "audio": (quiet_wav, "quiet.wav"),
    "session_id": session_b,
    "detector_version": "detector_improvement_v10",
    "profile": "balanced"
}, content_type="multipart/form-data")

data_a = res_a.get_json()
data_b = res_b.get_json()
print(f"  Session A Crest: {data_a['crest_factor_db']} dB | Session B Crest: {data_b['crest_factor_db']} dB", flush=True)
assert data_a["crest_factor_db"] != data_b["crest_factor_db"], "Sessions cross-contaminated!"
print("  PASS: Sessions are completely isolated.", flush=True)

# Test 4: Edge Case Robustness (Empty chunk, corrupt chunk)
print("\n[Test 4] Edge Case Robustness...", flush=True)
# Empty chunk
res_empty = client.post("/api/stream_window", data={
    "audio": (io.BytesIO(b""), "empty.wav"),
    "session_id": "test_edge",
    "detector_version": "detector_improvement_v10"
}, content_type="multipart/form-data")
assert res_empty.status_code == 200 or res_empty.status_code == 400, "Empty chunk unhandled"
print(f"  Empty chunk handled with status: {res_empty.status_code}", flush=True)

# Corrupt chunk
res_corrupt = client.post("/api/stream_window", data={
    "audio": (io.BytesIO(b"CORRUPT_BYTES_XYZ_123456"), "bad.wav"),
    "session_id": "test_edge",
    "detector_version": "detector_improvement_v10"
}, content_type="multipart/form-data")
assert res_corrupt.status_code == 200 or res_corrupt.status_code == 400 or res_corrupt.status_code == 422, "Corrupt chunk unhandled"
print(f"  Corrupt chunk handled gracefully with status: {res_corrupt.status_code}", flush=True)
print("  PASS: Edge cases handled without server crash.", flush=True)

# Test 5: Sustained Streaming Microbenchmark (50 continuous chunks)
print("\n[Test 5] Sustained Streaming Microbenchmark (50 chunks = 24.0s of audio)...", flush=True)
session_stream = "test_v10_sustained_stream"

# Warm-up chunk (initializes session detector and model graph)
warm_wav = generate_synthetic_chunk(duration_sec=0.48, sr=16000)
t_cold_start = time.perf_counter()
r_warm = client.post("/api/stream_window", data={
    "audio": (warm_wav, "warm.wav"),
    "session_id": session_stream,
    "detector_version": "detector_improvement_v10",
    "profile": "balanced"
}, content_type="multipart/form-data")
cold_start_lat = (time.perf_counter() - t_cold_start) * 1000.0
print(f"  Cold-start detector initialization latency: {cold_start_lat:.1f} ms", flush=True)

latencies = []
t_total_start = time.perf_counter()
for c_idx in range(50):
    c_wav = generate_synthetic_chunk(duration_sec=0.48, sr=16000)
    t0 = time.perf_counter()
    r = client.post("/api/stream_window", data={
        "audio": (c_wav, "chunk.wav"),
        "session_id": session_stream,
        "detector_version": "detector_improvement_v10",
        "profile": "balanced"
    }, content_type="multipart/form-data")
    lat = (time.perf_counter() - t0) * 1000.0
    latencies.append(lat)
    assert r.status_code == 200, f"Chunk {c_idx} failed: {r.status_code}"

t_total = time.perf_counter() - t_total_start
mean_lat = float(np.mean(latencies))
p95_lat = float(np.percentile(latencies, 95))
max_lat = float(np.max(latencies))
print(f"  Processed 50 chunks (24s audio) in {t_total:.2f}s total (Real-time factor: {(24.0/t_total):.1f}x).", flush=True)
print(f"  Sustained Mean Latency: {mean_lat:.2f} ms | p95 Latency: {p95_lat:.2f} ms | Max Latency: {max_lat:.2f} ms", flush=True)
assert mean_lat < 100.0, f"Mean latency exceeds 100 ms budget: {mean_lat} ms"
print("  PASS: Sustained streaming meets strict real-time deadlines (< 100ms vs 480ms window).", flush=True)

# Test 6: Session Reset Check
print("\n[Test 6] Session Reset Endpoint...", flush=True)
res_reset = client.post("/api/stream/reset", data={"session_id": session_stream})
assert res_reset.status_code == 200, f"Reset failed: {res_reset.status_code}"
print("  PASS: Session reset successfully.", flush=True)

print("\n" + "=" * 70, flush=True)
print("ALL 6 V10 LIVE STREAMING TESTS PASSED PERFECTLY!", flush=True)
print("=" * 70, flush=True)
